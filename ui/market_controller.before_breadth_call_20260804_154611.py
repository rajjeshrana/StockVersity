"""
=========================================================
StockVersity Scanner Pro
Powered by AI
Version : 4.0

File : ui/market_controller.py
=========================================================
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
    QTimer,
)

from ui.theme import current_theme


class MarketController(QObject):
    """
    Central Market Controller

    Responsibilities
    ----------------
    • Live NSE Market Data
    • Nifty
    • BankNifty
    • FinNifty
    • Midcap
    • India VIX
    • Market Breadth
    • Sector Rotation
    • Top Gainers
    • Top Losers
    • Market Status
    """

    marketUpdated = Signal(dict)

    marketStatusChanged = Signal(str)

    sectorUpdated = Signal(list)

    breadthUpdated = Signal(dict)

    indicesUpdated = Signal(dict)

    gainersUpdated = Signal(list)

    losersUpdated = Signal(list)

    statusChanged = Signal(str)

    statisticsUpdated = Signal(dict)

    def __init__(
        self,
        backend,
        dashboard=None,
        parent=None
    ):

        super().__init__(parent)

        self.backend = backend

        self.dashboard = dashboard

        self.market_open = False

        self.market_data = {}

        self.indices = {}

        self.sectors = []

        self.gainers = []

        self.losers = []

        self.breadth = {}

        self.last_update = None

        self._initialize()

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def _initialize(self):

        self._discover_widgets()

        self._create_timers()

        self._connect_signals()

    # =====================================================
    # DISCOVER UI
    # =====================================================

    def _discover_widgets(self):

        self.cards = {}

        self.tables = {}

        if self.dashboard is None:

            return

        if not hasattr(

            self.dashboard,

            "findChildren"

        ):

            return

        for widget in self.dashboard.findChildren(QObject):

            name = widget.objectName()

            if not name:

                continue

            if "card" in name.lower():

                self.cards[name] = widget

            elif "table" in name.lower():

                self.tables[name] = widget

    # =====================================================
    # TIMERS
    # =====================================================

    def _create_timers(self):

        self.market_timer = QTimer(self)

        self.market_timer.timeout.connect(

            self.refresh_market

        )

        self.status_timer = QTimer(self)

        self.status_timer.timeout.connect(

            self.check_market_status

        )

    # =====================================================
    # SIGNALS
    # =====================================================

    def _connect_signals(self):

        pass

    # =====================================================
    # START
    # =====================================================

    def start(self):

        self.market_timer.start(

            5000

        )

        self.status_timer.start(

            30000

        )

        self.statusChanged.emit(

            "Market Controller Started"

        )

    # =====================================================
    # STOP
    # =====================================================

    def stop(self):

        self.market_timer.stop()

        self.status_timer.stop()

    # =====================================================
    # MARKET STATUS
    # =====================================================

    def check_market_status(self):

        now = datetime.now()

        if now.weekday() >= 5:

            status = "Closed"

        else:

            current = now.hour * 60 + now.minute

            open_time = 9 * 60 + 15

            close_time = 15 * 60 + 30

            if current < open_time:

                status = "Pre Open"

            elif current <= close_time:

                status = "Open"

            else:

                status = "Closed"

        self.market_open = status == "Open"

        self.marketStatusChanged.emit(

            status

        )

        self.statusChanged.emit(

            f"Market Status : {status}"

        )

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh_market(self):

        try:

            self.market_data = self.backend.market_snapshot()

        except Exception:

            self.market_data = {}

            return

        # -------------------------------------------------
        # Merge the live NIFTY 500 universe into the legacy
        # backend snapshot.
        #
        # Existing index data remains untouched.
        # -------------------------------------------------

        self._merge_live_nifty500()

        self.last_update = datetime.now()

        self.update_indices()

        self.update_market_breadth()

        self.update_sectors()

        self.update_gainers()

        self.update_losers()

        self.marketUpdated.emit(

            self.market_data

        )

        self.update_statistics()

    # =====================================================
    # LIVE NIFTY 500 MERGE
    # =====================================================

    def _merge_live_nifty500(self):
        """
        Merge LiveStockUniverse data into market_data.

        Preserves:
            indices
            other legacy backend sections

        Replaces with live NIFTY 500 data:
            breadth
            sectors
            gainers
            losers
            heatmap
        """

        universe = getattr(
            self,
            "live_stock_universe",
            None,
        )

        if universe is None:
            return

        if not isinstance(
            self.market_data,
            dict,
        ):
            self.market_data = {}

        # -------------------------------------------------
        # BREADTH
        # -------------------------------------------------

        try:

            breadth = universe.breadth()

            if isinstance(
                breadth,
                dict,
            ):
                self.market_data[
                    "breadth"
                ] = breadth

        except Exception:
            pass

        # -------------------------------------------------
        # INDUSTRY STRENGTH -> SECTOR FORMAT
        # -------------------------------------------------

        try:

            industries = (
                universe.industry_strength()
            )

            sectors = []

            if isinstance(
                industries,
                list,
            ):

                for row in industries:

                    if not isinstance(
                        row,
                        dict,
                    ):
                        continue

                    name = str(
                        row.get(
                            "industry",
                            "Unknown",
                        )
                    )

                    try:
                        change = float(
                            row.get(
                                "average_change_percent",
                                0.0,
                            )
                            or 0.0
                        )
                    except (
                        TypeError,
                        ValueError,
                    ):
                        change = 0.0

                    sectors.append(
                        {
                            "name": name,
                            "sector": name,
                            "industry": name,

                            # Compatibility with the
                            # existing MarketController.
                            "change": change,
                            "change_percent": change,

                            "average_change_percent":
                                change,

                            "advance": row.get(
                                "advance",
                                0,
                            ),

                            "decline": row.get(
                                "decline",
                                0,
                            ),

                            "unchanged": row.get(
                                "unchanged",
                                0,
                            ),

                            "live_stocks": row.get(
                                "live_stocks",
                                0,
                            ),
                        }
                    )

            self.market_data[
                "sectors"
            ] = sectors

        except Exception:
            pass

        # -------------------------------------------------
        # GAINERS
        # -------------------------------------------------

        try:

            gainers = universe.top_gainers(
                limit=10
            )

            if isinstance(
                gainers,
                list,
            ):
                self.market_data[
                    "gainers"
                ] = gainers

        except Exception:
            pass

        # -------------------------------------------------
        # LOSERS
        # -------------------------------------------------

        try:

            losers = universe.top_losers(
                limit=10
            )

            if isinstance(
                losers,
                list,
            ):
                self.market_data[
                    "losers"
                ] = losers

        except Exception:
            pass

        # -------------------------------------------------
        # HEATMAP
        # -------------------------------------------------

        try:

            heatmap = universe.heatmap(
                limit=30
            )

            if isinstance(
                heatmap,
                list,
            ):
                self.market_data[
                    "heatmap"
                ] = heatmap

        except Exception:
            pass


    # =====================================================
    # UPDATE INDICES
    # =====================================================

    def update_indices(self):

        self.indices = self.market_data.get(

            "indices",

            {}

        )

        self.indicesUpdated.emit(

            self.indices

        )

    # =====================================================
    # MARKET BREADTH
    # =====================================================

    def update_market_breadth(self):

        self.breadth = self.market_data.get(

            "breadth",

            {}

        )

        self.breadthUpdated.emit(

            self.breadth

        )

    # =====================================================
    # SECTORS
    # =====================================================

    def update_sectors(self):

        self.sectors = self.market_data.get(

            "sectors",

            []

        )

        self.sectorUpdated.emit(

            self.sectors

        )

    # =====================================================
    # GAINERS
    # =====================================================

    def update_gainers(self):

        self.gainers = self.market_data.get(

            "gainers",

            []

        )

        self.gainersUpdated.emit(

            self.gainers

        )

    # =====================================================
    # LOSERS
    # =====================================================

    def update_losers(self):

        self.losers = self.market_data.get(

            "losers",

            []

        )

        self.losersUpdated.emit(

            self.losers

        )

    # =====================================================
    # MARKET STATISTICS
    # =====================================================

    def update_statistics(self):

        statistics = {

            "market_open":

                self.market_open,

            "indices":

                len(self.indices),

            "sectors":

                len(self.sectors),

            "gainers":

                len(self.gainers),

            "losers":

                len(self.losers),

            "last_update":

                self.last_update,

        }

        self.statisticsUpdated.emit(

            statistics

        )

        self.update_cards(

            statistics

        )

        self.update_tables()

    # =====================================================
    # DASHBOARD CARDS
    # =====================================================

    def update_cards(

        self,

        statistics

    ):

        mapping = {

            "market_status_card":

                "Open" if statistics["market_open"] else "Closed",

            "sector_count_card":

                statistics["sectors"],

            "gainers_count_card":

                statistics["gainers"],

            "losers_count_card":

                statistics["losers"],

        }

        for card_name, value in mapping.items():

            if card_name not in self.cards:

                continue

            card = self.cards[card_name]

            if hasattr(

                card,

                "set_value"

            ):

                card.set_value(

                    str(value)

                )

    # =====================================================
    # TABLE UPDATES
    # =====================================================

    def update_tables(self):

        self._update_gainers_table()

        self._update_losers_table()

        self._update_sector_table()

    # =====================================================
    # GAINERS TABLE
    # =====================================================

    def _update_gainers_table(self):

        if "gainers_table" not in self.tables:

            return

        table = self.tables["gainers_table"]

        if hasattr(

            table,

            "clear_rows"

        ):

            table.clear_rows()

        for stock in self.gainers:

            row = [

                stock.get("symbol", ""),

                stock.get("price", ""),

                stock.get("change", ""),

                stock.get("change_percent", ""),

                stock.get("volume", ""),

            ]

            if hasattr(

                table,

                "append_row"

            ):

                table.append_row(row)

    # =====================================================
    # LOSERS TABLE
    # =====================================================

    def _update_losers_table(self):

        if "losers_table" not in self.tables:

            return

        table = self.tables["losers_table"]

        if hasattr(

            table,

            "clear_rows"

        ):

            table.clear_rows()

        for stock in self.losers:

            row = [

                stock.get("symbol", ""),

                stock.get("price", ""),

                stock.get("change", ""),

                stock.get("change_percent", ""),

                stock.get("volume", ""),

            ]

            if hasattr(

                table,

                "append_row"

            ):

                table.append_row(row)

    # =====================================================
    # SECTOR TABLE
    # =====================================================

    def _update_sector_table(self):

        if "sector_table" not in self.tables:

            return

        table = self.tables["sector_table"]

        if hasattr(

            table,

            "clear_rows"

        ):

            table.clear_rows()

        ranked = self.rank_sectors()

        for sector in ranked:

            row = [

                sector.get(

                    "sector",

                    ""

                ),

                sector.get(

                    "change",

                    ""

                ),

                sector.get(

                    "advance",

                    ""

                ),

                sector.get(

                    "decline",

                    ""

                ),

            ]

            if hasattr(

                table,

                "append_row"

            ):

                table.append_row(row)

    # =====================================================
    # SEARCH
    # =====================================================

    def search_stock(

        self,

        keyword: str

    ):

        keyword = keyword.upper()

        results = []

        universe = self.gainers + self.losers

        for stock in universe:

            symbol = str(

                stock.get(

                    "symbol",

                    ""

                )

            ).upper()

            company = str(

                stock.get(

                    "company",

                    ""

                )

            ).upper()

            if keyword in symbol or keyword in company:

                results.append(stock)

        return results

    # =====================================================
    # SECTOR RANKING
    # =====================================================

    def rank_sectors(self):

        return sorted(

            self.sectors,

            key=lambda sector: sector.get(

                "change",

                0

            ),

            reverse=True

        )

    # =====================================================
    # SORT GAINERS
    # =====================================================

    def sort_gainers(

        self,

        field="change_percent"

    ):

        self.gainers.sort(

            key=lambda stock: stock.get(

                field,

                0

            ),

            reverse=True

        )

        self._update_gainers_table()

    # =====================================================
    # SORT LOSERS
    # =====================================================

    def sort_losers(

        self,

        field="change_percent"

    ):

        self.losers.sort(

            key=lambda stock: stock.get(

                field,

                0

            )

        )

        self._update_losers_table()

    # =====================================================
    # STATUS
    # =====================================================

    def set_status(

        self,

        message

    ):

        self.statusChanged.emit(

            message

        )

    # =====================================================
    # AUTO REFRESH
    # =====================================================

    def set_refresh_interval(

        self,

        seconds: int

    ):

        self.market_timer.setInterval(

            max(

                1,

                seconds

            ) * 1000

        )

    def refresh_interval(self):

        return self.market_timer.interval() // 1000

    def auto_refresh_enabled(self):

        return self.market_timer.isActive()

    # =====================================================
    # LAST UPDATE
    # =====================================================

    def last_update_text(self):

        if self.last_update is None:

            return "Never"

        return self.last_update.strftime(

            "%d-%m-%Y %H:%M:%S"

        )

    # =====================================================
    # INDEX CARDS
    # =====================================================

    def update_index_cards(self):
        """
        Update the fixed StockVersity dashboard index cards.

        Expected dashboard card keys:
            NIFTY
            BANKNIFTY
            FINNIFTY
            INDIAVIX

        Expected market snapshot keys:
            NIFTY
            BANKNIFTY
            FINNIFTY
            INDIA VIX
        """

        if self.dashboard is None:
            return

        index_cards = getattr(
            self.dashboard,
            "index_cards",
            None,
        )

        if not index_cards:
            return

        mapping = {
            "NIFTY": "NIFTY",
            "BANKNIFTY": "BANKNIFTY",
            "FINNIFTY": "FINNIFTY",
            "INDIA VIX": "INDIAVIX",
        }

        for market_key, card_key in mapping.items():

            data = self.indices.get(
                market_key,
                {},
            )

            if not data:
                continue

            card = index_cards.get(
                card_key
            )

            if card is None:
                continue

            # ---------------------------------------------
            # LTP / VALUE
            # ---------------------------------------------

            value = data.get(
                "ltp",
                data.get(
                    "value",
                    data.get(
                        "last_price",
                        0.0,
                    ),
                ),
            )

            # ---------------------------------------------
            # PERCENTAGE CHANGE
            # ---------------------------------------------

            change = data.get(
                "change_percent",
                data.get(
                    "change_pct",
                    data.get(
                        "change",
                        0.0,
                    ),
                ),
            )

            try:
                value = float(value or 0.0)
            except (TypeError, ValueError):
                value = 0.0

            try:
                change = float(change or 0.0)
            except (TypeError, ValueError):
                change = 0.0

            # ---------------------------------------------
            # HISTORY FOR SPARKLINE
            # ---------------------------------------------

            history = data.get(
                "history",
                [],
            )

            if not isinstance(
                history,
                (list, tuple),
            ):
                history = []

            history = list(history)

            # Until historical intraday series is connected,
            # preserve a small usable sparkline series.

            if not history and value:

                history = [
                    value,
                    value,
                ]

            # ---------------------------------------------
            # UPDATE FIXED DASHBOARD CARD
            # ---------------------------------------------

            if hasattr(
                card,
                "update_data",
            ):

                card.update_data(
                    value,
                    change,
                    history,
                )

    # =====================================================
    # MARKET BREADTH
    # =====================================================

    def update_breadth_cards(self):

        mapping = {

            "advance_card":

                self.breadth.get(

                    "advance",

                    0

                ),

            "decline_card":

                self.breadth.get(

                    "decline",

                    0

                ),

            "unchanged_card":

                self.breadth.get(

                    "unchanged",

                    0

                ),

        }

        for card_name, value in mapping.items():

            if card_name in self.cards:

                card = self.cards[card_name]

                if hasattr(

                    card,

                    "set_value"

                ):

                    card.set_value(

                        str(value)

                    )

        # -------------------------------------------------
        # LIVE BREADTH GAUGE
        # -------------------------------------------------

        gauge = getattr(
            self.dashboard,
            "breadth_gauge",
            None,
        )

        if gauge is not None:

            advance = self.breadth.get(
                "advance",
                0,
            )

            decline = self.breadth.get(
                "decline",
                0,
            )

            unchanged = self.breadth.get(
                "unchanged",
                0,
            )

            try:
                advance = float(advance or 0)
                decline = float(decline or 0)
                unchanged = float(unchanged or 0)

            except (TypeError, ValueError):
                advance = 0.0
                decline = 0.0
                unchanged = 0.0

            total = (
                advance
                + decline
                + unchanged
            )

            breadth_percent = (
                advance / total * 100.0
                if total > 0
                else 0.0
            )

            if hasattr(
                gauge,
                "set_value",
            ):
                gauge.set_value(
                    breadth_percent
                )

    # =====================================================
    # SECTOR LEADERS
    # =====================================================

    def sector_leaders(self):

        if not self.sectors:

            return []

        return sorted(

            self.sectors,

            key=lambda sector: sector.get(

                "change",

                0

            ),

            reverse=True

        )[:5]

    def sector_laggards(self):

        if not self.sectors:

            return []

        return sorted(

            self.sectors,

            key=lambda sector: sector.get(

                "change",

                0

            )

        )[:5]

    # =====================================================
    # GAINERS / LOSERS
    # =====================================================

    def top_gainers(

        self,

        limit=10

    ):

        return sorted(

            self.gainers,

            key=lambda stock: stock.get(

                "change_percent",

                0

            ),

            reverse=True

        )[:limit]

    def top_losers(

        self,

        limit=10

    ):

        return sorted(

            self.losers,

            key=lambda stock: stock.get(

                "change_percent",

                0

            )

        )[:limit]

    # =====================================================
    # DASHBOARD NOTIFICATIONS
    # =====================================================

    def notify_dashboard(

        self,

        message: str

    ):

        if self.dashboard is not None:

            if hasattr(

                self.dashboard,

                "show_notification"

            ):

                self.dashboard.show_notification(

                    message

                )

        self.statusChanged.emit(

            message

        )

    # =====================================================
    # MARKET HEALTH
    # =====================================================

    def market_health(self):

        advance = self.breadth.get(

            "advance",

            0

        )

        decline = self.breadth.get(

            "decline",

            0

        )

        if advance > decline:

            sentiment = "Bullish"

        elif decline > advance:

            sentiment = "Bearish"

        else:

            sentiment = "Neutral"

        return {

            "sentiment":

                sentiment,

            "market_open":

                self.market_open,

            "indices":

                len(self.indices),

            "sectors":

                len(self.sectors),

            "gainers":

                len(self.gainers),

            "losers":

                len(self.losers),

        }

    # =====================================================
    # BACKEND SYNC
    # =====================================================

    def synchronize_backend(self):

        if hasattr(

            self.backend,

            "refresh"

        ):

            self.backend.refresh()

        elif hasattr(

            self.backend,

            "synchronize"

        ):

            self.backend.synchronize()

        self.statusChanged.emit(

            "Market backend synchronized"

        )

    # =====================================================
    # SNAPSHOT CACHE
    # =====================================================

    def cache_snapshot(self):

        self._snapshot_cache = {

            "timestamp":

                self.last_update,

            "market":

                self.market_data,

            "indices":

                self.indices,

            "breadth":

                self.breadth,

            "sectors":

                self.sectors,

            "gainers":

                self.gainers,

            "losers":

                self.losers,

        }

    def cached_snapshot(self):

        return getattr(

            self,

            "_snapshot_cache",

            {}

        )