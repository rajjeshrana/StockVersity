"""
=========================================================
StockVersity Scanner Pro
Scanner Snapshot
Version : 2.0
=========================================================

Lightweight scanner subsystem snapshot.

Responsibilities
----------------
• Create dashboard-friendly scanner snapshots
• Expose runtime state
• Expose scanner counts
• Expose result count
• Expose scheduler information
• Expose last scanner error
• Avoid expensive full diagnostics for UI refreshes
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from core.scanner.manager import (
    scanner_manager,
)

from core.scanner.registry import (
    scanner_registry,
)

from core.scanner.result_store import (
    scanner_result_store,
)

from core.scanner.runtime import (
    scanner_runtime,
)

from core.scanner.scheduler import (
    scanner_scheduler,
)


# =========================================================
# SCANNER SNAPSHOT
# =========================================================

@dataclass(slots=True)
class ScannerSnapshot:
    """
    Lightweight immutable-style snapshot of scanner state.
    """

    created_at: datetime = field(
        default_factory=datetime.now
    )

    initialized: bool = False

    running: bool = False

    paused: bool = False

    scanning: bool = False

    registered_count: int = 0

    enabled_count: int = 0

    disabled_count: int = 0

    scheduled_count: int = 0

    due_count: int = 0

    result_count: int = 0

    enabled_scanners: List[str] = field(
        default_factory=list
    )

    disabled_scanners: List[str] = field(
        default_factory=list
    )

    due_scanners: List[str] = field(
        default_factory=list
    )

    last_error: str = ""

    last_cycle_at: Optional[
        datetime
    ] = None

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "created_at":
                self.created_at.isoformat(),

            "initialized":
                self.initialized,

            "running":
                self.running,

            "paused":
                self.paused,

            "scanning":
                self.scanning,

            "registered_count":
                self.registered_count,

            "enabled_count":
                self.enabled_count,

            "disabled_count":
                self.disabled_count,

            "scheduled_count":
                self.scheduled_count,

            "due_count":
                self.due_count,

            "result_count":
                self.result_count,

            "enabled_scanners":
                list(
                    self.enabled_scanners
                ),

            "disabled_scanners":
                list(
                    self.disabled_scanners
                ),

            "due_scanners":
                list(
                    self.due_scanners
                ),

            "last_error":
                self.last_error,

            "last_cycle_at":
                (
                    self.last_cycle_at.isoformat()
                    if self.last_cycle_at
                    else None
                ),
        }


# =========================================================
# SNAPSHOT SERVICE
# =========================================================

class ScannerSnapshotService:
    """
    Creates lightweight scanner snapshots.

    This service is suitable for frequent UI polling.
    """

    # =====================================================
    # DATETIME PARSER
    # =====================================================

    @staticmethod
    def _parse_datetime(
        value: Any,
    ) -> Optional[datetime]:

        if value is None:

            return None

        if isinstance(
            value,
            datetime,
        ):

            return value

        if isinstance(
            value,
            str,
        ):

            try:

                return datetime.fromisoformat(
                    value
                )

            except ValueError:

                return None

        return None

    # =====================================================
    # CREATE SNAPSHOT
    # =====================================================

    def create(
        self,
    ) -> ScannerSnapshot:
        """
        Create current scanner subsystem snapshot.
        """

        enabled = list(
            scanner_registry.enabled_names
        )

        disabled = list(
            scanner_registry.disabled_names
        )

        try:

            due = list(
                scanner_scheduler.due_scanners()
            )

        except Exception:

            due = []

        runtime_status = (
            scanner_runtime.status()
        )

        last_cycle_at = (
            self._parse_datetime(

                runtime_status.get(
                    "last_cycle_at"
                )
            )
        )

        last_error = (
            scanner_manager.last_error
            or runtime_status.get(
                "last_error",
                "",
            )
            or ""
        )

        return ScannerSnapshot(

            created_at=datetime.now(),

            initialized=(
                scanner_manager.initialized
            ),

            running=(
                scanner_runtime.running
            ),

            paused=(
                scanner_runtime.paused
            ),

            scanning=(
                scanner_manager.running
                and scanner_runtime.running
            ),

            registered_count=(
                len(
                    scanner_registry
                )
            ),

            enabled_count=(
                len(enabled)
            ),

            disabled_count=(
                len(disabled)
            ),

            scheduled_count=(
                len(
                    scanner_scheduler
                )
            ),

            due_count=(
                len(due)
            ),

            result_count=(
                len(
                    scanner_result_store
                )
            ),

            enabled_scanners=enabled,

            disabled_scanners=disabled,

            due_scanners=due,

            last_error=(
                str(last_error)
            ),

            last_cycle_at=(
                last_cycle_at
            ),
        )

    # =====================================================
    # DICTIONARY SNAPSHOT
    # =====================================================

    def get(
        self,
    ) -> Dict[str, Any]:
        """
        Return snapshot directly as dictionary.
        """

        return (
            self.create()
            .to_dict()
        )


# =========================================================
# GLOBAL SNAPSHOT SERVICE
# =========================================================

scanner_snapshot = (
    ScannerSnapshotService()
)


# =========================================================
# CONVENIENCE FUNCTIONS
# =========================================================

def create_scanner_snapshot(
) -> ScannerSnapshot:

    return (
        scanner_snapshot.create()
    )


def get_scanner_snapshot(
) -> Dict[str, Any]:

    return (
        scanner_snapshot.get()
    )


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "ScannerSnapshot",

    "ScannerSnapshotService",

    "scanner_snapshot",

    "create_scanner_snapshot",

    "get_scanner_snapshot",
]


# ==========================
# END OF FILE
# ==========================