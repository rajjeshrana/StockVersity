from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional


"""
==========================================================
StockVersity Scanner Pro
Market Provider Interface & Models
Version : 4.0
==========================================================

This module defines the abstract interface that every
market data provider must implement, along with standard
enums, data models, and validation utilities.

Supported Providers

• Upstox
• Shoonya
• NSE
• Future Brokers

The scanner engine NEVER talks directly to a broker.

Instead it communicates only with MarketProvider.

This allows changing broker without changing
scanner logic.
"""


class MarketProvider(ABC):
    """
    Base class for every market provider.

    All providers MUST inherit this class.
    """

    def __init__(self):
        self.provider_name = ""
        self.connected = False
        self.authenticated = False
        self.websocket_connected = False
        self.last_update: Optional[datetime] = None
        self.subscribed_symbols: List[str] = []
        self.market_status_val = "CLOSED"

    # =====================================================
    # Authentication
    # =====================================================

    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with broker.
        """
        raise NotImplementedError

    @abstractmethod
    def logout(self):
        """
        Logout broker session.
        """
        raise NotImplementedError

    # =====================================================
    # Connection
    # =====================================================

    @abstractmethod
    def connect(self):
        """
        Connect websocket.
        """
        raise NotImplementedError

    @abstractmethod
    def disconnect(self):
        """
        Disconnect websocket.
        """
        raise NotImplementedError

    @abstractmethod
    def reconnect(self):
        """
        Reconnect websocket.
        """
        raise NotImplementedError

    # =====================================================
    # Subscription
    # =====================================================

    @abstractmethod
    def subscribe(self, symbols: List[str]):
        """
        Subscribe symbols.
        """
        raise NotImplementedError

    @abstractmethod
    def unsubscribe(self, symbols: List[str]):
        """
        Unsubscribe symbols.
        """
        raise NotImplementedError

    # =====================================================
    # Live Data
    # =====================================================

    @abstractmethod
    def on_tick(self, tick: Dict[str, Any]):
        """
        Tick callback.
        """
        raise NotImplementedError

    @abstractmethod
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Latest quote.
        """
        raise NotImplementedError

    @abstractmethod
    def get_quotes(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Multiple quotes.
        """
        raise NotImplementedError

    @abstractmethod
    def get_ltp(self, symbol: str) -> float:
        """
        Latest traded price.
        """
        raise NotImplementedError

    # =====================================================
    # Historical Data
    # =====================================================

    @abstractmethod
    def historical_data(
        self, symbol: str, interval: str, start_date, end_date
    ):
        """
        Fetch historical candles.
        """
        raise NotImplementedError

    @abstractmethod
    def intraday_data(self, symbol: str, interval: str):
        """
        Fetch today's candles.
        """
        raise NotImplementedError

    # =====================================================
    # Order Book & Positions
    # =====================================================

    @abstractmethod
    def get_market_depth(self, symbol: str) -> Dict[str, Any]:
        """
        Return complete market depth.

        Example
        -------
        {
            "buy": [...],
            "sell": [...],
            "total_buy_qty": 0,
            "total_sell_qty": 0
        }
        """
        raise NotImplementedError

    @abstractmethod
    def get_order_book(self) -> List[Dict[str, Any]]:
        """
        Return broker order book.
        """
        raise NotImplementedError

    @abstractmethod
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Return current positions.
        """
        raise NotImplementedError

    @abstractmethod
    def get_holdings(self) -> List[Dict[str, Any]]:
        """
        Return holdings.
        """
        raise NotImplementedError

    # =====================================================
    # Symbol Management
    # =====================================================

    @abstractmethod
    def search_symbol(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Search instruments.
        """
        raise NotImplementedError

    @abstractmethod
    def instrument_master(self) -> List[Dict[str, Any]]:
        """
        Complete instrument master.
        """
        raise NotImplementedError

    @abstractmethod
    def exchange_list(self) -> List[str]:
        """
        Supported exchanges.

        Example
        -------
        NSE
        BSE
        MCX
        NFO
        CDS
        """
        raise NotImplementedError

    # =====================================================
    # Market Status
    # =====================================================

    @abstractmethod
    def market_status(self) -> Dict[str, Any]:
        """
        Return market status.

        Example
        -------
        {
            "status":"OPEN",
            "exchange":"NSE",
            "time":"09:45:10"
        }
        """
        raise NotImplementedError

    @abstractmethod
    def server_time(self) -> datetime:
        """
        Broker server time.
        """
        raise NotImplementedError

    # =====================================================
    # Heartbeat
    # =====================================================

    @abstractmethod
    def heartbeat(self):
        """
        Keep websocket alive.
        """
        raise NotImplementedError

    @abstractmethod
    def ping(self) -> bool:
        """
        Check broker connectivity.
        """
        raise NotImplementedError

    # =====================================================
    # Provider Information
    # =====================================================

    @abstractmethod
    def provider_info(self) -> Dict[str, Any]:
        """
        Provider information.

        Example
        -------
        {
            "name":"Upstox",
            "version":"2.0",
            "connected":True
        }
        """
        raise NotImplementedError

    @abstractmethod
    def capabilities(self) -> Dict[str, bool]:
        """
        Provider capabilities.

        Example
        -------
        {
            "websocket":True,
            "historical":True,
            "market_depth":True,
            "positions":True,
            "holdings":True
        }
        """
        raise NotImplementedError

    # =====================================================
    # Health Monitoring
    # =====================================================

    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """
        Return provider health.

        Example
        -------
        {
            "healthy":True,
            "latency":18,
            "last_tick":datetime,
            "subscribed":150
        }
        """
        raise NotImplementedError

    @abstractmethod
    def statistics(self) -> Dict[str, Any]:
        """
        Runtime statistics.

        Example
        -------
        {
            "ticks":120432,
            "messages":56340,
            "reconnects":0,
            "uptime":3600
        }
        """
        raise NotImplementedError

    # =====================================================
    # Lifecycle
    # =====================================================

    @abstractmethod
    def initialize(self):
        """
        Initialize provider resources.
        """
        raise NotImplementedError

    @abstractmethod
    def shutdown(self):
        """
        Shutdown provider cleanly.
        """
        raise NotImplementedError


# =====================================================
# Enumerations
# =====================================================

class Exchange(str, Enum):
    NSE = "NSE"
    BSE = "BSE"
    NFO = "NFO"
    CDS = "CDS"
    MCX = "MCX"


class Segment(str, Enum):
    EQUITY = "EQUITY"
    FUTURES = "FUTURES"
    OPTIONS = "OPTIONS"
    CURRENCY = "CURRENCY"
    COMMODITY = "COMMODITY"


class Interval(str, Enum):
    TICK = "tick"
    ONE_MIN = "1m"
    THREE_MIN = "3m"
    FIVE_MIN = "5m"
    TEN_MIN = "10m"
    FIFTEEN_MIN = "15m"
    THIRTY_MIN = "30m"
    ONE_HOUR = "60m"
    TWO_HOUR = "120m"
    FOUR_HOUR = "240m"
    DAILY = "1D"
    WEEKLY = "1W"
    MONTHLY = "1M"


class MarketState(str, Enum):
    CLOSED = "CLOSED"
    PRE_OPEN = "PRE_OPEN"
    OPEN = "OPEN"
    POST_CLOSE = "POST_CLOSE"
    HOLIDAY = "HOLIDAY"


# =====================================================
# Data Models
# =====================================================

@dataclass(slots=True)
class Tick:
    symbol: str
    exchange: str
    timestamp: datetime
    ltp: float
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0
    volume: int = 0
    bid: float = 0.0
    ask: float = 0.0
    bid_qty: int = 0
    ask_qty: int = 0
    oi: int = 0
    change: float = 0.0
    change_percent: float = 0.0


@dataclass(slots=True)
class Candle:
    symbol: str
    timeframe: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    oi: int = 0
    vwap: float = 0.0


@dataclass(slots=True)
class Quote:
    symbol: str
    ltp: float
    open: float
    high: float
    low: float
    close: float
    volume: int
    timestamp: datetime
    bid: float = 0.0
    ask: float = 0.0


@dataclass(slots=True)
class MarketDepth:
    symbol: str
    bids: list = field(default_factory=list)
    asks: list = field(default_factory=list)
    total_buy_qty: int = 0
    total_sell_qty: int = 0


# =====================================================
# Validation Helpers
# =====================================================

def validate_symbol(symbol: str) -> bool:
    return isinstance(symbol, str) and len(symbol.strip()) > 0


def validate_price(price: float) -> bool:
    return price >= 0


def validate_volume(volume: int) -> bool:
    return volume >= 0


# =====================================================
# Utilities
# =====================================================

def provider_connected(provider: MarketProvider) -> bool:
    return (
        provider.connected
        and provider.authenticated
        and provider.websocket_connected
    )


def provider_ready(provider: MarketProvider) -> bool:
    return provider_connected(provider)


# =====================================================
# Module Metadata
# =====================================================

__version__ = "4.0"

__author__ = "StockVersity Scanner Pro"

__all__ = [
    "MarketProvider",
    "Exchange",
    "Segment",
    "Interval",
    "MarketState",
    "Tick",
    "Quote",
    "Candle",
    "MarketDepth",
    "validate_symbol",
    "validate_price",
    "validate_volume",
    "provider_connected",
    "provider_ready",
]