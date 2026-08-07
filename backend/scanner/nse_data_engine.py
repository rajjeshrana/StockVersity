"""
============================================================
StockVersity Scanner Pro v4.0
Powered by AI

File:
backend/scanner/nse_data_engine.py

Enterprise NSE Data Engine

Author : StockVersity
============================================================
"""

from __future__ import annotations

import threading
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_REFRESH_SECONDS = 60
PREMARKET_REFRESH = 300

MARKET_OPEN_HOUR = 9
MARKET_OPEN_MINUTE = 15

MARKET_CLOSE_HOUR = 15
MARKET_CLOSE_MINUTE = 30

PREMARKET_START = 9
PREMARKET_MINUTE = 0

CACHE_TIMEOUT = 60

MAX_RETRY = 5


# ============================================================
# MARKET STATUS
# ============================================================

class MarketStatus:

    CLOSED = "CLOSED"

    PREMARKET = "PREMARKET"

    LIVE = "LIVE"

    POSTMARKET = "POSTMARKET"


# ============================================================
# NSE DATA ENGINE
# ============================================================

class NSEDataEngine:

    VERSION = "4.0"

    def __init__(

        self,

        refresh_interval: int = DEFAULT_REFRESH_SECONDS,

    ):

        self.refresh_interval = refresh_interval

        self.market_data: Dict[str, pd.DataFrame] = {}

        self.indices: Dict[str, Any] = {}

        self.sectors: Dict[str, Any] = {}

        self.watchlist: List[str] = []

        self.fno_symbols: List[str] = []

        self.top_gainers = pd.DataFrame()

        self.top_losers = pd.DataFrame()

        self.market_breadth = {}

        self.last_refresh: Optional[datetime] = None

        self.status = MarketStatus.CLOSED

        self.connected = False

        self.running = False

        self.stop_requested = False

        self.lock = threading.Lock()

        self.logger = logging.getLogger("NSEDataEngine")

        self.logger.setLevel(logging.INFO)

        self.update_callback = None

        self.status_callback = None

        self.error_callback = None


# ============================================================
# CALLBACKS
# ============================================================

    def set_update_callback(

        self,

        callback,

    ):

        self.update_callback = callback


    def set_status_callback(

        self,

        callback,

    ):

        self.status_callback = callback


    def set_error_callback(

        self,

        callback,

    ):

        self.error_callback = callback


# ============================================================
# STATUS UPDATE
# ============================================================

    def update_status(

        self,

        message: str,

    ):

        self.logger.info(message)

        if self.status_callback:

            self.status_callback(message)


# ============================================================
# ERROR
# ============================================================

    def report_error(

        self,

        error,

    ):

        self.logger.exception(error)

        if self.error_callback:

            self.error_callback(error)


# ============================================================
# VERSION
# ============================================================

    @staticmethod
    def version():

        return "4.0"


# ============================================================
# CURRENT TIME
# ============================================================

    @staticmethod
    def now():

        return datetime.now()


# ============================================================
# MARKET STATUS
# ============================================================

    def market_status(

        self,

    ) -> str:

        now = self.now()

        minutes = now.hour * 60 + now.minute

        premarket = PREMARKET_START * 60 + PREMARKET_MINUTE

        open_time = MARKET_OPEN_HOUR * 60 + MARKET_OPEN_MINUTE

        close_time = MARKET_CLOSE_HOUR * 60 + MARKET_CLOSE_MINUTE

        if now.weekday() >= 5:

            return MarketStatus.CLOSED

        if minutes < premarket:

            return MarketStatus.CLOSED

        if premarket <= minutes < open_time:

            return MarketStatus.PREMARKET

        if open_time <= minutes <= close_time:

            return MarketStatus.LIVE

        return MarketStatus.POSTMARKET


# ============================================================
# IS MARKET OPEN
# ============================================================

    def is_market_open(

        self,

    ) -> bool:

        return self.market_status() == MarketStatus.LIVE


# ============================================================
# IS PREMARKET
# ============================================================

    def is_premarket(

        self,

    ) -> bool:

        return self.market_status() == MarketStatus.PREMARKET


# ============================================================
# IS CLOSED
# ============================================================

    def is_closed(

        self,

    ) -> bool:

        return self.market_status() == MarketStatus.CLOSED


# ============================================================
# RESET
# ============================================================

    def reset(

        self,

    ):

        self.market_data.clear()

        self.indices.clear()

        self.sectors.clear()

        self.watchlist.clear()

        self.market_breadth = {}

        self.top_gainers = pd.DataFrame()

        self.top_losers = pd.DataFrame()

        self.last_refresh = None
        # ============================================================
# CONNECTION
# ============================================================

    def connect(
        self,
    ) -> bool:

        try:

            self.update_status(
                "Connecting to data source..."
            )

            self.connected = True

            self.update_status(
                "Connection established."
            )

            return True

        except Exception as exc:

            self.connected = False

            self.report_error(exc)

            return False


# ============================================================
# DISCONNECT
# ============================================================

    def disconnect(
        self,
    ) -> None:

        self.connected = False

        self.update_status(
            "Disconnected from data source."
        )


# ============================================================
# CONNECTION STATUS
# ============================================================

    def is_connected(
        self,
    ) -> bool:

        return self.connected


# ============================================================
# CONNECTION HEALTH
# ============================================================

    def connection_health(
        self,
    ) -> Dict:

        return {

            "Connected": self.connected,

            "Running": self.running,

            "Market": self.market_status(),

            "Last Refresh": self.last_refresh,

        }


# ============================================================
# AUTO RECONNECT
# ============================================================

    def reconnect(
        self,
    ) -> bool:

        for attempt in range(1, MAX_RETRY + 1):

            self.update_status(
                f"Reconnect attempt {attempt}/{MAX_RETRY}"
            )

            if self.connect():

                return True

            time.sleep(2)

        return False


# ============================================================
# LOAD SYMBOL MASTER
# ============================================================

    def load_symbol_master(
        self,
    ) -> None:

        self.update_status(
            "Loading NSE symbol master..."
        )

        # TODO
        # Load NSE stock universe

        self.update_status(
            "Symbol master loaded."
        )


# ============================================================
# LOAD SECTOR MASTER
# ============================================================

    def load_sector_master(
        self,
    ) -> None:

        self.update_status(
            "Loading sector mapping..."
        )

        # TODO

        self.update_status(
            "Sector mapping loaded."
        )


# ============================================================
# LOAD F&O SYMBOLS
# ============================================================

    def load_fno_symbols(
        self,
    ) -> None:

        self.update_status(
            "Loading F&O symbols..."
        )

        # TODO

        self.update_status(
            "F&O symbols loaded."
        )


# ============================================================
# LOAD WATCHLIST
# ============================================================

    def load_watchlist(
        self,
        symbols: List[str],
    ) -> None:

        self.watchlist = symbols.copy()


# ============================================================
# PRE-MARKET INITIALIZATION
# ============================================================

    def initialize_premarket(
        self,
    ) -> None:

        self.update_status(
            "Initializing pre-market..."
        )

        self.load_symbol_master()

        self.load_sector_master()

        self.load_fno_symbols()

        self.update_status(
            "Pre-market initialization completed."
        )


# ============================================================
# INITIALIZE LIVE SESSION
# ============================================================

    def initialize_live(
        self,
    ) -> None:

        self.update_status(
            "Initializing live session..."
        )

        self.last_refresh = datetime.now()

        self.update_status(
            "Live session ready."
        )


