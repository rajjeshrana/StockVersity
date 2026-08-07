"""
=========================================================
StockVersity Scanner Pro
Reusable Professional Table Component
Version : 4.0
Powered by AI
=========================================================
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from PySide6.QtCore import (
    Qt,
    Signal,
    QSortFilterProxyModel,
    QModelIndex,
)

from PySide6.QtGui import (
    QAction,
    QColor,
    QFont,
)

from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QMenu,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
)

from ui.theme import (
    current_theme,
    FONT_SIZE_MD,
    FONT_SIZE_SM,
)


# =========================================================
# PROFESSIONAL TABLE
# =========================================================

class ProfessionalTable(QTableWidget):

    rowActivated = Signal(int)
    selectionChangedSignal = Signal(list)
    exportRequested = Signal(str)
    refreshRequested = Signal()

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(parent)

        self._columns: List[str] = []
        self._row_data: List[Dict[str, Any]] = []

        self._setup_table()
        self._setup_header()
        self._setup_style()
        self._connect_signals()

    # =====================================================
    # TABLE CONFIGURATION
    # =====================================================

    def _setup_table(self):

        self.setAlternatingRowColors(True)

        self.setSortingEnabled(True)

        self.setMouseTracking(True)

        self.setWordWrap(False)

        self.setCornerButtonEnabled(False)

        self.setShowGrid(False)

        self.setSizePolicy(

            QSizePolicy.Expanding,

            QSizePolicy.Expanding

        )

        self.setSelectionBehavior(

            QAbstractItemView.SelectRows

        )

        self.setSelectionMode(

            QAbstractItemView.SingleSelection

        )

        self.setEditTriggers(

            QAbstractItemView.NoEditTriggers

        )

        self.setVerticalScrollMode(

            QAbstractItemView.ScrollPerPixel

        )

        self.setHorizontalScrollMode(

            QAbstractItemView.ScrollPerPixel

        )

        self.verticalHeader().setVisible(False)

    # =====================================================
    # HEADER
    # =====================================================

    def _setup_header(self):

        header = self.horizontalHeader()

        header.setSectionsMovable(True)

        header.setStretchLastSection(True)

        header.setHighlightSections(False)

        header.setDefaultAlignment(

            Qt.AlignCenter

        )

        header.setSectionResizeMode(

            QHeaderView.Interactive

        )

    # =====================================================
    # STYLING
    # =====================================================

    def _setup_style(self):

        theme = current_theme()

        font = QFont()

        font.setPointSize(FONT_SIZE_SM)

        self.setFont(font)

        self.setStyleSheet(

            f"""

            QTableWidget {{

                background:{theme.CARD};

                border:1px solid {theme.BORDER};

                border-radius:12px;

                gridline-color:{theme.BORDER};

            }}

            QHeaderView::section {{

                background:{theme.SIDEBAR};

                color:{theme.TEXT};

                font-size:{FONT_SIZE_MD}pt;

                font-weight:bold;

                border:none;

                padding:8px;

            }}

            QTableWidget::item {{

                padding:6px;

                border-bottom:1px solid {theme.BORDER};

            }}

            QTableWidget::item:selected {{

                background:{theme.PRIMARY};

                color:white;

            }}

            """

        )

    # =====================================================
    # SIGNALS
    # =====================================================

    def _connect_signals(self):

        self.itemDoubleClicked.connect(

            self._on_double_click

        )

        self.itemSelectionChanged.connect(

            self._emit_selection

        )

        self.setContextMenuPolicy(

            Qt.CustomContextMenu

        )

        self.customContextMenuRequested.connect(

            self._show_context_menu

        )

    # =====================================================
    # COLUMN API
    # =====================================================

    def set_columns(

        self,

        columns: List[str]

    ):

        self._columns = columns

        self.setColumnCount(len(columns))

        self.setHorizontalHeaderLabels(columns)

    # =====================================================
    # ROW API
    # =====================================================

    def clear_rows(self):

        self.setRowCount(0)

        self._row_data.clear()

    def append_row(

        self,

        values: List[Any]

    ):

        row = self.rowCount()

        self.insertRow(row)

        for col, value in enumerate(values):

            item = QTableWidgetItem(str(value))

            item.setTextAlignment(

                Qt.AlignCenter

            )

            self.setItem(

                row,

                col,

                item

            )

    def load_data(

        self,

        rows: List[List[Any]]

    ):

        self.setSortingEnabled(False)

        self.clear_rows()

        for row in rows:

            self.append_row(row)

        self.setSortingEnabled(True)
            # =====================================================
    # CONTEXT MENU
    # =====================================================

    def _show_context_menu(self, position):

        menu = QMenu(self)

        copy_action = QAction("Copy Selected Row", self)
        export_csv_action = QAction("Export to CSV", self)
        export_excel_action = QAction("Export to Excel", self)
        refresh_action = QAction("Refresh", self)
        clear_action = QAction("Clear Table", self)

        copy_action.triggered.connect(self.copy_selected_row)
        export_csv_action.triggered.connect(
            lambda: self.exportRequested.emit("csv")
        )
        export_excel_action.triggered.connect(
            lambda: self.exportRequested.emit("excel")
        )
        refresh_action.triggered.connect(
            self.refreshRequested.emit
        )
        clear_action.triggered.connect(
            self.clear_rows
        )

        menu.addAction(copy_action)
        menu.addSeparator()
        menu.addAction(export_csv_action)
        menu.addAction(export_excel_action)
        menu.addSeparator()
        menu.addAction(refresh_action)
        menu.addAction(clear_action)

        menu.exec(

            self.viewport().mapToGlobal(position)

        )

    # =====================================================
    # COPY ROW
    # =====================================================

    def copy_selected_row(self):

        row = self.currentRow()

        if row < 0:
            return

        values = []

        for col in range(self.columnCount()):

            item = self.item(row, col)

            values.append("" if item is None else item.text())

        from PySide6.QtWidgets import QApplication

        QApplication.clipboard().setText(

            "\t".join(values)

        )

    # =====================================================
    # ROW COLORS
    # =====================================================

    def set_row_color(

        self,

        row: int,

        color: str

    ):

        if row >= self.rowCount():

            return

        brush = QColor(color)

        for col in range(self.columnCount()):

            item = self.item(row, col)

            if item:

                item.setBackground(brush)

    # =====================================================
    # CELL COLOR
    # =====================================================

    def set_cell_color(

        self,

        row: int,

        column: int,

        color: str

    ):

        item = self.item(row, column)

        if item:

            item.setBackground(

                QColor(color)

            )

    # =====================================================
    # CELL TEXT COLOR
    # =====================================================

    def set_text_color(

        self,

        row: int,

        column: int,

        color: str

    ):

        item = self.item(row, column)

        if item:

            item.setForeground(

                QColor(color)

            )

    # =====================================================
    # CONDITIONAL FORMATTING
    # =====================================================

    def highlight_positive_negative(

        self,

        column: int

    ):

        theme = current_theme()

        for row in range(self.rowCount()):

            item = self.item(row, column)

            if not item:

                continue

            try:

                value = float(

                    item.text()

                    .replace("%", "")

                    .replace(",", "")

                )

            except Exception:

                continue

            if value > 0:

                item.setForeground(

                    QColor(theme.SUCCESS)

                )

            elif value < 0:

                item.setForeground(

                    QColor(theme.ERROR)

                )

            else:

                item.setForeground(

                    QColor(theme.TEXT)

                )

    # =====================================================
    # UPDATE ROW
    # =====================================================

    def update_row(

        self,

        row: int,

        values: List[Any]

    ):

        if row >= self.rowCount():

            return

        for column, value in enumerate(values):

            item = self.item(row, column)

            if item:

                item.setText(str(value))

            else:

                self.setItem(

                    row,

                    column,

                    QTableWidgetItem(str(value))

                )

    # =====================================================
    # FIND ROW
    # =====================================================

    def find_row(

        self,

        value: str,

        column: int = 0

    ) -> int:

        for row in range(self.rowCount()):

            item = self.item(row, column)

            if item and item.text() == value:

                return row

        return -1

    # =====================================================
    # FILTER ROWS
    # =====================================================

    def filter_rows(

        self,

        keyword: str

    ):

        keyword = keyword.lower()

        for row in range(self.rowCount()):

            visible = False

            for column in range(self.columnCount()):

                item = self.item(row, column)

                if item and keyword in item.text().lower():

                    visible = True

                    break

            self.setRowHidden(

                row,

                not visible

            )

    # =====================================================
    # CLEAR FILTER
    # =====================================================

    def clear_filter(self):

        for row in range(self.rowCount()):

            self.setRowHidden(

                row,

                False

            )

    # =====================================================
    # SELECTION UTILITIES
    # =====================================================

    def selected_rows(self) -> List[int]:

        return sorted(

            {

                index.row()

                for index in self.selectedIndexes()

            }

        )

    def selected_values(self) -> List[List[str]]:

        rows = []

        for row in self.selected_rows():

            data = []

            for col in range(self.columnCount()):

                item = self.item(row, col)

                data.append(

                    "" if item is None else item.text()

                )

            rows.append(data)

        return rows

    # =====================================================
    # SIGNAL HELPERS
    # =====================================================

    def _on_double_click(self, item):

        self.rowActivated.emit(

            item.row()

        )

    def _emit_selection(self):

        self.selectionChangedSignal.emit(

            self.selected_rows()

        )
            # =====================================================
    # MULTI COLUMN SORT
    # =====================================================

    def sort_by_column(
        self,
        column: int,
        ascending: bool = True
    ):

        order = (
            Qt.AscendingOrder
            if ascending
            else Qt.DescendingOrder
        )

        self.sortItems(column, order)

    def enable_sorting(
        self,
        enabled: bool = True
    ):

        self.setSortingEnabled(enabled)

    # =====================================================
    # COLUMN VISIBILITY
    # =====================================================

    def hide_column(
        self,
        column: int
    ):

        if 0 <= column < self.columnCount():
            self.setColumnHidden(column, True)

    def show_column(
        self,
        column: int
    ):

        if 0 <= column < self.columnCount():
            self.setColumnHidden(column, False)

    def toggle_column(
        self,
        column: int
    ):

        self.setColumnHidden(
            column,
            not self.isColumnHidden(column)
        )

    def visible_columns(self):

        return [

            i

            for i in range(self.columnCount())

            if not self.isColumnHidden(i)

        ]

    # =====================================================
    # COLUMN WIDTHS
    # =====================================================

    def save_column_widths(self):

        widths = {}

        for col in range(self.columnCount()):

            widths[col] = self.columnWidth(col)

        return widths

    def restore_column_widths(

        self,

        widths: dict

    ):

        for col, width in widths.items():

            if col < self.columnCount():

                self.setColumnWidth(

                    col,

                    width

                )

    def auto_resize_columns(self):

        self.resizeColumnsToContents()

    # =====================================================
    # FROZEN COLUMN SUPPORT
    # =====================================================

    def freeze_first_column(self):

        self.horizontalHeader().setSectionsMovable(False)

        self.setColumnWidth(

            0,

            max(

                self.columnWidth(0),

                120

            )

        )

    def unfreeze_columns(self):

        self.horizontalHeader().setSectionsMovable(True)

    # =====================================================
    # INCREMENTAL INSERT
    # =====================================================

    def insert_rows(

        self,

        rows: List[List[Any]]

    ):

        self.setUpdatesEnabled(False)

        for row in rows:

            self.append_row(row)

        self.setUpdatesEnabled(True)

        self.viewport().update()

    # =====================================================
    # BATCH UPDATE
    # =====================================================

    def begin_batch_update(self):

        self.setSortingEnabled(False)

        self.setUpdatesEnabled(False)

    def end_batch_update(self):

        self.setUpdatesEnabled(True)

        self.setSortingEnabled(True)

        self.viewport().update()

    # =====================================================
    # LIVE STREAM UPDATE
    # =====================================================

    def update_or_insert(

        self,

        key_column: int,

        key_value: str,

        values: List[Any]

    ):

        row = self.find_row(

            key_value,

            key_column

        )

        if row == -1:

            self.append_row(values)

        else:

            self.update_row(

                row,

                values

            )

    # =====================================================
    # REMOVE ROW
    # =====================================================

    def remove_row_by_key(

        self,

        key_column: int,

        key_value: str

    ):

        row = self.find_row(

            key_value,

            key_column

        )

        if row >= 0:

            self.removeRow(row)

    # =====================================================
    # PERFORMANCE MODE
    # =====================================================

    def enable_performance_mode(self):

        self.setUpdatesEnabled(False)

        self.setSortingEnabled(False)

        self.setWordWrap(False)

        self.setAlternatingRowColors(False)

    def disable_performance_mode(self):

        self.setAlternatingRowColors(True)

        self.setSortingEnabled(True)

        self.setUpdatesEnabled(True)

        self.viewport().update()

    # =====================================================
    # SCROLL HELPERS
    # =====================================================

    def scroll_to_top(self):

        self.scrollToTop()

    def scroll_to_bottom(self):

        self.scrollToBottom()

    def scroll_to_row(

        self,

        row: int

    ):

        if row < self.rowCount():

            self.scrollToItem(

                self.item(

                    row,

                    0

                )

            )

    # =====================================================
    # TABLE INFORMATION
    # =====================================================

    @property
    def total_rows(self):

        return self.rowCount()

    @property
    def total_columns(self):

        return self.columnCount()

    def table_info(self):

        return {

            "rows": self.rowCount(),

            "columns": self.columnCount(),

            "visible_columns": self.visible_columns(),

            "sorting_enabled": self.isSortingEnabled(),

            "selected_rows": self.selected_rows(),

        }
        # =====================================================
    # ROW HIGHLIGHTING
    # =====================================================

    def highlight_row(
        self,
        row: int,
        background: str,
        foreground: str = "#FFFFFF"
    ):

        if row < 0 or row >= self.rowCount():
            return

        bg = QColor(background)
        fg = QColor(foreground)

        for column in range(self.columnCount()):

            item = self.item(row, column)

            if item:

                item.setBackground(bg)
                item.setForeground(fg)

    # =====================================================
    # FLASH UPDATED CELL
    # =====================================================

    def flash_cell(
        self,
        row: int,
        column: int,
        color: str = "#FFD54F"
    ):

        item = self.item(row, column)

        if not item:
            return

        original = item.background()

        item.setBackground(QColor(color))

        from PySide6.QtCore import QTimer

        QTimer.singleShot(
            500,
            lambda: item.setBackground(original)
        )

    # =====================================================
    # LIVE UPDATE CELL
    # =====================================================

    def update_cell(
        self,
        row: int,
        column: int,
        value: Any,
        flash: bool = True
    ):

        if row >= self.rowCount():
            return

        item = self.item(row, column)

        if item is None:

            item = QTableWidgetItem()

            item.setTextAlignment(Qt.AlignCenter)

            self.setItem(row, column, item)

        previous = item.text()
        current = str(value)

        if previous != current:

            item.setText(current)

            if flash:

                self.flash_cell(row, column)

    # =====================================================
    # STATUS CELL
    # =====================================================

    def set_status(
        self,
        row: int,
        column: int,
        status: str
    ):

        theme = current_theme()

        status = status.upper()

        colors = {

            "BUY": theme.SUCCESS,

            "SELL": theme.ERROR,

            "HOLD": theme.WARNING,

            "WAIT": theme.INFO,

        }

        self.update_cell(
            row,
            column,
            status,
            flash=False
        )

        self.set_text_color(
            row,
            column,
            colors.get(
                status,
                theme.TEXT
            )
        )

    # =====================================================
    # GROUP ROWS
    # =====================================================

    def group_by_column(
        self,
        column: int
    ):

        self.sortItems(
            column,
            Qt.AscendingOrder
        )

    # =====================================================
    # PAGINATION
    # =====================================================

    def page_count(
        self,
        page_size: int
    ) -> int:

        if page_size <= 0:
            return 0

        rows = self.rowCount()

        return (rows + page_size - 1) // page_size

    def show_page(
        self,
        page: int,
        page_size: int
    ):

        start = page * page_size
        end = start + page_size

        for row in range(self.rowCount()):

            self.setRowHidden(
                row,
                not (start <= row < end)
            )

    # =====================================================
    # LAZY LOADING
    # =====================================================

    def append_batch(
        self,
        rows: List[List[Any]],
        batch_size: int = 100
    ):

        from PySide6.QtCore import QTimer

        self._lazy_rows = rows
        self._lazy_index = 0
        self._lazy_batch = batch_size

        def load():

            end = min(
                self._lazy_index + self._lazy_batch,
                len(self._lazy_rows)
            )

            self.begin_batch_update()

            while self._lazy_index < end:

                self.append_row(
                    self._lazy_rows[self._lazy_index]
                )

                self._lazy_index += 1

            self.end_batch_update()

            if self._lazy_index < len(self._lazy_rows):

                QTimer.singleShot(1, load)

        load()

    # =====================================================
    # VIEWPORT UPDATE
    # =====================================================

    def refresh_view(self):

        self.viewport().update()

    # =====================================================
    # CSV EXPORT
    # =====================================================

    def export_csv(
        self,
        filename: str
    ):

        import csv

        with open(
            filename,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            headers = [

                self.horizontalHeaderItem(i).text()

                for i in range(self.columnCount())

            ]

            writer.writerow(headers)

            for row in range(self.rowCount()):

                values = []

                for col in range(self.columnCount()):

                    item = self.item(row, col)

                    values.append(
                        "" if item is None else item.text()
                    )

                writer.writerow(values)

    # =====================================================
    # EXCEL EXPORT
    # =====================================================

    def export_excel(
        self,
        filename: str
    ):

        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active

        headers = [

            self.horizontalHeaderItem(i).text()

            for i in range(self.columnCount())

        ]

        ws.append(headers)

        for row in range(self.rowCount()):

            values = []

            for col in range(self.columnCount()):

                item = self.item(row, col)

                values.append(
                    "" if item is None else item.text()
                )

            ws.append(values)

        wb.save(filename)

    # =====================================================
    # THEME REFRESH
    # =====================================================

    def refresh_theme(self):

        self._setup_style()

        self.viewport().update()
            # =====================================================
    # COLUMN PINNING
    # =====================================================

    def pin_column(
        self,
        column: int
    ):

        if not hasattr(self, "_pinned_columns"):
            self._pinned_columns = set()

        if 0 <= column < self.columnCount():
            self._pinned_columns.add(column)

    def unpin_column(
        self,
        column: int
    ):

        if hasattr(self, "_pinned_columns"):
            self._pinned_columns.discard(column)

    def pinned_columns(self):

        return sorted(
            getattr(
                self,
                "_pinned_columns",
                set()
            )
        )

    # =====================================================
    # COLUMN SORT MODE
    # =====================================================

    def sort_numeric(
        self,
        column: int,
        reverse: bool = False
    ):

        rows = []

        for row in range(self.rowCount()):

            values = []

            for col in range(self.columnCount()):

                item = self.item(row, col)

                values.append("" if item is None else item.text())

            try:

                key = float(
                    values[column]
                    .replace(",", "")
                    .replace("%", "")
                )

            except Exception:

                key = 0

            rows.append((key, values))

        rows.sort(
            key=lambda x: x[0],
            reverse=reverse
        )

        self.begin_batch_update()

        self.clear_rows()

        for _, values in rows:
            self.append_row(values)

        self.end_batch_update()

    # =====================================================
    # ROW RANKING
    # =====================================================

    def add_rank_column(
        self,
        title="Rank"
    ):

        if self.columnCount() == 0:
            return

        self.insertColumn(0)

        self.setHorizontalHeaderItem(
            0,
            QTableWidgetItem(title)
        )

        for row in range(self.rowCount()):

            item = QTableWidgetItem(str(row + 1))

            item.setTextAlignment(Qt.AlignCenter)

            self.setItem(
                row,
                0,
                item
            )

    def refresh_ranking(self):

        if self.columnCount() == 0:
            return

        header = self.horizontalHeaderItem(0)

        if header is None:
            return

        if header.text().lower() != "rank":
            return

        for row in range(self.rowCount()):

            item = self.item(row, 0)

            if item:

                item.setText(str(row + 1))

    # =====================================================
    # SCORE COLUMN
    # =====================================================

    def update_score(
        self,
        row: int,
        column: int,
        score: float
    ):

        self.update_cell(
            row,
            column,
            f"{score:.2f}"
        )

        theme = current_theme()

        color = theme.ERROR

        if score >= 80:
            color = theme.SUCCESS

        elif score >= 60:
            color = theme.WARNING

        elif score >= 40:
            color = theme.INFO

        self.set_text_color(
            row,
            column,
            color
        )

    # =====================================================
    # TABLE STATISTICS
    # =====================================================

    def statistics(self):

        visible = 0

        hidden = 0

        selected = len(self.selected_rows())

        for row in range(self.rowCount()):

            if self.isRowHidden(row):
                hidden += 1
            else:
                visible += 1

        return {

            "rows": self.rowCount(),

            "columns": self.columnCount(),

            "visible_rows": visible,

            "hidden_rows": hidden,

            "selected_rows": selected,

            "pinned_columns": self.pinned_columns(),

        }

    # =====================================================
    # LIVE MODE
    # =====================================================

    def enable_live_mode(self):

        self._live_mode = True

    def disable_live_mode(self):

        self._live_mode = False

    def live_mode(self):

        return getattr(
            self,
            "_live_mode",
            False
        )

    # =====================================================
    # AUTO REFRESH
    # =====================================================

    def start_auto_refresh(
        self,
        interval=1000
    ):

        from PySide6.QtCore import QTimer

        if not hasattr(self, "_refresh_timer"):

            self._refresh_timer = QTimer(self)

            self._refresh_timer.timeout.connect(
                self.refreshRequested.emit
            )

        self._refresh_timer.start(interval)

    def stop_auto_refresh(self):

        if hasattr(self, "_refresh_timer"):

            self._refresh_timer.stop()

    # =====================================================
    # PERFORMANCE DIAGNOSTICS
    # =====================================================

    def diagnostics(self):

        return {

            "rows": self.rowCount(),

            "columns": self.columnCount(),

            "sorting": self.isSortingEnabled(),

            "live_mode": self.live_mode(),

            "selected": self.selected_rows(),

            "hidden_rows":

                sum(

                    self.isRowHidden(i)

                    for i in range(self.rowCount())

                ),

            "pinned_columns":

                self.pinned_columns(),

        }

    # =====================================================
    # MEMORY ESTIMATE
    # =====================================================

    def estimated_cells(self):

        return (

            self.rowCount()

            * self.columnCount()

        )

    # =====================================================
    # RESET TABLE
    # =====================================================

    def reset_table(self):

        self.stop_auto_refresh()

        self.clear_rows()

        self.clearContents()

        self.setRowCount(0)

        self.setColumnCount(0)

        if hasattr(self, "_pinned_columns"):

            self._pinned_columns.clear()

        self.viewport().update()
            # =====================================================
    # SIGNAL STRENGTH
    # =====================================================

    def set_signal_strength(
        self,
        row: int,
        column: int,
        strength: int
    ):

        strength = max(0, min(100, int(strength)))

        self.update_cell(
            row,
            column,
            f"{strength}%"
        )

        theme = current_theme()

        if strength >= 80:
            color = theme.SUCCESS
        elif strength >= 60:
            color = theme.INFO
        elif strength >= 40:
            color = theme.WARNING
        else:
            color = theme.ERROR

        self.set_text_color(
            row,
            column,
            color
        )

    # =====================================================
    # MOMENTUM COLOR
    # =====================================================

    def set_momentum(
        self,
        row: int,
        column: int,
        value: float
    ):

        self.update_cell(
            row,
            column,
            f"{value:.2f}"
        )

        theme = current_theme()

        if value > 0:
            self.set_text_color(
                row,
                column,
                theme.SUCCESS
            )
        elif value < 0:
            self.set_text_color(
                row,
                column,
                theme.ERROR
            )
        else:
            self.set_text_color(
                row,
                column,
                theme.TEXT
            )

    # =====================================================
    # BULK REPLACE
    # =====================================================

    def replace_rows(
        self,
        rows: List[List[Any]]
    ):

        self.begin_batch_update()

        self.clear_rows()

        for row in rows:

            self.append_row(row)

        self.end_batch_update()

    # =====================================================
    # SNAPSHOT
    # =====================================================

    def snapshot(self):

        data = []

        for row in range(self.rowCount()):

            values = []

            for col in range(self.columnCount()):

                item = self.item(row, col)

                values.append(
                    "" if item is None else item.text()
                )

            data.append(values)

        return data

    # =====================================================
    # RESTORE SNAPSHOT
    # =====================================================

    def restore_snapshot(
        self,
        snapshot: List[List[Any]]
    ):

        self.replace_rows(snapshot)

    # =====================================================
    # SAVE TABLE STATE
    # =====================================================

    def save_state(self):

        return {

            "column_widths":

                self.save_column_widths(),

            "hidden_columns":

                [

                    i

                    for i in range(self.columnCount())

                    if self.isColumnHidden(i)

                ],

            "sorting":

                self.isSortingEnabled(),

            "rows":

                self.snapshot(),

        }

    # =====================================================
    # RESTORE TABLE STATE
    # =====================================================

    def restore_state(
        self,
        state: dict
    ):

        if not state:
            return

        self.restore_column_widths(

            state.get(

                "column_widths",

                {}

            )

        )

        for column in state.get(

            "hidden_columns",

            []

        ):

            self.hide_column(column)

        self.replace_rows(

            state.get(

                "rows",

                []

            )

        )

        self.enable_sorting(

            state.get(

                "sorting",

                True

            )

        )

    # =====================================================
    # DASHBOARD HELPERS
    # =====================================================

    def top_row(self):

        if self.rowCount() == 0:
            return None

        return [

            self.item(0, col).text()

            if self.item(0, col)

            else ""

            for col in range(self.columnCount())

        ]

    def bottom_row(self):

        if self.rowCount() == 0:
            return None

        row = self.rowCount() - 1

        return [

            self.item(row, col).text()

            if self.item(row, col)

            else ""

            for col in range(self.columnCount())

        ]

    # =====================================================
    # SCANNER HELPERS
    # =====================================================

    def update_scanner_score(
        self,
        row: int,
        score_column: int,
        rr_column: int,
        score: float,
        rr: float
    ):

        self.update_score(
            row,
            score_column,
            score
        )

        self.update_cell(
            row,
            rr_column,
            f"{rr:.2f}"
        )

    # =====================================================
    # FIND STOCK
    # =====================================================

    def find_stock(
        self,
        symbol: str
    ) -> int:

        return self.find_row(symbol, 1)

    # =====================================================
    # REMOVE STOCK
    # =====================================================

    def remove_stock(
        self,
        symbol: str
    ):

        row = self.find_stock(symbol)

        if row >= 0:

            self.removeRow(row)

    # =====================================================
    # PERFORMANCE SUMMARY
    # =====================================================

    def performance_summary(self):

        return {

            "rows":

                self.rowCount(),

            "columns":

                self.columnCount(),

            "cells":

                self.estimated_cells(),

            "live_mode":

                self.live_mode(),

            "sorting":

                self.isSortingEnabled(),

            "selected":

                len(self.selected_rows()),

            "memory_estimate":

                f"{self.estimated_cells():,} cells"

        }

    # =====================================================
    # PREPARE FOR LIVE FEED
    # =====================================================

    def prepare_live_feed(self):

        self.enable_live_mode()

        self.enable_performance_mode()

        self.viewport().update()
            # =====================================================
    # THEME SYNCHRONIZATION
    # =====================================================

    def synchronize_theme(self):

        self.refresh_theme()

        self.viewport().update()

        self.horizontalHeader().viewport().update()

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def initialize(self):

        self._setup_table()

        self._setup_header()

        self.refresh_theme()

    # =====================================================
    # STARTUP
    # =====================================================

    def startup(self):

        self.initialize()

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(self):

        self.stop_auto_refresh()

        self.disable_live_mode()

        self.disable_performance_mode()

        self.clear_rows()

        self.viewport().update()

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        self.shutdown()

        self.initialize()

    # =====================================================
    # METADATA
    # =====================================================

    @staticmethod
    def metadata():

        return {

            "component": "ProfessionalTable",

            "application": "StockVersity Scanner Pro",

            "version": "4.0",

            "powered_by": "AI",

            "supports_live_updates": True,

            "supports_sorting": True,

            "supports_filtering": True,

            "supports_export": True,

            "supports_large_datasets": True,

        }

    # =====================================================
    # STRING REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (

            f"<ProfessionalTable "

            f"rows={self.rowCount()} "

            f"columns={self.columnCount()} "

            f"live_mode={self.live_mode()}>"

        )


# =========================================================
# FACTORY
# =========================================================

def create_table(
    columns: Optional[List[str]] = None
) -> ProfessionalTable:

    table = ProfessionalTable()

    if columns:

        table.set_columns(columns)

    table.initialize()

    return table


# =========================================================
# SPECIALIZED TABLES
# =========================================================

class ScannerTable(ProfessionalTable):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.set_columns([

            "Rank",

            "Stock",

            "Signal",

            "Pattern",

            "Score",

            "RR",

            "Price",

            "Volume",

        ])


class WatchlistTable(ProfessionalTable):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.set_columns([

            "Symbol",

            "LTP",

            "Change %",

            "Volume",

            "VWAP",

            "52W High",

            "52W Low",

        ])


class PositionsTable(ProfessionalTable):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.set_columns([

            "Symbol",

            "Qty",

            "Entry",

            "CMP",

            "PnL",

            "PnL %",

            "Status",

        ])


class AlertsTable(ProfessionalTable):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.set_columns([

            "Time",

            "Symbol",

            "Alert",

            "Price",

            "Status",

        ])


class TradesTable(ProfessionalTable):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.set_columns([

            "Trade ID",

            "Symbol",

            "Direction",

            "Entry",

            "Exit",

            "PnL",

            "Result",

        ])


# =========================================================
# PUBLIC EXPORTS
# =========================================================

__all__ = [

    "ProfessionalTable",

    "ScannerTable",

    "WatchlistTable",

    "PositionsTable",

    "AlertsTable",

    "TradesTable",

    "create_table",

]


# =========================================================
# END OF FILE
# =========================================================