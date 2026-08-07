from __future__ import annotations

import itertools
import threading
import time

from concurrent.futures import (
    Future,
    ThreadPoolExecutor,
)

from dataclasses import (
    dataclass,
    field,
)

from datetime import (
    datetime,
    timedelta,
)

from enum import IntEnum

from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
)

# =====================================================
# PRIORITY
# =====================================================

class TaskPriority(IntEnum):

    LOW = 10

    NORMAL = 50

    HIGH = 80

    CRITICAL = 100


# =====================================================
# TASK STATUS
# =====================================================

class TaskStatus:

    PENDING = "Pending"

    RUNNING = "Running"

    COMPLETED = "Completed"

    FAILED = "Failed"

    CANCELLED = "Cancelled"


# =====================================================
# TASK
# =====================================================

@dataclass(slots=True)
class Task:

    id: int

    name: str

    function: Callable

    args: tuple = ()

    kwargs: Dict[str, Any] = field(

        default_factory=dict

    )

    priority: TaskPriority = TaskPriority.NORMAL

    created_at: datetime = field(

        default_factory=datetime.now

    )

    started_at: Optional[datetime] = None

    finished_at: Optional[datetime] = None

    progress: float = 0.0

    status: str = TaskStatus.PENDING

    result: Any = None

    error: Optional[str] = None

    future: Optional[Future] = None

    metadata: Dict[str, Any] = field(

        default_factory=dict

    )

    # -------------------------------------------------

    @property
    def duration(self):

        if self.started_at is None:

            return timedelta()

        if self.finished_at is None:

            return (

                datetime.now()

                - self.started_at

            )

        return (

            self.finished_at

            - self.started_at

        )


# =====================================================
# TASK MANAGER
# =====================================================

