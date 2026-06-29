import asyncio
import json

from app.core.database import SessionLocal
from app.models.search_job import SearchJob

# How often (seconds) to poll PostgreSQL for progress changes
POLL_INTERVAL = 1.0

# Maximum time (seconds) to stream before force-closing the connection.
# Guards against orphaned connections when the client silently disconnects.
STREAM_TIMEOUT = 600.0

TERMINAL_STATUSES = {"completed", "failed"}


def _fetch_job_snapshot(job_id: int) -> dict | None:
    """
    Synchronous DB read — runs inside asyncio.to_thread so it never
    blocks the FastAPI event loop.  Opens and closes its own session
    to avoid holding a connection across awaits.
    """
    db = SessionLocal()
    try:
        job = db.query(SearchJob).filter(SearchJob.id == job_id).first()
        if not job:
            return None
        return {
            "job_id":      job.id,
            "status":      job.status,
            "progress":    job.progress,
            "current_step": job.current_step,
        }
    finally:
        db.close()


def _build_sse_event(data: dict) -> str:
    """Format a dict as a valid SSE event string."""
    return f"data: {json.dumps(data)}\n\n"


def _build_sse_error(message: str) -> str:
    return f"event: error\ndata: {json.dumps({'error': message})}\n\n"


async def job_progress_stream(job_id: int):
    """
    Async generator that yields SSE-formatted strings.

    Lifecycle:
    - Emits an event immediately on connect (current state).
    - Polls PostgreSQL every POLL_INTERVAL seconds.
    - Emits a new event ONLY when progress or status changes.
    - Closes cleanly when status is 'completed' or 'failed'.
    - Closes after STREAM_TIMEOUT seconds to prevent orphaned connections.
    - Emits a keep-alive comment every 15 s so proxies don't close idle connections.
    """
    last_progress: int | None = None
    last_status:   str | None = None
    elapsed = 0.0
    keepalive_interval = 15.0
    keepalive_counter = 0.0

    # ── Initial existence check ──────────────────────────────────────────────
    snapshot = await asyncio.to_thread(_fetch_job_snapshot, job_id)
    if snapshot is None:
        yield _build_sse_error(f"job {job_id} not found")
        return

    # ── Emit current state immediately so the client sees something at once ──
    yield _build_sse_event(snapshot)
    last_progress = snapshot["progress"]
    last_status   = snapshot["status"]

    if last_status in TERMINAL_STATUSES:
        return

    # ── Polling loop ─────────────────────────────────────────────────────────
    while elapsed < STREAM_TIMEOUT:
        await asyncio.sleep(POLL_INTERVAL)
        elapsed      += POLL_INTERVAL
        keepalive_counter += POLL_INTERVAL

        snapshot = await asyncio.to_thread(_fetch_job_snapshot, job_id)

        if snapshot is None:
            # Job row disappeared — treat as failure
            yield _build_sse_error(f"job {job_id} no longer exists")
            return

        changed = (
            snapshot["progress"] != last_progress
            or snapshot["status"] != last_status
        )

        if changed:
            yield _build_sse_event(snapshot)
            last_progress = snapshot["progress"]
            last_status   = snapshot["status"]
            keepalive_counter = 0.0  # reset keepalive timer after a real event

        if last_status in TERMINAL_STATUSES:
            return

        # Keep-alive comment — invisible to EventSource, but keeps proxies alive
        if keepalive_counter >= keepalive_interval:
            yield ": keep-alive\n\n"
            keepalive_counter = 0.0

    # Timeout reached — notify client
    yield _build_sse_error("stream timeout: reconnect to continue polling")
