from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

import numpy as np
import pandas as pd


# ======================================================
# PATTERN ENUMS
# ======================================================

class PatternType(Enum):

    VCP = "Volatility Contraction Pattern"

    CUP_HANDLE = "Cup & Handle"

    BULL_FLAG = "Bull Flag"

    FALLING_WEDGE = "Falling Wedge"

    RISING_WEDGE = "Rising Wedge"

    ASC_TRIANGLE = "Ascending Triangle"

    DESC_TRIANGLE = "Descending Triangle"

    SYM_TRIANGLE = "Symmetrical Triangle"

    DOUBLE_BOTTOM = "Double Bottom"

    DOUBLE_TOP = "Double Top"

    HEAD_SHOULDER = "Head & Shoulder"

    INVERSE_HEAD_SHOULDER = "Inverse Head & Shoulder"

    DARVAS_BOX = "Darvas Box"

    WYCKOFF_ACCUMULATION = "Wyckoff Accumulation"

    WYCKOFF_DISTRIBUTION = "Wyckoff Distribution"

    RECTANGLE = "Rectangle"

    ORB = "Opening Range Breakout"

    ATH_BREAKOUT = "All Time High Breakout"

    WEEK52_BREAKOUT = "52 Week Breakout"

    IPO_BASE = "IPO Base"

    FLAT_BASE = "Flat Base"

    TIGHT_CONSOLIDATION = "Tight Consolidation"

    NONE = "No Pattern"


class PatternStrength(Enum):

    VERY_STRONG = "Very Strong"

    STRONG = "Strong"

    MODERATE = "Moderate"

    WEAK = "Weak"

    INVALID = "Invalid"


# ======================================================
# RESULT MODEL
# ======================================================

@dataclass
class PatternResult:

    symbol: str

    pattern: PatternType

    strength: PatternStrength

    confidence: float

    probability: float

    score: float

    breakout_price: float

    entry: float

    stop_loss: float

    target1: float

    target2: float

    risk_reward: float

    reasons: List[str] = field(default_factory=list)

    warnings: List[str] = field(default_factory=list)

    indicators: Dict = field(default_factory=dict)


# ======================================================
# PATTERN RECOGNITION ENGINE
# ======================================================

