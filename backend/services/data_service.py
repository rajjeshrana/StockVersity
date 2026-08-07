from __future__ import annotations

import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable

from backend.models.market_data import MarketData
from backend.models.scan_result import ScanResult
from database.database_manager import DatabaseManager
from backend.services.yahoo_service import YahooFinanceService
from backend.services.nse_service import NseService


logger = logging.getLogger(__name__)


class DataService:
    """
    =========================================================
    StockVersity Scanner Pro v4.0

    Central Data Layer

    Responsibilities
    ----------------
    • Live Market Data
    • Yahoo Finance
    • NSE
    • Database
    • Historical Data
    • Cache
    • Background Updates
    • Dashboard Data
    =========================================================
    """

    # -----------------------------------------------------

    def __init__(self):

        self.database = DatabaseManager()

        self.yahoo = YahooFinanceService()

        self.nse = NseService()

        # ----------------------------------------------

        self.market_data: Dict[str, MarketData] = {}

        self.index_data: Dict[str, dict] = {}

        self.sector_data: Dict[str, dict] = {}

        self.scan_results: Dict[str, ScanResult] = {}

        # ----------------------------------------------

        self.cache = {}

        self.cache_expiry = {}

        self.cache_timeout = 60

        # ----------------------------------------------

        self.callbacks: List[Callable] = []

        self.lock = threading.RLock()

        self.executor = ThreadPoolExecutor(
            max_workers=10
        )

        # ----------------------------------------------

        self.running = False

        self.refresh_interval = 30

        self.last_refresh = None

        # ----------------------------------------------

        self.stats = {

            "requests": 0,

            "cache_hits": 0,

            "cache_miss": 0,

            "errors": 0,

            "symbols": 0,

            "last_update": None,

        }

        logger.info(
            "DataService Initialized"
        )

    # =====================================================
    # CALLBACKS
    # =====================================================

    def register_callback(
        self,
        callback,
    ):

        if callback not in self.callbacks:

            self.callbacks.append(
                callback
            )

    # -----------------------------------------------------

    def unregister_callback(
        self,
        callback,
    ):

        if callback in self.callbacks:

            self.callbacks.remove(
                callback
            )

    # -----------------------------------------------------

    def notify_callbacks(self):

        for callback in self.callbacks:

            try:

                callback()

            except Exception as exc:

                logger.exception(exc)

    # =====================================================
    # SERVICE CONTROL
    # =====================================================

    def start(self):

        if self.running:

            return

        self.running = True

        threading.Thread(

            target=self._background_loop,

            daemon=True,

        ).start()

        logger.info(
            "Background Data Service Started"
        )

    # -----------------------------------------------------

    def stop(self):

        self.running = False

        self.executor.shutdown(
            wait=False
        )

        logger.info(
            "Background Data Service Stopped"
        )

    # =====================================================
    # BACKGROUND LOOP
    # =====================================================

    def _background_loop(self):

        while self.running:

            try:

                self.refresh_market()

            except Exception as exc:

                logger.exception(exc)

            time.sleep(
                self.refresh_interval
            )

    # =====================================================
    # CACHE
    # =====================================================

    def clear_cache(self):

        with self.lock:

            self.cache.clear()

            self.cache_expiry.clear()

    # -----------------------------------------------------

    def cache_size(self):

        return len(
            self.cache
        )

    # -----------------------------------------------------

    def set_cache(

        self,

        key,

        value,

        timeout=None,

    ):

        timeout = timeout or self.cache_timeout

        self.cache[key] = value

        self.cache_expiry[key] = (

            datetime.now()

            + timedelta(

                seconds=timeout

            )

        )

    # -----------------------------------------------------

    def get_cache(

        self,

        key,

    ):

        expiry = self.cache_expiry.get(
            key
        )

        if expiry is None:

            self.stats["cache_miss"] += 1

            return None

        if datetime.now() > expiry:

            self.cache.pop(
                key,
                None,
            )

            self.cache_expiry.pop(
                key,
                None,
            )

            self.stats["cache_miss"] += 1

            return None

        self.stats["cache_hits"] += 1

        return self.cache.get(
            key
        )

    # =====================================================
    # MARKET DATA
    # =====================================================

    def add_market_data(

        self,

        market_data: MarketData,

    ):

        with self.lock:

            self.market_data[
                market_data.symbol
            ] = market_data

            self.stats["symbols"] = len(
                self.market_data
            )

    # -----------------------------------------------------

    def remove_symbol(

        self,

        symbol,

    ):

        with self.lock:

            self.market_data.pop(
                symbol,
                None,
            )

    # -----------------------------------------------------

    def get_symbol(

        self,

        symbol,

    ) -> Optional[MarketData]:

        return self.market_data.get(
            symbol
        )

    # -----------------------------------------------------

    def all_symbols(self):

        return sorted(

            self.market_data.keys()

        )

    # -----------------------------------------------------

    def all_market_data(self):

        return list(

            self.market_data.values()

        )

    # =====================================================
    # SYMBOL VALIDATION
    # =====================================================

    def symbol_exists(
        self,
        symbol: str,
    ) -> bool:

        return symbol.upper() in self.market_data

    # -----------------------------------------------------

    def validate_symbol(
        self,
        symbol: str,
    ) -> bool:

        try:

            info = self.yahoo.get_quote(symbol)

            return info is not None

        except Exception:

            return False

    # =====================================================
    # LIVE DOWNLOAD
    # =====================================================

    def fetch_live_data(
        self,
        symbol: str,
        use_cache=True,
    ) -> Optional[MarketData]:

        cache_key = f"live:{symbol}"

        if use_cache:

            cached = self.get_cache(cache_key)

            if cached is not None:

                return cached

        try:

            quote = self.yahoo.get_quote(symbol)

            if quote is None:

                return None

            market = MarketData.from_symbol(symbol)

            market.company_name = quote.get("name", "")
            market.ltp = quote.get("ltp", 0)
            market.open = quote.get("open", 0)
            market.high = quote.get("high", 0)
            market.low = quote.get("low", 0)
            market.close = quote.get("close", 0)
            market.previous_close = quote.get(
                "previous_close",
                0,
            )

            market.volume = quote.get("volume", 0)

            market.average_volume = quote.get(
                "average_volume",
                0,
            )

            market.market_cap = quote.get(
                "market_cap",
                0,
            )

            market.updated_at = datetime.now()

            market.calculate_gap()
            market.calculate_day_range()

            self.add_market_data(
                market
            )

            self.set_cache(
                cache_key,
                market,
            )

            self.stats["requests"] += 1

            return market

        except Exception as exc:

            logger.exception(exc)

            self.stats["errors"] += 1

            return None

    # =====================================================
    # NSE DATA
    # =====================================================

    def fetch_nse_data(
        self,
        symbol,
    ):

        try:

            data = self.nse.quote(symbol)

            return data

        except Exception as exc:

            logger.exception(exc)

            return None

    # =====================================================
    # HISTORICAL
    # =====================================================

    def historical_data(
        self,
        symbol,
        period="6mo",
        interval="1d",
    ):

        cache_key = (
            f"history:{symbol}:{period}:{interval}"
        )

        cached = self.get_cache(
            cache_key
        )

        if cached is not None:

            return cached

        history = self.yahoo.history(

            symbol=symbol,

            period=period,

            interval=interval,

        )

        self.set_cache(
            cache_key,
            history,
            timeout=600,
        )

        return history

    # =====================================================
    # BATCH DOWNLOAD
    # =====================================================

    def download_symbols(
        self,
        symbols,
    ):

        futures = []

        for symbol in symbols:

            future = self.executor.submit(

                self.fetch_live_data,

                symbol,

            )

            futures.append(
                future
            )

        results = []

        for future in futures:

            try:

                item = future.result()

                if item:

                    results.append(
                        item
                    )

            except Exception as exc:

                logger.exception(exc)

        return results

    # =====================================================
    # RETRY
    # =====================================================

    def retry_download(
        self,
        symbol,
        retries=3,
    ):

        last_exception = None

        for _ in range(retries):

            try:

                return self.fetch_live_data(
                    symbol,
                    use_cache=False,
                )

            except Exception as exc:

                last_exception = exc

                time.sleep(1)

        if last_exception:

            logger.exception(
                last_exception
            )

        return None

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh_symbol(
        self,
        symbol,
    ):

        return self.retry_download(
            symbol
        )

    # -----------------------------------------------------

    def refresh_market(self):

        symbols = list(
            self.market_data.keys()
        )

        if not symbols:

            return

        self.download_symbols(
            symbols
        )

        self.last_refresh = datetime.now()

        self.stats[
            "last_update"
        ] = self.last_refresh

        self.notify_callbacks()

    # =====================================================
    # INDICES
    # =====================================================

    def update_indices(self):

        indices = [

            "^NSEI",

            "^NSEBANK",

            "^CNXFIN",

        ]

        for index in indices:

            try:

                quote = self.yahoo.get_quote(
                    index
                )

                self.index_data[
                    index
                ] = quote

            except Exception as exc:

                logger.exception(exc)

    # =====================================================
    # MARKET STATUS
    # =====================================================

    def market_open(self):

        now = datetime.now()

        if now.weekday() >= 5:

            return False

        start = now.replace(
            hour=9,
            minute=15,
            second=0,
            microsecond=0,
        )

        end = now.replace(
            hour=15,
            minute=30,
            second=0,
            microsecond=0,
        )

        return start <= now <= end

    # -----------------------------------------------------

    def force_refresh(self):

        self.clear_cache()

        self.refresh_market()

        self.update_indices()

    # =====================================================
    # CACHE MAINTENANCE
    # =====================================================

    def cleanup_cache(self):

        now = datetime.now()

        expired = [

            key

            for key, expiry in self.cache_expiry.items()

            if expiry < now

        ]

        for key in expired:

            self.cache.pop(
                key,
                None,
            )

            self.cache_expiry.pop(
                key,
                None,
            )

        return len(expired)

    # -----------------------------------------------------

    def cache_statistics(self):

        return {

            "items": len(self.cache),

            "hits": self.stats["cache_hits"],

            "miss": self.stats["cache_miss"],

            "requests": self.stats["requests"],

            "errors": self.stats["errors"],

        }

    # =====================================================
    # SECTOR DATA
    # =====================================================

    def update_sector_data(self):

        try:

            sectors = self.nse.sector_indices()

        except Exception:

            sectors = {}

        self.sector_data = sectors

        return sectors

    # -----------------------------------------------------

    def sector_summary(self):

        return self.sector_data

    # -----------------------------------------------------

    def strongest_sector(self):

        if not self.sector_data:

            return None

        return max(

            self.sector_data.items(),

            key=lambda item: item[1].get(
                "change_percent",
                0,
            ),

        )

    # -----------------------------------------------------

    def weakest_sector(self):

        if not self.sector_data:

            return None

        return min(

            self.sector_data.items(),

            key=lambda item: item[1].get(
                "change_percent",
                0,
            ),

        )

    # =====================================================
    # F&O
    # =====================================================

    def option_chain(
        self,
        symbol,
    ):

        try:

            return self.nse.option_chain(
                symbol
            )

        except Exception as exc:

            logger.exception(exc)

            return None

    # -----------------------------------------------------

    def futures_data(
        self,
        symbol,
    ):

        try:

            return self.nse.futures_quote(
                symbol
            )

        except Exception as exc:

            logger.exception(exc)

            return None

    # =====================================================
    # DATABASE
    # =====================================================

    def save_market_data(self):

        count = 0

        for market in self.market_data.values():

            try:

                self.database.save_market_data(
                    market
                )

                count += 1

            except Exception as exc:

                logger.exception(exc)

        return count

    # -----------------------------------------------------

    def load_market_data(self):

        try:

            items = self.database.load_market_data()

        except Exception:

            return 0

        loaded = 0

        for item in items:

            self.market_data[
                item.symbol
            ] = item

            loaded += 1

        self.stats["symbols"] = loaded

        return loaded

    # =====================================================
    # AI PREPROCESSING
    # =====================================================

    def preprocess_ai(self):

        for market in self.market_data.values():

            try:

                market.refresh_ai()

            except Exception as exc:

                logger.exception(exc)

    # =====================================================
    # DASHBOARD
    # =====================================================

    def dashboard_cards(self):

        return {

            "symbols": len(
                self.market_data
            ),

            "cache": len(
                self.cache
            ),

            "requests": self.stats[
                "requests"
            ],

            "errors": self.stats[
                "errors"
            ],

            "last_update": self.stats[
                "last_update"
            ],

            "market_open": self.market_open(),

        }

    # -----------------------------------------------------

    def dashboard_table(self):

        data = list(
            self.market_data.values()
        )

        data.sort(

            key=lambda item: item.ai_score,

            reverse=True,

        )

        return [

            item.dashboard_row()

            for item in data

        ]

    # -----------------------------------------------------

    def top_opportunities(
        self,
        limit=10,
    ):

        return sorted(

            self.market_data.values(),

            key=lambda item: item.ai_score,

            reverse=True,

        )[:limit]

    # =====================================================
    # SCAN RESULT STORAGE
    # =====================================================

    def add_scan_result(
        self,
        name,
        result: ScanResult,
    ):

        self.scan_results[name] = result

    # -----------------------------------------------------

    def get_scan_result(
        self,
        name,
    ):

        return self.scan_results.get(
            name
        )

    # -----------------------------------------------------

    def remove_scan_result(
        self,
        name,
    ):

        self.scan_results.pop(
            name,
            None,
        )

    # =====================================================
    # DIAGNOSTICS
    # =====================================================

    def statistics(self):

        return {

            **self.stats,

            "market_data": len(
                self.market_data
            ),

            "sector_data": len(
                self.sector_data
            ),

            "indices": len(
                self.index_data
            ),

            "scan_results": len(
                self.scan_results
            ),

            "cache": len(
                self.cache
            ),

        }

    # -----------------------------------------------------

    def health_check(self):

        return {

            "running": self.running,

            "market_open": self.market_open(),

            "database": self.database is not None,

            "yahoo": self.yahoo is not None,

            "nse": self.nse is not None,

            "symbols": len(
                self.market_data
            ),

            "callbacks": len(
                self.callbacks
            ),

        }

    # =====================================================
    # CLEANUP
    # =====================================================

    def shutdown(self):

        self.running = False

        try:

            self.executor.shutdown(
                wait=False
            )

        except Exception:

            pass

        self.cleanup_cache()

        logger.info(
            "DataService shutdown completed."
        )


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "DataService",

]