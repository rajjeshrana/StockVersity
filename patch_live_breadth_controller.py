from pathlib import Path
from datetime import datetime
import shutil

FILE = Path("ui/market_controller.py")

text = FILE.read_text(encoding="utf-8")

if len(text) < 10000:
    raise SystemExit(
        "SAFETY STOP: market_controller.py unexpectedly small"
    )

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = FILE.with_name(
    f"market_controller.before_breadth_gauge_{stamp}.py"
)

shutil.copy2(FILE, backup)

needle = '''                    card.set_value(

                        str(value)

                    )
'''

replacement = '''                    card.set_value(

                        str(value)

                    )

        # -------------------------------------------------
        # LIVE BREADTH GAUGE
        # -------------------------------------------------

        gauge = getattr(
            self.dashboard,
            "breadth_gauge",
            None,
        )

        if gauge is not None:

            advance = self.breadth.get(
                "advance",
                0,
            )

            decline = self.breadth.get(
                "decline",
                0,
            )

            unchanged = self.breadth.get(
                "unchanged",
                0,
            )

            try:
                advance = float(advance or 0)
                decline = float(decline or 0)
                unchanged = float(unchanged or 0)

            except (TypeError, ValueError):
                advance = 0.0
                decline = 0.0
                unchanged = 0.0

            total = (
                advance
                + decline
                + unchanged
            )

            breadth_percent = (
                advance / total * 100.0
                if total > 0
                else 0.0
            )

            if hasattr(
                gauge,
                "set_value",
            ):
                gauge.set_value(
                    breadth_percent
                )
'''

if needle not in text:
    raise SystemExit(
        "SAFETY STOP: insertion point not found. "
        "market_controller.py NOT changed."
    )

text = text.replace(
    needle,
    replacement,
    1,
)

if len(text) < 10000:
    raise SystemExit(
        "SAFETY STOP: resulting controller unexpectedly small"
    )

FILE.write_text(
    text,
    encoding="utf-8",
)

print()
print("========================================")
print("LIVE BREADTH CONTROLLER PATCH COMPLETE")
print("========================================")
print("Advances       : LIVE")
print("Declines       : LIVE")
print("Unchanged      : LIVE")
print("Breadth Gauge  : LIVE")
print("Backup         :", backup)
print("========================================")
