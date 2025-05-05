import os
import numpy as np
import pandas as pd
from subprocess import call

# Parameters to vary
veh_per_hour_values = [900, 1200, 1500, 1800, 2100]
sigma_values = [0.2, 0.4, 0.6, 0.8]
min_gap_values = [1.0, 1.5, 2.0, 2.5]
aggressive_driver_percentages = [0.1, 0.2, 0.3, 0.4]

scenario_id = 0
results = []

for vph in veh_per_hour_values:
    for sigma in sigma_values:
        for min_gap in min_gap_values:
            for agg_pct in aggressive_driver_percentages:
                scenario_id += 1
                
                # Create a route file with these parameters
                with open(f"traffic_{scenario_id}.rou.xml", "w") as f:
                    f.write(f"""<routes>
    <vType id="cautious" accel="1.0" decel="4.5" sigma="{sigma}" length="5" minGap="{min_gap+1.0}" maxSpeed="25" speedDev="0.1"/>
    <vType id="normal" accel="1.5" decel="4.0" sigma="{sigma}" length="5" minGap="{min_gap}" maxSpeed="30" speedDev="0.1"/>
    <vType id="aggressive" accel="2.0" decel="5.0" sigma="{sigma+0.2}" length="5" minGap="{max(0.5, min_gap-1.0)}" maxSpeed="35" speedDev="0.3"/>
    
    <flow id="flow1" type="cautious" begin="0" end="3600" vehsPerHour="{int(vph*(1-agg_pct)*0.4)}" departLane="0" departSpeed="max"/>
    <flow id="flow2" type="normal" begin="0" end="3600" vehsPerHour="{int(vph*(1-agg_pct)*0.6)}" departLane="0" departSpeed="max"/>
    <flow id="flow3" type="aggressive" begin="0" end="3600" vehsPerHour="{int(vph*agg_pct)}" departLane="0" departSpeed="max"/>
</routes>""")
                
                # Update config file to use this route file
                with open(f"simulation_{scenario_id}.sumocfg", "w") as f:
                    f.write(f"""<configuration>
    <input>
        <net-file value="highway.net.xml"/>
        <route-files value="traffic_{scenario_id}.rou.xml"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="3600"/>
        <step-length value="0.1"/>
    </time>
    <processing>
        <default.speeddev value="0.1"/>
    </processing>
    <report>
        <verbose value="true"/>
        <no-step-log value="true"/>
    </report>
</configuration>""")
                
                # Run the simulation
                print(f"Running scenario {scenario_id} of {len(veh_per_hour_values)*len(sigma_values)*len(min_gap_values)*len(aggressive_driver_percentages)}")
                call(["python", "run_simulation.py", f"simulation_{scenario_id}.sumocfg", f"data_{scenario_id}.csv"])
                
                # Analyze results: did phantom jams occur?
                df = pd.read_csv(f"data_{scenario_id}.csv")
                jam_occurred = df["is_jam"].sum() > 0
                
                results.append({
                    "scenario_id": scenario_id,
                    "vehicles_per_hour": vph,
                    "driver_imperfection": sigma,
                    "min_gap": min_gap,
                    "aggressive_percentage": agg_pct,
                    "jam_occurred": jam_occurred,
                    "jam_count": df["is_jam"].sum(),
                    "avg_speed": df["average_speed"].mean(),
                    "min_speed": df["average_speed"].min()
                })

# Save the scenario results
results_df = pd.DataFrame(results) results_df.to_csv("simulation_results.csv", index=False) print("All scenarios completed!")
