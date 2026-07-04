"""Ephemeral job storage with auto-purge."""

from __future__ import annotations

import json
import os
import shutil
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Job:
    id: str
    tool: str
    status: JobStatus
    options: dict[str, Any]
    created_at: float
    updated_at: float
    progress: float = 0.0
    message: str = ""
    result_filename: str | None = None
    result_mime: str = "application/pdf"
    error: str | None = None
    input_files: list[str] = field(default_factory=list)
    purge_after_download: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "tool": self.tool,
            "status": self.status.value,
            "options": self.options,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "progress": self.progress,
            "message": self.message,
            "resultFilename": self.result_filename,
            "resultMime": self.result_mime,
            "error": self.error,
            "inputFiles": self.input_files,
            "downloadUrl": f"/jobs/{self.id}/download"
            if self.status == JobStatus.COMPLETED and self.result_filename
            else None,
        }


class JobStore:
    def __init__(self, data_dir: str, ttl_seconds: int = 600) -> None:
        self.data_dir = Path(data_dir.strip())
        self.ttl_seconds = ttl_seconds
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._jobs: dict[str, Job] = {}
        self._lock = threading.RLock()
        self._start_cleanup_thread()

    def _job_dir(self, job_id: str) -> Path:
        return self.data_dir / job_id

    def create(self, tool: str, options: dict[str, Any] | None = None) -> Job:
        job_id = str(uuid.uuid4())
        now = time.time()
        job = Job(
            id=job_id,
            tool=tool,
            status=JobStatus.PENDING,
            options=options or {},
            created_at=now,
            updated_at=now,
        )
        self._job_dir(job_id).mkdir(parents=True, exist_ok=True)
        with self._lock:
            self._jobs[job_id] = job
            self._persist(job)
        return job

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            if job_id in self._jobs:
                return self._jobs[job_id]
        meta = self._job_dir(job_id) / "meta.json"
        if not meta.exists():
            return None
        job = self._load_meta(meta)
        with self._lock:
            self._jobs[job_id] = job
        return job

    def update(self, job: Job, **kwargs: Any) -> Job:
        for key, value in kwargs.items():
            if hasattr(job, key):
                setattr(job, key, value)
        job.updated_at = time.time()
        with self._lock:
            self._jobs[job.id] = job
            self._persist(job)
        return job

    def save_input(self, job_id: str, filename: str, content: bytes) -> Path:
        safe_name = Path(filename).name
        path = self._job_dir(job_id) / "input" / safe_name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                meta = self._job_dir(job_id) / "meta.json"
                if meta.exists():
                    job = self._load_meta(meta)
                    self._jobs[job_id] = job
            if job and safe_name not in job.input_files:
                job.input_files.append(safe_name)
                self._persist(job)
        return path

    def input_dir(self, job_id: str) -> Path:
        path = self._job_dir(job_id) / "input"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def output_dir(self, job_id: str) -> Path:
        path = self._job_dir(job_id) / "output"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def set_result(self, job: Job, path: Path, mime: str = "application/pdf") -> Job:
        return self.update(
            job,
            status=JobStatus.COMPLETED,
            result_filename=path.name,
            result_mime=mime,
            progress=100.0,
            message="Done",
        )

    def fail(self, job: Job, error: str) -> Job:
        return self.update(
            job,
            status=JobStatus.FAILED,
            error=error,
            message="Failed",
        )

    def result_path(self, job: Job) -> Path | None:
        if not job.result_filename:
            return None
        return self.output_dir(job.id) / job.result_filename

    def purge(self, job_id: str) -> None:
        with self._lock:
            self._jobs.pop(job_id, None)
        path = self._job_dir(job_id)
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)

    def _persist(self, job: Job) -> None:
        meta = self._job_dir(job.id) / "meta.json"
        payload = {
            "id": job.id,
            "tool": job.tool,
            "status": job.status.value,
            "options": job.options,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
            "progress": job.progress,
            "message": job.message,
            "result_filename": job.result_filename,
            "result_mime": job.result_mime,
            "error": job.error,
            "input_files": job.input_files,
            "purge_after_download": job.purge_after_download,
        }
        meta.write_text(json.dumps(payload), encoding="utf-8")

    def _load_meta(self, meta: Path) -> Job:
        data = json.loads(meta.read_text(encoding="utf-8"))
        return Job(
            id=data["id"],
            tool=data["tool"],
            status=JobStatus(data["status"]),
            options=data.get("options", {}),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            progress=data.get("progress", 0),
            message=data.get("message", ""),
            result_filename=data.get("result_filename"),
            result_mime=data.get("result_mime", "application/pdf"),
            error=data.get("error"),
            input_files=data.get("input_files", []),
            purge_after_download=data.get("purge_after_download", True),
        )

    def _start_cleanup_thread(self) -> None:
        def cleanup() -> None:
            while True:
                time.sleep(60)
                try:
                    if not self.data_dir.exists():
                        self.data_dir.mkdir(parents=True, exist_ok=True)
                        continue
                    now = time.time()
                    for job_dir in self.data_dir.iterdir():
                        if not job_dir.is_dir():
                            continue
                        meta = job_dir / "meta.json"
                        if not meta.exists():
                            continue
                        try:
                            job = self._load_meta(meta)
                            if now - job.updated_at > self.ttl_seconds:
                                self.purge(job.id)
                        except Exception:
                            pass
                except Exception:
                    pass

        thread = threading.Thread(target=cleanup, daemon=True)
        thread.start()


def get_store() -> JobStore:
    data_dir = os.environ.get("DATA_DIR", "./data/jobs").strip()
    ttl = int(os.environ.get("JOB_TTL_SECONDS", "600").strip())
    return JobStore(data_dir=data_dir, ttl_seconds=ttl)
