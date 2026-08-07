"""
=========================================================
StockVersity Scanner Pro
Scanner Health Monitor
Version : 2.0
=========================================================

Central health monitoring for scanner subsystem.

Responsibilities
----------------
• Check scanner registry health
• Check runtime state
• Check scheduler health
• Check event bus errors
• Check scanner performance
• Check result store
• Check active sessions
• Detect stale / inconsistent states
• Provide dashboard-ready health report
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime
from datetime import timedelta

from enum import Enum

from threading import RLock

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from core.scanner.events import (
    scanner_events,
)

from core.scanner.metrics import (
    scanner_metrics,
)

from core.scanner.registry import (
    scanner_registry,
)

from core.scanner.result_store import (
    scanner_result_store,
)

from core.scanner.scheduler import (
    SchedulerStatus,
    scanner_scheduler,
)

from core.scanner.session import (
    ScannerSessionStatus,
    scanner_sessions,
)

from core.scanner.state import (
    ScannerEngineState,
    scanner_state,
)


# =========================================================
# HEALTH LEVEL
# =========================================================

class ScannerHealthLevel(str, Enum):

    HEALTHY = "HEALTHY"

    WARNING = "WARNING"

    ERROR = "ERROR"

    CRITICAL = "CRITICAL"


# =========================================================
# HEALTH ISSUE
# =========================================================

@dataclass(slots=True)
class ScannerHealthIssue:
    """
    One scanner subsystem health issue.
    """

    component: str

    message: str

    level: ScannerHealthLevel = (
        ScannerHealthLevel.WARNING
    )

    created_at: datetime = field(
        default_factory=datetime.now
    )

    details: Dict[str, Any] = field(
        default_factory=dict
    )

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "component":
                self.component,

            "message":
                self.message,

            "level":
                self.level.value,

            "created_at":
                self.created_at.isoformat(),

            "details":
                dict(
                    self.details
                ),
        }


# =========================================================
# HEALTH REPORT
# =========================================================

@dataclass(slots=True)
class ScannerHealthReport:
    """
    Complete scanner subsystem health report.
    """

    level: ScannerHealthLevel = (
        ScannerHealthLevel.HEALTHY
    )

    issues: List[
        ScannerHealthIssue
    ] = field(
        default_factory=list
    )

    checked_at: datetime = field(
        default_factory=datetime.now
    )

    components: Dict[
        str,
        Any
    ] = field(
        default_factory=dict
    )

    # =====================================================
    # HEALTHY
    # =====================================================

    @property
    def healthy(
        self,
    ) -> bool:

        return (
            self.level
            == ScannerHealthLevel.HEALTHY
        )

    # =====================================================
    # ISSUE COUNT
    # =====================================================

    @property
    def issue_count(
        self,
    ) -> int:

        return len(
            self.issues
        )

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "healthy":
                self.healthy,

            "level":
                self.level.value,

            "issue_count":
                self.issue_count,

            "checked_at":
                self.checked_at.isoformat(),

            "issues": [

                issue.to_dict()

                for issue
                in self.issues
            ],

            "components":
                dict(
                    self.components
                ),
        }


# =========================================================
# HEALTH MONITOR
# =========================================================

class ScannerHealthMonitor:
    """
    Performs health checks across scanner subsystem.
    """

    def __init__(
        self,
        *,
        stale_running_minutes: int = 30,
    ) -> None:

        self.stale_running_minutes = max(
            1,
            int(
                stale_running_minutes
            ),
        )

        self._lock = RLock()

        self._last_report: Optional[
            ScannerHealthReport
        ] = None

    # =====================================================
    # ADD ISSUE
    # =====================================================

    @staticmethod
    def _add_issue(
        issues: List[
            ScannerHealthIssue
        ],
        *,
        component: str,
        message: str,
        level: ScannerHealthLevel,
        details: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        issues.append(

            ScannerHealthIssue(

                component=component,

                message=message,

                level=level,

                details=(
                    dict(details)
                    if details
                    else {}
                ),
            )
        )

    # =====================================================
    # REGISTRY CHECK
    # =====================================================

    def _check_registry(
        self,
        issues: List[
            ScannerHealthIssue
        ],
    ) -> Dict[str, Any]:

        status = (
            scanner_registry.status()
        )

        if status[
            "registered"
        ] <= 0:

            self._add_issue(

                issues,

                component="registry",

                message=(
                    "No scanners are registered."
                ),

                level=(
                    ScannerHealthLevel.ERROR
                ),
            )

        elif status[
            "enabled"
        ] <= 0:

            self._add_issue(

                issues,

                component="registry",

                message=(
                    "All registered scanners "
                    "are disabled."
                ),

                level=(
                    ScannerHealthLevel.WARNING
                ),
            )

        registry_errors = (
            status.get(
                "errors",
                {},
            )
        )

        if registry_errors:

            self._add_issue(

                issues,

                component="registry",

                message=(
                    "Scanner registry contains "
                    f"{len(registry_errors)} "
                    "error(s)."
                ),

                level=(
                    ScannerHealthLevel.ERROR
                ),

                details={
                    "errors":
                        registry_errors
                },
            )

        return status

    # =====================================================
    # RUNTIME CHECK
    # =====================================================

    def _check_runtime(
        self,
        issues: List[
            ScannerHealthIssue
        ],
    ) -> Dict[str, Any]:

        snapshot = (
            scanner_state.snapshot()
        )

        status = (
            snapshot.to_dict()
        )

        if (
            snapshot.state
            == ScannerEngineState.ERROR
        ):

            self._add_issue(

                issues,

                component="runtime",

                message=(
                    snapshot.last_error
                    or "Scanner runtime is in ERROR state."
                ),

                level=(
                    ScannerHealthLevel.ERROR
                ),
            )

        # ---------------------------------------------
        # STALE RUNNING DETECTION
        # ---------------------------------------------

        if (
            snapshot.running
            and snapshot.started_at
            is not None
        ):

            stale_limit = (

                datetime.now()

                - timedelta(
                    minutes=(
                        self.stale_running_minutes
                    )
                )
            )

            if (
                snapshot.started_at
                < stale_limit
            ):

                self._add_issue(

                    issues,

                    component="runtime",

                    message=(
                        "Scanner has remained in a "
                        "running state longer than "
                        f"{self.stale_running_minutes} "
                        "minutes."
                    ),

                    level=(
                        ScannerHealthLevel.WARNING
                    ),

                    details={

                        "started_at":
                            (
                                snapshot
                                .started_at
                                .isoformat()
                            )
                    },
                )

        return status

    # =====================================================
    # SESSION CHECK
    # =====================================================

    def _check_session(
        self,
        issues: List[
            ScannerHealthIssue
        ],
    ) -> Dict[str, Any]:

        active = (
            scanner_sessions.active
        )

        last = (
            scanner_sessions.last
        )

        if active is not None:

            if (
                active.status
                == ScannerSessionStatus.FAILED
            ):

                self._add_issue(

                    issues,

                    component="session",

                    message=(
                        "Active scanner session "
                        "is marked FAILED."
                    ),

                    level=(
                        ScannerHealthLevel.ERROR
                    ),
                )

            if active.errors:

                self._add_issue(

                    issues,

                    component="session",

                    message=(
                        "Active scanner session "
                        f"contains {len(active.errors)} "
                        "error(s)."
                    ),

                    level=(
                        ScannerHealthLevel.WARNING
                    ),

                    details={

                        "errors":
                            list(
                                active.errors
                            )
                    },
                )

        return {

            "active":
                (
                    active.to_dict()
                    if active
                    else None
                ),

            "last":
                (
                    last.to_dict()
                    if last
                    else None
                ),

            "summary":
                scanner_sessions.summary(),
        }

    # =====================================================
    # SCHEDULER CHECK
    # =====================================================

    def _check_scheduler(
        self,
        issues: List[
            ScannerHealthIssue
        ],
    ) -> Dict[str, Any]:

        report = (
            scanner_scheduler.report()
        )

        if (
            scanner_scheduler.status
            == SchedulerStatus.RUNNING
            and len(
                scanner_scheduler
            ) == 0
        ):

            self._add_issue(

                issues,

                component="scheduler",

                message=(
                    "Scheduler is running but "
                    "contains no scanner schedules."
                ),

                level=(
                    ScannerHealthLevel.WARNING
                ),
            )

        if (
            scanner_scheduler.scan_in_progress
            and not scanner_state.snapshot().running
        ):

            self._add_issue(

                issues,

                component="scheduler",

                message=(
                    "Scheduler reports a scan in "
                    "progress while runtime is not "
                    "running."
                ),

                level=(
                    ScannerHealthLevel.WARNING
                ),
            )

        return report

    # =====================================================
    # EVENT BUS CHECK
    # =====================================================

    def _check_events(
        self,
        issues: List[
            ScannerHealthIssue
        ],
    ) -> Dict[str, Any]:

        status = (
            scanner_events.status()
        )

        errors = (
            scanner_events.errors
        )

        if errors:

            self._add_issue(

                issues,

                component="events",

                message=(
                    "Scanner event bus contains "
                    f"{len(errors)} listener "
                    "error(s)."
                ),

                level=(
                    ScannerHealthLevel.WARNING
                ),

                details={

                    "recent_errors":
                        errors[
                            -10:
                        ]
                },
            )

        return status

    # =====================================================
    # METRICS CHECK
    # =====================================================

    def _check_metrics(
        self,
        issues: List[
            ScannerHealthIssue
        ],
    ) -> Dict[str, Any]:

        metrics = (
            scanner_metrics.report()
        )

        scan_cycles = (
            metrics.get(
                "scan_cycles",
                0,
            )
        )

        failed_cycles = (
            metrics.get(
                "failed_cycles",
                0,
            )
        )

        if (
            scan_cycles >= 5
            and failed_cycles
            == scan_cycles
        ):

            self._add_issue(

                issues,

                component="metrics",

                message=(
                    "All recorded scanner cycles "
                    "have failed."
                ),

                level=(
                    ScannerHealthLevel.ERROR
                ),
            )

        market_requests = (
            metrics.get(
                "market_data_requests",
                0,
            )
        )

        market_errors = (
            metrics.get(
                "market_data_errors",
                0,
            )
        )

        if (
            market_requests >= 10
            and market_errors
            / market_requests
            >= 0.50
        ):

            self._add_issue(

                issues,

                component="market_data",

                message=(
                    "Market-data error rate is "
                    "50% or higher."
                ),

                level=(
                    ScannerHealthLevel.ERROR
                ),

                details={

                    "requests":
                        market_requests,

                    "errors":
                        market_errors,
                },
            )

        return metrics

    # =====================================================
    # RESULT STORE CHECK
    # =====================================================

    def _check_results(
        self,
        issues: List[
            ScannerHealthIssue
        ],
    ) -> Dict[str, Any]:

        try:

            result_count = len(
                scanner_result_store
            )

            return {

                "result_count":
                    result_count
            }

        except Exception as exc:

            self._add_issue(

                issues,

                component="result_store",

                message=(
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),

                level=(
                    ScannerHealthLevel.ERROR
                ),
            )

            return {

                "result_count":
                    0,

                "error":
                    (
                        f"{type(exc).__name__}: "
                        f"{exc}"
                    ),
            }

    # =====================================================
    # DETERMINE LEVEL
    # =====================================================

    @staticmethod
    def _determine_level(
        issues: List[
            ScannerHealthIssue
        ],
    ) -> ScannerHealthLevel:

        if not issues:

            return (
                ScannerHealthLevel.HEALTHY
            )

        levels = {

            issue.level

            for issue
            in issues
        }

        if (
            ScannerHealthLevel.CRITICAL
            in levels
        ):

            return (
                ScannerHealthLevel.CRITICAL
            )

        if (
            ScannerHealthLevel.ERROR
            in levels
        ):

            return (
                ScannerHealthLevel.ERROR
            )

        return (
            ScannerHealthLevel.WARNING
        )

    # =====================================================
    # CHECK
    # =====================================================

    def check(
        self,
    ) -> ScannerHealthReport:
        """
        Run complete scanner health check.
        """

        issues: List[
            ScannerHealthIssue
        ] = []

        components: Dict[
            str,
            Any
        ] = {}

        # ---------------------------------------------
        # REGISTRY
        # ---------------------------------------------

        try:

            components[
                "registry"
            ] = self._check_registry(
                issues
            )

        except Exception as exc:

            self._add_issue(

                issues,

                component="registry",

                message=(
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),

                level=(
                    ScannerHealthLevel.CRITICAL
                ),
            )

        # ---------------------------------------------
        # RUNTIME
        # ---------------------------------------------

        try:

            components[
                "runtime"
            ] = self._check_runtime(
                issues
            )

        except Exception as exc:

            self._add_issue(

                issues,

                component="runtime",

                message=(
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),

                level=(
                    ScannerHealthLevel.ERROR
                ),
            )

        # ---------------------------------------------
        # SESSION
        # ---------------------------------------------

        try:

            components[
                "session"
            ] = self._check_session(
                issues
            )

        except Exception as exc:

            self._add_issue(

                issues,

                component="session",

                message=(
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),

                level=(
                    ScannerHealthLevel.ERROR
                ),
            )

        # ---------------------------------------------
        # SCHEDULER
        # ---------------------------------------------

        try:

            components[
                "scheduler"
            ] = self._check_scheduler(
                issues
            )

        except Exception as exc:

            self._add_issue(

                issues,

                component="scheduler",

                message=(
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),

                level=(
                    ScannerHealthLevel.ERROR
                ),
            )

        # ---------------------------------------------
        # EVENTS
        # ---------------------------------------------

        try:

            components[
                "events"
            ] = self._check_events(
                issues
            )

        except Exception as exc:

            self._add_issue(

                issues,

                component="events",

                message=(
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),

                level=(
                    ScannerHealthLevel.WARNING
                ),
            )

        # ---------------------------------------------
        # METRICS
        # ---------------------------------------------

        try:

            components[
                "metrics"
            ] = self._check_metrics(
                issues
            )

        except Exception as exc:

            self._add_issue(

                issues,

                component="metrics",

                message=(
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),

                level=(
                    ScannerHealthLevel.WARNING
                ),
            )

        # ---------------------------------------------
        # RESULT STORE
        # ---------------------------------------------

        try:

            components[
                "results"
            ] = self._check_results(
                issues
            )

        except Exception as exc:

            self._add_issue(

                issues,

                component="result_store",

                message=(
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),

                level=(
                    ScannerHealthLevel.ERROR
                ),
            )

        # ---------------------------------------------
        # REPORT
        # ---------------------------------------------

        report = ScannerHealthReport(

            level=(
                self._determine_level(
                    issues
                )
            ),

            issues=issues,

            checked_at=datetime.now(),

            components=components,
        )

        with self._lock:

            self._last_report = (
                report
            )

        return report

    # =====================================================
    # LAST REPORT
    # =====================================================

    @property
    def last_report(
        self,
    ) -> Optional[
        ScannerHealthReport
    ]:

        with self._lock:

            return (
                self._last_report
            )

    # =====================================================
    # HEALTHY
    # =====================================================

    @property
    def healthy(
        self,
    ) -> bool:

        report = (
            self.last_report
        )

        if report is None:

            report = self.check()

        return (
            report.healthy
        )

    # =====================================================
    # STATUS
    # =====================================================

    def status(
        self,
    ) -> Dict[str, Any]:

        report = (
            self.check()
        )

        return (
            report.to_dict()
        )


# =========================================================
# GLOBAL HEALTH MONITOR
# =========================================================

scanner_health = ScannerHealthMonitor(
    stale_running_minutes=30
)


# =========================================================
# CONVENIENCE FUNCTIONS
# =========================================================

def check_scanner_health(
) -> ScannerHealthReport:

    return scanner_health.check()


def get_scanner_health_status(
) -> Dict[str, Any]:

    return (
        scanner_health
        .status()
    )


def scanner_is_healthy(
) -> bool:

    return (
        scanner_health
        .check()
        .healthy
    )


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "ScannerHealthLevel",

    "ScannerHealthIssue",

    "ScannerHealthReport",

    "ScannerHealthMonitor",

    "scanner_health",

    "check_scanner_health",

    "get_scanner_health_status",

    "scanner_is_healthy",
]


# ==========================
# END OF FILE
# ==========================