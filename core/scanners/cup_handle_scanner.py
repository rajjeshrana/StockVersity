"""
=========================================================
StockVersity Scanner Pro
Cup & Handle Scanner
Version : 2.1
=========================================================

File:
    core/scanners/cup_handle_scanner.py

Purpose:
    Detect bullish Cup & Handle continuation patterns.

Detection
---------
• Cup structure
• Left rim / cup bottom / right rim
• Controlled cup depth
• Right-side recovery
• Handle pullback
• Handle contraction
• Resistance / neckline
• Pre-breakout WATCH
• Confirmed breakout BUY
• Breakout volume confirmation
• RSI / MACD / ADX confirmation
• EMA trend confirmation
• ATR / structure stop loss
• Risk reward validation

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
# CUP & HANDLE SCANNER
# =========================================================

class CupHandleScanner(BaseScanner):

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
        minimum_adx: float = 18.0,
        breakout_volume_ratio: float = 1.50,
        breakout_buffer_percent: float = 0.10,
        pre_breakout_distance_percent: float = 2.0,
        minimum_cup_depth_percent: float = 8.0,
        maximum_cup_depth_percent: float = 40.0,
        maximum_handle_depth_percent: float = 15.0,
        rim_tolerance_percent: float = 6.0,
        atr_stop_multiple: float = 1.5,
        lookback: int = 60,
        max_signals: int = 30,
        debug: bool = False,
    ) -> None:

        super().__init__(
            name="CupHandleScanner",
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

        self.breakout_buffer_percent = max(
            0.0,
            float(breakout_buffer_percent),
        )

        self.pre_breakout_distance_percent = max(
            0.1,
            float(pre_breakout_distance_percent),
        )

        self.minimum_cup_depth_percent = max(
            0.0,
            float(minimum_cup_depth_percent),
        )

        self.maximum_cup_depth_percent = max(
            self.minimum_cup_depth_percent,
            float(maximum_cup_depth_percent),
        )

        self.maximum_handle_depth_percent = max(
            1.0,
            float(maximum_handle_depth_percent),
        )

        self.rim_tolerance_percent = max(
            0.1,
            float(rim_tolerance_percent),
        )

        self.atr_stop_multiple = max(
            0.1,
            float(atr_stop_multiple),
        )

        self.lookback = max(
            20,
            int(lookback),
        )

        self.max_signals = max(
            1,
            int(max_signals),
        )

        self.debug = bool(
            debug
        )

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

            return float(
                value
            )

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
    # SAFE VALUE
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
    # GET BARS
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
    # NORMALIZE RECORD
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

            "resistance":
                self._float(
                    self._value(
                        raw,
                        "cup_handle_resistance",
                        "resistance",
                        "neckline",
                        default=0.0,
                    )
                ),

            "handle_low":
                self._float(
                    self._value(
                        raw,
                        "handle_low",
                        default=0.0,
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
    # BASIC FILTERS
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
    # AVERAGE
    # =====================================================

    @staticmethod
    def _average(
        values: List[float],
    ) -> float:

        if not values:

            return 0.0

        return (
            sum(values)
            / len(values)
        )

    # =====================================================
    # ANALYZE CUP
    # =====================================================

    def _analyze_pattern(
        self,
        data: Dict[str, Any],
    ) -> Optional[
        Dict[str, float]
    ]:

        bars = data[
            "bars"
        ]

        # ---------------------------------------------
        # EXTERNALLY CALCULATED PATTERN
        # ---------------------------------------------

        if len(bars) < 20:

            raw = data[
                "raw"
            ]

            left_rim = self._float(
                raw.get(
                    "cup_left_rim",
                    0.0,
                )
            )

            bottom = self._float(
                raw.get(
                    "cup_bottom",
                    0.0,
                )
            )

            right_rim = self._float(
                raw.get(
                    "cup_right_rim",
                    0.0,
                )
            )

            resistance = data[
                "resistance"
            ]

            handle_low = data[
                "handle_low"
            ]

            if (
                left_rim > 0
                and bottom > 0
                and right_rim > 0
            ):

                if resistance <= 0:

                    resistance = max(
                        left_rim,
                        right_rim,
                    )

                if handle_low <= 0:

                    handle_low = (
                        right_rim
                        * 0.95
                    )

                depth = (

                    (
                        left_rim
                        - bottom
                    )

                    / left_rim

                    * 100.0

                )

                return {

                    "left_rim":
                        left_rim,

                    "bottom":
                        bottom,

                    "right_rim":
                        right_rim,

                    "resistance":
                        resistance,

                    "handle_low":
                        handle_low,

                    "cup_depth_percent":
                        depth,

                    "handle_depth_percent":
                        (
                            (
                                resistance
                                - handle_low
                            )
                            / resistance
                            * 100.0
                        ),

                    "rim_difference_percent":
                        (
                            abs(
                                left_rim
                                - right_rim
                            )
                            / left_rim
                            * 100.0
                        ),

                }

            return None

        # ---------------------------------------------
        # EXTRACT HIGH / LOW / CLOSE
        # ---------------------------------------------

        highs: List[
            float
        ] = []

        lows: List[
            float
        ] = []

        closes: List[
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

            close = self._float(
                bar.get(
                    "close",
                    0.0,
                )
            )

            if (
                high <= 0
                or low <= 0
            ):

                continue

            if close <= 0:

                close = (
                    high + low
                ) / 2.0

            highs.append(
                high
            )

            lows.append(
                low
            )

            closes.append(
                close
            )

        count = len(
            highs
        )

        if count < 20:

            return None

        # ---------------------------------------------
        # SPLIT CUP AND HANDLE
        # ---------------------------------------------

        handle_length = max(
            4,
            int(
                count * 0.20
            ),
        )

        cup_end = (
            count
            - handle_length
        )

        if cup_end < 15:

            return None

        cup_highs = highs[
            :cup_end
        ]

        cup_lows = lows[
            :cup_end
        ]

        handle_highs = highs[
            cup_end:
        ]

        handle_lows = lows[
            cup_end:
        ]

        cup_count = len(
            cup_highs
        )

        rim_window = max(
            3,
            int(
                cup_count
                * 0.20
            ),
        )

        # ---------------------------------------------
        # LEFT RIM
        # ---------------------------------------------

        left_section = cup_highs[
            :rim_window
        ]

        left_rim = max(
            left_section
        )

        # ---------------------------------------------
        # RIGHT RIM
        # ---------------------------------------------

        right_section = cup_highs[
            -rim_window:
        ]

        right_rim = max(
            right_section
        )

        # ---------------------------------------------
        # CUP BOTTOM
        # ---------------------------------------------

        middle_start = (
            rim_window
        )

        middle_end = (
            cup_count
            - rim_window
        )

        if (
            middle_end
            <= middle_start
        ):

            return None

        middle_lows = cup_lows[
            middle_start:
            middle_end
        ]

        if not middle_lows:

            return None

        bottom = min(
            middle_lows
        )

        # ---------------------------------------------
        # VALID PRICE STRUCTURE
        # ---------------------------------------------

        if (
            left_rim <= 0
            or right_rim <= 0
            or bottom <= 0
        ):

            return None

        if bottom >= left_rim:

            return None

        if bottom >= right_rim:

            return None

        # ---------------------------------------------
        # CUP DEPTH
        # ---------------------------------------------

        cup_depth_percent = (

            (
                left_rim
                - bottom
            )

            / left_rim

            * 100.0

        )

        if (
            cup_depth_percent
            < self.minimum_cup_depth_percent
        ):

            return None

        if (
            cup_depth_percent
            > self.maximum_cup_depth_percent
        ):

            return None

        # ---------------------------------------------
        # RIM SIMILARITY
        # ---------------------------------------------

        rim_difference_percent = (

            abs(
                left_rim
                - right_rim
            )

            / left_rim

            * 100.0

        )

        if (
            rim_difference_percent
            > self.rim_tolerance_percent
        ):

            return None

        # ---------------------------------------------
        # HANDLE
        # ---------------------------------------------

        if (
            not handle_highs
            or not handle_lows
        ):

            return None

        handle_high = max(
            handle_highs
        )

        handle_low = min(
            handle_lows
        )

        resistance = data[
            "resistance"
        ]

        if resistance <= 0:

            resistance = max(
                left_rim,
                right_rim,
            )

        if resistance <= 0:

            return None

        handle_depth_percent = (

            (
                resistance
                - handle_low
            )

            / resistance

            * 100.0

        )

        if handle_depth_percent < 0:

            return None

        if (
            handle_depth_percent
            > self.maximum_handle_depth_percent
        ):

            return None

        # ---------------------------------------------
        # HANDLE SHOULD STAY ABOVE CUP MIDPOINT
        # ---------------------------------------------

        cup_midpoint = (

            bottom

            + (
                resistance
                - bottom
            )
            * 0.50

        )

        if handle_low < cup_midpoint:

            return None

        # ---------------------------------------------
        # RIGHT SIDE RECOVERY
        # ---------------------------------------------

        recovery = (

            (
                right_rim
                - bottom
            )

            / (
                left_rim
                - bottom
            )

        )

        if recovery < 0.80:

            return None

        return {

            "left_rim":
                left_rim,

            "bottom":
                bottom,

            "right_rim":
                right_rim,

            "resistance":
                resistance,

            "handle_high":
                handle_high,

            "handle_low":
                handle_low,

            "cup_depth_percent":
                cup_depth_percent,

            "handle_depth_percent":
                handle_depth_percent,

            "rim_difference_percent":
                rim_difference_percent,

            "recovery":
                recovery,

        }

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

        trigger = (

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
            <= trigger
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
    # MOMENTUM VALIDATION
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

                if rsi < 52:

                    return False

            else:

                if rsi < 45:

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
    # VOLUME CONTRACTION
    # =====================================================

    def _handle_volume_contraction(
        self,
        data: Dict[str, Any],
    ) -> bool:

        raw = data[
            "raw"
        ]

        explicit = raw.get(
            "handle_volume_contraction"
        )

        if isinstance(
            explicit,
            bool,
        ):

            return explicit

        bars = data[
            "bars"
        ]

        if len(bars) < 10:

            return False

        handle_length = max(
            4,
            int(
                len(bars)
                * 0.20
            ),
        )

        cup_bars = bars[
            :-handle_length
        ]

        handle_bars = bars[
            -handle_length:
        ]

        cup_volumes = [

            self._float(
                bar.get(
                    "volume",
                    0.0,
                )
            )

            for bar in cup_bars

        ]

        handle_volumes = [

            self._float(
                bar.get(
                    "volume",
                    0.0,
                )
            )

            for bar in handle_bars

        ]

        cup_volumes = [

            volume

            for volume in cup_volumes

            if volume > 0

        ]

        handle_volumes = [

            volume

            for volume in handle_volumes

            if volume > 0

        ]

        if (
            not cup_volumes
            or not handle_volumes
        ):

            return False

        cup_average = (
            sum(cup_volumes)
            / len(cup_volumes)
        )

        handle_average = (
            sum(handle_volumes)
            / len(handle_volumes)
        )

        return (
            handle_average
            < cup_average
        )

    # =====================================================
    # SCORE
    # =====================================================

    def _calculate_score(
        self,
        data: Dict[str, Any],
        pattern: Dict[str, float],
        *,
        breakout: bool,
        volume_contraction: bool,
    ) -> Tuple[
        float,
        float,
        Dict[str, float],
    ]:

        # ---------------------------------------------
        # TREND : 15
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
            or price > ema21
        ):

            trend += 5.0

        if (
            ema50 <= 0
            or price > ema50
        ):

            trend += 5.0

        if (
            ema200 <= 0
            or price > ema200
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

            volume = 5.0

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

        elif rsi >= 45:

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

        pattern_score = 0.0

        cup_depth = pattern[
            "cup_depth_percent"
        ]

        if 12 <= cup_depth <= 30:

            pattern_score += 10.0

        elif (
            self.minimum_cup_depth_percent
            <= cup_depth
            <= self.maximum_cup_depth_percent
        ):

            pattern_score += 7.0

        rim_difference = pattern[
            "rim_difference_percent"
        ]

        if rim_difference <= 2:

            pattern_score += 7.0

        elif rim_difference <= 4:

            pattern_score += 6.0

        else:

            pattern_score += 4.0

        handle_depth = pattern[
            "handle_depth_percent"
        ]

        if handle_depth <= 8:

            pattern_score += 6.0

        elif (
            handle_depth
            <= self.maximum_handle_depth_percent
        ):

            pattern_score += 4.0

        if volume_contraction:

            pattern_score += 4.0

        if breakout:

            pattern_score += 3.0

        else:

            pattern_score += 2.0

        pattern_score = self._clamp(
            pattern_score,
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
        # MARKET : 5
        # ---------------------------------------------

        adx = data[
            "adx"
        ]

        if adx >= 30:

            market = 5.0

        elif adx >= 25:

            market = 4.0

        elif adx >= 18:

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
                    pattern_score,
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

            pattern_score
            / 30.0
            * 100.0

        )

        confidence = (

            score
            * 0.70

            + pattern_quality
            * 0.20

            + (
                100.0
                if breakout
                else 75.0
            )
            * 0.10

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
        handle_low: float,
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
            handle_low > 0
            and handle_low < entry
        ):

            stop = max(
                handle_low,
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
        pattern: Dict[str, float],
        *,
        breakout: bool,
        volume_contraction: bool,
    ) -> Optional[Signal]:

        entry = data[
            "last_price"
        ]

        resistance = pattern[
            "resistance"
        ]

        handle_low = pattern[
            "handle_low"
        ]

        if entry <= 0:

            return None

        stop_loss = self._stop_loss(
            data,
            entry,
            handle_low,
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

        # ---------------------------------------------
        # TARGETS
        # ---------------------------------------------

        rr_target = (

            entry

            + risk
            * self.minimum_rr

        )

        # Classical Cup & Handle measured target:
        # breakout + cup depth

        cup_height = (

            resistance

            - pattern[
                "bottom"
            ]

        )

        measured_target = (

            resistance
            + cup_height

        )

        target1 = max(
            rr_target,
            measured_target,
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
            pattern,
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

        # ---------------------------------------------
        # SIGNAL TYPE
        # ---------------------------------------------

        if breakout:

            signal_type = (
                SignalType.BUY
            )

            remarks = (
                "CUP_HANDLE_BREAKOUT"
            )

        else:

            signal_type = (
                SignalType.WATCH
            )

            remarks = (
                "CUP_HANDLE_PRE_BREAKOUT"
            )

        # ---------------------------------------------
        # MARKET TREND
        # ---------------------------------------------

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

        # ---------------------------------------------
        # CREATE SIGNAL
        # ---------------------------------------------

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
                PatternType.CUP_HANDLE
            ),

            strength=self._strength(
                score
            ),

            scanner_name=self.name,

            scanner_version=self.version,

            strategy_name=(
                "StockVersity Cup Handle"
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

                "CUP_HANDLE",

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

                "left_rim":
                    round(
                        pattern[
                            "left_rim"
                        ],
                        2,
                    ),

                "cup_bottom":
                    round(
                        pattern[
                            "bottom"
                        ],
                        2,
                    ),

                "right_rim":
                    round(
                        pattern[
                            "right_rim"
                        ],
                        2,
                    ),

                "resistance":
                    round(
                        resistance,
                        2,
                    ),

                "handle_low":
                    round(
                        handle_low,
                        2,
                    ),

                "cup_depth_percent":
                    round(
                        pattern[
                            "cup_depth_percent"
                        ],
                        2,
                    ),

                "handle_depth_percent":
                    round(
                        pattern[
                            "handle_depth_percent"
                        ],
                        2,
                    ),

                "rim_difference_percent":
                    round(
                        pattern[
                            "rim_difference_percent"
                        ],
                        2,
                    ),

                "volume_contraction":
                    volume_contraction,

                "breakout":
                    breakout,

                "measured_target":
                    round(
                        measured_target,
                        2,
                    ),

                "scanner_family":
                    "CUP_HANDLE",

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

                # -------------------------------------
                # NORMALIZE
                # -------------------------------------

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
                # PATTERN
                # -------------------------------------

                pattern = (
                    self._analyze_pattern(
                        data
                    )
                )

                if pattern is None:

                    continue

                resistance = pattern[
                    "resistance"
                ]

                # -------------------------------------
                # BREAKOUT
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
                # HANDLE VOLUME
                # -------------------------------------

                volume_contraction = (
                    self._handle_volume_contraction(
                        data
                    )
                )

                # Pre-breakout WATCH should ideally
                # have drying volume in the handle.

                if (
                    pre_breakout
                    and not volume_contraction
                ):

                    continue

                # -------------------------------------
                # CREATE SIGNAL
                # -------------------------------------

                signal = (
                    self._create_signal(
                        data,
                        pattern,
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
                    "Cup Handle scan failed:",
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

            "breakout_buffer_percent":
                self.breakout_buffer_percent,

            "pre_breakout_distance_percent":
                self.pre_breakout_distance_percent,

            "minimum_cup_depth_percent":
                self.minimum_cup_depth_percent,

            "maximum_cup_depth_percent":
                self.maximum_cup_depth_percent,

            "maximum_handle_depth_percent":
                self.maximum_handle_depth_percent,

            "rim_tolerance_percent":
                self.rim_tolerance_percent,

            "atr_stop_multiple":
                self.atr_stop_multiple,

            "lookback":
                self.lookback,

            "max_signals":
                self.max_signals,

        }


# =========================================================
# FACTORY
# =========================================================

def create_cup_handle_scanner(
    **kwargs: Any,
) -> CupHandleScanner:

    return CupHandleScanner(
        **kwargs
    )


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "CupHandleScanner",

    "create_cup_handle_scanner",

]


# =========================================================
# END OF FILE
# =========================================================