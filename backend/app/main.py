from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from .api.routes import router

app = FastAPI(title="JARVIS-X Backend", description="Personal AI assistant core services.")
app.include_router(router)

frontend_dist = Path(__file__).resolve().parents[1].parents[0] / 'frontend' / 'dist'
if frontend_dist.exists():
    app.mount('/dashboard', StaticFiles(directory=str(frontend_dist), html=True), name='dashboard')

@app.on_event("startup")
async def startup_event():
    app.state.ready = True

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get('/')
async def redirect_to_dashboard():
    return RedirectResponse(url='/dashboard/')

@app.get('/dashboard')
async def redirect_dashboard_trailing_slash():
    return RedirectResponse(url='/dashboard/')
