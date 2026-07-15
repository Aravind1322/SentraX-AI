"""
SentraX AI Backend — routes/analytics_routes.py
Endpoints for fetching SOC dashboard aggregated stats and time-series charting datasets.
"""

from fastapi import APIRouter, Depends
from services.statistics_service import StatisticsService
from utils.security import get_current_user, RoleChecker
from typing import Dict, Any

router = APIRouter()


@router.get("/dashboard", summary="Get aggregated dashboard stats for the SOC controller")
async def get_dashboard_data(
    current_user: Dict[str, Any] = Depends(RoleChecker(["Viewer", "Security Analyst", "Administrator"]))
):
    """
    Returns high-level metric summaries for today's scans, total scans,
    threat levels, averages, and system threat percentages.
    """
    return StatisticsService.get_dashboard_metrics()


@router.get("/analytics", summary="Get datasets formatted for charts and reporting dashboards")
async def get_analytics_data(
    current_user: Dict[str, Any] = Depends(RoleChecker(["Viewer", "Security Analyst", "Administrator"]))
):
    """
    Returns multiple aggregated datasets, including daily scan trends,
    threat distribution by level, and scanner usage distribution.
    """
    return StatisticsService.get_analytics_datasets()


@router.get("/statistics", summary="Get comprehensive reusable security stats")
async def get_detailed_stats(
    current_user: Dict[str, Any] = Depends(RoleChecker(["Security Analyst", "Administrator"]))
):
    """
    Returns detailed aggregation metrics: Average/Highest/Lowest risk,
    top frequent threats, and time-range scan counts (daily, weekly, monthly totals).
    """
    return StatisticsService.get_detailed_statistics()
