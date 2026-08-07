from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any

import pandas as pd


# ==========================================================
# MARKET DATA
# ==========================================================

@dataclass(slots=True)
class MarketData:

    symbol: str

    exchange: str = "NSE"

    timeframe: str = "15m"

    last_price: float = 0.0

    open_price: float = 0.0

    high_price: float = 0.0

    low_price: float = 0.0

    close_price: float = 0.0

    previous_close: float = 0.0

    volume: int = 0

    value: float = 0.0

    change: float = 0.0

    change_percent: float = 0.0

    bid: float = 0.0

    ask: float = 0.0

    bid_quantity: int = 0

    ask_quantity: int = 0

    vwap: float = 0.0

    atr: float = 0.0

    rsi: float = 0.0

    macd: float = 0.0

    macd_signal: float = 0.0

    macd_histogram: float = 0.0

    adx: float = 0.0

    supertrend: float = 0.0

    ema9: float = 0.0

    ema20: float = 0.0

    ema21: float = 0.0

    ema50: float = 0.0

    ema100: float = 0.0

    ema200: float = 0.0

    sma50: float = 0.0

    sma200: float = 0.0

    relative_volume: float = 0.0

    gap_percent: float = 0.0

    day_high_breakout: bool = False

    day_low_breakdown: bool = False

    week_high_breakout: bool = False

    month_high_breakout: bool = False

    all_time_high_breakout: bool = False

    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ==========================================================
# MARKET DATA MANAGER
# ==========================================================