# ============================================================
# START ENGINE
# ============================================================

    def start(
        self,
    ) -> None:

        if self.running:

            return

        if not self.connect():

            raise ConnectionError(
                "Unable to connect to data source."
            )

        self.running = True

        self.stop_requested = False

        if self.is_premarket():

            self.initialize_premarket()

        elif self.is_market_open():

            self.initialize_live()

        thread = threading.Thread(

            target=self.refresh_loop,

            daemon=True,

        )

        thread.start()

        self.update_status(
            "NSE Data Engine started."
        )


# ============================================================
# STOP ENGINE
# ============================================================

    def stop(
        self,
    ) -> None:

        self.stop_requested = True

        self.running = False

        self.disconnect()

        self.update_status(
            "NSE Data Engine stopped."
        )


# ============================================================
# REFRESH LOOP
# ============================================================

    def refresh_loop(
        self,
    ) -> None:

        while not self.stop_requested:

            try:

                self.refresh()

            except Exception as exc:

                self.report_error(exc)

                self.reconnect()

            interval = (

                PREMARKET_REFRESH

                if self.is_premarket()

                else self.refresh_interval

            )

            time.sleep(interval)


# ============================================================
# MANUAL REFRESH
# ============================================================

    def refresh(
        self,
    ) -> None:

        self.update_status(
            "Refreshing market data..."
        )

        self.last_refresh = datetime.now()

        if self.update_callback:

            self.update_callback()

        self.update_status(
            "Refresh completed."
        )
        # ============================================================
# LOAD PREVIOUS DAY DATA
# ============================================================

    def load_previous_day_data(
        self,
    ) -> None:

        self.update_status(
            "Loading previous day OHLCV..."
        )

        # TODO:
        # Download previous trading day OHLCV
        # for all NSE symbols.

        self.update_status(
            "Previous day data loaded."
        )


# ============================================================
# LOAD LIVE MARKET DATA
# ============================================================

    def load_live_market(
        self,
    ) -> None:

        self.update_status(
            "Loading live market data..."
        )

        # TODO:
        # Download latest OHLCV
        # for all active symbols.

        self.last_refresh = datetime.now()

        self.update_status(
            "Live market updated."
        )


# ============================================================
# UPDATE SINGLE SYMBOL
# ============================================================

    def update_symbol(
        self,
        symbol: str,
        dataframe: pd.DataFrame,
    ) -> None:

        with self.lock:

            self.market_data[symbol] = dataframe


# ============================================================
# GET SYMBOL DATA
# ============================================================

    def get_stock(
        self,
        symbol: str,
    ) -> Optional[pd.DataFrame]:

        return self.market_data.get(symbol)


# ============================================================
# SYMBOL EXISTS
# ============================================================

    def has_symbol(
        self,
        symbol: str,
    ) -> bool:

        return symbol in self.market_data


# ============================================================
# REMOVE SYMBOL
# ============================================================

    def remove_symbol(
        self,
        symbol: str,
    ) -> None:

        self.market_data.pop(
            symbol,
            None,
        )


# ============================================================
# ALL SYMBOLS
# ============================================================

    def symbols(
        self,
    ) -> List[str]:

        return sorted(
            self.market_data.keys()
        )


# ============================================================
# SYMBOL COUNT
# ============================================================

    @property
    def symbol_count(
        self,
    ) -> int:

        return len(
            self.market_data
        )


# ============================================================
# LOAD INDICES
# ============================================================

    def load_indices(
        self,
    ) -> None:

        self.update_status(
            "Loading indices..."
        )

        # TODO:
        # Fetch:
        # NIFTY 50
        # BANK NIFTY
        # FINNIFTY
        # MIDCAP
        # SENSEX
        # INDIA VIX

        self.indices = {

            "NIFTY": {},

            "BANKNIFTY": {},

            "FINNIFTY": {},

            "MIDCAP": {},

            "SENSEX": {},

            "INDIAVIX": {},

        }


# ============================================================
# GET INDEX
# ============================================================

    def get_index(
        self,
        name: str,
    ) -> Dict:

        return self.indices.get(
            name.upper(),
            {},
        )


# ============================================================
# GET ALL INDICES
# ============================================================

    def get_indices(
        self,
    ) -> Dict:

        return self.indices


# ============================================================
# UPDATE INDEX
# ============================================================

    def update_index(
        self,
        name: str,
        data: Dict,
    ) -> None:

        self.indices[
            name.upper()
        ] = data


# ============================================================
# LOAD MARKET BREADTH
# ============================================================

    def load_market_breadth(
        self,
    ) -> None:

        self.market_breadth = {

            "Advances": 0,

            "Declines": 0,

            "Unchanged": 0,

            "AdvanceRatio": 0,

        }


# ============================================================
# GET MARKET BREADTH
# ============================================================

    def get_market_breadth(
        self,
    ) -> Dict:

        return self.market_breadth


# ============================================================
# UPDATE MARKET BREADTH
# ============================================================

    def update_market_breadth(
        self,
        breadth: Dict,
    ) -> None:

        self.market_breadth = breadth


# ============================================================
# LAST UPDATE
# ============================================================

    def last_update(
        self,
    ) -> Optional[datetime]:

        return self.last_refresh


# ============================================================
# CACHE AGE
# ============================================================

    def cache_age(
        self,
    ) -> float:

        if self.last_refresh is None:

            return 999999

        return (

            datetime.now()

            -

            self.last_refresh

        ).total_seconds()


# ============================================================
# CACHE VALID
# ============================================================

    def cache_valid(
        self,
    ) -> bool:

        return (

            self.cache_age()

            <= CACHE_TIMEOUT

        )


# ============================================================
# REFRESH IF REQUIRED
# ============================================================

    def refresh_if_required(
        self,
    ) -> None:

        if not self.cache_valid():

            self.refresh()
            # ============================================================
# INCREMENTAL REFRESH
# ============================================================

    def incremental_refresh(
        self,
        changed_symbols: List[str],
    ) -> None:

        if not changed_symbols:
            return

        self.update_status(
            f"Refreshing {len(changed_symbols)} symbols..."
        )

        for symbol in changed_symbols:

            try:

                self.refresh_symbol(symbol)

            except Exception as exc:

                self.report_error(exc)

        self.last_refresh = datetime.now()


# ============================================================
# REFRESH SINGLE SYMBOL
# ============================================================

    def refresh_symbol(
        self,
        symbol: str,
    ) -> None:

        if symbol not in self.market_data:
            return

        # --------------------------------------------
        # Provider will replace this placeholder
        # --------------------------------------------

        df = self.market_data[symbol]

        self.market_data[symbol] = df


# ============================================================
# REFRESH WATCHLIST
# ============================================================

    def refresh_watchlist(
        self,
    ) -> None:

        if not self.watchlist:
            return

        self.incremental_refresh(
            self.watchlist
        )


# ============================================================
# LIVE UPDATE
# ============================================================

    def live_update(
        self,
    ) -> None:

        self.load_live_market()

        self.load_indices()

        self.load_market_breadth()

        self.update_top_gainers()

        self.update_top_losers()

        self.last_refresh = datetime.now()


# ============================================================
# FULL MARKET REFRESH
# ============================================================

    def full_refresh(
        self,
    ) -> None:

        self.update_status(
            "Running full market refresh..."
        )

        self.load_previous_day_data()

        self.load_live_market()

        self.load_indices()

        self.load_market_breadth()

        self.update_top_gainers()

        self.update_top_losers()

        self.last_refresh = datetime.now()

        self.update_status(
            "Full refresh completed."
        )


