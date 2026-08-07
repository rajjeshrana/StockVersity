"""
=========================================================
StockVersity Scanner Pro
Powered by AI
Version : 4.0

File : ui/scanner_controller.py
=========================================================
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from PySide6.QtCore import QObject, Signal, Slot, QTimer

from ui.theme import current_theme


class ScannerController(QObject):
    """
    Controls every scanner in the application.

    Responsibilities
    ----------------
    • Intraday Scanner
    • Swing Scanner
    • Positional Scanner
    • Scanner scheduling
    • Result routing
    • Progress updates
    • Backend communication
    """

    scannerStarted = Signal(str)
    scannerFinished = Signal(str)
    scannerFailed = Signal(str)

    progressChanged = Signal(int)

    resultsUpdated = Signal(list)

    statusChanged = Signal(str)

    profileChanged = Signal(str)

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

        self.current_profile = "Intraday"

        self.current_results: List[Dict] = []

        self.scanner_running = False

        self.last_scan: Optional[datetime] = None

        self._initialize()

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def _initialize(self):

        self._discover_components()

        self._create_timers()

        self._connect_signals()

    # =====================================================
    # DISCOVER UI
    # =====================================================

    def _discover_components(self):

        self.tables = {}

        self.cards = {}

        if self.dashboard is None:
            return

        if hasattr(
            self.dashboard,
            "findChildren"
        ):

            for widget in self.dashboard.findChildren(QObject):

                object_name = widget.objectName()

                if not object_name:
                    continue

                if "table" in object_name.lower():

                    self.tables[
                        object_name
                    ] = widget

                elif "card" in object_name.lower():

                    self.cards[
                        object_name
                    ] = widget

    # =====================================================
    # TIMERS
    # =====================================================

    def _create_timers(self):

        self.auto_scan_timer = QTimer(self)

        self.auto_scan_timer.timeout.connect(

            self.execute_current_profile

        )

    # =====================================================
    # SIGNALS
    # =====================================================

    def _connect_signals(self):

        pass

    # =====================================================
    # PROFILE
    # =====================================================

    def set_profile(
        self,
        profile: str
    ):

        profile = profile.title()

        valid = [

            "Intraday",

            "Swing",

            "Positional"

        ]

        if profile not in valid:

            raise ValueError(

                f"Unknown profile : {profile}"

            )

        self.current_profile = profile

        self.profileChanged.emit(profile)

        self.statusChanged.emit(

            f"{profile} Scanner Selected"

        )

    def profile(self):

        return self.current_profile

    # =====================================================
    # START
    # =====================================================

    def start(self):

        if self.scanner_running:
            return

        self.scanner_running = True

        self.scannerStarted.emit(

            self.current_profile

        )

    # =====================================================
    # STOP
    # =====================================================

    def stop(self):

        self.scanner_running = False

    # =====================================================
    # EXECUTE PROFILE
    # =====================================================

    def execute_current_profile(self):

        if self.current_profile == "Intraday":

            self.run_intraday()

        elif self.current_profile == "Swing":

            self.run_swing()

        else:

            self.run_positional()

    # =====================================================
    # INTRADAY
    # =====================================================

    def run_intraday(self):

        self.statusChanged.emit(

            "Running Intraday Scanner..."

        )

        self.start()

        self.current_results = self.backend.run_intraday()

        self._scan_completed()

    # =====================================================
    # SWING
    # =====================================================

    def run_swing(self):

        self.statusChanged.emit(

            "Running Swing Scanner..."

        )

        self.start()

        self.current_results = self.backend.run_swing()

        self._scan_completed()

    # =====================================================
    # POSITIONAL
    # =====================================================

    def run_positional(self):

        self.statusChanged.emit(

            "Running Positional Scanner..."

        )

        self.start()

        self.current_results = self.backend.run_positional()

        self._scan_completed()

    # =====================================================
    # SCAN COMPLETE
    # =====================================================

    def _scan_completed(self):

        self.last_scan = datetime.now()

        self.scanner_running = False

        self.resultsUpdated.emit(

            self.current_results

        )

        self.scannerFinished.emit(

            self.current_profile

        )

        self.update_statistics()
            # =====================================================
    # STATISTICS
    # =====================================================

    def update_statistics(self):

        total = len(self.current_results)

        buy = 0
        sell = 0
        neutral = 0

        for stock in self.current_results:

            signal = str(
                stock.get(
                    "signal",
                    ""
                )
            ).upper()

            if signal == "BUY":

                buy += 1

            elif signal == "SELL":

                sell += 1

            else:

                neutral += 1

        statistics = {

            "profile": self.current_profile,

            "total": total,

            "buy": buy,

            "sell": sell,

            "neutral": neutral,

            "last_scan": self.last_scan,

        }

        self.statisticsUpdated.emit(

            statistics

        )

        self.update_cards(

            statistics

        )

        self.update_tables()

    # =====================================================
    # RESULT FILTERING
    # =====================================================

    def filter_results(

        self,

        minimum_score=0,

        signal=None

    ):

        filtered = []

        for stock in self.current_results:

            score = stock.get(

                "score",

                0

            )

            if score < minimum_score:

                continue

            if signal:

                if str(

                    stock.get(

                        "signal",

                        ""

                    )

                ).upper() != signal.upper():

                    continue

            filtered.append(stock)

        return filtered

    # =====================================================
    # SEARCH
    # =====================================================

    def search(

        self,

        keyword: str

    ):

        keyword = keyword.upper()

        results = []

        for stock in self.current_results:

            symbol = str(

                stock.get(

                    "symbol",

                    ""

                )

            ).upper()

            if keyword in symbol:

                results.append(stock)

                continue

            company = str(

                stock.get(

                    "company",

                    ""

                )

            ).upper()

            if keyword in company:

                results.append(stock)

        return results

    # =====================================================
    # SORTING
    # =====================================================

    def sort_results(

        self,

        field="score",

        reverse=True

    ):

        self.current_results.sort(

            key=lambda x: x.get(

                field,

                0

            ),

            reverse=reverse

        )

        self.resultsUpdated.emit(

            self.current_results

        )

    # =====================================================
    # UPDATE CARDS
    # =====================================================

    def update_cards(

        self,

        statistics

    ):

        mapping = {

            "buy_card":

                statistics["buy"],

            "sell_card":

                statistics["sell"],

            "neutral_card":

                statistics["neutral"],

            "total_card":

                statistics["total"],

        }

        for name, value in mapping.items():

            if name in self.cards:

                card = self.cards[name]

                if hasattr(

                    card,

                    "set_value"

                ):

                    card.set_value(

                        str(value)

                    )

    # =====================================================
    # UPDATE TABLE
    # =====================================================

    def update_tables(self):

        if "scanner_table" not in self.tables:

            return

        table = self.tables[

            "scanner_table"

        ]

        if hasattr(

            table,

            "clear_rows"

        ):

            table.clear_rows()

        for stock in self.current_results:

            row = [

                stock.get(

                    "rank",

                    ""

                ),

                stock.get(

                    "symbol",

                    ""

                ),

                stock.get(

                    "signal",

                    ""

                ),

                stock.get(

                    "score",

                    ""

                ),

                stock.get(

                    "rr",

                    ""

                ),

                stock.get(

                    "pattern",

                    ""

                ),

                stock.get(

                    "price",

                    ""

                ),

            ]

            if hasattr(

                table,

                "append_row"

            ):

                table.append_row(

                    row

                )

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
    # AUTO SCAN
    # =====================================================

    def enable_auto_scan(

        self,

        seconds=60

    ):

        self.auto_scan_timer.start(

            seconds * 1000

        )

    def disable_auto_scan(self):

        self.auto_scan_timer.stop()

    def auto_scan_enabled(self):

        return self.auto_scan_timer.isActive()

    # =====================================================
    # LAST SCAN
    # =====================================================

    def last_scan_text(self):

        if self.last_scan is None:

            return "Never"

        return self.last_scan.strftime(

            "%d-%m-%Y %H:%M:%S"

        )
        # =====================================================
    # BACKGROUND SCANNER
    # =====================================================

    def enable_background_scanner(self):

        self._background_enabled = True

    def disable_background_scanner(self):

        self._background_enabled = False

    def background_enabled(self):

        return getattr(

            self,

            "_background_enabled",

            False

        )

    # =====================================================
    # ASYNC EXECUTION
    # =====================================================

    def execute_async(self):

        if self.scanner_running:

            return

        from PySide6.QtCore import QThread

        self._worker_thread = QThread()

        self._worker = ScannerWorker(

            self.backend,

            self.current_profile

        )

        self._worker.moveToThread(

            self._worker_thread

        )

        self._worker_thread.started.connect(

            self._worker.run

        )

        self._worker.finished.connect(

            self._scan_completed_async

        )

        self._worker.progress.connect(

            self._progress_changed

        )

        self._worker.error.connect(

            self._scan_failed

        )

        self._worker.finished.connect(

            self._worker_thread.quit

        )

        self._worker_thread.finished.connect(

            self._worker.deleteLater

        )

        self._worker_thread.finished.connect(

            self._worker_thread.deleteLater

        )

        self.start()

        self.begin_timing()

        self._worker_thread.start()

    # =====================================================
    # ASYNC COMPLETE
    # =====================================================

    @Slot(list)
    def _scan_completed_async(

        self,

        results

    ):

        self.current_results = results

        self.last_scan = datetime.now()

        self.scanner_running = False

        self._last_duration = self.end_timing()

        self.resultsUpdated.emit(

            self.current_results

        )

        self.update_statistics()

        self.scannerFinished.emit(

            self.current_profile

        )

        self.statusChanged.emit(

            f"{self.current_profile} scan completed "

            f"in {self._last_duration:.2f}s"

        )

        self.execute_queue()

    # =====================================================
    # SCAN FAILED
    # =====================================================

    @Slot(str)
    def _scan_failed(

        self,

        message

    ):

        self.scanner_running = False

        self.scannerFailed.emit(

            message

        )

        self.statusChanged.emit(

            f"Scanner Error : {message}"

        )

        if getattr(

            self,

            "_auto_retry",

            False

        ):

            self.retry_scan()

    # =====================================================
    # PROGRESS
    # =====================================================

    @Slot(int)
    def _progress_changed(

        self,

        value

    ):

        self.progressChanged.emit(

            value

        )

    # =====================================================
    # CANCEL
    # =====================================================

    def cancel_scan(self):

        if hasattr(

            self,

            "_worker"

        ):

            self._worker.cancel()

    # =====================================================
    # RETRY
    # =====================================================

    def enable_auto_retry(

        self,

        enabled=True

    ):

        self._auto_retry = enabled

    def retry_scan(self):

        self.statusChanged.emit(

            "Retrying scan..."

        )

        self.execute_async()

    # =====================================================
    # TASK QUEUE
    # =====================================================

    def queue_scan(self):

        self._queued_scan = True

    def execute_queue(self):

        if getattr(

            self,

            "_queued_scan",

            False

        ):

            self._queued_scan = False

            self.execute_async()

    # =====================================================
    # PERFORMANCE
    # =====================================================

    def begin_timing(self):

        from time import perf_counter

        self._timer = perf_counter()

    def end_timing(self):

        from time import perf_counter

        if not hasattr(

            self,

            "_timer"

        ):

            return 0.0

        return perf_counter() - self._timer

    def last_scan_duration(self):

        return getattr(

            self,

            "_last_duration",

            0.0

        )

    # =====================================================
    # LOGGING
    # =====================================================

    def log(

        self,

        message

    ):

        print(

            f"[Scanner] "

            f"{datetime.now()} "

            f"{message}"

        )


# =====================================================
# BACKGROUND WORKER
# =====================================================

class ScannerWorker(QObject):

    finished = Signal(list)

    progress = Signal(int)

    error = Signal(str)

    def __init__(

        self,

        backend,

        profile

    ):

        super().__init__()

        self.backend = backend

        self.profile = profile

        self._cancel = False

    @Slot()
    def run(self):

        try:

            self.progress.emit(5)

            if self._cancel:

                return

            if self.profile == "Intraday":

                results = self.backend.run_intraday(

                    progress_callback=self.progress.emit

                )

            elif self.profile == "Swing":

                results = self.backend.run_swing(

                    progress_callback=self.progress.emit

                )

            else:

                results = self.backend.run_positional(

                    progress_callback=self.progress.emit

                )

            if self._cancel:

                return

            self.progress.emit(100)

            self.finished.emit(results)

        except Exception as exc:

            self.error.emit(

                str(exc)

            )

    def cancel(self):

        self._cancel = True
            # =====================================================
    # LIVE MARKET DATA
    # =====================================================

    def update_market_data(
        self,
        market_data: Dict
    ):

        self._market_data = market_data

        mapping = {

            "nifty_card": market_data.get("nifty", "--"),

            "banknifty_card": market_data.get("banknifty", "--"),

            "vix_card": market_data.get("vix", "--"),

            "advance_decline_card": market_data.get(
                "advance_decline",
                "--"
            ),

        }

        for card_name, value in mapping.items():

            if card_name not in self.cards:
                continue

            card = self.cards[card_name]

            if hasattr(card, "set_value"):

                card.set_value(str(value))

    # =====================================================
    # MARKET STATUS
    # =====================================================

    def update_market_status(
        self,
        status: str
    ):

        self.market_status = status

        self.statusChanged.emit(

            f"Market : {status}"

        )

    # =====================================================
    # SECTOR ROTATION
    # =====================================================

    def update_sector_rotation(
        self,
        sectors: List[Dict]
    ):

        self._sector_data = sectors

        if not sectors:
            return

        leader = max(

            sectors,

            key=lambda x: x.get(

                "change",

                0

            )

        )

        laggard = min(

            sectors,

            key=lambda x: x.get(

                "change",

                0

            )

        )

        if "sector_leader_card" in self.cards:

            self.cards[

                "sector_leader_card"

            ].set_value(

                leader.get(

                    "sector",

                    "-"

                )

            )

        if "sector_laggard_card" in self.cards:

            self.cards[

                "sector_laggard_card"

            ].set_value(

                laggard.get(

                    "sector",

                    "-"

                )

            )

    # =====================================================
    # WATCHLIST
    # =====================================================

    def update_watchlist(
        self,
        stocks: List[Dict]
    ):

        self.watchlist = stocks

        if "watchlist_table" not in self.tables:

            return

        table = self.tables["watchlist_table"]

        if hasattr(table, "clear_rows"):

            table.clear_rows()

        for stock in stocks:

            row = [

                stock.get(

                    "symbol",

                    ""

                ),

                stock.get(

                    "price",

                    ""

                ),

                stock.get(

                    "change",

                    ""

                ),

                stock.get(

                    "volume",

                    ""

                ),

            ]

            if hasattr(

                table,

                "append_row"

            ):

                table.append_row(row)

    # =====================================================
    # ALERTS
    # =====================================================

    def add_alert(
        self,
        symbol,
        message,
        level="INFO"
    ):

        if not hasattr(

            self,

            "_alerts"

        ):

            self._alerts = []

        alert = {

            "time": datetime.now(),

            "symbol": symbol,

            "message": message,

            "level": level.upper()

        }

        self._alerts.append(alert)

        self.statusChanged.emit(

            f"[{level.upper()}] "

            f"{symbol} : {message}"

        )

    def alerts(self):

        return getattr(

            self,

            "_alerts",

            []

        )

    # =====================================================
    # ALERT RULES
    # =====================================================

    def evaluate_alert_rules(self):

        for stock in self.current_results:

            signal = str(

                stock.get(

                    "signal",

                    ""

                )

            ).upper()

            score = stock.get(

                "score",

                0

            )

            if signal == "BUY" and score >= 90:

                self.add_alert(

                    stock.get(

                        "symbol",

                        ""

                    ),

                    "High Conviction BUY",

                    "SUCCESS"

                )

            elif signal == "SELL" and score >= 90:

                self.add_alert(

                    stock.get(

                        "symbol",

                        ""

                    ),

                    "High Conviction SELL",

                    "WARNING"

                )

    # =====================================================
    # DASHBOARD NOTIFICATIONS
    # =====================================================

    def notify_dashboard(
        self,
        message
    ):

        if self.dashboard is None:

            return

        if hasattr(

            self.dashboard,

            "show_notification"

        ):

            self.dashboard.show_notification(

                message

            )

        self.statusChanged.emit(message)

    # =====================================================
    # BACKEND SYNC
    # =====================================================

    def synchronize_backend(self):

        if hasattr(

            self.backend,

            "refresh"

        ):

            self.backend.refresh()

    # =====================================================
    # SCANNER HEALTH
    # =====================================================

    def health_status(self):

        return {

            "profile":

                self.current_profile,

            "running":

                self.scanner_running,

            "results":

                len(self.current_results),

            "last_scan":

                self.last_scan_text(),

            "alerts":

                len(self.alerts()),

            "watchlist":

                len(

                    getattr(

                        self,

                        "watchlist",

                        []

                    )

                ),

            "backend":

                self.backend is not None,

        }

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh(self):

        self.update_statistics()

        self.evaluate_alert_rules()

        self.synchronize_backend()

        self.statusChanged.emit(

            "Scanner refreshed"

        )
            # =====================================================
    # WORKSPACE MANAGEMENT
    # =====================================================

    def save_workspace(self):

        return {

            "profile": self.current_profile,

            "filters": self.filters(),

            "favorites": self.favorites(),

            "auto_scan":

                self.auto_scan_enabled(),

            "last_scan":

                self.last_scan_text(),

        }

    def restore_workspace(

        self,

        workspace: Dict

    ):

        self.set_profile(

            workspace.get(

                "profile",

                "Intraday"

            )

        )

        self.set_filters(

            workspace.get(

                "filters",

                {}

            )

        )

        self.restore_favorites(

            workspace.get(

                "favorites",

                []

            )

        )

    # =====================================================
    # SCANNER PRESETS
    # =====================================================

    def load_preset(

        self,

        preset: str

    ):

        preset = preset.upper()

        presets = {

            "ORB": {

                "volume": 2,

                "adx": 20,

                "breakout": True,

            },

            "SWING": {

                "timeframe": "1D",

                "ema": 21,

                "volume": 1.5,

            },

            "VCP": {

                "contraction": True,

                "volume_dryup": True,

            },

            "MOMENTUM": {

                "rvol": 2,

                "price_change": 3,

            }

        }

        if preset in presets:

            self.set_filters(

                presets[preset]

            )

            self.statusChanged.emit(

                f"{preset} preset loaded"

            )

    # =====================================================
    # FILTERS
    # =====================================================

    def set_filters(

        self,

        filters: Dict

    ):

        self._filters = filters.copy()

    def update_filter(

        self,

        key,

        value

    ):

        if not hasattr(

            self,

            "_filters"

        ):

            self._filters = {}

        self._filters[key] = value

    def filters(self):

        return getattr(

            self,

            "_filters",

            {}

        )

    def clear_filters(self):

        self._filters = {}

    # =====================================================
    # FAVORITES
    # =====================================================

    def add_favorite(

        self,

        symbol: str

    ):

        if not hasattr(

            self,

            "_favorites"

        ):

            self._favorites = []

        if symbol not in self._favorites:

            self._favorites.append(symbol)

    def remove_favorite(

        self,

        symbol: str

    ):

        if hasattr(

            self,

            "_favorites"

        ):

            try:

                self._favorites.remove(symbol)

            except ValueError:

                pass

    def favorites(self):

        return getattr(

            self,

            "_favorites",

            []

        )

    def restore_favorites(

        self,

        favorites: List[str]

    ):

        self._favorites = list(

            favorites

        )

    # =====================================================
    # EXPORT CONFIGURATION
    # =====================================================

    def export_configuration(self):

        return {

            "profile":

                self.current_profile,

            "filters":

                self.filters(),

            "favorites":

                self.favorites(),

        }

    # =====================================================
    # IMPORT CONFIGURATION
    # =====================================================

    def import_configuration(

        self,

        config: Dict

    ):

        self.set_profile(

            config.get(

                "profile",

                "Intraday"

            )

        )

        self.set_filters(

            config.get(

                "filters",

                {}

            )

        )

        self.restore_favorites(

            config.get(

                "favorites",

                []

            )

        )

    # =====================================================
    # SESSION STATISTICS
    # =====================================================

    def session_statistics(self):

        return {

            "profile":

                self.current_profile,

            "results":

                len(

                    self.current_results

                ),

            "buy_signals":

                len(

                    self.filter_results(

                        signal="BUY"

                    )

                ),

            "sell_signals":

                len(

                    self.filter_results(

                        signal="SELL"

                    )

                ),

            "last_scan":

                self.last_scan_text(),

        }

    # =====================================================
    # PERFORMANCE
    # =====================================================

    def performance_metrics(self):

        return {

            "scan_duration":

                self.last_scan_duration(),

            "scanner_running":

                self.scanner_running,

            "auto_scan":

                self.auto_scan_enabled(),

            "result_count":

                len(

                    self.current_results

                ),

            "favorites":

                len(

                    self.favorites()

                ),

        }

    # =====================================================
    # DIAGNOSTICS
    # =====================================================

    def diagnostics(self):

        return {

            "profile":

                self.current_profile,

            "tables":

                len(

                    self.tables

                ),

            "cards":

                len(

                    self.cards

                ),

            "backend":

                self.backend is not None,

            "dashboard":

                self.dashboard is not None,

            "running":

                self.scanner_running,

            "filters":

                len(

                    self.filters()

                ),

        }
        # =====================================================
    # MULTI SCANNER REGISTRY
    # =====================================================

    def register_scanner(
        self,
        name: str,
        scanner
    ):

        if not hasattr(self, "_scanners"):
            self._scanners = {}

        self._scanners[name] = scanner

    def unregister_scanner(
        self,
        name: str
    ):

        if hasattr(self, "_scanners"):
            self._scanners.pop(name, None)

    def scanners(self):

        return getattr(
            self,
            "_scanners",
            {}
        )

    # =====================================================
    # RUN SPECIFIC SCANNER
    # =====================================================

    def execute_scanner(
        self,
        name: str
    ):

        scanners = self.scanners()

        if name not in scanners:

            return []

        scanner = scanners[name]

        self.statusChanged.emit(

            f"Executing {name} scanner..."

        )

        results = scanner.run()

        return results

    # =====================================================
    # EXECUTE ALL SCANNERS
    # =====================================================

    def execute_all_scanners(self):

        combined_results = []

        for name, scanner in self.ordered_scanners():

            try:

                results = scanner.run()

                combined_results.extend(results)

            except Exception as exc:

                self.log(

                    f"{name} failed : {exc}"

                )

        self.current_results = combined_results

        self.resultsUpdated.emit(

            combined_results

        )

        self.update_statistics()

    # =====================================================
    # PRIORITY MANAGEMENT
    # =====================================================

    def set_priorities(
        self,
        priorities: Dict[str, int]
    ):

        self._priorities = priorities.copy()

    def priorities(self):

        return getattr(
            self,
            "_priorities",
            {}
        )

    def ordered_scanners(self):

        scanners = list(
            self.scanners().items()
        )

        priorities = self.priorities()

        scanners.sort(

            key=lambda item: priorities.get(
                item[0],
                999
            )

        )

        return scanners

    # =====================================================
    # QUEUE MANAGEMENT
    # =====================================================

    def queue_profile(
        self,
        profile: str
    ):

        if not hasattr(self, "_scan_queue"):

            self._scan_queue = []

        self._scan_queue.append(profile)

    def execute_queue(self):

        if not hasattr(self, "_scan_queue"):

            return

        if not self._scan_queue:

            return

        profile = self._scan_queue.pop(0)

        self.set_profile(profile)

        self.execute_async()

    def clear_queue(self):

        self._scan_queue = []

    def queued_profiles(self):

        return getattr(
            self,
            "_scan_queue",
            []
        )

    # =====================================================
    # RULE ENGINE
    # =====================================================

    def register_rule(
        self,
        name: str,
        callback
    ):

        if not hasattr(self, "_rules"):

            self._rules = {}

        self._rules[name] = callback

    def unregister_rule(
        self,
        name: str
    ):

        if hasattr(self, "_rules"):

            self._rules.pop(name, None)

    def evaluate_rules(self):

        if not hasattr(self, "_rules"):

            return

        for stock in self.current_results:

            for rule_name, callback in self._rules.items():

                try:

                    if callback(stock):

                        self.add_alert(

                            stock.get(

                                "symbol",

                                ""

                            ),

                            rule_name,

                            "INFO"

                        )

                except Exception as exc:

                    self.log(

                        f"Rule '{rule_name}' failed : {exc}"

                    )

    # =====================================================
    # EVENT BUS
    # =====================================================

    def register_event(
        self,
        event_name: str,
        callback
    ):

        if not hasattr(self, "_events"):

            self._events = {}

        self._events.setdefault(

            event_name,

            []

        ).append(callback)

    def emit_event(
        self,
        event_name: str,
        *args,
        **kwargs
    ):

        if not hasattr(self, "_events"):

            return

        for callback in self._events.get(

            event_name,

            []

        ):

            try:

                callback(*args, **kwargs)

            except Exception as exc:

                self.log(

                    f"Event '{event_name}' error : {exc}"

                )

    # =====================================================
    # RISK MANAGEMENT
    # =====================================================

    def update_risk_metrics(
        self,
        metrics: Dict
    ):

        self._risk_metrics = metrics

    def risk_metrics(self):

        return getattr(

            self,

            "_risk_metrics",

            {}

        )

    # =====================================================
    # CONTROLLER MONITOR
    # =====================================================

    def controller_monitor(self):

        return {

            "profile":
                self.current_profile,

            "registered_scanners":
                len(self.scanners()),

            "queue":
                len(self.queued_profiles()),

            "rules":
                len(getattr(self, "_rules", {})),

            "events":
                len(getattr(self, "_events", {})),

            "results":
                len(self.current_results),

            "running":
                self.scanner_running,

            "duration":
                self.last_scan_duration(),

        }

    # =====================================================
    # BACKEND COORDINATION
    # =====================================================

    def synchronize_backend_modules(self):

        if hasattr(

            self.backend,

            "synchronize"

        ):

            self.backend.synchronize()

        elif hasattr(

            self.backend,

            "refresh"

        ):

            self.backend.refresh()

        self.statusChanged.emit(

            "Backend synchronization completed"

        )
            # =====================================================
    # WORKSPACE
    # =====================================================

    def save_workspace_state(self):

        return {

            "profile": self.current_profile,

            "filters": self.filters(),

            "favorites": self.favorites(),

            "queue": list(

                self.queued_profiles()

            ),

            "risk_metrics":

                self.risk_metrics(),

            "last_scan":

                self.last_scan_text(),

        }

    def restore_workspace_state(

        self,

        state: Dict

    ):

        self.set_profile(

            state.get(

                "profile",

                "Intraday"

            )

        )

        self.set_filters(

            state.get(

                "filters",

                {}

            )

        )

        self.restore_favorites(

            state.get(

                "favorites",

                []

            )

        )

        self._scan_queue = list(

            state.get(

                "queue",

                []

            )

        )

        self.update_risk_metrics(

            state.get(

                "risk_metrics",

                {}

            )

        )

    # =====================================================
    # SESSION
    # =====================================================

    def start_session(self):

        self._session_start = datetime.now()

        self.statusChanged.emit(

            "Scanner session started"

        )

    def stop_session(self):

        self._session_end = datetime.now()

        self.statusChanged.emit(

            "Scanner session stopped"

        )

    def session_duration(self):

        if not hasattr(

            self,

            "_session_start"

        ):

            return 0

        end_time = getattr(

            self,

            "_session_end",

            datetime.now()

        )

        return int(

            (

                end_time

                - self._session_start

            ).total_seconds()

        )

    # =====================================================
    # THEME
    # =====================================================

    def synchronize_theme(self):

        theme = current_theme()

        for card in self.cards.values():

            if hasattr(

                card,

                "refresh_theme"

            ):

                card.refresh_theme(theme)

        for table in self.tables.values():

            if hasattr(

                table,

                "refresh_theme"

            ):

                table.refresh_theme(theme)

        self.statusChanged.emit(

            "Theme synchronized"

        )

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(self):

        return {

            "backend":

                self.backend is not None,

            "dashboard":

                self.dashboard is not None,

            "scanner_running":

                self.scanner_running,

            "cards":

                len(self.cards),

            "tables":

                len(self.tables),

            "registered_scanners":

                len(self.scanners()),

            "queue":

                len(self.queued_profiles()),

            "auto_scan":

                self.auto_scan_enabled(),

        }

    # =====================================================
    # ERROR RECOVERY
    # =====================================================

    def recover(self):

        try:

            self.stop()

            self.start()

            self.statusChanged.emit(

                "Recovery completed"

            )

        except Exception as exc:

            self.scannerFailed.emit(

                str(exc)

            )

    # =====================================================
    # CLEANUP
    # =====================================================

    def cleanup(self):

        self.disable_auto_scan()

        self.current_results.clear()

        self.clear_queue()

        self.clear_filters()

        if hasattr(

            self,

            "_alerts"

        ):

            self._alerts.clear()

        self.scanner_running = False

    # =====================================================
    # MODULE REGISTRY
    # =====================================================

    def register_module(

        self,

        name: str,

        module

    ):

        if not hasattr(

            self,

            "_modules"

        ):

            self._modules = {}

        self._modules[name] = module

    def unregister_module(

        self,

        name: str

    ):

        if hasattr(

            self,

            "_modules"

        ):

            self._modules.pop(

                name,

                None

            )

    def module(

        self,

        name: str

    ):

        return getattr(

            self,

            "_modules",

            {}

        ).get(name)

    def modules(self):

        return getattr(

            self,

            "_modules",

            {}

        )

    # =====================================================
    # INITIALIZE MODULES
    # =====================================================

    def initialize_modules(self):

        for module in self.modules().values():

            if hasattr(

                module,

                "initialize"

            ):

                module.initialize()

    # =====================================================
    # SERIALIZATION
    # =====================================================

    def serialize(self):

        return {

            "workspace":

                self.save_workspace_state(),

            "configuration":

                self.export_configuration(),

            "health":

                self.health_check(),

            "statistics":

                self.session_statistics(),

            "performance":

                self.performance_metrics(),

        }

    # =====================================================
    # CONTROLLER SUMMARY
    # =====================================================

    def summary(self):

        return {

            "profile":

                self.current_profile,

            "results":

                len(

                    self.current_results

                ),

            "favorites":

                len(

                    self.favorites()

                ),

            "filters":

                len(

                    self.filters()

                ),

            "registered_scanners":

                len(

                    self.scanners()

                ),

            "modules":

                len(

                    self.modules()

                ),

            "queue":

                len(

                    self.queued_profiles()

                ),

            "health":

                self.health_check(),

        }
        # =====================================================
    # INITIALIZE
    # =====================================================

    def initialize(self):

        self.log(

            "Initializing Scanner Controller"

        )

        self._discover_components()

        self._create_timers()

        self._connect_signals()

        self.initialize_modules()

        self.update_statistics()

        self.statusChanged.emit(

            "Scanner Controller initialized"

        )

    # =====================================================
    # STARTUP
    # =====================================================

    def startup(self):

        self.log(

            "Scanner Controller startup"

        )

        self.start_session()

        self.initialize()

        self.emit_event(

            "startup"

        )

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(self):

        self.log(

            "Scanner Controller shutdown"

        )

        self.emit_event(

            "shutdown"

        )

        self.stop_session()

        self.cleanup()

        self.statusChanged.emit(

            "Scanner Controller stopped"

        )

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        self.log(

            "Resetting Scanner Controller"

        )

        self.stop()

        self.current_results.clear()

        self.clear_filters()

        self.clear_queue()

        self._favorites = []

        self._alerts = []

        self._modules = {}

        self._rules = {}

        self._events = {}

        self.statisticsUpdated.emit(

            {

                "profile": self.current_profile,

                "total": 0,

                "buy": 0,

                "sell": 0,

                "neutral": 0,

                "last_scan": None,

            }

        )

        self.statusChanged.emit(

            "Scanner Controller reset completed"

        )

    # =====================================================
    # RELOAD
    # =====================================================

    def reload(self):

        self.shutdown()

        self.startup()

    # =====================================================
    # BUILD INFORMATION
    # =====================================================

    @staticmethod
    def version():

        return "4.0"

    @staticmethod
    def application():

        return "StockVersity Scanner Pro"

    @staticmethod
    def powered_by():

        return "Powered by AI"

    def build_information(self):

        from PySide6.QtCore import qVersion
        import sys

        return {

            "application":

                self.application(),

            "version":

                self.version(),

            "powered_by":

                self.powered_by(),

            "python":

                sys.version.split()[0],

            "qt":

                qVersion(),

            "controller":

                self.__class__.__name__,

        }

    # =====================================================
    # STRING REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (

            f"<ScannerController "

            f"profile={self.current_profile} "

            f"results={len(self.current_results)} "

            f"running={self.scanner_running}>"

        )

    def __str__(self):

        return self.__repr__()


# =====================================================
# FACTORY
# =====================================================

def create_scanner_controller(

    backend,

    dashboard=None,

    parent=None

):

    controller = ScannerController(

        backend=backend,

        dashboard=dashboard,

        parent=parent,

    )

    controller.initialize()

    return controller


# =====================================================
# MODULE EXPORTS
# =====================================================

__all__ = [

    "ScannerController",

    "ScannerWorker",

    "create_scanner_controller",

]


# =====================================================
# END OF FILE
#
# StockVersity Scanner Pro
# Powered by AI
# Version 4.0
#
# File:
# ui/scanner_controller.py
# =====================================================