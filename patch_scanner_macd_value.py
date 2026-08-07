from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import sys


ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "ui" / "app.py"

if not TARGET.exists():
    print(f"ERROR: {TARGET} not found.")
    sys.exit(1)


text = TARGET.read_text(
    encoding="utf-8"
)


OLD = '''                                    elif macd_latest is not None:

                                        macd_value = float(
                                            macd_latest
                                        )

                                except Exception:
                                    pass
'''


NEW = '''                                    elif (
                                        macd_latest is not None
                                        and hasattr(
                                            macd_latest,
                                            "macd",
                                        )
                                    ):

                                        macd_value = float(
                                            getattr(
                                                macd_latest,
                                                "macd",
                                                0.0,
                                            )
                                            or 0.0
                                        )

                                        macd_signal = float(
                                            getattr(
                                                macd_latest,
                                                "signal",
                                                0.0,
                                            )
                                            or 0.0
                                        )

                                        macd_histogram = float(
                                            getattr(
                                                macd_latest,
                                                "histogram",
                                                0.0,
                                            )
                                            or 0.0
                                        )

                                    elif macd_latest is not None:

                                        try:
                                            macd_value = float(
                                                macd_latest
                                            )
                                        except (
                                            TypeError,
                                            ValueError,
                                        ):
                                            pass

                                except Exception as macd_exc:

                                    print(
                                        "[SCANNER MACD] "
                                        f"{symbol or instrument_key}: "
                                        f"{macd_exc}"
                                    )
'''


if OLD not in text:

    if '"SCANNER MACD"' in text:
        print("=" * 72)
        print("MACD VALUE ADAPTER ALREADY INSTALLED")
        print("=" * 72)
        sys.exit(0)

    print("=" * 72)
    print("PATCH NOT APPLIED")
    print("=" * 72)
    print(
        "Could not locate the existing MACD "
        "adapter block in ui/app.py."
    )
    print("No file was changed.")
    sys.exit(2)


stamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

backup = TARGET.with_name(
    "app.before_macd_value_fix_"
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
print("STOCKVERSITY MACD VALUE ADAPTER INSTALLED")
print("=" * 72)
print(f"Target : {TARGET}")
print(f"Backup : {backup}")

print()
print("MACD object mapping:")
print("  MACDValue.macd       -> macd")
print("  MACDValue.signal     -> macd_signal")
print("  MACDValue.histogram  -> macd_histogram")

print()
print("MACD calculation engine : UNCHANGED")
print("Scanner architecture    : UNCHANGED")
print("Historical candles      : UNCHANGED")
print("WebSocket               : UNCHANGED")
print()
print("Syntax validation: PASSED")
print("=" * 72)