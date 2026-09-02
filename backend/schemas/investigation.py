from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

class InvestigationStepSchema(BaseModel):
    step: int
    tool_name: str
    reason: str
    tool_result: Dict[str, Any]
    timestamp: str

class InvestigationResponse(BaseModel):
    transaction_id: str
    risk_probability: float
    risk_level: str
    evidence: Dict[str, Any]
    investigation_steps: Optional[List[InvestigationStepSchema]] = None
    investigation_summary: str
    confidence_score: float
    evidence_strength: Optional[str] = "HIGH"
    tools_executed_count: Optional[int] = 0
    max_tools: Optional[int] = 4
    recommended_action: str
    is_llm_generated: bool
    created_at: Optional[datetime] = None

class AuditLogResponse(BaseModel):
    id: int
    event_type: str
    transaction_id: str
    timestamp: datetime
    decision: str
    reason: str
    model_version: str
    details: Optional[Dict[str, Any]] = None
