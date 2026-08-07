from __future__ import annotations

import math
import statistics
import threading
import uuid

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


# =====================================================
# ANALYTICS RECORD
# =====================================================

@dataclass(slots=True)
class AnalyticsRecord:

    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    name: str = ""

    category: str = ""

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    values: List[float] = field(
        default_factory=list
    )

    metadata: Dict = field(
        default_factory=dict
    )


# =====================================================
# ANALYTICS MANAGER
# =====================================================

class AnalyticsManager:

    _instance = None

    _lock = threading.Lock()

    # -------------------------------------------------

    def __new__(cls):

        with cls._lock:

            if cls._instance is None:

                cls._instance = super().__new__(cls)

        return cls._instance

    # -------------------------------------------------

    def __init__(self):

        if getattr(

            self,

            "_initialized",

            False,

        ):

            return

        self._initialized = True

        self.manager_lock = threading.RLock()

        self.records: List[
            AnalyticsRecord
        ] = []

    # =====================================================
    # CREATE RECORD
    # =====================================================

    def create(

        self,

        name: str,

        category: str,

        values: Optional[
            List[float]
        ] = None,

        metadata: Optional[
            Dict
        ] = None,

    ):

        record = AnalyticsRecord(

            name=name,

            category=category,

            values=values or [],

            metadata=metadata or {},

        )

        self.records.append(

            record

        )

        return record

    # =====================================================
    # GET RECORD
    # =====================================================

    def get(

        self,

        record_id: str,

    ):

        for record in self.records:

            if record.id == record_id:

                return record

        return None

    # =====================================================
    # LIST
    # =====================================================

    def list_records(

        self,

    ):

        return list(

            self.records

        )

    # =====================================================
    # MEAN
    # =====================================================

    def mean(

        self,

        values: List[float],

    ):

        if not values:

            return 0.0

        return statistics.mean(

            values

        )

    # =====================================================
    # MEDIAN
    # =====================================================

    def median(

        self,

        values: List[float],

    ):

        if not values:

            return 0.0

        return statistics.median(

            values

        )

    # =====================================================
    # STANDARD DEVIATION
    # =====================================================

    def std(

        self,

        values: List[float],

    ):

        if len(values) < 2:

            return 0.0

        return statistics.stdev(

            values

        )

    # =====================================================
    # VARIANCE
    # =====================================================

    def variance(

        self,

        values: List[float],

    ):

        if len(values) < 2:

            return 0.0

        return statistics.variance(

            values

        )

    # =====================================================
    # MIN
    # =====================================================

    def minimum(

        self,

        values: List[float],

    ):

        return min(

            values,

            default=0.0,

        )

    # =====================================================
    # MAX
    # =====================================================

    def maximum(

        self,

        values: List[float],

    ):

        return max(

            values,

            default=0.0,

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

        values: List[float],

    ):

        return {

            "count": len(

                values

            ),

            "mean": self.mean(

                values

            ),

            "median": self.median(

                values

            ),

            "std": self.std(

                values

            ),

            "variance": self.variance(

                values

            ),

            "min": self.minimum(

                values

            ),

            "max": self.maximum(

                values

            ),

        }
        # =====================================================
    # WIN RATE
    # =====================================================

    def win_rate(

        self,

        wins: int,

        losses: int,

    ):

        total = wins + losses

        if total == 0:

            return 0.0

        return (

            wins / total

        ) * 100

    # =====================================================
    # PROFIT FACTOR
    # =====================================================

    def profit_factor(

        self,

        gross_profit: float,

        gross_loss: float,

    ):

        if gross_loss == 0:

            return float("inf")

        return gross_profit / abs(

            gross_loss

        )

    # =====================================================
    # EXPECTANCY
    # =====================================================

    def expectancy(

        self,

        avg_win: float,

        avg_loss: float,

        win_rate: float,

    ):

        win_probability = (

            win_rate / 100

        )

        loss_probability = (

            1 - win_probability

        )

        return (

            avg_win * win_probability

            - avg_loss * loss_probability

        )

    # =====================================================
    # MAX DRAWDOWN
    # =====================================================

    def max_drawdown(

        self,

        equity_curve: List[float],

    ):

        if not equity_curve:

            return 0.0

        peak = equity_curve[0]

        drawdown = 0.0

        for value in equity_curve:

            peak = max(

                peak,

                value,

            )

            if peak > 0:

                dd = (

                    (peak - value)

                    / peak

                ) * 100

                drawdown = max(

                    drawdown,

                    dd,

                )

        return drawdown

    # =====================================================
    # CAGR
    # =====================================================

    def cagr(

        self,

        initial_value: float,

        final_value: float,

        years: float,

    ):

        if (

            initial_value <= 0

            or years <= 0

        ):

            return 0.0

        return (

            (

                final_value

                / initial_value

            )

            ** (1 / years)

            - 1

        ) * 100

    # =====================================================
    # SHARPE RATIO
    # =====================================================

    def sharpe_ratio(

        self,

        returns: List[float],

        risk_free_rate: float = 0.0,

    ):

        if len(

            returns

        ) < 2:

            return 0.0

        excess_returns = [

            value - risk_free_rate

            for value in returns

        ]

        std = self.std(

            excess_returns

        )

        if std == 0:

            return 0.0

        return (

            self.mean(

                excess_returns

            )

            / std

        )

    # =====================================================
    # RISK / REWARD
    # =====================================================

    def risk_reward(

        self,

        risk: float,

        reward: float,

    ):

        if risk == 0:

            return 0.0

        return reward / risk

    # =====================================================
    # PORTFOLIO RETURN
    # =====================================================

    def portfolio_return(

        self,

        initial_value: float,

        current_value: float,

    ):

        if initial_value == 0:

            return 0.0

        return (

            (

                current_value

                - initial_value

            )

            / initial_value

        ) * 100

    # =====================================================
    # VOLATILITY
    # =====================================================

    def volatility(

        self,

        returns: List[float],

    ):

        return self.std(

            returns

        )

    # =====================================================
    # CALMAR RATIO
    # =====================================================

    def calmar_ratio(

        self,

        annual_return: float,

        max_drawdown: float,

    ):

        if max_drawdown == 0:

            return 0.0

        return (

            annual_return

            / max_drawdown

        )
        # =====================================================
    # BENCHMARK COMPARISON
    # =====================================================

    def benchmark_comparison(

        self,

        portfolio_return: float,

        benchmark_return: float,

    ):

        return {

            "portfolio": portfolio_return,

            "benchmark": benchmark_return,

            "outperformance": (

                portfolio_return

                - benchmark_return

            ),

        }

    # =====================================================
    # ALPHA
    # =====================================================

    def alpha(

        self,

        portfolio_return: float,

        benchmark_return: float,

        risk_free_rate: float = 0.0,

    ):

        return (

            portfolio_return

            - risk_free_rate

            - (

                benchmark_return

                - risk_free_rate

            )

        )

    # =====================================================
    # BETA
    # =====================================================

    def beta(

        self,

        portfolio_returns: List[float],

        benchmark_returns: List[float],

    ):

        if (

            len(portfolio_returns)

            != len(benchmark_returns)

            or len(portfolio_returns) < 2

        ):

            return 0.0

        portfolio_mean = self.mean(

            portfolio_returns

        )

        benchmark_mean = self.mean(

            benchmark_returns

        )

        covariance = sum(

            (

                p - portfolio_mean

            )

            * (

                b - benchmark_mean

            )

            for p, b in zip(

                portfolio_returns,

                benchmark_returns,

            )

        ) / (

            len(

                portfolio_returns

            ) - 1

        )

        variance = self.variance(

            benchmark_returns

        )

        if variance == 0:

            return 0.0

        return covariance / variance

    # =====================================================
    # TRADE ANALYTICS
    # =====================================================

    def trade_analytics(

        self,

        trades: List[Dict],

    ):

        profits = [

            trade.get(

                "profit",

                0.0,

            )

            for trade in trades

        ]

        wins = sum(

            1

            for value in profits

            if value > 0

        )

        losses = sum(

            1

            for value in profits

            if value <= 0

        )

        gross_profit = sum(

            value

            for value in profits

            if value > 0

        )

        gross_loss = abs(

            sum(

                value

                for value in profits

                if value < 0

            )

        )

        return {

            "trades": len(

                trades

            ),

            "wins": wins,

            "losses": losses,

            "win_rate": self.win_rate(

                wins,

                losses,

            ),

            "profit_factor": self.profit_factor(

                gross_profit,

                gross_loss,

            ),

            "net_profit": sum(

                profits

            ),

        }

    # =====================================================
    # PORTFOLIO ANALYTICS
    # =====================================================

    def portfolio_analytics(

        self,

        equity_curve: List[float],

    ):

        if len(

            equity_curve

        ) < 2:

            return {}

        total_return = self.portfolio_return(

            equity_curve[0],

            equity_curve[-1],

        )

        return {

            "return": total_return,

            "drawdown": self.max_drawdown(

                equity_curve

            ),

            "volatility": self.volatility(

                equity_curve

            ),

        }

    # =====================================================
    # SCANNER ANALYTICS
    # =====================================================

    def scanner_analytics(

        self,

        scan_results: List[Dict],

    ):

        bullish = sum(

            1

            for result in scan_results

            if result.get(

                "signal",

                "",

            ).lower() == "buy"

        )

        bearish = sum(

            1

            for result in scan_results

            if result.get(

                "signal",

                "",

            ).lower() == "sell"

        )

        return {

            "total": len(

                scan_results

            ),

            "bullish": bullish,

            "bearish": bearish,

        }

    # =====================================================
    # AI ANALYTICS
    # =====================================================

    def ai_analytics(

        self,

        opportunities: List[Dict],

    ):

        if not opportunities:

            return {

                "count": 0,

                "average_score": 0.0,

                "highest_score": 0.0,

            }

        scores = [

            item.get(

                "score",

                0.0,

            )

            for item in opportunities

        ]

        return {

            "count": len(

                opportunities

            ),

            "average_score": self.mean(

                scores

            ),

            "highest_score": self.maximum(

                scores

            ),

        }

    # =====================================================
    # HEALTH
    # =====================================================

    def health(

        self,

    ):

        return {

            "records": len(

                self.records

            ),

            "categories": len(

                {

                    record.category

                    for record in self.records

                }

            ),

        }

    # =====================================================
    # STATISTICS
    # =====================================================

    def statistics(

        self,

    ):

        return {

            "records": len(

                self.records

            ),

            "categories": len(

                {

                    record.category

                    for record in self.records

                }

            ),

            "created": sum(

                len(

                    record.values

                )

                for record in self.records

            ),

        }
        # =====================================================
    # SEARCH RECORDS
    # =====================================================

    def search(

        self,

        keyword: str,

    ):

        keyword = keyword.lower()

        return [

            record

            for record in self.records

            if (

                keyword in record.name.lower()

                or keyword

                in record.category.lower()

            )

        ]

    # =====================================================
    # FILTER CATEGORY
    # =====================================================

    def filter(

        self,

        category: str,

    ):

        return [

            record

            for record in self.records

            if record.category == category

        ]

    # =====================================================
    # DELETE RECORD
    # =====================================================

    def delete(

        self,

        record_id: str,

    ):

        record = self.get(

            record_id

        )

        if record is None:

            return False

        self.records.remove(

            record

        )

        return True

    # =====================================================
    # RESET
    # =====================================================

    def reset(

        self,

    ):

        """
        Clear all analytics records.
        """

        self.records.clear()

    # =====================================================
    # STARTUP
    # =====================================================

    def startup(

        self,

    ):

        """
        Startup hook.

        Reserved for loading
        persisted analytics data.
        """

        return self.statistics()

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(

        self,

    ):

        """
        Shutdown hook.

        Reserved for persisting
        analytics records.
        """

        return {

            "records": len(

                self.records

            ),

            "categories": len(

                {

                    record.category

                    for record in self.records

                }

            ),

        }

    # =====================================================
    # EXISTS
    # =====================================================

    def exists(

        self,

        record_id: str,

    ):

        return self.get(

            record_id

        ) is not None

    # =====================================================
    # REPR
    # =====================================================

    def __repr__(

        self,

    ):

        stats = self.statistics()

        return (

            "AnalyticsManager("

            f"records={stats['records']}, "

            f"categories={stats['categories']}"

            ")"

        )

    # =====================================================
    # STR
    # =====================================================

    def __str__(

        self,

    ):

        stats = self.statistics()

        return (

            "Analytics Manager\n"

            f"Records      : {stats['records']}\n"

            f"Categories   : {stats['categories']}\n"

            f"Data Points  : {stats['created']}"

        )


# =====================================================
# GLOBAL SINGLETON
# =====================================================

analytics_manager = AnalyticsManager()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "AnalyticsRecord",

    "AnalyticsManager",

    "analytics_manager",

]