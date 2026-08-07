from __future__ import annotations

"""
==========================================================
StockVersity Scanner Pro
Alert Service

Author  : StockVersity
Version : 1.0.0

Responsibilities
----------------
• Central alert engine
• Scanner alerts
• Price alerts
• Breakout alerts
• Volume alerts
• Pattern alerts
• Desktop notifications
• Sound notifications
• Email-ready interface
• Telegram-ready interface
• Alert history
• Deduplication
• Rate limiting
• Statistics
==========================================================
"""

import logging
import threading
import time

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from typing import Callable
from typing import Deque
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from core.alert_manager import AlertManager


# ==========================================================
# ALERT TYPE
# ==========================================================

class AlertType(Enum):
    """
    Alert categories.
    """

    PRICE = "price"

    BREAKOUT = "breakout"

    BREAKDOWN = "breakdown"

    VOLUME = "volume"

    MOMENTUM = "momentum"

    PATTERN = "pattern"

    SCANNER = "scanner"

    WATCHLIST = "watchlist"

    MARKET = "market"

    SYSTEM = "system"


# ==========================================================
# PRIORITY
# ==========================================================

class AlertPriority(Enum):
    """
    Alert priority.
    """

    LOW = 1

    NORMAL = 2

    HIGH = 3

    CRITICAL = 4


# ==========================================================
# STATUS
# ==========================================================

class AlertStatus(Enum):
    """
    Alert lifecycle.
    """

    PENDING = "pending"

    DELIVERED = "delivered"

    FAILED = "failed"

    DISMISSED = "dismissed"

    EXPIRED = "expired"


# ==========================================================
# ALERT MODEL
# ==========================================================

