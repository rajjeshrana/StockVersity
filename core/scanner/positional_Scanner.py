"""
=========================================================
StockVersity Scanner Pro
Positional Scanner
Version : 2.0
=========================================================

Professional positional trading scanner.

Designed for:
• Weekly / Monthly setups
• 3-week breakouts
• Monthly breakouts
• 2-month breakouts
• 3-month breakouts
• 52-week / yearly breakouts
• Long-term trend continuation
• EMA structure
• Volume expansion
• Relative strength
• Sector strength
• Institutional-quality risk/reward

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

from core.scanner.base_scanner import BaseScanner

from core.scanner.signal import Signal
from core.scanner.signal import SignalType
from core.scanner.signal import SignalStrength
from core.scanner.signal import PatternType
from core.scanner.signal import MarketTrend

from core.scanner.filters import ScannerFilters
from core.scanner.filters import create_scanner_filters


# =========================================================
# POSITIONAL SCANNER
# =========================================================

class PositionalScanner(BaseScanner):
    """
    Long-term positional opportunity scanner.

    Expected market_data example
    ----------------------------

    {
        "RELIANCE": {

            "instrument_key": "NSE_EQ|...",
            "symbol": "RELIANCE",
            "exchange": "NSE",

            "open": 1450,
            "high": 1485,
            "low": 1440,
            "close": 1480,
            "previous_close": 1445,

            "volume": 6000000,
            "average_volume": 3000000,

            "ema20": 1430,
            "ema21": 1425,
            "ema50": 1380,
            "ema100": 1300,
            "ema200": 1200,

            "rsi": 65,
            "adx": 30,
            "plus_di": 35,
            "minus_di": 15,

            "atr": 30,

            "market_cap": 1800000,
            "sector": "ENERGY",

            "relative_strength": 80,
            "sector_strength": 75,

            "high_3w": 1460,
            "high_1m": 1465,
            "high_2m": 1470,
            "high_3m": 1475,
            "high_52w": 1480,

            "low_3w": 1380,
            "low_1m": 1350,
            "low_2m": 1300,
            "low_3m": 1250,
            "low_52w": 1100,

            "previous_swing_low": 1400,
            "previous_swing_high": 1470,

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
        timeframe: str = "1d",
    ) -> None:

        super().__init__(
            name="Positional Scanner",
            version="2.0",
            timeframe=timeframe,
        )

        # -------------------------------------------------
        # GENERAL SETTINGS
        # -------------------------------------------------

        self.minimum_score = 68.0

        self.minimum_rr = 2.0

        self.max_signals = 20

        # -------------------------------------------------
        # UNIVERSE FILTERS
        # -------------------------------------------------

        self.minimum_price = 200.0

        self.minimum_market_cap = 1000.0

        self.minimum_volume_ratio = 1.10

        # -------------------------------------------------
        # TREND FILTERS
        # -------------------------------------------------

        self.minimum_adx = 18.0

        self.minimum_relative_strength = 50.0

        self.minimum_sector_strength = 40.0

        # -------------------------------------------------
        # ENTRY SETTINGS
        # -------------------------------------------------

        self.entry_buffer_percent = 0.10

        self.stop_atr_multiple = 2.0

        # -------------------------------------------------
        # TARGET SETTINGS
        # -------------------------------------------------

        self.target_rr_1 = 2.0

        self.target_rr_2 = 3.0

        self.target_rr_3 = 5.0

        # -------------------------------------------------
        # FILTER ENGINE
        # -------------------------------------------------

        self.filters: ScannerFilters = (
            create_scanner_filters(
                "positional"
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
        """
        Scan complete market universe.
        """

        generated: List[Signal] = []

        if not market_data:
            return generated

        for key, data in market_data.items():

            if not isinstance(data, dict):
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
                    "Positional scan error:",
                    key,
                    exc,
                )

        return generated

    # =====================================================
    # SCAN SYMBOL
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
        )

        if not symbol:
            return None

        # -------------------------------------------------
        # PRICE
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
        # MARKET CAP
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

        # -------------------------------------------------
        # EMA
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

        # -------------------------------------------------
        # MOMENTUM
        # -------------------------------------------------

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

        # -------------------------------------------------
        # MARKET DATA
        # -------------------------------------------------

        relative_strength = self._float(
            data.get(
                "relative_strength"
            )
        )

        sector_strength = self._float(
            data.get(
                "sector_strength"
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

        sector = str(
            data.get(
                "sector",
                "",
            )
        )

        # -------------------------------------------------
        # BASIC QUALITY
        # -------------------------------------------------

        if (
            adx > 0
            and adx < self.minimum_adx
        ):
            return None

        # -------------------------------------------------
        # GAP
        # -------------------------------------------------

        gap_percent = 0.0

        if previous_close > 0:

            gap_percent = (
                (
                    open_price
                    - previous_close
                )
                / previous_close
            ) * 100.0

        # -------------------------------------------------
        # DIRECTION SCORE
        # -------------------------------------------------

        bullish_score = (
            self._bullish_score(

                data=data,

                close=close,

                ema20=ema20,

                ema21=ema21,

                ema50=ema50,

                ema100=ema100,

                ema200=ema200,

                rsi=rsi,

                adx=adx,

                plus_di=plus_di,

                minus_di=minus_di,

                volume_ratio=volume_ratio,

                relative_strength=(
                    relative_strength
                ),

                sector_strength=(
                    sector_strength
                ),
            )
        )

        bearish_score = (
            self._bearish_score(

                data=data,

                close=close,

                ema20=ema20,

                ema21=ema21,

                ema50=ema50,

                ema100=ema100,

                ema200=ema200,

                rsi=rsi,

                adx=adx,

                plus_di=plus_di,

                minus_di=minus_di,

                volume_ratio=volume_ratio,

                relative_strength=(
                    relative_strength
                ),
            )
        )

        if (
            bullish_score < 45
            and bearish_score < 45
        ):
            return None

        if bullish_score >= bearish_score:

            signal_type = SignalType.BUY

            setup_score = bullish_score

        else:

            signal_type = SignalType.SELL

            setup_score = bearish_score

        # -------------------------------------------------
        # PATTERN
        # -------------------------------------------------

        pattern = self._detect_pattern(

            data=data,

            signal_type=signal_type,

            close=close,

            volume_ratio=volume_ratio,
        )

        # -------------------------------------------------
        # LEVELS
        # -------------------------------------------------

        levels = self._trade_levels(

            data=data,

            signal_type=signal_type,

            close=close,

            high=high,

            low=low,

            atr=atr,
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
        # SCORE BREAKDOWN
        # -------------------------------------------------

        score_breakdown = (
            self._score_breakdown(

                signal_type=signal_type,

                pattern=pattern,

                close=close,

                ema20=ema20,

                ema50=ema50,

                ema100=ema100,

                ema200=ema200,

                volume_ratio=volume_ratio,

                rsi=rsi,

                adx=adx,

                relative_strength=(
                    relative_strength
                ),

                sector_strength=(
                    sector_strength
                ),

                setup_score=setup_score,
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

            volume_ratio=volume_ratio,

            adx=adx,

            relative_strength=(
                relative_strength
            ),

            pattern=pattern,
        )

        # -------------------------------------------------
        # SIGNAL STRENGTH
        # -------------------------------------------------

        strength = self._strength(
            score
        )

        # -------------------------------------------------
        # MARKET TREND
        # -------------------------------------------------

        market_trend = (
            self._market_trend(
                data
            )
        )

        # -------------------------------------------------
        # CREATE SIGNAL
        # -------------------------------------------------

        signal = Signal(

            instrument_key=instrument_key,

            symbol=symbol,

            exchange=str(
                data.get(
                    "exchange",
                    "NSE",
                )
            ),

            signal_type=signal_type,

            pattern=pattern,

            strength=strength,

            scanner_name=self.name,

            scanner_version=self.version,

            strategy_name=(
                "StockVersity Positional"
            ),

            timeframe=self.timeframe,

            market_trend=market_trend,

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

            trigger_price=entry,

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

            confidence=confidence,

            score=score,

            score_breakdown=(
                score_breakdown
            ),

            remarks=(
                self._remarks(
                    signal_type,
                    pattern,
                    volume_ratio,
                    adx,
                    rsi,
                )
            ),

            tags=[

                "POSITIONAL",

                pattern.value,

                signal_type.value,
            ],

            metadata={

                "market_cap": (
                    market_cap
                ),

                "is_fno": bool(
                    data.get(
                        "is_fno",
                        False,
                    )
                ),

                "setup_score": (
                    setup_score
                ),

                "bullish_score": (
                    bullish_score
                ),

                "bearish_score": (
                    bearish_score
                ),

                "breakout_period": (
                    self._breakout_period(
                        data,
                        signal_type,
                        close,
                    )
                ),
            },
        )

        # -------------------------------------------------
        # CENTRAL FILTER ENGINE
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
    # BULLISH SCORE
    # =====================================================

    def _bullish_score(
        self,
        *,
        data: Dict[str, Any],
        close: float,
        ema20: float,
        ema21: float,
        ema50: float,
        ema100: float,
        ema200: float,
        rsi: float,
        adx: float,
        plus_di: float,
        minus_di: float,
        volume_ratio: float,
        relative_strength: float,
        sector_strength: float,
    ) -> float:

        score = 0.0

        # -------------------------------------------------
        # LONG-TERM TREND
        # -------------------------------------------------

        if (
            ema20 > 0
            and close > ema20
        ):
            score += 7

        if (
            ema50 > 0
            and close > ema50
        ):
            score += 10

        if (
            ema100 > 0
            and close > ema100
        ):
            score += 8

        if (
            ema200 > 0
            and close > ema200
        ):
            score += 12

        # -------------------------------------------------
        # EMA ALIGNMENT
        # -------------------------------------------------

        if (
            ema20 > 0
            and ema50 > 0
            and ema20 > ema50
        ):
            score += 7

        if (
            ema50 > 0
            and ema100 > 0
            and ema50 > ema100
        ):
            score += 6

        if (
            ema100 > 0
            and ema200 > 0
            and ema100 > ema200
        ):
            score += 5

        # -------------------------------------------------
        # MOMENTUM
        # -------------------------------------------------

        if 55 <= rsi <= 72:

            score += 8

        elif rsi > 50:

            score += 4

        if adx >= 30:

            score += 8

        elif adx >= 20:

            score += 5

        if plus_di > minus_di:

            score += 5

        # -------------------------------------------------
        # VOLUME
        # -------------------------------------------------

        if volume_ratio >= 2.0:

            score += 8

        elif volume_ratio >= 1.5:

            score += 6

        elif volume_ratio >= 1.1:

            score += 3

        # -------------------------------------------------
        # RELATIVE STRENGTH
        # -------------------------------------------------

        if relative_strength >= 80:

            score += 8

        elif relative_strength >= 60:

            score += 5

        elif relative_strength >= 50:

            score += 3

        # -------------------------------------------------
        # SECTOR
        # -------------------------------------------------

        if sector_strength >= 70:

            score += 5

        elif sector_strength >= 50:

            score += 3

        # -------------------------------------------------
        # BREAKOUT BONUS
        # -------------------------------------------------

        breakout = self._breakout_period(
            data,
            SignalType.BUY,
            close,
        )

        breakout_bonus = {

            "YEARLY": 12,

            "3_MONTH": 10,

            "2_MONTH": 8,

            "MONTHLY": 7,

            "3_WEEK": 5,
        }

        score += breakout_bonus.get(
            breakout,
            0,
        )

        return min(
            score,
            100.0,
        )

    # =====================================================
    # BEARISH SCORE
    # =====================================================

    def _bearish_score(
        self,
        *,
        data: Dict[str, Any],
        close: float,
        ema20: float,
        ema21: float,
        ema50: float,
        ema100: float,
        ema200: float,
        rsi: float,
        adx: float,
        plus_di: float,
        minus_di: float,
        volume_ratio: float,
        relative_strength: float,
    ) -> float:

        score = 0.0

        if (
            ema20 > 0
            and close < ema20
        ):
            score += 7

        if (
            ema50 > 0
            and close < ema50
        ):
            score += 10

        if (
            ema100 > 0
            and close < ema100
        ):
            score += 8

        if (
            ema200 > 0
            and close < ema200
        ):
            score += 12

        if (
            ema20 > 0
            and ema50 > 0
            and ema20 < ema50
        ):
            score += 7

        if (
            ema50 > 0
            and ema100 > 0
            and ema50 < ema100
        ):
            score += 6

        if (
            ema100 > 0
            and ema200 > 0
            and ema100 < ema200
        ):
            score += 5

        if 28 <= rsi <= 45:

            score += 8

        elif (
            rsi > 0
            and rsi < 50
        ):

            score += 4

        if adx >= 30:

            score += 8

        elif adx >= 20:

            score += 5

        if minus_di > plus_di:

            score += 5

        if volume_ratio >= 2.0:

            score += 8

        elif volume_ratio >= 1.5:

            score += 6

        elif volume_ratio >= 1.1:

            score += 3

        breakout = self._breakout_period(
            data,
            SignalType.SELL,
            close,
        )

        breakout_bonus = {

            "YEARLY": 12,

            "3_MONTH": 10,

            "2_MONTH": 8,

            "MONTHLY": 7,

            "3_WEEK": 5,
        }

        score += breakout_bonus.get(
            breakout,
            0,
        )

        return min(
            score,
            100.0,
        )

    # =====================================================
    # BREAKOUT PERIOD
    # =====================================================

    def _breakout_period(
        self,
        data: Dict[str, Any],
        signal_type: SignalType,
        close: float,
    ) -> str:
        """
        Determine strongest positional breakout.
        """

        if signal_type == SignalType.BUY:

            levels = [

                (
                    "YEARLY",
                    self._float(
                        data.get(
                            "high_52w"
                        )
                    ),
                ),

                (
                    "3_MONTH",
                    self._float(
                        data.get(
                            "high_3m"
                        )
                    ),
                ),

                (
                    "2_MONTH",
                    self._float(
                        data.get(
                            "high_2m"
                        )
                    ),
                ),

                (
                    "MONTHLY",
                    self._float(
                        data.get(
                            "high_1m"
                        )
                    ),
                ),

                (
                    "3_WEEK",
                    self._float(
                        data.get(
                            "high_3w"
                        )
                    ),
                ),
            ]

            for name, level in levels:

                if (
                    level > 0
                    and close >= level
                ):

                    return name

        else:

            levels = [

                (
                    "YEARLY",
                    self._float(
                        data.get(
                            "low_52w"
                        )
                    ),
                ),

                (
                    "3_MONTH",
                    self._float(
                        data.get(
                            "low_3m"
                        )
                    ),
                ),

                (
                    "2_MONTH",
                    self._float(
                        data.get(
                            "low_2m"
                        )
                    ),
                ),

                (
                    "MONTHLY",
                    self._float(
                        data.get(
                            "low_1m"
                        )
                    ),
                ),

                (
                    "3_WEEK",
                    self._float(
                        data.get(
                            "low_3w"
                        )
                    ),
                ),
            ]

            for name, level in levels:

                if (
                    level > 0
                    and close <= level
                ):

                    return name

        return ""

    # =====================================================
    # PATTERN DETECTION
    # =====================================================

    def _detect_pattern(
        self,
        *,
        data: Dict[str, Any],
        signal_type: SignalType,
        close: float,
        volume_ratio: float,
    ) -> PatternType:

        # -------------------------------------------------
        # EXPLICIT PATTERNS
        # -------------------------------------------------

        if (
            signal_type == SignalType.BUY
            and bool(
                data.get(
                    "vcp",
                    False,
                )
            )
        ):

            return PatternType.VCP

        if (
            signal_type == SignalType.BUY
            and bool(
                data.get(
                    "cup_handle",
                    False,
                )
            )
        ):

            return PatternType.CUP_HANDLE

        if (
            signal_type == SignalType.BUY
            and bool(
                data.get(
                    "bull_flag",
                    False,
                )
            )
        ):

            return PatternType.BULL_FLAG

        if (
            signal_type == SignalType.SELL
            and bool(
                data.get(
                    "bear_flag",
                    False,
                )
            )
        ):

            return PatternType.BEAR_FLAG

        if (
            signal_type == SignalType.BUY
            and bool(
                data.get(
                    "falling_wedge",
                    False,
                )
            )
        ):

            return PatternType.FALLING_WEDGE

        if (
            signal_type == SignalType.SELL
            and bool(
                data.get(
                    "rising_wedge",
                    False,
                )
            )
        ):

            return PatternType.RISING_WEDGE

        # -------------------------------------------------
        # POSITIONAL BREAKOUT
        # -------------------------------------------------

        breakout_period = (
            self._breakout_period(
                data,
                signal_type,
                close,
            )
        )

        if breakout_period:

            if (
                signal_type
                == SignalType.BUY
            ):

                return (
                    PatternType.BREAKOUT
                )

            return (
                PatternType.BREAKDOWN
            )

        return PatternType.MOMENTUM

    # =====================================================
    # TRADE LEVELS
    # =====================================================

    def _trade_levels(
        self,
        *,
        data: Dict[str, Any],
        signal_type: SignalType,
        close: float,
        high: float,
        low: float,
        atr: float,
    ) -> Optional[
        tuple[
            float,
            float,
            float,
            float,
            float,
        ]
    ]:

        swing_low = self._float(
            data.get(
                "previous_swing_low"
            )
        )

        swing_high = self._float(
            data.get(
                "previous_swing_high"
            )
        )

        # ATR fallback

        if atr <= 0:

            if (
                high > 0
                and low > 0
                and high > low
            ):

                atr = (
                    high - low
                )

            else:

                atr = (
                    close * 0.02
                )

        buffer = (

            close
            * self.entry_buffer_percent
            / 100.0
        )

        # -------------------------------------------------
        # BUY
        # -------------------------------------------------

        if signal_type == SignalType.BUY:

            breakout_level = (
                self._highest_breakout_level(
                    data
                )
            )

            entry = max(
                close,
                breakout_level,
            ) + buffer

            atr_stop = (

                entry

                - (
                    atr
                    * self.stop_atr_multiple
                )
            )

            if swing_low > 0:

                stop_loss = max(
                    atr_stop,
                    swing_low,
                )

            else:

                stop_loss = atr_stop

            if stop_loss >= entry:

                stop_loss = (
                    entry
                    - atr
                )

            risk = (
                entry
                - stop_loss
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

            breakdown_level = (
                self._lowest_breakdown_level(
                    data
                )
            )

            if breakdown_level > 0:

                entry = min(
                    close,
                    breakdown_level,
                ) - buffer

            else:

                entry = (
                    close
                    - buffer
                )

            atr_stop = (

                entry

                + (
                    atr
                    * self.stop_atr_multiple
                )
            )

            if swing_high > 0:

                stop_loss = min(
                    atr_stop,
                    swing_high,
                )

            else:

                stop_loss = atr_stop

            if stop_loss <= entry:

                stop_loss = (
                    entry
                    + atr
                )

            risk = (
                stop_loss
                - entry
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
    # HIGHEST BREAKOUT LEVEL
    # =====================================================

    def _highest_breakout_level(
        self,
        data: Dict[str, Any],
    ) -> float:

        levels = [

            self._float(
                data.get(
                    "high_3w"
                )
            ),

            self._float(
                data.get(
                    "high_1m"
                )
            ),

            self._float(
                data.get(
                    "high_2m"
                )
            ),

            self._float(
                data.get(
                    "high_3m"
                )
            ),

            self._float(
                data.get(
                    "high_52w"
                )
            ),
        ]

        valid = [

            level

            for level in levels

            if level > 0
        ]

        if not valid:
            return 0.0

        return max(valid)

    # =====================================================
    # LOWEST BREAKDOWN LEVEL
    # =====================================================

    def _lowest_breakdown_level(
        self,
        data: Dict[str, Any],
    ) -> float:

        levels = [

            self._float(
                data.get(
                    "low_3w"
                )
            ),

            self._float(
                data.get(
                    "low_1m"
                )
            ),

            self._float(
                data.get(
                    "low_2m"
                )
            ),

            self._float(
                data.get(
                    "low_3m"
                )
            ),

            self._float(
                data.get(
                    "low_52w"
                )
            ),
        ]

        valid = [

            level

            for level in levels

            if level > 0
        ]

        if not valid:
            return 0.0

        return min(valid)

    # =====================================================
    # SCORE BREAKDOWN
    # =====================================================

    def _score_breakdown(
        self,
        *,
        signal_type: SignalType,
        pattern: PatternType,
        close: float,
        ema20: float,
        ema50: float,
        ema100: float,
        ema200: float,
        volume_ratio: float,
        rsi: float,
        adx: float,
        relative_strength: float,
        sector_strength: float,
        setup_score: float,
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
        # TREND MAX 25
        # -------------------------------------------------

        if signal_type == SignalType.BUY:

            if (
                ema50 > 0
                and close > ema50
            ):
                scores["trend"] += 5

            if (
                ema100 > 0
                and close > ema100
            ):
                scores["trend"] += 5

            if (
                ema200 > 0
                and close > ema200
            ):
                scores["trend"] += 7

            if (
                ema50 > 0
                and ema100 > 0
                and ema50 > ema100
            ):
                scores["trend"] += 4

            if (
                ema100 > 0
                and ema200 > 0
                and ema100 > ema200
            ):
                scores["trend"] += 4

        else:

            if (
                ema50 > 0
                and close < ema50
            ):
                scores["trend"] += 5

            if (
                ema100 > 0
                and close < ema100
            ):
                scores["trend"] += 5

            if (
                ema200 > 0
                and close < ema200
            ):
                scores["trend"] += 7

            if (
                ema50 > 0
                and ema100 > 0
                and ema50 < ema100
            ):
                scores["trend"] += 4

            if (
                ema100 > 0
                and ema200 > 0
                and ema100 < ema200
            ):
                scores["trend"] += 4

        # -------------------------------------------------
        # VOLUME MAX 15
        # -------------------------------------------------

        if volume_ratio >= 2.5:

            scores["volume"] = 15

        elif volume_ratio >= 2.0:

            scores["volume"] = 13

        elif volume_ratio >= 1.5:

            scores["volume"] = 10

        elif volume_ratio >= 1.1:

            scores["volume"] = 6

        # -------------------------------------------------
        # MOMENTUM MAX 15
        # -------------------------------------------------

        if adx >= 30:

            scores["momentum"] += 8

        elif adx >= 25:

            scores["momentum"] += 6

        elif adx >= 18:

            scores["momentum"] += 4

        if signal_type == SignalType.BUY:

            if 55 <= rsi <= 70:

                scores[
                    "momentum"
                ] += 7

            elif rsi > 50:

                scores[
                    "momentum"
                ] += 4

        else:

            if 30 <= rsi <= 45:

                scores[
                    "momentum"
                ] += 7

            elif (
                rsi > 0
                and rsi < 50
            ):

                scores[
                    "momentum"
                ] += 4

        # -------------------------------------------------
        # PATTERN MAX 20
        # -------------------------------------------------

        pattern_scores = {

            PatternType.VCP: 20,

            PatternType.CUP_HANDLE: 20,

            PatternType.BREAKOUT: 20,

            PatternType.BREAKDOWN: 20,

            PatternType.BULL_FLAG: 17,

            PatternType.BEAR_FLAG: 17,

            PatternType.FALLING_WEDGE: 16,

            PatternType.RISING_WEDGE: 16,

            PatternType.MOMENTUM: 10,
        }

        scores["pattern"] = (
            pattern_scores.get(
                pattern,
                8,
            )
        )

        # -------------------------------------------------
        # SECTOR MAX 10
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
        # RELATIVE STRENGTH MAX 10
        # -------------------------------------------------

        if relative_strength >= 80:

            scores[
                "relative_strength"
            ] = 10

        elif relative_strength >= 70:

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
        # MARKET / SETUP MAX 5
        # -------------------------------------------------

        if setup_score >= 85:

            scores["market"] = 5

        elif setup_score >= 70:

            scores["market"] = 4

        elif setup_score >= 55:

            scores["market"] = 3

        return scores

    # =====================================================
    # CONFIDENCE
    # =====================================================

    @staticmethod
    def _confidence(
        *,
        score: float,
        volume_ratio: float,
        adx: float,
        relative_strength: float,
        pattern: PatternType,
    ) -> float:

        confidence = (
            score * 0.65
        )

        if volume_ratio >= 2.0:
            confidence += 8

        elif volume_ratio >= 1.5:
            confidence += 5

        if adx >= 30:
            confidence += 8

        elif adx >= 25:
            confidence += 5

        if relative_strength >= 80:
            confidence += 8

        elif relative_strength >= 60:
            confidence += 5

        premium_patterns = {

            PatternType.VCP,

            PatternType.CUP_HANDLE,

            PatternType.BREAKOUT,

            PatternType.BREAKDOWN,
        }

        if pattern in premium_patterns:

            confidence += 8

        return round(

            min(
                confidence,
                100.0,
            ),

            2,
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
    # REMARKS
    # =====================================================

    @staticmethod
    def _remarks(
        signal_type: SignalType,
        pattern: PatternType,
        volume_ratio: float,
        adx: float,
        rsi: float,
    ) -> str:

        return (

            f"{signal_type.value} positional setup | "

            f"{pattern.value} | "

            f"RVOL {volume_ratio:.2f}x | "

            f"ADX {adx:.1f} | "

            f"RSI {rsi:.1f}"
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

def create_positional_scanner(
    timeframe: str = "1d",
) -> PositionalScanner:
    """
    Create configured positional scanner.
    """

    return PositionalScanner(
        timeframe=timeframe
    )


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "PositionalScanner",

    "create_positional_scanner",

]


# ==========================
# END OF FILE
# ==========================