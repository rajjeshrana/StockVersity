from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from backend.ai.trading_decision_engine import (
    DecisionResult,
    TradingDecision,
    RiskLevel,
)


# ==========================================================
# OPPORTUNITY GRADE
# ==========================================================

class OpportunityGrade(Enum):
    A_PLUS = "A+"
    A = "A"
    B = "B"
    C = "C"
    D = "D"


# ==========================================================
# RANKED OPPORTUNITY
# ==========================================================

@dataclass
class RankedOpportunity:

    rank: int

    symbol: str

    score: float

    confidence: float

    grade: OpportunityGrade

    decision: TradingDecision

    risk: RiskLevel

    rr: float

    sector: str

    price: float

    volume: float

    momentum: float

    remarks: List[str] = field(default_factory=list)


# ==========================================================
# OPPORTUNITY RANKER
# ==========================================================

class OpportunityRanker:

    def __init__(self):

        self.decisions: List[DecisionResult] = []

        self.rankings: List[RankedOpportunity] = []

        self.minimum_score = 60

        self.minimum_confidence = 65

    # ======================================================
    # LOAD DECISIONS
    # ======================================================

    def load(

        self,

        decisions: List[DecisionResult],

    ) -> None:

        self.decisions = decisions

        self.rankings.clear()

    # ======================================================
    # VALIDATE
    # ======================================================

    def validate(self):

        if not self.decisions:

            raise ValueError(

                "No decision results loaded."

            )

    # ======================================================
    # SCORE
    # ======================================================

    def calculate_score(

        self,

        decision: DecisionResult,

    ) -> float:

        score = (

            decision.confidence * 0.35

            +

            decision.score * 0.35

            +

            min(

                decision.risk_reward,

                5,

            ) / 5 * 20

        )

        if decision.decision == TradingDecision.STRONG_BUY:

            score += 5

        if decision.decision == TradingDecision.STRONG_SELL:

            score += 5

        return round(

            min(

                score,

                100,

            ),

            2,

        )

    # ======================================================
    # GRADE
    # ======================================================

    def grade(

        self,

        score: float,

    ) -> OpportunityGrade:

        if score >= 90:

            return OpportunityGrade.A_PLUS

        if score >= 80:

            return OpportunityGrade.A

        if score >= 70:

            return OpportunityGrade.B

        if score >= 60:

            return OpportunityGrade.C

        return OpportunityGrade.D

    # ======================================================
    # FILTER
    # ======================================================

    def eligible(

        self,

        decision: DecisionResult,

    ) -> bool:

        if decision.confidence < self.minimum_confidence:

            return False

        if decision.score < self.minimum_score:

            return False

        if decision.decision in (

            TradingDecision.HOLD,

            TradingDecision.WATCH,

        ):

            return False

        return True
        # ======================================================
    # MOMENTUM SCORE
    # ======================================================

    def momentum_score(

        self,

        momentum: float,

    ) -> float:

        if momentum >= 10:

            return 100.0

        if momentum <= -10:

            return 0.0

        score = (momentum + 10) * 5

        return round(

            min(

                max(score, 0),

                100,

            ),

            2,

        )

    # ======================================================
    # VOLUME SCORE
    # ======================================================

    def volume_score(

        self,

        volume_ratio: float,

    ) -> float:

        score = min(

            volume_ratio,

            3,

        ) / 3 * 100

        return round(

            score,

            2,

        )

    # ======================================================
    # SECTOR SCORE
    # ======================================================

    def sector_score(

        self,

        sector_strength: float,

    ) -> float:

        return round(

            min(

                max(

                    sector_strength,

                    0,

                ),

                100,

            ),

            2,

        )

    # ======================================================
    # INSTITUTIONAL PRIORITY
    # ======================================================

    def institutional_priority(

        self,

        decision: DecisionResult,

    ) -> float:

        priority = decision.confidence * 0.50

        priority += decision.score * 0.30

        priority += min(

            decision.risk_reward,

            5,

        ) * 4

        return round(

            min(

                priority,

                100,

            ),

            2,

        )

    # ======================================================
    # COMPOSITE SCORE
    # ======================================================

    def composite_score(

        self,

        decision: DecisionResult,

        momentum: float,

        volume_ratio: float,

        sector_strength: float,

    ) -> float:

        technical = self.calculate_score(

            decision,

        )

        momentum_component = self.momentum_score(

            momentum,

        )

        volume_component = self.volume_score(

            volume_ratio,

        )

        sector_component = self.sector_score(

            sector_strength,

        )

        institutional = self.institutional_priority(

            decision,

        )

        score = (

            technical * 0.40

            +

            momentum_component * 0.15

            +

            volume_component * 0.15

            +

            sector_component * 0.10

            +

            institutional * 0.20

        )

        return round(

            min(

                score,

                100,

            ),

            2,

        )

    # ======================================================
    # BUILD RANKING
    # ======================================================

    def build_ranking(

        self,

        decision: DecisionResult,

        sector: str,

        momentum: float,

        volume: float,

        price: float,

        sector_strength: float,

    ) -> RankedOpportunity:

        score = self.composite_score(

            decision,

            momentum,

            volume,

            sector_strength,

        )

        return RankedOpportunity(

            rank=0,

            symbol=decision.symbol,

            score=score,

            confidence=decision.confidence,

            grade=self.grade(score),

            decision=decision.decision,

            risk=decision.risk,

            rr=decision.risk_reward,

            sector=sector,

            price=price,

            volume=volume,

            momentum=momentum,

            remarks=[],

        )

    # ======================================================
    # SORT RANKINGS
    # ======================================================

    def sort_rankings(

        self,

    ) -> None:

        self.rankings.sort(

            key=lambda x: (

                x.score,

                x.confidence,

                x.rr,

            ),

            reverse=True,

        )

        for index, item in enumerate(

            self.rankings,

            start=1,

        ):

            item.rank = index

    # ======================================================
    # TOP OPPORTUNITIES
    # ======================================================

    def top_opportunities(

        self,

        limit: int = 10,

    ) -> List[RankedOpportunity]:

        self.sort_rankings()

        return self.rankings[:limit]

    # ======================================================
    # RANK STATISTICS
    # ======================================================

    def statistics(

        self,

    ) -> Dict:

        if not self.rankings:

            return {}

        scores = [

            x.score

            for x in self.rankings

        ]

        return {

            "count":

                len(

                    self.rankings,

                ),

            "average":

                round(

                    float(

                        np.mean(

                            scores,

                        )

                    ),

                    2,

                ),

            "highest":

                round(

                    max(

                        scores,

                    ),

                    2,

                ),

            "lowest":

                round(

                    min(

                        scores,

                    ),

                    2,

                ),

        }
        # ======================================================
    # ATR NORMALIZATION
    # ======================================================

    def atr_score(

        self,

        atr_percent: float,

    ) -> float:

        if atr_percent <= 0:

            return 0.0

        if 1.5 <= atr_percent <= 4.0:

            return 100.0

        if atr_percent < 1.5:

            return round(

                atr_percent / 1.5 * 100,

                2,

            )

        excess = min(

            atr_percent,

            8.0,

        )

        score = 100 - ((excess - 4.0) / 4.0) * 100

        return round(

            max(score, 0),

            2,

        )

    # ======================================================
    # VOLATILITY SCORE
    # ======================================================

    def volatility_score(

        self,

        volatility: float,

    ) -> float:

        optimal = 25.0

        distance = abs(

            volatility - optimal,

        )

        score = max(

            100 - distance * 3,

            0,

        )

        return round(

            score,

            2,

        )

    # ======================================================
    # LIQUIDITY SCORE
    # ======================================================

    def liquidity_score(

        self,

        avg_turnover: float,

    ) -> float:

        if avg_turnover >= 500:

            return 100

        if avg_turnover >= 250:

            return 90

        if avg_turnover >= 100:

            return 80

        if avg_turnover >= 50:

            return 65

        if avg_turnover >= 20:

            return 45

        return 20

    # ======================================================
    # TREND QUALITY
    # ======================================================

    def trend_quality(

        self,

        ema_alignment: bool,

        adx: float,

    ) -> float:

        score = 0.0

        if ema_alignment:

            score += 50

        score += min(

            adx,

            50,

        )

        return round(

            min(

                score,

                100,

            ),

            2,

        )

    # ======================================================
    # BREAKOUT QUALITY
    # ======================================================

    def breakout_quality(

        self,

        breakout_volume: float,

        breakout_strength: float,

    ) -> float:

        volume = min(

            breakout_volume,

            3,

        ) / 3 * 50

        strength = min(

            breakout_strength,

            10,

        ) / 10 * 50

        return round(

            volume + strength,

            2,

        )

    # ======================================================
    # PENALTY ENGINE
    # ======================================================

    def penalty_score(

        self,

        gap_percent: float,

        spread_percent: float,

        near_resistance: bool,

    ) -> float:

        penalty = 0

        if abs(

            gap_percent,

        ) > 3:

            penalty += 15

        if spread_percent > 0.50:

            penalty += 10

        if near_resistance:

            penalty += 10

        return penalty

    # ======================================================
    # RISK ADJUSTED SCORE
    # ======================================================

    def risk_adjusted_score(

        self,

        base_score: float,

        atr_percent: float,

        volatility: float,

        liquidity: float,

        ema_alignment: bool,

        adx: float,

        breakout_volume: float,

        breakout_strength: float,

        gap_percent: float,

        spread_percent: float,

        near_resistance: bool,

    ) -> float:

        atr = self.atr_score(

            atr_percent,

        )

        vol = self.volatility_score(

            volatility,

        )

        liq = self.liquidity_score(

            liquidity,

        )

        trend = self.trend_quality(

            ema_alignment,

            adx,

        )

        breakout = self.breakout_quality(

            breakout_volume,

            breakout_strength,

        )

        bonus = (

            atr * 0.08

            +

            vol * 0.08

            +

            liq * 0.08

            +

            trend * 0.10

            +

            breakout * 0.10

        )

        penalty = self.penalty_score(

            gap_percent,

            spread_percent,

            near_resistance,

        )

        score = base_score + bonus - penalty

        return round(

            min(

                max(

                    score,

                    0,

                ),

                100,

            ),

            2,

        )

    # ======================================================
    # FINAL AI ADJUSTMENT
    # ======================================================

    def ai_adjustment(

        self,

        score: float,

        decision: TradingDecision,

        confidence: float,

    ) -> float:

        adjusted = score

        if decision == TradingDecision.STRONG_BUY:

            adjusted += 3

        elif decision == TradingDecision.BUY:

            adjusted += 1.5

        elif decision == TradingDecision.STRONG_SELL:

            adjusted += 2

        adjusted += (

            confidence - 70

        ) * 0.10

        return round(

            min(

                max(

                    adjusted,

                    0,

                ),

                100,

            ),

            2,

        )
        # ======================================================
    # MULTI-TIMEFRAME SCORE
    # ======================================================

    def multi_timeframe_score(

        self,

        timeframe_signals: Dict[str, str],

    ) -> float:

        weights = {

            "1m": 0.05,

            "5m": 0.10,

            "15m": 0.15,

            "30m": 0.20,

            "1h": 0.20,

            "4h": 0.15,

            "1d": 0.15,

        }

        score = 0.0

        total_weight = 0.0

        for tf, signal in timeframe_signals.items():

            weight = weights.get(

                tf,

                0.05,

            )

            total_weight += weight

            signal = signal.upper()

            if signal in (

                "STRONG_BUY",

                "BUY",

                "BULLISH",

            ):

                score += weight * 100

            elif signal in (

                "SELL",

                "STRONG_SELL",

                "BEARISH",

            ):

                score += weight * 20

            else:

                score += weight * 50

        if total_weight == 0:

            return 50.0

        return round(

            score / total_weight,

            2,

        )

    # ======================================================
    # SECTOR ROTATION SCORE
    # ======================================================

    def sector_rotation_score(

        self,

        sector_rank: int,

        total_sectors: int,

    ) -> float:

        if total_sectors <= 0:

            return 50.0

        score = (

            (total_sectors - sector_rank + 1)

            /

            total_sectors

        ) * 100

        return round(

            max(

                min(

                    score,

                    100,

                ),

                0,

            ),

            2,

        )

    # ======================================================
    # RELATIVE STRENGTH SCORE
    # ======================================================

    def relative_strength_score(

        self,

        rs_value: float,

    ) -> float:

        score = rs_value + 50

        return round(

            max(

                min(

                    score,

                    100,

                ),

                0,

            ),

            2,

        )

    # ======================================================
    # INSTITUTIONAL MONEY FLOW
    # ======================================================

    def money_flow_score(

        self,

        delivery_percent: float,

        volume_ratio: float,

    ) -> float:

        delivery = min(

            delivery_percent,

            100,

        ) * 0.50

        volume = min(

            volume_ratio,

            3,

        ) / 3 * 50

        return round(

            delivery + volume,

            2,

        )

    # ======================================================
    # CONFIDENCE OPTIMIZER
    # ======================================================

    def optimize_confidence(

        self,

        confidence: float,

        mtf_score: float,

        money_flow: float,

        rs_score: float,

    ) -> float:

        adjusted = (

            confidence * 0.60

            +

            mtf_score * 0.15

            +

            money_flow * 0.15

            +

            rs_score * 0.10

        )

        return round(

            min(

                adjusted,

                100,

            ),

            2,

        )

    # ======================================================
    # WATCHLIST BUILDER
    # ======================================================

    def build_watchlist(

        self,

        rankings: Optional[List[RankedOpportunity]] = None,

        minimum_grade: OpportunityGrade = OpportunityGrade.B,

    ) -> List[RankedOpportunity]:

        if rankings is None:

            rankings = self.rankings

        order = {

            OpportunityGrade.A_PLUS: 5,

            OpportunityGrade.A: 4,

            OpportunityGrade.B: 3,

            OpportunityGrade.C: 2,

            OpportunityGrade.D: 1,

        }

        minimum = order[minimum_grade]

        return [

            item

            for item in rankings

            if order[item.grade] >= minimum

        ]

    # ======================================================
    # OPPORTUNITY CLUSTERS
    # ======================================================

    def cluster_opportunities(

        self,

        rankings: Optional[List[RankedOpportunity]] = None,

    ) -> Dict[str, List[RankedOpportunity]]:

        if rankings is None:

            rankings = self.rankings

        clusters = {

            "A+": [],

            "A": [],

            "B": [],

            "C": [],

            "D": [],

        }

        for item in rankings:

            clusters[

                item.grade.value

            ].append(

                item,

            )

        return clusters

    # ======================================================
    # DYNAMIC RANK UPDATE
    # ======================================================

    def update_rankings(

        self,

        rankings: Optional[List[RankedOpportunity]] = None,

    ) -> List[RankedOpportunity]:

        if rankings is None:

            rankings = self.rankings

        rankings.sort(

            key=lambda x: (

                x.score,

                x.confidence,

                x.rr,

            ),

            reverse=True,

        )

        for index, item in enumerate(

            rankings,

            start=1,

        ):

            item.rank = index

        return rankings
        # ======================================================
    # POSITION SIZE RECOMMENDATION
    # ======================================================

    def recommended_position_size(

        self,

        capital: float,

        opportunity: RankedOpportunity,

        max_allocation_percent: float = 20.0,

    ) -> float:

        allocation = (

            opportunity.score

            / 100

        ) * max_allocation_percent

        allocation = min(

            allocation,

            max_allocation_percent,

        )

        return round(

            capital * allocation / 100,

            2,

        )

    # ======================================================
    # PORTFOLIO ALLOCATION
    # ======================================================

    def portfolio_allocation(

        self,

        capital: float,

        rankings: Optional[List[RankedOpportunity]] = None,

    ) -> List[Dict]:

        if rankings is None:

            rankings = self.rankings

        rankings = self.update_rankings(

            rankings,

        )

        total_score = sum(

            item.score

            for item in rankings

        )

        allocations = []

        if total_score <= 0:

            return allocations

        for item in rankings:

            weight = item.score / total_score

            allocations.append({

                "rank":

                    item.rank,

                "symbol":

                    item.symbol,

                "weight_percent":

                    round(

                        weight * 100,

                        2,

                    ),

                "capital":

                    round(

                        capital * weight,

                        2,

                    ),

            })

        return allocations

    # ======================================================
    # RISK CONCENTRATION
    # ======================================================

    def risk_concentration(

        self,

        rankings: Optional[List[RankedOpportunity]] = None,

    ) -> Dict:

        if rankings is None:

            rankings = self.rankings

        risk_count = {

            RiskLevel.VERY_LOW: 0,

            RiskLevel.LOW: 0,

            RiskLevel.MEDIUM: 0,

            RiskLevel.HIGH: 0,

            RiskLevel.VERY_HIGH: 0,

        }

        for item in rankings:

            risk_count[item.risk] += 1

        return {

            level.value: count

            for level, count in risk_count.items()

        }

    # ======================================================
    # SECTOR EXPOSURE
    # ======================================================

    def sector_exposure(

        self,

        rankings: Optional[List[RankedOpportunity]] = None,

    ) -> Dict[str, float]:

        if rankings is None:

            rankings = self.rankings

        total = max(

            len(rankings),

            1,

        )

        exposure = {}

        for item in rankings:

            exposure.setdefault(

                item.sector,

                0,

            )

            exposure[item.sector] += 1

        for sector in exposure:

            exposure[sector] = round(

                exposure[sector]

                /

                total

                * 100,

                2,

            )

        return exposure

    # ======================================================
    # TRADE CONFLICT DETECTION
    # ======================================================

    def detect_conflicts(

        self,

        rankings: Optional[List[RankedOpportunity]] = None,

    ) -> List[str]:

        if rankings is None:

            rankings = self.rankings

        conflicts = []

        seen = {}

        for item in rankings:

            if item.symbol in seen:

                conflicts.append(

                    item.symbol

                )

            else:

                seen[item.symbol] = item

        return conflicts

    # ======================================================
    # REMOVE DUPLICATES
    # ======================================================

    def remove_duplicates(

        self,

        rankings: Optional[List[RankedOpportunity]] = None,

    ) -> List[RankedOpportunity]:

        if rankings is None:

            rankings = self.rankings

        unique = {}

        for item in rankings:

            if item.symbol not in unique:

                unique[item.symbol] = item

            elif item.score > unique[item.symbol].score:

                unique[item.symbol] = item

        cleaned = list(

            unique.values(),

        )

        return self.update_rankings(

            cleaned,

        )

    # ======================================================
    # PORTFOLIO OPTIMIZER
    # ======================================================

    def optimize_portfolio(

        self,

        capital: float,

        max_positions: int = 10,

    ) -> Dict:

        rankings = self.remove_duplicates()

        rankings = self.update_rankings(

            rankings,

        )[:max_positions]

        allocations = self.portfolio_allocation(

            capital,

            rankings,

        )

        return {

            "positions":

                rankings,

            "allocation":

                allocations,

            "sector_exposure":

                self.sector_exposure(

                    rankings,

                ),

            "risk_distribution":

                self.risk_concentration(

                    rankings,

                ),

        }

    # ======================================================
    # PORTFOLIO SUMMARY
    # ======================================================

    def portfolio_summary(

        self,

        capital: float,

    ) -> Dict:

        optimized = self.optimize_portfolio(

            capital,

        )

        return {

            "generated":

                datetime.now().isoformat(),

            "capital":

                capital,

            "positions":

                len(

                    optimized["positions"],

                ),

            "allocation":

                optimized["allocation"],

            "sector_exposure":

                optimized["sector_exposure"],

            "risk_distribution":

                optimized["risk_distribution"],

        }
        # ======================================================
    # MARKET BREADTH SCORE
    # ======================================================

    def market_breadth_score(

        self,

        advancing: int,

        declining: int,

    ) -> float:

        total = max(

            advancing + declining,

            1,

        )

        ratio = advancing / total

        return round(

            ratio * 100,

            2,

        )

    # ======================================================
    # RELATIVE SECTOR RANK
    # ======================================================

    def relative_sector_rank(

        self,

        sector_return: float,

        market_return: float,

    ) -> float:

        alpha = sector_return - market_return

        score = 50 + alpha * 5

        return round(

            max(

                min(score, 100),

                0,

            ),

            2,

        )

    # ======================================================
    # INSTITUTIONAL ACCUMULATION
    # ======================================================

    def institutional_accumulation(

        self,

        delivery_percent: float,

        block_deals: int,

        bulk_deals: int,

    ) -> float:

        score = delivery_percent * 0.60

        score += min(

            block_deals,

            5,

        ) * 6

        score += min(

            bulk_deals,

            5,

        ) * 4

        return round(

            min(

                score,

                100,

            ),

            2,

        )

    # ======================================================
    # FII / DII SENTIMENT
    # ======================================================

    def fii_dii_sentiment(

        self,

        fii_flow: float,

        dii_flow: float,

    ) -> Dict:

        net = fii_flow + dii_flow

        if net >= 1000:

            sentiment = "VERY_BULLISH"

        elif net >= 300:

            sentiment = "BULLISH"

        elif net <= -1000:

            sentiment = "VERY_BEARISH"

        elif net <= -300:

            sentiment = "BEARISH"

        else:

            sentiment = "NEUTRAL"

        score = max(

            min(

                50 + net / 40,

                100,

            ),

            0,

        )

        return {

            "net_flow": net,

            "sentiment": sentiment,

            "score": round(score, 2),

        }

    # ======================================================
    # HEAT MAP SCORE
    # ======================================================

    def heat_map_score(

        self,

        ranking: RankedOpportunity,

        market_breadth: float,

        institutional_score: float,

        sector_score: float,

    ) -> float:

        score = (

            ranking.score * 0.55

            +

            market_breadth * 0.15

            +

            institutional_score * 0.15

            +

            sector_score * 0.15

        )

        return round(

            min(

                score,

                100,

            ),

            2,

        )

    # ======================================================
    # SMART FILTER
    # ======================================================

    def smart_filter(

        self,

        minimum_score: float = 75,

        minimum_confidence: float = 75,

    ) -> List[RankedOpportunity]:

        return [

            item

            for item in self.rankings

            if (

                item.score >= minimum_score

                and

                item.confidence >= minimum_confidence

            )

        ]

    # ======================================================
    # RANK CONFIDENCE ANALYTICS
    # ======================================================

    def confidence_analytics(

        self,

        rankings: Optional[List[RankedOpportunity]] = None,

    ) -> Dict:

        if rankings is None:

            rankings = self.rankings

        if not rankings:

            return {}

        confidence = [

            x.confidence

            for x in rankings

        ]

        return {

            "average":

                round(

                    float(

                        np.mean(

                            confidence,

                        )

                    ),

                    2,

                ),

            "highest":

                round(

                    max(

                        confidence,

                    ),

                    2,

                ),

            "lowest":

                round(

                    min(

                        confidence,

                    ),

                    2,

                ),

            "std":

                round(

                    float(

                        np.std(

                            confidence,

                        )

                    ),

                    2,

                ),

        }

    # ======================================================
    # ADVANCED DASHBOARD
    # ======================================================

    def dashboard(

        self,

        breadth: float,

        fii_dii: Dict,

    ) -> Dict:

        return {

            "generated":

                datetime.now().isoformat(),

            "total_opportunities":

                len(

                    self.rankings,

                ),

            "top_10":

                self.top_opportunities(

                    10,

                ),

            "statistics":

                self.statistics(),

            "confidence":

                self.confidence_analytics(),

            "market_breadth":

                breadth,

            "institutional_sentiment":

                fii_dii,

        }
        # ======================================================
    # AI RECOMMENDATION ENGINE
    # ======================================================

    def generate_recommendations(

        self,

        rankings: Optional[List[RankedOpportunity]] = None,

    ) -> List[Dict]:

        if rankings is None:

            rankings = self.rankings

        recommendations = []

        for item in self.update_rankings(rankings):

            action = "WATCH"

            if item.decision in (

                TradingDecision.STRONG_BUY,

                TradingDecision.BUY,

            ):

                action = "BUY"

            elif item.decision in (

                TradingDecision.STRONG_SELL,

                TradingDecision.SELL,

            ):

                action = "SELL"

            recommendations.append({

                "rank": item.rank,

                "symbol": item.symbol,

                "action": action,

                "confidence": item.confidence,

                "score": item.score,

                "grade": item.grade.value,

            })

        return recommendations

    # ======================================================
    # BUY PRIORITY QUEUE
    # ======================================================

    def buy_queue(

        self,

    ) -> List[RankedOpportunity]:

        return [

            item

            for item in self.update_rankings()

            if item.decision in (

                TradingDecision.BUY,

                TradingDecision.STRONG_BUY,

            )

        ]

    # ======================================================
    # SELL PRIORITY QUEUE
    # ======================================================

    def sell_queue(

        self,

    ) -> List[RankedOpportunity]:

        return [

            item

            for item in self.update_rankings()

            if item.decision in (

                TradingDecision.SELL,

                TradingDecision.STRONG_SELL,

            )

        ]

    # ======================================================
    # WATCHLIST SCORE
    # ======================================================

    def watchlist_score(

        self,

        opportunity: RankedOpportunity,

    ) -> float:

        score = (

            opportunity.score * 0.60

            +

            opportunity.confidence * 0.40

        )

        return round(

            min(score, 100),

            2,

        )

    # ======================================================
    # ENTRY TIMING
    # ======================================================

    def entry_timing(

        self,

        opportunity: RankedOpportunity,

    ) -> str:

        if opportunity.score >= 90:

            return "ENTER IMMEDIATELY"

        if opportunity.score >= 80:

            return "WAIT FOR PULLBACK"

        if opportunity.score >= 70:

            return "WATCH FOR BREAKOUT"

        return "OBSERVE"

    # ======================================================
    # EXIT PRIORITY
    # ======================================================

    def exit_priority(

        self,

        opportunity: RankedOpportunity,

    ) -> int:

        if opportunity.decision == TradingDecision.STRONG_SELL:

            return 1

        if opportunity.decision == TradingDecision.SELL:

            return 2

        if opportunity.risk == RiskLevel.VERY_HIGH:

            return 3

        if opportunity.risk == RiskLevel.HIGH:

            return 4

        return 5

    # ======================================================
    # PORTFOLIO REBALANCE
    # ======================================================

    def rebalance_portfolio(

        self,

        current_symbols: List[str],

    ) -> Dict:

        buys = []

        sells = []

        ranked = self.update_rankings()

        top_symbols = {

            item.symbol

            for item in ranked[:10]

        }

        for symbol in current_symbols:

            if symbol not in top_symbols:

                sells.append(symbol)

        for item in ranked[:10]:

            if item.symbol not in current_symbols:

                buys.append(item.symbol)

        return {

            "buy": buys,

            "sell": sells,

        }

    # ======================================================
    # EXPLAINABLE RANKING
    # ======================================================

    def explain(

        self,

        opportunity: RankedOpportunity,

    ) -> Dict:

        return {

            "symbol": opportunity.symbol,

            "rank": opportunity.rank,

            "grade": opportunity.grade.value,

            "score": opportunity.score,

            "confidence": opportunity.confidence,

            "decision": opportunity.decision.value,

            "entry_timing": self.entry_timing(

                opportunity,

            ),

            "remarks": opportunity.remarks,

        }

    # ======================================================
    # RECOMMENDATION HISTORY
    # ======================================================

    def recommendation_history(

        self,

    ) -> List[Dict]:

        history = []

        for item in self.rankings:

            history.append({

                "timestamp": datetime.now().isoformat(),

                "symbol": item.symbol,

                "rank": item.rank,

                "score": item.score,

                "grade": item.grade.value,

            })

        return history
        # ======================================================
    # COMPLETE RANKING PIPELINE
    # ======================================================

    def execute(
        self,
        decisions: List[DecisionResult],
        market_data: Dict[str, Dict],
    ) -> List[RankedOpportunity]:

        self.load(decisions)
        self.validate()

        self.rankings.clear()

        for decision in self.decisions:

            if not self.eligible(decision):
                continue

            data = market_data.get(decision.symbol, {})

            ranking = self.build_ranking(
                decision=decision,
                sector=data.get("sector", "UNKNOWN"),
                momentum=data.get("momentum", 0.0),
                volume=data.get("volume_ratio", 1.0),
                price=data.get("price", 0.0),
                sector_strength=data.get(
                    "sector_strength",
                    50.0,
                ),
            )

            base = self.risk_adjusted_score(
                base_score=ranking.score,
                atr_percent=data.get("atr_percent", 2.0),
                volatility=data.get("volatility", 25.0),
                liquidity=data.get("liquidity", 100.0),
                ema_alignment=data.get(
                    "ema_alignment",
                    True,
                ),
                adx=data.get("adx", 25.0),
                breakout_volume=data.get(
                    "breakout_volume",
                    1.5,
                ),
                breakout_strength=data.get(
                    "breakout_strength",
                    5.0,
                ),
                gap_percent=data.get(
                    "gap_percent",
                    0.0,
                ),
                spread_percent=data.get(
                    "spread_percent",
                    0.10,
                ),
                near_resistance=data.get(
                    "near_resistance",
                    False,
                ),
            )

            ranking.score = self.ai_adjustment(
                score=base,
                decision=ranking.decision,
                confidence=ranking.confidence,
            )

            ranking.grade = self.grade(
                ranking.score,
            )

            self.rankings.append(
                ranking,
            )

        self.rankings = self.remove_duplicates(
            self.rankings,
        )

        self.update_rankings()

        self.runtime = {

            "generated": datetime.now().isoformat(),

            "total_decisions": len(self.decisions),

            "eligible": len(self.rankings),

        }

        return self.rankings

    # ======================================================
    # DATAFRAME EXPORT
    # ======================================================

    def to_dataframe(
        self,
    ) -> pd.DataFrame:

        rows = []

        for item in self.rankings:

            rows.append({

                "Rank": item.rank,

                "Symbol": item.symbol,

                "Score": item.score,

                "Confidence": item.confidence,

                "Grade": item.grade.value,

                "Decision": item.decision.value,

                "Risk": item.risk.value,

                "RR": item.rr,

                "Sector": item.sector,

                "Price": item.price,

                "Momentum": item.momentum,

            })

        return pd.DataFrame(rows)

    # ======================================================
    # JSON EXPORT
    # ======================================================

    def export_json(
        self,
        path: str,
    ) -> None:

        records = self.to_dataframe().to_dict(
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
        path: str,
    ) -> None:

        self.to_dataframe().to_csv(
            path,
            index=False,
        )

    # ======================================================
    # COMPLETE REPORT
    # ======================================================

    def report(
        self,
    ) -> Dict:

        return {

            "generated":

                datetime.now().isoformat(),

            "statistics":

                self.statistics(),

            "confidence":

                self.confidence_analytics(),

            "portfolio":

                self.portfolio_summary(
                    capital=100000,
                ),

            "recommendations":

                self.generate_recommendations(),

        }

    # ======================================================
    # SERIALIZATION
    # ======================================================

    def to_dict(
        self,
    ) -> List[Dict]:

        return self.to_dataframe().to_dict(
            orient="records",
        )

    # ======================================================
    # RESET
    # ======================================================

    def reset(
        self,
    ) -> None:

        self.decisions.clear()

        self.rankings.clear()

        self.runtime = {}

    # ======================================================
    # VERSION
    # ======================================================

    @staticmethod
    def version() -> str:

        return "StockVersity Opportunity Ranker v4.0"

    # ======================================================
    # STATUS
    # ======================================================

    def status(
        self,
    ) -> Dict:

        return {

            "loaded_decisions":

                len(self.decisions),

            "ranked_opportunities":

                len(self.rankings),

            "runtime":

                getattr(
                    self,
                    "runtime",
                    {},
                ),

            "version":

                self.version(),

        }

# ==========================================================
# END OF FILE
# ==========================================================