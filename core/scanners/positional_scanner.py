"""
=========================================================
StockVersity Scanner Pro
Positional Scanner
Version : 2.1
=========================================================

File:
    core/scanners/positional_scanner.py

Purpose
-------
Detect high-quality positional trading opportunities
using medium/long-term trend, breakout, momentum,
volume, sector strength and risk/reward analysis.

Primary Use
-----------
• 3-week breakout
• Monthly breakout
• Multi-month breakout
• 52-week / yearly breakout
• Long-term trend continuation
• Positional BUY opportunities
• Positional SELL opportunities

Core Filters
------------
• Price >= ₹200
• Market cap >= ₹1000 Cr when available
• Gap <= 3%
• EMA 20 / 50 / 100 / 200 structure
• RSI confirmation
• MACD confirmation
• ADX trend strength
• Relative volume
• Relative strength
• Sector strength
• Market trend
• Breakout confirmation
• Minimum 1:2 risk/reward
=========================================================
"""

from __future__ import annotations

from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
)

from core.scanner.base_scanner import BaseScanner

from core.scanner.signal import (
    MarketTrend,
    PatternType,
    Signal,
    SignalStrength,
    SignalType,
)


# =========================================================
# CONSTANTS
# =========================================================

SCANNER_NAME = "PositionalScanner"

SCANNER_VERSION = "2.1"

DEFAULT_TIMEFRAME = "1D"

DEFAULT_MINIMUM_PRICE = 200.0

DEFAULT_MINIMUM_MARKET_CAP = 1000.0

DEFAULT_MAXIMUM_GAP_PERCENT = 3.0

DEFAULT_MINIMUM_SCORE = 70.0

DEFAULT_MINIMUM_CONFIDENCE = 65.0

DEFAULT_MINIMUM_RR = 2.0

DEFAULT_MINIMUM_ADX = 20.0

DEFAULT_MINIMUM_VOLUME_RATIO = 1.20

DEFAULT_BREAKOUT_VOLUME_RATIO = 1.50

DEFAULT_BREAKOUT_TOLERANCE = 2.0


# =========================================================
# HELPERS
# =========================================================

def _float(
    value: Any,
    default: float = 0.0,
) -> float:

    try:

        if value is None:
            return default

        return float(value)

    except (TypeError, ValueError):

        return default


def _int(
    value: Any,
    default: int = 0,
) -> int:

    try:

        if value is None:
            return default

        return int(value)

    except (TypeError, ValueError):

        return default


def _get(
    data: Dict[str, Any],
    *keys: str,
    default: Any = None,
) -> Any:

    for key in keys:

        if key not in data:
            continue

        value = data.get(key)

        if value is not None:
            return value

    return default


# =========================================================
# POSITIONAL SCANNER
# =========================================================

