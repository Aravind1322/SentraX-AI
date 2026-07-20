"""
SentraX AI Backend — database/__init__.py
Facade module importing legacy connection helpers to ensure full backward compatibility.
"""

import sqlite3
from contextlib import contextmanager
from config import DATABASE_PATH
from typing import Optional


# ── Connection factory ─────────────────────────────────────────────────────────

@contextmanager
def get_connection():
    """Yield a SQLite connection with row_factory enabled."""
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# ── Schema init (placeholder) ──────────────────────────────────────────────────

def init_db() -> None:
    """
    Create backend-specific tables if they do not already exist,
    run safe schema migrations on scan_history, and print diagnostics.
    """
    import os
    from config import HOST, PORT, DATABASE_PATH

    # 1. Startup Diagnostics Print
    backend_url = os.environ.get("BACKEND_URL", f"http://{HOST}:{PORT}")
    db_exists = os.path.exists(DATABASE_PATH)
    db_size = os.path.getsize(DATABASE_PATH) if db_exists else 0
    
    # We open a temporary connection just to check version
    try:
        temp_conn = sqlite3.connect(DATABASE_PATH)
        db_version = temp_conn.execute("select sqlite_version()").fetchone()[0]
        temp_conn.close()
    except Exception:
        db_version = "Unknown"

    print("="*60)
    print("SENTRAX STARTUP DIAGNOSTICS")
    print("="*60)
    print(f"Backend URL: {backend_url}")
    print(f"Resolved DATABASE_PATH: {DATABASE_PATH}")
    print(f"Absolute database path: {os.path.abspath(DATABASE_PATH)}")
    print(f"Database exists: {'Yes' if db_exists else 'No'}")
    print(f"Database size: {db_size} bytes")
    print(f"Database version: {db_version}")
    print("="*60)

    try:
        # Create parent directories if missing
        db_dir = os.path.dirname(DATABASE_PATH)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        with get_connection() as conn:
            cursor = conn.cursor()

            # API request log — placeholder table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_request_log (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    endpoint    TEXT NOT NULL,
                    scan_type   TEXT,
                    result      TEXT,
                    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # scans table (for Streamlit dashboard)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT,
                    label TEXT,
                    score INTEGER,
                    timestamp TEXT
                )
            """)

            # 2. scan_history table inspection and migration
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scan_history'")
            table_exists = cursor.fetchone() is not None

            if not table_exists:
                # Create with full unified schema
                cursor.execute("""
                    CREATE TABLE scan_history (
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
                print("[INIT DB] Created scan_history table with full unified schema.")
            else:
                # Inspect columns
                cursor.execute("PRAGMA table_info(scan_history)")
                existing_cols = {row[1] for row in cursor.fetchall()}
                
                required_cols = {
                    "scan_type": "TEXT NOT NULL DEFAULT 'web_scan'",
                    "input_data": "TEXT",
                    "score": "INTEGER DEFAULT 0",
                    "label": "TEXT DEFAULT 'Safe'",
                    "threat_level": "TEXT NOT NULL DEFAULT 'LOW'",
                    "confidence": "INTEGER DEFAULT 100",
                    "timestamp": "DATETIME DEFAULT CURRENT_TIMESTAMP",
                    "filename": "TEXT",
                    "result_summary": "TEXT",
                    "scan_time": "TEXT"
                }
                
                missing_cols = {name: definition for name, definition in required_cols.items() if name not in existing_cols}
                
                if missing_cols:
                    # Count rows before migration
                    cursor.execute("SELECT COUNT(*) FROM scan_history")
                    rows_before = cursor.fetchone()[0]
                    
                    print(f"[INIT DB] scan_history table exists. Missing columns: {list(missing_cols.keys())}. Performing migration...")
                    
                    for col_name, col_def in missing_cols.items():
                        cursor.execute(f"ALTER TABLE scan_history ADD COLUMN {col_name} {col_def}")
                        print(f"  Added column: {col_name} {col_def}")
                    
                    # Count rows after migration
                    cursor.execute("SELECT COUNT(*) FROM scan_history")
                    rows_after = cursor.fetchone()[0]
                    
                    if rows_before != rows_after:
                        raise RuntimeError(f"Database integrity warning! Rows mismatch before ({rows_before}) and after ({rows_after}) migration. Aborting transaction.")
                    
                    print(f"[INIT DB] Schema migration completed successfully. Preserved {rows_after} rows.")

            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name     TEXT NOT NULL,
                    email         TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role          TEXT NOT NULL,
                    is_active     INTEGER DEFAULT 1,
                    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login    DATETIME
                )
            """)

            # Audit logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    details    TEXT,
                    timestamp  DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_id    INTEGER,
                    ip_address TEXT
                )
            """)


            # Notifications table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    title     TEXT NOT NULL,
                    message   TEXT NOT NULL,
                    severity  TEXT NOT NULL,
                    is_read   INTEGER DEFAULT 0,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key   TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

            # Threat Feeds table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS threat_feeds (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    feed_type        TEXT NOT NULL,
                    value            TEXT NOT NULL,
                    source           TEXT,
                    confidence_score INTEGER DEFAULT 80,
                    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Feed Sync Status table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feed_sync_status (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    feed_name   TEXT NOT NULL UNIQUE,
                    last_synced DATETIME,
                    status      TEXT
                )
            """)

            # IOC Records table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ioc_records (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    ioc_type   TEXT NOT NULL,
                    value      TEXT NOT NULL,
                    source     TEXT,
                    severity   TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Run schema upgrades for ioc_records if columns do not exist
            try:
                cursor.execute("ALTER TABLE ioc_records ADD COLUMN confidence INTEGER DEFAULT 80")
            except sqlite3.OperationalError:
                pass
            try:
                cursor.execute("ALTER TABLE ioc_records ADD COLUMN description TEXT DEFAULT 'Threat intelligence watchlist item'")
            except sqlite3.OperationalError:
                pass
            try:
                cursor.execute("ALTER TABLE ioc_records ADD COLUMN status TEXT DEFAULT 'Active'")
            except sqlite3.OperationalError:
                pass
            try:
                cursor.execute("ALTER TABLE ioc_records ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP")
            except sqlite3.OperationalError:
                pass

            # Create ioc_triggers history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ioc_triggers (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp  DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_email TEXT NOT NULL,
                    scanner    TEXT NOT NULL,
                    ioc_value  TEXT NOT NULL,
                    severity   TEXT NOT NULL,
                    action     TEXT NOT NULL
                )
            """)

            # Alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    title           TEXT NOT NULL,
                    description     TEXT,
                    severity        TEXT NOT NULL,
                    status          TEXT NOT NULL DEFAULT 'Unacknowledged',
                    score           INTEGER,
                    acknowledged_by TEXT,
                    acknowledged_at DATETIME,
                    timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # SOC Cases table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS soc_cases (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    title            TEXT NOT NULL,
                    description      TEXT,
                    priority         TEXT NOT NULL,
                    status           TEXT NOT NULL,
                    assigned_analyst TEXT,
                    evidence_count   INTEGER DEFAULT 0,
                    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at       DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Case Evidence table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS case_evidence (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id       INTEGER NOT NULL,
                    evidence_type TEXT NOT NULL,
                    file_name     TEXT NOT NULL,
                    file_metadata TEXT,
                    added_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(case_id) REFERENCES soc_cases(id) ON DELETE CASCADE
                )
            """)

            # Case Timeline table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS case_timeline (
                    id                INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id           INTEGER NOT NULL,
                    event_title       TEXT NOT NULL,
                    event_description TEXT,
                    event_time        DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(case_id) REFERENCES soc_cases(id) ON DELETE CASCADE
                )
            """)

            # Normalized scan_details table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scan_details (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id         INTEGER NOT NULL,
                    scan_type       TEXT NOT NULL,
                    target          TEXT,
                    score           INTEGER NOT NULL,
                    label           TEXT NOT NULL,
                    confidence      INTEGER,
                    threat_level    TEXT NOT NULL,
                    scanner_version TEXT,
                    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(scan_id) REFERENCES scan_history(id) ON DELETE CASCADE
                )
            """)

            # Normalized scan_reasons table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scan_reasons (
                    id             INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_detail_id INTEGER NOT NULL,
                    reason         TEXT NOT NULL,
                    FOREIGN KEY(scan_detail_id) REFERENCES scan_details(id) ON DELETE CASCADE
                )
            """)

            # Normalized technical_metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS technical_metrics (
                    id             INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_detail_id INTEGER NOT NULL,
                    metric_name    TEXT NOT NULL,
                    metric_value   TEXT NOT NULL,
                    FOREIGN KEY(scan_detail_id) REFERENCES scan_details(id) ON DELETE CASCADE
                )
            """)

            # Normalized recommendations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recommendations (
                    id             INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_detail_id INTEGER NOT NULL,
                    recommendation TEXT NOT NULL,
                    FOREIGN KEY(scan_detail_id) REFERENCES scan_details(id) ON DELETE CASCADE
                )
            """)

            # Normalized scan_metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scan_metadata (
                    id                INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_detail_id    INTEGER NOT NULL,
                    execution_time_ms INTEGER,
                    backend_version   TEXT,
                    api_version       TEXT,
                    engine_name       TEXT,
                    engine_version    TEXT,
                    FOREIGN KEY(scan_detail_id) REFERENCES scan_details(id) ON DELETE CASCADE
                )
            """)

            # ── Performance Indexes ────────────────────────────────────────────
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scan_history_timestamp ON scan_history(timestamp DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scan_history_scan_type ON scan_history(scan_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scan_details_scan_id ON scan_details(scan_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scan_details_created_at ON scan_details(created_at DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scan_reasons_detail_id ON scan_reasons(scan_detail_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_technical_metrics_detail_id ON technical_metrics(scan_detail_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_recommendations_detail_id ON recommendations(scan_detail_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scan_metadata_detail_id ON scan_metadata(scan_detail_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_timestamp ON notifications(timestamp DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_request_log_created_at ON api_request_log(created_at DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")

            # Seed default Threat Feeds if empty
            cursor.execute("SELECT COUNT(*) FROM threat_feeds")
            if cursor.fetchone()[0] == 0:
                threats = [
                    # 1. Phishing Domains
                    ("domain", "paypal-security-update.com", "AlienVault OTX", 90),
                    ("domain", "microsoft-office365-login.net", "ThreatConnect", 95),
                    ("domain", "bank-verification-verify.info", "Spamhaus", 88),
                    # 2. Malicious IPs
                    ("ip", "198.51.100.42", "AbuseIPDB", 92),
                    ("ip", "203.0.113.195", "AlienVault OTX", 85),
                    ("ip", "192.0.2.78", "Emerging Threats", 90),
                    # 3. Scam Keywords
                    ("keyword", "lottery", "Local Intelligence", 80),
                    ("keyword", "winner", "Local Intelligence", 80),
                    ("keyword", "prize", "Local Intelligence", 80),
                    ("keyword", "claim", "Local Intelligence", 80),
                    ("keyword", "urgent", "Local Intelligence", 80),
                    # 4. Suspicious TLDs
                    ("tld", ".xyz", "Local Intelligence", 85),
                    ("tld", ".top", "Local Intelligence", 85),
                    ("tld", ".click", "Local Intelligence", 85),
                    ("tld", ".tk", "Local Intelligence", 85),
                    # 5. Crypto Scam Wallets
                    ("wallet", "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkjhxy", "CryptoScamDB", 98),
                    ("wallet", "0x71C7656EC7ab88b098defB751B7401B5f6d8976F", "CryptoScamDB", 98),
                    # 6. Shortened URL Providers
                    ("shortener", "bit.ly", "Local Intelligence", 75),
                    ("shortener", "tinyurl.com", "Local Intelligence", 75),
                    ("shortener", "t.co", "Local Intelligence", 70)
                ]
                for ft, val, src, conf in threats:
                    cursor.execute(
                        "INSERT INTO threat_feeds (feed_type, value, source, confidence_score) VALUES (?, ?, ?, ?)",
                        (ft, val, src, conf)
                    )

            # Seed default Feed Sync Status if empty
            cursor.execute("SELECT COUNT(*) FROM feed_sync_status")
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    "INSERT INTO feed_sync_status (feed_name, last_synced, status) VALUES (?, CURRENT_TIMESTAMP, ?)",
                    ("Optyx Threat Feed Tracker", "Success")
                )

            # Seed default Admin User if no Administrator exists or if it requires password migration
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Administrator'")
            has_admin = cursor.fetchone()[0] > 0
            
            cursor.execute("SELECT id, password_hash FROM users WHERE email = 'admin@sentrax.ai'")
            admin_row = cursor.fetchone()
            
            needs_update = False
            if admin_row:
                import bcrypt
                try:
                    if bcrypt.checkpw(b"admin", admin_row["password_hash"].encode("utf-8")):
                        needs_update = True
                except Exception:
                    pass

            if not has_admin or needs_update:
                import bcrypt
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(b"Admin@123", salt).decode("utf-8")
                if admin_row:
                    cursor.execute(
                        "UPDATE users SET password_hash = ?, role = 'Administrator' WHERE id = ?",
                        (hashed, admin_row["id"])
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO users (full_name, email, password_hash, role)
                        VALUES (?, ?, ?, ?)
                        """,
                        ("System Administrator", "admin@sentrax.ai", hashed, "Administrator")
                    )

            # Seed default Settings if not exists
            cursor.execute("SELECT COUNT(*) FROM settings")
            if cursor.fetchone()[0] == 0:
                import json
                default_settings = {
                    "risk_thresholds": json.dumps({"high": 70, "medium": 40}),
                    "alert_preferences": json.dumps({"email": False, "slack": False, "critical_only": True}),
                    "export_settings": json.dumps({"pdf_logo": True, "include_technical": True}),
                    "retention_period": "90"
                }
                for k, v in default_settings.items():
                    cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (k, v))

            conn.commit()
            
            # Clean up any HTML in alerts table
            migrate_existing_html_alerts()
            
    except Exception as e:
        print(f"Database error during schema initialization: {e}")


