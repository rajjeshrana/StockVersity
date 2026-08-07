"""
=========================================================
StockVersity Scanner Pro
Professional Status Bar
Version : 4.0
Powered By : AI
=========================================================
"""

from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import (
    Qt,
    Signal,
    QTimer,
)

from PySide6.QtGui import QFont

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QProgressBar,
    QSizePolicy,
    QFrame,
)


class StatusBar(QWidget):

    """
    Professional Trading Terminal Status Bar
    """

    messageChanged = Signal(str)

    # =====================================================
    # INIT
    # =====================================================

    def __init__(self):

        super().__init__()

        self.current_message = "Ready"

        self.build_ui()

        self.start_clock()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(self):

        self.setMinimumHeight(34)

        self.setMaximumHeight(34)

        layout = QHBoxLayout(self)

        layout.setContentsMargins(

            12,

            2,

            12,

            2

        )

        layout.setSpacing(10)

        # ----------------------------------------
        # Status Message
        # ----------------------------------------

        self.message = QLabel("Ready")

        self.message.setSizePolicy(

            QSizePolicy.Expanding,

            QSizePolicy.Preferred

        )

        # ----------------------------------------
        # Progress
        # ----------------------------------------

        self.progress = QProgressBar()

        self.progress.setFixedWidth(140)

        self.progress.setRange(0, 100)

        self.progress.setValue(0)

        self.progress.hide()

        # ----------------------------------------
        # Scanner
        # ----------------------------------------

        self.scanner = QLabel(

            "Scanner : Idle"

        )

        # ----------------------------------------
        # NSE Connection
        # ----------------------------------------

        self.connection = QLabel(

            "🟢 NSE"

        )

        # ----------------------------------------
        # Execution
        # ----------------------------------------

        self.execution = QLabel(

            "0 ms"

        )

        # ----------------------------------------
        # Clock
        # ----------------------------------------

        self.clock = QLabel()

        font = QFont()

        font.setPointSize(9)

        self.clock.setFont(font)

        layout.addWidget(

            self.message,

            1

        )

        layout.addWidget(

            self.progress

        )

        layout.addWidget(

            self.scanner

        )

        layout.addWidget(

            self.connection

        )

        layout.addWidget(

            self.execution

        )

        layout.addWidget(

            self.clock

        )

    # =====================================================
    # CLOCK
    # =====================================================

    def start_clock(self):

        self.timer = QTimer(self)

        self.timer.timeout.connect(

            self.update_clock

        )

        self.timer.start(

            1000

        )

        self.update_clock()

    # =====================================================
    # UPDATE CLOCK
    # =====================================================

    def update_clock(self):

        self.clock.setText(

            datetime.now().strftime(

                "%H:%M:%S"

            )

        )

    # =====================================================
    # STATUS MESSAGE
    # =====================================================

    def show_message(

        self,

        message: str

    ):

        self.current_message = message

        self.message.setText(

            message

        )

        self.messageChanged.emit(

            message

        )

    # =====================================================
    # CLEAR MESSAGE
    # =====================================================

    def clear_message(self):

        self.show_message(

            "Ready"

        )
            # =====================================================
    # AUTO CLEAR MESSAGE
    # =====================================================

    def show_temporary_message(

        self,

        message: str,

        timeout: int = 3000

    ):

        self.show_message(message)

        QTimer.singleShot(

            timeout,

            self.clear_message

        )

    # =====================================================
    # PROGRESS
    # =====================================================

    def show_progress(

        self,

        value: int

    ):

        self.progress.show()

        self.progress.setValue(

            max(0, min(100, value))

        )

    # =====================================================
    # HIDE PROGRESS
    # =====================================================

    def hide_progress(self):

        self.progress.hide()

        self.progress.setValue(0)

    # =====================================================
    # START TASK
    # =====================================================

    def start_task(

        self,

        task_name: str

    ):

        self.show_message(

            f"{task_name}..."

        )

        self.progress.show()

        self.progress.setRange(

            0,

            0

        )

    # =====================================================
    # FINISH TASK
    # =====================================================

    def finish_task(

        self,

        message: str = "Completed"

    ):

        self.progress.setRange(

            0,

            100

        )

        self.progress.setValue(100)

        QTimer.singleShot(

            400,

            self.hide_progress

        )

        self.show_temporary_message(

            message

        )

    # =====================================================
    # SCANNER STATUS
    # =====================================================

    def set_scanner_status(

        self,

        status: str

    ):

        self.scanner.setText(

            f"Scanner : {status}"

        )

    # =====================================================
    # CONNECTION STATUS
    # =====================================================

    def set_connection_status(

        self,

        connected: bool

    ):

        if connected:

            self.connection.setText(

                "🟢 NSE"

            )

        else:

            self.connection.setText(

                "🔴 NSE"

            )

    # =====================================================
    # EXECUTION TIME
    # =====================================================

    def set_execution_time(

        self,

        milliseconds: int

    ):

        self.execution.setText(

            f"{milliseconds} ms"

        )

    # =====================================================
    # BACKGROUND TASK
    # =====================================================

    def set_background_task(

        self,

        name: str

    ):

        self.show_message(

            f"Background : {name}"

        )

    # =====================================================
    # TASK QUEUE
    # =====================================================

    def set_queue_size(

        self,

        size: int

    ):

        self.scanner.setToolTip(

            f"Pending Tasks : {size}"

        )

    # =====================================================
    # MEMORY USAGE
    # =====================================================

    def set_memory_usage(

        self,

        usage_mb: float

    ):

        self.execution.setToolTip(

            f"Memory : {usage_mb:.1f} MB"

        )

    # =====================================================
    # CPU USAGE
    # =====================================================

    def set_cpu_usage(

        self,

        usage_percent: float

    ):

        tooltip = self.execution.toolTip()

        tooltip += (

            f"\nCPU : {usage_percent:.1f}%"

        )

        self.execution.setToolTip(

            tooltip

        )

    # =====================================================
    # RESET STATUS BAR
    # =====================================================

    def reset(self):

        self.hide_progress()

        self.show_message(

            "Ready"

        )

        self.set_scanner_status(

            "Idle"

        )

        self.set_connection_status(

            False

        )

        self.set_execution_time(

            0

        )
            # =====================================================
    # SCAN STATISTICS
    # =====================================================

    def initialize_statistics(self):

        self.total_scans = 0

        self.successful_scans = 0

        self.failed_scans = 0

        self.last_scan_time = None

    # =====================================================
    # SCAN STARTED
    # =====================================================

    def scan_started(self):

        self.total_scans += 1

        self.last_scan_time = datetime.now()

        self.set_scanner_status(

            "Scanning"

        )

        self.start_task(

            "Running Scanner"

        )

    # =====================================================
    # SCAN SUCCESS
    # =====================================================

    def scan_success(

        self,

        execution_ms: int

    ):

        self.successful_scans += 1

        self.set_execution_time(

            execution_ms

        )

        self.set_scanner_status(

            "Ready"

        )

        self.finish_task(

            "Scan Completed"

        )

    # =====================================================
    # SCAN FAILED
    # =====================================================

    def scan_failed(

        self,

        error: str = ""

    ):

        self.failed_scans += 1

        self.set_scanner_status(

            "Error"

        )

        self.hide_progress()

        if error:

            self.show_temporary_message(

                error,

                5000

            )

    # =====================================================
    # MARKET STATUS
    # =====================================================

    def set_market_status(

        self,

        status: str

    ):

        self.connection.setToolTip(

            f"Market : {status}"

        )

    # =====================================================
    # RUNTIME INFORMATION
    # =====================================================

    def runtime_information(self):

        return {

            "message":

                self.current_message,

            "scanner":

                self.scanner.text(),

            "connection":

                self.connection.text(),

            "execution":

                self.execution.text(),

            "last_scan":

                self.last_scan_time,

            "statistics":

                self.statistics()

        }

    # =====================================================
    # STATISTICS
    # =====================================================

    def statistics(self):

        success_rate = 0.0

        if self.total_scans:

            success_rate = (

                self.successful_scans

                / self.total_scans

            ) * 100

        return {

            "total":

                self.total_scans,

            "success":

                self.successful_scans,

            "failed":

                self.failed_scans,

            "success_rate":

                round(success_rate, 2)

        }

    # =====================================================
    # EXPORT STATE
    # =====================================================

    def export_state(self):

        return {

            "runtime":

                self.runtime_information(),

            "statistics":

                self.statistics()

        }

    # =====================================================
    # IMPORT STATE
    # =====================================================

    def import_state(

        self,

        state: dict

    ):

        if not state:

            return

        stats = state.get(

            "statistics",

            {}

        )

        self.total_scans = stats.get(

            "total",

            0

        )

        self.successful_scans = stats.get(

            "success",

            0

        )

        self.failed_scans = stats.get(

            "failed",

            0

        )

    # =====================================================
    # BUILD INFORMATION
    # =====================================================

    def build_information(self):

        return {

            "application":

                "StockVersity Scanner Pro",

            "component":

                "StatusBar",

            "version":

                "4.0",

            "powered_by":

                "AI"

        }

    # =====================================================
    # DIAGNOSTICS
    # =====================================================

    def diagnostics(self):

        return {

            "component":

                "StatusBar",

            "runtime":

                self.runtime_information(),

            "build":

                self.build_information()

        }

    # =====================================================
    # PUBLIC API
    # =====================================================

    def update_status(

        self,

        message: str,

        scanner: str,

        connected: bool,

        execution_ms: int

    ):

        self.show_message(

            message

        )

        self.set_scanner_status(

            scanner

        )

        self.set_connection_status(

            connected

        )

        self.set_execution_time(

            execution_ms

        )
            # =====================================================
    # CLEAR STATISTICS
    # =====================================================

    def clear_statistics(self):

        self.total_scans = 0

        self.successful_scans = 0

        self.failed_scans = 0

        self.last_scan_time = None

    # =====================================================
    # CLEAR ALL
    # =====================================================

    def clear(self):

        self.reset()

        self.clear_statistics()

        self.clear_message()

    # =====================================================
    # IS BUSY
    # =====================================================

    def is_busy(self):

        return self.progress.isVisible()

    # =====================================================
    # CURRENT MESSAGE
    # =====================================================

    def current_status(self):

        return self.current_message

    # =====================================================
    # COMPONENT INFORMATION
    # =====================================================

    @property
    def component_name(self):

        return "StatusBar"

    @property
    def application_name(self):

        return "StockVersity Scanner Pro"

    @property
    def version(self):

        return "4.0"

    # =====================================================
    # HEALTH STATUS
    # =====================================================

    def health_status(self):

        return {

            "healthy": True,

            "busy": self.is_busy(),

            "scanner":

                self.scanner.text(),

            "connection":

                self.connection.text()

        }

    # =====================================================
    # SAVE STATE
    # =====================================================

    def save_state(self):

        return {

            "message":

                self.current_message,

            "statistics":

                self.statistics(),

            "execution":

                self.execution.text(),

            "scanner":

                self.scanner.text()

        }

    # =====================================================
    # RESTORE STATE
    # =====================================================

    def restore_state(

        self,

        state: dict

    ):

        if not state:

            return

        self.show_message(

            state.get(

                "message",

                "Ready"

            )

        )

        self.import_state(state)

        self.execution.setText(

            state.get(

                "execution",

                "0 ms"

            )

        )

        self.scanner.setText(

            state.get(

                "scanner",

                "Scanner : Idle"

            )

        )

    # =====================================================
    # REFRESH UI
    # =====================================================

    def refresh(self):

        self.update()

        self.repaint()

    # =====================================================
    # STRING REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (

            f"<StatusBar "

            f"message='{self.current_message}' "

            f"scanner='{self.scanner.text()}'>"

        )


# =====================================================
# FACTORY
# =====================================================

def create_statusbar():

    return StatusBar()


# =====================================================
# END OF FILE
# =====================================================