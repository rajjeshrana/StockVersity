from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

import numpy as np
import pandas as pd


# ==========================================================
# MARKET REGIME
# ==========================================================

class MarketRegime(Enum):

    STRONG_BULL = "STRONG_BULL"

    BULL = "BULL"

    SIDEWAYS = "SIDEWAYS"

    BEAR = "BEAR"

    STRONG_BEAR = "STRONG_BEAR"

    VOLATILE = "VOLATILE"

    UNKNOWN = "UNKNOWN"


# ==========================================================
# VOLATILITY STATE
# ==========================================================

class VolatilityState(Enum):

    VERY_LOW = "VERY_LOW"

    LOW = "LOW"

    NORMAL = "NORMAL"

    HIGH = "HIGH"

    EXTREME = "EXTREME"


# ==========================================================
# TREND STRENGTH
# ==========================================================

class TrendStrength(Enum):

    VERY_WEAK = "VERY_WEAK"

    WEAK = "WEAK"

    MODERATE = "MODERATE"

    STRONG = "STRONG"

    VERY_STRONG = "VERY_STRONG"


# ==========================================================
# MARKET REGIME RESULT
# ==========================================================

@dataclass

class MarketRegimeResult:

    regime: MarketRegime

    confidence: float

    score: float

    trend_strength: TrendStrength

    volatility: VolatilityState

    reasons: List[str] = field(default_factory=list)

    warnings: List[str] = field(default_factory=list)

    indicators: Dict = field(default_factory=dict)


# ==========================================================
# MARKET REGIME ENGINE
# ==========================================================

