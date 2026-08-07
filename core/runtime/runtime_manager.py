"""
StockVersity Runtime Manager

Connects

Scanner
↓

Signal Dispatcher
↓

Dashboard Runtime

One runtime for entire application.
"""

from __future__ import annotations

from typing import List

from .signal_dispatcher import (
    get_signal_dispatcher,
)

from .dashboard_runtime import (
    DashboardRuntime,
)


class RuntimeManager:

    def __init__(self):

        self.dispatcher = (
            get_signal_dispatcher()
        )

        self.dashboard = (
            DashboardRuntime()
        )

    # -------------------------------------------------

    def publish(
        self,
        opportunities: List[dict],
    ) -> None:

        opportunities = (
            opportunities or []
        )

        self.dashboard.build_snapshot(
            opportunities
        )

        self.dispatcher.publish(
            opportunities
        )

    # -------------------------------------------------

    @property
    def snapshot(
        self,
    ):

        return self.dashboard.snapshot


_runtime = RuntimeManager()


def get_runtime():

    return _runtime