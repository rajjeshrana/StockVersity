from __future__ import annotations

import threading
import traceback
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

# =====================================================
# EVENT
# =====================================================

@dataclass(slots=True)
class Event:

    name: str

    payload: Dict[str, Any] = field(

        default_factory=dict

    )

    source: str = "System"

    timestamp: datetime = field(

        default_factory=datetime.now

    )

    priority: int = 0


# =====================================================
# EVENT LISTENER
# =====================================================

@dataclass(slots=True)
class EventListener:

    callback: Callable

    priority: int = 0

    asynchronous: bool = False

    once: bool = False


# =====================================================
# EVENT BUS
# =====================================================

class EventBus:

    _instance = None

    _lock = threading.Lock()

    # -------------------------------------------------

    def __new__(cls):

        with cls._lock:

            if cls._instance is None:

                cls._instance = super().__new__(

                    cls

                )

        return cls._instance

    # -------------------------------------------------

    def __init__(self):

        if getattr(

            self,

            "_initialized",

            False,

        ):

            return

        self._initialized = True

        self.listeners = defaultdict(

            list

        )

        self.history = deque(

            maxlen=1000

        )

        self.executor = ThreadPoolExecutor(

            max_workers=8

        )

        self.statistics = {

            "published": 0,

            "handled": 0,

            "errors": 0,

        }

        self.listener_lock = threading.RLock()

    # =====================================================
    # SUBSCRIBE
    # =====================================================

    def subscribe(

        self,

        event_name: str,

        callback: Callable,

        priority: int = 0,

        asynchronous: bool = False,

        once: bool = False,

    ):

        listener = EventListener(

            callback=callback,

            priority=priority,

            asynchronous=asynchronous,

            once=once,

        )

        with self.listener_lock:

            self.listeners[

                event_name

            ].append(

                listener

            )

            self.listeners[

                event_name

            ].sort(

                key=lambda l: l.priority,

                reverse=True,

            )

        return listener

    # =====================================================
    # UNSUBSCRIBE
    # =====================================================

    def unsubscribe(

        self,

        event_name: str,

        callback: Callable,

    ):

        with self.listener_lock:

            listeners = self.listeners.get(

                event_name,

                [],

            )

            self.listeners[event_name] = [

                listener

                for listener in listeners

                if listener.callback != callback

            ]

    # =====================================================
    # CLEAR EVENT
    # =====================================================

    def clear(

        self,

        event_name: str,

    ):

        with self.listener_lock:

            self.listeners.pop(

                event_name,

                None,

            )

    # =====================================================
    # CLEAR ALL
    # =====================================================

    def clear_all(self):

        with self.listener_lock:

            self.listeners.clear()

            self.history.clear()

            self.statistics = {

                "published": 0,

                "handled": 0,

                "errors": 0,

            }
                # =====================================================
    # PUBLISH EVENT
    # =====================================================

    def publish(

        self,

        event_name: str,

        payload: Optional[Dict[str, Any]] = None,

        source: str = "System",

        priority: int = 0,

    ):

        event = Event(

            name=event_name,

            payload=payload or {},

            source=source,

            priority=priority,

        )

        self.statistics["published"] += 1

        self.history.append(

            event

        )

        self._dispatch(

            event

        )

        return event

    # =====================================================
    # DISPATCH
    # =====================================================

    def _dispatch(

        self,

        event: Event,

    ):

        listeners = []

        with self.listener_lock:

            listeners.extend(

                self.listeners.get(

                    event.name,

                    [],

                )

            )

            listeners.extend(

                self.listeners.get(

                    "*",

                    [],

                )

            )

        for listener in listeners:

            if listener.asynchronous:

                self.executor.submit(

                    self._safe_execute,

                    listener,

                    event,

                )

            else:

                self._safe_execute(

                    listener,

                    event,

                )

    # =====================================================
    # SAFE EXECUTION
    # =====================================================

    def _safe_execute(

        self,

        listener: EventListener,

        event: Event,

    ):

        try:

            listener.callback(

                event

            )

            self.statistics["handled"] += 1

        except Exception:

            self.statistics["errors"] += 1

            traceback.print_exc()

        finally:

            if listener.once:

                self.unsubscribe(

                    event.name,

                    listener.callback,

                )

    # =====================================================
    # EMIT
    # =====================================================

    def emit(

        self,

        event_name: str,

        **payload,

    ):

        return self.publish(

            event_name,

            payload,

        )

    # =====================================================
    # HISTORY
    # =====================================================

    def recent_events(

        self,

        limit: int = 20,

    ):

        if limit <= 0:

            return []

        return list(

            self.history

        )[-limit:]

    # -------------------------------------------------

    def last_event(

        self,

    ):

        if not self.history:

            return None

        return self.history[-1]

    # -------------------------------------------------

    def history_size(

        self,

    ):

        return len(

            self.history

        )

    # =====================================================
    # LISTENER INFORMATION
    # =====================================================

    def listeners_for(

        self,

        event_name: str,

    ):

        return list(

            self.listeners.get(

                event_name,

                [],

            )

        )

    # -------------------------------------------------

    def listener_count(

        self,

        event_name: Optional[str] = None,

    ):

        if event_name is None:

            return sum(

                len(items)

                for items in self.listeners.values()

            )

        return len(

            self.listeners.get(

                event_name,

                [],

            )

        )

    # =====================================================
    # STATISTICS
    # =====================================================

    def stats(

        self,

    ):

        return {

            "published": self.statistics["published"],

            "handled": self.statistics["handled"],

            "errors": self.statistics["errors"],

            "registered_events": len(

                self.listeners

            ),

            "registered_listeners": self.listener_count(),

            "history_size": len(

                self.history

            ),

        }
        # =====================================================
    # WAIT FOR EVENT
    # =====================================================

    def wait_for(

        self,

        event_name: str,

        timeout: Optional[float] = None,

    ):

        """
        Blocks until the specified event is received
        or timeout expires.
        """

        signal = threading.Event()

        result = {"event": None}

        def _listener(event):

            result["event"] = event

            signal.set()

        self.subscribe(

            event_name,

            _listener,

            once=True,

        )

        signal.wait(timeout)

        return result["event"]

    # =====================================================
    # SEARCH HISTORY
    # =====================================================

    def find_events(

        self,

        event_name: Optional[str] = None,

        source: Optional[str] = None,

    ):

        results = []

        for event in self.history:

            if event_name and event.name != event_name:

                continue

            if source and event.source != source:

                continue

            results.append(event)

        return results

    # =====================================================
    # SERIALIZATION
    # =====================================================

    def history_to_dict(

        self,

    ):

        data = []

        for event in self.history:

            data.append(

                {

                    "name": event.name,

                    "payload": event.payload,

                    "source": event.source,

                    "priority": event.priority,

                    "timestamp": event.timestamp.isoformat(),

                }

            )

        return data

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(

        self,

        wait: bool = True,

    ):

        self.executor.shutdown(

            wait=wait,

        )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ):

        return (

            "EventBus("

            f"listeners={self.listener_count()}, "

            f"events={len(self.history)}, "

            f"published={self.statistics['published']})"

        )

    # -------------------------------------------------

    def __str__(

        self,

    ):

        stats = self.stats()

        return (

            "EventBus\n"

            f"Published : {stats['published']}\n"

            f"Handled   : {stats['handled']}\n"

            f"Errors    : {stats['errors']}\n"

            f"Listeners : {stats['registered_listeners']}\n"

            f"History   : {stats['history_size']}"

        )


# =====================================================
# GLOBAL SINGLETON
# =====================================================

event_bus = EventBus()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "Event",

    "EventListener",

    "EventBus",

    "event_bus",

]