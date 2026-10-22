import sqlite3

conn = sqlite3.connect(
    "candidates.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    phone TEXT,
    skills TEXT,
    score REAL
)
""")

conn.commit()

def get_candidate(candidate_id):

    cursor.execute(
        "SELECT * FROM candidates WHERE id=?",
        (candidate_id,)
    )

    candidate = cursor.fetchone()

    return candidate