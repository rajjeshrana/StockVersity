from pathlib import Path
from datetime import datetime
import shutil

path = Path("ui/app.py")

text = path.read_text(encoding="utf-8")

old = "            controller.run_scanner()"
new = "            controller.run_market_cycle()"

if old not in text:
    raise SystemExit(
        "SAFETY STOP: controller.run_scanner() not found. "
        "File unchanged."
    )

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = path.with_name(
    f"app.before_market_cycle_fix_{stamp}.py"
)

shutil.copy2(
    path,
    backup,
)

text = text.replace(
    old,
    new,
    1,
)

path.write_text(
    text,
    encoding="utf-8",
)

print()
print("=" * 52)
print("INTRADAY MARKET CYCLE CONNECTION FIXED")
print("=" * 52)
print("Old : controller.run_scanner()")
print("New : controller.run_market_cycle()")
print("Backup:", backup)
print("=" * 52)
