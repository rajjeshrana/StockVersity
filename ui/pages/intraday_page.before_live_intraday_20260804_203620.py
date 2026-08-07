"""
StockVersity Pro
Intraday Scanner Page

File:
    ui/pages/intraday_page.py

Purpose:
    Professional intraday opportunity scanner UI.

Core scanner philosophy:
    - Small number of high-quality opportunities
    - Momentum aligned with market direction
    - Relative-volume confirmation
    - VWAP confirmation
    - EMA structure
    - ADX trend-strength filtering
    - Sector-strength confirmation
    - Gap filtering
    - ORB quality control
    - Risk/reward validation

The page is UI focused.

Live NSE/broker data should be supplied later by the
market-data and scanner service layers.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from PySide6.QtCore import (
    QPointF,
    QRectF,
    Qt,
    QTimer,
    Signal,
)

from PySide6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)

from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


logger = logging.getLogger(__name__)


# ==========================================================
# DESIGN SYSTEM
# ==========================================================

BACKGROUND = "#07101D"
BACKGROUND_SECONDARY = "#0A1423"

SURFACE = "#0D1828"
SURFACE_2 = "#101D2F"
SURFACE_HOVER = "#14253C"

BORDER = "#182A42"
BORDER_LIGHT = "#213650"

TEXT_PRIMARY = "#F3F7FC"
TEXT_SECONDARY = "#AAB8CB"
TEXT_MUTED = "#65758C"

BLUE = "#4C8DFF"
CYAN = "#35D0FF"
GREEN = "#2ED6A1"
RED = "#FF5D73"
ORANGE = "#FFB547"
PURPLE = "#9A7BFF"

FONT_FAMILY = "Segoe UI"


# ==========================================================
# HELPERS
# ==========================================================

def movement_color(
    value: float,
) -> str:

    if value > 0:
        return GREEN

    if value < 0:
        return RED

    return TEXT_MUTED


def percent_text(
    value: float,
) -> str:

    sign = "+" if value > 0 else ""

    return f"{sign}{value:.2f}%"


def score_color(
    score: int,
) -> str:

    if score >= 90:
        return GREEN

    if score >= 80:
        return CYAN

    if score >= 70:
        return ORANGE

    return TEXT_MUTED


# ==========================================================
# BASE CARD
# ==========================================================

class ScannerCard(QFrame):

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setObjectName(
            "ScannerCard"
        )

        self.setStyleSheet(
            f"""
            QFrame#ScannerCard {{
                background: {SURFACE};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
            """
        )


# ==========================================================
# SECTION TITLE
# ==========================================================

class SectionTitle(QWidget):

    def __init__(
        self,
        title: str,
        subtitle: str = "",
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            0, 0, 0, 0
        )

        layout.setSpacing(1)

        title_label = QLabel(
            title
        )

        title_label.setStyleSheet(
            f"""
            color: {TEXT_PRIMARY};
            font-size: 11px;
            font-weight: 900;
            """
        )

        layout.addWidget(
            title_label
        )

        if subtitle:

            subtitle_label = QLabel(
                subtitle
            )

            subtitle_label.setStyleSheet(
                f"""
                color: {TEXT_MUTED};
                font-size: 8px;
                """
            )

            layout.addWidget(
                subtitle_label
            )


# ==========================================================
# MARKET BIAS METER
# ==========================================================

class MarketBiasMeter(QWidget):

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self._score = 50

        self.setMinimumSize(
            260,
            92,
        )

    def set_score(
        self,
        score: int,
    ) -> None:

        self._score = max(
            0,
            min(
                100,
                int(score),
            ),
        )

        self.update()

    def paintEvent(
        self,
        event,
    ) -> None:

        super().paintEvent(event)

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing,
            True,
        )

        rect = QRectF(
            12,
            46,
            self.width() - 24,
            12,
        )

        gradient = QLinearGradient(
            rect.left(),
            0,
            rect.right(),
            0,
        )

        gradient.setColorAt(
            0,
            QColor(RED),
        )

        gradient.setColorAt(
            0.45,
            QColor(ORANGE),
        )

        gradient.setColorAt(
            0.55,
            QColor(CYAN),
        )

        gradient.setColorAt(
            1,
            QColor(GREEN),
        )

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            gradient
        )

        painter.drawRoundedRect(
            rect,
            6,
            6,
        )

        position = (
            rect.left()
            + (
                self._score
                / 100
            )
            * rect.width()
        )

        painter.setBrush(
            QColor(TEXT_PRIMARY)
        )

        painter.drawEllipse(
            QPointF(
                position,
                rect.center().y(),
            ),
            7,
            7,
        )

        if self._score >= 70:

            bias = "BULLISH"
            color = GREEN

        elif self._score <= 30:

            bias = "BEARISH"
            color = RED

        else:

            bias = "NEUTRAL"
            color = ORANGE

        font = QFont(
            FONT_FAMILY,
            13,
        )

        font.setBold(True)

        painter.setFont(font)

        painter.setPen(
            QColor(color)
        )

        painter.drawText(
            QRectF(
                0,
                4,
                self.width(),
                28,
            ),
            Qt.AlignCenter,
            bias,
        )

        small_font = QFont(
            FONT_FAMILY,
            7,
        )

        small_font.setBold(True)

        painter.setFont(
            small_font
        )

        painter.setPen(
            QColor(TEXT_MUTED)
        )

        painter.drawText(
            QRectF(
                rect.left(),
                66,
                80,
                16,
            ),
            Qt.AlignLeft,
            "SELL BIAS",
        )

        painter.drawText(
            QRectF(
                rect.right() - 80,
                66,
                80,
                16,
            ),
            Qt.AlignRight,
            "BUY BIAS",
        )


# ==========================================================
# SCANNER HEADER
# ==========================================================

class IntradayScannerHeader(ScannerCard):

    scan_requested = Signal()

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setMinimumHeight(
            135
        )

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            18,
            14,
            18,
            14,
        )

        layout.setSpacing(
            20
        )

        # --------------------------------------------------
        # TITLE
        # --------------------------------------------------

        left = QVBoxLayout()

        left.setSpacing(4)

        title_row = QHBoxLayout()

        title = QLabel(
            "INTRADAY MOMENTUM SCANNER"
        )

        title.setStyleSheet(
            f"""
            color: {TEXT_PRIMARY};
            font-size: 16px;
            font-weight: 900;
            """
        )

        title_row.addWidget(
            title
        )

        live_badge = QLabel(
            "â— LIVE"
        )

        live_badge.setStyleSheet(
            f"""
            QLabel {{
                color: {GREEN};
                background:
                    rgba(46,214,161,0.07);
                border:
                    1px solid rgba(46,214,161,0.18);
                border-radius: 5px;
                padding: 3px 7px;
                font-size: 7px;
                font-weight: 900;
            }}
            """
        )

        title_row.addWidget(
            live_badge
        )

        title_row.addStretch(1)

        left.addLayout(
            title_row
        )

        subtitle = QLabel(
            "Institutional-style filtering for "
            "high-momentum NSE intraday opportunities"
        )

        subtitle.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 9px;
            """
        )

        left.addWidget(
            subtitle
        )

        rule = QLabel(
            "Market Cap > â‚¹1,000 Cr   â€¢   "
            "Price > â‚¹200   â€¢   "
            "ADX â‰¥ 20   â€¢   "
            "Gap â‰¤ 3%   â€¢   "
            "Volume confirmation"
        )

        rule.setStyleSheet(
            f"""
            color: {CYAN};
            font-size: 8px;
            font-weight: 700;
            """
        )

        left.addWidget(
            rule
        )

        left.addStretch(1)

        layout.addLayout(
            left,
            4,
        )

        # --------------------------------------------------
        # MARKET BIAS
        # --------------------------------------------------

        bias_box = QVBoxLayout()

        bias_title = QLabel(
            "TODAY'S MARKET BIAS"
        )

        bias_title.setAlignment(
            Qt.AlignCenter
        )

        bias_title.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 7px;
            font-weight: 900;
            """
        )

        bias_box.addWidget(
            bias_title
        )

        self.bias_meter = (
            MarketBiasMeter()
        )

        bias_box.addWidget(
            self.bias_meter
        )

        layout.addLayout(
            bias_box,
            2,
        )

        # --------------------------------------------------
        # SCAN BUTTON
        # --------------------------------------------------

        button_box = QVBoxLayout()

        button_box.addStretch(1)

        self.scan_button = QPushButton(
            "âš¡  RUN SCANNER"
        )

        self.scan_button.setCursor(
            Qt.PointingHandCursor
        )

        self.scan_button.setMinimumSize(
            145,
            42,
        )

        self.scan_button.setStyleSheet(
            f"""
            QPushButton {{
                color: #FFFFFF;
                background:
                    qlineargradient(
                        x1:0,
                        y1:0,
                        x2:1,
                        y2:0,
                        stop:0 {BLUE},
                        stop:1 {PURPLE}
                    );
                border: none;
                border-radius: 9px;
                padding: 8px 15px;
                font-size: 9px;
                font-weight: 900;
            }}

            QPushButton:hover {{
                border:
                    1px solid rgba(255,255,255,0.30);
            }}

            QPushButton:pressed {{
                padding-top: 10px;
            }}
            """
        )

        self.scan_button.clicked.connect(
            self.scan_requested.emit
        )

        button_box.addWidget(
            self.scan_button
        )

        self.last_scan_label = QLabel(
            "Last scan: --"
        )

        self.last_scan_label.setAlignment(
            Qt.AlignCenter
        )

        self.last_scan_label.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 7px;
            """
        )

        button_box.addWidget(
            self.last_scan_label
        )

        button_box.addStretch(1)

        layout.addLayout(
            button_box
        )

    def set_market_bias(
        self,
        score: int,
    ) -> None:

        self.bias_meter.set_score(
            score
        )

    def set_last_scan(
        self,
        text: str,
    ) -> None:

        self.last_scan_label.setText(
            f"Last scan: {text}"
        )


