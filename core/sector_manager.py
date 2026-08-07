from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any


# ==========================================================
# SECTOR DATA
# ==========================================================

@dataclass(slots=True)
class SectorData:

    name: str

    index_symbol: str = ""

    change_percent: float = 0.0

    volume: float = 0.0

    advancing: int = 0

    declining: int = 0

    unchanged: int = 0

    relative_strength: float = 0.0

    momentum_score: float = 0.0

    breakout_score: float = 0.0

    volume_score: float = 0.0

    trend_score: float = 0.0

    ai_score: float = 0.0

    total_score: float = 0.0

    strongest_stock: str = ""

    weakest_stock: str = ""

    leaders: List[str] = field(
        default_factory=list
    )

    laggards: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )


# ==========================================================
# SECTOR MANAGER
# ==========================================================

class SectorManager:

    _instance = None

    _instance_lock = threading.Lock()

    def __new__(cls):

        with cls._instance_lock:

            if cls._instance is None:

                cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):

        if getattr(self, "_initialized", False):

            return

        self._initialized = True

        self._lock = threading.RLock()

        self.sectors: Dict[
            str,
            SectorData
        ] = {}

        self.stock_sector_map: Dict[
            str,
            str
        ] = {}

        self.initialize_sectors()

    # ==========================================================
    # DEFAULT NSE SECTORS
    # ==========================================================

    def initialize_sectors(self):

        sector_names = [

            "NIFTY AUTO",

            "NIFTY BANK",

            "NIFTY FINANCIAL SERVICES",

            "NIFTY FMCG",

            "NIFTY IT",

            "NIFTY MEDIA",

            "NIFTY METAL",

            "NIFTY PHARMA",

            "NIFTY PSU BANK",

            "NIFTY PRIVATE BANK",

            "NIFTY REALTY",

            "NIFTY ENERGY",

            "NIFTY OIL & GAS",

            "NIFTY HEALTHCARE",

            "NIFTY CONSUMER DURABLES",

            "NIFTY SERVICES",

            "NIFTY INFRASTRUCTURE",

            "NIFTY COMMODITIES",

            "NIFTY CPSE",

            "NIFTY PSE",

            "NIFTY MIDCAP",

            "NIFTY SMALLCAP",

        ]

        for sector in sector_names:

            self.sectors[sector] = SectorData(

                name=sector

            )

    # ==========================================================
    # UPDATE SECTOR
    # ==========================================================

    def update_sector(

        self,

        sector: SectorData,

    ) -> None:

        with self._lock:

            sector.updated_at = datetime.utcnow()

            self.sectors[

                sector.name

            ] = sector

    # ==========================================================
    # GET SECTOR
    # ==========================================================

    def get(

        self,

        sector_name: str,

    ) -> Optional[SectorData]:

        return self.sectors.get(

            sector_name

        )

    # ==========================================================
    # ALL SECTORS
    # ==========================================================

    def all_sectors(

        self,

    ) -> List[SectorData]:

        return list(

            self.sectors.values()

        )

    # ==========================================================
    # MAP STOCK TO SECTOR
    # ==========================================================

    def assign_stock(

        self,

        symbol: str,

        sector: str,

    ) -> None:

        self.stock_sector_map[

            symbol.upper()

        ] = sector

    # ==========================================================
    # GET STOCK SECTOR
    # ==========================================================

    def sector_of(

        self,

        symbol: str,

    ) -> Optional[str]:

        return self.stock_sector_map.get(

            symbol.upper()

        )
        # ==========================================================
    # TOP GAINING SECTORS
    # ==========================================================

    def top_gainers(

        self,

        limit: int = 5,

    ) -> List[SectorData]:

        return sorted(

            self.sectors.values(),

            key=lambda sector: sector.change_percent,

            reverse=True,

        )[:limit]

    # ==========================================================
    # TOP LOSING SECTORS
    # ==========================================================

    def top_losers(

        self,

        limit: int = 5,

    ) -> List[SectorData]:

        return sorted(

            self.sectors.values(),

            key=lambda sector: sector.change_percent,

        )[:limit]

    # ==========================================================
    # RELATIVE STRENGTH RANKING
    # ==========================================================

    def strongest_sectors(

        self,

        limit: int = 10,

    ) -> List[SectorData]:

        return sorted(

            self.sectors.values(),

            key=lambda sector: sector.relative_strength,

            reverse=True,

        )[:limit]

    # ==========================================================
    # WEAKEST SECTORS
    # ==========================================================

    def weakest_sectors(

        self,

        limit: int = 10,

    ) -> List[SectorData]:

        return sorted(

            self.sectors.values(),

            key=lambda sector: sector.relative_strength,

        )[:limit]

    # ==========================================================
    # MOMENTUM RANKING
    # ==========================================================

    def momentum_ranking(

        self,

        limit: int = 10,

    ) -> List[SectorData]:

        return sorted(

            self.sectors.values(),

            key=lambda sector: sector.momentum_score,

            reverse=True,

        )[:limit]

    # ==========================================================
    # TREND RANKING
    # ==========================================================

    def trend_ranking(

        self,

        limit: int = 10,

    ) -> List[SectorData]:

        return sorted(

            self.sectors.values(),

            key=lambda sector: sector.trend_score,

            reverse=True,

        )[:limit]

    # ==========================================================
    # BREAKOUT RANKING
    # ==========================================================

    def breakout_ranking(

        self,

        limit: int = 10,

    ) -> List[SectorData]:

        return sorted(

            self.sectors.values(),

            key=lambda sector: sector.breakout_score,

            reverse=True,

        )[:limit]

    # ==========================================================
    # VOLUME RANKING
    # ==========================================================

    def volume_ranking(

        self,

        limit: int = 10,

    ) -> List[SectorData]:

        return sorted(

            self.sectors.values(),

            key=lambda sector: sector.volume_score,

            reverse=True,

        )[:limit]

    # ==========================================================
    # AI RANKING
    # ==========================================================

    def ai_ranking(

        self,

        limit: int = 10,

    ) -> List[SectorData]:

        return sorted(

            self.sectors.values(),

            key=lambda sector: sector.ai_score,

            reverse=True,

        )[:limit]

    # ==========================================================
    # OVERALL RANKING
    # ==========================================================

    def overall_ranking(

        self,

        limit: int = 10,

    ) -> List[SectorData]:

        return sorted(

            self.sectors.values(),

            key=lambda sector: sector.total_score,

            reverse=True,

        )[:limit]

    # ==========================================================
    # UPDATE TOTAL SCORE
    # ==========================================================

    def calculate_total_score(

        self,

        sector_name: str,

    ) -> float:

        sector = self.get(

            sector_name

        )

        if sector is None:

            return 0.0

        sector.total_score = round(

            (

                sector.relative_strength * 0.25 +

                sector.momentum_score * 0.20 +

                sector.trend_score * 0.20 +

                sector.breakout_score * 0.15 +

                sector.volume_score * 0.10 +

                sector.ai_score * 0.10

            ),

            2,

        )

        sector.updated_at = datetime.utcnow()

        return sector.total_score

    # ==========================================================
    # HEATMAP DATA
    # ==========================================================

    def heatmap_data(

        self,

    ) -> List[Dict[str, Any]]:

        data = []

        for sector in self.overall_ranking(

            limit=len(self.sectors)

        ):

            data.append(

                {

                    "sector": sector.name,

                    "score": sector.total_score,

                    "change": sector.change_percent,

                    "relative_strength": sector.relative_strength,

                    "leaders": sector.leaders,

                    "laggards": sector.laggards,

                }

            )

        return data
        # ==========================================================
    # SEARCH SECTOR
    # ==========================================================

    def search(

        self,

        keyword: str,

    ) -> List[SectorData]:

        keyword = keyword.upper()

        return [

            sector

            for sector in self.sectors.values()

            if keyword in sector.name.upper()

        ]

    # ==========================================================
    # REMOVE SECTOR
    # ==========================================================

    def remove_sector(

        self,

        sector_name: str,

    ) -> bool:

        with self._lock:

            if sector_name not in self.sectors:

                return False

            del self.sectors[sector_name]

            return True

    # ==========================================================
    # BULK UPDATE
    # ==========================================================

    def update_bulk(

        self,

        sectors: List[SectorData],

    ) -> None:

        with self._lock:

            for sector in sectors:

                sector.updated_at = datetime.utcnow()

                self.sectors[

                    sector.name

                ] = sector

    # ==========================================================
    # STOCKS IN SECTOR
    # ==========================================================

    def stocks_in_sector(

        self,

        sector_name: str,

    ) -> List[str]:

        return sorted(

            [

                symbol

                for symbol, sector in

                self.stock_sector_map.items()

                if sector == sector_name

            ]

        )

    # ==========================================================
    # SECTOR COUNT
    # ==========================================================

    def total_sectors(

        self,

    ) -> int:

        return len(

            self.sectors

        )

    # ==========================================================
    # ADVANCE DECLINE RATIO
    # ==========================================================

    def advance_decline_ratio(

        self,

        sector_name: str,

    ) -> float:

        sector = self.get(

            sector_name

        )

        if sector is None:

            return 0.0

        if sector.declining == 0:

            return float(

                sector.advancing

            )

        return round(

            sector.advancing /

            sector.declining,

            2,

        )

    # ==========================================================
    # MARKET BREADTH
    # ==========================================================

    def market_breadth(

        self,

        sector_name: str,

    ) -> Dict[str, int]:

        sector = self.get(

            sector_name

        )

        if sector is None:

            return {}

        return {

            "advancing": sector.advancing,

            "declining": sector.declining,

            "unchanged": sector.unchanged,

        }

    # ==========================================================
    # SECTOR LEADERS
    # ==========================================================

    def leaders(

        self,

        sector_name: str,

    ) -> List[str]:

        sector = self.get(

            sector_name

        )

        if sector is None:

            return []

        return list(

            sector.leaders

        )

    # ==========================================================
    # SECTOR LAGGARDS
    # ==========================================================

    def laggards(

        self,

        sector_name: str,

    ) -> List[str]:

        sector = self.get(

            sector_name

        )

        if sector is None:

            return []

        return list(

            sector.laggards

        )

    # ==========================================================
    # HOT SECTORS
    # ==========================================================

    def hot_sectors(

        self,

        minimum_score: float = 70,

    ) -> List[SectorData]:

        return [

            sector

            for sector in self.sectors.values()

            if sector.total_score >= minimum_score

        ]

    # ==========================================================
    # WEAK SECTORS
    # ==========================================================

    def weak_sectors(

        self,

        maximum_score: float = 40,

    ) -> List[SectorData]:

        return [

            sector

            for sector in self.sectors.values()

            if sector.total_score <= maximum_score

        ]

    # ==========================================================
    # BEST SECTOR FOR STOCK
    # ==========================================================

    def best_sector_for_stock(

        self,

        symbol: str,

    ) -> Optional[SectorData]:

        sector_name = self.sector_of(

            symbol

        )

        if sector_name is None:

            return None

        return self.get(

            sector_name

        )

    # ==========================================================
    # DASHBOARD SUMMARY
    # ==========================================================

    def dashboard_summary(

        self,

    ) -> Dict[str, Any]:

        strongest = self.strongest_sectors(

            limit=3

        )

        weakest = self.weakest_sectors(

            limit=3

        )

        return {

            "total_sectors": self.total_sectors(),

            "strongest": [

                s.name for s in strongest

            ],

            "weakest": [

                s.name for s in weakest

            ],

            "hot_sectors": len(

                self.hot_sectors()

            ),

            "weak_sectors": len(

                self.weak_sectors()

            ),

        }
    # ==========================================================
    # CACHE STATISTICS
    # ==========================================================

    def statistics(

        self,

    ) -> Dict[str, Any]:

        total_stocks = len(

            self.stock_sector_map

        )

        return {

            "total_sectors": len(

                self.sectors

            ),

            "mapped_stocks": total_stocks,

            "hot_sectors": len(

                self.hot_sectors()

            ),

            "weak_sectors": len(

                self.weak_sectors()

            ),

        }

    # ==========================================================
    # HEALTH
    # ==========================================================

    def health(

        self,

    ) -> Dict[str, Any]:

        stats = self.statistics()

        return {

            "status": "healthy",

            "updated": datetime.utcnow(),

            **stats,

        }

    # ==========================================================
    # RESET
    # ==========================================================

    def reset(

        self,

    ) -> None:

        with self._lock:

            self.sectors.clear()

            self.stock_sector_map.clear()

            self.initialize_sectors()

    # ==========================================================
    # RELOAD
    # ==========================================================

    def reload(

        self,

    ) -> None:

        self.reset()

    # ==========================================================
    # STARTUP
    # ==========================================================

    def startup(

        self,

    ) -> Dict[str, Any]:

        return self.health()

    # ==========================================================
    # SHUTDOWN
    # ==========================================================

    def shutdown(

        self,

    ) -> Dict[str, Any]:

        return {

            "status": "stopped",

            "updated": datetime.utcnow(),

        }

    # ==========================================================
    # EXPORT
    # ==========================================================

    def export(

        self,

    ) -> List[Dict[str, Any]]:

        data = []

        for sector in self.overall_ranking(

            limit=len(

                self.sectors

            )

        ):

            data.append(

                {

                    "sector": sector.name,

                    "score": sector.total_score,

                    "change": sector.change_percent,

                    "relative_strength": sector.relative_strength,

                    "momentum": sector.momentum_score,

                    "trend": sector.trend_score,

                    "breakout": sector.breakout_score,

                    "volume": sector.volume_score,

                    "ai": sector.ai_score,

                    "leaders": sector.leaders,

                    "laggards": sector.laggards,

                }

            )

        return data

    # ==========================================================
    # REPR
    # ==========================================================

    def __repr__(

        self,

    ) -> str:

        return (

            "SectorManager("

            f"sectors={len(self.sectors)}, "

            f"stocks={len(self.stock_sector_map)}"

            ")"

        )

    # ==========================================================
    # STR
    # ==========================================================

    def __str__(

        self,

    ) -> str:

        stats = self.statistics()

        return (

            "Sector Manager\n"

            f"Total Sectors : {stats['total_sectors']}\n"

            f"Mapped Stocks : {stats['mapped_stocks']}\n"

            f"Hot Sectors   : {stats['hot_sectors']}\n"

            f"Weak Sectors  : {stats['weak_sectors']}"

        )


# ==========================================================
# GLOBAL SINGLETON
# ==========================================================

sector_manager = SectorManager()


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [

    "SectorData",

    "SectorManager",

    "sector_manager",

]