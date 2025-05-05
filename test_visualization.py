import os
import sys
import time
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd

# Add SUMO to the Python path
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")

import traci

# Start the simulation
sumo_binary = "sumo-gui" if os.name != "nt" else "sumo-gui.exe"
sumo_cmd = [sumo_binary, "-c", "simulation.sumocfg"]
traci.start(sumo_cmd)

# Data collection
collected_data = []

# Run the simulation for 1000 steps (visualizing in SUMO-GUI)
print("Running simulation in SUMO-GUI. Close the SUMO window when done.")
for step in range(1000):
    traci.simulationStep()
    
    # Collect vehicle data every 10 steps
    if step % 10 == 0:
        vehicle_ids = traci.vehicle.getIDList()
        
        if vehicle_ids:
            positions = [traci.vehicle.getLanePosition(v_id) for v_id in vehicle_ids]
            speeds = [traci.vehicle.getSpeed(v_id) for v_id in vehicle_ids]
            
            # Calculate averages
            avg_speed = sum(speeds) / len(speeds) if speeds else 0
            
            # Store data
            collected_data.append({
                'time_step': step,
                'num_vehicles': len(vehicle_ids),
                'avg_speed': avg_speed
            })
            
            # Print status
            print(f"Step {step}: {len(vehicle_ids)} vehicles, Avg Speed: {avg_speed:.2f} m/s")
            
            # Look for signs of traffic jam
            if avg_speed < 5.56 and len(vehicle_ids) > 10:
                print(f"Potential phantom jam detected at step {step}!")

# Close the connection
traci.close()

# Convert collected data to DataFrame
df = pd.DataFrame(collected_data)

# Plot the results
plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
plt.plot(df['time_step'], df['num_vehicles'], 'b-')
plt.title('Number of Vehicles Over Time')
plt.xlabel('Simulation Step')
plt.ylabel('Number of Vehicles')
plt.grid(True)

plt.subplot(2, 1, 2)
plt.plot(df['time_step'], df['avg_speed'], 'r-')
plt.axhline(y=5.56, color='k', linestyle='--', label='Jam Threshold (5.56 m/s)')
plt.title('Average Speed Over Time')
plt.xlabel('Simulation Step')
plt.ylabel('Speed (m/s)')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.savefig('traffic_analysis.png')
plt.show()

print("Simulation complete. Results saved to traffic_analysis.png")