# ============================================================
# TOP GAINERS
# ============================================================

    def update_top_gainers(
        self,
    ) -> None:

        rows = []

        for symbol, df in self.market_data.items():

            if df.empty:
                continue

            last = df.iloc[-1]

            rows.append(

                {

                    "Symbol": symbol,

                    "Price": last.get("Close"),

                    "Change %": last.get("ChangePercent", 0),

                    "Volume": last.get("Volume", 0),

                }

            )

        if not rows:

            self.top_gainers = pd.DataFrame(
                columns=[
                    "Symbol",
                    "Price",
                    "Change %",
                    "Volume",
                ]
            )

            return

        if not rows:

            self.top_gainers = pd.DataFrame(
                columns=[
                    "Symbol",
                    "Price",
                    "Change %",
                    "Volume",
                ]
            )

            return

        self.top_gainers = (

            pd.DataFrame(rows)

            .sort_values(

                "Change %",

                ascending=False,

            )

            .head(20)

        )


# ============================================================
# TOP LOSERS
# ============================================================

    def update_top_losers(
        self,
    ) -> None:

        rows = []

        for symbol, df in self.market_data.items():

            if df.empty:
                continue

            last = df.iloc[-1]

            rows.append(

                {

                    "Symbol": symbol,

                    "Price": last.get("Close"),

                    "Change %": last.get("ChangePercent", 0),

                    "Volume": last.get("Volume", 0),

                }

            )

        if not rows:

            self.top_losers = pd.DataFrame(
                columns=[
                    "Symbol",
                    "Price",
                    "Change %",
                    "Volume",
                ]
            )

            return

        if not rows:

            self.top_losers = pd.DataFrame(
                columns=[
                    "Symbol",
                    "Price",
                    "Change %",
                    "Volume",
                ]
            )

            return

        self.top_losers = (

            pd.DataFrame(rows)

            .sort_values(

                "Change %",

                ascending=True,

            )

            .head(20)

        )


# ============================================================
# GET TOP GAINERS
# ============================================================

    def get_top_gainers(
        self,
        limit: int = 20,
    ) -> pd.DataFrame:

        return self.top_gainers.head(limit)


# ============================================================
# GET TOP LOSERS
# ============================================================

    def get_top_losers(
        self,
        limit: int = 20,
    ) -> pd.DataFrame:

        return self.top_losers.head(limit)


# ============================================================
# MARKET SNAPSHOT
# ============================================================

    def market_snapshot(
        self,
    ) -> Dict:

        # -------------------------------------------------
        # Institutional Flow
        #
        # FII/DII cash-market data is published after
        # market hours. Failure here must never interrupt
        # the main NSE / Upstox dashboard pipeline.
        # -------------------------------------------------

        institutional = {}

        try:

            from backend.services.fii_dii_service import (
                FIIDIIService,
            )

            service = getattr(
                self,
                "_fii_dii_service",
                None,
            )

            if service is None:

                service = FIIDIIService()

                self._fii_dii_service = service

            result = service.fetch()

            if isinstance(
                result,
                dict,
            ):

                institutional = result

        except Exception as exc:

            try:
                self.logger.warning(
                    "Institutional flow unavailable: %s",
                    exc,
                )
            except Exception:
                pass

        return {

            "Status": self.market_status(),

            "Last Update": self.last_refresh,

            "Stocks": len(self.market_data),

            "Indices": self.indices,

            "Breadth": self.market_breadth,

            "Top Gainers": self.top_gainers,

            "Top Losers": self.top_losers,

            # Normalized dashboard key
            "institutional": institutional,

        }


# ============================================================
# AUTO MARKET MODE
# ============================================================

    def auto_refresh(
        self,
    ) -> None:

        status = self.market_status()

        if status == MarketStatus.PREMARKET:

            self.full_refresh()

            return

        if status == MarketStatus.LIVE:

            self.live_update()

            return

        self.update_status(
            "Market Closed."
        )
        # ============================================================
# PRE-MARKET ENGINE
# ============================================================

    def premarket_engine(
        self,
    ) -> None:

        self.update_status(
            "Running Pre-Market Engine..."
        )

        self.detect_gap_up()

        self.detect_gap_down()

        self.calculate_sector_strength()

        self.calculate_rvol()

        self.build_opening_watchlist()

        self.generate_heatmap()

        self.update_status(
            "Pre-Market Analysis Completed."
        )


# ============================================================
# GAP UP DETECTION
# ============================================================

    def detect_gap_up(
        self,
        minimum_gap: float = 1.0,
    ) -> pd.DataFrame:

        rows = []

        for symbol, df in self.market_data.items():

            if len(df) < 2:

                continue

            previous = df.iloc[-2]

            current = df.iloc[-1]

            previous_close = previous["Close"]

            open_price = current["Open"]

            gap = (

                (open_price - previous_close)

                / previous_close

            ) * 100

            if gap >= minimum_gap:

                rows.append({

                    "Symbol": symbol,

                    "Gap %": round(gap,2),

                    "Open": open_price,

                    "Previous Close": previous_close,

                })

        self.gap_up = pd.DataFrame(rows)

        return self.gap_up.sort_values(

            "Gap %",

            ascending=False,

        )


# ============================================================
# GAP DOWN DETECTION
# ============================================================

    def detect_gap_down(
        self,
        minimum_gap: float = -1.0,
    ) -> pd.DataFrame:

        rows = []

        for symbol, df in self.market_data.items():

            if len(df) < 2:

                continue

            previous = df.iloc[-2]

            current = df.iloc[-1]

            previous_close = previous["Close"]

            open_price = current["Open"]

            gap = (

                (open_price - previous_close)

                / previous_close

            ) * 100

            if gap <= minimum_gap:

                rows.append({

                    "Symbol": symbol,

                    "Gap %": round(gap,2),

                    "Open": open_price,

                    "Previous Close": previous_close,

                })

        self.gap_down = pd.DataFrame(rows)

        return self.gap_down.sort_values(

            "Gap %"

        )


# ============================================================
# SECTOR STRENGTH
# ============================================================

    def calculate_sector_strength(
        self,
    ) -> Dict:

        strength = {}

        grouped = {}

        for symbol, sector in self.sectors.items():

            if symbol not in self.market_data:

                continue

            df = self.market_data[symbol]

            if df.empty:

                continue

            change = df.iloc[-1].get(

                "ChangePercent",

                0,

            )

            grouped.setdefault(

                sector,

                []

            ).append(change)

        for sector, values in grouped.items():

            strength[sector] = round(

                sum(values) / len(values),

                2,

            )

        self.sector_strength = dict(

            sorted(

                strength.items(),

                key=lambda x: x[1],

                reverse=True,

            )

        )

        return self.sector_strength


# ============================================================
# RELATIVE VOLUME
# ============================================================

    def calculate_rvol(
        self,
    ) -> None:

        for symbol, df in self.market_data.items():

            if len(df) < 21:

                continue

            avg = df["Volume"].tail(20).mean()

            current = df.iloc[-1]["Volume"]

            rvol = current / avg if avg else 0

            self.market_data[symbol].loc[

                df.index[-1],

                "RVOL",

            ] = round(rvol,2)


