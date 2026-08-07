"""
=========================================================
StockVersity Scanner Pro
Professional Opportunities Table
Version : 4.0
Powered By : AI
=========================================================
"""

from __future__ import annotations

import csv
from typing import List, Dict

from PySide6.QtCore import (
    Qt,
    Signal,
)

from PySide6.QtGui import (
    QColor,
    QAction,
)

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QMenu,
    QFileDialog,
)


class OpportunitiesTable(QWidget):
    """
    Professional Institutional Trading Table
    """

    stockDoubleClicked = Signal(dict)
    stockSelected = Signal(dict)
    refreshRequested = Signal()

    HEADERS = [

        "Rank",
        "Symbol",
        "Signal",
        "Pattern",
        "Sector",
        "Entry",
        "SL",
        "Target",
        "RR",
        "Confidence",
        "Score",
        "Volume",
        "Timeframe"

    ]

    # =====================================================
    # INIT
    # =====================================================

    def __init__(self, parent=None):

        super().__init__(parent)

        self.data: List[Dict] = []

        self.filtered_data: List[Dict] = []

        self.build_ui()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(self):

        root = QVBoxLayout(self)

        root.setContentsMargins(

            0,

            0,

            0,

            0

        )

        root.setSpacing(8)

        self.build_toolbar()

        self.build_table()

        self.status = QLabel(

            "0 Opportunities"

        )

        root.addWidget(

            self.status

        )

    # =====================================================
    # TOOLBAR
    # =====================================================

    def build_toolbar(self):

        toolbar = QHBoxLayout()

        self.search = QLineEdit()

        self.search.setPlaceholderText(

            "Search Symbol..."

        )

        self.search.textChanged.connect(

            self.apply_filters

        )

        self.signal_filter = QComboBox()

        self.signal_filter.addItems(

            [

                "All",

                "BUY",

                "SELL",

                "HOLD"

            ]

        )

        self.signal_filter.currentTextChanged.connect(

            self.apply_filters

        )

        self.timeframe_filter = QComboBox()

        self.timeframe_filter.addItems(

            [

                "All",

                "Intraday",

                "Swing",

                "Positional"

            ]

        )

        self.timeframe_filter.currentTextChanged.connect(

            self.apply_filters

        )

        self.refresh_button = QPushButton(

            "Refresh"

        )

        self.refresh_button.clicked.connect(

            self.refreshRequested.emit

        )

        toolbar.addWidget(

            self.search

        )

        toolbar.addWidget(

            self.signal_filter

        )

        toolbar.addWidget(

            self.timeframe_filter

        )

        toolbar.addStretch()

        toolbar.addWidget(

            self.refresh_button

        )

        self.layout().addLayout(

            toolbar

        )

    # =====================================================
    # TABLE
    # =====================================================

    def build_table(self):

        self.table = QTableWidget()

        self.table.setColumnCount(

            len(self.HEADERS)

        )

        self.table.setHorizontalHeaderLabels(

            self.HEADERS

        )

        self.table.setSelectionBehavior(

            QTableWidget.SelectRows

        )

        self.table.setSelectionMode(

            QTableWidget.SingleSelection

        )

        self.table.setAlternatingRowColors(

            True

        )

        self.table.setSortingEnabled(

            True

        )

        self.table.verticalHeader().setVisible(

            False

        )

        header = self.table.horizontalHeader()

        header.setStretchLastSection(

            True

        )

        header.setSectionResizeMode(

            QHeaderView.ResizeToContents

        )

        self.table.doubleClicked.connect(

            self.handle_double_click

        )

        self.table.itemSelectionChanged.connect(

            self.handle_selection

        )

        self.table.setContextMenuPolicy(

            Qt.CustomContextMenu

        )

        self.table.customContextMenuRequested.connect(

            self.show_context_menu

        )

        self.layout().addWidget(

            self.table
        )
            # =====================================================
    # SET DATA
    # =====================================================

    def set_data(
        self,
        data: List[Dict]
    ):

        self.data = data or []

        self.apply_filters()

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(self):

        self.data.clear()

        self.filtered_data.clear()

        self.table.setRowCount(0)

        self.status.setText(
            "0 Opportunities"
        )

    # =====================================================
    # APPLY FILTERS
    # =====================================================

    def apply_filters(self):

        symbol = self.search.text().strip().upper()

        signal = self.signal_filter.currentText()

        timeframe = self.timeframe_filter.currentText()

        filtered = []

        for stock in self.data:

            if symbol:

                if symbol not in str(
                    stock.get(
                        "symbol",
                        ""
                    )
                ).upper():

                    continue

            if signal != "All":

                if str(
                    stock.get(
                        "signal",
                        ""
                    )
                ).upper() != signal:

                    continue

            if timeframe != "All":

                trade_type = str(
                    stock.get(
                        "trade_type",
                        ""
                    )
                ).lower()

                if trade_type != timeframe.lower():

                    continue

            filtered.append(stock)

        self.filtered_data = filtered

        self.populate_table()

    # =====================================================
    # POPULATE TABLE
    # =====================================================

    def populate_table(self):

        self.table.setSortingEnabled(False)

        self.table.setUpdatesEnabled(False)

        self.table.setRowCount(

            len(self.filtered_data)

        )

        for row, stock in enumerate(

            self.filtered_data

        ):

            self.populate_row(

                row,

                stock

            )

        self.table.setUpdatesEnabled(True)

        self.table.setSortingEnabled(True)

        self.status.setText(

            f"{len(self.filtered_data)} Opportunities"

        )

    # =====================================================
    # POPULATE ROW
    # =====================================================

    def populate_row(
        self,
        row: int,
        stock: Dict
    ):

        values = [

            stock.get("rank", row + 1),

            stock.get("symbol", ""),

            stock.get("signal", ""),

            stock.get("pattern", ""),

            stock.get("sector", ""),

            stock.get("entry", ""),

            stock.get("sl", ""),

            stock.get("target", ""),

            stock.get("rr", ""),

            stock.get("confidence", ""),

            stock.get("score", ""),

            stock.get("volume", ""),

            stock.get("timeframe", "")

        ]

        signal = str(

            stock.get(

                "signal",

                ""

            )

        ).upper()

        for column, value in enumerate(values):

            item = QTableWidgetItem(

                str(value)

            )

            item.setTextAlignment(

                Qt.AlignCenter

            )

            if signal == "BUY":

                item.setBackground(

                    QColor(

                        225,

                        255,

                        225

                    )

                )

                if column == 2:

                    item.setForeground(

                        QColor(

                            0,

                            140,

                            0

                        )

                    )

            elif signal == "SELL":

                item.setBackground(

                    QColor(

                        255,

                        235,

                        235

                    )

                )

                if column == 2:

                    item.setForeground(

                        QColor(

                            180,

                            0,

                            0

                        )

                    )

            else:

                if column == 2:

                    item.setForeground(

                        QColor(

                            180,

                            120,

                            0

                        )

                    )

            self.table.setItem(

                row,

                column,

                item

            )

    # =====================================================
    # UPDATE SINGLE ROW
    # =====================================================

    def update_row(
        self,
        symbol: str,
        data: Dict
    ):

        for index, stock in enumerate(self.data):

            if stock.get("symbol") == symbol:

                self.data[index].update(data)

                break

        self.apply_filters()
            # =====================================================
    # HANDLE DOUBLE CLICK
    # =====================================================

    def handle_double_click(self):

        row = self.table.currentRow()

        if row < 0:

            return

        if row >= len(self.filtered_data):

            return

        self.stockDoubleClicked.emit(

            self.filtered_data[row]

        )

    # =====================================================
    # HANDLE SELECTION
    # =====================================================

    def handle_selection(self):

        row = self.table.currentRow()

        if row < 0:

            return

        if row >= len(self.filtered_data):

            return

        self.stockSelected.emit(

            self.filtered_data[row]

        )

    # =====================================================
    # CONTEXT MENU
    # =====================================================

    def show_context_menu(self, position):

        row = self.table.currentRow()

        if row < 0:

            return

        menu = QMenu(self)

        open_chart = QAction(

            "Open TradingView",

            self

        )

        copy_symbol = QAction(

            "Copy Symbol",

            self

        )

        add_watchlist = QAction(

            "Add to Watchlist",

            self

        )

        remove_row = QAction(

            "Remove",

            self

        )

        export_selected = QAction(

            "Export Selected",

            self

        )

        open_chart.triggered.connect(

            self.open_tradingview

        )

        copy_symbol.triggered.connect(

            self.copy_symbol

        )

        add_watchlist.triggered.connect(

            self.add_to_watchlist

        )

        remove_row.triggered.connect(

            self.remove_selected

        )

        export_selected.triggered.connect(

            self.export_selected_rows

        )

        menu.addAction(open_chart)

        menu.addSeparator()

        menu.addAction(copy_symbol)

        menu.addAction(add_watchlist)

        menu.addSeparator()

        menu.addAction(export_selected)

        menu.addSeparator()

        menu.addAction(remove_row)

        menu.exec(

            self.table.viewport().mapToGlobal(position)

        )

    # =====================================================
    # OPEN TRADINGVIEW
    # =====================================================

    def open_tradingview(self):

        row = self.table.currentRow()

        if row < 0:

            return

        symbol = self.filtered_data[row].get(

            "symbol",

            ""

        )

        import webbrowser

        webbrowser.open(

            f"https://www.tradingview.com/chart/?symbol=NSE:{symbol}"

        )

    # =====================================================
    # COPY SYMBOL
    # =====================================================

    def copy_symbol(self):

        row = self.table.currentRow()

        if row < 0:

            return

        symbol = self.filtered_data[row].get(

            "symbol",

            ""

        )

        from PySide6.QtWidgets import QApplication

        QApplication.clipboard().setText(symbol)

    # =====================================================
    # WATCHLIST
    # =====================================================

    def add_to_watchlist(self):

        row = self.table.currentRow()

        if row < 0:

            return

        stock = self.filtered_data[row]

        if not hasattr(

            self,

            "_watchlist"

        ):

            self._watchlist = []

        if stock not in self._watchlist:

            self._watchlist.append(stock)

    # =====================================================
    # REMOVE
    # =====================================================

    def remove_selected(self):

        row = self.table.currentRow()

        if row < 0:

            return

        stock = self.filtered_data[row]

        if stock in self.data:

            self.data.remove(stock)

        self.apply_filters()

    # =====================================================
    # EXPORT SELECTED
    # =====================================================

    def export_selected_rows(self):

        row = self.table.currentRow()

        if row < 0:

            return

        filename, _ = QFileDialog.getSaveFileName(

            self,

            "Export Selected",

            "selected_stock.csv",

            "CSV Files (*.csv)"

        )

        if not filename:

            return

        stock = self.filtered_data[row]

        with open(

            filename,

            "w",

            newline="",

            encoding="utf-8"

        ) as file:

            writer = csv.DictWriter(

                file,

                fieldnames=stock.keys()

            )

            writer.writeheader()

            writer.writerow(stock)

    # =====================================================
    # KEYBOARD SHORTCUTS
    # =====================================================

    def keyPressEvent(self, event):

        if event.key() in (

            Qt.Key_Return,

            Qt.Key_Enter

        ):

            self.handle_double_click()

            return

        if event.key() == Qt.Key_Delete:

            self.remove_selected()

            return

        if (

            event.modifiers() == Qt.ControlModifier

            and event.key() == Qt.Key_C

        ):

            self.copy_symbol()

            return

        super().keyPressEvent(event)
            # =====================================================
    # SORT BY SCORE
    # =====================================================

    def sort_by_score(
        self,
        descending: bool = True
    ):

        self.filtered_data.sort(

            key=lambda x: float(
                x.get(
                    "score",
                    0
                )
            ),

            reverse=descending

        )

        self.populate_table()

    # =====================================================
    # SORT BY CONFIDENCE
    # =====================================================

    def sort_by_confidence(
        self,
        descending: bool = True
    ):

        self.filtered_data.sort(

            key=lambda x: float(
                x.get(
                    "confidence",
                    0
                )
            ),

            reverse=descending

        )

        self.populate_table()

    # =====================================================
    # SORT BY RISK REWARD
    # =====================================================

    def sort_by_rr(
        self,
        descending: bool = True
    ):

        self.filtered_data.sort(

            key=lambda x: float(
                x.get(
                    "rr",
                    0
                )
            ),

            reverse=descending

        )

        self.populate_table()

    # =====================================================
    # RANK BADGE
    # =====================================================

    def rank_badge(
        self,
        rank: int
    ):

        if rank == 1:
            return "🥇"

        if rank == 2:
            return "🥈"

        if rank == 3:
            return "🥉"

        return str(rank)

    # =====================================================
    # COLOR ROW
    # =====================================================

    def apply_row_style(
        self,
        row: int,
        stock: Dict
    ):

        confidence = float(
            stock.get(
                "confidence",
                0
            )
        )

        rr = float(
            stock.get(
                "rr",
                0
            )
        )

        volume = float(
            stock.get(
                "relative_volume",
                stock.get(
                    "volume",
                    0
                )
            )
        )

        # ------------------------------------------
        # Rank Badge
        # ------------------------------------------

        rank_item = self.table.item(
            row,
            0
        )

        if rank_item:

            try:

                rank = int(
                    stock.get(
                        "rank",
                        row + 1
                    )
                )

            except Exception:

                rank = row + 1

            rank_item.setText(

                self.rank_badge(rank)

            )

        # ------------------------------------------
        # Confidence
        # ------------------------------------------

        confidence_item = self.table.item(
            row,
            9
        )

        if confidence_item:

            if confidence >= 90:

                confidence_item.setBackground(
                    QColor(
                        0,
                        180,
                        0
                    )
                )

                confidence_item.setForeground(
                    QColor(
                        255,
                        255,
                        255
                    )
                )

            elif confidence >= 75:

                confidence_item.setBackground(
                    QColor(
                        180,
                        255,
                        180
                    )
                )

        # ------------------------------------------
        # Risk Reward
        # ------------------------------------------

        rr_item = self.table.item(
            row,
            8
        )

        if rr_item:

            if rr >= 3:

                rr_item.setBackground(
                    QColor(
                        200,
                        255,
                        200
                    )
                )

            elif rr < 1.5:

                rr_item.setBackground(
                    QColor(
                        255,
                        220,
                        220
                    )
                )

        # ------------------------------------------
        # Relative Volume
        # ------------------------------------------

        volume_item = self.table.item(
            row,
            11
        )

        if volume_item:

            if volume >= 3:

                volume_item.setBackground(
                    QColor(
                        255,
                        245,
                        180
                    )
                )

    # =====================================================
    # FLASH UPDATED ROW
    # =====================================================

    def flash_row(
        self,
        row: int
    ):

        for column in range(

            self.table.columnCount()

        ):

            item = self.table.item(
                row,
                column
            )

            if item:

                item.setBackground(

                    QColor(
                        255,
                        255,
                        120
                    )

                )

    # =====================================================
    # UPDATE ROW WITHOUT RELOAD
    # =====================================================

    def refresh_row(
        self,
        symbol: str
    ):

        for row, stock in enumerate(

            self.filtered_data

        ):

            if stock.get(

                "symbol"

            ) == symbol:

                self.populate_row(

                    row,

                    stock

                )

                self.apply_row_style(

                    row,

                    stock

                )

                self.flash_row(

                    row

                )

                break

    # =====================================================
    # APPLY STYLES
    # =====================================================

    def apply_styles(self):

        for row, stock in enumerate(

            self.filtered_data

        ):

            self.apply_row_style(

                row,

                stock

            )
                # =====================================================
    # MULTI SELECTION
    # =====================================================

    def enable_multi_selection(self):

        self.table.setSelectionMode(

            QTableWidget.ExtendedSelection

        )

    # =====================================================
    # SINGLE SELECTION
    # =====================================================

    def enable_single_selection(self):

        self.table.setSelectionMode(

            QTableWidget.SingleSelection

        )

    # =====================================================
    # SELECTED STOCKS
    # =====================================================

    def selected_stocks(self):

        rows = sorted(

            {

                index.row()

                for index in self.table.selectedIndexes()

            }

        )

        stocks = []

        for row in rows:

            if row < len(self.filtered_data):

                stocks.append(

                    self.filtered_data[row]

                )

        return stocks

    # =====================================================
    # COPY ROW
    # =====================================================

    def copy_selected_rows(self):

        rows = self.selected_stocks()

        if not rows:

            return

        from PySide6.QtWidgets import QApplication

        lines = []

        headers = list(rows[0].keys())

        lines.append("\t".join(headers))

        for stock in rows:

            lines.append(

                "\t".join(

                    str(stock.get(h, ""))

                    for h in headers

                )

            )

        QApplication.clipboard().setText(

            "\n".join(lines)

        )

    # =====================================================
    # EXPORT CSV
    # =====================================================

    def export_csv(self):

        if not self.filtered_data:

            return

        filename, _ = QFileDialog.getSaveFileName(

            self,

            "Export CSV",

            "opportunities.csv",

            "CSV Files (*.csv)"

        )

        if not filename:

            return

        with open(

            filename,

            "w",

            newline="",

            encoding="utf-8"

        ) as file:

            writer = csv.DictWriter(

                file,

                fieldnames=self.filtered_data[0].keys()

            )

            writer.writeheader()

            writer.writerows(

                self.filtered_data

            )

    # =====================================================
    # EXPORT EXCEL
    # =====================================================

    def export_excel(self):

        try:

            from openpyxl import Workbook

        except ImportError:

            return

        if not self.filtered_data:

            return

        filename, _ = QFileDialog.getSaveFileName(

            self,

            "Export Excel",

            "opportunities.xlsx",

            "Excel (*.xlsx)"

        )

        if not filename:

            return

        workbook = Workbook()

        sheet = workbook.active

        headers = list(

            self.filtered_data[0].keys()

        )

        sheet.append(headers)

        for stock in self.filtered_data:

            sheet.append(

                [

                    stock.get(h, "")

                    for h in headers

                ]

            )

        workbook.save(filename)

    # =====================================================
    # PRINT TABLE
    # =====================================================

    def print_summary(self):

        for stock in self.filtered_data:

            print(

                stock

            )

    # =====================================================
    # SAVE WATCHLIST
    # =====================================================

    def save_watchlist(self):

        if not hasattr(

            self,

            "_watchlist"

        ):

            return

        filename, _ = QFileDialog.getSaveFileName(

            self,

            "Save Watchlist",

            "watchlist.csv",

            "CSV Files (*.csv)"

        )

        if not filename:

            return

        with open(

            filename,

            "w",

            newline="",

            encoding="utf-8"

        ) as file:

            writer = csv.DictWriter(

                file,

                fieldnames=self._watchlist[0].keys()

            )

            writer.writeheader()

            writer.writerows(

                self._watchlist

            )

    # =====================================================
    # LOAD WATCHLIST
    # =====================================================

    def load_watchlist(

        self,

        filename: str

    ):

        with open(

            filename,

            newline="",

            encoding="utf-8"

        ) as file:

            reader = csv.DictReader(file)

            self._watchlist = list(reader)

    # =====================================================
    # TABLE PREFERENCES
    # =====================================================

    def save_preferences(self):

        return {

            "signal":

                self.signal_filter.currentText(),

            "timeframe":

                self.timeframe_filter.currentText(),

            "search":

                self.search.text()

        }

    # =====================================================
    # RESTORE PREFERENCES
    # =====================================================

    def restore_preferences(

        self,

        preferences: dict

    ):

        if not preferences:

            return

        self.signal_filter.setCurrentText(

            preferences.get(

                "signal",

                "All"

            )

        )

        self.timeframe_filter.setCurrentText(

            preferences.get(

                "timeframe",

                "All"

            )

        )

        self.search.setText(

            preferences.get(

                "search",

                ""

            )

        )

    # =====================================================
    # ADVANCED FILTERS
    # =====================================================

    def filter_by_sector(

        self,

        sector: str

    ):

        self.filtered_data = [

            stock

            for stock in self.data

            if str(

                stock.get(

                    "sector",

                    ""

                )

            ).lower() == sector.lower()

        ]

        self.populate_table()

    def filter_by_pattern(

        self,

        pattern: str

    ):

        self.filtered_data = [

            stock

            for stock in self.data

            if str(

                stock.get(

                    "pattern",

                    ""

                )

            ).lower() == pattern.lower()

        ]

        self.populate_table()

    def filter_by_min_score(

        self,

        score: float

    ):

        self.filtered_data = [

            stock

            for stock in self.data

            if float(

                stock.get(

                    "score",

                    0

                )

            ) >= score

        ]

        self.populate_table()

    def filter_by_min_confidence(

        self,

        confidence: float

    ):

        self.filtered_data = [

            stock

            for stock in self.data

            if float(

                stock.get(

                    "confidence",

                    0

                )

            ) >= confidence

        ]

        self.populate_table()
            # =====================================================
    # LIVE UPDATE
    # =====================================================

    def live_update(
        self,
        updates: List[Dict]
    ):

        if not updates:
            return

        update_map = {
            stock.get("symbol"): stock
            for stock in updates
        }

        for stock in self.data:

            symbol = stock.get("symbol")

            if symbol in update_map:

                stock.update(
                    update_map[symbol]
                )

        self.refresh_visible_rows()

    # =====================================================
    # REFRESH VISIBLE ROWS
    # =====================================================

    def refresh_visible_rows(self):

        self.table.setUpdatesEnabled(False)

        for row, stock in enumerate(self.filtered_data):

            self.populate_row(
                row,
                stock
            )

            self.apply_row_style(
                row,
                stock
            )

        self.table.setUpdatesEnabled(True)

        self.table.viewport().update()

    # =====================================================
    # AI SCORE HEATMAP
    # =====================================================

    def apply_score_heatmap(self):

        for row, stock in enumerate(self.filtered_data):

            score = float(
                stock.get(
                    "score",
                    0
                )
            )

            item = self.table.item(
                row,
                10
            )

            if not item:
                continue

            if score >= 90:

                item.setBackground(
                    QColor(0, 160, 0)
                )

                item.setForeground(
                    QColor(255, 255, 255)
                )

            elif score >= 80:

                item.setBackground(
                    QColor(120, 220, 120)
                )

            elif score >= 60:

                item.setBackground(
                    QColor(255, 235, 150)
                )

            else:

                item.setBackground(
                    QColor(255, 210, 210)
                )

    # =====================================================
    # CONFIDENCE HEATMAP
    # =====================================================

    def apply_confidence_heatmap(self):

        for row, stock in enumerate(self.filtered_data):

            confidence = float(
                stock.get(
                    "confidence",
                    0
                )
            )

            item = self.table.item(
                row,
                9
            )

            if not item:
                continue

            if confidence >= 90:

                item.setBackground(
                    QColor(40, 170, 40)
                )

                item.setForeground(
                    QColor(255, 255, 255)
                )

            elif confidence >= 75:

                item.setBackground(
                    QColor(170, 255, 170)
                )

            elif confidence >= 60:

                item.setBackground(
                    QColor(255, 240, 180)
                )

            else:

                item.setBackground(
                    QColor(255, 215, 215)
                )

    # =====================================================
    # FLASH NEW SIGNALS
    # =====================================================

    def flash_new_signals(self):

        for row, stock in enumerate(self.filtered_data):

            if stock.get(
                "new_signal",
                False
            ):

                self.flash_row(row)

    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    def remove_duplicates(self):

        unique = {}

        for stock in self.data:

            symbol = stock.get("symbol")

            if symbol:

                unique[symbol] = stock

        self.data = list(unique.values())

        self.apply_filters()

    # =====================================================
    # PAGINATION
    # =====================================================

    def set_page(
        self,
        page: int,
        page_size: int = 100
    ):

        start = page * page_size

        end = start + page_size

        self.filtered_data = self.data[start:end]

        self.populate_table()

    # =====================================================
    # PERFORMANCE MODE
    # =====================================================

    def enable_performance_mode(self):

        self.table.setUpdatesEnabled(False)

        self.table.setSortingEnabled(False)

    # =====================================================
    # NORMAL MODE
    # =====================================================

    def disable_performance_mode(self):

        self.table.setSortingEnabled(True)

        self.table.setUpdatesEnabled(True)

    # =====================================================
    # BULK UPDATE
    # =====================================================

    def bulk_update(
        self,
        stocks: List[Dict]
    ):

        self.enable_performance_mode()

        self.live_update(stocks)

        self.apply_score_heatmap()

        self.apply_confidence_heatmap()

        self.flash_new_signals()

        self.disable_performance_mode()

    # =====================================================
    # TABLE STATISTICS
    # =====================================================

    def statistics(self):

        return {

            "rows":
                len(self.filtered_data),

            "total":
                len(self.data),

            "watchlist":
                len(
                    getattr(
                        self,
                        "_watchlist",
                        []
                    )
                ),

            "selection":
                len(
                    self.selected_stocks()
                )

        }
        # =====================================================
    # AUTO REFRESH
    # =====================================================

    def set_auto_refresh(
        self,
        enabled: bool,
        interval_ms: int = 30000
    ):

        from PySide6.QtCore import QTimer

        if not hasattr(self, "_refresh_timer"):

            self._refresh_timer = QTimer(self)

            self._refresh_timer.timeout.connect(
                self.refreshRequested.emit
            )

        if enabled:

            self._refresh_timer.start(interval_ms)

        else:

            self._refresh_timer.stop()

    # =====================================================
    # APPLICATION CONTROLLER
    # =====================================================

    def attach_application_controller(
        self,
        controller
    ):

        self.application_controller = controller

    # =====================================================
    # SCANNER ENGINE
    # =====================================================

    def attach_scanner_engine(
        self,
        scanner
    ):

        self.scanner_engine = scanner

    # =====================================================
    # OPPORTUNITY RANKER
    # =====================================================

    def attach_opportunity_ranker(
        self,
        ranker
    ):

        self.opportunity_ranker = ranker

    # =====================================================
    # THEME
    # =====================================================

    def apply_theme(
        self,
        theme_name: str
    ):

        self.setProperty(
            "theme",
            theme_name
        )

        self.style().unpolish(self)

        self.style().polish(self)

        self.update()

    # =====================================================
    # SAVE STATE
    # =====================================================

    def save_state(self):

        return {

            "filters": {

                "search":
                    self.search.text(),

                "signal":
                    self.signal_filter.currentText(),

                "timeframe":
                    self.timeframe_filter.currentText()

            },

            "statistics":
                self.statistics()

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

        filters = state.get(
            "filters",
            {}
        )

        self.search.setText(

            filters.get(
                "search",
                ""
            )

        )

        self.signal_filter.setCurrentText(

            filters.get(
                "signal",
                "All"
            )

        )

        self.timeframe_filter.setCurrentText(

            filters.get(
                "timeframe",
                "All"
            )

        )

        self.apply_filters()

    # =====================================================
    # HEALTH
    # =====================================================

    def health_status(self):

        return {

            "component":
                "OpportunitiesTable",

            "healthy":
                True,

            "rows":
                self.table.rowCount(),

            "loaded":
                len(self.data),

            "filtered":
                len(self.filtered_data),

            "selection":
                len(
                    self.selected_stocks()
                )

        }

    # =====================================================
    # DIAGNOSTICS
    # =====================================================

    def diagnostics(self):

        return {

            "component":
                "OpportunitiesTable",

            "health":
                self.health_status(),

            "statistics":
                self.statistics(),

            "sorting":
                self.table.isSortingEnabled(),

            "columns":
                self.table.columnCount(),

            "rows":
                self.table.rowCount()

        }

    # =====================================================
    # KEYBOARD NAVIGATION
    # =====================================================

    def select_first_row(self):

        if self.table.rowCount():

            self.table.selectRow(0)

    def select_last_row(self):

        rows = self.table.rowCount()

        if rows:

            self.table.selectRow(rows - 1)

    def move_selection_up(self):

        row = self.table.currentRow()

        if row > 0:

            self.table.selectRow(row - 1)

    def move_selection_down(self):

        row = self.table.currentRow()

        if row < self.table.rowCount() - 1:

            self.table.selectRow(row + 1)

    # =====================================================
    # PUBLIC REFRESH
    # =====================================================

    def refresh(self):

        self.apply_filters()

        self.apply_styles()

        self.apply_score_heatmap()

        self.apply_confidence_heatmap()

        self.update()

        self.repaint()
            # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        self.clear()

        self.search.clear()

        self.signal_filter.setCurrentIndex(0)

        self.timeframe_filter.setCurrentIndex(0)

        if hasattr(self, "_watchlist"):

            self._watchlist.clear()

    # =====================================================
    # CLEAR FILTERS
    # =====================================================

    def clear_filters(self):

        self.search.clear()

        self.signal_filter.setCurrentText("All")

        self.timeframe_filter.setCurrentText("All")

        self.apply_filters()

    # =====================================================
    # COMPONENT INFORMATION
    # =====================================================

    @property
    def component_name(self):

        return "OpportunitiesTable"

    @property
    def application_name(self):

        return "StockVersity Scanner Pro"

    @property
    def version(self):

        return "4.0"

    # =====================================================
    # BUILD INFORMATION
    # =====================================================

    def build_information(self):

        return {

            "application": self.application_name,

            "component": self.component_name,

            "version": self.version,

            "powered_by": "AI"

        }

    # =====================================================
    # EXPORT TABLE
    # =====================================================

    def export_table(self):

        return {

            "build": self.build_information(),

            "statistics": self.statistics(),

            "diagnostics": self.diagnostics(),

            "rows": self.filtered_data

        }

    # =====================================================
    # IMPORT TABLE
    # =====================================================

    def import_table(

        self,

        rows: List[Dict]

    ):

        self.set_data(rows)

    # =====================================================
    # GET STOCK
    # =====================================================

    def get_stock(

        self,

        row: int

    ):

        if 0 <= row < len(self.filtered_data):

            return self.filtered_data[row]

        return None

    # =====================================================
    # GET CURRENT STOCK
    # =====================================================

    def current_stock(self):

        return self.get_stock(

            self.table.currentRow()

        )

    # =====================================================
    # ROW COUNT
    # =====================================================

    def row_count(self):

        return self.table.rowCount()

    # =====================================================
    # COLUMN COUNT
    # =====================================================

    def column_count(self):

        return self.table.columnCount()

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(self):

        self.set_auto_refresh(False)

        self.reset()

    # =====================================================
    # CLOSE EVENT
    # =====================================================

    def closeEvent(

        self,

        event

    ):

        self.shutdown()

        super().closeEvent(event)

    # =====================================================
    # STRING REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (

            f"<OpportunitiesTable "

            f"rows={len(self.filtered_data)} "

            f"loaded={len(self.data)}>"

        )


# =====================================================
# FACTORY
# =====================================================

def create_opportunities_table():

    return OpportunitiesTable()


# =====================================================
# END OF FILE
# =====================================================