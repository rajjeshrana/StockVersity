from __future__ import annotations

import threading
import time
import uuid

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Dict, List, Optional


# =====================================================
# TASK STATUS
# =====================================================

class TaskStatus(str, Enum):

    PENDING = "pending"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"

    PAUSED = "paused"


# =====================================================
# SCHEDULE TYPE
# =====================================================

class ScheduleType(str, Enum):

    ONCE = "once"

    INTERVAL = "interval"


# =====================================================
# SCHEDULED TASK
# =====================================================

@dataclass(slots=True)
class ScheduledTask:

    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    name: str = ""

    callback: Optional[
        Callable
    ] = None

    schedule_type: ScheduleType = (
        ScheduleType.ONCE
    )

    run_at: Optional[
        datetime
    ] = None

    interval: int = 0

    priority: int = 5

    retries: int = 0

    retry_count: int = 0

    status: TaskStatus = (
        TaskStatus.PENDING
    )

    enabled: bool = True

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    last_run: Optional[
        datetime
    ] = None

    next_run: Optional[
        datetime
    ] = None

    metadata: Dict = field(
        default_factory=dict
    )


# =====================================================
# SCHEDULER MANAGER
# =====================================================

class SchedulerManager:

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

        if getattr(

            self,

            "_initialized",

            False,

        ):

            return

        self._initialized = True

        self.manager_lock = threading.RLock()

        self.tasks: List[
            ScheduledTask
        ] = []

        self.history: List[
            Dict
        ] = []

        self.running = False

        self.worker: Optional[
            threading.Thread
        ] = None

        self.poll_interval = 1

    # =====================================================
    # ADD TASK
    # =====================================================

    def add_task(

        self,

        name: str,

        callback: Callable,

        run_at: Optional[
            datetime
        ] = None,

        interval: int = 0,

        priority: int = 5,

        retries: int = 0,

        metadata: Optional[
            Dict
        ] = None,

    ):

        schedule_type = (

            ScheduleType.INTERVAL

            if interval > 0

            else ScheduleType.ONCE

        )

        task = ScheduledTask(

            name=name,

            callback=callback,

            run_at=run_at,

            interval=interval,

            priority=priority,

            retries=retries,

            schedule_type=schedule_type,

            next_run=run_at,

            metadata=metadata or {},

        )

        self.tasks.append(

            task

        )

        self.tasks.sort(

            key=lambda t: (

                t.priority,

                t.next_run

                or datetime.max,

            )

        )

        return task

    # =====================================================
    # GET TASK
    # =====================================================

    def get_task(

        self,

        task_id: str,

    ):

        for task in self.tasks:

            if task.id == task_id:

                return task

        return None

    # =====================================================
    # REMOVE TASK
    # =====================================================

    def remove_task(

        self,

        task_id: str,

    ):

        task = self.get_task(

            task_id

        )

        if task is None:

            return False

        self.tasks.remove(

            task

        )

        return True

    # =====================================================
    # LIST TASKS
    # =====================================================

    def list_tasks(

        self,

    ):

        return list(

            self.tasks

        )

    # =====================================================
    # ENABLE
    # =====================================================

    def enable(

        self,

        task_id: str,

    ):

        task = self.get_task(

            task_id

        )

        if task is None:

            return False

        task.enabled = True

        task.status = TaskStatus.PENDING

        return True

    # =====================================================
    # DISABLE
    # =====================================================

    def disable(

        self,

        task_id: str,

    ):

        task = self.get_task(

            task_id

        )

        if task is None:

            return False

        task.enabled = False

        task.status = TaskStatus.PAUSED

        return True
        # =====================================================
    # START
    # =====================================================

    def start(

        self,

    ):

        if self.running:

            return

        self.running = True

        self.worker = threading.Thread(

            target=self._worker_loop,

            daemon=True,

            name="SchedulerManager",

        )

        self.worker.start()

    # =====================================================
    # STOP
    # =====================================================

    def stop(

        self,

    ):

        self.running = False

        if (

            self.worker

            and self.worker.is_alive()

        ):

            self.worker.join(

                timeout=5

            )

    # =====================================================
    # WORKER LOOP
    # =====================================================

    def _worker_loop(

        self,

    ):

        while self.running:

            try:

                self._process_tasks()

            except Exception:

                pass

            time.sleep(

                self.poll_interval

            )

    # =====================================================
    # PROCESS TASKS
    # =====================================================

    def _process_tasks(

        self,

    ):

        now = datetime.utcnow()

        for task in list(

            self.tasks

        ):

            if not task.enabled:

                continue

            if task.status == TaskStatus.CANCELLED:

                continue

            if task.next_run is None:

                continue

            if now >= task.next_run:

                self._execute(

                    task

                )

    # =====================================================
    # EXECUTE
    # =====================================================

    def _execute(

        self,

        task: ScheduledTask,

    ):

        task.status = (

            TaskStatus.RUNNING

        )

        task.last_run = (

            datetime.utcnow()

        )

        try:

            if task.callback:

                task.callback()

            task.status = (

                TaskStatus.COMPLETED

            )

            self.history.append(

                {

                    "task": task.name,

                    "status": "completed",

                    "time": datetime.utcnow(),

                }

            )

            if (

                task.schedule_type

                == ScheduleType.INTERVAL

            ):

                task.next_run = (

                    datetime.utcnow()

                    + timedelta(

                        seconds=task.interval

                    )

                )

                task.status = (

                    TaskStatus.PENDING

                )

            else:

                task.enabled = False

        except Exception as exc:

            self._handle_failure(

                task,

                exc,

            )

    # =====================================================
    # FAILURE
    # =====================================================

    def _handle_failure(

        self,

        task: ScheduledTask,

        error: Exception,

    ):

        task.retry_count += 1

        self.history.append(

            {

                "task": task.name,

                "status": "failed",

                "error": str(

                    error

                ),

                "time": datetime.utcnow(),

            }

        )

        if (

            task.retry_count

            <= task.retries

        ):

            task.status = (

                TaskStatus.PENDING

            )

            task.next_run = (

                datetime.utcnow()

                + timedelta(

                    seconds=5

                )

            )

        else:

            task.status = (

                TaskStatus.FAILED

            )

            task.enabled = False

    # =====================================================
    # PAUSE
    # =====================================================

    def pause(

        self,

        task_id: str,

    ):

        task = self.get_task(

            task_id

        )

        if task is None:

            return False

        task.enabled = False

        task.status = (

            TaskStatus.PAUSED

        )

        return True

    # =====================================================
    # RESUME
    # =====================================================

    def resume(

        self,

        task_id: str,

    ):

        task = self.get_task(

            task_id

        )

        if task is None:

            return False

        task.enabled = True

        task.status = (

            TaskStatus.PENDING

        )

        if task.next_run is None:

            task.next_run = (

                datetime.utcnow()

            )

        return True

    # =====================================================
    # CANCEL
    # =====================================================

    def cancel(

        self,

        task_id: str,

    ):

        task = self.get_task(

            task_id

        )

        if task is None:

            return False

        task.enabled = False

        task.status = (

            TaskStatus.CANCELLED

        )

        return True

    # =====================================================
    # EXECUTION HISTORY
    # =====================================================

    def execution_history(

        self,

    ):

        return list(

            self.history

        )
        # =====================================================
    # RUN NOW
    # =====================================================

    def run_now(

        self,

        task_id: str,

    ):

        task = self.get_task(

            task_id

        )

        if task is None:

            return False

        self._execute(

            task

        )

        return True

    # =====================================================
    # RESCHEDULE
    # =====================================================

    def reschedule(

        self,

        task_id: str,

        run_at: datetime,

    ):

        task = self.get_task(

            task_id

        )

        if task is None:

            return False

        task.next_run = run_at

        task.status = TaskStatus.PENDING

        task.enabled = True

        return True

    # =====================================================
    # CHANGE INTERVAL
    # =====================================================

    def change_interval(

        self,

        task_id: str,

        seconds: int,

    ):

        task = self.get_task(

            task_id

        )

        if task is None:

            return False

        task.interval = seconds

        task.schedule_type = (

            ScheduleType.INTERVAL

        )

        task.next_run = (

            datetime.utcnow()

            + timedelta(

                seconds=seconds

            )

        )

        return True

    # =====================================================
    # SEARCH TASKS
    # =====================================================

    def search(

        self,

        keyword: str,

    ):

        keyword = keyword.lower()

        return [

            task

            for task in self.tasks

            if (

                keyword

                in task.name.lower()

            )

        ]

    # =====================================================
    # FILTER STATUS
    # =====================================================

    def filter_status(

        self,

        status: TaskStatus,

    ):

        return [

            task

            for task in self.tasks

            if task.status == status

        ]

    # =====================================================
    # SORT BY PRIORITY
    # =====================================================

    def sort_by_priority(

        self,

    ):

        return sorted(

            self.tasks,

            key=lambda task: (

                task.priority,

                task.next_run

                or datetime.max,

            ),

        )

    # =====================================================
    # CLEANUP
    # =====================================================

    def cleanup(

        self,

    ):

        before = len(

            self.tasks

        )

        self.tasks = [

            task

            for task in self.tasks

            if task.status

            not in (

                TaskStatus.COMPLETED,

                TaskStatus.CANCELLED,

            )

        ]

        return before - len(

            self.tasks

        )

    # =====================================================
    # HEALTH
    # =====================================================

    def health(

        self,

    ):

        pending = len(

            self.filter_status(

                TaskStatus.PENDING

            )

        )

        running = len(

            self.filter_status(

                TaskStatus.RUNNING

            )

        )

        failed = len(

            self.filter_status(

                TaskStatus.FAILED

            )

        )

        paused = len(

            self.filter_status(

                TaskStatus.PAUSED

            )

        )

        return {

            "running": self.running,

            "tasks": len(

                self.tasks

            ),

            "pending": pending,

            "running_tasks": running,

            "failed": failed,

            "paused": paused,

            "history": len(

                self.history

            ),

        }

    # =====================================================
    # STATISTICS
    # =====================================================

    def statistics(

        self,

    ):

        once = len(

            [

                task

                for task in self.tasks

                if task.schedule_type

                == ScheduleType.ONCE

            ]

        )

        interval = len(

            [

                task

                for task in self.tasks

                if task.schedule_type

                == ScheduleType.INTERVAL

            ]

        )

        return {

            "total_tasks": len(

                self.tasks

            ),

            "one_time": once,

            "interval": interval,

            "history": len(

                self.history

            ),

            "running": self.running,

        }

    # =====================================================
    # NEXT TASK
    # =====================================================

    def next_task(

        self,

    ):

        tasks = [

            task

            for task in self.tasks

            if (

                task.enabled

                and task.next_run

            )

        ]

        if not tasks:

            return None

        return min(

            tasks,

            key=lambda task: task.next_run,

        )
        # =====================================================
    # RESET
    # =====================================================

    def reset(

        self,

    ):

        """
        Reset scheduler state.
        """

        self.stop()

        self.tasks.clear()

        self.history.clear()

    # =====================================================
    # STARTUP
    # =====================================================

    def startup(

        self,

    ):

        """
        Startup hook.

        Starts the background scheduler.
        """

        if not self.running:

            self.start()

        return self.statistics()

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(

        self,

    ):

        """
        Shutdown hook.

        Stops the scheduler safely.
        """

        self.stop()

        return {

            "tasks": len(

                self.tasks

            ),

            "history": len(

                self.history

            ),

            "running": self.running,

        }

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
    # IS RUNNING
    # =====================================================

    def is_running(

        self,

    ):

        return self.running

    # =====================================================
    # ACTIVE TASKS
    # =====================================================

    def active_tasks(

        self,

    ):

        return [

            task

            for task in self.tasks

            if (

                task.enabled

                and task.status

                not in (

                    TaskStatus.CANCELLED,

                    TaskStatus.COMPLETED,

                )

            )

        ]

    # =====================================================
    # REPR
    # =====================================================

    def __repr__(

        self,

    ):

        stats = self.statistics()

        return (

            "SchedulerManager("

            f"tasks={stats['total_tasks']}, "

            f"history={stats['history']}, "

            f"running={stats['running']}"

            ")"

        )

    # =====================================================
    # STR
    # =====================================================

    def __str__(

        self,

    ):

        stats = self.statistics()

        return (

            "Scheduler Manager\n"

            f"Running      : {stats['running']}\n"

            f"Tasks        : {stats['total_tasks']}\n"

            f"One-Time     : {stats['one_time']}\n"

            f"Interval     : {stats['interval']}\n"

            f"History      : {stats['history']}"

        )


# =====================================================
# GLOBAL SINGLETON
# =====================================================

scheduler_manager = SchedulerManager()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "TaskStatus",

    "ScheduleType",

    "ScheduledTask",

    "SchedulerManager",

    "scheduler_manager",

]