from app.scoring import score_lead


def test_score_lead_high_value():
    lead = {
        "name": "Alex",
        "email": "alex@example.com",
        "company": "Acme",
        "source": "linkedin",
        "budget": 8000,
        "urgency": "high",
        "notes": "Needs support",
    }
    assert score_lead(lead) == 100


def test_score_lead_low_value():
    lead = {
        "name": "Sam",
        "budget": 0,
        "urgency": "low",
    }
    assert score_lead(lead) == 10
