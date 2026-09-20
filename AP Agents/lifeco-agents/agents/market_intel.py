"""Market Intelligence Agent: annuity rates, competitor moves, state DOI / pre-need regulatory news.
Uses Claude with web search. Without an API key it records a reminder instead of inventing data."""
from datetime import datetime

import pandas as pd

from agents.base import BaseAgent
from core.db import write_df
from core.llm import ask_claude, llm_available

TOPICS = [
    ("Annuity rates", "Summarize current U.S. MYGA and fixed indexed annuity rate trends and notable carrier rate changes this week. Cite sources and dates."),
    ("Regulatory", "Summarize new NAIC, state Department of Insurance, or FINRA developments affecting annuity and life insurance marketing in the last 2 weeks. Cite sources."),
    ("Pre-need", "Summarize recent news on pre-need funeral contracts/insurance regulation and industry trends (trust funding, cremation rates, NFDA data). Cite sources."),
]
SYSTEM = ("You are a market intelligence analyst for a life insurance, annuity and pre-need company. "
          "Only report what you find via search, include the source and date for each item, and say 'nothing notable found' "
          "rather than guessing. Keep it under 200 words.")


class MarketIntelAgent(BaseAgent):
    name = "Market Intelligence"
    role = "Monitors annuity rates, competitors, and state/NAIC/FINRA/pre-need regulatory news."

    def run(self) -> str:
        if not llm_available():
            return "Skipped: set ANTHROPIC_API_KEY to enable web-search intelligence"
        rows = []
        for topic, prompt in TOPICS:
            text = ask_claude(SYSTEM, prompt, max_tokens=800, web_search=True)
            if text:
                rows.append({"created_at": datetime.now().isoformat(timespec="seconds"), "topic": topic, "summary": text})
        if rows:
            write_df(pd.DataFrame(rows), "market_intel")
        return f"Saved {len(rows)} intelligence brief(s)"
