#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import logging
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.scoring import score_lead

logger = logging.getLogger("leadgen.process_csv")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score and rank leads from CSV")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--output", required=True, help="Output CSV path")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    args = parse_args()
    in_path = Path(args.input)
    out_path = Path(args.output)
    if not in_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {in_path}")
    logger.info("Scoring input file: %s", in_path)

    with open(in_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        for idx, row in enumerate(reader, start=2):
            budget_raw = (row.get("budget") or "0").strip() or "0"
            try:
                budget = int(budget_raw)
            except ValueError as exc:
                raise ValueError(f"Invalid budget at row {idx}: {budget_raw!r}") from exc
            normalized = {
                "name": (row.get("name") or "").strip(),
                "email": (row.get("email") or "").strip() or None,
                "company": (row.get("company") or "").strip() or None,
                "source": (row.get("source") or "").strip() or None,
                "notes": (row.get("notes") or "").strip() or None,
                "budget": budget,
                "urgency": (row.get("urgency") or "medium").strip().lower(),
            }
            if not normalized["name"]:
                raise ValueError(f"Missing required field `name` at row {idx}")
            normalized["score"] = score_lead(normalized)
            rows.append(normalized)

    rows.sort(key=lambda x: x.get("score", 0), reverse=True)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["name", "email", "company", "source", "budget", "urgency", "score", "notes"]
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})

    logger.info("Wrote ranked leads: %s", out_path)


if __name__ == "__main__":
    main()
