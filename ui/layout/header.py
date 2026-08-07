"""
=========================================================
StockVersity Scanner Pro
Professional Trading Header
Version : 4.0
Powered By : AI
=========================================================
"""

from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import (
    Qt,
    QTimer,
    Signal
)

from PySide6.QtGui import (
    QAction,
    QFont
)

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QLineEdit,
    QSizePolicy,
    QFrame,
)


class Header(QWidget):

    # ====================================================
    # Signals
    # ====================================================

    refreshRequested = Signal()

    scanRequested = Signal()

    themeChanged = Signal()

    searchRequested = Signal(str)

    notificationClicked = Signal()

    userMenuClicked = Signal()

    # ====================================================
    # Init
    # ====================================================

    def __init__(self):

        super().__init__()

        self.market_data = {}

        self.create_notification_center()

        self.build_ui()

        self.start_clock()

    # ====================================================
    # Build UI
    # ====================================================

    def build_ui(self):

        self.setMinimumHeight(80)

        self.setMaximumHeight(80)

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            15,
            10,
            15,
            10
        )

        layout.setSpacing(12)

        # --------------------------------------------
        # Left
        # --------------------------------------------

        left = QHBoxLayout()

        self.market_status = QLabel(
            "ðŸŸ¢ MARKET OPEN"
        )

        font = QFont()

        font.setBold(True)

        font.setPointSize(10)

        self.market_status.setFont(font)

        self.clock = QLabel()

        left.addWidget(
            self.market_status
        )

        left.addSpacing(15)

        left.addWidget(
            self.clock
        )

        left_widget = QWidget()

        left_widget.setLayout(left)

        layout.addWidget(
            left_widget
        )

        # --------------------------------------------
        # Center
        # --------------------------------------------

        center = QHBoxLayout()

        self.search = QLineEdit()

        self.search.setPlaceholderText(

            "Search NSE Symbol..."

        )

        self.search.returnPressed.connect(

            self.search_symbol

        )

        center.addWidget(

            self.search

        )

        center_widget = QWidget()

        center_widget.setLayout(center)

        center_widget.setSizePolicy(

            QSizePolicy.Expanding,

            QSizePolicy.Preferred

        )

        layout.addWidget(

            center_widget,

            1

        )

        # --------------------------------------------
        # Right
        # --------------------------------------------

        right = QHBoxLayout()

        self.ai_status = QLabel(

            "ðŸ¤– AI Ready"

        )

        self.refresh_button = QPushButton(

            "ðŸ”„"

        )

        self.scan_button = QPushButton(

            "â–¶"

        )

        self.theme_button = QPushButton(

            "ðŸŒ™"

        )

        self.notification_button = QPushButton(

            "ðŸ””"

        )

        self.user_button = QPushButton(

            "ðŸ‘¤"

        )

        right.addWidget(

            self.ai_status

        )

        right.addSpacing(8)

        right.addWidget(

            self.refresh_button

        )

        right.addWidget(

            self.scan_button

        )

        right.addWidget(

            self.theme_button

        )

        right.addWidget(

            self.notification_button

        )

        right.addWidget(

            self.user_button

        )

        right_widget = QWidget()

        right_widget.setLayout(right)

        layout.addWidget(

            right_widget

        )

        self.connect_signals()

    # ====================================================
    # Connect
    # ====================================================

    def connect_signals(self):

        self.refresh_button.clicked.connect(

            self.refreshRequested

        )

        self.scan_button.clicked.connect(

            self.scanRequested

        )

        self.theme_button.clicked.connect(

            self.themeChanged

        )

        self.notification_button.clicked.connect(

            self.notificationClicked

        )

        self.user_button.clicked.connect(

            self.userMenuClicked

        )

    # ====================================================
    # Clock
    # ====================================================

    def start_clock(self):

        self.timer = QTimer(self)

        self.timer.timeout.connect(

            self.update_clock

        )

        self.timer.start(1000)

        self.update_clock()

    # ====================================================
    # Update Clock
    # ====================================================

    def update_clock(self):

        now = datetime.now()

        self.clock.setText(

            now.strftime(

                "%d %b %Y   %H:%M:%S"

            )

        )

    # ====================================================
    # Search
    # ====================================================

    def search_symbol(self):

        symbol = self.search.text().strip().upper()

        if symbol:

            self.searchRequested.emit(

                symbol

            )
                # ====================================================
    # Market Widgets
    # ====================================================

    def create_market_widgets(self):

        self.nifty_label = QLabel("NIFTY")

        self.nifty_value = QLabel("--")

        self.banknifty_label = QLabel("BANK NIFTY")

        self.banknifty_value = QLabel("--")

        self.sensex_label = QLabel("SENSEX")

        self.sensex_value = QLabel("--")

        self.vix_label = QLabel("INDIA VIX")

        self.vix_value = QLabel("--")

        self.connection_status = QLabel("ðŸŸ¢ Connected")

        widgets = [

            self.nifty_label,
            self.nifty_value,

            self.banknifty_label,
            self.banknifty_value,

            self.sensex_label,
            self.sensex_value,

            self.vix_label,
            self.vix_value,

            self.connection_status

        ]

        for widget in widgets:

            widget.setAlignment(

                Qt.AlignCenter

            )

            widget.setMinimumWidth(80)

    # ====================================================
    # Add Widgets To Header
    # ====================================================

    def insert_market_widgets(

        self,

        layout: QHBoxLayout

    ):

        layout.addSpacing(20)

        layout.addWidget(self.nifty_label)

        layout.addWidget(self.nifty_value)

        layout.addSpacing(10)

        layout.addWidget(self.banknifty_label)

        layout.addWidget(self.banknifty_value)

        layout.addSpacing(10)

        layout.addWidget(self.sensex_label)

        layout.addWidget(self.sensex_value)

        layout.addSpacing(10)

        layout.addWidget(self.vix_label)

        layout.addWidget(self.vix_value)

        layout.addSpacing(20)

        layout.addWidget(

            self.connection_status

        )

    # ====================================================
    # Update Market Data
    # ====================================================

    def update_market_data(

        self,

        data: dict

    ):

        self.market_data = data

        self.nifty_value.setText(

            str(

                data.get(

                    "nifty",

                    "--"

                )

            )

        )

        self.banknifty_value.setText(

            str(

                data.get(

                    "banknifty",

                    "--"

                )

            )

        )

        self.sensex_value.setText(

            str(

                data.get(

                    "sensex",

                    "--"

                )

            )

        )

        self.vix_value.setText(

            str(

                data.get(

                    "vix",

                    "--"

                )

            )

        )

    # ====================================================
    # Market Session
    # ====================================================

    def market_session(self):

        now = datetime.now()

        minutes = now.hour * 60 + now.minute

        pre_open = 9 * 60

        market_open = 9 * 60 + 15

        market_close = 15 * 60 + 30

        if pre_open <= minutes < market_open:

            return "PRE-OPEN"

        if market_open <= minutes <= market_close:

            return "OPEN"

        if market_close < minutes <= 16 * 60:

            return "POST-CLOSE"

        return "CLOSED"

    # ====================================================
    # Update Market Status
    # ====================================================

    def update_market_status(

        self,

        summary=None

    ):

        session = self.market_session()

        if session == "OPEN":

            self.market_status.setText(

                "ðŸŸ¢ MARKET OPEN"

            )

        elif session == "PRE-OPEN":

            self.market_status.setText(

                "ðŸŸ¡ PRE-OPEN"

            )

        elif session == "POST-CLOSE":

            self.market_status.setText(

                "ðŸŸ  POST-CLOSE"

            )

        else:

            self.market_status.setText(

                "ðŸ”´ MARKET CLOSED"

            )

        if summary and isinstance(summary, dict):

            self.update_market_data(summary)

    # ====================================================
    # AI STATUS
    # ====================================================

    def set_ai_status(

        self,

        status: str

    ):

        self.ai_status.setText(

            status

        )

    # ====================================================
    # Connection Status
    # ====================================================

    def set_connection_status(

        self,

        connected: bool

    ):

        if connected:

            self.connection_status.setText(

                "ðŸŸ¢ Connected"

            )

        else:

            self.connection_status.setText(

                "ðŸ”´ Disconnected"

            )

    # ====================================================
    # Search History
    # ====================================================

    def add_search_history(

        self,

        symbol: str

    ):

        if not hasattr(

            self,

            "_history"

        ):

            self._history = []

        symbol = symbol.upper()

        if symbol in self._history:

            self._history.remove(symbol)

        self._history.insert(

            0,

            symbol

        )

        self._history = self._history[:20]

    # ====================================================
    # Recent Searches
    # ====================================================

    def recent_searches(self):

        return getattr(

            self,

            "_history",

            []

        )
        # ====================================================
    # Notification Center
    # ====================================================

    def create_notification_center(self):

        self.notifications = []

        self.notification_count = 0

    def add_notification(

        self,

        title: str,

        message: str

    ):

        notification = {

            "time": datetime.now(),

            "title": title,

            "message": message

        }

        self.notifications.insert(

            0,

            notification

        )

        self.notification_count = len(

            self.notifications

        )

        self.update_notification_icon()

    def clear_notifications(self):

        self.notifications.clear()

        self.notification_count = 0

        self.update_notification_icon()

    def update_notification_icon(self):

        if self.notification_count:

            self.notification_button.setText(

                f"ðŸ”” {self.notification_count}"

            )

        else:

            self.notification_button.setText(

                "ðŸ””"

            )

    def latest_notifications(

        self,

        limit: int = 10

    ):

        return self.notifications[:limit]

    # ====================================================
    # User Information
    # ====================================================

    def set_user(

        self,

        name: str,

        role: str = "Trader"

    ):

        self.user_name = name

        self.user_role = role

        self.user_button.setToolTip(

            f"{name}\n{role}"

        )

    # ====================================================
    # Theme Button
    # ====================================================

    def set_theme(

        self,

        theme: str

    ):

        theme = theme.lower()

        if theme == "dark":

            self.theme_button.setText(

                "ðŸŒ™"

            )

        else:

            self.theme_button.setText(

                "â˜€"

            )

    # ====================================================
    # Refresh Animation
    # ====================================================

    def begin_refresh(self):

        self.refresh_button.setEnabled(False)

        self.refresh_button.setText(

            "â³"

        )

    def end_refresh(self):

        self.refresh_button.setEnabled(True)

        self.refresh_button.setText(

            "ðŸ”„"

        )

    # ====================================================
    # Scan Indicator
    # ====================================================

    def begin_scan(self):

        self.scan_button.setEnabled(False)

        self.scan_button.setText(

            "â³"

        )

        self.ai_status.setText(

            "ðŸ¤– Scanning..."

        )

    def end_scan(self):

        self.scan_button.setEnabled(True)

        self.scan_button.setText(

            "â–¶"

        )

        self.ai_status.setText(

            "ðŸ¤– AI Ready"

        )

    # ====================================================
    # Live Timer
    # ====================================================

    def start_market_timer(self):

        self.market_timer = QTimer(self)

        self.market_timer.timeout.connect(

            self.update_market_status

        )

        self.market_timer.start(

            30000

        )

    # ====================================================
    # Keyboard Shortcuts
    # ====================================================

    def keyPressEvent(

        self,

        event

    ):

        key = event.key()

        if key == Qt.Key_F5:

            self.refreshRequested.emit()

            return

        if key == Qt.Key_F9:

            self.scanRequested.emit()

            return

        super().keyPressEvent(

            event

        )

    # ====================================================
    # Runtime Information
    # ====================================================

    def runtime_information(self):

        return {

            "market_session":

                self.market_session(),

            "notifications":

                self.notification_count,

            "connection":

                self.connection_status.text(),

            "ai_status":

                self.ai_status.text(),

            "searches":

                len(

                    self.recent_searches()

                )

        }

    # ====================================================
    # Diagnostics
    # ====================================================

    def diagnostics(self):

        return {

            "component":

                "Header",

            "runtime":

                self.runtime_information(),

            "market":

                self.market_data

        }
        # ====================================================
    # Symbol Autocomplete
    # ====================================================

    def set_symbol_list(

        self,

        symbols: list[str]

    ):

        try:

            from PySide6.QtWidgets import QCompleter

            completer = QCompleter(symbols)

            completer.setCaseSensitivity(

                Qt.CaseInsensitive

            )

            completer.setFilterMode(

                Qt.MatchContains

            )

            self.search.setCompleter(

                completer

            )

        except Exception:

            pass

    # ====================================================
    # Update Price Widget
    # ====================================================

    def update_index_widget(

        self,

        label: QLabel,

        value: QLabel,

        price,

        change

    ):

        value.setText(

            f"{price}"

        )

        if change > 0:

            value.setStyleSheet(

                "color:#00C853;font-weight:bold;"

            )

            label.setText(

                f"â–² {label.text().replace('â–² ','').replace('â–¼ ','')}"

            )

        elif change < 0:

            value.setStyleSheet(

                "color:#FF5252;font-weight:bold;"

            )

            label.setText(

                f"â–¼ {label.text().replace('â–² ','').replace('â–¼ ','')}"

            )

        else:

            value.setStyleSheet(

                ""

            )

    # ====================================================
    # Update All Indices
    # ====================================================

    def update_indices(

        self,

        market: dict

    ):

        self.update_index_widget(

            self.nifty_label,

            self.nifty_value,

            market.get("nifty", "--"),

            market.get("nifty_change", 0)

        )

        self.update_index_widget(

            self.banknifty_label,

            self.banknifty_value,

            market.get("banknifty", "--"),

            market.get("banknifty_change", 0)

        )

        self.update_index_widget(

            self.sensex_label,

            self.sensex_value,

            market.get("sensex", "--"),

            market.get("sensex_change", 0)

        )

        self.update_index_widget(

            self.vix_label,

            self.vix_value,

            market.get("vix", "--"),

            market.get("vix_change", 0)

        )

    # ====================================================
    # Market Trend
    # ====================================================

    def set_market_trend(

        self,

        trend: str

    ):

        trend = trend.upper()

        if trend == "BULLISH":

            self.market_status.setText(

                "ðŸŸ¢ MARKET OPEN â€¢ BULLISH"

            )

        elif trend == "BEARISH":

            self.market_status.setText(

                "ðŸ”´ MARKET OPEN â€¢ BEARISH"

            )

        elif trend == "SIDEWAYS":

            self.market_status.setText(

                "ðŸŸ¡ MARKET OPEN â€¢ SIDEWAYS"

            )

    # ====================================================
    # Connection Recovery
    # ====================================================

    def reconnect(self):

        self.connection_status.setText(

            "ðŸŸ¡ Reconnecting..."

        )

    def reconnect_success(self):

        self.connection_status.setText(

            "ðŸŸ¢ Connected"

        )

    def reconnect_failed(self):

        self.connection_status.setText(

            "ðŸ”´ Connection Failed"

        )

    # ====================================================
    # Clear Search
    # ====================================================

    def clear_search(self):

        self.search.clear()

    # ====================================================
    # Current Symbol
    # ====================================================

    def current_symbol(self):

        return self.search.text().strip().upper()

    # ====================================================
    # Header Busy State
    # ====================================================

    def set_busy(

        self,

        busy: bool

    ):

        controls = [

            self.search,

            self.refresh_button,

            self.scan_button,

            self.theme_button,

            self.notification_button,

            self.user_button

        ]

        for widget in controls:

            widget.setEnabled(

                not busy

            )

    # ====================================================
    # Build Information
    # ====================================================

    def build_information(self):

        return {

            "application":

                "StockVersity Scanner Pro",

            "component":

                "Header",

            "version":

                "4.0",

            "powered_by":

                "AI"

        }

    # ====================================================
    # Public API
    # ====================================================

    def refresh_header(

        self,

        market: dict,

        trend: str,

        connected: bool

    ):

        self.update_indices(

            market

        )

        self.set_market_trend(

            trend

        )

        self.set_connection_status(

            connected

        )
            # ====================================================
    # Reset Header
    # ====================================================

    def reset(self):

        self.market_data = {}

        self.create_notification_center()

        self.market_status.setText(

            "ðŸ”´ MARKET CLOSED"

        )

        self.ai_status.setText(

            "ðŸ¤– AI Ready"

        )

        self.connection_status.setText(

            "ðŸ”´ Disconnected"

        )

        self.nifty_value.setText("--")

        self.banknifty_value.setText("--")

        self.sensex_value.setText("--")

        self.vix_value.setText("--")

        self.search.clear()

        self.clear_notifications()

    # ====================================================
    # Clear Market Data
    # ====================================================

    def clear_market_data(self):

        self.market_data.clear()

        self.nifty_value.setText("--")

        self.banknifty_value.setText("--")

        self.sensex_value.setText("--")

        self.vix_value.setText("--")

    # ====================================================
    # Status Message
    # ====================================================

    def show_notification(

        self,

        title: str,

        message: str

    ):

        self.add_notification(

            title,

            message

        )

    # ====================================================
    # Current Runtime State
    # ====================================================

    def state(self):

        return {

            "market_session":

                self.market_session(),

            "connected":

                "Connected"

                in self.connection_status.text(),

            "ai":

                self.ai_status.text(),

            "symbol":

                self.current_symbol(),

            "notifications":

                self.notification_count

        }

    # ====================================================
    # Export Header State
    # ====================================================

    def export_state(self):

        return {

            "market":

                self.market_data,

            "runtime":

                self.state(),

            "recent_searches":

                self.recent_searches(),

            "notifications":

                self.latest_notifications()

        }

    # ====================================================
    # Import Header State
    # ====================================================

    def import_state(

        self,

        state: dict

    ):

        if not state:

            return

        self.market_data = state.get(

            "market",

            {}

        )

        self.update_market_data(

            self.market_data

        )

        searches = state.get(

            "recent_searches",

            []

        )

        self._history = searches.copy()

    # ====================================================
    # Focus Search Box
    # ====================================================

    def focus_search(self):

        self.search.setFocus()

        self.search.selectAll()

    # ====================================================
    # Component Information
    # ====================================================

    @property
    def component_name(self):

        return "Header"

    @property
    def application_name(self):

        return "StockVersity Scanner Pro"

    @property
    def version(self):

        return "4.0"

    # ====================================================
    # Runtime Diagnostics
    # ====================================================

    def runtime_diagnostics(self):

        return {

            "component":

                self.component_name,

            "application":

                self.application_name,

            "version":

                self.version,

            "runtime":

                self.runtime_information(),

            "market":

                self.market_data

        }

    # ====================================================
    # String Representation
    # ====================================================

    def __repr__(self):

        return (

            f"<Header "

            f"session='{self.market_session()}' "

            f"notifications={self.notification_count}>"

        )


# ====================================================
# Factory
# ====================================================

def create_header():

    return Header()


# ====================================================
# END OF FILE
# ====================================================
