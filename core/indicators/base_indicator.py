"""
==========================================================
StockVersity Scanner Pro
Base Indicator
==========================================================

Every indicator inherits from this class.

Author : StockVersity
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod


class BaseIndicator(ABC):

    """
    Base class for every indicator.
    """

    def __init__(self, period: int):

        self.period = period

        self.ready = False

        self.value = None

    @abstractmethod
    def update(self, *args, **kwargs):
        """
        Update indicator using latest candle.
        """
        pass

    def reset(self):

        self.ready = False

        self.value = None

    def is_ready(self):

        return self.ready

    def latest(self):

        return self.value