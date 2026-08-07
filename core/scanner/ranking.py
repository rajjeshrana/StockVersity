"""
=========================================================
StockVersity Scanner Pro
Signal Ranking System
Version : 2.0
=========================================================

Central ranking utilities for scanner signals.

Responsibilities
----------------
• Calculate priority score
• Calculate quality grade
• Rank scanner opportunities
• Rank BUY / SELL signals
• Rank sectors
• Build leaderboard rows
• Apply ranking metadata

This module DOES NOT execute scanners.
=========================================================
"""

from __future__ import annotations

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from core.scanner.signal import Signal
from core.scanner.signal import SignalType


# =========================================================
# DEFAULT RANKING WEIGHTS
# =========================================================

DEFAULT_SCORE_WEIGHT = 0.45

DEFAULT_CONFIDENCE_WEIGHT = 0.25

DEFAULT_RR_WEIGHT = 0.15

DEFAULT_VOLUME_WEIGHT = 0.10

DEFAULT_RELATIVE_STRENGTH_WEIGHT = 0.05


# =========================================================
# LIMITS
# =========================================================

MAX_RISK_REWARD_SCORE = 5.0

MAX_VOLUME_RATIO_SCORE = 5.0


# =========================================================
# SAFE NUMBER
# =========================================================

def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    Safely convert a value to float.
    """

    try:

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return default


# =========================================================
# CLAMP
# =========================================================

def clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 100.0,
) -> float:
    """
    Restrict value to a range.
    """

    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


# =========================================================
# NORMALIZE RISK REWARD
# =========================================================

def normalize_risk_reward(
    risk_reward: float,
) -> float:
    """
    Convert risk/reward to a 0-100 ranking component.

    RR 5.0 or higher = 100.
    """

    rr = max(
        _safe_float(
            risk_reward
        ),
        0.0,
    )

    rr = min(
        rr,
        MAX_RISK_REWARD_SCORE,
    )

    return round(
        (
            rr
            / MAX_RISK_REWARD_SCORE
        )
        * 100,
        2,
    )


# =========================================================
# NORMALIZE VOLUME
# =========================================================

def normalize_volume_ratio(
    volume_ratio: float,
) -> float:
    """
    Convert relative volume to 0-100.

    RVOL 5.0 or higher = 100.
    """

    ratio = max(
        _safe_float(
            volume_ratio
        ),
        0.0,
    )

    ratio = min(
        ratio,
        MAX_VOLUME_RATIO_SCORE,
    )

    return round(
        (
            ratio
            / MAX_VOLUME_RATIO_SCORE
        )
        * 100,
        2,
    )


# =========================================================
# NORMALIZE RELATIVE STRENGTH
# =========================================================

def normalize_relative_strength(
    relative_strength: float,
) -> float:
    """
    Normalize relative strength to 0-100.

    The Signal model does not enforce one fixed RS scale,
    therefore values already between 0 and 100 are used
    directly.
    """

    value = _safe_float(
        relative_strength
    )

    return round(
        clamp(value),
        2,
    )


# =========================================================
# PRIORITY SCORE
# =========================================================

def calculate_priority_score(
    signal: Signal,
    *,
    score_weight: float = DEFAULT_SCORE_WEIGHT,
    confidence_weight: float = DEFAULT_CONFIDENCE_WEIGHT,
    rr_weight: float = DEFAULT_RR_WEIGHT,
    volume_weight: float = DEFAULT_VOLUME_WEIGHT,
    relative_strength_weight: float = (
        DEFAULT_RELATIVE_STRENGTH_WEIGHT
    ),
) -> float:
    """
    Calculate unified opportunity priority score.

    Final score range:
        0 - 100
    """

    total_weight = (

        score_weight
        + confidence_weight
        + rr_weight
        + volume_weight
        + relative_strength_weight

    )

    if abs(
        total_weight - 1.0
    ) > 0.001:

        raise ValueError(
            "Ranking weights must total 1.0"
        )

    base_score = clamp(
        _safe_float(
            signal.score
        )
    )

    confidence = clamp(
        _safe_float(
            signal.confidence
        )
    )

    rr_score = normalize_risk_reward(
        signal.risk_reward
    )

    volume_score = normalize_volume_ratio(
        signal.volume_ratio
    )

    relative_strength_score = (
        normalize_relative_strength(
            signal.relative_strength
        )
    )

    priority = (

        base_score
        * score_weight

        + confidence
        * confidence_weight

        + rr_score
        * rr_weight

        + volume_score
        * volume_weight

        + relative_strength_score
        * relative_strength_weight

    )

    return round(
        clamp(priority),
        2,
    )


# =========================================================
# QUALITY GRADE
# =========================================================

def calculate_grade(
    signal: Signal,
) -> str:
    """
    Institutional-style opportunity grade.
    """

    priority = calculate_priority_score(
        signal
    )

    score = _safe_float(
        signal.score
    )

    confidence = _safe_float(
        signal.confidence
    )

    rr = _safe_float(
        signal.risk_reward
    )

    if (
        priority >= 90
        and score >= 90
        and confidence >= 85
        and rr >= 3.0
    ):
        return "A+"

    if (
        priority >= 80
        and score >= 80
        and confidence >= 75
        and rr >= 2.5
    ):
        return "A"

    if (
        priority >= 70
        and score >= 70
        and confidence >= 65
        and rr >= 2.0
    ):
        return "B"

    if priority >= 60:
        return "C"

    return "D"


# =========================================================
# RANK SIGNALS
# =========================================================

def rank_signals(
    signals: List[Signal],
    *,
    limit: Optional[int] = None,
) -> List[Signal]:
    """
    Rank signals from highest to lowest priority.
    """

    ranked = sorted(

        signals,

        key=lambda signal: (

            calculate_priority_score(
                signal
            ),

            _safe_float(
                signal.score
            ),

            _safe_float(
                signal.confidence
            ),

            _safe_float(
                signal.risk_reward
            ),

            _safe_float(
                signal.volume_ratio
            ),

        ),

        reverse=True,

    )

    if limit is not None:

        limit = max(
            int(limit),
            0,
        )

        ranked = ranked[
            :limit
        ]

    return ranked


# =========================================================
# APPLY RANKING METADATA
# =========================================================

def apply_ranking(
    signals: List[Signal],
) -> List[Signal]:
    """
    Rank signals and store ranking information inside
    Signal.metadata.

    Metadata added:
        rank
        priority_score
        grade
    """

    ranked = rank_signals(
        signals
    )

    for rank, signal in enumerate(
        ranked,
        start=1,
    ):

        signal.metadata[
            "rank"
        ] = rank

        signal.metadata[
            "priority_score"
        ] = calculate_priority_score(
            signal
        )

        signal.metadata[
            "grade"
        ] = calculate_grade(
            signal
        )

    return ranked


# =========================================================
# TOP OPPORTUNITIES
# =========================================================

def top_opportunities(
    signals: List[Signal],
    count: int = 10,
) -> List[Signal]:
    """
    Return top N ranked opportunities.
    """

    count = max(
        int(count),
        0,
    )

    return rank_signals(
        signals,
        limit=count,
    )


# =========================================================
# BUY RANKING
# =========================================================

def rank_buy_signals(
    signals: List[Signal],
    *,
    limit: Optional[int] = None,
) -> List[Signal]:
    """
    Rank BUY signals only.
    """

    buys = [

        signal

        for signal in signals

        if signal.signal_type
        == SignalType.BUY

    ]

    return rank_signals(
        buys,
        limit=limit,
    )


# =========================================================
# SELL RANKING
# =========================================================

def rank_sell_signals(
    signals: List[Signal],
    *,
    limit: Optional[int] = None,
) -> List[Signal]:
    """
    Rank SELL signals only.
    """

    sells = [

        signal

        for signal in signals

        if signal.signal_type
        == SignalType.SELL

    ]

    return rank_signals(
        sells,
        limit=limit,
    )


# =========================================================
# FILTER QUALITY
# =========================================================

def filter_quality(
    signals: List[Signal],
    *,
    minimum_score: float = 60.0,
    minimum_confidence: float = 60.0,
    minimum_rr: float = 2.0,
) -> List[Signal]:
    """
    Remove weak opportunities before ranking.
    """

    return [

        signal

        for signal in signals

        if (
            signal.score
            >= minimum_score

            and signal.confidence
            >= minimum_confidence

            and signal.risk_reward
            >= minimum_rr
        )

    ]


# =========================================================
# BEST SIGNAL
# =========================================================

def best_signal(
    signals: List[Signal],
) -> Optional[Signal]:
    """
    Return highest-ranked signal.
    """

    ranked = rank_signals(
        signals,
        limit=1,
    )

    if not ranked:
        return None

    return ranked[0]


# =========================================================
# RANK BY SCORE
# =========================================================

def rank_by_score(
    signals: List[Signal],
) -> List[Signal]:

    return sorted(

        signals,

        key=lambda signal: signal.score,

        reverse=True,

    )


# =========================================================
# RANK BY CONFIDENCE
# =========================================================

def rank_by_confidence(
    signals: List[Signal],
) -> List[Signal]:

    return sorted(

        signals,

        key=lambda signal: signal.confidence,

        reverse=True,

    )


# =========================================================
# RANK BY RISK REWARD
# =========================================================

def rank_by_risk_reward(
    signals: List[Signal],
) -> List[Signal]:

    return sorted(

        signals,

        key=lambda signal: signal.risk_reward,

        reverse=True,

    )


# =========================================================
# RANK BY VOLUME
# =========================================================

def rank_by_volume(
    signals: List[Signal],
) -> List[Signal]:

    return sorted(

        signals,

        key=lambda signal: signal.volume_ratio,

        reverse=True,

    )


# =========================================================
# SECTOR RANKING
# =========================================================

def rank_sectors(
    signals: List[Signal],
) -> List[Dict[str, Any]]:
    """
    Rank sectors using signals generated by scanners.
    """

    sectors: Dict[
        str,
        Dict[str, Any]
    ] = {}

    for signal in signals:

        sector = (
            signal.sector.strip()
            if signal.sector
            else "UNKNOWN"
        )

        if sector not in sectors:

            sectors[
                sector
            ] = {

                "sector": sector,

                "signals": 0,

                "buy_signals": 0,

                "sell_signals": 0,

                "total_score": 0.0,

                "total_confidence": 0.0,

                "total_priority": 0.0,

            }

        row = sectors[
            sector
        ]

        row[
            "signals"
        ] += 1

        if signal.is_buy:

            row[
                "buy_signals"
            ] += 1

        elif signal.is_sell:

            row[
                "sell_signals"
            ] += 1

        row[
            "total_score"
        ] += _safe_float(
            signal.score
        )

        row[
            "total_confidence"
        ] += _safe_float(
            signal.confidence
        )

        row[
            "total_priority"
        ] += calculate_priority_score(
            signal
        )

    ranking: List[
        Dict[str, Any]
    ] = []

    for row in sectors.values():

        count = row[
            "signals"
        ]

        average_score = (
            row["total_score"]
            / count
        )

        average_confidence = (
            row["total_confidence"]
            / count
        )

        average_priority = (
            row["total_priority"]
            / count
        )

        ranking.append(

            {

                "sector":
                    row["sector"],

                "signals":
                    count,

                "buy_signals":
                    row["buy_signals"],

                "sell_signals":
                    row["sell_signals"],

                "average_score":
                    round(
                        average_score,
                        2,
                    ),

                "average_confidence":
                    round(
                        average_confidence,
                        2,
                    ),

                "average_priority":
                    round(
                        average_priority,
                        2,
                    ),

                "net_breadth":
                    (
                        row["buy_signals"]
                        - row["sell_signals"]
                    ),

            }

        )

    ranking.sort(

        key=lambda row: (

            row[
                "average_priority"
            ],

            row[
                "average_score"
            ],

            row[
                "signals"
            ],

        ),

        reverse=True,

    )

    for index, row in enumerate(
        ranking,
        start=1,
    ):

        row[
            "rank"
        ] = index

    return ranking


# =========================================================
# LEADERBOARD
# =========================================================

def build_leaderboard(
    signals: List[Signal],
    *,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """
    Build UI-ready opportunity leaderboard.

    Suitable for StockVersity dashboard table.
    """

    ranked = apply_ranking(
        signals
    )

    limit = max(
        int(limit),
        0,
    )

    rows: List[
        Dict[str, Any]
    ] = []

    for signal in ranked[
        :limit
    ]:

        rows.append(

            {

                "rank":
                    signal.metadata.get(
                        "rank",
                        0,
                    ),

                "symbol":
                    signal.symbol,

                "scanner":
                    signal.scanner_name,

                "signal":
                    signal.signal_type.value,

                "pattern":
                    signal.pattern.value,

                "price":
                    signal.last_price,

                "entry":
                    signal.entry,

                "stop_loss":
                    signal.stop_loss,

                "target":
                    signal.target1,

                "score":
                    signal.score,

                "confidence":
                    signal.confidence,

                "rr":
                    signal.risk_reward,

                "volume_ratio":
                    signal.volume_ratio,

                "priority":
                    signal.metadata.get(
                        "priority_score",
                        0.0,
                    ),

                "grade":
                    signal.metadata.get(
                        "grade",
                        "",
                    ),

            }

        )

    return rows


# =========================================================
# RANKING ENGINE
# =========================================================

class SignalRanker:
    """
    Reusable ranking service.

    Useful when ranking settings need to be configured
    once and reused by the scanner service/dashboard.
    """

    def __init__(
        self,
        *,
        minimum_score: float = 60.0,
        minimum_confidence: float = 60.0,
        minimum_rr: float = 2.0,
    ) -> None:

        self.minimum_score = (
            float(minimum_score)
        )

        self.minimum_confidence = (
            float(minimum_confidence)
        )

        self.minimum_rr = (
            float(minimum_rr)
        )

    # =====================================================
    # FILTER
    # =====================================================

    def filter(
        self,
        signals: List[Signal],
    ) -> List[Signal]:

        return filter_quality(

            signals,

            minimum_score=(
                self.minimum_score
            ),

            minimum_confidence=(
                self.minimum_confidence
            ),

            minimum_rr=(
                self.minimum_rr
            ),

        )

    # =====================================================
    # RANK
    # =====================================================

    def rank(
        self,
        signals: List[Signal],
        *,
        limit: Optional[int] = None,
    ) -> List[Signal]:

        filtered = self.filter(
            signals
        )

        ranked = apply_ranking(
            filtered
        )

        if limit is None:

            return ranked

        return ranked[
            :max(
                int(limit),
                0,
            )
        ]

    # =====================================================
    # BEST
    # =====================================================

    def best(
        self,
        signals: List[Signal],
    ) -> Optional[Signal]:

        ranked = self.rank(
            signals,
            limit=1,
        )

        if not ranked:
            return None

        return ranked[0]

    # =====================================================
    # LEADERBOARD
    # =====================================================

    def leaderboard(
        self,
        signals: List[Signal],
        *,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:

        ranked = self.rank(
            signals
        )

        return build_leaderboard(
            ranked,
            limit=limit,
        )

    # =====================================================
    # SECTORS
    # =====================================================

    def sectors(
        self,
        signals: List[Signal],
    ) -> List[Dict[str, Any]]:

        filtered = self.filter(
            signals
        )

        return rank_sectors(
            filtered
        )


# =========================================================
# DEFAULT RANKER
# =========================================================

default_ranker = SignalRanker()


# =========================================================
# EXPORTS
# =========================================================

__all__ = [

    "SignalRanker",

    "default_ranker",

    "calculate_priority_score",

    "calculate_grade",

    "rank_signals",

    "apply_ranking",

    "top_opportunities",

    "rank_buy_signals",

    "rank_sell_signals",

    "filter_quality",

    "best_signal",

    "rank_by_score",

    "rank_by_confidence",

    "rank_by_risk_reward",

    "rank_by_volume",

    "rank_sectors",

    "build_leaderboard",

    "normalize_risk_reward",

    "normalize_volume_ratio",

    "normalize_relative_strength",

]


# ==========================
# END OF FILE
# ==========================