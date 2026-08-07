from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from backend.ai.market_regime_engine import (
    MarketRegimeEngine,
    MarketRegime,
)

from backend.ai.market_sentiment_engine import (
    MarketSentimentEngine,
    Sentiment,
)

from backend.ai.opportunity_ranker import (
    OpportunityRanker,
)

from backend.ai.trading_decision_engine import (
    TradingDecisionEngine,
)


# ======================================================
# PREDICTION ENUMS
# ======================================================

class Prediction(Enum):

    STRONG_BUY = "Strong Buy"

    BUY = "Buy"

    ACCUMULATE = "Accumulate"

    HOLD = "Hold"

    REDUCE = "Reduce"

    SELL = "Sell"

    STRONG_SELL = "Strong Sell"


class TrendDirection(Enum):

    STRONG_UP = "Strong Up"

    UP = "Up"

    SIDEWAYS = "Sideways"

    DOWN = "Down"

    STRONG_DOWN = "Strong Down"


class ConfidenceLevel(Enum):

    VERY_HIGH = "Very High"

    HIGH = "High"

    MEDIUM = "Medium"

    LOW = "Low"

    VERY_LOW = "Very Low"


# ======================================================
# RESULT MODEL
# ======================================================

@dataclass
class MarketPredictionResult:

    symbol: str

    prediction: Prediction

    confidence: float

    probability: float

    trend: TrendDirection

    confidence_level: ConfidenceLevel

    expected_return: float

    expected_drawdown: float

    risk_reward: float

    reasons: List[str] = field(default_factory=list)

    warnings: List[str] = field(default_factory=list)

    indicators: Dict = field(default_factory=dict)


# ======================================================
# MARKET PREDICTION ENGINE
# ======================================================

