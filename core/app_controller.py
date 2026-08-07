"""
=========================================================
                StockVersity Scanner Pro
                     Powered by AI
=========================================================

Central Application Controller

This controller manages:

â€¢ Dashboard
â€¢ Market Dashboard
â€¢ AI Dashboard
â€¢ Intraday Scanner
â€¢ Swing Scanner
â€¢ Positional Scanner
â€¢ Market Data
â€¢ Scanner Engine
â€¢ AI Ranking
â€¢ Export Manager
â€¢ Background Workers
â€¢ Refresh Timers

"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
    QThread,
    QTimer,
)

# ---------------------------------------------------------
# Backend Services
# ---------------------------------------------------------

from backend.services.nse_service import NseService
from backend.services.yahoo_service import YahooFinanceService
try:
    from backend.services.option_chain_service import OptionChainService
except ImportError:
    OptionChainService = None
try:
    from backend.services.market_breadth_service import MarketBreadthService
except ImportError:
    MarketBreadthService = None
try:
    from backend.services.sector_service import SectorService
except ImportError:
    SectorService = None
try:
    from backend.services.fii_dii_service import FIIDIIService
except ImportError:
    FIIDIIService = None

# ---------------------------------------------------------
# Scanner Engine
# ---------------------------------------------------------

from core.scanner.intraday import IntradayScanner
from core.scanner.swing_scanner import SwingScanner
from core.scanner.positional_Scanner import PositionalScanner

# ---------------------------------------------------------
# AI Engine
# ---------------------------------------------------------

from backend.ai.opportunity_engine import OpportunityEngine
from backend.ai.market_sentiment_engine import MarketSentimentEngine

# ---------------------------------------------------------
# Export
# ---------------------------------------------------------

try:
    from backend.services.export_service import ExportService
except ImportError:
    ExportService = None


class AppController(QObject):

    # =====================================================
    # SIGNALS
    # =====================================================

    marketUpdated = Signal(dict)

    scannersUpdated = Signal(dict)

    dashboardUpdated = Signal(dict)

    aiUpdated = Signal(dict)

    errorOccurred = Signal(str)

    statusChanged = Signal(str)

    finished = Signal()

    # =====================================================
    # INIT
    # =====================================================

    def __init__(self, parent=None):

        super().__init__(parent)

        #
        # Services
        #

        self.nse = NseService()

        self.yahoo = YahooFinanceService()

        self.option_chain = OptionChainService()

        self.market_breadth = MarketBreadthService()

        self.sector_service = SectorService()

        self.fii_dii = FIIDIIService()

        #
        # Scanner Engines
        #

        self.intraday = IntradayScanner()

        self.swing = SwingScanner()

        self.positional = PositionalScanner()

        #
        # AI
        #

        self.ai_engine = OpportunityEngine()

        self.sentiment = MarketSentimentEngine()

        #
        # Export
        #

        self.exporter = ExportService()

        #
        # Cache
        #

        self.market_cache = {}

        self.ai_cache = {}

        self.scanner_cache = {}

        self.dashboard_cache = {}

        #
        # Timers
        #

        self.refresh_timer = QTimer()

        self.refresh_timer.setInterval(30000)

        self.refresh_timer.timeout.connect(

            self.refresh_everything

        )

        #
        # State
        #

        self.running = False

        self.last_refresh = None

        self.market_status = "Closed"

        self.current_sector = ""

        self.current_theme = "Dark"

        self.version = "4.0"

        self.statusChanged.emit(

            "Application Controller Initialized"

        )
            # =====================================================
    # START CONTROLLER
    # =====================================================

    def start(self):

        if self.running:
            return

        self.running = True

        self.statusChanged.emit(

            "Starting StockVersity Services..."

        )

        self.refresh_timer.start()

        self.refresh_everything()

    # =====================================================
    # STOP CONTROLLER
    # =====================================================

    def stop(self):

        if not self.running:
            return

        self.running = False

        self.refresh_timer.stop()

        self.statusChanged.emit(

            "Services Stopped"

        )

        self.finished.emit()

    # =====================================================
    # REFRESH EVERYTHING
    # =====================================================

    @Slot()
    def refresh_everything(self):

        try:

            self.statusChanged.emit(

                "Refreshing Market Data..."

            )

            self.refresh_market()

            # FII/DII is intentionally refreshed separately.
            # A failure in Yahoo/NSE breadth/sectors must not
            # prevent Institutional Flow from updating.
            self.refresh_institutional_data()

            self.refresh_dashboards()

            self.refresh_scanners()

            self.refresh_ai()

            self.last_refresh = datetime.now()

            self.statusChanged.emit(

                "Refresh Completed"

            )

        except Exception as e:

            self.errorOccurred.emit(

                str(e)

            )

    # =====================================================
    # REFRESH MARKET
    # =====================================================

    def refresh_market(self):

        try:

            #
            # Live Indices
            #

            nifty = self.yahoo.get_nifty()

            banknifty = self.yahoo.get_banknifty()

            gold = self.yahoo.get_gold()

            usd = self.yahoo.get_usdinr()

            crude = self.yahoo.get_brent()

            vix = self.nse.get_india_vix()

            #
            # Breadth
            #

            breadth = self.market_breadth.fetch()

            #
            # Sector Rotation
            #

            sectors = self.sector_service.fetch()

            #
            # FII DII
            #

            fii = self.fii_dii.fetch()

            #
            # Cache
            #

            self.market_cache = {

                "nifty": nifty,

                "banknifty": banknifty,

                "gold": gold,

                "usd_inr": usd,

                "crude": crude,

                "vix": vix,

                "breadth": breadth,

                "sector": sectors,

                "institutional": fii,

                "updated": datetime.now(),

            }

            #
            # Market Status
            #

            hour = datetime.now().hour
            minute = datetime.now().minute

            current = hour * 60 + minute

            if 555 <= current <= 930:

                self.market_status = "OPEN"

            else:

                self.market_status = "CLOSED"

            self.market_cache["status"] = (

                self.market_status

            )

            self.marketUpdated.emit(

                self.market_cache

            )

        except Exception as e:

            self.errorOccurred.emit(

                str(e)

            )

    # =====================================================
    # REFRESH INSTITUTIONAL DATA
    # =====================================================

    def refresh_institutional_data(self):
        """
        Refresh FII/DII independently from the main market
        refresh so another provider failure cannot prevent
        Institutional Flow from updating.
        """

        try:

            service = getattr(
                self,
                "fii_dii",
                None,
            )

            if service is None:
                return

            data = service.fetch()

            if not isinstance(
                data,
                dict,
            ):
                return

            # Do not replace a valid cached session with an
            # unavailable response.
            if not data.get(
                "available",
                False,
            ):
                return

            if not isinstance(
                self.market_cache,
                dict,
            ):
                self.market_cache = {}

            self.market_cache[
                "institutional"
            ] = data

        except Exception as e:

            try:
                self.errorOccurred.emit(
                    f"Institutional refresh: {e}"
                )

            except Exception:
                pass


    # =====================================================
    # REFRESH DASHBOARDS
    # =====================================================

    def refresh_dashboards(self):

        try:

            dashboard = {

                "market":

                    self.market_cache,

                "updated":

                    datetime.now(),

                "status":

                    self.market_status,

            }

            self.dashboard_cache = dashboard

            self.dashboardUpdated.emit(

                dashboard

            )

        except Exception as e:

            self.errorOccurred.emit(

                str(e)

            )

    # =====================================================
    # REFRESH SCANNERS
    # =====================================================

    def refresh_scanners(self):

        try:

            intraday = self.intraday.scan()

            swing = self.swing.scan()

            positional = self.positional.scan()

            self.scanner_cache = {

                "intraday": intraday,

                "swing": swing,

                "positional": positional,

                "updated": datetime.now(),

            }

            self.scannersUpdated.emit(

                self.scanner_cache

            )

        except Exception as e:

            self.errorOccurred.emit(

                str(e)

            )

    # =====================================================
    # REFRESH AI
    # =====================================================

    def refresh_ai(self):

        try:

            sentiment = self.sentiment.analyze(

                self.market_cache

            )

            opportunities = (

                self.ai_engine.rank(

                    self.scanner_cache

                )

            )

            self.ai_cache = {

                "sentiment": sentiment,

                "opportunities": opportunities,

                "updated": datetime.now(),

            }

            self.aiUpdated.emit(

                self.ai_cache

            )

        except Exception as e:

            self.errorOccurred.emit(

                str(e)

            )

                # =====================================================
    # START CONTROLLER
    # =====================================================

    def start(self):

        if self.running:
            return

        self.running = True

        self.statusChanged.emit(

            "Starting StockVersity Services..."

        )

        self.refresh_timer.start()

        self.refresh_everything()

    # =====================================================
    # STOP CONTROLLER
    # =====================================================

    def stop(self):

        if not self.running:
            return

        self.running = False

        self.refresh_timer.stop()

        self.statusChanged.emit(

            "Services Stopped"

        )

        self.finished.emit()

    # =====================================================
    # REFRESH EVERYTHING
    # =====================================================

    @Slot()
    def refresh_everything(self):

        try:

            self.statusChanged.emit(

                "Refreshing Market Data..."

            )

            self.refresh_market()

            # FII/DII is intentionally refreshed separately.
            # A failure in Yahoo/NSE breadth/sectors must not
            # prevent Institutional Flow from updating.
            self.refresh_institutional_data()

            self.refresh_dashboards()

            self.refresh_scanners()

            self.refresh_ai()

            self.last_refresh = datetime.now()

            self.statusChanged.emit(

                "Refresh Completed"

            )

        except Exception as e:

            self.errorOccurred.emit(

                str(e)

            )

    # =====================================================
    # REFRESH MARKET
    # =====================================================

    def refresh_market(self):

        try:

            #
            # Live Indices
            #

            nifty = self.yahoo.get_nifty()

            banknifty = self.yahoo.get_banknifty()

            gold = self.yahoo.get_gold()

            usd = self.yahoo.get_usdinr()

            crude = self.yahoo.get_brent()

            vix = self.nse.get_india_vix()

            #
            # Breadth
            #

            breadth = self.market_breadth.fetch()

            #
            # Sector Rotation
            #

            sectors = self.sector_service.fetch()

            #
            # FII DII
            #

            fii = self.fii_dii.fetch()

            #
            # Cache
            #

            self.market_cache = {

                "nifty": nifty,

                "banknifty": banknifty,

                "gold": gold,

                "usd_inr": usd,

                "crude": crude,

                "vix": vix,

                "breadth": breadth,

                "sector": sectors,

                "institutional": fii,

                "updated": datetime.now(),

            }

            #
            # Market Status
            #

            hour = datetime.now().hour
            minute = datetime.now().minute

            current = hour * 60 + minute

            if 555 <= current <= 930:

                self.market_status = "OPEN"

            else:

                self.market_status = "CLOSED"

            self.market_cache["status"] = (

                self.market_status

            )

            self.marketUpdated.emit(

                self.market_cache

            )

        except Exception as e:

            self.errorOccurred.emit(

                str(e)

            )

    # =====================================================
    # REFRESH DASHBOARDS
    # =====================================================

    def refresh_dashboards(self):

        try:

            dashboard = {

                "market":

                    self.market_cache,

                "updated":

                    datetime.now(),

                "status":

                    self.market_status,

            }

            self.dashboard_cache = dashboard

            self.dashboardUpdated.emit(

                dashboard

            )

        except Exception as e:

            self.errorOccurred.emit(

                str(e)

            )

    # =====================================================
    # REFRESH SCANNERS
    # =====================================================

    def refresh_scanners(self):

        try:

            intraday = self.intraday.scan()

            swing = self.swing.scan()

            positional = self.positional.scan()

            self.scanner_cache = {

                "intraday": intraday,

                "swing": swing,

                "positional": positional,

                "updated": datetime.now(),

            }

            self.scannersUpdated.emit(

                self.scanner_cache

            )

        except Exception as e:

            self.errorOccurred.emit(

                str(e)

            )

    # =====================================================
    # REFRESH AI
    # =====================================================

    def refresh_ai(self):

        try:

            sentiment = self.sentiment.analyze(

                self.market_cache

            )

            opportunities = (

                self.ai_engine.rank(

                    self.scanner_cache

                )

            )

            self.ai_cache = {

                "sentiment": sentiment,

                "opportunities": opportunities,

                "updated": datetime.now(),

            }

            self.aiUpdated.emit(

                self.ai_cache

            )

        except Exception as e:

            self.errorOccurred.emit(

                str(e)

            )
                # =====================================================
    # GETTERS
    # =====================================================

    def get_market_data(self):

        """Return latest market cache."""

        return self.market_cache.copy()

    # -----------------------------------------------------

    def get_dashboard_data(self):

        """Return dashboard cache."""

        return self.dashboard_cache.copy()

    # -----------------------------------------------------

    def get_scanner_data(self):

        """Return scanner cache."""

        return self.scanner_cache.copy()

    # -----------------------------------------------------

    def get_ai_data(self):

        """Return AI cache."""

        return self.ai_cache.copy()

    # =====================================================
    # CACHE MANAGEMENT
    # =====================================================

    def clear_cache(self):

        self.market_cache.clear()

        self.dashboard_cache.clear()

        self.scanner_cache.clear()

        self.ai_cache.clear()

        self.statusChanged.emit(

            "Application cache cleared."

        )

    # -----------------------------------------------------

    def cache_statistics(self):

        return {

            "market_items":

                len(self.market_cache),

            "dashboard_items":

                len(self.dashboard_cache),

            "scanner_items":

                len(self.scanner_cache),

            "ai_items":

                len(self.ai_cache),

            "last_refresh":

                self.last_refresh,

        }

    # =====================================================
    # MANUAL REFRESH
    # =====================================================

    def refresh_market_only(self):

        self.refresh_market()

    # -----------------------------------------------------

    def refresh_dashboard_only(self):

        self.refresh_dashboards()

    # -----------------------------------------------------

    def refresh_scanners_only(self):

        self.refresh_scanners()

    # -----------------------------------------------------

    def refresh_ai_only(self):

        self.refresh_ai()

    # =====================================================
    # EXPORTS
    # =====================================================

    def export_intraday(self, filename):

        return self.exporter.export(

            filename,

            self.scanner_cache.get(

                "intraday",

                []

            )

        )

    # -----------------------------------------------------

    def export_swing(self, filename):

        return self.exporter.export(

            filename,

            self.scanner_cache.get(

                "swing",

                []

            )

        )

    # -----------------------------------------------------

    def export_positional(self, filename):

        return self.exporter.export(

            filename,

            self.scanner_cache.get(

                "positional",

                []

            )

        )

    # -----------------------------------------------------

    def export_ai(self, filename):

        return self.exporter.export(

            filename,

            self.ai_cache.get(

                "opportunities",

                []

            )

        )

    # =====================================================
    # MARKET SUMMARY
    # =====================================================

    def market_summary(self):

        return {

            "status":

                self.market_status,

            "nifty":

                self.market_cache.get(

                    "nifty"

                ),

            "banknifty":

                self.market_cache.get(

                    "banknifty"

                ),

            "vix":

                self.market_cache.get(

                    "vix"

                ),

            "breadth":

                self.market_cache.get(

                    "breadth"

                ),

            "sector":

                self.market_cache.get(

                    "sector"

                ),

            "institutional":

                self.market_cache.get(

                    "institutional"

                ),

            "updated":

                self.market_cache.get(

                    "updated"

                ),

        }

    # =====================================================
    # AI SUMMARY
    # =====================================================

    def ai_summary(self):

        return {

            "sentiment":

                self.ai_cache.get(

                    "sentiment"

                ),

            "top_opportunities":

                self.ai_cache.get(

                    "opportunities"

                ),

            "updated":

                self.ai_cache.get(

                    "updated"

                ),

        }

    # =====================================================
    # APPLICATION HEALTH
    # =====================================================

    def health_status(self):

        return {

            "running":

                self.running,

            "timer_active":

                self.refresh_timer.isActive(),

            "last_refresh":

                self.last_refresh,

            "market_status":

                self.market_status,

            "version":

                self.version,

        }
        # =====================================================
    # BACKGROUND WORKER MANAGEMENT
    # =====================================================

    def initialize_workers(self):

        """Initialize background worker thread."""

        self.worker_thread = QThread()

        self.worker_thread.setObjectName(

            "StockVersityWorker"

        )

        self.statusChanged.emit(

            "Background worker initialized."

        )

    # -----------------------------------------------------

    def start_worker(self):

        if not hasattr(self, "worker_thread"):
            self.initialize_workers()

        if not self.worker_thread.isRunning():

            self.worker_thread.start()

            self.statusChanged.emit(

                "Background worker started."

            )

    # -----------------------------------------------------

    def stop_worker(self):

        if hasattr(self, "worker_thread"):

            if self.worker_thread.isRunning():

                self.worker_thread.quit()

                self.worker_thread.wait(5000)

                self.statusChanged.emit(

                    "Background worker stopped."

                )

    # =====================================================
    # SERVICE HEALTH CHECK
    # =====================================================

    def check_services(self):

        services = {

            "NSE": self.nse,

            "Yahoo": self.yahoo,

            "Options": self.option_chain,

            "Breadth": self.market_breadth,

            "Sector": self.sector_service,

            "FII/DII": self.fii_dii,

        }

        result = {}

        for name, service in services.items():

            try:

                if hasattr(service, "health_check"):

                    result[name] = service.health_check()

                else:

                    result[name] = True

            except Exception:

                result[name] = False

        return result

    # =====================================================
    # RETRY LOGIC
    # =====================================================

    def retry_operation(

        self,

        callback,

        retries=3

    ):

        last_error = None

        for attempt in range(retries):

            try:

                return callback()

            except Exception as e:

                last_error = e

                self.statusChanged.emit(

                    f"Retry {attempt + 1}/{retries}"

                )

        if last_error:

            self.errorOccurred.emit(

                str(last_error)

            )

        return None

    # =====================================================
    # SAFE EXECUTION
    # =====================================================

    def safe_execute(

        self,

        callback,

        default=None

    ):

        try:

            return callback()

        except Exception as e:

            self.errorOccurred.emit(

                str(e)

            )

            return default

    # =====================================================
    # PERFORMANCE METRICS
    # =====================================================

    def performance_metrics(self):

        return {

            "running":

                self.running,

            "refresh_timer":

                self.refresh_timer.isActive(),

            "refresh_interval":

                self.refresh_timer.interval(),

            "last_refresh":

                self.last_refresh,

            "market_cache":

                len(self.market_cache),

            "scanner_cache":

                len(self.scanner_cache),

            "ai_cache":

                len(self.ai_cache),

            "dashboard_cache":

                len(self.dashboard_cache),

        }

    # =====================================================
    # SCHEDULER
    # =====================================================

    def set_refresh_interval(

        self,

        seconds

    ):

        seconds = max(5, int(seconds))

        self.refresh_timer.setInterval(

            seconds * 1000

        )

        self.statusChanged.emit(

            f"Refresh interval set to {seconds} seconds."

        )

    # -----------------------------------------------------

    def refresh_interval(self):

        return (

            self.refresh_timer.interval()

            // 1000

        )

    # =====================================================
    # ERROR LOGGER
    # =====================================================

    def log_error(

        self,

        error

    ):

        message = (

            f"[{datetime.now()}] "

            f"{error}"

        )

        print(message)

        self.errorOccurred.emit(

            str(error)

        )

    # =====================================================
    # CONNECTION STATUS
    # =====================================================

    def connection_status(self):

        health = self.check_services()

        online = sum(

            1 for status in health.values()

            if status

        )

        return {

            "services":

                health,

            "online":

                online,

            "total":

                len(health),

        }
        # =====================================================
    # MARKET ALERTS
    # =====================================================

    def initialize_alerts(self):

        self.alerts = []

        self.alert_history = []

    # -----------------------------------------------------

    def add_alert(

        self,

        title,

        message,

        level="INFO"

    ):

        alert = {

            "title": title,

            "message": message,

            "level": level,

            "time": datetime.now(),

        }

        self.alerts.append(alert)

        self.alert_history.append(alert)

        self.statusChanged.emit(message)

    # -----------------------------------------------------

    def clear_alerts(self):

        self.alerts.clear()

    # -----------------------------------------------------

    def get_alerts(self):

        return list(self.alerts)

    # =====================================================
    # NOTIFICATION CENTER
    # =====================================================

    def notify(

        self,

        message,

        level="INFO"

    ):

        self.statusChanged.emit(message)

        self.add_alert(

            "Notification",

            message,

            level

        )

    # =====================================================
    # EVENT QUEUE
    # =====================================================

    def initialize_event_queue(self):

        self.event_queue = []

    # -----------------------------------------------------

    def push_event(

        self,

        event_name,

        payload=None

    ):

        self.event_queue.append({

            "event": event_name,

            "payload": payload,

            "time": datetime.now()

        })

    # -----------------------------------------------------

    def pop_event(self):

        if not self.event_queue:

            return None

        return self.event_queue.pop(0)

    # -----------------------------------------------------

    def pending_events(self):

        return len(self.event_queue)

    # =====================================================
    # AI OPPORTUNITY MANAGER
    # =====================================================

    def top_opportunities(

        self,

        limit=10

    ):

        opportunities = self.ai_cache.get(

            "opportunities",

            []

        )

        return opportunities[:limit]

    # -----------------------------------------------------

    def best_intraday_trade(self):

        trades = self.scanner_cache.get(

            "intraday",

            []

        )

        if not trades:

            return None

        return trades[0]

    # -----------------------------------------------------

    def best_swing_trade(self):

        trades = self.scanner_cache.get(

            "swing",

            []

        )

        if not trades:

            return None

        return trades[0]

    # -----------------------------------------------------

    def best_positional_trade(self):

        trades = self.scanner_cache.get(

            "positional",

            []

        )

        if not trades:

            return None

        return trades[0]

    # =====================================================
    # SCANNER RANKING
    # =====================================================

    def ranked_scanners(self):

        return {

            "intraday":

                self.scanner_cache.get(

                    "intraday",

                    []

                ),

            "swing":

                self.scanner_cache.get(

                    "swing",

                    []

                ),

            "positional":

                self.scanner_cache.get(

                    "positional",

                    []

                ),

        }

    # =====================================================
    # CACHE CLEANUP
    # =====================================================

    def cleanup_cache(self):

        if len(self.alert_history) > 1000:

            self.alert_history = (

                self.alert_history[-500:]

            )

        self.statusChanged.emit(

            "Cache cleanup completed."

        )

    # =====================================================
    # CONTROLLER STATISTICS
    # =====================================================

    def statistics(self):

        return {

            "market_cache":

                len(self.market_cache),

            "scanner_cache":

                len(self.scanner_cache),

            "dashboard_cache":

                len(self.dashboard_cache),

            "ai_cache":

                len(self.ai_cache),

            "alerts":

                len(self.alerts),

            "event_queue":

                len(getattr(

                    self,

                    "event_queue",

                    []

                )),

            "running":

                self.running,

            "last_refresh":

                self.last_refresh,

        }

    # =====================================================
    # MARKET SNAPSHOT
    # =====================================================

    def market_snapshot(self):

        return {

            "market":

                self.market_cache,

            "scanners":

                self.scanner_cache,

            "ai":

                self.ai_cache,

            "generated":

                datetime.now(),

        }
        # =====================================================
    # HEARTBEAT
    # =====================================================

    def initialize_heartbeat(self):

        self.heartbeat_timer = QTimer()

        self.heartbeat_timer.setInterval(10000)

        self.heartbeat_timer.timeout.connect(

            self.heartbeat

        )

    # -----------------------------------------------------

    def start_heartbeat(self):

        if not hasattr(self, "heartbeat_timer"):

            self.initialize_heartbeat()

        if not self.heartbeat_timer.isActive():

            self.heartbeat_timer.start()

    # -----------------------------------------------------

    def stop_heartbeat(self):

        if hasattr(self, "heartbeat_timer"):

            self.heartbeat_timer.stop()

    # -----------------------------------------------------

    def heartbeat(self):

        self.last_heartbeat = datetime.now()

        self.statusChanged.emit(

            "Heartbeat OK"

        )

    # =====================================================
    # MARKET SESSION
    # =====================================================

    def market_session(self):

        now = datetime.now()

        minutes = now.hour * 60 + now.minute

        #
        # NSE Timings
        #

        if 540 <= minutes < 555:

            return "PRE_OPEN"

        if 555 <= minutes <= 930:

            return "LIVE"

        if 930 < minutes <= 960:

            return "POST_CLOSE"

        return "CLOSED"

    # -----------------------------------------------------

    def is_market_open(self):

        return self.market_session() == "LIVE"

    # -----------------------------------------------------

    def is_pre_open(self):

        return self.market_session() == "PRE_OPEN"

    # -----------------------------------------------------

    def is_post_close(self):

        return self.market_session() == "POST_CLOSE"

    # =====================================================
    # BACKGROUND TASK SCHEDULER
    # =====================================================

    def initialize_scheduler(self):

        self.scheduler = QTimer()

        self.scheduler.setInterval(

            60000

        )

        self.scheduler.timeout.connect(

            self.run_scheduled_tasks

        )

    # -----------------------------------------------------

    def start_scheduler(self):

        if not hasattr(self, "scheduler"):

            self.initialize_scheduler()

        if not self.scheduler.isActive():

            self.scheduler.start()

    # -----------------------------------------------------

    def stop_scheduler(self):

        if hasattr(self, "scheduler"):

            self.scheduler.stop()

    # -----------------------------------------------------

    def run_scheduled_tasks(self):

        self.cleanup_cache()

        self.check_connections()

    # =====================================================
    # API RATE LIMITER
    # =====================================================

    def initialize_rate_limiter(self):

        self.api_calls = 0

        self.api_window = datetime.now()

        self.api_limit = 100

    # -----------------------------------------------------

    def api_allowed(self):

        elapsed = (

            datetime.now()

            - self.api_window

        ).seconds

        if elapsed >= 60:

            self.api_calls = 0

            self.api_window = datetime.now()

        if self.api_calls >= self.api_limit:

            return False

        self.api_calls += 1

        return True

    # =====================================================
    # CONNECTION CHECK
    # =====================================================

    def check_connections(self):

        health = self.check_services()

        offline = [

            name

            for name, ok

            in health.items()

            if not ok

        ]

        if offline:

            self.notify(

                "Offline Services: "

                + ", ".join(offline),

                "WARNING"

            )

    # =====================================================
    # CONNECTION RECOVERY
    # =====================================================

    def recover_connections(self):

        services = self.check_services()

        recovered = []

        for name, state in services.items():

            if state:

                continue

            recovered.append(name)

        if recovered:

            self.notify(

                "Recovery Attempted: "

                + ", ".join(recovered),

                "INFO"

            )

    # =====================================================
    # FAILOVER
    # =====================================================

    def enable_failover(self):

        self.failover_enabled = True

    # -----------------------------------------------------

    def disable_failover(self):

        self.failover_enabled = False

    # -----------------------------------------------------

    def failover_status(self):

        return getattr(

            self,

            "failover_enabled",

            False

        )

    # =====================================================
    # THREAD SAFETY
    # =====================================================

    def controller_locked(self):

        return getattr(

            self,

            "_busy",

            False

        )

    # -----------------------------------------------------

    def lock(self):

        self._busy = True

    # -----------------------------------------------------

    def unlock(self):

        self._busy = False

    # -----------------------------------------------------

    def safe_refresh(self):

        if self.controller_locked():

            return

        self.lock()

        try:

            self.refresh_everything()

        finally:

            self.unlock()
                # =====================================================
    # AI SCORING ENGINE
    # =====================================================

    def calculate_stock_score(self, stock):

        """
        Calculates a professional AI score (0-100)
        """

        score = 0

        score += self.momentum_score(stock)
        score += self.relative_strength_score(stock)
        score += self.volume_score(stock)
        score += self.trend_score(stock)
        score += self.breakout_score(stock)

        return min(100, round(score, 2))

    # =====================================================
    # MOMENTUM SCORE
    # =====================================================

    def momentum_score(self, stock):

        score = 0

        score += stock.get("rsi_score", 0)
        score += stock.get("macd_score", 0)
        score += stock.get("adx_score", 0)

        return min(score, 20)

    # =====================================================
    # RELATIVE STRENGTH SCORE
    # =====================================================

    def relative_strength_score(self, stock):

        return min(

            stock.get(

                "relative_strength",

                0

            ),

            15

        )

    # =====================================================
    # VOLUME SCORE
    # =====================================================

    def volume_score(self, stock):

        return min(

            stock.get(

                "volume_score",

                0

            ),

            20

        )

    # =====================================================
    # TREND SCORE
    # =====================================================

    def trend_score(self, stock):

        return min(

            stock.get(

                "trend_score",

                0

            ),

            20

        )

    # =====================================================
    # BREAKOUT SCORE
    # =====================================================

    def breakout_score(self, stock):

        return min(

            stock.get(

                "breakout_score",

                0

            ),

            25

        )

    # =====================================================
    # RANK STOCKS
    # =====================================================

    def rank_stocks(self, stocks):

        ranked = []

        for stock in stocks:

            stock["ai_score"] = (

                self.calculate_stock_score(

                    stock

                )

            )

            ranked.append(stock)

        ranked.sort(

            key=lambda x: x["ai_score"],

            reverse=True

        )

        return ranked

    # =====================================================
    # SECTOR STRENGTH
    # =====================================================

    def calculate_sector_strength(

        self,

        sector_data

    ):

        if not sector_data:

            return 0

        total = sum(

            item.get(

                "strength",

                0

            )

            for item in sector_data

        )

        return round(

            total /

            len(sector_data),

            2

        )

    # =====================================================
    # MARKET MOMENTUM
    # =====================================================

    def market_momentum(self):

        try:

            return self.market_cache.get(

                "breadth",

                {}

            ).get(

                "momentum",

                0

            )

        except Exception:

            return 0

    # =====================================================
    # RISK SCORE
    # =====================================================

    def risk_score(self, stock):

        score = 100

        score -= stock.get(

            "volatility",

            0

        )

        score -= stock.get(

            "drawdown",

            0

        )

        return max(

            0,

            round(score, 2)

        )

    # =====================================================
    # REWARD SCORE
    # =====================================================

    def reward_score(self, stock):

        return min(

            stock.get(

                "reward",

                0

            ),

            100

        )

    # =====================================================
    # RISK / REWARD
    # =====================================================

    def risk_reward_ratio(

        self,

        stock

    ):

        risk = max(

            stock.get(

                "risk",

                1

            ),

            1

        )

        reward = stock.get(

            "reward",

            0

        )

        return round(

            reward / risk,

            2

        )

    # =====================================================
    # AI OPPORTUNITY LIST
    # =====================================================

    def ai_opportunities(

        self,

        stocks

    ):

        ranked = self.rank_stocks(

            stocks

        )

        opportunities = []

        for stock in ranked:

            stock["risk_score"] = (

                self.risk_score(

                    stock

                )

            )

            stock["reward_score"] = (

                self.reward_score(

                    stock

                )

            )

            stock["rr"] = (

                self.risk_reward_ratio(

                    stock

                )

            )

            opportunities.append(stock)

        return opportunities

    # =====================================================
    # TOP AI PICKS
    # =====================================================

    def top_ai_picks(

        self,

        limit=10

    ):

        stocks = self.ai_cache.get(

            "opportunities",

            []

        )

        return stocks[:limit]
        # =====================================================
    # INSTITUTIONAL ACTIVITY
    # =====================================================

    def institutional_summary(self):

        return self.market_cache.get(

            "institutional",

            {}

        )

    # -----------------------------------------------------

    def fii_status(self):

        data = self.institutional_summary()

        return data.get(

            "fii",

            {}

        )

    # -----------------------------------------------------

    def dii_status(self):

        data = self.institutional_summary()

        return data.get(

            "dii",

            {}

        )

    # -----------------------------------------------------

    def smart_money_direction(self):

        fii = self.fii_status()

        dii = self.dii_status()

        fii_net = fii.get("net", 0)
        dii_net = dii.get("net", 0)

        total = fii_net + dii_net

        if total > 0:
            return "Bullish"

        if total < 0:
            return "Bearish"

        return "Neutral"

    # =====================================================
    # OPTIONS ANALYTICS
    # =====================================================

    def option_summary(self):

        try:

            return self.option_chain.fetch()

        except Exception:

            return {}

    # -----------------------------------------------------

    def put_call_ratio(self):

        option = self.option_summary()

        return option.get(

            "pcr",

            1.0

        )

    # -----------------------------------------------------

    def max_call_oi(self):

        option = self.option_summary()

        return option.get(

            "max_call_oi",

            {}

        )

    # -----------------------------------------------------

    def max_put_oi(self):

        option = self.option_summary()

        return option.get(

            "max_put_oi",

            {}

        )

    # -----------------------------------------------------

    def option_sentiment(self):

        pcr = self.put_call_ratio()

        if pcr > 1.20:
            return "Bullish"

        if pcr < 0.80:
            return "Bearish"

        return "Neutral"

    # =====================================================
    # SECTOR ROTATION
    # =====================================================

    def sector_strength(self):

        sectors = self.market_cache.get(

            "sector",

            []

        )

        return sorted(

            sectors,

            key=lambda x: x.get(

                "strength",

                0

            ),

            reverse=True

        )

    # -----------------------------------------------------

    def strongest_sector(self):

        sectors = self.sector_strength()

        if not sectors:
            return None

        return sectors[0]

    # -----------------------------------------------------

    def weakest_sector(self):

        sectors = self.sector_strength()

        if not sectors:
            return None

        return sectors[-1]

    # =====================================================
    # MARKET BREADTH
    # =====================================================

    def breadth_summary(self):

        return self.market_cache.get(

            "breadth",

            {}

        )

    # -----------------------------------------------------

    def breadth_score(self):

        breadth = self.breadth_summary()

        advances = breadth.get(

            "advances",

            0

        )

        declines = breadth.get(

            "declines",

            0

        )

        total = advances + declines

        if total == 0:
            return 50

        return round(

            advances * 100 / total,

            2

        )

    # =====================================================
    # FEAR & GREED INDEX
    # =====================================================

    def fear_greed_index(self):

        score = 50

        #
        # Breadth
        #

        breadth = self.breadth_score()

        score += (breadth - 50) * 0.30

        #
        # PCR
        #

        pcr = self.put_call_ratio()

        score += (pcr - 1.0) * 20

        #
        # Smart Money
        #

        direction = self.smart_money_direction()

        if direction == "Bullish":
            score += 10

        elif direction == "Bearish":
            score -= 10

        score = max(

            0,

            min(

                100,

                round(score, 2)

            )

        )

        return score

    # -----------------------------------------------------

    def market_sentiment(self):

        score = self.fear_greed_index()

        if score >= 75:
            return "Extreme Greed"

        if score >= 60:
            return "Greed"

        if score >= 45:
            return "Neutral"

        if score >= 25:
            return "Fear"

        return "Extreme Fear"

    # =====================================================
    # MARKET ANALYTICS
    # =====================================================

    def analytics(self):

        return {

            "fear_greed":

                self.fear_greed_index(),

            "market_sentiment":

                self.market_sentiment(),

            "smart_money":

                self.smart_money_direction(),

            "breadth":

                self.breadth_summary(),

            "breadth_score":

                self.breadth_score(),

            "pcr":

                self.put_call_ratio(),

            "option_sentiment":

                self.option_sentiment(),

            "strongest_sector":

                self.strongest_sector(),

            "weakest_sector":

                self.weakest_sector(),

            "institutional":

                self.institutional_summary(),

            "generated":

                datetime.now(),

        }
        # =====================================================
    # USER PREFERENCES
    # =====================================================

    def initialize_preferences(self):

        self.preferences = {

            "theme": "Dark",

            "refresh_interval": 30,

            "auto_refresh": True,

            "notifications": True,

            "market_alerts": True,

            "language": "English",

            "default_page": "Dashboard",

            "export_format": "xlsx",

        }

    # -----------------------------------------------------

    def get_preference(self, key, default=None):

        return self.preferences.get(

            key,

            default

        )

    # -----------------------------------------------------

    def set_preference(

        self,

        key,

        value

    ):

        self.preferences[key] = value

        self.statusChanged.emit(

            f"Preference updated : {key}"

        )

    # =====================================================
    # SESSION MANAGEMENT
    # =====================================================

    def create_session(self):

        self.session = {

            "started": datetime.now(),

            "last_activity": datetime.now(),

            "current_page": "Dashboard",

        }

    # -----------------------------------------------------

    def update_session(self):

        if hasattr(self, "session"):

            self.session["last_activity"] = datetime.now()

    # -----------------------------------------------------

    def session_information(self):

        return getattr(

            self,

            "session",

            {}

        )

    # =====================================================
    # FAVORITES
    # =====================================================

    def initialize_favorites(self):

        self.favorite_stocks = []

    # -----------------------------------------------------

    def add_favorite(self, symbol):

        symbol = str(symbol).upper()

        if symbol not in self.favorite_stocks:

            self.favorite_stocks.append(symbol)

    # -----------------------------------------------------

    def remove_favorite(self, symbol):

        symbol = str(symbol).upper()

        if symbol in self.favorite_stocks:

            self.favorite_stocks.remove(symbol)

    # -----------------------------------------------------

    def favorites(self):

        return list(self.favorite_stocks)

    # =====================================================
    # SEARCH
    # =====================================================

    def search_stock(

        self,

        symbol

    ):

        symbol = symbol.upper()

        all_results = []

        for category in [

            "intraday",

            "swing",

            "positional"

        ]:

            for stock in self.scanner_cache.get(

                category,

                []

            ):

                if stock.get(

                    "symbol",

                    ""

                ).upper() == symbol:

                    all_results.append(stock)

        return all_results

    # =====================================================
    # GLOBAL FILTER
    # =====================================================

    def filter_by_sector(

        self,

        stocks,

        sector

    ):

        return [

            stock

            for stock in stocks

            if stock.get(

                "sector",

                ""

            ) == sector

        ]

    # -----------------------------------------------------

    def filter_by_score(

        self,

        stocks,

        minimum_score=70

    ):

        return [

            stock

            for stock in stocks

            if stock.get(

                "ai_score",

                0

            ) >= minimum_score

        ]

    # =====================================================
    # MARKET STATUS
    # =====================================================

    def market_information(self):

        return {

            "status":

                self.market_status,

            "session":

                self.market_session(),

            "last_refresh":

                self.last_refresh,

            "analytics":

                self.analytics(),

        }

    # =====================================================
    # CONTROLLER INFO
    # =====================================================

    def information(self):

        return {

            "application":

                "StockVersity Scanner Pro",

            "version":

                self.version,

            "powered_by":

                "AI",

            "running":

                self.running,

            "market":

                self.market_information(),

            "statistics":

                self.statistics(),

            "performance":

                self.performance_metrics(),

        }

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        self.clear_cache()

        self.initialize_alerts()

        self.initialize_event_queue()

        self.initialize_preferences()

        self.initialize_favorites()

        self.statusChanged.emit(

            "Controller reset successfully."

        )
            # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(self):

        self.statusChanged.emit(

            "Shutting down StockVersity Scanner Pro..."

        )

        self.running = False

        #
        # Stop refresh timer
        #

        try:

            self.refresh_timer.stop()

        except Exception:

            pass

        #
        # Stop scheduler
        #

        try:

            self.stop_scheduler()

        except Exception:

            pass

        #
        # Stop heartbeat
        #

        try:

            self.stop_heartbeat()

        except Exception:

            pass

        #
        # Stop worker
        #

        try:

            self.stop_worker()

        except Exception:

            pass

        #
        # Clear runtime data
        #

        try:

            self.clear_cache()

        except Exception:

            pass

        self.finished.emit()

        self.statusChanged.emit(

            "Application stopped successfully."

        )

    # =====================================================
    # RESOURCE CLEANUP
    # =====================================================

    def cleanup(self):

        self.shutdown()

        try:

            self.alerts.clear()
        except Exception:
            pass

        try:

            self.alert_history.clear()
        except Exception:
            pass

        try:

            self.event_queue.clear()
        except Exception:
            pass

        try:

            self.favorite_stocks.clear()
        except Exception:
            pass

    # =====================================================
    # RESTART CONTROLLER
    # =====================================================

    def restart(self):

        self.shutdown()

        self.initialize_alerts()

        self.initialize_event_queue()

        self.initialize_preferences()

        self.initialize_favorites()

        self.start()

    # =====================================================
    # CONTROLLER STATE
    # =====================================================

    def state(self):

        return {

            "running": self.running,

            "market_status": self.market_status,

            "market_session": self.market_session(),

            "last_refresh": self.last_refresh,

            "heartbeat":

                getattr(

                    self,

                    "last_heartbeat",

                    None

                ),

            "failover":

                self.failover_status(),

        }

    # =====================================================
    # VERSION
    # =====================================================

    @staticmethod
    def application_name():

        return "StockVersity Scanner Pro"

    # -----------------------------------------------------

    @staticmethod
    def application_version():

        return "4.0"

    # -----------------------------------------------------

    @staticmethod
    def powered_by():

        return "AI"

    # =====================================================
    # STRING
    # =====================================================

    def __str__(self):

        return (

            f"{self.application_name()} "

            f"v{self.application_version()} "

            f"| Powered by AI"

        )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (

            f"<AppController "

            f"running={self.running} "

            f"market='{self.market_status}' "

            f"version='{self.application_version()}'>"

        )

    # =====================================================
    # DESTRUCTOR
    # =====================================================

    def __del__(self):

        try:

            self.cleanup()

        except Exception:

            pass


# ==========================================================
# END OF FILE
# ==========================================================



