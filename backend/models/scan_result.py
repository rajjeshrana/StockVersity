from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any

from backend.models.opportunity import Opportunity


@dataclass(slots=True)
class ScanResult:

    # =====================================================
    # SCAN INFORMATION
    # =====================================================

    scan_name: str = ""

    scan_type: str = ""

    strategy: str = ""

    timeframe: str = ""

    market: str = "NSE"

    scanner_version: str = "4.0"

    started_at: datetime = field(
        default_factory=datetime.now
    )

    finished_at: datetime = field(
        default_factory=datetime.now
    )

    execution_time: float = 0.0

    # =====================================================
    # MARKET SUMMARY
    # =====================================================

    total_scanned: int = 0

    total_matches: int = 0

    buy_count: int = 0

    sell_count: int = 0

    wait_count: int = 0

    rejected_count: int = 0

    # =====================================================
    # MARKET BREADTH
    # =====================================================

    advances: int = 0

    declines: int = 0

    unchanged: int = 0

    advance_decline_ratio: float = 0.0

    market_sentiment: str = ""

    # =====================================================
    # INDEX DATA
    # =====================================================

    nifty_change: float = 0.0

    banknifty_change: float = 0.0

    finnifty_change: float = 0.0

    midcap_change: float = 0.0

    india_vix: float = 0.0

    # =====================================================
    # AI SUMMARY
    # =====================================================

    average_ai_score: float = 0.0

    average_confidence: float = 0.0

    average_probability: float = 0.0

    # =====================================================
    # OPPORTUNITIES
    # =====================================================

    opportunities: List[Opportunity] = field(
        default_factory=list
    )

    # =====================================================
    # SECTOR STRENGTH
    # =====================================================

    sector_strength: Dict[str, float] = field(
        default_factory=dict
    )

    # =====================================================
    # METADATA
    # =====================================================

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at: datetime = field(
        default_factory=datetime.now
    )

    # =====================================================
    # OPPORTUNITY MANAGEMENT
    # =====================================================

    def add(
        self,
        opportunity: Opportunity,
    ):

        self.opportunities.append(
            opportunity
        )

        self.total_matches = len(
            self.opportunities
        )

        signal = opportunity.signal.upper()

        if signal == "BUY":

            self.buy_count += 1

        elif signal == "SELL":

            self.sell_count += 1

        else:

            self.wait_count += 1

    # -----------------------------------------------------

    def extend(
        self,
        opportunities,
    ):

        for opportunity in opportunities:

            self.add(opportunity)

    # -----------------------------------------------------

    def clear(self):

        self.opportunities.clear()

        self.total_matches = 0

        self.buy_count = 0

        self.sell_count = 0

        self.wait_count = 0

    # =====================================================
    # TOP RESULTS
    # =====================================================

    def top(
        self,
        limit=10,
    ):

        return sorted(

            self.opportunities,

            reverse=True,

        )[:limit]

    # -----------------------------------------------------

    def buys(self):

        return [

            item

            for item in self.opportunities

            if item.signal.upper() == "BUY"

        ]

    # -----------------------------------------------------

    def sells(self):

        return [

            item

            for item in self.opportunities

            if item.signal.upper() == "SELL"

        ]

    # -----------------------------------------------------

    def waiting(self):

        return [

            item

            for item in self.opportunities

            if item.signal.upper() == "WAIT"

        ]

    # =====================================================
    # AI SUMMARY
    # =====================================================

    def calculate_summary(self):

        if not self.opportunities:

            self.average_ai_score = 0

            self.average_confidence = 0

            self.average_probability = 0

            return

        total = len(
            self.opportunities
        )

        self.average_ai_score = round(

            sum(

                o.ai_score

                for o in self.opportunities

            ) / total,

            2,

        )

        self.average_confidence = round(

            sum(

                o.confidence

                for o in self.opportunities

            ) / total,

            2,

        )

        self.average_probability = round(

            sum(

                o.probability

                for o in self.opportunities

            ) / total,

            2,

        )
            # =====================================================
    # SECTOR ANALYSIS
    # =====================================================

    def calculate_sector_strength(self):

        sectors = {}

        for opportunity in self.opportunities:

            sector = opportunity.sector or "Unknown"

            sectors.setdefault(
                sector,
                [],
            ).append(
                opportunity.score()
            )

        self.sector_strength = {

            sector: round(
                sum(scores) / len(scores),
                2,
            )

            for sector, scores in sectors.items()

        }

        return self.sector_strength

    # -----------------------------------------------------

    def strongest_sector(self):

        if not self.sector_strength:

            self.calculate_sector_strength()

        if not self.sector_strength:

            return None

        return max(

            self.sector_strength.items(),

            key=lambda item: item[1],

        )

    # -----------------------------------------------------

    def weakest_sector(self):

        if not self.sector_strength:

            self.calculate_sector_strength()

        if not self.sector_strength:

            return None

        return min(

            self.sector_strength.items(),

            key=lambda item: item[1],

        )

    # =====================================================
    # SEARCH
    # =====================================================

    def find_symbol(
        self,
        symbol,
    ):

        symbol = symbol.upper()

        for opportunity in self.opportunities:

            if opportunity.symbol.upper() == symbol:

                return opportunity

        return None

    # -----------------------------------------------------

    def filter_signal(
        self,
        signal,
    ):

        signal = signal.upper()

        return [

            opportunity

            for opportunity in self.opportunities

            if opportunity.signal.upper() == signal

        ]

    # -----------------------------------------------------

    def filter_pattern(
        self,
        pattern,
    ):

        pattern = pattern.upper()

        return [

            opportunity

            for opportunity in self.opportunities

            if opportunity.pattern.upper() == pattern

        ]

    # -----------------------------------------------------

    def filter_strategy(
        self,
        strategy,
    ):

        strategy = strategy.upper()

        return [

            opportunity

            for opportunity in self.opportunities

            if opportunity.strategy.upper() == strategy

        ]

    # -----------------------------------------------------

    def filter_score(
        self,
        minimum_score=80,
    ):

        return [

            opportunity

            for opportunity in self.opportunities

            if opportunity.score() >= minimum_score

        ]

    # =====================================================
    # SORTING
    # =====================================================

    def ranked(self):

        return sorted(

            self.opportunities,

            reverse=True,

        )

    # -----------------------------------------------------

    def best(self):

        ranked = self.ranked()

        if ranked:

            return ranked[0]

        return None

    # -----------------------------------------------------

    def worst(self):

        ranked = self.ranked()

        if ranked:

            return ranked[-1]

        return None

    # =====================================================
    # EXECUTION
    # =====================================================

    def start_timer(self):

        self.started_at = datetime.now()

    # -----------------------------------------------------

    def stop_timer(self):

        self.finished_at = datetime.now()

        self.execution_time = round(

            (

                self.finished_at

                - self.started_at

            ).total_seconds(),

            3,

        )

        return self.execution_time

    # =====================================================
    # MARKET BREADTH
    # =====================================================

    def calculate_market_breadth(self):

        total = (

            self.advances

            + self.declines

            + self.unchanged

        )

        if total == 0:

            self.advance_decline_ratio = 0

            self.market_sentiment = "UNKNOWN"

            return

        self.advance_decline_ratio = round(

            self.advances

            / max(self.declines, 1),

            2,

        )

        if self.advance_decline_ratio >= 2:

            self.market_sentiment = "STRONG_BULLISH"

        elif self.advance_decline_ratio >= 1.2:

            self.market_sentiment = "BULLISH"

        elif self.advance_decline_ratio <= 0.5:

            self.market_sentiment = "STRONG_BEARISH"

        elif self.advance_decline_ratio < 1:

            self.market_sentiment = "BEARISH"

        else:

            self.market_sentiment = "NEUTRAL"

    # =====================================================
    # DASHBOARD
    # =====================================================

    def dashboard_summary(self):

        return {

            "scan": self.scan_name,

            "strategy": self.strategy,

            "timeframe": self.timeframe,

            "matches": self.total_matches,

            "buy": self.buy_count,

            "sell": self.sell_count,

            "wait": self.wait_count,

            "average_score": self.average_ai_score,

            "confidence": self.average_confidence,

            "execution_time": self.execution_time,

            "market_sentiment": self.market_sentiment,

        }

    # -----------------------------------------------------

    def dashboard_rows(self):

        return [

            opportunity.dashboard_row()

            for opportunity in self.ranked()

        ]

    # =====================================================
    # PERFORMANCE
    # =====================================================

    def hit_rate(self):

        if self.total_scanned == 0:

            return 0

        return round(

            (

                self.total_matches

                / self.total_scanned

            ) * 100,

            2,

        )

    # -----------------------------------------------------

    def statistics(self):

        return {

            "total_scanned": self.total_scanned,

            "matches": self.total_matches,

            "hit_rate": self.hit_rate(),

            "buy": self.buy_count,

            "sell": self.sell_count,

            "wait": self.wait_count,

            "average_ai": self.average_ai_score,

            "average_confidence": self.average_confidence,

            "execution_time": self.execution_time,

        }
        # =====================================================
    # VALIDATION
    # =====================================================

    def validate(self):

        if self.total_scanned < 0:
            return False

        if self.total_matches < 0:
            return False

        if self.execution_time < 0:
            return False

        return True

    # =====================================================
    # MERGE RESULTS
    # =====================================================

    def merge(
        self,
        other,
    ):

        if not isinstance(other, ScanResult):
            return

        existing = {
            item.symbol.upper()
            for item in self.opportunities
        }

        for opportunity in other.opportunities:

            if opportunity.symbol.upper() not in existing:

                self.add(opportunity)

        self.total_scanned += other.total_scanned

        self.rejected_count += other.rejected_count

        self.calculate_summary()

        self.calculate_sector_strength()

    # =====================================================
    # COPY
    # =====================================================

    def clone(self):

        return ScanResult.from_dict(
            self.to_dict()
        )

    # =====================================================
    # SERIALIZATION
    # =====================================================

    def to_dict(self):

        return {

            "scan_name": self.scan_name,

            "scan_type": self.scan_type,

            "strategy": self.strategy,

            "timeframe": self.timeframe,

            "market": self.market,

            "scanner_version": self.scanner_version,

            "started_at": self.started_at.isoformat(),

            "finished_at": self.finished_at.isoformat(),

            "execution_time": self.execution_time,

            "total_scanned": self.total_scanned,

            "total_matches": self.total_matches,

            "buy_count": self.buy_count,

            "sell_count": self.sell_count,

            "wait_count": self.wait_count,

            "rejected_count": self.rejected_count,

            "advances": self.advances,

            "declines": self.declines,

            "unchanged": self.unchanged,

            "advance_decline_ratio": self.advance_decline_ratio,

            "market_sentiment": self.market_sentiment,

            "nifty_change": self.nifty_change,

            "banknifty_change": self.banknifty_change,

            "finnifty_change": self.finnifty_change,

            "midcap_change": self.midcap_change,

            "india_vix": self.india_vix,

            "average_ai_score": self.average_ai_score,

            "average_confidence": self.average_confidence,

            "average_probability": self.average_probability,

            "sector_strength": self.sector_strength,

            "metadata": self.metadata,

            "created_at": self.created_at.isoformat(),

            "opportunities": [

                item.to_dict()

                for item in self.opportunities

            ],

        }

    # -----------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        obj = cls()

        for key, value in data.items():

            if key == "opportunities":

                obj.opportunities = [

                    Opportunity.from_dict(item)

                    for item in value

                ]

                continue

            if key in (
                "started_at",
                "finished_at",
                "created_at",
            ):

                setattr(
                    obj,
                    key,
                    datetime.fromisoformat(value),
                )

                continue

            setattr(
                obj,
                key,
                value,
            )

        return obj

    # -----------------------------------------------------

    def to_json(self):

        import json

        return json.dumps(

            self.to_dict(),

            indent=4,

            default=str,

        )

    # -----------------------------------------------------

    @classmethod
    def from_json(
        cls,
        json_string,
    ):

        import json

        return cls.from_dict(

            json.loads(json_string)

        )

    # =====================================================
    # EXPORT HELPERS
    # =====================================================

    def export_rows(self):

        return [

            opportunity.compact_dict()

            for opportunity in self.ranked()

        ]

    # -----------------------------------------------------

    def symbols(self):

        return [

            opportunity.symbol

            for opportunity in self.opportunities

        ]

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __len__(self):

        return len(
            self.opportunities
        )

    # -----------------------------------------------------

    def __iter__(self):

        return iter(
            self.opportunities
        )

    # -----------------------------------------------------

    def __getitem__(
        self,
        index,
    ):

        return self.opportunities[index]

    # -----------------------------------------------------

    def __contains__(
        self,
        symbol,
    ):

        symbol = str(symbol).upper()

        return any(

            item.symbol.upper() == symbol

            for item in self.opportunities

        )

    # -----------------------------------------------------

    def __repr__(self):

        return (

            "ScanResult("

            f"scan='{self.scan_name}', "

            f"matches={self.total_matches}, "

            f"buy={self.buy_count}, "

            f"sell={self.sell_count})"

        )

    # -----------------------------------------------------

    def __str__(self):

        return (

            f"{self.scan_name} | "

            f"{self.total_matches} Opportunities | "

            f"{self.execution_time:.2f}s"

        )


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "ScanResult",

]