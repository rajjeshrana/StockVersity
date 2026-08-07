"""
=========================================================
StockVersity Scanner Pro
Scanner Facade
Version : 2.0
=========================================================

Application-facing facade for scanner subsystem.

Responsibilities
----------------
• Provide simple scanner API to UI
• Start / stop scanner system
• Run manual scans
• Pause / resume scheduled scanning
• Enable / disable scanners
• Access results
• Access scanner status
• Access health / diagnostics
• Hide scanner subsystem implementation details
=========================================================
"""

from __future__ import annotations

from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional

from core.scanner.manager import (
    scanner_manager,
)


# =========================================================
# SCANNER FACADE
# =========================================================

class ScannerFacade:
    """
    Simplified public interface for StockVersity UI.

    Recommended usage:

        from core.scanner.facade import scanner_facade

        scanner_facade.start()
        scanner_facade.scan(symbols)
        results = scanner_facade.results()
    """

    # =====================================================
    # INITIALIZE
    # =====================================================

    def initialize(
        self,
        *,
        default_interval_seconds: int = 60,
    ) -> bool:

        return scanner_manager.initialize(

            default_interval_seconds=(
                default_interval_seconds
            )
        )

    # =====================================================
    # START SYSTEM
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

        return scanner_manager.start(

            symbols=symbols,

            context=context,

            default_interval_seconds=(
                default_interval_seconds
            ),
        )

    # =====================================================
    # STOP SYSTEM
    # =====================================================

    def stop(
        self,
    ) -> bool:

        return scanner_manager.stop()

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(
        self,
    ) -> bool:

        return scanner_manager.shutdown()

    # =====================================================
    # PAUSE
    # =====================================================

    def pause(
        self,
    ) -> bool:

        return scanner_manager.pause()

    # =====================================================
    # RESUME
    # =====================================================

    def resume(
        self,
    ) -> bool:

        return scanner_manager.resume()

    # =====================================================
    # SCAN NOW
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
        Run a manual scanner cycle.

        Suitable for dashboard "Scan Now" action.
        """

        return scanner_manager.scan(

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

        return scanner_manager.stop_scan()

    # =====================================================
    # SCANNER LIST
    # =====================================================

    def scanners(
        self,
    ) -> List[str]:

        return scanner_manager.scanners()

    # =====================================================
    # ENABLED SCANNERS
    # =====================================================

    def enabled_scanners(
        self,
    ) -> List[str]:

        return scanner_manager.enabled_scanners()

    # =====================================================
    # DISABLED SCANNERS
    # =====================================================

    def disabled_scanners(
        self,
    ) -> List[str]:

        return scanner_manager.disabled_scanners()

    # =====================================================
    # ENABLE SCANNER
    # =====================================================

    def enable(
        self,
        scanner_name: str,
    ) -> bool:

        return scanner_manager.enable_scanner(
            scanner_name
        )

    # =====================================================
    # DISABLE SCANNER
    # =====================================================

    def disable(
        self,
        scanner_name: str,
    ) -> bool:

        return scanner_manager.disable_scanner(
            scanner_name
        )

    # =====================================================
    # SET INTERVAL
    # =====================================================

    def set_interval(
        self,
        scanner_name: str,
        interval_seconds: int,
    ) -> bool:

        return scanner_manager.set_interval(

            scanner_name,

            interval_seconds,
        )

    # =====================================================
    # RESULTS
    # =====================================================

    def results(
        self,
        *,
        limit: Optional[int] = None,
    ) -> List[Any]:

        return scanner_manager.results(
            limit=limit
        )

    # =====================================================
    # CLEAR RESULTS
    # =====================================================

    def clear_results(
        self,
    ) -> None:

        scanner_manager.clear_results()

    # =====================================================
    # STATUS
    # =====================================================

    def status(
        self,
    ) -> Dict[str, Any]:

        return scanner_manager.status()

    # =====================================================
    # HEALTH
    # =====================================================

    def health(
        self,
    ) -> Dict[str, Any]:

        return scanner_manager.health()

    # =====================================================
    # DIAGNOSTICS
    # =====================================================

    def diagnostics(
        self,
    ) -> Dict[str, Any]:

        return scanner_manager.diagnostics()

    # =====================================================
    # RUNNING
    # =====================================================

    @property
    def running(
        self,
    ) -> bool:

        return scanner_manager.running

    # =====================================================
    # PAUSED
    # =====================================================

    @property
    def paused(
        self,
    ) -> bool:

        return scanner_manager.paused

    # =====================================================
    # INITIALIZED
    # =====================================================

    @property
    def initialized(
        self,
    ) -> bool:

        return scanner_manager.initialized

    # =====================================================
    # LAST ERROR
    # =====================================================

    @property
    def last_error(
        self,
    ) -> str:

        return scanner_manager.last_error

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

        return scanner_manager.reset(

            clear_results=clear_results,

            clear_metrics=clear_metrics,

            clear_events=clear_events,
        )


# =========================================================
# GLOBAL FACADE
# =========================================================

scanner_facade = ScannerFacade()


# =========================================================
# CONVENIENCE FUNCTIONS
# =========================================================

def initialize_scanner(
    *,
    default_interval_seconds: int = 60,
) -> bool:

    return scanner_facade.initialize(

        default_interval_seconds=(
            default_interval_seconds
        )
    )


def start_scanning(
    *,
    symbols: Optional[
        Iterable[str]
    ] = None,
    context: Optional[
        Dict[str, Any]
    ] = None,
) -> bool:

    return scanner_facade.start(

        symbols=symbols,

        context=context,
    )


def scan_now(
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

    return scanner_facade.scan(

        symbols,

        scanner_names=scanner_names,

        context=context,

        background=background,
    )


def stop_scanning(
) -> bool:

    return scanner_facade.stop()


def get_results(
    *,
    limit: Optional[int] = None,
) -> List[Any]:

    return scanner_facade.results(
        limit=limit
    )


def get_status(
) -> Dict[str, Any]:

    return scanner_facade.status()


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "ScannerFacade",

    "scanner_facade",

    "initialize_scanner",

    "start_scanning",

    "scan_now",

    "stop_scanning",

    "get_results",

    "get_status",
]


# ==========================
# END OF FILE
# ==========================