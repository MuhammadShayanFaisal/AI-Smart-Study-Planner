from typing import List, Optional
from pydantic import BaseModel, Field


class SubjectIn(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    hours: int = Field(ge=1, le=8)
    priority: int = Field(ge=1, le=3)
    difficulty: int = Field(ge=1, le=5)
    preferred: str = Field(pattern="^(Morning|Evening)$")


class ScheduleRequest(BaseModel):
    subjects: List[SubjectIn] = Field(min_length=2)
    population_size: int = Field(default=30, ge=10, le=100)
    generations: int = Field(default=50, ge=10, le=200)
    break_interval: int = Field(default=2, ge=1, le=5)
    mutation_rate: float = Field(default=0.1, ge=0.01, le=0.5)
    seed: Optional[int] = None


class Progress(BaseModel):
    gen: int
    generations: int
    best_fitness: float


class SummaryRow(BaseModel):
    subject: str
    allocated: int
    scheduled: int


class ScheduleResult(BaseModel):
    schedule: List[dict]
    fitness: float
    fitness_history: List[float]
    overflow: List[str]
    violations: List[str]
    summary: List[SummaryRow]


class JobResponse(BaseModel):
    job_id: str
    status: str  # pending | running | done | failed
    progress: Optional[Progress] = None
    result: Optional[ScheduleResult] = None
    error: Optional[str] = None