class MarketRegimeEngine:

    def __init__(self):

        self.data: Optional[pd.DataFrame] = None

        self.symbol: str = ""

        self.result: Optional[MarketRegimeResult] = None

    # ======================================================
    # LOAD DATA
    # ======================================================

    def load(

        self,

        symbol: str,

        data: pd.DataFrame,

    ) -> None:

        self.symbol = symbol

        self.data = data.copy()

    # ======================================================
    # VALIDATE
    # ======================================================

    def validate(self):

        if self.data is None:

            raise ValueError(

                "Market data not loaded."

            )

        required = [

            "Open",

            "High",

            "Low",

            "Close",

            "Volume",

        ]

        for column in required:

            if column not in self.data.columns:

                raise ValueError(

                    f"Missing column: {column}"

                )

    # ======================================================
    # CLOSE
    # ======================================================

    @property

    def close(

        self,

    ) -> pd.Series:

        return self.data["Close"]

    # ======================================================
    # HIGH
    # ======================================================

    @property

    def high(

        self,

    ) -> pd.Series:

        return self.data["High"]

    # ======================================================
    # LOW
    # ======================================================

    @property

    def low(

        self,

    ) -> pd.Series:

        return self.data["Low"]

    # ======================================================
    # VOLUME
    # ======================================================

    @property

    def volume(

        self,

    ) -> pd.Series:

        return self.data["Volume"]

    # ======================================================
    # RESET
    # ======================================================

    def reset(self):

        self.data = None

        self.result = None

        self.symbol = ""
            # ======================================================
    # EMA
    # ======================================================

    def ema(

        self,

        period: int,

    ) -> pd.Series:

        return self.close.ewm(

            span=period,

            adjust=False,

        ).mean()

    # ======================================================
    # SMA
    # ======================================================

    def sma(

        self,

        period: int,

    ) -> pd.Series:

        return self.close.rolling(

            period,

        ).mean()

    # ======================================================
    # ATR
    # ======================================================

    def atr(

        self,

        period: int = 14,

    ) -> pd.Series:

        high_low = self.high - self.low

        high_close = (

            self.high

            - self.close.shift()

        ).abs()

        low_close = (

            self.low

            - self.close.shift()

        ).abs()

        true_range = pd.concat(

            [

                high_low,

                high_close,

                low_close,

            ],

            axis=1,

        ).max(

            axis=1,

        )

        return true_range.rolling(

            period,

        ).mean()

    # ======================================================
    # RSI
    # ======================================================

    def rsi(

        self,

        period: int = 14,

    ) -> pd.Series:

        delta = self.close.diff()

        gain = delta.clip(

            lower=0,

        )

        loss = -delta.clip(

            upper=0,

        )

        avg_gain = gain.rolling(

            period,

        ).mean()

        avg_loss = loss.rolling(

            period,

        ).mean()

        rs = avg_gain / avg_loss.replace(

            0,

            np.nan,

        )

        return 100 - (

            100

            /

            (

                1

                +

                rs

            )

        )

    # ======================================================
    # MACD
    # ======================================================

    def macd(

        self,

        fast: int = 12,

        slow: int = 26,

        signal: int = 9,

    ) -> Dict[str, pd.Series]:

        fast_ema = self.ema(

            fast,

        )

        slow_ema = self.ema(

            slow,

        )

        macd = fast_ema - slow_ema

        signal_line = macd.ewm(

            span=signal,

            adjust=False,

        ).mean()

        histogram = macd - signal_line

        return {

            "macd":

                macd,

            "signal":

                signal_line,

            "histogram":

                histogram,

        }

    # ======================================================
    # ADX
    # ======================================================

    def adx(

        self,

        period: int = 14,

    ) -> pd.Series:

        up_move = self.high.diff()

        down_move = -self.low.diff()

        plus_dm = np.where(

            (

                up_move > down_move

            )

            &

            (

                up_move > 0

            ),

            up_move,

            0,

        )

        minus_dm = np.where(

            (

                down_move > up_move

            )

            &

            (

                down_move > 0

            ),

            down_move,

            0,

        )

        tr = self.atr(

            1,

        )

        plus_di = (

            pd.Series(

                plus_dm,

                index=self.data.index,

            ).rolling(

                period,

            ).sum()

            /

            tr.rolling(

                period,

            ).sum()

        ) * 100

        minus_di = (

            pd.Series(

                minus_dm,

                index=self.data.index,

            ).rolling(

                period,

            ).sum()

            /

            tr.rolling(

                period,

            ).sum()

        ) * 100

        dx = (

            (

                plus_di

                -

                minus_di

            ).abs()

            /

            (

                plus_di

                +

                minus_di

            )

        ) * 100

        return dx.rolling(

            period,

        ).mean()

    # ======================================================
    # BOLLINGER BANDS
    # ======================================================

    def bollinger_bands(

        self,

        period: int = 20,

        deviation: float = 2.0,

    ) -> Dict[str, pd.Series]:

        middle = self.sma(

            period,

        )

        std = self.close.rolling(

            period,

        ).std()

        upper = middle + std * deviation

        lower = middle - std * deviation

        width = (

            upper - lower

        ) / middle

        return {

            "upper":

                upper,

            "middle":

                middle,

            "lower":

                lower,

            "width":

                width,

        }

    # ======================================================
    # VWAP
    # ======================================================

    def vwap(

        self,

    ) -> pd.Series:

        typical_price = (

            self.high

            +

            self.low

            +

            self.close

        ) / 3

        cumulative_tpv = (

            typical_price

            *

            self.volume

        ).cumsum()

        cumulative_volume = (

            self.volume.cumsum()

        )

        return cumulative_tpv / cumulative_volume
        # ======================================================
    # EMA ALIGNMENT
    # ======================================================

    def ema_alignment(

        self,

    ) -> Dict:

        ema20 = self.ema(20).iloc[-1]

        ema50 = self.ema(50).iloc[-1]

        ema100 = self.ema(100).iloc[-1]

        ema200 = self.ema(200).iloc[-1]

        bullish = (

            ema20 > ema50 >

            ema100 > ema200

        )

        bearish = (

            ema20 < ema50 <

            ema100 < ema200

        )

        score = 50.0

        if bullish:

            score = 100.0

        elif bearish:

            score = 0.0

        return {

            "bullish": bullish,

            "bearish": bearish,

            "score": score,

            "ema20": float(ema20),

            "ema50": float(ema50),

            "ema100": float(ema100),

            "ema200": float(ema200),

        }

    # ======================================================
    # PRICE STRUCTURE
    # ======================================================

    def price_structure(

        self,

        lookback: int = 20,

    ) -> Dict:

        highs = self.high.tail(

            lookback,

        )

        lows = self.low.tail(

            lookback,

        )

        higher_high = (

            highs.iloc[-1]

            >

            highs.iloc[:-1].max()

        )

        lower_low = (

            lows.iloc[-1]

            <

            lows.iloc[:-1].min()

        )

        return {

            "higher_high": higher_high,

            "lower_low": lower_low,

            "highest": float(highs.max()),

            "lowest": float(lows.min()),

        }

    # ======================================================
    # SWING ANALYSIS
    # ======================================================

    def swing_structure(

        self,

        period: int = 10,

    ) -> Dict:

        highs = self.high.tail(period)

        lows = self.low.tail(period)

        higher_lows = np.all(

            np.diff(

                lows.values

            ) >= 0

        )

        lower_highs = np.all(

            np.diff(

                highs.values

            ) <= 0

        )

        return {

            "higher_lows": bool(higher_lows),

            "lower_highs": bool(lower_highs),

        }

    # ======================================================
    # MOMENTUM SCORE
    # ======================================================

    def momentum_score(

        self,

    ) -> float:

        rsi = self.rsi().iloc[-1]

        macd = self.macd()

        hist = macd["histogram"].iloc[-1]

        score = 50.0

        score += (rsi - 50) * 0.8

        score += hist * 20

        return round(

            max(

                min(score, 100),

                0,

            ),

            2,

        )

    # ======================================================
    # VOLATILITY STATE
    # ======================================================

    def volatility_state(

        self,

    ) -> VolatilityState:

        atr_percent = (

            self.atr().iloc[-1]

            /

            self.close.iloc[-1]

        ) * 100

        if atr_percent < 1:

            return VolatilityState.VERY_LOW

        if atr_percent < 2:

            return VolatilityState.LOW

        if atr_percent < 4:

            return VolatilityState.NORMAL

        if atr_percent < 6:

            return VolatilityState.HIGH

        return VolatilityState.EXTREME

    # ======================================================
    # TREND STRENGTH
    # ======================================================

    def trend_strength(

        self,

    ) -> TrendStrength:

        adx = self.adx().iloc[-1]

        if adx < 15:

            return TrendStrength.VERY_WEAK

        if adx < 25:

            return TrendStrength.WEAK

        if adx < 35:

            return TrendStrength.MODERATE

        if adx < 45:

            return TrendStrength.STRONG

        return TrendStrength.VERY_STRONG

    # ======================================================
    # TREND SCORE
    # ======================================================

    def trend_score(

        self,

    ) -> float:

        ema = self.ema_alignment()

        momentum = self.momentum_score()

        adx = self.adx().iloc[-1]

        score = (

            ema["score"] * 0.40

            +

            momentum * 0.40

            +

            min(adx, 50) * 2 * 0.20

        )

        return round(

            min(score, 100),

            2,

        )

    # ======================================================
    # MARKET PHASE SCORE
    # ======================================================

    def phase_score(

        self,

    ) -> Dict:

        trend = self.trend_score()

        volatility = self.volatility_state()

        strength = self.trend_strength()

        return {

            "trend_score": trend,

            "volatility": volatility,

            "strength": strength,

        }
        # ======================================================
    # BULL SCORE
    # ======================================================

    def bull_score(

        self,

    ) -> float:

        ema = self.ema_alignment()

        momentum = self.momentum_score()

        adx = self.adx().iloc[-1]

        close = self.close.iloc[-1]

        ema20 = self.ema(20).iloc[-1]

        score = 0.0

        if ema["bullish"]:

            score += 35

        if close > ema20:

            score += 20

        score += momentum * 0.25

        score += min(

            adx,

            50,

        ) * 0.40

        return round(

            min(

                score,

                100,

            ),

            2,

        )

    # ======================================================
    # BEAR SCORE
    # ======================================================

    def bear_score(

        self,

    ) -> float:

        ema = self.ema_alignment()

        momentum = 100 - self.momentum_score()

        adx = self.adx().iloc[-1]

        close = self.close.iloc[-1]

        ema20 = self.ema(20).iloc[-1]

        score = 0.0

        if ema["bearish"]:

            score += 35

        if close < ema20:

            score += 20

        score += momentum * 0.25

        score += min(

            adx,

            50,

        ) * 0.40

        return round(

            min(

                score,

                100,

            ),

            2,

        )

    # ======================================================
    # REGIME CLASSIFICATION
    # ======================================================

    def classify_regime(

        self,

    ) -> MarketRegime:

        bull = self.bull_score()

        bear = self.bear_score()

        adx = self.adx().iloc[-1]

        volatility = self.volatility_state()

        if volatility == VolatilityState.EXTREME:

            return MarketRegime.VOLATILE

        if bull >= 85:

            return MarketRegime.STRONG_BULL

        if bull >= 65:

            return MarketRegime.BULL

        if bear >= 85:

            return MarketRegime.STRONG_BEAR

        if bear >= 65:

            return MarketRegime.BEAR

        if adx < 20:

            return MarketRegime.SIDEWAYS

        return MarketRegime.UNKNOWN

    # ======================================================
    # REGIME CONFIDENCE
    # ======================================================

    def regime_confidence(

        self,

    ) -> float:

        bull = self.bull_score()

        bear = self.bear_score()

        difference = abs(

            bull - bear,

        )

        confidence = 60 + difference * 0.40

        return round(

            min(

                confidence,

                99,

            ),

            2,

        )

    # ======================================================
    # REGIME TRANSITION
    # ======================================================

    def transition_probability(

        self,

    ) -> float:

        adx = self.adx().iloc[-1]

        macd_hist = self.macd()["histogram"].iloc[-1]

        probability = 0.0

        if adx < 20:

            probability += 40

        if abs(

            macd_hist,

        ) < 0.15:

            probability += 30

        probability += (

            30

            -

            min(

                adx,

                30,

            )

        )

        return round(

            min(

                max(

                    probability,

                    0,

                ),

                100,

            ),

            2,

        )

    # ======================================================
    # TREND CONTINUATION
    # ======================================================

    def continuation_probability(

        self,

    ) -> float:

        adx = self.adx().iloc[-1]

        ema = self.ema_alignment()

        probability = 40.0

        probability += min(

            adx,

            50,

        )

        if ema["bullish"] or ema["bearish"]:

            probability += 10

        return round(

            min(

                probability,

                100,

            ),

            2,

        )

    # ======================================================
    # REVERSAL PROBABILITY
    # ======================================================

    def reversal_probability(

        self,

    ) -> float:

        rsi = self.rsi().iloc[-1]

        macd_hist = self.macd()["histogram"].iloc[-1]

        probability = 0.0

        if rsi > 75 or rsi < 25:

            probability += 40

        if abs(

            macd_hist,

        ) < 0.10:

            probability += 30

        if self.adx().iloc[-1] < 20:

            probability += 20

        return round(

            min(

                probability,

                100,

            ),

            2,

        )

    # ======================================================
    # FALSE BREAKOUT DETECTOR
    # ======================================================

    def false_breakout_probability(

        self,

    ) -> float:

        bb = self.bollinger_bands()

        width = bb["width"].iloc[-1]

        volume_ratio = (

            self.volume.iloc[-1]

            /

            self.volume.rolling(

                20,

            ).mean().iloc[-1]

        )

        probability = 0.0

        if width < 0.05:

            probability += 35

        if volume_ratio < 1.20:

            probability += 35

        if self.adx().iloc[-1] < 20:

            probability += 20

        return round(

            min(

                probability,

                100,

            ),

            2,

        )

    # ======================================================
    # AI REGIME SCORE
    # ======================================================

    def regime_score(

        self,

    ) -> Dict:

        return {

            "regime":

                self.classify_regime(),

            "confidence":

                self.regime_confidence(),

            "bull_score":

                self.bull_score(),

            "bear_score":

                self.bear_score(),

            "transition":

                self.transition_probability(),

            "continuation":

                self.continuation_probability(),

            "reversal":

                self.reversal_probability(),

            "false_breakout":

                self.false_breakout_probability(),

        }
        # ======================================================
    # VOLUME REGIME
    # ======================================================

    def volume_regime(

        self,

    ) -> Dict:

        current = float(

            self.volume.iloc[-1]

        )

        average = float(

            self.volume.rolling(

                20,

            ).mean().iloc[-1]

        )

        ratio = current / average if average else 1.0

        if ratio >= 2.0:

            regime = "VERY_HIGH"

        elif ratio >= 1.5:

            regime = "HIGH"

        elif ratio >= 0.8:

            regime = "NORMAL"

        elif ratio >= 0.5:

            regime = "LOW"

        else:

            regime = "VERY_LOW"

        return {

            "current": current,

            "average": average,

            "ratio": round(ratio, 2),

            "regime": regime,

        }

    # ======================================================
    # MARKET HEALTH
    # ======================================================

    def market_health(

        self,

    ) -> float:

        trend = self.trend_score()

        momentum = self.momentum_score()

        volume = self.volume_regime()["ratio"] * 30

        health = (

            trend * 0.45

            +

            momentum * 0.35

            +

            min(volume, 100) * 0.20

        )

        return round(

            min(

                health,

                100,

            ),

            2,

        )

    # ======================================================
    # INSTITUTIONAL PARTICIPATION
    # ======================================================

    def institutional_participation(

        self,

    ) -> float:

        volume = self.volume_regime()["ratio"]

        atr = (

            self.atr().iloc[-1]

            /

            self.close.iloc[-1]

        ) * 100

        score = volume * 40

        if 1.5 <= atr <= 4:

            score += 30

        if self.adx().iloc[-1] >= 25:

            score += 30

        return round(

            min(

                score,

                100,

            ),

            2,

        )

    # ======================================================
    # MARKET BREADTH CONFIRMATION
    # ======================================================

    def breadth_confirmation(

        self,

        advancing: int,

        declining: int,

    ) -> Dict:

        total = max(

            advancing + declining,

            1,

        )

        ratio = advancing / total

        confirmed = ratio >= 0.60

        return {

            "advancing": advancing,

            "declining": declining,

            "ratio": round(ratio, 2),

            "confirmed": confirmed,

        }

    # ======================================================
    # TREND EXHAUSTION
    # ======================================================

    def trend_exhaustion(

        self,

    ) -> float:

        rsi = self.rsi().iloc[-1]

        adx = self.adx().iloc[-1]

        probability = 0.0

        if rsi > 75:

            probability += 40

        elif rsi < 25:

            probability += 40

        if adx > 45:

            probability += 35

        macd_hist = abs(

            self.macd()["histogram"].iloc[-1]

        )

        if macd_hist < 0.10:

            probability += 15

        return round(

            min(

                probability,

                100,

            ),

            2,

        )

    # ======================================================
    # LIQUIDITY QUALITY
    # ======================================================

    def liquidity_quality(

        self,

    ) -> Dict:

        avg_volume = float(

            self.volume.rolling(

                20,

            ).mean().iloc[-1]

        )

        atr_percent = (

            self.atr().iloc[-1]

            /

            self.close.iloc[-1]

        ) * 100

        score = 50.0

        if avg_volume > 1_000_000:

            score += 30

        if atr_percent < 4:

            score += 20

        return {

            "average_volume": avg_volume,

            "atr_percent": round(

                atr_percent,

                2,

            ),

            "score": round(

                min(

                    score,

                    100,

                ),

                2,

            ),

        }

    # ======================================================
    # SMART WARNINGS
    # ======================================================

    def warnings(

        self,

    ) -> List[str]:

        warnings = []

        if self.volatility_state() == VolatilityState.EXTREME:

            warnings.append(

                "Extreme market volatility."

            )

        if self.false_breakout_probability() > 60:

            warnings.append(

                "High false breakout probability."

            )

        if self.trend_exhaustion() > 70:

            warnings.append(

                "Trend appears exhausted."

            )

        if self.volume_regime()["ratio"] < 0.80:

            warnings.append(

                "Below-average trading volume."

            )

        return warnings

    # ======================================================
    # MARKET QUALITY SCORE
    # ======================================================

    def market_quality(

        self,

    ) -> Dict:

        health = self.market_health()

        liquidity = self.liquidity_quality()["score"]

        participation = self.institutional_participation()

        quality = (

            health * 0.45

            +

            liquidity * 0.25

            +

            participation * 0.30

        )

        return {

            "health": health,

            "liquidity": liquidity,

            "institutional": participation,

            "quality": round(

                min(

                    quality,

                    100,

                ),

                2,

            ),

            "warnings": self.warnings(),

        }
        # ======================================================
    # MULTI-TIMEFRAME REGIME CONFIRMATION
    # ======================================================

    def multi_timeframe_confirmation(

        self,

        timeframe_scores: Dict[str, float],

    ) -> Dict:

        weights = {

            "5m": 0.10,

            "15m": 0.15,

            "30m": 0.20,

            "1h": 0.20,

            "4h": 0.20,

            "1d": 0.15,

        }

        score = 0.0

        total_weight = 0.0

        confirmations = 0

        for tf, value in timeframe_scores.items():

            weight = weights.get(tf, 0.10)

            total_weight += weight

            score += value * weight

            if value >= 70:

                confirmations += 1

        if total_weight == 0:

            average = 50.0

        else:

            average = score / total_weight

        return {

            "score": round(average, 2),

            "confirmations": confirmations,

            "total": len(timeframe_scores),

            "confirmed": confirmations >= max(1, len(timeframe_scores) // 2),

        }

    # ======================================================
    # SECTOR REGIME COMPARISON
    # ======================================================

    def compare_sector_regime(

        self,

        market_score: float,

        sector_score: float,

    ) -> Dict:

        alpha = sector_score - market_score

        if alpha >= 15:

            status = "OUTPERFORMING"

        elif alpha <= -15:

            status = "UNDERPERFORMING"

        else:

            status = "INLINE"

        return {

            "market": round(market_score, 2),

            "sector": round(sector_score, 2),

            "alpha": round(alpha, 2),

            "status": status,

        }

    # ======================================================
    # RELATIVE STRENGTH
    # ======================================================

    def relative_strength(

        self,

        benchmark: pd.Series,

        period: int = 20,

    ) -> Dict:

        asset_return = (

            self.close.iloc[-1]

            /

            self.close.iloc[-period]

            - 1

        ) * 100

        benchmark_return = (

            benchmark.iloc[-1]

            /

            benchmark.iloc[-period]

            - 1

        ) * 100

        rs = asset_return - benchmark_return

        return {

            "asset_return": round(asset_return, 2),

            "benchmark_return": round(benchmark_return, 2),

            "relative_strength": round(rs, 2),

            "outperforming": rs > 0,

        }

    # ======================================================
    # RISK ON / RISK OFF
    # ======================================================

    def risk_environment(

        self,

        vix: float,

    ) -> Dict:

        if vix < 15:

            state = "RISK_ON"

            score = 90

        elif vix < 20:

            state = "MODERATE"

            score = 70

        elif vix < 30:

            state = "CAUTION"

            score = 45

        else:

            state = "RISK_OFF"

            score = 20

        return {

            "state": state,

            "vix": round(vix, 2),

            "score": score,

        }

    # ======================================================
    # VOLATILITY EXPANSION
    # ======================================================

    def volatility_expansion(

        self,

    ) -> Dict:

        atr = self.atr()

        current = atr.iloc[-1]

        average = atr.tail(20).mean()

        ratio = current / average if average else 1

        expanding = ratio > 1.20

        return {

            "ratio": round(ratio, 2),

            "expanding": expanding,

        }

    # ======================================================
    # MARKET CYCLE
    # ======================================================

    def market_cycle(

        self,

    ) -> Dict:

        trend = self.trend_score()

        momentum = self.momentum_score()

        if trend >= 80 and momentum >= 70:

            cycle = "MARKUP"

        elif trend >= 60:

            cycle = "ACCUMULATION"

        elif trend < 40 and momentum < 40:

            cycle = "MARKDOWN"

        else:

            cycle = "DISTRIBUTION"

        return {

            "cycle": cycle,

            "trend": trend,

            "momentum": momentum,

        }

    # ======================================================
    # AI CONFIDENCE REFINEMENT
    # ======================================================

    def refined_confidence(

        self,

        base_confidence: float,

        mtf_score: float,

        market_quality: float,

    ) -> float:

        confidence = (

            base_confidence * 0.60

            +

            mtf_score * 0.20

            +

            market_quality * 0.20

        )

        return round(

            min(

                confidence,

                99,

            ),

            2,

        )

    # ======================================================
    # INSTITUTIONAL MARKET SCORE
    # ======================================================

    def institutional_market_score(

        self,

    ) -> float:

        quality = self.market_quality()["quality"]

        participation = self.institutional_participation()

        trend = self.trend_score()

        score = (

            quality * 0.40

            +

            participation * 0.35

            +

            trend * 0.25

        )

        return round(

            min(

                score,

                100,

            ),

            2,

        )
        # ======================================================
    # ENTRY WINDOW
    # ======================================================

    def entry_window(

        self,

    ) -> Dict:

        trend = self.trend_score()

        momentum = self.momentum_score()

        volume = self.volume_regime()["ratio"]

        score = (

            trend * 0.45

            +

            momentum * 0.35

            +

            min(volume, 2.0) / 2.0 * 100 * 0.20

        )

        if score >= 85:

            window = "EXCELLENT"

        elif score >= 70:

            window = "GOOD"

        elif score >= 55:

            window = "AVERAGE"

        else:

            window = "POOR"

        return {

            "window": window,

            "score": round(score, 2),

        }

    # ======================================================
    # EXIT WINDOW
    # ======================================================

    def exit_window(

        self,

    ) -> Dict:

        reversal = self.reversal_probability()

        exhaustion = self.trend_exhaustion()

        score = (

            reversal * 0.60

            +

            exhaustion * 0.40

        )

        if score >= 75:

            signal = "EXIT_NOW"

        elif score >= 60:

            signal = "TRAIL_STOP"

        elif score >= 40:

            signal = "PARTIAL_BOOKING"

        else:

            signal = "HOLD"

        return {

            "signal": signal,

            "score": round(score, 2),

        }

    # ======================================================
    # BREAKOUT PROBABILITY
    # ======================================================

    def breakout_probability(

        self,

    ) -> float:

        trend = self.trend_score()

        adx = self.adx().iloc[-1]

        volume = self.volume_regime()["ratio"]

        bb_width = self.bollinger_bands()["width"].iloc[-1]

        probability = (

            trend * 0.40

            +

            min(adx, 50) * 2 * 0.30

            +

            min(volume, 2) / 2 * 100 * 0.20

        )

        if bb_width < 0.05:

            probability += 10

        return round(

            min(

                probability,

                100,

            ),

            2,

        )

    # ======================================================
    # PULLBACK PROBABILITY
    # ======================================================

    def pullback_probability(

        self,

    ) -> float:

        rsi = self.rsi().iloc[-1]

        probability = 20.0

        if rsi > 70:

            probability += 45

        elif rsi > 60:

            probability += 25

        if self.trend_strength() == TrendStrength.STRONG:

            probability += 15

        elif self.trend_strength() == TrendStrength.VERY_STRONG:

            probability += 25

        return round(

            min(

                probability,

                100,

            ),

            2,

        )

    # ======================================================
    # TREND CONTINUATION AI
    # ======================================================

    def trend_continuation_ai(

        self,

    ) -> Dict:

        continuation = self.continuation_probability()

        breakout = self.breakout_probability()

        confidence = (

            continuation * 0.60

            +

            breakout * 0.40

        )

        return {

            "continuation": continuation,

            "breakout": breakout,

            "confidence": round(confidence, 2),

        }

    # ======================================================
    # INSTITUTIONAL TIMING
    # ======================================================

    def institutional_timing(

        self,

    ) -> Dict:

        participation = self.institutional_participation()

        volume = self.volume_regime()["ratio"]

        trend = self.trend_score()

        score = (

            participation * 0.50

            +

            min(volume, 2) / 2 * 100 * 0.20

            +

            trend * 0.30

        )

        if score >= 85:

            timing = "ACCUMULATION"

        elif score >= 70:

            timing = "EARLY_ENTRY"

        elif score >= 55:

            timing = "WAIT_CONFIRMATION"

        else:

            timing = "AVOID"

        return {

            "timing": timing,

            "score": round(score, 2),

        }

    # ======================================================
    # TRADE READINESS SCORE
    # ======================================================

    def trade_readiness(

        self,

    ) -> Dict:

        entry = self.entry_window()["score"]

        quality = self.market_quality()["quality"]

        institutional = self.institutional_market_score()

        score = (

            entry * 0.35

            +

            quality * 0.35

            +

            institutional * 0.30

        )

        if score >= 85:

            readiness = "READY"

        elif score >= 70:

            readiness = "NEAR_READY"

        elif score >= 55:

            readiness = "WATCH"

        else:

            readiness = "NOT_READY"

        return {

            "status": readiness,

            "score": round(score, 2),

        }

    # ======================================================
    # SMART MARKET TIMING ENGINE
    # ======================================================

    def market_timing_engine(

        self,

    ) -> Dict:

        return {

            "entry":

                self.entry_window(),

            "exit":

                self.exit_window(),

            "breakout_probability":

                self.breakout_probability(),

            "pullback_probability":

                self.pullback_probability(),

            "trend_ai":

                self.trend_continuation_ai(),

            "institutional":

                self.institutional_timing(),

            "trade_readiness":

                self.trade_readiness(),

        }
        # ======================================================
    # COMPLETE MARKET ANALYSIS
    # ======================================================

    def analyze(
        self,
    ) -> MarketRegimeResult:

        self.validate()

        regime = self.classify_regime()

        confidence = self.regime_confidence()

        score = self.trend_score()

        trend_strength = self.trend_strength()

        volatility = self.volatility_state()

        indicators = {

            "ema_alignment": self.ema_alignment(),

            "phase": self.phase_score(),

            "market_quality": self.market_quality(),

            "timing": self.market_timing_engine(),

            "regime": self.regime_score(),

        }

        reasons = self.generate_reasons()

        warnings = self.warnings()

        self.result = MarketRegimeResult(

            regime=regime,

            confidence=confidence,

            score=score,

            trend_strength=trend_strength,

            volatility=volatility,

            reasons=reasons,

            warnings=warnings,

            indicators=indicators,

        )

        return self.result

    # ======================================================
    # EXPLAINABLE AI
    # ======================================================

    def explain(
        self,
        result: Optional[MarketRegimeResult] = None,
    ) -> Dict:

        if result is None:
            result = self.result

        if result is None:
            return {}

        return {

            "symbol": self.symbol,

            "market_regime": result.regime.value,

            "confidence": result.confidence,

            "trend_strength": result.trend_strength.value,

            "volatility": result.volatility.value,

            "score": result.score,

            "reasons": list(result.reasons),

            "warnings": list(result.warnings),

            "timing": result.indicators.get(

                "timing",

                {},

            ),

        }

    # ======================================================
    # MARKET ALERTS
    # ======================================================

    def alerts(
        self,
    ) -> List[str]:

        alerts = []

        readiness = self.trade_readiness()

        if readiness["status"] == "READY":

            alerts.append(

                "High probability trading environment."

            )

        if self.breakout_probability() >= 80:

            alerts.append(

                "Breakout probability is very high."

            )

        if self.pullback_probability() >= 75:

            alerts.append(

                "Pullback likely. Wait for retracement."

            )

        if self.false_breakout_probability() >= 70:

            alerts.append(

                "High probability of false breakout."

            )

        alerts.extend(

            self.warnings()

        )

        return list(

            dict.fromkeys(alerts)

        )

    # ======================================================
    # AI RECOMMENDATION
    # ======================================================

    def recommendation(
        self,
    ) -> str:

        regime = self.classify_regime()

        readiness = self.trade_readiness()["status"]

        if regime in (

            MarketRegime.STRONG_BULL,

            MarketRegime.BULL,

        ):

            if readiness == "READY":

                return "LOOK FOR LONG SETUPS"

            return "WAIT FOR CONFIRMATION"

        if regime in (

            MarketRegime.STRONG_BEAR,

            MarketRegime.BEAR,

        ):

            if readiness == "READY":

                return "LOOK FOR SHORT SETUPS"

            return "WAIT FOR RALLY"

        if regime == MarketRegime.SIDEWAYS:

            return "RANGE TRADING ONLY"

        if regime == MarketRegime.VOLATILE:

            return "REDUCE POSITION SIZE"

        return "NO ACTION"

    # ======================================================
    # DASHBOARD SUMMARY
    # ======================================================

    def dashboard(
        self,
    ) -> Dict:

        if self.result is None:

            self.analyze()

        return {

            "symbol": self.symbol,

            "market_regime": self.result.regime.value,

            "confidence": self.result.confidence,

            "trend_strength":

                self.result.trend_strength.value,

            "volatility":

                self.result.volatility.value,

            "market_quality":

                self.market_quality(),

            "timing":

                self.market_timing_engine(),

            "recommendation":

                self.recommendation(),

            "alerts":

                self.alerts(),

        }

    # ======================================================
    # HISTORY
    # ======================================================

    def add_history(
        self,
        history: List[MarketRegimeResult],
    ) -> List[MarketRegimeResult]:

        history.append(

            self.result,

        )

        return history

    # ======================================================
    # PERFORMANCE ANALYTICS
    # ======================================================

    def analytics(
        self,
        history: List[MarketRegimeResult],
    ) -> Dict:

        if not history:

            return {}

        confidence = [

            item.confidence

            for item in history

        ]

        scores = [

            item.score

            for item in history

        ]

        return {

            "samples":

                len(history),

            "average_confidence":

                round(

                    float(

                        np.mean(

                            confidence,

                        )

                    ),

                    2,

                ),

            "average_score":

                round(

                    float(

                        np.mean(

                            scores,

                        )

                    ),

                    2,

                ),

            "highest_score":

                round(

                    max(scores),

                    2,

                ),

            "lowest_score":

                round(

                    min(scores),

                    2,

                ),

        }

    # ======================================================
    # REASON GENERATOR
    # ======================================================

    def generate_reasons(
        self,
    ) -> List[str]:

        reasons = []

        ema = self.ema_alignment()

        if ema["bullish"]:

            reasons.append(

                "Bullish EMA alignment."

            )

        elif ema["bearish"]:

            reasons.append(

                "Bearish EMA alignment."

            )

        if self.adx().iloc[-1] >= 25:

            reasons.append(

                "Strong trend strength."

            )

        if self.volume_regime()["ratio"] >= 1.5:

            reasons.append(

                "Above-average trading volume."

            )

        if self.market_health() >= 80:

            reasons.append(

                "Healthy market structure."

            )

        return reasons
        # ======================================================
    # DATAFRAME EXPORT
    # ======================================================

    def to_dataframe(
        self,
        history: List[MarketRegimeResult],
    ) -> pd.DataFrame:

        rows = []

        for item in history:

            rows.append({

                "Symbol": self.symbol,

                "Regime": item.regime.value,

                "Confidence": item.confidence,

                "Score": item.score,

                "Trend Strength": item.trend_strength.value,

                "Volatility": item.volatility.value,

                "Reasons": ", ".join(item.reasons),

                "Warnings": ", ".join(item.warnings),

            })

        return pd.DataFrame(rows)

    # ======================================================
    # JSON EXPORT
    # ======================================================

    def export_json(
        self,
        history: List[MarketRegimeResult],
        path: str,
    ) -> None:

        records = self.to_dataframe(
            history,
        ).to_dict(
            orient="records",
        )

        with open(
            path,
            "w",
            encoding="utf-8",
        ) as fp:

            json.dump(
                records,
                fp,
                indent=4,
            )

    # ======================================================
    # CSV EXPORT
    # ======================================================

    def export_csv(
        self,
        history: List[MarketRegimeResult],
        path: str,
    ) -> None:

        self.to_dataframe(
            history,
        ).to_csv(
            path,
            index=False,
        )

    # ======================================================
    # SERIALIZE RESULT
    # ======================================================

    def to_dict(
        self,
        result: Optional[MarketRegimeResult] = None,
    ) -> Dict:

        if result is None:

            result = self.result

        if result is None:

            return {}

        return {

            "symbol": self.symbol,

            "regime": result.regime.value,

            "confidence": result.confidence,

            "score": result.score,

            "trend_strength": result.trend_strength.value,

            "volatility": result.volatility.value,

            "reasons": result.reasons,

            "warnings": result.warnings,

            "indicators": result.indicators,

        }

    # ======================================================
    # RUNTIME METRICS
    # ======================================================

    def runtime_metrics(
        self,
        start_time,
    ) -> Dict:

        runtime = (

            pd.Timestamp.now()

            -

            start_time

        ).total_seconds() * 1000

        return {

            "execution_ms":

                round(runtime, 2),

            "bars":

                len(self.data),

            "symbol":

                self.symbol,

        }

    # ======================================================
    # LOGGER
    # ======================================================

    def log(
        self,
        message: str,
    ) -> None:

        timestamp = pd.Timestamp.now().strftime(

            "%H:%M:%S"

        )

        print(

            f"[{timestamp}] {message}"

        )

    # ======================================================
    # BATCH ANALYSIS
    # ======================================================

    def batch_analyze(
        self,
        datasets: Dict[str, pd.DataFrame],
    ) -> Dict[str, MarketRegimeResult]:

        results = {}

        for symbol, data in datasets.items():

            engine = MarketRegimeEngine()

            engine.load(

                symbol,

                data,

            )

            results[symbol] = engine.analyze()

        return results

    # ======================================================
    # MULTI SYMBOL SCANNER
    # ======================================================

    def scan_market(
        self,
        datasets: Dict[str, pd.DataFrame],
    ) -> pd.DataFrame:

        rows = []

        results = self.batch_analyze(

            datasets,

        )

        for symbol, result in results.items():

            rows.append({

                "Symbol":

                    symbol,

                "Regime":

                    result.regime.value,

                "Confidence":

                    result.confidence,

                "Score":

                    result.score,

                "Trend":

                    result.trend_strength.value,

                "Volatility":

                    result.volatility.value,

            })

        df = pd.DataFrame(rows)

        if not df.empty:

            df = df.sort_values(

                by=[

                    "Score",

                    "Confidence",

                ],

                ascending=False,

            )

        return df

    # ======================================================
    # STATUS
    # ======================================================

    def status(
        self,
    ) -> Dict:

        return {

            "symbol":

                self.symbol,

            "loaded":

                self.data is not None,

            "bars":

                0 if self.data is None else len(self.data),

            "version":

                self.version(),

        }
        # ======================================================
    # COMPLETE EXECUTION PIPELINE
    # ======================================================

    def execute(
        self,
    ) -> Dict:

        start_time = pd.Timestamp.now()

        result = self.analyze()

        output = {
            "result": result,
            "summary": self.dashboard(),
            "recommendation": self.recommendation(),
            "alerts": self.alerts(),
            "timing": self.market_timing_engine(),
            "quality": self.market_quality(),
            "analytics": self.analytics([result]),
            "runtime": self.runtime_metrics(start_time),
        }

        return output

    # ======================================================
    # REPORT GENERATOR
    # ======================================================

    def generate_report(
        self,
    ) -> Dict:

        if self.result is None:
            self.analyze()

        return {
            "symbol": self.symbol,
            "generated_at": pd.Timestamp.now().isoformat(),
            "version": self.version(),
            "dashboard": self.dashboard(),
            "recommendation": self.recommendation(),
            "alerts": self.alerts(),
            "market_quality": self.market_quality(),
            "regime": self.regime_score(),
            "timing": self.market_timing_engine(),
            "explanation": self.explain(),
        }

    # ======================================================
    # MARKET SUMMARY API
    # ======================================================

    def market_summary(
        self,
    ) -> Dict:

        if self.result is None:
            self.analyze()

        return {
            "symbol": self.symbol,
            "regime": self.result.regime.value,
            "confidence": self.result.confidence,
            "score": self.result.score,
            "recommendation": self.recommendation(),
            "alerts": self.alerts(),
        }

    # ======================================================
    # SAVE REPORT
    # ======================================================

    def save_report(
        self,
        path: str,
    ) -> None:

        report = self.generate_report()

        with open(
            path,
            "w",
            encoding="utf-8",
        ) as fp:

            json.dump(
                report,
                fp,
                indent=4,
                default=str,
            )

    # ======================================================
    # RESET ENGINE
    # ======================================================

    def reset(
        self,
    ) -> None:

        self.data = None
        self.symbol = ""
        self.result = None

    # ======================================================
    # VERSION
    # ======================================================

    @staticmethod
    def version() -> str:

        return "4.0.0"

    # ======================================================
    # ENGINE INFORMATION
    # ======================================================

    def info(
        self,
    ) -> Dict:

        return {
            "engine": "MarketRegimeEngine",
            "version": self.version(),
            "powered_by": "StockVersity Scanner Pro AI",
            "author": "StockVersity",
            "supports": [
                "Bull Market Detection",
                "Bear Market Detection",
                "Sideways Detection",
                "Volatility Analysis",
                "Market Timing",
                "Institutional Scoring",
                "Trade Readiness",
                "Batch Analysis",
                "Multi-Symbol Scanner",
                "Explainable AI",
            ],
        }

    # ======================================================
    # HEALTH CHECK
    # ======================================================

    def health_check(
        self,
    ) -> Dict:

        return {
            "status": "OK",
            "data_loaded": self.data is not None,
            "symbol": self.symbol,
            "bars": 0 if self.data is None else len(self.data),
            "version": self.version(),
        }

    # ======================================================
    # STRING REPRESENTATION
    # ======================================================

    def __repr__(
        self,
    ) -> str:

        return (
            f"MarketRegimeEngine("
            f"symbol='{self.symbol}', "
            f"version='{self.version()}')"
        )

    __str__ = __repr__