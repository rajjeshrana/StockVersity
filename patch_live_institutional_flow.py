from pathlib import Path
from datetime import datetime
import shutil
import re

dash = Path("ui/pages/dashboard_page.py")
ctrl = Path("ui/market_controller.py")

if not dash.exists() or not ctrl.exists():
    raise SystemExit("SAFETY STOP: required files missing")

dash_text = dash.read_text(encoding="utf-8")
ctrl_text = ctrl.read_text(encoding="utf-8")

if len(dash_text) < 30000:
    raise SystemExit("SAFETY STOP: dashboard_page.py too small")

if len(ctrl_text) < 10000:
    raise SystemExit("SAFETY STOP: market_controller.py too small")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

dash_backup = dash.with_name(
    f"dashboard_page.before_live_institutional_{stamp}.py"
)

ctrl_backup = ctrl.with_name(
    f"market_controller.before_live_institutional_{stamp}.py"
)

shutil.copy2(dash, dash_backup)
shutil.copy2(ctrl, ctrl_backup)


# =========================================================
# 1. NORMALIZE INSTITUTIONAL DATA IN MARKET CONTROLLER
# =========================================================

merge_marker = '''        # -------------------------------------------------
        # BREADTH
        # -------------------------------------------------
'''

institutional_merge = '''        # -------------------------------------------------
        # INSTITUTIONAL FLOW
        #
        # AppController.market_snapshot() stores this under
        # market -> institutional. Copy it to the normalized
        # top-level dashboard snapshot.
        # -------------------------------------------------

        try:

            legacy_market = self.market_data.get(
                "market",
                {},
            )

            if isinstance(
                legacy_market,
                dict,
            ):

                institutional = legacy_market.get(
                    "institutional",
                    {},
                )

                if isinstance(
                    institutional,
                    dict,
                ):

                    self.market_data[
                        "institutional"
                    ] = institutional

        except Exception:
            pass

'''

if "legacy_market = self.market_data.get(" not in ctrl_text:

    if merge_marker not in ctrl_text:
        raise SystemExit(
            "SAFETY STOP: controller merge marker not found"
        )

    ctrl_text = ctrl_text.replace(
        merge_marker,
        institutional_merge + merge_marker,
        1,
    )


# =========================================================
# 2. ADD INSTITUTIONAL DATA TO DASHBOARD UPDATER CALL
# =========================================================

old_call = '''            losers=self.market_data.get(
                "losers",
                [],
            ),
        )'''

new_call = '''            losers=self.market_data.get(
                "losers",
                [],
            ),
            institutional=self.market_data.get(
                "institutional",
                {},
            ),
        )'''

if "institutional=self.market_data.get(" not in ctrl_text:

    if old_call not in ctrl_text:
        raise SystemExit(
            "SAFETY STOP: live dashboard updater call not found"
        )

    ctrl_text = ctrl_text.replace(
        old_call,
        new_call,
        1,
    )


# =========================================================
# 3. REPLACE INSTITUTIONAL FLOW CARD
# =========================================================

def replace_method(text, name, replacement):

    pattern = re.compile(
        rf"^    def {re.escape(name)}\(.*?"
        rf"(?=^    def |\Z)",
        re.MULTILINE | re.DOTALL,
    )

    matches = list(pattern.finditer(text))

    if len(matches) != 1:
        raise RuntimeError(
            f"{name}: expected 1 method, found {len(matches)}"
        )

    m = matches[0]

    return (
        text[:m.start()]
        + replacement.rstrip()
        + "\n\n"
        + text[m.end():]
    )


