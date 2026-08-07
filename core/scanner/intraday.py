"""
=========================================================
StockVersity Scanner Pro
Intraday Scanner
Version : 2.0
=========================================================

Main intraday opportunity scanner.

Designed for:
    • NSE intraday stocks
    • BUY and SELL opportunities
    • 1m / 3m / 5m / 15m / 30m / 45m
    • Momentum + trend confirmation
    • VWAP confirmation
    • EMA structure
    • RSI / MACD / ADX
    • Supertrend
    • Relative volume
    • ATR-based risk management
    • Market trend confirmation
    • Sector strength confirmation

The scanner receives pre-calculated market data and produces
Signal objects compatible with BaseScanner and ScannerEngine.
"""

from __future__ import annotations

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from core.scanner.base_scanner import BaseScanner

from core.scanner.signal import MarketTrend
from core.scanner.signal import PatternType
from core.scanner.signal import Signal
from core.scanner.signal import SignalStrength
from core.scanner.signal import SignalType


# =========================================================
# CONSTANTS
# =========================================================

SUPPORTED_TIMEFRAMES = {
    "1m",
    "3m",
    "5m",
    "15m",
    "30m",
    "45m",
}

DEFAULT_MINIMUM_PRICE = 200.0

DEFAULT_MINIMUM_MARKET_CAP = 1000.0

DEFAULT_MAXIMUM_GAP_PERCENT = 3.0

DEFAULT_MINIMUM_ADX = 20.0

DEFAULT_MINIMUM_VOLUME_RATIO = 1.20

DEFAULT_BREAKOUT_VOLUME_RATIO = 1.50

DEFAULT_MINIMUM_RR = 2.0

DEFAULT_MINIMUM_SCORE = 60.0

DEFAULT_MINIMUM_CONFIDENCE = 60.0

DEFAULT_ATR_STOP_MULTIPLE = 1.50

DEFAULT_TARGET_RR = 2.0


# =========================================================
# INTRADAY SCANNER
# =========================================================

