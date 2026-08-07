"""
==========================================================
StockVersity Scanner Pro
Application Controller
Version : 4.0
Powered By : AI
==========================================================
"""

from __future__ import annotations

import threading
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from PySide6.QtCore import QObject, Signal, QTimer

# ==========================================================
# Backend Engines
# ==========================================================

from backend.scanner.nse_data_engine import NSEDataEngine
from backend.scanner.scanner_executor import ScannerExecutor

from backend.ai.market_prediction_engine import MarketPredictionEngine
from backend.ai.market_sentiment_engine import MarketSentimentEngine
from backend.ai.market_regime_engine import MarketRegimeEngine

from backend.ai.opportunity_ranker import OpportunityRanker
from backend.ai.pattern_recognition_engine import PatternRecognitionEngine
from backend.ai.risk_management_engine import RiskManagementEngine
from backend.ai.market_structure_engine import MarketStructureEngine
from backend.ai.volume_analysis_engine import VolumeAnalysisEngine
from backend.ai.sector_rotation_engine import SectorRotationEngine


# ==========================================================
# APPLICATION CONTROLLER
# ==========================================================

class ApplicationController(QObject):

    # ------------------------------------------------------
    # Qt Signals
    # ------------------------------------------------------

    statusChanged = Signal(str)
    marketStatusChanged = Signal(str)

    dashboardUpdated = Signal(dict)

    scannerCompleted = Signal(list)

    opportunityFound = Signal(dict)

    errorOccurred = Signal(str)

    countdownUpdated = Signal(int)

    # ------------------------------------------------------

    def __init__(self):

        super().__init__()

        self.logger = logging.getLogger("ApplicationController")

        self.running = False

        self.market_open = False

        self.last_scan_time = None

        self.refresh_interval = 60

        self.scan_counter = 0

        self.best_opportunities = []

        self.dashboard_data = {}

        self.scheduler_thread = None

        self.stop_event = threading.Event()

        self.initialize_engines()

        self.initialize_callbacks()

        self.initialize_timer()

    # ======================================================
    # INITIALIZE ENGINES
    # ======================================================

    def initialize_engines(self):

        self.statusChanged.emit(
            "Loading Trading Engines..."
        )

        self.nse_engine = NSEDataEngine()

        self.scanner = ScannerExecutor()

        self.market_prediction = MarketPredictionEngine()

        self.market_sentiment = MarketSentimentEngine()

        self.market_regime = MarketRegimeEngine()

        self.pattern_engine = PatternRecognitionEngine()

        self.ranker = OpportunityRanker()

        self.risk_engine = RiskManagementEngine()

        self.structure_engine = MarketStructureEngine()

        self.volume_engine = VolumeAnalysisEngine()

        self.rotation_engine = SectorRotationEngine()

        self.statusChanged.emit(
            "Trading Engines Loaded"
        )

    # ======================================================
    # CALLBACKS
    # ======================================================

    def initialize_callbacks(self):

        self.nse_engine.dashboard_callback = (
            self.update_dashboard
        )

        self.nse_engine.notification_callback = (
            self.receive_notification
        )

    # ======================================================
    # TIMER
    # ======================================================

    def initialize_timer(self):

        self.timer = QTimer()

        self.timer.timeout.connect(
            self.countdown_tick
        )

        self.remaining_seconds = self.refresh_interval

    # ======================================================
    # START APPLICATION
    # ======================================================

    def start(self):

        if self.running:

            return

        self.running = True

        self.stop_event.clear()

        self.statusChanged.emit(
            "Starting StockVersity Scanner..."
        )

        self.nse_engine.initialize()

        self.scheduler_thread = threading.Thread(
            target=self.scheduler_loop,
            daemon=True
        )

        self.scheduler_thread.start()

        self.timer.start(1000)

        self.statusChanged.emit(
            "Application Started"
        )

    # ======================================================
    # STOP APPLICATION
    # ======================================================

    def stop(self):

        self.running = False

        self.stop_event.set()

        self.timer.stop()

        self.nse_engine.finalize()

        self.statusChanged.emit(
            "Application Stopped"
        )

    # ======================================================
    # COUNTDOWN
    # ======================================================

    def countdown_tick(self):

        self.remaining_seconds -= 1

        if self.remaining_seconds < 0:

            self.remaining_seconds = self.refresh_interval

        self.countdownUpdated.emit(
            self.remaining_seconds
        )

    # ======================================================
    # MARKET STATUS
    # ======================================================

    def update_market_status(self):

        now = datetime.now().time()

        market_start = now.replace(
            hour=9,
            minute=15,
            second=0,
            microsecond=0
        )

        market_end = now.replace(
            hour=15,
            minute=30,
            second=0,
            microsecond=0
        )

        self.market_open = (
            market_start <= now <= market_end
        )

        if self.market_open:

            self.marketStatusChanged.emit(
                "OPEN"
            )

        else:

            self.marketStatusChanged.emit(
                "CLOSED"
            )

    # ==========================================================
    # MARKET CHECK
    # ==========================================================

    def is_market_open(self) -> bool:

        self.update_market_status()

        return self.market_open


