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
# Find the EXISTING working dashboard callback.
# We insert production-scanner forwarding immediately after it.
# ============================================================

needle = """            self.upstox_provider.add_tick_callback(
                self.live_market_bridge.on_tick
            )
"""

if needle not in text:
    print("=" * 72)
    print("PATCH NOT APPLIED")
    print("=" * 72)
    print(
        "Could not find the existing "
        "LiveMarketBridge tick callback."
    )
    print()
    print("No file was changed.")
    sys.exit(2)


# Prevent accidental duplicate installation.
if (
    "_forward_tick_to_production_scanner"
    in text
):
    print("=" * 72)
    print("PATCH NOT APPLIED")
    print("=" * 72)
    print(
        "Production scanner tick callback "
        "already appears to be installed."
    )
    print()
    print("No file was changed.")
    sys.exit(3)


insertion = needle + """
            # ---------------------------------------------
            # Provider -> Production Scanner
            # ---------------------------------------------
            #
            # Feed the SAME parsed Upstox Tick used by the
            # dashboard into the shared production scanner.
            #
            # No second WebSocket is created.
            # No second market subscription is created.
            #

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

            print(
                "[PRODUCTION SCANNER] "
                "Shared scanner system initialized."
            )

            def _forward_tick_to_production_scanner(
                tick,
            ):

                try:

                    if tick is None:
                        return

                    instrument_key = str(
                        getattr(
                            tick,
                            "instrument_key",
                            "",
                        )
                        or ""
                    ).strip()

                    if not instrument_key:
                        return

                    symbol = str(
                        getattr(
                            tick,
                            "symbol",
                            "",
                        )
                        or ""
                    ).strip()

                    ltp = float(
                        getattr(
                            tick,
                            "ltp",
                            0.0,
                        )
                        or 0.0
                    )

                    if ltp <= 0:
                        return

                    quote = {
                        "instrument_key":
                            instrument_key,

                        "symbol":
                            symbol,

                        "ltp":
                            ltp,

                        "last_price":
                            ltp,

                        "price":
                            ltp,

                        "open":
                            float(
                                getattr(
                                    tick,
                                    "open",
                                    0.0,
                                )
                                or 0.0
                            ),

                        "high":
                            float(
                                getattr(
                                    tick,
                                    "high",
                                    0.0,
                                )
                                or 0.0
                            ),

                        "low":
                            float(
                                getattr(
                                    tick,
                                    "low",
                                    0.0,
                                )
                                or 0.0
                            ),

                        "close":
                            float(
                                getattr(
                                    tick,
                                    "close",
                                    0.0,
                                )
                                or 0.0
                            ),

                        "previous_close":
                            float(
                                getattr(
                                    tick,
                                    "previous_close",
                                    0.0,
                                )
                                or 0.0
                            ),

                        "volume":
                            int(
                                getattr(
                                    tick,
                                    "volume",
                                    0,
                                )
                                or 0
                            ),

                        "average_price":
                            float(
                                getattr(
                                    tick,
                                    "average_price",
                                    0.0,
                                )
                                or 0.0
                            ),

                        "timestamp":
                            getattr(
                                tick,
                                "timestamp",
                                0,
                            ),
                    }

                    self.scanner_system.update_market_quotes(
                        [quote],
                        trigger_scan=False,
                    )

                except Exception as exc:

                    print(
                        "[PRODUCTION SCANNER] "
                        "Tick forwarding error: "
                        f"{exc}"
                    )


            self._forward_tick_to_production_scanner = (
                _forward_tick_to_production_scanner
            )

            self.upstox_provider.add_tick_callback(
                self._forward_tick_to_production_scanner
            )

            print(
                "[PRODUCTION SCANNER] "
                "Live Upstox tick callback attached."
            )
"""


updated = text.replace(
    needle,
    insertion,
    1,
)


# ============================================================
# Backup
# ============================================================

stamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

backup = TARGET.with_name(
    "app.before_provider_scanner_bridge_"
    f"{stamp}.py"
)

shutil.copy2(
    TARGET,
    backup,
)


# ============================================================
# Write
# ============================================================

TARGET.write_text(
    updated,
    encoding="utf-8",
)


# ============================================================
# Validate syntax
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
    print(f"Reason: {exc}")
    print()
    print(
        "ui/app.py has been restored "
        "from backup."
    )

    sys.exit(4)


print("=" * 72)
print(
    "STOCKVERSITY LIVE PROVIDER -> "
    "PRODUCTION SCANNER BRIDGE INSTALLED"
)
print("=" * 72)

print(f"Target : {TARGET}")
print(f"Backup : {backup}")

print()
print("Added pipeline:")
print()
print("  Existing UpstoxProvider")
print("          |")
print("          +--> LiveMarketBridge")
print("          |")
print("          +--> Production Scanner")
print()
print("Production scanner receives:")
print("  instrument_key")
print("  symbol")
print("  ltp")
print("  OHLC")
print("  previous_close")
print("  volume")
print("  average_price")
print("  timestamp")

print()
print(
    "Uses update_market_quotes([quote], "
    "trigger_scan=False)"
)

print()
print("UNCHANGED:")
print("  Existing Upstox WebSocket")
print("  Existing NIFTY 500 subscription")
print("  LiveMarketBridge")
print("  LiveStockUniverse")
print("  Dashboard")
print("  Historical previous-close system")

print()
print("Syntax validation: PASSED")
print("=" * 72)