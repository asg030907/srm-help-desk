"""
main.py
FastAPI application entry point.
Run locally with: uvicorn main:app --reload

Runs two agents:
  - the Intake Agent, triggered per-request by POST /api/chat
    (src/agent/executor.py) — students talk to this one.
  - the Dispatch Agent, triggered on a schedule by the background
    scheduler set up below (src/agent/dispatch_executor.py) — nobody
    talks to this one directly; it batch-assigns open tickets.
They hand off work through the shared ticket store, not through
calling each other.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.agent.dispatch_executor import DispatchExecutor
from src.api.routes import router as api_router
from src.utils.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)
_scheduler = BackgroundScheduler()

app = FastAPI(
    title="ai-agent-project",
    description="CrewAI-based agent service with search, calculator, and weather tools.",
    version="0.1.0",
)

# Allow the deployed frontend (a different origin from the API) to call
# this service. ALLOWED_ORIGINS is a comma-separated list in .env, e.g.
# "https://your-frontend.netlify.app,http://localhost:5500". Defaults to
# "*" for early prototyping — tighten this before sharing the URL widely.
_settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


def _run_dispatch_pass() -> None:
    """Scheduled job body — kept as a plain function so failures are logged
    instead of silently killing the scheduler thread."""
    try:
        DispatchExecutor().run()
    except Exception:  # noqa: BLE001
        logger.exception("Scheduled dispatch pass failed")


@app.on_event("startup")
def on_startup() -> None:
    logger.info("ai-agent-project starting up")
    interval = _settings.dispatch_interval_minutes
    _scheduler.add_job(
        _run_dispatch_pass,
        "interval",
        minutes=interval,
        id="dispatch_pass",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("Dispatch Agent scheduled every %s minute(s)", interval)


@app.on_event("shutdown")
def on_shutdown() -> None:
    _scheduler.shutdown(wait=False)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=_settings.app_host, port=_settings.app_port, reload=True)
