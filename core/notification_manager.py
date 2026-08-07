from __future__ import annotations

import threading
import uuid

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Deque, Dict, List, Optional


# =====================================================
# PRIORITY
# =====================================================

class NotificationPriority(str, Enum):

    LOW = "low"

    NORMAL = "normal"

    HIGH = "high"

    CRITICAL = "critical"


# =====================================================
# TYPE
# =====================================================

class NotificationType(str, Enum):

    INFO = "info"

    SUCCESS = "success"

    WARNING = "warning"

    ERROR = "error"


# =====================================================
# NOTIFICATION
# =====================================================

@dataclass(slots=True)
class Notification:

    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    title: str = ""

    message: str = ""

    type: NotificationType = NotificationType.INFO

    priority: NotificationPriority = (
        NotificationPriority.NORMAL
    )

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    read: bool = False

    dismissed: bool = False

    metadata: Dict = field(
        default_factory=dict
    )


# =====================================================
# NOTIFICATION MANAGER
# =====================================================

class NotificationManager:

    _instance = None

    _lock = threading.Lock()

    # -------------------------------------------------

    def __new__(cls):

        with cls._lock:

            if cls._instance is None:

                cls._instance = super().__new__(cls)

        return cls._instance

    # -------------------------------------------------

    def __init__(self):

        if getattr(self, "_initialized", False):

            return

        self._initialized = True

        self.manager_lock = threading.RLock()

        self.queue: Deque[Notification] = deque()

        self.history: List[Notification] = []

        self.listeners: List[
            Callable[[Notification], None]
        ] = []

        self.max_history = 1000

    # =====================================================
    # CREATE
    # =====================================================

    def notify(

        self,

        title: str,

        message: str,

        type: NotificationType = NotificationType.INFO,

        priority: NotificationPriority = (
            NotificationPriority.NORMAL
        ),

        **metadata,

    ):

        notification = Notification(

            title=title,

            message=message,

            type=type,

            priority=priority,

            metadata=metadata,

        )

        self.queue.append(

            notification

        )

        self.history.append(

            notification

        )

        while len(self.history) > self.max_history:

            self.history.pop(

                0

            )

        self._emit(

            notification

        )

        return notification

    # =====================================================
    # LISTENERS
    # =====================================================

    def subscribe(

        self,

        callback: Callable[[Notification], None],

    ):

        if callback not in self.listeners:

            self.listeners.append(

                callback

            )

    # -------------------------------------------------

    def unsubscribe(

        self,

        callback,

    ):

        if callback in self.listeners:

            self.listeners.remove(

                callback

            )

    # =====================================================
    # EMIT
    # =====================================================

    def _emit(

        self,

        notification: Notification,

    ):

        for callback in list(

            self.listeners

        ):

            try:

                callback(

                    notification

                )

            except Exception:

                pass

    # =====================================================
    # POP QUEUE
    # =====================================================

    def next(

        self,

    ):

        if not self.queue:

            return None

        return self.queue.popleft()
        # =====================================================
    # DESKTOP NOTIFICATION
    # =====================================================

    def desktop(

        self,

        title: str,

        message: str,

    ):

        """
        Placeholder desktop notification.

        Integrate with:
        - QSystemTrayIcon (PySide6)
        - win10toast
        - plyer.notification
        """

        return self.notify(

            title=title,

            message=message,

            type=NotificationType.INFO,

        )

    # =====================================================
    # TOAST
    # =====================================================

    def toast(

        self,

        title: str,

        message: str,

        duration: int = 5,

    ):

        return self.notify(

            title=title,

            message=message,

            type=NotificationType.INFO,

            duration=duration,

        )

    # =====================================================
    # IN-APP
    # =====================================================

    def in_app(

        self,

        title: str,

        message: str,

        priority: NotificationPriority = (
            NotificationPriority.NORMAL
        ),

    ):

        return self.notify(

            title=title,

            message=message,

            priority=priority,

        )

    # =====================================================
    # EMAIL
    # =====================================================

    def email(

        self,

        to: str,

        subject: str,

        body: str,

    ):

        """
        Placeholder.

        Integrate SMTP or SendGrid
        here when required.
        """

        return {

            "success": False,

            "reason": "Email provider not configured.",

            "recipient": to,

            "subject": subject,

        }

    # =====================================================
    # MARK READ
    # =====================================================

    def mark_read(

        self,

        notification_id: str,

    ):

        for notification in self.history:

            if notification.id == notification_id:

                notification.read = True

                return True

        return False

    # =====================================================
    # MARK UNREAD
    # =====================================================

    def mark_unread(

        self,

        notification_id: str,

    ):

        for notification in self.history:

            if notification.id == notification_id:

                notification.read = False

                return True

        return False

    # =====================================================
    # DISMISS
    # =====================================================

    def dismiss(

        self,

        notification_id: str,

    ):

        for notification in self.history:

            if notification.id == notification_id:

                notification.dismissed = True

                return True

        return False

    # =====================================================
    # CLEAR QUEUE
    # =====================================================

    def clear_queue(

        self,

    ):

        count = len(

            self.queue

        )

        self.queue.clear()

        return count

    # =====================================================
    # CLEAR HISTORY
    # =====================================================

    def clear_history(

        self,

    ):

        count = len(

            self.history

        )

        self.history.clear()

        return count

    # =====================================================
    # UNREAD
    # =====================================================

    def unread(

        self,

    ):

        return [

            notification

            for notification in self.history

            if not notification.read

        ]

    # =====================================================
    # DISMISSED
    # =====================================================

    def dismissed(

        self,

    ):

        return [

            notification

            for notification in self.history

            if notification.dismissed

        ]

    # =====================================================
    # ACTIVE
    # =====================================================

    def active(

        self,

    ):

        return [

            notification

            for notification in self.history

            if not notification.dismissed

        ]
        # =====================================================
    # SCHEDULE
    # =====================================================

    def schedule(

        self,

        title: str,

        message: str,

        notify_at: datetime,

        type: NotificationType = NotificationType.INFO,

        priority: NotificationPriority = (
            NotificationPriority.NORMAL
        ),

        **metadata,

    ):

        notification = Notification(

            title=title,

            message=message,

            type=type,

            priority=priority,

            metadata=metadata,

        )

        notification.metadata["notify_at"] = notify_at

        self.history.append(notification)

        return notification

    # =====================================================
    # DUE NOTIFICATIONS
    # =====================================================

    def due_notifications(

        self,

    ):

        now = datetime.utcnow()

        due = []

        for notification in self.history:

            notify_at = notification.metadata.get(

                "notify_at"

            )

            if (

                notify_at

                and notify_at <= now

                and not notification.dismissed

            ):

                due.append(notification)

        return due

    # =====================================================
    # SORT BY PRIORITY
    # =====================================================

    def sort_by_priority(

        self,

    ):

        order = {

            NotificationPriority.CRITICAL: 4,

            NotificationPriority.HIGH: 3,

            NotificationPriority.NORMAL: 2,

            NotificationPriority.LOW: 1,

        }

        return sorted(

            self.active(),

            key=lambda n: order.get(

                n.priority,

                0,

            ),

            reverse=True,

        )

    # =====================================================
    # FILTER
    # =====================================================

    def filter(

        self,

        type: Optional[NotificationType] = None,

        priority: Optional[NotificationPriority] = None,

    ):

        results = self.history

        if type is not None:

            results = [

                n

                for n in results

                if n.type == type

            ]

        if priority is not None:

            results = [

                n

                for n in results

                if n.priority == priority

            ]

        return results

    # =====================================================
    # SEARCH
    # =====================================================

    def search(

        self,

        keyword: str,

    ):

        keyword = keyword.lower()

        return [

            n

            for n in self.history

            if (

                keyword in n.title.lower()

                or keyword in n.message.lower()

            )

        ]

    # =====================================================
    # EXPORT HISTORY
    # =====================================================

    def export_history(

        self,

    ):

        exported = []

        for n in self.history:

            exported.append(

                {

                    "id": n.id,

                    "title": n.title,

                    "message": n.message,

                    "type": n.type.value,

                    "priority": n.priority.value,

                    "created_at": n.created_at.isoformat(),

                    "read": n.read,

                    "dismissed": n.dismissed,

                    "metadata": n.metadata,

                }

            )

        return exported

    # =====================================================
    # IMPORT HISTORY
    # =====================================================

    def import_history(

        self,

        notifications: List[Dict],

    ):

        imported = 0

        for item in notifications:

            notification = Notification(

                id=item["id"],

                title=item["title"],

                message=item["message"],

                type=NotificationType(

                    item["type"]

                ),

                priority=NotificationPriority(

                    item["priority"]

                ),

                created_at=datetime.fromisoformat(

                    item["created_at"]

                ),

                read=item.get(

                    "read",

                    False,

                ),

                dismissed=item.get(

                    "dismissed",

                    False,

                ),

                metadata=item.get(

                    "metadata",

                    {},

                ),

            )

            self.history.append(notification)

            imported += 1

        return imported

    # =====================================================
    # CLEANUP
    # =====================================================

    def cleanup(

        self,

        days: int = 30,

    ):

        cutoff = datetime.utcnow().timestamp() - (

            days * 86400

        )

        before = len(

            self.history

        )

        self.history = [

            notification

            for notification in self.history

            if notification.created_at.timestamp()

            >= cutoff

        ]

        return before - len(

            self.history

        )

    # =====================================================
    # STATISTICS
    # =====================================================

    def statistics(

        self,

    ):

        return {

            "total": len(

                self.history

            ),

            "queue": len(

                self.queue

            ),

            "unread": len(

                self.unread()

            ),

            "dismissed": len(

                self.dismissed()

            ),

            "active": len(

                self.active()

            ),

            "listeners": len(

                self.listeners

            ),

        }

    # =====================================================
    # STATUS
    # =====================================================

    def status(

        self,

    ):

        stats = self.statistics()

        return {

            "notifications": stats["total"],

            "pending": stats["queue"],

            "active": stats["active"],

            "listeners": stats["listeners"],

        }
        # =====================================================
    # PROCESS QUEUE
    # =====================================================

    def process_queue(
        self,
    ):

        """
        Process all queued notifications by
        dispatching them to registered listeners.
        """

        processed = 0

        while self.queue:

            notification = self.queue.popleft()

            self._emit(notification)

            processed += 1

        return processed

    # =====================================================
    # RESET
    # =====================================================

    def reset(
        self,
    ):

        self.queue.clear()

        self.history.clear()

        self.listeners.clear()

    # =====================================================
    # STARTUP
    # =====================================================

    def startup(
        self,
    ):

        """
        Startup hook.
        Reserved for loading persisted
        notification history.
        """

        return self.statistics()

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(
        self,
    ):

        """
        Shutdown hook.
        Reserved for persisting notification history.
        """

        pending = len(self.queue)

        self.process_queue()

        return {

            "processed": pending,

            "history": len(self.history),

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(
        self,
    ):

        stats = self.statistics()

        return (

            "NotificationManager("

            f"queue={stats['queue']}, "

            f"history={stats['total']}, "

            f"listeners={stats['listeners']}"

            ")"

        )

    # -------------------------------------------------

    def __str__(
        self,
    ):

        stats = self.statistics()

        return (

            "Notification Manager\n"

            f"Queue       : {stats['queue']}\n"

            f"History     : {stats['total']}\n"

            f"Unread      : {stats['unread']}\n"

            f"Dismissed   : {stats['dismissed']}\n"

            f"Active      : {stats['active']}\n"

            f"Listeners   : {stats['listeners']}"

        )


# =====================================================
# GLOBAL SINGLETON
# =====================================================

notification_manager = NotificationManager()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "Notification",

    "NotificationPriority",

    "NotificationType",

    "NotificationManager",

    "notification_manager",

]
    # =====================================================
    # PROCESS QUEUE
    # =====================================================

