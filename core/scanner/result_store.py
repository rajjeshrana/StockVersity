"""
=========================================================
StockVersity Scanner Pro
Scanner Result Store
Version : 2.0
=========================================================

Central in-memory storage for scanner results.

Responsibilities
----------------
• Store latest scanner opportunities
• Replace duplicate results
• Retrieve results by scanner
• Retrieve results by symbol
• Retrieve results by timeframe
• Retrieve top-ranked opportunities
• Remove stale results
• Maintain bounded result history
• Provide dashboard-ready data
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime
from datetime import timedelta

from threading import RLock

from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Mapping
from typing import Optional


# =========================================================
# STORED SCANNER RESULT
# =========================================================

@dataclass(slots=True)
class StoredScannerResult:
    """
    Normalized scanner opportunity stored by ResultStore.
    """

    symbol: str

    scanner_name: str

    timeframe: str = ""

    signal: str = ""

    pattern: str = ""

    score: float = 0.0

    rank: int = 0

    entry: float = 0.0

    stop_loss: float = 0.0

    target: float = 0.0

    risk_reward: float = 0.0

    sector: str = ""

    created_at: datetime = field(
        default_factory=datetime.now
    )

    updated_at: datetime = field(
        default_factory=datetime.now
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    # =====================================================
    # KEY
    # =====================================================

    @property
    def key(
        self,
    ) -> str:
        """
        Unique result identity.

        Same scanner + symbol + timeframe + signal replaces
        the previous opportunity instead of duplicating it.
        """

        return "::".join(
            [
                self.scanner_name.strip().upper(),
                self.symbol.strip().upper(),
                self.timeframe.strip().upper(),
                self.signal.strip().upper(),
            ]
        )

    # =====================================================
    # AGE
    # =====================================================

    @property
    def age_seconds(
        self,
    ) -> float:

        return max(
            0.0,
            (
                datetime.now()
                - self.updated_at
            ).total_seconds(),
        )

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "symbol":
                self.symbol,

            "scanner_name":
                self.scanner_name,

            "timeframe":
                self.timeframe,

            "signal":
                self.signal,

            "pattern":
                self.pattern,

            "score":
                self.score,

            "rank":
                self.rank,

            "entry":
                self.entry,

            "stop_loss":
                self.stop_loss,

            "target":
                self.target,

            "risk_reward":
                self.risk_reward,

            "sector":
                self.sector,

            "created_at":
                self.created_at.isoformat(),

            "updated_at":
                self.updated_at.isoformat(),

            "age_seconds":
                round(
                    self.age_seconds,
                    2,
                ),

            "metadata":
                dict(
                    self.metadata
                ),
        }


# =========================================================
# RESULT STORE
# =========================================================

class ScannerResultStore:
    """
    Thread-safe in-memory scanner result repository.
    """

    def __init__(
        self,
        *,
        max_results: int = 5000,
        stale_minutes: int = 120,
    ) -> None:

        self.max_results = max(
            1,
            int(max_results),
        )

        self.stale_minutes = max(
            0,
            int(stale_minutes),
        )

        self._results: Dict[
            str,
            StoredScannerResult
        ] = {}

        self._lock = RLock()

    # =====================================================
    # NORMALIZE TEXT
    # =====================================================

    @staticmethod
    def _text(
        value: Any,
    ) -> str:

        if value is None:
            return ""

        return str(
            value
        ).strip()

    # =====================================================
    # NUMBER
    # =====================================================

    @staticmethod
    def _float(
        value: Any,
        default: float = 0.0,
    ) -> float:

        try:

            return float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):

            return default

    # =====================================================
    # INTEGER
    # =====================================================

    @staticmethod
    def _int(
        value: Any,
        default: int = 0,
    ) -> int:

        try:

            return int(
                value
            )

        except (
            TypeError,
            ValueError,
        ):

            return default

    # =====================================================
    # GET FIELD
    # =====================================================

    @staticmethod
    def _first(
        data: Mapping[str, Any],
        *keys: str,
        default: Any = None,
    ) -> Any:

        for key in keys:

            if key in data:

                value = data[
                    key
                ]

                if value is not None:

                    return value

        return default

    # =====================================================
    # NORMALIZE RESULT
    # =====================================================

    def normalize(
        self,
        result: Any,
        *,
        scanner_name: Optional[str] = None,
    ) -> StoredScannerResult:
        """
        Convert common scanner-result objects/dictionaries
        into StoredScannerResult.
        """

        if isinstance(
            result,
            StoredScannerResult,
        ):

            if scanner_name:

                result.scanner_name = (
                    scanner_name
                )

            return result

        # ---------------------------------------------
        # OBJECT -> DICTIONARY
        # ---------------------------------------------

        if isinstance(
            result,
            Mapping,
        ):

            data = dict(
                result
            )

        elif hasattr(
            result,
            "to_dict",
        ):

            converted = (
                result.to_dict()
            )

            if not isinstance(
                converted,
                Mapping,
            ):

                raise TypeError(
                    "result.to_dict() must return a mapping."
                )

            data = dict(
                converted
            )

        else:

            # Support dataclass-like scanner objects.

            data = {}

            fields = (
                "symbol",
                "scanner_name",
                "scanner",
                "timeframe",
                "signal",
                "signal_type",
                "pattern",
                "score",
                "rank",
                "entry",
                "entry_price",
                "stop_loss",
                "sl",
                "target",
                "target1",
                "risk_reward",
                "rr",
                "sector",
                "metadata",
            )

            for name in fields:

                if hasattr(
                    result,
                    name,
                ):

                    data[
                        name
                    ] = getattr(
                        result,
                        name
                    )

        # ---------------------------------------------
        # SYMBOL
        # ---------------------------------------------

        symbol = self._text(
            self._first(
                data,
                "symbol",
                "trading_symbol",
                "tradingsymbol",
            )
        )

        if not symbol:

            raise ValueError(
                "Scanner result has no symbol."
            )

        # ---------------------------------------------
        # SCANNER NAME
        # ---------------------------------------------

        resolved_scanner = (
            scanner_name
            or self._first(
                data,
                "scanner_name",
                "scanner",
                default="UnknownScanner",
            )
        )

        resolved_scanner = self._text(
            resolved_scanner
        )

        if not resolved_scanner:

            resolved_scanner = (
                "UnknownScanner"
            )

        # ---------------------------------------------
        # SIGNAL
        # ---------------------------------------------

        signal_value = self._first(
            data,
            "signal",
            "signal_type",
            "direction",
        )

        if hasattr(
            signal_value,
            "value",
        ):

            signal_value = (
                signal_value.value
            )

        # ---------------------------------------------
        # METADATA
        # ---------------------------------------------

        metadata = self._first(
            data,
            "metadata",
            default={},
        )

        if not isinstance(
            metadata,
            Mapping,
        ):

            metadata = {}

        # ---------------------------------------------
        # CREATE
        # ---------------------------------------------

        return StoredScannerResult(

            symbol=symbol,

            scanner_name=resolved_scanner,

            timeframe=self._text(
                self._first(
                    data,
                    "timeframe",
                    "tf",
                )
            ),

            signal=self._text(
                signal_value
            ),

            pattern=self._text(
                self._first(
                    data,
                    "pattern",
                    "setup",
                    "strategy",
                )
            ),

            score=self._float(
                self._first(
                    data,
                    "score",
                    "final_score",
                    "confidence",
                )
            ),

            rank=self._int(
                self._first(
                    data,
                    "rank",
                    default=0,
                )
            ),

            entry=self._float(
                self._first(
                    data,
                    "entry",
                    "entry_price",
                )
            ),

            stop_loss=self._float(
                self._first(
                    data,
                    "stop_loss",
                    "sl",
                )
            ),

            target=self._float(
                self._first(
                    data,
                    "target",
                    "target1",
                )
            ),

            risk_reward=self._float(
                self._first(
                    data,
                    "risk_reward",
                    "rr",
                )
            ),

            sector=self._text(
                self._first(
                    data,
                    "sector",
                )
            ),

            metadata=dict(
                metadata
            ),
        )

    # =====================================================
    # ADD
    # =====================================================

    def add(
        self,
        result: Any,
        *,
        scanner_name: Optional[str] = None,
    ) -> StoredScannerResult:
        """
        Add or replace one scanner result.
        """

        normalized = (
            self.normalize(
                result,
                scanner_name=scanner_name,
            )
        )

        now = datetime.now()

        with self._lock:

            existing = (
                self._results.get(
                    normalized.key
                )
            )

            if existing is not None:

                normalized.created_at = (
                    existing.created_at
                )

            normalized.updated_at = now

            self._results[
                normalized.key
            ] = normalized

            self._enforce_limit()

        return normalized

    # =====================================================
    # ADD MANY
    # =====================================================

    def add_many(
        self,
        results: Iterable[Any],
        *,
        scanner_name: Optional[str] = None,
    ) -> List[StoredScannerResult]:

        stored: List[
            StoredScannerResult
        ] = []

        for result in results:

            try:

                stored.append(
                    self.add(
                        result,
                        scanner_name=scanner_name,
                    )
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

        return stored

    # =====================================================
    # ENFORCE LIMIT
    # =====================================================

    def _enforce_limit(
        self,
    ) -> None:

        while (
            len(self._results)
            > self.max_results
        ):

            oldest_key = min(

                self._results,

                key=lambda key:
                    self._results[
                        key
                    ].updated_at,
            )

            del self._results[
                oldest_key
            ]

    # =====================================================
    # GET BY KEY
    # =====================================================

    def get(
        self,
        key: str,
    ) -> Optional[
        StoredScannerResult
    ]:

        with self._lock:

            return self._results.get(
                str(key)
            )

    # =====================================================
    # ALL
    # =====================================================

    def all(
        self,
    ) -> List[
        StoredScannerResult
    ]:

        with self._lock:

            return list(
                self._results.values()
            )

    # =====================================================
    # BY SCANNER
    # =====================================================

    def by_scanner(
        self,
        scanner_name: str,
    ) -> List[
        StoredScannerResult
    ]:

        name = (
            self._text(
                scanner_name
            ).upper()
        )

        with self._lock:

            return [

                result

                for result
                in self._results.values()

                if (
                    result.scanner_name
                    .upper()
                    == name
                )
            ]

    # =====================================================
    # BY SYMBOL
    # =====================================================

    def by_symbol(
        self,
        symbol: str,
    ) -> List[
        StoredScannerResult
    ]:

        symbol_key = (
            self._text(
                symbol
            ).upper()
        )

        with self._lock:

            return [

                result

                for result
                in self._results.values()

                if (
                    result.symbol
                    .upper()
                    == symbol_key
                )
            ]

    # =====================================================
    # BY TIMEFRAME
    # =====================================================

    def by_timeframe(
        self,
        timeframe: str,
    ) -> List[
        StoredScannerResult
    ]:

        timeframe_key = (
            self._text(
                timeframe
            ).upper()
        )

        with self._lock:

            return [

                result

                for result
                in self._results.values()

                if (
                    result.timeframe
                    .upper()
                    == timeframe_key
                )
            ]

    # =====================================================
    # BY SIGNAL
    # =====================================================

    def by_signal(
        self,
        signal: str,
    ) -> List[
        StoredScannerResult
    ]:

        signal_key = (
            self._text(
                signal
            ).upper()
        )

        with self._lock:

            return [

                result

                for result
                in self._results.values()

                if (
                    result.signal
                    .upper()
                    == signal_key
                )
            ]

    # =====================================================
    # TOP RESULTS
    # =====================================================

    def top(
        self,
        limit: int = 10,
        *,
        scanner_name: Optional[str] = None,
        signal: Optional[str] = None,
        timeframe: Optional[str] = None,
    ) -> List[
        StoredScannerResult
    ]:
        """
        Return highest-score opportunities.
        """

        limit = max(
            0,
            int(limit),
        )

        if limit == 0:

            return []

        results = self.all()

        if scanner_name:

            scanner_key = (
                self._text(
                    scanner_name
                ).upper()
            )

            results = [

                result

                for result in results

                if (
                    result.scanner_name
                    .upper()
                    == scanner_key
                )
            ]

        if signal:

            signal_key = (
                self._text(
                    signal
                ).upper()
            )

            results = [

                result

                for result in results

                if (
                    result.signal
                    .upper()
                    == signal_key
                )
            ]

        if timeframe:

            timeframe_key = (
                self._text(
                    timeframe
                ).upper()
            )

            results = [

                result

                for result in results

                if (
                    result.timeframe
                    .upper()
                    == timeframe_key
                )
            ]

        return sorted(

            results,

            key=lambda result: (
                result.score,
                result.risk_reward,
                result.updated_at,
            ),

            reverse=True,

        )[:limit]

    # =====================================================
    # RANK
    # =====================================================

    def rank(
        self,
    ) -> List[
        StoredScannerResult
    ]:
        """
        Rank all stored opportunities by score.
        """

        ranked = self.top(
            limit=len(self),
        )

        for index, result in enumerate(
            ranked,
            start=1,
        ):

            result.rank = index

        return ranked

    # =====================================================
    # REMOVE
    # =====================================================

    def remove(
        self,
        key: str,
    ) -> bool:

        with self._lock:

            if key not in self._results:

                return False

            del self._results[
                key
            ]

            return True

    # =====================================================
    # REMOVE SCANNER
    # =====================================================

    def remove_scanner(
        self,
        scanner_name: str,
    ) -> int:

        name = (
            self._text(
                scanner_name
            ).upper()
        )

        removed = 0

        with self._lock:

            keys = [

                key

                for key, result
                in self._results.items()

                if (
                    result.scanner_name
                    .upper()
                    == name
                )
            ]

            for key in keys:

                del self._results[
                    key
                ]

                removed += 1

        return removed

    # =====================================================
    # REMOVE SYMBOL
    # =====================================================

    def remove_symbol(
        self,
        symbol: str,
    ) -> int:

        symbol_key = (
            self._text(
                symbol
            ).upper()
        )

        removed = 0

        with self._lock:

            keys = [

                key

                for key, result
                in self._results.items()

                if (
                    result.symbol
                    .upper()
                    == symbol_key
                )
            ]

            for key in keys:

                del self._results[
                    key
                ]

                removed += 1

        return removed

    # =====================================================
    # CLEAN STALE
    # =====================================================

    def cleanup(
        self,
        *,
        stale_minutes: Optional[int] = None,
    ) -> int:
        """
        Remove old scanner opportunities.

        stale_minutes = 0 disables cleanup.
        """

        minutes = (
            self.stale_minutes
            if stale_minutes is None
            else max(
                0,
                int(stale_minutes),
            )
        )

        if minutes <= 0:

            return 0

        cutoff = (
            datetime.now()
            - timedelta(
                minutes=minutes
            )
        )

        removed = 0

        with self._lock:

            keys = [

                key

                for key, result
                in self._results.items()

                if (
                    result.updated_at
                    < cutoff
                )
            ]

            for key in keys:

                del self._results[
                    key
                ]

                removed += 1

        return removed

    # =====================================================
    # DASHBOARD DATA
    # =====================================================

    def dashboard_rows(
        self,
        limit: int = 50,
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Return compact rows suitable for the opportunities
        table in the StockVersity dashboard.
        """

        rows: List[
            Dict[str, Any]
        ] = []

        ranked = self.top(
            limit=limit
        )

        for index, result in enumerate(
            ranked,
            start=1,
        ):

            rows.append(
                {
                    "rank":
                        index,

                    "stock":
                        result.symbol,

                    "score":
                        round(
                            result.score,
                            2,
                        ),

                    "signal":
                        result.signal,

                    "pattern":
                        result.pattern,

                    "rr":
                        round(
                            result.risk_reward,
                            2,
                        ),

                    "timeframe":
                        result.timeframe,

                    "sector":
                        result.sector,

                    "entry":
                        result.entry,

                    "stop_loss":
                        result.stop_loss,

                    "target":
                        result.target,

                    "scanner":
                        result.scanner_name,

                    "updated_at":
                        result.updated_at,
                }
            )

        return rows

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> Dict[str, Any]:

        results = self.all()

        scanners = {
            result.scanner_name
            for result in results
        }

        symbols = {
            result.symbol
            for result in results
        }

        buy_count = sum(
            1
            for result in results
            if result.signal.upper()
            in (
                "BUY",
                "LONG",
            )
        )

        sell_count = sum(
            1
            for result in results
            if result.signal.upper()
            in (
                "SELL",
                "SHORT",
            )
        )

        return {

            "results":
                len(results),

            "scanners":
                len(scanners),

            "symbols":
                len(symbols),

            "buy_signals":
                buy_count,

            "sell_signals":
                sell_count,

            "max_results":
                self.max_results,

            "stale_minutes":
                self.stale_minutes,
        }

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(
        self,
    ) -> None:

        with self._lock:

            self._results.clear()

    # =====================================================
    # LENGTH
    # =====================================================

    def __len__(
        self,
    ) -> int:

        with self._lock:

            return len(
                self._results
            )


