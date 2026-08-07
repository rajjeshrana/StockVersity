"""
=========================================================
StockVersity Scanner Pro
Scanner Scheduler
Version : 2.0
=========================================================

Scheduling and timing control for scanner execution.

Responsibilities
----------------
• Control scan intervals
• Determine when next scan is due
• Prevent overlapping scan cycles
• Pause / resume scheduling
• Track last and next execution
• Support scanner-specific intervals
• Provide scheduler diagnostics
• Thread-safe scheduler state
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


# =========================================================
# SCHEDULER STATUS
# =========================================================

class SchedulerStatus(str, Enum):

    IDLE = "IDLE"

    RUNNING = "RUNNING"

    PAUSED = "PAUSED"

    STOPPED = "STOPPED"


# =========================================================
# SCANNER SCHEDULE
# =========================================================

@dataclass(slots=True)
class ScannerSchedule:
    """
    Schedule configuration for one scanner.
    """

    scanner_name: str

    interval_seconds: int = 60

    enabled: bool = True

    run_immediately: bool = True

    last_run_at: Optional[datetime] = None

    next_run_at: Optional[datetime] = None

    run_count: int = 0

    skipped_count: int = 0

    created_at: datetime = field(
        default_factory=datetime.now
    )

    # =====================================================
    # INITIALIZE NEXT RUN
    # =====================================================

    def initialize(
        self,
        now: Optional[datetime] = None,
    ) -> None:

        now = (
            now
            or datetime.now()
        )

        if self.run_immediately:

            self.next_run_at = now

        else:

            self.next_run_at = (
                now
                + timedelta(
                    seconds=self.interval_seconds
                )
            )

    # =====================================================
    # DUE
    # =====================================================

    def is_due(
        self,
        now: Optional[datetime] = None,
    ) -> bool:

        if not self.enabled:

            return False

        now = (
            now
            or datetime.now()
        )

        if self.next_run_at is None:

            self.initialize(
                now
            )

        return (
            self.next_run_at is not None
            and now >= self.next_run_at
        )

    # =====================================================
    # MARK EXECUTED
    # =====================================================

    def mark_executed(
        self,
        now: Optional[datetime] = None,
    ) -> None:

        now = (
            now
            or datetime.now()
        )

        self.last_run_at = now

        self.run_count += 1

        self.next_run_at = (
            now
            + timedelta(
                seconds=self.interval_seconds
            )
        )

    # =====================================================
    # MARK SKIPPED
    # =====================================================

    def mark_skipped(
        self,
        now: Optional[datetime] = None,
    ) -> None:

        now = (
            now
            or datetime.now()
        )

        self.skipped_count += 1

        self.next_run_at = (
            now
            + timedelta(
                seconds=self.interval_seconds
            )
        )

    # =====================================================
    # SECONDS UNTIL NEXT RUN
    # =====================================================

    def seconds_until_next_run(
        self,
        now: Optional[datetime] = None,
    ) -> float:

        if self.next_run_at is None:

            return 0.0

        now = (
            now
            or datetime.now()
        )

        return max(
            0.0,
            (
                self.next_run_at
                - now
            ).total_seconds(),
        )

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "scanner_name":
                self.scanner_name,

            "interval_seconds":
                self.interval_seconds,

            "enabled":
                self.enabled,

            "run_immediately":
                self.run_immediately,

            "last_run_at":
                (
                    self.last_run_at.isoformat()
                    if self.last_run_at
                    else None
                ),

            "next_run_at":
                (
                    self.next_run_at.isoformat()
                    if self.next_run_at
                    else None
                ),

            "seconds_until_next_run":
                round(
                    self.seconds_until_next_run(),
                    2,
                ),

            "run_count":
                self.run_count,

            "skipped_count":
                self.skipped_count,

            "created_at":
                self.created_at.isoformat(),
        }


# =========================================================
# SCANNER SCHEDULER
# =========================================================

class ScannerScheduler:
    """
    Thread-safe scheduler for scanner execution.
    """

    def __init__(
        self,
        *,
        default_interval_seconds: int = 60,
    ) -> None:

        self.default_interval_seconds = max(
            1,
            int(
                default_interval_seconds
            ),
        )

        self._schedules: Dict[
            str,
            ScannerSchedule
        ] = {}

        self._status = (
            SchedulerStatus.IDLE
        )

        self._scan_in_progress = False

        self._started_at: Optional[
            datetime
        ] = None

        self._stopped_at: Optional[
            datetime
        ] = None

        self._lock = RLock()

    # =====================================================
    # NORMALIZE NAME
    # =====================================================

    @staticmethod
    def _normalize_name(
        scanner_name: str,
    ) -> str:

        return (
            str(scanner_name)
            .strip()
            .lower()
        )

    # =====================================================
    # ADD
    # =====================================================

    def add(
        self,
        scanner_name: str,
        *,
        interval_seconds: Optional[int] = None,
        enabled: bool = True,
        run_immediately: bool = True,
        replace: bool = False,
    ) -> ScannerSchedule:

        name = str(
            scanner_name
        ).strip()

        if not name:

            raise ValueError(
                "scanner_name cannot be empty."
            )

        key = self._normalize_name(
            name
        )

        interval = (
            self.default_interval_seconds
            if interval_seconds is None
            else max(
                1,
                int(interval_seconds),
            )
        )

        with self._lock:

            existing = (
                self._schedules.get(
                    key
                )
            )

            if (
                existing is not None
                and not replace
            ):

                return existing

            schedule = ScannerSchedule(

                scanner_name=name,

                interval_seconds=interval,

                enabled=bool(
                    enabled
                ),

                run_immediately=bool(
                    run_immediately
                ),
            )

            schedule.initialize()

            self._schedules[
                key
            ] = schedule

            return schedule

    # =====================================================
    # REMOVE
    # =====================================================

    def remove(
        self,
        scanner_name: str,
    ) -> bool:

        key = self._normalize_name(
            scanner_name
        )

        with self._lock:

            if key not in self._schedules:

                return False

            del self._schedules[
                key
            ]

            return True

    # =====================================================
    # GET
    # =====================================================

    def get(
        self,
        scanner_name: str,
    ) -> Optional[
        ScannerSchedule
    ]:

        key = self._normalize_name(
            scanner_name
        )

        with self._lock:

            return self._schedules.get(
                key
            )

    # =====================================================
    # HAS
    # =====================================================

    def has(
        self,
        scanner_name: str,
    ) -> bool:

        return (
            self.get(
                scanner_name
            )
            is not None
        )

    # =====================================================
    # ENABLE
    # =====================================================

    def enable(
        self,
        scanner_name: str,
    ) -> bool:

        with self._lock:

            schedule = self.get(
                scanner_name
            )

            if schedule is None:

                return False

            schedule.enabled = True

            if schedule.next_run_at is None:

                schedule.initialize()

            return True

    # =====================================================
    # DISABLE
    # =====================================================

    def disable(
        self,
        scanner_name: str,
    ) -> bool:

        with self._lock:

            schedule = self.get(
                scanner_name
            )

            if schedule is None:

                return False

            schedule.enabled = False

            return True

    # =====================================================
    # SET INTERVAL
    # =====================================================

    def set_interval(
        self,
        scanner_name: str,
        interval_seconds: int,
        *,
        reset_next_run: bool = True,
    ) -> bool:

        interval = max(
            1,
            int(interval_seconds),
        )

        with self._lock:

            schedule = self.get(
                scanner_name
            )

            if schedule is None:

                return False

            schedule.interval_seconds = (
                interval
            )

            if reset_next_run:

                schedule.next_run_at = (
                    datetime.now()
                    + timedelta(
                        seconds=interval
                    )
                )

            return True

    # =====================================================
    # START
    # =====================================================

    def start(
        self,
    ) -> None:

        with self._lock:

            self._status = (
                SchedulerStatus.RUNNING
            )

            self._started_at = (
                datetime.now()
            )

            self._stopped_at = None

    # =====================================================
    # PAUSE
    # =====================================================

    def pause(
        self,
    ) -> bool:

        with self._lock:

            if (
                self._status
                != SchedulerStatus.RUNNING
            ):

                return False

            self._status = (
                SchedulerStatus.PAUSED
            )

            return True

    # =====================================================
    # RESUME
    # =====================================================

    def resume(
        self,
    ) -> bool:

        with self._lock:

            if (
                self._status
                != SchedulerStatus.PAUSED
            ):

                return False

            self._status = (
                SchedulerStatus.RUNNING
            )

            return True

    # =====================================================
    # STOP
    # =====================================================

    def stop(
        self,
    ) -> None:

        with self._lock:

            self._status = (
                SchedulerStatus.STOPPED
            )

            self._scan_in_progress = False

            self._stopped_at = (
                datetime.now()
            )

    # =====================================================
    # DUE SCANNERS
    # =====================================================

    def due_scanners(
        self,
        now: Optional[datetime] = None,
    ) -> List[str]:
        """
        Return enabled scanners whose execution time
        has arrived.
        """

        now = (
            now
            or datetime.now()
        )

        with self._lock:

            if (
                self._status
                != SchedulerStatus.RUNNING
            ):

                return []

            if self._scan_in_progress:

                return []

            return [

                schedule.scanner_name

                for schedule
                in self._schedules.values()

                if schedule.is_due(
                    now
                )
            ]

    # =====================================================
    # NEXT DUE SCANNER
    # =====================================================

    def next_due(
        self,
    ) -> Optional[
        ScannerSchedule
    ]:

        with self._lock:

            schedules = [

                schedule

                for schedule
                in self._schedules.values()

                if (
                    schedule.enabled
                    and schedule.next_run_at
                    is not None
                )
            ]

            if not schedules:

                return None

            return min(

                schedules,

                key=lambda schedule:
                    schedule.next_run_at,
            )

    # =====================================================
    # BEGIN SCAN
    # =====================================================

    def begin_scan(
        self,
    ) -> bool:
        """
        Acquire scan slot.

        Prevents overlapping scanner cycles.
        """

        with self._lock:

            if (
                self._status
                != SchedulerStatus.RUNNING
            ):

                return False

            if self._scan_in_progress:

                return False

            self._scan_in_progress = True

            return True

    # =====================================================
    # END SCAN
    # =====================================================

    def end_scan(
        self,
    ) -> None:

        with self._lock:

            self._scan_in_progress = False

    # =====================================================
    # MARK EXECUTED
    # =====================================================

    def mark_executed(
        self,
        scanner_name: str,
        now: Optional[datetime] = None,
    ) -> bool:

        with self._lock:

            schedule = self.get(
                scanner_name
            )

            if schedule is None:

                return False

            schedule.mark_executed(
                now
            )

            return True

    # =====================================================
    # MARK SKIPPED
    # =====================================================

    def mark_skipped(
        self,
        scanner_name: str,
        now: Optional[datetime] = None,
    ) -> bool:

        with self._lock:

            schedule = self.get(
                scanner_name
            )

            if schedule is None:

                return False

            schedule.mark_skipped(
                now
            )

            return True

    # =====================================================
    # RESET SCHEDULE
    # =====================================================

    def reset_schedule(
        self,
        scanner_name: str,
        *,
        immediate: bool = False,
    ) -> bool:

        with self._lock:

            schedule = self.get(
                scanner_name
            )

            if schedule is None:

                return False

            now = datetime.now()

            if immediate:

                schedule.next_run_at = now

            else:

                schedule.next_run_at = (
                    now
                    + timedelta(
                        seconds=(
                            schedule.interval_seconds
                        )
                    )
                )

            return True

    # =====================================================
    # RESET ALL
    # =====================================================

    def reset_all(
        self,
        *,
        immediate: bool = False,
    ) -> None:

        with self._lock:

            now = datetime.now()

            for schedule in (
                self._schedules.values()
            ):

                if immediate:

                    schedule.next_run_at = (
                        now
                    )

                else:

                    schedule.next_run_at = (
                        now
                        + timedelta(
                            seconds=(
                                schedule.interval_seconds
                            )
                        )
                    )

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(
        self,
    ) -> None:

        with self._lock:

            self._schedules.clear()

            self._scan_in_progress = False

    # =====================================================
    # SCHEDULES
    # =====================================================

    @property
    def schedules(
        self,
    ) -> List[
        ScannerSchedule
    ]:

        with self._lock:

            return list(
                self._schedules.values()
            )

    # =====================================================
    # ENABLED NAMES
    # =====================================================

    @property
    def enabled_names(
        self,
    ) -> List[str]:

        with self._lock:

            return sorted(

                schedule.scanner_name

                for schedule
                in self._schedules.values()

                if schedule.enabled
            )

    # =====================================================
    # STATUS
    # =====================================================

    @property
    def status(
        self,
    ) -> SchedulerStatus:

        with self._lock:

            return self._status

    # =====================================================
    # RUNNING
    # =====================================================

    @property
    def running(
        self,
    ) -> bool:

        return (
            self.status
            == SchedulerStatus.RUNNING
        )

    # =====================================================
    # PAUSED
    # =====================================================

    @property
    def paused(
        self,
    ) -> bool:

        return (
            self.status
            == SchedulerStatus.PAUSED
        )

    # =====================================================
    # SCAN IN PROGRESS
    # =====================================================

    @property
    def scan_in_progress(
        self,
    ) -> bool:

        with self._lock:

            return self._scan_in_progress

    # =====================================================
    # REPORT
    # =====================================================

    def report(
        self,
    ) -> Dict[str, Any]:

        next_schedule = (
            self.next_due()
        )

        with self._lock:

            return {

                "status":
                    self._status.value,

                "running":
                    (
                        self._status
                        == SchedulerStatus.RUNNING
                    ),

                "paused":
                    (
                        self._status
                        == SchedulerStatus.PAUSED
                    ),

                "scan_in_progress":
                    self._scan_in_progress,

                "schedule_count":
                    len(
                        self._schedules
                    ),

                "enabled_count":
                    len(
                        self.enabled_names
                    ),

                "enabled_scanners":
                    self.enabled_names,

                "next_scanner":
                    (
                        next_schedule.scanner_name
                        if next_schedule
                        else None
                    ),

                "next_run_at":
                    (
                        next_schedule.next_run_at.isoformat()
                        if (
                            next_schedule
                            and next_schedule.next_run_at
                        )
                        else None
                    ),

                "started_at":
                    (
                        self._started_at.isoformat()
                        if self._started_at
                        else None
                    ),

                "stopped_at":
                    (
                        self._stopped_at.isoformat()
                        if self._stopped_at
                        else None
                    ),

                "schedules": [

                    schedule.to_dict()

                    for schedule
                    in self._schedules.values()
                ],
            }

    # =====================================================
    # LENGTH
    # =====================================================

    def __len__(
        self,
    ) -> int:

        with self._lock:

            return len(
                self._schedules
            )


# =========================================================
# GLOBAL SCHEDULER
# =========================================================

scanner_scheduler = ScannerScheduler(
    default_interval_seconds=60
)


# =========================================================
# CONVENIENCE FUNCTIONS
# =========================================================

def schedule_scanner(
    scanner_name: str,
    *,
    interval_seconds: int = 60,
    enabled: bool = True,
    run_immediately: bool = True,
) -> ScannerSchedule:

    return scanner_scheduler.add(

        scanner_name,

        interval_seconds=(
            interval_seconds
        ),

        enabled=enabled,

        run_immediately=(
            run_immediately
        ),
    )


def get_due_scanners(
) -> List[str]:

    return (
        scanner_scheduler
        .due_scanners()
    )


def start_scanner_scheduler(
) -> None:

    scanner_scheduler.start()


def stop_scanner_scheduler(
) -> None:

    scanner_scheduler.stop()


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "SchedulerStatus",

    "ScannerSchedule",

    "ScannerScheduler",

    "scanner_scheduler",

    "schedule_scanner",

    "get_due_scanners",

    "start_scanner_scheduler",

    "stop_scanner_scheduler",
]


# ==========================
# END OF FILE
# ==========================