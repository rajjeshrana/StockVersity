"""
StockVersity Scanner Pro
Live NIFTY 500 Stock Universe

Consumes parsed Tick objects from the existing UpstoxProvider callback
and maintains live state for the mapped NIFTY 500 universe.

IMPORTANT
---------
This module does NOT create another WebSocket connection.
It is designed to attach to the existing UpstoxProvider:

    universe = LiveStockUniverse()
    universe.load()
    provider.add_tick_callback(universe.on_tick)
    provider.subscribe_many(universe.instrument_keys(), mode="ltpc")

Provides:
- live stock state
- advance / decline / unchanged breadth
- top gainers
- top losers
- industry strength
- heatmap-ready rows

Run standalone diagnostic:
    python -m core.market_data.live_stock_universe
"""

from __future__ import annotations

import threading
import time
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

from core.market_data.models import Tick
from core.market_data.nifty500_universe import (
    Nifty500Stock,
    Nifty500Universe,
)


@dataclass
class LiveStockState:
    symbol: str
    instrument_key: str
    company_name: str
    industry: str
    isin_code: str = ""

    ltp: float = 0.0
    previous_close: float = 0.0
    change: float = 0.0
    change_percent: float = 0.0
    volume: int = 0
    timestamp: int = 0

    tick_count: int = 0
    last_update_monotonic: float = 0.0

    @property
    def has_price(self) -> bool:
        return self.ltp > 0.0

    @property
    def has_previous_close(self) -> bool:
        return self.previous_close > 0.0

    @property
    def direction(self) -> str:
        if not self.has_price or not self.has_previous_close:
            return "unknown"

        epsilon = 1e-9

        if self.change > epsilon:
            return "advance"

        if self.change < -epsilon:
            return "decline"

        return "unchanged"

    def to_dict(self) -> Dict:
        return asdict(self)


