"""
=========================================================
StockVersity Scanner Pro

Institutional Pattern Recognition Engine

Detects professional chart patterns for
Intraday, Swing and Positional Trading

Author : StockVersity
=========================================================
"""

from __future__ import annotations

import logging
import threading

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from enum import Enum

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import numpy as np
import pandas as pd

from core.indicator_engine import IndicatorEngine


# =========================================================
# PATTERN TYPE
# =========================================================

class PatternType(Enum):

    NONE = "NONE"

    VCP = "VCP"

    BULL_FLAG = "BULL_FLAG"

    FALLING_WEDGE = "FALLING_WEDGE"

    CUP_HANDLE = "CUP_HANDLE"

    FLAT_BASE = "FLAT_BASE"

    ASCENDING_TRIANGLE = "ASC_TRIANGLE"

    DOUBLE_BOTTOM = "DOUBLE_BOTTOM"

    ROUNDING_BOTTOM = "ROUNDING_BOTTOM"

    CONSOLIDATION = "CONSOLIDATION"


# =========================================================
# BREAKOUT TYPE
# =========================================================

class BreakoutType(Enum):

    NONE = "NONE"

    EARLY = "EARLY"

    CONFIRMED = "CONFIRMED"

    RETEST = "RETEST"

    FAILED = "FAILED"


# =========================================================
# PATTERN QUALITY
# =========================================================

class PatternQuality(Enum):

    POOR = "POOR"

    FAIR = "FAIR"

    GOOD = "GOOD"

    EXCELLENT = "EXCELLENT"

    INSTITUTIONAL = "INSTITUTIONAL"


# =========================================================
# PIVOT
# =========================================================

@dataclass
class Pivot:

    index: int

    price: float

    is_high: bool

    timestamp: Any = None


# =========================================================
# PATTERN RESULT
# =========================================================

@dataclass
class PatternResult:

    symbol: str = ""

    timeframe: str = ""

    pattern: PatternType = PatternType.NONE

    quality: PatternQuality = PatternQuality.POOR

    breakout: BreakoutType = BreakoutType.NONE

    confidence: float = 0.0

    score: float = 0.0

    breakout_price: float = 0.0

    stop_loss: float = 0.0

    target: float = 0.0

    risk_reward: float = 0.0

    volume_confirmation: bool = False

    trend_confirmation: bool = False

    volatility_contraction: bool = False

    institutional_volume: bool = False

    valid: bool = False

    message: str = ""

    metadata: Dict[str, Any] = field(

        default_factory=dict

    )


# =========================================================
# PATTERN ENGINE
# =========================================================

