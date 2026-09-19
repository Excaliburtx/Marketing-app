# Insurance Marketing Agents

Multi-agent AI system for **Life Insurance Pre-need**, **At-need**, and **Annuities** marketing data collection and report generation.

Built with [CrewAI](https://github.com/joaomdmoura/crewai). Designed so marketing, distribution, and product teams can quickly generate structured, compliance-aware reports.

---

## What it does

A sequential crew of specialized agents:

1. **Data Collector** – Loads product definitions and key marketing KPIs
2. **Market Researcher** – Builds a structured market & competitive brief
3. **Analyst** – Turns research into prioritized insights and opportunities
4. **Report Writer** – Produces a clean Markdown marketing report
5. **Compliance Reviewer** – Checks language for typical life/annuity advertising issues

Reports are saved under `./reports/`. Intermediate data lives in `./data/`.

---

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/YOUR_USERNAME/insurance-marketing-agents.git
cd insurance-marketing-agents

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure API keys

```bash
cp .env.example .env
# Edit .env and add at least OPENAI_API_KEY (or ANTHROPIC_API_KEY)
```

### 3. Run a report

```bash
# Annuities market overview
python -m src.main run --product annuities --request "Current market size signals, top distribution channels, and 3 marketing opportunities for independent agents"

# Pre-need focused
python -m src.main run -p pre-need -r "Competitive landscape and funeral-home channel opportunities"

# At-need / final expense
python -m src.main run -p at-need -r "Lead sources, average case size trends, and messaging considerations"
```

### Other commands

```bash
python -m src.main list-reports
python -m src.main info
```

### 4. Run the Web Interface (recommended)

```bash
streamlit run app.py
```

Open the URL shown in the terminal (usually http://localhost:8501).  
You can select product line, type a request, and generate reports in the browser.

---

## Run it Online (No local install)

See the full guide: **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)**

Quick options:
- **Streamlit Community Cloud** (free) – connect your GitHub repo, add API key as secret, deploy `app.py`
- **Hugging Face Spaces** (free)
- **Google Colab** or **Replit**

---

## Project Structure

```
insurance-marketing-agents/
├── app.py                       # Streamlit web interface (run online or locally)
├── src/
│   ├── agents/
│   │   ├── config/
│   │   │   ├── agents.yaml      # Role, goal, backstory for each agent
│   │   │   └── tasks.yaml       # Task descriptions & expected outputs
│   │   └── crew.py              # Crew definition
│   ├── config/
│   │   └── settings.py
│   ├── tools/
│   │   ├── data_tools.py        # Save/load/list data + product context
│   │   └── report_tools.py      # Save & list Markdown reports
│   └── main.py                  # CLI entry point
├── data/                        # Intermediate research & context
├── reports/                     # Generated marketing reports
├── docs/
│   ├── ARCHITECTURE.md
│   └── DEPLOYMENT.md            # How to run it fully online
├── requirements.txt
├── .env.example
└── README.md
```

---

## Customization

### Change agent behavior
Edit `src/agents/config/agents.yaml` and `tasks.yaml`. No code changes needed for most prompt adjustments.

### Add real data sources
Extend `src/tools/data_tools.py` with:
- CRM / AMS connectors
- Rate feed APIs
- Internal data warehouse queries
- Web search (Serper, etc.)

### Switch LLM
Set `DEFAULT_MODEL` in `.env` and ensure the corresponding API key is present. CrewAI + LangChain support OpenAI, Anthropic, and many others.

### Make it production-ready
- Add human-in-the-loop approval gates
- Move to LangGraph for more complex branching and state
- Add evaluation (hallucination checks, citation requirements)
- Integrate with your existing BI / CRM tools
- Add proper authentication and audit logging

---

## Compliance Notice

This system is a **productivity aid**, not a substitute for licensed compliance review.

- All marketing language for life insurance and annuities is regulated.
- Guarantees are subject to the claims-paying ability of the issuing insurer.
- Always have final reports reviewed by your compliance team before external use.
- Do not feed the system non-public personal information unless you have proper controls.

---

## Roadmap ideas

- [ ] Real-time rate comparison tool (MYGA / FIA)
- [ ] CRM lead performance ingestion
- [ ] Automated monthly report scheduling
- [ ] Competitor product PDF ingestion + RAG
- [ ] LangGraph version with human approval steps
- [ ] Dashboard front-end

---

## License

MIT (or your preferred license). Add a LICENSE file before making the repo public.
