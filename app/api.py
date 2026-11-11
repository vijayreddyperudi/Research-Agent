import sys
from pathlib import Path

# Ensure project root is in sys.path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid
import time
from app.workflow import research_graph, run_research
from app.config import settings

app = FastAPI(
    title="Enterprise AI Research Agent API",
    description="REST API to orchestrate multi-step research tasks, source evaluations, and structured report generation.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for asynchronous research jobs
tasks_db: Dict[str, Dict[str, Any]] = {}


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=3, description="The research question or topic.")
    max_rounds: Optional[int] = Field(default=3, ge=1, le=5, description="Max search rounds.")


class ResearchResponse(BaseModel):
    task_id: str
    status: str
    user_query: str
    final_report: Optional[str] = None
    research_plan: Optional[List[str]] = None
    evaluated_sources_count: Optional[int] = 0
    research_round: Optional[int] = 0
    is_sufficient: Optional[bool] = False
    duration_seconds: Optional[float] = None


@app.get("/health")
def health_check():
    """Service health and readiness check."""
    return {
        "status": "healthy",
        "service": "Enterprise AI Research Agent",
        "version": "1.0.0",
        "timestamp": time.time()
    }


def execute_background_research(task_id: str, query: str, max_rounds: int):
    tasks_db[task_id]["status"] = "running"
    start_time = time.time()
    try:
        result = run_research(query=query, max_rounds=max_rounds)
        duration = round(time.time() - start_time, 2)
        tasks_db[task_id].update({
            "status": "completed",
            "final_report": result.get("final_report", ""),
            "research_plan": result.get("research_plan", []),
            "evaluated_sources_count": len(result.get("evaluated_sources", [])),
            "research_round": result.get("research_round", 1),
            "is_sufficient": result.get("is_sufficient", False),
            "duration_seconds": duration,
            "evaluated_sources": result.get("evaluated_sources", [])
        })
    except Exception as e:
        tasks_db[task_id].update({
            "status": "failed",
            "error": str(e),
            "duration_seconds": round(time.time() - start_time, 2)
        })


@app.post("/research", response_model=ResearchResponse)
def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """
    Initiate a research task asynchronously.
    """
    task_id = str(uuid.uuid4())
    tasks_db[task_id] = {
        "task_id": task_id,
        "status": "queued",
        "user_query": request.query,
        "max_rounds": request.max_rounds,
        "created_at": time.time()
    }

    background_tasks.add_task(
        execute_background_research,
        task_id=task_id,
        query=request.query,
        max_rounds=request.max_rounds
    )

    return ResearchResponse(
        task_id=task_id,
        status="queued",
        user_query=request.query
    )


@app.post("/research/sync", response_model=ResearchResponse)
def execute_research_sync(request: ResearchRequest):
    """
    Execute research synchronously and wait for the final completed report.
    """
    task_id = str(uuid.uuid4())
    start_time = time.time()
    try:
        result = run_research(query=request.query, max_rounds=request.max_rounds)
        duration = round(time.time() - start_time, 2)
        return ResearchResponse(
            task_id=task_id,
            status="completed",
            user_query=request.query,
            final_report=result.get("final_report"),
            research_plan=result.get("research_plan"),
            evaluated_sources_count=len(result.get("evaluated_sources", [])),
            research_round=result.get("research_round"),
            is_sufficient=result.get("is_sufficient"),
            duration_seconds=duration
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research execution failed: {str(e)}")


@app.get("/research/{task_id}")
def get_research_status(task_id: str):
    """Retrieve status and report of an ongoing or completed research task."""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks_db[task_id]

