"""
==========================================================
StockVersity Scanner Pro
Upstox REST API Client
==========================================================

Handles all REST communication with Upstox.

Responsibilities
----------------
✔ Profile
✔ Funds
✔ Holdings
✔ Positions
✔ Instruments
✔ Market Quote
✔ Historical Data
✔ WebSocket Authorization
"""

from __future__ import annotations

import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from core.authentication.authentication import Authentication
from core.network.http_client import HttpClient

logger = logging.getLogger(__name__)


class UpstoxAPI:
    """
    Wrapper around Upstox REST API.

    Example
    -------
    api = UpstoxAPI(auth)

    profile = api.get_profile()

    quote = api.get_market_quote(
        ["NSE_EQ|INE002A01018"]
    )
    """

    BASE_URL = "https://api.upstox.com/v2"

    ####################################################################
    # Constructor
    ####################################################################

    def __init__(
        self,
        authentication: Authentication,
    ) -> None:

        self._auth = authentication

        self._client = HttpClient(
            base_url=self.BASE_URL
        )

    ####################################################################
    # Internal Helpers
    ####################################################################

    def _headers(self) -> Dict[str, str]:
        """
        Returns authenticated headers.
        """

        token = self._auth.access_token

        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict:

        logger.debug("GET %s", endpoint)

        return self._client.get(
            endpoint=endpoint,
            headers=self._headers(),
            params=params,
        )

    def _post(
        self,
        endpoint: str,
        payload: Optional[Dict] = None,
    ) -> Dict:

        logger.debug("POST %s", endpoint)

        return self._client.post(
            endpoint=endpoint,
            headers=self._headers(),
            json=payload,
        )
        ####################################################################
    # User Profile
    ####################################################################

    def get_profile(self) -> Dict:
        """
        Returns logged-in user profile.

        Endpoint:
            GET /user/profile
        """

        return self._get(
            "/user/profile"
        )

    ####################################################################
    # Funds
    ####################################################################

    def get_funds(self) -> Dict:
        """
        Returns available funds.

        Endpoint:
            GET /user/get-funds-and-margin
        """

        return self._get(
            "/user/get-funds-and-margin"
        )

    ####################################################################
    # Holdings
    ####################################################################

    def get_holdings(self) -> Dict:
        """
        Returns current holdings.

        Endpoint:
            GET /portfolio/long-term-holdings
        """

        return self._get(
            "/portfolio/long-term-holdings"
        )

    ####################################################################
    # Positions
    ####################################################################

    def get_positions(self) -> Dict:
        """
        Returns intraday + overnight positions.

        Endpoint:
            GET /portfolio/short-term-positions
        """

        return self._get(
            "/portfolio/short-term-positions"
        )

    ####################################################################
    # Orders
    ####################################################################

    def get_orders(self) -> Dict:
        """
        Returns today's orders.

        Endpoint:
            GET /order/retrieve-all
        """

        return self._get(
            "/order/retrieve-all"
        )

    ####################################################################
    # Trades
    ####################################################################

    def get_trades(self) -> Dict:
        """
        Returns executed trades.

        Endpoint:
            GET /order/trades/get-trades
        """

        return self._get(
            "/order/trades/get-trades"
        )

    ####################################################################
    # Single Order
    ####################################################################

    def get_order(
        self,
        order_id: str,
    ) -> Dict:
        """
        Returns a specific order.
        """

        return self._get(
            f"/order/details?order_id={order_id}"
        )

    ####################################################################
    # Brokerage
    ####################################################################

    def get_brokerage(
        self,
        payload: Dict,
    ) -> Dict:
        """
        Brokerage calculator.
        """

        return self._post(
            "/charges/brokerage",
            payload
        )
        ####################################################################
    # Market Quote
    ####################################################################

    def get_market_quote(
        self,
        instrument_keys: List[str],
    ) -> Dict:
        """
        Fetch latest market quote.

        Parameters
        ----------
        instrument_keys:
            List of Upstox instrument keys.

        Example
        -------
        [
            "NSE_EQ|INE002A01018",
            "NSE_EQ|INE009A01021"
        ]
        """

        return self._get(
            "/market-quote/quotes",
            params={
                "instrument_key": ",".join(
                    instrument_keys
                )
            },
        )

    ####################################################################
    # Full Market Quote
    ####################################################################

    def get_full_market_quote(
        self,
        instrument_keys: List[str],
    ) -> Dict:
        """
        Returns full market depth including OHLC,
        bid/ask and volume.
        """

        return self._get(
            "/market-quote/ltp",
            params={
                "instrument_key": ",".join(
                    instrument_keys
                )
            },
        )

    ####################################################################
    # Last Traded Price
    ####################################################################

    def get_ltp(
        self,
        instrument_keys: List[str],
    ) -> Dict:
        """
        Fetch LTP only.
        """

        return self._get(
            "/market-quote/ltp",
            params={
                "instrument_key": ",".join(
                    instrument_keys
                )
            },
        )

    ####################################################################
    # OHLC Quote
    ####################################################################

    def get_ohlc(
        self,
        instrument_keys: List[str],
    ) -> Dict:
        """
        Returns latest OHLC values.
        """

        return self._get(
            "/market-quote/ohlc",
            params={
                "instrument_key": ",".join(
                    instrument_keys
                )
            },
        )

    ####################################################################
    # Option Contracts
    ####################################################################

    def get_option_contracts(
        self,
        instrument_key: str,
    ) -> Dict:
        """
        Returns available option contracts.
        """

        return self._get(
            "/option/contract",
            params={
                "instrument_key": instrument_key
            },
        )

    ####################################################################
    # Option Chain
    ####################################################################

    def get_option_chain(
        self,
        instrument_key: str,
        expiry_date: str,
    ) -> Dict:
        """
        Fetch complete option chain.

        expiry_date format:
            YYYY-MM-DD
        """

        return self._get(
            "/option/chain",
            params={
                "instrument_key": instrument_key,
                "expiry_date": expiry_date,
            },
        )

    ####################################################################
    # Instruments
    ####################################################################

    def search_instruments(
        self,
        query: str,
    ) -> Dict:
        """
        Search instruments.
        """

        return self._get(
            "/search/instruments",
            params={
                "query": query,
            },
        )

    ####################################################################
    # Expired Instruments
    ####################################################################

    def search_expired_instruments(
        self,
        query: str,
    ) -> Dict:
        """
        Search expired contracts.
        """

        return self._get(
            "/expired-instruments/search",
            params={
                "query": query,
            },
        )
        ####################################################################
    # Historical Candles
    ####################################################################

    def get_historical_candles(
        self,
        instrument_key: str,
        interval: str,
        to_date: str,
        from_date: Optional[str] = None,
    ) -> Dict:
        """
        Historical candle data.

        interval examples:
            1minute
            30minute
            day
            week
            month

        Date format:
            YYYY-MM-DD
        """

        endpoint = (
            f"/historical-candle/"
            f"{instrument_key}/"
            f"{interval}/"
            f"{to_date}"
        )

        if from_date:

            endpoint += f"/{from_date}"

        return self._get(endpoint)

    ####################################################################
    # Intraday Candles
    ####################################################################

    def get_intraday_candles(
        self,
        instrument_key: str,
        interval: str = "1minute",
    ) -> Dict:
        """
        Returns today's intraday candles.
        """

        endpoint = (
            "/historical-candle/intraday/"
            f"{instrument_key}/"
            f"{interval}"
        )

        return self._get(endpoint)

    ####################################################################
    # Expired Historical Candles
    ####################################################################

    def get_expired_historical_candles(
        self,
        expired_instrument_key: str,
        interval: str,
        to_date: str,
        from_date: Optional[str] = None,
    ) -> Dict:
        """
        Historical candles for expired F&O contracts.
        """

        endpoint = (
            "/expired-instruments/"
            "historical-candle/"
            f"{expired_instrument_key}/"
            f"{interval}/"
            f"{to_date}"
        )

        if from_date:

            endpoint += f"/{from_date}"

        return self._get(endpoint)

    ####################################################################
    # Market Data Feed Authorization
    ####################################################################

    def get_market_data_feed_authorization(
        self,
    ) -> Dict:
        """
        Returns websocket authorization
        information for Market Data Feed.
        """

        return self._get(
            "/feed/market-data-feed/authorize"
        )

    ####################################################################
    # Portfolio Feed Authorization
    ####################################################################

    def get_portfolio_feed_authorization(
        self,
    ) -> Dict:
        """
        Returns websocket authorization
        for portfolio updates.
        """

        return self._get(
            "/feed/portfolio-stream-feed/authorize"
        )

    ####################################################################
    # Market Feed Redirect
    ####################################################################

    def get_market_feed(
        self,
    ):
        """
        Returns websocket redirect response.
        """

        return self._get(
            "/feed/market-data-feed"
        )

    ####################################################################
    # Portfolio Feed Redirect
    ####################################################################

    def get_portfolio_feed(
        self,
    ):
        """
        Returns portfolio websocket redirect.
        """

        return self._get(
            "/feed/portfolio-stream-feed"
        )

    ####################################################################
    # Health Check
    ####################################################################

    def health_check(self) -> bool:
        """
        Simple connectivity test.
        """

        try:

            self.get_profile()

            return True

        except Exception:

            return False
            ####################################################################
    # Instrument File
    ####################################################################

    def get_instruments(
        self,
        exchange: str = "NSE"
    ):
        """
        Download master instrument file.

        Supported examples:
            NSE
            BSE
            MCX
            NCD
            CDS
        """

        endpoint = f"/market/instruments/{exchange}"

        return self._get(endpoint)

    ####################################################################
    # Market Holidays
    ####################################################################

    def get_market_holidays(self):

        return self._get(
            "/market/holidays"
        )

    ####################################################################
    # Exchange Timings
    ####################################################################

    def get_exchange_timings(self):

        return self._get(
            "/market/timings"
        )

    ####################################################################
    # Ping
    ####################################################################

    def ping(self):

        try:

            self.get_profile()

            return True

        except Exception:

            return False

    ####################################################################
    # Diagnostics
    ####################################################################

    def diagnostics(self):

        return {

            "base_url": self.BASE_URL,

            "authenticated": (
                self.auth.is_authenticated()
            ),

            "token_available": bool(

                self.auth.access_token

            ),

            "ping": self.ping(),

        }

    ####################################################################
    # Version
    ####################################################################

    @property
    def version(self):

        return "1.0"

    ####################################################################
    # Logout
    ####################################################################

    def logout(self):

        self.auth.clear_token()

    ####################################################################
    # Refresh Access Token
    ####################################################################

    def refresh_token(self):

        return self.auth.refresh_access_token()

    ####################################################################
    # Generic Request
    ####################################################################

    def request(

        self,

        method: str,

        endpoint: str,

        **kwargs,

    ):

        method = method.upper()

        if method == "GET":

            return self._get(

                endpoint,

                params=kwargs.get(

                    "params"

                ),

            )

        if method == "POST":

            return self._post(

                endpoint,

                json=kwargs.get(

                    "json"

                ),

            )

        if method == "PUT":

            return self.http.put(

                endpoint,

                headers=self._headers(),

                json=kwargs.get(

                    "json"

                ),

            )

        if method == "DELETE":

            return self.http.delete(

                endpoint,

                headers=self._headers(),

                json=kwargs.get(

                    "json"

                ),

            )

        raise ValueError(

            f"Unsupported HTTP method: {method}"

        )

    ####################################################################
    # Retry Wrapper
    ####################################################################

    def safe_request(

        self,

        method,

        endpoint,

        retries=3,

        **kwargs,

    ):

        last_error = None

        for _ in range(retries):

            try:

                return self.request(

                    method,

                    endpoint,

                    **kwargs,

                )

            except Exception as exc:

                last_error = exc

        raise last_error

    ####################################################################
    # Context Manager
    ####################################################################

    def __enter__(self):

        return self

    def __exit__(

        self,

        exc_type,

        exc,

        tb,

    ):

        return False

    ####################################################################
    # String Representation
    ####################################################################

    def __repr__(self):

        return (

            f"UpstoxAPI("

            f"authenticated="

            f"{self.auth.is_authenticated()}"

            f")"

        )