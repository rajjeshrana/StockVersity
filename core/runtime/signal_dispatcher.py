"""
StockVersity Runtime Signal Dispatcher

Single source of truth for scanner opportunities.

Desktop
Web
Mobile

All subscribe here.
"""

from __future__ import annotations

from threading import RLock
from typing import Callable, Dict, List, Any


Callback = Callable[[List[dict]], None]


class SignalDispatcher:

    def __init__(self):

        self._lock = RLock()

        self._callbacks: Dict[str, Callback] = {}

        self._latest: List[dict] = []

    # ----------------------------------------------------

    def publish(
        self,
        opportunities: List[dict],
    ) -> None:

        if opportunities is None:
            opportunities = []

        with self._lock:

            self._latest = list(opportunities)

            callbacks = list(
                self._callbacks.items()
            )

        for name, callback in callbacks:

            try:

                callback(self._latest)

            except Exception as exc:

                print(
                    "[DISPATCHER]",
                    name,
                    exc,
                )

    # ----------------------------------------------------

    def subscribe(
        self,
        name: str,
        callback: Callback,
    ) -> None:

        with self._lock:

            self._callbacks[name] = callback

    # ----------------------------------------------------

    def unsubscribe(
        self,
        name: str,
    ) -> None:

        with self._lock:

            self._callbacks.pop(
                name,
                None,
            )

    # ----------------------------------------------------

    def latest(
        self,
    ) -> List[dict]:

        with self._lock:

            return list(
                self._latest
            )

    # ----------------------------------------------------

    def clear(
        self,
    ) -> None:

        with self._lock:

            self._latest.clear()

    # ----------------------------------------------------

    @property
    def subscriber_count(
        self,
    ) -> int:

        with self._lock:

            return len(
                self._callbacks
            )


_dispatcher = SignalDispatcher()


def get_signal_dispatcher() -> SignalDispatcher:

    return _dispatcher