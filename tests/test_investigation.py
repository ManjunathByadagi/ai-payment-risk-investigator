from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_investigation_workflow_deterministic():
    # 1. Analyze high risk transaction
    payload = {
        "customer_id": "CUST_HIGH_INV",
        "merchant_id": "MERCH_HIGH_INV",
        "amount": 25000.00,
        "customer_country": "IN",
        "transaction_country": "US",
        "device_id": "DEV_HIGH_INV",
        "device_new": 1,
        "customer_account_age_days": 10,
        "transactions_last_10_minutes": 5,
        "transactions_last_1_hour": 10,
        "transactions_last_24_hours": 20,
        "average_customer_amount": 500.00,
        "merchant_risk_score": 0.80,
        "customer_previous_risk_count": 3,
        "failed_transactions_last_24_hours": 3,
        "ip_risk_score": 0.90,
        "unusual_time": 1
    }
    res_analyze = client.post("/api/v1/transactions/analyze", json=payload)
    assert res_analyze.status_code == 200
    data_analyze = res_analyze.json()
    txn_id = data_analyze["transaction_id"]

    # 2. Trigger Investigation endpoint
    res_inv = client.post(f"/api/v1/investigations/{txn_id}")
    assert res_inv.status_code == 200
    data_inv = res_inv.json()
    assert data_inv["transaction_id"] == txn_id
    assert "evidence" in data_inv
    assert "investigation_summary" in data_inv
    assert data_inv["recommended_action"] in ["MANUAL_REVIEW", "MONITOR"]

    # 3. Check audit log entries
    res_audit = client.get("/api/v1/audit")
    assert res_audit.status_code == 200
    audit_data = res_audit.json()
    assert len(audit_data) > 0
