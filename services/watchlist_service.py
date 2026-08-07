from __future__ import annotations

"""
==========================================================
StockVersity Scanner Pro
Watchlist Service

Author  : StockVersity
Version : 1.0.0

Responsibilities
----------------
• Multiple watchlists
• Add / Remove symbols
• Live quote updates
• Scanner integration
• Alert integration
• Sorting
• Import / Export
• Persistence
• Statistics
• Diagnostics
==========================================================
"""

import json
import logging
import threading

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional

from services.alert_service import AlertService
from services.data_service import DataService


# ==========================================================
# WATCHLIST TYPE
# ==========================================================

class WatchlistType(Enum):
    """
    Watchlist category.
    """

    DEFAULT = "default"

    INTRADAY = "intraday"

    SWING = "swing"

    POSITIONAL = "positional"

    CUSTOM = "custom"


# ==========================================================
# WATCHLIST ITEM
# ==========================================================

@dataclass(slots=True)
class WatchlistItem:
    """
    Single watchlist entry.
    """

    symbol: str

    instrument_key: str

    exchange: str = "NSE"

    added: datetime = field(
        default_factory=datetime.now
    )

    last_price: float = 0.0

    change: float = 0.0

    change_percent: float = 0.0

    volume: int = 0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ==========================================================
# WATCHLIST
# ==========================================================

@dataclass(slots=True)
class Watchlist:
    """
    Watchlist model.
    """

    name: str

    watchlist_type: WatchlistType

    created: datetime = field(
        default_factory=datetime.now
    )

    items: List[
        WatchlistItem
    ] = field(
        default_factory=list
    )


# ==========================================================
# STATISTICS
# ==========================================================

@dataclass(slots=True)
class WatchlistStatistics:

    watchlists_created: int = 0

    symbols_added: int = 0

    symbols_removed: int = 0

    refresh_requests: int = 0

    import_operations: int = 0

    export_operations: int = 0


# ==========================================================
# WATCHLIST SERVICE
# ==========================================================

