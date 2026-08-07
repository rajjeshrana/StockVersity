"""
StockVersity Scanner Pro
Fix live scanner tick forwarding.

Fix:
    ScannerBootstrap exposes update_market_quotes([...])
    but DataManager live wiring incorrectly calls update_market_quote(...).
"""

from pathlib import Path
from datetime import datetime
import py_compile
import shutil
import sys

ROOT = Path.cwd()
TARGET = ROOT / "core" / "data_manager.py"

if not TARGET.exists():
    print(f"ERROR: Target not found: {TARGET}")
    sys.exit(1)

text = TARGET.read_text(encoding="utf-8")

old = """            scanner_system.update_market_quote(
                quote,
                trigger_scan=False,
            )"""

new = """            scanner_system.update_market_quotes(
                [quote],
                trigger_scan=False,
            )"""

if old not in text:
    # Tolerate whitespace differences by checking whether already fixed.
    if "scanner_system.update_market_quotes(" in text:
        print("=" * 64)
        print("LIVE SCANNER TICK FORWARDING ALREADY FIXED")
        print("=" * 64)
        print(f"Target : {TARGET}")
        print("No changes required.")
        print("=" * 64)
        sys.exit(0)

    print("=" * 64)
    print("PATCH NOT APPLIED")
    print("=" * 64)
    print("Expected old code was not found.")
    print(f"Target: {TARGET}")
    print()
    print("Search for these calls:")
    print("  scanner_system.update_market_quote(")
    print("  scanner_system.update_market_quotes(")
    print("=" * 64)
    sys.exit(2)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = TARGET.with_name(
    f"data_manager.before_fix_live_scanner_quotes_{stamp}.py"
)

shutil.copy2(TARGET, backup)

updated = text.replace(old, new, 1)
TARGET.write_text(updated, encoding="utf-8")

try:
    py_compile.compile(str(TARGET), doraise=True)
except Exception as exc:
    shutil.copy2(backup, TARGET)
    print("=" * 64)
    print("PATCH FAILED - ORIGINAL RESTORED")
    print("=" * 64)
    print(exc)
    sys.exit(3)

print("=" * 64)
print("STOCKVERSITY LIVE SCANNER QUOTE FIX INSTALLED")
print("=" * 64)
print(f"Target : {TARGET}")
print(f"Backup : {backup}")
print("Changed:")
print("  update_market_quote(quote)")
print("        ->")
print("  update_market_quotes([quote])")
print()
print("Syntax validation: PASSED")
print("=" * 64)
