"""
=========================================================
StockVersity Scanner Pro
Signal Model
Version : 2.1
=========================================================

File:
    core/scanner/signal.py

Purpose:
    Canonical signal model used by the complete
    StockVersity scanner subsystem.

Responsibilities
----------------
• Signal representation
• Trading direction
• Pattern classification
• Risk / reward calculation
• Position sizing
• Confidence and scoring
• Signal lifecycle
• Serialization / deserialization
• Copy / update helpers
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


# =========================================================
# SIGNAL TYPE
# =========================================================

class SignalType(str, Enum):

    BUY = "BUY"
    SELL = "SELL"
    EXIT = "EXIT"
    WATCH = "WATCH"
    HOLD = "HOLD"


# =========================================================
# SIGNAL STRENGTH
# =========================================================

class SignalStrength(str, Enum):

    VERY_WEAK = "VERY_WEAK"
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"


# =========================================================
# PATTERN TYPE
# =========================================================

class PatternType(str, Enum):

    ORB = "ORB"

    MOMENTUM = "MOMENTUM"

    BREAKOUT = "BREAKOUT"
    BREAKDOWN = "BREAKDOWN"

    VCP = "VCP"

    BULL_FLAG = "BULL_FLAG"
    BEAR_FLAG = "BEAR_FLAG"

    FALLING_WEDGE = "FALLING_WEDGE"
    RISING_WEDGE = "RISING_WEDGE"

    CUP_HANDLE = "CUP_HANDLE"

    DOUBLE_BOTTOM = "DOUBLE_BOTTOM"
    DOUBLE_TOP = "DOUBLE_TOP"

    ASCENDING_TRIANGLE = "ASCENDING_TRIANGLE"
    DESCENDING_TRIANGLE = "DESCENDING_TRIANGLE"
    SYMMETRICAL_TRIANGLE = "SYMMETRICAL_TRIANGLE"

    RANGE_BREAKOUT = "RANGE_BREAKOUT"

    VWAP_RECLAIM = "VWAP_RECLAIM"

    EMA_CROSS = "EMA_CROSS"

    MACD = "MACD"

    RSI = "RSI"

    OPENING_RANGE = "OPENING_RANGE"

    CUSTOM = "CUSTOM"


# =========================================================
# SIGNAL STATUS
# =========================================================

class SignalStatus(str, Enum):

    ACTIVE = "ACTIVE"

    TRIGGERED = "TRIGGERED"

    EXECUTED = "EXECUTED"

    PARTIAL = "PARTIAL"

    CANCELLED = "CANCELLED"

    EXPIRED = "EXPIRED"


# =========================================================
# MARKET TREND
# =========================================================

class MarketTrend(str, Enum):

    STRONG_BULLISH = "STRONG_BULLISH"

    BULLISH = "BULLISH"

    SIDEWAYS = "SIDEWAYS"

    BEARISH = "BEARISH"

    STRONG_BEARISH = "STRONG_BEARISH"


# =========================================================
# DEFAULT SETTINGS
# =========================================================

DEFAULT_EXCHANGE = "NSE"

DEFAULT_TIMEFRAME = "5m"

DEFAULT_CAPITAL = 100000.0

DEFAULT_RISK_PERCENT = 1.0


# =========================================================
# SCORE KEYS
# =========================================================

SCORE_KEYS = (

    "trend",

    "volume",

    "momentum",

    "pattern",

    "sector",

    "relative_strength",

    "market",

)


# =========================================================
# INTERNAL HELPERS
# =========================================================

def _datetime_to_iso(
    value: Optional[datetime],
) -> Optional[str]:

    if value is None:
        return None

    return value.isoformat()


def _datetime_from_value(
    value: Any,
) -> Optional[datetime]:

    if value is None:
        return None

    if isinstance(
        value,
        datetime,
    ):
        return value

    if isinstance(
        value,
        str,
    ):

        value = value.strip()

        if not value:
            return None

        try:
            return datetime.fromisoformat(
                value
            )

        except ValueError:
            return None

    return None


def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:

    try:

        if value is None:
            return default

        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return default


def _safe_int(
    value: Any,
    default: int = 0,
) -> int:

    try:

        if value is None:
            return default

        return int(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return default


def _safe_enum(
    enum_class,
    value: Any,
    default,
):

    if isinstance(
        value,
        enum_class,
    ):
        return value

    try:

        return enum_class(
            value
        )

    except (
        ValueError,
        TypeError,
    ):

        try:

            return enum_class[
                str(value).upper()
            ]

        except (
            KeyError,
            TypeError,
        ):

            return default


# =========================================================
# SIGNAL MODEL
# =========================================================

@dataclass(slots=True)
class Signal:

    # =====================================================
    # UNIQUE IDENTIFICATION
    # =====================================================

    signal_id: str = field(
        default_factory=lambda: str(
            uuid4()
        )
    )

    instrument_key: str = ""

    symbol: str = ""

    exchange: str = DEFAULT_EXCHANGE

    # =====================================================
    # SIGNAL INFORMATION
    # =====================================================

    signal_type: SignalType = (
        SignalType.BUY
    )

    pattern: PatternType = (
        PatternType.CUSTOM
    )

    strength: SignalStrength = (
        SignalStrength.MODERATE
    )

    status: SignalStatus = (
        SignalStatus.ACTIVE
    )

    scanner_name: str = ""

    scanner_version: str = "2.1"

    strategy_name: str = ""

    strategy_id: str = ""

    # =====================================================
    # MARKET INFORMATION
    # =====================================================

    timeframe: str = (
        DEFAULT_TIMEFRAME
    )

    market_trend: MarketTrend = (
        MarketTrend.SIDEWAYS
    )

    sector: str = ""

    sector_strength: float = 0.0

    market_strength: float = 0.0

    relative_strength: float = 0.0

    beta: float = 0.0

    # =====================================================
    # PRICE INFORMATION
    # =====================================================

    last_price: float = 0.0

    open_price: float = 0.0

    high_price: float = 0.0

    low_price: float = 0.0

    close_price: float = 0.0

    previous_close: float = 0.0

    gap_percent: float = 0.0

    volume: int = 0

    average_volume: int = 0

    volume_ratio: float = 0.0

    # =====================================================
    # ENTRY / EXIT INFORMATION
    # =====================================================

    trigger_price: float = 0.0

    entry: float = 0.0

    stop_loss: float = 0.0

    trail_stop: float = 0.0

    target1: float = 0.0

    target2: float = 0.0

    target3: float = 0.0

    triggered: bool = False

    trigger_time: Optional[
        datetime
    ] = None

    # =====================================================
    # RISK MANAGEMENT
    # =====================================================

    capital: float = (
        DEFAULT_CAPITAL
    )

    risk_percent: float = (
        DEFAULT_RISK_PERCENT
    )

    quantity: int = 0

    risk: float = 0.0

    reward: float = 0.0

    risk_reward: float = 0.0

    expected_profit: float = 0.0

    expected_loss: float = 0.0

    # =====================================================
    # ATR
    # =====================================================

    atr: float = 0.0

    atr_multiple: float = 2.0

    atr_stop: float = 0.0

    # =====================================================
    # INDICATORS
    # =====================================================

    ema9: float = 0.0

    ema20: float = 0.0

    ema21: float = 0.0

    ema50: float = 0.0

    ema100: float = 0.0

    ema200: float = 0.0

    rsi: float = 0.0

    macd: float = 0.0

    macd_signal: float = 0.0

    macd_histogram: float = 0.0

    adx: float = 0.0

    plus_di: float = 0.0

    minus_di: float = 0.0

    vwap: float = 0.0

    supertrend: float = 0.0

    supertrend_direction: int = 0

    # =====================================================
    # CONFIDENCE / SCORE
    # =====================================================

    confidence: float = 0.0

    score: float = 0.0

    score_breakdown: Dict[
        str,
        float,
    ] = field(
        default_factory=lambda: {
            key: 0.0
            for key in SCORE_KEYS
        }
    )

    # =====================================================
    # TIME
    # =====================================================

    candle_time: Optional[
        datetime
    ] = None

    created_at: datetime = field(
        default_factory=datetime.now
    )

    updated_at: datetime = field(
        default_factory=datetime.now
    )

    expires_at: Optional[
        datetime
    ] = None

    # =====================================================
    # EXTRA INFORMATION
    # =====================================================

    remarks: str = ""

    tags: List[str] = field(
        default_factory=list
    )

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    extra: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __post_init__(
        self,
    ) -> None:

        self.signal_id = str(
            self.signal_id
        ).strip() or str(
            uuid4()
        )

        self.instrument_key = str(
            self.instrument_key
        ).strip()

        self.symbol = str(
            self.symbol
        ).strip().upper()

        self.exchange = str(
            self.exchange
        ).strip().upper()

        self.scanner_name = str(
            self.scanner_name
        ).strip()

        self.scanner_version = str(
            self.scanner_version
        ).strip() or "2.1"

        self.strategy_name = str(
            self.strategy_name
        ).strip()

        self.strategy_id = str(
            self.strategy_id
        ).strip()

        self.timeframe = str(
            self.timeframe
        ).strip() or DEFAULT_TIMEFRAME

        self.sector = str(
            self.sector
        ).strip()

        self.remarks = str(
            self.remarks
        )

        # -------------------------------------------------
        # NORMALIZE ENUMS
        # -------------------------------------------------

        self.signal_type = _safe_enum(
            SignalType,
            self.signal_type,
            SignalType.BUY,
        )

        self.pattern = _safe_enum(
            PatternType,
            self.pattern,
            PatternType.CUSTOM,
        )

        self.strength = _safe_enum(
            SignalStrength,
            self.strength,
            SignalStrength.MODERATE,
        )

        self.status = _safe_enum(
            SignalStatus,
            self.status,
            SignalStatus.ACTIVE,
        )

        self.market_trend = _safe_enum(
            MarketTrend,
            self.market_trend,
            MarketTrend.SIDEWAYS,
        )

        # -------------------------------------------------
        # NORMALIZE CONTAINERS
        # -------------------------------------------------

        self.tags = list(
            self.tags or []
        )

        self.metadata = dict(
            self.metadata or {}
        )

        self.extra = dict(
            self.extra or {}
        )

        supplied_scores = dict(
            self.score_breakdown or {}
        )

        self.score_breakdown = {
            key: _safe_float(
                supplied_scores.get(
                    key,
                    0.0,
                )
            )
            for key in SCORE_KEYS
        }

        for key, value in (
            supplied_scores.items()
        ):

            if (
                key
                not in self.score_breakdown
            ):

                self.score_breakdown[
                    key
                ] = _safe_float(
                    value
                )

        # -------------------------------------------------
        # NORMALIZE DATES
        # -------------------------------------------------

        self.trigger_time = (
            _datetime_from_value(
                self.trigger_time
            )
        )

        self.candle_time = (
            _datetime_from_value(
                self.candle_time
            )
        )

        self.created_at = (
            _datetime_from_value(
                self.created_at
            )
            or datetime.now()
        )

        self.updated_at = (
            _datetime_from_value(
                self.updated_at
            )
            or datetime.now()
        )

        self.expires_at = (
            _datetime_from_value(
                self.expires_at
            )
        )

        # -------------------------------------------------
        # NORMALIZE NUMBERS
        # -------------------------------------------------

        self._normalize_numeric_fields()

        # -------------------------------------------------
        # CALCULATE DERIVED VALUES
        # -------------------------------------------------

        self.recalculate()

        # -------------------------------------------------
        # VALIDATE
        # -------------------------------------------------

        self._validate()

    # =====================================================
    # NORMALIZE NUMERIC FIELDS
    # =====================================================

    def _normalize_numeric_fields(
        self,
    ) -> None:

        float_fields = (

            "sector_strength",

            "market_strength",

            "relative_strength",

            "beta",

            "last_price",

            "open_price",

            "high_price",

            "low_price",

            "close_price",

            "previous_close",

            "gap_percent",

            "volume_ratio",

            "trigger_price",

            "entry",

            "stop_loss",

            "trail_stop",

            "target1",

            "target2",

            "target3",

            "capital",

            "risk_percent",

            "risk",

            "reward",

            "risk_reward",

            "expected_profit",

            "expected_loss",

            "atr",

            "atr_multiple",

            "atr_stop",

            "ema9",

            "ema20",

            "ema21",

            "ema50",

            "ema100",

            "ema200",

            "rsi",

            "macd",

            "macd_signal",

            "macd_histogram",

            "adx",

            "plus_di",

            "minus_di",

            "vwap",

            "supertrend",

            "confidence",

            "score",

        )

        for field_name in float_fields:

            setattr(
                self,
                field_name,
                _safe_float(
                    getattr(
                        self,
                        field_name,
                    )
                ),
            )

        self.volume = _safe_int(
            self.volume
        )

        self.average_volume = (
            _safe_int(
                self.average_volume
            )
        )

        self.quantity = _safe_int(
            self.quantity
        )

        self.supertrend_direction = (
            _safe_int(
                self.supertrend_direction
            )
        )

    # =====================================================
    # VALIDATION
    # =====================================================

    def _validate(
        self,
    ) -> None:

        if not self.instrument_key:

            raise ValueError(
                "instrument_key cannot be empty."
            )

        if not self.symbol:

            raise ValueError(
                "symbol cannot be empty."
            )

        if self.entry < 0:

            raise ValueError(
                "Entry price cannot be negative."
            )

        if self.stop_loss < 0:

            raise ValueError(
                "Stop loss cannot be negative."
            )

        if self.target1 < 0:

            raise ValueError(
                "Target cannot be negative."
            )

        if not (
            0.0
            <= self.confidence
            <= 100.0
        ):

            raise ValueError(
                "Confidence must be between 0 and 100."
            )

        if not (
            0.0
            <= self.score
            <= 100.0
        ):

            raise ValueError(
                "Score must be between 0 and 100."
            )

        if self.capital <= 0:

            raise ValueError(
                "Capital must be greater than zero."
            )

        if self.risk_percent <= 0:

            raise ValueError(
                "Risk percent must be greater than zero."
            )

        if self.risk_percent > 100:

            raise ValueError(
                "Risk percent cannot exceed 100."
            )

    # =====================================================
    # RECALCULATE
    # =====================================================

    def recalculate(
        self,
    ) -> "Signal":

        self._calculate_risk_reward()

        self._calculate_position_size()

        self._calculate_expected_values()

        return self

    # =====================================================
    # RISK / REWARD
    # =====================================================

    def _calculate_risk_reward(
        self,
    ) -> None:

        self.risk = 0.0

        self.reward = 0.0

        self.risk_reward = 0.0

        if self.entry <= 0:
            return

        if self.stop_loss <= 0:
            return

        if self.target1 <= 0:
            return

        # -------------------------------------------------
        # BUY
        # -------------------------------------------------

        if self.signal_type == SignalType.BUY:

            self.risk = max(
                self.entry
                - self.stop_loss,
                0.0,
            )

            self.reward = max(
                self.target1
                - self.entry,
                0.0,
            )

        # -------------------------------------------------
        # SELL
        # -------------------------------------------------

        elif (
            self.signal_type
            == SignalType.SELL
        ):

            self.risk = max(
                self.stop_loss
                - self.entry,
                0.0,
            )

            self.reward = max(
                self.entry
                - self.target1,
                0.0,
            )

        else:

            return

        self.risk = round(
            self.risk,
            4,
        )

        self.reward = round(
            self.reward,
            4,
        )

        if self.risk > 0:

            self.risk_reward = round(
                self.reward
                / self.risk,
                2,
            )

    # =====================================================
    # POSITION SIZE
    # =====================================================

    def _calculate_position_size(
        self,
    ) -> None:

        if self.risk <= 0:

            self.quantity = 0

            return

        maximum_risk = (
            self.capital
            * self.risk_percent
            / 100.0
        )

        self.quantity = max(
            0,
            int(
                maximum_risk
                / self.risk
            ),
        )

    # =====================================================
    # EXPECTED VALUES
    # =====================================================

    def _calculate_expected_values(
        self,
    ) -> None:

        self.expected_profit = round(
            self.reward
            * self.quantity,
            2,
        )

        self.expected_loss = round(
            self.risk
            * self.quantity,
            2,
        )

    # =====================================================
    # SIGNAL HELPERS
    # =====================================================

    @property
    def is_buy(
        self,
    ) -> bool:

        return (
            self.signal_type
            == SignalType.BUY
        )

    @property
    def is_sell(
        self,
    ) -> bool:

        return (
            self.signal_type
            == SignalType.SELL
        )

    @property
    def is_exit(
        self,
    ) -> bool:

        return (
            self.signal_type
            == SignalType.EXIT
        )

    @property
    def is_watch(
        self,
    ) -> bool:

        return (
            self.signal_type
            == SignalType.WATCH
        )

    @property
    def is_hold(
        self,
    ) -> bool:

        return (
            self.signal_type
            == SignalType.HOLD
        )

    # =====================================================
    # STATUS HELPERS
    # =====================================================

    @property
    def is_active(
        self,
    ) -> bool:

        return (
            self.status
            == SignalStatus.ACTIVE
        )

    @property
    def is_triggered(
        self,
    ) -> bool:

        return (
            self.status
            == SignalStatus.TRIGGERED
        )

    @property
    def is_executed(
        self,
    ) -> bool:

        return (
            self.status
            == SignalStatus.EXECUTED
        )

    @property
    def is_cancelled(
        self,
    ) -> bool:

        return (
            self.status
            == SignalStatus.CANCELLED
        )

    @property
    def is_expired(
        self,
    ) -> bool:

        if self.status == SignalStatus.EXPIRED:

            return True

        if self.expires_at is None:

            return False

        return (
            datetime.now()
            >= self.expires_at
        )

    # =====================================================
    # TARGET HELPERS
    # =====================================================

    @property
    def targets(
        self,
    ) -> List[float]:

        return [
            target
            for target in (
                self.target1,
                self.target2,
                self.target3,
            )
            if target > 0
        ]

    def next_target(
        self,
        current_price: float,
    ) -> Optional[float]:

        current_price = (
            _safe_float(
                current_price
            )
        )

        if self.is_buy:

            for target in sorted(
                self.targets
            ):

                if (
                    target
                    > current_price
                ):

                    return target

        elif self.is_sell:

            for target in sorted(
                self.targets,
                reverse=True,
            ):

                if (
                    target
                    < current_price
                ):

                    return target

        return None

    # =====================================================
    # QUANTITY CALCULATION
    # =====================================================

    def calculate_quantity(
        self,
        capital: Optional[
            float
        ] = None,
        risk_percent: Optional[
            float
        ] = None,
    ) -> int:

        selected_capital = (
            self.capital
            if capital is None
            else _safe_float(
                capital
            )
        )

        selected_risk = (
            self.risk_percent
            if risk_percent is None
            else _safe_float(
                risk_percent
            )
        )

        if selected_capital <= 0:
            return 0

        if selected_risk <= 0:
            return 0

        if self.risk <= 0:
            return 0

        maximum_loss = (
            selected_capital
            * selected_risk
            / 100.0
        )

        return max(
            0,
            int(
                maximum_loss
                / self.risk
            ),
        )

    # =====================================================
    # CONFIDENCE
    # =====================================================

    def set_confidence(
        self,
        value: float,
    ) -> "Signal":

        self.confidence = round(
            max(
                0.0,
                min(
                    100.0,
                    _safe_float(
                        value
                    ),
                ),
            ),
            2,
        )

        self._touch()

        return self

    def increase_confidence(
        self,
        value: float,
    ) -> "Signal":

        return self.set_confidence(
            self.confidence
            + value
        )

    def decrease_confidence(
        self,
        value: float,
    ) -> "Signal":

        return self.set_confidence(
            self.confidence
            - value
        )

    # =====================================================
    # SCORE
    # =====================================================

    def update_score(
        self,
        category: str,
        value: float,
    ) -> "Signal":

        category = str(
            category
        ).strip()

        if not category:

            raise ValueError(
                "Score category cannot be empty."
            )

        self.score_breakdown[
            category
        ] = round(
            _safe_float(
                value
            ),
            2,
        )

        total = sum(
            self.score_breakdown.values()
        )

        self.score = round(
            max(
                0.0,
                min(
                    total,
                    100.0,
                ),
            ),
            2,
        )

        self._touch()

        return self

    # =====================================================
    # STATUS MANAGEMENT
    # =====================================================

    def activate(
        self,
    ) -> "Signal":

        self.status = (
            SignalStatus.ACTIVE
        )

        self._touch()

        return self

    def mark_triggered(
        self,
    ) -> "Signal":

        self.status = (
            SignalStatus.TRIGGERED
        )

        self.triggered = True

        self.trigger_time = (
            datetime.now()
        )

        self._touch()

        return self

    def mark_executed(
        self,
    ) -> "Signal":

        self.status = (
            SignalStatus.EXECUTED
        )

        self._touch()

        return self

    def mark_partial(
        self,
    ) -> "Signal":

        self.status = (
            SignalStatus.PARTIAL
        )

        self._touch()

        return self

    def mark_cancelled(
        self,
    ) -> "Signal":

        self.status = (
            SignalStatus.CANCELLED
        )

        self._touch()

        return self

    def mark_expired(
        self,
    ) -> "Signal":

        self.status = (
            SignalStatus.EXPIRED
        )

        self._touch()

        return self

    # =====================================================
    # EXPIRY
    # =====================================================

    def set_expiry_minutes(
        self,
        minutes: int,
    ) -> "Signal":

        minutes = int(
            minutes
        )

        if minutes <= 0:

            raise ValueError(
                "Expiry minutes must be greater than zero."
            )

        self.expires_at = (
            datetime.now()
            + timedelta(
                minutes=minutes
            )
        )

        self._touch()

        return self

    def set_expiry_hours(
        self,
        hours: int,
    ) -> "Signal":

        hours = int(
            hours
        )

        if hours <= 0:

            raise ValueError(
                "Expiry hours must be greater than zero."
            )

        self.expires_at = (
            datetime.now()
            + timedelta(
                hours=hours
            )
        )

        self._touch()

        return self

    def clear_expiry(
        self,
    ) -> "Signal":

        self.expires_at = None

        self._touch()

        return self

    # =====================================================
    # TOUCH
    # =====================================================

    def _touch(
        self,
    ) -> None:

        self.updated_at = (
            datetime.now()
        )

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        **kwargs: Any,
    ) -> "Signal":

        protected_fields = {
            "risk",
            "reward",
            "risk_reward",
            "quantity",
            "expected_profit",
            "expected_loss",
        }

        for key, value in (
            kwargs.items()
        ):

            if (
                key in protected_fields
            ):
                continue

            if hasattr(
                self,
                key,
            ):

                setattr(
                    self,
                    key,
                    value,
                )

        # Normalize enum fields in case strings were supplied.

        self.signal_type = _safe_enum(
            SignalType,
            self.signal_type,
            SignalType.BUY,
        )

        self.pattern = _safe_enum(
            PatternType,
            self.pattern,
            PatternType.CUSTOM,
        )

        self.strength = _safe_enum(
            SignalStrength,
            self.strength,
            SignalStrength.MODERATE,
        )

        self.status = _safe_enum(
            SignalStatus,
            self.status,
            SignalStatus.ACTIVE,
        )

        self.market_trend = _safe_enum(
            MarketTrend,
            self.market_trend,
            MarketTrend.SIDEWAYS,
        )

        self._normalize_numeric_fields()

        self.recalculate()

        self._touch()

        self._validate()

        return self

    # =====================================================
    # SERIALIZATION
    # =====================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            # ---------------------------------------------
            # IDENTIFICATION
            # ---------------------------------------------

            "signal_id":
                self.signal_id,

            "instrument_key":
                self.instrument_key,

            "symbol":
                self.symbol,

            "exchange":
                self.exchange,

            # ---------------------------------------------
            # SIGNAL
            # ---------------------------------------------

            "signal_type":
                self.signal_type.value,

            "pattern":
                self.pattern.value,

            "strength":
                self.strength.value,

            "status":
                self.status.value,

            "scanner_name":
                self.scanner_name,

            "scanner_version":
                self.scanner_version,

            "strategy_name":
                self.strategy_name,

            "strategy_id":
                self.strategy_id,

            # ---------------------------------------------
            # MARKET
            # ---------------------------------------------

            "timeframe":
                self.timeframe,

            "market_trend":
                self.market_trend.value,

            "sector":
                self.sector,

            "sector_strength":
                self.sector_strength,

            "market_strength":
                self.market_strength,

            "relative_strength":
                self.relative_strength,

            "beta":
                self.beta,

            # ---------------------------------------------
            # PRICE
            # ---------------------------------------------

            "last_price":
                self.last_price,

            "open_price":
                self.open_price,

            "high_price":
                self.high_price,

            "low_price":
                self.low_price,

            "close_price":
                self.close_price,

            "previous_close":
                self.previous_close,

            "gap_percent":
                self.gap_percent,

            "volume":
                self.volume,

            "average_volume":
                self.average_volume,

            "volume_ratio":
                self.volume_ratio,

            # ---------------------------------------------
            # TRADE LEVELS
            # ---------------------------------------------

            "trigger_price":
                self.trigger_price,

            "entry":
                self.entry,

            "stop_loss":
                self.stop_loss,

            "trail_stop":
                self.trail_stop,

            "target1":
                self.target1,

            "target2":
                self.target2,

            "target3":
                self.target3,

            "triggered":
                self.triggered,

            "trigger_time":
                _datetime_to_iso(
                    self.trigger_time
                ),

            # ---------------------------------------------
            # RISK
            # ---------------------------------------------

            "capital":
                self.capital,

            "risk_percent":
                self.risk_percent,

            "quantity":
                self.quantity,

            "risk":
                self.risk,

            "reward":
                self.reward,

            "risk_reward":
                self.risk_reward,

            "expected_profit":
                self.expected_profit,

            "expected_loss":
                self.expected_loss,

            # ---------------------------------------------
            # ATR
            # ---------------------------------------------

            "atr":
                self.atr,

            "atr_multiple":
                self.atr_multiple,

            "atr_stop":
                self.atr_stop,

            # ---------------------------------------------
            # INDICATORS
            # ---------------------------------------------

            "ema9":
                self.ema9,

            "ema20":
                self.ema20,

            "ema21":
                self.ema21,

            "ema50":
                self.ema50,

            "ema100":
                self.ema100,

            "ema200":
                self.ema200,

            "rsi":
                self.rsi,

            "macd":
                self.macd,

            "macd_signal":
                self.macd_signal,

            "macd_histogram":
                self.macd_histogram,

            "adx":
                self.adx,

            "plus_di":
                self.plus_di,

            "minus_di":
                self.minus_di,

            "vwap":
                self.vwap,

            "supertrend":
                self.supertrend,

            "supertrend_direction":
                self.supertrend_direction,

            # ---------------------------------------------
            # SCORE
            # ---------------------------------------------

            "confidence":
                self.confidence,

            "score":
                self.score,

            "score_breakdown":
                dict(
                    self.score_breakdown
                ),

            # ---------------------------------------------
            # TIME
            # ---------------------------------------------

            "candle_time":
                _datetime_to_iso(
                    self.candle_time
                ),

            "created_at":
                _datetime_to_iso(
                    self.created_at
                ),

            "updated_at":
                _datetime_to_iso(
                    self.updated_at
                ),

            "expires_at":
                _datetime_to_iso(
                    self.expires_at
                ),

            # ---------------------------------------------
            # EXTRA
            # ---------------------------------------------

            "remarks":
                self.remarks,

            "tags":
                list(
                    self.tags
                ),

            "metadata":
                dict(
                    self.metadata
                ),

            "extra":
                dict(
                    self.extra
                ),
        }

    # =====================================================
    # DESERIALIZATION
    # =====================================================

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "Signal":

        if not isinstance(
            data,
            dict,
        ):

            raise TypeError(
                "Signal.from_dict expects a dictionary."
            )

        return cls(

            # ---------------------------------------------
            # IDENTIFICATION
            # ---------------------------------------------

            signal_id=data.get(
                "signal_id",
                str(uuid4()),
            ),

            instrument_key=data.get(
                "instrument_key",
                "",
            ),

            symbol=data.get(
                "symbol",
                "",
            ),

            exchange=data.get(
                "exchange",
                DEFAULT_EXCHANGE,
            ),

            # ---------------------------------------------
            # SIGNAL
            # ---------------------------------------------

            signal_type=_safe_enum(
                SignalType,
                data.get(
                    "signal_type"
                ),
                SignalType.BUY,
            ),

            pattern=_safe_enum(
                PatternType,
                data.get(
                    "pattern"
                ),
                PatternType.CUSTOM,
            ),

            strength=_safe_enum(
                SignalStrength,
                data.get(
                    "strength"
                ),
                SignalStrength.MODERATE,
            ),

            status=_safe_enum(
                SignalStatus,
                data.get(
                    "status"
                ),
                SignalStatus.ACTIVE,
            ),

            scanner_name=data.get(
                "scanner_name",
                "",
            ),

            scanner_version=data.get(
                "scanner_version",
                "2.1",
            ),

            strategy_name=data.get(
                "strategy_name",
                "",
            ),

            strategy_id=data.get(
                "strategy_id",
                "",
            ),

            # ---------------------------------------------
            # MARKET
            # ---------------------------------------------

            timeframe=data.get(
                "timeframe",
                DEFAULT_TIMEFRAME,
            ),

            market_trend=_safe_enum(
                MarketTrend,
                data.get(
                    "market_trend"
                ),
                MarketTrend.SIDEWAYS,
            ),

            sector=data.get(
                "sector",
                "",
            ),

            sector_strength=_safe_float(
                data.get(
                    "sector_strength"
                )
            ),

            market_strength=_safe_float(
                data.get(
                    "market_strength"
                )
            ),

            relative_strength=_safe_float(
                data.get(
                    "relative_strength"
                )
            ),

            beta=_safe_float(
                data.get(
                    "beta"
                )
            ),

            # ---------------------------------------------
            # PRICE
            # ---------------------------------------------

            last_price=_safe_float(
                data.get(
                    "last_price"
                )
            ),

            open_price=_safe_float(
                data.get(
                    "open_price"
                )
            ),

            high_price=_safe_float(
                data.get(
                    "high_price"
                )
            ),

            low_price=_safe_float(
                data.get(
                    "low_price"
                )
            ),

            close_price=_safe_float(
                data.get(
                    "close_price"
                )
            ),

            previous_close=_safe_float(
                data.get(
                    "previous_close"
                )
            ),

            gap_percent=_safe_float(
                data.get(
                    "gap_percent"
                )
            ),

            volume=_safe_int(
                data.get(
                    "volume"
                )
            ),

            average_volume=_safe_int(
                data.get(
                    "average_volume"
                )
            ),

            volume_ratio=_safe_float(
                data.get(
                    "volume_ratio"
                )
            ),

            # ---------------------------------------------
            # TRADE LEVELS
            # ---------------------------------------------

            trigger_price=_safe_float(
                data.get(
                    "trigger_price"
                )
            ),

            entry=_safe_float(
                data.get(
                    "entry"
                )
            ),

            stop_loss=_safe_float(
                data.get(
                    "stop_loss"
                )
            ),

            trail_stop=_safe_float(
                data.get(
                    "trail_stop"
                )
            ),

            target1=_safe_float(
                data.get(
                    "target1"
                )
            ),

            target2=_safe_float(
                data.get(
                    "target2"
                )
            ),

            target3=_safe_float(
                data.get(
                    "target3"
                )
            ),

            triggered=bool(
                data.get(
                    "triggered",
                    False,
                )
            ),

            trigger_time=(
                _datetime_from_value(
                    data.get(
                        "trigger_time"
                    )
                )
            ),

            # ---------------------------------------------
            # RISK INPUTS
            # Derived values are recalculated.
            # ---------------------------------------------

            capital=_safe_float(
                data.get(
                    "capital",
                    DEFAULT_CAPITAL,
                ),
                DEFAULT_CAPITAL,
            ),

            risk_percent=_safe_float(
                data.get(
                    "risk_percent",
                    DEFAULT_RISK_PERCENT,
                ),
                DEFAULT_RISK_PERCENT,
            ),

            # ---------------------------------------------
            # ATR
            # ---------------------------------------------

            atr=_safe_float(
                data.get(
                    "atr"
                )
            ),

            atr_multiple=_safe_float(
                data.get(
                    "atr_multiple",
                    2.0,
                ),
                2.0,
            ),

            atr_stop=_safe_float(
                data.get(
                    "atr_stop"
                )
            ),

            # ---------------------------------------------
            # INDICATORS
            # ---------------------------------------------

            ema9=_safe_float(
                data.get(
                    "ema9"
                )
            ),

            ema20=_safe_float(
                data.get(
                    "ema20"
                )
            ),

            ema21=_safe_float(
                data.get(
                    "ema21"
                )
            ),

            ema50=_safe_float(
                data.get(
                    "ema50"
                )
            ),

            ema100=_safe_float(
                data.get(
                    "ema100"
                )
            ),

            ema200=_safe_float(
                data.get(
                    "ema200"
                )
            ),

            rsi=_safe_float(
                data.get(
                    "rsi"
                )
            ),

            macd=_safe_float(
                data.get(
                    "macd"
                )
            ),

            macd_signal=_safe_float(
                data.get(
                    "macd_signal"
                )
            ),

            macd_histogram=_safe_float(
                data.get(
                    "macd_histogram"
                )
            ),

            adx=_safe_float(
                data.get(
                    "adx"
                )
            ),

            plus_di=_safe_float(
                data.get(
                    "plus_di"
                )
            ),

            minus_di=_safe_float(
                data.get(
                    "minus_di"
                )
            ),

            vwap=_safe_float(
                data.get(
                    "vwap"
                )
            ),

            supertrend=_safe_float(
                data.get(
                    "supertrend"
                )
            ),

            supertrend_direction=_safe_int(
                data.get(
                    "supertrend_direction"
                )
            ),

            # ---------------------------------------------
            # SCORE
            # ---------------------------------------------

            confidence=_safe_float(
                data.get(
                    "confidence"
                )
            ),

            score=_safe_float(
                data.get(
                    "score"
                )
            ),

            score_breakdown=dict(
                data.get(
                    "score_breakdown"
                )
                or {}
            ),

            # ---------------------------------------------
            # TIME
            # ---------------------------------------------

            candle_time=(
                _datetime_from_value(
                    data.get(
                        "candle_time"
                    )
                )
            ),

            created_at=(
                _datetime_from_value(
                    data.get(
                        "created_at"
                    )
                )
                or datetime.now()
            ),

            updated_at=(
                _datetime_from_value(
                    data.get(
                        "updated_at"
                    )
                )
                or datetime.now()
            ),

            expires_at=(
                _datetime_from_value(
                    data.get(
                        "expires_at"
                    )
                )
            ),

            # ---------------------------------------------
            # EXTRA
            # ---------------------------------------------

            remarks=data.get(
                "remarks",
                "",
            ),

            tags=list(
                data.get(
                    "tags"
                )
                or []
            ),

            metadata=dict(
                data.get(
                    "metadata"
                )
                or {}
            ),

            extra=dict(
                data.get(
                    "extra"
                )
                or {}
            ),
        )

    # =====================================================
    # COPY
    # =====================================================

    def copy(
        self,
    ) -> "Signal":
        """
        Create independent signal copy.

        All serialized signal information is preserved.
        """

        return Signal.from_dict(
            self.to_dict()
        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> str:

        return (
            f"{self.signal_type.value} | "
            f"{self.symbol} | "
            f"{self.pattern.value} | "
            f"Entry ₹{self.entry:.2f} | "
            f"SL ₹{self.stop_loss:.2f} | "
            f"T1 ₹{self.target1:.2f} | "
            f"RR {self.risk_reward:.2f} | "
            f"Score {self.score:.2f}"
        )

    # =====================================================
    # MAGIC METHODS
    # =====================================================

    def __str__(
        self,
    ) -> str:

        return self.summary()

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"symbol='{self.symbol}', "
            f"type='{self.signal_type.value}', "
            f"pattern='{self.pattern.value}', "
            f"entry={self.entry:.2f}, "
            f"sl={self.stop_loss:.2f}, "
            f"target={self.target1:.2f}, "
            f"rr={self.risk_reward:.2f}, "
            f"score={self.score:.2f}, "
            f"status='{self.status.value}')"
        )


# =========================================================
# FACTORY FUNCTION
# =========================================================

def create_signal(
    instrument_key: str,
    symbol: str,
    signal_type: SignalType,
    pattern: PatternType,
    entry: float,
    stop_loss: float,
    target1: float,
    **kwargs: Any,
) -> Signal:
    """
    Convenience factory for scanner implementations.
    """

    return Signal(

        instrument_key=instrument_key,

        symbol=symbol,

        signal_type=signal_type,

        pattern=pattern,

        entry=entry,

        stop_loss=stop_loss,

        target1=target1,

        **kwargs,
    )


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "Signal",

    "SignalType",

    "SignalStrength",

    "PatternType",

    "SignalStatus",

    "MarketTrend",

    "DEFAULT_EXCHANGE",

    "DEFAULT_TIMEFRAME",

    "DEFAULT_CAPITAL",

    "DEFAULT_RISK_PERCENT",

    "SCORE_KEYS",

    "create_signal",
]


# =========================================================
# END OF FILE
# =========================================================