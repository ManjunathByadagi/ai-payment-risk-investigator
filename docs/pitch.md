# 5-Minute Technical Pitch Structure

## 0:00–0:30 | The Problem
"Modern payment gateways process millions of transactions daily. Traditional rule-based systems suffer from high false positive rates, while pure LLM solutions are too slow, expensive, and prone to hallucinations to evaluate transaction risk directly."

## 0:30–1:00 | The Solution
"We built the **AI Payment Risk Investigator**: a hybrid system where lightweight machine learning models score transaction risk in milliseconds, and an autonomous AI agent investigates high-risk anomalies by gathering evidence from contextual tools."

## 1:00–2:30 | Live Demo
- Demonstrate the **Dashboard View** showing total processed transactions and risk breakdowns.
- Walk through the **Analyze Transaction** tab using the pre-loaded **High Risk (New Device & Geo Mismatch)** demo preset.
- Show instant ML scoring (Probability: ~90%+, HIGH Risk).
- Trigger the **AI Investigation Agent** and show the generated evidence report detailing customer history, velocity spikes, and location anomalies.

## 2:30–3:30 | Architecture & Tech Stack
- Highlight the defensive architecture: FastAPI backend, scikit-learn/XGBoost ML pipeline, bounded tool-calling agent, React/Vite dashboard, and SQLAlchemy ORM.
- Emphasize safety: The LLM never touches payment rails or alters risk scores; it acts as an evidence compiler.

## 3:30–4:20 | Evaluation Results
- Share actual evaluation metrics from our test set:
  - **Accuracy**: 90.48%
  - **Precision**: 89.01%
  - **Recall**: 57.46%
  - **F1 Score**: 0.6984
  - **FPR**: 1.68%

## 4:20–5:00 | Limitations & Conclusion
- Discuss realistic limitations (synthetic data foundation, static risk thresholds).
- Conclude with the core project principle: *"AI where AI is useful: ML detects risk, deterministic tools gather evidence, AI synthesizes investigation."*
