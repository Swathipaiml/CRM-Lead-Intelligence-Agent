import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect("crm.db")
cursor = conn.cursor()

today = datetime.now()

leads = [
    ("L001", "Ananya Rao", "ananya@gmail.com", "9876500001",
     "B2C", "LinkedIn", "Python", "prospect", "Priya Sharma", today - timedelta(days=2)),

    ("L002", "Rahul Kumar", "rahul@gmail.com", "9876500002",
     "B2C", "Meta Ads", "Java", "registered", "Priya Sharma", today - timedelta(days=5)),

    ("L003", "Sneha Reddy", "sneha@gmail.com", "9876500003",
     "B2C", "Website", "Data Science", "followup", "Arjun Rao", today - timedelta(days=8)),

    ("L004", "Arjun Mehta", "arjun@gmail.com", "9876500004",
     "B2C", "Referral", "AI/ML", "closed", "Priya Sharma", today - timedelta(days=20)),

    ("L005", "Kiran Patel", "kiran@gmail.com", "9876500005",
     "B2C", "LinkedIn", "Data Science", "newlead", "Priya Sharma", today - timedelta(days=3)),

    ("L006", "Meera Nair", "meera@gmail.com", "9876500006",
     "B2C", "Meta Ads", "Python", "prospect", "Arjun Rao", today - timedelta(days=7)),

    ("L007", "Rohan Singh", "rohan@gmail.com", "9876500007",
     "B2C", "Google Ads", "Java", "walkin", "Neha Gupta", today - timedelta(days=12)),

    ("L008", "Divya Shetty", "divya@gmail.com", "9876500008",
     "B2C", "Website", "AI/ML", "registered", "Priya Sharma", today - timedelta(days=18)),

    ("L009", "Vishal Jain", "vishal@gmail.com", "9876500009",
     "B2B", "LinkedIn", "Data Analytics", "prospect", "Arjun Rao", today - timedelta(days=4)),

    ("L010", "Pooja Verma", "pooja@gmail.com", "9876500010",
     "B2C", "Referral", "Python", "closed", "Neha Gupta", today - timedelta(days=25)),

    ("L011", "Aditi Shah", "aditi@gmail.com", "9876500011",
     "B2C", "Meta Ads", "Java", "newlead", "Priya Sharma", today - timedelta(days=1)),

    ("L012", "Manoj Das", "manoj@gmail.com", "9876500012",
     "B2C", "Google Ads", "Data Science", "followup", "Arjun Rao", today - timedelta(days=10)),

    ("L013", "Neha Kapoor", "neha@gmail.com", "9876500013",
     "B2C", "LinkedIn", "AI/ML", "registered", "Neha Gupta", today - timedelta(days=6)),

    ("L014", "Sanjay Rao", "sanjay@gmail.com", "9876500014",
     "B2C", "Website", "Python", "walkin", "Priya Sharma", today - timedelta(days=9)),

    ("L015", "Ishita Roy", "ishita@gmail.com", "9876500015",
     "B2C", "Meta Ads", "Data Analytics", "prospect", "Neha Gupta", today - timedelta(days=11)),

    ("L016", "Varun Joshi", "varun@gmail.com", "9876500016",
     "B2C", "Referral", "Java", "closed", "Arjun Rao", today - timedelta(days=30)),

    ("L017", "Nisha Menon", "nisha@gmail.com", "9876500017",
     "B2C", "LinkedIn", "Python", "followup", "Priya Sharma", today - timedelta(days=13)),

    ("L018", "Akash Gupta", "akash@gmail.com", "9876500018",
     "B2C", "Google Ads", "AI/ML", "registered", "Neha Gupta", today - timedelta(days=15)),

    ("L019", "Riya Sharma", "riya@gmail.com", "9876500019",
     "B2C", "Meta Ads", "Data Science", "newlead", "Priya Sharma", today - timedelta(days=4)),

    ("L020", "Karthik Rao", "karthik@gmail.com", "9876500020",
     "B2C", "Website", "Java", "prospect", "Arjun Rao", today - timedelta(days=6)),
]