class WatchlistService:
    """
    Central watchlist manager.
    """

    VERSION = "1.0.0"

    DEFAULT_NAME = "My Watchlist"

    def __init__(
        self,
        data_service: DataService,
        alert_service: AlertService,
    ) -> None:

        self.logger = logging.getLogger(
            self.__class__.__name__
        )

        self._data_service = data_service

        self._alert_service = alert_service

        self._statistics = (
            WatchlistStatistics()
        )

        self._watchlists: Dict[
            str,
            Watchlist
        ] = {}

        self._callbacks: Dict[
            str,
            List[Callable[..., None]]
        ] = {}

        self._lock = threading.RLock()

        self._started = datetime.now()

        self.create_watchlist(
            self.DEFAULT_NAME
        )

        self.logger.info(
            "WatchlistService initialized."
        )
            # ==========================================================
    # PROPERTIES
    # ==========================================================

    @property
    def data_service(self) -> DataService:
        """
        Return DataService instance.
        """

        return self._data_service

    @property
    def alert_service(self) -> AlertService:
        """
        Return AlertService instance.
        """

        return self._alert_service

    @property
    def statistics(self) -> WatchlistStatistics:
        """
        Return runtime statistics.
        """

        return self._statistics

    @property
    def uptime(self):
        """
        Service uptime.
        """

        return datetime.now() - self._started

    # ==========================================================
    # EVENTS
    # ==========================================================

    def register_event(
        self,
        event: str,
        callback: Callable[..., None],
    ) -> None:
        """
        Register event callback.
        """

        self._callbacks.setdefault(
            event,
            [],
        ).append(callback)

    def unregister_event(
        self,
        event: str,
        callback: Callable[..., None],
    ) -> None:
        """
        Remove callback.
        """

        callbacks = self._callbacks.get(
            event,
        )

        if callbacks is None:

            return

        try:

            callbacks.remove(callback)

        except ValueError:

            pass

    def clear_events(self) -> None:
        """
        Remove all callbacks.
        """

        self._callbacks.clear()

    def _emit(
        self,
        event: str,
        **kwargs: Any,
    ) -> None:
        """
        Notify subscribers.
        """

        callbacks = self._callbacks.get(
            event,
            [],
        )

        for callback in callbacks:

            try:

                callback(**kwargs)

            except Exception:

                self.logger.exception(
                    "Watchlist callback failed."
                )

    # ==========================================================
    # WATCHLIST MANAGEMENT
    # ==========================================================

    def create_watchlist(
        self,
        name: str,
        watchlist_type: WatchlistType = WatchlistType.CUSTOM,
    ) -> Watchlist:
        """
        Create a new watchlist.
        """

        if name in self._watchlists:

            return self._watchlists[name]

        watchlist = Watchlist(

            name=name,

            watchlist_type=watchlist_type,

        )

        self._watchlists[name] = watchlist

        self._statistics.watchlists_created += 1

        self._emit(

            "watchlist_created",

            watchlist=watchlist,

        )

        return watchlist

    def delete_watchlist(
        self,
        name: str,
    ) -> bool:
        """
        Delete a watchlist.
        """

        if name == self.DEFAULT_NAME:

            return False

        watchlist = self._watchlists.pop(
            name,
            None,
        )

        if watchlist is None:

            return False

        self._emit(

            "watchlist_deleted",

            watchlist=watchlist,

        )

        return True

    def rename_watchlist(
        self,
        old_name: str,
        new_name: str,
    ) -> bool:
        """
        Rename a watchlist.
        """

        if old_name not in self._watchlists:

            return False

        if new_name in self._watchlists:

            return False

        watchlist = self._watchlists.pop(
            old_name,
        )

        watchlist.name = new_name

        self._watchlists[new_name] = watchlist

        self._emit(

            "watchlist_renamed",

            old_name=old_name,

            new_name=new_name,

        )

        return True

    def watchlist(
        self,
        name: str = DEFAULT_NAME,
    ) -> Optional[Watchlist]:
        """
        Return watchlist.
        """

        return self._watchlists.get(
            name,
        )

    def watchlists(
        self,
    ) -> List[Watchlist]:
        """
        Return all watchlists.
        """

        return list(
            self._watchlists.values(),
        )

    # ==========================================================
    # SYMBOL MANAGEMENT
    # ==========================================================

    def add_symbol(
        self,
        watchlist_name: str,
        symbol: str,
        instrument_key: str,
        exchange: str = "NSE",
    ) -> bool:
        """
        Add symbol to watchlist.
        """

        watchlist = self.watchlist(
            watchlist_name,
        )

        if watchlist is None:

            return False

        for item in watchlist.items:

            if item.symbol == symbol:

                return False

        watchlist.items.append(

            WatchlistItem(

                symbol=symbol,

                instrument_key=instrument_key,

                exchange=exchange,

            )

        )

        self._statistics.symbols_added += 1

        self._emit(

            "symbol_added",

            watchlist=watchlist_name,

            symbol=symbol,

        )

        return True

    def remove_symbol(
        self,
        watchlist_name: str,
        symbol: str,
    ) -> bool:
        """
        Remove symbol from watchlist.
        """

        watchlist = self.watchlist(
            watchlist_name,
        )

        if watchlist is None:

            return False

        for index, item in enumerate(
            watchlist.items,
        ):

            if item.symbol == symbol:

                watchlist.items.pop(index)

                self._statistics.symbols_removed += 1

                self._emit(

                    "symbol_removed",

                    watchlist=watchlist_name,

                    symbol=symbol,

                )

                return True

        return False
        # ==========================================================
    # REORDER
    # ==========================================================

    def move_symbol(
        self,
        watchlist_name: str,
        from_index: int,
        to_index: int,
    ) -> bool:
        """
        Move a symbol within a watchlist.
        """

        watchlist = self.watchlist(
            watchlist_name,
        )

        if watchlist is None:

            return False

        if (

            from_index < 0

            or from_index >= len(watchlist.items)

            or to_index < 0

            or to_index >= len(watchlist.items)

        ):

            return False

        item = watchlist.items.pop(
            from_index,
        )

        watchlist.items.insert(
            to_index,
            item,
        )

        self._emit(

            "watchlist_reordered",

            watchlist=watchlist_name,

        )

        return True

    # ==========================================================
    # LIVE REFRESH
    # ==========================================================

    def refresh_watchlist(
        self,
        watchlist_name: str = DEFAULT_NAME,
    ) -> bool:
        """
        Refresh live quotes for a watchlist.
        """

        watchlist = self.watchlist(
            watchlist_name,
        )

        if watchlist is None:

            return False

        self._statistics.refresh_requests += 1

        for item in watchlist.items:

            try:

                quote = self._data_service.get_quote(

                    item.instrument_key,

                )

                previous_price = item.last_price

                item.last_price = float(

                    quote.get(

                        "last_price",

                        quote.get(

                            "ltp",

                            0.0,

                        ),

                    )

                )

                item.volume = int(

                    quote.get(

                        "volume",

                        0,

                    )

                )

                if previous_price > 0:

                    item.change = (

                        item.last_price

                        - previous_price

                    )

                    item.change_percent = round(

                        (

                            item.change

                            / previous_price

                        ) * 100,

                        2,

                    )

            except Exception:

                self.logger.exception(

                    "Failed to refresh %s.",

                    item.symbol,

                )

        self._emit(

            "watchlist_refreshed",

            watchlist=watchlist_name,

        )

        return True

    # ==========================================================
    # SORTING
    # ==========================================================

    def sort_by_price(
        self,
        watchlist_name: str,
        reverse: bool = True,
    ) -> bool:
        """
        Sort by last traded price.
        """

        watchlist = self.watchlist(
            watchlist_name,
        )

        if watchlist is None:

            return False

        watchlist.items.sort(

            key=lambda x: x.last_price,

            reverse=reverse,

        )

        return True

    def sort_by_change(
        self,
        watchlist_name: str,
        reverse: bool = True,
    ) -> bool:
        """
        Sort by percentage change.
        """

        watchlist = self.watchlist(
            watchlist_name,
        )

        if watchlist is None:

            return False

        watchlist.items.sort(

            key=lambda x: x.change_percent,

            reverse=reverse,

        )

        return True

    def sort_by_volume(
        self,
        watchlist_name: str,
        reverse: bool = True,
    ) -> bool:
        """
        Sort by traded volume.
        """

        watchlist = self.watchlist(
            watchlist_name,
        )

        if watchlist is None:

            return False

        watchlist.items.sort(

            key=lambda x: x.volume,

            reverse=reverse,

        )

        return True

    # ==========================================================
    # SEARCH
    # ==========================================================

    def find_symbol(
        self,
        watchlist_name: str,
        symbol: str,
    ) -> Optional[WatchlistItem]:
        """
        Find a symbol in a watchlist.
        """

        watchlist = self.watchlist(
            watchlist_name,
        )

        if watchlist is None:

            return None

        symbol = symbol.upper()

        for item in watchlist.items:

            if item.symbol.upper() == symbol:

                return item

        return None

    # ==========================================================
    # GAINERS / LOSERS
    # ==========================================================

    def top_gainers(
        self,
        watchlist_name: str,
        limit: int = 5,
    ) -> List[WatchlistItem]:
        """
        Return top gaining symbols.
        """

        watchlist = self.watchlist(
            watchlist_name,
        )

        if watchlist is None:

            return []

        return sorted(

            watchlist.items,

            key=lambda item: item.change_percent,

            reverse=True,

        )[:limit]

    def top_losers(
        self,
        watchlist_name: str,
        limit: int = 5,
    ) -> List[WatchlistItem]:
        """
        Return top losing symbols.
        """

        watchlist = self.watchlist(
            watchlist_name,
        )

        if watchlist is None:

            return []

        return sorted(

            watchlist.items,

            key=lambda item: item.change_percent,

        )[:limit]

    # ==========================================================
    # ALERTS
    # ==========================================================

    def notify_price_change(
        self,
        item: WatchlistItem,
        threshold: float = 5.0,
    ) -> None:
        """
        Generate an alert when the percentage
        change exceeds the configured threshold.
        """

        if abs(item.change_percent) < threshold:

            return

        self._alert_service.price_alert(

            symbol=item.symbol,

            price=item.last_price,

            message=(

                f"{item.symbol} moved "

                f"{item.change_percent:.2f}%"

            ),

        )
            # ==========================================================
    # REORDER
    # ==========================================================

    def move_symbol(
        self,
        watchlist_name: str,
        from_index: int,
        to_index: int,
    ) -> bool:
        """
        Move a symbol within a watchlist.
        """

        watchlist = self.watchlist(
            watchlist_name,
        )

        if watchlist is None:

            return False

        if (

            from_index < 0

            or from_index >= len(watchlist.items)

            or to_index < 0

            or to_index >= len(watchlist.items)

        ):

            return False

        item = watchlist.items.pop(
            from_index,
        )

        watchlist.items.insert(
            to_index,
            item,
        )

        self._emit(

            "watchlist_reordered",

            watchlist=watchlist_name,

        )

        return True

    # ==========================================================
    # LIVE REFRESH
    # ==========================================================

    def refresh_watchlist(
        self,
        watchlist_name: str = DEFAULT_NAME,
    ) -> bool:
        """
        Refresh live quotes for a watchlist.
        """

        watchlist = self.watchlist(
            watchlist_name,
        )

        if watchlist is None:

            return False

        self._statistics.refresh_requests += 1

        for item in watchlist.items:

            try:

                quote = self._data_service.get_quote(

                    item.instrument_key,

                )

                previous_price = item.last_price

                item.last_price = float(

                    quote.get(

                        "last_price",

                        quote.get(

                            "ltp",

                            0.0,

                        ),

                    )

                )

                item.volume = int(

                    quote.get(

                        "volume",

                        0,

                    )

                )

                if previous_price > 0:

                    item.change = (

                        item.last_price

                        - previous_price

                    )

                    item.change_percent = round(

                        (

                            item.change

                            / previous_price

                        ) * 100,

                        2,

                    )

            except Exception:

                self.logger.exception(

                    "Failed to refresh %s.",

                    item.symbol,

                )

        self._emit(

            "watchlist_refreshed",

            watchlist=watchlist_name,

        )

        return True

    # ==========================================================
    # SORTING
    # ==========================================================

    def sort_by_price(
        self,
        watchlist_name: str,
        reverse: bool = True,
    ) -> bool:
        """
        Sort by last traded price.
        """

        watchlist = self.watchlist(
            watchlist_name,
        )

        if watchlist is None:

            return False

        watchlist.items.sort(

            key=lambda x: x.last_price,

            reverse=reverse,

        )

        return True

    def sort_by_change(
        self,
        watchlist_name: str,
        reverse: bool = True,
    ) -> bool:
        """
        Sort by percentage change.
        """

        watchlist = self.watchlist(
            watchlist_name,
        )

        if watchlist is None:

            return False

        watchlist.items.sort(

            key=lambda x: x.change_percent,

            reverse=reverse,

        )

        return True

    def sort_by_volume(
        self,
        watchlist_name: str,
        reverse: bool = True,
    ) -> bool:
        """
        Sort by traded volume.
        """

        watchlist = self.watchlist(
            watchlist_name,
        )

        if watchlist is None:

            return False

        watchlist.items.sort(

            key=lambda x: x.volume,

            reverse=reverse,

        )

        return True

    # ==========================================================
    # SEARCH
    # ==========================================================

    def find_symbol(
        self,
        watchlist_name: str,
        symbol: str,
    ) -> Optional[WatchlistItem]:
        """
        Find a symbol in a watchlist.
        """

        watchlist = self.watchlist(
            watchlist_name,
        )

        if watchlist is None:

            return None

        symbol = symbol.upper()

        for item in watchlist.items:

            if item.symbol.upper() == symbol:

                return item

        return None

    # ==========================================================
    # GAINERS / LOSERS
    # ==========================================================

    def top_gainers(
        self,
        watchlist_name: str,
        limit: int = 5,
    ) -> List[WatchlistItem]:
        """
        Return top gaining symbols.
        """

        watchlist = self.watchlist(
            watchlist_name,
        )

        if watchlist is None:

            return []

        return sorted(

            watchlist.items,

            key=lambda item: item.change_percent,

            reverse=True,

        )[:limit]

    def top_losers(
        self,
        watchlist_name: str,
        limit: int = 5,
    ) -> List[WatchlistItem]:
        """
        Return top losing symbols.
        """

        watchlist = self.watchlist(
            watchlist_name,
        )

        if watchlist is None:

            return []

        return sorted(

            watchlist.items,

            key=lambda item: item.change_percent,

        )[:limit]

    # ==========================================================
    # ALERTS
    # ==========================================================

    def notify_price_change(
        self,
        item: WatchlistItem,
        threshold: float = 5.0,
    ) -> None:
        """
        Generate an alert when the percentage
        change exceeds the configured threshold.
        """

        if abs(item.change_percent) < threshold:

            return

        self._alert_service.price_alert(

            symbol=item.symbol,

            price=item.last_price,

            message=(

                f"{item.symbol} moved "

                f"{item.change_percent:.2f}%"

            ),

        )
            # ==========================================================
    # CSV EXPORT
    # ==========================================================

    def export_csv(
        self,
        file_path: str,
        watchlist_name: str = DEFAULT_NAME,
    ) -> bool:
        """
        Export a watchlist to CSV.
        """

        import csv

        watchlist = self.watchlist(
            watchlist_name,
        )

        if watchlist is None:

            return False

        with open(
            file_path,
            "w",
            newline="",
            encoding="utf-8",
        ) as csv_file:

            writer = csv.writer(csv_file)

            writer.writerow(
                [
                    "Symbol",
                    "Instrument Key",
                    "Exchange",
                    "Last Price",
                    "Change %",
                    "Volume",
                ]
            )

            for item in watchlist.items:

                writer.writerow(
                    [
                        item.symbol,
                        item.instrument_key,
                        item.exchange,
                        item.last_price,
                        item.change_percent,
                        item.volume,
                    ]
                )

        self._statistics.export_operations += 1

        self._emit(
            "watchlist_exported_csv",
            watchlist=watchlist_name,
            file=file_path,
        )

        return True

    # ==========================================================
    # CSV IMPORT
    # ==========================================================

    def import_csv(
        self,
        file_path: str,
        watchlist_name: str = DEFAULT_NAME,
    ) -> int:
        """
        Import symbols from a CSV file.
        """

        import csv

        watchlist = self.watchlist(
            watchlist_name,
        )

        if watchlist is None:

            watchlist = self.create_watchlist(
                watchlist_name,
            )

        imported = 0

        with open(
            file_path,
            newline="",
            encoding="utf-8",
        ) as csv_file:

            reader = csv.DictReader(csv_file)

            for row in reader:

                if self.add_symbol(
                    watchlist_name,
                    row["Symbol"],
                    row["Instrument Key"],
                    row.get(
                        "Exchange",
                        "NSE",
                    ),
                ):

                    imported += 1

        self._statistics.import_operations += 1

        self._emit(
            "watchlist_imported_csv",
            watchlist=watchlist_name,
            file=file_path,
        )

        return imported

    # ==========================================================
    # STATISTICS
    # ==========================================================

    def statistics_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Return statistics as a dictionary.
        """

        return {

            "watchlists_created":
                self._statistics.watchlists_created,

            "symbols_added":
                self._statistics.symbols_added,

            "symbols_removed":
                self._statistics.symbols_removed,

            "refresh_requests":
                self._statistics.refresh_requests,

            "import_operations":
                self._statistics.import_operations,

            "export_operations":
                self._statistics.export_operations,

        }

    def performance_report(
        self,
    ) -> Dict[str, Any]:
        """
        Return performance metrics.
        """

        total_symbols = sum(
            len(w.items)
            for w in self._watchlists.values()
        )

        return {

            "version":
                self.VERSION,

            "uptime":
                str(self.uptime),

            "watchlists":
                len(self._watchlists),

            "symbols":
                total_symbols,

            "statistics":
                self.statistics_dict(),

        }

    # ==========================================================
    # DIAGNOSTICS
    # ==========================================================

    def diagnostics(
        self,
    ) -> Dict[str, Any]:
        """
        Return diagnostic information.
        """

        return {

            "healthy":
                True,

            "watchlists":
                len(self._watchlists),

            "callbacks":
                sum(
                    len(v)
                    for v
                    in self._callbacks.values()
                ),

            "cache_available":
                hasattr(
                    self._data_service,
                    "get_cache",
                ),

            "uptime":
                str(self.uptime),

        }

    def health(
        self,
    ) -> Dict[str, Any]:
        """
        Service health report.
        """

        return {

            "service":
                self.__class__.__name__,

            "status":
                "running",

            "version":
                self.VERSION,

            "watchlists":
                len(self._watchlists),

        }

    def summary(
        self,
    ) -> Dict[str, Any]:
        """
        Summary of the service.
        """

        return {

            "health":
                self.health(),

            "performance":
                self.performance_report(),

            "diagnostics":
                self.diagnostics(),

        }
        # ==========================================================
    # LIFECYCLE
    # ==========================================================

    def start(self) -> None:
        """
        Start the watchlist service.
        """

        self.logger.info(
            "Starting WatchlistService..."
        )

        self._started = datetime.now()

        self._emit(
            "service_started",
        )

    def stop(self) -> None:
        """
        Stop the watchlist service.
        """

        self.logger.info(
            "Stopping WatchlistService..."
        )

        self._emit(
            "service_stopped",
        )

    def restart(self) -> None:
        """
        Restart the service.
        """

        self.stop()

        self.start()

    # ==========================================================
    # RESET / CLEAR
    # ==========================================================

    def clear_watchlist(
        self,
        watchlist_name: str = DEFAULT_NAME,
    ) -> bool:
        """
        Remove all symbols from a watchlist.
        """

        watchlist = self.watchlist(
            watchlist_name,
        )

        if watchlist is None:

            return False

        watchlist.items.clear()

        self._emit(
            "watchlist_cleared",
            watchlist=watchlist_name,
        )

        return True

    def clear_all_watchlists(self) -> None:
        """
        Remove all symbols from every watchlist.
        """

        for watchlist in self._watchlists.values():

            watchlist.items.clear()

        self._emit(
            "all_watchlists_cleared",
        )

    def reset(self) -> None:
        """
        Reset the service.
        """

        self.clear_all_watchlists()

        self._statistics = WatchlistStatistics()

        self._emit(
            "service_reset",
        )

    # ==========================================================
    # SNAPSHOT
    # ==========================================================

    def snapshot(self) -> Dict[str, Any]:
        """
        Return current runtime snapshot.
        """

        return {

            "version":
                self.VERSION,

            "watchlists":
                len(self._watchlists),

            "symbols":
                sum(
                    len(w.items)
                    for w
                    in self._watchlists.values()
                ),

            "uptime":
                str(self.uptime),

            "statistics":
                self.statistics_dict(),

        }

    # ==========================================================
    # SERIALIZATION
    # ==========================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize service state.
        """

        return {

            "watchlists": {

                name: {

                    "type":
                        watchlist.watchlist_type.value,

                    "items": [

                        {

                            "symbol":
                                item.symbol,

                            "instrument_key":
                                item.instrument_key,

                            "exchange":
                                item.exchange,

                            "last_price":
                                item.last_price,

                            "change_percent":
                                item.change_percent,

                            "volume":
                                item.volume,

                        }

                        for item

                        in watchlist.items

                    ],

                }

                for name, watchlist

                in self._watchlists.items()

            },

            "statistics":
                self.statistics_dict(),

        }

    def dump(self) -> Dict[str, Any]:
        """
        Dump internal state.
        """

        return {

            "summary":
                self.summary(),

            "snapshot":
                self.snapshot(),

            "state":
                self.to_dict(),

        }

    # ==========================================================
    # CLONE
    # ==========================================================

    def clone(self) -> "WatchlistService":
        """
        Create a shallow copy of the service.
        """

        cloned = WatchlistService(

            data_service=self._data_service,

            alert_service=self._alert_service,

        )

        for name, watchlist in self._watchlists.items():

            cloned._watchlists[name] = Watchlist(

                name=watchlist.name,

                watchlist_type=watchlist.watchlist_type,

                created=watchlist.created,

                items=list(watchlist.items),

            )

        return cloned

    # ==========================================================
    # CLEANUP
    # ==========================================================

    def dispose(self) -> None:
        """
        Release resources.
        """

        self.clear_events()

        self.clear_all_watchlists()

        self.logger.info(
            "WatchlistService disposed."
        )

    # ==========================================================
    # CONTEXT MANAGER
    # ==========================================================

    def __enter__(self) -> "WatchlistService":

        self.start()

        return self

    def __exit__(
        self,
        exc_type,
        exc,
        traceback,
    ) -> None:

        self.stop()

    # ==========================================================
    # REPRESENTATION
    # ==========================================================

    def __repr__(self) -> str:

        return (

            f"{self.__class__.__name__}"

            f"(watchlists={len(self._watchlists)})"

        )

    def __str__(self) -> str:

        return (

            f"{self.__class__.__name__} "

            f"v{self.VERSION}"

        )
        # ==========================================================
    # EVENT UTILITIES
    # ==========================================================

    def event_count(self) -> int:
        """
        Return the total number of registered callbacks.
        """

        return sum(

            len(callbacks)

            for callbacks

            in self._callbacks.values()

        )

    def events(self) -> Dict[str, int]:
        """
        Return registered event summary.
        """

        return {

            event: len(callbacks)

            for event, callbacks

            in self._callbacks.items()

        }

    def has_event(
        self,
        event: str,
    ) -> bool:
        """
        Return True if the specified event
        has at least one subscriber.
        """

        return (

            event in self._callbacks

            and

            len(self._callbacks[event]) > 0

        )

    # ==========================================================
    # WATCHLIST UTILITIES
    # ==========================================================

    def watchlist_exists(
        self,
        name: str,
    ) -> bool:
        """
        Check whether a watchlist exists.
        """

        return name in self._watchlists

    def watchlist_names(self) -> List[str]:
        """
        Return all watchlist names.
        """

        return sorted(

            self._watchlists.keys()

        )

    def watchlist_count(self) -> int:
        """
        Return total watchlists.
        """

        return len(

            self._watchlists

        )

    def total_symbols(self) -> int:
        """
        Return total symbols across all watchlists.
        """

        return sum(

            len(watchlist.items)

            for watchlist

            in self._watchlists.values()

        )

    # ==========================================================
    # SYMBOL UTILITIES
    # ==========================================================

    def symbols(
        self,
        watchlist_name: str = DEFAULT_NAME,
    ) -> List[str]:
        """
        Return symbol list.
        """

        watchlist = self.watchlist(

            watchlist_name,

        )

        if watchlist is None:

            return []

        return [

            item.symbol

            for item

            in watchlist.items

        ]

    def instrument_keys(
        self,
        watchlist_name: str = DEFAULT_NAME,
    ) -> List[str]:
        """
        Return instrument key list.
        """

        watchlist = self.watchlist(

            watchlist_name,

        )

        if watchlist is None:

            return []

        return [

            item.instrument_key

            for item

            in watchlist.items

        ]

    def contains_symbol(
        self,
        watchlist_name: str,
        symbol: str,
    ) -> bool:
        """
        Check whether a symbol exists.
        """

        return (

            self.find_symbol(

                watchlist_name,

                symbol,

            )

            is not None

        )

    # ==========================================================
    # SERVICE INFORMATION
    # ==========================================================

    def info(self) -> Dict[str, Any]:
        """
        Return service information.
        """

        return {

            "service":
                self.__class__.__name__,

            "version":
                self.VERSION,

            "watchlists":
                self.watchlist_count(),

            "symbols":
                self.total_symbols(),

            "uptime":
                str(self.uptime),

        }

    # ==========================================================
    # FACTORY
    # ==========================================================

    @classmethod
    def create(
        cls,
        data_service: DataService,
        alert_service: AlertService,
    ) -> "WatchlistService":
        """
        Factory constructor.
        """

        return cls(

            data_service=data_service,

            alert_service=alert_service,

        )


# ==========================================================
# MODULE HELPERS
# ==========================================================

def create_watchlist_service(
    data_service: DataService,
    alert_service: AlertService,
) -> WatchlistService:
    """
    Convenience factory.
    """

    return WatchlistService.create(

        data_service=data_service,

        alert_service=alert_service,

    )


def build_watchlist_service(
    data_service: DataService,
    alert_service: AlertService,
) -> WatchlistService:
    """
    Alternate factory helper.
    """

    return WatchlistService(

        data_service=data_service,

        alert_service=alert_service,

    )
# ==========================================================
# MODULE EXPORTS
# ==========================================================

__all__ = [

    # Enums
    "WatchlistType",

    # Models
    "WatchlistItem",
    "Watchlist",
    "WatchlistStatistics",

    # Service
    "WatchlistService",

    # Factory Helpers
    "create_watchlist_service",
    "build_watchlist_service",

]

# ==========================================================
# END OF FILE
# ==========================================================

# ==========================
# END OF FILE
# ==========================