def migrate_existing_html_alerts() -> None:
    import re
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, description, title FROM alerts")
            rows = cursor.fetchall()
            updated_count = 0
            for r in rows:
                row_id = r["id"]
                desc = r["description"]
                title = r["title"]
                needs_update = False
                clean_desc = desc
                clean_title = title
                if desc and ("<" in str(desc) or ">" in str(desc)):
                    clean_desc = re.sub(r'<[^>]+>', '', str(desc))
                    clean_desc = " ".join(clean_desc.split())
                    needs_update = True
                if title and ("<" in str(title) or ">" in str(title)):
                    clean_title = re.sub(r'<[^>]+>', '', str(title))
                    clean_title = " ".join(clean_title.split())
                    needs_update = True
                if needs_update:
                    cursor.execute(
                        "UPDATE alerts SET description = ?, title = ? WHERE id = ?",
                        (clean_desc, clean_title, row_id)
                    )
                    updated_count += 1
            if updated_count > 0:
                conn.commit()
    except Exception as e:
        print(f"Error migrating HTML alert logs: {e}")


# ── Simple log helper (placeholder) ───────────────────────────────────────────

def log_request(endpoint: str, scan_type: str, result: str) -> None:
    """Insert a basic request record into the log table."""
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO api_request_log (endpoint, scan_type, result) VALUES (?, ?, ?)",
                (endpoint, scan_type, result),
            )
            conn.commit()
    except Exception as e:
        print(f"Database error in log_request: {e}")


