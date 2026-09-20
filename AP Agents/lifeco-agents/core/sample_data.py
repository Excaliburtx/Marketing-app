"""Generates realistic-looking DEMO data so the dashboard works before you connect real systems."""
import random
from datetime import date, timedelta

import pandas as pd

LINES = ["Pre-Need", "At-Need", "Life Insurance", "Annuity"]
SOURCES = {
    "Pre-Need": ["Seminar", "Direct Mail", "Funeral Home Referral", "Facebook Ads", "Google Ads"],
    "At-Need": ["Phone Call", "Google Ads", "Funeral Home Referral", "Website"],
    "Life Insurance": ["Google Ads", "Facebook Ads", "Email", "Referral"],
    "Annuity": ["Seminar", "Direct Mail", "Google Ads", "Email", "Referral"],
}
PRODUCTS = {
    "Pre-Need": ["Insurance-Funded", "Trust-Funded"],
    "At-Need": ["Cremation", "Burial"],
    "Life Insurance": ["Term", "Whole Life", "IUL"],
    "Annuity": ["MYGA", "FIA", "SPIA"],
}
STATES = ["CA", "TX", "FL", "AZ", "NV", "OH"]
CPL = {"Seminar": 95, "Direct Mail": 60, "Funeral Home Referral": 15, "Facebook Ads": 38,
       "Google Ads": 55, "Phone Call": 20, "Website": 25, "Email": 12, "Referral": 10}
CLOSE = {"Pre-Need": 0.22, "At-Need": 0.62, "Life Insurance": 0.14, "Annuity": 0.12}
PREMIUM = {"Pre-Need": (6000, 12000), "At-Need": (7500, 11500), "Life Insurance": (900, 3500),
           "Annuity": (50000, 250000)}


def generate(days: int = 60, seed: int = 7):
    rnd = random.Random(seed)
    leads, spend = [], []
    today = date.today()
    lead_id = 1
    for d in range(days, -1, -1):
        day = today - timedelta(days=d)
        for line in LINES:
            for src in SOURCES[line]:
                n = rnd.randint(1, 6)
                cpl = CPL[src] * rnd.uniform(0.85, 1.2)
                # planted anomaly: Facebook pre-need gets expensive in the last 5 days
                if line == "Pre-Need" and src == "Facebook Ads" and d <= 5:
                    cpl *= 2.1
                spend.append({"date": day.isoformat(), "line": line, "channel": src,
                              "spend": round(n * cpl, 2), "leads": n})
                for _ in range(n):
                    appt = rnd.random() < 0.55
                    applied = appt and rnd.random() < CLOSE[line] / 0.55 * 1.3
                    issued = applied and rnd.random() < 0.85
                    lo, hi = PREMIUM[line]
                    email = f"person{rnd.randint(1, 900)}@example.com" if rnd.random() < 0.9 else None
                    leads.append({
                        "lead_id": lead_id, "created_date": day.isoformat(), "line": line,
                        # deliberately messy so the Data Quality agent has work to do
                        "product": rnd.choice(PRODUCTS[line]) if rnd.random() > 0.05 else rnd.choice(["fia", "MYGA ", "pre need", "TERM"]),
                        "source": src if rnd.random() > 0.04 else None,
                        "email": email, "state": rnd.choice(STATES),
                        "appointment_set": int(appt), "application": int(applied), "issued": int(issued),
                        "premium": round(rnd.uniform(lo, hi), 2) if issued else 0.0,
                        "cost": round(cpl, 2),
                    })
                    lead_id += 1
    return pd.DataFrame(leads), pd.DataFrame(spend)
