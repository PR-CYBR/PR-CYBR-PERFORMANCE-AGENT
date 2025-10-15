"""FastAPI application exposing the DevX dashboard scaffolding."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent
REPORTS_DIR = REPO_ROOT / "reports"
SYNC_MAP_PATH = REPORTS_DIR / "agent_sync_map.json"


def load_sync_map() -> Dict[str, Any]:
    """Load the agent sync map with graceful fallbacks."""
    if not SYNC_MAP_PATH.exists():
        return {"error": "agent_sync_map.json not found", "agents": []}
    data = json.loads(SYNC_MAP_PATH.read_text(encoding="utf-8"))
    return data


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="PR-CYBR DevX Dashboard", version="0.1.0")

    templates = Jinja2Templates(directory=str(PACKAGE_DIR / "templates"))

    static_dir = PACKAGE_DIR / "static"
    static_dir.mkdir(exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/health", response_class=JSONResponse)
    async def health() -> Dict[str, str]:
        """Health check endpoint for uptime monitoring."""
        return {"status": "ok"}

    @app.get("/api/sync-map", response_class=JSONResponse)
    async def get_sync_map() -> Dict[str, Any]:
        """Expose the sync map JSON for frontend consumption."""
        return load_sync_map()

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> Any:
        """Render the dashboard landing page."""
        sync_map = load_sync_map()
        agents = sync_map.get("agents", [])
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "sync_map": sync_map,
                "agents": agents,
            },
        )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("dashboard.app:app", host="0.0.0.0", port=8000, reload=False)
