from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import sys

ROOT = Path.cwd()
TARGET = ROOT / "core" / "data_manager.py"

if not TARGET.exists():
    print(f"ERROR: Target not found: {TARGET}")
    sys.exit(1)

text = TARGET.read_text(encoding="utf-8")

old = """            scanner_system.add_candles(
                instrument_key,
                timeframe,
                records,
                max_candles=500,
            )"""

new = """            for candle in records:
                scanner_system.add_candle(
                    instrument_key,
                    timeframe,
                    candle,
                    max_candles=500,
                )"""

if old not in text:
    if new in text:
        print("=" * 68)
        print("SCANNER HISTORICAL ADD_CANDLE FIX ALREADY INSTALLED")
        print("=" * 68)
        try:
            py_compile.compile(str(TARGET), doraise=True)
            print("Syntax validation: PASSED")
        except Exception as exc:
            print(f"Syntax validation failed: {exc}")
            sys.exit(2)
        sys.exit(0)

    print("=" * 68)
    print("PATCH NOT APPLIED")
    print("=" * 68)
    print("Expected scanner_system.add_candles(...) block not found.")
    print("No changes made.")
    sys.exit(3)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = TARGET.with_name(
    f"data_manager.before_add_candle_fix_{stamp}.py"
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
    print("HISTORICAL ADD_CANDLE PATCH FAILED - ORIGINAL RESTORED")
    print("=" * 68)
    print(f"Reason: {exc}")
    sys.exit(4)

print("=" * 68)
print("STOCKVERSITY HISTORICAL CANDLE API FIX INSTALLED")
print("=" * 68)
print(f"Target : {TARGET}")
print(f"Backup : {backup}")
print("Changed: ScannerBootstrap.add_candles(...)")
print("     to: loop using existing ScannerBootstrap.add_candle(...)")
print("Maximum scanner candle history per timeframe: 500")
print("Syntax validation: PASSED")
print("=" * 68)
