import pytest
from agent.investigator import RiskInvestigatorAgent

def test_agent_new_device_selects_device_tool():
    agent = RiskInvestigatorAgent()
    txn = {
        "transaction_id": "TXN_DEV_01",
        "customer_id": "CUST_01",
        "merchant_id": "MERCH_01",
        "device_id": "DEV_NEW_99",
        "device_new": 1,
        "ip_risk_score": 0.85
    }
    risk_res = {
        "risk_probability": 0.82,
        "risk_level": "HIGH",
        "risk_signals": [{"signal": "new_device", "severity": "medium", "description": "New device"}]
    }
    report = agent.investigate(txn, risk_res)
    called_tool_names = [s.tool_name for s in report.investigation_steps]
    assert "get_device_activity" in called_tool_names

def test_agent_velocity_selects_velocity_tool():
    agent = RiskInvestigatorAgent()
    txn = {
        "transaction_id": "TXN_VEL_01",
        "customer_id": "CUST_02",
        "merchant_id": "MERCH_01",
        "device_id": "DEV_01",
        "transactions_last_10_minutes": 5,
        "velocity_score": 1.5
    }
    risk_res = {
        "risk_probability": 0.78,
        "risk_level": "HIGH",
        "risk_signals": [{"signal": "high_velocity", "severity": "high", "description": "High velocity"}]
    }
    report = agent.investigate(txn, risk_res)
    called_tool_names = [s.tool_name for s in report.investigation_steps]
    assert "get_transaction_velocity" in called_tool_names

def test_agent_geo_mismatch_selects_geo_tool():
    agent = RiskInvestigatorAgent()
    txn = {
        "transaction_id": "TXN_GEO_01",
        "customer_id": "CUST_03",
        "merchant_id": "MERCH_01",
        "device_id": "DEV_01",
        "customer_country": "IN",
        "transaction_country": "US"
    }
    risk_res = {
        "risk_probability": 0.75,
        "risk_level": "HIGH",
        "risk_signals": [{"signal": "geographic_mismatch", "severity": "high", "description": "Geo mismatch"}]
    }
    report = agent.investigate(txn, risk_res)
    called_tool_names = [s.tool_name for s in report.investigation_steps]
    assert "check_geographic_consistency" in called_tool_names

def test_agent_amount_deviation_selects_customer_history_tool():
    agent = RiskInvestigatorAgent()
    txn = {
        "transaction_id": "TXN_AMT_01",
        "customer_id": "CUST_04",
        "merchant_id": "MERCH_01",
        "device_id": "DEV_01",
        "amount": 25000.0,
        "average_customer_amount": 200.0
    }
    risk_res = {
        "risk_probability": 0.88,
        "risk_level": "HIGH",
        "risk_signals": [{"signal": "amount_deviation", "severity": "high", "description": "Amount deviation"}]
    }
    report = agent.investigate(txn, risk_res)
    called_tool_names = [s.tool_name for s in report.investigation_steps]
    assert "get_customer_history" in called_tool_names

def test_agent_never_exceeds_max_tool_calls():
    agent = RiskInvestigatorAgent()
    txn = {
        "transaction_id": "TXN_MAX_01",
        "customer_id": "CUST_MAX",
        "merchant_id": "MERCH_MAX",
        "device_id": "DEV_MAX",
        "device_new": 1,
        "customer_country": "IN",
        "transaction_country": "XX",
        "transactions_last_10_minutes": 10,
        "amount": 50000.0,
        "average_customer_amount": 100.0,
        "merchant_risk_score": 0.9,
        "customer_previous_risk_count": 5
    }
    risk_res = {
        "risk_probability": 0.95,
        "risk_level": "HIGH",
        "risk_signals": [
            {"signal": "new_device", "severity": "high", "description": "New device"},
            {"signal": "high_velocity", "severity": "high", "description": "Velocity"},
            {"signal": "geographic_mismatch", "severity": "high", "description": "Geo mismatch"},
            {"signal": "amount_deviation", "severity": "high", "description": "Amount"}
        ]
    }
    report = agent.investigate(txn, risk_res)
    assert len(report.investigation_steps) <= agent.MAX_TOOL_CALLS

def test_agent_deterministic_fallback():
    agent = RiskInvestigatorAgent()
    agent.llm_available = False # Force fallback
    txn = {
        "transaction_id": "TXN_FALLBACK_01",
        "customer_id": "CUST_FB",
        "merchant_id": "MERCH_FB",
        "device_id": "DEV_FB",
        "device_new": 1
    }
    risk_res = {
        "risk_probability": 0.72,
        "risk_level": "HIGH",
        "risk_signals": [{"signal": "new_device", "severity": "medium", "description": "New device"}]
    }
    report = agent.investigate(txn, risk_res)
    assert report.is_llm_generated is False
    assert len(report.investigation_steps) > 0
    assert report.recommended_action in ["MANUAL_REVIEW", "MONITOR"]

