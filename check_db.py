import sqlite3

conn = sqlite3.connect("crm.db")
cursor = conn.cursor()

tables = [
    "leads",
    "followups",
    "prospects",
    "walkin_stages",
    "registrations",
    "closed_leads",
    "lead_remarks",
    "call_recordings"
]

print("\n--- DATABASE CHECK ---")

for table in tables:
    count = cursor.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]

    print(f"{table}: {count}")


print("\n--- REGISTRATION JOIN TEST ---")

results = cursor.execute("""
SELECT
    leads.name,
    registrations.course_enrolled,
    registrations.pending_fee
FROM leads
JOIN registrations
ON leads.lead_id = registrations.lead_id
""").fetchall()

for row in results:
    print(row)

conn.close()