"""
=========================================================
StockVersity Scanner Pro
Scanner Controller
Version : 2.0
=========================================================

High-level scanner control interface.

Responsibilities
----------------
• Provide UI-friendly scanner controls
• Start scanner cycles
• Stop scanner cycles
• Pause / resume scanner scheduling
• Enable / disable scanners
• Manage scanner schedules
• Expose runtime status
• Expose results and diagnostics
=========================================================
"""

from __future__ import annotations

from threading import RLock
from threading import Thread

from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional

from core.scanner.orchestrator import (
    ScannerOrchestratorResult,
    scanner_orchestrator,
)

from core.scanner.registry import (
    scanner_registry,
)

from core.scanner.result_store import (
    scanner_result_store,
)

from core.scanner.scheduler import (
    scanner_scheduler,
)

from core.scanner.session import (
    scanner_sessions,
)

from core.scanner.state import (
    scanner_state,
)

from core.scanner.events import (
    scanner_events,
)

from core.scanner.metrics import (
    scanner_metrics,
)


# =========================================================
# SCANNER CONTROLLER
# =========================================================

class ScannerController:
    """
    Main control interface for scanner subsystem.

    This class is intended to be used by:

        • Dashboard
        • Scanner page
        • Background services
        • Application bootstrap
    """

    def __init__(
        self,
    ) -> None:

        self._lock = RLock()

        self._worker: Optional[
            Thread
        ] = None

        self._last_result: Optional[
            ScannerOrchestratorResult
        ] = None

        self._last_error: str = ""

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
    # START
    # =====================================================

    def start(
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
        background: bool = True,
    ) -> bool:
        """
        Start one scanner cycle.

        background=True
            Run scanner in worker thread.

        background=False
            Run scanner synchronously.
        """

        normalized_symbols = (
            self._normalize_symbols(
                symbols
            )
        )

        with self._lock:

            if self.running:

                return False

            self._last_error = ""

        if background:

            worker = Thread(

                target=self._run_worker,

                kwargs={

                    "symbols":
                        normalized_symbols,

                    "scanner_names":
                        (
                            list(scanner_names)
                            if scanner_names
                            is not None
                            else None
                        ),

                    "context":
                        (
                            dict(context)
                            if context
                            else None
                        ),

                    "clear_previous_results":
                        clear_previous_results,
                },

                name="StockVersityScanner",

                daemon=True,
            )

            with self._lock:

                self._worker = worker

            worker.start()

            return True

        self._run_worker(

            symbols=normalized_symbols,

            scanner_names=(
                list(scanner_names)
                if scanner_names
                is not None
                else None
            ),

            context=(
                dict(context)
                if context
                else None
            ),

            clear_previous_results=(
                clear_previous_results
            ),
        )

        return True

    # =====================================================
    # WORKER
    # =====================================================

    def _run_worker(
        self,
        *,
        symbols: List[str],
        scanner_names: Optional[
            List[str]
        ],
        context: Optional[
            Dict[str, Any]
        ],
        clear_previous_results: bool,
    ) -> None:

        try:

            result = (
                scanner_orchestrator.run(

                    symbols,

                    scanner_names=(
                        scanner_names
                    ),

                    context=context,

                    clear_previous_results=(
                        clear_previous_results
                    ),
                )
            )

            with self._lock:

                self._last_result = (
                    result
                )

        except Exception as exc:

            with self._lock:

                self._last_error = (

                    f"{type(exc).__name__}: "
                    f"{exc}"
                )

        finally:

            with self._lock:

                self._worker = None

    # =====================================================
    # STOP
    # =====================================================

    def stop(
        self,
    ) -> bool:
        """
        Request graceful scanner stop.
        """

        return (
            scanner_orchestrator.stop()
        )

    # =====================================================
    # PAUSE SCHEDULER
    # =====================================================

    def pause(
        self,
    ) -> bool:
        """
        Pause scheduled scans.

        Important:
        This does not interrupt a scanner already executing.
        """

        scheduler_paused = (
            scanner_scheduler.pause()
        )

        if scheduler_paused:

            scanner_state.pause(
                "Scanner scheduling paused."
            )

        return scheduler_paused

    # =====================================================
    # RESUME SCHEDULER
    # =====================================================

    def resume(
        self,
    ) -> bool:

        scheduler_resumed = (
            scanner_scheduler.resume()
        )

        if scheduler_resumed:

            scanner_state.resume(
                "Scanner scheduling resumed."
            )

        return scheduler_resumed

    # =====================================================
    # START SCHEDULER
    # =====================================================

    def start_scheduler(
        self,
    ) -> None:

        scanner_scheduler.start()

    # =====================================================
    # STOP SCHEDULER
    # =====================================================

    def stop_scheduler(
        self,
    ) -> None:

        scanner_scheduler.stop()

    # =====================================================
    # REGISTERED SCANNERS
    # =====================================================

    def scanners(
        self,
    ) -> List[str]:

        return (
            scanner_registry
            .scanner_names
        )

    # =====================================================
    # ENABLED SCANNERS
    # =====================================================

    def enabled_scanners(
        self,
    ) -> List[str]:

        return (
            scanner_registry
            .enabled_names
        )

    # =====================================================
    # DISABLED SCANNERS
    # =====================================================

    def disabled_scanners(
        self,
    ) -> List[str]:

        return (
            scanner_registry
            .disabled_names
        )

    # =====================================================
    # ENABLE SCANNER
    # =====================================================

    def enable_scanner(
        self,
        scanner_name: str,
    ) -> bool:

        registry_result = (
            scanner_registry.enable(
                scanner_name
            )
        )

        if scanner_scheduler.has(
            scanner_name
        ):

            scanner_scheduler.enable(
                scanner_name
            )

        return registry_result

    # =====================================================
    # DISABLE SCANNER
    # =====================================================

    def disable_scanner(
        self,
        scanner_name: str,
    ) -> bool:

        registry_result = (
            scanner_registry.disable(
                scanner_name
            )
        )

        if scanner_scheduler.has(
            scanner_name
        ):

            scanner_scheduler.disable(
                scanner_name
            )

        return registry_result

    # =====================================================
    # ENABLE ALL
    # =====================================================

    def enable_all(
        self,
    ) -> None:

        scanner_registry.enable_all()

        for scanner_name in (
            scanner_registry.scanner_names
        ):

            if scanner_scheduler.has(
                scanner_name
            ):

                scanner_scheduler.enable(
                    scanner_name
                )

    # =====================================================
    # DISABLE ALL
    # =====================================================

    def disable_all(
        self,
    ) -> None:

        scanner_registry.disable_all()

        for scanner_name in (
            scanner_registry.scanner_names
        ):

            if scanner_scheduler.has(
                scanner_name
            ):

                scanner_scheduler.disable(
                    scanner_name
                )

    # =====================================================
    # ADD SCHEDULE
    # =====================================================

    def schedule_scanner(
        self,
        scanner_name: str,
        *,
        interval_seconds: int = 60,
        enabled: bool = True,
        run_immediately: bool = True,
    ) -> bool:

        if not scanner_registry.has(
            scanner_name
        ):

            return False

        scanner_scheduler.add(

            scanner_name,

            interval_seconds=(
                interval_seconds
            ),

            enabled=enabled,

            run_immediately=(
                run_immediately
            ),

            replace=True,
        )

        return True

    # =====================================================
    # REMOVE SCHEDULE
    # =====================================================

    def unschedule_scanner(
        self,
        scanner_name: str,
    ) -> bool:

        return (
            scanner_scheduler.remove(
                scanner_name
            )
        )

    # =====================================================
    # SET INTERVAL
    # =====================================================

    def set_interval(
        self,
        scanner_name: str,
        interval_seconds: int,
    ) -> bool:

        return (
            scanner_scheduler.set_interval(

                scanner_name,

                interval_seconds,
            )
        )

    # =====================================================
    # DUE SCANNERS
    # =====================================================

    def due_scanners(
        self,
    ) -> List[str]:

        return (
            scanner_scheduler
            .due_scanners()
        )

    # =====================================================
    # RUN DUE SCANNERS
    # =====================================================

    def run_due(
        self,
        symbols: Optional[
            Iterable[str]
        ] = None,
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
        background: bool = True,
    ) -> bool:
        """
        Execute scanners currently due according
        to scheduler.
        """

        due = (
            scanner_scheduler
            .due_scanners()
        )

        if not due:

            return False

        if not scanner_scheduler.begin_scan():

            return False

        try:

            started = self.start(

                symbols,

                scanner_names=due,

                context=context,

                background=background,
            )

            if not started:

                return False

            for scanner_name in due:

                scanner_scheduler.mark_executed(
                    scanner_name
                )

            return True

        finally:

            # For synchronous execution the scan is already
            # complete. For background execution the scheduler
            # slot must not remain permanently locked.
            scanner_scheduler.end_scan()

    # =====================================================
    # RESULTS
    # =====================================================

    def results(
        self,
        *,
        limit: Optional[int] = None,
    ) -> List[Any]:

        results = (
            scanner_result_store
            .all()
        )

        if limit is None:

            return results

        limit = max(
            0,
            int(limit),
        )

        return results[
            :limit
        ]

    # =====================================================
    # CLEAR RESULTS
    # =====================================================

    def clear_results(
        self,
    ) -> None:

        scanner_result_store.clear()

    # =====================================================
    # RUNNING
    # =====================================================

    @property
    def running(
        self,
    ) -> bool:

        with self._lock:

            worker_running = (

                self._worker is not None

                and self._worker.is_alive()
            )

        return (

            worker_running

            or scanner_orchestrator.running
        )

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

        last_result = (
            self.last_result
        )

        active_session = (
            scanner_sessions.active
        )

        return {

            "running":
                self.running,

            "registered_scanners":
                scanner_registry.scanner_names,

            "enabled_scanners":
                scanner_registry.enabled_names,

            "disabled_scanners":
                scanner_registry.disabled_names,

            "registry":
                scanner_registry.status(),

            "runtime":
                scanner_state.status(),

            "scheduler":
                scanner_scheduler.report(),

            "orchestrator":
                scanner_orchestrator.status(),

            "metrics":
                scanner_metrics.report(),

            "events":
                scanner_events.status(),

            "result_count":
                len(
                    scanner_result_store
                ),

            "active_session":
                (
                    active_session.to_dict()
                    if active_session
                    else None
                ),

            "last_error":
                self.last_error,

            "last_result":
                (
                    last_result.to_dict()
                    if last_result
                    else None
                ),
        }

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(
        self,
    ) -> Dict[str, Any]:

        issues: List[str] = []

        registry_health = (
            scanner_registry
            .health_check()
        )

        if not registry_health[
            "healthy"
        ]:

            issues.extend(
                registry_health[
                    "issues"
                ]
            )

        if self.last_error:

            issues.append(
                self.last_error
            )

        event_errors = (
            scanner_events.errors
        )

        if event_errors:

            issues.append(
                (
                    f"Event bus contains "
                    f"{len(event_errors)} error(s)."
                )
            )

        return {

            "healthy":
                len(issues) == 0,

            "running":
                self.running,

            "issues":
                issues,

            "registered":
                len(
                    scanner_registry
                ),

            "enabled":
                len(
                    scanner_registry
                    .enabled_names
                ),

            "stored_results":
                len(
                    scanner_result_store
                ),
        }


# =========================================================
# GLOBAL CONTROLLER
# =========================================================

scanner_controller = (
    ScannerController()
)


# =========================================================
# CONVENIENCE FUNCTIONS
# =========================================================

def start_scanner(
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
    background: bool = True,
) -> bool:

    return scanner_controller.start(

        symbols,

        scanner_names=scanner_names,

        context=context,

        background=background,
    )


def stop_scanner(
) -> bool:

    return scanner_controller.stop()


def get_scanner_controller_status(
) -> Dict[str, Any]:

    return scanner_controller.status()


def get_scanner_health(
) -> Dict[str, Any]:

    return scanner_controller.health_check()


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "ScannerController",

    "scanner_controller",

    "start_scanner",

    "stop_scanner",

    "get_scanner_controller_status",

    "get_scanner_health",
]


# ==========================
# END OF FILE
# ==========================