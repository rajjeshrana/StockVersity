from pathlib import Path

p = Path("ui/app.py")

# Preserve Unicode explicitly.
s = p.read_text(encoding="utf-8")

# ---------------------------------------------------------
# 1. IMPORT
# ---------------------------------------------------------

old = "from core.dependency_container import get_container"

new = """from core.dependency_container import get_container
from core.market_data.nifty500_universe import Nifty500Universe
from core.market_data.live_stock_universe import LiveStockUniverse"""

if old not in s:
    raise RuntimeError("Import insertion point not found")

s = s.replace(old, new, 1)


# ---------------------------------------------------------
# 2. CREATE NIFTY 500 LIVE ENGINE
# ---------------------------------------------------------

old = """            # ---------------------------------------------
            # Dashboard live index subscriptions
            # ---------------------------------------------"""

new = """            # ---------------------------------------------
            # NIFTY 500 live stock universe
            # ---------------------------------------------

            self.nifty500_universe = (
                Nifty500Universe()
            )

            self.live_stock_universe = (
                LiveStockUniverse(
                    self.nifty500_universe
                ).load()
            )

            self.upstox_provider.add_tick_callback(
                self.live_stock_universe.on_tick
            )

            nifty500_instruments = (
                self.live_stock_universe.instrument_keys()
            )

            print(
                "[LIVE MARKET] "
                f"NIFTY 500 universe ready: "
                f"{len(nifty500_instruments)} instruments."
            )

            self.upstox_provider.subscribe_many(
                nifty500_instruments,
                mode="ltpc",
            )

            # ---------------------------------------------
            # Dashboard live index subscriptions
            # ---------------------------------------------"""

if old not in s:
    raise RuntimeError(
        "NIFTY 500 insertion point not found"
    )

s = s.replace(old, new, 1)


# ---------------------------------------------------------
# SAVE AS UTF-8
# ---------------------------------------------------------

p.write_text(
    s,
    encoding="utf-8",
    newline="\n",
)

print("SAFE PATCH COMPLETE")
print(
    "Lines:",
    len(s.splitlines())
)
print(
    "LiveStockUniverse:",
    "LiveStockUniverse" in s
)
print(
    "instrument_keys:",
    "instrument_keys()" in s
)
