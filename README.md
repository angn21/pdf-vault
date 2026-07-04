# PDF Vault

Self-hosted, privacy-first PDF toolkit — a local alternative to cloud services like iLovePDF.

**Your files never leave your machine.** Jobs are processed in ephemeral temp storage and auto-deleted after download (or after 10 minutes).

## Features

### Organize
- Merge PDF · Split PDF · Rotate PDF · Organize / reorder pages · Remove pages · Crop PDF

### Optimize
- Compress PDF (Ghostscript quality presets)

### Secure
- Protect PDF (password) · Unlock PDF · Watermark · Sign PDF (image overlay)

### Convert
- PDF to JPG/PNG · Images to PDF · Extract images · PDF to Word

### Advanced
- OCR PDF · Repair PDF · PDF to PDF/A · Compare PDF · Redact PDF

### Automate
- **Workflows** — chain tools in one job (e.g. compress → watermark → protect)

## Quick start (Docker)

**Requirements:** [Docker Desktop](https://www.docker.com/products/docker-desktop/)

```bash
git clone https://github.com/yourusername/pdf-vault.git
cd pdf-vault
cp .env.example .env
docker compose up --build
```

Open **http://localhost:3000**

## Local development (without Docker)

From the project root on Windows, run **`start-dev.bat`** to launch the worker and web UI in separate terminals.

Or manually:

### PDF Worker (Python)

```bash
cd pdf-worker
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
set DATA_DIR=..\data\jobs     # Windows
uvicorn main:app --host 127.0.0.1 --port 8000
```

> Optional system tools for best results: [Ghostscript](https://www.ghostscript.com/) (compress), [qpdf](https://github.com/qpdf/qpdf), [Poppler](https://poppler.freedesktop.org/), [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) (OCR). Pure-Python fallbacks cover PDF→image and basic compress when these are missing.

### Web UI (Next.js)

```bash
cd web
npm install
npm run dev
```

Open **http://localhost:3000**

## Architecture

```
Browser → Next.js (web) → FastAPI (pdf-worker) → qpdf / Ghostscript / Poppler / …
```

- **Ephemeral jobs:** each upload gets a UUID folder under `DATA_DIR`
- **Auto-purge:** files deleted after download + 10-minute TTL sweeper
- **No telemetry, no cloud storage, no third-party APIs**

## API

| Endpoint | Description |
|---|---|
| `POST /jobs` | Create job (`tool`, `options`, `files`) |
| `GET /jobs/:id` | Job status |
| `GET /jobs/:id/download` | Download result (triggers purge) |
| `DELETE /jobs/:id` | Manual purge |

The Next.js app proxies these at `/api/jobs`.

## Privacy

PDF Vault is designed for people who don't want contracts, tax forms, or medical records uploaded to random websites. Everything runs on infrastructure you control.

## License

AGPL-3.0 — see [LICENSE](LICENSE). Bundled system tools have their own licenses — see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