def process_queue(
        self,
    ):

        """
        Process all queued notifications by
        dispatching them to registered listeners.
        """

        processed = 0

        while self.queue:

            notification = self.queue.popleft()

            self._emit(notification)

            processed += 1

        return processed

    # =====================================================
    # RESET
    # =====================================================

    def reset(
        self,
    ):

        self.queue.clear()

        self.history.clear()

        self.listeners.clear()

    # =====================================================
    # STARTUP
    # =====================================================

    def startup(
        self,
    ):

        """
        Startup hook.
        Reserved for loading persisted
        notification history.
        """

        return self.statistics()

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(
        self,
    ):

        """
        Shutdown hook.
        Reserved for persisting notification history.
        """

        pending = len(self.queue)

        self.process_queue()

        return {

            "processed": pending,

            "history": len(self.history),

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(
        self,
    ):

        stats = self.statistics()

        return (

            "NotificationManager("

            f"queue={stats['queue']}, "

            f"history={stats['total']}, "

            f"listeners={stats['listeners']}"

            ")"

        )

    # -------------------------------------------------

    def __str__(
        self,
    ):

        stats = self.statistics()

        return (

            "Notification Manager\n"

            f"Queue       : {stats['queue']}\n"

            f"History     : {stats['total']}\n"

            f"Unread      : {stats['unread']}\n"

            f"Dismissed   : {stats['dismissed']}\n"

            f"Active      : {stats['active']}\n"

            f"Listeners   : {stats['listeners']}"

        )


# =====================================================
# GLOBAL SINGLETON
# =====================================================

notification_manager = NotificationManager()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "Notification",

    "NotificationPriority",

    "NotificationType",

    "NotificationManager",

    "notification_manager",

]