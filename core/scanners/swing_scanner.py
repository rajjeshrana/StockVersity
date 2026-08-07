"""
=========================================================
StockVersity Scanner Pro
Swing Scanner
Version : 2.1
=========================================================

File:
    core/scanners/swing_scanner.py

Purpose:
    Detect high-quality swing trading opportunities.

Primary Logic:
    • Trend alignment
    • EMA 21 / 50 / 200 structure
    • Breakout / pullback detection
    • Relative volume confirmation
    • ADX / DI trend strength
    • RSI momentum
    • MACD confirmation
    • Relative strength
    • Sector strength
    • ATR risk management
    • Minimum 1:2 risk/reward
    • Market cap and price filters
=========================================================
"""

from __future__ import annotations

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
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
# SWING SCANNER
# =========================================================

class SwingScanner(BaseScanner):
    """
    StockVersity swing trading scanner.

    Default timeframe
    -----------------
    1h

    Designed primarily for:

        • 1 hour
        • 2 hour
        • 4 hour
        • Daily

    Expected market-data fields
    ---------------------------

    instrument_key
    symbol

    last_price
    open
    high
    low
    close
    previous_close

    volume
    average_volume
    volume_ratio

    ema9
    ema20
    ema21
    ema50
    ema100
    ema200

    rsi

    macd
    macd_signal
    macd_histogram

    adx
    plus_di
    minus_di

    atr

    recent_high
    recent_low

    swing_high
    swing_low

    resistance
    support

    market_cap

    sector
    sector_strength

    market_strength
    relative_strength
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        *,
        timeframe: str = "1h",
        minimum_price: float = 200.0,
        minimum_market_cap: float = 1000.0,
        minimum_volume_ratio: float = 1.20,
        minimum_adx: float = 20.0,
        maximum_gap_percent: float = 5.0,
        minimum_score: float = 65.0,
        minimum_confidence: float = 60.0,
        minimum_rr: float = 2.0,
        breakout_buffer_percent: float = 0.10,
        pullback_tolerance_percent: float = 1.25,
        atr_stop_multiple: float = 1.5,
        max_signals: int = 30,
        debug: bool = False,
    ) -> None:

        super().__init__(
            name="SwingScanner",
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

        self.minimum_volume_ratio = max(
            0.0,
            float(minimum_volume_ratio),
        )

        self.minimum_adx = max(
            0.0,
            float(minimum_adx),
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

        self.breakout_buffer_percent = max(
            0.0,
            float(breakout_buffer_percent),
        )

        self.pullback_tolerance_percent = max(
            0.0,
            float(pullback_tolerance_percent),
        )

        self.atr_stop_multiple = max(
            0.1,
            float(atr_stop_multiple),
        )

        self.max_signals = max(
            1,
            int(max_signals),
        )

        self.debug = bool(
            debug
        )

        # ---------------------------------------------
        # Swing RSI zones
        # ---------------------------------------------

        self.buy_rsi_min = 52.0
        self.buy_rsi_max = 75.0

        self.sell_rsi_min = 25.0
        self.sell_rsi_max = 48.0

        # ---------------------------------------------
        # Target RR
        # ---------------------------------------------

        self.target_rr = max(
            2.0,
            self.minimum_rr,
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
    # VALUE LOOKUP
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

        open_price = self._float(
            self._value(
                raw,
                "open_price",
                "open",
                default=last_price,
            )
        )

        high_price = self._float(
            self._value(
                raw,
                "high_price",
                "high",
                default=last_price,
            )
        )

        low_price = self._float(
            self._value(
                raw,
                "low_price",
                "low",
                default=last_price,
            )
        )

        close_price = self._float(
            self._value(
                raw,
                "close_price",
                "close",
                default=last_price,
            )
        )

        previous_close = self._float(
            self._value(
                raw,
                "previous_close",
                "prev_close",
                "previousClose",
                default=0.0,
            )
        )

        volume = self._int(
            self._value(
                raw,
                "volume",
                "total_volume",
                default=0,
            )
        )

        average_volume = self._int(
            self._value(
                raw,
                "average_volume",
                "avg_volume",
                "averageVolume",
                default=0,
            )
        )

        volume_ratio = self._float(
            self._value(
                raw,
                "volume_ratio",
                "rvol",
                "relative_volume",
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

        market_cap = self._float(
            self._value(
                raw,
                "market_cap",
                "marketCap",
                default=0.0,
            )
        )

        ema9 = self._float(
            raw.get(
                "ema9",
                0.0,
            )
        )

        ema20 = self._float(
            raw.get(
                "ema20",
                0.0,
            )
        )

        ema21 = self._float(
            raw.get(
                "ema21",
                ema20,
            )
        )

        ema50 = self._float(
            raw.get(
                "ema50",
                0.0,
            )
        )

        ema100 = self._float(
            raw.get(
                "ema100",
                0.0,
            )
        )

        ema200 = self._float(
            raw.get(
                "ema200",
                0.0,
            )
        )

        rsi = self._float(
            raw.get(
                "rsi",
                0.0,
            )
        )

        macd = self._float(
            raw.get(
                "macd",
                0.0,
            )
        )

        macd_signal = self._float(
            self._value(
                raw,
                "macd_signal",
                "macdSignal",
                default=0.0,
            )
        )

        macd_histogram = self._float(
            self._value(
                raw,
                "macd_histogram",
                "macd_hist",
                default=(
                    macd
                    - macd_signal
                ),
            )
        )

        adx = self._float(
            raw.get(
                "adx",
                0.0,
            )
        )

        plus_di = self._float(
            self._value(
                raw,
                "plus_di",
                "plusDI",
                default=0.0,
            )
        )

        minus_di = self._float(
            self._value(
                raw,
                "minus_di",
                "minusDI",
                default=0.0,
            )
        )

        atr = self._float(
            raw.get(
                "atr",
                0.0,
            )
        )

        vwap = self._float(
            raw.get(
                "vwap",
                0.0,
            )
        )

        recent_high = self._float(
            self._value(
                raw,
                "recent_high",
                "recentHigh",
                "breakout_high",
                default=0.0,
            )
        )

        recent_low = self._float(
            self._value(
                raw,
                "recent_low",
                "recentLow",
                "breakdown_low",
                default=0.0,
            )
        )

        swing_high = self._float(
            self._value(
                raw,
                "swing_high",
                "swingHigh",
                default=recent_high,
            )
        )

        swing_low = self._float(
            self._value(
                raw,
                "swing_low",
                "swingLow",
                default=recent_low,
            )
        )

        resistance = self._float(
            self._value(
                raw,
                "resistance",
                "resistance_level",
                default=recent_high,
            )
        )

        support = self._float(
            self._value(
                raw,
                "support",
                "support_level",
                default=recent_low,
            )
        )

        gap_percent = self._float(
            raw.get(
                "gap_percent",
                0.0,
            )
        )

        if (
            gap_percent == 0.0
            and previous_close > 0
            and open_price > 0
        ):

            gap_percent = (
                (
                    open_price
                    - previous_close
                )
                / previous_close
                * 100.0
            )

        sector = str(
            raw.get(
                "sector",
                "",
            )
            or ""
        ).strip()

        sector_strength = self._float(
            raw.get(
                "sector_strength",
                0.0,
            )
        )

        market_strength = self._float(
            raw.get(
                "market_strength",
                0.0,
            )
        )

        relative_strength = self._float(
            raw.get(
                "relative_strength",
                0.0,
            )
        )

        beta = self._float(
            raw.get(
                "beta",
                0.0,
            )
        )

        return {

            "instrument_key": instrument_key,

            "symbol": symbol,

            "last_price": last_price,

            "open_price": open_price,

            "high_price": high_price,

            "low_price": low_price,

            "close_price": close_price,

            "previous_close": previous_close,

            "volume": volume,

            "average_volume": average_volume,

            "volume_ratio": volume_ratio,

            "market_cap": market_cap,

            "ema9": ema9,

            "ema20": ema20,

            "ema21": ema21,

            "ema50": ema50,

            "ema100": ema100,

            "ema200": ema200,

            "rsi": rsi,

            "macd": macd,

            "macd_signal": macd_signal,

            "macd_histogram":
                macd_histogram,

            "adx": adx,

            "plus_di": plus_di,

            "minus_di": minus_di,

            "atr": atr,

            "vwap": vwap,

            "recent_high": recent_high,

            "recent_low": recent_low,

            "swing_high": swing_high,

            "swing_low": swing_low,

            "resistance": resistance,

            "support": support,

            "gap_percent": gap_percent,

            "sector": sector,

            "sector_strength":
                sector_strength,

            "market_strength":
                market_strength,

            "relative_strength":
                relative_strength,

            "beta": beta,

            "raw": raw,
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

        if (
            abs(
                data[
                    "gap_percent"
                ]
            )
            > self.maximum_gap_percent
        ):
            return False

        if (
            data[
                "volume_ratio"
            ]
            < self.minimum_volume_ratio
        ):
            return False

        if (
            data["adx"] > 0
            and data["adx"]
            < self.minimum_adx
        ):
            return False

        return True

    # =====================================================
    # PERCENT DISTANCE
    # =====================================================

    @staticmethod
    def _percent_distance(
        price: float,
        level: float,
    ) -> float:

        if level <= 0:
            return 999.0

        return abs(
            (
                price
                - level
            )
            / level
            * 100.0
        )

    # =====================================================
    # BULLISH TREND
    # =====================================================

    def _bullish_trend(
        self,
        data: Dict[str, Any],
    ) -> bool:

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
            ema21 > 0
            and price < ema21
        ):
            return False

        if (
            ema21 > 0
            and ema50 > 0
            and ema21 <= ema50
        ):
            return False

        if (
            ema50 > 0
            and ema200 > 0
            and ema50 <= ema200
        ):
            return False

        return True

    # =====================================================
    # BEARISH TREND
    # =====================================================

    def _bearish_trend(
        self,
        data: Dict[str, Any],
    ) -> bool:

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
            ema21 > 0
            and price > ema21
        ):
            return False

        if (
            ema21 > 0
            and ema50 > 0
            and ema21 >= ema50
        ):
            return False

        if (
            ema50 > 0
            and ema200 > 0
            and ema50 >= ema200
        ):
            return False

        return True

    # =====================================================
    # BULLISH MOMENTUM
    # =====================================================

    def _bullish_momentum(
        self,
        data: Dict[str, Any],
    ) -> bool:

        rsi = data[
            "rsi"
        ]

        if (
            rsi > 0
            and not (
                self.buy_rsi_min
                <= rsi
                <= self.buy_rsi_max
            )
        ):
            return False

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

        macd = data[
            "macd"
        ]

        macd_signal = data[
            "macd_signal"
        ]

        if (
            macd != 0
            and macd_signal != 0
            and macd < macd_signal
        ):
            return False

        return True

    # =====================================================
    # BEARISH MOMENTUM
    # =====================================================

    def _bearish_momentum(
        self,
        data: Dict[str, Any],
    ) -> bool:

        rsi = data[
            "rsi"
        ]

        if (
            rsi > 0
            and not (
                self.sell_rsi_min
                <= rsi
                <= self.sell_rsi_max
            )
        ):
            return False

        plus_di = data[
            "plus_di"
        ]

        minus_di = data[
            "minus_di"
        ]

        if (
            plus_di > 0
            and minus_di > 0
            and minus_di <= plus_di
        ):
            return False

        macd = data[
            "macd"
        ]

        macd_signal = data[
            "macd_signal"
        ]

        if (
            macd != 0
            and macd_signal != 0
            and macd > macd_signal
        ):
            return False

        return True

    # =====================================================
    # BULLISH BREAKOUT
    # =====================================================

    def _bullish_breakout(
        self,
        data: Dict[str, Any],
    ) -> bool:

        price = data[
            "last_price"
        ]

        resistance = (
            data[
                "resistance"
            ]
            or data[
                "recent_high"
            ]
            or data[
                "swing_high"
            ]
        )

        if resistance <= 0:
            return False

        buffer = (
            resistance
            * self.breakout_buffer_percent
            / 100.0
        )

        return (
            price
            > resistance
            + buffer
        )

    # =====================================================
    # BEARISH BREAKDOWN
    # =====================================================

    def _bearish_breakdown(
        self,
        data: Dict[str, Any],
    ) -> bool:

        price = data[
            "last_price"
        ]

        support = (
            data[
                "support"
            ]
            or data[
                "recent_low"
            ]
            or data[
                "swing_low"
            ]
        )

        if support <= 0:
            return False

        buffer = (
            support
            * self.breakout_buffer_percent
            / 100.0
        )

        return (
            price
            < support
            - buffer
        )

    # =====================================================
    # BULLISH PULLBACK
    # =====================================================

    def _bullish_pullback(
        self,
        data: Dict[str, Any],
    ) -> bool:

        price = data[
            "last_price"
        ]

        ema21 = data[
            "ema21"
        ]

        ema50 = data[
            "ema50"
        ]

        near_ema21 = (
            ema21 > 0
            and self._percent_distance(
                price,
                ema21,
            )
            <= self.pullback_tolerance_percent
        )

        near_ema50 = (
            ema50 > 0
            and self._percent_distance(
                price,
                ema50,
            )
            <= self.pullback_tolerance_percent
        )

        if not (
            near_ema21
            or near_ema50
        ):
            return False

        if (
            data["close_price"] > 0
            and data["open_price"] > 0
            and data["close_price"]
            <= data["open_price"]
        ):
            return False

        return True

    # =====================================================
    # BEARISH PULLBACK
    # =====================================================

    def _bearish_pullback(
        self,
        data: Dict[str, Any],
    ) -> bool:

        price = data[
            "last_price"
        ]

        ema21 = data[
            "ema21"
        ]

        ema50 = data[
            "ema50"
        ]

        near_ema21 = (
            ema21 > 0
            and self._percent_distance(
                price,
                ema21,
            )
            <= self.pullback_tolerance_percent
        )

        near_ema50 = (
            ema50 > 0
            and self._percent_distance(
                price,
                ema50,
            )
            <= self.pullback_tolerance_percent
        )

        if not (
            near_ema21
            or near_ema50
        ):
            return False

        if (
            data["close_price"] > 0
            and data["open_price"] > 0
            and data["close_price"]
            >= data["open_price"]
        ):
            return False

        return True

    # =====================================================
    # DETERMINE SETUP
    # =====================================================

    def _determine_setup(
        self,
        data: Dict[str, Any],
    ) -> Optional[
        Tuple[
            SignalType,
            PatternType,
            str,
        ]
    ]:

        bullish_trend = (
            self._bullish_trend(
                data
            )
        )

        bearish_trend = (
            self._bearish_trend(
                data
            )
        )

        if (
            bullish_trend
            and self._bullish_momentum(
                data
            )
        ):

            if self._bullish_breakout(
                data
            ):

                return (
                    SignalType.BUY,
                    PatternType.BREAKOUT,
                    "SWING_BREAKOUT",
                )

            if self._bullish_pullback(
                data
            ):

                return (
                    SignalType.BUY,
                    PatternType.EMA_CROSS,
                    "SWING_PULLBACK",
                )

        if (
            bearish_trend
            and self._bearish_momentum(
                data
            )
        ):

            if self._bearish_breakdown(
                data
            ):

                return (
                    SignalType.SELL,
                    PatternType.BREAKDOWN,
                    "SWING_BREAKDOWN",
                )

            if self._bearish_pullback(
                data
            ):

                return (
                    SignalType.SELL,
                    PatternType.EMA_CROSS,
                    "SWING_PULLBACK",
                )

        return None

    # =====================================================
    # SCORE
    # =====================================================

    def _calculate_score(
        self,
        data: Dict[str, Any],
        signal_type: SignalType,
        setup_name: str,
    ) -> Tuple[
        float,
        float,
        Dict[str, float],
    ]:

        bullish = (
            signal_type
            == SignalType.BUY
        )

        price = data[
            "last_price"
        ]

        # ---------------------------------------------
        # TREND : 20
        # ---------------------------------------------

        trend = 0.0

        ema21 = data[
            "ema21"
        ]

        ema50 = data[
            "ema50"
        ]

        ema200 = data[
            "ema200"
        ]

        if bullish:

            if (
                ema21 <= 0
                or price > ema21
            ):
                trend += 7.0

            if (
                ema21 <= 0
                or ema50 <= 0
                or ema21 > ema50
            ):
                trend += 7.0

            if (
                ema50 <= 0
                or ema200 <= 0
                or ema50 > ema200
            ):
                trend += 6.0

        else:

            if (
                ema21 <= 0
                or price < ema21
            ):
                trend += 7.0

            if (
                ema21 <= 0
                or ema50 <= 0
                or ema21 < ema50
            ):
                trend += 7.0

            if (
                ema50 <= 0
                or ema200 <= 0
                or ema50 < ema200
            ):
                trend += 6.0

        trend = self._clamp(
            trend,
            0.0,
            20.0,
        )

        # ---------------------------------------------
        # VOLUME : 15
        # ---------------------------------------------

        rvol = data[
            "volume_ratio"
        ]

        volume = self._clamp(
            (
                rvol
                / 2.5
            )
            * 15.0,
            0.0,
            15.0,
        )

        # ---------------------------------------------
        # MOMENTUM : 15
        # ---------------------------------------------

        momentum = 0.0

        rsi = data[
            "rsi"
        ]

        if bullish:

            if 55 <= rsi <= 65:
                momentum += 7.0

            elif 52 <= rsi <= 70:
                momentum += 5.0

            elif rsi > 0:
                momentum += 3.0

            if (
                data["plus_di"]
                > data["minus_di"]
            ):
                momentum += 4.0

            if (
                data["macd"]
                >= data["macd_signal"]
            ):
                momentum += 4.0

        else:

            if 35 <= rsi <= 45:
                momentum += 7.0

            elif 30 <= rsi <= 48:
                momentum += 5.0

            elif rsi > 0:
                momentum += 3.0

            if (
                data["minus_di"]
                > data["plus_di"]
            ):
                momentum += 4.0

            if (
                data["macd"]
                <= data["macd_signal"]
            ):
                momentum += 4.0

        momentum = self._clamp(
            momentum,
            0.0,
            15.0,
        )

        # ---------------------------------------------
        # PATTERN : 20
        # ---------------------------------------------

        if setup_name in (
            "SWING_BREAKOUT",
            "SWING_BREAKDOWN",
        ):

            pattern = 20.0

        else:

            pattern = 16.0

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

        rs = data[
            "relative_strength"
        ]

        if rs > 0:

            relative = (
                self._clamp(
                    rs
                )
                * 0.10
            )

        else:

            relative = 5.0

        # ---------------------------------------------
        # MARKET / ADX : 10
        # ---------------------------------------------

        adx = data[
            "adx"
        ]

        if adx >= 35:

            market = 10.0

        elif adx >= 30:

            market = 9.0

        elif adx >= 25:

            market = 7.0

        elif adx >= 20:

            market = 5.0

        else:

            market = 2.0

        breakdown = {

            "trend": round(
                trend,
                2,
            ),

            "volume": round(
                volume,
                2,
            ),

            "momentum": round(
                momentum,
                2,
            ),

            "pattern": round(
                pattern,
                2,
            ),

            "sector": round(
                sector,
                2,
            ),

            "relative_strength": round(
                relative,
                2,
            ),

            "market": round(
                market,
                2,
            ),
        }

        score = self._clamp(
            sum(
                breakdown.values()
            )
        )

        confidence = (
            score * 0.70
            + (
                min(
                    rvol,
                    2.5,
                )
                / 2.5
                * 100.0
            )
            * 0.15
            + (
                min(
                    adx,
                    50.0,
                )
                / 50.0
                * 100.0
            )
            * 0.15
        )

        confidence = self._clamp(
            confidence
        )

        return (
            round(
                score,
                2,
            ),
            round(
                confidence,
                2,
            ),
            breakdown,
        )

    # =====================================================
    # RISK LEVELS
    # =====================================================

    def _risk_levels(
        self,
        data: Dict[str, Any],
        signal_type: SignalType,
    ) -> Optional[
        Tuple[
            float,
            float,
            float,
            float,
            float,
        ]
    ]:

        entry = data[
            "last_price"
        ]

        if entry <= 0:
            return None

        atr = data[
            "atr"
        ]

        if atr <= 0:

            atr = (
                entry
                * 0.02
            )

        atr_distance = (
            atr
            * self.atr_stop_multiple
        )

        if (
            signal_type
            == SignalType.BUY
        ):

            swing_low = (
                data[
                    "swing_low"
                ]
                or data[
                    "recent_low"
                ]
                or data[
                    "support"
                ]
            )

            atr_stop = (
                entry
                - atr_distance
            )

            if (
                swing_low > 0
                and swing_low < entry
            ):

                stop_loss = max(
                    swing_low,
                    atr_stop,
                )

            else:

                stop_loss = atr_stop

            risk = (
                entry
                - stop_loss
            )

            if risk <= 0:
                return None

            target1 = (
                entry
                + risk
                * self.target_rr
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

        else:

            swing_high = (
                data[
                    "swing_high"
                ]
                or data[
                    "recent_high"
                ]
                or data[
                    "resistance"
                ]
            )

            atr_stop = (
                entry
                + atr_distance
            )

            if (
                swing_high > entry
            ):

                stop_loss = min(
                    swing_high,
                    atr_stop,
                )

            else:

                stop_loss = atr_stop

            risk = (
                stop_loss
                - entry
            )

            if risk <= 0:
                return None

            target1 = (
                entry
                - risk
                * self.target_rr
            )

            target2 = (
                entry
                - risk
                * 3.0
            )

            target3 = (
                entry
                - risk
                * 4.0
            )

        if (
            stop_loss <= 0
            or target1 <= 0
        ):
            return None

        return (
            round(
                entry,
                2,
            ),
            round(
                stop_loss,
                2,
            ),
            round(
                target1,
                2,
            ),
            round(
                target2,
                2,
            ),
            round(
                target3,
                2,
            ),
        )

    # =====================================================
    # SIGNAL STRENGTH
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
    # MARKET TREND
    # =====================================================

    @staticmethod
    def _market_trend(
        signal_type: SignalType,
        adx: float,
    ) -> MarketTrend:

        if (
            signal_type
            == SignalType.BUY
        ):

            if adx >= 30:

                return (
                    MarketTrend.STRONG_BULLISH
                )

            return (
                MarketTrend.BULLISH
            )

        if adx >= 30:

            return (
                MarketTrend.STRONG_BEARISH
            )

        return (
            MarketTrend.BEARISH
        )

    # =====================================================
    # CREATE SIGNAL
    # =====================================================

    def _create_signal(
        self,
        data: Dict[str, Any],
        signal_type: SignalType,
        pattern: PatternType,
        setup_name: str,
    ) -> Optional[Signal]:

        levels = self._risk_levels(
            data,
            signal_type,
        )

        if levels is None:

            return None

        (
            entry,
            stop_loss,
            target1,
            target2,
            target3,
        ) = levels

        (
            score,
            confidence,
            score_breakdown,
        ) = self._calculate_score(
            data,
            signal_type,
            setup_name,
        )

        if (
            score
            < self.minimum_score
        ):

            return None

        if (
            confidence
            < self.minimum_confidence
        ):

            return None

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

            pattern=pattern,

            strength=self._strength(
                score
            ),

            scanner_name=self.name,

            scanner_version=self.version,

            strategy_name=(
                "StockVersity Swing"
            ),

            timeframe=self.timeframe,

            market_trend=(
                self._market_trend(
                    signal_type,
                    data["adx"],
                )
            ),

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

            gap_percent=round(
                data[
                    "gap_percent"
                ],
                2,
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

            trigger_price=entry,

            entry=entry,

            stop_loss=stop_loss,

            target1=target1,

            target2=target2,

            target3=target3,

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

            score_breakdown=(
                score_breakdown
            ),

            remarks=setup_name,

            tags=[
                "SWING",
                setup_name,
                self.timeframe.upper(),
                signal_type.value,
            ],

            metadata={

                "market_cap": (
                    data[
                        "market_cap"
                    ]
                ),

                "recent_high": (
                    data[
                        "recent_high"
                    ]
                ),

                "recent_low": (
                    data[
                        "recent_low"
                    ]
                ),

                "swing_high": (
                    data[
                        "swing_high"
                    ]
                ),

                "swing_low": (
                    data[
                        "swing_low"
                    ]
                ),

                "resistance": (
                    data[
                        "resistance"
                    ]
                ),

                "support": (
                    data[
                        "support"
                    ]
                ),

                "setup": setup_name,

                "scanner_family":
                    "SWING",
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

                if not (
                    self._passes_basic_filters(
                        data
                    )
                ):

                    continue

                setup = (
                    self._determine_setup(
                        data
                    )
                )

                if setup is None:

                    continue

                (
                    signal_type,
                    pattern,
                    setup_name,
                ) = setup

                signal = (
                    self._create_signal(
                        data,
                        signal_type,
                        pattern,
                        setup_name,
                    )
                )

                if signal is None:

                    continue

                generated.append(
                    signal
                )

            except Exception as exc:

                self.log(
                    "Swing scan failed:",
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

            "minimum_volume_ratio":
                self.minimum_volume_ratio,

            "minimum_adx":
                self.minimum_adx,

            "maximum_gap_percent":
                self.maximum_gap_percent,

            "minimum_score":
                self.minimum_score,

            "minimum_confidence":
                self.minimum_confidence,

            "minimum_rr":
                self.minimum_rr,

            "breakout_buffer_percent":
                self.breakout_buffer_percent,

            "pullback_tolerance_percent":
                self.pullback_tolerance_percent,

            "atr_stop_multiple":
                self.atr_stop_multiple,

            "target_rr":
                self.target_rr,

            "max_signals":
                self.max_signals,
        }


# =========================================================
# FACTORY
# =========================================================

def create_swing_scanner(
    **kwargs: Any,
) -> SwingScanner:

    return SwingScanner(
        **kwargs
    )


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [
    "SwingScanner",
    "create_swing_scanner",
]


# =========================================================
# END OF FILE
# =========================================================