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

    # Performance indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scans_id_desc ON scans(id DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scan_history_id_desc ON scan_history(id DESC)")

    conn.commit()
    conn.close()
    
    migrate_existing_html_records()
    migrate_existing_html_scans()


def migrate_existing_html_records():
    import re
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scan_history'")
    if not cursor.fetchone():
        conn.close()
        return
        
    cursor.execute("SELECT id, result_summary FROM scan_history")
    rows = cursor.fetchall()
    
    updated_count = 0
    for row_id, summary in rows:
        if summary and ("<" in str(summary) or ">" in str(summary)):
            # Strip all HTML tags
            clean_summary = re.sub(r'<[^>]+>', '', str(summary))
            # Remove redundant whitespaces
            clean_summary = " ".join(clean_summary.split())
            
            if not clean_summary:
                clean_summary = "Scan completed successfully"
                
            cursor.execute(
                "UPDATE scan_history SET result_summary = ? WHERE id = ?",
                (clean_summary, row_id)
            )
            updated_count += 1
            
    if updated_count > 0:
        conn.commit()
        
    conn.close()


def save_history_scan(scan_type, filename, result_summary, threat_level):
    import re
    # Strip any HTML tags to ensure only clean plain-text is saved
    if result_summary:
        result_summary = re.sub(r'<[^>]+>', '', str(result_summary))
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


def migrate_existing_html_scans():
    import re
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scans'")
    if not cursor.fetchone():
        conn.close()
        return
        
    cursor.execute("SELECT id, url, label FROM scans")
    rows = cursor.fetchall()
    
    updated_count = 0
    for row_id, url, label in rows:
        needs_update = False
        clean_url = url
        clean_label = label
        if url and ("<" in str(url) or ">" in str(url)):
            clean_url = re.sub(r'<[^>]+>', '', str(url))
            clean_url = " ".join(clean_url.split())
            needs_update = True
        if label and ("<" in str(label) or ">" in str(label)):
            clean_label = re.sub(r'<[^>]+>', '', str(label))
            clean_label = " ".join(clean_label.split())
            needs_update = True
            
        if needs_update:
            if not clean_url:
                clean_url = "http://unknown-domain.com"
            cursor.execute(
                "UPDATE scans SET url = ?, label = ? WHERE id = ?",
                (clean_url, clean_label, row_id)
            )
            updated_count += 1
            
    if updated_count > 0:
        conn.commit()
    conn.close()


def save_scan(url, label, score):
    import re
    # Strip any HTML tags to ensure only clean plain-text is saved
    if url:
        url = re.sub(r'<[^>]+>', '', str(url))
    if label:
        label = re.sub(r'<[^>]+>', '', str(label))
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