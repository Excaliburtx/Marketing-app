"""Streamlit dashboard: see what the agent team is doing, review reports, approve compliance items."""
import os

import pandas as pd
import plotly.express as px
import streamlit as st

from agents.compliance import submit_copy
from agents.orchestrator import BY_NAME, TEAM, run_job
from core.db import execute, read_df

st.set_page_config(page_title="Agent Team | Insurance Marketing", page_icon="🛡️", layout="wide")

# ---- simple password gate (set APP_PASSWORD in secrets). Strongly recommended: this data is sensitive.
pw = os.getenv("APP_PASSWORD")
if pw and st.session_state.get("ok") != True:
    entered = st.text_input("Password", type="password")
    if entered == pw:
        st.session_state["ok"] = True
        st.rerun()
    st.stop()

LINES = ["Pre-Need", "At-Need", "Life Insurance", "Annuity"]
RISK_ICON = {"low": "🟢", "medium": "🟡", "high": "🔴"}

st.sidebar.title("🛡️ Agent Team")
page = st.sidebar.radio("View", ["Overview", "Agent Team", "Reports", "Compliance", "Alerts & Data Quality", "Market Intel"])
if st.sidebar.button("▶ Run full pipeline now"):
    with st.spinner("Agents working..."):
        run_job("all")
    st.rerun()

leads, spend = read_df("SELECT * FROM leads"), read_df("SELECT * FROM spend")

# ------------------------------------------------------------------ Overview
if page == "Overview":
    st.title("Marketing Overview")
    if leads.empty:
        st.info("No data yet. Click **Run full pipeline now** in the sidebar to load demo data.")
        st.stop()
    leads["created_date"] = pd.to_datetime(leads["created_date"])
    spend["date"] = pd.to_datetime(spend["date"])
    c1, c2 = st.columns([2, 1])
    sel = c1.multiselect("Product line", LINES, default=LINES)
    days = c2.selectbox("Period", [7, 14, 30, 60], index=2, format_func=lambda d: f"Last {d} days")
    cutoff = leads.created_date.max() - pd.Timedelta(days=days)
    L = leads[(leads.line.isin(sel)) & (leads.created_date > cutoff)]
    S = spend[(spend.line.isin(sel)) & (spend.date > cutoff)]

    tot_spend, n = S.spend.sum(), len(L)
    issued = int(L.issued.sum())
    k = st.columns(5)
    k[0].metric("Leads", f"{n:,}")
    k[1].metric("Spend", f"${tot_spend:,.0f}")
    k[2].metric("Cost / lead", f"${tot_spend / n:,.0f}" if n else "n/a")
    k[3].metric("Policies issued", f"{issued:,}")
    k[4].metric("Cost / acquisition", f"${tot_spend / issued:,.0f}" if issued else "n/a")

    a, b = st.columns(2)
    daily = L.groupby(["created_date", "line"]).size().reset_index(name="leads")
    a.plotly_chart(px.line(daily, x="created_date", y="leads", color="line", title="Leads per day"), width="stretch")
    ch = S.groupby("channel")[["spend", "leads"]].sum().reset_index()
    ch["cpl"] = ch.spend / ch.leads
    b.plotly_chart(px.bar(ch.sort_values("cpl"), x="cpl", y="channel", orientation="h", title="Cost per lead by channel"), width="stretch")

    a, b = st.columns(2)
    f = L.groupby("line")[["appointment_set", "application", "issued"]].sum().reset_index()
    f = f.melt("line", var_name="stage", value_name="count")
    a.plotly_chart(px.bar(f, x="line", y="count", color="stage", barmode="group", title="Funnel by line"), width="stretch")
    prem = L[L.issued == 1].groupby("line").premium.sum().reset_index()
    b.plotly_chart(px.pie(prem, names="line", values="premium", title="Premium by line"), width="stretch")

