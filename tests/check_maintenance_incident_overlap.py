import sys
sys.path.append("simulation")
from machine import (
    ToolWearMachine, CalibrationDriftMachine,
    BearingDegradationMachine, MaterialBatchMachine
)

machines_to_check = [
    ("M1", ToolWearMachine),
    ("M2", CalibrationDriftMachine),
    ("M4", BearingDegradationMachine),
]

print("Checking for incident-onset / maintenance-interval collisions...\n")

all_clear = True
for machine_id, cls in machines_to_check:
    onset = cls.INCIDENT_START_CYCLE
    interval = cls.MAINTENANCE_INTERVAL
    distance_to_nearest_maintenance = min(onset % interval, interval - (onset % interval))

    status = "OK" if distance_to_nearest_maintenance >= 10 else "WARNING: TOO CLOSE"
    if distance_to_nearest_maintenance < 10:
        all_clear = False

    print(f"{machine_id}: onset={onset}, interval={interval}, "
          f"nearest maintenance is {distance_to_nearest_maintenance} cycles away  [{status}]")

print("\nAll clear!" if all_clear else "\nFix needed — see WARNING lines above.")