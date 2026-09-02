from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from backend.database import get_db
from backend.schemas.transaction import TransactionAnalyzeRequest, TransactionAnalyzeResponse
from backend.services.risk_service import RiskService
from backend.models.transaction import TransactionModel

router = APIRouter(prefix="/transactions", tags=["Transactions"])
risk_service = RiskService()

@router.post("/analyze", response_model=TransactionAnalyzeResponse, status_code=status.HTTP_200_OK)
def analyze_transaction(request: TransactionAnalyzeRequest, db: Session = Depends(get_db)):
    try:
        req_dict = request.model_dump()
        result = risk_service.analyze_transaction(db, req_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transaction analysis error: {str(e)}")

@router.get("/{transaction_id}")
def get_transaction(transaction_id: str, db: Session = Depends(get_db)):
    txn = db.query(TransactionModel).filter(TransactionModel.transaction_id == transaction_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found.")
    return {
        "transaction_id": txn.transaction_id,
        "customer_id": txn.customer_id,
        "merchant_id": txn.merchant_id,
        "amount": txn.amount,
        "currency": txn.currency,
        "customer_country": txn.customer_country,
        "transaction_country": txn.transaction_country,
        "device_id": txn.device_id,
        "risk_probability": txn.risk_probability,
        "risk_level": txn.risk_level,
        "decision": txn.decision,
        "risk_signals": txn.risk_signals or []
    }
