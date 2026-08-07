"""
=========================================================
StockVersity Scanner Pro
Scanner Utilities
Version : 2.0
=========================================================

Common helper functions used by StockVersity scanners.

Responsibilities
----------------
• Safe numeric conversion
• Percentage calculations
• Price change calculations
• Gap calculations
• Risk / reward calculations
• Position sizing
• Volume ratio calculations
• Candle analysis
• Symbol normalization
• Market-data extraction
• Generic scanner helpers

This module DOES NOT execute scanners.
=========================================================
"""

from __future__ import annotations

from math import isfinite

from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple


# =========================================================
# SAFE FLOAT
# =========================================================

def safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    Safely convert value to float.
    """

    try:

        result = float(value)

        if not isfinite(result):
            return default

        return result

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):

        return default


# =========================================================
# SAFE INT
# =========================================================

def safe_int(
    value: Any,
    default: int = 0,
) -> int:
    """
    Safely convert value to integer.
    """

    try:

        result = float(value)

        if not isfinite(result):
            return default

        return int(result)

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):

        return default


# =========================================================
# CLAMP
# =========================================================

def clamp(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    """
    Restrict value between minimum and maximum.
    """

    value = safe_float(
        value
    )

    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


# =========================================================
# SAFE DIVIDE
# =========================================================

def safe_divide(
    numerator: Any,
    denominator: Any,
    default: float = 0.0,
) -> float:
    """
    Division helper that prevents zero division.
    """

    numerator_value = safe_float(
        numerator
    )

    denominator_value = safe_float(
        denominator
    )

    if denominator_value == 0:
        return default

    return (
        numerator_value
        / denominator_value
    )


# =========================================================
# PERCENTAGE
# =========================================================

def percentage(
    part: Any,
    whole: Any,
    default: float = 0.0,
) -> float:
    """
    Return part as percentage of whole.
    """

    whole_value = safe_float(
        whole
    )

    if whole_value == 0:
        return default

    return round(
        (
            safe_float(part)
            / whole_value
        )
        * 100,
        2,
    )


# =========================================================
# PERCENT CHANGE
# =========================================================

def percent_change(
    old_value: Any,
    new_value: Any,
) -> float:
    """
    Percentage change from old value to new value.
    """

    old = safe_float(
        old_value
    )

    new = safe_float(
        new_value
    )

    if old == 0:
        return 0.0

    return round(
        (
            (
                new - old
            )
            / abs(old)
        )
        * 100,
        2,
    )


# =========================================================
# ABSOLUTE PERCENT DIFFERENCE
# =========================================================

def percent_difference(
    first: Any,
    second: Any,
) -> float:
    """
    Absolute percentage difference relative to first value.
    """

    first_value = safe_float(
        first
    )

    second_value = safe_float(
        second
    )

    if first_value == 0:
        return 0.0

    return round(
        (
            abs(
                second_value
                - first_value
            )
            / abs(first_value)
        )
        * 100,
        2,
    )


# =========================================================
# GAP PERCENT
# =========================================================

def calculate_gap_percent(
    open_price: Any,
    previous_close: Any,
) -> float:
    """
    Calculate opening gap percentage.

    Positive = gap up
    Negative = gap down
    """

    previous = safe_float(
        previous_close
    )

    opening = safe_float(
        open_price
    )

    if previous <= 0:
        return 0.0

    return round(
        (
            (
                opening
                - previous
            )
            / previous
        )
        * 100,
        2,
    )


# =========================================================
# GAP FILTER
# =========================================================

def gap_within_limit(
    open_price: Any,
    previous_close: Any,
    maximum_gap_percent: float = 3.0,
) -> bool:
    """
    Return True if absolute gap is within allowed limit.

    StockVersity default:
    Exclude gap-up/down greater than 3%.
    """

    gap = abs(
        calculate_gap_percent(
            open_price,
            previous_close,
        )
    )

    return (
        gap
        <= abs(
            safe_float(
                maximum_gap_percent,
                3.0,
            )
        )
    )


# =========================================================
# PRICE RANGE
# =========================================================

def price_range(
    high: Any,
    low: Any,
) -> float:
    """
    Absolute candle/range size.
    """

    return max(
        safe_float(high)
        - safe_float(low),
        0.0,
    )


# =========================================================
# RANGE PERCENT
# =========================================================

def range_percent(
    high: Any,
    low: Any,
    reference_price: Any,
) -> float:
    """
    Range size as percentage of reference price.
    """

    reference = safe_float(
        reference_price
    )

    if reference <= 0:
        return 0.0

    return round(
        (
            price_range(
                high,
                low,
            )
            / reference
        )
        * 100,
        2,
    )


# =========================================================
# ORB WIDTH
# =========================================================

def orb_width_percent(
    orb_high: Any,
    orb_low: Any,
) -> float:
    """
    Opening range width as percentage of ORB low.
    """

    low = safe_float(
        orb_low
    )

    if low <= 0:
        return 0.0

    return round(
        (
            (
                safe_float(
                    orb_high
                )
                - low
            )
            / low
        )
        * 100,
        2,
    )


# =========================================================
# ORB WIDTH FILTER
# =========================================================

def valid_orb_width(
    orb_high: Any,
    orb_low: Any,
    maximum_percent: float = 3.0,
) -> bool:
    """
    Reject unusually wide opening ranges.
    """

    width = orb_width_percent(
        orb_high,
        orb_low,
    )

    return (
        0
        < width
        <= maximum_percent
    )


# =========================================================
# VOLUME RATIO
# =========================================================

def calculate_volume_ratio(
    volume: Any,
    average_volume: Any,
) -> float:
    """
    Relative volume (RVOL).

    Example:
    volume = 200000
    average = 100000

    RVOL = 2.0
    """

    average = safe_float(
        average_volume
    )

    if average <= 0:
        return 0.0

    return round(
        safe_float(volume)
        / average,
        2,
    )


# =========================================================
# VOLUME CONFIRMATION
# =========================================================

def volume_confirmed(
    volume: Any,
    average_volume: Any,
    minimum_ratio: float = 1.5,
) -> bool:
    """
    Check whether breakout volume is strong enough.
    """

    return (
        calculate_volume_ratio(
            volume,
            average_volume,
        )
        >= minimum_ratio
    )


# =========================================================
# RISK
# =========================================================

def calculate_risk(
    entry: Any,
    stop_loss: Any,
) -> float:
    """
    Absolute price risk per share.
    """

    return round(
        abs(
            safe_float(entry)
            - safe_float(stop_loss)
        ),
        4,
    )


# =========================================================
# REWARD
# =========================================================

def calculate_reward(
    entry: Any,
    target: Any,
) -> float:
    """
    Absolute reward per share.
    """

    return round(
        abs(
            safe_float(target)
            - safe_float(entry)
        ),
        4,
    )


# =========================================================
# RISK REWARD
# =========================================================

def calculate_risk_reward(
    entry: Any,
    stop_loss: Any,
    target: Any,
) -> float:
    """
    Calculate reward/risk ratio.
    """

    risk = calculate_risk(
        entry,
        stop_loss,
    )

    if risk <= 0:
        return 0.0

    reward = calculate_reward(
        entry,
        target,
    )

    return round(
        reward / risk,
        2,
    )


# =========================================================
# TARGET FROM RR
# =========================================================

def calculate_target(
    entry: Any,
    stop_loss: Any,
    risk_reward: float = 2.0,
    *,
    is_buy: bool = True,
) -> float:
    """
    Calculate target from desired RR.
    """

    entry_value = safe_float(
        entry
    )

    stop_value = safe_float(
        stop_loss
    )

    rr = max(
        safe_float(
            risk_reward
        ),
        0.0,
    )

    risk = abs(
        entry_value
        - stop_value
    )

    if risk <= 0:
        return 0.0

    if is_buy:

        target = (
            entry_value
            + risk * rr
        )

    else:

        target = (
            entry_value
            - risk * rr
        )

    return round(
        target,
        2,
    )


# =========================================================
# MULTIPLE TARGETS
# =========================================================

def calculate_targets(
    entry: Any,
    stop_loss: Any,
    *,
    rr_levels: Sequence[float] = (
        2.0,
        3.0,
        4.0,
    ),
    is_buy: bool = True,
) -> List[float]:
    """
    Calculate multiple RR-based targets.
    """

    return [

        calculate_target(

            entry,
            stop_loss,
            rr,

            is_buy=is_buy,

        )

        for rr in rr_levels

    ]


# =========================================================
# POSITION SIZE
# =========================================================

def calculate_position_size(
    capital: Any,
    risk_percent: Any,
    entry: Any,
    stop_loss: Any,
) -> int:
    """
    Risk-based position sizing.
    """

    capital_value = safe_float(
        capital
    )

    risk_percent_value = safe_float(
        risk_percent
    )

    per_share_risk = calculate_risk(
        entry,
        stop_loss,
    )

    if capital_value <= 0:
        return 0

    if risk_percent_value <= 0:
        return 0

    if per_share_risk <= 0:
        return 0

    maximum_loss = (

        capital_value
        * risk_percent_value
        / 100

    )

    return max(
        int(
            maximum_loss
            / per_share_risk
        ),
        0,
    )


# =========================================================
# EXPECTED PROFIT
# =========================================================

def expected_profit(
    entry: Any,
    target: Any,
    quantity: Any,
) -> float:

    reward = calculate_reward(
        entry,
        target,
    )

    return round(
        reward
        * max(
            safe_int(quantity),
            0,
        ),
        2,
    )


# =========================================================
# EXPECTED LOSS
# =========================================================

def expected_loss(
    entry: Any,
    stop_loss: Any,
    quantity: Any,
) -> float:

    risk = calculate_risk(
        entry,
        stop_loss,
    )

    return round(
        risk
        * max(
            safe_int(quantity),
            0,
        ),
        2,
    )


# =========================================================
# CANDLE BODY
# =========================================================

def candle_body(
    open_price: Any,
    close_price: Any,
) -> float:
    """
    Absolute candle body.
    """

    return abs(
        safe_float(
            close_price
        )
        - safe_float(
            open_price
        )
    )


# =========================================================
# CANDLE BODY PERCENT
# =========================================================

def candle_body_percent(
    open_price: Any,
    high_price: Any,
    low_price: Any,
    close_price: Any,
) -> float:
    """
    Candle body as percentage of complete candle range.
    """

    total_range = price_range(
        high_price,
        low_price,
    )

    if total_range <= 0:
        return 0.0

    body = candle_body(
        open_price,
        close_price,
    )

    return round(
        (
            body
            / total_range
        )
        * 100,
        2,
    )


# =========================================================
# UPPER WICK
# =========================================================

def upper_wick(
    open_price: Any,
    high_price: Any,
    close_price: Any,
) -> float:

    opening = safe_float(
        open_price
    )

    high = safe_float(
        high_price
    )

    close = safe_float(
        close_price
    )

    return round(
        max(
            high
            - max(
                opening,
                close,
            ),
            0.0,
        ),
        4,
    )


# =========================================================
# LOWER WICK
# =========================================================

def lower_wick(
    open_price: Any,
    low_price: Any,
    close_price: Any,
) -> float:

    opening = safe_float(
        open_price
    )

    low = safe_float(
        low_price
    )

    close = safe_float(
        close_price
    )

    return round(
        max(
            min(
                opening,
                close,
            )
            - low,
            0.0,
        ),
        4,
    )


# =========================================================
# GREEN CANDLE
# =========================================================

def is_green_candle(
    open_price: Any,
    close_price: Any,
) -> bool:

    return (
        safe_float(close_price)
        > safe_float(open_price)
    )


# =========================================================
# RED CANDLE
# =========================================================

def is_red_candle(
    open_price: Any,
    close_price: Any,
) -> bool:

    return (
        safe_float(close_price)
        < safe_float(open_price)
    )


# =========================================================
# DOJI
# =========================================================

def is_doji(
    open_price: Any,
    high_price: Any,
    low_price: Any,
    close_price: Any,
    maximum_body_percent: float = 10.0,
) -> bool:
    """
    Detect small-body doji-style candle.
    """

    return (
        candle_body_percent(
            open_price,
            high_price,
            low_price,
            close_price,
        )
        <= maximum_body_percent
    )


# =========================================================
# BREAKOUT
# =========================================================

def is_breakout(
    price: Any,
    resistance: Any,
    buffer_percent: float = 0.0,
) -> bool:
    """
    Check price breakout above resistance.
    """

    resistance_value = safe_float(
        resistance
    )

    if resistance_value <= 0:
        return False

    trigger = (

        resistance_value
        * (
            1
            + safe_float(
                buffer_percent
            )
            / 100
        )

    )

    return (
        safe_float(price)
        > trigger
    )


# =========================================================
# BREAKDOWN
# =========================================================

def is_breakdown(
    price: Any,
    support: Any,
    buffer_percent: float = 0.0,
) -> bool:
    """
    Check price breakdown below support.
    """

    support_value = safe_float(
        support
    )

    if support_value <= 0:
        return False

    trigger = (

        support_value
        * (
            1
            - safe_float(
                buffer_percent
            )
            / 100
        )

    )

    return (
        safe_float(price)
        < trigger
    )


# =========================================================
# NEAR PRICE
# =========================================================

def is_near_price(
    price: Any,
    reference: Any,
    tolerance_percent: float = 0.25,
) -> bool:
    """
    Determine whether price is near another price.
    """

    reference_value = safe_float(
        reference
    )

    if reference_value <= 0:
        return False

    difference = (

        abs(
            safe_float(price)
            - reference_value
        )
        / reference_value
        * 100

    )

    return (
        difference
        <= tolerance_percent
    )


# =========================================================
# TREND HELPERS
# =========================================================

def bullish_ema_alignment(
    ema20: Any,
    ema50: Any,
    ema200: Any,
) -> bool:
    """
    Bullish institutional EMA structure.
    """

    return (

        safe_float(ema20)
        > safe_float(ema50)
        > safe_float(ema200)

    )


def bearish_ema_alignment(
    ema20: Any,
    ema50: Any,
    ema200: Any,
) -> bool:
    """
    Bearish institutional EMA structure.
    """

    return (

        safe_float(ema20)
        < safe_float(ema50)
        < safe_float(ema200)

    )


# =========================================================
# PRICE ABOVE EMA
# =========================================================

def price_above_ema(
    price: Any,
    ema: Any,
) -> bool:

    ema_value = safe_float(
        ema
    )

    if ema_value <= 0:
        return False

    return (
        safe_float(price)
        > ema_value
    )


# =========================================================
# PRICE BELOW EMA
# =========================================================

def price_below_ema(
    price: Any,
    ema: Any,
) -> bool:

    ema_value = safe_float(
        ema
    )

    if ema_value <= 0:
        return False

    return (
        safe_float(price)
        < ema_value
    )


# =========================================================
# ABOVE VWAP
# =========================================================

def above_vwap(
    price: Any,
    vwap: Any,
) -> bool:

    vwap_value = safe_float(
        vwap
    )

    if vwap_value <= 0:
        return False

    return (
        safe_float(price)
        > vwap_value
    )


# =========================================================
# BELOW VWAP
# =========================================================

def below_vwap(
    price: Any,
    vwap: Any,
) -> bool:

    vwap_value = safe_float(
        vwap
    )

    if vwap_value <= 0:
        return False

    return (
        safe_float(price)
        < vwap_value
    )


# =========================================================
# ADX FILTER
# =========================================================

def valid_adx(
    adx: Any,
    minimum_adx: float = 20.0,
) -> bool:
    """
    StockVersity default:
    reject weak trends below ADX 20.
    """

    return (
        safe_float(adx)
        >= minimum_adx
    )


# =========================================================
# RSI RANGE
# =========================================================

def rsi_in_range(
    rsi: Any,
    minimum: float = 0.0,
    maximum: float = 100.0,
) -> bool:

    value = safe_float(
        rsi
    )

    return (
        minimum
        <= value
        <= maximum
    )


# =========================================================
# SYMBOL NORMALIZATION
# =========================================================

def normalize_symbol(
    symbol: Any,
) -> str:
    """
    Normalize NSE trading symbol.
    """

    if symbol is None:
        return ""

    value = (
        str(symbol)
        .strip()
        .upper()
    )

    if ":" in value:

        value = value.split(
            ":"
        )[-1]

    return value


# =========================================================
# EXCHANGE NORMALIZATION
# =========================================================

def normalize_exchange(
    exchange: Any,
    default: str = "NSE",
) -> str:

    if exchange is None:
        return default

    value = (
        str(exchange)
        .strip()
        .upper()
    )

    return (
        value
        if value
        else default
    )


# =========================================================
# INSTRUMENT KEY
# =========================================================

def normalize_instrument_key(
    instrument_key: Any,
) -> str:

    if instrument_key is None:
        return ""

    return (
        str(
            instrument_key
        )
        .strip()
    )


# =========================================================
# GET NESTED VALUE
# =========================================================

def get_nested(
    data: Dict[str, Any],
    *keys: str,
    default: Any = None,
) -> Any:
    """
    Safely read nested dictionaries.

    Example:

        get_nested(
            data,
            "quote",
            "ohlc",
            "close"
        )
    """

    current: Any = data

    for key in keys:

        if not isinstance(
            current,
            dict,
        ):
            return default

        if key not in current:
            return default

        current = current[
            key
        ]

    return current


# =========================================================
# FIRST AVAILABLE VALUE
# =========================================================

def first_available(
    data: Dict[str, Any],
    keys: Sequence[str],
    default: Any = None,
) -> Any:
    """
    Return first existing non-None key.
    """

    for key in keys:

        if key not in data:
            continue

        value = data[
            key
        ]

        if value is not None:
            return value

    return default


# =========================================================
# EXTRACT PRICE
# =========================================================

def extract_price(
    data: Dict[str, Any],
) -> float:
    """
    Extract LTP/price from common market-data field names.
    """

    value = first_available(

        data,

        (
            "last_price",
            "ltp",
            "price",
            "close",
            "close_price",
        ),

        0.0,

    )

    return safe_float(
        value
    )


# =========================================================
# EXTRACT VOLUME
# =========================================================

def extract_volume(
    data: Dict[str, Any],
) -> int:

    value = first_available(

        data,

        (
            "volume",
            "total_volume",
            "volume_traded",
            "vol",
        ),

        0,

    )

    return safe_int(
        value
    )


# =========================================================
# EXTRACT OHLC
# =========================================================

def extract_ohlc(
    data: Dict[str, Any],
) -> Tuple[
    float,
    float,
    float,
    float,
]:
    """
    Extract open, high, low, close.
    """

    open_price = safe_float(

        first_available(
            data,
            (
                "open",
                "open_price",
            ),
            0.0,
        )

    )

    high_price = safe_float(

        first_available(
            data,
            (
                "high",
                "high_price",
            ),
            0.0,
        )

    )

    low_price = safe_float(

        first_available(
            data,
            (
                "low",
                "low_price",
            ),
            0.0,
        )

    )

    close_price = safe_float(

        first_available(
            data,
            (
                "close",
                "close_price",
                "last_price",
                "ltp",
            ),
            0.0,
        )

    )

    return (
        open_price,
        high_price,
        low_price,
        close_price,
    )


# =========================================================
# AVERAGE
# =========================================================

def average(
    values: Iterable[Any],
) -> float:
    """
    Safe arithmetic mean.
    """

    numbers = [

        safe_float(value)

        for value in values

    ]

    if not numbers:
        return 0.0

    return round(
        sum(numbers)
        / len(numbers),
        4,
    )


# =========================================================
# SIMPLE MOVING AVERAGE
# =========================================================

def simple_moving_average(
    values: Sequence[Any],
    period: int,
) -> float:
    """
    Calculate latest simple moving average.
    """

    if period <= 0:
        return 0.0

    if len(values) < period:
        return 0.0

    window = values[
        -period:
    ]

    return average(
        window
    )


# =========================================================
# HIGHEST
# =========================================================

def highest(
    values: Iterable[Any],
    default: float = 0.0,
) -> float:

    numbers = [

        safe_float(value)

        for value in values

    ]

    if not numbers:
        return default

    return max(
        numbers
    )


# =========================================================
# LOWEST
# =========================================================

def lowest(
    values: Iterable[Any],
    default: float = 0.0,
) -> float:

    numbers = [

        safe_float(value)

        for value in values

    ]

    if not numbers:
        return default

    return min(
        numbers
    )


# =========================================================
# MARKET CAP FILTER
# =========================================================

def valid_market_cap(
    market_cap: Any,
    minimum_market_cap: float = 1000.0,
) -> bool:
    """
    StockVersity default:
    market cap must be >= ₹1,000 crore.
    """

    return (
        safe_float(
            market_cap
        )
        >= minimum_market_cap
    )


# =========================================================
# PRICE FILTER
# =========================================================

def valid_stock_price(
    price: Any,
    minimum_price: float = 200.0,
) -> bool:
    """
    StockVersity default:
    stock price must be >= ₹200.
    """

    return (
        safe_float(
            price
        )
        >= minimum_price
    )


# =========================================================
# BASIC STOCK FILTER
# =========================================================

def passes_basic_filters(
    *,
    price: Any,
    market_cap: Any,
    open_price: Optional[Any] = None,
    previous_close: Optional[Any] = None,
    adx: Optional[Any] = None,
    minimum_price: float = 200.0,
    minimum_market_cap: float = 1000.0,
    maximum_gap_percent: float = 3.0,
    minimum_adx: float = 20.0,
) -> bool:
    """
    Apply StockVersity common stock-quality filters.

    Default rules
    -------------
    Price >= ₹200
    Market cap >= ₹1,000 crore
    Gap <= ±3%
    ADX >= 20
    """

    if not valid_stock_price(
        price,
        minimum_price,
    ):
        return False

    if not valid_market_cap(
        market_cap,
        minimum_market_cap,
    ):
        return False

    if (
        open_price is not None
        and previous_close is not None
    ):

        if not gap_within_limit(

            open_price,
            previous_close,
            maximum_gap_percent,

        ):
            return False

    if adx is not None:

        if not valid_adx(
            adx,
            minimum_adx,
        ):
            return False

    return True


# =========================================================
# SIGNAL DIRECTION
# =========================================================

def direction_from_price(
    price: Any,
    reference: Any,
) -> str:
    """
    Return BUY / SELL / NEUTRAL based on reference.
    """

    price_value = safe_float(
        price
    )

    reference_value = safe_float(
        reference
    )

    if price_value > reference_value:
        return "BUY"

    if price_value < reference_value:
        return "SELL"

    return "NEUTRAL"


# =========================================================
# SCORE TO GRADE
# =========================================================

def score_to_grade(
    score: Any,
) -> str:
    """
    Generic score grade.
    """

    value = safe_float(
        score
    )

    if value >= 90:
        return "A+"

    if value >= 80:
        return "A"

    if value >= 70:
        return "B"

    if value >= 60:
        return "C"

    return "D"


# =========================================================
# SCORE LABEL
# =========================================================

def score_label(
    score: Any,
) -> str:

    value = safe_float(
        score
    )

    if value >= 90:
        return "VERY_STRONG"

    if value >= 80:
        return "STRONG"

    if value >= 70:
        return "GOOD"

    if value >= 60:
        return "MODERATE"

    return "WEAK"


# =========================================================
# UNIQUE SYMBOLS
# =========================================================

def unique_symbols(
    symbols: Iterable[Any],
) -> List[str]:
    """
    Normalize and remove duplicate symbols while
    preserving original order.
    """

    seen = set()

    result: List[str] = []

    for symbol in symbols:

        normalized = normalize_symbol(
            symbol
        )

        if not normalized:
            continue

        if normalized in seen:
            continue

        seen.add(
            normalized
        )

        result.append(
            normalized
        )

    return result


# =========================================================
# CHUNK LIST
# =========================================================

def chunk_list(
    items: Sequence[Any],
    size: int,
) -> List[List[Any]]:
    """
    Split sequence into batches.

    Useful for API/feed batching.
    """

    size = max(
        int(size),
        1,
    )

    return [

        list(
            items[
                index:
                index + size
            ]
        )

        for index in range(
            0,
            len(items),
            size,
        )

    ]


# =========================================================
# ROUND PRICE
# =========================================================

def round_price(
    price: Any,
    digits: int = 2,
) -> float:

    return round(
        safe_float(
            price
        ),
        digits,
    )


# =========================================================
# VALID PRICE
# =========================================================

def valid_price(
    price: Any,
) -> bool:

    return (
        safe_float(
            price
        )
        > 0
    )


# =========================================================
# VALID OHLC
# =========================================================

def valid_ohlc(
    open_price: Any,
    high_price: Any,
    low_price: Any,
    close_price: Any,
) -> bool:
    """
    Basic OHLC consistency validation.
    """

    opening = safe_float(
        open_price
    )

    high = safe_float(
        high_price
    )

    low = safe_float(
        low_price
    )

    close = safe_float(
        close_price
    )

    if (
        opening <= 0
        or high <= 0
        or low <= 0
        or close <= 0
    ):
        return False

    if high < low:
        return False

    if high < opening:
        return False

    if high < close:
        return False

    if low > opening:
        return False

    if low > close:
        return False

    return True


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "safe_float",
    "safe_int",
    "safe_divide",
    "clamp",

    "percentage",
    "percent_change",
    "percent_difference",

    "calculate_gap_percent",
    "gap_within_limit",

    "price_range",
    "range_percent",

    "orb_width_percent",
    "valid_orb_width",

    "calculate_volume_ratio",
    "volume_confirmed",

    "calculate_risk",
    "calculate_reward",
    "calculate_risk_reward",

    "calculate_target",
    "calculate_targets",

    "calculate_position_size",

    "expected_profit",
    "expected_loss",

    "candle_body",
    "candle_body_percent",

    "upper_wick",
    "lower_wick",

    "is_green_candle",
    "is_red_candle",
    "is_doji",

    "is_breakout",
    "is_breakdown",
    "is_near_price",

    "bullish_ema_alignment",
    "bearish_ema_alignment",

    "price_above_ema",
    "price_below_ema",

    "above_vwap",
    "below_vwap",

    "valid_adx",
    "rsi_in_range",

    "normalize_symbol",
    "normalize_exchange",
    "normalize_instrument_key",

    "get_nested",
    "first_available",

    "extract_price",
    "extract_volume",
    "extract_ohlc",

    "average",
    "simple_moving_average",
    "highest",
    "lowest",

    "valid_market_cap",
    "valid_stock_price",
    "passes_basic_filters",

    "direction_from_price",

    "score_to_grade",
    "score_label",

    "unique_symbols",
    "chunk_list",

    "round_price",

    "valid_price",
    "valid_ohlc",

]


# ==========================
# END OF FILE
# ==========================