cursor.executemany("""
INSERT OR IGNORE INTO leads (
    lead_id,
    name,
    email,
    phone,
    lead_type,
    source,
    course_enquired,
    current_stage,
    assigned_counselor,
    created_at
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", leads)

# --------------------------------------------------
# FOLLOWUPS
# --------------------------------------------------

followups = [
    # lead_id, number, status, summary, sentiment,
    # next_followup_date, counselor, created_at

    ("L003", 1, "connected",
     "Interested but wants time to decide",
     "Hesitant",
     (today - timedelta(days=2)).date(),
     "Arjun Rao",
     today - timedelta(days=5)),

    ("L006", 1, "callback",
     "Interested in Python course",
     "Positive",
     (today + timedelta(days=2)).date(),
     "Arjun Rao",
     today - timedelta(days=3)),

    ("L012", 1, "connected",
     "Concerned about course fee",
     "Negative",
     (today - timedelta(days=3)).date(),
     "Arjun Rao",
     today - timedelta(days=6)),

    ("L017", 1, "not_reachable",
     "Unable to contact lead",
     "Neutral",
     (today - timedelta(days=1)).date(),
     "Priya Sharma",
     today - timedelta(days=8)),

    ("L001", 1, "connected",
     "Very interested in joining",
     "Positive",
     (today + timedelta(days=3)).date(),
     "Priya Sharma",
     today - timedelta(days=2))
]

cursor.executemany("""
INSERT INTO followups (
    lead_id,
    followup_number,
    call_status,
    discussion_summary,
    sentiment,
    next_followup_date,
    counselor,
    created_at
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", followups)
# --------------------------------------------------
# PROSPECTS
# --------------------------------------------------

prospects = [

    ("L001", "Python", "weekend", "offline",
     50000, "Hot",
     (today + timedelta(days=15)).date()),

    ("L006", "Python", "weekend", "offline",
     45000, "Warm",
     (today + timedelta(days=20)).date()),

    ("L009", "Data Analytics", "weekday", "online",
     60000, "Hot",
     (today + timedelta(days=10)).date()),

    ("L015", "Data Analytics", "weekend", "offline",
     55000, "Warm",
     (today + timedelta(days=25)).date()),

    ("L020", "Java", "weekday", "hybrid",
     35000, "Cold",
     (today + timedelta(days=30)).date())
]

cursor.executemany("""
INSERT INTO prospects (
    lead_id,
    preferred_course,
    preferred_batch_type,
    preferred_class_mode,
    budget,
    interest_rating,
    expected_joining_date
)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", prospects)
# --------------------------------------------------
# WALK-IN STAGES
# --------------------------------------------------

walkins = [

    ("L007",
     today - timedelta(days=4),
     "Chennai",
     "Neha Gupta",
     True,
     "T101",
     "Attended demo and showed interest"),

    ("L014",
     today - timedelta(days=3),
     "Chennai",
     "Priya Sharma",
     True,
     "T102",
     "Liked the demo but needs time"),

    ("L002",
     today - timedelta(days=10),
     "Bangalore",
     "Priya Sharma",
     True,
     "T103",
     "Demo completed successfully"),

    ("L018",
     today - timedelta(days=12),
     "Bangalore",
     "Neha Gupta",
     True,
     "T104",
     "Interested and later registered")
]

cursor.executemany("""
INSERT INTO walkin_stages (
    lead_id,
    visit_date,
    branch_location,
    counselor_met,
    demo_session_attended,
    token_number,
    counselor_notes
)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", walkins)
# --------------------------------------------------
# REGISTRATIONS
# --------------------------------------------------

registrations = [

    ("L002", "Java", "Vikram",
     60000, 35000, 25000,
     "upi",
     (today + timedelta(days=10)).date()),

    ("L008", "AI/ML", "Vikram",
     80000, 50000, 30000,
     "emi",
     (today + timedelta(days=15)).date()),

    ("L013", "AI/ML", "Anil",
     75000, 60000, 15000,
     "card",
     (today + timedelta(days=12)).date()),

    ("L018", "AI/ML", "Vikram",
     70000, 70000, 0,
     "upi",
     (today + timedelta(days=5)).date())
]

cursor.executemany("""
INSERT INTO registrations (
    lead_id,
    course_enrolled,
    trainer_assigned,
    total_fee,
    paid_fee,
    pending_fee,
    payment_mode,
    batch_start_date
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", registrations)
# --------------------------------------------------
# CLOSED LEADS
# --------------------------------------------------

closed_leads = [

    ("L004",
     "fee_high",
     "Student felt course fee was too high",
     "Priya Sharma"),

    ("L010",
     "competitor",
     "Joined another training institute",
     "Neha Gupta"),

    ("L016",
     "fee_high",
     "Could not afford the course",
     "Arjun Rao")
]

cursor.executemany("""
INSERT INTO closed_leads (
    lead_id,
    reason_for_closure,
    closing_remarks,
    closed_by
)
VALUES (?, ?, ?, ?)
""", closed_leads)
# --------------------------------------------------
# LEAD REMARKS
# --------------------------------------------------

remarks = [

    ("L003",
     "supervisor_feedback",
     "Lead requires immediate follow-up",
     "Supervisor",
     "Arjun Rao"),

    ("L007",
     "counselor_note",
     "Interested after demo session",
     "Neha Gupta",
     "Neha Gupta"),

    ("L012",
     "supervisor_feedback",
     "Potential lead is being neglected",
     "Supervisor",
     "Arjun Rao"),

    ("L015",
     "quality_audit",
     "Communication quality was good",
     "Quality Team",
     "Neha Gupta")
]

cursor.executemany("""
INSERT INTO lead_remarks (
    lead_id,
    remark_type,
    remark_text,
    created_by,
    target_employee
)
VALUES (?, ?, ?, ?, ?)
""", remarks)
# --------------------------------------------------
# CALL RECORDINGS
# --------------------------------------------------

call_recordings = [

    ("L004",
     "Priya Sharma",
     420,
     "Completed",
     "Lead liked the course but felt the fee was expensive"),

    ("L010",
     "Neha Gupta",
     250,
     "Completed",
     "Lead informed counselor about joining competitor"),

    ("L016",
     "Arjun Rao",
     380,
     "Completed",
     "Discussed payment options but lead declined"),

    ("L003",
     "Arjun Rao",
     180,
     "Completed",
     "Lead requested additional time to decide")
]

cursor.executemany("""
INSERT INTO call_recordings (
    lead_id,
    caller_name,
    call_duration_seconds,
    call_status,
    transcript_summary
)
VALUES (?, ?, ?, ?, ?)
""", call_recordings)

conn.commit()
conn.close()

print("All CRM fake data inserted successfully!")