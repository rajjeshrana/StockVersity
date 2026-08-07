"""
=========================================================
StockVersity Scanner Pro
Scanner Scheduler
Version : 2.0
=========================================================

Controls scanner execution timing.

Flow
----

Upstox Live Feed
        ↓
MarketDataBridge
        ↓
ScannerScheduler
        ↓
ScannerManager
        ↓
ScannerEngine
        ↓
Signals / Dashboard / Alerts

=========================================================
"""

from __future__ import annotations

from datetime import datetime
from datetime import time
from datetime import timedelta

from threading import Event
from threading import Lock
from threading import Thread

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import time as time_module

from core.scanner.signal import Signal
from core.scanner.scanner_manager import ScannerManager
from core.scanner.market_data_bridge import MarketDataBridge


# =========================================================
# MARKET TIMES
# =========================================================

MARKET_OPEN = time(
    hour=9,
    minute=15,
)

MARKET_CLOSE = time(
    hour=15,
    minute=30,
)


# =========================================================
# DEFAULT INTERVALS
# =========================================================

DEFAULT_INTRADAY_INTERVAL = 60

DEFAULT_SWING_INTERVAL = 900

DEFAULT_POSITIONAL_INTERVAL = 3600

DEFAULT_LOOP_INTERVAL = 1.0


# =========================================================
# SCANNER SCHEDULER
# =========================================================

