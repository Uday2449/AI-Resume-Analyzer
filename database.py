import sqlite3

conn = sqlite3.connect("resume_analyzer.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS analyses (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    filename TEXT,

    role TEXT,

    ats_score INTEGER,

    match_score INTEGER
)
""")

conn.commit()

conn.close()

print("Database Created Successfully")