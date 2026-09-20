"""Reporting Agent: computes KPIs by product line, detects anomalies, writes the narrative."""
from datetime import datetime, timedelta

import pandas as pd

from agents.base import BaseAgent
from core.db import read_df, write_df
from core.llm import ask_claude

SYSTEM = (
    "You are a marketing analyst for a company selling pre-need funeral insurance, at-need funeral services, "
    "life insurance and annuities. Write a concise weekly performance summary for the marketing team using ONLY "
    "the numbers provided. Cover: what changed, likely why, and 3 specific actions. Do not make product claims, "
    "rate promises, or performance guarantees. Use plain markdown."
)


def kpis_by_line(leads: pd.DataFrame, spend: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    l = leads[(leads.created_date > start) & (leads.created_date <= end)]
    s = spend[(spend.date > start) & (spend.date <= end)]
    g = l.groupby("line").agg(leads=("lead_id", "count"), appointments=("appointment_set", "sum"),
                              applications=("application", "sum"), issued=("issued", "sum"),
                              premium=("premium", "sum"))
    g["spend"] = s.groupby("line")["spend"].sum()
    g["cpl"] = g["spend"] / g["leads"]
    g["cpa"] = g["spend"] / g["issued"].replace(0, pd.NA)
    g["appt_rate"] = g["appointments"] / g["leads"]
    g["app_rate"] = g["applications"] / g["leads"]
    return g.reset_index()


def cpl_alerts(spend: pd.DataFrame, anchor: str, threshold: float = 0.30) -> pd.DataFrame:
    a = datetime.fromisoformat(anchor)
    d7, d14 = (a - timedelta(days=7)).date().isoformat(), (a - timedelta(days=14)).date().isoformat()
    cur = spend[spend.date > d7].groupby(["line", "channel"])[["spend", "leads"]].sum()
    prev = spend[(spend.date > d14) & (spend.date <= d7)].groupby(["line", "channel"])[["spend", "leads"]].sum()
    m = cur.join(prev, lsuffix="_cur", rsuffix="_prev").dropna()
    m["cpl_cur"] = m.spend_cur / m.leads_cur
    m["cpl_prev"] = m.spend_prev / m.leads_prev
    m["change"] = m.cpl_cur / m.cpl_prev - 1
    hot = m[(m.change > threshold) & (m.leads_cur >= 5)].reset_index()
    rows = [{"created_at": datetime.now().isoformat(timespec="seconds"), "severity": "high" if r.change > 0.6 else "medium",
             "message": f"{r.line} / {r.channel}: cost per lead up {r.change:.0%} week over week "
                        f"(${r.cpl_prev:,.0f} to ${r.cpl_cur:,.0f}). Review targeting, creative and bids."}
            for r in hot.itertuples()]
    return pd.DataFrame(rows)


def fmt_table(df: pd.DataFrame) -> str:
    out = ["| Line | Leads | Spend | CPL | Appt % | Issued | CPA | Premium |", "|---|---|---|---|---|---|---|---|"]
    for r in df.itertuples():
        cpa = f"${r.cpa:,.0f}" if pd.notna(r.cpa) else "n/a"
        out.append(f"| {r.line} | {r.leads} | ${r.spend:,.0f} | ${r.cpl:,.0f} | {r.appt_rate:.0%} | {r.issued} | {cpa} | ${r.premium:,.0f} |")
    return "\n".join(out)


def fallback_narrative(cur: pd.DataFrame, prev: pd.DataFrame, alerts: pd.DataFrame) -> str:
    m = cur.merge(prev[["line", "leads", "cpl"]], on="line", suffixes=("", "_prev"))
    lines = ["**What changed**"]
    for r in m.itertuples():
        d = (r.leads / r.leads_prev - 1) if r.leads_prev else 0
        lines.append(f"- {r.line}: leads {d:+.0%} vs prior week, CPL ${r.cpl:,.0f} (was ${r.cpl_prev:,.0f}).")
    lines.append("\n**Watch list**")
    lines += [f"- {a.message}" for a in alerts.itertuples()] if len(alerts) else ["- No cost anomalies detected."]
    lines.append("\n*Add ANTHROPIC_API_KEY to get Claude-written analysis and recommendations.*")
    return "\n".join(lines)


class ReportingAgent(BaseAgent):
    name = "Reporting"
    role = "Calculates KPIs by product line, detects cost anomalies, and writes the weekly narrative."

    def run(self) -> str:
        leads, spend = read_df("SELECT * FROM leads"), read_df("SELECT * FROM spend")
        if leads.empty or spend.empty:
            return "No clean data yet"
        anchor = leads.created_date.max()
        a = datetime.fromisoformat(anchor)
        d0 = anchor
        d7 = (a - timedelta(days=7)).date().isoformat()
        d14 = (a - timedelta(days=14)).date().isoformat()
        cur, prev = kpis_by_line(leads, spend, d7, d0), kpis_by_line(leads, spend, d14, d7)
        alerts = cpl_alerts(spend, anchor)
        write_df(alerts if len(alerts) else pd.DataFrame(columns=["created_at", "severity", "message"]), "alerts", mode="replace")

        prompt = (f"Week ending {anchor}.\n\nThis week:\n{cur.round(2).to_string(index=False)}\n\n"
                  f"Prior week:\n{prev.round(2).to_string(index=False)}\n\nAnomalies:\n"
                  f"{alerts.message.to_string(index=False) if len(alerts) else 'none'}")
        narrative = ask_claude(SYSTEM, prompt) or fallback_narrative(cur, prev, alerts)

        body = f"## Weekly Marketing Report: week ending {anchor}\n\n{fmt_table(cur)}\n\n{narrative}"
        now = datetime.now()
        write_df(pd.DataFrame([{
            "report_id": now.strftime("%Y%m%d%H%M%S"), "created_at": now.isoformat(timespec="seconds"),
            "title": f"Weekly Marketing Report ({anchor})", "body": body,
            "review_status": "pending", "compliance_risk": None, "compliance_notes": None,
        }]), "reports")
        return f"Report generated; {len(alerts)} cost alert(s)"
