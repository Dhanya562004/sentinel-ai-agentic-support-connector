"""
SentinelAI - AI Reasoning Engine (Rule-based LLM Simulation)
Simulates LLM cognitive capabilities: text summarization, priority classification, and structured response generation.
"""

import re
from typing import Dict, Any, Optional

class AIEngine:
    """Simulated AI Reasoning Engine performing NLP & Rule-based cognition."""

    HIGH_PRIORITY_KEYWORDS = [
        "failed", "fraud", "urgent", "unauthorized", "hack", "breach", "locked out", 
        "500", "429", "security", "stolen", "vulnerability", "critical", "compromised", "down"
    ]

    MEDIUM_PRIORITY_KEYWORDS = [
        "delay", "issue", "latency", "pending", "corrupted", "error", "slow", 
        "timeout", "duplicate", "downgraded", "failing"
    ]

    LOW_PRIORITY_KEYWORDS = [
        "query", "general", "invoice", "discount", "pricing", "export", "gdpr", "inquiry", "seats"
    ]

    def summarize_ticket(self, text: str) -> str:
        """
        Generates a concise, 1-line executive summary from a ticket description.
        Simulates abstractive/extractive summarization rules.
        """
        if not text or not text.strip():
            return "No content provided to summarize."

        clean_text = text.strip()
        
        # Remove extra whitespace/newlines
        clean_text = re.sub(r'\s+', ' ', clean_text)
        
        # Split into sentences
        sentences = [s.strip() for s in re.split(r'[.!?]+', clean_text) if len(s.strip()) > 5]

        if not sentences:
            return clean_text[:120] + "..." if len(clean_text) > 120 else clean_text

        # Extract primary subject and core issue sentence
        first_sent = sentences[0]

        # Extract core action phrases
        if len(first_sent) <= 130:
            summary = first_sent
        else:
            # Truncate at sensible punctuation or clause
            clauses = re.split(r'[,;]\s*', first_sent)
            summary = clauses[0]
            if len(summary) < 40 and len(clauses) > 1:
                summary += f", {clauses[1]}"
            if len(summary) > 130:
                summary = summary[:127] + "..."

        # Ensure sentence ends nicely
        if not summary.endswith('.'):
            summary += '.'

        return f"Issue Summary: {summary}"

    def classify_priority(self, text: str) -> str:
        """
        Classifies priority based on semantic urgency keywords.
        Returns: 'High' | 'Medium' | 'Low'
        """
        if not text:
            return "Medium"

        text_lower = text.lower()

        high_score = sum(1 for kw in self.HIGH_PRIORITY_KEYWORDS if kw in text_lower)
        med_score = sum(1 for kw in self.MEDIUM_PRIORITY_KEYWORDS if kw in text_lower)
        low_score = sum(1 for kw in self.LOW_PRIORITY_KEYWORDS if kw in text_lower)

        if high_score > 0:
            return "High"
        elif med_score > 0:
            return "Medium"
        elif low_score > 0:
            return "Low"
        else:
            return "Medium"

    def generate_reply(
        self, 
        text: str, 
        summary: Optional[str] = None, 
        priority: Optional[str] = None, 
        ticket: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generates a professional, structured, polite, and actionable support response.
        """
        customer_name = ticket.get("customer_name", "Valued Customer") if ticket else "Valued Customer"
        ticket_id = ticket.get("id", "TICK-REF") if ticket else "TICK-REF"
        category = ticket.get("category", "Support Inquiry") if ticket else "Support Inquiry"
        
        assigned_priority = priority or self.classify_priority(text)
        text_lower = text.lower()

        greeting = f"Dear {customer_name},"
        ack = f"Thank you for contacting Sentinel Customer Support. We have logged your request under Reference Ticket ID: [{ticket_id}]."

        # Domain-specific actionable resolution generation
        if "payment" in text_lower or "debited" in text_lower or "invoice" in text_lower:
            core_action = (
                "Our billing operations team has been notified regarding your payment transaction. "
                "If funds were debited during a failed checkout, our automated reconciliation service will verify "
                "the bank settlement status within 24 hours. A refund or account balance credit will be processed automatically."
            )
            next_steps = (
                "1. Please allow 1-3 business days for bank settlement updates.\n"
                "2. If you do not see a credit reflection, share your Bank RRN / Transaction Ref Number with us.\n"
                "3. Our tier-2 finance agent will personally monitor this ticket until resolution."
            )

        elif "fraud" in text_lower or "unauthorized" in text_lower or "hack" in text_lower or "breach" in text_lower:
            core_action = (
                "⚠️ SECURITY ALERT ACKNOWLEDGMENT: We treat unauthorized access and security flags with extreme urgency. "
                "Our SecOps team has temporarily locked session tokens associated with this profile to prevent potential exploitation."
            )
            next_steps = (
                "1. Our security engineering team is auditing active IP access logs.\n"
                "2. A mandatory password reset and 2FA re-authentication challenge link has been generated.\n"
                "3. A security officer will contact you directly within 30 minutes to verify identity."
            )

        elif "login" in text_lower or "2fa" in text_lower or "otp" in text_lower:
            core_action = (
                "We understand you are experiencing access issues with 2FA / Authentication. "
                "Our Identity & Access Management system has refreshed your SMS gateway dispatch route."
            )
            next_steps = (
                "1. Please retry requesting the OTP in 3 minutes or use your time-based TOTP app.\n"
                "2. Verify that your registered phone number is clear of carrier SPAM filters.\n"
                "3. If you remain locked out, click 'Request Manual Identity Verification' in your portal."
            )

        elif "api" in text_lower or "500" in text_lower or "429" in text_lower or "webhook" in text_lower or "latency" in text_lower:
            core_action = (
                "Our Site Reliability Engineering (SRE) team is actively investigating the API / Webhook execution degradation reported."
            )
            next_steps = (
                "1. We are reviewing system metrics and error payloads on our edge infrastructure.\n"
                "2. If this relates to rate limits (HTTP 429), temporary burst allowance has been submitted for approval.\n"
                "3. Check status updates live on status.sentinelai.internal."
            )

        else:
            core_action = (
                f"We have categorized your issue under [{category}] and prioritized it as [{assigned_priority}]. "
                "Our dedicated customer success specialist is actively reviewing the request details."
            )
            next_steps = (
                "1. Your ticket has been dispatched to the domain specialist queue.\n"
                "2. Expected SLA response time for this ticket priority is under 2 hours.\n"
                "3. You can reply directly to this thread to attach supplementary screenshots or logs."
            )

        closing = (
            "We apologize for any inconvenience caused and remain committed to securing your operations.\n\n"
            "Warm regards,\n"
            "SentinelAI Agent Operations Team\n"
            "Sentinel Enterprise Support"
        )

        reply = f"{greeting}\n\n{ack}\n\n{core_action}\n\nRecommended Action Steps:\n{next_steps}\n\n{closing}"
        return reply


if __name__ == "__main__":
    engine = AIEngine()
    sample_text = "Payment failed on Razorpay checkout but $499 was debited from my HDFC bank account."
    print("Summary:", engine.summarize_ticket(sample_text))
    print("Priority:", engine.classify_priority(sample_text))
    print("Reply:\n", engine.generate_reply(sample_text))
