"""
=========================================================
StockVersity Scanner Pro
Scanner Lifecycle Manager
Version : 2.0
=========================================================

Central lifecycle management for scanner subsystem.

Responsibilities
----------------
• Initialize scanner subsystem
• Load registered scanners
• Prepare scanner schedules
• Start scanner services
• Pause / resume services
• Gracefully stop scanner subsystem
• Reset runtime components
• Prevent duplicate initialization
• Provide lifecycle diagnostics
=========================================================
"""

from __future__ import annotations

from datetime import datetime

from enum import Enum

from threading import RLock

from typing import Any
from typing import Dict
from typing import Optional

from core.scanner.controller import (
    scanner_controller,
)

from core.scanner.events import (
    scanner_events,
)

from core.scanner.metrics import (
    scanner_metrics,
)

from core.scanner.registry import (
    load_default_scanners,
    scanner_registry,
)

from core.scanner.result_store import (
    scanner_result_store,
)

from core.scanner.scheduler import (
    scanner_scheduler,
)

from core.scanner.state import (
    scanner_state,
)


# =========================================================
# LIFECYCLE STATUS
# =========================================================

class ScannerLifecycleStatus(str, Enum):
    """
    Scanner subsystem lifecycle states.
    """

    NEW = "NEW"

    INITIALIZING = "INITIALIZING"

    READY = "READY"

    RUNNING = "RUNNING"

    PAUSED = "PAUSED"

    STOPPING = "STOPPING"

    STOPPED = "STOPPED"

    ERROR = "ERROR"


# =========================================================
# SCANNER LIFECYCLE
# =========================================================

