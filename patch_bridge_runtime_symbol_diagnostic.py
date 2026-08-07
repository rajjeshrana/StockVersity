from pathlib import Path
from datetime import datetime
import py_compile
import shutil

TARGET = Path(r"D:\StockVersityScanner\ui\app.py")

text = TARGET.read_text(
    encoding="utf-8",
)

stamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

backup = TARGET.with_name(
    f"{TARGET.stem}.before_bridge_symbol_diagnostic_{stamp}.py"
)

shutil.copy2(
    TARGET,
    backup,
)

needle = '''                    print(
                        "[SCANNER HISTORY] "
                        "5m preload complete. "
                        f"Instruments={successful}/{total}, "
                        f"Failed={failed}, "
                        f"Candles={candles_added}"
                    )
'''

if needle not in text:
    print(
        "Could not locate preload-complete block."
    )
    raise SystemExit(1)

replacement = needle + '''
                    # =========================================
                    # BRIDGE SYMBOL RUNTIME DIAGNOSTIC
                    # =========================================
                    try:
                        bridge_data = (
                            scanner_system.bridge.market_data()
                        )

                        total_bridge = 0
                        with_symbol = 0
                        missing_symbol = 0

                        print(
                            "[BRIDGE SYMBOL DIAGNOSTIC] "
                            f"symbol_map={len(symbol_map)}"
                        )

                        for bridge_key, bridge_row in (
                            bridge_data.items()
                        ):
                            if not isinstance(
                                bridge_row,
                                dict,
                            ):
                                continue

                            total_bridge += 1

                            bridge_symbol = str(
                                bridge_row.get(
                                    "symbol",
                                    "",
                                )
                                or ""
                            ).strip()

                            if bridge_symbol:
                                with_symbol += 1
                            else:
                                missing_symbol += 1

                                if missing_symbol <= 10:
                                    print(
                                        "[BRIDGE SYMBOL MISSING] "
                                        f"{bridge_key} | "
                                        f"keys="
                                        f"{sorted(bridge_row.keys())}"
                                    )

                        print(
                            "[BRIDGE SYMBOL DIAGNOSTIC] "
                            f"Bridge={total_bridge} | "
                            f"WithSymbol={with_symbol} | "
                            f"MissingSymbol={missing_symbol}"
                        )

                    except Exception as symbol_diag_exc:
                        print(
                            "[BRIDGE SYMBOL DIAGNOSTIC] "
                            f"FAILED: {symbol_diag_exc}"
                        )
'''

text = text.replace(
    needle,
    replacement,
    1,
)

TARGET.write_text(
    text,
    encoding="utf-8",
)

py_compile.compile(
    str(TARGET),
    doraise=True,
)

print("=" * 72)
print("STOCKVERSITY BRIDGE SYMBOL RUNTIME DIAGNOSTIC INSTALLED")
print("=" * 72)
print(f"Target : {TARGET}")
print(f"Backup : {backup}")
print()
print("Trading logic      : UNCHANGED")
print("Scanner thresholds : UNCHANGED")
print("Market data        : UNCHANGED")
print("Diagnostic only    : ENABLED")
print()
print("Syntax validation: PASSED")
print("=" * 72)