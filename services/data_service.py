from __future__ import annotations

"""
==========================================================
StockVersity Scanner Pro
Data Service

Author  : StockVersity
Version : 1.0.0

Responsibilities
----------------
• Historical candle retrieval
• Live market data
• Batch quote retrieval
• Instrument management
• Local cache
• Watchlist data
• Scanner data source
• Multi-timeframe support
• Retry logic
• Synchronization
• Diagnostics
==========================================================
"""

import logging
import threading

from dataclasses import dataclass, field
from datetime import datetime
from datetime import timedelta
from enum import Enum
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional

from core.data_manager import DataManager
from core.upstox_client import UpstoxClient


# ==========================================================
# DATA SOURCE
# ==========================================================

class DataSource(Enum):
    """
    Market data source.
    """

    LIVE = "live"

    CACHE = "cache"

    HISTORY = "history"

    LOCAL = "local"


# ==========================================================
# DATA STATUS
# ==========================================================

class DataStatus(Enum):
    """
    Data request status.
    """

    READY = "ready"

    LOADING = "loading"

    FAILED = "failed"

    EMPTY = "empty"

    STALE = "stale"


# ==========================================================
# CACHE ENTRY
# ==========================================================

@dataclass(slots=True)
class CacheEntry:
    """
    Cache entry.
    """

    key: str

    value: Any

    source: DataSource

    created: datetime = field(
        default_factory=datetime.now
    )

    expires: Optional[datetime] = None


# ==========================================================
# DATA STATISTICS
# ==========================================================

@dataclass(slots=True)
class DataStatistics:

    quote_requests: int = 0

    historical_requests: int = 0

    cache_hits: int = 0

    cache_misses: int = 0

    live_requests: int = 0

    sync_operations: int = 0

    api_errors: int = 0


# ==========================================================
# DATA SERVICE
# ==========================================================

