"""
=========================================================
StockVersity Scanner Pro
Scanner Manager
Version : 2.0
=========================================================

Top-level scanner subsystem manager.

Responsibilities
----------------
• Initialize complete scanner subsystem
• Configure runtime symbols/context
• Start background scanner runtime
• Stop complete scanner subsystem
• Pause / resume scanning
• Run manual scans
• Provide unified application status
• Provide health and diagnostics
• Support clean application shutdown
=========================================================
"""

from __future__ import annotations

from threading import RLock

from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional

from core.scanner.runtime import (
    ContextProvider,
    SymbolProvider,
    scanner_runtime,
)

from core.scanner.service import (
    scanner_service,
)


# =========================================================
# CALLBACK TYPES
# =========================================================

StatusCallback = Callable[
    [Dict[str, Any]],
    None,
]


# =========================================================
# SCANNER MANAGER
# =========================================================

class ScannerManager:
    """
    High-level manager for StockVersity scanner subsystem.

    Application code should normally interact with this
    manager instead of controlling individual scanner
    components directly.
    """

    def __init__(
        self,
    ) -> None:

        self._lock = RLock()

        self._initialized = False

        self._started = False

        self._last_error = ""

        self._status_callbacks: List[
            StatusCallback
        ] = []

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

        with self._lock:

            if (
                self._initialized
                and not force
            ):

                return True

            self._last_error = ""

        try:

            success = (
                scanner_service.initialize(

                    default_interval_seconds=(
                        default_interval_seconds
                    ),

                    force=force,
                )
            )

            if not success:

                with self._lock:

                    self._last_error = (
                        "Scanner service initialization failed."
                    )

                return False

            with self._lock:

                self._initialized = True

            self._notify_status()

            return True

        except Exception as exc:

            self._record_error(
                exc
            )

            return False

    # =====================================================
    # CONFIGURE SYMBOLS
    # =====================================================

    def set_symbols(
        self,
        symbols: Optional[
            Iterable[str]
        ],
    ) -> None:
        """
        Configure static runtime symbol universe.
        """

        scanner_runtime.set_symbols(
            symbols
        )

    # =====================================================
    # SYMBOL PROVIDER
    # =====================================================

    def set_symbol_provider(
        self,
        provider: Optional[
            SymbolProvider
        ],
    ) -> None:
        """
        Configure dynamic symbol provider.

        Example:

            scanner_manager.set_symbol_provider(
                universe_service.get_symbols
            )
        """

        scanner_runtime.set_symbol_provider(
            provider
        )

    # =====================================================
    # CONTEXT
    # =====================================================

    def set_context(
        self,
        context: Optional[
            Dict[str, Any]
        ],
    ) -> None:

        scanner_runtime.set_context(
            context
        )

    # =====================================================
    # CONTEXT PROVIDER
    # =====================================================

    def set_context_provider(
        self,
        provider: Optional[
            ContextProvider
        ],
    ) -> None:

        scanner_runtime.set_context_provider(
            provider
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
        default_interval_seconds: int = 60,
    ) -> bool:
        """
        Start complete scanner subsystem.

        Startup order
        -------------
        1. Initialize scanner subsystem
        2. Start lifecycle services
        3. Configure runtime
        4. Start background runtime
        """

        with self._lock:

            if self._started:

                if scanner_runtime.running:

                    return True

                self._started = False

            self._last_error = ""

        # ---------------------------------------------
        # INITIALIZE
        # ---------------------------------------------

        if not self._initialized:

            if not self.initialize(

                default_interval_seconds=(
                    default_interval_seconds
                )

            ):

                return False

        try:

            # -----------------------------------------
            # START SERVICE / SCHEDULER
            # -----------------------------------------

            if not scanner_service.start_system():

                with self._lock:

                    self._last_error = (
                        "Scanner system failed to start."
                    )

                return False

            # -----------------------------------------
            # CONFIGURE SYMBOLS
            # -----------------------------------------

            if symbols is not None:

                scanner_runtime.set_symbols(
                    symbols
                )

            # -----------------------------------------
            # CONFIGURE CONTEXT
            # -----------------------------------------

            if context is not None:

                scanner_runtime.set_context(
                    context
                )

            # -----------------------------------------
            # START RUNTIME
            # -----------------------------------------

            runtime_started = (
                scanner_runtime.start(

                    start_scheduler=False,
                )
            )

            if not runtime_started:

                scanner_service.stop_system()

                with self._lock:

                    self._last_error = (
                        "Scanner runtime failed to start."
                    )

                return False

            with self._lock:

                self._started = True

            self._notify_status()

            return True

        except Exception as exc:

            self._record_error(
                exc
            )

            try:

                scanner_runtime.stop(
                    stop_scheduler=False,
                    wait=False,
                )

            except Exception:

                pass

            try:

                scanner_service.stop_system()

            except Exception:

                pass

            return False

    # =====================================================
    # STOP
    # =====================================================

    def stop(
        self,
        *,
        wait: bool = True,
        timeout: Optional[float] = 5.0,
    ) -> bool:
        """
        Stop complete scanner subsystem.
        """

        success = True

        with self._lock:

            self._last_error = ""

        try:

            runtime_result = (
                scanner_runtime.stop(

                    stop_scheduler=False,

                    stop_active_scan=True,

                    wait=wait,

                    timeout=timeout,
                )
            )

            if not runtime_result:

                success = False

        except Exception as exc:

            success = False

            self._record_error(
                exc
            )

        try:

            service_result = (
                scanner_service.stop_system()
            )

            if not service_result:

                success = False

        except Exception as exc:

            success = False

            self._record_error(
                exc
            )

        with self._lock:

            self._started = False

        self._notify_status()

        return success

    # =====================================================
    # RESTART
    # =====================================================

    def restart(
        self,
        *,
        wait: bool = True,
    ) -> bool:

        if not self.stop(
            wait=wait
        ):

            return False

        return self.start()

    # =====================================================
    # PAUSE
    # =====================================================

    def pause(
        self,
    ) -> bool:
        """
        Pause scheduled scanner execution.
        """

        try:

            if not scanner_runtime.running:

                return False

            result = (
                scanner_runtime.pause()
            )

            self._notify_status()

            return result

        except Exception as exc:

            self._record_error(
                exc
            )

            return False

    # =====================================================
    # RESUME
    # =====================================================

    def resume(
        self,
    ) -> bool:
        """
        Resume scheduled scanner execution.
        """

        try:

            if not scanner_runtime.running:

                return False

            result = (
                scanner_runtime.resume()
            )

            self._notify_status()

            return result

        except Exception as exc:

            self._record_error(
                exc
            )

            return False

    # =====================================================
    # MANUAL SCAN
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
        Run manual scanner cycle.

        This can be used by the dashboard Scan Now button.
        """

        try:

            return scanner_service.scan(

                symbols,

                scanner_names=scanner_names,

                context=context,

                background=background,

                clear_previous_results=(
                    clear_previous_results
                ),
            )

        except Exception as exc:

            self._record_error(
                exc
            )

            return False

    # =====================================================
    # STOP MANUAL / ACTIVE SCAN
    # =====================================================

    def stop_scan(
        self,
    ) -> bool:

        try:

            return (
                scanner_service.stop_scan()
            )

        except Exception as exc:

            self._record_error(
                exc
            )

            return False

    # =====================================================
    # ENABLE SCANNER
    # =====================================================

    def enable_scanner(
        self,
        scanner_name: str,
    ) -> bool:

        result = (
            scanner_service.enable_scanner(
                scanner_name
            )
        )

        scanner_runtime.wake()

        self._notify_status()

        return result

    # =====================================================
    # DISABLE SCANNER
    # =====================================================

    def disable_scanner(
        self,
        scanner_name: str,
    ) -> bool:

        result = (
            scanner_service.disable_scanner(
                scanner_name
            )
        )

        scanner_runtime.wake()

        self._notify_status()

        return result

    # =====================================================
    # SET INTERVAL
    # =====================================================

    def set_interval(
        self,
        scanner_name: str,
        interval_seconds: int,
    ) -> bool:

        result = (
            scanner_service.set_interval(

                scanner_name,

                interval_seconds,
            )
        )

        scanner_runtime.wake()

        return result

    # =====================================================
    # SCANNERS
    # =====================================================

    def scanners(
        self,
    ) -> List[str]:

        return (
            scanner_service.scanners()
        )

    # =====================================================
    # ENABLED SCANNERS
    # =====================================================

    def enabled_scanners(
        self,
    ) -> List[str]:

        return (
            scanner_service
            .enabled_scanners()
        )

    # =====================================================
    # DISABLED SCANNERS
    # =====================================================

    def disabled_scanners(
        self,
    ) -> List[str]:

        return (
            scanner_service
            .disabled_scanners()
        )

    # =====================================================
    # RESULTS
    # =====================================================

    def results(
        self,
        *,
        limit: Optional[int] = None,
    ) -> List[Any]:

        return scanner_service.results(
            limit=limit
        )

    # =====================================================
    # CLEAR RESULTS
    # =====================================================

    def clear_results(
        self,
    ) -> None:

        scanner_service.clear_results()

    # =====================================================
    # HEALTH
    # =====================================================

    def health(
        self,
    ) -> Dict[str, Any]:

        return scanner_service.health()

    # =====================================================
    # DIAGNOSTICS
    # =====================================================

    def diagnostics(
        self,
    ) -> Dict[str, Any]:

        return (
            scanner_service
            .diagnostics()
        )

    # =====================================================
    # REGISTER STATUS CALLBACK
    # =====================================================

    def add_status_callback(
        self,
        callback: StatusCallback,
    ) -> bool:
        """
        Register application/UI status callback.
        """

        if not callable(
            callback
        ):

            raise TypeError(
                "Status callback must be callable."
            )

        with self._lock:

            if callback in (
                self._status_callbacks
            ):

                return False

            self._status_callbacks.append(
                callback
            )

        return True

    # =====================================================
    # REMOVE STATUS CALLBACK
    # =====================================================

    def remove_status_callback(
        self,
        callback: StatusCallback,
    ) -> bool:

        with self._lock:

            if callback not in (
                self._status_callbacks
            ):

                return False

            self._status_callbacks.remove(
                callback
            )

        return True

    # =====================================================
    # NOTIFY STATUS
    # =====================================================

    def _notify_status(
        self,
    ) -> None:

        with self._lock:

            callbacks = list(
                self._status_callbacks
            )

        if not callbacks:

            return

        try:

            status = self.status()

        except Exception:

            return

        for callback in callbacks:

            try:

                callback(
                    status
                )

            except Exception:

                # UI callback failures must never
                # terminate scanner services.
                continue

    # =====================================================
    # RECORD ERROR
    # =====================================================

    def _record_error(
        self,
        exc: BaseException,
    ) -> None:

        with self._lock:

            self._last_error = (

                f"{type(exc).__name__}: "
                f"{exc}"
            )

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
    # RUNNING
    # =====================================================

    @property
    def running(
        self,
    ) -> bool:

        return (
            scanner_runtime.running
        )

    # =====================================================
    # PAUSED
    # =====================================================

    @property
    def paused(
        self,
    ) -> bool:

        return (
            scanner_runtime.paused
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
    # STATUS
    # =====================================================

    def status(
        self,
    ) -> Dict[str, Any]:
        """
        Return unified scanner manager status.
        """

        with self._lock:

            initialized = (
                self._initialized
            )

            started = (
                self._started
            )

            last_error = (
                self._last_error
            )

        return {

            "initialized":
                initialized,

            "started":
                started,

            "running":
                scanner_runtime.running,

            "paused":
                scanner_runtime.paused,

            "last_error":
                last_error,

            "runtime":
                scanner_runtime.status(),

            "service":
                scanner_service.status(),
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

        Scanner must not be running.
        """

        if self.running:

            return False

        return scanner_service.reset(

            clear_results=clear_results,

            clear_metrics=clear_metrics,

            clear_events=clear_events,
        )

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(
        self,
    ) -> bool:
        """
        Application shutdown hook.

        Call this when StockVersity closes.
        """

        result = self.stop(
            wait=True
        )

        with self._lock:

            self._initialized = False

            self._started = False

        return result


# =========================================================
# GLOBAL MANAGER
# =========================================================

scanner_manager = ScannerManager()


# =========================================================
# CONVENIENCE FUNCTIONS
# =========================================================

def initialize_scanner_manager(
    *,
    default_interval_seconds: int = 60,
) -> bool:

    return scanner_manager.initialize(

        default_interval_seconds=(
            default_interval_seconds
        )
    )


def start_scanner_manager(
    *,
    symbols: Optional[
        Iterable[str]
    ] = None,
    context: Optional[
        Dict[str, Any]
    ] = None,
) -> bool:

    return scanner_manager.start(

        symbols=symbols,

        context=context,
    )


def stop_scanner_manager(
) -> bool:

    return scanner_manager.stop()


def shutdown_scanner_manager(
) -> bool:

    return scanner_manager.shutdown()


def get_scanner_manager_status(
) -> Dict[str, Any]:

    return scanner_manager.status()


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "StatusCallback",

    "ScannerManager",

    "scanner_manager",

    "initialize_scanner_manager",

    "start_scanner_manager",

    "stop_scanner_manager",

    "shutdown_scanner_manager",

    "get_scanner_manager_status",
]


# ==========================
# END OF FILE
# ==========================