from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import sys

ROOT = Path.cwd()
TARGET = ROOT / "backend" / "scanner" / "nse_data_engine.py"

if not TARGET.exists():
    print(f"ERROR: Target not found: {TARGET}")
    sys.exit(1)

text = TARGET.read_text(encoding="utf-8-sig")

old_gainers = '''        self.top_gainers = (

            pd.DataFrame(rows)

            .sort_values(

                "Change %",

                ascending=False,

            )

            .head(20)

        )
'''

new_gainers = '''        if not rows:

            self.top_gainers = pd.DataFrame(
                columns=[
                    "Symbol",
                    "Price",
                    "Change %",
                    "Volume",
                ]
            )

            return

        self.top_gainers = (

            pd.DataFrame(rows)

            .sort_values(

                "Change %",

                ascending=False,

            )

            .head(20)

        )
'''

old_losers = '''        self.top_losers = (

            pd.DataFrame(rows)

            .sort_values(

                "Change %",

                ascending=True,

            )

            .head(20)

        )
'''

new_losers = '''        if not rows:

            self.top_losers = pd.DataFrame(
                columns=[
                    "Symbol",
                    "Price",
                    "Change %",
                    "Volume",
                ]
            )

            return

        self.top_losers = (

            pd.DataFrame(rows)

            .sort_values(

                "Change %",

                ascending=True,

            )

            .head(20)

        )
'''

if old_gainers not in text:
    print("ERROR: update_top_gainers target block not found.")
    sys.exit(2)

if old_losers not in text:
    print("ERROR: update_top_losers target block not found.")
    sys.exit(3)

updated = text.replace(
    old_gainers,
    new_gainers,
    1,
)

updated = updated.replace(
    old_losers,
    new_losers,
    1,
)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = TARGET.with_name(
    f"nse_data_engine.before_empty_top_movers_fix_{stamp}.py"
)

shutil.copy2(TARGET, backup)

TARGET.write_text(
    updated,
    encoding="utf-8",
)

try:

    py_compile.compile(
        str(TARGET),
        doraise=True,
    )

except Exception as exc:

    shutil.copy2(
        backup,
        TARGET,
    )

    print("=" * 68)
    print("PATCH FAILED - ORIGINAL RESTORED")
    print("=" * 68)
    print(exc)
    sys.exit(4)

print("=" * 68)
print("STOCKVERSITY NSE TOP-MOVERS EMPTY-DATA FIX INSTALLED")
print("=" * 68)
print(f"Target : {TARGET}")
print(f"Backup : {backup}")
print()
print("Fixed:")
print("  update_top_gainers() safe when market_data is empty")
print("  update_top_losers() safe when market_data is empty")
print()
print("No synthetic market data added.")
print("No live WebSocket code changed.")
print("No dashboard code changed.")
print("Syntax validation: PASSED")
print("=" * 68)