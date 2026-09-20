"""Data Quality Agent: cleans raw data, standardizes product names, flags problems."""
from datetime import datetime

import pandas as pd

from agents.base import BaseAgent
from core.db import read_df, write_df

PRODUCT_MAP = {
    "fia": "FIA", "myga": "MYGA", "spia": "SPIA", "term": "Term", "whole life": "Whole Life",
    "iul": "IUL", "pre need": "Pre-Need Plan", "insurance-funded": "Insurance-Funded",
    "trust-funded": "Trust-Funded", "cremation": "Cremation", "burial": "Burial",
}


def _norm(p):
    if pd.isna(p):
        return "Unknown"
    key = str(p).strip().lower()
    return PRODUCT_MAP.get(key, str(p).strip())


class DataQualityAgent(BaseAgent):
    name = "Data Quality"
    role = "Dedupes, standardizes product names, and flags missing or suspicious fields."

    def run(self) -> str:
        df = read_df("SELECT * FROM raw_leads")
        if df.empty:
            return "No raw data to clean yet"
        issues = []
        now = datetime.now().isoformat(timespec="seconds")

        def flag(kind, n, detail):
            if n:
                issues.append({"checked_at": now, "issue": kind, "count": int(n), "detail": detail})

        flag("Missing lead source", df["source"].isna().sum(), "Attribution is broken for these leads; check UTM/call tracking.")
        flag("Missing email", df["email"].isna().sum(), "Cannot dedupe or follow up.")
        flag("Negative or zero cost", (df["cost"] <= 0).sum(), "Check the ad spend import.")

        before = df["product"].nunique()
        df["product"] = df["product"].map(_norm)
        flag("Product names standardized", before - df["product"].nunique(), "Variants like 'fia', 'MYGA ' merged.")

        df["source"] = df["source"].fillna("Unknown")
        dupes = df.duplicated(subset=["email", "line", "created_date"], keep="first") & df["email"].notna()
        flag("Duplicate leads removed", dupes.sum(), "Same email + line + day.")
        clean = df[~dupes].copy()

        write_df(clean, "leads", mode="replace")
        raw_spend = read_df("SELECT * FROM raw_spend")
        if not raw_spend.empty:
            write_df(raw_spend, "spend", mode="replace")
        if issues:
            write_df(pd.DataFrame(issues), "dq_issues")
        return f"Cleaned {len(clean):,} of {len(df):,} rows; {len(issues)} issue types logged"
