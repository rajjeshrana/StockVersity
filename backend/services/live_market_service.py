from __future__ import annotations

import threading
import time
from datetime import datetime
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from backend.core.market_data_manager import (
    market_data_manager,
)

from backend.services.yahoo_service import (
    YahooService,
)

from backend.services.nse_service import (
    NSEService,
)


# ==========================================================
# LIVE TICK
# ==========================================================

@dataclass(slots=True)
class LiveTick:

    symbol: str

    price: float

    open: float

    high: float

    low: float

    close: float

    volume: int

    bid: float = 0

    ask: float = 0

    change: float = 0

    change_percent: float = 0

    timestamp: datetime = field(
        default_factory=datetime.now
    )


# ==========================================================
# LIVE MARKET SERVICE
# ==========================================================

class LiveMarketService:

    REFRESH_INTERVAL = 5

    MAX_RETRY = 5

    def __init__(self):

        self.market = market_data_manager

        self.yahoo = YahooService()

        self.nse = NSEService()

        self.running = False

        self.connected = False

        self.retry_count = 0

        self.last_update: Optional[
            datetime
        ] = None

        self.symbols: List[str] = []

        self.tick_cache: Dict[
            str,
            LiveTick,
        ] = {}

        self.callbacks: List[
            Callable
        ] = []

        self.worker: Optional[
            threading.Thread
        ] = None

        self.lock = threading.RLock()

    # ==========================================================
    # SYMBOLS
    # ==========================================================

    def set_symbols(

        self,

        symbols: List[str],

    ):

        with self.lock:

            self.symbols = sorted(

                list(

                    set(symbols)

                )

            )

    def add_symbol(

        self,

        symbol: str,

    ):

        with self.lock:

            if symbol not in self.symbols:

                self.symbols.append(

                    symbol

                )

    def remove_symbol(

        self,

        symbol: str,

    ):

        with self.lock:

            if symbol in self.symbols:

                self.symbols.remove(

                    symbol

                )

    # ==========================================================
    # CALLBACKS
    # ==========================================================

    def register(

        self,

        callback: Callable,

    ):

        if callback not in self.callbacks:

            self.callbacks.append(

                callback

            )

    def unregister(

        self,

        callback: Callable,

    ):

        if callback in self.callbacks:

            self.callbacks.remove(

                callback

            )

    def notify(

        self,

        tick: LiveTick,

    ):

        for callback in self.callbacks:

            try:

                callback(

                    tick

                )

            except Exception:

                pass

    # ==========================================================
    # CACHE
    # ==========================================================

    def update_cache(

        self,

        tick: LiveTick,

    ):

        self.tick_cache[

            tick.symbol

        ] = tick

    # ==========================================================
    # MARKET STATUS
    # ==========================================================

    def market_open(

        self,

    ) -> bool:

        return self.market.is_market_open()

    # ==========================================================
    # CONNECT
    # ==========================================================

    def connect(

        self,

    ) -> bool:

        if self.connected:

            return True

        try:

            self.nse.connect()

            self.connected = True

            self.retry_count = 0

            return True

        except Exception:

            try:

                self.yahoo.connect()

                self.connected = True

                self.retry_count = 0

                return True

            except Exception:

                self.connected = False

                return False

    # ==========================================================
    # DISCONNECT
    # ==========================================================

    def disconnect(

        self,

    ):

        try:

            self.nse.disconnect()

        except Exception:

            pass

        try:

            self.yahoo.disconnect()

        except Exception:

            pass

        self.connected = False

    # ==========================================================
    # RECONNECT
    # ==========================================================

    def reconnect(

        self,

    ) -> bool:

        self.disconnect()

        while (

            self.retry_count <

            self.MAX_RETRY

        ):

            self.retry_count += 1

            if self.connect():

                return True

            time.sleep(2)

        return False

    # ==========================================================
    # FETCH FROM NSE
    # ==========================================================

    def fetch_nse(

        self,

        symbol: str,

    ) -> Optional[LiveTick]:

        try:

            data = self.nse.quote(

                symbol

            )

            if data is None:

                return None

            return LiveTick(

                symbol=symbol,

                price=data.last_price,

                open=data.open,

                high=data.high,

                low=data.low,

                close=data.previous_close,

                volume=data.volume,

                bid=data.bid,

                ask=data.ask,

                change=data.change,

                change_percent=data.change_percent,

            )

        except Exception:

            return None

    # ==========================================================
    # FETCH FROM YAHOO
    # ==========================================================

    def fetch_yahoo(

        self,

        symbol: str,

    ) -> Optional[LiveTick]:

        try:

            data = self.yahoo.quote(

                symbol

            )

            if data is None:

                return None

            return LiveTick(

                symbol=symbol,

                price=data.last_price,

                open=data.open,

                high=data.high,

                low=data.low,

                close=data.previous_close,

                volume=data.volume,

                bid=0,

                ask=0,

                change=data.change,

                change_percent=data.change_percent,

            )

        except Exception:

            return None

    # ==========================================================
    # FETCH LIVE TICK
    # ==========================================================

    def fetch_tick(

        self,

        symbol: str,

    ) -> Optional[LiveTick]:

        tick = self.fetch_nse(

            symbol

        )

        if tick:

            return tick

        return self.fetch_yahoo(

            symbol

        )

    # ==========================================================
    # UPDATE MARKET DATA MANAGER
    # ==========================================================

    def publish_tick(

        self,

        tick: LiveTick,

    ):

        self.update_cache(

            tick

        )

        self.market.update_live_tick(

            symbol=tick.symbol,

            price=tick.price,

            volume=tick.volume,

            high=tick.high,

            low=tick.low,

            change=tick.change,

            change_percent=tick.change_percent,

        )

        self.notify(

            tick

        )

        self.last_update = datetime.now()
            # ==========================================================
    # UPDATE ALL SYMBOLS
    # ==========================================================

    def update_all_symbols(

        self,

    ):

        with self.lock:

            symbols = list(

                self.symbols

            )

        for symbol in symbols:

            try:

                tick = self.fetch_tick(

                    symbol

                )

                if tick is None:

                    continue

                self.publish_tick(

                    tick

                )

            except Exception:

                continue

    # ==========================================================
    # DYNAMIC REFRESH INTERVAL
    # ==========================================================

    def refresh_interval(

        self,

    ) -> int:

        if self.market_open():

            return self.REFRESH_INTERVAL

        return 60

    # ==========================================================
    # LIVE UPDATE LOOP
    # ==========================================================

    def update_loop(

        self,

    ):

        while self.running:

            try:

                if not self.connected:

                    if not self.reconnect():

                        time.sleep(5)

                        continue

                self.update_all_symbols()

            except Exception:

                self.connected = False

                time.sleep(2)

                continue

            time.sleep(

                self.refresh_interval()

            )

    # ==========================================================
    # START LIVE SERVICE
    # ==========================================================

    def start(

        self,

    ):

        if self.running:

            return

        self.running = True

        if not self.connect():

            self.reconnect()

        self.worker = threading.Thread(

            target=self.update_loop,

            daemon=True,

            name="LiveMarketService",

        )

        self.worker.start()

    # ==========================================================
    # STOP LIVE SERVICE
    # ==========================================================

    def stop(

        self,

    ):

        self.running = False

        self.disconnect()

        if (

            self.worker

            and

            self.worker.is_alive()

        ):

            self.worker.join(

                timeout=5

            )

        self.worker = None

    # ==========================================================
    # RESTART
    # ==========================================================

    def restart(

        self,

    ):

        self.stop()

        self.start()

    # ==========================================================
    # FORCE REFRESH
    # ==========================================================

    def refresh_now(

        self,

    ):

        if not self.connected:

            self.connect()

        self.update_all_symbols()

    # ==========================================================
    # WAIT FOR FIRST UPDATE
    # ==========================================================

    def wait_until_ready(

        self,

        timeout: int = 20,

    ) -> bool:

        start = time.time()

        while (

            time.time() - start

            < timeout

        ):

            if self.last_update:

                return True

            time.sleep(

                0.25

            )

        return False

    # ==========================================================
    # SYMBOL STATUS
    # ==========================================================

    def symbol_status(

        self,

        symbol: str,

    ) -> Dict:

        tick = self.tick_cache.get(

            symbol

        )

        if tick is None:

            return {

                "symbol": symbol,

                "status": "offline",

            }

        return {

            "symbol": symbol,

            "status": "live",

            "price": tick.price,

            "change": tick.change,

            "change_percent": tick.change_percent,

            "volume": tick.volume,

            "updated": tick.timestamp,

        }

    # ==========================================================
    # ALL LIVE TICKS
    # ==========================================================

    def live_ticks(

        self,

    ) -> List[LiveTick]:

        return list(

            self.tick_cache.values()

        )
        # ==========================================================
    # TICK HISTORY
    # ==========================================================

    def initialize_history(

        self,

    ):

        self.tick_history: Dict[

            str,

            List[LiveTick]

        ] = {}

        self.completed_candles: Dict[

            str,

            List[Dict]

        ] = {}

    # ==========================================================
    # SAVE TICK
    # ==========================================================

    def save_tick(

        self,

        tick: LiveTick,

    ):

        history = self.tick_history.setdefault(

            tick.symbol,

            [],

        )

        history.append(

            tick

        )

        if len(history) > 5000:

            del history[:-5000]

    # ==========================================================
    # BUILD 1 MIN CANDLE
    # ==========================================================

    def build_1m_candle(

        self,

        symbol: str,

    ) -> Optional[Dict]:

        ticks = self.tick_history.get(

            symbol,

            [],

        )

        if len(ticks) < 2:

            return None

        latest = ticks[-1]

        minute = latest.timestamp.replace(

            second=0,

            microsecond=0,

        )

        candle_ticks = [

            t

            for t in ticks

            if t.timestamp.replace(

                second=0,

                microsecond=0,

            ) == minute

        ]

        if not candle_ticks:

            return None

        candle = {

            "datetime": minute,

            "open": candle_ticks[0].price,

            "high": max(

                t.price

                for t in candle_ticks

            ),

            "low": min(

                t.price

                for t in candle_ticks

            ),

            "close": candle_ticks[-1].price,

            "volume": sum(

                t.volume

                for t in candle_ticks

            ),

        }

        return candle

    # ==========================================================
    # AGGREGATE CANDLES
    # ==========================================================

    def aggregate(

        self,

        symbol: str,

        timeframe: int,

    ) -> Optional[Dict]:

        candles = self.completed_candles.get(

            symbol,

            [],

        )

        if len(candles) < timeframe:

            return None

        group = candles[-timeframe:]

        return {

            "datetime": group[0]["datetime"],

            "open": group[0]["open"],

            "high": max(

                c["high"]

                for c in group

            ),

            "low": min(

                c["low"]

                for c in group

            ),

            "close": group[-1]["close"],

            "volume": sum(

                c["volume"]

                for c in group

            ),

        }

    # ==========================================================
    # COMPLETE CURRENT CANDLE
    # ==========================================================

    def complete_candle(

        self,

        symbol: str,

    ):

        candle = self.build_1m_candle(

            symbol

        )

        if candle is None:

            return

        candles = self.completed_candles.setdefault(

            symbol,

            [],

        )

        if (

            candles

            and

            candles[-1]["datetime"]

            == candle["datetime"]

        ):

            candles[-1] = candle

        else:

            candles.append(

                candle

            )

        if len(candles) > 3000:

            del candles[:-3000]

    # ==========================================================
    # BUILD MULTI-TIMEFRAME
    # ==========================================================

    def update_timeframes(

        self,

        symbol: str,

    ):

        candle_1m = self.aggregate(

            symbol,

            1,

        )

        candle_5m = self.aggregate(

            symbol,

            5,

        )

        candle_15m = self.aggregate(

            symbol,

            15,

        )

        candle_30m = self.aggregate(

            symbol,

            30,

        )

        candle_60m = self.aggregate(

            symbol,

            60,

        )

        if candle_1m:

            self.market.update_candle(

                symbol,

                "1m",

                candle_1m,

            )

        if candle_5m:

            self.market.update_candle(

                symbol,

                "5m",

                candle_5m,

            )

        if candle_15m:

            self.market.update_candle(

                symbol,

                "15m",

                candle_15m,

            )

        if candle_30m:

            self.market.update_candle(

                symbol,

                "30m",

                candle_30m,

            )

        if candle_60m:

            self.market.update_candle(

                symbol,

                "1h",

                candle_60m,

            )

    # ==========================================================
    # PROCESS LIVE TICK
    # ==========================================================

    def process_tick(

        self,

        tick: LiveTick,

    ):

        self.save_tick(

            tick

        )

        self.publish_tick(

            tick

        )

        self.complete_candle(

            tick.symbol

        )

        self.update_timeframes(

            tick.symbol

        )

    # ==========================================================
    # PROCESS MULTIPLE TICKS
    # ==========================================================

    def process_ticks(

        self,

        ticks: List[LiveTick],

    ):

        for tick in ticks:

            self.process_tick(

                tick

            )
                # ==========================================================
    # SCANNER INTEGRATION
    # ==========================================================

    def attach_scanner(

        self,

        scanner,

    ):

        self.scanner = scanner

    # ==========================================================
    # ORCHESTRATOR INTEGRATION
    # ==========================================================

    def attach_orchestrator(

        self,

        orchestrator,

    ):

        self.orchestrator = orchestrator

    # ==========================================================
    # AI MANAGER
    # ==========================================================

    def attach_ai(

        self,

        ai_manager,

    ):

        self.ai_manager = ai_manager

    # ==========================================================
    # SECTOR MANAGER
    # ==========================================================

    def attach_sector_manager(

        self,

        sector_manager,

    ):

        self.sector_manager = sector_manager

    # ==========================================================
    # UPDATE ANALYTICS
    # ==========================================================

    def update_analytics(

        self,

        symbol: str,

    ):

        try:

            if hasattr(

                self,

                "sector_manager",

            ):

                self.sector_manager.update_stock(

                    symbol

                )

        except Exception:

            pass

        try:

            if hasattr(

                self,

                "ai_manager",

            ):

                self.ai_manager.analyze(

                    symbol

                )

        except Exception:

            pass

    # ==========================================================
    # TRIGGER SCANNER
    # ==========================================================

    def trigger_scanner(

        self,

        symbol: str,

    ):

        try:

            if hasattr(

                self,

                "scanner",

            ):

                self.scanner.scan_stock(

                    symbol

                )

        except Exception:

            pass

    # ==========================================================
    # ORCHESTRATOR EVENT
    # ==========================================================

    def trigger_orchestrator(

        self,

    ):

        try:

            if hasattr(

                self,

                "orchestrator",

            ):

                self.orchestrator.refresh()

        except Exception:

            pass

    # ==========================================================
    # PROCESS COMPLETE MARKET UPDATE
    # ==========================================================

    def process_market_update(

        self,

        tick: LiveTick,

    ):

        self.process_tick(

            tick

        )

        self.update_analytics(

            tick.symbol

        )

        self.trigger_scanner(

            tick.symbol

        )

    # ==========================================================
    # PROCESS BATCH UPDATE
    # ==========================================================

    def process_batch(

        self,

        ticks: List[LiveTick],

    ):

        for tick in ticks:

            self.process_market_update(

                tick

            )

        self.trigger_orchestrator()

    # ==========================================================
    # PERFORMANCE
    # ==========================================================

    def performance(

        self,

    ) -> Dict:

        return {

            "tracked_symbols": len(

                self.symbols

            ),

            "cached_ticks": len(

                self.tick_cache

            ),

            "connected": self.connected,

            "running": self.running,

            "last_update": self.last_update,

            "refresh_interval": self.refresh_interval(),

        }

    # ==========================================================
    # DASHBOARD SNAPSHOT
    # ==========================================================

    def dashboard_snapshot(

        self,

    ) -> Dict:

        gainers = sorted(

            self.tick_cache.values(),

            key=lambda t: t.change_percent,

            reverse=True,

        )[:5]

        losers = sorted(

            self.tick_cache.values(),

            key=lambda t: t.change_percent,

        )[:5]

        return {

            "market_status": (

                "OPEN"

                if self.market_open()

                else "CLOSED"

            ),

            "last_update": self.last_update,

            "tracked_symbols": len(

                self.symbols

            ),

            "gainers": gainers,

            "losers": losers,

        }

    # ==========================================================
    # BROADCAST EVENT
    # ==========================================================

    def broadcast(

        self,

        event: str,

        payload=None,

    ):

        for callback in self.callbacks:

            try:

                callback(

                    event,

                    payload,

                )

            except Exception:

                continue

    # ==========================================================
    # NOTIFY DASHBOARD
    # ==========================================================

    def notify_dashboard(

        self,

    ):

        self.broadcast(

            "dashboard_update",

            self.dashboard_snapshot(),

        )
            # ==========================================================
    # STATISTICS
    # ==========================================================

    def statistics(

        self,

    ) -> Dict:

        return {

            "tracked_symbols": len(self.symbols),

            "cached_ticks": len(self.tick_cache),

            "callbacks": len(self.callbacks),

            "connected": self.connected,

            "running": self.running,

            "retry_count": self.retry_count,

            "last_update": self.last_update,

        }

    # ==========================================================
    # HEALTH
    # ==========================================================

    def health(

        self,

    ) -> Dict:

        status = "healthy"

        if not self.connected:

            status = "disconnected"

        elif not self.running:

            status = "stopped"

        return {

            "status": status,

            "service": "Live Market Service",

            "statistics": self.statistics(),

        }

    # ==========================================================
    # RESET
    # ==========================================================

    def reset(

        self,

    ):

        with self.lock:

            self.symbols.clear()

            self.tick_cache.clear()

            self.callbacks.clear()

            if hasattr(self, "tick_history"):

                self.tick_history.clear()

            if hasattr(self, "completed_candles"):

                self.completed_candles.clear()

        self.connected = False

        self.retry_count = 0

        self.last_update = None

    # ==========================================================
    # RELOAD
    # ==========================================================

    def reload(

        self,

    ):

        self.stop()

        self.reset()

        self.initialize_history()

        self.start()

    # ==========================================================
    # STARTUP
    # ==========================================================

    def startup(

        self,

    ):

        self.initialize_history()

        self.start()

        return self.health()

    # ==========================================================
    # SHUTDOWN
    # ==========================================================

    def shutdown(

        self,

    ):

        self.stop()

        self.reset()

        return {

            "status": "shutdown",

        }

    # ==========================================================
    # VERSION
    # ==========================================================

    @property

    def version(

        self,

    ):

        return "4.0"

    # ==========================================================
    # NAME
    # ==========================================================

    @property

    def name(

        self,

    ):

        return "Live Market Service"

    # ==========================================================
    # REPR
    # ==========================================================

    def __repr__(

        self,

    ):

        return (

            "LiveMarketService("

            f"symbols={len(self.symbols)}, "

            f"connected={self.connected}, "

            f"running={self.running}"

            ")"

        )

    # ==========================================================
    # STR
    # ==========================================================

    def __str__(

        self,

    ):

        stats = self.statistics()

        return (

            "Live Market Service\n"

            f"Version           : {self.version}\n"

            f"Tracked Symbols   : {stats['tracked_symbols']}\n"

            f"Cached Ticks      : {stats['cached_ticks']}\n"

            f"Connected         : {stats['connected']}\n"

            f"Running           : {stats['running']}\n"

            f"Retry Count       : {stats['retry_count']}\n"

            f"Last Update       : {stats['last_update']}"

        )


# ==========================================================
# GLOBAL SINGLETON
# ==========================================================

live_market_service = LiveMarketService()


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [

    "LiveTick",

    "LiveMarketService",

    "live_market_service",

]