# ==========================================================
# SUMMARY METRIC CARD
# ==========================================================

class ScannerSummaryMetric(ScannerCard):

    def __init__(
        self,
        title: str,
        value: str,
        subtitle: str,
        accent: str,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setMinimumHeight(
            95
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            13,
            10,
            13,
            10,
        )

        layout.setSpacing(2)

        top = QHBoxLayout()

        title_label = QLabel(
            title
        )

        title_label.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 7px;
            font-weight: 900;
            """
        )

        top.addWidget(
            title_label
        )

        top.addStretch(1)

        dot = QLabel(
            "â—"
        )

        dot.setStyleSheet(
            f"""
            color: {accent};
            font-size: 8px;
            """
        )

        top.addWidget(
            dot
        )

        layout.addLayout(top)

        self.value_label = QLabel(
            value
        )

        self.value_label.setStyleSheet(
            f"""
            color: {TEXT_PRIMARY};
            font-size: 20px;
            font-weight: 900;
            """
        )

        layout.addWidget(
            self.value_label
        )

        self.subtitle_label = QLabel(
            subtitle
        )

        self.subtitle_label.setStyleSheet(
            f"""
            color: {accent};
            font-size: 8px;
            font-weight: 700;
            """
        )

        layout.addWidget(
            self.subtitle_label
        )

    def set_data(
        self,
        value: str,
        subtitle: str,
    ) -> None:

        self.value_label.setText(
            value
        )

        self.subtitle_label.setText(
            subtitle
        )


# ==========================================================
# FILTER CHIP
# ==========================================================

class FilterChip(QCheckBox):

    def __init__(
        self,
        text: str,
        checked: bool = True,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(
            text,
            parent,
        )

        self.setChecked(
            checked
        )

        self.setCursor(
            Qt.PointingHandCursor
        )

        self.setStyleSheet(
            f"""
            QCheckBox {{
                color: {TEXT_SECONDARY};
                spacing: 6px;
                font-size: 8px;
                font-weight: 700;
            }}

            QCheckBox::indicator {{
                width: 15px;
                height: 15px;
                border-radius: 4px;
                border: 1px solid {BORDER_LIGHT};
                background: {SURFACE_2};
            }}

            QCheckBox::indicator:hover {{
                border: 1px solid {BLUE};
            }}

            QCheckBox::indicator:checked {{
                background: {BLUE};
                border: 1px solid {BLUE};
            }}
            """
        )


# ==========================================================
# FILTER PANEL
# ==========================================================

class IntradayFilterPanel(ScannerCard):

    filters_changed = Signal(dict)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setMinimumHeight(
            145
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            15,
            12,
            15,
            12,
        )

        layout.setSpacing(
            9
        )

        # --------------------------------------------------
        # HEADER
        # --------------------------------------------------

        header = QHBoxLayout()

        header.addWidget(
            SectionTitle(
                "SCANNER FILTERS",
                "Quality controls applied before ranking",
            )
        )

        header.addStretch(1)

        self.reset_button = QPushButton(
            "Reset"
        )

        self.reset_button.setCursor(
            Qt.PointingHandCursor
        )

        self.reset_button.setStyleSheet(
            f"""
            QPushButton {{
                color: {TEXT_MUTED};
                background: transparent;
                border: none;
                font-size: 8px;
                font-weight: 800;
            }}

            QPushButton:hover {{
                color: {CYAN};
            }}
            """
        )

        self.reset_button.clicked.connect(
            self.reset_filters
        )

        header.addWidget(
            self.reset_button
        )

        layout.addLayout(
            header
        )

        # --------------------------------------------------
        # SELECTORS
        # --------------------------------------------------

        selectors = QHBoxLayout()

        selectors.setSpacing(
            10
        )

        self.timeframe_combo = (
            self._create_combo(
                [
                    "5 Min",
                    "15 Min",
                    "30 Min",
                    "45 Min",
                ]
            )
        )

        selectors.addWidget(
            self._selector_box(
                "TIMEFRAME",
                self.timeframe_combo,
            )
        )

        self.direction_combo = (
            self._create_combo(
                [
                    "Both",
                    "Buy",
                    "Sell",
                ]
            )
        )

        selectors.addWidget(
            self._selector_box(
                "DIRECTION",
                self.direction_combo,
            )
        )

        self.universe_combo = (
            self._create_combo(
                [
                    "NSE All",
                    "Nifty 500",
                    "F&O",
                    "Nifty 200",
                ]
            )
        )

        selectors.addWidget(
            self._selector_box(
                "UNIVERSE",
                self.universe_combo,
            )
        )

        self.score_combo = (
            self._create_combo(
                [
                    "70+",
                    "75+",
                    "80+",
                    "85+",
                    "90+",
                ]
            )
        )

        self.score_combo.setCurrentText(
            "80+"
        )

        selectors.addWidget(
            self._selector_box(
                "MIN SCORE",
                self.score_combo,
            )
        )

        selectors.addStretch(1)

        layout.addLayout(
            selectors
        )

        # --------------------------------------------------
        # QUALITY FILTERS
        # --------------------------------------------------

        chips = QHBoxLayout()

        chips.setSpacing(
            14
        )

        self.volume_filter = FilterChip(
            "Volume Confirmed",
            True,
        )

        self.vwap_filter = FilterChip(
            "VWAP Aligned",
            True,
        )

        self.adx_filter = FilterChip(
            "ADX â‰¥ 20",
            True,
        )

        self.gap_filter = FilterChip(
            "Exclude Gap > 3%",
            True,
        )

        self.orb_filter = FilterChip(
            "ORB Width â‰¤ 3%",
            True,
        )

        self.sector_filter = FilterChip(
            "Sector Aligned",
            True,
        )

        self.fno_filter = FilterChip(
            "F&O Only",
            False,
        )

        for chip in (
            self.volume_filter,
            self.vwap_filter,
            self.adx_filter,
            self.gap_filter,
            self.orb_filter,
            self.sector_filter,
            self.fno_filter,
        ):

            chips.addWidget(
                chip
            )

            chip.stateChanged.connect(
                self._emit_filters
            )

        chips.addStretch(1)

        layout.addLayout(
            chips
        )

        for combo in (
            self.timeframe_combo,
            self.direction_combo,
            self.universe_combo,
            self.score_combo,
        ):

            combo.currentTextChanged.connect(
                self._emit_filters
            )

    # ======================================================
    # COMBO
    # ======================================================

    def _create_combo(
        self,
        values: List[str],
    ) -> QComboBox:

        combo = QComboBox()

        combo.addItems(
            values
        )

        combo.setMinimumWidth(
            110
        )

        combo.setFixedHeight(
            31
        )

        combo.setCursor(
            Qt.PointingHandCursor
        )

        combo.setStyleSheet(
            f"""
            QComboBox {{
                color: {TEXT_PRIMARY};
                background: {SURFACE_2};
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 4px 9px;
                font-size: 8px;
                font-weight: 700;
            }}

            QComboBox:hover {{
                border: 1px solid {BLUE};
            }}

            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}

            QComboBox QAbstractItemView {{
                color: {TEXT_PRIMARY};
                background: {SURFACE};
                border: 1px solid {BORDER};
                selection-background-color:
                    rgba(76,141,255,0.20);
                outline: none;
            }}
            """
        )

        return combo

    def _selector_box(
        self,
        title: str,
        widget: QWidget,
    ) -> QWidget:

        container = QWidget()

        box = QVBoxLayout(
            container
        )

        box.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        box.setSpacing(3)

        label = QLabel(
            title
        )

        label.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 7px;
            font-weight: 800;
            """
        )

        box.addWidget(
            label
        )

        box.addWidget(
            widget
        )

        return container

    # ======================================================
    # FILTER DATA
    # ======================================================

    def get_filters(
        self,
    ) -> Dict:

        score_text = (
            self.score_combo.currentText()
        )

        minimum_score = int(
            score_text.replace(
                "+",
                "",
            )
        )

        return {
            "timeframe":
                self.timeframe_combo.currentText(),

            "direction":
                self.direction_combo.currentText(),

            "universe":
                self.universe_combo.currentText(),

            "minimum_score":
                minimum_score,

            "volume_confirmed":
                self.volume_filter.isChecked(),

            "vwap_aligned":
                self.vwap_filter.isChecked(),

            "adx_filter":
                self.adx_filter.isChecked(),

            "exclude_gap":
                self.gap_filter.isChecked(),

            "orb_width_filter":
                self.orb_filter.isChecked(),

            "sector_aligned":
                self.sector_filter.isChecked(),

            "fno_only":
                self.fno_filter.isChecked(),
        }

    def _emit_filters(
        self,
        *args,
    ) -> None:

        self.filters_changed.emit(
            self.get_filters()
        )

    def reset_filters(
        self,
    ) -> None:

        self.timeframe_combo.setCurrentText(
            "5 Min"
        )

        self.direction_combo.setCurrentText(
            "Both"
        )

        self.universe_combo.setCurrentText(
            "NSE All"
        )

        self.score_combo.setCurrentText(
            "80+"
        )

        self.volume_filter.setChecked(
            True
        )

        self.vwap_filter.setChecked(
            True
        )

        self.adx_filter.setChecked(
            True
        )

        self.gap_filter.setChecked(
            True
        )

        self.orb_filter.setChecked(
            True
        )

        self.sector_filter.setChecked(
            True
        )

        self.fno_filter.setChecked(
            False
        )

        self._emit_filters()


