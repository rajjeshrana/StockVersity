from pathlib import Path

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import server

ROOT = Path(__file__).resolve().parent

# Reuse the existing standalone market API application.
app = server.app

# The API application already defines "/".
# Remove that API-root route so the website can own "/".
for route in list(app.routes):
    if getattr(route, "path", None) == "/":
        try:
            app.router.routes.remove(route)
        except ValueError:
            pass

# Website assets.
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
