from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import sys

ROOT = Path.cwd()
TARGET = ROOT / "core" / "scanner" / "scanner_bootstrap.py"

if not TARGET.exists():
    print(f"ERROR: Target not found: {TARGET}")
    sys.exit(1)

text = TARGET.read_text(encoding="utf-8")

old = """            self.registered_scanner_names = list(
                self.engine.scanner_names()
            )"""

new = """            self.registered_scanner_names = list(
                self.engine.registered_scanners
            )"""

if old not in text:
    if new in text:
        print("=" * 68)
        print("SCANNER ENGINE NAME API FIX ALREADY INSTALLED")
        print("=" * 68)
        py_compile.compile(str(TARGET), doraise=True)
        print("Syntax validation: PASSED")
        sys.exit(0)

    print("=" * 68)
    print("PATCH NOT APPLIED")
    print("=" * 68)
    print("Expected self.engine.scanner_names() block was not found.")
    print("No changes made.")
    sys.exit(3)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = TARGET.with_name(
    f"scanner_bootstrap.before_engine_name_api_fix_{stamp}.py"
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
    print("ENGINE NAME API PATCH FAILED - ORIGINAL RESTORED")
    print("=" * 68)
    print(f"Reason: {exc}")
    sys.exit(4)

print("=" * 68)
print("STOCKVERSITY SCANNER ENGINE NAME API FIX INSTALLED")
print("=" * 68)
print(f"Target : {TARGET}")
print(f"Backup : {backup}")
print("Changed:")
print("  self.engine.scanner_names()")
print("      ->")
print("  self.engine.registered_scanners")
print("Syntax validation: PASSED")
print("=" * 68)