institutional_method = r'''
    def _institutional_flow(
        self,
    ) -> DashboardCard:

        card = DashboardCard(
            "INSTITUTIONAL FLOW"
        )

        # -------------------------------------------------
        # Session date
        # -------------------------------------------------

        self.institutional_date_label = make_label(
            "--",
            11,
            MUTED,
            True,
        )

        self.institutional_date_label.setAlignment(
            Qt.AlignRight
            | Qt.AlignVCenter
        )

        card.layout.addWidget(
            self.institutional_date_label
        )

        # -------------------------------------------------
        # FII
        # -------------------------------------------------

        fii_header = QHBoxLayout()

        fii_header.addWidget(
            make_label(
                "FII",
                13,
                TEXT,
                True,
            )
        )

        fii_header.addStretch(1)

        self.fii_net_label = make_label(
            "--",
            14,
            MUTED,
            True,
        )

        fii_header.addWidget(
            self.fii_net_label
        )

        card.layout.addLayout(
            fii_header
        )

        fii_values = QHBoxLayout()

        self.fii_buy_label = make_label(
            "BUY --",
            11,
            MUTED,
            True,
        )

        self.fii_sell_label = make_label(
            "SELL --",
            11,
            MUTED,
            True,
        )

        fii_values.addWidget(
            self.fii_buy_label
        )

        fii_values.addStretch(1)

        fii_values.addWidget(
            self.fii_sell_label
        )

        card.layout.addLayout(
            fii_values
        )

        # -------------------------------------------------
        # DII
        # -------------------------------------------------

        dii_header = QHBoxLayout()

        dii_header.addWidget(
            make_label(
                "DII",
                13,
                TEXT,
                True,
            )
        )

        dii_header.addStretch(1)

        self.dii_net_label = make_label(
            "--",
            14,
            MUTED,
            True,
        )

        dii_header.addWidget(
            self.dii_net_label
        )

        card.layout.addLayout(
            dii_header
        )

        dii_values = QHBoxLayout()

        self.dii_buy_label = make_label(
            "BUY --",
            11,
            MUTED,
            True,
        )

        self.dii_sell_label = make_label(
            "SELL --",
            11,
            MUTED,
            True,
        )

        dii_values.addWidget(
            self.dii_buy_label
        )

        dii_values.addStretch(1)

        dii_values.addWidget(
            self.dii_sell_label
        )

        card.layout.addLayout(
            dii_values
        )

        # -------------------------------------------------
        # Net institutional flow
        # -------------------------------------------------

        card.layout.addStretch(1)

        net_row = QHBoxLayout()

        net_row.addWidget(
            make_label(
                "NET INSTITUTIONAL FLOW",
                11,
                MUTED,
                True,
            )
        )

        net_row.addStretch(1)

        self.institutional_net_label = make_label(
            "--",
            15,
            MUTED,
            True,
        )

        net_row.addWidget(
            self.institutional_net_label
        )

        card.layout.addLayout(
            net_row
        )

        return card
'''

dash_text = replace_method(
    dash_text,
    "_institutional_flow",
    institutional_method,
)


# =========================================================
# 4. EXTEND EXISTING LIVE DASHBOARD UPDATE METHOD SIGNATURE
# =========================================================

old_signature = '''        gainers=None,
        losers=None,
    ) -> None:'''

new_signature = '''        gainers=None,
        losers=None,
        institutional=None,
    ) -> None:'''

if "institutional=None," not in dash_text:

    if old_signature not in dash_text:
        raise SystemExit(
            "SAFETY STOP: update_live_market_cards signature not found"
        )

    dash_text = dash_text.replace(
        old_signature,
        new_signature,
        1,
    )


old_defaults = '''        gainers = gainers or []
        losers = losers or []'''

new_defaults = '''        gainers = gainers or []
        losers = losers or []
        institutional = institutional or {}'''

if "institutional = institutional or {}" not in dash_text:

    if old_defaults not in dash_text:
        raise SystemExit(
            "SAFETY STOP: dashboard defaults not found"
        )

    dash_text = dash_text.replace(
        old_defaults,
        new_defaults,
        1,
    )


# =========================================================
# 5. ADD INSTITUTIONAL UI UPDATE TO LIVE METHOD
# =========================================================

