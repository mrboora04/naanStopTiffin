"""
ai/ — Machine Learning & AI placeholder module
================================================
This package is intentionally kept empty for now.
It is designed to receive the Phase 3 AI features:

  ai/
  ├── data_export.py      – exports DB data to pandas DataFrames for training
  ├── recommender.py      – menu recommendation engine (collaborative filtering)
  ├── demand_forecast.py  – delivery volume prediction (time-series)
  ├── feedback_analysis.py – sentiment scoring on feedback comments
  └── train.py            – CLI entry point to retrain models

HOW TO USE:
  1. Run `python -m ai.data_export` to export your SQLite data to CSV/parquet.
  2. Add your model training code in the relevant module.
  3. Expose trained model endpoints via a new FastAPI router in routers/.

DEPENDENCIES TO ADD WHEN READY (add to requirements.txt):
  pandas
  scikit-learn
  numpy
  torch   (or tensorflow)
"""
