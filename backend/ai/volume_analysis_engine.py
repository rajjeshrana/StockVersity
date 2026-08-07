"""
==========================================================
StockVersity Scanner Pro
Volume Analysis Engine
Version : 4.0
Powered by AI
==========================================================
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np
import pandas as pd


# ==========================================================
# RESULT OBJECT
# ==========================================================

@dataclass
class VolumeResult:

    symbol: str

    volume_score: float

    rvol: float

    delivery_score: float

    accumulation_score: float

    distribution_score: float

    institutional_activity: str

    recommendation: str

    confidence: float

    metrics: Dict = field(default_factory=dict)


# ==========================================================
# VOLUME ANALYSIS ENGINE
# ==========================================================

class VolumeAnalysisEngine:

    """
    Professional AI Volume Engine

    Features
    --------
    • Relative Volume (RVOL)
    • Delivery Analysis
    • Volume Spike Detection
    • Accumulation Detection
    • Distribution Detection
    • Institutional Activity
    • Breakout Volume Validation
    • Volume Dry-up Detection
    • Smart Money Analysis
    """

    def __init__(self):

        self.data: Optional[pd.DataFrame] = None

        self.result: Optional[VolumeResult] = None

        self.symbol = ""

        self.lookback = 20

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

            "Volume",

        ]

        for column in required:

            if column not in self.data.columns:

                return False

        return len(self.data) >= self.lookback

    # ======================================================
    # RESET
    # ======================================================

    def reset(

        self,

    ):

        self.result = None

        return self

    # ======================================================
    # CURRENT VOLUME
    # ======================================================

    def current_volume(

        self,

    ) -> float:

        return float(

            self.data["Volume"].iloc[-1]

        )

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

        average = self.average_volume(period)

        if average <= 0:

            return 0.0

        return round(

            self.current_volume()

            / average,

            2,

        )

    # ======================================================
    # VOLUME CHANGE %
    # ======================================================

    def volume_change(

        self,

    ) -> float:

        volume = self.data["Volume"]

        previous = volume.iloc[-2]

        if previous == 0:

            return 0.0

        change = (

            (

                volume.iloc[-1]

                -

                previous

            )

            /

            previous

        ) * 100

        return round(

            change,

            2,

        )

    # ======================================================
    # VOLUME MOVING AVERAGE
    # ======================================================

    def volume_sma(

        self,

        period: int = 20,

    ) -> float:

        return round(

            self.average_volume(period),

            2,

        )

    # ======================================================
    # VOLUME TREND
    # ======================================================

    def volume_trend(

        self,

    ) -> str:

        volume = self.data["Volume"]

        sma20 = volume.rolling(20).mean()

        sma50 = volume.rolling(50).mean()

        if sma20.iloc[-1] > sma50.iloc[-1]:

            return "Increasing"

        elif sma20.iloc[-1] < sma50.iloc[-1]:

            return "Decreasing"

        return "Neutral"

    # ======================================================
    # PRICE-VOLUME RELATIONSHIP
    # ======================================================

    def price_volume_relationship(

        self,

    ) -> Dict:

        close = self.data["Close"]

        volume = self.data["Volume"]

        price_up = close.iloc[-1] > close.iloc[-2]

        volume_up = volume.iloc[-1] > volume.iloc[-2]

        if price_up and volume_up:

            relation = "Bullish Confirmation"

        elif (not price_up) and volume_up:

            relation = "Bearish Distribution"

        elif price_up and (not volume_up):

            relation = "Weak Rally"

        else:

            relation = "Low Participation"

        return {

            "price_change":

                round(

                    close.pct_change().iloc[-1] * 100,

                    2,

                ),

            "volume_change":

                self.volume_change(),

            "relationship":

                relation,

        }
        # ======================================================
    # VOLUME SPIKE DETECTION
    # ======================================================

    def volume_spike(

        self,

        threshold: float = 2.0,

    ) -> Dict:

        rvol = self.relative_volume()

        detected = rvol >= threshold

        strength = min(

            rvol * 25,

            100,

        )

        return {

            "detected": detected,

            "rvol": rvol,

            "strength": round(

                strength,

                2,

            ),

        }

    # ======================================================
    # CLIMACTIC VOLUME
    # ======================================================

    def climactic_volume(

        self,

    ) -> Dict:

        volume = self.current_volume()

        avg = self.average_volume()

        close = self.data["Close"]

        candle = abs(

            close.iloc[-1]

            -

            close.iloc[-2]

        )

        detected = (

            volume >= avg * 3

            and

            candle > 0

        )

        return {

            "detected": detected,

            "multiple": round(

                volume / avg,

                2,

            ),

            "description":

                "Possible Blow-off"

                if detected

                else "Normal",

        }

    # ======================================================
    # VOLUME DRY-UP (VCP)
    # ======================================================

    def volume_dryup(

        self,

        period: int = 10,

    ) -> Dict:

        volume = self.data["Volume"]

        recent = volume.tail(period)

        avg20 = self.average_volume()

        ratio = (

            recent.mean()

            /

            avg20

        )

        dryup = ratio < 0.60

        return {

            "detected": dryup,

            "ratio": round(

                ratio,

                2,

            ),

            "quality":

                "Excellent"

                if ratio < 0.40

                else "Good"

                if ratio < 0.60

                else "Normal",

        }

    # ======================================================
    # BREAKOUT VOLUME CONFIRMATION
    # ======================================================

    def breakout_volume_confirmation(

        self,

    ) -> Dict:

        close = self.data["Close"]

        high = self.data["High"]

        breakout = (

            close.iloc[-1]

            >

            high.iloc[-21:-1].max()

        )

        rvol = self.relative_volume()

        confirmed = (

            breakout

            and

            rvol >= 1.50

        )

        score = (

            min(

                rvol * 50,

                100,

            )

            if confirmed

            else 0

        )

        return {

            "breakout": breakout,

            "confirmed": confirmed,

            "score": round(

                score,

                2,

            ),

        }

    # ======================================================
    # VOLUME EXHAUSTION
    # ======================================================

    def volume_exhaustion(

        self,

    ) -> Dict:

        spike = self.volume_spike()

        close = self.data["Close"]

        price_change = abs(

            close.pct_change().iloc[-1]

        ) * 100

        exhausted = (

            spike["detected"]

            and

            price_change < 0.50

        )

        return {

            "detected": exhausted,

            "price_change": round(

                price_change,

                2,

            ),

            "description":

                "Buying/Selling Exhaustion"

                if exhausted

                else "Healthy",

        }

    # ======================================================
    # CONSECUTIVE HIGH VOLUME
    # ======================================================

    def consecutive_high_volume(

        self,

        days: int = 3,

    ) -> Dict:

        volume = self.data["Volume"]

        avg = self.average_volume()

        recent = volume.tail(days)

        count = int(

            (

                recent >

                avg * 1.50

            ).sum()

        )

        detected = count == days

        return {

            "detected": detected,

            "count": count,

            "required": days,

        }

    # ======================================================
    # GAP VOLUME ANALYSIS
    # ======================================================

    def gap_volume_analysis(

        self,

    ) -> Dict:

        open_ = self.data["Open"]

        close = self.data["Close"]

        previous_close = close.iloc[-2]

        gap = (

            (

                open_.iloc[-1]

                -

                previous_close

            )

            /

            previous_close

        ) * 100

        rvol = self.relative_volume()

        quality = "Normal"

        if abs(gap) >= 2 and rvol >= 2:

            quality = "Institutional"

        elif abs(gap) >= 1:

            quality = "Tradable"

        return {

            "gap_percent": round(

                gap,

                2,

            ),

            "relative_volume": rvol,

            "quality": quality,

        }

    # ======================================================
    # AI VOLUME EVENT
    # ======================================================

    def volume_event(

        self,

    ) -> Dict:

        spike = self.volume_spike()

        climax = self.climactic_volume()

        dryup = self.volume_dryup()

        breakout = self.breakout_volume_confirmation()

        exhaustion = self.volume_exhaustion()

        if breakout["confirmed"]:

            event = "Breakout Confirmation"

        elif climax["detected"]:

            event = "Climactic Volume"

        elif dryup["detected"]:

            event = "Volume Dry-up"

        elif exhaustion["detected"]:

            event = "Volume Exhaustion"

        elif spike["detected"]:

            event = "Volume Spike"

        else:

            event = "Normal"

        return {

            "event": event,

            "spike": spike,

            "climactic": climax,

            "dryup": dryup,

            "breakout": breakout,

            "exhaustion": exhaustion,

        }
        # ======================================================
    # ACCUMULATION / DISTRIBUTION LINE (ADL)
    # ======================================================

    def accumulation_distribution(

        self,

    ) -> float:

        high = self.data["High"]

        low = self.data["Low"]

        close = self.data["Close"]

        volume = self.data["Volume"]

        multiplier = (

            (

                (close - low)

                -

                (high - close)

            )

            /

            (high - low).replace(

                0,

                np.nan,

            )

        ).fillna(0)

        money_flow = multiplier * volume

        adl = money_flow.cumsum()

        return round(

            float(

                adl.iloc[-1]

            ),

            2,

        )

    # ======================================================
    # ON BALANCE VOLUME
    # ======================================================

    def on_balance_volume(

        self,

    ) -> float:

        close = self.data["Close"]

        volume = self.data["Volume"]

        direction = np.sign(

            close.diff()

        ).fillna(0)

        obv = (

            direction *

            volume

        ).cumsum()

        return round(

            float(

                obv.iloc[-1]

            ),

            2,

        )

    # ======================================================
    # CHAIKIN MONEY FLOW
    # ======================================================

    def chaikin_money_flow(

        self,

        period: int = 20,

    ) -> float:

        high = self.data["High"]

        low = self.data["Low"]

        close = self.data["Close"]

        volume = self.data["Volume"]

        multiplier = (

            (

                (close - low)

                -

                (high - close)

            )

            /

            (high - low).replace(

                0,

                np.nan,

            )

        ).fillna(0)

        mf_volume = multiplier * volume

        cmf = (

            mf_volume

            .rolling(period)

            .sum()

            /

            volume

            .rolling(period)

            .sum()

        )

        return round(

            float(

                cmf.iloc[-1]

            ),

            4,

        )

    # ======================================================
    # VOLUME PRICE TREND
    # ======================================================

    def volume_price_trend(

        self,

    ) -> float:

        close = self.data["Close"]

        volume = self.data["Volume"]

        pct = close.pct_change().fillna(0)

        vpt = (

            volume *

            pct

        ).cumsum()

        return round(

            float(

                vpt.iloc[-1]

            ),

            2,

        )

    # ======================================================
    # EASE OF MOVEMENT
    # ======================================================

    def ease_of_movement(

        self,

        period: int = 14,

    ) -> float:

        high = self.data["High"]

        low = self.data["Low"]

        volume = self.data["Volume"]

        midpoint = (

            high +

            low

        ) / 2

        distance = midpoint.diff()

        box_ratio = (

            volume /

            (high - low).replace(

                0,

                np.nan,

            )

        )

        emv = (

            distance /

            box_ratio

        ).rolling(period).mean()

        return round(

            float(

                emv.iloc[-1]

            ),

            4,

        )

    # ======================================================
    # FORCE INDEX
    # ======================================================

    def force_index(

        self,

        period: int = 13,

    ) -> float:

        close = self.data["Close"]

        volume = self.data["Volume"]

        fi = (

            close.diff()

            *

            volume

        )

        force = fi.ewm(

            span=period,

            adjust=False,

        ).mean()

        return round(

            float(

                force.iloc[-1]

            ),

            2,

        )

    # ======================================================
    # INSTITUTIONAL BUYING / SELLING SCORE
    # ======================================================

    def institutional_score(

        self,

    ) -> Dict:

        rvol = self.relative_volume()

        cmf = self.chaikin_money_flow()

        force = self.force_index()

        score = (

            min(

                rvol * 30,

                30,

            )

            +

            max(

                min(

                    cmf * 100,

                    35,

                ),

                -35,

            )

            +

            (

                35

                if force > 0

                else 10

            )

        )

        score = max(

            0,

            min(score, 100),

        )

        if score >= 80:

            activity = "Strong Institutional Buying"

        elif score >= 65:

            activity = "Institutional Buying"

        elif score >= 45:

            activity = "Neutral"

        elif score >= 25:

            activity = "Institutional Selling"

        else:

            activity = "Strong Institutional Selling"

        return {

            "score": round(

                score,

                2,

            ),

            "activity": activity,

        }

    # ======================================================
    # SMART MONEY VOLUME SCORE
    # ======================================================

    def smart_money_score(

        self,

    ) -> float:

        rvol = self.relative_volume()

        breakout = self.breakout_volume_confirmation()

        institution = self.institutional_score()["score"]

        score = (

            min(

                rvol * 20,

                20,

            )

            +

            institution * 0.60

            +

            breakout["score"] * 0.20

        )

        return round(

            min(

                score,

                100,

            ),

            2,

        )
        # ======================================================
    # VOLUME QUALITY SCORE
    # ======================================================

    def volume_quality_score(

        self,

    ) -> float:

        rvol = self.relative_volume()

        institution = self.institutional_score()["score"]

        breakout = self.breakout_volume_confirmation()["score"]

        trend = self.volume_trend()

        trend_score = {

            "Increasing": 100,

            "Neutral": 60,

            "Decreasing": 30,

        }.get(

            trend,

            50,

        )

        score = (

            min(

                rvol * 20,

                20,

            )

            +

            institution * 0.40

            +

            breakout * 0.25

            +

            trend_score * 0.15

        )

        return round(

            min(

                score,

                100,

            ),

            2,

        )

    # ======================================================
    # VOLUME TREND STRENGTH
    # ======================================================

    def volume_trend_strength(

        self,

    ) -> Dict:

        sma20 = self.data["Volume"].rolling(20).mean()

        sma50 = self.data["Volume"].rolling(50).mean()

        strength = (

            sma20.iloc[-1]

            /

            sma50.iloc[-1]

            if sma50.iloc[-1] != 0

            else 0

        )

        score = min(

            strength * 100,

            100,

        )

        if score >= 90:

            trend = "Very Strong"

        elif score >= 75:

            trend = "Strong"

        elif score >= 55:

            trend = "Moderate"

        else:

            trend = "Weak"

        return {

            "strength": round(

                strength,

                2,

            ),

            "score": round(

                score,

                2,

            ),

            "trend": trend,

        }

    # ======================================================
    # HEALTHY VOLUME DETECTION
    # ======================================================

    def healthy_volume(

        self,

    ) -> Dict:

        rvol = self.relative_volume()

        relationship = self.price_volume_relationship()

        healthy = (

            1.20 <= rvol <= 3.00

            and

            relationship["relationship"]

            == "Bullish Confirmation"

        )

        score = 100 if healthy else max(

            20,

            rvol * 30,

        )

        return {

            "healthy": healthy,

            "score": round(

                min(score, 100),

                2,

            ),

            "relationship":

                relationship["relationship"],

        }

    # ======================================================
    # BREAKOUT QUALITY SCORE
    # ======================================================

    def breakout_quality_score(

        self,

    ) -> float:

        breakout = self.breakout_volume_confirmation()

        smart_money = self.smart_money_score()

        score = (

            breakout["score"] * 0.60

            +

            smart_money * 0.40

        )

        return round(

            min(

                score,

                100,

            ),

            2,

        )

    # ======================================================
    # EXHAUSTION RISK SCORE
    # ======================================================

    def exhaustion_risk(

        self,

    ) -> Dict:

        exhaustion = self.volume_exhaustion()

        climax = self.climactic_volume()

        risk = 0

        if exhaustion["detected"]:

            risk += 60

        if climax["detected"]:

            risk += 40

        risk = min(

            risk,

            100,

        )

        if risk >= 80:

            level = "Extreme"

        elif risk >= 60:

            level = "High"

        elif risk >= 40:

            level = "Moderate"

        else:

            level = "Low"

        return {

            "score": risk,

            "level": level,

        }

    # ======================================================
    # SMART MONEY CONFIDENCE
    # ======================================================

    def smart_money_confidence(

        self,

    ) -> float:

        smart = self.smart_money_score()

        institution = self.institutional_score()["score"]

        confidence = (

            smart * 0.70

            +

            institution * 0.30

        )

        return round(

            min(

                confidence,

                100,

            ),

            2,

        )

    # ======================================================
    # AI VOLUME RATING
    # ======================================================

    def ai_volume_rating(

        self,

    ) -> Dict:

        score = (

            self.volume_quality_score() * 0.35

            +

            self.smart_money_confidence() * 0.30

            +

            self.breakout_quality_score() * 0.20

            +

            self.healthy_volume()["score"] * 0.15

        )

        score = round(

            min(

                score,

                100,

            ),

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
    # PROFESSIONAL RECOMMENDATION
    # ======================================================

    def professional_recommendation(

        self,

    ) -> Dict:

        ai = self.ai_volume_rating()

        exhaustion = self.exhaustion_risk()

        if ai["score"] >= 85 and exhaustion["score"] < 40:

            recommendation = "Strong Buy"

        elif ai["score"] >= 70:

            recommendation = "Buy"

        elif ai["score"] >= 55:

            recommendation = "Watch"

        elif ai["score"] >= 40:

            recommendation = "Avoid"

        else:

            recommendation = "Strong Avoid"

        return {

            "recommendation": recommendation,

            "confidence": ai["score"],

            "rating": ai["rating"],

        }
        # ======================================================
    # DELIVERY VOLUME SCORE
    # ======================================================

    def delivery_volume_score(

        self,

        delivery_percentage: Optional[float] = None,

    ) -> Dict:

        if delivery_percentage is None:

            delivery_percentage = 55.0

        score = min(

            max(

                delivery_percentage,

                0,

            ),

            100,

        )

        if score >= 75:

            quality = "Excellent"

        elif score >= 60:

            quality = "Strong"

        elif score >= 45:

            quality = "Average"

        else:

            quality = "Weak"

        return {

            "delivery_percentage": round(

                delivery_percentage,

                2,

            ),

            "score": round(

                score,

                2,

            ),

            "quality": quality,

        }

    # ======================================================
    # DELIVERY BREAKOUT
    # ======================================================

    def delivery_breakout(

        self,

        delivery_percentage: Optional[float] = None,

    ) -> Dict:

        delivery = self.delivery_volume_score(

            delivery_percentage,

        )

        breakout = self.breakout_volume_confirmation()

        confirmed = (

            delivery["score"] >= 60

            and

            breakout["confirmed"]

        )

        score = (

            delivery["score"] * 0.40

            +

            breakout["score"] * 0.60

        )

        return {

            "confirmed": confirmed,

            "score": round(

                min(score, 100),

                2,

            ),

            "delivery_quality":

                delivery["quality"],

        }

    # ======================================================
    # ACCUMULATION PHASE
    # ======================================================

    def accumulation_phase(

        self,

    ) -> Dict:

        adl = self.accumulation_distribution()

        cmf = self.chaikin_money_flow()

        rvol = self.relative_volume()

        score = 0

        if adl > 0:

            score += 35

        if cmf > 0:

            score += 35

        if rvol > 1.20:

            score += 30

        score = min(

            score,

            100,

        )

        phase = (

            "Accumulation"

            if score >= 70

            else "Neutral"

        )

        return {

            "phase": phase,

            "score": score,

        }

    # ======================================================
    # DISTRIBUTION PHASE
    # ======================================================

    def distribution_phase(

        self,

    ) -> Dict:

        cmf = self.chaikin_money_flow()

        force = self.force_index()

        rvol = self.relative_volume()

        score = 0

        if cmf < 0:

            score += 40

        if force < 0:

            score += 35

        if rvol > 1.50:

            score += 25

        score = min(

            score,

            100,

        )

        phase = (

            "Distribution"

            if score >= 70

            else "Neutral"

        )

        return {

            "phase": phase,

            "score": score,

        }

    # ======================================================
    # VOLUME COMPRESSION (VCP)
    # ======================================================

    def volume_compression(

        self,

        period: int = 10,

    ) -> Dict:

        volume = self.data["Volume"].tail(period)

        cv = (

            volume.std()

            /

            volume.mean()

            if volume.mean() != 0

            else 0

        )

        score = max(

            0,

            100 - (cv * 100),

        )

        detected = (

            score >= 70

        )

        return {

            "detected": detected,

            "compression_score":

                round(

                    score,

                    2,

                ),

            "coefficient_variation":

                round(

                    cv,

                    4,

                ),

        }

    # ======================================================
    # EXPANSION PHASE
    # ======================================================

    def expansion_phase(

        self,

    ) -> Dict:

        spike = self.volume_spike()

        breakout = self.breakout_volume_confirmation()

        score = (

            spike["strength"] * 0.40

            +

            breakout["score"] * 0.60

        )

        phase = (

            "Expansion"

            if score >= 70

            else "Normal"

        )

        return {

            "phase": phase,

            "score": round(

                min(score, 100),

                2,

            ),

        }

    # ======================================================
    # INSTITUTIONAL ENTRY PROBABILITY
    # ======================================================

    def institutional_entry_probability(

        self,

    ) -> Dict:

        accumulation = self.accumulation_phase()

        smart_money = self.smart_money_score()

        breakout = self.breakout_quality_score()

        probability = (

            accumulation["score"] * 0.40

            +

            smart_money * 0.35

            +

            breakout * 0.25

        )

        probability = min(

            probability,

            100,

        )

        if probability >= 80:

            level = "Very High"

        elif probability >= 65:

            level = "High"

        elif probability >= 50:

            level = "Moderate"

        else:

            level = "Low"

        return {

            "probability": round(

                probability,

                2,

            ),

            "level": level,

        }

    # ======================================================
    # AI VOLUME OPPORTUNITY SCORE
    # ======================================================

    def volume_opportunity_score(

        self,

    ) -> float:

        institutional = (

            self.institutional_entry_probability()

        )

        compression = (

            self.volume_compression()

        )

        expansion = (

            self.expansion_phase()

        )

        score = (

            institutional["probability"] * 0.45

            +

            compression["compression_score"] * 0.20

            +

            expansion["score"] * 0.20

            +

            self.volume_quality_score() * 0.15

        )

        return round(

            min(

                score,

                100,

            ),

            2,

        )
        # ======================================================
    # VOLUME MOMENTUM SCORE
    # ======================================================

    def volume_momentum_score(

        self,

    ) -> float:

        rvol = self.relative_volume()

        change = abs(

            self.volume_change()

        )

        trend = self.volume_trend_strength()

        score = (

            min(

                rvol * 25,

                25,

            )

            +

            min(

                change,

                25,

            )

            +

            trend["score"] * 0.50

        )

        return round(

            min(

                score,

                100,

            ),

            2,

        )

    # ======================================================
    # INTRADAY VOLUME STRENGTH
    # ======================================================

    def intraday_volume_strength(

        self,

    ) -> Dict:

        rvol = self.relative_volume()

        quality = self.volume_quality_score()

        score = (

            rvol * 40

            +

            quality * 0.60

        )

        score = min(

            score,

            100,

        )

        return {

            "score": round(

                score,

                2,

            ),

            "strength":

                "Strong"

                if score >= 75

                else "Moderate"

                if score >= 50

                else "Weak",

        }

    # ======================================================
    # SWING VOLUME STRENGTH
    # ======================================================

    def swing_volume_strength(

        self,

    ) -> Dict:

        institution = self.institutional_score()

        accumulation = self.accumulation_phase()

        score = (

            institution["score"] * 0.55

            +

            accumulation["score"] * 0.45

        )

        return {

            "score": round(

                score,

                2,

            ),

            "strength":

                "Strong"

                if score >= 70

                else "Moderate"

                if score >= 50

                else "Weak",

        }

    # ======================================================
    # POSITIONAL VOLUME STRENGTH
    # ======================================================

    def positional_volume_strength(

        self,

    ) -> Dict:

        smart = self.smart_money_score()

        delivery = self.delivery_volume_score()

        score = (

            smart * 0.60

            +

            delivery["score"] * 0.40

        )

        return {

            "score": round(

                score,

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
    # BREAKOUT READINESS
    # ======================================================

    def breakout_readiness(

        self,

    ) -> Dict:

        breakout = self.breakout_quality_score()

        compression = self.volume_compression()

        readiness = (

            breakout * 0.70

            +

            compression["compression_score"] * 0.30

        )

        readiness = min(

            readiness,

            100,

        )

        return {

            "score": round(

                readiness,

                2,

            ),

            "ready":

                readiness >= 75,

        }

    # ======================================================
    # REVERSAL VOLUME DETECTION
    # ======================================================

    def reversal_volume(

        self,

    ) -> Dict:

        spike = self.volume_spike()

        exhaustion = self.exhaustion_risk()

        reversal = (

            spike["detected"]

            and

            exhaustion["score"] >= 60

        )

        score = (

            spike["strength"] * 0.50

            +

            exhaustion["score"] * 0.50

        )

        return {

            "detected": reversal,

            "score": round(

                min(score, 100),

                2,

            ),

        }

    # ======================================================
    # LIQUIDITY SCORE
    # ======================================================

    def liquidity_score(

        self,

    ) -> float:

        avg_volume = self.average_volume()

        close = self.data["Close"].iloc[-1]

        traded_value = (

            avg_volume

            *

            close

        )

        score = min(

            traded_value / 1_00_00_000,

            100,

        )

        return round(

            score,

            2,

        )

    # ======================================================
    # AI TRADING SIGNAL
    # ======================================================

    def trading_signal(

        self,

    ) -> Dict:

        opportunity = self.volume_opportunity_score()

        breakout = self.breakout_readiness()

        institutional = (

            self.institutional_entry_probability()

        )

        if (

            opportunity >= 85

            and

            breakout["ready"]

        ):

            signal = "Strong Buy"

        elif opportunity >= 70:

            signal = "Buy"

        elif opportunity >= 55:

            signal = "Watch"

        elif opportunity >= 40:

            signal = "Avoid"

        else:

            signal = "Strong Avoid"

        confidence = (

            opportunity * 0.70

            +

            institutional["probability"] * 0.30

        )

        return {

            "signal": signal,

            "confidence": round(

                min(

                    confidence,

                    100,

                ),

                2,

            ),

            "opportunity_score":

                round(

                    opportunity,

                    2,

                ),

        }
        # ======================================================
    # COMPOSITE VOLUME SCORE
    # ======================================================

    def composite_volume_score(

        self,

    ) -> float:

        quality = self.volume_quality_score()

        opportunity = self.volume_opportunity_score()

        smart_money = self.smart_money_score()

        liquidity = self.liquidity_score()

        momentum = self.volume_momentum_score()

        score = (

            quality * 0.25 +

            opportunity * 0.25 +

            smart_money * 0.20 +

            liquidity * 0.10 +

            momentum * 0.20

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

        trading = self.trading_signal()

        breakout = self.breakout_readiness()

        institutional = self.institutional_entry_probability()

        score = (

            trading["confidence"] * 0.40 +

            breakout["score"] * 0.30 +

            institutional["probability"] * 0.30

        )

        return round(

            min(score, 100),

            2,

        )

    # ======================================================
    # VOLUME RANK
    # ======================================================

    def volume_rank(

        self,

        all_scores: List[float],

    ) -> Dict:

        score = self.composite_volume_score()

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

        signal = self.trading_signal()

        return {

            "symbol":

                self.symbol,

            "priority_score":

                self.priority_score(),

            "volume_score":

                self.composite_volume_score(),

            "signal":

                signal["signal"],

            "confidence":

                signal["confidence"],

        }

    # ======================================================
    # DASHBOARD SUMMARY
    # ======================================================

    def dashboard_summary(

        self,

    ) -> Dict:

        signal = self.trading_signal()

        return {

            "Symbol":

                self.symbol,

            "Composite Score":

                self.composite_volume_score(),

            "Priority Score":

                self.priority_score(),

            "RVOL":

                self.relative_volume(),

            "Trend":

                self.volume_trend(),

            "Recommendation":

                signal["signal"],

            "Confidence":

                signal["confidence"],

        }

    # ======================================================
    # HEATMAP DATA
    # ======================================================

    def heatmap_data(

        self,

    ) -> Dict:

        score = self.composite_volume_score()

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

            "color":

                color,

            "trend":

                self.volume_trend(),

        }

    # ======================================================
    # VOLUME ALERT
    # ======================================================

    def generate_alert(

        self,

    ) -> Dict:

        breakout = self.breakout_readiness()

        signal = self.trading_signal()

        alert = False

        message = "No Alert"

        if (

            breakout["ready"]

            and

            signal["signal"]

            in [

                "Strong Buy",

                "Buy",

            ]

        ):

            alert = True

            message = (

                f"{self.symbol} "

                "showing institutional "

                "volume breakout."

            )

        return {

            "alert": alert,

            "message": message,

            "priority_score":

                self.priority_score(),

            "signal":

                signal["signal"],

        }

    # ======================================================
    # OPPORTUNITY RANK
    # ======================================================

    def opportunity_rank(

        self,

    ) -> Dict:

        signal = self.trading_signal()

        score = self.priority_score()

        if score >= 90:

            level = "★★★★★"

        elif score >= 80:

            level = "★★★★☆"

        elif score >= 70:

            level = "★★★☆☆"

        elif score >= 60:

            level = "★★☆☆☆"

        else:

            level = "★☆☆☆☆"

        return {

            "symbol":

                self.symbol,

            "priority_score":

                score,

            "rank":

                level,

            "recommendation":

                signal["signal"],

            "confidence":

                signal["confidence"],

        }
        # ======================================================
    # MASTER VOLUME ANALYSIS
    # ======================================================

    def analyze(

        self,

    ) -> VolumeResult:

        if not self.validate():

            raise ValueError(

                "Invalid volume data."

            )

        recommendation = (

            self.professional_recommendation()

        )

        institutional = (

            self.institutional_score()

        )

        accumulation = (

            self.accumulation_phase()

        )

        distribution = (

            self.distribution_phase()

        )

        self.result = VolumeResult(

            symbol=self.symbol,

            volume_score=self.composite_volume_score(),

            rvol=self.relative_volume(),

            delivery_score=self.delivery_volume_score()["score"],

            accumulation_score=accumulation["score"],

            distribution_score=distribution["score"],

            institutional_activity=institutional["activity"],

            recommendation=recommendation["recommendation"],

            confidence=recommendation["confidence"],

            metrics={

                "Composite Score":

                    self.composite_volume_score(),

                "Priority Score":

                    self.priority_score(),

                "Opportunity Score":

                    self.volume_opportunity_score(),

                "Momentum Score":

                    self.volume_momentum_score(),

                "Liquidity Score":

                    self.liquidity_score(),

                "Smart Money Score":

                    self.smart_money_score(),

                "Breakout Score":

                    self.breakout_quality_score(),

                "RVOL":

                    self.relative_volume(),

            },

        )

        return self.result

    # ======================================================
    # AI RECOMMENDATION
    # ======================================================

    def ai_recommendation(

        self,

    ) -> Dict:

        signal = self.trading_signal()

        alert = self.generate_alert()

        return {

            "symbol":

                self.symbol,

            "recommendation":

                signal["signal"],

            "confidence":

                signal["confidence"],

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

            "Volume Score":

                self.result.volume_score,

            "RVOL":

                self.result.rvol,

            "Institutional":

                self.result.institutional_activity,

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

            "volume_score":

                self.result.volume_score,

            "rvol":

                self.result.rvol,

            "delivery_score":

                self.result.delivery_score,

            "accumulation_score":

                self.result.accumulation_score,

            "distribution_score":

                self.result.distribution_score,

            "institutional_activity":

                self.result.institutional_activity,

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

        print("STOCKVERSITY AI VOLUME ANALYSIS REPORT")

        print("=" * 70)

        print(f"Symbol                : {self.result.symbol}")

        print(f"Composite Score       : {self.result.volume_score:.2f}")

        print(f"Relative Volume       : {self.result.rvol:.2f}")

        print(f"Delivery Score        : {self.result.delivery_score:.2f}")

        print(f"Accumulation Score    : {self.result.accumulation_score:.2f}")

        print(f"Distribution Score    : {self.result.distribution_score:.2f}")

        print(f"Institutional Activity: {self.result.institutional_activity}")

        print(f"Recommendation        : {self.result.recommendation}")

        print(f"Confidence            : {self.result.confidence:.2f}")

        print()

        print("METRICS")

        print("-" * 70)

        for key, value in self.result.metrics.items():

            print(f"{key:30} : {value}")

        print("=" * 70)
            # ======================================================
    # VOLUME RANKING ENGINE
    # ======================================================

    def ranking_summary(

        self,

        all_scores: List[float],

    ) -> Dict:

        rank = self.volume_rank(

            all_scores,

        )

        signal = self.trading_signal()

        return {

            "symbol":

                self.symbol,

            "rank":

                rank["rank"],

            "total":

                rank["total"],

            "percentile":

                rank["percentile"],

            "score":

                rank["score"],

            "signal":

                signal["signal"],

        }

    # ======================================================
    # SCANNER SUMMARY
    # ======================================================

    def scanner_summary(

        self,

    ) -> Dict:

        signal = self.trading_signal()

        recommendation = self.professional_recommendation()

        return {

            "Symbol":

                self.symbol,

            "Volume Score":

                self.composite_volume_score(),

            "Priority":

                self.priority_score(),

            "Opportunity":

                self.volume_opportunity_score(),

            "Recommendation":

                recommendation["recommendation"],

            "Signal":

                signal["signal"],

            "Confidence":

                signal["confidence"],

        }

    # ======================================================
    # HEATMAP EXPORT
    # ======================================================

    def export_heatmap(

        self,

    ) -> Dict:

        heat = self.heatmap_data()

        return {

            "symbol":

                heat["symbol"],

            "score":

                heat["score"],

            "color":

                heat["color"],

            "trend":

                heat["trend"],

            "rvol":

                self.relative_volume(),

        }

    # ======================================================
    # WATCHLIST EXPORT
    # ======================================================

    def export_watchlist(

        self,

    ) -> Dict:

        watch = self.watchlist_entry()

        event = self.volume_event()

        return {

            **watch,

            "event":

                event["event"],

            "rvol":

                self.relative_volume(),

            "trend":

                self.volume_trend(),

        }

    # ======================================================
    # OPPORTUNITY OUTPUT
    # ======================================================

    def opportunity_output(

        self,

    ) -> Dict:

        signal = self.trading_signal()

        return {

            "symbol":

                self.symbol,

            "priority_score":

                self.priority_score(),

            "volume_score":

                self.composite_volume_score(),

            "opportunity_score":

                self.volume_opportunity_score(),

            "recommendation":

                signal["signal"],

            "confidence":

                signal["confidence"],

        }

    # ======================================================
    # ALERT SUMMARY
    # ======================================================

    def alert_summary(

        self,

    ) -> Dict:

        alert = self.generate_alert()

        return {

            "symbol":

                self.symbol,

            "alert":

                alert["alert"],

            "message":

                alert["message"],

            "priority_score":

                alert["priority_score"],

            "signal":

                alert["signal"],

        }

    # ======================================================
    # DEBUG INFORMATION
    # ======================================================

    def debug(

        self,

    ) -> Dict:

        return {

            "symbol":

                self.symbol,

            "data_loaded":

                self.data is not None,

            "validated":

                self.validate(),

            "current_volume":

                self.current_volume()

                if self.validate()

                else None,

            "average_volume":

                self.average_volume()

                if self.validate()

                else None,

            "relative_volume":

                self.relative_volume()

                if self.validate()

                else None,

            "volume_score":

                self.composite_volume_score()

                if self.validate()

                else None,

            "priority_score":

                self.priority_score()

                if self.validate()

                else None,

        }

    # ======================================================
    # PRODUCTION RUNNER
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

            "alerts":

                self.alert_summary(),

        }
        # ======================================================
    # LOAD REPORT
    # ======================================================

    @staticmethod
    def load_report(

        filename: str,

    ) -> Dict:

        with open(

            filename,

            "r",

            encoding="utf-8",

        ) as file:

            return json.load(file)

    # ======================================================
    # RESULT OBJECT
    # ======================================================

    def get_result(

        self,

    ) -> Optional[VolumeResult]:

        return self.result

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

            "Volume Score":

                self.result.volume_score,

            "RVOL":

                self.result.rvol,

            "Recommendation":

                self.result.recommendation,

            "Confidence":

                self.result.confidence,

        }

    # ======================================================
    # VALIDATION REPORT
    # ======================================================

    def validation_report(

        self,

    ) -> Dict:

        report = {

            "Data Loaded":

                self.data is not None,

            "Validation":

                self.validate(),

            "Rows":

                len(self.data)

                if self.data is not None

                else 0,

        }

        report["Passed"] = all(

            [

                report["Data Loaded"],

                report["Validation"],

            ]

        )

        return report

    # ======================================================
    # CLEAR ENGINE
    # ======================================================

    def clear(

        self,

    ):

        self.data = None

        self.result = None

        self.symbol = ""

        return self

    # ======================================================
    # ENGINE INFORMATION
    # ======================================================

    @property
    def engine_name(

        self,

    ) -> str:

        return (

            "StockVersity AI Volume Analysis Engine"

        )

    @property
    def version(

        self,

    ) -> str:

        return "4.0"

    @property
    def build(

        self,

    ) -> Dict:

        return {

            "engine":

                self.engine_name,

            "version":

                self.version,

            "powered_by":

                "AI",

            "status":

                "Production",

        }

    # ======================================================
    # STRING REPRESENTATION
    # ======================================================

    def __repr__(

        self,

    ) -> str:

        score = (

            self.result.volume_score

            if self.result

            else 0.0

        )

        return (

            f"<VolumeAnalysisEngine "

            f"Symbol='{self.symbol}' "

            f"Score={score:.2f}>"

        )

    # ======================================================
    # LENGTH
    # ======================================================

    def __len__(

        self,

    ) -> int:

        if self.data is None:

            return 0

        return len(

            self.data,

        )

    # ======================================================
    # BOOLEAN SUPPORT
    # ======================================================

    def __bool__(

        self,

    ) -> bool:

        return self.validate()

    # ======================================================
    # EXPORT COMPLETE RESULT
    # ======================================================

    def export(

        self,

    ) -> Dict:

        if self.result is None:

            self.analyze()

        return {

            "dashboard":

                self.dashboard(),

            "summary":

                self.summary(),

            "scanner":

                self.scanner_summary(),

            "watchlist":

                self.export_watchlist(),

            "heatmap":

                self.export_heatmap(),

            "opportunity":

                self.opportunity_output(),

            "alerts":

                self.alert_summary(),

            "report":

                self.to_dict(),

        }

    # ======================================================
    # MODULE COMPLETE
    # ======================================================