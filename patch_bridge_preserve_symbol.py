from pathlib import Path
from datetime import datetime
import shutil
import py_compile


TARGET = Path(r"D:\StockVersityScanner\core\scanner\market_data_bridge.py")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

BACKUP = TARGET.with_name(
    f"market_data_bridge.before_symbol_preservation_{timestamp}.py"
)


print("=" * 72)
print("STOCKVERSITY BRIDGE SYMBOL PRESERVATION PATCH")
print("=" * 72)


if not TARGET.exists():
    raise FileNotFoundError(TARGET)


source = TARGET.read_text(encoding="utf-8")


# ------------------------------------------------------------
# Exact target block
# ------------------------------------------------------------

OLD = '''                existing.update(
                    normalized
                )

                existing["candles"] = (
                    candles
                )
'''


NEW = '''                # -------------------------------------------------
                # PRESERVE EXISTING SYMBOL
                # -------------------------------------------------
                #
                # Some live/enrichment updates do not carry a valid
                # trading symbol. normalize_quote() may therefore
                # produce symbol="".
                #
                # Never allow an empty incoming symbol to overwrite
                # a valid symbol already stored in the bridge.
                #
                existing_symbol = str(
                    existing.get(
                        "symbol",
                        ""
                    )
                    or ""
                ).strip()

                incoming_symbol = str(
                    normalized.get(
                        "symbol",
                        ""
                    )
                    or ""
                ).strip()

                if (
                    existing_symbol
                    and not incoming_symbol
                ):
                    normalized["symbol"] = (
                        existing_symbol
                    )

                existing.update(
                    normalized
                )

                existing["candles"] = (
                    candles
                )
'''


if OLD not in source:
    print()
    print("Could not locate exact update block.")
    print("No changes made.")
    raise SystemExit(1)


# ------------------------------------------------------------
# Backup
# ------------------------------------------------------------

shutil.copy2(
    TARGET,
    BACKUP,
)


# ------------------------------------------------------------
# Patch
# ------------------------------------------------------------

source = source.replace(
    OLD,
    NEW,
    1,
)


TARGET.write_text(
    source,
    encoding="utf-8",
)


# ------------------------------------------------------------
# Syntax validation
# ------------------------------------------------------------

py_compile.compile(
    str(TARGET),
    doraise=True,
)


print()
print("[PATCH] Existing non-empty symbol is now preserved.")
print()
print("=" * 72)
print("STOCKVERSITY BRIDGE SYMBOL PRESERVATION INSTALLED")
print("=" * 72)

print(f"Target : {TARGET}")
print(f"Backup : {BACKUP}")

print()
print("Behaviour:")
print("  Existing symbol + empty incoming symbol -> PRESERVE existing")
print("  Existing symbol + valid incoming symbol -> ACCEPT incoming")
print("  No existing symbol + valid incoming      -> ACCEPT incoming")
print("  Candle preservation                     -> UNCHANGED")
print("  WebSocket pipeline                       -> UNCHANGED")
print("  Indicator values                         -> UNCHANGED")
print("  Scanner rules                            -> UNCHANGED")
print("  Scanner thresholds                       -> UNCHANGED")

print()
print("Syntax validation: PASSED")
print("=" * 72)