import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

def init_sentry():
    sentry_logging = LoggingIntegration(
        level="ERROR",         # Log level capté
        event_level="ERROR"    # Ce qui est envoyé à Sentry
    )

    sentry_sdk.init(
        dsn="https://109e5be648910c8ce982f25c4b793e5d@o4509571053387776.ingest.de.sentry.io/4509571093823568",
        integrations=[sentry_logging],
        traces_sample_rate=1.0,
        send_default_pii=True
    )
