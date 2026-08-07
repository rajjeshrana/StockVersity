"""
=============================================================
StockVersity Scanner Pro
Market Data Service

Professional Market Data Engine

Features
--------
✓ Yahoo Finance Downloader
✓ NSE Symbol Support
✓ Multi-thread Download
✓ Smart Cache
✓ Live Refresh
✓ Thread Safe
✓ PySide6 Ready
=============================================================
"""

from __future__ import annotations

import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf


class MarketDataService:
    """
    Professional Market Data Service
    """

    CACHE_TIMEOUT = 300
    MAX_RETRY = 3

    def __init__(self):

        self.cache = {}

        self.cache_time = {}

        self.lock = threading.Lock()

        self.running = False

        self.progress_callback = None

        self.refresh_callback = None

        self.logger = logging.getLogger("MarketData")

        self.logger.setLevel(logging.INFO)

        self.download_workers = 8

        self.default_period = "6mo"

        self.default_interval = "1d"

    # =====================================================
    # CALLBACKS
    # =====================================================

    def set_progress_callback(self, callback):

        self.progress_callback = callback

    def set_refresh_callback(self, callback):

        self.refresh_callback = callback

    # =====================================================
    # CACHE
    # =====================================================

    def cache_key(self, symbol, interval, period):

        return f"{symbol}_{interval}_{period}"

    def put_cache(
        self,
        symbol,
        interval,
        period,
        dataframe,
    ):

        key = self.cache_key(
            symbol,
            interval,
            period,
        )

        with self.lock:

            self.cache[key] = dataframe

            self.cache_time[key] = datetime.now()

    def get_cache(
        self,
        symbol,
        interval,
        period,
    ):

        key = self.cache_key(
            symbol,
            interval,
            period,
        )

        with self.lock:

            if key not in self.cache:

                return None

            age = (

                datetime.now()

                - self.cache_time[key]

            ).seconds

            if age > self.CACHE_TIMEOUT:

                return None

            return self.cache[key]

    def clear_cache(self):

        with self.lock:

            self.cache.clear()

            self.cache_time.clear()

    # =====================================================
    # DOWNLOAD SINGLE SYMBOL
    # =====================================================

    def download_symbol(
        self,
        symbol,
        interval=None,
        period=None,
    ):

        interval = interval or self.default_interval

        period = period or self.default_period

        cached = self.get_cache(
            symbol,
            interval,
            period,
        )

        if cached is not None:

            return cached

        ticker = symbol

        if not ticker.endswith(".NS"):

            ticker += ".NS"

        for attempt in range(self.MAX_RETRY):

            try:

                df = yf.download(
                    ticker,
                    interval=interval,
                    period=period,
                    progress=False,
                    auto_adjust=True,
                    threads=False,
                )

                if df.empty:

                    continue

                df.reset_index(inplace=True)

                df.columns = [

                    str(c).lower()

                    for c in df.columns

                ]

                df["symbol"] = symbol

                self.put_cache(
                    symbol,
                    interval,
                    period,
                    df,
                )

                return df

            except Exception as e:

                self.logger.warning(

                    "%s : %s",

                    symbol,

                    e,

                )

                time.sleep(1)

        return pd.DataFrame()
        # =====================================================
    # DOWNLOAD MULTIPLE SYMBOLS
    # =====================================================

    def download_symbols(
        self,
        symbols,
        interval=None,
        period=None,
    ):

        interval = interval or self.default_interval

        period = period or self.default_period

        data = []

        total = len(symbols)

        completed = 0

        for symbol in symbols:

            completed += 1

            df = self.download_symbol(

                symbol,

                interval,

                period,

            )

            if not df.empty:

                data.append(df)

            if self.progress_callback:

                self.progress_callback(

                    completed,

                    total,

                    symbol,

                )

        if data:

            return pd.concat(

                data,

                ignore_index=True,

            )

        return pd.DataFrame()

    # =====================================================
    # PARALLEL DOWNLOAD
    # =====================================================

    def download_parallel(
        self,
        symbols,
        interval=None,
        period=None,
    ):

        interval = interval or self.default_interval

        period = period or self.default_period

        total = len(symbols)

        completed = 0

        result = []

        with ThreadPoolExecutor(

            max_workers=self.download_workers

        ) as executor:

            futures = {

                executor.submit(

                    self.download_symbol,

                    symbol,

                    interval,

                    period,

                ): symbol

                for symbol in symbols

            }

            for future in as_completed(

                futures

            ):

                symbol = futures[future]

                completed += 1

                try:

                    df = future.result()

                    if not df.empty:

                        result.append(df)

                except Exception as e:

                    self.logger.error(

                        "%s : %s",

                        symbol,

                        e,

                    )

                if self.progress_callback:

                    self.progress_callback(

                        completed,

                        total,

                        symbol,

                    )

        if result:

            return pd.concat(

                result,

                ignore_index=True,

            )

        return pd.DataFrame()

    # =====================================================
    # RETRY DOWNLOAD
    # =====================================================

    def retry_download(

        self,

        symbol,

        interval,

        period,

    ):

        for _ in range(self.MAX_RETRY):

            df = self.download_symbol(

                symbol,

                interval,

                period,

            )

            if not df.empty:

                return df

        return pd.DataFrame()

    # =====================================================
    # DOWNLOAD WATCHLIST
    # =====================================================

    def download_watchlist(

        self,

        symbols,

        interval="1d",

        period="6mo",

    ):

        return self.download_parallel(

            symbols,

            interval,

            period,

        )

    # =====================================================
    # REFRESH WATCHLIST
    # =====================================================

    def refresh_watchlist(

        self,

        symbols,

        interval="1d",

        period="6mo",

    ):

        self.clear_cache()

        return self.download_parallel(

            symbols,

            interval,

            period,

        )

    # =====================================================
    # UPDATE SINGLE SYMBOL
    # =====================================================

    def update_symbol(

        self,

        symbol,

    ):

        self.logger.info(

            "Updating %s",

            symbol,

        )

        return self.download_symbol(

            symbol,

            self.default_interval,

            self.default_period,

        )

    # =====================================================
    # GET LATEST PRICE
    # =====================================================

    def latest_price(

        self,

        symbol,

    ):

        df = self.download_symbol(

            symbol,

            interval="1m",

            period="1d",

        )

        if df.empty:

            return None

        return float(

            df.iloc[-1]["close"]

        )

    # =====================================================
    # GET LATEST CANDLE
    # =====================================================

    def latest_candle(

        self,

        symbol,

    ):

        df = self.download_symbol(

            symbol,

            interval="5m",

            period="5d",

        )

        if df.empty:

            return None

        return df.iloc[-1]

    # =====================================================
    # DOWNLOAD BY INTERVAL
    # =====================================================

    def intraday_data(

        self,

        symbol,

    ):

        return self.download_symbol(

            symbol,

            interval="5m",

            period="5d",

        )

    def swing_data(

        self,

        symbol,

    ):

        return self.download_symbol(

            symbol,

            interval="1d",

            period="1y",

        )

    def positional_data(

        self,

        symbol,

    ):

        return self.download_symbol(

            symbol,

            interval="1wk",

            period="5y",

        )
        # =====================================================
    # NSE INDEX URLs
    # =====================================================

    INDEX_URLS = {

        "NIFTY50":
        "https://archives.nseindia.com/content/indices/ind_nifty50list.csv",

        "NIFTY100":
        "https://archives.nseindia.com/content/indices/ind_nifty100list.csv",

        "NIFTY200":
        "https://archives.nseindia.com/content/indices/ind_nifty200list.csv",

        "NIFTY500":
        "https://archives.nseindia.com/content/indices/ind_nifty500list.csv",

    }

    # =====================================================
    # CACHE DIRECTORY
    # =====================================================

    def universe_directory(self):

        folder = Path.home() / ".stockversity"

        folder.mkdir(

            parents=True,

            exist_ok=True,

        )

        return folder

    # =====================================================
    # CACHE FILE
    # =====================================================

    def universe_file(

        self,

        index_name,

    ):

        return (

            self.universe_directory()

            / f"{index_name.lower()}.csv"

        )

    # =====================================================
    # DOWNLOAD INDEX
    # =====================================================

    def update_index(

        self,

        index_name,

    ):

        if index_name not in self.INDEX_URLS:

            return False

        try:

            headers = {

                "User-Agent":

                "Mozilla/5.0"

            }

            response = requests.get(

                self.INDEX_URLS[index_name],

                headers=headers,

                timeout=20,

            )

            response.raise_for_status()

            file = self.universe_file(

                index_name,

            )

            file.write_text(

                response.text,

                encoding="utf-8",

            )

            self.logger.info(

                "%s Updated",

                index_name,

            )

            return True

        except Exception as e:

            self.logger.warning(

                "%s",

                e,

            )

            return False

    # =====================================================
    # READ INDEX
    # =====================================================

    def read_index(

        self,

        index_name,

    ):

        file = self.universe_file(

            index_name,

        )

        if not file.exists():

            self.update_index(

                index_name,

            )

        if not file.exists():

            return []

        try:

            df = pd.read_csv(

                file,

            )

        except Exception:

            return []

        for column in df.columns:

            if "SYMBOL" in column.upper():

                return (

                    df[column]

                    .dropna()

                    .astype(str)

                    .str.strip()

                    .tolist()

                )

        return []

    # =====================================================
    # AUTO REFRESH
    # =====================================================

    def refresh_universe(

        self,

        index_name,

    ):

        file = self.universe_file(

            index_name,

        )

        if not file.exists():

            self.update_index(

                index_name,

            )

            return

        age = (

            time.time()

            -

            file.stat().st_mtime

        )

        if age > 86400:

            self.update_index(

                index_name,

            )

    # =====================================================
    # NIFTY 50
    # =====================================================

    def nifty50(self):

        self.refresh_universe(

            "NIFTY50"

        )

        return self.read_index(

            "NIFTY50"

        )

    # =====================================================
    # NIFTY 100
    # =====================================================

    def nifty100(self):

        self.refresh_universe(

            "NIFTY100"

        )

        return self.read_index(

            "NIFTY100"

        )

    # =====================================================
    # NIFTY 200
    # =====================================================

    def nifty200(self):

        self.refresh_universe(

            "NIFTY200"

        )

        return self.read_index(

            "NIFTY200"

        )

    # =====================================================
    # NIFTY 500
    # =====================================================

    def nifty500(self):

        self.refresh_universe(

            "NIFTY500"

        )

        return self.read_index(

            "NIFTY500"

        )

    # =====================================================
    # F&O SYMBOLS
    # =====================================================

    def fo_symbols(self):

        """
        Update this list periodically or replace it
        with automatic NSE F&O download.
        """

        return [

            "RELIANCE",

            "HDFCBANK",

            "ICICIBANK",

            "SBIN",

            "AXISBANK",

            "KOTAKBANK",

            "INFY",

            "TCS",

            "LT",

            "BAJFINANCE",

            "BHARTIARTL",

            "ADANIENT",

            "TATAMOTORS",

            "SUNPHARMA",

            "TATASTEEL",

            "JSWSTEEL",

            "ULTRACEMCO",

            "TECHM",

            "POWERGRID",

            "WIPRO",

        ]
        # =====================================================
    # REAL TIME ENGINE
    # =====================================================

    def start_live_updates(
        self,
        symbols,
        interval="1m",
        refresh_seconds=15,
    ):
        """
        Starts background market updates.
        """

        if self.running:
            return

        self.running = True

        self.live_symbols = list(symbols)

        self.live_interval = interval

        self.refresh_seconds = refresh_seconds

        self.thread = threading.Thread(
            target=self._live_loop,
            daemon=True,
        )

        self.thread.start()

        self.logger.info(
            "Live Market Engine Started"
        )

    # =====================================================
    # STOP LIVE ENGINE
    # =====================================================

    def stop_live_updates(self):

        self.running = False

        self.logger.info(
            "Live Market Engine Stopped"
        )

    # =====================================================
    # LIVE LOOP
    # =====================================================

    def _live_loop(self):

        while self.running:

            try:

                if self.market_open():

                    self.refresh_live_data()

            except Exception as e:

                self.logger.error(str(e))

            time.sleep(

                self.refresh_seconds

            )

    # =====================================================
    # REFRESH LIVE DATA
    # =====================================================

    def refresh_live_data(self):

        data = self.download_parallel(

            self.live_symbols,

            interval=self.live_interval,

            period="1d",

        )

        if data.empty:

            return

        self.live_data = data

        if self.refresh_callback:

            self.refresh_callback(data)

    # =====================================================
    # GET LIVE DATA
    # =====================================================

    def get_live_data(self):

        return getattr(

            self,

            "live_data",

            pd.DataFrame(),

        )

    # =====================================================
    # MARKET STATUS
    # =====================================================

    def market_open(self):

        now = datetime.now()

        if now.weekday() >= 5:

            return False

        current = now.hour * 60 + now.minute

        market_open = 9 * 60 + 15

        market_close = 15 * 60 + 30

        return market_open <= current <= market_close

    # =====================================================
    # WAIT FOR MARKET
    # =====================================================

    def wait_until_market(self):

        while not self.market_open():

            time.sleep(30)

    # =====================================================
    # PRELOAD CACHE
    # =====================================================

    def preload_market(
        self,
        symbols,
    ):

        self.logger.info(

            "Preloading %d symbols",

            len(symbols),

        )

        self.download_parallel(

            symbols,

            interval="1d",

            period="6mo",

        )

    # =====================================================
    # LIVE PRICE
    # =====================================================

    def live_price(
        self,
        symbol,
    ):

        df = self.download_symbol(

            symbol,

            interval="1m",

            period="1d",

        )

        if df.empty:

            return None

        return float(

            df.iloc[-1]["close"]

        )

    # =====================================================
    # LIVE CHANGE %
    # =====================================================

    def live_change(
        self,
        symbol,
    ):

        df = self.download_symbol(

            symbol,

            interval="1m",

            period="1d",

        )

        if len(df) < 2:

            return 0

        previous = df.iloc[-2]["close"]

        latest = df.iloc[-1]["close"]

        return round(

            ((latest - previous) / previous) * 100,

            2,

        )

    # =====================================================
    # MARKET BREADTH
    # =====================================================

    def market_breadth(
        self,
        dataframe,
    ):

        if dataframe.empty:

            return {

                "advance": 0,

                "decline": 0,

                "unchanged": 0,

            }

        advance = len(

            dataframe[

                dataframe["close"]

                >

                dataframe["open"]

            ]

        )

        decline = len(

            dataframe[

                dataframe["close"]

                <

                dataframe["open"]

            ]

        )

        unchanged = len(dataframe) - advance - decline

        return {

            "advance": advance,

            "decline": decline,

            "unchanged": unchanged,

        }

    # =====================================================
    # MARKET SENTIMENT
    # =====================================================

    def market_sentiment(
        self,
        dataframe,
    ):

        breadth = self.market_breadth(

            dataframe

        )

        if breadth["advance"] > breadth["decline"] * 1.5:

            return "Bullish"

        if breadth["decline"] > breadth["advance"] * 1.5:

            return "Bearish"

        return "Neutral"
        # =====================================================
    # SCANNER DATA
    # =====================================================

    def scanner_data(
        self,
        symbols,
        interval="1d",
        period="6mo",
    ):

        return self.download_parallel(

            symbols,

            interval,

            period,

        )

    # =====================================================
    # GET SYMBOL DATA
    # =====================================================

    def symbol_data(

        self,

        symbol,

        interval="1d",

        period="6mo",

    ):

        return self.download_symbol(

            symbol,

            interval,

            period,

        )

    # =====================================================
    # LAST CLOSE
    # =====================================================

    def last_close(

        self,

        symbol,

    ):

        df = self.symbol_data(

            symbol,

        )

        if df.empty:

            return None

        return float(

            df.iloc[-1]["close"]

        )

    # =====================================================
    # TODAY HIGH
    # =====================================================

    def today_high(

        self,

        symbol,

    ):

        df = self.download_symbol(

            symbol,

            interval="5m",

            period="1d",

        )

        if df.empty:

            return None

        return float(

            df["high"].max()

        )

    # =====================================================
    # TODAY LOW
    # =====================================================

    def today_low(

        self,

        symbol,

    ):

        df = self.download_symbol(

            symbol,

            interval="5m",

            period="1d",

        )

        if df.empty:

            return None

        return float(

            df["low"].min()

        )

    # =====================================================
    # TODAY VOLUME
    # =====================================================

    def today_volume(

        self,

        symbol,

    ):

        df = self.download_symbol(

            symbol,

            interval="5m",

            period="1d",

        )

        if df.empty:

            return 0

        return int(

            df["volume"].sum()

        )

    # =====================================================
    # 52 WEEK HIGH
    # =====================================================

    def high_52_week(

        self,

        symbol,

    ):

        df = self.download_symbol(

            symbol,

            interval="1d",

            period="1y",

        )

        if df.empty:

            return None

        return float(

            df["high"].max()

        )

    # =====================================================
    # 52 WEEK LOW
    # =====================================================

    def low_52_week(

        self,

        symbol,

    ):

        df = self.download_symbol(

            symbol,

            interval="1d",

            period="1y",

        )

        if df.empty:

            return None

        return float(

            df["low"].min()

        )

    # =====================================================
    # GAP %
    # =====================================================

    def gap_percent(

        self,

        symbol,

    ):

        df = self.download_symbol(

            symbol,

            interval="1d",

            period="5d",

        )

        if len(df) < 2:

            return 0

        previous_close = df.iloc[-2]["close"]

        today_open = df.iloc[-1]["open"]

        return round(

            (

                today_open

                -

                previous_close

            )

            /

            previous_close

            *

            100,

            2,

        )

    # =====================================================
    # PRICE CHANGE
    # =====================================================

    def change_percent(

        self,

        symbol,

    ):

        df = self.download_symbol(

            symbol,

            interval="1d",

            period="5d",

        )

        if len(df) < 2:

            return 0

        previous = df.iloc[-2]["close"]

        latest = df.iloc[-1]["close"]

        return round(

            (

                latest

                -

                previous

            )

            /

            previous

            *

            100,

            2,

        )

    # =====================================================
    # IS BREAKOUT
    # =====================================================

    def breakout(

        self,

        symbol,

    ):

        df = self.download_symbol(

            symbol,

            interval="1d",

            period="3mo",

        )

        if len(df) < 30:

            return False

        latest = df.iloc[-1]["close"]

        previous_high = (

            df.iloc[:-1]["high"]

            .tail(20)

            .max()

        )

        return latest > previous_high

    # =====================================================
    # IS BREAKDOWN
    # =====================================================

    def breakdown(

        self,

        symbol,

    ):

        df = self.download_symbol(

            symbol,

            interval="1d",

            period="3mo",

        )

        if len(df) < 30:

            return False

        latest = df.iloc[-1]["close"]

        previous_low = (

            df.iloc[:-1]["low"]

            .tail(20)

            .min()

        )

        return latest < previous_low
        # =====================================================
    # SCANNER DATA
    # =====================================================

    def scanner_data(
        self,
        symbols,
        interval="1d",
        period="6mo",
    ):

        return self.download_parallel(

            symbols,

            interval,

            period,

        )

    # =====================================================
    # GET SYMBOL DATA
    # =====================================================

    def symbol_data(

        self,

        symbol,

        interval="1d",

        period="6mo",

    ):

        return self.download_symbol(

            symbol,

            interval,

            period,

        )

    # =====================================================
    # LAST CLOSE
    # =====================================================

    def last_close(

        self,

        symbol,

    ):

        df = self.symbol_data(

            symbol,

        )

        if df.empty:

            return None

        return float(

            df.iloc[-1]["close"]

        )

    # =====================================================
    # TODAY HIGH
    # =====================================================

    def today_high(

        self,

        symbol,

    ):

        df = self.download_symbol(

            symbol,

            interval="5m",

            period="1d",

        )

        if df.empty:

            return None

        return float(

            df["high"].max()

        )

    # =====================================================
    # TODAY LOW
    # =====================================================

    def today_low(

        self,

        symbol,

    ):

        df = self.download_symbol(

            symbol,

            interval="5m",

            period="1d",

        )

        if df.empty:

            return None

        return float(

            df["low"].min()

        )

    # =====================================================
    # TODAY VOLUME
    # =====================================================

    def today_volume(

        self,

        symbol,

    ):

        df = self.download_symbol(

            symbol,

            interval="5m",

            period="1d",

        )

        if df.empty:

            return 0

        return int(

            df["volume"].sum()

        )

    # =====================================================
    # 52 WEEK HIGH
    # =====================================================

    def high_52_week(

        self,

        symbol,

    ):

        df = self.download_symbol(

            symbol,

            interval="1d",

            period="1y",

        )

        if df.empty:

            return None

        return float(

            df["high"].max()

        )

    # =====================================================
    # 52 WEEK LOW
    # =====================================================

    def low_52_week(

        self,

        symbol,

    ):

        df = self.download_symbol(

            symbol,

            interval="1d",

            period="1y",

        )

        if df.empty:

            return None

        return float(

            df["low"].min()

        )

    # =====================================================
    # GAP %
    # =====================================================

    def gap_percent(

        self,

        symbol,

    ):

        df = self.download_symbol(

            symbol,

            interval="1d",

            period="5d",

        )

        if len(df) < 2:

            return 0

        previous_close = df.iloc[-2]["close"]

        today_open = df.iloc[-1]["open"]

        return round(

            (

                today_open

                -

                previous_close

            )

            /

            previous_close

            *

            100,

            2,

        )

    # =====================================================
    # PRICE CHANGE
    # =====================================================

    def change_percent(

        self,

        symbol,

    ):

        df = self.download_symbol(

            symbol,

            interval="1d",

            period="5d",

        )

        if len(df) < 2:

            return 0

        previous = df.iloc[-2]["close"]

        latest = df.iloc[-1]["close"]

        return round(

            (

                latest

                -

                previous

            )

            /

            previous

            *

            100,

            2,

        )

    # =====================================================
    # IS BREAKOUT
    # =====================================================

    def breakout(

        self,

        symbol,

    ):

        df = self.download_symbol(

            symbol,

            interval="1d",

            period="3mo",

        )

        if len(df) < 30:

            return False

        latest = df.iloc[-1]["close"]

        previous_high = (

            df.iloc[:-1]["high"]

            .tail(20)

            .max()

        )

        return latest > previous_high

    # =====================================================
    # IS BREAKDOWN
    # =====================================================

    def breakdown(

        self,

        symbol,

    ):

        df = self.download_symbol(

            symbol,

            interval="1d",

            period="3mo",

        )

        if len(df) < 30:

            return False

        latest = df.iloc[-1]["close"]

        previous_low = (

            df.iloc[:-1]["low"]

            .tail(20)

            .min()

        )

        return latest < previous_low
        # =====================================================
    # SUPERTREND
    # =====================================================

    def supertrend(
        self,
        df,
        period=10,
        multiplier=3,
    ):

        df = df.copy()

        atr = self.atr(df, period)

        hl2 = (df["high"] + df["low"]) / 2

        upperband = hl2 + multiplier * atr
        lowerband = hl2 - multiplier * atr

        trend = [True]

        supertrend = [lowerband.iloc[0]]

        for i in range(1, len(df)):

            if df["close"].iloc[i] > upperband.iloc[i - 1]:
                trend.append(True)

            elif df["close"].iloc[i] < lowerband.iloc[i - 1]:
                trend.append(False)

            else:
                trend.append(trend[-1])

            if trend[-1]:
                supertrend.append(lowerband.iloc[i])
            else:
                supertrend.append(upperband.iloc[i])

        df["SUPERTREND"] = supertrend
        df["SUPERTREND_DIRECTION"] = trend

        return df

    # =====================================================
    # ICHIMOKU CLOUD
    # =====================================================

    def ichimoku(self, df):

        high9 = df["high"].rolling(9).max()
        low9 = df["low"].rolling(9).min()

        high26 = df["high"].rolling(26).max()
        low26 = df["low"].rolling(26).min()

        high52 = df["high"].rolling(52).max()
        low52 = df["low"].rolling(52).min()

        conversion = (high9 + low9) / 2

        base = (high26 + low26) / 2

        span_a = ((conversion + base) / 2).shift(26)

        span_b = ((high52 + low52) / 2).shift(26)

        lagging = df["close"].shift(-26)

        return {

            "conversion": conversion,

            "base": base,

            "span_a": span_a,

            "span_b": span_b,

            "lagging": lagging,

        }

    # =====================================================
    # STOCHASTIC RSI
    # =====================================================

    def stochastic_rsi(
        self,
        series,
        period=14,
    ):

        rsi = self.rsi(series, period)

        lowest = rsi.rolling(period).min()

        highest = rsi.rolling(period).max()

        return (

            (rsi - lowest)

            /

            (highest - lowest)

        ) * 100

    # =====================================================
    # CPR
    # =====================================================

    def cpr(self, df):

        pivot = (

            df["high"]

            + df["low"]

            + df["close"]

        ) / 3

        bc = (

            df["high"]

            + df["low"]

        ) / 2

        tc = pivot * 2 - bc

        return {

            "pivot": pivot,

            "bc": bc,

            "tc": tc,

        }

    # =====================================================
    # CLASSIC PIVOTS
    # =====================================================

    def pivot_points(self, df):

        pivot = (

            df["high"]

            + df["low"]

            + df["close"]

        ) / 3

        r1 = (2 * pivot) - df["low"]

        s1 = (2 * pivot) - df["high"]

        r2 = pivot + (

            df["high"]

            - df["low"]

        )

        s2 = pivot - (

            df["high"]

            - df["low"]

        )

        return {

            "pivot": pivot,

            "r1": r1,

            "r2": r2,

            "s1": s1,

            "s2": s2,

        }

    # =====================================================
    # OPENING RANGE
    # =====================================================

    def opening_range(
        self,
        df,
        minutes=15,
    ):

        if df.empty:
            return None

        candles = max(1, minutes // 5)

        opening = df.head(candles)

        return {

            "high": opening["high"].max(),

            "low": opening["low"].min(),

        }

    # =====================================================
    # 52 WEEK LEVELS
    # =====================================================

    def fifty_two_week_levels(
        self,
        df,
    ):

        if df.empty:

            return None

        return {

            "high": df["high"].tail(252).max(),

            "low": df["low"].tail(252).min(),

        }

    # =====================================================
    # VOLUME SPIKE
    # =====================================================

    def volume_spike(
        self,
        df,
        multiplier=2,
    ):

        average = (

            df["volume"]

            .rolling(20)

            .mean()

        )

        return (

            df["volume"]

            >

            average * multiplier

        )

    # =====================================================
    # EMA TREND
    # =====================================================

    def ema_trend(
        self,
        df,
    ):

        latest = df.iloc[-1]

        return (

            latest["EMA20"]

            >

            latest["EMA50"]

            >

            latest["EMA200"]

        )

    # =====================================================
    # GOLDEN CROSS
    # =====================================================

    def golden_cross(
        self,
        df,
    ):

        if len(df) < 2:

            return False

        prev = df.iloc[-2]

        curr = df.iloc[-1]

        return (

            prev["EMA50"] <= prev["EMA200"]

            and

            curr["EMA50"] > curr["EMA200"]

        )

    # =====================================================
    # DEATH CROSS
    # =====================================================

    def death_cross(
        self,
        df,
    ):

        if len(df) < 2:

            return False

        prev = df.iloc[-2]

        curr = df.iloc[-1]

        return (

            prev["EMA50"] >= prev["EMA200"]

            and

            curr["EMA50"] < curr["EMA200"]

        )
        # =====================================================
    # SYMBOL VALIDATION
    # =====================================================

    def validate_symbol(self, symbol):

        try:

            df = self.download_symbol(

                symbol,

                interval="1d",

                period="5d",

            )

            return not df.empty

        except Exception:

            return False

    # =====================================================
    # VALIDATE SYMBOL LIST
    # =====================================================

    def validate_symbols(self, symbols):

        valid = []

        invalid = []

        for symbol in symbols:

            if self.validate_symbol(symbol):

                valid.append(symbol)

            else:

                invalid.append(symbol)

        return valid, invalid

    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    def remove_duplicate_symbols(self, symbols):

        return sorted(

            list(

                dict.fromkeys(symbols)

            )

        )

    # =====================================================
    # DATA CLEANUP
    # =====================================================

    def clean_dataframe(self, df):

        if df.empty:

            return df

        df = df.copy()

        df.drop_duplicates(inplace=True)

        df.dropna(how="all", inplace=True)

        df.reset_index(

            drop=True,

            inplace=True,

        )

        return df

    # =====================================================
    # GET LAST UPDATE
    # =====================================================

    def last_update(self):

        return datetime.now().strftime(

            "%d-%m-%Y %H:%M:%S"

        )

    # =====================================================
    # MARKET SESSION
    # =====================================================

    def market_session(self):

        if not self.market_open():

            return "Closed"

        now = datetime.now()

        current = now.hour * 60 + now.minute

        if current <= 9 * 60 + 45:

            return "Opening"

        if current <= 14 * 60 + 30:

            return "Regular"

        return "Closing"

    # =====================================================
    # SYSTEM STATUS
    # =====================================================

    def status(self):

        return {

            "running": self.running,

            "market_open": self.market_open(),

            "session": self.market_session(),

            "cached_items": len(self.cache),

            "workers": self.download_workers,

            "last_update": self.last_update(),

        }

    # =====================================================
    # CACHE INFO
    # =====================================================

    def cache_info(self):

        return {

            "items": len(self.cache),

            "timeout": self.CACHE_TIMEOUT,

        }

    # =====================================================
    # EXPORT CACHE
    # =====================================================

    def export_cache(self):

        return {

            key: len(value)

            for key, value in self.cache.items()

        }

    # =====================================================
    # REFRESH EVERYTHING
    # =====================================================

    def refresh_all(

        self,

        symbols,

    ):

        self.clear_cache()

        return self.download_parallel(

            symbols,

            self.default_interval,

            self.default_period,

        )

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(self):

        self.stop_live_updates()

        self.clear_cache()

        self.logger.info(

            "MarketDataService shutdown complete."

        )

    # =====================================================
    # STRING REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (

            f"<MarketDataService "

            f"cache={len(self.cache)} "

            f"workers={self.download_workers} "

            f"running={self.running}>"

        )


# ==========================================================
# END OF FILE
# ==========================================================