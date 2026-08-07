"""
=========================================================
StockVersity Scanner Pro
Scoring Engine
Version : 2.0
=========================================================

Central scoring utilities for scanner signals.

Responsibilities
----------------
• Calculate institutional signal score
• Calculate confidence
• Score trend
• Score volume
• Score momentum
• Score pattern quality
• Score sector strength
• Score relative strength
• Score market alignment
• Calculate priority score
• Assign signal quality grade
=========================================================
"""

from __future__ import annotations

from typing import Any
from typing import Dict
from typing import Optional

from core.scanner.signal import Signal
from core.scanner.signal import SignalType
from core.scanner.signal import PatternType
from core.scanner.signal import MarketTrend


# =========================================================
# SCORE LIMITS
# =========================================================

MIN_SCORE = 0.0
MAX_SCORE = 100.0


# =========================================================
# DEFAULT SCORE WEIGHTS
# =========================================================

DEFAULT_WEIGHTS: Dict[str, float] = {

    "trend": 20.0,

    "volume": 15.0,

    "momentum": 15.0,

    "pattern": 20.0,

    "sector": 10.0,

    "relative_strength": 10.0,

    "market": 10.0,
}


# =========================================================
# HELPERS
# =========================================================

def clamp(
    value: float,
    minimum: float = MIN_SCORE,
    maximum: float = MAX_SCORE,
) -> float:
    """
    Keep a value inside a defined range.
    """

    return max(
        minimum,
        min(
            maximum,
            float(value),
        ),
    )


def safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    Convert a value to float safely.
    """

    try:

        if value is None:
            return default

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return default


# =========================================================
# SCORING ENGINE
# =========================================================

class ScoringEngine:
    """
    Central scoring engine used by StockVersity scanners.

    The engine calculates a 0-100 quality score using:

    • Trend
    • Volume
    • Momentum
    • Pattern
    • Sector
    • Relative strength
    • Market alignment
    """

    def __init__(
        self,
        weights: Optional[
            Dict[str, float]
        ] = None,
    ) -> None:

        self.weights = dict(
            DEFAULT_WEIGHTS
        )

        if weights:

            self.set_weights(
                weights
            )

    # =====================================================
    # SET WEIGHTS
    # =====================================================

    def set_weights(
        self,
        weights: Dict[str, float],
    ) -> None:
        """
        Update score category weights.

        Total weight should equal 100.
        """

        updated = dict(
            self.weights
        )

        for key, value in weights.items():

            if key not in updated:
                continue

            updated[key] = max(
                0.0,
                safe_float(value),
            )

        total = sum(
            updated.values()
        )

        if total <= 0:

            raise ValueError(
                "Scoring weights must be greater than zero."
            )

        # Normalize automatically to 100.

        self.weights = {

            key: (
                value
                / total
                * 100.0
            )

            for key, value
            in updated.items()

        }

    # =====================================================
    # TREND SCORE
    # =====================================================

    def trend_score(
        self,
        signal: Signal,
    ) -> float:
        """
        Score EMA structure and trend alignment.

        Returned value:
        0 - 100
        """

        score = 0.0

        price = (
            signal.last_price
            or signal.close_price
        )

        if price <= 0:
            return 0.0

        if signal.is_buy:

            if (
                signal.ema20 > 0
                and price > signal.ema20
            ):
                score += 20

            if (
                signal.ema21 > 0
                and price > signal.ema21
            ):
                score += 10

            if (
                signal.ema50 > 0
                and price > signal.ema50
            ):
                score += 20

            if (
                signal.ema200 > 0
                and price > signal.ema200
            ):
                score += 20

            if (
                signal.ema20 > 0
                and signal.ema50 > 0
                and signal.ema200 > 0
                and signal.ema20
                > signal.ema50
                > signal.ema200
            ):
                score += 30

        elif signal.is_sell:

            if (
                signal.ema20 > 0
                and price < signal.ema20
            ):
                score += 20

            if (
                signal.ema21 > 0
                and price < signal.ema21
            ):
                score += 10

            if (
                signal.ema50 > 0
                and price < signal.ema50
            ):
                score += 20

            if (
                signal.ema200 > 0
                and price < signal.ema200
            ):
                score += 20

            if (
                signal.ema20 > 0
                and signal.ema50 > 0
                and signal.ema200 > 0
                and signal.ema20
                < signal.ema50
                < signal.ema200
            ):
                score += 30

        else:

            score = 50.0

        return clamp(score)

    # =====================================================
    # VOLUME SCORE
    # =====================================================

    def volume_score(
        self,
        signal: Signal,
    ) -> float:
        """
        Score relative volume.

        RVOL >= 3.0 receives maximum score.
        """

        ratio = safe_float(
            signal.volume_ratio
        )

        if ratio <= 0:

            if (
                signal.average_volume > 0
                and signal.volume > 0
            ):

                ratio = (
                    signal.volume
                    / signal.average_volume
                )

        if ratio < 1.0:
            return 20.0

        if ratio < 1.25:
            return 40.0

        if ratio < 1.50:
            return 55.0

        if ratio < 2.0:
            return 70.0

        if ratio < 2.5:
            return 85.0

        if ratio < 3.0:
            return 95.0

        return 100.0

    # =====================================================
    # MOMENTUM SCORE
    # =====================================================

    def momentum_score(
        self,
        signal: Signal,
    ) -> float:
        """
        Score RSI, MACD and ADX momentum.
        """

        score = 0.0

        components = 0

        # -----------------------------
        # RSI
        # -----------------------------

        if signal.rsi > 0:

            components += 1

            if signal.is_buy:

                if 55 <= signal.rsi <= 70:
                    score += 100

                elif 50 <= signal.rsi < 55:
                    score += 75

                elif 70 < signal.rsi <= 80:
                    score += 70

                elif signal.rsi > 80:
                    score += 45

                else:
                    score += 30

            elif signal.is_sell:

                if 30 <= signal.rsi <= 45:
                    score += 100

                elif 45 < signal.rsi <= 50:
                    score += 75

                elif 20 <= signal.rsi < 30:
                    score += 70

                elif signal.rsi < 20:
                    score += 45

                else:
                    score += 30

            else:

                score += 50

        # -----------------------------
        # MACD
        # -----------------------------

        if (
            signal.macd != 0
            or signal.macd_signal != 0
            or signal.macd_histogram != 0
        ):

            components += 1

            if signal.is_buy:

                if (
                    signal.macd
                    > signal.macd_signal
                    and signal.macd_histogram > 0
                ):
                    score += 100

                elif (
                    signal.macd
                    > signal.macd_signal
                ):
                    score += 75

                else:
                    score += 30

            elif signal.is_sell:

                if (
                    signal.macd
                    < signal.macd_signal
                    and signal.macd_histogram < 0
                ):
                    score += 100

                elif (
                    signal.macd
                    < signal.macd_signal
                ):
                    score += 75

                else:
                    score += 30

            else:

                score += 50

        # -----------------------------
        # ADX
        # -----------------------------

        if signal.adx > 0:

            components += 1

            if signal.adx >= 35:
                score += 100

            elif signal.adx >= 25:
                score += 85

            elif signal.adx >= 20:
                score += 65

            elif signal.adx >= 15:
                score += 40

            else:
                score += 20

        if components == 0:
            return 0.0

        return clamp(
            score / components
        )

    # =====================================================
    # PATTERN SCORE
    # =====================================================

    def pattern_score(
        self,
        signal: Signal,
    ) -> float:
        """
        Score chart pattern quality.
        """

        scores = {

            PatternType.VCP:
                100.0,

            PatternType.CUP_HANDLE:
                95.0,

            PatternType.BULL_FLAG:
                92.0,

            PatternType.BEAR_FLAG:
                92.0,

            PatternType.FALLING_WEDGE:
                90.0,

            PatternType.RISING_WEDGE:
                90.0,

            PatternType.ASCENDING_TRIANGLE:
                90.0,

            PatternType.DESCENDING_TRIANGLE:
                90.0,

            PatternType.BREAKOUT:
                88.0,

            PatternType.BREAKDOWN:
                88.0,

            PatternType.RANGE_BREAKOUT:
                87.0,

            PatternType.DOUBLE_BOTTOM:
                85.0,

            PatternType.DOUBLE_TOP:
                85.0,

            PatternType.ORB:
                82.0,

            PatternType.OPENING_RANGE:
                82.0,

            PatternType.VWAP_RECLAIM:
                80.0,

            PatternType.EMA_CROSS:
                78.0,

            PatternType.MOMENTUM:
                75.0,

            PatternType.SYMMETRICAL_TRIANGLE:
                75.0,

            PatternType.MACD:
                70.0,

            PatternType.RSI:
                65.0,

            PatternType.CUSTOM:
                60.0,
        }

        return scores.get(
            signal.pattern,
            60.0,
        )

    # =====================================================
    # SECTOR SCORE
    # =====================================================

    def sector_score(
        self,
        signal: Signal,
    ) -> float:
        """
        Score sector strength.

        Supports either:
        0-100 values
        or
        -1 to +1 normalized values.
        """

        strength = safe_float(
            signal.sector_strength
        )

        if -1.0 <= strength <= 1.0:

            strength = (
                strength + 1.0
            ) * 50.0

        if signal.is_sell:

            strength = (
                100.0 - strength
            )

        return clamp(
            strength
        )

    # =====================================================
    # RELATIVE STRENGTH SCORE
    # =====================================================

    def relative_strength_score(
        self,
        signal: Signal,
    ) -> float:
        """
        Score stock relative strength.
        """

        rs = safe_float(
            signal.relative_strength
        )

        if -1.0 <= rs <= 1.0:

            rs = (
                rs + 1.0
            ) * 50.0

        if signal.is_sell:

            rs = (
                100.0 - rs
            )

        return clamp(
            rs
        )

    # =====================================================
    # MARKET ALIGNMENT SCORE
    # =====================================================

    def market_score(
        self,
        signal: Signal,
    ) -> float:
        """
        Score signal alignment with overall market trend.
        """

        trend = signal.market_trend

        if signal.is_buy:

            mapping = {

                MarketTrend.STRONG_BULLISH:
                    100.0,

                MarketTrend.BULLISH:
                    85.0,

                MarketTrend.SIDEWAYS:
                    55.0,

                MarketTrend.BEARISH:
                    25.0,

                MarketTrend.STRONG_BEARISH:
                    10.0,
            }

        elif signal.is_sell:

            mapping = {

                MarketTrend.STRONG_BEARISH:
                    100.0,

                MarketTrend.BEARISH:
                    85.0,

                MarketTrend.SIDEWAYS:
                    55.0,

                MarketTrend.BULLISH:
                    25.0,

                MarketTrend.STRONG_BULLISH:
                    10.0,
            }

        else:

            return 50.0

        return mapping.get(
            trend,
            50.0,
        )

    # =====================================================
    # SCORE BREAKDOWN
    # =====================================================

    def calculate_breakdown(
        self,
        signal: Signal,
    ) -> Dict[str, float]:
        """
        Calculate weighted contribution of each category.
        """

        raw_scores = {

            "trend":
                self.trend_score(
                    signal
                ),

            "volume":
                self.volume_score(
                    signal
                ),

            "momentum":
                self.momentum_score(
                    signal
                ),

            "pattern":
                self.pattern_score(
                    signal
                ),

            "sector":
                self.sector_score(
                    signal
                ),

            "relative_strength":
                self.relative_strength_score(
                    signal
                ),

            "market":
                self.market_score(
                    signal
                ),
        }

        breakdown: Dict[
            str,
            float
        ] = {}

        for key, raw_score in (
            raw_scores.items()
        ):

            weight = (
                self.weights.get(
                    key,
                    0.0,
                )
                / 100.0
            )

            breakdown[key] = round(
                raw_score * weight,
                2,
            )

        return breakdown

    # =====================================================
    # TOTAL SCORE
    # =====================================================

    def calculate(
        self,
        signal: Signal,
    ) -> float:
        """
        Calculate final signal score.
        """

        breakdown = (
            self.calculate_breakdown(
                signal
            )
        )

        total = sum(
            breakdown.values()
        )

        signal.score_breakdown = (
            breakdown
        )

        signal.score = round(
            clamp(total),
            2,
        )

        return signal.score

    # =====================================================
    # CONFIDENCE
    # =====================================================

    def calculate_confidence(
        self,
        signal: Signal,
    ) -> float:
        """
        Calculate confidence independently from
        the main score.
        """

        factors = []

        # Trend

        trend = self.trend_score(
            signal
        )

        if trend > 0:
            factors.append(trend)

        # Volume

        volume = self.volume_score(
            signal
        )

        if volume > 0:
            factors.append(volume)

        # Momentum

        momentum = (
            self.momentum_score(
                signal
            )
        )

        if momentum > 0:
            factors.append(momentum)

        # Pattern

        factors.append(
            self.pattern_score(
                signal
            )
        )

        # Risk reward

        rr = safe_float(
            signal.risk_reward
        )

        if rr >= 3.0:
            factors.append(100.0)

        elif rr >= 2.5:
            factors.append(90.0)

        elif rr >= 2.0:
            factors.append(80.0)

        elif rr >= 1.5:
            factors.append(60.0)

        elif rr > 0:
            factors.append(35.0)

        if not factors:

            confidence = 0.0

        else:

            confidence = (
                sum(factors)
                / len(factors)
            )

        signal.confidence = round(
            clamp(confidence),
            2,
        )

        return signal.confidence

    # =====================================================
    # PRIORITY SCORE
    # =====================================================

    def priority_score(
        self,
        signal: Signal,
    ) -> float:
        """
        Calculate dashboard priority.

        Uses:
        • Signal score
        • Confidence
        • Risk/reward
        • Relative volume
        """

        rr_score = min(
            max(
                signal.risk_reward,
                0.0,
            ),
            5.0,
        ) / 5.0 * 100.0

        volume_score = (
            self.volume_score(
                signal
            )
        )

        priority = (

            signal.score
            * 0.45

            +

            signal.confidence
            * 0.30

            +

            rr_score
            * 0.15

            +

            volume_score
            * 0.10
        )

        return round(
            clamp(priority),
            2,
        )

    # =====================================================
    # QUALITY GRADE
    # =====================================================

    def grade(
        self,
        signal: Signal,
    ) -> str:
        """
        Institutional quality grade.
        """

        score = signal.score

        confidence = signal.confidence

        rr = signal.risk_reward

        if (
            score >= 90
            and confidence >= 90
            and rr >= 3.0
        ):
            return "A+"

        if (
            score >= 85
            and confidence >= 80
            and rr >= 2.5
        ):
            return "A"

        if (
            score >= 75
            and confidence >= 70
            and rr >= 2.0
        ):
            return "B+"

        if (
            score >= 65
            and rr >= 2.0
        ):
            return "B"

        if score >= 60:
            return "C"

        return "D"

    # =====================================================
    # SCORE SIGNAL
    # =====================================================

    def score_signal(
        self,
        signal: Signal,
    ) -> Signal:
        """
        Complete scoring pipeline.

        Updates:
        • score
        • score_breakdown
        • confidence
        • grade metadata
        • priority metadata
        """

        self.calculate(
            signal
        )

        self.calculate_confidence(
            signal
        )

        signal.metadata[
            "grade"
        ] = self.grade(
            signal
        )

        signal.metadata[
            "priority_score"
        ] = self.priority_score(
            signal
        )

        return signal

    # =====================================================
    # SCORE MANY
    # =====================================================

    def score_many(
        self,
        signals: list[Signal],
    ) -> list[Signal]:
        """
        Score multiple signals.
        """

        for signal in signals:

            self.score_signal(
                signal
            )

        return signals


# =========================================================
# DEFAULT ENGINE
# =========================================================

scoring_engine = ScoringEngine()


# =========================================================
# CONVENIENCE FUNCTIONS
# =========================================================

def score_signal(
    signal: Signal,
) -> Signal:
    """
    Score one signal using the default engine.
    """

    return scoring_engine.score_signal(
        signal
    )


def calculate_score(
    signal: Signal,
) -> float:
    """
    Calculate total score.
    """

    return scoring_engine.calculate(
        signal
    )


def calculate_confidence(
    signal: Signal,
) -> float:
    """
    Calculate signal confidence.
    """

    return (
        scoring_engine
        .calculate_confidence(
            signal
        )
    )


def priority_score(
    signal: Signal,
) -> float:
    """
    Calculate signal priority.
    """

    return (
        scoring_engine
        .priority_score(
            signal
        )
    )


def quality_grade(
    signal: Signal,
) -> str:
    """
    Return signal quality grade.
    """

    return scoring_engine.grade(
        signal
    )


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "ScoringEngine",

    "scoring_engine",

    "score_signal",

    "calculate_score",

    "calculate_confidence",

    "priority_score",

    "quality_grade",

    "DEFAULT_WEIGHTS",

    "MIN_SCORE",

    "MAX_SCORE",
]


# ==========================
# END OF FILE
# ==========================