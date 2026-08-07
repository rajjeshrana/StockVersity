    # =====================================================
    # MARKET PROVIDER INTERFACE COMPATIBILITY
    # =====================================================

    def authenticate(self) -> bool:
        """
        Authentication is supplied by the configured
        Upstox ApiClient/access token.
        """
        return self.api_client is not None

    def logout(self):
        """
        Stop the live provider session.
        """
        self.stop()
        return True

    def on_tick(self, tick):
        """
        Public MarketProvider tick callback.
        """
        self._on_tick(tick)

    def get_quote(self, symbol: str) -> Dict:
        """
        Return latest cached live quote.
        """
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

    def get_quotes(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Return latest cached quotes for symbols.
        """
        return {
            symbol: self.get_quote(symbol)
            for symbol in symbols
        }

    def get_ltp(self, symbol: str) -> float:
        """
        Return latest cached traded price.
        """
        tick = self.get_latest_tick(symbol)

        if tick is None:
            return 0.0

        for attribute in (
            "ltp",
            "last_price",
            "price",
        ):
            value = getattr(
                tick,
                attribute,
                None,
            )

            if value is not None:
                try:
                    return float(value)
                except (TypeError, ValueError):
                    pass

        return 0.0

    def historical_data(
        self,
        symbol: str,
        interval: str,
        start_date,
        end_date,
    ):
        """
        REST historical-data implementation will be
        attached after live-feed validation.
        """
        raise NotImplementedError(
            "Upstox historical REST adapter is not configured yet."
        )

    def intraday_data(
        self,
        symbol: str,
        interval: str,
    ):
        """
        REST intraday-data implementation will be
        attached after live-feed validation.
        """
        raise NotImplementedError(
            "Upstox intraday REST adapter is not configured yet."
        )

    def get_market_depth(self, symbol: str) -> Dict:
        """
        Return cached depth when available on Tick.
        """
        tick = self.get_latest_tick(symbol)

        if tick is None:
            return {}

        depth = getattr(
            tick,
            "depth",
            None,
        )

        if depth is None:
            depth = getattr(
                tick,
                "market_depth",
                None,
            )

        return depth if isinstance(depth, dict) else {}

    def get_order_book(self) -> List[Dict]:
        """
        REST order-book adapter pending.
        """
        return []

    def get_positions(self) -> List[Dict]:
        """
        REST positions adapter pending.
        """
        return []

    def get_holdings(self) -> List[Dict]:
        """
        REST holdings adapter pending.
        """
        return []

    def search_symbol(
        self,
        keyword: str,
    ) -> List[Dict]:
        """
        Instrument-master adapter pending.
        """
        return []

    def instrument_master(self) -> List[Dict]:
        """
        Instrument-master adapter pending.
        """
        return []

    def exchange_list(self) -> List[str]:
        """
        Exchanges supported by Upstox.
        """
        return [
            "NSE",
            "BSE",
            "NFO",
            "BFO",
            "MCX",
            "CDS",
        ]

    def market_status(self) -> Dict:
        """
        Lightweight provider market status.
        """
        from datetime import datetime

        now = datetime.now()

        return {
            "status": (
                "CONNECTED"
                if self.connected
                else "DISCONNECTED"
            ),
            "exchange": "NSE",
            "time": now.strftime("%H:%M:%S"),
        }

    def server_time(self):
        """
        Local runtime time until REST server-time
        adapter is attached.
        """
        from datetime import datetime

        return datetime.now()

    def heartbeat(self):
        """
        Provider heartbeat.
        """
        return self.ping()

    def provider_info(self) -> Dict:
        """
        MarketProvider-compatible provider information.
        """
        data = self.info()

        return {
            "name": data.get(
                "provider",
                self.provider_name,
            ),
            "version": data.get(
                "version",
                self.version,
            ),
            "connected": data.get(
                "connected",
                self.connected,
            ),
            "state": data.get(
                "state",
                self.connection_state,
            ),
            "healthy": data.get(
                "healthy",
                self.healthy,
            ),
        }

    def capabilities(self) -> Dict[str, bool]:
        """
        Upstox provider capabilities.
        """
        return {
            "websocket": True,
            "historical": False,
            "intraday": False,
            "market_depth": True,
            "positions": False,
            "holdings": False,
            "orders": False,
            "instrument_master": False,
        }

    def health(self) -> Dict:
        """
        MarketProvider-compatible health information.
        """
        return self.health_summary()

    def initialize(self):
        """
        Initialize provider resources.
        """
        return self.start()

    def shutdown(self):
        """
        Shutdown provider resources.
        """
        self.stop()
        return True