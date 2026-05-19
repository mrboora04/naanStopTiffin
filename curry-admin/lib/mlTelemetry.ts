import "server-only";

import { promises as fs } from "fs";
import path from "path";

export type TelemetryActor =
  | "customer"
  | "driver"
  | "kitchen"
  | "ops"
  | "model";

export type TelemetrySurface =
  | "customer-app"
  | "driver-app"
  | "kitchen-console"
  | "ops-console"
  | "ml-lab";

export type TelemetryEvent = {
  id: string;
  timestamp: string;
  sessionId: string;
  actor: TelemetryActor;
  surface: TelemetrySurface;
  action: string;
  town: string;
  mealWindow: "breakfast" | "lunch" | "dinner";
  metadata?: Record<string, string | number | boolean | null>;
};

type TelemetryPayload = Omit<TelemetryEvent, "id" | "timestamp">;

type QueryResultRow = Record<string, unknown>;

type PostgresPool = {
  query: (
    text: string,
    params?: unknown[]
  ) => Promise<{ rows: QueryResultRow[] }>;
};

const telemetryDir = path.join(process.cwd(), "data", "telemetry");
const telemetryFile = path.join(telemetryDir, "events.ndjson");
const telemetryTable = "ml_telemetry_events";

let poolPromise: Promise<PostgresPool | null> | null = null;
let schemaEnsured = false;

function isPostgresConfigured() {
  return Boolean(process.env.DATABASE_URL);
}

async function ensureTelemetryStore() {
  await fs.mkdir(telemetryDir, { recursive: true });
}

async function getPostgresPool(): Promise<PostgresPool | null> {
  if (!isPostgresConfigured()) {
    return null;
  }

  if (!poolPromise) {
    poolPromise = (async () => {
      try {
        const pg = (await import("pg")) as {
          Pool: new (config: {
            connectionString?: string;
            ssl?: { rejectUnauthorized: boolean } | false;
          }) => PostgresPool;
        };

        return new pg.Pool({
          connectionString: process.env.DATABASE_URL,
          ssl:
            process.env.POSTGRES_SSL === "disable"
              ? false
              : { rejectUnauthorized: false },
        });
      } catch (error) {
        console.warn(
          "Postgres adapter unavailable. Falling back to local telemetry file.",
          error
        );
        return null;
      }
    })();
  }

  return poolPromise;
}

async function ensurePostgresSchema(pool: PostgresPool) {
  if (schemaEnsured) {
    return;
  }

  await pool.query(`
    CREATE TABLE IF NOT EXISTS ${telemetryTable} (
      id TEXT PRIMARY KEY,
      timestamp TIMESTAMPTZ NOT NULL,
      session_id TEXT NOT NULL,
      actor TEXT NOT NULL,
      surface TEXT NOT NULL,
      action TEXT NOT NULL,
      town TEXT NOT NULL,
      meal_window TEXT NOT NULL,
      metadata JSONB NOT NULL DEFAULT '{}'::jsonb
    );
  `);

  await pool.query(`
    CREATE INDEX IF NOT EXISTS idx_${telemetryTable}_timestamp
    ON ${telemetryTable} (timestamp DESC);
  `);

  await pool.query(`
    CREATE INDEX IF NOT EXISTS idx_${telemetryTable}_town_window
    ON ${telemetryTable} (town, meal_window);
  `);

  schemaEnsured = true;
}

