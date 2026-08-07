"""
=========================================================
StockVersity Scanner Pro
Scanner Orchestrator
Version : 2.0
=========================================================

High-level coordination layer for scanner execution.

Responsibilities
----------------
• Coordinate registered scanners
• Create scanner sessions
• Maintain runtime state
• Execute scanners safely
• Collect scanner results
• Store opportunities
• Track scanner performance
• Publish scanner events
• Handle failures without crashing full scan
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
from typing import Iterable
from typing import List
from typing import Optional

from core.scanner.events import (
    ScannerEventType,
    scanner_events,
)

from core.scanner.performance import (
    scanner_performance,
)

from core.scanner.registry import (
    scanner_registry,
)

from core.scanner.result_store import (
    StoredScannerResult,
    scanner_result_store,
)

from core.scanner.session import (
    ScannerSession,
    scanner_sessions,
)

from core.scanner.state import (
    scanner_state,
)


# =========================================================
# ORCHESTRATOR RESULT
# =========================================================

@dataclass(slots=True)
class ScannerOrchestratorResult:
    """
    Result of one complete orchestrator scan cycle.
    """

    session_id: str = ""

    success: bool = False

    scanner_count: int = 0

    scanners_completed: int = 0

    scanners_failed: int = 0

    symbols_total: int = 0

    results_found: int = 0

    results: List[
        StoredScannerResult
    ] = field(
        default_factory=list
    )

    errors: Dict[
        str,
        str
    ] = field(
        default_factory=dict
    )

    started_at: Optional[
        datetime
    ] = None

    completed_at: Optional[
        datetime
    ] = None

    duration_seconds: float = 0.0

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "session_id":
                self.session_id,

            "success":
                self.success,

            "scanner_count":
                self.scanner_count,

            "scanners_completed":
                self.scanners_completed,

            "scanners_failed":
                self.scanners_failed,

            "symbols_total":
                self.symbols_total,

            "results_found":
                self.results_found,

            "started_at":
                (
                    self.started_at.isoformat()
                    if self.started_at
                    else None
                ),

            "completed_at":
                (
                    self.completed_at.isoformat()
                    if self.completed_at
                    else None
                ),

            "duration_seconds":
                round(
                    self.duration_seconds,
                    6,
                ),

            "errors":
                dict(
                    self.errors
                ),

            "results": [

                result.to_dict()

                for result
                in self.results
            ],
        }


# =========================================================
# SCANNER ORCHESTRATOR
# =========================================================

class ScannerOrchestrator:
    """
    Coordinates complete scanner execution.
    """

    def __init__(
        self,
    ) -> None:

        self._lock = RLock()

        self._running = False

        self._stop_requested = False

        self._last_result: Optional[
            ScannerOrchestratorResult
        ] = None

    # =====================================================
    # SCANNER NAME
    # =====================================================

    @staticmethod
    def _scanner_name(
        scanner: Any,
    ) -> str:

        name = getattr(
            scanner,
            "name",
            None,
        )

        if name:

            return str(
                name
            ).strip()

        return (
            scanner.__class__.__name__
        )

    # =====================================================
    # NORMALIZE SYMBOLS
    # =====================================================

    @staticmethod
    def _normalize_symbols(
        symbols: Optional[
            Iterable[str]
        ],
    ) -> List[str]:

        if symbols is None:

            return []

        output: List[str] = []

        seen = set()

        for symbol in symbols:

            value = str(
                symbol
            ).strip().upper()

            if not value:

                continue

            if value in seen:

                continue

            seen.add(
                value
            )

            output.append(
                value
            )

        return output

    # =====================================================
    # CREATE SCANNERS
    # =====================================================

    def _create_scanners(
        self,
        scanner_names: Optional[
            Iterable[str]
        ] = None,
    ) -> List[Any]:

        if scanner_names is None:

            return (
                scanner_registry
                .create_all()
            )

        scanners: List[Any] = []

        for scanner_name in scanner_names:

            scanner = (
                scanner_registry.create(
                    str(scanner_name)
                )
            )

            if scanner is not None:

                scanners.append(
                    scanner
                )

        return scanners

    # =====================================================
    # CALL SCANNER
    # =====================================================

    @staticmethod
    def _call_scanner(
        scanner: Any,
        symbols: List[str],
        context: Optional[
            Dict[str, Any]
        ],
    ) -> Any:
        """
        Execute scanner using supported scanner interface.

        Preferred scanner interface:

            scanner.scan(
                symbols=symbols,
                context=context
            )

        Fallback interfaces are supported to keep the
        orchestrator compatible with scanner implementations.
        """

        scan_method = getattr(
            scanner,
            "scan",
            None,
        )

        if not callable(
            scan_method
        ):

            raise TypeError(
                (
                    f"{scanner.__class__.__name__} "
                    "does not provide scan()."
                )
            )

        # ---------------------------------------------
        # PRIMARY INTERFACE
        # ---------------------------------------------

        try:

            return scan_method(
                symbols=symbols,
                context=context,
            )

        except TypeError as first_error:

            # -----------------------------------------
            # FALLBACK: scan(symbols)
            # -----------------------------------------

            try:

                return scan_method(
                    symbols
                )

            except TypeError:

                # -------------------------------------
                # FALLBACK: scan()
                # -------------------------------------

                try:

                    return scan_method()

                except TypeError:

                    raise first_error

    # =====================================================
    # NORMALIZE SCANNER OUTPUT
    # =====================================================

    @staticmethod
    def _normalize_output(
        output: Any,
    ) -> List[Any]:

        if output is None:

            return []

        if isinstance(
            output,
            list,
        ):

            return output

        if isinstance(
            output,
            tuple,
        ):

            return list(
                output
            )

        if isinstance(
            output,
            set,
        ):

            return list(
                output
            )

        if isinstance(
            output,
            dict,
        ):

            # A single result dictionary.

            if (
                "symbol" in output
                or "trading_symbol" in output
                or "tradingsymbol" in output
            ):

                return [
                    output
                ]

            # Common wrapper structures.

            for key in (
                "results",
                "signals",
                "opportunities",
                "data",
            ):

                value = output.get(
                    key
                )

                if isinstance(
                    value,
                    (
                        list,
                        tuple,
                        set,
                    ),
                ):

                    return list(
                        value
                    )

            return []

        # Single result object.

        return [
            output
        ]

    # =====================================================
    # EXECUTE ONE SCANNER
    # =====================================================

    def _execute_scanner(
        self,
        scanner: Any,
        symbols: List[str],
        context: Optional[
            Dict[str, Any]
        ],
        session: ScannerSession,
    ) -> List[
        StoredScannerResult
    ]:

        scanner_name = (
            self._scanner_name(
                scanner
            )
        )

        scanner_state.set_scanner(
            scanner_name
        )

        scanner_events.emit(

            ScannerEventType.SCANNER_STARTED,

            source="ScannerOrchestrator",

            scanner_name=scanner_name,

            message=(
                f"{scanner_name} started."
            ),
        )

        timer = (
            scanner_performance.start(
                scanner_name
            )
        )

        started = (
            perf_counter()
        )

        try:

            raw_output = (
                self._call_scanner(
                    scanner,
                    symbols,
                    context,
                )
            )

            raw_results = (
                self._normalize_output(
                    raw_output
                )
            )

            stored_results = (
                scanner_result_store.add_many(
                    raw_results,
                    scanner_name=scanner_name,
                )
            )

            timer.symbols_processed = (
                len(symbols)
            )

            timer.signals_generated = (
                len(raw_results)
            )

            timer.signals_accepted = (
                len(stored_results)
            )

            timer.signals_rejected = max(
                0,
                len(raw_results)
                - len(stored_results),
            )

            scanner_performance.complete(
                timer,
                success=True,
            )

            session.mark_scanner_completed()

            session.mark_signal_generated(
                len(raw_results)
            )

            session.mark_signal_accepted(
                len(stored_results)
            )

            session.mark_signal_rejected(
                max(
                    0,
                    len(raw_results)
                    - len(stored_results),
                )
            )

            scanner_state.scanner_completed()

            scanner_state.signal_found(
                len(stored_results)
            )

            # -----------------------------------------
            # RESULT EVENTS
            # -----------------------------------------

            for result in stored_results:

                scanner_events.emit(

                    ScannerEventType.RESULT_CREATED,

                    source="ScannerOrchestrator",

                    scanner_name=scanner_name,

                    symbol=result.symbol,

                    timeframe=result.timeframe,

                    payload=(
                        result.to_dict()
                    ),
                )

            scanner_events.emit(

                ScannerEventType.SCANNER_COMPLETED,

                source="ScannerOrchestrator",

                scanner_name=scanner_name,

                message=(
                    f"{scanner_name} completed."
                ),

                payload={

                    "runtime_seconds":
                        round(
                            perf_counter()
                            - started,
                            6,
                        ),

                    "results":
                        len(
                            stored_results
                        ),
                },
            )

            return stored_results

        except Exception as exc:

            scanner_performance.complete(
                timer,
                success=False,
                error=exc,
            )

            session.mark_scanner_completed()

            session.add_error(
                (
                    f"{scanner_name}: "
                    f"{type(exc).__name__}: "
                    f"{exc}"
                )
            )

            scanner_state.scanner_completed()

            scanner_events.emit(

                ScannerEventType.SCANNER_FAILED,

                source="ScannerOrchestrator",

                scanner_name=scanner_name,

                message=(
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
            )

            raise

    # =====================================================
    # RUN
    # =====================================================

    def run(
        self,
        symbols: Optional[
            Iterable[str]
        ] = None,
        *,
        scanner_names: Optional[
            Iterable[str]
        ] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
        clear_previous_results: bool = False,
    ) -> ScannerOrchestratorResult:
        """
        Execute one complete scanner cycle.
        """

        with self._lock:

            if self._running:

                raise RuntimeError(
                    "Scanner orchestrator is already running."
                )

            self._running = True

            self._stop_requested = False

        normalized_symbols = (
            self._normalize_symbols(
                symbols
            )
        )

        scanners = (
            self._create_scanners(
                scanner_names
            )
        )

        if clear_previous_results:

            scanner_result_store.clear()

        started_at = (
            datetime.now()
        )

        started_timer = (
            perf_counter()
        )

        result = ScannerOrchestratorResult(

            scanner_count=len(
                scanners
            ),

            symbols_total=len(
                normalized_symbols
            ),

            started_at=started_at,
        )

        session = (
            scanner_sessions.create(

                name="ScannerOrchestrator",

                symbols_total=len(
                    normalized_symbols
                ),

                scanners_total=len(
                    scanners
                ),

                metadata={

                    "scanner_names": [

                        self._scanner_name(
                            scanner
                        )

                        for scanner
                        in scanners
                    ],
                },

                auto_start=True,
            )
        )

        result.session_id = (
            session.session_id
        )

        scanner_state.start(

            session_id=(
                session.session_id
            ),

            symbols_total=len(
                normalized_symbols
            ),

            scanners_total=len(
                scanners
            ),

            message=(
                "Scanner cycle started."
            ),
        )

        scanner_events.emit(

            ScannerEventType.ENGINE_STARTED,

            source="ScannerOrchestrator",

            message=(
                "Scanner cycle started."
            ),

            payload={

                "session_id":
                    session.session_id,

                "symbols":
                    len(
                        normalized_symbols
                    ),

                "scanners":
                    len(
                        scanners
                    ),
            },
        )

        all_results: List[
            StoredScannerResult
        ] = []

        try:

            for scanner in scanners:

                # -------------------------------------
                # STOP REQUEST
                # -------------------------------------

                with self._lock:

                    if self._stop_requested:

                        session.cancel(
                            "Stop requested."
                        )

                        scanner_state.stop(
                            "Scanner stopped by request."
                        )

                        break

                scanner_name = (
                    self._scanner_name(
                        scanner
                    )
                )

                try:

                    scanner_results = (
                        self._execute_scanner(
                            scanner,
                            normalized_symbols,
                            context,
                            session,
                        )
                    )

                    all_results.extend(
                        scanner_results
                    )

                    result.scanners_completed += 1

                except Exception as exc:

                    result.scanners_failed += 1

                    result.errors[
                        scanner_name
                    ] = (
                        f"{type(exc).__name__}: "
                        f"{exc}"
                    )

                    # One scanner failure must not
                    # terminate the complete scan cycle.

                    continue

            # -----------------------------------------
            # SYMBOL SESSION COUNT
            # -----------------------------------------

            session.mark_symbol_processed(
                len(
                    normalized_symbols
                )
            )

            for _ in normalized_symbols:

                scanner_state.symbol_processed()

            # -----------------------------------------
            # RESULTS
            # -----------------------------------------

            result.results = (
                all_results
            )

            result.results_found = (
                len(
                    all_results
                )
            )

            # -----------------------------------------
            # FINAL SESSION STATE
            # -----------------------------------------

            if session.running:

                session.complete()

            result.success = (
                result.scanners_failed == 0
                and session.successful
            )

            if (
                session.status.value
                == "COMPLETED"
            ):

                scanner_state.complete(
                    (
                        f"Scan completed. "
                        f"{len(all_results)} "
                        "opportunities found."
                    )
                )

            scanner_events.emit(

                ScannerEventType.ENGINE_STOPPED,

                source="ScannerOrchestrator",

                message=(
                    "Scanner cycle finished."
                ),

                payload={

                    "session_id":
                        session.session_id,

                    "results":
                        len(
                            all_results
                        ),

                    "failed_scanners":
                        result.scanners_failed,
                },
            )

        except Exception as exc:

            session.fail(
                exc
            )

            scanner_state.error(
                exc
            )

            result.success = False

            result.errors[
                "orchestrator"
            ] = (
                f"{type(exc).__name__}: "
                f"{exc}"
            )

            scanner_events.emit(

                ScannerEventType.ENGINE_ERROR,

                source="ScannerOrchestrator",

                message=(
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
            )

        finally:

            result.completed_at = (
                datetime.now()
            )

            result.duration_seconds = max(
                0.0,
                perf_counter()
                - started_timer,
            )

            with self._lock:

                self._running = False

                self._stop_requested = False

                self._last_result = (
                    result
                )

        return result

    # =====================================================
    # STOP
    # =====================================================

    def stop(
        self,
    ) -> bool:
        """
        Request graceful stop after current scanner.
        """

        with self._lock:

            if not self._running:

                return False

            self._stop_requested = True

            scanner_state.stopping(
                "Scanner stop requested."
            )

            return True

    # =====================================================
    # RUNNING
    # =====================================================

    @property
    def running(
        self,
    ) -> bool:

        with self._lock:

            return self._running

    # =====================================================
    # LAST RESULT
    # =====================================================

    @property
    def last_result(
        self,
    ) -> Optional[
        ScannerOrchestratorResult
    ]:

        with self._lock:

            return self._last_result

    # =====================================================
    # STATUS
    # =====================================================

    def status(
        self,
    ) -> Dict[str, Any]:

        last_result = (
            self.last_result
        )

        return {

            "running":
                self.running,

            "stop_requested":
                self._stop_requested,

            "state":
                scanner_state.status(),

            "active_session":
                (
                    scanner_sessions.active.to_dict()
                    if scanner_sessions.active
                    else None
                ),

            "stored_results":
                len(
                    scanner_result_store
                ),

            "last_result":
                (
                    last_result.to_dict()
                    if last_result
                    else None
                ),
        }


# =========================================================
# GLOBAL ORCHESTRATOR
# =========================================================

scanner_orchestrator = (
    ScannerOrchestrator()
)


# =========================================================
# CONVENIENCE FUNCTIONS
# =========================================================

def run_scanners(
    symbols: Optional[
        Iterable[str]
    ] = None,
    *,
    scanner_names: Optional[
        Iterable[str]
    ] = None,
    context: Optional[
        Dict[str, Any]
    ] = None,
    clear_previous_results: bool = False,
) -> ScannerOrchestratorResult:

    return scanner_orchestrator.run(

        symbols,

        scanner_names=scanner_names,

        context=context,

        clear_previous_results=(
            clear_previous_results
        ),
    )


def stop_scanners(
) -> bool:

    return scanner_orchestrator.stop()


def get_orchestrator_status(
) -> Dict[str, Any]:

    return scanner_orchestrator.status()


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "ScannerOrchestratorResult",

    "ScannerOrchestrator",

    "scanner_orchestrator",

    "run_scanners",

    "stop_scanners",

    "get_orchestrator_status",
]


# ==========================
# END OF FILE
# ==========================