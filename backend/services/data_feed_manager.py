from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any


# ==========================================================
# PROVIDER TYPE
# ==========================================================

class ProviderType(Enum):

    NSE = "NSE"

    YAHOO = "YAHOO"

    BROKER = "BROKER"

    WEBSOCKET = "WEBSOCKET"

    CUSTOM = "CUSTOM"


# ==========================================================
# PROVIDER STATUS
# ==========================================================

class ProviderStatus(Enum):

    ONLINE = "ONLINE"

    OFFLINE = "OFFLINE"

    CONNECTING = "CONNECTING"

    ERROR = "ERROR"


# ==========================================================
# PROVIDER INFORMATION
# ==========================================================

@dataclass(slots=True)
class ProviderInfo:

    name: str

    provider_type: ProviderType

    priority: int

    enabled: bool = True

    status: ProviderStatus = ProviderStatus.OFFLINE

    connected: bool = False

    latency: float = 0.0

    requests: int = 0

    failures: int = 0

    last_success: Optional[
        datetime
    ] = None

    last_failure: Optional[
        datetime
    ] = None

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )


# ==========================================================
# DATA FEED MANAGER
# ==========================================================

class DataFeedManager:

    def __init__(self):

        self.providers: Dict[
            str,
            Any,
        ] = {}

        self.provider_info: Dict[
            str,
            ProviderInfo,
        ] = {}

        self.primary_provider = None

        self.fallback_provider = None

        self.lock = threading.RLock()

        self.symbols = set()

        self.refresh_interval = 5

        self.running = False

        self.worker = None

    # ==========================================================
    # REGISTER PROVIDER
    # ==========================================================

    def register_provider(

        self,

        name: str,

        provider,

        provider_type: ProviderType,

        priority: int,

    ):

        with self.lock:

            self.providers[name] = provider

            self.provider_info[name] = ProviderInfo(

                name=name,

                provider_type=provider_type,

                priority=priority,

            )

            self._sort_providers()

    # ==========================================================
    # SORT PROVIDERS
    # ==========================================================

    def _sort_providers(

        self,

    ):

        ordered = sorted(

            self.provider_info.values(),

            key=lambda x: x.priority,

        )

        if ordered:

            self.primary_provider = ordered[0].name

        if len(ordered) > 1:

            self.fallback_provider = ordered[1].name

    # ==========================================================
    # ENABLE PROVIDER
    # ==========================================================

    def enable_provider(

        self,

        name: str,

    ):

        if name in self.provider_info:

            self.provider_info[

                name

            ].enabled = True

    # ==========================================================
    # DISABLE PROVIDER
    # ==========================================================

    def disable_provider(

        self,

        name: str,

    ):

        if name in self.provider_info:

            self.provider_info[

                name

            ].enabled = False

    # ==========================================================
    # GET PROVIDER
    # ==========================================================

    def provider(

        self,

        name: str,

    ):

        return self.providers.get(

            name

        )

    # ==========================================================
    # REGISTER SYMBOL
    # ==========================================================

    def add_symbol(

        self,

        symbol: str,

    ):

        self.symbols.add(

            symbol.upper()

        )
    # ==========================================================
    # CONNECT PROVIDER
    # ==========================================================

    def connect_provider(

        self,

        name: str,

    ) -> bool:

        info = self.provider_info.get(

            name

        )

        provider = self.providers.get(

            name

        )

        if (

            info is None

            or

            provider is None

            or

            not info.enabled

        ):

            return False

        try:

            info.status = ProviderStatus.CONNECTING

            provider.connect()

            info.connected = True

            info.status = ProviderStatus.ONLINE

            info.last_success = datetime.now()

            return True

        except Exception:

            info.connected = False

            info.status = ProviderStatus.ERROR

            info.failures += 1

            info.last_failure = datetime.now()

            return False

    # ==========================================================
    # DISCONNECT PROVIDER
    # ==========================================================

    def disconnect_provider(

        self,

        name: str,

    ):

        provider = self.providers.get(

            name

        )

        info = self.provider_info.get(

            name

        )

        if provider is None:

            return

        try:

            provider.disconnect()

        except Exception:

            pass

        if info:

            info.connected = False

            info.status = ProviderStatus.OFFLINE

    # ==========================================================
    # CONNECT ALL
    # ==========================================================

    def connect_all(

        self,

    ):

        for name in self.providers:

            self.connect_provider(

                name

            )

    # ==========================================================
    # DISCONNECT ALL
    # ==========================================================

    def disconnect_all(

        self,

    ):

        for name in self.providers:

            self.disconnect_provider(

                name

            )

    # ==========================================================
    # PROVIDER HEALTH
    # ==========================================================

    def provider_health(

        self,

        name: str,

    ) -> Dict:

        info = self.provider_info.get(

            name

        )

        if info is None:

            return {}

        return {

            "name": info.name,

            "status": info.status.value,

            "connected": info.connected,

            "latency": info.latency,

            "requests": info.requests,

            "failures": info.failures,

            "enabled": info.enabled,

            "last_success": info.last_success,

            "last_failure": info.last_failure,

        }

    # ==========================================================
    # BEST PROVIDER
    # ==========================================================

    def best_provider(

        self,

    ):

        providers = sorted(

            self.provider_info.values(),

            key=lambda p: (

                not p.connected,

                p.failures,

                p.priority,

                p.latency,

            ),

        )

        for provider in providers:

            if (

                provider.enabled

                and

                provider.connected

            ):

                return self.providers.get(

                    provider.name

                )

        return None

    # ==========================================================
    # GET QUOTE
    # ==========================================================

    def quote(

        self,

        symbol: str,

    ):

        provider = self.best_provider()

        if provider is None:

            return None

        info = self.provider_info.get(

            self.primary_provider

        )

        try:

            result = provider.quote(

                symbol

            )

            if info:

                info.requests += 1

                info.last_success = datetime.now()

            return result

        except Exception:

            if info:

                info.failures += 1

                info.last_failure = datetime.now()

            return self.quote_fallback(

                symbol

            )

    # ==========================================================
    # FALLBACK QUOTE
    # ==========================================================

    def quote_fallback(

        self,

        symbol: str,

    ):

        if self.fallback_provider is None:

            return None

        provider = self.providers.get(

            self.fallback_provider

        )

        if provider is None:

            return None

        try:

            return provider.quote(

                symbol

            )

        except Exception:

            return None

    # ==========================================================
    # HISTORICAL DATA
    # ==========================================================

    def history(

        self,

        symbol: str,

        interval: str,

        period: str,

    ):

        provider = self.best_provider()

        if provider is None:

            return None

        try:

            return provider.history(

                symbol,

                interval,

                period,

            )

        except Exception:

            return None
        import time


    # ==========================================================
    # LATENCY TEST
    # ==========================================================

    def measure_latency(

        self,

        name: str,

    ) -> float:

        provider = self.providers.get(

            name

        )

        info = self.provider_info.get(

            name

        )

        if provider is None or info is None:

            return -1

        try:

            start = time.perf_counter()

            provider.ping()

            latency = (

                time.perf_counter() - start

            ) * 1000

            info.latency = round(

                latency,

                2,

            )

            info.last_success = datetime.now()

            return info.latency

        except Exception:

            info.failures += 1

            info.status = ProviderStatus.ERROR

            info.last_failure = datetime.now()

            return -1

    # ==========================================================
    # HEALTH CHECK
    # ==========================================================

    def health_check(

        self,

    ):

        for name in list(

            self.providers.keys()

        ):

            info = self.provider_info.get(

                name

            )

            if info is None:

                continue

            latency = self.measure_latency(

                name

            )

            if latency < 0:

                info.connected = False

                info.status = ProviderStatus.ERROR

            else:

                info.connected = True

                info.status = ProviderStatus.ONLINE

    # ==========================================================
    # FAILOVER
    # ==========================================================

    def failover(

        self,

    ):

        current = self.provider_info.get(

            self.primary_provider

        )

        if (

            current

            and

            current.connected

        ):

            return

        providers = sorted(

            self.provider_info.values(),

            key=lambda p: (

                not p.connected,

                p.failures,

                p.priority,

                p.latency,

            ),

        )

        for provider in providers:

            if (

                provider.enabled

                and

                provider.connected

            ):

                self.primary_provider = (

                    provider.name

                )

                break

    # ==========================================================
    # SYNC SYMBOLS
    # ==========================================================

    def sync_symbols(

        self,

    ):

        for provider in self.providers.values():

            try:

                provider.set_symbols(

                    sorted(

                        self.symbols

                    )

                )

            except Exception:

                continue

    # ==========================================================
    # BACKGROUND LOOP
    # ==========================================================

    def worker_loop(

        self,

    ):

        while self.running:

            try:

                self.health_check()

                self.failover()

                self.sync_symbols()

            except Exception:

                pass

            time.sleep(

                self.refresh_interval

            )

    # ==========================================================
    # START
    # ==========================================================

    def start(

        self,

    ):

        if self.running:

            return

        self.running = True

        self.connect_all()

        self.worker = threading.Thread(

            target=self.worker_loop,

            daemon=True,

            name="DataFeedManager",

        )

        self.worker.start()

    # ==========================================================
    # STOP
    # ==========================================================

    def stop(

        self,

    ):

        self.running = False

        self.disconnect_all()

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
    # FORCE HEALTH CHECK
    # ==========================================================

    def refresh(

        self,

    ):

        self.health_check()

        self.failover()

    # ==========================================================
    # CONNECTED PROVIDERS
    # ==========================================================

    def connected_providers(

        self,

    ) -> List[str]:

        return [

            info.name

            for info in

            self.provider_info.values()

            if info.connected

        ]
        # ==========================================================
    # REQUEST CACHE
    # ==========================================================

    def initialize_cache(

        self,

    ):

        self.quote_cache: Dict[

            str,

            tuple[Any, datetime]

        ] = {}

        self.history_cache: Dict[

            str,

            tuple[Any, datetime]

        ] = {}

        self.cache_timeout = 10

    # ==========================================================
    # CACHE VALID
    # ==========================================================

    def cache_valid(

        self,

        timestamp: datetime,

    ) -> bool:

        return (

            datetime.now() - timestamp

        ).total_seconds() < self.cache_timeout

    # ==========================================================
    # QUOTE WITH CACHE
    # ==========================================================

    def cached_quote(

        self,

        symbol: str,

    ):

        item = self.quote_cache.get(

            symbol

        )

        if item:

            value, ts = item

            if self.cache_valid(

                ts

            ):

                return value

        quote = self.quote(

            symbol

        )

        if quote is not None:

            self.quote_cache[

                symbol

            ] = (

                quote,

                datetime.now(),

            )

        return quote

    # ==========================================================
    # BATCH QUOTES
    # ==========================================================

    def batch_quotes(

        self,

        symbols: List[str],

    ) -> Dict[str, Any]:

        results = {}

        for symbol in symbols:

            try:

                results[

                    symbol

                ] = self.cached_quote(

                    symbol

                )

            except Exception:

                results[

                    symbol

                ] = None

        return results

    # ==========================================================
    # CACHED HISTORY
    # ==========================================================

    def cached_history(

        self,

        symbol: str,

        interval: str,

        period: str,

    ):

        key = (

            f"{symbol}_{interval}_{period}"

        )

        item = self.history_cache.get(

            key

        )

        if item:

            value, ts = item

            if self.cache_valid(

                ts

            ):

                return value

        history = self.history(

            symbol,

            interval,

            period,

        )

        if history is not None:

            self.history_cache[

                key

            ] = (

                history,

                datetime.now(),

            )

        return history

    # ==========================================================
    # BATCH HISTORY
    # ==========================================================

    def batch_history(

        self,

        symbols: List[str],

        interval: str,

        period: str,

    ) -> Dict[str, Any]:

        output = {}

        for symbol in symbols:

            output[

                symbol

            ] = self.cached_history(

                symbol,

                interval,

                period,

            )

        return output

    # ==========================================================
    # RATE LIMIT
    # ==========================================================

    def rate_limit(

        self,

        delay: float = 0.10,

    ):

        time.sleep(

            delay

        )

    # ==========================================================
    # RETRY REQUEST
    # ==========================================================

    def retry_quote(

        self,

        symbol: str,

        retries: int = 3,

    ):

        for _ in range(

            retries

        ):

            result = self.quote(

                symbol

            )

            if result is not None:

                return result

            self.rate_limit(

                0.5

            )

        return None

    # ==========================================================
    # PREFETCH
    # ==========================================================

    def prefetch_quotes(

        self,

    ):

        for symbol in sorted(

            self.symbols

        ):

            try:

                self.cached_quote(

                    symbol

                )

            except Exception:

                continue

    # ==========================================================
    # CLEAR CACHE
    # ==========================================================

    def clear_cache(

        self,

    ):

        self.quote_cache.clear()

        self.history_cache.clear()
        from concurrent.futures import ThreadPoolExecutor, as_completed


    # ==========================================================
    # REQUEST QUEUE
    # ==========================================================

    def initialize_queue(

        self,

    ):

        self.executor = ThreadPoolExecutor(

            max_workers=8,

            thread_name_prefix="DataFeed",

        )

        self.max_workers = 8

    # ==========================================================
    # CONCURRENT QUOTE
    # ==========================================================

    def concurrent_quotes(

        self,

        symbols: List[str],

    ) -> Dict[str, Any]:

        results = {}

        futures = {}

        for symbol in symbols:

            future = self.executor.submit(

                self.cached_quote,

                symbol,

            )

            futures[future] = symbol

        for future in as_completed(

            futures

        ):

            symbol = futures[future]

            try:

                results[symbol] = future.result()

            except Exception:

                results[symbol] = None

        return results

    # ==========================================================
    # CONCURRENT HISTORY
    # ==========================================================

    def concurrent_history(

        self,

        symbols: List[str],

        interval: str,

        period: str,

    ) -> Dict[str, Any]:

        output = {}

        futures = {}

        for symbol in symbols:

            future = self.executor.submit(

                self.cached_history,

                symbol,

                interval,

                period,

            )

            futures[future] = symbol

        for future in as_completed(

            futures

        ):

            symbol = futures[future]

            try:

                output[symbol] = future.result()

            except Exception:

                output[symbol] = None

        return output

    # ==========================================================
    # PROVIDER UTILIZATION
    # ==========================================================

    def provider_usage(

        self,

    ) -> Dict[str, Dict]:

        usage = {}

        for name, info in self.provider_info.items():

            usage[name] = {

                "requests": info.requests,

                "failures": info.failures,

                "latency": info.latency,

                "connected": info.connected,

                "enabled": info.enabled,

                "status": info.status.value,

            }

        return usage

    # ==========================================================
    # LOAD BALANCER
    # ==========================================================

    def optimize_provider_order(

        self,

    ):

        ordered = sorted(

            self.provider_info.values(),

            key=lambda p: (

                not p.connected,

                p.failures,

                p.latency,

                p.priority,

            ),

        )

        if ordered:

            self.primary_provider = ordered[0].name

        if len(ordered) > 1:

            self.fallback_provider = ordered[1].name

    # ==========================================================
    # PERFORMANCE METRICS
    # ==========================================================

    def performance_metrics(

        self,

    ) -> Dict:

        connected = len(

            [

                p

                for p in

                self.provider_info.values()

                if p.connected

            ]

        )

        total_requests = sum(

            p.requests

            for p in

            self.provider_info.values()

        )

        total_failures = sum(

            p.failures

            for p in

            self.provider_info.values()

        )

        average_latency = 0.0

        latencies = [

            p.latency

            for p in

            self.provider_info.values()

            if p.latency > 0

        ]

        if latencies:

            average_latency = round(

                sum(latencies)

                /

                len(latencies),

                2,

            )

        return {

            "providers": len(

                self.providers

            ),

            "connected": connected,

            "requests": total_requests,

            "failures": total_failures,

            "average_latency": average_latency,

            "cached_quotes": len(

                self.quote_cache

            ),

            "cached_history": len(

                self.history_cache

            ),

        }

    # ==========================================================
    # DASHBOARD DATA
    # ==========================================================

    def dashboard_data(

        self,

    ) -> Dict:

        return {

            "primary_provider": self.primary_provider,

            "fallback_provider": self.fallback_provider,

            "performance": self.performance_metrics(),

            "provider_usage": self.provider_usage(),

            "tracked_symbols": len(

                self.symbols

            ),

        }

    # ==========================================================
    # AUTO OPTIMIZATION
    # ==========================================================

    def optimize(

        self,

    ):

        self.refresh()

        self.optimize_provider_order()

        self.prefetch_quotes()
            # ==========================================================
    # STATISTICS
    # ==========================================================

    def statistics(

        self,

    ) -> Dict:

        return {

            "providers": len(

                self.providers

            ),

            "tracked_symbols": len(

                self.symbols

            ),

            "primary_provider": self.primary_provider,

            "fallback_provider": self.fallback_provider,

            "running": self.running,

            "performance": self.performance_metrics(),

        }

    # ==========================================================
    # HEALTH
    # ==========================================================

    def health(

        self,

    ) -> Dict:

        healthy = all(

            info.connected

            for info in

            self.provider_info.values()

            if info.enabled

        )

        return {

            "status": (

                "healthy"

                if healthy

                else "degraded"

            ),

            "statistics": self.statistics(),

        }

    # ==========================================================
    # RESET
    # ==========================================================

    def reset(

        self,

    ):

        self.stop()

        self.clear_cache()

        self.symbols.clear()

        self.providers.clear()

        self.provider_info.clear()

        self.primary_provider = None

        self.fallback_provider = None

    # ==========================================================
    # RELOAD
    # ==========================================================

    def reload(

        self,

    ):

        self.clear_cache()

        self.optimize()

    # ==========================================================
    # STARTUP
    # ==========================================================

    def startup(

        self,

    ):

        self.initialize_cache()

        self.initialize_queue()

        self.connect_all()

        self.start()

        return self.health()

    # ==========================================================
    # SHUTDOWN
    # ==========================================================

    def shutdown(

        self,

    ):

        self.stop()

        self.disconnect_all()

        if hasattr(

            self,

            "executor",

        ):

            self.executor.shutdown(

                wait=True,

                cancel_futures=False,

            )

        self.clear_cache()

        return {

            "status": "shutdown",

        }

    # ==========================================================
    # VERSION
    # ==========================================================

    @property

    def version(

        self,

    ) -> str:

        return "4.0"

    # ==========================================================
    # NAME
    # ==========================================================

    @property

    def name(

        self,

    ) -> str:

        return "Data Feed Manager"

    # ==========================================================
    # REPR
    # ==========================================================

    def __repr__(

        self,

    ):

        return (

            "DataFeedManager("

            f"providers={len(self.providers)}, "

            f"symbols={len(self.symbols)}, "

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

            "Data Feed Manager\n"

            f"Version            : {self.version}\n"

            f"Providers          : {stats['providers']}\n"

            f"Tracked Symbols    : {stats['tracked_symbols']}\n"

            f"Primary Provider   : {stats['primary_provider']}\n"

            f"Fallback Provider  : {stats['fallback_provider']}\n"

            f"Running            : {stats['running']}"

        )


# ==========================================================
# GLOBAL SINGLETON
# ==========================================================

data_feed_manager = DataFeedManager()


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [

    "ProviderType",

    "ProviderStatus",

    "ProviderInfo",

    "DataFeedManager",

    "data_feed_manager",

]