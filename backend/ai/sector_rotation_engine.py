"""
==========================================================
StockVersity Scanner Pro
Sector Rotation Engine
Version : 4.0
Powered by AI
==========================================================
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np
import pandas as pd


# ==========================================================
# RESULT OBJECT
# ==========================================================

@dataclass
class SectorResult:

    sector: str

    score: float

    rank: int

    relative_strength: float

    momentum: float

    trend: str

    money_flow: float

    institutional_activity: str

    recommendation: str

    confidence: float

    metrics: Dict = field(default_factory=dict)


# ==========================================================
# SECTOR ROTATION ENGINE
# ==========================================================

class SectorRotationEngine:

    """
    AI Sector Rotation Engine

    Detects:
        • Strongest sectors
        • Weakest sectors
        • Relative Strength
        • Institutional Rotation
        • Momentum Ranking
        • Sector Leadership
        • Swing Sector Selection
        • Intraday Sector Rotation
    """

    def __init__(self):

        self.data: Optional[pd.DataFrame] = None

        self.benchmark: Optional[pd.Series] = None

        self.result: Optional[SectorResult] = None

        self.sector_name = ""

        self.lookback = 20

        self.minimum_stocks = 5

    # ======================================================
    # LOAD DATA
    # ======================================================

    def load_sector(

        self,

        sector_name: str,

        sector_dataframe: pd.DataFrame,

        benchmark_close: pd.Series,

    ):

        self.sector_name = sector_name

        self.data = sector_dataframe.copy()

        self.benchmark = benchmark_close.copy()

        return self

    # ======================================================
    # VALIDATION
    # ======================================================

    def validate(self) -> bool:

        if self.data is None:

            return False

        if self.benchmark is None:

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

        if len(self.data) < self.lookback:

            return False

        return True

    # ======================================================
    # RESET
    # ======================================================

    def reset(self):

        self.result = None

        return self

    # ======================================================
    # BASIC RETURNS
    # ======================================================

    def sector_return(self) -> float:

        close = self.data["Close"]

        return float(

            (

                close.iloc[-1]

                -

                close.iloc[-self.lookback]

            )

            /

            close.iloc[-self.lookback]

            * 100

        )

    def benchmark_return(self) -> float:

        close = self.benchmark

        return float(

            (

                close.iloc[-1]

                -

                close.iloc[-self.lookback]

            )

            /

            close.iloc[-self.lookback]

            * 100

        )

    # ======================================================
    # RELATIVE STRENGTH
    # ======================================================

    def relative_strength(self) -> float:

        return round(

            self.sector_return()

            -

            self.benchmark_return(),

            2,

        )

    # ======================================================
    # PRICE MOMENTUM
    # ======================================================

    def momentum(self) -> float:

        close = self.data["Close"]

        roc = (

            close.pct_change(

                self.lookback

            )

            * 100

        )

        return round(

            roc.iloc[-1],

            2,

        )

    # ======================================================
    # SHORT / LONG EMA
    # ======================================================

    def ema_trend(self):

        close = self.data["Close"]

        ema20 = close.ewm(

            span=20,

            adjust=False,

        ).mean()

        ema50 = close.ewm(

            span=50,

            adjust=False,

        ).mean()

        if ema20.iloc[-1] > ema50.iloc[-1]:

            return "Bullish"

        elif ema20.iloc[-1] < ema50.iloc[-1]:

            return "Bearish"

        return "Neutral"

    # ======================================================
    # VOLUME RATIO
    # ======================================================

    def volume_ratio(self) -> float:

        volume = self.data["Volume"]

        current = volume.iloc[-1]

        average = volume.tail(20).mean()

        return round(

            current /

            average,

            2,

        )
        # ======================================================
    # MONEY FLOW INDEX (MFI)
    # ======================================================

    def money_flow_index(

        self,

        period: int = 14,

    ) -> float:

        high = self.data["High"]

        low = self.data["Low"]

        close = self.data["Close"]

        volume = self.data["Volume"]

        typical_price = (

            high +

            low +

            close

        ) / 3

        money_flow = typical_price * volume

        positive_flow = np.where(

            typical_price > typical_price.shift(1),

            money_flow,

            0,

        )

        negative_flow = np.where(

            typical_price < typical_price.shift(1),

            money_flow,

            0,

        )

        positive = pd.Series(

            positive_flow,

            index=self.data.index,

        ).rolling(period).sum()

        negative = pd.Series(

            negative_flow,

            index=self.data.index,

        ).rolling(period).sum()

        ratio = positive / negative.replace(0, np.nan)

        mfi = 100 - (

            100 /

            (1 + ratio)

        )

        return round(

            float(

                mfi.iloc[-1]

            ),

            2,

        )

    # ======================================================
    # RELATIVE VOLUME (RVOL)
    # ======================================================

    def relative_volume(

        self,

        period: int = 20,

    ) -> float:

        volume = self.data["Volume"]

        current = volume.iloc[-1]

        average = volume.tail(period).mean()

        if average == 0:

            return 0.0

        return round(

            current / average,

            2,

        )

    # ======================================================
    # ACCUMULATION / DISTRIBUTION LINE
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

        money_flow_volume = (

            multiplier *

            volume

        )

        adl = money_flow_volume.cumsum()

        return round(

            float(

                adl.iloc[-1]

            ),

            2,

        )

    # ======================================================
    # ON BALANCE VOLUME
    # ======================================================

    def obv(

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
    # OBV TREND
    # ======================================================

    def obv_trend(

        self,

    ) -> str:

        close = self.data["Close"]

        volume = self.data["Volume"]

        direction = np.sign(

            close.diff()

        ).fillna(0)

        obv = (

            direction *

            volume

        ).cumsum()

        ema20 = obv.ewm(

            span=20,

            adjust=False,

        ).mean()

        if obv.iloc[-1] > ema20.iloc[-1]:

            return "Bullish"

        elif obv.iloc[-1] < ema20.iloc[-1]:

            return "Bearish"

        return "Neutral"

    # ======================================================
    # INSTITUTIONAL ACTIVITY
    # ======================================================

    def institutional_activity(

        self,

    ) -> str:

        mfi = self.money_flow_index()

        rvol = self.relative_volume()

        trend = self.obv_trend()

        if (

            mfi >= 70

            and

            rvol >= 1.50

            and

            trend == "Bullish"

        ):

            return "Strong Institutional Buying"

        elif (

            mfi <= 30

            and

            rvol >= 1.50

            and

            trend == "Bearish"

        ):

            return "Strong Institutional Selling"

        elif trend == "Bullish":

            return "Accumulation"

        elif trend == "Bearish":

            return "Distribution"

        return "Neutral"

    # ======================================================
    # VOLUME PRESSURE SCORE
    # ======================================================

    def volume_pressure_score(

        self,

    ) -> float:

        score = 50.0

        rvol = self.relative_volume()

        mfi = self.money_flow_index()

        if rvol > 1:

            score += min(

                rvol * 10,

                20,

            )

        if mfi > 50:

            score += (

                mfi - 50

            ) * 0.60

        else:

            score -= (

                50 - mfi

            ) * 0.60

        return round(

            max(

                0,

                min(score, 100),

            ),

            2,

        )

    # ======================================================
    # SMART MONEY SCORE
    # ======================================================

    def smart_money_score(

        self,

    ) -> float:

        score = (

            self.relative_strength() * 0.35 +

            self.momentum() * 0.20 +

            self.volume_pressure_score() * 0.45

        )

        return round(

            max(

                0,

                min(score, 100),

            ),

            2,

        )

    # ======================================================
    # LIQUIDITY SCORE
    # ======================================================

    def liquidity_score(

        self,

    ) -> float:

        volume = self.data["Volume"]

        avg_volume = volume.tail(20).mean()

        score = (

            math.log10(

                max(

                    avg_volume,

                    1,

                )

            ) * 20

        )

        return round(

            min(

                score,

                100,

            ),

            2,

        )
        # ======================================================
    # RELATIVE STRENGTH RATING (RS RATING)
    # ======================================================

    def relative_strength_rating(

        self,

    ) -> float:

        rs = self.relative_strength()

        score = 50 + (rs * 3)

        return round(

            max(

                0,

                min(score, 100),

            ),

            2,

        )

    # ======================================================
    # TREND STRENGTH SCORE
    # ======================================================

    def trend_strength_score(

        self,

    ) -> float:

        close = self.data["Close"]

        ema20 = close.ewm(

            span=20,

            adjust=False,

        ).mean()

        ema50 = close.ewm(

            span=50,

            adjust=False,

        ).mean()

        ema200 = close.ewm(

            span=200,

            adjust=False,

        ).mean()

        score = 0

        if close.iloc[-1] > ema20.iloc[-1]:

            score += 25

        if ema20.iloc[-1] > ema50.iloc[-1]:

            score += 35

        if ema50.iloc[-1] > ema200.iloc[-1]:

            score += 40

        return round(

            score,

            2,

        )

    # ======================================================
    # MOMENTUM SCORE
    # ======================================================

    def momentum_score(

        self,

    ) -> float:

        momentum = self.momentum()

        score = 50 + (

            momentum * 2

        )

        return round(

            max(

                0,

                min(score, 100),

            ),

            2,

        )

    # ======================================================
    # LEADERSHIP SCORE
    # ======================================================

    def leadership_score(

        self,

    ) -> float:

        rs = self.relative_strength_rating()

        trend = self.trend_strength_score()

        smart = self.smart_money_score()

        score = (

            rs * 0.40 +

            trend * 0.35 +

            smart * 0.25

        )

        return round(

            min(score, 100),

            2,

        )

    # ======================================================
    # SECTOR ROTATION SCORE
    # ======================================================

    def sector_rotation_score(

        self,

    ) -> float:

        score = (

            self.relative_strength_rating() * 0.25 +

            self.momentum_score() * 0.25 +

            self.trend_strength_score() * 0.20 +

            self.smart_money_score() * 0.20 +

            self.volume_pressure_score() * 0.10

        )

        return round(

            min(score, 100),

            2,

        )

    # ======================================================
    # MARKET LEADERSHIP STATUS
    # ======================================================

    def leadership_status(

        self,

    ) -> str:

        score = self.leadership_score()

        if score >= 90:

            return "Market Leader"

        elif score >= 80:

            return "Leading"

        elif score >= 70:

            return "Strong"

        elif score >= 60:

            return "Improving"

        elif score >= 50:

            return "Neutral"

        return "Weak"

    # ======================================================
    # BULLISH / BEARISH CLASSIFICATION
    # ======================================================

    def sector_classification(

        self,

    ) -> str:

        score = self.sector_rotation_score()

        if score >= 90:

            return "Strong Bullish"

        elif score >= 75:

            return "Bullish"

        elif score >= 60:

            return "Moderately Bullish"

        elif score >= 45:

            return "Sideways"

        elif score >= 30:

            return "Bearish"

        return "Strong Bearish"

    # ======================================================
    # INSTITUTIONAL CONFIDENCE SCORE
    # ======================================================

    def institutional_confidence(

        self,

    ) -> float:

        score = (

            self.smart_money_score() * 0.40 +

            self.volume_pressure_score() * 0.30 +

            self.relative_strength_rating() * 0.30

        )

        return round(

            min(score, 100),

            2,

        )

    # ======================================================
    # AI SECTOR STRENGTH SCORE
    # ======================================================

    def ai_sector_strength(

        self,

    ) -> Dict:

        rs = self.relative_strength_rating()

        trend = self.trend_strength_score()

        momentum = self.momentum_score()

        leadership = self.leadership_score()

        rotation = self.sector_rotation_score()

        confidence = self.institutional_confidence()

        classification = self.sector_classification()

        return {

            "relative_strength": rs,

            "trend_strength": trend,

            "momentum_score": momentum,

            "leadership_score": leadership,

            "rotation_score": rotation,

            "institutional_confidence": confidence,

            "classification": classification,

            "leadership_status": self.leadership_status(),

        }
        # ======================================================
    # INTRADAY SECTOR STRENGTH
    # ======================================================

    def intraday_strength(

        self,

    ) -> Dict:

        close = self.data["Close"]

        open_ = self.data["Open"]

        change = (

            (close.iloc[-1] - open_.iloc[-1])

            /

            open_.iloc[-1]

        ) * 100

        score = 50 + (change * 10)

        score = max(

            0,

            min(score, 100),

        )

        return {

            "change_percent": round(

                change,

                2,

            ),

            "score": round(

                score,

                2,

            ),

        }

    # ======================================================
    # SWING STRENGTH
    # ======================================================

    def swing_strength(

        self,

    ) -> Dict:

        close = self.data["Close"]

        ema20 = close.ewm(

            span=20,

            adjust=False,

        ).mean()

        distance = (

            (

                close.iloc[-1]

                -

                ema20.iloc[-1]

            )

            /

            ema20.iloc[-1]

        ) * 100

        score = 50 + (distance * 5)

        score = max(

            0,

            min(score, 100),

        )

        return {

            "ema_distance": round(

                distance,

                2,

            ),

            "score": round(

                score,

                2,

            ),

        }

    # ======================================================
    # POSITIONAL STRENGTH
    # ======================================================

    def positional_strength(

        self,

    ) -> Dict:

        close = self.data["Close"]

        sma200 = close.rolling(

            200

        ).mean()

        if np.isnan(

            sma200.iloc[-1]

        ):

            return {

                "score": 50.0,

                "status": "Insufficient Data",

            }

        distance = (

            (

                close.iloc[-1]

                -

                sma200.iloc[-1]

            )

            /

            sma200.iloc[-1]

        ) * 100

        score = 50 + (distance * 3)

        score = max(

            0,

            min(score, 100),

        )

        return {

            "distance": round(

                distance,

                2,

            ),

            "score": round(

                score,

                2,

            ),

            "status": (

                "Bullish"

                if distance > 0

                else "Bearish"

            ),

        }

    # ======================================================
    # MULTI TIMEFRAME ALIGNMENT
    # ======================================================

    def timeframe_alignment(

        self,

    ) -> Dict:

        intraday = self.intraday_strength()

        swing = self.swing_strength()

        positional = self.positional_strength()

        aligned = (

            intraday["score"] > 60

            and

            swing["score"] > 60

            and

            positional["score"] > 60

        )

        return {

            "aligned": aligned,

            "intraday": intraday,

            "swing": swing,

            "positional": positional,

        }

    # ======================================================
    # TREND CONSISTENCY SCORE
    # ======================================================

    def trend_consistency_score(

        self,

    ) -> float:

        alignment = self.timeframe_alignment()

        scores = [

            alignment["intraday"]["score"],

            alignment["swing"]["score"],

            alignment["positional"]["score"],

        ]

        consistency = 100 - (

            np.std(scores) * 2

        )

        return round(

            max(

                0,

                min(consistency, 100),

            ),

            2,

        )

    # ======================================================
    # BREAKOUT READINESS
    # ======================================================

    def breakout_readiness(

        self,

    ) -> Dict:

        volume = self.relative_volume()

        rs = self.relative_strength_rating()

        trend = self.trend_strength_score()

        score = (

            volume * 20 +

            rs * 0.40 +

            trend * 0.40

        )

        score = min(

            score,

            100,

        )

        if score >= 80:

            status = "High"

        elif score >= 60:

            status = "Moderate"

        else:

            status = "Low"

        return {

            "score": round(

                score,

                2,

            ),

            "status": status,

        }

    # ======================================================
    # PULLBACK OPPORTUNITY
    # ======================================================

    def pullback_opportunity(

        self,

    ) -> Dict:

        close = self.data["Close"]

        ema20 = close.ewm(

            span=20,

            adjust=False,

        ).mean()

        distance = abs(

            (

                close.iloc[-1]

                -

                ema20.iloc[-1]

            )

            /

            ema20.iloc[-1]

        ) * 100

        if distance <= 2:

            quality = "Excellent"

        elif distance <= 5:

            quality = "Good"

        elif distance <= 8:

            quality = "Average"

        else:

            quality = "Poor"

        return {

            "distance": round(

                distance,

                2,

            ),

            "quality": quality,

        }

    # ======================================================
    # AI MULTI TIMEFRAME RATING
    # ======================================================

    def ai_multi_timeframe_rating(

        self,

    ) -> Dict:

        alignment = self.timeframe_alignment()

        consistency = self.trend_consistency_score()

        breakout = self.breakout_readiness()

        pullback = self.pullback_opportunity()

        overall = (

            alignment["intraday"]["score"] * 0.20 +

            alignment["swing"]["score"] * 0.35 +

            alignment["positional"]["score"] * 0.30 +

            consistency * 0.15

        )

        overall = min(

            overall,

            100,

        )

        return {

            "overall_score": round(

                overall,

                2,

            ),

            "trend_alignment": alignment,

            "consistency_score": consistency,

            "breakout_readiness": breakout,

            "pullback_opportunity": pullback,

        }
        # ======================================================
    # SECTOR LEADERSHIP RANKING
    # ======================================================

    def leadership_ranking(

        self,

    ) -> Dict:

        leadership = self.leadership_score()

        rotation = self.sector_rotation_score()

        confidence = self.institutional_confidence()

        overall = (

            leadership * 0.45 +

            rotation * 0.35 +

            confidence * 0.20

        )

        if overall >= 90:

            rank = 1

            label = "Elite Leader"

        elif overall >= 80:

            rank = 2

            label = "Strong Leader"

        elif overall >= 70:

            rank = 3

            label = "Leader"

        elif overall >= 60:

            rank = 4

            label = "Emerging"

        else:

            rank = 5

            label = "Weak"

        return {

            "score": round(

                overall,

                2,

            ),

            "rank": rank,

            "label": label,

        }

    # ======================================================
    # SECTOR ROTATION PHASE
    # ======================================================

    def rotation_phase(

        self,

    ) -> str:

        rs = self.relative_strength()

        momentum = self.momentum()

        smart = self.smart_money_score()

        if rs > 5 and momentum > 5 and smart > 70:

            return "Leading"

        elif rs > 2 and momentum > 0:

            return "Advancing"

        elif rs < -2 and momentum < 0:

            return "Lagging"

        elif rs < -5 and momentum < -5:

            return "Weakening"

        return "Transition"

    # ======================================================
    # EARLY ROTATION DETECTION
    # ======================================================

    def early_rotation_signal(

        self,

    ) -> Dict:

        rs = self.relative_strength()

        mfi = self.money_flow_index()

        volume = self.relative_volume()

        signal = False

        probability = 25.0

        if (

            rs > 0

            and

            mfi > 60

            and

            volume > 1.20

        ):

            signal = True

            probability = 80.0

        elif (

            rs > 0

            and

            volume > 1.00

        ):

            probability = 60.0

        return {

            "signal": signal,

            "probability": round(

                probability,

                2,

            ),

        }

    # ======================================================
    # STRONG TO WEAK FLOW
    # ======================================================

    def strong_to_weak_flow(

        self,

    ) -> Dict:

        momentum = self.momentum()

        volume = self.relative_volume()

        smart = self.smart_money_score()

        weakening = (

            momentum < 0

            and

            smart < 50

            and

            volume > 1

        )

        return {

            "detected": weakening,

            "score": round(

                max(

                    0,

                    100 - smart,

                ),

                2,

            ),

        }

    # ======================================================
    # WEAK TO STRONG RECOVERY
    # ======================================================

    def weak_to_strong_recovery(

        self,

    ) -> Dict:

        rs = self.relative_strength()

        smart = self.smart_money_score()

        volume = self.relative_volume()

        recovery = (

            rs > 2

            and

            smart > 60

            and

            volume > 1.20

        )

        strength = (

            rs * 8 +

            smart * 0.60

        )

        return {

            "detected": recovery,

            "strength": round(

                min(

                    strength,

                    100,

                ),

                2,

            ),

        }

    # ======================================================
    # SECTOR MOMENTUM RANK
    # ======================================================

    def momentum_rank(

        self,

    ) -> Dict:

        score = (

            self.momentum_score() * 0.50 +

            self.relative_strength_rating() * 0.30 +

            self.volume_pressure_score() * 0.20

        )

        percentile = min(

            score,

            100,

        )

        return {

            "score": round(

                score,

                2,

            ),

            "percentile": round(

                percentile,

                2,

            ),

        }

    # ======================================================
    # ROTATION PROBABILITY
    # ======================================================

    def rotation_probability(

        self,

    ) -> float:

        probability = (

            self.relative_strength_rating() * 0.25 +

            self.smart_money_score() * 0.35 +

            self.momentum_score() * 0.25 +

            self.volume_pressure_score() * 0.15

        )

        return round(

            min(

                probability,

                100,

            ),

            2,

        )

    # ======================================================
    # INSTITUTIONAL ROTATION SCORE
    # ======================================================

    def institutional_rotation_score(

        self,

    ) -> Dict:

        leadership = self.leadership_ranking()

        probability = self.rotation_probability()

        early = self.early_rotation_signal()

        score = (

            leadership["score"] * 0.40 +

            probability * 0.40 +

            early["probability"] * 0.20

        )

        if score >= 85:

            recommendation = "Strong Buy Sector"

        elif score >= 70:

            recommendation = "Watch Closely"

        elif score >= 55:

            recommendation = "Neutral"

        else:

            recommendation = "Avoid"

        return {

            "rotation_score": round(

                score,

                2,

            ),

            "rotation_phase": self.rotation_phase(),

            "rotation_probability": probability,

            "leadership": leadership,

            "early_rotation": early,

            "recommendation": recommendation,

        }
        # ======================================================
    # STRONGEST SECTOR DETECTION
    # ======================================================

    def strongest_sector(

        self,

    ) -> Dict:

        rotation = self.sector_rotation_score()

        leadership = self.leadership_score()

        confidence = self.institutional_confidence()

        score = (

            rotation * 0.45 +

            leadership * 0.35 +

            confidence * 0.20

        )

        return {

            "sector": self.sector_name,

            "score": round(score, 2),

            "status": (

                "Strong"

                if score >= 75

                else "Average"

            ),

        }

    # ======================================================
    # WEAKEST SECTOR DETECTION
    # ======================================================

    def weakest_sector(

        self,

    ) -> Dict:

        score = 100 - self.sector_rotation_score()

        return {

            "sector": self.sector_name,

            "weakness_score": round(

                score,

                2,

            ),

            "status": (

                "Weak"

                if score >= 60

                else "Neutral"

            ),

        }

    # ======================================================
    # TOP ROTATION CANDIDATE
    # ======================================================

    def top_rotation_candidate(

        self,

    ) -> Dict:

        probability = self.rotation_probability()

        confidence = self.institutional_confidence()

        score = (

            probability * 0.60 +

            confidence * 0.40

        )

        return {

            "sector": self.sector_name,

            "rotation_score": round(

                score,

                2,

            ),

            "candidate": score >= 75,

        }

    # ======================================================
    # WATCHLIST SCORE
    # ======================================================

    def watchlist_score(

        self,

    ) -> float:

        score = (

            self.relative_strength_rating() * 0.20 +

            self.momentum_score() * 0.20 +

            self.trend_strength_score() * 0.20 +

            self.smart_money_score() * 0.20 +

            self.institutional_confidence() * 0.20

        )

        return round(

            min(score, 100),

            2,

        )

    # ======================================================
    # HEAT MAP SCORE
    # ======================================================

    def heatmap_score(

        self,

    ) -> Dict:

        score = self.watchlist_score()

        if score >= 85:

            color = "Dark Green"

        elif score >= 70:

            color = "Green"

        elif score >= 55:

            color = "Yellow"

        elif score >= 40:

            color = "Orange"

        else:

            color = "Red"

        return {

            "score": score,

            "heat_color": color,

        }

    # ======================================================
    # BULLISH / BEARISH FILTER
    # ======================================================

    def sector_filter(

        self,

    ) -> Dict:

        classification = self.sector_classification()

        bullish = classification in [

            "Strong Bullish",

            "Bullish",

            "Moderately Bullish",

        ]

        return {

            "classification":

                classification,

            "bullish":

                bullish,

            "bearish":

                not bullish,

        }

    # ======================================================
    # INTRADAY SCANNER
    # ======================================================

    def intraday_sector_scan(

        self,

    ) -> Dict:

        intraday = self.intraday_strength()

        breakout = self.breakout_readiness()

        confidence = self.institutional_confidence()

        qualified = (

            intraday["score"] >= 70

            and

            breakout["score"] >= 70

            and

            confidence >= 70

        )

        return {

            "qualified": qualified,

            "intraday_score":

                intraday["score"],

            "breakout":

                breakout,

            "confidence":

                confidence,

        }

    # ======================================================
    # SWING SCANNER
    # ======================================================

    def swing_sector_scan(

        self,

    ) -> Dict:

        swing = self.swing_strength()

        trend = self.trend_strength_score()

        rs = self.relative_strength_rating()

        qualified = (

            swing["score"] >= 70

            and

            trend >= 70

            and

            rs >= 70

        )

        overall = (

            swing["score"] * 0.40 +

            trend * 0.35 +

            rs * 0.25

        )

        return {

            "qualified":

                qualified,

            "overall_score":

                round(

                    overall,

                    2,

                ),

            "swing_score":

                swing["score"],

            "trend_score":

                trend,

            "relative_strength":

                rs,

        }
        # ======================================================
    # SECTOR RISK SCORE
    # ======================================================

    def sector_risk_score(

        self,

    ) -> float:

        volatility = self.data["Close"].pct_change().std() * 100

        rs = self.relative_strength_rating()

        trend = self.trend_strength_score()

        risk = (

            volatility * 2.5 +

            (100 - rs) * 0.35 +

            (100 - trend) * 0.40

        )

        risk = max(

            0,

            min(risk, 100),

        )

        return round(

            risk,

            2,

        )

    # ======================================================
    # VOLATILITY ANALYSIS
    # ======================================================

    def volatility_analysis(

        self,

        period: int = 20,

    ) -> Dict:

        returns = self.data["Close"].pct_change()

        volatility = (

            returns.tail(period).std()

            *

            np.sqrt(252)

            *

            100

        )

        if volatility < 15:

            level = "Low"

        elif volatility < 25:

            level = "Moderate"

        elif volatility < 35:

            level = "High"

        else:

            level = "Extreme"

        return {

            "annualized_volatility": round(

                volatility,

                2,

            ),

            "level": level,

        }

    # ======================================================
    # BETA ANALYSIS
    # ======================================================

    def beta_analysis(

        self,

    ) -> Dict:

        sector_returns = self.data["Close"].pct_change().dropna()

        benchmark_returns = self.benchmark.pct_change().dropna()

        length = min(

            len(sector_returns),

            len(benchmark_returns),

        )

        sector_returns = sector_returns.tail(length)

        benchmark_returns = benchmark_returns.tail(length)

        variance = np.var(

            benchmark_returns,

        )

        if variance == 0:

            beta = 1.0

        else:

            covariance = np.cov(

                sector_returns,

                benchmark_returns,

            )[0][1]

            beta = covariance / variance

        if beta > 1.20:

            category = "High Beta"

        elif beta < 0.80:

            category = "Defensive"

        else:

            category = "Market Beta"

        return {

            "beta": round(

                beta,

                2,

            ),

            "category": category,

        }

    # ======================================================
    # RELATIVE PERFORMANCE
    # ======================================================

    def relative_performance(

        self,

    ) -> Dict:

        sector = self.sector_return()

        benchmark = self.benchmark_return()

        outperformance = (

            sector -

            benchmark

        )

        return {

            "sector_return": round(

                sector,

                2,

            ),

            "benchmark_return": round(

                benchmark,

                2,

            ),

            "outperformance": round(

                outperformance,

                2,

            ),

        }

    # ======================================================
    # SECTOR STABILITY SCORE
    # ======================================================

    def stability_score(

        self,

    ) -> float:

        returns = self.data["Close"].pct_change().dropna()

        consistency = 100 - (

            returns.std() * 1000

        )

        return round(

            max(

                0,

                min(consistency, 100),

            ),

            2,

        )

    # ======================================================
    # INSTITUTIONAL FLOW RATING
    # ======================================================

    def institutional_flow_rating(

        self,

    ) -> Dict:

        smart = self.smart_money_score()

        confidence = self.institutional_confidence()

        mfi = self.money_flow_index()

        score = (

            smart * 0.40 +

            confidence * 0.35 +

            mfi * 0.25

        )

        if score >= 80:

            rating = "Strong Inflow"

        elif score >= 65:

            rating = "Moderate Inflow"

        elif score >= 50:

            rating = "Neutral"

        elif score >= 35:

            rating = "Moderate Outflow"

        else:

            rating = "Strong Outflow"

        return {

            "score": round(

                score,

                2,

            ),

            "rating": rating,

        }

    # ======================================================
    # AI SECTOR CONFIDENCE
    # ======================================================

    def sector_confidence(

        self,

    ) -> float:

        confidence = (

            self.relative_strength_rating() * 0.25 +

            self.trend_strength_score() * 0.25 +

            self.smart_money_score() * 0.20 +

            self.stability_score() * 0.15 +

            self.institutional_confidence() * 0.15

        )

        return round(

            min(

                confidence,

                100,

            ),

            2,

        )

    # ======================================================
    # PROFESSIONAL SECTOR RECOMMENDATION
    # ======================================================

    def professional_recommendation(

        self,

    ) -> Dict:

        confidence = self.sector_confidence()

        risk = self.sector_risk_score()

        rotation = self.rotation_probability()

        recommendation = "Avoid"

        if (

            confidence >= 85

            and

            risk < 30

        ):

            recommendation = "Strong Buy"

        elif (

            confidence >= 75

            and

            risk < 45

        ):

            recommendation = "Buy"

        elif (

            confidence >= 65

        ):

            recommendation = "Watch"

        return {

            "recommendation":

                recommendation,

            "confidence":

                confidence,

            "risk_score":

                risk,

            "rotation_probability":

                rotation,

            "institutional_flow":

                self.institutional_flow_rating(),

        }
        # ======================================================
    # SECTOR COMPOSITE SCORE
    # ======================================================

    def composite_score(

        self,

    ) -> float:

        score = (

            self.relative_strength_rating() * 0.20 +

            self.trend_strength_score() * 0.20 +

            self.momentum_score() * 0.15 +

            self.smart_money_score() * 0.15 +

            self.sector_confidence() * 0.15 +

            self.rotation_probability() * 0.15

        )

        return round(

            min(

                score,

                100,

            ),

            2,

        )

    # ======================================================
    # SECTOR RANK
    # ======================================================

    def sector_rank(

        self,

        all_scores: List[float],

    ) -> Dict:

        score = self.composite_score()

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

            "total_sectors": len(

                ranking,

            ),

            "percentile": round(

                percentile,

                2,

            ),

            "score": score,

        }

    # ======================================================
    # AI PRIORITY SCORE
    # ======================================================

    def priority_score(

        self,

    ) -> float:

        score = (

            self.composite_score() * 0.45 +

            self.breakout_readiness()["score"] * 0.20 +

            self.rotation_probability() * 0.20 +

            self.institutional_confidence() * 0.15

        )

        return round(

            min(

                score,

                100,

            ),

            2,

        )

    # ======================================================
    # DASHBOARD SUMMARY
    # ======================================================

    def dashboard_summary(

        self,

    ) -> Dict:

        return {

            "Sector":

                self.sector_name,

            "Composite Score":

                self.composite_score(),

            "Priority Score":

                self.priority_score(),

            "Classification":

                self.sector_classification(),

            "Trend":

                self.ema_trend(),

            "Rotation Phase":

                self.rotation_phase(),

            "Confidence":

                self.sector_confidence(),

            "Recommendation":

                self.professional_recommendation()[

                    "recommendation"

                ],

        }

    # ======================================================
    # HEATMAP DATA
    # ======================================================

    def heatmap_data(

        self,

    ) -> Dict:

        heat = self.heatmap_score()

        return {

            "sector":

                self.sector_name,

            "score":

                heat["score"],

            "color":

                heat["heat_color"],

            "trend":

                self.ema_trend(),

            "classification":

                self.sector_classification(),

        }

    # ======================================================
    # WATCHLIST OUTPUT
    # ======================================================

    def watchlist_entry(

        self,

    ) -> Dict:

        return {

            "sector":

                self.sector_name,

            "watchlist_score":

                self.watchlist_score(),

            "priority":

                self.priority_score(),

            "rotation_probability":

                self.rotation_probability(),

            "recommendation":

                self.professional_recommendation()[

                    "recommendation"

                ],

        }

    # ======================================================
    # TOP OPPORTUNITY
    # ======================================================

    def top_opportunity(

        self,

    ) -> Dict:

        recommendation = (

            self.professional_recommendation()

        )

        return {

            "sector":

                self.sector_name,

            "priority_score":

                self.priority_score(),

            "confidence":

                self.sector_confidence(),

            "rotation_probability":

                self.rotation_probability(),

            "recommendation":

                recommendation["recommendation"],

        }

    # ======================================================
    # ALERT GENERATOR
    # ======================================================

    def generate_alert(

        self,

    ) -> Dict:

        recommendation = (

            self.professional_recommendation()

        )

        breakout = (

            self.breakout_readiness()

        )

        alert = False

        message = "No Action"

        if (

            recommendation["recommendation"]

            in [

                "Strong Buy",

                "Buy",

            ]

            and

            breakout["score"] >= 75

        ):

            alert = True

            message = (

                f"{self.sector_name} "

                "showing strong "

                "institutional rotation."

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
    # MASTER SECTOR ANALYSIS
    # ======================================================

    def analyze(

        self,

    ) -> SectorResult:

        if not self.validate():

            raise ValueError(

                "Invalid sector data."

            )

        strength = self.ai_sector_strength()

        recommendation = self.professional_recommendation()

        self.result = SectorResult(

            sector=self.sector_name,

            score=self.composite_score(),

            rank=0,

            relative_strength=self.relative_strength(),

            momentum=self.momentum(),

            trend=self.ema_trend(),

            money_flow=self.money_flow_index(),

            institutional_activity=self.institutional_activity(),

            recommendation=recommendation[

                "recommendation"

            ],

            confidence=self.sector_confidence(),

            metrics={

                "Composite Score":

                    self.composite_score(),

                "Priority Score":

                    self.priority_score(),

                "Leadership":

                    self.leadership_score(),

                "Rotation Score":

                    self.sector_rotation_score(),

                "Risk Score":

                    self.sector_risk_score(),

                "Trend Strength":

                    strength["trend_strength"],

                "Momentum Score":

                    strength["momentum_score"],

                "Institutional Confidence":

                    strength[

                        "institutional_confidence"

                    ],

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

            "sector":

                self.sector_name,

            "recommendation":

                recommendation["recommendation"],

            "confidence":

                recommendation["confidence"],

            "priority_score":

                self.priority_score(),

            "rotation_probability":

                self.rotation_probability(),

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

            "Sector":

                self.result.sector,

            "Composite Score":

                self.result.score,

            "Relative Strength":

                self.result.relative_strength,

            "Momentum":

                self.result.momentum,

            "Trend":

                self.result.trend,

            "Confidence":

                self.result.confidence,

            "Recommendation":

                self.result.recommendation,

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

            "sector":

                self.result.sector,

            "score":

                self.result.score,

            "rank":

                self.result.rank,

            "relative_strength":

                self.result.relative_strength,

            "momentum":

                self.result.momentum,

            "trend":

                self.result.trend,

            "money_flow":

                self.result.money_flow,

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

        print("STOCKVERSITY AI SECTOR ROTATION REPORT")

        print("=" * 70)

        print(f"Sector               : {self.result.sector}")

        print(f"Composite Score      : {self.result.score:.2f}")

        print(f"Relative Strength    : {self.result.relative_strength:.2f}")

        print(f"Momentum             : {self.result.momentum:.2f}")

        print(f"Trend                : {self.result.trend}")

        print(f"Money Flow Index     : {self.result.money_flow:.2f}")

        print(f"Institutional Flow   : {self.result.institutional_activity}")

        print(f"Confidence           : {self.result.confidence:.2f}")

        print(f"Recommendation       : {self.result.recommendation}")

        print()

        print("METRICS")

        print("-" * 70)

        for key, value in self.result.metrics.items():

            print(f"{key:30} : {value}")

        print("=" * 70)
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

    ) -> Optional[SectorResult]:

        return self.result

    # ======================================================
    # DEBUG INFORMATION
    # ======================================================

    def debug(

        self,

    ) -> Dict:

        return {

            "sector":

                self.sector_name,

            "data_loaded":

                self.data is not None,

            "benchmark_loaded":

                self.benchmark is not None,

            "validated":

                self.validate(),

            "relative_strength":

                self.relative_strength()

                if self.validate()

                else None,

            "momentum":

                self.momentum()

                if self.validate()

                else None,

            "trend":

                self.ema_trend()

                if self.validate()

                else None,

            "rotation_score":

                self.sector_rotation_score()

                if self.validate()

                else None,

            "confidence":

                self.sector_confidence()

                if self.validate()

                else None,

        }

    # ======================================================
    # QUICK SUMMARY
    # ======================================================

    def summary(

        self,

    ) -> Dict:

        if self.result is None:

            self.analyze()

        return {

            "Sector":

                self.result.sector,

            "Score":

                self.result.score,

            "Trend":

                self.result.trend,

            "Recommendation":

                self.result.recommendation,

            "Confidence":

                self.result.confidence,

        }

    # ======================================================
    # VALIDATION SUMMARY
    # ======================================================

    def validation_report(

        self,

    ) -> Dict:

        checks = {

            "Sector Data":

                self.data is not None,

            "Benchmark":

                self.benchmark is not None,

            "Validation":

                self.validate(),

        }

        checks["Passed"] = all(

            checks.values()

        )

        return checks

    # ======================================================
    # RESET ENGINE
    # ======================================================

    def clear(

        self,

    ):

        self.data = None

        self.benchmark = None

        self.result = None

        self.sector_name = ""

        return self

    # ======================================================
    # PRODUCTION RUNNER
    # ======================================================

    def run(

        self,

    ) -> Dict:

        self.analyze()

        return self.to_dict()

    # ======================================================
    # STRING REPRESENTATION
    # ======================================================

    def __repr__(

        self,

    ) -> str:

        score = (

            self.result.score

            if self.result

            else 0.0

        )

        return (

            f"<SectorRotationEngine "

            f"Sector='{self.sector_name}' "

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

        return len(self.data)

    # ======================================================
    # BOOLEAN SUPPORT
    # ======================================================

    def __bool__(

        self,

    ) -> bool:

        return self.validate()

    # ======================================================
    # VERSION
    # ======================================================

    @property
    def version(

        self,

    ) -> str:

        return "4.0"

    # ======================================================
    # ENGINE NAME
    # ======================================================

    @property
    def engine_name(

        self,

    ) -> str:

        return "StockVersity AI Sector Rotation Engine"

    # ======================================================
    # BUILD INFORMATION
    # ======================================================

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
    # MODULE COMPLETE
    # ======================================================