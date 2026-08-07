"""
=========================================================
StockVersity Scanner Pro
Version 4.0
Powered by AI

Scanner Engine

Central scanning engine responsible for:

• Intraday Scanner
• Swing Scanner
• Positional Scanner
• AI Scanner
• Live Scanner
• Market Scanner

=========================================================
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from backend.ai.opportunity_engine import OpportunityEngine
from backend.services.nse_service import NseService
from backend.services.yahoo_service import YahooFinanceService


class ScannerEngine:

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self):

        self.ai = OpportunityEngine()

        self.nse = NseService()

        self.yahoo = YahooFinanceService()

        self.max_workers = 10

        self.scan_results = []

        self.last_scan = None

        self.minimum_score = 60

        self.minimum_price = 200

        self.maximum_price = None

    # =====================================================
    # SETTINGS
    # =====================================================

    def set_workers(

        self,

        workers,

    ):

        self.max_workers = max(

            1,

            workers,

        )

    def set_score(

        self,

        score,

    ):

        self.minimum_score = score

        self.ai.set_minimum_score(

            score

        )

    def set_price_filter(

        self,

        minimum=None,

        maximum=None,

    ):

        self.minimum_price = minimum

        self.maximum_price = maximum

    # =====================================================
    # DEFAULT UNIVERSE
    # =====================================================

    def default_universe(self):

        return self.ai.default_symbols()

    # =====================================================
    # MARKET STATUS
    # =====================================================

    def market_status(self):

        return self.nse.market_status()

    # =====================================================
    # MARKET SENTIMENT
    # =====================================================

    def market_sentiment(self):

        return self.ai.market_sentiment()

    # =====================================================
    # LAST SCAN
    # =====================================================

    def updated(self):

        return self.last_scan

    # =====================================================
    # PRICE FILTER
    # =====================================================

    def price_allowed(

        self,

        symbol,

    ):

        quote = self.yahoo.live_quote(

            symbol

        )

        price = quote.get(

            "price"

        )

        if price is None:

            return False

        if (

            self.minimum_price

            and

            price < self.minimum_price

        ):

            return False

        if (

            self.maximum_price

            and

            price > self.maximum_price

        ):

            return False

        return True
        # =====================================================
    # SCAN SINGLE STOCK
    # =====================================================

    def scan_stock(

        self,

        symbol,

        sector=None,

    ):

        try:

            if not self.price_allowed(symbol):

                return None

            result = self.ai.scan_stock(

                symbol,

                sector,

            )

            if result is None:

                return None

            if (

                result.get(

                    "score",

                    0,

                )

                <

                self.minimum_score

            ):

                return None

            result["scan_time"] = datetime.now()

            return result

        except Exception as e:

            return {

                "symbol": symbol,

                "error": str(e),

            }

    # =====================================================
    # INTERNAL THREAD WORKER
    # =====================================================

    def _worker(

        self,

        item,

        sector_map=None,

    ):

        if isinstance(

            item,

            tuple,

        ):

            symbol, sector = item

        else:

            symbol = item

            sector = (

                sector_map.get(symbol)

                if sector_map

                else None

            )

        return self.scan_stock(

            symbol,

            sector,

        )

    # =====================================================
    # PARALLEL SCAN
    # =====================================================

    def parallel_scan(

        self,

        symbols,

        sector_map=None,

    ):

        results = []

        with ThreadPoolExecutor(

            max_workers=self.max_workers

        ) as executor:

            futures = [

                executor.submit(

                    self._worker,

                    symbol,

                    sector_map,

                )

                for symbol in symbols

            ]

            for future in futures:

                try:

                    result = future.result()

                    if (

                        result

                        and

                        "error"

                        not in result

                    ):

                        results.append(

                            result

                        )

                except Exception:

                    continue

        self.scan_results = results

        self.last_scan = datetime.now()

        return results

    # =====================================================
    # SCAN ALL STOCKS
    # =====================================================

    def scan(

        self,

        symbols=None,

        sector_map=None,

    ):

        if symbols is None:

            symbols = self.default_universe()

        return self.parallel_scan(

            symbols,

            sector_map,

        )

    # =====================================================
    # LIVE SCAN
    # =====================================================

    def live_scan(

        self,

        symbols=None,

        sector_map=None,

    ):

        results = self.scan(

            symbols,

            sector_map,

        )

        for row in results:

            row["live"] = True

            row["updated"] = datetime.now()

        return results

    # =====================================================
    # SCAN PROGRESS
    # =====================================================

    def scan_progress(

        self,

        completed,

        total,

    ):

        if total == 0:

            return 0

        return round(

            completed

            * 100

            / total,

            2,

        )

    # =====================================================
    # CACHE
    # =====================================================

    def cache_results(

        self,

        results,

    ):

        self.scan_results = results

        self.last_scan = datetime.now()

    # =====================================================
    # GET CACHE
    # =====================================================

    def cached_results(

        self,

    ):

        return self.scan_results

    # =====================================================
    # CLEAR CACHE
    # =====================================================

    def clear_cache(

        self,

    ):

        self.scan_results = []

        self.last_scan = None
            # =====================================================
    # INTRADAY SCANNER
    # =====================================================

    def intraday_scan(

        self,

        symbols=None,

        sector_map=None,

        limit=20,

    ):

        if symbols is None:

            symbols = self.default_universe()

        opportunities = self.ai.intraday_scan(

            symbols,

            sector_map,

        )

        opportunities = [

            item

            for item in opportunities

            if item["score"] >= self.minimum_score

        ]

        opportunities.sort(

            key=lambda x: (

                x["confidence"],

                x["score"],

            ),

            reverse=True,

        )

        self.cache_results(

            opportunities

        )

        return opportunities[:limit]

    # =====================================================
    # SWING SCANNER
    # =====================================================

    def swing_scan(

        self,

        symbols=None,

        sector_map=None,

        limit=20,

    ):

        if symbols is None:

            symbols = self.default_universe()

        opportunities = self.ai.swing_scan(

            symbols,

            sector_map,

        )

        opportunities = [

            item

            for item in opportunities

            if item["score"] >= self.minimum_score

        ]

        opportunities.sort(

            key=lambda x: (

                x["stockversity_ai_score"],

                x["score"],

            ),

            reverse=True,

        )

        self.cache_results(

            opportunities

        )

        return opportunities[:limit]

    # =====================================================
    # POSITIONAL SCANNER
    # =====================================================

    def positional_scan(

        self,

        symbols=None,

        sector_map=None,

        limit=20,

    ):

        if symbols is None:

            symbols = self.default_universe()

        opportunities = self.ai.positional_scan(

            symbols,

            sector_map,

        )

        opportunities = [

            item

            for item in opportunities

            if item["score"] >= self.minimum_score

        ]

        opportunities.sort(

            key=lambda x: (

                x["stockversity_ai_score"],

                x["confidence"],

            ),

            reverse=True,

        )

        self.cache_results(

            opportunities

        )

        return opportunities[:limit]

    # =====================================================
    # AI SCANNER
    # =====================================================

    def ai_scan(

        self,

        symbols=None,

        sector_map=None,

        limit=20,

    ):

        if symbols is None:

            symbols = self.default_universe()

        opportunities = self.ai.top_ai_opportunities(

            symbols,

            sector_map,

            limit=limit,

        )

        self.cache_results(

            opportunities

        )

        return opportunities

    # =====================================================
    # BREAKOUT SCANNER
    # =====================================================

    def breakout_scan(

        self,

        symbols=None,

        sector_map=None,

        limit=20,

    ):

        if symbols is None:

            symbols = self.default_universe()

        results = []

        for symbol in symbols:

            try:

                if self.yahoo.breakout(symbol):

                    item = self.ai.scan_stock(

                        symbol,

                        sector_map.get(symbol)

                        if sector_map

                        else None,

                    )

                    if (

                        item

                        and

                        item["score"] >= self.minimum_score

                    ):

                        results.append(item)

            except Exception:

                continue

        results.sort(

            key=lambda x: (

                x["stockversity_ai_score"],

                x["score"],

            ),

            reverse=True,

        )

        self.cache_results(

            results

        )

        return results[:limit]

    # =====================================================
    # MOMENTUM SCANNER
    # =====================================================

    def momentum_scan(

        self,

        symbols=None,

        sector_map=None,

        limit=20,

    ):

        if symbols is None:

            symbols = self.default_universe()

        results = []

        for symbol in symbols:

            try:

                score = self.ai.momentum_score(

                    symbol

                )

                if score >= 70:

                    item = self.ai.scan_stock(

                        symbol,

                        sector_map.get(symbol)

                        if sector_map

                        else None,

                    )

                    if item:

                        results.append(item)

            except Exception:

                continue

        results.sort(

            key=lambda x: (

                x["score"],

                x["confidence"],

            ),

            reverse=True,

        )

        self.cache_results(

            results

        )

        return results[:limit]

    # =====================================================
    # VOLUME SCANNER
    # =====================================================

    def volume_scan(

        self,

        symbols=None,

        sector_map=None,

        limit=20,

    ):

        if symbols is None:

            symbols = self.default_universe()

        results = []

        for symbol in symbols:

            try:

                if self.yahoo.volume_breakout(

                    symbol

                ):

                    item = self.ai.scan_stock(

                        symbol,

                        sector_map.get(symbol)

                        if sector_map

                        else None,

                    )

                    if item:

                        results.append(item)

            except Exception:

                continue

        results.sort(

            key=lambda x: (

                x["confidence"],

                x["score"],

            ),

            reverse=True,

        )

        self.cache_results(

            results

        )

        return results[:limit]

    # =====================================================
    # REVERSAL SCANNER
    # =====================================================

    def reversal_scan(

        self,

        symbols=None,

        sector_map=None,

        limit=20,

    ):

        if symbols is None:

            symbols = self.default_universe()

        results = []

        for symbol in symbols:

            try:

                probability = self.ai.reversal_probability(

                    symbol

                )

                if probability >= 70:

                    item = self.ai.scan_stock(

                        symbol,

                        sector_map.get(symbol)

                        if sector_map

                        else None,

                    )

                    if item:

                        item["reversal_probability"] = probability

                        results.append(item)

            except Exception:

                continue

        results.sort(

            key=lambda x: (

                x["reversal_probability"],

                x["score"],

            ),

            reverse=True,

        )

        self.cache_results(

            results

        )

        return results[:limit]
        # =====================================================
    # OPENING RANGE BREAKOUT (ORB)
    # =====================================================

    def orb_scan(

        self,

        symbols=None,

        sector_map=None,

        limit=20,

    ):

        if symbols is None:

            symbols = self.default_universe()

        results = []

        for symbol in symbols:

            try:

                if not self.yahoo.orb_breakout(symbol):
                    continue

                item = self.ai.scan_stock(
                    symbol,
                    sector_map.get(symbol)
                    if sector_map else None,
                )

                if item:

                    item["pattern"] = "ORB"

                    results.append(item)

            except Exception:
                continue

        results.sort(

            key=lambda x: (

                x["stockversity_ai_score"],

                x["confidence"],

            ),

            reverse=True,

        )

        self.cache_results(results)

        return results[:limit]

    # =====================================================
    # VCP SCANNER
    # =====================================================

    def vcp_scan(

        self,

        symbols=None,

        sector_map=None,

        limit=20,

    ):

        if symbols is None:
            symbols = self.default_universe()

        results = []

        for symbol in symbols:

            try:

                if not self.yahoo.vcp(symbol):
                    continue

                item = self.ai.scan_stock(

                    symbol,

                    sector_map.get(symbol)

                    if sector_map else None,

                )

                if item:

                    item["pattern"] = "VCP"

                    results.append(item)

            except Exception:
                continue

        results.sort(

            key=lambda x: (

                x["stockversity_ai_score"],

                x["score"],

            ),

            reverse=True,

        )

        self.cache_results(results)

        return results[:limit]

    # =====================================================
    # BULL FLAG SCANNER
    # =====================================================

    def bull_flag_scan(

        self,

        symbols=None,

        sector_map=None,

        limit=20,

    ):

        if symbols is None:
            symbols = self.default_universe()

        results = []

        for symbol in symbols:

            try:

                if self.yahoo.bull_flag(symbol):

                    item = self.ai.scan_stock(

                        symbol,

                        sector_map.get(symbol)

                        if sector_map else None,

                    )

                    if item:

                        item["pattern"] = "Bull Flag"

                        results.append(item)

            except Exception:
                continue

        results.sort(

            key=lambda x: (

                x["stockversity_ai_score"],

                x["confidence"],

            ),

            reverse=True,

        )

        self.cache_results(results)

        return results[:limit]

    # =====================================================
    # FALLING WEDGE SCANNER
    # =====================================================

    def falling_wedge_scan(

        self,

        symbols=None,

        sector_map=None,

        limit=20,

    ):

        if symbols is None:
            symbols = self.default_universe()

        results = []

        for symbol in symbols:

            try:

                if self.yahoo.falling_wedge(symbol):

                    item = self.ai.scan_stock(

                        symbol,

                        sector_map.get(symbol)

                        if sector_map else None,

                    )

                    if item:

                        item["pattern"] = "Falling Wedge"

                        results.append(item)

            except Exception:
                continue

        results.sort(

            key=lambda x: (

                x["stockversity_ai_score"],

                x["score"],

            ),

            reverse=True,

        )

        self.cache_results(results)

        return results[:limit]

    # =====================================================
    # CUP & HANDLE SCANNER
    # =====================================================

    def cup_handle_scan(

        self,

        symbols=None,

        sector_map=None,

        limit=20,

    ):

        if symbols is None:
            symbols = self.default_universe()

        results = []

        for symbol in symbols:

            try:

                if self.yahoo.cup_handle(symbol):

                    item = self.ai.scan_stock(

                        symbol,

                        sector_map.get(symbol)

                        if sector_map else None,

                    )

                    if item:

                        item["pattern"] = "Cup & Handle"

                        results.append(item)

            except Exception:
                continue

        results.sort(

            key=lambda x: (

                x["stockversity_ai_score"],

                x["confidence"],

            ),

            reverse=True,

        )

        self.cache_results(results)

        return results[:limit]

    # =====================================================
    # 52 WEEK HIGH BREAKOUT
    # =====================================================

    def breakout_52week_scan(

        self,

        symbols=None,

        sector_map=None,

        limit=20,

    ):

        if symbols is None:
            symbols = self.default_universe()

        results = []

        for symbol in symbols:

            try:

                if self.yahoo.breakout_52week(symbol):

                    item = self.ai.scan_stock(

                        symbol,

                        sector_map.get(symbol)

                        if sector_map else None,

                    )

                    if item:

                        item["pattern"] = "52 Week Breakout"

                        results.append(item)

            except Exception:
                continue

        results.sort(

            key=lambda x: (

                x["stockversity_ai_score"],

                x["confidence"],

            ),

            reverse=True,

        )

        self.cache_results(results)

        return results[:limit]

    # =====================================================
    # RELATIVE VOLUME (RVOL)
    # =====================================================

    def rvol_scan(

        self,

        symbols=None,

        sector_map=None,

        limit=20,

    ):

        if symbols is None:
            symbols = self.default_universe()

        results = []

        for symbol in symbols:

            try:

                rvol = self.yahoo.relative_volume(symbol)

                if rvol >= 2.0:

                    item = self.ai.scan_stock(

                        symbol,

                        sector_map.get(symbol)

                        if sector_map else None,

                    )

                    if item:

                        item["rvol"] = rvol

                        results.append(item)

            except Exception:
                continue

        results.sort(

            key=lambda x: (

                x["rvol"],

                x["stockversity_ai_score"],

            ),

            reverse=True,

        )

        self.cache_results(results)

        return results[:limit]

    # =====================================================
    # MULTI TIMEFRAME TREND
    # =====================================================

    def multi_timeframe_scan(

        self,

        symbols=None,

        sector_map=None,

        limit=20,

    ):

        if symbols is None:
            symbols = self.default_universe()

        results = []

        for symbol in symbols:

            try:

                trend = self.yahoo.multi_timeframe_trend(symbol)

                if trend != "Bullish":

                    continue

                item = self.ai.scan_stock(

                    symbol,

                    sector_map.get(symbol)

                    if sector_map else None,

                )

                if item:

                    item["pattern"] = "Multi Timeframe Trend"

                    results.append(item)

            except Exception:
                continue

        results.sort(

            key=lambda x: (

                x["stockversity_ai_score"],

                x["confidence"],

            ),

            reverse=True,

        )

        self.cache_results(results)

        return results[:limit]
        # =====================================================
    # MARKET CAP FILTER
    # =====================================================

    def filter_market_cap(

        self,

        opportunities,

        minimum=1000,

        maximum=None,

    ):

        filtered = []

        for item in opportunities:

            try:

                market_cap = self.yahoo.market_cap(

                    item["symbol"]

                )

                if market_cap is None:

                    continue

                if market_cap < minimum:

                    continue

                if (

                    maximum is not None

                    and

                    market_cap > maximum

                ):

                    continue

                item["market_cap"] = market_cap

                filtered.append(item)

            except Exception:

                continue

        return filtered

    # =====================================================
    # SECTOR FILTER
    # =====================================================

    def filter_sector(

        self,

        opportunities,

        sectors,

    ):

        if not sectors:

            return opportunities

        return [

            item

            for item in opportunities

            if item.get(

                "sector"

            ) in sectors

        ]

    # =====================================================
    # F&O FILTER
    # =====================================================

    def filter_fo(

        self,

        opportunities,

    ):

        fo_symbols = set(

            self.nse.fo_symbols()

        )

        return [

            item

            for item in opportunities

            if item["symbol"] in fo_symbols

        ]

    # =====================================================
    # PRICE FILTER
    # =====================================================

    def filter_price(

        self,

        opportunities,

        minimum=None,

        maximum=None,

    ):

        filtered = []

        for item in opportunities:

            try:

                price = self.yahoo.live_quote(

                    item["symbol"]

                ).get("price")

                if price is None:

                    continue

                if (

                    minimum is not None

                    and

                    price < minimum

                ):

                    continue

                if (

                    maximum is not None

                    and

                    price > maximum

                ):

                    continue

                item["price"] = price

                filtered.append(item)

            except Exception:

                continue

        return filtered

    # =====================================================
    # VOLUME FILTER
    # =====================================================

    def filter_volume(

        self,

        opportunities,

        minimum_volume=100000,

    ):

        filtered = []

        for item in opportunities:

            try:

                volume = self.yahoo.volume(

                    item["symbol"]

                )

                if volume >= minimum_volume:

                    item["volume"] = volume

                    filtered.append(item)

            except Exception:

                continue

        return filtered

    # =====================================================
    # AI SCORE FILTER
    # =====================================================

    def filter_ai_score(

        self,

        opportunities,

        minimum=70,

    ):

        return [

            item

            for item in opportunities

            if item.get(

                "stockversity_ai_score",

                0,

            ) >= minimum

        ]

    # =====================================================
    # CONFIDENCE FILTER
    # =====================================================

    def filter_confidence(

        self,

        opportunities,

        minimum=75,

    ):

        return [

            item

            for item in opportunities

            if item.get(

                "confidence",

                0,

            ) >= minimum

        ]

    # =====================================================
    # SIGNAL FILTER
    # =====================================================

    def filter_signal(

        self,

        opportunities,

        signals,

    ):

        if isinstance(

            signals,

            str,

        ):

            signals = [

                signals

            ]

        return [

            item

            for item in opportunities

            if item.get(

                "signal"

            ) in signals

        ]

    # =====================================================
    # SORT RESULTS
    # =====================================================

    def sort_results(

        self,

        opportunities,

        field="stockversity_ai_score",

        descending=True,

    ):

        return sorted(

            opportunities,

            key=lambda x: x.get(

                field,

                0,

            ),

            reverse=descending,

        )

    # =====================================================
    # RANK RESULTS
    # =====================================================

    def rank_results(

        self,

        opportunities,

    ):

        ranked = self.sort_results(

            opportunities

        )

        for index, item in enumerate(

            ranked,

            start=1,

        ):

            item["rank"] = index

        return ranked

    # =====================================================
    # NIFTY 50 UNIVERSE
    # =====================================================

    def nifty50(

        self,

    ):

        return self.nse.nifty50_symbols()

    # =====================================================
    # NIFTY 100 UNIVERSE
    # =====================================================

    def nifty100(

        self,

    ):

        return self.nse.nifty100_symbols()

    # =====================================================
    # NIFTY 500 UNIVERSE
    # =====================================================

    def nifty500(

        self,

    ):

        return self.nse.nifty500_symbols()

    # =====================================================
    # CUSTOM UNIVERSE
    # =====================================================

    def custom_universe(

        self,

        symbols,

    ):

        return [

            s.strip().upper()

            for s in symbols

            if s

        ]
        # =====================================================
    # LIVE MARKET MONITOR
    # =====================================================

    def live_market_monitor(self):

        return {

            "market_status": self.market_status(),

            "market_sentiment": self.market_sentiment(),

            "last_updated": datetime.now(),

            "top_gainers": self.nse.top_gainers(),

            "top_losers": self.nse.top_losers(),

            "market_breadth": self.nse.market_breadth(),

        }

    # =====================================================
    # AUTO REFRESH SCAN
    # =====================================================

    def auto_refresh_scan(

        self,

        symbols=None,

        sector_map=None,

    ):

        results = self.scan(

            symbols,

            sector_map,

        )

        self.cache_results(

            results,

        )

        return {

            "scan_time": datetime.now(),

            "total": len(results),

            "results": results,

        }

    # =====================================================
    # SECTOR ROTATION
    # =====================================================

    def sector_rotation(self):

        sectors = self.nse.sector_analysis()

        ranked = sorted(

            sectors,

            key=lambda x: x.get(

                "change",

                0,

            ),

            reverse=True,

        )

        return {

            "leaders": ranked[:5],

            "laggards": ranked[-5:],

            "all": ranked,

        }

    # =====================================================
    # MARKET BREADTH ANALYSIS
    # =====================================================

    def market_breadth_analysis(self):

        breadth = self.nse.market_breadth()

        advances = breadth.get(

            "advances",

            0,

        )

        declines = breadth.get(

            "declines",

            0,

        )

        unchanged = breadth.get(

            "unchanged",

            0,

        )

        total = max(

            advances + declines + unchanged,

            1,

        )

        ratio = round(

            advances / total,

            2,

        )

        if ratio >= 0.70:

            strength = "Strong Bullish"

        elif ratio >= 0.55:

            strength = "Bullish"

        elif ratio >= 0.45:

            strength = "Neutral"

        elif ratio >= 0.30:

            strength = "Bearish"

        else:

            strength = "Strong Bearish"

        return {

            "advances": advances,

            "declines": declines,

            "unchanged": unchanged,

            "advance_ratio": ratio,

            "strength": strength,

        }

    # =====================================================
    # FII / DII SUMMARY
    # =====================================================

    def fii_dii_summary(self):

        data = self.nse.fii_dii_activity()

        fii = data.get(

            "fii",

            {},

        )

        dii = data.get(

            "dii",

            {},

        )

        return {

            "fii": fii,

            "dii": dii,

            "net_fii": fii.get(

                "net",

                0,

            ),

            "net_dii": dii.get(

                "net",

                0,

            ),

        }

    # =====================================================
    # SMART MONEY FLOW
    # =====================================================

    def smart_money_flow(self):

        summary = self.fii_dii_summary()

        fii = summary["net_fii"]

        dii = summary["net_dii"]

        total = fii + dii

        if total > 0:

            sentiment = "Bullish"

        elif total < 0:

            sentiment = "Bearish"

        else:

            sentiment = "Neutral"

        return {

            "net_flow": total,

            "sentiment": sentiment,

            "details": summary,

        }

    # =====================================================
    # MARKET ANALYTICS
    # =====================================================

    def market_analytics(self):

        return {

            "market_status":

                self.market_status(),

            "market_sentiment":

                self.market_sentiment(),

            "breadth":

                self.market_breadth_analysis(),

            "sector_rotation":

                self.sector_rotation(),

            "smart_money":

                self.smart_money_flow(),

            "top_gainers":

                self.nse.top_gainers(),

            "top_losers":

                self.nse.top_losers(),

            "last_updated":

                datetime.now(),

        }

    # =====================================================
    # DASHBOARD OVERVIEW
    # =====================================================

    def dashboard_overview(

        self,

        symbols=None,

        sector_map=None,

    ):

        if symbols is None:

            symbols = self.default_universe()

        return {

            "analytics":

                self.market_analytics(),

            "top_intraday":

                self.intraday_scan(

                    symbols,

                    sector_map,

                    limit=5,

                ),

            "top_swing":

                self.swing_scan(

                    symbols,

                    sector_map,

                    limit=5,

                ),

            "top_positional":

                self.positional_scan(

                    symbols,

                    sector_map,

                    limit=5,

                ),

            "top_ai":

                self.ai_scan(

                    symbols,

                    sector_map,

                    limit=5,

                ),

            "generated":

                datetime.now(),

        }
        # =====================================================
    # LIVE MARKET MONITOR
    # =====================================================

    def live_market_monitor(self):

        return {

            "market_status": self.market_status(),

            "market_sentiment": self.market_sentiment(),

            "last_updated": datetime.now(),

            "top_gainers": self.nse.top_gainers(),

            "top_losers": self.nse.top_losers(),

            "market_breadth": self.nse.market_breadth(),

        }

    # =====================================================
    # AUTO REFRESH SCAN
    # =====================================================

    def auto_refresh_scan(

        self,

        symbols=None,

        sector_map=None,

    ):

        results = self.scan(

            symbols,

            sector_map,

        )

        self.cache_results(

            results,

        )

        return {

            "scan_time": datetime.now(),

            "total": len(results),

            "results": results,

        }

    # =====================================================
    # SECTOR ROTATION
    # =====================================================

    def sector_rotation(self):

        sectors = self.nse.sector_analysis()

        ranked = sorted(

            sectors,

            key=lambda x: x.get(

                "change",

                0,

            ),

            reverse=True,

        )

        return {

            "leaders": ranked[:5],

            "laggards": ranked[-5:],

            "all": ranked,

        }

    # =====================================================
    # MARKET BREADTH ANALYSIS
    # =====================================================

    def market_breadth_analysis(self):

        breadth = self.nse.market_breadth()

        advances = breadth.get(

            "advances",

            0,

        )

        declines = breadth.get(

            "declines",

            0,

        )

        unchanged = breadth.get(

            "unchanged",

            0,

        )

        total = max(

            advances + declines + unchanged,

            1,

        )

        ratio = round(

            advances / total,

            2,

        )

        if ratio >= 0.70:

            strength = "Strong Bullish"

        elif ratio >= 0.55:

            strength = "Bullish"

        elif ratio >= 0.45:

            strength = "Neutral"

        elif ratio >= 0.30:

            strength = "Bearish"

        else:

            strength = "Strong Bearish"

        return {

            "advances": advances,

            "declines": declines,

            "unchanged": unchanged,

            "advance_ratio": ratio,

            "strength": strength,

        }

    # =====================================================
    # FII / DII SUMMARY
    # =====================================================

    def fii_dii_summary(self):

        data = self.nse.fii_dii_activity()

        fii = data.get(

            "fii",

            {},

        )

        dii = data.get(

            "dii",

            {},

        )

        return {

            "fii": fii,

            "dii": dii,

            "net_fii": fii.get(

                "net",

                0,

            ),

            "net_dii": dii.get(

                "net",

                0,

            ),

        }

    # =====================================================
    # SMART MONEY FLOW
    # =====================================================

    def smart_money_flow(self):

        summary = self.fii_dii_summary()

        fii = summary["net_fii"]

        dii = summary["net_dii"]

        total = fii + dii

        if total > 0:

            sentiment = "Bullish"

        elif total < 0:

            sentiment = "Bearish"

        else:

            sentiment = "Neutral"

        return {

            "net_flow": total,

            "sentiment": sentiment,

            "details": summary,

        }

    # =====================================================
    # MARKET ANALYTICS
    # =====================================================

    def market_analytics(self):

        return {

            "market_status":

                self.market_status(),

            "market_sentiment":

                self.market_sentiment(),

            "breadth":

                self.market_breadth_analysis(),

            "sector_rotation":

                self.sector_rotation(),

            "smart_money":

                self.smart_money_flow(),

            "top_gainers":

                self.nse.top_gainers(),

            "top_losers":

                self.nse.top_losers(),

            "last_updated":

                datetime.now(),

        }

    # =====================================================
    # DASHBOARD OVERVIEW
    # =====================================================

    def dashboard_overview(

        self,

        symbols=None,

        sector_map=None,

    ):

        if symbols is None:

            symbols = self.default_universe()

        return {

            "analytics":

                self.market_analytics(),

            "top_intraday":

                self.intraday_scan(

                    symbols,

                    sector_map,

                    limit=5,

                ),

            "top_swing":

                self.swing_scan(

                    symbols,

                    sector_map,

                    limit=5,

                ),

            "top_positional":

                self.positional_scan(

                    symbols,

                    sector_map,

                    limit=5,

                ),

            "top_ai":

                self.ai_scan(

                    symbols,

                    sector_map,

                    limit=5,

                ),

            "generated":

                datetime.now(),

        }
        # =====================================================
    # AI HEAT MAP
    # =====================================================

    def ai_heatmap(

        self,

        symbols=None,

        sector_map=None,

    ):

        if symbols is None:

            symbols = self.default_universe()

        heatmap = []

        for symbol in symbols:

            try:

                sector = (

                    sector_map.get(symbol)

                    if sector_map

                    else None

                )

                ai_score = self.ai.stockversity_ai_score(

                    symbol,

                    sector,

                )

                if ai_score >= 85:

                    color = "Dark Green"

                elif ai_score >= 70:

                    color = "Green"

                elif ai_score >= 55:

                    color = "Yellow"

                elif ai_score >= 40:

                    color = "Orange"

                else:

                    color = "Red"

                heatmap.append({

                    "symbol": symbol,

                    "sector": sector,

                    "score": ai_score,

                    "color": color,

                })

            except Exception:

                continue

        return sorted(

            heatmap,

            key=lambda x: x["score"],

            reverse=True,

        )

    # =====================================================
    # OPPORTUNITY RANKING ENGINE
    # =====================================================

    def opportunity_ranking(

        self,

        opportunities,

    ):

        ranked = []

        for item in opportunities:

            symbol = item["symbol"]

            sector = item.get("sector")

            ai_score = self.ai.stockversity_ai_score(

                symbol,

                sector,

            )

            item["stockversity_ai_score"] = ai_score

            ranked.append(item)

        ranked.sort(

            key=lambda x: (

                x["stockversity_ai_score"],

                x["confidence"],

                x["score"],

            ),

            reverse=True,

        )

        for index, row in enumerate(

            ranked,

            start=1,

        ):

            row["rank"] = index

        return ranked

    # =====================================================
    # RISK DASHBOARD
    # =====================================================

    def risk_dashboard(

        self,

        opportunities,

    ):

        dashboard = []

        for item in opportunities:

            symbol = item["symbol"]

            dashboard.append({

                "symbol": symbol,

                "risk":

                    self.ai.risk_category(

                        symbol,

                    ),

                "position_size":

                    self.ai.position_size(

                        symbol,

                    ),

                "rr":

                    item.get(

                        "rr",

                        0,

                    ),

                "confidence":

                    item.get(

                        "confidence",

                        0,

                    ),

            })

        return dashboard

    # =====================================================
    # SECTOR STRENGTH MATRIX
    # =====================================================

    def sector_strength_matrix(self):

        sectors = self.nse.sector_analysis()

        matrix = []

        for sector in sectors:

            score = self.nse.sector_ai_score(

                sector["sector"]

            )

            matrix.append({

                "sector":

                    sector["sector"],

                "change":

                    sector.get(

                        "change",

                        0,

                    ),

                "score":

                    score,

            })

        return sorted(

            matrix,

            key=lambda x: x["score"],

            reverse=True,

        )

    # =====================================================
    # RELATIVE STRENGTH RANKING
    # =====================================================

    def relative_strength_ranking(

        self,

        symbols,

    ):

        ranking = []

        for symbol in symbols:

            try:

                ranking.append({

                    "symbol": symbol,

                    "relative_strength":

                        self.yahoo.relative_strength(

                            symbol,

                        ),

                })

            except Exception:

                continue

        ranking.sort(

            key=lambda x: x["relative_strength"],

            reverse=True,

        )

        return ranking

    # =====================================================
    # PORTFOLIO SCANNER
    # =====================================================

    def portfolio_scan(

        self,

        symbols,

        sector_map=None,

    ):

        return self.ai.analyze_portfolio(

            symbols,

            sector_map,

        )

    # =====================================================
    # PORTFOLIO RISK ANALYZER
    # =====================================================

    def portfolio_risk(

        self,

        symbols,

    ):

        report = []

        for symbol in symbols:

            try:

                report.append({

                    "symbol": symbol,

                    "risk":

                        self.ai.risk_category(

                            symbol,

                        ),

                    "position":

                        self.ai.position_size(

                            symbol,

                        ),

                })

            except Exception:

                continue

        return report

    # =====================================================
    # AI SUMMARY
    # =====================================================

    def ai_summary(

        self,

        opportunities,

    ):

        if not opportunities:

            return {

                "message":

                    "No opportunities found."

            }

        best = max(

            opportunities,

            key=lambda x: x.get(

                "stockversity_ai_score",

                0,

            ),

        )

        return {

            "market_sentiment":

                self.market_sentiment(),

            "total_opportunities":

                len(opportunities),

            "best_stock":

                best["symbol"],

            "best_score":

                best.get(

                    "stockversity_ai_score",

                    0,

                ),

            "generated":

                datetime.now(),

        }
        # =====================================================
    # EXPORT TO CSV
    # =====================================================

    def export_csv(

        self,

        opportunities,

    ):

        import csv
        import io

        output = io.StringIO()

        writer = csv.DictWriter(

            output,

            fieldnames=[

                "symbol",

                "signal",

                "score",

                "stockversity_ai_score",

                "confidence",

                "entry",

                "stop",

                "target",

                "rr",

            ],

            extrasaction="ignore",

        )

        writer.writeheader()

        writer.writerows(

            opportunities

        )

        return output.getvalue()

    # =====================================================
    # EXPORT JSON
    # =====================================================

    def export_json(

        self,

        opportunities,

    ):

        import json

        return json.dumps(

            opportunities,

            default=str,

            indent=4,

        )

    # =====================================================
    # EXPORT EXCEL DATA
    # =====================================================

    def export_excel(

        self,

        opportunities,

    ):

        rows = []

        for item in opportunities:

            rows.append({

                "Rank":

                    item.get("rank"),

                "Symbol":

                    item.get("symbol"),

                "Signal":

                    item.get("signal"),

                "AI Score":

                    item.get(

                        "stockversity_ai_score"

                    ),

                "Score":

                    item.get("score"),

                "Confidence":

                    item.get(

                        "confidence"

                    ),

                "Entry":

                    item.get("entry"),

                "Stop":

                    item.get("stop"),

                "Target":

                    item.get("target"),

                "RR":

                    item.get("rr"),

            })

        return rows

    # =====================================================
    # SCAN STATISTICS
    # =====================================================

    def scan_statistics(

        self,

        opportunities,

    ):

        if not opportunities:

            return {

                "total": 0,

            }

        scores = [

            x.get(

                "stockversity_ai_score",

                0,

            )

            for x in opportunities

        ]

        confidence = [

            x.get(

                "confidence",

                0,

            )

            for x in opportunities

        ]

        return {

            "total":

                len(opportunities),

            "average_ai_score":

                round(

                    sum(scores)

                    / len(scores),

                    2,

                ),

            "highest_ai_score":

                max(scores),

            "lowest_ai_score":

                min(scores),

            "average_confidence":

                round(

                    sum(confidence)

                    / len(confidence),

                    2,

                ),

            "generated":

                datetime.now(),

        }

    # =====================================================
    # ENGINE DIAGNOSTICS
    # =====================================================

    def diagnostics(self):

        return {

            "scanner":

                "Running",

            "market":

                self.market_status(),

            "workers":

                self.max_workers,

            "cached_results":

                len(

                    self.scan_results

                ),

            "last_scan":

                self.last_scan,

            "minimum_score":

                self.minimum_score,

            "minimum_price":

                self.minimum_price,

        }

    # =====================================================
    # PERFORMANCE BENCHMARK
    # =====================================================

    def benchmark(

        self,

        symbols,

    ):

        start = datetime.now()

        results = self.scan(

            symbols

        )

        end = datetime.now()

        duration = (

            end - start

        ).total_seconds()

        return {

            "symbols":

                len(symbols),

            "results":

                len(results),

            "seconds":

                duration,

            "scan_per_second":

                round(

                    len(symbols)

                    / max(duration, 0.01),

                    2,

                ),

        }

    # =====================================================
    # CACHE STATUS
    # =====================================================

    def cache_status(self):

        return {

            "cached":

                len(

                    self.scan_results

                ),

            "last_scan":

                self.last_scan,

        }

    # =====================================================
    # OPTIMIZE CACHE
    # =====================================================

    def optimize_cache(

        self,

        max_items=500,

    ):

        if len(

            self.scan_results

        ) > max_items:

            self.scan_results = (

                self.scan_results[

                    :max_items

                ]

            )

    # =====================================================
    # SCAN LOG
    # =====================================================

    def scan_log(

        self,

        opportunities,

    ):

        return {

            "timestamp":

                datetime.now(),

            "market":

                self.market_sentiment(),

            "results":

                len(opportunities),

            "best_stock":

                opportunities[0]["symbol"]

                if opportunities

                else None,

        }

    # =====================================================
    # ERROR REPORT
    # =====================================================

    def error_report(

        self,

        exception,

    ):

        return {

            "time":

                datetime.now(),

            "type":

                type(exception).__name__,

            "message":

                str(exception),

        }

    # =====================================================
    # CLEANUP
    # =====================================================

    def cleanup(self):

        self.clear_cache()

        self.optimize_cache()

        return True
        # =====================================================
    # ENGINE HEALTH CHECK
    # =====================================================

    def health_check(self):

        report = {

            "scanner_engine": True,

            "ai_engine": False,

            "yahoo_service": False,

            "nse_service": False,

            "market_available": False,

            "overall": False,

        }

        try:

            report["ai_engine"] = (

                self.ai.health_check().get(

                    "overall",

                    False,

                )

            )

        except Exception:

            pass

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

            report["market_available"] = (

                self.market_status() is not None

            )

        except Exception:

            pass

        report["overall"] = all([

            report["scanner_engine"],

            report["ai_engine"],

            report["yahoo_service"],

            report["nse_service"],

            report["market_available"],

        ])

        return report

    # =====================================================
    # RESET SETTINGS
    # =====================================================

    def reset(self):

        self.clear_cache()

        self.clear_scan_history()

        self.initialize_profiles()

        self._profiles.clear()

        self.minimum_score = 60

        self.minimum_price = 200

        self.maximum_price = None

        self.max_workers = 10

        self.last_scan = None

        try:

            self.ai.reset()

        except Exception:

            pass

        try:

            self.yahoo.reset()

        except Exception:

            pass

        try:

            self.nse.reset()

        except Exception:

            pass

        return True

    # =====================================================
    # ENGINE INFORMATION
    # =====================================================

    @staticmethod
    def version():

        return {

            "application": "StockVersity Scanner Pro",

            "module": "Scanner Engine",

            "version": "4.0",

            "powered_by": "AI",

            "market": "NSE India",

        }

    # =====================================================
    # ENGINE STATISTICS
    # =====================================================

    def statistics(self):

        return {

            "last_scan": self.last_scan,

            "cached_results": len(

                self.scan_results

            ),

            "workers": self.max_workers,

            "minimum_score": self.minimum_score,

            "minimum_price": self.minimum_price,

            "market_sentiment":

                self.market_sentiment(),

            "market_status":

                self.market_status(),

        }

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(self):

        try:

            self.ai.shutdown()

        except Exception:

            pass

        try:

            self.yahoo.shutdown()

        except Exception:

            pass

        try:

            self.nse.shutdown()

        except Exception:

            pass

        self.clear_cache()

        self.clear_scan_history()

    # =====================================================
    # STRING
    # =====================================================

    def __str__(self):

        return (

            f"ScannerEngine("

            f"workers={self.max_workers}, "

            f"minimum_score={self.minimum_score}, "

            f"cached={len(self.scan_results)})"

        )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (

            f"<ScannerEngine "

            f"workers={self.max_workers} "

            f"score={self.minimum_score} "

            f"last_scan={self.last_scan}>"

        )


# =====================================================
# END OF FILE
# backend/scanner/scanner_engine.py
# =====================================================