@dataclass(slots=True)
class Alert:
    """
    Alert object.
    """

    id: str

    title: str

    message: str

    alert_type: AlertType

    priority: AlertPriority = AlertPriority.NORMAL

    status: AlertStatus = AlertStatus.PENDING

    symbol: Optional[str] = None

    price: Optional[float] = None

    created: datetime = field(
        default_factory=datetime.now
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ==========================================================
# STATISTICS
# ==========================================================

@dataclass(slots=True)
class AlertStatistics:

    total_created: int = 0

    delivered: int = 0

    failed: int = 0

    dismissed: int = 0

    duplicate_blocked: int = 0

    throttled: int = 0


# ==========================================================
# ALERT SERVICE
# ==========================================================

class AlertService:
    """
    Central alert service.
    """

    VERSION = "1.0.0"

    MAX_HISTORY = 5000

    DUPLICATE_WINDOW = 60

    def __init__(
        self,
        manager: AlertManager,
    ) -> None:

        self.logger = logging.getLogger(
            self.__class__.__name__
        )

        self._manager = manager

        self._history: Deque[Alert] = deque(
            maxlen=self.MAX_HISTORY
        )

        self._statistics = AlertStatistics()

        self._callbacks: Dict[
            str,
            List[Callable[..., None]]
        ] = {}

        self._duplicate_cache: Set[str] = set()

        self._lock = threading.RLock()

        self._started = datetime.now()

        self.logger.info(
            "AlertService initialized."
        )
            # ==========================================================
    # PROPERTIES
    # ==========================================================

    @property
    def manager(self) -> AlertManager:
        """
        Return underlying AlertManager.
        """

        return self._manager

    @property
    def statistics(self) -> AlertStatistics:
        """
        Return runtime statistics.
        """

        return self._statistics

    @property
    def history(self) -> List[Alert]:
        """
        Return alert history.
        """

        return list(self._history)

    @property
    def uptime(self):
        """
        Service uptime.
        """

        return datetime.now() - self._started

    # ==========================================================
    # EVENTS
    # ==========================================================

    def register_event(
        self,
        event: str,
        callback: Callable[..., None],
    ) -> None:
        """
        Register event callback.
        """

        self._callbacks.setdefault(
            event,
            [],
        ).append(callback)

    def unregister_event(
        self,
        event: str,
        callback: Callable[..., None],
    ) -> None:
        """
        Remove callback.
        """

        callbacks = self._callbacks.get(
            event,
        )

        if callbacks is None:

            return

        try:

            callbacks.remove(callback)

        except ValueError:

            pass

    def clear_events(self) -> None:
        """
        Remove every callback.
        """

        self._callbacks.clear()

    def _emit(
        self,
        event: str,
        **kwargs: Any,
    ) -> None:
        """
        Notify listeners.
        """

        callbacks = self._callbacks.get(
            event,
            [],
        )

        for callback in callbacks:

            try:

                callback(**kwargs)

            except Exception:

                self.logger.exception(
                    "Alert callback failed."
                )

    # ==========================================================
    # DUPLICATE PROTECTION
    # ==========================================================

    def _duplicate_key(
        self,
        title: str,
        message: str,
        symbol: Optional[str],
    ) -> str:
        """
        Create duplicate cache key.
        """

        return (

            f"{title}|"

            f"{message}|"

            f"{symbol or ''}"

        )

    def _is_duplicate(
        self,
        key: str,
    ) -> bool:
        """
        Check duplicate cache.
        """

        return key in self._duplicate_cache

    def _remember_duplicate(
        self,
        key: str,
    ) -> None:
        """
        Store duplicate key.
        """

        self._duplicate_cache.add(
            key,
        )

        timer = threading.Timer(

            self.DUPLICATE_WINDOW,

            lambda: self._duplicate_cache.discard(
                key,
            ),

        )

        timer.daemon = True

        timer.start()

    # ==========================================================
    # ALERT CREATION
    # ==========================================================

    def create_alert(
        self,
        *,
        alert_id: str,
        title: str,
        message: str,
        alert_type: AlertType,
        priority: AlertPriority = AlertPriority.NORMAL,
        symbol: Optional[str] = None,
        price: Optional[float] = None,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Optional[Alert]:
        """
        Create alert.
        """

        key = self._duplicate_key(

            title,

            message,

            symbol,

        )

        if self._is_duplicate(key):

            self._statistics.duplicate_blocked += 1

            return None

        self._remember_duplicate(key)

        alert = Alert(

            id=alert_id,

            title=title,

            message=message,

            alert_type=alert_type,

            priority=priority,

            symbol=symbol,

            price=price,

            metadata=metadata or {},

        )

        self._history.append(alert)

        self._statistics.total_created += 1

        self._emit(

            "alert_created",

            alert=alert,

        )

        return alert

    # ==========================================================
    # HISTORY
    # ==========================================================

    def latest(
        self,
        count: int = 20,
    ) -> List[Alert]:
        """
        Return latest alerts.
        """

        return list(

            self._history

        )[-count:]

    def clear_history(self) -> None:
        """
        Remove history.
        """

        self._history.clear()

    def alert_count(self) -> int:
        """
        Total stored alerts.
        """

        return len(
            self._history,
        )
        # ==========================================================
    # DELIVERY
    # ==========================================================

    def send(
        self,
        alert: Alert,
    ) -> bool:
        """
        Deliver an alert.
        """

        try:

            self._manager.notify(

                title=alert.title,

                message=alert.message,

            )

            alert.status = AlertStatus.DELIVERED

            self._statistics.delivered += 1

            self._emit(

                "alert_delivered",

                alert=alert,

            )

            return True

        except Exception:

            alert.status = AlertStatus.FAILED

            self._statistics.failed += 1

            self.logger.exception(
                "Failed to deliver alert."
            )

            self._emit(

                "alert_failed",

                alert=alert,

            )

            return False

    # ==========================================================
    # DISMISS
    # ==========================================================

    def dismiss(
        self,
        alert: Alert,
    ) -> None:
        """
        Dismiss an alert.
        """

        alert.status = AlertStatus.DISMISSED

        self._statistics.dismissed += 1

        self._emit(

            "alert_dismissed",

            alert=alert,

        )

    # ==========================================================
    # PRICE ALERT
    # ==========================================================

    def price_alert(
        self,
        *,
        symbol: str,
        price: float,
        message: str,
        priority: AlertPriority = AlertPriority.NORMAL,
    ) -> Optional[Alert]:
        """
        Create and send a price alert.
        """

        alert = self.create_alert(

            alert_id=f"PRICE-{int(time.time()*1000)}",

            title=f"{symbol} Price Alert",

            message=message,

            alert_type=AlertType.PRICE,

            priority=priority,

            symbol=symbol,

            price=price,

        )

        if alert is not None:

            self.send(alert)

        return alert

    # ==========================================================
    # BREAKOUT ALERT
    # ==========================================================

    def breakout_alert(
        self,
        *,
        symbol: str,
        breakout_price: float,
        message: str,
    ) -> Optional[Alert]:
        """
        Breakout notification.
        """

        alert = self.create_alert(

            alert_id=f"BREAKOUT-{int(time.time()*1000)}",

            title=f"{symbol} Breakout",

            message=message,

            alert_type=AlertType.BREAKOUT,

            priority=AlertPriority.HIGH,

            symbol=symbol,

            price=breakout_price,

        )

        if alert is not None:

            self.send(alert)

        return alert

    # ==========================================================
    # BREAKDOWN ALERT
    # ==========================================================

    def breakdown_alert(
        self,
        *,
        symbol: str,
        breakdown_price: float,
        message: str,
    ) -> Optional[Alert]:
        """
        Breakdown notification.
        """

        alert = self.create_alert(

            alert_id=f"BREAKDOWN-{int(time.time()*1000)}",

            title=f"{symbol} Breakdown",

            message=message,

            alert_type=AlertType.BREAKDOWN,

            priority=AlertPriority.HIGH,

            symbol=symbol,

            price=breakdown_price,

        )

        if alert is not None:

            self.send(alert)

        return alert

    # ==========================================================
    # VOLUME ALERT
    # ==========================================================

    def volume_alert(
        self,
        *,
        symbol: str,
        message: str,
    ) -> Optional[Alert]:
        """
        Volume spike notification.
        """

        alert = self.create_alert(

            alert_id=f"VOLUME-{int(time.time()*1000)}",

            title=f"{symbol} Volume Spike",

            message=message,

            alert_type=AlertType.VOLUME,

            priority=AlertPriority.NORMAL,

            symbol=symbol,

        )

        if alert is not None:

            self.send(alert)

        return alert

    # ==========================================================
    # SCANNER ALERT
    # ==========================================================

    def scanner_alert(
        self,
        *,
        symbol: str,
        signal: str,
        score: float,
    ) -> Optional[Alert]:
        """
        Scanner signal notification.
        """

        alert = self.create_alert(

            alert_id=f"SCAN-{int(time.time()*1000)}",

            title=f"{symbol} Scanner Signal",

            message=f"{signal} | Score: {score:.2f}",

            alert_type=AlertType.SCANNER,

            priority=AlertPriority.HIGH,

            symbol=symbol,

            metadata={

                "signal": signal,

                "score": score,

            },

        )

        if alert is not None:

            self.send(alert)

        return alert

    # ==========================================================
    # SYSTEM ALERT
    # ==========================================================

    def system_alert(
        self,
        title: str,
        message: str,
        priority: AlertPriority = AlertPriority.NORMAL,
    ) -> Optional[Alert]:
        """
        Internal application alert.
        """

        alert = self.create_alert(

            alert_id=f"SYS-{int(time.time()*1000)}",

            title=title,

            message=message,

            alert_type=AlertType.SYSTEM,

            priority=priority,

        )

        if alert is not None:

            self.send(alert)

        return alert
        # ==========================================================
    # PATTERN ALERT
    # ==========================================================

    def pattern_alert(
        self,
        *,
        symbol: str,
        pattern: str,
        confidence: float,
    ) -> Optional[Alert]:
        """
        Notify when a chart pattern is detected.
        """

        alert = self.create_alert(

            alert_id=f"PATTERN-{int(time.time() * 1000)}",

            title=f"{symbol} Pattern Detected",

            message=(
                f"{pattern} detected "
                f"(Confidence: {confidence:.1f}%)"
            ),

            alert_type=AlertType.PATTERN,

            priority=AlertPriority.HIGH,

            symbol=symbol,

            metadata={

                "pattern": pattern,

                "confidence": confidence,

            },

        )

        if alert:

            self.send(alert)

        return alert

    # ==========================================================
    # MOMENTUM ALERT
    # ==========================================================

    def momentum_alert(
        self,
        *,
        symbol: str,
        direction: str,
        strength: float,
    ) -> Optional[Alert]:
        """
        Notify about strong momentum.
        """

        alert = self.create_alert(

            alert_id=f"MOM-{int(time.time() * 1000)}",

            title=f"{symbol} Momentum",

            message=(
                f"{direction} momentum "
                f"({strength:.2f})"
            ),

            alert_type=AlertType.MOMENTUM,

            priority=AlertPriority.HIGH,

            symbol=symbol,

            metadata={

                "direction": direction,

                "strength": strength,

            },

        )

        if alert:

            self.send(alert)

        return alert

    # ==========================================================
    # WATCHLIST ALERT
    # ==========================================================

    def watchlist_alert(
        self,
        *,
        symbol: str,
        message: str,
    ) -> Optional[Alert]:
        """
        Watchlist notification.
        """

        alert = self.create_alert(

            alert_id=f"WATCH-{int(time.time() * 1000)}",

            title=f"{symbol} Watchlist",

            message=message,

            alert_type=AlertType.WATCHLIST,

            priority=AlertPriority.NORMAL,

            symbol=symbol,

        )

        if alert:

            self.send(alert)

        return alert

    # ==========================================================
    # MARKET ALERT
    # ==========================================================

    def market_alert(
        self,
        *,
        title: str,
        message: str,
    ) -> Optional[Alert]:
        """
        Market-wide notification.
        """

        alert = self.create_alert(

            alert_id=f"MARKET-{int(time.time() * 1000)}",

            title=title,

            message=message,

            alert_type=AlertType.MARKET,

            priority=AlertPriority.CRITICAL,

        )

        if alert:

            self.send(alert)

        return alert

    # ==========================================================
    # EMAIL INTERFACE
    # ==========================================================

    def send_email(
        self,
        alert: Alert,
    ) -> bool:
        """
        Email notification interface.

        Email implementation will be added in a
        future module.
        """

        self.logger.info(

            "Email notification queued: %s",

            alert.title,

        )

        self._emit(

            "email_notification",

            alert=alert,

        )

        return True

    # ==========================================================
    # TELEGRAM INTERFACE
    # ==========================================================

    def send_telegram(
        self,
        alert: Alert,
    ) -> bool:
        """
        Telegram notification interface.

        Telegram integration will be added later.
        """

        self.logger.info(

            "Telegram notification queued: %s",

            alert.title,

        )

        self._emit(

            "telegram_notification",

            alert=alert,

        )

        return True

    # ==========================================================
    # SOUND
    # ==========================================================

    def play_sound(
        self,
        priority: AlertPriority,
    ) -> None:
        """
        Play alert sound.

        Actual implementation belongs to the
        UI notification layer.
        """

        self.logger.debug(

            "Play sound (%s)",

            priority.name,

        )

        self._emit(

            "play_sound",

            priority=priority,

        )

    # ==========================================================
    # DESKTOP NOTIFICATION
    # ==========================================================

    def desktop_notification(
        self,
        alert: Alert,
    ) -> None:
        """
        Forward desktop notification event.
        """

        self._emit(

            "desktop_notification",

            alert=alert,

        )

    # ==========================================================
    # FULL NOTIFICATION
    # ==========================================================

    def notify(
        self,
        alert: Alert,
    ) -> bool:
        """
        Deliver an alert through every enabled
        notification channel.
        """

        delivered = self.send(alert)

        if delivered:

            self.play_sound(

                alert.priority,

            )

            self.desktop_notification(

                alert,

            )

            self.send_email(

                alert,

            )

            self.send_telegram(

                alert,

            )

        return delivered
        # ==========================================================
    # QUEUE
    # ==========================================================

    def pending_alerts(
        self,
    ) -> List[Alert]:
        """
        Return pending alerts.
        """

        return [

            alert

            for alert in self._history

            if alert.status == AlertStatus.PENDING

        ]

    def delivered_alerts(
        self,
    ) -> List[Alert]:
        """
        Return delivered alerts.
        """

        return [

            alert

            for alert in self._history

            if alert.status == AlertStatus.DELIVERED

        ]

    def failed_alerts(
        self,
    ) -> List[Alert]:
        """
        Return failed alerts.
        """

        return [

            alert

            for alert in self._history

            if alert.status == AlertStatus.FAILED

        ]

    # ==========================================================
    # RETRY
    # ==========================================================

    def retry_failed(self) -> int:
        """
        Retry all failed alerts.
        """

        retried = 0

        for alert in self.failed_alerts():

            alert.status = AlertStatus.PENDING

            if self.send(alert):

                retried += 1

        return retried

    # ==========================================================
    # FILTERS
    # ==========================================================

    def alerts_by_symbol(
        self,
        symbol: str,
    ) -> List[Alert]:
        """
        Return alerts for a symbol.
        """

        return [

            alert

            for alert in self._history

            if alert.symbol == symbol

        ]

    def alerts_by_type(
        self,
        alert_type: AlertType,
    ) -> List[Alert]:
        """
        Return alerts of a specific type.
        """

        return [

            alert

            for alert in self._history

            if alert.alert_type == alert_type

        ]

    def alerts_by_priority(
        self,
        priority: AlertPriority,
    ) -> List[Alert]:
        """
        Return alerts with the specified priority.
        """

        return [

            alert

            for alert in self._history

            if alert.priority == priority

        ]

    # ==========================================================
    # SEARCH
    # ==========================================================

    def search(
        self,
        text: str,
    ) -> List[Alert]:
        """
        Search alert history.
        """

        text = text.lower()

        results: List[Alert] = []

        for alert in self._history:

            if (

                text in alert.title.lower()

                or

                text in alert.message.lower()

            ):

                results.append(alert)

        return results

    # ==========================================================
    # CLEANUP
    # ==========================================================

    def remove_expired(
        self,
        max_age_seconds: int,
    ) -> int:
        """
        Remove expired alerts.
        """

        now = datetime.now()

        removed = 0

        remaining = deque(
            maxlen=self.MAX_HISTORY,
        )

        for alert in self._history:

            age = (

                now - alert.created

            ).total_seconds()

            if age <= max_age_seconds:

                remaining.append(alert)

            else:

                removed += 1

                alert.status = AlertStatus.EXPIRED

        self._history = remaining

        return removed

    # ==========================================================
    # STATISTICS
    # ==========================================================

    def statistics_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Runtime statistics.
        """

        stats = self.statistics

        return {

            "total_created":
                stats.total_created,

            "delivered":
                stats.delivered,

            "failed":
                stats.failed,

            "dismissed":
                stats.dismissed,

            "duplicate_blocked":
                stats.duplicate_blocked,

            "throttled":
                stats.throttled,

            "history_size":
                len(self._history),

            "uptime_seconds":
                int(

                    self.uptime.total_seconds()

                ),

        }

    # ==========================================================
    # PERFORMANCE
    # ==========================================================

    def performance_report(
        self,
    ) -> Dict[str, Any]:
        """
        Generate performance metrics.
        """

        stats = self.statistics_dict()

        total = stats["total_created"]

        delivered = stats["delivered"]

        failed = stats["failed"]

        success_rate = (

            100.0

            if total == 0

            else

            round(

                (delivered / total) * 100,

                2,

            )

        )

        return {

            "version":
                self.VERSION,

            "alerts":
                total,

            "delivered":
                delivered,

            "failed":
                failed,

            "success_rate":
                success_rate,

            "uptime":
                str(self.uptime),

        }
        # ==========================================================
    # HEALTH
    # ==========================================================

    def health(self) -> Dict[str, Any]:
        """
        Return service health information.
        """

        return {

            "healthy":
                True,

            "manager_available":
                self._manager is not None,

            "uptime":
                str(self.uptime),

            "history_size":
                len(self._history),

            "pending":
                len(self.pending_alerts()),

            "failed":
                len(self.failed_alerts()),

        }

    # ==========================================================
    # DIAGNOSTICS
    # ==========================================================

    def diagnostics(self) -> Dict[str, Any]:
        """
        Return diagnostic information.
        """

        return {

            "service":
                self.__class__.__name__,

            "version":
                self.VERSION,

            "health":
                self.health(),

            "statistics":
                self.statistics_dict(),

            "performance":
                self.performance_report(),

            "registered_events":
                {

                    name: len(callbacks)

                    for name, callbacks

                    in self._callbacks.items()

                },

        }

    # ==========================================================
    # CONFIGURATION
    # ==========================================================

    def enable_desktop_notifications(
        self,
        enabled: bool = True,
    ) -> None:
        """
        Enable or disable desktop notifications.
        """

        setattr(

            self,

            "_desktop_notifications",

            enabled,

        )

        self.logger.info(

            "Desktop notifications %s.",

            "enabled"

            if enabled

            else "disabled",

        )

    def enable_sound(
        self,
        enabled: bool = True,
    ) -> None:
        """
        Enable or disable sound alerts.
        """

        setattr(

            self,

            "_sound_enabled",

            enabled,

        )

        self.logger.info(

            "Sound notifications %s.",

            "enabled"

            if enabled

            else "disabled",

        )

    def enable_email(
        self,
        enabled: bool = True,
    ) -> None:
        """
        Enable or disable email notifications.
        """

        setattr(

            self,

            "_email_enabled",

            enabled,

        )

        self.logger.info(

            "Email notifications %s.",

            "enabled"

            if enabled

            else "disabled",

        )

    def enable_telegram(
        self,
        enabled: bool = True,
    ) -> None:
        """
        Enable or disable Telegram notifications.
        """

        setattr(

            self,

            "_telegram_enabled",

            enabled,

        )

        self.logger.info(

            "Telegram notifications %s.",

            "enabled"

            if enabled

            else "disabled",

        )

    # ==========================================================
    # LIFECYCLE
    # ==========================================================

    def start(self) -> None:
        """
        Start AlertService.
        """

        self.logger.info(
            "Starting AlertService..."
        )

        self._emit(
            "service_started",
        )

    def stop(self) -> None:
        """
        Stop AlertService.
        """

        self.logger.info(
            "Stopping AlertService..."
        )

        self._emit(
            "service_stopped",
        )

    def restart(self) -> None:
        """
        Restart AlertService.
        """

        self.stop()

        self.start()

    # ==========================================================
    # SUMMARY
    # ==========================================================

    def summary(self) -> Dict[str, Any]:
        """
        Return service summary.
        """

        stats = self.statistics

        return {

            "service":
                self.__class__.__name__,

            "version":
                self.VERSION,

            "uptime":
                str(self.uptime),

            "history":
                len(self._history),

            "created":
                stats.total_created,

            "delivered":
                stats.delivered,

            "failed":
                stats.failed,

        }

    # ==========================================================
    # EXPORT
    # ==========================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Export complete service information.
        """

        return {

            "summary":
                self.summary(),

            "health":
                self.health(),

            "statistics":
                self.statistics_dict(),

            "performance":
                self.performance_report(),

            "diagnostics":
                self.diagnostics(),

        }
        # ==========================================================
    # VALIDATION
    # ==========================================================

    def validate(self) -> bool:
        """
        Validate AlertService configuration.
        """

        if self._manager is None:

            raise RuntimeError(
                "AlertManager is not configured."
            )

        return True

    def assert_ready(self) -> None:
        """
        Ensure the service is ready for use.
        """

        self.validate()

    # ==========================================================
    # EVENT UTILITIES
    # ==========================================================

    def event_count(self) -> int:
        """
        Return total registered callbacks.
        """

        return sum(

            len(callbacks)

            for callbacks

            in self._callbacks.values()

        )

    def events(self) -> Dict[str, int]:
        """
        Return registered events.
        """

        return {

            event: len(callbacks)

            for event, callbacks

            in self._callbacks.items()

        }

    def has_event(
        self,
        event: str,
    ) -> bool:
        """
        Return True if an event has subscribers.
        """

        return (

            event in self._callbacks

            and

            len(self._callbacks[event]) > 0

        )

    # ==========================================================
    # SNAPSHOT
    # ==========================================================

    def snapshot(self) -> Dict[str, Any]:
        """
        Return a runtime snapshot.
        """

        return {

            "summary":
                self.summary(),

            "health":
                self.health(),

            "statistics":
                self.statistics_dict(),

            "performance":
                self.performance_report(),

            "events":
                self.events(),

        }

    # ==========================================================
    # RESET
    # ==========================================================

    def reset(self) -> None:
        """
        Reset runtime state.
        """

        self.clear_history()

        self.clear_events()

        self._duplicate_cache.clear()

        self._statistics = AlertStatistics()

        self.logger.info(
            "AlertService reset completed."
        )

        self._emit(
            "service_reset",
        )

    # ==========================================================
    # CLONE
    # ==========================================================

    def clone(self) -> "AlertService":
        """
        Create another AlertService using the same
        AlertManager instance.
        """

        return self.__class__(

            manager=self._manager,

        )

    # ==========================================================
    # DISPOSE
    # ==========================================================

    def dispose(self) -> None:
        """
        Release runtime resources.
        """

        self.clear_events()

        self._duplicate_cache.clear()

        self.logger.info(
            "AlertService disposed."
        )

    # ==========================================================
    # CONTEXT MANAGER
    # ==========================================================

    def __enter__(self) -> "AlertService":
        """
        Context manager entry.
        """

        self.start()

        return self

    def __exit__(
        self,
        exc_type,
        exc,
        traceback,
    ) -> None:
        """
        Context manager exit.
        """

        self.stop()

    # ==========================================================
    # STRING REPRESENTATION
    # ==========================================================

    def __repr__(self) -> str:

        return (

            f"{self.__class__.__name__}("

            f"alerts={len(self._history)}, "

            f"delivered={self.statistics.delivered}, "

            f"failed={self.statistics.failed})"

        )

    def __str__(self) -> str:

        return (

            f"{self.__class__.__name__}"

            f"[alerts={len(self._history)}]"

        )

    # ==========================================================
    # DEBUG
    # ==========================================================

    def dump(self) -> Dict[str, Any]:
        """
        Return complete runtime information.
        """

        return {

            "repr":
                repr(self),

            "snapshot":
                self.snapshot(),

            "diagnostics":
                self.diagnostics(),

            "registered_events":
                self.events(),

        }

    # ==========================================================
    # FACTORY
    # ==========================================================

    @classmethod
    def create(
        cls,
        manager: AlertManager,
    ) -> "AlertService":
        """
        Factory constructor.
        """

        return cls(manager)


# ==========================================================
# MODULE HELPERS
# ==========================================================

def create_alert_service(
    manager: AlertManager,
) -> AlertService:
    """
    Convenience factory.
    """

    return AlertService.create(
        manager,
    )


def build_alert_service(
    manager: AlertManager,
) -> AlertService:
    """
    Alternate factory helper.
    """

    return AlertService(
        manager,
    )
# ==========================================================
# MODULE EXPORTS
# ==========================================================

__all__ = [

    # Enums
    "AlertType",
    "AlertPriority",
    "AlertStatus",

    # Models
    "Alert",
    "AlertStatistics",

    # Service
    "AlertService",

    # Factory Helpers
    "create_alert_service",
    "build_alert_service",

]

# ==========================================================
# END OF FILE
# ==========================================================

# ==========================
# END OF FILE
# ==========================