class LiveStockUniverse:
    """
    Thread-safe live state engine for NIFTY 500 equities.
    """

    def __init__(
        self,
        universe: Optional[Nifty500Universe] = None,
    ) -> None:

        self.universe = universe or Nifty500Universe()

        self._lock = threading.RLock()

        self._states: Dict[str, LiveStockState] = {}
        self._symbol_to_key: Dict[str, str] = {}

        self._loaded = False
        self._accepted_ticks = 0
        self._ignored_ticks = 0

    # =====================================================
    # LOAD UNIVERSE
    # =====================================================

    def load(
        self,
        force_download: bool = False,
        force_instrument_download: bool = False,
    ) -> "LiveStockUniverse":

        self.universe.load(
            force_download=force_download,
            force_instrument_download=force_instrument_download,
        )

        states: Dict[str, LiveStockState] = {}
        symbol_to_key: Dict[str, str] = {}

        for stock in self.universe.stocks:

            state = LiveStockState(
                symbol=stock.symbol,
                instrument_key=stock.instrument_key,
                company_name=stock.company_name,
                industry=stock.industry,
                isin_code=stock.isin_code,
            )

            states[stock.instrument_key] = state
            symbol_to_key[stock.symbol.upper()] = stock.instrument_key

        with self._lock:
            self._states = states
            self._symbol_to_key = symbol_to_key
            self._accepted_ticks = 0
            self._ignored_ticks = 0
            self._loaded = True

        return self

    @property
    def loaded(self) -> bool:
        return self._loaded

    # =====================================================
    # SUBSCRIPTION HELPERS
    # =====================================================

    def instrument_keys(self) -> List[str]:
        with self._lock:
            return list(self._states.keys())

    def symbols(self) -> List[str]:
        with self._lock:
            return [
                state.symbol
                for state in self._states.values()
            ]

    def subscription_count(self) -> int:
        with self._lock:
            return len(self._states)

    # =====================================================
    # TICK INGESTION
    # =====================================================

    @staticmethod
    def _safe_float(value) -> float:
        try:
            return float(value or 0.0)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _safe_int(value) -> int:
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0

    def on_tick(self, tick: Tick) -> None:
        """
        Callback compatible with UpstoxProvider.add_tick_callback().
        """

        if tick is None:
            return

        instrument_key = str(
            getattr(tick, "instrument_key", "") or ""
        ).strip()

        if not instrument_key:
            return

        with self._lock:

            state = self._states.get(instrument_key)

            if state is None:
                self._ignored_ticks += 1
                return

            ltp = self._safe_float(
                getattr(tick, "ltp", 0.0)
            )

            previous_close = self._safe_float(
                getattr(tick, "previous_close", 0.0)
            )

            volume = self._safe_int(
                getattr(tick, "volume", 0)
            )

            timestamp = self._safe_int(
                getattr(tick, "timestamp", 0)
            )

            # Never replace a valid live price with an empty one.
            if ltp > 0.0:
                state.ltp = ltp

            # cp -> previous_close is already populated by
            # StockVersity's MarketDataParser for LTPC feeds.
            if previous_close > 0.0:
                state.previous_close = previous_close

            if volume >= 0:
                state.volume = volume

            if timestamp > 0:
                state.timestamp = timestamp

            if (
                state.ltp > 0.0
                and state.previous_close > 0.0
            ):
                state.change = (
                    state.ltp
                    - state.previous_close
                )

                state.change_percent = (
                    state.change
                    / state.previous_close
                ) * 100.0
            else:
                state.change = 0.0
                state.change_percent = 0.0

            state.tick_count += 1
            state.last_update_monotonic = time.monotonic()

            self._accepted_ticks += 1

    # =====================================================
    # LOOKUPS
    # =====================================================

    def get_by_instrument_key(
        self,
        instrument_key: str,
    ) -> Optional[LiveStockState]:

        with self._lock:
            return self._states.get(
                str(instrument_key or "").strip()
            )

    def get_by_symbol(
        self,
        symbol: str,
    ) -> Optional[LiveStockState]:

        normalized = str(symbol or "").strip().upper()

        with self._lock:

            key = self._symbol_to_key.get(
                normalized
            )

            if key is None:
                return None

            return self._states.get(key)

    def snapshot(self) -> List[Dict]:
        with self._lock:
            return [
                state.to_dict()
                for state in self._states.values()
            ]

    def live_snapshot(self) -> List[Dict]:
        with self._lock:
            return [
                state.to_dict()
                for state in self._states.values()
                if state.has_price
            ]

    # =====================================================
    # MARKET BREADTH
    # =====================================================

    def breadth(self) -> Dict[str, int | float]:

        advance = 0
        decline = 0
        unchanged = 0
        unknown = 0

        with self._lock:

            states = list(
                self._states.values()
            )

            for state in states:

                direction = state.direction

                if direction == "advance":
                    advance += 1

                elif direction == "decline":
                    decline += 1

                elif direction == "unchanged":
                    unchanged += 1

                else:
                    unknown += 1

        valid = (
            advance
            + decline
            + unchanged
        )

        breadth_ratio = (
            advance / decline
            if decline > 0
            else float(advance)
        )

        advance_percent = (
            (advance / valid) * 100.0
            if valid
            else 0.0
        )

        decline_percent = (
            (decline / valid) * 100.0
            if valid
            else 0.0
        )

        return {
            "advance": advance,
            "decline": decline,
            "unchanged": unchanged,
            "unknown": unknown,
            "valid": valid,
            "total": len(states),
            "breadth_ratio": breadth_ratio,
            "advance_percent": advance_percent,
            "decline_percent": decline_percent,
        }

    # =====================================================
    # GAINERS / LOSERS
    # =====================================================

    def _priced_states(self) -> List[LiveStockState]:

        with self._lock:
            return [
                state
                for state in self._states.values()
                if (
                    state.has_price
                    and state.has_previous_close
                )
            ]

    def top_gainers(
        self,
        limit: int = 10,
    ) -> List[Dict]:

        states = self._priced_states()

        states.sort(
            key=lambda state: state.change_percent,
            reverse=True,
        )

        return [
            state.to_dict()
            for state in states[:max(0, int(limit))]
        ]

    def top_losers(
        self,
        limit: int = 10,
    ) -> List[Dict]:

        states = self._priced_states()

        states.sort(
            key=lambda state: state.change_percent
        )

        return [
            state.to_dict()
            for state in states[:max(0, int(limit))]
        ]

    # =====================================================
    # INDUSTRY STRENGTH
    # =====================================================

    def industry_strength(self) -> List[Dict]:

        groups: Dict[str, List[LiveStockState]] = {}

        for state in self._priced_states():

            industry = (
                state.industry.strip()
                or "Unknown"
            )

            groups.setdefault(
                industry,
                [],
            ).append(state)

        result: List[Dict] = []

        for industry, states in groups.items():

            changes = [
                state.change_percent
                for state in states
            ]

            average_change = (
                sum(changes) / len(changes)
                if changes
                else 0.0
            )

            advances = sum(
                1
                for state in states
                if state.change > 0
            )

            declines = sum(
                1
                for state in states
                if state.change < 0
            )

            unchanged = (
                len(states)
                - advances
                - declines
            )

            result.append(
                {
                    "industry": industry,
                    "average_change_percent":
                        average_change,
                    "advance": advances,
                    "decline": declines,
                    "unchanged": unchanged,
                    "live_stocks": len(states),
                }
            )

        result.sort(
            key=lambda row:
                row["average_change_percent"],
            reverse=True,
        )

        return result

    # =====================================================
    # HEATMAP DATA
    # =====================================================

    def heatmap(
        self,
        limit: Optional[int] = None,
    ) -> List[Dict]:

        rows = self._priced_states()

        rows.sort(
            key=lambda state:
                abs(state.change_percent),
            reverse=True,
        )

        if limit is not None:
            rows = rows[:max(0, int(limit))]

        return [
            {
                "symbol": state.symbol,
                "company_name": state.company_name,
                "industry": state.industry,
                "instrument_key": state.instrument_key,
                "ltp": state.ltp,
                "previous_close": state.previous_close,
                "change": state.change,
                "change_percent": state.change_percent,
                "volume": state.volume,
                "timestamp": state.timestamp,
            }
            for state in rows
        ]

    # =====================================================
    # HEALTH / STATISTICS
    # =====================================================

    def statistics(self) -> Dict[str, int | float | bool]:

        with self._lock:

            total = len(self._states)

            live = sum(
                1
                for state in self._states.values()
                if state.has_price
            )

            complete = sum(
                1
                for state in self._states.values()
                if (
                    state.has_price
                    and state.has_previous_close
                )
            )

            accepted = self._accepted_ticks
            ignored = self._ignored_ticks

        return {
            "loaded": self._loaded,
            "total_stocks": total,
            "live_stocks": live,
            "complete_stocks": complete,
            "accepted_ticks": accepted,
            "ignored_ticks": ignored,
            "coverage_percent": (
                (complete / total) * 100.0
                if total
                else 0.0
            ),
        }


