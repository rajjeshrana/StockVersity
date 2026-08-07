"""
=========================================================
StockVersity Scanner Pro
Scanner Constants
Version : 2.0
=========================================================

Central constants used across the scanner system.

Responsibilities
----------------
• Exchange / market constants
• Trading modes
• Supported timeframes
• Market timings
• Score thresholds
• Risk / reward thresholds
• Volume thresholds
• Gap limits
• ADX thresholds
• Scanner limits
• Metadata keys
=========================================================
"""

from __future__ import annotations

from enum import Enum

from typing import Dict
from typing import Final
from typing import Tuple


# =========================================================
# APPLICATION
# =========================================================

APP_NAME: Final[str] = (
    "StockVersity Scanner Pro"
)

APP_VERSION: Final[str] = "2.0"

SCANNER_VERSION: Final[str] = "2.0"


# =========================================================
# MARKET
# =========================================================

DEFAULT_EXCHANGE: Final[str] = "NSE"

DEFAULT_MARKET: Final[str] = "INDIA"

DEFAULT_CURRENCY: Final[str] = "INR"

DEFAULT_TIMEZONE: Final[str] = (
    "Asia/Kolkata"
)


# =========================================================
# EXCHANGES
# =========================================================

NSE: Final[str] = "NSE"

BSE: Final[str] = "BSE"

NFO: Final[str] = "NFO"

BFO: Final[str] = "BFO"

MCX: Final[str] = "MCX"


SUPPORTED_EXCHANGES: Final[
    Tuple[str, ...]
] = (

    NSE,

    BSE,

    NFO,

    BFO,

    MCX,
)


# =========================================================
# TRADING MODE
# =========================================================

class TradingMode(str, Enum):

    INTRADAY = "INTRADAY"

    SWING = "SWING"

    POSITIONAL = "POSITIONAL"


# =========================================================
# MARKET DIRECTION
# =========================================================

class MarketDirection(str, Enum):

    LONG = "LONG"

    SHORT = "SHORT"

    BOTH = "BOTH"


# =========================================================
# SCANNER STATE
# =========================================================

class ScannerState(str, Enum):

    IDLE = "IDLE"

    STARTING = "STARTING"

    RUNNING = "RUNNING"

    STOPPING = "STOPPING"

    STOPPED = "STOPPED"

    ERROR = "ERROR"


# =========================================================
# MARKET SESSION
# =========================================================

class MarketSession(str, Enum):

    PRE_OPEN = "PRE_OPEN"

    OPEN = "OPEN"

    CLOSED = "CLOSED"

    POST_MARKET = "POST_MARKET"


# =========================================================
# MARKET HOURS
# =========================================================

MARKET_PRE_OPEN_HOUR: Final[int] = 9

MARKET_PRE_OPEN_MINUTE: Final[int] = 0


MARKET_OPEN_HOUR: Final[int] = 9

MARKET_OPEN_MINUTE: Final[int] = 15


MARKET_CLOSE_HOUR: Final[int] = 15

MARKET_CLOSE_MINUTE: Final[int] = 30


# =========================================================
# TIMEFRAMES
# =========================================================

TIMEFRAME_1M: Final[str] = "1m"

TIMEFRAME_3M: Final[str] = "3m"

TIMEFRAME_5M: Final[str] = "5m"

TIMEFRAME_10M: Final[str] = "10m"

TIMEFRAME_15M: Final[str] = "15m"

TIMEFRAME_30M: Final[str] = "30m"

TIMEFRAME_45M: Final[str] = "45m"

TIMEFRAME_1H: Final[str] = "1h"

TIMEFRAME_2H: Final[str] = "2h"

TIMEFRAME_4H: Final[str] = "4h"

TIMEFRAME_1D: Final[str] = "1d"

TIMEFRAME_1W: Final[str] = "1w"

TIMEFRAME_1MO: Final[str] = "1M"

TIMEFRAME_2MO: Final[str] = "2M"

TIMEFRAME_3MO: Final[str] = "3M"


# =========================================================
# INTRADAY TIMEFRAMES
# =========================================================

INTRADAY_TIMEFRAMES: Final[
    Tuple[str, ...]
] = (

    TIMEFRAME_1M,

    TIMEFRAME_3M,

    TIMEFRAME_5M,

    TIMEFRAME_10M,

    TIMEFRAME_15M,

    TIMEFRAME_30M,

    TIMEFRAME_45M,
)


# =========================================================
# SWING TIMEFRAMES
# =========================================================

SWING_TIMEFRAMES: Final[
    Tuple[str, ...]
] = (

    TIMEFRAME_1H,

    TIMEFRAME_2H,

    TIMEFRAME_4H,

    TIMEFRAME_1D,
)


