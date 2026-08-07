"""
=========================================================
StockVersity Scanner Pro

Institutional Stock Ranking Engine

Ranks scanned stocks based on
multiple institutional factors.

Author : StockVersity
=========================================================
"""

from __future__ import annotations

import logging
import threading

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from enum import Enum

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from core.pattern_engine import PatternResult
from core.market_analyzer import MarketAnalyzer
from core.scanner.signal import Signal


# =========================================================
# ENTRY GRADE
# =========================================================

class EntryGrade(Enum):

    A_PLUS = "A+"

    A = "A"

    B = "B"

    C = "C"

    D = "D"


# =========================================================
# INSTITUTIONAL RATING
# =========================================================

class InstitutionalRating(Enum):

    ELITE = "ELITE"

    PREMIUM = "PREMIUM"

    STRONG = "STRONG"

    GOOD = "GOOD"

    AVERAGE = "AVERAGE"

    WEAK = "WEAK"


# =========================================================
# RANK RESULT
# =========================================================

@dataclass
class RankResult:

    symbol: str = ""

    company_name: str = ""

    timeframe: str = ""

    final_score: float = 0.0

    rank: int = 0

    entry_grade: EntryGrade = EntryGrade.D

    institutional_rating: InstitutionalRating = InstitutionalRating.WEAK

    pattern_score: float = 0.0

    momentum_score: float = 0.0

    trend_score: float = 0.0

    volume_score: float = 0.0

    sector_score: float = 0.0

    relative_strength_score: float = 0.0

    risk_reward_score: float = 0.0

    volatility_score: float = 0.0

    institutional_score: float = 0.0

    confidence: float = 0.0

    win_probability: float = 0.0

    risk_reward: float = 0.0

    recommendation: str = ""

    reasons: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# =========================================================
# STOCK RANKER
# =========================================================

