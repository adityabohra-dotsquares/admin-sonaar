# app/audit_logger.py
from loguru import logger
from pathlib import Path
from datetime import datetime, timezone

# Ensure log directory exists
Path("logs").mkdir(exist_ok=True)

# Configure the audit log file
logger.add(
    "logs/audit.jsonl",       # one JSON record per line
    rotation="1 day",         # new file every day
    retention="180 days",     # keep logs for 6 months
    compression="zip",        # compress old logs
    serialize=True,           # structured JSON output
    enqueue=True              # async-safe logging
)

def audit_log(
    user_id: int | None,
    action: str,
    object_type: str,
    object_id: str | None = None,
    changes: dict | None = None,
    ip: str | None = None,
    user_agent: str | None = None,
    status: str = "success",
):
    """Write a JSON audit log entry."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "action": action,
        "object_type": object_type,
        "object_id": object_id,
        "changes": changes,
        "ip": ip,
        "user_agent": user_agent,
        "status": status,
    }
    logger.info(entry)