institutional_update = r'''

        # -------------------------------------------------
        # Institutional Flow
        # -------------------------------------------------

        if isinstance(
            institutional,
            dict,
        ):

            fii = institutional.get(
                "fii",
                {},
            )

            dii = institutional.get(
                "dii",
                {},
            )

            if not isinstance(fii, dict):
                fii = {}

            if not isinstance(dii, dict):
                dii = {}

            def safe_number(value):

                try:
                    return float(value or 0.0)

                except (
                    TypeError,
                    ValueError,
                ):
                    return 0.0

            fii_buy = safe_number(
                fii.get("buy")
            )

            fii_sell = safe_number(
                fii.get("sell")
            )

            fii_net = safe_number(
                fii.get("net")
            )

            dii_buy = safe_number(
                dii.get("buy")
            )

            dii_sell = safe_number(
                dii.get("sell")
            )

            dii_net = safe_number(
                dii.get("net")
            )

            total_net = safe_number(
                institutional.get(
                    "net",
                    fii_net + dii_net,
                )
            )

            # ---------------------------------------------
            # Institutional session date
            # ---------------------------------------------

            raw_date = str(
                institutional.get(
                    "date",
                    "",
                )
                or ""
            ).strip()

            display_date = "--"

            if raw_date:

                parsed = None

                for fmt in (
                    "%Y-%m-%d",
                    "%d-%m-%Y",
                    "%d/%m/%Y",
                    "%d-%b-%Y",
                    "%d %b %Y",
                ):

                    try:

                        parsed = datetime.strptime(
                            raw_date,
                            fmt,
                        )

                        break

                    except ValueError:
                        pass

                if parsed is not None:

                    display_date = parsed.strftime(
                        "%d %b %Y"
                    )

                else:
                    display_date = raw_date

            if hasattr(
                self,
                "institutional_date_label",
            ):

                self.institutional_date_label.setText(
                    display_date
                )

            # ---------------------------------------------
            # Formatting
            # ---------------------------------------------

            def money(value):

                sign = (
                    "+"
                    if value > 0
                    else ""
                )

                return (
                    f"{sign}₹{value:,.0f} Cr"
                )

            def flow_color(value):

                if value > 0:
                    return GREEN

                if value < 0:
                    return RED

                return MUTED

            if hasattr(
                self,
                "fii_buy_label",
            ):

                self.fii_buy_label.setText(
                    f"BUY ₹{fii_buy:,.0f} Cr"
                )

            if hasattr(
                self,
                "fii_sell_label",
            ):

                self.fii_sell_label.setText(
                    f"SELL ₹{fii_sell:,.0f} Cr"
                )

            if hasattr(
                self,
                "fii_net_label",
            ):

                self.fii_net_label.setText(
                    money(fii_net)
                )

                self.fii_net_label.setStyleSheet(
                    f"""
                    color: {flow_color(fii_net)};
                    font-size: 14px;
                    font-weight: 800;
                    """
                )

            if hasattr(
                self,
                "dii_buy_label",
            ):

                self.dii_buy_label.setText(
                    f"BUY ₹{dii_buy:,.0f} Cr"
                )

            if hasattr(
                self,
                "dii_sell_label",
            ):

                self.dii_sell_label.setText(
                    f"SELL ₹{dii_sell:,.0f} Cr"
                )

            if hasattr(
                self,
                "dii_net_label",
            ):

                self.dii_net_label.setText(
                    money(dii_net)
                )

                self.dii_net_label.setStyleSheet(
                    f"""
                    color: {flow_color(dii_net)};
                    font-size: 14px;
                    font-weight: 800;
                    """
                )

            if hasattr(
                self,
                "institutional_net_label",
            ):

                self.institutional_net_label.setText(
                    money(total_net)
                )

                self.institutional_net_label.setStyleSheet(
                    f"""
                    color: {flow_color(total_net)};
                    font-size: 15px;
                    font-weight: 900;
                    """
                )
'''

if "# Institutional Flow\n" not in dash_text:

    # Add at end of update_live_market_cards(), immediately
    # before the next class method.
    pattern = re.compile(
        r"(    def update_live_market_cards\(.*?)(?=^    def )",
        re.MULTILINE | re.DOTALL,
    )

    match = pattern.search(
        dash_text
    )

    if not match:
        raise SystemExit(
            "SAFETY STOP: live dashboard update method not found"
        )

    updated_method = (
        match.group(1).rstrip()
        + institutional_update
        + "\n\n"
    )

    dash_text = (
        dash_text[:match.start()]
        + updated_method
        + dash_text[match.end():]
    )


# =========================================================
# SAFETY CHECKS
# =========================================================

required_dash = [
    "self.institutional_date_label",
    "self.fii_buy_label",
    "self.fii_sell_label",
    "self.fii_net_label",
    "self.dii_buy_label",
    "self.dii_sell_label",
    "self.dii_net_label",
    "self.institutional_net_label",
    "institutional=None,",
]

required_ctrl = [
    '"institutional"',
    "institutional=self.market_data.get(",
]

for item in required_dash:

    if item not in dash_text:
        raise SystemExit(
            f"SAFETY STOP dashboard: {item}"
        )

for item in required_ctrl:

    if item not in ctrl_text:
        raise SystemExit(
            f"SAFETY STOP controller: {item}"
        )


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
print("LIVE INSTITUTIONAL FLOW PATCH COMPLETE")
print("========================================")
print("FII Buy/Sell/Net    : LIVE NSE DATA")
print("DII Buy/Sell/Net    : LIVE NSE DATA")
print("Net Flow            : LIVE")
print("Session Date        : LIVE")
print("Date Format         : 03 Aug 2026")
print("Extra NSE request   : NO")
print("Breadth             : UNTOUCHED")
print("Sector Strength     : UNTOUCHED")
print("Heatmap             : UNTOUCHED")
print("Top Movers          : UNTOUCHED")
print("Layout              : UNTOUCHED")
print("Dashboard backup    :", dash_backup)
print("Controller backup   :", ctrl_backup)
print("========================================")
