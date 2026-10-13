# Auto-Negotiator 🛡️

An AI-powered consumer advocate agent built with Google ADK (Agent Development Kit), Vertex AI, and Google Cloud. **Auto-Negotiator** helps everyday consumers audit, dispute, and negotiate corporate bills, bogus fees, parking tickets, and recurring subscription overcharges.

---

## What the Agent Does

The agent is built with the following core capabilities:

- **Dispute Tracking & Management (Firestore):**
  - Manages active dispute cases in a native Google Cloud Firestore database (`disputes` collection).
  - Tools:
    - `list_disputes()`: Lists consumer disputes filtered by status (`open`, `in_review`, `resolved`).
    - `get_dispute(dispute_id)`: Retrieves full details of a specific dispute, including provider, disputed amount, category, and negotiation strategy notes.
    - `create_or_update_dispute(...)`: Creates new dispute records or updates existing status, deadlines, and potential savings.

- **Legal Escalation & Demand Letter Drafting:**
  - `draft_dispute_letter(...)`: Generates structured, legally grounded escalation demand letters citing relevant consumer protection frameworks (e.g., FCC Truth-in-Billing, FTC ROSCA for subscriptions, Fair Debt Collection Practices Act, and local municipal parking codes).

- **Benchmark Interest & Fee Analysis (U.S. Treasury Fiscal Data API):**
  - `get_federal_benchmark_interest_rates(...)`: Fetches live public benchmark interest rates from the U.S. Department of the Treasury Fiscal Data API to contest exorbitant corporate late payment penalties and arbitrary finance charges.

- **Cross-Session Long-Term Memory (Vertex AI Memory Bank):**
  - Uses `PreloadMemoryTool` and an automatic post-turn extraction callback (`add_session_to_memory`) backed by Vertex AI Memory Bank (`VertexAiMemoryBankService`).
  - Remembers user provider accounts, billing details, negotiation preferences, past dispute outcomes, and user constraints across sessions.

- **FastAPI Chat Web Frontend (A2A Protocol):**
  - Built-in lightweight web chat interface located in `frontend/` powered by FastAPI and the A2A (Agent-to-Agent) protocol.
  - Handles session/context continuity per user and renders text responses and A2UI cards.

---

## Architecture & Wired Google Cloud Services

| Component | Service | Status | Description |
| :--- | :--- | :--- | :--- |
| **Agent Framework** | Google ADK & Gemini 2.5 Flash | **Wired & Active** | Core reasoning and orchestration |
| **Protocol** | A2A Protocol (v1.0) | **Wired & Active** | Agent-to-Agent passthrough communication |
| **Database** | Google Cloud Firestore | **Wired & Active** | Stores consumer disputes (`disputes_store.py`) |
| **Memory** | Vertex AI Memory Bank | **Wired & Active** | Persistent multi-session memory |
| **External API** | U.S. Treasury Fiscal Data API | **Wired & Active** | Live benchmark rates for fee disputes |
| **Assets Bucket** | Google Cloud Storage | **Wired & Active** | Public assets bucket created for dispute documents & media |
| **Web Proxy & UI** | FastAPI + HTML5 / CSS | **Wired & Active** | Responsive web client communicating via A2A |

### Planned / Not Yet Implemented
- **Image Generation / Victory Badges:** Cloud Storage bucket is provisioned; image generation tools (e.g. Imagen-based victory badge or annotated evidence generation) are planned for a future release.
- **A2UI Interactive Card Rendering in app code:** The frontend contains the built-in A2UI renderer, but dynamic A2UI surface card generation callbacks inside `app/` are planned.
- **Code Execution Sandbox:** Planned for complex financial interest compounding calculations and bill CSV parsing.

---

## Project Structure

```
auto-negotiator/
├── app/
│   ├── agent.py               # Root ADK agent configuration & tools
│   ├── dispute_tools.py       # Demand letter drafting tool
│   ├── disputes_store.py      # Firestore database operations
│   ├── treasury_tools.py      # U.S. Treasury API tool
│   ├── fast_api_app.py        # Local ADK FastAPI runner
│   └── app_utils/             # Service wiring (Memory Bank, sessions)
├── frontend/
│   ├── main.py                # FastAPI A2A proxy server
│   ├── requirements.txt       # Frontend dependencies
│   └── static/
│       └── index.html         # Web chat UI
├── agents-cli-manifest.yaml   # Agent manifest configuration
├── deployment_metadata.json   # Deployment tracking info
├── pyproject.toml             # Python dependencies (UV)
└── seed_firestore.py          # Script to seed initial dispute data
```

---

## Local Setup & Run Instructions

### 1. Prerequisites
- Python 3.11+
- `uv` or `pip`
- Google Cloud SDK (`gcloud`) authenticated with Application Default Credentials (`gcloud auth application-default login`)

### 2. Setup the Agent Backend
From the project root:

```bash
# Install dependencies
uv sync

# Run Firestore seed data (optional)
uv run python seed_firestore.py

# Launch the ADK development web UI locally
uv run adk web . --port 8080 --reload_agents
```

### 3. Setup and Run the Frontend Chat Proxy
To run the lightweight chat web interface against your agent:

```bash
cd frontend

# Install frontend dependencies
pip install -r requirements.txt

# Set your deployed agent resource name or run against local configuration
export AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_ID>/locations/<LOCATION>/reasoningEngines/<ENGINE_ID>"
export AGENT_DIRECTORY="app"

# Start the frontend server
python main.py
```
