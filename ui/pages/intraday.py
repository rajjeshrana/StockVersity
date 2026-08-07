"""
==========================================================
StockVersity Scanner Pro v3
Professional Intraday Scanner
==========================================================
"""

from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QComboBox,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QFrame,
    QMessageBox,
    QSizePolicy,
)

from backend.services.scanner_service import ScannerService

from ui.widgets.info_card import InfoCard
from ui.widgets.opportunities_table import OpportunitiesTable


class IntradayPage(QWidget):

    AUTO_REFRESH = 30000

    def __init__(self):

        super().__init__()

        self.scanner = ScannerService()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)

        self.opportunities = []

        self.build_ui()
        self.connect_signals()

        self.start_auto_refresh()
        self.refresh_data()

    # =====================================================
    # PANEL
    # =====================================================

    def create_panel(self, title):

        panel = QFrame()

        panel.setObjectName("ScannerPanel")

        panel.setStyleSheet("""
        QFrame#ScannerPanel{

            background:#1A1F2E;

            border:1px solid #30384A;

            border-radius:12px;

        }
        """)

        layout = QVBoxLayout(panel)

        layout.setContentsMargins(16,16,16,16)

        layout.setSpacing(10)

        lbl = QLabel(title)

        lbl.setStyleSheet("""
            font-size:16px;
            font-weight:700;
        """)

        layout.addWidget(lbl)

        return panel, layout

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(self):

        root = QVBoxLayout(self)

        root.setContentsMargins(20,20,20,20)

        root.setSpacing(16)

        # =================================================
        # HEADER
        # =================================================

        header = QHBoxLayout()

        title = QLabel("Intraday Scanner")

        title.setStyleSheet("""
            font-size:30px;
            font-weight:700;
        """)

        header.addWidget(title)

        header.addStretch()

        self.last_update = QLabel("Updated : --")

        header.addWidget(self.last_update)

        self.search = QLineEdit()

        self.search.setPlaceholderText(
            "Search Stock..."
        )

        self.search.setMinimumWidth(250)

        self.search.setFixedHeight(38)

        header.addWidget(self.search)

        self.strategy = QComboBox()

        self.strategy.addItems([

            "All Strategies",

            "ORB",

            "VWAP",

            "EMA",

            "Momentum",

            "Scalping",

            "Breakout",

        ])

        self.strategy.setFixedHeight(38)

        header.addWidget(self.strategy)

        self.refresh_btn = QPushButton("âŸ³ Refresh")
        self.export_btn = QPushButton("â¬‡ Export")

        self.refresh_btn.setMinimumHeight(38)
        self.export_btn.setMinimumHeight(38)

        header.addWidget(self.refresh_btn)
        header.addWidget(self.export_btn)

        root.addLayout(header)

        # =================================================
        # KPI
        # =================================================

        cards = QGridLayout()

        cards.setHorizontalSpacing(14)
        cards.setVerticalSpacing(14)

        self.total_card = InfoCard(
            "Stocks Scanned",
            "0",
            "ðŸ“Š"
        )

        self.buy_card = InfoCard(
            "BUY Signals",
            "0",
            "ðŸŸ¢"
        )

        self.sell_card = InfoCard(
            "SELL Signals",
            "0",
            "ðŸ”´"
        )

        self.volume_card = InfoCard(
            "High Volume",
            "0",
            "âš¡"
        )

        self.breakout_card = InfoCard(
            "Breakouts",
            "0",
            "ðŸš€"
        )

        self.ai_card = InfoCard(
            "AI Qualified",
            "0",
            "ðŸ¤–"
        )

        cards.addWidget(self.total_card,0,0)
        cards.addWidget(self.buy_card,0,1)
        cards.addWidget(self.sell_card,0,2)
        cards.addWidget(self.volume_card,0,3)
        cards.addWidget(self.breakout_card,0,4)
        cards.addWidget(self.ai_card,0,5)

        root.addLayout(cards)
                # =================================================
        # MARKET PANELS
        # =================================================

        panel_layout = QHBoxLayout()

        panel_layout.setSpacing(16)

        # ================================================
        # Scanner Statistics
        # ================================================

        stats_panel, stats_layout = self.create_panel(
            "Scanner Statistics"
        )

        self.lbl_scanned = QLabel("Scanned : 0")
        self.lbl_active = QLabel("Active Signals : 0")
        self.lbl_avg_ai = QLabel("Average AI Score : 0")
        self.lbl_rr = QLabel("Average R:R : 0")

        for lbl in (
            self.lbl_scanned,
            self.lbl_active,
            self.lbl_avg_ai,
            self.lbl_rr,
        ):

            lbl.setMinimumHeight(28)

            stats_layout.addWidget(lbl)

        stats_layout.addStretch()

        panel_layout.addWidget(stats_panel, 2)

        # ================================================
        # Top Momentum Stocks
        # ================================================

        momentum_panel, momentum_layout = self.create_panel(
            "Top Momentum"
        )

        self.momentum_list = QListWidget()

        self.momentum_list.setMinimumHeight(180)

        momentum_layout.addWidget(
            self.momentum_list
        )

        panel_layout.addWidget(momentum_panel, 2)

        # ================================================
        # Watch List
        # ================================================

        watch_panel, watch_layout = self.create_panel(
            "Watch List"
        )

        self.watch_list = QListWidget()

        self.watch_list.setMinimumHeight(180)

        watch_layout.addWidget(
            self.watch_list
        )

        panel_layout.addWidget(watch_panel, 2)

        root.addLayout(panel_layout)

        # =================================================
        # TABLE
        # =================================================

        table_panel, table_layout = self.create_panel(
            "Intraday Opportunities"
        )

        self.table = OpportunitiesTable()

        self.table.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

        table_layout.addWidget(self.table)

        root.addWidget(
            table_panel,
            stretch=1,
        )
            # =====================================================
    # REFRESH
    # =====================================================

    def refresh_data(self):

        try:

            self.load_opportunities()

            self.update_cards()

            self.update_statistics()

            self.update_momentum()

            self.update_watchlist()

            self.last_update.setText(
                "Updated : " +
                datetime.now().strftime("%H:%M:%S")
            )

        except Exception as e:

            QMessageBox.warning(
                self,
                "Scanner",
                str(e),
            )

    # =====================================================
    # LOAD OPPORTUNITIES
    # =====================================================

    def load_opportunities(self):

        try:

            self.opportunities = (
                self.scanner.get_opportunities()
            )

        except Exception:

            self.opportunities = []

        self.table.set_data(self.opportunities)

    # =====================================================
    # KPI CARDS
    # =====================================================

    def update_cards(self):

        total = len(self.opportunities)

        buy = 0
        sell = 0
        volume = 0
        breakout = 0
        ai = 0

        for item in self.opportunities:

            signal = str(
                getattr(item, "signal", "")
            ).upper()

            score = float(
                getattr(item, "ai_score", 0)
            )

            vol = float(
                getattr(item, "volume_ratio", 0)
            )

            pattern = str(
                getattr(item, "pattern", "")
            ).upper()

            if signal == "BUY":
                buy += 1

            elif signal == "SELL":
                sell += 1

            if vol >= 2:

                volume += 1

            if (
                "BREAKOUT" in pattern
                or "ORB" in pattern
            ):

                breakout += 1

            if score >= 70:

                ai += 1

        self.total_card.update_card(total)

        self.buy_card.update_card(
            buy,
            status="BUY",
        )

        self.sell_card.update_card(
            sell,
            status="SELL",
        )

        self.volume_card.update_card(volume)

        self.breakout_card.update_card(breakout)

        self.ai_card.update_card(
            ai,
            status="AI",
        )

    # =====================================================
    # STATISTICS
    # =====================================================

    def update_statistics(self):

        total = len(self.opportunities)

        if total == 0:

            self.lbl_scanned.setText(
                "Scanned : 0"
            )

            self.lbl_active.setText(
                "Active Signals : 0"
            )

            self.lbl_avg_ai.setText(
                "Average AI Score : 0"
            )

            self.lbl_rr.setText(
                "Average R:R : 0"
            )

            return

        active = 0

        ai_total = 0

        rr_total = 0

        rr_count = 0

        for item in self.opportunities:

            signal = str(
                getattr(item, "signal", "")
            ).upper()

            if signal in ("BUY", "SELL"):

                active += 1

            ai_total += float(
                getattr(item, "ai_score", 0)
            )

            rr = getattr(item, "risk_reward", None)

            if rr is not None:

                try:

                    rr_total += float(rr)

                    rr_count += 1

                except Exception:

                    pass

        avg_ai = round(
            ai_total / total,
            1,
        )

        avg_rr = (
            round(rr_total / rr_count, 2)
            if rr_count
            else 0
        )

        self.lbl_scanned.setText(
            f"Scanned : {total}"
        )

        self.lbl_active.setText(
            f"Active Signals : {active}"
        )

        self.lbl_avg_ai.setText(
            f"Average AI Score : {avg_ai}"
        )

        self.lbl_rr.setText(
            f"Average R:R : {avg_rr}"
        )

    # =====================================================
    # MOMENTUM
    # =====================================================

    def update_momentum(self):

        self.momentum_list.clear()

        ranked = sorted(

            self.opportunities,

            key=lambda x: float(
                getattr(
                    x,
                    "ai_score",
                    0,
                )
            ),

            reverse=True,

        )

        for item in ranked[:10]:

            symbol = getattr(
                item,
                "symbol",
                "",
            )

            score = getattr(
                item,
                "ai_score",
                0,
            )

            self.momentum_list.addItem(

                QListWidgetItem(

                    f"{symbol}   ({score})"

                )

            )

    # =====================================================
    # WATCHLIST
    # =====================================================

    def update_watchlist(self):

        self.watch_list.clear()

        for item in self.opportunities:

            score = float(
                getattr(
                    item,
                    "ai_score",
                    0,
                )
            )

            if score < 80:

                continue

            symbol = getattr(
                item,
                "symbol",
                "",
            )

            signal = getattr(
                item,
                "signal",
                "",
            )

            self.watch_list.addItem(

                QListWidgetItem(

                    f"{symbol}   [{signal}]"

                )

            )
                # =====================================================
    # SEARCH
    # =====================================================

    def search_data(self):

        text = self.search.text().strip().upper()

        strategy = self.strategy.currentText().upper()

        if not text and strategy == "ALL STRATEGIES":

            self.table.set_data(self.opportunities)

            return

        filtered = []

        for item in self.opportunities:

            symbol = str(
                getattr(item, "symbol", "")
            ).upper()

            company = str(
                getattr(item, "company", "")
            ).upper()

            sector = str(
                getattr(item, "sector", "")
            ).upper()

            pattern = str(
                getattr(item, "pattern", "")
            ).upper()

            if text:

                if (
                    text not in symbol
                    and text not in company
                    and text not in sector
                ):
                    continue

            if strategy != "ALL STRATEGIES":

                if strategy not in pattern:

                    continue

            filtered.append(item)

        self.table.set_data(filtered)

    # =====================================================
    # EXPORT
    # =====================================================

    def export_data(self):

        try:

            self.table.export_csv()

        except Exception as e:

            QMessageBox.warning(
                self,
                "Export",
                str(e),
            )

    # =====================================================
    # REFRESH BUTTON
    # =====================================================

    def manual_refresh(self):

        self.refresh_data()

    # =====================================================
    # SIGNALS
    # =====================================================

    def connect_signals(self):

        self.refresh_btn.clicked.connect(
            self.manual_refresh
        )

        self.export_btn.clicked.connect(
            self.export_data
        )

        self.search.textChanged.connect(
            self.search_data
        )

        self.strategy.currentIndexChanged.connect(
            self.search_data
        )

        if hasattr(
            self.table,
            "stock_double_clicked",
        ):

            self.table.stock_double_clicked.connect(
                self.open_stock
            )

    # =====================================================
    # OPEN STOCK
    # =====================================================

    def open_stock(self, symbol):

        QMessageBox.information(

            self,

            "Selected Stock",

            f"{symbol}"

        )

    # =====================================================
    # AUTO REFRESH
    # =====================================================

    def start_auto_refresh(self):

        self.timer.start(
            self.AUTO_REFRESH
        )

    def stop_auto_refresh(self):

        self.timer.stop()

    # =====================================================
    # PUBLIC HELPERS
    # =====================================================

    def refresh_table(self):

        self.load_opportunities()

    def refresh_cards(self):

        self.update_cards()

    def refresh_statistics(self):

        self.update_statistics()

    def refresh_panels(self):

        self.update_momentum()

        self.update_watchlist()

    def selected_stock(self):

        if hasattr(
            self.table,
            "selected_stock",
        ):

            return self.table.selected_stock()

        return None

    def scanner_info(self):

        return {

            "stocks": len(self.opportunities),

            "updated": datetime.now(),

            "strategy": self.strategy.currentText(),

        }

    def statistics(self):

        return self.scanner_info()

    def refresh_if_required(self):

        self.refresh_data()

    # =====================================================
    # EVENTS
    # =====================================================

    def closeEvent(self, event):

        self.stop_auto_refresh()

        event.accept()

    def __del__(self):

        try:

            self.stop_auto_refresh()

        except Exception:

            pass

    def __repr__(self):

        return "<IntradayPage>"
