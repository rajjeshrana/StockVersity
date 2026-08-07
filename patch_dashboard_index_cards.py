from pathlib import Path
from datetime import datetime
import py_compile
import shutil


ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "ui" / "pages" / "dashboard_page.py"

if not TARGET.exists():
    raise FileNotFoundError(TARGET)

text = TARGET.read_text(encoding="utf-8")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = TARGET.with_name(
    f"{TARGET.stem}.before_live_index_card_fix_{stamp}.py"
)

shutil.copy2(TARGET, backup)


# ============================================================
# 1. ADD FINNIFTY TO THE ACTUAL CARD DICTIONARY
# ============================================================

old_cards = '''self.index_cards: Dict[str, IndexCard] = {
            "NIFTY": IndexCard("NIFTY 50"),
            "BANKNIFTY": IndexCard("BANK NIFTY"),
            "INDIAVIX": IndexCard("INDIA VIX"),
        }'''

new_cards = '''self.index_cards: Dict[str, IndexCard] = {
            "NIFTY": IndexCard("NIFTY 50"),
            "BANKNIFTY": IndexCard("BANK NIFTY"),
            "FINNIFTY": IndexCard("FIN NIFTY"),
            "INDIAVIX": IndexCard("INDIA VIX"),
        }'''

if old_cards in text:
    text = text.replace(old_cards, new_cards, 1)
    print("[PATCH] FINNIFTY added to index_cards.")
elif '"FINNIFTY": IndexCard(' in text:
    print("[PATCH] FINNIFTY already exists.")
else:
    raise RuntimeError(
        "Could not locate self.index_cards dictionary safely."
    )


# ============================================================
# 2. REMOVE OUTDATED COMMENT
# ============================================================

text = text.replace(
    "# FINNIFTY deliberately NOT included.",
    "# FINNIFTY included for live Upstox index display.",
)


TARGET.write_text(text, encoding="utf-8")


# ============================================================
# VALIDATE
# ============================================================

py_compile.compile(
    str(TARGET),
    doraise=True,
)

print("=" * 72)
print("STOCKVERSITY DASHBOARD INDEX CARD FIX INSTALLED")
print("=" * 72)
print(f"Target : {TARGET}")
print(f"Backup : {backup}")
print()
print("Dashboard index cards:")
print("  NIFTY       : ENABLED")
print("  BANKNIFTY   : ENABLED")
print("  FINNIFTY    : ENABLED")
print("  INDIA VIX   : ENABLED")
print()
print("IndexCard.update_data API : UNCHANGED")
print("MarketController           : UNCHANGED")
print("Upstox pipeline            : UNCHANGED")
print("Scanner pipeline           : UNCHANGED")
print()
print("Syntax validation: PASSED")
print("=" * 72)