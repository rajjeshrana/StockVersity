from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import sys

ROOT = Path.cwd()
TARGET = ROOT / "core" / "scanner" / "orb_scanner.py"

if not TARGET.exists():
    print(f"ERROR: Target not found: {TARGET}")
    sys.exit(1)

text = TARGET.read_text(encoding="utf-8")

old = """        candles = data.get(
            "candles",
            [],
        )

        if not isinstance(
            candles,
            (list, tuple),
        ):

            return None
"""

new = """        candles = data.get(
            "candles",
            [],
        )

        # MarketDataBridge stores candles by timeframe:
        # {"1m": [...], "5m": [...], "15m": [...], ...}
        # ORB normally operates on 5-minute candles. Preserve
        # compatibility with the legacy flat-list format too.
        if isinstance(
            candles,
            dict,
        ):
            timeframe = getattr(
                self,
                "timeframe",
                "5m",
            )
            candles = candles.get(
                timeframe,
                candles.get(
                    "5m",
                    [],
                ),
            )

        if not isinstance(
            candles,
            (list, tuple),
        ):

            return None
"""

if old not in text:
    if new in text:
        print("=" * 68)
        print("ORB MULTI-TIMEFRAME COMPATIBILITY FIX ALREADY INSTALLED")
        print("=" * 68)
        py_compile.compile(str(TARGET), doraise=True)
        print("Syntax validation: PASSED")
        sys.exit(0)

    print("=" * 68)
    print("PATCH NOT APPLIED")
    print("=" * 68)
    print("Exact current ORB candle block was not found.")
    print("No changes made.")
    sys.exit(3)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = TARGET.with_name(
    f"orb_scanner.before_multitimeframe_fix_{stamp}.py"
)
shutil.copy2(TARGET, backup)

TARGET.write_text(
    text.replace(old, new, 1),
    encoding="utf-8",
)

try:
    py_compile.compile(str(TARGET), doraise=True)
except Exception as exc:
    shutil.copy2(backup, TARGET)
    print("=" * 68)
    print("ORB PATCH FAILED - ORIGINAL RESTORED")
    print("=" * 68)
    print(f"Reason: {exc}")
    sys.exit(4)

print("=" * 68)
print("STOCKVERSITY ORB MULTI-TIMEFRAME COMPATIBILITY FIX INSTALLED")
print("=" * 68)
print(f"Target : {TARGET}")
print(f"Backup : {backup}")
print("ORB now accepts MarketDataBridge timeframe dictionaries.")
print("ORB uses its configured timeframe, with 5m fallback.")
print("Legacy flat-list candles remain supported.")
print("Breakout/VCP and bridge wiring are untouched.")
print("Syntax validation: PASSED")
print("=" * 68)
