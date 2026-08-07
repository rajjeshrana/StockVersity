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
    """
==========================================================
StockVersity Scanner Pro
Abstract Market Provider
==========================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from typing import Callable
from typing import Dict
from typing import List

from core.market_data.models import ProviderState
from core.market_data.models import Tick


class MarketProvider(ABC):
    """
    Base interface for every broker provider.

    Examples
    --------
    UpstoxProvider
    ZerodhaProvider
    AngelProvider
    DhanProvider
    """

    def __init__(self):

        self.state = ProviderState.DISCONNECTED

    ####################################################################
    # Connection
    ####################################################################

    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to broker.
        """
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        """
        Disconnect broker.
        """
        raise NotImplementedError

    ####################################################################
    # Subscription
    ####################################################################

    @abstractmethod
    def subscribe(
        self,
        instrument_keys: List[str]
    ) -> None:
        """
        Subscribe instruments.
        """
        raise NotImplementedError

    @abstractmethod
    def unsubscribe(
        self,
        instrument_keys: List[str]
    ) -> None:
        """
        Unsubscribe instruments.
        """
        raise NotImplementedError

    ####################################################################
    # Status
    ####################################################################

    @abstractmethod
    def is_connected(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def connection_state(self) -> ProviderState:
        raise NotImplementedError

    ####################################################################
    # Tick Events
    ####################################################################

    @abstractmethod
    def register_tick_callback(
        self,
        callback: Callable[[Tick], None]
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def unregister_tick_callback(
        self,
        callback: Callable[[Tick], None]
    ) -> None:
        raise NotImplementedError

    ####################################################################
    # Status Events
    ####################################################################

    @abstractmethod
    def register_status_callback(
        self,
        callback: Callable[[ProviderState], None]
    ) -> None:
        raise NotImplementedError

    ####################################################################
    # Error Events
    ####################################################################

    @abstractmethod
    def register_error_callback(
        self,
        callback: Callable[[Exception], None]
    ) -> None:
        raise NotImplementedError

    ####################################################################
    # Diagnostics
    ####################################################################

    @abstractmethod
    def statistics(self) -> Dict:
        """
        Provider statistics.
        """
        raise NotImplementedError

    @abstractmethod
    def diagnostics(self) -> Dict:
        """
        Runtime diagnostics.
        """
        raise NotImplementedError