"""
=========================================================
StockVersity Scanner Pro
Base Scanner
Version : 2.1
=========================================================

File:
    core/scanner/base_scanner.py

Purpose:
    Common foundation for every StockVersity scanner.

Execution Contract
------------------

ScannerEngine
      ↓
BaseScanner.run()
      ↓
before_scan()
      ↓
scan()
      ↓
candidate signals
      ↓
validation
      ↓
on_signal_found()
      ↓
post processing
      ↓
ranking / filtering
      ↓
after_scan()
      ↓
final signals

IMPORTANT
---------
Child scanner scan() methods should RETURN Signal objects.

They should NOT normally append directly to self.signals.
=========================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
)

from core.scanner.signal import (
    MarketTrend,
    PatternType,
    Signal,
    SignalType,
)


# =========================================================
# TYPE ALIASES
# =========================================================

SignalFilter = Callable[[Signal], bool]


# =========================================================
# BASE SCANNER
# =========================================================

class BaseScanner(ABC):
    """
    Base class for every StockVersity scanner.
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        name: str,
        version: str = "2.1",
        timeframe: str = "5m",
    ) -> None:

        name = str(name).strip()

        if not name:
            raise ValueError(
                "Scanner name cannot be empty."
            )

        self.name = name

        self.version = str(
            version
        ).strip() or "2.1"

        self.timeframe = str(
            timeframe
        ).strip() or "5m"

        self.created_at = datetime.now()

        # -------------------------------------------------
        # MARKET CONTEXT
        # -------------------------------------------------

        self.market_trend: MarketTrend = (
            MarketTrend.SIDEWAYS
        )

        self.sector_strength: Dict[
            str,
            float,
        ] = {}

        self.symbols: List[str] = []

        # -------------------------------------------------
        # RESULTS
        # -------------------------------------------------

        self.signals: List[Signal] = []

        # -------------------------------------------------
        # FILTER SETTINGS
        # -------------------------------------------------

        self.max_signals = 50

        self.minimum_score = 60.0

        self.minimum_confidence = 60.0

        self.minimum_rr = 2.0

        self.filters_enabled = True

        # -------------------------------------------------
        # SCORE WEIGHTS
        # -------------------------------------------------

        self.score_weights: Dict[
            str,
            float,
        ] = {
            "score": 0.50,
            "confidence": 0.30,
            "risk_reward": 0.20,
        }

        # -------------------------------------------------
        # RUNTIME
        # -------------------------------------------------

        self.debug = False

        self.execution_time = 0.0

        self._scan_started: Optional[
            datetime
        ] = None

        self._scan_finished: Optional[
            datetime
        ] = None

        # -------------------------------------------------
        # CACHE / INDEX
        # -------------------------------------------------

        self._cache: Dict[
            str,
            Any,
        ] = {}

        self._signal_index: Dict[
            str,
            Signal,
        ] = {}

    # =====================================================
    # ABSTRACT SCAN
    # =====================================================

    @abstractmethod
    def scan(
        self,
        market_data: Dict[str, Any],
    ) -> List[Signal]:
        """
        Implement scanner-specific detection logic.

        IMPORTANT:
        Return candidate Signal objects.

        Do not normally modify self.signals directly.
        """

        raise NotImplementedError

    # =====================================================
    # HOOKS
    # =====================================================

    def before_scan(
        self,
        market_data: Dict[str, Any],
    ) -> None:
        """
        Hook executed immediately before scan().
        """

        return None

    def after_scan(
        self,
        signals: List[Signal],
    ) -> None:
        """
        Hook executed after final processing.
        """

        return None

    def on_signal_found(
        self,
        signal: Signal,
    ) -> None:
        """
        Hook called whenever a valid candidate is accepted.
        """

        return None

    # =====================================================
    # RESET
    # =====================================================

    def reset(
        self,
    ) -> None:

        self.signals.clear()

        self._signal_index.clear()

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(
        self,
    ) -> None:

        self.symbols.clear()

        self.signals.clear()

        self._signal_index.clear()

        self._cache.clear()

    # =====================================================
    # SIGNAL VALIDATION
    # =====================================================

    def validate_signal(
        self,
        signal: Signal,
    ) -> bool:
        """
        Validate a scanner candidate.
        """

        if not isinstance(
            signal,
            Signal,
        ):
            return False

        if not signal.instrument_key:
            return False

        if not signal.symbol:
            return False

        if signal.entry <= 0:
            return False

        if signal.stop_loss <= 0:
            return False

        if signal.target1 <= 0:
            return False

        # BUY structure
        if signal.is_buy:

            if signal.stop_loss >= signal.entry:
                return False

            if signal.target1 <= signal.entry:
                return False

        # SELL structure
        elif signal.is_sell:

            if signal.stop_loss <= signal.entry:
                return False

            if signal.target1 >= signal.entry:
                return False

        if signal.risk_reward < self.minimum_rr:
            return False

        if signal.score < self.minimum_score:
            return False

        if (
            signal.confidence
            < self.minimum_confidence
        ):
            return False

        return True

    # =====================================================
    # ADD SIGNAL
    # =====================================================

    def add_signal(
        self,
        signal: Signal,
    ) -> None:

        if not isinstance(
            signal,
            Signal,
        ):

            raise TypeError(
                "signal must be a Signal instance."
            )

        self.signals.append(
            signal
        )

        self._signal_index.clear()

    # =====================================================
    # SAFE ADD
    # =====================================================

    def add_if_valid(
        self,
        signal: Signal,
    ) -> bool:

        if not self.validate_signal(
            signal
        ):
            return False

        self.add_signal(
            signal
        )

        self.on_signal_found(
            signal
        )

        return True

    # =====================================================
    # ADD MANY
    # =====================================================

    def add_signals(
        self,
        signals: List[Signal],
    ) -> int:

        added = 0

        for signal in signals:

            if self.add_if_valid(
                signal
            ):

                added += 1

        return added

    # =====================================================
    # REMOVE SIGNAL
    # =====================================================

    def remove_signal(
        self,
        symbol: str,
    ) -> None:

        symbol = str(
            symbol
        ).strip().upper()

        self.signals = [
            signal
            for signal in self.signals
            if signal.symbol.upper()
            != symbol
        ]

        self._signal_index.clear()

    # =====================================================
    # GET SIGNAL
    # =====================================================

    def get_signal(
        self,
        symbol: str,
    ) -> Optional[Signal]:

        return self.find(
            symbol
        )

    # =====================================================
    # HAS SIGNAL
    # =====================================================

    def has_signal(
        self,
        symbol: str,
    ) -> bool:

        return (
            self.find(symbol)
            is not None
        )

    # =====================================================
    # FIND
    # =====================================================

    def find(
        self,
        symbol: str,
    ) -> Optional[Signal]:

        symbol = str(
            symbol
        ).strip().upper()

        for signal in self.signals:

            if (
                signal.symbol.upper()
                == symbol
            ):

                return signal

        return None

    # =====================================================
    # DUPLICATE REMOVAL
    # =====================================================

    def remove_duplicates(
        self,
    ) -> None:
        """
        Keep highest-quality signal for each symbol.

        Quality order:
            score
            confidence
            risk_reward
        """

        unique: Dict[
            str,
            Signal,
        ] = {}

        for signal in self.signals:

            symbol = (
                signal.symbol.upper()
            )

            existing = unique.get(
                symbol
            )

            if existing is None:

                unique[
                    symbol
                ] = signal

                continue

            candidate_quality = (
                signal.score,
                signal.confidence,
                signal.risk_reward,
            )

            existing_quality = (
                existing.score,
                existing.confidence,
                existing.risk_reward,
            )

            if (
                candidate_quality
                > existing_quality
            ):

                unique[
                    symbol
                ] = signal

        self.signals = list(
            unique.values()
        )

        self._signal_index.clear()

    # =====================================================
    # FILTER SCORE
    # =====================================================

    def filter_by_score(
        self,
        minimum_score: Optional[
            float
        ] = None,
    ) -> None:

        minimum = (
            self.minimum_score
            if minimum_score is None
            else float(minimum_score)
        )

        self.signals = [
            signal
            for signal in self.signals
            if signal.score >= minimum
        ]

        self._signal_index.clear()

    # =====================================================
    # FILTER CONFIDENCE
    # =====================================================

    def filter_by_confidence(
        self,
        minimum_confidence: Optional[
            float
        ] = None,
    ) -> None:

        minimum = (
            self.minimum_confidence
            if minimum_confidence is None
            else float(
                minimum_confidence
            )
        )

        self.signals = [
            signal
            for signal in self.signals
            if (
                signal.confidence
                >= minimum
            )
        ]

        self._signal_index.clear()

    # =====================================================
    # FILTER RISK REWARD
    # =====================================================

    def filter_by_rr(
        self,
        minimum_rr: Optional[
            float
        ] = None,
    ) -> None:

        minimum = (
            self.minimum_rr
            if minimum_rr is None
            else float(minimum_rr)
        )

        self.signals = [
            signal
            for signal in self.signals
            if (
                signal.risk_reward
                >= minimum
            )
        ]

        self._signal_index.clear()

    # =====================================================
    # FILTER SIGNAL TYPE
    # =====================================================

    def filter_by_signal_type(
        self,
        signal_type: SignalType,
    ) -> None:

        self.signals = [
            signal
            for signal in self.signals
            if (
                signal.signal_type
                == signal_type
            )
        ]

        self._signal_index.clear()

    # =====================================================
    # FILTER PATTERN
    # =====================================================

    def filter_by_pattern(
        self,
        pattern: PatternType,
    ) -> None:

        self.signals = [
            signal
            for signal in self.signals
            if signal.pattern == pattern
        ]

        self._signal_index.clear()

    # =====================================================
    # FILTER PRICE
    # =====================================================

    def filter_by_price(
        self,
        minimum: Optional[
            float
        ] = None,
        maximum: Optional[
            float
        ] = None,
    ) -> None:

        filtered: List[
            Signal
        ] = []

        for signal in self.signals:

            price = signal.last_price

            if (
                minimum is not None
                and price < minimum
            ):
                continue

            if (
                maximum is not None
                and price > maximum
            ):
                continue

            filtered.append(
                signal
            )

        self.signals = filtered

        self._signal_index.clear()

    # =====================================================
    # FILTER VOLUME
    # =====================================================

    def filter_by_volume(
        self,
        minimum_volume: int = 0,
        minimum_volume_ratio: float = 1.0,
    ) -> None:

        self.signals = [
            signal
            for signal in self.signals
            if (
                signal.volume
                >= minimum_volume
                and signal.volume_ratio
                >= minimum_volume_ratio
            )
        ]

        self._signal_index.clear()

    # =====================================================
    # FILTER MARKET CAP
    # =====================================================

    def filter_by_market_cap(
        self,
        minimum_market_cap: float,
    ) -> None:

        filtered: List[
            Signal
        ] = []

        for signal in self.signals:

            try:

                market_cap = float(
                    signal.metadata.get(
                        "market_cap",
                        0.0,
                    )
                )

            except (
                TypeError,
                ValueError,
            ):

                market_cap = 0.0

            if (
                market_cap
                >= minimum_market_cap
            ):

                filtered.append(
                    signal
                )

        self.signals = filtered

        self._signal_index.clear()

    # =====================================================
    # FILTER SECTOR
    # =====================================================

    def filter_by_sector(
        self,
        sectors: List[str],
    ) -> None:

        allowed = {
            str(sector)
            .strip()
            .upper()
            for sector in sectors
        }

        self.signals = [
            signal
            for signal in self.signals
            if (
                signal.sector
                and signal.sector.upper()
                in allowed
            )
        ]

        self._signal_index.clear()

    # =====================================================
    # FILTER MARKET TREND
    # =====================================================

    def filter_by_market_trend(
        self,
        trend: str,
    ) -> None:

        trend = str(
            trend
        ).strip().upper()

        self.signals = [
            signal
            for signal in self.signals
            if (
                signal.market_trend.value
                .upper()
                == trend
            )
        ]

        self._signal_index.clear()

    # =====================================================
    # CUSTOM FILTER
    # =====================================================

    def filter(
        self,
        callback: SignalFilter,
    ) -> None:

        self.signals = [
            signal
            for signal in self.signals
            if callback(signal)
        ]

        self._signal_index.clear()

    # =====================================================
    # MULTIPLE FILTERS
    # =====================================================

    def apply_filters(
        self,
        *callbacks: SignalFilter,
    ) -> None:

        for callback in callbacks:

            self.filter(
                callback
            )

    # =====================================================
    # SORT SCORE
    # =====================================================

    def sort_by_score(
        self,
        reverse: bool = True,
    ) -> None:

        self.signals.sort(
            key=lambda signal: (
                signal.score,
                signal.confidence,
                signal.risk_reward,
            ),
            reverse=reverse,
        )

    # =====================================================
    # SORT CONFIDENCE
    # =====================================================

    def sort_by_confidence(
        self,
        reverse: bool = True,
    ) -> None:

        self.signals.sort(
            key=lambda signal: (
                signal.confidence,
                signal.score,
            ),
            reverse=reverse,
        )

    # =====================================================
    # SORT RR
    # =====================================================

    def sort_by_rr(
        self,
        reverse: bool = True,
    ) -> None:

        self.signals.sort(
            key=lambda signal: (
                signal.risk_reward,
                signal.score,
            ),
            reverse=reverse,
        )

    # =====================================================
    # GENERIC SORT
    # =====================================================

    def sort(
        self,
        key: Callable[
            [Signal],
            Any,
        ],
        reverse: bool = True,
    ) -> None:

        self.signals.sort(
            key=key,
            reverse=reverse,
        )

    # =====================================================
    # SCORE WEIGHTS
    # =====================================================

    def set_score_weights(
        self,
        *,
        score: float = 0.50,
        confidence: float = 0.30,
        risk_reward: float = 0.20,
    ) -> None:

        total = (
            score
            + confidence
            + risk_reward
        )

        if (
            abs(
                total - 1.0
            )
            > 0.001
        ):

            raise ValueError(
                "Score weights must total 1.0"
            )

        self.score_weights = {
            "score": float(score),
            "confidence": float(
                confidence
            ),
            "risk_reward": float(
                risk_reward
            ),
        }

    # =====================================================
    # RANKING
    # =====================================================

    def rank_signals(
        self,
    ) -> None:
        """
        Calculate weighted opportunity score.

        Original scanner score is retained in metadata.
        """

        score_weight = (
            self.score_weights[
                "score"
            ]
        )

        confidence_weight = (
            self.score_weights[
                "confidence"
            ]
        )

        rr_weight = (
            self.score_weights[
                "risk_reward"
            ]
        )

        for signal in self.signals:

            if (
                "raw_score"
                not in signal.metadata
            ):

                signal.metadata[
                    "raw_score"
                ] = signal.score

            raw_score = float(
                signal.metadata.get(
                    "raw_score",
                    signal.score,
                )
            )

            rr_component = (
                min(
                    max(
                        signal.risk_reward,
                        0.0,
                    ),
                    5.0,
                )
                / 5.0
                * 100.0
            )

            final_score = (
                raw_score
                * score_weight
                + signal.confidence
                * confidence_weight
                + rr_component
                * rr_weight
            )

            signal.score = round(
                max(
                    0.0,
                    min(
                        final_score,
                        100.0,
                    ),
                ),
                2,
            )

        self.sort_by_score()

    # =====================================================
    # GRADE
    # =====================================================

    def grade(
        self,
        signal: Signal,
    ) -> str:

        score = signal.score

        confidence = (
            signal.confidence
        )

        rr = signal.risk_reward

        if (
            score >= 90
            and confidence >= 90
            and rr >= 3.0
        ):
            return "A+"

        if (
            score >= 80
            and confidence >= 80
            and rr >= 2.5
        ):
            return "A"

        if (
            score >= 70
            and confidence >= 70
            and rr >= 2.0
        ):
            return "B"

        if score >= 60:
            return "C"

        return "D"

    # =====================================================
    # ASSIGN RANKS
    # =====================================================

    def assign_ranks(
        self,
    ) -> None:

        self.sort_by_score()

        for index, signal in enumerate(
            self.signals,
            start=1,
        ):

            signal.metadata[
                "rank"
            ] = index

            signal.metadata[
                "grade"
            ] = self.grade(
                signal
            )

    # =====================================================
    # LIMIT RESULTS
    # =====================================================

    def limit_results(
        self,
        limit: Optional[
            int
        ] = None,
    ) -> None:

        maximum = (
            self.max_signals
            if limit is None
            else max(
                0,
                int(limit),
            )
        )

        self.signals = (
            self.signals[
                :maximum
            ]
        )

        self._signal_index.clear()

    # =====================================================
    # PROCESS PIPELINE
    # =====================================================

    def process_signals(
        self,
    ) -> List[Signal]:

        self.remove_duplicates()

        if self.filters_enabled:

            self.filter_by_score()

            self.filter_by_rr()

            self.filter_by_confidence()

        self.rank_signals()

        self.limit_results()

        self.assign_ranks()

        self.build_index()

        return self.signals

    # =====================================================
    # RUN
    # =====================================================

    def run(
        self,
        market_data: Dict[str, Any],
    ) -> List[Signal]:
        """
        Standard scanner execution pipeline.
        """

        if market_data is None:

            raise ValueError(
                "market_data cannot be None"
            )

        self.reset()

        self.start_timer()

        try:

            self.before_scan(
                market_data
            )

            candidates = self.scan(
                market_data
            )

            if candidates is None:

                candidates = []

            for signal in candidates:

                self.add_if_valid(
                    signal
                )

            self.process_signals()

            self.after_scan(
                self.signals
            )

        except Exception as exc:

            self.log(
                "Scanner Error:",
                repr(exc),
            )

            raise

        finally:

            self.execution_time = (
                self.stop_timer()
            )

        return list(
            self.signals
        )

    # =====================================================
    # BATCH SCAN
    # =====================================================

    def scan_batch(
        self,
        market_data_list: List[
            Dict[str, Any]
        ],
    ) -> List[Signal]:

        self.reset()

        self.start_timer()

        try:

            for market_data in (
                market_data_list
            ):

                self.before_scan(
                    market_data
                )

                candidates = self.scan(
                    market_data
                )

                if not candidates:
                    continue

                for signal in candidates:

                    self.add_if_valid(
                        signal
                    )

            self.process_signals()

            self.after_scan(
                self.signals
            )

        finally:

            self.execution_time = (
                self.stop_timer()
            )

        return list(
            self.signals
        )

    # =====================================================
    # REPLACE SIGNALS
    # =====================================================

    def replace_signals(
        self,
        signals: List[Signal],
    ) -> None:

        self.reset()

        self.add_signals(
            signals
        )

        self.process_signals()

    # =====================================================
    # MERGE
    # =====================================================

    def merge(
        self,
        scanner: "BaseScanner",
    ) -> None:

        self.add_signals(
            scanner.to_list()
        )

        self.process_signals()

    # =====================================================
    # COMPARATOR
    # =====================================================

    def compare(
        self,
        left: Signal,
        right: Signal,
    ) -> Signal:

        left_quality = (
            left.score,
            left.confidence,
            left.risk_reward,
        )

        right_quality = (
            right.score,
            right.confidence,
            right.risk_reward,
        )

        if (
            left_quality
            >= right_quality
        ):

            return left

        return right

    # =====================================================
    # TOP
    # =====================================================

    def top(
        self,
        count: int = 10,
    ) -> List[Signal]:

        count = max(
            0,
            int(count),
        )

        self.sort_by_score()

        return list(
            self.signals[
                :count
            ]
        )

    # =====================================================
    # BEST
    # =====================================================

    def best(
        self,
    ) -> Optional[Signal]:

        if not self.signals:
            return None

        self.sort_by_score()

        return self.signals[
            0
        ]

    # =====================================================
    # TOP BY GRADE
    # =====================================================

    def top_grade(
        self,
        grade: str,
    ) -> List[Signal]:

        grade = str(
            grade
        ).strip().upper()

        return [
            signal
            for signal in self.signals
            if str(
                signal.metadata.get(
                    "grade",
                    "",
                )
            ).upper()
            == grade
        ]

    # =====================================================
    # GROUP BY PATTERN
    # =====================================================

    def group_by_pattern(
        self,
    ) -> Dict[
        PatternType,
        List[Signal],
    ]:

        groups: Dict[
            PatternType,
            List[Signal],
        ] = {}

        for signal in self.signals:

            groups.setdefault(
                signal.pattern,
                [],
            ).append(
                signal
            )

        return groups

    # =====================================================
    # GROUP BY TYPE
    # =====================================================

    def group_by_type(
        self,
    ) -> Dict[
        SignalType,
        List[Signal],
    ]:

        groups: Dict[
            SignalType,
            List[Signal],
        ] = {}

        for signal in self.signals:

            groups.setdefault(
                signal.signal_type,
                [],
            ).append(
                signal
            )

        return groups

    # =====================================================
    # INDEX
    # =====================================================

    def build_index(
        self,
    ) -> None:

        self._signal_index = {
            signal.symbol.upper():
                signal
            for signal in self.signals
        }

    def get_indexed(
        self,
        symbol: str,
    ) -> Optional[Signal]:

        if not self._signal_index:

            self.build_index()

        return self._signal_index.get(
            str(
                symbol
            ).strip().upper()
        )

    # =====================================================
    # CACHE
    # =====================================================

    def clear_cache(
        self,
    ) -> None:

        self._cache.clear()

    def cache_set(
        self,
        key: str,
        value: Any,
    ) -> None:

        self._cache[
            key
        ] = value

    def cache_get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self._cache.get(
            key,
            default,
        )

    def cache_exists(
        self,
        key: str,
    ) -> bool:

        return (
            key
            in self._cache
        )

    # =====================================================
    # CONFIGURATION
    # =====================================================

    def configure(
        self,
        **kwargs: Any,
    ) -> "BaseScanner":

        for key, value in (
            kwargs.items()
        ):

            if hasattr(
                self,
                key,
            ):

                setattr(
                    self,
                    key,
                    value,
                )

        return self

    # =====================================================
    # FILTER CONTROL
    # =====================================================

    def enable_filters(
        self,
    ) -> None:

        self.filters_enabled = True

    def disable_filters(
        self,
    ) -> None:

        self.filters_enabled = False

    # =====================================================
    # TIMER
    # =====================================================

    def start_timer(
        self,
    ) -> None:

        self._scan_started = (
            datetime.now()
        )

    def stop_timer(
        self,
    ) -> float:

        self._scan_finished = (
            datetime.now()
        )

        if self._scan_started is None:

            return 0.0

        return (
            self._scan_finished
            - self._scan_started
        ).total_seconds()

    # =====================================================
    # STATISTICS
    # =====================================================

    @property
    def total_signals(
        self,
    ) -> int:

        return len(
            self.signals
        )

    @property
    def buy_signals(
        self,
    ) -> int:

        return sum(
            1
            for signal in self.signals
            if signal.is_buy
        )

    @property
    def sell_signals(
        self,
    ) -> int:

        return sum(
            1
            for signal in self.signals
            if signal.is_sell
        )

    @property
    def watch_signals(
        self,
    ) -> int:

        return sum(
            1
            for signal in self.signals
            if signal.is_watch
        )

    @property
    def average_score(
        self,
    ) -> float:

        if not self.signals:
            return 0.0

        return round(
            sum(
                signal.score
                for signal in self.signals
            )
            / len(self.signals),
            2,
        )

    @property
    def average_confidence(
        self,
    ) -> float:

        if not self.signals:
            return 0.0

        return round(
            sum(
                signal.confidence
                for signal in self.signals
            )
            / len(self.signals),
            2,
        )

    @property
    def average_rr(
        self,
    ) -> float:

        if not self.signals:
            return 0.0

        return round(
            sum(
                signal.risk_reward
                for signal in self.signals
            )
            / len(self.signals),
            2,
        )

    # =====================================================
    # STATISTICS REPORT
    # =====================================================

    def statistics(
        self,
    ) -> Dict[str, Any]:

        return {
            "scanner": self.name,
            "version": self.version,
            "timeframe": self.timeframe,
            "generated": len(
                self.signals
            ),
            "buy": self.buy_signals,
            "sell": self.sell_signals,
            "watch": self.watch_signals,
            "average_score":
                self.average_score,
            "average_confidence":
                self.average_confidence,
            "average_rr":
                self.average_rr,
            "execution_time":
                round(
                    self.execution_time,
                    4,
                ),
            "timestamp":
                datetime.now().isoformat(),
        }

    # =====================================================
    # PERFORMANCE
    # =====================================================

    def performance(
        self,
    ) -> Dict[str, Any]:

        return {
            "scanner": self.name,

            "execution_time": round(
                self.execution_time,
                4,
            ),

            "symbols_loaded": len(
                self.symbols
            ),

            "signals_found": len(
                self.signals
            ),

            "buy_signals":
                self.buy_signals,

            "sell_signals":
                self.sell_signals,

            "watch_signals":
                self.watch_signals,

            "average_score":
                self.average_score,

            "average_confidence":
                self.average_confidence,

            "average_rr":
                self.average_rr,

            "timestamp":
                datetime.now().isoformat(),
        }

    # =====================================================
    # LEADERBOARD
    # =====================================================

    def leaderboard(
        self,
    ) -> List[
        Dict[str, Any]
    ]:

        self.assign_ranks()

        return [
            {
                "rank":
                    signal.metadata.get(
                        "rank",
                        0,
                    ),

                "symbol":
                    signal.symbol,

                "type":
                    signal.signal_type.value,

                "pattern":
                    signal.pattern.value,

                "score":
                    signal.score,

                "confidence":
                    signal.confidence,

                "rr":
                    signal.risk_reward,

                "grade":
                    signal.metadata.get(
                        "grade",
                        "",
                    ),
            }

            for signal in self.signals
        ]

    # =====================================================
    # EXPORT LIST
    # =====================================================

    def to_list(
        self,
    ) -> List[Signal]:

        return list(
            self.signals
        )

    # =====================================================
    # EXPORT DICT
    # =====================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {
            "name": self.name,

            "version": self.version,

            "timeframe":
                self.timeframe,

            "created_at":
                self.created_at.isoformat(),

            "market_trend":
                self.market_trend.value,

            "minimum_score":
                self.minimum_score,

            "minimum_confidence":
                self.minimum_confidence,

            "minimum_rr":
                self.minimum_rr,

            "max_signals":
                self.max_signals,

            "filters_enabled":
                self.filters_enabled,

            "execution_time":
                self.execution_time,

            "total_signals":
                len(self.signals),

            "signals": [
                signal.to_dict()
                for signal in self.signals
            ],
        }

    # =====================================================
    # EXPORT SIGNALS
    # =====================================================

    def export(
        self,
    ) -> List[
        Dict[str, Any]
    ]:

        return [
            signal.to_dict()
            for signal in self.signals
        ]

    # =====================================================
    # AGGREGATE
    # =====================================================

    @staticmethod
    def aggregate(
        *scanners: "BaseScanner",
    ) -> List[Signal]:

        merged: Dict[
            str,
            Signal,
        ] = {}

        for scanner in scanners:

            for signal in (
                scanner.to_list()
            ):

                symbol = (
                    signal.symbol.upper()
                )

                existing = merged.get(
                    symbol
                )

                if existing is None:

                    merged[
                        symbol
                    ] = signal

                    continue

                candidate_quality = (
                    signal.score,
                    signal.confidence,
                    signal.risk_reward,
                )

                existing_quality = (
                    existing.score,
                    existing.confidence,
                    existing.risk_reward,
                )

                if (
                    candidate_quality
                    > existing_quality
                ):

                    merged[
                        symbol
                    ] = signal

        return sorted(
            merged.values(),
            key=lambda signal: (
                signal.score,
                signal.confidence,
                signal.risk_reward,
            ),
            reverse=True,
        )

    # =====================================================
    # DEBUG
    # =====================================================

    def enable_debug(
        self,
    ) -> None:

        self.debug = True

    def disable_debug(
        self,
    ) -> None:

        self.debug = False

    # =====================================================
    # LOG
    # =====================================================

    def log(
        self,
        *message: Any,
    ) -> None:

        if not self.debug:
            return

        print(
            f"[{self.name}]",
            *message,
        )

    # =====================================================
    # MAGIC METHODS
    # =====================================================

    def __len__(
        self,
    ) -> int:

        return len(
            self.signals
        )

    def __iter__(
        self,
    ) -> Iterator[Signal]:

        return iter(
            self.signals
        )

    def __getitem__(
        self,
        index: int,
    ) -> Signal:

        return self.signals[
            index
        ]

    def __contains__(
        self,
        symbol: object,
    ) -> bool:

        if not isinstance(
            symbol,
            str,
        ):

            return False

        symbol = (
            symbol.strip().upper()
        )

        return any(
            signal.symbol.upper()
            == symbol
            for signal in self.signals
        )

    def __bool__(
        self,
    ) -> bool:

        return bool(
            self.signals
        )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __str__(
        self,
    ) -> str:

        return (
            f"{self.name} "
            f"[{self.timeframe}] "
            f"- {len(self.signals)} signals"
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"version='{self.version}', "
            f"timeframe='{self.timeframe}', "
            f"signals={len(self.signals)}, "
            f"minimum_score={self.minimum_score}, "
            f"minimum_rr={self.minimum_rr})"
        )


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [
    "BaseScanner",
    "SignalFilter",
]


# =========================================================
# END OF FILE
# =========================================================