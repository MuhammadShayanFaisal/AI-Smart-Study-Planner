import asyncio
import random
import threading
import uuid
from collections import Counter
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from ga import run_ga
from csp import get_violations
from schemas import (
    ScheduleRequest,
    JobResponse,
    ScheduleResult,
    Progress,
    SummaryRow,
)

app = FastAPI(title="AI Smart Study Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store (single-process, not restart-safe).
# job_id -> {status, progress, result, error}
_jobs: Dict[str, dict] = {}
_lock = threading.Lock()


def _build_result(subjects_data, preferred_times, schedule, fitness, history, overflow):
    """Shape the GA output + CSP checks into the API response model."""
    subject_hours = {s["name"]: s["hours"] for s in subjects_data}
    subject_names = [s["name"] for s in subjects_data]

    violations = get_violations(schedule, subject_hours, subject_names)

    counts = Counter(sub for _, sub in schedule if sub != "Break")
    summary = [
        SummaryRow(
            subject=s["name"],
            allocated=s["hours"],
            scheduled=counts.get(s["name"], 0),
        )
        for s in subjects_data
    ]

    return ScheduleResult(
        schedule=[{"time": slot, "subject": sub} for slot, sub in schedule],
        fitness=fitness,
        fitness_history=history,
        overflow=overflow,
        violations=violations,
        summary=[row.model_dump() for row in summary],
    )


def _run_job_sync(job_id: str, req: ScheduleRequest):
    """Runs in a worker thread: executes the GA and stores the result."""
    try:
        subjects_data = [s.model_dump() for s in req.subjects]
        preferred_times = {s["name"]: s["preferred"] for s in subjects_data}
        total_hours = sum(s["hours"] for s in subjects_data)

        if req.seed is not None:
            random.seed(req.seed)

        def on_progress(gen, fit):
            with _lock:
                _jobs[job_id]["progress"] = Progress(
                    gen=gen, generations=req.generations, best_fitness=fit
                ).model_dump()

        schedule, fitness, history, overflow = run_ga(
            subjects_data=subjects_data,
            preferred_times=preferred_times,
            total_hours=total_hours,
            break_interval=req.break_interval,
            population_size=req.population_size,
            generations=req.generations,
            base_mutation_rate=req.mutation_rate,
            progress_callback=on_progress,
        )

        result = _build_result(
            subjects_data, preferred_times, schedule, fitness, history, overflow
        )
        with _lock:
            _jobs[job_id]["status"] = "done"
            _jobs[job_id]["result"] = result.model_dump()
    except Exception as exc:
        with _lock:
            _jobs[job_id]["status"] = "failed"
            _jobs[job_id]["error"] = str(exc)


@app.post("/api/schedule", status_code=202)
async def create_schedule(req: ScheduleRequest):
    job_id = uuid.uuid4().hex[:12]
    with _lock:
        _jobs[job_id] = {
            "job_id": job_id,
            "status": "pending",
            "progress": None,
            "result": None,
            "error": None,
        }

    asyncio.create_task(_execute(job_id, req))
    return {"job_id": job_id}


async def _execute(job_id: str, req: ScheduleRequest):
    """Offload the CPU-bound GA to a threadpool so the event loop stays responsive."""
    with _lock:
        _jobs[job_id]["status"] = "running"
    await asyncio.to_thread(_run_job_sync, job_id, req)


@app.get("/api/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    with _lock:
        job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse(**job)


@app.get("/health")
async def health():
    return {"status": "ok"}
