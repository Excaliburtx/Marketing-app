"""
Insurance Marketing Report Generator (Lightweight Online Version)
Works reliably on Streamlit Community Cloud.
"""

import os
from datetime import datetime

import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="Insurance Marketing Agents",
    page_icon="📊",
    layout="wide",
)

with st.sidebar:
    st.title("📊 Insurance Marketing")
    st.markdown("---")
    st.markdown(
        """
        **Supported products**
        - Pre-need Life Insurance  
        - At-need / Final Expense  
        - Annuities  
        """
    )
    st.markdown("---")
    st.caption("Lightweight online version")
    st.caption("Always have compliance review final output before external use.")

st.header("Generate Marketing Report")
st.markdown(
    "Create structured marketing reports for **Pre-need**, **At-need**, and **Annuities**."
)

col1, col2 = st.columns([1, 2])

with col1:
    product_line = st.selectbox(
        "Product Line",
        options=["Annuities", "Pre-need", "At-need", "All three"],
        index=0,
    )

with col2:
    defaults = {
        "Annuities": "Current market overview, key distribution channels, competitive environment, and top 3 marketing opportunities for independent agents and advisors.",
        "Pre-need": "Market size signals, funeral-home channel dynamics, competitive landscape, and marketing opportunities for pre-need life insurance.",
        "At-need": "Lead sources, average case characteristics, messaging considerations, and opportunities in the final-expense / at-need market.",
        "All three": "High-level overview across Pre-need, At-need, and Annuities with cross-sell and channel insights.",
    }
    user_request = st.text_area(
        "What should the report focus on?",
        value=defaults.get(product_line, defaults["Annuities"]),
        height=120,
    )

api_key = None
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
elif os.getenv("OPENAI_API_KEY"):
    api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.warning(
        "⚠️ No OpenAI API key found.\n\n"
        "Go to your app → ⋮ menu → **Settings → Secrets** and add:\n\n"
        "```toml\nOPENAI_API_KEY = \"sk-...\"\n```\n\n"
        "Then reboot the app."
    )

run_button = st.button(
    "🚀 Generate Report",
    type="primary",
    disabled=not user_request.strip() or not api_key,
)

if run_button and api_key:
    client = OpenAI(api_key=api_key)

    system_prompt = f"""You are an expert marketing strategist specializing in life insurance and annuities.
You create clear, professional, compliance-aware marketing reports for:
- Pre-need life insurance
- At-need / final expense
- Annuities

Rules:
- Be factual and practical.
- Never invent specific premium rates or sales numbers. Use qualitative language or note when data would need verification.
- Avoid absolute guarantees or "risk-free" language.
- Structure every report with clear headings.
- End with actionable recommendations and a short compliance note.
"""

    user_prompt = f"""Create a professional marketing report.

Product focus: {product_line}
Specific request: {user_request}

Required structure:
1. Executive Summary
2. Market & Product Overview
3. Key Insights
4. Distribution & Channel Observations
5. Opportunities & Recommendations
6. Compliance Notes / Caveats
7. Suggested Next Steps

Write in clean Markdown. Keep the tone professional and useful for a marketing or distribution leader.
"""

    with st.spinner("Generating report… (usually 20–60 seconds)"):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.4,
            )
            report = response.choices[0].message.content

            st.success("Report generated successfully.")
            st.markdown("---")
            st.markdown(report)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = f"{product_line.lower().replace(' ', '_')}_report_{timestamp}.md"
            st.download_button(
                label="⬇️ Download Report (Markdown)",
                data=report,
                file_name=filename,
                mime="text/markdown",
            )

        except Exception as e:
            st.error(f"Error generating report: {e}")

st.markdown("---")
st.caption(
    "This is the lightweight online version. "
    "The full multi-agent CrewAI version is available for local use."
)
