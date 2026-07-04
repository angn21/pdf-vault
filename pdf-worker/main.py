"""PDF Vault worker API."""

from __future__ import annotations

import json
import threading
from typing import Any, Dict, List

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from storage import JobStatus, get_store
from tools import MIME_MAP, process_job
from cli import (
    ghostscript_available,
    ocrmypdf_available,
    poppler_available,
    qpdf_available,
)

app = FastAPI(title="PDF Vault Worker", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = get_store()

_capabilities: Dict[str, bool] | None = None


def _probe_capabilities() -> Dict[str, bool]:
    return {
        "ghostscript": ghostscript_available(),
        "qpdf": qpdf_available(),
        "poppler": poppler_available(),
        "ocrmypdf": ocrmypdf_available(),
    }


@app.on_event("startup")
def _cache_capabilities() -> None:
    global _capabilities
    _capabilities = _probe_capabilities()


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/capabilities")
async def capabilities() -> Dict[str, Any]:
    if _capabilities is None:
        return _probe_capabilities()
    return dict(_capabilities)


@app.get("/tools")
async def list_tools() -> List[Dict[str, Any]]:
    return [
        {"id": "merge", "name": "Merge PDF", "category": "organize", "accept": ".pdf", "multiple": True},
        {"id": "split", "name": "Split PDF", "category": "organize", "accept": ".pdf"},
        {"id": "compress", "name": "Compress PDF", "category": "optimize", "accept": ".pdf"},
        {"id": "rotate", "name": "Rotate PDF", "category": "organize", "accept": ".pdf"},
        {"id": "organize", "name": "Organize PDF", "category": "organize", "accept": ".pdf"},
        {"id": "remove-pages", "name": "Remove Pages", "category": "organize", "accept": ".pdf"},
        {"id": "protect", "name": "Protect PDF", "category": "secure", "accept": ".pdf"},
        {"id": "unlock", "name": "Unlock PDF", "category": "secure", "accept": ".pdf"},
        {"id": "watermark", "name": "Watermark", "category": "secure", "accept": ".pdf"},
        {"id": "page-numbers", "name": "Page Numbers", "category": "organize", "accept": ".pdf"},
        {"id": "pdf-to-jpg", "name": "PDF to JPG", "category": "convert", "accept": ".pdf"},
        {"id": "images-to-pdf", "name": "Images to PDF", "category": "convert", "accept": ".jpg,.jpeg,.png", "multiple": True},
        {"id": "extract-images", "name": "Extract Images", "category": "convert", "accept": ".pdf"},
        {"id": "pdf-to-word", "name": "PDF to Word", "category": "convert", "accept": ".pdf"},
        {"id": "ocr", "name": "OCR PDF", "category": "advanced", "accept": ".pdf"},
        {"id": "repair", "name": "Repair PDF", "category": "advanced", "accept": ".pdf"},
        {"id": "pdf-to-pdfa", "name": "PDF to PDF/A", "category": "advanced", "accept": ".pdf"},
        {"id": "compare", "name": "Compare PDF", "category": "advanced", "accept": ".pdf", "multiple": True},
        {"id": "redact", "name": "Redact PDF", "category": "advanced", "accept": ".pdf"},
        {"id": "crop", "name": "Crop PDF", "category": "organize", "accept": ".pdf"},
        {"id": "sign", "name": "Sign PDF", "category": "secure", "accept": ".pdf"},
        {"id": "workflow", "name": "Workflow", "category": "automate", "accept": ".pdf", "multiple": True},
    ]


def _run_job(job_id: str) -> None:
    job = store.get(job_id)
    if not job:
        return
    store.update(job, status=JobStatus.PROCESSING, message="Processing", progress=10)
    try:
        result_path, mime = process_job(store, job)
        store.set_result(job, result_path, mime)
    except Exception as exc:
        job = store.get(job_id)
        if job:
            store.fail(job, str(exc))


def _start_job(job_id: str) -> None:
    thread = threading.Thread(target=_run_job, args=(job_id,), daemon=True)
    thread.start()


@app.post("/jobs")
async def create_job(
    tool: str = Form(...),
    options: str = Form("{}"),
    files: List[UploadFile] = File(...),
) -> JSONResponse:
    try:
        parsed_options: dict[str, Any] = json.loads(options) if options else {}
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid options JSON") from exc

    if not files:
        raise HTTPException(status_code=400, detail="At least one file is required")

    job = store.create(tool=tool, options=parsed_options)
    for upload in files:
        content = await upload.read()
        store.save_input(job.id, upload.filename or "file.pdf", content)

    _start_job(job.id)
    return JSONResponse({"jobId": job.id, "status": job.status.value})


@app.get("/jobs/{job_id}")
async def get_job(job_id: str) -> JSONResponse:
    job = store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JSONResponse(job.to_dict())


@app.get("/jobs/{job_id}/download")
def download_job(job_id: str) -> FileResponse:
    job = store.get(job_id)
    if not job or job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=404, detail="Result not ready")
    path = store.result_path(job)
    if not path or not path.exists():
        raise HTTPException(status_code=404, detail="Result file missing")

    def _purge() -> None:
        if job.purge_after_download:
            threading.Timer(2.0, store.purge, args=[job_id]).start()

    return FileResponse(
        path,
        media_type=job.result_mime,
        filename=job.result_filename or "result.pdf",
        background=_purge,
    )


@app.delete("/jobs/{job_id}")
def delete_job(job_id: str) -> JSONResponse:
    job = store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    store.purge(job_id)
    return JSONResponse({"deleted": True})
