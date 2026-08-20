# ai-agent-project

A CrewAI-based campus help desk with **two agents**, a FastAPI front
door, pluggable tools, conversation memory, and a small test suite.

## Two agents, two triggers

| | Intake Agent | Dispatch Agent |
|---|---|---|
| Talks to | Students, via `POST /api/chat` | Nobody — reads the ticket queue |
| Runs | Once per chat message | On a timer (`DISPATCH_INTERVAL_MINUTES`), or manually via `POST /api/dispatch/run` |
| Tools | search, calculator, weather, **Create Ticket** | **List Open Tickets, List Technicians, Assign Ticket**, weather, calculator |
| Job | Resolve simple issues inline; log a ticket when a technician is genuinely needed | Batch-assign every open ticket to a technician + time slot |
| Code | `src/agent/executor.py` | `src/agent/dispatch_executor.py` |

They never call each other directly. The **shared SQLite ticket store**
(`src/tickets/store.py`) is the entire handoff: the Intake Agent writes
a row, the Dispatch Agent (running independently, later) reads it and
assigns it. This split keeps per-message chat fast while letting the
Dispatch Agent see the *whole* queue at once — weather-aware, urgency-
sorted, location-clustered — instead of first-come-first-served.

## Layout

```
ai-agent-project/
├── src/
│   ├── agent/         # agent construction (both agents), executors, state, memory
│   ├── tickets/        # shared ticket model + SQLite store + technician roster
│   ├── tools/           # search, calculator, weather, ticketing tools
│   ├── models/          # LLM client + embeddings client wrappers
│   ├── prompts/         # system / agent prompt templates (both agents)
│   ├── utils/            # config, logging, small helpers
│   └── api/               # FastAPI routes + request/response schemas
├── tests/               # pytest suite
├── data/                 # examples, knowledge base docs, technicians.json
├── logs/                  # runtime logs (gitignored, .gitkeep only)
├── main.py                 # FastAPI app entry point + Dispatch Agent scheduler
├── docker-compose.yml
├── requirements.txt
└── .env                      # local secrets (never commit — see .gitignore)
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env .env.local   # or edit .env directly with your real keys
uvicorn main:app --reload
```

## Run with Docker

```bash
docker compose up --build
```

## Run the Streamlit demo UI

A single-file chat UI (`streamlit_app.py`) talks directly to the agent —
no separate API deployment needed for a quick demo:

```bash
streamlit run streamlit_app.py
```

Deploy it free at [share.streamlit.io](https://share.streamlit.io): connect
this repo, set the entry point to `streamlit_app.py`, and add
`ANTHROPIC_API_KEY` (and any tool keys) under the app's Settings → Secrets
in TOML format, e.g.:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
AGENT_LLM_MODEL = "anthropic/claude-sonnet-4-5-20250929"
```

## Run tests

```bash
pytest -v
```

## Configuration

All runtime configuration is read through `src/utils/config.py`
(pydantic-settings), sourced from environment variables / `.env`:

| Variable                    | Purpose                                   |
|-----------------------------|--------------------------------------------|
| `ANTHROPIC_API_KEY`         | LLM provider key                          |
| `AGENT_LLM_MODEL`           | Model string, e.g. `anthropic/claude-sonnet-4-5-20250929` |
| `SEARCH_API_KEY`            | Key for the web search tool provider      |
| `WEATHER_API_KEY`           | Key for the weather tool provider         |
| `LOG_LEVEL`                 | Python logging level (default `INFO`)     |
| `DISPATCH_INTERVAL_MINUTES` | How often the Dispatch Agent runs automatically (default `15`) |
| `TICKETS_DB_PATH`           | SQLite file for the shared ticket store (default `data/tickets.db`) |
| `TECHNICIANS_PATH`          | JSON technician roster used by the Dispatch Agent (default `data/technicians.json`) |
| `CAMPUS_LOCATION`           | Passed to the weather tool during dispatch (default `Kattankulathur, Chengalpattu, Tamil Nadu`) |

## API

- `POST /api/chat` — talk to the **Intake Agent**: send a message, get
  a response, and a ticket is logged behind the scenes if needed
  (`src/api/routes.py`, `src/api/schemas.py`).
- `GET /api/tickets` — list every ticket (open or assigned) in the
  shared store — no LLM call, just a read.
- `POST /api/dispatch/run` — manually trigger a **Dispatch Agent**
  pass instead of waiting for the scheduled interval. Useful for demos.

The Dispatch Agent also runs automatically in the background every
`DISPATCH_INTERVAL_MINUTES`, started from `main.py`'s FastAPI
`startup` event via APScheduler.

## Extending

- Add a new tool: drop a file in `src/tools/`, decorate a function with
  `@tool(...)` from `crewai.tools`, then wire it into
  `src/agent/agent.py`.
- Add a new prompt: extend `src/prompts/agent_prompts.py`.
- Swap the LLM: change `AGENT_LLM_MODEL` in `.env` — no code changes
  needed since `src/models/llm_client.py` reads it directly.
