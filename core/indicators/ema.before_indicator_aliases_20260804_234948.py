"""
==========================================================
EMA Indicator

Professional Incremental EMA

Time Complexity

O(1)

No recalculation of previous candles.
==========================================================
"""

from __future__ import annotations

from .base_indicator import BaseIndicator


class EMA(BaseIndicator):

    def __init__(self, period: int):

        super().__init__(period)

        self.multiplier = 2 / (period + 1)

        self.counter = 0

        self.sma = 0.0

    def update(self, close: float):

        self.counter += 1

        if self.counter < self.period:

            self.sma += close

            return None

        if self.counter == self.period:

            self.sma += close

            self.value = self.sma / self.period

            self.ready = True

            return self.value

        self.value = (

            close

            - self.value

        ) * self.multiplier + self.value

        return self.value

    def current(self):

        return self.value
    