# ==========================================================
# SCORE CELL
# ==========================================================

class ScoreCell(QWidget):

    def __init__(
        self,
        score: int,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self._score = max(
            0,
            min(
                100,
                score,
            ),
        )

        self.setMinimumSize(
            80,
            34,
        )

    def paintEvent(
        self,
        event,
    ) -> None:

        super().paintEvent(event)

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing,
            True,
        )

        color = QColor(
            score_color(
                self._score
            )
        )

        # Score number

        font = QFont(
            FONT_FAMILY,
            9,
        )

        font.setBold(True)

        painter.setFont(
            font
        )

        painter.setPen(
            color
        )

        painter.drawText(
            QRectF(
                3,
                1,
                30,
                20,
            ),
            Qt.AlignCenter,
            str(self._score),
        )

        # Progress background

        bar_rect = QRectF(
            35,
            13,
            self.width() - 41,
            6,
        )

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            QColor("#1B2A40")
        )

        painter.drawRoundedRect(
            bar_rect,
            3,
            3,
        )

        fill_rect = QRectF(
            bar_rect.left(),
            bar_rect.top(),
            bar_rect.width()
            * self._score
            / 100,
            bar_rect.height(),
        )

        painter.setBrush(
            color
        )

        painter.drawRoundedRect(
            fill_rect,
            3,
            3,
        )


# ==========================================================
# SIGNAL CELL
# ==========================================================

