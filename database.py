import sqlite3

# Connect to SQLite database
conn = sqlite3.connect("crm.db")

# Cursor is used to execute SQL commands
cursor = conn.cursor()


# 1. LEADS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS leads (
    lead_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT NOT NULL,
    lead_type TEXT CHECK (lead_type IN ('B2C', 'B2B')),
    source TEXT,
    course_enquired TEXT,
    current_stage TEXT CHECK (
        current_stage IN (
            'newlead',
            'followup',
            'prospect',
            'walkin',
            'registered',
            'closed'
        )
    ),
    assigned_counselor TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")


# 2. FOLLOWUPS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS followups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id TEXT,
    followup_number INTEGER DEFAULT 1,
    call_status TEXT CHECK (
        call_status IN (
            'connected',
            'busy',
            'callback',
            'not_reachable'
        )
    ),
    discussion_summary TEXT,
    sentiment TEXT DEFAULT 'Neutral',
    next_followup_date DATE,
    counselor TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (lead_id)
        REFERENCES leads(lead_id)
        ON DELETE CASCADE
)
""")


# 3. PROSPECTS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS prospects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id TEXT,
    preferred_course TEXT,
    preferred_batch_type TEXT CHECK (
        preferred_batch_type IN (
            'weekday',
            'weekend',
            'fastrack'
        )
    ),
    preferred_class_mode TEXT CHECK (
        preferred_class_mode IN (
            'offline',
            'online',
            'hybrid'
        )
    ),
    budget DECIMAL(10,2),
    interest_rating TEXT CHECK (
        interest_rating IN ('Hot', 'Warm', 'Cold')
    ),
    expected_joining_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (lead_id)
        REFERENCES leads(lead_id)
        ON DELETE CASCADE
)
""")


# 4. WALK-IN TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS walkin_stages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id TEXT,
    visit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    branch_location TEXT,
    counselor_met TEXT,
    demo_session_attended BOOLEAN DEFAULT FALSE,
    token_number TEXT,
    counselor_notes TEXT,

    FOREIGN KEY (lead_id)
        REFERENCES leads(lead_id)
        ON DELETE CASCADE
)
""")


# 5. REGISTRATIONS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id TEXT UNIQUE,
    course_enrolled TEXT,
    trainer_assigned TEXT,
    total_fee DECIMAL(10,2),
    paid_fee DECIMAL(10,2),
    pending_fee DECIMAL(10,2) DEFAULT 0.0,
    payment_mode TEXT CHECK (
        payment_mode IN (
            'upi',
            'card',
            'netbanking',
            'cash',
            'emi'
        )
    ),
    batch_start_date DATE,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (lead_id)
        REFERENCES leads(lead_id)
        ON DELETE CASCADE
)
""")


# 6. CLOSED LEADS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS closed_leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id TEXT UNIQUE,
    reason_for_closure TEXT CHECK (
        reason_for_closure IN (
            'fee_high',
            'competitor',
            'timing_mismatch',
            'location_far',
            'not_interested'
        )
    ),
    closing_remarks TEXT,
    closed_by TEXT,
    closed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (lead_id)
        REFERENCES leads(lead_id)
        ON DELETE CASCADE
)
""")


# 7. LEAD REMARKS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS lead_remarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id TEXT,
    remark_type TEXT CHECK (
        remark_type IN (
            'counselor_note',
            'supervisor_feedback',
            'quality_audit'
        )
    ),
    remark_text TEXT,
    created_by TEXT,
    target_employee TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (lead_id)
        REFERENCES leads(lead_id)
        ON DELETE CASCADE
)
""")


# 8. CALL RECORDINGS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS call_recordings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id TEXT,
    caller_name TEXT,
    call_duration_seconds INTEGER,
    call_status TEXT,
    transcript_summary TEXT,
    call_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (lead_id)
        REFERENCES leads(lead_id)
        ON DELETE CASCADE
)
""")


# Save changes
conn.commit()

# Close connection
conn.close()

print("CRM database and all 8 tables created successfully!")