# ==========================================================
# MAIN SCHEDULER
# ==========================================================

    def scheduler_loop(self):

        self.logger.info("Scheduler Started")

        while not self.stop_event.is_set():

            try:

                if not self.is_market_open():

                    self.statusChanged.emit(
                        "Waiting for Market Open..."
                    )

                    time.sleep(10)

                    continue

                self.run_market_cycle()

                self.remaining_seconds = self.refresh_interval

                for _ in range(self.refresh_interval):

                    if self.stop_event.is_set():

                        break

                    time.sleep(1)

            except Exception as e:

                self.logger.exception(e)

                self.errorOccurred.emit(str(e))

                time.sleep(5)

        self.logger.info("Scheduler Stopped")


# ==========================================================
# COMPLETE MARKET CYCLE
# ==========================================================

    def run_market_cycle(self):

        self.scan_counter += 1

        self.last_scan_time = datetime.now()

        self.statusChanged.emit(
            f"Running Scan #{self.scan_counter}"
        )

        start = time.perf_counter()

        self.fetch_market_data()

        self.calculate_indicators()

        opportunities = self.execute_scanner()

        ranked = self.rank_opportunities(
            opportunities
        )

        trades = self.generate_trade_cards(
            ranked
        )

        self.best_opportunities = trades

        self.dashboard_data = {

            "scan_number": self.scan_counter,

            "scan_time": self.last_scan_time,

            "market_open": self.market_open,

            "opportunities": trades

        }

        self.dashboardUpdated.emit(
            self.dashboard_data
        )

        self.scannerCompleted.emit(
            trades
        )

        runtime = round(

            time.perf_counter() - start,

            2

        )

        self.statusChanged.emit(

            f"Completed in {runtime} sec"

        )


# ==========================================================
# FETCH MARKET DATA
# ==========================================================

    def fetch_market_data(self):

        self.statusChanged.emit(

            "Downloading Market Data..."

        )

        self.nse_engine.live_update()


# ==========================================================
# CALCULATE INDICATORS
# ==========================================================

    def calculate_indicators(self):

        self.statusChanged.emit(

            "Calculating Indicators..."

        )

        self.nse_engine.update_indicators_batch()


# ==========================================================
# EXECUTE SCANNER
# ==========================================================

    def execute_scanner(self):

        self.statusChanged.emit(

            "Executing Scanner..."

        )

        return self.scanner.execute(

            self.nse_engine.market_data

        )


# ==========================================================
# RANK OPPORTUNITIES
# ==========================================================

    def rank_opportunities(

        self,

        opportunities

    ):

        self.statusChanged.emit(

            "Ranking Opportunities..."

        )

        return self.ranker.rank(

            opportunities

        )


# ==========================================================
# TRADE CARD GENERATOR
# ==========================================================

    def generate_trade_cards(

        self,

        ranked_list

    ):

        cards = []

        for stock in ranked_list:

            try:

                decision = self.market_prediction.predict(

                    stock

                )

                risk = self.risk_engine.evaluate(

                    stock

                )

                structure = self.structure_engine.evaluate(

                    stock

                )

                volume = self.volume_engine.evaluate(

                    stock

                )

                sector = self.rotation_engine.evaluate(

                    stock

                )

                pattern = self.pattern_engine.detect(

                    stock

                )

                card = {

                    "symbol":

                        stock.get("symbol"),

                    "score":

                        stock.get("score"),

                    "signal":

                        decision.get("signal"),

                    "confidence":

                        decision.get("confidence"),

                    "entry":

                        decision.get("entry"),

                    "stoploss":

                        decision.get("stoploss"),

                    "target":

                        decision.get("target"),

                    "rr":

                        risk.get("rr"),

                    "risk":

                        risk,

                    "structure":

                        structure,

                    "volume":

                        volume,

                    "sector":

                        sector,

                    "pattern":

                        pattern

                }

                cards.append(card)

            except Exception as e:

                self.logger.exception(e)

        cards.sort(

            key=lambda x: x["confidence"],

            reverse=True

        )

        return cards[:20]


