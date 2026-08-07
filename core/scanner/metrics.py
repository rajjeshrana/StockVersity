"""
=========================================================
StockVersity Scanner Pro
Scanner Metrics
Version : 2.0
=========================================================

Central scanner metrics and counters.

Responsibilities
----------------
• Track total scan cycles
• Track processed symbols
• Track generated / accepted / rejected signals
• Track market-data requests
• Track cache hits / misses
• Track scanner errors
• Track execution timing
• Calculate throughput
• Provide dashboard-ready metrics
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from threading import RLock

from typing import Any
from typing import Dict
from typing import Optional


# =========================================================
# METRIC COUNTERS
# =========================================================

@dataclass(slots=True)
class ScannerMetricsSnapshot:

    scan_cycles: int = 0

    successful_cycles: int = 0

    failed_cycles: int = 0

    symbols_processed: int = 0

    signals_generated: int = 0

    signals_accepted: int = 0

    signals_rejected: int = 0

    market_data_requests: int = 0

    market_data_errors: int = 0

    cache_hits: int = 0

    cache_misses: int = 0

    scanner_errors: int = 0

    total_execution_seconds: float = 0.0

    last_execution_seconds: float = 0.0

    started_at: datetime = field(
        default_factory=datetime.now
    )

    updated_at: datetime = field(
        default_factory=datetime.now
    )

    # =====================================================
    # SUCCESS RATE
    # =====================================================

    @property
    def success_rate(
        self,
    ) -> float:

        if self.scan_cycles <= 0:
            return 0.0

        return round(
            self.successful_cycles
            / self.scan_cycles
            * 100.0,
            2,
        )

    # =====================================================
    # ACCEPTANCE RATE
    # =====================================================

    @property
    def acceptance_rate(
        self,
    ) -> float:

        total = (
            self.signals_accepted
            + self.signals_rejected
        )

        if total <= 0:
            return 0.0

        return round(
            self.signals_accepted
            / total
            * 100.0,
            2,
        )

    # =====================================================
    # CACHE HIT RATE
    # =====================================================

    @property
    def cache_hit_rate(
        self,
    ) -> float:

        total = (
            self.cache_hits
            + self.cache_misses
        )

        if total <= 0:
            return 0.0

        return round(
            self.cache_hits
            / total
            * 100.0,
            2,
        )

    # =====================================================
    # AVERAGE EXECUTION TIME
    # =====================================================

    @property
    def average_execution_seconds(
        self,
    ) -> float:

        if self.scan_cycles <= 0:
            return 0.0

        return round(
            self.total_execution_seconds
            / self.scan_cycles,
            6,
        )

    # =====================================================
    # UPTIME
    # =====================================================

    @property
    def uptime_seconds(
        self,
    ) -> float:

        return max(
            0.0,
            (
                datetime.now()
                - self.started_at
            ).total_seconds(),
        )

    # =====================================================
    # SYMBOL THROUGHPUT
    # =====================================================

    @property
    def symbols_per_second(
        self,
    ) -> float:

        if self.total_execution_seconds <= 0:
            return 0.0

        return round(
            self.symbols_processed
            / self.total_execution_seconds,
            2,
        )

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "scan_cycles":
                self.scan_cycles,

            "successful_cycles":
                self.successful_cycles,

            "failed_cycles":
                self.failed_cycles,

            "success_rate":
                self.success_rate,

            "symbols_processed":
                self.symbols_processed,

            "signals_generated":
                self.signals_generated,

            "signals_accepted":
                self.signals_accepted,

            "signals_rejected":
                self.signals_rejected,

            "acceptance_rate":
                self.acceptance_rate,

            "market_data_requests":
                self.market_data_requests,

            "market_data_errors":
                self.market_data_errors,

            "cache_hits":
                self.cache_hits,

            "cache_misses":
                self.cache_misses,

            "cache_hit_rate":
                self.cache_hit_rate,

            "scanner_errors":
                self.scanner_errors,

            "total_execution_seconds":
                round(
                    self.total_execution_seconds,
                    6,
                ),

            "last_execution_seconds":
                round(
                    self.last_execution_seconds,
                    6,
                ),

            "average_execution_seconds":
                self.average_execution_seconds,

            "symbols_per_second":
                self.symbols_per_second,

            "uptime_seconds":
                round(
                    self.uptime_seconds,
                    2,
                ),

            "started_at":
                self.started_at.isoformat(),

            "updated_at":
                self.updated_at.isoformat(),
        }


# =========================================================
# METRICS MANAGER
# =========================================================

class ScannerMetrics:
    """
    Thread-safe global scanner metrics collector.
    """

    def __init__(
        self,
    ) -> None:

        self._lock = RLock()

        self._metrics = (
            ScannerMetricsSnapshot()
        )

    # =====================================================
    # TOUCH
    # =====================================================

    def _touch(
        self,
    ) -> None:

        self._metrics.updated_at = (
            datetime.now()
        )

    # =====================================================
    # SCAN CYCLE
    # =====================================================

    def record_scan_cycle(
        self,
        *,
        success: bool,
        execution_seconds: float = 0.0,
        symbols_processed: int = 0,
        signals_generated: int = 0,
        signals_accepted: int = 0,
        signals_rejected: int = 0,
    ) -> None:

        runtime = max(
            0.0,
            float(execution_seconds),
        )

        with self._lock:

            self._metrics.scan_cycles += 1

            if success:

                self._metrics.successful_cycles += 1

            else:

                self._metrics.failed_cycles += 1

            self._metrics.symbols_processed += max(
                0,
                int(symbols_processed),
            )

            self._metrics.signals_generated += max(
                0,
                int(signals_generated),
            )

            self._metrics.signals_accepted += max(
                0,
                int(signals_accepted),
            )

            self._metrics.signals_rejected += max(
                0,
                int(signals_rejected),
            )

            self._metrics.last_execution_seconds = (
                runtime
            )

            self._metrics.total_execution_seconds += (
                runtime
            )

            self._touch()

    # =====================================================
    # SYMBOLS
    # =====================================================

    def add_symbols(
        self,
        count: int = 1,
    ) -> None:

        with self._lock:

            self._metrics.symbols_processed += max(
                0,
                int(count),
            )

            self._touch()

    # =====================================================
    # GENERATED SIGNALS
    # =====================================================

    def add_generated_signals(
        self,
        count: int = 1,
    ) -> None:

        with self._lock:

            self._metrics.signals_generated += max(
                0,
                int(count),
            )

            self._touch()

    # =====================================================
    # ACCEPTED SIGNALS
    # =====================================================

    def add_accepted_signals(
        self,
        count: int = 1,
    ) -> None:

        with self._lock:

            self._metrics.signals_accepted += max(
                0,
                int(count),
            )

            self._touch()

    # =====================================================
    # REJECTED SIGNALS
    # =====================================================

    def add_rejected_signals(
        self,
        count: int = 1,
    ) -> None:

        with self._lock:

            self._metrics.signals_rejected += max(
                0,
                int(count),
            )

            self._touch()

    # =====================================================
    # MARKET DATA REQUEST
    # =====================================================

    def market_data_request(
        self,
        count: int = 1,
    ) -> None:

        with self._lock:

            self._metrics.market_data_requests += max(
                0,
                int(count),
            )

            self._touch()

    # =====================================================
    # MARKET DATA ERROR
    # =====================================================

    def market_data_error(
        self,
        count: int = 1,
    ) -> None:

        with self._lock:

            self._metrics.market_data_errors += max(
                0,
                int(count),
            )

            self._touch()

    # =====================================================
    # CACHE HIT
    # =====================================================

    def cache_hit(
        self,
        count: int = 1,
    ) -> None:

        with self._lock:

            self._metrics.cache_hits += max(
                0,
                int(count),
            )

            self._touch()

    # =====================================================
    # CACHE MISS
    # =====================================================

    def cache_miss(
        self,
        count: int = 1,
    ) -> None:

        with self._lock:

            self._metrics.cache_misses += max(
                0,
                int(count),
            )

            self._touch()

    # =====================================================
    # SCANNER ERROR
    # =====================================================

    def scanner_error(
        self,
        count: int = 1,
    ) -> None:

        with self._lock:

            self._metrics.scanner_errors += max(
                0,
                int(count),
            )

            self._touch()

    # =====================================================
    # SNAPSHOT
    # =====================================================

    def snapshot(
        self,
    ) -> ScannerMetricsSnapshot:

        with self._lock:

            item = self._metrics

            return ScannerMetricsSnapshot(

                scan_cycles=(
                    item.scan_cycles
                ),

                successful_cycles=(
                    item.successful_cycles
                ),

                failed_cycles=(
                    item.failed_cycles
                ),

                symbols_processed=(
                    item.symbols_processed
                ),

                signals_generated=(
                    item.signals_generated
                ),

                signals_accepted=(
                    item.signals_accepted
                ),

                signals_rejected=(
                    item.signals_rejected
                ),

                market_data_requests=(
                    item.market_data_requests
                ),

                market_data_errors=(
                    item.market_data_errors
                ),

                cache_hits=(
                    item.cache_hits
                ),

                cache_misses=(
                    item.cache_misses
                ),

                scanner_errors=(
                    item.scanner_errors
                ),

                total_execution_seconds=(
                    item.total_execution_seconds
                ),

                last_execution_seconds=(
                    item.last_execution_seconds
                ),

                started_at=(
                    item.started_at
                ),

                updated_at=(
                    item.updated_at
                ),
            )

    # =====================================================
    # REPORT
    # =====================================================

    def report(
        self,
    ) -> Dict[str, Any]:

        return (
            self.snapshot()
            .to_dict()
        )

    # =====================================================
    # RESET
    # =====================================================

    def reset(
        self,
    ) -> None:

        with self._lock:

            self._metrics = (
                ScannerMetricsSnapshot()
            )


# =========================================================
# GLOBAL METRICS
# =========================================================

scanner_metrics = ScannerMetrics()


# =========================================================
# CONVENIENCE FUNCTIONS
# =========================================================

def get_scanner_metrics(
) -> Dict[str, Any]:

    return scanner_metrics.report()


def reset_scanner_metrics(
) -> None:

    scanner_metrics.reset()


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "ScannerMetricsSnapshot",

    "ScannerMetrics",

    "scanner_metrics",

    "get_scanner_metrics",

    "reset_scanner_metrics",
]


# ==========================
# END OF FILE
# ==========================