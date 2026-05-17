FROM python:3.12-slim

WORKDIR /app

# Install system deps (curl_cffi needs gcc; curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Non-root user for security; /app/data gets 0755 so the mounted
# volume (owned by any UID) remains accessible.
RUN useradd -m -u 1000 appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