# ── Persistent Scan History helper ───────────────────────────────────────────

def save_scan(
    scan_type: str,
    input_data: str,
    score: int,
    label: str,
    threat_level: str,
    confidence: int,
    reasons: Optional[list] = None,
    metrics: Optional[dict] = None,
    recommendations: Optional[list] = None,
    metadata: Optional[dict] = None,
    scanner_version: str = "v5.0"
) -> None:
    """
    Persist scan summaries and details by delegating to utils/database_writer.
    """
    try:
        from utils.database_writer import save_scan as writer_save_scan
        writer_save_scan(
            scan_type=scan_type,
            input_data=input_data,
            score=score,
            label=label,
            threat_level=threat_level,
            confidence=confidence,
            reasons=reasons,
            metrics=metrics,
            recommendations=recommendations,
            metadata=metadata,
            scanner_version=scanner_version
        )
    except Exception as e:
        print(f"Error delegating save_scan: {e}")




def create_notification(
    title: str,
    message: str,
    severity: str
) -> None:
    """
    Create a new real-time warning, info, or critical notification alert.
    """
    try:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO notifications (title, message, severity)
                VALUES (?, ?, ?)
                """,
                (title, message, severity),
            )
            conn.commit()
    except Exception as e:
        print(f"Database error in create_notification: {e}")


# ── Database Cleanup helper ───────────────────────────────────────────────────

def cleanup_old_history() -> None:
    """
    Delete historical scan records older than the retention period days config.
    Designed for execution as an asynchronous background task.
    """
    from datetime import datetime, timedelta
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = 'retention_period'")
            row = cursor.fetchone()
            days = int(row[0]) if row else 90
            
            cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("DELETE FROM scan_history WHERE timestamp < ?", (cutoff,))
            conn.commit()
            print(f"Database cleanup executed: cleared logs older than {cutoff}")

            # Invalidate statistics cache after purging old records
            try:
                from services.statistics_service import StatisticsService
                StatisticsService.clear_cache()
            except Exception:
                pass
    except Exception as e:
        print(f"Database error in cleanup_old_history: {e}")
