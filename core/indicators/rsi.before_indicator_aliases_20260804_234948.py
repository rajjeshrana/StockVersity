"""
==================================================
Professional RSI

Incremental Wilder RSI

Complexity

O(1)
==================================================
"""

from __future__ import annotations

from .base_indicator import BaseIndicator


class RSI(BaseIndicator):

    def __init__(self, period: int = 14):

        super().__init__(period)

        self.previous_close = None

        self.avg_gain = 0.0

        self.avg_loss = 0.0

        self.counter = 0

    def update(self, close: float):

        if self.previous_close is None:

            self.previous_close = close

            return None

        change = close - self.previous_close

        gain = max(change, 0)

        loss = abs(min(change, 0))

        self.previous_close = close

        self.counter += 1

        if self.counter < self.period:

            self.avg_gain += gain

            self.avg_loss += loss

            return None

        if self.counter == self.period:

            self.avg_gain = (

                self.avg_gain + gain

            ) / self.period

            self.avg_loss = (

                self.avg_loss + loss

            ) / self.period

        else:

            self.avg_gain = (

                (self.avg_gain * (self.period - 1))

                + gain

            ) / self.period

            self.avg_loss = (

                (self.avg_loss * (self.period - 1))

                + loss

            ) / self.period

        if self.avg_loss == 0:

            self.value = 100.0

        else:

            rs = self.avg_gain / self.avg_loss

            self.value = (

                100

                -

                (

                    100

                    /

                    (1 + rs)

                )

            )

        self.ready = True

        return self.value