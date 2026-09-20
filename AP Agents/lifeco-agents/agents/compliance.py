"""Compliance Review Agent. Flags risky language and ROUTES TO A HUMAN. It never auto-approves.

IMPORTANT: these rules are a starting checklist, not legal advice. Have your compliance officer
review and extend them (state DOI rules, NAIC best-interest, FINRA 2210 for securities products,
TCPA, state pre-need statutes).
"""
import re
from datetime import datetime

import pandas as pd

from agents.base import BaseAgent
from core.db import execute, read_df, write_df
from core.llm import ask_claude

# (regex, severity, message)
RULES = [
    (r"\bguarantee[ds]?\b", "high", "Uses 'guarantee'. Must be tied to insurer claims-paying ability and specific contract terms."),
    (r"\brisk[- ]free\b|\bno risk\b|\bcan'?t lose\b", "high", "Risk-free / can't-lose claims are not permitted."),
    (r"\b(best|highest|top)[- ](rate|rates|return|returns|annuity)\b", "high", "Superlative rate claim needs substantiation and as-of date."),
    (r"\b\d+(\.\d+)?\s?%\s*(return|returns|interest|yield|growth)", "high", "Specific rate/return figure needs as-of date, conditions and disclosures."),
    (r"\bno (cost|fees?)\b|\bfree (quote|review|consultation)\b", "medium", "'Free / no cost' claims need clarification of any obligations."),
    (r"\b(act now|limited time|last chance|don'?t wait)\b", "medium", "High-pressure urgency language; review against UDAP and state rules."),
    (r"\b(testimonial|customer said|one client)\b", "medium", "Testimonials require substantiation and disclosure."),
    (r"\bmedicare\b|\bsocial security\b", "medium", "Government program references can imply affiliation; add non-affiliation disclaimer."),
    (r"\b(tax[- ]free|avoid taxes?)\b", "high", "Tax claims must be accurate and are usually not appropriate in marketing; refer to a tax advisor."),
    (r"\bfdic\b|\bbank\b", "medium", "Do not imply insurance products are bank products or FDIC insured."),
]


def check_text(text: str, line: str = "", disclosures: bool = True) -> tuple[str, list[str]]:
    """disclosures=False for internal reports (skips customer-facing disclosure checks)."""
    t = text.lower()
    findings, worst = [], "low"
    rank = {"low": 0, "medium": 1, "high": 2}
    for pattern, sev, msg in RULES:
        if re.search(pattern, t):
            findings.append(f"[{sev.upper()}] {msg}")
            worst = sev if rank[sev] > rank[worst] else worst
    if not disclosures:
        return worst, findings
    is_annuity = "annuit" in t or line == "Annuity"
    is_preneed = "pre-need" in t or "preneed" in t or "pre need" in t or line == "Pre-Need"
    if is_annuity and not re.search(r"surrender|withdrawal charge", t):
        findings.append("[MEDIUM] Annuity content should disclose surrender charges / liquidity limits.")
        worst = worst if rank[worst] >= 1 else "medium"
    if is_annuity and not re.search(r"claims[- ]paying|issuing (insurance )?company|insurer", t):
        findings.append("[LOW] Annuity content should reference the issuing insurer and its claims-paying ability.")
    if is_preneed and not re.search(r"refund|cancel", t):
        findings.append("[MEDIUM] Pre-need content should reference cancellation/refund rights (varies by state).")
        worst = worst if rank[worst] >= 1 else "medium"
    return worst, findings


def llm_second_opinion(text: str) -> str | None:
    return ask_claude(
        "You are an insurance marketing compliance reviewer. List concerns (max 5 bullets) about this text under "
        "NAIC best-interest/suitability, unfair trade practices, and pre-need rules. Do not rewrite it. "
        "State that a human compliance officer must make the final decision.", text, max_tokens=500)


class ComplianceAgent(BaseAgent):
    name = "Compliance Review"
    role = "Checks reports and marketing copy for risky language and routes everything to a human for approval."

    def run(self) -> str:
        reviewed = 0
        reports = read_df("SELECT report_id, body FROM reports WHERE compliance_risk IS NULL")
        for r in reports.itertuples():
            risk, findings = check_text(r.body, disclosures=False)
            notes = "\n".join(findings) or "No rule hits."
            execute("UPDATE reports SET compliance_risk=:r, compliance_notes=:n WHERE report_id=:i",
                    {"r": risk, "n": notes, "i": r.report_id})
            reviewed += 1
        items = read_df("SELECT item_id, text, line FROM content_reviews WHERE risk IS NULL")
        for it in items.itertuples():
            risk, findings = check_text(it.text, it.line or "")
            second = llm_second_opinion(it.text)
            notes = "\n".join(findings) or "No rule hits."
            if second:
                notes += f"\n\nClaude second opinion:\n{second}"
            execute("UPDATE content_reviews SET risk=:r, findings=:n WHERE item_id=:i",
                    {"r": risk, "n": notes, "i": it.item_id})
            reviewed += 1
        return f"Reviewed {reviewed} item(s); all await human approval"


def submit_copy(text: str, line: str) -> str:
    """Used by the dashboard: queue marketing copy for review."""
    item_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
    write_df(pd.DataFrame([{"item_id": item_id, "submitted_at": datetime.now().isoformat(timespec="seconds"),
                            "text": text, "line": line, "risk": None, "findings": None,
                            "review_status": "pending"}]), "content_reviews")
    return item_id
