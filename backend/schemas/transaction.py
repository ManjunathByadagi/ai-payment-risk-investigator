from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class TransactionAnalyzeRequest(BaseModel):
    transaction_id: Optional[str] = None
    customer_id: str = Field(..., json_schema_extra={"example": "CUST_00123"})
    merchant_id: str = Field(..., json_schema_extra={"example": "MERCH_0045"})
    amount: float = Field(..., gt=0, json_schema_extra={"example": 2500.50})
    currency: str = Field(default="INR", json_schema_extra={"example": "INR"})
    timestamp: Optional[str] = None
    customer_country: str = Field(default="IN", json_schema_extra={"example": "IN"})
    transaction_country: str = Field(default="IN", json_schema_extra={"example": "IN"})
    device_id: str = Field(..., json_schema_extra={"example": "DEV_0099"})
    device_new: int = Field(default=0, ge=0, le=1)
    customer_account_age_days: int = Field(default=120, ge=0)
    transactions_last_10_minutes: int = Field(default=0, ge=0)
    transactions_last_1_hour: int = Field(default=0, ge=0)
    transactions_last_24_hours: int = Field(default=0, ge=0)
    average_customer_amount: float = Field(default=150.0, gt=0)
    merchant_risk_score: float = Field(default=0.05, ge=0.0, le=1.0)
    customer_previous_risk_count: int = Field(default=0, ge=0)
    failed_transactions_last_24_hours: int = Field(default=0, ge=0)
    ip_risk_score: float = Field(default=0.1, ge=0.0, le=1.0)
    unusual_time: int = Field(default=0, ge=0, le=1)

class RiskSignal(BaseModel):
    signal: str
    severity: str
    description: str

class TransactionAnalyzeResponse(BaseModel):
    transaction_id: str
    risk_probability: float
    risk_level: str
    decision: str
    risk_signals: List[RiskSignal]
    investigation_available: bool