# =========================================================
# GLOBAL RESULT STORE
# =========================================================

scanner_result_store = ScannerResultStore(
    max_results=5000,
    stale_minutes=120,
)


# =========================================================
# CONVENIENCE FUNCTIONS
# =========================================================

def store_scanner_result(
    result: Any,
    *,
    scanner_name: Optional[str] = None,
) -> StoredScannerResult:

    return scanner_result_store.add(
        result,
        scanner_name=scanner_name,
    )


def store_scanner_results(
    results: Iterable[Any],
    *,
    scanner_name: Optional[str] = None,
) -> List[StoredScannerResult]:

    return scanner_result_store.add_many(
        results,
        scanner_name=scanner_name,
    )


def get_top_scanner_results(
    limit: int = 10,
) -> List[StoredScannerResult]:

    return scanner_result_store.top(
        limit=limit
    )


def get_dashboard_results(
    limit: int = 50,
) -> List[Dict[str, Any]]:

    return scanner_result_store.dashboard_rows(
        limit=limit
    )


def clear_scanner_results(
) -> None:

    scanner_result_store.clear()


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "StoredScannerResult",

    "ScannerResultStore",

    "scanner_result_store",

    "store_scanner_result",

    "store_scanner_results",

    "get_top_scanner_results",

    "get_dashboard_results",

    "clear_scanner_results",
]


# ==========================
# END OF FILE
# ==========================