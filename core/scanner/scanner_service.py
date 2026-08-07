"""
=========================================================
StockVersity Scanner Pro
Scanner Service
Version : 2.0
=========================================================

Application-facing scanner service.

Responsibilities
----------------
• Provide one interface for the UI/application
• Start scanner system
• Run market scans
• Refresh scans
• Return dashboard opportunities
• Return alerts
• Return scanner status
• Search/filter scanner results

Architecture
------------
UI / Dashboard
    ↓
ScannerService
    ↓
ScannerManager
    ↓
ScannerEngine
    ↓
Individual Scanners

=========================================================
"""

from __future__ import annotations

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from core.scanner.signal import Signal

from core.scanner.scanner_manager import (
    ScannerManager,
    create_scanner_manager,
)


# =========================================================
# SCANNER SERVICE
# =========================================================

class ScannerService:
    """
    Application-facing scanner service.

    The UI should normally communicate with this service
    rather than directly controlling ScannerEngine.
    """

    def __init__(
        self,
        *,
        manager: Optional[ScannerManager] = None,
        auto_start: bool = True,
        parallel: bool = True,
        max_workers: int = 8,
        debug: bool = False,
    ) -> None:

        self.debug = bool(debug)

        self.manager = (
            manager
            if manager is not None
            else create_scanner_manager(
                auto_load=False,
                parallel=parallel,
                max_workers=max_workers,
                debug=debug,
            )
        )

        self.started = False

        self.running = False

        self.last_error: Optional[str] = None

        self.scan_count = 0

        self.last_market_data: Dict[
            str,
            Any
        ] = {}

        self.last_results: List[
            Signal
        ] = []

        if auto_start:

            self.start()

    # =====================================================
    # LOG
    # =====================================================

    def log(
        self,
        *message: Any,
    ) -> None:

        if not self.debug:

            return

        print(
            "[ScannerService]",
            *message,
        )

    # =====================================================
    # START
    # =====================================================

    def start(
        self,
    ) -> bool:
        """
        Initialize scanner service and load scanners.
        """

        if self.started:

            return True

        try:

            self.manager.load_scanners()

            self.started = True

            self.last_error = None

            self.log(
                "Scanner service started."
            )

            return True

        except Exception as exc:

            self.last_error = (
                f"{type(exc).__name__}: {exc}"
            )

            self.log(
                "Startup failed:",
                self.last_error,
            )

            return False

    # =====================================================
    # STOP
    # =====================================================

    def stop(
        self,
    ) -> None:
        """
        Stop scanner service.
        """

        try:

            self.manager.shutdown()

        finally:

            self.started = False

            self.running = False

        self.log(
            "Scanner service stopped."
        )

    # =====================================================
    # RESTART
    # =====================================================

    def restart(
        self,
    ) -> bool:

        self.stop()

        return self.start()

    # =====================================================
    # RUN SCAN
    # =====================================================

    def scan(
        self,
        market_data: Dict[str, Any],
    ) -> List[Signal]:
        """
        Run all active scanners.
        """

        if not isinstance(
            market_data,
            dict,
        ):

            raise TypeError(
                "market_data must be a dictionary."
            )

        if not self.started:

            if not self.start():

                return []

        if self.running:

            return list(
                self.last_results
            )

        self.running = True

        self.last_error = None

        self.last_market_data = dict(
            market_data
        )

        try:

            results = self.manager.run(
                market_data
            )

            self.last_results = list(
                results
            )

            self.scan_count += 1

            return list(
                self.last_results
            )

        except Exception as exc:

            self.last_error = (
                f"{type(exc).__name__}: {exc}"
            )

            self.log(
                "Scan failed:",
                self.last_error,
            )

            raise

        finally:

            self.running = False

    # =====================================================
    # RUN ALIAS
    # =====================================================

    def run(
        self,
        market_data: Dict[str, Any],
    ) -> List[Signal]:
        """
        Compatibility alias for scan().
        """

        return self.scan(
            market_data
        )

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
        Refresh using supplied market data or the last
        market-data snapshot.
        """

        data = (
            market_data
            if market_data is not None
            else self.last_market_data
        )

        if not data:

            return []

        if not isinstance(
            data,
            dict,
        ):

            raise TypeError(
                "market_data must be a dictionary."
            )

        if not self.started:

            if not self.start():

                return []

        if self.running:

            return list(
                self.last_results
            )

        self.running = True

        self.last_error = None

        try:

            results = self.manager.refresh(
                data
            )

            self.last_results = list(
                results
            )

            self.last_market_data = dict(
                data
            )

            self.scan_count += 1

            return list(
                self.last_results
            )

        except Exception as exc:

            self.last_error = (
                f"{type(exc).__name__}: {exc}"
            )

            self.log(
                "Refresh failed:",
                self.last_error,
            )

            raise

        finally:

            self.running = False

    # =====================================================
    # RESULTS
    # =====================================================

    @property
    def results(
        self,
    ) -> List[Signal]:

        return list(
            self.manager.results
        )

    # =====================================================
    # RESULT COUNT
    # =====================================================

    @property
    def result_count(
        self,
    ) -> int:

        return len(
            self.manager.results
        )

    # =====================================================
    # HAS RESULTS
    # =====================================================

    @property
    def has_results(
        self,
    ) -> bool:

        return (
            self.result_count > 0
        )

    # =====================================================
    # TOP OPPORTUNITIES
    # =====================================================

    def top_opportunities(
        self,
        limit: int = 10,
    ) -> List[Signal]:

        limit = max(
            1,
            int(limit),
        )

        return self.manager.top_opportunities(
            limit
        )

    # =====================================================
    # WATCHLIST
    # =====================================================

    def watchlist(
        self,
        limit: int = 25,
    ) -> List[Signal]:

        limit = max(
            1,
            int(limit),
        )

        return self.manager.watchlist(
            limit
        )

    # =====================================================
    # BUY SIGNALS
    # =====================================================

    def buy_signals(
        self,
    ) -> List[Signal]:

        return self.manager.buy_signals()

    # =====================================================
    # SELL SIGNALS
    # =====================================================

    def sell_signals(
        self,
    ) -> List[Signal]:

        return self.manager.sell_signals()

    # =====================================================
    # WATCH SIGNALS
    # =====================================================

    def watch_signals(
        self,
    ) -> List[Signal]:

        return self.manager.watch_signals()

    # =====================================================
    # ALERTS
    # =====================================================

    def alerts(
        self,
        minimum_score: float = 85.0,
    ) -> List[Dict[str, Any]]:

        return self.manager.alerts(
            minimum_score
        )

    # =====================================================
    # FIND SYMBOL
    # =====================================================

    def find_symbol(
        self,
        symbol: str,
    ) -> Optional[Signal]:

        return self.manager.find_symbol(
            symbol
        )

    # =====================================================
    # FILTER BY SCANNER
    # =====================================================

    def filter_by_scanner(
        self,
        scanner_name: str,
    ) -> List[Signal]:

        return self.manager.filter_by_scanner(
            scanner_name
        )

    # =====================================================
    # FILTER BY SECTOR
    # =====================================================

    def filter_by_sector(
        self,
        sector: str,
    ) -> List[Signal]:

        return self.manager.filter_by_sector(
            sector
        )

    # =====================================================
    # ENABLE SCANNER
    # =====================================================

    def enable_scanner(
        self,
        scanner_name: str,
    ) -> bool:

        return bool(
            self.manager.enable(
                scanner_name
            )
        )

    # =====================================================
    # DISABLE SCANNER
    # =====================================================

    def disable_scanner(
        self,
        scanner_name: str,
    ) -> bool:

        return bool(
            self.manager.disable(
                scanner_name
            )
        )

    # =====================================================
    # ENABLE
    # =====================================================

    def enable(
        self,
        scanner_name: str,
    ) -> bool:
        """
        Compatibility alias.
        """

        return self.enable_scanner(
            scanner_name
        )

    # =====================================================
    # DISABLE
    # =====================================================

    def disable(
        self,
        scanner_name: str,
    ) -> bool:
        """
        Compatibility alias.
        """

        return self.disable_scanner(
            scanner_name
        )

    # =====================================================
    # ENABLE ALL
    # =====================================================

    def enable_all(
        self,
    ) -> None:

        self.manager.enable_all()

    # =====================================================
    # DISABLE ALL
    # =====================================================

    def disable_all(
        self,
    ) -> None:

        self.manager.disable_all()

    # =====================================================
    # SCANNER NAMES
    # =====================================================

    @property
    def scanner_names(
        self,
    ) -> List[str]:

        return list(
            self.manager.scanner_names
        )

    # =====================================================
    # ACTIVE SCANNERS
    # =====================================================

    @property
    def active_scanners(
        self,
    ) -> List[str]:

        return list(
            self.manager.active_scanners
        )

    # =====================================================
    # DASHBOARD FEED
    # =====================================================

    def dashboard_feed(
        self,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Data for OpportunitiesTable.
        """

        limit = max(
            1,
            int(limit),
        )

        return self.manager.dashboard_feed(
            limit
        )

    # =====================================================
    # DASHBOARD SUMMARY
    # =====================================================

    def dashboard_summary(
        self,
    ) -> Dict[str, Any]:
        """
        Data for dashboard cards.
        """

        return self.manager.dashboard_summary()

    # =====================================================
    # DASHBOARD DATA
    # =====================================================

    def dashboard_data(
        self,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Combined dashboard payload.
        """

        return {

            "summary":
                self.dashboard_summary(),

            "opportunities":
                self.dashboard_feed(
                    limit
                ),

            "alerts":
                self.alerts(),

            "market_breadth":
                self.market_breadth(),

            "sector_ranking":
                self.sector_ranking(),

            "scanner_ranking":
                self.scanner_ranking(),

        }

    # =====================================================
    # MARKET SENTIMENT
    # =====================================================

    def market_sentiment(
        self,
    ) -> str:

        return self.manager.market_sentiment()

    # =====================================================
    # MARKET HEALTH
    # =====================================================

    def market_health(
        self,
    ) -> float:

        return float(
            self.manager.market_health()
        )

    # =====================================================
    # MARKET BREADTH
    # =====================================================

    def market_breadth(
        self,
    ) -> Dict[str, Any]:

        return self.manager.market_breadth()

    # =====================================================
    # SECTOR RANKING
    # =====================================================

    def sector_ranking(
        self,
    ) -> List[Dict[str, Any]]:

        return self.manager.sector_ranking()

    # =====================================================
    # SCANNER RANKING
    # =====================================================

    def scanner_ranking(
        self,
    ) -> List[Dict[str, Any]]:

        return self.manager.scanner_ranking()

    # =====================================================
    # CONSENSUS
    # =====================================================

    def consensus(
        self,
        minimum_scanners: int = 2,
    ) -> List[Dict[str, Any]]:

        minimum_scanners = max(
            1,
            int(minimum_scanners),
        )

        return self.manager.consensus(
            minimum_scanners
        )

    # =====================================================
    # SNAPSHOT
    # =====================================================

    def snapshot(
        self,
    ) -> Dict[str, Any]:

        return self.manager.snapshot()

    # =====================================================
    # EXPORT
    # =====================================================

    def export(
        self,
    ) -> List[Dict[str, Any]]:

        return self.manager.export()

    # =====================================================
    # STATUS
    # =====================================================

    def status(
        self,
    ) -> Dict[str, Any]:

        return {

            "started":
                self.started,

            "running":
                self.running,

            "scan_count":
                self.scan_count,

            "scanners":
                len(
                    self.scanner_names
                ),

            "active_scanners":
                len(
                    self.active_scanners
                ),

            "results":
                self.result_count,

            "market_sentiment":
                self.market_sentiment(),

            "market_health":
                self.market_health(),

            "last_error":
                self.last_error,
        }

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(
        self,
    ) -> Dict[str, Any]:

        issues: List[str] = []

        if not self.started:

            issues.append(
                "Scanner service is not started."
            )

        if self.last_error:

            issues.append(
                self.last_error
            )

        manager_health: Dict[
            str,
            Any
        ] = {}

        if hasattr(
            self.manager,
            "health_check",
        ):

            try:

                manager_health = (
                    self.manager.health_check()
                )

                if not manager_health.get(
                    "healthy",
                    True,
                ):

                    issues.extend(
                        manager_health.get(
                            "issues",
                            [],
                        )
                    )

            except Exception as exc:

                issues.append(
                    f"Manager health check failed: "
                    f"{type(exc).__name__}: {exc}"
                )

        return {

            "healthy":
                len(issues) == 0,

            "started":
                self.started,

            "running":
                self.running,

            "issues":
                issues,

            "manager":
                manager_health,
        }

    # =====================================================
    # DIAGNOSTICS
    # =====================================================

    def diagnostics(
        self,
    ) -> Dict[str, Any]:

        manager_diagnostics: Dict[
            str,
            Any
        ] = {}

        if hasattr(
            self.manager,
            "diagnostics",
        ):

            manager_diagnostics = (
                self.manager.diagnostics()
            )

        return {

            "service":
                self.status(),

            "manager":
                manager_diagnostics,

            "health":
                self.health_check(),
        }

    # =====================================================
    # CLEAR RESULTS
    # =====================================================

    def clear_results(
        self,
    ) -> None:

        self.manager.clear_results()

        self.last_results = []

    # =====================================================
    # CLEAR ERROR
    # =====================================================

    def clear_error(
        self,
    ) -> None:

        self.last_error = None

    # =====================================================
    # RESET
    # =====================================================

    def reset(
        self,
    ) -> None:

        self.clear_results()

        self.last_market_data = {}

        self.scan_count = 0

        self.running = False

        self.last_error = None

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(
        self,
    ) -> None:
        """
        Compatibility alias for stop().
        """

        self.stop()

    # =====================================================
    # LENGTH
    # =====================================================

    def __len__(
        self,
    ) -> int:

        return self.result_count

    # =====================================================
    # BOOLEAN
    # =====================================================

    def __bool__(
        self,
    ) -> bool:

        return self.has_results

    # =====================================================
    # ITERATION
    # =====================================================

    def __iter__(
        self,
    ):

        return iter(
            self.results
        )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"started={self.started}, "

            f"running={self.running}, "

            f"scanners={len(self.scanner_names)}, "

            f"results={self.result_count})"
        )


# =========================================================
# DEFAULT SERVICE
# =========================================================

_default_service: Optional[
    ScannerService
] = None


def get_scanner_service(
) -> ScannerService:
    """
    Return shared ScannerService instance.
    """

    global _default_service

    if _default_service is None:

        _default_service = (
            ScannerService()
        )

    return _default_service


# =========================================================
# FACTORY
# =========================================================

def create_scanner_service(
    *,
    auto_start: bool = True,
    parallel: bool = True,
    max_workers: int = 8,
    debug: bool = False,
) -> ScannerService:
    """
    Create a ScannerService instance.
    """

    return ScannerService(

        auto_start=auto_start,

        parallel=parallel,

        max_workers=max_workers,

        debug=debug,
    )


# =========================================================
# CONVENIENCE FUNCTIONS
# =========================================================

def start_scanner_service(
) -> bool:

    return get_scanner_service().start()


def stop_scanner_service(
) -> None:

    get_scanner_service().stop()


def scan_market(
    market_data: Dict[str, Any],
) -> List[Signal]:

    return get_scanner_service().scan(
        market_data
    )


def refresh_market_scan(
    market_data: Optional[
        Dict[str, Any]
    ] = None,
) -> List[Signal]:

    return get_scanner_service().refresh(
        market_data
    )


def get_scanner_results(
) -> List[Signal]:

    return get_scanner_service().results


def get_scanner_status(
) -> Dict[str, Any]:

    return get_scanner_service().status()


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "ScannerService",

    "create_scanner_service",

    "get_scanner_service",

    "start_scanner_service",

    "stop_scanner_service",

    "scan_market",

    "refresh_market_scan",

    "get_scanner_results",

    "get_scanner_status",
]


# ==========================
# END OF FILE
# ==========================