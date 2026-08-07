from pathlib import Path
from datetime import datetime
import shutil
import re

dash = Path("ui/pages/dashboard_page.py")
ctrl = Path("ui/market_controller.py")

if not dash.exists() or not ctrl.exists():
    raise SystemExit("SAFETY STOP: required files not found")

dash_text = dash.read_text(encoding="utf-8")
ctrl_text = ctrl.read_text(encoding="utf-8")

if len(dash_text) < 30000:
    raise SystemExit(
        "SAFETY STOP: dashboard_page.py unexpectedly small"
    )

if len(ctrl_text) < 10000:
    raise SystemExit(
        "SAFETY STOP: market_controller.py unexpectedly small"
    )

# =========================================================
# BACKUPS
# =========================================================

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

dash_backup = dash.with_name(
    f"dashboard_page.before_live_3cards_{stamp}.py"
)

ctrl_backup = ctrl.with_name(
    f"market_controller.before_live_3cards_{stamp}.py"
)

shutil.copy2(dash, dash_backup)
shutil.copy2(ctrl, ctrl_backup)

# =========================================================
# REPLACE ONE CLASS METHOD SAFELY
# =========================================================

def replace_method(text, method_name, replacement):

    pattern = re.compile(
        rf"^    def {re.escape(method_name)}\("
        rf".*?"
        rf"(?=^    def |\Z)",
        re.MULTILINE | re.DOTALL,
    )

    matches = list(pattern.finditer(text))

    if len(matches) != 1:
        raise RuntimeError(
            f"{method_name}: expected 1 method, "
            f"found {len(matches)}"
        )

    return (
        text[:matches[0].start()]
        + replacement.rstrip()
        + "\n\n"
        + text[matches[0].end():]
    )


# =========================================================
# LIVE SECTOR STRENGTH CARD
# =========================================================

sector_method = r'''
    def _sector_strength(
        self,
    ) -> DashboardCard:

        card = DashboardCard(
            "SECTOR STRENGTH"
        )

        header = QHBoxLayout()

        header.addWidget(
            make_label(
                "SECTOR",
                10,
                MUTED,
                True,
            )
        )

        header.addStretch(1)

        header.addWidget(
            make_label(
                "STRENGTH",
                10,
                MUTED,
                True,
            )
        )

        header.addSpacing(8)

        header.addWidget(
            make_label(
                "CHANGE",
                10,
                MUTED,
                True,
            )
        )

        card.layout.addLayout(
            header
        )

        self.live_sector_rows = []

        for _ in range(5):

            row = QWidget()

            layout = QHBoxLayout(
                row
            )

            layout.setContentsMargins(
                0,
                4,
                0,
                4,
            )

            layout.setSpacing(7)

            sector_label = make_label(
                "--",
                12,
                TEXT,
                True,
            )

            sector_label.setFixedWidth(
                78
            )

            bar = StrengthBar(
                0,
                MUTED,
            )

            strength_label = make_label(
                "0",
                12,
                MUTED,
                True,
            )

            strength_label.setFixedWidth(
                28
            )

            change_label = make_label(
                "0.00%",
                12,
                MUTED,
                True,
            )

            change_label.setFixedWidth(
                58
            )

            change_label.setAlignment(
                Qt.AlignRight
                | Qt.AlignVCenter
            )

            layout.addWidget(
                sector_label
            )

            layout.addWidget(
                bar,
                1,
            )

            layout.addWidget(
                strength_label
            )

            layout.addWidget(
                change_label
            )

            card.layout.addWidget(
                row
            )

            self.live_sector_rows.append(
                {
                    "sector": sector_label,
                    "bar": bar,
                    "strength": strength_label,
                    "change": change_label,
                }
            )

        card.layout.addStretch(1)

        return card
'''

dash_text = replace_method(
    dash_text,
    "_sector_strength",
    sector_method,
)


# =========================================================
# LIVE MARKET HEATMAP
# =========================================================

heatmap_method = r'''
    def _market_heatmap(
        self,
    ) -> DashboardCard:

        card = DashboardCard(
            "MARKET HEATMAP"
        )

        card.layout.addStretch(1)

        grid = QGridLayout()

        grid.setHorizontalSpacing(5)
        grid.setVerticalSpacing(5)

        self.live_heatmap_tiles = []

        for i in range(9):

            tile = QLabel(
                "--\n0.00%"
            )

            tile.setAlignment(
                Qt.AlignCenter
            )

            tile.setMinimumHeight(
                48
            )

            tile.setStyleSheet(
                f"""
                QLabel {{
                    background: {CARD_2};
                    border: 1px solid {BORDER};
                    border-radius: 5px;
                    color: {MUTED};
                    font-size: 11px;
                    font-weight: 800;
                }}
                """
            )

            grid.addWidget(
                tile,
                i // 3,
                i % 3,
            )

            self.live_heatmap_tiles.append(
                tile
            )

        card.layout.addLayout(
            grid
        )

        card.layout.addStretch(1)

        return card
'''

dash_text = replace_method(
    dash_text,
    "_market_heatmap",
    heatmap_method,
)


