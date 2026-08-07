"""
=========================================================
StockVersity Scanner Pro
Technical Indicators
Version : 2.0
=========================================================

Shared technical indicator calculations for scanners.

Indicators
----------
• SMA
• EMA
• RSI
• MACD
• True Range
• ATR
• VWAP
• Bollinger Bands
• ADX / +DI / -DI
• Supertrend
• ROC
• Momentum
• Highest / Lowest
• Volume SMA / RVOL

This module contains calculations only.
It DOES NOT generate trading signals.
=========================================================
"""

from __future__ import annotations

from math import sqrt

from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple


# =========================================================
# TYPES
# =========================================================

NumberSeries = Sequence[float]


# =========================================================
# SAFE FLOAT
# =========================================================

def _float(
    value,
    default: float = 0.0,
) -> float:

    try:
        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return default


# =========================================================
# VALID PERIOD
# =========================================================

def _valid_period(
    period: int,
) -> int:

    return max(
        int(period),
        1,
    )


# =========================================================
# FLOAT SERIES
# =========================================================

def _series(
    values: NumberSeries,
) -> List[float]:

    return [
        _float(value)
        for value in values
    ]


# =========================================================
# SMA
# =========================================================

def sma(
    values: NumberSeries,
    period: int,
) -> Optional[float]:
    """
    Latest Simple Moving Average.
    """

    period = _valid_period(
        period
    )

    data = _series(
        values
    )

    if len(data) < period:
        return None

    window = data[
        -period:
    ]

    return round(
        sum(window)
        / period,
        4,
    )


# =========================================================
# SMA SERIES
# =========================================================

def sma_series(
    values: NumberSeries,
    period: int,
) -> List[Optional[float]]:

    period = _valid_period(
        period
    )

    data = _series(
        values
    )

    result: List[
        Optional[float]
    ] = [
        None
    ] * len(data)

    if len(data) < period:
        return result

    running_sum = sum(
        data[:period]
    )

    result[
        period - 1
    ] = round(
        running_sum / period,
        4,
    )

    for index in range(
        period,
        len(data),
    ):

        running_sum += (
            data[index]
            - data[
                index - period
            ]
        )

        result[
            index
        ] = round(
            running_sum / period,
            4,
        )

    return result


# =========================================================
# EMA SERIES
# =========================================================

def ema_series(
    values: NumberSeries,
    period: int,
) -> List[Optional[float]]:
    """
    Exponential Moving Average series.

    Initial EMA is seeded using SMA.
    """

    period = _valid_period(
        period
    )

    data = _series(
        values
    )

    result: List[
        Optional[float]
    ] = [
        None
    ] * len(data)

    if len(data) < period:
        return result

    seed = (
        sum(
            data[:period]
        )
        / period
    )

    seed_index = (
        period - 1
    )

    result[
        seed_index
    ] = round(
        seed,
        4,
    )

    multiplier = (
        2.0
        / (
            period + 1
        )
    )

    previous = seed

    for index in range(
        period,
        len(data),
    ):

        current = (

            (
                data[index]
                - previous
            )
            * multiplier
            + previous

        )

        result[
            index
        ] = round(
            current,
            4,
        )

        previous = current

    return result


# =========================================================
# EMA
# =========================================================

def ema(
    values: NumberSeries,
    period: int,
) -> Optional[float]:
    """
    Latest Exponential Moving Average.
    """

    result = ema_series(
        values,
        period,
    )

    if not result:
        return None

    return result[-1]


# =========================================================
# HIGHEST
# =========================================================

def highest(
    values: NumberSeries,
    period: Optional[int] = None,
) -> Optional[float]:

    data = _series(
        values
    )

    if not data:
        return None

    if period is not None:

        period = _valid_period(
            period
        )

        if len(data) < period:
            return None

        data = data[
            -period:
        ]

    return max(
        data
    )


# =========================================================
# LOWEST
# =========================================================

def lowest(
    values: NumberSeries,
    period: Optional[int] = None,
) -> Optional[float]:

    data = _series(
        values
    )

    if not data:
        return None

    if period is not None:

        period = _valid_period(
            period
        )

        if len(data) < period:
            return None

        data = data[
            -period:
        ]

    return min(
        data
    )


