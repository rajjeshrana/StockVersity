from pathlib import Path
from datetime import datetime
import shutil

path = Path("ui/pages/dashboard_page.py")

text = path.read_text(encoding="utf-8")

if len(text) < 30000:
    raise SystemExit(
        "SAFETY STOP: dashboard_page.py unexpectedly small"
    )

# ---------------------------------------------------------
# Backup
# ---------------------------------------------------------

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = path.with_name(
    f"dashboard_page.before_card2_fix_{stamp}.py"
)

shutil.copy2(
    path,
    backup,
)

# ---------------------------------------------------------
# Find unsupported CARD_2 references
# ---------------------------------------------------------

count = text.count("{CARD_2}")

if count == 0:
    print("No {CARD_2} reference found.")
    print("File unchanged.")
    raise SystemExit(0)

# Use the existing dashboard background constant instead.
#
# This preserves the dark neutral empty-tile appearance.
# BORDER is already used elsewhere in this file.
# ---------------------------------------------------------

text = text.replace(
    "background: {CARD_2};",
    "background: #0d2035;",
)

# ---------------------------------------------------------
# Safety verification
# ---------------------------------------------------------

remaining = text.count("{CARD_2}")

if remaining:
    raise SystemExit(
        f"SAFETY STOP: {remaining} CARD_2 reference(s) remain. "
        "File NOT written."
    )

path.write_text(
    text,
    encoding="utf-8",
)

print()
print("========================================")
print("DASHBOARD CARD COLOR FIX COMPLETE")
print("========================================")
print("CARD_2 references fixed :", count)
print("Live card patch          : PRESERVED")
print("Dashboard layout         : UNTOUCHED")
print("Market controller        : UNTOUCHED")
print("Upstox pipeline          : UNTOUCHED")
print("NIFTY 500 universe       : UNTOUCHED")
print("Backup                    :", backup)
print("========================================")
