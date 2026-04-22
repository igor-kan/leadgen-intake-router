# leadgen-intake-router

Lead intake + scoring API for "lead generation / selling leads" workflows.

## What it does
- Ingest leads via JSON or CSV
- Score and prioritize leads
- Export standardized CSV for delivery or CRM import

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8010
```

## API
- `POST /ingest/json`
- `POST /ingest/csv`
- `GET /leads`
- `GET /export/csv`

## Example
```bash
curl -X POST http://127.0.0.1:8010/ingest/json \
  -H "content-type: application/json" \
  -d '[{"name":"Alex","email":"alex@acme.com","company":"Acme","source":"linkedin","budget":2000,"urgency":"high"}]'
```

## Notes
- This starter uses in-memory storage.
- Add persistence (PostgreSQL/Redis) for production.
- Comply with local anti-spam and privacy rules.
