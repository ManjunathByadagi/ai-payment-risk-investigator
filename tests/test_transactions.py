from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_analyze_transaction_valid():
    payload = {
        "customer_id": "CUST_TEST_01",
        "merchant_id": "MERCH_TEST_01",
        "amount": 150.00,
        "currency": "INR",
        "customer_country": "IN",
        "transaction_country": "IN",
        "device_id": "DEV_TEST_01",
        "device_new": 0,
        "customer_account_age_days": 100,
        "transactions_last_10_minutes": 0,
        "transactions_last_1_hour": 1,
        "transactions_last_24_hours": 2,
        "average_customer_amount": 150.00,
        "merchant_risk_score": 0.02,
        "customer_previous_risk_count": 0,
        "failed_transactions_last_24_hours": 0,
        "ip_risk_score": 0.1,
        "unusual_time": 0
    }
    response = client.post("/api/v1/transactions/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "transaction_id" in data
    assert "risk_probability" in data
    assert "risk_level" in data
    assert "decision" in data
    assert isinstance(data["risk_signals"], list)

def test_analyze_transaction_invalid_amount():
    payload = {
        "customer_id": "CUST_TEST_01",
        "merchant_id": "MERCH_TEST_01",
        "amount": -50.00,  # Invalid negative amount
        "device_id": "DEV_TEST_01"
    }
    response = client.post("/api/v1/transactions/analyze", json=payload)
    assert response.status_code == 422  # Validation Error
