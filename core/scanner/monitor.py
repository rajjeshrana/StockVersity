"""
=========================================================
StockVersity Scanner Pro
Scanner Monitor
Version : 2.0
=========================================================

Scanner runtime monitoring service.

Responsibilities
----------------
• Monitor lightweight scanner snapshots
• Detect scanner state changes
• Detect new scanner results
• Detect new runtime errors
• Support monitor callbacks
• Run monitoring in background
• Provide monitor statistics
• Support clean shutdown
=========================================================
"""

from __future__ import annotations

from datetime import datetime

from threading import Event
from threading import RLock
from threading import Thread
from threading import current_thread

from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional

from core.scanner.snapshot import (
    ScannerSnapshot,
    scanner_snapshot,
)


# =========================================================
# CALLBACK TYPE
# =========================================================

MonitorCallback = Callable[
    [
        ScannerSnapshot,
        Dict[str, Any],
    ],
    None,
]


# =========================================================
# SCANNER MONITOR
# =========================================================

class ScannerMonitor:
    """
    Lightweight scanner subsystem monitor.

    The monitor periodically creates ScannerSnapshot
    objects and reports meaningful changes to registered
    callbacks.

    It does NOT execute scanners.
    """

    def __init__(
        self,
        *,
        interval_seconds: float = 1.0,
    ) -> None:

        self.interval_seconds = max(
            0.10,
            float(interval_seconds),
        )

        self._lock = RLock()

        self._stop_event = Event()

        self._wake_event = Event()

        self._thread: Optional[
            Thread
        ] = None

        self._callbacks: List[
            MonitorCallback
        ] = []

        self._last_snapshot: Optional[
            ScannerSnapshot
        ] = None

        self._last_changes: Dict[
            str,
            Any
        ] = {}

        self._last_error = ""

        self._started_at: Optional[
            datetime
        ] = None

        self._stopped_at: Optional[
            datetime
        ] = None

        self._check_count = 0

        self._change_count = 0

        self._callback_error_count = 0

    # =====================================================
    # ADD CALLBACK
    # =====================================================

    def add_callback(
        self,
        callback: MonitorCallback,
    ) -> bool:

        if not callable(callback):

            raise TypeError(
                "Monitor callback must be callable."
            )

        with self._lock:

            if callback in self._callbacks:

                return False

            self._callbacks.append(
                callback
            )

        return True

    # =====================================================
    # REMOVE CALLBACK
    # =====================================================

    def remove_callback(
        self,
        callback: MonitorCallback,
    ) -> bool:

        with self._lock:

            if callback not in self._callbacks:

                return False

            self._callbacks.remove(
                callback
            )

        return True

    # =====================================================
    # CLEAR CALLBACKS
    # =====================================================

    def clear_callbacks(
        self,
    ) -> None:

        with self._lock:

            self._callbacks.clear()

    # =====================================================
    # DETECT CHANGES
    # =====================================================

    @staticmethod
    def _detect_changes(
        previous: Optional[
            ScannerSnapshot
        ],
        current: ScannerSnapshot,
    ) -> Dict[str, Any]:
        """
        Compare two scanner snapshots.

        created_at is intentionally ignored.
        """

        if previous is None:

            return {

                "initial_snapshot":
                    True
            }

        changes: Dict[
            str,
            Any
        ] = {}

        fields = (

            "initialized",

            "running",

            "paused",

            "scanning",

            "registered_count",

            "enabled_count",

            "disabled_count",

            "scheduled_count",

            "due_count",

            "result_count",

            "last_error",

            "last_cycle_at",
        )

        for field_name in fields:

            old_value = getattr(
                previous,
                field_name,
            )

            new_value = getattr(
                current,
                field_name,
            )

            if old_value == new_value:

                continue

            changes[
                field_name
            ] = {

                "old":
                    old_value,

                "new":
                    new_value,
            }

        # ---------------------------------------------
        # ENABLED SCANNERS
        # ---------------------------------------------

        old_enabled = set(
            previous.enabled_scanners
        )

        new_enabled = set(
            current.enabled_scanners
        )

        enabled_added = sorted(
            new_enabled
            - old_enabled
        )

        enabled_removed = sorted(
            old_enabled
            - new_enabled
        )

        if (
            enabled_added
            or enabled_removed
        ):

            changes[
                "enabled_scanners"
            ] = {

                "added":
                    enabled_added,

                "removed":
                    enabled_removed,
            }

        # ---------------------------------------------
        # DISABLED SCANNERS
        # ---------------------------------------------

        old_disabled = set(
            previous.disabled_scanners
        )

        new_disabled = set(
            current.disabled_scanners
        )

        disabled_added = sorted(
            new_disabled
            - old_disabled
        )

        disabled_removed = sorted(
            old_disabled
            - new_disabled
        )

        if (
            disabled_added
            or disabled_removed
        ):

            changes[
                "disabled_scanners"
            ] = {

                "added":
                    disabled_added,

                "removed":
                    disabled_removed,
            }

        # ---------------------------------------------
        # DUE SCANNERS
        # ---------------------------------------------

        old_due = set(
            previous.due_scanners
        )

        new_due = set(
            current.due_scanners
        )

        due_added = sorted(
            new_due
            - old_due
        )

        due_removed = sorted(
            old_due
            - new_due
        )

        if (
            due_added
            or due_removed
        ):

            changes[
                "due_scanners"
            ] = {

                "added":
                    due_added,

                "removed":
                    due_removed,
            }

        return changes

    # =====================================================
    # CHECK ONCE
    # =====================================================

    def check(
        self,
        *,
        notify: bool = True,
    ) -> ScannerSnapshot:
        """
        Create one scanner snapshot and detect changes.
        """

        try:

            current = (
                scanner_snapshot.create()
            )

            with self._lock:

                previous = (
                    self._last_snapshot
                )

            changes = (
                self._detect_changes(
                    previous,
                    current,
                )
            )

            with self._lock:

                self._check_count += 1

                self._last_snapshot = (
                    current
                )

                self._last_changes = dict(
                    changes
                )

                self._last_error = ""

                if changes:

                    self._change_count += 1

            if (
                notify
                and changes
            ):

                self._notify(
                    current,
                    changes,
                )

            return current

        except Exception as exc:

            with self._lock:

                self._last_error = (

                    f"{type(exc).__name__}: "
                    f"{exc}"
                )

            raise

    # =====================================================
    # NOTIFY CALLBACKS
    # =====================================================

    def _notify(
        self,
        snapshot: ScannerSnapshot,
        changes: Dict[str, Any],
    ) -> None:

        with self._lock:

            callbacks = list(
                self._callbacks
            )

        for callback in callbacks:

            try:

                callback(
                    snapshot,
                    dict(changes),
                )

            except Exception:

                with self._lock:

                    self._callback_error_count += 1

    # =====================================================
    # START
    # =====================================================

    def start(
        self,
    ) -> bool:
        """
        Start background monitoring.
        """

        with self._lock:

            if (
                self._thread is not None
                and self._thread.is_alive()
            ):

                return True

            self._stop_event.clear()

            self._wake_event.clear()

            self._last_error = ""

            self._started_at = (
                datetime.now()
            )

            self._stopped_at = None

            thread = Thread(

                target=self._run_loop,

                name=(
                    "StockVersityScannerMonitor"
                ),

                daemon=True,
            )

            self._thread = thread

        thread.start()

        return True

    # =====================================================
    # STOP
    # =====================================================

    def stop(
        self,
        *,
        wait: bool = False,
        timeout: Optional[float] = 5.0,
    ) -> bool:
        """
        Stop background monitoring.
        """

        with self._lock:

            thread = (
                self._thread
            )

        if (
            thread is None
            or not thread.is_alive()
        ):

            return True

        self._stop_event.set()

        self._wake_event.set()

        if (
            wait
            and thread is not current_thread()
        ):

            thread.join(
                timeout=timeout
            )

        return True

    # =====================================================
    # WAKE
    # =====================================================

    def wake(
        self,
    ) -> None:

        self._wake_event.set()

    # =====================================================
    # RUN LOOP
    # =====================================================

    def _run_loop(
        self,
    ) -> None:

        try:

            while not self._stop_event.is_set():

                try:

                    self.check(
                        notify=True
                    )

                except Exception:

                    # Error already recorded by check().
                    pass

                self._wake_event.wait(
                    timeout=(
                        self.interval_seconds
                    )
                )

                self._wake_event.clear()

        finally:

            with self._lock:

                self._stopped_at = (
                    datetime.now()
                )

                self._thread = None

    # =====================================================
    # RUNNING
    # =====================================================

    @property
    def running(
        self,
    ) -> bool:

        with self._lock:

            return (

                self._thread is not None

                and self._thread.is_alive()
            )

    # =====================================================
    # LAST SNAPSHOT
    # =====================================================

    @property
    def last_snapshot(
        self,
    ) -> Optional[
        ScannerSnapshot
    ]:

        with self._lock:

            return self._last_snapshot

    # =====================================================
    # LAST CHANGES
    # =====================================================

    @property
    def last_changes(
        self,
    ) -> Dict[str, Any]:

        with self._lock:

            return dict(
                self._last_changes
            )

    # =====================================================
    # LAST ERROR
    # =====================================================

    @property
    def last_error(
        self,
    ) -> str:

        with self._lock:

            return self._last_error

    # =====================================================
    # STATUS
    # =====================================================

    def status(
        self,
    ) -> Dict[str, Any]:

        with self._lock:

            thread_running = (

                self._thread is not None

                and self._thread.is_alive()
            )

            last_snapshot = (
                self._last_snapshot
            )

            return {

                "running":
                    thread_running,

                "interval_seconds":
                    self.interval_seconds,

                "callback_count":
                    len(
                        self._callbacks
                    ),

                "check_count":
                    self._check_count,

                "change_count":
                    self._change_count,

                "callback_error_count":
                    self._callback_error_count,

                "last_error":
                    self._last_error,

                "last_changes":
                    dict(
                        self._last_changes
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

                "last_snapshot":
                    (
                        last_snapshot.to_dict()
                        if last_snapshot
                        else None
                    ),
            }

    # =====================================================
    # RESET
    # =====================================================

    def reset(
        self,
    ) -> bool:
        """
        Reset monitor statistics.

        Monitor must be stopped first.
        """

        if self.running:

            return False

        with self._lock:

            self._last_snapshot = None

            self._last_changes = {}

            self._last_error = ""

            self._started_at = None

            self._stopped_at = None

            self._check_count = 0

            self._change_count = 0

            self._callback_error_count = 0

        return True


# =========================================================
# GLOBAL MONITOR
# =========================================================

scanner_monitor = ScannerMonitor(
    interval_seconds=1.0
)


# =========================================================
# CONVENIENCE FUNCTIONS
# =========================================================

def start_scanner_monitor(
) -> bool:

    return scanner_monitor.start()


def stop_scanner_monitor(
    *,
    wait: bool = False,
) -> bool:

    return scanner_monitor.stop(
        wait=wait
    )


def check_scanner_monitor(
) -> ScannerSnapshot:

    return scanner_monitor.check()


def get_scanner_monitor_status(
) -> Dict[str, Any]:

    return scanner_monitor.status()


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "MonitorCallback",

    "ScannerMonitor",

    "scanner_monitor",

    "start_scanner_monitor",

    "stop_scanner_monitor",

    "check_scanner_monitor",

    "get_scanner_monitor_status",
]


# ==========================
# END OF FILE
# ==========================