"""
=========================================================
                StockVersity Scanner Pro
                     Powered by AI
=========================================================

Yahoo Finance Service

Provides live market data for:

• NIFTY 50
• BANK NIFTY
• SENSEX
• FINNIFTY
• MIDCAP
• INDIA VIX
• GOLD
• SILVER
• USD/INR
• BRENT CRUDE
"""

from __future__ import annotations

from datetime import datetime

import yfinance as yf


class YahooFinanceService:

    # =====================================================
    # INIT
    # =====================================================

    def __init__(self):

        self.last_update = None

        self.timeout = 10

        self.cache = {}

    # =====================================================
    # FETCH SYMBOL
    # =====================================================

    def fetch(self, symbol):

        try:

            ticker = yf.Ticker(symbol)

            info = ticker.fast_info

            price = info.get("lastPrice")

            previous = info.get("previousClose")

            change = 0.0
            percent = 0.0

            if price is not None and previous:

                change = round(price - previous, 2)

                percent = round(

                    (change / previous) * 100,

                    2

                )

            data = {

                "symbol": symbol,

                "price": price,

                "previous_close": previous,

                "change": change,

                "change_percent": percent,

                "updated": datetime.now(),

            }

            self.cache[symbol] = data

            self.last_update = datetime.now()

            return data

        except Exception:

            return {

                "symbol": symbol,

                "price": None,

                "previous_close": None,

                "change": 0,

                "change_percent": 0,

                "updated": datetime.now(),

            }

    # =====================================================
    # INDICES
    # =====================================================

    def get_nifty(self):

        return self.fetch("^NSEI")

    # -----------------------------------------------------

    def get_banknifty(self):

        return self.fetch("^NSEBANK")

    # -----------------------------------------------------

    def get_sensex(self):

        return self.fetch("^BSESN")

    # -----------------------------------------------------

    def get_finnifty(self):

        return self.fetch("^CNXFIN")

    # -----------------------------------------------------

    def get_midcap(self):

        return self.fetch("^NSEMDCP50")

    # -----------------------------------------------------

    def get_gold(self):

        return self.fetch("GC=F")

    # -----------------------------------------------------

    def get_silver(self):

        return self.fetch("SI=F")

    # -----------------------------------------------------

    def get_usdinr(self):

        return self.fetch("INR=X")

    # -----------------------------------------------------

    def get_brent(self):

        return self.fetch("BZ=F")
        # =====================================================
    # INDIA VIX
    # =====================================================

    def get_india_vix(self):

        """
        Yahoo sometimes exposes India VIX using different
        symbols depending on the exchange. Try each until
        one succeeds.
        """

        symbols = [

            "^INDIAVIX",

            "^INDIAVIXN",

            "^VIX"

        ]

        for symbol in symbols:

            data = self.fetch(symbol)

            if data.get("price") is not None:

                return data

        return {

            "symbol": "INDIA_VIX",

            "price": None,

            "change": 0,

            "change_percent": 0,

            "updated": datetime.now(),

        }

    # =====================================================
    # BULK QUOTES
    # =====================================================

    def get_market_snapshot(self):

        return {

            "nifty": self.get_nifty(),

            "banknifty": self.get_banknifty(),

            "sensex": self.get_sensex(),

            "finnifty": self.get_finnifty(),

            "midcap": self.get_midcap(),

            "gold": self.get_gold(),

            "silver": self.get_silver(),

            "usdinr": self.get_usdinr(),

            "brent": self.get_brent(),

            "vix": self.get_india_vix(),

            "updated": datetime.now(),

        }

    # =====================================================
    # HISTORY
    # =====================================================

    def history(

        self,

        symbol,

        period="6mo",

        interval="1d"

    ):

        try:

            ticker = yf.Ticker(symbol)

            data = ticker.history(

                period=period,

                interval=interval

            )

            return data

        except Exception:

            return None

    # =====================================================
    # INTRADAY
    # =====================================================

    def intraday(

        self,

        symbol,

        interval="5m"

    ):

        return self.history(

            symbol,

            period="5d",

            interval=interval

        )

    # =====================================================
    # DAILY
    # =====================================================

    def daily(self, symbol):

        return self.history(

            symbol,

            "6mo",

            "1d"

        )

    # =====================================================
    # WEEKLY
    # =====================================================

    def weekly(self, symbol):

        return self.history(

            symbol,

            "2y",

            "1wk"

        )

    # =====================================================
    # MONTHLY
    # =====================================================

    def monthly(self, symbol):

        return self.history(

            symbol,

            "10y",

            "1mo"

        )

    # =====================================================
    # CACHE
    # =====================================================

    def cached(self, symbol):

        return self.cache.get(symbol)

    # -----------------------------------------------------

    def clear_cache(self):

        self.cache.clear()

    # -----------------------------------------------------

    def cache_size(self):

        return len(self.cache)

    # =====================================================
    # LAST UPDATE
    # =====================================================

    def updated(self):

        return self.last_update
        # =====================================================
    # SYMBOL VALIDATION
    # =====================================================

    def validate_symbol(self, symbol):

        try:

            ticker = yf.Ticker(symbol)

            info = ticker.fast_info

            return info.get("lastPrice") is not None

        except Exception:

            return False

    # =====================================================
    # LIVE QUOTE
    # =====================================================

    def live_quote(self, symbol):

        return self.fetch(symbol)

    # =====================================================
    # SIMPLE MOVING AVERAGE
    # =====================================================

    def sma(

        self,

        symbol,

        period=20

    ):

        data = self.daily(symbol)

        if data is None or len(data) < period:

            return None

        return round(

            data["Close"]

            .rolling(period)

            .mean()

            .iloc[-1],

            2

        )

    # =====================================================
    # EXPONENTIAL MOVING AVERAGE
    # =====================================================

    def ema(

        self,

        symbol,

        period=20

    ):

        data = self.daily(symbol)

        if data is None or len(data) < period:

            return None

        return round(

            data["Close"]

            .ewm(span=period)

            .mean()

            .iloc[-1],

            2

        )

    # =====================================================
    # RSI
    # =====================================================

    def rsi(

        self,

        symbol,

        period=14

    ):

        data = self.daily(symbol)

        if data is None:

            return None

        close = data["Close"]

        delta = close.diff()

        gain = delta.clip(lower=0)

        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(period).mean()

        avg_loss = loss.rolling(period).mean()

        rs = avg_gain / avg_loss

        rsi = 100 - (

            100 / (1 + rs)

        )

        return round(

            rsi.iloc[-1],

            2

        )

    # =====================================================
    # MACD
    # =====================================================

    def macd(

        self,

        symbol,

        fast=12,

        slow=26,

        signal=9

    ):

        data = self.daily(symbol)

        if data is None:

            return None

        close = data["Close"]

        ema_fast = close.ewm(

            span=fast

        ).mean()

        ema_slow = close.ewm(

            span=slow

        ).mean()

        macd_line = ema_fast - ema_slow

        signal_line = macd_line.ewm(

            span=signal

        ).mean()

        histogram = (

            macd_line

            - signal_line

        )

        return {

            "macd":

                round(

                    macd_line.iloc[-1],

                    2

                ),

            "signal":

                round(

                    signal_line.iloc[-1],

                    2

                ),

            "histogram":

                round(

                    histogram.iloc[-1],

                    2

                ),

        }

    # =====================================================
    # ATR
    # =====================================================

    def atr(

        self,

        symbol,

        period=14

    ):

        data = self.daily(symbol)

        if data is None:

            return None

        high = data["High"]

        low = data["Low"]

        close = data["Close"]

        tr = (

            (high - low)

            .combine(

                (high - close.shift()).abs(),

                max

            )

            .combine(

                (low - close.shift()).abs(),

                max

            )

        )

        atr = tr.rolling(period).mean()

        return round(

            atr.iloc[-1],

            2

        )

    # =====================================================
    # AVERAGE VOLUME
    # =====================================================

    def average_volume(

        self,

        symbol,

        period=20

    ):

        data = self.daily(symbol)

        if data is None:

            return None

        return int(

            data["Volume"]

            .rolling(period)

            .mean()

            .iloc[-1]

        )

    # =====================================================
    # RELATIVE VOLUME
    # =====================================================

    def relative_volume(

        self,

        symbol,

        period=20

    ):

        data = self.daily(symbol)

        if data is None:

            return None

        avg = (

            data["Volume"]

            .rolling(period)

            .mean()

            .iloc[-1]

        )

        current = data["Volume"].iloc[-1]

        if avg == 0:

            return None

        return round(

            current / avg,

            2

        )
        # =====================================================
    # TREND DETECTION
    # =====================================================

    def trend(self, symbol):

        ema20 = self.ema(symbol, 20)
        ema50 = self.ema(symbol, 50)
        ema200 = self.ema(symbol, 200)

        if None in (ema20, ema50, ema200):
            return "Unknown"

        if ema20 > ema50 > ema200:
            return "Strong Bullish"

        if ema20 > ema50:
            return "Bullish"

        if ema20 < ema50 < ema200:
            return "Strong Bearish"

        if ema20 < ema50:
            return "Bearish"

        return "Sideways"

    # =====================================================
    # EMA ALIGNMENT
    # =====================================================

    def ema_alignment(self, symbol):

        ema20 = self.ema(symbol, 20)
        ema50 = self.ema(symbol, 50)
        ema200 = self.ema(symbol, 200)

        return {

            "ema20": ema20,

            "ema50": ema50,

            "ema200": ema200,

            "bullish":

                ema20 is not None
                and ema50 is not None
                and ema200 is not None
                and ema20 > ema50 > ema200,

        }

    # =====================================================
    # 52 WEEK HIGH / LOW
    # =====================================================

    def fifty_two_week(self, symbol):

        data = self.history(

            symbol,

            period="1y",

            interval="1d"

        )

        if data is None or data.empty:

            return None

        return {

            "high":

                round(

                    data["High"].max(),

                    2

                ),

            "low":

                round(

                    data["Low"].min(),

                    2

                ),

        }

    # =====================================================
    # DISTANCE FROM 52 WEEK HIGH
    # =====================================================

    def distance_from_high(self, symbol):

        quote = self.live_quote(symbol)

        levels = self.fifty_two_week(symbol)

        if (

            quote["price"] is None

            or levels is None

        ):

            return None

        return round(

            (

                (quote["price"] - levels["high"])

                / levels["high"]

            ) * 100,

            2

        )

    # =====================================================
    # DISTANCE FROM 52 WEEK LOW
    # =====================================================

    def distance_from_low(self, symbol):

        quote = self.live_quote(symbol)

        levels = self.fifty_two_week(symbol)

        if (

            quote["price"] is None

            or levels is None

        ):

            return None

        return round(

            (

                (quote["price"] - levels["low"])

                / levels["low"]

            ) * 100,

            2

        )

    # =====================================================
    # SUPPORT
    # =====================================================

    def support(self, symbol, lookback=20):

        data = self.daily(symbol)

        if data is None or len(data) < lookback:

            return None

        return round(

            data["Low"]

            .tail(lookback)

            .min(),

            2

        )

    # =====================================================
    # RESISTANCE
    # =====================================================

    def resistance(self, symbol, lookback=20):

        data = self.daily(symbol)

        if data is None or len(data) < lookback:

            return None

        return round(

            data["High"]

            .tail(lookback)

            .max(),

            2

        )

    # =====================================================
    # VOLATILITY
    # =====================================================

    def volatility(self, symbol, period=20):

        data = self.daily(symbol)

        if data is None or len(data) < period:

            return None

        returns = (

            data["Close"]

            .pct_change()

        )

        return round(

            returns

            .rolling(period)

            .std()

            .iloc[-1]

            * 100,

            2

        )

    # =====================================================
    # GAP ANALYSIS
    # =====================================================

    def gap_percentage(self, symbol):

        data = self.daily(symbol)

        if data is None or len(data) < 2:

            return None

        today = data.iloc[-1]

        yesterday = data.iloc[-2]

        return round(

            (

                (today["Open"] - yesterday["Close"])

                / yesterday["Close"]

            ) * 100,

            2

        )

    # =====================================================
    # BREAKOUT DETECTION
    # =====================================================

    def breakout(self, symbol, lookback=20):

        data = self.daily(symbol)

        if data is None or len(data) < lookback + 1:

            return False

        highest = (

            data["High"]

            .iloc[-(lookback + 1):-1]

            .max()

        )

        latest_close = data["Close"].iloc[-1]

        return latest_close > highest
        # =====================================================
    # TREND DETECTION
    # =====================================================

    def trend(self, symbol):

        ema20 = self.ema(symbol, 20)
        ema50 = self.ema(symbol, 50)
        ema200 = self.ema(symbol, 200)

        if None in (ema20, ema50, ema200):
            return "Unknown"

        if ema20 > ema50 > ema200:
            return "Strong Bullish"

        if ema20 > ema50:
            return "Bullish"

        if ema20 < ema50 < ema200:
            return "Strong Bearish"

        if ema20 < ema50:
            return "Bearish"

        return "Sideways"

    # =====================================================
    # EMA ALIGNMENT
    # =====================================================

    def ema_alignment(self, symbol):

        ema20 = self.ema(symbol, 20)
        ema50 = self.ema(symbol, 50)
        ema200 = self.ema(symbol, 200)

        return {

            "ema20": ema20,

            "ema50": ema50,

            "ema200": ema200,

            "bullish":

                ema20 is not None
                and ema50 is not None
                and ema200 is not None
                and ema20 > ema50 > ema200,

        }

    # =====================================================
    # 52 WEEK HIGH / LOW
    # =====================================================

    def fifty_two_week(self, symbol):

        data = self.history(

            symbol,

            period="1y",

            interval="1d"

        )

        if data is None or data.empty:

            return None

        return {

            "high":

                round(

                    data["High"].max(),

                    2

                ),

            "low":

                round(

                    data["Low"].min(),

                    2

                ),

        }

    # =====================================================
    # DISTANCE FROM 52 WEEK HIGH
    # =====================================================

    def distance_from_high(self, symbol):

        quote = self.live_quote(symbol)

        levels = self.fifty_two_week(symbol)

        if (

            quote["price"] is None

            or levels is None

        ):

            return None

        return round(

            (

                (quote["price"] - levels["high"])

                / levels["high"]

            ) * 100,

            2

        )

    # =====================================================
    # DISTANCE FROM 52 WEEK LOW
    # =====================================================

    def distance_from_low(self, symbol):

        quote = self.live_quote(symbol)

        levels = self.fifty_two_week(symbol)

        if (

            quote["price"] is None

            or levels is None

        ):

            return None

        return round(

            (

                (quote["price"] - levels["low"])

                / levels["low"]

            ) * 100,

            2

        )

    # =====================================================
    # SUPPORT
    # =====================================================

    def support(self, symbol, lookback=20):

        data = self.daily(symbol)

        if data is None or len(data) < lookback:

            return None

        return round(

            data["Low"]

            .tail(lookback)

            .min(),

            2

        )

    # =====================================================
    # RESISTANCE
    # =====================================================

    def resistance(self, symbol, lookback=20):

        data = self.daily(symbol)

        if data is None or len(data) < lookback:

            return None

        return round(

            data["High"]

            .tail(lookback)

            .max(),

            2

        )

    # =====================================================
    # VOLATILITY
    # =====================================================

    def volatility(self, symbol, period=20):

        data = self.daily(symbol)

        if data is None or len(data) < period:

            return None

        returns = (

            data["Close"]

            .pct_change()

        )

        return round(

            returns

            .rolling(period)

            .std()

            .iloc[-1]

            * 100,

            2

        )

    # =====================================================
    # GAP ANALYSIS
    # =====================================================

    def gap_percentage(self, symbol):

        data = self.daily(symbol)

        if data is None or len(data) < 2:

            return None

        today = data.iloc[-1]

        yesterday = data.iloc[-2]

        return round(

            (

                (today["Open"] - yesterday["Close"])

                / yesterday["Close"]

            ) * 100,

            2

        )

    # =====================================================
    # BREAKOUT DETECTION
    # =====================================================

    def breakout(self, symbol, lookback=20):

        data = self.daily(symbol)

        if data is None or len(data) < lookback + 1:

            return False

        highest = (

            data["High"]

            .iloc[-(lookback + 1):-1]

            .max()

        )

        latest_close = data["Close"].iloc[-1]

        return latest_close > highest
        # =====================================================
    # MARKET STATUS
    # =====================================================

    def market_status(self):

        now = datetime.now()

        current = now.hour * 60 + now.minute

        #
        # NSE Timing
        # 09:15 - 15:30
        #

        if 555 <= current <= 930:

            return "OPEN"

        return "CLOSED"

    # =====================================================
    # BATCH ANALYSIS
    # =====================================================

    def analyze_symbols(

        self,

        symbols

    ):

        results = []

        for symbol in symbols:

            try:

                results.append(

                    self.analyze(symbol)

                )

            except Exception:

                continue

        return results

    # =====================================================
    # EXPORT DATA
    # =====================================================

    def export_data(

        self,

        symbols

    ):

        export = []

        analyses = self.analyze_symbols(

            symbols

        )

        for item in analyses:

            export.append({

                "Symbol":

                    item["symbol"],

                "Price":

                    item["quote"]["price"],

                "Trend":

                    item["trend"],

                "Technical Score":

                    item["technical_score"],

                "RSI":

                    item["rsi"],

                "ATR":

                    item["atr"],

                "Support":

                    item["support"],

                "Resistance":

                    item["resistance"],

                "Risk Reward":

                    item["risk_reward"],

                "Updated":

                    item["updated"],

            })

        return export

    # =====================================================
    # SERVICE HEALTH
    # =====================================================

    def health_check(self):

        try:

            data = self.get_nifty()

            return data.get("price") is not None

        except Exception:

            return False

    # =====================================================
    # SERVICE INFORMATION
    # =====================================================

    def statistics(self):

        return {

            "cached_symbols":

                len(self.cache),

            "last_update":

                self.last_update,

            "market_status":

                self.market_status(),

            "timeout":

                self.timeout,

        }

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        self.clear_cache()

        self.last_update = None

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(self):

        self.reset()

    # =====================================================
    # STRING
    # =====================================================

    def __str__(self):

        return (

            "YahooFinanceService"

        )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (

            f"<YahooFinanceService "

            f"cached={len(self.cache)} "

            f"status={self.market_status()}>"

        )


# ==========================================================
# END OF FILE
# ==========================================================