class MarketDataManager:

    _instance = None

    _instance_lock = threading.Lock()

    def __new__(cls):

        with cls._instance_lock:

            if cls._instance is None:

                cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):

        if getattr(self, "_initialized", False):

            return

        self._initialized = True

        self._lock = threading.RLock()

        # Latest market data
        self.market_data: Dict[str, MarketData] = {}

        # Historical candles
        self.candle_cache: Dict[
            tuple[str, str],
            pd.DataFrame
        ] = {}

        # Indicator cache
        self.indicator_cache: Dict[
            tuple[str, str],
            Dict[str, Any]
        ] = {}

        # Last refresh time
        self.last_refresh: Dict[
            str,
            datetime
        ] = {}

        # Refresh interval (seconds)
        self.refresh_interval = 30

        self.running = False

        self.refresh_thread: Optional[
            threading.Thread
        ] = None

    # ==========================================================
    # STORE MARKET DATA
    # ==========================================================

    def update_market_data(

        self,

        data: MarketData,

    ) -> None:

        with self._lock:

            self.market_data[
                data.symbol
            ] = data

            self.last_refresh[
                data.symbol
            ] = datetime.utcnow()

    # ==========================================================
    # GET MARKET DATA
    # ==========================================================

    def get(

        self,

        symbol: str,

    ) -> Optional[MarketData]:

        return self.market_data.get(

            symbol

        )

    # ==========================================================
    # ALL MARKET DATA
    # ==========================================================

    def all_symbols(

        self,

    ) -> List[MarketData]:

        return list(

            self.market_data.values()

        )

    # ==========================================================
    # SYMBOL EXISTS
    # ==========================================================

    def exists(

        self,

        symbol: str,

    ) -> bool:

        return symbol in self.market_data
        # ==========================================================
    # STORE CANDLES
    # ==========================================================

    def update_candles(

        self,

        symbol: str,

        timeframe: str,

        candles: pd.DataFrame,

    ) -> None:

        with self._lock:

            self.candle_cache[

                (symbol, timeframe)

            ] = candles.copy()

    # ==========================================================
    # GET CANDLES
    # ==========================================================

    def get_candles(

        self,

        symbol: str,

        timeframe: str,

    ) -> Optional[pd.DataFrame]:

        return self.candle_cache.get(

            (symbol, timeframe)

        )

    # ==========================================================
    # REMOVE CANDLES
    # ==========================================================

    def remove_candles(

        self,

        symbol: str,

        timeframe: str,

    ) -> bool:

        key = (

            symbol,

            timeframe,

        )

        if key not in self.candle_cache:

            return False

        del self.candle_cache[key]

        return True

    # ==========================================================
    # STORE INDICATORS
    # ==========================================================

    def update_indicators(

        self,

        symbol: str,

        timeframe: str,

        indicators: Dict[str, Any],

    ) -> None:

        with self._lock:

            self.indicator_cache[

                (symbol, timeframe)

            ] = dict(

                indicators

            )

    # ==========================================================
    # GET INDICATORS
    # ==========================================================

    def get_indicators(

        self,

        symbol: str,

        timeframe: str,

    ) -> Dict[str, Any]:

        return self.indicator_cache.get(

            (symbol, timeframe),

            {},

        )

    # ==========================================================
    # REMOVE INDICATORS
    # ==========================================================

    def remove_indicators(

        self,

        symbol: str,

        timeframe: str,

    ) -> bool:

        key = (

            symbol,

            timeframe,

        )

        if key not in self.indicator_cache:

            return False

        del self.indicator_cache[key]

        return True

    # ==========================================================
    # SUPPORTED TIMEFRAMES
    # ==========================================================

    def supported_timeframes(

        self,

    ) -> List[str]:

        return [

            "1m",

            "3m",

            "5m",

            "10m",

            "15m",

            "30m",

            "45m",

            "1h",

            "2h",

            "4h",

            "1D",

            "1W",

            "1M",

        ]

    # ==========================================================
    # LAST REFRESH
    # ==========================================================

    def last_updated(

        self,

        symbol: str,

    ) -> Optional[datetime]:

        return self.last_refresh.get(

            symbol

        )

    # ==========================================================
    # CLEAR CACHE
    # ==========================================================

    def clear_cache(self) -> None:

        with self._lock:

            self.market_data.clear()

            self.candle_cache.clear()

            self.indicator_cache.clear()

            self.last_refresh.clear()

    # ==========================================================
    # MARKET STATUS
    # ==========================================================

    def market_open(self) -> bool:

        now = datetime.now()

        if now.weekday() >= 5:

            return False

        minutes = (

            now.hour * 60

            + now.minute

        )

        market_open = (

            9 * 60

            + 15

        )

        market_close = (

            15 * 60

            + 30

        )

        return (

            market_open

            <= minutes

            <= market_close

        )

    # ==========================================================
    # AUTO REFRESH LOOP
    # ==========================================================

    def _refresh_loop(self) -> None:

        while self.running:

            try:

                self.refresh()

            except Exception:

                pass

            time.sleep(

                self.refresh_interval

            )

    # ==========================================================
    # START AUTO REFRESH
    # ==========================================================

    def start(self) -> None:

        if self.running:

            return

        self.running = True

        self.refresh_thread = threading.Thread(

            target=self._refresh_loop,

            daemon=True,

            name="MarketDataRefresh",

        )

        self.refresh_thread.start()

    # ==========================================================
    # STOP AUTO REFRESH
    # ==========================================================

    def stop(self) -> None:

        self.running = False

        if (

            self.refresh_thread

            and self.refresh_thread.is_alive()

        ):

            self.refresh_thread.join(

                timeout=2

            )

    # ==========================================================
    # REFRESH PLACEHOLDER
    # ==========================================================

    def refresh(self) -> None:
        """
        This method will be implemented by the
        DataService (Yahoo/NSE/WebSocket provider).

        It intentionally remains empty here because
        MarketDataManager is responsible only for
        caching and distribution of market data.
        """
        return
        # ==========================================================
    # BULK UPDATE
    # ==========================================================

    def update_bulk(

        self,

        data_list: List[MarketData],

    ) -> None:

        with self._lock:

            now = datetime.utcnow()

            for data in data_list:

                self.market_data[data.symbol] = data

                self.last_refresh[data.symbol] = now

    # ==========================================================
    # REMOVE SYMBOL
    # ==========================================================

    def remove_symbol(

        self,

        symbol: str,

    ) -> bool:

        with self._lock:

            removed = False

            if symbol in self.market_data:

                del self.market_data[symbol]

                removed = True

            self.last_refresh.pop(symbol, None)

            return removed

    # ==========================================================
    # SEARCH SYMBOL
    # ==========================================================

    def search(

        self,

        keyword: str,

    ) -> List[MarketData]:

        keyword = keyword.upper()

        return [

            data

            for data in self.market_data.values()

            if keyword in data.symbol.upper()

        ]

    # ==========================================================
    # TOP GAINERS
    # ==========================================================

    def top_gainers(

        self,

        limit: int = 10,

    ) -> List[MarketData]:

        return sorted(

            self.market_data.values(),

            key=lambda x: x.change_percent,

            reverse=True,

        )[:limit]

    # ==========================================================
    # TOP LOSERS
    # ==========================================================

    def top_losers(

        self,

        limit: int = 10,

    ) -> List[MarketData]:

        return sorted(

            self.market_data.values(),

            key=lambda x: x.change_percent,

        )[:limit]

    # ==========================================================
    # TOP VOLUME
    # ==========================================================

    def top_volume(

        self,

        limit: int = 10,

    ) -> List[MarketData]:

        return sorted(

            self.market_data.values(),

            key=lambda x: x.volume,

            reverse=True,

        )[:limit]

    # ==========================================================
    # TOP RELATIVE VOLUME
    # ==========================================================

    def top_relative_volume(

        self,

        limit: int = 10,

    ) -> List[MarketData]:

        return sorted(

            self.market_data.values(),

            key=lambda x: x.relative_volume,

            reverse=True,

        )[:limit]

    # ==========================================================
    # GAP UP
    # ==========================================================

    def gap_up(

        self,

        minimum_gap: float = 2.0,

    ) -> List[MarketData]:

        return [

            data

            for data in self.market_data.values()

            if data.gap_percent >= minimum_gap

        ]

    # ==========================================================
    # GAP DOWN
    # ==========================================================

    def gap_down(

        self,

        minimum_gap: float = -2.0,

    ) -> List[MarketData]:

        return [

            data

            for data in self.market_data.values()

            if data.gap_percent <= minimum_gap

        ]

    # ==========================================================
    # DAY BREAKOUTS
    # ==========================================================

    def day_breakouts(

        self,

    ) -> List[MarketData]:

        return [

            data

            for data in self.market_data.values()

            if data.day_high_breakout

        ]

    # ==========================================================
    # WEEK BREAKOUTS
    # ==========================================================

    def week_breakouts(

        self,

    ) -> List[MarketData]:

        return [

            data

            for data in self.market_data.values()

            if data.week_high_breakout

        ]

    # ==========================================================
    # MONTH BREAKOUTS
    # ==========================================================

    def month_breakouts(

        self,

    ) -> List[MarketData]:

        return [

            data

            for data in self.market_data.values()

            if data.month_high_breakout

        ]

    # ==========================================================
    # ALL TIME HIGH BREAKOUTS
    # ==========================================================

    def all_time_high_breakouts(

        self,

    ) -> List[MarketData]:

        return [

            data

            for data in self.market_data.values()

            if data.all_time_high_breakout

        ]

    # ==========================================================
    # ABOVE EMA 20
    # ==========================================================

    def above_ema20(

        self,

    ) -> List[MarketData]:

        return [

            data

            for data in self.market_data.values()

            if data.last_price > data.ema20

        ]

    # ==========================================================
    # ABOVE EMA 50
    # ==========================================================

    def above_ema50(

        self,

    ) -> List[MarketData]:

        return [

            data

            for data in self.market_data.values()

            if data.last_price > data.ema50

        ]

    # ==========================================================
    # ABOVE EMA 200
    # ==========================================================

    def above_ema200(

        self,

    ) -> List[MarketData]:

        return [

            data

            for data in self.market_data.values()

            if data.last_price > data.ema200

        ]

    # ==========================================================
    # STRONG MOMENTUM
    # ==========================================================

    def strong_momentum(

        self,

        minimum_rsi: float = 60,

        minimum_adx: float = 25,

    ) -> List[MarketData]:

        return [

            data

            for data in self.market_data.values()

            if (

                data.rsi >= minimum_rsi

                and

                data.adx >= minimum_adx

                and

                data.last_price > data.ema20

            )

        ]

    # ==========================================================
    # HIGH QUALITY BREAKOUT
    # ==========================================================

    def quality_breakouts(

        self,

    ) -> List[MarketData]:

        return [

            data

            for data in self.market_data.values()

            if (

                data.day_high_breakout

                and

                data.relative_volume >= 2.0

                and

                data.adx >= 25

                and

                data.last_price > data.vwap

                and

                data.last_price > data.ema20

            )

        ]
        # ==========================================================
    # TOTAL SYMBOLS
    # ==========================================================

    def total_symbols(self) -> int:

        return len(

            self.market_data

        )

    # ==========================================================
    # CACHE STATISTICS
    # ==========================================================

    def cache_statistics(

        self,

    ) -> Dict[str, int]:

        return {

            "market_data": len(

                self.market_data

            ),

            "candles": len(

                self.candle_cache

            ),

            "indicators": len(

                self.indicator_cache

            ),

            "last_refresh": len(

                self.last_refresh

            ),

        }

    # ==========================================================
    # HEALTH
    # ==========================================================

    def health(self) -> Dict[str, Any]:

        return {

            "running": self.running,

            "market_open": self.market_open(),

            "refresh_interval": self.refresh_interval,

            "symbols": len(

                self.market_data

            ),

            "cache": self.cache_statistics(),

        }

    # ==========================================================
    # STARTUP
    # ==========================================================

    def startup(self) -> Dict[str, Any]:
        """
        Starts the Market Data Manager.
        """

        self.start()

        return self.health()

    # ==========================================================
    # SHUTDOWN
    # ==========================================================

    def shutdown(self) -> Dict[str, Any]:
        """
        Stops the Market Data Manager.
        """

        self.stop()

        return self.health()

    # ==========================================================
    # RELOAD
    # ==========================================================

    def reload(self) -> None:

        self.clear_cache()

        self.refresh()

    # ==========================================================
    # GET ALL SYMBOL NAMES
    # ==========================================================

    def symbols(

        self,

    ) -> List[str]:

        return sorted(

            self.market_data.keys()

        )

    # ==========================================================
    # SNAPSHOT
    # ==========================================================

    def snapshot(

        self,

    ) -> Dict[str, MarketData]:

        with self._lock:

            return dict(

                self.market_data

            )

    # ==========================================================
    # REMOVE ALL DATA
    # ==========================================================

    def reset(self) -> None:

        self.stop()

        self.clear_cache()

    # ==========================================================
    # REPR
    # ==========================================================

    def __repr__(self) -> str:

        return (

            "MarketDataManager("

            f"symbols={len(self.market_data)}, "

            f"running={self.running}"

            ")"

        )

    # ==========================================================
    # STR
    # ==========================================================

    def __str__(self) -> str:

        stats = self.health()

        return (

            "Market Data Manager\n"

            f"Running          : {stats['running']}\n"

            f"Market Open      : {stats['market_open']}\n"

            f"Symbols          : {stats['symbols']}\n"

            f"Candle Cache     : {stats['cache']['candles']}\n"

            f"Indicator Cache  : {stats['cache']['indicators']}"

        )


# ==========================================================
# GLOBAL SINGLETON
# ==========================================================

market_data_manager = MarketDataManager()


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [

    "MarketData",

    "MarketDataManager",

    "market_data_manager",

]