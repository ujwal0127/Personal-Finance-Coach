# Personal Finance Coach — Multi-Agent AI System

A Multi-Agent AI system that analyzes a user's income, expenses, investment profile,
and financial goals, then produces a single personalized financial report.

## Architecture

```
                    User
                      |
                      v
            Supervisor Agent
                      |
     +--------+--------+--------+---------+
     v        v        v        v
 Income   Expense   Investment   Goal
 Agent     Agent      Agent      Agent
     +--------+--------+--------+---------+
                      |
                      v
        Personalized Financial Report
```

- **Income Agent** — analyzes salary, freelance, rental, passive income, bonuses.
- **Expense Agent** — categorizes spending, flags overspending, computes savings potential.
- **Investment Agent** — recommends SIPs, mutual funds, FDs, gold, emergency fund allocation.
- **Goal Agent** — tracks progress toward house/car/education/retirement/vacation goals.
- **Supervisor Agent** — orchestrates all agents via a LangGraph workflow and merges
  their outputs into one financial report.

## Tech Stack

- Python 3.10+
- LangGraph (agent orchestration)
- LangChain (LLM tooling)
- Google Gemini or OpenAI GPT (LLM backend)
- SQLite (default) / PostgreSQL (scalable option)
- FAISS (optional vector store for memory/retrieval)
- Streamlit (frontend dashboard)
- Pydantic (data validation)

## Getting Started

```bash
# 1. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# then edit .env and add your OPENAI_API_KEY or GOOGLE_API_KEY

# 4. Run the CLI demo
python app/main.py

# 5. Or run the Streamlit dashboard
streamlit run app/ui/streamlit_app.py
```

No API key? The system automatically falls back to a rule-based mock LLM
(`app/services/llm_client.py`) so you can run and test the full agent pipeline offline.

## Project Structure

See `docs/architecture.md` for a full breakdown of each module.

## Running Tests

```bash
pytest tests/
```

## License

MIT — free to use for academic, hackathon, or prototype purposes.
