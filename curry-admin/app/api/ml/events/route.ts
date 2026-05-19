import { NextResponse } from "next/server";
import {
  appendTelemetryEvent,
  getTelemetrySummary,
  TelemetryActor,
  TelemetrySurface,
} from "@/lib/mlTelemetry";

type IncomingTelemetryEvent = {
  sessionId?: string;
  actor?: TelemetryActor;
  surface?: TelemetrySurface;
  action?: string;
  town?: string;
  mealWindow?: "breakfast" | "lunch" | "dinner";
  metadata?: Record<string, string | number | boolean | null>;
};

function isValidActor(actor: string): actor is TelemetryActor {
  return ["customer", "driver", "kitchen", "ops", "model"].includes(actor);
}

function isValidSurface(surface: string): surface is TelemetrySurface {
  return [
    "customer-app",
    "driver-app",
    "kitchen-console",
    "ops-console",
    "ml-lab",
  ].includes(surface);
}

function isValidMealWindow(
  mealWindow: string
): mealWindow is "breakfast" | "lunch" | "dinner" {
  return ["breakfast", "lunch", "dinner"].includes(mealWindow);
}

export async function GET() {
  const summary = await getTelemetrySummary();
  return NextResponse.json(summary);
}

export async function POST(request: Request) {
  const payload = (await request.json()) as IncomingTelemetryEvent;

  if (
    !payload.sessionId ||
    !payload.actor ||
    !payload.surface ||
    !payload.action ||
    !payload.town ||
    !payload.mealWindow
  ) {
    return NextResponse.json(
      { error: "Missing required telemetry fields." },
      { status: 400 }
    );
  }

  if (
    !isValidActor(payload.actor) ||
    !isValidSurface(payload.surface) ||
    !isValidMealWindow(payload.mealWindow)
  ) {
    return NextResponse.json(
      { error: "Invalid telemetry payload." },
      { status: 400 }
    );
  }

  const event = await appendTelemetryEvent({
    sessionId: payload.sessionId,
    actor: payload.actor,
    surface: payload.surface,
    action: payload.action,
    town: payload.town,
    mealWindow: payload.mealWindow,
    metadata: payload.metadata,
  });

  return NextResponse.json({ ok: true, event }, { status: 201 });
}
