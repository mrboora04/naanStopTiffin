"""
ai/generate_plot.py
===================
Generates a beautiful scatter plot and simple linear regression line 
from the live SQLite database deliveries, saving it as a PNG for portfolio use.
"""

import os
import sys
import sqlite3
import matplotlib.pyplot as plt

# Add backend root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ai.linear_regression import parse_time_to_minutes, train_ols_regression

def main():
    db_path = "backend/naanstop.db"
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at '{db_path}'")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Fetch historical completed deliveries
    cursor.execute(
        "SELECT route_order, delivery_time FROM deliveries WHERE status = 'delivered'"
    )
    rows = cursor.fetchall()
    conn.close()
    
    if len(rows) < 3:
        print("Error: Need at least 3 completed deliveries to fit a regression line.")
        return
        
    # 2. Extract X (route stop) and y (minutes elapsed)
    X = []
    y = []
    for row in rows:
        route_order, delivery_time = row
        if route_order and delivery_time:
            minutes = parse_time_to_minutes(delivery_time)
            if minutes > 0:
                X.append(float(route_order))
                y.append(minutes)
                
    if len(X) < 3:
        print("Error: Insufficient parsed data points.")
        return
        
    # 3. Fit the Ordinary Least Squares line (y = mx + c)
    m, c = train_ols_regression(X, y)
    print(f"Fitted Model: y = {m:.2f}x + {c:.2f}")
    
    # 4. Generate the plot
    plt.figure(figsize=(9, 5.5))
    
    # Use standard clean layout styles
    plt.grid(True, linestyle="--", alpha=0.5, zorder=0)
    
    # Plot scatter points (vibrant orange representing delicious tiffin food!)
    plt.scatter(
        X, y, 
        color="#FF5A36", 
        s=120, 
        edgecolors="#C0392B", 
        linewidth=1.2, 
        label="Actual Delivery Stop Logs", 
        zorder=3
    )
    
    # Plot regression line (professional clean slate blue)
    min_x, max_x = min(X), max(X)
    x_line = [min_x - 0.2, max_x + 0.2]
    y_line = [m * x + c for x in x_line]
    
    plt.plot(
        x_line, y_line, 
        color="#2C3E50", 
        linewidth=2.8, 
        label=f"Fitted OLS Line (y = {m:.2f}x + {c:.2f})", 
        zorder=2
    )
    
    # Labels, titles, and layout styling
    plt.title(
        "NaanStop Tiffin: Linear Regression Model (Delivery Time vs. Stop Order)", 
        fontsize=13, 
        fontweight="bold", 
        pad=15, 
        color="#2C3E50"
    )
    plt.xlabel("Delivery Route Sequence Order (Stop #)", fontsize=11, fontweight="bold", labelpad=8)
    plt.ylabel("Transit / Elapsed Minutes (from 12:00 PM)", fontsize=11, fontweight="bold", labelpad=8)
    
    # Make x-axis ticks represent exact integer stops
    all_stops = list(set(int(x) for x in X))
    plt.xticks(all_stops)
    
    # Display statistics details directly on the chart in a neat text box
    stats_text = (
        f"Model Parameters:\n"
        f"• Average Base Prep & Start Time: {c:.1f} mins\n"
        f"• Additional Time Per Stop: {m:.1f} mins\n"
        f"• Total Data Logs Trained: {len(X)}"
    )
    plt.gca().text(
        0.05, 0.92, stats_text, 
        transform=plt.gca().transAxes, 
        fontsize=10, 
        verticalalignment='top', 
        bbox=dict(boxstyle='round,pad=0.6', facecolor='#F8F9FA', edgecolor='#BDC3C7', alpha=0.9)
    )
    
    plt.legend(loc="lower right", frameon=True, facecolor="white", edgecolor="#BDC3C7", fontsize=10)
    plt.tight_layout()
    
    # Save the output image
    output_path = "delivery_regression.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    print(f"Success! Regression plot generated and saved as '{output_path}'.")

if __name__ == "__main__":
    main()
