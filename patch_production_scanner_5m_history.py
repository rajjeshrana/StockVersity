from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import sys


ROOT = Path.cwd()
TARGET = ROOT / "ui" / "app.py"

if not TARGET.exists():
    print(f"ERROR: Target not found: {TARGET}")
    sys.exit(1)


text = TARGET.read_text(
    encoding="utf-8-sig"
)


# ============================================================
# We attach history preload immediately after the existing
# NIFTY 500 live subscription has been established.
# ============================================================

needle = """            self.upstox_provider.subscribe_many(
                nifty500_instruments,
                mode="ltpc",
            )
"""

if needle not in text:
    print("=" * 72)
    print("PATCH NOT APPLIED")
    print("=" * 72)
    print(
        "Could not find existing "
        "NIFTY 500 subscribe_many() block."
    )
    print()
    print("No file was changed.")
    sys.exit(2)


if "_scanner_history_preload_worker" in text:
    print("=" * 72)
    print("PATCH NOT APPLIED")
    print("=" * 72)
    print(
        "Scanner historical preload "
        "already appears to be installed."
    )
    print()
    print("No file was changed.")
    sys.exit(3)


insertion = needle + """
            # =================================================
            # PRODUCTION SCANNER - 5 MIN HISTORICAL BOOTSTRAP
            # =================================================
            #
            # Live quotes are already flowing into the shared
            # production MarketDataBridge.
            #
            # Pattern scanners also require candle history.
            # Load 5-minute history in a BACKGROUND THREAD so
            # the Qt UI remains responsive.
            #
            # Uses:
            #   existing self.upstox_history_client
            #   existing NIFTY 500 universe
            #   existing shared ScannerBootstrap
            #
            # No second WebSocket.
            # No second login.
            # No duplicate live subscription.
            #

            import threading
            from datetime import date, timedelta

            def _scanner_history_preload_worker():

                try:

                    scanner_system = getattr(
                        self,
                        "scanner_system",
                        None,
                    )

                    if scanner_system is None:

                        from core.scanner.scanner_bootstrap import (
                            get_scanner_system,
                        )

                        scanner_system = (
                            get_scanner_system()
                        )

                        scanner_system.initialize()

                        self.scanner_system = (
                            scanner_system
                        )

                    universe = getattr(
                        self,
                        "nifty500_universe",
                        None,
                    )

                    if universe is None:

                        print(
                            "[SCANNER HISTORY] "
                            "NIFTY 500 universe unavailable."
                        )

                        return

                    instrument_keys = list(
                        universe.instrument_keys()
                    )

                    symbol_map = {}

                    try:

                        by_symbol = (
                            universe.by_symbol()
                        )

                        for symbol, stock in (
                            by_symbol.items()
                        ):

                            key = str(
                                getattr(
                                    stock,
                                    "instrument_key",
                                    "",
                                )
                                or ""
                            ).strip()

                            if key:
                                symbol_map[key] = str(
                                    symbol
                                )

                    except Exception as exc:

                        print(
                            "[SCANNER HISTORY] "
                            "Symbol-map warning: "
                            f"{exc}"
                        )

                    total = len(
                        instrument_keys
                    )

                    if total <= 0:

                        print(
                            "[SCANNER HISTORY] "
                            "No NIFTY 500 instruments found."
                        )

                        return

                    print(
                        "[SCANNER HISTORY] "
                        f"Starting 5m preload: "
                        f"{total} instruments."
                    )

                    history_to = date.today()

                    # Five calendar days normally provides
                    # several completed trading sessions and
                    # enough 5-minute bars for intraday logic.
                    history_from = (
                        history_to
                        - timedelta(days=5)
                    )

                    successful = 0
                    failed = 0
                    candles_added = 0

                    for index, instrument_key in enumerate(
                        instrument_keys,
                        start=1,
                    ):

                        try:

                            dataframe = (
                                self.upstox_history_client
                                .historical_data(
                                    instrument_key,
                                    "5m",
                                    history_from.isoformat(),
                                    history_to.isoformat(),
                                )
                            )

                            if (
                                dataframe is None
                                or dataframe.empty
                            ):
                                failed += 1
                                continue

                            records = []

                            for _, row in (
                                dataframe.iterrows()
                            ):

                                timestamp = (
                                    row.get(
                                        "datetime",
                                        None,
                                    )
                                )

                                if hasattr(
                                    timestamp,
                                    "isoformat",
                                ):
                                    timestamp = (
                                        timestamp.isoformat()
                                    )

                                candle = {
                                    "timestamp":
                                        timestamp,

                                    "open":
                                        float(
                                            row.get(
                                                "open",
                                                0.0,
                                            )
                                            or 0.0
                                        ),

                                    "high":
                                        float(
                                            row.get(
                                                "high",
                                                0.0,
                                            )
                                            or 0.0
                                        ),

                                    "low":
                                        float(
                                            row.get(
                                                "low",
                                                0.0,
                                            )
                                            or 0.0
                                        ),

                                    "close":
                                        float(
                                            row.get(
                                                "close",
                                                0.0,
                                            )
                                            or 0.0
                                        ),

                                    "volume":
                                        int(
                                            row.get(
                                                "volume",
                                                0,
                                            )
                                            or 0
                                        ),
                                }

                                records.append(
                                    candle
                                )

                            if not records:
                                failed += 1
                                continue

                            symbol = symbol_map.get(
                                instrument_key,
                                "",
                            )

                            added = (
                                scanner_system.bridge
                                .add_candles(
                                    instrument_key,
                                    "5m",
                                    records,
                                    symbol=symbol,
                                    max_candles=500,
                                )
                            )

                            successful += 1

                            candles_added += int(
                                added or 0
                            )

                        except Exception as exc:

                            failed += 1

                            # Avoid flooding terminal with
                            # hundreds of errors. Show the
                            # first few and continue.
                            if failed <= 10:

                                print(
                                    "[SCANNER HISTORY] "
                                    f"{instrument_key}: "
                                    f"{exc}"
                                )

                        if (
                            index % 25 == 0
                            or index == total
                        ):

                            print(
                                "[SCANNER HISTORY] "
                                f"Progress: "
                                f"{index}/{total} | "
                                f"OK={successful} | "
                                f"Failed={failed} | "
                                f"Candles={candles_added}"
                            )

                    print(
                        "[SCANNER HISTORY] "
                        "5m preload complete. "
                        f"Instruments={successful}/{total}, "
                        f"Failed={failed}, "
                        f"Candles={candles_added}"
                    )

                    try:

                        bridge_status = (
                            scanner_system.bridge.status()
                        )

                        print(
                            "[SCANNER HISTORY] "
                            "Bridge after preload: "
                            f"{bridge_status}"
                        )

                    except Exception:
                        pass

                except Exception as exc:

                    import traceback

                    print(
                        "[SCANNER HISTORY] "
                        "Preload worker failed: "
                        f"{exc}"
                    )

                    traceback.print_exc()


            self._scanner_history_preload_worker = (
                _scanner_history_preload_worker
            )

            self._scanner_history_thread = (
                threading.Thread(
                    target=(
                        self
                        ._scanner_history_preload_worker
                    ),
                    name=(
                        "StockVersityScannerHistory"
                    ),
                    daemon=True,
                )
            )

            self._scanner_history_thread.start()

            print(
                "[SCANNER HISTORY] "
                "Background 5m preload started."
            )
"""


