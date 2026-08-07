from __future__ import annotations

import logging
import threading
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any

from core.scanner.signal import Signal
from core.scanner.base_scanner import BaseScanner
from core.scanners.momentum_scanner import MomentumScanner
from core.pattern_engine import (
    PatternEngine,
    PatternResult,
)
from core.market_analyzer import (
    MarketAnalyzer,
)
from core.stock_ranker import (
    StockRanker,
    RankResult,
)
from core.data_manager import (
    DataManager,
)

# ==========================================================
# SCAN MODE
# ==========================================================

class ScanMode(Enum):
    INTRADAY = "Intraday"
    SWING = "Swing"
    POSITIONAL = "Positional"
    CUSTOM = "Custom"


# ==========================================================
# SCAN STATUS
# ==========================================================

class ScanStatus(Enum):
    IDLE = "Idle"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"


# ==========================================================
# OPPORTUNITY
# ==========================================================

@dataclass
class Opportunity:

    symbol: str

    timeframe: str

    mode: ScanMode

    signal: Optional[Signal] = None

    pattern: Optional[PatternResult] = None

    ranking: Optional[RankResult] = None

    score: float = 0.0

    confidence: float = 0.0

    recommendation: str = ""

    created: datetime = field(
        default_factory=datetime.now
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ==========================================================
# SCAN SUMMARY
# ==========================================================

@dataclass
class ScanSummary:

    started: datetime

    finished: Optional[datetime] = None

    total_symbols: int = 0

    scanned: int = 0

    opportunities: int = 0

    failed: int = 0

    elapsed_seconds: float = 0.0

    status: ScanStatus = ScanStatus.IDLE


# ==========================================================
# SCREENER ENGINE
# ==========================================================

class ScreenerEngine:

    VERSION = "1.0.0"

    def __init__(
        self,
        data_manager: DataManager,
        market_analyzer: MarketAnalyzer,
    ):

        self.logger = logging.getLogger(
            self.__class__.__name__
        )

        self.lock = threading.RLock()

        self.data_manager = data_manager

        self.market = market_analyzer

        self.pattern_engine = PatternEngine()

        self.ranker = StockRanker()

        self.momentum = MomentumScanner()

        self.status = ScanStatus.IDLE

        self.summary = ScanSummary(
            started=datetime.now()
        )

        self.opportunities: List[
            Opportunity
        ] = []

        self.watchlist: List[str] = []

        self.cancel_requested = False

        self.logger.info(
            "Screener Engine initialized."
        )
            # ==========================================================
    # RESET
    # ==========================================================

    def reset(self) -> None:
        """
        Reset engine state.
        """

        with self.lock:

            self.cancel_requested = False

            self.status = ScanStatus.IDLE

            self.opportunities.clear()

            self.ranker.clear()

            self.summary = ScanSummary(
                started=datetime.now()
            )

    # ==========================================================
    # WATCHLIST
    # ==========================================================

    def add_symbol(
        self,
        symbol: str,
    ) -> None:
        """
        Add symbol to watchlist.
        """

        symbol = symbol.upper().strip()

        if symbol and symbol not in self.watchlist:
            self.watchlist.append(symbol)

    def add_symbols(
        self,
        symbols: List[str],
    ) -> None:
        """
        Add multiple symbols.
        """

        for symbol in symbols:
            self.add_symbol(symbol)

    def remove_symbol(
        self,
        symbol: str,
    ) -> None:
        """
        Remove symbol.
        """

        symbol = symbol.upper().strip()

        if symbol in self.watchlist:
            self.watchlist.remove(symbol)

    def clear_watchlist(
        self,
    ) -> None:
        """
        Clear watchlist.
        """

        self.watchlist.clear()

    @property
    def symbol_count(
        self,
    ) -> int:
        """
        Total watchlist symbols.
        """

        return len(self.watchlist)

    # ==========================================================
    # TIMEFRAME
    # ==========================================================

    def timeframe_for_mode(
        self,
        mode: ScanMode,
    ) -> str:
        """
        Default timeframe.
        """

        mapping = {

            ScanMode.INTRADAY: "15m",

            ScanMode.SWING: "1h",

            ScanMode.POSITIONAL: "1d",

            ScanMode.CUSTOM: "1h",

        }

        return mapping.get(
            mode,
            "1h",
        )

    # ==========================================================
    # SCAN SETTINGS
    # ==========================================================

    def default_filters(
        self,
        mode: ScanMode,
    ) -> Dict[str, Any]:
        """
        Default institutional filters.
        """

        if mode == ScanMode.INTRADAY:

            return {

                "minimum_price": 200,

                "minimum_volume": 500000,

                "minimum_rvol": 1.5,

                "minimum_market_cap": 1000,

                "adx": 20,

                "require_vwap": True,

                "require_breakout": True,

            }

        if mode == ScanMode.SWING:

            return {

                "minimum_price": 150,

                "minimum_volume": 300000,

                "minimum_rvol": 1.2,

                "minimum_market_cap": 1000,

                "adx": 18,

                "require_breakout": True,

            }

        return {

            "minimum_price": 100,

            "minimum_volume": 200000,

            "minimum_market_cap": 1000,

            "minimum_rvol": 1.0,

            "adx": 15,

        }

    # ==========================================================
    # STATUS
    # ==========================================================

    @property
    def is_running(
        self,
    ) -> bool:

        return (
            self.status
            == ScanStatus.RUNNING
        )

    @property
    def is_cancelled(
        self,
    ) -> bool:

        return self.cancel_requested

    # ==========================================================
    # CANCEL
    # ==========================================================

    def cancel_scan(
        self,
    ) -> None:
        """
        Cancel active scan.
        """

        self.cancel_requested = True

        self.status = ScanStatus.CANCELLED

    # ==========================================================
    # START
    # ==========================================================

    def start_scan(
        self,
    ) -> None:
        """
        Initialize scan.
        """

        self.summary = ScanSummary(
            started=datetime.now(),
            total_symbols=len(
                self.watchlist
            ),
            status=ScanStatus.RUNNING,
        )

        self.status = ScanStatus.RUNNING

    # ==========================================================
    # COMPLETE
    # ==========================================================

    def complete_scan(
        self,
    ) -> None:
        """
        Finalize scan.
        """

        self.summary.finished = datetime.now()

        self.summary.elapsed_seconds = (

            self.summary.finished

            - self.summary.started

        ).total_seconds()

        self.summary.opportunities = len(
            self.opportunities
        )

        self.summary.status = (
            ScanStatus.COMPLETED
        )

        self.status = ScanStatus.COMPLETED

    # ==========================================================
    # FAILURE
    # ==========================================================

    def record_failure(
        self,
    ) -> None:

        self.summary.failed += 1

    # ==========================================================
    # PROGRESS
    # ==========================================================

    def update_progress(
        self,
    ) -> None:

        self.summary.scanned += 1
            # ==========================================================
    # SCAN SYMBOL
    # ==========================================================

    def scan_symbol(
        self,
        symbol: str,
        mode: ScanMode,
    ) -> Optional[Opportunity]:
        """
        Scan a single symbol and return an opportunity
        if all institutional filters pass.
        """

        if self.cancel_requested:
            return None

        try:

            timeframe = self.timeframe_for_mode(
                mode
            )

            # ---------------------------------------------
            # Load historical candles
            # ---------------------------------------------

            candles = self.data_manager.get_historical_data(
                symbol=symbol,
                timeframe=timeframe,
            )

            if candles is None:
                return None

            if len(candles) < 250:
                return None

            # ---------------------------------------------
            # Market Direction
            # ---------------------------------------------

            market = self.market.market_dashboard()

            market_strength = float(

                market.get(
                    "market_strength",
                    50,
                )

            )

            market_aligned = bool(

                market.get(
                    "bullish",
                    True,
                )

            )

            # ---------------------------------------------
            # Pattern Detection
            # ---------------------------------------------

            pattern = self.pattern_engine.detect_best_pattern(
                candles
            )

            if pattern is None:
                return None

            # ---------------------------------------------
            # Momentum Scanner
            # ---------------------------------------------

            signal = self.momentum.scan(
                symbol=symbol,
                data=candles,
            )

            if signal is None:
                return None

            # ---------------------------------------------
            # Ranking
            # ---------------------------------------------

            ranking = self.ranker.rank_stock(

                symbol=symbol,

                timeframe=timeframe,

                pattern=pattern,

                signal=signal,

                relative_strength=getattr(
                    signal,
                    "relative_strength",
                    50,
                ),

                relative_volume=getattr(
                    signal,
                    "relative_volume",
                    1.0,
                ),

                delivery_percent=getattr(
                    signal,
                    "delivery_percentage",
                    0,
                ),

                sector_strength=getattr(
                    signal,
                    "sector_strength",
                    50,
                ),

                institutional_buying=getattr(
                    signal,
                    "institutional_buying",
                    False,
                ),

                block_trade=getattr(
                    signal,
                    "block_trade",
                    False,
                ),

                fii_positive=getattr(
                    signal,
                    "fii_positive",
                    False,
                ),

                atr_percent=getattr(
                    signal,
                    "atr_percent",
                    3,
                ),

                market_strength=market_strength,

                breakout=getattr(
                    pattern,
                    "breakout_confirmed",
                    False,
                ),

                multi_timeframe=getattr(
                    signal,
                    "multi_timeframe_confirmation",
                    False,
                ),

                market_aligned=market_aligned,

            )

            # ---------------------------------------------
            # Opportunity
            # ---------------------------------------------

            opportunity = Opportunity(

                symbol=symbol,

                timeframe=timeframe,

                mode=mode,

                signal=signal,

                pattern=pattern,

                ranking=ranking,

                score=ranking.final_score,

                confidence=ranking.confidence,

                recommendation=ranking.recommendation,

                metadata={

                    "pattern": pattern.pattern_type.value,

                    "institutional_rating":
                        ranking.institutional_rating.value,

                    "entry_grade":
                        ranking.entry_grade.value,

                },

            )

            self.opportunities.append(
                opportunity
            )

            return opportunity

        except Exception as exc:

            self.logger.exception(

                "Scan failed for %s : %s",

                symbol,

                exc,

            )

            self.record_failure()

            return None

        finally:

            self.update_progress()
            from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)

    # ==========================================================
    # SCAN WATCHLIST
    # ==========================================================

    def scan_watchlist(
        self,
        mode: ScanMode = ScanMode.INTRADAY,
        max_workers: int = 8,
    ) -> List[Opportunity]:
        """
        Scan complete watchlist using parallel workers.
        """

        self.reset()

        self.start_scan()

        if not self.watchlist:

            self.logger.warning(
                "Watchlist is empty."
            )

            self.complete_scan()

            return []

        with ThreadPoolExecutor(

            max_workers=max_workers,

            thread_name_prefix="Scanner",

        ) as executor:

            futures = {

                executor.submit(

                    self.scan_symbol,

                    symbol,

                    mode,

                ): symbol

                for symbol in self.watchlist

            }

            for future in as_completed(
                futures
            ):

                if self.cancel_requested:
                    break

                symbol = futures[future]

                try:

                    opportunity = future.result()

                    if opportunity:

                        self.logger.info(

                            "%s scored %.2f",

                            symbol,

                            opportunity.score,

                        )

                except Exception as exc:

                    self.logger.exception(

                        "Scanner worker failed (%s): %s",

                        symbol,

                        exc,

                    )

        self.ranker.finalize_rankings()

        self._sync_ranks()

        self._sort_opportunities()

        self.complete_scan()

        return self.opportunities

    # ==========================================================
    # SYNC RANKS
    # ==========================================================

    def _sync_ranks(
        self,
    ) -> None:
        """
        Synchronize RankResult back to Opportunity.
        """

        rank_map = {

            item.symbol: item

            for item

            in self.ranker.results

        }

        for opportunity in self.opportunities:

            ranked = rank_map.get(
                opportunity.symbol
            )

            if ranked is None:
                continue

            opportunity.ranking = ranked

            opportunity.score = (
                ranked.final_score
            )

            opportunity.confidence = (
                ranked.confidence
            )

            opportunity.recommendation = (
                ranked.recommendation
            )

    # ==========================================================
    # SORT
    # ==========================================================

    def _sort_opportunities(
        self,
    ) -> None:
        """
        Highest score first.
        """

        self.opportunities.sort(

            key=lambda x: x.score,

            reverse=True,

        )

    # ==========================================================
    # TOP OPPORTUNITIES
    # ==========================================================

    def top_opportunities(
        self,
        limit: int = 10,
    ) -> List[Opportunity]:
        """
        Return best opportunities.
        """

        self._sort_opportunities()

        return self.opportunities[:limit]

    # ==========================================================
    # ELITE OPPORTUNITIES
    # ==========================================================

    def elite_opportunities(
        self,
    ) -> List[Opportunity]:
        """
        Elite institutional opportunities.
        """

        return [

            opportunity

            for opportunity

            in self.opportunities

            if (

                opportunity.ranking

                and

                opportunity.ranking.institutional_rating.value

                == "Elite"

            )

        ]

    # ==========================================================
    # BEST SYMBOL
    # ==========================================================

    def best_symbol(
        self,
    ) -> Optional[Opportunity]:
        """
        Return highest-ranked stock.
        """

        if not self.opportunities:
            return None

        self._sort_opportunities()

        return self.opportunities[0]

    # ==========================================================
    # FILTER BY SCORE
    # ==========================================================

    def minimum_score(
        self,
        score: float,
    ) -> List[Opportunity]:
        """
        Minimum score filter.
        """

        return [

            item

            for item

            in self.opportunities

            if item.score >= score

        ]
        # ==========================================================
    # PRICE FILTER
    # ==========================================================

    def _price_filter(
        self,
        price: float,
        minimum_price: float,
    ) -> bool:
        """
        Reject penny stocks.
        """

        return price >= minimum_price

    # ==========================================================
    # MARKET CAP FILTER
    # ==========================================================

    def _market_cap_filter(
        self,
        market_cap: float,
        minimum_market_cap: float,
    ) -> bool:
        """
        Market cap in Crores.
        """

        return market_cap >= minimum_market_cap

    # ==========================================================
    # LIQUIDITY FILTER
    # ==========================================================

    def _volume_filter(
        self,
        volume: float,
        minimum_volume: float,
    ) -> bool:

        return volume >= minimum_volume

    # ==========================================================
    # RVOL FILTER
    # ==========================================================

    def _relative_volume_filter(
        self,
        rvol: float,
        minimum_rvol: float,
    ) -> bool:

        return rvol >= minimum_rvol

    # ==========================================================
    # ADX FILTER
    # ==========================================================

    def _adx_filter(
        self,
        adx: float,
        minimum_adx: float,
    ) -> bool:

        return adx >= minimum_adx

    # ==========================================================
    # VWAP FILTER
    # ==========================================================

    def _vwap_filter(
        self,
        close: float,
        vwap: float,
    ) -> bool:

        return close >= vwap

    # ==========================================================
    # EMA200 FILTER
    # ==========================================================

    def _ema200_filter(
        self,
        close: float,
        ema200: float,
    ) -> bool:

        return close >= ema200

    # ==========================================================
    # GAP FILTER
    # ==========================================================

    def _gap_filter(
        self,
        previous_close: float,
        today_open: float,
        maximum_gap: float = 3.0,
    ) -> bool:
        """
        Reject gap > ±3%
        """

        if previous_close <= 0:
            return False

        gap = (

            (today_open - previous_close)

            / previous_close

        ) * 100

        return abs(gap) <= maximum_gap

    # ==========================================================
    # ORB FILTER
    # ==========================================================

    def _orb_filter(
        self,
        orb_high: float,
        orb_low: float,
        price: float,
        maximum_width: float = 3.0,
    ) -> bool:
        """
        Reject very wide ORB.
        """

        if price <= 0:
            return False

        width = (

            (orb_high - orb_low)

            / price

        ) * 100

        return width <= maximum_width

    # ==========================================================
    # F&O FILTER
    # ==========================================================

    def _fo_filter(
        self,
        is_fo_stock: bool,
    ) -> bool:

        return is_fo_stock

    # ==========================================================
    # DELIVERY FILTER
    # ==========================================================

    def _delivery_filter(
        self,
        delivery_percent: float,
        minimum_delivery: float = 35.0,
    ) -> bool:

        return delivery_percent >= minimum_delivery

    # ==========================================================
    # COMPLETE FILTER PIPELINE
    # ==========================================================

    def passes_filters(
        self,
        signal: Signal,
        filters: Dict[str, Any],
    ) -> bool:
        """
        Apply all institutional filters.
        """

        checks = [

            self._price_filter(
                getattr(signal, "price", 0),
                filters["minimum_price"],
            ),

            self._market_cap_filter(
                getattr(signal, "market_cap", 0),
                filters["minimum_market_cap"],
            ),

            self._volume_filter(
                getattr(signal, "volume", 0),
                filters["minimum_volume"],
            ),

            self._relative_volume_filter(
                getattr(signal, "relative_volume", 0),
                filters["minimum_rvol"],
            ),

            self._adx_filter(
                getattr(signal, "adx", 0),
                filters["adx"],
            ),

            self._delivery_filter(
                getattr(
                    signal,
                    "delivery_percentage",
                    0,
                ),
            ),

            self._vwap_filter(
                getattr(signal, "price", 0),
                getattr(signal, "vwap", 0),
            ),

            self._ema200_filter(
                getattr(signal, "price", 0),
                getattr(signal, "ema200", 0),
            ),

            self._gap_filter(
                getattr(
                    signal,
                    "previous_close",
                    0,
                ),
                getattr(
                    signal,
                    "today_open",
                    0,
                ),
            ),

            self._orb_filter(
                getattr(
                    signal,
                    "orb_high",
                    0,
                ),
                getattr(
                    signal,
                    "orb_low",
                    0,
                ),
                getattr(
                    signal,
                    "price",
                    0,
                ),
            ),

            self._fo_filter(
                getattr(
                    signal,
                    "is_fo_stock",
                    False,
                ),
            ),

        ]

        return all(checks)

    # ==========================================================
    # FILTER OPPORTUNITIES
    # ==========================================================

    def filter_opportunities(
        self,
        mode: ScanMode,
    ) -> List[Opportunity]:
        """
        Return only opportunities that pass
        institutional quality filters.
        """

        filters = self.default_filters(mode)

        filtered = []

        for opportunity in self.opportunities:

            if opportunity.signal is None:
                continue

            if self.passes_filters(
                opportunity.signal,
                filters,
            ):
                filtered.append(opportunity)

        self.opportunities = filtered

        self._sort_opportunities()

        return self.opportunities
        # ==========================================================
    # PATTERN SCORE
    # ==========================================================

    def pattern_quality_score(
        self,
        pattern: PatternResult,
    ) -> float:
        """
        Returns pattern quality score (0-100).
        """

        score = float(
            getattr(
                pattern,
                "score",
                0,
            )
        )

        confidence = float(
            getattr(
                pattern,
                "confidence",
                0,
            )
        )

        return (
            score * 0.60
            +
            confidence * 0.40
        )

    # ==========================================================
    # BREAKOUT VALIDATION
    # ==========================================================

    def breakout_confirmed(
        self,
        pattern: PatternResult,
    ) -> bool:

        return bool(

            getattr(
                pattern,
                "breakout_confirmed",
                False,
            )

        )

    # ==========================================================
    # VOLUME CONFIRMATION
    # ==========================================================

    def breakout_volume_confirmed(
        self,
        signal: Signal,
    ) -> bool:

        return (

            getattr(
                signal,
                "relative_volume",
                0,
            )

            >= 1.5

        )

    # ==========================================================
    # MULTI TIMEFRAME
    # ==========================================================

    def multi_timeframe_confirmation(
        self,
        signal: Signal,
    ) -> bool:

        return bool(

            getattr(

                signal,

                "multi_timeframe_confirmation",

                False,

            )

        )

    # ==========================================================
    # TREND ALIGNMENT
    # ==========================================================

    def trend_alignment(
        self,
        signal: Signal,
    ) -> bool:

        return bool(

            getattr(

                signal,

                "trend_confirmation",

                False,

            )

        )

    # ==========================================================
    # VCP
    # ==========================================================

    def valid_vcp(
        self,
        pattern: PatternResult,
    ) -> bool:

        return (

            getattr(
                pattern,
                "pattern_type",
                None,
            ).name

            ==

            "VCP"

        )

    # ==========================================================
    # FALLING WEDGE
    # ==========================================================

    def valid_falling_wedge(
        self,
        pattern: PatternResult,
    ) -> bool:

        return (

            getattr(
                pattern,
                "pattern_type",
                None,
            ).name

            ==

            "FALLING_WEDGE"

        )

    # ==========================================================
    # BULL FLAG
    # ==========================================================

    def valid_bull_flag(
        self,
        pattern: PatternResult,
    ) -> bool:

        return (

            getattr(
                pattern,
                "pattern_type",
                None,
            ).name

            ==

            "BULL_FLAG"

        )

    # ==========================================================
    # CUP & HANDLE
    # ==========================================================

    def valid_cup_handle(
        self,
        pattern: PatternResult,
    ) -> bool:

        return (

            getattr(
                pattern,
                "pattern_type",
                None,
            ).name

            ==

            "CUP_HANDLE"

        )

    # ==========================================================
    # ACCEPTED PATTERNS
    # ==========================================================

    def acceptable_pattern(
        self,
        pattern: PatternResult,
    ) -> bool:

        return any(

            [

                self.valid_vcp(
                    pattern
                ),

                self.valid_falling_wedge(
                    pattern
                ),

                self.valid_bull_flag(
                    pattern
                ),

                self.valid_cup_handle(
                    pattern
                ),

            ]

        )

    # ==========================================================
    # COMPLETE PATTERN VALIDATION
    # ==========================================================

    def validate_pattern(
        self,
        pattern: PatternResult,
        signal: Signal,
    ) -> bool:
        """
        Institutional-quality validation.
        """

        if not self.acceptable_pattern(
            pattern
        ):
            return False

        if not self.breakout_confirmed(
            pattern
        ):
            return False

        if not self.breakout_volume_confirmed(
            signal
        ):
            return False

        if not self.multi_timeframe_confirmation(
            signal
        ):
            return False

        if not self.trend_alignment(
            signal
        ):
            return False

        if self.pattern_quality_score(
            pattern
        ) < 75:
            return False

        return True

    # ==========================================================
    # FILTER PATTERNS
    # ==========================================================

    def filter_patterns(
        self,
    ) -> List[Opportunity]:
        """
        Keep only institutional-quality patterns.
        """

        qualified = []

        for opportunity in self.opportunities:

            if (
                opportunity.pattern is None
                or
                opportunity.signal is None
            ):
                continue

            if self.validate_pattern(

                opportunity.pattern,

                opportunity.signal,

            ):

                qualified.append(
                    opportunity
                )

        self.opportunities = qualified

        self._sort_opportunities()

        return self.opportunities
        # ==========================================================
    # DEFAULT PATTERNS
    # ==========================================================

    def allowed_patterns(self) -> set:
        """
        Institutional patterns enabled by default.
        """

        return {

            "VCP",

            "FALLING_WEDGE",

            "BULL_FLAG",

            "CUP_HANDLE",

            "ASCENDING_TRIANGLE",

            "FLAT_BASE",

            "DOUBLE_BOTTOM",

            "ROUNDING_BOTTOM",

        }

    # ==========================================================
    # PATTERN ENABLED
    # ==========================================================

    def is_pattern_enabled(
        self,
        pattern: PatternResult,
        enabled_patterns: Optional[set] = None,
    ) -> bool:

        if enabled_patterns is None:
            enabled_patterns = self.allowed_patterns()

        name = getattr(
            getattr(pattern, "pattern_type", None),
            "name",
            "",
        )

        return name in enabled_patterns

    # ==========================================================
    # PATTERN BONUS
    # ==========================================================

    def pattern_bonus(
        self,
        pattern: PatternResult,
    ) -> float:
        """
        Institutional preference.
        """

        name = getattr(
            getattr(pattern, "pattern_type", None),
            "name",
            "",
        )

        bonuses = {

            "VCP": 5,

            "CUP_HANDLE": 5,

            "FLAT_BASE": 4,

            "ASCENDING_TRIANGLE": 4,

            "BULL_FLAG": 4,

            "DOUBLE_BOTTOM": 3,

            "ROUNDING_BOTTOM": 3,

            "FALLING_WEDGE": 3,

        }

        return bonuses.get(name, 0)

    # ==========================================================
    # INSTITUTIONAL BONUS
    # ==========================================================

    def institutional_bonus(
        self,
        signal: Signal,
    ) -> float:
        """
        Extra score for institutional activity.
        """

        score = 0.0

        if getattr(
            signal,
            "institutional_buying",
            False,
        ):
            score += 2

        if getattr(
            signal,
            "block_trade",
            False,
        ):
            score += 2

        if getattr(
            signal,
            "fii_positive",
            False,
        ):
            score += 1

        return score

    # ==========================================================
    # FINAL OPPORTUNITY SCORE
    # ==========================================================

    def opportunity_score(
        self,
        opportunity: Opportunity,
    ) -> float:
        """
        Final score shown on dashboard.
        """

        ranking = opportunity.ranking

        if ranking is None:
            return 0.0

        score = ranking.final_score

        score += self.pattern_bonus(
            opportunity.pattern
        )

        score += self.institutional_bonus(
            opportunity.signal
        )

        return min(score, 100.0)

    # ==========================================================
    # RESCORE
    # ==========================================================

    def rescore_opportunities(
        self,
    ) -> None:
        """
        Apply final institutional scoring.
        """

        for opportunity in self.opportunities:

            opportunity.score = self.opportunity_score(
                opportunity
            )

    # ==========================================================
    # REMOVE DUPLICATES
    # ==========================================================

    def remove_duplicates(
        self,
    ) -> None:
        """
        Keep highest-scoring entry for each symbol.
        """

        unique: Dict[
            str,
            Opportunity,
        ] = {}

        for opportunity in self.opportunities:

            symbol = opportunity.symbol

            if symbol not in unique:

                unique[symbol] = opportunity

                continue

            if (
                opportunity.score
                >
                unique[symbol].score
            ):
                unique[symbol] = opportunity

        self.opportunities = list(
            unique.values()
        )

    # ==========================================================
    # FINAL SELECTION
    # ==========================================================

    def final_selection(
        self,
        maximum_results: int = 5,
    ) -> List[Opportunity]:
        """
        Institutional shortlist.
        """

        self.remove_duplicates()

        self.rescore_opportunities()

        self._sort_opportunities()

        return self.opportunities[
            :maximum_results
        ]

    # ==========================================================
    # MARKET QUALITY FILTER
    # ==========================================================

    def market_quality_filter(
        self,
    ) -> bool:
        """
        Skip scan during weak market.
        """

        dashboard = self.market.market_dashboard()

        strength = float(

            dashboard.get(

                "market_strength",

                0,

            )

        )

        return strength >= 50

    # ==========================================================
    # PRE-SCAN CHECK
    # ==========================================================

    def ready_to_scan(
        self,
    ) -> bool:
        """
        Complete readiness check.
        """

        if self.cancel_requested:
            return False

        if not self.watchlist:
            return False

        if not self.market_quality_filter():
            return False

        return True
        # ==========================================================
    # DASHBOARD TABLE
    # ==========================================================

    def dashboard_table(
        self,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Main dashboard table.
        """

        self._sort_opportunities()

        table = []

        for opportunity in self.opportunities[:limit]:

            ranking = opportunity.ranking

            table.append(

                {

                    "Rank": (
                        ranking.rank
                        if ranking
                        else "-"
                    ),

                    "Symbol": opportunity.symbol,

                    "Score": round(
                        opportunity.score,
                        2,
                    ),

                    "Pattern": getattr(
                        getattr(
                            opportunity.pattern,
                            "pattern_type",
                            None,
                        ),
                        "value",
                        "-",
                    ),

                    "Grade": (
                        ranking.entry_grade.value
                        if ranking
                        else "-"
                    ),

                    "Institutional": (
                        ranking.institutional_rating.value
                        if ranking
                        else "-"
                    ),

                    "Confidence": round(
                        opportunity.confidence,
                        1,
                    ),

                    "Recommendation":
                        opportunity.recommendation,

                }

            )

        return table

    # ==========================================================
    # TOP WIDGET
    # ==========================================================

    def top_widget(
        self,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Top opportunity cards.
        """

        self._sort_opportunities()

        cards = []

        for item in self.opportunities[:limit]:

            cards.append(

                {

                    "symbol": item.symbol,

                    "score": round(
                        item.score,
                        1,
                    ),

                    "pattern": getattr(

                        getattr(
                            item.pattern,
                            "pattern_type",
                            None,
                        ),

                        "value",

                        "",

                    ),

                    "recommendation":
                        item.recommendation,

                }

            )

        return cards

    # ==========================================================
    # BUY / SELL SUMMARY
    # ==========================================================

    def recommendation_summary(
        self,
    ) -> Dict[str, int]:
        """
        Count recommendations.
        """

        summary = {

            "Strong Buy": 0,

            "Buy": 0,

            "Watchlist": 0,

            "Speculative": 0,

            "Avoid": 0,

        }

        for opportunity in self.opportunities:

            recommendation = (
                opportunity.recommendation
            )

            if recommendation in summary:
                summary[recommendation] += 1

        return summary

    # ==========================================================
    # PATTERN SUMMARY
    # ==========================================================

    def pattern_summary(
        self,
    ) -> Dict[str, int]:
        """
        Pattern distribution.
        """

        summary: Dict[
            str,
            int,
        ] = {}

        for opportunity in self.opportunities:

            name = getattr(

                getattr(
                    opportunity.pattern,
                    "pattern_type",
                    None,
                ),

                "value",

                "Unknown",

            )

            summary[name] = (
                summary.get(name, 0)
                + 1
            )

        return dict(

            sorted(

                summary.items(),

                key=lambda x: x[1],

                reverse=True,

            )

        )

    # ==========================================================
    # SECTOR SUMMARY
    # ==========================================================

    def sector_summary(
        self,
    ) -> Dict[str, int]:
        """
        Opportunities by sector.
        """

        sectors: Dict[
            str,
            int,
        ] = {}

        for opportunity in self.opportunities:

            sector = opportunity.metadata.get(
                "sector",
                "Unknown",
            )

            sectors[sector] = (

                sectors.get(
                    sector,
                    0,
                )

                + 1

            )

        return dict(

            sorted(

                sectors.items(),

                key=lambda x: x[1],

                reverse=True,

            )

        )

    # ==========================================================
    # HEATMAP
    # ==========================================================

    def heatmap_data(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Data for heatmap widget.
        """

        return [

            {

                "symbol": opportunity.symbol,

                "score": round(
                    opportunity.score,
                    2,
                ),

                "confidence": round(
                    opportunity.confidence,
                    1,
                ),

            }

            for opportunity

            in self.opportunities

        ]

    # ==========================================================
    # DASHBOARD SNAPSHOT
    # ==========================================================

    def dashboard_snapshot(
        self,
    ) -> Dict[str, Any]:
        """
        Complete dashboard payload.
        """

        return {

            "generated": datetime.now().isoformat(),

            "status": self.status.value,

            "summary": self.summary,

            "top5": self.top_widget(5),

            "top10": self.dashboard_table(10),

            "recommendations":
                self.recommendation_summary(),

            "patterns":
                self.pattern_summary(),

            "sectors":
                self.sector_summary(),

            "heatmap":
                self.heatmap_data(),

        }

    # ==========================================================
    # LIVE REFRESH
    # ==========================================================

    def refresh_dashboard(
        self,
    ) -> Dict[str, Any]:
        """
        Refresh dashboard data.
        """

        self._sort_opportunities()

        return self.dashboard_snapshot()
        # ==========================================================
    # EXPORT JSON
    # ==========================================================

    def export_json(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Export all opportunities as JSON-ready objects.
        """

        export = []

        for opportunity in self.opportunities:

            ranking = opportunity.ranking

            export.append({

                "symbol": opportunity.symbol,

                "timeframe": opportunity.timeframe,

                "mode": opportunity.mode.value,

                "score": round(
                    opportunity.score,
                    2,
                ),

                "confidence": round(
                    opportunity.confidence,
                    2,
                ),

                "recommendation":
                    opportunity.recommendation,

                "pattern": getattr(

                    getattr(
                        opportunity.pattern,
                        "pattern_type",
                        None,
                    ),

                    "value",

                    "",

                ),

                "rank": (
                    ranking.rank
                    if ranking
                    else None
                ),

                "grade": (
                    ranking.entry_grade.value
                    if ranking
                    else ""
                ),

                "institutional": (
                    ranking.institutional_rating.value
                    if ranking
                    else ""
                ),

                "metadata":
                    opportunity.metadata,

            })

        return export

    # ==========================================================
    # EXPORT CSV
    # ==========================================================

    def export_csv(
        self,
    ) -> List[List[Any]]:
        """
        CSV rows.
        """

        rows = [[

            "Rank",

            "Symbol",

            "Timeframe",

            "Score",

            "Confidence",

            "Pattern",

            "Grade",

            "Institutional",

            "Recommendation",

        ]]

        for opportunity in self.opportunities:

            ranking = opportunity.ranking

            rows.append([

                ranking.rank
                if ranking
                else "",

                opportunity.symbol,

                opportunity.timeframe,

                round(
                    opportunity.score,
                    2,
                ),

                round(
                    opportunity.confidence,
                    2,
                ),

                getattr(

                    getattr(
                        opportunity.pattern,
                        "pattern_type",
                        None,
                    ),

                    "value",

                    "",

                ),

                ranking.entry_grade.value
                if ranking
                else "",

                ranking.institutional_rating.value
                if ranking
                else "",

                opportunity.recommendation,

            ])

        return rows

    # ==========================================================
    # FIND SYMBOL
    # ==========================================================

    def find_symbol(
        self,
        symbol: str,
    ) -> Optional[Opportunity]:
        """
        Find opportunity by symbol.
        """

        symbol = symbol.upper()

        for opportunity in self.opportunities:

            if opportunity.symbol.upper() == symbol:
                return opportunity

        return None

    # ==========================================================
    # SEARCH
    # ==========================================================

    def search(
        self,
        text: str,
    ) -> List[Opportunity]:
        """
        Search opportunities.
        """

        text = text.upper()

        return [

            opportunity

            for opportunity

            in self.opportunities

            if text in opportunity.symbol.upper()

        ]

    # ==========================================================
    # FILTER BY GRADE
    # ==========================================================

    def filter_by_grade(
        self,
        grade: str,
    ) -> List[Opportunity]:
        """
        Filter by entry grade.
        """

        grade = grade.upper()

        return [

            opportunity

            for opportunity

            in self.opportunities

            if (

                opportunity.ranking

                and

                opportunity.ranking.entry_grade.value.upper()

                == grade

            )

        ]

    # ==========================================================
    # FILTER BY PATTERN
    # ==========================================================

    def filter_by_pattern(
        self,
        pattern_name: str,
    ) -> List[Opportunity]:
        """
        Filter by chart pattern.
        """

        pattern_name = pattern_name.upper()

        return [

            opportunity

            for opportunity

            in self.opportunities

            if (

                getattr(

                    getattr(
                        opportunity.pattern,
                        "pattern_type",
                        None,
                    ),

                    "name",

                    "",

                )

                ==

                pattern_name

            )

        ]

    # ==========================================================
    # ENGINE DIAGNOSTICS
    # ==========================================================

    def diagnostics(
        self,
    ) -> Dict[str, Any]:
        """
        Runtime diagnostics.
        """

        return {

            "engine": "ScreenerEngine",

            "version": self.VERSION,

            "status": self.status.value,

            "watchlist_size":
                len(self.watchlist),

            "opportunities":
                len(self.opportunities),

            "cancel_requested":
                self.cancel_requested,

            "summary": {

                "total":
                    self.summary.total_symbols,

                "scanned":
                    self.summary.scanned,

                "failed":
                    self.summary.failed,

                "elapsed":
                    self.summary.elapsed_seconds,

            },

        }

    # ==========================================================
    # PERFORMANCE METRICS
    # ==========================================================

    def performance_metrics(
        self,
    ) -> Dict[str, float]:
        """
        Scan performance statistics.
        """

        total = max(
            self.summary.scanned,
            1,
        )

        success = (
            total
            - self.summary.failed
        )

        success_rate = (
            success / total
        ) * 100

        opportunities = (
            len(self.opportunities)
            / total
        ) * 100

        return {

            "success_rate":
                round(success_rate, 2),

            "opportunity_rate":
                round(opportunities, 2),

            "average_scan_time":

                round(

                    self.summary.elapsed_seconds
                    / total,

                    3,

                ),

        }
    