"""
SentraX AI Backend — routes/history.py
Endpoints for history listing, filtering, pagination, and keyword search.
"""

from fastapi import APIRouter, Query, Depends
from database import get_connection
from typing import Dict, Any, List, Optional
from utils.security import get_current_user, RoleChecker

router = APIRouter()


@router.get("", summary="Get paginated and filtered scan history")
async def get_history(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    scan_type: Optional[str] = Query(None, description="Filter by scan type (e.g., URL, SMS, Fraud, Employee)"),
    threat_level: Optional[str] = Query(None, description="Filter by threat level (e.g., LOW, MEDIUM, HIGH)"),
    current_user: Dict[str, Any] = Depends(RoleChecker(["Viewer", "Security Analyst", "Administrator"]))
):
    """
    Retrieve paginated scan records, optionally filtered by scan type or threat level.
    Results are returned newest first.
    """
    offset = (page - 1) * page_size
    query_parts = []
    params = []

    if scan_type:
        query_parts.append("scan_type = ?")
        params.append(scan_type)
    if threat_level:
        query_parts.append("threat_level = ?")
        params.append(threat_level)

    where_clause = " WHERE " + " AND ".join(query_parts) if query_parts else ""

    total_scans = 0
    scans = []

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Get total count
            count_query = f"SELECT COUNT(*) FROM scan_history{where_clause}"
            cursor.execute(count_query, params)
            total_scans = cursor.fetchone()[0]

            # Get paginated data sorted newest first
            data_query = f"""
                SELECT id, scan_type, input_data, score, label, threat_level, confidence, timestamp
                FROM scan_history
                {where_clause}
                ORDER BY timestamp DESC, id DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(data_query, params + [page_size, offset])
            
            for row in cursor.fetchall():
                scans.append({
                    "id": row["id"],
                    "scan_type": row["scan_type"],
                    "input_data": row["input_data"],
                    "score": row["score"],
                    "label": row["label"],
                    "threat_level": row["threat_level"],
                    "confidence": row["confidence"],
                    "timestamp": row["timestamp"],
                })

    except Exception as e:
        print(f"Error querying scan history: {e}")

    return {
        "total_scans": total_scans,
        "page": page,
        "page_size": page_size,
        "scans": scans
    }


@router.get("/search", summary="Search scan history with complex filters")
async def search_history(
    keyword: Optional[str] = Query(None, description="Search keyword in input data"),
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    scan_type: Optional[str] = Query(None, description="Filter by scan type"),
    threat_level: Optional[str] = Query(None, description="Filter by threat level"),
    min_score: Optional[int] = Query(None, description="Minimum risk score"),
    max_score: Optional[int] = Query(None, description="Maximum risk score"),
    label: Optional[str] = Query(None, description="Filter by threat label"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(RoleChecker(["Viewer", "Security Analyst", "Administrator"]))
):
    """
    Search historical scan records using flexible keywords, date matching,
    threat levels, risk score ranges, and labels.
    """
    # Clean up Query parameter objects for programmatic direct calling
    keyword = keyword if isinstance(keyword, str) else None
    date = date if isinstance(date, str) else None
    scan_type = scan_type if isinstance(scan_type, str) else None
    threat_level = threat_level if isinstance(threat_level, str) else None
    min_score = min_score if isinstance(min_score, int) else None
    max_score = max_score if isinstance(max_score, int) else None
    label = label if isinstance(label, str) else None
    page = page if isinstance(page, int) else 1
    page_size = page_size if isinstance(page_size, int) else 20

    query_parts = []
    params = []

    if keyword:
        query_parts.append("input_data LIKE ?")
        params.append(f"%{keyword}%")
    if date:
        query_parts.append("date(timestamp) = ?")
        params.append(date)
    if scan_type:
        query_parts.append("scan_type = ?")
        params.append(scan_type)
    if threat_level:
        query_parts.append("threat_level = ?")
        params.append(threat_level)
    if min_score is not None:
        query_parts.append("score >= ?")
        params.append(min_score)
    if max_score is not None:
        query_parts.append("score <= ?")
        params.append(max_score)
    if label:
        query_parts.append("label = ?")
        params.append(label)

    where_clause = " WHERE " + " AND ".join(query_parts) if query_parts else ""
    offset = (page - 1) * page_size
    total_scans = 0
    scans = []

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Get total count
            count_query = f"SELECT COUNT(*) FROM scan_history{where_clause}"
            cursor.execute(count_query, params)
            total_scans = cursor.fetchone()[0]

            # Get paginated data sorted newest first
            data_query = f"""
                SELECT id, scan_type, input_data, score, label, threat_level, confidence, timestamp
                FROM scan_history
                {where_clause}
                ORDER BY timestamp DESC, id DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(data_query, params + [page_size, offset])
            
            for row in cursor.fetchall():
                scans.append({
                    "id": row["id"],
                    "scan_type": row["scan_type"],
                    "input_data": row["input_data"],
                    "score": row["score"],
                    "label": row["label"],
                    "threat_level": row["threat_level"],
                    "confidence": row["confidence"],
                    "timestamp": row["timestamp"],
                })

    except Exception as e:
        print(f"Error searching history: {e}")

    return {
        "total_scans": total_scans,
        "page": page,
        "page_size": page_size,
        "scans": scans
    }