class PatternEngine:

    VERSION = "1.0.0"

    def __init__(

        self,

        indicators: Optional[
            IndicatorEngine
        ] = None,

    ):

        self.indicators = (

            indicators

            if indicators

            else IndicatorEngine()

        )

        self.logger = logging.getLogger(

            self.__class__.__name__

        )

        self.lock = threading.RLock()

        self.minimum_bars = 40

        self.maximum_bars = 250

        self.pivot_window = 5

        self.volume_factor = 1.5

        self.breakout_buffer = 0.0025

        self.max_base_depth = 0.30

        self.min_contraction = 0.08

        self.results: List[
            PatternResult
        ] = []

        self.statistics = {

            "patterns_checked": 0,

            "patterns_found": 0,

            "vcp": 0,

            "bull_flag": 0,

            "falling_wedge": 0,

            "cup_handle": 0,

            "flat_base": 0,

            "ascending_triangle": 0,

            "double_bottom": 0,

            "rounding_bottom": 0,

        }

        self.started = datetime.now()

        self.logger.info(

            "PatternEngine initialized."

        )

    # =====================================================
    # ANALYZE
    # =====================================================

    def analyze(

        self,

        symbol: str,

        data: pd.DataFrame,

        timeframe: str = "",

    ) -> List[PatternResult]:
        """
        Main pattern analysis entry.
        """

        self.statistics[

            "patterns_checked"

        ] += 1

        self.results = []

        if len(data) < self.minimum_bars:

            return self.results

        return self.results

    # =====================================================
    # ADD RESULT
    # =====================================================

    def add_result(

        self,

        result: PatternResult,

    ) -> None:

        self.results.append(

            result

        )

        self.statistics[

            "patterns_found"

        ] += 1

    # =====================================================
    # LAST PRICE
    # =====================================================

    @staticmethod
    def last_close(

        data: pd.DataFrame,

    ) -> float:

        return float(

            data["close"].iloc[-1]

        )

    # =====================================================
    # HIGH
    # =====================================================

    @staticmethod
    def highest(

        data: pd.DataFrame,

        length: int,

    ) -> float:

        return float(

            data["high"]

            .tail(length)

            .max()

        )

    # =====================================================
    # LOW
    # =====================================================

    @staticmethod
    def lowest(

        data: pd.DataFrame,

        length: int,

    ) -> float:

        return float(

            data["low"]

            .tail(length)

            .min()

        )

    # =====================================================
    # RANGE
    # =====================================================

    @staticmethod
    def price_range(

        data: pd.DataFrame,

        length: int,

    ) -> float:

        high = PatternEngine.highest(

            data,

            length,

        )

        low = PatternEngine.lowest(

            data,

            length,

        )

        return high - low
        # =====================================================
    # PIVOT HIGH
    # =====================================================

    def is_pivot_high(
        self,
        data: pd.DataFrame,
        index: int,
    ) -> bool:
        """
        Check whether a candle is a pivot high.
        """

        window = self.pivot_window

        if index < window:

            return False

        if index >= len(data) - window:

            return False

        value = data["high"].iloc[index]

        left = data["high"].iloc[
            index - window:index
        ]

        right = data["high"].iloc[
            index + 1:index + window + 1
        ]

        return (

            value > left.max()

            and value >= right.max()

        )

    # =====================================================
    # PIVOT LOW
    # =====================================================

    def is_pivot_low(
        self,
        data: pd.DataFrame,
        index: int,
    ) -> bool:
        """
        Check whether a candle is a pivot low.
        """

        window = self.pivot_window

        if index < window:

            return False

        if index >= len(data) - window:

            return False

        value = data["low"].iloc[index]

        left = data["low"].iloc[
            index - window:index
        ]

        right = data["low"].iloc[
            index + 1:index + window + 1
        ]

        return (

            value < left.min()

            and value <= right.min()

        )

    # =====================================================
    # PIVOTS
    # =====================================================

    def pivots(
        self,
        data: pd.DataFrame,
    ) -> List[Pivot]:
        """
        Extract pivot highs and lows.
        """

        pivots: List[Pivot] = []

        for i in range(

            self.pivot_window,

            len(data) - self.pivot_window,

        ):

            if self.is_pivot_high(

                data,

                i,

            ):

                pivots.append(

                    Pivot(

                        index=i,

                        price=float(

                            data["high"].iloc[i]

                        ),

                        is_high=True,

                        timestamp=data.index[i],

                    )

                )

                continue

            if self.is_pivot_low(

                data,

                i,

            ):

                pivots.append(

                    Pivot(

                        index=i,

                        price=float(

                            data["low"].iloc[i]

                        ),

                        is_high=False,

                        timestamp=data.index[i],

                    )

                )

        return pivots

    # =====================================================
    # PIVOT HIGHS
    # =====================================================

    def pivot_highs(
        self,
        data: pd.DataFrame,
    ) -> List[Pivot]:
        """
        Return only pivot highs.
        """

        return [

            pivot

            for pivot

            in self.pivots(data)

            if pivot.is_high

        ]

    # =====================================================
    # PIVOT LOWS
    # =====================================================

    def pivot_lows(
        self,
        data: pd.DataFrame,
    ) -> List[Pivot]:
        """
        Return only pivot lows.
        """

        return [

            pivot

            for pivot

            in self.pivots(data)

            if not pivot.is_high

        ]

    # =====================================================
    # LAST HIGH
    # =====================================================

    def last_pivot_high(
        self,
        data: pd.DataFrame,
    ) -> Optional[Pivot]:
        """
        Latest pivot high.
        """

        highs = self.pivot_highs(

            data

        )

        if not highs:

            return None

        return highs[-1]

    # =====================================================
    # LAST LOW
    # =====================================================

    def last_pivot_low(
        self,
        data: pd.DataFrame,
    ) -> Optional[Pivot]:
        """
        Latest pivot low.
        """

        lows = self.pivot_lows(

            data

        )

        if not lows:

            return None

        return lows[-1]

    # =====================================================
    # HIGHER HIGHS
    # =====================================================

    def higher_highs(
        self,
        data: pd.DataFrame,
        count: int = 3,
    ) -> bool:
        """
        Check higher-high sequence.
        """

        highs = self.pivot_highs(

            data

        )

        if len(highs) < count:

            return False

        values = [

            pivot.price

            for pivot

            in highs[-count:]

        ]

        return all(

            values[i]

            > values[i - 1]

            for i in range(

                1,

                len(values),

            )

        )

    # =====================================================
    # LOWER LOWS
    # =====================================================

    def lower_lows(
        self,
        data: pd.DataFrame,
        count: int = 3,
    ) -> bool:
        """
        Check lower-low sequence.
        """

        lows = self.pivot_lows(

            data

        )

        if len(lows) < count:

            return False

        values = [

            pivot.price

            for pivot

            in lows[-count:]

        ]

        return all(

            values[i]

            < values[i - 1]

            for i in range(

                1,

                len(values),

            )

        )

    # =====================================================
    # HIGHER LOWS
    # =====================================================

    def higher_lows(
        self,
        data: pd.DataFrame,
        count: int = 3,
    ) -> bool:
        """
        Check higher-low sequence.
        """

        lows = self.pivot_lows(

            data

        )

        if len(lows) < count:

            return False

        values = [

            pivot.price

            for pivot

            in lows[-count:]

        ]

        return all(

            values[i]

            > values[i - 1]

            for i in range(

                1,

                len(values),

            )

        )

    # =====================================================
    # LOWER HIGHS
    # =====================================================

    def lower_highs(
        self,
        data: pd.DataFrame,
        count: int = 3,
    ) -> bool:
        """
        Check lower-high sequence.
        """

        highs = self.pivot_highs(

            data

        )

        if len(highs) < count:

            return False

        values = [

            pivot.price

            for pivot

            in highs[-count:]

        ]

        return all(

            values[i]

            < values[i - 1]

            for i in range(

                1,

                len(values),

            )

        )

    # =====================================================
    # TREND STRUCTURE
    # =====================================================

    def trend_structure(
        self,
        data: pd.DataFrame,
    ) -> str:
        """
        Determine price structure from pivots.
        """

        if (

            self.higher_highs(data)

            and self.higher_lows(data)

        ):

            return "UPTREND"

        if (

            self.lower_highs(data)

            and self.lower_lows(data)

        ):

            return "DOWNTREND"

        return "SIDEWAYS"
        # =====================================================
    # LINE SLOPE
    # =====================================================

    @staticmethod
    def slope(
        p1: Pivot,
        p2: Pivot,
    ) -> float:
        """
        Calculate slope between two pivots.
        """

        dx = p2.index - p1.index

        if dx == 0:

            return 0.0

        return (

            p2.price - p1.price

        ) / dx

    # =====================================================
    # LINE VALUE
    # =====================================================

    @staticmethod
    def line_value(
        pivot: Pivot,
        slope: float,
        index: int,
    ) -> float:
        """
        Trendline value at index.
        """

        return (

            pivot.price

            + slope

            * (

                index

                - pivot.index

            )

        )

    # =====================================================
    # RESISTANCE LINE
    # =====================================================

    def resistance_line(
        self,
        data: pd.DataFrame,
    ) -> Optional[Tuple[Pivot, Pivot, float]]:
        """
        Build descending resistance line.
        """

        highs = self.pivot_highs(

            data

        )

        if len(highs) < 2:

            return None

        p1 = highs[-2]

        p2 = highs[-1]

        return (

            p1,

            p2,

            self.slope(

                p1,

                p2,

            ),

        )

    # =====================================================
    # SUPPORT LINE
    # =====================================================

    def support_line(
        self,
        data: pd.DataFrame,
    ) -> Optional[Tuple[Pivot, Pivot, float]]:
        """
        Build ascending support line.
        """

        lows = self.pivot_lows(

            data

        )

        if len(lows) < 2:

            return None

        p1 = lows[-2]

        p2 = lows[-1]

        return (

            p1,

            p2,

            self.slope(

                p1,

                p2,

            ),

        )

    # =====================================================
    # RESISTANCE SLOPE
    # =====================================================

    def resistance_slope(
        self,
        data: pd.DataFrame,
    ) -> float:
        """
        Latest resistance slope.
        """

        line = self.resistance_line(

            data

        )

        if line is None:

            return 0.0

        return line[2]

    # =====================================================
    # SUPPORT SLOPE
    # =====================================================

    def support_slope(
        self,
        data: pd.DataFrame,
    ) -> float:
        """
        Latest support slope.
        """

        line = self.support_line(

            data

        )

        if line is None:

            return 0.0

        return line[2]

    # =====================================================
    # PARALLEL CHANNEL
    # =====================================================

    def parallel_channel(
        self,
        data: pd.DataFrame,
        tolerance: float = 0.10,
    ) -> bool:
        """
        Detect parallel trend channel.
        """

        rs = self.resistance_slope(

            data

        )

        ss = self.support_slope(

            data

        )

        if rs == 0:

            return False

        return (

            abs(

                rs - ss

            )

            / abs(rs)

        ) <= tolerance

    # =====================================================
    # CONVERGING LINES
    # =====================================================

    def converging_lines(
        self,
        data: pd.DataFrame,
    ) -> bool:
        """
        Detect converging support and resistance.
        """

        rs = self.resistance_slope(

            data

        )

        ss = self.support_slope(

            data

        )

        return (

            rs < 0

            and ss > 0

        )

    # =====================================================
    # DIVERGING LINES
    # =====================================================

    def diverging_lines(
        self,
        data: pd.DataFrame,
    ) -> bool:
        """
        Detect expanding price structure.
        """

        rs = self.resistance_slope(

            data

        )

        ss = self.support_slope(

            data

        )

        return (

            rs > 0

            and ss < 0

        )

    # =====================================================
    # BREAK ABOVE RESISTANCE
    # =====================================================

    def breakout_resistance(
        self,
        data: pd.DataFrame,
    ) -> bool:
        """
        Check breakout above resistance line.
        """

        line = self.resistance_line(

            data

        )

        if line is None:

            return False

        p1, _, slope = line

        resistance = self.line_value(

            p1,

            slope,

            len(data) - 1,

        )

        close = self.last_close(

            data

        )

        return (

            close

            > resistance

            * (

                1

                + self.breakout_buffer

            )

        )

    # =====================================================
    # BREAK BELOW SUPPORT
    # =====================================================

    def breakdown_support(
        self,
        data: pd.DataFrame,
    ) -> bool:
        """
        Check breakdown below support line.
        """

        line = self.support_line(

            data

        )

        if line is None:

            return False

        p1, _, slope = line

        support = self.line_value(

            p1,

            slope,

            len(data) - 1,

        )

        close = self.last_close(

            data

        )

        return (

            close

            < support

            * (

                1

                - self.breakout_buffer

            )

        )

    # =====================================================
    # CHANNEL WIDTH
    # =====================================================

    def channel_width(
        self,
        data: pd.DataFrame,
    ) -> float:
        """
        Current distance between trendlines.
        """

        resistance = self.resistance_line(

            data

        )

        support = self.support_line(

            data

        )

        if (

            resistance is None

            or support is None

        ):

            return 0.0

        rp1, _, rs = resistance

        sp1, _, ss = support

        idx = len(data) - 1

        top = self.line_value(

            rp1,

            rs,

            idx,

        )

        bottom = self.line_value(

            sp1,

            ss,

            idx,

        )

        return max(

            top - bottom,

            0.0,

        )

    # =====================================================
    # TRENDLINE SUMMARY
    # =====================================================

    def trendline_summary(
        self,
        data: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        Trendline diagnostics.
        """

        return {

            "support_slope": self.support_slope(

                data

            ),

            "resistance_slope": self.resistance_slope(

                data

            ),

            "parallel": self.parallel_channel(

                data

            ),

            "converging": self.converging_lines(

                data

            ),

            "diverging": self.diverging_lines(

                data

            ),

            "breakout": self.breakout_resistance(

                data

            ),

            "breakdown": self.breakdown_support(

                data

            ),

            "channel_width": self.channel_width(

                data

            ),

        }
        # =====================================================
    # ATR
    # =====================================================

    def atr(
        self,
        data: pd.DataFrame,
        period: int = 14,
    ) -> float:
        """
        Current ATR value.
        """

        atr = self.indicators.atr(

            data,

            period,

        )

        if isinstance(

            atr,

            pd.Series,

        ):

            return float(

                atr.iloc[-1]

            )

        return float(

            atr

        )

    # =====================================================
    # PRICE RANGE %
    # =====================================================

    def range_percent(
        self,
        data: pd.DataFrame,
        bars: int = 20,
    ) -> float:
        """
        Price range percentage.
        """

        high = self.highest(

            data,

            bars,

        )

        low = self.lowest(

            data,

            bars,

        )

        if low <= 0:

            return 0.0

        return (

            (high - low)

            / low

        ) * 100

    # =====================================================
    # TIGHT RANGE
    # =====================================================

    def tight_range(
        self,
        data: pd.DataFrame,
        bars: int = 20,
        maximum: float = 8.0,
    ) -> bool:
        """
        Detect tight price range.
        """

        return (

            self.range_percent(

                data,

                bars,

            )

            <= maximum

        )

    # =====================================================
    # ATR CONTRACTION
    # =====================================================

    def atr_contraction(
        self,
        data: pd.DataFrame,
        short: int = 10,
        long: int = 30,
    ) -> bool:
        """
        Detect shrinking volatility.
        """

        if len(data) < long + 5:

            return False

        atr_short = self.indicators.atr(

            data,

            short,

        )

        atr_long = self.indicators.atr(

            data,

            long,

        )

        if isinstance(

            atr_short,

            pd.Series,

        ):

            atr_short = atr_short.iloc[-1]

        if isinstance(

            atr_long,

            pd.Series,

        ):

            atr_long = atr_long.iloc[-1]

        return (

            atr_short

            < atr_long

        )

    # =====================================================
    # VOLATILITY CONTRACTION
    # =====================================================

    def volatility_contraction(
        self,
        data: pd.DataFrame,
        bars: int = 30,
    ) -> bool:
        """
        Detect volatility contraction
        using rolling standard deviation.
        """

        if len(data) < bars:

            return False

        returns = data[

            "close"

        ].pct_change()

        current = (

            returns.tail(

                bars // 2

            ).std()

        )

        previous = (

            returns.head(

                len(returns)

                - bars // 2

            ).tail(

                bars // 2

            ).std()

        )

        if pd.isna(

            current

        ) or pd.isna(

            previous

        ):

            return False

        return (

            current

            < previous

        )

    # =====================================================
    # NR7
    # =====================================================

    def nr7(
        self,
        data: pd.DataFrame,
    ) -> bool:
        """
        Narrowest range of last 7 bars.
        """

        if len(data) < 7:

            return False

        ranges = (

            data["high"]

            - data["low"]

        ).tail(

            7

        )

        return (

            ranges.iloc[-1]

            == ranges.min()

        )

    # =====================================================
    # NR4
    # =====================================================

    def nr4(
        self,
        data: pd.DataFrame,
    ) -> bool:
        """
        Narrowest range of last 4 bars.
        """

        if len(data) < 4:

            return False

        ranges = (

            data["high"]

            - data["low"]

        ).tail(

            4

        )

        return (

            ranges.iloc[-1]

            == ranges.min()

        )

    # =====================================================
    # BASE DEPTH
    # =====================================================

    def base_depth(
        self,
        data: pd.DataFrame,
        bars: int = 30,
    ) -> float:
        """
        Calculate correction depth.
        """

        high = self.highest(

            data,

            bars,

        )

        low = self.lowest(

            data,

            bars,

        )

        if high <= 0:

            return 0.0

        return (

            (high - low)

            / high

        )

    # =====================================================
    # VALID BASE
    # =====================================================

    def valid_base(
        self,
        data: pd.DataFrame,
        bars: int = 30,
    ) -> bool:
        """
        Determine whether the base is
        acceptable.
        """

        return (

            self.base_depth(

                data,

                bars,

            )

            <= self.max_base_depth

        )

    # =====================================================
    # COMPRESSION SCORE
    # =====================================================

    def compression_score(
        self,
        data: pd.DataFrame,
    ) -> float:
        """
        Compression score (0–100).
        """

        score = 0.0

        if self.tight_range(

            data

        ):

            score += 30

        if self.atr_contraction(

            data

        ):

            score += 30

        if self.volatility_contraction(

            data

        ):

            score += 20

        if self.nr7(

            data

        ):

            score += 10

        if self.nr4(

            data

        ):

            score += 10

        return min(

            score,

            100.0,

        )

    # =====================================================
    # CONSOLIDATION
    # =====================================================

    def consolidation(
        self,
        data: pd.DataFrame,
    ) -> bool:
        """
        Institutional consolidation.
        """

        checks = (

            self.valid_base(

                data

            ),

            self.tight_range(

                data

            ),

            self.atr_contraction(

                data

            ),

            self.volatility_contraction(

                data

            ),

        )

        return sum(

            checks

        ) >= 3

    # =====================================================
    # CONSOLIDATION RESULT
    # =====================================================

    def consolidation_result(
        self,
        symbol: str,
        timeframe: str,
        data: pd.DataFrame,
    ) -> Optional[
        PatternResult
    ]:
        """
        Build PatternResult for a
        consolidation pattern.
        """

        if not self.consolidation(

            data

        ):

            return None

        result = PatternResult(

            symbol=symbol,

            timeframe=timeframe,

            pattern=PatternType.CONSOLIDATION,

            confidence=self.compression_score(

                data

            ),

            score=self.compression_score(

                data

            ),

            volatility_contraction=True,

            valid=True,

            message="Institutional consolidation detected.",

        )

        result.quality = (

            PatternQuality.EXCELLENT

            if result.score >= 80

            else PatternQuality.GOOD

        )

        return result
        # =====================================================
    # VCP CONTRACTION LEGS
    # =====================================================

    def vcp_contraction_legs(
        self,
        data: pd.DataFrame,
    ) -> List[float]:
        """
        Calculate contraction percentages
        between recent pivot highs/lows.
        """

        highs = self.pivot_highs(data)
        lows = self.pivot_lows(data)

        if len(highs) < 4 or len(lows) < 4:
            return []

        highs = highs[-4:]
        lows = lows[-4:]

        contractions = []

        for high, low in zip(highs, lows):

            if high.price <= 0:
                continue

            contraction = (
                (high.price - low.price)
                / high.price
            ) * 100

            contractions.append(contraction)

        return contractions

    # =====================================================
    # PROGRESSIVE CONTRACTION
    # =====================================================

    def progressive_contraction(
        self,
        contractions: List[float],
    ) -> bool:
        """
        Each contraction should become
        smaller than the previous one.
        """

        if len(contractions) < 3:
            return False

        for i in range(1, len(contractions)):

            if contractions[i] >= contractions[i - 1]:
                return False

        return True

    # =====================================================
    # VOLUME DRY-UP
    # =====================================================

    def volume_dry_up(
        self,
        data: pd.DataFrame,
        period: int = 20,
    ) -> bool:
        """
        Volume should decrease into
        the pivot.
        """

        if len(data) < period * 2:
            return False

        previous = data["volume"].iloc[-period * 2:-period].mean()

        current = data["volume"].tail(period).mean()

        return current < previous * 0.75

    # =====================================================
    # TIGHT PIVOTS
    # =====================================================

    def tight_pivots(
        self,
        data: pd.DataFrame,
    ) -> bool:
        """
        Recent pivot highs should cluster
        tightly together.
        """

        highs = self.pivot_highs(data)

        if len(highs) < 3:
            return False

        prices = [
            p.price
            for p in highs[-3:]
        ]

        spread = (
            max(prices) - min(prices)
        ) / max(prices)

        return spread <= 0.03

    # =====================================================
    # BREAKOUT PIVOT
    # =====================================================

    def breakout_pivot(
        self,
        data: pd.DataFrame,
    ) -> float:
        """
        Highest recent pivot high.
        """

        highs = self.pivot_highs(data)

        if not highs:
            return 0.0

        return max(
            p.price
            for p in highs[-5:]
        )

    # =====================================================
    # VCP BREAKOUT
    # =====================================================

    def vcp_breakout(
        self,
        data: pd.DataFrame,
    ) -> bool:
        """
        Price breaks above pivot.
        """

        pivot = self.breakout_pivot(data)

        if pivot == 0:
            return False

        close = self.last_close(data)

        return close > (
            pivot * (1 + self.breakout_buffer)
        )

    # =====================================================
    # VCP SCORE
    # =====================================================

    def vcp_score(
        self,
        data: pd.DataFrame,
    ) -> float:
        """
        Minervini-inspired VCP score.
        """

        score = 0.0

        contractions = self.vcp_contraction_legs(data)

        if self.progressive_contraction(contractions):
            score += 25

        if self.volume_dry_up(data):
            score += 20

        if self.tight_pivots(data):
            score += 15

        if self.consolidation(data):
            score += 20

        if self.vcp_breakout(data):
            score += 20

        return min(score, 100)

    # =====================================================
    # VCP QUALITY
    # =====================================================

    def vcp_quality(
        self,
        score: float,
    ) -> PatternQuality:
        """
        Convert score into quality.
        """

        if score >= 90:
            return PatternQuality.INSTITUTIONAL

        if score >= 75:
            return PatternQuality.EXCELLENT

        if score >= 60:
            return PatternQuality.GOOD

        if score >= 40:
            return PatternQuality.FAIR

        return PatternQuality.POOR

    # =====================================================
    # DETECT VCP
    # =====================================================

    def detect_vcp(
        self,
        symbol: str,
        timeframe: str,
        data: pd.DataFrame,
    ) -> Optional[PatternResult]:
        """
        Detect Volatility Contraction Pattern.
        """

        contractions = self.vcp_contraction_legs(data)

        if len(contractions) < 3:
            return None

        if not self.progressive_contraction(contractions):
            return None

        score = self.vcp_score(data)

        result = PatternResult()

        result.symbol = symbol
        result.timeframe = timeframe
        result.pattern = PatternType.VCP

        result.score = score
        result.confidence = score

        result.quality = self.vcp_quality(score)

        result.breakout = (
            BreakoutType.CONFIRMED
            if self.vcp_breakout(data)
            else BreakoutType.NONE
        )

        result.breakout_price = self.breakout_pivot(data)

        lows = self.pivot_lows(data)

        if lows:
            result.stop_loss = lows[-1].price

        result.target = (
            result.breakout_price * 1.20
        )

        if result.stop_loss > 0:

            risk = (
                result.breakout_price
                - result.stop_loss
            )

            reward = (
                result.target
                - result.breakout_price
            )

            if risk > 0:
                result.risk_reward = (
                    reward / risk
                )

        result.volume_confirmation = (
            self.volume_dry_up(data)
        )

        result.volatility_contraction = True

        result.valid = score >= 60

        result.message = (
            "Volatility Contraction Pattern detected."
        )

        return result
        # =====================================================
    # WEDGE RESISTANCE
    # =====================================================

    def wedge_resistance(self, data: pd.DataFrame) -> float:
        """
        Latest descending resistance slope.
        """

        return self.resistance_slope(data)

    # =====================================================
    # WEDGE SUPPORT
    # =====================================================

    def wedge_support(self, data: pd.DataFrame) -> float:
        """
        Latest descending support slope.
        """

        return self.support_slope(data)

    # =====================================================
    # DESCENDING TRENDLINES
    # =====================================================

    def descending_trendlines(
        self,
        data: pd.DataFrame,
    ) -> bool:
        """
        Both trendlines should slope down.
        """

        rs = self.wedge_resistance(data)
        ss = self.wedge_support(data)

        return (
            rs < 0
            and ss < 0
        )

    # =====================================================
    # WEDGE CONVERGENCE
    # =====================================================

    def wedge_convergence(
        self,
        data: pd.DataFrame,
    ) -> bool:
        """
        Support should fall slower than
        resistance, creating convergence.
        """

        rs = abs(self.wedge_resistance(data))
        ss = abs(self.wedge_support(data))

        if rs == 0 or ss == 0:
            return False

        return ss < rs

    # =====================================================
    # WEDGE VOLUME
    # =====================================================

    def wedge_volume(
        self,
        data: pd.DataFrame,
        period: int = 20,
    ) -> bool:
        """
        Volume contracts during wedge.
        """

        if len(data) < period * 2:
            return False

        old = data["volume"].iloc[-period * 2:-period].mean()
        recent = data["volume"].tail(period).mean()

        return recent < old * 0.80

    # =====================================================
    # WEDGE BREAKOUT
    # =====================================================

    def wedge_breakout(
        self,
        data: pd.DataFrame,
    ) -> bool:
        """
        Bullish breakout above
        descending resistance.
        """

        return self.breakout_resistance(data)

    # =====================================================
    # WEDGE HEIGHT
    # =====================================================

    def wedge_height(
        self,
        data: pd.DataFrame,
    ) -> float:
        """
        Initial wedge height.
        """

        highs = self.pivot_highs(data)
        lows = self.pivot_lows(data)

        if len(highs) < 2 or len(lows) < 2:
            return 0.0

        return (
            highs[-2].price
            - lows[-2].price
        )

    # =====================================================
    # WEDGE TARGET
    # =====================================================

    def wedge_target(
        self,
        data: pd.DataFrame,
    ) -> float:
        """
        Price target after breakout.
        """

        return (
            self.last_close(data)
            + self.wedge_height(data)
        )

    # =====================================================
    # WEDGE SCORE
    # =====================================================

    def wedge_score(
        self,
        data: pd.DataFrame,
    ) -> float:
        """
        Institutional Falling Wedge score.
        """

        score = 0.0

        if self.descending_trendlines(data):
            score += 20

        if self.wedge_convergence(data):
            score += 20

        if self.wedge_volume(data):
            score += 15

        if self.consolidation(data):
            score += 15

        if self.breakout_resistance(data):
            score += 20

        if self.higher_lows(data, 2):
            score += 10

        return min(score, 100)

    # =====================================================
    # DETECT FALLING WEDGE
    # =====================================================

    def detect_falling_wedge(
        self,
        symbol: str,
        timeframe: str,
        data: pd.DataFrame,
    ) -> Optional[PatternResult]:
        """
        Detect Falling Wedge.
        """

        if not self.descending_trendlines(data):
            return None

        if not self.wedge_convergence(data):
            return None

        score = self.wedge_score(data)

        result = PatternResult()

        result.symbol = symbol
        result.timeframe = timeframe
        result.pattern = PatternType.FALLING_WEDGE

        result.score = score
        result.confidence = score

        result.quality = self.vcp_quality(score)

        result.breakout = (
            BreakoutType.CONFIRMED
            if self.wedge_breakout(data)
            else BreakoutType.NONE
        )

        result.breakout_price = self.last_close(data)

        lows = self.pivot_lows(data)

        if lows:
            result.stop_loss = lows[-1].price

        result.target = self.wedge_target(data)

        if result.stop_loss > 0:

            risk = (
                result.breakout_price
                - result.stop_loss
            )

            reward = (
                result.target
                - result.breakout_price
            )

            if risk > 0:
                result.risk_reward = reward / risk

        result.volume_confirmation = (
            self.wedge_volume(data)
        )

        result.volatility_contraction = (
            self.volatility_contraction(data)
        )

        result.valid = score >= 60

        result.message = (
            "Bullish Falling Wedge detected."
        )

        return result
        # =====================================================
    # FLAGPOLE
    # =====================================================

    def flagpole_strength(
        self,
        data: pd.DataFrame,
        bars: int = 20,
    ) -> float:
        """
        Measure the impulsive move before
        the flag.
        """

        if len(data) < bars:
            return 0.0

        start = float(data["close"].iloc[-bars])
        end = self.last_close(data)

        if start <= 0:
            return 0.0

        return (
            (end - start)
            / start
        ) * 100

    # =====================================================
    # STRONG FLAGPOLE
    # =====================================================

    def strong_flagpole(
        self,
        data: pd.DataFrame,
    ) -> bool:
        """
        Minimum impulsive move.
        """

        return self.flagpole_strength(data) >= 10.0

    # =====================================================
    # FLAG DEPTH
    # =====================================================

    def flag_depth(
        self,
        data: pd.DataFrame,
        bars: int = 15,
    ) -> float:
        """
        Pullback percentage from the
        recent swing high.
        """

        if len(data) < bars:
            return 100.0

        high = self.highest(data, bars)
        low = self.lowest(data, bars)

        if high <= 0:
            return 100.0

        return (
            (high - low)
            / high
        ) * 100

    # =====================================================
    # VALID FLAG DEPTH
    # =====================================================

    def valid_flag_depth(
        self,
        data: pd.DataFrame,
    ) -> bool:
        """
        Flag should remain shallow.
        """

        depth = self.flag_depth(data)

        return (
            depth <= 25
        )

    # =====================================================
    # FLAG CHANNEL
    # =====================================================

    def flag_channel(
        self,
        data: pd.DataFrame,
    ) -> bool:
        """
        Flag should form inside a
        parallel channel.
        """

        return self.parallel_channel(data)

    # =====================================================
    # FLAG VOLUME
    # =====================================================

    def flag_volume(
        self,
        data: pd.DataFrame,
        period: int = 15,
    ) -> bool:
        """
        Volume should decline during
        the flag.
        """

        if len(data) < period * 2:
            return False

        previous = (
            data["volume"]
            .iloc[-period * 2:-period]
            .mean()
        )

        current = (
            data["volume"]
            .tail(period)
            .mean()
        )

        return current < previous * 0.80

    # =====================================================
    # FLAG BREAKOUT
    # =====================================================

    def bull_flag_breakout(
        self,
        data: pd.DataFrame,
    ) -> bool:
        """
        Breakout above upper channel.
        """

        return self.breakout_resistance(data)

    # =====================================================
    # FLAG TARGET
    # =====================================================

    def bull_flag_target(
        self,
        data: pd.DataFrame,
    ) -> float:
        """
        Measured move target.
        """

        move = self.flagpole_strength(data)

        return (
            self.last_close(data)
            * (1 + move / 100)
        )

    # =====================================================
    # FLAG SCORE
    # =====================================================

    def bull_flag_score(
        self,
        data: pd.DataFrame,
    ) -> float:
        """
        Institutional Bull Flag score.
        """

        score = 0.0

        if self.strong_flagpole(data):
            score += 25

        if self.flag_channel(data):
            score += 20

        if self.valid_flag_depth(data):
            score += 15

        if self.flag_volume(data):
            score += 15

        if self.consolidation(data):
            score += 10

        if self.bull_flag_breakout(data):
            score += 15

        return min(score, 100)

    # =====================================================
    # DETECT BULL FLAG
    # =====================================================

    def detect_bull_flag(
        self,
        symbol: str,
        timeframe: str,
        data: pd.DataFrame,
    ) -> Optional[PatternResult]:
        """
        Detect Bull Flag pattern.
        """

        if not self.strong_flagpole(data):
            return None

        if not self.flag_channel(data):
            return None

        score = self.bull_flag_score(data)

        result = PatternResult()

        result.symbol = symbol
        result.timeframe = timeframe

        result.pattern = PatternType.BULL_FLAG

        result.score = score
        result.confidence = score

        result.quality = self.vcp_quality(score)

        result.breakout = (
            BreakoutType.CONFIRMED
            if self.bull_flag_breakout(data)
            else BreakoutType.NONE
        )

        result.breakout_price = self.last_close(data)

        lows = self.pivot_lows(data)

        if lows:
            result.stop_loss = lows[-1].price

        result.target = self.bull_flag_target(data)

        if result.stop_loss > 0:

            risk = (
                result.breakout_price
                - result.stop_loss
            )

            reward = (
                result.target
                - result.breakout_price
            )

            if risk > 0:
                result.risk_reward = (
                    reward / risk
                )

        result.volume_confirmation = (
            self.flag_volume(data)
        )

        result.trend_confirmation = (
            self.higher_highs(data, 2)
            and self.higher_lows(data, 2)
        )

        result.volatility_contraction = (
            self.volatility_contraction(data)
        )

        result.valid = score >= 60

        result.message = (
            "Bull Flag pattern detected."
        )

        return result
        # =====================================================
    # CUP DEPTH
    # =====================================================

    def cup_depth(
        self,
        data: pd.DataFrame,
        bars: int = 60,
    ) -> float:
        """
        Calculate cup correction depth.
        """

        if len(data) < bars:
            return 100.0

        high = self.highest(data, bars)
        low = self.lowest(data, bars)

        if high <= 0:
            return 100.0

        return (
            (high - low)
            / high
        ) * 100

    # =====================================================
    # ROUNDED CUP
    # =====================================================

    def rounded_cup(
        self,
        data: pd.DataFrame,
        bars: int = 60,
    ) -> bool:
        """
        Detect rounded bottom.
        """

        if len(data) < bars:
            return False

        closes = (
            data["close"]
            .tail(bars)
            .reset_index(drop=True)
        )

        minimum = closes.idxmin()

        if minimum < bars * 0.25:
            return False

        if minimum > bars * 0.75:
            return False

        left = closes.iloc[:minimum].mean()
        right = closes.iloc[minimum:].mean()

        if left <= 0:
            return False

        difference = abs(
            left - right
        ) / left

        return difference <= 0.10

    # =====================================================
    # HANDLE DEPTH
    # =====================================================

    def handle_depth(
        self,
        data: pd.DataFrame,
        bars: int = 15,
    ) -> float:
        """
        Handle pullback percentage.
        """

        if len(data) < bars:
            return 100.0

        high = self.highest(data, bars)
        low = self.lowest(data, bars)

        if high <= 0:
            return 100.0

        return (
            (high - low)
            / high
        ) * 100

    # =====================================================
    # VALID HANDLE
    # =====================================================

    def valid_handle(
        self,
        data: pd.DataFrame,
    ) -> bool:
        """
        Handle should remain shallow.
        """

        depth = self.handle_depth(data)

        return depth <= 15

    # =====================================================
    # HANDLE VOLUME
    # =====================================================

    def handle_volume(
        self,
        data: pd.DataFrame,
        period: int = 15,
    ) -> bool:
        """
        Volume should contract during handle.
        """

        if len(data) < period * 2:
            return False

        previous = (
            data["volume"]
            .iloc[-period * 2:-period]
            .mean()
        )

        current = (
            data["volume"]
            .tail(period)
            .mean()
        )

        return current < previous * 0.80

    # =====================================================
    # CUP BREAKOUT
    # =====================================================

    def cup_breakout(
        self,
        data: pd.DataFrame,
    ) -> bool:
        """
        Breakout above cup resistance.
        """

        resistance = self.highest(
            data,
            60,
        )

        return (
            self.last_close(data)
            >
            resistance
            * (1 + self.breakout_buffer)
        )

    # =====================================================
    # CUP TARGET
    # =====================================================

    def cup_target(
        self,
        data: pd.DataFrame,
    ) -> float:
        """
        Measured move target.
        """

        high = self.highest(data, 60)
        low = self.lowest(data, 60)

        return (
            self.last_close(data)
            + (high - low)
        )

    # =====================================================
    # CUP SCORE
    # =====================================================

    def cup_score(
        self,
        data: pd.DataFrame,
    ) -> float:

        score = 0.0

        if self.rounded_cup(data):
            score += 25

        if self.valid_handle(data):
            score += 20

        if self.handle_volume(data):
            score += 15

        if self.consolidation(data):
            score += 15

        if self.cup_breakout(data):
            score += 20

        depth = self.cup_depth(data)

        if 12 <= depth <= 35:
            score += 5

        return min(score, 100)

    # =====================================================
    # DETECT CUP & HANDLE
    # =====================================================

    def detect_cup_handle(
        self,
        symbol: str,
        timeframe: str,
        data: pd.DataFrame,
    ) -> Optional[PatternResult]:

        if not self.rounded_cup(data):
            return None

        if not self.valid_handle(data):
            return None

        score = self.cup_score(data)

        result = PatternResult()

        result.symbol = symbol
        result.timeframe = timeframe

        result.pattern = PatternType.CUP_HANDLE

        result.score = score
        result.confidence = score

        result.quality = self.vcp_quality(score)

        result.breakout = (
            BreakoutType.CONFIRMED
            if self.cup_breakout(data)
            else BreakoutType.NONE
        )

        result.breakout_price = self.last_close(data)

        lows = self.pivot_lows(data)

        if lows:
            result.stop_loss = lows[-1].price

        result.target = self.cup_target(data)

        if result.stop_loss > 0:

            risk = (
                result.breakout_price
                - result.stop_loss
            )

            reward = (
                result.target
                - result.breakout_price
            )

            if risk > 0:
                result.risk_reward = (
                    reward / risk
                )

        result.volume_confirmation = (
            self.handle_volume(data)
        )

        result.trend_confirmation = (
            self.higher_highs(data, 2)
            and self.higher_lows(data, 2)
        )

        result.volatility_contraction = (
            self.volatility_contraction(data)
        )

        result.valid = score >= 60

        result.message = (
            "Cup & Handle pattern detected."
        )

        return result
        # =====================================================
    # FLAT BASE
    # =====================================================

    def detect_flat_base(
        self,
        symbol: str,
        timeframe: str,
        data: pd.DataFrame,
    ) -> Optional[PatternResult]:
        """
        Detect Flat Base.
        """

        depth = self.base_depth(data, 30)

        if depth > 0.15:
            return None

        score = 0.0

        if self.tight_range(data, 30, 10):
            score += 30

        if self.volume_dry_up(data):
            score += 20

        if self.breakout_resistance(data):
            score += 30

        if self.volatility_contraction(data):
            score += 20

        result = PatternResult()

        result.symbol = symbol
        result.timeframe = timeframe
        result.pattern = PatternType.FLAT_BASE
        result.score = score
        result.confidence = score
        result.quality = self.vcp_quality(score)

        result.breakout = (
            BreakoutType.CONFIRMED
            if self.breakout_resistance(data)
            else BreakoutType.NONE
        )

        result.breakout_price = self.last_close(data)

        lows = self.pivot_lows(data)

        if lows:
            result.stop_loss = lows[-1].price

        result.target = (
            result.breakout_price
            * 1.15
        )

        result.volume_confirmation = self.volume_dry_up(data)
        result.volatility_contraction = self.volatility_contraction(data)
        result.valid = score >= 60
        result.message = "Flat Base detected."

        return result

    # =====================================================
    # ASCENDING TRIANGLE
    # =====================================================

    def detect_ascending_triangle(
        self,
        symbol: str,
        timeframe: str,
        data: pd.DataFrame,
    ) -> Optional[PatternResult]:
        """
        Detect Ascending Triangle.
        """

        highs = self.pivot_highs(data)
        lows = self.pivot_lows(data)

        if len(highs) < 3 or len(lows) < 3:
            return None

        resistance = [
            p.price
            for p in highs[-3:]
        ]

        spread = (
            max(resistance)
            - min(resistance)
        ) / max(resistance)

        if spread > 0.02:
            return None

        if not self.higher_lows(data):
            return None

        score = 0.0

        score += 30

        if self.breakout_resistance(data):
            score += 30

        if self.volume_dry_up(data):
            score += 20

        if self.volatility_contraction(data):
            score += 20

        result = PatternResult()

        result.symbol = symbol
        result.timeframe = timeframe
        result.pattern = PatternType.ASCENDING_TRIANGLE
        result.score = score
        result.confidence = score
        result.quality = self.vcp_quality(score)

        result.breakout = (
            BreakoutType.CONFIRMED
            if self.breakout_resistance(data)
            else BreakoutType.NONE
        )

        result.breakout_price = self.last_close(data)

        if lows:
            result.stop_loss = lows[-1].price

        height = (
            max(resistance)
            - lows[-1].price
        )

        result.target = (
            result.breakout_price
            + height
        )

        result.volume_confirmation = self.volume_dry_up(data)
        result.valid = score >= 60
        result.message = "Ascending Triangle detected."

        return result

    # =====================================================
    # DOUBLE BOTTOM
    # =====================================================

    def detect_double_bottom(
        self,
        symbol: str,
        timeframe: str,
        data: pd.DataFrame,
    ) -> Optional[PatternResult]:
        """
        Detect Double Bottom.
        """

        lows = self.pivot_lows(data)

        if len(lows) < 2:
            return None

        first = lows[-2].price
        second = lows[-1].price

        difference = abs(
            first - second
        ) / first

        if difference > 0.03:
            return None

        score = 0.0

        score += 40

        if self.breakout_resistance(data):
            score += 30

        if self.volume_dry_up(data):
            score += 15

        if self.higher_highs(data, 2):
            score += 15

        result = PatternResult()

        result.symbol = symbol
        result.timeframe = timeframe
        result.pattern = PatternType.DOUBLE_BOTTOM
        result.score = score
        result.confidence = score
        result.quality = self.vcp_quality(score)

        result.breakout = (
            BreakoutType.CONFIRMED
            if self.breakout_resistance(data)
            else BreakoutType.NONE
        )

        result.breakout_price = self.last_close(data)
        result.stop_loss = second

        neckline = self.highest(data, 40)

        result.target = (
            neckline
            + (neckline - second)
        )

        result.volume_confirmation = self.volume_dry_up(data)
        result.valid = score >= 60
        result.message = "Double Bottom detected."

        return result

    # =====================================================
    # ROUNDING BOTTOM
    # =====================================================

    def detect_rounding_bottom(
        self,
        symbol: str,
        timeframe: str,
        data: pd.DataFrame,
    ) -> Optional[PatternResult]:
        """
        Detect Rounding Bottom.
        """

        if not self.rounded_cup(data):
            return None

        score = 50.0

        if self.volume_dry_up(data):
            score += 20

        if self.breakout_resistance(data):
            score += 30

        result = PatternResult()

        result.symbol = symbol
        result.timeframe = timeframe
        result.pattern = PatternType.ROUNDING_BOTTOM

        result.score = score
        result.confidence = score
        result.quality = self.vcp_quality(score)

        result.breakout = (
            BreakoutType.CONFIRMED
            if self.breakout_resistance(data)
            else BreakoutType.NONE
        )

        result.breakout_price = self.last_close(data)

        lows = self.pivot_lows(data)

        if lows:
            result.stop_loss = lows[-1].price

        result.target = self.cup_target(data)

        result.volume_confirmation = self.volume_dry_up(data)
        result.valid = score >= 60
        result.message = "Rounding Bottom detected."

        return result
        # =====================================================
    # RELATIVE VOLUME
    # =====================================================

    def relative_volume(
        self,
        data: pd.DataFrame,
        period: int = 20,
    ) -> float:
        """
        Calculate Relative Volume (RVOL).
        """

        if len(data) < period + 1:
            return 0.0

        avg_volume = (
            data["volume"]
            .tail(period)
            .mean()
        )

        if avg_volume <= 0:
            return 0.0

        current = float(
            data["volume"].iloc[-1]
        )

        return current / avg_volume

    # =====================================================
    # RVOL CONFIRMATION
    # =====================================================

    def rvol_confirmation(
        self,
        data: pd.DataFrame,
        minimum: float = 1.50,
    ) -> bool:
        """
        Institutional Relative Volume filter.
        """

        return (
            self.relative_volume(data)
            >= minimum
        )

    # =====================================================
    # EMA ALIGNMENT
    # =====================================================

    def ema_alignment(
        self,
        data: pd.DataFrame,
    ) -> bool:
        """
        21 EMA > 50 EMA > 200 EMA.
        """

        ema21 = self.indicators.ema(data, 21)
        ema50 = self.indicators.ema(data, 50)
        ema200 = self.indicators.ema(data, 200)

        if isinstance(ema21, pd.Series):
            ema21 = ema21.iloc[-1]

        if isinstance(ema50, pd.Series):
            ema50 = ema50.iloc[-1]

        if isinstance(ema200, pd.Series):
            ema200 = ema200.iloc[-1]

        return (
            ema21 > ema50 > ema200
        )

    # =====================================================
    # VWAP CONFIRMATION
    # =====================================================

    def vwap_confirmation(
        self,
        data: pd.DataFrame,
    ) -> bool:
        """
        Price above VWAP.
        """

        vwap = self.indicators.vwap(data)

        if isinstance(vwap, pd.Series):
            vwap = vwap.iloc[-1]

        return (
            self.last_close(data)
            > float(vwap)
        )

    # =====================================================
    # ADX CONFIRMATION
    # =====================================================

    def adx_confirmation(
        self,
        data: pd.DataFrame,
        minimum: float = 25,
    ) -> bool:
        """
        Strong trend filter.
        """

        adx = self.indicators.adx(data)

        if isinstance(adx, pd.Series):
            adx = adx.iloc[-1]

        return float(adx) >= minimum

    # =====================================================
    # ATR EXPANSION
    # =====================================================

    def atr_expansion(
        self,
        data: pd.DataFrame,
    ) -> bool:
        """
        Current ATR greater than previous ATR.
        """

        atr = self.indicators.atr(data)

        if not isinstance(atr, pd.Series):
            return False

        if len(atr) < 2:
            return False

        return (
            atr.iloc[-1]
            > atr.iloc[-2]
        )

    # =====================================================
    # INSTITUTIONAL VOLUME
    # =====================================================

    def institutional_volume(
        self,
        data: pd.DataFrame,
    ) -> bool:
        """
        Institutional participation.
        """

        return (
            self.rvol_confirmation(data)
            and self.relative_volume(data) >= 2.0
        )

    # =====================================================
    # BREAKOUT CONFIRMATION
    # =====================================================

    def breakout_confirmation(
        self,
        data: pd.DataFrame,
    ) -> bool:
        """
        Complete breakout confirmation.
        """

        return all(

            (

                self.breakout_resistance(data),

                self.rvol_confirmation(data),

                self.vwap_confirmation(data),

            )

        )

    # =====================================================
    # FINAL SCORE
    # =====================================================

    def institutional_score(
        self,
        data: pd.DataFrame,
        base_score: float,
    ) -> float:
        """
        Final institutional score (0-100).
        """

        score = base_score

        if self.ema_alignment(data):
            score += 8

        if self.vwap_confirmation(data):
            score += 6

        if self.adx_confirmation(data):
            score += 6

        if self.rvol_confirmation(data):
            score += 8

        if self.atr_expansion(data):
            score += 5

        if self.institutional_volume(data):
            score += 7

        return min(score, 100)

    # =====================================================
    # VALIDATE PATTERN
    # =====================================================

    def validate_pattern(
        self,
        result: PatternResult,
        data: pd.DataFrame,
    ) -> PatternResult:
        """
        Apply institutional validation.
        """

        result.score = self.institutional_score(
            data,
            result.score,
        )

        result.confidence = result.score

        result.volume_confirmation = (
            self.rvol_confirmation(data)
        )

        result.trend_confirmation = (
            self.ema_alignment(data)
        )

        result.institutional_volume = (
            self.institutional_volume(data)
        )

        result.valid = (

            result.score >= 70

            and result.breakout
            != BreakoutType.NONE

        )

        result.quality = self.vcp_quality(
            result.score
        )

        return result

    # =====================================================
    # VALIDATE ALL PATTERNS
    # =====================================================

    def validate_patterns(
        self,
        patterns: List[PatternResult],
        data: pd.DataFrame,
    ) -> List[PatternResult]:
        """
        Validate all detected patterns.
        """

        validated = []

        for pattern in patterns:

            validated.append(

                self.validate_pattern(
                    pattern,
                    data,
                )

            )

        return validated

    # =====================================================
    # SORT BY SCORE
    # =====================================================

    def sort_patterns(
        self,
        patterns: List[PatternResult],
    ) -> List[PatternResult]:
        """
        Highest quality first.
        """

        return sorted(

            patterns,

            key=lambda x: x.score,

            reverse=True,

        )

    # =====================================================
    # BEST PATTERN
    # =====================================================

    def best_pattern(
        self,
        patterns: List[PatternResult],
    ) -> Optional[PatternResult]:
        """
        Highest ranked pattern.
        """

        if not patterns:
            return None

        return self.sort_patterns(
            patterns
        )[0]
        # =====================================================
    # DETECT ALL PATTERNS
    # =====================================================

    def detect_patterns(
        self,
        symbol: str,
        timeframe: str,
        data: pd.DataFrame,
    ) -> List[PatternResult]:
        """
        Execute all pattern detectors.
        """

        patterns: List[PatternResult] = []

        detectors = [

            self.detect_vcp,

            self.detect_falling_wedge,

            self.detect_bull_flag,

            self.detect_cup_handle,

            self.detect_flat_base,

            self.detect_ascending_triangle,

            self.detect_double_bottom,

            self.detect_rounding_bottom,

        ]

        for detector in detectors:

            try:

                result = detector(

                    symbol,

                    timeframe,

                    data,

                )

                if result is not None:

                    patterns.append(result)

            except Exception as exc:

                self.logger.exception(

                    "%s failed : %s",

                    detector.__name__,

                    exc,

                )

        return patterns

    # =====================================================
    # SCAN
    # =====================================================

    def scan_patterns(
        self,
        symbol: str,
        timeframe: str,
        data: pd.DataFrame,
    ) -> List[PatternResult]:
        """
        Complete scanning pipeline.
        """

        patterns = self.detect_patterns(

            symbol,

            timeframe,

            data,

        )

        if not patterns:

            return []

        patterns = self.validate_patterns(

            patterns,

            data,

        )

        patterns = self.sort_patterns(

            patterns,

        )

        self.results = patterns

        return patterns

    # =====================================================
    # BEST SIGNAL
    # =====================================================

    def best_signal(
        self,
        symbol: str,
        timeframe: str,
        data: pd.DataFrame,
    ) -> Optional[PatternResult]:
        """
        Highest ranked valid pattern.
        """

        patterns = self.scan_patterns(

            symbol,

            timeframe,

            data,

        )

        if not patterns:

            return None

        for pattern in patterns:

            if pattern.valid:

                return pattern

        return patterns[0]

    # =====================================================
    # WIN PROBABILITY
    # =====================================================

    def win_probability(
        self,
        result: PatternResult,
    ) -> float:
        """
        Estimate probability of success.
        """

        probability = 40.0

        probability += result.score * 0.45

        if result.volume_confirmation:
            probability += 5

        if result.trend_confirmation:
            probability += 5

        if result.institutional_volume:
            probability += 5

        if result.breakout == BreakoutType.CONFIRMED:
            probability += 5

        return min(

            probability,

            95.0,

        )

    # =====================================================
    # RISK GRADE
    # =====================================================

    def risk_grade(
        self,
        result: PatternResult,
    ) -> str:
        """
        Trading risk classification.
        """

        rr = result.risk_reward

        if rr >= 4:

            return "A+"

        if rr >= 3:

            return "A"

        if rr >= 2:

            return "B"

        if rr >= 1.5:

            return "C"

        return "D"

    # =====================================================
    # INSTITUTIONAL RATING
    # =====================================================

    def institutional_rating(
        self,
        result: PatternResult,
    ) -> str:
        """
        Institutional quality rating.
        """

        score = result.score

        if score >= 95:

            return "★★★★★"

        if score >= 90:

            return "★★★★☆"

        if score >= 80:

            return "★★★★"

        if score >= 70:

            return "★★★"

        if score >= 60:

            return "★★"

        return "★"

    # =====================================================
    # PATTERN SUMMARY
    # =====================================================

    def pattern_summary(
        self,
        result: PatternResult,
    ) -> Dict[str, Any]:
        """
        Summary dictionary.
        """

        return {

            "symbol": result.symbol,

            "pattern": result.pattern.value,

            "quality": result.quality.value,

            "score": round(

                result.score,

                2,

            ),

            "confidence": round(

                result.confidence,

                2,

            ),

            "risk_reward": round(

                result.risk_reward,

                2,

            ),

            "win_probability": round(

                self.win_probability(

                    result,

                ),

                2,

            ),

            "rating": self.institutional_rating(

                result,

            ),

            "risk_grade": self.risk_grade(

                result,

            ),

            "breakout": result.breakout.value,

            "target": round(

                result.target,

                2,

            ),

            "stop_loss": round(

                result.stop_loss,

                2,

            ),

        }

    # =====================================================
    # DASHBOARD DATA
    # =====================================================

    def dashboard(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Dashboard-ready pattern data.
        """

        dashboard = []

        for result in self.results:

            dashboard.append(

                self.pattern_summary(

                    result,

                )

            )

        return dashboard

    # =====================================================
    # CLEAR RESULTS
    # =====================================================

    def clear(
        self,
    ) -> None:
        """
        Reset cached results.
        """

        self.results.clear()

    # =====================================================
    # PATTERN COUNT
    # =====================================================

    @property
    def pattern_count(
        self,
    ) -> int:
        """
        Number of detected patterns.
        """

        return len(

            self.results

        )

    # =====================================================
    # HAS VALID PATTERNS
    # =====================================================

    def has_valid_patterns(
        self,
    ) -> bool:
        """
        Check for valid institutional setups.
        """

        return any(

            result.valid

            for result

            in self.results

        )
        # =====================================================
    # STATISTICS
    # =====================================================

    def statistics_report(
        self,
    ) -> Dict[str, Any]:
        """
        Return engine statistics.
        """

        uptime = (
            datetime.now()
            - self.started
        ).total_seconds()

        return {

            "version": self.VERSION,

            "uptime_seconds": round(
                uptime,
                2,
            ),

            "patterns_checked": self.statistics[
                "patterns_checked"
            ],

            "patterns_found": self.statistics[
                "patterns_found"
            ],

            "vcp": self.statistics["vcp"],

            "bull_flag": self.statistics[
                "bull_flag"
            ],

            "falling_wedge": self.statistics[
                "falling_wedge"
            ],

            "cup_handle": self.statistics[
                "cup_handle"
            ],

            "flat_base": self.statistics[
                "flat_base"
            ],

            "ascending_triangle": self.statistics[
                "ascending_triangle"
            ],

            "double_bottom": self.statistics[
                "double_bottom"
            ],

            "rounding_bottom": self.statistics[
                "rounding_bottom"
            ],

        }

    # =====================================================
    # EXPORT RESULTS
    # =====================================================

    def export_results(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Export results as dictionaries.
        """

        output = []

        for result in self.results:

            output.append(

                {

                    "symbol": result.symbol,

                    "timeframe": result.timeframe,

                    "pattern": result.pattern.value,

                    "quality": result.quality.value,

                    "breakout": result.breakout.value,

                    "score": result.score,

                    "confidence": result.confidence,

                    "target": result.target,

                    "stop_loss": result.stop_loss,

                    "risk_reward": result.risk_reward,

                    "valid": result.valid,

                    "message": result.message,

                }

            )

        return output

    # =====================================================
    # RESET ENGINE
    # =====================================================

    def reset(
        self,
    ) -> None:
        """
        Reset runtime state.
        """

        self.results.clear()

        self.statistics = {

            "patterns_checked": 0,

            "patterns_found": 0,

            "vcp": 0,

            "bull_flag": 0,

            "falling_wedge": 0,

            "cup_handle": 0,

            "flat_base": 0,

            "ascending_triangle": 0,

            "double_bottom": 0,

            "rounding_bottom": 0,

        }

        self.started = datetime.now()

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(
        self,
    ) -> Dict[str, Any]:
        """
        Runtime diagnostics.
        """

        return {

            "engine": "PatternEngine",

            "version": self.VERSION,

            "running": True,

            "cached_results": len(self.results),

            "pivot_window": self.pivot_window,

            "volume_factor": self.volume_factor,

            "minimum_bars": self.minimum_bars,

            "maximum_bars": self.maximum_bars,

        }

    # =====================================================
    # CONFIGURATION
    # =====================================================

    def configuration(
        self,
    ) -> Dict[str, Any]:
        """
        Current engine configuration.
        """

        return {

            "pivot_window": self.pivot_window,

            "breakout_buffer": self.breakout_buffer,

            "volume_factor": self.volume_factor,

            "max_base_depth": self.max_base_depth,

            "min_contraction": self.min_contraction,

            "minimum_bars": self.minimum_bars,

            "maximum_bars": self.maximum_bars,

        }

    # =====================================================
    # UPDATE CONFIGURATION
    # =====================================================

    def update_configuration(
        self,
        **kwargs,
    ) -> None:
        """
        Update runtime configuration.
        """

        for key, value in kwargs.items():

            if hasattr(self, key):

                setattr(

                    self,

                    key,

                    value,

                )

    # =====================================================
    # CONTEXT MANAGER
    # =====================================================

    def __enter__(
        self,
    ) -> "PatternEngine":

        return self

    def __exit__(
        self,
        exc_type,
        exc,
        tb,
    ) -> None:

        self.reset()

    # =====================================================
    # STRING
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (

            f"PatternEngine("

            f"version={self.VERSION}, "

            f"patterns={len(self.results)})"

        )

    # =====================================================
    # FACTORY
    # =====================================================

    @classmethod
    def create(
        cls,
    ) -> "PatternEngine":
        """
        Factory constructor.
        """

        return cls()

    # =====================================================
    # SINGLE STOCK ANALYSIS
    # =====================================================

    @classmethod
    def analyze_stock(
        cls,
        symbol: str,
        timeframe: str,
        data: pd.DataFrame,
    ) -> Optional[PatternResult]:
        """
        Convenience method for analyzing
        a single stock.
        """

        engine = cls()

        return engine.best_signal(

            symbol,

            timeframe,

            data,

        )

    # =====================================================
    # MULTI STOCK ANALYSIS
    # =====================================================

    @classmethod
    def analyze_market(
        cls,
        market_data: Dict[
            str,
            pd.DataFrame,
        ],
        timeframe: str,
    ) -> List[PatternResult]:
        """
        Analyze multiple symbols and
        return all valid patterns sorted
        by score.
        """

        engine = cls()

        results: List[
            PatternResult
        ] = []

        for symbol, df in market_data.items():

            try:

                signal = engine.best_signal(

                    symbol,

                    timeframe,

                    df,

                )

                if signal is not None:

                    results.append(signal)

            except Exception:

                engine.logger.exception(

                    "Failed to analyze %s",

                    symbol,

                )

        results.sort(

            key=lambda x: x.score,

            reverse=True,

        )

        return results


# =========================================================
# FACTORY FUNCTION
# =========================================================

def create_pattern_engine() -> PatternEngine:
    """
    Factory helper.
    """

    return PatternEngine()


# =========================================================
# END OF FILE
# =========================================================