# =========================================================
# LIVE TOP MOVERS
# =========================================================

movers_method = r'''
    def _top_movers(
        self,
    ) -> DashboardCard:

        card = DashboardCard(
            "TOP MOVERS"
        )

        self.live_mover_rows = []

        for _ in range(6):

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

            symbol_label = self._table_cell(
                "--"
            )

            price_label = self._table_cell(
                "--"
            )

            change_label = self._table_cell(
                "0.00%",
                MUTED,
            )

            price_label.setAlignment(
                Qt.AlignRight
                | Qt.AlignVCenter
            )

            change_label.setAlignment(
                Qt.AlignRight
                | Qt.AlignVCenter
            )

            layout.addWidget(
                symbol_label,
                2,
            )

            layout.addWidget(
                price_label,
                1,
            )

            layout.addWidget(
                change_label,
                1,
            )

            card.layout.addWidget(
                row
            )

            self.live_mover_rows.append(
                {
                    "symbol": symbol_label,
                    "price": price_label,
                    "change": change_label,
                }
            )

        card.layout.addStretch(1)

        return card
'''

dash_text = replace_method(
    dash_text,
    "_top_movers",
    movers_method,
)


# =========================================================
# DASHBOARD LIVE UPDATE METHOD
# =========================================================

live_update_method = r'''
    def update_live_market_cards(
        self,
        sectors=None,
        heatmap=None,
        gainers=None,
        losers=None,
    ) -> None:

        sectors = sectors or []
        heatmap = heatmap or []
        gainers = gainers or []
        losers = losers or []

        # -------------------------------------------------
        # Sector Strength
        # -------------------------------------------------

        sector_rows = getattr(
            self,
            "live_sector_rows",
            [],
        )

        for i, widgets in enumerate(
            sector_rows
        ):

            if i < len(sectors):

                data = sectors[i]

                name = str(
                    data.get(
                        "name",
                        data.get(
                            "industry",
                            "--",
                        ),
                    )
                )

                change = float(
                    data.get(
                        "change",
                        data.get(
                            "average_change_percent",
                            0.0,
                        ),
                    )
                    or 0.0
                )

                advance = int(
                    data.get(
                        "advance",
                        0,
                    )
                    or 0
                )

                decline = int(
                    data.get(
                        "decline",
                        0,
                    )
                    or 0
                )

                unchanged = int(
                    data.get(
                        "unchanged",
                        0,
                    )
                    or 0
                )

                total = (
                    advance
                    + decline
                    + unchanged
                )

                if total > 0:
                    strength = int(
                        round(
                            advance
                            / total
                            * 100.0
                        )
                    )
                else:
                    strength = 0

                strength = max(
                    0,
                    min(
                        100,
                        strength,
                    ),
                )

                color = (
                    GREEN
                    if change >= 0
                    else RED
                )

                widgets[
                    "sector"
                ].setText(
                    name[:12]
                )

                widgets[
                    "strength"
                ].setText(
                    str(strength)
                )

                widgets[
                    "change"
                ].setText(
                    f"{change:+.2f}%"
                )

                widgets[
                    "strength"
                ].setStyleSheet(
                    f"""
                    color: {color};
                    font-size: 12px;
                    font-weight: 700;
                    """
                )

                widgets[
                    "change"
                ].setStyleSheet(
                    f"""
                    color: {color};
                    font-size: 12px;
                    font-weight: 700;
                    """
                )

                bar = widgets["bar"]

                if hasattr(
                    bar,
                    "value",
                ):
                    bar.value = strength

                if hasattr(
                    bar,
                    "color",
                ):
                    bar.color = color

                bar.update()

            else:

                widgets[
                    "sector"
                ].setText("--")

                widgets[
                    "strength"
                ].setText("0")

                widgets[
                    "change"
                ].setText("0.00%")

        # -------------------------------------------------
        # Heatmap
        # -------------------------------------------------

        tiles = getattr(
            self,
            "live_heatmap_tiles",
            [],
        )

        for i, tile in enumerate(
            tiles
        ):

            if i < len(heatmap):

                data = heatmap[i]

                symbol = str(
                    data.get(
                        "symbol",
                        "--",
                    )
                )

                change = float(
                    data.get(
                        "change_percent",
                        data.get(
                            "change",
                            0.0,
                        ),
                    )
                    or 0.0
                )

                positive = (
                    change >= 0
                )

                bg = (
                    GREEN_DARK
                    if positive
                    else RED_DARK
                )

                border = (
                    GREEN
                    if positive
                    else RED
                )

                tile.setText(
                    f"{symbol}\n"
                    f"{change:+.2f}%"
                )

                tile.setStyleSheet(
                    f"""
                    QLabel {{
                        background: {bg};
                        border: 1px solid {border};
                        border-radius: 5px;
                        color: #ffffff;
                        font-size: 11px;
                        font-weight: 800;
                    }}
                    """
                )

            else:

                tile.setText(
                    "--\n0.00%"
                )

                tile.setStyleSheet(
                    f"""
                    QLabel {{
                        background: {CARD_2};
                        border: 1px solid {BORDER};
                        border-radius: 5px;
                        color: {MUTED};
                        font-size: 11px;
                        font-weight: 800;
                    }}
                    """
                )

        # -------------------------------------------------
        # Top Movers
        # 3 gainers + 3 losers
        # -------------------------------------------------

        movers = (
            list(gainers[:3])
            + list(losers[:3])
        )

        mover_rows = getattr(
            self,
            "live_mover_rows",
            [],
        )

        for i, widgets in enumerate(
            mover_rows
        ):

            if i < len(movers):

                data = movers[i]

                symbol = str(
                    data.get(
                        "symbol",
                        "--",
                    )
                )

                price = float(
                    data.get(
                        "ltp",
                        data.get(
                            "last_price",
                            0.0,
                        ),
                    )
                    or 0.0
                )

                change = float(
                    data.get(
                        "change_percent",
                        0.0,
                    )
                    or 0.0
                )

                color = (
                    GREEN
                    if change >= 0
                    else RED
                )

                widgets[
                    "symbol"
                ].setText(
                    symbol
                )

                widgets[
                    "price"
                ].setText(
                    f"₹{price:,.2f}"
                )

                widgets[
                    "change"
                ].setText(
                    f"{change:+.2f}%"
                )

                widgets[
                    "change"
                ].setStyleSheet(
                    f"""
                    color: {color};
                    font-size: 12px;
                    font-weight: 700;
                    """
                )

            else:

                widgets[
                    "symbol"
                ].setText("--")

                widgets[
                    "price"
                ].setText("--")

                widgets[
                    "change"
                ].setText("0.00%")
'''

