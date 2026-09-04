import os
import json
import datetime
from typing import Dict, Any, List, Optional
from agent.tools import RiskTools
from agent.schemas import InvestigationReport, InvestigationStep, ToolResult
from agent.prompts import (
    SYSTEM_INVESTIGATOR_PROMPT,
    TOOL_SELECTION_SYSTEM_PROMPT,
    USER_INVESTIGATION_PROMPT_TEMPLATE
)

class RiskInvestigatorAgent:
    MAX_TOOL_CALLS = 4

    def __init__(self, tools_data_path: str = "data/raw/synthetic_transactions.csv"):
        self.risk_tools = RiskTools(data_path=tools_data_path)
        self.llm_available = os.getenv("LLM_AVAILABLE", "false").lower() in ("true", "1", "yes")
        self.api_key = os.getenv("OPENAI_API_KEY", "")

        # Tool Registry
        self.TOOLS = {
            "get_customer_history": lambda cust_id, merch_id, dev_id, txn: self.risk_tools.get_customer_history(cust_id, txn),
            "get_merchant_statistics": lambda cust_id, merch_id, dev_id, txn: self.risk_tools.get_merchant_statistics(merch_id),
            "get_transaction_velocity": lambda cust_id, merch_id, dev_id, txn: self.risk_tools.get_transaction_velocity(cust_id, txn),
            "get_device_activity": lambda cust_id, merch_id, dev_id, txn: self.risk_tools.get_device_activity(dev_id, txn),
            "check_geographic_consistency": lambda cust_id, merch_id, dev_id, txn: self.risk_tools.check_geographic_consistency(cust_id, txn.get("transaction_country", "IN"), txn),
            "get_recent_related_transactions": lambda cust_id, merch_id, dev_id, txn: self.risk_tools.get_recent_related_transactions(cust_id, merch_id)
        }

    def investigate(self, txn_data: Dict[str, Any], risk_result: Dict[str, Any]) -> InvestigationReport:
        cust_id = txn_data.get("customer_id", "UNKNOWN")
        merch_id = txn_data.get("merchant_id", "UNKNOWN")
        dev_id = txn_data.get("device_id", "UNKNOWN")
        txn_id = txn_data.get("transaction_id", "TXN_UNKNOWN")

        evidence: Dict[str, Any] = {}
        steps: List[InvestigationStep] = []
        called_tools: set = set()

        # Bounded Dynamic Tool Loop
        for step_num in range(1, self.MAX_TOOL_CALLS + 1):
            tool_choice = self._plan_next_tool(txn_data, risk_result, called_tools, evidence)
            
            tool_name = tool_choice.get("tool")
            reason = tool_choice.get("reason", "Investigating risk signal")
            cont = tool_choice.get("continue_investigation", True)

            if not cont or tool_name == "stop" or not tool_name or tool_name not in self.TOOLS:
                break

            # Execute tool through registry
            tool_func = self.TOOLS[tool_name]
            tool_output = tool_func(cust_id, merch_id, dev_id, txn_data)
            
            evidence[tool_name] = tool_output
            called_tools.add(tool_name)

            step_record = InvestigationStep(
                step=step_num,
                tool_name=tool_name,
                reason=reason,
                tool_result=tool_output,
                timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
            )
            steps.append(step_record)

            # Check early stopping condition: stop if budget reached or no remaining uncalled relevant signals exist
            if self._should_stop_early(risk_result, evidence, len(called_tools), txn_data, called_tools):
                break

        # Attach investigation metadata to evidence dict for DB persistence & frontend schema mapping
        evidence["_investigation_steps"] = [s.model_dump() for s in steps]
        evidence["_tools_executed_count"] = len(steps)
        evidence["_max_tools"] = self.MAX_TOOL_CALLS

        # Generate final investigation summary and recommendation
        if self.llm_available and self.api_key:
            return self._llm_summarize(txn_id, risk_result, evidence, steps)
        else:
            return self._deterministic_summarize(txn_id, risk_result, evidence, steps)

    def _plan_next_tool(self, txn_data: Dict[str, Any], risk_result: Dict[str, Any], called_tools: set, current_evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Planner component: decides next tool or stop command."""
        signals = [s.get("signal") for s in risk_result.get("risk_signals", [])]

        if self.llm_available and self.api_key:
            llm_plan = self._llm_plan_tool(txn_data, risk_result, called_tools, current_evidence)
            if llm_plan:
                return llm_plan

        # Deterministic Signal-to-Tool Planner
        # Signal priority mapping
        if ("new_device" in signals or txn_data.get("device_new") == 1 or txn_data.get("ip_risk_score", 0) > 0.6) and "get_device_activity" not in called_tools:
            return {
                "tool": "get_device_activity",
                "reason": "Transaction flagged with new device or elevated IP risk.",
                "continue_investigation": True
            }

        if ("high_velocity" in signals or txn_data.get("transactions_last_10_minutes", 0) >= 3 or txn_data.get("velocity_score", 0) > 1.0) and "get_transaction_velocity" not in called_tools:
            return {
                "tool": "get_transaction_velocity",
                "reason": "Short-term transaction velocity spike detected.",
                "continue_investigation": True
            }

        if ("geographic_mismatch" in signals or txn_data.get("transaction_country") != txn_data.get("customer_country")) and "check_geographic_consistency" not in called_tools:
            return {
                "tool": "check_geographic_consistency",
                "reason": "Transaction location differs from customer registered home country.",
                "continue_investigation": True
            }

        if ("amount_deviation" in signals or txn_data.get("amount", 0) > 3.0 * txn_data.get("average_customer_amount", 100)) and "get_customer_history" not in called_tools:
            return {
                "tool": "get_customer_history",
                "reason": "Transaction amount is significantly higher than customer's historical average.",
                "continue_investigation": True
            }

        if (txn_data.get("merchant_risk_score", 0) > 0.3) and "get_merchant_statistics" not in called_tools:
            return {
                "tool": "get_merchant_statistics",
                "reason": "Merchant risk score is elevated.",
                "continue_investigation": True
            }

        if (txn_data.get("customer_previous_risk_count", 0) > 0) and "get_recent_related_transactions" not in called_tools:
            return {
                "tool": "get_recent_related_transactions",
                "reason": "Customer has prior risk flags; checking related merchant history.",
                "continue_investigation": True
            }

        # Fallback to uncalled tools if high risk score remains unaddressed
        available = [t for t in self.TOOLS.keys() if t not in called_tools]
        if available and risk_result.get("risk_probability", 0) >= 0.70:
            next_t = available[0]
            return {
                "tool": next_t,
                "reason": f"Corroborating high risk score ({risk_result.get('risk_probability'):.2f}) with remaining context tool.",
                "continue_investigation": True
            }

        return {"tool": "stop", "reason": "Sufficient evidence collected.", "continue_investigation": False}

    def _should_stop_early(self, risk_result: Dict[str, Any], evidence: Dict[str, Any], tools_count: int, txn_data: Dict[str, Any] = None, called_tools: set = None) -> bool:
        """Determines if investigation should stop early or continue using available budget."""
        if tools_count >= self.MAX_TOOL_CALLS:
            return True

        if txn_data and called_tools is not None:
            signals = [s.get("signal") for s in risk_result.get("risk_signals", [])]
            
            # Check if any uncalled tool is relevant to an unverified risk signal
            uncalled_relevant = False
            
            if "get_device_activity" not in called_tools and ("new_device" in signals or txn_data.get("device_new") == 1 or txn_data.get("ip_risk_score", 0) > 0.6):
                uncalled_relevant = True
            elif "get_transaction_velocity" not in called_tools and ("high_velocity" in signals or txn_data.get("transactions_last_10_minutes", 0) >= 3 or txn_data.get("velocity_score", 0) > 1.0):
                uncalled_relevant = True
            elif "check_geographic_consistency" not in called_tools and ("geographic_mismatch" in signals or txn_data.get("transaction_country") != txn_data.get("customer_country")):
                uncalled_relevant = True
            elif "get_customer_history" not in called_tools and ("amount_deviation" in signals or txn_data.get("amount", 0) > 3.0 * txn_data.get("average_customer_amount", 100)):
                uncalled_relevant = True
            elif "get_merchant_statistics" not in called_tools and (txn_data.get("merchant_risk_score", 0) > 0.3):
                uncalled_relevant = True
            elif "get_recent_related_transactions" not in called_tools and (txn_data.get("customer_previous_risk_count", 0) > 0):
                uncalled_relevant = True

            # If there are relevant uncalled tools and budget remains, do NOT stop early
            if uncalled_relevant:
                return False

        # If no relevant uncalled signals remain, stop early
        return True

    def _llm_plan_tool(self, txn_data: Dict[str, Any], risk_result: Dict[str, Any], called_tools: set, current_evidence: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            prompt = f"""
Transaction ID: {txn_data.get('transaction_id')}
Risk Score: {risk_result.get('risk_probability')}
Signals: {json.dumps(risk_result.get('risk_signals', []))}
Already Called Tools: {list(called_tools)}
Current Evidence Collected: {json.dumps(current_evidence)}
Select next tool from: {list(self.TOOLS.keys())} or 'stop'.
"""
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": TOOL_SELECTION_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            if data.get("tool") in self.TOOLS or data.get("tool") == "stop":
                return data
        except Exception:
            pass
        return None

    def _calculate_investigation_confidence(
        self,
        evidence: Dict[str, Any],
        steps: List[InvestigationStep],
        evidence_strength: str
    ) -> float:
        """Calculate reproducible confidence from verified investigation evidence."""
        executed_results = [
            step.tool_result for step in steps
            if isinstance(step.tool_result, dict)
        ]
        verified_results = []
        verified_tool_names = set()
        for step in steps:
            result = step.tool_result
            if not isinstance(result, dict):
                continue
            status = str(result.get("status", "")).upper()
            if status in {"NOT CHECKED", "NOT_AVAILABLE", "NOT AVAILABLE"}:
                continue
            if status and status != "VERIFIED":
                continue
            if result:
                verified_results.append(result)
                verified_tool_names.add(step.tool_name)

        total_tools = len(executed_results)
        if total_tools == 0:
            return 0.0

        verified_count = len(verified_results)
        verified_coverage = verified_count / self.MAX_TOOL_CALLS
        execution_quality = verified_count / total_tools
        strength_factor = {
            "LOW": 0.0,
            "MEDIUM": 0.5,
            "HIGH": 1.0,
        }.get(evidence_strength, 0.0)

        # Keep strength gated by verified coverage so unchecked tools cannot raise
        # confidence; distinct verified tools add graduated corroboration.
        execution_completeness = verified_coverage
        execution_quality = verified_count / total_tools
        corroboration = min(1.0, max(0, len(verified_tool_names) - 1) / 3.0)
        confidence = (
            0.35 * verified_coverage
            + 0.20 * (strength_factor * verified_coverage)
            + 0.20 * corroboration
            + 0.10 * execution_quality
            + 0.05 * execution_completeness
        )
        return round(max(0.0, min(1.0, confidence)), 3)

    def _calculate_evidence_strength(self, evidence: Dict[str, Any]) -> str:
        confirmed = 0
        geo = evidence.get("check_geographic_consistency", {})
        if geo.get("geographic_mismatch"):
            confirmed += 1

        vel = evidence.get("get_transaction_velocity", {})
        if vel.get("velocity_status") == "HIGH":
            confirmed += 1

        dev = evidence.get("get_device_activity", {})
        if dev.get("device_risk_level") in ["HIGH", "MEDIUM"]:
            confirmed += 1

        cust = evidence.get("get_customer_history", {})
        if cust.get("previous_risk_flags", 0) > 0:
            confirmed += 1

        merch = evidence.get("get_merchant_statistics", {})
        if merch.get("merchant_risk_score", 0) > 0.3:
            confirmed += 1

        if confirmed >= 2:
            return "HIGH"
        elif confirmed == 1:
            return "MEDIUM"
        else:
            return "LOW"

    def _deterministic_summarize(self, txn_id: str, risk_result: Dict[str, Any], evidence: Dict[str, Any], steps: List[InvestigationStep]) -> InvestigationReport:
        prob = risk_result["risk_probability"]
        signals = risk_result.get("risk_signals", [])

        summary_lines = []
        summary_lines.append(f"Automated Bounded Investigation Report for Transaction {txn_id}:")
        summary_lines.append(f"- Calculated ML Risk Score: {prob:.4f} ({risk_result['risk_level']})")
        summary_lines.append(f"- Dynamic Tools Executed ({len(steps)}/{self.MAX_TOOL_CALLS}): {', '.join([s.tool_name for s in steps])}")
        
        high_severity_count = sum(1 for s in signals if s.get("severity") == "high")
        
        geo = evidence.get("check_geographic_consistency", {})
        if geo.get("geographic_mismatch"):
            summary_lines.append(f"- Geo Mismatch Alert: Transaction in {geo.get('transaction_country')} differs from home country {geo.get('home_country')}.")

        vel = evidence.get("get_transaction_velocity", {})
        if vel.get("velocity_status") == "HIGH":
            summary_lines.append(f"- Velocity Alert: Rapid sequence of {vel.get('transactions_last_10_minutes')} transactions in last 10 minutes.")

        dev = evidence.get("get_device_activity", {})
        if dev.get("is_new_device"):
            summary_lines.append(f"- Device Alert: First-time device used ({dev.get('device_id')}) with IP risk score {dev.get('ip_risk_score')}.")

        cust = evidence.get("get_customer_history", {})
        if cust.get("previous_risk_flags", 0) > 0:
            summary_lines.append(f"- Customer History: Account has {cust.get('previous_risk_flags')} prior risk flags.")

        evidence_strength = self._calculate_evidence_strength(evidence)
        evidence["_evidence_strength"] = evidence_strength

        # Determine Recommendation
        if high_severity_count >= 2 or prob >= 0.75 or (geo.get("geographic_mismatch") and vel.get("velocity_status") == "HIGH"):
            recommended_action = "MANUAL_REVIEW"
            confidence = self._calculate_investigation_confidence(evidence, steps, evidence_strength)
            summary_lines.append("\nFinal Assessment: Multiple corroborated high-risk indicators confirmed by tools. Flagged for Manual Review.")
        else:
            recommended_action = "MONITOR"
            confidence = self._calculate_investigation_confidence(evidence, steps, evidence_strength)
            summary_lines.append("\nFinal Assessment: Moderate anomalous signals detected. Recommending enhanced monitoring.")

        return InvestigationReport(
            transaction_id=txn_id,
            risk_probability=prob,
            risk_level=risk_result["risk_level"],
            evidence=evidence,
            investigation_steps=steps,
            investigation_summary="\n".join(summary_lines),
            confidence_score=confidence,
            evidence_strength=evidence_strength,
            tools_executed_count=len(steps),
            max_tools=self.MAX_TOOL_CALLS,
            recommended_action=recommended_action,
            is_llm_generated=False
        )

    def _llm_summarize(self, txn_id: str, risk_result: Dict[str, Any], evidence: Dict[str, Any], steps: List[InvestigationStep]) -> InvestigationReport:
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            steps_json = json.dumps([s.model_dump() for s in steps])
            prompt = USER_INVESTIGATION_PROMPT_TEMPLATE.format(
                transaction_id=txn_id,
                risk_probability=risk_result["risk_probability"],
                risk_level=risk_result["risk_level"],
                risk_signals=json.dumps(risk_result.get("risk_signals", [])),
                evidence_json=json.dumps(evidence),
                steps_json=steps_json
            )

            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": SYSTEM_INVESTIGATOR_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )

            llm_summary = response.choices[0].message.content
            recommended_action = "MANUAL_REVIEW" if "MANUAL_REVIEW" in llm_summary else "MONITOR"

            evidence_strength = self._calculate_evidence_strength(evidence)
            evidence["_evidence_strength"] = evidence_strength
            confidence = self._calculate_investigation_confidence(evidence, steps, evidence_strength)

            return InvestigationReport(
                transaction_id=txn_id,
                risk_probability=risk_result["risk_probability"],
                risk_level=risk_result["risk_level"],
                evidence=evidence,
                investigation_steps=steps,
                investigation_summary=llm_summary,
                confidence_score=confidence,
                evidence_strength=evidence_strength,
                tools_executed_count=len(steps),
                max_tools=self.MAX_TOOL_CALLS,
                recommended_action=recommended_action,
                is_llm_generated=True
            )
        except Exception:
            return self._deterministic_summarize(txn_id, risk_result, evidence, steps)
