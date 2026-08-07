"""
=========================================================
StockVersity Scanner Pro
Scanner Context
Version : 2.0
=========================================================

Shared runtime context for all scanners.

Responsibilities
----------------
• Store market-wide state
• Store Nifty / Bank Nifty information
• Store India VIX
• Store sector strength
• Store market breadth
• Store scanner timestamps
• Provide sector lookup helpers
• Provide market direction helpers
• Share common context between scanners
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from core.scanner.signal import MarketTrend


# =========================================================
# SECTOR STATE
# =========================================================

@dataclass(slots=True)
class SectorState:
    """
    Current state of one market sector.
    """

    name: str

    change_percent: float = 0.0

    strength: float = 0.0

    relative_strength: float = 0.0

    trend: MarketTrend = MarketTrend.SIDEWAYS

    rank: int = 0

    advancing_stocks: int = 0

    declining_stocks: int = 0

    unchanged_stocks: int = 0

    volume_ratio: float = 0.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    # =====================================================
    # HELPERS
    # =====================================================

    @property
    def bullish(self) -> bool:

        return self.trend in (
            MarketTrend.BULLISH,
            MarketTrend.STRONG_BULLISH,
        )

    @property
    def bearish(self) -> bool:

        return self.trend in (
            MarketTrend.BEARISH,
            MarketTrend.STRONG_BEARISH,
        )

    @property
    def breadth(self) -> float:
        """
        Sector breadth percentage.
        """

        total = (
            self.advancing_stocks
            + self.declining_stocks
            + self.unchanged_stocks
        )

        if total <= 0:
            return 0.0

        return round(
            (
                self.advancing_stocks
                - self.declining_stocks
            )
            / total
            * 100.0,
            2,
        )

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "name":
                self.name,

            "change_percent":
                self.change_percent,

            "strength":
                self.strength,

            "relative_strength":
                self.relative_strength,

            "trend":
                self.trend.value,

            "rank":
                self.rank,

            "advancing_stocks":
                self.advancing_stocks,

            "declining_stocks":
                self.declining_stocks,

            "unchanged_stocks":
                self.unchanged_stocks,

            "breadth":
                self.breadth,

            "volume_ratio":
                self.volume_ratio,

            "metadata":
                dict(self.metadata),
        }


# =========================================================
# MARKET BREADTH
# =========================================================

@dataclass(slots=True)
class MarketBreadth:
    """
    Overall market breadth information.
    """

    advances: int = 0

    declines: int = 0

    unchanged: int = 0

    new_highs: int = 0

    new_lows: int = 0

    above_20_ema: int = 0

    above_50_ema: int = 0

    above_200_ema: int = 0

    total_stocks: int = 0

    # =====================================================
    # ADVANCE DECLINE RATIO
    # =====================================================

    @property
    def advance_decline_ratio(
        self,
    ) -> float:

        if self.declines <= 0:

            if self.advances > 0:
                return float(
                    self.advances
                )

            return 0.0

        return round(
            self.advances
            / self.declines,
            2,
        )

    # =====================================================
    # BREADTH PERCENT
    # =====================================================

    @property
    def breadth_percent(
        self,
    ) -> float:

        total = (
            self.total_stocks
            or (
                self.advances
                + self.declines
                + self.unchanged
            )
        )

        if total <= 0:
            return 0.0

        return round(
            (
                self.advances
                - self.declines
            )
            / total
            * 100.0,
            2,
        )

    # =====================================================
    # BULLISH
    # =====================================================

    @property
    def bullish(
        self,
    ) -> bool:

        return (
            self.advances
            > self.declines
        )

    # =====================================================
    # BEARISH
    # =====================================================

    @property
    def bearish(
        self,
    ) -> bool:

        return (
            self.declines
            > self.advances
        )

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "advances":
                self.advances,

            "declines":
                self.declines,

            "unchanged":
                self.unchanged,

            "new_highs":
                self.new_highs,

            "new_lows":
                self.new_lows,

            "above_20_ema":
                self.above_20_ema,

            "above_50_ema":
                self.above_50_ema,

            "above_200_ema":
                self.above_200_ema,

            "total_stocks":
                self.total_stocks,

            "advance_decline_ratio":
                self.advance_decline_ratio,

            "breadth_percent":
                self.breadth_percent,
        }


# =========================================================
# INDEX STATE
# =========================================================

@dataclass(slots=True)
class IndexState:
    """
    Current state of an index.
    """

    symbol: str

    last_price: float = 0.0

    previous_close: float = 0.0

    change: float = 0.0

    change_percent: float = 0.0

    open_price: float = 0.0

    high_price: float = 0.0

    low_price: float = 0.0

    trend: MarketTrend = MarketTrend.SIDEWAYS

    ema20: float = 0.0

    ema50: float = 0.0

    ema200: float = 0.0

    vwap: float = 0.0

    rsi: float = 0.0

    adx: float = 0.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    # =====================================================
    # DIRECTION
    # =====================================================

    @property
    def bullish(
        self,
    ) -> bool:

        return self.trend in (
            MarketTrend.BULLISH,
            MarketTrend.STRONG_BULLISH,
        )

    @property
    def bearish(
        self,
    ) -> bool:

        return self.trend in (
            MarketTrend.BEARISH,
            MarketTrend.STRONG_BEARISH,
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

            "last_price":
                self.last_price,

            "previous_close":
                self.previous_close,

            "change":
                self.change,

            "change_percent":
                self.change_percent,

            "open_price":
                self.open_price,

            "high_price":
                self.high_price,

            "low_price":
                self.low_price,

            "trend":
                self.trend.value,

            "ema20":
                self.ema20,

            "ema50":
                self.ema50,

            "ema200":
                self.ema200,

            "vwap":
                self.vwap,

            "rsi":
                self.rsi,

            "adx":
                self.adx,

            "metadata":
                dict(self.metadata),
        }


# =========================================================
# SCANNER CONTEXT
# =========================================================

@dataclass(slots=True)
class ScannerContext:
    """
    Shared runtime context supplied to scanners.

    This object contains market-wide information that
    should not be recalculated independently by every
    scanner.
    """

    market_trend: MarketTrend = (
        MarketTrend.SIDEWAYS
    )

    market_strength: float = 0.0

    market_open: bool = False

    trading_date: Optional[str] = None

    timestamp: datetime = field(
        default_factory=datetime.now
    )

    # =====================================================
    # INDEX INFORMATION
    # =====================================================

    nifty: Optional[IndexState] = None

    bank_nifty: Optional[IndexState] = None

    fin_nifty: Optional[IndexState] = None

    midcap_nifty: Optional[IndexState] = None

    # =====================================================
    # VIX
    # =====================================================

    india_vix: float = 0.0

    india_vix_change_percent: float = 0.0

    # =====================================================
    # MARKET BREADTH
    # =====================================================

    breadth: MarketBreadth = field(
        default_factory=MarketBreadth
    )

    # =====================================================
    # SECTORS
    # =====================================================

    sectors: Dict[
        str,
        SectorState
    ] = field(
        default_factory=dict
    )

    # =====================================================
    # EXTRA INFORMATION
    # =====================================================

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    # =====================================================
    # NORMALIZATION
    # =====================================================

    @staticmethod
    def _sector_key(
        name: str,
    ) -> str:

        return (
            str(name)
            .strip()
            .upper()
        )

    # =====================================================
    # SET SECTOR
    # =====================================================

    def set_sector(
        self,
        sector: SectorState,
    ) -> None:

        key = self._sector_key(
            sector.name
        )

        self.sectors[
            key
        ] = sector

    # =====================================================
    # GET SECTOR
    # =====================================================

    def get_sector(
        self,
        name: str,
    ) -> Optional[SectorState]:

        return self.sectors.get(
            self._sector_key(
                name
            )
        )

    # =====================================================
    # SECTOR STRENGTH
    # =====================================================

    def sector_strength(
        self,
        name: str,
    ) -> float:

        sector = self.get_sector(
            name
        )

        if sector is None:
            return 0.0

        return sector.strength

    # =====================================================
    # SECTOR TREND
    # =====================================================

    def sector_trend(
        self,
        name: str,
    ) -> MarketTrend:

        sector = self.get_sector(
            name
        )

        if sector is None:

            return (
                MarketTrend.SIDEWAYS
            )

        return sector.trend

    # =====================================================
    # TOP SECTORS
    # =====================================================

    def top_sectors(
        self,
        count: int = 2,
    ) -> List[SectorState]:
        """
        Return strongest sectors.
        """

        if count <= 0:
            return []

        return sorted(
            self.sectors.values(),
            key=lambda sector: (
                sector.strength,
                sector.change_percent,
            ),
            reverse=True,
        )[:count]

    # =====================================================
    # WEAKEST SECTORS
    # =====================================================

    def weakest_sectors(
        self,
        count: int = 2,
    ) -> List[SectorState]:
        """
        Return weakest sectors.
        """

        if count <= 0:
            return []

        return sorted(
            self.sectors.values(),
            key=lambda sector: (
                sector.strength,
                sector.change_percent,
            ),
        )[:count]

    # =====================================================
    # BULLISH MARKET
    # =====================================================

    @property
    def bullish_market(
        self,
    ) -> bool:

        return self.market_trend in (
            MarketTrend.BULLISH,
            MarketTrend.STRONG_BULLISH,
        )

    # =====================================================
    # BEARISH MARKET
    # =====================================================

    @property
    def bearish_market(
        self,
    ) -> bool:

        return self.market_trend in (
            MarketTrend.BEARISH,
            MarketTrend.STRONG_BEARISH,
        )

    # =====================================================
    # SIDEWAYS MARKET
    # =====================================================

    @property
    def sideways_market(
        self,
    ) -> bool:

        return (
            self.market_trend
            == MarketTrend.SIDEWAYS
        )

    # =====================================================
    # LONG ALLOWED
    # =====================================================

    @property
    def long_allowed(
        self,
    ) -> bool:
        """
        Long trades allowed unless market is strongly
        bearish.
        """

        return (
            self.market_trend
            != MarketTrend.STRONG_BEARISH
        )

    # =====================================================
    # SHORT ALLOWED
    # =====================================================

    @property
    def short_allowed(
        self,
    ) -> bool:
        """
        Short trades allowed unless market is strongly
        bullish.
        """

        return (
            self.market_trend
            != MarketTrend.STRONG_BULLISH
        )

    # =====================================================
    # UPDATE TIMESTAMP
    # =====================================================

    def touch(
        self,
    ) -> None:

        self.timestamp = (
            datetime.now()
        )

    # =====================================================
    # CLEAR SECTORS
    # =====================================================

    def clear_sectors(
        self,
    ) -> None:

        self.sectors.clear()

    # =====================================================
    # RESET
    # =====================================================

    def reset(
        self,
    ) -> None:

        self.market_trend = (
            MarketTrend.SIDEWAYS
        )

        self.market_strength = 0.0

        self.market_open = False

        self.trading_date = None

        self.nifty = None

        self.bank_nifty = None

        self.fin_nifty = None

        self.midcap_nifty = None

        self.india_vix = 0.0

        self.india_vix_change_percent = 0.0

        self.breadth = (
            MarketBreadth()
        )

        self.sectors.clear()

        self.metadata.clear()

        self.touch()

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "market_trend":
                self.market_trend.value,

            "market_strength":
                self.market_strength,

            "market_open":
                self.market_open,

            "trading_date":
                self.trading_date,

            "timestamp":
                self.timestamp.isoformat(),

            "india_vix":
                self.india_vix,

            "india_vix_change_percent":
                self.india_vix_change_percent,

            "breadth":
                self.breadth.to_dict(),

            "nifty":
                (
                    self.nifty.to_dict()
                    if self.nifty
                    else None
                ),

            "bank_nifty":
                (
                    self.bank_nifty.to_dict()
                    if self.bank_nifty
                    else None
                ),

            "fin_nifty":
                (
                    self.fin_nifty.to_dict()
                    if self.fin_nifty
                    else None
                ),

            "midcap_nifty":
                (
                    self.midcap_nifty.to_dict()
                    if self.midcap_nifty
                    else None
                ),

            "sectors": {

                name:
                    sector.to_dict()

                for name, sector
                in self.sectors.items()
            },

            "metadata":
                dict(self.metadata),
        }


# =========================================================
# GLOBAL CONTEXT
# =========================================================

scanner_context = ScannerContext()


# =========================================================
# GET CONTEXT
# =========================================================

def get_scanner_context(
) -> ScannerContext:
    """
    Return shared scanner context.
    """

    return scanner_context


# =========================================================
# RESET CONTEXT
# =========================================================

def reset_scanner_context(
) -> ScannerContext:
    """
    Reset global scanner context.
    """

    scanner_context.reset()

    return scanner_context


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "ScannerContext",

    "SectorState",

    "MarketBreadth",

    "IndexState",

    "scanner_context",

    "get_scanner_context",

    "reset_scanner_context",
]


# ==========================
# END OF FILE
# ==========================