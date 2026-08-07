from pathlib import Path
from datetime import datetime
import shutil


ROOT = Path(__file__).resolve().parent

DASHBOARD = ROOT / "ui" / "pages" / "dashboard_page.py"
APP = ROOT / "ui" / "app.py"

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

dashboard_backup = (
    DASHBOARD.parent
    / f"dashboard_page.before_live_dashboard_{stamp}.py"
)

app_backup = (
    APP.parent
    / f"app.before_live_dashboard_{stamp}.py"
)

shutil.copy2(
    DASHBOARD,
    dashboard_backup,
)

shutil.copy2(
    APP,
    app_backup,
)


# ==========================================================
# DASHBOARD PAGE
# ==========================================================

text = DASHBOARD.read_text(
    encoding="utf-8"
)


# ----------------------------------------------------------
# 1. Replace TOP OPPORTUNITIES
# ----------------------------------------------------------

start = text.index(
    "    def _top_opportunities(self) -> DashboardCard:"
)

end = text.index(
    "    # =====================================================",
    start,
)

new_top = '''    def _top_opportunities(self) -> DashboardCard:
        """
        Live scanner Top Opportunities card.

        Rows are created once and updated from the existing
        ApplicationController scannerCompleted signal.
        """

        card = DashboardCard(
            "TOP OPPORTUNITIES"
        )

        header = QHBoxLayout()

        for text, stretch in (
            ("STOCK", 3),
            ("SIGNAL", 2),
            ("SCORE", 1),
            ("PRICE", 2),
        ):

            label = make_label(
                text,
                10,
                MUTED,
                True,
            )

            if text in (
                "SCORE",
                "PRICE",
            ):
                label.setAlignment(
                    Qt.AlignRight
                    | Qt.AlignVCenter
                )

            header.addWidget(
                label,
                stretch,
            )

        card.layout.addLayout(
            header
        )

        self.live_opportunity_rows = []

        for _ in range(5):

            row = self._table_row_frame()

            layout = QHBoxLayout(
                row
            )

            layout.setContentsMargins(
                10,
                5,
                10,
                5,
            )

            layout.setSpacing(8)

            symbol_label = self._table_cell(
                "--"
            )

            signal_label = self._table_cell(
                "--",
                MUTED,
            )

            score_label = self._table_cell(
                "--",
                BLUE,
            )

            price_label = self._table_cell(
                "--"
            )

            score_label.setAlignment(
                Qt.AlignRight
                | Qt.AlignVCenter
            )

            price_label.setAlignment(
                Qt.AlignRight
                | Qt.AlignVCenter
            )

            layout.addWidget(
                symbol_label,
                3,
            )

            layout.addWidget(
                signal_label,
                2,
            )

            layout.addWidget(
                score_label,
                1,
            )

            layout.addWidget(
                price_label,
                2,
            )

            card.layout.addWidget(
                row
            )

            self.live_opportunity_rows.append(
                {
                    "row": row,
                    "symbol": symbol_label,
                    "signal": signal_label,
                    "score": score_label,
                    "price": price_label,
                }
            )

        card.layout.addStretch(1)

        return card


'''

text = (
    text[:start]
    + new_top
    + text[end:]
)


# ----------------------------------------------------------
# 2. Replace SCANNER SUMMARY
# ----------------------------------------------------------

start = text.index(
    "    def _scanner_summary(self) -> DashboardCard:"
)

end = text.index(
    "    def _top_movers(",
    start,
)

new_summary = '''    def _scanner_summary(self) -> DashboardCard:
        """
        Live scanner summary.

        Uses the same opportunities delivered to the
        Intraday Scanner page.
        """

        card = DashboardCard(
            "SCANNER SUMMARY"
        )

        self.live_scanner_donut = DonutChart(
            total=0,
            buy=0,
            sell=0,
        )

        self.live_scanner_donut.setMinimumHeight(
            92
        )

        self.live_scanner_donut.setMaximumHeight(
            105
        )

        card.layout.addWidget(
            self.live_scanner_donut,
            0,
            Qt.AlignHCenter,
        )

        stats = QHBoxLayout()
        stats.setSpacing(6)

        self.live_scanner_summary_labels = {}

        for title, color in (
            ("BUY", GREEN),
            ("SELL", RED),
            ("AVG", BLUE),
        ):

            box = QFrame()

            box.setFixedHeight(
                45
            )

            box.setStyleSheet(
                f"""
                QFrame {{
                    background: {ROW_BG};
                    border: 1px solid {BORDER_SOFT};
                    border-radius: 5px;
                }}
                """
            )

            box_layout = QVBoxLayout(
                box
            )

            box_layout.setContentsMargins(
                5,
                2,
                5,
                2,
            )

            box_layout.setSpacing(0)

            title_label = make_label(
                title,
                8,
                MUTED,
                True,
            )

            value_label = make_label(
                "0",
                13,
                color,
                True,
            )

            title_label.setAlignment(
                Qt.AlignCenter
            )

            value_label.setAlignment(
                Qt.AlignCenter
            )

            box_layout.addWidget(
                title_label
            )

            box_layout.addWidget(
                value_label
            )

            stats.addWidget(
                box,
                1,
            )

            self.live_scanner_summary_labels[
                title
            ] = value_label

        card.layout.addLayout(
            stats
        )

        button = QPushButton(
            "OPEN SCANNER"
        )

        button.setFixedHeight(
            30
        )

        button.setCursor(
            Qt.PointingHandCursor
        )

        button.setStyleSheet(
            f"""
            QPushButton {{
                background: {BLUE};
                border: none;
                border-radius: 5px;
                color: white;
                font-size: 11px;
                font-weight: 800;
            }}

            QPushButton:hover {{
                background: #4a89ff;
            }}
            """
        )

        button.clicked.connect(
            lambda:
            self.scanner_requested.emit(
                "scanner"
            )
        )

        card.layout.addWidget(
            button
        )

        return card


'''

