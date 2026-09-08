import sqlite3
import pandas as pd
import os

DB_PATH = "data/rca_system.db"
SCHEMA_PATH = "data/schema.sql"

def build_database():
    # Start fresh each time this is run — safe since it's rebuilt from CSVs, not hand-edited
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())

    # --- machines: derive from production_cycles' distinct machine_type per machine_id ---
    production_df = pd.read_csv("data/machine_data.csv")
    machines_df = production_df[["machine_id", "machine_type"]].drop_duplicates()
    machines_df["description"] = None
    machines_df.to_sql("machines", conn, if_exists="append", index=False)

    # --- material_batches must load BEFORE production_cycles (FK dependency) ---
    batches_df = pd.read_csv("data/material_batches.csv")
    batches_df.to_sql("material_batches", conn, if_exists="append", index=False)

    # --- production_cycles ---
    production_cols = [
        "machine_id", "cycle", "cycle_time", "defect",
        "maintenance_event", "maintenance_action", "downtime_event", "active_batch_id"
    ]
    production_df[production_cols].to_sql("production_cycles", conn, if_exists="append", index=False)

    # --- sensor_readings ---
    sensor_df = pd.read_csv("data/sensor_readings.csv")
    sensor_df.to_sql("sensor_readings", conn, if_exists="append", index=False)

    # --- maintenance_orders ---
    maintenance_df = pd.read_csv("data/maintenance_log.csv")
    maintenance_df["technician_notes"] = None
    maintenance_df.to_sql("maintenance_orders", conn, if_exists="append", index=False)

    # --- incidents ---
    incidents_df = pd.read_csv("data/incidents.csv")
    incidents_df.to_sql("incidents", conn, if_exists="append", index=False)

    conn.commit()

    # --- sanity check: row counts ---
    print("Database built successfully at", DB_PATH)
    for table in ["machines", "production_cycles", "sensor_readings",
                  "maintenance_orders", "material_batches", "incidents"]:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {count} rows")

    conn.close()


if __name__ == "__main__":
    build_database()