# ------------------------------------------------------------------ Agent Team
elif page == "Agent Team":
    st.title("Your Agent Team")
    runs = read_df("SELECT * FROM agent_runs ORDER BY started_at DESC")
    cols = st.columns(len(TEAM))
    for col, agent in zip(cols, TEAM):
        with col:
            st.subheader(agent.name)
            st.caption(agent.role)
            last = runs[runs.agent == agent.name].head(1) if not runs.empty else pd.DataFrame()
            if last.empty:
                st.write("⚪ Never run")
            else:
                r = last.iloc[0]
                st.write(("🟢" if r.status == "success" else "🔴") + f" {r.status}")
                st.caption(f"Last run: {r.finished_at}")
                st.write(r.summary)
            if st.button("Run", key=f"run_{agent.name}"):
                with st.spinner(f"{agent.name} working..."):
                    agent.execute()
                st.rerun()
    st.divider()
    st.subheader("Run history")
    st.dataframe(runs.head(50), width="stretch", hide_index=True)

# ------------------------------------------------------------------ Reports
elif page == "Reports":
    st.title("Reports")
    rep = read_df("SELECT * FROM reports ORDER BY created_at DESC")
    if rep.empty:
        st.info("No reports yet. Run the Reporting agent.")
        st.stop()
    label = lambda r: f"{r.title}  |  {r.review_status}"
    choice = st.selectbox("Report", rep.itertuples(), format_func=label)
    if choice.compliance_risk:
        st.markdown(f"**Compliance risk:** {RISK_ICON.get(choice.compliance_risk, '')} {choice.compliance_risk}")
        with st.expander("Compliance notes"):
            st.text(choice.compliance_notes)
    st.markdown(choice.body)
    a, b, _ = st.columns([1, 1, 4])
    if a.button("✅ Approve"):
        execute("UPDATE reports SET review_status='approved' WHERE report_id=:i", {"i": choice.report_id}); st.rerun()
    if b.button("❌ Reject"):
        execute("UPDATE reports SET review_status='rejected' WHERE report_id=:i", {"i": choice.report_id}); st.rerun()
    st.download_button("Download (.md)", choice.body, file_name=f"report_{choice.report_id}.md")

# ------------------------------------------------------------------ Compliance
elif page == "Compliance":
    st.title("Compliance Review")
    st.warning("The agent flags risky language using a starter rule set. It does **not** approve anything: "
               "a licensed human must make the final call. Have your compliance officer extend the rules in agents/compliance.py.")
    with st.form("copy"):
        txt = st.text_area("Paste marketing copy (ad, email, mailer, script) to review", height=140)
        line = st.selectbox("Product line", ["", *LINES])
        if st.form_submit_button("Submit for review") and txt.strip():
            submit_copy(txt, line)
            BY_NAME["Compliance Review"].execute()
            st.rerun()
    items = read_df("SELECT * FROM content_reviews ORDER BY submitted_at DESC")
    for it in items.itertuples():
        with st.container(border=True):
            st.markdown(f"{RISK_ICON.get(it.risk, '⚪')} **{it.risk or 'pending'} risk** · {it.line or 'no line'} · _{it.review_status}_")
            st.write(it.text)
            if it.findings:
                st.text(it.findings)
            a, b, _ = st.columns([1, 1, 5])
            if a.button("Approve", key=f"a{it.item_id}"):
                execute("UPDATE content_reviews SET review_status='approved' WHERE item_id=:i", {"i": it.item_id}); st.rerun()
            if b.button("Reject", key=f"r{it.item_id}"):
                execute("UPDATE content_reviews SET review_status='rejected' WHERE item_id=:i", {"i": it.item_id}); st.rerun()

# ------------------------------------------------------------------ Alerts & Data Quality
elif page == "Alerts & Data Quality":
    st.title("Alerts & Data Quality")
    st.subheader("Cost anomalies")
    al = read_df("SELECT * FROM alerts")
    if al.empty:
        st.success("No anomalies detected.")
    for r in al.itertuples():
        (st.error if r.severity == "high" else st.warning)(r.message)
    st.subheader("Data quality issues (latest run)")
    dq = read_df("SELECT * FROM dq_issues ORDER BY checked_at DESC")
    if not dq.empty:
        st.dataframe(dq[dq.checked_at == dq.checked_at.max()], width="stretch", hide_index=True)

# ------------------------------------------------------------------ Market Intel
else:
    st.title("Market Intelligence")
    mi = read_df("SELECT * FROM market_intel ORDER BY created_at DESC")
    if mi.empty:
        st.info("No briefs yet. Add ANTHROPIC_API_KEY and run the Market Intelligence agent.")
    for r in mi.head(12).itertuples():
        with st.expander(f"{r.topic} · {r.created_at}", expanded=r.Index < 3):
            st.markdown(r.summary)
