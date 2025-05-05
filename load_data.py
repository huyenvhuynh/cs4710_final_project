import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

# Load all simulation data
all_data = []
for i in range(1, 101):  # Assuming 100 simulation scenarios
    try:
        df = pd.read_csv(f"data_{i}.csv")
        scenario_info = pd.read_csv("simulation_results.csv")
        scenario_info = scenario_info[scenario_info["scenario_id"] == i].iloc[0]
        
        # Add scenario parameters to each row
        df["vehicles_per_hour"] = scenario_info["vehicles_per_hour"]
        df["driver_imperfection"] = scenario_info["driver_imperfection"]
        df["min_gap"] = scenario_info["min_gap"]
        df["aggressive_percentage"] = scenario_info["aggressive_percentage"]
        
        all_data.append(df)
    except FileNotFoundError:
        continue

# Combine all data
combined_data = pd.concat(all_data, ignore_index=True)

# Feature engineering for jam prediction
# Create a window of past data to predict future jams
window_size = 30  # 30 seconds of data

# Create features and labels for prediction
X = []
y = []

for scenario_id in combined_data["scenario_id"].unique():
    scenario_data = combined_data[combined_data["scenario_id"] == scenario_id].sort_values("time")
    
    for i in range(len(scenario_data) - window_size):
        window_data = scenario_data.iloc[i:i+window_size]
        
        # Features: traffic metrics in the window
        features = {
            "avg_speed_mean": window_data["average_speed"].mean(),
            "avg_speed_std": window_data["average_speed"].std(),
            "speed_variance_mean": window_data["speed_variance"].mean(),
            "vehicle_density_mean": window_data["vehicle_density"].mean(),
            "min_gap_min": window_data["minimum_gap"].min(),
            "decel_mean": window_data["average_deceleration"].mean(),
            "vehicles_per_hour": window_data["vehicles_per_hour"].iloc[0],
            "driver_imperfection": window_data["driver_imperfection"].iloc[0],
            "min_gap_param": window_data["min_gap"].iloc[0],
            "aggressive_percentage": window_data["aggressive_percentage"].iloc[0]
        }
        
        # Label: will a jam occur in the next 60 seconds?
        future_window = scenario_data.iloc[i+window_size:i+window_size+60]
        will_jam_occur = future_window["is_jam"].sum() > 0
        
        X.append(features)
        y.append(will_jam_occur)

# Convert to DataFrames
X_df = pd.DataFrame(X)
y_series = pd.Series(y)

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_df, y_series, test_size=0.3, random_state=42)

# Save processed datasets
X_train.to_csv("X_train.csv", index=False)
X_test.to_csv("X_test.csv", index=False)
y_train.to_csv("y_train.csv", index=False)
y_test.to_csv("y_test.csv", index=False)

print("Data processing complete! Datasets ready for model training.")
