"""
=========================================================
StockVersity Scanner Pro
Indicator Engine
Version : 2.0
=========================================================

Centralized indicator calculation engine.

Purpose
-------
This engine calculates all technical indicators once and
shares them across all scanners.

Supported Indicators
--------------------
✔ EMA
✔ SMA
✔ RSI
✔ MACD
✔ ATR
✔ ADX
✔ VWAP
✔ Supertrend
✔ Bollinger Bands
✔ Stochastic RSI
✔ Highest High
✔ Lowest Low
✔ Volume SMA

Features
--------
✔ Multi-timeframe support
✔ Shared cache
✔ Lazy loading
✔ Batch calculation
✔ Thread-safe
✔ Performance monitoring
✔ Automatic cache management
"""

from __future__ import annotations

from datetime import datetime
from threading import Lock
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import pandas as pd

from core.indicators.adx import ADXIndicator
from core.indicators.atr import ATRIndicator
from core.indicators.ema import EMAIndicator
from core.indicators.macd import MACDIndicator
from core.indicators.rsi import RSIIndicator
from core.indicators.vwap import VWAPIndicator


class IndicatorEngine:
    """
    Central indicator calculation engine.

    All scanners request indicators through this class
    instead of calculating them individually.

    Example
    -------

    engine.get_ema(
        "RELIANCE",
        "15m",
        df,
        20,
    )

    engine.get_rsi(
        "RELIANCE",
        "15m",
        df,
    )
    """

    VERSION = "2.0"

    def __init__(
        self,
    ) -> None:

        # ---------------------------------
        # CACHE
        # ---------------------------------

        self.cache: Dict[
            str,
            Any,
        ] = {}

        self.market_data: Dict[
            str,
            pd.DataFrame,
        ] = {}

        # ---------------------------------
        # THREAD SAFETY
        # ---------------------------------

        self.lock = Lock()

        # ---------------------------------
        # STATISTICS
        # ---------------------------------

        self.cache_hits = 0

        self.cache_misses = 0

        self.total_requests = 0

        self.total_calculations = 0

        self.started = datetime.now()

        # ---------------------------------
        # INDICATOR OBJECTS
        # ---------------------------------

        self.ema = EMAIndicator(20)

        self.rsi = RSIIndicator()

        self.macd = MACDIndicator()

        self.atr = ATRIndicator()

        self.adx = ADXIndicator()

        self.vwap = VWAPIndicator()

    # =====================================================
    # CACHE KEY
    # =====================================================

    def _key(

        self,

        symbol: str,

        timeframe: str,

        indicator: str,

        *args: Any,

    ) -> str:

        values = [

            symbol.upper(),

            timeframe,

            indicator,

        ]

        values.extend(

            str(arg)

            for arg in args

        )

        return "|".join(values)

    # =====================================================
    # RESET
    # =====================================================

    def reset(
        self,
    ) -> None:

        with self.lock:

            self.cache.clear()

            self.market_data.clear()

            self.cache_hits = 0

            self.cache_misses = 0

            self.total_requests = 0

            self.total_calculations = 0

            self.started = datetime.now()
                # =====================================================
    # CACHE LOOKUP
    # =====================================================

    def _get_cached(
        self,
        key: str,
    ) -> Optional[Any]:
        """
        Retrieve a value from cache.
        """

        self.total_requests += 1

        value = self.cache.get(key)

        if value is None:

            self.cache_misses += 1

            return None

        self.cache_hits += 1

        return value

    # =====================================================
    # CACHE STORE
    # =====================================================

    def _store_cache(
        self,
        key: str,
        value: Any,
    ) -> Any:
        """
        Store value in cache.
        """

        self.cache[key] = value

        self.total_calculations += 1

        return value

    # =====================================================
    # CACHE EXISTS
    # =====================================================

    def has_cache(
        self,
        key: str,
    ) -> bool:

        return key in self.cache

    # =====================================================
    # CLEAR CACHE
    # =====================================================

    def clear_cache(
        self,
    ) -> None:

        with self.lock:

            self.cache.clear()

            self.cache_hits = 0

            self.cache_misses = 0

            self.total_requests = 0

            self.total_calculations = 0

    # =====================================================
    # REMOVE CACHE
    # =====================================================

    def remove_cache(
        self,
        symbol: str,
        timeframe: Optional[str] = None,
    ) -> None:
        """
        Remove all cached indicators for a symbol or
        a specific timeframe.
        """

        with self.lock:

            keys = list(self.cache.keys())

            symbol = symbol.upper()

            for key in keys:

                parts = key.split("|")

                if len(parts) < 3:
                    continue

                if parts[0] != symbol:
                    continue

                if timeframe is not None:

                    if parts[1] != timeframe:
                        continue

                self.cache.pop(
                    key,
                    None,
                )

    # =====================================================
    # REGISTER MARKET DATA
    # =====================================================

    def register_data(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
    ) -> None:
        """
        Register OHLCV data for later use.
        """

        key = self._key(

            symbol,

            timeframe,

            "DATA",

        )

        self.market_data[key] = dataframe

    # =====================================================
    # GET MARKET DATA
    # =====================================================

    def get_data(
        self,
        symbol: str,
        timeframe: str,
    ) -> Optional[pd.DataFrame]:
        """
        Retrieve registered OHLCV data.
        """

        key = self._key(

            symbol,

            timeframe,

            "DATA",

        )

        return self.market_data.get(key)

    # =====================================================
    # DATA EXISTS
    # =====================================================

    def has_data(
        self,
        symbol: str,
        timeframe: str,
    ) -> bool:

        return (

            self.get_data(

                symbol,

                timeframe,

            )

            is not None

        )

    # =====================================================
    # CACHE STATISTICS
    # =====================================================

    def cache_statistics(
        self,
    ) -> Dict[str, Any]:

        hit_rate = 0.0

        if self.total_requests:

            hit_rate = (

                self.cache_hits

                / self.total_requests

            ) * 100

        return {

            "cache_size": len(

                self.cache

            ),

            "hits": self.cache_hits,

            "misses": self.cache_misses,

            "requests": self.total_requests,

            "calculations": self.total_calculations,

            "hit_rate": round(

                hit_rate,

                2,

            ),

        }

    # =====================================================
    # INVALIDATE SYMBOL
    # =====================================================

    def invalidate_symbol(
        self,
        symbol: str,
    ) -> None:
        """
        Remove all cached data belonging to a symbol.
        """

        self.remove_cache(
            symbol=symbol
        )

    # =====================================================
    # INVALIDATE ALL
    # =====================================================

    def invalidate_all(
        self,
    ) -> None:
        """
        Clear the complete cache.
        """

        self.clear_cache()
            # =====================================================
    # EMA
    # =====================================================

    def get_ema(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
        period: int = 20,
    ) -> pd.Series:
        """
        Get EMA with caching.
        """

        key = self._key(
            symbol,
            timeframe,
            "EMA",
            period,
        )

        cached = self._get_cached(key)

        if cached is not None:
            return cached

        value = self.ema.calculate(
            dataframe,
            period,
        )

        return self._store_cache(
            key,
            value,
        )

    # =====================================================
    # SMA
    # =====================================================

    def get_sma(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
        period: int = 20,
    ) -> pd.Series:
        """
        Calculate SMA with caching.
        """

        key = self._key(
            symbol,
            timeframe,
            "SMA",
            period,
        )

        cached = self._get_cached(key)

        if cached is not None:
            return cached

        value = dataframe["close"].rolling(
            window=period,
            min_periods=period,
        ).mean()

        return self._store_cache(
            key,
            value,
        )

    # =====================================================
    # RSI
    # =====================================================

    def get_rsi(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
        period: int = 14,
    ) -> pd.Series:
        """
        Get RSI with caching.
        """

        key = self._key(
            symbol,
            timeframe,
            "RSI",
            period,
        )

        cached = self._get_cached(key)

        if cached is not None:
            return cached

        value = self.rsi.calculate(
            dataframe,
            period,
        )

        return self._store_cache(
            key,
            value,
        )

    # =====================================================
    # MACD
    # =====================================================

    def get_macd(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9,
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Get MACD, Signal and Histogram.
        """

        key = self._key(
            symbol,
            timeframe,
            "MACD",
            fast,
            slow,
            signal,
        )

        cached = self._get_cached(key)

        if cached is not None:
            return cached

        value = self.macd.calculate(
            dataframe,
            fast=fast,
            slow=slow,
            signal=signal,
        )

        return self._store_cache(
            key,
            value,
        )

    # =====================================================
    # ATR
    # =====================================================

    def get_atr(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
        period: int = 14,
    ) -> pd.Series:
        """
        Get ATR with caching.
        """

        key = self._key(
            symbol,
            timeframe,
            "ATR",
            period,
        )

        cached = self._get_cached(key)

        if cached is not None:
            return cached

        value = self.atr.calculate(
            dataframe,
            period,
        )

        return self._store_cache(
            key,
            value,
        )

    # =====================================================
    # ADX
    # =====================================================

    def get_adx(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
        period: int = 14,
    ) -> pd.Series:
        """
        Get ADX with caching.
        """

        key = self._key(
            symbol,
            timeframe,
            "ADX",
            period,
        )

        cached = self._get_cached(key)

        if cached is not None:
            return cached

        value = self.adx.calculate(
            dataframe,
            period,
        )

        return self._store_cache(
            key,
            value,
        )

    # =====================================================
    # VWAP
    # =====================================================

    def get_vwap(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
    ) -> pd.Series:
        """
        Get VWAP with caching.
        """

        key = self._key(
            symbol,
            timeframe,
            "VWAP",
        )

        cached = self._get_cached(key)

        if cached is not None:
            return cached

        value = self.vwap.calculate(
            dataframe,
        )

        return self._store_cache(
            key,
            value,
        )
        # =====================================================
    # SUPERTREND
    # =====================================================

    def get_supertrend(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
        period: int = 10,
        multiplier: float = 3.0,
    ) -> pd.DataFrame:
        """
        Calculate Supertrend.
        Returns a DataFrame with:
        - supertrend
        - upper_band
        - lower_band
        - direction
        """

        key = self._key(
            symbol,
            timeframe,
            "SUPERTREND",
            period,
            multiplier,
        )

        cached = self._get_cached(key)

        if cached is not None:
            return cached

        atr = self.get_atr(
            symbol,
            timeframe,
            dataframe,
            period,
        )

        hl2 = (
            dataframe["high"] +
            dataframe["low"]
        ) / 2.0

        upper = hl2 + multiplier * atr
        lower = hl2 - multiplier * atr

        direction = pd.Series(
            1,
            index=dataframe.index,
            dtype="int64",
        )

        supertrend = upper.copy()

        for i in range(1, len(dataframe)):

            if dataframe["close"].iloc[i] > upper.iloc[i - 1]:

                direction.iloc[i] = 1

            elif dataframe["close"].iloc[i] < lower.iloc[i - 1]:

                direction.iloc[i] = -1

            else:

                direction.iloc[i] = direction.iloc[i - 1]

                if (
                    direction.iloc[i] == 1
                    and lower.iloc[i] < lower.iloc[i - 1]
                ):
                    lower.iloc[i] = lower.iloc[i - 1]

                if (
                    direction.iloc[i] == -1
                    and upper.iloc[i] > upper.iloc[i - 1]
                ):
                    upper.iloc[i] = upper.iloc[i - 1]

            supertrend.iloc[i] = (

                lower.iloc[i]

                if direction.iloc[i] == 1

                else upper.iloc[i]

            )

        value = pd.DataFrame(

            {

                "supertrend": supertrend,

                "upper_band": upper,

                "lower_band": lower,

                "direction": direction,

            }

        )

        return self._store_cache(
            key,
            value,
        )

    # =====================================================
    # BOLLINGER BANDS
    # =====================================================

    def get_bollinger_bands(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
        period: int = 20,
        deviation: float = 2.0,
    ) -> pd.DataFrame:
        """
        Calculate Bollinger Bands.
        """

        key = self._key(

            symbol,

            timeframe,

            "BOLLINGER",

            period,

            deviation,

        )

        cached = self._get_cached(key)

        if cached is not None:

            return cached

        middle = dataframe["close"].rolling(
            period
        ).mean()

        std = dataframe["close"].rolling(
            period
        ).std()

        upper = middle + (std * deviation)

        lower = middle - (std * deviation)

        value = pd.DataFrame(

            {

                "upper": upper,

                "middle": middle,

                "lower": lower,

                "width": upper - lower,

            }

        )

        return self._store_cache(
            key,
            value,
        )

    # =====================================================
    # STOCHASTIC RSI
    # =====================================================

    def get_stochastic_rsi(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
        period: int = 14,
    ) -> pd.Series:
        """
        Calculate Stochastic RSI.
        """

        key = self._key(

            symbol,

            timeframe,

            "STOCH_RSI",

            period,

        )

        cached = self._get_cached(key)

        if cached is not None:

            return cached

        rsi = self.get_rsi(

            symbol,

            timeframe,

            dataframe,

            period,

        )

        lowest = rsi.rolling(
            period
        ).min()

        highest = rsi.rolling(
            period
        ).max()

        value = (
            (rsi - lowest)
            /
            (highest - lowest)
        ) * 100

        return self._store_cache(
            key,
            value,
        )

    # =====================================================
    # HIGHEST HIGH
    # =====================================================

    def get_highest_high(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
        period: int = 20,
    ) -> pd.Series:
        """
        Rolling highest high.
        """

        key = self._key(

            symbol,

            timeframe,

            "HIGHEST_HIGH",

            period,

        )

        cached = self._get_cached(key)

        if cached is not None:

            return cached

        value = dataframe["high"].rolling(
            period
        ).max()

        return self._store_cache(
            key,
            value,
        )

    # =====================================================
    # LOWEST LOW
    # =====================================================

    def get_lowest_low(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
        period: int = 20,
    ) -> pd.Series:
        """
        Rolling lowest low.
        """

        key = self._key(

            symbol,

            timeframe,

            "LOWEST_LOW",

            period,

        )

        cached = self._get_cached(key)

        if cached is not None:

            return cached

        value = dataframe["low"].rolling(
            period
        ).min()

        return self._store_cache(
            key,
            value,
        )

    # =====================================================
    # VOLUME SMA
    # =====================================================

    def get_volume_sma(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
        period: int = 20,
    ) -> pd.Series:
        """
        Moving average of volume.
        """

        key = self._key(

            symbol,

            timeframe,

            "VOLUME_SMA",

            period,

        )

        cached = self._get_cached(key)

        if cached is not None:

            return cached

        value = dataframe["volume"].rolling(
            period
        ).mean()

        return self._store_cache(
            key,
            value,
        )
        # =====================================================
    # INDICATOR BUNDLE
    # =====================================================

    def indicator_bundle(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        Calculate the most commonly used indicators
        for institutional scanners.
        """

        return {

            "ema9": self.get_ema(
                symbol,
                timeframe,
                dataframe,
                9,
            ),

            "ema20": self.get_ema(
                symbol,
                timeframe,
                dataframe,
                20,
            ),

            "ema21": self.get_ema(
                symbol,
                timeframe,
                dataframe,
                21,
            ),

            "ema50": self.get_ema(
                symbol,
                timeframe,
                dataframe,
                50,
            ),

            "ema100": self.get_ema(
                symbol,
                timeframe,
                dataframe,
                100,
            ),

            "ema200": self.get_ema(
                symbol,
                timeframe,
                dataframe,
                200,
            ),

            "rsi": self.get_rsi(
                symbol,
                timeframe,
                dataframe,
            ),

            "macd": self.get_macd(
                symbol,
                timeframe,
                dataframe,
            ),

            "atr": self.get_atr(
                symbol,
                timeframe,
                dataframe,
            ),

            "adx": self.get_adx(
                symbol,
                timeframe,
                dataframe,
            ),

            "vwap": self.get_vwap(
                symbol,
                timeframe,
                dataframe,
            ),

            "supertrend": self.get_supertrend(
                symbol,
                timeframe,
                dataframe,
            ),

            "bollinger": self.get_bollinger_bands(
                symbol,
                timeframe,
                dataframe,
            ),

            "stoch_rsi": self.get_stochastic_rsi(
                symbol,
                timeframe,
                dataframe,
            ),

            "highest20": self.get_highest_high(
                symbol,
                timeframe,
                dataframe,
                20,
            ),

            "lowest20": self.get_lowest_low(
                symbol,
                timeframe,
                dataframe,
                20,
            ),

            "volume_sma20": self.get_volume_sma(
                symbol,
                timeframe,
                dataframe,
                20,
            ),

        }

    # =====================================================
    # PRELOAD
    # =====================================================

    def preload(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
    ) -> None:
        """
        Warm up the cache by calculating the
        standard indicator bundle.
        """

        self.indicator_bundle(

            symbol,

            timeframe,

            dataframe,

        )

    # =====================================================
    # PRELOAD MULTIPLE SYMBOLS
    # =====================================================

    def preload_many(
        self,
        market_data: Dict[
            str,
            pd.DataFrame,
        ],
        timeframe: str,
    ) -> None:
        """
        Preload indicators for multiple symbols.
        """

        for symbol, dataframe in market_data.items():

            self.preload(

                symbol,

                timeframe,

                dataframe,

            )

    # =====================================================
    # MULTI-TIMEFRAME BUNDLE
    # =====================================================

    def multi_timeframe_bundle(
        self,
        symbol: str,
        datasets: Dict[
            str,
            pd.DataFrame,
        ],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate indicator bundles across
        multiple timeframes.

        Example:

        {
            "5m": {...},
            "15m": {...},
            "1h": {...},
            "1d": {...}
        }
        """

        output: Dict[
            str,
            Dict[str, Any],
        ] = {}

        for timeframe, dataframe in datasets.items():

            output[timeframe] = self.indicator_bundle(

                symbol,

                timeframe,

                dataframe,

            )

        return output

    # =====================================================
    # CALCULATE ALL
    # =====================================================

    def calculate_all(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        Alias for indicator_bundle().
        """

        return self.indicator_bundle(

            symbol,

            timeframe,

            dataframe,

        )

    # =====================================================
    # CALCULATE MARKET
    # =====================================================

    def calculate_market(
        self,
        market: Dict[
            str,
            pd.DataFrame,
        ],
        timeframe: str,
    ) -> Dict[
        str,
        Dict[str, Any],
    ]:
        """
        Calculate indicators for an entire market.
        """

        result: Dict[
            str,
            Dict[str, Any],
        ] = {}

        for symbol, dataframe in market.items():

            result[symbol] = self.indicator_bundle(

                symbol,

                timeframe,

                dataframe,

            )

        return result
        # =====================================================
    # LATEST EMA
    # =====================================================

    def latest_ema(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
        period: int,
    ) -> float:
        """
        Return the latest EMA value.
        """

        ema = self.get_ema(
            symbol,
            timeframe,
            dataframe,
            period,
        )

        return float(ema.iloc[-1])

    # =====================================================
    # LATEST RSI
    # =====================================================

    def latest_rsi(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
        period: int = 14,
    ) -> float:

        rsi = self.get_rsi(
            symbol,
            timeframe,
            dataframe,
            period,
        )

        return float(rsi.iloc[-1])

    # =====================================================
    # LATEST ATR
    # =====================================================

    def latest_atr(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
        period: int = 14,
    ) -> float:

        atr = self.get_atr(
            symbol,
            timeframe,
            dataframe,
            period,
        )

        return float(atr.iloc[-1])

    # =====================================================
    # LATEST ADX
    # =====================================================

    def latest_adx(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
        period: int = 14,
    ) -> float:

        adx = self.get_adx(
            symbol,
            timeframe,
            dataframe,
            period,
        )

        return float(adx.iloc[-1])

    # =====================================================
    # LATEST VWAP
    # =====================================================

    def latest_vwap(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
    ) -> float:

        vwap = self.get_vwap(
            symbol,
            timeframe,
            dataframe,
        )

        return float(vwap.iloc[-1])

    # =====================================================
    # LATEST MACD
    # =====================================================

    def latest_macd(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
    ) -> Tuple[float, float, float]:
        """
        Returns:
        (MACD, Signal, Histogram)
        """

        macd, signal, histogram = self.get_macd(
            symbol,
            timeframe,
            dataframe,
        )

        return (

            float(macd.iloc[-1]),

            float(signal.iloc[-1]),

            float(histogram.iloc[-1]),

        )

    # =====================================================
    # EMA ALIGNMENT
    # =====================================================

    def ema_alignment(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
    ) -> bool:
        """
        Bullish institutional EMA alignment.

        EMA21 > EMA50 > EMA200
        """

        ema21 = self.latest_ema(
            symbol,
            timeframe,
            dataframe,
            21,
        )

        ema50 = self.latest_ema(
            symbol,
            timeframe,
            dataframe,
            50,
        )

        ema200 = self.latest_ema(
            symbol,
            timeframe,
            dataframe,
            200,
        )

        return (

            ema21 >

            ema50 >

            ema200

        )

    # =====================================================
    # PRICE ABOVE EMA
    # =====================================================

    def price_above_ema(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
        period: int = 21,
    ) -> bool:

        return (

            dataframe["close"].iloc[-1]

            >

            self.latest_ema(

                symbol,

                timeframe,

                dataframe,

                period,

            )

        )

    # =====================================================
    # PRICE ABOVE VWAP
    # =====================================================

    def price_above_vwap(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
    ) -> bool:

        return (

            dataframe["close"].iloc[-1]

            >

            self.latest_vwap(

                symbol,

                timeframe,

                dataframe,

            )

        )

    # =====================================================
    # STRONG TREND
    # =====================================================

    def strong_trend(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
        minimum_adx: float = 25.0,
    ) -> bool:
        """
        ADX-based trend strength.
        """

        return (

            self.latest_adx(

                symbol,

                timeframe,

                dataframe,

            )

            >= minimum_adx

        )
        # =====================================================
    # MACD BULLISH CROSSOVER
    # =====================================================

    def macd_bullish_crossover(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
    ) -> bool:
        """
        MACD crosses above Signal.
        """

        macd, signal, _ = self.get_macd(
            symbol,
            timeframe,
            dataframe,
        )

        if len(macd) < 2:
            return False

        return (
            macd.iloc[-2] <= signal.iloc[-2]
            and
            macd.iloc[-1] > signal.iloc[-1]
        )

    # =====================================================
    # MACD BEARISH CROSSOVER
    # =====================================================

    def macd_bearish_crossover(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
    ) -> bool:

        macd, signal, _ = self.get_macd(
            symbol,
            timeframe,
            dataframe,
        )

        if len(macd) < 2:
            return False

        return (
            macd.iloc[-2] >= signal.iloc[-2]
            and
            macd.iloc[-1] < signal.iloc[-1]
        )

    # =====================================================
    # RSI BULLISH
    # =====================================================

    def rsi_bullish(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
        level: float = 55.0,
    ) -> bool:

        return (

            self.latest_rsi(
                symbol,
                timeframe,
                dataframe,
            )

            >= level

        )

    # =====================================================
    # RSI BEARISH
    # =====================================================

    def rsi_bearish(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
        level: float = 45.0,
    ) -> bool:

        return (

            self.latest_rsi(
                symbol,
                timeframe,
                dataframe,
            )

            <= level

        )

    # =====================================================
    # VOLUME EXPANSION
    # =====================================================

    def volume_expansion(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
        multiplier: float = 2.0,
        period: int = 20,
    ) -> bool:
        """
        Detect unusually high volume.
        """

        volume_sma = self.get_volume_sma(
            symbol,
            timeframe,
            dataframe,
            period,
        )

        latest_volume = float(
            dataframe["volume"].iloc[-1]
        )

        latest_average = float(
            volume_sma.iloc[-1]
        )

        if latest_average <= 0:

            return False

        return latest_volume >= (
            latest_average * multiplier
        )

    # =====================================================
    # BREAKOUT
    # =====================================================

    def breakout(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
        lookback: int = 20,
    ) -> bool:
        """
        Close above previous highest high.
        """

        highest = self.get_highest_high(
            symbol,
            timeframe,
            dataframe,
            lookback,
        )

        if len(highest) < 2:

            return False

        previous_high = float(
            highest.iloc[-2]
        )

        return (

            dataframe["close"].iloc[-1]

            >

            previous_high

        )

    # =====================================================
    # BREAKDOWN
    # =====================================================

    def breakdown(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
        lookback: int = 20,
    ) -> bool:
        """
        Close below previous lowest low.
        """

        lowest = self.get_lowest_low(
            symbol,
            timeframe,
            dataframe,
            lookback,
        )

        if len(lowest) < 2:

            return False

        previous_low = float(
            lowest.iloc[-2]
        )

        return (

            dataframe["close"].iloc[-1]

            <

            previous_low

        )

    # =====================================================
    # BOLLINGER SQUEEZE
    # =====================================================

    def bollinger_squeeze(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
        threshold: float = 0.05,
    ) -> bool:
        """
        Detect Bollinger Band squeeze.
        """

        bands = self.get_bollinger_bands(
            symbol,
            timeframe,
            dataframe,
        )

        latest_width = float(
            bands["width"].iloc[-1]
        )

        latest_middle = float(
            bands["middle"].iloc[-1]
        )

        if latest_middle <= 0:

            return False

        return (

            latest_width / latest_middle

            <= threshold

        )

    # =====================================================
    # SUPERTREND BUY
    # =====================================================

    def supertrend_buy(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
    ) -> bool:

        trend = self.get_supertrend(
            symbol,
            timeframe,
            dataframe,
        )

        return bool(
            trend["direction"].iloc[-1] == 1
        )

    # =====================================================
    # SUPERTREND SELL
    # =====================================================

    def supertrend_sell(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
    ) -> bool:

        trend = self.get_supertrend(
            symbol,
            timeframe,
            dataframe,
        )

        return bool(
            trend["direction"].iloc[-1] == -1
        )
        # =====================================================
    # HIGHER HIGH
    # =====================================================

    def higher_high(
        self,
        dataframe: pd.DataFrame,
        lookback: int = 2,
    ) -> bool:
        """
        Latest high is greater than previous high.
        """

        if len(dataframe) < lookback + 1:
            return False

        return (
            dataframe["high"].iloc[-1]
            >
            dataframe["high"].iloc[-2]
        )

    # =====================================================
    # HIGHER LOW
    # =====================================================

    def higher_low(
        self,
        dataframe: pd.DataFrame,
        lookback: int = 2,
    ) -> bool:

        if len(dataframe) < lookback + 1:
            return False

        return (
            dataframe["low"].iloc[-1]
            >
            dataframe["low"].iloc[-2]
        )

    # =====================================================
    # LOWER HIGH
    # =====================================================

    def lower_high(
        self,
        dataframe: pd.DataFrame,
        lookback: int = 2,
    ) -> bool:

        if len(dataframe) < lookback + 1:
            return False

        return (
            dataframe["high"].iloc[-1]
            <
            dataframe["high"].iloc[-2]
        )

    # =====================================================
    # LOWER LOW
    # =====================================================

    def lower_low(
        self,
        dataframe: pd.DataFrame,
        lookback: int = 2,
    ) -> bool:

        if len(dataframe) < lookback + 1:
            return False

        return (
            dataframe["low"].iloc[-1]
            <
            dataframe["low"].iloc[-2]
        )

    # =====================================================
    # UPTREND
    # =====================================================

    def uptrend(
        self,
        dataframe: pd.DataFrame,
    ) -> bool:
        """
        Higher High + Higher Low.
        """

        return (

            self.higher_high(dataframe)

            and

            self.higher_low(dataframe)

        )

    # =====================================================
    # DOWNTREND
    # =====================================================

    def downtrend(
        self,
        dataframe: pd.DataFrame,
    ) -> bool:
        """
        Lower High + Lower Low.
        """

        return (

            self.lower_high(dataframe)

            and

            self.lower_low(dataframe)

        )

    # =====================================================
    # CONSOLIDATION
    # =====================================================

    def consolidation(
        self,
        dataframe: pd.DataFrame,
        candles: int = 10,
        threshold: float = 3.0,
    ) -> bool:
        """
        Detect price consolidation.

        Range % <= threshold.
        """

        if len(dataframe) < candles:

            return False

        recent = dataframe.tail(candles)

        highest = recent["high"].max()

        lowest = recent["low"].min()

        if lowest <= 0:

            return False

        range_percent = (

            (highest - lowest)

            / lowest

        ) * 100

        return range_percent <= threshold

    # =====================================================
    # NR7
    # =====================================================

    def nr7(
        self,
        dataframe: pd.DataFrame,
    ) -> bool:
        """
        Narrowest range in last 7 candles.
        """

        if len(dataframe) < 7:

            return False

        recent = dataframe.tail(7)

        ranges = recent["high"] - recent["low"]

        return ranges.iloc[-1] == ranges.min()

    # =====================================================
    # INSIDE BAR
    # =====================================================

    def inside_bar(
        self,
        dataframe: pd.DataFrame,
    ) -> bool:
        """
        Current candle is inside previous candle.
        """

        if len(dataframe) < 2:

            return False

        previous = dataframe.iloc[-2]

        current = dataframe.iloc[-1]

        return (

            current["high"] <= previous["high"]

            and

            current["low"] >= previous["low"]

        )

    # =====================================================
    # WIDE RANGE CANDLE
    # =====================================================

    def wide_range_candle(
        self,
        dataframe: pd.DataFrame,
        multiplier: float = 1.8,
        period: int = 20,
    ) -> bool:
        """
        Detect institutional momentum candle.
        """

        if len(dataframe) < period + 1:

            return False

        candle_range = (

            dataframe["high"]

            -

            dataframe["low"]

        )

        latest = float(
            candle_range.iloc[-1]
        )

        average = float(

            candle_range.tail(period).mean()

        )

        if average <= 0:

            return False

        return latest >= (

            average * multiplier

        )

    # =====================================================
    # TREND SCORE
    # =====================================================

    def trend_score(
        self,
        symbol: str,
        timeframe: str,
        dataframe: pd.DataFrame,
    ) -> int:
        """
        Institutional trend score (0-100).
        """

        score = 0

        if self.ema_alignment(
            symbol,
            timeframe,
            dataframe,
        ):
            score += 30

        if self.price_above_vwap(
            symbol,
            timeframe,
            dataframe,
        ):
            score += 15

        if self.price_above_ema(
            symbol,
            timeframe,
            dataframe,
            21,
        ):
            score += 15

        if self.strong_trend(
            symbol,
            timeframe,
            dataframe,
        ):
            score += 20

        if self.macd_bullish_crossover(
            symbol,
            timeframe,
            dataframe,
        ):
            score += 10

        if self.rsi_bullish(
            symbol,
            timeframe,
            dataframe,
        ):
            score += 10

        return min(score, 100)
        # =====================================================
    # CACHE HIT RATE
    # =====================================================

    @property
    def cache_hit_rate(
        self,
    ) -> float:
        """
        Cache hit percentage.
        """

        if self.total_requests == 0:

            return 0.0

        return round(

            (self.cache_hits / self.total_requests) * 100,

            2,

        )

    # =====================================================
    # CACHE MISS RATE
    # =====================================================

    @property
    def cache_miss_rate(
        self,
    ) -> float:
        """
        Cache miss percentage.
        """

        if self.total_requests == 0:

            return 0.0

        return round(

            (self.cache_misses / self.total_requests) * 100,

            2,

        )

    # =====================================================
    # MEMORY USAGE
    # =====================================================

    def memory_statistics(
        self,
    ) -> Dict[str, Any]:
        """
        Approximate memory usage statistics.
        """

        return {

            "cached_items": len(self.cache),

            "registered_datasets": len(self.market_data),

            "cache_hits": self.cache_hits,

            "cache_misses": self.cache_misses,

            "requests": self.total_requests,

            "calculations": self.total_calculations,

        }

    # =====================================================
    # REMOVE EXPIRED CACHE
    # =====================================================

    def cleanup_cache(
        self,
        max_items: int = 5000,
    ) -> None:
        """
        Keep cache size under control.

        Current implementation clears the cache if it
        grows beyond the configured threshold.
        """

        if len(self.cache) <= max_items:

            return

        self.clear_cache()

    # =====================================================
    # INDICATOR EXISTS
    # =====================================================

    def has_indicator(
        self,
        symbol: str,
        timeframe: str,
        indicator: str,
        *args: Any,
    ) -> bool:
        """
        Check whether a cached indicator exists.
        """

        key = self._key(

            symbol,

            timeframe,

            indicator,

            *args,

        )

        return key in self.cache

    # =====================================================
    # VALIDATE DATAFRAME
    # =====================================================

    def validate_dataframe(
        self,
        dataframe: pd.DataFrame,
    ) -> bool:
        """
        Validate minimum OHLCV structure.
        """

        required = {

            "open",

            "high",

            "low",

            "close",

            "volume",

        }

        return required.issubset(

            dataframe.columns

        )

    # =====================================================
    # DIAGNOSTICS
    # =====================================================

    def diagnostics(
        self,
    ) -> Dict[str, Any]:
        """
        Complete engine diagnostics.
        """

        return {

            "version": self.VERSION,

            "started": self.started.isoformat(),

            "cache": self.cache_statistics(),

            "memory": self.memory_statistics(),

            "cache_hit_rate": self.cache_hit_rate,

            "cache_miss_rate": self.cache_miss_rate,

        }

    # =====================================================
    # ENGINE STATUS
    # =====================================================

    def status(
        self,
    ) -> Dict[str, Any]:
        """
        Runtime status.
        """

        return {

            "healthy": True,

            "cache_items": len(self.cache),

            "registered_symbols": len(

                self.market_data

            ),

            "requests": self.total_requests,

            "calculations": self.total_calculations,

            "uptime_seconds": round(

                (

                    datetime.now()

                    - self.started

                ).total_seconds(),

                2,

            ),

        }

    # =====================================================
    # ENGINE INFO
    # =====================================================

    def info(
        self,
    ) -> Dict[str, Any]:
        """
        Static engine information.
        """

        return {

            "name": "Indicator Engine",

            "version": self.VERSION,

            "supported_indicators": [

                "EMA",

                "SMA",

                "RSI",

                "MACD",

                "ATR",

                "ADX",

                "VWAP",

                "SUPERTREND",

                "BOLLINGER",

                "STOCHASTIC_RSI",

                "HIGHEST_HIGH",

                "LOWEST_LOW",

                "VOLUME_SMA",

            ],

        }

    # =====================================================
    # EXPORT CACHE
    # =====================================================

    def export_cache(
        self,
    ) -> Dict[str, Any]:
        """
        Export cache metadata.
        """

        return {

            "keys": sorted(

                self.cache.keys()

            ),

            "size": len(

                self.cache

            ),

        }
        # =====================================================
    # MAGIC METHODS
    # =====================================================

    def __len__(
        self,
    ) -> int:
        """
        Number of cached indicators.
        """

        return len(
            self.cache
        )

    def __bool__(
        self,
    ) -> bool:
        """
        Engine has cached indicators.
        """

        return bool(
            self.cache
        )

    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"cache={len(self.cache)}, "

            f"datasets={len(self.market_data)}, "

            f"hit_rate={self.cache_hit_rate:.2f}%)"

        )

    def __str__(
        self,
    ) -> str:

        return (

            f"IndicatorEngine "

            f"[Cache={len(self.cache)} | "

            f"Requests={self.total_requests} | "

            f"Hit Rate={self.cache_hit_rate:.2f}%]"

        )

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(
        self,
    ) -> None:
        """
        Gracefully shutdown the engine.
        """

        self.reset()

    # =====================================================
    # METADATA
    # =====================================================

    @property
    def metadata(
        self,
    ) -> Dict[str, Any]:
        """
        Engine metadata.
        """

        return {

            "name": "StockVersity Indicator Engine",

            "version": self.VERSION,

            "cached_items": len(
                self.cache
            ),

            "registered_datasets": len(
                self.market_data
            ),

            "requests": self.total_requests,

            "calculations": self.total_calculations,

            "cache_hit_rate": self.cache_hit_rate,

        }


# =====================================================
# FACTORY
# =====================================================

def create_indicator_engine() -> IndicatorEngine:
    """
    Create a new IndicatorEngine instance.
    """

    return IndicatorEngine()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "IndicatorEngine",

    "create_indicator_engine",

]


# ==========================
# END OF FILE
# ==========================