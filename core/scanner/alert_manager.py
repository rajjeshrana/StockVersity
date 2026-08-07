"""
=========================================================
StockVersity Scanner Pro
Scanner Alert Manager
Version : 2.0
=========================================================

Responsibilities
----------------
• Convert scanner signals into alerts
• Prevent duplicate alerts
• Alert cooldown management
• Minimum quality filters
• BUY / SELL alert filtering
• Track alert history
• Detect changed opportunities
• Dashboard alert feed
• Thread-safe operation

=========================================================
"""

from __future__ import annotations

from datetime import datetime
from datetime import timedelta

from threading import RLock

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from core.scanner.signal import Signal
from core.scanner.signal import SignalType

from core.scanner.result_store import ScannerResultStore


# =========================================================
# ALERT MANAGER
# =========================================================

class ScannerAlertManager:
    """
    Central alert manager for StockVersity Scanner Pro.

    Flow
    ----

    ScannerEngine
        ↓
    ScannerResultStore
        ↓
    ScannerAlertManager
        ↓
    Dashboard / Notification System
    """

    def __init__(
        self,
        *,
        minimum_score: float = 80.0,
        minimum_confidence: float = 75.0,
        minimum_rr: float = 2.0,
        cooldown_minutes: int = 15,
        max_history: int = 1000,
        debug: bool = False,
    ) -> None:

        self.minimum_score = float(
            minimum_score
        )

        self.minimum_confidence = float(
            minimum_confidence
        )

        self.minimum_rr = float(
            minimum_rr
        )

        self.cooldown_minutes = max(
            0,
            int(cooldown_minutes),
        )

        self.max_history = max(
            1,
            int(max_history),
        )

        self.debug = debug

        self._lock = RLock()

        # -------------------------------------------------
        # ALERT HISTORY
        # -------------------------------------------------

        self._history: List[
            Dict[str, Any]
        ] = []

        # -------------------------------------------------
        # LAST ALERT BY KEY
        # -------------------------------------------------

        self._last_alert: Dict[
            str,
            datetime
        ] = {}

        # -------------------------------------------------
        # LAST ALERT PAYLOAD
        # -------------------------------------------------

        self._last_payload: Dict[
            str,
            Dict[str, Any]
        ] = {}

        # -------------------------------------------------
        # SESSION COUNTERS
        # -------------------------------------------------

        self._alerts_generated = 0

        self._alerts_rejected = 0

        self._duplicates_blocked = 0

        self._cooldown_blocked = 0

        self._last_generated_at: Optional[
            datetime
        ] = None

    # =====================================================
    # ALERT KEY
    # =====================================================

    @staticmethod
    def _alert_key(
        signal: Signal,
    ) -> str:
        """
        Unique key for an alert setup.

        Symbol + signal type + scanner + pattern.
        """

        return (
            f"{signal.symbol.upper()}|"
            f"{signal.signal_type.value}|"
            f"{signal.scanner_name.upper()}|"
            f"{signal.pattern.value}"
        )

    # =====================================================
    # QUALITY CHECK
    # =====================================================

    def qualifies(
        self,
        signal: Signal,
    ) -> bool:
        """
        Check whether a signal is good enough
        to become an alert.
        """

        if signal.score < self.minimum_score:

            return False

        if (
            signal.confidence
            < self.minimum_confidence
        ):

            return False

        if (
            signal.risk_reward
            < self.minimum_rr
        ):

            return False

        if signal.entry <= 0:

            return False

        if signal.stop_loss <= 0:

            return False

        if signal.target1 <= 0:

            return False

        if signal.signal_type not in (
            SignalType.BUY,
            SignalType.SELL,
        ):

            return False

        return True

    # =====================================================
    # COOLDOWN
    # =====================================================

    def in_cooldown(
        self,
        signal: Signal,
    ) -> bool:
        """
        Check whether the same setup is still
        inside its cooldown period.
        """

        if self.cooldown_minutes <= 0:

            return False

        key = self._alert_key(
            signal
        )

        with self._lock:

            last_time = self._last_alert.get(
                key
            )

        if last_time is None:

            return False

        cooldown_until = (
            last_time
            + timedelta(
                minutes=self.cooldown_minutes
            )
        )

        return (
            datetime.now()
            < cooldown_until
        )

    # =====================================================
    # DUPLICATE CHECK
    # =====================================================

    def is_duplicate(
        self,
        signal: Signal,
    ) -> bool:
        """
        Detect an unchanged repeated setup.
        """

        key = self._alert_key(
            signal
        )

        with self._lock:

            previous = self._last_payload.get(
                key
            )

        if previous is None:

            return False

        if (
            previous.get("entry")
            != signal.entry
        ):

            return False

        if (
            previous.get("stop_loss")
            != signal.stop_loss
        ):

            return False

        if (
            previous.get("target")
            != signal.target1
        ):

            return False

        if abs(
            float(
                previous.get(
                    "score",
                    0.0,
                )
            )
            - signal.score
        ) >= 1.0:

            return False

        if abs(
            float(
                previous.get(
                    "confidence",
                    0.0,
                )
            )
            - signal.confidence
        ) >= 1.0:

            return False

        return True

    # =====================================================
    # PRIORITY SCORE
    # =====================================================

    @staticmethod
    def priority_score(
        signal: Signal,
    ) -> float:
        """
        Calculate alert priority.

        Weighting
        ---------
        Score       45%
        Confidence  30%
        RR          15%
        RVOL        10%
        """

        rr_component = (
            min(
                max(
                    signal.risk_reward,
                    0.0,
                ),
                5.0,
            )
            / 5.0
            * 100.0
        )

        volume_component = (
            min(
                max(
                    signal.volume_ratio,
                    0.0,
                ),
                5.0,
            )
            / 5.0
            * 100.0
        )

        priority = (

            signal.score * 0.45

            + signal.confidence * 0.30

            + rr_component * 0.15

            + volume_component * 0.10
        )

        return round(
            min(
                max(
                    priority,
                    0.0,
                ),
                100.0,
            ),
            2,
        )

    # =====================================================
    # ALERT GRADE
    # =====================================================

    @staticmethod
    def alert_grade(
        signal: Signal,
    ) -> str:
        """
        Institutional-style alert grading.
        """

        if (
            signal.score >= 90
            and signal.confidence >= 90
            and signal.risk_reward >= 3.0
        ):

            return "A+"

        if (
            signal.score >= 85
            and signal.confidence >= 80
            and signal.risk_reward >= 2.5
        ):

            return "A"

        if (
            signal.score >= 75
            and signal.confidence >= 70
            and signal.risk_reward >= 2.0
        ):

            return "B"

        return "C"

    # =====================================================
    # CREATE PAYLOAD
    # =====================================================

    def create_payload(
        self,
        signal: Signal,
    ) -> Dict[str, Any]:
        """
        Create standardized alert payload.
        """

        now = datetime.now()

        return {

            "alert_id":
                signal.signal_id,

            "symbol":
                signal.symbol,

            "instrument_key":
                signal.instrument_key,

            "exchange":
                signal.exchange,

            "scanner":
                signal.scanner_name,

            "strategy":
                signal.strategy_name,

            "signal":
                signal.signal_type.value,

            "pattern":
                signal.pattern.value,

            "strength":
                signal.strength.value,

            "timeframe":
                signal.timeframe,

            "sector":
                signal.sector,

            "market_trend":
                signal.market_trend.value,

            "price":
                signal.last_price,

            "entry":
                signal.entry,

            "stop_loss":
                signal.stop_loss,

            "target":
                signal.target1,

            "target2":
                signal.target2,

            "target3":
                signal.target3,

            "risk_reward":
                signal.risk_reward,

            "quantity":
                signal.quantity,

            "expected_profit":
                signal.expected_profit,

            "expected_loss":
                signal.expected_loss,

            "score":
                signal.score,

            "confidence":
                signal.confidence,

            "priority":
                self.priority_score(
                    signal
                ),

            "grade":
                self.alert_grade(
                    signal
                ),

            "volume":
                signal.volume,

            "volume_ratio":
                signal.volume_ratio,

            "rsi":
                signal.rsi,

            "adx":
                signal.adx,

            "vwap":
                signal.vwap,

            "remarks":
                signal.remarks,

            "tags":
                list(
                    signal.tags
                ),

            "created_at":
                now.isoformat(),

        }

    # =====================================================
    # GENERATE ALERT
    # =====================================================

    def generate(
        self,
        signal: Signal,
        *,
        force: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Generate an alert from one signal.

        Returns None when rejected.
        """

        # -------------------------------------------------
        # QUALITY FILTER
        # -------------------------------------------------

        if not force:

            if not self.qualifies(
                signal
            ):

                with self._lock:

                    self._alerts_rejected += 1

                return None

        # -------------------------------------------------
        # DUPLICATE FILTER
        # -------------------------------------------------

        if not force:

            if self.is_duplicate(
                signal
            ):

                with self._lock:

                    self._duplicates_blocked += 1

                return None

        # -------------------------------------------------
        # COOLDOWN FILTER
        # -------------------------------------------------

        if not force:

            if self.in_cooldown(
                signal
            ):

                with self._lock:

                    self._cooldown_blocked += 1

                return None

        # -------------------------------------------------
        # BUILD ALERT
        # -------------------------------------------------

        payload = self.create_payload(
            signal
        )

        key = self._alert_key(
            signal
        )

        now = datetime.now()

        # -------------------------------------------------
        # STORE ALERT
        # -------------------------------------------------

        with self._lock:

            self._history.append(
                payload
            )

            self._last_alert[
                key
            ] = now

            self._last_payload[
                key
            ] = dict(
                payload
            )

            self._alerts_generated += 1

            self._last_generated_at = now

            self._trim_history()

        self.log(
            "Alert generated:",
            signal.symbol,
            signal.signal_type.value,
            payload["grade"],
        )

        return payload

    # =====================================================
    # GENERATE MANY
    # =====================================================

    def generate_many(
        self,
        signals: List[Signal],
        *,
        force: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Generate alerts from multiple signals.
        """

        alerts: List[
            Dict[str, Any]
        ] = []

        ranked = sorted(

            signals,

            key=lambda signal: (
                self.priority_score(
                    signal
                ),
                signal.score,
                signal.confidence,
            ),

            reverse=True,
        )

        for signal in ranked:

            alert = self.generate(
                signal,
                force=force,
            )

            if alert is not None:

                alerts.append(
                    alert
                )

        return alerts

    # =====================================================
    # PROCESS RESULT STORE
    # =====================================================

    def process_store(
        self,
        store: ScannerResultStore,
    ) -> List[Dict[str, Any]]:
        """
        Generate alerts from new and changed
        scanner results.
        """

        candidates = (
            store.new_signals()
            + store.changed_signals()
        )

        # -------------------------------------------------
        # REMOVE DUPLICATE SYMBOL OBJECTS
        # -------------------------------------------------

        unique: Dict[
            str,
            Signal
        ] = {}

        for signal in candidates:

            existing = unique.get(
                signal.symbol
            )

            if existing is None:

                unique[
                    signal.symbol
                ] = signal

                continue

            if (
                self.priority_score(
                    signal
                )
                >
                self.priority_score(
                    existing
                )
            ):

                unique[
                    signal.symbol
                ] = signal

        alerts = self.generate_many(
            list(
                unique.values()
            )
        )

        return alerts

    # =====================================================
    # BUY ALERTS
    # =====================================================

    def buy_alerts(
        self,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:

        alerts = [

            alert

            for alert in self.history()

            if (
                alert.get("signal")
                == SignalType.BUY.value
            )
        ]

        if limit is not None:

            return alerts[
                :max(
                    0,
                    int(limit),
                )
            ]

        return alerts

    # =====================================================
    # SELL ALERTS
    # =====================================================

    def sell_alerts(
        self,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:

        alerts = [

            alert

            for alert in self.history()

            if (
                alert.get("signal")
                == SignalType.SELL.value
            )
        ]

        if limit is not None:

            return alerts[
                :max(
                    0,
                    int(limit),
                )
            ]

        return alerts

    # =====================================================
    # HISTORY
    # =====================================================

    def history(
        self,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Return newest alerts first.
        """

        with self._lock:

            alerts = list(
                reversed(
                    self._history
                )
            )

        if limit is not None:

            return alerts[
                :max(
                    0,
                    int(limit),
                )
            ]

        return alerts

    # =====================================================
    # LATEST
    # =====================================================

    def latest(
        self,
    ) -> Optional[Dict[str, Any]]:

        alerts = self.history(
            limit=1
        )

        if not alerts:

            return None

        return alerts[0]

    # =====================================================
    # FIND BY SYMBOL
    # =====================================================

    def by_symbol(
        self,
        symbol: str,
    ) -> List[Dict[str, Any]]:

        symbol = symbol.upper()

        return [

            alert

            for alert in self.history()

            if (
                str(
                    alert.get(
                        "symbol",
                        "",
                    )
                ).upper()
                == symbol
            )
        ]

    # =====================================================
    # HIGH PRIORITY ALERTS
    # =====================================================

    def high_priority(
        self,
        minimum_priority: float = 80.0,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:

        alerts = [

            alert

            for alert in self.history()

            if (
                float(
                    alert.get(
                        "priority",
                        0.0,
                    )
                )
                >= minimum_priority
            )
        ]

        alerts.sort(

            key=lambda alert: (
                float(
                    alert.get(
                        "priority",
                        0.0,
                    )
                ),
                float(
                    alert.get(
                        "score",
                        0.0,
                    )
                ),
            ),

            reverse=True,
        )

        return alerts[
            :max(
                1,
                int(limit),
            )
        ]

    # =====================================================
    # DASHBOARD FEED
    # =====================================================

    def dashboard_feed(
        self,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Lightweight alert feed for UI.
        """

        rows: List[
            Dict[str, Any]
        ] = []

        for alert in self.history(
            limit=limit
        ):

            rows.append(

                {

                    "symbol":
                        alert.get(
                            "symbol"
                        ),

                    "signal":
                        alert.get(
                            "signal"
                        ),

                    "scanner":
                        alert.get(
                            "scanner"
                        ),

                    "pattern":
                        alert.get(
                            "pattern"
                        ),

                    "entry":
                        alert.get(
                            "entry"
                        ),

                    "stop_loss":
                        alert.get(
                            "stop_loss"
                        ),

                    "target":
                        alert.get(
                            "target"
                        ),

                    "rr":
                        alert.get(
                            "risk_reward"
                        ),

                    "score":
                        alert.get(
                            "score"
                        ),

                    "confidence":
                        alert.get(
                            "confidence"
                        ),

                    "priority":
                        alert.get(
                            "priority"
                        ),

                    "grade":
                        alert.get(
                            "grade"
                        ),

                    "time":
                        alert.get(
                            "created_at"
                        ),

                }

            )

        return rows

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> Dict[str, Any]:

        history = self.history()

        buy_count = sum(

            1

            for alert in history

            if (
                alert.get("signal")
                == SignalType.BUY.value
            )
        )

        sell_count = sum(

            1

            for alert in history

            if (
                alert.get("signal")
                == SignalType.SELL.value
            )
        )

        return {

            "total_history":
                len(history),

            "buy_alerts":
                buy_count,

            "sell_alerts":
                sell_count,

            "generated":
                self._alerts_generated,

            "rejected":
                self._alerts_rejected,

            "duplicates_blocked":
                self._duplicates_blocked,

            "cooldown_blocked":
                self._cooldown_blocked,

            "minimum_score":
                self.minimum_score,

            "minimum_confidence":
                self.minimum_confidence,

            "minimum_rr":
                self.minimum_rr,

            "cooldown_minutes":
                self.cooldown_minutes,

            "last_generated_at":
                (
                    self._last_generated_at.isoformat()
                    if self._last_generated_at
                    else None
                ),

        }

    # =====================================================
    # CONFIGURE
    # =====================================================

    def configure(
        self,
        *,
        minimum_score: Optional[
            float
        ] = None,
        minimum_confidence: Optional[
            float
        ] = None,
        minimum_rr: Optional[
            float
        ] = None,
        cooldown_minutes: Optional[
            int
        ] = None,
        debug: Optional[
            bool
        ] = None,
    ) -> None:

        with self._lock:

            if minimum_score is not None:

                self.minimum_score = float(
                    minimum_score
                )

            if minimum_confidence is not None:

                self.minimum_confidence = float(
                    minimum_confidence
                )

            if minimum_rr is not None:

                self.minimum_rr = float(
                    minimum_rr
                )

            if cooldown_minutes is not None:

                self.cooldown_minutes = max(
                    0,
                    int(
                        cooldown_minutes
                    ),
                )

            if debug is not None:

                self.debug = bool(
                    debug
                )

    # =====================================================
    # TRIM HISTORY
    # =====================================================

    def _trim_history(
        self,
    ) -> None:

        if (
            len(self._history)
            <= self.max_history
        ):

            return

        self._history = self._history[
            -self.max_history:
        ]

    # =====================================================
    # CLEAR HISTORY
    # =====================================================

    def clear_history(
        self,
    ) -> None:

        with self._lock:

            self._history.clear()

    # =====================================================
    # CLEAR COOLDOWNS
    # =====================================================

    def clear_cooldowns(
        self,
    ) -> None:

        with self._lock:

            self._last_alert.clear()

            self._last_payload.clear()

    # =====================================================
    # RESET
    # =====================================================

    def reset(
        self,
    ) -> None:

        with self._lock:

            self._history.clear()

            self._last_alert.clear()

            self._last_payload.clear()

            self._alerts_generated = 0

            self._alerts_rejected = 0

            self._duplicates_blocked = 0

            self._cooldown_blocked = 0

            self._last_generated_at = None

    # =====================================================
    # LOGGING
    # =====================================================

    def log(
        self,
        *message: Any,
    ) -> None:

        if not self.debug:

            return

        print(
            "[ScannerAlertManager]",
            *message,
        )

    # =====================================================
    # MAGIC METHODS
    # =====================================================

    def __len__(
        self,
    ) -> int:

        with self._lock:

            return len(
                self._history
            )

    def __bool__(
        self,
    ) -> bool:

        return len(self) > 0

    def __iter__(
        self,
    ):

        return iter(
            self.history()
        )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (
            "ScannerAlertManager("
            f"alerts={len(self)}, "
            f"minimum_score={self.minimum_score}, "
            f"minimum_confidence={self.minimum_confidence}, "
            f"minimum_rr={self.minimum_rr}, "
            f"cooldown={self.cooldown_minutes}m"
            ")"
        )


# =========================================================
# FACTORY
# =========================================================

def create_alert_manager(
    *,
    minimum_score: float = 80.0,
    minimum_confidence: float = 75.0,
    minimum_rr: float = 2.0,
    cooldown_minutes: int = 15,
    max_history: int = 1000,
    debug: bool = False,
) -> ScannerAlertManager:
    """
    Factory for ScannerAlertManager.
    """

    return ScannerAlertManager(

        minimum_score=minimum_score,

        minimum_confidence=minimum_confidence,

        minimum_rr=minimum_rr,

        cooldown_minutes=cooldown_minutes,

        max_history=max_history,

        debug=debug,
    )


# =========================================================
# EXPORTS
# =========================================================

__all__ = [

    "ScannerAlertManager",

    "create_alert_manager",
]


# ==========================
# END OF FILE
# ==========================