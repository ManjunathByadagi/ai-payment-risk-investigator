from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from backend.database import get_db
from backend.schemas.investigation import InvestigationResponse, AuditLogResponse
from backend.services.investigation_service import InvestigationService
from backend.services.audit_service import AuditService
from backend.models.transaction import InvestigationModel
from backend.models.transaction import TransactionModel

router = APIRouter(tags=["Investigations & Audit"])
investigation_service = InvestigationService()
audit_service = AuditService()

def _format_investigation_response(inv: InvestigationModel) -> Dict[str, Any]:
    evidence_dict = inv.evidence or {}
    steps = evidence_dict.get("_investigation_steps", [])
    evidence_strength = evidence_dict.get("_evidence_strength", "HIGH")
    tools_count = evidence_dict.get("_tools_executed_count", len([k for k in evidence_dict.keys() if not k.startswith("_")]))
    max_tools = evidence_dict.get("_max_tools", 4)
    
    return {
        "transaction_id": inv.transaction_id,
        "risk_probability": inv.risk_probability,
        "risk_level": inv.risk_level,
        "evidence": evidence_dict,
        "investigation_steps": steps,
        "investigation_summary": inv.investigation_summary,
        "confidence_score": inv.confidence_score,
        "evidence_strength": evidence_strength,
        "tools_executed_count": tools_count,
        "max_tools": max_tools,
        "recommended_action": inv.recommended_action,
        "is_llm_generated": bool(inv.is_llm_generated),
        "created_at": inv.created_at
    }

@router.post("/investigations/{transaction_id}", response_model=InvestigationResponse)
def trigger_investigation(transaction_id: str, db: Session = Depends(get_db)):
    try:
        txn = db.query(TransactionModel).filter(TransactionModel.transaction_id == transaction_id).first()
        if not txn:
            raise ValueError(f"Transaction {transaction_id} not found in database.")
        if txn.risk_level == "LOW":
            raise ValueError("Automatic investigation is not available for LOW risk transactions.")
        inv = investigation_service.run_investigation(db, transaction_id)
        return _format_investigation_response(inv)
    except ValueError as ve:
        status_code = 400 if "LOW risk" in str(ve) else 404
        raise HTTPException(status_code=status_code, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Investigation failed: {str(e)}")

@router.get("/investigations/{transaction_id}", response_model=InvestigationResponse)
def get_investigation(transaction_id: str, db: Session = Depends(get_db)):
    inv = investigation_service.get_investigation(db, transaction_id)
    if not inv:
        raise HTTPException(status_code=404, detail=f"No investigation record found for {transaction_id}")
    return _format_investigation_response(inv)

@router.get("/audit", response_model=list[AuditLogResponse])
def get_audit_logs(limit: int = 50, db: Session = Depends(get_db)):
    return audit_service.get_logs(db, limit=limit)
