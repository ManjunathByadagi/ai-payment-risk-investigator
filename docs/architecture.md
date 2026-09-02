# System Architecture & Technical Specifications

## 1. System Overview
The **AI Payment Risk Investigator** is a defensive, dual-tier payment anomaly risk analysis and investigation platform.
It combines supervised machine learning for fast risk scoring with a tool-calling AI agent for bounded evidence collection and automated synthesis.

## 2. Core Architectural Diagram

```mermaid
flowchart TD
    Client[React + Vite Frontend Dashboard] -->|HTTP REST| API[FastAPI Backend Server]
    
    subgraph Core Backend Engine
        API -->|Transaction Data| FeatureEng[Feature Engineering & Preprocessor]
        FeatureEng -->|Scaled Feature Matrix| Model[Supervised Risk Model: XGBoost / RF]
        Model -->|Probabilistic Risk Score| DecisionRouter{Risk Level Classification}
    end

    DecisionRouter -->|Score < 0.30| Approve[LOW RISK: APPROVE]
    DecisionRouter -->|0.30 <= Score < 0.70| Monitor[MEDIUM RISK: MONITOR]
    DecisionRouter -->|Score >= 0.70| TriggerAgent[HIGH RISK: Trigger AI Agent]

    subgraph Autonomous Investigation Agent
        TriggerAgent --> AgentCore[Investigation Agent Orchestrator]
        AgentCore --> Tool1[Customer History Tool]
        AgentCore --> Tool2[Merchant Stats Tool]
        AgentCore --> Tool3[Velocity Analysis Tool]
        AgentCore --> Tool4[Device Activity Tool]
        AgentCore --> Tool5[Geo Consistency Tool]
        
        Tool1 --> EvidenceAgg[Structured Evidence Matrix]
        Tool2 --> EvidenceAgg
        Tool3 --> EvidenceAgg
        Tool4 --> EvidenceAgg
        Tool5 --> EvidenceAgg
        
        EvidenceAgg -->|Structured JSON| SummaryEngine[Deterministic / LLM Explanation Engine]
    end

    SummaryEngine -->|Investigation Report| ManualReview[MANUAL_REVIEW Recommendation]
    Approve --> Audit[Database & Audit Logging Service]
    Monitor --> Audit
    ManualReview --> Audit
    Audit --> DB[(SQLite / PostgreSQL DB)]
```

## 3. Component Details

### 3.1 Preprocessing & Feature Pipeline
- Input features are scaled using `StandardScaler` fitted strictly on training data to prevent data leakage.
- Derived features (Amount Deviation, Geographic Mismatch Indicator, Velocity Score) are computed dynamically before inference.

### 3.2 Machine Learning Engine
- Primary Serving Model: **XGBoost Classifier** persistence artifact (`ml/model/risk_model.joblib`).
- Baselines: Logistic Regression and Random Forest.
- Outputs continuous risk probability between `0.0` and `1.0`.

### 3.3 Autonomous Investigation Agent
- Triggers when `risk_probability >= 0.70`.
- Bounded Execution: Uses 5 deterministic read-only tools to gather contextual background.
- LLM Fallback: If `OPENAI_API_KEY` is present, OpenAI model formats evidence into narrative reports. If missing or failing, deterministic rules format evidence safely.

### 3.4 Data & Persistence Layer
- ORM: SQLAlchemy models for `Transaction`, `Investigation`, and `AuditLog`.
- Storage: SQLite default (`risk_investigator.db`), PostgreSQL ready via `DATABASE_URL`.
