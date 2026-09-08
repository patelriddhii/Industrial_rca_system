import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class ToolWearMachine:
    """Machine failure mode: progressive tool wear affecting both cycle time and defects."""

    MACHINE_TYPE = "tool_wear_machine"
    MAINTENANCE_INTERVAL = 100
    INCIDENT_START_CYCLE = 615
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
    INCIDENT_START_CYCLE = 385
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
    MAINTENANCE_INTERVAL = 150
    INCIDENT_START_CYCLE = 520
    INCIDENT_MULTIPLIER = 3.5
    TEMPERATURE_LAG_FACTOR = 0.1

    def __init__(self, machine_id):
        self.machine_id = machine_id
        self.bearing_degradation = 0.0
        self.temperature = 40.0

    def run_cycle(self, cycle_number):
        degradation_increment = np.random.uniform(0.01, 0.03)
        if cycle_number >= self.INCIDENT_START_CYCLE:
            degradation_increment *= self.INCIDENT_MULTIPLIER
        self.bearing_degradation += degradation_increment

        maintenance_event = False
        if cycle_number % self.MAINTENANCE_INTERVAL == 0:
            self.bearing_degradation = 0.0
            maintenance_event = True

        vibration = 0.5 + (self.bearing_degradation * 0.4) + np.random.uniform(-0.05, 0.05)

        temperature_target = 40 + (self.bearing_degradation * 3.0)
        self.temperature += (temperature_target - self.temperature) * self.TEMPERATURE_LAG_FACTOR
        self.temperature += np.random.uniform(-0.3, 0.3)

        motor_current = 5.0 + (self.bearing_degradation * 0.35) + np.random.uniform(-0.1, 0.1)

        cycle_time = 10 + (self.bearing_degradation * 0.8)

        downtime_probability = min(max(0.0, (self.bearing_degradation - 5.0) * 0.03), 0.6)
        downtime = np.random.random() < downtime_probability

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


class MaterialBatch:
    """Represents one raw-material batch loaded into a machine.
    Not a Machine subclass — this is external context fed into MaterialBatchMachine."""

    def __init__(self, batch_id, quality_score, supplier, introduced_cycle,
                 duration_cycles, is_incident_batch=False):
        self.batch_id = batch_id
        self.quality_score = quality_score  # 0.0 (bad) to 1.0 (good)
        self.supplier = supplier
        self.introduced_cycle = introduced_cycle
        self.duration_cycles = duration_cycles
        self.is_incident_batch = is_incident_batch


def generate_batch_schedule(n_cycles=1000, batch_duration=100,
                             incident_batch_index=6, incident_quality=0.35):
    """Creates a sequential, non-overlapping batch schedule covering the full run.
    One batch (by index, 0-based) is deliberately marked defective."""
    n_batches = n_cycles // batch_duration
    batches = []
    for i in range(n_batches):
        is_incident = (i == incident_batch_index)
        quality = incident_quality if is_incident else np.random.uniform(0.85, 0.98)
        batches.append(MaterialBatch(
            batch_id=f"B{100 + i}",
            quality_score=quality,
            supplier="SupplierA" if i % 2 == 0 else "SupplierB",
            introduced_cycle=(i * batch_duration) + 1,
            duration_cycles=batch_duration,
            is_incident_batch=is_incident
        ))
    return batches


def get_active_batch(cycle_number, batches):
    """Finds which batch is active at a given cycle."""
    for batch in batches:
        if batch.introduced_cycle <= cycle_number < batch.introduced_cycle + batch.duration_cycles:
            return batch
    return batches[-1]