updated = text.replace(
    needle,
    insertion,
    1,
)


# ============================================================
# BACKUP
# ============================================================

stamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

backup = TARGET.with_name(
    "app.before_scanner_5m_history_"
    f"{stamp}.py"
)

shutil.copy2(
    TARGET,
    backup,
)


# ============================================================
# WRITE
# ============================================================

TARGET.write_text(
    updated,
    encoding="utf-8",
)


# ============================================================
# VALIDATE
# ============================================================

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
    print()
    print(exc)
    print()
    print(
        "ui/app.py restored from backup."
    )

    sys.exit(4)


print("=" * 72)
print(
    "STOCKVERSITY PRODUCTION SCANNER "
    "5M HISTORY BOOTSTRAP INSTALLED"
)
print("=" * 72)

print(f"Target : {TARGET}")
print(f"Backup : {backup}")

print()
print("Pipeline:")
print(
    "  Existing Upstox historical client"
)
print("          |")
print("          v")
print("  NIFTY 500 - 5m history")
print("          |")
print("          v")
print(
    "  MarketDataBridge.add_candles()"
)
print("          |")
print("          v")
print("  10 production scanners")

print()
print("Behaviour:")
print(
    "  Runs in background daemon thread"
)
print(
    "  UI remains responsive"
)
print(
    "  Uses existing authenticated client"
)
print(
    "  Uses existing scanner singleton"
)
print(
    "  Does NOT create another WebSocket"
)
print(
    "  Does NOT duplicate live subscription"
)
print(
    "  One failed stock does not stop preload"
)

print()
print("Syntax validation: PASSED")
print("=" * 72)