from pathlib import Path

path = Path("core/market_data/upstox_provider.py")

text = path.read_text(encoding="utf-8")

anchor = """# ==========================================================
# FACTORY
# ==========================================================
"""

if anchor not in text:
    raise SystemExit("ERROR: FACTORY anchor not found.")

marker = "    # MARKET PROVIDER ABSTRACT INTERFACE IMPLEMENTATION"

if marker in text:
    raise SystemExit("ERROR: Compatibility block already exists.")

block = r'''
    # =====================================================
    # MARKET PROVIDER ABSTRACT INTERFACE IMPLEMENTATION
    # =====================================================

    def authenticate(self) -> bool:
        return self.api_client is not None

    def logout(self):
        self.stop()
        return True

    def on_tick(self, tick):
        self._on_tick(tick)

    def get_quote(self, symbol: str) -> Dict:

        tick = self.get_latest_tick(symbol)

        if tick is None:
            return {}

        if hasattr(tick, "to_dict"):
            return tick.to_dict()

        if hasattr(tick, "__dict__"):
            return dict(tick.__dict__)

        return {
            "instrument_key": symbol,
            "tick": tick,
        }

    def get_quotes(
        self,
        symbols: List[str],
    ) -> Dict:

        return {
            symbol: self.get_quote(symbol)
            for symbol in symbols
        }

    def get_ltp(self, symbol: str):

        tick = self.get_latest_tick(symbol)

        if tick is None:
            return None

        for name in (
            "ltp",
            "last_price",
            "price",
        ):

            value = getattr(
                tick,
                name,
                None,
            )

            if value is not None:
                return value

        return None

    def get_market_depth(
        self,
        symbol: str,
    ) -> Dict:

        tick = self.get_latest_tick(symbol)

        if tick is None:
            return {}

        for name in (
            "market_depth",
            "depth",
        ):

            value = getattr(
                tick,
                name,
                None,
            )

            if value is not None:
                return value

        return {}

    def get_order_book(self):
        return []

    def get_positions(self):
        return []

    def get_holdings(self):
        return []

    def historical_data(
        self,
        *args,
        **kwargs,
    ):
        return []

    def intraday_data(
        self,
        *args,
        **kwargs,
    ):
        return []

    def instrument_master(self):
        return []

    def search_symbol(
        self,
        symbol: str,
    ):
        return []

    def exchange_list(self):

        return [
            "NSE",
            "BSE",
            "NFO",
            "BFO",
            "MCX",
        ]

    def market_status(self) -> Dict:

        return {
            "connected": self.connected,
            "state": self.connection_state,
        }

    def server_time(self):

        return datetime.now()

    def heartbeat(self) -> bool:

        return self.ping()

    def provider_info(self) -> Dict:

        return self.info()

    def capabilities(self) -> Dict:

        return {
            "live_market_data": True,
            "websocket": True,
            "subscriptions": True,
            "historical_data": False,
            "intraday_data": False,
            "orders": False,
            "positions": False,
            "holdings": False,
        }

    def health(self) -> Dict:

        return self.health_summary()

    def initialize(self) -> bool:

        return self.start()

    def shutdown(self):

        self.stop()

        return True


'''

text = text.replace(
    anchor,
    block + anchor,
    1,
)

path.write_text(
    text,
    encoding="utf-8",
)

print("PATCH INSERTED: OK")