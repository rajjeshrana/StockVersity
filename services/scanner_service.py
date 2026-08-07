from __future__ import annotations

"""
==========================================================
StockVersity Scanner Pro
Scanner Service

Author  : StockVersity
Version : 1.0.0

This service acts as the business layer between the UI
controllers and the ScreenerEngine.

Responsibilities
----------------
• Execute scans
• Scan lifecycle management
• Cache management
• Progress reporting
• Event notifications
• Retry handling
• Statistics
• Diagnostics
• Health monitoring
==========================================================
"""

import logging
import threading
import time

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional

from core.screener_engine import ScreenerEngine


# ==========================================================
# SCAN MODE
# ==========================================================

class ScanMode(Enum):
    """
    Supported scan modes.
    """

    INTRADAY = "intraday"

    SWING = "swing"

    POSITIONAL = "positional"

    CUSTOM = "custom"


# ==========================================================
# SCAN STATE
# ==========================================================

class ScanState(Enum):
    """
    Scanner lifecycle state.
    """

    IDLE = "idle"

    VALIDATING = "validating"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"


# ==========================================================
# CACHE ENTRY
# ==========================================================

@dataclass(slots=True)
class ScanCacheEntry:
    """
    Cached scan result.
    """

    mode: ScanMode

    created: datetime

    duration: float

    results: List[Dict[str, Any]]

    parameters: Dict[str, Any] = field(
        default_factory=dict
    )


# ==========================================================
# SCAN STATISTICS
# ==========================================================

@dataclass(slots=True)
class ScanStatistics:
    """
    Runtime statistics.
    """

    total_scans: int = 0

    successful_scans: int = 0

    failed_scans: int = 0

    cancelled_scans: int = 0

    cache_hits: int = 0

    cache_misses: int = 0

    total_scan_time: float = 0.0

    last_scan: Optional[datetime] = None

    last_duration: float = 0.0


# ==========================================================
# SCANNER SERVICE
# ==========================================================

