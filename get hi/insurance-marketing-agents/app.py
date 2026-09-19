"""
Insurance Marketing Agents - Streamlit Web Interface
Run locally:  streamlit run app.py
Deploy online: Streamlit Community Cloud or Hugging Face Spaces
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Project root on path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

load_dotenv()

from src.config.settings import settings
from src.agents.crew import InsuranceMarketingCrew

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Insurance Marketing Agents",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def ensure_dirs():
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.reports_dir.mkdir(parents=True, exist_ok=True)


def list_recent_reports(limit: int = 10):
    if not settings.reports_dir.exists():
        return []
    files = sorted(settings.reports_dir.glob("*.md"), reverse=True)
    return files[:limit]


def run_crew(product_line: str, user_request: str) -> str:
    """Execute the multi-agent crew and return the final result as string."""
    inputs = {
        "product_line": product_line,
        "user_request": user_request,
    }
    crew = InsuranceMarketingCrew().crew()
    result = crew.kickoff(inputs=inputs)
    return str(result)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("📊 Insurance Marketing Agents")
    st.markdown("---")
    st.markdown(
        """
        **Product lines supported**
        - Pre-need
        - At-need
        - Annuities
        """
    )
    st.markdown("---")
    st.markdown("### How it works")
    st.markdown(
        """
        1. Data Collector gathers context  
        2. Market Researcher builds brief  
        3. Analyst finds opportunities  
        4. Report Writer creates the report  
        5. Compliance Reviewer checks language  
        """
    )
    st.markdown("---")
    st.caption("Built with CrewAI • For internal marketing use")
    st.caption("Always have compliance review final output before external use.")


# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------
st.header("Generate Marketing Report")
st.markdown(
    "Create structured, compliance-aware marketing reports for "
    "**Pre-need**, **At-need**, and **Annuities**."
)

col1, col2 = st.columns([1, 2])

with col1:
    product_line = st.selectbox(
        "Product Line",
        options=["annuities", "pre-need", "at-need", "all"],
        index=0,
        help="Choose the product focus for this report",
    )

with col2:
    default_request = {
        "annuities": "Current market overview, key distribution channels, competitive rate environment, and top 3 marketing opportunities for independent agents and advisors.",
        "pre-need": "Market size signals, funeral-home channel dynamics, competitive landscape, and marketing opportunities for pre-need life insurance.",
        "at-need": "Lead sources, average case characteristics, messaging considerations, and opportunities in the final-expense / at-need market.",
        "all": "High-level overview across Pre-need, At-need, and Annuities with cross-sell and channel insights.",
    }
    user_request = st.text_area(
        "What should the agents focus on?",
        value=default_request.get(product_line, default_request["annuities"]),
        height=120,
        help="Describe the report you need. Be as specific as you like.",
    )

# API key check (works with .env locally and Streamlit Secrets in the cloud)
api_key_present = bool(
    os.getenv("OPENAI_API_KEY")
    or os.getenv("ANTHROPIC_API_KEY")
    or (hasattr(st, "secrets") and (st.secrets.get("OPENAI_API_KEY") or st.secrets.get("ANTHROPIC_API_KEY")))
)
if not api_key_present:
    st.warning(
        "⚠️ No LLM API key detected.\n\n"
        "**On Streamlit Cloud:** Go to your app → ⋮ menu → Settings → Secrets "
        "and add:\n\n"
        "```toml\nOPENAI_API_KEY = \"sk-...\"\n```\n\n"
        "Then reboot the app."
    )

run_button = st.button(
    "🚀 Generate Report",
    type="primary",
    disabled=not user_request.strip() or not api_key_present,
    use_container_width=False,
)

# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------
if run_button:
    ensure_dirs()
    with st.spinner("Agents are working… This usually takes 1–3 minutes."):
        try:
            result = run_crew(product_line=product_line, user_request=user_request.strip())
            st.success("Report generated successfully.")
            st.markdown("### Final Output")
            st.markdown(result)

            # Offer download of the latest report file if one was saved
            recent = list_recent_reports(1)
            if recent:
                latest = recent[0]
                st.download_button(
                    label="⬇️ Download latest report (Markdown)",
                    data=latest.read_text(encoding="utf-8"),
                    file_name=latest.name,
                    mime="text/markdown",
                )
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            st.exception(e)

# ---------------------------------------------------------------------------
# Recent reports section
# ---------------------------------------------------------------------------
st.markdown("---")
st.subheader("Recent Reports")

reports = list_recent_reports(8)
if not reports:
    st.info("No reports generated yet. Create your first one above.")
else:
    for r in reports:
        with st.expander(f"📄 {r.name}"):
            content = r.read_text(encoding="utf-8")
            st.markdown(content)
            st.download_button(
                label="Download",
                data=content,
                file_name=r.name,
                mime="text/markdown",
                key=f"dl_{r.name}",
            )
