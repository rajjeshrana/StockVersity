from pathlib import Path
from datetime import datetime
import shutil

path = Path(r"ui\app.py")

if not path.exists():
    raise SystemExit("ERROR: ui\\app.py not found.")

text = path.read_text(encoding="utf-8")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = path.with_name(
    f"app.before_history_client_{stamp}.py"
)

shutil.copy2(path, backup)

# =========================================================
# 1. ADD IMPORT
# =========================================================

import_line = "from core.upstox_client import UpstoxClient"

if import_line not in text:

    anchor = (
        "from core.market_data.live_stock_universe "
        "import LiveStockUniverse"
    )

    if anchor in text:

        text = text.replace(
            anchor,
            anchor + "\n" + import_line,
            1,
        )

    else:
        # Safe fallback: place after standard UI imports.
        anchor = "from core.dependency_container import get_container"

        if anchor not in text:
            raise SystemExit(
                "ERROR: Could not find safe import location."
            )

        text = text.replace(
            anchor,
            anchor + "\n" + import_line,
            1,
        )


# =========================================================
# 2. ADD HISTORICAL CLIENT
# =========================================================

marker = (
    "[SCANNER DATA] "
    "Historical Upstox client ready."
)

if marker not in text:

    anchor = (
        "configuration = (\n"
        "                upstox_client.Configuration()\n"
        "            )"
    )

    if anchor not in text:
        raise SystemExit(
            "ERROR: Upstox configuration block not found. "
            "No changes written."
        )

    block = '''# ---------------------------------------------
            # Scanner historical REST client
            # Uses SAME authenticated Upstox token.
            # ---------------------------------------------

            self.upstox_history_client = UpstoxClient(
                api_key=api_key,
                access_token=access_token,
                sandbox=False,
            )

            print(
                "[SCANNER DATA] "
                "Historical Upstox client ready."
            )

            # ---------------------------------------------
            # Official Upstox SDK configuration
            # ---------------------------------------------

            '''

    text = text.replace(
        anchor,
        block + anchor,
        1,
    )


# =========================================================
# WRITE
# =========================================================

path.write_text(
    text,
    encoding="utf-8",
)

print()
print("=" * 60)
print("UPSTOX HISTORICAL CLIENT PATCH COMPLETE")
print("=" * 60)
print(f"Patched : {path}")
print(f"Backup  : {backup}")
print()
print("Added:")
print("  - UpstoxClient import")
print("  - Historical REST client")
print("  - Existing access token reused")
print("  - Existing WebSocket provider untouched")
print("=" * 60)