class IntradayScanner(BaseScanner):
    """
    StockVersity general intraday opportunity scanner.

    This scanner searches for high-quality BUY and SELL
    opportunities using multiple confirmations.

    Expected market_data format
    ---------------------------

    {
        "RELIANCE": {
            "instrument_key": "NSE_EQ|INE002A01018",
            "symbol": "RELIANCE",

            "last_price": 3000.0,
            "open": 2975.0,
            "high": 3010.0,
            "low": 2965.0,
            "close": 3000.0,
            "previous_close": 2970.0,

            "volume": 1500000,
            "average_volume": 900000,
            "volume_ratio": 1.67,

            "market_cap": 2000000,
            "sector": "ENERGY",
            "sector_strength": 75.0,

            "ema9": 2995.0,
            "ema20": 2988.0,
            "ema21": 2987.0,
            "ema50": 2970.0,
            "ema200": 2900.0,

            "rsi": 64.0,

            "macd": 8.0,
            "macd_signal": 5.0,
            "macd_histogram": 3.0,

            "adx": 28.0,
            "plus_di": 31.0,
            "minus_di": 17.0,

            "vwap": 2985.0,

            "supertrend": 2970.0,
            "supertrend_direction": 1,

            "atr": 20.0,

            "relative_strength": 70.0,
            "beta": 1.1,

            "market_trend": "BULLISH"
        }
    }
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        timeframe: str = "5m",
    ) -> None:

        if timeframe not in SUPPORTED_TIMEFRAMES:

            raise ValueError(
                f"Unsupported intraday timeframe: {timeframe}. "
                f"Supported: {sorted(SUPPORTED_TIMEFRAMES)}"
            )

        super().__init__(
            name="Intraday Scanner",
            version="2.0",
            timeframe=timeframe,
        )

        # -------------------------------------------------
        # Scanner thresholds
        # -------------------------------------------------

        self.minimum_price = DEFAULT_MINIMUM_PRICE

        self.minimum_market_cap = (
            DEFAULT_MINIMUM_MARKET_CAP
        )

        self.maximum_gap_percent = (
            DEFAULT_MAXIMUM_GAP_PERCENT
        )

        self.minimum_adx = DEFAULT_MINIMUM_ADX

        self.minimum_volume_ratio = (
            DEFAULT_MINIMUM_VOLUME_RATIO
        )

        self.breakout_volume_ratio = (
            DEFAULT_BREAKOUT_VOLUME_RATIO
        )

        self.minimum_rr = DEFAULT_MINIMUM_RR

        self.minimum_score = (
            DEFAULT_MINIMUM_SCORE
        )

        self.minimum_confidence = (
            DEFAULT_MINIMUM_CONFIDENCE
        )

        self.atr_stop_multiple = (
            DEFAULT_ATR_STOP_MULTIPLE
        )

        self.target_rr = DEFAULT_TARGET_RR

        self.max_signals = 25

        # -------------------------------------------------
        # Direction controls
        # -------------------------------------------------

        self.allow_buy = True

        self.allow_sell = True

        # -------------------------------------------------
        # Confirmation controls
        # -------------------------------------------------

        self.require_vwap = True

        self.require_adx = True

        self.require_volume = True

        self.require_market_trend = False

        self.require_sector_confirmation = False

    # =====================================================
    # MAIN SCAN
    # =====================================================

    def scan(
        self,
        market_data: Dict[str, Any],
    ) -> List[Signal]:
        """
        Scan all supplied instruments.

        Important:
        This method only GENERATES signals.

        BaseScanner.run() handles:
            • validation
            • duplicate removal
            • filtering
            • ranking
            • limiting
        """

        generated: List[Signal] = []

        if not market_data:

            return generated

        for key, raw_data in market_data.items():

            if not isinstance(
                raw_data,
                dict,
            ):
                continue

            try:

                signal = self._scan_symbol(
                    key,
                    raw_data,
                )

                if signal is not None:

                    generated.append(
                        signal
                    )

            except Exception as exc:

                self.log(
                    "Failed:",
                    key,
                    exc,
                )

        return generated

    # =====================================================
    # SCAN SINGLE SYMBOL
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
                "",
            )
        ).strip()

        if not symbol:

            return None

        if not instrument_key:

            return None

        # -------------------------------------------------
        # Read prices
        # -------------------------------------------------

        last_price = self._number(
            data,
            "last_price",
            "ltp",
            "close",
        )

        open_price = self._number(
            data,
            "open",
            "open_price",
        )

        high_price = self._number(
            data,
            "high",
            "high_price",
        )

        low_price = self._number(
            data,
            "low",
            "low_price",
        )

        close_price = self._number(
            data,
            "close",
            "close_price",
            "last_price",
        )

        previous_close = self._number(
            data,
            "previous_close",
            "prev_close",
        )

        if last_price <= 0:

            return None

        # -------------------------------------------------
        # Basic universe filters
        # -------------------------------------------------

        if last_price < self.minimum_price:

            return None

        market_cap = self._number(
            data,
            "market_cap",
            "market_cap_cr",
        )

        if (
            market_cap > 0
            and market_cap
            < self.minimum_market_cap
        ):

            return None

        # -------------------------------------------------
        # Gap filter
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
        # Indicators
        # -------------------------------------------------

        ema9 = self._number(
            data,
            "ema9",
        )

        ema20 = self._number(
            data,
            "ema20",
        )

        ema21 = self._number(
            data,
            "ema21",
        )

        ema50 = self._number(
            data,
            "ema50",
        )

        ema100 = self._number(
            data,
            "ema100",
        )

        ema200 = self._number(
            data,
            "ema200",
        )

        rsi = self._number(
            data,
            "rsi",
        )

        macd = self._number(
            data,
            "macd",
        )

        macd_signal = self._number(
            data,
            "macd_signal",
        )

        macd_histogram = self._number(
            data,
            "macd_histogram",
        )

        adx = self._number(
            data,
            "adx",
        )

        plus_di = self._number(
            data,
            "plus_di",
        )

        minus_di = self._number(
            data,
            "minus_di",
        )

        vwap = self._number(
            data,
            "vwap",
        )

        supertrend = self._number(
            data,
            "supertrend",
        )

        supertrend_direction = self._integer(
            data,
            "supertrend_direction",
        )

        atr = self._number(
            data,
            "atr",
        )

        # -------------------------------------------------
        # Volume
        # -------------------------------------------------

        volume = self._integer(
            data,
            "volume",
        )

        average_volume = self._integer(
            data,
            "average_volume",
            "avg_volume",
        )

        volume_ratio = self._number(
            data,
            "volume_ratio",
            "rvol",
        )

        if (
            volume_ratio <= 0
            and volume > 0
            and average_volume > 0
        ):

            volume_ratio = (
                volume
                / average_volume
            )

        # -------------------------------------------------
        # ADX filter
        # -------------------------------------------------

        if (
            self.require_adx
            and adx > 0
            and adx < self.minimum_adx
        ):

            return None

        # -------------------------------------------------
        # Volume filter
        # -------------------------------------------------

        if (
            self.require_volume
            and volume_ratio > 0
            and volume_ratio
            < self.minimum_volume_ratio
        ):

            return None

        # -------------------------------------------------
        # Market information
        # -------------------------------------------------

        market_trend = (
            self._parse_market_trend(
                data.get(
                    "market_trend",
                    self.market_trend,
                )
            )
        )

        sector = str(
            data.get(
                "sector",
                "",
            )
        ).strip()

        sector_strength = self._number(
            data,
            "sector_strength",
        )

        market_strength = self._number(
            data,
            "market_strength",
        )

        relative_strength = self._number(
            data,
            "relative_strength",
        )

        beta = self._number(
            data,
            "beta",
        )

        # -------------------------------------------------
        # Determine direction
        # -------------------------------------------------

        buy_score = self._buy_setup_score(
            price=last_price,
            open_price=open_price,
            ema9=ema9,
            ema20=ema20,
            ema21=ema21,
            ema50=ema50,
            ema200=ema200,
            vwap=vwap,
            rsi=rsi,
            macd=macd,
            macd_signal=macd_signal,
            macd_histogram=macd_histogram,
            adx=adx,
            plus_di=plus_di,
            minus_di=minus_di,
            supertrend_direction=(
                supertrend_direction
            ),
            volume_ratio=volume_ratio,
            relative_strength=(
                relative_strength
            ),
            sector_strength=(
                sector_strength
            ),
            market_trend=market_trend,
        )

        sell_score = self._sell_setup_score(
            price=last_price,
            open_price=open_price,
            ema9=ema9,
            ema20=ema20,
            ema21=ema21,
            ema50=ema50,
            ema200=ema200,
            vwap=vwap,
            rsi=rsi,
            macd=macd,
            macd_signal=macd_signal,
            macd_histogram=macd_histogram,
            adx=adx,
            plus_di=plus_di,
            minus_di=minus_di,
            supertrend_direction=(
                supertrend_direction
            ),
            volume_ratio=volume_ratio,
            relative_strength=(
                relative_strength
            ),
            sector_strength=(
                sector_strength
            ),
            market_trend=market_trend,
        )

        signal_type: Optional[
            SignalType
        ] = None

        raw_score = 0.0

        if (
            self.allow_buy
            and buy_score >= sell_score
            and buy_score
            >= self.minimum_score
        ):

            signal_type = SignalType.BUY

            raw_score = buy_score

        elif (
            self.allow_sell
            and sell_score > buy_score
            and sell_score
            >= self.minimum_score
        ):

            signal_type = SignalType.SELL

            raw_score = sell_score

        if signal_type is None:

            return None

        # -------------------------------------------------
        # Direction-specific hard confirmations
        # -------------------------------------------------

        if signal_type == SignalType.BUY:

            if (
                self.require_vwap
                and vwap > 0
                and last_price <= vwap
            ):

                return None

            if (
                self.require_market_trend
                and market_trend
                in {
                    MarketTrend.BEARISH,
                    MarketTrend.STRONG_BEARISH,
                }
            ):

                return None

            if (
                self.require_sector_confirmation
                and sector_strength < 50
            ):

                return None

        else:

            if (
                self.require_vwap
                and vwap > 0
                and last_price >= vwap
            ):

                return None

            if (
                self.require_market_trend
                and market_trend
                in {
                    MarketTrend.BULLISH,
                    MarketTrend.STRONG_BULLISH,
                }
            ):

                return None

            if (
                self.require_sector_confirmation
                and sector_strength > 50
            ):

                return None

        # -------------------------------------------------
        # Risk management
        # -------------------------------------------------

        (
            entry,
            stop_loss,
            target1,
            target2,
            target3,
        ) = self._calculate_trade_levels(
            signal_type=signal_type,
            price=last_price,
            low_price=low_price,
            high_price=high_price,
            atr=atr,
        )

        if (
            entry <= 0
            or stop_loss <= 0
            or target1 <= 0
        ):

            return None

        # -------------------------------------------------
        # Pattern classification
        # -------------------------------------------------

        pattern = self._detect_pattern(
            signal_type=signal_type,
            price=last_price,
            high_price=high_price,
            low_price=low_price,
            ema9=ema9,
            ema21=ema21,
            ema50=ema50,
            vwap=vwap,
            volume_ratio=volume_ratio,
        )

        # -------------------------------------------------
        # Confidence
        # -------------------------------------------------

        confidence = self._calculate_confidence(
            score=raw_score,
            adx=adx,
            volume_ratio=volume_ratio,
            relative_strength=(
                relative_strength
            ),
            sector_strength=(
                sector_strength
            ),
        )

        if (
            confidence
            < self.minimum_confidence
        ):

            return None

        # -------------------------------------------------
        # Strength
        # -------------------------------------------------

        strength = self._signal_strength(
            raw_score
        )

        # -------------------------------------------------
        # Score breakdown
        # -------------------------------------------------

        score_breakdown = (
            self._score_breakdown(
                signal_type=signal_type,
                price=last_price,
                ema9=ema9,
                ema21=ema21,
                ema50=ema50,
                ema200=ema200,
                vwap=vwap,
                rsi=rsi,
                macd=macd,
                macd_signal=macd_signal,
                adx=adx,
                volume_ratio=volume_ratio,
                relative_strength=(
                    relative_strength
                ),
                sector_strength=(
                    sector_strength
                ),
                market_trend=market_trend,
            )
        )

        # -------------------------------------------------
        # Create signal
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
                "StockVersity Intraday"
            ),

            timeframe=self.timeframe,

            market_trend=market_trend,

            sector=sector,

            sector_strength=sector_strength,

            market_strength=market_strength,

            relative_strength=(
                relative_strength
            ),

            beta=beta,

            last_price=last_price,

            open_price=open_price,

            high_price=high_price,

            low_price=low_price,

            close_price=close_price,

            previous_close=previous_close,

            gap_percent=gap_percent,

            volume=volume,

            average_volume=average_volume,

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

            atr_multiple=(
                self.atr_stop_multiple
            ),

            atr_stop=stop_loss,

            ema9=ema9,

            ema20=ema20,

            ema21=ema21,

            ema50=ema50,

            ema100=ema100,

            ema200=ema200,

            rsi=rsi,

            macd=macd,

            macd_signal=macd_signal,

            macd_histogram=(
                macd_histogram
            ),

            adx=adx,

            plus_di=plus_di,

            minus_di=minus_di,

            vwap=vwap,

            supertrend=supertrend,

            supertrend_direction=(
                supertrend_direction
            ),

            confidence=confidence,

            score=round(
                min(raw_score, 100.0),
                2,
            ),

            score_breakdown=(
                score_breakdown
            ),

            remarks=(
                self._build_remarks(
                    signal_type,
                    pattern,
                    adx,
                    volume_ratio,
                )
            ),

            tags=self._build_tags(
                signal_type=signal_type,
                pattern=pattern,
                volume_ratio=volume_ratio,
                adx=adx,
            ),

            metadata={

                "market_cap": market_cap,

                "scanner_category": (
                    "INTRADAY"
                ),

                "timeframe": (
                    self.timeframe
                ),

                "raw_score": (
                    round(
                        raw_score,
                        2,
                    )
                ),

            },

        )

        # -------------------------------------------------
        # Final RR protection
        # -------------------------------------------------

        if (
            signal.risk_reward
            < self.minimum_rr
        ):

            return None

        return signal

    # =====================================================
    # BUY SCORE
    # =====================================================

    def _buy_setup_score(
        self,
        *,
        price: float,
        open_price: float,
        ema9: float,
        ema20: float,
        ema21: float,
        ema50: float,
        ema200: float,
        vwap: float,
        rsi: float,
        macd: float,
        macd_signal: float,
        macd_histogram: float,
        adx: float,
        plus_di: float,
        minus_di: float,
        supertrend_direction: int,
        volume_ratio: float,
        relative_strength: float,
        sector_strength: float,
        market_trend: MarketTrend,
    ) -> float:

        score = 0.0

        # Trend structure - 25

        if ema9 > 0 and price > ema9:
            score += 5

        if (
            ema9 > 0
            and ema21 > 0
            and ema9 > ema21
        ):
            score += 5

        if (
            ema21 > 0
            and ema50 > 0
            and ema21 > ema50
        ):
            score += 5

        if (
            ema50 > 0
            and ema200 > 0
            and ema50 > ema200
        ):
            score += 5

        if (
            ema200 > 0
            and price > ema200
        ):
            score += 5

        # VWAP - 10

        if vwap > 0 and price > vwap:
            score += 10

        # RSI - 10

        if 55 <= rsi <= 75:
            score += 10

        elif 50 <= rsi < 55:
            score += 5

        # MACD - 10

        if (
            macd > macd_signal
            and macd_histogram >= 0
        ):
            score += 10

        # ADX / DI - 10

        if (
            adx >= self.minimum_adx
            and plus_di > minus_di
        ):
            score += 10

        # Supertrend - 5

        if supertrend_direction > 0:
            score += 5

        # Volume - 10

        if (
            volume_ratio
            >= self.breakout_volume_ratio
        ):
            score += 10

        elif (
            volume_ratio
            >= self.minimum_volume_ratio
        ):
            score += 5

        # Relative strength - 5

        if relative_strength >= 60:
            score += 5

        # Sector - 5

        if sector_strength >= 60:
            score += 5

        # Market trend - 5

        if market_trend in {
            MarketTrend.BULLISH,
            MarketTrend.STRONG_BULLISH,
        }:
            score += 5

        # Intraday positive candle - 5

        if (
            open_price > 0
            and price > open_price
        ):
            score += 5

        return min(
            score,
            100.0,
        )

    # =====================================================
    # SELL SCORE
    # =====================================================

    def _sell_setup_score(
        self,
        *,
        price: float,
        open_price: float,
        ema9: float,
        ema20: float,
        ema21: float,
        ema50: float,
        ema200: float,
        vwap: float,
        rsi: float,
        macd: float,
        macd_signal: float,
        macd_histogram: float,
        adx: float,
        plus_di: float,
        minus_di: float,
        supertrend_direction: int,
        volume_ratio: float,
        relative_strength: float,
        sector_strength: float,
        market_trend: MarketTrend,
    ) -> float:

        score = 0.0

        # Trend structure - 25

        if ema9 > 0 and price < ema9:
            score += 5

        if (
            ema9 > 0
            and ema21 > 0
            and ema9 < ema21
        ):
            score += 5

        if (
            ema21 > 0
            and ema50 > 0
            and ema21 < ema50
        ):
            score += 5

        if (
            ema50 > 0
            and ema200 > 0
            and ema50 < ema200
        ):
            score += 5

        if (
            ema200 > 0
            and price < ema200
        ):
            score += 5

        # VWAP - 10

        if vwap > 0 and price < vwap:
            score += 10

        # RSI - 10

        if 25 <= rsi <= 45:
            score += 10

        elif 45 < rsi <= 50:
            score += 5

        # MACD - 10

        if (
            macd < macd_signal
            and macd_histogram <= 0
        ):
            score += 10

        # ADX / DI - 10

        if (
            adx >= self.minimum_adx
            and minus_di > plus_di
        ):
            score += 10

        # Supertrend - 5

        if supertrend_direction < 0:
            score += 5

        # Volume - 10

        if (
            volume_ratio
            >= self.breakout_volume_ratio
        ):
            score += 10

        elif (
            volume_ratio
            >= self.minimum_volume_ratio
        ):
            score += 5

        # Relative weakness - 5

        if (
            relative_strength > 0
            and relative_strength <= 40
        ):
            score += 5

        # Weak sector - 5

        if (
            sector_strength > 0
            and sector_strength <= 40
        ):
            score += 5

        # Bearish market - 5

        if market_trend in {
            MarketTrend.BEARISH,
            MarketTrend.STRONG_BEARISH,
        }:
            score += 5

        # Intraday negative candle - 5

        if (
            open_price > 0
            and price < open_price
        ):
            score += 5

        return min(
            score,
            100.0,
        )

    # =====================================================
    # SCORE BREAKDOWN
    # =====================================================

    def _score_breakdown(
        self,
        *,
        signal_type: SignalType,
        price: float,
        ema9: float,
        ema21: float,
        ema50: float,
        ema200: float,
        vwap: float,
        rsi: float,
        macd: float,
        macd_signal: float,
        adx: float,
        volume_ratio: float,
        relative_strength: float,
        sector_strength: float,
        market_trend: MarketTrend,
    ) -> Dict[str, float]:

        bullish = (
            signal_type == SignalType.BUY
        )

        trend = 0.0

        if bullish:

            if ema9 > 0 and price > ema9:
                trend += 4

            if (
                ema9 > 0
                and ema21 > 0
                and ema9 > ema21
            ):
                trend += 4

            if (
                ema21 > 0
                and ema50 > 0
                and ema21 > ema50
            ):
                trend += 4

            if (
                ema200 > 0
                and price > ema200
            ):
                trend += 3

        else:

            if ema9 > 0 and price < ema9:
                trend += 4

            if (
                ema9 > 0
                and ema21 > 0
                and ema9 < ema21
            ):
                trend += 4

            if (
                ema21 > 0
                and ema50 > 0
                and ema21 < ema50
            ):
                trend += 4

            if (
                ema200 > 0
                and price < ema200
            ):
                trend += 3

        volume_score = min(
            max(
                volume_ratio,
                0.0,
            ) * 4.0,
            15.0,
        )

        momentum = 0.0

        if bullish:

            if 50 <= rsi <= 75:
                momentum += 5

            if macd > macd_signal:
                momentum += 5

            if adx >= self.minimum_adx:
                momentum += 5

        else:

            if 25 <= rsi <= 50:
                momentum += 5

            if macd < macd_signal:
                momentum += 5

            if adx >= self.minimum_adx:
                momentum += 5

        pattern_score = 10.0

        if bullish:

            if vwap > 0 and price > vwap:
                pattern_score += 5

        else:

            if vwap > 0 and price < vwap:
                pattern_score += 5

        sector_score = min(
            max(
                (
                    sector_strength
                    if bullish
                    else 100
                    - sector_strength
                ),
                0.0,
            )
            / 100
            * 10,
            10.0,
        )

        rs_score = min(
            max(
                (
                    relative_strength
                    if bullish
                    else 100
                    - relative_strength
                ),
                0.0,
            )
            / 100
            * 15,
            15.0,
        )

        market_score = 0.0

        if bullish and market_trend in {
            MarketTrend.BULLISH,
            MarketTrend.STRONG_BULLISH,
        }:
            market_score = 15.0

        elif (
            not bullish
            and market_trend in {
                MarketTrend.BEARISH,
                MarketTrend.STRONG_BEARISH,
            }
        ):
            market_score = 15.0

        elif (
            market_trend
            == MarketTrend.SIDEWAYS
        ):
            market_score = 7.5

        breakdown = {

            "trend": round(
                trend,
                2,
            ),

            "volume": round(
                volume_score,
                2,
            ),

            "momentum": round(
                momentum,
                2,
            ),

            "pattern": round(
                pattern_score,
                2,
            ),

            "sector": round(
                sector_score,
                2,
            ),

            "relative_strength": round(
                rs_score,
                2,
            ),

            "market": round(
                market_score,
                2,
            ),

        }

        return breakdown

    # =====================================================
    # TRADE LEVELS
    # =====================================================

    def _calculate_trade_levels(
        self,
        *,
        signal_type: SignalType,
        price: float,
        low_price: float,
        high_price: float,
        atr: float,
    ) -> Tuple[
        float,
        float,
        float,
        float,
        float,
    ]:

        entry = price

        # -------------------------------------------------
        # ATR fallback
        # -------------------------------------------------

        if atr <= 0:

            atr = price * 0.01

        atr_distance = (
            atr
            * self.atr_stop_multiple
        )

        # -------------------------------------------------
        # BUY
        # -------------------------------------------------

        if signal_type == SignalType.BUY:

            atr_stop = (
                entry - atr_distance
            )

            if (
                low_price > 0
                and low_price < entry
            ):

                stop_loss = max(
                    atr_stop,
                    low_price,
                )

            else:

                stop_loss = atr_stop

            risk = (
                entry - stop_loss
            )

            if risk <= 0:

                return (
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                )

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

        # -------------------------------------------------
        # SELL
        # -------------------------------------------------

        else:

            atr_stop = (
                entry + atr_distance
            )

            if (
                high_price > entry
            ):

                stop_loss = min(
                    atr_stop,
                    high_price,
                )

            else:

                stop_loss = atr_stop

            risk = (
                stop_loss - entry
            )

            if risk <= 0:

                return (
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                )

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

            if target1 <= 0:

                return (
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                )

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
                max(
                    target2,
                    0.0,
                ),
                2,
            ),

            round(
                max(
                    target3,
                    0.0,
                ),
                2,
            ),

        )

    # =====================================================
    # PATTERN DETECTION
    # =====================================================

    def _detect_pattern(
        self,
        *,
        signal_type: SignalType,
        price: float,
        high_price: float,
        low_price: float,
        ema9: float,
        ema21: float,
        ema50: float,
        vwap: float,
        volume_ratio: float,
    ) -> PatternType:

        if signal_type == SignalType.BUY:

            if (
                volume_ratio
                >= self.breakout_volume_ratio
                and high_price > 0
                and price >= high_price * 0.998
            ):

                return PatternType.BREAKOUT

            if (
                ema9 > 0
                and ema21 > 0
                and ema50 > 0
                and ema9 > ema21 > ema50
            ):

                return PatternType.MOMENTUM

            if (
                vwap > 0
                and price > vwap
                and ema9 > 0
                and price > ema9
            ):

                return PatternType.VWAP_RECLAIM

        else:

            if (
                volume_ratio
                >= self.breakout_volume_ratio
                and low_price > 0
                and price <= low_price * 1.002
            ):

                return PatternType.BREAKDOWN

            if (
                ema9 > 0
                and ema21 > 0
                and ema50 > 0
                and ema9 < ema21 < ema50
            ):

                return PatternType.MOMENTUM

        return PatternType.CUSTOM

    # =====================================================
    # CONFIDENCE
    # =====================================================

    def _calculate_confidence(
        self,
        *,
        score: float,
        adx: float,
        volume_ratio: float,
        relative_strength: float,
        sector_strength: float,
    ) -> float:

        confidence = (
            score * 0.65
        )

        if adx >= 30:

            confidence += 10

        elif adx >= 25:

            confidence += 7

        elif adx >= 20:

            confidence += 4

        if volume_ratio >= 2.0:

            confidence += 10

        elif volume_ratio >= 1.5:

            confidence += 7

        elif volume_ratio >= 1.2:

            confidence += 4

        if (
            relative_strength >= 60
            or (
                relative_strength > 0
                and relative_strength <= 40
            )
        ):

            confidence += 5

        if (
            sector_strength >= 60
            or (
                sector_strength > 0
                and sector_strength <= 40
            )
        ):

            confidence += 5

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
    def _signal_strength(
        score: float,
    ) -> SignalStrength:

        if score >= 90:

            return (
                SignalStrength.VERY_STRONG
            )

        if score >= 80:

            return SignalStrength.STRONG

        if score >= 70:

            return (
                SignalStrength.MODERATE
            )

        if score >= 60:

            return SignalStrength.WEAK

        return SignalStrength.VERY_WEAK

    # =====================================================
    # REMARKS
    # =====================================================

    @staticmethod
    def _build_remarks(
        signal_type: SignalType,
        pattern: PatternType,
        adx: float,
        volume_ratio: float,
    ) -> str:

        direction = (
            "Bullish"
            if signal_type
            == SignalType.BUY
            else "Bearish"
        )

        return (

            f"{direction} intraday setup | "

            f"{pattern.value} | "

            f"ADX {adx:.1f} | "

            f"RVOL {volume_ratio:.2f}"

        )

    # =====================================================
    # TAGS
    # =====================================================

    @staticmethod
    def _build_tags(
        *,
        signal_type: SignalType,
        pattern: PatternType,
        volume_ratio: float,
        adx: float,
    ) -> List[str]:

        tags = [

            "INTRADAY",

            signal_type.value,

            pattern.value,

        ]

        if volume_ratio >= 2.0:

            tags.append(
                "HIGH_VOLUME"
            )

        if adx >= 30:

            tags.append(
                "STRONG_TREND"
            )

        return tags

    # =====================================================
    # GAP PERCENT
    # =====================================================

    @staticmethod
    def _gap_percent(
        open_price: float,
        previous_close: float,
    ) -> float:

        if previous_close <= 0:

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
    # MARKET TREND PARSER
    # =====================================================

    @staticmethod
    def _parse_market_trend(
        value: Any,
    ) -> MarketTrend:

        if isinstance(
            value,
            MarketTrend,
        ):

            return value

        text = str(
            value or ""
        ).upper().strip()

        aliases = {

            "STRONG_BULLISH":
                MarketTrend.STRONG_BULLISH,

            "STRONGLY_BULLISH":
                MarketTrend.STRONG_BULLISH,

            "BULLISH":
                MarketTrend.BULLISH,

            "UP":
                MarketTrend.BULLISH,

            "SIDEWAYS":
                MarketTrend.SIDEWAYS,

            "NEUTRAL":
                MarketTrend.SIDEWAYS,

            "UNKNOWN":
                MarketTrend.SIDEWAYS,

            "BEARISH":
                MarketTrend.BEARISH,

            "DOWN":
                MarketTrend.BEARISH,

            "STRONG_BEARISH":
                MarketTrend.STRONG_BEARISH,

            "STRONGLY_BEARISH":
                MarketTrend.STRONG_BEARISH,

        }

        return aliases.get(
            text,
            MarketTrend.SIDEWAYS,
        )

    # =====================================================
    # SAFE FLOAT READER
    # =====================================================

    @staticmethod
    def _number(
        data: Dict[str, Any],
        *keys: str,
    ) -> float:

        for key in keys:

            value = data.get(key)

            if value is None:
                continue

            try:

                return float(value)

            except (
                TypeError,
                ValueError,
            ):

                continue

        return 0.0

    # =====================================================
    # SAFE INTEGER READER
    # =====================================================

    @staticmethod
    def _integer(
        data: Dict[str, Any],
        *keys: str,
    ) -> int:

        for key in keys:

            value = data.get(key)

            if value is None:
                continue

            try:

                return int(
                    float(value)
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

        return 0

    # =====================================================
    # CONFIGURATION HELPERS
    # =====================================================

    def set_universe_filters(
        self,
        *,
        minimum_price: Optional[
            float
        ] = None,
        minimum_market_cap: Optional[
            float
        ] = None,
        maximum_gap_percent: Optional[
            float
        ] = None,
    ) -> "IntradayScanner":

        if minimum_price is not None:

            self.minimum_price = max(
                float(
                    minimum_price
                ),
                0.0,
            )

        if (
            minimum_market_cap
            is not None
        ):

            self.minimum_market_cap = max(
                float(
                    minimum_market_cap
                ),
                0.0,
            )

        if (
            maximum_gap_percent
            is not None
        ):

            self.maximum_gap_percent = max(
                float(
                    maximum_gap_percent
                ),
                0.0,
            )

        return self

    # =====================================================
    # QUALITY FILTERS
    # =====================================================

    def set_quality_filters(
        self,
        *,
        minimum_score: Optional[
            float
        ] = None,
        minimum_confidence: Optional[
            float
        ] = None,
        minimum_rr: Optional[
            float
        ] = None,
        minimum_adx: Optional[
            float
        ] = None,
        minimum_volume_ratio: Optional[
            float
        ] = None,
    ) -> "IntradayScanner":

        if minimum_score is not None:

            self.minimum_score = max(
                0.0,
                min(
                    float(
                        minimum_score
                    ),
                    100.0,
                ),
            )

        if (
            minimum_confidence
            is not None
        ):

            self.minimum_confidence = max(
                0.0,
                min(
                    float(
                        minimum_confidence
                    ),
                    100.0,
                ),
            )

        if minimum_rr is not None:

            self.minimum_rr = max(
                float(
                    minimum_rr
                ),
                0.0,
            )

        if minimum_adx is not None:

            self.minimum_adx = max(
                float(
                    minimum_adx
                ),
                0.0,
            )

        if (
            minimum_volume_ratio
            is not None
        ):

            self.minimum_volume_ratio = max(
                float(
                    minimum_volume_ratio
                ),
                0.0,
            )

        return self

    # =====================================================
    # DIRECTION CONTROL
    # =====================================================

    def enable_buy(
        self,
    ) -> "IntradayScanner":

        self.allow_buy = True

        return self

    def disable_buy(
        self,
    ) -> "IntradayScanner":

        self.allow_buy = False

        return self

    def enable_sell(
        self,
    ) -> "IntradayScanner":

        self.allow_sell = True

        return self

    def disable_sell(
        self,
    ) -> "IntradayScanner":

        self.allow_sell = False

        return self


# =========================================================
# FACTORY
# =========================================================

def create_intraday_scanner(
    timeframe: str = "5m",
    *,
    minimum_price: float = (
        DEFAULT_MINIMUM_PRICE
    ),
    minimum_market_cap: float = (
        DEFAULT_MINIMUM_MARKET_CAP
    ),
    minimum_score: float = (
        DEFAULT_MINIMUM_SCORE
    ),
    minimum_rr: float = (
        DEFAULT_MINIMUM_RR
    ),
) -> IntradayScanner:
    """
    Create a configured IntradayScanner.
    """

    scanner = IntradayScanner(
        timeframe=timeframe
    )

    scanner.set_universe_filters(

        minimum_price=minimum_price,

        minimum_market_cap=(
            minimum_market_cap
        ),

    )

    scanner.set_quality_filters(

        minimum_score=minimum_score,

        minimum_rr=minimum_rr,

    )

    return scanner


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "IntradayScanner",

    "create_intraday_scanner",

    "SUPPORTED_TIMEFRAMES",

]


# ==========================
# END OF FILE
# ==========================