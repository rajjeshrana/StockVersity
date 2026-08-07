"""StockVersity Pro application shell with a modern dashboard layout."""

from __future__ import annotations

from typing import Dict, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ui.pages.dashboard_page import DashboardPage
from ui.pages.intraday_page import IntradayScannerPage


class MainWindow(QMainWindow):
    """Main window for StockVersity Scanner Pro."""

    PAGES = {
        "dashboard": "Dashboard",
        "scanner": "Scanner",
        "market": "Market",
        "watchlist": "Watchlist",
        "alerts": "Alerts",
        "portfolio": "Portfolio",
        "news": "News",
        "reports": "Reports",
        "settings": "Settings",
    }

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._pages: Dict[str, QWidget] = {}
        self._nav_buttons: Dict[str, QPushButton] = {}
        self.setWindowTitle("StockVersity Scanner Pro")
        self.setMinimumSize(1280, 760)
        self.resize(1600, 960)
        self._build_ui()
        self.show_page("dashboard")

    def _build_ui(self) -> None:
        self.setStyleSheet("""
            QMainWindow { background: #070d18; }
            QLabel { color: #e8edf7; font-family: 'Segoe UI'; }
            QScrollBar:vertical { background: #0b1322; width: 10px; }
            QScrollBar::handle:vertical { background: #24314b; border-radius: 5px; }
        """)
        root = QWidget(self)
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(self._create_sidebar())

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        right_layout.addWidget(self._create_header())

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("QStackedWidget { background: #080f1c; }")
        right_layout.addWidget(self.stack, 1)
        right_layout.addWidget(self._create_footer())
        root_layout.addWidget(right, 1)
        self.setCentralWidget(root)

        self._add_page("dashboard", DashboardPage())
        self._add_page("scanner", IntradayScannerPage())

    def _create_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setFixedWidth(196)
        sidebar.setStyleSheet("""
            QFrame { background: #08111f; border-right: 1px solid #1c2940; }
            QPushButton { color: #b9c3d5; background: transparent; border: 0; border-radius: 7px;
                          text-align: left; padding: 10px 14px; font-size: 15px; }
            QPushButton:hover { background: #13233e; color: white; }
            QPushButton[active='true'] { background: #172a50; color: #ffffff; font-weight: 600; }
        """)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(14, 18, 14, 16)
        layout.setSpacing(4)
        brand = QLabel("â—†  StockVersity")
        brand.setFont(QFont("Segoe UI", 18, QFont.Bold))
        brand.setStyleSheet("color: #f5f7fc; padding: 0 6px 18px 6px;")
        layout.addWidget(brand)
        subtitle = QLabel("SCANNER PRO")
        subtitle.setStyleSheet("color: #5e90ff; font-size: 10px; font-weight: 700; padding: 0 8px 18px 8px;")
        layout.addWidget(subtitle)
        for key, label in self.PAGES.items():
            button = QPushButton(label)
            button.setCursor(Qt.PointingHandCursor)
            button.clicked.connect(lambda checked=False, name=key: self.show_page(name))
            self._nav_buttons[key] = button
            layout.addWidget(button)
        layout.addStretch(1)
        market = QLabel("MARKET TIME\n\n09:28:15 AM\n\nNSE   â€¢ OPEN\nBSE   â€¢ OPEN")
        market.setStyleSheet("color: #98a7be; font-size: 12px; border-top: 1px solid #1c2940; padding: 16px 6px 0 6px;")
        layout.addWidget(market)
        return sidebar

    def _create_header(self) -> QFrame:
        header = QFrame()
        header.setFixedHeight(78)
        header.setStyleSheet("QFrame { background: #09111f; border-bottom: 1px solid #1c2940; }")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 10, 24, 10)
        search = QLabel("âŒ•   Search stocks, indices...     Ctrl + K")
        search.setStyleSheet("background: #111d31; border: 1px solid #22314a; border-radius: 8px; color: #aeb9cb; padding: 10px 14px; font-size: 14px;")
        search.setFixedWidth(300)
        layout.addWidget(search)
        for name, value, change in (("NIFTY 50", "25,488.90", "+243.60 (+0.97%)"), ("BANK NIFTY", "57,920.15", "+512.45 (+0.89%)"), ("SENSEX", "83,502.35", "+775.30 (+0.94%)"), ("INDIA VIX", "12.42", "-0.35 (-2.74%)")):
            block = QLabel(f"{name}\n{value}\n{change}")
            color = "#37db83" if change.startswith("+") else "#ff5d68"
            block.setStyleSheet(f"color: #dfe7f5; padding: 0 16px; font-size: 12px; font-weight: 600;")
            block.setProperty("change_color", color)
            layout.addWidget(block)
        layout.addStretch(1)
        open_label = QLabel("â— Market Open\n  09:28:15 AM")
        open_label.setStyleSheet("background: #0d1b28; border: 1px solid #203048; border-radius: 10px; color: #46e58b; padding: 8px 13px; font-size: 12px; font-weight: 600;")
        layout.addWidget(open_label)
        return header

    def _create_footer(self) -> QFrame:
        footer = QFrame()
        footer.setFixedHeight(34)
        footer.setStyleSheet("QFrame { background: #09111f; border-top: 1px solid #1c2940; }")
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(20, 0, 20, 0)
        label = QLabel("Data provided by NSE  â€¢  BSE     Powered by StockVersity Engine")
        label.setStyleSheet("color: #8b99b0; font-size: 11px;")
        layout.addWidget(label)
        layout.addStretch(1)
        live = QLabel("â—  All data is real-time     Connected")
        live.setStyleSheet("color: #45d881; font-size: 11px;")
        layout.addWidget(live)
        return footer

    def _add_page(self, key: str, page: QWidget) -> None:
        self._pages[key] = page
        self.stack.addWidget(page)

    def _placeholder(self, key: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        title = QLabel(self.PAGES[key])
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        detail = QLabel("This workspace is ready for its next module.")
        detail.setAlignment(Qt.AlignCenter)
        detail.setStyleSheet("color: #95a3b8; font-size: 15px;")
        layout.addWidget(title)
        layout.addWidget(detail)
        return page

    def show_page(self, key: str) -> None:
        if key not in self._pages:
            self._add_page(key, self._placeholder(key))
        self.stack.setCurrentWidget(self._pages[key])
        for name, button in self._nav_buttons.items():
            button.setProperty("active", name == key)
            button.style().unpolish(button)
            button.style().polish(button)

    def cleanup(self) -> None:
        """Hook called by main.py during shutdown."""

    def closeEvent(self, event: QCloseEvent) -> None:
        self.cleanup()
        event.accept()