def test_agent_produces_audit_steps():
    agent = RiskInvestigatorAgent()
    txn = {
        "transaction_id": "TXN_AUDIT_01",
        "customer_id": "CUST_AUD",
        "merchant_id": "MERCH_AUD",
        "device_id": "DEV_AUD",
        "device_new": 1
    }
    risk_res = {
        "risk_probability": 0.80,
        "risk_level": "HIGH",
        "risk_signals": [{"signal": "new_device", "severity": "high", "description": "New device"}]
    }
    report = agent.investigate(txn, risk_res)
    assert len(report.investigation_steps) > 0
    first_step = report.investigation_steps[0]
    assert first_step.step == 1
    assert first_step.tool_name != ""
    assert first_step.reason != ""
    assert first_step.timestamp != ""

def test_evidence_mapping_device_and_velocity_executed():
    agent = RiskInvestigatorAgent()
    txn = {
        "transaction_id": "TXN_MULTI_SIG",
        "customer_id": "CUST_M",
        "merchant_id": "MERCH_M",
        "device_id": "DEV_99812",
        "device_new": 1,
        "ip_risk_score": 0.85,
        "transactions_last_10_minutes": 4,
        "transactions_last_1_hour": 7,
        "transactions_last_24_hours": 12,
        "failed_transactions_last_24_hours": 2,
        "velocity_score": 1.45,
        "customer_country": "IN",
        "transaction_country": "US"
    }
    risk_res = {
        "risk_probability": 0.776,
        "risk_level": "HIGH",
        "risk_signals": [
            {"signal": "new_device", "severity": "high", "description": "New device"},
            {"signal": "high_velocity", "severity": "high", "description": "Velocity surge"}
        ]
    }
    report = agent.investigate(txn, risk_res)
    
    # Device tool executed
    assert "get_device_activity" in report.evidence
    dev = report.evidence["get_device_activity"]
    assert dev["is_new_device"] is True
    assert dev["device_risk_level"] == "HIGH"
    
    # Velocity tool executed
    assert "get_transaction_velocity" in report.evidence
    vel = report.evidence["get_transaction_velocity"]
    assert vel["velocity_status"] == "HIGH"
    assert vel["transactions_last_10_minutes"] == 4

def test_unexecuted_tools_marked_not_checked():
    agent = RiskInvestigatorAgent()
    txn = {
        "transaction_id": "TXN_PARTIAL_UNCHECKED",
        "customer_id": "CUST_UNCHECKED",
        "merchant_id": "MERCH_UNCHECKED",
        "device_id": "DEV_UNCHECKED",
        "device_new": 1,
        "ip_risk_score": 0.85
    }
    risk_res = {
        "risk_probability": 0.776,
        "risk_level": "HIGH",
        "risk_signals": [
            {"signal": "new_device", "severity": "high", "description": "New device"}
        ]
    }
    report = agent.investigate(txn, risk_res)
    # Geo tool was NOT executed because signals focused only on device
    assert "check_geographic_consistency" not in report.evidence
    assert "get_customer_history" not in report.evidence

def test_evidence_strength_metadata_present():
    agent = RiskInvestigatorAgent()
    txn = {
        "transaction_id": "TXN_STR_01",
        "customer_id": "CUST_STR",
        "merchant_id": "MERCH_STR",
        "device_id": "DEV_STR",
        "device_new": 1,
        "ip_risk_score": 0.9,
        "transactions_last_10_minutes": 5
    }
    risk_res = {
        "risk_probability": 0.85,
        "risk_level": "HIGH",
        "risk_signals": [
            {"signal": "new_device", "severity": "high", "description": "New device"},
            {"signal": "high_velocity", "severity": "high", "description": "High velocity"}
        ]
    }
    report = agent.investigate(txn, risk_res)
    assert report.evidence_strength in ["HIGH", "MEDIUM", "LOW"]
    assert report.tools_executed_count > 0
    assert report.max_tools == 4

