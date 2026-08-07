from __future__ import annotations

import logging
from typing import Any, Dict, Type, TypeVar

T = TypeVar("T")


# ==========================================================
# SERVICE CONTAINER
# ==========================================================

class ServiceContainer:
    """
    Central dependency injection container.

    Responsible for:
    - Registering services
    - Resolving services
    - Singleton lifecycle
    - Service discovery
    """

    def __init__(self):

        self.logger = logging.getLogger(
            self.__class__.__name__
        )

        self._services: Dict[str, Any] = {}

        self.logger.info(
            "ServiceContainer initialized."
        )

    # ==========================================================
    # REGISTER
    # ==========================================================

    def register(
        self,
        name: str,
        service: Any,
    ) -> None:
        """
        Register a singleton service.
        """

        self._services[name] = service

        self.logger.info(
            "Registered service: %s",
            name,
        )

    # ==========================================================
    # REGISTER TYPE
    # ==========================================================

    def register_type(
        self,
        service_type: Type[T],
        instance: T,
    ) -> None:
        """
        Register a service using its class name.
        """

        self.register(
            service_type.__name__,
            instance,
        )

    # ==========================================================
    # RESOLVE
    # ==========================================================

    def resolve(
        self,
        name: str,
    ) -> Any:
        """
        Resolve a registered service.
        """

        if name not in self._services:

            raise KeyError(
                f"Service '{name}' is not registered."
            )

        return self._services[name]

    # ==========================================================
    # RESOLVE TYPE
    # ==========================================================

    def resolve_type(
        self,
        service_type: Type[T],
    ) -> T:
        """
        Resolve by class type.
        """

        return self.resolve(
            service_type.__name__
        )

    # ==========================================================
    # EXISTS
    # ==========================================================

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Check whether a service is registered.
        """

        return name in self._services
    from collections.abc import Callable


# ==========================================================
# REGISTER FACTORY
# ==========================================================

    def register_factory(
        self,
        name: str,
        factory: Callable[[], Any],
    ) -> None:
        """
        Register a lazy factory.
        """

        if not hasattr(self, "_factories"):
            self._factories: Dict[str, Callable[[], Any]] = {}

        self._factories[name] = factory

        self.logger.info(
            "Factory registered: %s",
            name,
        )

# ==========================================================
# REGISTER SINGLETON
# ==========================================================

    def register_singleton(
        self,
        service_type: Type[T],
        factory: Callable[[], T],
    ) -> None:
        """
        Register a singleton using a factory.
        """

        self.register_factory(
            service_type.__name__,
            factory,
        )

# ==========================================================
# RESOLVE (UPDATED)
# ==========================================================

    def resolve(
        self,
        name: str,
    ) -> Any:
        """
        Resolve a service.
        Supports lazy singleton creation.
        """

        if name in self._services:

            return self._services[name]

        factories = getattr(
            self,
            "_factories",
            {},
        )

        if name in factories:

            instance = factories[name]()

            self._services[name] = instance

            self.logger.info(
                "Lazy service created: %s",
                name,
            )

            return instance

        raise KeyError(
            f"Service '{name}' is not registered."
        )

# ==========================================================
# REMOVE SERVICE
# ==========================================================

    def unregister(
        self,
        name: str,
    ) -> bool:
        """
        Remove a registered service.
        """

        removed = False

        if name in self._services:

            del self._services[name]

            removed = True

        factories = getattr(
            self,
            "_factories",
            {},
        )

        if name in factories:

            del factories[name]

            removed = True

        if removed:

            self.logger.info(
                "Service removed: %s",
                name,
            )

        return removed

# ==========================================================
# CLEAR
# ==========================================================

    def clear(self) -> None:
        """
        Remove every registered service.
        """

        self._services.clear()

        if hasattr(self, "_factories"):

            self._factories.clear()

        self.logger.info(
            "ServiceContainer cleared."
        )

# ==========================================================
# SERVICE NAMES
# ==========================================================

    def service_names(self) -> list[str]:
        """
        Return all registered service names.
        """

        names = set(self._services.keys())

        factories = getattr(
            self,
            "_factories",
            {},
        )

        names.update(factories.keys())

        return sorted(names)

# ==========================================================
# COUNT
# ==========================================================

    def service_count(self) -> int:
        """
        Total registered services.
        """

        return len(
            self.service_names()
        )

# ==========================================================
# STATISTICS
# ==========================================================

    def statistics(self) -> Dict[str, Any]:
        """
        Container statistics.
        """

        return {

            "services":

                len(self._services),

            "factories":

                len(
                    getattr(
                        self,
                        "_factories",
                        {},
                    )
                ),

            "registered":

                self.service_names(),

        }
        # ==========================================================
    # REGISTER TRANSIENT
    # ==========================================================

    def register_transient(
        self,
        service_type: Type[T],
        factory: Callable[[], T],
    ) -> None:
        """
        Register a transient service.

        A new instance is created every time it is resolved.
        """

        if not hasattr(self, "_transients"):
            self._transients: Dict[
                str,
                Callable[[], Any]
            ] = {}

        self._transients[
            service_type.__name__
        ] = factory

        self.logger.info(
            "Transient service registered: %s",
            service_type.__name__,
        )

    # ==========================================================
    # RESOLVE TRANSIENT
    # ==========================================================

    def resolve_transient(
        self,
        service_type: Type[T],
    ) -> T:
        """
        Resolve a transient service.
        """

        if not hasattr(self, "_transients"):

            raise KeyError(
                "No transient services registered."
            )

        name = service_type.__name__

        if name not in self._transients:

            raise KeyError(
                f"Transient '{name}' not registered."
            )

        return self._transients[name]()

    # ==========================================================
    # VALIDATE
    # ==========================================================

    def validate(self) -> bool:
        """
        Validate registered services.
        """

        try:

            for name in self.service_names():

                self.resolve(name)

            return True

        except Exception as ex:

            self.logger.exception(ex)

            return False

    # ==========================================================
    # MISSING SERVICES
    # ==========================================================

    def missing_services(
        self,
        required: list[str],
    ) -> list[str]:
        """
        Return missing required services.
        """

        return [

            service

            for service in required

            if not self.contains(service)

        ]

    # ==========================================================
    # IS VALID
    # ==========================================================

    def is_valid(self) -> bool:
        """
        Check whether container is valid.
        """

        return self.validate()

    # ==========================================================
    # HEALTH CHECK
    # ==========================================================

    def health_check(self) -> Dict[str, Any]:
        """
        Container health report.
        """

        return {

            "healthy":

                self.validate(),

            "registered":

                self.service_count(),

            "singleton_instances":

                len(self._services),

            "factory_services":

                len(

                    getattr(

                        self,

                        "_factories",

                        {},

                    )

                ),

            "transient_services":

                len(

                    getattr(

                        self,

                        "_transients",

                        {},

                    )

                ),

        }

    # ==========================================================
    # REGISTERED TYPES
    # ==========================================================

    def registered_types(self) -> list[str]:
        """
        Return registered service types.
        """

        return self.service_names()

    # ==========================================================
    # HAS TYPE
    # ==========================================================

    def has_type(
        self,
        service_type: Type[Any],
    ) -> bool:
        """
        Check whether a type is registered.
        """

        return self.contains(
            service_type.__name__
        )
        # ==========================================================
    # CREATE CHILD CONTAINER
    # ==========================================================

    def create_scope(self) -> "ServiceContainer":
        """
        Create a child service container.
        """

        child = ServiceContainer()

        child._parent = self

        self.logger.info(
            "Child service container created."
        )

        return child

    # ==========================================================
    # PARENT CONTAINER
    # ==========================================================

    def parent(self) -> "ServiceContainer | None":
        """
        Return parent container.
        """

        return getattr(
            self,
            "_parent",
            None,
        )

    # ==========================================================
    # RESOLVE (UPDATED FOR PARENT)
    # ==========================================================

    def resolve(
        self,
        name: str,
    ) -> Any:
        """
        Resolve a service with parent fallback.
        """

        if name in self._services:

            return self._services[name]

        factories = getattr(
            self,
            "_factories",
            {},
        )

        if name in factories:

            instance = factories[name]()

            self._services[name] = instance

            return instance

        parent = self.parent()

        if parent is not None:

            return parent.resolve(name)

        raise KeyError(
            f"Service '{name}' is not registered."
        )

    # ==========================================================
    # DISPOSE SERVICE
    # ==========================================================

    def dispose_service(
        self,
        name: str,
    ) -> bool:
        """
        Dispose a service if it supports cleanup().
        """

        if name not in self._services:

            return False

        service = self._services[name]

        try:

            if hasattr(service, "cleanup"):

                service.cleanup()

            elif hasattr(service, "shutdown"):

                service.shutdown()

            elif hasattr(service, "close"):

                service.close()

        except Exception as ex:

            self.logger.exception(ex)

        finally:

            del self._services[name]

        return True

    # ==========================================================
    # DISPOSE ALL
    # ==========================================================

    def dispose_all(self) -> None:
        """
        Dispose every instantiated service.
        """

        for name in list(self._services.keys()):

            self.dispose_service(name)

        self.logger.info(
            "All services disposed."
        )

    # ==========================================================
    # RESET
    # ==========================================================

    def reset(self) -> None:
        """
        Reset the container.
        """

        self.dispose_all()

        if hasattr(self, "_factories"):

            self._factories.clear()

        if hasattr(self, "_transients"):

            self._transients.clear()

        self.logger.info(
            "ServiceContainer reset."
        )

    # ==========================================================
    # IS EMPTY
    # ==========================================================

    def is_empty(self) -> bool:
        """
        Check whether the container has any registrations.
        """

        return self.service_count() == 0

    # ==========================================================
    # CONTEXT MANAGER
    # ==========================================================

    def __enter__(self):
        """
        Context manager entry.
        """

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        """
        Context manager exit.
        """

        self.dispose_all()

        return False
        # ==========================================================
    # SERVICE INFO
    # ==========================================================

    def service_info(
        self,
        name: str,
    ) -> Dict[str, Any]:
        """
        Return information about a registered service.
        """

        if not self.contains(name):

            raise KeyError(
                f"Service '{name}' is not registered."
            )

        instance = self.resolve(name)

        return {

            "name": name,

            "type": type(instance).__name__,

            "module": type(instance).__module__,

            "singleton": name in self._services,

            "factory":
                name in getattr(
                    self,
                    "_factories",
                    {},
                ),

            "transient":
                name in getattr(
                    self,
                    "_transients",
                    {},
                ),

        }

    # ==========================================================
    # LIST SERVICES
    # ==========================================================

    def list_services(self) -> list[Dict[str, Any]]:
        """
        Return metadata for all registered services.
        """

        services = []

        for name in self.service_names():

            try:

                services.append(
                    self.service_info(name)
                )

            except Exception as ex:

                self.logger.exception(ex)

        return services

    # ==========================================================
    # CONTAINER REPORT
    # ==========================================================

    def report(self) -> Dict[str, Any]:
        """
        Generate a complete container report.
        """

        return {

            "statistics":
                self.statistics(),

            "health":
                self.health_check(),

            "services":
                self.list_services(),

        }

    # ==========================================================
    # VERIFY REGISTRATION
    # ==========================================================

    def verify_registration(
        self,
        required_services: list[str],
    ) -> bool:
        """
        Verify all required services exist.
        """

        missing = self.missing_services(
            required_services
        )

        if missing:

            self.logger.error(
                "Missing services: %s",
                ", ".join(missing),
            )

            return False

        return True

    # ==========================================================
    # VERIFY RESOLUTION
    # ==========================================================

    def verify_resolution(self) -> bool:
        """
        Verify every registered service
        can be resolved.
        """

        try:

            for name in self.service_names():

                self.resolve(name)

            return True

        except Exception as ex:

            self.logger.exception(ex)

            return False

    # ==========================================================
    # PRINT REPORT
    # ==========================================================

    def print_report(self) -> None:
        """
        Print container diagnostics.
        """

        report = self.report()

        self.logger.info(
            "=" * 60
        )

        self.logger.info(
            "Service Container Report"
        )

        self.logger.info(
            "=" * 60
        )

        self.logger.info(
            "Registered Services: %s",
            report["statistics"]["registered"],
        )

        self.logger.info(
            "Health: %s",
            report["health"]["healthy"],
        )

        for service in report["services"]:

            self.logger.info(
                "%s -> %s",
                service["name"],
                service["type"],
            )

    # ==========================================================
    # STRING REPRESENTATION
    # ==========================================================

    def __repr__(self):

        return (

            f"<ServiceContainer "

            f"services={self.service_count()}>"

        )

    def __str__(self):

        return (

            f"ServiceContainer("

            f"{self.service_count()} services)"

        )
    # ==========================================================
# INITIALIZE RUNTIME STATE
# ==========================================================

    def _initialize_runtime(self) -> None:
        """
        Initialize runtime tracking structures.
        """

        if not hasattr(self, "_resolution_stack"):
            self._resolution_stack: list[str] = []

        if not hasattr(self, "_resolution_count"):
            self._resolution_count: Dict[str, int] = {}

        if not hasattr(self, "_resolution_time"):
            self._resolution_time: Dict[str, float] = {}

# ==========================================================
# RESOLUTION START
# ==========================================================

    def _begin_resolution(
        self,
        name: str,
    ) -> None:
        """
        Begin service resolution.
        """

        self._initialize_runtime()

        if name in self._resolution_stack:

            chain = " -> ".join(
                self._resolution_stack + [name]
            )

            raise RuntimeError(
                "Circular dependency detected: "
                f"{chain}"
            )

        self._resolution_stack.append(name)

# ==========================================================
# RESOLUTION END
# ==========================================================

    def _end_resolution(
        self,
        name: str,
        elapsed: float,
    ) -> None:
        """
        Finish service resolution.
        """

        if self._resolution_stack:

            self._resolution_stack.pop()

        self._resolution_count[name] = (

            self._resolution_count.get(
                name,
                0,
            )
            + 1

        )

        self._resolution_time[name] = (

            self._resolution_time.get(
                name,
                0.0,
            )
            + elapsed

        )

# ==========================================================
# RESOLUTION COUNT
# ==========================================================

    def resolution_count(
        self,
        name: str,
    ) -> int:
        """
        Number of resolutions.
        """

        self._initialize_runtime()

        return self._resolution_count.get(
            name,
            0,
        )

# ==========================================================
# RESOLUTION TIME
# ==========================================================

    def resolution_time(
        self,
        name: str,
    ) -> float:
        """
        Total resolution time.
        """

        self._initialize_runtime()

        return self._resolution_time.get(
            name,
            0.0,
        )

# ==========================================================
# CURRENT STACK
# ==========================================================

    def resolution_stack(
        self,
    ) -> list[str]:
        """
        Current dependency stack.
        """

        self._initialize_runtime()

        return list(
            self._resolution_stack
        )

# ==========================================================
# RESET METRICS
# ==========================================================

    def reset_metrics(self) -> None:
        """
        Reset runtime metrics.
        """

        self._initialize_runtime()

        self._resolution_stack.clear()

        self._resolution_count.clear()

        self._resolution_time.clear()

# ==========================================================
# PERFORMANCE REPORT
# ==========================================================

    def performance_report(
        self,
    ) -> Dict[str, Any]:
        """
        Runtime performance report.
        """

        self._initialize_runtime()

        report = {}

        for name in self.service_names():

            report[name] = {

                "resolved":

                    self.resolution_count(
                        name
                    ),

                "time":

                    self.resolution_time(
                        name
                    ),

            }

        return report
    from collections.abc import Callable
from datetime import datetime


# ==========================================================
# EVENT REGISTRATION
# ==========================================================

    def register_event_handler(
        self,
        event: str,
        handler: Callable[..., None],
    ) -> None:
        """
        Register a container event handler.
        """

        if not hasattr(self, "_event_handlers"):

            self._event_handlers: Dict[
                str,
                list[Callable[..., None]]
            ] = {}

        self._event_handlers.setdefault(
            event,
            [],
        ).append(handler)

# ==========================================================
# EMIT EVENT
# ==========================================================

    def _emit_event(
        self,
        event: str,
        **kwargs,
    ) -> None:
        """
        Emit a container event.
        """

        handlers = getattr(
            self,
            "_event_handlers",
            {},
        ).get(event, [])

        for handler in handlers:

            try:

                handler(**kwargs)

            except Exception as ex:

                self.logger.exception(ex)

# ==========================================================
# CONTAINER SNAPSHOT
# ==========================================================

    def snapshot(self) -> Dict[str, Any]:
        """
        Create a runtime snapshot.
        """

        return {

            "timestamp":

                datetime.now(),

            "statistics":

                self.statistics(),

            "health":

                self.health_check(),

            "performance":

                self.performance_report(),

            "services":

                self.service_names(),

        }

# ==========================================================
# EXPORT DEPENDENCY GRAPH
# ==========================================================

    def dependency_graph(self) -> Dict[str, list[str]]:
        """
        Export a simple dependency graph.

        This version reports registered services.
        Dependency discovery can be extended later.
        """

        graph = {}

        for service in self.service_names():

            graph[service] = []

        return graph

# ==========================================================
# DEBUG SUMMARY
# ==========================================================

    def debug_summary(self) -> Dict[str, Any]:
        """
        Complete debugging information.
        """

        return {

            "container":

                self.snapshot(),

            "graph":

                self.dependency_graph(),

        }

# ==========================================================
# BUILD INFORMATION
# ==========================================================

    @staticmethod
    def build_info() -> Dict[str, str]:
        """
        Build information.
        """

        return {

            "container":

                "ServiceContainer",

            "version":

                "1.0.0",

            "application":

                "StockVersity Scanner Pro",

            "framework":

                "PySide6",

        }

# ==========================================================
# CONTAINER VERSION
# ==========================================================

    @classmethod
    def version(cls) -> str:
        """
        Return container version.
        """

        return "1.0.0"

# ==========================================================
# PRINT SNAPSHOT
# ==========================================================

    def print_snapshot(self) -> None:
        """
        Log a snapshot of the container.
        """

        snapshot = self.snapshot()

        self.logger.info("=" * 60)

        self.logger.info(
            "Container Snapshot"
        )

        self.logger.info("=" * 60)

        self.logger.info(
            "Registered Services: %s",
            snapshot["statistics"]["registered"],
        )

        self.logger.info(
            "Health: %s",
            snapshot["health"]["healthy"],
        )

        self.logger.info(
            "Timestamp: %s",
            snapshot["timestamp"],
        )
        # ==========================================================
# GLOBAL CONTAINER
# ==========================================================

_default_container: ServiceContainer | None = None


def get_container() -> ServiceContainer:
    """
    Return the global ServiceContainer instance.
    """

    global _default_container

    if _default_container is None:

        _default_container = ServiceContainer()

    return _default_container


# ==========================================================
# SET DEFAULT CONTAINER
# ==========================================================

def set_container(
    container: ServiceContainer,
) -> None:
    """
    Set the global ServiceContainer.
    """

    global _default_container

    _default_container = container


# ==========================================================
# RESET DEFAULT CONTAINER
# ==========================================================

def reset_container() -> None:
    """
    Dispose and recreate the global container.
    """

    global _default_container

    if _default_container is not None:

        _default_container.dispose_all()

    _default_container = ServiceContainer()


# ==========================================================
# REGISTER DEFAULT SERVICES
# ==========================================================

def register_default_services(
    container: ServiceContainer,
) -> None:
    """
    Register application-wide services.

    Actual service registrations should be added
    by the application bootstrap.
    """

    container.logger.info(
        "Registering default services..."
    )

    # Example:
    #
    # container.register_factory(
    #     "ScannerService",
    #     lambda: ScannerService(...)
    # )
    #
    # container.register_factory(
    #     "MarketService",
    #     lambda: MarketService(...)
    # )

    container.logger.info(
        "Default service registration complete."
    )


# ==========================================================
# CONTAINER FACTORY
# ==========================================================

def create_service_container() -> ServiceContainer:
    """
    Create and initialize a ServiceContainer.
    """

    container = ServiceContainer()

    register_default_services(
        container
    )

    return container


# ==========================================================
# MODULE VERSION
# ==========================================================

__version__ = "1.0.0"


# ==========================================================
# END OF FILE
# ==========================================================