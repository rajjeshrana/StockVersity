"""
=========================================================
StockVersity Scanner Pro
Scanner Runtime State
Version : 2.0
=========================================================

Central runtime state for the scanner subsystem.

Responsibilities
----------------
• Track scanner engine state
• Track current scanner
• Track current symbol
• Track scan progress
• Track start/finish timestamps
• Track latest error
• Track pause/resume/stop state
• Provide dashboard-ready runtime status
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
from typing import Optional


# =========================================================
# ENGINE STATE
# =========================================================

class ScannerEngineState(str, Enum):

    IDLE = "IDLE"

    STARTING = "STARTING"

    RUNNING = "RUNNING"

    PAUSED = "PAUSED"

    STOPPING = "STOPPING"

    STOPPED = "STOPPED"

    COMPLETED = "COMPLETED"

    ERROR = "ERROR"


# =========================================================
# RUNTIME STATE DATA
# =========================================================

@dataclass(slots=True)
class ScannerRuntimeSnapshot:
    """
    Immutable-style snapshot of current scanner runtime.
    """

    state: ScannerEngineState = (
        ScannerEngineState.IDLE
    )

    session_id: str = ""

    current_scanner: str = ""

    current_symbol: str = ""

    current_timeframe: str = ""

    symbols_total: int = 0

    symbols_processed: int = 0

    scanners_total: int = 0

    scanners_completed: int = 0

    signals_found: int = 0

    started_at: Optional[datetime] = None

    finished_at: Optional[datetime] = None

    updated_at: datetime = field(
        default_factory=datetime.now
    )

    last_error: str = ""

    message: str = ""

    # =====================================================
    # SYMBOL PROGRESS
    # =====================================================

    @property
    def symbol_progress(
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
    def scanner_progress(
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
    # RUNNING
    # =====================================================

    @property
    def running(
        self,
    ) -> bool:

        return self.state in (
            ScannerEngineState.STARTING,
            ScannerEngineState.RUNNING,
            ScannerEngineState.PAUSED,
            ScannerEngineState.STOPPING,
        )

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "state":
                self.state.value,

            "running":
                self.running,

            "session_id":
                self.session_id,

            "current_scanner":
                self.current_scanner,

            "current_symbol":
                self.current_symbol,

            "current_timeframe":
                self.current_timeframe,

            "symbols_total":
                self.symbols_total,

            "symbols_processed":
                self.symbols_processed,

            "symbol_progress":
                self.symbol_progress,

            "scanners_total":
                self.scanners_total,

            "scanners_completed":
                self.scanners_completed,

            "scanner_progress":
                self.scanner_progress,

            "signals_found":
                self.signals_found,

            "started_at":
                (
                    self.started_at.isoformat()
                    if self.started_at
                    else None
                ),

            "finished_at":
                (
                    self.finished_at.isoformat()
                    if self.finished_at
                    else None
                ),

            "updated_at":
                self.updated_at.isoformat(),

            "last_error":
                self.last_error,

            "message":
                self.message,
        }


# =========================================================
# SCANNER STATE MANAGER
# =========================================================

class ScannerStateManager:
    """
    Thread-safe runtime state manager.
    """

    def __init__(
        self,
    ) -> None:

        self._lock = RLock()

        self._state = (
            ScannerRuntimeSnapshot()
        )

    # =====================================================
    # TOUCH
    # =====================================================

    def _touch(
        self,
    ) -> None:

        self._state.updated_at = (
            datetime.now()
        )

    # =====================================================
    # START
    # =====================================================

    def start(
        self,
        *,
        session_id: str = "",
        symbols_total: int = 0,
        scanners_total: int = 0,
        message: str = "",
    ) -> None:

        with self._lock:

            now = datetime.now()

            self._state = (
                ScannerRuntimeSnapshot(

                    state=(
                        ScannerEngineState.RUNNING
                    ),

                    session_id=str(
                        session_id
                    ),

                    symbols_total=max(
                        0,
                        int(symbols_total),
                    ),

                    scanners_total=max(
                        0,
                        int(scanners_total),
                    ),

                    started_at=now,

                    updated_at=now,

                    message=str(
                        message
                    ),
                )
            )

    # =====================================================
    # STARTING
    # =====================================================

    def starting(
        self,
        message: str = "",
    ) -> None:

        with self._lock:

            self._state.state = (
                ScannerEngineState.STARTING
            )

            self._state.message = str(
                message
            )

            self._touch()

    # =====================================================
    # CURRENT SCANNER
    # =====================================================

    def set_scanner(
        self,
        scanner_name: str,
        *,
        timeframe: Optional[str] = None,
    ) -> None:

        with self._lock:

            self._state.current_scanner = (
                str(scanner_name)
            )

            if timeframe is not None:

                self._state.current_timeframe = (
                    str(timeframe)
                )

            self._touch()

    # =====================================================
    # CURRENT SYMBOL
    # =====================================================

    def set_symbol(
        self,
        symbol: str,
    ) -> None:

        with self._lock:

            self._state.current_symbol = (
                str(symbol)
            )

            self._touch()

    # =====================================================
    # TIMEFRAME
    # =====================================================

    def set_timeframe(
        self,
        timeframe: str,
    ) -> None:

        with self._lock:

            self._state.current_timeframe = (
                str(timeframe)
            )

            self._touch()

    # =====================================================
    # SYMBOL PROCESSED
    # =====================================================

    def symbol_processed(
        self,
        count: int = 1,
    ) -> None:

        with self._lock:

            self._state.symbols_processed += max(
                0,
                int(count),
            )

            if self._state.symbols_total > 0:

                self._state.symbols_processed = min(
                    self._state.symbols_processed,
                    self._state.symbols_total,
                )

            self._touch()

    # =====================================================
    # SCANNER COMPLETED
    # =====================================================

    def scanner_completed(
        self,
        count: int = 1,
    ) -> None:

        with self._lock:

            self._state.scanners_completed += max(
                0,
                int(count),
            )

            if self._state.scanners_total > 0:

                self._state.scanners_completed = min(
                    self._state.scanners_completed,
                    self._state.scanners_total,
                )

            self._touch()

    # =====================================================
    # SIGNAL FOUND
    # =====================================================

    def signal_found(
        self,
        count: int = 1,
    ) -> None:

        with self._lock:

            self._state.signals_found += max(
                0,
                int(count),
            )

            self._touch()

    # =====================================================
    # MESSAGE
    # =====================================================

    def set_message(
        self,
        message: str,
    ) -> None:

        with self._lock:

            self._state.message = str(
                message
            )

            self._touch()

    # =====================================================
    # PAUSE
    # =====================================================

    def pause(
        self,
        message: str = "Scanner paused.",
    ) -> bool:

        with self._lock:

            if (
                self._state.state
                != ScannerEngineState.RUNNING
            ):

                return False

            self._state.state = (
                ScannerEngineState.PAUSED
            )

            self._state.message = (
                message
            )

            self._touch()

            return True

    # =====================================================
    # RESUME
    # =====================================================

    def resume(
        self,
        message: str = "Scanner resumed.",
    ) -> bool:

        with self._lock:

            if (
                self._state.state
                != ScannerEngineState.PAUSED
            ):

                return False

            self._state.state = (
                ScannerEngineState.RUNNING
            )

            self._state.message = (
                message
            )

            self._touch()

            return True

    # =====================================================
    # STOPPING
    # =====================================================

    def stopping(
        self,
        message: str = "Scanner stopping.",
    ) -> None:

        with self._lock:

            self._state.state = (
                ScannerEngineState.STOPPING
            )

            self._state.message = (
                message
            )

            self._touch()

    # =====================================================
    # STOP
    # =====================================================

    def stop(
        self,
        message: str = "Scanner stopped.",
    ) -> None:

        with self._lock:

            now = datetime.now()

            self._state.state = (
                ScannerEngineState.STOPPED
            )

            self._state.finished_at = now

            self._state.current_scanner = ""

            self._state.current_symbol = ""

            self._state.message = (
                message
            )

            self._state.updated_at = now

    # =====================================================
    # COMPLETE
    # =====================================================

    def complete(
        self,
        message: str = "Scan completed.",
    ) -> None:

        with self._lock:

            now = datetime.now()

            self._state.state = (
                ScannerEngineState.COMPLETED
            )

            self._state.finished_at = now

            self._state.current_scanner = ""

            self._state.current_symbol = ""

            self._state.message = (
                message
            )

            self._state.updated_at = now

    # =====================================================
    # ERROR
    # =====================================================

    def error(
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

        with self._lock:

            now = datetime.now()

            self._state.state = (
                ScannerEngineState.ERROR
            )

            self._state.last_error = (
                message
            )

            self._state.message = (
                message
            )

            self._state.finished_at = now

            self._state.updated_at = now

    # =====================================================
    # CLEAR ERROR
    # =====================================================

    def clear_error(
        self,
    ) -> None:

        with self._lock:

            self._state.last_error = ""

            if (
                self._state.state
                == ScannerEngineState.ERROR
            ):

                self._state.state = (
                    ScannerEngineState.IDLE
                )

            self._touch()

    # =====================================================
    # RESET
    # =====================================================

    def reset(
        self,
    ) -> None:

        with self._lock:

            self._state = (
                ScannerRuntimeSnapshot()
            )

    # =====================================================
    # SNAPSHOT
    # =====================================================

    def snapshot(
        self,
    ) -> ScannerRuntimeSnapshot:
        """
        Return a detached copy of current state.
        """

        with self._lock:

            state = self._state

            return ScannerRuntimeSnapshot(

                state=state.state,

                session_id=state.session_id,

                current_scanner=(
                    state.current_scanner
                ),

                current_symbol=(
                    state.current_symbol
                ),

                current_timeframe=(
                    state.current_timeframe
                ),

                symbols_total=(
                    state.symbols_total
                ),

                symbols_processed=(
                    state.symbols_processed
                ),

                scanners_total=(
                    state.scanners_total
                ),

                scanners_completed=(
                    state.scanners_completed
                ),

                signals_found=(
                    state.signals_found
                ),

                started_at=(
                    state.started_at
                ),

                finished_at=(
                    state.finished_at
                ),

                updated_at=(
                    state.updated_at
                ),

                last_error=(
                    state.last_error
                ),

                message=(
                    state.message
                ),
            )

    # =====================================================
    # STATUS
    # =====================================================

    def status(
        self,
    ) -> Dict[str, Any]:

        return (
            self.snapshot()
            .to_dict()
        )

    # =====================================================
    # IS RUNNING
    # =====================================================

    @property
    def is_running(
        self,
    ) -> bool:

        with self._lock:

            return (
                self._state.state
                == ScannerEngineState.RUNNING
            )

    # =====================================================
    # IS PAUSED
    # =====================================================

    @property
    def is_paused(
        self,
    ) -> bool:

        with self._lock:

            return (
                self._state.state
                == ScannerEngineState.PAUSED
            )

    # =====================================================
    # SHOULD STOP
    # =====================================================

    @property
    def should_stop(
        self,
    ) -> bool:

        with self._lock:

            return self._state.state in (

                ScannerEngineState.STOPPING,

                ScannerEngineState.STOPPED,

                ScannerEngineState.ERROR,
            )


# =========================================================
# GLOBAL STATE MANAGER
# =========================================================

scanner_state = ScannerStateManager()


# =========================================================
# CONVENIENCE FUNCTIONS
# =========================================================

def get_scanner_state(
) -> ScannerRuntimeSnapshot:

    return scanner_state.snapshot()


def get_scanner_status(
) -> Dict[str, Any]:

    return scanner_state.status()


def scanner_is_running(
) -> bool:

    return scanner_state.is_running


def scanner_is_paused(
) -> bool:

    return scanner_state.is_paused


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "ScannerEngineState",

    "ScannerRuntimeSnapshot",

    "ScannerStateManager",

    "scanner_state",

    "get_scanner_state",

    "get_scanner_status",

    "scanner_is_running",

    "scanner_is_paused",
]


# ==========================
# END OF FILE
# ==========================