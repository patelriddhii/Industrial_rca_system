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

        cycle_time = 10 + (self.tool_wear * 2)
        defect_probability = min(0.01 + (self.tool_wear * 0.015), 0.9)
        defect = np.random.random() < defect_probability

        production_record = {
            "machine_id": self.machine_id,
            "machine_type": self.MACHINE_TYPE,
            "cycle": cycle_number,
            "cycle_time": cycle_time,
            "defect": int(defect),
            "maintenance_event": int(maintenance_event),
            "maintenance_action": "tool_replacement" if maintenance_event else None
        }

        sensor_readings = [
            {"machine_id": self.machine_id, "cycle": cycle_number,
             "sensor_name": "tool_wear", "sensor_value": self.tool_wear}
        ]

        return production_record, sensor_readings


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

        cycle_time = 10 + np.random.uniform(-0.3, 0.3)
        defect_probability = min(0.01 + (self.calibration_offset * 0.018), 0.9)
        defect = np.random.random() < defect_probability

        production_record = {
            "machine_id": self.machine_id,
            "machine_type": self.MACHINE_TYPE,
            "cycle": cycle_number,
            "cycle_time": cycle_time,
            "defect": int(defect),
            "maintenance_event": int(maintenance_event),
            "maintenance_action": "recalibration" if maintenance_event else None
        }

        sensor_readings = [
            {"machine_id": self.machine_id, "cycle": cycle_number,
             "sensor_name": "calibration_offset", "sensor_value": self.calibration_offset}
        ]

        return production_record, sensor_readings


class HealthyControlMachine:
    """Control machine: normal wear-and-tear only, NO incident ever injected."""

    MACHINE_TYPE = "healthy_control_machine"
    MAINTENANCE_INTERVAL = 100

    def __init__(self, machine_id):
        self.machine_id = machine_id
        self.component_condition = 0.0

    def run_cycle(self, cycle_number):
        condition_increment = np.random.uniform(0.01, 0.03)
        self.component_condition += condition_increment

        maintenance_event = False
        if cycle_number % self.MAINTENANCE_INTERVAL == 0:
            self.component_condition = 0.0
            maintenance_event = True

        cycle_time = 10 + np.random.uniform(-0.3, 0.3)
        defect_probability = min(0.01 + (self.component_condition * 0.008), 0.15)
        defect = np.random.random() < defect_probability

        production_record = {
            "machine_id": self.machine_id,
            "machine_type": self.MACHINE_TYPE,
            "cycle": cycle_number,
            "cycle_time": cycle_time,
            "defect": int(defect),
            "maintenance_event": int(maintenance_event),
            "maintenance_action": "routine_check" if maintenance_event else None
        }

        sensor_readings = [
            {"machine_id": self.machine_id, "cycle": cycle_number,
             "sensor_name": "component_condition", "sensor_value": self.component_condition}
        ]

        return production_record, sensor_readings


class BearingDegradationMachine:
    """Machine failure mode: gradual bearing/mechanical degradation.
    Evidence is primarily visible through machine-health telemetry
    (vibration, temperature, motor current), not just defect rate —
    this gives the Maintenance Agent a scenario where it owns the strongest signal.

    Causal chain: bearing_degradation -> vibration (immediate)
                                       -> temperature (lagged, follows vibration)
                                       -> motor_current (immediate)
                                       -> cycle_time (small, gradual)
                                       -> downtime_risk (only significant late in degradation)
    """

    MACHINE_TYPE = "bearing_degradation_machine"
    MAINTENANCE_INTERVAL = 150  # bearings inspected/replaced less frequently than tools
    INCIDENT_START_CYCLE = 500
    INCIDENT_MULTIPLIER = 3.5
    TEMPERATURE_LAG_FACTOR = 0.1  # temperature moves toward vibration-driven target gradually

    def __init__(self, machine_id):
        self.machine_id = machine_id
        self.bearing_degradation = 0.0
        self.temperature = 40.0  # baseline ambient-ish operating temperature

    def run_cycle(self, cycle_number):
        degradation_increment = np.random.uniform(0.01, 0.03)
        if cycle_number >= self.INCIDENT_START_CYCLE:
            degradation_increment *= self.INCIDENT_MULTIPLIER
        self.bearing_degradation += degradation_increment

        maintenance_event = False
        if cycle_number % self.MAINTENANCE_INTERVAL == 0:
            self.bearing_degradation = 0.0
            maintenance_event = True

        # Vibration reacts immediately to current degradation level
        vibration = 0.5 + (self.bearing_degradation * 0.4) + np.random.uniform(-0.05, 0.05)

        # Temperature lags behind — moves gradually toward a degradation-driven target
        # rather than jumping instantly, simulating thermal inertia
        temperature_target = 40 + (self.bearing_degradation * 3.0)
        self.temperature += (temperature_target - self.temperature) * self.TEMPERATURE_LAG_FACTOR
        self.temperature += np.random.uniform(-0.3, 0.3)

        # Motor current rises as the motor works harder against a degrading bearing
        motor_current = 5.0 + (self.bearing_degradation * 0.35) + np.random.uniform(-0.1, 0.1)

        # Cycle time increases only gradually — mechanical degradation slows
        # the machine down less directly than tool wear does
        cycle_time = 10 + (self.bearing_degradation * 0.8)

        # Downtime risk only becomes meaningful once degradation is well advanced
        downtime_probability = min(max(0.0, (self.bearing_degradation - 5.0) * 0.03), 0.6)
        downtime = np.random.random() < downtime_probability

        # Defects rise only mildly — this failure mode is primarily a maintenance
        # signal, not primarily a quality signal, by design
        defect_probability = min(0.01 + (self.bearing_degradation * 0.006), 0.5)
        defect = np.random.random() < defect_probability

        production_record = {
            "machine_id": self.machine_id,
            "machine_type": self.MACHINE_TYPE,
            "cycle": cycle_number,
            "cycle_time": cycle_time,
            "defect": int(defect),
            "downtime_event": int(downtime),
            "maintenance_event": int(maintenance_event),
            "maintenance_action": "bearing_replacement" if maintenance_event else None
        }

        sensor_readings = [
            {"machine_id": self.machine_id, "cycle": cycle_number,
             "sensor_name": "bearing_degradation", "sensor_value": self.bearing_degradation},
            {"machine_id": self.machine_id, "cycle": cycle_number,
             "sensor_name": "vibration", "sensor_value": vibration},
            {"machine_id": self.machine_id, "cycle": cycle_number,
             "sensor_name": "temperature", "sensor_value": self.temperature},
            {"machine_id": self.machine_id, "cycle": cycle_number,
             "sensor_name": "motor_current", "sensor_value": motor_current},
        ]

        return production_record, sensor_readings


