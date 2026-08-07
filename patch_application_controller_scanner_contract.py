from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import sys

ROOT = Path.cwd()
TARGET = ROOT / "core" / "application_controller.py"

if not TARGET.exists():
    print(f"ERROR: Target not found: {TARGET}")
    sys.exit(1)

text = TARGET.read_text(encoding="utf-8-sig")

old = '''        return self.scanner.execute(

            self.nse_engine.market_data

        )
'''

new = '''        # ScannerExecutor is stateful:
        # market data must be loaded before execute().
        self.scanner.load_market_data(
            self.nse_engine.market_data
        )

        print(
            "[SCANNER] Market data loaded:",
            len(self.nse_engine.market_data),
            "symbols",
        )

        results = self.scanner.execute()

        print(
            "[SCANNER] Executor completed:",
            len(results),
            "records",
        )

        return results
'''

if old not in text:
    print("=" * 68)
    print("PATCH NOT APPLIED")
    print("=" * 68)
    print("Expected execute_scanner block was not found.")
    print("No changes made.")
    sys.exit(2)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = TARGET.with_name(
    f"application_controller.before_scanner_contract_fix_{stamp}.py"
)

shutil.copy2(TARGET, backup)

updated = text.replace(old, new, 1)
TARGET.write_text(updated, encoding="utf-8")

try:
    py_compile.compile(str(TARGET), doraise=True)

except Exception as exc:
    shutil.copy2(backup, TARGET)

    print("=" * 68)
    print("PATCH FAILED - ORIGINAL RESTORED")
    print("=" * 68)
    print(f"Reason: {exc}")
    sys.exit(3)

print("=" * 68)
print("STOCKVERSITY SCANNER EXECUTOR CONTRACT FIX INSTALLED")
print("=" * 68)
print(f"Target : {TARGET}")
print(f"Backup : {backup}")
print()
print("Changed:")
print("  OLD: ScannerExecutor.execute(market_data)")
print("  NEW: ScannerExecutor.load_market_data(market_data)")
print("       ScannerExecutor.execute()")
print()
print("Added runtime diagnostics:")
print("  [SCANNER] Market data loaded: N symbols")
print("  [SCANNER] Executor completed: N records")
print()
print("Syntax validation: PASSED")
print("=" * 68)