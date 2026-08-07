from pathlib import Path
from datetime import datetime
import shutil
import py_compile


TARGET = Path(
    r"D:\StockVersityScanner\core\scanner\market_data_bridge.py"
)

if not TARGET.exists():
    raise FileNotFoundError(TARGET)


timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

BACKUP = TARGET.with_name(
    f"market_data_bridge.before_partial_update_fix_{timestamp}.py"
)

shutil.copy2(
    TARGET,
    BACKUP,
)

text = TARGET.read_text(
    encoding="utf-8"
)


# ============================================================
# We patch update_quote(), not scanner trading logic.
#
# normalize_quote() intentionally produces a complete normalized
# quote, using zero defaults for absent fields.
#
# That is acceptable for a NEW quote, but dangerous when an
# incoming message is only an enrichment/partial update.
#
# Example:
#
# {
#     "instrument_key": "...",
#     "symbol": "TCS",
#     "ema9": ...,
#     "rsi": ...
# }
#
# contains no LTP/OHLC/volume. normalize_quote() nevertheless
# creates:
#
# last_price = 0
# open = 0
# high = 0
# low = 0
# close = 0
# previous_close = 0
# volume = 0
#
# existing.update(normalized) would therefore destroy valid
# bridge values.
#
# The fix removes normalized market fields when the ORIGINAL
# incoming mapping did not provide the corresponding field.
# ============================================================


needle = '''            normalized = (
                self.normalize_quote(
                    data
                )
            )

            key = self._resolve_key(
                normalized
            )
'''


replacement = '''            normalized = (
                self.normalize_quote(
                    data
                )
            )

            # -------------------------------------------------
            # PARTIAL-UPDATE PROTECTION
            # -------------------------------------------------
            #
            # normalize_quote() creates zero/default values for
            # missing quote fields. That behaviour is useful when
            # normalizing a complete/new quote, but a partial
            # enrichment update (EMA/RSI/MACD/etc.) must NOT
            # overwrite valid live/historical market values with
            # synthetic zeros.
            #
            # Preserve an existing market field whenever none of
            # its accepted aliases was present in the ORIGINAL
            # incoming mapping.
            #
            # Important:
            # If a field really IS supplied by the provider, its
            # value is left untouched and is allowed to update the
            # bridge normally.
            # -------------------------------------------------

            incoming_keys = set(
                data.keys()
            )

            protected_fields = {

                "last_price": (
                    "last_price",
                    "ltp",
                    "last_traded_price",
                    "lastTradedPrice",
                    "price",
                ),

                "open": (
                    "open",
                    "open_price",
                    "openPrice",
                ),

                "high": (
                    "high",
                    "high_price",
                    "highPrice",
                ),

                "low": (
                    "low",
                    "low_price",
                    "lowPrice",
                ),

                "close": (
                    "close",
                    "close_price",
                    "closePrice",
                ),

                "previous_close": (
                    "previous_close",
                    "prev_close",
                    "previousClose",
                    "prevClose",
                ),

                "volume": (
                    "volume",
                    "total_volume",
                    "totalTradedVolume",
                    "ttv",
                ),

                "average_volume": (
                    "average_volume",
                    "avg_volume",
                    "averageVolume",
                ),

                "volume_ratio": (
                    "volume_ratio",
                    "rvol",
                    "relative_volume",
                ),
            }

            for (
                normalized_field,
                aliases,
            ) in protected_fields.items():

                supplied = any(
                    alias in incoming_keys
                    for alias in aliases
                )

                if not supplied:

                    normalized.pop(
                        normalized_field,
                        None,
                    )

            # change/change_percent are derived from LTP and
            # previous close by normalize_quote(). On a partial
            # enrichment update neither should replace the
            # existing bridge values unless price information was
            # actually supplied.
            #
            # If only one side is supplied, retaining a derived
            # zero would still be misleading, so require both.

            has_last_price = any(
                alias in incoming_keys
                for alias in protected_fields[
                    "last_price"
                ]
            )

            has_previous_close = any(
                alias in incoming_keys
                for alias in protected_fields[
                    "previous_close"
                ]
            )

            if not (
                has_last_price
                and has_previous_close
            ):

                normalized.pop(
                    "change",
                    None,
                )

                normalized.pop(
                    "change_percent",
                    None,
                )

            key = self._resolve_key(
                normalized
            )
'''


if needle not in text:
    raise RuntimeError(
        "Could not locate normalize_quote/update_quote block. "
        "No changes made."
    )


text = text.replace(
    needle,
    replacement,
    1,
)


TARGET.write_text(
    text,
    encoding="utf-8",
)


# ============================================================
# Syntax validation
# ============================================================

py_compile.compile(
    str(TARGET),
    doraise=True,
)


print("=" * 72)
print("STOCKVERSITY BRIDGE PARTIAL-UPDATE FIX INSTALLED")
print("=" * 72)
print()
print("Target :", TARGET)
print("Backup :", BACKUP)
print()
print("Fix:")
print("  Missing LTP       -> existing LTP preserved")
print("  Missing OHLC      -> existing OHLC preserved")
print("  Missing prev close-> existing previous close preserved")
print("  Missing volume    -> existing volume preserved")
print("  Indicator updates -> indicators still updated")
print("  Genuine quotes    -> supplied quote fields still updated")
print()
print("Trading logic      : UNCHANGED")
print("Scanner thresholds : UNCHANGED")
print("Momentum rules     : UNCHANGED")
print("UI score filter    : UNCHANGED")
print()
print("Syntax validation: PASSED")
print("=" * 72)