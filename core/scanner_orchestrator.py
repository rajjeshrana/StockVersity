from __future__ import annotations

import threading
import time
from datetime import datetime
from typing import Dict, List, Optional

from backend.core.market_data_manager import (
    market_data_manager,
    MarketData,
)

from backend.core.sector_manager import (
    sector_manager,
)

from backend.core.ai_manager import (
    ai_manager,
)

from backend.scanner.scanner_engine import (
    ScannerEngine,
)

from backend.services.data_service import (
    DataService,
)


class ScannerOrchestrator:
    """
    Central controller responsible for coordinating
    market data, scanners, sector analysis and AI scoring.
    """

    def __init__(self):

        self.market = market_data_manager

        self.sectors = sector_manager

        self.ai = ai_manager

        self.scanner = ScannerEngine()

        self.data_service = DataService()

        self.running = False

        self.scan_interval = 30

        self.thread: Optional[
            threading.Thread
        ] = None

        self.last_scan: Optional[
            datetime
        ] = None

        self.scan_count = 0

        self.error_count = 0

    # ======================================================
    # START
    # ======================================================

    def start(self):

        if self.running:

            return

        self.running = True

        self.thread = threading.Thread(

            target=self._worker,

            daemon=True,

            name="ScannerOrchestrator",

        )

        self.thread.start()

    # ======================================================
    # STOP
    # ======================================================

    def stop(self):

        self.running = False

        if self.thread:

            self.thread.join(timeout=2)

    # ======================================================
    # LOOP
    # ======================================================

    def _worker(self):

        while self.running:

            try:

                self.run_cycle()

            except Exception:

                self.error_count += 1

            time.sleep(

                self.scan_interval

            )

    # ======================================================
    # SINGLE CYCLE
    # ======================================================

    def run_cycle(self):

        self.load_market_data()

        self.calculate_sector_strength()

        self.run_scanners()

        self.run_ai()

        self.last_scan = datetime.utcnow()

        self.scan_count += 1

    # ======================================================
    # LOAD DATA
    # ======================================================

    def load_market_data(self):

        stocks = self.data_service.fetch_market_data()

        if not stocks:

            return

        self.market.update_bulk(

            stocks

        )

    # ======================================================
    # MARKET SNAPSHOT
    # ======================================================

    def snapshot(self):

        return self.market.snapshot()

    # ======================================================
    # SYMBOLS
    # ======================================================

    def symbols(self):

        return self.market.symbols()
        # ======================================================
    # CALCULATE SECTOR STRENGTH
    # ======================================================

    def calculate_sector_strength(self):

        sector_scores: Dict[str, List[MarketData]] = {}

        for stock in self.market.all_symbols():

            sector_name = self.sectors.sector_of(

                stock.symbol

            )

            if not sector_name:

                continue

            sector_scores.setdefault(

                sector_name,

                []

            ).append(stock)

        for sector_name, stocks in sector_scores.items():

            sector = self.sectors.get(

                sector_name

            )

            if sector is None:

                continue

            sector.volume = sum(

                stock.volume

                for stock in stocks

            )

            sector.change_percent = round(

                sum(

                    stock.change_percent

                    for stock in stocks

                ) / max(

                    len(stocks),

                    1,

                ),

                2,

            )

            sector.advancing = len(

                [

                    s for s in stocks

                    if s.change_percent > 0

                ]

            )

            sector.declining = len(

                [

                    s for s in stocks

                    if s.change_percent < 0

                ]

            )

            sector.unchanged = len(stocks) - (

                sector.advancing +

                sector.declining

            )

            sector.relative_strength = round(

                (

                    sector.advancing /

                    max(

                        len(stocks),

                        1,

                    )

                ) * 100,

                2,

            )

            sector.momentum_score = round(

                sum(

                    s.rsi

                    for s in stocks

                ) / max(

                    len(stocks),

                    1,

                ),

                2,

            )

            sector.volume_score = min(

                100,

                round(

                    sum(

                        s.relative_volume

                        for s in stocks

                    ) *

                    10,

                    2,

                ),

            )

            sector.breakout_score = min(

                100,

                len(

                    [

                        s for s in stocks

                        if s.day_high_breakout

                    ]

                ) * 10,

            )

            sector.trend_score = round(

                len(

                    [

                        s for s in stocks

                        if s.last_price > s.ema50

                    ]

                ) /

                max(

                    len(stocks),

                    1,

                ) * 100,

                2,

            )

            self.sectors.calculate_total_score(

                sector_name

            )

    # ======================================================
    # RUN SCANNERS
    # ======================================================

    def run_scanners(self):

        symbols = self.market.symbols()

        self.scanner.scan(

            symbols

        )

    # ======================================================
    # RUN AI
    # ======================================================

    def run_ai(self):

        self.ai.clear()

        self.ai.analyze_bulk(

            self.market.symbols()

        )

    # ======================================================
    # TOP OPPORTUNITIES
    # ======================================================

    def opportunities(

        self,

        limit: int = 20,

    ):

        return self.ai.top_opportunities(

            limit

        )

    # ======================================================
    # DASHBOARD DATA
    # ======================================================

    def dashboard_data(self):

        return {

            "market": self.market.health(),

            "sectors": self.sectors.dashboard_summary(),

            "ai": self.ai.dashboard_summary(),

            "top_opportunities": self.opportunities(

                10

            ),

        }

    # ======================================================
    # HEALTH
    # ======================================================

    def health(self):

        return {

            "running": self.running,

            "last_scan": self.last_scan,

            "scan_count": self.scan_count,

            "errors": self.error_count,

            "market": self.market.health(),

            "sector": self.sectors.health(),

            "ai": self.ai.health(),

        }
        # ======================================================
    # INTRADAY OPPORTUNITIES
    # ======================================================

    def intraday_opportunities(

        self,

        limit: int = 20,

    ):

        return self.ai.intraday_opportunities()[:limit]

    # ======================================================
    # SWING OPPORTUNITIES
    # ======================================================

    def swing_opportunities(

        self,

        limit: int = 20,

    ):

        return self.ai.swing_opportunities()[:limit]

    # ======================================================
    # POSITIONAL OPPORTUNITIES
    # ======================================================

    def positional_opportunities(

        self,

        limit: int = 20,

    ):

        return self.ai.positional_opportunities()[:limit]

    # ======================================================
    # BUY LIST
    # ======================================================

    def buy_list(self):

        return self.ai.buy_list()

    # ======================================================
    # WATCH LIST
    # ======================================================

    def watch_list(self):

        return self.ai.watch_list()

    # ======================================================
    # HOT SECTORS
    # ======================================================

    def hot_sectors(self):

        return self.sectors.hot_sectors()

    # ======================================================
    # WEAK SECTORS
    # ======================================================

    def weak_sectors(self):

        return self.sectors.weak_sectors()

    # ======================================================
    # EXPORT AI RESULTS
    # ======================================================

    def export_ai_results(self):

        return self.ai.export()

    # ======================================================
    # EXPORT SECTOR DATA
    # ======================================================

    def export_sector_data(self):

        return self.sectors.export()

    # ======================================================
    # MARKET STATISTICS
    # ======================================================

    def market_statistics(self):

        return {

            "symbols": self.market.total_symbols(),

            "cache": self.market.cache_statistics(),

            "market_open": self.market.market_open(),

        }

    # ======================================================
    # PERFORMANCE
    # ======================================================

    def performance(self):

        return {

            "scan_count": self.scan_count,

            "last_scan": self.last_scan,

            "errors": self.error_count,

            "scan_interval": self.scan_interval,

        }

    # ======================================================
    # FULL DASHBOARD
    # ======================================================

    def full_dashboard(self):

        return {

            "statistics": self.market_statistics(),

            "performance": self.performance(),

            "market": self.market.health(),

            "sector": self.sectors.health(),

            "ai": self.ai.health(),

            "top_intraday": self.intraday_opportunities(10),

            "top_swing": self.swing_opportunities(10),

            "top_positional": self.positional_opportunities(10),

            "hot_sectors": self.hot_sectors(),

            "weak_sectors": self.weak_sectors(),

        }

    # ======================================================
    # REFRESH NOW
    # ======================================================

    def refresh_now(self):

        self.run_cycle()

    # ======================================================
    # RESET
    # ======================================================

    def reset(self):

        self.market.reset()

        self.sectors.reset()

        self.ai.reset()

        self.scan_count = 0

        self.error_count = 0

        self.last_scan = None

    # ======================================================
    # SCAN HISTORY
    # ======================================================

    def summary(self):

        return {

            "running": self.running,

            "last_scan": self.last_scan,

            "total_scans": self.scan_count,

            "errors": self.error_count,

            "symbols": self.market.total_symbols(),

            "opportunities": len(

                self.ai.all_results()

            ),

        }
        # ======================================================
    # STARTUP
    # ======================================================

    def startup(self):

        self.market.startup()

        self.sectors.startup()

        self.ai.startup()

        self.start()

        return {

            "status": "started",

            "started_at": datetime.utcnow(),

            "scan_interval": self.scan_interval,

        }

    # ======================================================
    # SHUTDOWN
    # ======================================================

    def shutdown(self):

        self.stop()

        self.market.shutdown()

        self.sectors.shutdown()

        self.ai.shutdown()

        return {

            "status": "stopped",

            "stopped_at": datetime.utcnow(),

            "total_scans": self.scan_count,

            "errors": self.error_count,

        }

    # ======================================================
    # CHANGE SCAN INTERVAL
    # ======================================================

    def set_scan_interval(

        self,

        seconds: int,

    ):

        self.scan_interval = max(

            5,

            int(seconds),

        )

    # ======================================================
    # STATUS
    # ======================================================

    def status(self):

        return {

            "running": self.running,

            "interval": self.scan_interval,

            "last_scan": self.last_scan,

            "scan_count": self.scan_count,

            "errors": self.error_count,

        }

    # ======================================================
    # SYNCHRONIZE
    # ======================================================

    def synchronize(self):

        """
        Synchronize managers after
        loading fresh market data.
        """

        self.calculate_sector_strength()

        self.run_ai()

    # ======================================================
    # RELOAD
    # ======================================================

    def reload(self):

        self.reset()

        self.run_cycle()

    # ======================================================
    # VERSION
    # ======================================================

    @property
    def version(self):

        return "4.0"

    # ======================================================
    # APPLICATION NAME
    # ======================================================

    @property
    def application(self):

        return "StockVersity Scanner Pro"

    # ======================================================
    # REPR
    # ======================================================

    def __repr__(self):

        return (

            "ScannerOrchestrator("

            f"running={self.running}, "

            f"scans={self.scan_count}, "

            f"errors={self.error_count}"

            ")"

        )

    # ======================================================
    # STR
    # ======================================================

    def __str__(self):

        return (

            "StockVersity Scanner Pro\n"

            f"Version        : {self.version}\n"

            f"Running        : {self.running}\n"

            f"Scan Interval  : {self.scan_interval}s\n"

            f"Total Scans    : {self.scan_count}\n"

            f"Errors         : {self.error_count}\n"

            f"Last Scan      : {self.last_scan}"

        )


# ======================================================
# GLOBAL SINGLETON
# ======================================================

scanner_orchestrator = ScannerOrchestrator()


# ======================================================
# EXPORTS
# ======================================================

__all__ = [

    "ScannerOrchestrator",

    "scanner_orchestrator",

]