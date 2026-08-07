from __future__ import annotations

from pathlib import Path
from datetime import datetime
import shutil
import sys
import py_compile

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "core" / "data_manager.py"
IMPORT_LINE = "from core.scanner.scanner_bootstrap import get_scanner_system"
MARKER = "# STOCKVERSITY_SCANNER_LIVE_WIRING_V1"

def fail(message):
    print("\n[PATCH ERROR]", message, "\n")
    sys.exit(1)

if not TARGET.exists():
    fail(f"Target file not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if MARKER in text:
    print("Patch is already installed.")
    sys.exit(0)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = TARGET.with_name(
    f"{TARGET.stem}.before_scanner_live_wiring_{stamp}{TARGET.suffix}"
)
shutil.copy2(TARGET, backup)

if IMPORT_LINE not in text:
    anchor = "from core.upstox_client import UpstoxClient"
    if anchor not in text:
        fail("Could not find UpstoxClient import.")
    text = text.replace(anchor, anchor + "\n" + IMPORT_LINE, 1)

anchors = [
"""        self.client.register_tick_callback(

            self.on_tick

        )""",
"""        self.client.register_tick_callback(
            self.on_tick
        )"""
]

registration_anchor = next((a for a in anchors if a in text), None)
if registration_anchor is None:
    fail("Could not locate existing self.on_tick callback registration.")

registration_block = """        self.client.register_tick_callback(

            self.on_tick

        )

        # STOCKVERSITY_SCANNER_LIVE_WIRING_V1
        try:
            self.client.register_tick_callback(
                self._forward_tick_to_scanner
            )
            self.logger.info(
                "Scanner live market-data callback registered."
            )
        except Exception:
            self.logger.exception(
                "Unable to register scanner live-data callback."
            )"""

text = text.replace(registration_anchor, registration_block, 1)

method_anchor = """    # =====================================================
    # STORE DATAFRAME
    # ====================================================="""

method_block = """    # =====================================================
    # SCANNER LIVE MARKET DATA BRIDGE
    # =====================================================

    def _forward_tick_to_scanner(
        self,
        tick,
    ) -> None:
        \"\"\"Forward one existing Upstox live tick to the shared scanner.\"\"\"

        try:
            if tick is None:
                return

            if isinstance(tick, dict):
                quote = dict(tick)
            elif hasattr(tick, "to_dict"):
                quote = tick.to_dict()
            elif hasattr(tick, "__dict__"):
                quote = {
                    key: value
                    for key, value in vars(tick).items()
                    if not key.startswith("_")
                }
            else:
                return

            if not quote:
                return

            scanner_system = get_scanner_system()

            if not getattr(scanner_system, "initialized", False):
                scanner_system.initialize()

            scanner_system.update_market_quote(
                quote,
                trigger_scan=False,
            )

        except Exception:
            self.logger.exception(
                "Scanner live tick forwarding failed."
            )

"""

if method_anchor not in text:
    fail("Could not locate STORE DATAFRAME section.")

text = text.replace(method_anchor, method_block + method_anchor, 1)
TARGET.write_text(text, encoding="utf-8")

try:
    py_compile.compile(str(TARGET), doraise=True)
except Exception as exc:
    shutil.copy2(backup, TARGET)
    fail(f"Syntax validation failed; original restored. Reason: {exc}")

print("=" * 64)
print("STOCKVERSITY SCANNER LIVE WIRING PATCH INSTALLED")
print("=" * 64)
print(f"Target : {TARGET}")
print(f"Backup : {backup}")
print("Syntax validation: PASSED")
print("Existing Upstox connection reused; no second websocket created.")
print("=" * 64)
