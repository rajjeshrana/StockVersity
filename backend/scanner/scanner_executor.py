"""
==========================================================
StockVersity Scanner Pro v4.0
Enterprise Scanner Executor
Powered by AI
==========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
import pandas as pd

# ==========================================================
# IMPORT AI MODULES
# ==========================================================

from backend.ai.scanner_engine import ScannerEngine

# ==========================================================
# CONFIGURATION
# ==========================================================

DEFAULT_WORKERS = 8

MAX_TOP_STOCKS = 5

DEFAULT_REFRESH_SECONDS = 60


# ==========================================================
# SCAN RESULT
# ==========================================================

@dataclass
class ScanRecord:

    symbol: str

    sector: str

    category: str

    score: float

    recommendation: str

    signal: str

    price: float

    confidence: float

    timestamp: datetime = field(
        default_factory=datetime.now
    )


# ==========================================================
# SCAN SUMMARY
# ==========================================================

@dataclass
class ScanSummary:

    total_scanned: int = 0

    successful: int = 0

    failed: int = 0

    duration: float = 0.0

    started_at: datetime = field(
        default_factory=datetime.now
    )

    finished_at: Optional[datetime] = None


# ==========================================================
# MASTER EXECUTOR
# ==========================================================

class ScannerExecutor:

    VERSION = "4.0"

    def __init__(

        self,

        max_workers: int = DEFAULT_WORKERS,

    ):

        self.max_workers = max_workers

        self.market_data: Dict[str, pd.DataFrame] = {}

        self.sectors: Dict[str, str] = {}

        self.scanners: List[ScannerEngine] = []

        self.records: List[ScanRecord] = []

        self.summary = ScanSummary()

        self.is_running = False

        self.stop_requested = False

        self.last_scan = None

        self.progress_callback: Optional[
            Callable[[int, int], None]
        ] = None

        self.status_callback: Optional[
            Callable[[str], None]
        ] = None


# ==========================================================
# CALLBACKS
# ==========================================================

    def set_progress_callback(

        self,

        callback: Callable[[int, int], None],

    ) -> None:

        self.progress_callback = callback


    def set_status_callback(

        self,

        callback: Callable[[str], None],

    ) -> None:

        self.status_callback = callback


# ==========================================================
# STATUS
# ==========================================================

    def update_status(

        self,

        message: str,

    ) -> None:

        if self.status_callback:

            self.status_callback(

                message

            )


# ==========================================================
# RESET
# ==========================================================

    def reset(

        self,

    ) -> None:

        self.scanners.clear()

        self.records.clear()

        self.summary = ScanSummary()

        self.stop_requested = False


# ==========================================================
# LOAD MARKET DATA
# ==========================================================

    def load_market_data(

        self,

        data: Dict[str, pd.DataFrame],

    ) -> None:

        self.market_data = data


# ==========================================================
# LOAD SECTORS
# ==========================================================

    def load_sectors(

        self,

        sectors: Dict[str, str],

    ) -> None:

        self.sectors = sectors


# ==========================================================
# SYMBOL VALIDATION
# ==========================================================

    def valid_symbol(

        self,

        symbol: str,

    ) -> bool:

        return (

            symbol in self.market_data

            and

            self.market_data[symbol] is not None

            and

            not self.market_data[symbol].empty

        )


# ==========================================================
# CREATE SCANNER
# ==========================================================

    def create_scanner(

        self,

        symbol: str,

    ) -> Optional[ScannerEngine]:

        if not self.valid_symbol(

            symbol

        ):

            return None

        sector = self.sectors.get(

            symbol,

            "Unknown",

        )

        return ScannerEngine(

            symbol=symbol,

            dataframe=self.market_data[symbol],

            sector=sector,

        )


# ==========================================================
# STOP SCAN
# ==========================================================

    def stop(

        self,

    ) -> None:

        self.stop_requested = True


# ==========================================================
# IS BUSY
# ==========================================================

    @property
    def busy(

        self,

    ) -> bool:

        return self.is_running


# ==========================================================
# TOTAL SYMBOLS
# ==========================================================

    @property
    def total_symbols(

        self,

    ) -> int:

        return len(

            self.market_data

        )


# ==========================================================
# VERSION INFO
# ==========================================================

    @staticmethod
    def version(

    ) -> Dict:

        return {

            "Application":

                "StockVersity Scanner Pro",

            "Module":

                "Scanner Executor",

            "Version":

                "4.0",

            "Powered By":

                "AI",

        }
    # ==========================================================
# START SCAN
# ==========================================================

    def start_scan(

        self,

    ) -> None:

        self.reset()

        self.is_running = True

        self.summary.started_at = datetime.now()

        self.update_status(

            "Initializing scanner..."

        )


# ==========================================================
# FINISH SCAN
# ==========================================================

    def finish_scan(

        self,

    ) -> None:

        self.summary.finished_at = datetime.now()

        self.summary.duration = (

            self.summary.finished_at

            -

            self.summary.started_at

        ).total_seconds()

        self.last_scan = self.summary.finished_at

        self.is_running = False

        self.update_status(

            "Scan completed."

        )


# ==========================================================
# PROCESS SINGLE SYMBOL
# ==========================================================

    def process_symbol(

        self,

        symbol: str,

    ) -> Optional[ScanRecord]:

        if self.stop_requested:

            return None

        try:

            scanner = self.create_scanner(

                symbol

            )

            if scanner is None:

                return None

            result = scanner.run()

            recommendation = result[

                "recommendation"

            ]

            record = ScanRecord(

                symbol=symbol,

                sector=scanner.sector,

                category=result["category"]["category"],

                score=scanner.priority_score(),

                recommendation=recommendation[

                    "recommendation"

                ],

                signal=scanner.signal(),

                price=scanner.last_price(),

                confidence=scanner.confidence_score(),

            )

            self.scanners.append(

                scanner

            )

            self.records.append(

                record

            )

            self.summary.successful += 1

            return record

        except Exception:

            self.summary.failed += 1

            return None


# ==========================================================
# PROCESS ALL SYMBOLS
# ==========================================================

    def process_all(

        self,

    ) -> List[ScanRecord]:

        symbols = list(

            self.market_data.keys()

        )

        total = len(

            symbols

        )

        self.summary.total_scanned = total

        completed = 0

        with ThreadPoolExecutor(

            max_workers=self.max_workers

        ) as executor:

            futures = {

                executor.submit(

                    self.process_symbol,

                    symbol,

                ): symbol

                for symbol in symbols

            }

            for future in as_completed(

                futures

            ):

                if self.stop_requested:

                    break

                completed += 1

                if self.progress_callback:

                    self.progress_callback(

                        completed,

                        total,

                    )

                future.result()

        return self.records


# ==========================================================
# EXECUTE SCAN
# ==========================================================

    def execute(

        self,

    ) -> List[ScanRecord]:

        self.start_scan()

        try:

            records = self.process_all()

        finally:

            self.finish_scan()

        return records


# ==========================================================
# RUN IN BACKGROUND
# ==========================================================

    def run_background(

        self,

    ) -> threading.Thread:

        thread = threading.Thread(

            target=self.execute,

            daemon=True,

        )

        thread.start()

        return thread


# ==========================================================
# WAIT UNTIL COMPLETE
# ==========================================================

    def wait(

        self,

        interval: float = 0.1,

    ) -> None:

        while self.busy:

            time.sleep(

                interval

            )


# ==========================================================
# CURRENT PROGRESS
# ==========================================================

    @property
    def progress(

        self,

    ) -> float:

        if self.summary.total_scanned == 0:

            return 0.0

        return round(

            (

                self.summary.successful

                +

                self.summary.failed

            )

            /

            self.summary.total_scanned

            * 100,

            2,

        )


# ==========================================================
# HAS RESULTS
# ==========================================================

    @property
    def has_results(

        self,

    ) -> bool:

        return len(

            self.records

        ) > 0


# ==========================================================
# FAILED SYMBOLS
# ==========================================================

    @property
    def failed_count(

        self,

    ) -> int:

        return self.summary.failed


# ==========================================================
# SUCCESS COUNT
# ==========================================================

    @property
    def success_count(

        self,

    ) -> int:

        return self.summary.successful
    # ==========================================================
# RANK SCANNERS
# ==========================================================

    def rank_scanners(

        self,

    ) -> List[ScannerEngine]:

        self.scanners.sort(

            key=lambda scanner:

            scanner.priority_score(),

            reverse=True,

        )

        return self.scanners


# ==========================================================
# TOP INTRADAY
# ==========================================================

    def top_intraday(

        self,

        limit: int = MAX_TOP_STOCKS,

    ) -> List[Dict]:

        ranked = ScannerEngine.top_intraday(

            self.scanners,

            limit,

        )

        return ranked


# ==========================================================
# TOP SWING
# ==========================================================

    def top_swing(

        self,

        limit: int = MAX_TOP_STOCKS,

    ) -> List[Dict]:

        ranked = ScannerEngine.top_swing(

            self.scanners,

            limit,

        )

        return ranked


# ==========================================================
# TOP POSITIONAL
# ==========================================================

    def top_positional(

        self,

        limit: int = MAX_TOP_STOCKS,

    ) -> List[Dict]:

        ranked = ScannerEngine.top_positional(

            self.scanners,

            limit,

        )

        return ranked


# ==========================================================
# WATCHLIST
# ==========================================================

    def watchlist(

        self,

    ) -> pd.DataFrame:

        return ScannerEngine.watchlist_dashboard(

            self.scanners

        )


# ==========================================================
# SECTOR RANKING
# ==========================================================

    def sector_ranking(

        self,

    ) -> pd.DataFrame:

        return ScannerEngine.sector_ranking(

            self.scanners

        )


# ==========================================================
# MARKET SUMMARY
# ==========================================================

    def market_summary(

        self,

    ) -> Dict:

        return ScannerEngine.market_summary(

            self.scanners

        )


# ==========================================================
# MARKET STATISTICS
# ==========================================================

    def statistics(

        self,

    ) -> Dict:

        return ScannerEngine.statistics(

            self.scanners

        )


# ==========================================================
# AI RANKING TABLE
# ==========================================================

    def ranking_table(

        self,

    ) -> pd.DataFrame:

        return ScannerEngine.ai_ranking(

            self.scanners

        )


# ==========================================================
# HIGH CONVICTION
# ==========================================================

    def high_conviction(

        self,

    ) -> List[Dict]:

        return ScannerEngine.high_conviction_picks(

            self.scanners

        )


# ==========================================================
# BREAKOUTS
# ==========================================================

    def breakout_candidates(

        self,

    ) -> List[Dict]:

        return ScannerEngine.breakout_candidates(

            self.scanners

        )


# ==========================================================
# TREND CONTINUATION
# ==========================================================

    def trend_continuation(

        self,

    ) -> List[Dict]:

        return ScannerEngine.trend_continuation_candidates(

            self.scanners

        )


# ==========================================================
# REVERSALS
# ==========================================================

    def reversals(

        self,

    ) -> List[Dict]:

        return ScannerEngine.reversal_candidates(

            self.scanners

        )


# ==========================================================
# INSTITUTIONAL PICKS
# ==========================================================

    def institutional(

        self,

    ) -> List[Dict]:

        return ScannerEngine.institutional_picks(

            self.scanners

        )


# ==========================================================
# DAILY TOP 5
# ==========================================================

    def daily_top_five(

        self,

    ) -> pd.DataFrame:

        return ScannerEngine.daily_top_five(

            self.scanners

        )


# ==========================================================
# ENTERPRISE DASHBOARD
# ==========================================================

    def dashboard(

        self,

    ) -> Dict:

        return {

            "summary":

                self.market_summary(),

            "statistics":

                self.statistics(),

            "watchlist":

                self.watchlist(),

            "sector_ranking":

                self.sector_ranking(),

            "top_intraday":

                self.top_intraday(),

            "top_swing":

                self.top_swing(),

            "top_positional":

                self.top_positional(),

            "high_conviction":

                self.high_conviction(),

            "institutional":

                self.institutional(),

            "breakouts":

                self.breakout_candidates(),

            "trend_continuation":

                self.trend_continuation(),

            "reversals":

                self.reversals(),

            "ranking":

                self.ranking_table(),

        }


# ==========================================================
# COMPLETE REPORT
# ==========================================================

    def report(

        self,

    ) -> Dict:

        return {

            "version":

                self.version(),

            "summary":

                self.summary,

            "dashboard":

                self.dashboard(),

            "scan_time":

                self.last_scan,

        }
    # ==========================================================
# LIVE SCAN LOOP
# ==========================================================

    def live_scan(

        self,

        refresh_seconds: int = DEFAULT_REFRESH_SECONDS,

    ) -> None:

        self.update_status(

            "Live Scanner Started"

        )

        while not self.stop_requested:

            self.execute()

            if self.stop_requested:

                break

            time.sleep(

                refresh_seconds

            )

        self.update_status(

            "Live Scanner Stopped"

        )


# ==========================================================
# START LIVE SCANNER
# ==========================================================

    def start_live(

        self,

        refresh_seconds: int = DEFAULT_REFRESH_SECONDS,

    ) -> threading.Thread:

        thread = threading.Thread(

            target=self.live_scan,

            kwargs={

                "refresh_seconds":

                    refresh_seconds

            },

            daemon=True,

        )

        thread.start()

        return thread


# ==========================================================
# AUTO REFRESH
# ==========================================================

    def auto_refresh(

        self,

        refresh_seconds: int = DEFAULT_REFRESH_SECONDS,

    ) -> None:

        self.live_scan(

            refresh_seconds

        )


# ==========================================================
# MARKET OPEN CHECK
# ==========================================================

    @staticmethod
    def market_open(

    ) -> bool:

        now = datetime.now()

        if now.weekday() >= 5:

            return False

        minutes = (

            now.hour * 60

            +

            now.minute

        )

        market_open = 9 * 60 + 15

        market_close = 15 * 60 + 30

        return (

            market_open

            <= minutes

            <= market_close

        )


# ==========================================================
# WAIT FOR MARKET
# ==========================================================

    def wait_for_market(

        self,

        interval: int = 60,

    ) -> None:

        while (

            not self.market_open()

            and

            not self.stop_requested

        ):

            self.update_status(

                "Waiting for market..."

            )

            time.sleep(

                interval

            )


# ==========================================================
# LIVE MARKET MONITOR
# ==========================================================

    def monitor_market(

        self,

        refresh_seconds: int = DEFAULT_REFRESH_SECONDS,

    ) -> None:

        self.wait_for_market()

        if self.stop_requested:

            return

        self.live_scan(

            refresh_seconds

        )


# ==========================================================
# ALERTS
# ==========================================================

    def alerts(

        self,

        minimum_score: float = 85,

    ) -> List[Dict]:

        return ScannerEngine.alert_queue(

            self.scanners,

            minimum_score,

        )


# ==========================================================
# SCAN HISTORY
# ==========================================================

    def history(

        self,

    ) -> pd.DataFrame:

        return ScannerEngine.scan_history(

            self.scanners

        )


# ==========================================================
# CACHE REFRESH
# ==========================================================

    def refresh_cache(

        self,

    ) -> None:

        for scanner in self.scanners:

            scanner.refresh()


# ==========================================================
# EXPORT CSV
# ==========================================================

    def export_csv(

        self,

        filename: str,

    ) -> bool:

        return ScannerEngine.export_csv(

            self.scanners,

            filename,

        )


# ==========================================================
# EXPORT EXCEL
# ==========================================================

    def export_excel(

        self,

        filename: str,

    ) -> bool:

        return ScannerEngine.export_excel(

            self.scanners,

            filename,

        )


# ==========================================================
# EXPORT JSON
# ==========================================================

    def export_json(

        self,

    ) -> str:

        return ScannerEngine.export_json(

            self.scanners

        )


# ==========================================================
# PERFORMANCE METRICS
# ==========================================================

    def performance(

        self,

    ) -> Dict:

        return ScannerEngine.performance_metrics(

            self.scanners

        )


# ==========================================================
# HEALTH CHECK
# ==========================================================

    def health(

        self,

    ) -> Dict:

        return {

            "Executor":

                True,

            "Scanner Count":

                len(

                    self.scanners

                ),

            "Records":

                len(

                    self.records

                ),

            "Running":

                self.is_running,

            "Progress":

                self.progress,

            "Market Open":

                self.market_open(),

        }


# ==========================================================
# PRODUCTION SNAPSHOT
# ==========================================================

    def snapshot(

        self,

    ) -> Dict:

        return {

            "Dashboard":

                self.dashboard(),

            "Summary":

                self.summary,

            "Performance":

                self.performance(),

            "Health":

                self.health(),

            "Generated":

                datetime.now(),

        }
    # ==========================================================
# FILTER BY MINIMUM SCORE
# ==========================================================

    def filter_by_score(

        self,

        minimum_score: float = 75,

    ) -> List[ScannerEngine]:

        return [

            scanner

            for scanner in self.scanners

            if scanner.priority_score()

            >= minimum_score

        ]


# ==========================================================
# FILTER BY CONFIDENCE
# ==========================================================

    def filter_by_confidence(

        self,

        minimum_confidence: float = 70,

    ) -> List[ScannerEngine]:

        return [

            scanner

            for scanner in self.scanners

            if scanner.confidence_score()

            >= minimum_confidence

        ]


# ==========================================================
# FILTER BY CATEGORY
# ==========================================================

    def filter_by_category(

        self,

        category: str,

    ) -> List[ScannerEngine]:

        return [

            scanner

            for scanner in self.scanners

            if scanner.trade_category()["category"]

            == category

        ]


# ==========================================================
# FILTER BY SECTOR
# ==========================================================

    def filter_by_sector(

        self,

        sector: str,

    ) -> List[ScannerEngine]:

        return [

            scanner

            for scanner in self.scanners

            if scanner.sector.lower()

            == sector.lower()

        ]


# ==========================================================
# BATCH EXECUTION
# ==========================================================

    def execute_batch(

        self,

        symbols: List[str],

    ) -> List[ScanRecord]:

        output = []

        for symbol in symbols:

            record = self.process_symbol(

                symbol

            )

            if record:

                output.append(

                    record

                )

        return output


# ==========================================================
# EXECUTE SECTOR
# ==========================================================

    def execute_sector(

        self,

        sector: str,

    ) -> List[ScanRecord]:

        symbols = [

            symbol

            for symbol, sec

            in self.sectors.items()

            if sec.lower()

            == sector.lower()

        ]

        return self.execute_batch(

            symbols

        )


# ==========================================================
# RETRY FAILED SYMBOLS
# ==========================================================

    def retry_failed(

        self,

        retries: int = 1,

    ) -> None:

        failed_symbols = [

            symbol

            for symbol

            in self.market_data

            if symbol

            not in [

                record.symbol

                for record

                in self.records

            ]

        ]

        for _ in range(

            retries

        ):

            if not failed_symbols:

                break

            remaining = []

            for symbol in failed_symbols:

                record = self.process_symbol(

                    symbol

                )

                if record is None:

                    remaining.append(

                        symbol

                    )

            failed_symbols = remaining


# ==========================================================
# EXECUTE BY SECTOR
# ==========================================================

    def execute_all_sectors(

        self,

    ) -> Dict[str, List[ScanRecord]]:

        results = {}

        for sector in sorted(

            set(

                self.sectors.values()

            )

        ):

            results[sector] = (

                self.execute_sector(

                    sector

                )

            )

        return results


# ==========================================================
# SCAN LOG
# ==========================================================

    def scan_log(

        self,

    ) -> pd.DataFrame:

        rows = []

        for record in self.records:

            rows.append(

                {

                    "Time":

                        record.timestamp,

                    "Symbol":

                        record.symbol,

                    "Sector":

                        record.sector,

                    "Category":

                        record.category,

                    "Score":

                        record.score,

                    "Signal":

                        record.signal,

                    "Recommendation":

                        record.recommendation,

                }

            )

        return pd.DataFrame(

            rows

        )


# ==========================================================
# AUDIT TRAIL
# ==========================================================

    def audit_trail(

        self,

    ) -> Dict:

        return {

            "Started":

                self.summary.started_at,

            "Finished":

                self.summary.finished_at,

            "Duration":

                self.summary.duration,

            "Scanned":

                self.summary.total_scanned,

            "Success":

                self.summary.successful,

            "Failed":

                self.summary.failed,

        }


# ==========================================================
# ENTERPRISE REPORT
# ==========================================================

    def enterprise_report(

        self,

    ) -> Dict:

        return {

            "Audit":

                self.audit_trail(),

            "Dashboard":

                self.dashboard(),

            "Performance":

                self.performance(),

            "Health":

                self.health(),

            "History":

                self.history(),

        }


# ==========================================================
# MASTER ORCHESTRATION
# ==========================================================

    def orchestrate(

        self,

    ) -> Dict:

        self.execute()

        self.rank_scanners()

        self.retry_failed()

        return self.enterprise_report()
    # ==========================================================
# PARALLEL SECTOR EXECUTION
# ==========================================================

    def execute_sectors_parallel(

        self,

    ) -> Dict[str, List[ScanRecord]]:

        results = {}

        sectors = sorted(

            set(

                self.sectors.values()

            )

        )

        with ThreadPoolExecutor(

            max_workers=min(

                self.max_workers,

                len(sectors),

            )

        ) as executor:

            futures = {

                executor.submit(

                    self.execute_sector,

                    sector,

                ): sector

                for sector in sectors

            }

            for future in as_completed(

                futures

            ):

                sector = futures[future]

                try:

                    results[sector] = future.result()

                except Exception:

                    results[sector] = []

        return results


# ==========================================================
# SCAN QUEUE
# ==========================================================

    def build_scan_queue(

        self,

    ) -> List[str]:

        return sorted(

            self.market_data.keys()

        )


# ==========================================================
# EXECUTE QUEUE
# ==========================================================

    def execute_queue(

        self,

        queue: List[str],

    ) -> List[ScanRecord]:

        output = []

        for symbol in queue:

            if self.stop_requested:

                break

            result = self.process_symbol(

                symbol

            )

            if result:

                output.append(

                    result

                )

        return output


# ==========================================================
# MEMORY CLEANUP
# ==========================================================

    def cleanup(

        self,

    ) -> None:

        self.records = list(

            self.records

        )

        self.scanners = list(

            self.scanners

        )


# ==========================================================
# REMOVE DUPLICATES
# ==========================================================

    def remove_duplicates(

        self,

    ) -> None:

        unique = {}

        for scanner in self.scanners:

            unique[scanner.symbol] = scanner

        self.scanners = list(

            unique.values()

        )

        unique_records = {}

        for record in self.records:

            unique_records[record.symbol] = record

        self.records = list(

            unique_records.values()

        )


# ==========================================================
# SORT RESULTS
# ==========================================================

    def sort_results(

        self,

    ) -> None:

        self.scanners.sort(

            key=lambda x:

            x.priority_score(),

            reverse=True,

        )

        self.records.sort(

            key=lambda x:

            x.score,

            reverse=True,

        )


# ==========================================================
# PERFORMANCE OPTIMIZER
# ==========================================================

    def optimize(

        self,

    ) -> None:

        self.remove_duplicates()

        self.sort_results()

        self.cleanup()


# ==========================================================
# INCREMENTAL SCAN
# ==========================================================

    def incremental_scan(

        self,

        symbols: List[str],

    ) -> List[ScanRecord]:

        output = []

        for symbol in symbols:

            scanner = self.create_scanner(

                symbol

            )

            if scanner is None:

                continue

            self.scanners.append(

                scanner

            )

            record = self.process_symbol(

                symbol

            )

            if record:

                output.append(

                    record

                )

        self.optimize()

        return output


# ==========================================================
# REFRESH SINGLE SYMBOL
# ==========================================================

    def refresh_symbol(

        self,

        symbol: str,

    ) -> Optional[ScanRecord]:

        scanner = self.create_scanner(

            symbol

        )

        if scanner is None:

            return None

        return self.process_symbol(

            symbol

        )


# ==========================================================
# EXECUTION MANAGER
# ==========================================================

    def execute_optimized(

        self,

    ) -> Dict:

        self.start_scan()

        try:

            queue = self.build_scan_queue()

            self.execute_queue(

                queue

            )

            self.optimize()

        finally:

            self.finish_scan()

        return self.dashboard()


# ==========================================================
# CACHE SNAPSHOT
# ==========================================================

    def cache_snapshot(

        self,

    ) -> Dict:

        return {

            "Symbols":

                len(

                    self.market_data

                ),

            "Scanners":

                len(

                    self.scanners

                ),

            "Records":

                len(

                    self.records

                ),

            "Last Scan":

                self.last_scan,

        }


# ==========================================================
# EXECUTION STATISTICS
# ==========================================================

    def execution_statistics(

        self,

    ) -> Dict:

        return {

            "Workers":

                self.max_workers,

            "Progress":

                self.progress,

            "Successful":

                self.success_count,

            "Failed":

                self.failed_count,

            "Cached":

                len(

                    self.records

                ),

            "Running":

                self.busy,

        }
    # ==========================================================
# LIVE WATCHLIST
# ==========================================================

    def live_watchlist(
        self,
        limit: int = MAX_TOP_STOCKS,
    ) -> pd.DataFrame:

        self.rank_scanners()

        scanners = self.scanners[:limit]

        rows = []

        for scanner in scanners:

            rows.append(
                {
                    "Symbol": scanner.symbol,
                    "Sector": scanner.sector,
                    "Price": scanner.last_price(),
                    "Signal": scanner.signal(),
                    "Recommendation": scanner.recommendation(),
                    "Confidence": scanner.confidence_score(),
                    "Score": scanner.priority_score(),
                }
            )

        return pd.DataFrame(rows)


# ==========================================================
# LIVE LEADERBOARD
# ==========================================================

    def leaderboard(
        self,
        limit: int = 20,
    ) -> pd.DataFrame:

        self.sort_results()

        return pd.DataFrame(
            [
                {
                    "Rank": i + 1,
                    "Symbol": record.symbol,
                    "Sector": record.sector,
                    "Score": record.score,
                    "Signal": record.signal,
                    "Recommendation": record.recommendation,
                }
                for i, record in enumerate(
                    self.records[:limit]
                )
            ]
        )


# ==========================================================
# MOMENTUM LEADERS
# ==========================================================

    def momentum_leaders(
        self,
        minimum_score: float = 85,
    ) -> List[ScannerEngine]:

        return [
            scanner
            for scanner in self.scanners
            if (
                scanner.priority_score()
                >= minimum_score
            )
            and (
                scanner.signal().upper()
                in ["BUY", "STRONG BUY"]
            )
        ]


# ==========================================================
# TOP GAINERS
# ==========================================================

    def top_gainers(
        self,
        limit: int = 10,
    ) -> List[ScannerEngine]:

        ranked = sorted(
            self.scanners,
            key=lambda s: s.change_percent(),
            reverse=True,
        )

        return ranked[:limit]


# ==========================================================
# TOP LOSERS
# ==========================================================

    def top_losers(
        self,
        limit: int = 10,
    ) -> List[ScannerEngine]:

        ranked = sorted(
            self.scanners,
            key=lambda s: s.change_percent(),
        )

        return ranked[:limit]


# ==========================================================
# SECTOR ROTATION MONITOR
# ==========================================================

    def sector_rotation_monitor(
        self,
    ) -> pd.DataFrame:

        return ScannerEngine.sector_rotation_dashboard(
            self.scanners
        )


# ==========================================================
# MARKET BREADTH
# ==========================================================

    def market_breadth_dashboard(
        self,
    ) -> Dict:

        return ScannerEngine.market_breadth(
            self.scanners
        )


# ==========================================================
# INTRADAY OPPORTUNITIES
# ==========================================================

    def intraday_stream(
        self,
        limit: int = 15,
    ) -> List[Dict]:

        return ScannerEngine.top_intraday(
            self.scanners,
            limit,
        )


# ==========================================================
# AI CONFIDENCE DASHBOARD
# ==========================================================

    def confidence_dashboard(
        self,
    ) -> pd.DataFrame:

        rows = []

        for scanner in self.scanners:

            rows.append(
                {
                    "Symbol": scanner.symbol,
                    "Confidence": scanner.confidence_score(),
                    "AI Score": scanner.priority_score(),
                    "Signal": scanner.signal(),
                    "Category": scanner.trade_category()["category"],
                }
            )

        return pd.DataFrame(rows).sort_values(
            "Confidence",
            ascending=False,
        )


# ==========================================================
# PRIORITY ALERTS
# ==========================================================

    def priority_alerts(
        self,
        minimum_score: float = 90,
    ) -> List[Dict]:

        alerts = []

        for scanner in self.scanners:

            if (
                scanner.priority_score()
                >= minimum_score
            ):

                alerts.append(
                    {
                        "Symbol": scanner.symbol,
                        "Sector": scanner.sector,
                        "Signal": scanner.signal(),
                        "Score": scanner.priority_score(),
                        "Confidence": scanner.confidence_score(),
                        "Recommendation": scanner.recommendation(),
                    }
                )

        alerts.sort(
            key=lambda x: x["Score"],
            reverse=True,
        )

        return alerts


# ==========================================================
# LIVE MARKET DASHBOARD
# ==========================================================

    def live_dashboard(
        self,
    ) -> Dict:

        return {

            "Leaderboard":
                self.leaderboard(),

            "Watchlist":
                self.live_watchlist(),

            "Momentum":
                self.momentum_leaders(),

            "Top Gainers":
                self.top_gainers(),

            "Top Losers":
                self.top_losers(),

            "Sector Rotation":
                self.sector_rotation_monitor(),

            "Market Breadth":
                self.market_breadth_dashboard(),

            "Intraday":
                self.intraday_stream(),

            "AI Confidence":
                self.confidence_dashboard(),

            "Priority Alerts":
                self.priority_alerts(),

            "Updated":
                datetime.now(),

        }
    # ==========================================================
# SCHEDULED SCAN
# ==========================================================

    def scheduled_scan(
        self,
        interval_seconds: int = DEFAULT_REFRESH_SECONDS,
    ) -> None:

        self.update_status(
            "Scheduled scanner started."
        )

        while not self.stop_requested:

            start = time.time()

            try:
                self.execute_optimized()
            except Exception as exc:
                self.log_error(exc)

            elapsed = time.time() - start
            remaining = max(
                0,
                interval_seconds - elapsed,
            )

            time.sleep(remaining)

        self.update_status(
            "Scheduled scanner stopped."
        )


# ==========================================================
# START SCHEDULER
# ==========================================================

    def start_scheduler(
        self,
        interval_seconds: int = DEFAULT_REFRESH_SECONDS,
    ) -> threading.Thread:

        thread = threading.Thread(
            target=self.scheduled_scan,
            kwargs={
                "interval_seconds":
                    interval_seconds
            },
            daemon=True,
        )

        thread.start()

        return thread


# ==========================================================
# WATCHLIST SYNC
# ==========================================================

    def synchronize_watchlist(
        self,
    ) -> pd.DataFrame:

        watchlist = self.live_watchlist()

        watchlist["Updated"] = datetime.now()

        return watchlist


# ==========================================================
# ALERT HISTORY
# ==========================================================

    def alert_history(
        self,
    ) -> List[Dict]:

        if not hasattr(
            self,
            "_alert_history",
        ):

            self._alert_history = []

        alerts = self.priority_alerts()

        self._alert_history.extend(
            alerts
        )

        return self._alert_history


# ==========================================================
# NOTIFICATION QUEUE
# ==========================================================

    def notification_queue(
        self,
    ) -> List[Dict]:

        return sorted(

            self.priority_alerts(),

            key=lambda x:

            x["Confidence"],

            reverse=True,

        )


# ==========================================================
# LOG ERROR
# ==========================================================

    def log_error(
        self,
        error: Exception,
    ) -> None:

        if not hasattr(
            self,
            "_errors",
        ):

            self._errors = []

        self._errors.append(

            {

                "Time":

                    datetime.now(),

                "Error":

                    str(error),

            }

        )


# ==========================================================
# ERROR HISTORY
# ==========================================================

    def error_history(
        self,
    ) -> pd.DataFrame:

        if not hasattr(
            self,
            "_errors",
        ):

            return pd.DataFrame()

        return pd.DataFrame(

            self._errors

        )


# ==========================================================
# SYSTEM METRICS
# ==========================================================

    def system_metrics(
        self,
    ) -> Dict:

        return {

            "CPU Workers":

                self.max_workers,

            "Symbols":

                len(

                    self.market_data

                ),

            "Scanners":

                len(

                    self.scanners

                ),

            "Records":

                len(

                    self.records

                ),

            "Running":

                self.busy,

            "Progress":

                self.progress,

            "Timestamp":

                datetime.now(),

        }


# ==========================================================
# RUNTIME DIAGNOSTICS
# ==========================================================

    def diagnostics(
        self,
    ) -> Dict:

        return {

            "Health":

                self.health(),

            "Performance":

                self.performance(),

            "Execution":

                self.execution_statistics(),

            "Errors":

                len(

                    self.error_history()

                ),

            "Cache":

                self.cache_snapshot(),

        }


# ==========================================================
# BACKUP STATE
# ==========================================================

    def backup_state(
        self,
    ) -> Dict:

        return {

            "Summary":

                self.summary,

            "Records":

                self.records,

            "Last Scan":

                self.last_scan,

            "Timestamp":

                datetime.now(),

        }


# ==========================================================
# RESTORE STATE
# ==========================================================

    def restore_state(
        self,
        state: Dict,
    ) -> None:

        self.summary = state.get(
            "Summary",
            self.summary,
        )

        self.records = state.get(
            "Records",
            [],
        )

        self.last_scan = state.get(
            "Last Scan",
            None,
        )


# ==========================================================
# ENTERPRISE MONITOR
# ==========================================================

    def monitor(
        self,
    ) -> Dict:

        return {

            "Diagnostics":
                self.diagnostics(),

            "Metrics":
                self.system_metrics(),

            "Alert Queue":
                self.notification_queue(),

            "Alert History":
                self.alert_history(),

            "Watchlist":
                self.synchronize_watchlist(),

            "Updated":
                datetime.now(),

        }
    # ==========================================================
# VALIDATE CONFIGURATION
# ==========================================================

    def validate_configuration(
        self,
    ) -> bool:

        if self.max_workers <= 0:
            raise ValueError(
                "max_workers must be greater than zero."
            )

        if not isinstance(
            self.market_data,
            dict,
        ):
            raise TypeError(
                "market_data must be a dictionary."
            )

        if self.sectors is None:
            self.sectors = {}

        return True


# ==========================================================
# STARTUP CHECKS
# ==========================================================

    def startup_checks(
        self,
    ) -> Dict:

        return {
            "Configuration":
                self.validate_configuration(),
            "Market Data":
                len(self.market_data) > 0,
            "Sector Data":
                len(self.sectors) > 0,
            "Executor Ready":
                not self.busy,
            "Timestamp":
                datetime.now(),
        }


# ==========================================================
# RECOVERY MANAGER
# ==========================================================

    def recover(
        self,
    ) -> bool:

        try:

            self.stop_requested = False

            self.is_running = False

            self.cleanup()

            self.optimize()

            return True

        except Exception as exc:

            self.log_error(exc)

            return False


# ==========================================================
# PREPARE EXECUTION
# ==========================================================

    def prepare(
        self,
    ) -> None:

        self.validate_configuration()

        self.reset()

        self.update_status(
            "Preparing scanner..."
        )


# ==========================================================
# FINAL EXECUTION PIPELINE
# ==========================================================

    def run_pipeline(
        self,
    ) -> Dict:

        self.prepare()

        self.execute()

        self.rank_scanners()

        self.optimize()

        return self.dashboard()


# ==========================================================
# ENTERPRISE INITIALIZATION
# ==========================================================

    def initialize(
        self,
    ) -> None:

        self.prepare()

        self.update_status(
            "Scanner initialized successfully."
        )


# ==========================================================
# PAUSE EXECUTION
# ==========================================================

    def pause(
        self,
    ) -> None:

        self.is_running = False

        self.update_status(
            "Scanner paused."
        )


# ==========================================================
# RESUME EXECUTION
# ==========================================================

    def resume(
        self,
    ) -> None:

        if self.stop_requested:
            self.stop_requested = False

        self.is_running = True

        self.update_status(
            "Scanner resumed."
        )


# ==========================================================
# GRACEFUL SHUTDOWN
# ==========================================================

    def shutdown(
        self,
    ) -> None:

        self.stop_requested = True

        self.is_running = False

        self.update_status(
            "Shutting down scanner..."
        )

        self.cleanup()


# ==========================================================
# RELEASE RESOURCES
# ==========================================================

    def release_resources(
        self,
    ) -> None:

        self.records.clear()

        self.scanners.clear()

        self.market_data.clear()

        self.sectors.clear()


# ==========================================================
# TERMINATE
# ==========================================================

    def terminate(
        self,
    ) -> None:

        self.shutdown()

        self.release_resources()

        self.update_status(
            "Scanner terminated."
        )


# ==========================================================
# RESTART
# ==========================================================

    def restart(
        self,
    ) -> None:

        self.shutdown()

        self.recover()

        self.initialize()


# ==========================================================
# PRODUCTION READY
# ==========================================================

    @property
    def production_ready(
        self,
    ) -> bool:

        try:

            checks = self.startup_checks()

            return all(
                value
                for key, value
                in checks.items()
                if isinstance(
                    value,
                    bool,
                )
            )

        except Exception:

            return False


# ==========================================================
# FINAL STATUS
# ==========================================================

    def status(
        self,
    ) -> Dict:

        return {

            "Running":
                self.is_running,

            "Busy":
                self.busy,

            "Production Ready":
                self.production_ready,

            "Progress":
                self.progress,

            "Records":
                len(self.records),

            "Last Scan":
                self.last_scan,

            "Timestamp":
                datetime.now(),

        }
    # ==========================================================
# SUMMARY SERIALIZATION
# ==========================================================

    def summary_dict(
        self,
    ) -> Dict:

        return {

            "started_at":
                self.summary.started_at,

            "finished_at":
                self.summary.finished_at,

            "duration":
                self.summary.duration,

            "total_scanned":
                self.summary.total_scanned,

            "successful":
                self.summary.successful,

            "failed":
                self.summary.failed,

        }


# ==========================================================
# RECORDS DATAFRAME
# ==========================================================

    def records_dataframe(
        self,
    ) -> pd.DataFrame:

        return pd.DataFrame(

            [

                vars(record)

                for record in self.records

            ]

        )


# ==========================================================
# VERIFY DATA INTEGRITY
# ==========================================================

    def verify_integrity(
        self,
    ) -> bool:

        if len(self.records) != len(set(r.symbol for r in self.records)):
            return False

        if len(self.scanners) != len(set(s.symbol for s in self.scanners)):
            return False

        return True


# ==========================================================
# EXPORT REPORT DICTIONARY
# ==========================================================

    def export_report(
        self,
    ) -> Dict:

        return {

            "version":
                self.version(),

            "summary":
                self.summary_dict(),

            "statistics":
                self.statistics(),

            "dashboard":
                self.dashboard(),

            "records":
                self.records_dataframe(),

        }


# ==========================================================
# IMPORT PREVIOUS RECORDS
# ==========================================================

    def load_records(
        self,
        records: List[ScanRecord],
    ) -> None:

        self.records = records.copy()


# ==========================================================
# CLEAR RESULTS
# ==========================================================

    def clear_results(
        self,
    ) -> None:

        self.records.clear()

        self.scanners.clear()


# ==========================================================
# DEBUG INFORMATION
# ==========================================================

    def debug_info(
        self,
    ) -> Dict:

        return {

            "Executor":
                self.__class__.__name__,

            "Version":
                self.version(),

            "Python":
                platform.python_version(),

            "Workers":
                self.max_workers,

            "Market Data":
                len(self.market_data),

            "Scanners":
                len(self.scanners),

            "Records":
                len(self.records),

            "Integrity":
                self.verify_integrity(),

        }


# ==========================================================
# BUILD INFORMATION
# ==========================================================

    @staticmethod
    def build_info(
    ) -> Dict:

        return {

            "Application":
                "StockVersity Scanner Pro",

            "Version":
                "4.0",

            "Powered By":
                "AI",

            "Environment":
                "Production",

        }


# ==========================================================
# ABOUT
# ==========================================================

    def about(
        self,
    ) -> str:

        return (

            "StockVersity Scanner Pro v4.0 | "

            "Powered by AI | "

            "Enterprise Scanner Engine"

        )


# ==========================================================
# FINAL SNAPSHOT
# ==========================================================

    def final_snapshot(
        self,
    ) -> Dict:

        return {

            "About":
                self.about(),

            "Build":
                self.build_info(),

            "Status":
                self.status(),

            "Summary":
                self.summary_dict(),

            "Integrity":
                self.verify_integrity(),

            "Generated":
                datetime.now(),

        }


# ==========================================================
# STRING REPRESENTATION
# ==========================================================

    def __str__(
        self,
    ) -> str:

        return (

            f"ScannerExecutor("

            f"symbols={len(self.market_data)}, "

            f"records={len(self.records)}, "

            f"workers={self.max_workers})"

        )


# ==========================================================
# REPRESENTATION
# ==========================================================

    def __repr__(
        self,
    ) -> str:

        return self.__str__()