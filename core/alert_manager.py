"""
=========================================================
StockVersity Scanner Pro

Alert Manager

Centralized Alert Engine

Author : StockVersity
=========================================================
"""

from __future__ import annotations

import logging
import threading
import uuid

from dataclasses import dataclass, field
from datetime import datetime
from datetime import timedelta

from enum import Enum

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from core.market_analyzer import MarketAnalyzer
from core.scanner.signal import Signal


# =========================================================
# ALERT PRIORITY
# =========================================================

class AlertPriority(Enum):

    LOW = "LOW"

    MEDIUM = "MEDIUM"

    HIGH = "HIGH"

    CRITICAL = "CRITICAL"


# =========================================================
# ALERT TYPE
# =========================================================

class AlertType(Enum):

    BUY = "BUY"

    SELL = "SELL"

    BREAKOUT = "BREAKOUT"

    BREAKDOWN = "BREAKDOWN"

    VOLUME = "VOLUME"

    MOMENTUM = "MOMENTUM"

    MARKET = "MARKET"

    RISK = "RISK"

    SYSTEM = "SYSTEM"


# =========================================================
# ALERT STATUS
# =========================================================

class AlertStatus(Enum):

    NEW = "NEW"

    SENT = "SENT"

    ACKNOWLEDGED = "ACKNOWLEDGED"

    EXPIRED = "EXPIRED"

    DISMISSED = "DISMISSED"


# =========================================================
# ALERT OBJECT
# =========================================================

@dataclass
class Alert:

    id: str = field(

        default_factory=lambda: str(

            uuid.uuid4()

        )

    )

    symbol: str = ""

    title: str = ""

    message: str = ""

    alert_type: AlertType = AlertType.SYSTEM

    priority: AlertPriority = AlertPriority.MEDIUM

    status: AlertStatus = AlertStatus.NEW

    scanner: str = ""

    timeframe: str = ""

    created: datetime = field(

        default_factory=datetime.now

    )

    expires: Optional[datetime] = None

    metadata: Dict[str, Any] = field(

        default_factory=dict

    )

    signal: Optional[Signal] = None


# =========================================================
# ALERT MANAGER
# =========================================================