class StockRanker:

    VERSION = "1.0.0"

    # Weight Distribution
    PATTERN_WEIGHT = 25
    TREND_WEIGHT = 20
    MOMENTUM_WEIGHT = 15
    RELATIVE_STRENGTH_WEIGHT = 10
    VOLUME_WEIGHT = 10
    SECTOR_WEIGHT = 5
    INSTITUTIONAL_WEIGHT = 5
    RISK_REWARD_WEIGHT = 5
    VOLATILITY_WEIGHT = 5

    def __init__(
        self,
        market_analyzer: Optional[
            MarketAnalyzer
        ] = None,
    ):

        self.market_analyzer = (
            market_analyzer
            if market_analyzer
            else MarketAnalyzer()
        )

        self.logger = logging.getLogger(
            self.__class__.__name__
        )

        self.lock = threading.RLock()

        self.results: List[
            RankResult
        ] = []

        self.statistics = {

            "stocks_ranked": 0,

            "elite": 0,

            "premium": 0,

            "strong": 0,

            "good": 0,

            "average": 0,

            "weak": 0,

        }

        self.started = datetime.now()

        self.logger.info(
            "StockRanker initialized."
        )

    # =====================================================
    # RESET
    # =====================================================

    def reset(self) -> None:

        self.results.clear()

    # =====================================================
    # ADD RESULT
    # =====================================================

    def add_result(
        self,
        result: RankResult,
    ) -> None:

        self.results.append(result)

        self.statistics[
            "stocks_ranked"
        ] += 1

    # =====================================================
    # COUNT
    # =====================================================

    @property
    def count(self) -> int:

        return len(self.results)

    # =====================================================
    # EMPTY
    # =====================================================

    def is_empty(self) -> bool:

        return len(self.results) == 0
        # =====================================================
    # PATTERN SCORE
    # =====================================================

    def pattern_score(
        self,
        pattern: Optional[PatternResult],
    ) -> float:
        """
        Pattern contribution (25).
        """

        if pattern is None:
            return 0.0

        return min(
            (pattern.score / 100.0)
            * self.PATTERN_WEIGHT,
            self.PATTERN_WEIGHT,
        )

    # =====================================================
    # TREND SCORE
    # =====================================================

    def trend_score(
        self,
        signal: Optional[Signal],
    ) -> float:
        """
        Trend contribution (20).
        """

        if signal is None:
            return 0.0

        score = 0.0

        if getattr(
            signal,
            "trend_confirmation",
            False,
        ):
            score += 10

        probability = float(

            getattr(
                signal,
                "win_probability",
                0,
            )

        )

        score += min(

            probability / 10,

            10,

        )

        return min(

            score,

            self.TREND_WEIGHT,

        )

    # =====================================================
    # MOMENTUM SCORE
    # =====================================================

    def momentum_score(
        self,
        signal: Optional[Signal],
    ) -> float:
        """
        Momentum contribution (15).
        """

        if signal is None:
            return 0.0

        confidence = float(

            getattr(

                signal,

                "confidence",

                0,

            )

        )

        return min(

            confidence / 100

            * self.MOMENTUM_WEIGHT,

            self.MOMENTUM_WEIGHT,

        )

    # =====================================================
    # CONFIDENCE
    # =====================================================

    def confidence_score(
        self,
        pattern: Optional[
            PatternResult
        ],
        signal: Optional[
            Signal
        ],
    ) -> float:
        """
        Combined confidence.
        """

        values = []

        if pattern:

            values.append(

                pattern.confidence

            )

        if signal:

            values.append(

                float(

                    getattr(

                        signal,

                        "confidence",

                        0,

                    )

                )

            )

        if not values:

            return 0.0

        return sum(values) / len(values)

    # =====================================================
    # WIN PROBABILITY
    # =====================================================

    def win_probability(
        self,
        confidence: float,
        final_score: float,
    ) -> float:
        """
        Estimated probability.
        """

        probability = (

            confidence * 0.60

            +

            final_score * 0.40

        )

        return min(

            probability,

            95.0,

        )

    # =====================================================
    # ENTRY GRADE
    # =====================================================

    def entry_grade(
        self,
        score: float,
    ) -> EntryGrade:
        """
        Entry grade.
        """

        if score >= 90:

            return EntryGrade.A_PLUS

        if score >= 80:

            return EntryGrade.A

        if score >= 70:

            return EntryGrade.B

        if score >= 60:

            return EntryGrade.C

        return EntryGrade.D

    # =====================================================
    # INSTITUTIONAL RATING
    # =====================================================

    def institutional_rating(
        self,
        score: float,
    ) -> InstitutionalRating:
        """
        Institutional classification.
        """

        if score >= 90:

            return InstitutionalRating.ELITE

        if score >= 80:

            return InstitutionalRating.PREMIUM

        if score >= 70:

            return InstitutionalRating.STRONG

        if score >= 60:

            return InstitutionalRating.GOOD

        if score >= 50:

            return InstitutionalRating.AVERAGE

        return InstitutionalRating.WEAK

    # =====================================================
    # UPDATE STATISTICS
    # =====================================================

    def update_statistics(
        self,
        rating: InstitutionalRating,
    ) -> None:
        """
        Update counters.
        """

        if rating == InstitutionalRating.ELITE:

            self.statistics["elite"] += 1

        elif rating == InstitutionalRating.PREMIUM:

            self.statistics["premium"] += 1

        elif rating == InstitutionalRating.STRONG:

            self.statistics["strong"] += 1

        elif rating == InstitutionalRating.GOOD:

            self.statistics["good"] += 1

        elif rating == InstitutionalRating.AVERAGE:

            self.statistics["average"] += 1

        else:

            self.statistics["weak"] += 1
                # =====================================================
    # RELATIVE STRENGTH SCORE
    # =====================================================

    def relative_strength_score(
        self,
        rs_value: float,
    ) -> float:
        """
        Relative Strength contribution (10).
        Expects RS value between 0-100.
        """

        rs_value = max(
            0.0,
            min(100.0, rs_value),
        )

        return (
            rs_value / 100.0
        ) * self.RELATIVE_STRENGTH_WEIGHT

    # =====================================================
    # VOLUME SCORE
    # =====================================================

    def volume_score(
        self,
        relative_volume: float,
    ) -> float:
        """
        Relative Volume contribution (10).
        """

        if relative_volume >= 3.0:
            return 10.0

        if relative_volume >= 2.5:
            return 9.0

        if relative_volume >= 2.0:
            return 8.0

        if relative_volume >= 1.8:
            return 7.0

        if relative_volume >= 1.5:
            return 6.0

        if relative_volume >= 1.2:
            return 4.0

        if relative_volume >= 1.0:
            return 2.0

        return 0.0

    # =====================================================
    # DELIVERY SCORE
    # =====================================================

    def delivery_score(
        self,
        delivery_percent: float,
    ) -> float:
        """
        Delivery percentage quality.
        """

        if delivery_percent >= 80:
            return 2.0

        if delivery_percent >= 70:
            return 1.5

        if delivery_percent >= 60:
            return 1.0

        return 0.0

    # =====================================================
    # COMBINED VOLUME SCORE
    # =====================================================

    def combined_volume_score(
        self,
        relative_volume: float,
        delivery_percent: float = 0.0,
    ) -> float:
        """
        RVOL + Delivery participation.
        """

        score = self.volume_score(
            relative_volume
        )

        score += self.delivery_score(
            delivery_percent
        )

        return min(
            score,
            self.VOLUME_WEIGHT,
        )

    # =====================================================
    # SECTOR SCORE
    # =====================================================

    def sector_score(
        self,
        sector_strength: float,
    ) -> float:
        """
        Sector strength contribution (5).
        """

        sector_strength = max(
            0.0,
            min(100.0, sector_strength),
        )

        return (
            sector_strength / 100.0
        ) * self.SECTOR_WEIGHT

    # =====================================================
    # MARKET TREND SCORE
    # =====================================================

    def market_score(
        self,
        market_strength: float,
    ) -> float:
        """
        Overall market trend.
        """

        market_strength = max(
            0.0,
            min(100.0, market_strength),
        )

        return (
            market_strength / 100.0
        ) * 5.0

    # =====================================================
    # INSTITUTIONAL SCORE
    # =====================================================

    def institutional_score(
        self,
        institutional_buying: bool,
        block_trade: bool,
        fii_positive: bool,
    ) -> float:
        """
        Institutional participation score (5).
        """

        score = 0.0

        if institutional_buying:
            score += 2.0

        if block_trade:
            score += 1.5

        if fii_positive:
            score += 1.5

        return min(
            score,
            self.INSTITUTIONAL_WEIGHT,
        )

    # =====================================================
    # VOLATILITY SCORE
    # =====================================================

    def volatility_score(
        self,
        atr_percent: float,
    ) -> float:
        """
        Lower ATR receives better score.
        """

        if atr_percent <= 2:
            return 5.0

        if atr_percent <= 3:
            return 4.0

        if atr_percent <= 4:
            return 3.0

        if atr_percent <= 5:
            return 2.0

        return 1.0

    # =====================================================
    # INTERMEDIATE SCORE
    # =====================================================

    def intermediate_score(
        self,
        pattern_score: float,
        trend_score: float,
        momentum_score: float,
        rs_score: float,
        volume_score: float,
        sector_score: float,
        institutional_score: float,
        volatility_score: float,
    ) -> float:
        """
        Score before Risk/Reward adjustment.
        """

        return (

            pattern_score

            + trend_score

            + momentum_score

            + rs_score

            + volume_score

            + sector_score

            + institutional_score

            + volatility_score

        )

    # =====================================================
    # BONUS SCORE
    # =====================================================

    def bonus_score(
        self,
        breakout: bool,
        multi_timeframe: bool,
        market_aligned: bool,
    ) -> float:
        """
        Small institutional bonus.
        """

        score = 0.0

        if breakout:
            score += 2.0

        if multi_timeframe:
            score += 2.0

        if market_aligned:
            score += 1.0

        return score
        # =====================================================
    # RISK / REWARD SCORE
    # =====================================================

    def risk_reward_score(
        self,
        risk_reward: float,
    ) -> float:
        """
        Risk / Reward contribution (5).
        """

        if risk_reward >= 5.0:
            return 5.0

        if risk_reward >= 4.0:
            return 4.5

        if risk_reward >= 3.0:
            return 4.0

        if risk_reward >= 2.5:
            return 3.5

        if risk_reward >= 2.0:
            return 3.0

        if risk_reward >= 1.5:
            return 2.0

        if risk_reward >= 1.0:
            return 1.0

        return 0.0

    # =====================================================
    # ATR RISK
    # =====================================================

    def atr_risk_multiplier(
        self,
        atr_percent: float,
    ) -> float:
        """
        Risk adjustment using ATR%.
        """

        if atr_percent <= 2.0:
            return 1.00

        if atr_percent <= 3.0:
            return 0.90

        if atr_percent <= 4.0:
            return 0.80

        if atr_percent <= 5.0:
            return 0.70

        return 0.60

    # =====================================================
    # POSITION SIZE %
    # =====================================================

    def position_size_percent(
        self,
        final_score: float,
        atr_percent: float,
    ) -> float:
        """
        Suggested portfolio allocation.
        """

        if final_score >= 90:
            allocation = 10.0

        elif final_score >= 80:
            allocation = 8.0

        elif final_score >= 70:
            allocation = 6.0

        elif final_score >= 60:
            allocation = 4.0

        else:
            allocation = 2.0

        return round(
            allocation
            * self.atr_risk_multiplier(
                atr_percent
            ),
            2,
        )

    # =====================================================
    # CAPITAL ALLOCATION
    # =====================================================

    def capital_allocation(
        self,
        capital: float,
        position_percent: float,
    ) -> float:
        """
        Suggested capital allocation.
        """

        if capital <= 0:
            return 0.0

        return round(
            capital
            * position_percent
            / 100,
            2,
        )

    # =====================================================
    # STOP LOSS QUALITY
    # =====================================================

    def stop_loss_quality(
        self,
        entry: float,
        stop_loss: float,
    ) -> float:
        """
        Score stop-loss distance.
        """

        if entry <= 0:
            return 0.0

        distance = (
            abs(
                entry - stop_loss
            )
            / entry
        ) * 100

        if distance <= 2:
            return 5.0

        if distance <= 3:
            return 4.0

        if distance <= 4:
            return 3.0

        if distance <= 5:
            return 2.0

        return 1.0

    # =====================================================
    # TARGET QUALITY
    # =====================================================

    def target_quality(
        self,
        entry: float,
        target: float,
    ) -> float:
        """
        Score upside potential.
        """

        if entry <= 0:
            return 0.0

        upside = (
            (target - entry)
            / entry
        ) * 100

        if upside >= 25:
            return 5.0

        if upside >= 20:
            return 4.5

        if upside >= 15:
            return 4.0

        if upside >= 10:
            return 3.0

        if upside >= 5:
            return 2.0

        return 1.0

    # =====================================================
    # RISK ADJUSTED SCORE
    # =====================================================

    def risk_adjusted_score(
        self,
        intermediate_score: float,
        risk_reward_score: float,
        atr_percent: float,
    ) -> float:
        """
        Apply risk adjustment.
        """

        total = (
            intermediate_score
            + risk_reward_score
        )

        total *= self.atr_risk_multiplier(
            atr_percent
        )

        return min(
            total,
            100.0,
        )

    # =====================================================
    # TRADE RECOMMENDATION
    # =====================================================

    def recommendation(
        self,
        score: float,
    ) -> str:
        """
        Generate recommendation.
        """

        if score >= 90:
            return "Strong Buy"

        if score >= 80:
            return "Buy"

        if score >= 70:
            return "Watchlist"

        if score >= 60:
            return "Speculative"

        return "Avoid"

    # =====================================================
    # BUILD RISK SUMMARY
    # =====================================================

    def risk_summary(
        self,
        entry: float,
        stop_loss: float,
        target: float,
        capital: float,
        atr_percent: float,
        final_score: float,
    ) -> Dict[str, Any]:
        """
        Complete risk profile.
        """

        allocation_percent = self.position_size_percent(
            final_score,
            atr_percent,
        )

        allocation = self.capital_allocation(
            capital,
            allocation_percent,
        )

        return {

            "position_percent": allocation_percent,

            "capital": allocation,

            "stop_loss_quality": self.stop_loss_quality(
                entry,
                stop_loss,
            ),

            "target_quality": self.target_quality(
                entry,
                target,
            ),

            "recommendation": self.recommendation(
                final_score,
            ),

        }
        # =====================================================
    # RANK STOCK
    # =====================================================

    def rank_stock(
        self,
        symbol: str,
        timeframe: str,
        pattern: Optional[PatternResult],
        signal: Optional[Signal],
        *,
        relative_strength: float = 50.0,
        relative_volume: float = 1.0,
        delivery_percent: float = 0.0,
        sector_strength: float = 50.0,
        institutional_buying: bool = False,
        block_trade: bool = False,
        fii_positive: bool = False,
        atr_percent: float = 3.0,
        market_strength: float = 50.0,
        breakout: bool = False,
        multi_timeframe: bool = False,
        market_aligned: bool = False,
    ) -> RankResult:
        """
        Generate institutional rank.
        """

        result = RankResult()

        result.symbol = symbol
        result.timeframe = timeframe

        # ---------------------------------------------
        # Component Scores
        # ---------------------------------------------

        result.pattern_score = self.pattern_score(
            pattern
        )

        result.trend_score = self.trend_score(
            signal
        )

        result.momentum_score = self.momentum_score(
            signal
        )

        result.relative_strength_score = (
            self.relative_strength_score(
                relative_strength
            )
        )

        result.volume_score = (
            self.combined_volume_score(
                relative_volume,
                delivery_percent,
            )
        )

        result.sector_score = (
            self.sector_score(
                sector_strength
            )
        )

        result.institutional_score = (
            self.institutional_score(
                institutional_buying,
                block_trade,
                fii_positive,
            )
        )

        result.volatility_score = (
            self.volatility_score(
                atr_percent
            )
        )

        result.risk_reward = (
            pattern.risk_reward
            if pattern
            else 0.0
        )

        result.risk_reward_score = (
            self.risk_reward_score(
                result.risk_reward
            )
        )

        # ---------------------------------------------
        # Composite Score
        # ---------------------------------------------

        intermediate = self.intermediate_score(

            result.pattern_score,

            result.trend_score,

            result.momentum_score,

            result.relative_strength_score,

            result.volume_score,

            result.sector_score,

            result.institutional_score,

            result.volatility_score,

        )

        intermediate += self.market_score(
            market_strength
        )

        intermediate += self.bonus_score(

            breakout,

            multi_timeframe,

            market_aligned,

        )

        result.final_score = (
            self.risk_adjusted_score(

                intermediate,

                result.risk_reward_score,

                atr_percent,

            )
        )

        # ---------------------------------------------
        # Confidence
        # ---------------------------------------------

        result.confidence = (
            self.confidence_score(
                pattern,
                signal,
            )
        )

        result.win_probability = (
            self.win_probability(
                result.confidence,
                result.final_score,
            )
        )

        # ---------------------------------------------
        # Rating
        # ---------------------------------------------

        result.entry_grade = (
            self.entry_grade(
                result.final_score
            )
        )

        result.institutional_rating = (
            self.institutional_rating(
                result.final_score
            )
        )

        result.recommendation = (
            self.recommendation(
                result.final_score
            )
        )

        # ---------------------------------------------
        # Reasons
        # ---------------------------------------------

        if result.pattern_score >= 20:
            result.reasons.append(
                "High-quality chart pattern"
            )

        if result.relative_strength_score >= 8:
            result.reasons.append(
                "Strong relative strength"
            )

        if result.volume_score >= 8:
            result.reasons.append(
                "High institutional volume"
            )

        if result.sector_score >= 4:
            result.reasons.append(
                "Leading sector"
            )

        if result.risk_reward >= 2:
            result.reasons.append(
                "Favorable risk/reward"
            )

        if breakout:
            result.reasons.append(
                "Confirmed breakout"
            )

        if multi_timeframe:
            result.reasons.append(
                "Multi-timeframe confirmation"
            )

        if market_aligned:
            result.reasons.append(
                "Aligned with market trend"
            )

        # ---------------------------------------------
        # Metadata
        # ---------------------------------------------

        result.metadata = {

            "market_strength": market_strength,

            "relative_volume": relative_volume,

            "relative_strength": relative_strength,

            "sector_strength": sector_strength,

            "atr_percent": atr_percent,

            "institutional_buying": institutional_buying,

            "block_trade": block_trade,

            "fii_positive": fii_positive,

        }

        self.update_statistics(
            result.institutional_rating
        )

        self.add_result(result)

        return result

    # =====================================================
    # NORMALIZE SCORES
    # =====================================================

    def normalize_scores(
        self,
    ) -> None:
        """
        Ensure scores remain within
        0-100.
        """

        for result in self.results:

            result.final_score = max(

                0.0,

                min(

                    100.0,

                    result.final_score,

                ),

            )

    # =====================================================
    # ASSIGN RANKS
    # =====================================================

    def assign_ranks(
        self,
    ) -> None:
        """
        Rank by descending score.
        """

        self.results.sort(

            key=lambda x: x.final_score,

            reverse=True,

        )

        for index, result in enumerate(

            self.results,

            start=1,

        ):

            result.rank = index

    # =====================================================
    # PROCESS ALL RESULTS
    # =====================================================

    def finalize_rankings(
        self,
    ) -> List[RankResult]:
        """
        Final ranking pipeline.
        """

        self.normalize_scores()

        self.assign_ranks()

        return self.results
        # =====================================================
    # TOP PICKS
    # =====================================================

    def top_picks(
        self,
        limit: int = 5,
    ) -> List[RankResult]:
        """
        Return highest-ranked stocks.
        """

        self.assign_ranks()

        return self.results[:limit]

    # =====================================================
    # ELITE PICKS
    # =====================================================

    def elite_picks(
        self,
    ) -> List[RankResult]:
        """
        Elite institutional opportunities.
        """

        return [

            stock

            for stock

            in self.results

            if stock.institutional_rating
            == InstitutionalRating.ELITE

        ]

    # =====================================================
    # DASHBOARD EXPORT
    # =====================================================

    def dashboard_data(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Dashboard-ready output.
        """

        data = []

        for stock in self.results:

            data.append(

                {

                    "Rank": stock.rank,

                    "Symbol": stock.symbol,

                    "Score": round(
                        stock.final_score,
                        2,
                    ),

                    "Grade": stock.entry_grade.value,

                    "Institutional": stock.institutional_rating.value,

                    "Confidence": round(
                        stock.confidence,
                        1,
                    ),

                    "Win %": round(
                        stock.win_probability,
                        1,
                    ),

                    "RR": round(
                        stock.risk_reward,
                        2,
                    ),

                    "Recommendation": stock.recommendation,

                }

            )

        return data

    # =====================================================
    # EXPORT
    # =====================================================

    def export_results(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Export complete ranking results.
        """

        return [

            {

                "symbol": stock.symbol,

                "timeframe": stock.timeframe,

                "rank": stock.rank,

                "score": stock.final_score,

                "entry_grade": stock.entry_grade.value,

                "institutional_rating": (
                    stock.institutional_rating.value
                ),

                "confidence": stock.confidence,

                "win_probability": stock.win_probability,

                "recommendation": stock.recommendation,

                "reasons": stock.reasons,

                "metadata": stock.metadata,

            }

            for stock in self.results

        ]

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(
        self,
    ) -> Dict[str, Any]:
        """
        Runtime health.
        """

        return {

            "engine": "StockRanker",

            "version": self.VERSION,

            "results": len(self.results),

            "running": True,

            "started": self.started.isoformat(),

        }

    # =====================================================
    # STATISTICS
    # =====================================================

    def statistics_report(
        self,
    ) -> Dict[str, Any]:
        """
        Ranking statistics.
        """

        uptime = (
            datetime.now()
            - self.started
        ).total_seconds()

        return {

            "version": self.VERSION,

            "uptime_seconds": round(
                uptime,
                2,
            ),

            **self.statistics,

        }

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(
        self,
    ) -> None:
        """
        Clear ranking cache.
        """

        self.results.clear()

    # =====================================================
    # CONTEXT MANAGER
    # =====================================================

    def __enter__(
        self,
    ) -> "StockRanker":

        return self

    def __exit__(
        self,
        exc_type,
        exc,
        tb,
    ) -> None:

        self.clear()

    # =====================================================
    # STRING
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (

            f"StockRanker("

            f"version={self.VERSION}, "

            f"stocks={len(self.results)})"

        )

    # =====================================================
    # FACTORY
    # =====================================================

    @classmethod
    def create(
        cls,
    ) -> "StockRanker":
        """
        Factory constructor.
        """

        return cls()

    # =====================================================
    # ANALYZE MARKET
    # =====================================================

    @classmethod
    def analyze_market(
        cls,
        rankings: List[RankResult],
    ) -> List[RankResult]:
        """
        Sort existing rankings.
        """

        rankings.sort(

            key=lambda x: x.final_score,

            reverse=True,

        )

        for index, stock in enumerate(

            rankings,

            start=1,

        ):

            stock.rank = index

        return rankings


# =========================================================
# FACTORY FUNCTION
# =========================================================

def create_stock_ranker() -> StockRanker:
    """
    Factory helper.
    """

    return StockRanker()


# ==========================================================
# END OF FILE
# ==========================================================