class ScannerSignalBadge(QLabel):

    def __init__(
        self,
        signal: str,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setAlignment(
            Qt.AlignCenter
        )

        self.setMinimumWidth(
            62
        )

        self.setFixedHeight(
            25
        )

        self.set_signal(
            signal
        )

    def set_signal(
        self,
        signal: str,
    ) -> None:

        signal = (
            signal
            .strip()
            .upper()
        )

        if signal == "BUY":

            color = GREEN

        elif signal == "SELL":

            color = RED

        else:

            color = ORANGE

        self.setText(
            signal
        )

        self.setStyleSheet(
            f"""
            QLabel {{
                color: {color};
                background:
                    rgba(255,255,255,0.035);
                border: 1px solid {color};
                border-radius: 5px;
                padding: 3px 7px;
                font-size: 7px;
                font-weight: 900;
            }}
            """
        )


# ==========================================================
# TREND MINI VISUAL
# ==========================================================

class TrendMiniChart(QWidget):

    def __init__(
        self,
        values: Optional[List[float]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.values = (
            list(values)
            if values
            else []
        )

        self.setMinimumSize(
            80,
            32,
        )

    def set_values(
        self,
        values: List[float],
    ) -> None:

        self.values = list(values)

        self.update()

    def paintEvent(
        self,
        event,
    ) -> None:

        super().paintEvent(event)

        if len(self.values) < 2:

            return

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing,
            True,
        )

        rect = self.rect().adjusted(
            4,
            5,
            -4,
            -5,
        )

        minimum = min(
            self.values
        )

        maximum = max(
            self.values
        )

        spread = (
            maximum - minimum
        )

        if spread == 0:
            spread = 1

        step = (
            rect.width()
            / (
                len(self.values)
                - 1
            )
        )

        points = []

        for index, value in enumerate(
            self.values
        ):

            normalized = (
                value - minimum
            ) / spread

            x = (
                rect.left()
                + index * step
            )

            y = (
                rect.bottom()
                - normalized
                * rect.height()
            )

            points.append(
                QPointF(
                    x,
                    y,
                )
            )

        positive = (
            self.values[-1]
            >= self.values[0]
        )

        color = QColor(
            GREEN
            if positive
            else RED
        )

        path = QPainterPath()

        path.moveTo(
            points[0]
        )

        for point in points[1:]:

            path.lineTo(
                point
            )

        painter.setPen(
            QPen(
                color,
                1.6,
                Qt.SolidLine,
                Qt.RoundCap,
                Qt.RoundJoin,
            )
        )

        painter.drawPath(
            path
        )

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            color
        )

        painter.drawEllipse(
            points[-1],
            2.5,
            2.5,
        )
        # ==========================================================
# INTRADAY OPPORTUNITY TABLE
# ==========================================================

class IntradayOpportunityTable(ScannerCard):

    stock_requested = Signal(str)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setMinimumHeight(
            430
        )

        self._rows: List[Dict] = []

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            15,
            13,
            15,
            13,
        )

        layout.setSpacing(
            10
        )

        # --------------------------------------------------
        # HEADER
        # --------------------------------------------------

        header = QHBoxLayout()

        header.addWidget(
            SectionTitle(
                "RANKED OPPORTUNITIES",
                "Best intraday setups after all quality filters",
            )
        )

        header.addStretch(1)

        self.result_count = QLabel(
            "0 QUALIFIED"
        )

        self.result_count.setStyleSheet(
            f"""
            QLabel {{
                color: {CYAN};
                background:
                    rgba(53,208,255,0.06);
                border:
                    1px solid rgba(53,208,255,0.18);
                border-radius: 6px;
                padding: 5px 9px;
                font-size: 7px;
                font-weight: 900;
            }}
            """
        )

        header.addWidget(
            self.result_count
        )

        layout.addLayout(
            header
        )

        # --------------------------------------------------
        # TABLE
        # --------------------------------------------------

        self.table = QTableWidget()

        self.table.setColumnCount(
            15
        )

        self.table.setHorizontalHeaderLabels(
            [
                "RANK",
                "STOCK",
                "SCORE",
                "SIGNAL",
                "PATTERN",
                "TF",
                "PRICE",
                "CHANGE",
                "RVOL",
                "ADX",
                "VWAP",
                "EMA",
                "SECTOR",
                "RR",
                "MOMENTUM",
            ]
        )

        self.table.setAlternatingRowColors(
            False
        )

        self.table.setShowGrid(
            False
        )

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.table.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        self.table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.table.setFocusPolicy(
            Qt.NoFocus
        )

        self.table.setSortingEnabled(
            False
        )

        self.table.verticalHeader().setVisible(
            False
        )

        self.table.verticalHeader().setDefaultSectionSize(
            48
        )

        self.table.setStyleSheet(
            f"""
            QTableWidget {{
                color: {TEXT_SECONDARY};
                background: transparent;
                border: none;
                outline: none;
                font-size: 8px;
                selection-background-color:
                    rgba(76,141,255,0.08);
            }}

            QTableWidget::item {{
                border-bottom:
                    1px solid rgba(255,255,255,0.035);
                padding: 5px;
            }}

            QTableWidget::item:selected {{
                color: {TEXT_PRIMARY};
                background:
                    rgba(76,141,255,0.10);
            }}

            QHeaderView::section {{
                color: {TEXT_MUTED};
                background: {SURFACE_2};
                border: none;
                border-bottom: 1px solid {BORDER};
                padding: 7px 5px;
                font-size: 7px;
                font-weight: 900;
            }}

            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
            }}

            QScrollBar::handle:vertical {{
                background: #263A57;
                border-radius: 4px;
                min-height: 30px;
            }}

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            """
        )

        table_header = (
            self.table.horizontalHeader()
        )

        table_header.setSectionResizeMode(
            QHeaderView.Interactive
        )

        # Rank
        self.table.setColumnWidth(
            0,
            48,
        )

        # Stock
        self.table.setColumnWidth(
            1,
            100,
        )

        # Score
        self.table.setColumnWidth(
            2,
            95,
        )

        # Signal
        self.table.setColumnWidth(
            3,
            78,
        )

        # Pattern
        self.table.setColumnWidth(
            4,
            130,
        )

        # TF
        self.table.setColumnWidth(
            5,
            60,
        )

        # Price
        self.table.setColumnWidth(
            6,
            90,
        )

        # Change
        self.table.setColumnWidth(
            7,
            72,
        )

        # RVOL
        self.table.setColumnWidth(
            8,
            65,
        )

        # ADX
        self.table.setColumnWidth(
            9,
            60,
        )

        # VWAP
        self.table.setColumnWidth(
            10,
            70,
        )

        # EMA
        self.table.setColumnWidth(
            11,
            85,
        )

        # Sector
        self.table.setColumnWidth(
            12,
            105,
        )

        # RR
        self.table.setColumnWidth(
            13,
            70,
        )

        # Momentum
        table_header.setSectionResizeMode(
            14,
            QHeaderView.Stretch,
        )

        self.table.cellDoubleClicked.connect(
            self._handle_double_click
        )

        layout.addWidget(
            self.table
        )

    # ======================================================
    # TABLE DATA
    # ======================================================

    def set_opportunities(
        self,
        opportunities: List[Dict],
    ) -> None:

        # Rank primarily by score and then RVOL.

        ranked = sorted(
            opportunities,
            key=lambda item: (
                int(
                    item.get(
                        "score",
                        0,
                    )
                ),
                float(
                    item.get(
                        "rvol",
                        0,
                    )
                ),
            ),
            reverse=True,
        )

        self._rows = ranked

        self.table.setRowCount(
            len(ranked)
        )

        self.result_count.setText(
            f"{len(ranked)} QUALIFIED"
        )

        for row, data in enumerate(
            ranked
        ):

            self._populate_row(
                row,
                data,
            )

    # ======================================================
    # ROW
    # ======================================================

    def _populate_row(
        self,
        row: int,
        data: Dict,
    ) -> None:

        rank = row + 1

        symbol = str(
            data.get(
                "symbol",
                "--",
            )
        )

        score = int(
            data.get(
                "score",
                0,
            )
        )

        signal = str(
            data.get(
                "signal",
                "WATCH",
            )
        ).upper()

        pattern = str(
            data.get(
                "pattern",
                "--",
            )
        )

        timeframe = str(
            data.get(
                "timeframe",
                "--",
            )
        )

        price = float(
            data.get(
                "price",
                0.0,
            )
        )

        change = float(
            data.get(
                "change",
                0.0,
            )
        )

        rvol = float(
            data.get(
                "rvol",
                0.0,
            )
        )

        adx = float(
            data.get(
                "adx",
                0.0,
            )
        )

        vwap = str(
            data.get(
                "vwap",
                "--",
            )
        )

        ema = str(
            data.get(
                "ema",
                "--",
            )
        )

        sector = str(
            data.get(
                "sector",
                "--",
            )
        )

        rr = str(
            data.get(
                "rr",
                "--",
            )
        )

        history = data.get(
            "history",
            [],
        )

        # --------------------------------------------------
        # RANK
        # --------------------------------------------------

        rank_item = QTableWidgetItem(
            f"#{rank}"
        )

        rank_item.setTextAlignment(
            Qt.AlignCenter
        )

        if rank == 1:

            rank_color = GREEN

        elif rank <= 3:

            rank_color = CYAN

        else:

            rank_color = TEXT_MUTED

        rank_item.setForeground(
            QColor(
                rank_color
            )
        )

        font = rank_item.font()

        font.setBold(
            True
        )

        rank_item.setFont(
            font
        )

        self.table.setItem(
            row,
            0,
            rank_item,
        )

        # --------------------------------------------------
        # STOCK
        # --------------------------------------------------

        stock_item = QTableWidgetItem(
            symbol
        )

        stock_item.setTextAlignment(
            Qt.AlignVCenter
            | Qt.AlignLeft
        )

        stock_item.setForeground(
            QColor(
                TEXT_PRIMARY
            )
        )

        stock_font = stock_item.font()

        stock_font.setBold(
            True
        )

        stock_item.setFont(
            stock_font
        )

        self.table.setItem(
            row,
            1,
            stock_item,
        )

        # --------------------------------------------------
        # SCORE
        # --------------------------------------------------

        score_widget = ScoreCell(
            score
        )

        self.table.setCellWidget(
            row,
            2,
            score_widget,
        )

        # --------------------------------------------------
        # SIGNAL
        # --------------------------------------------------

        signal_container = QWidget()

        signal_layout = QHBoxLayout(
            signal_container
        )

        signal_layout.setContentsMargins(
            5,
            5,
            5,
            5,
        )

        signal_layout.addWidget(
            ScannerSignalBadge(
                signal
            )
        )

        self.table.setCellWidget(
            row,
            3,
            signal_container,
        )

        # --------------------------------------------------
        # PATTERN
        # --------------------------------------------------

        pattern_item = QTableWidgetItem(
            pattern
        )

        pattern_item.setForeground(
            QColor(
                TEXT_SECONDARY
            )
        )

        self.table.setItem(
            row,
            4,
            pattern_item,
        )

        # --------------------------------------------------
        # TIMEFRAME
        # --------------------------------------------------

        tf_item = QTableWidgetItem(
            timeframe
        )

        tf_item.setTextAlignment(
            Qt.AlignCenter
        )

        tf_item.setForeground(
            QColor(
                CYAN
            )
        )

        self.table.setItem(
            row,
            5,
            tf_item,
        )

        # --------------------------------------------------
        # PRICE
        # --------------------------------------------------

        price_item = QTableWidgetItem(
            f"â‚¹{price:,.2f}"
        )

        price_item.setTextAlignment(
            Qt.AlignRight
            | Qt.AlignVCenter
        )

        price_item.setForeground(
            QColor(
                TEXT_PRIMARY
            )
        )

        self.table.setItem(
            row,
            6,
            price_item,
        )

        # --------------------------------------------------
        # CHANGE
        # --------------------------------------------------

        change_item = QTableWidgetItem(
            percent_text(
                change
            )
        )

        change_item.setTextAlignment(
            Qt.AlignCenter
        )

        change_item.setForeground(
            QColor(
                movement_color(
                    change
                )
            )
        )

        self.table.setItem(
            row,
            7,
            change_item,
        )

        # --------------------------------------------------
        # RVOL
        # --------------------------------------------------

        rvol_item = QTableWidgetItem(
            f"{rvol:.2f}Ã—"
        )

        rvol_item.setTextAlignment(
            Qt.AlignCenter
        )

        rvol_item.setForeground(
            QColor(
                GREEN
                if rvol >= 1.5
                else ORANGE
            )
        )

        self.table.setItem(
            row,
            8,
            rvol_item,
        )

        # --------------------------------------------------
        # ADX
        # --------------------------------------------------

        adx_item = QTableWidgetItem(
            f"{adx:.1f}"
        )

        adx_item.setTextAlignment(
            Qt.AlignCenter
        )

        adx_item.setForeground(
            QColor(
                GREEN
                if adx >= 25
                else ORANGE
            )
        )

        self.table.setItem(
            row,
            9,
            adx_item,
        )

        # --------------------------------------------------
        # VWAP
        # --------------------------------------------------

        vwap_upper = (
            vwap.upper()
        )

        vwap_item = QTableWidgetItem(
            vwap_upper
        )

        vwap_item.setTextAlignment(
            Qt.AlignCenter
        )

        if signal == "BUY":

            vwap_good = (
                vwap_upper == "ABOVE"
            )

        elif signal == "SELL":

            vwap_good = (
                vwap_upper == "BELOW"
            )

        else:

            vwap_good = False

        vwap_item.setForeground(
            QColor(
                GREEN
                if vwap_good
                else ORANGE
            )
        )

        self.table.setItem(
            row,
            10,
            vwap_item,
        )

        # --------------------------------------------------
        # EMA
        # --------------------------------------------------

        ema_item = QTableWidgetItem(
            ema
        )

        ema_item.setTextAlignment(
            Qt.AlignCenter
        )

        ema_upper = ema.upper()

        if (
            "BULL" in ema_upper
            or "21>50" in ema_upper
        ):

            ema_color = GREEN

        elif (
            "BEAR" in ema_upper
            or "21<50" in ema_upper
        ):

            ema_color = RED

        else:

            ema_color = ORANGE

        ema_item.setForeground(
            QColor(
                ema_color
            )
        )

        self.table.setItem(
            row,
            11,
            ema_item,
        )

        # --------------------------------------------------
        # SECTOR
        # --------------------------------------------------

        sector_item = QTableWidgetItem(
            sector
        )

        sector_item.setForeground(
            QColor(
                PURPLE
            )
        )

        self.table.setItem(
            row,
            12,
            sector_item,
        )

        # --------------------------------------------------
        # RR
        # --------------------------------------------------

        rr_item = QTableWidgetItem(
            rr
        )

        rr_item.setTextAlignment(
            Qt.AlignCenter
        )

        rr_item.setForeground(
            QColor(
                GREEN
            )
        )

        rr_font = rr_item.font()

        rr_font.setBold(
            True
        )

        rr_item.setFont(
            rr_font
        )

        self.table.setItem(
            row,
            13,
            rr_item,
        )

        # --------------------------------------------------
        # MOMENTUM CHART
        # --------------------------------------------------

        chart = TrendMiniChart(
            history
        )

        self.table.setCellWidget(
            row,
            14,
            chart,
        )

    # ======================================================
    # DOUBLE CLICK
    # ======================================================

    def _handle_double_click(
        self,
        row: int,
        column: int,
    ) -> None:

        if (
            row < 0
            or row >= len(
                self._rows
            )
        ):

            return

        symbol = str(
            self._rows[
                row
            ].get(
                "symbol",
                "",
            )
        )

        if symbol:

            self.stock_requested.emit(
                symbol
            )


