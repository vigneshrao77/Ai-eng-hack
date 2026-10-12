import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Callable, Any, Dict, List
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import Job
from app.core.logging import logger

_executor = ThreadPoolExecutor(max_workers=4)
_ws_subscribers: Dict[str, List[Any]] = {}


def register_ws_subscriber(job_id: str, ws: Any):
    if job_id not in _ws_subscribers:
        _ws_subscribers[job_id] = []
    _ws_subscribers[job_id].append(ws)


def unregister_ws_subscriber(job_id: str, ws: Any):
    if job_id in _ws_subscribers and ws in _ws_subscribers[job_id]:
        _ws_subscribers[job_id].remove(ws)


def update_job_progress(job_id: str, progress: int, message: str, status: str = "RUNNING", result: Any = None):
    db: Session = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.progress = progress
            job.message = message
            job.status = status
            if result is not None:
                job.result_json = result
            if status in ("COMPLETED", "FAILED"):
                job.finished_at = datetime.now(timezone.utc)
            db.commit()
            logger.info(f"Job [{job_id}] -> {status} ({progress}%): {message}")
    finally:
        db.close()


def submit_background_job(job_id: str, fn: Callable[..., Any], *args, **kwargs):
    """Run a long task asynchronously in the background pool."""
    def wrapper():
        db: Session = SessionLocal()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = "RUNNING"
                job.started_at = datetime.now(timezone.utc)
                db.commit()

            # Execute task function
            result = fn(job_id, *args, **kwargs)

            # Mark complete
            update_job_progress(job_id, progress=100, message="Completed successfully", status="COMPLETED", result=result)
        except Exception as e:
            logger.error(f"Job [{job_id}] failed: {e}")
            db_err: Session = SessionLocal()
            try:
                job_err = db_err.query(Job).filter(Job.id == job_id).first()
                if job_err:
                    job_err.status = "FAILED"
                    job_err.error = str(e)
                    job_err.finished_at = datetime.now(timezone.utc)
                    db_err.commit()
            finally:
                db_err.close()
        finally:
            db.close()

    _executor.submit(wrapper)
