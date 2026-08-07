"""
=====================================================

Professional VWAP

O(1)

=====================================================
"""

from __future__ import annotations


class VWAP:

    def __init__(self):

        self.price_volume = 0.0

        self.total_volume = 0.0

        self.value = None

    def update(

        self,

        high,

        low,

        close,

        volume,

    ):

        typical = (

            high

            + low

            + close

        ) / 3

        self.price_volume += (

            typical

            * volume

        )

        self.total_volume += volume

        if self.total_volume == 0:

            return None

        self.value = (

            self.price_volume

            /

            self.total_volume

        )

        return self.value

    def reset(self):

        self.price_volume = 0.0

        self.total_volume = 0.0

        self.value = None

    def latest(self):

        return self.value