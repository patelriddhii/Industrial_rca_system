import sqlite3

conn = sqlite3.connect("data/rca_system.db")
conn.row_factory = sqlite3.Row  # lets us access columns by name

print("=" * 70)
print("QUERY 1 — Maintenance Agent style:")
print("Sensor readings for M4 in the 50 cycles before its incident onset")
print("=" * 70)

# First, get M4's incident start_cycle from ground truth
incident = conn.execute(
    "SELECT start_cycle FROM incidents WHERE machine_id = 'M4'"
).fetchone()
onset = incident["start_cycle"]

rows = conn.execute("""
    SELECT cycle, sensor_name, sensor_value
    FROM sensor_readings
    WHERE machine_id = 'M4'
      AND cycle BETWEEN ? AND ?
    ORDER BY cycle, sensor_name
""", (onset - 50, onset)).fetchall()

print(f"Incident onset at cycle {onset}. Showing first 10 of {len(rows)} readings:")
for row in rows[:10]:
    print(f"  cycle={row['cycle']:4d}  {row['sensor_name']:20s}  {row['sensor_value']:.4f}")


print("\n" + "=" * 70)
print("QUERY 2 — Material Agent style:")
print("Defect rate trend for M5 during and after the incident batch window")
print("=" * 70)

batch = conn.execute(
    "SELECT batch_id, introduced_cycle, duration_cycles, quality_score "
    "FROM material_batches WHERE is_incident_batch = 1"
).fetchone()

start = batch["introduced_cycle"]
end = start + batch["duration_cycles"]

rows = conn.execute("""
    SELECT cycle, defect, active_batch_id
    FROM production_cycles
    WHERE machine_id = 'M5'
      AND cycle BETWEEN ? AND ?
    ORDER BY cycle
""", (start, end + 100)).fetchall()  # +100 to see recovery period after batch ends

total_defects = sum(r["defect"] for r in rows)
print(f"Incident batch: {batch['batch_id']} (quality_score={batch['quality_score']:.2f}), "
      f"active cycles {start}-{end}")
print(f"Defects in window + 100-cycle recovery period: {total_defects} out of {len(rows)} cycles")
print(f"Sample rows:")
for row in rows[::20][:8]:  # every 20th row, first 8
    print(f"  cycle={row['cycle']:4d}  defect={row['defect']}  active_batch={row['active_batch_id']}")


print("\n" + "=" * 70)
print("QUERY 3 — Temporal correlation check:")
print("Was there a maintenance event on M1 shortly before its incident?")
print("=" * 70)

incident = conn.execute(
    "SELECT start_cycle FROM incidents WHERE machine_id = 'M1'"
).fetchone()
onset = incident["start_cycle"]

rows = conn.execute("""
    SELECT cycle, action, reason
    FROM maintenance_orders
    WHERE machine_id = 'M1'
      AND cycle BETWEEN ? AND ?
    ORDER BY cycle
""", (onset - 100, onset)).fetchall()

if rows:
    print(f"Incident onset at cycle {onset}. Maintenance events in prior 100 cycles:")
    for row in rows:
        cycles_before = onset - row["cycle"]
        print(f"  cycle={row['cycle']:4d} ({cycles_before} cycles before onset)  "
              f"action={row['action']}  reason={row['reason']}")
else:
    print(f"Incident onset at cycle {onset}. No maintenance events found in the prior 100 cycles.")
    print("(This is expected/correct here — M1's incident is an unrelated wear-rate spike,")
    print(" not caused by or related to a maintenance event — useful negative evidence")
    print(" for a Maintenance Agent to report as 'no maintenance correlation found'.)")

conn.close()