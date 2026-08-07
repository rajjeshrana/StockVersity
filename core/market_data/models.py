"""
==========================================================
StockVersity Scanner Pro
Shared Market Data Models
==========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict
from typing import List
from typing import Optional


class ProviderState(Enum):
    """
    Connection state.
    """

    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    RECONNECTING = "RECONNECTING"
    ERROR = "ERROR"


class MarketStatus(Enum):
    """
    Exchange status.
    """

    PRE_OPEN = "PRE_OPEN"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    UNKNOWN = "UNKNOWN"


@dataclass(slots=True)
class QuoteLevel:
    """
    One bid/ask level.
    """

    bid_price: float = 0.0
    bid_quantity: int = 0

    ask_price: float = 0.0
    ask_quantity: int = 0


@dataclass(slots=True)
class Greeks:

    delta: float = 0.0
    gamma: float = 0.0
    theta: float = 0.0
    vega: float = 0.0
    rho: float = 0.0


@dataclass(slots=True)
class OHLC:

    interval: str = ""

    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0

    volume: int = 0

    timestamp: int = 0


@dataclass(slots=True)
class Tick:
    """
    Universal Tick Model
    Used by the entire scanner.
    """

    instrument_key: str

    exchange: str = ""

    symbol: str = ""

    ltp: float = 0.0

    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0

    previous_close: float = 0.0

    volume: int = 0

    last_quantity: int = 0

    average_price: float = 0.0

    timestamp: int = 0

    bid_price: float = 0.0
    bid_quantity: int = 0

    ask_price: float = 0.0
    ask_quantity: int = 0

    open_interest: float = 0.0

    implied_volatility: float = 0.0

    total_buy_quantity: float = 0.0

    total_sell_quantity: float = 0.0

    greeks: Greeks = field(
        default_factory=Greeks
    )

    depth: List[QuoteLevel] = field(
        default_factory=list
    )

    ohlc: Dict[str, OHLC] = field(
        default_factory=dict
    )

    metadata: Dict = field(
        default_factory=dict
    )
