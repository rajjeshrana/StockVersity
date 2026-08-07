from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

import numpy as np
import pandas as pd


# ======================================================
# SENTIMENT ENUMS
# ======================================================

class Sentiment(Enum):
    VERY_BULLISH = "Very Bullish"
    BULLISH = "Bullish"
    NEUTRAL = "Neutral"
    BEARISH = "Bearish"
    VERY_BEARISH = "Very Bearish"


class FearGreed(Enum):
    EXTREME_FEAR = "Extreme Fear"
    FEAR = "Fear"
    NEUTRAL = "Neutral"
    GREED = "Greed"
    EXTREME_GREED = "Extreme Greed"


class MoneyFlow(Enum):
    STRONG_INFLOW = "Strong Inflow"
    INFLOW = "Inflow"
    NEUTRAL = "Neutral"
    OUTFLOW = "Outflow"
    STRONG_OUTFLOW = "Strong Outflow"


# ======================================================
# RESULT MODEL
# ======================================================

@dataclass
class MarketSentimentResult:

    symbol: str

    sentiment: Sentiment

    confidence: float

    score: float

    fear_greed: FearGreed

    money_flow: MoneyFlow

    reasons: List[str] = field(default_factory=list)

    warnings: List[str] = field(default_factory=list)

    indicators: Dict = field(default_factory=dict)


# ======================================================
# MARKET SENTIMENT ENGINE
# ======================================================

