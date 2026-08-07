"""
==========================================================
StockVersity Scanner Pro
Market Structure Engine
Version : 4.0
Powered by AI
==========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import json
import numpy as np
import pandas as pd


# ==========================================================
# RESULT OBJECT
# ==========================================================

@dataclass
class MarketStructureResult:

    symbol: str

    structure_score: float

    trend: str

    bos: bool

    choch: bool

    swing_high: float

    swing_low: float

    recommendation: str

    confidence: float

    metrics: Dict = field(default_factory=dict)


# ==========================================================
# MARKET STRUCTURE ENGINE
# ==========================================================

class MarketStructureEngine:

    """
    Institutional Smart Money Market Structure Engine

    Features
    --------
    • Higher High Detection
    • Higher Low Detection
    • Lower High Detection
    • Lower Low Detection
    • BOS Detection
    • CHoCH Detection
    • Swing High & Swing Low
    • Support & Resistance
    • Smart Money Concepts
    """

    def __init__(self):

        self.data: Optional[pd.DataFrame] = None

        self.result: Optional[MarketStructureResult] = None

        self.symbol = ""

        self.swing_period = 5

    # ======================================================
    # LOAD DATA
    # ======================================================

    def load_data(

        self,

        symbol: str,

        dataframe: pd.DataFrame,

    ):

        self.symbol = symbol

        self.data = dataframe.copy()

        return self

    # ======================================================
    # VALIDATION
    # ======================================================

    def validate(

        self,

    ) -> bool:

        if self.data is None:

            return False

        required = [

            "Open",

            "High",

            "Low",

            "Close",

        ]

        for column in required:

            if column not in self.data.columns:

                return False

        return len(self.data) >= 50

    # ======================================================
    # RESET
    # ======================================================

    def reset(

        self,

    ):

        self.result = None

        return self

    # ======================================================
    # SWING HIGH
    # ======================================================

    def swing_high(

        self,

        period: int = 5,

    ) -> float:

        highs = self.data["High"]

        value = highs.tail(

            period

        ).max()

        return round(

            float(value),

            2,

        )

    # ======================================================
    # SWING LOW
    # ======================================================

    def swing_low(

        self,

        period: int = 5,

    ) -> float:

        lows = self.data["Low"]

        value = lows.tail(

            period

        ).min()

        return round(

            float(value),

            2,

        )

    # ======================================================
    # PREVIOUS SWING HIGH
    # ======================================================

    def previous_swing_high(

        self,

        period: int = 5,

    ) -> float:

        highs = self.data["High"]

        value = highs.iloc[

            -(period * 2):-period

        ].max()

        return round(

            float(value),

            2,

        )

    # ======================================================
    # PREVIOUS SWING LOW
    # ======================================================

    def previous_swing_low(

        self,

        period: int = 5,

    ) -> float:

        lows = self.data["Low"]

        value = lows.iloc[

            -(period * 2):-period

        ].min()

        return round(

            float(value),

            2,

        )

    # ======================================================
    # HIGHER HIGH
    # ======================================================

    def higher_high(

        self,

    ) -> bool:

        return (

            self.swing_high()

            >

            self.previous_swing_high()

        )

    # ======================================================
    # HIGHER LOW
    # ======================================================

    def higher_low(

        self,

    ) -> bool:

        return (

            self.swing_low()

            >

            self.previous_swing_low()

        )

    # ======================================================
    # LOWER HIGH
    # ======================================================

    def lower_high(

        self,

    ) -> bool:

        return (

            self.swing_high()

            <

            self.previous_swing_high()

        )

    # ======================================================
    # LOWER LOW
    # ======================================================

    def lower_low(

        self,

    ) -> bool:

        return (

            self.swing_low()

            <

            self.previous_swing_low()

        )
        # ======================================================
    # BREAK OF STRUCTURE (BOS)
    # ======================================================

    def break_of_structure(

        self,

    ) -> Dict:

        close = self.data["Close"].iloc[-1]

        bullish = (

            close >

            self.previous_swing_high()

        )

        bearish = (

            close <

            self.previous_swing_low()

        )

        if bullish:

            direction = "Bullish BOS"

        elif bearish:

            direction = "Bearish BOS"

        else:

            direction = "No BOS"

        strength = 100 if bullish or bearish else 0

        return {

            "detected":

                bullish or bearish,

            "bullish":

                bullish,

            "bearish":

                bearish,

            "direction":

                direction,

            "strength":

                strength,

        }

    # ======================================================
    # CHANGE OF CHARACTER (CHoCH)
    # ======================================================

    def change_of_character(

        self,

    ) -> Dict:

        bos = self.break_of_structure()

        hh = self.higher_high()

        hl = self.higher_low()

        lh = self.lower_high()

        ll = self.lower_low()

        bullish = (

            bos["bullish"]

            and

            lh

        )

        bearish = (

            bos["bearish"]

            and

            hl

        )

        detected = bullish or bearish

        if bullish:

            direction = "Bullish CHoCH"

        elif bearish:

            direction = "Bearish CHoCH"

        else:

            direction = "No CHoCH"

        return {

            "detected":

                detected,

            "bullish":

                bullish,

            "bearish":

                bearish,

            "direction":

                direction,

        }

    # ======================================================
    # BULLISH STRUCTURE
    # ======================================================

    def bullish_structure(

        self,

    ) -> Dict:

        hh = self.higher_high()

        hl = self.higher_low()

        score = 0

        if hh:

            score += 50

        if hl:

            score += 50

        return {

            "bullish":

                hh and hl,

            "score":

                score,

        }

    # ======================================================
    # BEARISH STRUCTURE
    # ======================================================

    def bearish_structure(

        self,

    ) -> Dict:

        lh = self.lower_high()

        ll = self.lower_low()

        score = 0

        if lh:

            score += 50

        if ll:

            score += 50

        return {

            "bearish":

                lh and ll,

            "score":

                score,

        }

    # ======================================================
    # INTERNAL STRUCTURE
    # ======================================================

    def internal_structure(

        self,

    ) -> Dict:

        close = self.data["Close"]

        sma20 = close.rolling(20).mean()

        latest = close.iloc[-1]

        average = sma20.iloc[-1]

        if latest > average:

            structure = "Bullish"

            score = 100

        elif latest < average:

            structure = "Bearish"

            score = 30

        else:

            structure = "Neutral"

            score = 60

        return {

            "structure":

                structure,

            "score":

                score,

        }

    # ======================================================
    # EXTERNAL STRUCTURE
    # ======================================================

    def external_structure(

        self,

    ) -> Dict:

        close = self.data["Close"]

        sma50 = close.rolling(50).mean()

        latest = close.iloc[-1]

        average = sma50.iloc[-1]

        if latest > average:

            structure = "Bullish"

            score = 100

        elif latest < average:

            structure = "Bearish"

            score = 30

        else:

            structure = "Neutral"

            score = 60

        return {

            "structure":

                structure,

            "score":

                score,

        }

    # ======================================================
    # TREND STATE
    # ======================================================

    def trend_state(

        self,

    ) -> str:

        internal = self.internal_structure()

        external = self.external_structure()

        if (

            internal["structure"]

            == "Bullish"

            and

            external["structure"]

            == "Bullish"

        ):

            return "Strong Uptrend"

        elif (

            internal["structure"]

            == "Bearish"

            and

            external["structure"]

            == "Bearish"

        ):

            return "Strong Downtrend"

        elif (

            internal["structure"]

            == external["structure"]

        ):

            return internal["structure"]

        return "Transition"

    # ======================================================
    # AI STRUCTURE CLASSIFICATION
    # ======================================================

    def structure_classification(

        self,

    ) -> Dict:

        bullish = self.bullish_structure()

        bearish = self.bearish_structure()

        bos = self.break_of_structure()

        choch = self.change_of_character()

        score = max(

            bullish["score"],

            bearish["score"],

        )

        if choch["detected"]:

            classification = "Trend Reversal"

        elif bos["bullish"]:

            classification = "Bullish Continuation"

        elif bos["bearish"]:

            classification = "Bearish Continuation"

        elif bullish["bullish"]:

            classification = "Bullish Structure"

        elif bearish["bearish"]:

            classification = "Bearish Structure"

        else:

            classification = "Range Bound"

        return {

            "classification":

                classification,

            "score":

                score,

        }
        # ======================================================
    # SUPPORT ZONE
    # ======================================================

    def support_zone(

        self,

        period: int = 20,

    ) -> Dict:

        lows = self.data["Low"].tail(period)

        support = float(

            lows.min()

        )

        distance = (

            (

                self.data["Close"].iloc[-1]

                -

                support

            )

            /

            support

        ) * 100

        return {

            "price": round(

                support,

                2,

            ),

            "distance": round(

                distance,

                2,

            ),

            "strength":

                "Strong"

                if distance <= 2

                else "Moderate"

                if distance <= 5

                else "Weak",

        }

    # ======================================================
    # RESISTANCE ZONE
    # ======================================================

    def resistance_zone(

        self,

        period: int = 20,

    ) -> Dict:

        highs = self.data["High"].tail(period)

        resistance = float(

            highs.max()

        )

        distance = (

            (

                resistance

                -

                self.data["Close"].iloc[-1]

            )

            /

            resistance

        ) * 100

        return {

            "price": round(

                resistance,

                2,

            ),

            "distance": round(

                distance,

                2,

            ),

            "strength":

                "Strong"

                if distance <= 2

                else "Moderate"

                if distance <= 5

                else "Weak",

        }

    # ======================================================
    # DEMAND ZONE
    # ======================================================

    def demand_zone(

        self,

    ) -> Dict:

        support = self.support_zone()

        bullish = self.bullish_structure()

        score = (

            70

            if bullish["bullish"]

            else 40

        )

        return {

            "zone":

                support["price"],

            "score":

                score,

            "active":

                bullish["bullish"],

        }

    # ======================================================
    # SUPPLY ZONE
    # ======================================================

    def supply_zone(

        self,

    ) -> Dict:

        resistance = self.resistance_zone()

        bearish = self.bearish_structure()

        score = (

            70

            if bearish["bearish"]

            else 40

        )

        return {

            "zone":

                resistance["price"],

            "score":

                score,

            "active":

                bearish["bearish"],

        }

    # ======================================================
    # ORDER BLOCK DETECTION
    # ======================================================

    def order_block(

        self,

    ) -> Dict:

        open_ = self.data["Open"]

        close = self.data["Close"]

        high = self.data["High"]

        low = self.data["Low"]

        bullish = (

            close.iloc[-2]

            <

            open_.iloc[-2]

            and

            close.iloc[-1]

            >

            high.iloc[-2]

        )

        bearish = (

            close.iloc[-2]

            >

            open_.iloc[-2]

            and

            close.iloc[-1]

            <

            low.iloc[-2]

        )

        if bullish:

            block = "Bullish Order Block"

        elif bearish:

            block = "Bearish Order Block"

        else:

            block = "None"

        return {

            "detected":

                bullish or bearish,

            "type":

                block,

            "bullish":

                bullish,

            "bearish":

                bearish,

        }

    # ======================================================
    # FAIR VALUE GAP (FVG)
    # ======================================================

    def fair_value_gap(

        self,

    ) -> Dict:

        high = self.data["High"]

        low = self.data["Low"]

        bullish = (

            low.iloc[-1]

            >

            high.iloc[-3]

        )

        bearish = (

            high.iloc[-1]

            <

            low.iloc[-3]

        )

        gap = 0.0

        direction = "None"

        if bullish:

            gap = (

                low.iloc[-1]

                -

                high.iloc[-3]

            )

            direction = "Bullish"

        elif bearish:

            gap = (

                low.iloc[-3]

                -

                high.iloc[-1]

            )

            direction = "Bearish"

        return {

            "detected":

                bullish or bearish,

            "direction":

                direction,

            "gap_size":

                round(

                    float(gap),

                    2,

                ),

        }

    # ======================================================
    # LIQUIDITY SWEEP
    # ======================================================

    def liquidity_sweep(

        self,

    ) -> Dict:

        high = self.data["High"]

        low = self.data["Low"]

        close = self.data["Close"]

        bullish = (

            low.iloc[-1]

            <

            self.previous_swing_low()

            and

            close.iloc[-1]

            >

            self.previous_swing_low()

        )

        bearish = (

            high.iloc[-1]

            >

            self.previous_swing_high()

            and

            close.iloc[-1]

            <

            self.previous_swing_high()

        )

        return {

            "detected":

                bullish or bearish,

            "bullish":

                bullish,

            "bearish":

                bearish,

        }

    # ======================================================
    # SMART MONEY STRUCTURE SCORE
    # ======================================================

    def smart_money_score(

        self,

    ) -> float:

        score = 0

        if self.order_block()["detected"]:

            score += 25

        if self.fair_value_gap()["detected"]:

            score += 25

        if self.liquidity_sweep()["detected"]:

            score += 25

        if self.break_of_structure()["detected"]:

            score += 25

        return round(

            min(

                score,

                100,

            ),

            2,

        )
        # ======================================================
    # STRUCTURE STRENGTH SCORE
    # ======================================================

    def structure_strength_score(

        self,

    ) -> float:

        bullish = self.bullish_structure()

        bearish = self.bearish_structure()

        bos = self.break_of_structure()

        smc = self.smart_money_score()

        score = (

            max(

                bullish["score"],

                bearish["score"],

            ) * 0.40

            +

            bos["strength"] * 0.30

            +

            smc * 0.30

        )

        return round(

            min(

                score,

                100,

            ),

            2,

        )

    # ======================================================
    # TREND CONTINUATION PROBABILITY
    # ======================================================

    def trend_continuation_probability(

        self,

    ) -> Dict:

        trend = self.trend_state()

        structure = self.structure_strength_score()

        probability = structure

        if trend == "Strong Uptrend":

            probability += 10

        elif trend == "Strong Downtrend":

            probability += 5

        probability = min(

            probability,

            100,

        )

        return {

            "probability": round(

                probability,

                2,

            ),

            "trend": trend,

        }

    # ======================================================
    # REVERSAL PROBABILITY
    # ======================================================

    def reversal_probability(

        self,

    ) -> Dict:

        choch = self.change_of_character()

        sweep = self.liquidity_sweep()

        probability = 0

        if choch["detected"]:

            probability += 60

        if sweep["detected"]:

            probability += 40

        probability = min(

            probability,

            100,

        )

        if probability >= 80:

            level = "Very High"

        elif probability >= 60:

            level = "High"

        elif probability >= 40:

            level = "Moderate"

        else:

            level = "Low"

        return {

            "probability": probability,

            "level": level,

        }

    # ======================================================
    # BREAKOUT READINESS
    # ======================================================

    def breakout_readiness(

        self,

    ) -> Dict:

        bos = self.break_of_structure()

        resistance = self.resistance_zone()

        support = self.support_zone()

        structure = self.structure_strength_score()

        close = self.data["Close"].iloc[-1]

        resistance_distance = abs(

            resistance["price"]

            -

            close

        ) / close * 100

        support_distance = abs(

            close

            -

            support["price"]

        ) / close * 100

        ready = (

            bos["bullish"]

            or

            resistance_distance <= 2

        )

        score = (

            structure * 0.70

            +

            (

                30

                if ready

                else 10

            )

        )

        return {

            "ready": ready,

            "score": round(

                min(

                    score,

                    100,

                ),

                2,

            ),

            "support_distance": round(

                support_distance,

                2,

            ),

            "resistance_distance": round(

                resistance_distance,

                2,

            ),

        }

    # ======================================================
    # PULLBACK OPPORTUNITY
    # ======================================================

    def pullback_opportunity(

        self,

    ) -> Dict:

        support = self.support_zone()

        bullish = self.bullish_structure()

        close = self.data["Close"].iloc[-1]

        distance = abs(

            close

            -

            support["price"]

        ) / close * 100

        opportunity = (

            bullish["bullish"]

            and

            distance <= 3

        )

        score = (

            90

            if opportunity

            else 45

        )

        return {

            "opportunity": opportunity,

            "score": score,

            "distance": round(

                distance,

                2,

            ),

        }

    # ======================================================
    # STRUCTURE CONFIDENCE
    # ======================================================

    def structure_confidence(

        self,

    ) -> float:

        strength = self.structure_strength_score()

        continuation = (

            self.trend_continuation_probability()

        )

        smart_money = self.smart_money_score()

        confidence = (

            strength * 0.40

            +

            continuation["probability"] * 0.35

            +

            smart_money * 0.25

        )

        return round(

            min(

                confidence,

                100,

            ),

            2,

        )

    # ======================================================
    # AI STRUCTURE RATING
    # ======================================================

    def ai_structure_rating(

        self,

    ) -> Dict:

        score = self.structure_confidence()

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
    # PROFESSIONAL RECOMMENDATION
    # ======================================================

    def professional_recommendation(

        self,

    ) -> Dict:

        rating = self.ai_structure_rating()

        breakout = self.breakout_readiness()

        reversal = self.reversal_probability()

        if (

            rating["score"] >= 85

            and

            breakout["ready"]

        ):

            recommendation = "Strong Buy"

        elif rating["score"] >= 70:

            recommendation = "Buy"

        elif reversal["probability"] >= 70:

            recommendation = "Watch for Reversal"

        elif rating["score"] >= 50:

            recommendation = "Hold"

        else:

            recommendation = "Avoid"

        return {

            "recommendation": recommendation,

            "confidence": rating["score"],

            "rating": rating["rating"],

        }
        # ======================================================
    # INTRADAY STRUCTURE STRENGTH
    # ======================================================

    def intraday_structure_strength(

        self,

    ) -> Dict:

        structure = self.structure_strength_score()

        breakout = self.breakout_readiness()

        smart_money = self.smart_money_score()

        score = (

            structure * 0.45 +

            breakout["score"] * 0.35 +

            smart_money * 0.20

        )

        score = min(score, 100)

        return {

            "score": round(score, 2),

            "strength":

                "Strong"

                if score >= 75

                else "Moderate"

                if score >= 50

                else "Weak",

        }

    # ======================================================
    # SWING STRUCTURE STRENGTH
    # ======================================================

    def swing_structure_strength(

        self,

    ) -> Dict:

        continuation = (

            self.trend_continuation_probability()

        )

        pullback = (

            self.pullback_opportunity()

        )

        confidence = (

            self.structure_confidence()

        )

        score = (

            continuation["probability"] * 0.40 +

            confidence * 0.40 +

            pullback["score"] * 0.20

        )

        return {

            "score": round(

                min(score, 100),

                2,

            ),

            "strength":

                "Strong"

                if score >= 75

                else "Moderate"

                if score >= 55

                else "Weak",

        }

    # ======================================================
    # POSITIONAL STRUCTURE STRENGTH
    # ======================================================

    def positional_structure_strength(

        self,

    ) -> Dict:

        confidence = (

            self.structure_confidence()

        )

        smart_money = (

            self.smart_money_score()

        )

        trend = (

            self.trend_continuation_probability()

        )

        score = (

            confidence * 0.45 +

            smart_money * 0.30 +

            trend["probability"] * 0.25

        )

        return {

            "score": round(

                min(score, 100),

                2,

            ),

            "strength":

                "Strong"

                if score >= 80

                else "Moderate"

                if score >= 60

                else "Weak",

        }

    # ======================================================
    # MULTI-TIMEFRAME ALIGNMENT
    # ======================================================

    def timeframe_alignment(

        self,

    ) -> Dict:

        intraday = (

            self.intraday_structure_strength()

        )

        swing = (

            self.swing_structure_strength()

        )

        positional = (

            self.positional_structure_strength()

        )

        score = (

            intraday["score"] +

            swing["score"] +

            positional["score"]

        ) / 3

        aligned = (

            intraday["strength"] == swing["strength"]

            and

            swing["strength"] == positional["strength"]

        )

        return {

            "aligned": aligned,

            "score": round(score, 2),

        }

    # ======================================================
    # TREND CONSISTENCY SCORE
    # ======================================================

    def trend_consistency_score(

        self,

    ) -> float:

        alignment = (

            self.timeframe_alignment()

        )

        trend = (

            self.trend_state()

        )

        bonus = 10 if (

            trend in [

                "Strong Uptrend",

                "Strong Downtrend",

            ]

        ) else 0

        score = (

            alignment["score"] +

            bonus

        )

        return round(

            min(score, 100),

            2,

        )

    # ======================================================
    # STRUCTURE MOMENTUM SCORE
    # ======================================================

    def structure_momentum_score(

        self,

    ) -> float:

        bos = self.break_of_structure()

        confidence = (

            self.structure_confidence()

        )

        continuation = (

            self.trend_continuation_probability()

        )

        score = (

            bos["strength"] * 0.40 +

            continuation["probability"] * 0.35 +

            confidence * 0.25

        )

        return round(

            min(score, 100),

            2,

        )

    # ======================================================
    # INSTITUTIONAL STRUCTURE SCORE
    # ======================================================

    def institutional_structure_score(

        self,

    ) -> float:

        smart_money = (

            self.smart_money_score()

        )

        order_block = (

            self.order_block()

        )

        liquidity = (

            self.liquidity_sweep()

        )

        score = smart_money

        if order_block["detected"]:

            score += 15

        if liquidity["detected"]:

            score += 10

        return round(

            min(score, 100),

            2,

        )

    # ======================================================
    # AI MULTI-TIMEFRAME STRUCTURE RATING
    # ======================================================

    def ai_multi_timeframe_rating(

        self,

    ) -> Dict:

        alignment = (

            self.timeframe_alignment()

        )

        consistency = (

            self.trend_consistency_score()

        )

        institutional = (

            self.institutional_structure_score()

        )

        score = (

            alignment["score"] * 0.40 +

            consistency * 0.30 +

            institutional * 0.30

        )

        score = round(

            min(score, 100),

            2,

        )

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
    # STRUCTURE OPPORTUNITY SCORE
    # ======================================================

    def structure_opportunity_score(

        self,

    ) -> float:

        confidence = self.structure_confidence()

        breakout = self.breakout_readiness()

        pullback = self.pullback_opportunity()

        institutional = self.institutional_structure_score()

        score = (

            confidence * 0.35 +

            breakout["score"] * 0.30 +

            pullback["score"] * 0.20 +

            institutional * 0.15

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

        opportunity = self.structure_opportunity_score()

        mtf = self.ai_multi_timeframe_rating()

        recommendation = self.professional_recommendation()

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
    # MARKET STRUCTURE RANK
    # ======================================================

    def structure_rank(

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

                - rank

                + 1

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

            "structure_score":

                self.structure_strength_score(),

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

            "Trend":

                self.trend_state(),

            "Structure Score":

                self.structure_strength_score(),

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

                self.trend_state(),

            "color":

                color,

        }

    # ======================================================
    # ALERT GENERATOR
    # ======================================================

    def generate_alert(

        self,

    ) -> Dict:

        breakout = self.breakout_readiness()

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

                "shows institutional "

                "market structure breakout."

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
    # MASTER MARKET STRUCTURE ANALYSIS
    # ======================================================

    def analyze(

        self,

    ) -> MarketStructureResult:

        if not self.validate():

            raise ValueError(

                "Invalid market structure data."

            )

        recommendation = (

            self.professional_recommendation()

        )

        bos = self.break_of_structure()

        choch = self.change_of_character()

        self.result = MarketStructureResult(

            symbol=self.symbol,

            structure_score=self.priority_score(),

            trend=self.trend_state(),

            bos=bos["detected"],

            choch=choch["detected"],

            swing_high=self.swing_high(),

            swing_low=self.swing_low(),

            recommendation=recommendation["recommendation"],

            confidence=recommendation["confidence"],

            metrics={

                "Structure Strength":

                    self.structure_strength_score(),

                "Smart Money Score":

                    self.smart_money_score(),

                "Institutional Score":

                    self.institutional_structure_score(),

                "Opportunity Score":

                    self.structure_opportunity_score(),

                "Priority Score":

                    self.priority_score(),

                "Trend Consistency":

                    self.trend_consistency_score(),

                "Breakout Score":

                    self.breakout_readiness()["score"],

                "Pullback Score":

                    self.pullback_opportunity()["score"],

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

            "Trend":

                self.result.trend,

            "Structure Score":

                self.result.structure_score,

            "BOS":

                self.result.bos,

            "CHoCH":

                self.result.choch,

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

            "structure_score":

                self.result.structure_score,

            "trend":

                self.result.trend,

            "bos":

                self.result.bos,

            "choch":

                self.result.choch,

            "swing_high":

                self.result.swing_high,

            "swing_low":

                self.result.swing_low,

            "recommendation":

                self.result.recommendation,

            "confidence":

                self.result.confidence,

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

    ):

        if self.result is None:

            self.analyze()

        print("=" * 70)

        print("STOCKVERSITY AI MARKET STRUCTURE REPORT")

        print("=" * 70)

        print(f"Symbol               : {self.result.symbol}")

        print(f"Trend                : {self.result.trend}")

        print(f"Structure Score      : {self.result.structure_score:.2f}")

        print(f"BOS                  : {self.result.bos}")

        print(f"CHoCH                : {self.result.choch}")

        print(f"Swing High           : {self.result.swing_high:.2f}")

        print(f"Swing Low            : {self.result.swing_low:.2f}")

        print(f"Recommendation       : {self.result.recommendation}")

        print(f"Confidence           : {self.result.confidence:.2f}")

        print()

        print("METRICS")

        print("-" * 70)

        for key, value in self.result.metrics.items():

            print(f"{key:30} : {value}")

        print("=" * 70)
            # ======================================================
    # MARKET STRUCTURE RANKING ENGINE
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

        df = pd.DataFrame(

            {

                "Symbol": symbols,

                "Score": scores,

            }

        )

        df = df.sort_values(

            by="Score",

            ascending=False,

        ).reset_index(

            drop=True,

        )

        df["Rank"] = (

            df.index + 1

        )

        df["Grade"] = df["Score"].apply(

            lambda x:

            "A+"

            if x >= 90 else

            "A"

            if x >= 80 else

            "B+"

            if x >= 70 else

            "B"

            if x >= 60 else

            "C"

            if x >= 50 else

            "D"

        )

        return df

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

            "Trend":

                self.trend_state(),

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

            self.ai_multi_timeframe_rating()["rating"]

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

        alert = self.generate_alert()

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

            "trend":

                self.trend_state(),

            "bos":

                self.break_of_structure(),

            "choch":

                self.change_of_character(),

            "smart_money":

                self.smart_money_score(),

            "priority":

                self.priority_score(),

            "confidence":

                self.structure_confidence(),

            "institutional":

                self.institutional_structure_score(),

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
        analyzers: List["MarketStructureEngine"],
    ) -> pd.DataFrame:

        results = []

        for engine in analyzers:

            try:

                result = engine.run()

                scanner = result["scanner"]

                results.append(scanner)

            except Exception as error:

                results.append(
                    {
                        "Symbol": engine.symbol,
                        "Trend": "Error",
                        "Priority": 0,
                        "Rating": "-",
                        "Recommendation": str(error),
                        "Confidence": 0,
                    }
                )

        return pd.DataFrame(results)

    # ======================================================
    # MULTI STOCK ANALYZER
    # ======================================================

    @staticmethod
    def analyze_multiple(
        analyzers: List["MarketStructureEngine"],
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
    # SECTOR ANALYSIS
    # ======================================================

    @staticmethod
    def sector_analysis(
        sector_name: str,
        analyzers: List["MarketStructureEngine"],
    ) -> Dict:

        scores = []

        recommendations = []

        for engine in analyzers:

            score = engine.priority_score()

            scores.append(score)

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

        strong_buy = recommendations.count(
            "Strong Buy"
        )

        buy = recommendations.count(
            "Buy"
        )

        hold = recommendations.count(
            "Hold"
        )

        return {

            "sector": sector_name,

            "stocks": len(analyzers),

            "average_score": round(
                average,
                2,
            ),

            "strong_buy": strong_buy,

            "buy": buy,

            "hold": hold,

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

            "Symbol": self.symbol,

            "Trend": self.trend_state(),

            "Priority": self.priority_score(),

            "Structure": self.structure_strength_score(),

            "Institutional": self.institutional_structure_score(),

            "Rating": rating["rating"],

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

        ordered = sorted(scores)

        count = len(ordered)

        average = sum(ordered) / count

        highest = max(ordered)

        lowest = min(ordered)

        if count % 2 == 0:

            median = (

                ordered[count // 2]

                +

                ordered[(count // 2) - 1]

            ) / 2

        else:

            median = ordered[count // 2]

        return {

            "count": count,

            "average": round(
                average,
                2,
            ),

            "highest": round(
                highest,
                2,
            ),

            "lowest": round(
                lowest,
                2,
            ),

            "median": round(
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

        analyzers: List["MarketStructureEngine"],

    ) -> pd.DataFrame:

        rows = []

        for engine in analyzers:

            rows.append(

                engine.scanner_row()

            )

        dataframe = pd.DataFrame(rows)

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

            f"MarketStructureEngine("

            f"symbol='{self.symbol}', "

            f"trend='{self.trend_state()}', "

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

            "     STOCKVERSITY AI MARKET STRUCTURE\n"

            "=============================================\n"

            f"Symbol          : {self.symbol}\n"

            f"Trend           : {self.trend_state()}\n"

            f"Priority Score  : {self.priority_score():.2f}\n"

            f"Confidence      : "

            f"{recommendation['confidence']:.2f}\n"

            f"Recommendation  : "

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

            "trend_state":

                isinstance(

                    self.trend_state(),

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

                    MarketStructureResult,

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

        test = self.self_test()

        ready = (

            health["status"] == "Healthy"

            and

            test["passed"]

        )

        return {

            "ready": ready,

            "health": health,

            "tests": test,

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

                "Market Structure Engine",

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