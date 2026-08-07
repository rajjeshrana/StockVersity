"""
=========================================================
StockVersity Scanner Pro
Scanner Session
Version : 2.0
=========================================================

Scanner execution session management.

Responsibilities
----------------
• Create scanner run sessions
• Track session lifecycle
• Track processed symbols
• Track generated opportunities
• Track errors and warnings
• Calculate session duration
• Maintain recent session history
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from enum import Enum

from threading import RLock

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from uuid import uuid4


# =========================================================
# SESSION STATUS
# =========================================================

class ScannerSessionStatus(
    str,
    Enum,
):

    CREATED = "CREATED"

    RUNNING = "RUNNING"

    COMPLETED = "COMPLETED"

    FAILED = "FAILED"

    CANCELLED = "CANCELLED"


# =========================================================
# SCANNER SESSION
# =========================================================

@dataclass(slots=True)
class ScannerSession:
    """
    Represents one complete scanner execution cycle.
    """

    session_id: str = field(
        default_factory=lambda: uuid4().hex
    )

    name: str = "ScannerSession"

    status: ScannerSessionStatus = (
        ScannerSessionStatus.CREATED
    )

    created_at: datetime = field(
        default_factory=datetime.now
    )

    started_at: Optional[datetime] = None

    completed_at: Optional[datetime] = None

    symbols_total: int = 0

    symbols_processed: int = 0

    scanners_total: int = 0

    scanners_completed: int = 0

    signals_generated: int = 0

    signals_accepted: int = 0

    signals_rejected: int = 0

    errors: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    # =====================================================
    # START
    # =====================================================

    def start(
        self,
    ) -> None:

        if (
            self.status
            == ScannerSessionStatus.RUNNING
        ):

            return

        self.status = (
            ScannerSessionStatus.RUNNING
        )

        self.started_at = (
            datetime.now()
        )

        self.completed_at = None

    # =====================================================
    # COMPLETE
    # =====================================================

    def complete(
        self,
    ) -> None:

        self.status = (
            ScannerSessionStatus.COMPLETED
        )

        self.completed_at = (
            datetime.now()
        )

    # =====================================================
    # FAIL
    # =====================================================

    def fail(
        self,
        error: Optional[
            BaseException | str
        ] = None,
    ) -> None:

        self.status = (
            ScannerSessionStatus.FAILED
        )

        self.completed_at = (
            datetime.now()
        )

        if error is not None:

            self.add_error(
                error
            )

    # =====================================================
    # CANCEL
    # =====================================================

    def cancel(
        self,
        reason: Optional[str] = None,
    ) -> None:

        self.status = (
            ScannerSessionStatus.CANCELLED
        )

        self.completed_at = (
            datetime.now()
        )

        if reason:

            self.add_warning(
                reason
            )

    # =====================================================
    # ADD ERROR
    # =====================================================

    def add_error(
        self,
        error: BaseException | str,
    ) -> None:

        if isinstance(
            error,
            BaseException,
        ):

            message = (
                f"{type(error).__name__}: "
                f"{error}"
            )

        else:

            message = str(
                error
            )

        self.errors.append(
            message
        )

    # =====================================================
    # ADD WARNING
    # =====================================================

    def add_warning(
        self,
        warning: Any,
    ) -> None:

        self.warnings.append(
            str(warning)
        )

    # =====================================================
    # SYMBOL PROCESSED
    # =====================================================

    def mark_symbol_processed(
        self,
        count: int = 1,
    ) -> None:

        self.symbols_processed += max(
            0,
            int(count),
        )

    # =====================================================
    # SCANNER COMPLETED
    # =====================================================

    def mark_scanner_completed(
        self,
        count: int = 1,
    ) -> None:

        self.scanners_completed += max(
            0,
            int(count),
        )

    # =====================================================
    # SIGNAL GENERATED
    # =====================================================

    def mark_signal_generated(
        self,
        count: int = 1,
    ) -> None:

        self.signals_generated += max(
            0,
            int(count),
        )

    # =====================================================
    # SIGNAL ACCEPTED
    # =====================================================

    def mark_signal_accepted(
        self,
        count: int = 1,
    ) -> None:

        value = max(
            0,
            int(count),
        )

        self.signals_accepted += (
            value
        )

    # =====================================================
    # SIGNAL REJECTED
    # =====================================================

    def mark_signal_rejected(
        self,
        count: int = 1,
    ) -> None:

        value = max(
            0,
            int(count),
        )

        self.signals_rejected += (
            value
        )

    # =====================================================
    # DURATION
    # =====================================================

    @property
    def duration_seconds(
        self,
    ) -> float:

        if self.started_at is None:

            return 0.0

        end_time = (
            self.completed_at
            if self.completed_at
            is not None
            else datetime.now()
        )

        return max(
            0.0,
            (
                end_time
                - self.started_at
            ).total_seconds(),
        )

    # =====================================================
    # PROGRESS
    # =====================================================

    @property
    def progress_percent(
        self,
    ) -> float:

        if self.symbols_total <= 0:

            return 0.0

        return round(
            min(
                100.0,
                self.symbols_processed
                / self.symbols_total
                * 100.0,
            ),
            2,
        )

    # =====================================================
    # SCANNER PROGRESS
    # =====================================================

    @property
    def scanner_progress_percent(
        self,
    ) -> float:

        if self.scanners_total <= 0:

            return 0.0

        return round(
            min(
                100.0,
                self.scanners_completed
                / self.scanners_total
                * 100.0,
            ),
            2,
        )

    # =====================================================
    # SUCCESS
    # =====================================================

    @property
    def successful(
        self,
    ) -> bool:

        return (
            self.status
            == ScannerSessionStatus.COMPLETED
            and not self.errors
        )

    # =====================================================
    # RUNNING
    # =====================================================

    @property
    def running(
        self,
    ) -> bool:

        return (
            self.status
            == ScannerSessionStatus.RUNNING
        )

    # =====================================================
    # FINISHED
    # =====================================================

    @property
    def finished(
        self,
    ) -> bool:

        return self.status in (

            ScannerSessionStatus.COMPLETED,

            ScannerSessionStatus.FAILED,

            ScannerSessionStatus.CANCELLED,
        )

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "session_id":
                self.session_id,

            "name":
                self.name,

            "status":
                self.status.value,

            "successful":
                self.successful,

            "running":
                self.running,

            "finished":
                self.finished,

            "created_at":
                self.created_at.isoformat(),

            "started_at":
                (
                    self.started_at.isoformat()
                    if self.started_at
                    else None
                ),

            "completed_at":
                (
                    self.completed_at.isoformat()
                    if self.completed_at
                    else None
                ),

            "duration_seconds":
                round(
                    self.duration_seconds,
                    4,
                ),

            "symbols_total":
                self.symbols_total,

            "symbols_processed":
                self.symbols_processed,

            "progress_percent":
                self.progress_percent,

            "scanners_total":
                self.scanners_total,

            "scanners_completed":
                self.scanners_completed,

            "scanner_progress_percent":
                self.scanner_progress_percent,

            "signals_generated":
                self.signals_generated,

            "signals_accepted":
                self.signals_accepted,

            "signals_rejected":
                self.signals_rejected,

            "error_count":
                len(
                    self.errors
                ),

            "warning_count":
                len(
                    self.warnings
                ),

            "errors":
                list(
                    self.errors
                ),

            "warnings":
                list(
                    self.warnings
                ),

            "metadata":
                dict(
                    self.metadata
                ),
        }


# =========================================================
# SESSION MANAGER
# =========================================================

class ScannerSessionManager:
    """
    Manages scanner execution sessions.
    """

    def __init__(
        self,
        *,
        history_limit: int = 100,
    ) -> None:

        self.history_limit = max(
            1,
            int(history_limit),
        )

        self._sessions: Dict[
            str,
            ScannerSession
        ] = {}

        self._history: List[
            str
        ] = []

        self._active_session_id: Optional[
            str
        ] = None

        self._lock = RLock()

    # =====================================================
    # CREATE
    # =====================================================

    def create(
        self,
        *,
        name: str = "ScannerSession",
        symbols_total: int = 0,
        scanners_total: int = 0,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
        auto_start: bool = True,
    ) -> ScannerSession:

        session = ScannerSession(

            name=str(
                name
            ).strip()
            or "ScannerSession",

            symbols_total=max(
                0,
                int(symbols_total),
            ),

            scanners_total=max(
                0,
                int(scanners_total),
            ),

            metadata=(
                dict(metadata)
                if metadata
                else {}
            ),
        )

        if auto_start:

            session.start()

        with self._lock:

            self._sessions[
                session.session_id
            ] = session

            self._history.append(
                session.session_id
            )

            self._active_session_id = (
                session.session_id
            )

            self._trim_history()

        return session

    # =====================================================
    # ACTIVE
    # =====================================================

    @property
    def active(
        self,
    ) -> Optional[
        ScannerSession
    ]:

        with self._lock:

            if (
                self._active_session_id
                is None
            ):

                return None

            return self._sessions.get(
                self._active_session_id
            )

    # =====================================================
    # GET
    # =====================================================

    def get(
        self,
        session_id: str,
    ) -> Optional[
        ScannerSession
    ]:

        with self._lock:

            return self._sessions.get(
                str(session_id)
            )

    # =====================================================
    # COMPLETE ACTIVE
    # =====================================================

    def complete_active(
        self,
    ) -> Optional[
        ScannerSession
    ]:

        with self._lock:

            session = self.active

            if session is None:

                return None

            session.complete()

            self._active_session_id = None

            return session

    # =====================================================
    # FAIL ACTIVE
    # =====================================================

    def fail_active(
        self,
        error: Optional[
            BaseException | str
        ] = None,
    ) -> Optional[
        ScannerSession
    ]:

        with self._lock:

            session = self.active

            if session is None:

                return None

            session.fail(
                error
            )

            self._active_session_id = None

            return session

    # =====================================================
    # CANCEL ACTIVE
    # =====================================================

    def cancel_active(
        self,
        reason: Optional[str] = None,
    ) -> Optional[
        ScannerSession
    ]:

        with self._lock:

            session = self.active

            if session is None:

                return None

            session.cancel(
                reason
            )

            self._active_session_id = None

            return session

    # =====================================================
    # HISTORY
    # =====================================================

    def history(
        self,
        *,
        limit: Optional[int] = None,
    ) -> List[
        ScannerSession
    ]:

        with self._lock:

            ids = list(
                self._history
            )

            if limit is not None:

                limit_value = max(
                    0,
                    int(limit),
                )

                ids = ids[
                    -limit_value:
                ]

            sessions = [

                self._sessions[
                    session_id
                ]

                for session_id in ids

                if session_id
                in self._sessions
            ]

            return list(
                reversed(
                    sessions
                )
            )

    # =====================================================
    # LAST SESSION
    # =====================================================

    @property
    def last(
        self,
    ) -> Optional[
        ScannerSession
    ]:

        history = self.history(
            limit=1
        )

        if not history:

            return None

        return history[
            0
        ]

    # =====================================================
    # TRIM HISTORY
    # =====================================================

    def _trim_history(
        self,
    ) -> None:

        while (
            len(self._history)
            > self.history_limit
        ):

            oldest_id = (
                self._history.pop(
                    0
                )
            )

            if (
                oldest_id
                == self._active_session_id
            ):

                self._history.append(
                    oldest_id
                )

                break

            self._sessions.pop(
                oldest_id,
                None,
            )

    # =====================================================
    # REMOVE
    # =====================================================

    def remove(
        self,
        session_id: str,
    ) -> bool:

        session_id = str(
            session_id
        )

        with self._lock:

            if (
                session_id
                not in self._sessions
            ):

                return False

            if (
                session_id
                == self._active_session_id
            ):

                return False

            del self._sessions[
                session_id
            ]

            try:

                self._history.remove(
                    session_id
                )

            except ValueError:

                pass

            return True

    # =====================================================
    # CLEAR HISTORY
    # =====================================================

    def clear(
        self,
        *,
        keep_active: bool = True,
    ) -> None:

        with self._lock:

            if (
                keep_active
                and self._active_session_id
                is not None
            ):

                active_id = (
                    self._active_session_id
                )

                active = (
                    self._sessions.get(
                        active_id
                    )
                )

                self._sessions.clear()

                self._history.clear()

                if active is not None:

                    self._sessions[
                        active_id
                    ] = active

                    self._history.append(
                        active_id
                    )

            else:

                self._sessions.clear()

                self._history.clear()

                self._active_session_id = None

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> Dict[str, Any]:

        sessions = self.history()

        completed = sum(

            1

            for session in sessions

            if (
                session.status
                == ScannerSessionStatus.COMPLETED
            )
        )

        failed = sum(

            1

            for session in sessions

            if (
                session.status
                == ScannerSessionStatus.FAILED
            )
        )

        cancelled = sum(

            1

            for session in sessions

            if (
                session.status
                == ScannerSessionStatus.CANCELLED
            )
        )

        return {

            "sessions":
                len(sessions),

            "completed":
                completed,

            "failed":
                failed,

            "cancelled":
                cancelled,

            "active":
                (
                    self.active.session_id
                    if self.active
                    else None
                ),

            "history_limit":
                self.history_limit,
        }

    # =====================================================
    # LENGTH
    # =====================================================

    def __len__(
        self,
    ) -> int:

        with self._lock:

            return len(
                self._sessions
            )


# =========================================================
# GLOBAL SESSION MANAGER
# =========================================================

scanner_sessions = ScannerSessionManager(
    history_limit=100
)


# =========================================================
# CONVENIENCE FUNCTIONS
# =========================================================

def create_scanner_session(
    *,
    name: str = "ScannerSession",
    symbols_total: int = 0,
    scanners_total: int = 0,
    metadata: Optional[
        Dict[str, Any]
    ] = None,
) -> ScannerSession:

    return scanner_sessions.create(

        name=name,

        symbols_total=symbols_total,

        scanners_total=scanners_total,

        metadata=metadata,
    )


def get_active_scanner_session(
) -> Optional[ScannerSession]:

    return scanner_sessions.active


def complete_scanner_session(
) -> Optional[ScannerSession]:

    return (
        scanner_sessions
        .complete_active()
    )


def fail_scanner_session(
    error: Optional[
        BaseException | str
    ] = None,
) -> Optional[ScannerSession]:

    return (
        scanner_sessions
        .fail_active(
            error
        )
    )


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "ScannerSessionStatus",

    "ScannerSession",

    "ScannerSessionManager",

    "scanner_sessions",

    "create_scanner_session",

    "get_active_scanner_session",

    "complete_scanner_session",

    "fail_scanner_session",
]


# ==========================
# END OF FILE
# ==========================