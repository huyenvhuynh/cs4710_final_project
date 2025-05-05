import os
import sys
import traci
import numpy as np
import pandas as pd
from collections import defaultdict

# Adding SUMO to the path (adjust according to your installation)
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")

# Simulation parameters
simulation_time = 3600  # seconds
simulation_step = 0.1   # seconds
data_collection_interval = 1.0  # seconds (collect data every 1 second)
section_length = 5000   # meters
detection_zones = [1000, 2000, 3000, 4000]  # positions of detectors

# Start the simulation
sumoBinary = "sumo" if sys.platform.startswith('win') else "sumo-gui"
sumoCmd = [sumoBinary, "-c", "simulation.sumocfg", "--start"]
traci.start(sumoCmd)

# Data collection structures
collected_data = []
time_since_last_collection = 0

# Define a function to calculate traffic metrics
def calculate_traffic_metrics():
    vehicle_ids = traci.vehicle.getIDList()
    
    if not vehicle_ids:
        return None
    
    # Collect data for all vehicles
    positions = [traci.vehicle.getLanePosition(v_id) for v_id in vehicle_ids]
    speeds = [traci.vehicle.getSpeed(v_id) for v_id in vehicle_ids]
    accelerations = [traci.vehicle.getAcceleration(v_id) for v_id in vehicle_ids]
    
    # Calculate metrics
    avg_speed = np.mean(speeds) if speeds else 0
    speed_variance = np.var(speeds) if len(speeds) > 1 else 0
    vehicle_density = len(vehicle_ids) / section_length
    
    # Calculate gaps between consecutive vehicles
    sorted_vehicles = sorted(zip(vehicle_ids, positions), key=lambda x: x[1])
    gaps = []
    for i in range(len(sorted_vehicles)-1):
        gap = sorted_vehicles[i+1][1] - sorted_vehicles[i][1] - traci.vehicle.getLength(sorted_vehicles[i][0])
        gaps.append(max(0, gap))  # Avoid negative gaps due to collision
    
    min_gap = min(gaps) if gaps else float('inf')
    avg_gap = np.mean(gaps) if gaps else float('inf')
    
    # Calculate average deceleration (only for decelerating vehicles)
    decelerations = [acc for acc in accelerations if acc < 0]
    avg_deceleration = np.mean(decelerations) if decelerations else 0
    
    # Detector data
    detector_speeds = {}
    detector_counts = {}
    for pos in detection_zones:
        detector_speeds[pos] = []
        detector_counts[pos] = 0
    
    # Count vehicles passing detectors
    for v_id, pos in zip(vehicle_ids, positions):
        for detector_pos in detection_zones:
            # Check if vehicle is within 50m of detector
            if abs(pos - detector_pos) < 5:
                detector_speeds[detector_pos].append(traci.vehicle.getSpeed(v_id))
                detector_counts[detector_pos] += 1
    
    # Calculate average speeds at detectors
    detector_avg_speeds = {pos: np.mean(speeds) if speeds else 0 
                          for pos, speeds in detector_speeds.items()}
    
    # Determine if there's a jam
    # A phantom jam is defined as when average speed drops below 20 km/h (5.56 m/s)
    # without any accident or infrastructure cause
    is_jam = avg_speed < 5.56
    
    # Return all metrics as a dictionary
    return {
        "time": traci.simulation.getTime(),
        "vehicle_count": len(vehicle_ids),
        "average_speed": avg_speed,
        "speed_variance": speed_variance,
        "vehicle_density": vehicle_density,
        "minimum_gap": min_gap,
        "average_gap": avg_gap,
        "average_deceleration": avg_deceleration,
        "detector_counts": detector_counts,
        "detector_speeds": detector_avg_speeds,
        "is_jam": is_jam
    }

# Run the simulation
step = 0
while step < simulation_time / simulation_step:
    traci.simulationStep()
    time_since_last_collection += simulation_step
    
    # Collect data at the specified interval
    if time_since_last_collection >= data_collection_interval:
        metrics = calculate_traffic_metrics()
        if metrics:
            collected_data.append(metrics)
        time_since_last_collection = 0
    
    step += 1

# Close the simulation
traci.close()

# Convert collected data to a DataFrame
df = pd.DataFrame(collected_data)

# Save the data
df.to_csv("traffic_simulation_data.csv", index=False)

print("Simulation completed. Data saved to traffic_simulation_data.csv")
