"""
SentinelAI - Guardrails & Reliability Engineering Layer
Ensures AI agent safety, validates model outputs, detects high-risk sensitive topics, and manages human-in-the-loop escalations.
"""

from typing import Dict, Any, List, Optional

class GuardrailsEngine:
    """Safety and Guardrails engine to audit inputs, outputs, and trigger human review when necessary."""

    SENSITIVE_KEYWORDS: List[str] = [
        "fraud", "payment failed", "unauthorized", "hack", 
        "breach", "security vulnerability", "stolen card", "compromised",
        "payout freeze", "exploit", "leak"
    ]

    SAFE_FALLBACK_REPLY: str = (
        "Dear Valued Customer,\n\n"
        "Thank you for reaching out to Sentinel Support. Your ticket contains sensitive operational or security "
        "concerns that require direct oversight. Our automated agent has safely flagged this request for direct human "
        "review by our Senior Support Specialist.\n\n"
        "A human specialist has been assigned and will contact you directly within 15 minutes.\n\n"
        "Best regards,\n"
        "Sentinel AI Safety & Operations Engine"
    )

    def evaluate_safety(self, query_text: str, reply_text: str) -> Dict[str, Any]:
        """
        Audits input text and generated reply against enterprise safety guardrails.
        
        Returns structured dict:
        {
            "flagged": bool,
            "reasons": List[str],
            "requires_human_review": bool,
            "risk_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
            "sanitized_reply": str
        }
        """
        combined_text = f"{query_text or ''} {reply_text or ''}".lower()
        reasons = []
        flagged = False
        requires_human_review = False
        risk_level = "LOW"

        # 1. Sensitive Keyword Detection
        matched_keywords = [kw for kw in self.SENSITIVE_KEYWORDS if kw in combined_text]
        if matched_keywords:
            flagged = True
            requires_human_review = True
            reasons.append(f"Detected sensitive keyword(s): {', '.join(matched_keywords)}")
            risk_level = "CRITICAL" if any(k in ["fraud", "unauthorized", "hack", "breach"] for k in matched_keywords) else "HIGH"

        # 2. Empty / Malformed Output Check
        if not reply_text or len(reply_text.strip()) < 20:
            flagged = True
            reasons.append("Generated response was empty or too short.")
            reply_text = self.SAFE_FALLBACK_REPLY

        # 3. Profanity / Inappropriate Content Check (Simulated)
        toxic_terms = ["idiot", "scam", "stupid", "garbage", "trash"]
        if any(term in combined_text for term in toxic_terms):
            flagged = True
            requires_human_review = True
            reasons.append("Potential toxic or unprofessional language pattern detected.")
            if risk_level not in ["HIGH", "CRITICAL"]:
                risk_level = "MEDIUM"

        sanitized_reply = reply_text if reply_text else self.SAFE_FALLBACK_REPLY

        return {
            "flagged": flagged,
            "reasons": reasons if reasons else ["Passed all safety checks."],
            "requires_human_review": requires_human_review,
            "risk_level": risk_level,
            "sanitized_reply": sanitized_reply,
            "matched_keywords": matched_keywords
        }


if __name__ == "__main__":
    guardrails = GuardrailsEngine()
    test_res = guardrails.evaluate_safety("Suspected fraud on payment gateway", "Here is your response...")
    print("Guardrails Test Output:")
    print(test_res)
