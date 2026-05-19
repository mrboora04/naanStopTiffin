CREATE TABLE IF NOT EXISTS ml_telemetry_events (
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

CREATE INDEX IF NOT EXISTS idx_ml_telemetry_events_timestamp
ON ml_telemetry_events (timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_ml_telemetry_events_town_window
ON ml_telemetry_events (town, meal_window);
