from __future__ import annotations

import csv
import io
import logging
from typing import Any, List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, EmailStr, Field

from app.scoring import score_lead

app = FastAPI(title="Leadgen Intake Router")
logger = logging.getLogger("leadgen")


class ErrorResponse(BaseModel):
    detail: str


class Lead(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr | None = None
    company: str | None = None
    source: str | None = None
    notes: str | None = None
    budget: int | None = 0
    urgency: str | None = "medium"


class LeadRecord(BaseModel):
    name: str
    email: EmailStr | None = None
    company: str | None = None
    source: str | None = None
    notes: str | None = None
    budget: int = 0
    urgency: str = "medium"
    score: int = Field(ge=0, le=100)


class HealthResponse(BaseModel):
    ok: bool
    count: int


class IngestResponse(BaseModel):
    created: int
    total: int


LEADS: list[LeadRecord] = []


def _parse_int(raw: Any, field: str, row_num: int) -> int:
    value = str(raw or "").strip()
    if value == "":
        return 0
    try:
        return int(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid integer for `{field}` at row {row_num}: {value!r}",
        ) from exc


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(ok=True, count=len(LEADS))


@app.post("/ingest/json", response_model=IngestResponse, responses={400: {"model": ErrorResponse}})
def ingest_json(leads: List[Lead]) -> IngestResponse:
    logger.info("ingest_json called with %d leads", len(leads))
    created = 0
    for lead in leads:
        row = lead.model_dump()
        row["score"] = score_lead(row)
        LEADS.append(LeadRecord(**row))
        created += 1
    logger.info("ingest_json completed created=%d total=%d", created, len(LEADS))
    return IngestResponse(created=created, total=len(LEADS))


@app.post("/ingest/csv", response_model=IngestResponse, responses={400: {"model": ErrorResponse}})
async def ingest_csv(file: UploadFile = File(...)) -> IngestResponse:
    logger.info("ingest_csv called filename=%s", file.filename)
    try:
        content = await file.read()
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded") from exc
    reader = csv.DictReader(io.StringIO(text))

    created = 0
    for idx, row in enumerate(reader, start=2):
        normalized = {
            "name": row.get("name", "").strip(),
            "email": (row.get("email") or "").strip() or None,
            "company": (row.get("company") or "").strip() or None,
            "source": (row.get("source") or "").strip() or None,
            "notes": (row.get("notes") or "").strip() or None,
            "budget": _parse_int(row.get("budget"), "budget", idx),
            "urgency": (row.get("urgency") or "medium").strip().lower(),
        }
        if not normalized["name"]:
            raise HTTPException(status_code=400, detail=f"Missing required field `name` at row {idx}")
        normalized["score"] = score_lead(normalized)
        LEADS.append(LeadRecord(**normalized))
        created += 1

    logger.info("ingest_csv completed created=%d total=%d", created, len(LEADS))
    return IngestResponse(created=created, total=len(LEADS))


@app.get("/leads", response_model=list[LeadRecord])
def list_leads() -> list[LeadRecord]:
    return sorted(LEADS, key=lambda x: x.score, reverse=True)


@app.get("/export/csv")
def export_csv() -> PlainTextResponse:
    buffer = io.StringIO()
    fieldnames = ["name", "email", "company", "source", "budget", "urgency", "score", "notes"]
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for lead in sorted(LEADS, key=lambda x: x.score, reverse=True):
        writer.writerow({k: getattr(lead, k) for k in fieldnames})

    return PlainTextResponse(buffer.getvalue(), media_type="text/csv")
