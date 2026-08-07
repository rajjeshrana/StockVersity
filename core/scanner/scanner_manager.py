"""
=========================================================
StockVersity Scanner Pro
Scanner Manager
Version : 2.0
=========================================================

High-level scanner management layer.

Responsibilities
----------------
â€¢ Load scanner classes from registry
â€¢ Create scanner instances
â€¢ Register scanners with ScannerEngine
â€¢ Enable / disable scanners
â€¢ Run scans
â€¢ Refresh scans
â€¢ Provide dashboard data
â€¢ Provide scanner diagnostics
=========================================================
"""

from __future__ import annotations

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from core.scanner.base_scanner import BaseScanner
from core.scanner.signal import Signal
from core.scanner.scanner_engine import ScannerEngine
from core.scanner.scanner_engine import create_scanner_engine

from core.scanner.scanner_registry import ScannerRegistry
from core.scanner.scanner_registry import scanner_registry
from core.scanner.scanner_registry import load_default_scanners


# =========================================================
# SCANNER MANAGER
# =========================================================

class ScannerManager:
    """
    High-level controller for StockVersity scanners.

    Architecture
    ------------

    ScannerRegistry
        â†“
    ScannerManager
        â†“
    ScannerEngine
        â†“
    Individual Scanners
        â†“
    Signals
    """

    def __init__(
        self,
        *,
        registry: Optional[ScannerRegistry] = None,
        engine: Optional[ScannerEngine] = None,
        auto_load: bool = True,
        parallel: bool = True,
        max_workers: int = 8,
        debug: bool = False,
    ) -> None:

        # -------------------------------------------------
        # REGISTRY
        # -------------------------------------------------

        self.registry = (
            registry
            if registry is not None
            else scanner_registry
        )

        # -------------------------------------------------
        # ENGINE
        # -------------------------------------------------

        self.engine = (
            engine
            if engine is not None
            else create_scanner_engine(
                parallel=parallel,
                max_workers=max_workers,
                debug=debug,
            )
        )

        # -------------------------------------------------
        # STATE
        # -------------------------------------------------

        self.debug = debug

        self.loaded = False

        self.last_market_data: Dict[
            str,
            Any
        ] = {}

        self.last_results: List[
            Signal
        ] = []

        self.errors: List[
            str
        ] = []

        # -------------------------------------------------
        # AUTO LOAD
        # -------------------------------------------------

        if auto_load:

            self.load_scanners()

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
            "[ScannerManager]",
            *message,
        )

    # =====================================================
    # LOAD SCANNERS
    # =====================================================

    def load_scanners(
        self,
        *,
        reload: bool = False,
    ) -> List[BaseScanner]:
        """
        Load all enabled scanners from registry and
        register them with ScannerEngine.
        """

        if reload:

            self.engine.disable_all()

            self.engine.scanners.clear()

            self.engine.enabled_scanners.clear()

        # -------------------------------------------------
        # LOAD DEFAULT REGISTRY
        # -------------------------------------------------

        try:

            load_default_scanners()

        except Exception as exc:

            self._add_error(
                "Registry loading failed",
                exc,
            )

        # -------------------------------------------------
        # CREATE SCANNERS
        # -------------------------------------------------

        try:

            scanners = (
                self.registry.create_all()
            )

        except Exception as exc:

            self._add_error(
                "Scanner creation failed",
                exc,
            )

            scanners = []

        # -------------------------------------------------
        # REGISTER WITH ENGINE
        # -------------------------------------------------

        existing_names = {

            scanner.name

            for scanner
            in self.engine.scanners.values()

        }

        for scanner in scanners:

            try:

                if scanner.name in existing_names:
                    continue

                self.engine.register(
                    scanner
                )

                existing_names.add(
                    scanner.name
                )

            except Exception as exc:

                self._add_error(
                    f"Failed to register "
                    f"{getattr(scanner, 'name', scanner)}",
                    exc,
                )

        self.loaded = True

        return list(self.engine.scanners.values())

    # =====================================================
    # RELOAD
    # =====================================================

    def reload(
        self,
    ) -> List[BaseScanner]:
        """
        Reload scanner instances.
        """

        return self.load_scanners(
            reload=True
        )

    # =====================================================
    # ADD SCANNER
    # =====================================================

    def add_scanner(
        self,
        scanner: BaseScanner,
    ) -> bool:
        """
        Add scanner directly to engine.
        """

        if not isinstance(
            scanner,
            BaseScanner,
        ):

            raise TypeError(
                "scanner must inherit BaseScanner."
            )

        if self.engine.get(
            scanner.name
        ) is not None:

            return False

        self.engine.register(
            scanner
        )

        return True

    # =====================================================
    # REMOVE SCANNER
    # =====================================================

    def remove_scanner(
        self,
        scanner_name: str,
    ) -> bool:

        if self.engine.get(
            scanner_name
        ) is None:

            return False

        self.engine.unregister(
            scanner_name
        )

        return True

    # =====================================================
    # ENABLE SCANNER
    # =====================================================

    def enable(
        self,
        scanner_name: str,
    ) -> bool:

        scanner = self.engine.get(
            scanner_name
        )

        if scanner is None:

            return False

        self.engine.enable(
            scanner_name
        )

        return True

    # =====================================================
    # DISABLE SCANNER
    # =====================================================

    def disable(
        self,
        scanner_name: str,
    ) -> bool:

        scanner = self.engine.get(
            scanner_name
        )

        if scanner is None:

            return False

        self.engine.disable(
            scanner_name
        )

        return True

    # =====================================================
    # ENABLE ALL
    # =====================================================

    def enable_all(
        self,
    ) -> None:

        self.engine.enable_all()

    # =====================================================
    # DISABLE ALL
    # =====================================================

    def disable_all(
        self,
    ) -> None:

        self.engine.disable_all()

    # =====================================================
    # GET SCANNER
    # =====================================================

    def get_scanner(
        self,
        scanner_name: str,
    ) -> Optional[BaseScanner]:

        return self.engine.get(
            scanner_name
        )

    # =====================================================
    # RUN
    # =====================================================

    def run(
        self,
        market_data: Dict[str, Any],
    ) -> List[Signal]:
        """
        Execute all enabled scanners.
        """

        if not isinstance(
            market_data,
            dict,
        ):

            raise TypeError(
                "market_data must be a dictionary."
            )

        if not self.loaded:

            self.load_scanners()

        self.last_market_data = (
            market_data
        )

        try:

            self.last_results = (
                self.engine.run(
                    market_data
                )
            )

        except Exception as exc:

            self._add_error(
                "Scanner engine execution failed",
                exc,
            )

            raise

        return self.last_results

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
        Re-run scanners.

        If market_data is not supplied, previous
        market data is used.
        """

        data = (
            market_data
            if market_data is not None
            else self.last_market_data
        )

        if not data:

            return []

        self.last_market_data = data

        self.last_results = (
            self.engine.refresh(
                data
            )
        )

        return self.last_results

    # =====================================================
    # RESULTS
    # =====================================================

    @property
    def results(
        self,
    ) -> List[Signal]:

        return list(
            self.engine.results
        )

    # =====================================================
    # TOP OPPORTUNITIES
    # =====================================================

    def top_opportunities(
        self,
        limit: int = 10,
    ) -> List[Signal]:

        return self.engine.priority_ranking(
            limit
        )

    # =====================================================
    # WATCHLIST
    # =====================================================

    def watchlist(
        self,
        limit: int = 25,
    ) -> List[Signal]:

        return self.engine.generate_watchlist(
            limit
        )

    # =====================================================
    # ALERTS
    # =====================================================

    def alerts(
        self,
        minimum_score: float = 85.0,
    ) -> List[Dict[str, Any]]:

        return self.engine.build_alert_queue(
            minimum_score
        )

    # =====================================================
    # BUY SIGNALS
    # =====================================================

    def buy_signals(
        self,
    ) -> List[Signal]:

        return self.engine.buy_signals()

    # =====================================================
    # SELL SIGNALS
    # =====================================================

    def sell_signals(
        self,
    ) -> List[Signal]:

        return self.engine.sell_signals()

    # =====================================================
    # WATCH SIGNALS
    # =====================================================

    def watch_signals(
        self,
    ) -> List[Signal]:

        return self.engine.watch_signals()

    # =====================================================
    # FIND SYMBOL
    # =====================================================

    def find_symbol(
        self,
        symbol: str,
    ) -> Optional[Signal]:

        return self.engine.find_symbol(
            symbol
        )

    # =====================================================
    # FILTER BY SCANNER
    # =====================================================

    def filter_by_scanner(
        self,
        scanner_name: str,
    ) -> List[Signal]:

        return self.engine.filter_by_scanner(
            scanner_name
        )

    # =====================================================
    # FILTER BY SECTOR
    # =====================================================

    def filter_by_sector(
        self,
        sector: str,
    ) -> List[Signal]:

        return self.engine.filter_by_sector(
            sector
        )

    # =====================================================
    # DASHBOARD FEED
    # =====================================================

    def dashboard_feed(
        self,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:

        return self.engine.dashboard_feed(
            limit
        )

    # =====================================================
    # DASHBOARD SUMMARY
    # =====================================================

    def dashboard_summary(
        self,
    ) -> Dict[str, Any]:

        return self.engine.dashboard_summary()

    # =====================================================
    # MARKET SENTIMENT
    # =====================================================

    def market_sentiment(
        self,
    ) -> str:

        return self.engine.market_sentiment()

    # =====================================================
    # MARKET HEALTH
    # =====================================================

    def market_health(
        self,
    ) -> float:

        return self.engine.market_health_score()

    # =====================================================
    # MARKET BREADTH
    # =====================================================

    def market_breadth(
        self,
    ) -> Dict[str, Any]:

        return self.engine.market_breadth()

    # =====================================================
    # SECTOR RANKING
    # =====================================================

    def sector_ranking(
        self,
    ) -> List[Dict[str, Any]]:

        return self.engine.sector_ranking()

    # =====================================================
    # SCANNER RANKING
    # =====================================================

    def scanner_ranking(
        self,
    ) -> List[Dict[str, Any]]:

        return self.engine.scanner_ranking()

    # =====================================================
    # CONSENSUS
    # =====================================================

    def consensus(
        self,
        minimum_scanners: int = 2,
    ) -> List[Dict[str, Any]]:

        return self.engine.consensus_signals(
            minimum_scanners
        )

    # =====================================================
    # SNAPSHOT
    # =====================================================

    def snapshot(
        self,
    ) -> Dict[str, Any]:

        return self.engine.snapshot()

    # =====================================================
    # EXPORT
    # =====================================================

    def export(
        self,
    ) -> List[Dict[str, Any]]:

        return self.engine.export()

    # =====================================================
    # SCANNER NAMES
    # =====================================================

    @property
    def scanner_names(
        self,
    ) -> List[str]:

        return sorted(

            scanner.name

            for scanner in self.engine.scanners.values()

        )

    # =====================================================
    # ACTIVE SCANNERS
    # =====================================================

    @property
    def active_scanners(
        self,
    ) -> List[str]:

        return sorted(

            scanner.name

            for scanner in self.engine.enabled_scanners.values()

        )

    # =====================================================
    # RESULT COUNT
    # =====================================================

    @property
    def result_count(
        self,
    ) -> int:

        return len(
            self.engine.results
        )

    # =====================================================
    # ERROR HANDLING
    # =====================================================

    def _add_error(
        self,
        message: str,
        exception: Exception,
    ) -> None:

        error = (
            f"{message}: "
            f"{type(exception).__name__}: "
            f"{exception}"
        )

        self.errors.append(
            error
        )

        self.log(
            error
        )

    # =====================================================
    # CLEAR ERRORS
    # =====================================================

    def clear_errors(
        self,
    ) -> None:

        self.errors.clear()

    # =====================================================
    # STATUS
    # =====================================================

    def status(
        self,
    ) -> Dict[str, Any]:

        return {

            "loaded":
                self.loaded,

            "registered_scanners":
                len(
                    self.engine.scanners
                ),

            "enabled_scanners":
                len(
                    self.engine.enabled_scanners
                ),

            "scanner_names":
                self.scanner_names,

            "active_scanners":
                self.active_scanners,

            "results":
                self.result_count,

            "market_sentiment":
                self.market_sentiment(),

            "market_health":
                self.market_health(),

            "errors":
                list(
                    self.errors
                ),

        }

    # =====================================================
    # DIAGNOSTICS
    # =====================================================

    def diagnostics(
        self,
    ) -> Dict[str, Any]:

        return {

            "manager":
                self.status(),

            "registry":
                self.registry.status(),

            "engine":
                self.engine.diagnostics(),

        }

    # =====================================================
    # CLEAR RESULTS
    # =====================================================

    def clear_results(
        self,
    ) -> None:

        self.engine.clear_results()

        self.last_results = []

    # =====================================================
    # CLEANUP
    # =====================================================

    def cleanup(
        self,
    ) -> None:

        self.engine.cleanup()

        self.last_results = []

        self.last_market_data = {}

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(
        self,
    ) -> None:

        self.engine.shutdown()

        self.last_results = []

        self.last_market_data = {}

        self.loaded = False

    # =====================================================
    # LENGTH
    # =====================================================

    def __len__(
        self,
    ) -> int:

        return self.result_count

    # =====================================================
    # ITERATION
    # =====================================================

    def __iter__(
        self,
    ):

        return iter(
            self.engine.results
        )

    # =====================================================
    # CONTAINS
    # =====================================================

    def __contains__(
        self,
        symbol: object,
    ) -> bool:

        if not isinstance(
            symbol,
            str,
        ):

            return False

        return symbol in self.engine

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"scanners="
            f"{len(self.engine.scanners)}, "

            f"active="
            f"{len(self.engine.enabled_scanners)}, "

            f"results="
            f"{self.result_count})"

        )


# =========================================================
# FACTORY
# =========================================================

def create_scanner_manager(
    *,
    auto_load: bool = True,
    parallel: bool = True,
    max_workers: int = 8,
    debug: bool = False,
) -> ScannerManager:
    """
    Create configured ScannerManager.
    """

    return ScannerManager(

        auto_load=auto_load,

        parallel=parallel,

        max_workers=max_workers,

        debug=debug,

    )


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "ScannerManager",

    "create_scanner_manager",

]


# ==========================
# END OF FILE
# ==========================

