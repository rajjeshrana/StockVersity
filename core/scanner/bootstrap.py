"""Public compatibility bootstrap interface for the scanner subsystem."""

from __future__ import annotations

from typing import Any, Dict, Optional

from core.scanner.scanner_bootstrap import (
    DEFAULT_CONFIG,
    ScannerBootstrap as _ScannerBootstrap,
    create_scanner_system as _create_scanner_system,
    get_scanner_system,
)


class ScannerBootstrap(_ScannerBootstrap):
    """Scanner bootstrap with convenient configuration arguments."""

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        *,
        parallel: Optional[bool] = None,
        debug: Optional[bool] = None,
    ) -> None:
        resolved_config: Dict[str, Any] = {}

        if config:
            resolved_config.update(config)

        if parallel is not None:
            resolved_config["parallel"] = bool(parallel)

        if debug is not None:
            resolved_config["debug"] = bool(debug)

        super().__init__(config=resolved_config)

    def initialize(self):
        """Initialize the scanner system and return its engine."""
        super().initialize()

        if self.manager is None:
            raise RuntimeError("ScannerManager was not created.")

        if not self.manager.loaded:
            self.manager.load_scanners()

        if self.engine is None:
            raise RuntimeError("ScannerEngine was not created.")

        return self.engine

    @property
    def registry(self):
        """Expose the manager's scanner registry."""
        if self.manager is None:
            raise RuntimeError(
                "Scanner system has not been initialized."
            )

        return self.manager.registry


    def validate(self) -> list[str]:
        """Return validation errors; an empty list means valid."""
        errors: list[str] = []

        if not self.initialized:
            errors.append("Scanner system is not initialized.")

        if self.engine is None:
            errors.append("ScannerEngine is unavailable.")
        elif not self.engine.scanners:
            errors.append("ScannerEngine has no registered scanners.")

        if self.manager is None:
            errors.append("ScannerManager is unavailable.")

        if self.last_error:
            errors.append(self.last_error)

        return errors
    def status(self) -> Dict[str, Any]:
        """Return bootstrap status including registry and engine counts."""
        result = super().status()

        if self.manager is None:
            result["registry_registered"] = 0
            result["registry_enabled"] = 0
        else:
            registry_count = len(
                self.manager.registry.enabled_names
            )
            result["registry_registered"] = registry_count
            result["registry_enabled"] = registry_count

        if self.engine is None:
            result["engine_registered"] = 0
            result["engine_enabled"] = 0
        else:
            result["engine_registered"] = len(
                self.engine.scanners
            )
            result["engine_enabled"] = len(
                self.engine.enabled_scanners
            )
        result["created_instances"] = result["engine_registered"]    
        return result

def create_scanner_system(
    config: Optional[Dict[str, Any]] = None,
    *,
    parallel: Optional[bool] = None,
    debug: Optional[bool] = None,
) -> ScannerBootstrap:
    """Create a configured ScannerBootstrap instance."""
    return ScannerBootstrap(
        config=config,
        parallel=parallel,
        debug=debug,
    )


def create_original_scanner_system(*args: Any, **kwargs: Any):
    """Access the original scanner_bootstrap factory."""
    return _create_scanner_system(*args, **kwargs)


__all__ = [
    "ScannerBootstrap",
    "create_scanner_system",
    "create_original_scanner_system",
    "get_scanner_system",
    "DEFAULT_CONFIG",
]
