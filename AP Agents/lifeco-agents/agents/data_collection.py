"""Data Collection Agent: pulls from every connector into the warehouse.

To add a real source (Salesforce, HubSpot, Google Ads...), subclass Connector and return
DataFrames with the same columns as core/sample_data.py, then register it in get_connectors().
"""
import glob
import os

import pandas as pd

from agents.base import BaseAgent
from core.db import write_df
from core.sample_data import generate


class Connector:
    name = "connector"

    def fetch(self) -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
        """Return (leads_df, spend_df). Either can be None."""
        raise NotImplementedError


class DemoConnector(Connector):
    name = "demo-data"

    def fetch(self):
        return generate()


class CSVInboxConnector(Connector):
    """Drop CRM/ad-platform exports into data/inbox/. Files starting with 'leads' or 'spend' are loaded."""
    name = "csv-inbox"

    def fetch(self):
        leads = [pd.read_csv(f) for f in glob.glob("data/inbox/leads*.csv")]
        spend = [pd.read_csv(f) for f in glob.glob("data/inbox/spend*.csv")]
        return (pd.concat(leads) if leads else None, pd.concat(spend) if spend else None)


class SalesforceConnector(Connector):
    """TODO: use `simple-salesforce`. Map Opportunity/Lead fields to the leads schema."""
    name = "salesforce"

    def fetch(self):
        raise NotImplementedError("Add credentials + query, then register in get_connectors().")


def get_connectors() -> list[Connector]:
    if os.getenv("DATA_MODE", "demo") == "demo":
        return [DemoConnector()]
    return [CSVInboxConnector()]  # add SalesforceConnector(), GoogleAdsConnector(), etc.


class DataCollectionAgent(BaseAgent):
    name = "Data Collection"
    role = "Pulls leads, spend and policy data from all sources into the warehouse."

    def run(self) -> str:
        all_leads, all_spend, sources = [], [], []
        for c in get_connectors():
            leads, spend = c.fetch()
            if leads is not None and len(leads):
                all_leads.append(leads)
            if spend is not None and len(spend):
                all_spend.append(spend)
            sources.append(c.name)
        if not all_leads:
            return f"No new data found in: {', '.join(sources)}"
        leads_df = pd.concat(all_leads, ignore_index=True)
        # raw layer is replaced each run (idempotent); the quality agent produces the clean layer
        write_df(leads_df, "raw_leads", mode="replace")
        if all_spend:
            write_df(pd.concat(all_spend, ignore_index=True), "raw_spend", mode="replace")
        return f"Loaded {len(leads_df):,} leads from {', '.join(sources)}"
