from pathlib import Path
from datetime import datetime
import shutil

path = Path("backend/services/fii_dii_service.py")

if not path.exists():
    raise SystemExit(
        "SAFETY STOP: fii_dii_service.py not found"
    )

text = path.read_text(encoding="utf-8")

old = 'ENDPOINT = "/api/fiidiiTradeReact"'
new = 'ENDPOINT = "/fiidiiTradeReact"'

if old not in text:
    raise SystemExit(
        "SAFETY STOP: expected endpoint not found. "
        "File unchanged."
    )

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = path.with_name(
    f"fii_dii_service.before_endpoint_fix_{stamp}.py"
)

shutil.copy2(path, backup)

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
print("========================================")
print("FII/DII ENDPOINT FIX COMPLETE")
print("========================================")
print("Old : /api/fiidiiTradeReact")
print("New : /fiidiiTradeReact")
print("Final URL should be:")
print("https://www.nseindia.com/api/fiidiiTradeReact")
print("Backup:", backup)
print("========================================")