def test_investigation_confidence_is_dynamic_and_bounded():
    agent = RiskInvestigatorAgent()
    low_evidence = agent.investigate(
        {"transaction_id": "TXN_CONF_LOW", "customer_id": "CUST_CONF_LOW"},
        {"risk_probability": 0.31, "risk_level": "MEDIUM", "risk_signals": []}
    )
    high_evidence = agent.investigate(
        {
            "transaction_id": "TXN_CONF_HIGH",
            "customer_id": "CUST_CONF_HIGH",
            "merchant_id": "MERCH_CONF_HIGH",
            "device_id": "DEV_CONF_HIGH",
            "device_new": 1,
            "ip_risk_score": 0.9,
            "transactions_last_10_minutes": 5,
            "customer_country": "IN",
            "transaction_country": "US",
            "amount": 10000.0,
            "average_customer_amount": 100.0,
        },
        {
            "risk_probability": 0.95,
            "risk_level": "HIGH",
            "risk_signals": [
                {"signal": "new_device", "severity": "high"},
                {"signal": "high_velocity", "severity": "high"},
                {"signal": "geographic_mismatch", "severity": "high"},
                {"signal": "amount_deviation", "severity": "high"},
            ],
        }
    )

    assert 0.0 <= low_evidence.confidence_score <= 1.0
    assert 0.0 <= high_evidence.confidence_score <= 1.0
    assert low_evidence.confidence_score != high_evidence.confidence_score

def test_investigation_confidence_excludes_unverified_states():
    agent = RiskInvestigatorAgent()
    steps = [
        type("Step", (), {"tool_name": "device", "tool_result": {"status": "VERIFIED", "value": True}})(),
        type("Step", (), {"tool_name": "velocity", "tool_result": {"status": "NOT CHECKED"}})(),
        type("Step", (), {"tool_name": "geo", "tool_result": {"status": "NOT AVAILABLE"}})(),
    ]

    confidence = agent._calculate_investigation_confidence({}, steps, "MEDIUM")
    expected = agent._calculate_investigation_confidence({}, steps[:1], "MEDIUM")

    assert confidence < expected
    assert 0.0 <= confidence <= 1.0

def test_investigation_confidence_graduates_without_saturating():
    agent = RiskInvestigatorAgent()
    no_verified = [
        type("Step", (), {"tool_name": "device", "tool_result": {"status": "NOT CHECKED"}})()
    ]
    partial = [
        type("Step", (), {"tool_name": "device", "tool_result": {"status": "VERIFIED", "value": True}})(),
        type("Step", (), {"tool_name": "velocity", "tool_result": {"status": "VERIFIED", "value": True}})(),
    ]
    strong = [
        type("Step", (), {"tool_name": name, "tool_result": {"status": "VERIFIED", "value": True}})()
        for name in ["device", "velocity", "geo", "customer"]
    ]

    no_verified_confidence = agent._calculate_investigation_confidence({}, no_verified, "HIGH")
    partial_confidence = agent._calculate_investigation_confidence({}, partial, "MEDIUM")
    strong_confidence = agent._calculate_investigation_confidence({}, strong, "HIGH")

    assert no_verified_confidence < partial_confidence < strong_confidence < 1.0
    assert strong_confidence == 0.9
    assert round(strong_confidence, 3) == strong_confidence

def test_multi_signal_uses_full_4_tool_budget():
    agent = RiskInvestigatorAgent()
    txn = {
        "transaction_id": "TXN_FULL_BUDGET_01",
        "customer_id": "CUST_FULL",
        "merchant_id": "MERCH_FULL",
        "device_id": "DEV_FULL",
        "device_new": 1,
        "ip_risk_score": 0.85,
        "transactions_last_10_minutes": 4,
        "amount": 12500.0,
        "average_customer_amount": 850.0,
        "customer_country": "IN",
        "transaction_country": "US"
    }
    risk_res = {
        "risk_probability": 0.776,
        "risk_level": "HIGH",
        "risk_signals": [
            {"signal": "new_device", "severity": "high", "description": "New device"},
            {"signal": "high_velocity", "severity": "high", "description": "High velocity"},
            {"signal": "geographic_mismatch", "severity": "high", "description": "Geo mismatch"},
            {"signal": "amount_deviation", "severity": "high", "description": "Amount deviation"}
        ]
    }
    report = agent.investigate(txn, risk_res)
    assert report.tools_executed_count == 4
    called_tool_names = [s.tool_name for s in report.investigation_steps]
    assert "get_device_activity" in called_tool_names
    assert "get_transaction_velocity" in called_tool_names
    assert "check_geographic_consistency" in called_tool_names
    assert "get_customer_history" in called_tool_names

def test_customer_history_preserves_benchmark_amount():
    agent = RiskInvestigatorAgent()
    txn = {
        "transaction_id": "TXN_BENCH_01",
        "customer_id": "CUST_BENCH",
        "merchant_id": "MERCH_BENCH",
        "device_id": "DEV_BENCH",
        "amount": 12500.0,
        "average_customer_amount": 850.0
    }
    risk_res = {
        "risk_probability": 0.80,
        "risk_level": "HIGH",
        "risk_signals": [{"signal": "amount_deviation", "severity": "high", "description": "Amount deviation"}]
    }
    report = agent.investigate(txn, risk_res)
    cust_evidence = report.evidence.get("get_customer_history", {})
    assert cust_evidence.get("declared_benchmark_amount") == 850.0
    assert "average_amount" in cust_evidence
