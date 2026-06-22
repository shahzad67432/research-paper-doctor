import json
import os
import sys
import tempfile
import threading

from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.graph import app as langgraph_app
from src.rag_engine import _get_collection as get_rag_collection

from api.job_store import store

app = FastAPI(title="PaperDoctor AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QARequest(BaseModel):
    query: str


class DiscoverRequest(BaseModel):
    interest: str


def _run_job(job_id: str) -> None:
    job = store.get(job_id)
    if not job:
        return
    try:
        store.update(job_id, status="running")
        mode = job["mode"]
        inp = job["input"]

        state = {"mode": mode, "paper_path": None, "query": None}

        if mode == "analyze":
            state["paper_path"] = inp["paper_path"]
        elif mode == "qa":
            state["query"] = inp["query"]
        elif mode == "discover":
            state["query"] = inp["interest"]

        result = langgraph_app.invoke(state)

        steps = result.get("_steps", [])
        store.set_result(job_id, result, steps=steps)
    except Exception as e:
        print(f"Job {job_id} failed: {e}", file=sys.stderr)
        store.set_error(job_id, str(e))
    finally:
        paper_path = job.get("input", {}).get("paper_path")
        if paper_path and os.path.exists(paper_path):
            try:
                os.unlink(paper_path)
            except Exception:
                pass


def _background_run(job_id: str) -> None:
    thread = threading.Thread(target=_run_job, args=(job_id,), daemon=True)
    thread.start()


@app.post("/api/analyze")
async def analyze_paper(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted")

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    content = await file.read()
    tmp.write(content)
    tmp.close()

    job_id = store.create("analyze", {"paper_path": tmp.name})
    _background_run(job_id)
    return {"job_id": job_id}


@app.post("/api/qa")
async def qa_query(body: QARequest):
    if not body.query.strip():
        raise HTTPException(400, "Query is required")
    job_id = store.create("qa", {"query": body.query})
    _background_run(job_id)
    return {"job_id": job_id}


@app.post("/api/discover")
async def discover_gaps(body: DiscoverRequest):
    if not body.interest.strip():
        raise HTTPException(400, "Research interest is required")
    job_id = store.create("discover", {"interest": body.interest})
    _background_run(job_id)
    return {"job_id": job_id}


@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    job = store.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return {
        "id": job["id"],
        "mode": job["mode"],
        "status": job["status"],
        "created_at": job["created_at"],
        "completed_at": job["completed_at"],
        "result": job["result"],
        "error": job["error"],
        "steps": job["steps"],
    }


@app.get("/api/cache/stats")
async def cache_stats():
    try:
        collection = get_rag_collection()
        count = collection.count()
    except Exception:
        count = 0
    return {"papers_cached": count}


@app.get("/api/health")
async def health():
    return {"status": "ok"}
