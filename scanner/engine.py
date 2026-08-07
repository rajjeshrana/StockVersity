"""
=========================================================
StockVersity Scanner Pro
Scanner Engine Compatibility Module
Version : 2.0
=========================================================

Purpose
-------
Provides a stable import path for the StockVersity
ScannerEngine.

The actual ScannerEngine implementation lives in:

    core.scanner.scanner_engine

This file intentionally DOES NOT contain another
ScannerEngine implementation.

Recommended imports
-------------------

Either:

    from core.scanner.engine import ScannerEngine

or:

    from core.scanner.scanner_engine import ScannerEngine

Both point to the same implementation.
=========================================================
"""

from __future__ import annotations


# =========================================================
# SCANNER ENGINE
# =========================================================

from core.scanner.scanner_engine import ScannerEngine
from core.scanner.scanner_engine import create_scanner_engine


# =========================================================
# FACTORY ALIAS
# =========================================================

def create_engine(
    *,
    parallel: bool = True,
    max_workers: int = 8,
    debug: bool = False,
) -> ScannerEngine:
    """
    Convenience factory.

    This is an alias around create_scanner_engine().

    Example
    -------

    engine = create_engine(
        parallel=True,
        max_workers=8,
        debug=False,
    )
    """

    return create_scanner_engine(
        parallel=parallel,
        max_workers=max_workers,
        debug=debug,
    )


# =========================================================
# ENGINE TYPE CHECK
# =========================================================

def is_scanner_engine(
    instance: object,
) -> bool:
    """
    Check whether an object is a ScannerEngine instance.
    """

    return isinstance(
        instance,
        ScannerEngine,
    )


# =========================================================
# DEFAULT ENGINE
# =========================================================

def default_engine() -> ScannerEngine:
    """
    Create a ScannerEngine using StockVersity defaults.

    A new instance is returned on every call.
    """

    return create_scanner_engine(
        parallel=True,
        max_workers=8,
        debug=False,
    )


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "ScannerEngine",

    "create_scanner_engine",

    "create_engine",

    "default_engine",

    "is_scanner_engine",

]


# ==========================
# END OF FILE
# ==========================