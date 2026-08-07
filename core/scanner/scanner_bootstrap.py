"""
=========================================================
StockVersity Scanner Pro
Scanner Bootstrap
Version : 2.0
=========================================================

Central bootstrap for the complete scanner subsystem.

Responsibilities
----------------
• Create ScannerEngine
• Create ScannerManager
• Create MarketDataBridge
• Create ScannerScheduler
• Register available scanners
• Start / stop scanner services
• Provide one clean interface for main.py

Architecture
------------
ScannerBootstrap
    ↓
ScannerEngine
    ↓
ScannerManager
    ↓
MarketDataBridge
    ↓
ScannerScheduler

=========================================================
"""

from __future__ import annotations

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Type

from core.scanner.signal import Signal
from core.scanner.base_scanner import BaseScanner

from core.scanner.scanner_engine import (
    ScannerEngine,
    create_scanner_engine,
)

from core.scanner.scanner_manager import (
    ScannerManager,
)

from core.scanner.market_data_bridge import (
    MarketDataBridge,
)

from core.scanner.scanner_scheduler import (
    ScannerScheduler,
    create_scanner_scheduler,
)


# =========================================================
# OPTIONAL SCANNER IMPORTS
# =========================================================

try:
    from core.scanner.momentum_scanner import (
        MomentumScanner,
    )
except ImportError:
    MomentumScanner = None


try:
    from core.scanner.orb_scanner import (
        ORBScanner,
    )
except ImportError:
    ORBScanner = None


try:
    from core.scanner.breakout_scanner import (
        BreakoutScanner,
    )
except ImportError:
    BreakoutScanner = None


try:
    from core.scanner.vcp_scanner import (
        VCPScanner,
    )
except ImportError:
    VCPScanner = None


try:
    from core.scanner.swing import (
        SwingScanner,
    )
except ImportError:
    SwingScanner = None


try:
    from core.scanner.positional_scanner import (
        PositionalScanner,
    )
except ImportError:
    PositionalScanner = None


# =========================================================
# DEFAULT CONFIGURATION
# =========================================================

DEFAULT_CONFIG: Dict[str, Any] = {

    # -----------------------------------------------------
    # ENGINE
    # -----------------------------------------------------

    "parallel": True,

    "max_workers": 8,

    "debug": False,

    # -----------------------------------------------------
    # SCHEDULER
    # -----------------------------------------------------

    "intraday_interval": 60,

    "swing_interval": 900,

    "positional_interval": 3600,

    "market_hours_only": True,

    # -----------------------------------------------------
    # MARKET DATA BRIDGE
    # -----------------------------------------------------

    "auto_scan": False,

    # -----------------------------------------------------
    # SCANNER FILTERS
    # -----------------------------------------------------

    "minimum_price": 200.0,

    "minimum_market_cap": 1000.0,

    "minimum_score": 60.0,

    "minimum_rr": 2.0,

    # -----------------------------------------------------
    # RESULT CONTROL
    # -----------------------------------------------------

    "max_signals_per_scanner": 50,
}


# =========================================================
# SCANNER BOOTSTRAP
# =========================================================