# ==========================================================
# REJECTION BAR
# ==========================================================

class RejectionBar(QWidget):

    def __init__(
        self,
        label: str,
        value: int,
        maximum: int,
        accent: str,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.label_text = label

        self.value = max(
            0,
            value,
        )

        self.maximum = max(
            1,
            maximum,
        )

        self.accent = accent

        self.setMinimumHeight(
            35
        )

    def set_value(
        self,
        value: int,
        maximum: int,
    ) -> None:

        self.value = max(
            0,
            value,
        )

        self.maximum = max(
            1,
            maximum,
        )

        self.update()

    def paintEvent(
        self,
        event,
    ) -> None:

        super().paintEvent(event)

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing,
            True,
        )

        # Label

        font = QFont(
            FONT_FAMILY,
            7,
        )

        font.setBold(
            True
        )

        painter.setFont(
            font
        )

        painter.setPen(
            QColor(
                TEXT_SECONDARY
            )
        )

        painter.drawText(
            QRectF(
                0,
                0,
                125,
                16,
            ),
            Qt.AlignLeft
            | Qt.AlignVCenter,
            self.label_text,
        )

        # Value

        painter.setPen(
            QColor(
                self.accent
            )
        )

        painter.drawText(
            QRectF(
                self.width() - 45,
                0,
                45,
                16,
            ),
            Qt.AlignRight
            | Qt.AlignVCenter,
            str(
                self.value
            ),
        )

        bar_rect = QRectF(
            0,
            22,
            self.width(),
            6,
        )

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            QColor(
                "#17263A"
            )
        )

        painter.drawRoundedRect(
            bar_rect,
            3,
            3,
        )

        ratio = min(
            self.value
            / self.maximum,
            1.0,
        )

        active_rect = QRectF(
            bar_rect.left(),
            bar_rect.top(),
            bar_rect.width()
            * ratio,
            bar_rect.height(),
        )

        painter.setBrush(
            QColor(
                self.accent
            )
        )

        painter.drawRoundedRect(
            active_rect,
            3,
            3,
        )


# ==========================================================
# SCAN QUALITY CARD
# ==========================================================

