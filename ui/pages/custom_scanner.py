"""
==========================================================
StockVersity Scanner Pro
Custom Scanner
==========================================================
"""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
    QComboBox,
    QLineEdit,
    QSizePolicy,
)

from backend.services.scanner_service import ScannerService

from ui.widgets.info_card import InfoCard
from ui.widgets.opportunities_table import OpportunitiesTable


class CustomScannerPage(QWidget):

    AUTO_REFRESH = 60000

    def __init__(self):

        super().__init__()

        self.scanner = ScannerService()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)

        self.build_ui()

        self.connect_signals()

        self.start_auto_refresh()

        self.refresh_data()

    # =====================================================
    # Create Panel
    # =====================================================

    def create_panel(self, title):

        frame = QFrame()

        frame.setObjectName("InfoPanel")

        layout = QVBoxLayout(frame)

        layout.setContentsMargins(15, 15, 15, 15)

        label = QLabel(title)

        label.setStyleSheet("""
            font-size:16px;
            font-weight:bold;
        """)

        layout.addWidget(label)

        return frame, layout

    # =====================================================
    # Build UI
    # =====================================================

    def build_ui(self):

        root = QVBoxLayout(self)

        root.setContentsMargins(20,20,20,20)

        root.setSpacing(15)

        # =================================================
        # Header
        # =================================================

        header = QHBoxLayout()

        title = QLabel("Custom Scanner")

        title.setStyleSheet("""
            font-size:24px;
            font-weight:bold;
        """)

        header.addWidget(title)

        header.addStretch()

        self.search = QLineEdit()

        self.search.setPlaceholderText(
            "Search Stock..."
        )

        self.search.setMinimumWidth(220)

        header.addWidget(self.search)

        self.refresh_btn = QPushButton("Refresh")

        header.addWidget(self.refresh_btn)

        self.export_btn = QPushButton("Export")

        header.addWidget(self.export_btn)

        root.addLayout(header)

        # =================================================
        # Filter Row
        # =================================================

        filters = QGridLayout()

        self.timeframe = QComboBox()
        self.timeframe.addItems([
            "1 Minute",
            "5 Minute",
            "15 Minute",
            "1 Hour",
            "Daily",
            "Weekly"
        ])

        self.indicator = QComboBox()
        self.indicator.addItems([
            "EMA",
            "VWAP",
            "RSI",
            "MACD",
            "ADX",
            "Supertrend",
            "Volume",
            "ATR"
        ])

        self.condition = QComboBox()
        self.condition.addItems([
            "Greater Than",
            "Less Than",
            "Cross Above",
            "Cross Below",
            "Equal To"
        ])

        self.value = QLineEdit()
        self.value.setPlaceholderText("Value")

        self.add_rule_btn = QPushButton("Add Rule")

        filters.addWidget(QLabel("Timeframe"),0,0)
        filters.addWidget(self.timeframe,0,1)

        filters.addWidget(QLabel("Indicator"),0,2)
        filters.addWidget(self.indicator,0,3)

        filters.addWidget(QLabel("Condition"),0,4)
        filters.addWidget(self.condition,0,5)

        filters.addWidget(QLabel("Value"),0,6)
        filters.addWidget(self.value,0,7)

        filters.addWidget(self.add_rule_btn,0,8)

        root.addLayout(filters)

        # =================================================
        # Summary Cards
        # =================================================

        cards = QGridLayout()

        cards.setHorizontalSpacing(12)

        self.total_card = InfoCard(
            "Rules",
            "0"
        )

        self.result_card = InfoCard(
            "Stocks Found",
            "0"
        )

        self.buy_card = InfoCard(
            "Buy",
            "0"
        )

        self.sell_card = InfoCard(
            "Sell",
            "0"
        )

        self.status_card = InfoCard(
            "Scanner Status",
            "Idle"
        )

        cards.addWidget(self.total_card,0,0)
        cards.addWidget(self.result_card,0,1)
        cards.addWidget(self.buy_card,0,2)
        cards.addWidget(self.sell_card,0,3)
        cards.addWidget(self.status_card,0,4)

        root.addLayout(cards)

        # =================================================
        # Information Panels
        # =================================================

        top = QHBoxLayout()

        self.rule_panel, rule_layout = self.create_panel(
            "Scanner Rules"
        )

        self.rule_label = QLabel(
            "No rules added."
        )

        self.rule_label.setWordWrap(True)

        rule_layout.addWidget(
            self.rule_label
        )

        top.addWidget(
            self.rule_panel
        )

        self.summary_panel, summary_layout = self.create_panel(
            "Scanner Summary"
        )

        self.summary_label = QLabel()

        self.summary_label.setWordWrap(True)

        summary_layout.addWidget(
            self.summary_label
        )

        top.addWidget(
            self.summary_panel
        )

        root.addLayout(top)
                # =================================================
        # Scanner Results Table
        # =================================================

        self.table = OpportunitiesTable()

        self.table.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        root.addWidget(self.table)

        # =================================================
        # Bottom Panels
        # =================================================

        bottom = QHBoxLayout()

        # -----------------------------------------------
        # Performance Panel
        # -----------------------------------------------

        self.performance_panel, performance_layout = self.create_panel(
            "Performance"
        )

        self.performance_label = QLabel()

        self.performance_label.setWordWrap(True)

        performance_layout.addWidget(
            self.performance_label
        )

        bottom.addWidget(
            self.performance_panel
        )

        # -----------------------------------------------
        # Statistics Panel
        # -----------------------------------------------

        self.stats_panel, stats_layout = self.create_panel(
            "Scanner Statistics"
        )

        self.stats_label = QLabel()

        self.stats_label.setWordWrap(True)

        stats_layout.addWidget(
            self.stats_label
        )

        bottom.addWidget(
            self.stats_panel
        )

        root.addLayout(bottom)

        # =================================================
        # Footer Status
        # =================================================

        self.status = QLabel("Ready")

        self.status.setAlignment(
            Qt.AlignRight
        )

        root.addWidget(
            self.status
        )

        # =================================================
        # Rule Storage
        # =================================================

        self.rules = []

    # =====================================================
    # Refresh Scanner
    # =====================================================

    def refresh_data(self):

        try:

            self.status.setText(
                "Refreshing custom scanner..."
            )

            self.update_cards()

            self.load_results()

            self.update_summary()

            self.update_statistics()

            self.status.setText(
                "Custom scanner ready."
            )

        except Exception as e:

            self.status.setText(
                f"Error : {e}"
            )

            print(e)

    # =====================================================
    # Update Cards
    # =====================================================

    def update_cards(self):

        stats = self.scanner.statistics()

        self.total_card.set_value(
            str(len(self.rules))
        )

        self.result_card.set_value(
            str(stats.get("total", 0))
        )

        self.buy_card.set_value(
            str(stats.get("buy", 0))
        )

        self.sell_card.set_value(
            str(stats.get("sell", 0))
        )

        self.status_card.set_value(
            stats.get(
                "status",
                "Ready"
            )
        )

    # =====================================================
    # Load Scanner Results
    # =====================================================

    def load_results(self):

        try:

            data = self.scanner.get_custom_opportunities()

        except AttributeError:

            try:

                data = self.scanner.get_opportunities()

            except AttributeError:

                data = []

        self.table.set_data(data)
            # =====================================================
    # Add Scanner Rule
    # =====================================================

    def add_rule(self):

        rule = {
            "timeframe": self.timeframe.currentText(),
            "indicator": self.indicator.currentText(),
            "condition": self.condition.currentText(),
            "value": self.value.text().strip()
        }

        if not rule["value"]:

            self.status.setText(
                "Please enter a value."
            )

            return

        self.rules.append(rule)

        text = ""

        for i, r in enumerate(self.rules, start=1):

            text += (
                f"{i}. "
                f"{r['timeframe']} | "
                f"{r['indicator']} "
                f"{r['condition']} "
                f"{r['value']}\n"
            )

        self.rule_label.setText(text)

        self.value.clear()

        self.update_cards()

        self.status.setText(
            "Rule added successfully."
        )

    # =====================================================
    # Update Summary
    # =====================================================

    def update_summary(self):

        try:

            stats = self.scanner.statistics()

            summary = (
                f"Rules Created : {len(self.rules)}\n"
                f"Stocks Found : {stats.get('total',0)}\n"
                f"Buy Signals : {stats.get('buy',0)}\n"
                f"Sell Signals : {stats.get('sell',0)}\n"
                f"Scanner Status : "
                f"{stats.get('status','Ready')}"
            )

            self.summary_label.setText(
                summary
            )

        except Exception as e:

            self.summary_label.setText(
                str(e)
            )

    # =====================================================
    # Update Statistics
    # =====================================================

    def update_statistics(self):

        try:

            stats = self.scanner.statistics()

            performance = (
                f"Signals Today : "
                f"{stats.get('signals_today',0)}\n"

                f"Open Trades : "
                f"{stats.get('open_trades',0)}\n"

                f"Closed Trades : "
                f"{stats.get('closed_trades',0)}\n"

                f"Win Rate : "
                f"{stats.get('win_rate',0)}%\n"

                f"Last Refresh : "
                f"{stats.get('last_refresh','-')}"
            )

            self.performance_label.setText(
                performance
            )

            details = (
                f"Rules : {len(self.rules)}\n"
                f"Buy : {stats.get('buy',0)}\n"
                f"Sell : {stats.get('sell',0)}\n"
                f"Total : {stats.get('total',0)}"
            )

            self.stats_label.setText(
                details
            )

        except Exception as e:

            self.performance_label.setText(
                str(e)
            )

            self.stats_label.setText("")

    # =====================================================
    # Search
    # =====================================================

    def search_data(self):

        keyword = self.search.text().strip()

        if not keyword:

            self.load_results()

            return

        results = self.scanner.search(keyword)

        self.table.set_data(results)

        self.status.setText(
            f"{len(results)} stock(s) found."
        )

    # =====================================================
    # Manual Refresh
    # =====================================================

    def manual_refresh(self):

        self.refresh_data()

    # =====================================================
    # Export CSV
    # =====================================================

    def export_csv(self):

        self.table.export_csv()

        self.status.setText(
            "Scanner results exported."
        )

    # =====================================================
    # Selected Stock
    # =====================================================

    def open_stock(self, symbol):

        print(f"Selected : {symbol}")

        self.status.setText(
            f"Selected : {symbol}"
        )
            # =====================================================
    # Connect Signals
    # =====================================================

    def connect_signals(self):

        self.refresh_btn.clicked.connect(
            self.manual_refresh
        )

        self.export_btn.clicked.connect(
            self.export_csv
        )

        self.add_rule_btn.clicked.connect(
            self.add_rule
        )

        self.search.returnPressed.connect(
            self.search_data
        )

        try:

            self.table.set_double_click_callback(
                self.open_stock
            )

        except Exception:

            pass

    # =====================================================
    # Auto Refresh
    # =====================================================

    def start_auto_refresh(self):

        if not self.timer.isActive():

            self.timer.start(
                self.AUTO_REFRESH
            )

    # =====================================================

    def stop_auto_refresh(self):

        if self.timer.isActive():

            self.timer.stop()

    # =====================================================
    # Clear Rules
    # =====================================================

    def clear_rules(self):

        self.rules.clear()

        self.rule_label.setText(
            "No rules added."
        )

        self.update_cards()

        self.status.setText(
            "All rules cleared."
        )

    # =====================================================
    # Clear Search
    # =====================================================

    def clear_search(self):

        self.search.clear()

        self.load_results()

        self.status.setText(
            "Search cleared."
        )

    # =====================================================
    # Reset Page
    # =====================================================

    def reset_page(self):

        self.clear_rules()

        self.clear_search()

        self.timeframe.setCurrentIndex(0)

        self.indicator.setCurrentIndex(0)

        self.condition.setCurrentIndex(0)

        self.value.clear()

        self.refresh_data()

    # =====================================================
    # Information
    # =====================================================

    def page_name(self):

        return "Custom Scanner"

    # =====================================================

    def page_version(self):

        return "1.0"

    # =====================================================

    def scanner_service(self):

        return self.scanner

    # =====================================================
    # Enable Controls
    # =====================================================

    def enable_controls(self):

        self.refresh_btn.setEnabled(True)

        self.export_btn.setEnabled(True)

        self.add_rule_btn.setEnabled(True)

        self.search.setEnabled(True)

        self.timeframe.setEnabled(True)

        self.indicator.setEnabled(True)

        self.condition.setEnabled(True)

        self.value.setEnabled(True)

    # =====================================================
    # Disable Controls
    # =====================================================

    def disable_controls(self):

        self.refresh_btn.setEnabled(False)

        self.export_btn.setEnabled(False)

        self.add_rule_btn.setEnabled(False)

        self.search.setEnabled(False)

        self.timeframe.setEnabled(False)

        self.indicator.setEnabled(False)

        self.condition.setEnabled(False)

        self.value.setEnabled(False)

    # =====================================================
    # Refresh Helpers
    # =====================================================

    def refresh_table(self):

        self.load_results()

    # =====================================================

    def refresh_cards(self):

        self.update_cards()

    # =====================================================

    def refresh_summary(self):

        self.update_summary()

    # =====================================================

    def refresh_statistics(self):

        self.update_statistics()

    # =====================================================

    def full_refresh(self):

        self.refresh_data()

    # =====================================================
    # Close Event
    # =====================================================

    def closeEvent(self, event):

        self.stop_auto_refresh()

        event.accept()

    # =====================================================
    # Destructor
    # =====================================================

    def __del__(self):

        try:

            self.stop_auto_refresh()

        except Exception:

            pass

    # =====================================================
    # End of Custom Scanner
    # =====================================================
