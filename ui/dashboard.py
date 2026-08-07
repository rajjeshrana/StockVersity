from __future__ import annotations

"""
==========================================================
StockVersity Scanner Pro
Main Window

Author  : StockVersity
Version : 1.0.0

Responsibilities
----------------
• Main application window
• Menu bar
• Toolbar
• Sidebar
• Header
• Status bar
• Central stacked pages
• Theme integration
• Window persistence
• Service integration
==========================================================
"""

import logging

from pathlib import Path

from typing import Dict
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtCore import QSize
from PySide6.QtCore import QSettings

from PySide6.QtGui import QAction
from PySide6.QtGui import QCloseEvent
from PySide6.QtGui import QIcon
from PySide6.QtGui import QKeySequence

from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QSplitter
from PySide6.QtWidgets import QStackedWidget
from PySide6.QtWidgets import QStatusBar
from PySide6.QtWidgets import QToolBar
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QVBoxLayout

from services.service_container import (
    ServiceContainer,
)

from services.settings_service import (
    SettingsService,
)

from services.theme_service import (
    ThemeService,
)

from ui.layout.header import Header

from ui.layout.sidebar import Sidebar

from ui.layout.statusbar import StatusBar

# ==========================================================
# MAIN WINDOW
# ==========================================================

class MainWindow(QMainWindow):
    """
    Main application window.
    """

    ORGANIZATION = "StockVersity"

    APPLICATION = "Scanner Pro"

    VERSION = "1.0.0"

    DEFAULT_WIDTH = 1700

    DEFAULT_HEIGHT = 980

    # ======================================================
    # INITIALIZATION
    # ======================================================

    def __init__(
        self,
        services: ServiceContainer,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.logger = logging.getLogger(

            self.__class__.__name__

        )

        self.services = services

        self.settings: SettingsService = (

            services.settings

        )

        self.theme: ThemeService = (

            services.theme

        )

        self.qt_settings = QSettings(

            self.ORGANIZATION,

            self.APPLICATION,

        )

        self.pages: Dict[
            str,
            QWidget,
        ] = {}

        self._create_window()

        self._create_actions()

        self._create_toolbar()

        self._create_layout()

        self._create_statusbar()

        self._restore_geometry()

        self.logger.info(

            "MainWindow initialized."

        )
            # ======================================================
    # WINDOW
    # ======================================================

    def _create_window(
        self,
    ) -> None:
        """
        Configure the main application window.
        """

        self.setWindowTitle(

            f"StockVersity Scanner Pro "

            f"v{self.VERSION}"

        )

        self.resize(

            self.DEFAULT_WIDTH,

            self.DEFAULT_HEIGHT,

        )

        self.setMinimumSize(

            QSize(

                1400,

                850,

            )

        )

        icon_path = Path(

            "resources/icons/app.png"

        )

        if icon_path.exists():

            self.setWindowIcon(

                QIcon(

                    str(icon_path),

                )

            )

    # ======================================================
    # ACTIONS
    # ======================================================

    def _create_actions(
        self,
    ) -> None:
        """
        Create window actions.
        """

        # Dashboard

        self.dashboard_action = QAction(

            "Dashboard",

            self,

        )

        self.dashboard_action.triggered.connect(

            lambda: self.show_page(

                "dashboard",

            )

        )

        # Scanner

        self.scanner_action = QAction(

            "Scanner",

            self,

        )

        self.scanner_action.triggered.connect(

            lambda: self.show_page(

                "scanner",

            )

        )

        # Market

        self.market_action = QAction(

            "Market",

            self,

        )

        self.market_action.triggered.connect(

            lambda: self.show_page(

                "market",

            )

        )

        # Watchlist

        self.watchlist_action = QAction(

            "Watchlist",

            self,

        )

        self.watchlist_action.triggered.connect(

            lambda: self.show_page(

                "watchlist",

            )

        )

        # Alerts

        self.alert_action = QAction(

            "Alerts",

            self,

        )

        self.alert_action.triggered.connect(

            lambda: self.show_page(

                "alerts",

            )

        )

        # Settings

        self.settings_action = QAction(

            "Settings",

            self,

        )

        self.settings_action.triggered.connect(

            lambda: self.show_page(

                "settings",

            )

        )

        # Exit

        self.exit_action = QAction(

            "Exit",

            self,

        )

        self.exit_action.setShortcut(

            QKeySequence.Quit,

        )

        self.exit_action.triggered.connect(

            self.close,

        )

    # ======================================================
    # TOOLBAR
    # ======================================================

    def _create_toolbar(
        self,
    ) -> None:
        """
        Build application toolbar.
        """

        self.toolbar = QToolBar(

            "Main Toolbar",

            self,

        )

        self.toolbar.setMovable(

            False,

        )

        self.toolbar.setIconSize(

            QSize(

                20,

                20,

            )

        )

        self.addToolBar(

            Qt.TopToolBarArea,

            self.toolbar,

        )

        self.toolbar.addAction(

            self.dashboard_action,

        )

        self.toolbar.addAction(

            self.scanner_action,

        )

        self.toolbar.addAction(

            self.market_action,

        )

        self.toolbar.addAction(

            self.watchlist_action,

        )

        self.toolbar.addAction(

            self.alert_action,

        )

        self.toolbar.addSeparator()

        self.toolbar.addAction(

            self.settings_action,

        )

        self.toolbar.addSeparator()

        self.toolbar.addAction(

            self.exit_action,

        )

    # ======================================================
    # LAYOUT
    # ======================================================

    def _create_layout(
        self,
    ) -> None:
        """
        Build the main window layout.
        """

        self.central = QWidget()

        self.setCentralWidget(

            self.central,

        )

        self.root_layout = QVBoxLayout(

            self.central,

        )

        self.root_layout.setContentsMargins(

            0,

            0,

            0,

            0,

        )

        self.root_layout.setSpacing(

            0,

        )

        self.header = Header(

            self.services,

        )

        self.root_layout.addWidget(

            self.header,

        )

        self.splitter = QSplitter(

            Qt.Horizontal,

        )

        self.sidebar = Sidebar(

            self.services,

        )

        self.stack = QStackedWidget()

        self.splitter.addWidget(

            self.sidebar,

        )

        self.splitter.addWidget(

            self.stack,

        )

        self.splitter.setStretchFactor(

            0,

            0,

        )

        self.splitter.setStretchFactor(

            1,

            1,

        )

        self.root_layout.addWidget(

            self.splitter,

        )
            # ======================================================
    # MENU BAR
    # ======================================================

    def _create_menu_bar(
        self,
    ) -> None:
        """
        Create the application menu bar.
        """

        menu_bar = self.menuBar()

        # --------------------------------------------------
        # FILE
        # --------------------------------------------------

        file_menu = menu_bar.addMenu(
            "&File",
        )

        file_menu.addAction(
            self.dashboard_action,
        )

        file_menu.addSeparator()

        file_menu.addAction(
            self.settings_action,
        )

        file_menu.addSeparator()

        file_menu.addAction(
            self.exit_action,
        )

        # --------------------------------------------------
        # VIEW
        # --------------------------------------------------

        view_menu = menu_bar.addMenu(
            "&View",
        )

        view_menu.addAction(
            self.dashboard_action,
        )

        view_menu.addAction(
            self.scanner_action,
        )

        view_menu.addAction(
            self.market_action,
        )

        view_menu.addAction(
            self.watchlist_action,
        )

        view_menu.addAction(
            self.alert_action,
        )

        # --------------------------------------------------
        # TOOLS
        # --------------------------------------------------

        tools_menu = menu_bar.addMenu(
            "&Tools",
        )

        tools_menu.addAction(
            self.settings_action,
        )

        # --------------------------------------------------
        # HELP
        # --------------------------------------------------

        help_menu = menu_bar.addMenu(
            "&Help",
        )

        self.about_action = QAction(
            "About",
            self,
        )

        self.about_action.triggered.connect(
            self.show_about,
        )

        help_menu.addAction(
            self.about_action,
        )

    # ======================================================
    # STATUS BAR
    # ======================================================

    def _create_statusbar(
        self,
    ) -> None:
        """
        Create the application status bar.
        """

        self.statusbar = StatusBar(
            self.services,
        )

        self.setStatusBar(
            self.statusbar,
        )

        self.status_label = QLabel(
            "Ready",
        )

        self.statusBar().addPermanentWidget(
            self.status_label,
        )

    # ======================================================
    # PAGE MANAGEMENT
    # ======================================================

    def register_page(
        self,
        name: str,
        widget: QWidget,
    ) -> None:
        """
        Register a page.
        """

        if name in self.pages:

            self.logger.warning(

                "Page '%s' already exists.",

                name,

            )

            return

        self.pages[name] = widget

        self.stack.addWidget(
            widget,
        )

        self.logger.info(

            "Registered page: %s",

            name,

        )

    def unregister_page(
        self,
        name: str,
    ) -> bool:
        """
        Remove a registered page.
        """

        widget = self.pages.pop(
            name,
            None,
        )

        if widget is None:

            return False

        self.stack.removeWidget(
            widget,
        )

        widget.deleteLater()

        return True

    def page(
        self,
        name: str,
    ) -> Optional[QWidget]:
        """
        Return a registered page.
        """

        return self.pages.get(
            name,
        )

    def show_page(
        self,
        name: str,
    ) -> bool:
        """
        Display a registered page.
        """

        widget = self.page(
            name,
        )

        if widget is None:

            self.logger.warning(

                "Unknown page: %s",

                name,

            )

            return False

        self.stack.setCurrentWidget(
            widget,
        )

        self.status_label.setText(
            name.title(),
        )

        self._emit_page_changed(
            name,
        )

        return True

    def current_page(
        self,
    ) -> Optional[str]:
        """
        Return current page name.
        """

        current = self.stack.currentWidget()

        for name, widget in self.pages.items():

            if widget is current:

                return name

        return None

    # ======================================================
    # PAGE EVENTS
    # ======================================================

    def _emit_page_changed(
        self,
        page: str,
    ) -> None:
        """
        Notify dependent services that
        the active page has changed.
        """

        self.logger.info(

            "Page changed: %s",

            page,

        )

        self.statusBar().showMessage(

            f"{page.title()} loaded",

            2500,

        )

    # ======================================================
    # INITIALIZATION
    # ======================================================

    def initialize_ui(
        self,
    ) -> None:
        """
        Complete UI initialization.
        """

        self._create_menu_bar()

        self.theme.apply()

        self.logger.info(
            "UI initialized."
        )
            # ======================================================
    # SIDEBAR
    # ======================================================

    def connect_sidebar(
        self,
    ) -> None:
        """
        Connect sidebar navigation.
        """

        if hasattr(
            self.sidebar,
            "page_selected",
        ):

            self.sidebar.page_selected.connect(
                self.show_page,
            )

        if hasattr(
            self.sidebar,
            "theme_requested",
        ):

            self.sidebar.theme_requested.connect(
                self.toggle_theme,
            )

    # ======================================================
    # SHORTCUTS
    # ======================================================

    def setup_shortcuts(
        self,
    ) -> None:
        """
        Configure keyboard shortcuts.
        """

        self.dashboard_action.setShortcut(
            QKeySequence("Ctrl+1"),
        )

        self.scanner_action.setShortcut(
            QKeySequence("Ctrl+2"),
        )

        self.market_action.setShortcut(
            QKeySequence("Ctrl+3"),
        )

        self.watchlist_action.setShortcut(
            QKeySequence("Ctrl+4"),
        )

        self.alert_action.setShortcut(
            QKeySequence("Ctrl+5"),
        )

        self.settings_action.setShortcut(
            QKeySequence("Ctrl+,"),
        )

        self.about_action.setShortcut(
            QKeySequence("F1"),
        )

        self.logger.info(
            "Keyboard shortcuts initialized."
        )

    # ======================================================
    # THEME
    # ======================================================

    def toggle_theme(
        self,
    ) -> None:
        """
        Toggle between dark and light themes.
        """

        from services.theme_service import (
            ThemeMode,
        )

        if self.theme.current_mode() == ThemeMode.DARK:

            self.theme.set_mode(
                ThemeMode.LIGHT,
            )

        else:

            self.theme.set_mode(
                ThemeMode.DARK,
            )

        self.theme.apply(
            QApplication.instance(),
        )

        self.theme.save_configuration()

        self.statusBar().showMessage(

            "Theme updated",

            2000,

        )

    # ======================================================
    # WINDOW STATE
    # ======================================================

    def _restore_geometry(
        self,
    ) -> None:
        """
        Restore window geometry.
        """

        geometry = self.qt_settings.value(
            "geometry",
        )

        if geometry is not None:

            self.restoreGeometry(
                geometry,
            )

        state = self.qt_settings.value(
            "windowState",
        )

        if state is not None:

            self.restoreState(
                state,
            )

    def _save_geometry(
        self,
    ) -> None:
        """
        Save window geometry.
        """

        self.qt_settings.setValue(

            "geometry",

            self.saveGeometry(),

        )

        self.qt_settings.setValue(

            "windowState",

            self.saveState(),

        )

        self.qt_settings.sync()

    # ======================================================
    # WINDOW MODES
    # ======================================================

    def toggle_fullscreen(
        self,
    ) -> None:
        """
        Toggle full-screen mode.
        """

        if self.isFullScreen():

            self.showNormal()

        else:

            self.showFullScreen()

    def maximize(
        self,
    ) -> None:
        """
        Maximize the window.
        """

        self.showMaximized()

    def minimize(
        self,
    ) -> None:
        """
        Minimize the window.
        """

        self.showMinimized()

    def restore_window(
        self,
    ) -> None:
        """
        Restore the normal window.
        """

        self.showNormal()

    # ======================================================
    # PAGE HISTORY
    # ======================================================

    def remember_page(
        self,
        page: str,
    ) -> None:
        """
        Save last visited page.
        """

        self.qt_settings.setValue(

            "lastPage",

            page,

        )

    def restore_last_page(
        self,
    ) -> None:
        """
        Restore previously opened page.
        """

        page = self.qt_settings.value(

            "lastPage",

            "dashboard",

        )

        if page in self.pages:

            self.show_page(
                page,
            )

        else:

            self.show_page(
                "dashboard",
            )
                # ======================================================
    # STATUS
    # ======================================================

    def set_status(
        self,
        message: str,
        timeout: int = 3000,
    ) -> None:
        """
        Display a status message.
        """

        self.statusBar().showMessage(
            message,
            timeout,
        )

        self.status_label.setText(
            message,
        )

    # ======================================================
    # PROGRESS
    # ======================================================

    def show_progress(
        self,
        message: str = "Working...",
    ) -> None:
        """
        Enter busy state.
        """

        QApplication.setOverrideCursor(
            Qt.WaitCursor,
        )

        self.set_status(
            message,
            0,
        )

    def hide_progress(
        self,
    ) -> None:
        """
        Exit busy state.
        """

        QApplication.restoreOverrideCursor()

        self.set_status(
            "Ready",
        )

    # ======================================================
    # NOTIFICATIONS
    # ======================================================

    def notify(
        self,
        title: str,
        message: str,
    ) -> None:
        """
        Display a simple notification.
        """

        QMessageBox.information(

            self,

            title,

            message,

        )

    def notify_warning(
        self,
        title: str,
        message: str,
    ) -> None:
        """
        Display a warning.
        """

        QMessageBox.warning(

            self,

            title,

            message,

        )

    def notify_error(
        self,
        title: str,
        message: str,
    ) -> None:
        """
        Display an error dialog.
        """

        QMessageBox.critical(

            self,

            title,

            message,

        )

    # ======================================================
    # SERVICE EVENTS
    # ======================================================

    def connect_services(
        self,
    ) -> None:
        """
        Connect application services.
        """

        if hasattr(
            self.services.market,
            "register_event",
        ):

            self.services.market.register_event(

                "market_status_changed",

                self.on_market_status,

            )

        if hasattr(
            self.services.scanner,
            "register_event",
        ):

            self.services.scanner.register_event(

                "scan_completed",

                self.on_scan_completed,

            )

        if hasattr(
            self.services.alert,
            "register_event",
        ):

            self.services.alert.register_event(

                "alert_triggered",

                self.on_alert_triggered,

            )

        if hasattr(
            self.theme,
            "register_event",
        ):

            self.theme.register_event(

                "theme_changed",

                self.on_theme_changed,

            )

    # ======================================================
    # MARKET EVENTS
    # ======================================================

    def on_market_status(
        self,
        **kwargs,
    ) -> None:
        """
        Handle market status changes.
        """

        status = kwargs.get(
            "status",
            "Unknown",
        )

        self.set_status(

            f"Market: {status}",

        )

    # ======================================================
    # SCANNER EVENTS
    # ======================================================

    def on_scan_completed(
        self,
        **kwargs,
    ) -> None:
        """
        Handle completed scans.
        """

        total = kwargs.get(
            "results",
            0,
        )

        self.set_status(

            f"Scanner finished ({total} stocks)",

            5000,

        )

    # ======================================================
    # ALERT EVENTS
    # ======================================================

    def on_alert_triggered(
        self,
        **kwargs,
    ) -> None:
        """
        Handle alert notifications.
        """

        title = kwargs.get(
            "title",
            "Alert",
        )

        message = kwargs.get(
            "message",
            "",
        )

        self.notify(

            title,

            message,

        )

    # ======================================================
    # THEME EVENTS
    # ======================================================

    def on_theme_changed(
        self,
        **kwargs,
    ) -> None:
        """
        Handle theme changes.
        """

        self.theme.apply()

        self.set_status(

            "Theme updated",

            2000,

        )

    # ======================================================
    # STARTUP
    # ======================================================

    def initialize(
        self,
    ) -> None:
        """
        Complete window initialization.
        """

        self.initialize_ui()

        self.connect_sidebar()

        self.connect_services()

        self.setup_shortcuts()

        self.restore_last_page()

        self.set_status(
            "Ready",
        )

        self.logger.info(
            "Main window fully initialized."
        )
            # ======================================================
    # CLOSE EVENT
    # ======================================================

    def closeEvent(
        self,
        event: QCloseEvent,
    ) -> None:
        """
        Handle application close.
        """

        if not self.confirm_exit():

            event.ignore()

            return

        self.shutdown()

        self._save_geometry()

        event.accept()

    # ======================================================
    # EXIT CONFIRMATION
    # ======================================================

    def confirm_exit(
        self,
    ) -> bool:
        """
        Ask the user before closing.
        """

        reply = QMessageBox.question(

            self,

            "Exit",

            (
                "Are you sure you want to "
                "exit StockVersity Scanner Pro?"
            ),

            QMessageBox.Yes

            | QMessageBox.No,

            QMessageBox.No,

        )

        return reply == QMessageBox.Yes

    # ======================================================
    # STARTUP
    # ======================================================

    def startup(
        self,
    ) -> None:
        """
        Start application services.
        """

        self.logger.info(
            "Starting application..."
        )

        try:

            self.services.start_all()

        except Exception:

            self.logger.exception(
                "Failed to start services."
            )

        self.set_status(
            "Application started.",
        )

    # ======================================================
    # SHUTDOWN
    # ======================================================

    def shutdown(
        self,
    ) -> None:
        """
        Shutdown application services.
        """

        self.logger.info(
            "Stopping application..."
        )

        try:

            self.services.stop_all()

        except Exception:

            self.logger.exception(
                "Failed to stop services."
            )

        self.set_status(
            "Application stopped.",
        )

    # ======================================================
    # RESTART
    # ======================================================

    def restart_services(
        self,
    ) -> None:
        """
        Restart every registered service.
        """

        try:

            self.services.restart_all()

            self.set_status(

                "Services restarted.",

                3000,

            )

        except Exception:

            self.logger.exception(

                "Unable to restart services."

            )

    # ======================================================
    # SESSION
    # ======================================================

    def save_session(
        self,
    ) -> None:
        """
        Save current session.
        """

        self.remember_page(

            self.current_page()

            or

            "dashboard",

        )

        self._save_geometry()

    def restore_session(
        self,
    ) -> None:
        """
        Restore previous session.
        """

        self._restore_geometry()

        self.restore_last_page()

    # ======================================================
    # LOGGING
    # ======================================================

    def log_info(
        self,
        message: str,
    ) -> None:
        """
        Log an information message.
        """

        self.logger.info(
            message,
        )

    def log_warning(
        self,
        message: str,
    ) -> None:
        """
        Log a warning.
        """

        self.logger.warning(
            message,
        )

    def log_error(
        self,
        message: str,
    ) -> None:
        """
        Log an error.
        """

        self.logger.error(
            message,
        )

    # ======================================================
    # EXCEPTION HANDLER
    # ======================================================

    def handle_exception(
        self,
        exception: Exception,
    ) -> None:
        """
        Handle unexpected exceptions.
        """

        self.logger.exception(
            exception,
        )

        self.notify_error(

            "Unexpected Error",

            str(exception),

        )

    # ======================================================
    # REFRESH
    # ======================================================

    def refresh(
        self,
    ) -> None:
        """
        Refresh the active page.
        """

        widget = self.stack.currentWidget()

        if (

            widget is not None

            and

            hasattr(

                widget,

                "refresh",

            )

        ):

            widget.refresh()

        self.set_status(

            "Refreshed.",

            1500,

        )
            # ======================================================
    # NAVIGATION
    # ======================================================

    def next_page(
        self,
    ) -> None:
        """
        Navigate to the next page.
        """

        count = self.stack.count()

        if count == 0:

            return

        index = (

            self.stack.currentIndex()

            + 1

        ) % count

        self.stack.setCurrentIndex(
            index,
        )

        self.set_status(
            f"Page {index + 1}/{count}",
            1500,
        )

    def previous_page(
        self,
    ) -> None:
        """
        Navigate to the previous page.
        """

        count = self.stack.count()

        if count == 0:

            return

        index = (

            self.stack.currentIndex()

            - 1

        ) % count

        self.stack.setCurrentIndex(
            index,
        )

        self.set_status(
            f"Page {index + 1}/{count}",
            1500,
        )

    def page_names(
        self,
    ) -> list[str]:
        """
        Return registered page names.
        """

        return sorted(
            self.pages.keys(),
        )

    # ======================================================
    # PAGE CACHE
    # ======================================================

    def has_page(
        self,
        name: str,
    ) -> bool:
        """
        Return True if page exists.
        """

        return name in self.pages

    def page_count(
        self,
    ) -> int:
        """
        Return registered page count.
        """

        return len(
            self.pages,
        )

    # ======================================================
    # SPLITTER
    # ======================================================

    def collapse_sidebar(
        self,
    ) -> None:
        """
        Collapse sidebar.
        """

        self.splitter.setSizes(

            [

                0,

                1,

            ]

        )

    def expand_sidebar(
        self,
    ) -> None:
        """
        Expand sidebar.
        """

        self.splitter.setSizes(

            [

                260,

                1400,

            ]

        )

    def toggle_sidebar(
        self,
    ) -> None:
        """
        Toggle sidebar visibility.
        """

        sizes = self.splitter.sizes()

        if sizes[0] == 0:

            self.expand_sidebar()

        else:

            self.collapse_sidebar()

    # ======================================================
    # SERVICE HELPERS
    # ======================================================

    def service_status(
        self,
    ) -> Dict[str, bool]:
        """
        Return service availability.
        """

        return {

            "settings":
                self.settings is not None,

            "theme":
                self.theme is not None,

            "scanner":
                getattr(
                    self.services,
                    "scanner",
                    None,
                )
                is not None,

            "market":
                getattr(
                    self.services,
                    "market",
                    None,
                )
                is not None,

            "watchlist":
                getattr(
                    self.services,
                    "watchlist",
                    None,
                )
                is not None,

            "alerts":
                getattr(
                    self.services,
                    "alert",
                    None,
                )
                is not None,

        }

    # ======================================================
    # THEME HELPERS
    # ======================================================

    def reload_theme(
        self,
    ) -> None:
        """
        Reload and apply the active theme.
        """

        self.theme.load_configuration()

        self.theme.apply()

        self.set_status(

            "Theme reloaded.",

            2000,

        )

    # ======================================================
    # DIAGNOSTICS
    # ======================================================

    def diagnostics(
        self,
    ) -> Dict[str, object]:
        """
        Return runtime diagnostics.
        """

        return {

            "window":

                self.windowTitle(),

            "current_page":

                self.current_page(),

            "pages":

                self.page_names(),

            "service_status":

                self.service_status(),

            "fullscreen":

                self.isFullScreen(),

            "maximized":

                self.isMaximized(),

            "visible":

                self.isVisible(),

        }

    # ======================================================
    # INFORMATION
    # ======================================================

    def info(
        self,
    ) -> Dict[str, object]:
        """
        Return window information.
        """

        return {

            "application":

                self.APPLICATION,

            "version":

                self.VERSION,

            "organization":

                self.ORGANIZATION,

            "size":

                {

                    "width":

                        self.width(),

                    "height":

                        self.height(),

                },

            "page_count":

                self.page_count(),

        }
        # ======================================================
    # SNAPSHOT
    # ======================================================

    def snapshot(
        self,
    ) -> Dict[str, object]:
        """
        Return current window snapshot.
        """

        return {

            "application":

                self.APPLICATION,

            "version":

                self.VERSION,

            "window":

                {

                    "title":

                        self.windowTitle(),

                    "width":

                        self.width(),

                    "height":

                        self.height(),

                    "x":

                        self.x(),

                    "y":

                        self.y(),

                    "visible":

                        self.isVisible(),

                    "maximized":

                        self.isMaximized(),

                    "fullscreen":

                        self.isFullScreen(),

                },

            "current_page":

                self.current_page(),

            "pages":

                self.page_names(),

            "services":

                self.service_status(),

            "theme":

                {

                    "mode":

                        self.theme.current_mode().value,

                    "accent":

                        self.theme.accent_color().value,

                },

        }

    # ======================================================
    # DUMP
    # ======================================================

    def dump(
        self,
    ) -> Dict[str, object]:
        """
        Dump complete runtime state.
        """

        return {

            "info":

                self.info(),

            "snapshot":

                self.snapshot(),

            "diagnostics":

                self.diagnostics(),

        }

    # ======================================================
    # UTILITIES
    # ======================================================

    def clear_status(
        self,
    ) -> None:
        """
        Clear status message.
        """

        self.statusBar().clearMessage()

        self.status_label.setText(
            "Ready",
        )

    def update_title(
        self,
        suffix: str = "",
    ) -> None:
        """
        Update window title.
        """

        title = (

            f"StockVersity Scanner Pro "

            f"v{self.VERSION}"

        )

        if suffix:

            title = f"{title} - {suffix}"

        self.setWindowTitle(
            title,
        )

    def activate(
        self,
    ) -> None:
        """
        Bring window to front.
        """

        self.raise_()

        self.activateWindow()

    # ======================================================
    # FACTORY
    # ======================================================

    @classmethod
    def create(
        cls,
        services: ServiceContainer,
    ) -> "MainWindow":
        """
        Factory constructor.
        """

        window = cls(
            services,
        )

        window.initialize()

        return window

    # ======================================================
    # REPRESENTATION
    # ======================================================

    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"page={self.current_page()}, "

            f"pages={self.page_count()}, "

            f"size={self.width()}x{self.height()})"

        )

    def __str__(
        self,
    ) -> str:

        return (

            f"{self.APPLICATION} "

            f"v{self.VERSION}"

        )

    # ======================================================
    # CONTEXT MANAGER
    # ======================================================

    def __enter__(
        self,
    ) -> "MainWindow":
        """
        Context manager entry.
        """

        self.startup()

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        """
        Context manager exit.
        """

        self.shutdown()
            # ======================================================
    # ABOUT
    # ======================================================

    def show_about(
        self,
    ) -> None:
        """
        Display the About dialog.
        """

        QMessageBox.about(

            self,

            "About StockVersity Scanner Pro",

            (
                f"<h2>{self.APPLICATION}</h2>"

                f"<p><b>Version:</b> {self.VERSION}</p>"

                "<p>Professional Indian Stock Market "

                "Scanner built with Python & PySide6.</p>"

                "<p>Features include:</p>"

                "<ul>"

                "<li>Intraday Scanner</li>"

                "<li>Swing Scanner</li>"

                "<li>Market Dashboard</li>"

                "<li>Watchlists</li>"

                "<li>Alerts</li>"

                "<li>Technical Analysis</li>"

                "</ul>"

                "<p>© StockVersity</p>"

            ),

        )

    # ======================================================
    # HELP
    # ======================================================

    def open_documentation(
        self,
    ) -> None:
        """
        Placeholder for documentation.
        """

        self.notify(

            "Documentation",

            "Documentation will be available "

            "in a future release.",

        )

    def report_issue(
        self,
    ) -> None:
        """
        Placeholder for issue reporting.
        """

        self.notify(

            "Report Issue",

            "Issue reporting is not yet "

            "implemented.",

        )

    # ======================================================
    # DEBUG
    # ======================================================

    def debug_info(
        self,
    ) -> Dict[str, object]:
        """
        Return debugging information.
        """

        return {

            "window":

                self.dump(),

            "theme":

                self.theme.snapshot(),

            "settings":

                self.settings.snapshot(),

            "services":

                self.service_status(),

        }

    def print_debug_info(
        self,
    ) -> None:
        """
        Print debug information.
        """

        import pprint

        pprint.pprint(

            self.debug_info(),

        )

    # ======================================================
    # VALIDATION
    # ======================================================

    def validate(
        self,
    ) -> bool:
        """
        Validate the main window.
        """

        if self.stack is None:

            return False

        if self.sidebar is None:

            return False

        if self.header is None:

            return False

        if self.statusbar is None:

            return False

        return True

    def assert_valid(
        self,
    ) -> None:
        """
        Raise if the window is invalid.
        """

        if not self.validate():

            raise RuntimeError(

                "MainWindow validation failed."

            )

    # ======================================================
    # UTILITIES
    # ======================================================

    def enable_ui(
        self,
    ) -> None:
        """
        Enable the user interface.
        """

        self.setEnabled(
            True,
        )

    def disable_ui(
        self,
    ) -> None:
        """
        Disable the user interface.
        """

        self.setEnabled(
            False,
        )

    def center_window(
        self,
    ) -> None:
        """
        Center the window on screen.
        """

        screen = self.screen()

        if screen is None:

            return

        geometry = screen.availableGeometry()

        frame = self.frameGeometry()

        frame.moveCenter(

            geometry.center(),

        )

        self.move(

            frame.topLeft(),

        )

    # ======================================================
    # PAGE UTILITIES
    # ======================================================

    def refresh_all_pages(
        self,
    ) -> None:
        """
        Refresh every registered page.
        """

        for page in self.pages.values():

            if hasattr(

                page,

                "refresh",

            ):

                try:

                    page.refresh()

                except Exception:

                    self.logger.exception(

                        "Unable to refresh page."

                    )

    def page_exists(
        self,
        name: str,
    ) -> bool:
        """
        Return True if page exists.
        """

        return name in self.pages
        # ======================================================
    # APPLICATION HELPERS
    # ======================================================

    def show_dashboard(
        self,
    ) -> None:
        """
        Show dashboard page.
        """

        self.show_page(
            "dashboard",
        )

    def show_scanner(
        self,
    ) -> None:
        """
        Show scanner page.
        """

        self.show_page(
            "scanner",
        )

    def show_market(
        self,
    ) -> None:
        """
        Show market page.
        """

        self.show_page(
            "market",
        )

    def show_watchlist(
        self,
    ) -> None:
        """
        Show watchlist page.
        """

        self.show_page(
            "watchlist",
        )

    def show_alerts(
        self,
    ) -> None:
        """
        Show alerts page.
        """

        self.show_page(
            "alerts",
        )

    def show_settings(
        self,
    ) -> None:
        """
        Show settings page.
        """

        self.show_page(
            "settings",
        )

    # ======================================================
    # APPLICATION STATE
    # ======================================================

    def is_ready(
        self,
    ) -> bool:
        """
        Return True if the window is ready.
        """

        return (

            self.validate()

            and

            self.page_count() > 0

        )

    def wait_cursor(
        self,
        enabled: bool,
    ) -> None:
        """
        Toggle wait cursor.
        """

        if enabled:

            QApplication.setOverrideCursor(
                Qt.WaitCursor,
            )

        else:

            QApplication.restoreOverrideCursor()

    # ======================================================
    # FINALIZE
    # ======================================================

    def finalize(
        self,
    ) -> None:
        """
        Perform final initialization.
        """

        self.assert_valid()

        self.logger.info(

            "MainWindow finalized."

        )


# ==========================================================
# FACTORY HELPERS
# ==========================================================

def create_main_window(
    services: ServiceContainer,
) -> MainWindow:
    """
    Convenience factory.
    """

    return MainWindow.create(
        services,
    )


def build_main_window(
    services: ServiceContainer,
) -> MainWindow:
    """
    Alternate factory helper.
    """

    return MainWindow(
        services,
    )


# ==========================================================
# MODULE EXPORTS
# ==========================================================

__all__ = [

    "MainWindow",

    "create_main_window",

    "build_main_window",

]

# ==========================================================
# END OF FILE
# ==========================================================