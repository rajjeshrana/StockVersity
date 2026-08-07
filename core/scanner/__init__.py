"""
=========================================================
StockVersity Scanner Pro
Scanner Core Package
Version : 2.1
=========================================================

File:
    core/scanner/__init__.py

Purpose:
    Public interface for the StockVersity scanner core.

Current core components:
    • Signal model
    • Base scanner
    • Scanner registry
    • Scanner engine
=========================================================
"""

from __future__ import annotations


# =========================================================
# PACKAGE INFORMATION
# =========================================================

__version__ = "2.1"

__package_name__ = "StockVersity Scanner Pro"


# =========================================================
# SIGNAL MODEL
# =========================================================

from core.scanner.signal import (
    Signal,
    SignalType,
    SignalStrength,
    PatternType,
    SignalStatus,
    MarketTrend,
    DEFAULT_EXCHANGE,
    DEFAULT_TIMEFRAME,
    DEFAULT_CAPITAL,
    DEFAULT_RISK_PERCENT,
    SCORE_KEYS,
    create_signal,
)


# =========================================================
# BASE SCANNER
# =========================================================

from core.scanner.base_scanner import (
    BaseScanner,
)


# =========================================================
# SCANNER REGISTRY
# =========================================================

from core.scanner.registry import (
    ScannerRegistry,
    scanner_registry,
    load_default_scanners,
    create_default_scanners,
)


# =========================================================
# SCANNER ENGINE
# =========================================================

from core.scanner.scanner_engine import (
    ScannerEngine,
    create_scanner_engine,
)


# =========================================================
# CREATE DEFAULT ENGINE
# =========================================================

def create_default_engine(
    *,
    parallel: bool = True,
    max_workers: int = 8,
    debug: bool = False,
) -> ScannerEngine:
    """
    Create a ScannerEngine and register all currently
    enabled scanners from the global scanner registry.

    Returns
    -------
    ScannerEngine
        Configured scanner execution engine.
    """

    engine = create_scanner_engine(
        parallel=parallel,
        max_workers=max_workers,
        debug=debug,
    )

    scanners = create_default_scanners()

    if scanners:

        engine.register_many(
            scanners,
            enabled=True,
        )

    return engine


# =========================================================
# CORE STATUS
# =========================================================

def core_status():
    """
    Return basic scanner-core status.
    """

    return {
        "package": __package_name__,
        "version": __version__,
        "registry": scanner_registry.status(),
    }


# =========================================================
# CORE HEALTH
# =========================================================

def core_health():
    """
    Return basic scanner-core health information.
    """

    return {
        "package": __package_name__,
        "version": __version__,
        "registry": scanner_registry.health_check(),
    }


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    # -----------------------------------------------------
    # PACKAGE
    # -----------------------------------------------------

    "__version__",
    "__package_name__",

    # -----------------------------------------------------
    # SIGNAL
    # -----------------------------------------------------

    "Signal",
    "SignalType",
    "SignalStrength",
    "PatternType",
    "SignalStatus",
    "MarketTrend",
    "DEFAULT_EXCHANGE",
    "DEFAULT_TIMEFRAME",
    "DEFAULT_CAPITAL",
    "DEFAULT_RISK_PERCENT",
    "SCORE_KEYS",
    "create_signal",

    # -----------------------------------------------------
    # BASE SCANNER
    # -----------------------------------------------------

    "BaseScanner",

    # -----------------------------------------------------
    # REGISTRY
    # -----------------------------------------------------

    "ScannerRegistry",
    "scanner_registry",
    "load_default_scanners",
    "create_default_scanners",

    # -----------------------------------------------------
    # ENGINE
    # -----------------------------------------------------

    "ScannerEngine",
    "create_scanner_engine",
    "create_default_engine",

    # -----------------------------------------------------
    # STATUS
    # -----------------------------------------------------

    "core_status",
    "core_health",
]


# =========================================================
# END OF FILE
# =========================================================