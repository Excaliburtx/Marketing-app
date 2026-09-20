# Insurance Marketing Agent Team

An AI agent team for **Pre-Need, At-Need, Life Insurance and Annuities** marketing. It collects data,
cleans it, writes reports, watches the market, and screens marketing copy for compliance, all on a schedule,
with a Streamlit dashboard so your team can see what every agent did.

```
GitHub Actions (schedule) ─► run_agents.py ─► Orchestrator ─► [Collect → Clean → Report → Compliance → Market Intel]
                                                     │
                                          Postgres (shared DB)
                                                     │
                                       Streamlit dashboard (app.py)  ◄── your team
```

## The team

| Agent | What it does | File |
|---|---|---|
| Data Collection | Pulls leads/spend from connectors (demo, CSV inbox, Salesforce stub) | `agents/data_collection.py` |
| Data Quality | Dedupes, standardizes product names, flags missing sources | `agents/data_quality.py` |
| Reporting | KPIs by line, week-over-week, cost-spike alerts, Claude-written narrative | `agents/reporting.py` |
| Compliance Review | Flags risky wording, routes to a human. **Never auto-approves** | `agents/compliance.py` |
| Market Intelligence | Annuity rates, NAIC/state DOI/FINRA and pre-need news via Claude web search | `agents/market_intel.py` |
| Orchestrator | Runs them in order; stops if data collection fails | `agents/orchestrator.py` |

## 1. Run it locally (2 minutes)

```bash
pip install -r requirements.txt
cp .env.example .env            # add ANTHROPIC_API_KEY for Claude-written reports + market intel
python run_agents.py --job all  # loads demo data and runs the whole team
streamlit run app.py            # open the dashboard
```

It works without an API key (rule-based fallbacks); the key unlocks the written analysis and market intel.

## 2. Put it on GitHub + go live (always-on)

1. Create a GitHub repo and push this folder.
2. **Create a free hosted Postgres** (Supabase or Neon). Copy the connection string.
   *This step matters:* GitHub Actions runners are wiped after every run, so a local SQLite file won't persist. The
   agents (GitHub) and the dashboard (Streamlit) must share one cloud database.
3. Repo → Settings → Secrets and variables → Actions:
   - Secrets: `ANTHROPIC_API_KEY`, `DATABASE_URL` (`postgresql+psycopg2://user:pass@host:5432/db`)
   - Variable: `DATA_MODE` = `demo` (later `live`)
4. The workflow `.github/workflows/agents.yml` now runs hourly (collect + clean) and daily at 7am PT (everything).
   Trigger manually from the Actions tab to test.
5. Deploy the dashboard: [share.streamlit.io](https://share.streamlit.io) → New app → pick the repo → `app.py`.
   In App settings → Secrets add `DATABASE_URL`, `ANTHROPIC_API_KEY`, and `APP_PASSWORD` (**set a password**; this is sensitive data).

Prefer a server? Run `python scheduler.py` on any VM/container instead of Actions (it runs the same jobs continuously).

## 3. Connect your real data (`DATA_MODE=live`)

- **Fastest:** export CSVs from your CRM / ad platforms into `data/inbox/` named `leads*.csv` and `spend*.csv`
  (same columns as `core/sample_data.py`).
- **Proper:** add a connector class in `agents/data_collection.py` (Salesforce, HubSpot, Redtail, Google Ads, Meta...)
  and register it in `get_connectors()`.

## 4. Compliance: read this before using with customers

The compliance checker is a **starter rule set, not legal advice**. It catches obvious problems (guarantees, "risk-free",
unsubstantiated rate claims, missing surrender/refund disclosures) and always requires human sign-off. Have your compliance
officer review and extend `RULES` for your states, NAIC best-interest requirements, FINRA rules for any securities-based
products (RILAs, variable annuities), state pre-need statutes, and TCPA. Agents here are read-only reporters. They do not
send anything to customers.

## Suggested next steps

1. Wire your first real connector (CRM leads) and replace the demo data.
2. Give the compliance officer the `RULES` list to edit.
3. Add agents: lead scoring, campaign copy drafting (routed through Compliance), agent/advisor production reports.
