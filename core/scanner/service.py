"""
=========================================================
StockVersity Scanner Pro
Scanner Service
Version : 2.0
=========================================================

Public service layer for scanner subsystem.

Responsibilities
----------------
• Provide one scanner API for the application
• Initialize scanner subsystem
• Start / stop scanning
• Pause / resume scheduler
• Run selected scanners
• Manage scanner enable / disable state
• Access scanner results
• Access health and diagnostics
• Expose dashboard-ready status
=========================================================
"""

from __future__ import annotations

from threading import RLock

from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional

from core.scanner.controller import (
    scanner_controller,
)

from core.scanner.diagnostics import (
    scanner_diagnostics,
)

from core.scanner.health import (
    scanner_health,
)

from core.scanner.lifecycle import (
    scanner_lifecycle,
)

from core.scanner.metrics import (
    scanner_metrics,
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


# =========================================================
# SCANNER SERVICE
# =========================================================

class ScannerService:
    """
    Public application-facing scanner service.

    UI and application modules should prefer using this
    service instead of directly controlling scanner
    subsystem components.
    """

    def __init__(
        self,
    ) -> None:

        self._lock = RLock()

    # =====================================================
    # INITIALIZE
    # =====================================================

    def initialize(
        self,
        *,
        default_interval_seconds: int = 60,
        force: bool = False,
    ) -> bool:
        """
        Initialize scanner subsystem.
        """

        return scanner_lifecycle.initialize(

            default_interval_seconds=(
                default_interval_seconds
            ),

            force=force,
        )

    # =====================================================
    # START SYSTEM
    # =====================================================

    def start_system(
        self,
    ) -> bool:
        """
        Start scanner subsystem scheduler/services.
        """

        return scanner_lifecycle.start()

    # =====================================================
    # STOP SYSTEM
    # =====================================================

    def stop_system(
        self,
    ) -> bool:
        """
        Stop scanner subsystem.
        """

        return scanner_lifecycle.stop()

    # =====================================================
    # RESTART SYSTEM
    # =====================================================

    def restart_system(
        self,
    ) -> bool:

        return scanner_lifecycle.restart()

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(
        self,
    ) -> bool:

        return scanner_lifecycle.shutdown()

    # =====================================================
    # PAUSE
    # =====================================================

    def pause(
        self,
    ) -> bool:

        return scanner_lifecycle.pause()

    # =====================================================
    # RESUME
    # =====================================================

    def resume(
        self,
    ) -> bool:

        return scanner_lifecycle.resume()

    # =====================================================
    # RUN SCAN
    # =====================================================

    def scan(
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
        background: bool = True,
        clear_previous_results: bool = False,
    ) -> bool:
        """
        Start one scanner cycle.
        """

        return scanner_controller.start(

            symbols,

            scanner_names=scanner_names,

            context=context,

            background=background,

            clear_previous_results=(
                clear_previous_results
            ),
        )

    # =====================================================
    # STOP ACTIVE SCAN
    # =====================================================

    def stop_scan(
        self,
    ) -> bool:

        return scanner_controller.stop()

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

        return scanner_controller.run_due(

            symbols,

            context=context,

            background=background,
        )

    # =====================================================
    # REGISTERED SCANNERS
    # =====================================================

    def scanners(
        self,
    ) -> List[str]:

        return list(
            scanner_registry.scanner_names
        )

    # =====================================================
    # ENABLED SCANNERS
    # =====================================================

    def enabled_scanners(
        self,
    ) -> List[str]:

        return list(
            scanner_registry.enabled_names
        )

    # =====================================================
    # DISABLED SCANNERS
    # =====================================================

    def disabled_scanners(
        self,
    ) -> List[str]:

        return list(
            scanner_registry.disabled_names
        )

    # =====================================================
    # ENABLE SCANNER
    # =====================================================

    def enable_scanner(
        self,
        scanner_name: str,
    ) -> bool:

        return scanner_controller.enable_scanner(
            scanner_name
        )

    # =====================================================
    # DISABLE SCANNER
    # =====================================================

    def disable_scanner(
        self,
        scanner_name: str,
    ) -> bool:

        return scanner_controller.disable_scanner(
            scanner_name
        )

    # =====================================================
    # ENABLE ALL
    # =====================================================

    def enable_all(
        self,
    ) -> None:

        scanner_controller.enable_all()

    # =====================================================
    # DISABLE ALL
    # =====================================================

    def disable_all(
        self,
    ) -> None:

        scanner_controller.disable_all()

    # =====================================================
    # SCHEDULE SCANNER
    # =====================================================

    def schedule(
        self,
        scanner_name: str,
        *,
        interval_seconds: int = 60,
        enabled: bool = True,
        run_immediately: bool = True,
    ) -> bool:

        return scanner_controller.schedule_scanner(

            scanner_name,

            interval_seconds=(
                interval_seconds
            ),

            enabled=enabled,

            run_immediately=(
                run_immediately
            ),
        )

    # =====================================================
    # UNSCHEDULE SCANNER
    # =====================================================

    def unschedule(
        self,
        scanner_name: str,
    ) -> bool:

        return scanner_controller.unschedule_scanner(
            scanner_name
        )

    # =====================================================
    # SET SCAN INTERVAL
    # =====================================================

    def set_interval(
        self,
        scanner_name: str,
        interval_seconds: int,
    ) -> bool:

        return scanner_controller.set_interval(

            scanner_name,

            interval_seconds,
        )

    # =====================================================
    # DUE SCANNERS
    # =====================================================

    def due_scanners(
        self,
    ) -> List[str]:

        return scanner_controller.due_scanners()

    # =====================================================
    # RESULTS
    # =====================================================

    def results(
        self,
        *,
        limit: Optional[int] = None,
    ) -> List[Any]:

        return scanner_controller.results(
            limit=limit
        )

    # =====================================================
    # RESULT COUNT
    # =====================================================

    def result_count(
        self,
    ) -> int:

        return len(
            scanner_result_store
        )

    # =====================================================
    # CLEAR RESULTS
    # =====================================================

    def clear_results(
        self,
    ) -> None:

        scanner_controller.clear_results()

    # =====================================================
    # HEALTH
    # =====================================================

    def health(
        self,
    ) -> Dict[str, Any]:

        return (
            scanner_health
            .check()
            .to_dict()
        )

    # =====================================================
    # IS HEALTHY
    # =====================================================

    def is_healthy(
        self,
    ) -> bool:

        return (
            scanner_health
            .check()
            .healthy
        )

    # =====================================================
    # DIAGNOSTICS
    # =====================================================

    def diagnostics(
        self,
    ) -> Dict[str, Any]:

        return (
            scanner_diagnostics
            .run()
            .to_dict()
        )

    # =====================================================
    # DIAGNOSTIC SUMMARY
    # =====================================================

    def diagnostic_summary(
        self,
    ) -> Dict[str, Any]:

        return (
            scanner_diagnostics
            .summary()
        )

    # =====================================================
    # METRICS
    # =====================================================

    def metrics(
        self,
    ) -> Dict[str, Any]:

        return scanner_metrics.report()

    # =====================================================
    # SCHEDULER STATUS
    # =====================================================

    def scheduler_status(
        self,
    ) -> Dict[str, Any]:

        return scanner_scheduler.report()

    # =====================================================
    # LIFECYCLE STATUS
    # =====================================================

    def lifecycle_status(
        self,
    ) -> Dict[str, Any]:

        return scanner_lifecycle.report()

    # =====================================================
    # CONTROLLER STATUS
    # =====================================================

    def controller_status(
        self,
    ) -> Dict[str, Any]:

        return scanner_controller.status()

    # =====================================================
    # RUNNING
    # =====================================================

    @property
    def running(
        self,
    ) -> bool:

        return scanner_controller.running

    # =====================================================
    # INITIALIZED
    # =====================================================

    @property
    def initialized(
        self,
    ) -> bool:

        return scanner_lifecycle.initialized

    # =====================================================
    # READY
    # =====================================================

    @property
    def ready(
        self,
    ) -> bool:

        return scanner_lifecycle.ready

    # =====================================================
    # FULL STATUS
    # =====================================================

    def status(
        self,
    ) -> Dict[str, Any]:
        """
        Dashboard-ready scanner subsystem status.
        """

        with self._lock:

            return {

                "initialized":
                    self.initialized,

                "ready":
                    self.ready,

                "running":
                    self.running,

                "lifecycle":
                    scanner_lifecycle.report(),

                "registry": {

                    "registered":
                        len(
                            scanner_registry
                        ),

                    "scanner_names":
                        list(
                            scanner_registry
                            .scanner_names
                        ),

                    "enabled_names":
                        list(
                            scanner_registry
                            .enabled_names
                        ),

                    "disabled_names":
                        list(
                            scanner_registry
                            .disabled_names
                        ),
                },

                "scheduler":
                    scanner_scheduler.report(),

                "metrics":
                    scanner_metrics.report(),

                "result_count":
                    len(
                        scanner_result_store
                    ),
            }

    # =====================================================
    # RESET
    # =====================================================

    def reset(
        self,
        *,
        clear_results: bool = True,
        clear_metrics: bool = True,
        clear_events: bool = False,
    ) -> bool:
        """
        Reset scanner runtime data.

        Registered scanner classes remain intact.
        """

        return scanner_lifecycle.reset_runtime(

            clear_results=clear_results,

            clear_metrics=clear_metrics,

            clear_events=clear_events,
        )


# =========================================================
# GLOBAL SERVICE
# =========================================================

scanner_service = ScannerService()


# =========================================================
# CONVENIENCE FUNCTIONS
# =========================================================

def initialize_scanners(
    *,
    default_interval_seconds: int = 60,
) -> bool:

    return scanner_service.initialize(

        default_interval_seconds=(
            default_interval_seconds
        )
    )


def scan_market(
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

    return scanner_service.scan(

        symbols,

        scanner_names=scanner_names,

        context=context,

        background=background,
    )


def stop_market_scan(
) -> bool:

    return scanner_service.stop_scan()


def get_scanner_status(
) -> Dict[str, Any]:

    return scanner_service.status()


def get_scanner_results(
    *,
    limit: Optional[int] = None,
) -> List[Any]:

    return scanner_service.results(
        limit=limit
    )


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "ScannerService",

    "scanner_service",

    "initialize_scanners",

    "scan_market",

    "stop_market_scan",

    "get_scanner_status",

    "get_scanner_results",
]


# ==========================
# END OF FILE
# ==========================