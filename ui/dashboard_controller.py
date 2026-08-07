"""
=========================================================
StockVersity Scanner Pro
Dashboard Controller
Version : 4.0
Powered by AI
=========================================================
"""

from __future__ import annotations

from typing import Dict, List, Optional
from datetime import datetime

from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
    QTimer,
)

from ui.theme import current_theme


# =========================================================
# DASHBOARD CONTROLLER
# =========================================================

class DashboardController(QObject):

    # -----------------------------------------------------
    # Signals
    # -----------------------------------------------------

    dashboardUpdated = Signal()
    marketStatusChanged = Signal(bool)
    scannerStarted = Signal()
    scannerFinished = Signal()
    scannerFailed = Signal(str)

    opportunitiesUpdated = Signal(list)
    sectorUpdated = Signal(dict)
    statusMessage = Signal(str)

    # -----------------------------------------------------

    def __init__(

        self,

        dashboard,

        backend,

        parent=None

    ):

        super().__init__(parent)

        self.dashboard = dashboard
        self.backend = backend

        self.market_open = False
        self.scanner_running = False

        self.last_scan = None
        self.current_results = []

        self.cards = {}
        self.tables = {}

        self.refresh_timer = QTimer(self)
        self.market_timer = QTimer(self)

        self._initialize()

    # =====================================================
    # INITIALIZE
    # =====================================================

    def _initialize(self):

        self._discover_widgets()

        self._configure_timers()

        self._connect_signals()

        self.statusMessage.emit(

            "Dashboard initialized"

        )

    # =====================================================
    # DISCOVER UI
    # =====================================================

    def _discover_widgets(self):

        if hasattr(

            self.dashboard,

            "cards"

        ):

            self.cards = self.dashboard.cards

        if hasattr(

            self.dashboard,

            "tables"

        ):

            self.tables = self.dashboard.tables

    # =====================================================
    # TIMERS
    # =====================================================

    def _configure_timers(self):

        self.refresh_timer.setInterval(

            15000

        )

        self.market_timer.setInterval(

            1000

        )

    # =====================================================
    # SIGNALS
    # =====================================================

    def _connect_signals(self):

        self.refresh_timer.timeout.connect(

            self.run_scan

        )

        self.market_timer.timeout.connect(

            self.check_market_status

        )

    # =====================================================
    # START
    # =====================================================

    def start(self):

        self.market_timer.start()

        self.refresh_timer.start()

        self.statusMessage.emit(

            "Dashboard started"

        )

    # =====================================================
    # STOP
    # =====================================================

    def stop(self):

        self.market_timer.stop()

        self.refresh_timer.stop()

        self.statusMessage.emit(

            "Dashboard stopped"

        )

    # =====================================================
    # MARKET STATUS
    # =====================================================

    @Slot()

    def check_market_status(self):

        now = datetime.now()

        current = now.hour * 60 + now.minute

        market = (

            9 * 60 + 15

        ) <= current <= (

            15 * 60 + 30

        )

        if market != self.market_open:

            self.market_open = market

            self.marketStatusChanged.emit(

                market

            )

            if market:

                self.statusMessage.emit(

                    "Market Open"

                )

            else:

                self.statusMessage.emit(

                    "Market Closed"

                )

    # =====================================================
    # RUN SCANNER
    # =====================================================

    @Slot()

    def run_scan(self):

        if self.scanner_running:

            return

        self.scanner_running = True

        self.scannerStarted.emit()

        self.statusMessage.emit(

            "Running scanner..."

        )

        try:

            results = self.backend.run_scan()

            self.current_results = results

            self.last_scan = datetime.now()

            self._update_dashboard()

            self.scannerFinished.emit()

        except Exception as e:

            self.scannerFailed.emit(

                str(e)

            )

        finally:

            self.scanner_running = False

    # =====================================================
    # UPDATE DASHBOARD
    # =====================================================

    def _update_dashboard(self):

        self.update_cards()

        self.update_tables()

        self.dashboardUpdated.emit()
            # =====================================================
    # UPDATE CARDS
    # =====================================================

    def update_cards(self):

        total = len(self.current_results)

        if "opportunities" in self.cards:

            self.cards["opportunities"].set_value(str(total))

        if "market_status" in self.cards:

            if self.market_open:

                self.cards["market_status"].set_value("OPEN")

                self.cards["market_status"].set_status_color(

                    current_theme().SUCCESS

                )

            else:

                self.cards["market_status"].set_value("CLOSED")

                self.cards["market_status"].set_status_color(

                    current_theme().ERROR

                )

        if "last_scan" in self.cards:

            if self.last_scan:

                self.cards["last_scan"].set_value(

                    self.last_scan.strftime(

                        "%H:%M:%S"

                    )

                )

        if "scanner_status" in self.cards:

            self.cards["scanner_status"].set_value(

                "RUNNING"

                if self.scanner_running

                else "READY"

            )

    # =====================================================
    # UPDATE TABLES
    # =====================================================

    def update_tables(self):

        scanner_table = self.tables.get("scanner")

        if scanner_table is None:

            return

        scanner_table.begin_batch_update()

        scanner_table.clear_rows()

        for stock in self.current_results:

            scanner_table.append_row([

                stock.get("rank", ""),

                stock.get("symbol", ""),

                stock.get("signal", ""),

                stock.get("pattern", ""),

                stock.get("score", ""),

                stock.get("rr", ""),

                stock.get("price", ""),

                stock.get("volume", ""),

            ])

        scanner_table.end_batch_update()

        self.opportunitiesUpdated.emit(

            self.current_results

        )

    # =====================================================
    # UPDATE STATUS BAR
    # =====================================================

    def update_statusbar(

        self,

        message: str

    ):

        if hasattr(

            self.dashboard,

            "statusbar"

        ):

            try:

                self.dashboard.statusbar.set_message(

                    message

                )

            except Exception:

                pass

    # =====================================================
    # LAST SCAN TEXT
    # =====================================================

    def last_scan_text(self):

        if self.last_scan is None:

            return "Never"

        return self.last_scan.strftime(

            "%d-%m-%Y %H:%M:%S"

        )

    # =====================================================
    # LIVE METRICS
    # =====================================================

    def update_live_metrics(self):

        if "total_scans" in self.cards:

            current = getattr(

                self,

                "_scan_counter",

                0

            )

            current += 1

            self._scan_counter = current

            self.cards["total_scans"].set_value(

                str(current)

            )

        if "stocks_found" in self.cards:

            self.cards["stocks_found"].set_value(

                str(len(self.current_results))

            )

    # =====================================================
    # SECTOR SUMMARY
    # =====================================================

    def update_sector_summary(

        self,

        sector_data: Dict

    ):

        self.sectorUpdated.emit(

            sector_data

        )

        if "sector" in self.cards:

            leader = sector_data.get(

                "leader",

                "-"

            )

            self.cards["sector"].set_value(

                leader

            )

    # =====================================================
    # REFRESH DASHBOARD
    # =====================================================

    def refresh_dashboard(self):

        self.update_cards()

        self.update_tables()

        self.update_live_metrics()

        self.update_statusbar(

            f"Last Scan : {self.last_scan_text()}"

        )

        self.dashboardUpdated.emit()

    # =====================================================
    # CLEAR RESULTS
    # =====================================================

    def clear_results(self):

        self.current_results.clear()

        table = self.tables.get("scanner")

        if table:

            table.clear_rows()

        self.refresh_dashboard()

    # =====================================================
    # HELPER
    # =====================================================

    def total_opportunities(self):

        return len(self.current_results)

    def has_results(self):

        return len(self.current_results) > 0

    def scanner_busy(self):

        return self.scanner_running

    # =====================================================
    # CURRENT RESULTS
    # =====================================================

    def results(self):

        return self.current_results
        # =====================================================
    # BACKGROUND SCANNER WORKER
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
    # ASYNC SCAN
    # =====================================================

    def run_scan_async(self):

        if self.scanner_running:

            return

        from PySide6.QtCore import QThread

        self._worker_thread = QThread()

        self._worker = ScannerWorker(self.backend)

        self._worker.moveToThread(

            self._worker_thread

        )

        self._worker_thread.started.connect(

            self._worker.run

        )

        self._worker.finished.connect(

            self._worker_thread.quit

        )

        self._worker.finished.connect(

            self._scan_completed

        )

        self._worker.error.connect(

            self._scan_failed

        )

        self._worker.progress.connect(

            self._scan_progress

        )

        self._worker_thread.finished.connect(

            self._worker.deleteLater

        )

        self._worker_thread.finished.connect(

            self._worker_thread.deleteLater

        )

        self.scanner_running = True

        self.scannerStarted.emit()

        self._worker_thread.start()

    # =====================================================
    # SCAN COMPLETED
    # =====================================================

    @Slot(list)
    def _scan_completed(

        self,

        results

    ):

        self.current_results = results

        self.last_scan = datetime.now()

        self.scanner_running = False

        self.refresh_dashboard()

        self.scannerFinished.emit()

        self.statusMessage.emit(

            f"Scan completed ({len(results)} stocks)"

        )

    # =====================================================
    # SCAN FAILED
    # =====================================================

    @Slot(str)
    def _scan_failed(

        self,

        message

    ):

        self.scanner_running = False

        self.scannerFailed.emit(message)

        self.statusMessage.emit(

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
    def _scan_progress(

        self,

        value

    ):

        if hasattr(

            self.dashboard,

            "progress_bar"

        ):

            self.dashboard.progress_bar.setValue(

                value

            )

    # =====================================================
    # AUTO RETRY
    # =====================================================

    def enable_auto_retry(

        self,

        enabled=True

    ):

        self._auto_retry = enabled

    def retry_scan(self):

        self.statusMessage.emit(

            "Retrying scanner..."

        )

        self.run_scan_async()

    # =====================================================
    # CANCEL SCAN
    # =====================================================

    def cancel_scan(self):

        if hasattr(

            self,

            "_worker"

        ):

            self._worker.cancel()

    # =====================================================
    # TASK QUEUE
    # =====================================================

    def queue_scan(self):

        if not hasattr(

            self,

            "_queued_scan"

        ):

            self._queued_scan = False

        self._queued_scan = True

    def execute_queue(self):

        if getattr(

            self,

            "_queued_scan",

            False

        ):

            self._queued_scan = False

            self.run_scan_async()

    # =====================================================
    # PERFORMANCE TIMER
    # =====================================================

    def begin_timing(self):

        from time import perf_counter

        self._scan_timer = perf_counter()

    def end_timing(self):

        from time import perf_counter

        if not hasattr(

            self,

            "_scan_timer"

        ):

            return 0

        return round(

            perf_counter()

            - self._scan_timer,

            3

        )

    # =====================================================
    # LOGGING
    # =====================================================

    def log_scan(

        self,

        message

    ):

        print(

            f"[Dashboard] {datetime.now()} : {message}"

        )

    # =====================================================
    # LAST DURATION
    # =====================================================

    def last_scan_duration(self):

        return getattr(

            self,

            "_last_duration",

            0

        )


# =========================================================
# BACKGROUND WORKER
# =========================================================

class ScannerWorker(QObject):

    finished = Signal(list)

    progress = Signal(int)

    error = Signal(str)

    def __init__(

        self,

        backend

    ):

        super().__init__()

        self.backend = backend

        self._cancel = False

    @Slot()
    def run(self):

        try:

            self.progress.emit(5)

            if self._cancel:

                return

            results = self.backend.run_scan(

                progress_callback=self.progress.emit

            )

            if self._cancel:

                return

            self.progress.emit(100)

            self.finished.emit(results)

        except Exception as e:

            self.error.emit(

                str(e)

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

        if "nifty" in self.cards:

            self.cards["nifty"].set_value(

                f"{market_data.get('nifty', '--')}"

            )

        if "banknifty" in self.cards:

            self.cards["banknifty"].set_value(

                f"{market_data.get('banknifty', '--')}"

            )

        if "india_vix" in self.cards:

            self.cards["india_vix"].set_value(

                f"{market_data.get('vix', '--')}"

            )

        self.dashboardUpdated.emit()

    # =====================================================
    # MARKET SUMMARY
    # =====================================================

    def update_market_summary(
        self,
        summary: Dict
    ):

        if "advance_decline" in self.cards:

            self.cards["advance_decline"].set_value(

                summary.get("advance_decline", "-")

            )

        if "market_trend" in self.cards:

            trend = summary.get("trend", "Neutral")

            self.cards["market_trend"].set_value(trend)

            if trend.lower() == "bullish":

                self.cards["market_trend"].set_status_color(

                    current_theme().SUCCESS

                )

            elif trend.lower() == "bearish":

                self.cards["market_trend"].set_status_color(

                    current_theme().ERROR

                )

            else:

                self.cards["market_trend"].set_status_color(

                    current_theme().WARNING

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

            key=lambda x: x.get("change", 0)

        )

        laggard = min(

            sectors,

            key=lambda x: x.get("change", 0)

        )

        if "top_sector" in self.cards:

            self.cards["top_sector"].set_value(

                leader.get("name", "-")

            )

        if "weak_sector" in self.cards:

            self.cards["weak_sector"].set_value(

                laggard.get("name", "-")

            )

        self.sectorUpdated.emit(

            {

                "leader": leader,

                "laggard": laggard,

                "all": sectors

            }

        )

    # =====================================================
    # WATCHLIST
    # =====================================================

    def update_watchlist(
        self,
        stocks: List[Dict]
    ):

        table = self.tables.get("watchlist")

        if table is None:

            return

        table.begin_batch_update()

        table.clear_rows()

        for stock in stocks:

            table.append_row([

                stock.get("symbol", ""),

                stock.get("ltp", ""),

                stock.get("change", ""),

                stock.get("volume", ""),

                stock.get("vwap", ""),

                stock.get("high52", ""),

                stock.get("low52", ""),

            ])

        table.end_batch_update()

    # =====================================================
    # ALERTS
    # =====================================================

    def add_alert(
        self,
        symbol: str,
        message: str,
        level: str = "INFO"
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

            "level": level

        }

        self._alerts.append(alert)

        alerts_table = self.tables.get("alerts")

        if alerts_table:

            alerts_table.append_row([

                alert["time"].strftime("%H:%M:%S"),

                symbol,

                message,

                "",

                level

            ])

        self.statusMessage.emit(

            f"{symbol}: {message}"

        )

    # =====================================================
    # NOTIFICATIONS
    # =====================================================

    def notify(
        self,
        message: str
    ):

        self.statusMessage.emit(message)

        self.update_statusbar(message)

    # =====================================================
    # AUTO REFRESH
    # =====================================================

    def set_refresh_interval(
        self,
        seconds: int
    ):

        self.refresh_timer.setInterval(

            max(1, seconds) * 1000

        )

    def refresh_interval(self):

        return self.refresh_timer.interval() // 1000

    # =====================================================
    # BACKEND SYNCHRONIZATION
    # =====================================================

    def synchronize_backend(self):

        if hasattr(

            self.backend,

            "refresh"

        ):

            self.backend.refresh()

        self.statusMessage.emit(

            "Backend synchronized"

        )

    # =====================================================
    # CONTROLLER STATUS
    # =====================================================

    def controller_status(self):

        return {

            "market_open": self.market_open,

            "scanner_running": self.scanner_running,

            "results": len(self.current_results),

            "refresh_interval":

                self.refresh_interval(),

            "last_scan":

                self.last_scan_text(),

        }
        # =====================================================
    # TRADING SESSION
    # =====================================================

    def set_trading_session(
        self,
        session: str
    ):

        session = session.title()

        valid = [

            "Intraday",

            "Swing",

            "Positional"

        ]

        if session not in valid:

            raise ValueError(

                f"Invalid trading session: {session}"

            )

        self._trading_session = session

        self.statusMessage.emit(

            f"Trading Session: {session}"

        )

    def trading_session(self):

        return getattr(

            self,

            "_trading_session",

            "Intraday"

        )

    # =====================================================
    # SCANNER PROFILE
    # =====================================================

    def set_scanner_profile(
        self,
        profile: str
    ):

        self._scanner_profile = profile

        if hasattr(

            self.backend,

            "set_profile"

        ):

            self.backend.set_profile(profile)

        self.statusMessage.emit(

            f"Profile switched to {profile}"

        )

    def scanner_profile(self):

        return getattr(

            self,

            "_scanner_profile",

            "Default"

        )

    # =====================================================
    # FILTER MANAGEMENT
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

    def remove_filter(
        self,
        key
    ):

        if hasattr(

            self,

            "_filters"

        ):

            self._filters.pop(

                key,

                None

            )

    def filters(self):

        return getattr(

            self,

            "_filters",

            {}

        )

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

    # =====================================================
    # WATCHLIST PERSISTENCE
    # =====================================================

    def save_watchlist(self):

        return list(

            self.favorites()

        )

    def restore_watchlist(
        self,
        symbols: List[str]
    ):

        self._favorites = list(symbols)

    # =====================================================
    # DASHBOARD LAYOUT
    # =====================================================

    def save_layout(self):

        layout = {}

        for name, card in self.cards.items():

            if hasattr(

                card,

                "save_state"

            ):

                layout[name] = card.save_state()

        return layout

    def restore_layout(
        self,
        layout: Dict
    ):

        for name, state in layout.items():

            if name in self.cards:

                card = self.cards[name]

                if hasattr(

                    card,

                    "restore_state"

                ):

                    card.restore_state(state)

    # =====================================================
    # USER PREFERENCES
    # =====================================================

    def save_preferences(self):

        return {

            "session":

                self.trading_session(),

            "profile":

                self.scanner_profile(),

            "filters":

                self.filters(),

            "favorites":

                self.save_watchlist(),

            "refresh_interval":

                self.refresh_interval(),

        }

    def load_preferences(
        self,
        preferences: Dict
    ):

        self.set_trading_session(

            preferences.get(

                "session",

                "Intraday"

            )

        )

        self.set_scanner_profile(

            preferences.get(

                "profile",

                "Default"

            )

        )

        self.set_filters(

            preferences.get(

                "filters",

                {}

            )

        )

        self.restore_watchlist(

            preferences.get(

                "favorites",

                []

            )

        )

        self.set_refresh_interval(

            preferences.get(

                "refresh_interval",

                15

            )

        )

    # =====================================================
    # EXPORT STATE
    # =====================================================

    def export_state(self):

        return {

            "preferences":

                self.save_preferences(),

            "layout":

                self.save_layout(),

            "controller":

                self.controller_status(),

        }

    # =====================================================
    # IMPORT STATE
    # =====================================================

    def import_state(
        self,
        state: Dict
    ):

        self.load_preferences(

            state.get(

                "preferences",

                {}

            )

        )

        self.restore_layout(

            state.get(

                "layout",

                {}

            )

        )

    # =====================================================
    # DIAGNOSTICS
    # =====================================================

    def diagnostics(self):

        return {

            "cards":

                len(self.cards),

            "tables":

                len(self.tables),

            "favorites":

                len(self.favorites()),

            "filters":

                len(self.filters()),

            "profile":

                self.scanner_profile(),

            "session":

                self.trading_session(),

            "market_open":

                self.market_open,

            "scanner_running":

                self.scanner_running,

        }
        # =====================================================
    # TRADING SESSION
    # =====================================================

    def set_trading_session(
        self,
        session: str
    ):

        session = session.title()

        valid = [

            "Intraday",

            "Swing",

            "Positional"

        ]

        if session not in valid:

            raise ValueError(

                f"Invalid trading session: {session}"

            )

        self._trading_session = session

        self.statusMessage.emit(

            f"Trading Session: {session}"

        )

    def trading_session(self):

        return getattr(

            self,

            "_trading_session",

            "Intraday"

        )

    # =====================================================
    # SCANNER PROFILE
    # =====================================================

    def set_scanner_profile(
        self,
        profile: str
    ):

        self._scanner_profile = profile

        if hasattr(

            self.backend,

            "set_profile"

        ):

            self.backend.set_profile(profile)

        self.statusMessage.emit(

            f"Profile switched to {profile}"

        )

    def scanner_profile(self):

        return getattr(

            self,

            "_scanner_profile",

            "Default"

        )

    # =====================================================
    # FILTER MANAGEMENT
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

    def remove_filter(
        self,
        key
    ):

        if hasattr(

            self,

            "_filters"

        ):

            self._filters.pop(

                key,

                None

            )

    def filters(self):

        return getattr(

            self,

            "_filters",

            {}

        )

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

    # =====================================================
    # WATCHLIST PERSISTENCE
    # =====================================================

    def save_watchlist(self):

        return list(

            self.favorites()

        )

    def restore_watchlist(
        self,
        symbols: List[str]
    ):

        self._favorites = list(symbols)

    # =====================================================
    # DASHBOARD LAYOUT
    # =====================================================

    def save_layout(self):

        layout = {}

        for name, card in self.cards.items():

            if hasattr(

                card,

                "save_state"

            ):

                layout[name] = card.save_state()

        return layout

    def restore_layout(
        self,
        layout: Dict
    ):

        for name, state in layout.items():

            if name in self.cards:

                card = self.cards[name]

                if hasattr(

                    card,

                    "restore_state"

                ):

                    card.restore_state(state)

    # =====================================================
    # USER PREFERENCES
    # =====================================================

    def save_preferences(self):

        return {

            "session":

                self.trading_session(),

            "profile":

                self.scanner_profile(),

            "filters":

                self.filters(),

            "favorites":

                self.save_watchlist(),

            "refresh_interval":

                self.refresh_interval(),

        }

    def load_preferences(
        self,
        preferences: Dict
    ):

        self.set_trading_session(

            preferences.get(

                "session",

                "Intraday"

            )

        )

        self.set_scanner_profile(

            preferences.get(

                "profile",

                "Default"

            )

        )

        self.set_filters(

            preferences.get(

                "filters",

                {}

            )

        )

        self.restore_watchlist(

            preferences.get(

                "favorites",

                []

            )

        )

        self.set_refresh_interval(

            preferences.get(

                "refresh_interval",

                15

            )

        )

    # =====================================================
    # EXPORT STATE
    # =====================================================

    def export_state(self):

        return {

            "preferences":

                self.save_preferences(),

            "layout":

                self.save_layout(),

            "controller":

                self.controller_status(),

        }

    # =====================================================
    # IMPORT STATE
    # =====================================================

    def import_state(
        self,
        state: Dict
    ):

        self.load_preferences(

            state.get(

                "preferences",

                {}

            )

        )

        self.restore_layout(

            state.get(

                "layout",

                {}

            )

        )

    # =====================================================
    # DIAGNOSTICS
    # =====================================================

    def diagnostics(self):

        return {

            "cards":

                len(self.cards),

            "tables":

                len(self.tables),

            "favorites":

                len(self.favorites()),

            "filters":

                len(self.filters()),

            "profile":

                self.scanner_profile(),

            "session":

                self.trading_session(),

            "market_open":

                self.market_open,

            "scanner_running":

                self.scanner_running,

        }
        # =====================================================
    # MULTI SCANNER MANAGEMENT
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
    # EXECUTE SCANNER
    # =====================================================

    def execute_scanner(
        self,
        name: str
    ):

        scanners = self.scanners()

        if name not in scanners:
            return []

        scanner = scanners[name]

        self.statusMessage.emit(
            f"Running {name} scanner..."
        )

        results = scanner.run()

        return results

    # =====================================================
    # EXECUTE ALL SCANNERS
    # =====================================================

    def execute_all_scanners(self):

        combined = []

        for name in self.scanners():

            try:

                result = self.execute_scanner(name)

                combined.extend(result)

            except Exception as exc:

                self.log_scan(
                    f"{name} failed : {exc}"
                )

        self.current_results = combined

        self.refresh_dashboard()

    # =====================================================
    # SCAN PRIORITY
    # =====================================================

    def set_scan_priority(
        self,
        priorities: Dict[str, int]
    ):

        self._priorities = priorities

    def scan_priorities(self):

        return getattr(
            self,
            "_priorities",
            {}
        )

    def ordered_scanners(self):

        scanners = list(self.scanners().items())

        priority = self.scan_priorities()

        scanners.sort(
            key=lambda x: priority.get(
                x[0],
                999
            )
        )

        return scanners

    # =====================================================
    # SCHEDULED SCANS
    # =====================================================

    def enable_scheduled_scans(
        self,
        interval_seconds: int
    ):

        self.refresh_timer.setInterval(
            interval_seconds * 1000
        )

        if not self.refresh_timer.isActive():

            self.refresh_timer.start()

    def disable_scheduled_scans(self):

        self.refresh_timer.stop()

    # =====================================================
    # ALERT RULE ENGINE
    # =====================================================

    def register_alert_rule(
        self,
        name: str,
        callback
    ):

        if not hasattr(self, "_alert_rules"):

            self._alert_rules = {}

        self._alert_rules[name] = callback

    def evaluate_alerts(self):

        if not hasattr(
            self,
            "_alert_rules"
        ):
            return

        for stock in self.current_results:

            for name, callback in self._alert_rules.items():

                try:

                    triggered = callback(stock)

                    if triggered:

                        self.add_alert(

                            stock.get(
                                "symbol",
                                "-"
                            ),

                            name,

                            "INFO"

                        )

                except Exception as exc:

                    self.log_scan(

                        f"Alert rule error : {exc}"

                    )

    # =====================================================
    # NOTIFICATION ROUTING
    # =====================================================

    def route_notification(
        self,
        level: str,
        message: str
    ):

        level = level.upper()

        formatted = f"[{level}] {message}"

        self.notify(formatted)

    # =====================================================
    # SECTOR SCANNING
    # =====================================================

    def run_sector_scan(
        self,
        sector: str
    ):

        if not hasattr(

            self.backend,

            "run_sector_scan"

        ):

            return []

        results = self.backend.run_sector_scan(

            sector

        )

        self.statusMessage.emit(

            f"{sector} scan completed"

        )

        return results

    # =====================================================
    # RISK METRICS
    # =====================================================

    def update_risk_metrics(
        self,
        metrics: Dict
    ):

        self._risk_metrics = metrics

        if "risk" in self.cards:

            self.cards["risk"].set_value(

                metrics.get(

                    "risk",

                    "-"

                )

            )

        if "reward" in self.cards:

            self.cards["reward"].set_value(

                metrics.get(

                    "reward",

                    "-"

                )

            )

    def risk_metrics(self):

        return getattr(

            self,

            "_risk_metrics",

            {}

        )

    # =====================================================
    # PERFORMANCE MONITOR
    # =====================================================

    def performance_monitor(self):

        return {

            "last_scan_duration":

                self.last_scan_duration(),

            "scheduled":

                self.refresh_timer.isActive(),

            "market_open":

                self.market_open,

            "scanner_count":

                len(self.scanners()),

            "alerts":

                len(

                    getattr(

                        self,

                        "_alerts",

                        []

                    )

                ),

            "results":

                len(self.current_results),

        }
        # =====================================================
    # EVENT BUS
    # =====================================================

    def register_event(
        self,
        event_name: str,
        callback
    ):

        if not hasattr(self, "_event_bus"):
            self._event_bus = {}

        self._event_bus.setdefault(
            event_name,
            []
        ).append(callback)

    def unregister_event(
        self,
        event_name: str,
        callback
    ):

        if not hasattr(self, "_event_bus"):
            return

        callbacks = self._event_bus.get(
            event_name,
            []
        )

        if callback in callbacks:
            callbacks.remove(callback)

    def emit_event(
        self,
        event_name: str,
        *args,
        **kwargs
    ):

        if not hasattr(self, "_event_bus"):
            return

        for callback in self._event_bus.get(
            event_name,
            []
        ):

            try:
                callback(*args, **kwargs)
            except Exception as exc:
                self.log_scan(
                    f"Event '{event_name}' failed: {exc}"
                )

    # =====================================================
    # WORKSPACE MANAGEMENT
    # =====================================================

    def save_workspace(self):

        return {

            "layout": self.save_layout(),

            "preferences": self.save_preferences(),

            "filters": self.filters(),

            "favorites": self.favorites(),

        }

    def restore_workspace(
        self,
        workspace: Dict
    ):

        self.restore_layout(
            workspace.get(
                "layout",
                {}
            )
        )

        self.load_preferences(
            workspace.get(
                "preferences",
                {}
            )
        )

    # =====================================================
    # SESSION MANAGEMENT
    # =====================================================

    def start_session(self):

        self._session_start = datetime.now()

        self.statusMessage.emit(
            "Trading session started"
        )

    def end_session(self):

        self._session_end = datetime.now()

        self.statusMessage.emit(
            "Trading session ended"
        )

    def session_duration(self):

        if not hasattr(self, "_session_start"):
            return 0

        end = getattr(
            self,
            "_session_end",
            datetime.now()
        )

        return int(
            (
                end - self._session_start
            ).total_seconds()
        )

    # =====================================================
    # THEME SYNCHRONIZATION
    # =====================================================

    def synchronize_theme(self):

        for card in self.cards.values():

            if hasattr(
                card,
                "refresh_theme"
            ):

                card.refresh_theme()

        for table in self.tables.values():

            if hasattr(
                table,
                "refresh_theme"
            ):

                table.refresh_theme()

        self.dashboardUpdated.emit()

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(self):

        return {

            "dashboard":

                self.dashboard is not None,

            "backend":

                self.backend is not None,

            "cards":

                len(self.cards),

            "tables":

                len(self.tables),

            "market_timer":

                self.market_timer.isActive(),

            "refresh_timer":

                self.refresh_timer.isActive(),

            "scanner_running":

                self.scanner_running,

        }

    # =====================================================
    # ERROR RECOVERY
    # =====================================================

    def recover(self):

        try:

            self.stop()

            self.start()

            self.statusMessage.emit(
                "Recovery completed"
            )

        except Exception as exc:

            self.statusMessage.emit(
                f"Recovery failed: {exc}"
            )

    # =====================================================
    # MEMORY CLEANUP
    # =====================================================

    def cleanup(self):

        self.stop()

        self.current_results.clear()

        if hasattr(self, "_alerts"):
            self._alerts.clear()

        if hasattr(self, "_favorites"):
            self._favorites.clear()

        if hasattr(self, "_filters"):
            self._filters.clear()

    # =====================================================
    # MODULE REGISTRATION
    # =====================================================

    def register_module(
        self,
        name: str,
        module
    ):

        if not hasattr(self, "_modules"):
            self._modules = {}

        self._modules[name] = module

    def module(
        self,
        name: str
    ):

        return getattr(
            self,
            "_modules",
            {}
        ).get(name)

    def registered_modules(self):

        return getattr(
            self,
            "_modules",
            {}
        )

    # =====================================================
    # MODULE INITIALIZATION
    # =====================================================

    def initialize_modules(self):

        for module in self.registered_modules().values():

            if hasattr(
                module,
                "initialize"
            ):

                module.initialize()

    # =====================================================
    # CONTROLLER SUMMARY
    # =====================================================

    def summary(self):

        return {

            "session":

                self.trading_session(),

            "profile":

                self.scanner_profile(),

            "market_open":

                self.market_open,

            "results":

                len(self.current_results),

            "favorites":

                len(self.favorites()),

            "modules":

                len(self.registered_modules()),

            "health":

                self.health_check(),

        }
        # =====================================================
    # CONTROLLER INITIALIZATION
    # =====================================================

    def initialize(self):

        self.log_scan("Initializing Dashboard Controller")

        self._discover_widgets()

        self._configure_timers()

        self._connect_signals()

        self.initialize_modules()

        self.refresh_dashboard()

        self.statusMessage.emit(
            "Dashboard Controller initialized"
        )

    # =====================================================
    # STARTUP
    # =====================================================

    def startup(self):

        self.log_scan("Dashboard startup")

        self.start_session()

        self.start()

        self.initialize()

        self.emit_event("startup")

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(self):

        self.log_scan("Dashboard shutdown")

        self.emit_event("shutdown")

        self.end_session()

        self.cleanup()

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        self.log_scan("Resetting controller")

        self.clear_results()

        self.current_results = []

        self._alerts = []

        self._favorites = []

        self._filters = {}

        self._modules = {}

        self.dashboardUpdated.emit()

        self.statusMessage.emit(
            "Controller reset completed"
        )

    # =====================================================
    # RELOAD
    # =====================================================

    def reload(self):

        self.shutdown()

        self.startup()

    # =====================================================
    # VERSION
    # =====================================================

    @staticmethod
    def version():

        return "4.0"

    @staticmethod
    def application_name():

        return "StockVersity Scanner Pro"

    @staticmethod
    def powered_by():

        return "Powered by AI"

    # =====================================================
    # BUILD INFO
    # =====================================================

    def build_info(self):

        return {

            "application":
                self.application_name(),

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

            f"<DashboardController "

            f"version={self.version()} "

            f"session={self.trading_session()} "

            f"profile={self.scanner_profile()} "

            f"results={len(self.current_results)}>"

        )

    def __str__(self):

        return self.__repr__()


# =====================================================
# FACTORY
# =====================================================

def create_dashboard_controller(

    dashboard,

    backend

):

    controller = DashboardController(

        dashboard,

        backend

    )

    controller.initialize()

    return controller


# =====================================================
# MODULE EXPORTS
# =====================================================

__all__ = [

    "DashboardController",

    "ScannerWorker",

    "create_dashboard_controller",

]


# =====================================================
# END OF FILE
#
# StockVersity Scanner Pro
# Powered by AI
# Version 4.0
#
# ui/dashboard_controller.py
# =====================================================