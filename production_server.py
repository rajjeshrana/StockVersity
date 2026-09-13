from pathlib import Path
import sys

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "website_backend"

sys.path.insert(0, str(BACKEND))

from server import app

app.mount(
    "/assets",
    StaticFiles(directory=str(ROOT / "assets")),
    name="assets",
)

@app.get("/", include_in_schema=False)
def website_root():
    return FileResponse(str(ROOT / "index.html"))

@app.get("/index.html", include_in_schema=False)
def website_index():
    return FileResponse(str(ROOT / "index.html"))

@app.get("/app.js", include_in_schema=False)
def website_app_js():
    return FileResponse(str(ROOT / "app.js"), media_type="application/javascript")

@app.get("/market_api.js", include_in_schema=False)
def website_market_api_js():
    return FileResponse(str(ROOT / "market_api.js"), media_type="application/javascript")
