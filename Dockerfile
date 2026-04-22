# ── Stage 1: Builder ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install dependencies only (layer-cached separately from code)
COPY requirements.txt .
RUN pip install --upgrade pip && \
  pip install --no-cache-dir -r requirements.txt

# ── Stage 2: Runtime ─��────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code first
COPY app/ ./app/
COPY ui/ ./ui/
COPY train_model.py .
COPY .env.example .env

# Create logs directory
RUN mkdir -p logs

# Generate models during build
RUN python train_model.py

# Expose FastAPI port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run FastAPI with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]