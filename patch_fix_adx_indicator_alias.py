from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import sys

ROOT = Path.cwd()
TARGET = ROOT / "core" / "indicators" / "adx.py"

if not TARGET.exists():
    print(f"ERROR: Target not found: {TARGET}")
    sys.exit(1)

text = TARGET.read_text(encoding="utf-8")

alias = "ADXIndicator = ADX"

if alias in text:
    print("=" * 64)
    print("ADX COMPATIBILITY ALIAS ALREADY INSTALLED")
    print("=" * 64)
    print(f"Target : {TARGET}")
    try:
        py_compile.compile(str(TARGET), doraise=True)
        print("Syntax validation: PASSED")
    except Exception as exc:
        print(f"Syntax validation failed: {exc}")
        sys.exit(2)
    sys.exit(0)

if "class ADX(BaseIndicator):" not in text:
    print("=" * 64)
    print("PATCH NOT APPLIED")
    print("=" * 64)
    print("Could not find class ADX(BaseIndicator).")
    print("No changes made.")
    sys.exit(3)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = TARGET.with_name(
    f"adx.before_indicator_alias_{stamp}.py"
)
shutil.copy2(TARGET, backup)

# Add alias at module level after the complete class definition.
# Appending is safe because ADX is defined before this statement.
updated = text.rstrip() + """

# ==========================================================
# COMPATIBILITY ALIAS
# ==========================================================
# core.indicator_engine imports ADXIndicator, while this
# module's implementation class is named ADX.
ADXIndicator = ADX
"""

TARGET.write_text(updated + "\n", encoding="utf-8")

try:
    py_compile.compile(str(TARGET), doraise=True)
except Exception as exc:
    shutil.copy2(backup, TARGET)
    print("=" * 64)
    print("ADX ALIAS PATCH FAILED - ORIGINAL RESTORED")
    print("=" * 64)
    print(f"Reason: {exc}")
    sys.exit(4)

print("=" * 64)
print("STOCKVERSITY ADX COMPATIBILITY FIX INSTALLED")
print("=" * 64)
print(f"Target : {TARGET}")
print(f"Backup : {backup}")
print("Added  : ADXIndicator = ADX")
print("Syntax validation: PASSED")
print("=" * 64)