# =========================================================
# POSITIONAL TIMEFRAMES
# =========================================================

POSITIONAL_TIMEFRAMES: Final[
    Tuple[str, ...]
] = (

    TIMEFRAME_1D,

    TIMEFRAME_1W,

    TIMEFRAME_1MO,

    TIMEFRAME_2MO,

    TIMEFRAME_3MO,
)


# =========================================================
# ALL SUPPORTED TIMEFRAMES
# =========================================================

SUPPORTED_TIMEFRAMES: Final[
    Tuple[str, ...]
] = tuple(
    dict.fromkeys(

        INTRADAY_TIMEFRAMES

        + SWING_TIMEFRAMES

        + POSITIONAL_TIMEFRAMES
    )
)


# =========================================================
# DEFAULT TIMEFRAMES
# =========================================================

DEFAULT_INTRADAY_TIMEFRAME: Final[
    str
] = TIMEFRAME_5M


DEFAULT_SWING_TIMEFRAME: Final[
    str
] = TIMEFRAME_1D


DEFAULT_POSITIONAL_TIMEFRAME: Final[
    str
] = TIMEFRAME_1W


# =========================================================
# PRICE FILTERS
# =========================================================

DEFAULT_MIN_PRICE: Final[
    float
] = 200.0


DEFAULT_MAX_PRICE: Final[
    float
] = 100000.0


# =========================================================
# MARKET CAP
# =========================================================

DEFAULT_MIN_MARKET_CAP_CR: Final[
    float
] = 1000.0


# =========================================================
# VOLUME
# =========================================================

DEFAULT_MIN_VOLUME: Final[
    int
] = 100_000


DEFAULT_MIN_AVERAGE_VOLUME: Final[
    int
] = 100_000


DEFAULT_MIN_RVOL: Final[
    float
] = 1.20


INTRADAY_MIN_RVOL: Final[
    float
] = 1.50


STRONG_RVOL: Final[
    float
] = 2.0


VERY_STRONG_RVOL: Final[
    float
] = 3.0


# =========================================================
# GAP FILTER
# =========================================================

DEFAULT_MAX_GAP_PERCENT: Final[
    float
] = 3.0


# =========================================================
# ORB
# =========================================================

DEFAULT_ORB_MINUTES: Final[
    int
] = 15


DEFAULT_MAX_ORB_WIDTH_PERCENT: Final[
    float
] = 3.0


PREFERRED_MAX_ORB_WIDTH_PERCENT: Final[
    float
] = 2.5


# =========================================================
# ADX
# =========================================================

ADX_WEAK: Final[
    float
] = 15.0


ADX_MINIMUM: Final[
    float
] = 20.0


ADX_TRENDING: Final[
    float
] = 25.0


ADX_STRONG: Final[
    float
] = 35.0


ADX_VERY_STRONG: Final[
    float
] = 50.0


# =========================================================
# RSI
# =========================================================

RSI_MIN: Final[
    float
] = 0.0


RSI_MAX: Final[
    float
] = 100.0


RSI_OVERSOLD: Final[
    float
] = 30.0


RSI_NEUTRAL: Final[
    float
] = 50.0


RSI_BULLISH: Final[
    float
] = 55.0


RSI_STRONG_BULLISH: Final[
    float
] = 60.0


RSI_OVERBOUGHT: Final[
    float
] = 70.0


RSI_EXTREME: Final[
    float
] = 80.0


# =========================================================
# RISK MANAGEMENT
# =========================================================

DEFAULT_CAPITAL: Final[
    float
] = 100000.0


DEFAULT_RISK_PERCENT: Final[
    float
] = 1.0


DEFAULT_MIN_RR: Final[
    float
] = 2.0


PREFERRED_RR: Final[
    float
] = 3.0


MAX_RR_FOR_SCORING: Final[
    float
] = 5.0


DEFAULT_ATR_MULTIPLE: Final[
    float
] = 2.0


DEFAULT_MIN_STOP_PERCENT: Final[
    float
] = 0.20


DEFAULT_MAX_STOP_PERCENT: Final[
    float
] = 3.0


# =========================================================
# SCORE THRESHOLDS
# =========================================================

SCORE_MINIMUM: Final[
    float
] = 60.0


SCORE_GOOD: Final[
    float
] = 70.0


SCORE_HIGH_QUALITY: Final[
    float
] = 80.0


SCORE_PREMIUM: Final[
    float
] = 90.0


# =========================================================
# CONFIDENCE
# =========================================================

CONFIDENCE_MINIMUM: Final[
    float
] = 60.0


CONFIDENCE_GOOD: Final[
    float
] = 70.0


CONFIDENCE_HIGH: Final[
    float
] = 80.0


CONFIDENCE_PREMIUM: Final[
    float
] = 90.0