# ==========================================================
# UPDATE DASHBOARD
# ==========================================================

    def update_dashboard(

        self,

        dashboard=None

    ):

        if dashboard is not None:

            self.dashboard_data = dashboard

        self.dashboardUpdated.emit(

            self.dashboard_data

        )


# ==========================================================
# NOTIFICATION RECEIVER
# ==========================================================

    def receive_notification(
        self,
        message: str
    ):

        self.logger.info(message)

        self.statusChanged.emit(message)


# ==========================================================
# MARKET SENTIMENT
# ==========================================================

    def calculate_market_sentiment(self):

        try:

            sentiment = self.market_sentiment.analyze(

                self.nse_engine.market_snapshot()

            )

            return sentiment

        except Exception as e:

            self.logger.exception(e)

            return {}


# ==========================================================
# MARKET REGIME
# ==========================================================

    def calculate_market_regime(self):

        try:

            regime = self.market_regime.detect(

                self.nse_engine.market_snapshot()

            )

            return regime

        except Exception as e:

            self.logger.exception(e)

            return {}


# ==========================================================
# FILTER BUY SIGNALS
# ==========================================================

    def buy_signals(self):

        return [

            x for x in self.best_opportunities

            if x["signal"] == "BUY"

        ]


# ==========================================================
# FILTER SELL SIGNALS
# ==========================================================

    def sell_signals(self):

        return [

            x for x in self.best_opportunities

            if x["signal"] == "SELL"

        ]


# ==========================================================
# TOP INTRADAY
# ==========================================================

    def top_intraday(self):

        data = [

            x

            for x in self.buy_signals()

            if x["confidence"] >= 70

        ]

        data.sort(

            key=lambda x: x["confidence"],

            reverse=True

        )

        return data[:5]


# ==========================================================
# TOP SWING
# ==========================================================

    def top_swing(self):

        result = []

        for stock in self.buy_signals():

            if stock["pattern"] in [

                "Bull Flag",

                "Falling Wedge",

                "Cup & Handle",

                "VCP"

            ]:

                result.append(stock)

        result.sort(

            key=lambda x: x["confidence"],

            reverse=True

        )

        return result[:5]


# ==========================================================
# TOP POSITIONAL
# ==========================================================

    def top_positional(self):

        result = []

        for stock in self.buy_signals():

            if stock["structure"].get(

                "stage"

            ) >= 2:

                result.append(stock)

        result.sort(

            key=lambda x: x["confidence"],

            reverse=True

        )

        return result[:5]


# ==========================================================
# MARKET SUMMARY
# ==========================================================

    def market_summary(self):

        sentiment = self.calculate_market_sentiment()

        regime = self.calculate_market_regime()

        return {

            "market_status":

                "OPEN"

                if self.market_open

                else "CLOSED",

            "sentiment":

                sentiment,

            "regime":

                regime,

            "total_scans":

                self.scan_counter,

            "last_scan":

                self.last_scan_time

        }


# ==========================================================
# LIVE DASHBOARD DATA
# ==========================================================

    def dashboard_payload(self):

        payload = {

            "summary":

                self.market_summary(),

            "top_intraday":

                self.top_intraday(),

            "top_swing":

                self.top_swing(),

            "top_positional":

                self.top_positional(),

            "buy":

                self.buy_signals(),

            "sell":

                self.sell_signals(),

            "market":

                self.nse_engine.market_snapshot(),

            "breadth":

                self.nse_engine.market_breadth(),

            "indices":

                self.nse_engine.indices(),

            "gainers":

                self.nse_engine.top_gainers(),

            "losers":

                self.nse_engine.top_losers()

        }

        return payload


# ==========================================================
# REFRESH UI
# ==========================================================

    def refresh_dashboard(self):

        self.dashboard_data = self.dashboard_payload()

        self.dashboardUpdated.emit(

            self.dashboard_data

        )


# ==========================================================
# LIVE STATISTICS
# ==========================================================

    def statistics(self):

        return {

            "running":

                self.running,

            "market_open":

                self.market_open,

            "scan_counter":

                self.scan_counter,

            "symbols":

                len(

                    self.nse_engine.market_data

                ),

            "buy":

                len(

                    self.buy_signals()

                ),

            "sell":

                len(

                    self.sell_signals()

                ),

            "last_scan":

                self.last_scan_time

        }


