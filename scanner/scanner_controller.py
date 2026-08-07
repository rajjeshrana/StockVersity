"""
=========================================================
StockVersity Scanner Pro
Scanner Controller
Version : 2.0
=========================================================

UI-facing scanner controller.

Responsibilities
----------------
• Control ScannerService
• Start / stop scanner system
• Execute scans
• Refresh scanner results
• Enable / disable scanners
• Provide dashboard data
• Provide opportunities
• Provide alerts
• Provide market analytics
=========================================================
"""

from __future__ import annotations

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from core.scanner.signal import Signal
from core.scanner.scanner_service import ScannerService
from core.scanner.scanner_service import get_scanner_service


# =========================================================
# SCANNER CONTROLLER
# =========================================================

class ScannerController:
    """
    Controller used by the application and dashboard.

    Architecture
    ------------

    Dashboard / UI
        ↓
    ScannerController
        ↓
    ScannerService
        ↓
    ScannerManager
        ↓
    ScannerEngine
        ↓
    Scanners
    """

    def __init__(
        self,
        service: Optional[ScannerService] = None,
    ) -> None:

        self.service = (
            service
            if service is not None
            else get_scanner_service()
        )

        self.last_error: Optional[str] = None

    # =====================================================
    # START
    # =====================================================

    def start(
        self,
    ) -> bool:
        """
        Start scanner subsystem.
        """

        try:

            result = self.service.start()

            self.last_error = None

            return result

        except Exception as exc:

            self.last_error = (
                f"{type(exc).__name__}: {exc}"
            )

            return False

    # =====================================================
    # STOP
    # =====================================================

    def stop(
        self,
    ) -> None:
        """
        Stop scanner subsystem.
        """

        try:

            self.service.stop()

            self.last_error = None

        except Exception as exc:

            self.last_error = (
                f"{type(exc).__name__}: {exc}"
            )

    # =====================================================
    # RESTART
    # =====================================================

    def restart(
        self,
    ) -> bool:

        try:

            result = self.service.restart()

            self.last_error = None

            return result

        except Exception as exc:

            self.last_error = (
                f"{type(exc).__name__}: {exc}"
            )

            return False

    # =====================================================
    # RUN SCAN
    # =====================================================

    def run_scan(
        self,
        market_data: Dict[str, Any],
    ) -> List[Signal]:
        """
        Run all enabled scanners.
        """

        try:

            results = self.service.scan(
                market_data
            )

            self.last_error = None

            return results

        except Exception as exc:

            self.last_error = (
                f"{type(exc).__name__}: {exc}"
            )

            return []

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh(
        self,
        market_data: Optional[
            Dict[str, Any]
        ] = None,
    ) -> List[Signal]:
        """
        Refresh scanner results.
        """

        try:

            results = self.service.refresh(
                market_data
            )

            self.last_error = None

            return results

        except Exception as exc:

            self.last_error = (
                f"{type(exc).__name__}: {exc}"
            )

            return []

    # =====================================================
    # RESULTS
    # =====================================================

    def results(
        self,
    ) -> List[Signal]:

        return self.service.results

    # =====================================================
    # RESULT COUNT
    # =====================================================

    def result_count(
        self,
    ) -> int:

        return self.service.result_count

    # =====================================================
    # HAS RESULTS
    # =====================================================

    def has_results(
        self,
    ) -> bool:

        return self.service.has_results

    # =====================================================
    # TOP OPPORTUNITIES
    # =====================================================

    def top_opportunities(
        self,
        limit: int = 10,
    ) -> List[Signal]:

        return self.service.top_opportunities(
            limit
        )

    # =====================================================
    # WATCHLIST
    # =====================================================

    def watchlist(
        self,
        limit: int = 25,
    ) -> List[Signal]:

        return self.service.watchlist(
            limit
        )

    # =====================================================
    # BUY SIGNALS
    # =====================================================

    def buy_signals(
        self,
    ) -> List[Signal]:

        return self.service.buy_signals()

    # =====================================================
    # SELL SIGNALS
    # =====================================================

    def sell_signals(
        self,
    ) -> List[Signal]:

        return self.service.sell_signals()

    # =====================================================
    # WATCH SIGNALS
    # =====================================================

    def watch_signals(
        self,
    ) -> List[Signal]:

        return self.service.watch_signals()

    # =====================================================
    # FIND SYMBOL
    # =====================================================

    def find_symbol(
        self,
        symbol: str,
    ) -> Optional[Signal]:

        return self.service.find_symbol(
            symbol
        )

    # =====================================================
    # FILTER BY SCANNER
    # =====================================================

    def filter_by_scanner(
        self,
        scanner_name: str,
    ) -> List[Signal]:

        return self.service.filter_by_scanner(
            scanner_name
        )

    # =====================================================
    # FILTER BY SECTOR
    # =====================================================

    def filter_by_sector(
        self,
        sector: str,
    ) -> List[Signal]:

        return self.service.filter_by_sector(
            sector
        )

    # =====================================================
    # ENABLE SCANNER
    # =====================================================

    def enable_scanner(
        self,
        scanner_name: str,
    ) -> bool:

        try:

            result = (
                self.service.enable_scanner(
                    scanner_name
                )
            )

            self.last_error = None

            return result

        except Exception as exc:

            self.last_error = (
                f"{type(exc).__name__}: {exc}"
            )

            return False

    # =====================================================
    # DISABLE SCANNER
    # =====================================================

    def disable_scanner(
        self,
        scanner_name: str,
    ) -> bool:

        try:

            result = (
                self.service.disable_scanner(
                    scanner_name
                )
            )

            self.last_error = None

            return result

        except Exception as exc:

            self.last_error = (
                f"{type(exc).__name__}: {exc}"
            )

            return False

    # =====================================================
    # ENABLE ALL
    # =====================================================

    def enable_all(
        self,
    ) -> None:

        self.service.enable_all()

    # =====================================================
    # DISABLE ALL
    # =====================================================

    def disable_all(
        self,
    ) -> None:

        self.service.disable_all()

    # =====================================================
    # SCANNER NAMES
    # =====================================================

    def scanner_names(
        self,
    ) -> List[str]:

        return self.service.scanner_names

    # =====================================================
    # ACTIVE SCANNERS
    # =====================================================

    def active_scanners(
        self,
    ) -> List[str]:

        return self.service.active_scanners

    # =====================================================
    # DASHBOARD FEED
    # =====================================================

    def dashboard_feed(
        self,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Main opportunity table data.
        """

        return self.service.dashboard_feed(
            limit
        )

    # =====================================================
    # DASHBOARD SUMMARY
    # =====================================================

    def dashboard_summary(
        self,
    ) -> Dict[str, Any]:
        """
        Dashboard card data.
        """

        return self.service.dashboard_summary()

    # =====================================================
    # MARKET SENTIMENT
    # =====================================================

    def market_sentiment(
        self,
    ) -> str:

        return self.service.market_sentiment()

    # =====================================================
    # MARKET HEALTH
    # =====================================================

    def market_health(
        self,
    ) -> float:

        return self.service.market_health()

    # =====================================================
    # MARKET BREADTH
    # =====================================================

    def market_breadth(
        self,
    ) -> Dict[str, Any]:

        return self.service.market_breadth()

    # =====================================================
    # SECTOR RANKING
    # =====================================================

    def sector_ranking(
        self,
    ) -> List[Dict[str, Any]]:

        return self.service.sector_ranking()

    # =====================================================
    # SCANNER RANKING
    # =====================================================

    def scanner_ranking(
        self,
    ) -> List[Dict[str, Any]]:

        return self.service.scanner_ranking()

    # =====================================================
    # CONSENSUS
    # =====================================================

    def consensus(
        self,
        minimum_scanners: int = 2,
    ) -> List[Dict[str, Any]]:

        return self.service.consensus(
            minimum_scanners
        )

    # =====================================================
    # ALERTS
    # =====================================================

    def alerts(
        self,
        minimum_score: float = 85.0,
    ) -> List[Dict[str, Any]]:

        return self.service.alerts(
            minimum_score
        )

    # =====================================================
    # SNAPSHOT
    # =====================================================

    def snapshot(
        self,
    ) -> Dict[str, Any]:

        return self.service.snapshot()

    # =====================================================
    # EXPORT
    # =====================================================

    def export(
        self,
    ) -> List[Dict[str, Any]]:

        return self.service.export()

    # =====================================================
    # STATUS
    # =====================================================

    def status(
        self,
    ) -> Dict[str, Any]:

        status = self.service.status()

        status["controller_error"] = (
            self.last_error
        )

        return status

    # =====================================================
    # DIAGNOSTICS
    # =====================================================

    def diagnostics(
        self,
    ) -> Dict[str, Any]:

        return {

            "controller": {
                "last_error": self.last_error,
            },

            "service":
                self.service.diagnostics(),

        }

    # =====================================================
    # CLEAR RESULTS
    # =====================================================

    def clear_results(
        self,
    ) -> None:

        self.service.clear_results()

    # =====================================================
    # CLEAR ERROR
    # =====================================================

    def clear_error(
        self,
    ) -> None:

        self.last_error = None

        self.service.clear_error()

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"scanners="
            f"{len(self.scanner_names())}, "

            f"active="
            f"{len(self.active_scanners())}, "

            f"results="
            f"{self.result_count()})"

        )


# =========================================================
# SHARED CONTROLLER
# =========================================================

_default_controller: Optional[
    ScannerController
] = None


def get_scanner_controller(
) -> ScannerController:
    """
    Return shared ScannerController instance.
    """

    global _default_controller

    if _default_controller is None:

        _default_controller = (
            ScannerController()
        )

    return _default_controller


# =========================================================
# FACTORY
# =========================================================

def create_scanner_controller(
    service: Optional[
        ScannerService
    ] = None,
) -> ScannerController:

    return ScannerController(
        service=service
    )


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "ScannerController",

    "create_scanner_controller",

    "get_scanner_controller",

]


# ==========================
# END OF FILE
# ==========================