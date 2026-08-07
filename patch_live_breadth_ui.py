from pathlib import Path
from datetime import datetime
import shutil

FILE = Path("ui/pages/dashboard_page.py")

text = FILE.read_text(
    encoding="utf-8"
)

if len(text) < 30000:
    raise SystemExit(
        "SAFETY STOP: dashboard_page.py unexpectedly small"
    )

stamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

backup = FILE.with_name(
    f"dashboard_page.before_live_breadth_{stamp}.py"
)

shutil.copy2(
    FILE,
    backup,
)

old = '''        gauge = BreadthGauge(
            64
        )

        card.layout.addWidget(
            gauge,
            1,
        )
'''

new = '''        self.breadth_gauge = BreadthGauge(
            0
        )

        card.layout.addWidget(
            self.breadth_gauge,
            1,
        )
'''

if old not in text:
    raise SystemExit(
        "SAFETY STOP: breadth gauge block not found. "
        "Nothing written."
    )

text = text.replace(
    old,
    new,
    1,
)

if len(text) < 30000:
    raise SystemExit(
        "SAFETY STOP: resulting dashboard unexpectedly small"
    )

FILE.write_text(
    text,
    encoding="utf-8",
)

print("========================================")
print("LIVE BREADTH UI PATCH COMPLETE")
print("========================================")
print("breadth_gauge reference : ADDED")
print("Initial demo 64         : REMOVED")
print("Layout                  : UNTOUCHED")
print("========================================")