# ==========================================================
# HEALTH CHECK
# ==========================================================

    def health(self):

        return {

            "controller":

                "Running"

                if self.running

                else "Stopped",

            "nse_engine":

                self.nse_engine.health_status(),

            "statistics":

                self.statistics()

        }

# ==========================================================
# MANUAL SCAN
# ==========================================================

    def manual_scan(self):

        if not self.running:

            self.statusChanged.emit(
                "Application is not running."
            )
            return

        self.statusChanged.emit(
            "Manual Scan Started..."
        )

        self.run_market_cycle()


# ==========================================================
# FORCE DASHBOARD REFRESH
# ==========================================================

    def refresh_now(self):

        self.statusChanged.emit(
            "Refreshing Dashboard..."
        )

        self.refresh_dashboard()


# ==========================================================
# RESTART SERVICES
# ==========================================================

    def restart_services(self):

        self.statusChanged.emit(
            "Restarting Services..."
        )

        try:

            self.nse_engine.shutdown()

        except Exception:
            pass

        time.sleep(2)

        self.nse_engine.initialize()

        self.statusChanged.emit(
            "Services Restarted."
        )


# ==========================================================
# RECONNECT MARKET DATA
# ==========================================================

    def reconnect_market(self):

        self.statusChanged.emit(
            "Reconnecting Market Feed..."
        )

        try:

            self.nse_engine.reconnect()

            self.statusChanged.emit(
                "Market Feed Connected."
            )

        except Exception as e:

            self.logger.exception(e)

            self.errorOccurred.emit(str(e))


# ==========================================================
# INTERNET RECOVERY
# ==========================================================

    def internet_recovery(self):

        self.statusChanged.emit(
            "Checking Internet..."
        )

        while self.running:

            try:

                if self.nse_engine.internet_available():

                    self.statusChanged.emit(
                        "Internet Restored."
                    )

                    self.reconnect_market()

                    break

            except Exception:

                pass

            time.sleep(5)


# ==========================================================
# AUTO RECOVERY
# ==========================================================

    def auto_recovery(self):

        self.statusChanged.emit(
            "Running Recovery..."
        )

        try:

            self.internet_recovery()

            self.restart_services()

        except Exception as e:

            self.logger.exception(e)

            self.errorOccurred.emit(str(e))


# ==========================================================
# START BACKGROUND THREAD
# ==========================================================

    def start_background_worker(
        self,
        target,
        name="Worker"
    ):

        thread = threading.Thread(
            target=target,
            daemon=True,
            name=name
        )

        thread.start()

        return thread


# ==========================================================
# THREAD STATUS
# ==========================================================

    def thread_status(self):

        threads = []

        for thread in threading.enumerate():

            threads.append({

                "name": thread.name,

                "alive": thread.is_alive(),

                "daemon": thread.daemon

            })

        return threads


# ==========================================================
# ACTIVE THREAD COUNT
# ==========================================================

    def active_threads(self):

        return len(

            threading.enumerate()

        )


# ==========================================================
# EXPORT OPPORTUNITIES
# ==========================================================

    def export_opportunities(self):

        return self.best_opportunities


# ==========================================================
# EXPORT DASHBOARD
# ==========================================================

    def export_dashboard(self):

        return self.dashboard_data


# ==========================================================
# APPLICATION STATUS
# ==========================================================

    def application_status(self):

        return {

            "running": self.running,

            "market": self.market_open,

            "refresh_interval": self.refresh_interval,

            "threads": self.active_threads(),

            "last_scan": self.last_scan_time,

            "scan_counter": self.scan_counter

        }


# ==========================================================
# CLEAR CACHE
# ==========================================================

    def clear_cache(self):

        try:

            self.nse_engine.market_data.clear()

            self.best_opportunities.clear()

            self.dashboard_data.clear()

            self.statusChanged.emit(
                "Application Cache Cleared."
            )

        except Exception as e:

            self.logger.exception(e)


# ==========================================================
# RESET SESSION
# ==========================================================

    def reset_session(self):

        self.clear_cache()

        self.scan_counter = 0

        self.last_scan_time = None

        self.statusChanged.emit(

            "Trading Session Reset."

        )


# ==========================================================
# EMERGENCY STOP
# ==========================================================

    def emergency_stop(self):

        self.statusChanged.emit(

            "Emergency Stop Activated."

        )

        self.stop()

        try:

            self.nse_engine.shutdown()

        except Exception:
            pass

