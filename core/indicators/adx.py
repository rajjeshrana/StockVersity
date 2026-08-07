"""
==========================================================

Professional ADX

Incremental Wilder ADX

O(1)

==========================================================
"""

from __future__ import annotations

from .base_indicator import BaseIndicator


class ADX(BaseIndicator):

    def __init__(

        self,

        period: int = 14,

    ):

        super().__init__(period)

        self.previous_high = None

        self.previous_low = None

        self.previous_close = None

        self.counter = 0

        self.atr = 0.0

        self.plus_dm = 0.0

        self.minus_dm = 0.0

        self.plus_di = 0.0

        self.minus_di = 0.0

        self.dx = 0.0

    def update(

        self,

        high,

        low,

        close,

    ):

        if self.previous_high is None:

            self.previous_high = high

            self.previous_low = low

            self.previous_close = close

            return None

        up_move = high - self.previous_high

        down_move = self.previous_low - low

        plus = 0.0

        minus = 0.0

        if up_move > down_move and up_move > 0:

            plus = up_move

        if down_move > up_move and down_move > 0:

            minus = down_move

        tr = max(

            high - low,

            abs(high - self.previous_close),

            abs(low - self.previous_close),

        )

        self.previous_high = high

        self.previous_low = low

        self.previous_close = close
        self.counter += 1

        if self.counter < self.period:

            self.atr += tr
            self.plus_dm += plus
            self.minus_dm += minus

            return None

        if self.counter == self.period:

            self.atr = (self.atr + tr) / self.period

            self.plus_dm = (
                self.plus_dm + plus
            ) / self.period

            self.minus_dm = (
                self.minus_dm + minus
            ) / self.period

        else:

            self.atr = (
                (self.atr * (self.period - 1))
                + tr
            ) / self.period

            self.plus_dm = (
                (self.plus_dm * (self.period - 1))
                + plus
            ) / self.period

            self.minus_dm = (
                (self.minus_dm * (self.period - 1))
                + minus
            ) / self.period

        if self.atr == 0:

            return None

        self.plus_di = (
            100.0 *
            self.plus_dm /
            self.atr
        )

        self.minus_di = (
            100.0 *
            self.minus_dm /
            self.atr
        )

        denominator = (
            self.plus_di +
            self.minus_di
        )

        if denominator == 0:

            return None

        dx = (
            abs(
                self.plus_di -
                self.minus_di
            )
            /
            denominator
        ) * 100

        if self.counter == self.period:

            self.dx = dx

        else:

            self.dx = (
                (
                    self.dx *
                    (self.period - 1)
                )
                +
                dx
            ) / self.period

        self.value = self.dx

        self.ready = True

        return self.value

# ==========================================================
# COMPATIBILITY ALIAS
# ==========================================================
# core.indicator_engine imports ADXIndicator, while this
# module's implementation class is named ADX.
ADXIndicator = ADX

