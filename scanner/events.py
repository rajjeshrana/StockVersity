"""
=========================================================
StockVersity Scanner Pro
Scanner Event System
Version : 2.0
=========================================================

Internal event bus for scanner components.

Responsibilities
----------------
• Publish scanner events
• Subscribe / unsubscribe listeners
• Scanner lifecycle events
• Signal/result events
• Market-data events
• Session events
• Error events
• Thread-safe event dispatch
• Event history
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from enum import Enum

from threading import RLock

from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional

from uuid import uuid4


# =========================================================
# EVENT TYPE
# =========================================================

class ScannerEventType(str, Enum):

    # -----------------------------------------------------
    # ENGINE
    # -----------------------------------------------------

    ENGINE_STARTED = "ENGINE_STARTED"

    ENGINE_STOPPED = "ENGINE_STOPPED"

    ENGINE_ERROR = "ENGINE_ERROR"

    # -----------------------------------------------------
    # SCANNER
    # -----------------------------------------------------

    SCANNER_STARTED = "SCANNER_STARTED"

    SCANNER_COMPLETED = "SCANNER_COMPLETED"

    SCANNER_FAILED = "SCANNER_FAILED"

    # -----------------------------------------------------
    # SYMBOL
    # -----------------------------------------------------

    SYMBOL_STARTED = "SYMBOL_STARTED"

    SYMBOL_COMPLETED = "SYMBOL_COMPLETED"

    SYMBOL_FAILED = "SYMBOL_FAILED"

    # -----------------------------------------------------
    # SIGNAL
    # -----------------------------------------------------

    SIGNAL_GENERATED = "SIGNAL_GENERATED"

    SIGNAL_ACCEPTED = "SIGNAL_ACCEPTED"

    SIGNAL_REJECTED = "SIGNAL_REJECTED"

    # -----------------------------------------------------
    # RESULT
    # -----------------------------------------------------

    RESULT_CREATED = "RESULT_CREATED"

    RESULT_UPDATED = "RESULT_UPDATED"

    RESULT_REMOVED = "RESULT_REMOVED"

    # -----------------------------------------------------
    # MARKET DATA
    # -----------------------------------------------------

    MARKET_DATA_UPDATED = "MARKET_DATA_UPDATED"

    MARKET_DATA_INVALID = "MARKET_DATA_INVALID"

    MARKET_DATA_STALE = "MARKET_DATA_STALE"

    # -----------------------------------------------------
    # CONTEXT
    # -----------------------------------------------------

    CONTEXT_UPDATED = "CONTEXT_UPDATED"

    # -----------------------------------------------------
    # SESSION
    # -----------------------------------------------------

    SESSION_CREATED = "SESSION_CREATED"

    SESSION_STARTED = "SESSION_STARTED"

    SESSION_COMPLETED = "SESSION_COMPLETED"

    SESSION_FAILED = "SESSION_FAILED"

    SESSION_CANCELLED = "SESSION_CANCELLED"

    # -----------------------------------------------------
    # SYSTEM
    # -----------------------------------------------------

    HEALTH_WARNING = "HEALTH_WARNING"

    HEALTH_ERROR = "HEALTH_ERROR"

    CACHE_CLEARED = "CACHE_CLEARED"

    CUSTOM = "CUSTOM"


# =========================================================
# SCANNER EVENT
# =========================================================

@dataclass(slots=True)
class ScannerEvent:
    """
    One event generated inside the scanner subsystem.
    """

    event_type: ScannerEventType

    source: str = ""

    symbol: str = ""

    scanner_name: str = ""

    timeframe: str = ""

    message: str = ""

    payload: Dict[str, Any] = field(
        default_factory=dict
    )

    event_id: str = field(
        default_factory=lambda: uuid4().hex
    )

    created_at: datetime = field(
        default_factory=datetime.now
    )

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "event_id":
                self.event_id,

            "event_type":
                self.event_type.value,

            "source":
                self.source,

            "symbol":
                self.symbol,

            "scanner_name":
                self.scanner_name,

            "timeframe":
                self.timeframe,

            "message":
                self.message,

            "payload":
                dict(
                    self.payload
                ),

            "created_at":
                self.created_at.isoformat(),
        }


# =========================================================
# EVENT CALLBACK
# =========================================================

EventCallback = Callable[
    [ScannerEvent],
    None,
]


# =========================================================
# EVENT BUS
# =========================================================

class ScannerEventBus:
    """
    Thread-safe internal event dispatcher.
    """

    def __init__(
        self,
        *,
        history_limit: int = 500,
    ) -> None:

        self.history_limit = max(
            0,
            int(history_limit),
        )

        self._listeners: Dict[
            ScannerEventType,
            List[EventCallback]
        ] = {}

        self._global_listeners: List[
            EventCallback
        ] = []

        self._history: List[
            ScannerEvent
        ] = []

        self._errors: List[str] = []

        self._lock = RLock()

    # =====================================================
    # SUBSCRIBE
    # =====================================================

    def subscribe(
        self,
        event_type: ScannerEventType,
        callback: EventCallback,
    ) -> bool:
        """
        Subscribe callback to one event type.
        """

        if not callable(
            callback
        ):

            raise TypeError(
                "callback must be callable."
            )

        if not isinstance(
            event_type,
            ScannerEventType,
        ):

            event_type = (
                ScannerEventType(
                    event_type
                )
            )

        with self._lock:

            listeners = (
                self._listeners
                .setdefault(
                    event_type,
                    [],
                )
            )

            if callback in listeners:

                return False

            listeners.append(
                callback
            )

            return True

    # =====================================================
    # SUBSCRIBE ALL
    # =====================================================

    def subscribe_all(
        self,
        callback: EventCallback,
    ) -> bool:
        """
        Subscribe callback to every scanner event.
        """

        if not callable(
            callback
        ):

            raise TypeError(
                "callback must be callable."
            )

        with self._lock:

            if (
                callback
                in self._global_listeners
            ):

                return False

            self._global_listeners.append(
                callback
            )

            return True

    # =====================================================
    # UNSUBSCRIBE
    # =====================================================

    def unsubscribe(
        self,
        event_type: ScannerEventType,
        callback: EventCallback,
    ) -> bool:

        if not isinstance(
            event_type,
            ScannerEventType,
        ):

            try:

                event_type = (
                    ScannerEventType(
                        event_type
                    )
                )

            except ValueError:

                return False

        with self._lock:

            listeners = (
                self._listeners.get(
                    event_type
                )
            )

            if not listeners:

                return False

            try:

                listeners.remove(
                    callback
                )

            except ValueError:

                return False

            if not listeners:

                self._listeners.pop(
                    event_type,
                    None,
                )

            return True

    # =====================================================
    # UNSUBSCRIBE ALL
    # =====================================================

    def unsubscribe_all(
        self,
        callback: EventCallback,
    ) -> bool:

        removed = False

        with self._lock:

            try:

                self._global_listeners.remove(
                    callback
                )

                removed = True

            except ValueError:

                pass

            for event_type in list(
                self._listeners.keys()
            ):

                listeners = (
                    self._listeners[
                        event_type
                    ]
                )

                while callback in listeners:

                    listeners.remove(
                        callback
                    )

                    removed = True

                if not listeners:

                    del self._listeners[
                        event_type
                    ]

        return removed

    # =====================================================
    # PUBLISH
    # =====================================================

    def publish(
        self,
        event: ScannerEvent,
    ) -> ScannerEvent:
        """
        Publish an existing ScannerEvent.
        """

        if not isinstance(
            event,
            ScannerEvent,
        ):

            raise TypeError(
                "event must be ScannerEvent."
            )

        # ---------------------------------------------
        # STORE HISTORY
        # ---------------------------------------------

        with self._lock:

            if self.history_limit > 0:

                self._history.append(
                    event
                )

                if (
                    len(self._history)
                    > self.history_limit
                ):

                    overflow = (
                        len(self._history)
                        - self.history_limit
                    )

                    del self._history[
                        :overflow
                    ]

            listeners = list(
                self._listeners.get(
                    event.event_type,
                    [],
                )
            )

            global_listeners = list(
                self._global_listeners
            )

        # ---------------------------------------------
        # DISPATCH
        # ---------------------------------------------

        callbacks = (
            listeners
            + global_listeners
        )

        for callback in callbacks:

            try:

                callback(
                    event
                )

            except Exception as exc:

                self._record_error(
                    event,
                    callback,
                    exc,
                )

        return event

    # =====================================================
    # EMIT
    # =====================================================

    def emit(
        self,
        event_type: ScannerEventType,
        *,
        source: str = "",
        symbol: str = "",
        scanner_name: str = "",
        timeframe: str = "",
        message: str = "",
        payload: Optional[
            Dict[str, Any]
        ] = None,
    ) -> ScannerEvent:
        """
        Create and publish an event.
        """

        if not isinstance(
            event_type,
            ScannerEventType,
        ):

            event_type = (
                ScannerEventType(
                    event_type
                )
            )

        event = ScannerEvent(

            event_type=event_type,

            source=str(
                source
            ).strip(),

            symbol=str(
                symbol
            ).strip(),

            scanner_name=str(
                scanner_name
            ).strip(),

            timeframe=str(
                timeframe
            ).strip(),

            message=str(
                message
            ).strip(),

            payload=(
                dict(payload)
                if payload
                else {}
            ),
        )

        return self.publish(
            event
        )

    # =====================================================
    # RECORD LISTENER ERROR
    # =====================================================

    def _record_error(
        self,
        event: ScannerEvent,
        callback: EventCallback,
        error: BaseException,
    ) -> None:

        callback_name = getattr(
            callback,
            "__name__",
            callback.__class__.__name__,
        )

        message = (

            f"{event.event_type.value} -> "
            f"{callback_name}: "
            f"{type(error).__name__}: "
            f"{error}"
        )

        with self._lock:

            self._errors.append(
                message
            )

            if len(
                self._errors
            ) > 100:

                self._errors = (
                    self._errors[
                        -100:
                    ]
                )

    # =====================================================
    # LISTENERS
    # =====================================================

    def listener_count(
        self,
        event_type: Optional[
            ScannerEventType
        ] = None,
    ) -> int:

        with self._lock:

            if event_type is None:

                return (
                    len(
                        self._global_listeners
                    )
                    + sum(
                        len(listeners)

                        for listeners
                        in self._listeners.values()
                    )
                )

            if not isinstance(
                event_type,
                ScannerEventType,
            ):

                try:

                    event_type = (
                        ScannerEventType(
                            event_type
                        )
                    )

                except ValueError:

                    return 0

            return len(
                self._listeners.get(
                    event_type,
                    [],
                )
            )

    # =====================================================
    # HISTORY
    # =====================================================

    def history(
        self,
        *,
        event_type: Optional[
            ScannerEventType
        ] = None,
        limit: Optional[int] = None,
    ) -> List[ScannerEvent]:

        with self._lock:

            events = list(
                self._history
            )

        if event_type is not None:

            if not isinstance(
                event_type,
                ScannerEventType,
            ):

                try:

                    event_type = (
                        ScannerEventType(
                            event_type
                        )
                    )

                except ValueError:

                    return []

            events = [

                event

                for event in events

                if (
                    event.event_type
                    == event_type
                )
            ]

        if limit is not None:

            limit = max(
                0,
                int(limit),
            )

            if limit == 0:

                return []

            events = events[
                -limit:
            ]

        return list(
            reversed(
                events
            )
        )

    # =====================================================
    # LATEST
    # =====================================================

    def latest(
        self,
        event_type: Optional[
            ScannerEventType
        ] = None,
    ) -> Optional[ScannerEvent]:

        events = self.history(
            event_type=event_type,
            limit=1,
        )

        if not events:

            return None

        return events[
            0
        ]

    # =====================================================
    # ERRORS
    # =====================================================

    @property
    def errors(
        self,
    ) -> List[str]:

        with self._lock:

            return list(
                self._errors
            )

    # =====================================================
    # CLEAR ERRORS
    # =====================================================

    def clear_errors(
        self,
    ) -> None:

        with self._lock:

            self._errors.clear()

    # =====================================================
    # CLEAR HISTORY
    # =====================================================

    def clear_history(
        self,
    ) -> None:

        with self._lock:

            self._history.clear()

    # =====================================================
    # CLEAR LISTENERS
    # =====================================================

    def clear_listeners(
        self,
    ) -> None:

        with self._lock:

            self._listeners.clear()

            self._global_listeners.clear()

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(
        self,
    ) -> None:

        with self._lock:

            self._history.clear()

            self._errors.clear()

            self._listeners.clear()

            self._global_listeners.clear()

    # =====================================================
    # STATUS
    # =====================================================

    def status(
        self,
    ) -> Dict[str, Any]:

        with self._lock:

            subscriptions = {

                event_type.value:
                    len(listeners)

                for event_type, listeners
                in self._listeners.items()
            }

            return {

                "history_size":
                    len(
                        self._history
                    ),

                "history_limit":
                    self.history_limit,

                "listener_count":
                    self.listener_count(),

                "global_listeners":
                    len(
                        self._global_listeners
                    ),

                "subscriptions":
                    subscriptions,

                "error_count":
                    len(
                        self._errors
                    ),
            }

    # =====================================================
    # LENGTH
    # =====================================================

    def __len__(
        self,
    ) -> int:

        with self._lock:

            return len(
                self._history
            )


# =========================================================
# GLOBAL EVENT BUS
# =========================================================

scanner_events = ScannerEventBus(
    history_limit=500
)


# =========================================================
# CONVENIENCE FUNCTIONS
# =========================================================

def emit_scanner_event(
    event_type: ScannerEventType,
    *,
    source: str = "",
    symbol: str = "",
    scanner_name: str = "",
    timeframe: str = "",
    message: str = "",
    payload: Optional[
        Dict[str, Any]
    ] = None,
) -> ScannerEvent:

    return scanner_events.emit(

        event_type,

        source=source,

        symbol=symbol,

        scanner_name=scanner_name,

        timeframe=timeframe,

        message=message,

        payload=payload,
    )


def subscribe_scanner_event(
    event_type: ScannerEventType,
    callback: EventCallback,
) -> bool:

    return scanner_events.subscribe(
        event_type,
        callback,
    )


def unsubscribe_scanner_event(
    event_type: ScannerEventType,
    callback: EventCallback,
) -> bool:

    return scanner_events.unsubscribe(
        event_type,
        callback,
    )


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "ScannerEventType",

    "ScannerEvent",

    "EventCallback",

    "ScannerEventBus",

    "scanner_events",

    "emit_scanner_event",

    "subscribe_scanner_event",

    "unsubscribe_scanner_event",
]


# ==========================
# END OF FILE
# ==========================