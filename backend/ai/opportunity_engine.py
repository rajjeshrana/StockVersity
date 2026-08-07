"""
=========================================================
StockVersity Scanner Pro
Powered by AI

AI Opportunity Engine

Generates professional trading opportunities by combining
technical indicators, market breadth, sector strength,
institutional activity and AI scoring.
=========================================================
"""

from __future__ import annotations

from datetime import datetime

from backend.services.yahoo_service import YahooFinanceService
from backend.services.nse_service import NseService


class OpportunityEngine:

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self):

        self.yahoo = YahooFinanceService()

        self.nse = NseService()

        self.minimum_score = 60

        self.maximum_results = 20

        self.last_scan = None

    # =====================================================
    # SETTINGS
    # =====================================================

    def set_minimum_score(self, score):

        self.minimum_score = max(0, min(score, 100))

    def set_maximum_results(self, count):

        self.maximum_results = max(1, count)

    # =====================================================
    # DEFAULT WATCHLIST
    # =====================================================

    def default_symbols(self):

        return [

            "RELIANCE",

            "HDFCBANK",

            "ICICIBANK",

            "SBIN",

            "LT",

            "TCS",

            "INFY",

            "AXISBANK",

            "BAJFINANCE",

            "KOTAKBANK",

            "MARUTI",

            "TITAN",

            "ULTRACEMCO",

            "SUNPHARMA",

            "BHARTIARTL",

            "ASIANPAINT",

            "ADANIENT",

            "ADANIPORTS",

            "POWERGRID",

            "NTPC",

            "HINDALCO",

            "JSWSTEEL",

            "TATASTEEL",

            "COALINDIA",

            "BEL",

            "HAL",

            "DLF",

            "LODHA",

            "INDIGO",

            "TRENT",

            "BSE",

            "CDSL",

            "MCX",

            "POLYCAB",

            "DIXON",

            "PERSISTENT",

            "LTIM",

            "OFSS",

            "ABB",

            "SIEMENS",

        ]

    # =====================================================
    # MARKET SENTIMENT
    # =====================================================

    def market_sentiment(self):

        breadth = self.nse.market_breadth()

        ratio = breadth.get(

            "advance_decline_ratio",

            1

        )

        if ratio >= 2:

            return "Strong Bullish"

        if ratio >= 1.2:

            return "Bullish"

        if ratio <= 0.5:

            return "Strong Bearish"

        if ratio <= 0.8:

            return "Bearish"

        return "Neutral"

    # =====================================================
    # MARKET FILTER
    # =====================================================

    def allow_long_trades(self):

        sentiment = self.market_sentiment()

        return sentiment in (

            "Bullish",

            "Strong Bullish",

        )

    # =====================================================
    # SHORT FILTER
    # =====================================================

    def allow_short_trades(self):

        sentiment = self.market_sentiment()

        return sentiment in (

            "Bearish",

            "Strong Bearish",

        )

    # =====================================================
    # LAST SCAN
    # =====================================================

    def updated(self):

        return self.last_scan
        # =====================================================
    # TECHNICAL SCORE
    # =====================================================

    def technical_score(self, symbol):

        analysis = self.yahoo.analyze(symbol)

        return analysis.get(

            "technical_score",

            0,

        )

    # =====================================================
    # TREND SCORE
    # =====================================================

    def trend_score(self, symbol):

        trend = self.yahoo.trend(symbol)

        mapping = {

            "Strong Bullish": 100,

            "Bullish": 80,

            "Sideways": 50,

            "Bearish": 20,

            "Strong Bearish": 0,

        }

        return mapping.get(

            trend,

            50,

        )

    # =====================================================
    # MOMENTUM SCORE
    # =====================================================

    def momentum_score(self, symbol):

        rsi = self.yahoo.rsi(symbol)

        macd = self.yahoo.macd(symbol)

        score = 0

        if rsi is not None:

            if 55 <= rsi <= 70:

                score += 50

            elif 50 <= rsi < 55:

                score += 35

            elif rsi > 70:

                score += 20

        if (

            macd

            and

            macd["macd"] >

            macd["signal"]

        ):

            score += 50

        return min(score, 100)

    # =====================================================
    # VOLUME SCORE
    # =====================================================

    def volume_score(self, symbol):

        rvol = self.yahoo.relative_volume(symbol)

        if rvol is None:

            return 0

        if rvol >= 3:

            return 100

        if rvol >= 2:

            return 80

        if rvol >= 1.5:

            return 60

        if rvol >= 1:

            return 40

        return 20

    # =====================================================
    # RISK SCORE
    # =====================================================

    def risk_score(self, symbol):

        atr = self.yahoo.atr(symbol)

        quote = self.yahoo.live_quote(symbol)

        if (

            atr is None

            or

            quote["price"] is None

        ):

            return 50

        volatility = (

            atr /

            quote["price"]

        ) * 100

        if volatility <= 1:

            return 100

        if volatility <= 2:

            return 80

        if volatility <= 3:

            return 60

        if volatility <= 5:

            return 40

        return 20

    # =====================================================
    # BREAKOUT SCORE
    # =====================================================

    def breakout_score(self, symbol):

        score = 0

        if self.yahoo.breakout(symbol):

            score += 70

        if self.yahoo.volume_breakout(symbol):

            score += 30

        return score

    # =====================================================
    # SECTOR SCORE
    # =====================================================

    def sector_score(self, sector):

        return self.nse.sector_ai_score(

            sector

        )

    # =====================================================
    # INSTITUTIONAL SCORE
    # =====================================================

    def institutional_score(self, symbol):

        return self.nse.institutional_score(

            symbol

        )

    # =====================================================
    # AI OPPORTUNITY SCORE
    # =====================================================

    def opportunity_score(

        self,

        symbol,

        sector=None,

    ):

        technical = self.technical_score(

            symbol

        )

        momentum = self.momentum_score(

            symbol

        )

        trend = self.trend_score(

            symbol

        )

        volume = self.volume_score(

            symbol

        )

        breakout = self.breakout_score(

            symbol

        )

        risk = self.risk_score(

            symbol

        )

        institutional = self.institutional_score(

            symbol

        )

        sector_strength = 70

        if sector:

            sector_strength = self.sector_score(

                sector

            )

        score = (

            technical * 0.25 +

            momentum * 0.15 +

            trend * 0.15 +

            volume * 0.10 +

            breakout * 0.10 +

            institutional * 0.10 +

            sector_strength * 0.10 +

            risk * 0.05

        )

        return round(score, 2)
        # =====================================================
    # SIGNAL
    # =====================================================

    def signal(self, symbol):

        analysis = self.yahoo.analyze(symbol)

        score = analysis.get(

            "technical_score",

            0

        )

        trend = analysis.get(

            "trend",

            "Sideways"

        )

        breakout = analysis.get(

            "breakout",

            False

        )

        if (

            score >= 80

            and breakout

            and "Bullish" in trend

        ):

            return "STRONG BUY"

        if (

            score >= 65

            and "Bullish" in trend

        ):

            return "BUY"

        if (

            score <= 35

            and "Bearish" in trend

        ):

            return "SELL"

        if (

            score <= 20

        ):

            return "STRONG SELL"

        return "HOLD"

    # =====================================================
    # CONFIDENCE
    # =====================================================

    def confidence(self, symbol):

        score = self.opportunity_score(symbol)

        if score >= 90:

            return "Very High"

        if score >= 80:

            return "High"

        if score >= 70:

            return "Medium"

        if score >= 60:

            return "Low"

        return "Very Low"

    # =====================================================
    # AI REASONING
    # =====================================================

    def ai_reason(self, symbol):

        analysis = self.yahoo.analyze(symbol)

        reasons = []

        if analysis["breakout"]:

            reasons.append(

                "Price breakout detected"

            )

        if analysis["volume_breakout"]:

            reasons.append(

                "High relative volume"

            )
    # =====================================================
    # BUY / SELL SIGNAL
    # =====================================================

    def trading_signal(

        self,

        symbol,

        sector=None,

    ):

        score = self.opportunity_score(

            symbol,

            sector,

        )

        trend = self.yahoo.trend(symbol)

        breakout = self.yahoo.breakout(symbol)

        volume = self.yahoo.volume_breakout(symbol)

        sentiment = self.market_sentiment()

        if (

            score >= 85

            and breakout

            and volume

            and trend.startswith("Strong")

            and self.allow_long_trades()

        ):

            return "STRONG BUY"

        if (

            score >= 70

            and trend in (

                "Bullish",

                "Strong Bullish",

            )

            and self.allow_long_trades()

        ):

            return "BUY"

        if (

            score <= 30

            and trend in (

                "Bearish",

                "Strong Bearish",

            )

            and self.allow_short_trades()

        ):

            return "SELL"

        return "HOLD"

    # =====================================================
    # ENTRY
    # =====================================================

    def entry_price(

        self,

        symbol,

    ):

        quote = self.yahoo.live_quote(symbol)

        return quote.get("price")

    # =====================================================
    # STOP LOSS
    # =====================================================

    def stop_loss(

        self,

        symbol,

    ):

        return self.yahoo.atr_stop_loss(symbol)

    # =====================================================
    # TARGET
    # =====================================================

    def target(

        self,

        symbol,

    ):

        return self.yahoo.atr_target(symbol)

    # =====================================================
    # RISK REWARD
    # =====================================================

    def risk_reward(

        self,

        symbol,

    ):

        entry = self.entry_price(symbol)

        stop = self.stop_loss(symbol)

        target = self.target(symbol)

        if None in (

            entry,

            stop,

            target,

        ):

            return None

        return self.yahoo.risk_reward(

            entry,

            stop,

            target,

        )

    # =====================================================
    # CONFIDENCE
    # =====================================================

    def confidence(

        self,

        symbol,

        sector=None,

    ):

        score = self.opportunity_score(

            symbol,

            sector,

        )

        signal = self.trading_signal(

            symbol,

            sector,

        )

        confidence = score

        if signal == "STRONG BUY":

            confidence += 10

        elif signal == "BUY":

            confidence += 5

        return min(

            confidence,

            100,

        )

    # =====================================================
    # AI REASONING
    # =====================================================

    def ai_reason(

        self,

        symbol,

    ):

        reasons = []

        if self.yahoo.breakout(symbol):

            reasons.append(

                "Price breakout"

            )

        if self.yahoo.volume_breakout(symbol):

            reasons.append(

                "High relative volume"

            )

        trend = self.yahoo.trend(symbol)

        if trend.startswith("Strong"):

            reasons.append(

                trend

            )

        rsi = self.yahoo.rsi(symbol)

        if (

            rsi

            and

            55 <= rsi <= 70

        ):

            reasons.append(

                "Healthy RSI"

            )

        macd = self.yahoo.macd(symbol)

        if (

            macd

            and

            macd["macd"] >

            macd["signal"]

        ):

            reasons.append(

                "MACD Bullish"

            )

        if not reasons:

            reasons.append(

                "No strong setup"

            )

        return reasons

    # =====================================================
    # SCAN STOCK
    # =====================================================

    def scan_stock(

        self,

        symbol,

        sector=None,

    ):

        analysis = self.yahoo.analyze(

            symbol

        )

        return {

            "symbol":

                symbol,

            "signal":

                self.trading_signal(

                    symbol,

                    sector,

                ),

            "score":

                self.opportunity_score(

                    symbol,

                    sector,

                ),

            "confidence":

                self.confidence(

                    symbol,

                    sector,

                ),

            "trend":

                analysis.get(

                    "trend"

                ),

            "entry":

                self.entry_price(

                    symbol,

                ),

            "stop":

                self.stop_loss(

                    symbol,

                ),

            "target":

                self.target(

                    symbol,

                ),

            "rr":

                self.risk_reward(

                    symbol,

                ),

            "reason":

                self.ai_reason(

                    symbol,

                ),

            "technical":

                analysis,

            "timestamp":

                datetime.now(),

        }
        # =====================================================
    # BATCH SCAN
    # =====================================================

    def scan_symbols(

        self,

        symbols,

        sector_map=None,

    ):

        results = []

        self.last_scan = datetime.now()

        for symbol in symbols:

            try:

                sector = None

                if sector_map:

                    sector = sector_map.get(

                        symbol

                    )

                result = self.scan_stock(

                    symbol,

                    sector,

                )

                results.append(

                    result

                )

            except Exception:

                continue

        return results

    # =====================================================
    # FILTER BY SCORE
    # =====================================================

    def filter_by_score(

        self,

        opportunities,

        minimum=None,

    ):

        if minimum is None:

            minimum = self.minimum_score

        return [

            item

            for item in opportunities

            if item["score"] >= minimum

        ]

    # =====================================================
    # FILTER BY SIGNAL
    # =====================================================

    def filter_by_signal(

        self,

        opportunities,

        signal,

    ):

        return [

            item

            for item in opportunities

            if item["signal"] == signal

        ]

    # =====================================================
    # SORT
    # =====================================================

    def rank(

        self,

        opportunities,

    ):

        return sorted(

            opportunities,

            key=lambda x: (

                x["score"],

                x["confidence"],

            ),

            reverse=True,

        )

    # =====================================================
    # TOP OPPORTUNITIES
    # =====================================================

    def top_opportunities(

        self,

        opportunities,

        limit=None,

    ):

        ranked = self.rank(

            opportunities

        )

        if limit is None:

            limit = self.maximum_results
        return ranked[:limit]

    # =====================================================
    # INTRADAY SCANNER
    # =====================================================

    def intraday_scan(

        self,

        symbols,

        sector_map=None,

    ):

        opportunities = self.scan_symbols(

            symbols,

            sector_map,

        )

        filtered = []

        for item in opportunities:

            if (

                item["signal"] in (

                    "BUY",

                    "STRONG BUY",

                )

                and

                item["score"] >= self.minimum_score

                and

                item["rr"] is not None

                and

                item["rr"] >= 2

            ):

                filtered.append(item)

        return self.top_opportunities(

            filtered

        )

    # =====================================================
    # SWING SCANNER
    # =====================================================

    def swing_scan(

        self,

        symbols,

        sector_map=None,

    ):

        opportunities = self.scan_symbols(

            symbols,

            sector_map,

        )

        filtered = []

        for item in opportunities:

            trend = item["technical"].get(

                "trend",

                ""

            )

            if (

                trend in (

                    "Bullish",

                    "Strong Bullish",

                )

                and

                item["score"] >= 70

                and

                item["confidence"] >= 75

            ):

                filtered.append(item)

        return self.top_opportunities(

            filtered

        )

    # =====================================================
    # POSITIONAL SCANNER
    # =====================================================

    def positional_scan(

        self,

        symbols,

        sector_map=None,

    ):

        opportunities = self.scan_symbols(

            symbols,

            sector_map,

        )

        filtered = []

        for item in opportunities:

            technical = item["technical"]

            trend = technical.get(

                "trend",

                ""

            )

            score = technical.get(

                "technical_score",

                0,

            )

            if (

                trend == "Strong Bullish"

                and

                score >= 80

            ):

                filtered.append(item)

        return self.top_opportunities(

            filtered

        )

    # =====================================================
    # FILTER MARKET SENTIMENT
    # =====================================================

    def filter_market(

        self,

        opportunities,

    ):

        sentiment = self.market_sentiment()

        if sentiment in (

            "Bullish",

            "Strong Bullish",

        ):

            return [

                item

                for item in opportunities

                if item["signal"] in (

                    "BUY",

                    "STRONG BUY",

                )

            ]

        if sentiment in (

            "Bearish",

            "Strong Bearish",

        ):

            return [

                item

                for item in opportunities

                if item["signal"] == "SELL"

            ]

        return opportunities

    # =====================================================
    # BEST OPPORTUNITY
    # =====================================================

    def best_opportunity(

        self,

        symbols,

        sector_map=None,

    ):

        ranked = self.rank(

            self.filter_market(

                self.scan_symbols(

                    symbols,

                    sector_map,

                )

            )

        )

        if ranked:

            return ranked[0]

        return None
        # =====================================================
    # WATCHLIST ANALYSIS
    # =====================================================

    def analyze_watchlist(

        self,

        symbols,

        sector_map=None,

    ):

        opportunities = self.scan_symbols(

            symbols,

            sector_map,

        )

        opportunities = self.rank(

            opportunities

        )

        return {

            "total_symbols": len(symbols),

            "qualified": len(

                self.filter_by_score(

                    opportunities

                )

            ),

            "buy_signals": len(

                self.filter_by_signal(

                    opportunities,

                    "BUY",

                )

            ),

            "strong_buy_signals": len(

                self.filter_by_signal(

                    opportunities,

                    "STRONG BUY",

                )

            ),

            "sell_signals": len(

                self.filter_by_signal(

                    opportunities,

                    "SELL",

                )

            ),

            "watchlist":

                opportunities,

        }

    # =====================================================
    # PORTFOLIO ANALYSIS
    # =====================================================

    def analyze_portfolio(

        self,

        holdings,

        sector_map=None,

    ):

        results = []

        total_score = 0

        for holding in holdings:

            if isinstance(

                holding,

                dict,

            ):

                symbol = holding.get(

                    "symbol"

                )

                quantity = holding.get(

                    "quantity",

                    0,

                )

            else:

                symbol = holding

                quantity = 0

            sector = None

            if sector_map:

                sector = sector_map.get(

                    symbol

                )

            analysis = self.scan_stock(

                symbol,

                sector,

            )

            analysis["quantity"] = quantity

            results.append(

                analysis

            )

            total_score += analysis["score"]

        average_score = 0

        if results:

            average_score = round(

                total_score /

                len(results),

                2,

            )

        return {

            "holdings":

                results,

            "average_score":

                average_score,

            "best_holding":

                max(

                    results,

                    key=lambda x: x["score"],

                    default=None,

                ),

            "worst_holding":

                min(

                    results,

                    key=lambda x: x["score"],

                    default=None,

                ),

        }

    # =====================================================
    # SECTOR OPPORTUNITIES
    # =====================================================

    def sector_opportunities(

        self,

        symbols,

        sector_map,

    ):

        sectors = {}

        scans = self.scan_symbols(

            symbols,

            sector_map,

        )

        for item in scans:

            sector = sector_map.get(

                item["symbol"],

                "Unknown",

            )

            sectors.setdefault(

                sector,

                []

            ).append(

                item

            )

        ranking = []

        for sector, stocks in sectors.items():

            average = round(

                sum(

                    s["score"]

                    for s in stocks

                ) /

                len(stocks),

                2,

            )

            ranking.append({

                "sector":

                    sector,

                "average_score":

                    average,

                "stocks":

                    len(stocks),

                "best_stock":

                    max(

                        stocks,

                        key=lambda x: x["score"],

                    )["symbol"],

            })

        ranking.sort(

            key=lambda x:

                x["average_score"],

            reverse=True,

        )

        return ranking

    # =====================================================
    # MARKET SUMMARY
    # =====================================================

    def market_summary(self):

        return {

            "timestamp":

                datetime.now(),

            "market_sentiment":

                self.market_sentiment(),

            "market_breadth":

                self.nse.market_breadth(),

            "nifty":

                self.nse.nifty(),

            "banknifty":

                self.nse.banknifty(),

            "top_sectors":

                self.nse.top_sectors(

                    5,

                ),

            "worst_sectors":

                self.nse.worst_sectors(

                    5,

                ),

        }

    # =====================================================
    # DASHBOARD STATISTICS
    # =====================================================

    def dashboard_statistics(

        self,

        opportunities,

    ):

        return {

            "total":

                len(opportunities),

            "strong_buy":

                len(

                    self.filter_by_signal(

                        opportunities,

                        "STRONG BUY",

                    )

                ),

            "buy":

                len(

                    self.filter_by_signal(

                        opportunities,

                        "BUY",

                    )

                ),

            "hold":

                len(

                    self.filter_by_signal(

                        opportunities,

                        "HOLD",

                    )

                ),

            "sell":

                len(

                    self.filter_by_signal(

                        opportunities,

                        "SELL",

                    )

                ),

            "average_score":

                round(

                    sum(

                        x["score"]

                        for x in opportunities

                    ) /

                    max(

                        len(opportunities),

                        1,

                    ),

                    2,

                ),

        }
        # =====================================================
    # TRADE GRADE
    # =====================================================

    def trade_grade(

        self,

        symbol,

        sector=None,

    ):

        score = self.opportunity_score(

            symbol,

            sector,

        )

        if score >= 95:
            return "A+"

        if score >= 90:
            return "A"

        if score >= 80:
            return "B+"

        if score >= 70:
            return "B"

        if score >= 60:
            return "C+"

        if score >= 50:
            return "C"

        return "D"

    # =====================================================
    # RISK CATEGORY
    # =====================================================

    def risk_category(

        self,

        symbol,

    ):

        risk = self.risk_score(

            symbol,

        )

        if risk >= 85:
            return "Very Low"

        if risk >= 70:
            return "Low"

        if risk >= 55:
            return "Moderate"

        if risk >= 35:
            return "High"

        return "Very High"

    # =====================================================
    # OPPORTUNITY TAGS
    # =====================================================

    def opportunity_tags(

        self,

        symbol,

    ):

        tags = []

        analysis = self.yahoo.analyze(

            symbol

        )

        if analysis.get("breakout"):

            tags.append(

                "Breakout"

            )

        if analysis.get("volume_breakout"):

            tags.append(

                "High Volume"

            )

        if analysis.get("trend") == "Strong Bullish":

            tags.append(

                "Trend"

            )

        rsi = analysis.get(

            "rsi"

        )

        if rsi is not None:

            if 55 <= rsi <= 70:

                tags.append(

                    "Momentum"

                )

            elif rsi > 70:

                tags.append(

                    "Overbought"

                )

            elif rsi < 35:

                tags.append(

                    "Oversold"

                )

        rr = self.risk_reward(

            symbol

        )

        if (

            rr is not None

            and

            rr >= 3

        ):

            tags.append(

                "High RR"

            )

        if not tags:

            tags.append(

                "Neutral"

            )

        return tags

    # =====================================================
    # EXPECTED HOLDING PERIOD
    # =====================================================

    def holding_period(

        self,

        symbol,

    ):

        trend = self.yahoo.trend(

            symbol

        )

        if trend == "Strong Bullish":

            return "2â€“8 Weeks"

        if trend == "Bullish":

            return "3â€“10 Days"

        if trend == "Sideways":

            return "Intraday"

        return "Avoid"

    # =====================================================
    # POSITION SIZE
    # =====================================================

    def position_size(

        self,

        symbol,

        capital,

        risk_amount,

    ):

        entry = self.entry_price(

            symbol

        )

        stop = self.stop_loss(

            symbol

        )

        if (

            entry is None

            or

            stop is None

        ):

            return 0

        return self.yahoo.position_size(

            capital,

            risk_amount,

            entry,

            stop,

        )

    # =====================================================
    # RECOMMENDATION
    # =====================================================

    def recommendation(

        self,

        symbol,

        sector=None,

    ):

        signal = self.trading_signal(

            symbol,

            sector,

        )

        score = self.opportunity_score(

            symbol,

            sector,

        )

        if (

            signal == "STRONG BUY"

            and

            score >= 85

        ):

            return "BUY NOW"

        if (

            signal == "BUY"

            and

            score >= 70

        ):

            return "BUY ON PULLBACK"

        if score >= 60:

            return "WATCH"

        if signal == "SELL":

            return "EXIT / SHORT"

        return "AVOID"

    # =====================================================
    # COMPLETE AI SUMMARY
    # =====================================================

    def ai_summary(

        self,

        symbol,

        sector=None,

        capital=None,

        risk_amount=None,

    ):

        return {

            "symbol":

                symbol,

            "signal":

                self.trading_signal(

                    symbol,

                    sector,

                ),

            "recommendation":

                self.recommendation(

                    symbol,

                    sector,

                ),

            "grade":

                self.trade_grade(

                    symbol,

                    sector,

                ),

            "score":

                self.opportunity_score(

                    symbol,

                    sector,

                ),

            "confidence":

                self.confidence(

                    symbol,

                    sector,

                ),

            "risk":

                self.risk_category(

                    symbol,

                ),

            "holding_period":

                self.holding_period(

                    symbol,

                ),

            "tags":

                self.opportunity_tags(

                    symbol,

                ),

            "entry":

                self.entry_price(

                    symbol,

                ),

            "stop":

                self.stop_loss(

                    symbol,

                ),

            "target":

                self.target(

                    symbol,

                ),

            "rr":

                self.risk_reward(

                    symbol,

                ),

            "position_size":

                self.position_size(

                    symbol,

                    capital,

                    risk_amount,

                ) if (

                    capital is not None

                    and

                    risk_amount is not None

                ) else None,

        }
        # =====================================================
    # AI QUALITY SCORE
    # =====================================================

    def quality_score(

        self,

        symbol,

        sector=None,

    ):

        score = 0

        technical = self.technical_score(symbol)
        trend = self.trend_score(symbol)
        momentum = self.momentum_score(symbol)
        risk = self.risk_score(symbol)

        score += technical * 0.40
        score += trend * 0.25
        score += momentum * 0.20
        score += risk * 0.15

        return round(min(score, 100), 2)

    # =====================================================
    # SMART MONEY SCORE
    # =====================================================

    def smart_money_score(

        self,

        symbol,

    ):

        institutional = self.institutional_score(symbol)

        volume = self.volume_score(symbol)

        breakout = self.breakout_score(symbol)

        score = (

            institutional * 0.50 +

            volume * 0.30 +

            breakout * 0.20

        )

        return round(

            min(score, 100),

            2,

        )

    # =====================================================
    # TREND CONTINUATION PROBABILITY
    # =====================================================

    def trend_probability(

        self,

        symbol,

    ):

        trend = self.yahoo.trend(symbol)

        rsi = self.yahoo.rsi(symbol)

        probability = 40

        if trend == "Strong Bullish":

            probability += 35

        elif trend == "Bullish":

            probability += 20

        if rsi is not None:

            if 55 <= rsi <= 70:

                probability += 20

            elif 50 <= rsi < 55:

                probability += 10

        if self.yahoo.volume_breakout(symbol):

            probability += 10

        return min(

            probability,

            100,

        )

    # =====================================================
    # BREAKOUT PROBABILITY
    # =====================================================

    def breakout_probability(

        self,

        symbol,

    ):

        probability = 0

        if self.yahoo.breakout(symbol):

            probability += 50

        if self.yahoo.volume_breakout(symbol):

            probability += 25

        macd = self.yahoo.macd(symbol)

        if (

            macd

            and

            macd["macd"] >

            macd["signal"]

        ):

            probability += 15

        rsi = self.yahoo.rsi(symbol)

        if (

            rsi

            and

            55 <= rsi <= 70

        ):

            probability += 10

        return min(

            probability,

            100,

        )

    # =====================================================
    # REVERSAL PROBABILITY
    # =====================================================

    def reversal_probability(

        self,

        symbol,

    ):

        probability = 0

        rsi = self.yahoo.rsi(symbol)

        trend = self.yahoo.trend(symbol)

        if (

            trend == "Bearish"

            and

            rsi is not None

            and

            rsi < 35

        ):

            probability = 80

        elif (

            trend == "Strong Bearish"

            and

            rsi is not None

            and

            rsi < 30

        ):

            probability = 90

        elif (

            trend == "Sideways"

        ):

            probability = 40

        return probability

    # =====================================================
    # SECTOR LEADERSHIP SCORE
    # =====================================================

    def sector_leadership_score(

        self,

        sector,

    ):

        if not sector:

            return 50

        return self.nse.sector_ai_score(

            sector

        )

    # =====================================================
    # MARKET STRENGTH SCORE
    # =====================================================

    def market_strength_score(self):

        sentiment = self.market_sentiment()

        mapping = {

            "Strong Bullish": 100,

            "Bullish": 80,

            "Neutral": 60,

            "Bearish": 40,

            "Strong Bearish": 20,

        }

        return mapping.get(

            sentiment,

            60,

        )

    # =====================================================
    # STOCKVERSITY AI SCORE
    # =====================================================

    def stockversity_ai_score(

        self,

        symbol,

        sector=None,

    ):

        score = (

            self.quality_score(

                symbol,

                sector,

            ) * 0.30 +

            self.smart_money_score(

                symbol,

            ) * 0.20 +

            self.trend_probability(

                symbol,

            ) * 0.15 +

            self.breakout_probability(

                symbol,

            ) * 0.10 +

            self.sector_leadership_score(

                sector,

            ) * 0.10 +

            self.market_strength_score() * 0.10 +

            self.risk_score(

                symbol,

            ) * 0.05

        )

        return round(

            min(score, 100),

            2,

        )

    # =====================================================
    # COMPLETE AI METRICS
    # =====================================================

    def ai_metrics(

        self,

        symbol,

        sector=None,

    ):

        return {

            "quality_score":

                self.quality_score(

                    symbol,

                    sector,

                ),

            "smart_money_score":

                self.smart_money_score(

                    symbol,

                ),

            "trend_probability":

                self.trend_probability(

                    symbol,

                ),

            "breakout_probability":

                self.breakout_probability(

                    symbol,

                ),

            "reversal_probability":

                self.reversal_probability(

                    symbol,

                ),

            "sector_score":

                self.sector_leadership_score(

                    sector,

                ),

            "market_strength":

                self.market_strength_score(),

            "stockversity_ai_score":

                self.stockversity_ai_score(

                    symbol,

                    sector,

                ),

        }
        # =====================================================
    # TOP AI OPPORTUNITIES
    # =====================================================

    def top_ai_opportunities(

        self,

        symbols,

        sector_map=None,

        limit=10,

    ):

        opportunities = []

        for symbol in symbols:

            try:

                sector = None

                if sector_map:

                    sector = sector_map.get(symbol)

                scan = self.scan_stock(

                    symbol,

                    sector,

                )

                scan["stockversity_ai_score"] = (

                    self.stockversity_ai_score(

                        symbol,

                        sector,

                    )

                )

                opportunities.append(scan)

            except Exception:

                continue

        opportunities.sort(

            key=lambda x: (

                x["stockversity_ai_score"],

                x["confidence"],

                x["score"],

            ),

            reverse=True,

        )

        return opportunities[:limit]

    # =====================================================
    # BEST INTRADAY PICKS
    # =====================================================

    def best_intraday(

        self,

        symbols,

        sector_map=None,

        limit=5,

    ):

        picks = []

        for item in self.intraday_scan(

            symbols,

            sector_map,

        ):

            item["stockversity_ai_score"] = (

                self.stockversity_ai_score(

                    item["symbol"],

                    sector_map.get(item["symbol"])

                    if sector_map else None,

                )

            )

            picks.append(item)

        picks.sort(

            key=lambda x: x["stockversity_ai_score"],

            reverse=True,

        )

        return picks[:limit]

    # =====================================================
    # BEST SWING PICKS
    # =====================================================

    def best_swing(

        self,

        symbols,

        sector_map=None,

        limit=5,

    ):

        picks = []

        for item in self.swing_scan(

            symbols,

            sector_map,

        ):

            item["stockversity_ai_score"] = (

                self.stockversity_ai_score(

                    item["symbol"],

                    sector_map.get(item["symbol"])

                    if sector_map else None,

                )

            )

            picks.append(item)

        picks.sort(

            key=lambda x: x["stockversity_ai_score"],

            reverse=True,

        )

        return picks[:limit]

    # =====================================================
    # BEST POSITIONAL PICKS
    # =====================================================

    def best_positional(

        self,

        symbols,

        sector_map=None,

        limit=5,

    ):

        picks = []

        for item in self.positional_scan(

            symbols,

            sector_map,

        ):

            item["stockversity_ai_score"] = (

                self.stockversity_ai_score(

                    item["symbol"],

                    sector_map.get(item["symbol"])

                    if sector_map else None,

                )

            )

            picks.append(item)

        picks.sort(

            key=lambda x: x["stockversity_ai_score"],

            reverse=True,

        )

        return picks[:limit]

    # =====================================================
    # MARKET LEADER
    # =====================================================

    def market_leader(

        self,

        symbols,

        sector_map=None,

    ):

        leaders = self.top_ai_opportunities(

            symbols,

            sector_map,

            limit=1,

        )

        return leaders[0] if leaders else None

    # =====================================================
    # SECTOR LEADERS
    # =====================================================

    def sector_leaders(

        self,

        symbols,

        sector_map,

    ):

        grouped = {}

        for item in self.scan_symbols(

            symbols,

            sector_map,

        ):

            sector = sector_map.get(

                item["symbol"],

                "Unknown",

            )

            grouped.setdefault(

                sector,

                []

            ).append(item)

        leaders = []

        for sector, stocks in grouped.items():

            best = max(

                stocks,

                key=lambda x: self.stockversity_ai_score(

                    x["symbol"],

                    sector,

                ),

            )

            leaders.append({

                "sector": sector,

                "leader": best["symbol"],

                "score": self.stockversity_ai_score(

                    best["symbol"],

                    sector,

                ),

            })

        leaders.sort(

            key=lambda x: x["score"],

            reverse=True,

        )

        return leaders

    # =====================================================
    # DASHBOARD DATA
    # =====================================================

    def dashboard_data(

        self,

        symbols,

        sector_map=None,

    ):

        return {

            "market_summary":

                self.market_summary(),

            "top_intraday":

                self.best_intraday(

                    symbols,

                    sector_map,

                ),

            "top_swing":

                self.best_swing(

                    symbols,

                    sector_map,

                ),

            "top_positional":

                self.best_positional(

                    symbols,

                    sector_map,

                ),

            "top_ai":

                self.top_ai_opportunities(

                    symbols,

                    sector_map,

                ),

            "market_leader":

                self.market_leader(

                    symbols,

                    sector_map,

                ),

            "last_scan":

                datetime.now(),

        }
        # =====================================================
    # SCORE HISTORY
    # =====================================================

    def initialize_history(self):

        if not hasattr(self, "_score_history"):

            self._score_history = {}

    # =====================================================
    # UPDATE HISTORY
    # =====================================================

    def update_history(

        self,

        symbol,

        score,

    ):

        self.initialize_history()

        history = self._score_history.setdefault(

            symbol,

            []

        )

        history.append({

            "time": datetime.now(),

            "score": score,

        })

        if len(history) > 100:

            history.pop(0)

    # =====================================================
    # GET HISTORY
    # =====================================================

    def score_history(

        self,

        symbol,

    ):

        self.initialize_history()

        return self._score_history.get(

            symbol,

            [],

        )

    # =====================================================
    # SCORE CHANGE
    # =====================================================

    def score_change(

        self,

        symbol,

    ):

        history = self.score_history(

            symbol

        )

        if len(history) < 2:

            return 0

        return round(

            history[-1]["score"]

            -

            history[-2]["score"],

            2,

        )

    # =====================================================
    # RANK CHANGE
    # =====================================================

    def rank_change(

        self,

        previous,

        current,

    ):

        previous_rank = {

            item["symbol"]: index

            for index, item

            in enumerate(previous)

        }

        changes = []

        for index, item in enumerate(current):

            old = previous_rank.get(

                item["symbol"]

            )

            if old is None:

                movement = "NEW"

            elif index < old:

                movement = "UP"

            elif index > old:

                movement = "DOWN"

            else:

                movement = "UNCHANGED"

            changes.append({

                "symbol":

                    item["symbol"],

                "movement":

                    movement,

                "current_rank":

                    index + 1,

                "previous_rank":

                    None if old is None else old + 1,

            })

        return changes

    # =====================================================
    # ALERTS
    # =====================================================

    def alerts(

        self,

        opportunities,

    ):

        alerts = []

        for item in opportunities:

            if item["signal"] == "STRONG BUY":

                alerts.append({

                    "type": "BUY",

                    "symbol": item["symbol"],

                    "message":

                        f'{item["symbol"]} generated STRONG BUY signal.',

                })

            elif item["signal"] == "SELL":

                alerts.append({

                    "type": "SELL",

                    "symbol": item["symbol"],

                    "message":

                        f'{item["symbol"]} generated SELL signal.',

                })

        return alerts

    # =====================================================
    # TRADE JOURNAL ENTRY
    # =====================================================

    def trade_journal_entry(

        self,

        opportunity,

    ):

        return {

            "date":

                datetime.now(),

            "symbol":

                opportunity["symbol"],

            "signal":

                opportunity["signal"],

            "entry":

                opportunity["entry"],

            "stop":

                opportunity["stop"],

            "target":

                opportunity["target"],

            "rr":

                opportunity["rr"],

            "confidence":

                opportunity["confidence"],

            "score":

                opportunity["score"],

            "reason":

                ", ".join(

                    opportunity["reason"]

                ),

        }

    # =====================================================
    # PERFORMANCE SUMMARY
    # =====================================================

    def performance_summary(

        self,

        opportunities,

    ):

        if not opportunities:

            return {}

        scores = [

            x["score"]

            for x in opportunities

        ]

        confidence = [

            x["confidence"]

            for x in opportunities

        ]

        return {

            "total":

                len(opportunities),

            "highest_score":

                max(scores),

            "lowest_score":

                min(scores),

            "average_score":

                round(

                    sum(scores)

                    / len(scores),

                    2,

                ),

            "average_confidence":

                round(

                    sum(confidence)

                    / len(confidence),

                    2,

                ),

        }

    # =====================================================
    # EXPORT REPORT
    # =====================================================

    def export_report(

        self,

        opportunities,

    ):

        report = []

        for item in opportunities:

            report.append({

                "Symbol":

                    item["symbol"],

                "Signal":

                    item["signal"],

                "Score":

                    item["score"],

                "Confidence":

                    item["confidence"],

                "Entry":

                    item["entry"],

                "Stop":

                    item["stop"],

                "Target":

                    item["target"],

                "RiskReward":

                    item["rr"],

            })

        return report
        # =====================================================
    # ENGINE STATISTICS
    # =====================================================

    def statistics(self):

        self.initialize_history()

        return {

            "engine": "Opportunity Engine",

            "version": "4.0",

            "last_scan": self.last_scan,

            "minimum_score": self.minimum_score,

            "maximum_results": self.maximum_results,

            "tracked_symbols": len(self._score_history),

            "market_sentiment": self.market_sentiment(),

        }

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(self):

        report = {

            "yahoo_service": False,

            "nse_service": False,

            "market_data": False,

            "overall": False,

        }

        try:

            report["yahoo_service"] = (

                self.yahoo.health_check()

            )

        except Exception:

            pass

        try:

            report["nse_service"] = (

                self.nse.health_check().get(

                    "overall",

                    False,

                )

            )

        except Exception:

            pass

        try:

            report["market_data"] = (

                self.market_summary() is not None

            )

        except Exception:

            pass

        report["overall"] = (

            report["yahoo_service"]

            and

            report["nse_service"]

            and

            report["market_data"]

        )

        return report

    # =====================================================
    # CLEAR HISTORY
    # =====================================================

    def clear_history(self):

        self.initialize_history()

        self._score_history.clear()

    # =====================================================
    # RESET ENGINE
    # =====================================================

    def reset(self):

        self.clear_history()

        self.last_scan = None

        self.minimum_score = 60

        self.maximum_results = 20

        try:

            self.yahoo.reset()

        except Exception:

            pass

        try:

            self.nse.reset()

        except Exception:

            pass

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(self):

        try:

            self.yahoo.shutdown()

        except Exception:

            pass

        try:

            self.nse.shutdown()

        except Exception:

            pass

        self.clear_history()

    # =====================================================
    # VERSION
    # =====================================================

    @staticmethod
    def version():

        return {

            "application": "StockVersity Scanner Pro",

            "engine": "Opportunity Engine",

            "version": "4.0",

            "powered_by": "AI",

            "author": "StockVersity",

        }

    # =====================================================
    # ABOUT
    # =====================================================

    @staticmethod
    def about():

        return (

            "StockVersity AI Opportunity Engine\n"

            "Professional stock ranking engine for\n"

            "Intraday, Swing and Positional trading."

        )

    # =====================================================
    # STRING
    # =====================================================

    def __str__(self):

        return (

            f"OpportunityEngine("

            f"min_score={self.minimum_score}, "

            f"max_results={self.maximum_results})"

        )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (

            f"<OpportunityEngine "

            f"score={self.minimum_score} "

            f"results={self.maximum_results} "

            f"last_scan={self.last_scan}>"

        )


# ==========================================================
# END OF FILE
# backend/ai/opportunity_engine.py
# ==========================================================
