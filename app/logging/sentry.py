import sentry_sdk
import logging
from sentry_sdk.integrations.logging import LoggingIntegration
import os
from dotenv import load_dotenv
from pathlib import Path

# Charge .env depuis la racine du projet, peu importe où est lancé le script
BASE_DIR = Path(__file__).resolve().parent.parent  # = epic_events/
load_dotenv(dotenv_path=BASE_DIR / ".env")
SENTRY_DSN = os.getenv("SENTRY_DSN")

def init_sentry():
    sentry_logging = LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)

    def before_send_filter(event, hint):
        message = event.get("message", "")
        if "abort: no error message" in message:
            return None
        return event

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[sentry_logging],
        traces_sample_rate=1.0,
        send_default_pii=True,
        before_send=before_send_filter,
        _experiments={
        "enable_logs": True,
    },
    )
    
