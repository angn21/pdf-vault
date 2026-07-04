"""PDF tool implementations."""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path
from typing import Any

import img2pdf
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from cli import (
    compress_with_ghostscript,
    extract_images,
    ghostscript_available,
    merge_with_qpdf,
    ocr_pdf,
    ocrmypdf_available,
    pdf_to_images,
    pdf_to_pdfa,
    protect_with_qpdf,
    qpdf_available,
    repair_with_qpdf,
    split_with_qpdf,
    unlock_with_qpdf,
)
from storage import Job, JobStore


def _sorted_inputs(store: JobStore, job: Job) -> list[Path]:
    input_dir = store.input_dir(job.id)
    order = job.options.get("fileOrder")
    files = [p for p in input_dir.iterdir() if p.is_file()]
    if order:
        name_map = {p.name: p for p in files}
        return [name_map[name] for name in order if name in name_map]
    return sorted(files, key=lambda p: p.name)


def _write_pypdf(writer: PdfWriter, output: Path) -> None:
    with open(output, "wb") as f:
        writer.write(f)


def parse_page_numbers(spec: Any) -> set[int]:
    """Parse page numbers from a list or comma-separated string (supports ranges like 2-4)."""
    if spec is None:
        return set()
    if isinstance(spec, (int, float)):
        return {int(spec)}

    parts: list[str]
    if isinstance(spec, str):
        parts = spec.split(",")
    elif isinstance(spec, list):
        parts = [str(p) for p in spec]
    else:
        return set()

    pages: set[int] = set()
    for part in parts:
        token = part.strip()
        if not token:
            continue
        if "-" in token:
            start_s, end_s = token.split("-", 1)
            start, end = int(start_s.strip()), int(end_s.strip())
            if start > end:
                start, end = end, start
            pages.update(range(start, end + 1))
        else:
            pages.add(int(token))
    return pages


def merge_pdf(store: JobStore, job: Job) -> Path:
    inputs = _sorted_inputs(store, job)
    if not inputs:
        raise ValueError("No input PDF files found for merge")
    output = store.output_dir(job.id) / "merged.pdf"
    if qpdf_available() and len(inputs) > 1:
        merge_with_qpdf(inputs, output)
        return output
    writer = PdfWriter()
    for path in inputs:
        reader = PdfReader(str(path))
        for page in reader.pages:
            writer.add_page(page)
    _write_pypdf(writer, output)
    return output


def split_pdf(store: JobStore, job: Job) -> Path:
    inputs = _sorted_inputs(store, job)
    if not inputs:
        raise ValueError("No input file")
    input_path = inputs[0]
    mode = job.options.get("mode", "ranges")
    output_dir = store.output_dir(job.id)

    if mode == "every_n":
        n = int(job.options.get("everyN", 1))
        reader = PdfReader(str(input_path))
        zip_path = output_dir / "split_pages.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for start in range(0, len(reader.pages), n):
                writer = PdfWriter()
                for page in reader.pages[start : start + n]:
                    writer.add_page(page)
                buf = io.BytesIO()
                writer.write(buf)
                part = start // n + 1
                zf.writestr(f"part_{part}.pdf", buf.getvalue())
        return zip_path

    ranges = job.options.get("ranges", "1")
    output = output_dir / "split.pdf"
    if qpdf_available():
        split_with_qpdf(input_path, output, ranges)
        return output

    reader = PdfReader(str(input_path))
    writer = PdfWriter()
    for spec in ranges.split(","):
        spec = spec.strip()
        if "-" in spec:
            start, end = spec.split("-", 1)
            start_i, end_i = int(start), int(end)
            for i in range(start_i - 1, end_i):
                if 0 <= i < len(reader.pages):
                    writer.add_page(reader.pages[i])
        else:
            i = int(spec) - 1
            if 0 <= i < len(reader.pages):
                writer.add_page(reader.pages[i])
    _write_pypdf(writer, output)
    return output


def compress_pdf(store: JobStore, job: Job) -> Path:
    inputs = _sorted_inputs(store, job)
    input_path = inputs[0]
    output = store.output_dir(job.id) / "compressed.pdf"
    quality = job.options.get("quality", "ebook")
    if ghostscript_available():
        compress_with_ghostscript(input_path, output, quality)
        return output
    # pypdf fallback: pages must be added to writer before compress_content_streams()
    reader = PdfReader(str(input_path))
    writer = PdfWriter()
    writer.append(reader)
    for page in writer.pages:
        page.compress_content_streams()
    if hasattr(writer, "compress_identical_objects"):
        writer.compress_identical_objects()
    _write_pypdf(writer, output)
    return output


