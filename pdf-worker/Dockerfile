FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    qpdf \
    ghostscript \
    poppler-utils \
    ocrmypdf \
    tesseract-ocr \
    tesseract-ocr-eng \
    img2pdf \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /data/jobs

ENV DATA_DIR=/data/jobs
ENV JOB_TTL_SECONDS=600

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