# =========================================================
# GRADES
# =========================================================

GRADE_A_PLUS: Final[str] = "A+"

GRADE_A: Final[str] = "A"

GRADE_B_PLUS: Final[str] = "B+"

GRADE_B: Final[str] = "B"

GRADE_C: Final[str] = "C"

GRADE_D: Final[str] = "D"


# =========================================================
# SCANNER RESULT LIMITS
# =========================================================

DEFAULT_MAX_SIGNALS: Final[
    int
] = 50


DEFAULT_DASHBOARD_SIGNALS: Final[
    int
] = 20


DEFAULT_TOP_SIGNALS: Final[
    int
] = 10


DEFAULT_INTRADAY_TOP_SIGNALS: Final[
    int
] = 5


# =========================================================
# ENGINE
# =========================================================

DEFAULT_MAX_WORKERS: Final[
    int
] = 8


# =========================================================
# SCORE KEYS
# =========================================================

SCORE_KEYS: Final[
    Tuple[str, ...]
] = (

    "trend",

    "volume",

    "momentum",

    "pattern",

    "sector",

    "relative_strength",

    "market",
)


# =========================================================
# SCORE WEIGHTS
# =========================================================

DEFAULT_SCORE_WEIGHTS: Final[
    Dict[str, float]
] = {

    "trend":
        20.0,

    "volume":
        15.0,

    "momentum":
        15.0,

    "pattern":
        20.0,

    "sector":
        10.0,

    "relative_strength":
        10.0,

    "market":
        10.0,
}


# =========================================================
# RANKING WEIGHTS
# =========================================================

DEFAULT_RANKING_WEIGHTS: Final[
    Dict[str, float]
] = {

    "score":
        0.50,

    "confidence":
        0.30,

    "risk_reward":
        0.20,
}


# =========================================================
# PRIORITY WEIGHTS
# =========================================================

DEFAULT_PRIORITY_WEIGHTS: Final[
    Dict[str, float]
] = {

    "score":
        0.45,

    "confidence":
        0.30,

    "risk_reward":
        0.15,

    "volume":
        0.10,
}


# =========================================================
# METADATA KEYS
# =========================================================

META_MARKET_CAP: Final[
    str
] = "market_cap"


META_RANK: Final[
    str
] = "rank"


META_GRADE: Final[
    str
] = "grade"


META_PRIORITY_SCORE: Final[
    str
] = "priority_score"


META_SECTOR: Final[
    str
] = "sector"


META_INDUSTRY: Final[
    str
] = "industry"


META_FNO: Final[
    str
] = "fno"


META_BETA: Final[
    str
] = "beta"


META_SCANNER: Final[
    str
] = "scanner"


META_STRATEGY: Final[
    str
] = "strategy"


# =========================================================
# COMMON MARKET INDEX SYMBOLS
# =========================================================

NIFTY_50: Final[
    str
] = "NIFTY 50"


NIFTY_BANK: Final[
    str
] = "NIFTY BANK"


NIFTY_FIN_SERVICE: Final[
    str
] = "NIFTY FIN SERVICE"


NIFTY_MIDCAP_100: Final[
    str
] = "NIFTY MIDCAP 100"


NIFTY_500: Final[
    str
] = "NIFTY 500"


# =========================================================
# BOOLEAN DEFAULTS
# =========================================================

DEFAULT_REQUIRE_VOLUME_CONFIRMATION: Final[
    bool
] = True


DEFAULT_REQUIRE_MARKET_ALIGNMENT: Final[
    bool
] = True


DEFAULT_REQUIRE_SECTOR_ALIGNMENT: Final[
    bool
] = True


DEFAULT_REMOVE_DUPLICATES: Final[
    bool
] = True


DEFAULT_RANK_RESULTS: Final[
    bool
] = True


# =========================================================
# HELPER : VALID TIMEFRAME
# =========================================================

def is_supported_timeframe(
    timeframe: str,
) -> bool:
    """
    Return True if timeframe is supported.
    """

    return str(
        timeframe
    ).strip() in SUPPORTED_TIMEFRAMES


# =========================================================
# HELPER : TRADING MODE
# =========================================================

def timeframe_mode(
    timeframe: str,
) -> TradingMode | None:
    """
    Determine trading mode from timeframe.
    """

    timeframe = str(
        timeframe
    ).strip()

    if timeframe in INTRADAY_TIMEFRAMES:

        return TradingMode.INTRADAY

    if timeframe in SWING_TIMEFRAMES:

        return TradingMode.SWING

    if timeframe in POSITIONAL_TIMEFRAMES:

        return TradingMode.POSITIONAL

    return None


# =========================================================
# HELPER : SCORE GRADE
# =========================================================

