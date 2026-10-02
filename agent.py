"""
SentinelAI - Agent Core Orchestration Pipeline
Coordinates data retrieval, AI reasoning, safety guardrails, rate limiting, and output evaluation.
"""

import time
from typing import Dict, Any, Optional, List
from connector import TicketConnector
from ai_engine import AIEngine
from guardrails import GuardrailsEngine
from rate_limiter import RateLimiter
from evaluator import EvaluatorEngine

class SentinelAgent:
    """Enterprise AI Agent Orchestrator managing end-to-end agentic workflows."""

    def __init__(self):
        self.connector = TicketConnector()
        self.ai_engine = AIEngine()
        self.guardrails = GuardrailsEngine()
        self.rate_limiter = RateLimiter(max_requests=5)
        self.evaluator = EvaluatorEngine()

    def process_query(self, query_or_id: str, session_id: str = "default") -> Dict[str, Any]:
        """
        Executes the full agentic workflow pipeline:
        1. Check Rate Limiter
        2. Tool Call: Search or Get Ticket
        3. AI Reasoning: Summarize
        4. AI Reasoning: Classify Priority
        5. AI Reasoning: Generate Reply
        6. Guardrails: Safety & Risk Validation
        7. Evaluator: Quality Scoring (X/3)
        8. Return Structured Result & Observability Trace
        """
        trace: List[Dict[str, Any]] = []
        start_time = time.time()

        # Step 1: Rate Limit Verification
        allowed, rate_msg, remaining = self.rate_limiter.is_allowed(session_id)
        trace.append({
            "step": "1. Rate Limiter Audit",
            "status": "PASS" if allowed else "BLOCKED",
            "duration_ms": round((time.time() - start_time) * 1000, 2),
            "details": f"Allowed: {allowed} | Remaining Session Quota: {remaining}/5"
        })

        if not allowed:
            return {
                "status": "rate_limited",
                "message": rate_msg,
                "remaining_quota": 0,
                "ticket": None,
                "summary": "N/A - Rate Limit Exceeded",
                "priority": "N/A",
                "reply": rate_msg,
                "flagged": True,
                "guardrails": {"requires_human_review": True, "reasons": [rate_msg]},
                "evaluation": {"score": 0, "max_score": 3, "percentage": 0, "grade": "N/A"},
                "trace": trace
            }

        # Record valid request usage
        self.rate_limiter.record_request(session_id)

        # Step 2: Data Connector Retrieval (Search / Lookup)
        step2_start = time.time()
        clean_input = query_or_id.strip() if query_or_id else ""
        
        # Check if input is exact ticket ID first
        target_ticket = self.connector.get_ticket(clean_input)
        if not target_ticket:
            search_results = self.connector.search_tickets(clean_input)
            if search_results:
                target_ticket = search_results[0]

        if not target_ticket:
            # Fallback mock ticket if no direct match found
            target_ticket = {
                "id": "TICK-CUSTOM",
                "customer_name": "Portal User",
                "title": "Ad-hoc User Support Query",
                "description": clean_input or "General support request",
                "status": "open",
                "priority": "Medium",
                "category": "General Inquiry",
                "created_at": "Just now"
            }
            retrieval_mode = "Generated dynamic query payload"
        else:
            retrieval_mode = f"Matched Ticket {target_ticket['id']} via search"

        trace.append({
            "step": "2. Data Connector Search",
            "status": "SUCCESS",
            "duration_ms": round((time.time() - step2_start) * 1000, 2),
            "details": f"{retrieval_mode} | Title: '{target_ticket['title']}'"
        })

        # Step 3: AI Summarization
        step3_start = time.time()
        summary = self.ai_engine.summarize_ticket(target_ticket.get("description", ""))
        trace.append({
            "step": "3. AI Reasoning: Summarization",
            "status": "SUCCESS",
            "duration_ms": round((time.time() - step3_start) * 1000, 2),
            "details": summary
        })

        # Step 4: AI Priority Classification
        step4_start = time.time()
        priority = self.ai_engine.classify_priority(target_ticket.get("description", ""))
        trace.append({
            "step": "4. AI Reasoning: Priority Classification",
            "status": "SUCCESS",
            "duration_ms": round((time.time() - step4_start) * 1000, 2),
            "details": f"Classified Priority: {priority}"
        })

        # Step 5: AI Reply Generation
        step5_start = time.time()
        raw_reply = self.ai_engine.generate_reply(
            text=target_ticket.get("description", ""),
            summary=summary,
            priority=priority,
            ticket=target_ticket
        )
        trace.append({
            "step": "5. AI Reasoning: Reply Generation",
            "status": "SUCCESS",
            "duration_ms": round((time.time() - step5_start) * 1000, 2),
            "details": f"Generated reply length: {len(raw_reply)} chars"
        })

        # Step 6: Guardrails & Safety Validation
        step6_start = time.time()
        safety_report = self.guardrails.evaluate_safety(
            query_text=target_ticket.get("description", ""),
            reply_text=raw_reply
        )
        final_reply = safety_report["sanitized_reply"]
        flagged = safety_report["flagged"]
        trace.append({
            "step": "6. Guardrails Audit & Safety Check",
            "status": "FLAGGED" if flagged else "CLEARED",
            "duration_ms": round((time.time() - step6_start) * 1000, 2),
            "details": f"Flagged: {flagged} | Risk: {safety_report['risk_level']} | Reasons: {', '.join(safety_report['reasons'])}"
        })

        # Step 7: Evaluation Engine Scoring
        step7_start = time.time()
        eval_report = self.evaluator.evaluate_response(
            ticket=target_ticket,
            summary=summary,
            priority=priority,
            reply=final_reply
        )
        trace.append({
            "step": "7. Evaluation Engine Scoring",
            "status": "COMPLETED",
            "duration_ms": round((time.time() - step7_start) * 1000, 2),
            "details": f"Score: {eval_report['score']}/{eval_report['max_score']} ({eval_report['percentage']}%) | Grade: {eval_report['grade']}"
        })

        total_time_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "status": "success",
            "session_id": session_id,
            "total_execution_ms": total_time_ms,
            "remaining_quota": remaining - 1,
            "ticket": target_ticket,
            "summary": summary,
            "priority": priority,
            "reply": final_reply,
            "flagged": flagged,
            "guardrails": safety_report,
            "evaluation": eval_report,
            "trace": trace
        }

    def reset_rate_limit(self, session_id: str = "default"):
        """Resets the rate limit counter for a session."""
        self.rate_limiter.reset_limit(session_id)


if __name__ == "__main__":
    agent = SentinelAgent()
    print("Testing Sentinel Agent Orchestrator...")
    res = agent.process_query("TICK-1001", session_id="test_runner")
    print(f"Status: {res['status']} | Flagged: {res['flagged']} | Score: {res['evaluation']['score']}/3")
    print("Summary:", res['summary'])
    print("Priority:", res['priority'])
