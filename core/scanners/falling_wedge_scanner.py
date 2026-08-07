"""
=========================================================
StockVersity Scanner Pro
Falling Wedge Scanner
Version : 2.1
=========================================================

File:
    core/scanners/falling_wedge_scanner.py

Purpose:
    Detect bullish Falling Wedge reversal / continuation
    opportunities.

Detection
---------
• Contracting price structure
• Lower highs
• Lower lows
• Upper trendline falling faster than lower trendline
• Range contraction
• Price near / above wedge resistance
• Volume contraction inside wedge
• Breakout volume expansion
• RSI / MACD / ADX confirmation
• EMA trend confirmation
• Relative strength / sector confirmation
• ATR + structure based stop
• Minimum risk/reward validation

Signals
-------
WATCH
    Valid wedge approaching breakout resistance.

BUY
    Confirmed wedge breakout.

=========================================================
"""

from __future__ import annotations

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple

from core.scanner.base_scanner import BaseScanner

from core.scanner.signal import (
    MarketTrend,
    PatternType,
    Signal,
    SignalStrength,
    SignalType,
)


# =========================================================
# FALLING WEDGE SCANNER
# =========================================================

class FallingWedgeScanner(BaseScanner):

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        *,
        timeframe: str = "1h",
        minimum_price: float = 200.0,
        minimum_market_cap: float = 1000.0,
        minimum_score: float = 65.0,
        minimum_confidence: float = 60.0,
        minimum_rr: float = 2.0,
        minimum_adx: float = 15.0,
        breakout_volume_ratio: float = 1.50,
        dry_volume_ratio: float = 0.90,
        breakout_buffer_percent: float = 0.10,
        pre_breakout_distance_percent: float = 2.0,
        atr_stop_multiple: float = 1.5,
        minimum_contraction_percent: float = 20.0,
        lookback: int = 30,
        max_signals: int = 30,
        debug: bool = False,
    ) -> None:

        super().__init__(
            name="FallingWedgeScanner",
            version="2.1",
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

        self.breakout_volume_ratio = max(
            0.0,
            float(breakout_volume_ratio),
        )

        self.dry_volume_ratio = max(
            0.0,
            float(dry_volume_ratio),
        )

        self.breakout_buffer_percent = max(
            0.0,
            float(breakout_buffer_percent),
        )

        self.pre_breakout_distance_percent = max(
            0.1,
            float(pre_breakout_distance_percent),
        )

        self.atr_stop_multiple = max(
            0.1,
            float(atr_stop_multiple),
        )

        self.minimum_contraction_percent = max(
            0.0,
            float(minimum_contraction_percent),
        )

        self.lookback = max(
            10,
            int(lookback),
        )

        self.max_signals = max(
            1,
            int(max_signals),
        )

        self.debug = bool(debug)

    # =====================================================
    # SAFE FLOAT
    # =====================================================

    @staticmethod
    def _float(
        value: Any,
        default: float = 0.0,
    ) -> float:

        try:

            if value is None:
                return default

            return float(value)

        except (
            TypeError,
            ValueError,
        ):

            return default

    # =====================================================
    # SAFE INT
    # =====================================================

    @staticmethod
    def _int(
        value: Any,
        default: int = 0,
    ) -> int:

        try:

            if value is None:
                return default

            return int(
                float(value)
            )

        except (
            TypeError,
            ValueError,
        ):

            return default

    # =====================================================
    # SAFE LOOKUP
    # =====================================================

    @staticmethod
    def _value(
        data: Dict[str, Any],
        *keys: str,
        default: Any = None,
    ) -> Any:

        for key in keys:

            value = data.get(
                key
            )

            if value is not None:

                return value

        return default

    # =====================================================
    # CLAMP
    # =====================================================

    @staticmethod
    def _clamp(
        value: float,
        minimum: float = 0.0,
        maximum: float = 100.0,
    ) -> float:

        return max(
            minimum,
            min(
                maximum,
                value,
            ),
        )

    # =====================================================
    # BARS
    # =====================================================

    def _get_bars(
        self,
        raw: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        possible = (

            raw.get("candles")
            or raw.get("history")
            or raw.get("bars")
            or []

        )

        if not isinstance(
            possible,
            Sequence,
        ):

            return []

        bars: List[
            Dict[str, Any]
        ] = []

        for item in possible:

            if isinstance(
                item,
                dict,
            ):

                bars.append(
                    item
                )

        if len(bars) > self.lookback:

            bars = bars[
                -self.lookback:
            ]

        return bars

    # =====================================================
    # NORMALIZE
    # =====================================================

    def _normalize_record(
        self,
        key: str,
        raw: Dict[str, Any],
    ) -> Dict[str, Any]:

        instrument_key = str(
            self._value(
                raw,
                "instrument_key",
                "instrumentKey",
                default=key,
            )
            or key
        ).strip()

        symbol = str(
            self._value(
                raw,
                "symbol",
                "trading_symbol",
                "tradingSymbol",
                default="",
            )
            or ""
        ).strip().upper()

        last_price = self._float(
            self._value(
                raw,
                "last_price",
                "ltp",
                "lastPrice",
                "close",
                default=0.0,
            )
        )

        volume = self._int(
            raw.get(
                "volume",
                0,
            )
        )

        average_volume = self._int(
            self._value(
                raw,
                "average_volume",
                "avg_volume",
                default=0,
            )
        )

        volume_ratio = self._float(
            self._value(
                raw,
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

        return {

            "instrument_key":
                instrument_key,

            "symbol":
                symbol,

            "last_price":
                last_price,

            "open_price":
                self._float(
                    self._value(
                        raw,
                        "open_price",
                        "open",
                        default=last_price,
                    )
                ),

            "high_price":
                self._float(
                    self._value(
                        raw,
                        "high_price",
                        "high",
                        default=last_price,
                    )
                ),

            "low_price":
                self._float(
                    self._value(
                        raw,
                        "low_price",
                        "low",
                        default=last_price,
                    )
                ),

            "close_price":
                self._float(
                    self._value(
                        raw,
                        "close_price",
                        "close",
                        default=last_price,
                    )
                ),

            "previous_close":
                self._float(
                    self._value(
                        raw,
                        "previous_close",
                        "prev_close",
                        default=0.0,
                    )
                ),

            "volume":
                volume,

            "average_volume":
                average_volume,

            "volume_ratio":
                volume_ratio,

            "market_cap":
                self._float(
                    self._value(
                        raw,
                        "market_cap",
                        "marketCap",
                        default=0.0,
                    )
                ),

            "ema9":
                self._float(
                    raw.get(
                        "ema9",
                        0.0,
                    )
                ),

            "ema20":
                self._float(
                    raw.get(
                        "ema20",
                        0.0,
                    )
                ),

            "ema21":
                self._float(
                    raw.get(
                        "ema21",
                        raw.get(
                            "ema20",
                            0.0,
                        ),
                    )
                ),

            "ema50":
                self._float(
                    raw.get(
                        "ema50",
                        0.0,
                    )
                ),

            "ema100":
                self._float(
                    raw.get(
                        "ema100",
                        0.0,
                    )
                ),

            "ema200":
                self._float(
                    raw.get(
                        "ema200",
                        0.0,
                    )
                ),

            "rsi":
                self._float(
                    raw.get(
                        "rsi",
                        0.0,
                    )
                ),

            "macd":
                self._float(
                    raw.get(
                        "macd",
                        0.0,
                    )
                ),

            "macd_signal":
                self._float(
                    self._value(
                        raw,
                        "macd_signal",
                        "macdSignal",
                        default=0.0,
                    )
                ),

            "macd_histogram":
                self._float(
                    self._value(
                        raw,
                        "macd_histogram",
                        "macd_hist",
                        default=0.0,
                    )
                ),

            "adx":
                self._float(
                    raw.get(
                        "adx",
                        0.0,
                    )
                ),

            "plus_di":
                self._float(
                    self._value(
                        raw,
                        "plus_di",
                        "plusDI",
                        default=0.0,
                    )
                ),

            "minus_di":
                self._float(
                    self._value(
                        raw,
                        "minus_di",
                        "minusDI",
                        default=0.0,
                    )
                ),

            "atr":
                self._float(
                    raw.get(
                        "atr",
                        0.0,
                    )
                ),

            "vwap":
                self._float(
                    raw.get(
                        "vwap",
                        0.0,
                    )
                ),

            "wedge_resistance":
                self._float(
                    self._value(
                        raw,
                        "wedge_resistance",
                        "resistance",
                        default=0.0,
                    )
                ),

            "wedge_support":
                self._float(
                    self._value(
                        raw,
                        "wedge_support",
                        "support",
                        default=0.0,
                    )
                ),

            "sector":
                str(
                    raw.get(
                        "sector",
                        "",
                    )
                    or ""
                ).strip(),

            "sector_strength":
                self._float(
                    raw.get(
                        "sector_strength",
                        0.0,
                    )
                ),

            "market_strength":
                self._float(
                    raw.get(
                        "market_strength",
                        0.0,
                    )
                ),

            "relative_strength":
                self._float(
                    raw.get(
                        "relative_strength",
                        0.0,
                    )
                ),

            "beta":
                self._float(
                    raw.get(
                        "beta",
                        0.0,
                    )
                ),

            "bars":
                self._get_bars(
                    raw
                ),

            "raw":
                raw,
        }

    # =====================================================
    # BASIC FILTER
    # =====================================================

    def _passes_basic_filters(
        self,
        data: Dict[str, Any],
    ) -> bool:

        if not data[
            "instrument_key"
        ]:

            return False

        if not data[
            "symbol"
        ]:

            return False

        if (
            data["last_price"]
            < self.minimum_price
        ):

            return False

        market_cap = data[
            "market_cap"
        ]

        if (
            market_cap > 0
            and market_cap
            < self.minimum_market_cap
        ):

            return False

        return True

    # =====================================================
    # LINEAR SLOPE
    # =====================================================

    @staticmethod
    def _slope(
        values: List[float],
    ) -> float:
        """
        Simple least-squares slope without external
        dependencies.
        """

        count = len(
            values
        )

        if count < 2:

            return 0.0

        x_mean = (
            count - 1
        ) / 2.0

        y_mean = (
            sum(values)
            / count
        )

        numerator = 0.0

        denominator = 0.0

        for index, value in enumerate(
            values
        ):

            x_delta = (
                index
                - x_mean
            )

            numerator += (
                x_delta
                * (
                    value
                    - y_mean
                )
            )

            denominator += (
                x_delta
                * x_delta
            )

        if denominator == 0:

            return 0.0

        return (
            numerator
            / denominator
        )

    # =====================================================
    # WEDGE STRUCTURE
    # =====================================================

    def _analyze_wedge(
        self,
        data: Dict[str, Any],
    ) -> Optional[
        Dict[str, float]
    ]:

        bars = data[
            "bars"
        ]

        if len(bars) < 8:

            # Allow externally calculated wedge
            # resistance/support.

            resistance = data[
                "wedge_resistance"
            ]

            support = data[
                "wedge_support"
            ]

            if (
                resistance > 0
                and support > 0
                and resistance > support
            ):

                return {

                    "resistance":
                        resistance,

                    "support":
                        support,

                    "upper_slope":
                        -1.0,

                    "lower_slope":
                        -0.5,

                    "contraction":
                        25.0,

                    "initial_width":
                        resistance
                        - support,

                    "current_width":
                        resistance
                        - support,

                }

            return None

        highs: List[
            float
        ] = []

        lows: List[
            float
        ] = []

        for bar in bars:

            high = self._float(
                bar.get(
                    "high",
                    0.0,
                )
            )

            low = self._float(
                bar.get(
                    "low",
                    0.0,
                )
            )

            if (
                high <= 0
                or low <= 0
            ):

                continue

            highs.append(
                high
            )

            lows.append(
                low
            )

        if len(highs) < 8:

            return None

        upper_slope = (
            self._slope(
                highs
            )
        )

        lower_slope = (
            self._slope(
                lows
            )
        )

        # Falling wedge requires both trendlines
        # declining.

        if upper_slope >= 0:

            return None

        if lower_slope >= 0:

            return None

        # Upper resistance should generally decline
        # faster than support.

        if (
            abs(upper_slope)
            <= abs(lower_slope)
        ):

            return None

        section = max(
            3,
            len(highs) // 4,
        )

        initial_high = max(
            highs[
                :section
            ]
        )

        initial_low = min(
            lows[
                :section
            ]
        )

        current_high = max(
            highs[
                -section:
            ]
        )

        current_low = min(
            lows[
                -section:
            ]
        )

        initial_width = (
            initial_high
            - initial_low
        )

        current_width = (
            current_high
            - current_low
        )

        if initial_width <= 0:

            return None

        contraction = (
            (
                initial_width
                - current_width
            )
            / initial_width
            * 100.0
        )

        if (
            contraction
            < self.minimum_contraction_percent
        ):

            return None

        resistance = data[
            "wedge_resistance"
        ]

        if resistance <= 0:

            resistance = (
                highs[-1]
            )

        support = data[
            "wedge_support"
        ]

        if support <= 0:

            support = (
                lows[-1]
            )

        if (
            resistance <= 0
            or support <= 0
            or resistance <= support
        ):

            return None

        return {

            "resistance":
                resistance,

            "support":
                support,

            "upper_slope":
                upper_slope,

            "lower_slope":
                lower_slope,

            "contraction":
                contraction,

            "initial_width":
                initial_width,

            "current_width":
                current_width,

        }

    # =====================================================
    # VOLUME CONTRACTION
    # =====================================================

    def _volume_contraction(
        self,
        data: Dict[str, Any],
    ) -> bool:

        raw = data[
            "raw"
        ]

        explicit = raw.get(
            "volume_contraction"
        )

        if isinstance(
            explicit,
            bool,
        ):

            return explicit

        wedge_volume_ratio = self._float(
            self._value(
                raw,
                "wedge_volume_ratio",
                "contraction_volume_ratio",
                default=0.0,
            )
        )

        if wedge_volume_ratio > 0:

            return (
                wedge_volume_ratio
                <= self.dry_volume_ratio
            )

        bars = data[
            "bars"
        ]

        if len(bars) < 8:

            return False

        half = (
            len(bars)
            // 2
        )

        first_volumes = [

            self._float(
                bar.get(
                    "volume",
                    0.0,
                )
            )

            for bar in bars[
                :half
            ]

        ]

        second_volumes = [

            self._float(
                bar.get(
                    "volume",
                    0.0,
                )
            )

            for bar in bars[
                half:
            ]

        ]

        first_volumes = [
            value
            for value in first_volumes
            if value > 0
        ]

        second_volumes = [
            value
            for value in second_volumes
            if value > 0
        ]

        if (
            not first_volumes
            or not second_volumes
        ):

            return False

        first_average = (
            sum(first_volumes)
            / len(first_volumes)
        )

        second_average = (
            sum(second_volumes)
            / len(second_volumes)
        )

        return (
            second_average
            < first_average
        )

    # =====================================================
    # BREAKOUT
    # =====================================================

    def _is_breakout(
        self,
        data: Dict[str, Any],
        resistance: float,
    ) -> bool:

        if resistance <= 0:

            return False

        breakout_price = (

            resistance

            * (
                1.0
                + (
                    self.breakout_buffer_percent
                    / 100.0
                )
            )

        )

        if (
            data["last_price"]
            <= breakout_price
        ):

            return False

        if (
            data["volume_ratio"]
            < self.breakout_volume_ratio
        ):

            return False

        return True

    # =====================================================
    # PRE BREAKOUT
    # =====================================================

    def _is_pre_breakout(
        self,
        data: Dict[str, Any],
        resistance: float,
    ) -> bool:

        price = data[
            "last_price"
        ]

        if (
            price <= 0
            or resistance <= 0
        ):

            return False

        if price >= resistance:

            return False

        distance = (
            (
                resistance
                - price
            )
            / resistance
            * 100.0
        )

        return (
            0.0
            <= distance
            <= self.pre_breakout_distance_percent
        )

    # =====================================================
    # MOMENTUM CONFIRMATION
    # =====================================================

    def _momentum_valid(
        self,
        data: Dict[str, Any],
        breakout: bool,
    ) -> bool:

        rsi = data[
            "rsi"
        ]

        if rsi > 0:

            if breakout:

                if rsi < 50:

                    return False

            else:

                if rsi < 40:

                    return False

            if rsi > 82:

                return False

        adx = data[
            "adx"
        ]

        if (
            adx > 0
            and adx < self.minimum_adx
        ):

            return False

        if breakout:

            plus_di = data[
                "plus_di"
            ]

            minus_di = data[
                "minus_di"
            ]

            if (
                plus_di > 0
                and minus_di > 0
                and plus_di <= minus_di
            ):

                return False

        return True

    # =====================================================
    # SCORE
    # =====================================================

    def _calculate_score(
        self,
        data: Dict[str, Any],
        wedge: Dict[str, float],
        *,
        breakout: bool,
        volume_contraction: bool,
    ) -> Tuple[
        float,
        float,
        Dict[str, float],
    ]:

        # ---------------------------------------------
        # TREND / REVERSAL QUALITY : 15
        # ---------------------------------------------

        trend = 0.0

        price = data[
            "last_price"
        ]

        ema21 = data[
            "ema21"
        ]

        ema50 = data[
            "ema50"
        ]

        ema200 = data[
            "ema200"
        ]

        if (
            ema21 <= 0
            or price >= ema21
        ):

            trend += 5.0

        if (
            ema50 <= 0
            or price >= ema50
        ):

            trend += 5.0

        if (
            ema200 <= 0
            or price >= ema200
        ):

            trend += 5.0

        # ---------------------------------------------
        # VOLUME : 15
        # ---------------------------------------------

        if breakout:

            volume = self._clamp(
                (
                    data[
                        "volume_ratio"
                    ]
                    / 2.5
                )
                * 15.0,
                0.0,
                15.0,
            )

        elif volume_contraction:

            volume = 12.0

        else:

            volume = 4.0

        # ---------------------------------------------
        # MOMENTUM : 15
        # ---------------------------------------------

        momentum = 0.0

        rsi = data[
            "rsi"
        ]

        if 55 <= rsi <= 70:

            momentum += 6.0

        elif 50 <= rsi <= 75:

            momentum += 5.0

        elif rsi >= 40:

            momentum += 3.0

        if (
            data["macd"]
            > data["macd_signal"]
        ):

            momentum += 5.0

        if (
            data["plus_di"]
            > data["minus_di"]
        ):

            momentum += 4.0

        momentum = self._clamp(
            momentum,
            0.0,
            15.0,
        )

        # ---------------------------------------------
        # PATTERN : 30
        # ---------------------------------------------

        pattern = 0.0

        contraction = wedge[
            "contraction"
        ]

        if contraction >= 50:

            pattern += 12.0

        elif contraction >= 35:

            pattern += 10.0

        elif contraction >= 20:

            pattern += 8.0

        else:

            pattern += 5.0

        upper = abs(
            wedge[
                "upper_slope"
            ]
        )

        lower = abs(
            wedge[
                "lower_slope"
            ]
        )

        if (
            upper > 0
            and upper > lower
        ):

            pattern += 8.0

        if volume_contraction:

            pattern += 5.0

        if breakout:

            pattern += 5.0

        else:

            pattern += 3.0

        pattern = self._clamp(
            pattern,
            0.0,
            30.0,
        )

        # ---------------------------------------------
        # SECTOR : 10
        # ---------------------------------------------

        sector_strength = data[
            "sector_strength"
        ]

        if sector_strength > 0:

            sector = (
                self._clamp(
                    sector_strength
                )
                * 0.10
            )

        else:

            sector = 5.0

        # ---------------------------------------------
        # RELATIVE STRENGTH : 10
        # ---------------------------------------------

        relative_strength = data[
            "relative_strength"
        ]

        if relative_strength > 0:

            relative = (
                self._clamp(
                    relative_strength
                )
                * 0.10
            )

        else:

            relative = 5.0

        # ---------------------------------------------
        # MARKET / ADX : 5
        # ---------------------------------------------

        adx = data[
            "adx"
        ]

        if adx >= 30:

            market = 5.0

        elif adx >= 25:

            market = 4.0

        elif adx >= 15:

            market = 3.0

        else:

            market = 1.0

        breakdown = {

            "trend":
                round(
                    trend,
                    2,
                ),

            "volume":
                round(
                    volume,
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
                    relative,
                    2,
                ),

            "market":
                round(
                    market,
                    2,
                ),

        }

        score = self._clamp(
            sum(
                breakdown.values()
            )
        )

        pattern_quality = (
            pattern
            / 30.0
            * 100.0
        )

        confidence = (

            score * 0.70

            + pattern_quality * 0.20

            + (
                100.0
                if breakout
                else 75.0
            ) * 0.10

        )

        return (

            round(
                score,
                2,
            ),

            round(
                self._clamp(
                    confidence
                ),
                2,
            ),

            breakdown,

        )

    # =====================================================
    # STRENGTH
    # =====================================================

    @staticmethod
    def _strength(
        score: float,
    ) -> SignalStrength:

        if score >= 90:

            return (
                SignalStrength.VERY_STRONG
            )

        if score >= 80:

            return (
                SignalStrength.STRONG
            )

        if score >= 70:

            return (
                SignalStrength.MODERATE
            )

        if score >= 60:

            return (
                SignalStrength.WEAK
            )

        return (
            SignalStrength.VERY_WEAK
        )

    # =====================================================
    # STOP LOSS
    # =====================================================

    def _stop_loss(
        self,
        data: Dict[str, Any],
        entry: float,
        support: float,
    ) -> float:

        atr = data[
            "atr"
        ]

        if atr <= 0:

            atr = (
                entry
                * 0.02
            )

        atr_stop = (

            entry

            - (
                atr
                * self.atr_stop_multiple
            )

        )

        if (
            support > 0
            and support < entry
        ):

            # Use the tighter of structural support
            # and ATR stop while remaining below entry.

            stop = max(
                support,
                atr_stop,
            )

        else:

            stop = atr_stop

        return round(
            stop,
            2,
        )

    # =====================================================
    # CREATE SIGNAL
    # =====================================================

    def _create_signal(
        self,
        data: Dict[str, Any],
        wedge: Dict[str, float],
        *,
        breakout: bool,
        volume_contraction: bool,
    ) -> Optional[Signal]:

        entry = data[
            "last_price"
        ]

        if entry <= 0:

            return None

        resistance = wedge[
            "resistance"
        ]

        support = wedge[
            "support"
        ]

        stop_loss = self._stop_loss(
            data,
            entry,
            support,
        )

        if (
            stop_loss <= 0
            or stop_loss >= entry
        ):

            return None

        risk = (
            entry
            - stop_loss
        )

        if risk <= 0:

            return None

        target1 = (
            entry
            + risk
            * self.minimum_rr
        )

        target2 = (
            entry
            + risk
            * 3.0
        )

        target3 = (
            entry
            + risk
            * 4.0
        )

        (
            score,
            confidence,
            breakdown,
        ) = self._calculate_score(
            data,
            wedge,
            breakout=breakout,
            volume_contraction=(
                volume_contraction
            ),
        )

        if score < self.minimum_score:

            return None

        if (
            confidence
            < self.minimum_confidence
        ):

            return None

        if breakout:

            signal_type = (
                SignalType.BUY
            )

            remarks = (
                "FALLING_WEDGE_BREAKOUT"
            )

        else:

            signal_type = (
                SignalType.WATCH
            )

            remarks = (
                "FALLING_WEDGE_PRE_BREAKOUT"
            )

        if (
            breakout
            and data["adx"] >= 30
        ):

            market_trend = (
                MarketTrend.STRONG_BULLISH
            )

        elif breakout:

            market_trend = (
                MarketTrend.BULLISH
            )

        else:

            market_trend = (
                MarketTrend.SIDEWAYS
            )

        signal = Signal(

            instrument_key=(
                data[
                    "instrument_key"
                ]
            ),

            symbol=(
                data[
                    "symbol"
                ]
            ),

            signal_type=signal_type,

            pattern=(
                PatternType.FALLING_WEDGE
            ),

            strength=self._strength(
                score
            ),

            scanner_name=self.name,

            scanner_version=self.version,

            strategy_name=(
                "StockVersity Falling Wedge"
            ),

            timeframe=self.timeframe,

            market_trend=market_trend,

            sector=(
                data[
                    "sector"
                ]
            ),

            sector_strength=(
                data[
                    "sector_strength"
                ]
            ),

            market_strength=(
                data[
                    "market_strength"
                ]
            ),

            relative_strength=(
                data[
                    "relative_strength"
                ]
            ),

            beta=(
                data[
                    "beta"
                ]
            ),

            last_price=(
                data[
                    "last_price"
                ]
            ),

            open_price=(
                data[
                    "open_price"
                ]
            ),

            high_price=(
                data[
                    "high_price"
                ]
            ),

            low_price=(
                data[
                    "low_price"
                ]
            ),

            close_price=(
                data[
                    "close_price"
                ]
            ),

            previous_close=(
                data[
                    "previous_close"
                ]
            ),

            volume=(
                data[
                    "volume"
                ]
            ),

            average_volume=(
                data[
                    "average_volume"
                ]
            ),

            volume_ratio=round(
                data[
                    "volume_ratio"
                ],
                2,
            ),

            trigger_price=round(
                resistance,
                2,
            ),

            entry=round(
                entry,
                2,
            ),

            stop_loss=stop_loss,

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

            atr=(
                data[
                    "atr"
                ]
            ),

            atr_multiple=(
                self.atr_stop_multiple
            ),

            atr_stop=stop_loss,

            ema9=(
                data[
                    "ema9"
                ]
            ),

            ema20=(
                data[
                    "ema20"
                ]
            ),

            ema21=(
                data[
                    "ema21"
                ]
            ),

            ema50=(
                data[
                    "ema50"
                ]
            ),

            ema100=(
                data[
                    "ema100"
                ]
            ),

            ema200=(
                data[
                    "ema200"
                ]
            ),

            rsi=(
                data[
                    "rsi"
                ]
            ),

            macd=(
                data[
                    "macd"
                ]
            ),

            macd_signal=(
                data[
                    "macd_signal"
                ]
            ),

            macd_histogram=(
                data[
                    "macd_histogram"
                ]
            ),

            adx=(
                data[
                    "adx"
                ]
            ),

            plus_di=(
                data[
                    "plus_di"
                ]
            ),

            minus_di=(
                data[
                    "minus_di"
                ]
            ),

            vwap=(
                data[
                    "vwap"
                ]
            ),

            confidence=confidence,

            score=score,

            score_breakdown=breakdown,

            remarks=remarks,

            tags=[

                "FALLING_WEDGE",

                (
                    "BREAKOUT"
                    if breakout
                    else "PRE_BREAKOUT"
                ),

                self.timeframe.upper(),

            ],

            metadata={

                "market_cap":
                    data[
                        "market_cap"
                    ],

                "wedge_resistance":
                    round(
                        resistance,
                        2,
                    ),

                "wedge_support":
                    round(
                        support,
                        2,
                    ),

                "upper_slope":
                    round(
                        wedge[
                            "upper_slope"
                        ],
                        6,
                    ),

                "lower_slope":
                    round(
                        wedge[
                            "lower_slope"
                        ],
                        6,
                    ),

                "contraction_percent":
                    round(
                        wedge[
                            "contraction"
                        ],
                        2,
                    ),

                "initial_width":
                    round(
                        wedge[
                            "initial_width"
                        ],
                        2,
                    ),

                "current_width":
                    round(
                        wedge[
                            "current_width"
                        ],
                        2,
                    ),

                "volume_contraction":
                    volume_contraction,

                "breakout":
                    breakout,

                "scanner_family":
                    "FALLING_WEDGE",

            },

        )

        if (
            signal.risk_reward
            < self.minimum_rr
        ):

            return None

        return signal

    # =====================================================
    # SCAN
    # =====================================================

    def scan(
        self,
        market_data: Dict[str, Any],
    ) -> List[Signal]:

        generated: List[
            Signal
        ] = []

        if not isinstance(
            market_data,
            dict,
        ):

            return generated

        for key, raw in (
            market_data.items()
        ):

            if not isinstance(
                raw,
                dict,
            ):

                continue

            try:

                data = (
                    self._normalize_record(
                        str(key),
                        raw,
                    )
                )

                symbol = data[
                    "symbol"
                ]

                if symbol:

                    self.symbols.append(
                        symbol
                    )

                # -------------------------------------
                # BASIC FILTERS
                # -------------------------------------

                if not (
                    self._passes_basic_filters(
                        data
                    )
                ):

                    continue

                # -------------------------------------
                # WEDGE STRUCTURE
                # -------------------------------------

                wedge = (
                    self._analyze_wedge(
                        data
                    )
                )

                if wedge is None:

                    continue

                resistance = wedge[
                    "resistance"
                ]

                # -------------------------------------
                # BREAKOUT STATE
                # -------------------------------------

                breakout = (
                    self._is_breakout(
                        data,
                        resistance,
                    )
                )

                pre_breakout = (
                    self._is_pre_breakout(
                        data,
                        resistance,
                    )
                )

                if not (
                    breakout
                    or pre_breakout
                ):

                    continue

                # -------------------------------------
                # MOMENTUM
                # -------------------------------------

                if not (
                    self._momentum_valid(
                        data,
                        breakout,
                    )
                ):

                    continue

                # -------------------------------------
                # VOLUME CONTRACTION
                # -------------------------------------

                volume_contraction = (
                    self._volume_contraction(
                        data
                    )
                )

                # WATCH requires proper contraction.
                # Confirmed breakout can pass because
                # breakout RVOL itself confirms demand.

                if (
                    pre_breakout
                    and not volume_contraction
                ):

                    continue

                # -------------------------------------
                # SIGNAL
                # -------------------------------------

                signal = (
                    self._create_signal(
                        data,
                        wedge,
                        breakout=breakout,
                        volume_contraction=(
                            volume_contraction
                        ),
                    )
                )

                if signal is None:

                    continue

                generated.append(
                    signal
                )

            except Exception as exc:

                self.log(
                    "Falling Wedge scan failed:",
                    key,
                    repr(exc),
                )

        return generated

    # =====================================================
    # CONFIGURATION
    # =====================================================

    def configuration(
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

            "minimum_score":
                self.minimum_score,

            "minimum_confidence":
                self.minimum_confidence,

            "minimum_rr":
                self.minimum_rr,

            "minimum_adx":
                self.minimum_adx,

            "breakout_volume_ratio":
                self.breakout_volume_ratio,

            "dry_volume_ratio":
                self.dry_volume_ratio,

            "breakout_buffer_percent":
                self.breakout_buffer_percent,

            "pre_breakout_distance_percent":
                self.pre_breakout_distance_percent,

            "atr_stop_multiple":
                self.atr_stop_multiple,

            "minimum_contraction_percent":
                self.minimum_contraction_percent,

            "lookback":
                self.lookback,

            "max_signals":
                self.max_signals,

        }


# =========================================================
# FACTORY
# =========================================================

def create_falling_wedge_scanner(
    **kwargs: Any,
) -> FallingWedgeScanner:

    return FallingWedgeScanner(
        **kwargs
    )


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "FallingWedgeScanner",

    "create_falling_wedge_scanner",

]


# =========================================================
# END OF FILE
# =========================================================