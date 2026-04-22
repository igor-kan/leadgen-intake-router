#!/usr/bin/env bash
set -euo pipefail

curl -s -X POST http://127.0.0.1:8010/ingest/json \
  -H "content-type: application/json" \
  -d '[{"name":"Demo Lead","email":"demo@example.com","company":"DemoCo","source":"manual","budget":1500,"urgency":"high"}]'

echo
curl -s http://127.0.0.1:8010/leads
