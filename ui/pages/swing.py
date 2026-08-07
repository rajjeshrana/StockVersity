"""
==========================================================
StockVersity Scanner Pro v3
Professional Swing Scanner
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


class SwingPage(QWidget):

    AUTO_REFRESH = 120000

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

        panel.setObjectName("SwingPanel")

        panel.setStyleSheet("""
        QFrame#SwingPanel{

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

        title = QLabel("Swing Scanner")

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

        self.pattern = QComboBox()

        self.pattern.addItems([

            "All Patterns",

            "VCP",

            "Cup & Handle",

            "Bull Flag",

            "Falling Wedge",

            "Ascending Triangle",

            "Breakout",

        ])

        self.pattern.setFixedHeight(38)

        header.addWidget(self.pattern)

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
            "Swing Stocks",
            "0",
            "ðŸ“ˆ"
        )

        self.buy_card = InfoCard(
            "BUY Setup",
            "0",
            "ðŸŸ¢"
        )

        self.breakout_card = InfoCard(
            "Fresh Breakout",
            "0",
            "ðŸš€"
        )

        self.vcp_card = InfoCard(
            "VCP Pattern",
            "0",
            "ðŸ“Š"
        )

        self.volume_card = InfoCard(
            "Volume Spike",
            "0",
            "âš¡"
        )

        self.ai_card = InfoCard(
            "AI Qualified",
            "0",
            "ðŸ¤–"
        )

        cards.addWidget(self.total_card,0,0)
        cards.addWidget(self.buy_card,0,1)
        cards.addWidget(self.breakout_card,0,2)
        cards.addWidget(self.vcp_card,0,3)
        cards.addWidget(self.volume_card,0,4)
        cards.addWidget(self.ai_card,0,5)

        root.addLayout(cards)
                # =================================================
        # SWING PANELS
        # =================================================

        panel_layout = QHBoxLayout()

        panel_layout.setSpacing(16)

        # ================================================
        # Swing Statistics
        # ================================================

        stats_panel, stats_layout = self.create_panel(
            "Swing Statistics"
        )

        self.lbl_scanned = QLabel("Stocks Scanned : 0")
        self.lbl_breakout = QLabel("Breakouts : 0")
        self.lbl_avg_ai = QLabel("Average AI Score : 0")
        self.lbl_avg_rr = QLabel("Average R:R : 0")

        for lbl in (
            self.lbl_scanned,
            self.lbl_breakout,
            self.lbl_avg_ai,
            self.lbl_avg_rr,
        ):

            lbl.setMinimumHeight(28)

            stats_layout.addWidget(lbl)

        stats_layout.addStretch()

        panel_layout.addWidget(
            stats_panel,
            2,
        )

        # ================================================
        # Top Swing Picks
        # ================================================

        picks_panel, picks_layout = self.create_panel(
            "Top Swing Picks"
        )

        self.top_picks = QListWidget()

        self.top_picks.setMinimumHeight(190)

        picks_layout.addWidget(
            self.top_picks
        )

        panel_layout.addWidget(
            picks_panel,
            2,
        )

        # ================================================
        # High Conviction
        # ================================================

        conviction_panel, conviction_layout = self.create_panel(
            "High Conviction"
        )

        self.watch_list = QListWidget()

        self.watch_list.setMinimumHeight(190)

        conviction_layout.addWidget(
            self.watch_list
        )

        panel_layout.addWidget(
            conviction_panel,
            2,
        )

        root.addLayout(panel_layout)

        # =================================================
        # OPPORTUNITIES TABLE
        # =================================================

        table_panel, table_layout = self.create_panel(
            "Swing Opportunities"
        )

        self.table = OpportunitiesTable()

        self.table.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

        table_layout.addWidget(
            self.table
        )

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

            self.update_top_picks()

            self.update_watchlist()

            self.last_update.setText(

                "Updated : " +

                datetime.now().strftime("%H:%M:%S")

            )

        except Exception as e:

            QMessageBox.warning(

                self,

                "Swing Scanner",

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

        breakout = 0

        vcp = 0

        volume = 0

        ai = 0

        for item in self.opportunities:

            signal = str(

                getattr(item, "signal", "")

            ).upper()

            pattern = str(

                getattr(item, "pattern", "")

            ).upper()

            score = float(

                getattr(item, "ai_score", 0)

            )

            vol = float(

                getattr(item, "volume_ratio", 0)

            )

            if signal == "BUY":

                buy += 1

            if "BREAKOUT" in pattern:

                breakout += 1

            if "VCP" in pattern:

                vcp += 1

            if vol >= 2:

                volume += 1

            if score >= 70:

                ai += 1

        self.total_card.update_card(total)

        self.buy_card.update_card(

            buy,

            status="BUY",

        )

        self.breakout_card.update_card(

            breakout

        )

        self.vcp_card.update_card(

            vcp

        )

        self.volume_card.update_card(

            volume

        )

        self.ai_card.update_card(

            ai,

            status="AI",

        )

    # =====================================================
    # SWING STATISTICS
    # =====================================================

    def update_statistics(self):

        total = len(self.opportunities)

        if total == 0:

            self.lbl_scanned.setText(

                "Stocks Scanned : 0"

            )

            self.lbl_breakout.setText(

                "Breakouts : 0"

            )

            self.lbl_avg_ai.setText(

                "Average AI Score : 0"

            )

            self.lbl_avg_rr.setText(

                "Average R:R : 0"

            )

            return

        breakout = 0

        ai_total = 0

        rr_total = 0

        rr_count = 0

        for item in self.opportunities:

            pattern = str(

                getattr(item, "pattern", "")

            ).upper()

            if "BREAKOUT" in pattern:

                breakout += 1

            ai_total += float(

                getattr(item, "ai_score", 0)

            )

            rr = getattr(

                item,

                "risk_reward",

                None,

            )

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

            round(

                rr_total / rr_count,

                2,

            )

            if rr_count

            else 0

        )

        self.lbl_scanned.setText(

            f"Stocks Scanned : {total}"

        )

        self.lbl_breakout.setText(

            f"Breakouts : {breakout}"

        )

        self.lbl_avg_ai.setText(

            f"Average AI Score : {avg_ai}"

        )

        self.lbl_avg_rr.setText(

            f"Average R:R : {avg_rr}"

        )

    # =====================================================
    # TOP PICKS
    # =====================================================

    def update_top_picks(self):

        self.top_picks.clear()

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

            self.top_picks.addItem(

                QListWidgetItem(

                    f"{symbol}   ({score})"

                )

            )

    # =====================================================
    # HIGH CONVICTION
    # =====================================================

    def update_watchlist(self):

        self.watch_list.clear()

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

        for item in ranked:

            score = float(

                getattr(

                    item,

                    "ai_score",

                    0,

                )

            )

            if score < 85:

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
    # SEARCH & FILTER
    # =====================================================

    def search_data(self):

        text = self.search.text().strip().upper()

        pattern = self.pattern.currentText().upper()

        if (
            not text
            and pattern == "ALL PATTERNS"
        ):

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

            stock_pattern = str(
                getattr(item, "pattern", "")
            ).upper()

            if text:

                if (
                    text not in symbol
                    and text not in company
                    and text not in sector
                ):

                    continue

            if pattern != "ALL PATTERNS":

                if pattern not in stock_pattern:

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
    # MANUAL REFRESH
    # =====================================================

    def manual_refresh(self):

        self.refresh_data()

    # =====================================================
    # SIGNAL CONNECTIONS
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

        self.pattern.currentIndexChanged.connect(
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

            "Swing Stock",

            f"Selected : {symbol}"

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
    # PUBLIC METHODS
    # =====================================================

    def refresh_table(self):

        self.load_opportunities()

    def refresh_cards(self):

        self.update_cards()

    def refresh_statistics(self):

        self.update_statistics()

    def refresh_panels(self):

        self.update_top_picks()

        self.update_watchlist()

    def selected_stock(self):

        if hasattr(
            self.table,
            "selected_stock",
        ):

            return self.table.selected_stock()

        return None

    def swing_info(self):

        return {

            "stocks": len(self.opportunities),

            "updated": datetime.now(),

            "pattern": self.pattern.currentText(),

        }

    def statistics(self):

        return self.swing_info()

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

        return "<SwingPage>"
