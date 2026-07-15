# SentraX AI — Backend API

> **Enterprise Cyber Threat Intelligence API**  
> FastAPI · Uvicorn · Pydantic v2 · SQLite

---

## Architecture

```
backend/
├── main.py            # FastAPI app entry point — routers, CORS, root endpoints
├── config.py          # Central configuration (APP_NAME, VERSION, DATABASE_PATH …)
├── database.py        # SQLite connection helper & schema init (backend-only DB)
├── schemas.py         # Pydantic request / response models for all scan types
├── requirements.txt   # Python dependencies
│
├── routes/            # FastAPI routers — one file per scan domain
│   ├── url.py         # /api/url
│   ├── sms.py         # /api/sms
│   ├── fraud.py       # /api/fraud
│   └── employee.py    # /api/employee
│
├── services/          # Business logic / service layer
│   ├── url_service.py
│   ├── sms_service.py
│   ├── fraud_service.py
│   └── employee_service.py
│
├── models/            # ORM models (future — SQLAlchemy / SQLModel)
└── utils/
    └── helpers.py     # Shared utilities (threat-tier, login-hour parser …)
```

> The backend database (`sentrax_backend.db`) is **separate** from the Streamlit
> scan-history database (`data/sentrax.db`). The two are never connected or shared.

---

## Installation

```bash
# 1. Enter the backend directory
cd backend

# 2. Create and activate a virtual environment (already created as venv/)
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Running the server

```bash
# Development (auto-reload on save)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## Available Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/` | Root — platform info |
| `GET`  | `/health` | Health check |
| `GET`  | `/api/url/` | URL API status |
| `POST` | `/api/url/scan` | Scan a URL |
| `GET`  | `/api/sms/` | SMS API status |
| `POST` | `/api/sms/scan` | Analyse an SMS message |
| `GET`  | `/api/fraud/` | Fraud API status |
| `POST` | `/api/fraud/scan` | Analyse a transaction |
| `GET`  | `/api/employee/` | Employee API status |
| `POST` | `/api/employee/scan` | Analyse an employee login |

---

## Swagger / OpenAPI

Once the server is running, visit:

| UI | URL |
|----|-----|
| **Swagger UI** | http://localhost:8000/docs |
| **ReDoc** | http://localhost:8000/redoc |
| **OpenAPI JSON** | http://localhost:8000/openapi.json |

---

## Configuration

All values can be overridden with environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SENTRAX_DB_PATH` | `backend/sentrax_backend.db` | Backend SQLite path |
| `SENTRAX_HOST` | `0.0.0.0` | Bind host |
| `SENTRAX_PORT` | `8000` | Bind port |
| `SENTRAX_SECRET_KEY` | `changeme-before-production` | JWT secret (future) |
| `SENTRAX_ORIGINS` | `*` | Comma-separated CORS origins |

---

## Next Steps (Future Sprints)

- [ ] Migrate detection logic from `src/utils/detector.py`
- [ ] Add JWT authentication middleware
- [ ] Connect Streamlit frontend via `httpx` API calls
- [ ] Add SQLAlchemy ORM models to `models/`
- [ ] Write pytest integration tests for each endpoint
