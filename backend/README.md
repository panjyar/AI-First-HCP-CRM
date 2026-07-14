# python -m uvicorn app.main:app --reload

# AI-First CRM — HCP Log Interaction Backend

FastAPI + PostgreSQL + LangGraph + Groq backend for the assignment's split-screen HCP interaction experience. The React form is read-only; natural-language chat calls LangGraph tools that create or update its state.

## Implemented LangGraph tools

1. `log_interaction` — extracts a new interaction, fills the form, and saves it.
2. `edit_interaction` — applies only explicitly requested corrections.
3. `search_hcp` — searches HCP master records and auto-selects a unique match.
4. `get_interaction_history` — retrieves recent interactions for an HCP.
5. `schedule_follow_up` — creates a follow-up and updates the current form.

The model decides which tool to call. There is no keyword-based `if/else` intent router.

## Model note

The assignment mentions `gemma2-9b-it`, but Groq retired that model. The application therefore uses the assignment-approved `llama-3.3-70b-versatile`, configured through `GROQ_MODEL`.

## 1. Start PostgreSQL

```bash
docker compose up -d postgres
```

## 2. Create the Python environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your Groq key to `.env`:

```env
GROQ_API_KEY=your_real_key
```

## 3. Seed demo data

```bash
python -m app.database.seed
```

## 4. Run the API

```bash
uvicorn app.main:app --reload
```

Open:

- Swagger: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`
- Tool list: `http://127.0.0.1:8000/api/tools`

## Main chat endpoint

`POST /api/chat`

```json
{
  "session_id": "demo-session",
  "message": "Today I met Dr. Smith at Apollo Hospital in person. We discussed Product X efficacy. The sentiment was positive and I shared a brochure.",
  "current_form": {}
}
```

For later messages, either send the latest `current_form` or omit it / send `null` to restore the persisted form for that `session_id`.

## Suggested five-tool demo

### 1. Log

```text
Today I met Dr. Anjali Mehta at Fortis Hospital in person. We discussed CardioPlus efficacy and dosing. Her sentiment was positive and I shared a product brochure.
```

### 2. Edit

```text
Correction: the sentiment was neutral and I also shared the safety study.
```

### 3. Search HCP

```text
Find Dr. Priya Nair from Manipal Hospital.
```

### 4. Interaction history

```text
Show the last two interactions with Dr. Anjali Mehta.
```

### 5. Schedule follow-up

```text
Schedule a follow-up call with the selected HCP next Monday to discuss the safety data. Set priority to high.
```

## Supporting endpoints

- `GET /api/hcps?q=Mehta`
- `GET /api/interactions?session_id=demo-session`
- `GET /api/interactions/{interaction_id}`
- `GET /api/follow-ups`
- `GET /api/sessions/{session_id}`
- `DELETE /api/sessions/{session_id}`

## Database tables

- `hcps`
- `interactions`
- `follow_ups`
- `agent_sessions`
- `chat_messages`

Tables are created on startup for assignment convenience. In a production system, replace automatic `create_all` with reviewed Alembic migrations.
