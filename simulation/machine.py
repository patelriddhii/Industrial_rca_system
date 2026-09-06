import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class ToolWearMachine:
    """Machine failure mode: progressive tool wear affecting both cycle time and defects."""

    MACHINE_TYPE = "tool_wear_machine"
    MAINTENANCE_INTERVAL = 100
    INCIDENT_START_CYCLE = 600
    INCIDENT_MULTIPLIER = 3.0

    def __init__(self, machine_id):
        self.machine_id = machine_id
        self.tool_wear = 0.0

    def run_cycle(self, cycle_number):
        wear_increment = np.random.uniform(0.02, 0.05)
        if cycle_number >= self.INCIDENT_START_CYCLE:
            wear_increment *= self.INCIDENT_MULTIPLIER

        self.tool_wear += wear_increment

        maintenance_event = False
        if cycle_number % self.MAINTENANCE_INTERVAL == 0:
            self.tool_wear = 0.0
            maintenance_event = True

        base_cycle_time = 10
        cycle_time = base_cycle_time + (self.tool_wear * 2)
        defect_probability = min(0.01 + (self.tool_wear * 0.015), 0.9)
        defect = np.random.random() < defect_probability

        return {
            "machine_id": self.machine_id,
            "machine_type": self.MACHINE_TYPE,
            "cycle": cycle_number,
            "latent_state_value": self.tool_wear,
            "latent_state_name": "tool_wear",
            "cycle_time": cycle_time,
            "defect": int(defect),
            "maintenance_event": int(maintenance_event)
        }


class CalibrationDriftMachine:
    """Machine failure mode: sensor/calibration drift affecting defects but NOT cycle time."""

    MACHINE_TYPE = "calibration_drift_machine"
    MAINTENANCE_INTERVAL = 100
    INCIDENT_START_CYCLE = 400
    INCIDENT_MULTIPLIER = 4.0

    def __init__(self, machine_id):
        self.machine_id = machine_id
        self.calibration_offset = 0.0

    def run_cycle(self, cycle_number):
        drift_increment = np.random.uniform(0.015, 0.04)
        if cycle_number >= self.INCIDENT_START_CYCLE:
            drift_increment *= self.INCIDENT_MULTIPLIER

        self.calibration_offset += drift_increment

        maintenance_event = False
        if cycle_number % self.MAINTENANCE_INTERVAL == 0:
            self.calibration_offset = 0.0
            maintenance_event = True

        base_cycle_time = 10
        cycle_time = base_cycle_time + np.random.uniform(-0.3, 0.3)

        defect_probability = min(0.01 + (self.calibration_offset * 0.018), 0.9)
        defect = np.random.random() < defect_probability

        return {
            "machine_id": self.machine_id,
            "machine_type": self.MACHINE_TYPE,
            "cycle": cycle_number,
            "latent_state_value": self.calibration_offset,
            "latent_state_name": "calibration_offset",
            "cycle_time": cycle_time,
            "defect": int(defect),
            "maintenance_event": int(maintenance_event)
        }


class HealthyControlMachine:
    """Control machine: normal wear-and-tear only, NO incident ever injected.
    Used to verify the detection/investigation system doesn't false-alarm on healthy operation."""

    MACHINE_TYPE = "healthy_control_machine"
    MAINTENANCE_INTERVAL = 100

    def __init__(self, machine_id):
        self.machine_id = machine_id
        self.component_condition = 0.0

    def run_cycle(self, cycle_number):
        # Small, stable degradation — no incident multiplier is ever applied here
        condition_increment = np.random.uniform(0.01, 0.03)
        self.component_condition += condition_increment

        maintenance_event = False
        if cycle_number % self.MAINTENANCE_INTERVAL == 0:
            self.component_condition = 0.0
            maintenance_event = True

        base_cycle_time = 10
        cycle_time = base_cycle_time + np.random.uniform(-0.3, 0.3)

        # Defect probability stays low and stable throughout the entire run
        defect_probability = min(0.01 + (self.component_condition * 0.008), 0.15)
        defect = np.random.random() < defect_probability

        return {
            "machine_id": self.machine_id,
            "machine_type": self.MACHINE_TYPE,
            "cycle": cycle_number,
            "latent_state_value": self.component_condition,
            "latent_state_name": "component_condition",
            "cycle_time": cycle_time,
            "defect": int(defect),
            "maintenance_event": int(maintenance_event)
        }


