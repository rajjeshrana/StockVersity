"""
=========================================================
StockVersity Scanner Pro
Scanner Registry
Version : 2.0
=========================================================

Central registry for all StockVersity scanners.

Responsibilities
----------------
• Register scanner classes
• Prevent duplicate registration
• Create scanner instances
• Create all scanners
• Lookup scanners
• Enable / disable scanners
• Registry diagnostics
=========================================================
"""

from __future__ import annotations

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Type

from core.scanner.base_scanner import BaseScanner


# =========================================================
# SCANNER REGISTRY
# =========================================================

class ScannerRegistry:
    """
    Central registry for scanner classes.

    Important
    ---------
    The registry stores scanner CLASSES, not running
    scanner instances.

    Example:

        registry.register(MomentumScanner)

        scanner = registry.create(
            "MomentumScanner"
        )
    """

    def __init__(self) -> None:

        self._scanners: Dict[
            str,
            Type[BaseScanner]
        ] = {}

        self._enabled: Dict[
            str,
            bool
        ] = {}

        self._errors: Dict[
            str,
            str
        ] = {}

    # =====================================================
    # NORMALIZE NAME
    # =====================================================

    @staticmethod
    def _normalize_name(
        name: str,
    ) -> str:
        """
        Normalize scanner name for registry lookup.
        """

        return (
            str(name)
            .strip()
            .lower()
        )

    # =====================================================
    # REGISTER
    # =====================================================

    def register(
        self,
        scanner_class: Type[BaseScanner],
        *,
        enabled: bool = True,
        replace: bool = False,
    ) -> None:
        """
        Register a scanner class.
        """

        if not isinstance(
            scanner_class,
            type,
        ):
            raise TypeError(
                "scanner_class must be a class."
            )

        if not issubclass(
            scanner_class,
            BaseScanner,
        ):
            raise TypeError(
                f"{scanner_class} must inherit BaseScanner."
            )

        if scanner_class is BaseScanner:
            raise TypeError(
                "BaseScanner itself cannot be registered."
            )

        class_name = scanner_class.__name__

        key = self._normalize_name(
            class_name
        )

        if (
            key in self._scanners
            and not replace
        ):
            return

        self._scanners[
            key
        ] = scanner_class

        self._enabled[
            key
        ] = bool(enabled)

    # =====================================================
    # REGISTER MANY
    # =====================================================

    def register_many(
        self,
        scanner_classes: List[
            Type[BaseScanner]
        ],
        *,
        enabled: bool = True,
    ) -> None:
        """
        Register multiple scanner classes.
        """

        for scanner_class in scanner_classes:

            try:

                self.register(
                    scanner_class,
                    enabled=enabled,
                )

            except Exception as exc:

                name = getattr(
                    scanner_class,
                    "__name__",
                    str(scanner_class),
                )

                self._errors[
                    name
                ] = (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                )

    # =====================================================
    # UNREGISTER
    # =====================================================

    def unregister(
        self,
        scanner_name: str,
    ) -> bool:
        """
        Remove scanner from registry.
        """

        key = self._normalize_name(
            scanner_name
        )

        if key not in self._scanners:
            return False

        del self._scanners[
            key
        ]

        self._enabled.pop(
            key,
            None,
        )

        return True

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(
        self,
    ) -> None:
        """
        Clear complete registry.
        """

        self._scanners.clear()

        self._enabled.clear()

        self._errors.clear()

    # =====================================================
    # HAS SCANNER
    # =====================================================

    def has(
        self,
        scanner_name: str,
    ) -> bool:

        key = self._normalize_name(
            scanner_name
        )

        return key in self._scanners

    # =====================================================
    # GET CLASS
    # =====================================================

    def get_class(
        self,
        scanner_name: str,
    ) -> Optional[
        Type[BaseScanner]
    ]:
        """
        Return registered scanner class.
        """

        key = self._normalize_name(
            scanner_name
        )

        return self._scanners.get(
            key
        )

    # =====================================================
    # ENABLE
    # =====================================================

    def enable(
        self,
        scanner_name: str,
    ) -> bool:
        """
        Enable registered scanner.
        """

        key = self._normalize_name(
            scanner_name
        )

        if key not in self._scanners:
            return False

        self._enabled[
            key
        ] = True

        return True

    # =====================================================
    # DISABLE
    # =====================================================

    def disable(
        self,
        scanner_name: str,
    ) -> bool:
        """
        Disable registered scanner.
        """

        key = self._normalize_name(
            scanner_name
        )

        if key not in self._scanners:
            return False

        self._enabled[
            key
        ] = False

        return True

    # =====================================================
    # ENABLE ALL
    # =====================================================

    def enable_all(
        self,
    ) -> None:

        for key in self._scanners:

            self._enabled[
                key
            ] = True

    # =====================================================
    # DISABLE ALL
    # =====================================================

    def disable_all(
        self,
    ) -> None:

        for key in self._scanners:

            self._enabled[
                key
            ] = False

    # =====================================================
    # IS ENABLED
    # =====================================================

    def is_enabled(
        self,
        scanner_name: str,
    ) -> bool:

        key = self._normalize_name(
            scanner_name
        )

        return self._enabled.get(
            key,
            False,
        )

    # =====================================================
    # CREATE
    # =====================================================

    def create(
        self,
        scanner_name: str,
        **kwargs: Any,
    ) -> Optional[BaseScanner]:
        """
        Create scanner instance by class name.
        """

        key = self._normalize_name(
            scanner_name
        )

        scanner_class = (
            self._scanners.get(
                key
            )
        )

        if scanner_class is None:
            return None

        if not self._enabled.get(
            key,
            False,
        ):
            return None

        try:

            return scanner_class(
                **kwargs
            )

        except Exception as exc:

            self._errors[
                scanner_class.__name__
            ] = (
                f"{type(exc).__name__}: "
                f"{exc}"
            )

            return None

    # =====================================================
    # CREATE ALL
    # =====================================================

    def create_all(
        self,
    ) -> List[BaseScanner]:
        """
        Instantiate all enabled scanners.
        """

        instances: List[
            BaseScanner
        ] = []

        for key, scanner_class in (
            self._scanners.items()
        ):

            if not self._enabled.get(
                key,
                False,
            ):
                continue

            try:

                scanner = (
                    scanner_class()
                )

                instances.append(
                    scanner
                )

            except Exception as exc:

                self._errors[
                    scanner_class.__name__
                ] = (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                )

        return instances

    # =====================================================
    # REGISTERED CLASSES
    # =====================================================

    @property
    def scanner_classes(
        self,
    ) -> List[
        Type[BaseScanner]
    ]:

        return list(
            self._scanners.values()
        )

    # =====================================================
    # REGISTERED NAMES
    # =====================================================

    @property
    def scanner_names(
        self,
    ) -> List[str]:

        return sorted(

            scanner_class.__name__

            for scanner_class
            in self._scanners.values()

        )

    # =====================================================
    # ENABLED NAMES
    # =====================================================

    @property
    def enabled_names(
        self,
    ) -> List[str]:

        names: List[str] = []

        for key, scanner_class in (
            self._scanners.items()
        ):

            if self._enabled.get(
                key,
                False,
            ):

                names.append(
                    scanner_class.__name__
                )

        return sorted(
            names
        )

    # =====================================================
    # DISABLED NAMES
    # =====================================================

    @property
    def disabled_names(
        self,
    ) -> List[str]:

        names: List[str] = []

        for key, scanner_class in (
            self._scanners.items()
        ):

            if not self._enabled.get(
                key,
                False,
            ):

                names.append(
                    scanner_class.__name__
                )

        return sorted(
            names
        )

    # =====================================================
    # ERRORS
    # =====================================================

    @property
    def errors(
        self,
    ) -> Dict[str, str]:

        return dict(
            self._errors
        )

    # =====================================================
    # CLEAR ERRORS
    # =====================================================

    def clear_errors(
        self,
    ) -> None:

        self._errors.clear()

    # =====================================================
    # STATUS
    # =====================================================

    def status(
        self,
    ) -> Dict[str, Any]:

        return {

            "registered":
                len(
                    self._scanners
                ),

            "enabled":
                len(
                    self.enabled_names
                ),

            "disabled":
                len(
                    self.disabled_names
                ),

            "scanner_names":
                self.scanner_names,

            "enabled_names":
                self.enabled_names,

            "disabled_names":
                self.disabled_names,

            "errors":
                self.errors,

        }

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(
        self,
    ) -> Dict[str, Any]:

        issues: List[str] = []

        if not self._scanners:

            issues.append(
                "No scanners registered."
            )

        if self._errors:

            issues.append(
                "Scanner registry contains errors."
            )

        return {

            "healthy":
                len(issues) == 0,

            "issues":
                issues,

            "registered":
                len(
                    self._scanners
                ),

            "enabled":
                len(
                    self.enabled_names
                ),

        }

    # =====================================================
    # LENGTH
    # =====================================================

    def __len__(
        self,
    ) -> int:

        return len(
            self._scanners
        )

    # =====================================================
    # CONTAINS
    # =====================================================

    def __contains__(
        self,
        scanner_name: object,
    ) -> bool:

        if not isinstance(
            scanner_name,
            str,
        ):
            return False

        return self.has(
            scanner_name
        )

    # =====================================================
    # ITERATION
    # =====================================================

    def __iter__(
        self,
    ):

        return iter(
            self.scanner_classes
        )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"registered={len(self._scanners)}, "

            f"enabled={len(self.enabled_names)}, "

            f"errors={len(self._errors)})"

        )


# =========================================================
# GLOBAL REGISTRY
# =========================================================

scanner_registry = ScannerRegistry()


# =========================================================
# LOAD DEFAULT SCANNERS
# =========================================================

def load_default_scanners(
) -> ScannerRegistry:
    """
    Load scanner classes exported by core.scanners.

    Safe to call more than once.
    """

    try:

        from core.scanners import (
            get_scanner_classes,
        )

        scanner_classes = (
            get_scanner_classes()
        )

        scanner_registry.register_many(
            scanner_classes
        )

    except Exception as exc:

        scanner_registry._errors[
            "default_loader"
        ] = (
            f"{type(exc).__name__}: "
            f"{exc}"
        )

    return scanner_registry


# =========================================================
# CREATE DEFAULT SCANNERS
# =========================================================

def create_default_scanners(
) -> List[BaseScanner]:
    """
    Load and instantiate all enabled default scanners.
    """

    registry = (
        load_default_scanners()
    )

    return registry.create_all()


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "ScannerRegistry",

    "scanner_registry",

    "load_default_scanners",

    "create_default_scanners",

]


# ==========================
# END OF FILE
# ==========================