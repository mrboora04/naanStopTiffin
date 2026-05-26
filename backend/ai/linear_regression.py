"""
ai/linear_regression.py
========================
Provides dynamic simple linear regression (y = mx + c) training 
and prediction utilities for NaanStop Tiffin deliveries.

Written in pure Python using Ordinary Least Squares (OLS) 
derived directly from the IBM ML Lab 1 concepts.
"""

from datetime import datetime
from sqlalchemy.orm import Session
from models.delivery import Delivery

def parse_time_to_minutes(time_str: str, base_time_str: str = "12:00 PM") -> float:
    """
    Parses a timestamp string like '12:35 PM' relative to a route start 
    time like '12:00 PM' and returns elapsed minutes (e.g. 35.0).
    """
    try:
        # Strip outer spaces and format properly
        time_str = time_str.strip()
        base_time_str = base_time_str.strip()
        
        # Handle cases where leading zeros are omitted (e.g., '12:35 PM' or '1:15 PM')
        fmt = "%I:%M %p"
        
        start_dt = datetime.strptime(base_time_str, fmt)
        end_dt = datetime.strptime(time_str, fmt)
        
        delta = end_dt - start_dt
        return delta.total_seconds() / 60.0
    except Exception as e:
        # Fallback to zero if parsing fails
        return 0.0

def train_ols_regression(X: list[float], y: list[float]) -> tuple[float, float]:
    """
    Fits a simple linear regression line (y = mx + c) using Ordinary Least Squares.
    Returns: (slope m, intercept c)
    """
    n = len(X)
    if n == 0:
        return 0.0, 0.0
        
    mean_x = sum(X) / n
    mean_y = sum(y) / n
    
    # Calculate covariance and variance
    numerator = sum((X[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    denominator = sum((X[i] - mean_x) ** 2 for i in range(n))
    
    # Avoid division by zero if all X values are identical
    if denominator == 0:
        return 0.0, mean_y
        
    m = numerator / denominator
    c = mean_y - m * mean_x
    
    return m, c

def get_live_predictions(route_order: int, db: Session) -> dict:
    """
    Queries historical completed deliveries, runs Ordinary Least Squares,
    and returns a prediction for the specified route order stop.
    """
    # 1. Query all delivered items
    completed_deliveries = (
        db.query(Delivery)
        .filter(Delivery.status == "delivered")
        .all()
    )
    
    # If not enough historical data, use a fallback heuristic
    if len(completed_deliveries) < 3:
        m, c = 12.0, 8.0  # Safe defaults
        predicted_minutes = (m * route_order) + c
        return {
            "requested_stop": route_order,
            "predicted_travel_time_minutes": round(predicted_minutes, 1),
            "formula_used": f"y = {m:.1f}x + {c:.1f} (default fallback)",
            "data_points_used": len(completed_deliveries),
            "status": "insufficient_data"
        }
        
    # 2. Extract X (route stop sequence) and y (minutes elapsed)
    X = []
    y = []
    for d in completed_deliveries:
        if d.route_order and d.delivery_time:
            minutes = parse_time_to_minutes(d.delivery_time)
            # Add data points if we successfully parse a positive duration
            if minutes > 0:
                X.append(float(d.route_order))
                y.append(minutes)
                
    # If parsing yielded no valid data points, use fallback
    if len(X) < 3:
        m, c = 12.0, 8.0
        predicted_minutes = (m * route_order) + c
        return {
            "requested_stop": route_order,
            "predicted_travel_time_minutes": round(predicted_minutes, 1),
            "formula_used": f"y = {m:.1f}x + {c:.1f} (parsing fallback)",
            "data_points_used": len(X),
            "status": "insufficient_data"
        }
        
    # 3. Fit our OLS regression line
    m, c = train_ols_regression(X, y)
    
    # 4. Compute prediction
    predicted_minutes = (m * route_order) + c
    
    return {
        "requested_stop": route_order,
        "predicted_travel_time_minutes": round(predicted_minutes, 1),
        "formula_used": f"y = {m:.2f}x + {c:.2f}",
        "data_points_used": len(X),
        "status": "success",
        "details": f"Based on {len(X)} delivery runs, each additional stop adds ~{m:.1f} minutes of transit, with a base startup time of {c:.1f} minutes."
    }
