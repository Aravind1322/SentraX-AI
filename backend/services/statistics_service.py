"""
SentraX AI Backend — services/statistics_service.py
Reusable service layer for computing scan history statistics, dashboard metrics,
and analytics datasets from SQLite persistent storage.
"""

from typing import Dict, Any, List
from database import get_connection
from datetime import datetime, timedelta


class StatisticsService:
    """
    Service class handling SQLite database aggregation queries
    for security dashboard metrics, search queries, and historical trends.
    """

    @staticmethod
    def get_dashboard_metrics() -> Dict[str, Any]:
        """
        Aggregate scan metrics for the main SOC dashboard.
        """
        metrics = {
            "total_scans": 0,
            "todays_scans": 0,
            "safe_scans": 0,
            "fraud_scans": 0,
            "critical_scans": 0,
            "average_score": 0.0,
            "average_confidence": 0.0,
            "most_common_scan_type": "N/A",
            "latest_scan_timestamp": None,
            "threat_percentage": 0.0
        }

        try:
            with get_connection() as conn:
                cursor = conn.cursor()

                # 1. Basic aggregates
                cursor.execute("""
                    SELECT 
                        COUNT(*), 
                        AVG(score), 
                        AVG(confidence),
                        MAX(timestamp)
                    FROM scan_history
                """)
                row = cursor.fetchone()
                if row and row[0] > 0:
                    metrics["total_scans"] = row[0]
                    metrics["average_score"] = round(row[1] or 0.0, 2)
                    metrics["average_confidence"] = round(row[2] or 0.0, 2)
                    metrics["latest_scan_timestamp"] = row[3]

                # 2. Today's scans
                today_str = datetime.now().strftime('%Y-%m-%d')
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM scan_history 
                    WHERE date(timestamp) = ?
                """, (today_str,))
                metrics["todays_scans"] = cursor.fetchone()[0]

                # 3. Threat level counts
                # Safe scans (threat_level = LOW)
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM scan_history 
                    WHERE threat_level = 'LOW'
                """)
                metrics["safe_scans"] = cursor.fetchone()[0]

                # Critical scans (threat_level = HIGH)
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM scan_history 
                    WHERE threat_level = 'HIGH'
                """)
                metrics["critical_scans"] = cursor.fetchone()[0]

                # Fraud scans (scan_type = 'Fraud' or label like 'Fraud' or label like 'Scam' or risk_level = 'SUSPICIOUS')
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM scan_history 
                    WHERE threat_level IN ('HIGH', 'MEDIUM')
                """)
                metrics["fraud_scans"] = cursor.fetchone()[0]

                # 4. Most common scan type
                cursor.execute("""
                    SELECT scan_type, COUNT(*) as cnt 
                    FROM scan_history 
                    GROUP BY scan_type 
                    ORDER BY cnt DESC 
                    LIMIT 1
                """)
                row_type = cursor.fetchone()
                if row_type:
                    metrics["most_common_scan_type"] = row_type[0]

                # 5. Threat percentage
                if metrics["total_scans"] > 0:
                    threat_scans = metrics["total_scans"] - metrics["safe_scans"]
                    metrics["threat_percentage"] = round((threat_scans / metrics["total_scans"]) * 100, 2)

        except Exception as e:
            print(f"Error computing dashboard metrics: {e}")

        return metrics

    @staticmethod
    def get_analytics_datasets() -> Dict[str, Any]:
        """
        Aggregate analytics datasets for graphing components.
        """
        datasets = {
            "threat_distribution": [],
            "daily_scan_counts": [],
            "scanner_usage": [],
            "average_risk_trend": [],
            "threat_level_distribution": []
        }

        try:
            with get_connection() as conn:
                cursor = conn.cursor()

                # 1. Threat / Threat Level distribution
                cursor.execute("""
                    SELECT threat_level, COUNT(*) 
                    FROM scan_history 
                    GROUP BY threat_level
                """)
                for row in cursor.fetchall():
                    item = {"threat_level": row[0], "count": row[1]}
                    datasets["threat_distribution"].append(item)
                    datasets["threat_level_distribution"].append(item)

                # 2. Scanner usage
                cursor.execute("""
                    SELECT scan_type, COUNT(*) 
                    FROM scan_history 
                    GROUP BY scan_type
                """)
                for row in cursor.fetchall():
                    datasets["scanner_usage"].append({
                        "scanner": row[0],
                        "count": row[1]
                    })

                # 3. Daily scan counts (last 14 days)
                days_limit = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
                cursor.execute("""
                    SELECT 
                        date(timestamp) as day, 
                        COUNT(*),
                        SUM(CASE WHEN threat_level != 'LOW' THEN 1 ELSE 0 END)
                    FROM scan_history 
                    WHERE date(timestamp) >= ?
                    GROUP BY day
                    ORDER BY day ASC
                """, (days_limit,))
                for row in cursor.fetchall():
                    datasets["daily_scan_counts"].append({
                        "date": row[0],
                        "total_scans": row[1],
                        "threat_scans": row[2]
                    })

                # 4. Average risk trend (last 14 days)
                cursor.execute("""
                    SELECT 
                        date(timestamp) as day, 
                        AVG(score)
                    FROM scan_history 
                    WHERE date(timestamp) >= ?
                    GROUP BY day
                    ORDER BY day ASC
                """, (days_limit,))
                for row in cursor.fetchall():
                    datasets["average_risk_trend"].append({
                        "date": row[0],
                        "average_score": round(row[1] or 0.0, 2)
                    })

        except Exception as e:
            print(f"Error computing analytics datasets: {e}")

        return datasets

    @staticmethod
    def get_detailed_statistics() -> Dict[str, Any]:
        """
        Calculates reusable comprehensive SOC stats for Statistics Service:
        Average, highest, lowest risk, most frequent threats, daily/weekly/monthly totals.
        """
        stats = {
            "average_risk": 0.0,
            "highest_risk": 0,
            "lowest_risk": 0,
            "most_frequent_threats": [],
            "daily_totals": 0,
            "weekly_totals": 0,
            "monthly_totals": 0
        }

        try:
            with get_connection() as conn:
                cursor = conn.cursor()

                # Basic score queries
                cursor.execute("SELECT AVG(score), MAX(score), MIN(score) FROM scan_history")
                row = cursor.fetchone()
                if row:
                    stats["average_risk"] = round(row[0] or 0.0, 2)
                    stats["highest_risk"] = row[1] or 0
                    stats["lowest_risk"] = row[2] or 0

                # Most frequent threats (by label description)
                cursor.execute("""
                    SELECT label, COUNT(*) as cnt 
                    FROM scan_history 
                    WHERE threat_level != 'LOW'
                    GROUP BY label 
                    ORDER BY cnt DESC 
                    LIMIT 5
                """)
                for row in cursor.fetchall():
                    stats["most_frequent_threats"].append({
                        "threat": row[0],
                        "count": row[1]
                    })

                # Daily, Weekly, Monthly totals
                now = datetime.now()
                day_str = now.strftime('%Y-%m-%d')
                week_str = (now - timedelta(days=7)).strftime('%Y-%m-%d')
                month_str = (now - timedelta(days=30)).strftime('%Y-%m-%d')

                cursor.execute("SELECT COUNT(*) FROM scan_history WHERE date(timestamp) = ?", (day_str,))
                stats["daily_totals"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM scan_history WHERE date(timestamp) >= ?", (week_str,))
                stats["weekly_totals"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM scan_history WHERE date(timestamp) >= ?", (month_str,))
                stats["monthly_totals"] = cursor.fetchone()[0]

        except Exception as e:
            print(f"Error computing detailed statistics: {e}")

        return stats