function createEvent(payload: TelemetryPayload): TelemetryEvent {
  return {
    ...payload,
    id: `evt_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
    timestamp: new Date().toISOString(),
  };
}

async function appendFileTelemetryEvent(event: TelemetryEvent) {
  await ensureTelemetryStore();
  await fs.appendFile(telemetryFile, `${JSON.stringify(event)}\n`, "utf8");
}

async function appendPostgresTelemetryEvent(
  pool: PostgresPool,
  event: TelemetryEvent
) {
  await ensurePostgresSchema(pool);
  await pool.query(
    `
      INSERT INTO ${telemetryTable} (
        id,
        timestamp,
        session_id,
        actor,
        surface,
        action,
        town,
        meal_window,
        metadata
      )
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9::jsonb)
    `,
    [
      event.id,
      event.timestamp,
      event.sessionId,
      event.actor,
      event.surface,
      event.action,
      event.town,
      event.mealWindow,
      JSON.stringify(event.metadata ?? {}),
    ]
  );
}

async function readFileTelemetryEvents(): Promise<TelemetryEvent[]> {
  await ensureTelemetryStore();

  let content = "";
  try {
    content = await fs.readFile(telemetryFile, "utf8");
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") {
      return [];
    }
    throw error;
  }

  return content
    .split(/\r?\n/)
    .filter(Boolean)
    .map((line) => JSON.parse(line) as TelemetryEvent);
}

function mapDbRow(row: QueryResultRow): TelemetryEvent {
  const metadata = row.metadata as Record<
    string,
    string | number | boolean | null
  > | null;

  return {
    id: String(row.id),
    timestamp:
      row.timestamp instanceof Date
        ? row.timestamp.toISOString()
        : String(row.timestamp),
    sessionId: String(row.session_id),
    actor: row.actor as TelemetryActor,
    surface: row.surface as TelemetrySurface,
    action: String(row.action),
    town: String(row.town),
    mealWindow: row.meal_window as "breakfast" | "lunch" | "dinner",
    metadata: metadata ?? {},
  };
}

async function readPostgresTelemetryEvents(pool: PostgresPool) {
  await ensurePostgresSchema(pool);
  const result = await pool.query(
    `
      SELECT
        id,
        timestamp,
        session_id,
        actor,
        surface,
        action,
        town,
        meal_window,
        metadata
      FROM ${telemetryTable}
      ORDER BY timestamp DESC
    `
  );

  return result.rows.map(mapDbRow);
}

export async function appendTelemetryEvent(
  payload: TelemetryPayload
): Promise<TelemetryEvent> {
  const event = createEvent(payload);
  const pool = await getPostgresPool();

  if (pool) {
    await appendPostgresTelemetryEvent(pool, event);
    return event;
  }

  await appendFileTelemetryEvent(event);
  return event;
}

export async function readTelemetryEvents(): Promise<TelemetryEvent[]> {
  const pool = await getPostgresPool();

  if (pool) {
    return readPostgresTelemetryEvents(pool);
  }

  return readFileTelemetryEvents();
}

function countBy<T extends string>(
  values: T[]
): Array<{ key: T; count: number }> {
  const counts = new Map<T, number>();
  values.forEach((value) => {
    counts.set(value, (counts.get(value) ?? 0) + 1);
  });

  return [...counts.entries()]
    .map(([key, count]) => ({ key, count }))
    .sort((a, b) => b.count - a.count);
}

export async function getTelemetrySummary() {
  const events = await readTelemetryEvents();
  const actionCounts = countBy(events.map((event) => event.action));
  const actorCounts = countBy(events.map((event) => event.actor));
  const townCounts = countBy(events.map((event) => event.town));

  const hasDelaySignals = actionCounts.some(
    (item) => item.key === "order_delayed" && item.count >= 2
  );
  const hasTasteSignals = actionCounts.some(
    (item) => item.key === "meal_rated" && item.count >= 2
  );
  const hasPreferenceSignals = actionCounts.some(
    (item) =>
      (item.key === "addon_selected" ||
        item.key === "special_request_added" ||
        item.key === "menu_viewed") &&
      item.count >= 2
  );

  return {
    storage: isPostgresConfigured() ? "postgres-preferred" : "file-fallback",
    totalEvents: events.length,
    latestEvents: [...events].slice(0, 8),
    topActions: actionCounts.slice(0, 5),
    topActors: actorCounts.slice(0, 5),
    topTowns: townCounts.slice(0, 5),
    trainingReadiness: [
      {
        model: "ETA Risk Model",
        status: hasDelaySignals ? "warming" : "collecting",
        note:
          "Use route, town, meal window, and delay outcomes to predict late deliveries.",
      },
      {
        model: "Meal Personalization Ranker",
        status: hasPreferenceSignals ? "warming" : "collecting",
        note:
          "Use menu views, add-ons, reorders, and special requests to rank meals.",
      },
      {
        model: "Taste Satisfaction Model",
        status: hasTasteSignals ? "warming" : "collecting",
        note:
          "Use ratings and comments to find dishes that increase retention.",
      },
    ],
  };
}