class DataService:
    """
    Centralized market data service.
    """

    VERSION = "1.0.0"

    CACHE_TTL = timedelta(
        seconds=15,
    )

    def __init__(
        self,
        client: UpstoxClient,
        manager: DataManager,
    ) -> None:

        self.logger = logging.getLogger(
            self.__class__.__name__
        )

        self._client = client

        self._manager = manager

        self._statistics = DataStatistics()

        self._cache: Dict[
            str,
            CacheEntry
        ] = {}

        self._callbacks: Dict[
            str,
            List[Callable[..., None]]
        ] = {}

        self._lock = threading.RLock()

        self._started = datetime.now()

        self.logger.info(
            "DataService initialized."
        )
            # ==========================================================
    # PROPERTIES
    # ==========================================================

    @property
    def client(self) -> UpstoxClient:
        """
        Return the configured Upstox client.
        """

        return self._client

    @property
    def manager(self) -> DataManager:
        """
        Return the configured data manager.
        """

        return self._manager

    @property
    def statistics(self) -> DataStatistics:
        """
        Return runtime statistics.
        """

        return self._statistics

    @property
    def uptime(self) -> timedelta:
        """
        Service uptime.
        """

        return datetime.now() - self._started

    # ==========================================================
    # EVENTS
    # ==========================================================

    def register_event(
        self,
        event: str,
        callback: Callable[..., None],
    ) -> None:
        """
        Register an event callback.
        """

        self._callbacks.setdefault(
            event,
            [],
        ).append(callback)

    def unregister_event(
        self,
        event: str,
        callback: Callable[..., None],
    ) -> None:
        """
        Remove an event callback.
        """

        callbacks = self._callbacks.get(event)

        if callbacks is None:

            return

        try:

            callbacks.remove(callback)

        except ValueError:

            pass

    def clear_events(self) -> None:
        """
        Remove every registered callback.
        """

        self._callbacks.clear()

    def _emit(
        self,
        event: str,
        **kwargs: Any,
    ) -> None:
        """
        Notify subscribers.
        """

        callbacks = self._callbacks.get(
            event,
            [],
        )

        for callback in callbacks:

            try:

                callback(**kwargs)

            except Exception:

                self.logger.exception(
                    "DataService callback failed."
                )

    # ==========================================================
    # CACHE
    # ==========================================================

    def _expired(
        self,
        entry: CacheEntry,
    ) -> bool:
        """
        Check cache expiry.
        """

        if entry.expires is None:

            return False

        return datetime.now() >= entry.expires

    def get_cache(
        self,
        key: str,
    ) -> Optional[Any]:
        """
        Return cached value.
        """

        entry = self._cache.get(key)

        if entry is None:

            self._statistics.cache_misses += 1

            return None

        if self._expired(entry):

            self._cache.pop(
                key,
                None,
            )

            self._statistics.cache_misses += 1

            return None

        self._statistics.cache_hits += 1

        return entry.value

    def set_cache(
        self,
        key: str,
        value: Any,
        source: DataSource = DataSource.CACHE,
        ttl: Optional[timedelta] = None,
    ) -> None:
        """
        Store cache entry.
        """

        expiry = None

        if ttl is not None:

            expiry = datetime.now() + ttl

        elif self.CACHE_TTL:

            expiry = datetime.now() + self.CACHE_TTL

        self._cache[key] = CacheEntry(

            key=key,

            value=value,

            source=source,

            expires=expiry,

        )

    def clear_cache(self) -> None:
        """
        Remove every cached object.
        """

        self._cache.clear()

        self.logger.info(
            "Data cache cleared."
        )

        self._emit(
            "cache_cleared",
        )

    # ==========================================================
    # QUOTES
    # ==========================================================

    def get_quote(
        self,
        instrument_key: str,
        *,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Return latest quote.
        """

        cache_key = f"QUOTE:{instrument_key}"

        if use_cache:

            cached = self.get_cache(
                cache_key,
            )

            if cached is not None:

                return cached

        self._statistics.quote_requests += 1
        self._statistics.live_requests += 1

        quote = self._client.get_quote(
            instrument_key,
        )

        self.set_cache(

            cache_key,

            quote,

            DataSource.LIVE,

        )

        self._emit(

            "quote",

            instrument_key=instrument_key,

        )

        return quote

    # ==========================================================
    # BATCH QUOTES
    # ==========================================================

    def get_quotes(
        self,
        instrument_keys: List[str],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Return quotes for multiple instruments.
        """

        quotes: Dict[str, Dict[str, Any]] = {}

        for key in instrument_keys:

            try:

                quotes[key] = self.get_quote(
                    key,
                )

            except Exception:

                self._statistics.api_errors += 1

                self.logger.exception(

                    "Failed to fetch quote for %s.",

                    key,

                )

        return quotes
        # ==========================================================
    # PROPERTIES
    # ==========================================================

    @property
    def client(self) -> UpstoxClient:
        """
        Return the configured Upstox client.
        """

        return self._client

    @property
    def manager(self) -> DataManager:
        """
        Return the configured data manager.
        """

        return self._manager

    @property
    def statistics(self) -> DataStatistics:
        """
        Return runtime statistics.
        """

        return self._statistics

    @property
    def uptime(self) -> timedelta:
        """
        Service uptime.
        """

        return datetime.now() - self._started

    # ==========================================================
    # EVENTS
    # ==========================================================

    def register_event(
        self,
        event: str,
        callback: Callable[..., None],
    ) -> None:
        """
        Register an event callback.
        """

        self._callbacks.setdefault(
            event,
            [],
        ).append(callback)

    def unregister_event(
        self,
        event: str,
        callback: Callable[..., None],
    ) -> None:
        """
        Remove an event callback.
        """

        callbacks = self._callbacks.get(event)

        if callbacks is None:

            return

        try:

            callbacks.remove(callback)

        except ValueError:

            pass

    def clear_events(self) -> None:
        """
        Remove every registered callback.
        """

        self._callbacks.clear()

    def _emit(
        self,
        event: str,
        **kwargs: Any,
    ) -> None:
        """
        Notify subscribers.
        """

        callbacks = self._callbacks.get(
            event,
            [],
        )

        for callback in callbacks:

            try:

                callback(**kwargs)

            except Exception:

                self.logger.exception(
                    "DataService callback failed."
                )

    # ==========================================================
    # CACHE
    # ==========================================================

    def _expired(
        self,
        entry: CacheEntry,
    ) -> bool:
        """
        Check cache expiry.
        """

        if entry.expires is None:

            return False

        return datetime.now() >= entry.expires

    def get_cache(
        self,
        key: str,
    ) -> Optional[Any]:
        """
        Return cached value.
        """

        entry = self._cache.get(key)

        if entry is None:

            self._statistics.cache_misses += 1

            return None

        if self._expired(entry):

            self._cache.pop(
                key,
                None,
            )

            self._statistics.cache_misses += 1

            return None

        self._statistics.cache_hits += 1

        return entry.value

    def set_cache(
        self,
        key: str,
        value: Any,
        source: DataSource = DataSource.CACHE,
        ttl: Optional[timedelta] = None,
    ) -> None:
        """
        Store cache entry.
        """

        expiry = None

        if ttl is not None:

            expiry = datetime.now() + ttl

        elif self.CACHE_TTL:

            expiry = datetime.now() + self.CACHE_TTL

        self._cache[key] = CacheEntry(

            key=key,

            value=value,

            source=source,

            expires=expiry,

        )

    def clear_cache(self) -> None:
        """
        Remove every cached object.
        """

        self._cache.clear()

        self.logger.info(
            "Data cache cleared."
        )

        self._emit(
            "cache_cleared",
        )

    # ==========================================================
    # QUOTES
    # ==========================================================

    def get_quote(
        self,
        instrument_key: str,
        *,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Return latest quote.
        """

        cache_key = f"QUOTE:{instrument_key}"

        if use_cache:

            cached = self.get_cache(
                cache_key,
            )

            if cached is not None:

                return cached

        self._statistics.quote_requests += 1
        self._statistics.live_requests += 1

        quote = self._client.get_quote(
            instrument_key,
        )

        self.set_cache(

            cache_key,

            quote,

            DataSource.LIVE,

        )

        self._emit(

            "quote",

            instrument_key=instrument_key,

        )

        return quote

    # ==========================================================
    # BATCH QUOTES
    # ==========================================================

    def get_quotes(
        self,
        instrument_keys: List[str],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Return quotes for multiple instruments.
        """

        quotes: Dict[str, Dict[str, Any]] = {}

        for key in instrument_keys:

            try:

                quotes[key] = self.get_quote(
                    key,
                )

            except Exception:

                self._statistics.api_errors += 1

                self.logger.exception(

                    "Failed to fetch quote for %s.",

                    key,

                )
    # ==========================================================
    # HISTORICAL DATA
    # ==========================================================

    def get_history(
        self,
        instrument_key: str,
        interval: str,
        from_date: Any,
        to_date: Any,
        *,
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Return historical candle data.
        """

        cache_key = (
            f"HISTORY:{instrument_key}:"
            f"{interval}:{from_date}:{to_date}"
        )

        if use_cache:

            cached = self.get_cache(
                cache_key,
            )

            if cached is not None:

                return cached

        self._statistics.historical_requests += 1
        self._statistics.live_requests += 1

        try:

            candles = self._client.get_history(

                instrument_key=instrument_key,

                interval=interval,

                from_date=from_date,

                to_date=to_date,

            )

            self.set_cache(

                cache_key,

                candles,

                DataSource.HISTORY,

                ttl=timedelta(
                    minutes=5,
                ),

            )

            self._emit(

                "history_loaded",

                instrument_key=instrument_key,

                interval=interval,

            )

            return candles

        except Exception:

            self._statistics.api_errors += 1

            self.logger.exception(
                "Historical data request failed."
            )

            raise

    # ==========================================================
    # MULTI TIMEFRAME
    # ==========================================================

    def get_multi_timeframe_history(
        self,
        instrument_key: str,
        intervals: List[str],
        from_date: Any,
        to_date: Any,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load multiple timeframes.
        """

        result: Dict[
            str,
            List[Dict[str, Any]]
        ] = {}

        for interval in intervals:

            result[interval] = self.get_history(

                instrument_key,

                interval,

                from_date,

                to_date,

            )

        return result

    # ==========================================================
    # LTP
    # ==========================================================

    def get_ltp(
        self,
        instrument_key: str,
    ) -> float:
        """
        Return Last Traded Price.
        """

        quote = self.get_quote(
            instrument_key,
        )

        if not isinstance(
            quote,
            dict,
        ):

            return 0.0

        return float(

            quote.get(

                "last_price",

                quote.get(

                    "ltp",

                    0.0,

                ),

            )

        )

    # ==========================================================
    # INSTRUMENT SEARCH
    # ==========================================================

    def search_instruments(
        self,
        query: str,
        exchange: str = "NSE",
    ) -> List[Dict[str, Any]]:
        """
        Search instruments.
        """

        try:

            instruments = (
                self._client.search_instruments(

                    exchange=exchange,

                    query=query,

                )
            )

            self._emit(

                "instrument_search",

                query=query,

            )

            return instruments

        except Exception:

            self._statistics.api_errors += 1

            self.logger.exception(
                "Instrument search failed."
            )

            return []

    # ==========================================================
    # INSTRUMENT LOOKUP
    # ==========================================================

    def get_instrument(
        self,
        symbol: str,
        exchange: str = "NSE",
    ) -> Optional[Dict[str, Any]]:
        """
        Return first matching instrument.
        """

        results = self.search_instruments(

            query=symbol,

            exchange=exchange,

        )

        if results:

            return results[0]

        return None

    # ==========================================================
    # INSTRUMENT KEY
    # ==========================================================

    def instrument_key(
        self,
        symbol: str,
        exchange: str = "NSE",
    ) -> Optional[str]:
        """
        Resolve Upstox instrument key.
        """

        instrument = self.get_instrument(

            symbol,

            exchange,

        )

        if instrument is None:

            return None

        return instrument.get(
            "instrument_key",
        )

    # ==========================================================
    # SYNCHRONIZATION
    # ==========================================================

    def synchronize(self) -> bool:
        """
        Synchronize local data.
        """

        self._statistics.sync_operations += 1

        sync = getattr(

            self._manager,

            "synchronize",

            None,

        )

        if callable(sync):

            try:

                sync()

            except Exception:

                self.logger.exception(
                    "Synchronization failed."
                )

                return False

        self._emit(
            "synchronized",
        )

        return True
        # ==========================================================
    # BATCH HISTORY
    # ==========================================================

    def get_histories(
        self,
        instrument_keys: List[str],
        interval: str,
        from_date: Any,
        to_date: Any,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load historical data for multiple instruments.
        """

        result: Dict[
            str,
            List[Dict[str, Any]]
        ] = {}

        for key in instrument_keys:

            try:

                result[key] = self.get_history(

                    instrument_key=key,

                    interval=interval,

                    from_date=from_date,

                    to_date=to_date,

                )

            except Exception:

                self._statistics.api_errors += 1

                self.logger.exception(

                    "History download failed for %s.",

                    key,

                )

        return result

    # ==========================================================
    # WATCHLIST
    # ==========================================================

    def watchlist_quotes(
        self,
        instrument_keys: List[str],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Return quotes for all watchlist instruments.
        """

        quotes = self.get_quotes(
            instrument_keys,
        )

        self._emit(

            "watchlist_updated",

            instruments=instrument_keys,

        )

        return quotes

    # ==========================================================
    # SCANNER DATA
    # ==========================================================

    def scanner_feed(
        self,
        instrument_keys: List[str],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Return live data for scanner engine.
        """

        feed = self.get_quotes(
            instrument_keys,
        )

        self._emit(

            "scanner_feed",

            instruments=instrument_keys,

        )

        return feed

    # ==========================================================
    # LIVE REFRESH
    # ==========================================================

    def refresh_quote(
        self,
        instrument_key: str,
    ) -> Dict[str, Any]:
        """
        Force refresh a quote from the data source.
        """

        cache_key = f"QUOTE:{instrument_key}"

        self._cache.pop(
            cache_key,
            None,
        )

        return self.get_quote(

            instrument_key,

            use_cache=False,

        )

    def refresh_quotes(
        self,
        instrument_keys: List[str],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Force refresh multiple quotes.
        """

        refreshed: Dict[
            str,
            Dict[str, Any]
        ] = {}

        for key in instrument_keys:

            try:

                refreshed[key] = self.refresh_quote(
                    key,
                )

            except Exception:

                self._statistics.api_errors += 1

        return refreshed

    # ==========================================================
    # CACHE CLEANUP
    # ==========================================================

    def cleanup_cache(self) -> int:
        """
        Remove expired cache entries.
        """

        removed = 0

        expired = []

        now = datetime.now()

        for key, entry in self._cache.items():

            if (

                entry.expires is not None

                and

                entry.expires <= now

            ):

                expired.append(key)

        for key in expired:

            self._cache.pop(
                key,
                None,
            )

            removed += 1

        if removed:

            self.logger.info(

                "Removed %d expired cache entries.",

                removed,

            )

        return removed

    # ==========================================================
    # VALIDATION
    # ==========================================================

    def validate_cache(
        self,
    ) -> bool:
        """
        Validate cache integrity.
        """

        for key, entry in self._cache.items():

            if key != entry.key:

                return False

        return True

    # ==========================================================
    # HEALTH
    # ==========================================================

    def health(self) -> Dict[str, Any]:
        """
        Return service health.
        """

        return {

            "healthy":
                True,

            "cache_entries":
                len(self._cache),

            "cache_valid":
                self.validate_cache(),

            "uptime":
                str(self.uptime),

            "statistics":
                self.statistics_dict(),

        }

    # ==========================================================
    # METRICS
    # ==========================================================

    def cache_size(self) -> int:
        """
        Return number of cached objects.
        """

        return len(
            self._cache,
        )

    def cache_keys(
        self,
    ) -> List[str]:
        """
        Return cached keys.
        """

        return sorted(
            self._cache.keys(),
        )
        # ==========================================================
    # STATISTICS
    # ==========================================================

    def reset_statistics(self) -> None:
        """
        Reset runtime statistics.
        """

        self._statistics = DataStatistics()

        self.logger.info(
            "DataService statistics reset."
        )

    def statistics_dict(self) -> Dict[str, Any]:
        """
        Return runtime statistics.
        """

        stats = self._statistics

        return {

            "quote_requests":
                stats.quote_requests,

            "historical_requests":
                stats.historical_requests,

            "live_requests":
                stats.live_requests,

            "cache_hits":
                stats.cache_hits,

            "cache_misses":
                stats.cache_misses,

            "sync_operations":
                stats.sync_operations,

            "api_errors":
                stats.api_errors,

            "cache_entries":
                len(self._cache),

            "uptime_seconds":
                int(
                    self.uptime.total_seconds()
                ),

        }

    # ==========================================================
    # PERFORMANCE
    # ==========================================================

    def performance_report(
        self,
    ) -> Dict[str, Any]:
        """
        Return performance metrics.
        """

        stats = self.statistics_dict()

        total_requests = (

            stats["quote_requests"]

            + stats["historical_requests"]

        )

        cache_requests = (

            stats["cache_hits"]

            + stats["cache_misses"]

        )

        cache_hit_rate = (

            100.0

            if cache_requests == 0

            else round(

                (stats["cache_hits"] / cache_requests) * 100,

                2,

            )

        )

        success = max(

            total_requests - stats["api_errors"],

            0,

        )

        success_rate = (

            100.0

            if total_requests == 0

            else round(

                (success / total_requests) * 100,

                2,

            )

        )

        return {

            "version":
                self.VERSION,

            "total_requests":
                total_requests,

            "success_rate":
                success_rate,

            "cache_hit_rate":
                cache_hit_rate,

            "cache_entries":
                len(self._cache),

            "uptime":
                str(self.uptime),

        }

    # ==========================================================
    # DIAGNOSTICS
    # ==========================================================

    def diagnostics(
        self,
    ) -> Dict[str, Any]:
        """
        Return diagnostic information.
        """

        return {

            "service":
                self.__class__.__name__,

            "version":
                self.VERSION,

            "health":
                self.health(),

            "statistics":
                self.statistics_dict(),

            "performance":
                self.performance_report(),

            "registered_events":
                {

                    event: len(callbacks)

                    for event, callbacks

                    in self._callbacks.items()

                },

        }

    # ==========================================================
    # SUMMARY
    # ==========================================================

    def summary(self) -> Dict[str, Any]:
        """
        Return concise service summary.
        """

        return {

            "service":
                self.__class__.__name__,

            "version":
                self.VERSION,

            "cache_entries":
                len(self._cache),

            "uptime":
                str(self.uptime),

            "quotes":
                self.statistics.quote_requests,

            "history":
                self.statistics.historical_requests,

            "errors":
                self.statistics.api_errors,

        }

    # ==========================================================
    # EXPORT
    # ==========================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Export service information.
        """

        return {

            "summary":
                self.summary(),

            "health":
                self.health(),

            "statistics":
                self.statistics_dict(),

            "performance":
                self.performance_report(),

            "diagnostics":
                self.diagnostics(),

        }

    # ==========================================================
    # CACHE PERSISTENCE
    # ==========================================================

    def export_cache(
        self,
    ) -> Dict[str, Any]:
        """
        Export cache contents.

        Serialization is intentionally lightweight.
        """

        return {

            key: {

                "source": entry.source.value,

                "created": entry.created,

                "expires": entry.expires,

                "value": entry.value,

            }

            for key, entry

            in self._cache.items()

        }

    def import_cache(
        self,
        cache: Dict[str, CacheEntry],
    ) -> None:
        """
        Import cache entries.
        """

        self._cache.update(cache)

        self.logger.info(

            "Imported %d cache entries.",

            len(cache),

        )

        self._emit(

            "cache_imported",

            entries=len(cache),

        )

    # ==========================================================
    # RESET
    # ==========================================================

    def reset(self) -> None:
        """
        Reset runtime state.
        """

        self.clear_cache()

        self.clear_events()

        self.reset_statistics()

        self.logger.info(
            "DataService reset completed."
        )

        self._emit(
            "service_reset",
        )
            # ==========================================================
    # LIFECYCLE
    # ==========================================================

    def start(self) -> None:
        """
        Start the DataService.
        """

        self.logger.info(
            "Starting DataService..."
        )

        self._emit(
            "service_started",
        )

    def stop(self) -> None:
        """
        Stop the DataService.
        """

        self.logger.info(
            "Stopping DataService..."
        )

        self._emit(
            "service_stopped",
        )

    def restart(self) -> None:
        """
        Restart the DataService.
        """

        self.stop()

        self.start()

    # ==========================================================
    # VALIDATION
    # ==========================================================

    def validate(self) -> bool:
        """
        Validate service configuration.
        """

        if self._client is None:

            raise RuntimeError(
                "UpstoxClient is not configured."
            )

        if self._manager is None:

            raise RuntimeError(
                "DataManager is not configured."
            )

        return True

    def assert_ready(self) -> None:
        """
        Ensure the service is ready.
        """

        self.validate()

    # ==========================================================
    # SNAPSHOT
    # ==========================================================

    def snapshot(self) -> Dict[str, Any]:
        """
        Return runtime snapshot.
        """

        return {

            "summary":
                self.summary(),

            "health":
                self.health(),

            "statistics":
                self.statistics_dict(),

            "performance":
                self.performance_report(),

            "cache_size":
                self.cache_size(),

            "registered_events":
                {

                    event: len(callbacks)

                    for event, callbacks

                    in self._callbacks.items()

                },

        }

    # ==========================================================
    # CLONE
    # ==========================================================

    def clone(self) -> "DataService":
        """
        Create another DataService using the
        same client and manager.
        """

        return self.__class__(

            client=self._client,

            manager=self._manager,

        )

    # ==========================================================
    # DISPOSE
    # ==========================================================

    def dispose(self) -> None:
        """
        Release runtime resources.
        """

        self.clear_cache()

        self.clear_events()

        self.logger.info(
            "DataService disposed."
        )

    # ==========================================================
    # CONTEXT MANAGER
    # ==========================================================

    def __enter__(self) -> "DataService":
        """
        Context manager entry.
        """

        self.start()

        return self

    def __exit__(
        self,
        exc_type,
        exc,
        traceback,
    ) -> None:
        """
        Context manager exit.
        """

        self.stop()

    # ==========================================================
    # STRING REPRESENTATION
    # ==========================================================

    def __repr__(self) -> str:

        return (

            f"{self.__class__.__name__}("

            f"cache={len(self._cache)}, "

            f"quotes={self.statistics.quote_requests}, "

            f"history={self.statistics.historical_requests}, "

            f"errors={self.statistics.api_errors})"

        )

    def __str__(self) -> str:

        return (

            f"{self.__class__.__name__}"

            f"[cache={len(self._cache)}]"

        )

    # ==========================================================
    # DEBUG
    # ==========================================================

    def dump(self) -> Dict[str, Any]:
        """
        Return complete runtime information.
        """

        return {

            "repr":
                repr(self),

            "snapshot":
                self.snapshot(),

            "diagnostics":
                self.diagnostics(),

            "cache_keys":
                self.cache_keys(),

        }
        # ==========================================================
    # EVENT UTILITIES
    # ==========================================================

    def event_count(self) -> int:
        """
        Return total registered callbacks.
        """

        return sum(

            len(callbacks)

            for callbacks

            in self._callbacks.values()

        )

    def events(self) -> Dict[str, int]:
        """
        Return registered event summary.
        """

        return {

            event: len(callbacks)

            for event, callbacks

            in self._callbacks.items()

        }

    def has_event(
        self,
        event: str,
    ) -> bool:
        """
        Return True if an event has subscribers.
        """

        return (

            event in self._callbacks

            and

            len(
                self._callbacks[event]
            ) > 0

        )

    # ==========================================================
    # CACHE UTILITIES
    # ==========================================================

    def has_cache(
        self,
        key: str,
    ) -> bool:
        """
        Check whether a cache entry exists and is valid.
        """

        return self.get_cache(key) is not None

    def remove_cache(
        self,
        key: str,
    ) -> bool:
        """
        Remove a cache entry.
        """

        if key not in self._cache:

            return False

        self._cache.pop(
            key,
            None,
        )

        self._emit(
            "cache_removed",
            key=key,
        )

        return True

    # ==========================================================
    # CONNECTION
    # ==========================================================

    def connected(self) -> bool:
        """
        Return True if the underlying client
        is connected.
        """

        checker = getattr(

            self._client,

            "is_connected",

            None,

        )

        if callable(checker):

            try:

                return bool(checker())

            except Exception:

                self.logger.exception(
                    "Connection check failed."
                )

                return False

        return True

    # ==========================================================
    # INFORMATION
    # ==========================================================

    def info(self) -> Dict[str, Any]:
        """
        Return general service information.
        """

        return {

            "service":
                self.__class__.__name__,

            "version":
                self.VERSION,

            "connected":
                self.connected(),

            "cache_entries":
                len(self._cache),

            "uptime":
                str(self.uptime),

        }

    # ==========================================================
    # FACTORY
    # ==========================================================

    @classmethod
    def create(
        cls,
        client: UpstoxClient,
        manager: DataManager,
    ) -> "DataService":
        """
        Factory constructor.
        """

        return cls(

            client=client,

            manager=manager,

        )


# ==========================================================
# MODULE HELPERS
# ==========================================================

def create_data_service(
    client: UpstoxClient,
    manager: DataManager,
) -> DataService:
    """
    Convenience factory.
    """

    return DataService.create(

        client=client,

        manager=manager,

    )


def build_data_service(
    client: UpstoxClient,
    manager: DataManager,
) -> DataService:
    """
    Alternate factory helper.
    """

    return DataService(

        client=client,

        manager=manager,

    )
# ==========================================================
# MODULE EXPORTS
# ==========================================================

__all__ = [

    # Enums
    "DataSource",
    "DataStatus",

    # Models
    "CacheEntry",
    "DataStatistics",

    # Service
    "DataService",

    # Factory Helpers
    "create_data_service",
    "build_data_service",

]

# ==========================================================
# END OF FILE
# ==========================================================

# ==========================
# END OF FILE
# ==========================