def run_simulation(n_cycles=1000, seed=42):
    np.random.seed(seed)

    machines = [
        ToolWearMachine(machine_id="M1"),
        CalibrationDriftMachine(machine_id="M2"),
        HealthyControlMachine(machine_id="M3"),
        BearingDegradationMachine(machine_id="M4"),
    ]

    production_data = []
    sensor_data = []
    maintenance_log = []

    for cycle in range(1, n_cycles + 1):
        for machine in machines:
            production_record, sensor_readings = machine.run_cycle(cycle)
            production_data.append(production_record)
            sensor_data.extend(sensor_readings)

            if production_record["maintenance_event"]:
                maintenance_log.append({
                    "machine_id": machine.machine_id,
                    "cycle": cycle,
                    "action": production_record["maintenance_action"],
                    "reason": "scheduled_maintenance"
                })

    production_df = pd.DataFrame(production_data)
    sensor_df = pd.DataFrame(sensor_data)
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
        },
        {
            "incident_id": 3,
            "machine_id": "M4",
            "start_cycle": BearingDegradationMachine.INCIDENT_START_CYCLE,
            "root_cause": "bearing_degradation",
            "description": "Simulated bearing fault causing 3.5x normal degradation rate, "
                            "visible primarily through vibration/temperature/motor current"
        }
    ])

    return production_df, sensor_df, maintenance_df, incidents_df


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    production_df, sensor_df, maintenance_df, incidents_df = run_simulation(n_cycles=1000)

    production_df.to_csv("data/machine_data.csv", index=False)
    sensor_df.to_csv("data/sensor_readings.csv", index=False)
    maintenance_df.to_csv("data/maintenance_log.csv", index=False)
    incidents_df.to_csv("data/incidents.csv", index=False)

    print("Data saved successfully!")
    print(f"\nTotal maintenance events: {len(maintenance_df)}")
    print(maintenance_df["action"].value_counts())
    print(f"\nProduction data sample:\n{production_df.head()}")
    print(f"\nSensor data sample:\n{sensor_df.head()}")

    machine_ids = production_df["machine_id"].unique()
    fig, axes = plt.subplots(len(machine_ids), 1, figsize=(10, 4 * len(machine_ids)), sharex=True)

    incidents_by_machine = incidents_df.set_index("machine_id")["start_cycle"].to_dict()
    titles_by_machine = incidents_df.set_index("machine_id")["root_cause"].to_dict()

    for ax, machine_id in zip(axes, machine_ids):
        machine_df = production_df[production_df["machine_id"] == machine_id].copy()
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

    # Second figure: M4's telemetry signature specifically — this is the plot
    # that should show vibration/temperature/current rising while defect rate
    # (in the plot above) barely moves, proving this is a maintenance-signal-led incident
    m4_sensors = sensor_df[sensor_df["machine_id"] == "M4"]
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    for sensor_name in ["vibration", "temperature", "motor_current"]:
        subset = m4_sensors[m4_sensors["sensor_name"] == sensor_name]
        # Normalize each sensor to 0-1 so they're visually comparable on one axis
        vals = subset["sensor_value"]
        normalized = (vals - vals.min()) / (vals.max() - vals.min())
        ax2.plot(subset["cycle"], normalized, label=sensor_name)
    ax2.axvline(x=BearingDegradationMachine.INCIDENT_START_CYCLE, color="red",
                linestyle="--", label="Incident onset")
    ax2.set_title("M4 — Bearing Degradation: Normalized Telemetry")
    ax2.set_xlabel("Production Cycle")
    ax2.set_ylabel("Normalized sensor value")
    ax2.legend()
    plt.tight_layout()
    plt.savefig("data/m4_telemetry_signature.png")
    plt.show()