def rotate_pdf(store: JobStore, job: Job) -> Path:
    inputs = _sorted_inputs(store, job)
    input_path = inputs[0]
    angle = int(job.options.get("angle", 90))
    output = store.output_dir(job.id) / "rotated.pdf"
    reader = PdfReader(str(input_path))
    writer = PdfWriter()
    for page in reader.pages:
        page.rotate(angle)
        writer.add_page(page)
    _write_pypdf(writer, output)
    return output


def organize_pdf(store: JobStore, job: Job) -> Path:
    inputs = _sorted_inputs(store, job)
    input_path = inputs[0]
    order = job.options.get("pageOrder", [])
    output = store.output_dir(job.id) / "organized.pdf"
    reader = PdfReader(str(input_path))
    writer = PdfWriter()
    if not order:
        order = list(range(1, len(reader.pages) + 1))
    for page_num in order:
        idx = int(page_num) - 1
        if 0 <= idx < len(reader.pages):
            writer.add_page(reader.pages[idx])
    _write_pypdf(writer, output)
    return output


def remove_pages(store: JobStore, job: Job) -> Path:
    inputs = _sorted_inputs(store, job)
    input_path = inputs[0]
    remove = parse_page_numbers(job.options.get("removePages", []))
    output = store.output_dir(job.id) / "removed.pdf"
    reader = PdfReader(str(input_path))
    writer = PdfWriter()
    for i, page in enumerate(reader.pages, start=1):
        if i not in remove:
            writer.add_page(page)
    _write_pypdf(writer, output)
    return output


def protect_pdf(store: JobStore, job: Job) -> Path:
    inputs = _sorted_inputs(store, job)
    input_path = inputs[0]
    password = job.options.get("password", "")
    if not password:
        raise ValueError("Password is required")
    output = store.output_dir(job.id) / "protected.pdf"
    if qpdf_available():
        protect_with_qpdf(input_path, output, password)
        return output
    reader = PdfReader(str(input_path))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(password)
    _write_pypdf(writer, output)
    return output


def unlock_pdf(store: JobStore, job: Job) -> Path:
    inputs = _sorted_inputs(store, job)
    input_path = inputs[0]
    password = job.options.get("password", "")
    output = store.output_dir(job.id) / "unlocked.pdf"
    if qpdf_available():
        unlock_with_qpdf(input_path, output, password)
        return output
    reader = PdfReader(str(input_path))
    if reader.is_encrypted:
        reader.decrypt(password)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    _write_pypdf(writer, output)
    return output


def watermark_pdf(store: JobStore, job: Job) -> Path:
    inputs = _sorted_inputs(store, job)
    input_path = inputs[0]
    text = job.options.get("text", "CONFIDENTIAL")
    output = store.output_dir(job.id) / "watermarked.pdf"

    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    c.setFont("Helvetica", 40)
    c.setFillAlpha(0.2)
    c.saveState()
    c.translate(300, 400)
    c.rotate(45)
    c.drawCentredString(0, 0, text)
    c.restoreState()
    c.save()
    packet.seek(0)
    watermark = PdfReader(packet)
    watermark_page = watermark.pages[0]

    reader = PdfReader(str(input_path))
    writer = PdfWriter()
    for page in reader.pages:
        page.merge_page(watermark_page)
        writer.add_page(page)
    _write_pypdf(writer, output)
    return output


def page_numbers_pdf(store: JobStore, job: Job) -> Path:
    inputs = _sorted_inputs(store, job)
    input_path = inputs[0]
    position = job.options.get("position", "bottom-center")
    output = store.output_dir(job.id) / "numbered.pdf"
    reader = PdfReader(str(input_path))
    writer = PdfWriter()
    total = len(reader.pages)

    for i, page in enumerate(reader.pages, start=1):
        packet = io.BytesIO()
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        c = canvas.Canvas(packet, pagesize=(width, height))
        c.setFont("Helvetica", 10)
        label = f"{i} / {total}"
        if position == "bottom-center":
            c.drawCentredString(width / 2, 20, label)
        elif position == "bottom-right":
            c.drawRightString(width - 20, 20, label)
        else:
            c.drawString(20, 20, label)
        c.save()
        packet.seek(0)
        overlay = PdfReader(packet).pages[0]
        page.merge_page(overlay)
        writer.add_page(page)

    _write_pypdf(writer, output)
    return output


