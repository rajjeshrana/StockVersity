from __future__ import annotations

"""
==========================================================
StockVersity Scanner Pro
Market Service

Author  : StockVersity
Version : 1.0.0

This service is responsible for:

• Market session management
• Market status
• Trading day validation
• NSE/BSE timings
• Index monitoring
• Symbol lookup
• Quote retrieval interface
• OHLC retrieval interface
• Event notifications
• Runtime statistics
• Diagnostics

Controllers should never communicate directly with
the market data provider. All requests must flow
through this service.
==========================================================
"""

import logging
import threading

from dataclasses import dataclass
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from enum import Enum
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional


# ==========================================================
# IMPORTS
# ==========================================================

from core.upstox_client import UpstoxClient


# ==========================================================
# MARKET STATE
# ==========================================================

class MarketState(Enum):
    """
    Current market state.
    """

    PRE_OPEN = "pre_open"

    OPEN = "open"

    POST_CLOSE = "post_close"

    CLOSED = "closed"

    HOLIDAY = "holiday"

    UNKNOWN = "unknown"


# ==========================================================
# EXCHANGE
# ==========================================================

class Exchange(Enum):
    """
    Supported exchanges.
    """

    NSE = "NSE"

    BSE = "BSE"

    MCX = "MCX"

    CDS = "CDS"


# ==========================================================
# MARKET SESSION
# ==========================================================

@dataclass(slots=True)
class MarketSession:
    """
    Trading session timings.
    """

    pre_open_start: time

    market_open: time

    market_close: time

    post_close_end: time


# ==========================================================
# MARKET STATISTICS
# ==========================================================

@dataclass(slots=True)
class MarketStatistics:
    """
    Runtime statistics.
    """

    quote_requests: int = 0

    ohlc_requests: int = 0

    symbol_requests: int = 0

    index_requests: int = 0

    api_errors: int = 0

    last_request: Optional[datetime] = None


# ==========================================================
# MARKET SERVICE
# ==========================================================

