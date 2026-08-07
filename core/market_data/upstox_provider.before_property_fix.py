"""
StockVersity Scanner Pro

Upstox Provider

Concrete implementation of the
MarketProvider interface.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

import upstox_client

from core.market_provider import MarketProvider
from .market_data_parser import MarketDataParser
from .websocket_manager import WebSocketManager
from .models import Tick

logger = logging.getLogger(__name__)


class UpstoxProvider(MarketProvider):

    def __init__(

        self,

        api_client,

    ):

        super().__init__()

        self.api_client = api_client

        #
        # Parser
        #

        self.parser = MarketDataParser()

        #
        # WebSocket
        #

        self.websocket = WebSocketManager(
            api_client
        )

        self.websocket.set_message_parser(
            self.parser.parse
        )

        self.websocket.add_tick_callback(
            self._on_tick
        )

        #
        # Latest ticks cache
        #

        self.latest_ticks: Dict[
            str,
            Tick,
        ] = {}

        #
        # User callbacks
        #

        self.tick_callbacks = []

        self.connected = False

    # =====================================================
    # INTERNAL TICK CALLBACK
    # =====================================================

    def _on_tick(

        self,

        tick: Tick,

    ):

        self.latest_ticks[
            tick.instrument_key
        ] = tick

        for callback in list(
            self.tick_callbacks
        ):

            try:

                callback(
                    tick
                )

            except Exception:

                logger.exception(
                    "Tick callback failed."
                )

    # =====================================================
    # REGISTER CALLBACK
    # =====================================================

    def add_tick_callback(

        self,

        callback,

    ):

        if callback not in self.tick_callbacks:

            self.tick_callbacks.append(
                callback
            )

    def remove_tick_callback(

        self,

        callback,

    ):

        if callback in self.tick_callbacks:

            self.tick_callbacks.remove(
                callback
            )

    # =====================================================
    # CONNECTION
    # =====================================================

    def connect(self):

        logger.info(
            "Connecting Upstox Provider..."
        )

        self.websocket.connect()

        self.connected = self.websocket.wait_until_connected()

        return self.connected

    def disconnect(self):

        self.websocket.disconnect()

        self.connected = False
            # =====================================================
    # SUBSCRIBE
    # =====================================================

    def subscribe(

        self,

        instrument_key: str,

        mode: str = "full",

    ) -> bool:

        return self.websocket.subscribe(

            instrument_key,

            mode,

        )

    # =====================================================
    # SUBSCRIBE MANY
    # =====================================================

    def subscribe_many(

        self,

        instrument_keys: List[str],

        mode: str = "full",

    ) -> bool:

        if not instrument_keys:

            return False

        return self.websocket.subscribe_many(

            instrument_keys,

            mode,

        )

    # =====================================================
    # UNSUBSCRIBE
    # =====================================================

    def unsubscribe(

        self,

        instrument_key: str,

    ) -> bool:

        self.latest_ticks.pop(

            instrument_key,

            None,

        )

        return self.websocket.unsubscribe(

            instrument_key

        )

    # =====================================================
    # UNSUBSCRIBE MANY
    # =====================================================

    def unsubscribe_many(

        self,

        instrument_keys: List[str],

    ) -> bool:

        for key in instrument_keys:

            self.latest_ticks.pop(

                key,

                None,

            )

        return self.websocket.unsubscribe_many(

            instrument_keys

        )

    # =====================================================
    # CHANGE STREAM MODE
    # =====================================================

    def change_mode(

        self,

        instrument_keys: List[str],

        mode: str,

    ) -> bool:

        return self.websocket.change_mode(

            instrument_keys,

            mode,

        )

    # =====================================================
    # CLEAR SUBSCRIPTIONS
    # =====================================================

    def clear_subscriptions(self):

        self.websocket.clear_subscriptions()

        self.latest_ticks.clear()

    # =====================================================
    # GET LATEST TICK
    # =====================================================

    def get_latest_tick(

        self,

        instrument_key: str,

    ) -> Optional[Tick]:

        return self.latest_ticks.get(

            instrument_key

        )

    # =====================================================
    # GET MULTIPLE TICKS
    # =====================================================

    def get_latest_ticks(

        self,

    ) -> Dict[str, Tick]:

        return dict(

            self.latest_ticks

        )

    # =====================================================
    # HAS TICK
    # =====================================================

    def has_tick(

        self,

        instrument_key: str,

    ) -> bool:

        return (

            instrument_key

            in self.latest_ticks

        )

    # =====================================================
    # WAIT FOR NEXT TICK
    # =====================================================

    def next_tick(

        self,

        timeout: float = 0.20,

    ) -> Optional[Tick]:

        return self.websocket.next_tick(

            timeout

        )

    # =====================================================
    # CACHE SIZE
    # =====================================================

    @property

    def cache_size(self) -> int:

        return len(

            self.latest_ticks

        )
        # =====================================================
    # CONNECTION STATUS
    # =====================================================

    def is_connected(self) -> bool:

        return self.websocket.connected

    @property
    def connection_state(self) -> str:

        return self.websocket.state

    @property
    def uptime(self) -> int:

        return self.websocket.uptime

    # =====================================================
    # PROVIDER HEALTH
    # =====================================================

    @property
    def healthy(self) -> bool:

        return (

            self.websocket.connected

            and

            self.parser.healthy

        )

    # =====================================================
    # PROVIDER STATISTICS
    # =====================================================

    def statistics(self) -> Dict:

        websocket_stats = self.websocket.statistics()

        parser_stats = self.parser.statistics()

        return {

            "provider": "Upstox",

            "connected": self.connected,

            "healthy": self.healthy,

            "cached_ticks": len(

                self.latest_ticks

            ),

            "subscriptions": websocket_stats.get(

                "subscriptions",

                0,

            ),

            "messages": parser_stats.get(

                "messages",

                0,

            ),

            "ticks": parser_stats.get(

                "ticks",

                0,

            ),

            "failed": parser_stats.get(

                "failed",

                0,

            ),

            "uptime": self.uptime,

        }

    # =====================================================
    # DIAGNOSTICS
    # =====================================================

    def diagnostics(self) -> Dict:

        return {

            "provider": "Upstox",

            "healthy": self.healthy,

            "connected": self.connected,

            "connection_state": self.connection_state,

            "uptime": self.uptime,

            "cache_size": len(

                self.latest_ticks

            ),

            "parser": self.parser.diagnostics(),

            "websocket": self.websocket.diagnostics(),

        }

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        self.latest_ticks.clear()

        self.parser.reset()

        self.websocket.reset()

    # =====================================================
    # WAIT FOR CONNECTION
    # =====================================================

    def wait_until_connected(

        self,

        timeout: float = 20.0,

    ) -> bool:

        return self.websocket.wait_until_connected(

            timeout

        )

    # =====================================================
    # WAIT FOR DISCONNECT
    # =====================================================

    def wait_until_disconnected(

        self,

        timeout: float = 10.0,

    ) -> bool:

        return self.websocket.wait_until_disconnected(

            timeout

        )

    # =====================================================
    # INSTRUMENTS
    # =====================================================

    @property
    def subscribed_instruments(

        self,

    ) -> List[str]:

        return sorted(

            self.websocket.subscribed

        )

    # =====================================================
    # CACHE OPERATIONS
    # =====================================================

    def clear_cache(self):

        self.latest_ticks.clear()

    def remove_tick(

        self,

        instrument_key: str,

    ):

        self.latest_ticks.pop(

            instrument_key,

            None,

        )

    # =====================================================
    # PROVIDER INFO
    # =====================================================

    @property
    def provider_name(self) -> str:

        return "Upstox"

    @property
    def websocket_manager(self):

        return self.websocket
        # =====================================================
    # START
    # =====================================================

    def start(self) -> bool:

        return self.connect()

    # =====================================================
    # STOP
    # =====================================================

    def stop(self):

        logger.info(
            "Stopping Upstox Provider..."
        )

        try:

            self.websocket.disconnect()

        except Exception:

            logger.exception(
                "Failed to disconnect websocket."
            )

        self.connected = False

    # =====================================================
    # CLOSE
    # =====================================================

    def close(self):

        self.stop()

    # =====================================================
    # RECONNECT
    # =====================================================

    def reconnect(self) -> bool:

        logger.info(
            "Reconnecting Upstox Provider..."
        )

        self.stop()

        return self.connect()

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh(self):

        """
        Placeholder for future refresh logic.
        """

        if not self.connected:

            self.connect()

    # =====================================================
    # CONTEXT MANAGER
    # =====================================================

    def __enter__(self):

        self.connect()

        return self

    def __exit__(

        self,

        exc_type,

        exc_value,

        traceback,

    ):

        self.stop()

        return False

    # =====================================================
    # LENGTH
    # =====================================================

    def __len__(self):

        return len(

            self.latest_ticks

        )

    # =====================================================
    # ITERATOR
    # =====================================================

    def __iter__(self):

        return iter(

            self.latest_ticks.values()

        )

    # =====================================================
    # CONTAINS
    # =====================================================

    def __contains__(

        self,

        instrument_key: str,

    ):

        return (

            instrument_key

            in self.latest_ticks

        )

    # =====================================================
    # STRING
    # =====================================================

    def __str__(self):

        return (

            f"UpstoxProvider("

            f"connected={self.connected}, "

            f"subscriptions={len(self.subscribed_instruments)}, "

            f"cached_ticks={len(self.latest_ticks)}"

            f")"

        )

    # =====================================================
    # REPR
    # =====================================================

    def __repr__(self):

        return (

            "<UpstoxProvider "

            f"connected={self.connected} "

            f"subscriptions={len(self.subscribed_instruments)} "

            f"ticks={len(self.latest_ticks)}>"

        )

    # =====================================================
    # DESTRUCTOR
    # =====================================================

    def __del__(self):

        try:

            self.stop()

        except Exception:

            pass
            # =====================================================
    # EXPORT LATEST CACHE
    # =====================================================

    def export_cache(self) -> Dict[str, Tick]:
        """
        Return a copy of the latest tick cache.
        """

        return dict(self.latest_ticks)

    # =====================================================
    # IMPORT CACHE
    # =====================================================

    def import_cache(
        self,
        cache: Dict[str, Tick],
    ) -> None:

        if cache:

            self.latest_ticks.update(cache)

    # =====================================================
    # CLEAR EVERYTHING
    # =====================================================

    def clear(self):

        self.clear_cache()

        self.parser.reset()

        self.websocket.reset()

    # =====================================================
    # HEALTH SUMMARY
    # =====================================================

    def health_summary(self) -> Dict:

        return {

            "provider": self.provider_name,

            "connected": self.connected,

            "healthy": self.healthy,

            "subscriptions": len(
                self.subscribed_instruments
            ),

            "cached_ticks": len(
                self.latest_ticks
            ),

            "messages": self.parser.total_messages,

            "ticks": self.parser.total_ticks,

            "failed": self.parser.failed_messages,

            "uptime": self.uptime,

        }

    # =====================================================
    # PING
    # =====================================================

    def ping(self) -> bool:
        """
        Lightweight connectivity check.
        """

        return self.websocket.heartbeat_ok()

    # =====================================================
    # VERSION
    # =====================================================

    @property
    def version(self) -> str:

        return "1.0.0"

    # =====================================================
    # INFO
    # =====================================================

    def info(self) -> Dict:

        return {

            "provider": self.provider_name,

            "version": self.version,

            "connected": self.connected,

            "state": self.connection_state,

            "healthy": self.healthy,

            "subscriptions": len(
                self.subscribed_instruments
            ),

        }



    # =====================================================
    # MARKET PROVIDER ABSTRACT INTERFACE IMPLEMENTATION
    # =====================================================

    def authenticate(self) -> bool:
        return self.api_client is not None

    def logout(self):
        self.stop()
        return True

    def on_tick(self, tick):
        self._on_tick(tick)

    def get_quote(self, symbol: str) -> Dict:

        tick = self.get_latest_tick(symbol)

        if tick is None:
            return {}

        if hasattr(tick, "to_dict"):
            return tick.to_dict()

        if hasattr(tick, "__dict__"):
            return dict(tick.__dict__)

        return {
            "instrument_key": symbol,
            "tick": tick,
        }

    def get_quotes(
        self,
        symbols: List[str],
    ) -> Dict:

        return {
            symbol: self.get_quote(symbol)
            for symbol in symbols
        }

    def get_ltp(self, symbol: str):

        tick = self.get_latest_tick(symbol)

        if tick is None:
            return None

        for name in (
            "ltp",
            "last_price",
            "price",
        ):

            value = getattr(
                tick,
                name,
                None,
            )

            if value is not None:
                return value

        return None

    def get_market_depth(
        self,
        symbol: str,
    ) -> Dict:

        tick = self.get_latest_tick(symbol)

        if tick is None:
            return {}

        for name in (
            "market_depth",
            "depth",
        ):

            value = getattr(
                tick,
                name,
                None,
            )

            if value is not None:
                return value

        return {}

    def get_order_book(self):
        return []

    def get_positions(self):
        return []

    def get_holdings(self):
        return []

    def historical_data(
        self,
        *args,
        **kwargs,
    ):
        return []

    def intraday_data(
        self,
        *args,
        **kwargs,
    ):
        return []

    def instrument_master(self):
        return []

    def search_symbol(
        self,
        symbol: str,
    ):
        return []

    def exchange_list(self):

        return [
            "NSE",
            "BSE",
            "NFO",
            "BFO",
            "MCX",
        ]

    def market_status(self) -> Dict:

        return {
            "connected": self.connected,
            "state": self.connection_state,
        }

    def server_time(self):

        return datetime.now()

    def heartbeat(self) -> bool:

        return self.ping()

    def provider_info(self) -> Dict:

        return self.info()

    def capabilities(self) -> Dict:

        return {
            "live_market_data": True,
            "websocket": True,
            "subscriptions": True,
            "historical_data": False,
            "intraday_data": False,
            "orders": False,
            "positions": False,
            "holdings": False,
        }

    def health(self) -> Dict:

        return self.health_summary()

    def initialize(self) -> bool:

        return self.start()

    def shutdown(self):

        self.stop()

        return True


# ==========================================================
# FACTORY
# ==========================================================

def create_upstox_provider(
    api_client,
) -> UpstoxProvider:

    """
    Factory helper.
    """

    return UpstoxProvider(
        api_client
    )


# ==========================================================
# MODULE EXPORTS
# ==========================================================

__all__ = [

    "UpstoxProvider",

    "create_upstox_provider",

]

