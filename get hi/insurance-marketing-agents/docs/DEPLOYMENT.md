# Online Deployment Guide

This project can be used completely online. Below are the recommended options.

---

## Option 1 – Streamlit Community Cloud (Easiest & Free)

### Prerequisites
- A free [Streamlit Community Cloud](https://share.streamlit.io) account (sign in with GitHub)
- This repository pushed to GitHub
- An OpenAI or Anthropic API key

### Steps

1. Push the project to a **public or private** GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and click **New app**.
3. Select your repository, branch (`main`), and set the Main file path to:
   ```
   app.py
   ```
4. Click **Advanced settings** → **Secrets** and add:

   ```toml
   OPENAI_API_KEY = "sk-..."
   # or
   # ANTHROPIC_API_KEY = "sk-ant-..."
   DEFAULT_MODEL = "gpt-4o"
   ```

5. Click **Deploy**.

Your app will be live at a URL like:
`https://your-app-name.streamlit.app`

Anyone with the link (or your team) can generate reports in the browser.

---

## Option 2 – Hugging Face Spaces (Also Free)

1. Create a new **Space** on [huggingface.co/spaces](https://huggingface.co/spaces).
2. Choose **Streamlit** as the SDK.
3. Upload or connect the GitHub repo.
4. Add a file named `README.md` at the root with the Space metadata (or let HF generate it).
5. In **Settings → Secrets**, add:
   ```
   OPENAI_API_KEY=sk-...
   ```
6. The Space will build and run `app.py` automatically.

---

## Option 3 – Google Colab (No deployment needed)

1. Open a new Colab notebook.
2. Upload the project zip or clone the repo.
3. Install dependencies:
   ```python
   !pip install -r requirements.txt
   ```
4. Set your API key:
   ```python
   import os
   os.environ["OPENAI_API_KEY"] = "sk-..."
   ```
5. Run the crew directly or launch Streamlit with a tunnel (e.g. `ngrok` / `localtunnel`).

For a pure notebook experience you can also call the crew without Streamlit:

```python
from src.agents.crew import InsuranceMarketingCrew

crew = InsuranceMarketingCrew().crew()
result = crew.kickoff(inputs={
    "product_line": "annuities",
    "user_request": "Market overview and top opportunities"
})
print(result)
```

---

## Option 4 – Replit

1. Create a new Repl → Import from GitHub.
2. Add secrets (OPENAI_API_KEY) in the Replit Secrets panel.
3. Set the run command to:
   ```
   streamlit run app.py --server.port 8501
   ```
4. Click Run. Replit will give you a public URL.

---

## Option 5 – Production-style (Railway / Render / Fly.io)

For a more robust online service:

1. Add a simple `Dockerfile` (or use the Python buildpack).
2. Expose port 8501.
3. Set environment variables for the API keys.
4. Deploy.

Example start command:
```
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

---

## Security Notes for Online Use

- Never commit your `.env` or real API keys.
- Use Streamlit Secrets / Hugging Face Secrets / platform environment variables.
- Restrict who can access the deployed app if it will handle internal company data.
- The current version does **not** store personal client data. Keep it that way unless you add proper security controls.
- Always have a human compliance review before using any generated report externally.

---

## Local testing of the web UI

```bash
cd insurance-marketing-agents
source .venv/bin/activate
streamlit run app.py
```

Open the local URL shown in the terminal (usually http://localhost:8501).
