import time
import uuid
from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


class JobStore:
    def __init__(self):
        self._jobs: dict[str, dict] = {}

    def create(self, mode: str, input_data: dict) -> str:
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = {
            "id": job_id,
            "mode": mode,
            "status": JobStatus.PENDING,
            "created_at": time.time(),
            "completed_at": None,
            "result": None,
            "error": None,
            "steps": [],
            "input": input_data,
        }
        return job_id

    def get(self, job_id: str) -> dict | None:
        return self._jobs.get(job_id)

    def update(self, job_id: str, **kwargs) -> None:
        if job_id in self._jobs:
            self._jobs[job_id].update(kwargs)

    def set_result(self, job_id: str, result: dict, steps: list | None = None) -> None:
        self._jobs[job_id].update({
            "status": JobStatus.DONE,
            "completed_at": time.time(),
            "result": result,
            "steps": steps or [],
        })

    def set_error(self, job_id: str, error: str) -> None:
        self._jobs[job_id].update({
            "status": JobStatus.ERROR,
            "completed_at": time.time(),
            "error": error,
        })


store = JobStore()