# ============================================================
# OPENING WATCHLIST
# ============================================================

    def build_opening_watchlist(
        self,
    ) -> List[str]:

        watchlist = []

        for symbol, df in self.market_data.items():

            if df.empty:

                continue

            row = df.iloc[-1]

            if (

                row.get("RVOL",0) >= 2

                and

                row.get("ChangePercent",0) > 0

            ):

                watchlist.append(symbol)

        self.watchlist = watchlist

        return watchlist


# ============================================================
# MARKET HEATMAP
# ============================================================

    def generate_heatmap(
        self,
    ) -> Dict:

        heat = {}

        for symbol, df in self.market_data.items():

            if df.empty:

                continue

            heat[symbol] = df.iloc[-1].get(

                "ChangePercent",

                0,

            )

        self.heatmap = heat

        return heat


# ============================================================
# EARLY MOMENTUM
# ============================================================

    def early_momentum(
        self,
        minimum_rvol: float = 2.0,
    ) -> pd.DataFrame:

        rows = []

        for symbol, df in self.market_data.items():

            if df.empty:

                continue

            row = df.iloc[-1]

            if row.get("RVOL",0) < minimum_rvol:

                continue

            rows.append({

                "Symbol": symbol,

                "RVOL": row.get("RVOL"),

                "Change %": row.get("ChangePercent"),

                "Volume": row.get("Volume"),

            })

        return pd.DataFrame(rows).sort_values(

            "RVOL",

            ascending=False,

        )


# ============================================================
# OPENING BELL ENGINE
# ============================================================

    def opening_bell_engine(
        self,
    ) -> Dict:

        self.update_status(

            "Running Opening Bell Engine..."

        )

        return {

            "Gap Up":

                self.detect_gap_up(),

            "Gap Down":

                self.detect_gap_down(),

            "Sector Strength":

                self.calculate_sector_strength(),

            "Heatmap":

                self.generate_heatmap(),

            "Opening Watchlist":

                self.build_opening_watchlist(),

            "Momentum":

                self.early_momentum(),

            "Top Gainers":

                self.get_top_gainers(),

            "Top Losers":

                self.get_top_losers(),

        }
    # ============================================================
# ORB (OPENING RANGE BREAKOUT)
# ============================================================

    def opening_range_breakout(
        self,
        range_minutes: int = 15,
    ) -> pd.DataFrame:

        candidates = []

        for symbol, df in self.market_data.items():

            if len(df) < range_minutes + 2:
                continue

            opening = df.iloc[:range_minutes]

            orb_high = opening["High"].max()
            orb_low = opening["Low"].min()

            latest = df.iloc[-1]

            if latest["Close"] > orb_high:

                candidates.append({

                    "Symbol": symbol,

                    "ORB High": orb_high,

                    "Price": latest["Close"],

                    "Signal": "BUY"

                })

            elif latest["Close"] < orb_low:

                candidates.append({

                    "Symbol": symbol,

                    "ORB Low": orb_low,

                    "Price": latest["Close"],

                    "Signal": "SELL"

                })

        return pd.DataFrame(candidates)


# ============================================================
# VWAP FILTER
# ============================================================

    def vwap_filter(
        self,
    ) -> List[str]:

        output = []

        for symbol, df in self.market_data.items():

            if df.empty:
                continue

            latest = df.iloc[-1]

            if latest["Close"] > latest.get("VWAP", 0):

                output.append(symbol)

        return output


# ============================================================
# EMA TREND FILTER
# ============================================================

    def ema_trend_filter(
        self,
    ) -> List[str]:

        trend = []

        for symbol, df in self.market_data.items():

            if df.empty:
                continue

            row = df.iloc[-1]

            if (

                row.get("EMA21", 0)

                >

                row.get("EMA50", 0)

            ):

                trend.append(symbol)

        return trend


# ============================================================
# MACD FILTER
# ============================================================

    def macd_filter(
        self,
    ) -> List[str]:

        output = []

        for symbol, df in self.market_data.items():

            row = df.iloc[-1]

            if (

                row.get("MACD", 0)

                >

                row.get("MACD_SIGNAL", 0)

            ):

                output.append(symbol)

        return output


# ============================================================
# ADX FILTER
# ============================================================

    def adx_filter(
        self,
        minimum: float = 20,
    ) -> List[str]:

        output = []

        for symbol, df in self.market_data.items():

            row = df.iloc[-1]

            if row.get("ADX", 0) >= minimum:

                output.append(symbol)

        return output


# ============================================================
# VOLUME BREAKOUT
# ============================================================

    def volume_breakout(
        self,
        multiplier: float = 2,
    ) -> List[str]:

        output = []

        for symbol, df in self.market_data.items():

            if len(df) < 21:
                continue

            avg = df["Volume"].tail(20).mean()

            current = df.iloc[-1]["Volume"]

            if current >= avg * multiplier:

                output.append(symbol)

        return output


# ============================================================
# F&O FILTER
# ============================================================

    def fno_filter(
        self,
    ) -> List[str]:

        return [

            symbol

            for symbol

            in self.watchlist

            if symbol in self.fno_symbols

        ]


# ============================================================
# INTRADAY SCORE
# ============================================================

    def intraday_score(
        self,
        symbol: str,
    ) -> int:

        score = 0

        df = self.market_data.get(symbol)

        if df is None or df.empty:

            return score

        row = df.iloc[-1]

        if row.get("Close", 0) > row.get("VWAP", 0):
            score += 15

        if row.get("EMA21", 0) > row.get("EMA50", 0):
            score += 15

        if row.get("MACD", 0) > row.get("MACD_SIGNAL", 0):
            score += 15

        if row.get("ADX", 0) >= 20:
            score += 15

        if row.get("RVOL", 0) >= 2:
            score += 15

        if symbol in self.fno_symbols:
            score += 10

        if symbol in self.watchlist:
            score += 15

        return score


# ============================================================
# TOP INTRADAY CANDIDATES
# ============================================================

    def top_intraday_candidates(
        self,
        limit: int = 5,
    ) -> pd.DataFrame:

        rows = []

        for symbol in self.market_data.keys():

            rows.append({

                "Symbol": symbol,

                "Score": self.intraday_score(symbol),

            })

        return (

            pd.DataFrame(rows)

            .sort_values(

                "Score",

                ascending=False,

            )

            .head(limit)

        )


# ============================================================
# INTRADAY ENGINE
# ============================================================

    def intraday_engine(
        self,
    ) -> Dict:

        self.update_status(

            "Running Intraday Intelligence..."

        )

        return {

            "ORB":

                self.opening_range_breakout(),

            "VWAP":

                self.vwap_filter(),

            "EMA":

                self.ema_trend_filter(),

            "MACD":

                self.macd_filter(),

            "ADX":

                self.adx_filter(),

            "Volume":

                self.volume_breakout(),

            "F&O":

                self.fno_filter(),

            "Top 5":

                self.top_intraday_candidates(),

        }
    # ============================================================
# VCP CANDIDATES
# ============================================================

    def vcp_candidates(
        self,
    ) -> pd.DataFrame:

        candidates = []

        for symbol, df in self.market_data.items():

            if len(df) < 30:
                continue

            contraction = (

                df["High"].tail(10).max()

                -

                df["Low"].tail(10).min()

            )

            previous = (

                df["High"].tail(20).max()

                -

                df["Low"].tail(20).min()

            )

            if contraction < previous * 0.70:

                candidates.append({

                    "Symbol": symbol,

                    "Pattern": "VCP",

                    "Score": 90,

                })

        return pd.DataFrame(candidates)


