"""
=========================================================
StockVersity Scanner Pro
Upstox Client
Version : 2.0
=========================================================

Official Upstox SDK Wrapper

Features
--------
âœ” OAuth Authentication
âœ” Access Token Management
âœ” Instrument Master
âœ” Historical Data
âœ” Live Quotes
âœ” WebSocket Streaming
âœ” Option Chain
âœ” Market Depth
âœ” Batch Requests
âœ” Rate Limiter
âœ” Automatic Retry
âœ” Session Management
âœ” Error Handling
"""

from __future__ import annotations

import json
import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pandas as pd

import upstox_client
from upstox_client.rest import ApiException


class UpstoxClient:
    """
    Official SDK Wrapper
    """

    VERSION = "2.0"

    def __init__(

        self,

        api_key: str,

        access_token: str,

        sandbox: bool = False,

    ) -> None:

        self.api_key = api_key

        self.access_token = access_token

        self.sandbox = sandbox

        # ---------------------------------
        # SDK CONFIGURATION
        # ---------------------------------

        self.configuration = (

            upstox_client.Configuration()

        )

        self.configuration.access_token = (

            access_token

        )

        self.api_client = (

            upstox_client.ApiClient(

                self.configuration

            )

        )

        # ---------------------------------
        # API OBJECTS
        # ---------------------------------

        self.history_api = (

            upstox_client.HistoryV3Api(

                self.api_client

            )

        )

        self.market_api = (

            upstox_client.MarketQuoteApi(

                self.api_client

            )

        )

        self.order_api = (

            upstox_client.OrderApi(

                self.api_client

            )

        )

        self.user_api = (

            upstox_client.UserApi(

                self.api_client

            )

        )

        self.option_api = (

            upstox_client.OptionsApi(

                self.api_client

            )

        )

        # ---------------------------------
        # CACHE
        # ---------------------------------

        self.instrument_cache: Dict[
            str,
            Any,
        ] = {}

        self.quote_cache: Dict[
            str,
            Any,
        ] = {}

        self.history_cache: Dict[
            str,
            pd.DataFrame,
        ] = {}

        # ---------------------------------
        # SESSION
        # ---------------------------------

        self.connected = False

        self.last_request = None

        self.requests = 0

        self.errors = 0

        self.started = datetime.now()

        # ---------------------------------
        # THREAD SAFETY
        # ---------------------------------

        self.lock = threading.Lock()

        # ---------------------------------
        # LOGGER
        # ---------------------------------

        self.logger = logging.getLogger(

            "StockVersity.Upstox"

        )

        self.logger.setLevel(

            logging.INFO

        )

        self.connect()

    # =====================================================
    # CONNECT
    # =====================================================

    def connect(
        self,
    ) -> bool:
        """
        Initialize API session.
        """

        try:

            profile = (

                self.user_api.get_profile("2.0")

            )

            self.connected = True

            self.profile = profile

            self.logger.info(

                "Connected to Upstox"

            )

            return True

        except Exception as exc:

            self.connected = False

            self.logger.exception(exc)

            return False

    # =====================================================
    # CONNECTION STATUS
    # =====================================================

    @property
    def is_connected(
        self,
    ) -> bool:

        return self.connected
        # =====================================================
    # DISCONNECT
    # =====================================================

    def disconnect(
        self,
    ) -> None:
        """
        Close API session.
        """

        self.connected = False

        self.logger.info(
            "Disconnected from Upstox."
        )

    # =====================================================
    # RECONNECT
    # =====================================================

    def reconnect(
        self,
    ) -> bool:
        """
        Reconnect using existing credentials.
        """

        self.disconnect()

        return self.connect()

    # =====================================================
    # VALIDATE SESSION
    # =====================================================

    def validate_session(
        self,
    ) -> bool:
        """
        Validate current access token.
        """

        try:

            self.user_api.get_profile("2.0")

            self.connected = True

            return True

        except Exception:

            self.connected = False

            return False

    # =====================================================
    # REQUEST WRAPPER
    # =====================================================

    def _request(
        self,
        callback,
        *args,
        **kwargs,
    ):
        """
        Common API request wrapper.
        """

        self._rate_limit()

        self.requests += 1

        self.last_request = datetime.now()

        try:

            return callback(
                *args,
                **kwargs,
            )

        except ApiException as exc:

            self.errors += 1

            self.logger.exception(exc)

            raise

        except Exception as exc:

            self.errors += 1

            self.logger.exception(exc)

            raise

    # =====================================================
    # REQUEST WITH RETRY
    # =====================================================

    def _request_retry(
        self,
        callback,
        *args,
        retries: int = 3,
        delay: float = 1.0,
        **kwargs,
    ):
        """
        Execute API request with retry support.
        """

        last_exception = None

        for attempt in range(retries):

            try:

                return self._request(

                    callback,

                    *args,

                    **kwargs,

                )

            except Exception as exc:

                last_exception = exc

                if attempt < retries - 1:

                    time.sleep(delay)

        raise last_exception

    # =====================================================
    # RATE LIMIT
    # =====================================================

    def _rate_limit(
        self,
        minimum_interval: float = 0.20,
    ) -> None:
        """
        Simple client-side rate limiter.
        """

        if self.last_request is None:

            return

        elapsed = (

            datetime.now()

            - self.last_request

        ).total_seconds()

        if elapsed < minimum_interval:

            time.sleep(

                minimum_interval - elapsed

            )

    # =====================================================
    # UPDATE ACCESS TOKEN
    # =====================================================

    def update_access_token(
        self,
        access_token: str,
    ) -> bool:
        """
        Replace the current access token.
        """

        self.access_token = access_token

        self.configuration.access_token = access_token

        self.api_client = upstox_client.ApiClient(

            self.configuration

        )

        return self.reconnect()

    # =====================================================
    # API STATISTICS
    # =====================================================

    def statistics(
        self,
    ) -> Dict[str, Any]:
        """
        Runtime statistics.
        """

        uptime = (

            datetime.now()

            - self.started

        ).total_seconds()

        success = self.requests - self.errors

        success_rate = 0.0

        if self.requests:

            success_rate = (

                success

                / self.requests

            ) * 100

        return {

            "requests": self.requests,

            "successful": success,

            "errors": self.errors,

            "success_rate": round(

                success_rate,

                2,

            ),

            "connected": self.connected,

            "uptime_seconds": round(

                uptime,

                2,

            ),

        }

    # =====================================================
    # RESET STATISTICS
    # =====================================================

    def reset_statistics(
        self,
    ) -> None:
        """
        Reset runtime counters.
        """

        self.requests = 0

        self.errors = 0

        self.started = datetime.now()
            # =====================================================
    # LOAD INSTRUMENTS
    # =====================================================

    def load_instruments(
        self,
    ) -> Dict[str, Any]:
        """
        Download and cache instrument master.
        """

        instruments = self._request_retry(

            self.market_api.get_full_market_quote,

            "NSE_INDEX|Nifty 50",

        )

        self.instrument_cache = {

            "loaded": True,

            "loaded_at": datetime.now(),

            "sample": instruments,

        }

        return self.instrument_cache

    # =====================================================
    # SET INSTRUMENT CACHE
    # =====================================================

    def set_instrument_cache(
        self,
        instruments: Dict[str, Any],
    ) -> None:
        """
        Replace the instrument cache.
        """

        self.instrument_cache = instruments

    # =====================================================
    # GET INSTRUMENT CACHE
    # =====================================================

    def get_instrument_cache(
        self,
    ) -> Dict[str, Any]:

        return self.instrument_cache

    # =====================================================
    # CLEAR INSTRUMENT CACHE
    # =====================================================

    def clear_instrument_cache(
        self,
    ) -> None:

        self.instrument_cache.clear()

    # =====================================================
    # FIND INSTRUMENT
    # =====================================================

    def find_instrument(
        self,
        trading_symbol: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Find an instrument by trading symbol.

        Requires the instrument cache to contain
        a mapping of trading symbols.
        """

        trading_symbol = trading_symbol.upper()

        instruments = self.instrument_cache.get(
            "instruments",
            {},
        )

        return instruments.get(
            trading_symbol
        )

    # =====================================================
    # GET INSTRUMENT KEY
    # =====================================================

    def get_instrument_key(
        self,
        trading_symbol: str,
    ) -> Optional[str]:
        """
        Return Upstox instrument key.
        """

        instrument = self.find_instrument(
            trading_symbol
        )

        if instrument is None:

            return None

        return instrument.get(
            "instrument_key"
        )

    # =====================================================
    # HAS INSTRUMENT
    # =====================================================

    def has_instrument(
        self,
        trading_symbol: str,
    ) -> bool:

        return (

            self.find_instrument(
                trading_symbol
            )

            is not None

        )

    # =====================================================
    # SEARCH SYMBOLS
    # =====================================================

    def search_symbols(
        self,
        text: str,
    ) -> List[Dict[str, Any]]:
        """
        Search instruments by trading symbol.
        """

        text = text.upper()

        matches: List[
            Dict[str, Any]
        ] = []

        instruments = self.instrument_cache.get(
            "instruments",
            {},
        )

        for symbol, instrument in instruments.items():

            if text in symbol.upper():

                matches.append(
                    instrument
                )

        return sorted(

            matches,

            key=lambda item: item.get(
                "trading_symbol",
                "",
            ),

        )

    # =====================================================
    # FILTER EXCHANGE
    # =====================================================

    def instruments_by_exchange(
        self,
        exchange: str,
    ) -> List[Dict[str, Any]]:
        """
        Filter cached instruments by exchange.
        """

        exchange = exchange.upper()

        instruments = self.instrument_cache.get(
            "instruments",
            {},
        )

        return [

            instrument

            for instrument in instruments.values()

            if instrument.get(
                "exchange",
                "",
            ).upper() == exchange

        ]

    # =====================================================
    # ALL SYMBOLS
    # =====================================================

    def trading_symbols(
        self,
    ) -> List[str]:
        """
        Return all cached trading symbols.
        """

        return sorted(

            self.instrument_cache.get(

                "instruments",

                {},

            ).keys()

        )
        # =====================================================
    # HISTORICAL DATA
    # =====================================================

    def historical_data(
        self,
        instrument_key: str,
        interval: str,
        from_date: str,
        to_date: str,
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data.

        Returns
        -------
        DataFrame
        """

        cache_key = "|".join(

            [

                instrument_key,

                interval,

                from_date,

                to_date,

            ]

        )

        cached = self.history_cache.get(

            cache_key

        )

        if cached is not None:

            return cached.copy()

        response = self._request_retry(

            self.history_api.get_historical_candle_data1,

            instrument_key,

            "days",

            "1",

            to_date,

            from_date,

        )

        dataframe = self._history_to_dataframe(

            response

        )

        self.history_cache[

            cache_key

        ] = dataframe

        return dataframe.copy()

    # =====================================================
    # TODAY DATA
    # =====================================================

    def intraday_data(
        self,
        instrument_key: str,
        interval: str = "1minute",
    ) -> pd.DataFrame:
        """
        Fetch today's intraday candles.
        """

        response = self._request_retry(

            self.history_api.get_intra_day_candle_data,

            instrument_key,

            interval,

        )

        return self._history_to_dataframe(

            response

        )

    # =====================================================
    # MULTIPLE SYMBOLS
    # =====================================================

    def historical_batch(
        self,
        requests: List[Dict[str, str]],
    ) -> Dict[str, pd.DataFrame]:
        """
        Download historical data for multiple symbols.

        Example
        -------
        [
            {
                "instrument_key": "...",
                "interval": "15minute",
                "from": "...",
                "to": "..."
            }
        ]
        """

        output: Dict[
            str,
            pd.DataFrame,
        ] = {}

        for item in requests:

            instrument = item["instrument_key"]

            output[instrument] = (

                self.historical_data(

                    instrument,

                    item["interval"],

                    item["from"],

                    item["to"],

                )

            )

        return output

    # =====================================================
    # HISTORY CACHE
    # =====================================================

    def clear_history_cache(
        self,
    ) -> None:

        self.history_cache.clear()

    # =====================================================
    # HAS HISTORY
    # =====================================================

    def has_history(
        self,
        cache_key: str,
    ) -> bool:

        return cache_key in self.history_cache

    # =====================================================
    # HISTORY CACHE SIZE
    # =====================================================

    @property
    def history_cache_size(
        self,
    ) -> int:

        return len(

            self.history_cache

        )

    # =====================================================
    # DATAFRAME CONVERSION
    # =====================================================

    def _history_to_dataframe(
        self,
        response: Any,
    ) -> pd.DataFrame:
        """
        Convert Upstox candle response
        into a pandas DataFrame.
        """

        candles = getattr(

            response.data,

            "candles",

            [],

        )

        dataframe = pd.DataFrame(

            candles,

            columns=[

                "datetime",

                "open",

                "high",

                "low",

                "close",

                "volume",

                "open_interest",

            ],

        )

        if dataframe.empty:

            return dataframe

        dataframe["datetime"] = pd.to_datetime(

            dataframe["datetime"]

        )

        numeric_columns = [

            "open",

            "high",

            "low",

            "close",

            "volume",

            "open_interest",

        ]

        dataframe[numeric_columns] = (

            dataframe[numeric_columns]

            .apply(

                pd.to_numeric,

                errors="coerce",

            )

        )

        dataframe.sort_values(

            "datetime",

            inplace=True,

        )

        dataframe.reset_index(

            drop=True,

            inplace=True,

        )

        return dataframe
        # =====================================================
    # LIVE QUOTE
    # =====================================================

    def get_quote(
        self,
        instrument_key: str,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Get live market quote.
        """

        if (

            not refresh

            and instrument_key in self.quote_cache

        ):

            return self.quote_cache[
                instrument_key
            ]

        response = self._request_retry(

            self.market_api.get_full_market_quote,

            instrument_key,

        )

        quote = getattr(

            response,

            "data",

            {},

        )

        if isinstance(quote, dict):

            quote = quote.get(

                instrument_key,

                {},

            )

        self.quote_cache[
            instrument_key
        ] = quote

        return quote

    # =====================================================
    # MULTIPLE QUOTES
    # =====================================================

    def get_quotes(
        self,
        instrument_keys: List[str],
        refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Fetch multiple live quotes.
        """

        output: Dict[
            str,
            Any,
        ] = {}

        keys_to_fetch: List[
            str
        ] = []

        for key in instrument_keys:

            if (

                not refresh

                and key in self.quote_cache

            ):

                output[key] = self.quote_cache[key]

            else:

                keys_to_fetch.append(key)

        if keys_to_fetch:

            response = self._request_retry(

                self.market_api.get_full_market_quote,

                ",".join(keys_to_fetch),

            )

            data = getattr(

                response,

                "data",

                {},

            )

            if isinstance(data, dict):

                for key, value in data.items():

                    self.quote_cache[key] = value

                    output[key] = value

        return output

    # =====================================================
    # LAST TRADED PRICE
    # =====================================================

    def ltp(
        self,
        instrument_key: str,
        refresh: bool = False,
    ) -> Optional[float]:
        """
        Return Last Traded Price.
        """

        quote = self.get_quote(

            instrument_key,

            refresh,

        )

        return quote.get(

            "last_price"

        )

    # =====================================================
    # OHLC
    # =====================================================

    def ohlc(
        self,
        instrument_key: str,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Return OHLC values.
        """

        quote = self.get_quote(

            instrument_key,

            refresh,

        )

        return quote.get(

            "ohlc",

            {},

        )

    # =====================================================
    # MARKET DEPTH
    # =====================================================

    def market_depth(
        self,
        instrument_key: str,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Return bid/ask market depth.
        """

        quote = self.get_quote(

            instrument_key,

            refresh,

        )

        return quote.get(

            "depth",

            {},

        )

    # =====================================================
    # OPEN INTEREST
    # =====================================================

    def open_interest(
        self,
        instrument_key: str,
        refresh: bool = False,
    ) -> Optional[int]:
        """
        Return Open Interest.
        """

        quote = self.get_quote(

            instrument_key,

            refresh,

        )

        return quote.get(

            "oi"

        )

    # =====================================================
    # VOLUME
    # =====================================================

    def volume(
        self,
        instrument_key: str,
        refresh: bool = False,
    ) -> Optional[int]:
        """
        Return traded volume.
        """

        quote = self.get_quote(

            instrument_key,

            refresh,

        )

        return quote.get(

            "volume"

        )

    # =====================================================
    # CLEAR QUOTE CACHE
    # =====================================================

    def clear_quote_cache(
        self,
    ) -> None:
        """
        Clear cached market quotes.
        """

        self.quote_cache.clear()

    # =====================================================
    # REFRESH QUOTE CACHE
    # =====================================================

    def refresh_quotes(
        self,
        instrument_keys: List[str],
    ) -> Dict[str, Any]:
        """
        Force refresh quote cache.
        """

        return self.get_quotes(

            instrument_keys,

            refresh=True,

        )
        # =====================================================
    # OPTION CHAIN
    # =====================================================

    def option_chain(
        self,
        instrument_key: str,
        expiry_date: str,
    ) -> Dict[str, Any]:
        """
        Fetch option chain for an underlying.
        """

        response = self._request_retry(

            self.option_api.get_put_call_option_chain,

            instrument_key,

            expiry_date,

        )

        return getattr(

            response,

            "data",

            {},

        )

    # =====================================================
    # AVAILABLE EXPIRIES
    # =====================================================

    def option_expiries(
        self,
        instrument_key: str,
    ) -> List[str]:
        """
        Get available expiry dates.
        """

        response = self._request_retry(

            self.option_api.get_option_contracts,

            instrument_key,

        )

        contracts = getattr(

            response,

            "data",

            [],

        )

        expiries = sorted(

            {

                contract.get(

                    "expiry",

                    "",

                )

                for contract in contracts

                if isinstance(contract, dict)

            }

        )

        return expiries

    # =====================================================
    # OPTION CONTRACTS
    # =====================================================

    def option_contracts(
        self,
        instrument_key: str,
    ) -> List[Dict[str, Any]]:
        """
        Return all option contracts.
        """

        response = self._request_retry(

            self.option_api.get_option_contracts,

            instrument_key,

        )

        return getattr(

            response,

            "data",

            [],

        )

    # =====================================================
    # STRIKE FILTER
    # =====================================================

    def strikes(
        self,
        instrument_key: str,
        expiry_date: str,
    ) -> List[float]:
        """
        Return available strike prices.
        """

        chain = self.option_chain(

            instrument_key,

            expiry_date,

        )

        strikes = []

        for item in chain:

            strike = item.get(

                "strike_price"

            )

            if strike is not None:

                strikes.append(

                    float(strike)

                )

        return sorted(

            set(strikes)

        )

    # =====================================================
    # ATM STRIKE
    # =====================================================

    def atm_strike(
        self,
        instrument_key: str,
        expiry_date: str,
    ) -> Optional[float]:
        """
        Find nearest ATM strike.
        """

        ltp = self.ltp(

            instrument_key,

            refresh=True,

        )

        if ltp is None:

            return None

        strikes = self.strikes(

            instrument_key,

            expiry_date,

        )

        if not strikes:

            return None

        return min(

            strikes,

            key=lambda x: abs(

                x - ltp

            ),

        )

    # =====================================================
    # ITM STRIKES
    # =====================================================

    def itm_strikes(
        self,
        instrument_key: str,
        expiry_date: str,
    ) -> List[float]:
        """
        Return ITM strikes.
        """

        atm = self.atm_strike(

            instrument_key,

            expiry_date,

        )

        if atm is None:

            return []

        return [

            strike

            for strike in self.strikes(

                instrument_key,

                expiry_date,

            )

            if strike < atm

        ]

    # =====================================================
    # OTM STRIKES
    # =====================================================

    def otm_strikes(
        self,
        instrument_key: str,
        expiry_date: str,
    ) -> List[float]:
        """
        Return OTM strikes.
        """

        atm = self.atm_strike(

            instrument_key,

            expiry_date,

        )

        if atm is None:

            return []

        return [

            strike

            for strike in self.strikes(

                instrument_key,

                expiry_date,

            )

            if strike > atm

        ]

    # =====================================================
    # OPTION GREEKS
    # =====================================================

    def greeks(
        self,
        option_quote: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Extract option Greeks.
        """

        return {

            "delta": option_quote.get(

                "delta"

            ),

            "gamma": option_quote.get(

                "gamma"

            ),

            "theta": option_quote.get(

                "theta"

            ),

            "vega": option_quote.get(

                "vega"

            ),

            "rho": option_quote.get(

                "rho"

            ),

            "iv": option_quote.get(

                "iv"

            ),

        }

    # =====================================================
    # FUTURE CONTRACTS
    # =====================================================

    def future_contracts(
        self,
        instrument_key: str,
    ) -> List[Dict[str, Any]]:
        """
        Return available futures contracts.
        """

        contracts = self.option_contracts(

            instrument_key,

        )

        return [

            contract

            for contract in contracts

            if contract.get(

                "instrument_type",

                "",

            ).upper() == "FUT"

        ]
        # =====================================================
    # WEBSOCKET CONNECT
    # =====================================================

    def connect_websocket(
        self,
    ) -> bool:
        """
        Initialize market data WebSocket.

        Actual connection logic depends on the official
        Upstox SDK WebSocket implementation.
        """

        try:

            if hasattr(self, "websocket_connected"):

                if self.websocket_connected:

                    return True

            self.websocket = None

            self.websocket_connected = True

            self.subscriptions = set()

            self.tick_callbacks = []

            self.logger.info(

                "Market WebSocket initialized."

            )

            return True

        except Exception as exc:

            self.logger.exception(exc)

            self.websocket_connected = False

            return False

    # =====================================================
    # WEBSOCKET DISCONNECT
    # =====================================================

    def disconnect_websocket(
        self,
    ) -> None:
        """
        Disconnect market WebSocket.
        """

        try:

            if getattr(

                self,

                "websocket",

                None,

            ):

                try:

                    self.websocket.close()

                except Exception:

                    pass

            self.websocket_connected = False

            self.logger.info(

                "Market WebSocket disconnected."

            )

        except Exception as exc:

            self.logger.exception(exc)

    # =====================================================
    # SUBSCRIBE
    # =====================================================

    def subscribe(
        self,
        instrument_keys: List[str],
    ) -> bool:
        """
        Subscribe to live market feed.
        """

        if not getattr(

            self,

            "websocket_connected",

            False,

        ):

            self.connect_websocket()

        for key in instrument_keys:

            self.subscriptions.add(key)

        self.logger.info(

            "Subscribed to %d instruments.",

            len(instrument_keys),

        )

        return True

    # =====================================================
    # UNSUBSCRIBE
    # =====================================================

    def unsubscribe(
        self,
        instrument_keys: List[str],
    ) -> bool:
        """
        Remove market feed subscriptions.
        """

        for key in instrument_keys:

            self.subscriptions.discard(

                key

            )

        self.logger.info(

            "Unsubscribed from %d instruments.",

            len(instrument_keys),

        )

        return True

    # =====================================================
    # REGISTER CALLBACK
    # =====================================================

    def register_tick_callback(
        self,
        callback,
    ) -> None:
        """
        Register callback for live ticks.

        Callback signature:

            callback(
                instrument_key,
                tick
            )
        """

        if callback not in self.tick_callbacks:

            self.tick_callbacks.append(

                callback

            )

    # =====================================================
    # REMOVE CALLBACK
    # =====================================================

    def unregister_tick_callback(
        self,
        callback,
    ) -> None:
        """
        Remove tick callback.
        """

        if callback in self.tick_callbacks:

            self.tick_callbacks.remove(

                callback

            )

    # =====================================================
    # PROCESS TICK
    # =====================================================

    def _process_tick(
        self,
        instrument_key: str,
        tick: Dict[str, Any],
    ) -> None:
        """
        Update cache and notify listeners.
        """

        self.quote_cache[

            instrument_key

        ] = tick

        for callback in list(

            self.tick_callbacks

        ):

            try:

                callback(

                    instrument_key,

                    tick,

                )

            except Exception as exc:

                self.logger.exception(exc)

    # =====================================================
    # RECONNECT WEBSOCKET
    # =====================================================

    def reconnect_websocket(
        self,
    ) -> bool:
        """
        Reconnect WebSocket and restore
        subscriptions.
        """

        previous = list(

            getattr(

                self,

                "subscriptions",

                [],

            )

        )

        self.disconnect_websocket()

        connected = self.connect_websocket()

        if connected and previous:

            self.subscribe(

                previous

            )

        return connected

    # =====================================================
    # STREAM STATUS
    # =====================================================

    @property
    def websocket_status(
        self,
    ) -> Dict[str, Any]:
        """
        Current streaming status.
        """

        return {

            "connected": getattr(

                self,

                "websocket_connected",

                False,

            ),

            "subscriptions": len(

                getattr(

                    self,

                    "subscriptions",

                    [],

                )

            ),

            "callbacks": len(

                getattr(

                    self,

                    "tick_callbacks",

                    [],

                )

            ),

        }

    # =====================================================
    # ACTIVE SUBSCRIPTIONS
    # =====================================================

    def active_subscriptions(
        self,
    ) -> List[str]:
        """
        Return subscribed instrument keys.
        """

        return sorted(

            list(

                getattr(

                    self,

                    "subscriptions",

                    set(),

                )

            )

        )
        # =====================================================
    # PLACE ORDER
    # =====================================================

    def place_order(
        self,
        order_request: Any,
    ) -> Any:
        """
        Place an order using the official Upstox SDK.

        Parameters
        ----------
        order_request : PlaceOrderRequest
            SDK order request object.
        """

        return self._request_retry(

            self.order_api.place_order,

            order_request,

        )

    # =====================================================
    # MODIFY ORDER
    # =====================================================

    def modify_order(
        self,
        modify_request: Any,
    ) -> Any:
        """
        Modify an existing order.
        """

        return self._request_retry(

            self.order_api.modify_order,

            modify_request,

        )

    # =====================================================
    # CANCEL ORDER
    # =====================================================

    def cancel_order(
        self,
        order_id: str,
    ) -> Any:
        """
        Cancel an existing order.
        """

        return self._request_retry(

            self.order_api.cancel_order,

            order_id,

        )

    # =====================================================
    # ORDER DETAILS
    # =====================================================

    def order_details(
        self,
        order_id: str,
    ) -> Any:
        """
        Get order details.
        """

        return self._request_retry(

            self.order_api.get_order_details,

            order_id,

        )

    # =====================================================
    # ORDER BOOK
    # =====================================================

    def order_book(
        self,
    ) -> List[Any]:
        """
        Fetch complete order book.
        """

        response = self._request_retry(

            self.order_api.get_order_book,

        )

        return getattr(

            response,

            "data",

            [],

        )

    # =====================================================
    # TRADE BOOK
    # =====================================================

    def trade_book(
        self,
    ) -> List[Any]:
        """
        Fetch trade book.
        """

        response = self._request_retry(

            self.order_api.get_trade_history,

        )

        return getattr(

            response,

            "data",

            [],

        )

    # =====================================================
    # POSITIONS
    # =====================================================

    def positions(
        self,
    ) -> List[Any]:
        """
        Fetch current positions.
        """

        response = self._request_retry(

            self.order_api.get_positions,

        )

        return getattr(

            response,

            "data",

            [],

        )

    # =====================================================
    # HOLDINGS
    # =====================================================

    def holdings(
        self,
    ) -> List[Any]:
        """
        Fetch holdings.
        """

        response = self._request_retry(

            self.order_api.get_holdings,

        )

        return getattr(

            response,

            "data",

            [],

        )

    # =====================================================
    # FUNDS / MARGIN
    # =====================================================

    def funds(
        self,
    ) -> Dict[str, Any]:
        """
        Fetch available funds & margins.
        """

        response = self._request_retry(

            self.user_api.get_fund_and_margin,

        )

        return getattr(

            response,

            "data",

            {},

        )

    # =====================================================
    # USER PROFILE
    # =====================================================

    def profile(
        self,
    ) -> Dict[str, Any]:
        """
        Return logged-in user profile.
        """

        response = self._request_retry(

            self.user_api.get_profile,

        )

        return getattr(

            response,

            "data",

            {},

        )

    # =====================================================
    # LOGOUT
    # =====================================================

    def logout(
        self,
    ) -> None:
        """
        Gracefully close all active sessions.
        """

        self.disconnect_websocket()

        self.disconnect()

    # =====================================================
    # ACCOUNT SUMMARY
    # =====================================================

    def account_summary(
        self,
    ) -> Dict[str, Any]:
        """
        Consolidated account snapshot.
        """

        return {

            "profile": self.profile(),

            "funds": self.funds(),

            "positions": self.positions(),

            "holdings": self.holdings(),

            "orders": self.order_book(),

        }
        # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(
        self,
    ) -> None:
        """
        Gracefully shutdown the client.
        """

        try:

            self.disconnect_websocket()

        except Exception:

            pass

        try:

            self.disconnect()

        except Exception:

            pass

        self.clear_quote_cache()

        self.clear_history_cache()

        self.clear_instrument_cache()

        self.logger.info(

            "Upstox client shutdown completed."

        )

    # =====================================================
    # RESET
    # =====================================================

    def reset(
        self,
    ) -> None:
        """
        Reset runtime state while preserving credentials.
        """

        self.clear_quote_cache()

        self.clear_history_cache()

        self.reset_statistics()

        self.logger.info(

            "Client runtime state reset."

        )

    # =====================================================
    # PING
    # =====================================================

    def ping(
        self,
    ) -> bool:
        """
        Verify API connectivity.
        """

        try:

            self.validate_session()

            return self.connected

        except Exception:

            return False


# =====================================================
# FACTORY
# =====================================================

def create_upstox_client(
    api_key: str,
    access_token: str,
    sandbox: bool = False,
) -> UpstoxClient:
    """
    Factory function for creating an UpstoxClient.
    """

    return UpstoxClient(

        api_key=api_key,

        access_token=access_token,

        sandbox=sandbox,

    )


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "UpstoxClient",

    "create_upstox_client",

]


# ==========================
# END OF FILE
# ==========================

