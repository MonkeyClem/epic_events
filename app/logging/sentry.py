import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

def init_sentry():
    sentry_logging = LoggingIntegration(
        level="ERROR",         
        event_level="ERROR"   
    )

    # sentry_sdk.init(
    #     dsn="https://109e5be648910c8ce982f25c4b793e5d@o4509571053387776.ingest.de.sentry.io/4509571093823568",
    #     integrations=[sentry_logging],
    #     traces_sample_rate=1.0,
    #     send_default_pii=True,
    #     before_send=lambda event, hint: None if "abort: no error message" in str(event) else event     
    # )

    def before_send_filter(event, hint):
        message = event.get("message", "")
        if "abort: no error message" in message:
            return None
        return event

    sentry_sdk.init(
        dsn="…",
        integrations=[sentry_logging],
        traces_sample_rate=1.0,
        send_default_pii=True,
        before_send=before_send_filter
    )