# ==========================================================
# PRE MARKET INITIALIZATION
# ==========================================================

    def pre_market_initialize(self):

        self.statusChanged.emit(
            "Initializing Pre-Market..."
        )

        try:

            self.nse_engine.initialize()

            self.nse_engine.premarket_engine()

            self.refresh_dashboard()

        except Exception as e:

            self.logger.exception(e)

            self.errorOccurred.emit(str(e))


# ==========================================================
# MARKET OPEN EVENT
# ==========================================================

    def on_market_open(self):

        self.market_open = True

        self.statusChanged.emit(
            "Market Open"
        )

        self.run_market_cycle()


# ==========================================================
# MARKET CLOSE EVENT
# ==========================================================

    def on_market_close(self):

        self.market_open = False

        self.statusChanged.emit(
            "Market Closed"
        )

        self.end_of_day_report()


# ==========================================================
# END OF DAY REPORT
# ==========================================================

    def end_of_day_report(self):

        report = {

            "date": datetime.now(),

            "total_scans": self.scan_counter,

            "buy_signals": len(

                self.buy_signals()

            ),

            "sell_signals": len(

                self.sell_signals()

            ),

            "top_trades":

                self.best_opportunities[:10]

        }

        self.logger.info(report)

        return report


# ==========================================================
# SAVE SESSION
# ==========================================================

    def save_session(self):

        try:

            self.nse_engine.save_configuration(

                "config.json"

            )

        except Exception as e:

            self.logger.exception(e)


# ==========================================================
# LOAD SESSION
# ==========================================================

    def load_session(self):

        try:

            self.nse_engine.load_configuration(

                "config.json"

            )

        except Exception as e:

            self.logger.exception(e)


# ==========================================================
# PERFORMANCE METRICS
# ==========================================================

    def performance_metrics(self):

        return {

            "runtime":

                self.nse_engine.performance_metrics(),

            "statistics":

                self.statistics(),

            "threads":

                self.active_threads()

        }


# ==========================================================
# AI ANALYSIS
# ==========================================================

    def ai_analysis(self):

        try:

            return self.nse_engine.run_ai_pipeline()

        except Exception as e:

            self.logger.exception(e)

            return {}


# ==========================================================
# FULL REFRESH
# ==========================================================

    def full_refresh(self):

        self.statusChanged.emit(

            "Performing Full Refresh..."

        )

        self.fetch_market_data()

        self.calculate_indicators()

        self.refresh_dashboard()


# ==========================================================
# APPLICATION READY
# ==========================================================

    def application_ready(self):

        return {

            "running":

                self.running,

            "market":

                self.market_open,

            "scanner":

                self.scanner is not None,

            "engine":

                self.nse_engine is not None

        }


# ==========================================================
# STARTUP SEQUENCE
# ==========================================================

    def startup_sequence(self):

        self.load_session()

        self.pre_market_initialize()

        self.start()


# ==========================================================
# SHUTDOWN SEQUENCE
# ==========================================================

    def shutdown_sequence(self):

        self.save_session()

        self.stop()

        self.statusChanged.emit(

            "Application Shutdown Complete."

        )

# ==========================================================
# APPLICATION INFORMATION
# ==========================================================

    @property
    def application_name(self):

        return "StockVersity Scanner Pro"

    @property
    def version(self):

        return "4.0"

    @property
    def powered_by(self):

        return "AI"


# ==========================================================
# BUILD INFORMATION
# ==========================================================

    def build_information(self):

        return {

            "application": self.application_name,

            "version": self.version,

            "powered_by": self.powered_by,

            "python": "3.14",

            "framework": "PySide6",

            "status": "Production"

        }


# ==========================================================
# CURRENT SESSION
# ==========================================================

    def session_information(self):
        return {
            "session_id": getattr(self, "session_id", "default"),
            "start_time": str(self.last_scan_time)
        }

    def verify_engines(self) -> Dict[str, bool]:
        """Verify that all core backend engines are properly initialized."""
        return {
            "nse_engine": self.nse_engine is not None,
            "scanner": self.scanner is not None,
            "market_prediction": self.market_prediction is not None,
            "market_sentiment": self.market_sentiment is not None,
            "market_regime": self.market_regime is not None,
            "pattern_engine": self.pattern_engine is not None,
            "ranker": self.ranker is not None,
            "risk_engine": self.risk_engine is not None,
            "structure_engine": self.structure_engine is not None,
            "volume_engine": self.volume_engine is not None,
            "rotation_engine": self.rotation_engine is not None
        }