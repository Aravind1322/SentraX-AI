import sqlite3
import os
from datetime import datetime

_LOGGED_STARTUP = False

def get_database_path() -> str:
    """
    Dynamically resolve the database path.
    1. Checks the SENTRAX_DB_PATH environment variable.
    2. Checks if backend/sentrax_backend.db exists.
    3. Falls back to data/sentrax_backend.db.
    """
    global _LOGGED_STARTUP
    env_path = os.environ.get("SENTRAX_DB_PATH")
    
    if env_path:
        resolved_path = os.path.abspath(env_path)
        is_env = True
        is_backend = False
        is_fallback = False
    else:
        is_env = False
        backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", "sentrax_backend.db"))
        if os.path.exists(backend_path):
            resolved_path = backend_path
            is_backend = True
            is_fallback = False
        else:
            resolved_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "sentrax_backend.db"))
            is_backend = False
            is_fallback = True

    # Ensure parent directory exists
    parent_dir = os.path.dirname(resolved_path)
    created_dir = False
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)
        created_dir = True

    if not _LOGGED_STARTUP:
        db_exists = os.path.exists(resolved_path)
        print(f"Resolved database path: {resolved_path}")
        print(f"Database exists: {'Yes' if db_exists else 'No'}")
        if created_dir:
            print(f"Creating data directory: {parent_dir}")
        else:
            print("Creating data directory: No (already exists)")
        
        if is_env:
            print(f"Using environment database: {resolved_path}")
        elif is_backend:
            print("Using backend database: Yes")
        elif is_fallback:
            print("Using fallback data database: Yes")
            
        _LOGGED_STARTUP = True

    return resolved_path


def init_db():
    db_path = get_database_path()
    # Ensure the parent directory exists
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    # Legacy DB file path for migration
    legacy_db = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "sentrax.db"))
    legacy_exists = os.path.exists(legacy_db)

    # Connect to unified DB
    conn = sqlite3.connect(db_path)
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
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_type      TEXT NOT NULL,
        input_data     TEXT,
        score          INTEGER DEFAULT 0,
        label          TEXT DEFAULT 'Safe',
        threat_level   TEXT NOT NULL,
        confidence     INTEGER DEFAULT 100,
        timestamp      DATETIME DEFAULT CURRENT_TIMESTAMP,
        filename       TEXT,
        result_summary TEXT,
        scan_time      TEXT
    )
    """)

    # Performance indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scans_id_desc ON scans(id DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scan_history_id_desc ON scan_history(id DESC)")
    conn.commit()

    # If legacy DB exists, run safe schema migration
    if legacy_exists:
        try:
            print(f"[FRONTEND DB] Found legacy database at {legacy_db}. Migrating records...")
            legacy_conn = sqlite3.connect(legacy_db)
            legacy_cursor = legacy_conn.cursor()

            # Migrate scans
            try:
                legacy_cursor.execute("SELECT url, label, score, timestamp FROM scans")
                legacy_scans = legacy_cursor.fetchall()
                if legacy_scans:
                    cursor.execute("SELECT url, timestamp FROM scans")
                    existing_scans = {(r[0], r[1]) for r in cursor.fetchall()}
                    new_scans = [s for s in legacy_scans if (s[0], s[3]) not in existing_scans]
                    if new_scans:
                        cursor.executemany(
                            "INSERT INTO scans (url, label, score, timestamp) VALUES (?, ?, ?, ?)",
                            new_scans
                        )
                        print(f"[FRONTEND DB] Migrated {len(new_scans)} new scans.")
            except Exception as e:
                print(f"Error migrating legacy scans table: {e}")

            # Migrate scan_history
            try:
                legacy_cursor.execute("SELECT scan_time, scan_type, filename, result_summary, threat_level FROM scan_history")
                legacy_history = legacy_cursor.fetchall()
                if legacy_history:
                    cursor.execute("SELECT scan_time, filename FROM scan_history")
                    existing_history = {(r[0], r[1]) for r in cursor.fetchall()}
                    new_history = [h for h in legacy_history if (h[0], h[2]) not in existing_history]
                    if new_history:
                        cursor.executemany(
                            """
                            INSERT INTO scan_history (scan_time, scan_type, filename, result_summary, threat_level, input_data, score, label, confidence)
                            VALUES (?, ?, ?, ?, ?, ?, 0, 'Safe', 100)
                            """,
                            [(h[0], h[1], h[2], h[3], h[4], h[2]) for h in new_history]
                        )
                        print(f"[FRONTEND DB] Migrated {len(new_history)} new scan_history records.")
            except Exception as e:
                print(f"Error migrating legacy scan_history table: {e}")

            legacy_conn.close()
            conn.commit()

            # Rename legacy DB so we don't try to migrate it again
            try:
                if os.path.exists(legacy_db + ".bak"):
                    os.remove(legacy_db + ".bak")
                os.rename(legacy_db, legacy_db + ".bak")
                print(f"[FRONTEND DB] Renamed legacy database to {legacy_db}.bak")
            except Exception as rename_err:
                print(f"Error renaming legacy database: {rename_err}")
        except Exception as mig_err:
            print(f"Error during legacy database migration: {mig_err}")

    conn.close()
    
    migrate_existing_html_records()
    migrate_existing_html_scans()


def migrate_existing_html_records():
    import re
    conn = sqlite3.connect(get_database_path())
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
    conn = sqlite3.connect(get_database_path())
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO scan_history (scan_time, scan_type, filename, result_summary, threat_level, input_data, score, label, confidence)
    VALUES (?, ?, ?, ?, ?, ?, 0, 'Safe', 100)
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), scan_type, filename, result_summary, threat_level, filename))
    conn.commit()
    conn.close()


def get_history_scans(limit=100):
    conn = sqlite3.connect(get_database_path())
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
    conn = sqlite3.connect(get_database_path())
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
    conn = sqlite3.connect(get_database_path())
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO scans (url, label, score, timestamp)
    VALUES (?, ?, ?, ?)
    """, (url, label, score, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()


def get_recent_scans(limit=10):
    conn = sqlite3.connect(get_database_path())
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