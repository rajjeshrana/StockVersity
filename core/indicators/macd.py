"""
==========================================================
Professional MACD

Uses Incremental EMA

Time Complexity

O(1)

==========================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from .ema import EMA


@dataclass(slots=True)
class MACDValue:

    macd: float

    signal: float

    histogram: float


class MACD:

    """
    Incremental MACD

    Fast EMA 12
    Slow EMA 26
    Signal EMA 9
    """

    def __init__(

        self,

        fast_period: int = 12,

        slow_period: int = 26,

        signal_period: int = 9,

    ):

        self.fast = EMA(fast_period)

        self.slow = EMA(slow_period)

        self.signal = EMA(signal_period)

        self.ready = False

        self.value = None

    def update(

        self,

        close: float,

    ):

        fast = self.fast.update(close)

        slow = self.slow.update(close)

        if fast is None:

            return None

        if slow is None:

            return None

        macd = fast - slow

        signal = self.signal.update(macd)

        if signal is None:

            return None

        histogram = macd - signal

        self.value = MACDValue(

            macd=macd,

            signal=signal,

            histogram=histogram,

        )

        self.ready = True

        return self.value

    def latest(self):

        return self.value

    def is_ready(self):

        return self.ready

    def reset(self):

        self.__init__()

# ==========================================================
# COMPATIBILITY ALIAS
# ==========================================================
MACDIndicator = MACD
