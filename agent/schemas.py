from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class InvestigationStep(BaseModel):
    step: int
    tool_name: str
    reason: str
    tool_result: Dict[str, Any]
    timestamp: str

class ToolResult(BaseModel):
    tool_name: str
    status: str = "success"
    data: Dict[str, Any]

class InvestigationReport(BaseModel):
    transaction_id: str
    risk_probability: float
    risk_level: str
    evidence: Dict[str, Any]
    investigation_steps: List[InvestigationStep] = []
    investigation_summary: str
    confidence_score: float
    evidence_strength: str = "HIGH"
    tools_executed_count: int = 0
    max_tools: int = 4
    recommended_action: str
    is_llm_generated: bool = False
