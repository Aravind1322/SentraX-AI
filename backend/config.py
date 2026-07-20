import os
import logging
import logging.config
from dotenv import load_dotenv

# Load environment variable files
load_dotenv()

# Setup log directory structure before initializing standard handlers
os.makedirs("logs", exist_ok=True)

log_config = os.path.join(os.path.dirname(__file__), "logging.conf")
if os.path.exists(log_config):
    try:
        logging.config.fileConfig(log_config, disable_existing_loggers=False)
    except Exception as e:
        print(f"Failed initializing production logging configuration: {e}")

# ── Application metadata ───────────────────────────────────────────────────────
APP_NAME        = "SentraX AI Backend"
APP_VERSION     = "1.0.0"
APP_DESCRIPTION = (
    "Enterprise Cyber Threat Intelligence API — "
    "AI-powered cybersecurity and fraud detection platform."
)

# ── Database ───────────────────────────────────────────────────────────────────
def get_database_path() -> str:
    """Always returns the canonical absolute path of backend/sentrax_backend.db."""
    env_path = os.environ.get("SENTRAX_DB_PATH")
    if env_path:
        return os.path.abspath(env_path)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "sentrax_backend.db"))

DATABASE_PATH = get_database_path()
SENTRAX_DEBUG = os.environ.get("SENTRAX_DEBUG", "True").lower() == "true"

# ── Server ─────────────────────────────────────────────────────────────────────
HOST = os.environ.get("SENTRAX_HOST", "0.0.0.0")
PORT = int(os.environ.get("SENTRAX_PORT", 8000))

# ── Security ───────────────────────────────────────────────────────────────────
SECRET_KEY  = os.environ.get("SENTRAX_SECRET_KEY", "changeme-before-production")
ALLOWED_ORIGINS: list[str] = os.environ.get("SENTRAX_ORIGINS", "*").split(",")

# ── Feature flags (placeholder) ────────────────────────────────────────────────
ENABLE_URL_SCAN      = True
ENABLE_SMS_SCAN      = True
ENABLE_FRAUD_SCAN    = True
ENABLE_EMPLOYEE_SCAN = True
