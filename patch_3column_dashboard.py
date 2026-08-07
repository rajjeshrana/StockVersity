from pathlib import Path
import re
import sys

FILE = Path("ui/pages/dashboard_page.py")

if not FILE.exists():
    print("ERROR: dashboard_page.py not found")
    sys.exit(1)

text = FILE.read_text(encoding="utf-8")


# =========================================================
# FIND _build_ui METHOD
# =========================================================

pattern = re.compile(
    r"^    def _build_ui\(self\) -> None:.*?"
    r"(?=^    def _simple_row\()",
    re.MULTILINE | re.DOTALL,
)

match = pattern.search(text)

if not match:
    raise RuntimeError(
        "Could not locate DashboardPage._build_ui()"
    )


# =========================================================
# NEW 3-COLUMN SCROLLABLE DASHBOARD
# =========================================================

new_method = '''    def _build_ui(self) -> None:
        """
        Build StockVersity professional dashboard.

        Layout:
            3 cards per row
            4 dashboard rows

        Scrolling:
            ONLY dashboard card area scrolls vertically.

        Fixed outside this widget:
            Main header
            Sidebar
            Bottom status bar

        Live-market card references are preserved.
        """

        # -------------------------------------------------
        # Local import
        #
        # Keeping QScrollArea local means we do not need
        # to modify the existing Qt import block.
        # -------------------------------------------------

        from PySide6.QtWidgets import QScrollArea

        # -------------------------------------------------
        # ROOT
        # -------------------------------------------------

        root = QVBoxLayout(self)

        root.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        root.setSpacing(0)

        # -------------------------------------------------
        # SCROLL AREA
        #
        # IMPORTANT:
        # Only DashboardPage content scrolls.
        # Header/sidebar/footer remain controlled by app.py
        # and therefore remain fixed.
        # -------------------------------------------------

        self.dashboard_scroll = QScrollArea()

        self.dashboard_scroll.setObjectName(
            "dashboardScroll"
        )

        self.dashboard_scroll.setWidgetResizable(
            True
        )

        self.dashboard_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.dashboard_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        self.dashboard_scroll.setFrameShape(
            QFrame.NoFrame
        )

        self.dashboard_scroll.setStyleSheet(
            f"""
            QScrollArea#dashboardScroll {{
                background: {BG};
                border: none;
            }}

            QScrollArea#dashboardScroll > QWidget > QWidget {{
                background: {BG};
            }}

            QScrollBar:vertical {{
                background: {BG};
                width: 10px;
                margin: 2px 2px 2px 2px;
            }}

            QScrollBar::handle:vertical {{
                background: #263b55;
                min-height: 45px;
                border-radius: 4px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: #345170;
            }}

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
            """
        )

        # -------------------------------------------------
        # SCROLL CONTENT
        # -------------------------------------------------

        content = QWidget()

        content.setObjectName(
            "dashboardContent"
        )

        content.setStyleSheet(
            f"""
            QWidget#dashboardContent {{
                background: {BG};
            }}
            """
        )

        # Four proper dashboard rows.
        #
        # This intentionally makes the content taller than
        # the normal viewport so row 4 can be reached with
        # one smooth vertical scroll.

        content.setMinimumHeight(
            1080
        )

        self.grid = QGridLayout(
            content
        )

        self.grid.setContentsMargins(
            14,
            12,
            14,
            14,
        )

        self.grid.setHorizontalSpacing(
            12
        )

        self.grid.setVerticalSpacing(
            12
        )

        # =================================================
        # CREATE ALL CARDS
        # =================================================

        self.market_pulse_card = (
            self._market_pulse()
        )

        self.sector_strength_card = (
            self._sector_strength()
        )

        self.market_breadth_card = (
            self._market_breadth()
        )

        self.market_heatmap_card = (
            self._market_heatmap()
        )

        self.top_opportunities_card = (
            self._top_opportunities()
        )

        self.scanner_summary_card = (
            self._scanner_summary()
        )

        self.top_movers_card = (
            self._top_movers()
        )

        self.live_alerts_card = (
            self._live_scanner_alerts()
        )

        self.institutional_flow_card = (
            self._institutional_flow()
        )

        self.derivatives_card = (
            self._derivatives_pulse()
        )

        self.nifty_oi_card = (
            self._nifty_oi_chart()
        )

        # =================================================
        # ROW 1
        #
        # MARKET PULSE
        # SECTOR STRENGTH
        # MARKET BREADTH
        # =================================================

        self.grid.addWidget(
            self.market_pulse_card,
            0,
            0,
        )

        self.grid.addWidget(
            self.sector_strength_card,
            0,
            1,
        )

        self.grid.addWidget(
            self.market_breadth_card,
            0,
            2,
        )

        # =================================================
        # ROW 2
        #
        # MARKET HEATMAP
        # TOP OPPORTUNITIES
        # SCANNER SUMMARY
        # =================================================

        self.grid.addWidget(
            self.market_heatmap_card,
            1,
            0,
        )

        self.grid.addWidget(
            self.top_opportunities_card,
            1,
            1,
        )

        self.grid.addWidget(
            self.scanner_summary_card,
            1,
            2,
        )

        # =================================================
        # ROW 3
        #
        # TOP MOVERS
        # LIVE ALERTS
        # INSTITUTIONAL FLOW
        # =================================================

        self.grid.addWidget(
            self.top_movers_card,
            2,
            0,
        )

        self.grid.addWidget(
            self.live_alerts_card,
            2,
            1,
        )

        self.grid.addWidget(
            self.institutional_flow_card,
            2,
            2,
        )

        # =================================================
        # ROW 4
        #
        # DERIVATIVES = 1 COLUMN
        # NIFTY OI    = 2 COLUMNS
        #
        # NIFTY OI intentionally receives double width.
        # =================================================

        self.grid.addWidget(
            self.derivatives_card,
            3,
            0,
        )

        self.grid.addWidget(
            self.nifty_oi_card,
            3,
            1,
            1,
            2,
        )

        # =================================================
        # THREE EQUAL COLUMNS
        # =================================================

        for column in range(3):

            self.grid.setColumnStretch(
                column,
                1,
            )

            self.grid.setColumnMinimumWidth(
                column,
                300,
            )

        # =================================================
        # FOUR COMFORTABLE ROWS
        #
        # Larger cards allow readable text, gauges,
        # graphics and tables without overlap.
        # =================================================

        for row in range(4):

            self.grid.setRowStretch(
                row,
                1,
            )

            self.grid.setRowMinimumHeight(
                row,
                250,
            )

        # -------------------------------------------------
        # INSTALL CONTENT INTO SCROLL AREA
        # -------------------------------------------------

        self.dashboard_scroll.setWidget(
            content
        )

        root.addWidget(
            self.dashboard_scroll,
            1,
        )


    # =====================================================
    # GENERIC ROW
    # =====================================================

'''

text = (
    text[:match.start()]
    + new_method
    + text[match.end():]
)

FILE.write_text(
    text,
    encoding="utf-8",
    newline="\n",
)

print()
print("========================================")
print("3-COLUMN DASHBOARD PATCH COMPLETE")
print("========================================")
print("Columns              : 3")
print("Rows                 : 4")
print("Vertical scrolling   : ENABLED")
print("Horizontal scrolling : DISABLED")
print("NIFTY OI width       : 2 columns")
print("Header               : UNTOUCHED")
print("Sidebar              : UNTOUCHED")
print("Bottom status bar    : UNTOUCHED")
print("Upstox pipeline      : UNTOUCHED")
print("NIFTY 500 engine     : UNTOUCHED")
print("========================================")