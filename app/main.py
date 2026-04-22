from __future__ import annotations

import csv
import io
from typing import List

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, EmailStr, Field

from app.scoring import score_lead

app = FastAPI(title="Leadgen Intake Router")


class Lead(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr | None = None
    company: str | None = None
    source: str | None = None
    notes: str | None = None
    budget: int | None = 0
    urgency: str | None = "medium"


LEADS: list[dict] = []


@app.get("/health")
def health() -> dict:
    return {"ok": True, "count": len(LEADS)}


@app.post("/ingest/json")
def ingest_json(leads: List[Lead]) -> dict:
    created = 0
    for lead in leads:
        row = lead.model_dump()
        row["score"] = score_lead(row)
        LEADS.append(row)
        created += 1
    return {"created": created, "total": len(LEADS)}


@app.post("/ingest/csv")
async def ingest_csv(file: UploadFile = File(...)) -> dict:
    content = await file.read()
    text = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))

    created = 0
    for row in reader:
        normalized = {
            "name": row.get("name", "").strip(),
            "email": (row.get("email") or "").strip() or None,
            "company": (row.get("company") or "").strip() or None,
            "source": (row.get("source") or "").strip() or None,
            "notes": (row.get("notes") or "").strip() or None,
            "budget": int((row.get("budget") or "0").strip() or 0),
            "urgency": (row.get("urgency") or "medium").strip().lower(),
        }
        normalized["score"] = score_lead(normalized)
        LEADS.append(normalized)
        created += 1

    return {"created": created, "total": len(LEADS)}


@app.get("/leads")
def list_leads() -> list[dict]:
    return sorted(LEADS, key=lambda x: x.get("score", 0), reverse=True)


@app.get("/export/csv")
def export_csv() -> PlainTextResponse:
    buffer = io.StringIO()
    fieldnames = ["name", "email", "company", "source", "budget", "urgency", "score", "notes"]
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for lead in sorted(LEADS, key=lambda x: x.get("score", 0), reverse=True):
        writer.writerow({k: lead.get(k, "") for k in fieldnames})

    return PlainTextResponse(buffer.getvalue(), media_type="text/csv")
