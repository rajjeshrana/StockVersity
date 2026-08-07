"""
=========================================================
StockVersity Scanner Pro
Scanner Market Bridge
Version : 2.0
=========================================================

Purpose
-------

Connect the StockVersity market-data layer with the
scanner architecture.

Flow
----

Market Provider / Upstox Feed
        ↓
Market Data Parser
        ↓
ScannerMarketBridge
        ↓
ScannerDataAdapter
        ↓
Scanner Engine
        ↓
Signals

=========================================================
"""

from __future__ import annotations

from datetime import datetime

from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Mapping
from typing import Optional

from core.scanner.signal import Signal
from core.scanner.scanner_engine import ScannerEngine
from core.scanner.scanner_data_adapter import ScannerDataAdapter
from core.scanner.scanner_data_adapter import get_scanner_data_adapter


# =========================================================
# SCANNER MARKET BRIDGE
# =========================================================

class ScannerMarketBridge:
    """
    Bridge between live market data and ScannerEngine.

    Responsibilities
    ----------------
    • Receive raw market data
    • Normalize scanner data
    • Maintain latest market snapshot
    • Apply scanner universe filters
    • Run ScannerEngine
    • Maintain latest signals
    • Notify signal listeners
    • Provide bridge diagnostics
    """

    def __init__(
        self,
        engine: ScannerEngine,
        *,
        adapter: Optional[ScannerDataAdapter] = None,
    ) -> None:

        if not isinstance(engine, ScannerEngine):
            raise TypeError(
                "engine must be a ScannerEngine instance."
            )

        self.engine = engine

        self.adapter = (
            adapter
            if adapter is not None
            else get_scanner_data_adapter()
        )

        # =================================================
        # RAW / NORMALIZED DATA
        # =================================================

        self.raw_market_data: Any = {}

        self.market_data: Dict[
            str,
            Dict[str, Any]
        ] = {}

        # =================================================
        # SIGNAL STATE
        # =================================================

        self.signals: List[Signal] = []

        self.previous_signals: List[Signal] = []

        # =================================================
        # FILTER SETTINGS
        # =================================================

        self.minimum_price: float = 200.0

        self.minimum_market_cap: float = 1000.0

        self.maximum_gap: float = 3.0

        # =================================================
        # EXECUTION SETTINGS
        # =================================================

        self.enabled: bool = True

        self.auto_scan: bool = True

        self.debug: bool = False

        # =================================================
        # TIMING
        # =================================================

        self.last_update: Optional[
            datetime
        ] = None

        self.last_scan: Optional[
            datetime
        ] = None

        self.last_scan_duration: float = 0.0

        # =================================================
        # COUNTERS
        # =================================================

        self.update_count: int = 0

        self.scan_count: int = 0

        self.error_count: int = 0

        # =================================================
        # ERROR STATE
        # =================================================

        self.last_error: Optional[str] = None

        # =================================================
        # CALLBACKS
        # =================================================

        self._signal_callbacks: List[
            Callable[[List[Signal]], None]
        ] = []

        self._market_callbacks: List[
            Callable[
                [Dict[str, Dict[str, Any]]],
                None,
            ]
        ] = []

    # =====================================================
    # CONFIGURE
    # =====================================================

    def configure(
        self,
        *,
        minimum_price: Optional[float] = None,
        minimum_market_cap: Optional[float] = None,
        maximum_gap: Optional[float] = None,
        auto_scan: Optional[bool] = None,
        enabled: Optional[bool] = None,
        debug: Optional[bool] = None,
    ) -> "ScannerMarketBridge":
        """
        Update bridge configuration.
        """

        if minimum_price is not None:

            self.minimum_price = max(
                0.0,
                float(minimum_price),
            )

        if minimum_market_cap is not None:

            self.minimum_market_cap = max(
                0.0,
                float(minimum_market_cap),
            )

        if maximum_gap is not None:

            self.maximum_gap = max(
                0.0,
                float(maximum_gap),
            )

        if auto_scan is not None:
            self.auto_scan = bool(auto_scan)

        if enabled is not None:
            self.enabled = bool(enabled)

        if debug is not None:
            self.debug = bool(debug)

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
            "[ScannerMarketBridge]",
            *message,
        )

    # =====================================================
    # RECEIVE MARKET DATA
    # =====================================================

    def update(
        self,
        raw_market_data: Any,
        *,
        run_scan: Optional[bool] = None,
    ) -> List[Signal]:
        """
        Receive a new market-data snapshot.

        If auto_scan is enabled, the scanner engine is
        automatically executed.
        """

        if not self.enabled:

            self.log(
                "Bridge disabled. Update ignored."
            )

            return self.signals

        self.raw_market_data = raw_market_data

        self.last_update = datetime.now()

        self.update_count += 1

        try:

            self.market_data = (
                self.adapter.prepare(
                    raw_market_data,
                    minimum_price=self.minimum_price,
                    minimum_market_cap=(
                        self.minimum_market_cap
                    ),
                    maximum_gap=self.maximum_gap,
                )
            )

            self._notify_market_callbacks()

            should_scan = (
                self.auto_scan
                if run_scan is None
                else bool(run_scan)
            )

            if should_scan:

                return self.scan()

            return self.signals

        except Exception as exc:

            self._handle_error(
                "Market update failed",
                exc,
            )

            return self.signals

    # =====================================================
    # UPDATE SINGLE INSTRUMENT
    # =====================================================

    def update_instrument(
        self,
        instrument_key: str,
        data: Mapping[str, Any],
        *,
        run_scan: Optional[bool] = None,
    ) -> List[Signal]:
        """
        Update one instrument.

        Useful for websocket/live feed updates.
        """

        if not instrument_key:

            raise ValueError(
                "instrument_key cannot be empty."
            )

        if not isinstance(data, Mapping):

            raise TypeError(
                "data must be a mapping/dictionary."
            )

        if not isinstance(
            self.raw_market_data,
            dict,
        ):

            self.raw_market_data = {}

        record = dict(data)

        record.setdefault(
            "instrument_key",
            instrument_key,
        )

        self.raw_market_data[
            instrument_key
        ] = record

        return self.update(
            self.raw_market_data,
            run_scan=run_scan,
        )

    # =====================================================
    # UPDATE MANY INSTRUMENTS
    # =====================================================

    def update_many(
        self,
        updates: Mapping[
            str,
            Mapping[str, Any]
        ],
        *,
        run_scan: Optional[bool] = None,
    ) -> List[Signal]:
        """
        Update multiple instruments in one operation.
        """

        if not isinstance(
            self.raw_market_data,
            dict,
        ):

            self.raw_market_data = {}

        for instrument_key, data in updates.items():

            if not isinstance(
                data,
                Mapping,
            ):
                continue

            record = dict(data)

            record.setdefault(
                "instrument_key",
                instrument_key,
            )

            self.raw_market_data[
                instrument_key
            ] = record

        return self.update(
            self.raw_market_data,
            run_scan=run_scan,
        )

    # =====================================================
    # RUN SCANNER ENGINE
    # =====================================================

    def scan(
        self,
    ) -> List[Signal]:
        """
        Run ScannerEngine using the current normalized
        market snapshot.
        """

        if not self.enabled:

            return self.signals

        if not self.market_data:

            self.log(
                "No normalized market data available."
            )

            return []

        started = datetime.now()

        try:

            self.previous_signals = list(
                self.signals
            )

            self.signals = self.engine.run(
                self.market_data
            )

            self.last_scan = datetime.now()

            self.last_scan_duration = (
                self.last_scan
                - started
            ).total_seconds()

            self.scan_count += 1

            self.last_error = None

            self._notify_signal_callbacks()

            self.log(
                "Scan complete:",
                len(self.signals),
                "signals",
                f"{self.last_scan_duration:.3f}s",
            )

            return self.signals

        except Exception as exc:

            self._handle_error(
                "Scanner execution failed",
                exc,
            )

            return []

    # =====================================================
    # FORCE SCAN
    # =====================================================

    def force_scan(
        self,
    ) -> List[Signal]:
        """
        Run scanner regardless of auto_scan setting.
        """

        return self.scan()

    # =====================================================
    # SIGNAL CALLBACK
    # =====================================================

    def add_signal_listener(
        self,
        callback: Callable[
            [List[Signal]],
            None,
        ],
    ) -> None:
        """
        Register signal callback.

        callback(signals)
        """

        if callback not in self._signal_callbacks:

            self._signal_callbacks.append(
                callback
            )

    # =====================================================
    # REMOVE SIGNAL CALLBACK
    # =====================================================

    def remove_signal_listener(
        self,
        callback: Callable[
            [List[Signal]],
            None,
        ],
    ) -> None:

        if callback in self._signal_callbacks:

            self._signal_callbacks.remove(
                callback
            )

    # =====================================================
    # MARKET CALLBACK
    # =====================================================

    def add_market_listener(
        self,
        callback: Callable[
            [Dict[str, Dict[str, Any]]],
            None,
        ],
    ) -> None:

        if callback not in self._market_callbacks:

            self._market_callbacks.append(
                callback
            )

    # =====================================================
    # REMOVE MARKET CALLBACK
    # =====================================================

    def remove_market_listener(
        self,
        callback: Callable[
            [Dict[str, Dict[str, Any]]],
            None,
        ],
    ) -> None:

        if callback in self._market_callbacks:

            self._market_callbacks.remove(
                callback
            )

    # =====================================================
    # NOTIFY SIGNAL CALLBACKS
    # =====================================================

    def _notify_signal_callbacks(
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
                    "Signal callback failed",
                    exc,
                )

    # =====================================================
    # NOTIFY MARKET CALLBACKS
    # =====================================================

    def _notify_market_callbacks(
        self,
    ) -> None:

        for callback in list(
            self._market_callbacks
        ):

            try:

                callback(
                    dict(self.market_data)
                )

            except Exception as exc:

                self._handle_error(
                    "Market callback failed",
                    exc,
                )

    # =====================================================
    # NEW SIGNALS
    # =====================================================

    def new_signals(
        self,
    ) -> List[Signal]:
        """
        Return signals that did not exist in the previous
        scanner cycle.

        Comparison uses:
        symbol + signal type + pattern.
        """

        previous = {

            (
                signal.symbol,
                signal.signal_type.value,
                signal.pattern.value,
            )

            for signal in self.previous_signals

        }

        return [

            signal

            for signal in self.signals

            if (
                signal.symbol,
                signal.signal_type.value,
                signal.pattern.value,
            )
            not in previous

        ]

    # =====================================================
    # REMOVED SIGNALS
    # =====================================================

    def removed_signals(
        self,
    ) -> List[Signal]:
        """
        Signals present in previous scan but not current.
        """

        current = {

            (
                signal.symbol,
                signal.signal_type.value,
                signal.pattern.value,
            )

            for signal in self.signals

        }

        return [

            signal

            for signal in self.previous_signals

            if (
                signal.symbol,
                signal.signal_type.value,
                signal.pattern.value,
            )
            not in current

        ]

    # =====================================================
    # GET SIGNAL
    # =====================================================

    def get_signal(
        self,
        symbol: str,
    ) -> Optional[Signal]:

        symbol = symbol.upper().strip()

        for signal in self.signals:

            if (
                signal.symbol.upper()
                == symbol
            ):

                return signal

        return None

    # =====================================================
    # GET MARKET RECORD
    # =====================================================

    def get_market_record(
        self,
        instrument_key: str,
    ) -> Optional[Dict[str, Any]]:

        record = self.market_data.get(
            instrument_key
        )

        if record is None:
            return None

        return dict(record)

    # =====================================================
    # FIND MARKET RECORD BY SYMBOL
    # =====================================================

    def find_market_record(
        self,
        symbol: str,
    ) -> Optional[Dict[str, Any]]:

        symbol = symbol.upper().strip()

        for record in self.market_data.values():

            if (
                str(
                    record.get(
                        "symbol",
                        "",
                    )
                ).upper()
                == symbol
            ):

                return dict(record)

        return None

    # =====================================================
    # TOP SIGNALS
    # =====================================================

    def top_signals(
        self,
        count: int = 10,
    ) -> List[Signal]:

        return sorted(

            self.signals,

            key=lambda signal: (
                signal.score,
                signal.confidence,
                signal.risk_reward,
            ),

            reverse=True,

        )[:max(0, count)]

    # =====================================================
    # BUY SIGNALS
    # =====================================================

    def buy_signals(
        self,
    ) -> List[Signal]:

        return [

            signal

            for signal in self.signals

            if signal.is_buy

        ]

    # =====================================================
    # SELL SIGNALS
    # =====================================================

    def sell_signals(
        self,
    ) -> List[Signal]:

        return [

            signal

            for signal in self.signals

            if signal.is_sell

        ]

    # =====================================================
    # ALERT SIGNALS
    # =====================================================

    def alert_signals(
        self,
        *,
        minimum_score: float = 85.0,
        minimum_confidence: float = 80.0,
    ) -> List[Signal]:

        signals = [

            signal

            for signal in self.signals

            if (
                signal.score
                >= minimum_score
                and
                signal.confidence
                >= minimum_confidence
            )

        ]

        return sorted(

            signals,

            key=lambda signal: (
                signal.score,
                signal.confidence,
            ),

            reverse=True,

        )

    # =====================================================
    # MARKET COUNT
    # =====================================================

    @property
    def market_count(
        self,
    ) -> int:

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
    # HAS MARKET DATA
    # =====================================================

    @property
    def has_market_data(
        self,
    ) -> bool:

        return bool(
            self.market_data
        )

    # =====================================================
    # HAS SIGNALS
    # =====================================================

    @property
    def has_signals(
        self,
    ) -> bool:

        return bool(
            self.signals
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

    # =====================================================
    # STATUS
    # =====================================================

    def status(
        self,
    ) -> Dict[str, Any]:

        return {

            "enabled":
                self.enabled,

            "auto_scan":
                self.auto_scan,

            "market_records":
                len(
                    self.market_data
                ),

            "signals":
                len(
                    self.signals
                ),

            "updates":
                self.update_count,

            "scans":
                self.scan_count,

            "errors":
                self.error_count,

            "last_error":
                self.last_error,

            "last_update": (
                self.last_update.isoformat()
                if self.last_update
                else None
            ),

            "last_scan": (
                self.last_scan.isoformat()
                if self.last_scan
                else None
            ),

            "last_scan_duration":
                round(
                    self.last_scan_duration,
                    4,
                ),

            "minimum_price":
                self.minimum_price,

            "minimum_market_cap":
                self.minimum_market_cap,

            "maximum_gap":
                self.maximum_gap,

        }

    # =====================================================
    # SNAPSHOT
    # =====================================================

    def snapshot(
        self,
    ) -> Dict[str, Any]:
        """
        Complete bridge snapshot for dashboard/debugging.
        """

        return {

            "generated_at":
                datetime.now().isoformat(),

            "status":
                self.status(),

            "adapter":
                self.adapter.status(),

            "engine":
                self.engine.status(),

            "signals": [

                signal.to_dict()

                for signal in self.signals

            ],

        }

    # =====================================================
    # ENABLE
    # =====================================================

    def enable(
        self,
    ) -> None:

        self.enabled = True

    # =====================================================
    # DISABLE
    # =====================================================

    def disable(
        self,
    ) -> None:

        self.enabled = False

    # =====================================================
    # CLEAR SIGNALS
    # =====================================================

    def clear_signals(
        self,
    ) -> None:

        self.previous_signals.clear()

        self.signals.clear()

        self.engine.clear_results()

    # =====================================================
    # CLEAR MARKET DATA
    # =====================================================

    def clear_market_data(
        self,
    ) -> None:

        self.raw_market_data = {}

        self.market_data.clear()

    # =====================================================
    # RESET
    # =====================================================

    def reset(
        self,
    ) -> None:

        self.clear_signals()

        self.clear_market_data()

        self.last_update = None

        self.last_scan = None

        self.last_scan_duration = 0.0

        self.update_count = 0

        self.scan_count = 0

        self.error_count = 0

        self.last_error = None

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"market_records="
            f"{len(self.market_data)}, "

            f"signals="
            f"{len(self.signals)}, "

            f"enabled="
            f"{self.enabled}, "

            f"auto_scan="
            f"{self.auto_scan}"

            f")"

        )

    def __str__(
        self,
    ) -> str:

        return (

            "ScannerMarketBridge | "

            f"{len(self.market_data)} stocks | "

            f"{len(self.signals)} signals | "

            f"{self.scan_count} scans"

        )


# =========================================================
# FACTORY
# =========================================================

def create_scanner_market_bridge(
    engine: ScannerEngine,
    *,
    adapter: Optional[
        ScannerDataAdapter
    ] = None,
    minimum_price: float = 200.0,
    minimum_market_cap: float = 1000.0,
    maximum_gap: float = 3.0,
    auto_scan: bool = True,
    debug: bool = False,
) -> ScannerMarketBridge:
    """
    Create configured ScannerMarketBridge.
    """

    bridge = ScannerMarketBridge(
        engine=engine,
        adapter=adapter,
    )

    bridge.configure(

        minimum_price=minimum_price,

        minimum_market_cap=(
            minimum_market_cap
        ),

        maximum_gap=maximum_gap,

        auto_scan=auto_scan,

        debug=debug,

    )

    return bridge


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "ScannerMarketBridge",

    "create_scanner_market_bridge",

]


# ==========================
# END OF FILE
# ==========================