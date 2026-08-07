"""
=========================================================
StockVersity Scanner Pro
Scanner Registry
Version : 2.1
=========================================================

File:
    core/scanner/registry.py

Purpose:
    Central registry for all StockVersity scanner classes.

Responsibilities
----------------
• Register scanner classes
• Prevent duplicate registration
• Replace scanner registrations safely
• Enable / disable scanners
• Create scanner instances
• Create all enabled scanners
• Scanner lookup
• Constructor configuration
• Error isolation
• Registry validation
• Diagnostics
• Engine integration
=========================================================
"""

from __future__ import annotations

from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Optional,
    Type,
)

from core.scanner.base_scanner import BaseScanner


# =========================================================
# REGISTRY CONSTANTS
# =========================================================

REGISTRY_NAME = "StockVersity Scanner Registry"

REGISTRY_VERSION = "2.1"


# =========================================================
# SCANNER REGISTRY
# =========================================================

class ScannerRegistry:
    """
    Central registry for StockVersity scanner classes.

    Important
    ---------
    The registry stores scanner CLASSES, not running
    scanner instances.

    Example
    -------

        registry.register(
            MomentumScanner
        )

        scanner = registry.create(
            "MomentumScanner"
        )

    Scanner constructor arguments can also be stored:

        registry.register(
            MomentumScanner,
            config={
                "timeframe": "5m",
            },
        )

    Then:

        scanner = registry.create(
            "MomentumScanner"
        )
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        *,
        debug: bool = False,
    ) -> None:

        # -------------------------------------------------
        # REGISTERED SCANNER CLASSES
        # -------------------------------------------------

        self._scanners: Dict[
            str,
            Type[BaseScanner],
        ] = {}

        # -------------------------------------------------
        # ENABLE / DISABLE STATE
        # -------------------------------------------------

        self._enabled: Dict[
            str,
            bool,
        ] = {}

        # -------------------------------------------------
        # DEFAULT CONSTRUCTOR CONFIGURATION
        # -------------------------------------------------

        self._configs: Dict[
            str,
            Dict[str, Any],
        ] = {}

        # -------------------------------------------------
        # ERRORS
        # -------------------------------------------------

        self._errors: Dict[
            str,
            str,
        ] = {}

        # -------------------------------------------------
        # DEBUG
        # -------------------------------------------------

        self.debug = bool(
            debug
        )

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
    # RESOLVE KEY
    # =====================================================

    def _resolve_key(
        self,
        scanner_name: str,
    ) -> Optional[str]:
        """
        Resolve scanner using class name or scanner alias.

        Primary registry keys are class names.
        """

        key = self._normalize_name(
            scanner_name
        )

        if key in self._scanners:

            return key

        return None

    # =====================================================
    # REGISTER
    # =====================================================

    def register(
        self,
        scanner_class: Type[BaseScanner],
        *,
        enabled: bool = True,
        replace: bool = False,
        config: Optional[
            Dict[str, Any]
        ] = None,
    ) -> bool:
        """
        Register one scanner class.

        Returns
        -------
        bool
            True when registered or replaced.
            False when already registered and replace=False.
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

        class_name = (
            scanner_class.__name__
        )

        key = self._normalize_name(
            class_name
        )

        if (
            key in self._scanners
            and not replace
        ):

            self.log(
                "Scanner already registered:",
                class_name,
            )

            return False

        self._scanners[
            key
        ] = scanner_class

        self._enabled[
            key
        ] = bool(
            enabled
        )

        self._configs[
            key
        ] = dict(
            config or {}
        )

        # Remove an old creation/registration error
        # if this scanner is now registered correctly.
        self._errors.pop(
            class_name,
            None,
        )

        self.log(
            "Registered scanner:",
            class_name,
        )

        return True

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
        replace: bool = False,
    ) -> int:
        """
        Register multiple scanner classes.

        One bad scanner will not prevent remaining
        scanners from being registered.

        Returns
        -------
        int
            Number of successful registrations.
        """

        registered = 0

        for scanner_class in (
            scanner_classes
        ):

            try:

                success = self.register(
                    scanner_class,
                    enabled=enabled,
                    replace=replace,
                )

                if success:

                    registered += 1

            except Exception as exc:

                name = getattr(
                    scanner_class,
                    "__name__",
                    str(scanner_class),
                )

                self._record_error(
                    name,
                    exc,
                )

        return registered

    # =====================================================
    # REGISTER WITH CONFIG
    # =====================================================

    def register_configured(
        self,
        scanner_class: Type[BaseScanner],
        *,
        config: Dict[str, Any],
        enabled: bool = True,
        replace: bool = False,
    ) -> bool:
        """
        Convenience method for registering a scanner
        with constructor configuration.
        """

        return self.register(
            scanner_class,
            enabled=enabled,
            replace=replace,
            config=config,
        )

    # =====================================================
    # UNREGISTER
    # =====================================================

    def unregister(
        self,
        scanner_name: str,
    ) -> bool:
        """
        Remove scanner completely from registry.
        """

        key = self._resolve_key(
            scanner_name
        )

        if key is None:

            return False

        scanner_class = (
            self._scanners.pop(
                key
            )
        )

        self._enabled.pop(
            key,
            None,
        )

        self._configs.pop(
            key,
            None,
        )

        self._errors.pop(
            scanner_class.__name__,
            None,
        )

        self.log(
            "Unregistered scanner:",
            scanner_class.__name__,
        )

        return True

    # =====================================================
    # UNREGISTER MANY
    # =====================================================

    def unregister_many(
        self,
        scanner_names: List[str],
    ) -> int:

        removed = 0

        for scanner_name in (
            scanner_names
        ):

            if self.unregister(
                scanner_name
            ):

                removed += 1

        return removed

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

        self._configs.clear()

        self._errors.clear()

    # =====================================================
    # HAS SCANNER
    # =====================================================

    def has(
        self,
        scanner_name: str,
    ) -> bool:

        return (
            self._resolve_key(
                scanner_name
            )
            is not None
        )

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

        key = self._resolve_key(
            scanner_name
        )

        if key is None:

            return None

        return self._scanners.get(
            key
        )

    # =====================================================
    # GET CONFIG
    # =====================================================

    def get_config(
        self,
        scanner_name: str,
    ) -> Dict[str, Any]:

        key = self._resolve_key(
            scanner_name
        )

        if key is None:

            return {}

        return dict(
            self._configs.get(
                key,
                {},
            )
        )

    # =====================================================
    # SET CONFIG
    # =====================================================

    def set_config(
        self,
        scanner_name: str,
        **config: Any,
    ) -> bool:
        """
        Update default constructor configuration.
        """

        key = self._resolve_key(
            scanner_name
        )

        if key is None:

            return False

        current = self._configs.setdefault(
            key,
            {},
        )

        current.update(
            config
        )

        return True

    # =====================================================
    # REPLACE CONFIG
    # =====================================================

    def replace_config(
        self,
        scanner_name: str,
        config: Dict[str, Any],
    ) -> bool:

        key = self._resolve_key(
            scanner_name
        )

        if key is None:

            return False

        self._configs[
            key
        ] = dict(
            config
        )

        return True

    # =====================================================
    # CLEAR CONFIG
    # =====================================================

    def clear_config(
        self,
        scanner_name: str,
    ) -> bool:

        key = self._resolve_key(
            scanner_name
        )

        if key is None:

            return False

        self._configs[
            key
        ] = {}

        return True

    # =====================================================
    # ENABLE
    # =====================================================

    def enable(
        self,
        scanner_name: str,
    ) -> bool:

        key = self._resolve_key(
            scanner_name
        )

        if key is None:

            return False

        self._enabled[
            key
        ] = True

        self.log(
            "Enabled scanner:",
            self._scanners[
                key
            ].__name__,
        )

        return True

    # =====================================================
    # DISABLE
    # =====================================================

    def disable(
        self,
        scanner_name: str,
    ) -> bool:

        key = self._resolve_key(
            scanner_name
        )

        if key is None:

            return False

        self._enabled[
            key
        ] = False

        self.log(
            "Disabled scanner:",
            self._scanners[
                key
            ].__name__,
        )

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

        key = self._resolve_key(
            scanner_name
        )

        if key is None:

            return False

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
        *,
        allow_disabled: bool = False,
        **kwargs: Any,
    ) -> Optional[BaseScanner]:
        """
        Create scanner instance.

        Stored registry configuration is combined with
        kwargs supplied here.

        Runtime kwargs take priority.
        """

        key = self._resolve_key(
            scanner_name
        )

        if key is None:

            return None

        if (
            not allow_disabled
            and not self._enabled.get(
                key,
                False,
            )
        ):

            return None

        scanner_class = (
            self._scanners[
                key
            ]
        )

        config = dict(
            self._configs.get(
                key,
                {},
            )
        )

        config.update(
            kwargs
        )

        try:

            scanner = scanner_class(
                **config
            )

            if not isinstance(
                scanner,
                BaseScanner,
            ):

                raise TypeError(
                    "Created scanner is not a BaseScanner."
                )

            self._errors.pop(
                scanner_class.__name__,
                None,
            )

            return scanner

        except Exception as exc:

            self._record_error(
                scanner_class.__name__,
                exc,
            )

            return None

    # =====================================================
    # CREATE ALL
    # =====================================================

    def create_all(
        self,
        *,
        include_disabled: bool = False,
        common_config: Optional[
            Dict[str, Any]
        ] = None,
    ) -> List[BaseScanner]:
        """
        Instantiate registered scanners.

        Parameters
        ----------
        include_disabled:
            Instantiate disabled scanners too.

        common_config:
            Optional constructor arguments applied to
            every scanner. These override stored config.
        """

        instances: List[
            BaseScanner
        ] = []

        common = dict(
            common_config or {}
        )

        for key, scanner_class in (
            self._scanners.items()
        ):

            if (
                not include_disabled
                and not self._enabled.get(
                    key,
                    False,
                )
            ):

                continue

            config = dict(
                self._configs.get(
                    key,
                    {},
                )
            )

            config.update(
                common
            )

            try:

                scanner = scanner_class(
                    **config
                )

                if not isinstance(
                    scanner,
                    BaseScanner,
                ):

                    raise TypeError(
                        "Created scanner is not a BaseScanner."
                    )

                instances.append(
                    scanner
                )

                self._errors.pop(
                    scanner_class.__name__,
                    None,
                )

            except Exception as exc:

                self._record_error(
                    scanner_class.__name__,
                    exc,
                )

        return instances

    # =====================================================
    # CREATE ENABLED
    # =====================================================

    def create_enabled(
        self,
    ) -> List[BaseScanner]:

        return self.create_all(
            include_disabled=False
        )

    # =====================================================
    # CREATE FOR ENGINE
    # =====================================================

    def create_for_engine(
        self,
    ) -> List[BaseScanner]:
        """
        Create enabled scanners for ScannerEngine.

        Kept as a separate semantic method so the engine
        integration does not need to know registry details.
        """

        return self.create_enabled()

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
    # RECORD ERROR
    # =====================================================

    def _record_error(
        self,
        scanner_name: str,
        exc: Exception,
    ) -> None:

        self._errors[
            scanner_name
        ] = (
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        self.log(
            "Scanner registry error:",
            scanner_name,
            self._errors[
                scanner_name
            ],
        )

    # =====================================================
    # CLEAR ERRORS
    # =====================================================

    def clear_errors(
        self,
    ) -> None:

        self._errors.clear()

    # =====================================================
    # VALIDATE
    # =====================================================

    def validate(
        self,
    ) -> List[str]:
        """
        Validate internal registry consistency.
        """

        issues: List[str] = []

        for key, scanner_class in (
            self._scanners.items()
        ):

            expected_key = (
                self._normalize_name(
                    scanner_class.__name__
                )
            )

            if key != expected_key:

                issues.append(
                    "Scanner key mismatch: "
                    f"{key} != {expected_key}"
                )

            if not issubclass(
                scanner_class,
                BaseScanner,
            ):

                issues.append(
                    f"{scanner_class.__name__} "
                    "does not inherit BaseScanner."
                )

            if key not in self._enabled:

                issues.append(
                    "Missing enabled state: "
                    f"{scanner_class.__name__}"
                )

            if key not in self._configs:

                issues.append(
                    "Missing scanner configuration: "
                    f"{scanner_class.__name__}"
                )

        for key in self._enabled:

            if key not in self._scanners:

                issues.append(
                    "Orphan enabled state: "
                    f"{key}"
                )

        for key in self._configs:

            if key not in self._scanners:

                issues.append(
                    "Orphan scanner config: "
                    f"{key}"
                )

        return issues

    # =====================================================
    # TEST INSTANTIATION
    # =====================================================

    def validate_instances(
        self,
        *,
        enabled_only: bool = True,
    ) -> List[str]:
        """
        Try constructing scanners to identify broken
        scanner constructors.

        This does not execute scans.
        """

        issues: List[str] = []

        for key, scanner_class in (
            self._scanners.items()
        ):

            if (
                enabled_only
                and not self._enabled.get(
                    key,
                    False,
                )
            ):

                continue

            config = dict(
                self._configs.get(
                    key,
                    {},
                )
            )

            try:

                scanner = scanner_class(
                    **config
                )

                if not isinstance(
                    scanner,
                    BaseScanner,
                ):

                    issues.append(
                        f"{scanner_class.__name__}: "
                        "invalid scanner instance."
                    )

            except Exception as exc:

                message = (
                    f"{scanner_class.__name__}: "
                    f"{type(exc).__name__}: "
                    f"{exc}"
                )

                issues.append(
                    message
                )

                self._record_error(
                    scanner_class.__name__,
                    exc,
                )

        return issues

    # =====================================================
    # STATUS
    # =====================================================

    def status(
        self,
    ) -> Dict[str, Any]:

        return {

            "name":
                REGISTRY_NAME,

            "version":
                REGISTRY_VERSION,

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
        *,
        test_instances: bool = False,
    ) -> Dict[str, Any]:

        issues = self.validate()

        if not self._scanners:

            issues.append(
                "No scanners registered."
            )

        if (
            self._scanners
            and not self.enabled_names
        ):

            issues.append(
                "No scanners enabled."
            )

        if self._errors:

            issues.append(
                "Scanner registry contains errors."
            )

        instance_issues: List[str] = []

        if test_instances:

            instance_issues = (
                self.validate_instances()
            )

            issues.extend(
                instance_issues
            )

        # Remove duplicate issue strings.
        issues = list(
            dict.fromkeys(
                issues
            )
        )

        return {

            "healthy":
                len(issues) == 0,

            "issues":
                issues,

            "instance_issues":
                instance_issues,

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

            "errors":
                self.errors,

        }

    # =====================================================
    # DIAGNOSTICS
    # =====================================================

    def diagnostics(
        self,
        *,
        test_instances: bool = False,
    ) -> Dict[str, Any]:

        return {

            "status":
                self.status(),

            "health":
                self.health_check(
                    test_instances=(
                        test_instances
                    )
                ),

            "validation":
                self.validate(),

            "configs": {

                self._scanners[
                    key
                ].__name__: dict(
                    config
                )

                for key, config
                in self._configs.items()

                if key in self._scanners
            },

        }

    # =====================================================
    # CONFIGURE REGISTRY
    # =====================================================

    def configure(
        self,
        *,
        debug: Optional[bool] = None,
    ) -> None:

        if debug is not None:

            self.debug = bool(
                debug
            )

    # =====================================================
    # INFO
    # =====================================================

    def info(
        self,
    ) -> Dict[str, Any]:

        return {

            "name":
                REGISTRY_NAME,

            "version":
                REGISTRY_VERSION,

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
    # LOGGING
    # =====================================================

    def log(
        self,
        *args: Any,
    ) -> None:

        if not self.debug:

            return

        print(
            "[ScannerRegistry]",
            *args,
        )

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
    ) -> Iterator[
        Type[BaseScanner]
    ]:

        return iter(
            self.scanner_classes
        )

    # =====================================================
    # GET ITEM
    # =====================================================

    def __getitem__(
        self,
        scanner_name: str,
    ) -> Type[BaseScanner]:

        scanner_class = (
            self.get_class(
                scanner_name
            )
        )

        if scanner_class is None:

            raise KeyError(
                f"Scanner not registered: "
                f"{scanner_name}"
            )

        return scanner_class

    # =====================================================
    # BOOL
    # =====================================================

    def __bool__(
        self,
    ) -> bool:

        return bool(
            self._scanners
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
            f"disabled={len(self.disabled_names)}, "
            f"errors={len(self._errors)})"
        )

    def __str__(
        self,
    ) -> str:

        return (
            f"{REGISTRY_NAME} | "
            f"{len(self._scanners)} registered | "
            f"{len(self.enabled_names)} enabled"
        )


# =========================================================
# GLOBAL REGISTRY
# =========================================================

scanner_registry = ScannerRegistry()


# =========================================================
# LOAD DEFAULT SCANNERS
# =========================================================

def load_default_scanners(
    *,
    force_reload: bool = False,
) -> ScannerRegistry:
    """
    Load scanner classes exported by core.scanners.

    Safe to call repeatedly.

    Parameters
    ----------
    force_reload:
        When True, existing registry entries are replaced.
    """

    try:

        from core.scanners import (
            get_scanner_classes,
        )

        scanner_classes = (
            get_scanner_classes()
        )

        if scanner_classes is None:

            scanner_classes = []

        scanner_registry.register_many(
            list(
                scanner_classes
            ),
            replace=force_reload,
        )

        scanner_registry._errors.pop(
            "default_loader",
            None,
        )

    except Exception as exc:

        scanner_registry._record_error(
            "default_loader",
            exc,
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

    return registry.create_enabled()


# =========================================================
# CREATE SCANNER
# =========================================================

def create_scanner(
    scanner_name: str,
    **kwargs: Any,
) -> Optional[BaseScanner]:
    """
    Convenience global scanner factory.
    """

    load_default_scanners()

    return scanner_registry.create(
        scanner_name,
        **kwargs,
    )


# =========================================================
# GET SCANNER CLASS
# =========================================================

def get_scanner_class(
    scanner_name: str,
) -> Optional[
    Type[BaseScanner]
]:

    load_default_scanners()

    return scanner_registry.get_class(
        scanner_name
    )


# =========================================================
# REGISTRY STATUS
# =========================================================

def get_registry_status(
) -> Dict[str, Any]:

    return scanner_registry.status()


# =========================================================
# REGISTRY HEALTH
# =========================================================

def get_registry_health(
    *,
    test_instances: bool = False,
) -> Dict[str, Any]:

    return scanner_registry.health_check(
        test_instances=test_instances
    )


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "REGISTRY_NAME",

    "REGISTRY_VERSION",

    "ScannerRegistry",

    "scanner_registry",

    "load_default_scanners",

    "create_default_scanners",

    "create_scanner",

    "get_scanner_class",

    "get_registry_status",

    "get_registry_health",
]


# =========================================================
# END OF FILE
# =========================================================