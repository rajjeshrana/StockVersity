"""
=========================================================
StockVersity Scanner Pro
Scanner Data Adapter
Version : 2.0
=========================================================

Converts raw/live market data into a standard structure
used by StockVersity scanners.

Architecture
------------

Upstox / Market Provider
        ↓
Market Data Parser
        ↓
ScannerDataAdapter
        ↓
ScannerController
        ↓
ScannerService
        ↓
Scanner Engine
        ↓
Individual Scanners
=========================================================
"""

from __future__ import annotations

from datetime import datetime

from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Mapping
from typing import Optional


# =========================================================
# DEFAULT VALUES
# =========================================================

DEFAULT_EXCHANGE = "NSE"

DEFAULT_TIMEFRAME = "5m"


# =========================================================
# SCANNER DATA ADAPTER
# =========================================================

class ScannerDataAdapter:
    """
    Normalize raw market data for the scanner system.

    Every stock is converted into a common dictionary.

    Example
    -------

    {
        "NSE_EQ|INE002A01018": {
            "instrument_key": "NSE_EQ|INE002A01018",
            "symbol": "RELIANCE",
            "exchange": "NSE",
            "last_price": 1450.50,
            "open": 1430.00,
            "high": 1460.00,
            "low": 1425.00,
            "close": 1450.50,
            "previous_close": 1428.00,
            "volume": 1500000,
            "timeframe": "5m"
        }
    }
    """

    def __init__(
        self,
        *,
        exchange: str = DEFAULT_EXCHANGE,
        timeframe: str = DEFAULT_TIMEFRAME,
    ) -> None:

        self.exchange = exchange.upper()

        self.timeframe = timeframe

        self.last_adapted_at: Optional[
            datetime
        ] = None

        self.last_count: int = 0

        self.errors: List[str] = []

    # =====================================================
    # SAFE FLOAT
    # =====================================================

    @staticmethod
    def _float(
        value: Any,
        default: float = 0.0,
    ) -> float:

        if value is None:
            return default

        try:
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

        if value is None:
            return default

        try:
            return int(float(value))

        except (
            TypeError,
            ValueError,
        ):
            return default

    # =====================================================
    # FIRST AVAILABLE VALUE
    # =====================================================

    @staticmethod
    def _first(
        data: Mapping[str, Any],
        *keys: str,
        default: Any = None,
    ) -> Any:

        for key in keys:

            value = data.get(key)

            if value is not None:
                return value

        return default

    # =====================================================
    # NORMALIZE SYMBOL
    # =====================================================

    @staticmethod
    def normalize_symbol(
        symbol: Any,
    ) -> str:

        if symbol is None:
            return ""

        return str(
            symbol
        ).strip().upper()

    # =====================================================
    # NORMALIZE INSTRUMENT KEY
    # =====================================================

    @staticmethod
    def normalize_instrument_key(
        instrument_key: Any,
    ) -> str:

        if instrument_key is None:
            return ""

        return str(
            instrument_key
        ).strip()

    # =====================================================
    # NORMALIZE EXCHANGE
    # =====================================================

    def normalize_exchange(
        self,
        exchange: Any,
    ) -> str:

        if not exchange:
            return self.exchange

        value = str(
            exchange
        ).strip().upper()

        # Upstox may use NSE_EQ etc.
        if value.startswith("NSE"):
            return "NSE"

        if value.startswith("BSE"):
            return "BSE"

        return value

    # =====================================================
    # GAP PERCENT
    # =====================================================

    @staticmethod
    def calculate_gap_percent(
        open_price: float,
        previous_close: float,
    ) -> float:

        if previous_close <= 0:
            return 0.0

        return round(

            (
                (
                    open_price
                    - previous_close
                )
                / previous_close
            )
            * 100,

            2,

        )

    # =====================================================
    # VOLUME RATIO
    # =====================================================

    @staticmethod
    def calculate_volume_ratio(
        volume: int,
        average_volume: int,
    ) -> float:

        if average_volume <= 0:
            return 0.0

        return round(

            volume
            / average_volume,

            2,

        )

    # =====================================================
    # ADAPT SINGLE RECORD
    # =====================================================

    def adapt_record(
        self,
        raw: Mapping[str, Any],
        *,
        fallback_instrument_key: str = "",
    ) -> Dict[str, Any]:
        """
        Normalize one stock record.
        """

        instrument_key = (
            self.normalize_instrument_key(
                self._first(
                    raw,
                    "instrument_key",
                    "instrumentKey",
                    "instrument",
                    "key",
                    default=fallback_instrument_key,
                )
            )
        )

        symbol = self.normalize_symbol(
            self._first(
                raw,
                "symbol",
                "trading_symbol",
                "tradingSymbol",
                "tradingsymbol",
                default="",
            )
        )

        exchange = (
            self.normalize_exchange(
                self._first(
                    raw,
                    "exchange",
                    "segment",
                    "exchange_segment",
                    default=self.exchange,
                )
            )
        )

        last_price = self._float(
            self._first(
                raw,
                "last_price",
                "ltp",
                "lastPrice",
                "price",
                "close",
                default=0.0,
            )
        )

        open_price = self._float(
            self._first(
                raw,
                "open",
                "open_price",
                "openPrice",
                default=0.0,
            )
        )

        high_price = self._float(
            self._first(
                raw,
                "high",
                "high_price",
                "highPrice",
                default=0.0,
            )
        )

        low_price = self._float(
            self._first(
                raw,
                "low",
                "low_price",
                "lowPrice",
                default=0.0,
            )
        )

        close_price = self._float(
            self._first(
                raw,
                "close",
                "close_price",
                "closePrice",
                "ltp",
                "last_price",
                default=last_price,
            )
        )

        previous_close = self._float(
            self._first(
                raw,
                "previous_close",
                "prev_close",
                "previousClose",
                "prevClose",
                "cp",
                default=0.0,
            )
        )

        volume = self._int(
            self._first(
                raw,
                "volume",
                "vol",
                "total_volume",
                "totalVolume",
                default=0,
            )
        )

        average_volume = self._int(
            self._first(
                raw,
                "average_volume",
                "avg_volume",
                "averageVolume",
                "avgVolume",
                default=0,
            )
        )

        volume_ratio = self._float(
            self._first(
                raw,
                "volume_ratio",
                "rvol",
                "relative_volume",
                default=0.0,
            )
        )

        if (
            volume_ratio <= 0
            and average_volume > 0
        ):

            volume_ratio = (
                self.calculate_volume_ratio(
                    volume,
                    average_volume,
                )
            )

        gap_percent = self._float(
            self._first(
                raw,
                "gap_percent",
                "gap",
                "gapPercent",
                default=0.0,
            )
        )

        if (
            gap_percent == 0.0
            and open_price > 0
            and previous_close > 0
        ):

            gap_percent = (
                self.calculate_gap_percent(
                    open_price,
                    previous_close,
                )
            )

        timestamp = self._first(
            raw,
            "timestamp",
            "time",
            "candle_time",
            "candleTime",
            default=None,
        )

        sector = str(
            self._first(
                raw,
                "sector",
                default="",
            )
            or ""
        ).strip()

        market_cap = self._float(
            self._first(
                raw,
                "market_cap",
                "marketCap",
                "mcap",
                default=0.0,
            )
        )

        beta = self._float(
            self._first(
                raw,
                "beta",
                default=0.0,
            )
        )

        # =================================================
        # INDICATORS
        # =================================================

        ema9 = self._float(
            self._first(
                raw,
                "ema9",
                "ema_9",
                default=0.0,
            )
        )

        ema20 = self._float(
            self._first(
                raw,
                "ema20",
                "ema_20",
                default=0.0,
            )
        )

        ema21 = self._float(
            self._first(
                raw,
                "ema21",
                "ema_21",
                default=0.0,
            )
        )

        ema50 = self._float(
            self._first(
                raw,
                "ema50",
                "ema_50",
                default=0.0,
            )
        )

        ema100 = self._float(
            self._first(
                raw,
                "ema100",
                "ema_100",
                default=0.0,
            )
        )

        ema200 = self._float(
            self._first(
                raw,
                "ema200",
                "ema_200",
                default=0.0,
            )
        )

        rsi = self._float(
            self._first(
                raw,
                "rsi",
                "rsi14",
                default=0.0,
            )
        )

        macd = self._float(
            self._first(
                raw,
                "macd",
                default=0.0,
            )
        )

        macd_signal = self._float(
            self._first(
                raw,
                "macd_signal",
                "macdSignal",
                default=0.0,
            )
        )

        macd_histogram = self._float(
            self._first(
                raw,
                "macd_histogram",
                "macdHistogram",
                "macd_hist",
                default=0.0,
            )
        )

        adx = self._float(
            self._first(
                raw,
                "adx",
                default=0.0,
            )
        )

        plus_di = self._float(
            self._first(
                raw,
                "plus_di",
                "plusDI",
                default=0.0,
            )
        )

        minus_di = self._float(
            self._first(
                raw,
                "minus_di",
                "minusDI",
                default=0.0,
            )
        )

        vwap = self._float(
            self._first(
                raw,
                "vwap",
                default=0.0,
            )
        )

        atr = self._float(
            self._first(
                raw,
                "atr",
                "atr14",
                default=0.0,
            )
        )

        supertrend = self._float(
            self._first(
                raw,
                "supertrend",
                default=0.0,
            )
        )

        supertrend_direction = self._int(
            self._first(
                raw,
                "supertrend_direction",
                "supertrendDirection",
                default=0,
            )
        )

        # =================================================
        # CANDLES
        # =================================================

        candles = self._first(
            raw,
            "candles",
            "ohlcv",
            "history",
            default=[],
        )

        if not isinstance(
            candles,
            list,
        ):
            candles = []

        # =================================================
        # NORMALIZED RECORD
        # =================================================

        return {

            "instrument_key":
                instrument_key,

            "symbol":
                symbol,

            "exchange":
                exchange,

            "timeframe":
                str(
                    self._first(
                        raw,
                        "timeframe",
                        "interval",
                        default=self.timeframe,
                    )
                ),

            "last_price":
                last_price,

            "open":
                open_price,

            "high":
                high_price,

            "low":
                low_price,

            "close":
                close_price,

            "previous_close":
                previous_close,

            "volume":
                volume,

            "average_volume":
                average_volume,

            "volume_ratio":
                volume_ratio,

            "gap_percent":
                gap_percent,

            "timestamp":
                timestamp,

            "sector":
                sector,

            "market_cap":
                market_cap,

            "beta":
                beta,

            # Indicators

            "ema9":
                ema9,

            "ema20":
                ema20,

            "ema21":
                ema21,

            "ema50":
                ema50,

            "ema100":
                ema100,

            "ema200":
                ema200,

            "rsi":
                rsi,

            "macd":
                macd,

            "macd_signal":
                macd_signal,

            "macd_histogram":
                macd_histogram,

            "adx":
                adx,

            "plus_di":
                plus_di,

            "minus_di":
                minus_di,

            "vwap":
                vwap,

            "atr":
                atr,

            "supertrend":
                supertrend,

            "supertrend_direction":
                supertrend_direction,

            # Historical candles

            "candles":
                candles,

            # Preserve original data

            "raw":
                dict(raw),

        }

    # =====================================================
    # ADAPT DICTIONARY
    # =====================================================

    def adapt_dict(
        self,
        raw_data: Mapping[
            str,
            Any
        ],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Adapt dictionary-based market data.

        Expected format
        ---------------

        {
            instrument_key: {
                market data
            }
        }
        """

        output: Dict[
            str,
            Dict[str, Any]
        ] = {}

        for key, value in raw_data.items():

            if not isinstance(
                value,
                Mapping,
            ):
                continue

            try:

                record = self.adapt_record(

                    value,

                    fallback_instrument_key=str(
                        key
                    ),

                )

                instrument_key = (
                    record["instrument_key"]
                    or str(key)
                )

                if not record["symbol"]:

                    record["symbol"] = (
                        self.normalize_symbol(
                            value.get(
                                "symbol",
                                "",
                            )
                        )
                    )

                output[
                    instrument_key
                ] = record

            except Exception as exc:

                self.errors.append(

                    f"{key}: "
                    f"{type(exc).__name__}: "
                    f"{exc}"

                )

        return output

    # =====================================================
    # ADAPT LIST
    # =====================================================

    def adapt_list(
        self,
        raw_data: Iterable[
            Mapping[str, Any]
        ],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Adapt list-based market data.
        """

        output: Dict[
            str,
            Dict[str, Any]
        ] = {}

        for index, value in enumerate(
            raw_data
        ):

            if not isinstance(
                value,
                Mapping,
            ):
                continue

            try:

                record = self.adapt_record(
                    value
                )

                instrument_key = (
                    record["instrument_key"]
                )

                if not instrument_key:

                    symbol = (
                        record["symbol"]
                    )

                    if symbol:

                        instrument_key = (
                            f"{record['exchange']}"
                            f"|{symbol}"
                        )

                    else:

                        instrument_key = (
                            f"UNKNOWN|{index}"
                        )

                record[
                    "instrument_key"
                ] = instrument_key

                output[
                    instrument_key
                ] = record

            except Exception as exc:

                self.errors.append(

                    f"Record {index}: "
                    f"{type(exc).__name__}: "
                    f"{exc}"

                )

        return output

    # =====================================================
    # ADAPT
    # =====================================================

    def adapt(
        self,
        raw_data: Any,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Automatically detect input structure.
        """

        self.errors.clear()

        if raw_data is None:

            self.last_count = 0

            self.last_adapted_at = (
                datetime.now()
            )

            return {}

        if isinstance(
            raw_data,
            Mapping,
        ):

            output = self.adapt_dict(
                raw_data
            )

        elif isinstance(
            raw_data,
            (
                list,
                tuple,
            ),
        ):

            output = self.adapt_list(
                raw_data
            )

        else:

            raise TypeError(

                "Unsupported market data "
                f"type: {type(raw_data).__name__}"

            )

        self.last_count = len(
            output
        )

        self.last_adapted_at = (
            datetime.now()
        )

        return output

    # =====================================================
    # VALIDATE RECORD
    # =====================================================

    @staticmethod
    def validate_record(
        record: Mapping[str, Any],
    ) -> bool:

        if not record.get(
            "instrument_key"
        ):
            return False

        if not record.get(
            "symbol"
        ):
            return False

        if float(
            record.get(
                "last_price",
                0.0,
            )
        ) <= 0:

            return False

        return True

    # =====================================================
    # VALID RECORDS ONLY
    # =====================================================

    def valid_only(
        self,
        data: Mapping[
            str,
            Dict[str, Any]
        ],
    ) -> Dict[str, Dict[str, Any]]:

        return {

            key: record

            for key, record in data.items()

            if self.validate_record(
                record
            )

        }

    # =====================================================
    # FILTER MINIMUM PRICE
    # =====================================================

    @staticmethod
    def filter_price(
        data: Mapping[
            str,
            Dict[str, Any]
        ],
        minimum_price: float = 200.0,
    ) -> Dict[str, Dict[str, Any]]:
        """
        StockVersity default:
        price >= ₹200.
        """

        return {

            key: value

            for key, value in data.items()

            if float(
                value.get(
                    "last_price",
                    0.0,
                )
            ) >= minimum_price

        }

    # =====================================================
    # FILTER MARKET CAP
    # =====================================================

    @staticmethod
    def filter_market_cap(
        data: Mapping[
            str,
            Dict[str, Any]
        ],
        minimum_market_cap: float = 1000.0,
    ) -> Dict[str, Dict[str, Any]]:
        """
        StockVersity default:
        market cap >= ₹1000 crore.

        Records without market-cap data are retained because
        live Upstox feeds normally do not provide market cap.
        """

        output: Dict[
            str,
            Dict[str, Any]
        ] = {}

        for key, value in data.items():

            market_cap = float(
                value.get(
                    "market_cap",
                    0.0,
                )
            )

            if market_cap <= 0:

                output[key] = value

                continue

            if (
                market_cap
                >= minimum_market_cap
            ):

                output[key] = value

        return output

    # =====================================================
    # FILTER GAP
    # =====================================================

    @staticmethod
    def filter_gap(
        data: Mapping[
            str,
            Dict[str, Any]
        ],
        maximum_gap: float = 3.0,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Remove stocks with absolute gap > 3%.
        """

        return {

            key: value

            for key, value in data.items()

            if abs(
                float(
                    value.get(
                        "gap_percent",
                        0.0,
                    )
                )
            ) <= maximum_gap

        }

    # =====================================================
    # PREPARE
    # =====================================================

    def prepare(
        self,
        raw_data: Any,
        *,
        minimum_price: float = 200.0,
        minimum_market_cap: float = 1000.0,
        maximum_gap: float = 3.0,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Complete scanner preparation pipeline.

        Steps
        -----
        1. Normalize data
        2. Remove invalid records
        3. Apply minimum price
        4. Apply market-cap filter
        5. Remove >3% gaps
        """

        data = self.adapt(
            raw_data
        )

        data = self.valid_only(
            data
        )

        data = self.filter_price(
            data,
            minimum_price,
        )

        data = self.filter_market_cap(
            data,
            minimum_market_cap,
        )

        data = self.filter_gap(
            data,
            maximum_gap,
        )

        self.last_count = len(
            data
        )

        return data

    # =====================================================
    # STATUS
    # =====================================================

    def status(
        self,
    ) -> Dict[str, Any]:

        return {

            "records":
                self.last_count,

            "errors":
                len(
                    self.errors
                ),

            "last_adapted_at": (
                self.last_adapted_at.isoformat()
                if self.last_adapted_at
                else None
            ),

            "exchange":
                self.exchange,

            "timeframe":
                self.timeframe,

        }


# =========================================================
# SHARED ADAPTER
# =========================================================

_default_adapter: Optional[
    ScannerDataAdapter
] = None


def get_scanner_data_adapter(
) -> ScannerDataAdapter:
    """
    Return shared adapter instance.
    """

    global _default_adapter

    if _default_adapter is None:

        _default_adapter = (
            ScannerDataAdapter()
        )

    return _default_adapter


# =========================================================
# FACTORY
# =========================================================

def create_scanner_data_adapter(
    *,
    exchange: str = DEFAULT_EXCHANGE,
    timeframe: str = DEFAULT_TIMEFRAME,
) -> ScannerDataAdapter:

    return ScannerDataAdapter(

        exchange=exchange,

        timeframe=timeframe,

    )


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "ScannerDataAdapter",

    "create_scanner_data_adapter",

    "get_scanner_data_adapter",

]


# ==========================
# END OF FILE
# ==========================