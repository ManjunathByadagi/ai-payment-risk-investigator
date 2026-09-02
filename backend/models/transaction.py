import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, JSON
from backend.database import Base

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)

class TransactionModel(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    merchant_id = Column(String, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    timestamp = Column(DateTime, default=utc_now, index=True)
    customer_country = Column(String, default="IN")
    transaction_country = Column(String, default="IN")
    device_id = Column(String)
    device_new = Column(Integer, default=0)
    customer_account_age_days = Column(Integer, default=30)
    transactions_last_10_minutes = Column(Integer, default=0)
    transactions_last_1_hour = Column(Integer, default=0)
    transactions_last_24_hours = Column(Integer, default=0)
    average_customer_amount = Column(Float, default=150.0)
    amount_deviation = Column(Float, default=1.0)
    merchant_risk_score = Column(Float, default=0.05)
    customer_previous_risk_count = Column(Integer, default=0)
    failed_transactions_last_24_hours = Column(Integer, default=0)
    ip_risk_score = Column(Float, default=0.1)
    unusual_time = Column(Integer, default=0)
    geographic_mismatch = Column(Integer, default=0)
    velocity_score = Column(Float, default=0.0)
    
    # ML Scoring Output fields
    risk_probability = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)
    decision = Column(String, nullable=True)
    risk_signals = Column(JSON, nullable=True)
    model_version = Column(String, default="v1.0-xgb")

class InvestigationModel(Base):
    __tablename__ = "investigations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String, index=True, nullable=False)
    risk_probability = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    evidence = Column(JSON, nullable=False)
    investigation_summary = Column(Text, nullable=False)
    confidence_score = Column(Float, default=0.90)
    recommended_action = Column(String, nullable=False)
    is_llm_generated = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)

class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String, nullable=False)
    transaction_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, default=utc_now, index=True)
    decision = Column(String, nullable=False)
    reason = Column(Text, nullable=False)
    model_version = Column(String, default="v1.0-xgb")
    details = Column(JSON, nullable=True)
