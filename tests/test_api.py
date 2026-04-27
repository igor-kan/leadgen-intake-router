from fastapi.testclient import TestClient

from app.main import LEADS, app


client = TestClient(app)


def setup_function() -> None:
    LEADS.clear()


def test_ingest_json_and_list_sorted() -> None:
    payload = [
        {
            "name": "Low Lead",
            "email": "low@example.com",
            "budget": 200,
            "urgency": "low",
        },
        {
            "name": "High Lead",
            "email": "high@example.com",
            "budget": 8000,
            "urgency": "high",
            "company": "Northpoint",
            "source": "referral",
        },
    ]
    res = client.post("/ingest/json", json=payload)
    assert res.status_code == 200
    assert res.json()["created"] == 2

    leads = client.get("/leads").json()
    assert leads[0]["name"] == "High Lead"
    assert leads[0]["score"] >= leads[1]["score"]


def test_ingest_csv_invalid_budget_returns_400() -> None:
    csv_body = "name,email,budget,urgency\nAlex,alex@example.com,not-a-number,high\n"
    res = client.post(
        "/ingest/csv",
        files={"file": ("leads.csv", csv_body, "text/csv")},
    )
    assert res.status_code == 400
    assert "Invalid integer" in res.json()["detail"]