def _diagnostic() -> int:

    print("========================================")
    print("StockVersity Live NIFTY 500 Universe")
    print("========================================")

    try:
        engine = LiveStockUniverse().load()
    except Exception as exc:
        print("Universe load: FAILED")
        print("ERROR:", exc)
        return 1

    print("Universe load: OK")
    print(
        "Subscription instruments:",
        engine.subscription_count(),
    )

    reliance = engine.get_by_symbol(
        "RELIANCE"
    )

    if reliance is None:
        print("RELIANCE state: FAILED")
        return 1

    print(
        "RELIANCE:",
        reliance.instrument_key,
    )

    # Synthetic tick verifies calculation logic only.
    # It does NOT connect to Upstox.
    synthetic = Tick(
        instrument_key=reliance.instrument_key,
        symbol="RELIANCE",
        ltp=1515.0,
        previous_close=1500.0,
        timestamp=1,
    )

    engine.on_tick(synthetic)

    reliance = engine.get_by_symbol(
        "RELIANCE"
    )

    print(
        "Synthetic LTP:",
        f"{reliance.ltp:.2f}",
    )

    print(
        "Synthetic previous close:",
        f"{reliance.previous_close:.2f}",
    )

    print(
        "Synthetic change %:",
        f"{reliance.change_percent:.2f}%",
    )

    breadth = engine.breadth()

    print(
        "Synthetic breadth:",
        f"A={breadth['advance']} "
        f"D={breadth['decline']} "
        f"U={breadth['unchanged']} "
        f"Unknown={breadth['unknown']}",
    )

    stats = engine.statistics()

    print(
        "Accepted ticks:",
        stats["accepted_ticks"],
    )

    print("Live stock engine: OK")

    return 0


if __name__ == "__main__":
    raise SystemExit(_diagnostic())
