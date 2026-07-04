"""CLI wrappers with pypdf fallbacks."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def has_command(name: str) -> bool:
    return shutil.which(name) is not None


def run_command(args: list[str], timeout: int = 300) -> None:
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip() or "Command failed"
        raise RuntimeError(stderr)


def qpdf_available() -> bool:
    return has_command("qpdf")


def ghostscript_available() -> bool:
    return get_ghostscript_command() is not None


def get_ghostscript_command() -> str | None:
    for cmd in ("gswin64c", "gswin32c", "gs"):
        if has_command(cmd):
            return cmd
    return None


def poppler_available() -> bool:
    return has_command("pdftoppm")


def ocrmypdf_available() -> bool:
    if has_command("ocrmypdf"):
        return True
    import importlib.util

    return importlib.util.find_spec("ocrmypdf") is not None


def _ocrmypdf_argv() -> list[str]:
    if has_command("ocrmypdf"):
        return ["ocrmypdf"]
    return [sys.executable, "-m", "ocrmypdf"]


def merge_with_qpdf(inputs: list[Path], output: Path) -> None:
    args = ["qpdf", "--empty", "--pages", *[str(p) for p in inputs], "--", str(output)]
    run_command(args)


def split_with_qpdf(input_path: Path, output: Path, pages: str) -> None:
    run_command(["qpdf", str(input_path), "--pages", ".", pages, "--", str(output)])


def compress_with_ghostscript(input_path: Path, output: Path, quality: str) -> None:
    gs = get_ghostscript_command()
    if not gs:
        raise RuntimeError("Ghostscript is not installed")
    settings = {
        "screen": "/screen",
        "ebook": "/ebook",
        "printer": "/printer",
        "prepress": "/prepress",
    }
    pdf_setting = settings.get(quality, "/ebook")
    run_command(
        [
            gs,
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS={pdf_setting}",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={output}",
            str(input_path),
        ]
    )


def protect_with_qpdf(input_path: Path, output: Path, password: str) -> None:
    run_command(
        [
            "qpdf",
            "--encrypt",
            password,
            password,
            "256",
            "--",
            str(input_path),
            str(output),
        ]
    )


def unlock_with_qpdf(input_path: Path, output: Path, password: str) -> None:
    run_command(
        [
            "qpdf",
            f"--password={password}",
            "--decrypt",
            str(input_path),
            str(output),
        ]
    )


def repair_with_qpdf(input_path: Path, output: Path) -> None:
    run_command(["qpdf", str(input_path), str(output)])


def pdf_to_images_poppler(input_path: Path, output_dir: Path, fmt: str = "jpeg") -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    prefix = output_dir / "page"
    ext = "jpg" if fmt == "jpeg" else fmt
    run_command(["pdftoppm", f"-{fmt}", str(input_path), str(prefix)])
    return sorted(output_dir.glob(f"page-*.{ext}"))


def pdf_to_images_pypdfium(input_path: Path, output_dir: Path, fmt: str = "jpeg") -> list[Path]:
    import pypdfium2 as pdfium

    output_dir.mkdir(parents=True, exist_ok=True)
    ext = "jpg" if fmt == "jpeg" else fmt
    pdf = pdfium.PdfDocument(str(input_path))
    paths: list[Path] = []
    try:
        for index in range(len(pdf)):
            page = pdf[index]
            bitmap = page.render(scale=2)
            image = bitmap.to_pil()
            path = output_dir / f"page-{index + 1:03d}.{ext}"
            if fmt == "jpeg":
                image.convert("RGB").save(path, "JPEG", quality=85)
            else:
                image.save(path, "PNG")
            paths.append(path)
    finally:
        pdf.close()
    return paths


def pdf_to_images(input_path: Path, output_dir: Path, fmt: str = "jpeg") -> list[Path]:
    if poppler_available():
        return pdf_to_images_poppler(input_path, output_dir, fmt)
    return pdf_to_images_pypdfium(input_path, output_dir, fmt)


def extract_images_poppler(input_path: Path, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    run_command(["pdfimages", "-all", str(input_path), str(output_dir / "img")])
    return sorted(output_dir.glob("img*"))


def extract_images_pypdf(input_path: Path, output_dir: Path) -> list[Path]:
    from pypdf import PdfReader

    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    reader = PdfReader(str(input_path))
    for page_num, page in enumerate(reader.pages, start=1):
        for img_idx, image in enumerate(page.images):
            name = image.name or f"img_{page_num}_{img_idx}"
            suffix = Path(name).suffix or ".png"
            path = output_dir / f"page{page_num}_{img_idx}{suffix}"
            path.write_bytes(image.data)
            paths.append(path)
    if not paths:
        raise RuntimeError("No embedded images found in this PDF")
    return paths


def extract_images(input_path: Path, output_dir: Path) -> list[Path]:
    if has_command("pdfimages"):
        return extract_images_poppler(input_path, output_dir)
    return extract_images_pypdf(input_path, output_dir)


def ocr_pdf(input_path: Path, output: Path) -> None:
    run_command([*_ocrmypdf_argv(), str(input_path), str(output)])


def pdf_to_pdfa(input_path: Path, output: Path) -> None:
    if ocrmypdf_available():
        run_command(
            [*_ocrmypdf_argv(), "--output-type", "pdfa", str(input_path), str(output)]
        )
    else:
        compress_with_ghostscript(input_path, output, "prepress")
