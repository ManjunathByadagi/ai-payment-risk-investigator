from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.models.transaction import TransactionModel, InvestigationModel

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    total_txns = db.query(TransactionModel).count()
    if total_txns == 0:
        return {
            "total_transactions": 0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0,
            "avg_risk_score": 0.0,
            "total_investigations": 0
        }
        
    high_count = db.query(TransactionModel).filter(TransactionModel.risk_level == "HIGH").count()
    medium_count = db.query(TransactionModel).filter(TransactionModel.risk_level == "MEDIUM").count()
    low_count = db.query(TransactionModel).filter(TransactionModel.risk_level == "LOW").count()
    
    avg_score = db.query(func.avg(TransactionModel.risk_probability)).scalar() or 0.0
    total_invs = db.query(InvestigationModel).count()

    return {
        "total_transactions": total_txns,
        "high_risk_count": high_count,
        "medium_risk_count": medium_count,
        "low_risk_count": low_count,
        "avg_risk_score": round(float(avg_score), 4),
        "total_investigations": total_invs
    }

@router.get("/risk-distribution")
def get_risk_distribution(db: Session = Depends(get_db)):
    txns = db.query(TransactionModel).order_by(TransactionModel.timestamp.desc()).limit(100).all()
    recent = []
    for t in txns:
        recent.append({
            "transaction_id": t.transaction_id,
            "amount": t.amount,
            "risk_probability": t.risk_probability,
            "risk_level": t.risk_level,
            "decision": t.decision,
            "timestamp": t.timestamp.isoformat() if t.timestamp else None
        })
    return {"recent_transactions": recent}
