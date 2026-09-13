from pathlib import Path
import sys

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "website_backend"

# Allow production_server.py to import website_backend/server.py
sys.path.insert(0, str(BACKEND))

import server

# Reuse the standalone market API.
app = server.app

# Remove the API's root route so "/" serves the website.
for route in list(app.routes):
    if getattr(route, "path", None) == "/":
        try:
            app.router.routes.remove(route)
        except ValueError:
            pass

app.mount(
    "/assets",
    StaticFiles(directory=str(ROOT / "assets")),
    name="assets",
)

@app.get("/", include_in_schema=False)
def website_root():
    return FileResponse(
        str(ROOT / "index.html"),
        media_type="text/html",
    )

@app.get("/index.html", include_in_schema=False)
def website_index():
    return FileResponse(
        str(ROOT / "index.html"),
        media_type="text/html",
    )

@app.get("/app.js", include_in_schema=False)
def website_app_js():
    return FileResponse(
        str(ROOT / "app.js"),
        media_type="application/javascript",
    )

@app.get("/market_api.js", include_in_schema=False)
def website_market_api_js():
    return FileResponse(
        str(ROOT / "market_api.js"),
        media_type="application/javascript",
    )