# =========================================================
# RSI SERIES
# =========================================================

def rsi_series(
    closes: NumberSeries,
    period: int = 14,
) -> List[Optional[float]]:
    """
    Wilder RSI series.
    """

    period = _valid_period(
        period
    )

    data = _series(
        closes
    )

    result: List[
        Optional[float]
    ] = [
        None
    ] * len(data)

    if len(data) <= period:
        return result

    gains: List[float] = []

    losses: List[float] = []

    for index in range(
        1,
        period + 1,
    ):

        change = (
            data[index]
            - data[index - 1]
        )

        gains.append(
            max(
                change,
                0.0,
            )
        )

        losses.append(
            max(
                -change,
                0.0,
            )
        )

    average_gain = (
        sum(gains)
        / period
    )

    average_loss = (
        sum(losses)
        / period
    )

    if average_loss == 0:

        first_rsi = 100.0

    else:

        rs = (
            average_gain
            / average_loss
        )

        first_rsi = (

            100.0
            - (
                100.0
                / (
                    1.0 + rs
                )
            )

        )

    result[
        period
    ] = round(
        first_rsi,
        2,
    )

    for index in range(
        period + 1,
        len(data),
    ):

        change = (
            data[index]
            - data[index - 1]
        )

        gain = max(
            change,
            0.0,
        )

        loss = max(
            -change,
            0.0,
        )

        average_gain = (

            (
                average_gain
                * (
                    period - 1
                )
            )
            + gain

        ) / period

        average_loss = (

            (
                average_loss
                * (
                    period - 1
                )
            )
            + loss

        ) / period

        if average_loss == 0:

            current_rsi = 100.0

        else:

            rs = (
                average_gain
                / average_loss
            )

            current_rsi = (

                100.0
                - (
                    100.0
                    / (
                        1.0 + rs
                    )
                )

            )

        result[
            index
        ] = round(
            current_rsi,
            2,
        )

    return result


# =========================================================
# RSI
# =========================================================

def rsi(
    closes: NumberSeries,
    period: int = 14,
) -> Optional[float]:

    result = rsi_series(
        closes,
        period,
    )

    if not result:
        return None

    return result[-1]


# =========================================================
# TRUE RANGE SERIES
# =========================================================

