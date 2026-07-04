# Contributing to PDF Vault

Thanks for helping improve PDF Vault!

## Development setup

1. Fork and clone the repo
2. Copy `.env.example` to `.env`
3. Start the PDF worker: `cd pdf-worker && pip install -r requirements.txt && uvicorn main:app --reload`
4. Start the web UI: `cd web && npm install && npm run dev`

## Pull requests

- Keep changes focused — one feature or fix per PR
- Test affected PDF tools manually before submitting
- Do not commit real PDFs with personal data — use generated test files only
- Update README if you add tools or change setup steps

## Adding a new tool

1. Implement handler in `pdf-worker/tools.py` and register in `TOOL_HANDLERS`
2. Add tool metadata in `pdf-worker/main.py` `/tools` endpoint
3. Add UI definition in `web/src/lib/tools.ts`
4. Document in README feature list

## Code style

- Python: follow existing patterns in `pdf-worker/`
- TypeScript: strict mode, functional React components where possible

## Security

If you find a security issue, please do not open a public issue. Describe the problem privately to the maintainer.
