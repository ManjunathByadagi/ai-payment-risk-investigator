from sqlalchemy.orm import Session
from backend.models.transaction import AuditLogModel
from typing import List, Optional

class AuditService:
    def get_logs(self, db: Session, limit: int = 50) -> List[AuditLogModel]:
        return db.query(AuditLogModel).order_by(AuditLogModel.timestamp.desc()).limit(limit).all()

    def get_logs_by_transaction(self, db: Session, transaction_id: str) -> List[AuditLogModel]:
        return db.query(AuditLogModel).filter(AuditLogModel.transaction_id == transaction_id).order_by(AuditLogModel.timestamp.desc()).all()
