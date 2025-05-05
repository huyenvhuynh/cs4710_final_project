import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
import traci

# Adding SUMO to the path
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")

# Start the simulation
sumoBinary = "sumo-gui"  # Use GUI version for visualization
sumoCmd = [sumoBinary, "-c", "simulation.sumocfg"]
traci.start(sumoCmd)

# Setup the figure for animation
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
highway_length = 5000
max_vehicles = 500

# Initialize plots
scatter = ax1.scatter([], [], c=[], cmap='coolwarm', vmin=0, vmax=33.33)
ax1.set_xlim(0, highway_length)
ax1.set_ylim(-5, 5)
ax1.set_title('Vehicle Positions and Speeds')
ax1.set_xlabel('Position (m)')
ax1.set_yticks([])
cbar = fig.colorbar(scatter, ax=ax1)
cbar.set_label('Speed (m/s)')

# Speed over time plot
times = []
avg_speeds = []
speed_line, = ax2.plot([], [], 'b-')
ax2.set_xlim(0, 500)  # Show last 500 seconds
ax2.set_ylim(0, 35)
ax2.set_title('Average Speed Over Time')
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Speed (m/s)')
ax2.grid(True)

# Function to initialize the animation
def init():
    scatter.set_offsets(np.empty((0, 2)))
    scatter.set_array(np.array([]))
    speed_line.set_data([], [])
    return scatter, speed_line

# Animation update function
def update(frame):
    traci.simulationStep()
    
    # Get vehicle data
    vehicle_ids = traci.vehicle.getIDList()
    positions = [traci.vehicle.getLanePosition(v_id) for v_id in vehicle_ids]
    speeds = [traci.vehicle.getSpeed(v_id) for v_id in vehicle_ids]
    
    # Update position scatter plot
    y_positions = [0] * len(positions)  # All vehicles on same y-coordinate
    scatter.set_offsets(np.column_stack((positions, y_positions)))
    scatter.set_array(np.array(speeds))
    
    # Update speed over time plot
    current_time = traci.simulation.getTime()
    avg_speed = np.mean(speeds) if speeds else 0
    
    times.append(current_time)
    avg_speeds.append(avg_speed)
    
    # Keep only the last 500 seconds of data
    if len(times) > 500:
        times.pop(0)
        avg_speeds.pop(0)
    
    speed_line.set_data(times, avg_speeds)
    
    # Highlight if there's a jam (avg speed < 5.56 m/s)
    if avg_speed < 5.56:
        ax2.set_facecolor((1, 0.9, 0.9))  # Light red background
    else:
        ax2.set_facecolor((0.95, 1, 0.95))  # Light green background
    
    return scatter, speed_line

# Create the animation
ani = animation.FuncAnimation(fig, update, frames=3600, 
                              init_func=init, blit=True, interval=100)

plt.tight_layout()
plt.show()

# Close traci when done
traci.close()
