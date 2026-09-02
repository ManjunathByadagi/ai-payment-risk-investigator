# Autonomous Agent Design & Safety Boundaries

## 1. Agent Design Philosophy
The AI Agent is designed as a **defensive, bounded assistant**. It does not replace the statistical ML model for numerical risk scoring, nor does it possess write access to financial rails.

## 2. Tools Catalog

1. `get_customer_history(customer_id: str)`: Inspects historical transaction counts, prior risk flags, and average customer spending.
2. `get_merchant_statistics(merchant_id: str)`: Retrieves merchant risk score and baseline dispute rates.
3. `get_transaction_velocity(customer_id: str)`: Computes short-term (10 min, 1 hr, 24 hr) velocity spikes.
4. `get_device_activity(device_id: str)`: Analyzes device novelty and IP address risk.
5. `check_geographic_consistency(customer_id: str, country: str)`: Checks transaction location against customer home country.

## 3. Execution Safety Guarantees
- **No Financial Mutating Actions**: The agent cannot execute transfers, issue refunds, or block accounts autonomously.
- **Strict Evidence Anchoring**: Summaries are built directly from structured tool JSON outputs.
- **Graceful Degraded Mode**: If external LLM APIs fail or are unconfigured, the system relies on deterministic python templates, ensuring 100% operational uptime.
