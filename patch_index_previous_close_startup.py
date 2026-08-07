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

text = TARGET.read_text(encoding="utf-8-sig")

old = '''            self.live_market_bridge = (
                LiveMarketBridge(
                    market_controller=(
                        self.market_controller
                    ),
                    parent=self,
                )
            )

            # ---------------------------------------------
            # Provider -> Qt bridge
'''

new = '''            self.live_market_bridge = (
                LiveMarketBridge(
                    market_controller=(
                        self.market_controller
                    ),
                    parent=self,
                )
            )

            # ---------------------------------------------
            # Previous-session index closes
            # ---------------------------------------------
            # Load once from the existing authenticated
            # historical REST client. These values are used
            # by LiveMarketBridge only when an incoming
            # WebSocket index tick does not contain a valid
            # previous_close.
            #
            # No second WebSocket or authentication session
            # is created here.

            try:

                from datetime import date, timedelta

                history_to = date.today()
                history_from = (
                    history_to
                    - timedelta(days=10)
                )

                index_history_keys = (
                    "NSE_INDEX|Nifty 50",
                    "NSE_INDEX|Nifty Bank",
                    "NSE_INDEX|Nifty Fin Service",
                    "NSE_INDEX|India VIX",
                )

                previous_closes = {}

                for instrument_key in index_history_keys:

                    try:

                        dataframe = (
                            self.upstox_history_client
                            .historical_data(
                                instrument_key,
                                "day",
                                history_from.isoformat(),
                                history_to.isoformat(),
                            )
                        )

                        if (
                            dataframe is not None
                            and not dataframe.empty
                            and "close" in dataframe.columns
                        ):

                            valid_close = (
                                dataframe["close"]
                                .dropna()
                            )

                            if not valid_close.empty:

                                close = float(
                                    valid_close.iloc[-1]
                                )

                                if close > 0:

                                    previous_closes[
                                        instrument_key
                                    ] = close

                                    print(
                                        "[INDEX HISTORY] "
                                        f"{instrument_key}: "
                                        f"previous close "
                                        f"{close:.2f}"
                                    )

                    except Exception as exc:

                        print(
                            "[INDEX HISTORY] "
                            f"Unable to load "
                            f"{instrument_key}: "
                            f"{exc}"
                        )

                self.live_market_bridge.set_previous_closes(
                    previous_closes
                )

                print(
                    "[INDEX HISTORY] "
                    f"Loaded {len(previous_closes)}/"
                    f"{len(index_history_keys)} "
                    "previous closes."
                )

            except Exception as exc:

                print(
                    "[INDEX HISTORY] "
                    "Previous-close bootstrap failed: "
                    f"{exc}"
                )

            # ---------------------------------------------
            # Provider -> Qt bridge
'''

if old not in text:
    print("=" * 68)
    print("PATCH NOT APPLIED")
    print("=" * 68)
    print("Expected LiveMarketBridge startup block was not found.")
    print("No changes made.")
    sys.exit(2)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = TARGET.with_name(
    f"app.before_index_previous_close_startup_{stamp}.py"
)

shutil.copy2(TARGET, backup)

updated = text.replace(old, new, 1)

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

    print("=" * 68)
    print("PATCH FAILED - ORIGINAL RESTORED")
    print("=" * 68)
    print(f"Reason: {exc}")
    sys.exit(3)

print("=" * 68)
print("STOCKVERSITY INDEX PREVIOUS-CLOSE STARTUP WIRING INSTALLED")
print("=" * 68)
print(f"Target : {TARGET}")
print(f"Backup : {backup}")
print()
print("Historical source:")
print("  Existing self.upstox_history_client")
print()
print("Indices:")
print("  NIFTY 50")
print("  BANK NIFTY")
print("  FIN NIFTY")
print("  INDIA VIX")
print()
print("Behaviour:")
print("  Loads latest completed daily close once at startup")
print("  Sends values to LiveMarketBridge.set_previous_closes()")
print("  Existing WebSocket remains unchanged")
print("  No hard-coded index values")
print()
print("Syntax validation: PASSED")
print("=" * 68)