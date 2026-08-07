"""
=========================================================
StockVersity Scanner Pro
Scanners Package
Version : 2.1
=========================================================

File:
    core/scanners/__init__.py

Purpose
-------
Central scanner package registration.

Responsibilities
----------------
• Import all production scanners
• Expose scanner classes
• Provide get_scanner_classes()
• Provide scanner lookup
• Keep ScannerRegistry integration centralized
=========================================================
"""

from __future__ import annotations

from typing import Dict
from typing import List
from typing import Optional
from typing import Type

from core.scanner.base_scanner import BaseScanner


# =========================================================
# SCANNER IMPORTS
# =========================================================

from core.scanners.momentum_scanner import (
    MomentumScanner,
)

from core.scanners.orb_scanner import (
    ORBScanner,
)

from core.scanners.swing_scanner import (
    SwingScanner,
)

from core.scanners.breakout_scanner import (
    BreakoutScanner,
)

from core.scanners.vcp_scanner import (
    VCPScanner,
)

from core.scanners.bull_flag_scanner import (
    BullFlagScanner,
)

from core.scanners.falling_wedge_scanner import (
    FallingWedgeScanner,
)

from core.scanners.cup_handle_scanner import (
    CupHandleScanner,
)

from core.scanners.sector_rotation_scanner import (
    SectorRotationScanner,
)

from core.scanners.relative_strength_scanner import (
    RelativeStrengthScanner,
)


# =========================================================
# SCANNER CLASS LIST
# =========================================================

SCANNER_CLASSES: List[
    Type[BaseScanner]
] = [

    MomentumScanner,

    ORBScanner,

    SwingScanner,

    BreakoutScanner,

    VCPScanner,

    BullFlagScanner,

    FallingWedgeScanner,

    CupHandleScanner,

    SectorRotationScanner,

    RelativeStrengthScanner,

]


# =========================================================
# SCANNER CLASS MAP
# =========================================================

SCANNER_CLASS_MAP: Dict[
    str,
    Type[BaseScanner]
] = {

    scanner_class.__name__:
        scanner_class

    for scanner_class
    in SCANNER_CLASSES

}


# =========================================================
# NORMALIZED CLASS MAP
# =========================================================

_NORMALIZED_SCANNER_MAP: Dict[
    str,
    Type[BaseScanner]
] = {

    scanner_class.__name__.lower():
        scanner_class

    for scanner_class
    in SCANNER_CLASSES

}


# =========================================================
# GET SCANNER CLASSES
# =========================================================

def get_scanner_classes(
) -> List[Type[BaseScanner]]:
    """
    Return every production scanner class.

    ScannerRegistry uses this function to load
    default scanners.

    Returns
    -------
    List[Type[BaseScanner]]
    """

    return list(
        SCANNER_CLASSES
    )


# =========================================================
# GET SCANNER CLASS
# =========================================================

def get_scanner_class(
    scanner_name: str,
) -> Optional[Type[BaseScanner]]:
    """
    Find scanner class by class name.

    Lookup is case-insensitive.

    Example
    -------
    get_scanner_class(
        "MomentumScanner"
    )

    get_scanner_class(
        "momentumscanner"
    )
    """

    if not scanner_name:

        return None

    key = str(
        scanner_name
    ).strip().lower()

    return (
        _NORMALIZED_SCANNER_MAP.get(
            key
        )
    )


# =========================================================
# HAS SCANNER
# =========================================================

def has_scanner(
    scanner_name: str,
) -> bool:
    """
    Check whether scanner exists.
    """

    return (
        get_scanner_class(
            scanner_name
        )
        is not None
    )


# =========================================================
# CREATE SCANNER
# =========================================================

def create_scanner(
    scanner_name: str,
    **kwargs,
) -> Optional[BaseScanner]:
    """
    Create one scanner directly from the scanners package.

    Registry remains the recommended high-level interface,
    but this helper is useful for testing.
    """

    scanner_class = (
        get_scanner_class(
            scanner_name
        )
    )

    if scanner_class is None:

        return None

    return scanner_class(
        **kwargs
    )


