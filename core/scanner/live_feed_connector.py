"""
=========================================================
StockVersity Scanner Pro
Live Feed Connector
Version : 2.0
=========================================================

Purpose
-------

Connect parsed live market-feed updates with the
ScannerMarketBridge.

Flow
----

Upstox WebSocket
        ↓
MarketDataParser
        ↓
LiveFeedConnector
        ↓
ScannerMarketBridge
        ↓
ScannerDataAdapter
        ↓
ScannerEngine
        ↓
Signals

=========================================================
"""

from __future__ import annotations

from datetime import datetime
from threading import Lock
from time import monotonic

from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Mapping
from typing import Optional

from core.scanner.signal import Signal
from core.scanner.scanner_market_bridge import ScannerMarketBridge


# =========================================================
# LIVE FEED CONNECTOR
# =========================================================

class LiveFeedConnector:
    """
    Receives parsed live market-data updates and forwards
    them to ScannerMarketBridge.

    Responsibilities
    ----------------
    • Receive tick updates
    • Maintain latest instrument snapshots
    • Batch updates
    • Control scanner frequency
    • Forward data to ScannerMarketBridge
    • Track feed health
    • Track update statistics
    • Notify listeners
    """

    def __init__(
        self,
        bridge: ScannerMarketBridge,
        *,
        scan_interval: float = 2.0,
        auto_scan: bool = True,
    ) -> None:

        if not isinstance(
            bridge,
            ScannerMarketBridge,
        ):
            raise TypeError(
                "bridge must be a ScannerMarketBridge instance."
            )

        self.bridge = bridge

        # =================================================
        # SETTINGS
        # =================================================

        self.scan_interval = max(
            0.1,
            float(scan_interval),
        )

        self.auto_scan = bool(
            auto_scan
        )

        self.enabled = True

        self.debug = False

        # =================================================
        # MARKET SNAPSHOT
        # =================================================

        self.market_data: Dict[
            str,
            Dict[str, Any]
        ] = {}

        self.pending_updates: Dict[
            str,
            Dict[str, Any]
        ] = {}

        # =================================================
        # SIGNAL STATE
        # =================================================

        self.signals: List[Signal] = []

        # =================================================
        # TIMING
        # =================================================

        self.started_at: Optional[
            datetime
        ] = None

        self.last_tick_at: Optional[
            datetime
        ] = None

        self.last_flush_at: Optional[
            datetime
        ] = None

        self.last_scan_at: Optional[
            datetime
        ] = None

        self._last_scan_clock = 0.0

        # =================================================
        # COUNTERS
        # =================================================

        self.tick_count = 0

        self.update_count = 0

        self.flush_count = 0

        self.scan_count = 0

        self.error_count = 0

        # =================================================
        # STATE
        # =================================================

        self.running = False

        self.last_error: Optional[
            str
        ] = None

        # =================================================
        # THREAD SAFETY
        # =================================================

        self._lock = Lock()

        # =================================================
        # CALLBACKS
        # =================================================

        self._signal_callbacks: List[
            Callable[[List[Signal]], None]
        ] = []

        self._tick_callbacks: List[
            Callable[
                [str, Dict[str, Any]],
                None,
            ]
        ] = []

        self._error_callbacks: List[
            Callable[[str], None]
        ] = []

    # =====================================================
    # CONFIGURE
    # =====================================================

    def configure(
        self,
        *,
        scan_interval: Optional[
            float
        ] = None,
        auto_scan: Optional[
            bool
        ] = None,
        enabled: Optional[
            bool
        ] = None,
        debug: Optional[
            bool
        ] = None,
    ) -> "LiveFeedConnector":

        if scan_interval is not None:

            self.scan_interval = max(
                0.1,
                float(scan_interval),
            )

        if auto_scan is not None:

            self.auto_scan = bool(
                auto_scan
            )

        if enabled is not None:

            self.enabled = bool(
                enabled
            )

        if debug is not None:

            self.debug = bool(
                debug
            )

        return self

    # =====================================================
    # LOG
    # =====================================================

    def log(
        self,
        *message: Any,
    ) -> None:

        if not self.debug:
            return

        print(
            "[LiveFeedConnector]",
            *message,
        )

    # =====================================================
    # START
    # =====================================================

    def start(
        self,
    ) -> None:
        """
        Start accepting live feed updates.
        """

        if self.running:
            return

        self.running = True

        self.started_at = datetime.now()

        self._last_scan_clock = (
            monotonic()
        )

        self.log(
            "Live feed connector started."
        )

    # =====================================================
    # STOP
    # =====================================================

    def stop(
        self,
        *,
        flush: bool = True,
    ) -> None:
        """
        Stop accepting live feed updates.

        Pending data may optionally be flushed first.
        """

        if flush:

            try:

                self.flush(
                    force_scan=False
                )

            except Exception as exc:

                self._handle_error(
                    "Final flush failed",
                    exc,
                )

        self.running = False

        self.log(
            "Live feed connector stopped."
        )

    # =====================================================
    # RECEIVE TICK
    # =====================================================

    def on_tick(
        self,
        instrument_key: str,
        data: Mapping[str, Any],
    ) -> List[Signal]:
        """
        Receive one parsed market-data update.

        This method is intended to be called by the
        MarketDataParser or websocket callback.
        """

        if not self.enabled:
            return self.signals

        if not self.running:

            self.start()

        if not instrument_key:

            return self.signals

        if not isinstance(
            data,
            Mapping,
        ):

            return self.signals

        try:

            record = dict(data)

            record.setdefault(
                "instrument_key",
                instrument_key,
            )

            record.setdefault(
                "updated_at",
                datetime.now().isoformat(),
            )

            with self._lock:

                existing = (
                    self.market_data.get(
                        instrument_key,
                        {},
                    )
                )

                merged = {
                    **existing,
                    **record,
                }

                self.market_data[
                    instrument_key
                ] = merged

                self.pending_updates[
                    instrument_key
                ] = merged

                self.tick_count += 1

                self.update_count += 1

                self.last_tick_at = (
                    datetime.now()
                )

            self._notify_tick(
                instrument_key,
                record,
            )

            if self.auto_scan:

                if self.scan_due:

                    return self.flush(
                        force_scan=True
                    )

            return self.signals

        except Exception as exc:

            self._handle_error(
                "Tick processing failed",
                exc,
            )

            return self.signals

    # =====================================================
    # RECEIVE MANY
    # =====================================================

    def on_ticks(
        self,
        updates: Mapping[
            str,
            Mapping[str, Any]
        ],
    ) -> List[Signal]:
        """
        Receive multiple parsed instrument updates.
        """

        if not updates:
            return self.signals

        for instrument_key, data in (
            updates.items()
        ):

            self.on_tick(
                instrument_key,
                data,
            )

        return self.signals

    # =====================================================
    # GENERIC UPDATE
    # =====================================================

    def update(
        self,
        instrument_key: str,
        data: Mapping[str, Any],
    ) -> List[Signal]:
        """
        Alias for on_tick().
        """

        return self.on_tick(
            instrument_key,
            data,
        )

    # =====================================================
    # FLUSH
    # =====================================================

    def flush(
        self,
        *,
        force_scan: bool = True,
    ) -> List[Signal]:
        """
        Push pending updates into ScannerMarketBridge.

        Pending updates are copied and cleared before
        processing so new websocket ticks can continue
        arriving safely.
        """

        if not self.enabled:

            return self.signals

        with self._lock:

            if not self.pending_updates:

                if force_scan:

                    return self._run_bridge_scan()

                return self.signals

            updates = dict(
                self.pending_updates
            )

            self.pending_updates.clear()

        try:

            self.flush_count += 1

            self.last_flush_at = (
                datetime.now()
            )

            self.signals = (
                self.bridge.update_many(
                    updates,
                    run_scan=force_scan,
                )
            )

            if force_scan:

                self.scan_count += 1

                self.last_scan_at = (
                    datetime.now()
                )

                self._last_scan_clock = (
                    monotonic()
                )

                self._notify_signals()

            return self.signals

        except Exception as exc:

            self._handle_error(
                "Feed flush failed",
                exc,
            )

            return self.signals

    # =====================================================
    # FORCE SCAN
    # =====================================================

    def force_scan(
        self,
    ) -> List[Signal]:
        """
        Immediately run scanner using latest snapshot.
        """

        if self.pending_updates:

            return self.flush(
                force_scan=True
            )

        return self._run_bridge_scan()

    # =====================================================
    # BRIDGE SCAN
    # =====================================================

    def _run_bridge_scan(
        self,
    ) -> List[Signal]:

        try:

            self.signals = (
                self.bridge.force_scan()
            )

            self.scan_count += 1

            self.last_scan_at = (
                datetime.now()
            )

            self._last_scan_clock = (
                monotonic()
            )

            self._notify_signals()

            return self.signals

        except Exception as exc:

            self._handle_error(
                "Bridge scan failed",
                exc,
            )

            return self.signals

    # =====================================================
    # SCAN DUE
    # =====================================================

    @property
    def scan_due(
        self,
    ) -> bool:

        if self._last_scan_clock <= 0:

            return True

        elapsed = (

            monotonic()

            - self._last_scan_clock

        )

        return (
            elapsed
            >= self.scan_interval
        )

    # =====================================================
    # SIGNAL LISTENER
    # =====================================================

    def add_signal_listener(
        self,
        callback: Callable[
            [List[Signal]],
            None,
        ],
    ) -> None:

        if callback not in (
            self._signal_callbacks
        ):

            self._signal_callbacks.append(
                callback
            )

    # =====================================================
    # REMOVE SIGNAL LISTENER
    # =====================================================

    def remove_signal_listener(
        self,
        callback: Callable[
            [List[Signal]],
            None,
        ],
    ) -> None:

        if callback in (
            self._signal_callbacks
        ):

            self._signal_callbacks.remove(
                callback
            )

    # =====================================================
    # TICK LISTENER
    # =====================================================

    def add_tick_listener(
        self,
        callback: Callable[
            [str, Dict[str, Any]],
            None,
        ],
    ) -> None:

        if callback not in (
            self._tick_callbacks
        ):

            self._tick_callbacks.append(
                callback
            )

    # =====================================================
    # REMOVE TICK LISTENER
    # =====================================================

    def remove_tick_listener(
        self,
        callback: Callable[
            [str, Dict[str, Any]],
            None,
        ],
    ) -> None:

        if callback in (
            self._tick_callbacks
        ):

            self._tick_callbacks.remove(
                callback
            )

    # =====================================================
    # ERROR LISTENER
    # =====================================================

    def add_error_listener(
        self,
        callback: Callable[
            [str],
            None,
        ],
    ) -> None:

        if callback not in (
            self._error_callbacks
        ):

            self._error_callbacks.append(
                callback
            )

    # =====================================================
    # NOTIFY SIGNALS
    # =====================================================

    def _notify_signals(
        self,
    ) -> None:

        for callback in list(
            self._signal_callbacks
        ):

            try:

                callback(
                    list(self.signals)
                )

            except Exception as exc:

                self._handle_error(
                    "Signal listener failed",
                    exc,
                )

    # =====================================================
    # NOTIFY TICK
    # =====================================================

    def _notify_tick(
        self,
        instrument_key: str,
        data: Dict[str, Any],
    ) -> None:

        for callback in list(
            self._tick_callbacks
        ):

            try:

                callback(
                    instrument_key,
                    dict(data),
                )

            except Exception as exc:

                self._handle_error(
                    "Tick listener failed",
                    exc,
                )

    # =====================================================
    # ERROR HANDLER
    # =====================================================

    def _handle_error(
        self,
        prefix: str,
        exc: Exception,
    ) -> None:

        self.error_count += 1

        self.last_error = (

            f"{prefix}: "
            f"{type(exc).__name__}: "
            f"{exc}"

        )

        self.log(
            self.last_error
        )

        for callback in list(
            self._error_callbacks
        ):

            try:

                callback(
                    self.last_error
                )

            except Exception:

                pass

    # =====================================================
    # GET MARKET DATA
    # =====================================================

    def get(
        self,
        instrument_key: str,
    ) -> Optional[
        Dict[str, Any]
    ]:

        with self._lock:

            data = self.market_data.get(
                instrument_key
            )

            if data is None:
                return None

            return dict(data)

    # =====================================================
    # FIND SYMBOL
    # =====================================================

    def find_symbol(
        self,
        symbol: str,
    ) -> Optional[
        Dict[str, Any]
    ]:

        symbol = symbol.upper().strip()

        with self._lock:

            for data in (
                self.market_data.values()
            ):

                current_symbol = str(
                    data.get(
                        "symbol",
                        "",
                    )
                ).upper()

                if (
                    current_symbol
                    == symbol
                ):

                    return dict(data)

        return None

    # =====================================================
    # MARKET SNAPSHOT
    # =====================================================

    def market_snapshot(
        self,
    ) -> Dict[
        str,
        Dict[str, Any]
    ]:

        with self._lock:

            return {

                key: dict(value)

                for key, value
                in self.market_data.items()

            }

    # =====================================================
    # SIGNAL SNAPSHOT
    # =====================================================

    def signal_snapshot(
        self,
    ) -> List[
        Dict[str, Any]
    ]:

        return [

            signal.to_dict()

            for signal in self.signals

        ]

    # =====================================================
    # PENDING COUNT
    # =====================================================

    @property
    def pending_count(
        self,
    ) -> int:

        with self._lock:

            return len(
                self.pending_updates
            )

    # =====================================================
    # INSTRUMENT COUNT
    # =====================================================

    @property
    def instrument_count(
        self,
    ) -> int:

        with self._lock:

            return len(
                self.market_data
            )

    # =====================================================
    # SIGNAL COUNT
    # =====================================================

    @property
    def signal_count(
        self,
    ) -> int:

        return len(
            self.signals
        )

    # =====================================================
    # FEED HEALTH
    # =====================================================

    def feed_health(
        self,
        stale_after_seconds: float = 10.0,
    ) -> Dict[str, Any]:
        """
        Determine whether live feed is receiving updates.
        """

        if self.last_tick_at is None:

            age = None

            healthy = False

        else:

            age = (

                datetime.now()

                - self.last_tick_at

            ).total_seconds()

            healthy = (
                age
                <= stale_after_seconds
            )

        return {

            "healthy":
                healthy,

            "running":
                self.running,

            "enabled":
                self.enabled,

            "last_tick_age":
                round(age, 2)
                if age is not None
                else None,

            "stale_after":
                stale_after_seconds,

            "instruments":
                self.instrument_count,

            "pending":
                self.pending_count,

            "ticks":
                self.tick_count,

            "errors":
                self.error_count,

        }

    # =====================================================
    # STATUS
    # =====================================================

    def status(
        self,
    ) -> Dict[str, Any]:

        return {

            "running":
                self.running,

            "enabled":
                self.enabled,

            "auto_scan":
                self.auto_scan,

            "scan_interval":
                self.scan_interval,

            "instruments":
                self.instrument_count,

            "pending_updates":
                self.pending_count,

            "signals":
                self.signal_count,

            "ticks":
                self.tick_count,

            "updates":
                self.update_count,

            "flushes":
                self.flush_count,

            "scans":
                self.scan_count,

            "errors":
                self.error_count,

            "last_error":
                self.last_error,

            "started_at": (
                self.started_at.isoformat()
                if self.started_at
                else None
            ),

            "last_tick_at": (
                self.last_tick_at.isoformat()
                if self.last_tick_at
                else None
            ),

            "last_flush_at": (
                self.last_flush_at.isoformat()
                if self.last_flush_at
                else None
            ),

            "last_scan_at": (
                self.last_scan_at.isoformat()
                if self.last_scan_at
                else None
            ),

        }

    # =====================================================
    # RESET
    # =====================================================

    def reset(
        self,
    ) -> None:

        with self._lock:

            self.market_data.clear()

            self.pending_updates.clear()

        self.signals.clear()

        self.tick_count = 0

        self.update_count = 0

        self.flush_count = 0

        self.scan_count = 0

        self.error_count = 0

        self.last_error = None

        self.last_tick_at = None

        self.last_flush_at = None

        self.last_scan_at = None

        self._last_scan_clock = 0.0

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(
        self,
    ) -> None:

        self.reset()

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"running="
            f"{self.running}, "

            f"instruments="
            f"{self.instrument_count}, "

            f"signals="
            f"{self.signal_count}, "

            f"scan_interval="
            f"{self.scan_interval}"

            f")"

        )

    def __str__(
        self,
    ) -> str:

        return (

            "LiveFeedConnector | "

            f"{self.instrument_count} instruments | "

            f"{self.tick_count} ticks | "

            f"{self.signal_count} signals"

        )


# =========================================================
# FACTORY
# =========================================================

def create_live_feed_connector(
    bridge: ScannerMarketBridge,
    *,
    scan_interval: float = 2.0,
    auto_scan: bool = True,
    debug: bool = False,
) -> LiveFeedConnector:
    """
    Create configured LiveFeedConnector.
    """

    connector = LiveFeedConnector(

        bridge=bridge,

        scan_interval=scan_interval,

        auto_scan=auto_scan,

    )

    connector.configure(
        debug=debug
    )

    return connector


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "LiveFeedConnector",

    "create_live_feed_connector",

]


# ==========================
# END OF FILE
# ==========================