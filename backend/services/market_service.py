from __future__ import annotations

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional

from backend.services.data_service import DataService
from backend.models.market_data import MarketData


class MarketService:
    """
    =====================================================
    StockVersity Scanner Pro v4.0

    High-Level Market Service

    Responsibilities
    ----------------
    • Market Status
    • Index Monitoring
    • Market Breadth
    • Sector Rotation
    • Dashboard Summary
    • AI Market Sentiment
    =====================================================
    """

    # -------------------------------------------------

    def __init__(

        self,

        data_service: DataService,

    ):

        self.data = data_service

        self.market_summary = {}

        self.market_sentiment = "NEUTRAL"

        self.market_score = 50

        self.index_cache = {}

        self.sector_cache = {}

        self.last_update = None

    # =====================================================
    # MARKET SESSION
    # =====================================================

    def market_open(self):

        return self.data.market_open()

    # -------------------------------------------------

    def market_closed(self):

        return not self.market_open()

    # -------------------------------------------------

    def current_session(self):

        now = datetime.now()

        if now.weekday() >= 5:

            return "WEEKEND"

        pre_open = now.replace(

            hour=9,

            minute=0,

            second=0,

            microsecond=0,

        )

        market_open = now.replace(

            hour=9,

            minute=15,

            second=0,

            microsecond=0,

        )

        market_close = now.replace(

            hour=15,

            minute=30,

            second=0,

            microsecond=0,

        )

        if now < pre_open:

            return "PRE_MARKET"

        if pre_open <= now < market_open:

            return "PRE_OPEN"

        if market_open <= now <= market_close:

            return "LIVE"

        return "POST_MARKET"

    # =====================================================
    # INDEX DATA
    # =====================================================

    def refresh_indices(self):

        self.data.update_indices()

        self.index_cache = dict(

            self.data.index_data

        )

        self.last_update = datetime.now()

    # -------------------------------------------------

    def index(

        self,

        symbol,

    ):

        return self.index_cache.get(

            symbol

        )

    # -------------------------------------------------

    def nifty(self):

        return self.index("^NSEI")

    # -------------------------------------------------

    def banknifty(self):

        return self.index("^NSEBANK")

    # -------------------------------------------------

    def finnifty(self):

        return self.index("^CNXFIN")

    # =====================================================
    # INDEX CHANGE
    # =====================================================

    def index_change(

        self,

        symbol,

    ):

        quote = self.index(symbol)

        if not quote:

            return 0

        return quote.get(

            "change_percent",

            0,

        )

    # -------------------------------------------------

    def nifty_change(self):

        return self.index_change(

            "^NSEI"

        )

    # -------------------------------------------------

    def banknifty_change(self):

        return self.index_change(

            "^NSEBANK"

        )

    # -------------------------------------------------

    def finnifty_change(self):

        return self.index_change(

            "^CNXFIN"

        )

    # =====================================================
    # MARKET DIRECTION
    # =====================================================

    def market_direction(self):

        nifty = self.nifty_change()

        bank = self.banknifty_change()

        score = 0

        if nifty > 0:

            score += 1

        else:

            score -= 1

        if bank > 0:

            score += 1

        else:

            score -= 1

        if score >= 2:

            return "STRONG_BULLISH"

        if score == 1:

            return "BULLISH"

        if score == -1:

            return "BEARISH"

        if score <= -2:

            return "STRONG_BEARISH"

        return "SIDEWAYS"

    # =====================================================
    # MARKET BREADTH
    # =====================================================

    def market_breadth(self):

        advances = 0

        declines = 0

        unchanged = 0

        for market in self.data.all_market_data():

            if market.change_percent > 0:

                advances += 1

            elif market.change_percent < 0:

                declines += 1

            else:

                unchanged += 1

        total = (

            advances

            + declines

            + unchanged

        )

        ratio = 0

        if declines > 0:

            ratio = round(

                advances / declines,

                2,

            )

        return {

            "advances": advances,

            "declines": declines,

            "unchanged": unchanged,

            "total": total,

            "ratio": ratio,

        }

    # =====================================================
    # MARKET HEALTH
    # =====================================================

    def healthy_market(self):

        breadth = self.market_breadth()

        return (

            breadth["ratio"] >= 1.5

            and

            self.nifty_change() > 0

        )
        # =====================================================
    # SECTOR ROTATION
    # =====================================================

    def refresh_sectors(self):

        self.sector_cache = self.data.update_sector_data()

        return self.sector_cache

    # -------------------------------------------------

    def sectors(self):

        return self.sector_cache

    # -------------------------------------------------

    def strongest_sector(self):

        if not self.sector_cache:

            self.refresh_sectors()

        if not self.sector_cache:

            return None

        return max(

            self.sector_cache.items(),

            key=lambda item: item[1].get(

                "change_percent",

                0,

            ),

        )

    # -------------------------------------------------

    def weakest_sector(self):

        if not self.sector_cache:

            self.refresh_sectors()

        if not self.sector_cache:

            return None

        return min(

            self.sector_cache.items(),

            key=lambda item: item[1].get(

                "change_percent",

                0,

            ),

        )

    # -------------------------------------------------

    def top_sectors(

        self,

        limit=5,

    ):

        sectors = sorted(

            self.sector_cache.items(),

            key=lambda item: item[1].get(

                "change_percent",

                0,

            ),

            reverse=True,

        )

        return sectors[:limit]

    # -------------------------------------------------

    def bottom_sectors(

        self,

        limit=5,

    ):

        sectors = sorted(

            self.sector_cache.items(),

            key=lambda item: item[1].get(

                "change_percent",

                0,

            ),

        )

        return sectors[:limit]

    # =====================================================
    # TOP GAINERS
    # =====================================================

    def top_gainers(

        self,

        limit=10,

    ):

        stocks = sorted(

            self.data.all_market_data(),

            key=lambda item: item.change_percent,

            reverse=True,

        )

        return stocks[:limit]

    # -------------------------------------------------

    def top_losers(

        self,

        limit=10,

    ):

        stocks = sorted(

            self.data.all_market_data(),

            key=lambda item: item.change_percent,

        )

        return stocks[:limit]

    # =====================================================
    # VOLUME LEADERS
    # =====================================================

    def volume_leaders(

        self,

        limit=10,

    ):

        stocks = sorted(

            self.data.all_market_data(),

            key=lambda item: item.volume,

            reverse=True,

        )

        return stocks[:limit]

    # -------------------------------------------------

    def relative_volume_leaders(

        self,

        limit=10,

    ):

        stocks = sorted(

            self.data.all_market_data(),

            key=lambda item: item.relative_volume,

            reverse=True,

        )

        return stocks[:limit]

    # -------------------------------------------------

    def delivery_leaders(

        self,

        limit=10,

    ):

        stocks = sorted(

            self.data.all_market_data(),

            key=lambda item: item.delivery_percent,

            reverse=True,

        )

        return stocks[:limit]

    # =====================================================
    # RELATIVE STRENGTH
    # =====================================================

    def strongest_stocks(

        self,

        limit=20,

    ):

        stocks = sorted(

            self.data.all_market_data(),

            key=lambda item: (

                item.relative_strength,

                item.ai_score,

            ),

            reverse=True,

        )

        return stocks[:limit]

    # -------------------------------------------------

    def weakest_stocks(

        self,

        limit=20,

    ):

        stocks = sorted(

            self.data.all_market_data(),

            key=lambda item: (

                item.relative_strength,

                item.ai_score,

            ),

        )

        return stocks[:limit]

    # =====================================================
    # AI MARKET SCORE
    # =====================================================

    def calculate_market_score(self):

        score = 50

        if self.nifty_change() > 0:

            score += 10

        else:

            score -= 10

        if self.banknifty_change() > 0:

            score += 10

        else:

            score -= 10

        breadth = self.market_breadth()

        if breadth["ratio"] >= 2:

            score += 20

        elif breadth["ratio"] >= 1.2:

            score += 10

        elif breadth["ratio"] <= 0.5:

            score -= 20

        elif breadth["ratio"] < 1:

            score -= 10

        strong = len(

            [

                s

                for s in self.data.all_market_data()

                if s.ai_score >= 80

            ]

        )

        score += min(

            strong,

            10,

        )

        score = max(

            0,

            min(

                score,

                100,

            ),

        )

        self.market_score = score

        return score

    # =====================================================
    # MARKET SENTIMENT
    # =====================================================

    def update_sentiment(self):

        score = self.calculate_market_score()

        if score >= 85:

            sentiment = "EXTREMELY_BULLISH"

        elif score >= 70:

            sentiment = "BULLISH"

        elif score >= 55:

            sentiment = "SLIGHTLY_BULLISH"

        elif score >= 45:

            sentiment = "NEUTRAL"

        elif score >= 30:

            sentiment = "BEARISH"

        else:

            sentiment = "EXTREMELY_BEARISH"

        self.market_sentiment = sentiment

        return sentiment

    # -------------------------------------------------

    def bullish_market(self):

        return self.market_score >= 70

    # -------------------------------------------------

    def bearish_market(self):

        return self.market_score <= 30
        # =====================================================
    # INDIA VIX
    # =====================================================

    def india_vix(self):

        quote = self.index("^INDIAVIX")

        if quote:

            return quote

        return {

            "ltp": 0,

            "change_percent": 0,

        }

    # -------------------------------------------------

    def vix_value(self):

        return self.india_vix().get(

            "ltp",

            0,

        )

    # -------------------------------------------------

    def volatility_level(self):

        vix = self.vix_value()

        if vix < 12:

            return "VERY_LOW"

        if vix < 16:

            return "LOW"

        if vix < 20:

            return "NORMAL"

        if vix < 25:

            return "HIGH"

        return "EXTREME"

    # -------------------------------------------------

    def market_risk(self):

        level = self.volatility_level()

        mapping = {

            "VERY_LOW": 10,

            "LOW": 25,

            "NORMAL": 50,

            "HIGH": 75,

            "EXTREME": 100,

        }

        return mapping[level]

    # =====================================================
    # TRADING DAYS
    # =====================================================

    def trading_day(

        self,

        day: Optional[date] = None,

    ):

        day = day or date.today()

        return day.weekday() < 5

    # -------------------------------------------------

    def next_trading_day(

        self,

        day: Optional[date] = None,

    ):

        day = day or date.today()

        while True:

            day += timedelta(days=1)

            if self.trading_day(day):

                return day

    # -------------------------------------------------

    def previous_trading_day(

        self,

        day: Optional[date] = None,

    ):

        day = day or date.today()

        while True:

            day -= timedelta(days=1)

            if self.trading_day(day):

                return day

    # =====================================================
    # MARKET TIMING
    # =====================================================

    def minutes_to_close(self):

        if not self.market_open():

            return 0

        now = datetime.now()

        close = now.replace(

            hour=15,

            minute=30,

            second=0,

            microsecond=0,

        )

        return int(

            (

                close

                - now

            ).total_seconds()

            / 60

        )

    # -------------------------------------------------

    def minutes_since_open(self):

        if not self.market_open():

            return 0

        now = datetime.now()

        open_time = now.replace(

            hour=9,

            minute=15,

            second=0,

            microsecond=0,

        )

        return int(

            (

                now

                - open_time

            ).total_seconds()

            / 60

        )

    # =====================================================
    # INTRADAY MOMENTUM
    # =====================================================

    def momentum_summary(self):

        stocks = self.data.all_market_data()

        bullish = len(

            [

                s

                for s in stocks

                if s.signal == "BUY"

            ]

        )

        bearish = len(

            [

                s

                for s in stocks

                if s.signal == "SELL"

            ]

        )

        waiting = len(stocks) - bullish - bearish

        return {

            "buy": bullish,

            "sell": bearish,

            "wait": waiting,

        }

    # =====================================================
    # DASHBOARD
    # =====================================================

    def dashboard_summary(self):

        breadth = self.market_breadth()

        return {

            "session": self.current_session(),

            "market_open": self.market_open(),

            "sentiment": self.market_sentiment,

            "score": self.market_score,

            "risk": self.market_risk(),

            "volatility": self.volatility_level(),

            "nifty": self.nifty_change(),

            "banknifty": self.banknifty_change(),

            "finnifty": self.finnifty_change(),

            "breadth": breadth,

            "symbols": len(

                self.data.all_market_data()

            ),

            "last_update": self.last_update,

        }

    # =====================================================
    # ALERTS
    # =====================================================

    def market_alerts(self):

        alerts = []

        if self.market_score >= 85:

            alerts.append(

                "Strong Bullish Market"

            )

        if self.market_score <= 20:

            alerts.append(

                "Strong Bearish Market"

            )

        if self.market_risk() >= 75:

            alerts.append(

                "High Volatility"

            )

        if self.market_breadth()["ratio"] >= 2:

            alerts.append(

                "Excellent Market Breadth"

            )

        if self.market_breadth()["ratio"] <= 0.5:

            alerts.append(

                "Weak Market Breadth"

            )

        return alerts
        # =====================================================
    # HOLIDAY UTILITIES
    # =====================================================

    def is_holiday(
        self,
        day: Optional[date] = None,
    ) -> bool:

        """
        Weekend check.
        Future versions can integrate
        official NSE holiday calendar.
        """

        day = day or date.today()

        return day.weekday() >= 5

    # -------------------------------------------------

    def trading_status(self):

        if self.is_holiday():

            return "HOLIDAY"

        if self.market_open():

            return "OPEN"

        return "CLOSED"

    # =====================================================
    # MARKET STATISTICS
    # =====================================================

    def statistics(self):

        breadth = self.market_breadth()

        return {

            "session": self.current_session(),

            "market_status": self.trading_status(),

            "market_score": self.market_score,

            "market_sentiment": self.market_sentiment,

            "market_risk": self.market_risk(),

            "volatility": self.volatility_level(),

            "symbols": len(

                self.data.all_market_data()

            ),

            "advances": breadth["advances"],

            "declines": breadth["declines"],

            "unchanged": breadth["unchanged"],

            "breadth_ratio": breadth["ratio"],

            "nifty_change": self.nifty_change(),

            "banknifty_change": self.banknifty_change(),

            "finnifty_change": self.finnifty_change(),

            "last_update": self.last_update,

        }

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh(self):

        self.refresh_indices()

        self.refresh_sectors()

        self.update_sentiment()

        self.last_update = datetime.now()

        return self.dashboard_summary()

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health(self):

        return {

            "service": "MarketService",

            "running": self.data.running,

            "session": self.current_session(),

            "market_open": self.market_open(),

            "market_status": self.trading_status(),

            "symbols": len(

                self.data.market_data

            ),

            "indices": len(

                self.index_cache

            ),

            "sectors": len(

                self.sector_cache

            ),

            "last_update": self.last_update,

        }

    # =====================================================
    # SERIALIZATION
    # =====================================================

    def to_dict(self):

        return {

            "market_score": self.market_score,

            "market_sentiment": self.market_sentiment,

            "last_update": (

                self.last_update.isoformat()

                if self.last_update

                else None

            ),

            "index_cache": self.index_cache,

            "sector_cache": self.sector_cache,

        }

    # -------------------------------------------------

    @classmethod
    def from_dict(

        cls,

        data_service,

        data,

    ):

        obj = cls(data_service)

        obj.market_score = data.get(

            "market_score",

            50,

        )

        obj.market_sentiment = data.get(

            "market_sentiment",

            "NEUTRAL",

        )

        obj.index_cache = data.get(

            "index_cache",

            {},

        )

        obj.sector_cache = data.get(

            "sector_cache",

            {},

        )

        last_update = data.get(

            "last_update"

        )

        if last_update:

            obj.last_update = datetime.fromisoformat(

                last_update

            )

        return obj

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (

            "MarketService("

            f"score={self.market_score}, "

            f"sentiment='{self.market_sentiment}', "

            f"symbols={len(self.data.market_data)})"

        )

    # -------------------------------------------------

    def __str__(self):

        return (

            f"Market Session : {self.current_session()}\n"

            f"Market Status  : {self.trading_status()}\n"

            f"Sentiment      : {self.market_sentiment}\n"

            f"Market Score   : {self.market_score}\n"

            f"Risk           : {self.market_risk()}\n"

            f"Symbols        : {len(self.data.market_data)}"

        )


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "MarketService",

]