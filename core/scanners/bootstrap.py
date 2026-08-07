"""
=========================================================
StockVersity Scanner Pro
Scanner Bootstrap
Version : 2.1
=========================================================

File:
    core/scanner/bootstrap.py

Purpose
-------
Bootstrap and connect the StockVersity scanner subsystem.

Architecture
------------
core.scanners
      ↓
ScannerRegistry
      ↓
Scanner Instances
      ↓
ScannerEngine
      ↓
Market Scan

Responsibilities
----------------
• Load default scanner classes
• Instantiate enabled scanners
• Register scanners with ScannerEngine
• Prevent duplicate engine registration
• Rebuild scanner engine
• Validate scanner bootstrap
• Provide bootstrap diagnostics
=========================================================
"""

from __future__ import annotations

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from core.scanner.base_scanner import BaseScanner

from core.scanner.registry import (
    ScannerRegistry,
    scanner_registry,
    load_default_scanners,
)

from core.scanner.scanner_engine import (
    ScannerEngine,
    create_scanner_engine,
)


# =========================================================
# VERSION
# =========================================================

BOOTSTRAP_VERSION = "2.1"


# =========================================================
# SCANNER BOOTSTRAP
# =========================================================

class ScannerBootstrap:
    """
    Connect ScannerRegistry with ScannerEngine.

    Typical usage
    -------------

    bootstrap = ScannerBootstrap()

    engine = bootstrap.initialize()

    results = engine.run(
        market_data
    )
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        *,
        registry: Optional[ScannerRegistry] = None,
        engine: Optional[ScannerEngine] = None,
        parallel: bool = True,
        max_workers: int = 8,
        debug: bool = False,
    ) -> None:

        self.registry = (
            registry
            if registry is not None
            else scanner_registry
        )

        self.parallel = bool(
            parallel
        )

        self.max_workers = max(
            1,
            int(max_workers),
        )

        self.debug = bool(
            debug
        )

        self.engine = (
            engine
            if engine is not None
            else create_scanner_engine(
                parallel=self.parallel,
                max_workers=self.max_workers,
                debug=self.debug,
            )
        )

        self.initialized = False

        self.last_error: Optional[str] = None

        self.created_scanners: List[
            BaseScanner
        ] = []

    # =====================================================
    # LOAD REGISTRY
    # =====================================================

    def load_registry(
        self,
    ) -> ScannerRegistry:
        """
        Load all default scanner classes into registry.

        Safe to call repeatedly because ScannerRegistry
        already protects against duplicate registration.
        """

        try:

            load_default_scanners()

            self.last_error = None

        except Exception as exc:

            self.last_error = (
                f"{type(exc).__name__}: "
                f"{exc}"
            )

            self.log(
                "Registry load failed:",
                self.last_error,
            )

            raise

        return self.registry

    # =====================================================
    # CREATE SCANNERS
    # =====================================================

    def create_scanners(
        self,
    ) -> List[BaseScanner]:
        """
        Instantiate all currently enabled scanner classes.
        """

        self.created_scanners = (
            self.registry.create_all()
        )

        return list(
            self.created_scanners
        )

    # =====================================================
    # REGISTER WITH ENGINE
    # =====================================================

    def register_scanners(
        self,
        scanners: Optional[List[BaseScanner]] = None,
    ) -> int:
        """
        Register scanner instances with ScannerEngine.

        Existing scanner names are skipped to make
        bootstrap initialization idempotent.
        """

        if scanners is None:

            scanners = (
                self.created_scanners
            )

        registered = 0

        for scanner in scanners:

            if self.engine.has_scanner(
                scanner.name
            ):

                self.log(
                    "Scanner already in engine:",
                    scanner.name,
                )

                continue

            self.engine.register(
                scanner,
                enabled=True,
            )

            registered += 1

        return registered

    # =====================================================
    # INITIALIZE
    # =====================================================

    def initialize(
        self,
    ) -> ScannerEngine:
        """
        Initialize complete scanner execution layer.

        Steps
        -----
        1. Load scanner classes.
        2. Instantiate enabled scanners.
        3. Register instances with engine.
        4. Validate resulting configuration.
        """

        self.last_error = None

        try:

            self.load_registry()

            scanners = (
                self.create_scanners()
            )

            self.register_scanners(
                scanners
            )

            errors = (
                self.validate()
            )

            if errors:

                raise RuntimeError(
                    "Scanner bootstrap validation failed: "
                    + "; ".join(errors)
                )

            self.initialized = True

            self.log(
                "Bootstrap initialized.",
                f"Registry={len(self.registry)}",
                f"Engine={len(self.engine.scanners)}",
            )

            return self.engine

        except Exception as exc:

            self.initialized = False

            self.last_error = (
                f"{type(exc).__name__}: "
                f"{exc}"
            )

            self.log(
                "Bootstrap failed:",
                self.last_error,
            )

            raise

    # =====================================================
    # REBUILD ENGINE
    # =====================================================

    def rebuild(
        self,
    ) -> ScannerEngine:
        """
        Recreate ScannerEngine and reload all enabled
        scanner instances.

        Useful after registry configuration changes.
        """

        self.engine = (
            create_scanner_engine(
                parallel=self.parallel,
                max_workers=self.max_workers,
                debug=self.debug,
            )
        )

        self.created_scanners = []

        self.initialized = False

        return self.initialize()

    # =====================================================
    # REFRESH REGISTRY
    # =====================================================

    def refresh(
        self,
    ) -> ScannerEngine:
        """
        Rebuild engine using current registry state.
        """

        return self.rebuild()

    # =====================================================
    # ENABLE SCANNER
    # =====================================================

    def enable(
        self,
        scanner_name: str,
    ) -> bool:
        """
        Enable scanner in registry and rebuild engine.
        """

        success = (
            self.registry.enable(
                scanner_name
            )
        )

        if not success:

            return False

        self.rebuild()

        return True

    # =====================================================
    # DISABLE SCANNER
    # =====================================================

    def disable(
        self,
        scanner_name: str,
    ) -> bool:
        """
        Disable scanner in registry and rebuild engine.
        """

        success = (
            self.registry.disable(
                scanner_name
            )
        )

        if not success:

            return False

        self.rebuild()

        return True

    # =====================================================
    # ENABLE ALL
    # =====================================================

    def enable_all(
        self,
    ) -> None:

        self.registry.enable_all()

        self.rebuild()

    # =====================================================
    # DISABLE ALL
    # =====================================================

    def disable_all(
        self,
    ) -> None:

        self.registry.disable_all()

        self.engine.disable_all()

        self.created_scanners = []

        self.initialized = True

    # =====================================================
    # GET SCANNER
    # =====================================================

    def get_scanner(
        self,
        scanner_name: str,
    ) -> Optional[BaseScanner]:
        """
        Return running scanner instance from engine.

        Supports engine scanner name first, then registry
        class name lookup.
        """

        scanner = (
            self.engine.get(
                scanner_name
            )
        )

        if scanner is not None:

            return scanner

        normalized = (
            str(scanner_name)
            .strip()
            .lower()
        )

        for scanner in (
            self.engine.scanners.values()
        ):

            class_name = (
                scanner.__class__.__name__
                .lower()
            )

            if class_name == normalized:

                return scanner

        return None

    # =====================================================
    # RUN
    # =====================================================

    def run(
        self,
        market_data: Dict[str, Any],
    ):
        """
        Run current scanner engine.

        Automatically initializes bootstrap when needed.
        """

        if not self.initialized:

            self.initialize()

        return self.engine.run(
            market_data
        )

    # =====================================================
    # VALIDATE
    # =====================================================

    def validate(
        self,
    ) -> List[str]:
        """
        Validate registry → engine integration.
        """

        errors: List[str] = []

        registry_errors = (
            self.registry.errors
        )

        if registry_errors:

            for name, error in (
                registry_errors.items()
            ):

                errors.append(
                    f"Registry error "
                    f"[{name}]: {error}"
                )

        engine_errors = (
            self.engine.validate_scanners()
        )

        errors.extend(
            engine_errors
        )

        enabled_registry_names = set(
            self.registry.enabled_names
        )

        engine_class_names = {

            scanner.__class__.__name__

            for scanner in (
                self.engine.scanners.values()
            )

        }

        missing = (
            enabled_registry_names
            - engine_class_names
        )

        for scanner_name in sorted(
            missing
        ):

            errors.append(
                f"Enabled registry scanner "
                f"not loaded into engine: "
                f"{scanner_name}"
            )

        return errors

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(
        self,
    ) -> Dict[str, Any]:

        errors = (
            self.validate()
        )

        registry_health = (
            self.registry.health_check()
        )

        engine_health = (
            self.engine.health_check()
        )

        return {

            "healthy": (
                not errors
                and registry_health.get(
                    "healthy",
                    False,
                )
                and engine_health.get(
                    "healthy",
                    False,
                )
            ),

            "initialized":
                self.initialized,

            "errors":
                errors,

            "registry":
                registry_health,

            "engine":
                engine_health,

        }

    # =====================================================
    # STATUS
    # =====================================================

    def status(
        self,
    ) -> Dict[str, Any]:

        return {

            "version":
                BOOTSTRAP_VERSION,

            "initialized":
                self.initialized,

            "registry_registered":
                len(
                    self.registry
                ),

            "registry_enabled":
                len(
                    self.registry.enabled_names
                ),

            "engine_registered":
                len(
                    self.engine.scanners
                ),

            "engine_enabled":
                len(
                    self.engine.enabled_scanners
                ),

            "created_instances":
                len(
                    self.created_scanners
                ),

            "last_error":
                self.last_error,

        }

    # =====================================================
    # DIAGNOSTICS
    # =====================================================

    def diagnostics(
        self,
    ) -> Dict[str, Any]:

        return {

            "bootstrap":
                self.status(),

            "health":
                self.health_check(),

            "registry":
                self.registry.status(),

            "engine":
                self.engine.diagnostics(),

            "validation_errors":
                self.validate(),

        }

    # =====================================================
    # RESET
    # =====================================================

    def reset(
        self,
    ) -> None:
        """
        Reset runtime results while preserving scanner
        registry and scanner registration.
        """

        self.engine.reset()

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(
        self,
    ) -> None:
        """
        Shutdown scanner execution layer.

        Registry classes remain registered.
        """

        self.engine.shutdown()

        self.created_scanners = []

        self.initialized = False

    # =====================================================
    # CONFIGURE
    # =====================================================

    def configure(
        self,
        *,
        parallel: Optional[bool] = None,
        max_workers: Optional[int] = None,
        debug: Optional[bool] = None,
    ) -> None:

        if parallel is not None:

            self.parallel = bool(
                parallel
            )

        if max_workers is not None:

            self.max_workers = max(
                1,
                int(max_workers),
            )

        if debug is not None:

            self.debug = bool(
                debug
            )

        self.engine.configure(
            parallel=parallel,
            max_workers=max_workers,
            debug=debug,
        )

    # =====================================================
    # LOG
    # =====================================================

    def log(
        self,
        *args: Any,
    ) -> None:

        if not self.debug:

            return

        print(
            "[ScannerBootstrap]",
            *args,
        )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"initialized={self.initialized}, "
            f"registry={len(self.registry)}, "
            f"engine={len(self.engine.scanners)})"
        )


# =========================================================
# GLOBAL BOOTSTRAP
# =========================================================

scanner_bootstrap = (
    ScannerBootstrap()
)


# =========================================================
# INITIALIZE DEFAULT ENGINE
# =========================================================

def initialize_scanner_engine(
) -> ScannerEngine:
    """
    Initialize default StockVersity scanner engine.
    """

    return (
        scanner_bootstrap.initialize()
    )


# =========================================================
# GET ENGINE
# =========================================================

def get_scanner_engine(
) -> ScannerEngine:
    """
    Return global ScannerEngine.

    Initializes scanner system if required.
    """

    if not scanner_bootstrap.initialized:

        scanner_bootstrap.initialize()

    return scanner_bootstrap.engine


# =========================================================
# REBUILD ENGINE
# =========================================================

def rebuild_scanner_engine(
) -> ScannerEngine:

    return (
        scanner_bootstrap.rebuild()
    )


# =========================================================
# BOOTSTRAP STATUS
# =========================================================

def get_scanner_bootstrap_status(
) -> Dict[str, Any]:

    return (
        scanner_bootstrap.status()
    )


# =========================================================
# BOOTSTRAP HEALTH
# =========================================================

def get_scanner_bootstrap_health(
) -> Dict[str, Any]:

    return (
        scanner_bootstrap.health_check()
    )


# =========================================================
# EXPORTS
# =========================================================

__all__ = [

    "ScannerBootstrap",

    "scanner_bootstrap",

    "initialize_scanner_engine",

    "get_scanner_engine",

    "rebuild_scanner_engine",

    "get_scanner_bootstrap_status",

    "get_scanner_bootstrap_health",

]


# =========================================================
# END OF FILE
# =========================================================