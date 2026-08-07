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

old_manager = """            self.manager = ScannerManager(

                engine=self.engine,

                auto_load=False,

                debug=self.debug,
            )"""

new_manager = """            self.manager = ScannerManager(

                engine=self.engine,

                auto_load=True,

                debug=self.debug,
            )"""

old_register = """            self._register_default_scanners()"""

new_register = """            # Production scanners are loaded centrally by
            # ScannerManager / ScannerRegistry.  Do not also
            # register Bootstrap-local scanner implementations.
            self.registered_scanner_names = list(
                self.engine.scanner_names()
            )"""

if old_manager not in text:
    if new_manager not in text:
        print("ERROR: Expected ScannerManager(auto_load=False) block not found.")
        sys.exit(2)

if old_register not in text:
    if new_register not in text:
        print("ERROR: Expected Bootstrap registration call not found.")
        sys.exit(3)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = TARGET.with_name(
    f"scanner_bootstrap.before_registry_cleanup_{stamp}.py"
)
shutil.copy2(TARGET, backup)

updated = text

if old_manager in updated:
    updated = updated.replace(old_manager, new_manager, 1)

if old_register in updated:
    updated = updated.replace(old_register, new_register, 1)

TARGET.write_text(updated, encoding="utf-8")

try:
    py_compile.compile(str(TARGET), doraise=True)
except Exception as exc:
    shutil.copy2(backup, TARGET)
    print("=" * 68)
    print("SCANNER REGISTRATION CLEANUP FAILED - ORIGINAL RESTORED")
    print("=" * 68)
    print(f"Reason: {exc}")
    sys.exit(4)

print("=" * 68)
print("STOCKVERSITY SCANNER REGISTRATION CLEANUP INSTALLED")
print("=" * 68)
print(f"Target : {TARGET}")
print(f"Backup : {backup}")
print()
print("Changed:")
print("  ScannerManager auto_load=False -> auto_load=True")
print("  Bootstrap duplicate _register_default_scanners() call removed")
print("  Production ScannerRegistry is now authoritative")
print()
print("Expected production scanner count: 10")
print("Bridge and scheduler initialization order remains unchanged.")
print("Live/historical market-data wiring is untouched.")
print("Syntax validation: PASSED")
print("=" * 68)
