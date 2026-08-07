from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import sys


ROOT = Path.cwd()
TARGET = ROOT / "core" / "indicator_engine.py"

if not TARGET.exists():
    print(f"ERROR: Target not found: {TARGET}")
    sys.exit(1)


text = TARGET.read_text(
    encoding="utf-8-sig"
)


OLD = "self.ema = EMAIndicator()"
NEW = "self.ema = EMAIndicator(20)"


if NEW in text:
    print("=" * 70)
    print("PATCH ALREADY INSTALLED")
    print("=" * 70)
    print(f"Target: {TARGET}")
    sys.exit(0)


if OLD not in text:
    print("=" * 70)
    print("PATCH NOT APPLIED")
    print("=" * 70)
    print()
    print(
        "Expected constructor line was not found:"
    )
    print()
    print(f"    {OLD}")
    print()
    print("No file was changed.")
    sys.exit(2)


stamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

backup = TARGET.with_name(
    "indicator_engine.before_ema_constructor_fix_"
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

    print("=" * 70)
    print(
        "PATCH FAILED - ORIGINAL RESTORED"
    )
    print("=" * 70)
    print(exc)
    sys.exit(3)


print("=" * 70)
print(
    "STOCKVERSITY INDICATOR ENGINE "
    "CONSTRUCTOR FIX INSTALLED"
)
print("=" * 70)

print(f"Target : {TARGET}")
print(f"Backup : {backup}")

print()
print("Changed:")
print(
    "  EMAIndicator()"
)
print("       ->")
print(
    "  EMAIndicator(20)"
)

print()
print(
    "EMA calculation periods remain dynamic."
)
print(
    "get_ema(..., period) still controls "
    "EMA 9/20/21/50/100/200."
)

print()
print("Syntax validation: PASSED")
print("=" * 70)