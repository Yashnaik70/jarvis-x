# JARVIS-X

A personal AI assistant platform inspired by JARVIS from Iron Man.

## Goal

Build a modular, voice-first, extensible AI operating system for a single user.

## Project structure

- `backend/` — FastAPI backend and core services
- `docs/` — architecture and specification reference

## Getting started

1. Create a Python virtual environment
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Install dependencies
   ```powershell
   pip install -r backend/requirements.txt
   ```
3. Create a `.env` file in `backend/` with your SerpAPI and JARVIS-X API key:
   ```text
   SERPAPI_KEY=your_serpapi_key_here
   JARVISX_API_KEY=your_jarvisx_api_key_here
   ```
4. Run the backend
   ```powershell
   uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
   ```

## React dashboard

The dashboard is now implemented as a React app in `frontend/`.

1. Install frontend dependencies:
   ```powershell
   cd frontend
   npm install
   ```
2. Run the dashboard in development mode:
   ```powershell
   npm run dev
   ```
3. Build for production and serve from FastAPI:
   ```powershell
   npm run build
   uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
   ```

When the frontend is built, the backend serves the dashboard at `http://127.0.0.1:8000/dashboard/`.

## Search Integration
- `search_web` is now implemented with SerpAPI.
- Use the dashboard at `GET /dashboard` and the Web search card to query the internet directly.

## API Key protection
- If `JARVISX_API_KEY` is set in `backend/.env`, all `/api/*` endpoints require an API key.
- Use either the `Authorization: Bearer <key>` header or `X-API-Key: <key>`.

## API Endpoints

- `GET /health` - service health check
- `GET /api/info` - project metadata
- `POST /api/brain/command` - send a command to the AI brain
- `POST /api/memory/add` - store a memory item
- `GET /api/memory/search?q=...` - search stored memory items
- `GET /api/memory/list` - list stored memory items
- `POST /api/memory/query` - look up a memory item
- `GET /api/voice/status` - get voice subsystem status
- `POST /api/voice/command` - send a voice command to the brain
- `POST /api/voice/transcribe` - send base64 WAV audio for transcription
- `POST /api/voice/tts` - convert text to speech and return MP3 audio
- `GET /api/dashboard/overview` - get a system dashboard overview
- `GET /dashboard` - access the web dashboard UI
- `POST /api/brain/execute` - execute a brain command and run tool actions when possible
- `GET /api/tools/list` - list available tools
- `GET /api/agents/list` - list registered agents
- `POST /api/approval/request` - request approval for sensitive actions
- `GET /api/approval/status/{approval_id}` - check approval request status
- `GET /api/approval/list` - list all pending approval requests
- `POST /api/approval/decision` - approve or deny a request
- `POST /api/agent/execute` - execute a registered agent
- `POST /api/tool/execute` - invoke a placeholder tool execution
- `GET /api/automation/list` - list available automation workflows
- `POST /api/automation/run` - trigger a named automation workflow

## Testing and CI

- Install the backend test requirements:
  ```powershell
  pip install -r backend/requirements.txt
  ```
- Run tests locally from the project root:
  ```powershell
  cd backend
  pytest -q
  ```
- GitHub Actions will run the same tests on `main` push and PRs via `.github/workflows/python-app.yml`.

## Next steps

- Add voice layer integration
- Implement memory and agent systems
- Build a dashboard frontend
- Connect tool execution and automation layers
