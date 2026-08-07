"""
=========================================================
StockVersity Scanner Pro
Breakout Scanner
Version : 2.0
=========================================================

Professional multi-timeframe breakout scanner.

Detects:
• Range breakout
• Previous-day high breakout
• Weekly breakout
• Monthly breakout
• 3-month breakout
• 52-week breakout
• Volume-confirmed breakout
• Breakdown / short setups
• EMA trend confirmation
• ADX confirmation
• Relative-strength confirmation

Default universe:
• Price >= ₹200
• Market Cap >= ₹1,000 Cr
=========================================================
"""

from __future__ import annotations

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from core.scanner.base_scanner import BaseScanner

from core.scanner.signal import Signal
from core.scanner.signal import SignalType
from core.scanner.signal import SignalStrength
from core.scanner.signal import PatternType
from core.scanner.signal import MarketTrend

from core.scanner.filters import ScannerFilters
from core.scanner.filters import create_scanner_filters


# =========================================================
# BREAKOUT SCANNER
# =========================================================

class BreakoutScanner(BaseScanner):
    """
    Multi-timeframe breakout / breakdown scanner.

    Expected market_data format
    ---------------------------

    {
        "RELIANCE": {

            "instrument_key": "NSE_EQ|...",
            "symbol": "RELIANCE",
            "exchange": "NSE",

            "open": 1500,
            "high": 1540,
            "low": 1490,
            "close": 1535,
            "previous_close": 1505,

            "volume": 6000000,
            "average_volume": 3000000,

            "ema9": 1510,
            "ema20": 1495,
            "ema21": 1490,
            "ema50": 1450,
            "ema100": 1400,
            "ema200": 1300,

            "rsi": 64,
            "adx": 30,
            "plus_di": 35,
            "minus_di": 15,
            "atr": 25,

            "vwap": 1515,

            "previous_day_high": 1525,
            "previous_day_low": 1480,

            "high_1w": 1520,
            "low_1w": 1450,

            "high_1m": 1530,
            "low_1m": 1400,

            "high_3m": 1535,
            "low_3m": 1350,

            "high_52w": 1540,
            "low_52w": 1100,

            "range_high": 1520,
            "range_low": 1460,

            "market_cap": 1800000,

            "sector": "ENERGY",

            "sector_strength": 75,

            "relative_strength": 82,

            "market_strength": 70,

            "market_trend": "BULLISH",

            "is_fno": True
        }
    }
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        timeframe: str = "15m",
    ) -> None:

        super().__init__(

            name="Breakout Scanner",

            version="2.0",

            timeframe=timeframe,
        )

        # -------------------------------------------------
        # QUALITY SETTINGS
        # -------------------------------------------------

        self.minimum_score = 65.0

        self.minimum_rr = 2.0

        self.max_signals = 30

        # -------------------------------------------------
        # UNIVERSE
        # -------------------------------------------------

        self.minimum_price = 200.0

        self.minimum_market_cap = 1000.0

        # -------------------------------------------------
        # BREAKOUT QUALITY
        # -------------------------------------------------

        self.minimum_volume_ratio = 1.20

        self.strong_volume_ratio = 2.0

        self.minimum_adx = 20.0

        self.maximum_gap_percent = 3.0

        # -------------------------------------------------
        # ENTRY
        # -------------------------------------------------

        self.entry_buffer_percent = 0.05

        self.stop_atr_multiple = 1.5

        # -------------------------------------------------
        # TARGETS
        # -------------------------------------------------

        self.target_rr_1 = 2.0

        self.target_rr_2 = 3.0

        self.target_rr_3 = 4.0

        # -------------------------------------------------
        # FILTER ENGINE
        # -------------------------------------------------

        self.filters: ScannerFilters = (
            create_scanner_filters(
                "breakout"
            )
        )

        self.filters.configure(

            minimum_price=self.minimum_price,

            minimum_market_cap=(
                self.minimum_market_cap
            ),

            minimum_volume_ratio=(
                self.minimum_volume_ratio
            ),

            minimum_adx=self.minimum_adx,

            maximum_gap_percent=(
                self.maximum_gap_percent
            ),

            minimum_score=self.minimum_score,

            minimum_risk_reward=(
                self.minimum_rr
            ),
        )

    # =====================================================
    # MAIN SCAN
    # =====================================================

    def scan(
        self,
        market_data: Dict[str, Any],
    ) -> List[Signal]:

        generated: List[Signal] = []

        if not market_data:
            return generated

        for key, data in market_data.items():

            if not isinstance(
                data,
                dict,
            ):
                continue

            try:

                signal = self._scan_symbol(
                    key,
                    data,
                )

                if signal is not None:

                    generated.append(
                        signal
                    )

            except Exception as exc:

                self.log(
                    "Breakout scan error:",
                    key,
                    exc,
                )

        return generated

    # =====================================================
    # SCAN ONE SYMBOL
    # =====================================================

    def _scan_symbol(
        self,
        key: str,
        data: Dict[str, Any],
    ) -> Optional[Signal]:

        symbol = str(

            data.get(
                "symbol",
                key,
            )

        ).upper().strip()

        instrument_key = str(

            data.get(
                "instrument_key",
                key,
            )

        ).strip()

        if not symbol:
            return None

        # -------------------------------------------------
        # OHLC
        # -------------------------------------------------

        open_price = self._float(
            data.get("open")
        )

        high = self._float(
            data.get("high")
        )

        low = self._float(
            data.get("low")
        )

        close = self._float(

            data.get(
                "close",
                data.get(
                    "last_price",
                    0.0,
                ),
            )

        )

        previous_close = self._float(
            data.get(
                "previous_close"
            )
        )

        if close <= 0:
            return None

        # -------------------------------------------------
        # UNIVERSE FILTER
        # -------------------------------------------------

        market_cap = self._float(
            data.get(
                "market_cap"
            )
        )

        if close < self.minimum_price:
            return None

        if (
            market_cap
            < self.minimum_market_cap
        ):
            return None

        # -------------------------------------------------
        # GAP FILTER
        # -------------------------------------------------

        gap_percent = 0.0

        if (
            previous_close > 0
            and open_price > 0
        ):

            gap_percent = (

                (
                    open_price
                    - previous_close
                )

                / previous_close

            ) * 100.0

        if (
            abs(gap_percent)
            > self.maximum_gap_percent
        ):
            return None

        # -------------------------------------------------
        # VOLUME
        # -------------------------------------------------

        volume = self._int(
            data.get(
                "volume"
            )
        )

        average_volume = self._int(
            data.get(
                "average_volume"
            )
        )

        volume_ratio = 0.0

        if average_volume > 0:

            volume_ratio = (

                volume
                / average_volume

            )

        # We do NOT want breakout without volume.

        if (
            volume_ratio
            < self.minimum_volume_ratio
        ):
            return None

        # -------------------------------------------------
        # INDICATORS
        # -------------------------------------------------

        ema9 = self._float(
            data.get("ema9")
        )

        ema20 = self._float(
            data.get("ema20")
        )

        ema21 = self._float(
            data.get("ema21")
        )

        ema50 = self._float(
            data.get("ema50")
        )

        ema100 = self._float(
            data.get("ema100")
        )

        ema200 = self._float(
            data.get("ema200")
        )

        rsi = self._float(
            data.get("rsi")
        )

        adx = self._float(
            data.get("adx")
        )

        plus_di = self._float(
            data.get("plus_di")
        )

        minus_di = self._float(
            data.get("minus_di")
        )

        atr = self._float(
            data.get("atr")
        )

        vwap = self._float(
            data.get("vwap")
        )

        # -------------------------------------------------
        # STRENGTH
        # -------------------------------------------------

        sector = str(
            data.get(
                "sector",
                "",
            )
        )

        sector_strength = self._float(
            data.get(
                "sector_strength"
            )
        )

        relative_strength = self._float(
            data.get(
                "relative_strength"
            )
        )

        market_strength = self._float(
            data.get(
                "market_strength"
            )
        )

        beta = self._float(
            data.get(
                "beta"
            )
        )

        # -------------------------------------------------
        # ADX FILTER
        # -------------------------------------------------

        if (
            adx > 0
            and adx < self.minimum_adx
        ):
            return None

        # -------------------------------------------------
        # DETECT BREAKOUT
        # -------------------------------------------------

        breakout = self._detect_breakout(
            data=data,
            close=close,
        )

        if breakout is None:
            return None

        (
            signal_type,
            breakout_level,
            breakout_name,
        ) = breakout

        # -------------------------------------------------
        # TREND CONFIRMATION
        # -------------------------------------------------

        if not self._trend_confirmed(

            signal_type=signal_type,

            close=close,

            ema20=ema20,

            ema50=ema50,

            ema200=ema200,

            plus_di=plus_di,

            minus_di=minus_di,

            vwap=vwap,

        ):
            return None

        # -------------------------------------------------
        # ENTRY / STOP / TARGETS
        # -------------------------------------------------

        levels = self._trade_levels(

            signal_type=signal_type,

            breakout_level=breakout_level,

            close=close,

            high=high,

            low=low,

            atr=atr,

            data=data,
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

        # -------------------------------------------------
        # PATTERN
        # -------------------------------------------------

        if signal_type == SignalType.BUY:

            pattern = (
                PatternType.BREAKOUT
            )

        else:

            pattern = (
                PatternType.BREAKDOWN
            )

        # -------------------------------------------------
        # SCORE
        # -------------------------------------------------

        score_breakdown = (
            self._score_breakdown(

                signal_type=signal_type,

                breakout_name=(
                    breakout_name
                ),

                close=close,

                ema20=ema20,

                ema50=ema50,

                ema200=ema200,

                rsi=rsi,

                adx=adx,

                plus_di=plus_di,

                minus_di=minus_di,

                volume_ratio=(
                    volume_ratio
                ),

                relative_strength=(
                    relative_strength
                ),

                sector_strength=(
                    sector_strength
                ),
            )
        )

        score = round(

            min(

                sum(
                    score_breakdown.values()
                ),

                100.0,
            ),

            2,
        )

        # -------------------------------------------------
        # CONFIDENCE
        # -------------------------------------------------

        confidence = self._confidence(

            score=score,

            breakout_name=(
                breakout_name
            ),

            volume_ratio=(
                volume_ratio
            ),

            adx=adx,

            relative_strength=(
                relative_strength
            ),
        )

        strength = self._strength(
            score
        )

        market_trend = (
            self._market_trend(
                data
            )
        )

        # -------------------------------------------------
        # SIGNAL
        # -------------------------------------------------

        signal = Signal(

            instrument_key=(
                instrument_key
            ),

            symbol=symbol,

            exchange=str(

                data.get(
                    "exchange",
                    "NSE",
                )

            ),

            signal_type=(
                signal_type
            ),

            pattern=pattern,

            strength=strength,

            scanner_name=self.name,

            scanner_version=(
                self.version
            ),

            strategy_name=(
                "StockVersity Breakout"
            ),

            timeframe=self.timeframe,

            market_trend=(
                market_trend
            ),

            sector=sector,

            sector_strength=(
                sector_strength
            ),

            market_strength=(
                market_strength
            ),

            relative_strength=(
                relative_strength
            ),

            beta=beta,

            last_price=close,

            open_price=open_price,

            high_price=high,

            low_price=low,

            close_price=close,

            previous_close=(
                previous_close
            ),

            gap_percent=round(
                gap_percent,
                2,
            ),

            volume=volume,

            average_volume=(
                average_volume
            ),

            volume_ratio=round(
                volume_ratio,
                2,
            ),

            trigger_price=(
                breakout_level
            ),

            entry=entry,

            stop_loss=stop_loss,

            target1=target1,

            target2=target2,

            target3=target3,

            atr=atr,

            ema9=ema9,

            ema20=ema20,

            ema21=ema21,

            ema50=ema50,

            ema100=ema100,

            ema200=ema200,

            rsi=rsi,

            adx=adx,

            plus_di=plus_di,

            minus_di=minus_di,

            vwap=vwap,

            confidence=confidence,

            score=score,

            score_breakdown=(
                score_breakdown
            ),

            remarks=(

                f"{breakout_name} "
                f"{signal_type.value} | "
                f"RVOL {volume_ratio:.2f}x | "
                f"ADX {adx:.1f} | "
                f"RSI {rsi:.1f}"

            ),

            tags=[

                "BREAKOUT",

                breakout_name,

                signal_type.value,
            ],

            metadata={

                "market_cap": (
                    market_cap
                ),

                "breakout_name": (
                    breakout_name
                ),

                "breakout_level": (
                    breakout_level
                ),

                "is_fno": bool(

                    data.get(
                        "is_fno",
                        False,
                    )

                ),
            },
        )

        # -------------------------------------------------
        # CENTRAL FILTER
        # -------------------------------------------------

        filter_result = (
            self.filters.evaluate(
                signal
            )
        )

        signal.metadata[
            "filter_result"
        ] = filter_result.to_dict()

        if not filter_result.passed:
            return None

        return signal

    # =====================================================
    # DETECT BREAKOUT
    # =====================================================

    def _detect_breakout(
        self,
        *,
        data: Dict[str, Any],
        close: float,
    ) -> Optional[
        Tuple[
            SignalType,
            float,
            str,
        ]
    ]:

        # -------------------------------------------------
        # BULLISH LEVELS
        # Strongest breakout checked first.
        # -------------------------------------------------

        bullish_levels = [

            (
                "52_WEEK_BREAKOUT",
                self._float(
                    data.get(
                        "high_52w"
                    )
                ),
            ),

            (
                "3_MONTH_BREAKOUT",
                self._float(
                    data.get(
                        "high_3m"
                    )
                ),
            ),

            (
                "MONTHLY_BREAKOUT",
                self._float(
                    data.get(
                        "high_1m"
                    )
                ),
            ),

            (
                "WEEKLY_BREAKOUT",
                self._float(
                    data.get(
                        "high_1w"
                    )
                ),
            ),

            (
                "PREVIOUS_DAY_HIGH",
                self._float(
                    data.get(
                        "previous_day_high"
                    )
                ),
            ),

            (
                "RANGE_BREAKOUT",
                self._float(
                    data.get(
                        "range_high"
                    )
                ),
            ),
        ]

        for name, level in bullish_levels:

            if (
                level > 0
                and close > level
            ):

                return (
                    SignalType.BUY,
                    level,
                    name,
                )

        # -------------------------------------------------
        # BEARISH LEVELS
        # -------------------------------------------------

        bearish_levels = [

            (
                "52_WEEK_BREAKDOWN",
                self._float(
                    data.get(
                        "low_52w"
                    )
                ),
            ),

            (
                "3_MONTH_BREAKDOWN",
                self._float(
                    data.get(
                        "low_3m"
                    )
                ),
            ),

            (
                "MONTHLY_BREAKDOWN",
                self._float(
                    data.get(
                        "low_1m"
                    )
                ),
            ),

            (
                "WEEKLY_BREAKDOWN",
                self._float(
                    data.get(
                        "low_1w"
                    )
                ),
            ),

            (
                "PREVIOUS_DAY_LOW",
                self._float(
                    data.get(
                        "previous_day_low"
                    )
                ),
            ),

            (
                "RANGE_BREAKDOWN",
                self._float(
                    data.get(
                        "range_low"
                    )
                ),
            ),
        ]

        for name, level in bearish_levels:

            if (
                level > 0
                and close < level
            ):

                return (
                    SignalType.SELL,
                    level,
                    name,
                )

        return None

    # =====================================================
    # TREND CONFIRMATION
    # =====================================================

    @staticmethod
    def _trend_confirmed(
        *,
        signal_type: SignalType,
        close: float,
        ema20: float,
        ema50: float,
        ema200: float,
        plus_di: float,
        minus_di: float,
        vwap: float,
    ) -> bool:

        bullish_points = 0

        bearish_points = 0

        if ema20 > 0:

            if close > ema20:
                bullish_points += 1

            elif close < ema20:
                bearish_points += 1

        if ema50 > 0:

            if close > ema50:
                bullish_points += 1

            elif close < ema50:
                bearish_points += 1

        if ema200 > 0:

            if close > ema200:
                bullish_points += 1

            elif close < ema200:
                bearish_points += 1

        if vwap > 0:

            if close > vwap:
                bullish_points += 1

            elif close < vwap:
                bearish_points += 1

        if plus_di > minus_di:

            bullish_points += 1

        elif minus_di > plus_di:

            bearish_points += 1

        if signal_type == SignalType.BUY:

            return bullish_points >= 2

        return bearish_points >= 2

    # =====================================================
    # TRADE LEVELS
    # =====================================================

    def _trade_levels(
        self,
        *,
        signal_type: SignalType,
        breakout_level: float,
        close: float,
        high: float,
        low: float,
        atr: float,
        data: Dict[str, Any],
    ) -> Optional[
        Tuple[
            float,
            float,
            float,
            float,
            float,
        ]
    ]:

        if atr <= 0:

            if (
                high > low
                and low > 0
            ):

                atr = high - low

            else:

                atr = (
                    close * 0.01
                )

        buffer = (

            breakout_level
            * self.entry_buffer_percent
            / 100.0

        )

        # -------------------------------------------------
        # BUY
        # -------------------------------------------------

        if signal_type == SignalType.BUY:

            entry = max(

                close,

                breakout_level
                + buffer,

            )

            swing_low = self._float(

                data.get(
                    "previous_swing_low"
                )

            )

            atr_stop = (

                entry
                - (
                    atr
                    * self.stop_atr_multiple
                )

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
                entry - stop_loss
            )

            if risk <= 0:
                return None

            target1 = (

                entry
                + risk
                * self.target_rr_1

            )

            target2 = (

                entry
                + risk
                * self.target_rr_2

            )

            target3 = (

                entry
                + risk
                * self.target_rr_3

            )

        # -------------------------------------------------
        # SELL
        # -------------------------------------------------

        else:

            entry = min(

                close,

                breakout_level
                - buffer,

            )

            swing_high = self._float(

                data.get(
                    "previous_swing_high"
                )

            )

            atr_stop = (

                entry
                + (
                    atr
                    * self.stop_atr_multiple
                )

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
                stop_loss - entry
            )

            if risk <= 0:
                return None

            target1 = (

                entry
                - risk
                * self.target_rr_1

            )

            target2 = (

                entry
                - risk
                * self.target_rr_2

            )

            target3 = (

                entry
                - risk
                * self.target_rr_3

            )

            if target1 <= 0:
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
    # SCORE BREAKDOWN
    # =====================================================

    def _score_breakdown(
        self,
        *,
        signal_type: SignalType,
        breakout_name: str,
        close: float,
        ema20: float,
        ema50: float,
        ema200: float,
        rsi: float,
        adx: float,
        plus_di: float,
        minus_di: float,
        volume_ratio: float,
        relative_strength: float,
        sector_strength: float,
    ) -> Dict[str, float]:

        scores = {

            "trend": 0.0,

            "volume": 0.0,

            "momentum": 0.0,

            "pattern": 0.0,

            "sector": 0.0,

            "relative_strength": 0.0,

            "market": 0.0,
        }

        # -------------------------------------------------
        # TREND - MAX 20
        # -------------------------------------------------

        if signal_type == SignalType.BUY:

            if (
                ema20 > 0
                and close > ema20
            ):
                scores["trend"] += 5

            if (
                ema50 > 0
                and close > ema50
            ):
                scores["trend"] += 6

            if (
                ema200 > 0
                and close > ema200
            ):
                scores["trend"] += 6

            if plus_di > minus_di:
                scores["trend"] += 3

        else:

            if (
                ema20 > 0
                and close < ema20
            ):
                scores["trend"] += 5

            if (
                ema50 > 0
                and close < ema50
            ):
                scores["trend"] += 6

            if (
                ema200 > 0
                and close < ema200
            ):
                scores["trend"] += 6

            if minus_di > plus_di:
                scores["trend"] += 3

        # -------------------------------------------------
        # VOLUME - MAX 20
        # -------------------------------------------------

        if volume_ratio >= 3.0:

            scores["volume"] = 20

        elif volume_ratio >= 2.0:

            scores["volume"] = 17

        elif volume_ratio >= 1.5:

            scores["volume"] = 13

        elif volume_ratio >= 1.2:

            scores["volume"] = 8

        # -------------------------------------------------
        # MOMENTUM - MAX 15
        # -------------------------------------------------

        if adx >= 35:

            scores["momentum"] += 8

        elif adx >= 25:

            scores["momentum"] += 6

        elif adx >= 20:

            scores["momentum"] += 4

        if signal_type == SignalType.BUY:

            if 55 <= rsi <= 72:

                scores["momentum"] += 7

            elif rsi > 50:

                scores["momentum"] += 4

        else:

            if 28 <= rsi <= 45:

                scores["momentum"] += 7

            elif (
                rsi > 0
                and rsi < 50
            ):

                scores["momentum"] += 4

        # -------------------------------------------------
        # PATTERN - MAX 20
        # -------------------------------------------------

        breakout_scores = {

            "52_WEEK_BREAKOUT": 20,

            "52_WEEK_BREAKDOWN": 20,

            "3_MONTH_BREAKOUT": 18,

            "3_MONTH_BREAKDOWN": 18,

            "MONTHLY_BREAKOUT": 16,

            "MONTHLY_BREAKDOWN": 16,

            "WEEKLY_BREAKOUT": 14,

            "WEEKLY_BREAKDOWN": 14,

            "PREVIOUS_DAY_HIGH": 11,

            "PREVIOUS_DAY_LOW": 11,

            "RANGE_BREAKOUT": 12,

            "RANGE_BREAKDOWN": 12,
        }

        scores["pattern"] = (
            breakout_scores.get(
                breakout_name,
                10,
            )
        )

        # -------------------------------------------------
        # SECTOR - MAX 10
        # -------------------------------------------------

        if sector_strength >= 80:

            scores["sector"] = 10

        elif sector_strength >= 70:

            scores["sector"] = 8

        elif sector_strength >= 50:

            scores["sector"] = 5

        elif sector_strength >= 40:

            scores["sector"] = 3

        # -------------------------------------------------
        # RELATIVE STRENGTH - MAX 10
        # -------------------------------------------------

        if relative_strength >= 85:

            scores[
                "relative_strength"
            ] = 10

        elif relative_strength >= 75:

            scores[
                "relative_strength"
            ] = 8

        elif relative_strength >= 60:

            scores[
                "relative_strength"
            ] = 6

        elif relative_strength >= 50:

            scores[
                "relative_strength"
            ] = 4

        # -------------------------------------------------
        # MARKET - MAX 5
        # -------------------------------------------------

        if (
            volume_ratio >= 2.0
            and adx >= 25
        ):

            scores["market"] = 5

        elif (
            volume_ratio >= 1.5
            and adx >= 20
        ):

            scores["market"] = 3

        return scores

    # =====================================================
    # CONFIDENCE
    # =====================================================

    @staticmethod
    def _confidence(
        *,
        score: float,
        breakout_name: str,
        volume_ratio: float,
        adx: float,
        relative_strength: float,
    ) -> float:

        confidence = (
            score * 0.65
        )

        if volume_ratio >= 3.0:

            confidence += 12

        elif volume_ratio >= 2.0:

            confidence += 9

        elif volume_ratio >= 1.5:

            confidence += 5

        if adx >= 35:

            confidence += 8

        elif adx >= 25:

            confidence += 5

        if relative_strength >= 80:

            confidence += 8

        elif relative_strength >= 60:

            confidence += 5

        major_breakouts = {

            "52_WEEK_BREAKOUT",

            "52_WEEK_BREAKDOWN",

            "3_MONTH_BREAKOUT",

            "3_MONTH_BREAKDOWN",
        }

        if breakout_name in major_breakouts:

            confidence += 8

        return round(

            min(
                confidence,
                100.0,
            ),

            2,
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
        data: Dict[str, Any],
    ) -> MarketTrend:

        raw = str(

            data.get(
                "market_trend",
                "SIDEWAYS",
            )

        ).upper()

        mapping = {

            "STRONG_BULLISH":
                MarketTrend.STRONG_BULLISH,

            "BULLISH":
                MarketTrend.BULLISH,

            "SIDEWAYS":
                MarketTrend.SIDEWAYS,

            "NEUTRAL":
                MarketTrend.SIDEWAYS,

            "BEARISH":
                MarketTrend.BEARISH,

            "STRONG_BEARISH":
                MarketTrend.STRONG_BEARISH,
        }

        return mapping.get(

            raw,

            MarketTrend.SIDEWAYS,
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
    # SAFE INTEGER
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


# =========================================================
# FACTORY
# =========================================================

def create_breakout_scanner(
    timeframe: str = "15m",
) -> BreakoutScanner:

    return BreakoutScanner(
        timeframe=timeframe
    )


# =========================================================
# EXPORTS
# =========================================================

__all__ = [

    "BreakoutScanner",

    "create_breakout_scanner",

]


# ==========================
# END OF FILE
# ==========================