"""
SentraX AI Backend — main.py
Entry point for the FastAPI application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from config import APP_NAME, APP_VERSION, APP_DESCRIPTION
from database import init_db, log_request
from routes import (
    url, sms, fraud, employee, quick_scan,
    history, analytics_routes, export, monitoring,
    auth, settings_routes, admin,
    threats, ioc, alerts, cases, reports
)
from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from collections import defaultdict
import time

# Rate limit configs
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_REQUESTS = 100
request_counts = defaultdict(list)

# ── Application ────────────────────────────────────────────────────────────────
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


def custom_openapi():
    """Override the OpenAPI schema to inject global HTTPBearer security
    so Swagger UI's Authorize button applies the token to every protected endpoint."""
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=APP_NAME,
        version=APP_VERSION,
        description=APP_DESCRIPTION,
        routes=app.routes,
    )
    # Declare the Bearer token security scheme
    schema.setdefault("components", {})
    schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Paste your JWT access token (without the 'Bearer ' prefix).",
        }
    }
    # Apply the scheme globally so Swagger sends it on every request
    schema["security"] = [{"HTTPBearer": []}]
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi

@app.on_event("startup")
def on_startup():
    """Initialise database schema migrations on service startup."""
    init_db()

# ── Custom Security, Rate Limit, and Request Logging Middleware ────────────────
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    # 1. IP-based Rate Limiter (100 requests per 60 seconds per IP)
    client_ip = request.client.host if request.client else "127.0.0.1"
    now = time.time()
    request_counts[client_ip] = [t for t in request_counts[client_ip] if now - t < RATE_LIMIT_WINDOW_SECONDS]
    
    if len(request_counts[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
        return Response(
            content="Rate limit exceeded. Capped at 100 requests/min.",
            status_code=429
        )
    request_counts[client_ip].append(now)

    # Proceed with request
    response = await call_next(request)

    # 2. Inject Security Headers
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    # 3. Log API requests to database (non-blocking background task)
    try:
        if "/api/" in request.url.path:
            from starlette.background import BackgroundTask
            response.background = BackgroundTask(
                log_request,
                endpoint=request.url.path,
                scan_type=request.method,
                result=f"Status: {response.status_code}"
            )
    except Exception as e:
        print(f"Failed logging request: {e}")

    return response

# ── CORS (open for dev; tighten in production) ─────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(url.router,              prefix="/api/url",        tags=["URL Intelligence"])
app.include_router(sms.router,              prefix="/api/sms",        tags=["SMS Shield"])
app.include_router(fraud.router,            prefix="/api/fraud",      tags=["Fraud Detection"])
app.include_router(employee.router,         prefix="/api/employee",   tags=["Employee Monitoring"])
app.include_router(quick_scan.router,       prefix="/api/quick-scan", tags=["Quick Scan"])
app.include_router(history.router,          prefix="/api/history",    tags=["SOC History"])
app.include_router(analytics_routes.router, prefix="/api/analytics",  tags=["SOC Analytics"])
app.include_router(export.router,           prefix="/api/export",     tags=["SOC Data Export"])
app.include_router(monitoring.router,       prefix="/api",            tags=["SOC Health & Monitoring"])
app.include_router(auth.router,             prefix="/api/auth",       tags=["SOC Authentication"])
app.include_router(settings_routes.router,  prefix="/api",            tags=["SOC Settings & Notifications"])
app.include_router(admin.router,            prefix="/api/admin",      tags=["SOC Admin Statistics"])
app.include_router(threats.router,          prefix="/api/threats",    tags=["Threat Intelligence"])
app.include_router(ioc.router,              prefix="/api/ioc",        tags=["IOC Tracker"])
app.include_router(alerts.router,           prefix="/api/alerts",     tags=["Realtime Alerts"])
app.include_router(cases.router,            prefix="/api/cases",      tags=["Case Management"])
app.include_router(reports.router,          prefix="/api/reports",    tags=["Enterprise Reporting"])



# ── Root endpoints ─────────────────────────────────────────────────────────────
@app.get("/", tags=["Root"])
async def root():
    """SentraX AI Backend — root endpoint."""
    return {
        "platform": APP_NAME,
        "version": APP_VERSION,
        "status": "operational",
        "docs": "/docs",
        "message": "SentraX AI Backend is running. Visit /docs for Swagger UI.",
    }


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint for monitoring and load-balancer probes."""
    return {
        "status": "healthy",
        "service": APP_NAME,
        "version": APP_VERSION,
    }


# ── WebSockets ────────────────────────────────────────────────────────────────

@app.websocket("/ws/alerts")
async def websocket_alerts_endpoint(websocket: WebSocket):
    """Real-time SOC alert stream. Receives HIGH/CRITICAL broadcasts from AlertEngine."""
    from utils.connection_manager import manager
    await manager.connect(websocket, channel="alerts")
    try:
        while True:
            await websocket.receive_text()   # keepalive / heartbeat frames
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel="alerts")
    except Exception:
        manager.disconnect(websocket, channel="alerts")


@app.websocket("/ws/dashboard")
async def websocket_dashboard_endpoint(websocket: WebSocket):
    """Live dashboard KPI stream. Pushed after every scan completion."""
    from utils.connection_manager import manager
    from utils.broadcast import _get_dashboard_stats
    await manager.connect(websocket, channel="dashboard")
    # Push current stats immediately on connect so dashboard loads without waiting
    try:
        await websocket.send_json({
            "event":     "dashboard_update",
            **_get_dashboard_stats(),
        })
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel="dashboard")
    except Exception:
        manager.disconnect(websocket, channel="dashboard")


@app.websocket("/ws/scans")
async def websocket_scans_endpoint(websocket: WebSocket):
    """Live recent-scan feed. Pushed a new_scan event after every successful scan."""
    from utils.connection_manager import manager
    await manager.connect(websocket, channel="scans")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel="scans")
    except Exception:
        manager.disconnect(websocket, channel="scans")

@app.get("/ws/status", tags=["WebSocket"])
async def websocket_status():
    """Return current active WebSocket connection counts per channel."""
    from utils.connection_manager import manager
    return {
        "alerts":    manager.connection_count("alerts"),
        "dashboard": manager.connection_count("dashboard"),
        "scans":     manager.connection_count("scans"),
    }