class MarketPredictionEngine:

    def __init__(self):

        self.symbol: str = ""

        self.data: Optional[pd.DataFrame] = None

        self.result: Optional[
            MarketPredictionResult
        ] = None

        self.regime_engine = MarketRegimeEngine()

        self.sentiment_engine = MarketSentimentEngine()

        self.ranker = OpportunityRanker()

        self.decision_engine = TradingDecisionEngine()

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

        self.regime_engine.load(

            symbol,

            data,

        )

        self.sentiment_engine.load(

            symbol,

            data,

        )

        return self

    # ======================================================
    # VALIDATE
    # ======================================================

    def validate(

        self,

    ):

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

        missing = [

            c

            for c in required

            if c not in self.data.columns

        ]

        if missing:

            raise ValueError(

                f"Missing columns: {missing}"

            )

    # ======================================================
    # OHLCV PROPERTIES
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
    # INDICATORS
    # ======================================================

    def ema(

        self,

        period: int,

    ):

        return self.close.ewm(

            span=period,

            adjust=False,

        ).mean()

    def sma(

        self,

        period: int,

    ):

        return self.close.rolling(

            period,

        ).mean()

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

        return tr.rolling(

            period,

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

        rs = avg_gain / avg_loss.replace(

            0,

            np.nan,

        )

        return 100 - (

            100

            /

            (

                1 + rs

            )

        )

    # ======================================================
    # RESET
    # ======================================================

    def reset(

        self,

    ):

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

                (up_move > down_move)

                &

                (up_move > 0),

                up_move,

                0,

            ),

            index=self.data.index,

        )

        minus_dm = pd.Series(

            np.where(

                (down_move > up_move)

                &

                (down_move > 0),

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

            *

            plus_dm.rolling(period).sum()

            /

            atr

        )

        minus_di = (

            100

            *

            minus_dm.rolling(period).sum()

            /

            atr

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
    # VOLATILITY SCORE
    # ======================================================

    def volatility_score(

        self,

    ) -> float:

        atr_percent = (

            self.atr().iloc[-1]

            /

            self.close.iloc[-1]

        ) * 100

        score = max(

            0,

            100 - atr_percent * 10,

        )

        return round(

            min(

                score,

                100,

            ),

            2,

        )

    # ======================================================
    # TREND SCORE
    # ======================================================

    def trend_score(

        self,

    ) -> float:

        ema20 = self.ema(20).iloc[-1]

        ema50 = self.ema(50).iloc[-1]

        ema200 = self.ema(200).iloc[-1]

        close = self.close.iloc[-1]

        score = 0.0

        if close > ema20:

            score += 20

        if ema20 > ema50:

            score += 35

        if ema50 > ema200:

            score += 45

        return round(

            min(

                score,

                100,

            ),

            2,

        )

    # ======================================================
    # MOMENTUM SCORE
    # ======================================================

    def momentum_score(

        self,

    ) -> float:

        rsi = self.rsi().iloc[-1]

        histogram = self.macd()["histogram"].iloc[-1]

        adx = self.adx().iloc[-1]

        score = (

            rsi * 0.45

            +

            min(

                adx,

                50,

            ) * 1.0

        )

        if histogram > 0:

            score += 10

        else:

            score -= 10

        return round(

            max(

                0,

                min(

                    score,

                    100,

                ),

            ),

            2,

        )

    # ======================================================
    # PROBABILITY ENGINE
    # ======================================================

    def probability_score(

        self,

    ) -> float:

        trend = self.trend_score()

        momentum = self.momentum_score()

        volatility = self.volatility_score()

        regime = self.regime_engine.regime_confidence()

        sentiment = self.sentiment_engine.sentiment_confidence()

        probability = (

            trend * 0.25

            +

            momentum * 0.20

            +

            volatility * 0.10

            +

            regime * 0.25

            +

            sentiment * 0.20

        )

        return round(

            min(

                probability,

                99,

            ),

            2,

        )

    # ======================================================
    # EXPECTED MOVE
    # ======================================================

    def expected_move(

        self,

        days: int = 5,

    ) -> Dict:

        atr = self.atr().iloc[-1]

        move = atr * np.sqrt(days)

        close = self.close.iloc[-1]

        return {

            "days": days,

            "expected_move": round(move, 2),

            "upper_target": round(close + move, 2),

            "lower_target": round(close - move, 2),

        }

    # ======================================================
    # RISK / REWARD
    # ======================================================

    def risk_reward_estimate(

        self,

    ) -> Dict:

        atr = self.atr().iloc[-1]

        risk = atr

        reward = atr * 2.5

        rr = reward / max(

            risk,

            0.01,

        )

        return {

            "risk": round(risk, 2),

            "reward": round(reward, 2),

            "risk_reward": round(rr, 2),

        }
        # ======================================================
    # AI BULLISH PROBABILITY
    # ======================================================

    def bullish_probability(

        self,

    ) -> float:

        trend = self.trend_score()

        momentum = self.momentum_score()

        sentiment = self.sentiment_engine.bullish_score()

        regime = self.regime_engine.regime_confidence()

        probability = (

            trend * 0.30 +

            momentum * 0.25 +

            sentiment * 0.25 +

            regime * 0.20

        )

        return round(

            max(

                0,

                min(

                    probability,

                    100,

                ),

            ),

            2,

        )

    # ======================================================
    # AI BEARISH PROBABILITY
    # ======================================================

    def bearish_probability(

        self,

    ) -> float:

        bullish = self.bullish_probability()

        bearish = 100 - bullish

        return round(

            bearish,

            2,

        )

    # ======================================================
    # TREND CLASSIFICATION
    # ======================================================

    def trend_direction(

        self,

    ) -> TrendDirection:

        score = self.trend_score()

        if score >= 90:

            return TrendDirection.STRONG_UP

        if score >= 70:

            return TrendDirection.UP

        if score >= 40:

            return TrendDirection.SIDEWAYS

        if score >= 20:

            return TrendDirection.DOWN

        return TrendDirection.STRONG_DOWN

    # ======================================================
    # CONFIDENCE LEVEL
    # ======================================================

    def confidence_level(

        self,

    ) -> ConfidenceLevel:

        confidence = self.probability_score()

        if confidence >= 90:

            return ConfidenceLevel.VERY_HIGH

        if confidence >= 75:

            return ConfidenceLevel.HIGH

        if confidence >= 60:

            return ConfidenceLevel.MEDIUM

        if confidence >= 40:

            return ConfidenceLevel.LOW

        return ConfidenceLevel.VERY_LOW

    # ======================================================
    # EXPECTED RETURN
    # ======================================================

    def expected_return(

        self,

        holding_days: int = 20,

    ) -> float:

        atr = self.atr().iloc[-1]

        probability = self.bullish_probability() / 100

        expected = (

            atr *

            np.sqrt(

                holding_days,

            ) *

            probability

        )

        return round(

            expected,

            2,

        )

    # ======================================================
    # EXPECTED DRAWDOWN
    # ======================================================

    def expected_drawdown(

        self,

        holding_days: int = 20,

    ) -> float:

        atr = self.atr().iloc[-1]

        probability = self.bearish_probability() / 100

        drawdown = (

            atr *

            np.sqrt(

                holding_days,

            ) *

            probability

        )

        return round(

            drawdown,

            2,

        )

    # ======================================================
    # WIN PROBABILITY
    # ======================================================

    def win_probability(

        self,

    ) -> float:

        probability = (

            self.bullish_probability() * 0.60 +

            self.probability_score() * 0.40

        )

        return round(

            min(

                probability,

                99,

            ),

            2,

        )

    # ======================================================
    # PREDICTION SCORE
    # ======================================================

    def prediction_score(

        self,

    ) -> float:

        probability = self.win_probability()

        rr = self.risk_reward_estimate()[

            "risk_reward"

        ]

        score = (

            probability * 0.70 +

            min(

                rr * 20,

                100,

            ) * 0.30

        )

        return round(

            min(

                score,

                100,

            ),

            2,

        )
        # ======================================================
    # AI PREDICTION DECISION
    # ======================================================

    def prediction(

        self,

    ) -> Prediction:

        score = self.prediction_score()

        if score >= 90:

            return Prediction.STRONG_BUY

        if score >= 75:

            return Prediction.BUY

        if score >= 60:

            return Prediction.ACCUMULATE

        if score >= 45:

            return Prediction.HOLD

        if score >= 30:

            return Prediction.REDUCE

        if score >= 15:

            return Prediction.SELL

        return Prediction.STRONG_SELL

    # ======================================================
    # RISK CLASSIFICATION
    # ======================================================

    def risk_classification(

        self,

    ) -> str:

        volatility = self.volatility_score()

        drawdown = self.expected_drawdown()

        probability = self.win_probability()

        score = (

            volatility * 0.30 +

            probability * 0.40 +

            (100 - drawdown) * 0.30

        )

        if score >= 85:

            return "Very Low"

        if score >= 70:

            return "Low"

        if score >= 55:

            return "Moderate"

        if score >= 40:

            return "High"

        return "Very High"

    # ======================================================
    # OPPORTUNITY GRADE
    # ======================================================

    def opportunity_grade(

        self,

    ) -> str:

        score = self.prediction_score()

        if score >= 95:

            return "A+"

        if score >= 85:

            return "A"

        if score >= 75:

            return "A-"

        if score >= 65:

            return "B+"

        if score >= 55:

            return "B"

        if score >= 45:

            return "C+"

        if score >= 35:

            return "C"

        return "D"

    # ======================================================
    # POSITION SIZE
    # ======================================================

    def recommended_position_size(

        self,

        capital: float,

        risk_percent: float = 1.0,

    ) -> Dict:

        risk_amount = (

            capital *

            risk_percent /

            100

        )

        atr = self.atr().iloc[-1]

        stop_distance = max(

            atr,

            0.01,

        )

        shares = int(

            risk_amount /

            stop_distance

        )

        investment = (

            shares *

            self.close.iloc[-1]

        )

        return {

            "capital": round(capital, 2),

            "risk_percent": risk_percent,

            "risk_amount": round(risk_amount, 2),

            "shares": shares,

            "investment": round(investment, 2),

        }

    # ======================================================
    # STOP LOSS
    # ======================================================

    def stop_loss(

        self,

        multiplier: float = 1.5,

    ) -> float:

        atr = self.atr().iloc[-1]

        sl = (

            self.close.iloc[-1]

            -

            atr * multiplier

        )

        return round(

            sl,

            2,

        )

    # ======================================================
    # TARGET PRICE
    # ======================================================

    def target_price(

        self,

        multiplier: float = 3.0,

    ) -> float:

        atr = self.atr().iloc[-1]

        target = (

            self.close.iloc[-1]

            +

            atr * multiplier

        )

        return round(

            target,

            2,

        )

    # ======================================================
    # MULTI-FACTOR AI SCORE
    # ======================================================

    def ai_score(

        self,

    ) -> Dict:

        trend = self.trend_score()

        momentum = self.momentum_score()

        volatility = self.volatility_score()

        probability = self.win_probability()

        sentiment = self.sentiment_engine.sentiment_confidence()

        regime = self.regime_engine.regime_confidence()

        overall = (

            trend * 0.20 +

            momentum * 0.20 +

            volatility * 0.10 +

            probability * 0.20 +

            sentiment * 0.15 +

            regime * 0.15

        )

        return {

            "trend": round(trend, 2),

            "momentum": round(momentum, 2),

            "volatility": round(volatility, 2),

            "probability": round(probability, 2),

            "sentiment": round(sentiment, 2),

            "regime": round(regime, 2),

            "overall": round(min(overall, 100), 2),

        }
        # ======================================================
    # MULTI-TIMEFRAME PREDICTION
    # ======================================================

    def multi_timeframe_prediction(

        self,

        higher_timeframe_probability: float = 70.0,

        lower_timeframe_probability: float = 70.0,

    ) -> Dict:

        current = self.win_probability()

        score = (

            current * 0.50 +

            higher_timeframe_probability * 0.30 +

            lower_timeframe_probability * 0.20

        )

        if score >= 85:

            signal = "Very Strong Alignment"

        elif score >= 70:

            signal = "Strong Alignment"

        elif score >= 55:

            signal = "Moderate Alignment"

        else:

            signal = "Weak Alignment"

        return {

            "current": round(current, 2),

            "higher_timeframe": round(

                higher_timeframe_probability,

                2,

            ),

            "lower_timeframe": round(

                lower_timeframe_probability,

                2,

            ),

            "combined_score": round(score, 2),

            "signal": signal,

        }

    # ======================================================
    # SECTOR RELATIVE PREDICTION
    # ======================================================

    def sector_relative_prediction(

        self,

        sector_strength: float = 70.0,

    ) -> Dict:

        stock = self.prediction_score()

        alpha = stock - sector_strength

        return {

            "stock_score": round(stock, 2),

            "sector_score": round(sector_strength, 2),

            "relative_strength": round(alpha, 2),

            "outperforming": alpha > 0,

        }

    # ======================================================
    # MARKET RELATIVE STRENGTH
    # ======================================================

    def market_relative_strength(

        self,

        market_score: float = 65.0,

    ) -> Dict:

        stock = self.prediction_score()

        rs = stock - market_score

        if rs >= 20:

            status = "Strong Outperformer"

        elif rs >= 10:

            status = "Outperformer"

        elif rs >= -10:

            status = "In Line"

        elif rs >= -20:

            status = "Underperformer"

        else:

            status = "Weak"

        return {

            "market_score": round(

                market_score,

                2,

            ),

            "stock_score": round(

                stock,

                2,

            ),

            "strength": round(

                rs,

                2,

            ),

            "status": status,

        }

    # ======================================================
    # PROBABILITY REFINEMENT
    # ======================================================

    def refined_probability(

        self,

    ) -> float:

        base = self.win_probability()

        ai = self.ai_score()["overall"]

        refined = (

            base * 0.70 +

            ai * 0.30

        )

        return round(

            min(

                refined,

                99,

            ),

            2,

        )

    # ======================================================
    # INSTITUTIONAL CONFIDENCE
    # ======================================================

    def institutional_confidence(

        self,

    ) -> float:

        institutional = self.sentiment_engine.institutional_activity()

        confidence = institutional.get(

            "score",

            50,

        )

        return round(

            confidence,

            2,

        )

    # ======================================================
    # AI CONVICTION SCORE
    # ======================================================

    def conviction_score(

        self,

    ) -> float:

        probability = self.refined_probability()

        confidence = self.institutional_confidence()

        sentiment = self.sentiment_engine.sentiment_confidence()

        conviction = (

            probability * 0.40 +

            confidence * 0.30 +

            sentiment * 0.30

        )

        return round(

            min(

                conviction,

                100,

            ),

            2,

        )

    # ======================================================
    # ENTRY TIMING
    # ======================================================

    def entry_timing(

        self,

    ) -> Dict:

        probability = self.refined_probability()

        conviction = self.conviction_score()

        if probability >= 85 and conviction >= 85:

            timing = "Immediate Entry"

        elif probability >= 70:

            timing = "Buy on Minor Pullback"

        elif probability >= 55:

            timing = "Wait for Confirmation"

        else:

            timing = "Avoid Entry"

        return {

            "timing": timing,

            "probability": probability,

            "conviction": conviction,

        }

    # ======================================================
    # EXIT TIMING
    # ======================================================

    def exit_timing(

        self,

    ) -> Dict:

        bearish = self.bearish_probability()

        if bearish >= 80:

            signal = "Immediate Exit"

        elif bearish >= 65:

            signal = "Partial Profit Booking"

        elif bearish >= 50:

            signal = "Trail Stop Loss"

        else:

            signal = "Hold Position"

        return {

            "bearish_probability": round(

                bearish,

                2,

            ),

            "action": signal,

        }
        # ======================================================
    # AI REASON GENERATOR
    # ======================================================

    def generate_reasons(

        self,

    ) -> List[str]:

        reasons = []

        if self.trend_score() >= 75:

            reasons.append(

                "Strong bullish trend across moving averages."

            )

        if self.momentum_score() >= 70:

            reasons.append(

                "Momentum indicators remain positive."

            )

        if self.sentiment_engine.bullish_score() > \
           self.sentiment_engine.bearish_score():

            reasons.append(

                "Market sentiment favors buyers."

            )

        if self.regime_engine.regime_confidence() >= 75:

            reasons.append(

                "Market regime supports long positions."

            )

        if self.win_probability() >= 80:

            reasons.append(

                "High probability trade setup."

            )

        if not reasons:

            reasons.append(

                "No significant bullish edge detected."

            )

        return reasons

    # ======================================================
    # RISK WARNING ENGINE
    # ======================================================

    def risk_warnings(

        self,

    ) -> List[str]:

        warnings = []

        if self.volatility_score() < 40:

            warnings.append(

                "High market volatility."

            )

        if self.expected_drawdown() > self.expected_return():

            warnings.append(

                "Expected drawdown exceeds expected return."

            )

        if self.bearish_probability() > 60:

            warnings.append(

                "Bearish probability increasing."

            )

        if self.risk_classification() in (

            "High",

            "Very High",

        ):

            warnings.append(

                "Overall trade risk is elevated."

            )

        if self.conviction_score() < 50:

            warnings.append(

                "Low AI conviction."

            )

        return warnings

    # ======================================================
    # OPPORTUNITY SUMMARY
    # ======================================================

    def opportunity_summary(

        self,

    ) -> Dict:

        return {

            "prediction":

                self.prediction().value,

            "grade":

                self.opportunity_grade(),

            "win_probability":

                self.win_probability(),

            "confidence":

                self.confidence_level().value,

            "risk":

                self.risk_classification(),

            "entry":

                self.entry_timing(),

            "exit":

                self.exit_timing(),

        }

    # ======================================================
    # DASHBOARD
    # ======================================================

    def dashboard(

        self,

    ) -> Dict:

        return {

            "Prediction":

                self.prediction().value,

            "Trend":

                self.trend_direction().value,

            "AI Score":

                self.ai_score()["overall"],

            "Win Probability":

                self.win_probability(),

            "Conviction":

                self.conviction_score(),

            "Opportunity Grade":

                self.opportunity_grade(),

            "Risk":

                self.risk_classification(),

        }

    # ======================================================
    # EXPLAINABLE AI
    # ======================================================

    def explain(

        self,

    ) -> str:

        reasons = self.generate_reasons()

        warnings = self.risk_warnings()

        text = []

        text.append(

            f"Prediction: {self.prediction().value}"

        )

        text.append(

            f"Win Probability: {self.win_probability():.2f}%"

        )

        text.append(

            f"Conviction Score: {self.conviction_score():.2f}"

        )

        text.append("")

        text.append("Reasons:")

        for reason in reasons:

            text.append(

                f"• {reason}"

            )

        if warnings:

            text.append("")

            text.append("Warnings:")

            for warning in warnings:

                text.append(

                    f"• {warning}"

                )

        return "\n".join(text)

    # ======================================================
    # PREDICTION REPORT
    # ======================================================

    def report(

        self,

    ) -> Dict:

        return {

            "summary":

                self.opportunity_summary(),

            "dashboard":

                self.dashboard(),

            "ai_score":

                self.ai_score(),

            "entry":

                self.entry_timing(),

            "exit":

                self.exit_timing(),

            "expected_move":

                self.expected_move(),

            "risk_reward":

                self.risk_reward_estimate(),

            "reasons":

                self.generate_reasons(),

            "warnings":

                self.risk_warnings(),

            "explanation":

                self.explain(),

        }

    # ======================================================
    # HISTORY ANALYTICS
    # ======================================================

    def prediction_analytics(

        self,

        history: List[MarketPredictionResult],

    ) -> Dict:

        if not history:

            return {}

        probabilities = [

            item.probability

            for item in history

        ]

        returns = [

            item.expected_return

            for item in history

        ]

        return {

            "samples":

                len(history),

            "average_probability":

                round(float(np.mean(probabilities)), 2),

            "average_expected_return":

                round(float(np.mean(returns)), 2),

            "highest_probability":

                round(max(probabilities), 2),

            "lowest_probability":

                round(min(probabilities), 2),

        }

    # ======================================================
    # BATCH PREDICTION
    # ======================================================

    def batch_predict(

        self,

        datasets: Dict[str, pd.DataFrame],

    ) -> Dict[str, Dict]:

        results = {}

        for symbol, data in datasets.items():

            engine = MarketPredictionEngine()

            engine.load(

                symbol,

                data,

            )

            results[symbol] = engine.report()

        return results
        # ======================================================
    # BUILD PREDICTION RESULT
    # ======================================================

    def analyze(

        self,

    ) -> MarketPredictionResult:

        probability = self.refined_probability()

        confidence = self.conviction_score()

        rr = self.risk_reward_estimate()

        result = MarketPredictionResult(

            symbol=self.symbol,

            prediction=self.prediction(),

            confidence=confidence,

            probability=probability,

            trend=self.trend_direction(),

            confidence_level=self.confidence_level(),

            expected_return=self.expected_return(),

            expected_drawdown=self.expected_drawdown(),

            risk_reward=rr["risk_reward"],

            reasons=self.generate_reasons(),

            warnings=self.risk_warnings(),

            indicators={

                "trend_score": self.trend_score(),

                "momentum_score": self.momentum_score(),

                "volatility_score": self.volatility_score(),

                "prediction_score": self.prediction_score(),

                "ai_score": self.ai_score(),

                "entry": self.entry_timing(),

                "exit": self.exit_timing(),

                "risk_reward": rr,

                "expected_move": self.expected_move(),

            },

        )

        self.result = result

        return result

    # ======================================================
    # MULTI STOCK SCANNER
    # ======================================================

    def scan_market(

        self,

        datasets: Dict[str, pd.DataFrame],

    ) -> pd.DataFrame:

        rows = []

        for symbol, df in datasets.items():

            engine = MarketPredictionEngine()

            engine.load(

                symbol,

                df,

            )

            result = engine.analyze()

            rows.append({

                "Symbol":

                    result.symbol,

                "Prediction":

                    result.prediction.value,

                "Probability":

                    result.probability,

                "Confidence":

                    result.confidence,

                "Trend":

                    result.trend.value,

                "Grade":

                    engine.opportunity_grade(),

                "RiskReward":

                    result.risk_reward,

            })

        scanner = pd.DataFrame(rows)

        if not scanner.empty:

            scanner = scanner.sort_values(

                by=[

                    "Probability",

                    "Confidence",

                ],

                ascending=False,

            )

        return scanner.reset_index(

            drop=True,

        )

    # ======================================================
    # PREDICTION RANKING
    # ======================================================

    def rank_predictions(

        self,

        scanner: pd.DataFrame,

    ) -> pd.DataFrame:

        if scanner.empty:

            return scanner

        ranked = scanner.copy()

        ranked["Rank"] = (

            ranked["Probability"]

            .rank(

                ascending=False,

                method="dense",

            )

            .astype(int)

        )

        ranked = ranked.sort_values(

            "Rank",

        )

        columns = [

            "Rank",

            "Symbol",

            "Prediction",

            "Probability",

            "Confidence",

            "Trend",

            "Grade",

            "RiskReward",

        ]

        return ranked[columns]

    # ======================================================
    # PORTFOLIO PREDICTION
    # ======================================================

    def portfolio_prediction(

        self,

        history: List[MarketPredictionResult],

    ) -> Dict:

        if not history:

            return {}

        probabilities = [

            x.probability

            for x in history

        ]

        confidence = [

            x.confidence

            for x in history

        ]

        rr = [

            x.risk_reward

            for x in history

        ]

        return {

            "positions":

                len(history),

            "average_probability":

                round(

                    float(

                        np.mean(

                            probabilities,

                        )

                    ),

                    2,

                ),

            "average_confidence":

                round(

                    float(

                        np.mean(

                            confidence,

                        )

                    ),

                    2,

                ),

            "average_rr":

                round(

                    float(

                        np.mean(

                            rr,

                        )

                    ),

                    2,

                ),

            "best_probability":

                round(

                    max(

                        probabilities,

                    ),

                    2,

                ),

        }

    # ======================================================
    # RECOMMENDATION ENGINE
    # ======================================================

    def recommendation(

        self,

    ) -> str:

        prediction = self.prediction()

        conviction = self.conviction_score()

        if (

            prediction == Prediction.STRONG_BUY

            and conviction >= 85

        ):

            return "Aggressive Buy"

        if prediction == Prediction.BUY:

            return "Buy"

        if prediction == Prediction.ACCUMULATE:

            return "Accumulate Gradually"

        if prediction == Prediction.HOLD:

            return "Hold Existing Position"

        if prediction == Prediction.REDUCE:

            return "Reduce Exposure"

        if prediction == Prediction.SELL:

            return "Sell"

        return "Exit Immediately"

    # ======================================================
    # ALERT ENGINE
    # ======================================================

    def alerts(

        self,

    ) -> List[str]:

        alerts = []

        if self.win_probability() >= 90:

            alerts.append(

                "High Probability Opportunity"

            )

        if self.opportunity_grade() == "A+":

            alerts.append(

                "Institutional Grade Setup"

            )

        if self.conviction_score() >= 90:

            alerts.append(

                "Very High AI Conviction"

            )

        if self.bearish_probability() >= 80:

            alerts.append(

                "Bearish Reversal Risk"

            )

        if self.volatility_score() < 30:

            alerts.append(

                "Extreme Volatility"

            )

        return alerts

    # ======================================================
    # AI EXECUTION SUMMARY
    # ======================================================

    def execute(

        self,

    ) -> Dict:

        result = self.analyze()

        return {

            "result": result,

            "recommendation":

                self.recommendation(),

            "alerts":

                self.alerts(),

            "dashboard":

                self.dashboard(),

            "report":

                self.report(),

            "summary":

                self.opportunity_summary(),

        }
        # ======================================================
    # DATAFRAME EXPORT
    # ======================================================

    def to_dataframe(

        self,

        history: List[MarketPredictionResult],

    ) -> pd.DataFrame:

        rows = []

        for item in history:

            rows.append({

                "Symbol": item.symbol,

                "Prediction": item.prediction.value,

                "Trend": item.trend.value,

                "Probability": item.probability,

                "Confidence": item.confidence,

                "Confidence Level": item.confidence_level.value,

                "Expected Return": item.expected_return,

                "Expected Drawdown": item.expected_drawdown,

                "Risk Reward": item.risk_reward,

                "Reasons": "; ".join(item.reasons),

                "Warnings": "; ".join(item.warnings),

            })

        return pd.DataFrame(rows)

    # ======================================================
    # JSON EXPORT
    # ======================================================

    def export_json(

        self,

        history: List[MarketPredictionResult],

        filename: str,

    ) -> None:

        dataframe = self.to_dataframe(history)

        with open(

            filename,

            "w",

            encoding="utf-8",

        ) as fp:

            json.dump(

                dataframe.to_dict(

                    orient="records",

                ),

                fp,

                indent=4,

            )

    # ======================================================
    # CSV EXPORT
    # ======================================================

    def export_csv(

        self,

        history: List[MarketPredictionResult],

        filename: str,

    ) -> None:

        self.to_dataframe(

            history,

        ).to_csv(

            filename,

            index=False,

        )

    # ======================================================
    # SERIALIZATION
    # ======================================================

    def to_dict(

        self,

        result: Optional[
            MarketPredictionResult
        ] = None,

    ) -> Dict:

        if result is None:

            result = self.result

        if result is None:

            return {}

        return {

            "symbol":

                result.symbol,

            "prediction":

                result.prediction.value,

            "trend":

                result.trend.value,

            "probability":

                result.probability,

            "confidence":

                result.confidence,

            "confidence_level":

                result.confidence_level.value,

            "expected_return":

                result.expected_return,

            "expected_drawdown":

                result.expected_drawdown,

            "risk_reward":

                result.risk_reward,

            "reasons":

                result.reasons,

            "warnings":

                result.warnings,

            "indicators":

                result.indicators,

        }

    # ======================================================
    # HISTORY MANAGEMENT
    # ======================================================

    def add_history(

        self,

        history: List[MarketPredictionResult],

    ) -> List[MarketPredictionResult]:

        if self.result is not None:

            history.append(

                self.result,

            )

        return history

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

            "rows_processed":

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

            "%Y-%m-%d %H:%M:%S",

        )

        print(

            f"[{timestamp}] "

            f"[PredictionEngine] "

            f"{message}"

        )

    # ======================================================
    # ENGINE STATUS
    # ======================================================

    def status(

        self,

    ) -> Dict:

        return {

            "engine":

                "MarketPredictionEngine",

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

            "AI Prediction",

            "Probability Engine",

            "Expected Return Forecast",

            "Expected Drawdown",

            "Trend Prediction",

            "Multi-Timeframe Analysis",

            "Institutional Confidence",

            "Opportunity Ranking",

            "Risk Classification",

            "Portfolio Analytics",

            "Batch Prediction",

            "Scanner",

            "CSV Export",

            "JSON Export",

            "Explainable AI",

        ]

    @staticmethod

    def engine_info(

    ) -> Dict:

        return {

            "name":

                "MarketPredictionEngine",

            "version":

                "4.0.0",

            "powered_by":

                "StockVersity Scanner Pro AI",

            "features":

                MarketPredictionEngine.supported_features(),

        }
        # ======================================================
    # COMPLETE REPORT
    # ======================================================

    def report(

        self,

    ) -> Dict:

        if self.result is None:

            self.analyze()

        return {

            "symbol":

                self.result.symbol,

            "prediction":

                self.result.prediction.value,

            "trend":

                self.result.trend.value,

            "confidence":

                self.result.confidence,

            "confidence_level":

                self.result.confidence_level.value,

            "probability":

                self.result.probability,

            "expected_return":

                self.result.expected_return,

            "expected_drawdown":

                self.result.expected_drawdown,

            "risk_reward":

                self.result.risk_reward,

            "recommendation":

                self.recommendation(),

            "dashboard":

                self.dashboard(),

            "summary":

                self.opportunity_summary(),

            "ai_score":

                self.ai_score(),

            "entry":

                self.entry_timing(),

            "exit":

                self.exit_timing(),

            "expected_move":

                self.expected_move(),

            "alerts":

                self.alerts(),

            "reasons":

                self.generate_reasons(),

            "warnings":

                self.risk_warnings(),

            "explanation":

                self.explain(),

        }

    # ======================================================
    # SAVE REPORT
    # ======================================================

    def save_report(

        self,

        filename: str,

    ) -> None:

        with open(

            filename,

            "w",

            encoding="utf-8",

        ) as fp:

            json.dump(

                self.report(),

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

                "MarketPredictionEngine",

            "version":

                self.version(),

            "symbol":

                self.symbol,

            "loaded":

                self.data is not None,

            "rows":

                0 if self.data is None else len(self.data),

            "prediction_ready":

                self.result is not None,

        }

    # ======================================================
    # SNAPSHOT
    # ======================================================

    def snapshot(

        self,

    ) -> Dict:

        return {

            "engine":

                self.engine_info(),

            "status":

                self.status(),

            "health":

                self.health_check(),

            "summary":

                self.summary(),

            "dashboard":

                self.dashboard(),

            "report":

                self.report(),

        }

    # ======================================================
    # SUMMARY
    # ======================================================

    def summary(

        self,

    ) -> Dict:

        if self.result is None:

            self.analyze()

        return {

            "Symbol":

                self.result.symbol,

            "Prediction":

                self.result.prediction.value,

            "Trend":

                self.result.trend.value,

            "Probability":

                self.result.probability,

            "Confidence":

                self.result.confidence,

            "Grade":

                self.opportunity_grade(),

            "Recommendation":

                self.recommendation(),

        }

    # ======================================================
    # RESET
    # ======================================================

    def reset(

        self,

    ) -> None:

        self.symbol = ""

        self.data = None

        self.result = None

    # ======================================================
    # CLEANUP
    # ======================================================

    def cleanup(

        self,

    ) -> None:

        self.reset()

    # ======================================================
    # ENHANCED EXECUTION
    # ======================================================

    def execute(

        self,

    ) -> Dict:

        start = pd.Timestamp.now()

        result = self.analyze()

        return {

            "result":

                result,

            "summary":

                self.summary(),

            "dashboard":

                self.dashboard(),

            "report":

                self.report(),

            "alerts":

                self.alerts(),

            "recommendation":

                self.recommendation(),

            "runtime":

                self.runtime_metrics(start),

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

        print("=" * 70)

        print(" STOCKVERSITY AI MARKET PREDICTION ")

        print("=" * 70)

        for key, value in summary.items():

            print(

                f"{key:<18}: {value}"

            )

        print("=" * 70)
            # ======================================================
    # ENGINE BANNER
    # ======================================================

    @staticmethod
    def banner() -> str:

        return (
            "\n"
            "=============================================================\n"
            "            STOCKVERSITY SCANNER PRO AI v4.0\n"
            "                 Market Prediction Engine\n"
            "=============================================================\n"
        )

    # ======================================================
    # DEFAULT CONFIGURATION
    # ======================================================

    @staticmethod
    def default_config() -> Dict:

        return {

            "version": "4.0.0",

            "risk_reward_default": 2.5,

            "default_risk_percent": 1.0,

            "atr_period": 14,

            "ema_fast": 20,

            "ema_medium": 50,

            "ema_long": 200,

            "rsi_period": 14,

            "macd_fast": 12,

            "macd_slow": 26,

            "macd_signal": 9,

            "prediction_threshold": 75,

            "confidence_threshold": 70,

        }

    # ======================================================
    # DATA VALIDATION
    # ======================================================

    def validate_result(

        self,

        result: Optional[
            MarketPredictionResult
        ] = None,

    ) -> bool:

        if result is None:

            result = self.result

        if result is None:

            return False

        required = [

            result.symbol,

            result.prediction,

            result.trend,

            result.confidence,

            result.probability,

        ]

        return all(

            item is not None

            for item in required

        )

    # ======================================================
    # LAST RESULT
    # ======================================================

    def last_result(

        self,

    ) -> Optional[
        MarketPredictionResult
    ]:

        return self.result

    # ======================================================
    # ENGINE READY
    # ======================================================

    def is_ready(

        self,

    ) -> bool:

        return (

            self.data is not None

            and

            len(self.data) > 0

        )

    # ======================================================
    # FINALIZE
    # ======================================================

    def finalize(

        self,

    ) -> Dict:

        if self.result is None:

            self.analyze()

        return {

            "status": "SUCCESS",

            "engine": self.engine_info(),

            "health": self.health_check(),

            "summary": self.summary(),

            "recommendation": self.recommendation(),

        }

    # ======================================================
    # STRING REPRESENTATION
    # ======================================================

    def __repr__(

        self,

    ) -> str:

        return (

            "MarketPredictionEngine("

            f"symbol='{self.symbol}', "

            f"version='{self.version()}', "

            f"loaded={self.data is not None}"

            ")"

        )

    def __str__(

        self,

    ) -> str:

        if self.result is None:

            return self.__repr__()

        return (

            f"{self.symbol} | "

            f"{self.result.prediction.value} | "

            f"Probability={self.result.probability:.2f}% | "

            f"Confidence={self.result.confidence:.2f}%"

        )

    # ======================================================
    # CLOSE ENGINE
    # ======================================================

    def close(

        self,

    ) -> None:

        self.cleanup()

    # ======================================================
    # END OF FILE
    # ======================================================