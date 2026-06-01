# ML Backend Recommendation

This pilot app should use a product stack that captures clean operational data now and grows into model training later.

## Recommended stack

| Layer | Recommendation | Why it fits this app |
|---|---|---|
| Web product | Next.js app router | One codebase for customer, driver, kitchen, and admin workflows. |
| Core database | Postgres | Strong fit for orders, subscriptions, deliveries, routes, and support records. |
| Raw telemetry | Event table + NDJSON/JSONL export | Easy local pilot collection, easy later migration to durable pipelines. |
| ML dataset store | Hugging Face Dataset repo | Versioned snapshots for ratings, ETA outcomes, route traces, and add-on behavior. |
| Batch compute | Hugging Face Jobs | Good for data cleaning, feature generation, fine-tuning, and offline evaluation. |
| Experiment tracking | Trackio | Compare ETA, ranking, personalization, and demand models over time. |

## Data to collect from day one

- Menu impressions by town and meal window
- Add-on selections and conversion
- Meal ratings and free-text comments
- Special food requests
- Route plans and actual completion times
- Delay reasons
- Cancellation reasons
- Support contacts and resolution outcomes

## First models worth training

1. ETA risk model
Predict likely late deliveries before dispatch so the kitchen or driver can intervene.

2. Meal personalization ranker
Rank dishes and add-ons based on taste scores, repeat orders, and dietary preferences.

3. Demand forecasting model
Predict breakfast, lunch, and dinner demand by town and weekday.

4. Surplus Food Matcher (Flash Sales)
Uses location and order history to instantly push discounted flash sales to nearby customers when the kitchen has excess prepped food, minimizing food waste.

5. Subscription Churn/Pause Predictor
Predicts when a regular subscriber is experiencing fatigue (e.g., missed meals) and proactively offers them a "pause" or a menu swap to prevent outright cancellation.

## Why Hugging Face fits

- Hugging Face Jobs supports cloud jobs for data ingestion, processing, training, and inference workflows:
  https://huggingface.co/docs/hub/jobs
- Jobs are designed for AI and data workflows on managed compute:
  https://huggingface.co/docs/hub/jobs-overview
- Hugging Face Datasets give you a natural home for versioned training data:
  https://huggingface.co/docs/hub/datasets

## Suggested next step after this prototype

- Move telemetry writes from local NDJSON into Postgres.
- Add nightly export from Postgres to a Hugging Face Dataset repo.
- Start one Hugging Face Job for offline ETA prediction experiments.
- Use Trackio to compare each training run before rollout.
