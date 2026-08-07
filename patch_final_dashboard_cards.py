from pathlib import Path
import re
import shutil
import sys

FILE = Path("ui/pages/dashboard_page.py")
BACKUP = Path("ui/pages/dashboard_page.before_final_card_fix.py")

if not FILE.exists():
    print("ERROR: dashboard_page.py not found")
    sys.exit(1)

text = FILE.read_text(encoding="utf-8")


def replace_method(source, method_name, new_method):
    pattern = re.compile(
        rf"^    def {re.escape(method_name)}\(.*?"
        rf"(?=^    def |\Z)",
        re.MULTILINE | re.DOTALL,
    )

    match = pattern.search(source)

    if not match:
        raise RuntimeError(
            f"Could not locate method: {method_name}"
        )

    return (
        source[:match.start()]
        + new_method.rstrip()
        + "\n\n"
        + source[match.end():]
    )


# =========================================================
# 1. BREADTH GAUGE
# Make geometry fit actual 100-115px widget height
# =========================================================

old = '''        width = min(
            self.width() - 36,
            165,
        )'''

new = '''        width = min(
            self.width() - 42,
            138,
        )'''

if old not in text:
    raise RuntimeError(
        "BreadthGauge width patch point not found"
    )

text = text.replace(old, new, 1)


old = '''        rect = QRectF(
            (self.width() - width) / 2,
            8,
            width,
            width,
        )'''

new = '''        rect = QRectF(
            (self.width() - width) / 2,
            5,
            width,
            width,
        )'''

if old not in text:
    raise RuntimeError(
        "BreadthGauge rect patch point not found"
    )

text = text.replace(old, new, 1)


old = '''        painter.setFont(
            QFont(
                "Segoe UI",
                22,
                QFont.Bold,
            )
        )'''

new = '''        painter.setFont(
            QFont(
                "Segoe UI",
                19,
                QFont.Bold,
            )
        )'''

if old not in text:
    raise RuntimeError(
        "BreadthGauge font patch point not found"
    )

text = text.replace(old, new, 1)


old = '''        text_rect = QRectF(
            rect.x(),
            rect.y() + 22,
            rect.width(),
            58,
        )'''

new = '''        text_rect = QRectF(
            rect.x(),
            rect.y() + 30,
            rect.width(),
            46,
        )'''

if old not in text:
    raise RuntimeError(
        "BreadthGauge text patch point not found"
    )

text = text.replace(old, new, 1)


# =========================================================
# 2. SCANNER SUMMARY
# Explicit donut region + stats + button
# =========================================================

