"""
=========================================================
StockVersity Scanner Pro
Scanner Loader
Version : 2.0
=========================================================

Automatically discovers and loads scanner classes
from the scanner implementation package.

Framework:
    core/scanner/

Scanner implementations:
    core/scanners/
=========================================================
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil

from typing import Any
from typing import List
from typing import Optional
from typing import Type

from core.scanner.base_scanner import BaseScanner
from core.scanner.scanner_engine import ScannerEngine


# =========================================================
# DEFAULT SCANNER PACKAGE
# =========================================================

DEFAULT_SCANNER_PACKAGE = "core.scanners"


# =========================================================
# SCANNER LOADER
# =========================================================

class ScannerLoader:
    """
    Automatically discover, instantiate and register
    scanner classes.

    Expected structure:

        core/
        ├── scanner/
        │   ├── __init__.py
        │   ├── signal.py
        │   ├── base_scanner.py
        │   ├── scanner_engine.py
        │   ├── scanner_registry.py
        │   └── scanner_loader.py
        │
        └── scanners/
            ├── __init__.py
            ├── momentum.py
            ├── orb.py
            ├── breakout.py
            ├── vcp.py
            ├── swing.py
            └── positional.py

    Every scanner implementation must inherit BaseScanner.
    """

    def __init__(
        self,
        package_name: str = DEFAULT_SCANNER_PACKAGE,
        debug: bool = False,
    ) -> None:

        self.package_name = package_name
        self.debug = debug

        self.scanner_classes: List[
            Type[BaseScanner]
        ] = []

        self.scanners: List[
            BaseScanner
        ] = []

        self.loaded_modules: List[str] = []

        self.failed_modules: List[str] = []

        self.errors: List[str] = []

    # =====================================================
    # LOGGING
    # =====================================================

    def log(
        self,
        *message: Any,
    ) -> None:

        if not self.debug:
            return

        print(
            "[ScannerLoader]",
            *message,
        )

    # =====================================================
    # IMPORT SCANNER PACKAGE
    # =====================================================

    def _import_package(self):

        try:

            return importlib.import_module(
                self.package_name
            )

        except ModuleNotFoundError as exc:

            raise RuntimeError(
                f"Scanner package "
                f"'{self.package_name}' "
                f"could not be found."
            ) from exc

    # =====================================================
    # DISCOVER MODULES
    # =====================================================

    def discover_modules(
        self,
    ) -> List[str]:
        """
        Discover Python modules inside core.scanners.
        """

        package = self._import_package()

        if not hasattr(
            package,
            "__path__",
        ):

            raise RuntimeError(
                f"'{self.package_name}' "
                f"is not a Python package."
            )

        modules: List[str] = []

        for module_info in pkgutil.iter_modules(
            package.__path__
        ):

            module_name = module_info.name

            # Ignore private modules.
            if module_name.startswith("_"):
                continue

            full_name = (
                f"{self.package_name}."
                f"{module_name}"
            )

            modules.append(
                full_name
            )

        return sorted(
            modules
        )

    # =====================================================
    # IMPORT MODULE
    # =====================================================

    def import_module(
        self,
        module_name: str,
    ):

        try:

            module = importlib.import_module(
                module_name
            )

            if module_name not in self.loaded_modules:

                self.loaded_modules.append(
                    module_name
                )

            self.log(
                "Loaded:",
                module_name,
            )

            return module

        except Exception as exc:

            if module_name not in self.failed_modules:

                self.failed_modules.append(
                    module_name
                )

            error_message = (
                f"{module_name}: "
                f"{type(exc).__name__}: "
                f"{exc}"
            )

            self.errors.append(
                error_message
            )

            self.log(
                "Failed:",
                error_message,
            )

            return None

    # =====================================================
    # FIND SCANNER CLASSES
    # =====================================================

    def find_scanner_classes(
        self,
        module,
    ) -> List[Type[BaseScanner]]:
        """
        Find concrete BaseScanner subclasses
        defined directly inside a scanner module.
        """

        discovered: List[
            Type[BaseScanner]
        ] = []

        for _, obj in inspect.getmembers(
            module,
            inspect.isclass,
        ):

            if obj is BaseScanner:
                continue

            try:

                is_scanner = issubclass(
                    obj,
                    BaseScanner,
                )

            except TypeError:

                continue

            if not is_scanner:
                continue

            # Ignore classes imported from other modules.
            if obj.__module__ != module.__name__:
                continue

            # Ignore abstract classes.
            if inspect.isabstract(obj):
                continue

            discovered.append(
                obj
            )

        return discovered

    # =====================================================
    # DISCOVER SCANNERS
    # =====================================================

    def discover(
        self,
    ) -> List[Type[BaseScanner]]:
        """
        Discover every scanner class inside
        the configured scanner package.
        """

        self.scanner_classes.clear()

        self.loaded_modules.clear()

        self.failed_modules.clear()

        self.errors.clear()

        modules = self.discover_modules()

        seen = set()

        for module_name in modules:

            module = self.import_module(
                module_name
            )

            if module is None:
                continue

            classes = self.find_scanner_classes(
                module
            )

            for scanner_class in classes:

                key = (
                    scanner_class.__module__,
                    scanner_class.__name__,
                )

                if key in seen:
                    continue

                seen.add(
                    key
                )

                self.scanner_classes.append(
                    scanner_class
                )

        self.log(
            "Scanner classes discovered:",
            len(self.scanner_classes),
        )

        return list(
            self.scanner_classes
        )

    # =====================================================
    # CREATE ONE SCANNER
    # =====================================================

    def create_scanner(
        self,
        scanner_class: Type[BaseScanner],
    ) -> Optional[BaseScanner]:
        """
        Instantiate one scanner class.

        Scanner implementations should normally
        support construction without arguments.
        """

        try:

            scanner = scanner_class()

            if not isinstance(
                scanner,
                BaseScanner,
            ):

                return None

            return scanner

        except Exception as exc:

            error_message = (
                f"{scanner_class.__name__}: "
                f"{type(exc).__name__}: "
                f"{exc}"
            )

            self.errors.append(
                error_message
            )

            self.log(
                "Could not create scanner:",
                error_message,
            )

            return None

    # =====================================================
    # CREATE ALL SCANNERS
    # =====================================================

    def create_all(
        self,
    ) -> List[BaseScanner]:
        """
        Instantiate every discovered scanner.
        """

        if not self.scanner_classes:

            self.discover()

        self.scanners.clear()

        seen_names = set()

        for scanner_class in self.scanner_classes:

            scanner = self.create_scanner(
                scanner_class
            )

            if scanner is None:
                continue

            scanner_name = (
                scanner.name
                .strip()
                .lower()
            )

            if not scanner_name:

                self.errors.append(
                    f"{scanner_class.__name__} "
                    f"has an empty scanner name."
                )

                continue

            if scanner_name in seen_names:

                self.errors.append(
                    f"Duplicate scanner ignored: "
                    f"{scanner.name}"
                )

                continue

            seen_names.add(
                scanner_name
            )

            self.scanners.append(
                scanner
            )

        self.log(
            "Scanner instances created:",
            len(self.scanners),
        )

        return list(
            self.scanners
        )

    # =====================================================
    # LOAD INTO ENGINE
    # =====================================================

    def load_into(
        self,
        engine: ScannerEngine,
    ) -> List[BaseScanner]:
        """
        Discover scanners, create them and
        register them with ScannerEngine.
        """

        if not isinstance(
            engine,
            ScannerEngine,
        ):

            raise TypeError(
                "engine must be a ScannerEngine instance."
            )

        scanners = self.create_all()

        for scanner in scanners:

            existing = engine.get(
                scanner.name
            )

            if existing is not None:
                continue

            engine.register(
                scanner
            )

        return scanners

    # =====================================================
    # GET SCANNER INSTANCE
    # =====================================================

    def get(
        self,
        scanner_name: str,
    ) -> Optional[BaseScanner]:

        search_name = (
            scanner_name
            .strip()
            .lower()
        )

        for scanner in self.scanners:

            if (
                scanner.name
                .strip()
                .lower()
                == search_name
            ):

                return scanner

        return None

    # =====================================================
    # HAS SCANNER
    # =====================================================

    def has(
        self,
        scanner_name: str,
    ) -> bool:

        return self.get(
            scanner_name
        ) is not None

    # =====================================================
    # SCANNER NAMES
    # =====================================================

    @property
    def scanner_names(
        self,
    ) -> List[str]:

        return sorted(
            scanner.name
            for scanner in self.scanners
        )

    # =====================================================
    # CLASS NAMES
    # =====================================================

    @property
    def class_names(
        self,
    ) -> List[str]:

        return sorted(
            scanner_class.__name__
            for scanner_class
            in self.scanner_classes
        )

    # =====================================================
    # MODULE COUNT
    # =====================================================

    @property
    def module_count(
        self,
    ) -> int:

        return len(
            self.loaded_modules
        )

    # =====================================================
    # SCANNER COUNT
    # =====================================================

    @property
    def scanner_count(
        self,
    ) -> int:

        return len(
            self.scanners
        )

    # =====================================================
    # STATUS
    # =====================================================

    def status(
        self,
    ) -> dict:
        """
        Return scanner loader status.
        """

        return {

            "package":
                self.package_name,

            "modules_loaded":
                len(
                    self.loaded_modules
                ),

            "modules_failed":
                len(
                    self.failed_modules
                ),

            "classes_discovered":
                len(
                    self.scanner_classes
                ),

            "scanners_created":
                len(
                    self.scanners
                ),

            "scanner_names":
                self.scanner_names,

            "failed_modules":
                list(
                    self.failed_modules
                ),

            "errors":
                list(
                    self.errors
                ),

        }

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(
        self,
    ) -> dict:
        """
        Basic loader health check.
        """

        issues: List[str] = []

        if self.failed_modules:

            issues.append(
                f"{len(self.failed_modules)} "
                f"scanner module(s) failed to load."
            )

        if self.errors:

            issues.extend(
                self.errors
            )

        return {

            "healthy":
                len(issues) == 0,

            "issues":
                issues,

            "package":
                self.package_name,

            "loaded_modules":
                len(
                    self.loaded_modules
                ),

            "scanner_classes":
                len(
                    self.scanner_classes
                ),

            "scanner_instances":
                len(
                    self.scanners
                ),

        }

    # =====================================================
    # RESET
    # =====================================================

    def reset(
        self,
    ) -> None:
        """
        Reset loader runtime state.
        """

        self.scanner_classes.clear()

        self.scanners.clear()

        self.loaded_modules.clear()

        self.failed_modules.clear()

        self.errors.clear()

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh(
        self,
    ) -> List[BaseScanner]:
        """
        Rediscover and recreate scanners.
        """

        self.reset()

        self.discover()

        return self.create_all()

    # =====================================================
    # MAGIC METHODS
    # =====================================================

    def __len__(
        self,
    ) -> int:

        return len(
            self.scanners
        )

    def __iter__(
        self,
    ):

        return iter(
            self.scanners
        )

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
    # REPRESENTATION
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (
            f"ScannerLoader("
            f"package='{self.package_name}', "
            f"classes={len(self.scanner_classes)}, "
            f"scanners={len(self.scanners)}, "
            f"failed={len(self.failed_modules)})"
        )


# =========================================================
# DEFAULT LOADER
# =========================================================

scanner_loader = ScannerLoader()


# =========================================================
# FACTORY
# =========================================================

def create_scanner_loader(
    package_name: str = DEFAULT_SCANNER_PACKAGE,
    debug: bool = False,
) -> ScannerLoader:
    """
    Create a configured ScannerLoader.
    """

    return ScannerLoader(
        package_name=package_name,
        debug=debug,
    )


# =========================================================
# LOAD SCANNERS HELPER
# =========================================================

def load_scanners(
    engine: ScannerEngine,
    package_name: str = DEFAULT_SCANNER_PACKAGE,
    debug: bool = False,
) -> List[BaseScanner]:
    """
    Discover scanner implementations and
    register them directly with ScannerEngine.
    """

    loader = ScannerLoader(
        package_name=package_name,
        debug=debug,
    )

    return loader.load_into(
        engine
    )


# =========================================================
# DISCOVER SCANNERS HELPER
# =========================================================

def discover_scanners(
    package_name: str = DEFAULT_SCANNER_PACKAGE,
    debug: bool = False,
) -> List[Type[BaseScanner]]:
    """
    Discover scanner classes without creating them.
    """

    loader = ScannerLoader(
        package_name=package_name,
        debug=debug,
    )

    return loader.discover()


# =========================================================
# EXPORTS
# =========================================================

__all__ = [

    "ScannerLoader",

    "scanner_loader",

    "create_scanner_loader",

    "load_scanners",

    "discover_scanners",

    "DEFAULT_SCANNER_PACKAGE",

]


# ==========================
# END OF FILE
# ==========================