class MaterialBatchMachine:
    """Machine failure mode: defects driven entirely by raw-material batch quality,
    NOT by machine condition. Machine telemetry stays healthy throughout — this is
    the key property that lets the Maintenance Agent correctly CONTRADICT a mechanical
    hypothesis while Material/Quality agents SUPPORT a batch-related one.

    Defect pressure uses exponential smoothing toward the active batch's quality,
    producing gradual onset AND gradual recovery rather than an instant step —
    simulating inspection lag and residual bad units still in the pipeline.
    """

    MACHINE_TYPE = "material_batch_machine"
    MAINTENANCE_INTERVAL = 100
    SMOOTHING_ALPHA = 0.06  # lower = slower response to batch quality changes

    def __init__(self, machine_id):
        self.machine_id = machine_id
        self.machine_health = 0.0  # stays boring, like M3 — machine itself is fine
        self.defect_pressure = 0.05  # starts low/normal

    def run_cycle(self, cycle_number, active_batch):
        self.machine_health += np.random.uniform(0.01, 0.03)

        maintenance_event = False
        if cycle_number % self.MAINTENANCE_INTERVAL == 0:
            self.machine_health = 0.0
            maintenance_event = True

        cycle_time = 10 + np.random.uniform(-0.3, 0.3)

        batch_defect_target = (1 - active_batch.quality_score) * 0.6
        self.defect_pressure = (
            self.SMOOTHING_ALPHA * batch_defect_target
            + (1 - self.SMOOTHING_ALPHA) * self.defect_pressure
        )

        defect_probability = min(0.02 + self.defect_pressure, 0.9)
        defect = np.random.random() < defect_probability

        production_record = {
            "machine_id": self.machine_id,
            "machine_type": self.MACHINE_TYPE,
            "cycle": cycle_number,
            "cycle_time": cycle_time,
            "defect": int(defect),
            "maintenance_event": int(maintenance_event),
            "maintenance_action": "routine_check" if maintenance_event else None,
            "active_batch_id": active_batch.batch_id
        }

        sensor_readings = [
            {"machine_id": self.machine_id, "cycle": cycle_number,
             "sensor_name": "machine_health", "sensor_value": self.machine_health},
            {"machine_id": self.machine_id, "cycle": cycle_number,
             "sensor_name": "defect_pressure", "sensor_value": self.defect_pressure},
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
    m5 = MaterialBatchMachine(machine_id="M5")
    batch_schedule = generate_batch_schedule(n_cycles=n_cycles)

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

        active_batch = get_active_batch(cycle, batch_schedule)
        production_record, sensor_readings = m5.run_cycle(cycle, active_batch)
        production_data.append(production_record)
        sensor_data.extend(sensor_readings)
        if production_record["maintenance_event"]:
            maintenance_log.append({
                "machine_id": m5.machine_id,
                "cycle": cycle,
                "action": production_record["maintenance_action"],
                "reason": "scheduled_maintenance"
            })

    production_df = pd.DataFrame(production_data)
    sensor_df = pd.DataFrame(sensor_data)
    maintenance_df = pd.DataFrame(maintenance_log)

    batches_df = pd.DataFrame([{
        "batch_id": b.batch_id,
        "supplier": b.supplier,
        "quality_score": b.quality_score,
        "introduced_cycle": b.introduced_cycle,
        "duration_cycles": b.duration_cycles,
        "is_incident_batch": b.is_incident_batch
    } for b in batch_schedule])

    incident_batch = next(b for b in batch_schedule if b.is_incident_batch)

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
        },
        {
            "incident_id": 4,
            "machine_id": "M5",
            "start_cycle": incident_batch.introduced_cycle,
            "root_cause": "defective_material_batch",
            "description": f"Batch {incident_batch.batch_id} introduced with "
                            f"quality_score={incident_batch.quality_score:.2f}; "
                            f"machine telemetry remained normal throughout"
        }
    ])

    return production_df, sensor_df, maintenance_df, incidents_df, batches_df


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    production_df, sensor_df, maintenance_df, incidents_df, batches_df = run_simulation(n_cycles=1000)

    production_df.to_csv("data/machine_data.csv", index=False)
    sensor_df.to_csv("data/sensor_readings.csv", index=False)
    maintenance_df.to_csv("data/maintenance_log.csv", index=False)
    incidents_df.to_csv("data/incidents.csv", index=False)
    batches_df.to_csv("data/material_batches.csv", index=False)

    print("Data saved successfully!")
    print(f"\nTotal maintenance events: {len(maintenance_df)}")
    print(maintenance_df["action"].value_counts())
    print(f"\nProduction data sample:\n{production_df.head()}")
    print(f"\nSensor data sample:\n{sensor_df.head()}")
    print(f"\nBatch schedule:\n{batches_df}")

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

    # M4 telemetry signature: vibration/temperature/motor_current should rise
    # together post-incident while defect rate (above) barely moves
    m4_sensors = sensor_df[sensor_df["machine_id"] == "M4"]
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    for sensor_name in ["vibration", "temperature", "motor_current"]:
        subset = m4_sensors[m4_sensors["sensor_name"] == sensor_name]
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

    # M5 diagnostic: defect rate should pulse around the incident batch window
    # (gradual rise, gradual decay), while machine_health sensor stays flat throughout —
    # proving this incident is batch-driven, not machine-driven
    m5_prod = production_df[production_df["machine_id"] == "M5"].copy()
    m5_prod["rolling_defect_rate"] = m5_prod["defect"].rolling(window=20).mean()
    incident_row = batches_df[batches_df["is_incident_batch"]].iloc[0]

    fig3, ax3 = plt.subplots(figsize=(10, 5))
    ax3.plot(m5_prod["cycle"], m5_prod["rolling_defect_rate"], label="M5 defect rate")
    ax3.axvspan(incident_row["introduced_cycle"],
                incident_row["introduced_cycle"] + incident_row["duration_cycles"],
                color="red", alpha=0.15, label=f"Bad batch {incident_row['batch_id']} active")
    ax3.set_title("M5 — Material Batch Defect Pattern (should pulse, not step)")
    ax3.set_xlabel("Production Cycle")
    ax3.set_ylabel("Defect rate (rolling)")
    ax3.legend()
    plt.tight_layout()
    plt.savefig("data/m5_batch_pattern.png")
    plt.show()