import datetime
from sqlalchemy.orm import Session
from backend.models.transaction import TransactionModel, InvestigationModel, AuditLogModel
from agent.investigator import RiskInvestigatorAgent

class InvestigationService:
    def __init__(self):
        self.agent = RiskInvestigatorAgent()

    def run_investigation(self, db: Session, transaction_id: str):
        # Fetch transaction
        txn = db.query(TransactionModel).filter(TransactionModel.transaction_id == transaction_id).first()
        if not txn:
            raise ValueError(f"Transaction {transaction_id} not found in database.")

        txn_dict = {
            "transaction_id": txn.transaction_id,
            "customer_id": txn.customer_id,
            "merchant_id": txn.merchant_id,
            "amount": txn.amount,
            "currency": txn.currency,
            "customer_country": txn.customer_country,
            "transaction_country": txn.transaction_country,
            "device_id": txn.device_id,
            "device_new": txn.device_new,
            "customer_account_age_days": txn.customer_account_age_days,
            "transactions_last_10_minutes": txn.transactions_last_10_minutes,
            "transactions_last_1_hour": txn.transactions_last_1_hour,
            "transactions_last_24_hours": txn.transactions_last_24_hours,
            "average_customer_amount": txn.average_customer_amount,
            "merchant_risk_score": txn.merchant_risk_score,
            "customer_previous_risk_count": txn.customer_previous_risk_count,
            "failed_transactions_last_24_hours": txn.failed_transactions_last_24_hours,
            "ip_risk_score": txn.ip_risk_score,
            "unusual_time": txn.unusual_time
        }

        risk_result = {
            "risk_probability": txn.risk_probability,
            "risk_level": txn.risk_level,
            "risk_signals": txn.risk_signals or []
        }

        # Run agent investigation
        report = self.agent.investigate(txn_dict, risk_result)

        # Check existing investigation
        existing_inv = db.query(InvestigationModel).filter(InvestigationModel.transaction_id == transaction_id).first()
        if not existing_inv:
            inv_db = InvestigationModel(
                transaction_id=transaction_id,
                risk_probability=report.risk_probability,
                risk_level=report.risk_level,
                evidence=report.evidence,
                investigation_summary=report.investigation_summary,
                confidence_score=report.confidence_score,
                recommended_action=report.recommended_action,
                is_llm_generated=1 if report.is_llm_generated else 0
            )
            db.add(inv_db)
        else:
            existing_inv.evidence = report.evidence
            existing_inv.investigation_summary = report.investigation_summary
            existing_inv.recommended_action = report.recommended_action
            existing_inv.is_llm_generated = 1 if report.is_llm_generated else 0
            inv_db = existing_inv

        # Create Audit Log
        audit = AuditLogModel(
            event_type="AI_INVESTIGATION_COMPLETED",
            transaction_id=transaction_id,
            decision=report.recommended_action,
            reason=f"Investigation completed with confidence {report.confidence_score}. Recommendation: {report.recommended_action}",
            model_version="v1.0-xgb",
            details={"is_llm_generated": report.is_llm_generated}
        )
        db.add(audit)
        
        # Update transaction decision if recommended action differs
        txn.decision = report.recommended_action
        
        db.commit()
        db.refresh(inv_db)
        return inv_db

    def get_investigation(self, db: Session, transaction_id: str):
        return db.query(InvestigationModel).filter(InvestigationModel.transaction_id == transaction_id).first()