class ScanQualityCard(ScannerCard):

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setMinimumHeight(
            285
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            14,
            12,
            14,
            12,
        )

        layout.setSpacing(
            8
        )

        layout.addWidget(
            SectionTitle(
                "QUALITY FILTER",
                "Why stocks were rejected",
            )
        )

        self.gap_bar = RejectionBar(
            "Gap > 3%",
            0,
            1,
            RED,
        )

        self.volume_bar = RejectionBar(
            "Weak volume",
            0,
            1,
            ORANGE,
        )

        self.adx_bar = RejectionBar(
            "ADX < 20",
            0,
            1,
            ORANGE,
        )

        self.vwap_bar = RejectionBar(
            "VWAP mismatch",
            0,
            1,
            CYAN,
        )

        self.sector_bar = RejectionBar(
            "Sector mismatch",
            0,
            1,
            PURPLE,
        )

        self.rr_bar = RejectionBar(
            "Poor RR",
            0,
            1,
            RED,
        )

        for bar in (
            self.gap_bar,
            self.volume_bar,
            self.adx_bar,
            self.vwap_bar,
            self.sector_bar,
            self.rr_bar,
        ):

            layout.addWidget(
                bar
            )

        layout.addStretch(1)

    def set_rejections(
        self,
        data: Dict,
    ) -> None:

        values = [
            int(
                data.get(
                    "gap",
                    0,
                )
            ),
            int(
                data.get(
                    "volume",
                    0,
                )
            ),
            int(
                data.get(
                    "adx",
                    0,
                )
            ),
            int(
                data.get(
                    "vwap",
                    0,
                )
            ),
            int(
                data.get(
                    "sector",
                    0,
                )
            ),
            int(
                data.get(
                    "rr",
                    0,
                )
            ),
        ]

        maximum = max(
            max(values),
            1,
        )

        self.gap_bar.set_value(
            values[0],
            maximum,
        )

        self.volume_bar.set_value(
            values[1],
            maximum,
        )

        self.adx_bar.set_value(
            values[2],
            maximum,
        )

        self.vwap_bar.set_value(
            values[3],
            maximum,
        )

        self.sector_bar.set_value(
            values[4],
            maximum,
        )

        self.rr_bar.set_value(
            values[5],
            maximum,
        )


# ==========================================================
# MARKET ALIGNMENT ROW
# ==========================================================

class AlignmentRow(QFrame):

    def __init__(
        self,
        title: str,
        value: str,
        status: bool,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setObjectName(
            "AlignmentRow"
        )

        self.setStyleSheet(
            f"""
            QFrame#AlignmentRow {{
                background:
                    rgba(255,255,255,0.018);
                border:
                    1px solid {BORDER};
                border-radius: 7px;
            }}
            """
        )

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            9,
            6,
            9,
            6,
        )

        title_label = QLabel(
            title
        )

        title_label.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 7px;
            font-weight: 800;
            """
        )

        layout.addWidget(
            title_label
        )

        layout.addStretch(1)

        self.value_label = QLabel()

        layout.addWidget(
            self.value_label
        )

        self.set_data(
            value,
            status,
        )

    def set_data(
        self,
        value: str,
        status: bool,
    ) -> None:

        color = (
            GREEN
            if status
            else RED
        )

        marker = (
            "âœ“"
            if status
            else "Ã—"
        )

        self.value_label.setText(
            f"{marker}  {value}"
        )

        self.value_label.setStyleSheet(
            f"""
            color: {color};
            font-size: 8px;
            font-weight: 800;
            """
        )


# ==========================================================
# MARKET ALIGNMENT CARD
# ==========================================================

class MarketAlignmentCard(ScannerCard):

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setMinimumHeight(
            285
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            14,
            12,
            14,
            12,
        )

        layout.setSpacing(
            7
        )

        layout.addWidget(
            SectionTitle(
                "MARKET ALIGNMENT",
                "Intraday environment confirmation",
            )
        )

        self.nifty_row = AlignmentRow(
            "NIFTY TREND",
            "--",
            False,
        )

        self.vwap_row = AlignmentRow(
            "INDEX VWAP",
            "--",
            False,
        )

        self.breadth_row = AlignmentRow(
            "MARKET BREADTH",
            "--",
            False,
        )

        self.sector_row = AlignmentRow(
            "SECTOR ROTATION",
            "--",
            False,
        )

        self.vix_row = AlignmentRow(
            "INDIA VIX",
            "--",
            False,
        )

        self.volume_row = AlignmentRow(
            "MARKET VOLUME",
            "--",
            False,
        )

        for row in (
            self.nifty_row,
            self.vwap_row,
            self.breadth_row,
            self.sector_row,
            self.vix_row,
            self.volume_row,
        ):

            layout.addWidget(
                row
            )

        layout.addStretch(1)

    def set_alignment(
        self,
        data: Dict,
    ) -> None:

        self.nifty_row.set_data(
            str(
                data.get(
                    "nifty",
                    "--",
                )
            ),
            bool(
                data.get(
                    "nifty_ok",
                    False,
                )
            ),
        )

        self.vwap_row.set_data(
            str(
                data.get(
                    "vwap",
                    "--",
                )
            ),
            bool(
                data.get(
                    "vwap_ok",
                    False,
                )
            ),
        )

        self.breadth_row.set_data(
            str(
                data.get(
                    "breadth",
                    "--",
                )
            ),
            bool(
                data.get(
                    "breadth_ok",
                    False,
                )
            ),
        )

        self.sector_row.set_data(
            str(
                data.get(
                    "sector",
                    "--",
                )
            ),
            bool(
                data.get(
                    "sector_ok",
                    False,
                )
            ),
        )

        self.vix_row.set_data(
            str(
                data.get(
                    "vix",
                    "--",
                )
            ),
            bool(
                data.get(
                    "vix_ok",
                    False,
                )
            ),
        )

        self.volume_row.set_data(
            str(
                data.get(
                    "volume",
                    "--",
                )
            ),
            bool(
                data.get(
                    "volume_ok",
                    False,
                )
            ),
        )


# ==========================================================
# SCANNER STATUS CARD
# ==========================================================

class ScannerStatusCard(ScannerCard):

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setMinimumHeight(
            285
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            14,
            12,
            14,
            12,
        )

        layout.setSpacing(
            9
        )

        layout.addWidget(
            SectionTitle(
                "SCANNER ENGINE",
                "Current scan diagnostics",
            )
        )

        self.status_label = QLabel(
            "READY"
        )

        self.status_label.setAlignment(
            Qt.AlignCenter
        )

        self.status_label.setStyleSheet(
            f"""
            QLabel {{
                color: {GREEN};
                background:
                    rgba(46,214,161,0.06);
                border:
                    1px solid rgba(46,214,161,0.18);
                border-radius: 8px;
                padding: 8px;
                font-size: 10px;
                font-weight: 900;
            }}
            """
        )

        layout.addWidget(
            self.status_label
        )

        self.universe_value = (
            self._metric(
                layout,
                "STOCKS SCANNED",
            )
        )

        self.filtered_value = (
            self._metric(
                layout,
                "PASSED FILTERS",
            )
        )

        self.buy_value = (
            self._metric(
                layout,
                "BUY SETUPS",
            )
        )

        self.sell_value = (
            self._metric(
                layout,
                "SELL SETUPS",
            )
        )

        self.best_value = (
            self._metric(
                layout,
                "BEST SCORE",
            )
        )

        self.runtime_value = (
            self._metric(
                layout,
                "SCAN TIME",
            )
        )

        layout.addStretch(1)

    def _metric(
        self,
        layout: QVBoxLayout,
        title: str,
    ) -> QLabel:

        row = QHBoxLayout()

        label = QLabel(
            title
        )

        label.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 7px;
            font-weight: 800;
            """
        )

        row.addWidget(
            label
        )

        row.addStretch(1)

        value = QLabel(
            "--"
        )

        value.setStyleSheet(
            f"""
            color: {TEXT_PRIMARY};
            font-size: 9px;
            font-weight: 900;
            """
        )

        row.addWidget(
            value
        )

        layout.addLayout(
            row
        )

        return value

    def set_status(
        self,
        data: Dict,
    ) -> None:

        status = str(
            data.get(
                "status",
                "READY",
            )
        ).upper()

        if status == "SCANNING":

            color = CYAN

        elif status == "READY":

            color = GREEN

        elif status == "ERROR":

            color = RED

        else:

            color = ORANGE

        self.status_label.setText(
            status
        )

        self.status_label.setStyleSheet(
            f"""
            QLabel {{
                color: {color};
                background:
                    rgba(255,255,255,0.025);
                border: 1px solid {color};
                border-radius: 8px;
                padding: 8px;
                font-size: 10px;
                font-weight: 900;
            }}
            """
        )

        self.universe_value.setText(
            f"{int(data.get('scanned', 0)):,}"
        )

        self.filtered_value.setText(
            str(
                int(
                    data.get(
                        "passed",
                        0,
                    )
                )
            )
        )

        self.buy_value.setText(
            str(
                int(
                    data.get(
                        "buys",
                        0,
                    )
                )
            )
        )

        self.sell_value.setText(
            str(
                int(
                    data.get(
                        "sells",
                        0,
                    )
                )
            )
        )

        self.best_value.setText(
            str(
                int(
                    data.get(
                        "best_score",
                        0,
                    )
                )
            )
        )

        self.runtime_value.setText(
            str(
                data.get(
                    "runtime",
                    "--",
                )
            )
        )