def pdf_to_jpg(store: JobStore, job: Job) -> Path:
    inputs = _sorted_inputs(store, job)
    input_path = inputs[0]
    fmt = job.options.get("format", "jpeg")
    output_dir = store.output_dir(job.id) / "images"
    images = pdf_to_images(input_path, output_dir, fmt)
    zip_path = store.output_dir(job.id) / "images.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for img in images:
            zf.write(img, img.name)
    return zip_path


def images_to_pdf(store: JobStore, job: Job) -> Path:
    inputs = _sorted_inputs(store, job)
    output = store.output_dir(job.id) / "images.pdf"
    paths = [str(p) for p in inputs if p.suffix.lower() in {".jpg", ".jpeg", ".png"}]
    with open(output, "wb") as f:
        f.write(img2pdf.convert(paths))
    return output


def extract_images_pdf(store: JobStore, job: Job) -> Path:
    inputs = _sorted_inputs(store, job)
    input_path = inputs[0]
    output_dir = store.output_dir(job.id) / "extracted"
    images = extract_images(input_path, output_dir)
    zip_path = store.output_dir(job.id) / "extracted_images.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for img in images:
            zf.write(img, img.name)
    return zip_path


def pdf_to_word(store: JobStore, job: Job) -> Path:
    from pdf2docx import Converter

    inputs = _sorted_inputs(store, job)
    input_path = inputs[0]
    output = store.output_dir(job.id) / "converted.docx"
    cv = Converter(str(input_path))
    cv.convert(str(output))
    cv.close()
    return output


def ocr_pdf_tool(store: JobStore, job: Job) -> Path:
    inputs = _sorted_inputs(store, job)
    input_path = inputs[0]
    output = store.output_dir(job.id) / "ocr.pdf"
    if not ocrmypdf_available():
        raise RuntimeError(
            "ocrmypdf is not installed. Run: pip install ocrmypdf "
            "(also requires Tesseract OCR on your system)"
        )
    try:
        ocr_pdf(input_path, output)
    except RuntimeError as exc:
        msg = str(exc)
        if "tesseract" in msg.lower() or "winerror 2" in msg.lower():
            raise RuntimeError(
                "Tesseract OCR is not installed or not on PATH. "
                "Install Tesseract (https://github.com/UB-Mannheim/tesseract/wiki on Windows), "
                "then retry."
            ) from exc
        raise
    return output


def repair_pdf(store: JobStore, job: Job) -> Path:
    inputs = _sorted_inputs(store, job)
    input_path = inputs[0]
    output = store.output_dir(job.id) / "repaired.pdf"
    if qpdf_available():
        repair_with_qpdf(input_path, output)
        return output
    reader = PdfReader(str(input_path))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    _write_pypdf(writer, output)
    return output


def pdf_to_pdfa_tool(store: JobStore, job: Job) -> Path:
    inputs = _sorted_inputs(store, job)
    input_path = inputs[0]
    output = store.output_dir(job.id) / "pdfa.pdf"
    pdf_to_pdfa(input_path, output)
    return output


def compare_pdf(store: JobStore, job: Job) -> Path:
    inputs = _sorted_inputs(store, job)
    if len(inputs) < 2:
        raise ValueError("Two PDF files required")
    output_dir = store.output_dir(job.id) / "compare"
    imgs_a = pdf_to_images(inputs[0], output_dir / "a", "png")
    imgs_b = pdf_to_images(inputs[1], output_dir / "b", "png")
    report = {
        "fileA": inputs[0].name,
        "fileB": inputs[1].name,
        "pagesA": len(imgs_a),
        "pagesB": len(imgs_b),
        "match": imgs_a[0].stat().st_size == imgs_b[0].stat().st_size if imgs_a and imgs_b else False,
    }
    report_path = store.output_dir(job.id) / "compare_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report_path


def redact_pdf(store: JobStore, job: Job) -> Path:
    import fitz

    inputs = _sorted_inputs(store, job)
    input_path = inputs[0]
    boxes = job.options.get("boxes", [])
    if not boxes:
        raise ValueError("At least one redaction box is required")
    output = store.output_dir(job.id) / "redacted.pdf"
    doc = fitz.open(str(input_path))
    try:
        by_page: dict[int, list[dict[str, Any]]] = {}
        for box in boxes:
            page_num = int(box.get("page", 1)) - 1
            by_page.setdefault(page_num, []).append(box)
        for page_num, page_boxes in by_page.items():
            if page_num < 0 or page_num >= len(doc):
                continue
            page = doc[page_num]
            for box in page_boxes:
                rect = fitz.Rect(
                    float(box["x"]),
                    float(box["y"]),
                    float(box["x"]) + float(box["width"]),
                    float(box["y"]) + float(box["height"]),
                )
                page.add_redact_annot(rect, fill=(0, 0, 0))
            page.apply_redactions()
        doc.save(str(output), garbage=4)
    finally:
        doc.close()
    return output


