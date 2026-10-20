import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

BASE_INPUT = {
    "initial_principal": 1000,
    "monthly_contribution": 100,
    "annual_rate": 0.05,
    "years": 2,
}


@pytest.mark.parametrize(
    "changes, contributions, interest, balance",
    [
        (
            {"annual_rate": 0},
            "3400.00",
            "0.00",
            "3400.00",
        ),
        (
            {"monthly_contribution": 0},
            "1000.00",
            "102.50",
            "1102.50",
        ),
        (
            {"annual_rate": 1.01**12 - 1, "years": 1},
            "2200.00",
            "195.08",
            "2395.08",
        ),
    ],
)
def test_simulation(changes, contributions, interest, balance):
    payload = BASE_INPUT | changes
    response = client.post("/api/simulate", json=payload)

    assert response.status_code == 200
    result = response.json()

    assert result["currency"] == "CAD"
    assert result["total_contributions"] == contributions
    assert result["interest"] == interest
    assert result["final_balance"] == balance

    annual = result["annual_progression"]
    assert [row["year"] for row in annual] == list(range(1, payload["years"] + 1))
    assert annual[-1]["final_balance"] == balance


@pytest.mark.parametrize(
    "changes",
    [
        {"initial_principal": -1},
        {"initial_principal": 10_000_001},
        {"initial_principal": "1000"},
        {"initial_principal": True},
        {"monthly_contribution": -1},
        {"monthly_contribution": 100_001},
        {"annual_rate": -0.01},
        {"annual_rate": 1.01},
        {"years": 0},
        {"years": 61},
        {"years": 1.5},
        {"years": True},
        {"unexpected_field": 123},
    ],
)
def test_invalid_input(changes):
    response = client.post("/api/simulate", json=BASE_INPUT | changes)
    assert response.status_code == 422


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity"])
def test_non_finite_input(value):
    body = (
        '{"initial_principal":'
        + value
        + ',"monthly_contribution":100,"annual_rate":0.05,"years":2}'
    )
    response = client.post(
        "/api/simulate",
        content=body,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422
    assert "detail" in response.json()


def test_missing_fields():
    response = client.post("/api/simulate", json={})
    assert response.status_code == 422


def test_malformed_json():
    response = client.post(
        "/api/simulate",
        content="{",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