def score_grade(
    score: float,
) -> str:
    """
    Convert numeric score into basic grade.
    """

    score = float(
        score
    )

    if score >= SCORE_PREMIUM:

        return GRADE_A_PLUS

    if score >= SCORE_HIGH_QUALITY:

        return GRADE_A

    if score >= SCORE_GOOD:

        return GRADE_B

    if score >= SCORE_MINIMUM:

        return GRADE_C

    return GRADE_D


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "APP_NAME",
    "APP_VERSION",
    "SCANNER_VERSION",

    "DEFAULT_EXCHANGE",
    "DEFAULT_MARKET",
    "DEFAULT_CURRENCY",
    "DEFAULT_TIMEZONE",

    "NSE",
    "BSE",
    "NFO",
    "BFO",
    "MCX",
    "SUPPORTED_EXCHANGES",

    "TradingMode",
    "MarketDirection",
    "ScannerState",
    "MarketSession",

    "MARKET_PRE_OPEN_HOUR",
    "MARKET_PRE_OPEN_MINUTE",
    "MARKET_OPEN_HOUR",
    "MARKET_OPEN_MINUTE",
    "MARKET_CLOSE_HOUR",
    "MARKET_CLOSE_MINUTE",

    "INTRADAY_TIMEFRAMES",
    "SWING_TIMEFRAMES",
    "POSITIONAL_TIMEFRAMES",
    "SUPPORTED_TIMEFRAMES",

    "DEFAULT_INTRADAY_TIMEFRAME",
    "DEFAULT_SWING_TIMEFRAME",
    "DEFAULT_POSITIONAL_TIMEFRAME",

    "DEFAULT_MIN_PRICE",
    "DEFAULT_MAX_PRICE",
    "DEFAULT_MIN_MARKET_CAP_CR",

    "DEFAULT_MIN_VOLUME",
    "DEFAULT_MIN_AVERAGE_VOLUME",
    "DEFAULT_MIN_RVOL",
    "INTRADAY_MIN_RVOL",
    "STRONG_RVOL",
    "VERY_STRONG_RVOL",

    "DEFAULT_MAX_GAP_PERCENT",

    "DEFAULT_ORB_MINUTES",
    "DEFAULT_MAX_ORB_WIDTH_PERCENT",
    "PREFERRED_MAX_ORB_WIDTH_PERCENT",

    "ADX_WEAK",
    "ADX_MINIMUM",
    "ADX_TRENDING",
    "ADX_STRONG",
    "ADX_VERY_STRONG",

    "RSI_OVERSOLD",
    "RSI_NEUTRAL",
    "RSI_BULLISH",
    "RSI_STRONG_BULLISH",
    "RSI_OVERBOUGHT",
    "RSI_EXTREME",

    "DEFAULT_CAPITAL",
    "DEFAULT_RISK_PERCENT",
    "DEFAULT_MIN_RR",
    "PREFERRED_RR",
    "MAX_RR_FOR_SCORING",
    "DEFAULT_ATR_MULTIPLE",
    "DEFAULT_MIN_STOP_PERCENT",
    "DEFAULT_MAX_STOP_PERCENT",

    "SCORE_MINIMUM",
    "SCORE_GOOD",
    "SCORE_HIGH_QUALITY",
    "SCORE_PREMIUM",

    "CONFIDENCE_MINIMUM",
    "CONFIDENCE_GOOD",
    "CONFIDENCE_HIGH",
    "CONFIDENCE_PREMIUM",

    "GRADE_A_PLUS",
    "GRADE_A",
    "GRADE_B_PLUS",
    "GRADE_B",
    "GRADE_C",
    "GRADE_D",

    "DEFAULT_MAX_SIGNALS",
    "DEFAULT_DASHBOARD_SIGNALS",
    "DEFAULT_TOP_SIGNALS",
    "DEFAULT_INTRADAY_TOP_SIGNALS",

    "DEFAULT_MAX_WORKERS",

    "SCORE_KEYS",
    "DEFAULT_SCORE_WEIGHTS",
    "DEFAULT_RANKING_WEIGHTS",
    "DEFAULT_PRIORITY_WEIGHTS",

    "META_MARKET_CAP",
    "META_RANK",
    "META_GRADE",
    "META_PRIORITY_SCORE",
    "META_SECTOR",
    "META_INDUSTRY",
    "META_FNO",
    "META_BETA",
    "META_SCANNER",
    "META_STRATEGY",

    "NIFTY_50",
    "NIFTY_BANK",
    "NIFTY_FIN_SERVICE",
    "NIFTY_MIDCAP_100",
    "NIFTY_500",

    "is_supported_timeframe",
    "timeframe_mode",
    "score_grade",
]


# ==========================
# END OF FILE
# ==========================