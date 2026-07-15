"""
SentraX AI Backend — services/threat_intelligence_service.py
Threat Intelligence service layer handling known malicious feeds (domains, IPs, wallets, TLDs) and schedule synchronization.
"""

from typing import Dict, Any, List
from database import get_connection
from datetime import datetime


class ThreatIntelligenceService:
    """
    Service class managing persistent SQLite storage of known threat lists
    and background updates scheduler status.
    """

    @staticmethod
    def get_all_feeds() -> List[Dict[str, Any]]:
        """Fetch all malicious feeds from SQLite."""
        feeds = []
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, feed_type, value, source, confidence_score, created_at FROM threat_feeds")
                for row in cursor.fetchall():
                    feeds.append(dict(row))
        except Exception as e:
            print(f"Error fetching feeds: {e}")
        return feeds

    @staticmethod
    def get_feeds_by_type(feed_type: str) -> List[Dict[str, Any]]:
        """Fetch malicious feeds filtered by type (e.g. domain, ip, wallet)."""
        feeds = []
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, feed_type, value, source, confidence_score, created_at FROM threat_feeds WHERE feed_type = ?",
                    (feed_type,)
                )
                for row in cursor.fetchall():
                    feeds.append(dict(row))
        except Exception as e:
            print(f"Error fetching feeds of type {feed_type}: {e}")
        return feeds

    @staticmethod
    def get_statistics() -> Dict[str, Any]:
        """Compute feed statistics counts."""
        stats = {
            "total_indicators": 0,
            "phishing_domains": 0,
            "malicious_ips": 0,
            "suspicious_tlds": 0,
            "scam_keywords": 0,
            "crypto_wallets": 0,
            "url_shorteners": 0,
            "last_synced_time": None
        }

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM threat_feeds")
                stats["total_indicators"] = cursor.fetchone()[0] or 0

                cursor.execute("SELECT feed_type, COUNT(*) FROM threat_feeds GROUP BY feed_type")
                for row in cursor.fetchall():
                    ftype = row[0]
                    cnt = row[1]
                    if ftype == "domain":
                        stats["phishing_domains"] = cnt
                    elif ftype == "ip":
                        stats["malicious_ips"] = cnt
                    elif ftype == "tld":
                        stats["suspicious_tlds"] = cnt
                    elif ftype == "keyword":
                        stats["scam_keywords"] = cnt
                    elif ftype == "wallet":
                        stats["crypto_wallets"] = cnt
                    elif ftype == "shortener":
                        stats["url_shorteners"] = cnt

                cursor.execute("SELECT last_synced FROM feed_sync_status ORDER BY last_synced DESC LIMIT 1")
                row_sync = cursor.fetchone()
                if row_sync:
                    stats["last_synced_time"] = row_sync[0]

        except Exception as e:
            print(f"Error calculating threat stats: {e}")

        return stats

    @staticmethod
    def sync_feeds(feed_name: str = "Optyx Threat Feed Tracker") -> Dict[str, Any]:
        """Simulate feed synchronization, updating last_synced timestamp."""
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO feed_sync_status (feed_name, last_synced, status)
                    VALUES (?, CURRENT_TIMESTAMP, ?)
                    """,
                    (feed_name, "Success")
                )
                conn.commit()
                return {"message": "Sync completed successfully", "feed": feed_name, "timestamp": datetime.now().isoformat()}
        except Exception as e:
            print(f"Error syncing feeds: {e}")
            return {"message": "Sync failed", "error": str(e)}
