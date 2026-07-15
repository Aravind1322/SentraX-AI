"""
SentraX AI — utils/websocket_client.py

Thread-safe WebSocket listeners for Streamlit to consume real-time events
without injecting JavaScript or HTML.

Three singleton listeners (one per channel):
  AlertListener    → /ws/alerts    — security alert toasts
  DashboardListener → /ws/dashboard — live KPI metrics
  ScanFeedListener  → /ws/scans    — live recent-scan rows

All listeners:
  - Auto-connect on first start()
  - Auto-reconnect (3 s back-off) when backend is offline
  - Expose connected property for sidebar status indicator
  - Never raise inside Streamlit — they run in daemon threads
"""

import threading
import json
import time
from typing import Any, Dict, List, Optional

_WS_BASE = "ws://127.0.0.1:8000"


# ── Base listener class ────────────────────────────────────────────────────────

class _BaseListener:
    _lock = threading.Lock()
    _instance = None          # overridden per subclass via __new__

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                obj = super().__new__(cls)
                obj._thread: Optional[threading.Thread] = None
                obj._running = False
                obj._connected = False
                obj._queue: List[Dict[str, Any]] = []
                obj._data_lock = threading.Lock()
                obj._ctx = None
                cls._instance = obj
        return cls._instance

    # ── subclass must set this ─────────────────────────────────────────────────
    @property
    def _ws_url(self) -> str:
        raise NotImplementedError

    @property
    def connected(self) -> bool:
        return self._connected

    # ── public API ─────────────────────────────────────────────────────────────

    def start(self):
        """Start background listener thread if not already alive."""
        if self._thread and self._thread.is_alive():
            return
        
        # Capture current Streamlit run context to support background thread UI reruns
        try:
            from streamlit.runtime.scriptrunner import get_script_run_ctx
            self._ctx = get_script_run_ctx()
        except Exception:
            self._ctx = None

        self._running = True
        self._thread = threading.Thread(
            target=self._listen_loop, daemon=True
        )
        
        if self._ctx:
            try:
                from streamlit.runtime.scriptrunner import add_script_run_ctx
                add_script_run_ctx(self._thread)
            except Exception:
                pass
                
        self._thread.start()

    def stop(self):
        self._running = False
        self._connected = False

    def get_events(self) -> List[Dict[str, Any]]:
        """Drain and return accumulated events."""
        with self._data_lock:
            events = list(self._queue)
            self._queue.clear()
        return events

    # ── internal ───────────────────────────────────────────────────────────────

    def _trigger_rerun(self):
        """Trigger session script run rerun to dynamically refresh the view."""
        if self._ctx:
            try:
                from streamlit.runtime import get_instance
                runtime = get_instance()
                if runtime:
                    session_info = runtime._session_mgr.get_active_session_info(self._ctx.session_id)
                    if session_info:
                        session_info.session.request_rerun(None)
            except Exception:
                pass

    def _listen_loop(self):
        from websockets.sync.client import connect as ws_connect
        while self._running:
            try:
                with ws_connect(self._ws_url, open_timeout=4) as ws:
                    was_connected = self._connected
                    self._connected = True
                    
                    # Refresh connection status to LIVE on the UI immediately
                    if not was_connected:
                        self._trigger_rerun()
                        
                    while self._running:
                        raw = ws.recv(timeout=30)          # 30 s recv timeout
                        try:
                            data = json.loads(raw)
                            self._handle(data)
                        except json.JSONDecodeError:
                            pass
            except Exception:
                was_connected = self._connected
                self._connected = False
                
                # Refresh connection status to RECONNECTING on the UI immediately
                if was_connected:
                    self._trigger_rerun()
                    
                if self._running:
                    time.sleep(3)                          # back-off before reconnect
        self._connected = False

    def _handle(self, data: Dict[str, Any]):
        """Subclasses override to filter / transform incoming messages."""
        with self._data_lock:
            self._queue.append(data)
        self._trigger_rerun()


# ── Channel-specific listeners ─────────────────────────────────────────────────

class AlertListener(_BaseListener):
    """Subscribes to /ws/alerts — emits new_alert events."""
    _instance = None

    @property
    def _ws_url(self):
        return f"{_WS_BASE}/ws/alerts"

    def _handle(self, data):
        if data.get("event") == "new_alert":
            super()._handle(data)

    # Backward-compat alias used in existing app.py
    def get_new_alerts(self) -> List[Dict[str, Any]]:
        return self.get_events()


class DashboardListener(_BaseListener):
    """
    Subscribes to /ws/dashboard — holds the latest dashboard_update payload.
    Streamlit reads .latest_stats instead of draining a queue.
    """
    _instance = None

    @property
    def _ws_url(self):
        return f"{_WS_BASE}/ws/dashboard"

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        if not hasattr(obj, "_latest"):
            obj._latest: Optional[Dict[str, Any]] = None
        return obj

    def _handle(self, data):
        if data.get("event") == "dashboard_update":
            with self._data_lock:
                self._latest = data
            super()._handle(data)

    @property
    def latest_stats(self) -> Optional[Dict[str, Any]]:
        with self._data_lock:
            return self._latest


class ScanFeedListener(_BaseListener):
    """Subscribes to /ws/scans — emits new_scan events for the recent-scan feed."""
    _instance = None

    @property
    def _ws_url(self):
        return f"{_WS_BASE}/ws/scans"

    def _handle(self, data):
        if data.get("event") == "new_scan":
            super()._handle(data)

    def get_new_scans(self) -> List[Dict[str, Any]]:
        return self.get_events()