@router.get("/statistics", summary="Get comprehensive history metrics and common issues")
async def get_history_statistics(
    current_user: Dict[str, Any] = Depends(RoleChecker(["Viewer", "Security Analyst", "Administrator"]))
):
    """
    Returns aggregated history counts, threat tiers breakdown,
    averages, and common security issues/reasons.
    """
    stats = {
        "total_scans": 0,
        "safe": 0,
        "medium": 0,
        "high": 0,
        "critical": 0,
        "average_score": 0.0,
        "average_confidence": 0.0,
        "most_common_reasons": [],
        "most_common_technical_issues": []
    }

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Total scans
            cursor.execute("SELECT COUNT(*) FROM scan_history")
            stats["total_scans"] = cursor.fetchone()[0] or 0

            if stats["total_scans"] > 0:
                # Threat level breakdowns
                cursor.execute("SELECT threat_level, COUNT(*) FROM scan_history GROUP BY threat_level")
                for row in cursor.fetchall():
                    lvl = row[0].upper()
                    cnt = row[1]
                    if lvl == "LOW" or lvl == "SAFE":
                        stats["safe"] += cnt
                    elif lvl == "MEDIUM" or lvl == "MODERATE" or lvl == "SUSPICIOUS":
                        stats["medium"] += cnt
                    elif lvl == "HIGH":
                        stats["high"] += cnt
                    elif lvl == "CRITICAL":
                        stats["critical"] += cnt

                # Include scans >= 90 score as Critical
                cursor.execute("SELECT COUNT(*) FROM scan_history WHERE score >= 90")
                stats["critical"] = cursor.fetchone()[0] or 0

                # Averages
                cursor.execute("SELECT AVG(score), AVG(confidence) FROM scan_history")
                avg_row = cursor.fetchone()
                if avg_row:
                    stats["average_score"] = round(avg_row[0] or 0.0, 2)
                    stats["average_confidence"] = round(avg_row[1] or 0.0, 2)

                # Most common reasons
                cursor.execute("SELECT reason, COUNT(*) as cnt FROM scan_reasons GROUP BY reason ORDER BY cnt DESC LIMIT 5")
                stats["most_common_reasons"] = [{"reason": r[0], "count": r[1]} for r in cursor.fetchall()]

                # Most common technical issues
                cursor.execute("SELECT metric_name, metric_value, COUNT(*) as cnt FROM technical_metrics GROUP BY metric_name, metric_value ORDER BY cnt DESC LIMIT 5")
                stats["most_common_technical_issues"] = [{"metric": r[0], "value": r[1], "count": r[2]} for r in cursor.fetchall()]

    except Exception as e:
        print(f"Error compiling history statistics: {e}")

    return stats