class TaskManager:

    _instance = None

    _lock = threading.Lock()

    # -------------------------------------------------

    def __new__(

        cls,

    ):

        with cls._lock:

            if cls._instance is None:

                cls._instance = super().__new__(

                    cls

                )

        return cls._instance

    # -------------------------------------------------

    def __init__(

        self,

        max_workers: int = 8,

    ):

        if getattr(

            self,

            "_initialized",

            False,

        ):

            return

        self._initialized = True

        self.executor = ThreadPoolExecutor(

            max_workers=max_workers,

            thread_name_prefix="StockVersity",

        )

        self.tasks: Dict[int, Task] = {}

        self.task_lock = threading.RLock()

        self.counter = itertools.count(

            start=1

        )

        self.statistics = {

            "submitted": 0,

            "completed": 0,

            "failed": 0,

            "cancelled": 0,

        }

    # =====================================================
    # CREATE TASK
    # =====================================================

    def create_task(

        self,

        name: str,

        function: Callable,

        *args,

        priority: TaskPriority = TaskPriority.NORMAL,

        **kwargs,

    ) -> Task:

        task = Task(

            id=next(

                self.counter

            ),

            name=name,

            function=function,

            args=args,

            kwargs=kwargs,

            priority=priority,

        )

        with self.task_lock:

            self.tasks[

                task.id

            ] = task

            self.statistics[

                "submitted"

            ] += 1

        return task

    # =====================================================
    # SUBMIT TASK
    # =====================================================

    def submit(

        self,

        name: str,

        function: Callable,

        *args,

        priority: TaskPriority = TaskPriority.NORMAL,

        **kwargs,

    ) -> Task:

        task = self.create_task(

            name,

            function,

            *args,

            priority=priority,

            **kwargs,

        )

        future = self.executor.submit(

            self._execute,

            task,

        )

        task.future = future

        return task
        # =====================================================
    # EXECUTION ENGINE
    # =====================================================

    def _execute(

        self,

        task: Task,

    ):

        task.status = TaskStatus.RUNNING

        task.started_at = datetime.now()

        task.progress = 0.0

        try:

            result = task.function(

                *task.args,

                **task.kwargs,

            )

            task.result = result

            task.progress = 100.0

            task.status = TaskStatus.COMPLETED

            self.statistics[

                "completed"

            ] += 1

            return result

        except Exception as exc:

            task.error = str(

                exc

            )

            task.status = TaskStatus.FAILED

            task.progress = 100.0

            self.statistics[

                "failed"

            ] += 1

            raise

        finally:

            task.finished_at = datetime.now()

    # =====================================================
    # PROGRESS
    # =====================================================

    def update_progress(

        self,

        task_id: int,

        progress: float,

    ):

        task = self.tasks.get(

            task_id

        )

        if task is None:

            return False

        task.progress = max(

            0.0,

            min(

                100.0,

                progress,

            ),

        )

        return True

    # -------------------------------------------------

    def progress(

        self,

        task_id: int,

    ):

        task = self.tasks.get(

            task_id

        )

        if task is None:

            return None

        return task.progress

    # =====================================================
    # TASK LOOKUP
    # =====================================================

    def task(

        self,

        task_id: int,

    ) -> Optional[Task]:

        return self.tasks.get(

            task_id

        )

    # -------------------------------------------------

    def exists(

        self,

        task_id: int,

    ):

        return task_id in self.tasks

    # =====================================================
    # STATUS
    # =====================================================

    def status(

        self,

        task_id: int,

    ):

        task = self.tasks.get(

            task_id

        )

        if task is None:

            return None

        return task.status

    # =====================================================
    # RESULT
    # =====================================================

    def result(

        self,

        task_id: int,

        timeout: Optional[float] = None,

    ):

        task = self.tasks.get(

            task_id

        )

        if task is None:

            return None

        if task.future:

            return task.future.result(

                timeout=timeout,

            )

        return task.result

    # =====================================================
    # WAIT
    # =====================================================

    def wait(

        self,

        task_id: int,

        timeout: Optional[float] = None,

    ):

        task = self.tasks.get(

            task_id

        )

        if task is None:

            return None

        if task.future:

            task.future.result(

                timeout=timeout,

            )

        return task

    # =====================================================
    # CANCELLATION
    # =====================================================

    def cancel(

        self,

        task_id: int,

    ):

        task = self.tasks.get(

            task_id

        )

        if task is None:

            return False

        if task.future is None:

            return False

        cancelled = task.future.cancel()

        if cancelled:

            task.status = (

                TaskStatus.CANCELLED

            )

            self.statistics[

                "cancelled"

            ] += 1

        return cancelled

    # =====================================================
    # COMPLETION CHECK
    # =====================================================

    def done(

        self,

        task_id: int,

    ):

        task = self.tasks.get(

            task_id

        )

        if task is None:

            return False

        if task.future is None:

            return False

        return task.future.done()

    # -------------------------------------------------

    def running(

        self,

        task_id: int,

    ):

        task = self.tasks.get(

            task_id

        )

        if task is None:

            return False

        return (

            task.status

            == TaskStatus.RUNNING

        )
        # =====================================================
    # DELAYED TASK
    # =====================================================

    def submit_delayed(

        self,

        delay: float,

        name: str,

        function: Callable,

        *args,

        priority: TaskPriority = TaskPriority.NORMAL,

        **kwargs,

    ):

        def delayed():

            time.sleep(delay)

            return function(

                *args,

                **kwargs,

            )

        return self.submit(

            name,

            delayed,

            priority=priority,

        )

    # =====================================================
    # PERIODIC TASK
    # =====================================================

    def submit_periodic(

        self,

        interval: float,

        name: str,

        function: Callable,

        *args,

        priority: TaskPriority = TaskPriority.NORMAL,

        **kwargs,

    ):

        stop_event = threading.Event()

        def runner():

            while not stop_event.is_set():

                try:

                    function(

                        *args,

                        **kwargs,

                    )

                except Exception:

                    pass

                stop_event.wait(

                    interval

                )

        task = self.submit(

            name,

            runner,

            priority=priority,

        )

        task.metadata[

            "stop_event"

        ] = stop_event

        task.metadata[

            "periodic"

        ] = True

        return task

    # =====================================================
    # STOP PERIODIC TASK
    # =====================================================

    def stop_periodic(

        self,

        task_id: int,

    ):

        task = self.tasks.get(

            task_id

        )

        if task is None:

            return False

        stop_event = task.metadata.get(

            "stop_event"

        )

        if stop_event:

            stop_event.set()

            return True

        return False

    # =====================================================
    # REMOVE TASK
    # =====================================================

    def remove(

        self,

        task_id: int,

    ):

        with self.task_lock:

            return (

                self.tasks.pop(

                    task_id,

                    None,

                )

                is not None

            )

    # =====================================================
    # CLEANUP
    # =====================================================

    def cleanup(

        self,

        keep_completed: int = 100,

    ):

        completed = [

            task

            for task in self.tasks.values()

            if task.status in (

                TaskStatus.COMPLETED,

                TaskStatus.FAILED,

                TaskStatus.CANCELLED,

            )

        ]

        completed.sort(

            key=lambda t: (

                t.finished_at

                or datetime.min

            ),

            reverse=True,

        )

        removed = 0

        for task in completed[keep_completed:]:

            if self.remove(

                task.id

            ):

                removed += 1

        return removed

    # =====================================================
    # FILTERS
    # =====================================================

    def all_tasks(

        self,

    ):

        return list(

            self.tasks.values()

        )

    # -------------------------------------------------

    def active_tasks(

        self,

    ):

        return [

            task

            for task in self.tasks.values()

            if task.status in (

                TaskStatus.PENDING,

                TaskStatus.RUNNING,

            )

        ]

    # -------------------------------------------------

    def completed_tasks(

        self,

    ):

        return [

            task

            for task in self.tasks.values()

            if task.status ==

            TaskStatus.COMPLETED

        ]

    # -------------------------------------------------

    def failed_tasks(

        self,

    ):

        return [

            task

            for task in self.tasks.values()

            if task.status ==

            TaskStatus.FAILED

        ]

    # -------------------------------------------------

    def cancelled_tasks(

        self,

    ):

        return [

            task

            for task in self.tasks.values()

            if task.status ==

            TaskStatus.CANCELLED

        ]

    # =====================================================
    # STATISTICS
    # =====================================================

    def stats(

        self,

    ):

        return {

            **self.statistics,

            "registered_tasks": len(

                self.tasks

            ),

            "active_tasks": len(

                self.active_tasks()

            ),

            "completed_tasks": len(

                self.completed_tasks()

            ),

            "failed_tasks": len(

                self.failed_tasks()

            ),

            "cancelled_tasks": len(

                self.cancelled_tasks()

            ),

        }

    # =====================================================
    # QUEUE INFORMATION
    # =====================================================

    def pending_count(

        self,

    ):

        return len(

            [

                task

                for task in self.tasks.values()

                if task.status ==

                TaskStatus.PENDING

            ]

        )

    # -------------------------------------------------

    def running_count(

        self,

    ):

        return len(

            [

                task

                for task in self.tasks.values()

                if task.status ==

                TaskStatus.RUNNING

            ]

        )
        # =====================================================
    # BULK OPERATIONS
    # =====================================================

    def wait_all(

        self,

        timeout: Optional[float] = None,

    ):

        """
        Wait for all submitted tasks to finish.
        """

        for task in list(self.tasks.values()):

            if task.future is None:

                continue

            try:

                task.future.result(

                    timeout=timeout,

                )

            except Exception:

                pass

        return True

    # -------------------------------------------------

    def cancel_all(

        self,

    ):

        cancelled = 0

        for task in list(

            self.tasks.values()

        ):

            if self.cancel(

                task.id

            ):

                cancelled += 1

        return cancelled

    # -------------------------------------------------

    def remove_completed(

        self,

    ):

        removed = 0

        for task in list(

            self.completed_tasks()

        ):

            if self.remove(

                task.id

            ):

                removed += 1

        return removed

    # -------------------------------------------------

    def remove_failed(

        self,

    ):

        removed = 0

        for task in list(

            self.failed_tasks()

        ):

            if self.remove(

                task.id

            ):

                removed += 1

        return removed

    # =====================================================
    # CONFIGURATION
    # =====================================================

    def set_max_workers(

        self,

        workers: int,

    ):

        if workers <= 0:

            raise ValueError(

                "workers must be greater than zero."

            )

        old = self.executor

        self.executor = ThreadPoolExecutor(

            max_workers=workers,

            thread_name_prefix="StockVersity",

        )

        old.shutdown(

            wait=False,

        )

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(

        self,

        wait: bool = True,

    ):

        self.executor.shutdown(

            wait=wait,

        )

    # =====================================================
    # RESET
    # =====================================================

    def reset(

        self,

    ):

        self.cancel_all()

        self.tasks.clear()

        self.statistics = {

            "submitted": 0,

            "completed": 0,

            "failed": 0,

            "cancelled": 0,

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ):

        stats = self.stats()

        return (

            "TaskManager("

            f"tasks={stats['registered_tasks']}, "

            f"running={stats['active_tasks']}, "

            f"completed={stats['completed_tasks']})"

        )

    # -------------------------------------------------

    def __str__(

        self,

    ):

        stats = self.stats()

        return (

            "Task Manager\n"

            f"Submitted : {stats['submitted']}\n"

            f"Running   : {stats['active_tasks']}\n"

            f"Completed : {stats['completed_tasks']}\n"

            f"Failed    : {stats['failed_tasks']}\n"

            f"Cancelled : {stats['cancelled_tasks']}"

        )


# =====================================================
# GLOBAL SINGLETON
# =====================================================

task_manager = TaskManager()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "Task",

    "TaskPriority",

    "TaskStatus",

    "TaskManager",

    "task_manager",

]