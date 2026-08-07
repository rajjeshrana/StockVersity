from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import sys


ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "core" / "scanner" / "scanner_engine.py"

if not TARGET.exists():
    print(f"ERROR: {TARGET} not found.")
    sys.exit(1)


text = TARGET.read_text(encoding="utf-8")


OLD = '''    def _execute_scanner(
        self,
        scanner: BaseScanner,
    ) -> List[Signal]:

        scanner.reset()

        signals = scanner.run(
            self.market_data
        )

        if signals is None:

            return []

        return list(
            signals
        )
'''


NEW = '''    def _execute_scanner(
        self,
        scanner: BaseScanner,
    ) -> List[Signal]:

        scanner_name = getattr(
            scanner,
            "name",
            type(scanner).__name__,
        )

        print(
            f"[SCANNER EXEC] {scanner_name} START "
            f"| market_data={len(self.market_data)}"
        )

        try:

            scanner.reset()

            signals = scanner.run(
                self.market_data
            )

            if signals is None:
                signals = []

            signals = list(
                signals
            )

            print(
                f"[SCANNER EXEC] {scanner_name} DONE "
                f"| signals={len(signals)}"
            )

            return signals

        except Exception as exc:

            print(
                f"[SCANNER EXEC] {scanner_name} FAILED "
                f"| {type(exc).__name__}: {exc}"
            )

            raise
'''


if OLD not in text:

    if "[SCANNER EXEC]" in text:
        print("=" * 72)
        print("SCANNER ENGINE EXECUTION DIAGNOSTICS ALREADY INSTALLED")
        print("=" * 72)
        sys.exit(0)

    print("=" * 72)
    print("PATCH NOT APPLIED")
    print("=" * 72)
    print("_execute_scanner() block was not found.")
    print("No file was changed.")
    sys.exit(2)


stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = TARGET.with_name(
    "scanner_engine.before_execution_diagnostics_"
    f"{stamp}.py"
)

shutil.copy2(
    TARGET,
    backup,
)


updated = text.replace(
    OLD,
    NEW,
    1,
)

TARGET.write_text(
    updated,
    encoding="utf-8",
)


try:

    py_compile.compile(
        str(TARGET),
        doraise=True,
    )

except Exception as exc:

    shutil.copy2(
        backup,
        TARGET,
    )

    print("=" * 72)
    print("PATCH FAILED - ORIGINAL RESTORED")
    print("=" * 72)
    print(exc)
    sys.exit(3)


print("=" * 72)
print("STOCKVERSITY SCANNER EXECUTION DIAGNOSTICS INSTALLED")
print("=" * 72)
print(f"Target : {TARGET}")
print(f"Backup : {backup}")
print()
print("Diagnostic output:")
print("  Scanner START")
print("  Scanner DONE + signal count")
print("  Scanner FAILED + real exception")
print()
print("Trading rules       : UNCHANGED")
print("Scanner thresholds  : UNCHANGED")
print("Ranking              : UNCHANGED")
print("Market data          : UNCHANGED")
print("Parallel execution   : UNCHANGED")
print()
print("Syntax validation: PASSED")
print("=" * 72)