class PatternRecognitionEngine:

    def __init__(self):

        self.symbol: str = ""

        self.data: Optional[pd.DataFrame] = None

        self.result: Optional[PatternResult] = None

    # ======================================================
    # LOAD
    # ======================================================

    def load(

        self,

        symbol: str,

        data: pd.DataFrame,

    ):

        self.symbol = symbol

        self.data = data.copy()

        self.validate()

        return self

    # ======================================================
    # VALIDATE
    # ======================================================

    def validate(

        self,

    ):

        if self.data is None:

            raise ValueError(

                "Market data not loaded."

            )

        required = [

            "Open",

            "High",

            "Low",

            "Close",

            "Volume",

        ]

        missing = [

            c

            for c in required

            if c not in self.data.columns

        ]

        if missing:

            raise ValueError(

                f"Missing columns: {missing}"

            )

    # ======================================================
    # OHLCV
    # ======================================================

    @property
    def open(self):

        return self.data["Open"]

    @property
    def high(self):

        return self.data["High"]

    @property
    def low(self):

        return self.data["Low"]

    @property
    def close(self):

        return self.data["Close"]

    @property
    def volume(self):

        return self.data["Volume"]

    # ======================================================
    # INDICATORS
    # ======================================================

    def sma(

        self,

        period: int,

    ):

        return self.close.rolling(period).mean()

    def ema(

        self,

        period: int,

    ):

        return self.close.ewm(

            span=period,

            adjust=False,

        ).mean()

    def atr(

        self,

        period: int = 14,

    ):

        tr = pd.concat(

            [

                self.high - self.low,

                (self.high - self.close.shift()).abs(),

                (self.low - self.close.shift()).abs(),

            ],

            axis=1,

        ).max(axis=1)

        return tr.rolling(period).mean()

    def rsi(

        self,

        period: int = 14,

    ):

        delta = self.close.diff()

        gain = delta.clip(lower=0)

        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(period).mean()

        avg_loss = loss.rolling(period).mean()

        rs = avg_gain / avg_loss.replace(

            0,

            np.nan,

        )

        return 100 - (

            100 /

            (

                1 + rs

            )

        )

    # ======================================================
    # SWING HIGHS
    # ======================================================

    def swing_highs(

        self,

        lookback: int = 5,

    ) -> pd.Series:

        return self.high.where(

            self.high ==

            self.high.rolling(

                lookback,

                center=True,

            ).max()

        )

    # ======================================================
    # SWING LOWS
    # ======================================================

    def swing_lows(

        self,

        lookback: int = 5,

    ) -> pd.Series:

        return self.low.where(

            self.low ==

            self.low.rolling(

                lookback,

                center=True,

            ).min()

        )

    # ======================================================
    # VOLUME RATIO
    # ======================================================

    def relative_volume(

        self,

        period: int = 20,

    ) -> float:

        avg = self.volume.rolling(

            period,

        ).mean().iloc[-1]

        if avg == 0:

            return 1.0

        return round(

            self.volume.iloc[-1] / avg,

            2,

        )

    # ======================================================
    # RESET
    # ======================================================

    def reset(

        self,

    ):

        self.symbol = ""

        self.data = None

        self.result = None
            # ======================================================
    # VCP (VOLATILITY CONTRACTION PATTERN)
    # ======================================================

    def detect_vcp(

        self,

        lookback: int = 40,

    ) -> Dict:

        data = self.data.tail(lookback)

        highs = data["High"]

        lows = data["Low"]

        ranges = highs - lows

        contractions = 0

        for i in range(1, len(ranges)):

            if ranges.iloc[i] < ranges.iloc[i - 1]:

                contractions += 1

        volume_contracting = (

            data["Volume"].tail(10).mean()

            <

            data["Volume"].head(10).mean()

        )

        detected = (

            contractions >= int(

                len(ranges) * 0.60

            )

            and

            volume_contracting

        )

        score = min(

            contractions * 3,

            100,

        )

        return {

            "detected": detected,

            "score": round(score, 2),

            "volume_contraction": volume_contracting,

            "breakout":

                highs.max(),

        }

    # ======================================================
    # CUP & HANDLE
    # ======================================================

    def detect_cup_handle(

        self,

        lookback: int = 80,

    ) -> Dict:

        close = self.close.tail(lookback)

        center = len(close) // 2

        left = close.iloc[:center].max()

        bottom = close.min()

        right = close.iloc[center:].max()

        cup = (

            abs(left - right)

            / max(left, 1)

            < 0.08

        )

        depth = (

            (left - bottom)

            / max(left, 1)

        )

        handle = (

            close.tail(10).max()

            < right * 1.02

        )

        detected = (

            cup

            and

            depth > 0.10

            and

            handle

        )

        score = 85 if detected else 25

        return {

            "detected": detected,

            "score": score,

            "depth": round(depth, 3),

            "breakout": right,

        }

    # ======================================================
    # BULL FLAG
    # ======================================================

    def detect_bull_flag(

        self,

        impulse: int = 15,

        flag: int = 10,

    ) -> Dict:

        impulse_move = (

            self.close.iloc[-flag-impulse]

            -

            self.close.iloc[-flag]

        )

        impulse_pct = (

            abs(impulse_move)

            /

            self.close.iloc[-flag-impulse]

        ) * 100

        consolidation = (

            self.high.tail(flag).max()

            -

            self.low.tail(flag).min()

        )

        consolidation_pct = (

            consolidation

            /

            self.close.iloc[-1]

        ) * 100

        detected = (

            impulse_pct > 10

            and

            consolidation_pct < 6

        )

        score = 90 if detected else 30

        return {

            "detected": detected,

            "score": score,

            "impulse_pct":

                round(impulse_pct, 2),

            "flag_pct":

                round(consolidation_pct, 2),

        }

    # ======================================================
    # FALLING WEDGE
    # ======================================================

    def detect_falling_wedge(

        self,

        lookback: int = 40,

    ) -> Dict:

        highs = self.high.tail(lookback)

        lows = self.low.tail(lookback)

        x = np.arange(len(highs))

        upper = np.polyfit(

            x,

            highs,

            1,

        )[0]

        lower = np.polyfit(

            x,

            lows,

            1,

        )[0]

        detected = (

            upper < 0

            and

            lower < 0

            and

            abs(lower) < abs(upper)

        )

        score = 88 if detected else 20

        return {

            "detected": detected,

            "score": score,

            "upper_slope":

                round(upper, 4),

            "lower_slope":

                round(lower, 4),

        }

    # ======================================================
    # RISING WEDGE
    # ======================================================

    def detect_rising_wedge(

        self,

        lookback: int = 40,

    ) -> Dict:

        highs = self.high.tail(lookback)

        lows = self.low.tail(lookback)

        x = np.arange(len(highs))

        upper = np.polyfit(

            x,

            highs,

            1,

        )[0]

        lower = np.polyfit(

            x,

            lows,

            1,

        )[0]

        detected = (

            upper > 0

            and

            lower > 0

            and

            lower > upper

        )

        score = 85 if detected else 25

        return {

            "detected": detected,

            "score": score,

            "upper_slope":

                round(upper, 4),

            "lower_slope":

                round(lower, 4),

        }

    # ======================================================
    # RECTANGLE
    # ======================================================

    def detect_rectangle(

        self,

        lookback: int = 30,

    ) -> Dict:

        highs = self.high.tail(lookback)

        lows = self.low.tail(lookback)

        resistance = highs.max()

        support = lows.min()

        width = (

            (resistance - support)

            /

            max(support, 1)

        ) * 100

        detected = width < 8

        return {

            "detected": detected,

            "score": 80 if detected else 25,

            "support": support,

            "resistance": resistance,

        }

    # ======================================================
    # FLAT BASE
    # ======================================================

    def detect_flat_base(

        self,

        lookback: int = 30,

    ) -> Dict:

        close = self.close.tail(lookback)

        deviation = (

            close.std()

            /

            close.mean()

        ) * 100

        detected = deviation < 4

        return {

            "detected": detected,

            "score": 85 if detected else 20,

            "deviation":

                round(deviation, 2),

        }

    # ======================================================
    # TIGHT CONSOLIDATION
    # ======================================================

    def detect_tight_consolidation(

        self,

        bars: int = 10,

    ) -> Dict:

        high = self.high.tail(bars).max()

        low = self.low.tail(bars).min()

        range_pct = (

            (high - low)

            /

            self.close.iloc[-1]

        ) * 100

        detected = range_pct < 3

        return {

            "detected": detected,

            "score": 90 if detected else 20,

            "range_pct":

                round(range_pct, 2),

        }
        # ======================================================
    # ASCENDING TRIANGLE
    # ======================================================

    def detect_ascending_triangle(

        self,

        lookback: int = 40,

    ) -> Dict:

        highs = self.high.tail(lookback)

        lows = self.low.tail(lookback)

        resistance = highs.tail(15).mean()

        x = np.arange(len(lows))

        slope = np.polyfit(

            x,

            lows.values,

            1,

        )[0]

        resistance_dev = (

            highs.tail(15).std()

            /

            max(resistance, 1)

        ) * 100

        detected = (

            slope > 0

            and

            resistance_dev < 2.5

        )

        score = 92 if detected else 25

        return {

            "detected": detected,

            "score": score,

            "support_slope": round(slope, 4),

            "resistance": round(resistance, 2),

        }

    # ======================================================
    # DESCENDING TRIANGLE
    # ======================================================

    def detect_descending_triangle(

        self,

        lookback: int = 40,

    ) -> Dict:

        highs = self.high.tail(lookback)

        lows = self.low.tail(lookback)

        support = lows.tail(15).mean()

        x = np.arange(len(highs))

        slope = np.polyfit(

            x,

            highs.values,

            1,

        )[0]

        support_dev = (

            lows.tail(15).std()

            /

            max(support, 1)

        ) * 100

        detected = (

            slope < 0

            and

            support_dev < 2.5

        )

        score = 90 if detected else 25

        return {

            "detected": detected,

            "score": score,

            "resistance_slope": round(slope, 4),

            "support": round(support, 2),

        }

    # ======================================================
    # SYMMETRICAL TRIANGLE
    # ======================================================

    def detect_symmetrical_triangle(

        self,

        lookback: int = 40,

    ) -> Dict:

        highs = self.high.tail(lookback)

        lows = self.low.tail(lookback)

        x = np.arange(len(highs))

        upper = np.polyfit(

            x,

            highs.values,

            1,

        )[0]

        lower = np.polyfit(

            x,

            lows.values,

            1,

        )[0]

        detected = (

            upper < 0

            and

            lower > 0

        )

        score = 88 if detected else 20

        return {

            "detected": detected,

            "score": score,

            "upper_slope": round(upper, 4),

            "lower_slope": round(lower, 4),

        }

    # ======================================================
    # DOUBLE BOTTOM
    # ======================================================

    def detect_double_bottom(

        self,

        lookback: int = 60,

        tolerance: float = 0.03,

    ) -> Dict:

        lows = self.swing_lows().dropna().tail(6)

        detected = False

        neckline = None

        if len(lows) >= 2:

            first = lows.iloc[-2]

            second = lows.iloc[-1]

            detected = (

                abs(first - second)

                /

                max(first, 1)

                <= tolerance

            )

            neckline = self.high.tail(lookback).max()

        score = 90 if detected else 20

        return {

            "detected": detected,

            "score": score,

            "neckline": neckline,

            "bottoms": len(lows),

        }

    # ======================================================
    # DOUBLE TOP
    # ======================================================

    def detect_double_top(

        self,

        lookback: int = 60,

        tolerance: float = 0.03,

    ) -> Dict:

        highs = self.swing_highs().dropna().tail(6)

        detected = False

        support = None

        if len(highs) >= 2:

            first = highs.iloc[-2]

            second = highs.iloc[-1]

            detected = (

                abs(first - second)

                /

                max(first, 1)

                <= tolerance

            )

            support = self.low.tail(lookback).min()

        score = 90 if detected else 20

        return {

            "detected": detected,

            "score": score,

            "support": support,

            "tops": len(highs),

        }

    # ======================================================
    # HEAD & SHOULDERS
    # ======================================================

    def detect_head_shoulders(

        self,

        lookback: int = 60,

    ) -> Dict:

        highs = self.swing_highs().dropna().tail(5)

        detected = False

        if len(highs) >= 3:

            left = highs.iloc[-3]

            head = highs.iloc[-2]

            right = highs.iloc[-1]

            detected = (

                head > left

                and

                head > right

                and

                abs(left - right)

                / max(left, 1)

                < 0.05

            )

        score = 94 if detected else 20

        return {

            "detected": detected,

            "score": score,

        }

    # ======================================================
    # INVERSE HEAD & SHOULDERS
    # ======================================================

    def detect_inverse_head_shoulders(

        self,

        lookback: int = 60,

    ) -> Dict:

        lows = self.swing_lows().dropna().tail(5)

        detected = False

        if len(lows) >= 3:

            left = lows.iloc[-3]

            head = lows.iloc[-2]

            right = lows.iloc[-1]

            detected = (

                head < left

                and

                head < right

                and

                abs(left - right)

                / max(left, 1)

                < 0.05

            )

        score = 94 if detected else 20

        return {

            "detected": detected,

            "score": score,

        }

    # ======================================================
    # DARVAS BOX
    # ======================================================

    def detect_darvas_box(

        self,

        lookback: int = 20,

    ) -> Dict:

        highs = self.high.tail(lookback)

        lows = self.low.tail(lookback)

        top = highs.max()

        bottom = lows.min()

        width = (

            (top - bottom)

            /

            max(bottom, 1)

        ) * 100

        breakout = (

            self.close.iloc[-1]

            >

            top

        )

        detected = (

            width < 10

        )

        score = 88 if detected else 20

        return {

            "detected": detected,

            "score": score,

            "top": round(top, 2),

            "bottom": round(bottom, 2),

            "breakout": breakout,

        }
        # ======================================================
    # WYCKOFF ACCUMULATION
    # ======================================================

    def detect_wyckoff_accumulation(

        self,

        lookback: int = 60,

    ) -> Dict:

        data = self.data.tail(lookback)

        avg_volume = data["Volume"].mean()

        recent_volume = data["Volume"].tail(10).mean()

        price_range = (

            data["High"].max()

            -

            data["Low"].min()

        ) / max(

            data["Low"].min(),

            1,

        ) * 100

        close_position = (

            self.close.iloc[-1]

            -

            data["Low"].min()

        ) / (

            max(

                data["High"].max()

                -

                data["Low"].min(),

                0.01,

            )

        )

        detected = (

            recent_volume > avg_volume * 1.20

            and

            price_range < 18

            and

            close_position > 0.70

        )

        score = 92 if detected else 25

        return {

            "detected": detected,

            "score": score,

            "volume_ratio": round(

                recent_volume / avg_volume,

                2,

            ),

            "price_range": round(

                price_range,

                2,

            ),

        }

    # ======================================================
    # WYCKOFF DISTRIBUTION
    # ======================================================

    def detect_wyckoff_distribution(

        self,

        lookback: int = 60,

    ) -> Dict:

        data = self.data.tail(lookback)

        avg_volume = data["Volume"].mean()

        recent_volume = data["Volume"].tail(10).mean()

        close_position = (

            self.close.iloc[-1]

            -

            data["Low"].min()

        ) / (

            max(

                data["High"].max()

                -

                data["Low"].min(),

                0.01,

            )

        )

        detected = (

            recent_volume > avg_volume * 1.20

            and

            close_position < 0.35

        )

        score = 92 if detected else 20

        return {

            "detected": detected,

            "score": score,

            "volume_ratio": round(

                recent_volume / avg_volume,

                2,

            ),

        }

    # ======================================================
    # OPENING RANGE BREAKOUT (ORB)
    # ======================================================

    def detect_orb(

        self,

        opening_bars: int = 9,

    ) -> Dict:

        session = self.data.iloc[:opening_bars]

        orb_high = session["High"].max()

        orb_low = session["Low"].min()

        latest_close = self.close.iloc[-1]

        latest_volume = self.volume.iloc[-1]

        avg_volume = self.volume.tail(20).mean()

        bullish_breakout = (

            latest_close > orb_high

        )

        bearish_breakout = (

            latest_close < orb_low

        )

        volume_confirmed = (

            latest_volume >

            avg_volume * 1.50

        )

        detected = (

            (

                bullish_breakout

                or

                bearish_breakout

            )

            and

            volume_confirmed

        )

        score = 95 if detected else 25

        return {

            "detected": detected,

            "score": score,

            "bullish": bullish_breakout,

            "bearish": bearish_breakout,

            "orb_high": round(

                orb_high,

                2,

            ),

            "orb_low": round(

                orb_low,

                2,

            ),

        }

    # ======================================================
    # 52 WEEK BREAKOUT
    # ======================================================

    def detect_52week_breakout(

        self,

        lookback: int = 252,

    ) -> Dict:

        highest = self.high.tail(

            lookback,

        ).max()

        breakout = (

            self.close.iloc[-1]

            >= highest

        )

        score = 98 if breakout else 20

        return {

            "detected": breakout,

            "score": score,

            "breakout_level":

                round(highest, 2),

        }

    # ======================================================
    # ALL TIME HIGH BREAKOUT
    # ======================================================

    def detect_ath_breakout(

        self,

    ) -> Dict:

        highest = self.high.max()

        breakout = (

            self.close.iloc[-1]

            >= highest

        )

        score = 100 if breakout else 20

        return {

            "detected": breakout,

            "score": score,

            "ath":

                round(highest, 2),

        }

    # ======================================================
    # IPO BASE
    # ======================================================

    def detect_ipo_base(

        self,

        bars: int = 120,

    ) -> Dict:

        if len(self.data) > bars:

            return {

                "detected": False,

                "score": 0,

            }

        deviation = (

            self.close.std()

            /

            self.close.mean()

        ) * 100

        breakout = (

            self.close.iloc[-1]

            >

            self.high.shift(1).max()

        )

        detected = (

            deviation < 12

            and

            breakout

        )

        score = 90 if detected else 20

        return {

            "detected": detected,

            "score": score,

            "deviation":

                round(deviation, 2),

        }

    # ======================================================
    # BREAKOUT QUALITY SCORE
    # ======================================================

    def breakout_quality(

        self,

    ) -> float:

        volume = self.relative_volume()

        atr_pct = (

            self.atr().iloc[-1]

            /

            self.close.iloc[-1]

        ) * 100

        breakout_strength = (

            self.close.iloc[-1]

            -

            self.close.tail(20).min()

        ) / max(

            self.close.tail(20).min(),

            1,

        ) * 100

        score = (

            min(volume * 20, 40)

            +

            min(breakout_strength, 40)

            +

            max(

                20 - atr_pct,

                0,

            )

        )

        return round(

            min(score, 100),

            2,

        )

    # ======================================================
    # VOLUME CONFIRMATION
    # ======================================================

    def volume_confirmation(

        self,

        multiplier: float = 1.50,

    ) -> Dict:

        avg = self.volume.tail(20).mean()

        latest = self.volume.iloc[-1]

        ratio = latest / max(

            avg,

            1,

        )

        confirmed = ratio >= multiplier

        return {

            "confirmed": confirmed,

            "ratio": round(ratio, 2),

            "score": min(

                round(ratio * 40, 2),

                100,

            ),

        }
        # ======================================================
    # PATTERN SCORE ENGINE
    # ======================================================

    def pattern_score(

        self,

        detection: Dict,

    ) -> float:

        base = detection.get(

            "score",

            0,

        )

        volume = self.volume_confirmation()[

            "score"

        ]

        breakout = self.breakout_quality()

        score = (

            base * 0.60 +

            volume * 0.20 +

            breakout * 0.20

        )

        return round(

            min(score, 100),

            2,

        )

    # ======================================================
    # CONFIDENCE ENGINE
    # ======================================================

    def confidence(

        self,

        detection: Dict,

    ) -> float:

        score = self.pattern_score(

            detection,

        )

        rvol = self.relative_volume()

        confidence = (

            score * 0.80 +

            min(

                rvol * 10,

                20,

            )

        )

        return round(

            min(

                confidence,

                100,

            ),

            2,

        )

    # ======================================================
    # PATTERN STRENGTH
    # ======================================================

    def pattern_strength(

        self,

        score: float,

    ) -> PatternStrength:

        if score >= 90:

            return PatternStrength.VERY_STRONG

        if score >= 75:

            return PatternStrength.STRONG

        if score >= 60:

            return PatternStrength.MODERATE

        if score >= 40:

            return PatternStrength.WEAK

        return PatternStrength.INVALID

    # ======================================================
    # BEST PATTERN SELECTOR
    # ======================================================

    def best_pattern(

        self,

    ) -> Dict:

        scans = {

            PatternType.VCP:

                self.detect_vcp(),

            PatternType.CUP_HANDLE:

                self.detect_cup_handle(),

            PatternType.BULL_FLAG:

                self.detect_bull_flag(),

            PatternType.FALLING_WEDGE:

                self.detect_falling_wedge(),

            PatternType.RISING_WEDGE:

                self.detect_rising_wedge(),

            PatternType.ASC_TRIANGLE:

                self.detect_ascending_triangle(),

            PatternType.DESC_TRIANGLE:

                self.detect_descending_triangle(),

            PatternType.SYM_TRIANGLE:

                self.detect_symmetrical_triangle(),

            PatternType.DOUBLE_BOTTOM:

                self.detect_double_bottom(),

            PatternType.DOUBLE_TOP:

                self.detect_double_top(),

            PatternType.HEAD_SHOULDER:

                self.detect_head_shoulders(),

            PatternType.INVERSE_HEAD_SHOULDER:

                self.detect_inverse_head_shoulders(),

            PatternType.DARVAS_BOX:

                self.detect_darvas_box(),

            PatternType.WYCKOFF_ACCUMULATION:

                self.detect_wyckoff_accumulation(),

            PatternType.WYCKOFF_DISTRIBUTION:

                self.detect_wyckoff_distribution(),

            PatternType.ORB:

                self.detect_orb(),

            PatternType.WEEK52_BREAKOUT:

                self.detect_52week_breakout(),

            PatternType.ATH_BREAKOUT:

                self.detect_ath_breakout(),

            PatternType.IPO_BASE:

                self.detect_ipo_base(),

            PatternType.FLAT_BASE:

                self.detect_flat_base(),

            PatternType.RECTANGLE:

                self.detect_rectangle(),

            PatternType.TIGHT_CONSOLIDATION:

                self.detect_tight_consolidation(),

        }

        winner = PatternType.NONE

        winner_data = {

            "score": 0,

            "detected": False,

        }

        for pattern, result in scans.items():

            if (

                result.get("detected", False)

                and

                result.get("score", 0)

                >

                winner_data["score"]

            ):

                winner = pattern

                winner_data = result

        return {

            "pattern": winner,

            "data": winner_data,

        }

    # ======================================================
    # ENTRY PRICE
    # ======================================================

    def entry_price(

        self,

        detection: Dict,

    ) -> float:

        if "breakout" in detection:

            return round(

                detection["breakout"],

                2,

            )

        return round(

            self.close.iloc[-1],

            2,

        )

    # ======================================================
    # STOP LOSS
    # ======================================================

    def stop_loss(

        self,

        multiplier: float = 1.5,

    ) -> float:

        atr = self.atr().iloc[-1]

        stop = (

            self.close.iloc[-1]

            -

            atr * multiplier

        )

        return round(

            stop,

            2,

        )

    # ======================================================
    # TARGETS
    # ======================================================

    def targets(

        self,

        multiplier1: float = 2.0,

        multiplier2: float = 4.0,

    ) -> Dict:

        atr = self.atr().iloc[-1]

        entry = self.close.iloc[-1]

        return {

            "target1":

                round(

                    entry + atr * multiplier1,

                    2,

                ),

            "target2":

                round(

                    entry + atr * multiplier2,

                    2,

                ),

        }

    # ======================================================
    # RISK REWARD
    # ======================================================

    def risk_reward(

        self,

    ) -> float:

        entry = self.close.iloc[-1]

        stop = self.stop_loss()

        target = self.targets()[

            "target2"

        ]

        risk = max(

            entry - stop,

            0.01,

        )

        reward = max(

            target - entry,

            0.01,

        )

        return round(

            reward / risk,

            2,

        )
        # ======================================================
    # PATTERN REASON GENERATOR
    # ======================================================

    def generate_reasons(

        self,

        pattern: PatternType,

        detection: Dict,

    ) -> List[str]:

        reasons = []

        if detection.get("detected"):

            reasons.append(

                f"{pattern.value} detected."

            )

        if detection.get(

            "score",

            0,

        ) >= 80:

            reasons.append(

                "High quality pattern structure."

            )

        volume = self.volume_confirmation()

        if volume["confirmed"]:

            reasons.append(

                f"Volume confirmation ({volume['ratio']}x average)."

            )

        breakout = self.breakout_quality()

        if breakout >= 80:

            reasons.append(

                "Excellent breakout quality."

            )

        ema20 = self.ema(20).iloc[-1]

        ema50 = self.ema(50).iloc[-1]

        if ema20 > ema50:

            reasons.append(

                "Short-term trend aligned with pattern."

            )

        if self.close.iloc[-1] > ema20:

            reasons.append(

                "Price trading above 20 EMA."

            )

        rsi = self.rsi().iloc[-1]

        if 50 <= rsi <= 70:

            reasons.append(

                f"Healthy RSI ({rsi:.1f})."

            )

        return reasons

    # ======================================================
    # WARNING ENGINE
    # ======================================================

    def generate_warnings(

        self,

        detection: Dict,

    ) -> List[str]:

        warnings = []

        volume = self.volume_confirmation()

        if not volume["confirmed"]:

            warnings.append(

                "Breakout volume is below ideal."

            )

        if self.relative_volume() < 1.20:

            warnings.append(

                "Relative volume is weak."

            )

        atr_pct = (

            self.atr().iloc[-1]

            /

            self.close.iloc[-1]

        ) * 100

        if atr_pct > 6:

            warnings.append(

                "High volatility."

            )

        rsi = self.rsi().iloc[-1]

        if rsi > 75:

            warnings.append(

                "Stock is overbought."

            )

        if rsi < 30:

            warnings.append(

                "Stock is oversold."

            )

        if detection.get(

            "score",

            0,

        ) < 60:

            warnings.append(

                "Pattern confidence is low."

            )

        return warnings

    # ======================================================
    # AI EXPLANATION
    # ======================================================

    def ai_explanation(

        self,

        result: PatternResult,

    ) -> str:

        text = []

        text.append(

            f"Pattern: {result.pattern.value}"

        )

        text.append(

            f"Strength: {result.strength.value}"

        )

        text.append(

            f"Confidence: {result.confidence:.1f}%"

        )

        text.append(

            f"Pattern Score: {result.score:.1f}"

        )

        text.append(

            f"Entry: {result.entry:.2f}"

        )

        text.append(

            f"Stop Loss: {result.stop_loss:.2f}"

        )

        text.append(

            f"Target 1: {result.target1:.2f}"

        )

        text.append(

            f"Target 2: {result.target2:.2f}"

        )

        text.append(

            f"Risk/Reward: 1:{result.risk_reward:.2f}"

        )

        return "\n".join(text)

    # ======================================================
    # DASHBOARD DATA
    # ======================================================

    def dashboard(

        self,

        result: PatternResult,

    ) -> Dict:

        return {

            "Symbol": result.symbol,

            "Pattern": result.pattern.value,

            "Strength": result.strength.value,

            "Confidence": result.confidence,

            "Score": result.score,

            "Entry": result.entry,

            "StopLoss": result.stop_loss,

            "Target1": result.target1,

            "Target2": result.target2,

            "RR": result.risk_reward,

            "Reasons": result.reasons,

            "Warnings": result.warnings,

        }

    # ======================================================
    # SUMMARY
    # ======================================================

    def summary(

        self,

        result: PatternResult,

    ) -> Dict:

        return {

            "pattern": result.pattern.value,

            "confidence": result.confidence,

            "score": result.score,

            "entry": result.entry,

            "stop_loss": result.stop_loss,

            "target": result.target2,

            "rr": result.risk_reward,

        }

    # ======================================================
    # FULL REPORT
    # ======================================================

    def report(

        self,

        result: PatternResult,

    ) -> Dict:

        return {

            "dashboard":

                self.dashboard(result),

            "summary":

                self.summary(result),

            "explanation":

                self.ai_explanation(result),

        }

    # ======================================================
    # MULTI PATTERN RANKING
    # ======================================================

    def rank_patterns(

        self,

    ) -> List[Dict]:

        ranking = []

        detectors = {

            PatternType.VCP: self.detect_vcp,

            PatternType.CUP_HANDLE: self.detect_cup_handle,

            PatternType.BULL_FLAG: self.detect_bull_flag,

            PatternType.FALLING_WEDGE: self.detect_falling_wedge,

            PatternType.RISING_WEDGE: self.detect_rising_wedge,

            PatternType.ASC_TRIANGLE: self.detect_ascending_triangle,

            PatternType.DESC_TRIANGLE: self.detect_descending_triangle,

            PatternType.SYM_TRIANGLE: self.detect_symmetrical_triangle,

            PatternType.DOUBLE_BOTTOM: self.detect_double_bottom,

            PatternType.DOUBLE_TOP: self.detect_double_top,

            PatternType.HEAD_SHOULDER: self.detect_head_shoulders,

            PatternType.INVERSE_HEAD_SHOULDER: self.detect_inverse_head_shoulders,

            PatternType.DARVAS_BOX: self.detect_darvas_box,

            PatternType.WYCKOFF_ACCUMULATION: self.detect_wyckoff_accumulation,

            PatternType.WYCKOFF_DISTRIBUTION: self.detect_wyckoff_distribution,

            PatternType.ORB: self.detect_orb,

            PatternType.WEEK52_BREAKOUT: self.detect_52week_breakout,

            PatternType.ATH_BREAKOUT: self.detect_ath_breakout,

            PatternType.IPO_BASE: self.detect_ipo_base,

            PatternType.FLAT_BASE: self.detect_flat_base,

            PatternType.RECTANGLE: self.detect_rectangle,

            PatternType.TIGHT_CONSOLIDATION: self.detect_tight_consolidation,

        }

        for pattern, detector in detectors.items():

            data = detector()

            if data.get("detected"):

                ranking.append({

                    "pattern": pattern,

                    "score": self.pattern_score(data),

                    "confidence": self.confidence(data),

                })

        ranking.sort(

            key=lambda x: x["score"],

            reverse=True,

        )

        return ranking

    # ======================================================
    # COMPARE TOP PATTERNS
    # ======================================================

    def compare_patterns(

        self,

        top: int = 5,

    ) -> List[Dict]:

        ranked = self.rank_patterns()

        return ranked[:top]
        # ======================================================
    # ANALYZE
    # ======================================================

    def analyze(

        self,

    ) -> PatternResult:

        best = self.best_pattern()

        pattern = best["pattern"]

        detection = best["data"]

        if pattern == PatternType.NONE:

            self.result = PatternResult(

                symbol=self.symbol,

                pattern=PatternType.NONE,

                strength=PatternStrength.INVALID,

                confidence=0.0,

                probability=0.0,

                score=0.0,

                breakout_price=0.0,

                entry=0.0,

                stop_loss=0.0,

                target1=0.0,

                target2=0.0,

                risk_reward=0.0,

                reasons=["No valid technical pattern detected."],

                warnings=["Wait for a higher probability setup."],

                indicators={},

            )

            return self.result

        score = self.pattern_score(

            detection,

        )

        confidence = self.confidence(

            detection,

        )

        strength = self.pattern_strength(

            score,

        )

        entry = self.entry_price(

            detection,

        )

        stop = self.stop_loss()

        targets = self.targets()

        rr = self.risk_reward()

        breakout_price = detection.get(

            "breakout",

            entry,

        )

        probability = round(

            confidence * 0.95,

            2,

        )

        reasons = self.generate_reasons(

            pattern,

            detection,

        )

        warnings = self.generate_warnings(

            detection,

        )

        indicators = {

            "EMA20":

                round(

                    self.ema(20).iloc[-1],

                    2,

                ),

            "EMA50":

                round(

                    self.ema(50).iloc[-1],

                    2,

                ),

            "RSI":

                round(

                    self.rsi().iloc[-1],

                    2,

                ),

            "ATR":

                round(

                    self.atr().iloc[-1],

                    2,

                ),

            "RVOL":

                self.relative_volume(),

            "BreakoutQuality":

                self.breakout_quality(),

            "VolumeConfirmation":

                self.volume_confirmation(),

        }

        self.result = PatternResult(

            symbol=self.symbol,

            pattern=pattern,

            strength=strength,

            confidence=confidence,

            probability=probability,

            score=score,

            breakout_price=breakout_price,

            entry=entry,

            stop_loss=stop,

            target1=targets["target1"],

            target2=targets["target2"],

            risk_reward=rr,

            reasons=reasons,

            warnings=warnings,

            indicators=indicators,

        )

        return self.result

    # ======================================================
    # GET RESULT
    # ======================================================

    def get_result(

        self,

    ) -> Optional[PatternResult]:

        return self.result

    # ======================================================
    # RESULT AS DICTIONARY
    # ======================================================

    def to_dict(

        self,

    ) -> Dict:

        if self.result is None:

            self.analyze()

        return {

            "symbol":

                self.result.symbol,

            "pattern":

                self.result.pattern.value,

            "strength":

                self.result.strength.value,

            "confidence":

                self.result.confidence,

            "probability":

                self.result.probability,

            "score":

                self.result.score,

            "breakout_price":

                self.result.breakout_price,

            "entry":

                self.result.entry,

            "stop_loss":

                self.result.stop_loss,

            "target1":

                self.result.target1,

            "target2":

                self.result.target2,

            "risk_reward":

                self.result.risk_reward,

            "reasons":

                self.result.reasons,

            "warnings":

                self.result.warnings,

            "indicators":

                self.result.indicators,

        }

    # ======================================================
    # JSON READY
    # ======================================================

    def json(

        self,

    ) -> Dict:

        return self.to_dict()

    # ======================================================
    # PRINT REPORT
    # ======================================================

    def print_report(

        self,

    ):

        if self.result is None:

            self.analyze()

        print("=" * 60)

        print("STOCKVERSITY AI PATTERN ANALYSIS")

        print("=" * 60)

        print(f"Symbol      : {self.result.symbol}")

        print(f"Pattern     : {self.result.pattern.value}")

        print(f"Strength    : {self.result.strength.value}")

        print(f"Confidence  : {self.result.confidence:.2f}%")

        print(f"Probability : {self.result.probability:.2f}%")

        print(f"Score       : {self.result.score:.2f}")

        print(f"Entry       : {self.result.entry:.2f}")

        print(f"Stop Loss   : {self.result.stop_loss:.2f}")

        print(f"Target 1    : {self.result.target1:.2f}")

        print(f"Target 2    : {self.result.target2:.2f}")

        print(f"RR          : 1:{self.result.risk_reward:.2f}")

        print()

        print("Reasons")

        print("-" * 60)

        for reason in self.result.reasons:

            print(f"• {reason}")

        print()

        print("Warnings")

        print("-" * 60)

        for warning in self.result.warnings:

            print(f"• {warning}")

        print()

        print("Indicators")

        print("-" * 60)

        for key, value in self.result.indicators.items():

            print(f"{key:20} : {value}")

        print("=" * 60)

    # ======================================================
    # CALL SHORTCUT
    # ======================================================

    def __call__(

        self,

    ) -> PatternResult:

        return self.analyze()
        # ======================================================
    # MULTI TIMEFRAME CONFIRMATION
    # ======================================================

    def multi_timeframe_confirmation(

        self,

    ) -> Dict:

        ema20 = self.ema(20).iloc[-1]

        ema50 = self.ema(50).iloc[-1]

        ema200 = self.ema(200).iloc[-1]

        price = self.close.iloc[-1]

        short_term = price > ema20

        medium_term = ema20 > ema50

        long_term = ema50 > ema200

        confirmations = sum(

            [

                short_term,

                medium_term,

                long_term,

            ]

        )

        score = round(

            confirmations / 3 * 100,

            2,

        )

        return {

            "confirmed": confirmations >= 2,

            "score": score,

            "short_term": short_term,

            "medium_term": medium_term,

            "long_term": long_term,

        }

    # ======================================================
    # TREND ALIGNMENT
    # ======================================================

    def trend_alignment(

        self,

    ) -> Dict:

        ema20 = self.ema(20).iloc[-1]

        ema50 = self.ema(50).iloc[-1]

        ema200 = self.ema(200).iloc[-1]

        bullish = (

            self.close.iloc[-1]

            >

            ema20

            >

            ema50

            >

            ema200

        )

        bearish = (

            self.close.iloc[-1]

            <

            ema20

            <

            ema50

            <

            ema200

        )

        score = 100 if bullish else 85 if bearish else 45

        return {

            "bullish": bullish,

            "bearish": bearish,

            "score": score,

        }

    # ======================================================
    # SUPPORT & RESISTANCE
    # ======================================================

    def support_resistance(

        self,

        lookback: int = 60,

    ) -> Dict:

        support = self.low.tail(

            lookback,

        ).min()

        resistance = self.high.tail(

            lookback,

        ).max()

        distance_support = (

            (

                self.close.iloc[-1]

                -

                support

            )

            /

            support

        ) * 100

        distance_resistance = (

            (

                resistance

                -

                self.close.iloc[-1]

            )

            /

            self.close.iloc[-1]

        ) * 100

        return {

            "support":

                round(

                    support,

                    2,

                ),

            "resistance":

                round(

                    resistance,

                    2,

                ),

            "distance_support":

                round(

                    distance_support,

                    2,

                ),

            "distance_resistance":

                round(

                    distance_resistance,

                    2,

                ),

        }

    # ======================================================
    # BREAKOUT RETEST
    # ======================================================

    def breakout_retest(

        self,

        tolerance: float = 0.01,

    ) -> Dict:

        resistance = self.high.shift(

            1,

        ).tail(

            20,

        ).max()

        close = self.close.iloc[-1]

        low = self.low.iloc[-1]

        retest = (

            low

            <=

            resistance * (

                1 + tolerance

            )

            and

            close > resistance

        )

        return {

            "detected": retest,

            "level": round(

                resistance,

                2,

            ),

            "score": 95 if retest else 35,

        }

    # ======================================================
    # FALSE BREAKOUT
    # ======================================================

    def false_breakout(

        self,

    ) -> Dict:

        resistance = self.high.shift(

            1,

        ).tail(

            20,

        ).max()

        high = self.high.iloc[-1]

        close = self.close.iloc[-1]

        failed = (

            high > resistance

            and

            close < resistance

        )

        return {

            "detected": failed,

            "score": 100 if failed else 20,

        }

    # ======================================================
    # VOLUME DRY-UP
    # ======================================================

    def volume_dryup(

        self,

        period: int = 10,

    ) -> Dict:

        recent = self.volume.tail(

            period,

        ).mean()

        average = self.volume.tail(

            50,

        ).mean()

        ratio = recent / max(

            average,

            1,

        )

        dryup = ratio < 0.70

        score = (

            (1 - ratio) * 100

        )

        return {

            "detected": dryup,

            "ratio": round(

                ratio,

                2,

            ),

            "score": round(

                min(

                    score,

                    100,

                ),

                2,

            ),

        }

    # ======================================================
    # AI CONVICTION SCORE
    # ======================================================

    def conviction_score(

        self,

        pattern_score: float,

    ) -> float:

        trend = self.trend_alignment()[

            "score"

        ]

        mtf = self.multi_timeframe_confirmation()[

            "score"

        ]

        breakout = self.breakout_quality()

        volume = self.volume_confirmation()[

            "score"

        ]

        conviction = (

            pattern_score * 0.40 +

            trend * 0.20 +

            mtf * 0.15 +

            breakout * 0.15 +

            volume * 0.10

        )

        return round(

            min(

                conviction,

                100,

            ),

            2,

        )

    # ======================================================
    # INSTITUTIONAL QUALITY FILTER
    # ======================================================

    def institutional_quality_filter(

        self,

    ) -> Dict:

        trend = self.trend_alignment()

        mtf = self.multi_timeframe_confirmation()

        volume = self.volume_confirmation()

        dryup = self.volume_dryup()

        retest = self.breakout_retest()

        false_break = self.false_breakout()

        score = 0

        if trend["bullish"]:

            score += 25

        if mtf["confirmed"]:

            score += 20

        if volume["confirmed"]:

            score += 20

        if dryup["detected"]:

            score += 15

        if retest["detected"]:

            score += 20

        if false_break["detected"]:

            score -= 30

        score = max(

            0,

            min(

                score,

                100,

            ),

        )

        return {

            "institutional_quality": score,

            "approved": score >= 70,

            "trend": trend,

            "multi_timeframe": mtf,

            "volume": volume,

            "volume_dryup": dryup,

            "retest": retest,

            "false_breakout": false_break,

        }
        # ======================================================
    # SMART ENTRY OPTIMIZATION
    # ======================================================

    def optimize_entry(

        self,

        buffer_pct: float = 0.20,

    ) -> Dict:

        resistance = self.high.tail(20).max()

        support = self.low.tail(20).min()

        atr = self.atr().iloc[-1]

        breakout_entry = resistance * (1 + buffer_pct / 100)

        pullback_entry = resistance

        aggressive_entry = self.close.iloc[-1]

        return {

            "aggressive": round(aggressive_entry, 2),

            "breakout": round(breakout_entry, 2),

            "pullback": round(pullback_entry, 2),

            "support": round(support, 2),

            "atr": round(atr, 2),

        }

    # ======================================================
    # DYNAMIC STOP LOSS
    # ======================================================

    def optimized_stop_loss(

        self,

        atr_multiplier: float = 1.50,

    ) -> Dict:

        atr = self.atr().iloc[-1]

        swing_low = self.low.tail(15).min()

        ema20 = self.ema(20).iloc[-1]

        atr_stop = self.close.iloc[-1] - atr * atr_multiplier

        technical_stop = min(

            swing_low,

            ema20,

            atr_stop,

        )

        return {

            "atr_stop": round(atr_stop, 2),

            "technical_stop": round(technical_stop, 2),

            "recommended": round(technical_stop, 2),

        }

    # ======================================================
    # MULTI TARGET PROJECTION
    # ======================================================

    def projected_targets(

        self,

    ) -> Dict:

        atr = self.atr().iloc[-1]

        entry = self.close.iloc[-1]

        return {

            "target1": round(entry + atr * 2, 2),

            "target2": round(entry + atr * 4, 2),

            "target3": round(entry + atr * 6, 2),

        }

    # ======================================================
    # POSITION SIZE CALCULATOR
    # ======================================================

    def position_size(

        self,

        capital: float,

        risk_percent: float = 1.0,

    ) -> Dict:

        stop = self.optimized_stop_loss()["recommended"]

        entry = self.close.iloc[-1]

        risk_amount = capital * (risk_percent / 100)

        risk_per_share = max(

            entry - stop,

            0.01,

        )

        quantity = int(

            risk_amount / risk_per_share

        )

        investment = quantity * entry

        return {

            "capital": capital,

            "risk_amount": round(risk_amount, 2),

            "entry": round(entry, 2),

            "stop": round(stop, 2),

            "risk_per_share": round(risk_per_share, 2),

            "quantity": quantity,

            "investment": round(investment, 2),

        }

    # ======================================================
    # TRADE QUALITY GRADE
    # ======================================================

    def trade_grade(

        self,

        pattern_score: float,

    ) -> str:

        conviction = self.conviction_score(

            pattern_score,

        )

        quality = self.institutional_quality_filter()[

            "institutional_quality"

        ]

        final = (

            conviction * 0.60 +

            quality * 0.40

        )

        if final >= 95:

            return "A+"

        if final >= 90:

            return "A"

        if final >= 80:

            return "B+"

        if final >= 70:

            return "B"

        if final >= 60:

            return "C+"

        if final >= 50:

            return "C"

        return "Avoid"

    # ======================================================
    # SCANNER OUTPUT
    # ======================================================

    def scanner_output(

        self,

    ) -> Dict:

        result = self.analyze()

        quality = self.institutional_quality_filter()

        entry = self.optimize_entry()

        stop = self.optimized_stop_loss()

        targets = self.projected_targets()

        return {

            "Symbol": result.symbol,

            "Pattern": result.pattern.value,

            "Grade": self.trade_grade(

                result.score,

            ),

            "Confidence": result.confidence,

            "AI Score": round(

                self.conviction_score(

                    result.score,

                ),

                2,

            ),

            "Institutional Score":

                quality["institutional_quality"],

            "Entry":

                entry["breakout"],

            "Stop":

                stop["recommended"],

            "Target1":

                targets["target1"],

            "Target2":

                targets["target2"],

            "Target3":

                targets["target3"],

            "RR":

                result.risk_reward,

        }

    # ======================================================
    # DASHBOARD ROW
    # ======================================================

    def dashboard_row(

        self,

    ) -> Dict:

        output = self.scanner_output()

        return {

            "Rank": 0,

            "Stock": output["Symbol"],

            "Pattern": output["Pattern"],

            "Grade": output["Grade"],

            "AI Score": output["AI Score"],

            "Confidence": output["Confidence"],

            "Entry": output["Entry"],

            "SL": output["Stop"],

            "T1": output["Target1"],

            "T2": output["Target2"],

            "RR": output["RR"],

        }

    # ======================================================
    # AI SCANNER PAYLOAD
    # ======================================================

    def scanner_payload(

        self,

    ) -> Dict:

        result = self.analyze()

        institutional = self.institutional_quality_filter()

        return {

            "symbol": result.symbol,

            "pattern": result.pattern.value,

            "pattern_score": result.score,

            "confidence": result.confidence,

            "conviction_score":

                self.conviction_score(

                    result.score,

                ),

            "institutional_score":

                institutional["institutional_quality"],

            "grade":

                self.trade_grade(

                    result.score,

                ),

            "entry":

                self.optimize_entry(),

            "stop":

                self.optimized_stop_loss(),

            "targets":

                self.projected_targets(),

            "warnings":

                result.warnings,

            "reasons":

                result.reasons,

            "dashboard":

                self.dashboard_row(),

        }
        # ======================================================
    # SAFE ANALYSIS
    # ======================================================

    def safe_analyze(

        self,

    ) -> PatternResult:

        try:

            return self.analyze()

        except Exception as e:

            self.result = PatternResult(

                symbol=self.symbol,

                pattern=PatternType.NONE,

                strength=PatternStrength.INVALID,

                confidence=0.0,

                probability=0.0,

                score=0.0,

                breakout_price=0.0,

                entry=0.0,

                stop_loss=0.0,

                target1=0.0,

                target2=0.0,

                risk_reward=0.0,

                reasons=[],

                warnings=[

                    str(e),

                ],

                indicators={},

            )

            return self.result

    # ======================================================
    # BATCH ANALYSIS
    # ======================================================

    @classmethod

    def batch_analyze(

        cls,

        datasets: Dict[str, pd.DataFrame],

    ) -> List[PatternResult]:

        results = []

        for symbol, data in datasets.items():

            try:

                engine = cls()

                engine.load(

                    symbol,

                    data,

                )

                results.append(

                    engine.safe_analyze()

                )

            except Exception:

                continue

        return results

    # ======================================================
    # SORT RESULTS
    # ======================================================

    @staticmethod

    def sort_results(

        results: List[PatternResult],

        by: str = "score",

        descending: bool = True,

    ) -> List[PatternResult]:

        return sorted(

            results,

            key=lambda x: getattr(

                x,

                by,

                0,

            ),

            reverse=descending,

        )

    # ======================================================
    # FILTER RESULTS
    # ======================================================

    @staticmethod

    def filter_results(

        results: List[PatternResult],

        min_score: float = 70,

        min_confidence: float = 70,

    ) -> List[PatternResult]:

        filtered = []

        for result in results:

            if (

                result.score >= min_score

                and

                result.confidence >= min_confidence

            ):

                filtered.append(

                    result

                )

        return filtered

    # ======================================================
    # ENGINE STATISTICS
    # ======================================================

    @staticmethod

    def statistics(

        results: List[PatternResult],

    ) -> Dict:

        if not results:

            return {

                "total": 0,

                "average_score": 0,

                "average_confidence": 0,

                "best_pattern": None,

            }

        avg_score = np.mean(

            [

                r.score

                for r in results

            ]

        )

        avg_confidence = np.mean(

            [

                r.confidence

                for r in results

            ]

        )

        best = max(

            results,

            key=lambda x: x.score,

        )

        return {

            "total":

                len(results),

            "average_score":

                round(avg_score, 2),

            "average_confidence":

                round(avg_confidence, 2),

            "best_pattern":

                best.pattern.value,

            "best_symbol":

                best.symbol,

            "best_score":

                best.score,

        }

    # ======================================================
    # EXPORT SCANNER DATA
    # ======================================================

    @staticmethod

    def scanner_table(

        results: List[PatternResult],

    ) -> List[Dict]:

        table = []

        ranked = sorted(

            results,

            key=lambda x: x.score,

            reverse=True,

        )

        for rank, result in enumerate(

            ranked,

            start=1,

        ):

            table.append(

                {

                    "Rank": rank,

                    "Stock": result.symbol,

                    "Pattern": result.pattern.value,

                    "Strength": result.strength.value,

                    "Score": round(

                        result.score,

                        2,

                    ),

                    "Confidence": round(

                        result.confidence,

                        2,

                    ),

                    "Entry": result.entry,

                    "SL": result.stop_loss,

                    "Target": result.target2,

                    "RR": result.risk_reward,

                }

            )

        return table

    # ======================================================
    # RESET ENGINE
    # ======================================================

    def clear(

        self,

    ):

        self.reset()

    # ======================================================
    # VERSION
    # ======================================================

    @staticmethod

    def version() -> str:

        return "Pattern Recognition Engine v4.0"

    # ======================================================
    # SELF TEST
    # ======================================================

    @staticmethod

    def self_test() -> bool:

        try:

            data = pd.DataFrame(

                {

                    "Open": np.random.rand(300) * 100,

                    "High": np.random.rand(300) * 100 + 2,

                    "Low": np.random.rand(300) * 100 - 2,

                    "Close": np.random.rand(300) * 100,

                    "Volume": np.random.randint(

                        100000,

                        5000000,

                        300,

                    ),

                }

            )

            engine = PatternRecognitionEngine()

            engine.load(

                "TEST",

                data,

            )

            engine.safe_analyze()

            return True

        except Exception:

            return False

    # ======================================================
    # ENGINE INFO
    # ======================================================

    @staticmethod

    def info() -> Dict:

        return {

            "name": "Pattern Recognition Engine",

            "version": "4.0",

            "developer": "StockVersity AI",

            "patterns_supported": 22,

            "features": [

                "Multi Pattern Detection",

                "Institutional Validation",

                "AI Conviction Score",

                "Breakout Intelligence",

                "Trade Planning",

                "Risk Reward Calculation",

                "Scanner Integration",

                "Dashboard Integration",

                "Batch Processing",

            ],

        }