from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional, Dict, Any

from core.alert_manager import AlertManager
from core.data_manager import DataManager
from core.market_analyzer import MarketAnalyzer
from core.screener_engine import ScreenerEngine

from ui.dashboard import DashboardWindow


# ==========================================================
# DASHBOARD CONTROLLER
# ==========================================================

class DashboardController:

    VERSION = "1.0.0"

    def __init__(
        self,
        dashboard: DashboardWindow,
        data_manager: DataManager,
        market_analyzer: MarketAnalyzer,
        screener: ScreenerEngine,
        alert_manager: AlertManager,
    ):

        self.logger = logging.getLogger(
            self.__class__.__name__
        )

        self.dashboard = dashboard

        self.data_manager = data_manager

        self.market_analyzer = market_analyzer

        self.screener = screener

        self.alert_manager = alert_manager

        self.started = datetime.now()

        self.logger.info(
            "DashboardController initialized."
        )

        self._connect_dashboard()
            # ==========================================================
    # CONNECT DASHBOARD
    # ==========================================================

    def _connect_dashboard(self) -> None:
        """
        Connect dashboard signals.
        """

        self.logger.info(
            "Connecting dashboard..."
        )

        if hasattr(
            self.dashboard,
            "refresh_requested",
        ):

            self.dashboard.refresh_requested.connect(
                self.refresh_dashboard
            )

        if hasattr(
            self.dashboard,
            "scan_requested",
        ):

            self.dashboard.scan_requested.connect(
                self.run_scan
            )

        if hasattr(
            self.dashboard,
            "settings_requested",
        ):

            self.dashboard.settings_requested.connect(
                self.open_settings
            )

        self.logger.info(
            "Dashboard connected."
        )
            # ==========================================================
    # INITIALIZE DASHBOARD
    # ==========================================================

    def initialize(self) -> None:
        """
        Initialize the dashboard after login.
        """

        self.logger.info(
            "Initializing dashboard..."
        )

        self.load_dashboard()

        self.load_market_status()

        self.load_summary_cards()

        self.load_watchlist()

        self.load_recent_alerts()

        self.logger.info(
            "Dashboard initialized successfully."
        )

    # ==========================================================
    # LOAD DASHBOARD
    # ==========================================================

    def load_dashboard(self) -> None:
        """
        Load dashboard components.
        """

        try:

            if hasattr(
                self.dashboard,
                "initialize"
            ):

                self.dashboard.initialize()

        except Exception as ex:

            self.logger.exception(ex)

    # ==========================================================
    # LOAD MARKET STATUS
    # ==========================================================

    def load_market_status(self) -> None:
        """
        Display current market status.
        """

        try:

            status = self.market_analyzer.market_status()

            if hasattr(
                self.dashboard,
                "update_market_status"
            ):

                self.dashboard.update_market_status(
                    status
                )

        except Exception as ex:

            self.logger.exception(ex)

    # ==========================================================
    # LOAD SUMMARY CARDS
    # ==========================================================

    def load_summary_cards(self) -> None:
        """
        Load dashboard information cards.
        """

        try:

            summary = {

                "market": self.market_analyzer.market_summary(),

                "scanner": self.screener.summary(),

                "alerts": self.alert_manager.summary(),

            }

            if hasattr(
                self.dashboard,
                "update_summary_cards"
            ):

                self.dashboard.update_summary_cards(
                    summary
                )

        except Exception as ex:

            self.logger.exception(ex)

    # ==========================================================
    # LOAD WATCHLIST
    # ==========================================================

    def load_watchlist(self) -> None:
        """
        Load watchlist.
        """

        try:

            watchlist = self.data_manager.get_watchlist()

            if hasattr(
                self.dashboard,
                "update_watchlist"
            ):

                self.dashboard.update_watchlist(
                    watchlist
                )

        except Exception as ex:

            self.logger.exception(ex)

    # ==========================================================
    # LOAD RECENT ALERTS
    # ==========================================================

    def load_recent_alerts(self) -> None:
        """
        Load latest alerts.
        """

        try:

            alerts = self.alert_manager.latest_alerts(
                limit=10
            )

            if hasattr(
                self.dashboard,
                "update_alert_table"
            ):

                self.dashboard.update_alert_table(
                    alerts
                )

        except Exception as ex:

            self.logger.exception(ex)

    # ==========================================================
    # SHOW DASHBOARD
    # ==========================================================

    def show_dashboard(self) -> None:
        """
        Show dashboard window.
        """

        self.dashboard.show()

    # ==========================================================
    # HIDE DASHBOARD
    # ==========================================================

    def hide_dashboard(self) -> None:
        """
        Hide dashboard.
        """

        self.dashboard.hide()

    # ==========================================================
    # ACTIVATE DASHBOARD
    # ==========================================================

    def activate_dashboard(self) -> None:
        """
        Bring dashboard to front.
        """

        self.dashboard.raise_()

        self.dashboard.activateWindow()
            # ==========================================================
    # MARKET UPDATE
    # ==========================================================

    def update_market(self) -> None:
        """
        Update complete market information.
        """

        self.logger.debug(
            "Updating market..."
        )

        try:

            self.update_market_status()

            self.update_indices()

            self.update_sector_rotation()

            self.update_market_breadth()

            self.update_vix()

            self.update_header()

        except Exception as ex:

            self.logger.exception(ex)

    # ==========================================================
    # MARKET STATUS
    # ==========================================================

    def update_market_status(self) -> None:
        """
        Update market status.
        """

        status = self.market_analyzer.market_status()

        if hasattr(
            self.dashboard,
            "update_market_status",
        ):

            self.dashboard.update_market_status(
                status
            )

    # ==========================================================
    # MARKET INDICES
    # ==========================================================

    def update_indices(self) -> None:
        """
        Update Nifty and Bank Nifty.
        """

        indices = self.market_analyzer.market_indices()

        if hasattr(
            self.dashboard,
            "update_indices",
        ):

            self.dashboard.update_indices(
                indices
            )

    # ==========================================================
    # SECTOR ROTATION
    # ==========================================================

    def update_sector_rotation(self) -> None:
        """
        Update sector strength.
        """

        sectors = (
            self.market_analyzer
            .sector_rotation()
        )

        if hasattr(
            self.dashboard,
            "update_sector_rotation",
        ):

            self.dashboard.update_sector_rotation(
                sectors
            )

    # ==========================================================
    # MARKET BREADTH
    # ==========================================================

    def update_market_breadth(self) -> None:
        """
        Update advance/decline ratio.
        """

        breadth = (

            self.market_analyzer

            .market_breadth()

        )

        if hasattr(
            self.dashboard,
            "update_market_breadth",
        ):

            self.dashboard.update_market_breadth(
                breadth
            )

    # ==========================================================
    # INDIA VIX
    # ==========================================================

    def update_vix(self) -> None:
        """
        Update India VIX.
        """

        vix = self.market_analyzer.vix()

        if hasattr(
            self.dashboard,
            "update_vix",
        ):

            self.dashboard.update_vix(
                vix
            )

    # ==========================================================
    # HEADER
    # ==========================================================

    def update_header(self) -> None:
        """
        Update dashboard header.
        """

        header = {

            "time": datetime.now(),

            "market":

                self.market_analyzer.market_status(),

            "connected":

                self.data_manager.is_connected(),

        }

        if hasattr(
            self.dashboard,
            "update_header",
        ):

            self.dashboard.update_header(
                header
            )

    # ==========================================================
    # AUTO REFRESH
    # ==========================================================

    def refresh_market(self) -> None:
        """
        Refresh market information.
        """

        self.update_market()
            # ==========================================================
    # RUN SCAN
    # ==========================================================

    def run_scan(self) -> None:
        """
        Run complete market scan.
        """

        self.logger.info(
            "Starting market scan..."
        )

        try:

            self.dashboard.show_loading(
                "Scanning market..."
            )

            self.update_scan_progress(0)

            opportunities = self.screener.scan()

            self.update_scan_progress(100)

            self.update_opportunities(
                opportunities
            )

            self.update_scanner_summary()

            self.dashboard.hide_loading()

            self.logger.info(
                "Market scan completed."
            )

        except Exception as ex:

            self.logger.exception(ex)

            self.dashboard.hide_loading()

    # ==========================================================
    # INTRADAY SCAN
    # ==========================================================

    def run_intraday_scan(self) -> None:
        """
        Execute Intraday scan.
        """

        try:

            opportunities = (

                self.screener.scan_intraday()

            )

            self.update_opportunities(
                opportunities
            )

        except Exception as ex:

            self.logger.exception(ex)

    # ==========================================================
    # SWING SCAN
    # ==========================================================

    def run_swing_scan(self) -> None:
        """
        Execute Swing scan.
        """

        try:

            opportunities = (

                self.screener.scan_swing()

            )

            self.update_opportunities(
                opportunities
            )

        except Exception as ex:

            self.logger.exception(ex)

    # ==========================================================
    # POSITIONAL SCAN
    # ==========================================================

    def run_positional_scan(self) -> None:
        """
        Execute Positional scan.
        """

        try:

            opportunities = (

                self.screener.scan_positional()

            )

            self.update_opportunities(
                opportunities
            )

        except Exception as ex:

            self.logger.exception(ex)

    # ==========================================================
    # UPDATE TABLE
    # ==========================================================

    def update_opportunities(
        self,
        opportunities,
    ) -> None:
        """
        Update scanner table.
        """

        if hasattr(
            self.dashboard,
            "update_opportunities",
        ):

            self.dashboard.update_opportunities(
                opportunities
            )

    # ==========================================================
    # UPDATE SUMMARY
    # ==========================================================

    def update_scanner_summary(
        self,
    ) -> None:
        """
        Update scanner summary cards.
        """

        summary = self.screener.summary()

        if hasattr(
            self.dashboard,
            "update_scanner_summary",
        ):

            self.dashboard.update_scanner_summary(
                summary
            )

    # ==========================================================
    # SCAN PROGRESS
    # ==========================================================

    def update_scan_progress(
        self,
        value: int,
    ) -> None:
        """
        Update scan progress.
        """

        if hasattr(
            self.dashboard,
            "update_progress",
        ):

            self.dashboard.update_progress(
                value
            )

    # ==========================================================
    # AUTO SCAN
    # ==========================================================

    def auto_scan(self) -> None:
        """
        Execute automatic scan.
        """

        self.logger.info(
            "Auto scan triggered."
        )

        self.run_scan()

    # ==========================================================
    # REFRESH SCANNER
    # ==========================================================

    def refresh_scanner(self) -> None:
        """
        Refresh scanner results.
        """

        self.run_scan()

    # ==========================================================
    # FILTER RESULTS
    # ==========================================================

    def apply_filter(
        self,
        filters: Dict[str, Any],
    ) -> None:
        """
        Apply dashboard filters.
        """

        try:

            filtered = self.screener.filter(
                filters
            )

            self.update_opportunities(
                filtered
            )

        except Exception as ex:

            self.logger.exception(ex)
                # ==========================================================
    # PROCESS ALERTS
    # ==========================================================

    def process_alerts(self) -> None:
        """
        Process newly generated alerts.
        """

        try:

            alerts = self.alert_manager.process()

            if alerts:

                self.display_alerts(alerts)

                self.update_alert_history()

        except Exception as ex:

            self.logger.exception(ex)

    # ==========================================================
    # DISPLAY ALERTS
    # ==========================================================

    def display_alerts(
        self,
        alerts,
    ) -> None:
        """
        Display alerts on dashboard.
        """

        if hasattr(
            self.dashboard,
            "show_alerts",
        ):

            self.dashboard.show_alerts(
                alerts
            )

    # ==========================================================
    # BUY SIGNAL
    # ==========================================================

    def handle_buy_signal(
        self,
        signal: Dict[str, Any],
    ) -> None:
        """
        Handle buy signal.
        """

        self.logger.info(
            "BUY Signal: %s",
            signal.get("symbol")
        )

        self.alert_manager.notify(
            signal
        )

    # ==========================================================
    # SELL SIGNAL
    # ==========================================================

    def handle_sell_signal(
        self,
        signal: Dict[str, Any],
    ) -> None:
        """
        Handle sell signal.
        """

        self.logger.info(
            "SELL Signal: %s",
            signal.get("symbol")
        )

        self.alert_manager.notify(
            signal
        )

    # ==========================================================
    # ALERT HISTORY
    # ==========================================================

    def update_alert_history(self) -> None:
        """
        Update alert history table.
        """

        history = self.alert_manager.history()

        if hasattr(
            self.dashboard,
            "update_alert_history",
        ):

            self.dashboard.update_alert_history(
                history
            )

    # ==========================================================
    # UNREAD ALERTS
    # ==========================================================

    def unread_alerts(self) -> int:
        """
        Return unread alert count.
        """

        return self.alert_manager.unread_count()

    # ==========================================================
    # MARK ALERT READ
    # ==========================================================

    def mark_alert_read(
        self,
        alert_id: str,
    ) -> None:
        """
        Mark alert as read.
        """

        self.alert_manager.mark_read(
            alert_id
        )

        self.update_alert_history()

    # ==========================================================
    # CLEAR ALERTS
    # ==========================================================

    def clear_alerts(self) -> None:
        """
        Clear alert history.
        """

        self.alert_manager.clear()

        self.update_alert_history()

    # ==========================================================
    # PLAY ALERT SOUND
    # ==========================================================

    def play_alert_sound(self) -> None:
        """
        Play alert notification sound.
        """

        if hasattr(
            self.dashboard,
            "play_notification_sound",
        ):

            self.dashboard.play_notification_sound()

    # ==========================================================
    # DESKTOP NOTIFICATION
    # ==========================================================

    def notify_user(
        self,
        title: str,
        message: str,
    ) -> None:
        """
        Show desktop notification.
        """

        if hasattr(
            self.dashboard,
            "show_notification",
        ):

            self.dashboard.show_notification(
                title,
                message,
            )

    # ==========================================================
    # FILTER ALERTS
    # ==========================================================

    def filter_alerts(
        self,
        filters: Dict[str, Any],
    ) -> None:
        """
        Filter alert history.
        """

        alerts = self.alert_manager.filter(
            filters
        )

        if hasattr(
            self.dashboard,
            "update_alert_history",
        ):

            self.dashboard.update_alert_history(
                alerts
            )
                # ==========================================================
    # LOAD WATCHLIST
    # ==========================================================

    def refresh_watchlist(self) -> None:
        """
        Refresh the watchlist displayed on the dashboard.
        """

        try:

            watchlist = self.data_manager.get_watchlist()

            if hasattr(
                self.dashboard,
                "update_watchlist",
            ):

                self.dashboard.update_watchlist(
                    watchlist
                )

        except Exception as ex:

            self.logger.exception(ex)

    # ==========================================================
    # ADD SYMBOL
    # ==========================================================

    def add_to_watchlist(
        self,
        symbol: str,
    ) -> bool:
        """
        Add a stock to the watchlist.
        """

        try:

            added = self.data_manager.add_to_watchlist(
                symbol
            )

            if added:

                self.refresh_watchlist()

            return added

        except Exception as ex:

            self.logger.exception(ex)

            return False

    # ==========================================================
    # REMOVE SYMBOL
    # ==========================================================

    def remove_from_watchlist(
        self,
        symbol: str,
    ) -> bool:
        """
        Remove a stock from the watchlist.
        """

        try:

            removed = (
                self.data_manager.remove_from_watchlist(
                    symbol
                )
            )

            if removed:

                self.refresh_watchlist()

            return removed

        except Exception as ex:

            self.logger.exception(ex)

            return False

    # ==========================================================
    # PIN SYMBOL
    # ==========================================================

    def pin_symbol(
        self,
        symbol: str,
    ) -> None:
        """
        Pin a symbol to the top of the watchlist.
        """

        try:

            self.data_manager.pin_symbol(
                symbol
            )

            self.refresh_watchlist()

        except Exception as ex:

            self.logger.exception(ex)

    # ==========================================================
    # UNPIN SYMBOL
    # ==========================================================

    def unpin_symbol(
        self,
        symbol: str,
    ) -> None:
        """
        Remove pin from a symbol.
        """

        try:

            self.data_manager.unpin_symbol(
                symbol
            )

            self.refresh_watchlist()

        except Exception as ex:

            self.logger.exception(ex)

    # ==========================================================
    # SEARCH WATCHLIST
    # ==========================================================

    def search_watchlist(
        self,
        keyword: str,
    ) -> None:
        """
        Search symbols in the watchlist.
        """

        try:

            results = (
                self.data_manager.search_watchlist(
                    keyword
                )
            )

            if hasattr(
                self.dashboard,
                "update_watchlist",
            ):

                self.dashboard.update_watchlist(
                    results
                )

        except Exception as ex:

            self.logger.exception(ex)

    # ==========================================================
    # IMPORT WATCHLIST
    # ==========================================================

    def import_watchlist(
        self,
        file_path: str,
    ) -> bool:
        """
        Import watchlist from file.
        """

        try:

            success = (
                self.data_manager.import_watchlist(
                    file_path
                )
            )

            if success:

                self.refresh_watchlist()

            return success

        except Exception as ex:

            self.logger.exception(ex)

            return False

    # ==========================================================
    # EXPORT WATCHLIST
    # ==========================================================

    def export_watchlist(
        self,
        file_path: str,
    ) -> bool:
        """
        Export watchlist.
        """

        try:

            return self.data_manager.export_watchlist(
                file_path
            )

        except Exception as ex:

            self.logger.exception(ex)

            return False

    # ==========================================================
    # WATCHLIST SELECTION
    # ==========================================================

    def select_watchlist_symbol(
        self,
        symbol: str,
    ) -> None:
        """
        Handle symbol selection from the watchlist.
        """

        try:

            if hasattr(
                self.dashboard,
                "select_symbol",
            ):

                self.dashboard.select_symbol(
                    symbol
                )

        except Exception as ex:

            self.logger.exception(ex)

    # ==========================================================
    # WATCHLIST SYNCHRONIZATION
    # ==========================================================

    def synchronize_watchlist(self) -> None:
        """
        Synchronize watchlist with live market data.
        """

        try:

            self.data_manager.sync_watchlist()

            self.refresh_watchlist()

        except Exception as ex:

            self.logger.exception(ex)
                # ==========================================================
    # REFRESH DASHBOARD
    # ==========================================================

    def refresh_dashboard(self) -> None:
        """
        Refresh all dashboard components.
        """

        self.logger.info(
            "Refreshing dashboard..."
        )

        try:

            self.update_market()

            self.refresh_watchlist()

            self.update_scanner_summary()

            self.update_alert_history()

            self.logger.info(
                "Dashboard refreshed."
            )

        except Exception as ex:

            self.logger.exception(ex)

    # ==========================================================
    # START AUTO REFRESH
    # ==========================================================

    def start_auto_refresh(self) -> None:
        """
        Start automatic dashboard refresh.
        """

        if hasattr(
            self.dashboard,
            "start_refresh_timer",
        ):

            self.dashboard.start_refresh_timer()

            self.logger.info(
                "Auto refresh started."
            )

    # ==========================================================
    # STOP AUTO REFRESH
    # ==========================================================

    def stop_auto_refresh(self) -> None:
        """
        Stop automatic dashboard refresh.
        """

        if hasattr(
            self.dashboard,
            "stop_refresh_timer",
        ):

            self.dashboard.stop_refresh_timer()

            self.logger.info(
                "Auto refresh stopped."
            )

    # ==========================================================
    # PAUSE REFRESH
    # ==========================================================

    def pause_refresh(self) -> None:
        """
        Pause refresh updates.
        """

        self.stop_auto_refresh()

    # ==========================================================
    # RESUME REFRESH
    # ==========================================================

    def resume_refresh(self) -> None:
        """
        Resume refresh updates.
        """

        self.start_auto_refresh()

    # ==========================================================
    # REFRESH MARKET DATA
    # ==========================================================

    def refresh_market_data(self) -> None:
        """
        Refresh live market data.
        """

        try:

            self.data_manager.refresh_market_data()

            self.update_market()

        except Exception as ex:

            self.logger.exception(ex)

    # ==========================================================
    # REFRESH SCANNER DATA
    # ==========================================================

    def refresh_scanner_data(self) -> None:
        """
        Refresh scanner results.
        """

        try:

            self.refresh_scanner()

        except Exception as ex:

            self.logger.exception(ex)

    # ==========================================================
    # BACKGROUND UPDATE
    # ==========================================================

    def background_update(self) -> None:
        """
        Background refresh cycle.
        """

        try:

            self.refresh_market_data()

            self.process_alerts()

        except Exception as ex:

            self.logger.exception(ex)

    # ==========================================================
    # MARKET HOURS CHECK
    # ==========================================================

    def refresh_if_market_open(self) -> None:
        """
        Refresh only when the market is open.
        """

        try:

            if self.market_analyzer.market_status().get(
                "is_open",
                False,
            ):

                self.background_update()

            else:

                self.logger.debug(
                    "Market is closed. Refresh skipped."
                )

        except Exception as ex:

            self.logger.exception(ex)

    # ==========================================================
    # FORCE REFRESH
    # ==========================================================

    def force_refresh(self) -> None:
        """
        Force a complete refresh.
        """

        self.refresh_dashboard()

        self.run_scan()
            # ==========================================================
    # DASHBOARD STATISTICS
    # ==========================================================

    def dashboard_statistics(self) -> Dict[str, Any]:
        """
        Return dashboard statistics.
        """

        return {

            "started": self.started,

            "uptime": datetime.now() - self.started,

            "market_status":
                self.market_analyzer.market_status(),

            "watchlist_count":
                len(self.data_manager.get_watchlist()),

            "scanner_summary":
                self.screener.summary(),

            "alert_summary":
                self.alert_manager.summary(),

        }

    # ==========================================================
    # HEALTH CHECK
    # ==========================================================

    def health_check(self) -> Dict[str, Any]:
        """
        Check controller health.
        """

        return {

            "healthy": True,

            "dashboard":

                self.dashboard is not None,

            "data_manager":

                self.data_manager is not None,

            "market_analyzer":

                self.market_analyzer is not None,

            "screener":

                self.screener is not None,

            "alert_manager":

                self.alert_manager is not None,

            "connected":

                self.data_manager.is_connected(),

        }

    # ==========================================================
    # PERFORMANCE METRICS
    # ==========================================================

    def performance_metrics(self) -> Dict[str, Any]:
        """
        Runtime performance metrics.
        """

        return {

            "uptime_seconds":

                (datetime.now() - self.started)

                .total_seconds(),

            "watchlist":

                len(self.data_manager.get_watchlist()),

            "alerts":

                self.alert_manager.unread_count(),

        }

    # ==========================================================
    # DIAGNOSTICS
    # ==========================================================

    def diagnostics(self) -> Dict[str, Any]:
        """
        Complete diagnostics.
        """

        return {

            "statistics":

                self.dashboard_statistics(),

            "health":

                self.health_check(),

            "performance":

                self.performance_metrics(),

        }

    # ==========================================================
    # DEBUG REPORT
    # ==========================================================

    def debug_report(self) -> Dict[str, Any]:
        """
        Generate debug report.
        """

        return {

            "controller":

                self.__class__.__name__,

            "version":

                self.VERSION,

            "diagnostics":

                self.diagnostics(),

        }

    # ==========================================================
    # STATUS
    # ==========================================================

    def status(self) -> Dict[str, Any]:
        """
        Current controller status.
        """

        return {

            "running": True,

            "started": self.started,

            "uptime":

                str(datetime.now() - self.started),

        }

    # ==========================================================
    # RESET STATISTICS
    # ==========================================================

    def reset_statistics(self) -> None:
        """
        Reset runtime statistics.
        """

        self.started = datetime.now()

        self.logger.info(
            "Dashboard statistics reset."
        )

    # ==========================================================
    # STRING REPRESENTATION
    # ==========================================================

    def __repr__(self):

        return (

            f"<DashboardController "

            f"version={self.VERSION}>"

        )

    def __str__(self):

        return (

            "DashboardController"

        )
        # ==========================================================
    # STOP SERVICES
    # ==========================================================

    def stop_services(self) -> None:
        """
        Stop all background services managed by the controller.
        """

        self.logger.info(
            "Stopping dashboard services..."
        )

        try:

            self.stop_auto_refresh()

        except Exception as ex:

            self.logger.exception(ex)

    # ==========================================================
    # DISCONNECT SIGNALS
    # ==========================================================

    def disconnect_signals(self) -> None:
        """
        Disconnect dashboard signals safely.
        """

        try:

            if hasattr(
                self.dashboard,
                "refresh_requested",
            ):

                self.dashboard.refresh_requested.disconnect(
                    self.refresh_dashboard
                )

        except Exception:
            pass

        try:

            if hasattr(
                self.dashboard,
                "scan_requested",
            ):

                self.dashboard.scan_requested.disconnect(
                    self.run_scan
                )

        except Exception:
            pass

        try:

            if hasattr(
                self.dashboard,
                "settings_requested",
            ):

                self.dashboard.settings_requested.disconnect(
                    self.open_settings
                )

        except Exception:
            pass

    # ==========================================================
    # RELEASE RESOURCES
    # ==========================================================

    def release_resources(self) -> None:
        """
        Release controller resources.
        """

        self.logger.info(
            "Releasing dashboard resources..."
        )

        self.dashboard = None

        self.data_manager = None

        self.market_analyzer = None

        self.screener = None

        self.alert_manager = None

    # ==========================================================
    # CLEANUP
    # ==========================================================

    def cleanup(self) -> None:
        """
        Cleanup controller resources.
        """

        self.logger.info(
            "Cleaning DashboardController..."
        )

        self.stop_services()

        self.disconnect_signals()

        self.release_resources()

    # ==========================================================
    # SHUTDOWN
    # ==========================================================

    def shutdown(self) -> None:
        """
        Shutdown dashboard controller.
        """

        self.logger.info(
            "DashboardController shutdown initiated."
        )

        try:

            self.cleanup()

        except Exception as ex:

            self.logger.exception(ex)

    # ==========================================================
    # CLOSE DASHBOARD
    # ==========================================================

    def close_dashboard(self) -> None:
        """
        Close dashboard window.
        """

        try:

            if self.dashboard is not None:

                self.dashboard.close()

        except Exception as ex:

            self.logger.exception(ex)

    # ==========================================================
    # APPLICATION EXIT
    # ==========================================================

    def exit_application(self) -> None:
        """
        Perform complete application exit.
        """

        self.close_dashboard()

        self.shutdown()

    # ==========================================================
    # IS ACTIVE
    # ==========================================================

    def is_active(self) -> bool:
        """
        Check whether the controller is active.
        """

        return self.dashboard is not None
        # ==========================================================
    # RESET CONTROLLER
    # ==========================================================

    def reset(self) -> None:
        """
        Reset the controller state.
        """

        self.logger.info(
            "Resetting DashboardController..."
        )

        self.reset_statistics()

        self.refresh_dashboard()

    # ==========================================================
    # RESTART
    # ==========================================================

    def restart(self) -> None:
        """
        Restart dashboard services.
        """

        self.logger.info(
            "Restarting DashboardController..."
        )

        self.stop_auto_refresh()

        self.start_auto_refresh()

        self.refresh_dashboard()

    # ==========================================================
    # VERSION
    # ==========================================================

    @classmethod
    def version(cls) -> str:
        """
        Return controller version.
        """

        return cls.VERSION

    # ==========================================================
    # BUILD INFO
    # ==========================================================

    @staticmethod
    def build_info() -> Dict[str, str]:
        """
        Return build information.
        """

        return {

            "controller": "DashboardController",

            "version": DashboardController.VERSION,

            "framework": "PySide6",

            "application": "StockVersity Scanner Pro",

        }

    # ==========================================================
    # CONTEXT MANAGER
    # ==========================================================

    def __enter__(self):
        """
        Context manager entry.
        """

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        """
        Context manager exit.
        """

        self.shutdown()

        return False

    # ==========================================================
    # FACTORY
    # ==========================================================

    @classmethod
    def create(
        cls,
        dashboard,
        data_manager,
        market_analyzer,
        screener,
        alert_manager,
    ):
        """
        Create a DashboardController instance.
        """

        return cls(
            dashboard=dashboard,
            data_manager=data_manager,
            market_analyzer=market_analyzer,
            screener=screener,
            alert_manager=alert_manager,
        )


# ==========================================================
# FACTORY FUNCTION
# ==========================================================

def create_dashboard_controller(
    dashboard,
    data_manager,
    market_analyzer,
    screener,
    alert_manager,
) -> DashboardController:
    """
    Create a DashboardController.
    """

    return DashboardController(
        dashboard=dashboard,
        data_manager=data_manager,
        market_analyzer=market_analyzer,
        screener=screener,
        alert_manager=alert_manager,
    )


# ==========================
# END OF FILE
# ==========================