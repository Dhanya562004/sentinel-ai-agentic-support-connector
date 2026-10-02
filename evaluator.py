"""
SentinelAI - Evaluation & Observability Engine
Evaluates AI agent response quality across 3 enterprise scoring metrics.
"""

from typing import Dict, Any, Optional

class EvaluatorEngine:
    """Evaluates agent response quality, length, actionability, and classification accuracy."""

    def evaluate_response(
        self,
        ticket: Optional[Dict[str, Any]],
        summary: str,
        priority: str,
        reply: str
    ) -> Dict[str, Any]:
        """
        Evaluates the generated response against 3 criteria:
        1. Summary Conciseness & Structure (+1)
        2. Reply Completeness & Actionability (+1)
        3. Priority Classification Alignment (+1)
        
        Returns score dict: { "score": int, "max_score": 3, "details": dict }
        """
        score = 0
        details = {}

        # 1. Summary Metric Evaluation
        # Summary should be non-empty, start with or contain concise info, and be <= 150 chars
        summary_len = len(summary.strip()) if summary else 0
        if 15 <= summary_len <= 160:
            summary_passed = True
            summary_reason = f"Concise 1-line summary generated ({summary_len} chars)."
            score += 1
        elif summary_len > 160:
            summary_passed = False
            summary_reason = f"Summary exceeds 160 characters length threshold ({summary_len} chars)."
        else:
            summary_passed = False
            summary_reason = "Summary is too short or empty."

        details["summary_metric"] = {
            "passed": summary_passed,
            "score": 1 if summary_passed else 0,
            "reason": summary_reason
        }

        # 2. Reply Completeness Evaluation
        # Reply must contain greeting, action steps, and polite closing
        reply_lower = reply.lower() if reply else ""
        has_greeting = any(g in reply_lower for g in ["dear", "hello", "hi", "thank you"])
        has_actions = any(a in reply_lower for a in ["action steps", "1.", "next steps", "please", "verify"])
        has_closing = any(c in reply_lower for c in ["regards", "sentinel", "sincerely", "support team"])

        if has_greeting and has_actions and has_closing and len(reply) >= 120:
            reply_passed = True
            reply_reason = "Reply contains greeting, structured actionable steps, and formal closing."
            score += 1
        else:
            missing_parts = []
            if not has_greeting: missing_parts.append("greeting")
            if not has_actions: missing_parts.append("action steps")
            if not has_closing: missing_parts.append("closing signature")
            reply_passed = False
            reply_reason = f"Reply incomplete. Missing: {', '.join(missing_parts)}."

        details["reply_metric"] = {
            "passed": reply_passed,
            "score": 1 if reply_passed else 0,
            "reason": reply_reason
        }

        # 3. Priority Classification Alignment Evaluation
        # Checks if classified priority matches expected rules from ticket text
        ticket_desc = (ticket.get("description", "") + " " + ticket.get("title", "")).lower() if ticket else ""
        
        expected_priority = "Medium"
        if any(kw in ticket_desc for kw in ["failed", "fraud", "unauthorized", "hack", "500", "429", "urgent", "breach"]):
            expected_priority = "High"
        elif any(kw in ticket_desc for kw in ["query", "general", "invoice", "discount", "gdpr", "inquiry"]):
            expected_priority = "Low"

        if priority.lower() == expected_priority.lower():
            priority_passed = True
            priority_reason = f"Priority '{priority}' perfectly aligns with rule-based expectations ('{expected_priority}')."
            score += 1
        else:
            priority_passed = False
            priority_reason = f"Priority '{priority}' mismatched expected rule priority '{expected_priority}'."

        details["priority_metric"] = {
            "passed": priority_passed,
            "score": 1 if priority_passed else 0,
            "reason": priority_reason
        }

        percentage = round((score / 3.0) * 100, 1)
        grade = "EXCELLENT" if score == 3 else ("GOOD" if score == 2 else "NEEDS_IMPROVEMENT")

        return {
            "score": score,
            "max_score": 3,
            "percentage": percentage,
            "grade": grade,
            "details": details
        }


if __name__ == "__main__":
    evaluator = EvaluatorEngine()
    res = evaluator.evaluate_response(
        ticket={"title": "Payment failed", "description": "Payment failed on Razorpay"},
        summary="Issue Summary: Payment transaction failed at checkout.",
        priority="High",
        reply="Dear Rahul,\n\nThank you for contacting support...\n\nRecommended Action Steps:\n1. Check bank statement.\n\nWarm regards,\nSentinel Support"
    )
    print("Evaluation Result Score:", f"{res['score']}/{res['max_score']}")
    print(res)