@router.get("/timeline", summary="Get timeline of latest security events")
async def get_history_timeline(
    current_user: Dict[str, Any] = Depends(RoleChecker(["Viewer", "Security Analyst", "Administrator"]))
):
    """
    Returns latest scans, alerts, and active case investigations.
    """
    timeline = {
        "latest_scans": [],
        "latest_alerts": [],
        "latest_investigations": []
    }

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Latest 10 scans
            cursor.execute("SELECT id, scan_type, input_data, score, label, threat_level, timestamp FROM scan_history ORDER BY timestamp DESC LIMIT 10")
            timeline["latest_scans"] = [dict(r) for r in cursor.fetchall()]

            # Latest 10 alerts
            cursor.execute("SELECT id, title, severity, status, timestamp FROM alerts ORDER BY timestamp DESC LIMIT 10")
            timeline["latest_alerts"] = [dict(r) for r in cursor.fetchall()]

            # Latest 10 case investigations
            cursor.execute("SELECT id, title, priority, status, updated_at FROM soc_cases ORDER BY updated_at DESC LIMIT 10")
            timeline["latest_investigations"] = [dict(r) for r in cursor.fetchall()]

    except Exception as e:
        print(f"Error fetching history timeline: {e}")

    return timeline


@router.get("/{scan_id}", summary="Get normalized enterprise history by scan ID")
async def get_normalized_history(
    scan_id: int,
    current_user: Dict[str, Any] = Depends(RoleChecker(["Viewer", "Security Analyst", "Administrator"]))
):
    """
    Retrieve paginated scan summary, details, reasons list, technical metrics,
    recommendations, and execution metadata.
    """
    from fastapi import HTTPException
    
    summary = None
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scan_history WHERE id = ?", (scan_id,))
            row = cursor.fetchone()
            if row:
                summary = dict(row)
    except Exception as e:
        print(f"Error reading scan_history: {e}")
    
    if not summary:
        raise HTTPException(status_code=404, detail="Scan record not found")
    
    details = {}
    reasons = []
    technical = {}
    recommendations = []
    metadata = {}
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scan_details WHERE scan_id = ?", (scan_id,))
            det_row = cursor.fetchone()
            if det_row:
                details = dict(det_row)
                detail_id = details["id"]
                
                # Reasons
                cursor.execute("SELECT reason FROM scan_reasons WHERE scan_detail_id = ?", (detail_id,))
                reasons = [r[0] for r in cursor.fetchall()]
                
                # Technical Metrics
                cursor.execute("SELECT metric_name, metric_value FROM technical_metrics WHERE scan_detail_id = ?", (detail_id,))
                for name, val in cursor.fetchall():
                    technical[name] = val
                    
                # Recommendations
                cursor.execute("SELECT recommendation FROM recommendations WHERE scan_detail_id = ?", (detail_id,))
                recommendations = [r[0] for r in cursor.fetchall()]
                
                # Metadata
                cursor.execute("SELECT execution_time_ms, backend_version, api_version, engine_name, engine_version FROM scan_metadata WHERE scan_detail_id = ?", (detail_id,))
                meta_row = cursor.fetchone()
                if meta_row:
                    metadata = dict(meta_row)
            else:
                # Return fallback mock/default details so the API is fully compatible for older rows
                details = {
                    "id": -1,
                    "scan_id": scan_id,
                    "scan_type": summary["scan_type"],
                    "target": summary["input_data"],
                    "score": summary["score"],
                    "label": summary["label"],
                    "confidence": summary["confidence"],
                    "threat_level": summary["threat_level"],
                    "scanner_version": "v5.0",
                    "created_at": summary["timestamp"]
                }
                metadata = {
                    "execution_time_ms": 10,
                    "backend_version": "v1.0.0",
                    "api_version": "v1",
                    "engine_name": "SentraX AI Engine",
                    "engine_version": "v1.0"
                }
    except Exception as e:
        print(f"Error fetching normalized data: {e}")
        
    return {
        "summary": summary,
        "details": details,
        "reasons": reasons,
        "technical": technical,
        "recommendations": recommendations,
        "metadata": metadata
    }
