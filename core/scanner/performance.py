"""
=========================================================
StockVersity Scanner Pro
Scanner Performance Monitor
Version : 2.0
=========================================================

Runtime performance monitoring for scanner components.

Responsibilities
----------------
• Track scanner execution count
• Track execution time
• Track generated signals
• Track accepted / rejected signals
• Track scanner errors
• Track symbols processed
• Calculate success rate
• Calculate average runtime
• Maintain per-scanner statistics
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from threading import RLock

from time import perf_counter

from typing import Any
from typing import Dict
from typing import List
from typing import Optional


# =========================================================
# SCANNER PERFORMANCE RECORD
# =========================================================

@dataclass(slots=True)
class ScannerPerformanceRecord:
    """
    Runtime statistics for one scanner.
    """

    scanner_name: str

    runs: int = 0

    successful_runs: int = 0

    failed_runs: int = 0

    symbols_processed: int = 0

    signals_generated: int = 0

    signals_accepted: int = 0

    signals_rejected: int = 0

    total_runtime_seconds: float = 0.0

    fastest_runtime_seconds: float = 0.0

    slowest_runtime_seconds: float = 0.0

    last_runtime_seconds: float = 0.0

    last_run_at: Optional[datetime] = None

    last_success_at: Optional[datetime] = None

    last_error_at: Optional[datetime] = None

    last_error: Optional[str] = None

    errors: List[str] = field(
        default_factory=list
    )

    # =====================================================
    # AVERAGE RUNTIME
    # =====================================================

    @property
    def average_runtime_seconds(
        self,
    ) -> float:

        if self.runs <= 0:

            return 0.0

        return round(
            self.total_runtime_seconds
            / self.runs,
            6,
        )

    # =====================================================
    # SUCCESS RATE
    # =====================================================

    @property
    def success_rate(
        self,
    ) -> float:

        if self.runs <= 0:

            return 0.0

        return round(
            self.successful_runs
            / self.runs
            * 100.0,
            2,
        )

    # =====================================================
    # SIGNAL ACCEPTANCE RATE
    # =====================================================

    @property
    def signal_acceptance_rate(
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
    # ERROR RATE
    # =====================================================

    @property
    def error_rate(
        self,
    ) -> float:

        if self.runs <= 0:

            return 0.0

        return round(
            self.failed_runs
            / self.runs
            * 100.0,
            2,
        )

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "scanner_name":
                self.scanner_name,

            "runs":
                self.runs,

            "successful_runs":
                self.successful_runs,

            "failed_runs":
                self.failed_runs,

            "symbols_processed":
                self.symbols_processed,

            "signals_generated":
                self.signals_generated,

            "signals_accepted":
                self.signals_accepted,

            "signals_rejected":
                self.signals_rejected,

            "success_rate":
                self.success_rate,

            "error_rate":
                self.error_rate,

            "signal_acceptance_rate":
                self.signal_acceptance_rate,

            "total_runtime_seconds":
                round(
                    self.total_runtime_seconds,
                    6,
                ),

            "average_runtime_seconds":
                self.average_runtime_seconds,

            "fastest_runtime_seconds":
                round(
                    self.fastest_runtime_seconds,
                    6,
                ),

            "slowest_runtime_seconds":
                round(
                    self.slowest_runtime_seconds,
                    6,
                ),

            "last_runtime_seconds":
                round(
                    self.last_runtime_seconds,
                    6,
                ),

            "last_run_at":
                (
                    self.last_run_at.isoformat()
                    if self.last_run_at
                    else None
                ),

            "last_success_at":
                (
                    self.last_success_at.isoformat()
                    if self.last_success_at
                    else None
                ),

            "last_error_at":
                (
                    self.last_error_at.isoformat()
                    if self.last_error_at
                    else None
                ),

            "last_error":
                self.last_error,

            "errors":
                list(
                    self.errors
                ),
        }


# =========================================================
# RUN TIMER
# =========================================================

@dataclass(slots=True)
class ScannerRunTimer:
    """
    Temporary timer used for one scanner execution.
    """

    scanner_name: str

    started_at: float = field(
        default_factory=perf_counter
    )

    symbols_processed: int = 0

    signals_generated: int = 0

    signals_accepted: int = 0

    signals_rejected: int = 0

    finished: bool = False

    # =====================================================
    # ELAPSED
    # =====================================================

    @property
    def elapsed(
        self,
    ) -> float:

        return max(
            0.0,
            perf_counter()
            - self.started_at,
        )


# =========================================================
# PERFORMANCE MONITOR
# =========================================================

class ScannerPerformanceMonitor:
    """
    Central performance monitor for all scanners.
    """

    def __init__(
        self,
        *,
        maximum_errors_per_scanner: int = 50,
    ) -> None:

        self.maximum_errors_per_scanner = max(
            1,
            int(
                maximum_errors_per_scanner
            ),
        )

        self._records: Dict[
            str,
            ScannerPerformanceRecord
        ] = {}

        self._lock = RLock()

    # =====================================================
    # NORMALIZE NAME
    # =====================================================

    @staticmethod
    def _normalize_name(
        scanner_name: str,
    ) -> str:

        return (
            str(scanner_name)
            .strip()
        )

    # =====================================================
    # GET / CREATE RECORD
    # =====================================================

    def _record(
        self,
        scanner_name: str,
    ) -> ScannerPerformanceRecord:

        name = self._normalize_name(
            scanner_name
        )

        if not name:

            name = "UnknownScanner"

        if name not in self._records:

            self._records[
                name
            ] = ScannerPerformanceRecord(
                scanner_name=name
            )

        return self._records[
            name
        ]

    # =====================================================
    # START RUN
    # =====================================================

    def start(
        self,
        scanner_name: str,
    ) -> ScannerRunTimer:
        """
        Start scanner execution timer.
        """

        return ScannerRunTimer(
            scanner_name=self._normalize_name(
                scanner_name
            )
        )

    # =====================================================
    # COMPLETE RUN
    # =====================================================

    def complete(
        self,
        timer: ScannerRunTimer,
        *,
        success: bool = True,
        error: Optional[
            BaseException | str
        ] = None,
    ) -> float:
        """
        Complete scanner execution and update metrics.
        """

        if timer.finished:

            return timer.elapsed

        runtime = timer.elapsed

        timer.finished = True

        now = datetime.now()

        with self._lock:

            record = self._record(
                timer.scanner_name
            )

            record.runs += 1

            record.last_run_at = now

            record.last_runtime_seconds = (
                runtime
            )

            record.total_runtime_seconds += (
                runtime
            )

            record.symbols_processed += (
                timer.symbols_processed
            )

            record.signals_generated += (
                timer.signals_generated
            )

            record.signals_accepted += (
                timer.signals_accepted
            )

            record.signals_rejected += (
                timer.signals_rejected
            )

            # -----------------------------------------
            # FASTEST
            # -----------------------------------------

            if (
                record.fastest_runtime_seconds
                <= 0
                or runtime
                < record.fastest_runtime_seconds
            ):

                record.fastest_runtime_seconds = (
                    runtime
                )

            # -----------------------------------------
            # SLOWEST
            # -----------------------------------------

            if (
                runtime
                > record.slowest_runtime_seconds
            ):

                record.slowest_runtime_seconds = (
                    runtime
                )

            # -----------------------------------------
            # SUCCESS
            # -----------------------------------------

            if success and error is None:

                record.successful_runs += 1

                record.last_success_at = now

            else:

                record.failed_runs += 1

                record.last_error_at = now

                if error is not None:

                    message = (
                        f"{type(error).__name__}: {error}"
                        if isinstance(
                            error,
                            BaseException,
                        )
                        else str(error)
                    )

                    record.last_error = message

                    record.errors.append(
                        message
                    )

                    if (
                        len(record.errors)
                        > self.maximum_errors_per_scanner
                    ):

                        record.errors = (
                            record.errors[
                                -self.maximum_errors_per_scanner:
                            ]
                        )

        return runtime

    # =====================================================
    # RECORD RUN DIRECTLY
    # =====================================================

    def record_run(
        self,
        scanner_name: str,
        runtime_seconds: float,
        *,
        success: bool = True,
        symbols_processed: int = 0,
        signals_generated: int = 0,
        signals_accepted: int = 0,
        signals_rejected: int = 0,
        error: Optional[
            BaseException | str
        ] = None,
    ) -> None:
        """
        Record execution when caller already knows runtime.
        """

        runtime = max(
            0.0,
            float(runtime_seconds),
        )

        now = datetime.now()

        with self._lock:

            record = self._record(
                scanner_name
            )

            record.runs += 1

            record.last_run_at = now

            record.last_runtime_seconds = (
                runtime
            )

            record.total_runtime_seconds += (
                runtime
            )

            record.symbols_processed += max(
                0,
                int(symbols_processed),
            )

            record.signals_generated += max(
                0,
                int(signals_generated),
            )

            record.signals_accepted += max(
                0,
                int(signals_accepted),
            )

            record.signals_rejected += max(
                0,
                int(signals_rejected),
            )

            if (
                record.fastest_runtime_seconds
                <= 0
                or runtime
                < record.fastest_runtime_seconds
            ):

                record.fastest_runtime_seconds = (
                    runtime
                )

            if (
                runtime
                > record.slowest_runtime_seconds
            ):

                record.slowest_runtime_seconds = (
                    runtime
                )

            if success and error is None:

                record.successful_runs += 1

                record.last_success_at = now

            else:

                record.failed_runs += 1

                record.last_error_at = now

                if error is not None:

                    message = (
                        f"{type(error).__name__}: {error}"
                        if isinstance(
                            error,
                            BaseException,
                        )
                        else str(error)
                    )

                    record.last_error = message

                    record.errors.append(
                        message
                    )

                    if (
                        len(record.errors)
                        > self.maximum_errors_per_scanner
                    ):

                        record.errors = (
                            record.errors[
                                -self.maximum_errors_per_scanner:
                            ]
                        )

    # =====================================================
    # SYMBOL COUNT
    # =====================================================

    def add_symbols(
        self,
        scanner_name: str,
        count: int = 1,
    ) -> None:

        with self._lock:

            self._record(
                scanner_name
            ).symbols_processed += max(
                0,
                int(count),
            )

    # =====================================================
    # GENERATED SIGNAL
    # =====================================================

    def add_generated(
        self,
        scanner_name: str,
        count: int = 1,
    ) -> None:

        with self._lock:

            self._record(
                scanner_name
            ).signals_generated += max(
                0,
                int(count),
            )

    # =====================================================
    # ACCEPTED SIGNAL
    # =====================================================

    def add_accepted(
        self,
        scanner_name: str,
        count: int = 1,
    ) -> None:

        with self._lock:

            self._record(
                scanner_name
            ).signals_accepted += max(
                0,
                int(count),
            )

    # =====================================================
    # REJECTED SIGNAL
    # =====================================================

    def add_rejected(
        self,
        scanner_name: str,
        count: int = 1,
    ) -> None:

        with self._lock:

            self._record(
                scanner_name
            ).signals_rejected += max(
                0,
                int(count),
            )

    # =====================================================
    # GET RECORD
    # =====================================================

    def get(
        self,
        scanner_name: str,
    ) -> Optional[
        ScannerPerformanceRecord
    ]:

        name = self._normalize_name(
            scanner_name
        )

        with self._lock:

            return self._records.get(
                name
            )

    # =====================================================
    # REPORT
    # =====================================================

    def report(
        self,
        scanner_name: str,
    ) -> Dict[str, Any]:

        record = self.get(
            scanner_name
        )

        if record is None:

            return {}

        return record.to_dict()

    # =====================================================
    # ALL REPORTS
    # =====================================================

    def reports(
        self,
    ) -> Dict[
        str,
        Dict[str, Any]
    ]:

        with self._lock:

            return {

                name:
                    record.to_dict()

                for name, record
                in self._records.items()
            }

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> Dict[str, Any]:

        with self._lock:

            records = list(
                self._records.values()
            )

            total_runs = sum(
                record.runs
                for record in records
            )

            successful_runs = sum(
                record.successful_runs
                for record in records
            )

            failed_runs = sum(
                record.failed_runs
                for record in records
            )

            symbols = sum(
                record.symbols_processed
                for record in records
            )

            generated = sum(
                record.signals_generated
                for record in records
            )

            accepted = sum(
                record.signals_accepted
                for record in records
            )

            rejected = sum(
                record.signals_rejected
                for record in records
            )

            runtime = sum(
                record.total_runtime_seconds
                for record in records
            )

            success_rate = (
                successful_runs
                / total_runs
                * 100.0
                if total_runs > 0
                else 0.0
            )

            acceptance_total = (
                accepted
                + rejected
            )

            acceptance_rate = (
                accepted
                / acceptance_total
                * 100.0
                if acceptance_total > 0
                else 0.0
            )

            return {

                "scanners":
                    len(records),

                "total_runs":
                    total_runs,

                "successful_runs":
                    successful_runs,

                "failed_runs":
                    failed_runs,

                "success_rate":
                    round(
                        success_rate,
                        2,
                    ),

                "symbols_processed":
                    symbols,

                "signals_generated":
                    generated,

                "signals_accepted":
                    accepted,

                "signals_rejected":
                    rejected,

                "signal_acceptance_rate":
                    round(
                        acceptance_rate,
                        2,
                    ),

                "total_runtime_seconds":
                    round(
                        runtime,
                        6,
                    ),
            }

    # =====================================================
    # RESET SCANNER
    # =====================================================

    def reset(
        self,
        scanner_name: str,
    ) -> bool:

        name = self._normalize_name(
            scanner_name
        )

        with self._lock:

            if name not in self._records:

                return False

            del self._records[
                name
            ]

            return True

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(
        self,
    ) -> None:

        with self._lock:

            self._records.clear()

    # =====================================================
    # NAMES
    # =====================================================

    @property
    def scanner_names(
        self,
    ) -> List[str]:

        with self._lock:

            return sorted(
                self._records.keys()
            )

    # =====================================================
    # LENGTH
    # =====================================================

    def __len__(
        self,
    ) -> int:

        with self._lock:

            return len(
                self._records
            )


# =========================================================
# GLOBAL PERFORMANCE MONITOR
# =========================================================

scanner_performance = (
    ScannerPerformanceMonitor()
)


# =========================================================
# CONVENIENCE FUNCTIONS
# =========================================================

def start_scanner_timer(
    scanner_name: str,
) -> ScannerRunTimer:

    return scanner_performance.start(
        scanner_name
    )


def complete_scanner_timer(
    timer: ScannerRunTimer,
    *,
    success: bool = True,
    error: Optional[
        BaseException | str
    ] = None,
) -> float:

    return scanner_performance.complete(
        timer,
        success=success,
        error=error,
    )


def scanner_performance_report(
    scanner_name: str,
) -> Dict[str, Any]:

    return scanner_performance.report(
        scanner_name
    )


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "ScannerPerformanceRecord",

    "ScannerRunTimer",

    "ScannerPerformanceMonitor",

    "scanner_performance",

    "start_scanner_timer",

    "complete_scanner_timer",

    "scanner_performance_report",
]


# ==========================
# END OF FILE
# ==========================