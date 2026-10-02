"""
SentinelAI - Agentic Support Connector with Guardrails & Evaluation Engine
Production-grade Streamlit Web Application & Observability Dashboard.
"""

import streamlit as st
import json
import os
import time
from typing import Dict, Any

from connector import TicketConnector
from ai_engine import AIEngine
from guardrails import GuardrailsEngine
from rate_limiter import RateLimiter
from evaluator import EvaluatorEngine
from agent import SentinelAgent

# ---------------------------------------------------------
# Page Configuration & Custom Enterprise Dark Theme CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="SentinelAI - Agentic Support Connector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
    /* Global Styling & Dark Palette */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main {
        background-color: #0b0f19;
        color: #f1f5f9;
    }

    .stApp {
        background: radial-gradient(circle at top right, #131b2e, #0b0f19 80%);
    }

    /* Enterprise Glassmorphism Cards */
    .sentinel-card {
        background: rgba(18, 26, 43, 0.75);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
    }

    .sentinel-card-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #38bdf8;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Priority Badges */
    .badge-high {
        background-color: rgba(239, 68, 68, 0.2);
        color: #fca5a5;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
    }

    .badge-medium {
        background-color: rgba(245, 158, 11, 0.2);
        color: #fcd34d;
        border: 1px solid rgba(245, 158, 11, 0.4);
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
    }

    .badge-low {
        background-color: rgba(16, 185, 129, 0.2);
        color: #6ee7b7;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
    }

    /* Alert Banner for Human Review */
    .alert-flagged {
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.25), rgba(153, 27, 27, 0.35));
        border: 1px solid #ef4444;
        border-radius: 10px;
        padding: 16px;
        color: #fecdd3;
        margin: 16px 0;
    }

    .alert-safe {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(4, 120, 87, 0.25));
        border: 1px solid #10b981;
        border-radius: 10px;
        padding: 16px;
        color: #a7f3d0;
        margin: 16px 0;
    }

    /* Metric Badges */
    .metric-container {
        display: flex;
        gap: 16px;
        margin-bottom: 20px;
    }
    
    .metric-box {
        flex: 1;
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 14px;
        text-align: center;
    }

    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #38bdf8;
    }

    .metric-label {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Code & Trace Fonts */
    .trace-step {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        background: rgba(15, 23, 42, 0.8);
        padding: 10px;
        border-left: 3px solid #38bdf8;
        border-radius: 4px;
        margin-bottom: 8px;
    }
    
    .stCodeBlock {
        border-radius: 8px !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "agent" not in st.session_state:
    st.session_state.agent = SentinelAgent()

if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{int(time.time())}"

if "current_result" not in st.session_state:
    st.session_state.current_result = None

agent: SentinelAgent = st.session_state.agent
session_id: str = st.session_state.session_id

# ---------------------------------------------------------
# Sidebar Controls
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/isometric/96/shield-protection.png", width=64)
    st.title("SentinelAI Control")
    st.caption("Agentic Support Connector v2.4 (Enterprise Edition)")
    st.markdown("---")

    # Rate Limit Status Box
    remaining_quota = agent.rate_limiter.get_remaining(session_id)
    quota_color = "#10b981" if remaining_quota > 2 else ("#f59e0b" if remaining_quota > 0 else "#ef4444")
    
    st.markdown("### ⏱️ Session Quota")
    st.markdown(
        f"""
        <div style="background: rgba(30,41,59,0.7); padding: 12px; border-radius: 8px; border: 1px solid {quota_color};">
            <span style="font-size: 1.4rem; font-weight: 700; color: {quota_color};">{remaining_quota} / 5</span>
            <span style="font-size: 0.85rem; color: #94a3b8; float: right; margin-top: 4px;">Requests Left</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("🔄 Reset Rate Limit Quota", use_container_width=True):
        agent.reset_rate_limit(session_id)
        st.session_state.current_result = None
        st.success("Session quota reset to 5 requests.")
        st.rerun()

    st.markdown("---")
    st.markdown("### 🚀 Quick Preset Ticket Tests")
    preset_tickets = [
        ("TICK-1001", "Payment Failure (High)"),
        ("TICK-1004", "Fraud Suspicion (Critical)"),
        ("TICK-1003", "Login 2FA Issue (High)"),
        ("TICK-1005", "API 500 Webhook Error (High)"),
        ("TICK-1008", "API Rate Limit 429 (High)"),
        ("TICK-1002", "Refund Delay (Medium)"),
        ("TICK-1010", "GDPR Data Export (Low)"),
    ]

    selected_preset = st.selectbox(
        "Load Sample Ticket Case:",
        options=["Select preset..."] + [f"{p[0]} - {p[1]}" for p in preset_tickets]
    )

    if selected_preset != "Select preset...":
        preset_id = selected_preset.split(" - ")[0]
        if st.button(f"⚡ Run Agent on {preset_id}", use_container_width=True):
            with st.spinner("Processing workflow pipeline..."):
                st.session_state.current_result = agent.process_query(preset_id, session_id=session_id)
            st.rerun()

    st.markdown("---")
    st.markdown("### 🛠️ Architecture Stack")
    st.markdown("- **Connector**: Local JSON Vector/Keyword API")
    st.markdown("- **Reasoning**: Cognitive Rule Engine")
    st.markdown("- **Guardrails**: Keyword & Risk Auditor")
    st.markdown("- **Evaluator**: 3-Point Quality Engine")
    st.markdown("- **Protocol**: Model Context Protocol (MCP)")

# ---------------------------------------------------------
# Top Navigation Header & System Status
# ---------------------------------------------------------
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("🛡️ SentinelAI Studio")
    st.markdown("**Enterprise Agentic Support Connector with Safety Guardrails & Observability Evaluation Engine**")

with col_h2:
    st.markdown(
        """
        <div style="text-align: right; margin-top: 10px;">
            <span style="background: rgba(16, 185, 129, 0.2); color: #6ee7b7; padding: 6px 14px; border-radius: 20px; font-weight: 600; font-size: 0.85rem; border: 1px solid #10b981;">
                🟢 SYSTEM OPERATIONAL
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# ---------------------------------------------------------
# Main Application Tabs
# ---------------------------------------------------------
tab_workbench, tab_explorer, tab_guardrails, tab_eval, tab_mcp, tab_logs = st.tabs([
    "🤖 Agent Workbench",
    "📋 Ticket Explorer",
    "🛡️ Guardrails & Safety",
    "📊 Evaluation Engine",
    "⚙️ MCP Tool Inspector",
    "📈 Observability & Logs"
])

# =========================================================
# TAB 1: AGENT WORKBENCH
# =========================================================
with tab_workbench:
    st.subheader("Interactive Agentic Workflow Execution")
    
    col_input, col_btn = st.columns([4, 1])
    with col_input:
        user_query = st.text_input(
            "Search Ticket by ID or Enter Natural Language Support Query:",
            placeholder="e.g. TICK-1001 or 'Payment failed on Razorpay checkout but amount debited'",
            key="input_query"
        )
    with col_btn:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        run_submitted = st.button("🚀 Run Agent Pipeline", use_container_width=True, type="primary")

    if run_submitted and user_query:
        with st.spinner("Executing multi-step agentic workflow..."):
            st.session_state.current_result = agent.process_query(user_query, session_id=session_id)

    res = st.session_state.current_result

    if res:
        if res.get("status") == "rate_limited":
            st.error(f"⚠️ {res['message']}")
            st.info("💡 Reset session quota in the sidebar to continue testing.")
        else:
            ticket = res.get("ticket", {})
            summary = res.get("summary", "")
            priority = res.get("priority", "Medium")
            reply = res.get("reply", "")
            flagged = res.get("flagged", False)
            guardrails_info = res.get("guardrails", {})
            eval_info = res.get("evaluation", {})

            # Top Metrics Strip
            mcol1, mcol2, mcol3, mcol4 = st.columns(4)
            with mcol1:
                st.markdown(
                    f"""
                    <div class="metric-box">
                        <div class="metric-label">Matched Ticket</div>
                        <div class="metric-value">{ticket.get('id', 'N/A')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with mcol2:
                priority_class = f"badge-{priority.lower()}"
                st.markdown(
                    f"""
                    <div class="metric-box">
                        <div class="metric-label">Assigned Priority</div>
                        <div style="margin-top:6px;"><span class="{priority_class}">{priority.upper()}</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with mcol3:
                safety_color = "#ef4444" if flagged else "#10b981"
                safety_text = "HUMAN REVIEW REQUIRED" if flagged else "CLEARED BY GUARDRAILS"
                st.markdown(
                    f"""
                    <div class="metric-box">
                        <div class="metric-label">Safety Status</div>
                        <div style="color: {safety_color}; font-weight: 700; font-size: 1.1rem; margin-top: 4px;">{safety_text}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with mcol4:
                score_val = eval_info.get('score', 0)
                st.markdown(
                    f"""
                    <div class="metric-box">
                        <div class="metric-label">Evaluation Score</div>
                        <div class="metric-value">{score_val} / 3 <span style="font-size:0.9rem; color:#94a3b8;">({eval_info.get('percentage', 0)}%)</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("<br>", unsafe_allow_html=True)

            # Left Column: Workflow Outputs | Right Column: Evaluation & Guardrails Audit
            c_left, c_right = st.columns([3, 2])

            with c_left:
                # Matched Ticket Display
                st.markdown(
                    f"""
                    <div class="sentinel-card">
                        <div class="sentinel-card-header">📋 Matched Ticket Details</div>
                        <p><strong>Customer:</strong> {ticket.get('customer_name')} | <strong>Category:</strong> {ticket.get('category')}</p>
                        <p><strong>Title:</strong> {ticket.get('title')}</p>
                        <p style="color: #cbd5e1; background: rgba(15,23,42,0.6); padding: 10px; border-radius: 6px; font-size: 0.95rem;">
                            {ticket.get('description')}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # AI Summary Section
                st.markdown(
                    f"""
                    <div class="sentinel-card">
                        <div class="sentinel-card-header">💡 AI Executive Summary (1-Line)</div>
                        <p style="font-weight: 600; color: #38bdf8; font-size: 1.05rem;">{summary}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Guardrail Safety Alert Banner (Requirements #5 & #9)
                if flagged:
                    st.markdown(
                        f"""
                        <div class="alert-flagged">
                            <h4 style="margin:0 0 8px 0;">⚠️ Human Review Required (Flagged by Guardrails)</h4>
                            <p style="margin:0;"><strong>Reason:</strong> {', '.join(guardrails_info.get('reasons', []))}</p>
                            <p style="margin:4px 0 0 0; font-size: 0.85rem; color: #fca5a5;">
                                Risk Level: <strong>{guardrails_info.get('risk_level')}</strong> | Matched Sensitive Keywords: {', '.join(guardrails_info.get('matched_keywords', []))}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        """
                        <div class="alert-safe">
                            <h4 style="margin:0 0 4px 0;">✅ Passed All Safety Guardrails</h4>
                            <p style="margin:0; font-size: 0.9rem;">No fraud or sensitive security indicators detected. Response is safe for automated dispatch.</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # Suggested Reply Card
                st.markdown("### 💬 Suggested Customer Support Reply")
                st.text_area(
                    "Generated Response Payload:",
                    value=reply,
                    height=280,
                    key="reply_text_area"
                )

            with c_right:
                # Evaluation Breakdown Card (Requirement #10)
                st.markdown("### 📊 Response Quality Scoring")
                
                det = eval_info.get("details", {})
                
                sum_metric = det.get("summary_metric", {})
                reply_metric = det.get("reply_metric", {})
                prio_metric = det.get("priority_metric", {})

                st.markdown(
                    f"""
                    <div class="sentinel-card">
                        <div class="sentinel-card-header">Score Breakdown ({eval_info.get('score')}/3 Points)</div>
                        
                        <div style="margin-bottom: 12px;">
                            <span style="font-weight:600;">1. Summary Conciseness:</span> 
                            {'✅ Pass (+1)' if sum_metric.get('passed') else '❌ Fail (+0)'}<br>
                            <span style="font-size:0.85rem; color:#94a3b8;">{sum_metric.get('reason')}</span>
                        </div>
                        
                        <div style="margin-bottom: 12px;">
                            <span style="font-weight:600;">2. Reply Completeness & Actionability:</span> 
                            {'✅ Pass (+1)' if reply_metric.get('passed') else '❌ Fail (+0)'}<br>
                            <span style="font-size:0.85rem; color:#94a3b8;">{reply_metric.get('reason')}</span>
                        </div>
                        
                        <div style="margin-bottom: 12px;">
                            <span style="font-weight:600;">3. Priority Classification Accuracy:</span> 
                            {'✅ Pass (+1)' if prio_metric.get('passed') else '❌ Fail (+0)'}<br>
                            <span style="font-size:0.85rem; color:#94a3b8;">{prio_metric.get('reason')}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Agentic Execution Timeline / Trace
                st.markdown("### ⏱️ Agent Workflow Trace")
                for trace_step in res.get("trace", []):
                    st.markdown(
                        f"""
                        <div class="trace-step">
                            <strong>{trace_step['step']}</strong> [{trace_step['duration_ms']}ms]<br>
                            <span style="color: #94a3b8;">{trace_step['details']}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

# =========================================================
# TAB 2: TICKET EXPLORER
# =========================================================
with tab_explorer:
    st.subheader("📋 Support Ticket Database Explorer")
    st.caption("Inspect available customer support tickets and dataset schema.")

    connector: TicketConnector = agent.connector
    all_tickets = connector.list_tickets()

    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        status_filter = st.selectbox("Filter Status:", ["All", "open", "pending", "closed"])
    with fcol2:
        priority_filter = st.selectbox("Filter Priority:", ["All", "High", "Medium", "Low"])
    with fcol3:
        search_kw = st.text_input("Search Keyword:", placeholder="Filter titles/desc...")

    filtered_tickets = all_tickets
    if status_filter != "All":
        filtered_tickets = [t for t in filtered_tickets if t.get("status") == status_filter]
    if priority_filter != "All":
        filtered_tickets = [t for t in filtered_tickets if t.get("priority") == priority_filter]
    if search_kw:
        filtered_tickets = [t for t in filtered_tickets if search_kw.lower() in t.get("title","").lower() or search_kw.lower() in t.get("description","").lower()]

    st.markdown(f"**Showing {len(filtered_tickets)} of {len(all_tickets)} tickets**")

    for t in filtered_tickets:
        p_class = f"badge-{t.get('priority', 'low').lower()}"
        with st.expander(f"{t['id']} — {t['title']} ({t['customer_name']})"):
            st.markdown(f"**Status:** `{t['status']}` | **Priority:** <span class='{p_class}'>{t['priority']}</span> | **Category:** `{t.get('category')}`", unsafe_allow_html=True)
            st.markdown(f"**Description:** {t['description']}")
            st.json(t)

# =========================================================
# TAB 3: GUARDRAILS & SAFETY HUB
# =========================================================
with tab_guardrails:
    st.subheader("🛡️ Safety & Guardrails Testing Hub")
    st.caption("Audits input queries and AI responses for sensitive risk terms, fraud, and security escalation criteria.")

    col_g1, col_g2 = st.columns([1, 1])

    with col_g1:
        st.markdown("#### 🧪 Safety Sandbox Tester")
        sample_input = st.text_area(
            "Test Text Payload:",
            value="We detected an unauthorized transaction attempt and suspect fraud on our payment account.",
            height=140
        )
        if st.button("Audit Text with Guardrails"):
            safety_res = agent.guardrails.evaluate_safety(sample_input, "Sample response text...")
            st.json(safety_res)

    with col_g2:
        st.markdown("#### 📜 Guardrail Policy Rules")
        st.markdown(
            f"""
            - **Sensitive Keyword Triggers:** `{', '.join(agent.guardrails.SENSITIVE_KEYWORDS)}`
            - **Human Escalation Trigger:** If sensitive keyword matches or risk level >= HIGH
            - **Empty Output Defense:** Automatic fallback to human review template
            - **Sanitization Engine:** Strips malicious script injection & unsafe html
            """
        )
        st.markdown("#### 🔄 Default Safe Fallback Template")
        st.code(agent.guardrails.SAFE_FALLBACK_REPLY, language="markdown")

# =========================================================
# TAB 4: EVALUATION & BENCHMARK ENGINE
# =========================================================
with tab_eval:
    st.subheader("📊 System-Wide Benchmark & Quality Analytics")
    st.caption("Runs evaluation engine across all 15 customer tickets to compute global response scores.")

    if st.button("⚡ Run Global Benchmark Suite Across All 15 Tickets", type="primary"):
        all_t = agent.connector.list_tickets()
        results_list = []
        total_score = 0
        max_possible = len(all_t) * 3

        for t in all_t:
            res = agent.process_query(t["id"], session_id="eval_runner")
            score = res["evaluation"]["score"]
            total_score += score
            results_list.append({
                "Ticket ID": t["id"],
                "Category": t.get("category"),
                "Priority": res["priority"],
                "Flagged": "⚠️ Yes" if res["flagged"] else "✅ No",
                "Score": f"{score}/3",
                "Percentage": f"{res['evaluation']['percentage']}%",
                "Grade": res['evaluation']['grade']
            })

        overall_pct = round((total_score / max_possible) * 100, 1)

        bcol1, bcol2, bcol3 = st.columns(3)
        with bcol1:
            st.metric("Total Tickets Evaluated", len(all_t))
        with bcol2:
            st.metric("Global Quality Score", f"{total_score} / {max_possible}")
        with bcol3:
            st.metric("Overall Accuracy Rate", f"{overall_pct}%")

        st.dataframe(results_list, use_container_width=True)

# =========================================================
# TAB 5: MCP TOOL INSPECTOR
# =========================================================
with tab_mcp:
    st.subheader("⚙️ Model Context Protocol (MCP) Tool Specification")
    st.caption("Inspect structured tool schemas defined in `mcp_tools.json`.")

    mcp_path = os.path.join(os.path.dirname(__file__), "mcp_tools.json")
    if os.path.exists(mcp_path):
        with open(mcp_path, 'r', encoding='utf-8') as f:
            tools_data = json.load(f)
        
        st.markdown(f"**Loaded {len(tools_data)} Tool Definitions:**")
        st.json(tools_data)
    else:
        st.error("`mcp_tools.json` file not found!")

# =========================================================
# TAB 6: OBSERVABILITY & LOGS
# =========================================================
with tab_logs:
    st.subheader("📈 System Logs & Session Observability")
    st.caption("Real-time runtime state, session parameters, and execution telemetry.")

    st.markdown(f"**Active Session ID:** `{session_id}`")
    st.markdown(f"**Remaining Requests Quota:** `{agent.rate_limiter.get_remaining(session_id)} / 5`")

    if st.session_state.current_result:
        st.markdown("#### Latest Agent Execution Payload")
        st.json(st.session_state.current_result)
