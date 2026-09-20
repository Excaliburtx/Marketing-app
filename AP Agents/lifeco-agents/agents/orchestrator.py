"""Orchestrator: runs the agent team in the right order and records each step."""
from agents.compliance import ComplianceAgent
from agents.data_collection import DataCollectionAgent
from agents.data_quality import DataQualityAgent
from agents.market_intel import MarketIntelAgent
from agents.reporting import ReportingAgent

TEAM = [DataCollectionAgent(), DataQualityAgent(), ReportingAgent(), ComplianceAgent(), MarketIntelAgent()]
BY_NAME = {a.name: a for a in TEAM}

JOBS = {
    "collect": ["Data Collection", "Data Quality"],                 # hourly
    "report": ["Reporting", "Compliance Review"],                   # daily / weekly
    "intel": ["Market Intelligence"],                               # daily
    "review": ["Compliance Review"],                                # picks up newly submitted copy
    "all": ["Data Collection", "Data Quality", "Reporting", "Compliance Review", "Market Intelligence"],
}


def run_job(job: str) -> list[dict]:
    results = []
    for name in JOBS[job]:
        res = BY_NAME[name].execute()
        results.append(res)
        if res["status"] == "failed" and name in ("Data Collection", "Data Quality"):
            break  # downstream agents would only work on stale/bad data
    return results
