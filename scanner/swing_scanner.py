"""
=========================================================
StockVersity Scanner Pro
Swing Scanner
Version : 2.0
=========================================================

Professional swing-trading scanner.

Designed for:
• 1H / 2H / 4H / Daily swing setups
• Trend continuation
• Breakouts
• EMA pullbacks
• Momentum expansion
• Volume confirmation
• Relative strength
• VCP-style contraction
• Risk / reward filtering

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
from typing import Sequence

from core.scanner.base_scanner import BaseScanner

from core.scanner.signal import Signal
from core.scanner.signal import SignalType
from core.scanner.signal import SignalStrength
from core.scanner.signal import PatternType
from core.scanner.signal import MarketTrend

from core.scanner.filters import ScannerFilters
from core.scanner.filters import create_scanner_filters


# =========================================================
# SWING SCANNER
# =========================================================

class SwingScanner(BaseScanner):
    """
    StockVersity professional swing scanner.

    Expected market_data structure
    ------------------------------

    {
        "RELIANCE": {
            "instrument_key": "...",
            "symbol": "RELIANCE",
            "exchange": "NSE",

            "open": 1450,
            "high": 1480,
            "low": 1440,
            "close": 1475,
            "previous_close": 1445,

            "volume": 5000000,
            "average_volume": 2500000,

            "ema9": 1460,
            "ema20": 1445,
            "ema21": 1440,
            "ema50": 1400,
            "ema100": 1350,
            "ema200": 1250,

            "rsi": 65,
            "adx": 28,

            "plus_di": 30,
            "minus_di": 15,

            "atr": 25,

            "market_cap": 1800000,
            "sector": "ENERGY",

            "relative_strength": 75,
            "sector_strength": 70,

            "previous_high": 1465,
            "previous_low": 1420,

            "high_20": 1465,
            "low_20": 1350,

            "high_50": 1480,

            "beta": 1.1,

            "is_fno": True
        }
    }
    """

    # =====================================================
    # INIT
    # =====================================================

    def __init__(
        self,
        timeframe: str = "1h",
    ) -> None:

        super().__init__(
            name="Swing Scanner",
            version="2.0",
            timeframe=timeframe,
        )

        # -------------------------------------------------
        # BASE SCANNER SETTINGS
        # -------------------------------------------------

        self.minimum_score = 65.0

        self.minimum_rr = 2.0

        self.max_signals = 25

        # -------------------------------------------------
        # SWING SETTINGS
        # -------------------------------------------------

        self.minimum_price = 200.0

        self.minimum_market_cap = 1000.0

        self.minimum_rvol = 1.20

        self.minimum_adx = 18.0

        self.minimum_rsi = 50.0

        self.maximum_rsi = 78.0

        self.minimum_relative_strength = 50.0

        self.minimum_sector_strength = 40.0

        self.breakout_buffer_percent = 0.10

        self.stop_atr_multiple = 1.5

        self.target_rr_1 = 2.0

        self.target_rr_2 = 3.0

        self.target_rr_3 = 4.0

        # -------------------------------------------------
        # FILTER ENGINE
        # -------------------------------------------------

        self.filters: ScannerFilters = (
            create_scanner_filters(
                "swing"
            )
        )

        # Swing-specific overrides.

        self.filters.configure(

            minimum_price=self.minimum_price,

            minimum_market_cap=(
                self.minimum_market_cap
            ),

            minimum_volume_ratio=(
                self.minimum_rvol
            ),

            minimum_adx=(
                self.minimum_adx
            ),

            minimum_score=(
                self.minimum_score
            ),

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
        Scan complete market data universe.
        """

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

                if signal is None:
                    continue

                generated.append(
                    signal
                )

            except Exception as exc:

                self.log(
                    "Swing scan error:",
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
        ).upper()

        instrument_key = str(
            data.get(
                "instrument_key",
                key,
            )
        )

        # -------------------------------------------------
        # PRICES
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
        # HARD UNIVERSE FILTER
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

        beta = self._float(
            data.get("beta")
        )

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

        sector = str(
            data.get(
                "sector",
                "",
            )
        )

        # -------------------------------------------------
        # BASIC QUALITY
        # -------------------------------------------------

        if adx < self.minimum_adx:
            return None

        if (
            rsi > 0
            and (
                rsi < self.minimum_rsi
                or rsi > self.maximum_rsi
            )
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
        # DETECT DIRECTION
        # -------------------------------------------------

        bullish_score = (
            self._bullish_setup_score(
                data=data,
                close=close,
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
            self._bearish_setup_score(
                data=data,
                close=close,
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
                volume_ratio=volume_ratio,
                relative_strength=(
                    relative_strength
                ),
            )
        )

        # -------------------------------------------------
        # NO SETUP
        # -------------------------------------------------

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
            ema20=ema20,
            ema21=ema21,
            ema50=ema50,
            volume_ratio=volume_ratio,
        )

        # -------------------------------------------------
        # ENTRY / STOP / TARGETS
        # -------------------------------------------------

        levels = self._calculate_trade_levels(

            signal_type=signal_type,

            data=data,

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
        # SCORE
        # -------------------------------------------------

        score_breakdown = (
            self._score_breakdown(
                signal_type=signal_type,
                pattern=pattern,
                close=close,
                ema20=ema20,
                ema21=ema21,
                ema50=ema50,
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

        confidence = (
            self._confidence(
                score=score,
                volume_ratio=volume_ratio,
                adx=adx,
                relative_strength=(
                    relative_strength
                ),
                pattern=pattern,
            )
        )

        strength = (
            self._strength(
                score
            )
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
                "StockVersity Swing"
            ),

            timeframe=self.timeframe,

            market_trend=market_trend,

            sector=sector,

            sector_strength=(
                sector_strength
            ),

            market_strength=self._float(
                data.get(
                    "market_strength"
                )
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
                self._build_remarks(
                    signal_type=(
                        signal_type
                    ),
                    pattern=pattern,
                    volume_ratio=(
                        volume_ratio
                    ),
                    adx=adx,
                    rsi=rsi,
                )
            ),

            tags=[
                "SWING",
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

                "turnover": self._float(
                    data.get(
                        "turnover"
                    )
                ),

                "spread_percent": (
                    self._float(
                        data.get(
                            "spread_percent"
                        )
                    )
                ),

            },
        )

        # -------------------------------------------------
        # CENTRAL FILTERS
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

    def _bullish_setup_score(
        self,
        *,
        data: Dict[str, Any],
        close: float,
        ema9: float,
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
        # EMA TREND
        # -------------------------------------------------

        if (
            ema20 > 0
            and close > ema20
        ):
            score += 10

        if (
            ema21 > 0
            and close > ema21
        ):
            score += 5

        if (
            ema50 > 0
            and close > ema50
        ):
            score += 10

        if (
            ema200 > 0
            and close > ema200
        ):
            score += 10

        if (
            ema20 > 0
            and ema50 > 0
            and ema20 > ema50
        ):
            score += 8

        if (
            ema50 > 0
            and ema200 > 0
            and ema50 > ema200
        ):
            score += 7

        # -------------------------------------------------
        # MOMENTUM
        # -------------------------------------------------

        if 55 <= rsi <= 75:
            score += 10

        elif rsi > 50:
            score += 5

        if adx >= 25:
            score += 8

        elif adx >= 18:
            score += 4

        if plus_di > minus_di:
            score += 5

        # -------------------------------------------------
        # VOLUME
        # -------------------------------------------------

        if volume_ratio >= 2.0:
            score += 10

        elif volume_ratio >= 1.5:
            score += 7

        elif volume_ratio >= 1.2:
            score += 4

        # -------------------------------------------------
        # RELATIVE STRENGTH
        # -------------------------------------------------

        if relative_strength >= 70:
            score += 7

        elif relative_strength >= 50:
            score += 4

        # -------------------------------------------------
        # SECTOR
        # -------------------------------------------------

        if sector_strength >= 70:
            score += 5

        elif sector_strength >= 50:
            score += 3

        # -------------------------------------------------
        # BREAKOUT
        # -------------------------------------------------

        high_20 = self._float(
            data.get(
                "high_20"
            )
        )

        if (
            high_20 > 0
            and close >= high_20
        ):
            score += 10

        return min(
            score,
            100.0,
        )

    # =====================================================
    # BEARISH SCORE
    # =====================================================

    def _bearish_setup_score(
        self,
        *,
        data: Dict[str, Any],
        close: float,
        ema9: float,
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
            score += 10

        if (
            ema21 > 0
            and close < ema21
        ):
            score += 5

        if (
            ema50 > 0
            and close < ema50
        ):
            score += 10

        if (
            ema200 > 0
            and close < ema200
        ):
            score += 10

        if (
            ema20 > 0
            and ema50 > 0
            and ema20 < ema50
        ):
            score += 8

        if (
            ema50 > 0
            and ema200 > 0
            and ema50 < ema200
        ):
            score += 7

        if 25 <= rsi <= 45:
            score += 10

        elif (
            rsi > 0
            and rsi < 50
        ):
            score += 5

        if adx >= 25:
            score += 8

        elif adx >= 18:
            score += 4

        if minus_di > plus_di:
            score += 5

        if volume_ratio >= 2.0:
            score += 10

        elif volume_ratio >= 1.5:
            score += 7

        elif volume_ratio >= 1.2:
            score += 4

        low_20 = self._float(
            data.get(
                "low_20"
            )
        )

        if (
            low_20 > 0
            and close <= low_20
        ):
            score += 10

        return min(
            score,
            100.0,
        )

    # =====================================================
    # PATTERN DETECTION
    # =====================================================

    def _detect_pattern(
        self,
        *,
        data: Dict[str, Any],
        signal_type: SignalType,
        close: float,
        ema20: float,
        ema21: float,
        ema50: float,
        volume_ratio: float,
    ) -> PatternType:

        high_20 = self._float(
            data.get(
                "high_20"
            )
        )

        low_20 = self._float(
            data.get(
                "low_20"
            )
        )

        contraction = bool(
            data.get(
                "volatility_contraction",
                False,
            )
        )

        bull_flag = bool(
            data.get(
                "bull_flag",
                False,
            )
        )

        bear_flag = bool(
            data.get(
                "bear_flag",
                False,
            )
        )

        falling_wedge = bool(
            data.get(
                "falling_wedge",
                False,
            )
        )

        rising_wedge = bool(
            data.get(
                "rising_wedge",
                False,
            )
        )

        cup_handle = bool(
            data.get(
                "cup_handle",
                False,
            )
        )

        # VCP

        if (
            contraction
            and signal_type
            == SignalType.BUY
        ):
            return PatternType.VCP

        # Cup & Handle

        if (
            cup_handle
            and signal_type
            == SignalType.BUY
        ):
            return PatternType.CUP_HANDLE

        # Bull Flag

        if (
            bull_flag
            and signal_type
            == SignalType.BUY
        ):
            return PatternType.BULL_FLAG

        # Bear Flag

        if (
            bear_flag
            and signal_type
            == SignalType.SELL
        ):
            return PatternType.BEAR_FLAG

        # Falling Wedge

        if (
            falling_wedge
            and signal_type
            == SignalType.BUY
        ):
            return PatternType.FALLING_WEDGE

        # Rising Wedge

        if (
            rising_wedge
            and signal_type
            == SignalType.SELL
        ):
            return PatternType.RISING_WEDGE

        # Breakout

        if (
            signal_type == SignalType.BUY
            and high_20 > 0
            and close >= high_20
            and volume_ratio >= 1.20
        ):
            return PatternType.BREAKOUT

        # Breakdown

        if (
            signal_type == SignalType.SELL
            and low_20 > 0
            and close <= low_20
            and volume_ratio >= 1.20
        ):
            return PatternType.BREAKDOWN

        # EMA continuation

        reference_ema = (
            ema20
            or ema21
            or ema50
        )

        if reference_ema > 0:

            distance = abs(
                close
                - reference_ema
            )

            distance_percent = (
                distance
                / reference_ema
            ) * 100

            if distance_percent <= 2.0:

                return (
                    PatternType.EMA_CROSS
                )

        return PatternType.MOMENTUM

    # =====================================================
    # TRADE LEVELS
    # =====================================================

    def _calculate_trade_levels(
        self,
        *,
        signal_type: SignalType,
        data: Dict[str, Any],
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

        previous_high = self._float(
            data.get(
                "previous_high"
            )
        )

        previous_low = self._float(
            data.get(
                "previous_low"
            )
        )

        # ATR fallback.

        if atr <= 0:

            candle_range = (
                high - low
            )

            if candle_range > 0:

                atr = candle_range

            else:

                atr = (
                    close * 0.015
                )

        buffer = (

            close
            * self.breakout_buffer_percent
            / 100.0

        )

        # -------------------------------------------------
        # BUY
        # -------------------------------------------------

        if signal_type == SignalType.BUY:

            entry = max(
                close,
                previous_high,
            ) + buffer

            atr_stop = (
                entry
                - (
                    atr
                    * self.stop_atr_multiple
                )
            )

            structural_stop = (
                previous_low
                if previous_low > 0
                else low
            )

            if structural_stop > 0:

                stop_loss = max(
                    atr_stop,
                    structural_stop,
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
                + (
                    risk
                    * self.target_rr_1
                )
            )

            target2 = (
                entry
                + (
                    risk
                    * self.target_rr_2
                )
            )

            target3 = (
                entry
                + (
                    risk
                    * self.target_rr_3
                )
            )

        # -------------------------------------------------
        # SELL
        # -------------------------------------------------

        else:

            candidate_low = (
                previous_low
                if previous_low > 0
                else close
            )

            entry = min(
                close,
                candidate_low,
            ) - buffer

            atr_stop = (
                entry
                + (
                    atr
                    * self.stop_atr_multiple
                )
            )

            structural_stop = (
                previous_high
                if previous_high > 0
                else high
            )

            if structural_stop > 0:

                stop_loss = min(
                    atr_stop,
                    structural_stop,
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
                - (
                    risk
                    * self.target_rr_1
                )
            )

            target2 = (
                entry
                - (
                    risk
                    * self.target_rr_2
                )
            )

            target3 = (
                entry
                - (
                    risk
                    * self.target_rr_3
                )
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
        pattern: PatternType,
        close: float,
        ema20: float,
        ema21: float,
        ema50: float,
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
        # TREND : MAX 20
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
                scores["trend"] += 5

            if (
                ema200 > 0
                and close > ema200
            ):
                scores["trend"] += 5

            if (
                ema20 > 0
                and ema50 > 0
                and ema20 > ema50
            ):
                scores["trend"] += 5

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
                scores["trend"] += 5

            if (
                ema200 > 0
                and close < ema200
            ):
                scores["trend"] += 5

            if (
                ema20 > 0
                and ema50 > 0
                and ema20 < ema50
            ):
                scores["trend"] += 5

        # -------------------------------------------------
        # VOLUME : MAX 15
        # -------------------------------------------------

        if volume_ratio >= 2.5:

            scores["volume"] = 15

        elif volume_ratio >= 2.0:

            scores["volume"] = 13

        elif volume_ratio >= 1.5:

            scores["volume"] = 10

        elif volume_ratio >= 1.2:

            scores["volume"] = 7

        # -------------------------------------------------
        # MOMENTUM : MAX 20
        # -------------------------------------------------

        if adx >= 30:

            scores["momentum"] += 10

        elif adx >= 25:

            scores["momentum"] += 8

        elif adx >= 18:

            scores["momentum"] += 5

        if signal_type == SignalType.BUY:

            if 55 <= rsi <= 70:

                scores[
                    "momentum"
                ] += 10

            elif 50 <= rsi <= 75:

                scores[
                    "momentum"
                ] += 7

        else:

            if 30 <= rsi <= 45:

                scores[
                    "momentum"
                ] += 10

            elif 25 <= rsi < 50:

                scores[
                    "momentum"
                ] += 7

        # -------------------------------------------------
        # PATTERN : MAX 20
        # -------------------------------------------------

        pattern_scores = {

            PatternType.VCP: 20,

            PatternType.CUP_HANDLE: 20,

            PatternType.BULL_FLAG: 18,

            PatternType.BEAR_FLAG: 18,

            PatternType.FALLING_WEDGE: 17,

            PatternType.RISING_WEDGE: 17,

            PatternType.BREAKOUT: 18,

            PatternType.BREAKDOWN: 18,

            PatternType.EMA_CROSS: 12,

            PatternType.MOMENTUM: 10,
        }

        scores["pattern"] = (
            pattern_scores.get(
                pattern,
                8,
            )
        )

        # -------------------------------------------------
        # SECTOR : MAX 10
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
        # RELATIVE STRENGTH : MAX 10
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
        # MARKET : MAX 5
        # -------------------------------------------------

        if setup_score >= 80:

            scores["market"] = 5

        elif setup_score >= 65:

            scores["market"] = 4

        elif setup_score >= 50:

            scores["market"] = 3

        return scores

    # =====================================================
    # CONFIDENCE
    # =====================================================

    def _confidence(
        self,
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

        if relative_strength >= 70:

            confidence += 6

        premium_patterns = {

            PatternType.VCP,

            PatternType.CUP_HANDLE,

            PatternType.BULL_FLAG,

            PatternType.BEAR_FLAG,

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
    # SIGNAL STRENGTH
    # =====================================================

    @staticmethod
    def _strength(
        score: float,
    ) -> SignalStrength:

        if score >= 90:

            return (
                SignalStrength
                .VERY_STRONG
            )

        if score >= 80:

            return (
                SignalStrength
                .STRONG
            )

        if score >= 70:

            return (
                SignalStrength
                .MODERATE
            )

        if score >= 60:

            return (
                SignalStrength
                .WEAK
            )

        return (
            SignalStrength
            .VERY_WEAK
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
    def _build_remarks(
        *,
        signal_type: SignalType,
        pattern: PatternType,
        volume_ratio: float,
        adx: float,
        rsi: float,
    ) -> str:

        return (

            f"{signal_type.value} swing setup | "

            f"{pattern.value} | "

            f"RVOL {volume_ratio:.2f}x | "

            f"ADX {adx:.1f} | "

            f"RSI {rsi:.1f}"

        )

    # =====================================================
    # HELPERS
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

def create_swing_scanner(
    timeframe: str = "1h",
) -> SwingScanner:
    """
    Create configured swing scanner.
    """

    return SwingScanner(
        timeframe=timeframe
    )


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "SwingScanner",

    "create_swing_scanner",

]


# ==========================
# END OF FILE
# ==========================