# =========================================================
# CREATE ALL SCANNERS
# =========================================================

def create_all_scanners(
) -> List[BaseScanner]:
    """
    Create every production scanner.

    Scanner initialization errors are intentionally not
    hidden here so configuration problems can be detected
    during development/testing.
    """

    return [

        scanner_class()

        for scanner_class
        in SCANNER_CLASSES

    ]


# =========================================================
# SCANNER NAMES
# =========================================================

def get_scanner_names(
) -> List[str]:
    """
    Return registered production scanner class names.
    """

    return [

        scanner_class.__name__

        for scanner_class
        in SCANNER_CLASSES

    ]


# =========================================================
# SCANNER COUNT
# =========================================================

def scanner_count(
) -> int:
    """
    Number of production scanners.
    """

    return len(
        SCANNER_CLASSES
    )


# =========================================================
# VALIDATE SCANNERS
# =========================================================

def validate_scanner_classes(
) -> List[str]:
    """
    Validate scanner package configuration.

    Returns an empty list when everything is valid.
    """

    errors: List[str] = []

    names = set()

    for scanner_class in (
        SCANNER_CLASSES
    ):

        # ---------------------------------------------
        # CLASS CHECK
        # ---------------------------------------------

        if not isinstance(
            scanner_class,
            type,
        ):

            errors.append(
                f"{scanner_class!r} "
                f"is not a class."
            )

            continue

        # ---------------------------------------------
        # BASE CLASS CHECK
        # ---------------------------------------------

        if not issubclass(
            scanner_class,
            BaseScanner,
        ):

            errors.append(
                f"{scanner_class.__name__} "
                f"does not inherit BaseScanner."
            )

            continue

        # ---------------------------------------------
        # DUPLICATE CHECK
        # ---------------------------------------------

        name = (
            scanner_class.__name__
        )

        normalized = (
            name.lower()
        )

        if normalized in names:

            errors.append(
                f"Duplicate scanner class: "
                f"{name}"
            )

        names.add(
            normalized
        )

    return errors


# =========================================================
# PACKAGE STATUS
# =========================================================

def scanner_package_status(
) -> Dict[str, object]:
    """
    Return scanner package diagnostics.
    """

    errors = (
        validate_scanner_classes()
    )

    return {

        "version":
            __version__,

        "scanner_count":
            len(
                SCANNER_CLASSES
            ),

        "scanner_names":
            get_scanner_names(),

        "healthy":
            not errors,

        "errors":
            errors,

    }


# =========================================================
# PACKAGE INFORMATION
# =========================================================

__version__ = "2.1"

__package_name__ = (
    "StockVersity Scanner Pro - Scanners"
)


# =========================================================
# EXPORTS
# =========================================================

__all__ = [

    # ---------------------------------------------
    # SCANNER CLASSES
    # ---------------------------------------------

    "MomentumScanner",

    "ORBScanner",

    "SwingScanner",

    "BreakoutScanner",

    "VCPScanner",

    "BullFlagScanner",

    "FallingWedgeScanner",

    "CupHandleScanner",

    "SectorRotationScanner",

    "RelativeStrengthScanner",

    # ---------------------------------------------
    # COLLECTIONS
    # ---------------------------------------------

    "SCANNER_CLASSES",

    "SCANNER_CLASS_MAP",

    # ---------------------------------------------
    # HELPERS
    # ---------------------------------------------

    "get_scanner_classes",

    "get_scanner_class",

    "has_scanner",

    "create_scanner",

    "create_all_scanners",

    "get_scanner_names",

    "scanner_count",

    "validate_scanner_classes",

    "scanner_package_status",

    # ---------------------------------------------
    # PACKAGE
    # ---------------------------------------------

    "__version__",

    "__package_name__",
]


# =========================================================
# END OF FILE
# =========================================================