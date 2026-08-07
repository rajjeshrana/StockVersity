"""
=========================================================
StockVersity Scanner Pro
Data Manager
=========================================================

Central Market Data Manager

Responsibilities
----------------
✔ Historical Data Cache
✔ Live Tick Cache
✔ Multi-Timeframe Storage
✔ Indicator Cache
✔ Batch Downloads
✔ Scanner Feed
✔ Watchlist Feed
✔ Thread Safe
✔ Auto Refresh
✔ Performance Monitoring
"""

from __future__ import annotations

import logging
import threading
from collections import defaultdict
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pandas as pd

from core.indicator_engine import IndicatorEngine
from core.upstox_client import UpstoxClient
from core.scanner.scanner_bootstrap import get_scanner_system


class DataManager:
    """
    Central market data manager.

    All scanners, dashboard widgets and
    indicator calculations should obtain
    their data through this class.
    """

    VERSION = "1.0"

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(

        self,

        client: UpstoxClient,

        indicator_engine: IndicatorEngine,

    ) -> None:

        self.client = client

        self.indicators = indicator_engine

        # ---------------------------------------------
        # Historical Data
        # ---------------------------------------------

        self.data: Dict[
            str,
            Dict[str, pd.DataFrame],
        ] = defaultdict(dict)

        # ---------------------------------------------
        # Latest Tick Cache
        # ---------------------------------------------

        self.live_ticks: Dict[
            str,
            Dict[str, Any],
        ] = {}

        # ---------------------------------------------
        # Watchlists
        # ---------------------------------------------

        self.watchlists: Dict[
            str,
            List[str],
        ] = defaultdict(list)

        # ---------------------------------------------
        # Refresh Tracking
        # ---------------------------------------------

        self.last_refresh: Dict[
            str,
            datetime,
        ] = {}

        # ---------------------------------------------
        # Runtime Statistics
        # ---------------------------------------------

        self.requests = 0

        self.cache_hits = 0

        self.cache_misses = 0

        self.started = datetime.now()

        # ---------------------------------------------
        # Thread Safety
        # ---------------------------------------------

        self.lock = threading.RLock()

        # ---------------------------------------------
        # Logger
        # ---------------------------------------------

        self.logger = logging.getLogger(

            "StockVersity.DataManager"

        )

        self.logger.setLevel(

            logging.INFO

        )

        # ---------------------------------------------
        # Register Tick Callback
        # ---------------------------------------------

        self.client.register_tick_callback(

            self.on_tick

        )

        # STOCKVERSITY_SCANNER_LIVE_WIRING_V1
        try:
            self.client.register_tick_callback(
                self._forward_tick_to_scanner
            )
            self.logger.info(
                "Scanner live market-data callback registered."
            )
        except Exception:
            self.logger.exception(
                "Unable to register scanner live-data callback."
            )

    # =====================================================
    # SCANNER LIVE MARKET DATA BRIDGE
    # =====================================================

    def _forward_tick_to_scanner(
        self,
        tick,
    ) -> None:
        """Forward one existing Upstox live tick to the shared scanner."""

        try:
            if tick is None:
                return

            if isinstance(tick, dict):
                quote = dict(tick)
            elif hasattr(tick, "to_dict"):
                quote = tick.to_dict()
            elif hasattr(tick, "__dict__"):
                quote = {
                    key: value
                    for key, value in vars(tick).items()
                    if not key.startswith("_")
                }
            else:
                return

            if not quote:
                return

            scanner_system = get_scanner_system()

            if not getattr(scanner_system, "initialized", False):
                scanner_system.initialize()

            scanner_system.update_market_quotes(
                [quote],
                trigger_scan=False,
            )

        except Exception:
            self.logger.exception(
                "Scanner live tick forwarding failed."
            )

    # =====================================================
    # STORE DATAFRAME
    # =====================================================

    def set_data(

        self,

        instrument_key: str,

        timeframe: str,

        dataframe: pd.DataFrame,

    ) -> None:
        """
        Store OHLCV dataframe.
        """

        with self.lock:

            self.data[

                instrument_key

            ][

                timeframe

            ] = dataframe.copy()

            self.last_refresh[

                f"{instrument_key}:{timeframe}"

            ] = datetime.now()

        self._forward_history_to_scanner(
            instrument_key,
            timeframe,
            dataframe,
        )

    # =====================================================
    # FORWARD HISTORICAL DATA TO SHARED SCANNER
    # =====================================================

    def _forward_history_to_scanner(
        self,
        instrument_key: str,
        timeframe: str,
        dataframe: pd.DataFrame,
    ) -> None:
        """Forward an existing OHLCV DataFrame to the shared scanner."""

        try:
            if dataframe is None or dataframe.empty:
                return

            scanner_system = get_scanner_system()

            if not getattr(scanner_system, "initialized", False):
                scanner_system.initialize()

            records = []

            for index, row in dataframe.iterrows():
                timestamp = row.get("timestamp", row.get("time", row.get("datetime", index)))
                records.append({
                    "timestamp": timestamp,
                    "open": row.get("open", row.get("Open", 0.0)),
                    "high": row.get("high", row.get("High", 0.0)),
                    "low": row.get("low", row.get("Low", 0.0)),
                    "close": row.get("close", row.get("Close", 0.0)),
                    "volume": row.get("volume", row.get("Volume", 0)),
                })

            if not records:
                return

            scanner_system.add_candles(
                instrument_key,
                timeframe,
                records,
                max_candles=500,
            )

        except Exception:
            self.logger.exception(
                "Scanner historical candle forwarding failed."
            )

    # =====================================================
    # GET DATAFRAME
    # =====================================================

    def get_data(

        self,

        instrument_key: str,

        timeframe: str,

    ) -> Optional[pd.DataFrame]:
        """
        Return cached dataframe.
        """

        with self.lock:

            timeframe_map = self.data.get(

                instrument_key

            )

            if timeframe_map is None:

                self.cache_misses += 1

                return None

            dataframe = timeframe_map.get(

                timeframe

            )

            if dataframe is None:

                self.cache_misses += 1

                return None

            self.cache_hits += 1

            return dataframe.copy()

    # =====================================================
    # HAS DATA
    # =====================================================

    def has_data(

        self,

        instrument_key: str,

        timeframe: str,

    ) -> bool:

        return (

            instrument_key in self.data

            and timeframe in self.data[

                instrument_key

            ]

        )

    # =====================================================
    # REMOVE DATA
    # =====================================================

    def remove_data(

        self,

        instrument_key: str,

        timeframe: str,

    ) -> None:

        with self.lock:

            if (

                instrument_key in self.data

                and timeframe in self.data[

                    instrument_key

                ]

            ):

                del self.data[

                    instrument_key

                ][

                    timeframe

                ]
                    # =====================================================
    # LOAD HISTORICAL DATA
    # =====================================================

    def load_history(

        self,

        instrument_key: str,

        timeframe: str,

        from_date: str,

        to_date: str,

        force: bool = False,

    ) -> pd.DataFrame:
        """
        Load historical data from Upstox.
        """

        if (

            not force

            and self.has_data(

                instrument_key,

                timeframe,

            )

        ):

            cached = self.get_data(

                instrument_key,

                timeframe,

            )

            if cached is not None:

                return cached

        dataframe = self.client.historical_data(

            instrument_key=instrument_key,

            interval=timeframe,

            from_date=from_date,

            to_date=to_date,

        )

        self.set_data(

            instrument_key,

            timeframe,

            dataframe,

        )

        self.requests += 1

        return dataframe.copy()

    # =====================================================
    # REFRESH DATA
    # =====================================================

    def refresh_data(

        self,

        instrument_key: str,

        timeframe: str,

        from_date: str,

        to_date: str,

    ) -> pd.DataFrame:
        """
        Force refresh historical data.
        """

        return self.load_history(

            instrument_key,

            timeframe,

            from_date,

            to_date,

            force=True,

        )

    # =====================================================
    # LOAD MULTIPLE TIMEFRAMES
    # =====================================================

    def load_multiple_timeframes(

        self,

        instrument_key: str,

        timeframes: List[str],

        from_date: str,

        to_date: str,

    ) -> Dict[str, pd.DataFrame]:
        """
        Load multiple timeframes.
        """

        result: Dict[
            str,
            pd.DataFrame,
        ] = {}

        for timeframe in timeframes:

            result[timeframe] = (

                self.load_history(

                    instrument_key,

                    timeframe,

                    from_date,

                    to_date,

                )

            )

        return result

    # =====================================================
    # BATCH DOWNLOAD
    # =====================================================

    def batch_download(

        self,

        instrument_keys: List[str],

        timeframe: str,

        from_date: str,

        to_date: str,

    ) -> Dict[str, pd.DataFrame]:
        """
        Download data for multiple symbols.
        """

        output: Dict[
            str,
            pd.DataFrame,
        ] = {}

        for instrument_key in instrument_keys:

            try:

                output[instrument_key] = (

                    self.load_history(

                        instrument_key,

                        timeframe,

                        from_date,

                        to_date,

                    )

                )

            except Exception as exc:

                self.logger.exception(exc)

        return output

    # =====================================================
    # CACHE EXPIRED
    # =====================================================

    def cache_expired(

        self,

        instrument_key: str,

        timeframe: str,

        expiry_minutes: int = 5,

    ) -> bool:
        """
        Check whether cached data has expired.
        """

        key = f"{instrument_key}:{timeframe}"

        timestamp = self.last_refresh.get(

            key

        )

        if timestamp is None:

            return True

        return (

            datetime.now()

            - timestamp

        ) > timedelta(

            minutes=expiry_minutes

        )

    # =====================================================
    # AUTO REFRESH
    # =====================================================

    def auto_refresh(

        self,

        instrument_key: str,

        timeframe: str,

        from_date: str,

        to_date: str,

        expiry_minutes: int = 5,

    ) -> pd.DataFrame:
        """
        Refresh only when cache expires.
        """

        if self.cache_expired(

            instrument_key,

            timeframe,

            expiry_minutes,

        ):

            return self.refresh_data(

                instrument_key,

                timeframe,

                from_date,

                to_date,

            )

        cached = self.get_data(

            instrument_key,

            timeframe,

        )

        return cached.copy()
        # =====================================================
    # TICK CALLBACK
    # =====================================================

    def on_tick(
        self,
        instrument_key: str,
        tick: Dict[str, Any],
    ) -> None:
        """
        Callback executed for every incoming live tick.
        """

        with self.lock:

            self.live_ticks[
                instrument_key
            ] = tick

        self._update_latest_candle(

            instrument_key,

            tick,

        )

    # =====================================================
    # GET LIVE TICK
    # =====================================================

    def latest_tick(
        self,
        instrument_key: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Return latest received tick.
        """

        return self.live_ticks.get(

            instrument_key

        )

    # =====================================================
    # LAST TRADED PRICE
    # =====================================================

    def last_price(
        self,
        instrument_key: str,
    ) -> Optional[float]:
        """
        Return cached LTP.
        """

        tick = self.latest_tick(

            instrument_key

        )

        if tick is None:

            return None

        return tick.get(

            "last_price"

        )

    # =====================================================
    # UPDATE CURRENT CANDLE
    # =====================================================

    def _update_latest_candle(
        self,
        instrument_key: str,
        tick: Dict[str, Any],
    ) -> None:
        """
        Update the latest candle with incoming
        live market data.
        """

        with self.lock:

            if instrument_key not in self.data:

                return

            last_price = tick.get(

                "last_price"

            )

            volume = tick.get(

                "volume"

            )

            if last_price is None:

                return

            for timeframe, dataframe in self.data[
                instrument_key
            ].items():

                if dataframe.empty:

                    continue

                index = dataframe.index[-1]

                dataframe.at[
                    index,
                    "close",
                ] = last_price

                dataframe.at[
                    index,
                    "high",
                ] = max(

                    dataframe.at[
                        index,
                        "high",
                    ],

                    last_price,

                )

                dataframe.at[
                    index,
                    "low",
                ] = min(

                    dataframe.at[
                        index,
                        "low",
                    ],

                    last_price,

                )

                if volume is not None:

                    dataframe.at[
                        index,
                        "volume",
                    ] = volume

                self.indicators.invalidate_symbol(

                    instrument_key,

                    timeframe,

                )

    # =====================================================
    # REFRESH LIVE QUOTE
    # =====================================================

    def refresh_quote(
        self,
        instrument_key: str,
    ) -> Dict[str, Any]:
        """
        Refresh quote from Upstox.
        """

        quote = self.client.get_quote(

            instrument_key,

            refresh=True,

        )

        self.live_ticks[
            instrument_key
        ] = quote

        return quote

    # =====================================================
    # REFRESH MULTIPLE QUOTES
    # =====================================================

    def refresh_quotes(
        self,
        instrument_keys: List[str],
    ) -> Dict[str, Any]:
        """
        Refresh quotes for multiple symbols.
        """

        quotes = self.client.refresh_quotes(

            instrument_keys,

        )

        self.live_ticks.update(

            quotes

        )

        return quotes

    # =====================================================
    # REMOVE LIVE TICK
    # =====================================================

    def remove_tick(
        self,
        instrument_key: str,
    ) -> None:
        """
        Remove cached live tick.
        """

        self.live_ticks.pop(

            instrument_key,

            None,

        )

    # =====================================================
    # CLEAR LIVE TICKS
    # =====================================================

    def clear_live_ticks(
        self,
    ) -> None:
        """
        Remove all cached live ticks.
        """

        self.live_ticks.clear()
            # =====================================================
    # INDICATOR BUNDLE
    # =====================================================

    def indicator_bundle(
        self,
        instrument_key: str,
        timeframe: str,
    ) -> Dict[str, Any]:
        """
        Return commonly used indicators for a scanner.
        """

        dataframe = self.get_data(

            instrument_key,

            timeframe,

        )

        if dataframe is None:

            return {}

        self.indicators.register_data(

            instrument_key,

            timeframe,

            dataframe,

        )

        return self.indicators.indicator_bundle(

            instrument_key,

            timeframe,

        )

    # =====================================================
    # LATEST EMA
    # =====================================================

    def ema(
        self,
        instrument_key: str,
        timeframe: str,
        period: int,
    ) -> Optional[float]:
        """
        Return latest EMA value.
        """

        dataframe = self.get_data(

            instrument_key,

            timeframe,

        )

        if dataframe is None:

            return None

        self.indicators.register_data(

            instrument_key,

            timeframe,

            dataframe,

        )

        return self.indicators.latest_ema(

            instrument_key,

            timeframe,

            period,

        )

    # =====================================================
    # LATEST RSI
    # =====================================================

    def rsi(
        self,
        instrument_key: str,
        timeframe: str,
        period: int = 14,
    ) -> Optional[float]:
        """
        Return latest RSI.
        """

        dataframe = self.get_data(

            instrument_key,

            timeframe,

        )

        if dataframe is None:

            return None

        self.indicators.register_data(

            instrument_key,

            timeframe,

            dataframe,

        )

        return self.indicators.latest_rsi(

            instrument_key,

            timeframe,

            period,

        )

    # =====================================================
    # LATEST MACD
    # =====================================================

    def macd(
        self,
        instrument_key: str,
        timeframe: str,
    ) -> Dict[str, float]:
        """
        Return latest MACD values.
        """

        dataframe = self.get_data(

            instrument_key,

            timeframe,

        )

        if dataframe is None:

            return {}

        self.indicators.register_data(

            instrument_key,

            timeframe,

            dataframe,

        )

        return self.indicators.latest_macd(

            instrument_key,

            timeframe,

        )

    # =====================================================
    # LATEST ATR
    # =====================================================

    def atr(
        self,
        instrument_key: str,
        timeframe: str,
        period: int = 14,
    ) -> Optional[float]:
        """
        Return latest ATR.
        """

        dataframe = self.get_data(

            instrument_key,

            timeframe,

        )

        if dataframe is None:

            return None

        self.indicators.register_data(

            instrument_key,

            timeframe,

            dataframe,

        )

        return self.indicators.latest_atr(

            instrument_key,

            timeframe,

            period,

        )

    # =====================================================
    # LATEST ADX
    # =====================================================

    def adx(
        self,
        instrument_key: str,
        timeframe: str,
        period: int = 14,
    ) -> Optional[float]:
        """
        Return latest ADX.
        """

        dataframe = self.get_data(

            instrument_key,

            timeframe,

        )

        if dataframe is None:

            return None

        self.indicators.register_data(

            instrument_key,

            timeframe,

            dataframe,

        )

        return self.indicators.latest_adx(

            instrument_key,

            timeframe,

            period,

        )

    # =====================================================
    # LATEST VWAP
    # =====================================================

    def vwap(
        self,
        instrument_key: str,
        timeframe: str,
    ) -> Optional[float]:
        """
        Return latest VWAP.
        """

        dataframe = self.get_data(

            instrument_key,

            timeframe,

        )

        if dataframe is None:

            return None

        self.indicators.register_data(

            instrument_key,

            timeframe,

            dataframe,

        )

        return self.indicators.latest_vwap(

            instrument_key,

            timeframe,

        )

    # =====================================================
    # PRELOAD INDICATORS
    # =====================================================

    def preload_indicators(
        self,
        instrument_key: str,
        timeframe: str,
    ) -> None:
        """
        Pre-calculate all commonly used indicators.
        """

        dataframe = self.get_data(

            instrument_key,

            timeframe,

        )

        if dataframe is None:

            return

        self.indicators.register_data(

            instrument_key,

            timeframe,

            dataframe,

        )

        self.indicators.calculate_all(

            instrument_key,

            timeframe,

        )
            # =====================================================
    # MARKET SNAPSHOT
    # =====================================================

    def market_snapshot(
        self,
        instrument_key: str,
        timeframe: str,
    ) -> Dict[str, Any]:
        """
        Scanner-ready market snapshot.
        """

        dataframe = self.get_data(

            instrument_key,

            timeframe,

        )

        if dataframe is None or dataframe.empty:

            return {}

        self.preload_indicators(

            instrument_key,

            timeframe,

        )

        last = dataframe.iloc[-1]

        return {

            "instrument_key": instrument_key,

            "timeframe": timeframe,

            "close": float(last["close"]),

            "open": float(last["open"]),

            "high": float(last["high"]),

            "low": float(last["low"]),

            "volume": int(last["volume"]),

            "ema21": self.ema(

                instrument_key,

                timeframe,

                21,

            ),

            "ema50": self.ema(

                instrument_key,

                timeframe,

                50,

            ),

            "ema200": self.ema(

                instrument_key,

                timeframe,

                200,

            ),

            "rsi": self.rsi(

                instrument_key,

                timeframe,

            ),

            "adx": self.adx(

                instrument_key,

                timeframe,

            ),

            "atr": self.atr(

                instrument_key,

                timeframe,

            ),

            "vwap": self.vwap(

                instrument_key,

                timeframe,

            ),

            "macd": self.macd(

                instrument_key,

                timeframe,

            ),

        }

    # =====================================================
    # MULTI TIMEFRAME SNAPSHOT
    # =====================================================

    def multi_timeframe_snapshot(
        self,
        instrument_key: str,
        timeframes: List[str],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Snapshot for multiple timeframes.
        """

        output: Dict[
            str,
            Dict[str, Any],
        ] = {}

        for timeframe in timeframes:

            output[timeframe] = (

                self.market_snapshot(

                    instrument_key,

                    timeframe,

                )

            )

        return output

    # =====================================================
    # TREND SUMMARY
    # =====================================================

    def trend_summary(
        self,
        instrument_key: str,
        timeframe: str,
    ) -> Dict[str, Any]:
        """
        Trend information used by scanners.
        """

        return {

            "ema_alignment": (

                self.indicators.ema_alignment(

                    instrument_key,

                    timeframe,

                )

            ),

            "price_above_ema": (

                self.indicators.price_above_ema(

                    instrument_key,

                    timeframe,

                    21,

                )

            ),

            "price_above_vwap": (

                self.indicators.price_above_vwap(

                    instrument_key,

                    timeframe,

                )

            ),

            "strong_trend": (

                self.indicators.strong_trend(

                    instrument_key,

                    timeframe,

                )

            ),

            "trend_score": (

                self.indicators.trend_score(

                    instrument_key,

                    timeframe,

                )

            ),

        }

    # =====================================================
    # VOLUME SUMMARY
    # =====================================================

    def volume_summary(
        self,
        instrument_key: str,
        timeframe: str,
    ) -> Dict[str, Any]:
        """
        Volume analysis summary.
        """

        dataframe = self.get_data(

            instrument_key,

            timeframe,

        )

        if dataframe is None or dataframe.empty:

            return {}

        latest_volume = int(

            dataframe.iloc[-1]["volume"]

        )

        average_volume = float(

            dataframe["volume"]

            .tail(20)

            .mean()

        )

        ratio = 0.0

        if average_volume > 0:

            ratio = (

                latest_volume

                / average_volume

            )

        return {

            "latest_volume": latest_volume,

            "average_volume": average_volume,

            "volume_ratio": round(

                ratio,

                2,

            ),

            "volume_expansion": (

                self.indicators.volume_expansion(

                    instrument_key,

                    timeframe,

                )

            ),

        }

    # =====================================================
    # SYMBOL CONTEXT
    # =====================================================

    def symbol_context(
        self,
        instrument_key: str,
        timeframe: str,
    ) -> Dict[str, Any]:
        """
        Complete scanner-ready context object.
        """

        return {

            "market": self.market_snapshot(

                instrument_key,

                timeframe,

            ),

            "trend": self.trend_summary(

                instrument_key,

                timeframe,

            ),

            "volume": self.volume_summary(

                instrument_key,

                timeframe,

            ),

            "latest_tick": self.latest_tick(

                instrument_key,

            ),

        }
        # =====================================================
    # CREATE WATCHLIST
    # =====================================================

    def create_watchlist(
        self,
        name: str,
    ) -> None:
        """
        Create an empty watchlist.
        """

        with self.lock:

            self.watchlists.setdefault(

                name,

                [],

            )

    # =====================================================
    # ADD SYMBOL
    # =====================================================

    def add_to_watchlist(
        self,
        watchlist: str,
        instrument_key: str,
    ) -> bool:
        """
        Add an instrument to a watchlist.
        """

        with self.lock:

            symbols = self.watchlists.setdefault(

                watchlist,

                [],

            )

            if instrument_key in symbols:

                return False

            symbols.append(

                instrument_key

            )

            return True

    # =====================================================
    # REMOVE SYMBOL
    # =====================================================

    def remove_from_watchlist(
        self,
        watchlist: str,
        instrument_key: str,
    ) -> bool:
        """
        Remove an instrument from a watchlist.
        """

        with self.lock:

            symbols = self.watchlists.get(

                watchlist,

            )

            if symbols is None:

                return False

            if instrument_key not in symbols:

                return False

            symbols.remove(

                instrument_key

            )

            return True

    # =====================================================
    # IMPORT WATCHLIST
    # =====================================================

    def import_watchlist(
        self,
        watchlist: str,
        instrument_keys: List[str],
    ) -> int:
        """
        Bulk import instruments.
        """

        added = 0

        for instrument_key in instrument_keys:

            if self.add_to_watchlist(

                watchlist,

                instrument_key,

            ):

                added += 1

        return added

    # =====================================================
    # REMOVE MULTIPLE SYMBOLS
    # =====================================================

    def remove_many(
        self,
        watchlist: str,
        instrument_keys: List[str],
    ) -> int:
        """
        Remove multiple instruments.
        """

        removed = 0

        for instrument_key in instrument_keys:

            if self.remove_from_watchlist(

                watchlist,

                instrument_key,

            ):

                removed += 1

        return removed

    # =====================================================
    # GET WATCHLIST
    # =====================================================

    def get_watchlist(
        self,
        watchlist: str,
    ) -> List[str]:
        """
        Return instruments in a watchlist.
        """

        return list(

            self.watchlists.get(

                watchlist,

                [],

            )

        )

    # =====================================================
    # WATCHLIST EXISTS
    # =====================================================

    def has_watchlist(
        self,
        watchlist: str,
    ) -> bool:
        """
        Check whether a watchlist exists.
        """

        return watchlist in self.watchlists

    # =====================================================
    # DELETE WATCHLIST
    # =====================================================

    def delete_watchlist(
        self,
        watchlist: str,
    ) -> bool:
        """
        Delete an entire watchlist.
        """

        with self.lock:

            if watchlist not in self.watchlists:

                return False

            del self.watchlists[

                watchlist

            ]

            return True

    # =====================================================
    # WATCHLIST NAMES
    # =====================================================

    def watchlist_names(
        self,
    ) -> List[str]:
        """
        Return all watchlist names.
        """

        return sorted(

            self.watchlists.keys()

        )

    # =====================================================
    # FAVORITES
    # =====================================================

    def add_favorite(
        self,
        instrument_key: str,
    ) -> bool:
        """
        Add instrument to Favorites.
        """

        return self.add_to_watchlist(

            "Favorites",

            instrument_key,

        )

    # =====================================================
    # RECENTLY SCANNED
    # =====================================================

    def add_recent(
        self,
        instrument_key: str,
        limit: int = 100,
    ) -> None:
        """
        Maintain recently scanned symbols.
        """

        with self.lock:

            recent = self.watchlists.setdefault(

                "Recent",

                [],

            )

            if instrument_key in recent:

                recent.remove(

                    instrument_key

                )

            recent.insert(

                0,

                instrument_key,

            )

            del recent[limit:]
                # =====================================================
    # SCANNER FEED
    # =====================================================

    def scanner_feed(
        self,
        instrument_key: str,
        timeframe: str,
    ) -> Dict[str, Any]:
        """
        Return a complete data package for scanners.
        """

        dataframe = self.get_data(

            instrument_key,

            timeframe,

        )

        if dataframe is None:

            return {}

        return {

            "instrument_key": instrument_key,

            "timeframe": timeframe,

            "dataframe": dataframe,

            "context": self.symbol_context(

                instrument_key,

                timeframe,

            ),

            "tick": self.latest_tick(

                instrument_key,

            ),

        }

    # =====================================================
    # BATCH SCANNER FEED
    # =====================================================

    def scanner_feed_batch(
        self,
        instrument_keys: List[str],
        timeframe: str,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Create scanner feed for multiple instruments.
        """

        feeds: Dict[
            str,
            Dict[str, Any],
        ] = {}

        for instrument_key in instrument_keys:

            try:

                feed = self.scanner_feed(

                    instrument_key,

                    timeframe,

                )

                if feed:

                    feeds[

                        instrument_key

                    ] = feed

            except Exception as exc:

                self.logger.exception(

                    exc

                )

        return feeds

    # =====================================================
    # FILTER LOADED SYMBOLS
    # =====================================================

    def loaded_symbols(
        self,
    ) -> List[str]:
        """
        Return all symbols currently loaded.
        """

        return sorted(

            self.data.keys()

        )

    # =====================================================
    # FILTER BY TIMEFRAME
    # =====================================================

    def symbols_by_timeframe(
        self,
        timeframe: str,
    ) -> List[str]:
        """
        Return symbols that have a specific timeframe loaded.
        """

        symbols: List[
            str
        ] = []

        for instrument_key, frames in self.data.items():

            if timeframe in frames:

                symbols.append(

                    instrument_key

                )

        return sorted(

            symbols

        )

    # =====================================================
    # PRELOAD WATCHLIST
    # =====================================================

    def preload_watchlist(
        self,
        watchlist: str,
        timeframe: str,
        from_date: str,
        to_date: str,
    ) -> int:
        """
        Download historical data for every symbol
        in a watchlist.
        """

        symbols = self.get_watchlist(

            watchlist

        )

        loaded = 0

        for instrument_key in symbols:

            try:

                self.load_history(

                    instrument_key,

                    timeframe,

                    from_date,

                    to_date,

                )

                loaded += 1

            except Exception as exc:

                self.logger.exception(

                    exc

                )

        return loaded

    # =====================================================
    # PRELOAD MULTIPLE WATCHLISTS
    # =====================================================

    def preload_watchlists(
        self,
        watchlists: List[str],
        timeframe: str,
        from_date: str,
        to_date: str,
    ) -> Dict[str, int]:
        """
        Preload multiple watchlists.
        """

        results: Dict[
            str,
            int,
        ] = {}

        for watchlist in watchlists:

            results[watchlist] = (

                self.preload_watchlist(

                    watchlist,

                    timeframe,

                    from_date,

                    to_date,

                )

            )

        return results

    # =====================================================
    # READY FOR SCAN
    # =====================================================

    def ready_for_scan(
        self,
        instrument_key: str,
        timeframe: str,
    ) -> bool:
        """
        Check whether a symbol is fully prepared
        for scanner execution.
        """

        return (

            self.has_data(

                instrument_key,

                timeframe,

            )

            and instrument_key in self.live_ticks

        )

    # =====================================================
    # READY SYMBOLS
    # =====================================================

    def ready_symbols(
        self,
        timeframe: str,
    ) -> List[str]:
        """
        Return all symbols that are scan-ready.
        """

        return [

            symbol

            for symbol in self.symbols_by_timeframe(

                timeframe

            )

            if self.ready_for_scan(

                symbol,

                timeframe,

            )

        ]

    # =====================================================
    # MARKET DISTRIBUTION
    # =====================================================

    def distribute_market_data(
        self,
        timeframe: str,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Build scanner feeds for every loaded symbol.
        """

        return self.scanner_feed_batch(

            self.ready_symbols(

                timeframe

            ),

            timeframe,

        )
        # =====================================================
    # REMOVE SYMBOL CACHE
    # =====================================================

    def clear_symbol(
        self,
        instrument_key: str,
    ) -> None:
        """
        Remove all cached data for a symbol.
        """

        with self.lock:

            self.data.pop(

                instrument_key,

                None,

            )

            self.live_ticks.pop(

                instrument_key,

                None,

            )

            keys_to_remove = [

                key

                for key in self.last_refresh

                if key.startswith(

                    f"{instrument_key}:"

                )

            ]

            for key in keys_to_remove:

                del self.last_refresh[key]

    # =====================================================
    # CLEAR ALL DATA
    # =====================================================

    def clear(
        self,
    ) -> None:
        """
        Remove all cached data.
        """

        with self.lock:

            self.data.clear()

            self.live_ticks.clear()

            self.last_refresh.clear()

            self.indicators.invalidate_all()

    # =====================================================
    # REMOVE EXPIRED CACHE
    # =====================================================

    def cleanup_cache(
        self,
        expiry_minutes: int = 30,
    ) -> int:
        """
        Remove expired datasets.
        """

        removed = 0

        now = datetime.now()

        expired = []

        for key, timestamp in self.last_refresh.items():

            if (

                now - timestamp

            ) > timedelta(

                minutes=expiry_minutes,

            ):

                expired.append(

                    key

                )

        for key in expired:

            instrument_key, timeframe = key.split(

                ":",

                1,

            )

            if (

                instrument_key in self.data

                and timeframe in self.data[
                    instrument_key
                ]

            ):

                del self.data[
                    instrument_key
                ][
                    timeframe
                ]

                removed += 1

            del self.last_refresh[key]

        return removed

    # =====================================================
    # MEMORY STATISTICS
    # =====================================================

    def memory_statistics(
        self,
    ) -> Dict[str, Any]:
        """
        Return memory usage statistics.
        """

        dataframe_count = sum(

            len(frames)

            for frames in self.data.values()

        )

        row_count = 0

        for frames in self.data.values():

            for dataframe in frames.values():

                row_count += len(

                    dataframe

                )

        return {

            "symbols": len(

                self.data

            ),

            "timeframes": dataframe_count,

            "rows": row_count,

            "live_ticks": len(

                self.live_ticks

            ),

            "watchlists": len(

                self.watchlists

            ),

        }

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

        total = (

            self.cache_hits

            + self.cache_misses

        )

        if total == 0:

            return 0.0

        return round(

            (

                self.cache_hits

                / total

            ) * 100,

            2,

        )

    # =====================================================
    # PERFORMANCE
    # =====================================================

    def performance(
        self,
    ) -> Dict[str, Any]:
        """
        Runtime performance metrics.
        """

        uptime = (

            datetime.now()

            - self.started

        ).total_seconds()

        return {

            "uptime_seconds": round(

                uptime,

                2,

            ),

            "requests": self.requests,

            "cache_hits": self.cache_hits,

            "cache_misses": self.cache_misses,

            "cache_hit_rate": self.cache_hit_rate,

        }

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(
        self,
    ) -> Dict[str, Any]:
        """
        Verify manager health.
        """

        return {

            "healthy": True,

            "client_connected": bool(

                self.client

            ),

            "indicator_engine": bool(

                self.indicators

            ),

            "loaded_symbols": len(

                self.data

            ),

            "live_ticks": len(

                self.live_ticks

            ),

        }

    # =====================================================
    # DIAGNOSTICS
    # =====================================================

    def diagnostics(
        self,
    ) -> Dict[str, Any]:
        """
        Complete diagnostic information.
        """

        return {

            "version": self.VERSION,

            "performance": self.performance(),

            "memory": self.memory_statistics(),

            "health": self.health_check(),

        }
        # =====================================================
    # EXPORT WATCHLISTS
    # =====================================================

    def export_watchlists(
        self,
    ) -> Dict[str, List[str]]:
        """
        Export all watchlists.
        """

        with self.lock:

            return {

                name: symbols.copy()

                for name, symbols in self.watchlists.items()

            }

    # =====================================================
    # IMPORT WATCHLISTS
    # =====================================================

    def import_watchlists(
        self,
        watchlists: Dict[str, List[str]],
        replace: bool = False,
    ) -> None:
        """
        Import watchlists.
        """

        with self.lock:

            if replace:

                self.watchlists.clear()

            for name, symbols in watchlists.items():

                self.watchlists[name] = list(

                    dict.fromkeys(symbols)

                )

    # =====================================================
    # SNAPSHOT
    # =====================================================

    def snapshot(
        self,
    ) -> Dict[str, Any]:
        """
        Create a lightweight runtime snapshot.
        """

        return {

            "created_at": datetime.now().isoformat(),

            "symbols": self.loaded_symbols(),

            "watchlists": self.export_watchlists(),

            "performance": self.performance(),

            "memory": self.memory_statistics(),

        }

    # =====================================================
    # EXPORT STATE
    # =====================================================

    def export_state(
        self,
    ) -> Dict[str, Any]:
        """
        Export DataManager state.
        """

        state = {

            "version": self.VERSION,

            "created": datetime.now().isoformat(),

            "watchlists": self.export_watchlists(),

            "last_refresh": {

                key: value.isoformat()

                for key, value in self.last_refresh.items()

            },

            "loaded_symbols": self.loaded_symbols(),

        }

        return state

    # =====================================================
    # IMPORT STATE
    # =====================================================

    def import_state(
        self,
        state: Dict[str, Any],
    ) -> None:
        """
        Restore previously exported state.
        """

        watchlists = state.get(

            "watchlists",

            {},

        )

        self.import_watchlists(

            watchlists,

            replace=True,

        )

        refresh = state.get(

            "last_refresh",

            {},

        )

        self.last_refresh.clear()

        for key, value in refresh.items():

            try:

                self.last_refresh[key] = (

                    datetime.fromisoformat(

                        value

                    )

                )

            except Exception:

                continue

    # =====================================================
    # SERIALIZE SYMBOL
    # =====================================================

    def serialize_symbol(
        self,
        instrument_key: str,
    ) -> Dict[str, Any]:
        """
        Serialize cached symbol data.
        """

        output = {

            "instrument_key": instrument_key,

            "timeframes": {},

        }

        if instrument_key not in self.data:

            return output

        for timeframe, dataframe in self.data[
            instrument_key
        ].items():

            output["timeframes"][

                timeframe

            ] = dataframe.to_dict(

                orient="records"

            )

        return output

    # =====================================================
    # RESTORE SYMBOL
    # =====================================================

    def restore_symbol(
        self,
        payload: Dict[str, Any],
    ) -> None:
        """
        Restore serialized symbol.
        """

        instrument_key = payload.get(

            "instrument_key"

        )

        if not instrument_key:

            return

        for timeframe, rows in payload.get(

            "timeframes",

            {},

        ).items():

            dataframe = pd.DataFrame(

                rows

            )

            if "datetime" in dataframe.columns:

                dataframe["datetime"] = (

                    pd.to_datetime(

                        dataframe["datetime"]

                    )

                )

            self.set_data(

                instrument_key,

                timeframe,

                dataframe,

            )

    # =====================================================
    # BACKUP
    # =====================================================

    def backup(
        self,
    ) -> Dict[str, Any]:
        """
        Create a complete backup object.
        """

        backup = self.export_state()

        backup["symbols"] = [

            self.serialize_symbol(

                symbol

            )

            for symbol in self.loaded_symbols()

        ]

        return backup

    # =====================================================
    # RESTORE BACKUP
    # =====================================================

    def restore_backup(
        self,
        backup: Dict[str, Any],
    ) -> None:
        """
        Restore backup.
        """

        self.clear()

        self.import_state(

            backup

        )

        for symbol in backup.get(

            "symbols",

            [],

        ):

            self.restore_symbol(

                symbol

            )
                # =====================================================
    # DATA SUMMARY
    # =====================================================

    def data_summary(
        self,
    ) -> Dict[str, Any]:
        """
        Return a summary of all cached datasets.
        """

        summary: Dict[str, Any] = {}

        for instrument_key, frames in self.data.items():

            summary[instrument_key] = {}

            for timeframe, dataframe in frames.items():

                if dataframe.empty:

                    continue

                summary[instrument_key][timeframe] = {

                    "rows": len(dataframe),

                    "start": dataframe.index[0]

                    if not dataframe.index.empty

                    else None,

                    "end": dataframe.index[-1]

                    if not dataframe.index.empty

                    else None,

                    "last_close": float(

                        dataframe.iloc[-1]["close"]

                    ),

                    "last_volume": int(

                        dataframe.iloc[-1]["volume"]

                    ),

                }

        return summary

    # =====================================================
    # DATA INTEGRITY
    # =====================================================

    def validate_data(
        self,
        instrument_key: str,
        timeframe: str,
    ) -> Dict[str, Any]:
        """
        Validate a cached dataframe.
        """

        dataframe = self.get_data(

            instrument_key,

            timeframe,

        )

        if dataframe is None:

            return {

                "valid": False,

                "reason": "Data not loaded",

            }

        required_columns = [

            "open",

            "high",

            "low",

            "close",

            "volume",

        ]

        missing = [

            column

            for column in required_columns

            if column not in dataframe.columns

        ]

        if missing:

            return {

                "valid": False,

                "missing_columns": missing,

            }

        return {

            "valid": True,

            "rows": len(dataframe),

            "missing_values": int(

                dataframe.isna().sum().sum()

            ),

            "duplicates": int(

                dataframe.duplicated().sum()

            ),

        }

    # =====================================================
    # VALIDATE ALL DATA
    # =====================================================

    def validate_all(
        self,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Validate every loaded dataframe.
        """

        results: Dict[
            str,
            Dict[str, Any],
        ] = {}

        for instrument_key, frames in self.data.items():

            results[instrument_key] = {}

            for timeframe in frames:

                results[instrument_key][

                    timeframe

                ] = self.validate_data(

                    instrument_key,

                    timeframe,

                )

        return results

    # =====================================================
    # MANAGER METADATA
    # =====================================================

    def metadata(
        self,
    ) -> Dict[str, Any]:
        """
        Metadata describing the DataManager.
        """

        return {

            "name": self.__class__.__name__,

            "version": self.VERSION,

            "started": self.started.isoformat(),

            "loaded_symbols": len(

                self.data

            ),

            "watchlists": len(

                self.watchlists

            ),

            "live_ticks": len(

                self.live_ticks

            ),

        }

    # =====================================================
    # RUNTIME REPORT
    # =====================================================

    def runtime_report(
        self,
    ) -> Dict[str, Any]:
        """
        Complete runtime report.
        """

        return {

            "metadata": self.metadata(),

            "performance": self.performance(),

            "health": self.health_check(),

            "memory": self.memory_statistics(),

            "data": self.data_summary(),

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

        self.cache_hits = 0

        self.cache_misses = 0

        self.started = datetime.now()

    # =====================================================
    # IS SYMBOL LOADED
    # =====================================================

    def is_loaded(
        self,
        instrument_key: str,
    ) -> bool:
        """
        Check whether any timeframe is loaded for a symbol.
        """

        return instrument_key in self.data

    # =====================================================
    # TOTAL DATASETS
    # =====================================================

    @property
    def dataset_count(
        self,
    ) -> int:
        """
        Total cached dataframes.
        """

        return sum(

            len(frames)

            for frames in self.data.values()

        )

    # =====================================================
    # TOTAL ROWS
    # =====================================================

    @property
    def total_rows(
        self,
    ) -> int:
        """
        Total cached OHLCV rows.
        """

        total = 0

        for frames in self.data.values():

            for dataframe in frames.values():

                total += len(

                    dataframe

                )

        return total

    # =====================================================
    # MANAGER INFO
    # =====================================================

    def info(
        self,
    ) -> Dict[str, Any]:
        """
        High-level manager information.
        """

        return {

            "metadata": self.metadata(),

            "datasets": self.dataset_count,

            "rows": self.total_rows,

            "performance": self.performance(),

            "cache_hit_rate": self.cache_hit_rate,

        }
        # =====================================================
    # MAGIC METHODS
    # =====================================================

    def __len__(
        self,
    ) -> int:
        """
        Number of loaded symbols.
        """

        return len(

            self.data

        )

    def __contains__(
        self,
        instrument_key: str,
    ) -> bool:
        """
        Check if a symbol exists.
        """

        return instrument_key in self.data

    def __getitem__(
        self,
        instrument_key: str,
    ) -> Dict[str, pd.DataFrame]:
        """
        Dictionary-style access.

        Example:
            manager["NSE_EQ|INE040A01034"]
        """

        return self.data.get(

            instrument_key,

            {},

        )

    def __iter__(
        self,
    ):
        """
        Iterate over loaded symbols.
        """

        return iter(

            self.data.items()

        )

    # =====================================================
    # CONVENIENCE HELPERS
    # =====================================================

    def symbols(
        self,
    ) -> List[str]:
        """
        Return all loaded symbols.
        """

        return self.loaded_symbols()

    def timeframes(
        self,
        instrument_key: str,
    ) -> List[str]:
        """
        Return loaded timeframes for a symbol.
        """

        if instrument_key not in self.data:

            return []

        return sorted(

            self.data[instrument_key].keys()

        )

    def symbol_count(
        self,
    ) -> int:
        """
        Number of loaded symbols.
        """

        return len(

            self.data

        )

    def timeframe_count(
        self,
        instrument_key: str,
    ) -> int:
        """
        Number of loaded timeframes for a symbol.
        """

        return len(

            self.data.get(

                instrument_key,

                {},

            )

        )

    # =====================================================
    # FACTORY
    # =====================================================

    @classmethod
    def create(
        cls,
        client: UpstoxClient,
        indicators: Optional[IndicatorEngine] = None,
    ) -> "DataManager":
        """
        Factory constructor.
        """

        return cls(

            client=client,

            indicators=indicators,

        )

    # =====================================================
    # CONTEXT MANAGER
    # =====================================================

    def __enter__(
        self,
    ) -> "DataManager":
        """
        Context manager entry.
        """

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> bool:
        """
        Context manager exit.
        """

        self.shutdown()

        return False

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(
        self,
        clear_cache: bool = False,
    ) -> None:
        """
        Gracefully shut down the manager.
        """

        self.logger.info(

            "Shutting down DataManager..."

        )

        if clear_cache:

            self.clear()

    # =====================================================
    # STRING REPRESENTATIONS
    # =====================================================

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (

            f"{self.__class__.__name__}("

            f"symbols={len(self.data)}, "

            f"datasets={self.dataset_count}, "

            f"ticks={len(self.live_ticks)})"

        )

    def __str__(
        self,
    ) -> str:
        """
        User-friendly representation.
        """

        return (

            f"{self.__class__.__name__}"

            f" | Symbols: {len(self.data)}"

            f" | Datasets: {self.dataset_count}"

            f" | Watchlists: {len(self.watchlists)}"

        )

    # =====================================================
    # DEBUG HELPERS
    # =====================================================

    def dump_state(
        self,
    ) -> Dict[str, Any]:
        """
        Lightweight debug dump.
        """

        return {

            "symbols": self.loaded_symbols(),

            "watchlists": self.watchlist_names(),

            "datasets": self.dataset_count,

            "rows": self.total_rows,

            "ticks": len(

                self.live_ticks

            ),

            "performance": self.performance(),

        }

    def print_summary(
        self,
    ) -> None:
        """
        Print a concise runtime summary.
        """

        self.logger.info(

            "========== DataManager =========="

        )

        self.logger.info(

            "Symbols      : %s",

            self.symbol_count(),

        )

        self.logger.info(

            "Datasets     : %s",

            self.dataset_count,

        )

        self.logger.info(

            "Rows         : %s",

            self.total_rows,

        )

        self.logger.info(

            "Watchlists   : %s",

            len(self.watchlists),

        )

        self.logger.info(

            "Live Ticks   : %s",

            len(self.live_ticks),

        )

        self.logger.info(

            "Cache Hit %%  : %s",

            self.cache_hit_rate,

        )

        self.logger.info(

            "================================="

        )
            # =====================================================
    # REFRESH ALL LOADED DATA
    # =====================================================

    def refresh_all(
        self,
    ) -> int:
        """
        Refresh every loaded dataset.

        Returns
        -------
        int
            Number of datasets refreshed successfully.
        """

        refreshed = 0

        for instrument_key, frames in list(self.data.items()):

            for timeframe in list(frames.keys()):

                try:

                    if self.refresh_data(

                        instrument_key,

                        timeframe,

                    ):

                        refreshed += 1

                except Exception as exc:

                    self.logger.exception(

                        "Refresh failed for %s [%s]: %s",

                        instrument_key,

                        timeframe,

                        exc,

                    )

        return refreshed

    # =====================================================
    # INVALIDATE INDICATOR CACHE
    # =====================================================

    def invalidate_indicator_cache(
        self,
        instrument_key: Optional[str] = None,
        timeframe: Optional[str] = None,
    ) -> None:
        """
        Invalidate indicator cache.
        """

        if instrument_key and timeframe:

            self.indicators.invalidate(

                instrument_key,

                timeframe,

            )

            return

        self.indicators.invalidate_all()

    # =====================================================
    # REGISTER DATAFRAME
    # =====================================================

    def register_dataframe(
        self,
        instrument_key: str,
        timeframe: str,
        dataframe: pd.DataFrame,
    ) -> None:
        """
        Register dataframe with DataManager and IndicatorEngine.
        """

        self.set_data(

            instrument_key,

            timeframe,

            dataframe,

        )

        self.preload_indicators(

            instrument_key,

            timeframe,

        )

    # =====================================================
    # IS READY
    # =====================================================

    @property
    def ready(
        self,
    ) -> bool:
        """
        Returns True when at least one dataset is loaded.
        """

        return self.dataset_count > 0

    # =====================================================
    # STATUS
    # =====================================================

    @property
    def status(
        self,
    ) -> Dict[str, Any]:
        """
        Current manager status.
        """

        return {

            "ready": self.ready,

            "symbols": self.symbol_count(),

            "datasets": self.dataset_count,

            "rows": self.total_rows,

            "watchlists": len(

                self.watchlists,

            ),

            "live_ticks": len(

                self.live_ticks,

            ),

            "cache_hit_rate": self.cache_hit_rate,

        }

    # =====================================================
    # VERSION
    # =====================================================

    @classmethod
    def version(
        cls,
    ) -> str:
        """
        Return DataManager version.
        """

        return cls.VERSION

    # =====================================================
    # BUILD REPORT
    # =====================================================

    @classmethod
    def build_report(
        cls,
    ) -> Dict[str, str]:
        """
        Static build information.
        """

        return {

            "component": cls.__name__,

            "version": cls.VERSION,

            "status": "Production",

            "thread_safe": "Yes",

            "live_data": "Supported",

            "historical_data": "Supported",

            "indicator_engine": "Integrated",

            "scanner_ready": "Yes",

        }

    # =====================================================
    # CLOSE
    # =====================================================

    def close(
        self,
    ) -> None:
        """
        Compatibility wrapper.
        """

        self.shutdown()

    # =====================================================
    # DESTROY
    # =====================================================

    def destroy(
        self,
    ) -> None:
        """
        Release cached resources.
        """

        self.shutdown(

            clear_cache=True,

        )

    # =====================================================
    # FINALIZE
    # =====================================================

    def finalize(
        self,
    ) -> None:
        """
        Final cleanup before application exit.
        """

        self.logger.info(

            "Finalizing DataManager."

        )

        self.destroy()


# ==========================
# END OF FILE
# ==========================