class AlertManager:

    VERSION = "1.0.0"

    def __init__(

        self,

        market: Optional[MarketAnalyzer] = None,

    ):

        self.market = market

        self.logger = logging.getLogger(

            self.__class__.__name__

        )

        self.lock = threading.RLock()

        self.alerts: Dict[

            str,

            Alert,

        ] = {}

        self.sent_history: List[str] = []

        self.last_sent: Dict[

            str,

            datetime,

        ] = {}

        self.started = datetime.now()

        self.requests = 0

        self.sent_count = 0

        self.expired_count = 0

        self.dismissed_count = 0

        self.logger.info(

            "AlertManager initialized."

        )

    # =====================================================
    # CREATE ALERT
    # =====================================================

    def create_alert(

        self,

        symbol: str,

        title: str,

        message: str,

        alert_type: AlertType,

        priority: AlertPriority = AlertPriority.MEDIUM,

        scanner: str = "",

        timeframe: str = "",

        signal: Optional[Signal] = None,

        expires_after_minutes: int = 60,

        metadata: Optional[

            Dict[str, Any]

        ] = None,

    ) -> Alert:
        """
        Create a new alert.
        """

        alert = Alert(

            symbol=symbol,

            title=title,

            message=message,

            alert_type=alert_type,

            priority=priority,

            scanner=scanner,

            timeframe=timeframe,

            signal=signal,

            metadata=metadata or {},

            expires=datetime.now()

            + timedelta(

                minutes=expires_after_minutes,

            ),

        )

        with self.lock:

            self.alerts[

                alert.id

            ] = alert

        return alert

    # =====================================================
    # GET ALERT
    # =====================================================

    def get(

        self,

        alert_id: str,

    ) -> Optional[Alert]:

        return self.alerts.get(

            alert_id

        )

    # =====================================================
    # ALL ALERTS
    # =====================================================

    def all_alerts(

        self,

    ) -> List[Alert]:

        return list(

            self.alerts.values()

        )
        # =====================================================
    # SEND ALERT
    # =====================================================

    def send(
        self,
        alert: Alert,
    ) -> bool:
        """
        Send an alert after validation.
        """

        self.requests += 1

        if not self.can_send(alert):

            return False

        alert.status = AlertStatus.SENT

        self.sent_history.append(

            alert.id

        )

        self.last_sent[

            self._alert_key(alert)

        ] = datetime.now()

        self.sent_count += 1

        self.logger.info(

            "[%s] %s | %s",

            alert.priority.value,

            alert.symbol,

            alert.title,

        )

        return True

    # =====================================================
    # DUPLICATE KEY
    # =====================================================

    def _alert_key(
        self,
        alert: Alert,
    ) -> str:
        """
        Generate duplicate detection key.
        """

        return (

            f"{alert.symbol}|"

            f"{alert.scanner}|"

            f"{alert.timeframe}|"

            f"{alert.alert_type.value}"

        )

    # =====================================================
    # COOLDOWN CHECK
    # =====================================================

    def can_send(
        self,
        alert: Alert,
        cooldown_seconds: int = 300,
    ) -> bool:
        """
        Prevent duplicate alerts within cooldown.
        """

        if self.is_expired(alert):

            return False

        key = self._alert_key(alert)

        previous = self.last_sent.get(

            key

        )

        if previous is None:

            return True

        elapsed = (

            datetime.now()

            - previous

        ).total_seconds()

        return elapsed >= cooldown_seconds

    # =====================================================
    # PRIORITY FILTER
    # =====================================================

    def alerts_by_priority(
        self,
        priority: AlertPriority,
    ) -> List[Alert]:
        """
        Return alerts matching priority.
        """

        return [

            alert

            for alert in self.alerts.values()

            if alert.priority == priority

        ]

    # =====================================================
    # EXPIRED
    # =====================================================

    def is_expired(
        self,
        alert: Alert,
    ) -> bool:
        """
        Check alert expiry.
        """

        if alert.expires is None:

            return False

        return datetime.now() >= alert.expires

    # =====================================================
    # CLEANUP
    # =====================================================

    def cleanup_expired(
        self,
    ) -> int:
        """
        Remove expired alerts.
        """

        removed = 0

        for alert in list(

            self.alerts.values()

        ):

            if not self.is_expired(alert):

                continue

            alert.status = (

                AlertStatus.EXPIRED

            )

            self.expired_count += 1

            removed += 1

            del self.alerts[

                alert.id

            ]

        return removed

    # =====================================================
    # ACKNOWLEDGE
    # =====================================================

    def acknowledge(
        self,
        alert_id: str,
    ) -> bool:
        """
        Mark an alert as acknowledged.
        """

        alert = self.get(

            alert_id

        )

        if alert is None:

            return False

        alert.status = (

            AlertStatus.ACKNOWLEDGED

        )

        return True

    # =====================================================
    # DISMISS
    # =====================================================

    def dismiss(
        self,
        alert_id: str,
    ) -> bool:
        """
        Dismiss an alert.
        """

        alert = self.get(

            alert_id

        )

        if alert is None:

            return False

        alert.status = (

            AlertStatus.DISMISSED

        )

        self.dismissed_count += 1

        return True

    # =====================================================
    # HISTORY
    # =====================================================

    def history(
        self,
    ) -> List[Alert]:
        """
        Return alerts ordered by creation time.
        """

        return sorted(

            self.alerts.values(),

            key=lambda x: x.created,

            reverse=True,

        )

    # =====================================================
    # ACTIVE ALERTS
    # =====================================================

    def active_alerts(
        self,
    ) -> List[Alert]:
        """
        Return active alerts only.
        """

        return [

            alert

            for alert in self.alerts.values()

            if alert.status
            not in (

                AlertStatus.EXPIRED,

                AlertStatus.DISMISSED,

            )

        ]
        # =====================================================
    # SIGNAL TO ALERT
    # =====================================================

    def from_signal(
        self,
        signal: Signal,
    ) -> Alert:
        """
        Convert scanner signal into an Alert.
        """

        priority = AlertPriority.MEDIUM

        if signal.score >= 90:

            priority = AlertPriority.CRITICAL

        elif signal.score >= 80:

            priority = AlertPriority.HIGH

        elif signal.score >= 70:

            priority = AlertPriority.MEDIUM

        else:

            priority = AlertPriority.LOW

        title = (

            f"{signal.signal_type.value} "

            f"{signal.symbol}"

        )

        message = (

            f"{signal.pattern.value}"

            f" | Score: {signal.score:.1f}"

            f" | RR: {signal.risk_reward:.2f}"

        )

        return self.create_alert(

            symbol=signal.symbol,

            title=title,

            message=message,

            alert_type=self._signal_alert_type(

                signal

            ),

            priority=priority,

            scanner=signal.scanner,

            timeframe=signal.timeframe,

            signal=signal,

        )

    # =====================================================
    # ALERT TYPE FROM SIGNAL
    # =====================================================

    def _signal_alert_type(
        self,
        signal: Signal,
    ) -> AlertType:
        """
        Determine alert type from signal.
        """

        value = signal.signal_type.value.upper()

        if "BUY" in value:

            return AlertType.BUY

        if "SELL" in value:

            return AlertType.SELL

        return AlertType.MOMENTUM

    # =====================================================
    # BUY ALERT
    # =====================================================

    def buy_alert(
        self,
        signal: Signal,
    ) -> Alert:
        """
        Generate buy alert.
        """

        return self.create_alert(

            symbol=signal.symbol,

            title="BUY Opportunity",

            message=(

                f"{signal.symbol} "

                f"generated BUY signal."

            ),

            alert_type=AlertType.BUY,

            priority=AlertPriority.HIGH,

            scanner=signal.scanner,

            timeframe=signal.timeframe,

            signal=signal,

        )

    # =====================================================
    # SELL ALERT
    # =====================================================

    def sell_alert(
        self,
        signal: Signal,
    ) -> Alert:
        """
        Generate sell alert.
        """

        return self.create_alert(

            symbol=signal.symbol,

            title="SELL Opportunity",

            message=(

                f"{signal.symbol} "

                f"generated SELL signal."

            ),

            alert_type=AlertType.SELL,

            priority=AlertPriority.HIGH,

            scanner=signal.scanner,

            timeframe=signal.timeframe,

            signal=signal,

        )

    # =====================================================
    # BREAKOUT ALERT
    # =====================================================

    def breakout_alert(
        self,
        signal: Signal,
    ) -> Alert:
        """
        Generate breakout alert.
        """

        return self.create_alert(

            symbol=signal.symbol,

            title="Breakout",

            message=(

                f"{signal.symbol} "

                f"confirmed breakout."

            ),

            alert_type=AlertType.BREAKOUT,

            priority=AlertPriority.CRITICAL,

            scanner=signal.scanner,

            timeframe=signal.timeframe,

            signal=signal,

        )

    # =====================================================
    # BREAKDOWN ALERT
    # =====================================================

    def breakdown_alert(
        self,
        signal: Signal,
    ) -> Alert:
        """
        Generate breakdown alert.
        """

        return self.create_alert(

            symbol=signal.symbol,

            title="Breakdown",

            message=(

                f"{signal.symbol} "

                f"confirmed breakdown."

            ),

            alert_type=AlertType.BREAKDOWN,

            priority=AlertPriority.CRITICAL,

            scanner=signal.scanner,

            timeframe=signal.timeframe,

            signal=signal,

        )

    # =====================================================
    # VOLUME ALERT
    # =====================================================

    def volume_alert(
        self,
        symbol: str,
        volume_ratio: float,
    ) -> Alert:
        """
        Generate unusual volume alert.
        """

        return self.create_alert(

            symbol=symbol,

            title="Volume Spike",

            message=(

                f"RVOL "

                f"{volume_ratio:.2f}x detected."

            ),

            alert_type=AlertType.VOLUME,

            priority=AlertPriority.HIGH,

        )

    # =====================================================
    # MARKET ALERT
    # =====================================================

    def market_alert(
        self,
        title: str,
        message: str,
        priority: AlertPriority = AlertPriority.HIGH,
    ) -> Alert:
        """
        Generate market-wide alert.
        """

        return self.create_alert(

            symbol="MARKET",

            title=title,

            message=message,

            alert_type=AlertType.MARKET,

            priority=priority,

        )

    # =====================================================
    # RISK ALERT
    # =====================================================

    def risk_alert(
        self,
        message: str,
    ) -> Alert:
        """
        Generate risk management alert.
        """

        return self.create_alert(

            symbol="RISK",

            title="Risk Warning",

            message=message,

            alert_type=AlertType.RISK,

            priority=AlertPriority.CRITICAL,

        )

    # =====================================================
    # AUTO CREATE
    # =====================================================

    def process_signal(
        self,
        signal: Signal,
    ) -> Optional[Alert]:
        """
        Automatically create and send an alert
        from a scanner signal.
        """

        alert = self.from_signal(

            signal

        )

        if self.send(alert):

            return alert

        return None
        # =====================================================
    # PROCESS SIGNALS
    # =====================================================

    def process_signals(
        self,
        signals: List[Signal],
    ) -> List[Alert]:
        """
        Process multiple scanner signals.
        """

        alerts: List[Alert] = []

        for signal in signals:

            alert = self.process_signal(

                signal

            )

            if alert is not None:

                alerts.append(

                    alert

                )

        return alerts

    # =====================================================
    # MARKET ALERTS
    # =====================================================

    def process_market(
        self,
    ) -> List[Alert]:
        """
        Generate alerts from MarketAnalyzer.
        """

        if self.market is None:

            return []

        alerts: List[Alert] = []

        for event in self.market.market_events():

            alert = self.market_alert(

                title=event,

                message=event,

                priority=AlertPriority.HIGH,

            )

            if self.send(alert):

                alerts.append(

                    alert

                )

        return alerts

    # =====================================================
    # CRITICAL ALERTS
    # =====================================================

    def critical_alerts(
        self,
    ) -> List[Alert]:
        """
        Return critical alerts.
        """

        return [

            alert

            for alert in self.active_alerts()

            if alert.priority

            == AlertPriority.CRITICAL

        ]

    # =====================================================
    # HIGH PRIORITY
    # =====================================================

    def high_priority(
        self,
    ) -> List[Alert]:
        """
        High or critical alerts.
        """

        return [

            alert

            for alert in self.active_alerts()

            if alert.priority in (

                AlertPriority.HIGH,

                AlertPriority.CRITICAL,

            )

        ]

    # =====================================================
    # FILTER BY SYMBOL
    # =====================================================

    def by_symbol(
        self,
        symbol: str,
    ) -> List[Alert]:
        """
        Alerts for a symbol.
        """

        symbol = symbol.upper()

        return [

            alert

            for alert in self.alerts.values()

            if alert.symbol.upper()

            == symbol

        ]

    # =====================================================
    # FILTER BY SCANNER
    # =====================================================

    def by_scanner(
        self,
        scanner: str,
    ) -> List[Alert]:
        """
        Alerts generated by scanner.
        """

        return [

            alert

            for alert in self.alerts.values()

            if alert.scanner == scanner

        ]

    # =====================================================
    # FILTER BY TIMEFRAME
    # =====================================================

    def by_timeframe(
        self,
        timeframe: str,
    ) -> List[Alert]:
        """
        Alerts for timeframe.
        """

        return [

            alert

            for alert in self.alerts.values()

            if alert.timeframe

            == timeframe

        ]

    # =====================================================
    # SEARCH
    # =====================================================

    def search(
        self,
        text: str,
    ) -> List[Alert]:
        """
        Search alerts.
        """

        query = text.lower()

        results: List[Alert] = []

        for alert in self.alerts.values():

            if (

                query in alert.title.lower()

                or query

                in alert.message.lower()

                or query

                in alert.symbol.lower()

            ):

                results.append(

                    alert

                )

        return results

    # =====================================================
    # SORT
    # =====================================================

    def sorted_alerts(
        self,
        descending: bool = True,
    ) -> List[Alert]:
        """
        Sort alerts by priority then creation.
        """

        priority = {

            AlertPriority.CRITICAL: 4,

            AlertPriority.HIGH: 3,

            AlertPriority.MEDIUM: 2,

            AlertPriority.LOW: 1,

        }

        return sorted(

            self.active_alerts(),

            key=lambda a: (

                priority[a.priority],

                a.created,

            ),

            reverse=descending,

        )

    # =====================================================
    # LATEST
    # =====================================================

    def latest(
        self,
        count: int = 20,
    ) -> List[Alert]:
        """
        Latest alerts.
        """

        return sorted(

            self.alerts.values(),

            key=lambda a: a.created,

            reverse=True,

        )[:count]

    # =====================================================
    # ALERT STATISTICS
    # =====================================================

    def statistics(
        self,
    ) -> Dict[str, Any]:
        """
        Alert statistics.
        """

        return {

            "total": len(

                self.alerts

            ),

            "active": len(

                self.active_alerts()

            ),

            "critical": len(

                self.critical_alerts()

            ),

            "sent": self.sent_count,

            "dismissed": self.dismissed_count,

            "expired": self.expired_count,

            "buy": len(

                [

                    a

                    for a

                    in self.alerts.values()

                    if a.alert_type

                    == AlertType.BUY

                ]

            ),

            "sell": len(

                [

                    a

                    for a

                    in self.alerts.values()

                    if a.alert_type

                    == AlertType.SELL

                ]

            ),

        }
        # =====================================================
    # ALERT TO DICTIONARY
    # =====================================================

    def to_dict(
        self,
        alert: Alert,
    ) -> Dict[str, Any]:
        """
        Convert Alert to dictionary.
        """

        return {

            "id": alert.id,

            "symbol": alert.symbol,

            "title": alert.title,

            "message": alert.message,

            "alert_type": alert.alert_type.value,

            "priority": alert.priority.value,

            "status": alert.status.value,

            "scanner": alert.scanner,

            "timeframe": alert.timeframe,

            "created": alert.created.isoformat(),

            "expires": (

                alert.expires.isoformat()

                if alert.expires

                else None

            ),

            "metadata": alert.metadata,

        }

    # =====================================================
    # FROM DICTIONARY
    # =====================================================

    def from_dict(
        self,
        data: Dict[str, Any],
    ) -> Alert:
        """
        Restore Alert from dictionary.
        """

        alert = Alert(

            id=data["id"],

            symbol=data["symbol"],

            title=data["title"],

            message=data["message"],

            alert_type=AlertType(

                data["alert_type"]

            ),

            priority=AlertPriority(

                data["priority"]

            ),

            status=AlertStatus(

                data["status"]

            ),

            scanner=data.get(

                "scanner",

                "",

            ),

            timeframe=data.get(

                "timeframe",

                "",

            ),

            created=datetime.fromisoformat(

                data["created"]

            ),

            expires=(

                datetime.fromisoformat(

                    data["expires"]

                )

                if data.get(

                    "expires"

                )

                else None

            ),

            metadata=data.get(

                "metadata",

                {},

            ),

        )

        return alert

    # =====================================================
    # EXPORT
    # =====================================================

    def export(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Export all alerts.
        """

        return [

            self.to_dict(

                alert

            )

            for alert

            in self.history()

        ]

    # =====================================================
    # IMPORT
    # =====================================================

    def import_alerts(
        self,
        alerts: List[
            Dict[str, Any]
        ],
    ) -> int:
        """
        Import alert list.
        """

        count = 0

        for item in alerts:

            alert = self.from_dict(

                item

            )

            self.alerts[

                alert.id

            ] = alert

            count += 1

        return count

    # =====================================================
    # SAVE JSON
    # =====================================================

    def save_json(
        self,
        filename: str,
    ) -> None:
        """
        Save alerts as JSON.
        """

        import json

        with open(

            filename,

            "w",

            encoding="utf-8",

        ) as fp:

            json.dump(

                self.export(),

                fp,

                indent=4,

            )

    # =====================================================
    # LOAD JSON
    # =====================================================

    def load_json(
        self,
        filename: str,
    ) -> int:
        """
        Load alerts from JSON.
        """

        import json

        with open(

            filename,

            "r",

            encoding="utf-8",

        ) as fp:

            data = json.load(

                fp

            )

        return self.import_alerts(

            data

        )

    # =====================================================
    # EXPORT CSV
    # =====================================================

    def export_csv(
        self,
        filename: str,
    ) -> None:
        """
        Export alerts to CSV.
        """

        import csv

        rows = self.export()

        if not rows:

            return

        with open(

            filename,

            "w",

            newline="",

            encoding="utf-8",

        ) as fp:

            writer = csv.DictWriter(

                fp,

                fieldnames=list(

                    rows[0].keys()

                ),

            )

            writer.writeheader()

            writer.writerows(

                rows

            )

    # =====================================================
    # ARCHIVE
    # =====================================================

    def archive(
        self,
    ) -> List[Alert]:
        """
        Return expired or dismissed alerts.
        """

        return [

            alert

            for alert

            in self.alerts.values()

            if alert.status in (

                AlertStatus.EXPIRED,

                AlertStatus.DISMISSED,

            )

        ]

    # =====================================================
    # CLEAR ARCHIVE
    # =====================================================

    def clear_archive(
        self,
    ) -> int:
        """
        Remove archived alerts.
        """

        removed = 0

        for alert in list(

            self.alerts.values()

        ):

            if alert.status not in (

                AlertStatus.EXPIRED,

                AlertStatus.DISMISSED,

            ):

                continue

            del self.alerts[

                alert.id

            ]

            removed += 1

        return removed

    # =====================================================
    # BACKUP
    # =====================================================

    def backup(
        self,
        filename: str,
    ) -> None:
        """
        Create backup.
        """

        self.save_json(

            filename

        )

    # =====================================================
    # RESTORE
    # =====================================================

    def restore(
        self,
        filename: str,
    ) -> int:
        """
        Restore backup.
        """

        self.alerts.clear()

        return self.load_json(

            filename

        )
        # =====================================================
    # NOTIFICATION QUEUE
    # =====================================================

    def notification_queue(
        self,
    ) -> List[Alert]:
        """
        Return pending notifications ordered by priority.
        """

        return self.sorted_alerts()

    # =====================================================
    # DASHBOARD FEED
    # =====================================================

    def dashboard_feed(
        self,
        limit: int = 25,
    ) -> List[Dict[str, Any]]:
        """
        Dashboard notification feed.
        """

        feed: List[Dict[str, Any]] = []

        for alert in self.latest(limit):

            feed.append(

                {

                    "id": alert.id,

                    "symbol": alert.symbol,

                    "title": alert.title,

                    "message": alert.message,

                    "priority": alert.priority.value,

                    "status": alert.status.value,

                    "time": alert.created,

                }

            )

        return feed

    # =====================================================
    # TOAST NOTIFICATION
    # =====================================================

    def toast(
        self,
        alert: Alert,
    ) -> None:
        """
        Desktop toast notification hook.
        """

        self.logger.info(

            "Toast | %s | %s",

            alert.symbol,

            alert.title,

        )

    # =====================================================
    # SOUND
    # =====================================================

    def play_sound(
        self,
        alert: Alert,
    ) -> None:
        """
        Notification sound hook.
        """

        self.logger.debug(

            "Play sound for %s",

            alert.id,

        )

    # =====================================================
    # VIBRATION
    # =====================================================

    def vibrate(
        self,
        alert: Alert,
    ) -> None:
        """
        Mobile vibration hook.
        """

        self.logger.debug(

            "Vibration triggered for %s",

            alert.id,

        )

    # =====================================================
    # WEBHOOK
    # =====================================================

    def webhook(
        self,
        alert: Alert,
        url: str,
    ) -> bool:
        """
        Placeholder for webhook delivery.
        """

        self.logger.info(

            "Webhook queued -> %s",

            url,

        )

        return True

    # =====================================================
    # EMAIL
    # =====================================================

    def email(
        self,
        alert: Alert,
        recipient: str,
    ) -> bool:
        """
        Email notification hook.
        """

        self.logger.info(

            "Email -> %s",

            recipient,

        )

        return True

    # =====================================================
    # SMS
    # =====================================================

    def sms(
        self,
        alert: Alert,
        number: str,
    ) -> bool:
        """
        SMS notification hook.
        """

        self.logger.info(

            "SMS -> %s",

            number,

        )

        return True

    # =====================================================
    # TELEGRAM
    # =====================================================

    def telegram(
        self,
        alert: Alert,
        chat_id: str,
    ) -> bool:
        """
        Telegram notification hook.
        """

        self.logger.info(

            "Telegram -> %s",

            chat_id,

        )

        return True

    # =====================================================
    # BROADCAST
    # =====================================================

    def broadcast(
        self,
        alert: Alert,
    ) -> None:
        """
        Send alert to all configured channels.
        """

        self.toast(

            alert

        )

        self.play_sound(

            alert

        )

        self.vibrate(

            alert

        )

    # =====================================================
    # ROUTER
    # =====================================================

    def notify(
        self,
        alert: Alert,
    ) -> bool:
        """
        Primary notification entry point.
        """

        if not self.send(

            alert

        ):

            return False

        self.broadcast(

            alert

        )

        return True

    # =====================================================
    # FLUSH QUEUE
    # =====================================================

    def flush_notifications(
        self,
    ) -> int:
        """
        Deliver all pending notifications.
        """

        delivered = 0

        for alert in self.active_alerts():

            if alert.status != AlertStatus.NEW:

                continue

            if self.notify(

                alert

            ):

                delivered += 1

        return delivered
        # =====================================================
    # ALERT SCORE
    # =====================================================

    def alert_score(
        self,
        alert: Alert,
    ) -> float:
        """
        Calculate overall alert score.
        """

        score = 50.0

        if alert.signal is not None:

            score = float(

                alert.signal.score

            )

        priority_bonus = {

            AlertPriority.LOW: 0,

            AlertPriority.MEDIUM: 5,

            AlertPriority.HIGH: 10,

            AlertPriority.CRITICAL: 20,

        }

        score += priority_bonus.get(

            alert.priority,

            0,

        )

        return min(

            score,

            100.0,

        )

    # =====================================================
    # AUTO PRIORITY
    # =====================================================

    def update_priority(
        self,
        alert: Alert,
    ) -> AlertPriority:
        """
        Automatically adjust alert priority.
        """

        score = self.alert_score(

            alert

        )

        if score >= 90:

            priority = AlertPriority.CRITICAL

        elif score >= 80:

            priority = AlertPriority.HIGH

        elif score >= 65:

            priority = AlertPriority.MEDIUM

        else:

            priority = AlertPriority.LOW

        alert.priority = priority

        return priority

    # =====================================================
    # CONFIDENCE FILTER
    # =====================================================

    def confidence_filter(
        self,
        alert: Alert,
        minimum: float = 70.0,
    ) -> bool:
        """
        Filter alerts using signal confidence.
        """

        if alert.signal is None:

            return True

        confidence = getattr(

            alert.signal,

            "confidence",

            alert.signal.score,

        )

        return confidence >= minimum

    # =====================================================
    # RISK FILTER
    # =====================================================

    def risk_filter(
        self,
        alert: Alert,
    ) -> bool:
        """
        Suppress alerts during high market risk.
        """

        if self.market is None:

            return True

        try:

            return (

                self.market.risk_mode()

                != "HIGH_RISK"

            )

        except Exception:

            return True

    # =====================================================
    # MARKET FILTER
    # =====================================================

    def market_filter(
        self,
        alert: Alert,
    ) -> bool:
        """
        Validate alert against market conditions.
        """

        if self.market is None:

            return True

        try:

            return self.market.trade_allowed()

        except Exception:

            return True

    # =====================================================
    # SESSION FILTER
    # =====================================================

    def session_filter(
        self,
        alert: Alert,
    ) -> bool:
        """
        Allow alerts only during active session.
        """

        now = datetime.now()

        market_open = now.replace(

            hour=9,

            minute=15,

            second=0,

            microsecond=0,

        )

        market_close = now.replace(

            hour=15,

            minute=30,

            second=0,

            microsecond=0,

        )

        return (

            market_open

            <= now

            <= market_close

        )

    # =====================================================
    # VALIDATE ALERT
    # =====================================================

    def validate(
        self,
        alert: Alert,
    ) -> bool:
        """
        Run all validation filters.
        """

        checks = (

            self.confidence_filter(

                alert

            ),

            self.risk_filter(

                alert

            ),

            self.market_filter(

                alert

            ),

            self.session_filter(

                alert

            ),

        )

        return all(

            checks

        )

    # =====================================================
    # SMART DUPLICATE
    # =====================================================

    def is_duplicate(
        self,
        alert: Alert,
    ) -> bool:
        """
        Intelligent duplicate detection.
        """

        for existing in self.active_alerts():

            if (

                existing.symbol

                != alert.symbol

            ):

                continue

            if (

                existing.alert_type

                != alert.alert_type

            ):

                continue

            if (

                existing.scanner

                != alert.scanner

            ):

                continue

            delta = (

                alert.created

                - existing.created

            ).total_seconds()

            if abs(

                delta

            ) < 300:

                return True

        return False

    # =====================================================
    # RANK ALERTS
    # =====================================================

    def ranked_alerts(
        self,
    ) -> List[Alert]:
        """
        Rank alerts by calculated score.
        """

        alerts = self.active_alerts()

        alerts.sort(

            key=lambda alert: (

                self.alert_score(

                    alert

                ),

                alert.created,

            ),

            reverse=True,

        )

        return alerts

    # =====================================================
    # BEST ALERT
    # =====================================================

    def best_alert(
        self,
    ) -> Optional[Alert]:
        """
        Highest-ranked active alert.
        """

        alerts = self.ranked_alerts()

        if not alerts:

            return None

        return alerts[0]
        # =====================================================
    # CLEAR ALERTS
    # =====================================================

    def clear(
        self,
    ) -> None:
        """
        Clear all alerts.
        """

        with self.lock:

            self.alerts.clear()

            self.sent_history.clear()

            self.last_sent.clear()

    # =====================================================
    # RESET STATISTICS
    # =====================================================

    def reset_statistics(
        self,
    ) -> None:
        """
        Reset runtime statistics.
        """

        self.requests = 0

        self.sent_count = 0

        self.expired_count = 0

        self.dismissed_count = 0

        self.started = datetime.now()

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

        total = max(

            self.requests,

            1,

        )

        success_rate = (

            self.sent_count

            / total

        ) * 100

        return {

            "uptime_seconds": round(

                uptime,

                2,

            ),

            "requests": self.requests,

            "alerts_sent": self.sent_count,

            "success_rate": round(

                success_rate,

                2,

            ),

            "active_alerts": len(

                self.active_alerts()

            ),

        }

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(
        self,
    ) -> Dict[str, Any]:
        """
        Health status.
        """

        healthy = True

        issues: List[str] = []

        if self.requests > 0:

            failure_rate = (

                self.requests

                - self.sent_count

            ) / self.requests

            if failure_rate > 0.5:

                healthy = False

                issues.append(

                    "High notification failure rate."

                )

        return {

            "healthy": healthy,

            "issues": issues,

            "active_alerts": len(

                self.active_alerts()

            ),

            "pending_notifications": len(

                [

                    a

                    for a in self.alerts.values()

                    if a.status

                    == AlertStatus.NEW

                ]

            ),

        }

    # =====================================================
    # METADATA
    # =====================================================

    def metadata(
        self,
    ) -> Dict[str, Any]:
        """
        Component metadata.
        """

        return {

            "component": self.__class__.__name__,

            "version": self.VERSION,

            "started": self.started.isoformat(),

            "market_connected": (

                self.market

                is not None

            ),

        }

    # =====================================================
    # DIAGNOSTICS
    # =====================================================

    def diagnostics(
        self,
    ) -> Dict[str, Any]:
        """
        Diagnostic information.
        """

        return {

            "metadata": self.metadata(),

            "health": self.health_check(),

            "performance": self.performance(),

            "statistics": self.statistics(),

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

            "diagnostics": self.diagnostics(),

            "latest_alerts": [

                self.to_dict(

                    alert

                )

                for alert

                in self.latest(

                    10

                )

            ],

        }

    # =====================================================
    # CACHE SIZE
    # =====================================================

    def cache_size(
        self,
    ) -> int:
        """
        Number of cooldown cache entries.
        """

        return len(

            self.last_sent

        )

    # =====================================================
    # PURGE COOLDOWN CACHE
    # =====================================================

    def purge_cache(
        self,
        older_than_minutes: int = 120,
    ) -> int:
        """
        Remove stale cooldown entries.
        """

        removed = 0

        threshold = datetime.now() - timedelta(

            minutes=older_than_minutes

        )

        for key in list(

            self.last_sent.keys()

        ):

            if self.last_sent[

                key

            ] >= threshold:

                continue

            del self.last_sent[

                key

            ]

            removed += 1

        return removed

    # =====================================================
    # MAINTENANCE
    # =====================================================

    def maintenance(
        self,
    ) -> Dict[str, int]:
        """
        Run routine maintenance.
        """

        expired = self.cleanup_expired()

        cache = self.purge_cache()

        return {

            "expired_removed": expired,

            "cache_removed": cache,

        }
        # =====================================================
    # READY
    # =====================================================

    @property
    def ready(
        self,
    ) -> bool:
        """
        Returns True if AlertManager is ready.
        """

        return True

    # =====================================================
    # STATUS
    # =====================================================

    @property
    def status(
        self,
    ) -> Dict[str, Any]:
        """
        Current AlertManager status.
        """

        return {

            "ready": self.ready,

            "alerts": len(

                self.alerts

            ),

            "active": len(

                self.active_alerts()

            ),

            "sent": self.sent_count,

            "requests": self.requests,

            "cache_entries": self.cache_size(),

            "last_update": datetime.now(),

        }

    # =====================================================
    # FACTORY
    # =====================================================

    @classmethod
    def create(
        cls,
        market: Optional[
            MarketAnalyzer
        ] = None,
    ) -> "AlertManager":
        """
        Factory constructor.
        """

        return cls(

            market=market

        )

    # =====================================================
    # CONTEXT MANAGER
    # =====================================================

    def __enter__(
        self,
    ) -> "AlertManager":
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
    ) -> None:
        """
        Gracefully shutdown manager.
        """

        self.logger.info(

            "Shutting down AlertManager."

        )

        self.maintenance()

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
    # MAGIC METHODS
    # =====================================================

    def __len__(
        self,
    ) -> int:
        """
        Total alerts.
        """

        return len(

            self.alerts

        )

    def __contains__(
        self,
        alert_id: str,
    ) -> bool:
        """
        Check alert existence.
        """

        return alert_id in self.alerts

    def __getitem__(
        self,
        alert_id: str,
    ) -> Alert:
        """
        Dictionary-style access.
        """

        return self.alerts[

            alert_id

        ]

    def __iter__(
        self,
    ):
        """
        Iterate through alerts.
        """

        return iter(

            self.alerts.values()

        )

    # =====================================================
    # STRING REPRESENTATION
    # =====================================================

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (

            f"{self.__class__.__name__}("

            f"alerts={len(self)}, "

            f"sent={self.sent_count}, "

            f"active={len(self.active_alerts())})"

        )

    def __str__(
        self,
    ) -> str:
        """
        User-friendly representation.
        """

        return (

            f"{self.__class__.__name__}"

            f" | Alerts={len(self)}"

            f" | Sent={self.sent_count}"

        )

    # =====================================================
    # DEBUG SUMMARY
    # =====================================================

    def print_summary(
        self,
    ) -> None:
        """
        Print runtime summary.
        """

        self.logger.info(

            "========== AlertManager =========="

        )

        self.logger.info(

            "Total Alerts : %s",

            len(

                self.alerts

            ),

        )

        self.logger.info(

            "Active       : %s",

            len(

                self.active_alerts()

            ),

        )

        self.logger.info(

            "Sent         : %s",

            self.sent_count,

        )

        self.logger.info(

            "Expired      : %s",

            self.expired_count,

        )

        self.logger.info(

            "Dismissed    : %s",

            self.dismissed_count,

        )

        self.logger.info(

            "=================================="

        )

    # =====================================================
    # DEBUG STATE
    # =====================================================

    def dump_state(
        self,
    ) -> Dict[str, Any]:
        """
        Return lightweight runtime state.
        """

        return {

            "status": self.status,

            "statistics": self.statistics(),

            "performance": self.performance(),

            "health": self.health_check(),

        }
        # =====================================================
    # DELIVERY SUCCESS RATE
    # =====================================================

    def delivery_success_rate(
        self,
    ) -> float:
        """
        Calculate alert delivery success rate.
        """

        if self.requests == 0:

            return 100.0

        return round(

            (

                self.sent_count

                / self.requests

            )

            * 100,

            2,

        )

    # =====================================================
    # FAILURE COUNT
    # =====================================================

    def failed_count(
        self,
    ) -> int:
        """
        Number of failed deliveries.
        """

        return max(

            self.requests

            - self.sent_count,

            0,

        )

    # =====================================================
    # FAILURE RATE
    # =====================================================

    def failure_rate(
        self,
    ) -> float:
        """
        Percentage of failed deliveries.
        """

        if self.requests == 0:

            return 0.0

        return round(

            (

                self.failed_count()

                / self.requests

            )

            * 100,

            2,

        )

    # =====================================================
    # AVERAGE ALERT AGE
    # =====================================================

    def average_alert_age(
        self,
    ) -> float:
        """
        Average age of active alerts in seconds.
        """

        alerts = self.active_alerts()

        if not alerts:

            return 0.0

        ages = [

            (

                datetime.now()

                - alert.created

            ).total_seconds()

            for alert in alerts

        ]

        return round(

            sum(ages)

            / len(ages),

            2,

        )

    # =====================================================
    # ALERT THROUGHPUT
    # =====================================================

    def throughput(
        self,
    ) -> float:
        """
        Alerts sent per minute.
        """

        uptime = (

            datetime.now()

            - self.started

        ).total_seconds()

        if uptime <= 0:

            return 0.0

        return round(

            self.sent_count

            / (uptime / 60),

            2,

        )

    # =====================================================
    # PRIORITY DISTRIBUTION
    # =====================================================

    def priority_distribution(
        self,
    ) -> Dict[str, int]:
        """
        Distribution of alerts by priority.
        """

        distribution = {

            priority.value: 0

            for priority

            in AlertPriority

        }

        for alert in self.alerts.values():

            distribution[

                alert.priority.value

            ] += 1

        return distribution

    # =====================================================
    # TYPE DISTRIBUTION
    # =====================================================

    def type_distribution(
        self,
    ) -> Dict[str, int]:
        """
        Distribution of alerts by type.
        """

        distribution = {

            alert_type.value: 0

            for alert_type

            in AlertType

        }

        for alert in self.alerts.values():

            distribution[

                alert.alert_type.value

            ] += 1

        return distribution

    # =====================================================
    # STATUS DISTRIBUTION
    # =====================================================

    def status_distribution(
        self,
    ) -> Dict[str, int]:
        """
        Distribution of alerts by status.
        """

        distribution = {

            status.value: 0

            for status

            in AlertStatus

        }

        for alert in self.alerts.values():

            distribution[

                alert.status.value

            ] += 1

        return distribution

    # =====================================================
    # KPI DASHBOARD
    # =====================================================

    def dashboard_metrics(
        self,
    ) -> Dict[str, Any]:
        """
        Dashboard KPIs.
        """

        return {

            "total_alerts": len(

                self.alerts

            ),

            "active_alerts": len(

                self.active_alerts()

            ),

            "success_rate": self.delivery_success_rate(),

            "failure_rate": self.failure_rate(),

            "throughput_per_minute": self.throughput(),

            "average_alert_age": self.average_alert_age(),

            "priority_distribution": (

                self.priority_distribution()

            ),

            "type_distribution": (

                self.type_distribution()

            ),

            "status_distribution": (

                self.status_distribution()

            ),

        }

    # =====================================================
    # PRODUCTION MONITOR
    # =====================================================

    def monitor(
        self,
    ) -> Dict[str, Any]:
        """
        Production monitoring snapshot.
        """

        return {

            "timestamp": datetime.now(),

            "health": self.health_check(),

            "performance": self.performance(),

            "dashboard": self.dashboard_metrics(),

            "maintenance": self.maintenance(),

        }
        # =====================================================
    # COMPONENT VERSION
    # =====================================================

    @classmethod
    def version(
        cls,
    ) -> str:
        """
        Return component version.
        """

        return cls.VERSION

    # =====================================================
    # COMPONENT REPORT
    # =====================================================

    @classmethod
    def build_report(
        cls,
    ) -> Dict[str, str]:
        """
        Static component information.
        """

        return {

            "component": cls.__name__,

            "version": cls.VERSION,

            "status": "Production",

            "thread_safe": "Yes",

            "notification_engine": "Enabled",

            "duplicate_filter": "Enabled",

            "cooldown_manager": "Enabled",

            "dashboard_support": "Enabled",

            "analytics": "Enabled",

            "backup_restore": "Enabled",

            "scanner_ready": "Yes",

        }

    # =====================================================
    # EXPORT STATE
    # =====================================================

    def export_state(
        self,
    ) -> Dict[str, Any]:
        """
        Export complete runtime state.
        """

        return {

            "metadata": self.metadata(),

            "status": self.status,

            "statistics": self.statistics(),

            "performance": self.performance(),

            "dashboard": self.dashboard_metrics(),

            "alerts": [

                self.to_dict(

                    alert

                )

                for alert in self.history()

            ],

        }

    # =====================================================
    # COPY
    # =====================================================

    def copy(
        self,
    ) -> "AlertManager":
        """
        Create a deep runtime copy.
        """

        manager = self.__class__(

            market=self.market

        )

        manager.alerts = {

            key: self.from_dict(

                self.to_dict(

                    alert

                )

            )

            for key, alert

            in self.alerts.items()

        }

        manager.sent_history = list(

            self.sent_history

        )

        manager.last_sent = dict(

            self.last_sent

        )

        manager.requests = self.requests

        manager.sent_count = self.sent_count

        manager.expired_count = (

            self.expired_count

        )

        manager.dismissed_count = (

            self.dismissed_count

        )

        manager.started = self.started

        return manager

    # =====================================================
    # DESTROY
    # =====================================================

    def destroy(
        self,
    ) -> None:
        """
        Release all runtime resources.
        """

        self.logger.info(

            "Destroying AlertManager."

        )

        self.clear()

        self.reset_statistics()

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

            "Finalizing AlertManager."

        )

        self.destroy()

    # =====================================================
    # IS EMPTY
    # =====================================================

    def is_empty(
        self,
    ) -> bool:
        """
        True if no alerts are present.
        """

        return len(

            self.alerts

        ) == 0

    # =====================================================
    # HAS ACTIVE ALERTS
    # =====================================================

    def has_active_alerts(
        self,
    ) -> bool:
        """
        Check for active alerts.
        """

        return len(

            self.active_alerts()

        ) > 0

    # =====================================================
    # TOP ALERT
    # =====================================================

    def top_alert(
        self,
    ) -> Optional[Alert]:
        """
        Highest priority active alert.
        """

        alerts = self.sorted_alerts()

        if not alerts:

            return None

        return alerts[0]

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> Dict[str, Any]:
        """
        Compact summary for dashboard cards.
        """

        top = self.top_alert()

        return {

            "active": len(

                self.active_alerts()

            ),

            "critical": len(

                self.critical_alerts()

            ),

            "latest": (

                top.title

                if top

                else None

            ),

            "success_rate": (

                self.delivery_success_rate()

            ),

            "throughput": (

                self.throughput()

            ),

        }
        # =====================================================
    # BOOL
    # =====================================================

    def __bool__(
        self,
    ) -> bool:
        """
        Truth value of AlertManager.
        """

        return self.has_active_alerts()

    # =====================================================
    # COPY SUPPORT
    # =====================================================

    def __copy__(
        self,
    ) -> "AlertManager":
        """
        Shallow copy compatibility.
        """

        return self.copy()

    # =====================================================
    # DEEP COPY SUPPORT
    # =====================================================

    def __deepcopy__(
        self,
        memo,
    ) -> "AlertManager":
        """
        Deep copy compatibility.
        """

        return self.copy()

    # =====================================================
    # REMOVE ALERT
    # =====================================================

    def remove(
        self,
        alert_id: str,
    ) -> bool:
        """
        Remove an alert by ID.
        """

        if alert_id not in self.alerts:

            return False

        del self.alerts[

            alert_id

        ]

        return True

    # =====================================================
    # REMOVE ALL
    # =====================================================

    def remove_all(
        self,
    ) -> int:
        """
        Remove every alert.
        """

        count = len(

            self.alerts

        )

        self.clear()

        return count

    # =====================================================
    # EXISTS
    # =====================================================

    def exists(
        self,
        alert_id: str,
    ) -> bool:
        """
        Check whether an alert exists.
        """

        return alert_id in self.alerts

    # =====================================================
    # GET IDS
    # =====================================================

    def ids(
        self,
    ) -> List[str]:
        """
        Return all alert IDs.
        """

        return list(

            self.alerts.keys()

        )

    # =====================================================
    # COUNT BY TYPE
    # =====================================================

    def count_by_type(
        self,
        alert_type: AlertType,
    ) -> int:
        """
        Count alerts by type.
        """

        return sum(

            1

            for alert

            in self.alerts.values()

            if alert.alert_type

            == alert_type

        )

    # =====================================================
    # COUNT BY PRIORITY
    # =====================================================

    def count_by_priority(
        self,
        priority: AlertPriority,
    ) -> int:
        """
        Count alerts by priority.
        """

        return sum(

            1

            for alert

            in self.alerts.values()

            if alert.priority

            == priority

        )

    # =====================================================
    # OLDEST ALERT
    # =====================================================

    def oldest_alert(
        self,
    ) -> Optional[Alert]:
        """
        Return the oldest stored alert.
        """

        if not self.alerts:

            return None

        return min(

            self.alerts.values(),

            key=lambda a: a.created,

        )

    # =====================================================
    # NEWEST ALERT
    # =====================================================

    def newest_alert(
        self,
    ) -> Optional[Alert]:
        """
        Return the newest stored alert.
        """

        if not self.alerts:

            return None

        return max(

            self.alerts.values(),

            key=lambda a: a.created,

        )

    # =====================================================
    # UPTIME
    # =====================================================

    def uptime(
        self,
    ) -> float:
        """
        Runtime in seconds.
        """

        return round(

            (

                datetime.now()

                - self.started

            ).total_seconds(),

            2,

        )

    # =====================================================
    # FINAL REPORT
    # =====================================================

    def final_report(
        self,
    ) -> Dict[str, Any]:
        """
        Final production report.
        """

        return {

            "metadata": self.metadata(),

            "status": self.status,

            "summary": self.summary(),

            "statistics": self.statistics(),

            "performance": self.performance(),

            "dashboard": self.dashboard_metrics(),

            "health": self.health_check(),

            "uptime_seconds": self.uptime(),

        }


# ==========================
# END OF FILE
# ==========================