class ScannerLifecycle:
    """
    Controls scanner subsystem startup and shutdown.
    """

    def __init__(
        self,
    ) -> None:

        self._lock = RLock()

        self._status = (
            ScannerLifecycleStatus.NEW
        )

        self._initialized = False

        self._initialized_at: Optional[
            datetime
        ] = None

        self._started_at: Optional[
            datetime
        ] = None

        self._stopped_at: Optional[
            datetime
        ] = None

        self._last_error: str = ""

    # =====================================================
    # STATUS
    # =====================================================

    @property
    def status(
        self,
    ) -> ScannerLifecycleStatus:

        with self._lock:

            return self._status

    # =====================================================
    # INITIALIZED
    # =====================================================

    @property
    def initialized(
        self,
    ) -> bool:

        with self._lock:

            return self._initialized

    # =====================================================
    # READY
    # =====================================================

    @property
    def ready(
        self,
    ) -> bool:

        return self.status in {

            ScannerLifecycleStatus.READY,

            ScannerLifecycleStatus.RUNNING,

            ScannerLifecycleStatus.PAUSED,
        }

    # =====================================================
    # RUNNING
    # =====================================================

    @property
    def running(
        self,
    ) -> bool:

        return (
            self.status
            == ScannerLifecycleStatus.RUNNING
        )

    # =====================================================
    # PAUSED
    # =====================================================

    @property
    def paused(
        self,
    ) -> bool:

        return (
            self.status
            == ScannerLifecycleStatus.PAUSED
        )

    # =====================================================
    # INITIALIZE
    # =====================================================

    def initialize(
        self,
        *,
        load_scanners: bool = True,
        create_schedules: bool = True,
        default_interval_seconds: int = 60,
        force: bool = False,
    ) -> bool:
        """
        Initialize scanner subsystem.

        Safe to call more than once.
        """

        with self._lock:

            if (
                self._initialized
                and not force
            ):

                return True

            self._status = (
                ScannerLifecycleStatus.INITIALIZING
            )

            self._last_error = ""

        try:

            # -----------------------------------------
            # LOAD DEFAULT SCANNERS
            # -----------------------------------------

            if load_scanners:

                load_default_scanners()

            # -----------------------------------------
            # VALIDATE REGISTRY
            # -----------------------------------------

            registry_status = (
                scanner_registry.status()
            )

            if (
                registry_status[
                    "registered"
                ] <= 0
            ):

                raise RuntimeError(
                    "No scanners registered."
                )

            # -----------------------------------------
            # CREATE DEFAULT SCHEDULES
            # -----------------------------------------

            if create_schedules:

                interval = max(
                    1,
                    int(
                        default_interval_seconds
                    ),
                )

                for scanner_name in (
                    scanner_registry
                    .enabled_names
                ):

                    if scanner_scheduler.has(
                        scanner_name
                    ):

                        continue

                    scanner_scheduler.add(

                        scanner_name,

                        interval_seconds=(
                            interval
                        ),

                        enabled=True,

                        run_immediately=True,
                    )

            # -----------------------------------------
            # COMPLETE INITIALIZATION
            # -----------------------------------------

            with self._lock:

                self._initialized = True

                self._initialized_at = (
                    datetime.now()
                )

                self._status = (
                    ScannerLifecycleStatus.READY
                )

            return True

        except Exception as exc:

            with self._lock:

                self._initialized = False

                self._status = (
                    ScannerLifecycleStatus.ERROR
                )

                self._last_error = (

                    f"{type(exc).__name__}: "
                    f"{exc}"
                )

            return False

    # =====================================================
    # START
    # =====================================================

    def start(
        self,
        *,
        auto_initialize: bool = True,
    ) -> bool:
        """
        Start scanner subsystem services.

        This starts the scheduler.

        It does not automatically launch a scan cycle.
        """

        if not self.initialized:

            if not auto_initialize:

                return False

            initialized = (
                self.initialize()
            )

            if not initialized:

                return False

        with self._lock:

            if (
                self._status
                == ScannerLifecycleStatus.RUNNING
            ):

                return True

            self._last_error = ""

        try:

            scanner_scheduler.start()

            with self._lock:

                self._status = (
                    ScannerLifecycleStatus.RUNNING
                )

                self._started_at = (
                    datetime.now()
                )

                self._stopped_at = None

            return True

        except Exception as exc:

            with self._lock:

                self._status = (
                    ScannerLifecycleStatus.ERROR
                )

                self._last_error = (

                    f"{type(exc).__name__}: "
                    f"{exc}"
                )

            return False

    # =====================================================
    # PAUSE
    # =====================================================

    def pause(
        self,
    ) -> bool:
        """
        Pause scanner scheduler.
        """

        with self._lock:

            if (
                self._status
                != ScannerLifecycleStatus.RUNNING
            ):

                return False

        try:

            paused = (
                scanner_controller.pause()
            )

            if not paused:

                return False

            with self._lock:

                self._status = (
                    ScannerLifecycleStatus.PAUSED
                )

            return True

        except Exception as exc:

            with self._lock:

                self._status = (
                    ScannerLifecycleStatus.ERROR
                )

                self._last_error = (

                    f"{type(exc).__name__}: "
                    f"{exc}"
                )

            return False

    # =====================================================
    # RESUME
    # =====================================================

    def resume(
        self,
    ) -> bool:
        """
        Resume scanner scheduler.
        """

        with self._lock:

            if (
                self._status
                != ScannerLifecycleStatus.PAUSED
            ):

                return False

        try:

            resumed = (
                scanner_controller.resume()
            )

            if not resumed:

                return False

            with self._lock:

                self._status = (
                    ScannerLifecycleStatus.RUNNING
                )

            return True

        except Exception as exc:

            with self._lock:

                self._status = (
                    ScannerLifecycleStatus.ERROR
                )

                self._last_error = (

                    f"{type(exc).__name__}: "
                    f"{exc}"
                )

            return False

    # =====================================================
    # STOP
    # =====================================================

    def stop(
        self,
        *,
        stop_active_scan: bool = True,
    ) -> bool:
        """
        Gracefully stop scanner subsystem.
        """

        with self._lock:

            if self._status in {

                ScannerLifecycleStatus.STOPPED,

                ScannerLifecycleStatus.NEW,
            }:

                return True

            self._status = (
                ScannerLifecycleStatus.STOPPING
            )

        try:

            # -----------------------------------------
            # STOP ACTIVE SCAN
            # -----------------------------------------

            if (
                stop_active_scan
                and scanner_controller.running
            ):

                scanner_controller.stop()

            # -----------------------------------------
            # STOP SCHEDULER
            # -----------------------------------------

            scanner_scheduler.stop()

            # -----------------------------------------
            # FINAL STATE
            # -----------------------------------------

            with self._lock:

                self._status = (
                    ScannerLifecycleStatus.STOPPED
                )

                self._stopped_at = (
                    datetime.now()
                )

            return True

        except Exception as exc:

            with self._lock:

                self._status = (
                    ScannerLifecycleStatus.ERROR
                )

                self._last_error = (

                    f"{type(exc).__name__}: "
                    f"{exc}"
                )

            return False

    # =====================================================
    # RESTART
    # =====================================================

    def restart(
        self,
    ) -> bool:
        """
        Stop and restart scanner subsystem.
        """

        if not self.stop():

            return False

        return self.start()

    # =====================================================
    # RESET RUNTIME
    # =====================================================

    def reset_runtime(
        self,
        *,
        clear_results: bool = False,
        clear_metrics: bool = False,
        clear_events: bool = False,
    ) -> bool:
        """
        Reset runtime data without removing registered
        scanner classes.
        """

        if scanner_controller.running:

            return False

        try:

            # -----------------------------------------
            # STATE
            # -----------------------------------------

            reset_state = getattr(
                scanner_state,
                "reset",
                None,
            )

            if callable(
                reset_state
            ):

                reset_state()

            # -----------------------------------------
            # RESULTS
            # -----------------------------------------

            if clear_results:

                scanner_result_store.clear()

            # -----------------------------------------
            # METRICS
            # -----------------------------------------

            if clear_metrics:

                scanner_metrics.reset()

            # -----------------------------------------
            # EVENTS
            # -----------------------------------------

            if clear_events:

                clear_method = getattr(
                    scanner_events,
                    "clear",
                    None,
                )

                if callable(
                    clear_method
                ):

                    clear_method()

                else:

                    clear_errors = getattr(
                        scanner_events,
                        "clear_errors",
                        None,
                    )

                    if callable(
                        clear_errors
                    ):

                        clear_errors()

            return True

        except Exception as exc:

            with self._lock:

                self._last_error = (

                    f"{type(exc).__name__}: "
                    f"{exc}"
                )

            return False

    # =====================================================
    # RESET SCHEDULES
    # =====================================================

    def reset_schedules(
        self,
        *,
        immediate: bool = False,
    ) -> None:
        """
        Reset next-run times for all schedules.
        """

        scanner_scheduler.reset_all(
            immediate=immediate
        )

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(
        self,
    ) -> bool:
        """
        Application shutdown hook.
        """

        return self.stop(
            stop_active_scan=True
        )

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
    # REPORT
    # =====================================================

    def report(
        self,
    ) -> Dict[str, Any]:

        with self._lock:

            return {

                "status":
                    self._status.value,

                "initialized":
                    self._initialized,

                "ready":
                    self.ready,

                "running":
                    (
                        self._status
                        == ScannerLifecycleStatus.RUNNING
                    ),

                "paused":
                    (
                        self._status
                        == ScannerLifecycleStatus.PAUSED
                    ),

                "initialized_at":
                    (
                        self._initialized_at.isoformat()
                        if self._initialized_at
                        else None
                    ),

                "started_at":
                    (
                        self._started_at.isoformat()
                        if self._started_at
                        else None
                    ),

                "stopped_at":
                    (
                        self._stopped_at.isoformat()
                        if self._stopped_at
                        else None
                    ),

                "last_error":
                    self._last_error,

                "registered_scanners":
                    len(
                        scanner_registry
                    ),

                "enabled_scanners":
                    len(
                        scanner_registry
                        .enabled_names
                    ),

                "scheduled_scanners":
                    len(
                        scanner_scheduler
                    ),

                "controller_running":
                    scanner_controller.running,
            }


