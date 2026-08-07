from pathlib import Path
from datetime import datetime
import shutil
import re

path = Path("ui/pages/dashboard_page.py")
text = path.read_text(encoding="utf-8")

if len(text) < 10000:
    raise SystemExit(
        "SAFETY STOP: dashboard_page.py unexpectedly small."
    )

# Already imported correctly
if re.search(
    r"^\s*from\s+datetime\s+import\s+.*\bdatetime\b",
    text,
    re.MULTILINE,
):
    print("datetime is already imported.")
    raise SystemExit(0)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = path.with_name(
    f"dashboard_page.before_datetime_import_{stamp}.py"
)

shutil.copy2(path, backup)

# Put import near the beginning, after future import if present.
lines = text.splitlines()

insert_at = 0

for i, line in enumerate(lines[:100]):
    if line.startswith("from __future__ import"):
        insert_at = i + 1
        break
else:
    # Insert before first normal import
    for i, line in enumerate(lines[:100]):
        stripped = line.strip()
        if (
            stripped.startswith("import ")
            or stripped.startswith("from ")
        ):
            insert_at = i
            break

lines.insert(
    insert_at,
    "from datetime import datetime",
)

text = "\n".join(lines) + "\n"

path.write_text(
    text,
    encoding="utf-8",
)

print()
print("========================================")
print("DATETIME IMPORT FIX COMPLETE")
print("========================================")
print("File   :", path)
print("Added  : from datetime import datetime")
print("Backup :", backup)
print("========================================")