# Insert immediately before _institutional_flow.
insert_marker = (
    "    def _institutional_flow("
)

if (
    "def update_live_market_cards(" 
    not in dash_text
):

    if insert_marker not in dash_text:
        raise RuntimeError(
            "Dashboard insertion marker not found"
        )

    dash_text = dash_text.replace(
        insert_marker,
        live_update_method.rstrip()
        + "\n\n"
        + insert_marker,
        1,
    )


# =========================================================
# CONTROLLER METHOD
# =========================================================

controller_method = r'''
    def update_live_dashboard_cards(
        self,
    ):

        dashboard = getattr(
            self,
            "dashboard",
            None,
        )

        if dashboard is None:
            return

        updater = getattr(
            dashboard,
            "update_live_market_cards",
            None,
        )

        if not callable(updater):
            return

        updater(
            sectors=self.market_data.get(
                "sectors",
                [],
            ),
            heatmap=self.market_data.get(
                "heatmap",
                [],
            ),
            gainers=self.market_data.get(
                "gainers",
                [],
            ),
            losers=self.market_data.get(
                "losers",
                [],
            ),
        )
'''

if (
    "def update_live_dashboard_cards("
    not in ctrl_text
):

    marker = (
        "    # =====================================================\n"
        "    # MARKET STATISTICS"
    )

    if marker not in ctrl_text:
        raise RuntimeError(
            "Controller method insertion marker not found"
        )

    ctrl_text = ctrl_text.replace(
        marker,
        controller_method.rstrip()
        + "\n\n"
        + marker,
        1,
    )


# =========================================================
# ADD REFRESH CALL
# =========================================================

call = (
    "        self.update_live_dashboard_cards()"
)

if call not in ctrl_text:

    target = (
        "        self.update_losers()"
    )

    if target not in ctrl_text:
        raise RuntimeError(
            "update_losers() refresh call not found"
        )

    ctrl_text = ctrl_text.replace(
        target,
        target
        + "\n\n"
        + call,
        1,
    )


# =========================================================
# SAFETY CHECKS
# =========================================================

required_dash = [
    "self.live_sector_rows",
    "self.live_heatmap_tiles",
    "self.live_mover_rows",
    "def update_live_market_cards(",
]

for item in required_dash:
    if item not in dash_text:
        raise RuntimeError(
            f"Dashboard safety check failed: {item}"
        )

required_ctrl = [
    "def update_live_dashboard_cards(",
    "self.update_live_dashboard_cards()",
]

for item in required_ctrl:
    if item not in ctrl_text:
        raise RuntimeError(
            f"Controller safety check failed: {item}"
        )


# =========================================================
# WRITE
# =========================================================

dash.write_text(
    dash_text,
    encoding="utf-8",
)

ctrl.write_text(
    ctrl_text,
    encoding="utf-8",
)

print()
print("========================================")
print("LIVE DASHBOARD 3-CARD PATCH COMPLETE")
print("========================================")
print("Sector Strength : LIVE")
print("Market Heatmap   : LIVE")
print("Top Movers       : LIVE")
print("Market Breadth   : UNTOUCHED")
print("3-column layout  : UNTOUCHED")
print("Scrolling        : UNTOUCHED")
print("Upstox pipeline  : UNTOUCHED")
print("NIFTY 500        : UNTOUCHED")
print("Dashboard backup :", dash_backup)
print("Controller backup:", ctrl_backup)
print("========================================")