def run_simulation(n_cycles=1000, seed=42):
    np.random.seed(seed)

    machines = [
        ToolWearMachine(machine_id="M1"),
        CalibrationDriftMachine(machine_id="M2"),
        HealthyControlMachine(machine_id="M3"),
    ]

    data = []
    maintenance_log = []

    for cycle in range(1, n_cycles + 1):
        for machine in machines:
            result = machine.run_cycle(cycle)
            data.append(result)

            if result["maintenance_event"]:
                if isinstance(machine, CalibrationDriftMachine):
                    action = "recalibration"
                elif isinstance(machine, ToolWearMachine):
                    action = "tool_replacement"
                else:
                    action = "routine_check"

                maintenance_log.append({
                    "machine_id": machine.machine_id,
                    "cycle": cycle,
                    "action": action,
                    "reason": "scheduled_maintenance"
                })

    df = pd.DataFrame(data)
    maintenance_df = pd.DataFrame(maintenance_log)

    # Note: M3 deliberately has NO row here — it's a negative/control case
    incidents_df = pd.DataFrame([
        {
            "incident_id": 1,
            "machine_id": "M1",
            "start_cycle": ToolWearMachine.INCIDENT_START_CYCLE,
            "root_cause": "abnormal_tool_wear_rate",
            "description": "Simulated lubrication failure causing 3x normal wear rate"
        },
        {
            "incident_id": 2,
            "machine_id": "M2",
            "start_cycle": CalibrationDriftMachine.INCIDENT_START_CYCLE,
            "root_cause": "abnormal_calibration_drift",
            "description": "Simulated sensor drift causing 4x normal calibration offset accumulation"
        }
    ])

    return df, maintenance_df, incidents_df


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    df, maintenance_df, incidents_df = run_simulation(n_cycles=1000)

    df.to_csv("data/machine_data.csv", index=False)
    maintenance_df.to_csv("data/maintenance_log.csv", index=False)
    incidents_df.to_csv("data/incidents.csv", index=False)

    print("Data saved successfully!")
    print(f"\nTotal maintenance events: {len(maintenance_df)}")
    print(maintenance_df["action"].value_counts())
    print(f"\nSample data:\n{df.head()}")

    machine_ids = df["machine_id"].unique()
    fig, axes = plt.subplots(len(machine_ids), 1, figsize=(10, 4 * len(machine_ids)), sharex=True)

    incidents_by_machine = incidents_df.set_index("machine_id")["start_cycle"].to_dict()
    titles_by_machine = incidents_df.set_index("machine_id")["root_cause"].to_dict()

    for ax, machine_id in zip(axes, machine_ids):
        machine_df = df[df["machine_id"] == machine_id].copy()
        machine_df["rolling_defect_rate"] = machine_df["defect"].rolling(window=30).mean()

        ax.plot(machine_df["cycle"], machine_df["rolling_defect_rate"], label=f"{machine_id} defect rate")

        if machine_id in incidents_by_machine:
            ax.axvline(x=incidents_by_machine[machine_id], color="red", linestyle="--", label="Incident onset")
            ax.set_title(f"{machine_id} — {titles_by_machine[machine_id]}")
        else:
            ax.set_title(f"{machine_id} — healthy control (no incident)")

        ax.set_ylabel("Defect rate (rolling)")
        ax.legend()

    axes[-1].set_xlabel("Production Cycle")
    plt.tight_layout()
    plt.savefig("data/defect_rate_by_machine.png")
    plt.show()