import uuid
import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.models.transaction import TransactionModel, AuditLogModel
from backend.config import settings
from ml.predict import RiskPredictor
from agent.tools import RiskTools

_global_predictor: Optional[RiskPredictor] = None

def get_risk_predictor() -> RiskPredictor:
    global _global_predictor
    if _global_predictor is None:
        _global_predictor = RiskPredictor()
    return _global_predictor

class RiskService:
    def __init__(self, predictor: Optional[RiskPredictor] = None):
        self.predictor = predictor or get_risk_predictor()
        self.risk_tools = RiskTools()

    def analyze_transaction(self, db: Session, req_data: Dict[str, Any]) -> Dict[str, Any]:
        # Generate TXN ID if missing
        if not req_data.get("transaction_id"):
            req_data["transaction_id"] = f"TXN_{uuid.uuid4().hex[:8].upper()}"

        # Use the same ledger history as the investigation evidence when available.
        customer_history = self.risk_tools.get_customer_history(req_data["customer_id"])
        if customer_history.get("found"):
            req_data["average_customer_amount"] = customer_history["average_amount"]

        # Run ML Predictor using centralized config thresholds
        ml_res = self.predictor.predict(
            req_data,
            low_threshold=settings.LOW_RISK_THRESHOLD,
            high_threshold=settings.HIGH_RISK_THRESHOLD
        )
        
        # Merge results
        txn_id = req_data["transaction_id"]
        prob = ml_res["risk_probability"]
        risk_level = ml_res["risk_level"]
        decision = ml_res["decision"]
        signals = ml_res["risk_signals"]

        # Calculate derived values for storage
        amount_dev = req_data.get("amount") / (req_data.get("average_customer_amount", 150.0) + 1e-5)
        geo_mismatch = 1 if req_data.get("transaction_country") != req_data.get("customer_country") else 0
        velocity_score = (
            req_data.get("transactions_last_10_minutes", 0) * 3.0 + 
            req_data.get("transactions_last_1_hour", 0) * 1.5 + 
            req_data.get("transactions_last_24_hours", 0) * 0.5
        ) / 10.0

        # Save to DB
        txn_db = db.query(TransactionModel).filter(TransactionModel.transaction_id == txn_id).first()
        if not txn_db:
            txn_db = TransactionModel(
                transaction_id=txn_id,
                customer_id=req_data["customer_id"],
                merchant_id=req_data["merchant_id"],
                amount=req_data["amount"],
                currency=req_data.get("currency", "INR"),
                customer_country=req_data.get("customer_country", "IN"),
                transaction_country=req_data.get("transaction_country", "IN"),
                device_id=req_data["device_id"],
                device_new=req_data.get("device_new", 0),
                customer_account_age_days=req_data.get("customer_account_age_days", 30),
                transactions_last_10_minutes=req_data.get("transactions_last_10_minutes", 0),
                transactions_last_1_hour=req_data.get("transactions_last_1_hour", 0),
                transactions_last_24_hours=req_data.get("transactions_last_24_hours", 0),
                average_customer_amount=req_data.get("average_customer_amount", 150.0),
                amount_deviation=amount_dev,
                merchant_risk_score=req_data.get("merchant_risk_score", 0.05),
                customer_previous_risk_count=req_data.get("customer_previous_risk_count", 0),
                failed_transactions_last_24_hours=req_data.get("failed_transactions_last_24_hours", 0),
                ip_risk_score=req_data.get("ip_risk_score", 0.1),
                unusual_time=req_data.get("unusual_time", 0),
                geographic_mismatch=geo_mismatch,
                velocity_score=velocity_score,
                risk_probability=prob,
                risk_level=risk_level,
                decision=decision,
                risk_signals=signals,
                model_version="v1.0-xgb"
            )
            db.add(txn_db)
        else:
            txn_db.risk_probability = prob
            txn_db.risk_level = risk_level
            txn_db.decision = decision
            txn_db.risk_signals = signals

        # Audit Record
        audit = AuditLogModel(
            event_type="TRANSACTION_ANALYSIS",
            transaction_id=txn_id,
            decision=decision,
            reason=f"Risk Score {prob:.4f} evaluated as {risk_level} risk.",
            model_version="v1.0-xgb",
            details={"risk_signals_count": len(signals)}
        )
        db.add(audit)
        db.commit()
        db.refresh(txn_db)

        return {
            "transaction_id": txn_id,
            "risk_probability": prob,
            "risk_level": risk_level,
            "decision": decision,
            "risk_signals": signals,
            "investigation_available": risk_level != "LOW"
        }