text = (
    text[:start]
    + new_summary
    + text[end:]
)


# ----------------------------------------------------------
# 3. Replace LIVE SCANNER ALERTS
# ----------------------------------------------------------

start = text.index(
    "    def _live_scanner_alerts(self) -> DashboardCard:"
)

end = text.index(
    "    # =====================================================",
    start,
)

new_alerts = '''    def _live_scanner_alerts(self) -> DashboardCard:
        """
        Latest real scanner alerts.
        """

        card = DashboardCard(
            "LIVE SCANNER ALERTS"
        )

        header = QHBoxLayout()

        header.addWidget(
            make_label(
                "SYMBOL",
                10,
                MUTED,
                True,
            )
        )

        header.addStretch(1)

        header.addWidget(
            make_label(
                "TRIGGER",
                10,
                MUTED,
                True,
            )
        )

        card.layout.addLayout(
            header
        )

        self.live_scanner_alert_rows = []

        for _ in range(5):

            row = self._table_row_frame()

            layout = QHBoxLayout(
                row
            )

            layout.setContentsMargins(
                10,
                5,
                10,
                5,
            )

            layout.setSpacing(8)

            symbol_label = self._table_cell(
                "--"
            )

            trigger_label = self._table_cell(
                "--",
                MUTED,
            )

            trigger_label.setAlignment(
                Qt.AlignRight
                | Qt.AlignVCenter
            )

            layout.addWidget(
                symbol_label,
                1,
            )

            layout.addWidget(
                trigger_label,
                2,
            )

            card.layout.addWidget(
                row
            )

            self.live_scanner_alert_rows.append(
                {
                    "row": row,
                    "symbol": symbol_label,
                    "trigger": trigger_label,
                }
            )

        card.layout.addStretch(1)

        return card


'''

text = (
    text[:start]
    + new_alerts
    + text[end:]
)


# ----------------------------------------------------------
# 4. Add dashboard scanner update method
# ----------------------------------------------------------

marker = (
    "    def update_live_market_cards("
)

insert_at = text.index(
    marker
)

