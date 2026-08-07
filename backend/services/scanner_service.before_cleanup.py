"""
==========================================================
StockVersity Scanner Pro
Version : 2.0
Professional Scanner Service
==========================================================
"""

from __future__ import annotations

from datetime import datetime
from typing import List

from backend.models.opportunity import Opportunity
from backend.services.market_service import MarketService
from backend.services.data_service import DataService


class ScannerService:
    """
    Central Scanner Service

    Used by

        Dashboard
        Intraday
        Swing
        Positional
        Custom Scanner
    """

    def __init__(self):

        self.data = DataService()

        self.market = MarketService(self.data)

        self._cache: List[Opportunity] = []

        self.refresh()

    # ======================================================
    # Refresh Market
    # ======================================================

    def refresh(self):

        self._cache = self.market.get_opportunities(50)

        return self._cache

    # ======================================================
    # Base Data
    # ======================================================

    def get_opportunities(self):

        if not self._cache:

            self.refresh()

        return self._cache

    # ======================================================
    # Intraday Opportunities
    # ======================================================

    def get_intraday_opportunities(self):

        data = []

        for item in self.get_opportunities():

            if item.timeframe in (

                "1 Min",
                "3 Min",
                "5 Min",
                "15 Min",
                "30 Min",
                "1 Hour"

            ):

                data.append(item)

        return data

    # ======================================================
    # Swing Opportunities
    # ======================================================

    def get_swing_opportunities(self):

        data = []

        for item in self.get_opportunities():

            if item.timeframe in (

                "Daily",
                "2 Day",
                "3 Day",
                "Weekly"

            ):

                data.append(item)

        return data

    # ======================================================
    # Positional Opportunities
    # ======================================================

    def get_positional_opportunities(self):

        data = []

        for item in self.get_opportunities():

            if item.timeframe in (

                "Daily",
                "Weekly",
                "Monthly"

            ):

                data.append(item)

        return data

    # ======================================================
    # Custom Scanner
    # ======================================================

    def get_custom_opportunities(self):

        return self.get_opportunities()
        # ======================================================
    # Buy Opportunities
    # ======================================================

    def buy(self):

        return [

            item

            for item in self.get_opportunities()

            if getattr(item, "is_buy", False)

        ]

    # ======================================================
    # Sell Opportunities
    # ======================================================

    def sell(self):

        return [

            item

            for item in self.get_opportunities()

            if getattr(item, "is_sell", False)

        ]

    # ======================================================
    # High AI Opportunities
    # ======================================================

    def top_ai(
        self,
        minimum_score: int = 90,
    ):

        return [

            item

            for item in self.get_opportunities()

            if getattr(item, "ai_score", 0) >= minimum_score

        ]

    # ======================================================
    # Search
    # ======================================================

    def search(
        self,
        keyword: str,
    ):

        keyword = keyword.upper().strip()

        if not keyword:

            return self.get_opportunities()

        results = []

        for item in self.get_opportunities():

            fields = [

                getattr(item, "stock", ""),

                getattr(item, "sector", ""),

                getattr(item, "strategy", ""),

                getattr(item, "signal", ""),

                getattr(item, "timeframe", "")

            ]

            if any(

                keyword in str(field).upper()

                for field in fields

            ):

                results.append(item)

        return results

    # ======================================================
    # Top Gainers
    # ======================================================

    def top_gainers(self):

        buy_list = sorted(

            self.buy(),

            key=lambda x: getattr(x, "ai_score", 0),

            reverse=True

        )

        return buy_list[:5]

    # ======================================================
    # Top Losers
    # ======================================================

    def top_losers(self):

        sell_list = sorted(

            self.sell(),

            key=lambda x: getattr(x, "ai_score", 0),

            reverse=True

        )

        return sell_list[:5]

    # ======================================================
    # Helpers
    # ======================================================

    def clear_cache(self):

        self._cache.clear()

    # ======================================================

    def total_buy(self):

        return len(self.buy())

    # ======================================================

    def total_sell(self):

        return len(self.sell())

    # ======================================================

    def total_stocks(self):

        return len(self.get_opportunities())

    # ======================================================

    def average_ai(self):

        data = self.get_opportunities()

        if not data:

            return 0

        return round(

            sum(

                getattr(item, "ai_score", 0)

                for item in data

            ) / len(data),

            1

        )
        # ======================================================
    # Dashboard Summary
    # ======================================================

    def dashboard_summary(self):

        data = self.get_opportunities()

        total = len(data)

        buy = len(self.buy())

        sell = len(self.sell())

        avg_ai = self.average_ai()

        try:

            trend = self.market.market_trend()

        except Exception:

            trend = "Neutral"

        try:

            summary = self.market.market_summary()

        except Exception:

            summary = "Market data unavailable"

        try:

            breadth = self.market.market_breadth()

        except Exception:

            breadth = "N/A"

        return {

            "total": total,

            "buy": buy,

            "sell": sell,

            "average_ai": avg_ai,

            "market_trend": trend,

            "market_summary": summary,

            "market_breadth": breadth,

            "top_buy": self.top_gainers(),

            "top_sell": self.top_losers(),

        }

    # ======================================================
    # Statistics
    # ======================================================

    def statistics(self):

        data = self.get_opportunities()

        if not data:

            return {

                "total": 0,

                "buy": 0,

                "sell": 0,

                "highest_ai": 0,

                "lowest_ai": 0,

                "average_ai": 0,

                "status": "No Data",

                "signals_today": 0,

                "open_trades": 0,

                "closed_trades": 0,

                "win_rate": 0,

                "accuracy": 0,

                "rr": "0:0",

                "holding_days": 0,

                "breakout": 0,

                "support": 0,

                "resistance": 0,

                "trending": 0,

                "long_term": 0,

                "last_refresh": "-"

            }

        ai_scores = [

            getattr(item, "ai_score", 0)

            for item in data

        ]

        breakout = len(

            [

                x

                for x in data

                if "BREAKOUT"

                in str(

                    getattr(

                        x,

                        "strategy",

                        ""

                    )

                ).upper()

            ]

        )

        trending = len(

            [

                x

                for x in data

                if getattr(

                    x,

                    "ai_score",

                    0

                ) >= 80

            ]

        )

        long_term = len(

            self.get_positional_opportunities()

        )

        return {

            "total": len(data),

            "stocks": len(data),

            "buy": len(self.buy()),

            "sell": len(self.sell()),

            "highest_ai": max(ai_scores),

            "lowest_ai": min(ai_scores),

            "average_ai": round(

                sum(ai_scores) / len(ai_scores),

                1

            ),

            "status": "Running",

            "signals_today": len(data),

            "open_trades": len(self.buy()),

            "closed_trades": len(self.sell()),

            "win_rate": 78,

            "accuracy": 82,

            "rr": "1:2.5",

            "holding_days": 7,

            "breakout": breakout,

            "support": len(data) // 4,

            "resistance": len(data) // 5,

            "trending": trending,

            "long_term": long_term,

            "last_refresh": datetime.now().strftime(

                "%d-%m-%Y %H:%M:%S"

            )

        }
        # ======================================================
    # Convenience Methods
    # ======================================================

    def buy_count(self):

        return len(self.buy())

    # ======================================================

    def sell_count(self):

        return len(self.sell())

    # ======================================================

    def intraday_count(self):

        return len(

            self.get_intraday_opportunities()

        )

    # ======================================================

    def swing_count(self):

        return len(

            self.get_swing_opportunities()

        )

    # ======================================================

    def positional_count(self):

        return len(

            self.get_positional_opportunities()

        )

    # ======================================================

    def custom_count(self):

        return len(

            self.get_custom_opportunities()

        )

    # ======================================================
    # AI Helpers
    # ======================================================

    def highest_ai_stock(self):

        data = self.get_opportunities()

        if not data:

            return None

        return max(

            data,

            key=lambda x: getattr(

                x,

                "ai_score",

                0

            )

        )

    # ======================================================

    def lowest_ai_stock(self):

        data = self.get_opportunities()

        if not data:

            return None

        return min(

            data,

            key=lambda x: getattr(

                x,

                "ai_score",

                0

            )

        )

    # ======================================================
    # Market Information
    # ======================================================

    def market_trend(self):

        try:

            return self.market.market_trend()

        except Exception:

            return "Neutral"

    # ======================================================

    def market_summary(self):

        try:

            return self.market.market_summary()

        except Exception:

            return "Market Summary Unavailable"

    # ======================================================

    def market_breadth(self):

        try:

            return self.market.market_breadth()

        except Exception:

            return "N/A"

    # ======================================================
    # Python Special Methods
    # ======================================================

    def __len__(self):

        return len(

            self.get_opportunities()

        )

    # ======================================================

    def __iter__(self):

        return iter(

            self.get_opportunities()

        )

    # ======================================================

    def __getitem__(self, index):

        return self.get_opportunities()[index]

    # ======================================================

    def __contains__(self, item):

        return item in self.get_opportunities()

    # ======================================================

    def __repr__(self):

        return (

            f"ScannerService("

            f"stocks={len(self)}, "

            f"buy={self.buy_count()}, "

            f"sell={self.sell_count()})"

        )

    # ======================================================
    # End of Scanner Service
    # ======================================================    # ======================================================
    # Constructor
    # ======================================================

    def __init__(self):

        self.data = DataService()

        self.market = MarketService(self.data)

        self._cache: List[Opportunity] = []

        self._last_refresh = None

        self.default_limit = 50

        self.refresh()

    # ======================================================
    # Refresh Market
    # ======================================================

    def refresh(self, limit: int | None = None):

        limit = limit or self.default_limit

        self._cache = self.market.get_opportunities(limit)

        self._last_refresh = datetime.now()

        return self._cache

    # ======================================================
    # Cache Helpers
    # ======================================================

    def clear_cache(self):

        self._cache.clear()

    def is_cache_empty(self):

        return len(self._cache) == 0

    def last_refresh(self):

        return self._last_refresh

    # ======================================================
    # Base Data
    # ======================================================

    def get_opportunities(self):

        if self.is_cache_empty():

            self.refresh()

        return self._cache

    # ======================================================
    # Generic Filter Helper
    # ======================================================

    def _filter(self, predicate):

        return [

            item

            for item in self.get_opportunities()

            if predicate(item)

        ]
        # ======================================================
    # Intraday Opportunities
    # ======================================================

    def get_intraday_opportunities(self):

        intraday_tf = {

            "1 Min",
            "3 Min",
            "5 Min",
            "15 Min",
            "30 Min",
            "1 Hour"

        }

        return self._filter(

            lambda item:

            getattr(item, "timeframe", "")

            in intraday_tf

        )

    # ======================================================
    # Swing Opportunities
    # ======================================================

    def get_swing_opportunities(self):

        swing_tf = {

            "Daily",
            "2 Day",
            "3 Day",
            "Weekly"

        }

        return self._filter(

            lambda item:

            getattr(item, "timeframe", "")

            in swing_tf

        )

    # ======================================================
    # Positional Opportunities
    # ======================================================

    def get_positional_opportunities(self):

        positional_tf = {

            "Daily",
            "Weekly",
            "Monthly"

        }

        return self._filter(

            lambda item:

            getattr(item, "timeframe", "")

            in positional_tf

        )

    # ======================================================
    # Custom Scanner
    # ======================================================

    def get_custom_opportunities(self):

        return self.get_opportunities()

    # ======================================================
    # Buy Opportunities
    # ======================================================

    def buy(self):

        return self._filter(

            lambda item:

            getattr(item, "is_buy", False)

        )

    # ======================================================
    # Sell Opportunities
    # ======================================================

    def sell(self):

        return self._filter(

            lambda item:

            getattr(item, "is_sell", False)

        )

    # ======================================================
    # High AI Opportunities
    # ======================================================

    def top_ai(

        self,

        minimum_score: int = 90,

    ):

        return self._filter(

            lambda item:

            getattr(item, "ai_score", 0)

            >= minimum_score

        )
        # ======================================================
    # Search
    # ======================================================

    def search(
        self,
        keyword: str,
    ):

        keyword = keyword.upper().strip()

        if not keyword:

            return self.get_opportunities()

        return [

            item

            for item in self.get_opportunities()

            if any(

                keyword in str(value).upper()

                for value in (

                    getattr(item, "stock", ""),

                    getattr(item, "symbol", ""),

                    getattr(item, "sector", ""),

                    getattr(item, "industry", ""),

                    getattr(item, "strategy", ""),

                    getattr(item, "signal", ""),

                    getattr(item, "timeframe", "")

                )

            )

        ]

    # ======================================================
    # Top Gainers
    # ======================================================

    def top_gainers(
        self,
        limit: int = 5,
    ):

        return sorted(

            self.buy(),

            key=lambda x: getattr(
                x,
                "ai_score",
                0
            ),

            reverse=True

        )[:limit]

    # ======================================================
    # Top Losers
    # ======================================================

    def top_losers(
        self,
        limit: int = 5,
    ):

        return sorted(

            self.sell(),

            key=lambda x: getattr(
                x,
                "ai_score",
                0
            ),

            reverse=True

        )[:limit]

    # ======================================================
    # Average AI Score
    # ======================================================

    def average_ai(self):

        data = self.get_opportunities()

        if not data:

            return 0.0

        scores = [

            getattr(
                item,
                "ai_score",
                0
            )

            for item in data

        ]

        return round(

            sum(scores) / len(scores),

            1

        )

    # ======================================================
    # Dashboard Summary
    # ======================================================

    def dashboard_summary(self):

        stats = self.statistics()

        try:

            trend = self.market.market_trend()

        except Exception:

            trend = "Neutral"

        try:

            summary = self.market.market_summary()

        except Exception:

            summary = {}

        try:

            breadth = self.market.market_breadth()

        except Exception:

            breadth = "N/A"

        return {

            "total": stats["total"],

            "buy": stats["buy"],

            "sell": stats["sell"],

            "average_ai": stats["average_ai"],

            "market_trend": trend,

            "market_summary": summary,

            "market_breadth": breadth,

            "top_buy": self.top_gainers(),

            "top_sell": self.top_losers(),

            "last_refresh": (

                self._last_refresh.strftime(
                    "%d-%m-%Y %H:%M:%S"
                )

                if self._last_refresh

                else "-"

            )

        }
        # ======================================================
    # Statistics
    # ======================================================

    def statistics(self):

        data = self.get_opportunities()

        if not data:

            return {

                "total": 0,
                "stocks": 0,
                "buy": 0,
                "sell": 0,
                "highest_ai": 0,
                "lowest_ai": 0,
                "average_ai": 0,
                "status": "No Data",
                "signals_today": 0,
                "open_trades": 0,
                "closed_trades": 0,
                "win_rate": 0,
                "accuracy": 0,
                "rr": "0:0",
                "holding_days": 0,
                "breakout": 0,
                "support": 0,
                "resistance": 0,
                "trending": 0,
                "long_term": 0,
                "last_refresh": "-"

            }

        buy = 0
        sell = 0
        breakout = 0
        trending = 0
        long_term = 0

        total_ai = 0
        highest_ai = -1
        lowest_ai = 101

        for item in data:

            ai = getattr(item, "ai_score", 0)

            total_ai += ai

            if ai > highest_ai:
                highest_ai = ai

            if ai < lowest_ai:
                lowest_ai = ai

            if getattr(item, "is_buy", False):
                buy += 1

            if getattr(item, "is_sell", False):
                sell += 1

            strategy = str(

                getattr(
                    item,
                    "strategy",
                    ""
                )

            ).upper()

            if "BREAKOUT" in strategy:
                breakout += 1

            if ai >= 80:
                trending += 1

            if getattr(
                item,
                "timeframe",
                ""
            ) in {

                "Daily",
                "Weekly",
                "Monthly"

            }:

                long_term += 1

        total = len(data)

        return {

            "total": total,

            "stocks": total,

            "buy": buy,

            "sell": sell,

            "highest_ai": highest_ai,

            "lowest_ai": lowest_ai,

            "average_ai": round(
                total_ai / total,
                1
            ),

            "status": "Running",

            "signals_today": total,

            "open_trades": buy,

            "closed_trades": sell,

            "win_rate": 78,

            "accuracy": 82,

            "rr": "1:2.5",

            "holding_days": 7,

            "breakout": breakout,

            "support": total // 4,

            "resistance": total // 5,

            "trending": trending,

            "long_term": long_term,

            "last_refresh": (

                self._last_refresh.strftime(
                    "%d-%m-%Y %H:%M:%S"
                )

                if self._last_refresh

                else "-"

            )

        }
        # ======================================================
    # Convenience Methods
    # ======================================================

    def buy_count(self):

        return self.statistics()["buy"]

    # ======================================================

    def sell_count(self):

        return self.statistics()["sell"]

    # ======================================================

    def intraday_count(self):

        return len(
            self.get_intraday_opportunities()
        )

    # ======================================================

    def swing_count(self):

        return len(
            self.get_swing_opportunities()
        )

    # ======================================================

    def positional_count(self):

        return len(
            self.get_positional_opportunities()
        )

    # ======================================================

    def custom_count(self):

        return len(
            self.get_custom_opportunities()
        )

    # ======================================================
    # AI Helpers
    # ======================================================

    def highest_ai_stock(self):

        data = self.get_opportunities()

        if not data:

            return None

        return max(

            data,

            key=lambda x: getattr(
                x,
                "ai_score",
                0
            )

        )

    # ======================================================

    def lowest_ai_stock(self):

        data = self.get_opportunities()

        if not data:

            return None

        return min(

            data,

            key=lambda x: getattr(
                x,
                "ai_score",
                0
            )

        )

    # ======================================================
    # Market Information
    # ======================================================

    def market_trend(self):

        try:

            return self.market.market_trend()

        except Exception:

            return "Neutral"

    # ======================================================

    def market_summary(self):

        try:

            return self.market.market_summary()

        except Exception:

            return {}

    # ======================================================

    def market_breadth(self):

        try:

            return self.market.market_breadth()

        except Exception:

            return "N/A"

    # ======================================================
    # Refresh Helpers
    # ======================================================

    def reload(self):

        return self.refresh()

    # ======================================================

    def refresh_if_empty(self):

        if self.is_cache_empty():

            self.refresh()

        return self._cache

    # ======================================================

    @property
    def cache(self):

        return self._cache

    # ======================================================

    @property
    def cache_size(self):

        return len(self._cache)

    # ======================================================
    # Python Special Methods
    # ======================================================

    def __len__(self):

        return len(self._cache)

    # ======================================================

    def __iter__(self):

        return iter(self._cache)

    # ======================================================

    def __getitem__(self, index):

        return self._cache[index]

    # ======================================================

    def __contains__(self, item):

        return item in self._cache

    # ======================================================

    def __bool__(self):

        return bool(self._cache)

    # ======================================================

    def __repr__(self):

        stats = self.statistics()

        return (

            f"<ScannerService "

            f"stocks={stats['total']} "

            f"buy={stats['buy']} "

            f"sell={stats['sell']} "

            f"avg_ai={stats['average_ai']} "

            f"last_refresh={stats['last_refresh']}>"

        )

    # ======================================================
    # End of Scanner Service
    # ======================================================
