from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import sys


ROOT = Path.cwd()
TARGET = (
    ROOT
    / "core"
    / "scanner"
    / "market_data_bridge.py"
)

if not TARGET.exists():
    print(f"ERROR: Target not found: {TARGET}")
    sys.exit(1)


text = TARGET.read_text(
    encoding="utf-8-sig"
)


# ------------------------------------------------------------
# Find the existing passthrough tuple.
# We insert scanner indicator fields immediately after
# "exchange", which is already the last known field.
# ------------------------------------------------------------

OLD = '''            "exchange",

        )'''

NEW = '''            "exchange",

            # ---------------------------------------------
            # Scanner indicator enrichment
            # ---------------------------------------------

            "ema9",
            "ema20",
            "ema21",
            "ema50",
            "ema100",
            "ema200",

            "rsi",

            "macd",
            "macd_signal",
            "macd_histogram",

            "adx",
            "plus_di",
            "minus_di",

            "atr",

            "vwap",

            "volume_sma20",

            "rvol",
            "relative_volume",

        )'''


if '"plus_di"' in text and '"ema200"' in text:

    print("=" * 72)
    print(
        "BRIDGE INDICATOR PASSTHROUGH "
        "ALREADY INSTALLED"
    )
    print("=" * 72)

    sys.exit(0)


if OLD not in text:

    print("=" * 72)
    print("PATCH NOT APPLIED")
    print("=" * 72)

    print()
    print(
        "Expected passthrough tuple ending "
        "was not found."
    )

    print()
    print("No file was changed.")

    sys.exit(2)


# ------------------------------------------------------------
# Backup
# ------------------------------------------------------------

stamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

backup = TARGET.with_name(
    "market_data_bridge."
    "before_indicator_passthrough_"
    f"{stamp}.py"
)

shutil.copy2(
    TARGET,
    backup,
)


# ------------------------------------------------------------
# Patch
# ------------------------------------------------------------

updated = text.replace(
    OLD,
    NEW,
    1,
)

TARGET.write_text(
    updated,
    encoding="utf-8",
)


# ------------------------------------------------------------
# Syntax validation
# ------------------------------------------------------------

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
    print(
        "PATCH FAILED - ORIGINAL RESTORED"
    )
    print("=" * 72)

    print(exc)

    sys.exit(3)


print("=" * 72)
print(
    "STOCKVERSITY SCANNER INDICATOR "
    "PASSTHROUGH INSTALLED"
)
print("=" * 72)

print(f"Target : {TARGET}")
print(f"Backup : {backup}")

print()
print("Preserved scanner fields:")
print("  EMA 9 / 20 / 21 / 50 / 100 / 200")
print("  RSI")
print("  MACD / Signal / Histogram")
print("  ADX / DI+ / DI-")
print("  ATR")
print("  VWAP")
print("  Volume SMA20")
print("  RVOL")

print()
print(
    "Existing live quote normalization: UNCHANGED"
)
print(
    "Existing candle preservation: UNCHANGED"
)
print(
    "Existing WebSocket pipeline: UNCHANGED"
)

print()
print("Syntax validation: PASSED")
print("=" * 72)