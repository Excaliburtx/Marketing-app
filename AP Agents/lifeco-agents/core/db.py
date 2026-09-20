"""Database layer. SQLite by default, Postgres in the cloud (set DATABASE_URL)."""
import os
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

_engine = None


def get_engine():
    global _engine
    if _engine is None:
        url = os.getenv("DATABASE_URL", "sqlite:///data/agents.db")
        if url.startswith("sqlite:///"):
            folder = os.path.dirname(url.replace("sqlite:///", ""))
            if folder:
                os.makedirs(folder, exist_ok=True)
        _engine = create_engine(url, pool_pre_ping=True)
    return _engine


def write_df(df: pd.DataFrame, table: str, mode: str = "append"):
    df.to_sql(table, get_engine(), if_exists=mode, index=False)


def read_df(query: str, params: dict | None = None) -> pd.DataFrame:
    try:
        with get_engine().connect() as conn:
            return pd.read_sql(text(query), conn, params=params or {})
    except Exception:
        return pd.DataFrame()  # table doesn't exist yet


def execute(query: str, params: dict | None = None):
    with get_engine().begin() as conn:
        conn.execute(text(query), params or {})


def log_run(agent: str, status: str, summary: str, started: datetime, finished: datetime):
    write_df(pd.DataFrame([{
        "agent": agent, "status": status, "summary": summary[:1000],
        "started_at": started.isoformat(timespec="seconds"),
        "finished_at": finished.isoformat(timespec="seconds"),
    }]), "agent_runs")