update_method = '''    def update_scanner_results(
        self,
        opportunities,
    ) -> None:
        """
        Update dashboard scanner widgets from the existing
        scannerCompleted result list.

        No scanner execution happens here.
        """

        if opportunities is None:
            opportunities = []

        try:
            opportunities = list(
                opportunities
            )
        except TypeError:
            opportunities = []

        # --------------------------------------------------
        # Helpers
        # --------------------------------------------------

        def safe_float(
            value,
            default=0.0,
        ):

            try:
                return float(value)

            except (
                TypeError,
                ValueError,
            ):
                return default

        def get_signal(item):

            return str(
                item.get(
                    "signal",
                    "",
                )
            ).upper()

        # --------------------------------------------------
        # Sort best opportunities first
        # --------------------------------------------------

        ranked = sorted(
            opportunities,
            key=lambda item: safe_float(
                item.get(
                    "score",
                    item.get(
                        "confidence",
                        0,
                    ),
                )
            ),
            reverse=True,
        )

        # --------------------------------------------------
        # TOP OPPORTUNITIES
        # --------------------------------------------------

        for index, row_data in enumerate(
            self.live_opportunity_rows
        ):

            if index < len(ranked):

                item = ranked[index]

                symbol = str(
                    item.get(
                        "symbol",
                        "--",
                    )
                )

                signal = get_signal(
                    item
                ) or "--"

                score_value = safe_float(
                    item.get(
                        "score",
                        item.get(
                            "confidence",
                            0,
                        ),
                    )
                )

                entry_value = safe_float(
                    item.get(
                        "entry",
                        item.get(
                            "price",
                            item.get(
                                "ltp",
                                0,
                            ),
                        ),
                    )
                )

                row_data[
                    "symbol"
                ].setText(
                    symbol
                )

                row_data[
                    "signal"
                ].setText(
                    signal
                )

                row_data[
                    "score"
                ].setText(
                    f"{score_value:.0f}"
                )

                if entry_value:

                    row_data[
                        "price"
                    ].setText(
                        f"₹{entry_value:,.2f}"
                    )

                else:

                    row_data[
                        "price"
                    ].setText(
                        "--"
                    )

                if signal == "BUY":

                    signal_color = GREEN

                elif signal == "SELL":

                    signal_color = RED

                else:

                    signal_color = MUTED

                row_data[
                    "signal"
                ].setStyleSheet(
                    f"""
                    color: {signal_color};
                    background: transparent;
                    border: none;
                    """
                )

                row_data[
                    "row"
                ].show()

            else:

                row_data[
                    "symbol"
                ].setText("--")

                row_data[
                    "signal"
                ].setText("--")

                row_data[
                    "score"
                ].setText("--")

                row_data[
                    "price"
                ].setText("--")

        # --------------------------------------------------
        # SCANNER SUMMARY
        # --------------------------------------------------

        buy_count = sum(
            1
            for item in opportunities
            if get_signal(item) == "BUY"
        )

        sell_count = sum(
            1
            for item in opportunities
            if get_signal(item) == "SELL"
        )

        scores = [
            safe_float(
                item.get(
                    "score",
                    item.get(
                        "confidence",
                        0,
                    ),
                )
            )
            for item in opportunities
        ]

        avg_score = (
            sum(scores)
            / len(scores)
            if scores
            else 0
        )

        self.live_scanner_summary_labels[
            "BUY"
        ].setText(
            str(buy_count)
        )

        self.live_scanner_summary_labels[
            "SELL"
        ].setText(
            str(sell_count)
        )

        self.live_scanner_summary_labels[
            "AVG"
        ].setText(
            f"{avg_score:.0f}"
        )

        self.live_scanner_donut.total = len(
            opportunities
        )

        self.live_scanner_donut.buy = (
            buy_count
        )

        self.live_scanner_donut.sell = (
            sell_count
        )

        self.live_scanner_donut.update()

        # --------------------------------------------------
        # LIVE SCANNER ALERTS
        # --------------------------------------------------

        for index, row_data in enumerate(
            self.live_scanner_alert_rows
        ):

            if index < len(ranked):

                item = ranked[index]

                symbol = str(
                    item.get(
                        "symbol",
                        "--",
                    )
                )

                signal = get_signal(
                    item
                )

                pattern = item.get(
                    "pattern"
                )

                trigger = ""

                if isinstance(
                    pattern,
                    dict,
                ):

                    trigger = str(
                        pattern.get(
                            "pattern",
                            pattern.get(
                                "name",
                                "",
                            ),
                        )
                    )

                elif pattern:

                    trigger = str(
                        pattern
                    )

                if not trigger:

                    confidence = safe_float(
                        item.get(
                            "confidence",
                            0,
                        )
                    )

                    if confidence >= 90:

                        trigger = (
                            "High Confidence"
                        )

                    elif signal == "BUY":

                        trigger = (
                            "BUY Opportunity"
                        )

                    elif signal == "SELL":

                        trigger = (
                            "SELL Opportunity"
                        )

                    else:

                        trigger = (
                            "Scanner Match"
                        )

                if signal == "BUY":

                    trigger_color = GREEN

                elif signal == "SELL":

                    trigger_color = RED

                else:

                    trigger_color = BLUE

                row_data[
                    "symbol"
                ].setText(
                    symbol
                )

                row_data[
                    "trigger"
                ].setText(
                    trigger
                )

                row_data[
                    "trigger"
                ].setStyleSheet(
                    f"""
                    color: {trigger_color};
                    background: transparent;
                    border: none;
                    """
                )

            else:

                row_data[
                    "symbol"
                ].setText("--")

                row_data[
                    "trigger"
                ].setText("--")


'''

text = (
    text[:insert_at]
    + update_method
    + text[insert_at:]
)


DASHBOARD.write_text(
    text,
    encoding="utf-8",
)


# ==========================================================
# APP.PY
# ==========================================================

app_text = APP.read_text(
    encoding="utf-8"
)


old = '''            self.intraday_page.set_scanner_results(
                opportunities
            )
'''

new = '''            self.intraday_page.set_scanner_results(
                opportunities
            )

            # Keep Dashboard scanner widgets synchronized
            # with the same real scannerCompleted payload.
            if hasattr(
                self,
                "dashboard_page",
            ):

                self.dashboard_page.update_scanner_results(
                    opportunities
                )
'''


if old not in app_text:

    raise RuntimeError(
        "Could not find intraday result update block "
        "inside ui/app.py"
    )


app_text = app_text.replace(
    old,
    new,
    1,
)


APP.write_text(
    app_text,
    encoding="utf-8",
)


print()
print("=" * 58)
print("LIVE DASHBOARD SCANNER CONNECTION COMPLETE")
print("=" * 58)
print(
    "Dashboard backup:",
    dashboard_backup,
)
print(
    "App backup      :",
    app_backup,
)
print()
print("Connected:")
print(
    "  scannerCompleted"
)
print(
    "       -> Intraday Scanner"
)
print(
    "       -> Dashboard Top Opportunities"
)
print(
    "       -> Dashboard Scanner Summary"
)
print(
    "       -> Dashboard Live Scanner Alerts"
)
print()
print(
    "Hard-coded scanner dashboard demo rows removed."
)
print("=" * 58)