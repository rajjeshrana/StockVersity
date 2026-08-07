from pathlib import Path
from datetime import datetime
import py_compile
import shutil

target = Path(
    r"D:\StockVersityScanner\core\scanner\market_data_bridge.py"
)

text = target.read_text(
    encoding="utf-8"
)

timestamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

backup = target.with_name(
    "market_data_bridge.before_zero_price_diagnostic_"
    + timestamp
    + ".py"
)

shutil.copy2(
    target,
    backup,
)

marker = """                existing.update(
                    normalized
                )
"""

diagnostic = """                # =================================================
                # STOCKVERSITY ZERO-PRICE OVERWRITE DIAGNOSTIC
                # Diagnostic only - no market data is modified.
                # =================================================

                try:
                    incoming_price_supplied = any(
                        alias in incoming_keys
                        for alias in (
                            "last_price",
                            "ltp",
                            "last_traded_price",
                            "lastTradedPrice",
                            "price",
                        )
                    )

                    incoming_normalized_price = float(
                        normalized.get(
                            "last_price",
                            0.0,
                        )
                        or 0.0
                    )

                    existing_price = float(
                        existing.get(
                            "last_price",
                            0.0,
                        )
                        or 0.0
                    )

                    if (
                        incoming_price_supplied
                        and incoming_normalized_price <= 0
                        and existing_price > 0
                    ):
                        diagnostic_symbol = (
                            existing.get("symbol")
                            or normalized.get("symbol")
                            or key
                        )

                        print(
                            "[BRIDGE ZERO PRICE OVERWRITE] "
                            f"{diagnostic_symbol} | "
                            f"key={key} | "
                            f"existing={existing_price:.2f} | "
                            f"incoming={incoming_normalized_price:.2f} | "
                            f"raw_ltp={data.get('ltp', '<missing>')} | "
                            f"raw_last_price={data.get('last_price', '<missing>')} | "
                            f"raw_price={data.get('price', '<missing>')} | "
                            f"keys={sorted(str(k) for k in incoming_keys)}"
                        )

                except Exception as diagnostic_exc:
                    print(
                        "[BRIDGE ZERO PRICE DIAGNOSTIC ERROR]",
                        repr(diagnostic_exc),
                    )

                existing.update(
                    normalized
                )
"""

if marker not in text:
    raise RuntimeError(
        "Could not locate existing.update(normalized) merge block. "
        "No changes made."
    )

if "STOCKVERSITY ZERO-PRICE OVERWRITE DIAGNOSTIC" in text:
    raise RuntimeError(
        "Zero-price diagnostic already installed."
    )

text = text.replace(
    marker,
    diagnostic,
    1,
)

target.write_text(
    text,
    encoding="utf-8",
)

py_compile.compile(
    str(target),
    doraise=True,
)

print("=" * 72)
print("STOCKVERSITY BRIDGE ZERO-PRICE DIAGNOSTIC INSTALLED")
print("=" * 72)
print("Target :", target)
print("Backup :", backup)
print()
print("Trading logic : UNCHANGED")
print("Bridge data   : UNCHANGED")
print("Zero blocking : NOT ENABLED")
print("Diagnostic    : ENABLED")
print()
print("Syntax validation: PASSED")
print("=" * 72)