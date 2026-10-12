# AI Smart Study Planner

Genetic Algorithm + Constraint Satisfaction study scheduler.  
**v2** — FastAPI backend, React (Recharts) frontend.

## Quick Start

### 1. Backend (FastAPI)

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt

cd backend
uvicorn app:app --port 8000
```

### 2. Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).  
The Vite dev server proxies `/api` to the backend on port 8000.

## API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/schedule` | Start a scheduling job. Returns `202 {job_id}`. |
| `GET` | `/api/jobs/{job_id}` | Poll job status/progress. Returns full result when `done`. |
| `GET` | `/health` | Health check. |

### Request body

```json
{
  "subjects": [
    {"name": "AI", "hours": 2, "priority": 3, "difficulty": 5, "preferred": "Morning"}
  ],
  "population_size": 30,
  "generations": 50,
  "break_interval": 2,
  "mutation_rate": 0.1,
  "seed": 42
}
```

### Response (when job is `done`)

```json
{
  "schedule": [{"time": "8-9", "subject": "AI"}],
  "fitness": 218,
  "fitness_history": [120, 135, "..."],
  "overflow": [],
  "violations": [],
  "summary": [{"subject": "AI", "allocated": 2, "scheduled": 2}]
}
```

## Project Structure

```
backend/
  app.py          # FastAPI app (job endpoints, threadpool execution)
  schemas.py      # Pydantic request/response models
  ga.py           # Genetic algorithm
  csp.py          # Constraint validation + repair
  fitness.py      # Fitness scoring
  utils.py        # Formatting helpers
frontend/
  src/
    App.jsx       # Main layout, tabs, state
    api.js        # API client + polling
    components/   # SubjectForm, ScheduleTab, FitnessTab, CspTab, SummaryTab
```