# ==========================================================
# INTRADAY SCANNER PAGE
# ==========================================================

class IntradayScannerPage(QWidget):

    stock_requested = Signal(str)

    scan_requested = Signal(dict)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.logger = logger

        self._current_filters: Dict = {}

        self.setObjectName(
            "IntradayScannerPage"
        )

        self.setStyleSheet(
            f"""
            QWidget#IntradayScannerPage {{
                background: {BACKGROUND};
            }}
            """
        )

        self._build_ui()

        self._connect_signals()

        self._load_demo_data()

    # ======================================================
    # BUILD UI
    # ======================================================

    def _build_ui(
        self,
    ) -> None:

        root = QVBoxLayout(
            self
        )

        root.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        root.setSpacing(
            0
        )

        self.scroll_area = QScrollArea()

        self.scroll_area.setWidgetResizable(
            True
        )

        self.scroll_area.setFrameShape(
            QFrame.NoFrame
        )

        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.scroll_area.setStyleSheet(
            f"""
            QScrollArea {{
                background: {BACKGROUND};
                border: none;
            }}

            QScrollBar:vertical {{
                background: {BACKGROUND};
                width: 9px;
            }}

            QScrollBar::handle:vertical {{
                background: #263A57;
                border-radius: 4px;
                min-height: 35px;
            }}

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            """
        )

        content = QWidget()

        content.setStyleSheet(
            f"""
            background: {BACKGROUND};
            """
        )

        layout = QVBoxLayout(
            content
        )

        layout.setContentsMargins(
            20,
            18,
            20,
            24,
        )

        layout.setSpacing(
            12
        )

        # --------------------------------------------------
        # HEADER
        # --------------------------------------------------

        self.scanner_header = (
            IntradayScannerHeader()
        )

        layout.addWidget(
            self.scanner_header
        )

        # --------------------------------------------------
        # SUMMARY CARDS
        # --------------------------------------------------

        summary = QWidget()

        summary_layout = QGridLayout(
            summary
        )

        summary_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        summary_layout.setSpacing(
            10
        )

        self.qualified_metric = (
            ScannerSummaryMetric(
                "QUALIFIED",
                "0",
                "Opportunities",
                CYAN,
            )
        )

        self.buy_metric = (
            ScannerSummaryMetric(
                "BUY SETUPS",
                "0",
                "Long candidates",
                GREEN,
            )
        )

        self.sell_metric = (
            ScannerSummaryMetric(
                "SELL SETUPS",
                "0",
                "Short candidates",
                RED,
            )
        )

        self.best_score_metric = (
            ScannerSummaryMetric(
                "BEST SCORE",
                "0",
                "Setup quality",
                PURPLE,
            )
        )

        self.avg_rvol_metric = (
            ScannerSummaryMetric(
                "AVG RVOL",
                "0.00Ã—",
                "Participation",
                ORANGE,
            )
        )

        self.market_bias_metric = (
            ScannerSummaryMetric(
                "MARKET BIAS",
                "--",
                "NIFTY alignment",
                GREEN,
            )
        )

        summary_cards = (
            self.qualified_metric,
            self.buy_metric,
            self.sell_metric,
            self.best_score_metric,
            self.avg_rvol_metric,
            self.market_bias_metric,
        )

        for column, card in enumerate(
            summary_cards
        ):

            summary_layout.addWidget(
                card,
                0,
                column,
            )

            summary_layout.setColumnStretch(
                column,
                1,
            )

        layout.addWidget(
            summary
        )

        # --------------------------------------------------
        # FILTERS
        # --------------------------------------------------

        self.filter_panel = (
            IntradayFilterPanel()
        )

        layout.addWidget(
            self.filter_panel
        )

        # --------------------------------------------------
        # OPPORTUNITY TABLE
        # --------------------------------------------------

        self.opportunity_table = (
            IntradayOpportunityTable()
        )

        layout.addWidget(
            self.opportunity_table
        )

        # --------------------------------------------------
        # LOWER INTELLIGENCE
        # --------------------------------------------------

        intelligence = QWidget()

        intelligence_layout = QGridLayout(
            intelligence
        )

        intelligence_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        intelligence_layout.setHorizontalSpacing(
            12
        )

        intelligence_layout.setVerticalSpacing(
            12
        )

        self.market_alignment = (
            MarketAlignmentCard()
        )

        self.scan_quality = (
            ScanQualityCard()
        )

        self.scanner_status = (
            ScannerStatusCard()
        )

        intelligence_layout.addWidget(
            self.market_alignment,
            0,
            0,
        )

        intelligence_layout.addWidget(
            self.scan_quality,
            0,
            1,
        )

        intelligence_layout.addWidget(
            self.scanner_status,
            0,
            2,
        )

        intelligence_layout.setColumnStretch(
            0,
            1,
        )

        intelligence_layout.setColumnStretch(
            1,
            1,
        )

        intelligence_layout.setColumnStretch(
            2,
            1,
        )

        layout.addWidget(
            intelligence
        )

        layout.addStretch(1)

        self.scroll_area.setWidget(
            content
        )

        root.addWidget(
            self.scroll_area
        )

    # ======================================================
    # SIGNALS
    # ======================================================

    def _connect_signals(
        self,
    ) -> None:

        self.scanner_header.scan_requested.connect(
            self.run_scan
        )

        self.filter_panel.filters_changed.connect(
            self._handle_filters_changed
        )

        self.opportunity_table.stock_requested.connect(
            self.stock_requested.emit
        )

    # ======================================================
    # FILTER CHANGE
    # ======================================================

    def _handle_filters_changed(
        self,
        filters: Dict,
    ) -> None:

        self._current_filters = filters

    # ======================================================
    # RUN SCAN
    # ======================================================

    def run_scan(
        self,
    ) -> None:

        self._current_filters = (
            self.filter_panel.get_filters()
        )

        self.scanner_header.scan_button.setEnabled(
            False
        )

        self.scanner_header.scan_button.setText(
            "SCANNING..."
        )

        self.scanner_status.set_status(
            {
                "status": "SCANNING",
                "scanned": 0,
                "passed": 0,
                "buys": 0,
                "sells": 0,
                "best_score": 0,
                "runtime": "...",
            }
        )

        # Signal for the future scanner service.

        self.scan_requested.emit(
            self._current_filters
        )

        # Development mode only:
        # simulate a short scan cycle.

        QTimer.singleShot(
            700,
            self._finish_demo_scan,
        )

    def _finish_demo_scan(
        self,
    ) -> None:

        self.scanner_header.scan_button.setEnabled(
            True
        )

        self.scanner_header.scan_button.setText(
            "âš¡  RUN SCANNER"
        )

        from PySide6.QtCore import (
            QDateTime,
        )

        self.scanner_header.set_last_scan(
            QDateTime.currentDateTime().toString(
                "hh:mm:ss AP"
            )
        )

        self._load_demo_data()

    # ======================================================
    # EXTERNAL DATA API
    # ======================================================

    def set_scanner_results(
        self,
        opportunities: List[Dict],
        scanner_stats: Optional[Dict] = None,
        rejection_stats: Optional[Dict] = None,
        alignment: Optional[Dict] = None,
        market_bias_score: int = 50,
    ) -> None:
        """
        Public entry point for the real scanner service.

        The scanner engine can call this method after
        processing the NSE universe.
        """

        self.opportunity_table.set_opportunities(
            opportunities
        )

        qualified = len(
            opportunities
        )

        buys = sum(
            1
            for item in opportunities
            if str(
                item.get(
                    "signal",
                    "",
                )
            ).upper() == "BUY"
        )

        sells = sum(
            1
            for item in opportunities
            if str(
                item.get(
                    "signal",
                    "",
                )
            ).upper() == "SELL"
        )

        best_score = max(
            [
                int(
                    item.get(
                        "score",
                        0,
                    )
                )
                for item in opportunities
            ],
            default=0,
        )

        rvol_values = [
            float(
                item.get(
                    "rvol",
                    0.0,
                )
            )
            for item in opportunities
        ]

        avg_rvol = (
            sum(rvol_values)
            / len(rvol_values)
            if rvol_values
            else 0.0
        )

        self.qualified_metric.set_data(
            str(
                qualified
            ),
            "Opportunities",
        )

        self.buy_metric.set_data(
            str(
                buys
            ),
            "Long candidates",
        )

        self.sell_metric.set_data(
            str(
                sells
            ),
            "Short candidates",
        )

        self.best_score_metric.set_data(
            str(
                best_score
            ),
            (
                "Elite setup"
                if best_score >= 90
                else "Best available"
            ),
        )

        self.avg_rvol_metric.set_data(
            f"{avg_rvol:.2f}Ã—",
            "Participation",
        )

        if market_bias_score >= 70:

            bias_text = "BULLISH"
            bias_subtitle = "Prefer BUY"

        elif market_bias_score <= 30:

            bias_text = "BEARISH"
            bias_subtitle = "Prefer SELL"

        else:

            bias_text = "NEUTRAL"
            bias_subtitle = "Selective"

        self.market_bias_metric.set_data(
            bias_text,
            bias_subtitle,
        )

        self.scanner_header.set_market_bias(
            market_bias_score
        )

        if scanner_stats:

            self.scanner_status.set_status(
                scanner_stats
            )

        if rejection_stats:

            self.scan_quality.set_rejections(
                rejection_stats
            )

        if alignment:

            self.market_alignment.set_alignment(
                alignment
            )

    # ======================================================
    # REFRESH
    # ======================================================

    def refresh(
        self,
    ) -> None:

        self.logger.debug(
            "Intraday scanner refresh requested."
        )

    # ======================================================
    # DEMO DATA
    # ======================================================

    def _load_demo_data(
        self,
    ) -> None:

        opportunities = [
            {
                "symbol": "HAL",
                "score": 97,
                "signal": "BUY",
                "pattern": "VCP BREAKOUT",
                "timeframe": "15M",
                "price": 5318.40,
                "change": 4.82,
                "rvol": 2.42,
                "adx": 31.8,
                "vwap": "ABOVE",
                "ema": "21>50>200",
                "sector": "DEFENCE",
                "rr": "1:4.2",
                "history": [
                    5200,
                    5212,
                    5208,
                    5225,
                    5238,
                    5231,
                    5255,
                    5262,
                    5258,
                    5280,
                    5294,
                    5318,
                ],
            },
            {
                "symbol": "BEL",
                "score": 94,
                "signal": "BUY",
                "pattern": "BULL FLAG",
                "timeframe": "15M",
                "price": 412.75,
                "change": 3.74,
                "rvol": 2.18,
                "adx": 29.6,
                "vwap": "ABOVE",
                "ema": "BULLISH",
                "sector": "DEFENCE",
                "rr": "1:3.6",
                "history": [
                    399,
                    401,
                    400,
                    404,
                    405,
                    404,
                    407,
                    409,
                    408,
                    411,
                    410,
                    413,
                ],
            },
            {
                "symbol": "SBIN",
                "score": 91,
                "signal": "BUY",
                "pattern": "VWAP BREAKOUT",
                "timeframe": "5M",
                "price": 846.20,
                "change": 2.68,
                "rvol": 1.96,
                "adx": 27.4,
                "vwap": "ABOVE",
                "ema": "21>50",
                "sector": "PSU BANK",
                "rr": "1:3.1",
                "history": [
                    829,
                    831,
                    830,
                    834,
                    833,
                    836,
                    838,
                    837,
                    841,
                    840,
                    844,
                    846,
                ],
            },
            {
                "symbol": "RELIANCE",
                "score": 88,
                "signal": "BUY",
                "pattern": "ORB",
                "timeframe": "15M",
                "price": 1498.55,
                "change": 1.82,
                "rvol": 1.74,
                "adx": 25.8,
                "vwap": "ABOVE",
                "ema": "BULLISH",
                "sector": "ENERGY",
                "rr": "1:2.8",
                "history": [
                    1474,
                    1478,
                    1476,
                    1481,
                    1485,
                    1483,
                    1488,
                    1490,
                    1489,
                    1494,
                    1493,
                    1499,
                ],
            },
            {
                "symbol": "TATASTEEL",
                "score": 85,
                "signal": "BUY",
                "pattern": "BREAKOUT",
                "timeframe": "30M",
                "price": 167.45,
                "change": 1.18,
                "rvol": 1.68,
                "adx": 24.7,
                "vwap": "ABOVE",
                "ema": "BULLISH",
                "sector": "METAL",
                "rr": "1:2.6",
                "history": [
                    164,
                    164.5,
                    164.2,
                    165,
                    165.4,
                    165.1,
                    165.8,
                    166.1,
                    165.9,
                    166.6,
                    166.9,
                    167.45,
                ],
            },
            {
                "symbol": "HCLTECH",
                "score": 82,
                "signal": "SELL",
                "pattern": "VWAP REJECT",
                "timeframe": "15M",
                "price": 1634.80,
                "change": -0.81,
                "rvol": 1.61,
                "adx": 23.9,
                "vwap": "BELOW",
                "ema": "BEARISH",
                "sector": "IT",
                "rr": "1:2.5",
                "history": [
                    1654,
                    1652,
                    1653,
                    1649,
                    1650,
                    1646,
                    1647,
                    1642,
                    1644,
                    1639,
                    1637,
                    1635,
                ],
            },
        ]

        self.set_scanner_results(
            opportunities=opportunities,

            scanner_stats={
                "status": "READY",
                "scanned": 1847,
                "passed": 6,
                "buys": 5,
                "sells": 1,
                "best_score": 97,
                "runtime": "1.24 sec",
            },

            rejection_stats={
                "gap": 84,
                "volume": 617,
                "adx": 428,
                "vwap": 231,
                "sector": 174,
                "rr": 307,
            },

            alignment={
                "nifty": "BULLISH",
                "nifty_ok": True,

                "vwap": "ABOVE",
                "vwap_ok": True,

                "breadth": "34 / 14",
                "breadth_ok": True,

                "sector": "BROAD",
                "sector_ok": True,

                "vix": "12.42",
                "vix_ok": True,

                "volume": "STRONG",
                "volume_ok": True,
            },

            market_bias_score=82,
        )


# ==========================================================
# END OF FILE
# ==========================================================
