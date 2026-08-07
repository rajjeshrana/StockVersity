from pathlib import Path

p = Path("ui/pages/dashboard_page.py")
s = p.read_text(encoding="utf-8")

changes = []

def replace_once(old, new, name):
    global s
    if old not in s:
        raise RuntimeError(f"PATCH POINT NOT FOUND: {name}")
    s = s.replace(old, new, 1)
    changes.append(name)


# =========================================================
# 1. DONUT CHART
# Reduce Scanner Summary donut footprint
# =========================================================

replace_once(
'''        self.setMinimumSize(
            150,
            150,
        )

        self.setMaximumHeight(
            175
        )''',
'''        self.setMinimumSize(
            115,
            115,
        )

        self.setMaximumHeight(
            125
        )''',
"DonutChart size"
)


# =========================================================
# 2. MARKET BREADTH GAUGE
# =========================================================

replace_once(
'''        self.setMinimumHeight(
            145
        )

        self.setMaximumHeight(
            175
        )''',
'''        self.setMinimumHeight(
            100
        )

        self.setMaximumHeight(
            115
        )''',
"BreadthGauge height"
)

replace_once(
'''        width = min(
            self.width() - 28,
            220,
        )''',
'''        width = min(
            self.width() - 36,
            165,
        )''',
"BreadthGauge width"
)

replace_once(
'''        rect = QRectF(
            (self.width() - width) / 2,
            22,
            width,
            width,
        )''',
'''        rect = QRectF(
            (self.width() - width) / 2,
            8,
            width,
            width,
        )''',
"BreadthGauge position"
)

replace_once(
'''        text_rect = QRectF(
            rect.x(),
            rect.y() + 35,
            rect.width(),
            80,
        )''',
'''        text_rect = QRectF(
            rect.x(),
            rect.y() + 22,
            rect.width(),
            58,
        )''',
"BreadthGauge text"
)


# =========================================================
# 3. PULSE TREND GRAPH
# =========================================================

replace_once(
'''        self.setMinimumHeight(
            120
        )''',
'''        self.setMinimumHeight(
            88
        )

        self.setMaximumHeight(
            105
        )''',
"PulseTrendGraph height"
)


# =========================================================
# 4. MARKET ANIMAL GRAPHIC
# =========================================================

replace_once(
'''        self.setMinimumSize(190, 132)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)''',
'''        self.setMinimumSize(145, 95)
        self.setMaximumHeight(110)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)''',
"MarketAnimalGraphic size"
)


# =========================================================
# 5. DERIVATIVES GAUGE
# =========================================================

replace_once(
'''        self.setMinimumHeight(
            175
        )''',
'''        self.setMinimumHeight(
            105
        )

        self.setMaximumHeight(
            120
        )''',
"DerivativesGauge height"
)

replace_once(
'''        size = min(
            self.width() - 20,
            180,
        )''',
'''        size = min(
            self.width() - 36,
            135,
        )''',
"DerivativesGauge size"
)

replace_once(
'''        rect = QRectF(
            (self.width() - size) / 2,
            25,
            size,
            size,
        )''',
'''        rect = QRectF(
            (self.width() - size) / 2,
            6,
            size,
            size,
        )''',
"DerivativesGauge position"
)


# =========================================================
# SAVE
# =========================================================

p.write_text(
    s,
    encoding="utf-8",
    newline="\n",
)

print("DASHBOARD OVERLAP PATCH COMPLETE")
print("Changes:", len(changes))

for item in changes:
    print(" OK:", item)
