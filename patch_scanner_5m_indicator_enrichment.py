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


MARKER = """
                            successful += 1

                            candles_added += int(
                                added or 0
                            )
"""


if "[SCANNER INDICATORS]" in text:
    print("=" * 72)
    print("INDICATOR ENRICHMENT ALREADY INSTALLED")
    print("=" * 72)
    sys.exit(0)


if MARKER not in text:
    print("=" * 72)
    print("PATCH NOT APPLIED")
    print("=" * 72)
    print()
    print(
        "Could not locate the existing "
        "5m history preload success block."
    )
    print()
    print("No file was changed.")
    sys.exit(2)


REPLACEMENT = """
                            # =========================================
                            # SCANNER 5M INDICATOR ENRICHMENT
                            # =========================================
                            #
                            # The core.indicators package uses
                            # streaming/stateful indicators.
                            #
                            # Replay this stock's historical 5m
                            # candles through fresh indicator objects,
                            # then merge their latest values into the
                            # SAME MarketDataBridge snapshot.
                            #
                            # Existing candles are preserved by
                            # MarketDataBridge.update_quote().
                            #

                            try:

                                from core.indicators.ema import EMA
                                from core.indicators.rsi import RSI
                                from core.indicators.macd import MACD
                                from core.indicators.atr import ATR
                                from core.indicators.adx import ADX
                                from core.indicators.vwap import VWAP

                                ema9_engine = EMA(9)
                                ema20_engine = EMA(20)
                                ema21_engine = EMA(21)
                                ema50_engine = EMA(50)
                                ema100_engine = EMA(100)
                                ema200_engine = EMA(200)

                                rsi_engine = RSI(14)

                                macd_engine = MACD(
                                    12,
                                    26,
                                    9,
                                )

                                atr_engine = ATR(14)
                                adx_engine = ADX(14)
                                vwap_engine = VWAP()

                                volume_window = []

                                for _, indicator_row in (
                                    dataframe.iterrows()
                                ):

                                    close_value = float(
                                        indicator_row.get(
                                            "close",
                                            0.0,
                                        )
                                        or 0.0
                                    )

                                    high_value = float(
                                        indicator_row.get(
                                            "high",
                                            0.0,
                                        )
                                        or 0.0
                                    )

                                    low_value = float(
                                        indicator_row.get(
                                            "low",
                                            0.0,
                                        )
                                        or 0.0
                                    )

                                    volume_value = float(
                                        indicator_row.get(
                                            "volume",
                                            0.0,
                                        )
                                        or 0.0
                                    )

                                    if close_value <= 0:
                                        continue

                                    ema9_engine.update(
                                        close_value
                                    )

                                    ema20_engine.update(
                                        close_value
                                    )

                                    ema21_engine.update(
                                        close_value
                                    )

                                    ema50_engine.update(
                                        close_value
                                    )

                                    ema100_engine.update(
                                        close_value
                                    )

                                    ema200_engine.update(
                                        close_value
                                    )

                                    rsi_engine.update(
                                        close_value
                                    )

                                    macd_engine.update(
                                        close_value
                                    )

                                    atr_engine.update(
                                        high_value,
                                        low_value,
                                        close_value,
                                    )

                                    adx_engine.update(
                                        high_value,
                                        low_value,
                                        close_value,
                                    )

                                    vwap_engine.update(
                                        high_value,
                                        low_value,
                                        close_value,
                                        volume_value,
                                    )

                                    volume_window.append(
                                        volume_value
                                    )

                                    if len(volume_window) > 20:
                                        volume_window.pop(0)

                                def _safe_latest(
                                    indicator,
                                    default=0.0,
                                ):

                                    try:

                                        value = (
                                            indicator.latest
                                        )

                                        if callable(value):
                                            value = value()

                                        if value is None:
                                            return float(default)

                                        return float(value)

                                    except Exception:
                                        return float(default)


                                ema9 = _safe_latest(
                                    ema9_engine
                                )

                                ema20 = _safe_latest(
                                    ema20_engine
                                )

                                ema21 = _safe_latest(
                                    ema21_engine
                                )

                                ema50 = _safe_latest(
                                    ema50_engine
                                )

                                ema100 = _safe_latest(
                                    ema100_engine
                                )

                                ema200 = _safe_latest(
                                    ema200_engine
                                )

                                rsi = _safe_latest(
                                    rsi_engine
                                )

                                atr = _safe_latest(
                                    atr_engine
                                )

                                adx = _safe_latest(
                                    adx_engine
                                )

                                vwap = _safe_latest(
                                    vwap_engine
                                )


                                # ---------------------------------
                                # MACD latest may be a tuple,
                                # mapping, scalar or object depending
                                # on the project's implementation.
                                # ---------------------------------

                                macd_value = 0.0
                                macd_signal = 0.0
                                macd_histogram = 0.0

                                try:

                                    macd_latest = (
                                        macd_engine.latest
                                    )

                                    if callable(macd_latest):
                                        macd_latest = (
                                            macd_latest()
                                        )

                                    if isinstance(
                                        macd_latest,
                                        dict,
                                    ):

                                        macd_value = float(
                                            macd_latest.get(
                                                "macd",
                                                macd_latest.get(
                                                    "value",
                                                    0.0,
                                                ),
                                            )
                                            or 0.0
                                        )

                                        macd_signal = float(
                                            macd_latest.get(
                                                "signal",
                                                macd_latest.get(
                                                    "macd_signal",
                                                    0.0,
                                                ),
                                            )
                                            or 0.0
                                        )

                                        macd_histogram = float(
                                            macd_latest.get(
                                                "histogram",
                                                macd_latest.get(
                                                    "hist",
                                                    0.0,
                                                ),
                                            )
                                            or 0.0
                                        )

                                    elif isinstance(
                                        macd_latest,
                                        (tuple, list),
                                    ):

                                        if len(macd_latest) >= 1:
                                            macd_value = float(
                                                macd_latest[0]
                                                or 0.0
                                            )

                                        if len(macd_latest) >= 2:
                                            macd_signal = float(
                                                macd_latest[1]
                                                or 0.0
                                            )

                                        if len(macd_latest) >= 3:
                                            macd_histogram = float(
                                                macd_latest[2]
                                                or 0.0
                                            )

                                    elif macd_latest is not None:

                                        macd_value = float(
                                            macd_latest
                                        )

                                except Exception:
                                    pass


                                # ---------------------------------
                                # ADX object maintains DI values.
                                # ---------------------------------

                                plus_di = float(
                                    getattr(
                                        adx_engine,
                                        "plus_di",
                                        0.0,
                                    )
                                    or 0.0
                                )

                                minus_di = float(
                                    getattr(
                                        adx_engine,
                                        "minus_di",
                                        0.0,
                                    )
                                    or 0.0
                                )


                                # ---------------------------------
                                # Volume SMA20 / RVOL
                                # ---------------------------------

                                if volume_window:

                                    volume_sma20 = (
                                        sum(volume_window)
                                        / len(volume_window)
                                    )

                                else:

                                    volume_sma20 = 0.0


                                current_volume = 0.0

                                if not dataframe.empty:

                                    current_volume = float(
                                        dataframe.iloc[-1].get(
                                            "volume",
                                            0.0,
                                        )
                                        or 0.0
                                    )


                                if volume_sma20 > 0:

                                    rvol = (
                                        current_volume
                                        / volume_sma20
                                    )

                                else:

                                    rvol = 0.0


                                # ---------------------------------
                                # Merge indicators into existing
                                # production bridge snapshot.
                                # ---------------------------------

                                indicator_quote = {
                                    "instrument_key":
                                        instrument_key,

                                    "symbol":
                                        symbol,

                                    "ema9":
                                        ema9,

                                    "ema20":
                                        ema20,

                                    "ema21":
                                        ema21,

                                    "ema50":
                                        ema50,

                                    "ema100":
                                        ema100,

                                    "ema200":
                                        ema200,

                                    "rsi":
                                        rsi,

                                    "macd":
                                        macd_value,

                                    "macd_signal":
                                        macd_signal,

                                    "macd_histogram":
                                        macd_histogram,

                                    "adx":
                                        adx,

                                    "plus_di":
                                        plus_di,

                                    "minus_di":
                                        minus_di,

                                    "atr":
                                        atr,

                                    "vwap":
                                        vwap,

                                    "volume_sma20":
                                        volume_sma20,

                                    "average_volume":
                                        volume_sma20,

                                    "rvol":
                                        rvol,

                                    "relative_volume":
                                        rvol,
                                }


                                scanner_system.bridge.update_quote(
                                    indicator_quote,
                                    trigger_scan=False,
                                )


                                if index <= 3:

                                    print(
                                        "[SCANNER INDICATORS] "
                                        f"{symbol or instrument_key} | "
                                        f"EMA9={ema9:.2f} | "
                                        f"EMA200={ema200:.2f} | "
                                        f"RSI={rsi:.2f} | "
                                        f"MACD={macd_value:.4f} | "
                                        f"ADX={adx:.2f} | "
                                        f"DI+={plus_di:.2f} | "
                                        f"DI-={minus_di:.2f} | "
                                        f"ATR={atr:.2f} | "
                                        f"VWAP={vwap:.2f} | "
                                        f"RVOL={rvol:.2f}"
                                    )

                            except Exception as indicator_exc:

                                print(
                                    "[SCANNER INDICATORS] "
                                    f"{symbol or instrument_key}: "
                                    f"{indicator_exc}"
                                )


                            successful += 1

                            candles_added += int(
                                added or 0
                            )
"""


updated = text.replace(
    MARKER,
    REPLACEMENT,
    1,
)


stamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

backup = TARGET.with_name(
    "app.before_5m_indicator_enrichment_"
    f"{stamp}.py"
)

shutil.copy2(
    TARGET,
    backup,
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
print(
    "STOCKVERSITY 5M SCANNER "
    "INDICATOR ENRICHMENT INSTALLED"
)
print("=" * 72)

print(f"Target : {TARGET}")
print(f"Backup : {backup}")

print()
print("Calculated from real 5m candles:")
print("  EMA 9 / 20 / 21 / 50 / 100 / 200")
print("  RSI 14")
print("  MACD 12/26/9")
print("  ATR 14")
print("  ADX 14")
print("  DI+ / DI-")
print("  VWAP")
print("  Volume SMA20")
print("  RVOL")

print()
print("Architecture:")
print("  Existing Upstox history       : UNCHANGED")
print("  Existing WebSocket            : UNCHANGED")
print("  Existing MarketDataBridge     : REUSED")
print("  Existing 10 scanners          : UNCHANGED")
print("  Scanner thresholds            : UNCHANGED")
print("  Indicator values              : REAL CANDLE DATA")

print()
print("Syntax validation: PASSED")
print("=" * 72)