def true_range_series(
    highs: NumberSeries,
    lows: NumberSeries,
    closes: NumberSeries,
) -> List[float]:

    high_data = _series(
        highs
    )

    low_data = _series(
        lows
    )

    close_data = _series(
        closes
    )

    size = min(
        len(high_data),
        len(low_data),
        len(close_data),
    )

    if size == 0:
        return []

    result: List[float] = []

    for index in range(
        size
    ):

        high = high_data[
            index
        ]

        low = low_data[
            index
        ]

        if index == 0:

            true_range = (
                high - low
            )

        else:

            previous_close = (
                close_data[
                    index - 1
                ]
            )

            true_range = max(

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

        result.append(
            max(
                true_range,
                0.0,
            )
        )

    return result


# =========================================================
# TRUE RANGE
# =========================================================

def true_range(
    high: float,
    low: float,
    previous_close: float,
) -> float:

    return round(
        max(

            _float(high)
            - _float(low),

            abs(
                _float(high)
                - _float(
                    previous_close
                )
            ),

            abs(
                _float(low)
                - _float(
                    previous_close
                )
            ),

        ),
        4,
    )


# =========================================================
# WILDER SMOOTH SERIES
# =========================================================

def _wilder_average_series(
    values: NumberSeries,
    period: int,
) -> List[Optional[float]]:

    period = _valid_period(
        period
    )

    data = _series(
        values
    )

    result: List[
        Optional[float]
    ] = [
        None
    ] * len(data)

    if len(data) < period:
        return result

    first_average = (
        sum(
            data[:period]
        )
        / period
    )

    result[
        period - 1
    ] = round(
        first_average,
        4,
    )

    previous = first_average

    for index in range(
        period,
        len(data),
    ):

        current = (

            (
                previous
                * (
                    period - 1
                )
            )
            + data[index]

        ) / period

        result[
            index
        ] = round(
            current,
            4,
        )

        previous = current

    return result


# =========================================================
# ATR SERIES
# =========================================================

def atr_series(
    highs: NumberSeries,
    lows: NumberSeries,
    closes: NumberSeries,
    period: int = 14,
) -> List[Optional[float]]:

    tr_values = true_range_series(
        highs,
        lows,
        closes,
    )

    return _wilder_average_series(
        tr_values,
        period,
    )


# =========================================================
# ATR
# =========================================================

def atr(
    highs: NumberSeries,
    lows: NumberSeries,
    closes: NumberSeries,
    period: int = 14,
) -> Optional[float]:

    result = atr_series(
        highs,
        lows,
        closes,
        period,
    )

    if not result:
        return None

    return result[-1]


# =========================================================
# MACD SERIES
# =========================================================

def macd_series(
    closes: NumberSeries,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> Dict[
    str,
    List[Optional[float]]
]:
    """
    MACD series.

    Returns
    -------
    {
        "macd": [...],
        "signal": [...],
        "histogram": [...]
    }
    """

    data = _series(
        closes
    )

    fast_values = ema_series(
        data,
        fast_period,
    )

    slow_values = ema_series(
        data,
        slow_period,
    )

    size = len(data)

    macd_values: List[
        Optional[float]
    ] = [
        None
    ] * size

    for index in range(
        size
    ):

        fast_value = (
            fast_values[index]
        )

        slow_value = (
            slow_values[index]
        )

        if (
            fast_value is None
            or slow_value is None
        ):
            continue

        macd_values[
            index
        ] = round(
            fast_value
            - slow_value,
            4,
        )

    valid_macd = [

        value

        for value in macd_values

        if value is not None

    ]

    valid_signal = ema_series(
        valid_macd,
        signal_period,
    )

    signal_values: List[
        Optional[float]
    ] = [
        None
    ] * size

    valid_index = 0

    for index, value in enumerate(
        macd_values
    ):

        if value is None:
            continue

        if valid_index < len(
            valid_signal
        ):

            signal_values[
                index
            ] = valid_signal[
                valid_index
            ]

        valid_index += 1

    histogram_values: List[
        Optional[float]
    ] = [
        None
    ] * size

    for index in range(
        size
    ):

        macd_value = (
            macd_values[index]
        )

        signal_value = (
            signal_values[index]
        )

        if (
            macd_value is None
            or signal_value is None
        ):
            continue

        histogram_values[
            index
        ] = round(
            macd_value
            - signal_value,
            4,
        )

    return {

        "macd":
            macd_values,

        "signal":
            signal_values,

        "histogram":
            histogram_values,

    }


# =========================================================
# MACD
# =========================================================

def macd(
    closes: NumberSeries,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> Tuple[
    Optional[float],
    Optional[float],
    Optional[float],
]:
    """
    Return latest MACD, signal and histogram.
    """

    result = macd_series(

        closes,

        fast_period,

        slow_period,

        signal_period,

    )

    if not result["macd"]:
        return (
            None,
            None,
            None,
        )

    return (

        result[
            "macd"
        ][-1],

        result[
            "signal"
        ][-1],

        result[
            "histogram"
        ][-1],

    )


# =========================================================
# VWAP SERIES
# =========================================================

def vwap_series(
    highs: NumberSeries,
    lows: NumberSeries,
    closes: NumberSeries,
    volumes: NumberSeries,
) -> List[Optional[float]]:
    """
    Cumulative session VWAP.
    """

    high_data = _series(
        highs
    )

    low_data = _series(
        lows
    )

    close_data = _series(
        closes
    )

    volume_data = _series(
        volumes
    )

    size = min(

        len(high_data),

        len(low_data),

        len(close_data),

        len(volume_data),

    )

    result: List[
        Optional[float]
    ] = []

    cumulative_price_volume = 0.0

    cumulative_volume = 0.0

    for index in range(
        size
    ):

        typical_price = (

            high_data[index]
            + low_data[index]
            + close_data[index]

        ) / 3.0

        volume = max(
            volume_data[index],
            0.0,
        )

        cumulative_price_volume += (
            typical_price
            * volume
        )

        cumulative_volume += (
            volume
        )

        if cumulative_volume <= 0:

            result.append(
                None
            )

        else:

            result.append(

                round(
                    cumulative_price_volume
                    / cumulative_volume,
                    4,
                )

            )

    return result


# =========================================================
# VWAP
# =========================================================

def vwap(
    highs: NumberSeries,
    lows: NumberSeries,
    closes: NumberSeries,
    volumes: NumberSeries,
) -> Optional[float]:

    result = vwap_series(
        highs,
        lows,
        closes,
        volumes,
    )

    if not result:
        return None

    return result[-1]


# =========================================================
# STANDARD DEVIATION
# =========================================================

def standard_deviation(
    values: NumberSeries,
    period: int,
) -> Optional[float]:

    period = _valid_period(
        period
    )

    data = _series(
        values
    )

    if len(data) < period:
        return None

    window = data[
        -period:
    ]

    mean = (
        sum(window)
        / period
    )

    variance = (

        sum(

            (
                value - mean
            ) ** 2

            for value in window

        )

        / period

    )

    return round(
        sqrt(
            variance
        ),
        4,
    )


# =========================================================
# BOLLINGER BANDS
# =========================================================

def bollinger_bands(
    closes: NumberSeries,
    period: int = 20,
    deviation: float = 2.0,
) -> Tuple[
    Optional[float],
    Optional[float],
    Optional[float],
]:
    """
    Return upper, middle and lower bands.
    """

    middle = sma(
        closes,
        period,
    )

    std = standard_deviation(
        closes,
        period,
    )

    if (
        middle is None
        or std is None
    ):

        return (
            None,
            None,
            None,
        )

    upper = (

        middle
        + (
            std
            * deviation
        )

    )

    lower = (

        middle
        - (
            std
            * deviation
        )

    )

    return (

        round(
            upper,
            4,
        ),

        round(
            middle,
            4,
        ),

        round(
            lower,
            4,
        ),

    )


# =========================================================
# BOLLINGER BANDWIDTH
# =========================================================

def bollinger_bandwidth(
    closes: NumberSeries,
    period: int = 20,
    deviation: float = 2.0,
) -> Optional[float]:
    """
    Bollinger bandwidth percentage.

    Useful for VCP / volatility contraction scanners.
    """

    upper, middle, lower = (
        bollinger_bands(

            closes,

            period,

            deviation,

        )
    )

    if (
        upper is None
        or middle is None
        or lower is None
        or middle == 0
    ):

        return None

    return round(

        (
            (
                upper - lower
            )
            / middle
        )
        * 100,

        2,

    )


# =========================================================
# RATE OF CHANGE
# =========================================================

def roc(
    closes: NumberSeries,
    period: int = 10,
) -> Optional[float]:
    """
    Rate of Change percentage.
    """

    period = _valid_period(
        period
    )

    data = _series(
        closes
    )

    if len(data) <= period:
        return None

    previous = data[
        -period - 1
    ]

    current = data[
        -1
    ]

    if previous == 0:
        return None

    return round(

        (
            (
                current
                - previous
            )
            / previous
        )
        * 100,

        2,

    )


# =========================================================
# MOMENTUM
# =========================================================

def momentum(
    closes: NumberSeries,
    period: int = 10,
) -> Optional[float]:

    period = _valid_period(
        period
    )

    data = _series(
        closes
    )

    if len(data) <= period:
        return None

    return round(

        data[-1]
        - data[
            -period - 1
        ],

        4,

    )


# =========================================================
# VOLUME SMA
# =========================================================

def volume_sma(
    volumes: NumberSeries,
    period: int = 20,
) -> Optional[float]:

    return sma(
        volumes,
        period,
    )


# =========================================================
# RELATIVE VOLUME
# =========================================================

def relative_volume(
    volumes: NumberSeries,
    period: int = 20,
) -> Optional[float]:
    """
    Latest volume / previous average volume.

    Current candle is excluded from the baseline.
    """

    period = _valid_period(
        period
    )

    data = _series(
        volumes
    )

    if len(data) < (
        period + 1
    ):
        return None

    current_volume = (
        data[-1]
    )

    baseline = data[
        -(period + 1):-1
    ]

    average_volume = (

        sum(baseline)
        / period

    )

    if average_volume <= 0:
        return None

    return round(
        current_volume
        / average_volume,
        2,
    )


# =========================================================
# DIRECTIONAL MOVEMENT
# =========================================================

def directional_movement(
    highs: NumberSeries,
    lows: NumberSeries,
) -> Tuple[
    List[float],
    List[float],
]:
    """
    Return +DM and -DM series.
    """

    high_data = _series(
        highs
    )

    low_data = _series(
        lows
    )

    size = min(
        len(high_data),
        len(low_data),
    )

    plus_dm: List[float] = [
        0.0
    ] * size

    minus_dm: List[float] = [
        0.0
    ] * size

    for index in range(
        1,
        size,
    ):

        upward_move = (

            high_data[index]
            - high_data[
                index - 1
            ]

        )

        downward_move = (

            low_data[
                index - 1
            ]
            - low_data[index]

        )

        if (
            upward_move
            > downward_move
            and upward_move > 0
        ):

            plus_dm[
                index
            ] = upward_move

        if (
            downward_move
            > upward_move
            and downward_move > 0
        ):

            minus_dm[
                index
            ] = downward_move

    return (
        plus_dm,
        minus_dm,
    )


# =========================================================
# ADX
# =========================================================

def adx(
    highs: NumberSeries,
    lows: NumberSeries,
    closes: NumberSeries,
    period: int = 14,
) -> Tuple[
    Optional[float],
    Optional[float],
    Optional[float],
]:
    """
    Calculate latest ADX, +DI and -DI.

    Uses Wilder-style smoothing.
    """

    period = _valid_period(
        period
    )

    high_data = _series(
        highs
    )

    low_data = _series(
        lows
    )

    close_data = _series(
        closes
    )

    size = min(
        len(high_data),
        len(low_data),
        len(close_data),
    )

    if size < (
        period * 2
    ):
        return (
            None,
            None,
            None,
        )

    high_data = high_data[
        :size
    ]

    low_data = low_data[
        :size
    ]

    close_data = close_data[
        :size
    ]

    tr_values = true_range_series(
        high_data,
        low_data,
        close_data,
    )

    plus_dm, minus_dm = (
        directional_movement(
            high_data,
            low_data,
        )
    )

    atr_values = (
        _wilder_average_series(
            tr_values,
            period,
        )
    )

    plus_smoothed = (
        _wilder_average_series(
            plus_dm,
            period,
        )
    )

    minus_smoothed = (
        _wilder_average_series(
            minus_dm,
            period,
        )
    )

    plus_di: List[
        Optional[float]
    ] = [
        None
    ] * size

    minus_di: List[
        Optional[float]
    ] = [
        None
    ] * size

    dx: List[
        Optional[float]
    ] = [
        None
    ] * size

    for index in range(
        size
    ):

        atr_value = (
            atr_values[index]
        )

        plus_value = (
            plus_smoothed[index]
        )

        minus_value = (
            minus_smoothed[index]
        )

        if (
            atr_value is None
            or plus_value is None
            or minus_value is None
            or atr_value <= 0
        ):
            continue

        current_plus_di = (

            100.0
            * plus_value
            / atr_value

        )

        current_minus_di = (

            100.0
            * minus_value
            / atr_value

        )

        plus_di[
            index
        ] = round(
            current_plus_di,
            2,
        )

        minus_di[
            index
        ] = round(
            current_minus_di,
            2,
        )

        denominator = (

            current_plus_di
            + current_minus_di

        )

        if denominator <= 0:

            dx[
                index
            ] = 0.0

        else:

            dx[
                index
            ] = (

                abs(
                    current_plus_di
                    - current_minus_di
                )
                / denominator
                * 100.0

            )

    valid_dx = [

        value

        for value in dx

        if value is not None

    ]

    if len(valid_dx) < period:

        return (
            None,
            plus_di[-1],
            minus_di[-1],
        )

    initial_adx = (

        sum(
            valid_dx[:period]
        )
        / period

    )

    current_adx = (
        initial_adx
    )

    for value in valid_dx[
        period:
    ]:

        current_adx = (

            (
                current_adx
                * (
                    period - 1
                )
            )
            + value

        ) / period

    return (

        round(
            current_adx,
            2,
        ),

        plus_di[-1],

        minus_di[-1],

    )


# =========================================================
# SUPERTREND SERIES
# =========================================================

def supertrend_series(
    highs: NumberSeries,
    lows: NumberSeries,
    closes: NumberSeries,
    period: int = 10,
    multiplier: float = 3.0,
) -> Dict[
    str,
    List[Optional[float]]
]:
    """
    Calculate Supertrend series.

    direction:
        1  = bullish
        -1 = bearish
    """

    period = _valid_period(
        period
    )

    high_data = _series(
        highs
    )

    low_data = _series(
        lows
    )

    close_data = _series(
        closes
    )

    size = min(
        len(high_data),
        len(low_data),
        len(close_data),
    )

    high_data = high_data[
        :size
    ]

    low_data = low_data[
        :size
    ]

    close_data = close_data[
        :size
    ]

    atr_values = atr_series(
        high_data,
        low_data,
        close_data,
        period,
    )

    supertrend_values: List[
        Optional[float]
    ] = [
        None
    ] * size

    direction_values: List[
        Optional[int]
    ] = [
        None
    ] * size

    final_upper: List[
        Optional[float]
    ] = [
        None
    ] * size

    final_lower: List[
        Optional[float]
    ] = [
        None
    ] * size

    for index in range(
        size
    ):

        atr_value = (
            atr_values[index]
        )

        if atr_value is None:
            continue

        hl2 = (

            high_data[index]
            + low_data[index]

        ) / 2.0

        basic_upper = (

            hl2
            + multiplier
            * atr_value

        )

        basic_lower = (

            hl2
            - multiplier
            * atr_value

        )

        previous_index = (
            index - 1
        )

        if (
            previous_index < 0
            or final_upper[
                previous_index
            ] is None
            or final_lower[
                previous_index
            ] is None
        ):

            final_upper[
                index
            ] = basic_upper

            final_lower[
                index
            ] = basic_lower

            if close_data[index] >= hl2:

                direction_values[
                    index
                ] = 1

                supertrend_values[
                    index
                ] = basic_lower

            else:

                direction_values[
                    index
                ] = -1

                supertrend_values[
                    index
                ] = basic_upper

            continue

        previous_upper = (
            final_upper[
                previous_index
            ]
        )

        previous_lower = (
            final_lower[
                previous_index
            ]
        )

        previous_close = (
            close_data[
                previous_index
            ]
        )

        if (
            basic_upper
            < previous_upper
            or previous_close
            > previous_upper
        ):

            final_upper[
                index
            ] = basic_upper

        else:

            final_upper[
                index
            ] = previous_upper

        if (
            basic_lower
            > previous_lower
            or previous_close
            < previous_lower
        ):

            final_lower[
                index
            ] = basic_lower

        else:

            final_lower[
                index
            ] = previous_lower

        previous_direction = (
            direction_values[
                previous_index
            ]
        )

        if previous_direction == 1:

            if (
                close_data[index]
                < final_lower[index]
            ):

                direction = -1

            else:

                direction = 1

        else:

            if (
                close_data[index]
                > final_upper[index]
            ):

                direction = 1

            else:

                direction = -1

        direction_values[
            index
        ] = direction

        if direction == 1:

            supertrend_values[
                index
            ] = round(
                final_lower[index],
                4,
            )

        else:

            supertrend_values[
                index
            ] = round(
                final_upper[index],
                4,
            )

    return {

        "supertrend":
            supertrend_values,

        "direction":
            direction_values,

    }


# =========================================================
# SUPERTREND
# =========================================================

def supertrend(
    highs: NumberSeries,
    lows: NumberSeries,
    closes: NumberSeries,
    period: int = 10,
    multiplier: float = 3.0,
) -> Tuple[
    Optional[float],
    Optional[int],
]:

    result = supertrend_series(

        highs,

        lows,

        closes,

        period,

        multiplier,

    )

    if not result[
        "supertrend"
    ]:

        return (
            None,
            None,
        )

    return (

        result[
            "supertrend"
        ][-1],

        result[
            "direction"
        ][-1],

    )


# =========================================================
# EMA CROSS
# =========================================================

def ema_cross(
    closes: NumberSeries,
    fast_period: int,
    slow_period: int,
) -> str:
    """
    Detect latest EMA crossover.

    Returns
    -------
    BULLISH
    BEARISH
    NONE
    """

    fast = ema_series(
        closes,
        fast_period,
    )

    slow = ema_series(
        closes,
        slow_period,
    )

    if len(fast) < 2:
        return "NONE"

    current_fast = fast[-1]

    previous_fast = fast[-2]

    current_slow = slow[-1]

    previous_slow = slow[-2]

    if (
        current_fast is None
        or previous_fast is None
        or current_slow is None
        or previous_slow is None
    ):
        return "NONE"

    if (
        previous_fast
        <= previous_slow
        and current_fast
        > current_slow
    ):
        return "BULLISH"

    if (
        previous_fast
        >= previous_slow
        and current_fast
        < current_slow
    ):
        return "BEARISH"

    return "NONE"


# =========================================================
# PRICE ABOVE EMA
# =========================================================

def price_above_ema(
    closes: NumberSeries,
    period: int,
) -> bool:

    data = _series(
        closes
    )

    if not data:
        return False

    ema_value = ema(
        data,
        period,
    )

    if ema_value is None:
        return False

    return (
        data[-1]
        > ema_value
    )


# =========================================================
# PRICE BELOW EMA
# =========================================================

def price_below_ema(
    closes: NumberSeries,
    period: int,
) -> bool:

    data = _series(
        closes
    )

    if not data:
        return False

    ema_value = ema(
        data,
        period,
    )

    if ema_value is None:
        return False

    return (
        data[-1]
        < ema_value
    )


# =========================================================
# EMA ALIGNMENT
# =========================================================

def ema_alignment(
    closes: NumberSeries,
    periods: Sequence[int] = (
        20,
        50,
        200,
    ),
) -> str:
    """
    Detect EMA trend structure.

    Returns:
        BULLISH
        BEARISH
        MIXED
        UNKNOWN
    """

    values: List[float] = []

    for period in periods:

        value = ema(
            closes,
            period,
        )

        if value is None:
            return "UNKNOWN"

        values.append(
            value
        )

    bullish = all(

        values[index]
        > values[index + 1]

        for index in range(
            len(values) - 1
        )

    )

    if bullish:
        return "BULLISH"

    bearish = all(

        values[index]
        < values[index + 1]

        for index in range(
            len(values) - 1
        )

    )

    if bearish:
        return "BEARISH"

    return "MIXED"


# =========================================================
# INDICATOR SNAPSHOT
# =========================================================

def indicator_snapshot(
    highs: NumberSeries,
    lows: NumberSeries,
    closes: NumberSeries,
    volumes: NumberSeries,
) -> Dict[str, Optional[float]]:
    """
    Calculate common scanner indicators in one call.

    Useful when creating a Signal object.
    """

    ema9_value = ema(
        closes,
        9,
    )

    ema20_value = ema(
        closes,
        20,
    )

    ema21_value = ema(
        closes,
        21,
    )

    ema50_value = ema(
        closes,
        50,
    )

    ema100_value = ema(
        closes,
        100,
    )

    ema200_value = ema(
        closes,
        200,
    )

    rsi_value = rsi(
        closes,
        14,
    )

    (
        macd_value,
        macd_signal_value,
        macd_histogram_value,
    ) = macd(
        closes
    )

    atr_value = atr(
        highs,
        lows,
        closes,
        14,
    )

    (
        adx_value,
        plus_di_value,
        minus_di_value,
    ) = adx(
        highs,
        lows,
        closes,
        14,
    )

    vwap_value = vwap(
        highs,
        lows,
        closes,
        volumes,
    )

    (
        supertrend_value,
        supertrend_direction,
    ) = supertrend(
        highs,
        lows,
        closes,
    )

    relative_volume_value = (
        relative_volume(
            volumes,
            20,
        )
    )

    return {

        "ema9":
            ema9_value,

        "ema20":
            ema20_value,

        "ema21":
            ema21_value,

        "ema50":
            ema50_value,

        "ema100":
            ema100_value,

        "ema200":
            ema200_value,

        "rsi":
            rsi_value,

        "macd":
            macd_value,

        "macd_signal":
            macd_signal_value,

        "macd_histogram":
            macd_histogram_value,

        "atr":
            atr_value,

        "adx":
            adx_value,

        "plus_di":
            plus_di_value,

        "minus_di":
            minus_di_value,

        "vwap":
            vwap_value,

        "supertrend":
            supertrend_value,

        "supertrend_direction":
            supertrend_direction,

        "volume_ratio":
            relative_volume_value,

    }


# =========================================================
# INDICATOR ENGINE
# =========================================================

class IndicatorEngine:
    """
    Convenience wrapper for technical indicators.
    """

    @staticmethod
    def sma(
        values: NumberSeries,
        period: int,
    ) -> Optional[float]:

        return sma(
            values,
            period,
        )

    @staticmethod
    def ema(
        values: NumberSeries,
        period: int,
    ) -> Optional[float]:

        return ema(
            values,
            period,
        )

    @staticmethod
    def rsi(
        closes: NumberSeries,
        period: int = 14,
    ) -> Optional[float]:

        return rsi(
            closes,
            period,
        )

    @staticmethod
    def atr(
        highs: NumberSeries,
        lows: NumberSeries,
        closes: NumberSeries,
        period: int = 14,
    ) -> Optional[float]:

        return atr(
            highs,
            lows,
            closes,
            period,
        )

    @staticmethod
    def macd(
        closes: NumberSeries,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ):

        return macd(

            closes,

            fast_period,

            slow_period,

            signal_period,

        )

    @staticmethod
    def vwap(
        highs: NumberSeries,
        lows: NumberSeries,
        closes: NumberSeries,
        volumes: NumberSeries,
    ) -> Optional[float]:

        return vwap(
            highs,
            lows,
            closes,
            volumes,
        )

    @staticmethod
    def adx(
        highs: NumberSeries,
        lows: NumberSeries,
        closes: NumberSeries,
        period: int = 14,
    ):

        return adx(
            highs,
            lows,
            closes,
            period,
        )

    @staticmethod
    def supertrend(
        highs: NumberSeries,
        lows: NumberSeries,
        closes: NumberSeries,
        period: int = 10,
        multiplier: float = 3.0,
    ):

        return supertrend(

            highs,

            lows,

            closes,

            period,

            multiplier,

        )

    @staticmethod
    def snapshot(
        highs: NumberSeries,
        lows: NumberSeries,
        closes: NumberSeries,
        volumes: NumberSeries,
    ):

        return indicator_snapshot(

            highs,

            lows,

            closes,

            volumes,

        )


# =========================================================
# DEFAULT ENGINE
# =========================================================

indicator_engine = (
    IndicatorEngine()
)


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "IndicatorEngine",

    "indicator_engine",

    "sma",
    "sma_series",

    "ema",
    "ema_series",

    "rsi",
    "rsi_series",

    "true_range",
    "true_range_series",

    "atr",
    "atr_series",

    "macd",
    "macd_series",

    "vwap",
    "vwap_series",

    "standard_deviation",

    "bollinger_bands",
    "bollinger_bandwidth",

    "roc",
    "momentum",

    "volume_sma",
    "relative_volume",

    "directional_movement",
    "adx",

    "supertrend",
    "supertrend_series",

    "ema_cross",
    "ema_alignment",

    "price_above_ema",
    "price_below_ema",

    "highest",
    "lowest",

    "indicator_snapshot",

]


# ==========================
# END OF FILE
# ==========================