from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import sys

ROOT = Path.cwd()
IND = ROOT / "core" / "indicators"

aliases = {
    "adx.py": ("ADXIndicator", "ADX"),
    "atr.py": ("ATRIndicator", "ATR"),
    "ema.py": ("EMAIndicator", "EMA"),
    "macd.py": ("MACDIndicator", "MACD"),
    "rsi.py": ("RSIIndicator", "RSI"),
    "vwap.py": ("VWAPIndicator", "VWAP"),
}

backups = []
changed = []

for filename, (alias, actual) in aliases.items():
    target = IND / filename
    if not target.exists():
        print(f"ERROR: Missing {target}")
        sys.exit(1)

    text = target.read_text(encoding="utf-8")

    if f"{alias} = {actual}" in text:
        continue

    if f"class {actual}" not in text:
        print(f"ERROR: Could not find class {actual} in {target}")
        sys.exit(2)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = target.with_name(
        f"{target.stem}.before_indicator_aliases_{stamp}.py"
    )
    shutil.copy2(target, backup)
    backups.append((target, backup))

    addition = (
        "\n\n# ==========================================================\n"
        "# COMPATIBILITY ALIAS\n"
        "# ==========================================================\n"
        f"{alias} = {actual}\n"
    )

    target.write_text(text.rstrip() + addition, encoding="utf-8")
    changed.append(f"{filename}: {alias} = {actual}")

try:
    for filename in aliases:
        py_compile.compile(str(IND / filename), doraise=True)

    py_compile.compile(
        str(ROOT / "core" / "indicator_engine.py"),
        doraise=True,
    )

except Exception as exc:
    for target, backup in backups:
        shutil.copy2(backup, target)

    print("=" * 68)
    print("INDICATOR ALIAS PATCH FAILED - ORIGINAL FILES RESTORED")
    print("=" * 68)
    print(f"Reason: {exc}")
    sys.exit(3)

print("=" * 68)
print("STOCKVERSITY INDICATOR COMPATIBILITY PATCH INSTALLED")
print("=" * 68)

if changed:
    for item in changed:
        print("Added :", item)
else:
    print("All required aliases were already present.")

print()
print("Expected IndicatorEngine names:")
print("  ADXIndicator  -> ADX")
print("  ATRIndicator  -> ATR")
print("  EMAIndicator  -> EMA")
print("  MACDIndicator -> MACD")
print("  RSIIndicator  -> RSI")
print("  VWAPIndicator -> VWAP")
print()
print("Syntax validation: PASSED")
print("=" * 68)