class ScannerService:
    """
    Business service responsible for executing
    all StockVersity scanners.

    Controllers should communicate only with this
    service instead of calling ScreenerEngine directly.
    """

    VERSION = "1.0.0"

    DEFAULT_CACHE_TTL = timedelta(
        seconds=30
    )

    DEFAULT_RETRY_COUNT = 3

    def __init__(
        self,
        screener: ScreenerEngine,
    ) -> None:

        self.logger = logging.getLogger(
            self.__class__.__name__
        )

        self._screener = screener

        self._state = ScanState.IDLE

        self._statistics = ScanStatistics()

        self._cache: Dict[
            str,
            ScanCacheEntry
        ] = {}

        self._history: List[
            ScanCacheEntry
        ] = []

        self._cache_ttl = (
            self.DEFAULT_CACHE_TTL
        )

        self._progress_callback: Optional[
            Callable[[int], None]
        ] = None

        self._event_handlers: Dict[
            str,
            List[Callable[..., None]]
        ] = {}

        self._cancel_requested = False

        self._lock = threading.RLock()

        self._started = datetime.now()

        self.logger.info(
            "ScannerService initialized."
        )
            # ==========================================================
    # PROPERTIES
    # ==========================================================

    @property
    def screener(self) -> ScreenerEngine:
        """
        Return ScreenerEngine instance.
        """

        return self._screener

    @property
    def state(self) -> ScanState:
        """
        Current scanner state.
        """

        return self._state

    @property
    def started(self) -> datetime:
        """
        Service start time.
        """

        return self._started

    @property
    def statistics(self) -> ScanStatistics:
        """
        Runtime statistics.
        """

        return self._statistics

    # ==========================================================
    # STATE MANAGEMENT
    # ==========================================================

    def _set_state(
        self,
        state: ScanState,
    ) -> None:
        """
        Change scanner state.
        """

        self._state = state

        self.logger.debug(
            "Scanner state changed to %s",
            state.value,
        )

        self._emit_event(
            "state_changed",
            state=state,
        )

    def is_idle(self) -> bool:
        """
        True if scanner is idle.
        """

        return self._state == ScanState.IDLE

    def is_running(self) -> bool:
        """
        True if scanner is running.
        """

        return self._state == ScanState.RUNNING

    def is_cancelled(self) -> bool:
        """
        True if cancellation was requested.
        """

        return self._cancel_requested

    def is_ready(self) -> bool:
        """
        Check whether the service is ready.
        """

        return self._screener is not None

    # ==========================================================
    # EVENT SYSTEM
    # ==========================================================

    def register_event(
        self,
        event: str,
        callback: Callable[..., None],
    ) -> None:
        """
        Register an event callback.
        """

        self._event_handlers.setdefault(
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

        if event not in self._event_handlers:
            return

        try:

            self._event_handlers[event].remove(
                callback,
            )

        except ValueError:
            pass

    def clear_events(self) -> None:
        """
        Remove every registered callback.
        """

        self._event_handlers.clear()

    def _emit_event(
        self,
        event: str,
        **kwargs: Any,
    ) -> None:
        """
        Notify subscribers.
        """

        callbacks = self._event_handlers.get(
            event,
            [],
        )

        for callback in callbacks:

            try:

                callback(**kwargs)

            except Exception:

                self.logger.exception(
                    "Event callback failed (%s).",
                    event,
                )

    # ==========================================================
    # PROGRESS CALLBACK
    # ==========================================================

    def set_progress_callback(
        self,
        callback: Callable[[int], None],
    ) -> None:
        """
        Register progress callback.
        """

        self._progress_callback = callback

    def clear_progress_callback(
        self,
    ) -> None:
        """
        Remove progress callback.
        """

        self._progress_callback = None

    def _update_progress(
        self,
        value: int,
    ) -> None:
        """
        Update scan progress.
        """

        value = max(
            0,
            min(
                100,
                value,
            ),
        )

        if self._progress_callback is not None:

            try:

                self._progress_callback(
                    value,
                )

            except Exception:

                self.logger.exception(
                    "Progress callback failed."
                )

        self._emit_event(
            "progress",
            value=value,
        )

    # ==========================================================
    # CANCELLATION
    # ==========================================================

    def cancel_scan(self) -> None:
        """
        Request scan cancellation.
        """

        self.logger.info(
            "Cancellation requested."
        )

        self._cancel_requested = True

    def reset_cancellation(self) -> None:
        """
        Reset cancellation flag.
        """

        self._cancel_requested = False

    def _check_cancelled(self) -> None:
        """
        Raise when cancellation requested.
        """

        if self._cancel_requested:

            self._statistics.cancelled_scans += 1

            self._set_state(
                ScanState.CANCELLED,
            )

            raise RuntimeError(
                "Scan cancelled."
            )
            # ==========================================================
    # VALIDATION
    # ==========================================================

    def validate_scan(
        self,
        mode: ScanMode,
        **kwargs: Any,
    ) -> None:
        """
        Validate a scan request.
        """

        if not self.is_ready():

            raise RuntimeError(
                "ScannerService is not initialized."
            )

        if not isinstance(
            mode,
            ScanMode,
        ):

            raise TypeError(
                "Invalid scan mode."
            )

        if self.is_running():

            raise RuntimeError(
                "Another scan is already running."
            )

    # ==========================================================
    # CACHE
    # ==========================================================

    def _build_cache_key(
        self,
        mode: ScanMode,
        **kwargs: Any,
    ) -> str:
        """
        Build cache key.
        """

        if not kwargs:

            return mode.value

        parts: List[str] = []

        for key in sorted(kwargs):

            value = kwargs[key]

            parts.append(
                f"{key}={value}"
            )

        return (
            mode.value
            + "|"
            + "|".join(parts)
        )

    def _is_cache_valid(
        self,
        entry: ScanCacheEntry,
    ) -> bool:
        """
        Check cache expiration.
        """

        age = datetime.now() - entry.created

        return age <= self._cache_ttl

    def _get_cached_result(
        self,
        mode: ScanMode,
        **kwargs: Any,
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Return cached scan if available.
        """

        key = self._build_cache_key(
            mode,
            **kwargs,
        )

        entry = self._cache.get(key)

        if entry is None:

            self._statistics.cache_misses += 1

            return None

        if not self._is_cache_valid(
            entry,
        ):

            self.logger.debug(
                "Cache expired (%s).",
                key,
            )

            del self._cache[key]

            self._statistics.cache_misses += 1

            return None

        self._statistics.cache_hits += 1

        self.logger.debug(
            "Cache hit (%s).",
            key,
        )

        return entry.results

    def _store_cache(
        self,
        mode: ScanMode,
        duration: float,
        results: List[Dict[str, Any]],
        **kwargs: Any,
    ) -> None:
        """
        Store scan in cache.
        """

        key = self._build_cache_key(
            mode,
            **kwargs,
        )

        entry = ScanCacheEntry(

            mode=mode,

            created=datetime.now(),

            duration=duration,

            results=results,

            parameters=dict(kwargs),

        )

        self._cache[key] = entry

        self._history.append(entry)

    # ==========================================================
    # CACHE MANAGEMENT
    # ==========================================================

    def clear_cache(self) -> None:
        """
        Clear all cached scans.
        """

        self._cache.clear()

        self.logger.info(
            "Cache cleared."
        )

    def cache_size(self) -> int:
        """
        Number of cached scans.
        """

        return len(
            self._cache
        )

    def cache_hit_ratio(self) -> float:
        """
        Cache hit ratio.
        """

        total = (

            self._statistics.cache_hits

            + self._statistics.cache_misses

        )

        if total == 0:

            return 0.0

        return round(

            self._statistics.cache_hits
            / total,

            4,

        )

    def cache_statistics(
        self,
    ) -> Dict[str, Any]:
        """
        Cache statistics.
        """

        return {

            "entries":

                len(self._cache),

            "history":

                len(self._history),

            "hits":

                self._statistics.cache_hits,

            "misses":

                self._statistics.cache_misses,

            "hit_ratio":

                self.cache_hit_ratio(),

            "ttl_seconds":

                int(
                    self._cache_ttl.total_seconds()
                ),

        }

    # ==========================================================
    # HISTORY
    # ==========================================================

    def history(
        self,
    ) -> List[ScanCacheEntry]:
        """
        Complete scan history.
        """

        return list(
            self._history
        )

    def last_history(
        self,
        count: int = 10,
    ) -> List[ScanCacheEntry]:
        """
        Return recent scan history.
        """

        if count <= 0:

            return []

        return self._history[-count:]

    def clear_history(self) -> None:
        """
        Remove scan history.
        """

        self._history.clear()

        self.logger.info(
            "History cleared."
        )
            # ==========================================================
    # STRATEGY REGISTRY
    # ==========================================================

    def _strategy_registry(
        self,
    ) -> Dict[ScanMode, Callable[..., List[Dict[str, Any]]]]:
        """
        Return registered scan strategies.
        """

        return {

            ScanMode.INTRADAY:
                self._screener.scan_intraday,

            ScanMode.SWING:
                self._screener.scan_swing,

            ScanMode.POSITIONAL:
                self._screener.scan_positional,

            ScanMode.CUSTOM:
                self._screener.scan_custom,

        }

    # ==========================================================
    # EXECUTE STRATEGY
    # ==========================================================

    def _execute_strategy(
        self,
        mode: ScanMode,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Execute selected scan strategy.
        """

        registry = self._strategy_registry()

        strategy = registry.get(mode)

        if strategy is None:

            raise ValueError(
                f"No strategy registered for '{mode.value}'."
            )

        return strategy(**kwargs)

    # ==========================================================
    # RETRY EXECUTION
    # ==========================================================

    def _execute_with_retry(
        self,
        mode: ScanMode,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Execute strategy with retry support.
        """

        last_exception: Exception | None = None

        for attempt in range(
            1,
            self.DEFAULT_RETRY_COUNT + 1,
        ):

            self._check_cancelled()

            try:

                return self._execute_strategy(
                    mode,
                    **kwargs,
                )

            except Exception as ex:

                last_exception = ex

                self.logger.warning(

                    "Scan attempt %s/%s failed: %s",

                    attempt,

                    self.DEFAULT_RETRY_COUNT,

                    ex,

                )

                if attempt < self.DEFAULT_RETRY_COUNT:

                    time.sleep(
                        attempt * 0.5
                    )

        raise RuntimeError(
            "Maximum retry attempts exceeded."
        ) from last_exception

    # ==========================================================
    # MAIN SCAN
    # ==========================================================

    def scan(
        self,
        mode: ScanMode = ScanMode.INTRADAY,
        use_cache: bool = True,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Execute a scanner.
        """

        with self._lock:

            self.validate_scan(
                mode,
                **kwargs,
            )

            self.reset_cancellation()

            self._set_state(
                ScanState.VALIDATING
            )

            if use_cache:

                cached = self._get_cached_result(
                    mode,
                    **kwargs,
                )

                if cached is not None:

                    self.logger.info(
                        "Returning cached results."
                    )

                    self._emit_event(
                        "cache_hit",
                        mode=mode,
                    )

                    return cached

            self._set_state(
                ScanState.RUNNING
            )

            self._update_progress(
                5
            )

            self._emit_event(
                "scan_started",
                mode=mode,
            )

            started = time.perf_counter()

            try:

                results = self._execute_with_retry(
                    mode,
                    **kwargs,
                )

                duration = (

                    time.perf_counter()

                    - started

                )

                self._statistics.total_scans += 1

                self._statistics.successful_scans += 1

                self._statistics.total_scan_time += (
                    duration
                )

                self._statistics.last_scan = (
                    datetime.now()
                )

                self._statistics.last_duration = (
                    duration
                )

                self._store_cache(

                    mode,

                    duration,

                    results,

                    **kwargs,

                )

                self._update_progress(
                    100
                )

                self._set_state(
                    ScanState.COMPLETED
                )

                self._emit_event(

                    "scan_completed",

                    mode=mode,

                    results=results,

                    duration=duration,

                )

                self.logger.info(

                    "%s scan completed in %.3f sec (%d stocks).",

                    mode.value,

                    duration,

                    len(results),

                )

                return results

            except Exception as ex:

                self._statistics.total_scans += 1

                self._statistics.failed_scans += 1

                self._set_state(
                    ScanState.FAILED
                )

                self._emit_event(

                    "scan_failed",

                    mode=mode,

                    exception=ex,

                )

                self.logger.exception(
                    ex
                )

                raise

            finally:

                if self._state != ScanState.CANCELLED:

                    self._set_state(
                        ScanState.IDLE
                    )

                self._update_progress(
                    0
                )

    # ==========================================================
    # SHORTCUT METHODS
    # ==========================================================

    def intraday_scan(
        self,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Execute intraday scan.
        """

        return self.scan(
            ScanMode.INTRADAY,
            **kwargs,
        )

    def swing_scan(
        self,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Execute swing scan.
        """

        return self.scan(
            ScanMode.SWING,
            **kwargs,
        )

    def positional_scan(
        self,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Execute positional scan.
        """

        return self.scan(
            ScanMode.POSITIONAL,
            **kwargs,
        )

    def custom_scan(
        self,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Execute custom scan.
        """

        return self.scan(
            ScanMode.CUSTOM,
            **kwargs,
        )
        # ==========================================================
    # STATISTICS
    # ==========================================================

    def total_scans(self) -> int:
        """
        Total number of executed scans.
        """

        return self._statistics.total_scans

    def successful_scans(self) -> int:
        """
        Total successful scans.
        """

        return self._statistics.successful_scans

    def failed_scans(self) -> int:
        """
        Total failed scans.
        """

        return self._statistics.failed_scans

    def cancelled_scans(self) -> int:
        """
        Total cancelled scans.
        """

        return self._statistics.cancelled_scans

    def last_scan_time(
        self,
    ) -> Optional[datetime]:
        """
        Return last scan timestamp.
        """

        return self._statistics.last_scan

    def last_scan_duration(
        self,
    ) -> float:
        """
        Return last scan duration.
        """

        return self._statistics.last_duration

    def average_scan_duration(
        self,
    ) -> float:
        """
        Average execution time.
        """

        completed = (
            self._statistics.successful_scans
        )

        if completed == 0:

            return 0.0

        return round(

            self._statistics.total_scan_time
            / completed,

            4,

        )

    def uptime(self) -> timedelta:
        """
        Service uptime.
        """

        return datetime.now() - self._started

    # ==========================================================
    # HEALTH
    # ==========================================================

    def health_check(
        self,
    ) -> Dict[str, Any]:
        """
        Service health report.
        """

        healthy = (
            self.is_ready()
            and self.state != ScanState.FAILED
        )

        return {

            "healthy":
                healthy,

            "state":
                self.state.value,

            "uptime_seconds":
                int(
                    self.uptime().total_seconds()
                ),

            "cache_entries":
                self.cache_size(),

            "history_entries":
                len(self._history),

            "total_scans":
                self.total_scans(),

            "success":
                self.successful_scans(),

            "failed":
                self.failed_scans(),

            "cancelled":
                self.cancelled_scans(),

        }

    # ==========================================================
    # PERFORMANCE
    # ==========================================================

    def performance_report(
        self,
    ) -> Dict[str, Any]:
        """
        Runtime performance information.
        """

        return {

            "average_scan_time":
                self.average_scan_duration(),

            "last_scan_time":
                self.last_scan_time(),

            "last_scan_duration":
                self.last_scan_duration(),

            "cache_hit_ratio":
                self.cache_hit_ratio(),

            "cache_statistics":
                self.cache_statistics(),

        }

    # ==========================================================
    # SUMMARY
    # ==========================================================

    def summary(
        self,
    ) -> Dict[str, Any]:
        """
        Return complete service summary.
        """

        return {

            "version":
                self.VERSION,

            "state":
                self.state.value,

            "started":
                self.started,

            "uptime":
                str(
                    self.uptime()
                ),

            "statistics": {

                "total":
                    self.total_scans(),

                "successful":
                    self.successful_scans(),

                "failed":
                    self.failed_scans(),

                "cancelled":
                    self.cancelled_scans(),

            },

            "performance":
                self.performance_report(),

            "health":
                self.health_check(),

        }

    # ==========================================================
    # DIAGNOSTICS
    # ==========================================================

    def diagnostics(
        self,
    ) -> Dict[str, Any]:
        """
        Detailed diagnostic report.
        """

        return {

            "service":
                self.summary(),

            "cache":
                self.cache_statistics(),

            "history_count":
                len(self._history),

            "events":
                {

                    event: len(callbacks)

                    for event, callbacks

                    in self._event_handlers.items()

                },

            "thread":

                threading.current_thread().name,

        }

    # ==========================================================
    # PRINT REPORT
    # ==========================================================

    def print_report(
        self,
    ) -> None:
        """
        Write diagnostic report to logger.
        """

        report = self.summary()

        self.logger.info("=" * 60)

        self.logger.info(
            "Scanner Service Report"
        )

        self.logger.info("=" * 60)

        self.logger.info(
            "State          : %s",
            report["state"],
        )

        self.logger.info(
            "Total Scans    : %s",
            report["statistics"]["total"],
        )

        self.logger.info(
            "Successful     : %s",
            report["statistics"]["successful"],
        )

        self.logger.info(
            "Failed         : %s",
            report["statistics"]["failed"],
        )

        self.logger.info(
            "Average Time   : %.3f sec",
            self.average_scan_duration(),
        )

        self.logger.info(
            "Cache Hit Rate : %.2f%%",
            self.cache_hit_ratio() * 100,
        )

        self.logger.info("=" * 60)
            # ==========================================================
    # CONFIGURATION
    # ==========================================================

    def cache_ttl(self) -> timedelta:
        """
        Return current cache TTL.
        """

        return self._cache_ttl

    def set_cache_ttl(
        self,
        ttl: timedelta,
    ) -> None:
        """
        Update cache TTL.
        """

        if ttl.total_seconds() <= 0:

            raise ValueError(
                "Cache TTL must be greater than zero."
            )

        self._cache_ttl = ttl

        self.logger.info(
            "Cache TTL updated to %s seconds.",
            int(ttl.total_seconds()),
        )

    def retry_count(self) -> int:
        """
        Return retry count.
        """

        return self.DEFAULT_RETRY_COUNT

    # ==========================================================
    # STRATEGY REGISTRATION
    # ==========================================================

    def register_strategy(
        self,
        mode: ScanMode,
        strategy: Callable[..., List[Dict[str, Any]]],
    ) -> None:
        """
        Register or replace a scan strategy.
        """

        if not hasattr(self, "_custom_strategies"):

            self._custom_strategies: Dict[
                ScanMode,
                Callable[..., List[Dict[str, Any]]]
            ] = {}

        self._custom_strategies[mode] = strategy

        self.logger.info(
            "Strategy registered for '%s'.",
            mode.value,
        )

    def unregister_strategy(
        self,
        mode: ScanMode,
    ) -> None:
        """
        Remove a custom strategy.
        """

        if not hasattr(self, "_custom_strategies"):

            return

        self._custom_strategies.pop(
            mode,
            None,
        )

    def available_strategies(
        self,
    ) -> List[str]:
        """
        Return available strategy names.
        """

        names = [
            mode.value
            for mode in ScanMode
        ]

        if hasattr(
            self,
            "_custom_strategies",
        ):

            for mode in self._custom_strategies:

                if mode.value not in names:

                    names.append(
                        mode.value
                    )

        return sorted(names)

    # ==========================================================
    # INTERNAL STRATEGY LOOKUP
    # ==========================================================

    def _strategy_registry(
        self,
    ) -> Dict[
        ScanMode,
        Callable[..., List[Dict[str, Any]]],
    ]:
        """
        Return merged strategy registry.
        """

        registry = {

            ScanMode.INTRADAY:
                self._screener.scan_intraday,

            ScanMode.SWING:
                self._screener.scan_swing,

            ScanMode.POSITIONAL:
                self._screener.scan_positional,

            ScanMode.CUSTOM:
                self._screener.scan_custom,

        }

        if hasattr(
            self,
            "_custom_strategies",
        ):

            registry.update(
                self._custom_strategies
            )

        return registry

    # ==========================================================
    # RESET SERVICE
    # ==========================================================

    def reset(
        self,
    ) -> None:
        """
        Reset runtime state.
        """

        with self._lock:

            self._set_state(
                ScanState.IDLE
            )

            self.reset_cancellation()

            self.clear_cache()

            self.clear_history()

            self._statistics = ScanStatistics()

            self.logger.info(
                "ScannerService reset completed."
            )

    # ==========================================================
    # SNAPSHOT
    # ==========================================================

    def snapshot(
        self,
    ) -> Dict[str, Any]:
        """
        Capture current runtime snapshot.
        """

        return {

            "timestamp":
                datetime.now(),

            "state":
                self.state.value,

            "statistics":
                self.summary(),

            "performance":
                self.performance_report(),

            "health":
                self.health_check(),

            "cache":
                self.cache_statistics(),

        }

    # ==========================================================
    # EXPORT RUNTIME
    # ==========================================================

    def export_runtime(
        self,
    ) -> Dict[str, Any]:
        """
        Export runtime information.
        """

        return {

            "version":
                self.VERSION,

            "started":
                self.started,

            "snapshot":
                self.snapshot(),

            "history":
                len(self._history),

            "available_modes":
                self.available_strategies(),

        }

    # ==========================================================
    # VERSION
    # ==========================================================

    @classmethod
    def version(cls) -> str:
        """
        Service version.
        """

        return cls.VERSION
        # ==========================================================
    # VALIDATION
    # ==========================================================

    def validate(self) -> bool:
        """
        Validate the service configuration.
        """

        if self._screener is None:

            self.logger.error(
                "ScreenerEngine is not configured."
            )

            return False

        if not isinstance(
            self._cache,
            dict,
        ):

            self.logger.error(
                "Cache storage is invalid."
            )

            return False

        if not isinstance(
            self._history,
            list,
        ):

            self.logger.error(
                "History storage is invalid."
            )

            return False

        return True

    def assert_valid(self) -> None:
        """
        Raise an exception if the service is invalid.
        """

        if not self.validate():

            raise RuntimeError(
                "ScannerService validation failed."
            )

    # ==========================================================
    # INFORMATION
    # ==========================================================

    def info(self) -> Dict[str, Any]:
        """
        Return service information.
        """

        return {

            "service":
                self.__class__.__name__,

            "version":
                self.VERSION,

            "state":
                self.state.value,

            "started":
                self.started,

            "uptime":
                str(self.uptime()),

            "ready":
                self.is_ready(),

            "running":
                self.is_running(),

            "cache_entries":
                self.cache_size(),

            "history_entries":
                len(self._history),

        }

    # ==========================================================
    # CLONE CONFIGURATION
    # ==========================================================

    def clone(
        self,
    ) -> "ScannerService":
        """
        Create a new service with the same configuration.
        Runtime state, cache and history are not copied.
        """

        clone = ScannerService(
            self._screener,
        )

        clone.set_cache_ttl(
            self._cache_ttl,
        )

        if hasattr(
            self,
            "_custom_strategies",
        ):

            for mode, strategy in (
                self._custom_strategies.items()
            ):

                clone.register_strategy(
                    mode,
                    strategy,
                )

        return clone

    # ==========================================================
    # DISPOSAL
    # ==========================================================

    def dispose(self) -> None:
        """
        Release runtime resources.
        """

        self.logger.info(
            "Disposing ScannerService..."
        )

        with self._lock:

            self.reset_cancellation()

            self.clear_progress_callback()

            self.clear_events()

            self.clear_cache()

            self.clear_history()

            self._set_state(
                ScanState.IDLE,
            )

        self.logger.info(
            "ScannerService disposed."
        )

    # ==========================================================
    # CONTEXT MANAGER
    # ==========================================================

    def __enter__(
        self,
    ) -> "ScannerService":
        """
        Context manager entry.
        """

        self.assert_valid()

        return self

    def __exit__(
        self,
        exc_type: Any,
        exc_val: Any,
        exc_tb: Any,
    ) -> bool:
        """
        Context manager exit.
        """

        self.dispose()

        return False

    # ==========================================================
    # REPRESENTATION
    # ==========================================================

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (

            f"{self.__class__.__name__}("

            f"state={self.state.value!r}, "

            f"ready={self.is_ready()}, "

            f"scans={self.total_scans()})"

        )

    def __str__(
        self,
    ) -> str:
        """
        Human-readable representation.
        """

        return (

            f"{self.__class__.__name__}"

            f"[{self.state.value}]"

        )

    # ==========================================================
    # FACTORY
    # ==========================================================

    @classmethod
    def create(
        cls,
        screener: ScreenerEngine,
    ) -> "ScannerService":
        """
        Factory method.
        """

        service = cls(
            screener,
        )

        service.assert_valid()

        return service

    # ==========================================================
    # IS HEALTHY
    # ==========================================================

    def is_healthy(
        self,
    ) -> bool:
        """
        Return overall health status.
        """

        return self.health_check()[
            "healthy"
        ]
    # ==========================================================
# MODULE FACTORY
# ==========================================================

_default_service: ScannerService | None = None


def create_scanner_service(
    screener: ScreenerEngine,
) -> ScannerService:
    """
    Create a new ScannerService instance.
    """

    return ScannerService.create(
        screener,
    )


def set_default_scanner_service(
    service: ScannerService,
) -> None:
    """
    Set the module default ScannerService.
    """

    global _default_service

    _default_service = service


def get_default_scanner_service() -> ScannerService:
    """
    Return the default ScannerService.
    """

    if _default_service is None:

        raise RuntimeError(
            "Default ScannerService has not been configured."
        )

    return _default_service


def clear_default_scanner_service() -> None:
    """
    Dispose and remove the default ScannerService.
    """

    global _default_service

    if _default_service is not None:

        try:

            _default_service.dispose()

        finally:

            _default_service = None


# ==========================================================
# MODULE INFORMATION
# ==========================================================

__version__ = "1.0.0"

__author__ = "StockVersity"

__license__ = "Proprietary"

__all__ = [

    "ScanMode",

    "ScanState",

    "ScanCacheEntry",

    "ScanStatistics",

    "ScannerService",

    "create_scanner_service",

    "set_default_scanner_service",

    "get_default_scanner_service",

    "clear_default_scanner_service",

]


# ==========================================================
# END OF FILE
# ==========================================================part 