class PositionalScanner(BaseScanner):
    """
    Long-term positional opportunity scanner.

    The scanner supports:

        3-week breakout
        1-month breakout
        2-month breakout
        3-month breakout
        6-month breakout
        52-week breakout

    It can also detect strong trend-continuation
    opportunities even when price has not yet broken
    the major resistance.
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        *,
        timeframe: str = DEFAULT_TIMEFRAME,
        minimum_price: float = DEFAULT_MINIMUM_PRICE,
        minimum_market_cap: float = (
            DEFAULT_MINIMUM_MARKET_CAP
        ),
        maximum_gap_percent: float = (
            DEFAULT_MAXIMUM_GAP_PERCENT
        ),
        minimum_score: float = DEFAULT_MINIMUM_SCORE,
        minimum_confidence: float = (
            DEFAULT_MINIMUM_CONFIDENCE
        ),
        minimum_rr: float = DEFAULT_MINIMUM_RR,
        minimum_adx: float = DEFAULT_MINIMUM_ADX,
        minimum_volume_ratio: float = (
            DEFAULT_MINIMUM_VOLUME_RATIO
        ),
        breakout_volume_ratio: float = (
            DEFAULT_BREAKOUT_VOLUME_RATIO
        ),
        breakout_tolerance_percent: float = (
            DEFAULT_BREAKOUT_TOLERANCE
        ),
    ) -> None:

        super().__init__(
            name=SCANNER_NAME,
            version=SCANNER_VERSION,
            timeframe=timeframe,
        )

        self.minimum_price = max(
            0.0,
            float(minimum_price),
        )

        self.minimum_market_cap = max(
            0.0,
            float(minimum_market_cap),
        )

        self.maximum_gap_percent = max(
            0.0,
            float(maximum_gap_percent),
        )

        self.minimum_score = max(
            0.0,
            float(minimum_score),
        )

        self.minimum_confidence = max(
            0.0,
            float(minimum_confidence),
        )

        self.minimum_rr = max(
            1.0,
            float(minimum_rr),
        )

        self.minimum_adx = max(
            0.0,
            float(minimum_adx),
        )

        self.minimum_volume_ratio = max(
            0.0,
            float(minimum_volume_ratio),
        )

        self.breakout_volume_ratio = max(
            0.0,
            float(breakout_volume_ratio),
        )

        self.breakout_tolerance_percent = max(
            0.0,
            float(breakout_tolerance_percent),
        )

        self.max_signals = 30

    # =====================================================
    # SCAN
    # =====================================================

    def scan(
        self,
        market_data: Dict[str, Any],
    ) -> List[Signal]:

        results: List[Signal] = []

        for (
            instrument_key,
            data,
        ) in self._iter_market_data(
            market_data
        ):

            try:

                signal = self._scan_symbol(
                    instrument_key,
                    data,
                )

                if signal is not None:

                    results.append(
                        signal
                    )

            except Exception as exc:

                self.log(
                    "Positional scan error:",
                    instrument_key,
                    repr(exc),
                )

        return results

    # =====================================================
    # MARKET DATA ITERATOR
    # =====================================================

    def _iter_market_data(
        self,
        market_data: Dict[str, Any],
    ) -> Iterable[
        Tuple[str, Dict[str, Any]]
    ]:

        if not isinstance(
            market_data,
            dict,
        ):
            return

        symbols = market_data.get(
            "symbols"
        )

        if isinstance(
            symbols,
            dict,
        ):

            for key, value in symbols.items():

                if not isinstance(
                    value,
                    dict,
                ):
                    continue

                instrument_key = str(
                    _get(
                        value,
                        "instrument_key",
                        default=key,
                    )
                )

                yield (
                    instrument_key,
                    value,
                )

            return

        data_block = market_data.get(
            "data"
        )

        if isinstance(
            data_block,
            dict,
        ):

            for key, value in data_block.items():

                if not isinstance(
                    value,
                    dict,
                ):
                    continue

                instrument_key = str(
                    _get(
                        value,
                        "instrument_key",
                        default=key,
                    )
                )

                yield (
                    instrument_key,
                    value,
                )

            return

        for key, value in market_data.items():

            if not isinstance(
                value,
                dict,
            ):
                continue

            instrument_key = str(
                _get(
                    value,
                    "instrument_key",
                    default=key,
                )
            )

            yield (
                instrument_key,
                value,
            )

    # =====================================================
    # SCAN ONE SYMBOL
    # =====================================================

    def _scan_symbol(
        self,
        instrument_key: str,
        data: Dict[str, Any],
    ) -> Optional[Signal]:

        # -------------------------------------------------
        # SYMBOL
        # -------------------------------------------------

        symbol = str(
            _get(
                data,
                "symbol",
                "trading_symbol",
                "tradingsymbol",
                default="",
            )
        ).upper().strip()

        if not symbol:
            return None

        if not instrument_key:
            return None

        # -------------------------------------------------
        # PRICE
        # -------------------------------------------------

        last_price = _float(
            _get(
                data,
                "last_price",
                "ltp",
                "close",
                "close_price",
                default=0.0,
            )
        )

        if last_price < self.minimum_price:
            return None

        open_price = _float(
            _get(
                data,
                "open_price",
                "open",
                default=0.0,
            )
        )

        high_price = _float(
            _get(
                data,
                "high_price",
                "high",
                default=0.0,
            )
        )

        low_price = _float(
            _get(
                data,
                "low_price",
                "low",
                default=0.0,
            )
        )

        previous_close = _float(
            _get(
                data,
                "previous_close",
                "prev_close",
                default=0.0,
            )
        )

        # -------------------------------------------------
        # GAP FILTER
        # -------------------------------------------------

        gap_percent = self._gap_percent(
            open_price,
            previous_close,
        )

        if (
            abs(gap_percent)
            > self.maximum_gap_percent
        ):
            return None

        # -------------------------------------------------
        # MARKET CAP
        # -------------------------------------------------

        market_cap = _float(
            _get(
                data,
                "market_cap",
                "market_cap_cr",
                default=0.0,
            )
        )

        if (
            market_cap > 0
            and market_cap
            < self.minimum_market_cap
        ):
            return None

        # -------------------------------------------------
        # VOLUME
        # -------------------------------------------------

        volume = _int(
            _get(
                data,
                "volume",
                default=0,
            )
        )

        average_volume = _int(
            _get(
                data,
                "average_volume",
                "avg_volume",
                default=0,
            )
        )

        volume_ratio = _float(
            _get(
                data,
                "volume_ratio",
                "relative_volume",
                "rvol",
                default=0.0,
            )
        )

        if (
            volume_ratio <= 0
            and average_volume > 0
        ):

            volume_ratio = (
                volume
                / average_volume
            )

        # -------------------------------------------------
        # INDICATORS
        # -------------------------------------------------

        ema9 = _float(
            _get(
                data,
                "ema9",
                "ema_9",
                default=0.0,
            )
        )

        ema20 = _float(
            _get(
                data,
                "ema20",
                "ema_20",
                default=0.0,
            )
        )

        ema21 = _float(
            _get(
                data,
                "ema21",
                "ema_21",
                default=0.0,
            )
        )

        ema50 = _float(
            _get(
                data,
                "ema50",
                "ema_50",
                default=0.0,
            )
        )

        ema100 = _float(
            _get(
                data,
                "ema100",
                "ema_100",
                default=0.0,
            )
        )

        ema200 = _float(
            _get(
                data,
                "ema200",
                "ema_200",
                default=0.0,
            )
        )

        rsi = _float(
            _get(
                data,
                "rsi",
                default=0.0,
            )
        )

        macd = _float(
            _get(
                data,
                "macd",
                default=0.0,
            )
        )

        macd_signal = _float(
            _get(
                data,
                "macd_signal",
                default=0.0,
            )
        )

        macd_histogram = _float(
            _get(
                data,
                "macd_histogram",
                "macd_hist",
                default=0.0,
            )
        )

        adx = _float(
            _get(
                data,
                "adx",
                default=0.0,
            )
        )

        plus_di = _float(
            _get(
                data,
                "plus_di",
                "di_plus",
                default=0.0,
            )
        )

        minus_di = _float(
            _get(
                data,
                "minus_di",
                "di_minus",
                default=0.0,
            )
        )

        atr = _float(
            _get(
                data,
                "atr",
                default=0.0,
            )
        )

        # -------------------------------------------------
        # LONG-TERM LEVELS
        # -------------------------------------------------

        high_3_week = _float(
            _get(
                data,
                "high_3_week",
                "three_week_high",
                "3_week_high",
                default=0.0,
            )
        )

        high_1_month = _float(
            _get(
                data,
                "high_1_month",
                "one_month_high",
                "monthly_high",
                default=0.0,
            )
        )

        high_2_month = _float(
            _get(
                data,
                "high_2_month",
                "two_month_high",
                default=0.0,
            )
        )

        high_3_month = _float(
            _get(
                data,
                "high_3_month",
                "three_month_high",
                default=0.0,
            )
        )

        high_6_month = _float(
            _get(
                data,
                "high_6_month",
                "six_month_high",
                default=0.0,
            )
        )

        high_52_week = _float(
            _get(
                data,
                "high_52_week",
                "52_week_high",
                "year_high",
                default=0.0,
            )
        )

        low_3_week = _float(
            _get(
                data,
                "low_3_week",
                "three_week_low",
                default=0.0,
            )
        )

        low_1_month = _float(
            _get(
                data,
                "low_1_month",
                "monthly_low",
                default=0.0,
            )
        )

        swing_low = _float(
            _get(
                data,
                "swing_low",
                "previous_swing_low",
                default=0.0,
            )
        )

        swing_high = _float(
            _get(
                data,
                "swing_high",
                "previous_swing_high",
                default=0.0,
            )
        )

        # -------------------------------------------------
        # DIRECTION
        # -------------------------------------------------

        direction = self._determine_direction(
            price=last_price,
            ema20=ema20,
            ema21=ema21,
            ema50=ema50,
            ema100=ema100,
            ema200=ema200,
            rsi=rsi,
            macd=macd,
            macd_signal=macd_signal,
            plus_di=plus_di,
            minus_di=minus_di,
        )

        if direction is None:
            return None

        # -------------------------------------------------
        # ADX FILTER
        # -------------------------------------------------

        if (
            adx > 0
            and adx < self.minimum_adx
        ):
            return None

        # -------------------------------------------------
        # BREAKOUT / BREAKDOWN
        # -------------------------------------------------

        if direction == SignalType.BUY:

            (
                breakout_level,
                breakout_name,
            ) = self._bullish_breakout_level(
                price=last_price,
                high_3_week=high_3_week,
                high_1_month=high_1_month,
                high_2_month=high_2_month,
                high_3_month=high_3_month,
                high_6_month=high_6_month,
                high_52_week=high_52_week,
            )

            breakout = (
                breakout_level > 0
                and last_price
                >= breakout_level
            )

            near_breakout = (
                breakout_level > 0
                and self._distance_percent(
                    last_price,
                    breakout_level,
                )
                <= self.breakout_tolerance_percent
            )

        else:

            (
                breakout_level,
                breakout_name,
            ) = self._bearish_breakdown_level(
                price=last_price,
                low_3_week=low_3_week,
                low_1_month=low_1_month,
                swing_low=swing_low,
            )

            breakout = (
                breakout_level > 0
                and last_price
                <= breakout_level
            )

            near_breakout = (
                breakout_level > 0
                and self._distance_percent(
                    last_price,
                    breakout_level,
                )
                <= self.breakout_tolerance_percent
            )

        # -------------------------------------------------
        # VOLUME CONFIRMATION
        # -------------------------------------------------

        if breakout:

            if (
                volume_ratio > 0
                and volume_ratio
                < self.breakout_volume_ratio
            ):
                return None

        elif (
            volume_ratio > 0
            and volume_ratio
            < self.minimum_volume_ratio
            and not near_breakout
        ):

            return None

        # -------------------------------------------------
        # MARKET CONTEXT
        # -------------------------------------------------

        market_trend = self._market_trend(
            data
        )

        sector = str(
            _get(
                data,
                "sector",
                default="",
            )
        )

        sector_strength = _float(
            _get(
                data,
                "sector_strength",
                default=0.0,
            )
        )

        relative_strength = _float(
            _get(
                data,
                "relative_strength",
                "rs",
                default=0.0,
            )
        )

        # -------------------------------------------------
        # SCORE
        # -------------------------------------------------

        (
            score,
            confidence,
            score_breakdown,
        ) = self._calculate_score(
            direction=direction,
            price=last_price,
            breakout=breakout,
            near_breakout=near_breakout,
            breakout_name=breakout_name,
            volume_ratio=volume_ratio,
            ema20=ema20,
            ema21=ema21,
            ema50=ema50,
            ema100=ema100,
            ema200=ema200,
            rsi=rsi,
            macd=macd,
            macd_signal=macd_signal,
            macd_histogram=macd_histogram,
            adx=adx,
            plus_di=plus_di,
            minus_di=minus_di,
            sector_strength=sector_strength,
            relative_strength=relative_strength,
            market_trend=market_trend,
        )

        if score < self.minimum_score:
            return None

        if (
            confidence
            < self.minimum_confidence
        ):
            return None

        # -------------------------------------------------
        # SIGNAL TYPE
        # -------------------------------------------------

        if breakout:

            signal_type = direction

        else:

            signal_type = SignalType.WATCH

        # -------------------------------------------------
        # ENTRY
        # -------------------------------------------------

        if breakout:

            entry = last_price

        elif breakout_level > 0:

            entry = breakout_level

        else:

            entry = last_price

        # -------------------------------------------------
        # STOP LOSS
        # -------------------------------------------------

        stop_loss = self._calculate_stop_loss(
            direction=direction,
            entry=entry,
            atr=atr,
            ema20=ema20,
            ema21=ema21,
            ema50=ema50,
            swing_low=swing_low,
            swing_high=swing_high,
            low_3_week=low_3_week,
            high_3_week=high_3_week,
        )

        if stop_loss <= 0:
            return None

        # -------------------------------------------------
        # TARGETS
        # -------------------------------------------------

        (
            target1,
            target2,
            target3,
        ) = self._targets(
            direction=direction,
            entry=entry,
            stop_loss=stop_loss,
        )

        if target1 <= 0:
            return None

        # -------------------------------------------------
        # PATTERN
        # -------------------------------------------------

        if direction == SignalType.BUY:

            pattern = PatternType.BREAKOUT

        else:

            pattern = PatternType.BREAKDOWN

        # -------------------------------------------------
        # REMARKS
        # -------------------------------------------------

        if breakout:

            remarks = (
                f"Positional {breakout_name} "
                f"{direction.value} confirmed"
            )

        elif near_breakout:

            remarks = (
                f"Positional {breakout_name} "
                "near trigger"
            )

        else:

            remarks = (
                "Strong positional trend setup"
            )

        # -------------------------------------------------
        # SIGNAL
        # -------------------------------------------------

        signal = Signal(
            instrument_key=instrument_key,
            symbol=symbol,
            signal_type=signal_type,
            pattern=pattern,
            strength=self._strength(
                score
            ),
            scanner_name=self.name,
            scanner_version=self.version,
            strategy_name=(
                "StockVersity Positional"
            ),
            timeframe=self.timeframe,
            market_trend=market_trend,
            sector=sector,
            sector_strength=sector_strength,
            relative_strength=relative_strength,
            last_price=last_price,
            open_price=open_price,
            high_price=high_price,
            low_price=low_price,
            close_price=last_price,
            previous_close=previous_close,
            gap_percent=gap_percent,
            volume=volume,
            average_volume=average_volume,
            volume_ratio=round(
                volume_ratio,
                2,
            ),
            trigger_price=round(
                breakout_level,
                2,
            ),
            entry=round(
                entry,
                2,
            ),
            stop_loss=round(
                stop_loss,
                2,
            ),
            target1=round(
                target1,
                2,
            ),
            target2=round(
                target2,
                2,
            ),
            target3=round(
                target3,
                2,
            ),
            atr=atr,
            ema9=ema9,
            ema20=ema20,
            ema21=ema21,
            ema50=ema50,
            ema100=ema100,
            ema200=ema200,
            rsi=rsi,
            macd=macd,
            macd_signal=macd_signal,
            macd_histogram=macd_histogram,
            adx=adx,
            plus_di=plus_di,
            minus_di=minus_di,
            confidence=confidence,
            score=score,
            score_breakdown=score_breakdown,
            remarks=remarks,
            tags=[
                "POSITIONAL",
                direction.value,
                breakout_name,
                (
                    "CONFIRMED"
                    if breakout
                    else "WATCH"
                ),
            ],
            metadata={
                "market_cap":
                    market_cap,

                "direction":
                    direction.value,

                "breakout_level":
                    breakout_level,

                "breakout_name":
                    breakout_name,

                "breakout":
                    breakout,

                "near_breakout":
                    near_breakout,

                "high_3_week":
                    high_3_week,

                "high_1_month":
                    high_1_month,

                "high_2_month":
                    high_2_month,

                "high_3_month":
                    high_3_month,

                "high_6_month":
                    high_6_month,

                "high_52_week":
                    high_52_week,

                "low_3_week":
                    low_3_week,

                "low_1_month":
                    low_1_month,

                "swing_low":
                    swing_low,

                "swing_high":
                    swing_high,
            },
        )

        if (
            signal.risk_reward
            < self.minimum_rr
        ):
            return None

        return signal

    # =====================================================
    # DIRECTION
    # =====================================================

    @staticmethod
    def _determine_direction(
        *,
        price: float,
        ema20: float,
        ema21: float,
        ema50: float,
        ema100: float,
        ema200: float,
        rsi: float,
        macd: float,
        macd_signal: float,
        plus_di: float,
        minus_di: float,
    ) -> Optional[SignalType]:

        short_ema = (
            ema20
            if ema20 > 0
            else ema21
        )

        bullish = 0

        bearish = 0

        if short_ema > 0:

            if price > short_ema:
                bullish += 1

            elif price < short_ema:
                bearish += 1

        if ema50 > 0:

            if price > ema50:
                bullish += 1

            elif price < ema50:
                bearish += 1

        if ema200 > 0:

            if price > ema200:
                bullish += 2

            elif price < ema200:
                bearish += 2

        if (
            ema50 > 0
            and ema200 > 0
        ):

            if ema50 > ema200:
                bullish += 2

            elif ema50 < ema200:
                bearish += 2

        if (
            ema100 > 0
            and ema200 > 0
        ):

            if ema100 > ema200:
                bullish += 1

            elif ema100 < ema200:
                bearish += 1

        if rsi > 0:

            if rsi >= 55:
                bullish += 2

            elif rsi <= 45:
                bearish += 2

        if (
            macd != 0
            or macd_signal != 0
        ):

            if macd > macd_signal:
                bullish += 1

            elif macd < macd_signal:
                bearish += 1

        if (
            plus_di > 0
            or minus_di > 0
        ):

            if plus_di > minus_di:
                bullish += 1

            elif minus_di > plus_di:
                bearish += 1

        if bullish >= 5 and bullish > bearish:
            return SignalType.BUY

        if bearish >= 5 and bearish > bullish:
            return SignalType.SELL

        return None

    # =====================================================
    # BULLISH BREAKOUT LEVEL
    # =====================================================

    @staticmethod
    def _bullish_breakout_level(
        *,
        price: float,
        high_3_week: float,
        high_1_month: float,
        high_2_month: float,
        high_3_month: float,
        high_6_month: float,
        high_52_week: float,
    ) -> Tuple[float, str]:

        levels = [
            (
                high_52_week,
                "52_WEEK_BREAKOUT",
            ),
            (
                high_6_month,
                "6_MONTH_BREAKOUT",
            ),
            (
                high_3_month,
                "3_MONTH_BREAKOUT",
            ),
            (
                high_2_month,
                "2_MONTH_BREAKOUT",
            ),
            (
                high_1_month,
                "MONTHLY_BREAKOUT",
            ),
            (
                high_3_week,
                "3_WEEK_BREAKOUT",
            ),
        ]

        # First check already-broken major levels.

        for level, name in levels:

            if (
                level > 0
                and price >= level
            ):

                return (
                    level,
                    name,
                )

        # Otherwise find nearest resistance.

        candidates = [
            (
                level,
                name,
            )
            for level, name in levels
            if level > price
        ]

        if not candidates:
            return (
                0.0,
                "TREND_CONTINUATION",
            )

        return min(
            candidates,
            key=lambda item: (
                item[0] - price
            ),
        )

    # =====================================================
    # BEARISH BREAKDOWN LEVEL
    # =====================================================

    @staticmethod
    def _bearish_breakdown_level(
        *,
        price: float,
        low_3_week: float,
        low_1_month: float,
        swing_low: float,
    ) -> Tuple[float, str]:

        levels = [
            (
                low_1_month,
                "MONTHLY_BREAKDOWN",
            ),
            (
                low_3_week,
                "3_WEEK_BREAKDOWN",
            ),
            (
                swing_low,
                "SWING_BREAKDOWN",
            ),
        ]

        for level, name in levels:

            if (
                level > 0
                and price <= level
            ):

                return (
                    level,
                    name,
                )

        candidates = [
            (
                level,
                name,
            )
            for level, name in levels
            if (
                level > 0
                and level < price
            )
        ]

        if not candidates:

            return (
                0.0,
                "TREND_CONTINUATION",
            )

        return max(
            candidates,
            key=lambda item: item[0],
        )

    # =====================================================
    # STOP LOSS
    # =====================================================

    @staticmethod
    def _calculate_stop_loss(
        *,
        direction: SignalType,
        entry: float,
        atr: float,
        ema20: float,
        ema21: float,
        ema50: float,
        swing_low: float,
        swing_high: float,
        low_3_week: float,
        high_3_week: float,
    ) -> float:

        if direction == SignalType.BUY:

            candidates: List[float] = []

            if (
                swing_low > 0
                and swing_low < entry
            ):
                candidates.append(
                    swing_low
                )

            if (
                low_3_week > 0
                and low_3_week < entry
            ):
                candidates.append(
                    low_3_week
                )

            short_ema = (
                ema20
                if ema20 > 0
                else ema21
            )

            if (
                short_ema > 0
                and short_ema < entry
            ):
                candidates.append(
                    short_ema
                )

            if (
                ema50 > 0
                and ema50 < entry
            ):
                candidates.append(
                    ema50
                )

            if atr > 0:

                atr_stop = (
                    entry
                    - atr * 2.0
                )

                if atr_stop > 0:
                    candidates.append(
                        atr_stop
                    )

            if not candidates:
                return 0.0

            # Closest valid structural stop.

            return max(
                candidates
            )

        # SELL

        candidates = []

        if (
            swing_high > entry
        ):
            candidates.append(
                swing_high
            )

        if (
            high_3_week > entry
        ):
            candidates.append(
                high_3_week
            )

        short_ema = (
            ema20
            if ema20 > 0
            else ema21
        )

        if (
            short_ema > entry
        ):
            candidates.append(
                short_ema
            )

        if (
            ema50 > entry
        ):
            candidates.append(
                ema50
            )

        if atr > 0:

            atr_stop = (
                entry
                + atr * 2.0
            )

            candidates.append(
                atr_stop
            )

        if not candidates:
            return 0.0

        return min(
            candidates
        )

    # =====================================================
    # TARGETS
    # =====================================================

    def _targets(
        self,
        *,
        direction: SignalType,
        entry: float,
        stop_loss: float,
    ) -> Tuple[
        float,
        float,
        float,
    ]:

        if direction == SignalType.BUY:

            risk = (
                entry
                - stop_loss
            )

            if risk <= 0:

                return (
                    0.0,
                    0.0,
                    0.0,
                )

            return (
                entry
                + risk * self.minimum_rr,

                entry
                + risk * 3.0,

                entry
                + risk * 4.0,
            )

        risk = (
            stop_loss
            - entry
        )

        if risk <= 0:

            return (
                0.0,
                0.0,
                0.0,
            )

        return (
            max(
                entry
                - risk * self.minimum_rr,
                0.01,
            ),

            max(
                entry
                - risk * 3.0,
                0.01,
            ),

            max(
                entry
                - risk * 4.0,
                0.01,
            ),
        )

    # =====================================================
    # SCORE
    # =====================================================

    @staticmethod
    def _calculate_score(
        *,
        direction: SignalType,
        price: float,
        breakout: bool,
        near_breakout: bool,
        breakout_name: str,
        volume_ratio: float,
        ema20: float,
        ema21: float,
        ema50: float,
        ema100: float,
        ema200: float,
        rsi: float,
        macd: float,
        macd_signal: float,
        macd_histogram: float,
        adx: float,
        plus_di: float,
        minus_di: float,
        sector_strength: float,
        relative_strength: float,
        market_trend: MarketTrend,
    ) -> Tuple[
        float,
        float,
        Dict[str, float],
    ]:

        trend = 0.0

        volume_score = 0.0

        momentum = 0.0

        pattern = 0.0

        sector = 0.0

        rs = 0.0

        market = 0.0

        short_ema = (
            ema20
            if ema20 > 0
            else ema21
        )

        # -------------------------------------------------
        # TREND : 25
        # -------------------------------------------------

        if direction == SignalType.BUY:

            if (
                short_ema > 0
                and price > short_ema
            ):
                trend += 5

            if (
                ema50 > 0
                and price > ema50
            ):
                trend += 5

            if (
                ema100 > 0
                and price > ema100
            ):
                trend += 4

            if (
                ema200 > 0
                and price > ema200
            ):
                trend += 5

            if (
                ema50 > 0
                and ema200 > 0
                and ema50 > ema200
            ):
                trend += 6

        else:

            if (
                short_ema > 0
                and price < short_ema
            ):
                trend += 5

            if (
                ema50 > 0
                and price < ema50
            ):
                trend += 5

            if (
                ema100 > 0
                and price < ema100
            ):
                trend += 4

            if (
                ema200 > 0
                and price < ema200
            ):
                trend += 5

            if (
                ema50 > 0
                and ema200 > 0
                and ema50 < ema200
            ):
                trend += 6

        trend = min(
            trend,
            25.0,
        )

        # -------------------------------------------------
        # VOLUME : 15
        # -------------------------------------------------

        if volume_ratio >= 3.0:
            volume_score = 15

        elif volume_ratio >= 2.0:
            volume_score = 13

        elif volume_ratio >= 1.5:
            volume_score = 11

        elif volume_ratio >= 1.2:
            volume_score = 8

        elif volume_ratio > 0:
            volume_score = 4

        else:
            volume_score = 3

        # -------------------------------------------------
        # MOMENTUM : 20
        # -------------------------------------------------

        if direction == SignalType.BUY:

            if 55 <= rsi <= 70:
                momentum += 6

            elif rsi > 50:
                momentum += 3

            if macd > macd_signal:
                momentum += 4

            if macd_histogram > 0:
                momentum += 3

            if plus_di > minus_di:
                momentum += 3

        else:

            if 30 <= rsi <= 45:
                momentum += 6

            elif (
                rsi > 0
                and rsi < 50
            ):
                momentum += 3

            if macd < macd_signal:
                momentum += 4

            if macd_histogram < 0:
                momentum += 3

            if (
                minus_di > plus_di
            ):
                momentum += 3

        if adx >= 30:
            momentum += 4

        elif adx >= 25:
            momentum += 3

        elif adx >= 20:
            momentum += 2

        momentum = min(
            momentum,
            20.0,
        )

        # -------------------------------------------------
        # BREAKOUT / PATTERN : 20
        # -------------------------------------------------

        if breakout:
            pattern += 12

        elif near_breakout:
            pattern += 8

        else:
            pattern += 4

        breakout_bonus = {

            "52_WEEK_BREAKOUT":
                8,

            "6_MONTH_BREAKOUT":
                7,

            "3_MONTH_BREAKOUT":
                6,

            "2_MONTH_BREAKOUT":
                5,

            "MONTHLY_BREAKOUT":
                5,

            "3_WEEK_BREAKOUT":
                4,

            "MONTHLY_BREAKDOWN":
                5,

            "3_WEEK_BREAKDOWN":
                4,

            "SWING_BREAKDOWN":
                3,

            "TREND_CONTINUATION":
                2,
        }

        pattern += breakout_bonus.get(
            breakout_name,
            0,
        )

        pattern = min(
            pattern,
            20.0,
        )

        # -------------------------------------------------
        # SECTOR : 7
        # -------------------------------------------------

        if sector_strength >= 75:
            sector = 7

        elif sector_strength >= 60:
            sector = 6

        elif sector_strength >= 50:
            sector = 4

        elif sector_strength > 0:
            sector = 2

        else:
            sector = 2

        # -------------------------------------------------
        # RELATIVE STRENGTH : 7
        # -------------------------------------------------

        if direction == SignalType.BUY:

            if relative_strength >= 80:
                rs = 7

            elif relative_strength >= 70:
                rs = 6

            elif relative_strength >= 55:
                rs = 4

            elif relative_strength > 0:
                rs = 2

            else:
                rs = 2

        else:

            if (
                0
                < relative_strength
                <= 20
            ):
                rs = 7

            elif relative_strength <= 30:
                rs = 6

            elif relative_strength <= 45:
                rs = 4

            elif relative_strength > 0:
                rs = 2

            else:
                rs = 2

        # -------------------------------------------------
        # MARKET : 6
        # -------------------------------------------------

        if direction == SignalType.BUY:

            if (
                market_trend
                == MarketTrend.STRONG_BULLISH
            ):
                market = 6

            elif (
                market_trend
                == MarketTrend.BULLISH
            ):
                market = 5

            elif (
                market_trend
                == MarketTrend.SIDEWAYS
            ):
                market = 3

            else:
                market = 1

        else:

            if (
                market_trend
                == MarketTrend.STRONG_BEARISH
            ):
                market = 6

            elif (
                market_trend
                == MarketTrend.BEARISH
            ):
                market = 5

            elif (
                market_trend
                == MarketTrend.SIDEWAYS
            ):
                market = 3

            else:
                market = 1

        # -------------------------------------------------
        # TOTAL
        # -------------------------------------------------

        score = (
            trend
            + volume_score
            + momentum
            + pattern
            + sector
            + rs
            + market
        )

        score = round(
            min(
                score,
                100.0,
            ),
            2,
        )

        # -------------------------------------------------
        # CONFIDENCE
        # -------------------------------------------------

        confidence = (
            score * 0.75
        )

        if breakout:
            confidence += 8

        if volume_ratio >= 1.5:
            confidence += 5

        if adx >= 25:
            confidence += 4

        if direction == SignalType.BUY:

            if (
                ema50 > 0
                and ema200 > 0
                and ema50 > ema200
            ):
                confidence += 5

            if (
                macd > macd_signal
                and macd_histogram > 0
            ):
                confidence += 3

        else:

            if (
                ema50 > 0
                and ema200 > 0
                and ema50 < ema200
            ):
                confidence += 5

            if (
                macd < macd_signal
                and macd_histogram < 0
            ):
                confidence += 3

        confidence = round(
            min(
                confidence,
                100.0,
            ),
            2,
        )

        score_breakdown = {

            "trend":
                round(
                    trend,
                    2,
                ),

            "volume":
                round(
                    volume_score,
                    2,
                ),

            "momentum":
                round(
                    momentum,
                    2,
                ),

            "pattern":
                round(
                    pattern,
                    2,
                ),

            "sector":
                round(
                    sector,
                    2,
                ),

            "relative_strength":
                round(
                    rs,
                    2,
                ),

            "market":
                round(
                    market,
                    2,
                ),
        }

        return (
            score,
            confidence,
            score_breakdown,
        )

    # =====================================================
    # GAP
    # =====================================================

    @staticmethod
    def _gap_percent(
        open_price: float,
        previous_close: float,
    ) -> float:

        if (
            open_price <= 0
            or previous_close <= 0
        ):
            return 0.0

        return round(
            (
                (
                    open_price
                    - previous_close
                )
                / previous_close
            )
            * 100,
            2,
        )

    # =====================================================
    # DISTANCE
    # =====================================================

    @staticmethod
    def _distance_percent(
        price: float,
        level: float,
    ) -> float:

        if level <= 0:
            return 100.0

        return abs(
            (
                price
                - level
            )
            / level
            * 100
        )

    # =====================================================
    # MARKET TREND
    # =====================================================

    @staticmethod
    def _market_trend(
        data: Dict[str, Any],
    ) -> MarketTrend:

        value = _get(
            data,
            "market_trend",
            "trend",
            default="SIDEWAYS",
        )

        if isinstance(
            value,
            MarketTrend,
        ):
            return value

        value = str(
            value
        ).upper().strip()

        mapping = {

            "STRONG_BULLISH":
                MarketTrend.STRONG_BULLISH,

            "BULLISH":
                MarketTrend.BULLISH,

            "UP":
                MarketTrend.BULLISH,

            "SIDEWAYS":
                MarketTrend.SIDEWAYS,

            "NEUTRAL":
                MarketTrend.SIDEWAYS,

            "BEARISH":
                MarketTrend.BEARISH,

            "DOWN":
                MarketTrend.BEARISH,

            "STRONG_BEARISH":
                MarketTrend.STRONG_BEARISH,
        }

        return mapping.get(
            value,
            MarketTrend.SIDEWAYS,
        )

    # =====================================================
    # STRENGTH
    # =====================================================

    @staticmethod
    def _strength(
        score: float,
    ) -> SignalStrength:

        if score >= 90:
            return SignalStrength.VERY_STRONG

        if score >= 80:
            return SignalStrength.STRONG

        if score >= 70:
            return SignalStrength.MODERATE

        if score >= 60:
            return SignalStrength.WEAK

        return SignalStrength.VERY_WEAK

    # =====================================================
    # INFO
    # =====================================================

    def info(
        self,
    ) -> Dict[str, Any]:

        return {

            "scanner":
                self.name,

            "version":
                self.version,

            "timeframe":
                self.timeframe,

            "minimum_price":
                self.minimum_price,

            "minimum_market_cap":
                self.minimum_market_cap,

            "maximum_gap_percent":
                self.maximum_gap_percent,

            "minimum_score":
                self.minimum_score,

            "minimum_confidence":
                self.minimum_confidence,

            "minimum_rr":
                self.minimum_rr,

            "minimum_adx":
                self.minimum_adx,

            "minimum_volume_ratio":
                self.minimum_volume_ratio,

            "breakout_volume_ratio":
                self.breakout_volume_ratio,

            "breakout_tolerance_percent":
                self.breakout_tolerance_percent,
        }


# =========================================================
# FACTORY
# =========================================================

def create_positional_scanner(
    **kwargs: Any,
) -> PositionalScanner:

    return PositionalScanner(
        **kwargs
    )


# =========================================================
# EXPORTS
# =========================================================

__all__ = [
    "PositionalScanner",
    "create_positional_scanner",
]


# =========================================================
# END OF FILE
# =========================================================