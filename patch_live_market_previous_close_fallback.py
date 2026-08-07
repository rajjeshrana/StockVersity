from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import sys

ROOT = Path.cwd()
TARGET = ROOT / "ui" / "live_market_bridge.py"

if not TARGET.exists():
    print(f"ERROR: Target not found: {TARGET}")
    sys.exit(1)

text = TARGET.read_text(encoding="utf-8-sig")

# ------------------------------------------------------------
# PATCH 1
# Add previous-close cache to __init__
# ------------------------------------------------------------

old_init = '''        self.max_history = 60

        # Queued Qt signal crossing worker -> GUI thread.
'''

new_init = '''        self.max_history = 60

        # -----------------------------------------------------
        # HISTORICAL PREVIOUS-CLOSE FALLBACK
        # -----------------------------------------------------
        # Populated once during application startup.
        # Used only when an incoming WebSocket tick does not
        # contain a valid previous_close value.
        self.previous_closes: Dict[str, float] = {}

        # Queued Qt signal crossing worker -> GUI thread.
'''

if old_init not in text:
    print("PATCH NOT APPLIED: __init__ insertion point not found.")
    sys.exit(2)

text = text.replace(old_init, new_init, 1)

# ------------------------------------------------------------
# PATCH 2
# Add setter method before WEBSOCKET CALLBACK
# ------------------------------------------------------------

old_callback_header = '''    # =====================================================
    # WEBSOCKET CALLBACK
    # =====================================================
'''

new_callback_header = '''    # =====================================================
    # HISTORICAL PREVIOUS CLOSE
    # =====================================================

    def set_previous_closes(
        self,
        values: Dict[str, float],
    ) -> None:
        """
        Store latest completed-session closes.

        Keys must be Upstox instrument keys, for example:
            NSE_INDEX|Nifty 50
            NSE_INDEX|Nifty Bank
            NSE_INDEX|Nifty Fin Service
            NSE_INDEX|India VIX
        """

        cleaned: Dict[str, float] = {}

        for instrument_key, value in (values or {}).items():

            close = self._number(value)

            if instrument_key and close > 0:
                cleaned[str(instrument_key)] = close

        self.previous_closes = cleaned

        logger.info(
            "Historical previous closes loaded for %d indices.",
            len(cleaned),
        )

    # =====================================================
    # WEBSOCKET CALLBACK
    # =====================================================
'''

if old_callback_header not in text:
    print("PATCH NOT APPLIED: callback header not found.")
    sys.exit(3)

text = text.replace(
    old_callback_header,
    new_callback_header,
    1,
)

# ------------------------------------------------------------
# PATCH 3
# Use historical close if tick.previous_close is absent/zero
# ------------------------------------------------------------

old_previous_close = '''            previous_close = self._number(
                getattr(
                    tick,
                    "previous_close",
                    0.0,
                )
            )

            # ---------------------------------------------
            # CHANGE %
'''

new_previous_close = '''            previous_close = self._number(
                getattr(
                    tick,
                    "previous_close",
                    0.0,
                )
            )

            # Some Upstox index ticks may not provide a
            # usable previous_close. Fall back to the latest
            # completed daily candle loaded during startup.
            if previous_close <= 0:

                previous_close = self._number(
                    self.previous_closes.get(
                        instrument_key,
                        0.0,
                    )
                )

            # ---------------------------------------------
            # CHANGE %
'''

if old_previous_close not in text:
    print("PATCH NOT APPLIED: previous_close block not found.")
    sys.exit(4)

text = text.replace(
    old_previous_close,
    new_previous_close,
    1,
)

# ------------------------------------------------------------
# BACKUP + WRITE + VALIDATE
# ------------------------------------------------------------

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = TARGET.with_name(
    f"live_market_bridge.before_previous_close_fallback_{stamp}.py"
)

shutil.copy2(TARGET, backup)

TARGET.write_text(text, encoding="utf-8")

try:
    py_compile.compile(str(TARGET), doraise=True)

except Exception as exc:

    shutil.copy2(backup, TARGET)

    print("=" * 68)
    print("PATCH FAILED - ORIGINAL RESTORED")
    print("=" * 68)
    print(f"Reason: {exc}")
    sys.exit(5)

print("=" * 68)
print("STOCKVERSITY LIVE MARKET PREVIOUS-CLOSE FALLBACK INSTALLED")
print("=" * 68)
print(f"Target : {TARGET}")
print(f"Backup : {backup}")
print()
print("Added:")
print("  LiveMarketBridge.previous_closes")
print("  LiveMarketBridge.set_previous_closes(...)")
print("  Historical fallback when tick.previous_close <= 0")
print()
print("WebSocket architecture: UNCHANGED")
print("MarketController wiring: UNCHANGED")
print("Info-card wiring: UNCHANGED")
print("Syntax validation: PASSED")
print("=" * 68)