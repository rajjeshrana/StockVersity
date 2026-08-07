"""
=========================================================
StockVersity Scanner Pro
Market Data Validator
Version : 2.0
=========================================================

Validates incoming scanner market data before strategy
logic is executed.

Responsibilities
----------------
• Validate OHLCV structure
• Validate candle values
• Detect malformed candles
• Detect duplicate timestamps
• Detect unsorted candles
• Detect stale data
• Validate minimum history
• Validate symbol / instrument information
• Clean invalid candle records
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime
from datetime import timedelta
from datetime import timezone

from math import isfinite

from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Mapping
from typing import Optional
from typing import Sequence
from typing import Tuple


# =========================================================
# VALIDATION RESULT
# =========================================================

@dataclass(slots=True)
class MarketDataValidationResult:
    """
    Result returned by MarketDataValidator.
    """

    valid: bool = True

    errors: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    total_rows: int = 0

    valid_rows: int = 0

    invalid_rows: int = 0

    duplicate_rows: int = 0

    stale: bool = False

    checks: Dict[str, bool] = field(
        default_factory=dict
    )

    # =====================================================
    # ERROR
    # =====================================================

    def add_error(
        self,
        message: str,
        *,
        check: Optional[str] = None,
    ) -> None:

        self.valid = False

        self.errors.append(
            str(message)
        )

        if check:

            self.checks[
                check
            ] = False

    # =====================================================
    # WARNING
    # =====================================================

    def add_warning(
        self,
        message: str,
    ) -> None:

        self.warnings.append(
            str(message)
        )

    # =====================================================
    # PASS
    # =====================================================

    def pass_check(
        self,
        name: str,
    ) -> None:

        if name not in self.checks:

            self.checks[
                name
            ] = True

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "valid":
                self.valid,

            "errors":
                list(
                    self.errors
                ),

            "warnings":
                list(
                    self.warnings
                ),

            "total_rows":
                self.total_rows,

            "valid_rows":
                self.valid_rows,

            "invalid_rows":
                self.invalid_rows,

            "duplicate_rows":
                self.duplicate_rows,

            "stale":
                self.stale,

            "checks":
                dict(
                    self.checks
                ),
        }

    def __bool__(
        self,
    ) -> bool:

        return self.valid


# =========================================================
# DATA VALIDATOR
# =========================================================

class MarketDataValidator:
    """
    Validate scanner input data.

    Supported input styles
    ----------------------
    • List[dict]
    • Tuple[dict, ...]
    • Dictionary containing "candles"
    • Dictionary containing "data"
    • Dictionary containing "ohlcv"

    Candle aliases are supported for common field names.
    """

    OPEN_KEYS: Tuple[str, ...] = (
        "open",
        "o",
        "open_price",
    )

    HIGH_KEYS: Tuple[str, ...] = (
        "high",
        "h",
        "high_price",
    )

    LOW_KEYS: Tuple[str, ...] = (
        "low",
        "l",
        "low_price",
    )

    CLOSE_KEYS: Tuple[str, ...] = (
        "close",
        "c",
        "close_price",
        "ltp",
        "last_price",
    )

    VOLUME_KEYS: Tuple[str, ...] = (
        "volume",
        "v",
        "vol",
    )

    TIMESTAMP_KEYS: Tuple[str, ...] = (
        "timestamp",
        "time",
        "datetime",
        "date",
        "ts",
    )

    SYMBOL_KEYS: Tuple[str, ...] = (
        "symbol",
        "trading_symbol",
        "tradingsymbol",
    )

    INSTRUMENT_KEYS: Tuple[str, ...] = (
        "instrument_key",
        "instrument_token",
        "token",
    )

    def __init__(
        self,
        *,
        minimum_candles: int = 20,
        maximum_stale_minutes: int = 15,
        require_volume: bool = True,
        require_timestamp: bool = True,
    ) -> None:

        self.minimum_candles = max(
            1,
            int(minimum_candles),
        )

        self.maximum_stale_minutes = max(
            0,
            int(maximum_stale_minutes),
        )

        self.require_volume = bool(
            require_volume
        )

        self.require_timestamp = bool(
            require_timestamp
        )

    # =====================================================
    # NUMBER
    # =====================================================

    @staticmethod
    def _number(
        value: Any,
    ) -> bool:

        try:

            return isfinite(
                float(value)
            )

        except (
            TypeError,
            ValueError,
        ):

            return False

    # =====================================================
    # VALUE LOOKUP
    # =====================================================

    @staticmethod
    def _first(
        record: Mapping[str, Any],
        keys: Iterable[str],
        default: Any = None,
    ) -> Any:

        for key in keys:

            if key in record:

                value = record[
                    key
                ]

                if value is not None:

                    return value

        return default

    # =====================================================
    # DATETIME PARSER
    # =====================================================

    @staticmethod
    def _parse_datetime(
        value: Any,
    ) -> Optional[datetime]:

        if value is None:

            return None

        if isinstance(
            value,
            datetime,
        ):

            return value

        # ---------------------------------------------
        # UNIX TIMESTAMP
        # ---------------------------------------------

        if isinstance(
            value,
            (int, float),
        ):

            try:

                numeric = float(
                    value
                )

                # Millisecond timestamp

                if numeric > 10_000_000_000:

                    numeric /= 1000.0

                return datetime.fromtimestamp(
                    numeric,
                    tz=timezone.utc,
                )

            except (
                ValueError,
                OverflowError,
                OSError,
            ):

                return None

        # ---------------------------------------------
        # STRING
        # ---------------------------------------------

        text = str(
            value
        ).strip()

        if not text:

            return None

        # ISO strings with Z suffix

        if text.endswith(
            "Z"
        ):

            text = (
                text[:-1]
                + "+00:00"
            )

        try:

            return datetime.fromisoformat(
                text
            )

        except ValueError:

            pass

        formats = (

            "%Y-%m-%d %H:%M:%S",

            "%Y-%m-%d %H:%M",

            "%Y-%m-%d",

            "%d-%m-%Y %H:%M:%S",

            "%d-%m-%Y %H:%M",

            "%d-%m-%Y",
        )

        for fmt in formats:

            try:

                return datetime.strptime(
                    text,
                    fmt,
                )

            except ValueError:

                continue

        return None

    # =====================================================
    # EXTRACT CANDLES
    # =====================================================

    def extract_candles(
        self,
        market_data: Any,
    ) -> List[Mapping[str, Any]]:
        """
        Extract candle records from common input formats.
        """

        if market_data is None:

            return []

        if isinstance(
            market_data,
            (list, tuple),
        ):

            return [

                row

                for row in market_data

                if isinstance(
                    row,
                    Mapping,
                )
            ]

        if isinstance(
            market_data,
            Mapping,
        ):

            for key in (
                "candles",
                "data",
                "ohlcv",
                "history",
                "records",
            ):

                value = market_data.get(
                    key
                )

                if isinstance(
                    value,
                    (list, tuple),
                ):

                    return [

                        row

                        for row in value

                        if isinstance(
                            row,
                            Mapping,
                        )
                    ]

            # Single candle dictionary

            has_ohlc = all(

                self._first(
                    market_data,
                    keys,
                ) is not None

                for keys in (
                    self.OPEN_KEYS,
                    self.HIGH_KEYS,
                    self.LOW_KEYS,
                    self.CLOSE_KEYS,
                )
            )

            if has_ohlc:

                return [
                    market_data
                ]

        return []

    # =====================================================
    # NORMALIZE CANDLE
    # =====================================================

    def normalize_candle(
        self,
        candle: Mapping[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Convert a candle into StockVersity standard keys.
        """

        open_value = self._first(
            candle,
            self.OPEN_KEYS,
        )

        high_value = self._first(
            candle,
            self.HIGH_KEYS,
        )

        low_value = self._first(
            candle,
            self.LOW_KEYS,
        )

        close_value = self._first(
            candle,
            self.CLOSE_KEYS,
        )

        volume_value = self._first(
            candle,
            self.VOLUME_KEYS,
            0,
        )

        timestamp_value = self._first(
            candle,
            self.TIMESTAMP_KEYS,
        )

        values = (
            open_value,
            high_value,
            low_value,
            close_value,
        )

        if not all(
            self._number(value)
            for value in values
        ):

            return None

        if not self._number(
            volume_value
        ):

            return None

        normalized = {

            "open":
                float(open_value),

            "high":
                float(high_value),

            "low":
                float(low_value),

            "close":
                float(close_value),

            "volume":
                float(volume_value),

            "timestamp":
                self._parse_datetime(
                    timestamp_value
                ),

            "raw":
                candle,
        }

        return normalized

    # =====================================================
    # VALIDATE CANDLE
    # =====================================================

    def validate_candle(
        self,
        candle: Mapping[str, Any],
    ) -> Tuple[bool, List[str]]:
        """
        Validate one OHLCV candle.
        """

        errors: List[str] = []

        normalized = (
            self.normalize_candle(
                candle
            )
        )

        if normalized is None:

            return (
                False,
                [
                    "Candle contains invalid OHLCV values."
                ],
            )

        open_price = normalized[
            "open"
        ]

        high_price = normalized[
            "high"
        ]

        low_price = normalized[
            "low"
        ]

        close_price = normalized[
            "close"
        ]

        volume = normalized[
            "volume"
        ]

        timestamp = normalized[
            "timestamp"
        ]

        # ---------------------------------------------
        # POSITIVE PRICES
        # ---------------------------------------------

        if min(
            open_price,
            high_price,
            low_price,
            close_price,
        ) <= 0:

            errors.append(
                "OHLC prices must be greater than zero."
            )

        # ---------------------------------------------
        # HIGH STRUCTURE
        # ---------------------------------------------

        if high_price < max(
            open_price,
            close_price,
            low_price,
        ):

            errors.append(
                "High price is below another OHLC value."
            )

        # ---------------------------------------------
        # LOW STRUCTURE
        # ---------------------------------------------

        if low_price > min(
            open_price,
            close_price,
            high_price,
        ):

            errors.append(
                "Low price is above another OHLC value."
            )

        # ---------------------------------------------
        # HIGH / LOW
        # ---------------------------------------------

        if high_price < low_price:

            errors.append(
                "High price cannot be below low price."
            )

        # ---------------------------------------------
        # VOLUME
        # ---------------------------------------------

        if volume < 0:

            errors.append(
                "Volume cannot be negative."
            )

        if (
            self.require_volume
            and volume <= 0
        ):

            errors.append(
                "Volume is missing or zero."
            )

        # ---------------------------------------------
        # TIMESTAMP
        # ---------------------------------------------

        if (
            self.require_timestamp
            and timestamp is None
        ):

            errors.append(
                "Timestamp is missing or invalid."
            )

        return (
            len(errors) == 0,
            errors,
        )

    # =====================================================
    # CLEAN CANDLES
    # =====================================================

    def clean(
        self,
        market_data: Any,
        *,
        sort: bool = True,
        remove_duplicates: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Normalize and remove invalid candle records.
        """

        candles = (
            self.extract_candles(
                market_data
            )
        )

        cleaned: List[
            Dict[str, Any]
        ] = []

        seen = set()

        for candle in candles:

            valid, _ = (
                self.validate_candle(
                    candle
                )
            )

            if not valid:

                continue

            normalized = (
                self.normalize_candle(
                    candle
                )
            )

            if normalized is None:

                continue

            timestamp = normalized[
                "timestamp"
            ]

            if (
                remove_duplicates
                and timestamp is not None
            ):

                key = (
                    timestamp.isoformat()
                )

                if key in seen:

                    continue

                seen.add(
                    key
                )

            cleaned.append(
                normalized
            )

        if sort:

            with_timestamp = all(
                candle[
                    "timestamp"
                ] is not None
                for candle in cleaned
            )

            if with_timestamp:

                cleaned.sort(
                    key=lambda row: row[
                        "timestamp"
                    ]
                )

        return cleaned

    # =====================================================
    # STALE CHECK
    # =====================================================

    def is_stale(
        self,
        candles: Sequence[
            Mapping[str, Any]
        ],
        *,
        now: Optional[datetime] = None,
    ) -> bool:
        """
        Determine whether latest candle is stale.

        maximum_stale_minutes = 0 disables stale checking.
        """

        if self.maximum_stale_minutes <= 0:

            return False

        if not candles:

            return True

        latest_value = self._first(
            candles[-1],
            self.TIMESTAMP_KEYS,
        )

        # Normalized candle

        if (
            latest_value is None
            and "timestamp" in candles[-1]
        ):

            latest_value = candles[
                -1
            ].get(
                "timestamp"
            )

        latest = self._parse_datetime(
            latest_value
        )

        if latest is None:

            return False

        current = (
            now
            if now is not None
            else datetime.now(
                tz=latest.tzinfo
            )
        )

        # Avoid aware / naive datetime mismatch.

        if (
            latest.tzinfo is None
            and current.tzinfo is not None
        ):

            current = current.replace(
                tzinfo=None
            )

        elif (
            latest.tzinfo is not None
            and current.tzinfo is None
        ):

            current = current.replace(
                tzinfo=latest.tzinfo
            )

        age = (
            current
            - latest
        )

        return age > timedelta(
            minutes=self.maximum_stale_minutes
        )

    # =====================================================
    # SYMBOL VALIDATION
    # =====================================================

    def validate_identity(
        self,
        market_data: Any,
        result: MarketDataValidationResult,
    ) -> None:
        """
        Validate symbol/instrument identity when supplied.
        """

        if not isinstance(
            market_data,
            Mapping,
        ):

            result.pass_check(
                "identity"
            )

            return

        symbol = self._first(
            market_data,
            self.SYMBOL_KEYS,
        )

        instrument = self._first(
            market_data,
            self.INSTRUMENT_KEYS,
        )

        # Market-data batches may not contain identity
        # because symbol can be supplied externally.

        if (
            symbol is None
            and instrument is None
        ):

            result.add_warning(
                "Symbol/instrument identity not present in market data."
            )

        result.pass_check(
            "identity"
        )

    # =====================================================
    # COMPLETE VALIDATION
    # =====================================================

    def validate(
        self,
        market_data: Any,
        *,
        check_stale: bool = False,
        now: Optional[datetime] = None,
    ) -> MarketDataValidationResult:
        """
        Perform complete market-data validation.
        """

        result = (
            MarketDataValidationResult()
        )

        candles = (
            self.extract_candles(
                market_data
            )
        )

        result.total_rows = len(
            candles
        )

        # ---------------------------------------------
        # DATA EXISTS
        # ---------------------------------------------

        if not candles:

            result.add_error(
                "No OHLCV candle data available.",
                check="data_exists",
            )

            return result

        result.pass_check(
            "data_exists"
        )

        # ---------------------------------------------
        # MINIMUM HISTORY
        # ---------------------------------------------

        if (
            len(candles)
            < self.minimum_candles
        ):

            result.add_error(
                (
                    f"Only {len(candles)} candles available; "
                    f"minimum {self.minimum_candles} required."
                ),
                check="minimum_history",
            )

        else:

            result.pass_check(
                "minimum_history"
            )

        # ---------------------------------------------
        # CANDLE VALIDATION
        # ---------------------------------------------

        normalized_valid: List[
            Dict[str, Any]
        ] = []

        timestamps: List[
            datetime
        ] = []

        seen_timestamps = set()

        for index, candle in enumerate(
            candles
        ):

            valid, errors = (
                self.validate_candle(
                    candle
                )
            )

            if not valid:

                result.invalid_rows += 1

                for error in errors:

                    result.add_warning(
                        (
                            f"Candle {index}: "
                            f"{error}"
                        )
                    )

                continue

            normalized = (
                self.normalize_candle(
                    candle
                )
            )

            if normalized is None:

                result.invalid_rows += 1

                continue

            result.valid_rows += 1

            normalized_valid.append(
                normalized
            )

            timestamp = normalized[
                "timestamp"
            ]

            if timestamp is not None:

                timestamp_key = (
                    timestamp.isoformat()
                )

                if (
                    timestamp_key
                    in seen_timestamps
                ):

                    result.duplicate_rows += 1

                else:

                    seen_timestamps.add(
                        timestamp_key
                    )

                timestamps.append(
                    timestamp
                )

        # ---------------------------------------------
        # VALID ROWS
        # ---------------------------------------------

        if result.valid_rows <= 0:

            result.add_error(
                "No valid OHLCV candles remain.",
                check="valid_candles",
            )

        else:

            result.pass_check(
                "valid_candles"
            )

        # ---------------------------------------------
        # INVALID ROW WARNING
        # ---------------------------------------------

        if result.invalid_rows > 0:

            result.add_warning(
                (
                    f"{result.invalid_rows} malformed "
                    f"candle(s) detected."
                )
            )

        # ---------------------------------------------
        # DUPLICATES
        # ---------------------------------------------

        if result.duplicate_rows > 0:

            result.add_warning(
                (
                    f"{result.duplicate_rows} duplicate "
                    f"timestamp(s) detected."
                )
            )

            result.checks[
                "duplicates"
            ] = False

        else:

            result.pass_check(
                "duplicates"
            )

        # ---------------------------------------------
        # SORT ORDER
        # ---------------------------------------------

        if len(timestamps) >= 2:

            sorted_timestamps = sorted(
                timestamps
            )

            if timestamps != sorted_timestamps:

                result.add_warning(
                    "Candles are not sorted by timestamp."
                )

                result.checks[
                    "chronological_order"
                ] = False

            else:

                result.pass_check(
                    "chronological_order"
                )

        else:

            result.pass_check(
                "chronological_order"
            )

        # ---------------------------------------------
        # STALE DATA
        # ---------------------------------------------

        if (
            check_stale
            and normalized_valid
        ):

            result.stale = (
                self.is_stale(
                    normalized_valid,
                    now=now,
                )
            )

            if result.stale:

                result.add_error(
                    "Latest market data is stale.",
                    check="freshness",
                )

            else:

                result.pass_check(
                    "freshness"
                )

        # ---------------------------------------------
        # IDENTITY
        # ---------------------------------------------

        self.validate_identity(
            market_data,
            result,
        )

        # ---------------------------------------------
        # FINAL STATE
        # ---------------------------------------------

        result.valid = (
            len(result.errors) == 0
        )

        return result

    # =====================================================
    # SIMPLE BOOL
    # =====================================================

    def is_valid(
        self,
        market_data: Any,
        *,
        check_stale: bool = False,
    ) -> bool:

        return self.validate(
            market_data,
            check_stale=check_stale,
        ).valid

    # =====================================================
    # LATEST CANDLE
    # =====================================================

    def latest(
        self,
        market_data: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Return latest valid normalized candle.
        """

        candles = self.clean(
            market_data
        )

        if not candles:

            return None

        return candles[
            -1
        ]

    # =====================================================
    # OHLCV ARRAYS
    # =====================================================

    def arrays(
        self,
        market_data: Any,
    ) -> Dict[str, List[float]]:
        """
        Return normalized OHLCV arrays.

        Useful for indicator calculations.
        """

        candles = self.clean(
            market_data
        )

        return {

            "open": [
                candle["open"]
                for candle in candles
            ],

            "high": [
                candle["high"]
                for candle in candles
            ],

            "low": [
                candle["low"]
                for candle in candles
            ],

            "close": [
                candle["close"]
                for candle in candles
            ],

            "volume": [
                candle["volume"]
                for candle in candles
            ],
        }


# =========================================================
# GLOBAL VALIDATOR
# =========================================================

market_data_validator = (
    MarketDataValidator()
)


# =========================================================
# CONVENIENCE FUNCTIONS
# =========================================================

def validate_market_data(
    market_data: Any,
    *,
    check_stale: bool = False,
) -> MarketDataValidationResult:
    """
    Validate market data using global validator.
    """

    return (
        market_data_validator
        .validate(
            market_data,
            check_stale=check_stale,
        )
    )


def clean_market_data(
    market_data: Any,
) -> List[Dict[str, Any]]:
    """
    Clean and normalize market data.
    """

    return (
        market_data_validator
        .clean(market_data)
    )


def market_data_arrays(
    market_data: Any,
) -> Dict[str, List[float]]:
    """
    Convert market data into OHLCV arrays.
    """

    return (
        market_data_validator
        .arrays(market_data)
    )


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "MarketDataValidationResult",

    "MarketDataValidator",

    "market_data_validator",

    "validate_market_data",

    "clean_market_data",

    "market_data_arrays",
]


# ==========================
# END OF FILE
# ==========================