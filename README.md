# Data Analysis Agent (BigQuery + LangGraph) `data_analysis_agent`

CLI-based data analysis agent that queries Google BigQuery’s public dataset `bigquery-public-data.thelook_ecommerce` and returns actionable business insights using a 3-agent pipeline:

**Orchestrator → 1) Planner → 2) SQL Agent → 3) BigQuery Execute → Analyst**

This repo is designed to be reproducible on another machine using **uv** and **uv.lock**.

---

## What this does

Given a natural-language question (e.g., “top products in Czech Republic last 2 weeks”), the system:

1. **Planner**: interprets the user intent and outputs a structured analysis plan
2. **SQL Agent**: converts the plan/question into a single BigQuery Standard SQL query (read-only)
3. **Execute**: runs SQL against BigQuery (with safety checks) and produces a compact preview
4. **Analyst**: converts the results into business insights + recommended actions

The CLI prints both:
- the **final answer**
- the **intermediate steps** (plan, SQL, preview/errors) for transparency/debugging


### Overall Architecture 
- Reasons for choosing this model: while Gemini models was a requirement, they are known to work good on NLP solutions.
- Three agent pipeline: orchestrator -> 1) planner -> 2) sql -> 3) analyst. This way functionalities, guardrails, metrics and monitoring can be managed as independant micro-services
- Error handling: at this point basic due to time constraints. If i had more time, i'd add custom guradrails (LLM-as-a-judge) or using parallelism to manage multiple calls at once using libraries like ember (more expensive but very safe)

---

## Requirements

- Python 3.12+ (recommended)
- `uv` installed
- A Google Cloud project (used to run BigQuery jobs)
- BigQuery access configured via Application Default Credentials (ADC)
- Gemini API key (or other backend)

---

## Reproducible setup (uv + lockfile)

### 1) Clone repo and sync
```bash
git clone
cd data_analysis_agent
uv sync
```

### 2) .env variables
```bash
GOOGLE_API_KEY=YOUR_GEMINI_KEY
GEMINI_MODEL=gemini-3-flash
BIGQUERY_PROJECT_ID=gen-lang-client-xxxxxxxxxx
BIGQUERY_DATASET_ID=bigquery-public-data.thelook_ecommerce
BQ_MAX_BYTES=2000000000
```


### 3) run
from root:
```bash
uv run python -m app.cli
```





