"""
=========================================================
StockVersity Scanner Pro
Indicator Engine
Version : 2.0
=========================================================

Central technical indicator calculation engine.

Calculates:

    • SMA
    • EMA
    • RSI
    • MACD
    • ATR
    • ADX
    • +DI / -DI
    • VWAP
    • Supertrend
    • Relative Volume
    • Bollinger Bands
    • ROC
    • Momentum
    • True Range

Designed to work with StockVersity Scanner Engine.

Expected candle format:

[
    {
        "open": 100.0,
        "high": 105.0,
        "low": 99.0,
        "close": 103.0,
        "volume": 100000
    },
    ...
]

The latest calculated values can be merged directly
into scanner market_data.
=========================================================
"""

from __future__ import annotations

from math import sqrt

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple


# =========================================================
# TYPES
# =========================================================

NumberList = List[float]

Candle = Dict[str, Any]

CandleList = List[Candle]


# =========================================================
# INDICATOR ENGINE
# =========================================================

class IndicatorEngine:
    """
    Central technical indicator engine.

    All calculations use pure Python so the scanner does
    not depend on TA-Lib or pandas-ta.
    """

    VERSION = "2.0"

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        *,
        rsi_period: int = 14,
        atr_period: int = 14,
        adx_period: int = 14,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        supertrend_period: int = 10,
        supertrend_multiplier: float = 3.0,
        volume_period: int = 20,
    ) -> None:

        self.rsi_period = max(
            int(rsi_period),
            1,
        )

        self.atr_period = max(
            int(atr_period),
            1,
        )

        self.adx_period = max(
            int(adx_period),
            1,
        )

        self.macd_fast = max(
            int(macd_fast),
            1,
        )

        self.macd_slow = max(
            int(macd_slow),
            2,
        )

        self.macd_signal_period = max(
            int(macd_signal),
            1,
        )

        self.supertrend_period = max(
            int(supertrend_period),
            1,
        )

        self.supertrend_multiplier = max(
            float(supertrend_multiplier),
            0.1,
        )

        self.volume_period = max(
            int(volume_period),
            1,
        )

        self.debug = False

    # =====================================================
    # SAFE FLOAT
    # =====================================================

    @staticmethod
    def _float(
        value: Any,
        default: float = 0.0,
    ) -> float:

        try:

            if value is None:
                return default

            return float(value)

        except (
            TypeError,
            ValueError,
        ):

            return default

    # =====================================================
    # SAFE INTEGER
    # =====================================================

    @staticmethod
    def _int(
        value: Any,
        default: int = 0,
    ) -> int:

        try:

            if value is None:
                return default

            return int(float(value))

        except (
            TypeError,
            ValueError,
        ):

            return default

    # =====================================================
    # EXTRACT CANDLE SERIES
    # =====================================================

    @classmethod
    def extract_series(
        cls,
        candles: Sequence[Candle],
    ) -> Dict[str, NumberList]:

        opens: NumberList = []

        highs: NumberList = []

        lows: NumberList = []

        closes: NumberList = []

        volumes: NumberList = []

        for candle in candles:

            if not isinstance(
                candle,
                dict,
            ):
                continue

            open_price = cls._float(
                candle.get(
                    "open",
                    candle.get(
                        "open_price",
                        0.0,
                    ),
                )
            )

            high_price = cls._float(
                candle.get(
                    "high",
                    candle.get(
                        "high_price",
                        0.0,
                    ),
                )
            )

            low_price = cls._float(
                candle.get(
                    "low",
                    candle.get(
                        "low_price",
                        0.0,
                    ),
                )
            )

            close_price = cls._float(
                candle.get(
                    "close",
                    candle.get(
                        "close_price",
                        0.0,
                    ),
                )
            )

            volume = cls._float(
                candle.get(
                    "volume",
                    0.0,
                )
            )

            opens.append(
                open_price
            )

            highs.append(
                high_price
            )

            lows.append(
                low_price
            )

            closes.append(
                close_price
            )

            volumes.append(
                volume
            )

        return {

            "open": opens,

            "high": highs,

            "low": lows,

            "close": closes,

            "volume": volumes,

        }

    # =====================================================
    # SMA
    # =====================================================

    @staticmethod
    def sma(
        values: Sequence[float],
        period: int,
    ) -> NumberList:
        """
        Simple Moving Average.
        """

        period = max(
            int(period),
            1,
        )

        size = len(values)

        if size == 0:

            return []

        result: NumberList = [
            0.0
        ] * size

        running_sum = 0.0

        for index, value in enumerate(
            values
        ):

            current = float(value)

            running_sum += current

            if index >= period:

                running_sum -= float(
                    values[
                        index - period
                    ]
                )

            if index >= period - 1:

                result[index] = (
                    running_sum
                    / period
                )

        return result

    # =====================================================
    # EMA
    # =====================================================

    @staticmethod
    def ema(
        values: Sequence[float],
        period: int,
    ) -> NumberList:
        """
        Exponential Moving Average.

        Uses SMA as initial seed.
        """

        period = max(
            int(period),
            1,
        )

        size = len(values)

        if size == 0:

            return []

        result: NumberList = [
            0.0
        ] * size

        if size < period:

            return result

        seed = sum(
            float(value)
            for value in values[:period]
        ) / period

        seed_index = (
            period - 1
        )

        result[
            seed_index
        ] = seed

        multiplier = (
            2.0
            / (
                period + 1.0
            )
        )

        previous = seed

        for index in range(
            period,
            size,
        ):

            current = float(
                values[index]
            )

            current_ema = (

                (
                    current
                    - previous
                )
                * multiplier

                + previous
            )

            result[index] = (
                current_ema
            )

            previous = (
                current_ema
            )

        return result

    # =====================================================
    # RMA / WILDER SMOOTHING
    # =====================================================

    @staticmethod
    def rma(
        values: Sequence[float],
        period: int,
    ) -> NumberList:
        """
        Wilder's moving average.
        """

        period = max(
            int(period),
            1,
        )

        size = len(values)

        if size == 0:

            return []

        result: NumberList = [
            0.0
        ] * size

        if size < period:

            return result

        seed = sum(
            float(value)
            for value in values[:period]
        ) / period

        index = (
            period - 1
        )

        result[index] = seed

        previous = seed

        for index in range(
            period,
            size,
        ):

            current = float(
                values[index]
            )

            smoothed = (

                (
                    previous
                    * (
                        period - 1
                    )
                )

                + current

            ) / period

            result[index] = (
                smoothed
            )

            previous = (
                smoothed
            )

        return result

    # =====================================================
    # TRUE RANGE
    # =====================================================

    @staticmethod
    def true_range(
        highs: Sequence[float],
        lows: Sequence[float],
        closes: Sequence[float],
    ) -> NumberList:

        size = min(
            len(highs),
            len(lows),
            len(closes),
        )

        if size == 0:

            return []

        result: NumberList = [
            0.0
        ] * size

        result[0] = max(

            float(highs[0])
            - float(lows[0]),

            0.0,

        )

        for index in range(
            1,
            size,
        ):

            high = float(
                highs[index]
            )

            low = float(
                lows[index]
            )

            previous_close = float(
                closes[
                    index - 1
                ]
            )

            result[index] = max(

                high - low,

                abs(
                    high
                    - previous_close
                ),

                abs(
                    low
                    - previous_close
                ),

            )

        return result

    # =====================================================
    # ATR
    # =====================================================

    @classmethod
    def atr(
        cls,
        highs: Sequence[float],
        lows: Sequence[float],
        closes: Sequence[float],
        period: int = 14,
    ) -> NumberList:
        """
        Average True Range.
        """

        tr = cls.true_range(
            highs,
            lows,
            closes,
        )

        return cls.rma(
            tr,
            period,
        )

    # =====================================================
    # RSI
    # =====================================================

    @classmethod
    def rsi(
        cls,
        closes: Sequence[float],
        period: int = 14,
    ) -> NumberList:
        """
        Relative Strength Index.
        """

        size = len(closes)

        if size == 0:

            return []

        result: NumberList = [
            0.0
        ] * size

        if size <= period:

            return result

        gains: NumberList = [
            0.0
        ] * size

        losses: NumberList = [
            0.0
        ] * size

        for index in range(
            1,
            size,
        ):

            change = (

                float(
                    closes[index]
                )

                - float(
                    closes[
                        index - 1
                    ]
                )

            )

            if change > 0:

                gains[index] = (
                    change
                )

            elif change < 0:

                losses[index] = (
                    abs(change)
                )

        average_gain = sum(
            gains[
                1:period + 1
            ]
        ) / period

        average_loss = sum(
            losses[
                1:period + 1
            ]
        ) / period

        if average_loss == 0:

            result[period] = (
                100.0
            )

        else:

            rs = (
                average_gain
                / average_loss
            )

            result[period] = (

                100.0

                - (
                    100.0
                    / (
                        1.0 + rs
                    )
                )

            )

        for index in range(
            period + 1,
            size,
        ):

            average_gain = (

                (
                    average_gain
                    * (
                        period - 1
                    )
                )

                + gains[index]

            ) / period

            average_loss = (

                (
                    average_loss
                    * (
                        period - 1
                    )
                )

                + losses[index]

            ) / period

            if average_loss == 0:

                result[index] = (
                    100.0
                )

                continue

            rs = (
                average_gain
                / average_loss
            )

            result[index] = (

                100.0

                - (
                    100.0
                    / (
                        1.0 + rs
                    )
                )

            )

        return result

    # =====================================================
    # MACD
    # =====================================================

    @classmethod
    def macd(
        cls,
        closes: Sequence[float],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> Tuple[
        NumberList,
        NumberList,
        NumberList,
    ]:
        """
        MACD.

        Returns:
            macd_line
            signal_line
            histogram
        """

        size = len(closes)

        if size == 0:

            return (
                [],
                [],
                [],
            )

        fast = cls.ema(
            closes,
            fast_period,
        )

        slow = cls.ema(
            closes,
            slow_period,
        )

        macd_line: NumberList = [
            0.0
        ] * size

        for index in range(
            size
        ):

            if (
                fast[index] != 0.0
                and slow[index] != 0.0
            ):

                macd_line[index] = (

                    fast[index]
                    - slow[index]

                )

        # -------------------------------------------------
        # Calculate EMA only from valid MACD section
        # -------------------------------------------------

        start_index = max(
            slow_period - 1,
            0,
        )

        valid_macd = (
            macd_line[
                start_index:
            ]
        )

        valid_signal = cls.ema(
            valid_macd,
            signal_period,
        )

        signal_line: NumberList = [
            0.0
        ] * size

        for offset, value in enumerate(
            valid_signal
        ):

            target_index = (
                start_index
                + offset
            )

            if target_index < size:

                signal_line[
                    target_index
                ] = value

        histogram: NumberList = [
            0.0
        ] * size

        for index in range(
            size
        ):

            if (
                macd_line[index] != 0.0
                and signal_line[index] != 0.0
            ):

                histogram[index] = (

                    macd_line[index]
                    - signal_line[index]

                )

        return (

            macd_line,

            signal_line,

            histogram,

        )

    # =====================================================
    # DIRECTIONAL MOVEMENT
    # =====================================================

    @classmethod
    def directional_movement(
        cls,
        highs: Sequence[float],
        lows: Sequence[float],
    ) -> Tuple[
        NumberList,
        NumberList,
    ]:

        size = min(
            len(highs),
            len(lows),
        )

        plus_dm: NumberList = [
            0.0
        ] * size

        minus_dm: NumberList = [
            0.0
        ] * size

        for index in range(
            1,
            size,
        ):

            up_move = (

                float(
                    highs[index]
                )

                - float(
                    highs[
                        index - 1
                    ]
                )

            )

            down_move = (

                float(
                    lows[
                        index - 1
                    ]
                )

                - float(
                    lows[index]
                )

            )

            if (
                up_move > down_move
                and up_move > 0
            ):

                plus_dm[index] = (
                    up_move
                )

            if (
                down_move > up_move
                and down_move > 0
            ):

                minus_dm[index] = (
                    down_move
                )

        return (
            plus_dm,
            minus_dm,
        )

    # =====================================================
    # ADX / +DI / -DI
    # =====================================================

    @classmethod
    def adx(
        cls,
        highs: Sequence[float],
        lows: Sequence[float],
        closes: Sequence[float],
        period: int = 14,
    ) -> Tuple[
        NumberList,
        NumberList,
        NumberList,
    ]:
        """
        Average Directional Index.

        Returns:
            ADX
            +DI
            -DI
        """

        size = min(
            len(highs),
            len(lows),
            len(closes),
        )

        if size == 0:

            return (
                [],
                [],
                [],
            )

        tr = cls.true_range(
            highs,
            lows,
            closes,
        )

        plus_dm, minus_dm = (
            cls.directional_movement(
                highs,
                lows,
            )
        )

        atr_values = cls.rma(
            tr,
            period,
        )

        smooth_plus = cls.rma(
            plus_dm,
            period,
        )

        smooth_minus = cls.rma(
            minus_dm,
            period,
        )

        plus_di: NumberList = [
            0.0
        ] * size

        minus_di: NumberList = [
            0.0
        ] * size

        dx: NumberList = [
            0.0
        ] * size

        for index in range(
            size
        ):

            current_atr = (
                atr_values[index]
            )

            if current_atr <= 0:
                continue

            plus_di[index] = (

                100.0

                * smooth_plus[index]

                / current_atr

            )

            minus_di[index] = (

                100.0

                * smooth_minus[index]

                / current_atr

            )

            denominator = (

                plus_di[index]
                + minus_di[index]

            )

            if denominator <= 0:
                continue

            dx[index] = (

                100.0

                * abs(
                    plus_di[index]
                    - minus_di[index]
                )

                / denominator

            )

        # -------------------------------------------------
        # ADX needs smoothing from valid DX region
        # -------------------------------------------------

        adx_values: NumberList = [
            0.0
        ] * size

        first_dx = (
            period - 1
        )

        valid_dx = (
            dx[
                first_dx:
            ]
        )

        smoothed_dx = cls.rma(
            valid_dx,
            period,
        )

        for offset, value in enumerate(
            smoothed_dx
        ):

            index = (
                first_dx
                + offset
            )

            if index < size:

                adx_values[
                    index
                ] = value

        return (

            adx_values,

            plus_di,

            minus_di,

        )

    # =====================================================
    # VWAP
    # =====================================================

    @staticmethod
    def vwap(
        highs: Sequence[float],
        lows: Sequence[float],
        closes: Sequence[float],
        volumes: Sequence[float],
    ) -> NumberList:
        """
        Cumulative session VWAP.

        IMPORTANT:
        Candle list should contain one trading session when
        using this function for intraday scanning.
        """

        size = min(
            len(highs),
            len(lows),
            len(closes),
            len(volumes),
        )

        result: NumberList = [
            0.0
        ] * size

        cumulative_price_volume = (
            0.0
        )

        cumulative_volume = 0.0

        for index in range(
            size
        ):

            typical_price = (

                float(
                    highs[index]
                )

                + float(
                    lows[index]
                )

                + float(
                    closes[index]
                )

            ) / 3.0

            volume = max(
                float(
                    volumes[index]
                ),
                0.0,
            )

            cumulative_price_volume += (
                typical_price
                * volume
            )

            cumulative_volume += (
                volume
            )

            if cumulative_volume > 0:

                result[index] = (

                    cumulative_price_volume
                    / cumulative_volume

                )

        return result

    # =====================================================
    # BOLLINGER BANDS
    # =====================================================

    @staticmethod
    def bollinger_bands(
        closes: Sequence[float],
        period: int = 20,
        deviation: float = 2.0,
    ) -> Tuple[
        NumberList,
        NumberList,
        NumberList,
    ]:

        period = max(
            int(period),
            1,
        )

        size = len(closes)

        middle: NumberList = [
            0.0
        ] * size

        upper: NumberList = [
            0.0
        ] * size

        lower: NumberList = [
            0.0
        ] * size

        if size < period:

            return (
                upper,
                middle,
                lower,
            )

        for index in range(
            period - 1,
            size,
        ):

            window = [

                float(value)

                for value in closes[
                    index
                    - period
                    + 1:
                    index
                    + 1
                ]

            ]

            mean = (
                sum(window)
                / period
            )

            variance = (

                sum(
                    (
                        value
                        - mean
                    ) ** 2
                    for value in window
                )

                / period

            )

            standard_deviation = sqrt(
                variance
            )

            middle[index] = mean

            upper[index] = (

                mean
                + deviation
                * standard_deviation

            )

            lower[index] = (

                mean
                - deviation
                * standard_deviation

            )

        return (
            upper,
            middle,
            lower,
        )

    # =====================================================
    # RATE OF CHANGE
    # =====================================================

    @staticmethod
    def roc(
        closes: Sequence[float],
        period: int = 10,
    ) -> NumberList:

        period = max(
            int(period),
            1,
        )

        size = len(closes)

        result: NumberList = [
            0.0
        ] * size

        for index in range(
            period,
            size,
        ):

            previous = float(
                closes[
                    index - period
                ]
            )

            if previous == 0:
                continue

            result[index] = (

                (
                    float(
                        closes[index]
                    )

                    - previous

                )

                / previous

            ) * 100.0

        return result

    # =====================================================
    # MOMENTUM
    # =====================================================

    @staticmethod
    def momentum(
        closes: Sequence[float],
        period: int = 10,
    ) -> NumberList:

        period = max(
            int(period),
            1,
        )

        size = len(closes)

        result: NumberList = [
            0.0
        ] * size

        for index in range(
            period,
            size,
        ):

            result[index] = (

                float(
                    closes[index]
                )

                - float(
                    closes[
                        index - period
                    ]
                )

            )

        return result

    # =====================================================
    # RELATIVE VOLUME
    # =====================================================

    @staticmethod
    def relative_volume(
        volumes: Sequence[float],
        period: int = 20,
    ) -> NumberList:
        """
        Current volume divided by average previous volume.

        Current candle is excluded from the historical
        average to avoid look-ahead distortion.
        """

        period = max(
            int(period),
            1,
        )

        size = len(volumes)

        result: NumberList = [
            0.0
        ] * size

        if size <= period:

            return result

        running_sum = sum(

            float(value)

            for value in volumes[
                :period
            ]

        )

        for index in range(
            period,
            size,
        ):

            average = (
                running_sum
                / period
            )

            current_volume = float(
                volumes[index]
            )

            if average > 0:

                result[index] = (

                    current_volume
                    / average

                )

            running_sum -= float(
                volumes[
                    index - period
                ]
            )

            running_sum += (
                current_volume
            )

        return result

    # =====================================================
    # SUPERTREND
    # =====================================================

    @classmethod
    def supertrend(
        cls,
        highs: Sequence[float],
        lows: Sequence[float],
        closes: Sequence[float],
        period: int = 10,
        multiplier: float = 3.0,
    ) -> Tuple[
        NumberList,
        List[int],
    ]:
        """
        Supertrend indicator.

        Direction:
             1 = bullish
            -1 = bearish
             0 = unavailable
        """

        size = min(
            len(highs),
            len(lows),
            len(closes),
        )

        supertrend_values: NumberList = [
            0.0
        ] * size

        directions: List[int] = [
            0
        ] * size

        if size == 0:

            return (
                supertrend_values,
                directions,
            )

        atr_values = cls.atr(
            highs,
            lows,
            closes,
            period,
        )

        basic_upper: NumberList = [
            0.0
        ] * size

        basic_lower: NumberList = [
            0.0
        ] * size

        final_upper: NumberList = [
            0.0
        ] * size

        final_lower: NumberList = [
            0.0
        ] * size

        for index in range(
            size
        ):

            atr_value = (
                atr_values[index]
            )

            if atr_value <= 0:
                continue

            midpoint = (

                float(
                    highs[index]
                )

                + float(
                    lows[index]
                )

            ) / 2.0

            basic_upper[index] = (

                midpoint
                + multiplier
                * atr_value

            )

            basic_lower[index] = (

                midpoint
                - multiplier
                * atr_value

            )

        start = (
            period - 1
        )

        if start >= size:

            return (
                supertrend_values,
                directions,
            )

        if (
            atr_values[start]
            <= 0
        ):

            return (
                supertrend_values,
                directions,
            )

        final_upper[start] = (
            basic_upper[start]
        )

        final_lower[start] = (
            basic_lower[start]
        )

        # Initial trend determination

        if (
            float(
                closes[start]
            )
            >= final_lower[start]
        ):

            directions[start] = 1

            supertrend_values[
                start
            ] = final_lower[start]

        else:

            directions[start] = -1

            supertrend_values[
                start
            ] = final_upper[start]

        for index in range(
            start + 1,
            size,
        ):

            if atr_values[index] <= 0:
                continue

            previous_close = float(
                closes[
                    index - 1
                ]
            )

            # ---------------------------------------------
            # Final upper band
            # ---------------------------------------------

            if (
                basic_upper[index]
                < final_upper[
                    index - 1
                ]
                or previous_close
                > final_upper[
                    index - 1
                ]
            ):

                final_upper[index] = (
                    basic_upper[index]
                )

            else:

                final_upper[index] = (
                    final_upper[
                        index - 1
                    ]
                )

            # ---------------------------------------------
            # Final lower band
            # ---------------------------------------------

            if (
                basic_lower[index]
                > final_lower[
                    index - 1
                ]
                or previous_close
                < final_lower[
                    index - 1
                ]
            ):

                final_lower[index] = (
                    basic_lower[index]
                )

            else:

                final_lower[index] = (
                    final_lower[
                        index - 1
                    ]
                )

            close = float(
                closes[index]
            )

            previous_direction = (
                directions[
                    index - 1
                ]
            )

            # ---------------------------------------------
            # Direction switch
            # ---------------------------------------------

            if previous_direction >= 0:

                if (
                    close
                    < final_lower[index]
                ):

                    directions[index] = -1

                    supertrend_values[
                        index
                    ] = final_upper[index]

                else:

                    directions[index] = 1

                    supertrend_values[
                        index
                    ] = final_lower[index]

            else:

                if (
                    close
                    > final_upper[index]
                ):

                    directions[index] = 1

                    supertrend_values[
                        index
                    ] = final_lower[index]

                else:

                    directions[index] = -1

                    supertrend_values[
                        index
                    ] = final_upper[index]

        return (
            supertrend_values,
            directions,
        )

    # =====================================================
    # CALCULATE ALL INDICATORS
    # =====================================================

    def calculate(
        self,
        candles: Sequence[Candle],
    ) -> Dict[str, Any]:
        """
        Calculate all indicators for a candle series.

        Returns latest values plus selected series.
        """

        if not candles:

            return {}

        series = self.extract_series(
            candles
        )

        opens = series["open"]

        highs = series["high"]

        lows = series["low"]

        closes = series["close"]

        volumes = series["volume"]

        if not closes:

            return {}

        # -------------------------------------------------
        # Moving averages
        # -------------------------------------------------

        ema9_values = self.ema(
            closes,
            9,
        )

        ema20_values = self.ema(
            closes,
            20,
        )

        ema21_values = self.ema(
            closes,
            21,
        )

        ema50_values = self.ema(
            closes,
            50,
        )

        ema100_values = self.ema(
            closes,
            100,
        )

        ema200_values = self.ema(
            closes,
            200,
        )

        sma20_values = self.sma(
            closes,
            20,
        )

        sma50_values = self.sma(
            closes,
            50,
        )

        sma200_values = self.sma(
            closes,
            200,
        )

        # -------------------------------------------------
        # RSI
        # -------------------------------------------------

        rsi_values = self.rsi(
            closes,
            self.rsi_period,
        )

        # -------------------------------------------------
        # MACD
        # -------------------------------------------------

        (
            macd_values,
            macd_signal_values,
            macd_histogram_values,
        ) = self.macd(

            closes,

            self.macd_fast,

            self.macd_slow,

            self.macd_signal_period,

        )

        # -------------------------------------------------
        # ATR
        # -------------------------------------------------

        atr_values = self.atr(

            highs,

            lows,

            closes,

            self.atr_period,

        )

        # -------------------------------------------------
        # ADX
        # -------------------------------------------------

        (
            adx_values,
            plus_di_values,
            minus_di_values,
        ) = self.adx(

            highs,

            lows,

            closes,

            self.adx_period,

        )

        # -------------------------------------------------
        # VWAP
        # -------------------------------------------------

        vwap_values = self.vwap(

            highs,

            lows,

            closes,

            volumes,

        )

        # -------------------------------------------------
        # Supertrend
        # -------------------------------------------------

        (
            supertrend_values,
            supertrend_directions,
        ) = self.supertrend(

            highs,

            lows,

            closes,

            self.supertrend_period,

            self.supertrend_multiplier,

        )

        # -------------------------------------------------
        # Relative volume
        # -------------------------------------------------

        rvol_values = (
            self.relative_volume(

                volumes,

                self.volume_period,

            )
        )

        # -------------------------------------------------
        # Bollinger
        # -------------------------------------------------

        (
            bb_upper,
            bb_middle,
            bb_lower,
        ) = self.bollinger_bands(

            closes,

            20,

            2.0,

        )

        # -------------------------------------------------
        # ROC / Momentum
        # -------------------------------------------------

        roc_values = self.roc(
            closes,
            10,
        )

        momentum_values = (
            self.momentum(
                closes,
                10,
            )
        )

        # -------------------------------------------------
        # Latest index
        # -------------------------------------------------

        index = (
            len(closes) - 1
        )

        previous_close = 0.0

        if index > 0:

            previous_close = (
                closes[
                    index - 1
                ]
            )

        # -------------------------------------------------
        # Average volume
        # -------------------------------------------------

        average_volume = (
            self._average_previous_volume(
                volumes,
                self.volume_period,
            )
        )

        # -------------------------------------------------
        # Result
        # -------------------------------------------------

        result: Dict[str, Any] = {

            # ---------------------------------------------
            # Price
            # ---------------------------------------------

            "open": self._latest(
                opens
            ),

            "high": self._latest(
                highs
            ),

            "low": self._latest(
                lows
            ),

            "close": self._latest(
                closes
            ),

            "last_price": self._latest(
                closes
            ),

            "previous_close": (
                previous_close
            ),

            # ---------------------------------------------
            # Volume
            # ---------------------------------------------

            "volume": int(
                self._latest(
                    volumes
                )
            ),

            "average_volume": int(
                average_volume
            ),

            "volume_ratio": round(
                self._latest(
                    rvol_values
                ),
                4,
            ),

            # ---------------------------------------------
            # EMA
            # ---------------------------------------------

            "ema9": round(
                self._latest(
                    ema9_values
                ),
                4,
            ),

            "ema20": round(
                self._latest(
                    ema20_values
                ),
                4,
            ),

            "ema21": round(
                self._latest(
                    ema21_values
                ),
                4,
            ),

            "ema50": round(
                self._latest(
                    ema50_values
                ),
                4,
            ),

            "ema100": round(
                self._latest(
                    ema100_values
                ),
                4,
            ),

            "ema200": round(
                self._latest(
                    ema200_values
                ),
                4,
            ),

            # ---------------------------------------------
            # SMA
            # ---------------------------------------------

            "sma20": round(
                self._latest(
                    sma20_values
                ),
                4,
            ),

            "sma50": round(
                self._latest(
                    sma50_values
                ),
                4,
            ),

            "sma200": round(
                self._latest(
                    sma200_values
                ),
                4,
            ),

            # ---------------------------------------------
            # RSI
            # ---------------------------------------------

            "rsi": round(
                self._latest(
                    rsi_values
                ),
                4,
            ),

            # ---------------------------------------------
            # MACD
            # ---------------------------------------------

            "macd": round(
                self._latest(
                    macd_values
                ),
                4,
            ),

            "macd_signal": round(
                self._latest(
                    macd_signal_values
                ),
                4,
            ),

            "macd_histogram": round(
                self._latest(
                    macd_histogram_values
                ),
                4,
            ),

            # ---------------------------------------------
            # ATR
            # ---------------------------------------------

            "atr": round(
                self._latest(
                    atr_values
                ),
                4,
            ),

            # ---------------------------------------------
            # ADX
            # ---------------------------------------------

            "adx": round(
                self._latest(
                    adx_values
                ),
                4,
            ),

            "plus_di": round(
                self._latest(
                    plus_di_values
                ),
                4,
            ),

            "minus_di": round(
                self._latest(
                    minus_di_values
                ),
                4,
            ),

            # ---------------------------------------------
            # VWAP
            # ---------------------------------------------

            "vwap": round(
                self._latest(
                    vwap_values
                ),
                4,
            ),

            # ---------------------------------------------
            # Supertrend
            # ---------------------------------------------

            "supertrend": round(
                self._latest(
                    supertrend_values
                ),
                4,
            ),

            "supertrend_direction": int(
                self._latest(
                    supertrend_directions
                )
            ),

            # ---------------------------------------------
            # Bollinger Bands
            # ---------------------------------------------

            "bb_upper": round(
                self._latest(
                    bb_upper
                ),
                4,
            ),

            "bb_middle": round(
                self._latest(
                    bb_middle
                ),
                4,
            ),

            "bb_lower": round(
                self._latest(
                    bb_lower
                ),
                4,
            ),

            # ---------------------------------------------
            # Momentum
            # ---------------------------------------------

            "roc": round(
                self._latest(
                    roc_values
                ),
                4,
            ),

            "momentum": round(
                self._latest(
                    momentum_values
                ),
                4,
            ),

            # ---------------------------------------------
            # Diagnostics
            # ---------------------------------------------

            "candle_count": len(
                closes
            ),

            "indicators_ready": (
                self._indicators_ready(
                    len(closes)
                )
            ),

        }

        return result

    # =====================================================
    # CALCULATE WITH SERIES
    # =====================================================

    def calculate_full(
        self,
        candles: Sequence[Candle],
    ) -> Dict[str, Any]:
        """
        Calculate indicators and return full indicator series.

        Useful for charting and pattern scanners.
        """

        if not candles:

            return {}

        series = self.extract_series(
            candles
        )

        highs = series["high"]

        lows = series["low"]

        closes = series["close"]

        volumes = series["volume"]

        if not closes:

            return {}

        ema9 = self.ema(
            closes,
            9,
        )

        ema20 = self.ema(
            closes,
            20,
        )

        ema21 = self.ema(
            closes,
            21,
        )

        ema50 = self.ema(
            closes,
            50,
        )

        ema100 = self.ema(
            closes,
            100,
        )

        ema200 = self.ema(
            closes,
            200,
        )

        rsi = self.rsi(
            closes,
            self.rsi_period,
        )

        (
            macd,
            macd_signal,
            macd_histogram,
        ) = self.macd(

            closes,

            self.macd_fast,

            self.macd_slow,

            self.macd_signal_period,

        )

        atr = self.atr(

            highs,

            lows,

            closes,

            self.atr_period,

        )

        (
            adx,
            plus_di,
            minus_di,
        ) = self.adx(

            highs,

            lows,

            closes,

            self.adx_period,

        )

        vwap = self.vwap(

            highs,

            lows,

            closes,

            volumes,

        )

        (
            supertrend,
            supertrend_direction,
        ) = self.supertrend(

            highs,

            lows,

            closes,

            self.supertrend_period,

            self.supertrend_multiplier,

        )

        volume_ratio = (
            self.relative_volume(

                volumes,

                self.volume_period,

            )
        )

        (
            bb_upper,
            bb_middle,
            bb_lower,
        ) = self.bollinger_bands(

            closes,

            20,

            2.0,

        )

        return {

            "price": series,

            "ema9": ema9,

            "ema20": ema20,

            "ema21": ema21,

            "ema50": ema50,

            "ema100": ema100,

            "ema200": ema200,

            "rsi": rsi,

            "macd": macd,

            "macd_signal": (
                macd_signal
            ),

            "macd_histogram": (
                macd_histogram
            ),

            "atr": atr,

            "adx": adx,

            "plus_di": plus_di,

            "minus_di": minus_di,

            "vwap": vwap,

            "supertrend": (
                supertrend
            ),

            "supertrend_direction": (
                supertrend_direction
            ),

            "volume_ratio": (
                volume_ratio
            ),

            "bb_upper": bb_upper,

            "bb_middle": bb_middle,

            "bb_lower": bb_lower,

            "roc": self.roc(
                closes,
                10,
            ),

            "momentum": self.momentum(
                closes,
                10,
            ),

        }

    # =====================================================
    # ENRICH MARKET DATA
    # =====================================================

    def enrich(
        self,
        market_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Add calculated indicators to one symbol's market data.

        Expected:

        {
            "symbol": "RELIANCE",
            "instrument_key": "...",
            "candles": [...]
        }

        Existing metadata is preserved.
        """

        if not isinstance(
            market_data,
            dict,
        ):

            return {}

        enriched = dict(
            market_data
        )

        candles = market_data.get(
            "candles",
            [],
        )

        if not isinstance(
            candles,
            (list, tuple),
        ):

            return enriched

        indicators = self.calculate(
            candles
        )

        enriched.update(
            indicators
        )

        return enriched

    # =====================================================
    # ENRICH UNIVERSE
    # =====================================================

    def enrich_universe(
        self,
        universe: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Enrich complete scanner universe.

        Input:

        {
            "RELIANCE": {
                "instrument_key": "...",
                "candles": [...]
            },

            "TCS": {
                ...
            }
        }
        """

        enriched: Dict[
            str,
            Any
        ] = {}

        for symbol, data in (
            universe.items()
        ):

            if not isinstance(
                data,
                dict,
            ):

                continue

            try:

                row = self.enrich(
                    data
                )

                row.setdefault(
                    "symbol",
                    symbol,
                )

                enriched[
                    symbol
                ] = row

            except Exception as exc:

                self.log(
                    "Indicator calculation failed:",
                    symbol,
                    exc,
                )

                row = dict(data)

                row.setdefault(
                    "symbol",
                    symbol,
                )

                enriched[
                    symbol
                ] = row

        return enriched

    # =====================================================
    # AVERAGE PREVIOUS VOLUME
    # =====================================================

    @staticmethod
    def _average_previous_volume(
        volumes: Sequence[float],
        period: int,
    ) -> float:

        if not volumes:

            return 0.0

        if len(volumes) == 1:

            return 0.0

        historical = list(
            volumes[:-1]
        )

        if not historical:

            return 0.0

        sample = historical[
            -period:
        ]

        if not sample:

            return 0.0

        return (

            sum(
                float(value)
                for value in sample
            )

            / len(sample)

        )

    # =====================================================
    # LATEST VALUE
    # =====================================================

    @staticmethod
    def _latest(
        values: Sequence[Any],
        default: float = 0.0,
    ) -> Any:

        if not values:

            return default

        value = values[-1]

        if value is None:

            return default

        return value

    # =====================================================
    # INDICATOR READINESS
    # =====================================================

    @staticmethod
    def _indicators_ready(
        candle_count: int,
    ) -> bool:
        """
        Full scanner indicator set needs enough history
        for EMA200.
        """

        return candle_count >= 200

    # =====================================================
    # MINIMUM HISTORY
    # =====================================================

    @property
    def minimum_history(
        self,
    ) -> int:
        """
        Recommended number of candles.

        250 gives enough warm-up for EMA200.
        """

        return 250

    # =====================================================
    # CONFIGURATION
    # =====================================================

    def configure(
        self,
        *,
        rsi_period: Optional[
            int
        ] = None,
        atr_period: Optional[
            int
        ] = None,
        adx_period: Optional[
            int
        ] = None,
        macd_fast: Optional[
            int
        ] = None,
        macd_slow: Optional[
            int
        ] = None,
        macd_signal: Optional[
            int
        ] = None,
        supertrend_period: Optional[
            int
        ] = None,
        supertrend_multiplier: Optional[
            float
        ] = None,
        volume_period: Optional[
            int
        ] = None,
    ) -> "IndicatorEngine":

        if rsi_period is not None:

            self.rsi_period = max(
                int(
                    rsi_period
                ),
                1,
            )

        if atr_period is not None:

            self.atr_period = max(
                int(
                    atr_period
                ),
                1,
            )

        if adx_period is not None:

            self.adx_period = max(
                int(
                    adx_period
                ),
                1,
            )

        if macd_fast is not None:

            self.macd_fast = max(
                int(
                    macd_fast
                ),
                1,
            )

        if macd_slow is not None:

            self.macd_slow = max(
                int(
                    macd_slow
                ),
                2,
            )

        if macd_signal is not None:

            self.macd_signal_period = max(
                int(
                    macd_signal
                ),
                1,
            )

        if (
            supertrend_period
            is not None
        ):

            self.supertrend_period = max(
                int(
                    supertrend_period
                ),
                1,
            )

        if (
            supertrend_multiplier
            is not None
        ):

            self.supertrend_multiplier = max(
                float(
                    supertrend_multiplier
                ),
                0.1,
            )

        if volume_period is not None:

            self.volume_period = max(
                int(
                    volume_period
                ),
                1,
            )

        return self

    # =====================================================
    # SCALPING PRESET
    # =====================================================

    def use_scalping_preset(
        self,
    ) -> "IndicatorEngine":
        """
        Faster settings for 1m / 3m / 5m intraday scanning.
        """

        self.rsi_period = 9

        self.atr_period = 10

        self.adx_period = 14

        self.macd_fast = 8

        self.macd_slow = 21

        self.macd_signal_period = 5

        self.supertrend_period = 10

        self.supertrend_multiplier = (
            2.0
        )

        self.volume_period = 20

        return self

    # =====================================================
    # STANDARD INTRADAY PRESET
    # =====================================================

    def use_intraday_preset(
        self,
    ) -> "IndicatorEngine":
        """
        Standard StockVersity intraday configuration.
        """

        self.rsi_period = 14

        self.atr_period = 14

        self.adx_period = 14

        self.macd_fast = 12

        self.macd_slow = 26

        self.macd_signal_period = 9

        self.supertrend_period = 10

        self.supertrend_multiplier = (
            3.0
        )

        self.volume_period = 20

        return self

    # =====================================================
    # INFO
    # =====================================================

    def info(
        self,
    ) -> Dict[str, Any]:

        return {

            "engine": (
                "StockVersity Indicator Engine"
            ),

            "version": self.VERSION,

            "rsi_period": (
                self.rsi_period
            ),

            "atr_period": (
                self.atr_period
            ),

            "adx_period": (
                self.adx_period
            ),

            "macd": {

                "fast": (
                    self.macd_fast
                ),

                "slow": (
                    self.macd_slow
                ),

                "signal": (
                    self.macd_signal_period
                ),

            },

            "supertrend": {

                "period": (
                    self.supertrend_period
                ),

                "multiplier": (
                    self.supertrend_multiplier
                ),

            },

            "volume_period": (
                self.volume_period
            ),

            "minimum_history": (
                self.minimum_history
            ),

        }

    # =====================================================
    # DEBUG
    # =====================================================

    def enable_debug(
        self,
    ) -> None:

        self.debug = True

    def disable_debug(
        self,
    ) -> None:

        self.debug = False

    def log(
        self,
        *message: Any,
    ) -> None:

        if not self.debug:

            return

        print(
            "[IndicatorEngine]",
            *message,
        )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (

            "IndicatorEngine("

            f"rsi={self.rsi_period}, "

            f"atr={self.atr_period}, "

            f"adx={self.adx_period}, "

            f"macd="
            f"{self.macd_fast}/"
            f"{self.macd_slow}/"
            f"{self.macd_signal_period}, "

            f"supertrend="
            f"{self.supertrend_period}/"
            f"{self.supertrend_multiplier}"

            ")"

        )


# =========================================================
# FACTORY
# =========================================================

def create_indicator_engine(
    *,
    preset: str = "intraday",
) -> IndicatorEngine:
    """
    Create configured indicator engine.

    preset:
        intraday
        scalping
        default
    """

    engine = IndicatorEngine()

    preset = (
        preset
        .lower()
        .strip()
    )

    if preset == "scalping":

        engine.use_scalping_preset()

    elif preset == "intraday":

        engine.use_intraday_preset()

    return engine


# =========================================================
# CONVENIENCE FUNCTION
# =========================================================

def calculate_indicators(
    candles: Sequence[Candle],
) -> Dict[str, Any]:
    """
    Quick calculation helper.

    Example:

        indicators = calculate_indicators(candles)
    """

    engine = (
        create_indicator_engine()
    )

    return engine.calculate(
        candles
    )


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "IndicatorEngine",

    "create_indicator_engine",

    "calculate_indicators",

]


# ==========================
# END OF FILE
# ==========================