# =========================================================
# GLOBAL LIFECYCLE MANAGER
# =========================================================

scanner_lifecycle = (
    ScannerLifecycle()
)


# =========================================================
# CONVENIENCE FUNCTIONS
# =========================================================

def initialize_scanner_system(
    *,
    default_interval_seconds: int = 60,
) -> bool:

    return scanner_lifecycle.initialize(

        default_interval_seconds=(
            default_interval_seconds
        )
    )


def start_scanner_system(
) -> bool:

    return scanner_lifecycle.start()


def pause_scanner_system(
) -> bool:

    return scanner_lifecycle.pause()


def resume_scanner_system(
) -> bool:

    return scanner_lifecycle.resume()


def stop_scanner_system(
) -> bool:

    return scanner_lifecycle.stop()


def restart_scanner_system(
) -> bool:

    return scanner_lifecycle.restart()


def shutdown_scanner_system(
) -> bool:

    return scanner_lifecycle.shutdown()


def get_scanner_lifecycle_status(
) -> Dict[str, Any]:

    return scanner_lifecycle.report()


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "ScannerLifecycleStatus",

    "ScannerLifecycle",

    "scanner_lifecycle",

    "initialize_scanner_system",

    "start_scanner_system",

    "pause_scanner_system",

    "resume_scanner_system",

    "stop_scanner_system",

    "restart_scanner_system",

    "shutdown_scanner_system",

    "get_scanner_lifecycle_status",
]


# ==========================
# END OF FILE
# ==========================