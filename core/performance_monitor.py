from __future__ import annotations

import os
import threading
import time
import uuid

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


# =====================================================
# PERFORMANCE SAMPLE
# =====================================================

@dataclass(slots=True)
class PerformanceSample:

    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    timestamp: datetime = field(
        default_factory=datetime.utcnow
    )

    cpu_percent: float = 0.0

    memory_percent: float = 0.0

    disk_percent: float = 0.0

    thread_count: int = 0

    metadata: Dict = field(
        default_factory=dict
    )


# =====================================================
# PERFORMANCE MONITOR
# =====================================================

class PerformanceMonitor:

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

        self.history: List[
            PerformanceSample
        ] = []

        self.running = False

        self.worker: Optional[
            threading.Thread
        ] = None

        self.interval = 5

        self.max_history = 1000

    # =====================================================
    # START
    # =====================================================

    def start(

        self,

        interval: int = 5,

    ):

        if self.running:

            return

        self.interval = max(

            1,

            interval,

        )

        self.running = True

        self.worker = threading.Thread(

            target=self._worker,

            daemon=True,

            name="PerformanceMonitor",

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
    # WORKER
    # =====================================================

    def _worker(

        self,

    ):

        while self.running:

            try:

                self.capture()

            except Exception:

                pass

            time.sleep(

                self.interval

            )

    # =====================================================
    # CAPTURE
    # =====================================================

    def capture(

        self,

    ):

        sample = PerformanceSample(

            cpu_percent=self.cpu_usage(),

            memory_percent=self.memory_usage(),

            disk_percent=self.disk_usage(),

            thread_count=self.thread_count(),

        )

        self.history.append(

            sample

        )

        while len(

            self.history

        ) > self.max_history:

            self.history.pop(

                0

            )

        return sample

    # =====================================================
    # CPU
    # =====================================================

    def cpu_usage(

        self,

    ):

        """
        Placeholder.

        Replace with psutil.cpu_percent()
        when psutil is integrated.
        """

        return 0.0

    # =====================================================
    # MEMORY
    # =====================================================

    def memory_usage(

        self,

    ):

        """
        Placeholder.

        Replace with
        psutil.virtual_memory().
        """

        return 0.0

    # =====================================================
    # DISK
    # =====================================================

    def disk_usage(

        self,

    ):

        """
        Placeholder.

        Replace with
        psutil.disk_usage().
        """

        return 0.0

    # =====================================================
    # THREAD COUNT
    # =====================================================

    def thread_count(

        self,

    ):

        return threading.active_count()

    # =====================================================
    # PROCESS ID
    # =====================================================

    def process_id(

        self,

    ):

        return os.getpid()

    # =====================================================
    # LAST SAMPLE
    # =====================================================

    def latest(

        self,

    ):

        if not self.history:

            return None

        return self.history[-1]
        # =====================================================
    # NETWORK USAGE
    # =====================================================

    def network_usage(

        self,

    ):

        """
        Placeholder.

        Replace with psutil.net_io_counters()
        if psutil becomes a dependency.
        """

        return {

            "bytes_sent": 0,

            "bytes_received": 0,

        }

    # =====================================================
    # EXECUTION TIMER START
    # =====================================================

    def start_timer(

        self,

    ):

        return time.perf_counter()

    # =====================================================
    # EXECUTION TIMER STOP
    # =====================================================

    def stop_timer(

        self,

        start_time: float,

    ):

        return (

            time.perf_counter()

            - start_time

        )

    # =====================================================
    # TIME FUNCTION
    # =====================================================

    def time_function(

        self,

        func,

        *args,

        **kwargs,

    ):

        started = self.start_timer()

        result = func(

            *args,

            **kwargs,

        )

        elapsed = self.stop_timer(

            started

        )

        return {

            "result": result,

            "elapsed": elapsed,

        }

    # =====================================================
    # TIMING DECORATOR
    # =====================================================

    def timed(

        self,

        func,

    ):

        def wrapper(

            *args,

            **kwargs,

        ):

            started = self.start_timer()

            result = func(

                *args,

                **kwargs,

            )

            elapsed = self.stop_timer(

                started

            )

            return result, elapsed

        return wrapper

    # =====================================================
    # AVERAGE CPU
    # =====================================================

    def average_cpu(

        self,

    ):

        if not self.history:

            return 0.0

        return sum(

            sample.cpu_percent

            for sample in self.history

        ) / len(

            self.history

        )

    # =====================================================
    # AVERAGE MEMORY
    # =====================================================

    def average_memory(

        self,

    ):

        if not self.history:

            return 0.0

        return sum(

            sample.memory_percent

            for sample in self.history

        ) / len(

            self.history

        )

    # =====================================================
    # PEAK CPU
    # =====================================================

    def peak_cpu(

        self,

    ):

        if not self.history:

            return 0.0

        return max(

            sample.cpu_percent

            for sample in self.history

        )

    # =====================================================
    # PEAK MEMORY
    # =====================================================

    def peak_memory(

        self,

    ):

        if not self.history:

            return 0.0

        return max(

            sample.memory_percent

            for sample in self.history

        )

    # =====================================================
    # RESOURCE ALERTS
    # =====================================================

    def alerts(

        self,

        cpu_limit: float = 90.0,

        memory_limit: float = 90.0,

        disk_limit: float = 90.0,

    ):

        sample = self.latest()

        if sample is None:

            return []

        alerts = []

        if sample.cpu_percent >= cpu_limit:

            alerts.append(

                "High CPU usage"

            )

        if sample.memory_percent >= memory_limit:

            alerts.append(

                "High memory usage"

            )

        if sample.disk_percent >= disk_limit:

            alerts.append(

                "High disk usage"

            )

        return alerts

    # =====================================================
    # SEARCH HISTORY
    # =====================================================

    def search(

        self,

        predicate,

    ):

        return [

            sample

            for sample in self.history

            if predicate(

                sample

            )

        ]

    # =====================================================
    # CLEANUP
    # =====================================================

    def cleanup(

        self,

        keep: int = 500,

    ):

        if keep < 0:

            keep = 0

        removed = max(

            0,

            len(

                self.history

            ) - keep,

        )

        if removed:

            self.history = self.history[

                -keep:

            ] if keep else []

        return removed
        # =====================================================
    # STATISTICS
    # =====================================================

    def statistics(

        self,

    ):

        return {

            "samples": len(

                self.history

            ),

            "average_cpu": self.average_cpu(),

            "average_memory": self.average_memory(),

            "peak_cpu": self.peak_cpu(),

            "peak_memory": self.peak_memory(),

            "latest": self.latest(),

        }

    # =====================================================
    # HEALTH
    # =====================================================

    def health(

        self,

    ):

        sample = self.latest()

        return {

            "running": self.running,

            "thread_alive": (

                self.worker.is_alive()

                if self.worker

                else False

            ),

            "samples": len(

                self.history

            ),

            "latest_cpu": (

                sample.cpu_percent

                if sample

                else 0.0

            ),

            "latest_memory": (

                sample.memory_percent

                if sample

                else 0.0

            ),

            "latest_disk": (

                sample.disk_percent

                if sample

                else 0.0

            ),

        }

    # =====================================================
    # UPTIME
    # =====================================================

    def uptime(

        self,

    ):

        if not self.history:

            return 0.0

        first = self.history[0].timestamp

        last = self.history[-1].timestamp

        return (

            last - first

        ).total_seconds()

    # =====================================================
    # THREAD INFORMATION
    # =====================================================

    def thread_info(

        self,

    ):

        return {

            "active_threads": threading.active_count(),

            "monitor_running": self.running,

            "worker_name": (

                self.worker.name

                if self.worker

                else None

            ),

            "worker_alive": (

                self.worker.is_alive()

                if self.worker

                else False

            ),

        }

    # =====================================================
    # EXPORT HISTORY
    # =====================================================

    def export_history(

        self,

    ):

        exported = []

        for sample in self.history:

            exported.append(

                {

                    "id": sample.id,

                    "timestamp": sample.timestamp.isoformat(),

                    "cpu": sample.cpu_percent,

                    "memory": sample.memory_percent,

                    "disk": sample.disk_percent,

                    "threads": sample.thread_count,

                }

            )

        return exported

    # =====================================================
    # RESET
    # =====================================================

    def reset(

        self,

    ):

        self.history.clear()

    # =====================================================
    # MONITOR STATUS
    # =====================================================

    def status(

        self,

    ):

        return {

            "running": self.running,

            "interval": self.interval,

            "history_size": len(

                self.history

            ),

            "max_history": self.max_history,

        }

    # =====================================================
    # RESOURCE SUMMARY
    # =====================================================

    def resource_summary(

        self,

    ):

        sample = self.latest()

        if sample is None:

            return {

                "cpu": 0.0,

                "memory": 0.0,

                "disk": 0.0,

                "threads": 0,

            }

        return {

            "cpu": sample.cpu_percent,

            "memory": sample.memory_percent,

            "disk": sample.disk_percent,

            "threads": sample.thread_count,

        }

    # =====================================================
    # SAMPLE COUNT
    # =====================================================

    def sample_count(

        self,

    ):

        return len(

            self.history

        )

    # =====================================================
    # IS RUNNING
    # =====================================================

    def is_running(

        self,

    ):

        return self.running
        # =====================================================
    # STARTUP
    # =====================================================

    def startup(

        self,

    ):

        """
        Startup hook.

        Reserved for future initialization,
        configuration loading, or OS-specific
        performance integrations.
        """

        return self.statistics()

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(

        self,

    ):

        """
        Gracefully stop monitoring and
        return final statistics.
        """

        if self.running:

            self.stop()

        return self.statistics()

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
    # EXISTS
    # =====================================================

    def exists(

        self,

        sample_id: str,

    ):

        return any(

            sample.id == sample_id

            for sample in self.history

        )

    # =====================================================
    # LAST ALERTS
    # =====================================================

    def last_alerts(

        self,

    ):

        return self.alerts()

    # =====================================================
    # REPR
    # =====================================================

    def __repr__(

        self,

    ):

        stats = self.statistics()

        return (

            "PerformanceMonitor("

            f"samples={stats['samples']}, "

            f"running={self.running}"

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

            "Performance Monitor\n"

            f"Running        : {self.running}\n"

            f"Samples        : {stats['samples']}\n"

            f"Average CPU    : {stats['average_cpu']:.2f}%\n"

            f"Peak CPU       : {stats['peak_cpu']:.2f}%\n"

            f"Average Memory : {stats['average_memory']:.2f}%\n"

            f"Peak Memory    : {stats['peak_memory']:.2f}%\n"

            f"Uptime         : {self.uptime():.2f} sec"

        )


# =====================================================
# GLOBAL SINGLETON
# =====================================================

performance_monitor = PerformanceMonitor()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "PerformanceSample",

    "PerformanceMonitor",

    "performance_monitor",

]