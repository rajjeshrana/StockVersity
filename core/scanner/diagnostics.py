"""
=========================================================
StockVersity Scanner Pro
Scanner Diagnostics
Version : 2.0
=========================================================

Scanner subsystem diagnostics.

Responsibilities
----------------
• Inspect scanner registry
• Inspect runtime state
• Inspect sessions
• Inspect scheduler
• Inspect metrics
• Inspect event bus
• Inspect result store
• Inspect health monitor
• Run subsystem self-check
• Produce dashboard/debug reports
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from threading import RLock

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from core.scanner.events import (
    scanner_events,
)

from core.scanner.health import (
    scanner_health,
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
    scanner_scheduler,
)

from core.scanner.session import (
    scanner_sessions,
)

from core.scanner.state import (
    scanner_state,
)


# =========================================================
# DIAGNOSTIC RESULT
# =========================================================

@dataclass(slots=True)
class DiagnosticCheck:
    """
    Result of one diagnostic check.
    """

    name: str

    passed: bool

    message: str = ""

    details: Dict[str, Any] = field(
        default_factory=dict
    )

    checked_at: datetime = field(
        default_factory=datetime.now
    )

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "name":
                self.name,

            "passed":
                self.passed,

            "message":
                self.message,

            "details":
                dict(
                    self.details
                ),

            "checked_at":
                self.checked_at.isoformat(),
        }


# =========================================================
# DIAGNOSTIC REPORT
# =========================================================

@dataclass(slots=True)
class ScannerDiagnosticReport:
    """
    Complete scanner diagnostic report.
    """

    checks: List[
        DiagnosticCheck
    ] = field(
        default_factory=list
    )

    generated_at: datetime = field(
        default_factory=datetime.now
    )

    # =====================================================
    # PASSED
    # =====================================================

    @property
    def passed(
        self,
    ) -> bool:

        return all(

            check.passed

            for check
            in self.checks
        )

    # =====================================================
    # TOTAL
    # =====================================================

    @property
    def total_checks(
        self,
    ) -> int:

        return len(
            self.checks
        )

    # =====================================================
    # PASSED COUNT
    # =====================================================

    @property
    def passed_count(
        self,
    ) -> int:

        return sum(

            1

            for check
            in self.checks

            if check.passed
        )

    # =====================================================
    # FAILED COUNT
    # =====================================================

    @property
    def failed_count(
        self,
    ) -> int:

        return (
            self.total_checks
            - self.passed_count
        )

    # =====================================================
    # FAILURES
    # =====================================================

    @property
    def failures(
        self,
    ) -> List[
        DiagnosticCheck
    ]:

        return [

            check

            for check
            in self.checks

            if not check.passed
        ]

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "passed":
                self.passed,

            "total_checks":
                self.total_checks,

            "passed_count":
                self.passed_count,

            "failed_count":
                self.failed_count,

            "generated_at":
                self.generated_at.isoformat(),

            "checks": [

                check.to_dict()

                for check
                in self.checks
            ],
        }


# =========================================================
# SCANNER DIAGNOSTICS
# =========================================================

class ScannerDiagnostics:
    """
    Diagnostic service for scanner subsystem.
    """

    def __init__(
        self,
    ) -> None:

        self._lock = RLock()

        self._last_report: Optional[
            ScannerDiagnosticReport
        ] = None

    # =====================================================
    # SAFE CHECK
    # =====================================================

    @staticmethod
    def _safe_check(
        name: str,
        callback,
    ) -> DiagnosticCheck:
        """
        Execute one diagnostic check safely.
        """

        try:

            result = callback()

            if isinstance(
                result,
                DiagnosticCheck,
            ):

                return result

            if isinstance(
                result,
                bool,
            ):

                return DiagnosticCheck(

                    name=name,

                    passed=result,

                    message=(
                        "Check passed."
                        if result
                        else "Check failed."
                    ),
                )

            return DiagnosticCheck(

                name=name,

                passed=True,

                message="Check completed.",

                details={

                    "result":
                        result
                },
            )

        except Exception as exc:

            return DiagnosticCheck(

                name=name,

                passed=False,

                message=(
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
            )

    # =====================================================
    # REGISTRY CHECK
    # =====================================================

    @staticmethod
    def _check_registry(
    ) -> DiagnosticCheck:

        status = (
            scanner_registry.status()
        )

        registered = (
            status.get(
                "registered",
                0,
            )
        )

        errors = (
            status.get(
                "errors",
                {},
            )
        )

        passed = (
            registered > 0
            and not errors
        )

        if registered <= 0:

            message = (
                "No scanners registered."
            )

        elif errors:

            message = (
                "Scanner registry contains errors."
            )

        else:

            message = (
                f"{registered} scanner(s) registered."
            )

        return DiagnosticCheck(

            name="registry",

            passed=passed,

            message=message,

            details=status,
        )

    # =====================================================
    # STATE CHECK
    # =====================================================

    @staticmethod
    def _check_state(
    ) -> DiagnosticCheck:

        status = (
            scanner_state.status()
        )

        state = (
            status.get(
                "state",
                "UNKNOWN",
            )
        )

        passed = (
            state != "ERROR"
        )

        return DiagnosticCheck(

            name="runtime_state",

            passed=passed,

            message=(
                f"Runtime state: {state}"
            ),

            details=status,
        )

    # =====================================================
    # SESSION CHECK
    # =====================================================

    @staticmethod
    def _check_sessions(
    ) -> DiagnosticCheck:

        summary = (
            scanner_sessions.summary()
        )

        active = (
            scanner_sessions.active
        )

        active_error = False

        if active is not None:

            active_error = bool(
                active.errors
            )

        passed = (
            not active_error
        )

        return DiagnosticCheck(

            name="sessions",

            passed=passed,

            message=(
                "Session manager operational."
                if passed
                else "Active session contains errors."
            ),

            details={

                "summary":
                    summary,

                "active":
                    (
                        active.to_dict()
                        if active
                        else None
                    ),
            },
        )

    # =====================================================
    # SCHEDULER CHECK
    # =====================================================

    @staticmethod
    def _check_scheduler(
    ) -> DiagnosticCheck:

        report = (
            scanner_scheduler.report()
        )

        return DiagnosticCheck(

            name="scheduler",

            passed=True,

            message=(
                "Scheduler operational."
            ),

            details=report,
        )

    # =====================================================
    # METRICS CHECK
    # =====================================================

    @staticmethod
    def _check_metrics(
    ) -> DiagnosticCheck:

        report = (
            scanner_metrics.report()
        )

        return DiagnosticCheck(

            name="metrics",

            passed=True,

            message=(
                "Metrics collector operational."
            ),

            details=report,
        )

    # =====================================================
    # EVENTS CHECK
    # =====================================================

    @staticmethod
    def _check_events(
    ) -> DiagnosticCheck:

        status = (
            scanner_events.status()
        )

        errors = (
            scanner_events.errors
        )

        passed = (
            len(errors) == 0
        )

        return DiagnosticCheck(

            name="event_bus",

            passed=passed,

            message=(
                "Event bus operational."
                if passed
                else (
                    f"Event bus contains "
                    f"{len(errors)} error(s)."
                )
            ),

            details={

                "status":
                    status,

                "errors":
                    errors[
                        -10:
                    ],
            },
        )

    # =====================================================
    # RESULT STORE CHECK
    # =====================================================

    @staticmethod
    def _check_result_store(
    ) -> DiagnosticCheck:

        result_count = len(
            scanner_result_store
        )

        return DiagnosticCheck(

            name="result_store",

            passed=True,

            message=(
                "Result store operational."
            ),

            details={

                "result_count":
                    result_count
            },
        )

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    @staticmethod
    def _check_health(
    ) -> DiagnosticCheck:

        report = (
            scanner_health.check()
        )

        return DiagnosticCheck(

            name="health_monitor",

            passed=(
                report.healthy
            ),

            message=(
                f"Health level: "
                f"{report.level.value}"
            ),

            details=(
                report.to_dict()
            ),
        )

    # =====================================================
    # RESULT STORE API CHECK
    # =====================================================

    @staticmethod
    def _check_result_store_api(
    ) -> DiagnosticCheck:
        """
        Verify required result-store interface exists.
        """

        required = (

            "add_many",

            "clear",

            "all",
        )

        missing = [

            name

            for name
            in required

            if not callable(
                getattr(
                    scanner_result_store,
                    name,
                    None,
                )
            )
        ]

        return DiagnosticCheck(

            name="result_store_api",

            passed=(
                len(missing) == 0
            ),

            message=(
                "Result store API available."
                if not missing
                else (
                    "Missing result store methods: "
                    + ", ".join(
                        missing
                    )
                )
            ),

            details={

                "required":
                    list(
                        required
                    ),

                "missing":
                    missing,
            },
        )

    # =====================================================
    # REGISTRY API CHECK
    # =====================================================

    @staticmethod
    def _check_registry_api(
    ) -> DiagnosticCheck:
        """
        Verify registry methods required by the
        orchestrator/controller are available.
        """

        required = (

            "register",

            "register_many",

            "create",

            "create_all",

            "enable",

            "disable",

            "health_check",
        )

        missing = [

            name

            for name
            in required

            if not callable(
                getattr(
                    scanner_registry,
                    name,
                    None,
                )
            )
        ]

        return DiagnosticCheck(

            name="registry_api",

            passed=(
                len(missing) == 0
            ),

            message=(
                "Registry API available."
                if not missing
                else (
                    "Missing registry methods: "
                    + ", ".join(
                        missing
                    )
                )
            ),

            details={

                "required":
                    list(
                        required
                    ),

                "missing":
                    missing,
            },
        )

    # =====================================================
    # SESSION API CHECK
    # =====================================================

    @staticmethod
    def _check_session_api(
    ) -> DiagnosticCheck:

        required = (

            "create",

            "complete_active",

            "fail_active",

            "cancel_active",

            "history",

            "summary",
        )

        missing = [

            name

            for name
            in required

            if not callable(
                getattr(
                    scanner_sessions,
                    name,
                    None,
                )
            )
        ]

        return DiagnosticCheck(

            name="session_api",

            passed=(
                len(missing) == 0
            ),

            message=(
                "Session API available."
                if not missing
                else (
                    "Missing session methods: "
                    + ", ".join(
                        missing
                    )
                )
            ),

            details={

                "required":
                    list(
                        required
                    ),

                "missing":
                    missing,
            },
        )

    # =====================================================
    # RUN ALL
    # =====================================================

    def run(
        self,
    ) -> ScannerDiagnosticReport:
        """
        Run complete scanner subsystem diagnostics.
        """

        checks = [

            self._safe_check(
                "registry",
                self._check_registry,
            ),

            self._safe_check(
                "registry_api",
                self._check_registry_api,
            ),

            self._safe_check(
                "runtime_state",
                self._check_state,
            ),

            self._safe_check(
                "sessions",
                self._check_sessions,
            ),

            self._safe_check(
                "session_api",
                self._check_session_api,
            ),

            self._safe_check(
                "scheduler",
                self._check_scheduler,
            ),

            self._safe_check(
                "metrics",
                self._check_metrics,
            ),

            self._safe_check(
                "event_bus",
                self._check_events,
            ),

            self._safe_check(
                "result_store",
                self._check_result_store,
            ),

            self._safe_check(
                "result_store_api",
                self._check_result_store_api,
            ),

            self._safe_check(
                "health_monitor",
                self._check_health,
            ),
        ]

        report = (
            ScannerDiagnosticReport(

                checks=checks,

                generated_at=datetime.now(),
            )
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
        ScannerDiagnosticReport
    ]:

        with self._lock:

            return self._last_report

    # =====================================================
    # STATUS
    # =====================================================

    def status(
        self,
    ) -> Dict[str, Any]:

        report = (
            self.run()
        )

        return (
            report.to_dict()
        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> Dict[str, Any]:

        report = (
            self.run()
        )

        return {

            "passed":
                report.passed,

            "total":
                report.total_checks,

            "passed_count":
                report.passed_count,

            "failed_count":
                report.failed_count,

            "failures": [

                {

                    "name":
                        check.name,

                    "message":
                        check.message,
                }

                for check
                in report.failures
            ],
        }


# =========================================================
# GLOBAL DIAGNOSTICS
# =========================================================

scanner_diagnostics = (
    ScannerDiagnostics()
)


# =========================================================
# CONVENIENCE FUNCTIONS
# =========================================================

def run_scanner_diagnostics(
) -> ScannerDiagnosticReport:

    return (
        scanner_diagnostics.run()
    )


def get_scanner_diagnostics(
) -> Dict[str, Any]:

    return (
        scanner_diagnostics
        .status()
    )


def get_scanner_diagnostic_summary(
) -> Dict[str, Any]:

    return (
        scanner_diagnostics
        .summary()
    )


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "DiagnosticCheck",

    "ScannerDiagnosticReport",

    "ScannerDiagnostics",

    "scanner_diagnostics",

    "run_scanner_diagnostics",

    "get_scanner_diagnostics",

    "get_scanner_diagnostic_summary",
]


# ==========================
# END OF FILE
# ==========================