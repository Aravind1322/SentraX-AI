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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scan_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_time TEXT,
        scan_type TEXT,
        filename TEXT,
        result_summary TEXT,
        threat_level TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_history_scan(scan_type, filename, result_summary, threat_level):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO scan_history (scan_time, scan_type, filename, result_summary, threat_level)
    VALUES (?, ?, ?, ?, ?)
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), scan_type, filename, result_summary, threat_level))
    conn.commit()
    conn.close()


def get_history_scans(limit=100):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT scan_time, scan_type, filename, result_summary, threat_level
    FROM scan_history
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows


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