export const mlBackendBlueprint = [
  {
    title: "App + API",
    stack: "Next.js route handlers",
    reason:
      "Fast to ship for pilots, keeps product and data capture in one codebase.",
  },
  {
    title: "Transactional store",
    stack: "Postgres",
    reason:
      "Best home for orders, subscriptions, drivers, kitchens, and feature flags.",
  },
  {
    title: "Raw ML dataset",
    stack: "Hugging Face Dataset repo",
    reason:
      "Version your feedback, routes, ETA outcomes, and meal preferences for training.",
  },
  {
    title: "Batch jobs",
    stack: "Hugging Face Jobs",
    reason:
      "Run ingestion, labeling, offline evaluation, and fine-tuning without local GPUs.",
  },
  {
    title: "Training telemetry",
    stack: "Trackio",
    reason:
      "Track experiments and compare ranking, ETA, demand, and personalization models.",
  },
];