class ScannerScheduler:
    """
    Controls scanner execution frequency.

    The scheduler prevents the complete scanner engine
    from running on every market-data tick.

    Typical usage
    -------------

    Intraday:
        Run frequently during market hours.

    Swing:
        Run less frequently.

    Positional:
        Run on larger intervals / completed higher
        timeframe candles.
    """

    def __init__(
        self,
        manager: ScannerManager,
        bridge: MarketDataBridge,
        *,
        intraday_interval: int = DEFAULT_INTRADAY_INTERVAL,
        swing_interval: int = DEFAULT_SWING_INTERVAL,
        positional_interval: int = DEFAULT_POSITIONAL_INTERVAL,
        loop_interval: float = DEFAULT_LOOP_INTERVAL,
        market_hours_only: bool = True,
        debug: bool = False,
    ) -> None:

        self.manager = manager

        self.bridge = bridge

        self.intraday_interval = max(
            1,
            int(intraday_interval),
        )

        self.swing_interval = max(
            1,
            int(swing_interval),
        )

        self.positional_interval = max(
            1,
            int(positional_interval),
        )

        self.loop_interval = max(
            0.25,
            float(loop_interval),
        )

        self.market_hours_only = (
            market_hours_only
        )

        self.debug = debug

        self.running = False

        self.paused = False

        self._thread: Optional[
            Thread
        ] = None

        self._stop_event = Event()

        self._lock = Lock()

        self.last_intraday_scan: Optional[
            datetime
        ] = None

        self.last_swing_scan: Optional[
            datetime
        ] = None

        self.last_positional_scan: Optional[
            datetime
        ] = None

        self.last_scan: Optional[
            datetime
        ] = None

        self.last_error: Optional[
            str
        ] = None

        self.total_scans = 0

        self.intraday_scans = 0

        self.swing_scans = 0

        self.positional_scans = 0

        self.latest_signals: List[
            Signal
        ] = []

    # =====================================================
    # MARKET OPEN CHECK
    # =====================================================

    def is_market_open(
        self,
        now: Optional[datetime] = None,
    ) -> bool:
        """
        Return True during NSE normal market hours.

        Monday-Friday
        09:15 - 15:30
        """

        if now is None:

            now = datetime.now()

        # Monday = 0
        # Sunday = 6

        if now.weekday() >= 5:

            return False

        current_time = now.time()

        return (
            MARKET_OPEN
            <= current_time
            <= MARKET_CLOSE
        )

    # =====================================================
    # MARKET STATUS
    # =====================================================

    def market_status(
        self,
    ) -> str:

        if self.is_market_open():

            return "OPEN"

        return "CLOSED"

    # =====================================================
    # ELAPSED CHECK
    # =====================================================

    @staticmethod
    def _interval_elapsed(
        last_run: Optional[datetime],
        interval_seconds: int,
        now: datetime,
    ) -> bool:

        if last_run is None:

            return True

        elapsed = (
            now - last_run
        ).total_seconds()

        return (
            elapsed
            >= interval_seconds
        )

    # =====================================================
    # SHOULD RUN INTRADAY
    # =====================================================

    def should_run_intraday(
        self,
        now: Optional[datetime] = None,
    ) -> bool:

        if now is None:

            now = datetime.now()

        if (
            self.market_hours_only
            and not self.is_market_open(now)
        ):

            return False

        return self._interval_elapsed(
            self.last_intraday_scan,
            self.intraday_interval,
            now,
        )

    # =====================================================
    # SHOULD RUN SWING
    # =====================================================

    def should_run_swing(
        self,
        now: Optional[datetime] = None,
    ) -> bool:

        if now is None:

            now = datetime.now()

        if (
            self.market_hours_only
            and not self.is_market_open(now)
        ):

            return False

        return self._interval_elapsed(
            self.last_swing_scan,
            self.swing_interval,
            now,
        )

    # =====================================================
    # SHOULD RUN POSITIONAL
    # =====================================================

    def should_run_positional(
        self,
        now: Optional[datetime] = None,
    ) -> bool:

        if now is None:

            now = datetime.now()

        if (
            self.market_hours_only
            and not self.is_market_open(now)
        ):

            return False

        return self._interval_elapsed(
            self.last_positional_scan,
            self.positional_interval,
            now,
        )

    # =====================================================
    # EXECUTE SCAN
    # =====================================================

    def _execute_scan(
        self,
        scan_type: str,
    ) -> List[Signal]:
        """
        Execute one scanner-engine cycle.

        scan_type is recorded for diagnostics.

        Later this can be upgraded so each scan type
        executes only its own scanner group.
        """

        if self.bridge.symbol_count == 0:

            self.log(
                scan_type,
                "scan skipped - no market data."
            )

            return []

        try:

            results = (
                self.bridge.run_scan()
            )

            now = datetime.now()

            with self._lock:

                self.latest_signals = list(
                    results
                )

                self.last_scan = now

                self.total_scans += 1

                if scan_type == "INTRADAY":

                    self.last_intraday_scan = now

                    self.intraday_scans += 1

                elif scan_type == "SWING":

                    self.last_swing_scan = now

                    self.swing_scans += 1

                elif scan_type == "POSITIONAL":

                    self.last_positional_scan = now

                    self.positional_scans += 1

                self.last_error = None

            self.log(
                scan_type,
                "scan completed:",
                len(results),
                "signals",
            )

            return results

        except Exception as exc:

            with self._lock:

                self.last_error = str(exc)

            self.log(
                scan_type,
                "scan failed:",
                exc,
            )

            return []

    # =====================================================
    # RUN INTRADAY
    # =====================================================

    def run_intraday(
        self,
    ) -> List[Signal]:

        return self._execute_scan(
            "INTRADAY"
        )

    # =====================================================
    # RUN SWING
    # =====================================================

    def run_swing(
        self,
    ) -> List[Signal]:

        return self._execute_scan(
            "SWING"
        )

    # =====================================================
    # RUN POSITIONAL
    # =====================================================

    def run_positional(
        self,
    ) -> List[Signal]:

        return self._execute_scan(
            "POSITIONAL"
        )

    # =====================================================
    # RUN ALL
    # =====================================================

    def run_all(
        self,
    ) -> List[Signal]:
        """
        Force one complete scan immediately.
        """

        return self._execute_scan(
            "MANUAL"
        )

    # =====================================================
    # SCHEDULER TICK
    # =====================================================

    def tick(
        self,
    ) -> None:
        """
        Execute one scheduler cycle.
        """

        if self.paused:

            return

        now = datetime.now()

        if (
            self.market_hours_only
            and not self.is_market_open(now)
        ):

            return

        # -------------------------------------------------
        # IMPORTANT
        #
        # Because the current ScannerEngine executes every
        # enabled scanner together, only one engine run is
        # performed per scheduler tick.
        #
        # This prevents the same scanners being executed
        # three times when intraday/swing/positional timers
        # become due together.
        #
        # Later scanner groups can be separated.
        # -------------------------------------------------

        intraday_due = (
            self.should_run_intraday(now)
        )

        swing_due = (
            self.should_run_swing(now)
        )

        positional_due = (
            self.should_run_positional(now)
        )

        if not any(
            (
                intraday_due,
                swing_due,
                positional_due,
            )
        ):

            return

        results = self._execute_scan(
            "SCHEDULED"
        )

        scan_time = datetime.now()

        with self._lock:

            if intraday_due:

                self.last_intraday_scan = (
                    scan_time
                )

                self.intraday_scans += 1

            if swing_due:

                self.last_swing_scan = (
                    scan_time
                )

                self.swing_scans += 1

            if positional_due:

                self.last_positional_scan = (
                    scan_time
                )

                self.positional_scans += 1

        self.log(
            "Scheduled scan:",
            len(results),
            "signals",
        )

    # =====================================================
    # WORKER LOOP
    # =====================================================

    def _worker(
        self,
    ) -> None:
        """
        Background scheduler loop.
        """

        self.log(
            "Scheduler worker started."
        )

        while not self._stop_event.is_set():

            try:

                self.tick()

            except Exception as exc:

                with self._lock:

                    self.last_error = str(exc)

                self.log(
                    "Scheduler error:",
                    exc,
                )

            self._stop_event.wait(
                self.loop_interval
            )

        self.log(
            "Scheduler worker stopped."
        )

    # =====================================================
    # START
    # =====================================================

    def start(
        self,
    ) -> None:
        """
        Start background scheduler.
        """

        if self.running:

            return

        self._stop_event.clear()

        self.running = True

        self.paused = False

        self._thread = Thread(
            target=self._worker,
            name="StockVersityScannerScheduler",
            daemon=True,
        )

        self._thread.start()

        self.log(
            "Scanner scheduler started."
        )

    # =====================================================
    # STOP
    # =====================================================

    def stop(
        self,
        timeout: float = 5.0,
    ) -> None:
        """
        Stop background scheduler.
        """

        if not self.running:

            return

        self._stop_event.set()

        thread = self._thread

        if (
            thread is not None
            and thread.is_alive()
        ):

            thread.join(
                timeout=timeout
            )

        self.running = False

        self.paused = False

        self._thread = None

        self.log(
            "Scanner scheduler stopped."
        )

    # =====================================================
    # PAUSE
    # =====================================================

    def pause(
        self,
    ) -> None:

        self.paused = True

        self.log(
            "Scanner scheduler paused."
        )

    # =====================================================
    # RESUME
    # =====================================================

    def resume(
        self,
    ) -> None:

        self.paused = False

        self.log(
            "Scanner scheduler resumed."
        )

    # =====================================================
    # RESET TIMERS
    # =====================================================

    def reset_timers(
        self,
    ) -> None:

        with self._lock:

            self.last_intraday_scan = None

            self.last_swing_scan = None

            self.last_positional_scan = None

            self.last_scan = None

    # =====================================================
    # NEXT INTRADAY SCAN
    # =====================================================

    def next_intraday_scan(
        self,
    ) -> Optional[datetime]:

        if self.last_intraday_scan is None:

            return datetime.now()

        return (
            self.last_intraday_scan
            + timedelta(
                seconds=self.intraday_interval
            )
        )

    # =====================================================
    # NEXT SWING SCAN
    # =====================================================

    def next_swing_scan(
        self,
    ) -> Optional[datetime]:

        if self.last_swing_scan is None:

            return datetime.now()

        return (
            self.last_swing_scan
            + timedelta(
                seconds=self.swing_interval
            )
        )

    # =====================================================
    # NEXT POSITIONAL SCAN
    # =====================================================

    def next_positional_scan(
        self,
    ) -> Optional[datetime]:

        if self.last_positional_scan is None:

            return datetime.now()

        return (
            self.last_positional_scan
            + timedelta(
                seconds=self.positional_interval
            )
        )

    # =====================================================
    # CONFIGURE INTERVALS
    # =====================================================

    def configure_intervals(
        self,
        *,
        intraday: Optional[int] = None,
        swing: Optional[int] = None,
        positional: Optional[int] = None,
    ) -> None:

        if intraday is not None:

            self.intraday_interval = max(
                1,
                int(intraday),
            )

        if swing is not None:

            self.swing_interval = max(
                1,
                int(swing),
            )

        if positional is not None:

            self.positional_interval = max(
                1,
                int(positional),
            )

    # =====================================================
    # RESULTS
    # =====================================================

    def results(
        self,
    ) -> List[Signal]:

        with self._lock:

            return list(
                self.latest_signals
            )

    # =====================================================
    # STATUS
    # =====================================================

    def status(
        self,
    ) -> Dict[str, Any]:

        return {

            "running":
                self.running,

            "paused":
                self.paused,

            "market_status":
                self.market_status(),

            "market_hours_only":
                self.market_hours_only,

            "intraday_interval":
                self.intraday_interval,

            "swing_interval":
                self.swing_interval,

            "positional_interval":
                self.positional_interval,

            "total_scans":
                self.total_scans,

            "intraday_scans":
                self.intraday_scans,

            "swing_scans":
                self.swing_scans,

            "positional_scans":
                self.positional_scans,

            "signals":
                len(
                    self.latest_signals
                ),

            "last_scan":
                (
                    self.last_scan.isoformat()
                    if self.last_scan
                    else None
                ),

            "last_intraday_scan":
                (
                    self.last_intraday_scan.isoformat()
                    if self.last_intraday_scan
                    else None
                ),

            "last_swing_scan":
                (
                    self.last_swing_scan.isoformat()
                    if self.last_swing_scan
                    else None
                ),

            "last_positional_scan":
                (
                    self.last_positional_scan.isoformat()
                    if self.last_positional_scan
                    else None
                ),

            "last_error":
                self.last_error,
        }

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(
        self,
    ) -> Dict[str, Any]:

        issues: List[str] = []

        if self.manager is None:

            issues.append(
                "ScannerManager missing."
            )

        if self.bridge is None:

            issues.append(
                "MarketDataBridge missing."
            )

        if self.last_error:

            issues.append(
                self.last_error
            )

        if self.running:

            if (
                self._thread is None
                or not self._thread.is_alive()
            ):

                issues.append(
                    "Scheduler thread is not alive."
                )

        return {

            "healthy":
                len(issues) == 0,

            "issues":
                issues,

            "running":
                self.running,

            "paused":
                self.paused,

            "market":
                self.market_status(),
        }

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
            "[ScannerScheduler]",
            *message,
        )

    # =====================================================
    # CONTEXT MANAGER
    # =====================================================

    def __enter__(
        self,
    ) -> "ScannerScheduler":

        self.start()

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:

        self.stop()

    # =====================================================
    # MAGIC METHODS
    # =====================================================

    def __bool__(
        self,
    ) -> bool:

        return self.running

    def __repr__(
        self,
    ) -> str:

        return (
            "ScannerScheduler("
            f"running={self.running}, "
            f"paused={self.paused}, "
            f"market='{self.market_status()}', "
            f"scans={self.total_scans}"
            ")"
        )

    def __str__(
        self,
    ) -> str:

        return (
            f"ScannerScheduler | "
            f"{self.market_status()} | "
            f"{self.total_scans} scans | "
            f"{len(self.latest_signals)} signals"
        )


# =========================================================
# FACTORY
# =========================================================

def create_scanner_scheduler(
    manager: ScannerManager,
    bridge: MarketDataBridge,
    *,
    intraday_interval: int = DEFAULT_INTRADAY_INTERVAL,
    swing_interval: int = DEFAULT_SWING_INTERVAL,
    positional_interval: int = DEFAULT_POSITIONAL_INTERVAL,
    market_hours_only: bool = True,
    debug: bool = False,
) -> ScannerScheduler:
    """
    Factory for ScannerScheduler.
    """

    return ScannerScheduler(

        manager=manager,

        bridge=bridge,

        intraday_interval=intraday_interval,

        swing_interval=swing_interval,

        positional_interval=positional_interval,

        market_hours_only=market_hours_only,

        debug=debug,
    )


# =========================================================
# EXPORTS
# =========================================================

__all__ = [

    "ScannerScheduler",

    "create_scanner_scheduler",

    "MARKET_OPEN",

    "MARKET_CLOSE",

    "DEFAULT_INTRADAY_INTERVAL",

    "DEFAULT_SWING_INTERVAL",

    "DEFAULT_POSITIONAL_INTERVAL",
]


# ==========================
# END OF FILE
# ==========================