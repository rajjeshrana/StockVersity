"""
=========================================================
StockVersity Scanner Pro
Sidebar Navigation
Version : 4.0
Powered By : AI
=========================================================
"""

from __future__ import annotations

from PySide6.QtCore import (
    Qt,
    Signal,
    QEasingCurve,
    QPropertyAnimation,
)

from PySide6.QtGui import QFont

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QFrame,
    QSpacerItem,
)


class Sidebar(QWidget):

    # ============================================
    # Signals
    # ============================================

    dashboardClicked = Signal()

    intradayClicked = Signal()

    swingClicked = Signal()

    positionalClicked = Signal()

    marketClicked = Signal()

    settingsClicked = Signal()

    refreshClicked = Signal()

    scanClicked = Signal()

    collapseChanged = Signal(bool)

    # ============================================
    # Init
    # ============================================

    def __init__(self):

        super().__init__()

        self.expanded_width = 260

        self.collapsed_width = 70

        self.expanded = True

        self.current_button = None

        self.setObjectName("Sidebar")

        self.setMinimumWidth(
            self.expanded_width
        )

        self.setMaximumWidth(
            self.expanded_width
        )

        self.build_ui()

    # ============================================
    # Build UI
    # ============================================

    def build_ui(self):

        self.main_layout = QVBoxLayout(self)

        self.main_layout.setContentsMargins(
            12,
            15,
            12,
            15
        )

        self.main_layout.setSpacing(12)

        self.create_logo()

        self.create_navigation()

        self.main_layout.addStretch()

        self.create_quick_actions()

        self.create_status_panel()

    # ============================================
    # Logo
    # ============================================

    def create_logo(self):

        frame = QFrame()

        layout = QVBoxLayout(frame)

        layout.setContentsMargins(
            8,
            8,
            8,
            8
        )

        self.logo = QLabel("📈")

        self.logo.setAlignment(
            Qt.AlignCenter
        )

        font = QFont()

        font.setPointSize(26)

        self.logo.setFont(font)

        self.title = QLabel(
            "StockVersity"
        )

        self.title.setAlignment(
            Qt.AlignCenter
        )

        title_font = QFont()

        title_font.setPointSize(14)

        title_font.setBold(True)

        self.title.setFont(
            title_font
        )

        self.subtitle = QLabel(
            "Scanner Pro"
        )

        self.subtitle.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            self.logo
        )

        layout.addWidget(
            self.title
        )

        layout.addWidget(
            self.subtitle
        )

        self.main_layout.addWidget(
            frame
        )

    # ============================================
    # Navigation
    # ============================================

    def create_navigation(self):

        self.dashboard_button = self.create_button(
            "🏠 Dashboard"
        )

        self.intraday_button = self.create_button(
            "⚡ Intraday"
        )

        self.swing_button = self.create_button(
            "📊 Swing"
        )

        self.positional_button = self.create_button(
            "📅 Positional"
        )

        self.market_button = self.create_button(
            "🌐 Market"
        )

        self.settings_button = self.create_button(
            "⚙ Settings"
        )

        self.main_layout.addWidget(
            self.dashboard_button
        )

        self.main_layout.addWidget(
            self.intraday_button
        )

        self.main_layout.addWidget(
            self.swing_button
        )

        self.main_layout.addWidget(
            self.positional_button
        )

        self.main_layout.addWidget(
            self.market_button
        )

        self.main_layout.addWidget(
            self.settings_button
        )

        self.dashboard_button.clicked.connect(
            self.dashboardClicked
        )

        self.intraday_button.clicked.connect(
            self.intradayClicked
        )

        self.swing_button.clicked.connect(
            self.swingClicked
        )

        self.positional_button.clicked.connect(
            self.positionalClicked
        )

        self.market_button.clicked.connect(
            self.marketClicked
        )

        self.settings_button.clicked.connect(
            self.settingsClicked
        )

        self.set_active_button(
            self.dashboard_button
        )

    # ============================================
    # Create Button
    # ============================================

    def create_button(

        self,

        text: str

    ):

        button = QPushButton(text)

        button.setMinimumHeight(48)

        button.setCursor(
            Qt.PointingHandCursor
        )

        button.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        return button
        # ============================================
    # Quick Actions
    # ============================================

    def create_quick_actions(self):

        frame = QFrame()

        layout = QVBoxLayout(frame)

        layout.setContentsMargins(0, 0, 0, 0)

        layout.setSpacing(8)

        self.refresh_button = self.create_button(
            "🔄 Refresh"
        )

        self.scan_button = self.create_button(
            "🚀 Scan Now"
        )

        layout.addWidget(
            self.refresh_button
        )

        layout.addWidget(
            self.scan_button
        )

        self.refresh_button.clicked.connect(
            self.refreshClicked
        )

        self.scan_button.clicked.connect(
            self.scanClicked
        )

        self.main_layout.addWidget(frame)

    # ============================================
    # Status Panel
    # ============================================

    def create_status_panel(self):

        self.status_frame = QFrame()

        layout = QVBoxLayout(self.status_frame)

        layout.setContentsMargins(
            10,
            10,
            10,
            10
        )

        self.market_status = QLabel(
            "🟢 Market Open"
        )

        self.market_status.setAlignment(
            Qt.AlignCenter
        )

        self.scanner_status = QLabel(
            "Scanner Ready"
        )

        self.scanner_status.setAlignment(
            Qt.AlignCenter
        )

        self.connection_status = QLabel(
            "Connected"
        )

        self.connection_status.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            self.market_status
        )

        layout.addWidget(
            self.scanner_status
        )

        layout.addWidget(
            self.connection_status
        )

        self.main_layout.addWidget(
            self.status_frame
        )

    # ============================================
    # Active Button
    # ============================================

    def set_active_button(

        self,

        button: QPushButton

    ):

        if self.current_button:

            self.current_button.setProperty(

                "active",

                False

            )

            self.current_button.style().unpolish(

                self.current_button

            )

            self.current_button.style().polish(

                self.current_button

            )

        self.current_button = button

        self.current_button.setProperty(

            "active",

            True

        )

        self.current_button.style().unpolish(

            self.current_button

        )

        self.current_button.style().polish(

            self.current_button

        )

    # ============================================
    # Collapse / Expand
    # ============================================

    def toggle_sidebar(self):

        self.expanded = not self.expanded

        target_width = (

            self.expanded_width

            if self.expanded

            else self.collapsed_width

        )

        self.animation = QPropertyAnimation(

            self,

            b"minimumWidth"

        )

        self.animation.setDuration(250)

        self.animation.setStartValue(

            self.width()

        )

        self.animation.setEndValue(

            target_width

        )

        self.animation.setEasingCurve(

            QEasingCurve.OutCubic

        )

        self.animation.start()

        self.setMaximumWidth(

            target_width

        )

        self.update_button_texts()

        self.collapseChanged.emit(

            self.expanded

        )

    # ============================================
    # Update Button Text
    # ============================================

    def update_button_texts(self):

        if self.expanded:

            self.dashboard_button.setText(
                "🏠 Dashboard"
            )

            self.intraday_button.setText(
                "⚡ Intraday"
            )

            self.swing_button.setText(
                "📊 Swing"
            )

            self.positional_button.setText(
                "📅 Positional"
            )

            self.market_button.setText(
                "🌐 Market"
            )

            self.settings_button.setText(
                "⚙ Settings"
            )

            self.refresh_button.setText(
                "🔄 Refresh"
            )

            self.scan_button.setText(
                "🚀 Scan Now"
            )

            self.title.show()

            self.subtitle.show()

        else:

            self.dashboard_button.setText("🏠")

            self.intraday_button.setText("⚡")

            self.swing_button.setText("📊")

            self.positional_button.setText("📅")

            self.market_button.setText("🌐")

            self.settings_button.setText("⚙")

            self.refresh_button.setText("🔄")

            self.scan_button.setText("🚀")

            self.title.hide()

            self.subtitle.hide()

    # ============================================
    # Market Status
    # ============================================

    def set_market_status(

        self,

        is_open: bool

    ):

        if is_open:

            self.market_status.setText(

                "🟢 Market Open"

            )

        else:

            self.market_status.setText(

                "🔴 Market Closed"

            )

    # ============================================
    # Scanner Status
    # ============================================

    def set_scanner_status(

        self,

        status: str

    ):

        self.scanner_status.setText(

            status

        )

    # ============================================
    # Connection Status
    # ============================================

    def set_connection_status(

        self,

        connected: bool

    ):

        if connected:

            self.connection_status.setText(

                "Connected"

            )

        else:

            self.connection_status.setText(

                "Disconnected"

            )
                # ============================================
    # Navigation Selection
    # ============================================

    def select_dashboard(self):

        self.set_active_button(
            self.dashboard_button
        )

        self.dashboardClicked.emit()

    def select_intraday(self):

        self.set_active_button(
            self.intraday_button
        )

        self.intradayClicked.emit()

    def select_swing(self):

        self.set_active_button(
            self.swing_button
        )

        self.swingClicked.emit()

    def select_positional(self):

        self.set_active_button(
            self.positional_button
        )

        self.positionalClicked.emit()

    def select_market(self):

        self.set_active_button(
            self.market_button
        )

        self.marketClicked.emit()

    def select_settings(self):

        self.set_active_button(
            self.settings_button
        )

        self.settingsClicked.emit()

    # ============================================
    # User Profile
    # ============================================

    def create_user_profile(self):

        self.profile_frame = QFrame()

        layout = QVBoxLayout(
            self.profile_frame
        )

        layout.setContentsMargins(
            8,
            8,
            8,
            8
        )

        self.user_avatar = QLabel("👤")

        avatar_font = QFont()

        avatar_font.setPointSize(28)

        self.user_avatar.setFont(
            avatar_font
        )

        self.user_avatar.setAlignment(
            Qt.AlignCenter
        )

        self.user_name = QLabel(
            "Trader"
        )

        self.user_name.setAlignment(
            Qt.AlignCenter
        )

        self.user_role = QLabel(
            "Professional"
        )

        self.user_role.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            self.user_avatar
        )

        layout.addWidget(
            self.user_name
        )

        layout.addWidget(
            self.user_role
        )

        self.main_layout.insertWidget(
            1,
            self.profile_frame
        )

    # ============================================
    # Hover State
    # ============================================

    def enterEvent(self, event):

        self.setProperty(
            "hover",
            True
        )

        self.style().unpolish(
            self
        )

        self.style().polish(
            self
        )

        super().enterEvent(event)

    def leaveEvent(self, event):

        self.setProperty(
            "hover",
            False
        )

        self.style().unpolish(
            self
        )

        self.style().polish(
            self
        )

        super().leaveEvent(event)

    # ============================================
    # Keyboard Navigation
    # ============================================

    def keyPressEvent(self, event):

        key = event.key()

        if key == Qt.Key_1:

            self.select_dashboard()

        elif key == Qt.Key_2:

            self.select_intraday()

        elif key == Qt.Key_3:

            self.select_swing()

        elif key == Qt.Key_4:

            self.select_positional()

        elif key == Qt.Key_5:

            self.select_market()

        elif key == Qt.Key_6:

            self.select_settings()

        elif key == Qt.Key_Space:

            self.toggle_sidebar()

        else:

            super().keyPressEvent(
                event
            )

    # ============================================
    # Theme
    # ============================================

    def apply_theme(

        self,

        theme: str

    ):

        self.setProperty(

            "theme",

            theme.lower()

        )

        self.style().unpolish(
            self
        )

        self.style().polish(
            self
        )

    # ============================================
    # Runtime Status
    # ============================================

    def update_runtime_status(

        self,

        market_open: bool,

        scanner_status: str,

        connected: bool

    ):

        self.set_market_status(
            market_open
        )

        self.set_scanner_status(
            scanner_status
        )

        self.set_connection_status(
            connected
        )

    # ============================================
    # Animation Finished
    # ============================================

    def on_animation_finished(self):

        self.update()

        self.repaint()

    # ============================================
    # Expand
    # ============================================

    def expand(self):

        if not self.expanded:

            self.toggle_sidebar()

    # ============================================
    # Collapse
    # ============================================

    def collapse(self):

        if self.expanded:

            self.toggle_sidebar()

    # ============================================
    # Expanded State
    # ============================================

    def is_expanded(self):

        return self.expanded

    # ============================================
    # Width
    # ============================================

    def sidebar_width(self):

        return self.width()
        # ============================================
    # Refresh
    # ============================================

    def refresh(self):

        self.refreshClicked.emit()

    # ============================================
    # Scan
    # ============================================

    def scan(self):

        self.scanClicked.emit()

    # ============================================
    # Update User
    # ============================================

    def set_user(

        self,

        name: str,

        role: str = "Professional"

    ):

        if hasattr(self, "user_name"):

            self.user_name.setText(name)

            self.user_role.setText(role)

    # ============================================
    # Reset Sidebar
    # ============================================

    def reset(self):

        self.set_active_button(

            self.dashboard_button

        )

        self.set_market_status(False)

        self.set_scanner_status(

            "Idle"

        )

        self.set_connection_status(False)

    # ============================================
    # Enable Navigation
    # ============================================

    def enable_navigation(

        self,

        enabled: bool = True

    ):

        buttons = [

            self.dashboard_button,

            self.intraday_button,

            self.swing_button,

            self.positional_button,

            self.market_button,

            self.settings_button,

            self.refresh_button,

            self.scan_button

        ]

        for button in buttons:

            button.setEnabled(enabled)

    # ============================================
    # Runtime Information
    # ============================================

    def runtime_information(self):

        return {

            "expanded":

                self.expanded,

            "width":

                self.width(),

            "current_page":

                self.current_button.text()

                if self.current_button

                else None,

            "market_status":

                self.market_status.text(),

            "scanner_status":

                self.scanner_status.text(),

            "connection":

                self.connection_status.text()

        }

    # ============================================
    # Diagnostics
    # ============================================

    def diagnostics(self):

        return {

            "widget":

                "Sidebar",

            "runtime":

                self.runtime_information()

        }

    # ============================================
    # Build Information
    # ============================================

    @property
    def application(self):

        return "StockVersity Scanner Pro"

    @property
    def version(self):

        return "4.0"

    def build_information(self):

        return {

            "application":

                self.application,

            "version":

                self.version,

            "component":

                "Sidebar"

        }

    # ============================================
    # Public API
    # ============================================

    def refresh_status(

        self,

        market_open: bool,

        scanner_status: str,

        connected: bool

    ):

        self.update_runtime_status(

            market_open,

            scanner_status,

            connected

        )

    # ============================================
    # String Representation
    # ============================================

    def __repr__(self):

        page = (

            self.current_button.text()

            if self.current_button

            else "None"

        )

        return (

            f"<Sidebar "

            f"expanded={self.expanded} "

            f"page='{page}'>"

        )


# ============================================
# Factory
# ============================================

def create_sidebar():

    return Sidebar()


# ============================================
# END OF FILE
# ============================================