def crop_pdf(store: JobStore, job: Job) -> Path:
    inputs = _sorted_inputs(store, job)
    input_path = inputs[0]
    margin = float(job.options.get("margin", 0))
    output = store.output_dir(job.id) / "cropped.pdf"
    reader = PdfReader(str(input_path))
    writer = PdfWriter()
    for page in reader.pages:
        page.mediabox.lower_left = (margin, margin)
        page.mediabox.upper_right = (
            float(page.mediabox.right) - margin,
            float(page.mediabox.top) - margin,
        )
        writer.add_page(page)
    _write_pypdf(writer, output)
    return output


def sign_pdf(store: JobStore, job: Job) -> Path:
    inputs = _sorted_inputs(store, job)
    pdf_inputs = [p for p in inputs if p.suffix.lower() == ".pdf"]
    if not pdf_inputs:
        raise ValueError("PDF file required")
    input_path = pdf_inputs[0]

    sig_path: Path | None = None
    for p in inputs:
        if p.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            sig_path = p
            break
    if not sig_path:
        sig_name = job.options.get("signatureFile")
        if sig_name:
            candidate = store.input_dir(job.id) / sig_name
            if candidate.exists():
                sig_path = candidate
    if not sig_path or not sig_path.exists():
        raise ValueError("Signature image required")

    output = store.output_dir(job.id) / "signed.pdf"
    x = float(job.options.get("x", 50))
    y = float(job.options.get("y", 50))

    sig_reader = PdfReader(str(sig_path))
    sig_page = sig_reader.pages[0]

    reader = PdfReader(str(input_path))
    writer = PdfWriter()
    for i, page in enumerate(reader.pages):
        if i == 0:
            page.merge_page(sig_page)
        writer.add_page(page)
    _write_pypdf(writer, output)
    return output


def run_workflow(store: JobStore, job: Job) -> Path:
    steps: list[dict[str, Any]] = job.options.get("steps", [])
    if not steps:
        raise ValueError("Workflow steps required")

    initial_inputs = _sorted_inputs(store, job)
    if not initial_inputs:
        raise ValueError("No input files")

    current_file = initial_inputs[0]
    result: Path | None = None

    for index, step in enumerate(steps):
        tool = step.get("tool")
        if tool not in TOOL_HANDLERS or tool == "workflow":
            raise ValueError(f"Invalid workflow step tool: {tool}")

        working_name = f"workflow_step_{index}.pdf"
        working_input = store.input_dir(job.id) / working_name
        working_input.write_bytes(current_file.read_bytes())

        step_job = Job(
            id=job.id,
            tool=tool,
            status=job.status,
            options={**step.get("options", {}), "fileOrder": [working_name]},
            created_at=job.created_at,
            updated_at=job.updated_at,
            input_files=[working_name],
        )
        result = TOOL_HANDLERS[tool](store, step_job)
        current_file = result

    if result is None:
        raise RuntimeError("Workflow produced no output")

    ext = result.suffix or ".pdf"
    final = store.output_dir(job.id) / f"workflow_result{ext}"
    final.write_bytes(result.read_bytes())
    return final


TOOL_HANDLERS = {
    "merge": merge_pdf,
    "split": split_pdf,
    "compress": compress_pdf,
    "rotate": rotate_pdf,
    "organize": organize_pdf,
    "remove-pages": remove_pages,
    "protect": protect_pdf,
    "unlock": unlock_pdf,
    "watermark": watermark_pdf,
    "page-numbers": page_numbers_pdf,
    "pdf-to-jpg": pdf_to_jpg,
    "images-to-pdf": images_to_pdf,
    "extract-images": extract_images_pdf,
    "pdf-to-word": pdf_to_word,
    "ocr": ocr_pdf_tool,
    "repair": repair_pdf,
    "pdf-to-pdfa": pdf_to_pdfa_tool,
    "compare": compare_pdf,
    "redact": redact_pdf,
    "crop": crop_pdf,
    "sign": sign_pdf,
    "workflow": run_workflow,
}


MIME_MAP = {
    ".pdf": "application/pdf",
    ".zip": "application/zip",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".json": "application/json",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
}


def process_job(store: JobStore, job: Job) -> tuple[Path, str]:
    handler = TOOL_HANDLERS.get(job.tool)
    if not handler:
        raise ValueError(f"Unknown tool: {job.tool}")
    result = handler(store, job)
    mime = MIME_MAP.get(result.suffix.lower(), "application/octet-stream")
    return result, mime
