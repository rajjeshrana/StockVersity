from pathlib import Path

path = Path(r"ui/app.py")

text = path.read_text(
    encoding="utf-8"
)

old = '''            self.live_stock_universe = (
                LiveStockUniverse(
                    self.nifty500_universe
                ).load()
            )

            self.upstox_provider.add_tick_callback('''

new = '''            self.live_stock_universe = (
                LiveStockUniverse(
                    self.nifty500_universe
                ).load()
            )

            # ---------------------------------------------
            # Give MarketController access to the same
            # live NIFTY 500 universe.
            # ---------------------------------------------

            self.market_controller.live_stock_universe = (
                self.live_stock_universe
            )

            self.upstox_provider.add_tick_callback('''

if old not in text:
    raise SystemExit(
        "Target block not found. app.py NOT changed."
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

print("MarketController -> LiveStockUniverse link added.")