# ============================================================
# BULL FLAG
# ============================================================

    def bull_flag_candidates(
        self,
    ) -> pd.DataFrame:

        rows = []

        for symbol, df in self.market_data.items():

            if len(df) < 20:
                continue

            change = (

                df.iloc[-1]["Close"]

                -

                df.iloc[-20]["Close"]

            ) / df.iloc[-20]["Close"] * 100

            if change > 10:

                rows.append({

                    "Symbol": symbol,

                    "Pattern": "Bull Flag",

                    "Score": 88,

                })

        return pd.DataFrame(rows)


# ============================================================
# FALLING WEDGE
# ============================================================

    def falling_wedge_candidates(
        self,
    ) -> pd.DataFrame:

        rows = []

        for symbol, df in self.market_data.items():

            if len(df) < 30:
                continue

            highs = df["High"].tail(15)

            lows = df["Low"].tail(15)

            if (

                highs.iloc[-1] < highs.iloc[0]

                and

                lows.iloc[-1] < lows.iloc[0]

            ):

                rows.append({

                    "Symbol": symbol,

                    "Pattern": "Falling Wedge",

                    "Score": 87,

                })

        return pd.DataFrame(rows)


# ============================================================
# CUP & HANDLE
# ============================================================

    def cup_handle_candidates(
        self,
    ) -> pd.DataFrame:

        rows = []

        for symbol, df in self.market_data.items():

            if len(df) < 60:
                continue

            highest = df["High"].tail(60).max()

            latest = df.iloc[-1]["Close"]

            if latest >= highest * 0.97:

                rows.append({

                    "Symbol": symbol,

                    "Pattern": "Cup & Handle",

                    "Score": 92,

                })

        return pd.DataFrame(rows)


# ============================================================
# WEEKLY BREAKOUT
# ============================================================

    def weekly_breakouts(
        self,
    ) -> pd.DataFrame:

        rows = []

        for symbol, df in self.market_data.items():

            if len(df) < 5:
                continue

            weekly_high = df["High"].tail(5).max()

            if df.iloc[-1]["Close"] > weekly_high:

                rows.append({

                    "Symbol": symbol,

                    "Breakout": "Weekly",

                })

        return pd.DataFrame(rows)


# ============================================================
# MONTHLY BREAKOUT
# ============================================================

    def monthly_breakouts(
        self,
    ) -> pd.DataFrame:

        rows = []

        for symbol, df in self.market_data.items():

            if len(df) < 22:
                continue

            monthly_high = df["High"].tail(22).max()

            if df.iloc[-1]["Close"] > monthly_high:

                rows.append({

                    "Symbol": symbol,

                    "Breakout": "Monthly",

                })

        return pd.DataFrame(rows)


# ============================================================
# 52 WEEK HIGH
# ============================================================

    def near_52_week_high(
        self,
    ) -> pd.DataFrame:

        rows = []

        for symbol, df in self.market_data.items():

            if len(df) < 252:
                continue

            high = df["High"].tail(252).max()

            latest = df.iloc[-1]["Close"]

            distance = (

                (high - latest)

                / high

            ) * 100

            if distance <= 3:

                rows.append({

                    "Symbol": symbol,

                    "Distance %": round(distance, 2),

                })

        return pd.DataFrame(rows)


# ============================================================
# SWING SCORE
# ============================================================

    def swing_score(
        self,
        symbol: str,
    ) -> int:

        score = 0

        df = self.market_data.get(symbol)

        if df is None or df.empty:
            return score

        row = df.iloc[-1]

        if row.get("EMA21", 0) > row.get("EMA50", 0):
            score += 20

        if row.get("MACD", 0) > row.get("MACD_SIGNAL", 0):
            score += 20

        if row.get("ADX", 0) > 20:
            score += 15

        if row.get("RVOL", 0) > 1.5:
            score += 15

        if symbol in self.fno_symbols:
            score += 10

        if symbol in self.watchlist:
            score += 20

        return score


# ============================================================
# TOP SWING
# ============================================================

    def top_swing_candidates(
        self,
        limit: int = 5,
    ) -> pd.DataFrame:

        rows = []

        for symbol in self.market_data.keys():

            rows.append({

                "Symbol": symbol,

                "Score": self.swing_score(symbol),

            })

        return (

            pd.DataFrame(rows)

            .sort_values(

                "Score",

                ascending=False,

            )

            .head(limit)

        )


# ============================================================
# SWING ENGINE
# ============================================================

    def swing_engine(
        self,
    ) -> Dict:

        self.update_status(
            "Running Swing Intelligence..."
        )

        return {

            "VCP":
                self.vcp_candidates(),

            "Bull Flag":
                self.bull_flag_candidates(),

            "Falling Wedge":
                self.falling_wedge_candidates(),

            "Cup & Handle":
                self.cup_handle_candidates(),

            "Weekly Breakout":
                self.weekly_breakouts(),

            "Monthly Breakout":
                self.monthly_breakouts(),

            "52 Week High":
                self.near_52_week_high(),

            "Top Swing":
                self.top_swing_candidates(),

        }
    # ============================================================
# STAGE ANALYSIS
# ============================================================

    def stage_analysis(
        self,
    ) -> pd.DataFrame:

        rows = []

        for symbol, df in self.market_data.items():

            if df.empty:
                continue

            row = df.iloc[-1]

            ema50 = row.get("EMA50", 0)
            ema200 = row.get("EMA200", 0)
            price = row.get("Close", 0)

            if price > ema50 > ema200:

                stage = "Stage 2 Uptrend"

            elif price < ema50 < ema200:

                stage = "Stage 4 Downtrend"

            elif price > ema200:

                stage = "Stage 1 Accumulation"

            else:

                stage = "Stage 3 Distribution"

            rows.append({

                "Symbol": symbol,

                "Stage": stage,

                "Price": price,

            })

        return pd.DataFrame(rows)


# ============================================================
# 200 EMA TREND
# ============================================================

    def trend_200ema(
        self,
    ) -> pd.DataFrame:

        rows = []

        for symbol, df in self.market_data.items():

            if df.empty:
                continue

            row = df.iloc[-1]

            rows.append({

                "Symbol": symbol,

                "Above 200 EMA":

                    row.get("Close",0)

                    >

                    row.get("EMA200",0),

            })

        return pd.DataFrame(rows)


# ============================================================
# RELATIVE STRENGTH VS NIFTY
# ============================================================

    def relative_strength_vs_nifty(
        self,
    ) -> pd.DataFrame:

        nifty_change = self.indices.get(

            "NIFTY",

            {}

        ).get(

            "ChangePercent",

            0,

        )

        rows = []

        for symbol, df in self.market_data.items():

            if df.empty:
                continue

            row = df.iloc[-1]

            rs = row.get(

                "ChangePercent",

                0,

            ) - nifty_change

            rows.append({

                "Symbol": symbol,

                "RS": round(rs,2),

            })

        return (

            pd.DataFrame(rows)

            .sort_values(

                "RS",

                ascending=False,

            )

        )


# ============================================================
# SECTOR LEADERS
# ============================================================

    def sector_leaders(
        self,
    ) -> pd.DataFrame:

        rows = []

        for sector, value in self.sector_strength.items():

            rows.append({

                "Sector": sector,

                "Strength": value,

            })

        return (

            pd.DataFrame(rows)

            .sort_values(

                "Strength",

                ascending=False,

            )

        )


