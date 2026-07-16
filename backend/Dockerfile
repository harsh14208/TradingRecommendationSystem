# ── Stage 1: Frontend build ───────────────────────────────────────────────────
# Uses Node.js (not present in final image) to compile JSX → dist/*-bundle.js.
# Eliminates Babel standalone (~900 KB) and allows removing 'unsafe-eval' from CSP.
FROM node:20-slim AS frontend-builder
WORKDIR /build

COPY package.json ./
RUN npm install --prefer-offline

# Copy build script and JSX sources (frontend/src was reorganized 2026-06-13).
COPY build.mjs ./
COPY frontend/src ./frontend/src

RUN node build.mjs

# ── Stage 2: Python runtime ───────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Install system deps (curl_cffi needs gcc; curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Inject pre-compiled frontend bundle from build stage.
# dist/ is in .gitignore — it comes from the build stage, not git.
COPY --from=frontend-builder /frontend/dist ./dist

# Non-root user for security; /app/data gets 0755 so the mounted
# volume (owned by any UID) remains accessible.
RUN useradd -m -u 1000 appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
