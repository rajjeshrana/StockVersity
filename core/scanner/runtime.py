"""
=========================================================
StockVersity Scanner Pro
Scanner Runtime
Version : 2.0
=========================================================

Background runtime loop for scanner subsystem.

Responsibilities
----------------
• Run scanner scheduler continuously
• Check scanners that are due
• Trigger scheduled scanner cycles
• Prevent duplicate runtime threads
• Support start / stop / pause / resume
• Provide symbols dynamically
• Provide scan context dynamically
• Track runtime statistics
• Handle runtime errors safely
=========================================================
"""

from __future__ import annotations

from datetime import datetime

from threading import Event
from threading import RLock
from threading import Thread
from threading import current_thread

from time import monotonic

from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional

from core.scanner.controller import (
    scanner_controller,
)

from core.scanner.scheduler import (
    scanner_scheduler,
)


# =========================================================
# TYPE ALIASES
# =========================================================

SymbolProvider = Callable[
    [],
    Iterable[str],
]

ContextProvider = Callable[
    [],
    Optional[
        Dict[str, Any]
    ],
]


# =========================================================
# SCANNER RUNTIME
# =========================================================

class ScannerRuntime:
    """
    Continuous background runtime for scheduled scanners.

    Important
    ---------
    This class does not contain scanner logic.

    It only:

        1. checks scheduler
        2. finds due scanners
        3. obtains symbols
        4. triggers scanner controller
        5. updates schedules

    Actual scanning remains inside the orchestrator and
    scanner implementations.
    """

    def __init__(
        self,
        *,
        poll_interval_seconds: float = 1.0,
    ) -> None:

        self.poll_interval_seconds = max(
            0.10,
            float(
                poll_interval_seconds
            ),
        )

        self._lock = RLock()

        self._stop_event = Event()

        self._wake_event = Event()

        self._thread: Optional[
            Thread
        ] = None

        self._symbol_provider: Optional[
            SymbolProvider
        ] = None

        self._context_provider: Optional[
            ContextProvider
        ] = None

        self._static_symbols: List[
            str
        ] = []

        self._static_context: Dict[
            str,
            Any
        ] = {}

        self._paused = False

        self._started_at: Optional[
            datetime
        ] = None

        self._stopped_at: Optional[
            datetime
        ] = None

        self._last_cycle_at: Optional[
            datetime
        ] = None

        self._last_error: str = ""

        self._loop_count = 0

        self._trigger_count = 0

        self._error_count = 0

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

            value = (
                str(symbol)
                .strip()
                .upper()
            )

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
    # SET SYMBOLS
    # =====================================================

    def set_symbols(
        self,
        symbols: Optional[
            Iterable[str]
        ],
    ) -> None:
        """
        Set static symbols used by scheduled scans.
        """

        normalized = (
            self._normalize_symbols(
                symbols
            )
        )

        with self._lock:

            self._static_symbols = (
                normalized
            )

        self.wake()

    # =====================================================
    # GET SYMBOLS
    # =====================================================

    def get_symbols(
        self,
    ) -> List[str]:

        with self._lock:

            provider = (
                self._symbol_provider
            )

            static_symbols = list(
                self._static_symbols
            )

        if provider is None:

            return static_symbols

        try:

            symbols = provider()

            return (
                self._normalize_symbols(
                    symbols
                )
            )

        except Exception as exc:

            self._record_error(
                exc
            )

            return static_symbols

    # =====================================================
    # SET SYMBOL PROVIDER
    # =====================================================

    def set_symbol_provider(
        self,
        provider: Optional[
            SymbolProvider
        ],
    ) -> None:
        """
        Set callable used to dynamically obtain symbols.

        Example:

            runtime.set_symbol_provider(
                universe_service.get_symbols
            )
        """

        if (
            provider is not None
            and not callable(provider)
        ):

            raise TypeError(
                "Symbol provider must be callable."
            )

        with self._lock:

            self._symbol_provider = (
                provider
            )

        self.wake()

    # =====================================================
    # SET CONTEXT
    # =====================================================

    def set_context(
        self,
        context: Optional[
            Dict[str, Any]
        ],
    ) -> None:

        with self._lock:

            self._static_context = (
                dict(context)
                if context
                else {}
            )

        self.wake()

    # =====================================================
    # GET CONTEXT
    # =====================================================

    def get_context(
        self,
    ) -> Dict[str, Any]:

        with self._lock:

            provider = (
                self._context_provider
            )

            static_context = dict(
                self._static_context
            )

        if provider is None:

            return static_context

        try:

            dynamic_context = (
                provider()
            )

            if not dynamic_context:

                return static_context

            merged = dict(
                static_context
            )

            merged.update(
                dynamic_context
            )

            return merged

        except Exception as exc:

            self._record_error(
                exc
            )

            return static_context

    # =====================================================
    # SET CONTEXT PROVIDER
    # =====================================================

    def set_context_provider(
        self,
        provider: Optional[
            ContextProvider
        ],
    ) -> None:

        if (
            provider is not None
            and not callable(provider)
        ):

            raise TypeError(
                "Context provider must be callable."
            )

        with self._lock:

            self._context_provider = (
                provider
            )

        self.wake()

    # =====================================================
    # RECORD ERROR
    # =====================================================

    def _record_error(
        self,
        exc: BaseException,
    ) -> None:

        with self._lock:

            self._error_count += 1

            self._last_error = (
                f"{type(exc).__name__}: "
                f"{exc}"
            )

    # =====================================================
    # START
    # =====================================================

    def start(
        self,
        *,
        symbols: Optional[
            Iterable[str]
        ] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
        start_scheduler: bool = True,
    ) -> bool:
        """
        Start background scanner runtime.
        """

        with self._lock:

            if (
                self._thread is not None
                and self._thread.is_alive()
            ):

                return True

        if symbols is not None:

            self.set_symbols(
                symbols
            )

        if context is not None:

            self.set_context(
                context
            )

        if start_scheduler:

            scanner_scheduler.start()

        self._stop_event.clear()

        self._wake_event.clear()

        with self._lock:

            self._paused = False

            self._last_error = ""

            self._started_at = (
                datetime.now()
            )

            self._stopped_at = None

            thread = Thread(

                target=self._run_loop,

                name=(
                    "StockVersityScannerRuntime"
                ),

                daemon=True,
            )

            self._thread = thread

        thread.start()

        return True

    # =====================================================
    # STOP
    # =====================================================

    def stop(
        self,
        *,
        stop_scheduler: bool = True,
        stop_active_scan: bool = True,
        wait: bool = False,
        timeout: Optional[float] = 5.0,
    ) -> bool:
        """
        Stop runtime loop.

        The active scanner can optionally receive a graceful
        stop request.
        """

        with self._lock:

            thread = (
                self._thread
            )

        if (
            thread is None
            or not thread.is_alive()
        ):

            if stop_scheduler:

                scanner_scheduler.stop()

            return True

        self._stop_event.set()

        self._wake_event.set()

        if (
            stop_active_scan
            and scanner_controller.running
        ):

            scanner_controller.stop()

        if stop_scheduler:

            scanner_scheduler.stop()

        if (
            wait
            and thread is not current_thread()
        ):

            thread.join(
                timeout=timeout
            )

        return True

    # =====================================================
    # PAUSE
    # =====================================================

    def pause(
        self,
    ) -> bool:

        with self._lock:

            if (
                self._thread is None
                or not self._thread.is_alive()
            ):

                return False

            if self._paused:

                return True

            self._paused = True

        scanner_scheduler.pause()

        self.wake()

        return True

    # =====================================================
    # RESUME
    # =====================================================

    def resume(
        self,
    ) -> bool:

        with self._lock:

            if (
                self._thread is None
                or not self._thread.is_alive()
            ):

                return False

            if not self._paused:

                return True

            self._paused = False

        scanner_scheduler.resume()

        self.wake()

        return True

    # =====================================================
    # WAKE
    # =====================================================

    def wake(
        self,
    ) -> None:
        """
        Wake runtime loop immediately.
        """

        self._wake_event.set()

    # =====================================================
    # PROCESS DUE SCANNERS
    # =====================================================

    def process_due_scanners(
        self,
    ) -> bool:
        """
        Execute scanners currently due.

        Returns True when a scan was triggered.
        """

        if scanner_controller.running:

            return False

        due_scanners = (
            scanner_scheduler
            .due_scanners()
        )

        if not due_scanners:

            return False

        symbols = (
            self.get_symbols()
        )

        context = (
            self.get_context()
        )

        # ---------------------------------------------
        # ACQUIRE SCHEDULER SLOT
        # ---------------------------------------------

        if not scanner_scheduler.begin_scan():

            return False

        try:

            started = (
                scanner_controller.start(

                    symbols,

                    scanner_names=(
                        due_scanners
                    ),

                    context=context,

                    background=False,
                )
            )

            if not started:

                for scanner_name in (
                    due_scanners
                ):

                    scanner_scheduler.mark_skipped(
                        scanner_name
                    )

                return False

            # -----------------------------------------
            # MARK SCHEDULES COMPLETE
            # -----------------------------------------

            for scanner_name in (
                due_scanners
            ):

                scanner_scheduler.mark_executed(
                    scanner_name
                )

            with self._lock:

                self._trigger_count += 1

                self._last_cycle_at = (
                    datetime.now()
                )

            return True

        except Exception as exc:

            self._record_error(
                exc
            )

            for scanner_name in (
                due_scanners
            ):

                try:

                    scanner_scheduler.mark_skipped(
                        scanner_name
                    )

                except Exception:

                    pass

            return False

        finally:

            scanner_scheduler.end_scan()

    # =====================================================
    # RUNTIME LOOP
    # =====================================================

    def _run_loop(
        self,
    ) -> None:
        """
        Main scheduler runtime loop.
        """

        try:

            while not self._stop_event.is_set():

                loop_started = (
                    monotonic()
                )

                with self._lock:

                    self._loop_count += 1

                    paused = (
                        self._paused
                    )

                if not paused:

                    try:

                        self.process_due_scanners()

                    except Exception as exc:

                        self._record_error(
                            exc
                        )

                # -------------------------------------
                # CALCULATE WAIT
                # -------------------------------------

                elapsed = max(
                    0.0,
                    monotonic()
                    - loop_started,
                )

                wait_seconds = max(
                    0.05,
                    (
                        self.poll_interval_seconds
                        - elapsed
                    ),
                )

                self._wake_event.wait(
                    timeout=wait_seconds
                )

                self._wake_event.clear()

        except Exception as exc:

            self._record_error(
                exc
            )

        finally:

            with self._lock:

                self._stopped_at = (
                    datetime.now()
                )

                self._paused = False

                self._thread = None

    # =====================================================
    # RUNNING
    # =====================================================

    @property
    def running(
        self,
    ) -> bool:

        with self._lock:

            return (

                self._thread is not None

                and self._thread.is_alive()
            )

    # =====================================================
    # PAUSED
    # =====================================================

    @property
    def paused(
        self,
    ) -> bool:

        with self._lock:

            return self._paused

    # =====================================================
    # LAST ERROR
    # =====================================================

    @property
    def last_error(
        self,
    ) -> str:

        with self._lock:

            return self._last_error

    # =====================================================
    # STATUS
    # =====================================================

    def status(
        self,
    ) -> Dict[str, Any]:

        with self._lock:

            thread_running = (

                self._thread is not None

                and self._thread.is_alive()
            )

            paused = (
                self._paused
            )

            symbol_count = len(
                self._static_symbols
            )

            has_symbol_provider = (
                self._symbol_provider
                is not None
            )

            has_context_provider = (
                self._context_provider
                is not None
            )

            loop_count = (
                self._loop_count
            )

            trigger_count = (
                self._trigger_count
            )

            error_count = (
                self._error_count
            )

            last_error = (
                self._last_error
            )

            started_at = (
                self._started_at
            )

            stopped_at = (
                self._stopped_at
            )

            last_cycle_at = (
                self._last_cycle_at
            )

        return {

            "running":
                thread_running,

            "paused":
                paused,

            "poll_interval_seconds":
                self.poll_interval_seconds,

            "static_symbol_count":
                symbol_count,

            "has_symbol_provider":
                has_symbol_provider,

            "has_context_provider":
                has_context_provider,

            "loop_count":
                loop_count,

            "trigger_count":
                trigger_count,

            "error_count":
                error_count,

            "last_error":
                last_error,

            "started_at":
                (
                    started_at.isoformat()
                    if started_at
                    else None
                ),

            "stopped_at":
                (
                    stopped_at.isoformat()
                    if stopped_at
                    else None
                ),

            "last_cycle_at":
                (
                    last_cycle_at.isoformat()
                    if last_cycle_at
                    else None
                ),

            "scheduler":
                scanner_scheduler.report(),
        }

    # =====================================================
    # RESET STATISTICS
    # =====================================================

    def reset_statistics(
        self,
    ) -> bool:

        if self.running:

            return False

        with self._lock:

            self._started_at = None

            self._stopped_at = None

            self._last_cycle_at = None

            self._last_error = ""

            self._loop_count = 0

            self._trigger_count = 0

            self._error_count = 0

        return True


# =========================================================
# GLOBAL RUNTIME
# =========================================================

scanner_runtime = ScannerRuntime(
    poll_interval_seconds=1.0
)


# =========================================================
# CONVENIENCE FUNCTIONS
# =========================================================

def start_scanner_runtime(
    *,
    symbols: Optional[
        Iterable[str]
    ] = None,
    context: Optional[
        Dict[str, Any]
    ] = None,
) -> bool:

    return scanner_runtime.start(

        symbols=symbols,

        context=context,
    )


def stop_scanner_runtime(
    *,
    wait: bool = False,
) -> bool:

    return scanner_runtime.stop(
        wait=wait
    )


def pause_scanner_runtime(
) -> bool:

    return scanner_runtime.pause()


def resume_scanner_runtime(
) -> bool:

    return scanner_runtime.resume()


def get_scanner_runtime_status(
) -> Dict[str, Any]:

    return scanner_runtime.status()


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "SymbolProvider",

    "ContextProvider",

    "ScannerRuntime",

    "scanner_runtime",

    "start_scanner_runtime",

    "stop_scanner_runtime",

    "pause_scanner_runtime",

    "resume_scanner_runtime",

    "get_scanner_runtime_status",
]


# ==========================
# END OF FILE
# ==========================