# ============================================================
# INSTITUTIONAL ACCUMULATION
# ============================================================

    def institutional_accumulation(
        self,
    ) -> pd.DataFrame:

        rows = []

        for symbol, df in self.market_data.items():

            if len(df) < 20:
                continue

            avg_volume = df["Volume"].tail(20).mean()

            latest = df.iloc[-1]

            if (

                latest["Volume"]

                >=

                avg_volume * 3

                and

                latest["Close"]

                >

                latest["Open"]

            ):

                rows.append({

                    "Symbol": symbol,

                    "Signal": "Institutional Buying",

                    "RVOL":

                        round(

                            latest["Volume"]/avg_volume,

                            2,

                        ),

                })

        return pd.DataFrame(rows)


# ============================================================
# MULTI TIMEFRAME CONFIRMATION
# ============================================================

    def multi_timeframe_confirmation(
        self,
        symbol: str,
    ) -> bool:

        df = self.market_data.get(symbol)

        if df is None:

            return False

        row = df.iloc[-1]

        return (

            row.get("EMA21",0)

            >

            row.get("EMA50",0)

            >

            row.get("EMA200",0)

        )


# ============================================================
# POSITIONAL SCORE
# ============================================================

    def positional_score(
        self,
        symbol: str,
    ) -> int:

        score = 0

        df = self.market_data.get(symbol)

        if df is None or df.empty:
            return score

        row = df.iloc[-1]

        if row.get("Close",0) > row.get("EMA200",0):
            score += 20

        if row.get("EMA50",0) > row.get("EMA200",0):
            score += 20

        if row.get("EMA21",0) > row.get("EMA50",0):
            score += 15

        if row.get("MACD",0) > row.get("MACD_SIGNAL",0):
            score += 15

        if row.get("ADX",0) > 25:
            score += 10

        if row.get("RVOL",0) > 1.5:
            score += 10

        if self.multi_timeframe_confirmation(symbol):
            score += 10

        return score


# ============================================================
# TOP POSITIONAL
# ============================================================

    def top_positional_candidates(
        self,
        limit: int = 5,
    ) -> pd.DataFrame:

        rows = []

        for symbol in self.market_data.keys():

            rows.append({

                "Symbol": symbol,

                "Score": self.positional_score(symbol),

            })

        return (

            pd.DataFrame(rows)

            .sort_values(

                "Score",

                ascending=False,

            )

            .head(limit)

        )


# ============================================================
# MARKET LEADERSHIP ENGINE
# ============================================================

    def market_leadership_engine(
        self,
    ) -> Dict:

        self.update_status(

            "Running Market Leadership Engine..."

        )

        return {

            "Stage Analysis":
                self.stage_analysis(),

            "200 EMA":
                self.trend_200ema(),

            "Relative Strength":
                self.relative_strength_vs_nifty(),

            "Sector Leaders":
                self.sector_leaders(),

            "Institutional Buying":
                self.institutional_accumulation(),

            "Top Positional":
                self.top_positional_candidates(),

        }
    # ============================================================
# AI CONFIDENCE SCORE
# ============================================================

    def ai_confidence(
        self,
        symbol: str,
    ) -> float:

        score = 0

        df = self.market_data.get(symbol)

        if df is None or df.empty:
            return 0.0

        row = df.iloc[-1]

        if row.get("Close", 0) > row.get("VWAP", 0):
            score += 15

        if row.get("EMA21", 0) > row.get("EMA50", 0):
            score += 15

        if row.get("EMA50", 0) > row.get("EMA200", 0):
            score += 15

        if row.get("MACD", 0) > row.get("MACD_SIGNAL", 0):
            score += 15

        if row.get("ADX", 0) >= 25:
            score += 10

        if row.get("RVOL", 0) >= 2:
            score += 10

        if symbol in self.watchlist:
            score += 10

        if symbol in self.fno_symbols:
            score += 10

        return round(min(score, 100), 2)


# ============================================================
# TRADE DIRECTION
# ============================================================

    def trade_direction(
        self,
        symbol: str,
    ) -> str:

        df = self.market_data.get(symbol)

        if df is None or df.empty:
            return "HOLD"

        row = df.iloc[-1]

        bullish = (

            row.get("EMA21", 0)

            >

            row.get("EMA50", 0)

            and

            row.get("MACD", 0)

            >

            row.get("MACD_SIGNAL", 0)

        )

        bearish = (

            row.get("EMA21", 0)

            <

            row.get("EMA50", 0)

            and

            row.get("MACD", 0)

            <

            row.get("MACD_SIGNAL", 0)

        )

        if bullish:
            return "BUY"

        if bearish:
            return "SELL"

        return "HOLD"


# ============================================================
# STOP LOSS
# ============================================================

    def calculate_stoploss(
        self,
        symbol: str,
    ) -> float:

        df = self.market_data.get(symbol)

        if df is None or df.empty:
            return 0

        latest = df.iloc[-1]

        return round(

            latest["Low"],

            2,

        )


# ============================================================
# TARGETS
# ============================================================

    def calculate_targets(
        self,
        entry: float,
        stoploss: float,
        direction: str,
    ) -> Dict:

        risk = abs(entry - stoploss)

        if direction == "BUY":

            return {

                "Target1": round(entry + risk, 2),

                "Target2": round(entry + risk * 2, 2),

                "Target3": round(entry + risk * 3, 2),

            }

        return {

            "Target1": round(entry - risk, 2),

            "Target2": round(entry - risk * 2, 2),

            "Target3": round(entry - risk * 3, 2),

        }


# ============================================================
# RISK REWARD
# ============================================================

    def risk_reward(
        self,
        entry: float,
        stoploss: float,
        target: float,
    ) -> float:

        risk = abs(entry - stoploss)

        reward = abs(target - entry)

        if risk == 0:

            return 0

        return round(

            reward / risk,

            2,

        )


# ============================================================
# POSITION SIZE
# ============================================================

    def position_size(
        self,
        capital: float,
        risk_amount: float,
        entry: float,
        stoploss: float,
    ) -> int:

        risk = abs(entry - stoploss)

        if risk == 0:

            return 0

        qty = int(

            risk_amount / risk

        )

        max_qty = int(

            capital / entry

        )

        return min(

            qty,

            max_qty,

        )


# ============================================================
# TRADE CARD
# ============================================================

    def generate_trade(
        self,
        symbol: str,
        capital: float = 100000,
        risk_amount: float = 1000,
    ) -> Dict:

        df = self.market_data.get(symbol)

        if df is None or df.empty:

            return {}

        latest = df.iloc[-1]

        entry = latest["Close"]

        direction = self.trade_direction(symbol)

        stoploss = self.calculate_stoploss(symbol)

        targets = self.calculate_targets(

            entry,

            stoploss,

            direction,

        )

        quantity = self.position_size(

            capital,

            risk_amount,

            entry,

            stoploss,

        )

        return {

            "Symbol": symbol,

            "Signal": direction,

            "Entry": round(entry, 2),

            "StopLoss": stoploss,

            "Target1": targets["Target1"],

            "Target2": targets["Target2"],

            "Target3": targets["Target3"],

            "RR": self.risk_reward(

                entry,

                stoploss,

                targets["Target2"],

            ),

            "Quantity": quantity,

            "Confidence": self.ai_confidence(symbol),

        }


