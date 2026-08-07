"""
=========================================================
StockVersity Scanner Pro
Main Window
Version : 4.0
Powered By : AI
=========================================================
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from core.dependency_container import (
    get_container
)

from core.configuration_manager import (
    get_configuration
)

from ui.layout.sidebar import Sidebar
from ui.layout.header import Header
from ui.layout.statusbar import StatusBar

from ui.pages.dashboard import DashboardPage
from ui.pages.intraday import IntradayPage
from ui.pages.swing import SwingPage
from ui.pages.positional import PositionalPage
from ui.pages.market_dashboard import MarketDashboardPage
from ui.pages.settings import SettingsPage


class MainWindow(QMainWindow):

    """
    Main Application Window
    """

    def __init__(self):

        super().__init__()

        self.container = get_container()

        self.config = get_configuration()

        self.setWindowTitle(
            "StockVersity Scanner Pro"
        )

        self.resize(1700, 980)

        self.setMinimumSize(1400, 850)

        self._create_ui()

        self._connect_signals()

        self.load_theme()

    # ====================================================
    # UI
    # ====================================================

    def _create_ui(self):

        central = QWidget()

        self.setCentralWidget(central)

        root = QHBoxLayout(central)

        root.setContentsMargins(0, 0, 0, 0)

        root.setSpacing(0)

        # ----------------------------------------
        # Sidebar
        # ----------------------------------------

        self.sidebar = Sidebar()

        root.addWidget(self.sidebar)

        # ----------------------------------------
        # Right Panel
        # ----------------------------------------

        right = QWidget()

        right_layout = QVBoxLayout(right)

        right_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        right_layout.setSpacing(0)

        root.addWidget(right)

        # ----------------------------------------
        # Header
        # ----------------------------------------

        self.header = Header()

        right_layout.addWidget(
            self.header
        )

        # ----------------------------------------
        # Pages
        # ----------------------------------------

        self.stack = QStackedWidget()

        right_layout.addWidget(
            self.stack,
            1
        )

        # ----------------------------------------
        # Status Bar
        # ----------------------------------------

        self.status = StatusBar()

        right_layout.addWidget(
            self.status
        )

        self._create_pages()

    # ====================================================
    # PAGES
    # ====================================================

    def _create_pages(self):

        # ------------------------------------------------
        # Create Pages
        # ------------------------------------------------

        self.dashboard_page = DashboardPage()

        self.intraday_page = IntradayPage()

        self.swing_page = SwingPage()

        self.positional_page = PositionalPage()

        self.market_page = MarketDashboardPage()

        self.settings_page = SettingsPage(
            self.container.get("application_controller")
        )

        # ------------------------------------------------
        # Add Pages To Stack
        # ------------------------------------------------

        self.stack.addWidget(
            self.dashboard_page
        )

        self.stack.addWidget(
            self.intraday_page
        )

        self.stack.addWidget(
            self.swing_page
        )

        self.stack.addWidget(
            self.positional_page
        )

        self.stack.addWidget(
            self.market_page
        )

        self.stack.addWidget(
            self.settings_page
        )

        # ------------------------------------------------
        # Default Page
        # ------------------------------------------------

        self.stack.setCurrentWidget(
            self.dashboard_page
        )

    # ====================================================
    # CONNECT SIGNALS
    # ====================================================

    def _connect_signals(self):

        # ----------------------------------------
        # Sidebar Navigation
        # ----------------------------------------

        self.sidebar.dashboardClicked.connect(
            lambda: self.show_page("dashboard")
        )

        self.sidebar.intradayClicked.connect(
            lambda: self.show_page("intraday")
        )

        self.sidebar.swingClicked.connect(
            lambda: self.show_page("swing")
        )

        self.sidebar.positionalClicked.connect(
            lambda: self.show_page("positional")
        )

        self.sidebar.marketClicked.connect(
            lambda: self.show_page("market")
        )

        self.sidebar.settingsClicked.connect(
            lambda: self.show_page("settings")
        )

        # ----------------------------------------
        # Header
        # ----------------------------------------

        self.header.refreshRequested.connect(
            self.refresh_all
        )

        self.header.themeChanged.connect(
            self.toggle_theme
        )

        self.header.scanRequested.connect(
            self.start_manual_scan
        )

        # ----------------------------------------
        # Service Manager
        # ----------------------------------------

        self.container.service_manager.statusChanged.connect(
            self.status.show_message
        )

        self.container.service_manager.serviceStarted.connect(
            self.on_service_started
        )

        self.container.service_manager.serviceStopped.connect(
            self.on_service_stopped
        )

        self.container.service_manager.serviceFailed.connect(
            self.on_service_failed
        )

    # ====================================================
    # PAGE NAVIGATION
    # ====================================================

    def show_page(

        self,

        page_name: str

    ):

        pages = {

            "dashboard":
                self.dashboard_page,

            "intraday":
                self.intraday_page,

            "swing":
                self.swing_page,

            "positional":
                self.positional_page,

            "market":
                self.market_page,

            "settings":
                self.settings_page

        }

        page = pages.get(page_name)

        if page is None:

            return

        self.stack.setCurrentWidget(page)

        self.status.show_message(

            f"{page_name.title()} Page Loaded"

        )

    # ====================================================
    # REFRESH
    # ====================================================

    def refresh_all(self):

        try:

            self.container.application.full_refresh()

            self.status.show_message(

                "Refreshing Scanner..."

            )

        except Exception as e:

            self.status.show_message(

                str(e)

            )

    # ====================================================
    # MANUAL SCAN
    # ====================================================

    def start_manual_scan(self):

        try:

            self.container.application.manual_scan()

            self.status.show_message(

                "Manual Scan Started"

            )

        except Exception as e:

            self.status.show_message(

                str(e)

            )

    # ====================================================
    # THEME
    # ====================================================

    def load_theme(self):

        theme = self.config.theme()

        self.apply_theme(theme)

    def toggle_theme(self):

        current = self.config.theme()

        if current.lower() == "dark":

            self.apply_theme("Light")

        else:

            self.apply_theme("Dark")

    def apply_theme(

        self,

        theme: str

    ):

        self.config.set_theme(theme)

        self.setProperty(

            "theme",

            theme.lower()

        )

        QApplication.instance().setStyleSheet("")

        self.style().polish(self)

        self.status.show_message(

            f"{theme} Theme Activated"

        )

    # ====================================================
    # SERVICE EVENTS
    # ====================================================

    def on_service_started(

        self,

        service_name: str

    ):

        self.status.show_message(

            f"{service_name} Started"

        )

    def on_service_stopped(

        self,

        service_name: str

    ):

        self.status.show_message(

            f"{service_name} Stopped"

        )

    def on_service_failed(

        self,

        service_name: str

    ):

        self.status.show_message(

            f"{service_name} Failed"

        )

    # ====================================================
    # BUSY STATE
    # ====================================================

    def set_busy(

        self,

        busy: bool,

        message: str = ""

    ):

        QApplication.setOverrideCursor(

            Qt.WaitCursor

        ) if busy else QApplication.restoreOverrideCursor()

        if message:

            self.status.show_message(message)

        self.header.setEnabled(

            not busy

        )

        self.sidebar.setEnabled(

            not busy

        )

    # ====================================================
    # NOTIFICATION
    # ====================================================

    def notify(

        self,

        title: str,

        message: str

    ):

        self.status.show_message(

            f"{title}: {message}"

        )

        if hasattr(

            self.header,

            "show_notification"

        ):

            self.header.show_notification(

                title,

                message

            )

    # ====================================================
    # ERROR
    # ====================================================

    def show_error(

        self,

        message: str

    ):

        self.notify(

            "Error",

            message

        )

    # ====================================================
    # SUCCESS
    # ====================================================

    def show_success(

        self,

        message: str

    ):

        self.notify(

            "Success",

            message

        )

    # ====================================================
    # WARNING
    # ====================================================

    def show_warning(

        self,

        message: str

    ):

        self.notify(

            "Warning",

            message

        )

    # ====================================================
    # SAVE WINDOW STATE
    # ====================================================

    def save_window_state(self):

        try:

            geometry = self.saveGeometry().toBase64().data().decode()

            state = self.saveState().toBase64().data().decode()

            self.config.set(

                "window_geometry",

                geometry

            )

            self.config.set(

                "window_state",

                state

            )

            self.config.save()

        except Exception:

            pass

    # ====================================================
    # RESTORE WINDOW STATE
    # ====================================================

    def restore_window_state(self):

        try:

            geometry = self.config.get(

                "window_geometry"

            )

            state = self.config.get(

                "window_state"

            )

            if geometry:

                from PySide6.QtCore import QByteArray

                self.restoreGeometry(

                    QByteArray.fromBase64(

                        geometry.encode()

                    )

                )

            if state:

                from PySide6.QtCore import QByteArray

                self.restoreState(

                    QByteArray.fromBase64(

                        state.encode()

                    )

                )

        except Exception:

            pass

    # ====================================================
    # MAXIMIZE
    # ====================================================

    def maximize_window(self):

        if self.isMaximized():

            self.showNormal()

        else:

            self.showMaximized()

    # ====================================================
    # MINIMIZE
    # ====================================================

    def minimize_window(self):

        self.showMinimized()

    # ====================================================
    # FULLSCREEN
    # ====================================================

    def fullscreen(self):

        if self.isFullScreen():

            self.showNormal()

        else:

            self.showFullScreen()

    # ====================================================
    # CLOSE EVENT
    # ====================================================

    def closeEvent(

        self,

        event: QCloseEvent

    ):

        try:

            self.set_busy(

                True,

                "Closing Application..."

            )

            self.save_window_state()

            self.container.shutdown()

            self.status.show_message(

                "Shutdown Complete"

            )

        except Exception as e:

            self.show_error(

                str(e)

            )

        finally:

            QApplication.restoreOverrideCursor()

            event.accept()

    # ====================================================
    # MENU BAR
    # ====================================================

    def create_menu(self):

        menu = self.menuBar()

        # ----------------------------------------
        # File
        # ----------------------------------------

        file_menu = menu.addMenu("&File")

        refresh_action = QAction("Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(
            self.refresh_all
        )

        manual_scan_action = QAction(
            "Manual Scan",
            self
        )
        manual_scan_action.setShortcut(
            "Ctrl+S"
        )
        manual_scan_action.triggered.connect(
            self.start_manual_scan
        )

        exit_action = QAction(
            "Exit",
            self
        )
        exit_action.setShortcut(
            "Ctrl+Q"
        )
        exit_action.triggered.connect(
            self.close
        )

        file_menu.addAction(refresh_action)
        file_menu.addAction(manual_scan_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # ----------------------------------------
        # View
        # ----------------------------------------

        view_menu = menu.addMenu("&View")

        dashboard_action = QAction(
            "Dashboard",
            self
        )
        dashboard_action.triggered.connect(
            lambda: self.show_page(
                "dashboard"
            )
        )

        intraday_action = QAction(
            "Intraday",
            self
        )
        intraday_action.triggered.connect(
            lambda: self.show_page(
                "intraday"
            )
        )

        swing_action = QAction(
            "Swing",
            self
        )
        swing_action.triggered.connect(
            lambda: self.show_page(
                "swing"
            )
        )

        positional_action = QAction(
            "Positional",
            self
        )
        positional_action.triggered.connect(
            lambda: self.show_page(
                "positional"
            )
        )

        market_action = QAction(
            "Market",
            self
        )
        market_action.triggered.connect(
            lambda: self.show_page(
                "market"
            )
        )

        settings_action = QAction(
            "Settings",
            self
        )
        settings_action.triggered.connect(
            lambda: self.show_page(
                "settings"
            )
        )

        view_menu.addActions([
            dashboard_action,
            intraday_action,
            swing_action,
            positional_action,
            market_action,
            settings_action
        ])

        # ----------------------------------------
        # Tools
        # ----------------------------------------

        tools_menu = menu.addMenu("&Tools")

        diagnostics_action = QAction(
            "Diagnostics",
            self
        )

        diagnostics_action.triggered.connect(
            self.show_diagnostics
        )

        tools_menu.addAction(
            diagnostics_action
        )

        # ----------------------------------------
        # Help
        # ----------------------------------------

        help_menu = menu.addMenu("&Help")

        about_action = QAction(
            "About",
            self
        )

        about_action.triggered.connect(
            self.show_about
        )

        help_menu.addAction(
            about_action)

    # ====================================================
    # DIAGNOSTICS
    # ====================================================

    def show_diagnostics(self):

        diagnostics = (

            self.container.system_information()

        )

        self.status.show_message(

            "Diagnostics Generated"

        )

        return diagnostics

    # ====================================================
    # ABOUT
    # ====================================================

    def show_about(self):

        about = (
            "StockVersity Scanner Pro\n\n"
            "Version : 4.0\n"
            "Powered By : AI\n\n"
            "Professional Indian Stock Market Scanner\n\n"
            "Modules Included:\n"
            "â€¢ Intraday Scanner\n"
            "â€¢ Swing Scanner\n"
            "â€¢ Positional Scanner\n"
            "â€¢ AI Ranking Engine\n"
            "â€¢ Pattern Recognition\n"
            "â€¢ Sector Rotation\n"
            "â€¢ Risk Management"
        )

        self.notify(
            "About",
            about
        )

    # ====================================================
    # APPLICATION INFO
    # ====================================================

    @property
    def application_name(self):

        return "StockVersity Scanner Pro"

    @property
    def version(self):

        return "4.0"

    # ====================================================
    # STRING REPRESENTATION
    # ====================================================

    def __repr__(self):

        return (

            f"<MainWindow "

            f"application='{self.application_name}' "

            f"version='{self.version}'>"

        )


# ========================================================
# APPLICATION ENTRY
# ========================================================

def create_main_window():

    return MainWindow()


# ========================================================
# END OF FILE
# ========================================================
