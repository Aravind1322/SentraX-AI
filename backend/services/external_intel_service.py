"""
SentraX AI Backend — services/external_intel_service.py
Service layer for concurrent lookups against VirusTotal, AbuseIPDB, PhishTank, and URLHaus.
"""

import os
import httpx
import asyncio
from typing import Dict, Any, Optional
import urllib.parse
import base64


class ExternalIntelService:
    """
    Orchestrates real-time threat intelligence queries to third-party vendors.
    """
    VIRUSTOTAL_API_KEY = os.environ.get("VIRUSTOTAL_API_KEY")
    ABUSEIPDB_API_KEY = os.environ.get("ABUSEIPDB_API_KEY")
    PHISHTANK_API_KEY = os.environ.get("PHISHTANK_API_KEY")
    URLHAUS_API_KEY = os.environ.get("URLHAUS_API_KEY")

    @classmethod
    async def lookup_virustotal(cls, client: httpx.AsyncClient, target: str) -> Optional[Dict[str, Any]]:
        """Query VirusTotal API v3 for URL analysis records."""
        if not cls.VIRUSTOTAL_API_KEY:
            return None
        try:
            # VT URL ID is base64 representation of URL without padding
            url_id = base64.urlsafe_b64encode(target.encode()).decode().strip("=")
            url = f"https://www.virustotal.com/api/v3/urls/{url_id}"
            headers = {"x-apikey": cls.VIRUSTOTAL_API_KEY}
            resp = await client.get(url, headers=headers, timeout=2.0)
            if resp.status_code == 200:
                data = resp.json().get("data", {})
                attr = data.get("attributes", {})
                last_analysis = attr.get("last_analysis_stats", {})
                return {
                    "malicious": last_analysis.get("malicious", 0),
                    "suspicious": last_analysis.get("suspicious", 0),
                    "harmless": last_analysis.get("harmless", 0),
                    "undetected": last_analysis.get("undetected", 0),
                    "verdict": "malicious" if last_analysis.get("malicious", 0) > 0 else "clean"
                }
        except Exception:
            pass
        return None

    @classmethod
    async def lookup_abuseipdb(cls, client: httpx.AsyncClient, target: str) -> Optional[Dict[str, Any]]:
        """Query AbuseIPDB API v2 for IP reputation ratings."""
        if not cls.ABUSEIPDB_API_KEY:
            return None
        ip = target
        if "://" in target:
            try:
                parsed = urllib.parse.urlparse(target)
                ip = parsed.netloc.split(":")[0]
            except Exception:
                pass
        
        try:
            url = f"https://api.abuseipdb.com/api/v2/check?ipAddress={ip}"
            headers = {
                "Key": cls.ABUSEIPDB_API_KEY,
                "Accept": "application/json"
            }
            resp = await client.get(url, headers=headers, timeout=2.0)
            if resp.status_code == 200:
                data = resp.json().get("data", {})
                return {
                    "abuse_confidence_score": data.get("abuseConfidenceScore", 0),
                    "total_reports": data.get("totalReports", 0),
                    "is_whitelisted": data.get("isWhitelisted", False),
                    "verdict": "malicious" if data.get("abuseConfidenceScore", 0) > 10 else "clean"
                }
        except Exception:
            pass
        return None

    @classmethod
    async def lookup_phishtank(cls, client: httpx.AsyncClient, target: str) -> Optional[Dict[str, Any]]:
        """Query PhishTank database check API."""
        if not target.startswith("http"):
            return None
        try:
            url = "https://check.phishtank.com/check"
            data = {"url": target, "format": "json"}
            if cls.PHISHTANK_API_KEY:
                data["app_key"] = cls.PHISHTANK_API_KEY
            headers = {"User-Agent": "phishtank/sentrax-ai"}
            resp = await client.post(url, data=data, headers=headers, timeout=2.0)
            if resp.status_code == 200:
                res_json = resp.json()
                res_data = res_json.get("results", {})
                return {
                    "in_database": res_data.get("in_database", False),
                    "phish": res_data.get("valid", False),
                    "verified": res_data.get("verified", False),
                    "verdict": "malicious" if res_data.get("valid", False) else "clean"
                }
        except Exception:
            pass
        return None

    @classmethod
    async def lookup_urlhaus(cls, client: httpx.AsyncClient, target: str) -> Optional[Dict[str, Any]]:
        """Query Abuse.ch URLHaus endpoint check API."""
        if not cls.URLHAUS_API_KEY or not target.startswith("http"):
            return None
        try:
            url = "https://urlhaus-api.abuse.ch/v1/url/"
            data = {"url": target}
            headers = {"User-Agent": "urlhaus/sentrax-ai"}
            resp = await client.post(url, data=data, headers=headers, timeout=2.0)
            if resp.status_code == 200:
                res_data = resp.json()
                status = res_data.get("query_status")
                return {
                    "query_status": status,
                    "url_status": res_data.get("url_status"),
                    "threat": res_data.get("threat"),
                    "verdict": "malicious" if status == "malicious" else "clean"
                }
        except Exception:
            pass
        return None

    @classmethod
    async def run_lookup(cls, target: str) -> Dict[str, Any]:
        """
        Run lookups across all configured providers concurrently with timeout handling.
        """
        results = {}
        async with httpx.AsyncClient() as client:
            tasks = {
                "virustotal": cls.lookup_virustotal(client, target),
                "abuseipdb": cls.lookup_abuseipdb(client, target),
                "phishtank": cls.lookup_phishtank(client, target),
                "urlhaus": cls.lookup_urlhaus(client, target),
            }
            keys = list(tasks.keys())
            resolved = await asyncio.gather(*tasks.values(), return_exceptions=True)
            for k, val in zip(keys, resolved):
                if val and not isinstance(val, Exception):
                    results[k] = val
        return results