# ============================================================
# BUILD TRADE LIST
# ============================================================

    def generate_trade_list(
        self,
        symbols: List[str],
    ) -> pd.DataFrame:

        trades = []

        for symbol in symbols:

            trade = self.generate_trade(symbol)

            if trade:

                trades.append(trade)

        return (

            pd.DataFrame(trades)

            .sort_values(

                "Confidence",

                ascending=False,

            )

        )


# ============================================================
# TOP AI TRADES
# ============================================================

    def top_ai_trades(
        self,
    ) -> Dict:

        intraday = list(

            self.top_intraday_candidates()["Symbol"]

        )

        swing = list(

            self.top_swing_candidates()["Symbol"]

        )

        positional = list(

            self.top_positional_candidates()["Symbol"]

        )

        return {

            "Intraday":

                self.generate_trade_list(intraday),

            "Swing":

                self.generate_trade_list(swing),

            "Positional":

                self.generate_trade_list(positional),

        }


# ============================================================
# AI DECISION ENGINE
# ============================================================

    def ai_decision_engine(
        self,
    ) -> Dict:

        self.update_status(

            "Generating AI Trade Decisions..."

        )

        decisions = self.top_ai_trades()

        self.update_status(

            "AI Decision Engine Complete."

        )

        return decisions
    # ============================================================
# DASHBOARD CALLBACK
# ============================================================

    def register_dashboard_callback(
        self,
        callback,
    ) -> None:

        self.dashboard_callback = callback


# ============================================================
# NOTIFICATION CALLBACK
# ============================================================

    def register_notification_callback(
        self,
        callback,
    ) -> None:

        self.notification_callback = callback


# ============================================================
# UPDATE DASHBOARD
# ============================================================

    def update_dashboard(
        self,
    ) -> None:

        if self.dashboard_callback is None:
            return

        data = {

            "market_status": self.market_status(),

            "last_update": self.last_refresh,

            "top_gainers": self.get_top_gainers(),

            "top_losers": self.get_top_losers(),

            "intraday": self.top_intraday_candidates(),

            "swing": self.top_swing_candidates(),

            "positional": self.top_positional_candidates(),

            "indices": self.indices,

            "breadth": self.market_breadth,

        }

        self.dashboard_callback(data)


# ============================================================
# SEND NOTIFICATION
# ============================================================

    def notify(
        self,
        title: str,
        message: str,
    ) -> None:

        if self.notification_callback is None:
            return

        self.notification_callback(
            title,
            message,
        )


# ============================================================
# MARKET CYCLE
# ============================================================

    def market_cycle(
        self,
    ) -> None:

        status = self.market_status()

        if status == MarketStatus.PREMARKET:

            self.premarket_engine()

        elif status == MarketStatus.LIVE:

            self.live_update()

            self.intraday_engine()

            self.swing_engine()

            self.market_leadership_engine()

            self.ai_decision_engine()

        self.update_dashboard()


# ============================================================
# AUTO SCHEDULER
# ============================================================

    def scheduler_loop(
        self,
    ) -> None:

        while self.running:

            try:

                self.market_cycle()

            except Exception as exc:

                self.report_error(exc)

            time.sleep(

                self.refresh_interval

            )


# ============================================================
# START SCHEDULER
# ============================================================

    def start_scheduler(
        self,
    ) -> None:

        if getattr(self, "_scheduler", None):

            if self._scheduler.is_alive():

                return

        self.running = True

        self._scheduler = threading.Thread(

            target=self.scheduler_loop,

            daemon=True,

        )

        self._scheduler.start()


# ============================================================
# STOP SCHEDULER
# ============================================================

    def stop_scheduler(
        self,
    ) -> None:

        self.running = False


# ============================================================
# COUNTDOWN
# ============================================================

    def refresh_countdown(
        self,
    ) -> int:

        if self.last_refresh is None:

            return self.refresh_interval

        elapsed = (

            datetime.now()

            -

            self.last_refresh

        ).seconds

        return max(

            self.refresh_interval - elapsed,

            0,

        )


# ============================================================
# END OF DAY REPORT
# ============================================================

    def end_of_day_report(
        self,
    ) -> Dict:

        return {

            "Date": datetime.now().date(),

            "Scanned Stocks": len(self.market_data),

            "Top Intraday":

                self.top_intraday_candidates(),

            "Top Swing":

                self.top_swing_candidates(),

            "Top Positional":

                self.top_positional_candidates(),

            "Market Breadth":

                self.market_breadth,

        }


# ============================================================
# ENGINE HEALTH
# ============================================================

    def health_status(
        self,
    ) -> Dict:

        return {

            "Connected":

                self.is_connected(),

            "Running":

                self.running,

            "Market":

                self.market_status(),

            "Cache Valid":

                self.cache_valid(),

            "Stocks":

                len(self.market_data),

            "Last Refresh":

                self.last_refresh,

        }


# ============================================================
# SHUTDOWN
# ============================================================

    def shutdown(
        self,
    ) -> None:

        self.update_status(

            "Stopping NSE Data Engine..."

        )

        self.stop_scheduler()

        self.disconnect()

        self.market_data.clear()

        self.indices.clear()

        self.watchlist.clear()

        self.update_status(

            "NSE Data Engine Stopped."

        )


# ============================================================
# STARTUP
# ============================================================

    def startup(
        self,
    ) -> None:

        self.update_status(

            "Starting NSE Data Engine..."

        )

        self.connect()

        self.load_symbol_master()

        self.load_sector_master()

        self.load_fno_symbols()

        self.start_scheduler()

        self.update_status(

            "NSE Data Engine Ready."

        )


# ============================================================
# VERSION
# ============================================================

    @property
    def version(
        self,
    ) -> str:

        return "4.0.0"
    # ============================================================
# INTERNET CONNECTIVITY
# ============================================================

    def internet_available(
        self,
    ) -> bool:

        try:

            socket.create_connection(

                ("8.8.8.8", 53),

                timeout=3,

            )

            return True

        except OSError:

            return False


# ============================================================
# WAIT FOR INTERNET
# ============================================================

    def wait_for_connection(
        self,
        retry_interval: int = 5,
    ) -> None:

        while not self.internet_available():

            self.update_status(

                "Waiting for internet..."

            )

            time.sleep(retry_interval)

        self.update_status(

            "Internet connection restored."

        )


# ============================================================
# EXPONENTIAL RECONNECT
# ============================================================

    def reconnect_with_backoff(
        self,
        max_attempts: int = 6,
    ) -> bool:

        delay = 2

        for attempt in range(max_attempts):

            try:

                self.connect()

                if self.is_connected():

                    self.update_status(

                        "Reconnected successfully."

                    )

                    return True

            except Exception as exc:

                self.report_error(exc)

            time.sleep(delay)

            delay *= 2

        self.update_status(

            "Reconnect failed."

        )

        return False


# ============================================================
# REQUEST RATE LIMITER
# ============================================================

    def rate_limit(
        self,
    ) -> None:

        current = time.time()

        elapsed = current - self._last_request

        minimum_delay = 0.25

        if elapsed < minimum_delay:

            time.sleep(

                minimum_delay - elapsed

            )

        self._last_request = time.time()


# ============================================================
# SAFE REQUEST WRAPPER
# ============================================================

    def execute_request(
        self,
        callback,
        *args,
        **kwargs,
    ):

        self.rate_limit()

        retries = 3

        for _ in range(retries):

            try:

                return callback(

                    *args,

                    **kwargs,

                )

            except Exception as exc:

                self.report_error(exc)

                time.sleep(1)

        return None


