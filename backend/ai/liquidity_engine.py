"""
==========================================================
StockVersity Scanner Pro
Liquidity Engine
Powered by AI
Version : 4.0
==========================================================
"""

from __future__ import annotations

import json

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np
import pandas as pd


# ==========================================================
# RESULT MODEL
# ==========================================================

@dataclass
class LiquidityResult:

    symbol: str

    liquidity_score: float

    liquidity_type: str

    recommendation: str

    confidence: float

    buy_side_liquidity: float

    sell_side_liquidity: float

    metrics: Dict = field(default_factory=dict)


# ==========================================================
# LIQUIDITY ENGINE
# ==========================================================

class LiquidityEngine:

    VERSION = "4.0"

    REQUIRED_COLUMNS = [

        "Open",
        "High",
        "Low",
        "Close",
        "Volume",

    ]

    def __init__(

        self,

        data: pd.DataFrame,

        symbol: str = "",

    ):

        self.symbol = symbol

        self.data = data.copy()

        self.result: Optional[
            LiquidityResult
        ] = None

        self.validate()

    # ======================================================
    # VALIDATION
    # ======================================================

    def validate(

        self,

    ) -> bool:

        if self.data is None:

            return False

        if self.data.empty:

            return False

        for column in self.REQUIRED_COLUMNS:

            if column not in self.data.columns:

                return False

        return True

    # ======================================================
    # RESET
    # ======================================================

    def reset(

        self,

    ):

        self.result = None

    # ======================================================
    # AVERAGE VOLUME
    # ======================================================

    def average_volume(

        self,

        period: int = 20,

    ) -> float:

        return float(

            self.data["Volume"]

            .tail(period)

            .mean()

        )

    # ======================================================
    # RELATIVE VOLUME (RVOL)
    # ======================================================

    def relative_volume(

        self,

        period: int = 20,

    ) -> float:

        avg = self.average_volume(period)

        current = float(

            self.data["Volume"].iloc[-1]

        )

        if avg == 0:

            return 0.0

        return round(

            current / avg,

            2,

        )

    # ======================================================
    # CURRENT LIQUIDITY
    # ======================================================

    def current_liquidity(

        self,

    ) -> float:

        volume = float(

            self.data["Volume"].iloc[-1]

        )

        close = float(

            self.data["Close"].iloc[-1]

        )

        return round(

            volume * close,

            2,

        )

    # ======================================================
    # LIQUIDITY TREND
    # ======================================================

    def liquidity_trend(

        self,

    ) -> str:

        rvol = self.relative_volume()

        if rvol >= 2.0:

            return "Very High"

        elif rvol >= 1.5:

            return "High"

        elif rvol >= 1.0:

            return "Normal"

        return "Low"

    # ======================================================
    # BUY SIDE LIQUIDITY
    # ======================================================

    def buy_side_liquidity(

        self,

    ) -> float:

        bullish = self.data[

            self.data["Close"]

            >

            self.data["Open"]

        ]

        return round(

            float(

                bullish["Volume"].sum()

            ),

            2,

        )

    # ======================================================
    # SELL SIDE LIQUIDITY
    # ======================================================

    def sell_side_liquidity(

        self,

    ) -> float:

        bearish = self.data[

            self.data["Close"]

            <

            self.data["Open"]

        ]

        return round(

            float(

                bearish["Volume"].sum()

            ),

            2,

        )

    # ======================================================
    # LIQUIDITY IMBALANCE
    # ======================================================

    def liquidity_imbalance(

        self,

    ) -> Dict:

        buy = self.buy_side_liquidity()

        sell = self.sell_side_liquidity()

        total = buy + sell

        if total == 0:

            score = 50

        else:

            score = (buy / total) * 100

        return {

            "buy": buy,

            "sell": sell,

            "score": round(score, 2),

            "bias":

                "Bullish"

                if score > 55

                else "Bearish"

                if score < 45

                else "Neutral",

        }
        # ======================================================
    # BUY SIDE LIQUIDITY SWEEP
    # ======================================================

    def buy_side_liquidity_sweep(

        self,

        lookback: int = 20,

    ) -> Dict:

        highs = self.data["High"].tail(lookback)

        current_high = float(

            self.data["High"].iloc[-1]

        )

        previous_high = float(

            highs.iloc[:-1].max()

        )

        close = float(

            self.data["Close"].iloc[-1]

        )

        swept = (

            current_high > previous_high

            and

            close < previous_high

        )

        return {

            "detected": swept,

            "level": round(previous_high, 2),

            "current_high": round(current_high, 2),

            "type": "Buy Side Sweep" if swept else "None",

        }

    # ======================================================
    # SELL SIDE LIQUIDITY SWEEP
    # ======================================================

    def sell_side_liquidity_sweep(

        self,

        lookback: int = 20,

    ) -> Dict:

        lows = self.data["Low"].tail(lookback)

        current_low = float(

            self.data["Low"].iloc[-1]

        )

        previous_low = float(

            lows.iloc[:-1].min()

        )

        close = float(

            self.data["Close"].iloc[-1]

        )

        swept = (

            current_low < previous_low

            and

            close > previous_low

        )

        return {

            "detected": swept,

            "level": round(previous_low, 2),

            "current_low": round(current_low, 2),

            "type": "Sell Side Sweep" if swept else "None",

        }

    # ======================================================
    # EQUAL HIGHS DETECTION
    # ======================================================

    def equal_highs(

        self,

        tolerance: float = 0.002,

        lookback: int = 20,

    ) -> Dict:

        highs = self.data["High"].tail(lookback)

        latest = float(highs.iloc[-1])

        matches = highs[

            np.abs(

                highs - latest

            )

            <=

            latest * tolerance

        ]

        detected = len(matches) >= 2

        return {

            "detected": detected,

            "count": len(matches),

            "level": round(latest, 2),

        }

    # ======================================================
    # EQUAL LOWS DETECTION
    # ======================================================

    def equal_lows(

        self,

        tolerance: float = 0.002,

        lookback: int = 20,

    ) -> Dict:

        lows = self.data["Low"].tail(lookback)

        latest = float(lows.iloc[-1])

        matches = lows[

            np.abs(

                lows - latest

            )

            <=

            latest * tolerance

        ]

        detected = len(matches) >= 2

        return {

            "detected": detected,

            "count": len(matches),

            "level": round(latest, 2),

        }

    # ======================================================
    # STOP HUNT DETECTION
    # ======================================================

    def stop_hunt(

        self,

    ) -> Dict:

        buy_sweep = self.buy_side_liquidity_sweep()

        sell_sweep = self.sell_side_liquidity_sweep()

        detected = (

            buy_sweep["detected"]

            or

            sell_sweep["detected"]

        )

        direction = "None"

        if buy_sweep["detected"]:

            direction = "Bearish Stop Hunt"

        elif sell_sweep["detected"]:

            direction = "Bullish Stop Hunt"

        return {

            "detected": detected,

            "direction": direction,

        }

    # ======================================================
    # LIQUIDITY GRAB
    # ======================================================

    def liquidity_grab(

        self,

    ) -> Dict:

        stop = self.stop_hunt()

        imbalance = self.liquidity_imbalance()

        score = 0

        if stop["detected"]:

            score += 60

        if imbalance["bias"] != "Neutral":

            score += 40

        return {

            "detected": stop["detected"],

            "score": min(score, 100),

            "bias": imbalance["bias"],

        }

    # ======================================================
    # RESTING LIQUIDITY ZONES
    # ======================================================

    def resting_liquidity(

        self,

    ) -> Dict:

        highs = self.equal_highs()

        lows = self.equal_lows()

        zones = []

        if highs["detected"]:

            zones.append(

                {

                    "type": "Equal Highs",

                    "price": highs["level"],

                }

            )

        if lows["detected"]:

            zones.append(

                {

                    "type": "Equal Lows",

                    "price": lows["level"],

                }

            )

        return {

            "count": len(zones),

            "zones": zones,

        }

    # ======================================================
    # INSTITUTIONAL LIQUIDITY SCORE
    # ======================================================

    def institutional_liquidity_score(

        self,

    ) -> float:

        score = 0

        if self.buy_side_liquidity_sweep()["detected"]:

            score += 25

        if self.sell_side_liquidity_sweep()["detected"]:

            score += 25

        if self.equal_highs()["detected"]:

            score += 15

        if self.equal_lows()["detected"]:

            score += 15

        if self.stop_hunt()["detected"]:

            score += 10

        if self.liquidity_grab()["detected"]:

            score += 10

        return round(

            min(score, 100),

            2,

        )
        # ======================================================
    # LIQUIDITY VOID DETECTION
    # ======================================================

    def liquidity_void(

        self,

        atr_multiplier: float = 1.5,

        period: int = 14,

    ) -> Dict:

        high = self.data["High"]

        low = self.data["Low"]

        close = self.data["Close"]

        tr = pd.concat(

            [

                high - low,

                (high - close.shift()).abs(),

                (low - close.shift()).abs(),

            ],

            axis=1,

        ).max(axis=1)

        atr = tr.rolling(period).mean().iloc[-1]

        latest_range = (

            high.iloc[-1]

            -

            low.iloc[-1]

        )

        detected = (

            latest_range >

            atr * atr_multiplier

        )

        return {

            "detected": detected,

            "range": round(

                float(latest_range),

                2,

            ),

            "atr": round(

                float(atr),

                2,

            ),

            "strength":

                "Strong"

                if detected

                else "Normal",

        }

    # ======================================================
    # VOLUME SPIKE ANALYSIS
    # ======================================================

    def volume_spike(

        self,

        period: int = 20,

        multiplier: float = 2.0,

    ) -> Dict:

        avg_volume = self.average_volume(period)

        current = float(

            self.data["Volume"].iloc[-1]

        )

        ratio = (

            current / avg_volume

            if avg_volume > 0

            else 0

        )

        return {

            "detected":

                ratio >= multiplier,

            "ratio":

                round(ratio, 2),

            "current":

                current,

            "average":

                round(avg_volume, 2),

        }

    # ======================================================
    # ABSORPTION DETECTION
    # ======================================================

    def absorption(

        self,

    ) -> Dict:

        candle = abs(

            self.data["Close"].iloc[-1]

            -

            self.data["Open"].iloc[-1]

        )

        rng = (

            self.data["High"].iloc[-1]

            -

            self.data["Low"].iloc[-1]

        )

        spike = self.volume_spike()

        absorbed = (

            spike["detected"]

            and

            candle < (rng * 0.35)

        )

        return {

            "detected": absorbed,

            "body": round(

                float(candle),

                2,

            ),

            "range": round(

                float(rng),

                2,

            ),

        }

    # ======================================================
    # EXHAUSTION DETECTION
    # ======================================================

    def exhaustion(

        self,

    ) -> Dict:

        spike = self.volume_spike()

        rvol = self.relative_volume()

        body = abs(

            self.data["Close"].iloc[-1]

            -

            self.data["Open"].iloc[-1]

        )

        rng = (

            self.data["High"].iloc[-1]

            -

            self.data["Low"].iloc[-1]

        )

        exhausted = (

            spike["detected"]

            and

            body <= rng * 0.25

            and

            rvol >= 2

        )

        return {

            "detected": exhausted,

            "rvol": rvol,

        }

    # ======================================================
    # HIDDEN LIQUIDITY
    # ======================================================

    def hidden_liquidity(

        self,

    ) -> Dict:

        absorption = self.absorption()

        imbalance = self.liquidity_imbalance()

        hidden = (

            absorption["detected"]

            and

            imbalance["bias"] != "Neutral"

        )

        return {

            "detected": hidden,

            "bias": imbalance["bias"],

        }

    # ======================================================
    # LIQUIDITY PRESSURE INDEX
    # ======================================================

    def liquidity_pressure_index(

        self,

    ) -> float:

        imbalance = self.liquidity_imbalance()

        score = imbalance["score"]

        if self.volume_spike()["detected"]:

            score += 15

        if self.absorption()["detected"]:

            score += 10

        if self.hidden_liquidity()["detected"]:

            score += 15

        return round(

            min(score, 100),

            2,

        )

    # ======================================================
    # SMART MONEY ACTIVITY SCORE
    # ======================================================

    def smart_money_activity_score(

        self,

    ) -> float:

        score = 0

        if self.absorption()["detected"]:

            score += 20

        if self.exhaustion()["detected"]:

            score += 20

        if self.hidden_liquidity()["detected"]:

            score += 20

        if self.liquidity_grab()["detected"]:

            score += 20

        if self.liquidity_void()["detected"]:

            score += 20

        return round(

            min(score, 100),

            2,

        )

    # ======================================================
    # AI LIQUIDITY CLASSIFICATION
    # ======================================================

    def liquidity_classification(

        self,

    ) -> Dict:

        institutional = (

            self.institutional_liquidity_score()

        )

        smart_money = (

            self.smart_money_activity_score()

        )

        pressure = (

            self.liquidity_pressure_index()

        )

        score = (

            institutional * 0.40 +

            smart_money * 0.35 +

            pressure * 0.25

        )

        score = round(

            min(score, 100),

            2,

        )

        if score >= 85:

            classification = "Institutional Accumulation"

        elif score >= 70:

            classification = "Professional Buying"

        elif score >= 55:

            classification = "Balanced Liquidity"

        elif score >= 40:

            classification = "Distribution"

        else:

            classification = "Weak Liquidity"

        return {

            "classification":

                classification,

            "score":

                score,

        }
        # ======================================================
    # LIQUIDITY STRENGTH SCORE
    # ======================================================

    def liquidity_strength_score(

        self,

    ) -> float:

        institutional = (

            self.institutional_liquidity_score()

        )

        smart_money = (

            self.smart_money_activity_score()

        )

        pressure = (

            self.liquidity_pressure_index()

        )

        score = (

            institutional * 0.40 +

            smart_money * 0.35 +

            pressure * 0.25

        )

        return round(

            min(score, 100),

            2,

        )

    # ======================================================
    # INSTITUTIONAL PARTICIPATION SCORE
    # ======================================================

    def institutional_participation(

        self,

    ) -> Dict:

        rvol = self.relative_volume()

        volume_spike = self.volume_spike()

        institutional = self.institutional_liquidity_score()

        score = (

            institutional * 0.60 +

            min(rvol * 20, 100) * 0.25 +

            (100 if volume_spike["detected"] else 40) * 0.15

        )

        score = round(

            min(score, 100),

            2,

        )

        return {

            "score": score,

            "institutional":

                score >= 70,

        }

    # ======================================================
    # BREAKOUT LIQUIDITY SCORE
    # ======================================================

    def breakout_liquidity_score(

        self,

    ) -> Dict:

        sweep = self.buy_side_liquidity_sweep()

        pressure = self.liquidity_pressure_index()

        spike = self.volume_spike()

        score = (

            pressure * 0.50 +

            (100 if sweep["detected"] else 40) * 0.30 +

            (100 if spike["detected"] else 50) * 0.20

        )

        score = round(

            min(score, 100),

            2,

        )

        return {

            "score": score,

            "ready":

                score >= 70,

        }

    # ======================================================
    # REVERSAL LIQUIDITY SCORE
    # ======================================================

    def reversal_liquidity_score(

        self,

    ) -> Dict:

        stop_hunt = self.stop_hunt()

        grab = self.liquidity_grab()

        exhaustion = self.exhaustion()

        score = (

            (100 if stop_hunt["detected"] else 40) * 0.40 +

            grab["score"] * 0.35 +

            (100 if exhaustion["detected"] else 40) * 0.25

        )

        score = round(

            min(score, 100),

            2,

        )

        return {

            "score": score,

            "reversal":

                score >= 70,

        }

    # ======================================================
    # TREND LIQUIDITY SCORE
    # ======================================================

    def trend_liquidity_score(

        self,

    ) -> Dict:

        imbalance = self.liquidity_imbalance()

        pressure = self.liquidity_pressure_index()

        score = (

            imbalance["score"] * 0.60 +

            pressure * 0.40

        )

        score = round(

            min(score, 100),

            2,

        )

        trend = (

            "Bullish"

            if imbalance["bias"] == "Bullish"

            else

            "Bearish"

            if imbalance["bias"] == "Bearish"

            else

            "Neutral"

        )

        return {

            "score": score,

            "trend": trend,

        }

    # ======================================================
    # LIQUIDITY CONFIDENCE
    # ======================================================

    def liquidity_confidence(

        self,

    ) -> float:

        strength = (

            self.liquidity_strength_score()

        )

        institutional = (

            self.institutional_participation()

        )

        trend = (

            self.trend_liquidity_score()

        )

        confidence = (

            strength * 0.45 +

            institutional["score"] * 0.30 +

            trend["score"] * 0.25

        )

        return round(

            min(confidence, 100),

            2,

        )

    # ======================================================
    # AI LIQUIDITY RATING
    # ======================================================

    def ai_liquidity_rating(

        self,

    ) -> Dict:

        score = self.liquidity_confidence()

        if score >= 90:

            rating = "A+"

        elif score >= 80:

            rating = "A"

        elif score >= 70:

            rating = "B+"

        elif score >= 60:

            rating = "B"

        elif score >= 50:

            rating = "C"

        else:

            rating = "D"

        return {

            "score": score,

            "rating": rating,

        }

    # ======================================================
    # PROFESSIONAL RECOMMENDATION ENGINE
    # ======================================================

    def professional_recommendation(

        self,

    ) -> Dict:

        rating = self.ai_liquidity_rating()

        breakout = self.breakout_liquidity_score()

        reversal = self.reversal_liquidity_score()

        trend = self.trend_liquidity_score()

        if (

            rating["score"] >= 85

            and

            breakout["ready"]

            and

            trend["trend"] == "Bullish"

        ):

            recommendation = "Strong Buy"

        elif (

            rating["score"] >= 70

            and

            trend["trend"] == "Bullish"

        ):

            recommendation = "Buy"

        elif reversal["reversal"]:

            recommendation = "Watch Reversal"

        elif rating["score"] >= 50:

            recommendation = "Hold"

        else:

            recommendation = "Avoid"

        return {

            "recommendation":

                recommendation,

            "confidence":

                rating["score"],

            "rating":

                rating["rating"],

        }
        # ======================================================
    # INTRADAY LIQUIDITY STRENGTH
    # ======================================================

    def intraday_liquidity_strength(

        self,

    ) -> Dict:

        confidence = self.liquidity_confidence()

        breakout = self.breakout_liquidity_score()

        pressure = self.liquidity_pressure_index()

        score = (

            confidence * 0.45 +

            breakout["score"] * 0.35 +

            pressure * 0.20

        )

        score = round(

            min(score, 100),

            2,

        )

        return {

            "score": score,

            "strength":

                "Strong"

                if score >= 75

                else

                "Moderate"

                if score >= 55

                else

                "Weak",

        }

    # ======================================================
    # SWING LIQUIDITY STRENGTH
    # ======================================================

    def swing_liquidity_strength(

        self,

    ) -> Dict:

        confidence = self.liquidity_confidence()

        institutional = (

            self.institutional_participation()

        )

        trend = (

            self.trend_liquidity_score()

        )

        score = (

            confidence * 0.40 +

            institutional["score"] * 0.35 +

            trend["score"] * 0.25

        )

        score = round(

            min(score, 100),

            2,

        )

        return {

            "score": score,

            "strength":

                "Strong"

                if score >= 75

                else

                "Moderate"

                if score >= 55

                else

                "Weak",

        }

    # ======================================================
    # POSITIONAL LIQUIDITY STRENGTH
    # ======================================================

    def positional_liquidity_strength(

        self,

    ) -> Dict:

        confidence = self.liquidity_confidence()

        smart_money = (

            self.smart_money_activity_score()

        )

        institutional = (

            self.institutional_liquidity_score()

        )

        score = (

            confidence * 0.40 +

            smart_money * 0.30 +

            institutional * 0.30

        )

        score = round(

            min(score, 100),

            2,

        )

        return {

            "score": score,

            "strength":

                "Strong"

                if score >= 80

                else

                "Moderate"

                if score >= 60

                else

                "Weak",

        }

    # ======================================================
    # MULTI TIMEFRAME LIQUIDITY ALIGNMENT
    # ======================================================

    def timeframe_alignment(

        self,

    ) -> Dict:

        intraday = (

            self.intraday_liquidity_strength()

        )

        swing = (

            self.swing_liquidity_strength()

        )

        positional = (

            self.positional_liquidity_strength()

        )

        score = (

            intraday["score"] +

            swing["score"] +

            positional["score"]

        ) / 3

        aligned = (

            intraday["strength"]

            ==

            swing["strength"]

            ==

            positional["strength"]

        )

        return {

            "aligned": aligned,

            "score": round(

                score,

                2,

            ),

        }

    # ======================================================
    # LIQUIDITY MOMENTUM SCORE
    # ======================================================

    def liquidity_momentum_score(

        self,

    ) -> float:

        breakout = (

            self.breakout_liquidity_score()

        )

        pressure = (

            self.liquidity_pressure_index()

        )

        smart_money = (

            self.smart_money_activity_score()

        )

        score = (

            breakout["score"] * 0.40 +

            pressure * 0.35 +

            smart_money * 0.25

        )

        return round(

            min(score, 100),

            2,

        )

    # ======================================================
    # LIQUIDITY CONSISTENCY SCORE
    # ======================================================

    def liquidity_consistency_score(

        self,

    ) -> float:

        alignment = (

            self.timeframe_alignment()

        )

        confidence = (

            self.liquidity_confidence()

        )

        score = (

            alignment["score"] * 0.60 +

            confidence * 0.40

        )

        return round(

            min(score, 100),

            2,

        )

    # ======================================================
    # INSTITUTIONAL LIQUIDITY RATING
    # ======================================================

    def institutional_liquidity_rating(

        self,

    ) -> Dict:

        score = (

            self.institutional_participation()

        )["score"]

        if score >= 90:

            rating = "Excellent"

        elif score >= 75:

            rating = "High"

        elif score >= 60:

            rating = "Medium"

        elif score >= 45:

            rating = "Low"

        else:

            rating = "Very Low"

        return {

            "score": score,

            "rating": rating,

        }

    # ======================================================
    # AI MULTI TIMEFRAME LIQUIDITY RATING
    # ======================================================

    def ai_multi_timeframe_rating(

        self,

    ) -> Dict:

        alignment = (

            self.timeframe_alignment()

        )

        consistency = (

            self.liquidity_consistency_score()

        )

        institutional = (

            self.institutional_liquidity_rating()

        )

        score = (

            alignment["score"] * 0.40 +

            consistency * 0.35 +

            institutional["score"] * 0.25

        )

        score = round(

            min(score, 100),

            2,

        )

        if score >= 90:

            grade = "A+"

        elif score >= 80:

            grade = "A"

        elif score >= 70:

            grade = "B+"

        elif score >= 60:

            grade = "B"

        elif score >= 50:

            grade = "C"

        else:

            grade = "D"

        return {

            "score": score,

            "rating": grade,

        }
        # ======================================================
    # LIQUIDITY OPPORTUNITY SCORE
    # ======================================================

    def liquidity_opportunity_score(

        self,

    ) -> float:

        confidence = self.liquidity_confidence()

        breakout = self.breakout_liquidity_score()

        institutional = (

            self.institutional_participation()

        )

        smart_money = (

            self.smart_money_activity_score()

        )

        score = (

            confidence * 0.35 +

            breakout["score"] * 0.30 +

            institutional["score"] * 0.20 +

            smart_money * 0.15

        )

        return round(

            min(score, 100),

            2,

        )

    # ======================================================
    # AI PRIORITY SCORE
    # ======================================================

    def priority_score(

        self,

    ) -> float:

        opportunity = (

            self.liquidity_opportunity_score()

        )

        mtf = (

            self.ai_multi_timeframe_rating()

        )

        recommendation = (

            self.professional_recommendation()

        )

        score = (

            opportunity * 0.45 +

            mtf["score"] * 0.35 +

            recommendation["confidence"] * 0.20

        )

        return round(

            min(score, 100),

            2,

        )

    # ======================================================
    # LIQUIDITY RANK
    # ======================================================

    def liquidity_rank(

        self,

        all_scores: List[float],

    ) -> Dict:

        score = self.priority_score()

        ranking = sorted(

            all_scores,

            reverse=True,

        )

        rank = (

            ranking.index(score) + 1

            if score in ranking

            else len(ranking) + 1

        )

        percentile = (

            (

                len(ranking)

                -

                rank

                +

                1

            )

            /

            max(

                len(ranking),

                1,

            )

        ) * 100

        return {

            "rank": rank,

            "total": len(ranking),

            "percentile": round(

                percentile,

                2,

            ),

            "score": score,

        }

    # ======================================================
    # WATCHLIST ENTRY
    # ======================================================

    def watchlist_entry(

        self,

    ) -> Dict:

        recommendation = (

            self.professional_recommendation()

        )

        return {

            "symbol":

                self.symbol,

            "priority_score":

                self.priority_score(),

            "liquidity_score":

                self.liquidity_strength_score(),

            "recommendation":

                recommendation["recommendation"],

            "confidence":

                recommendation["confidence"],

        }

    # ======================================================
    # DASHBOARD SUMMARY
    # ======================================================

    def dashboard_summary(

        self,

    ) -> Dict:

        recommendation = (

            self.professional_recommendation()

        )

        return {

            "Symbol":

                self.symbol,

            "Liquidity Trend":

                self.liquidity_trend(),

            "Liquidity Score":

                self.liquidity_strength_score(),

            "Priority Score":

                self.priority_score(),

            "Recommendation":

                recommendation["recommendation"],

            "Confidence":

                recommendation["confidence"],

        }

    # ======================================================
    # HEATMAP DATA
    # ======================================================

    def heatmap_data(

        self,

    ) -> Dict:

        score = self.priority_score()

        if score >= 80:

            color = "Dark Green"

        elif score >= 65:

            color = "Green"

        elif score >= 50:

            color = "Yellow"

        elif score >= 35:

            color = "Orange"

        else:

            color = "Red"

        return {

            "symbol":

                self.symbol,

            "score":

                score,

            "trend":

                self.liquidity_trend(),

            "color":

                color,

        }

    # ======================================================
    # ALERT GENERATOR
    # ======================================================

    def generate_alert(

        self,

    ) -> Dict:

        breakout = (

            self.breakout_liquidity_score()

        )

        recommendation = (

            self.professional_recommendation()

        )

        alert = False

        message = "No Alert"

        if (

            breakout["ready"]

            and

            recommendation["recommendation"]

            in [

                "Strong Buy",

                "Buy",

            ]

        ):

            alert = True

            message = (

                f"{self.symbol} "

                "shows strong institutional "

                "liquidity activity."

            )

        return {

            "alert": alert,

            "message": message,

            "priority_score":

                self.priority_score(),

            "recommendation":

                recommendation["recommendation"],

        }

    # ======================================================
    # OPPORTUNITY RANK
    # ======================================================

    def opportunity_rank(

        self,

    ) -> Dict:

        recommendation = (

            self.professional_recommendation()

        )

        score = self.priority_score()

        if score >= 90:

            stars = "★★★★★"

        elif score >= 80:

            stars = "★★★★☆"

        elif score >= 70:

            stars = "★★★☆☆"

        elif score >= 60:

            stars = "★★☆☆☆"

        else:

            stars = "★☆☆☆☆"

        return {

            "symbol":

                self.symbol,

            "priority_score":

                score,

            "rank":

                stars,

            "recommendation":

                recommendation["recommendation"],

            "confidence":

                recommendation["confidence"],

        }
        # ======================================================
    # MASTER LIQUIDITY ANALYSIS
    # ======================================================

    def analyze(

        self,

    ) -> LiquidityResult:

        if not self.validate():

            raise ValueError(

                "Invalid liquidity data."

            )

        recommendation = (

            self.professional_recommendation()

        )

        self.result = LiquidityResult(

            symbol=self.symbol,

            liquidity_score=self.priority_score(),

            liquidity_type=self.liquidity_classification()[

                "classification"

            ],

            recommendation=recommendation[

                "recommendation"

            ],

            confidence=recommendation[

                "confidence"

            ],

            buy_side_liquidity=self.buy_side_liquidity(),

            sell_side_liquidity=self.sell_side_liquidity(),

            metrics={

                "Liquidity Strength":

                    self.liquidity_strength_score(),

                "Institutional Score":

                    self.institutional_liquidity_score(),

                "Smart Money Score":

                    self.smart_money_activity_score(),

                "Pressure Index":

                    self.liquidity_pressure_index(),

                "Opportunity Score":

                    self.liquidity_opportunity_score(),

                "Priority Score":

                    self.priority_score(),

                "Liquidity Confidence":

                    self.liquidity_confidence(),

                "Momentum Score":

                    self.liquidity_momentum_score(),

            },

        )

        return self.result

    # ======================================================
    # AI RECOMMENDATION
    # ======================================================

    def ai_recommendation(

        self,

    ) -> Dict:

        recommendation = (

            self.professional_recommendation()

        )

        alert = self.generate_alert()

        return {

            "symbol":

                self.symbol,

            "recommendation":

                recommendation["recommendation"],

            "confidence":

                recommendation["confidence"],

            "priority_score":

                self.priority_score(),

            "alert":

                alert["alert"],

            "message":

                alert["message"],

        }

    # ======================================================
    # DASHBOARD EXPORT
    # ======================================================

    def dashboard(

        self,

    ) -> Dict:

        if self.result is None:

            self.analyze()

        return {

            "Symbol":

                self.result.symbol,

            "Liquidity Type":

                self.result.liquidity_type,

            "Liquidity Score":

                self.result.liquidity_score,

            "Buy Side":

                self.result.buy_side_liquidity,

            "Sell Side":

                self.result.sell_side_liquidity,

            "Recommendation":

                self.result.recommendation,

            "Confidence":

                self.result.confidence,

        }

    # ======================================================
    # EXPORT TO DICTIONARY
    # ======================================================

    def to_dict(

        self,

    ) -> Dict:

        if self.result is None:

            self.analyze()

        return {

            "symbol":

                self.result.symbol,

            "liquidity_score":

                self.result.liquidity_score,

            "liquidity_type":

                self.result.liquidity_type,

            "recommendation":

                self.result.recommendation,

            "confidence":

                self.result.confidence,

            "buy_side_liquidity":

                self.result.buy_side_liquidity,

            "sell_side_liquidity":

                self.result.sell_side_liquidity,

            "metrics":

                self.result.metrics,

        }

    # ======================================================
    # EXPORT JSON
    # ======================================================

    def export_json(

        self,

    ) -> str:

        return json.dumps(

            self.to_dict(),

            indent=4,

            default=str,

        )

    # ======================================================
    # EXPORT DATAFRAME
    # ======================================================

    def export_dataframe(

        self,

    ) -> pd.DataFrame:

        return pd.DataFrame(

            [

                self.to_dict()

            ]

        )

    # ======================================================
    # SAVE REPORT
    # ======================================================

    def save_report(

        self,

        filename: str,

    ) -> bool:

        try:

            with open(

                filename,

                "w",

                encoding="utf-8",

            ) as file:

                file.write(

                    self.export_json()

                )

            return True

        except Exception:

            return False

    # ======================================================
    # PRINT REPORT
    # ======================================================

    def print_report(

        self,

    ) -> None:

        if self.result is None:

            self.analyze()

        print("=" * 70)

        print(

            "STOCKVERSITY AI LIQUIDITY REPORT"

        )

        print("=" * 70)

        print(

            f"Symbol              : {self.result.symbol}"

        )

        print(

            f"Liquidity Type      : {self.result.liquidity_type}"

        )

        print(

            f"Liquidity Score     : "

            f"{self.result.liquidity_score:.2f}"

        )

        print(

            f"Buy Side Liquidity  : "

            f"{self.result.buy_side_liquidity:.2f}"

        )

        print(

            f"Sell Side Liquidity : "

            f"{self.result.sell_side_liquidity:.2f}"

        )

        print(

            f"Recommendation      : "

            f"{self.result.recommendation}"

        )

        print(

            f"Confidence          : "

            f"{self.result.confidence:.2f}"

        )

        print()

        print("METRICS")

        print("-" * 70)

        for key, value in self.result.metrics.items():

            print(

                f"{key:30} : {value}"

            )

        print("=" * 70)
            # ======================================================
    # LIQUIDITY RANKING ENGINE
    # ======================================================

    def ranking_engine(

        self,

        symbols: List[str],

        scores: List[float],

    ) -> pd.DataFrame:

        if len(symbols) != len(scores):

            raise ValueError(

                "symbols and scores length must match."

            )

        dataframe = pd.DataFrame(

            {

                "Symbol": symbols,

                "Score": scores,

            }

        )

        dataframe = dataframe.sort_values(

            by="Score",

            ascending=False,

        ).reset_index(

            drop=True,

        )

        dataframe["Rank"] = (

            dataframe.index + 1

        )

        dataframe["Grade"] = dataframe["Score"].apply(

            lambda value:

            "A+"

            if value >= 90 else

            "A"

            if value >= 80 else

            "B+"

            if value >= 70 else

            "B"

            if value >= 60 else

            "C"

            if value >= 50 else

            "D"

        )

        return dataframe

    # ======================================================
    # SCANNER SUMMARY
    # ======================================================

    def scanner_summary(

        self,

    ) -> Dict:

        recommendation = (

            self.professional_recommendation()

        )

        rating = (

            self.ai_multi_timeframe_rating()

        )

        return {

            "Symbol":

                self.symbol,

            "Liquidity Trend":

                self.liquidity_trend(),

            "Priority":

                self.priority_score(),

            "Rating":

                rating["rating"],

            "Recommendation":

                recommendation["recommendation"],

            "Confidence":

                recommendation["confidence"],

        }

    # ======================================================
    # HEATMAP EXPORT
    # ======================================================

    def export_heatmap(

        self,

    ) -> Dict:

        heatmap = self.heatmap_data()

        return {

            "symbol":

                heatmap["symbol"],

            "score":

                heatmap["score"],

            "trend":

                heatmap["trend"],

            "color":

                heatmap["color"],

            "timestamp":

                datetime.now(),

        }

    # ======================================================
    # WATCHLIST EXPORT
    # ======================================================

    def export_watchlist(

        self,

    ) -> Dict:

        watch = self.watchlist_entry()

        watch["added_at"] = datetime.now()

        watch["rating"] = (

            self.ai_multi_timeframe_rating()[

                "rating"

            ]

        )

        return watch

    # ======================================================
    # OPPORTUNITY OUTPUT
    # ======================================================

    def opportunity_output(

        self,

    ) -> Dict:

        opportunity = (

            self.opportunity_rank()

        )

        return {

            "Symbol":

                opportunity["symbol"],

            "Priority Score":

                opportunity["priority_score"],

            "Stars":

                opportunity["rank"],

            "Recommendation":

                opportunity["recommendation"],

            "Confidence":

                opportunity["confidence"],

        }

    # ======================================================
    # ALERT SUMMARY
    # ======================================================

    def alert_summary(

        self,

    ) -> Dict:

        alert = (

            self.generate_alert()

        )

        return {

            "Symbol":

                self.symbol,

            "Alert":

                alert["alert"],

            "Message":

                alert["message"],

            "Recommendation":

                alert["recommendation"],

            "Priority Score":

                alert["priority_score"],

        }

    # ======================================================
    # DEBUG INFORMATION
    # ======================================================

    def debug_info(

        self,

    ) -> Dict:

        return {

            "symbol":

                self.symbol,

            "liquidity_trend":

                self.liquidity_trend(),

            "buy_side_sweep":

                self.buy_side_liquidity_sweep(),

            "sell_side_sweep":

                self.sell_side_liquidity_sweep(),

            "institutional_score":

                self.institutional_liquidity_score(),

            "smart_money_score":

                self.smart_money_activity_score(),

            "priority_score":

                self.priority_score(),

            "confidence":

                self.liquidity_confidence(),

            "recommendation":

                self.professional_recommendation(),

        }

    # ======================================================
    # PRODUCTION WRAPPER
    # ======================================================

    def run(

        self,

    ) -> Dict:

        self.analyze()

        return {

            "dashboard":

                self.dashboard(),

            "scanner":

                self.scanner_summary(),

            "watchlist":

                self.export_watchlist(),

            "heatmap":

                self.export_heatmap(),

            "opportunity":

                self.opportunity_output(),

            "alert":

                self.alert_summary(),

            "recommendation":

                self.ai_recommendation(),

            "debug":

                self.debug_info(),

        }
        # ======================================================
    # BATCH ANALYSIS ENGINE
    # ======================================================

    @staticmethod
    def batch_analysis(

        analyzers: List["LiquidityEngine"],

    ) -> pd.DataFrame:

        results = []

        for engine in analyzers:

            try:

                result = engine.run()

                results.append(

                    result["scanner"]

                )

            except Exception as error:

                results.append(

                    {

                        "Symbol":

                            engine.symbol,

                        "Liquidity Trend":

                            "Error",

                        "Priority":

                            0,

                        "Rating":

                            "-",

                        "Recommendation":

                            str(error),

                        "Confidence":

                            0,

                    }

                )

        return pd.DataFrame(

            results

        )

    # ======================================================
    # MULTI STOCK ANALYZER
    # ======================================================

    @staticmethod
    def analyze_multiple(

        analyzers: List["LiquidityEngine"],

    ) -> List[Dict]:

        output = []

        for engine in analyzers:

            try:

                output.append(

                    engine.run()

                )

            except Exception:

                continue

        return output

    # ======================================================
    # SECTOR LIQUIDITY ANALYSIS
    # ======================================================

    @staticmethod
    def sector_analysis(

        sector_name: str,

        analyzers: List["LiquidityEngine"],

    ) -> Dict:

        scores = []

        recommendations = []

        for engine in analyzers:

            scores.append(

                engine.priority_score()

            )

            recommendations.append(

                engine.professional_recommendation()[

                    "recommendation"

                ]

            )

        average = (

            sum(scores) / len(scores)

            if scores

            else 0

        )

        return {

            "sector":

                sector_name,

            "stocks":

                len(analyzers),

            "average_score":

                round(

                    average,

                    2,

                ),

            "strong_buy":

                recommendations.count(

                    "Strong Buy"

                ),

            "buy":

                recommendations.count(

                    "Buy"

                ),

            "hold":

                recommendations.count(

                    "Hold"

                ),

        }

    # ======================================================
    # NSE SCANNER HELPER
    # ======================================================

    def scanner_row(

        self,

    ) -> Dict:

        recommendation = (

            self.professional_recommendation()

        )

        rating = (

            self.ai_multi_timeframe_rating()

        )

        return {

            "Symbol":

                self.symbol,

            "Liquidity Trend":

                self.liquidity_trend(),

            "Priority":

                self.priority_score(),

            "Liquidity Score":

                self.liquidity_strength_score(),

            "Institutional":

                self.institutional_liquidity_score(),

            "Rating":

                rating["rating"],

            "Recommendation":

                recommendation["recommendation"],

            "Confidence":

                recommendation["confidence"],

        }

    # ======================================================
    # PERFORMANCE STATISTICS
    # ======================================================

    @staticmethod
    def performance_statistics(

        scores: List[float],

    ) -> Dict:

        if not scores:

            return {

                "count": 0,

                "average": 0,

                "highest": 0,

                "lowest": 0,

                "median": 0,

            }

        ordered = sorted(

            scores

        )

        count = len(

            ordered

        )

        average = (

            sum(ordered)

            / count

        )

        highest = max(

            ordered

        )

        lowest = min(

            ordered

        )

        if count % 2 == 0:

            median = (

                ordered[count // 2]

                +

                ordered[(count // 2) - 1]

            ) / 2

        else:

            median = ordered[

                count // 2

            ]

        return {

            "count":

                count,

            "average":

                round(

                    average,

                    2,

                ),

            "highest":

                round(

                    highest,

                    2,

                ),

            "lowest":

                round(

                    lowest,

                    2,

                ),

            "median":

                round(

                    median,

                    2,

                ),

        }

    # ======================================================
    # CACHE MANAGEMENT
    # ======================================================

    def clear_cache(

        self,

    ) -> None:

        self.result = None

    # ======================================================
    # VALIDATION UTILITIES
    # ======================================================

    @staticmethod
    def validate_dataframe(

        dataframe: pd.DataFrame,

    ) -> bool:

        required = [

            "Open",

            "High",

            "Low",

            "Close",

            "Volume",

        ]

        return all(

            column in dataframe.columns

            for column in required

        )

    # ======================================================
    # ENTERPRISE HELPER
    # ======================================================

    @staticmethod
    def create_summary_table(

        analyzers: List["LiquidityEngine"],

    ) -> pd.DataFrame:

        rows = []

        for engine in analyzers:

            rows.append(

                engine.scanner_row()

            )

        dataframe = pd.DataFrame(

            rows

        )

        if not dataframe.empty:

            dataframe = dataframe.sort_values(

                by="Priority",

                ascending=False,

            ).reset_index(

                drop=True,

            )

        return dataframe
        # ======================================================
    # STRING REPRESENTATION
    # ======================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"LiquidityEngine("

            f"symbol='{self.symbol}', "

            f"trend='{self.liquidity_trend()}', "

            f"priority={self.priority_score():.2f})"

        )

    # ======================================================
    # HUMAN READABLE OUTPUT
    # ======================================================

    def __str__(

        self,

    ) -> str:

        recommendation = (

            self.professional_recommendation()

        )

        return (

            "\n"

            "=============================================\n"

            "        STOCKVERSITY AI LIQUIDITY ENGINE\n"

            "=============================================\n"

            f"Symbol              : {self.symbol}\n"

            f"Liquidity Trend     : {self.liquidity_trend()}\n"

            f"Priority Score      : {self.priority_score():.2f}\n"

            f"Confidence          : "

            f"{recommendation['confidence']:.2f}\n"

            f"Recommendation      : "

            f"{recommendation['recommendation']}\n"

            "============================================="

        )

    # ======================================================
    # HEALTH CHECK
    # ======================================================

    def health_check(

        self,

    ) -> Dict:

        status = "Healthy"

        issues = []

        if self.data is None:

            status = "Failed"

            issues.append(

                "DataFrame missing."

            )

        elif self.data.empty:

            status = "Failed"

            issues.append(

                "DataFrame empty."

            )

        elif not self.validate():

            status = "Failed"

            issues.append(

                "Required OHLCV columns missing."

            )

        return {

            "status": status,

            "issues": issues,

            "symbol": self.symbol,

        }

    # ======================================================
    # SELF TEST
    # ======================================================

    def self_test(

        self,

    ) -> Dict:

        tests = {

            "validation":

                self.validate(),

            "liquidity_trend":

                isinstance(

                    self.liquidity_trend(),

                    str,

                ),

            "priority_score":

                isinstance(

                    self.priority_score(),

                    float,

                ),

            "recommendation":

                isinstance(

                    self.professional_recommendation(),

                    dict,

                ),

            "analysis":

                isinstance(

                    self.analyze(),

                    LiquidityResult,

                ),

        }

        passed = all(

            tests.values()

        )

        return {

            "passed": passed,

            "tests": tests,

        }

    # ======================================================
    # PRODUCTION VALIDATION
    # ======================================================

    def production_ready(

        self,

    ) -> Dict:

        health = self.health_check()

        tests = self.self_test()

        ready = (

            health["status"] == "Healthy"

            and

            tests["passed"]

        )

        return {

            "ready": ready,

            "health": health,

            "tests": tests,

        }

    # ======================================================
    # VERSION INFORMATION
    # ======================================================

    @staticmethod

    def version(

    ) -> Dict:

        return {

            "application":

                "StockVersity Scanner Pro",

            "engine":

                "Liquidity Engine",

            "version":

                "4.0",

            "powered_by":

                "AI",

            "status":

                "Production Ready",

        }

    # ======================================================
    # RESET ENGINE
    # ======================================================

    def reset_engine(

        self,

    ) -> None:

        self.result = None

        self.reset()

    # ======================================================
    # COMPLETE ENGINE SUMMARY
    # ======================================================

    def engine_summary(

        self,

    ) -> Dict:

        return {

            "engine":

                self.version(),

            "health":

                self.health_check(),

            "production":

                self.production_ready(),

            "dashboard":

                self.dashboard(),

        }

    # ======================================================
    # END OF FILE
    # ======================================================