from pathlib import Path
from datetime import datetime
import shutil

path = Path("ui/market_controller.py")
text = path.read_text(encoding="utf-8")

# Safety
if len(text) < 10000:
    raise SystemExit(
        "SAFETY STOP: market_controller.py unexpectedly small"
    )

# Don't add twice
if "self.update_breadth_cards()" in text:
    print("Breadth UI refresh call already exists.")
    raise SystemExit(0)

target = "        self.update_market_breadth()"

if target not in text:
    raise SystemExit(
        "SAFETY STOP: update_market_breadth call not found. "
        "File unchanged."
    )

# Timestamped backup
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = path.with_name(
    f"market_controller.before_breadth_call_{stamp}.py"
)

shutil.copy2(path, backup)

replacement = (
    target
    + "\n\n"
    + "        self.update_breadth_cards()"
)

text = text.replace(
    target,
    replacement,
    1,
)

path.write_text(
    text,
    encoding="utf-8",
)

print("Breadth UI refresh call added.")
print("Backup:", backup)