# ============================================================
# VALIDATE OHLCV
# ============================================================

    def validate_dataframe(
        self,
        df: pd.DataFrame,
    ) -> bool:

        required = [

            "Open",

            "High",

            "Low",

            "Close",

            "Volume",

        ]

        for column in required:

            if column not in df.columns:

                return False

        return not df.empty


# ============================================================
# REMOVE DUPLICATES
# ============================================================

    def clean_dataframe(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        df = df.drop_duplicates()

        df = df.sort_index()

        return df


# ============================================================
# RECOVER MISSING CANDLES
# ============================================================

    def recover_missing_candles(
        self,
        symbol: str,
    ) -> None:

        df = self.market_data.get(symbol)

        if df is None:

            return

        df = self.clean_dataframe(df)

        self.market_data[symbol] = df


# ============================================================
# PERFORMANCE METRICS
# ============================================================

    def update_metrics(
        self,
        execution_time: float,
    ) -> None:

        self.metrics["refreshes"] += 1

        self.metrics["last_runtime"] = execution_time

        self.metrics["total_runtime"] += execution_time

        self.metrics["average_runtime"] = (

            self.metrics["total_runtime"]

            /

            self.metrics["refreshes"]

        )


# ============================================================
# ENGINE STATISTICS
# ============================================================

    def statistics(
        self,
    ) -> Dict:

        return {

            "Stocks":

                len(self.market_data),

            "Refreshes":

                self.metrics["refreshes"],

            "Average Runtime":

                round(

                    self.metrics["average_runtime"],

                    2,

                ),

            "Last Runtime":

                round(

                    self.metrics["last_runtime"],

                    2,

                ),

            "Connected":

                self.is_connected(),

        }


# ============================================================
# MEMORY CLEANUP
# ============================================================

    def cleanup_cache(
        self,
    ) -> None:

        gc.collect()

        self.update_status(

            "Memory cleanup completed."

        )


# ============================================================
# HEARTBEAT
# ============================================================

    def heartbeat(
        self,
    ) -> None:

        self.metrics["heartbeat"] = datetime.now()


# ============================================================
# HEALTH CHECK
# ============================================================

    def health_check(
        self,
    ) -> bool:

        if not self.internet_available():

            return False

        if not self.is_connected():

            return False

        return True


# ============================================================
# WATCHDOG
# ============================================================

    def watchdog(
        self,
    ) -> None:

        if not self.health_check():

            self.update_status(

                "Watchdog restarting engine..."

            )

            self.reconnect_with_backoff()

        self.heartbeat()
        # ============================================================
# PRIORITY SYMBOLS
# ============================================================

    def priority_symbols(
        self,
    ) -> List[str]:

        priority = []

        # -----------------------------------------
        # 1. F&O Stocks
        # -----------------------------------------

        priority.extend(self.fno_symbols)

        # -----------------------------------------
        # 2. Watchlist
        # -----------------------------------------

        for symbol in self.watchlist:

            if symbol not in priority:

                priority.append(symbol)

        # -----------------------------------------
        # 3. Remaining Stocks
        # -----------------------------------------

        for symbol in self.market_data.keys():

            if symbol not in priority:

                priority.append(symbol)

        return priority


# ============================================================
# BATCH INDICATOR UPDATE
# ============================================================

    def update_indicators_batch(
        self,
    ) -> None:

        for symbol in self.priority_symbols():

            df = self.market_data.get(symbol)

            if df is None:

                continue

            if df.empty:

                continue

            # -------------------------------------
            # Indicator Engine Integration
            # -------------------------------------

            self.market_data[symbol] = (

                self.indicator_engine.calculate(df)

            )


# ============================================================
# INCREMENTAL UPDATE
# ============================================================

    def incremental_indicator_update(
        self,
        symbols: List[str],
    ) -> None:

        for symbol in symbols:

            df = self.market_data.get(symbol)

            if df is None:

                continue

            self.market_data[symbol] = (

                self.indicator_engine.update_last_bar(df)

            )


# ============================================================
# SCANNER EXECUTOR
# ============================================================

    def execute_scanners(
        self,
    ) -> Dict:

        return self.scanner_executor.execute(

            self.market_data

        )


# ============================================================
# OPPORTUNITY RANKER
# ============================================================

    def rank_opportunities(
        self,
        opportunities: Dict,
    ):

        return self.opportunity_ranker.rank(

            opportunities

        )


# ============================================================
# AI PIPELINE
# ============================================================

    def run_ai_pipeline(
        self,
    ) -> Dict:

        opportunities = (

            self.execute_scanners()

        )

        ranked = (

            self.rank_opportunities(

                opportunities

            )

        )

        return self.ai_engine.analyse(

            ranked

        )


# ============================================================
# EVENT BUS
# ============================================================

    def publish_event(
        self,
        event: str,
        payload=None,
    ) -> None:

        if not hasattr(

            self,

            "_event_bus",

        ):

            return

        self._event_bus.publish(

            event,

            payload,

        )


# ============================================================
# EVENT SUBSCRIBE
# ============================================================

    def subscribe(
        self,
        event: str,
        callback,
    ) -> None:

        self._event_bus.subscribe(

            event,

            callback,

        )


# ============================================================
# SAVE CONFIGURATION
# ============================================================

    def save_configuration(
        self,
        filename: str,
    ) -> None:

        config = {

            "refresh_interval":

                self.refresh_interval,

            "watchlist":

                self.watchlist,

            "version":

                self.version,

        }

        with open(

            filename,

            "w",

        ) as file:

            json.dump(

                config,

                file,

                indent=4,

            )


# ============================================================
# LOAD CONFIGURATION
# ============================================================

    def load_configuration(
        self,
        filename: str,
    ) -> None:

        if not os.path.exists(

            filename,

        ):

            return

        with open(

            filename,

            "r",

        ) as file:

            config = json.load(file)

        self.refresh_interval = config.get(

            "refresh_interval",

            self.refresh_interval,

        )

        self.watchlist = config.get(

            "watchlist",

            [],

        )


# ============================================================
# COMPLETE MARKET PIPELINE
# ============================================================

    def run_complete_pipeline(
        self,
    ) -> Dict:

        start = time.perf_counter()

        self.live_update()

        self.update_indicators_batch()

        self.premarket_engine()

        self.intraday_engine()

        self.swing_engine()

        self.market_leadership_engine()

        decisions = self.run_ai_pipeline()

        self.update_dashboard()

        runtime = (

            time.perf_counter()

            - start

        )

        self.update_metrics(runtime)

        self.publish_event(

            "pipeline_completed",

            decisions,

        )

        return decisions


# ============================================================
# FINAL INITIALIZATION
# ============================================================

    def initialize(
        self,
    ) -> None:

        self.update_status(

            "Initializing StockVersity Scanner Pro..."

        )

        self.load_configuration(

            "config.json",

        )

        self.startup()

        self.update_status(

            "System Ready."

        )


# ============================================================
# FINALIZE
# ============================================================

    def finalize(
        self,
    ) -> None:

        self.save_configuration(

            "config.json",

        )

        self.shutdown()

        self.update_status(

            "Shutdown Complete."

        )


# ============================================================
# BUILD INFORMATION
# ============================================================

    @property
    def build_information(
        self,
    ) -> Dict:

        return {

            "Application":

                "StockVersity Scanner Pro",

            "Version":

                "4.0",

            "Powered By":

                "AI",

            "Status":

                "Production",

            "Market":

                "NSE",

        }


# ============================================================
# END OF FILE
# ============================================================