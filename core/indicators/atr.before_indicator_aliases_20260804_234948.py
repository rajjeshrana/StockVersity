"""
====================================================

Professional ATR

Wilder ATR

O(1)

====================================================
"""

from __future__ import annotations

from .base_indicator import BaseIndicator


class ATR(BaseIndicator):

    def __init__(

        self,

        period: int = 14,

    ):

        super().__init__(period)

        self.previous_close = None

        self.atr = None

        self.counter = 0

    def update(

        self,

        high: float,

        low: float,

        close: float,

    ):

        if self.previous_close is None:

            tr = high - low

            self.previous_close = close

            self.counter += 1

            self.atr = tr

            return None

        tr = max(

            high - low,

            abs(high - self.previous_close),

            abs(low - self.previous_close),

        )

        self.previous_close = close

        self.counter += 1

        if self.counter < self.period:

            self.atr += tr

            return None

        if self.counter == self.period:

            self.atr = (

                self.atr + tr

            ) / self.period

        else:

            self.atr = (

                (

                    self.atr

                    *

                    (

                        self.period - 1

                    )

                )

                +

                tr

            ) / self.period

        self.value = self.atr

        self.ready = True

        return self.value