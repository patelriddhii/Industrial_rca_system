## Machine Roster (Digital Factory)

- M1 — ToolWearMachine: progressive tool wear → cycle_time ↑ + defect_rate ↑
- M2 — CalibrationDriftMachine: calibration drift → defect_rate ↑, cycle_time flat
- M3 — HealthyControlMachine: negative control, no incident
- M4 — BearingDegradationMachine: mechanical degradation → vibration ↑, temperature ↑,
       motor_current ↑, cycle_time ↑ (gradual), downtime risk ↑
       Tests: Maintenance Agent as primary evidence owner
- M5 — MaterialBatchMachine: machine stays healthy; defect_rate driven by batch quality,
       not machine state
       Tests: cross-agent contradiction handling (Maintenance CONTRADICT vs Material/Quality SUPPORT)

Canonical dataset: seed=42, n_cycles=1000 (see simulation/machine.py)