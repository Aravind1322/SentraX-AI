"""
SentraX AI Backend — routes/threats.py
Endpoints for querying known phishing domains, malicious IPs, and feed synchronization parameters.
"""

from fastapi import APIRouter, Depends
from services.threat_intelligence_service import ThreatIntelligenceService
from utils.security import get_current_user, RoleChecker
from typing import Dict, Any

router = APIRouter()


@router.get("", summary="Get all threat intelligence indicators")
async def get_threats(
    current_user: Dict[str, Any] = Depends(RoleChecker(["Viewer", "Security Analyst", "Administrator"]))
):
    """Retrieve the full feed of threat intelligence indicators."""
    return ThreatIntelligenceService.get_all_feeds()


@router.get("/domains", summary="Get phishing domains feed")
async def get_threat_domains(
    current_user: Dict[str, Any] = Depends(RoleChecker(["Viewer", "Security Analyst", "Administrator"]))
):
    """Retrieve known phishing domain indicators."""
    return ThreatIntelligenceService.get_feeds_by_type("domain")


@router.get("/ip", summary="Get malicious IP addresses feed")
async def get_threat_ips(
    current_user: Dict[str, Any] = Depends(RoleChecker(["Viewer", "Security Analyst", "Administrator"]))
):
    """Retrieve known malicious IP indicators."""
    return ThreatIntelligenceService.get_feeds_by_type("ip")


@router.get("/statistics", summary="Get threat feed statistics")
async def get_threat_stats(
    current_user: Dict[str, Any] = Depends(RoleChecker(["Viewer", "Security Analyst", "Administrator"]))
):
    """Retrieve aggregated counts for domain, IP, and wallet feeds."""
    return ThreatIntelligenceService.get_statistics()


@router.post("/sync", summary="Trigger threat feeds refresh (Scheduler sync)")
async def sync_threat_feeds(
    current_user: Dict[str, Any] = Depends(RoleChecker(["Security Analyst", "Administrator"]))
):
    """Simulates executing the background threat feeds sync scheduler."""
    return ThreatIntelligenceService.sync_feeds()
