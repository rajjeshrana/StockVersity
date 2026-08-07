"""
=========================================================
StockVersity Scanner Pro
Market Data Scanner Bridge
Version : 2.0
=========================================================

Connects live/historical market data with the scanner system.

Flow
----

Upstox WebSocket
        ↓
Market Data Parser
        ↓
MarketDataBridge
        ↓
ScannerManager
        ↓
ScannerEngine
        ↓
Individual Scanners

=========================================================
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from threading import RLock

from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Mapping
from typing import Optional

from core.scanner.signal import Signal
from core.scanner.scanner_manager import ScannerManager


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    Convert a value safely to float.
    """

    try:

        if value is None:
            return default

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return default


def _safe_int(
    value: Any,
    default: int = 0,
) -> int:
    """
    Convert a value safely to int.
    """

    try:

        if value is None:
            return default

        return int(float(value))

    except (
        TypeError,
        ValueError,
    ):

        return default


def _first_value(
    data: Mapping[str, Any],
    *keys: str,
    default: Any = None,
) -> Any:
    """
    Return first available non-None value.
    """

    for key in keys:

        if key in data:

            value = data[key]

            if value is not None:
                return value

    return default


def _normalize_symbol(
    symbol: Any,
) -> str:
    """
    Normalize trading symbol.
    """

    if symbol is None:
        return ""

    return str(
        symbol
    ).strip().upper()


def _normalize_instrument_key(
    instrument_key: Any,
) -> str:
    """
    Normalize Upstox instrument key.
    """

    if instrument_key is None:
        return ""

    return str(
        instrument_key
    ).strip()


# =========================================================
# MARKET DATA BRIDGE
# =========================================================