class MarketService:
    """
    Central market service.

    Responsibilities
    ----------------
    • Market timings
    • Trading day validation
    • Exchange abstraction
    • Quote retrieval
    • Candle retrieval
    • Index monitoring
    • Symbol management
    • Runtime diagnostics
    """

    VERSION = "1.0.0"

    NSE_SESSION = MarketSession(

        pre_open_start=time(
            9,
            0,
        ),

        market_open=time(
            9,
            15,
        ),

        market_close=time(
            15,
            30,
        ),

        post_close_end=time(
            16,
            0,
        ),
    )

    def __init__(
        self,
        client: UpstoxClient,
    ) -> None:

        self.logger = logging.getLogger(
            self.__class__.__name__
        )

        self._client = client

        self._statistics = (
            MarketStatistics()
        )

        self._event_handlers: Dict[
            str,
            List[Callable[..., None]]
        ] = {}

        self._lock = threading.RLock()

        self._started = datetime.now()

        self.logger.info(
            "MarketService initialized."
        )
    sfd
        # ==========================================================
    # PROPERTIES
    # ==========================================================

    @property
    def client(self) -> UpstoxClient:
        """
        Return the configured Upstox client.
        """

        return self._client

    @property
    def statistics(self) -> MarketStatistics:
        """
        Return runtime statistics.
        """

        return self._statistics

    @property
    def started(self) -> datetime:
        """
        Service start time.
        """

        return self._started

    @property
    def uptime(self) -> timedelta:
        """
        Service uptime.
        """

        return datetime.now() - self._started

    # ==========================================================
    # CURRENT TIME
    # ==========================================================

    def now(self) -> datetime:
        """
        Return current system time.
        """

        return datetime.now()

    def current_date(self) -> date:
        """
        Return today's date.
        """

        return self.now().date()

    def current_time(self) -> time:
        """
        Return current time.
        """

        return self.now().time()

    # ==========================================================
    # TRADING DAY
    # ==========================================================

    def is_weekend(
        self,
        check_date: Optional[date] = None,
    ) -> bool:
        """
        Return True if the supplied date is a weekend.
        """

        if check_date is None:

            check_date = self.current_date()

        return check_date.weekday() >= 5

    def is_holiday(
        self,
        check_date: Optional[date] = None,
    ) -> bool:
        """
        Return True if the supplied date is an exchange holiday.

        Holiday integration will be added through
        HolidayService in a later module.
        """

        return False

    def is_trading_day(
        self,
        check_date: Optional[date] = None,
    ) -> bool:
        """
        Return True if trading is allowed.
        """

        if check_date is None:

            check_date = self.current_date()

        return (

            not self.is_weekend(check_date)

            and

            not self.is_holiday(check_date)

        )

    # ==========================================================
    # MARKET STATE
    # ==========================================================

    def market_state(self) -> MarketState:
        """
        Determine current market state.
        """

        if not self.is_trading_day():

            return MarketState.HOLIDAY

        current = self.current_time()

        session = self.NSE_SESSION

        if (

            session.pre_open_start

            <= current

            < session.market_open

        ):

            return MarketState.PRE_OPEN

        if (

            session.market_open

            <= current

            <= session.market_close

        ):

            return MarketState.OPEN

        if (

            session.market_close

            < current

            <= session.post_close_end

        ):

            return MarketState.POST_CLOSE

        return MarketState.CLOSED

    def is_market_open(self) -> bool:
        """
        Return True if market is currently open.
        """

        return self.market_state() == MarketState.OPEN

    def is_pre_open(self) -> bool:
        """
        Return True if market is in pre-open.
        """

        return self.market_state() == MarketState.PRE_OPEN

    def is_post_close(self) -> bool:
        """
        Return True if market is in post-close.
        """

        return self.market_state() == MarketState.POST_CLOSE

    # ==========================================================
    # EVENTS
    # ==========================================================

    def register_event(
        self,
        event: str,
        callback: Callable[..., None],
    ) -> None:
        """
        Register an event callback.
        """

        self._event_handlers.setdefault(
            event,
            [],
        ).append(callback)

    def unregister_event(
        self,
        event: str,
        callback: Callable[..., None],
    ) -> None:
        """
        Remove an event callback.
        """

        if event not in self._event_handlers:

            return

        try:

            self._event_handlers[event].remove(
                callback,
            )

        except ValueError:

            pass

    def clear_events(self) -> None:
        """
        Remove all registered callbacks.
        """

        self._event_handlers.clear()

    def _emit_event(
        self,
        event: str,
        **kwargs: Any,
    ) -> None:
        """
        Notify all subscribers.
        """

        callbacks = self._event_handlers.get(
            event,
            [],
        )

        for callback in callbacks:

            try:

                callback(**kwargs)

            except Exception:

                self.logger.exception(

                    "Event callback failed (%s).",

                    event,

                )
                    # ==========================================================
    # QUOTE
    # ==========================================================

    def get_quote(
        self,
        instrument_key: str,
    ) -> Dict[str, Any]:
        """
        Return complete quote for an instrument.
        """

        self._statistics.quote_requests += 1
        self._statistics.last_request = datetime.now()

        try:

            quote = self._client.get_quote(
                instrument_key,
            )

            self._emit_event(
                "quote_received",
                instrument_key=instrument_key,
            )

            return quote

        except Exception:

            self._statistics.api_errors += 1

            self.logger.exception(
                "Failed to retrieve quote for %s.",
                instrument_key,
            )

            raise

    # ==========================================================
    # LAST TRADED PRICE
    # ==========================================================

    def get_ltp(
        self,
        instrument_key: str,
    ) -> float:
        """
        Return Last Traded Price.
        """

        quote = self.get_quote(
            instrument_key,
        )

        if isinstance(
            quote,
            dict,
        ):

            return float(

                quote.get(
                    "last_price",

                    quote.get(
                        "ltp",
                        0.0,
                    ),
                )

            )

        return 0.0

    # ==========================================================
    # OHLC
    # ==========================================================

    def get_ohlc(
        self,
        instrument_key: str,
        interval: str = "day",
    ) -> Dict[str, Any]:
        """
        Return OHLC information.
        """

        self._statistics.ohlc_requests += 1
        self._statistics.last_request = datetime.now()

        try:

            data = self._client.get_ohlc(
                instrument_key,
                interval,
            )

            self._emit_event(
                "ohlc_received",
                instrument_key=instrument_key,
                interval=interval,
            )

            return data

        except Exception:

            self._statistics.api_errors += 1

            self.logger.exception(
                "Unable to retrieve OHLC for %s.",
                instrument_key,
            )

            raise

    # ==========================================================
    # HISTORICAL CANDLES
    # ==========================================================

    def get_history(
        self,
        instrument_key: str,
        interval: str,
        from_date: date,
        to_date: date,
    ) -> List[Dict[str, Any]]:
        """
        Return historical candles.
        """

        self._statistics.ohlc_requests += 1
        self._statistics.last_request = datetime.now()

        try:

            candles = self._client.get_history(
                instrument_key=instrument_key,
                interval=interval,
                from_date=from_date,
                to_date=to_date,
            )

            self._emit_event(
                "history_received",
                instrument_key=instrument_key,
            )

            return candles

        except Exception:

            self._statistics.api_errors += 1

            self.logger.exception(
                "Failed to retrieve historical data."
            )

            raise

    # ==========================================================
    # INDEX QUOTES
    # ==========================================================

    def get_nifty(self) -> Dict[str, Any]:
        """
        Return NIFTY 50 quote.
        """

        self._statistics.index_requests += 1

        return self.get_quote(
            "NSE_INDEX|Nifty 50",
        )

    def get_banknifty(self) -> Dict[str, Any]:
        """
        Return NIFTY BANK quote.
        """

        self._statistics.index_requests += 1

        return self.get_quote(
            "NSE_INDEX|Nifty Bank",
        )

    def get_finnifty(self) -> Dict[str, Any]:
        """
        Return FINNIFTY quote.
        """

        self._statistics.index_requests += 1

        return self.get_quote(
            "NSE_INDEX|Nifty Fin Service",
        )

    def get_midcap_nifty(self) -> Dict[str, Any]:
        """
        Return NIFTY Midcap Select quote.
        """

        self._statistics.index_requests += 1

        return self.get_quote(
            "NSE_INDEX|Nifty Mid Select",
        )

    # ==========================================================
    # MARKET SNAPSHOT
    # ==========================================================

    def market_snapshot(self) -> Dict[str, Any]:
        """
        Return current market snapshot.
        """

        return {

            "timestamp":
                datetime.now(),

            "market_state":
                self.market_state().value,

            "market_open":
                self.is_market_open(),

            "nifty":
                self.get_nifty(),

            "banknifty":
                self.get_banknifty(),

            "finnifty":
                self.get_finnifty(),

        }
        # ==========================================================
    # INSTRUMENT SEARCH
    # ==========================================================

    def search_instruments(
        self,
        query: str,
        exchange: Exchange = Exchange.NSE,
    ) -> List[Dict[str, Any]]:
        """
        Search instruments by symbol or company name.
        """

        self._statistics.symbol_requests += 1
        self._statistics.last_request = datetime.now()

        try:

            instruments = self._client.search_instruments(
                exchange=exchange.value,
                query=query,
            )

            self._emit_event(
                "instrument_search",
                query=query,
                exchange=exchange.value,
            )

            return instruments

        except Exception:

            self._statistics.api_errors += 1

            self.logger.exception(
                "Instrument search failed."
            )

            raise

    # ==========================================================
    # INSTRUMENT LOOKUP
    # ==========================================================

    def get_instrument(
        self,
        symbol: str,
        exchange: Exchange = Exchange.NSE,
    ) -> Optional[Dict[str, Any]]:
        """
        Return instrument information.
        """

        results = self.search_instruments(
            query=symbol,
            exchange=exchange,
        )

        if not results:

            return None

        return results[0]

    # ==========================================================
    # INSTRUMENT KEY
    # ==========================================================

    def instrument_key(
        self,
        symbol: str,
        exchange: Exchange = Exchange.NSE,
    ) -> Optional[str]:
        """
        Return Upstox instrument key.
        """

        instrument = self.get_instrument(
            symbol=symbol,
            exchange=exchange,
        )

        if instrument is None:

            return None

        return instrument.get(
            "instrument_key",
        )

    # ==========================================================
    # SYMBOL EXISTS
    # ==========================================================

    def symbol_exists(
        self,
        symbol: str,
        exchange: Exchange = Exchange.NSE,
    ) -> bool:
        """
        Check whether a symbol exists.
        """

        return (

            self.instrument_key(
                symbol,
                exchange,
            )

            is not None

        )

    # ==========================================================
    # EXCHANGE VALIDATION
    # ==========================================================

    def is_supported_exchange(
        self,
        exchange: Exchange,
    ) -> bool:
        """
        Check exchange support.
        """

        return exchange in Exchange

    def supported_exchanges(
        self,
    ) -> List[str]:
        """
        Return supported exchanges.
        """

        return [

            exchange.value

            for exchange in Exchange

        ]

    # ==========================================================
    # SESSION INFORMATION
    # ==========================================================

    def session(
        self,
        exchange: Exchange = Exchange.NSE,
    ) -> MarketSession:
        """
        Return trading session.
        """

        if exchange == Exchange.NSE:

            return self.NSE_SESSION

        return self.NSE_SESSION

    def market_open_time(
        self,
        exchange: Exchange = Exchange.NSE,
    ) -> time:
        """
        Return market opening time.
        """

        return self.session(
            exchange
        ).market_open

    def market_close_time(
        self,
        exchange: Exchange = Exchange.NSE,
    ) -> time:
        """
        Return market closing time.
        """

        return self.session(
            exchange
        ).market_close

    # ==========================================================
    # TIME TO OPEN
    # ==========================================================

    def time_until_open(
        self,
    ) -> Optional[timedelta]:
        """
        Return remaining time until market open.
        Returns None while market is open.
        """

        if self.is_market_open():

            return None

        today = self.current_date()

        open_time = datetime.combine(

            today,

            self.market_open_time(),

        )

        current = self.now()

        if current >= open_time:

            open_time += timedelta(
                days=1,
            )

        return open_time - current

    # ==========================================================
    # TIME TO CLOSE
    # ==========================================================

    def time_until_close(
        self,
    ) -> Optional[timedelta]:
        """
        Return remaining trading time.
        """

        if not self.is_market_open():

            return None

        close_time = datetime.combine(

            self.current_date(),

            self.market_close_time(),

        )

        return close_time - self.now()

    # ==========================================================
    # MARKET STATUS
    # ==========================================================

    def market_status(
        self,
    ) -> Dict[str, Any]:
        """
        Return current market status.
        """

        return {

            "state":
                self.market_state().value,

            "is_open":
                self.is_market_open(),

            "is_trading_day":
                self.is_trading_day(),

            "server_time":
                self.now(),

            "market_open":
                self.market_open_time(),

            "market_close":
                self.market_close_time(),

            "time_until_open":
                self.time_until_open(),

            "time_until_close":
                self.time_until_close(),

        }
        # ==========================================================
    # CACHE
    # ==========================================================

    def clear_cache(self) -> None:
        """
        Clear all client-side caches maintained by the
        underlying market client, if supported.
        """

        cache_clear = getattr(
            self._client,
            "clear_cache",
            None,
        )

        if callable(cache_clear):

            cache_clear()

            self.logger.info(
                "Market cache cleared."
            )

            self._emit_event(
                "cache_cleared",
            )

    def refresh_symbols(self) -> None:
        """
        Refresh instrument master.
        """

        refresh = getattr(
            self._client,
            "refresh_instruments",
            None,
        )

        if callable(refresh):

            refresh()

            self.logger.info(
                "Instrument master refreshed."
            )

            self._emit_event(
                "symbols_refreshed",
            )

    # ==========================================================
    # HEALTH
    # ==========================================================

    def ping(self) -> bool:
        """
        Verify connectivity with the market provider.
        """

        ping = getattr(
            self._client,
            "ping",
            None,
        )

        if callable(ping):

            try:

                return bool(ping())

            except Exception:

                self._statistics.api_errors += 1

                self.logger.exception(
                    "Market ping failed."
                )

                return False

        return True

    def health(self) -> Dict[str, Any]:
        """
        Return service health.
        """

        return {

            "healthy":
                self.ping(),

            "market_open":
                self.is_market_open(),

            "market_state":
                self.market_state().value,

            "uptime":
                str(self.uptime),

            "started":
                self.started,

            "last_request":
                self.statistics.last_request,

        }

    # ==========================================================
    # STATISTICS
    # ==========================================================

    def reset_statistics(self) -> None:
        """
        Reset runtime statistics.
        """

        self._statistics = MarketStatistics()

        self.logger.info(
            "Market statistics reset."
        )

    def statistics_dict(self) -> Dict[str, Any]:
        """
        Return statistics as dictionary.
        """

        stats = self.statistics

        return {

            "quote_requests":
                stats.quote_requests,

            "ohlc_requests":
                stats.ohlc_requests,

            "symbol_requests":
                stats.symbol_requests,

            "index_requests":
                stats.index_requests,

            "api_errors":
                stats.api_errors,

            "last_request":
                stats.last_request,

            "uptime_seconds":
                int(
                    self.uptime.total_seconds()
                ),

        }

    # ==========================================================
    # PERFORMANCE
    # ==========================================================

    def performance_report(
        self,
    ) -> Dict[str, Any]:
        """
        Return a compact runtime report.
        """

        stats = self.statistics_dict()

        total_requests = (

            stats["quote_requests"]

            + stats["ohlc_requests"]

            + stats["symbol_requests"]

            + stats["index_requests"]

        )

        errors = stats["api_errors"]

        success = max(
            total_requests - errors,
            0,
        )

        success_rate = (

            100.0

            if total_requests == 0

            else

            round(

                (success / total_requests) * 100,

                2,

            )

        )

        return {

            "version":
                self.VERSION,

            "uptime":
                str(self.uptime),

            "requests":
                total_requests,

            "successful":
                success,

            "failed":
                errors,

            "success_rate":
                success_rate,

        }

    # ==========================================================
    # DIAGNOSTICS
    # ==========================================================

    def diagnostics(
        self,
    ) -> Dict[str, Any]:
        """
        Return diagnostic information.
        """

        return {

            "service":
                self.__class__.__name__,

            "version":
                self.VERSION,

            "health":
                self.health(),

            "statistics":
                self.statistics_dict(),

            "performance":
                self.performance_report(),

            "supported_exchanges":
                self.supported_exchanges(),

            "registered_events":
                {

                    name: len(callbacks)

                    for name, callbacks

                    in self._event_handlers.items()

                },

        }
        # ==========================================================
    # LIFECYCLE
    # ==========================================================

    def start(self) -> None:
        """
        Start the market service.
        """

        self.logger.info(
            "Starting MarketService..."
        )

        self._emit_event(
            "service_started",
        )

    def stop(self) -> None:
        """
        Stop the market service.
        """

        self.logger.info(
            "Stopping MarketService..."
        )

        self._emit_event(
            "service_stopped",
        )

    def restart(self) -> None:
        """
        Restart the service.
        """

        self.stop()

        self.start()

    # ==========================================================
    # SUMMARY
    # ==========================================================

    def summary(self) -> Dict[str, Any]:
        """
        Return a concise summary of the service.
        """

        return {

            "service":
                self.__class__.__name__,

            "version":
                self.VERSION,

            "market_state":
                self.market_state().value,

            "market_open":
                self.is_market_open(),

            "uptime":
                str(self.uptime),

            "requests":
                (

                    self.statistics.quote_requests

                    + self.statistics.ohlc_requests

                    + self.statistics.symbol_requests

                    + self.statistics.index_requests

                ),

            "errors":
                self.statistics.api_errors,

        }

    # ==========================================================
    # EXPORT
    # ==========================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Export service information.
        """

        return {

            "summary":
                self.summary(),

            "health":
                self.health(),

            "statistics":
                self.statistics_dict(),

            "performance":
                self.performance_report(),

            "market_status":
                self.market_status(),

        }

    # ==========================================================
    # RESET
    # ==========================================================

    def reset(self) -> None:
        """
        Reset runtime state.
        """

        self.reset_statistics()

        self.clear_events()

        self.logger.info(
            "MarketService reset completed."
        )

        self._emit_event(
            "service_reset",
        )

    # ==========================================================
    # CONTEXT MANAGER
    # ==========================================================

    def __enter__(self) -> "MarketService":
        """
        Context manager entry.
        """

        self.start()

        return self

    def __exit__(
        self,
        exc_type,
        exc,
        traceback,
    ) -> None:
        """
        Context manager exit.
        """

        self.stop()

    # ==========================================================
    # STRING REPRESENTATION
    # ==========================================================

    def __repr__(self) -> str:

        return (

            f"{self.__class__.__name__}("

            f"state={self.market_state().value}, "

            f"uptime='{self.uptime}', "

            f"quotes={self.statistics.quote_requests}, "

            f"errors={self.statistics.api_errors})"

        )

    def __str__(self) -> str:

        return (

            f"{self.__class__.__name__}"

            f"[{self.market_state().value}]"

        )

    # ==========================================================
    # DEBUG
    # ==========================================================

    def dump(self) -> Dict[str, Any]:
        """
        Return full runtime dump for debugging.
        """

        return {

            "repr":
                repr(self),

            "summary":
                self.summary(),

            "diagnostics":
                self.diagnostics(),

            "event_handlers":
                {

                    event: len(callbacks)

                    for event, callbacks

                    in self._event_handlers.items()

                },

        }
        # ==========================================================
    # VALIDATION
    # ==========================================================

    def validate(self) -> bool:
        """
        Validate MarketService configuration.
        """

        if self._client is None:

            raise RuntimeError(
                "Upstox client is not configured."
            )

        return True

    def assert_ready(self) -> None:
        """
        Ensure the service is ready.
        """

        self.validate()

    # ==========================================================
    # CONNECTION
    # ==========================================================

    def connected(self) -> bool:
        """
        Return True if the underlying client is connected.
        """

        checker = getattr(
            self._client,
            "is_connected",
            None,
        )

        if callable(checker):

            try:

                return bool(checker())

            except Exception:

                return False

        return True

    # ==========================================================
    # EVENT UTILITIES
    # ==========================================================

    def event_count(self) -> int:
        """
        Return total registered callbacks.
        """

        return sum(

            len(callbacks)

            for callbacks

            in self._event_handlers.values()

        )

    def events(self) -> Dict[str, int]:
        """
        Return registered event summary.
        """

        return {

            event: len(callbacks)

            for event, callbacks

            in self._event_handlers.items()

        }

    def has_event(
        self,
        event: str,
    ) -> bool:
        """
        Check whether an event has subscribers.
        """

        return (

            event in self._event_handlers

            and

            len(
                self._event_handlers[event]
            ) > 0

        )

    # ==========================================================
    # INFORMATION
    # ==========================================================

    def info(self) -> Dict[str, Any]:
        """
        Return general service information.
        """

        return {

            "service":
                self.__class__.__name__,

            "version":
                self.VERSION,

            "connected":
                self.connected(),

            "market_state":
                self.market_state().value,

            "market_open":
                self.is_market_open(),

            "uptime":
                str(self.uptime),

        }

    # ==========================================================
    # SNAPSHOT
    # ==========================================================

    def snapshot(self) -> Dict[str, Any]:
        """
        Return complete runtime snapshot.
        """

        return {

            "info":
                self.info(),

            "market":
                self.market_status(),

            "statistics":
                self.statistics_dict(),

            "performance":
                self.performance_report(),

            "events":
                self.events(),

        }

    # ==========================================================
    # CLONE
    # ==========================================================

    def clone(self) -> "MarketService":
        """
        Create a new MarketService instance using the
        same Upstox client.
        """

        return self.__class__(

            client=self._client,

        )

    # ==========================================================
    # DISPOSE
    # ==========================================================

    def dispose(self) -> None:
        """
        Release runtime resources.
        """

        self.clear_events()

        self.logger.info(
            "MarketService disposed."
        )

    # ==========================================================
    # FACTORY
    # ==========================================================

    @classmethod
    def create(
        cls,
        client: UpstoxClient,
    ) -> "MarketService":
        """
        Factory constructor.
        """

        return cls(client)

# ==========================================================
# MODULE HELPERS
# ==========================================================

def create_market_service(
    client: UpstoxClient,
) -> MarketService:
    """
    Convenience factory.
    """

    return MarketService.create(
        client,
    )


def build_market_service(
    client: UpstoxClient,
) -> MarketService:
    """
    Alternate factory helper.
    """

    return MarketService(
        client,
    )
# ==========================================================
# MODULE EXPORTS
# ==========================================================

__all__ = [

    "Exchange",

    "MarketSession",

    "MarketState",

    "MarketStatistics",

    "MarketService",

    "create_market_service",

    "build_market_service",

]

# ==========================================================
# END OF FILE
# ==========================================================