scanner_method = '''    def _scanner_summary(self) -> DashboardCard:
        card = DashboardCard("SCANNER SUMMARY")

        donut = DonutChart(
            total=127,
            buy=74,
            sell=53,
        )

        donut.setMinimumHeight(92)
        donut.setMaximumHeight(105)

        card.layout.addWidget(
            donut,
            0,
            Qt.AlignHCenter,
        )

        stats = QHBoxLayout()
        stats.setSpacing(6)

        for title, value, color in (
            ("BUY", "74", GREEN),
            ("SELL", "53", RED),
            ("AVG", "81", BLUE),
        ):
            box = QFrame()

            box.setFixedHeight(45)

            box.setStyleSheet(
                f"""
                QFrame {{
                    background: {ROW_BG};
                    border: 1px solid {BORDER_SOFT};
                    border-radius: 5px;
                }}
                """
            )

            box_layout = QVBoxLayout(box)

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
                value,
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

        card.layout.addLayout(
            stats
        )

        button = QPushButton(
            "OPEN SCANNER"
        )

        button.setFixedHeight(30)

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

text = replace_method(
    text,
    "_scanner_summary",
    scanner_method,
)


# =========================================================
# 3. DERIVATIVES PULSE
# Gauge + status + compact 2x2 metrics
# =========================================================

derivatives_method = '''    def _derivatives_pulse(
        self,
    ) -> DashboardCard:

        card = DashboardCard(
            "DERIVATIVES PULSE"
        )

        gauge = DerivativesGauge(
            value=0.72,
            bullish=True,
        )

        gauge.setMinimumHeight(82)
        gauge.setMaximumHeight(92)

        card.layout.addWidget(
            gauge,
            0,
        )

        status = QLabel(
            "BULLISH"
        )

        status.setFixedHeight(22)

        status.setAlignment(
            Qt.AlignCenter
        )

        status.setStyleSheet(
            f"""
            QLabel {{
                color: {GREEN};
                background: transparent;
                border: none;
                font-size: 15px;
                font-weight: 900;
            }}
            """
        )

        card.layout.addWidget(
            status
        )

        stats = QGridLayout()

        stats.setHorizontalSpacing(8)
        stats.setVerticalSpacing(4)

        labels = [
            ("PCR", "1.18", GREEN),
            ("MAX PAIN", "25,500", BLUE),
            ("FUT OI", "+4.2%", GREEN),
            ("VIX", "12.42", GREEN),
        ]

        for i, (
            title,
            value,
            color,
        ) in enumerate(labels):

            box = QFrame()

            box.setFixedHeight(34)

            box.setStyleSheet(
                f"""
                QFrame {{
                    background: {ROW_BG};
                    border: 1px solid {BORDER_SOFT};
                    border-radius: 5px;
                }}
                """
            )

            layout = QVBoxLayout(
                box
            )

            layout.setContentsMargins(
                4,
                1,
                4,
                1,
            )

            layout.setSpacing(0)

            title_label = make_label(
                title,
                7,
                MUTED,
                True,
            )

            value_label = make_label(
                value,
                10,
                color,
                True,
            )

            title_label.setAlignment(
                Qt.AlignCenter
            )

            value_label.setAlignment(
                Qt.AlignCenter
            )

            layout.addWidget(
                title_label
            )

            layout.addWidget(
                value_label
            )

            stats.addWidget(
                box,
                i // 2,
                i % 2,
            )

        card.layout.addLayout(
            stats
        )

        return card
'''

text = replace_method(
    text,
    "_derivatives_pulse",
    derivatives_method,
)


# =========================================================
# 4. NIFTY OI CHART CLASS
# Remove 210px requirement
# =========================================================

old = '''        self.setMinimumHeight(
            210
        )'''

new = '''        self.setMinimumHeight(
            105
        )

        self.setMaximumHeight(
            135
        )'''

if old not in text:
    raise RuntimeError(
        "NiftyOIChart minimum height patch point not found"
    )

text = text.replace(old, new, 1)


# Reduce internal chart margins.
old = '''        area = self.rect().adjusted(
            35,
            18,
            -18,
            -28,
        )'''

new = '''        area = self.rect().adjusted(
            28,
            10,
            -14,
            -12,
        )'''

if old not in text:
    raise RuntimeError(
        "NiftyOIChart drawing-area patch point not found"
    )

text = text.replace(old, new, 1)


# =========================================================
# 5. NIFTY OI CARD
# Compact bottom information row
# =========================================================

old = '''            box_layout.setContentsMargins(
                7,
                4,
                7,
                4,
            )'''

new = '''            box.setFixedHeight(38)

            box_layout.setContentsMargins(
                5,
                2,
                5,
                2,
            )'''

if old not in text:
    raise RuntimeError(
        "NIFTY OI bottom-box patch point not found"
    )

text = text.replace(old, new, 1)


# =========================================================
# SAVE
# =========================================================

FILE.write_text(
    text,
    encoding="utf-8",
    newline="\n",
)

print()
print("========================================")
print("FINAL DASHBOARD CARD PATCH COMPLETE")
print("========================================")
print("Market Breadth       : FIXED")
print("Scanner Summary      : FIXED")
print("Derivatives Pulse    : FIXED")
print("NIFTY OI Chart       : FIXED")
print()
print("Live market files    : UNTOUCHED")
print("Upstox pipeline      : UNTOUCHED")
print("NIFTY 500 engine     : UNTOUCHED")
print("========================================")