class MarketDataBridge:
    """
    Bridge between market-data providers and ScannerManager.

    The bridge keeps one normalized snapshot for each
    instrument.

    Example snapshot
    ----------------

    {
        "NSE_EQ|INE002A01018": {

            "instrument_key": "NSE_EQ|INE002A01018",

            "symbol": "RELIANCE",

            "last_price": 1450.00,

            "open": 1435.00,

            "high": 1455.00,

            "low": 1430.00,

            "close": 1450.00,

            "previous_close": 1438.00,

            "volume": 5000000,

            "average_volume": 2500000,

            "volume_ratio": 2.0,

            "timestamp": "...",

            "candles": {
                "1m": [],
                "5m": [],
                "15m": [],
                "1h": [],
                "1d": [],
            }
        }
    }
    """

    def __init__(
        self,
        manager: Optional[ScannerManager] = None,
        *,
        debug: bool = False,
        auto_scan: bool = False,
    ) -> None:

        self.manager = manager

        self.debug = debug

        self.auto_scan = auto_scan

        self._lock = RLock()

        self._market_data: Dict[
            str,
            Dict[str, Any]
        ] = {}

        self._symbol_index: Dict[
            str,
            str
        ] = {}

        self.total_updates: int = 0

        self.last_update: Optional[
            datetime
        ] = None

        self.last_scan: Optional[
            datetime
        ] = None

        self.last_error: Optional[
            str
        ] = None

    # =====================================================
    # MANAGER
    # =====================================================

    def set_manager(
        self,
        manager: ScannerManager,
    ) -> None:
        """
        Attach ScannerManager.
        """

        self.manager = manager

    # =====================================================
    # NORMALIZE QUOTE
    # =====================================================

    def normalize_quote(
        self,
        data: Mapping[str, Any],
    ) -> Dict[str, Any]:
        """
        Normalize market quote from different providers.

        Supports common aliases such as:

        ltp
        last_price
        last_traded_price

        open / open_price
        high / high_price
        low / low_price
        close / close_price
        """

        instrument_key = (
            _normalize_instrument_key(
                _first_value(
                    data,
                    "instrument_key",
                    "instrumentKey",
                    "instrument",
                    "key",
                    default="",
                )
            )
        )

        symbol = (
            _normalize_symbol(
                _first_value(
                    data,
                    "symbol",
                    "trading_symbol",
                    "tradingSymbol",
                    "tradingsymbol",
                    default="",
                )
            )
        )

        last_price = _safe_float(
            _first_value(
                data,
                "last_price",
                "ltp",
                "last_traded_price",
                "lastTradedPrice",
                "price",
                default=0.0,
            )
        )

        open_price = _safe_float(
            _first_value(
                data,
                "open",
                "open_price",
                "openPrice",
                default=0.0,
            )
        )

        high_price = _safe_float(
            _first_value(
                data,
                "high",
                "high_price",
                "highPrice",
                default=0.0,
            )
        )

        low_price = _safe_float(
            _first_value(
                data,
                "low",
                "low_price",
                "lowPrice",
                default=0.0,
            )
        )

        close_price = _safe_float(
            _first_value(
                data,
                "close",
                "close_price",
                "closePrice",
                default=last_price,
            )
        )

        previous_close = _safe_float(
            _first_value(
                data,
                "previous_close",
                "prev_close",
                "previousClose",
                "prevClose",
                default=0.0,
            )
        )

        volume = _safe_int(
            _first_value(
                data,
                "volume",
                "total_volume",
                "totalTradedVolume",
                "ttv",
                default=0,
            )
        )

        average_volume = _safe_int(
            _first_value(
                data,
                "average_volume",
                "avg_volume",
                "averageVolume",
                default=0,
            )
        )

        volume_ratio = _safe_float(
            _first_value(
                data,
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
                volume
                / average_volume
            )

        change = 0.0

        change_percent = 0.0

        if (
            last_price > 0
            and previous_close > 0
        ):

            change = (
                last_price
                - previous_close
            )

            change_percent = (
                change
                / previous_close
            ) * 100

        timestamp = _first_value(
            data,
            "timestamp",
            "time",
            "feed_time",
            "feedTime",
            default=datetime.now().isoformat(),
        )

        normalized = {

            "instrument_key":
                instrument_key,

            "symbol":
                symbol,

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

            "change":
                round(
                    change,
                    4,
                ),

            "change_percent":
                round(
                    change_percent,
                    4,
                ),

            "volume":
                volume,

            "average_volume":
                average_volume,

            "volume_ratio":
                round(
                    volume_ratio,
                    4,
                ),

            "timestamp":
                timestamp,
        }

        # Preserve useful extra fields.

        passthrough_fields = (

            "sector",

            "market_cap",

            "beta",

            "bid_price",

            "ask_price",

            "bid_quantity",

            "ask_quantity",

            "oi",

            "open_interest",

            "upper_circuit",

            "lower_circuit",

            "exchange",

            # ---------------------------------------------
            # Scanner indicator enrichment
            # ---------------------------------------------

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

            "atr",

            "vwap",

            "volume_sma20",

            "rvol",
            "relative_volume",

        )

        for field in passthrough_fields:

            if field in data:

                normalized[field] = (
                    data[field]
                )

        return normalized

    # =====================================================
    # RESOLVE KEY
    # =====================================================

    def _resolve_key(
        self,
        data: Mapping[str, Any],
    ) -> str:
        """
        Determine unique storage key.

        Upstox instrument_key is preferred.
        Symbol is fallback.
        """

        instrument_key = (
            _normalize_instrument_key(
                data.get(
                    "instrument_key",
                    ""
                )
            )
        )

        if instrument_key:
            return instrument_key

        symbol = _normalize_symbol(
            data.get(
                "symbol",
                ""
            )
        )

        return symbol

    # =====================================================
    # UPDATE QUOTE
    # =====================================================

    def update_quote(
        self,
        data: Mapping[str, Any],
        *,
        trigger_scan: Optional[
            bool
        ] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Add/update one live market quote.
        """

        try:

            normalized = (
                self.normalize_quote(
                    data
                )
            )

            key = self._resolve_key(
                normalized
            )

            if not key:

                self.log(
                    "Ignored quote without "
                    "instrument key or symbol."
                )

                return None

            with self._lock:

                existing = (
                    self._market_data.get(
                        key,
                        {}
                    )
                )

                candles = existing.get(
                    "candles",
                    {}
                )

                existing.update(
                    normalized
                )

                existing["candles"] = (
                    candles
                )

                self._market_data[key] = (
                    existing
                )

                symbol = existing.get(
                    "symbol",
                    ""
                )

                if symbol:

                    self._symbol_index[
                        symbol.upper()
                    ] = key

                self.total_updates += 1

                self.last_update = (
                    datetime.now()
                )

            should_scan = (
                self.auto_scan
                if trigger_scan is None
                else trigger_scan
            )

            if should_scan:

                self.run_scan()

            return dict(existing)

        except Exception as exc:

            self.last_error = str(exc)

            self.log(
                "Quote update error:",
                exc,
            )

            raise

    # =====================================================
    # UPDATE MANY QUOTES
    # =====================================================

    def update_quotes(
        self,
        quotes: Iterable[
            Mapping[str, Any]
        ],
        *,
        trigger_scan: bool = False,
    ) -> int:
        """
        Update multiple quotes.
        """

        count = 0

        for quote in quotes:

            result = self.update_quote(
                quote,
                trigger_scan=False,
            )

            if result is not None:

                count += 1

        if (
            trigger_scan
            or self.auto_scan
        ):

            self.run_scan()

        return count

    # =====================================================
    # ADD CANDLE
    # =====================================================

    def add_candle(
        self,
        instrument_key: str,
        timeframe: str,
        candle: Mapping[str, Any],
        *,
        symbol: str = "",
        max_candles: int = 500,
    ) -> None:
        """
        Add one OHLCV candle.

        Candle format:

        {
            "timestamp": ...,
            "open": ...,
            "high": ...,
            "low": ...,
            "close": ...,
            "volume": ...
        }
        """

        instrument_key = (
            _normalize_instrument_key(
                instrument_key
            )
        )

        symbol = _normalize_symbol(
            symbol
        )

        timeframe = str(
            timeframe
        ).strip()

        if not instrument_key:

            instrument_key = symbol

        if not instrument_key:
            return

        normalized_candle = {

            "timestamp":
                _first_value(
                    candle,
                    "timestamp",
                    "time",
                    "candle_time",
                    default=datetime.now().isoformat(),
                ),

            "open":
                _safe_float(
                    _first_value(
                        candle,
                        "open",
                        "open_price",
                        default=0.0,
                    )
                ),

            "high":
                _safe_float(
                    _first_value(
                        candle,
                        "high",
                        "high_price",
                        default=0.0,
                    )
                ),

            "low":
                _safe_float(
                    _first_value(
                        candle,
                        "low",
                        "low_price",
                        default=0.0,
                    )
                ),

            "close":
                _safe_float(
                    _first_value(
                        candle,
                        "close",
                        "close_price",
                        default=0.0,
                    )
                ),

            "volume":
                _safe_int(
                    _first_value(
                        candle,
                        "volume",
                        default=0,
                    )
                ),
        }

        with self._lock:

            snapshot = (
                self._market_data.setdefault(
                    instrument_key,
                    {
                        "instrument_key":
                            instrument_key,

                        "symbol":
                            symbol,

                        "candles":
                            {},
                    }
                )
            )

            if symbol:

                snapshot["symbol"] = symbol

                self._symbol_index[
                    symbol
                ] = instrument_key

            candles = snapshot.setdefault(
                "candles",
                {}
            )

            timeframe_candles = (
                candles.setdefault(
                    timeframe,
                    []
                )
            )

            timeframe_candles.append(
                normalized_candle
            )

            if (
                max_candles > 0
                and len(
                    timeframe_candles
                ) > max_candles
            ):

                del timeframe_candles[
                    :-max_candles
                ]

            # Update current OHLC from candle.

            snapshot["open"] = (
                normalized_candle["open"]
            )

            snapshot["high"] = (
                normalized_candle["high"]
            )

            snapshot["low"] = (
                normalized_candle["low"]
            )

            snapshot["close"] = (
                normalized_candle["close"]
            )

            snapshot["last_price"] = (
                normalized_candle["close"]
            )

            snapshot["volume"] = (
                normalized_candle["volume"]
            )

            snapshot["timestamp"] = (
                normalized_candle[
                    "timestamp"
                ]
            )

            self.total_updates += 1

            self.last_update = (
                datetime.now()
            )

    # =====================================================
    # ADD MANY CANDLES
    # =====================================================

    def add_candles(
        self,
        instrument_key: str,
        timeframe: str,
        candles: Iterable[
            Mapping[str, Any]
        ],
        *,
        symbol: str = "",
        max_candles: int = 500,
    ) -> int:
        """
        Add historical candles.
        """

        count = 0

        for candle in candles:

            self.add_candle(
                instrument_key,
                timeframe,
                candle,
                symbol=symbol,
                max_candles=max_candles,
            )

            count += 1

        return count

    # =====================================================
    # GET SNAPSHOT
    # =====================================================

    def get(
        self,
        instrument_key: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get one instrument snapshot.
        """

        key = (
            _normalize_instrument_key(
                instrument_key
            )
        )

        with self._lock:

            data = self._market_data.get(
                key
            )

            if data is None:
                return None

            return deepcopy(data)

    # =====================================================
    # GET BY SYMBOL
    # =====================================================

    def get_by_symbol(
        self,
        symbol: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Find market data using trading symbol.
        """

        symbol = _normalize_symbol(
            symbol
        )

        with self._lock:

            key = self._symbol_index.get(
                symbol
            )

            if key is None:
                return None

            data = self._market_data.get(
                key
            )

            if data is None:
                return None

            return deepcopy(data)

    # =====================================================
    # GET CANDLES
    # =====================================================

    def get_candles(
        self,
        instrument_key: str,
        timeframe: str,
    ) -> List[Dict[str, Any]]:
        """
        Return candles for one timeframe.
        """

        snapshot = self.get(
            instrument_key
        )

        if not snapshot:
            return []

        candles = snapshot.get(
            "candles",
            {}
        )

        return list(
            candles.get(
                timeframe,
                []
            )
        )

    # =====================================================
    # REMOVE SYMBOL
    # =====================================================

    def remove(
        self,
        instrument_key: str,
    ) -> None:
        """
        Remove instrument from bridge.
        """

        instrument_key = (
            _normalize_instrument_key(
                instrument_key
            )
        )

        with self._lock:

            data = self._market_data.pop(
                instrument_key,
                None,
            )

            if data:

                symbol = data.get(
                    "symbol",
                    ""
                )

                if symbol:

                    self._symbol_index.pop(
                        symbol.upper(),
                        None,
                    )

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(self) -> None:
        """
        Clear all market data.
        """

        with self._lock:

            self._market_data.clear()

            self._symbol_index.clear()

    # =====================================================
    # MARKET DATA
    # =====================================================

    def market_data(
        self,
    ) -> Dict[str, Any]:
        """
        Return scanner-ready market snapshot.
        """

        with self._lock:

            return deepcopy(
                self._market_data
            )

    # =====================================================
    # RUN SCAN
    # =====================================================

    def run_scan(
        self,
    ) -> List[Signal]:
        """
        Send current market snapshot to ScannerManager.
        """

        if self.manager is None:

            self.log(
                "No ScannerManager attached."
            )

            return []

        try:

            snapshot = (
                self.market_data()
            )

            results = self.manager.run(
                snapshot
            )

            self.last_scan = (
                datetime.now()
            )

            self.last_error = None

            return results

        except Exception as exc:

            self.last_error = str(exc)

            self.log(
                "Scan error:",
                exc,
            )

            raise

    # =====================================================
    # REFRESH SCAN
    # =====================================================

    def refresh(
        self,
    ) -> List[Signal]:

        return self.run_scan()

    # =====================================================
    # SYMBOL COUNT
    # =====================================================

    @property
    def symbol_count(
        self,
    ) -> int:

        with self._lock:

            return len(
                self._market_data
            )

    # =====================================================
    # SYMBOLS
    # =====================================================

    @property
    def symbols(
        self,
    ) -> List[str]:

        with self._lock:

            symbols = [

                data.get(
                    "symbol",
                    ""
                )

                for data
                in self._market_data.values()

                if data.get(
                    "symbol"
                )
            ]

        return sorted(
            set(symbols)
        )

    # =====================================================
    # INSTRUMENT KEYS
    # =====================================================

    @property
    def instrument_keys(
        self,
    ) -> List[str]:

        with self._lock:

            return list(
                self._market_data.keys()
            )

    # =====================================================
    # STATUS
    # =====================================================

    def status(
        self,
    ) -> Dict[str, Any]:

        return {

            "symbols":
                self.symbol_count,

            "total_updates":
                self.total_updates,

            "auto_scan":
                self.auto_scan,

            "manager_attached":
                self.manager is not None,

            "last_update":
                (
                    self.last_update.isoformat()
                    if self.last_update
                    else None
                ),

            "last_scan":
                (
                    self.last_scan.isoformat()
                    if self.last_scan
                    else None
                ),

            "last_error":
                self.last_error,
        }

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(
        self,
    ) -> Dict[str, Any]:

        issues: List[str] = []

        if self.manager is None:

            issues.append(
                "ScannerManager not attached."
            )

        if self.last_error:

            issues.append(
                self.last_error
            )

        return {

            "healthy":
                len(issues) == 0,

            "issues":
                issues,

            "symbols":
                self.symbol_count,

            "updates":
                self.total_updates,
        }

    # =====================================================
    # AUTO SCAN
    # =====================================================

    def enable_auto_scan(
        self,
    ) -> None:

        self.auto_scan = True

    def disable_auto_scan(
        self,
    ) -> None:

        self.auto_scan = False

    # =====================================================
    # LOGGING
    # =====================================================

    def log(
        self,
        *message: Any,
    ) -> None:

        if not self.debug:
            return

        print(
            "[MarketDataBridge]",
            *message,
        )

    # =====================================================
    # MAGIC METHODS
    # =====================================================

    def __len__(
        self,
    ) -> int:

        return self.symbol_count

    def __contains__(
        self,
        item: object,
    ) -> bool:

        if not isinstance(
            item,
            str,
        ):

            return False

        item = item.strip()

        with self._lock:

            if item in self._market_data:
                return True

            return (
                item.upper()
                in self._symbol_index
            )

    def __bool__(
        self,
    ) -> bool:

        return self.symbol_count > 0

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (
            "MarketDataBridge("
            f"symbols={self.symbol_count}, "
            f"updates={self.total_updates}, "
            f"auto_scan={self.auto_scan}"
            ")"
        )

    def __str__(
        self,
    ) -> str:

        return (
            f"MarketDataBridge | "
            f"{self.symbol_count} symbols | "
            f"{self.total_updates} updates"
        )


# =========================================================
# FACTORY
# =========================================================

def create_market_data_bridge(
    manager: Optional[
        ScannerManager
    ] = None,
    *,
    debug: bool = False,
    auto_scan: bool = False,
) -> MarketDataBridge:
    """
    Create MarketDataBridge.
    """

    return MarketDataBridge(
        manager=manager,
        debug=debug,
        auto_scan=auto_scan,
    )


# =========================================================
# EXPORTS
# =========================================================

__all__ = [

    "MarketDataBridge",

    "create_market_data_bridge",

]


# ==========================
# END OF FILE
# ==========================