class MarketSentimentEngine:

    def __init__(self):

        self.symbol: str = ""

        self.data: Optional[pd.DataFrame] = None

        self.result: Optional[
            MarketSentimentResult
        ] = None

    # ======================================================
    # LOAD DATA
    # ======================================================

    def load(

        self,

        symbol: str,

        data: pd.DataFrame,

    ):

        self.symbol = symbol

        self.data = data.copy()

        self.validate()

        return self

    # ======================================================
    # VALIDATE
    # ======================================================

    def validate(self):

        if self.data is None:

            raise ValueError("Data not loaded.")

        required = [

            "Open",

            "High",

            "Low",

            "Close",

            "Volume",

        ]

        missing = [

            col

            for col in required

            if col not in self.data.columns

        ]

        if missing:

            raise ValueError(

                f"Missing columns: {missing}"

            )

    # ======================================================
    # PROPERTIES
    # ======================================================

    @property
    def open(self):

        return self.data["Open"]

    @property
    def high(self):

        return self.data["High"]

    @property
    def low(self):

        return self.data["Low"]

    @property
    def close(self):

        return self.data["Close"]

    @property
    def volume(self):

        return self.data["Volume"]

    # ======================================================
    # BASIC INDICATORS
    # ======================================================

    def sma(

        self,

        period: int,

    ):

        return self.close.rolling(period).mean()

    def ema(

        self,

        period: int,

    ):

        return self.close.ewm(

            span=period,

            adjust=False,

        ).mean()

    def rsi(

        self,

        period: int = 14,

    ):

        delta = self.close.diff()

        gain = delta.clip(lower=0)

        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(period).mean()

        avg_loss = loss.rolling(period).mean()

        rs = avg_gain / avg_loss.replace(0, np.nan)

        return 100 - (100 / (1 + rs))

    def atr(

        self,

        period: int = 14,

    ):

        tr = pd.concat(

            [

                self.high - self.low,

                (self.high - self.close.shift()).abs(),

                (self.low - self.close.shift()).abs(),

            ],

            axis=1,

        ).max(axis=1)

        return tr.rolling(period).mean()

    # ======================================================
    # RESET
    # ======================================================

    def reset(self):

        self.symbol = ""

        self.data = None

        self.result = None
            # ======================================================
    # MACD
    # ======================================================

    def macd(

        self,

        fast: int = 12,

        slow: int = 26,

        signal: int = 9,

    ) -> Dict[str, pd.Series]:

        fast_ema = self.ema(fast)

        slow_ema = self.ema(slow)

        macd_line = fast_ema - slow_ema

        signal_line = macd_line.ewm(

            span=signal,

            adjust=False,

        ).mean()

        histogram = macd_line - signal_line

        return {

            "macd": macd_line,

            "signal": signal_line,

            "histogram": histogram,

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

        plus_dm = pd.Series(

            np.where(

                (up_move > down_move) & (up_move > 0),

                up_move,

                0,

            ),

            index=self.data.index,

        )

        minus_dm = pd.Series(

            np.where(

                (down_move > up_move) & (down_move > 0),

                down_move,

                0,

            ),

            index=self.data.index,

        )

        tr = pd.concat(

            [

                self.high - self.low,

                (self.high - self.close.shift()).abs(),

                (self.low - self.close.shift()).abs(),

            ],

            axis=1,

        ).max(axis=1)

        atr = tr.rolling(period).mean()

        plus_di = (

            100

            * plus_dm.rolling(period).sum()

            / atr

        )

        minus_di = (

            100

            * minus_dm.rolling(period).sum()

            / atr

        )

        dx = (

            (

                plus_di - minus_di

            ).abs()

            /

            (

                plus_di + minus_di

            )

        ) * 100

        return dx.rolling(period).mean()

    # ======================================================
    # ON BALANCE VOLUME
    # ======================================================

    def obv(

        self,

    ) -> pd.Series:

        direction = np.sign(

            self.close.diff().fillna(0)

        )

        return (

            direction

            * self.volume

        ).cumsum()

    # ======================================================
    # CHAIKIN MONEY FLOW
    # ======================================================

    def cmf(

        self,

        period: int = 20,

    ) -> pd.Series:

        multiplier = (

            (

                (self.close - self.low)

                -

                (self.high - self.close)

            )

            /

            (

                self.high - self.low

            ).replace(

                0,

                np.nan,

            )

        )

        money_flow = multiplier * self.volume

        return (

            money_flow.rolling(period).sum()

            /

            self.volume.rolling(period).sum()

        )

    # ======================================================
    # MONEY FLOW INDEX
    # ======================================================

    def mfi(

        self,

        period: int = 14,

    ) -> pd.Series:

        typical = (

            self.high

            + self.low

            + self.close

        ) / 3

        money = typical * self.volume

        positive = money.where(

            typical.diff() > 0,

            0,

        )

        negative = money.where(

            typical.diff() < 0,

            0,

        )

        pos_sum = positive.rolling(period).sum()

        neg_sum = negative.rolling(period).sum()

        ratio = pos_sum / neg_sum.replace(

            0,

            np.nan,

        )

        return 100 - (

            100

            /

            (

                1 + ratio

            )

        )

    # ======================================================
    # ACCUMULATION DISTRIBUTION LINE
    # ======================================================

    def adl(

        self,

    ) -> pd.Series:

        clv = (

            (

                (self.close - self.low)

                -

                (self.high - self.close)

            )

            /

            (

                self.high - self.low

            ).replace(

                0,

                np.nan,

            )

        )

        return (

            clv

            * self.volume

        ).cumsum()

    # ======================================================
    # VWAP
    # ======================================================

    def vwap(

        self,

    ) -> pd.Series:

        typical = (

            self.high

            + self.low

            + self.close

        ) / 3

        return (

            (typical * self.volume).cumsum()

            /

            self.volume.cumsum()

        )

    # ======================================================
    # VOLUME ANALYTICS
    # ======================================================

    def volume_statistics(

        self,

    ) -> Dict:

        current = float(

            self.volume.iloc[-1]

        )

        average20 = float(

            self.volume.rolling(

                20,

            ).mean().iloc[-1]

        )

        ratio = (

            current / average20

            if average20

            else 1.0

        )

        return {

            "current": current,

            "average20": average20,

            "ratio": round(ratio, 2),

            "high_volume": ratio >= 1.5,

        }

    # ======================================================
    # PRICE MOMENTUM
    # ======================================================

    def price_momentum(

        self,

        period: int = 20,

    ) -> float:

        momentum = (

            (

                self.close.iloc[-1]

                /

                self.close.iloc[-period]

            )

            - 1

        ) * 100

        return round(

            float(momentum),

            2,

        )
        # ======================================================
    # BULLISH SENTIMENT SCORE
    # ======================================================

    def bullish_score(

        self,

    ) -> float:

        score = 0.0

        rsi = self.rsi().iloc[-1]

        macd = self.macd()

        cmf = self.cmf().iloc[-1]

        mfi = self.mfi().iloc[-1]

        momentum = self.price_momentum()

        volume = self.volume_statistics()["ratio"]

        if rsi > 60:

            score += 20

        elif rsi > 50:

            score += 10

        if macd["macd"].iloc[-1] > macd["signal"].iloc[-1]:

            score += 20

        if cmf > 0:

            score += 15

        if mfi > 60:

            score += 15

        if momentum > 0:

            score += min(momentum, 20)

        score += min(volume * 10, 10)

        return round(min(score, 100), 2)

    # ======================================================
    # BEARISH SENTIMENT SCORE
    # ======================================================

    def bearish_score(

        self,

    ) -> float:

        score = 0.0

        rsi = self.rsi().iloc[-1]

        macd = self.macd()

        cmf = self.cmf().iloc[-1]

        mfi = self.mfi().iloc[-1]

        momentum = self.price_momentum()

        volume = self.volume_statistics()["ratio"]

        if rsi < 40:

            score += 20

        elif rsi < 50:

            score += 10

        if macd["macd"].iloc[-1] < macd["signal"].iloc[-1]:

            score += 20

        if cmf < 0:

            score += 15

        if mfi < 40:

            score += 15

        if momentum < 0:

            score += min(abs(momentum), 20)

        score += min(volume * 10, 10)

        return round(min(score, 100), 2)

    # ======================================================
    # FEAR & GREED INDEX
    # ======================================================

    def fear_greed_index(

        self,

    ) -> FearGreed:

        score = self.bullish_score()

        if score >= 85:

            return FearGreed.EXTREME_GREED

        if score >= 65:

            return FearGreed.GREED

        if score >= 45:

            return FearGreed.NEUTRAL

        if score >= 25:

            return FearGreed.FEAR

        return FearGreed.EXTREME_FEAR

    # ======================================================
    # MONEY FLOW CLASSIFICATION
    # ======================================================

    def money_flow_state(

        self,

    ) -> MoneyFlow:

        cmf = self.cmf().iloc[-1]

        if cmf >= 0.25:

            return MoneyFlow.STRONG_INFLOW

        if cmf >= 0.05:

            return MoneyFlow.INFLOW

        if cmf <= -0.25:

            return MoneyFlow.STRONG_OUTFLOW

        if cmf <= -0.05:

            return MoneyFlow.OUTFLOW

        return MoneyFlow.NEUTRAL

    # ======================================================
    # VOLUME SENTIMENT
    # ======================================================

    def volume_sentiment(

        self,

    ) -> Dict:

        stats = self.volume_statistics()

        obv = self.obv()

        rising = obv.iloc[-1] > obv.iloc[-5]

        return {

            "volume_ratio": stats["ratio"],

            "obv_rising": rising,

            "bullish":

                stats["ratio"] > 1.20 and rising,

        }

    # ======================================================
    # MOMENTUM SENTIMENT
    # ======================================================

    def momentum_sentiment(

        self,

    ) -> Dict:

        momentum = self.price_momentum()

        rsi = self.rsi().iloc[-1]

        adx = self.adx().iloc[-1]

        score = 50.0

        score += momentum

        score += (rsi - 50)

        score += min(adx, 30)

        score = max(

            0,

            min(

                score,

                100,

            ),

        )

        return {

            "score": round(score, 2),

            "positive": score >= 60,

        }

    # ======================================================
    # SENTIMENT CONFIDENCE
    # ======================================================

    def sentiment_confidence(

        self,

    ) -> float:

        bull = self.bullish_score()

        bear = self.bearish_score()

        difference = abs(

            bull - bear,

        )

        confidence = 55 + difference * 0.45

        return round(

            min(

                confidence,

                99,

            ),

            2,

        )

    # ======================================================
    # MARKET SENTIMENT
    # ======================================================

    def classify_sentiment(

        self,

    ) -> Sentiment:

        bull = self.bullish_score()

        bear = self.bearish_score()

        if bull >= 85:

            return Sentiment.VERY_BULLISH

        if bull >= 65:

            return Sentiment.BULLISH

        if bear >= 85:

            return Sentiment.VERY_BEARISH

        if bear >= 65:

            return Sentiment.BEARISH

        return Sentiment.NEUTRAL
        # ======================================================
    # INSTITUTIONAL BUYING / SELLING
    # ======================================================

    def institutional_activity(

        self,

    ) -> Dict:

        volume_ratio = self.volume_statistics()["ratio"]

        cmf = self.cmf().iloc[-1]

        adl = self.adl()

        adl_trend = adl.iloc[-1] - adl.iloc[-5]

        buying = (

            volume_ratio > 1.50

            and cmf > 0.10

            and adl_trend > 0

        )

        selling = (

            volume_ratio > 1.50

            and cmf < -0.10

            and adl_trend < 0

        )

        score = 50.0

        if buying:

            score += 35

        elif selling:

            score -= 35

        score += cmf * 40

        score = max(

            0,

            min(

                score,

                100,

            ),

        )

        return {

            "buying": buying,

            "selling": selling,

            "score": round(score, 2),

        }

    # ======================================================
    # SMART MONEY ANALYSIS
    # ======================================================

    def smart_money_activity(

        self,

    ) -> Dict:

        cmf = self.cmf().iloc[-1]

        obv = self.obv()

        obv_slope = obv.iloc[-1] - obv.iloc[-10]

        score = 50.0

        score += cmf * 60

        if obv_slope > 0:

            score += 20

        else:

            score -= 20

        score = max(

            0,

            min(

                score,

                100,

            ),

        )

        return {

            "score": round(score, 2),

            "accumulating": score >= 65,

            "distributing": score <= 35,

        }

    # ======================================================
    # ACCUMULATION / DISTRIBUTION
    # ======================================================

    def accumulation_distribution(

        self,

    ) -> Dict:

        adl = self.adl()

        slope = adl.iloc[-1] - adl.iloc[-20]

        if slope > 0:

            phase = "ACCUMULATION"

        elif slope < 0:

            phase = "DISTRIBUTION"

        else:

            phase = "NEUTRAL"

        return {

            "phase": phase,

            "slope": round(float(slope), 2),

        }

    # ======================================================
    # RETAIL VS INSTITUTIONAL PRESSURE
    # ======================================================

    def market_pressure(

        self,

    ) -> Dict:

        smart = self.smart_money_activity()["score"]

        sentiment = self.bullish_score()

        institutional = smart * 0.60

        retail = sentiment * 0.40

        pressure = institutional - retail

        if pressure > 15:

            dominance = "INSTITUTIONAL"

        elif pressure < -15:

            dominance = "RETAIL"

        else:

            dominance = "BALANCED"

        return {

            "institutional": round(institutional, 2),

            "retail": round(retail, 2),

            "pressure": round(pressure, 2),

            "dominance": dominance,

        }

    # ======================================================
    # BUYING EXHAUSTION
    # ======================================================

    def buying_exhaustion(

        self,

    ) -> float:

        rsi = self.rsi().iloc[-1]

        mfi = self.mfi().iloc[-1]

        probability = 0.0

        if rsi > 75:

            probability += 45

        if mfi > 80:

            probability += 35

        if self.price_momentum() > 10:

            probability += 20

        return round(

            min(

                probability,

                100,

            ),

            2,

        )

    # ======================================================
    # SELLING CLIMAX
    # ======================================================

    def selling_climax(

        self,

    ) -> float:

        rsi = self.rsi().iloc[-1]

        mfi = self.mfi().iloc[-1]

        probability = 0.0

        if rsi < 25:

            probability += 45

        if mfi < 20:

            probability += 35

        if self.price_momentum() < -10:

            probability += 20

        return round(

            min(

                probability,

                100,

            ),

            2,

        )

    # ======================================================
    # AI SENTIMENT PROBABILITY
    # ======================================================

    def sentiment_probability(

        self,

    ) -> Dict:

        bull = self.bullish_score()

        bear = self.bearish_score()

        total = max(

            bull + bear,

            1,

        )

        return {

            "bullish": round(

                bull / total * 100,

                2,

            ),

            "bearish": round(

                bear / total * 100,

                2,

            ),

            "confidence":

                self.sentiment_confidence(),

        }

    # ======================================================
    # MARKET PARTICIPATION
    # ======================================================

    def participation_score(

        self,

    ) -> float:

        volume = self.volume_statistics()["ratio"]

        adx = self.adx().iloc[-1]

        cmf = self.cmf().iloc[-1]

        score = (

            min(volume, 2.0) / 2.0 * 40

            +

            min(adx, 50) / 50 * 40

            +

            max(

                min(

                    (cmf + 1) * 10,

                    20,

                ),

                0,

            )

        )

        return round(

            min(

                score,

                100,

            ),

            2,

        )
        # ======================================================
    # NEWS IMPACT SCORE
    # ======================================================

    def news_impact_score(

        self,

        news_sentiment: float = 50.0,

    ) -> Dict:

        score = max(

            0.0,

            min(

                news_sentiment,

                100.0,

            ),

        )

        if score >= 75:

            impact = "VERY_POSITIVE"

        elif score >= 60:

            impact = "POSITIVE"

        elif score >= 40:

            impact = "NEUTRAL"

        elif score >= 25:

            impact = "NEGATIVE"

        else:

            impact = "VERY_NEGATIVE"

        return {

            "score": round(score, 2),

            "impact": impact,

        }

    # ======================================================
    # GAP SENTIMENT
    # ======================================================

    def gap_sentiment(

        self,

    ) -> Dict:

        previous_close = self.close.iloc[-2]

        today_open = self.open.iloc[-1]

        gap = (

            (today_open - previous_close)

            / previous_close

        ) * 100

        if gap >= 2:

            sentiment = "STRONG_GAP_UP"

        elif gap > 0:

            sentiment = "GAP_UP"

        elif gap <= -2:

            sentiment = "STRONG_GAP_DOWN"

        elif gap < 0:

            sentiment = "GAP_DOWN"

        else:

            sentiment = "FLAT"

        return {

            "gap_percent": round(gap, 2),

            "sentiment": sentiment,

        }

    # ======================================================
    # VOLATILITY SENTIMENT
    # ======================================================

    def volatility_sentiment(

        self,

    ) -> Dict:

        atr_percent = (

            self.atr().iloc[-1]

            /

            self.close.iloc[-1]

        ) * 100

        if atr_percent >= 5:

            state = "HIGH_VOLATILITY"

            score = 30

        elif atr_percent >= 3:

            state = "MODERATE_VOLATILITY"

            score = 60

        else:

            state = "LOW_VOLATILITY"

            score = 90

        return {

            "atr_percent": round(

                atr_percent,

                2,

            ),

            "state": state,

            "score": score,

        }

    # ======================================================
    # TREND QUALITY
    # ======================================================

    def trend_quality(

        self,

    ) -> float:

        adx = self.adx().iloc[-1]

        momentum = abs(

            self.price_momentum(),

        )

        volume = self.volume_statistics()["ratio"]

        quality = (

            min(

                adx,

                50,

            )

            * 0.50

        )

        quality += min(

            momentum,

            20,

        ) * 2.0

        quality += min(

            volume,

            2.0,

        ) * 10

        return round(

            min(

                quality,

                100,

            ),

            2,

        )

    # ======================================================
    # MULTI FACTOR SENTIMENT
    # ======================================================

    def sentiment_fusion(

        self,

        news_score: float = 50,

    ) -> Dict:

        technical = self.bullish_score()

        money = self.participation_score()

        volatility = self.volatility_sentiment()["score"]

        total = (

            technical * 0.40

            +

            money * 0.30

            +

            news_score * 0.20

            +

            volatility * 0.10

        )

        return {

            "score": round(total, 2),

            "technical": technical,

            "money_flow": money,

            "news": news_score,

            "volatility": volatility,

        }

    # ======================================================
    # RISK SENTIMENT
    # ======================================================

    def risk_sentiment(

        self,

    ) -> Dict:

        volatility = self.volatility_sentiment()["score"]

        participation = self.participation_score()

        risk = 100 - (

            volatility * 0.50

            +

            participation * 0.50

        )

        risk = max(

            0,

            min(

                risk,

                100,

            ),

        )

        if risk >= 75:

            level = "HIGH_RISK"

        elif risk >= 50:

            level = "MEDIUM_RISK"

        else:

            level = "LOW_RISK"

        return {

            "score": round(risk, 2),

            "level": level,

        }

    # ======================================================
    # PANIC / EUPHORIA
    # ======================================================

    def emotional_state(

        self,

    ) -> Dict:

        greed = self.fear_greed_index()

        buying = self.buying_exhaustion()

        selling = self.selling_climax()

        if greed == FearGreed.EXTREME_GREED:

            state = "EUPHORIA"

        elif greed == FearGreed.EXTREME_FEAR:

            state = "PANIC"

        elif buying >= 80:

            state = "OVERHEATED"

        elif selling >= 80:

            state = "CAPITULATION"

        else:

            state = "NORMAL"

        return {

            "state": state,

            "buying_exhaustion": buying,

            "selling_climax": selling,

        }

    # ======================================================
    # SENTIMENT QUALITY
    # ======================================================

    def sentiment_quality(

        self,

    ) -> Dict:

        fusion = self.sentiment_fusion()

        confidence = self.sentiment_confidence()

        participation = self.participation_score()

        quality = (

            fusion["score"] * 0.50

            +

            confidence * 0.25

            +

            participation * 0.25

        )

        return {

            "quality": round(

                quality,

                2,

            ),

            "confidence": confidence,

            "participation": participation,

            "fusion": fusion["score"],

        }
        # ======================================================
    # MULTI-TIMEFRAME SENTIMENT
    # ======================================================

    def multi_timeframe_sentiment(

        self,

        timeframe_scores: Dict[str, float],

    ) -> Dict:

        weights = {

            "5m": 0.10,

            "15m": 0.15,

            "30m": 0.15,

            "1h": 0.20,

            "4h": 0.20,

            "1d": 0.20,

        }

        total_score = 0.0

        total_weight = 0.0

        confirmations = 0

        for tf, score in timeframe_scores.items():

            weight = weights.get(

                tf,

                0.10,

            )

            total_score += score * weight

            total_weight += weight

            if score >= 65:

                confirmations += 1

        average = (

            total_score / total_weight

            if total_weight

            else 50.0

        )

        return {

            "score": round(average, 2),

            "confirmations": confirmations,

            "timeframes": len(timeframe_scores),

            "confirmed":

                confirmations >= max(1, len(timeframe_scores) // 2),

        }

    # ======================================================
    # SECTOR SENTIMENT
    # ======================================================

    def sector_sentiment(

        self,

        sector_score: float,

        market_score: float,

    ) -> Dict:

        alpha = sector_score - market_score

        if alpha >= 15:

            status = "STRONGER_THAN_MARKET"

        elif alpha <= -15:

            status = "WEAKER_THAN_MARKET"

        else:

            status = "INLINE"

        return {

            "sector": round(sector_score, 2),

            "market": round(market_score, 2),

            "alpha": round(alpha, 2),

            "status": status,

        }

    # ======================================================
    # RELATIVE STRENGTH SENTIMENT
    # ======================================================

    def relative_strength_sentiment(

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

            "asset_return":

                round(asset_return, 2),

            "benchmark_return":

                round(benchmark_return, 2),

            "relative_strength":

                round(rs, 2),

            "outperforming":

                rs > 0,

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

            state = "BULLISH"

            score = 75

        elif vix < 30:

            state = "CAUTION"

            score = 50

        else:

            state = "RISK_OFF"

            score = 20

        return {

            "state": state,

            "vix": round(vix, 2),

            "score": score,

        }

    # ======================================================
    # MARKET BREADTH SENTIMENT
    # ======================================================

    def breadth_sentiment(

        self,

        advancing: int,

        declining: int,

    ) -> Dict:

        total = max(

            advancing + declining,

            1,

        )

        ratio = advancing / total

        score = ratio * 100

        if ratio >= 0.70:

            state = "VERY_BULLISH"

        elif ratio >= 0.55:

            state = "BULLISH"

        elif ratio >= 0.45:

            state = "NEUTRAL"

        elif ratio >= 0.30:

            state = "BEARISH"

        else:

            state = "VERY_BEARISH"

        return {

            "advancing": advancing,

            "declining": declining,

            "ratio": round(ratio, 2),

            "score": round(score, 2),

            "state": state,

        }

    # ======================================================
    # CONFIDENCE REFINEMENT
    # ======================================================

    def refined_confidence(

        self,

        mtf_score: float,

        quality_score: float,

    ) -> float:

        confidence = (

            self.sentiment_confidence() * 0.60

            +

            mtf_score * 0.20

            +

            quality_score * 0.20

        )

        return round(

            min(

                confidence,

                99,

            ),

            2,

        )

    # ======================================================
    # INSTITUTIONAL SENTIMENT INDEX
    # ======================================================

    def institutional_sentiment_index(

        self,

    ) -> Dict:

        institutional = self.institutional_activity()["score"]

        smart = self.smart_money_activity()["score"]

        participation = self.participation_score()

        score = (

            institutional * 0.40

            +

            smart * 0.35

            +

            participation * 0.25

        )

        return {

            "score": round(score, 2),

            "institutional": round(institutional, 2),

            "smart_money": round(smart, 2),

            "participation": round(participation, 2),

        }

    # ======================================================
    # SMART SENTIMENT TIMING
    # ======================================================

    def sentiment_timing(

        self,

    ) -> Dict:

        quality = self.sentiment_quality()["quality"]

        risk = self.risk_sentiment()["score"]

        confidence = self.sentiment_confidence()

        timing = (

            quality * 0.50

            +

            confidence * 0.30

            +

            (100 - risk) * 0.20

        )

        if timing >= 85:

            signal = "STRONG_BUY"

        elif timing >= 70:

            signal = "BUY"

        elif timing >= 55:

            signal = "WAIT"

        elif timing >= 40:

            signal = "CAUTION"

        else:

            signal = "AVOID"

        return {

            "signal": signal,

            "score": round(timing, 2),

            "quality": quality,

            "risk": risk,

            "confidence": confidence,

        }
        # ======================================================
    # SENTIMENT ENTRY ENGINE
    # ======================================================

    def entry_signal(

        self,

    ) -> Dict:

        sentiment = self.classify_sentiment()

        timing = self.sentiment_timing()

        participation = self.participation_score()

        confidence = self.sentiment_confidence()

        score = (

            confidence * 0.40

            +

            timing["score"] * 0.35

            +

            participation * 0.25

        )

        if score >= 85:

            signal = "STRONG_ENTRY"

        elif score >= 70:

            signal = "ENTRY"

        elif score >= 55:

            signal = "WATCH"

        else:

            signal = "NO_ENTRY"

        return {

            "signal": signal,

            "score": round(score, 2),

            "sentiment": sentiment.value,

        }

    # ======================================================
    # SENTIMENT EXIT ENGINE
    # ======================================================

    def exit_signal(

        self,

    ) -> Dict:

        buying = self.buying_exhaustion()

        selling = self.selling_climax()

        risk = self.risk_sentiment()["score"]

        score = max(

            buying,

            selling,

            risk,

        )

        if score >= 85:

            signal = "EXIT_NOW"

        elif score >= 70:

            signal = "PARTIAL_EXIT"

        elif score >= 55:

            signal = "TRAIL_STOP"

        else:

            signal = "HOLD"

        return {

            "signal": signal,

            "score": round(score, 2),

        }

    # ======================================================
    # BUYING OPPORTUNITY
    # ======================================================

    def buying_opportunity(

        self,

    ) -> Dict:

        bull = self.bullish_score()

        smart = self.smart_money_activity()["score"]

        timing = self.sentiment_timing()["score"]

        score = (

            bull * 0.40

            +

            smart * 0.35

            +

            timing * 0.25

        )

        return {

            "available": score >= 70,

            "score": round(score, 2),

        }

    # ======================================================
    # SELLING OPPORTUNITY
    # ======================================================

    def selling_opportunity(

        self,

    ) -> Dict:

        bear = self.bearish_score()

        risk = self.risk_sentiment()["score"]

        exhaustion = self.buying_exhaustion()

        score = (

            bear * 0.45

            +

            risk * 0.30

            +

            exhaustion * 0.25

        )

        return {

            "available": score >= 70,

            "score": round(score, 2),

        }

    # ======================================================
    # AI RECOMMENDATION
    # ======================================================

    def recommendation(

        self,

    ) -> str:

        sentiment = self.classify_sentiment()

        entry = self.entry_signal()["signal"]

        if sentiment in (

            Sentiment.VERY_BULLISH,

            Sentiment.BULLISH,

        ):

            if entry in (

                "STRONG_ENTRY",

                "ENTRY",

            ):

                return "LOOK FOR LONG SETUPS"

            return "WAIT FOR CONFIRMATION"

        if sentiment in (

            Sentiment.VERY_BEARISH,

            Sentiment.BEARISH,

        ):

            return "AVOID LONGS / LOOK FOR SHORTS"

        return "NEUTRAL MARKET"

    # ======================================================
    # SENTIMENT ALERTS
    # ======================================================

    def alerts(

        self,

    ) -> List[str]:

        alerts = []

        if self.buying_exhaustion() >= 80:

            alerts.append(

                "Buying exhaustion detected."

            )

        if self.selling_climax() >= 80:

            alerts.append(

                "Selling climax detected."

            )

        if self.smart_money_activity()["accumulating"]:

            alerts.append(

                "Institutional accumulation detected."

            )

        if self.smart_money_activity()["distributing"]:

            alerts.append(

                "Institutional distribution detected."

            )

        if self.risk_sentiment()["level"] == "HIGH_RISK":

            alerts.append(

                "High risk environment."

            )

        return alerts

    # ======================================================
    # DASHBOARD
    # ======================================================

    def dashboard(

        self,

    ) -> Dict:

        return {

            "symbol": self.symbol,

            "sentiment":

                self.classify_sentiment().value,

            "confidence":

                self.sentiment_confidence(),

            "fear_greed":

                self.fear_greed_index().value,

            "money_flow":

                self.money_flow_state().value,

            "entry":

                self.entry_signal(),

            "exit":

                self.exit_signal(),

            "recommendation":

                self.recommendation(),

            "alerts":

                self.alerts(),

        }

    # ======================================================
    # EXPLAINABLE AI
    # ======================================================

    def explain(

        self,

    ) -> Dict:

        return {

            "symbol": self.symbol,

            "sentiment":

                self.classify_sentiment().value,

            "confidence":

                self.sentiment_confidence(),

            "bullish_score":

                self.bullish_score(),

            "bearish_score":

                self.bearish_score(),

            "fear_greed":

                self.fear_greed_index().value,

            "money_flow":

                self.money_flow_state().value,

            "institutional":

                self.institutional_activity(),

            "smart_money":

                self.smart_money_activity(),

            "recommendation":

                self.recommendation(),

            "alerts":

                self.alerts(),

        }
        # ======================================================
    # COMPLETE SENTIMENT ANALYSIS
    # ======================================================

    def analyze(

        self,

    ) -> MarketSentimentResult:

        self.validate()

        sentiment = self.classify_sentiment()

        confidence = self.sentiment_confidence()

        score = self.sentiment_quality()["quality"]

        fear_greed = self.fear_greed_index()

        money_flow = self.money_flow_state()

        indicators = {

            "bullish_score": self.bullish_score(),

            "bearish_score": self.bearish_score(),

            "participation": self.participation_score(),

            "quality": self.sentiment_quality(),

            "institutional": self.institutional_activity(),

            "smart_money": self.smart_money_activity(),

            "timing": self.sentiment_timing(),

            "entry": self.entry_signal(),

            "exit": self.exit_signal(),

        }

        reasons = self.generate_reasons()

        warnings = self.alerts()

        self.result = MarketSentimentResult(

            symbol=self.symbol,

            sentiment=sentiment,

            confidence=confidence,

            score=score,

            fear_greed=fear_greed,

            money_flow=money_flow,

            reasons=reasons,

            warnings=warnings,

            indicators=indicators,

        )

        return self.result

    # ======================================================
    # HISTORY
    # ======================================================

    def add_history(

        self,

        history: List[MarketSentimentResult],

    ) -> List[MarketSentimentResult]:

        if self.result is not None:

            history.append(

                self.result,

            )

        return history

    # ======================================================
    # ANALYTICS
    # ======================================================

    def analytics(

        self,

        history: List[MarketSentimentResult],

    ) -> Dict:

        if not history:

            return {}

        scores = [

            item.score

            for item in history

        ]

        confidence = [

            item.confidence

            for item in history

        ]

        bullish = sum(

            1

            for item in history

            if item.sentiment in (

                Sentiment.BULLISH,

                Sentiment.VERY_BULLISH,

            )

        )

        bearish = sum(

            1

            for item in history

            if item.sentiment in (

                Sentiment.BEARISH,

                Sentiment.VERY_BEARISH,

            )

        )

        return {

            "samples": len(history),

            "average_score":

                round(float(np.mean(scores)), 2),

            "average_confidence":

                round(float(np.mean(confidence)), 2),

            "highest_score":

                round(max(scores), 2),

            "lowest_score":

                round(min(scores), 2),

            "bullish_count": bullish,

            "bearish_count": bearish,

        }

    # ======================================================
    # BATCH ANALYSIS
    # ======================================================

    def batch_analyze(

        self,

        datasets: Dict[str, pd.DataFrame],

    ) -> Dict[str, MarketSentimentResult]:

        results = {}

        for symbol, data in datasets.items():

            engine = MarketSentimentEngine()

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

                "Sentiment":

                    result.sentiment.value,

                "Confidence":

                    result.confidence,

                "Score":

                    result.score,

                "Fear & Greed":

                    result.fear_greed.value,

                "Money Flow":

                    result.money_flow.value,

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
    # SUMMARY REPORT
    # ======================================================

    def report(

        self,

    ) -> Dict:

        if self.result is None:

            self.analyze()

        return {

            "symbol": self.symbol,

            "sentiment":

                self.result.sentiment.value,

            "confidence":

                self.result.confidence,

            "score":

                self.result.score,

            "fear_greed":

                self.result.fear_greed.value,

            "money_flow":

                self.result.money_flow.value,

            "recommendation":

                self.recommendation(),

            "alerts":

                self.alerts(),

            "dashboard":

                self.dashboard(),

            "explanation":

                self.explain(),

        }

    # ======================================================
    # EXECUTION PIPELINE
    # ======================================================

    def execute(

        self,

    ) -> Dict:

        result = self.analyze()

        return {

            "result": result,

            "dashboard": self.dashboard(),

            "report": self.report(),

            "recommendation": self.recommendation(),

            "alerts": self.alerts(),

            "analytics": self.analytics([result]),

        }

    # ======================================================
    # REASON GENERATOR
    # ======================================================

    def generate_reasons(

        self,

    ) -> List[str]:

        reasons = []

        if self.bullish_score() > self.bearish_score():

            reasons.append(

                "Bullish technical structure."

            )

        else:

            reasons.append(

                "Bearish technical structure."

            )

        if self.smart_money_activity()["accumulating"]:

            reasons.append(

                "Institutional accumulation detected."

            )

        if self.money_flow_state() in (

            MoneyFlow.INFLOW,

            MoneyFlow.STRONG_INFLOW,

        ):

            reasons.append(

                "Positive money flow."

            )

        if self.participation_score() >= 70:

            reasons.append(

                "Strong market participation."

            )

        return reasons
        # ======================================================
    # DATAFRAME EXPORT
    # ======================================================

    def to_dataframe(

        self,

        history: List[MarketSentimentResult],

    ) -> pd.DataFrame:

        rows = []

        for item in history:

            rows.append({

                "Symbol": item.symbol,

                "Sentiment": item.sentiment.value,

                "Confidence": item.confidence,

                "Score": item.score,

                "FearGreed": item.fear_greed.value,

                "MoneyFlow": item.money_flow.value,

                "Reasons": "; ".join(item.reasons),

                "Warnings": "; ".join(item.warnings),

            })

        return pd.DataFrame(rows)

    # ======================================================
    # JSON EXPORT
    # ======================================================

    def export_json(

        self,

        history: List[MarketSentimentResult],

        filename: str,

    ) -> None:

        df = self.to_dataframe(

            history,

        )

        records = df.to_dict(

            orient="records",

        )

        with open(

            filename,

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

        history: List[MarketSentimentResult],

        filename: str,

    ) -> None:

        self.to_dataframe(

            history,

        ).to_csv(

            filename,

            index=False,

        )

    # ======================================================
    # SERIALIZE RESULT
    # ======================================================

    def to_dict(

        self,

        result: Optional[
            MarketSentimentResult
        ] = None,

    ) -> Dict:

        if result is None:

            result = self.result

        if result is None:

            return {}

        return {

            "symbol": result.symbol,

            "sentiment": result.sentiment.value,

            "confidence": result.confidence,

            "score": result.score,

            "fear_greed": result.fear_greed.value,

            "money_flow": result.money_flow.value,

            "reasons": result.reasons,

            "warnings": result.warnings,

            "indicators": result.indicators,

        }

    # ======================================================
    # RUNTIME METRICS
    # ======================================================

    def runtime_metrics(

        self,

        start_time: pd.Timestamp,

    ) -> Dict:

        elapsed = (

            pd.Timestamp.now()

            -

            start_time

        ).total_seconds() * 1000

        return {

            "execution_ms":

                round(elapsed, 2),

            "bars_processed":

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

            "%H:%M:%S",

        )

        print(

            f"[{timestamp}] "

            f"[MarketSentiment] "

            f"{message}"

        )

    # ======================================================
    # STATUS
    # ======================================================

    def status(

        self,

    ) -> Dict:

        return {

            "engine":

                "MarketSentimentEngine",

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
    # PRODUCTION UTILITIES
    # ======================================================

    @staticmethod

    def version(

    ) -> str:

        return "4.0.0"

    @staticmethod

    def supported_features(

    ) -> List[str]:

        return [

            "Bullish Sentiment",

            "Bearish Sentiment",

            "Fear & Greed",

            "Money Flow Analysis",

            "Institutional Activity",

            "Smart Money Detection",

            "Market Participation",

            "Risk Sentiment",

            "Gap Analysis",

            "News Impact",

            "Sentiment Timing",

            "Multi-Timeframe Sentiment",

            "Batch Analysis",

            "Multi-Symbol Scanner",

            "Explainable AI",

            "JSON Export",

            "CSV Export",

        ]

    @staticmethod

    def engine_info(

    ) -> Dict:

        return {

            "name":

                "MarketSentimentEngine",

            "version":

                "4.0.0",

            "powered_by":

                "StockVersity Scanner Pro AI",

            "supports":

                MarketSentimentEngine.supported_features(),

        }
        # ======================================================
    # ENHANCED EXECUTION PIPELINE
    # ======================================================

    def execute(

        self,

    ) -> Dict:

        start_time = pd.Timestamp.now()

        result = self.analyze()

        return {

            "result": result,

            "dashboard": self.dashboard(),

            "report": self.report(),

            "recommendation": self.recommendation(),

            "alerts": self.alerts(),

            "analytics": self.analytics([result]),

            "runtime": self.runtime_metrics(start_time),

            "engine": self.engine_info(),

        }

    # ======================================================
    # SAVE REPORT
    # ======================================================

    def save_report(

        self,

        filename: str,

    ) -> None:

        report = self.report()

        with open(

            filename,

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
    # HEALTH CHECK
    # ======================================================

    def health_check(

        self,

    ) -> Dict:

        return {

            "status":

                "OK",

            "engine":

                "MarketSentimentEngine",

            "symbol":

                self.symbol,

            "loaded":

                self.data is not None,

            "rows":

                0 if self.data is None else len(self.data),

            "version":

                self.version(),

        }

    # ======================================================
    # RESET ENGINE
    # ======================================================

    def reset(

        self,

    ) -> None:

        self.symbol = ""

        self.data = None

        self.result = None

    # ======================================================
    # SUMMARY API
    # ======================================================

    def summary(

        self,

    ) -> Dict:

        if self.result is None:

            self.analyze()

        return {

            "symbol":

                self.result.symbol,

            "sentiment":

                self.result.sentiment.value,

            "confidence":

                self.result.confidence,

            "score":

                self.result.score,

            "fear_greed":

                self.result.fear_greed.value,

            "money_flow":

                self.result.money_flow.value,

            "recommendation":

                self.recommendation(),

        }

    # ======================================================
    # COMPLETE ENGINE SNAPSHOT
    # ======================================================

    def snapshot(

        self,

    ) -> Dict:

        return {

            "status":

                self.status(),

            "summary":

                self.summary(),

            "dashboard":

                self.dashboard(),

            "report":

                self.report(),

            "engine":

                self.engine_info(),

        }

    # ======================================================
    # PRINT SUMMARY
    # ======================================================

    def print_summary(

        self,

    ) -> None:

        summary = self.summary()

        print("=" * 60)

        print("Market Sentiment Summary")

        print("=" * 60)

        print(

            f"Symbol      : {summary['symbol']}"

        )

        print(

            f"Sentiment   : {summary['sentiment']}"

        )

        print(

            f"Confidence  : {summary['confidence']:.2f}%"

        )

        print(

            f"Score       : {summary['score']:.2f}"

        )

        print(

            f"Fear/Greed  : {summary['fear_greed']}"

        )

        print(

            f"Money Flow  : {summary['money_flow']}"

        )

        print(

            f"Recommendation : {summary['recommendation']}"

        )

        print("=" * 60)

    # ======================================================
    # STRING REPRESENTATION
    # ======================================================

    def __repr__(

        self,

    ) -> str:

        return (

            "MarketSentimentEngine("

            f"symbol='{self.symbol}', "

            f"version='{self.version()}'"

            ")"

        )

    __str__ = __repr__