class ScannerBootstrap:
    """
    Main bootstrap/controller for the StockVersity
    scanner subsystem.

    main.py should normally create only one instance:

        scanner_system = ScannerBootstrap()

    The bootstrap then creates and connects:

        ScannerEngine
        ScannerManager
        MarketDataBridge
        ScannerScheduler
        Individual scanners
    """

    def __init__(
        self,
        config: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        # -------------------------------------------------
        # CONFIGURATION
        # -------------------------------------------------

        self.config: Dict[
            str,
            Any
        ] = dict(
            DEFAULT_CONFIG
        )

        if config:

            self.config.update(
                config
            )

        self.debug = bool(
            self.config.get(
                "debug",
                False,
            )
        )

        # -------------------------------------------------
        # COMPONENTS
        # -------------------------------------------------

        self.engine: Optional[
            ScannerEngine
        ] = None

        self.manager: Optional[
            ScannerManager
        ] = None

        self.bridge: Optional[
            MarketDataBridge
        ] = None

        self.scheduler: Optional[
            ScannerScheduler
        ] = None

        # -------------------------------------------------
        # STATE
        # -------------------------------------------------

        self.initialized = False

        self.started = False

        self.last_error: Optional[
            str
        ] = None

        self.registered_scanner_names: List[
            str
        ] = []

    # =====================================================
    # INITIALIZE
    # =====================================================

    def initialize(
        self,
    ) -> "ScannerBootstrap":
        """
        Build and connect complete scanner infrastructure.
        """

        if self.initialized:

            return self

        self.last_error = None

        try:

            # =============================================
            # ENGINE
            # =============================================

            self.engine = create_scanner_engine(

                parallel=bool(
                    self.config.get(
                        "parallel",
                        True,
                    )
                ),

                max_workers=int(
                    self.config.get(
                        "max_workers",
                        8,
                    )
                ),

                debug=self.debug,
            )

            # =============================================
            # MANAGER
            # =============================================
            #
            # IMPORTANT:
            # ScannerManager uses keyword-only parameters.
            # Therefore engine MUST be passed as engine=.
            #
            # auto_load=False prevents registry scanners
            # being loaded automatically because this
            # bootstrap performs explicit registration.
            # =============================================

            self.manager = ScannerManager(

                engine=self.engine,

                auto_load=True,

                debug=self.debug,
            )

            # =============================================
            # REGISTER SCANNERS
            # =============================================

            # Production scanners are loaded centrally by
            # ScannerManager / ScannerRegistry.  Do not also
            # register Bootstrap-local scanner implementations.
            self.registered_scanner_names = list(
                self.engine.registered_scanners
            )

            # =============================================
            # MARKET DATA BRIDGE
            # =============================================

            self.bridge = MarketDataBridge(

                manager=self.manager,

                debug=self.debug,

                auto_scan=bool(
                    self.config.get(
                        "auto_scan",
                        False,
                    )
                ),
            )

            # =============================================
            # SCHEDULER
            # =============================================

            self.scheduler = create_scanner_scheduler(

                manager=self.manager,

                bridge=self.bridge,

                intraday_interval=int(
                    self.config.get(
                        "intraday_interval",
                        60,
                    )
                ),

                swing_interval=int(
                    self.config.get(
                        "swing_interval",
                        900,
                    )
                ),

                positional_interval=int(
                    self.config.get(
                        "positional_interval",
                        3600,
                    )
                ),

                market_hours_only=bool(
                    self.config.get(
                        "market_hours_only",
                        True,
                    )
                ),

                debug=self.debug,
            )

            # =============================================
            # COMPLETE
            # =============================================

            self.initialized = True

            self.started = False

            self.last_error = None

            self.log(
                "Scanner system initialized."
            )

            self.log(
                "Registered scanners:",
                self.registered_scanner_names,
            )

            return self

        except Exception as exc:

            self.initialized = False

            self.started = False

            self.last_error = (
                f"{type(exc).__name__}: {exc}"
            )

            self.log(
                "Initialization failed:",
                self.last_error,
            )

            raise

    # =====================================================
    # REGISTER DEFAULT SCANNERS
    # =====================================================

    def _register_default_scanners(
        self,
    ) -> None:
        """
        Register every scanner currently available.

        Scanner imports are optional so one unfinished
        scanner does not prevent the complete application
        from starting.
        """

        if self.engine is None:

            raise RuntimeError(
                "ScannerEngine has not been created."
            )

        scanner_classes: List[
            Optional[
                Type[BaseScanner]
            ]
        ] = [

            MomentumScanner,

            ORBScanner,

            BreakoutScanner,

            VCPScanner,

            SwingScanner,

            PositionalScanner,
        ]

        for scanner_class in scanner_classes:

            if scanner_class is None:

                continue

            try:

                scanner = scanner_class()

                self._configure_scanner(
                    scanner
                )

                existing = self.engine.get(
                    scanner.name
                )

                if existing is not None:

                    if (
                        scanner.name
                        not in
                        self.registered_scanner_names
                    ):

                        self.registered_scanner_names.append(
                            scanner.name
                        )

                    continue

                self.engine.register(
                    scanner
                )

                if (
                    scanner.name
                    not in
                    self.registered_scanner_names
                ):

                    self.registered_scanner_names.append(
                        scanner.name
                    )

                self.log(
                    "Registered:",
                    scanner.name,
                )

            except Exception as exc:

                self.log(
                    "Scanner registration skipped:",
                    getattr(
                        scanner_class,
                        "__name__",
                        scanner_class,
                    ),
                    exc,
                )

    # =====================================================
    # CONFIGURE SCANNER
    # =====================================================

    def _configure_scanner(
        self,
        scanner: BaseScanner,
    ) -> None:
        """
        Apply global bootstrap configuration to scanner.
        """

        scanner.minimum_score = float(
            self.config.get(
                "minimum_score",
                60.0,
            )
        )

        scanner.minimum_rr = float(
            self.config.get(
                "minimum_rr",
                2.0,
            )
        )

        scanner.max_signals = int(
            self.config.get(
                "max_signals_per_scanner",
                50,
            )
        )

        scanner.debug = self.debug

    # =====================================================
    # REGISTER CUSTOM SCANNER
    # =====================================================

    def register_scanner(
        self,
        scanner: BaseScanner,
    ) -> bool:
        """
        Register a scanner after initialization.
        """

        if not isinstance(
            scanner,
            BaseScanner,
        ):

            raise TypeError(
                "scanner must inherit BaseScanner."
            )

        self._require_initialized()

        if self.engine is None:

            raise RuntimeError(
                "ScannerEngine unavailable."
            )

        if self.engine.get(
            scanner.name
        ) is not None:

            return False

        self._configure_scanner(
            scanner
        )

        self.engine.register(
            scanner
        )

        if (
            scanner.name
            not in self.registered_scanner_names
        ):

            self.registered_scanner_names.append(
                scanner.name
            )

        self.log(
            "Custom scanner registered:",
            scanner.name,
        )

        return True

    # =====================================================
    # UNREGISTER SCANNER
    # =====================================================

    def unregister_scanner(
        self,
        scanner_name: str,
    ) -> bool:

        self._require_initialized()

        if self.engine is None:

            return False

        if self.engine.get(
            scanner_name
        ) is None:

            return False

        self.engine.unregister(
            scanner_name
        )

        normalized_name = (
            scanner_name
            .strip()
            .lower()
        )

        self.registered_scanner_names = [

            name

            for name
            in self.registered_scanner_names

            if (
                name.strip().lower()
                != normalized_name
            )
        ]

        return True

    # =====================================================
    # START
    # =====================================================

    def start(
        self,
    ) -> None:
        """
        Start scanner scheduler.
        """

        if not self.initialized:

            self.initialize()

        if self.started:

            return

        if self.scheduler is None:

            raise RuntimeError(
                "ScannerScheduler unavailable."
            )

        self.scheduler.start()

        self.started = True

        self.last_error = None

        self.log(
            "Scanner system started."
        )

    # =====================================================
    # STOP
    # =====================================================

    def stop(
        self,
    ) -> None:
        """
        Stop scheduled scanning while keeping the scanner
        subsystem initialized.
        """

        if self.scheduler is not None:

            self.scheduler.stop()

        if self.engine is not None:

            self.engine.cleanup()

        self.started = False

        self.log(
            "Scanner system stopped."
        )

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(
        self,
    ) -> None:
        """
        Fully shutdown scanner subsystem.
        """

        if self.scheduler is not None:

            self.scheduler.stop()

        if self.engine is not None:

            self.engine.shutdown()

        self.started = False

        self.initialized = False

        self.scheduler = None

        self.bridge = None

        self.manager = None

        self.engine = None

        self.registered_scanner_names = []

        self.log(
            "Scanner system shutdown completed."
        )

    # =====================================================
    # PAUSE
    # =====================================================

    def pause(
        self,
    ) -> None:

        self._require_initialized()

        if self.scheduler is not None:

            self.scheduler.pause()

    # =====================================================
    # RESUME
    # =====================================================

    def resume(
        self,
    ) -> None:

        self._require_initialized()

        if self.scheduler is not None:

            self.scheduler.resume()

    # =====================================================
    # MARKET DATA UPDATE
    # =====================================================

    def update_market_data(
        self,
        instrument_key: str,
        data: Dict[str, Any],
    ) -> None:
        """
        Send one live market-data update into the bridge.

        The instrument key supplied by the feed is injected
        into the quote before normalization.
        """

        self._require_initialized()

        if self.bridge is None:

            raise RuntimeError(
                "MarketDataBridge unavailable."
            )

        if not isinstance(
            data,
            dict,
        ):

            raise TypeError(
                "data must be a dictionary."
            )

        quote = dict(
            data
        )

        if instrument_key:

            quote[
                "instrument_key"
            ] = instrument_key

        self.bridge.update_quote(
            quote
        )

    # =====================================================
    # UPDATE MANY MARKET QUOTES
    # =====================================================

    def update_market_quotes(
        self,
        quotes: List[
            Dict[str, Any]
        ],
        *,
        trigger_scan: bool = False,
    ) -> int:
        """
        Send multiple quotes into MarketDataBridge.
        """

        self._require_initialized()

        if self.bridge is None:

            raise RuntimeError(
                "MarketDataBridge unavailable."
            )

        return self.bridge.update_quotes(
            quotes,
            trigger_scan=trigger_scan,
        )

    # =====================================================
    # ADD CANDLE
    # =====================================================

    def add_candle(
        self,
        instrument_key: str,
        timeframe: str,
        candle: Dict[str, Any],
        *,
        symbol: str = "",
        max_candles: int = 500,
    ) -> None:
        """
        Add one OHLCV candle to MarketDataBridge.
        """

        self._require_initialized()

        if self.bridge is None:

            raise RuntimeError(
                "MarketDataBridge unavailable."
            )

        self.bridge.add_candle(

            instrument_key,

            timeframe,

            candle,

            symbol=symbol,

            max_candles=max_candles,
        )

    # =====================================================
    # MANUAL SCAN
    # =====================================================

    def scan_now(
        self,
    ) -> List[Signal]:
        """
        Force immediate complete scan.
        """

        self._require_initialized()

        if self.scheduler is None:

            raise RuntimeError(
                "ScannerScheduler unavailable."
            )

        return self.scheduler.run_all()

    # =====================================================
    # RESULTS
    # =====================================================

    def results(
        self,
    ) -> List[Signal]:

        if self.engine is None:

            return []

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

        if self.engine is None:

            return []

        return self.engine.priority_ranking(
            limit
        )

    # =====================================================
    # DASHBOARD FEED
    # =====================================================

    def dashboard_feed(
        self,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:

        if self.engine is None:

            return []

        return self.engine.dashboard_feed(
            limit
        )

    # =====================================================
    # DASHBOARD SUMMARY
    # =====================================================

    def dashboard_summary(
        self,
    ) -> Dict[str, Any]:

        if self.engine is None:

            return {}

        return self.engine.dashboard_summary()

    # =====================================================
    # ALERTS
    # =====================================================

    def alerts(
        self,
        minimum_score: float = 85.0,
    ) -> List[Dict[str, Any]]:

        if self.engine is None:

            return []

        return self.engine.build_alert_queue(
            minimum_score
        )

    # =====================================================
    # MARKET SENTIMENT
    # =====================================================

    def market_sentiment(
        self,
    ) -> str:

        if self.engine is None:

            return "UNKNOWN"

        return self.engine.market_sentiment()

    # =====================================================
    # MARKET HEALTH
    # =====================================================

    def market_health(
        self,
    ) -> float:

        if self.engine is None:

            return 0.0

        return float(
            self.engine.market_health_score()
        )

    # =====================================================
    # ENABLE SCANNER
    # =====================================================

    def enable_scanner(
        self,
        scanner_name: str,
    ) -> bool:

        self._require_initialized()

        if self.manager is None:

            return False

        return self.manager.enable(
            scanner_name
        )

    # =====================================================
    # DISABLE SCANNER
    # =====================================================

    def disable_scanner(
        self,
        scanner_name: str,
    ) -> bool:

        self._require_initialized()

        if self.manager is None:

            return False

        return self.manager.disable(
            scanner_name
        )

    # =====================================================
    # STATUS
    # =====================================================

    def status(
        self,
    ) -> Dict[str, Any]:

        engine_status: Dict[
            str,
            Any
        ] = {}

        manager_status: Dict[
            str,
            Any
        ] = {}

        bridge_status: Dict[
            str,
            Any
        ] = {}

        scheduler_status: Dict[
            str,
            Any
        ] = {}

        if self.engine is not None:

            engine_status = (
                self.engine.status()
            )

        if self.manager is not None:

            manager_status = (
                self.manager.status()
            )

        if self.bridge is not None:

            bridge_status = (
                self.bridge.status()
            )

        if self.scheduler is not None:

            scheduler_status = (
                self.scheduler.status()
            )

        return {

            "initialized":
                self.initialized,

            "started":
                self.started,

            "registered_scanners":
                list(
                    self.registered_scanner_names
                ),

            "engine":
                engine_status,

            "manager":
                manager_status,

            "bridge":
                bridge_status,

            "scheduler":
                scheduler_status,

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

        if not self.initialized:

            issues.append(
                "Scanner system not initialized."
            )

        if self.engine is None:

            issues.append(
                "ScannerEngine missing."
            )

        if self.manager is None:

            issues.append(
                "ScannerManager missing."
            )

        if self.bridge is None:

            issues.append(
                "MarketDataBridge missing."
            )

        if self.scheduler is None:

            issues.append(
                "ScannerScheduler missing."
            )

        if self.last_error:

            issues.append(
                self.last_error
            )

        engine_health: Dict[
            str,
            Any
        ] = {}

        bridge_health: Dict[
            str,
            Any
        ] = {}

        scheduler_health: Dict[
            str,
            Any
        ] = {}

        if self.engine is not None:

            try:

                engine_health = (
                    self.engine.health_check()
                )

                if not engine_health.get(
                    "healthy",
                    True,
                ):

                    issues.extend(
                        engine_health.get(
                            "issues",
                            [],
                        )
                    )

            except Exception as exc:

                issues.append(
                    "Engine health check failed: "
                    f"{type(exc).__name__}: {exc}"
                )

        if self.bridge is not None:

            bridge_health = (
                self.bridge.health_check()
            )

            if not bridge_health.get(
                "healthy",
                True,
            ):

                issues.extend(
                    bridge_health.get(
                        "issues",
                        [],
                    )
                )

        if self.scheduler is not None:

            scheduler_health = (
                self.scheduler.health_check()
            )

            if not scheduler_health.get(
                "healthy",
                True,
            ):

                issues.extend(
                    scheduler_health.get(
                        "issues",
                        [],
                    )
                )

        return {

            "healthy":
                len(issues) == 0,

            "issues":
                issues,

            "initialized":
                self.initialized,

            "started":
                self.started,

            "engine":
                engine_health,

            "bridge":
                bridge_health,

            "scheduler":
                scheduler_health,
        }

    # =====================================================
    # REQUIRE INITIALIZED
    # =====================================================

    def _require_initialized(
        self,
    ) -> None:

        if not self.initialized:

            self.initialize()

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
            "[ScannerBootstrap]",
            *message,
        )

    # =====================================================
    # CONTEXT MANAGER
    # =====================================================

    def __enter__(
        self,
    ) -> "ScannerBootstrap":

        self.initialize()

        self.start()

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:

        self.shutdown()

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (

            "ScannerBootstrap("

            f"initialized={self.initialized}, "

            f"started={self.started}, "

            f"scanners="
            f"{len(self.registered_scanner_names)}"

            ")"
        )

    def __str__(
        self,
    ) -> str:

        return (

            "StockVersity Scanner System | "

            f"{len(self.registered_scanner_names)} scanners | "

            f"{'RUNNING' if self.started else 'STOPPED'}"
        )


# =========================================================
# FACTORY
# =========================================================

def create_scanner_system(
    config: Optional[
        Dict[str, Any]
    ] = None,
    *,
    auto_initialize: bool = True,
    auto_start: bool = False,
) -> ScannerBootstrap:
    """
    Create complete StockVersity scanner system.
    """

    system = ScannerBootstrap(
        config=config
    )

    if auto_initialize:

        system.initialize()

    if auto_start:

        system.start()

    return system


# =========================================================
# DEFAULT INSTANCE
# =========================================================

_default_scanner_system: Optional[
    ScannerBootstrap
] = None


def get_scanner_system(
) -> ScannerBootstrap:
    """
    Return shared ScannerBootstrap instance.
    """

    global _default_scanner_system

    if _default_scanner_system is None:

        _default_scanner_system = (
            ScannerBootstrap()
        )

    return _default_scanner_system


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "ScannerBootstrap",

    "create_scanner_system",

    "get_scanner_system",

    "DEFAULT_CONFIG",
]


# ==========================
# END OF FILE
# ==========================