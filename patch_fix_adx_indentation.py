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

bad = """        self.previous_close = close
                self.counter += 1"""

good = """        self.previous_close = close
        self.counter += 1"""

if bad not in text:
    if good in text:
        print("=" * 64)
        print("ADX INDENTATION IS ALREADY FIXED")
        print("=" * 64)
        print(f"Target : {TARGET}")
        try:
            py_compile.compile(str(TARGET), doraise=True)
            print("Syntax validation: PASSED")
        except Exception as exc:
            print(f"Syntax validation still fails: {exc}")
            sys.exit(2)
        sys.exit(0)

    print("=" * 64)
    print("PATCH NOT APPLIED")
    print("=" * 64)
    print("Expected malformed ADX lines were not found.")
    print("No changes made.")
    sys.exit(3)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = TARGET.with_name(
    f"adx.before_indent_fix_{stamp}.py"
)
shutil.copy2(TARGET, backup)

updated = text.replace(bad, good, 1)
TARGET.write_text(updated, encoding="utf-8")

try:
    py_compile.compile(str(TARGET), doraise=True)
except Exception as exc:
    shutil.copy2(backup, TARGET)
    print("=" * 64)
    print("ADX PATCH FAILED - ORIGINAL RESTORED")
    print("=" * 64)
    print(f"Reason: {exc}")
    sys.exit(4)

print("=" * 64)
print("STOCKVERSITY ADX INDENTATION FIX INSTALLED")
print("=" * 64)
print(f"Target : {TARGET}")
print(f"Backup : {backup}")
print("Fixed  : line containing self.counter += 1")
print("Syntax validation: PASSED")
print("=" * 64)
