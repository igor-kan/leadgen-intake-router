# Deployment

## Production baseline
- Runtime: Python 3.11+
- ASGI server: `uvicorn` behind `gunicorn` or process manager
- Reverse proxy: Nginx/Caddy with TLS
- Env: `PYTHONUNBUFFERED=1`

## Start command
```bash
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 2 -b 0.0.0.0:8010
```

## Health checks
- Liveness: `GET /health`
- Readiness: `GET /health`

## Operational notes
- Move in-memory `LEADS` storage to PostgreSQL for production.
- Enable centralized logs and request tracing at proxy layer.
- Run CI workflow before deploy.
