import sqlite3
from datetime import datetime

DB_PATH = "data/sentrax.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        label TEXT,
        score INTEGER,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_scan(url, label, score):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO scans (url, label, score, timestamp)
    VALUES (?, ?, ?, ?)
    """, (url, label, score, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()


def get_recent_scans(limit=10):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT url, label, score, timestamp
    FROM scans
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return rows