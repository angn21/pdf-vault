# PDF Vault

Self-hosted, privacy-first PDF toolkit — a local alternative to cloud services like iLovePDF.

**Your files never leave your machine.** Jobs are processed in ephemeral temp storage and auto-deleted after download (or after 10 minutes).

## Features

### Organize
- Merge PDF · Split PDF · Rotate PDF · Organize / reorder pages · Remove pages · Crop PDF · Page numbers

### Optimize
- Compress PDF (Ghostscript quality presets)

### Secure
- Protect PDF (password) · Unlock PDF · Watermark · Sign PDF (image overlay)

### Convert
- PDF to JPG/PNG · Images to PDF · Extract images · PDF to Word

### Advanced
- OCR PDF · Repair PDF · PDF to PDF/A · Compare PDF · Redact PDF

### Automate
- **Workflows** — chain tools in one job (e.g. compress → watermark → protect). Preset recipes live in the UI; see `workflows.example.json` for JSON examples.

## Project structure

```
pdf-vault/
├── web/                    # Next.js 15 UI + API proxy (/api/jobs, /api/capabilities)
│   └── src/
│       ├── app/            # Pages (home, /tools/[toolId], /workflows)
│       ├── components/     # ToolCard, ToolWizard, PrivacyBadge
│       └── lib/            # Tool definitions (tools.ts), API client (api.ts)
├── pdf-worker/             # FastAPI worker — job queue, PDF processing
│   ├── main.py             # REST API (/jobs, /tools, /health, /capabilities)
│   ├── tools.py            # Tool handlers
│   ├── storage.py          # Ephemeral job storage + TTL sweeper
│   ├── cli.py              # qpdf / Ghostscript / Poppler wrappers + fallbacks
│   └── test_tools.py       # Integration smoke tests (pure Python, no CLIs)
├── data/jobs/              # Local job files (gitignored; .gitkeep only in repo)
├── docker-compose.yml      # web + pdf-worker services
├── start-dev.bat           # Windows one-command local start
├── start-dev.sh            # macOS / Linux one-command local start
├── workflows.example.json  # Example workflow step chains
├── .env.example            # Optional env vars for Docker or manual runs
├── CONTRIBUTING.md
├── THIRD_PARTY_NOTICES.md
└── LICENSE
```

## Requirements

**Docker is optional.** Pick one way to run PDF Vault:

| Method | You need |
|--------|----------|
| **Docker** (easiest all-in-one) | [Docker Desktop](https://www.docker.com/products/docker-desktop/) |
| **Local dev** (no Docker) | Python **3.9–3.12** (3.14+ is not supported yet) and [Node.js 18+](https://nodejs.org/) |

Most tools work out of the box with `pip install`. Optional system tools improve compress, OCR, and repair — see [Optional tools](#optional-system-tools) below.

## Quick start (Docker)

```bash
git clone https://github.com/angn21/pdf-vault.git
cd pdf-vault
cp .env.example .env   # optional — docker-compose.yml sets defaults
docker compose up --build
```

Open **http://localhost:3000**

The `pdf-worker` image bundles qpdf, Ghostscript, Poppler, Tesseract, and OCRmyPDF so compress, OCR, and repair work without extra setup.

## Local development (without Docker)

### First-time setup

Install web dependencies once:

```bash
cd web
npm install
cd ..
```

The start scripts create a Python venv in `pdf-worker/` and install `requirements.txt` automatically on first run.

### One-command start

**Windows** — double-click or run from the project root:

```bat
start-dev.bat
```

**macOS / Linux** — from the project root:

```bash
chmod +x start-dev.sh   # first time only
./start-dev.sh
```

On macOS this opens two Terminal windows (worker + web). On Linux, or if you prefer a single terminal, run:

```bash
PDF_VAULT_NO_TERMINAL=1 ./start-dev.sh
```

Open **http://localhost:3000**

### Manual setup

Use two terminals if you prefer to start services yourself.

#### Terminal 1 — PDF worker (Python)

**macOS / Linux:**

```bash
git clone https://github.com/angn21/pdf-vault.git
cd pdf-vault/pdf-worker

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export DATA_DIR="$(cd .. && pwd)/data/jobs"
mkdir -p "$DATA_DIR"

python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

**Windows (PowerShell):**

```powershell
cd pdf-worker
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

$env:DATA_DIR = "..\data\jobs"
New-Item -ItemType Directory -Force -Path $env:DATA_DIR

python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

#### Terminal 2 — Web UI (Next.js)

```bash
cd web
npm install
npm run dev
```

Open **http://localhost:3000**

The web app talks to the worker at `http://localhost:8000` by default (`PDF_WORKER_URL` in `.env.example` overrides this).

### Optional system tools

Not required for basic use. Pure-Python fallbacks cover PDF→image and light compression when these are missing.

| Tool | Used for | macOS (Homebrew) | Windows |
|------|----------|------------------|---------|
| [Ghostscript](https://www.ghostscript.com/) | Strong compress | `brew install ghostscript` | [Installer](https://ghostscript.com/releases/gsdnld.html) |
| [qpdf](https://github.com/qpdf/qpdf) | Merge/repair/protect | `brew install qpdf` | [Releases](https://github.com/qpdf/qpdf/releases) |
| [Poppler](https://poppler.freedesktop.org/) | PDF→image (faster) | `brew install poppler` | [Releases](https://github.com/oschwartz10612/poppler-windows/releases) |
| [Tesseract](https://github.com/tesseract-ocr/tesseract) | OCR (with `ocrmypdf` from pip) | `brew install tesseract` | [UB Mannheim builds](https://github.com/UB-Mannheim/tesseract/wiki) |

`ocrmypdf` is installed via `pip install -r requirements.txt` but still needs Tesseract on your PATH for OCR jobs.

The UI calls `/api/capabilities` to show which optional tools are available on the worker.

### Running tests

From `pdf-worker/` with the venv activated:

```bash
python test_tools.py
```

## Architecture

```
Browser → Next.js (web, port 3000) → FastAPI (pdf-worker, port 8000) → qpdf / Ghostscript / Poppler / pypdf / …
```

- **Ephemeral jobs:** each upload gets a UUID folder under `DATA_DIR` (default `./data/jobs`)
- **Auto-purge:** files deleted after download + TTL sweeper (`JOB_TTL_SECONDS`, default 600)
- **No telemetry, no cloud storage, no third-party APIs**

## API

Worker endpoints (proxied by Next.js under `/api/…`):

| Endpoint | Description |
|---|---|
| `GET /health` | Worker liveness check |
| `GET /capabilities` | Which optional CLIs are installed (ghostscript, qpdf, poppler, ocrmypdf) |
| `GET /tools` | Tool catalog (id, name, category, accepted file types) |
| `POST /jobs` | Create job (`tool`, `options`, `files`) |
| `GET /jobs/:id` | Job status |
| `GET /jobs/:id/download` | Download result (triggers purge) |
| `DELETE /jobs/:id` | Manual purge |

The Next.js app proxies jobs at `/api/jobs` and capabilities at `/api/capabilities`.

## Privacy

PDF Vault is designed for people who don't want contracts, tax forms, or medical records uploaded to random websites. Everything runs on infrastructure you control.

## License

AGPL-3.0 — see [LICENSE](LICENSE). Bundled system tools have their own licenses — see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
