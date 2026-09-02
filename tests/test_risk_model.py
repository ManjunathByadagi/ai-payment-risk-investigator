import pytest
from unittest.mock import MagicMock
from ml.predict import RiskPredictor

def test_risk_predictor_low_risk():
    predictor = RiskPredictor()
    txn = {
        "customer_id": "CUST_99",
        "merchant_id": "MERCH_99",
        "amount": 100.0,
        "customer_country": "IN",
        "transaction_country": "IN",
        "device_id": "DEV_99",
        "device_new": 0,
        "customer_account_age_days": 500,
        "transactions_last_10_minutes": 0,
        "transactions_last_1_hour": 0,
        "transactions_last_24_hours": 1,
        "average_customer_amount": 100.0,
        "merchant_risk_score": 0.01,
        "customer_previous_risk_count": 0,
        "failed_transactions_last_24_hours": 0,
        "ip_risk_score": 0.05,
        "unusual_time": 0
    }
    result = predictor.predict(txn)
    assert result["risk_probability"] < 0.50
    assert result["risk_level"] in ["LOW", "MEDIUM"]

def test_risk_predictor_high_risk():
    predictor = RiskPredictor()
    txn = {
        "customer_id": "CUST_99",
        "merchant_id": "MERCH_99",
        "amount": 50000.0,
        "customer_country": "IN",
        "transaction_country": "XX",
        "device_id": "DEV_NEW",
        "device_new": 1,
        "customer_account_age_days": 2,
        "transactions_last_10_minutes": 6,
        "transactions_last_1_hour": 15,
        "transactions_last_24_hours": 30,
        "average_customer_amount": 100.0,
        "merchant_risk_score": 0.90,
        "customer_previous_risk_count": 5,
        "failed_transactions_last_24_hours": 4,
        "ip_risk_score": 0.95,
        "unusual_time": 1
    }
    result = predictor.predict(txn)
    assert result["risk_probability"] >= 0.70
    assert result["risk_level"] == "HIGH"
    assert result["decision"] == "MANUAL_REVIEW"

def test_risk_threshold_boundaries():
    predictor = RiskPredictor()
    txn = {
        "customer_id": "CUST_BOUND",
        "merchant_id": "MERCH_BOUND",
        "amount": 150.0,
        "device_id": "DEV_BOUND"
    }

    # Mock model probability outputs for boundary testing
    # The trained model uses classes [0, 1], so the second value is risk probability.
    predictor.model.predict_proba = MagicMock(return_value=[[0.7001, 0.2999]])
    res_low = predictor.predict(txn, low_threshold=0.30, high_threshold=0.70)
    assert res_low["risk_level"] == "LOW"
    assert res_low["decision"] == "APPROVE"

    predictor.model.predict_proba = MagicMock(return_value=[[0.7000, 0.3000]])
    res_med_exact_lower = predictor.predict(txn, low_threshold=0.30, high_threshold=0.70)
    assert res_med_exact_lower["risk_level"] == "MEDIUM"

    predictor.model.predict_proba = MagicMock(return_value=[[0.6999, 0.3001]])
    res_med_lower_above = predictor.predict(txn, low_threshold=0.30, high_threshold=0.70)
    assert res_med_lower_above["risk_level"] == "MEDIUM"

    predictor.model.predict_proba = MagicMock(return_value=[[0.70, 0.30]])
    res_med_lower = predictor.predict(txn, low_threshold=0.30, high_threshold=0.70)
    assert res_med_lower["risk_level"] == "MEDIUM"
    assert res_med_lower["decision"] == "MONITOR"

    predictor.model.predict_proba = MagicMock(return_value=[[0.3001, 0.6999]])
    res_med_upper = predictor.predict(txn, low_threshold=0.30, high_threshold=0.70)
    assert res_med_upper["risk_level"] == "MEDIUM"
    assert res_med_upper["decision"] == "MONITOR"

    predictor.model.predict_proba = MagicMock(return_value=[[0.3001, 0.6999]])
    res_med_exact_upper = predictor.predict(txn, low_threshold=0.30, high_threshold=0.70)
    assert res_med_exact_upper["risk_level"] == "MEDIUM"

    predictor.model.predict_proba = MagicMock(return_value=[[0.30, 0.70]])
    res_high = predictor.predict(txn, low_threshold=0.30, high_threshold=0.70)
    assert res_high["risk_level"] == "HIGH"
    assert res_high["decision"] == "MANUAL_REVIEW"

    predictor.model.predict_proba = MagicMock(return_value=[[0.2999, 0.7001]])
    res_high_above = predictor.predict(txn, low_threshold=0.30, high_threshold=0.70)
    assert res_high_above["risk_level"] == "HIGH"
