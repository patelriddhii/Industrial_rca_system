-- ============================================================
-- Machines: static reference table
-- ============================================================
CREATE TABLE machines (
    machine_id TEXT PRIMARY KEY,
    machine_type TEXT NOT NULL,
    description TEXT
);

-- ============================================================
-- Production cycles: one row per machine per cycle
-- ============================================================
CREATE TABLE production_cycles (
    production_id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine_id TEXT NOT NULL,
    cycle INTEGER NOT NULL,
    cycle_time REAL,
    defect INTEGER,
    maintenance_event INTEGER,
    maintenance_action TEXT,
    downtime_event INTEGER,
    active_batch_id TEXT,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id),
    FOREIGN KEY (active_batch_id) REFERENCES material_batches(batch_id)
);

-- ============================================================
-- Sensor readings: long format, one row per machine/cycle/sensor
-- ============================================================
CREATE TABLE sensor_readings (
    reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine_id TEXT NOT NULL,
    cycle INTEGER NOT NULL,
    sensor_name TEXT NOT NULL,
    sensor_value REAL,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id)
);

-- ============================================================
-- Maintenance orders
-- ============================================================
CREATE TABLE maintenance_orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine_id TEXT NOT NULL,
    cycle INTEGER NOT NULL,
    action TEXT,
    reason TEXT,
    technician_notes TEXT,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id)
);

-- ============================================================
-- Material batches
-- ============================================================
CREATE TABLE material_batches (
    batch_id TEXT PRIMARY KEY,
    supplier TEXT,
    quality_score REAL,
    introduced_cycle INTEGER,
    duration_cycles INTEGER,
    is_incident_batch INTEGER
);

-- ============================================================
-- Incidents: ground truth. Treat as append-only / immutable.
-- ============================================================
CREATE TABLE incidents (
    incident_id INTEGER PRIMARY KEY,
    machine_id TEXT NOT NULL,
    start_cycle INTEGER NOT NULL,
    root_cause TEXT NOT NULL,
    description TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id)
);

-- ============================================================
-- Hypotheses: agent-generated, populated starting Phase 5
-- ============================================================
CREATE TABLE hypotheses (
    hypothesis_id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER NOT NULL,
    source_agent TEXT NOT NULL,
    hypothesis_text TEXT NOT NULL,
    confidence REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id)
);

-- ============================================================
-- Evidence items: atomic evidence with provenance
-- ============================================================
CREATE TABLE evidence_items (
    evidence_id INTEGER PRIMARY KEY AUTOINCREMENT,
    hypothesis_id INTEGER NOT NULL,
    source_agent TEXT NOT NULL,
    source_table TEXT NOT NULL,
    source_record_id INTEGER,
    evidence_description TEXT,
    supports_or_contradicts TEXT CHECK (supports_or_contradicts IN ('supports', 'contradicts', 'neutral')),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hypothesis_id) REFERENCES hypotheses(hypothesis_id)
);

-- ============================================================
-- Verification results: cross-agent verdicts on hypotheses
-- ============================================================
CREATE TABLE verification_results (
    verification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    hypothesis_id INTEGER NOT NULL,
    verifying_agent TEXT NOT NULL,
    verdict TEXT CHECK (verdict IN ('support', 'contradict', 'insufficient')),
    rationale TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hypothesis_id) REFERENCES hypotheses(hypothesis_id)
);

-- ============================================================
-- Corrective actions
-- ============================================================
CREATE TABLE corrective_actions (
    action_id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER NOT NULL,
    recommended_action TEXT,
    rationale TEXT,
    human_decision TEXT CHECK (human_decision IN ('accept', 'modify', 'reject') OR human_decision IS NULL),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id)
);

-- ============================================================
-- Indexes for the joins/queries agents will run constantly
-- ============================================================
CREATE INDEX idx_production_machine_cycle ON production_cycles(machine_id, cycle);
CREATE INDEX idx_sensor_machine_cycle ON sensor_readings(machine_id, cycle);
CREATE INDEX idx_maintenance_machine_cycle ON maintenance_orders(machine_id, cycle);
CREATE INDEX idx_hypotheses_incident ON hypotheses(incident_id);
CREATE INDEX idx_evidence_hypothesis ON evidence_items(hypothesis_id);
CREATE INDEX idx_verification_hypothesis ON verification_results(hypothesis_id);