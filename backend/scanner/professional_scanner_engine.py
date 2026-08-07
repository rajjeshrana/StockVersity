from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd

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


# ==========================================================
# SCAN RESULT
# ==========================================================

@dataclass(slots=True)
class ScanResult:

    symbol: str

    timeframe: str

    strategy: str

    signal: str

    score: float = 0.0

    confidence: float = 0.0

    entry: float = 0.0

    stop_loss: float = 0.0

    target: float = 0.0

    risk_reward: float = 0.0

    sector: str = ""

    ai_score: float = 0.0

    volume_score: float = 0.0

    momentum_score: float = 0.0

    trend_score: float = 0.0

    pattern_score: float = 0.0

    reasons: List[str] = field(
        default_factory=list
    )

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )


# ==========================================================
# PROFESSIONAL SCANNER
# ==========================================================

class ProfessionalScannerEngine:

    def __init__(self):

        self.market = market_data_manager

        self.sectors = sector_manager

        self.ai = ai_manager

        self.results: List[
            ScanResult
        ] = []

        self.timeframes = [

            "1m",

            "5m",

            "15m",

            "30m",

            "1h",

            "4h",

            "1D",

            "1W",

        ]

        self.minimum_volume = 500000

        self.minimum_price = 100

        self.maximum_gap = 3

        self.minimum_rvol = 2

        self.minimum_adx = 25

        self.minimum_ai = 75

    # ==========================================================
    # CLEAR RESULTS
    # ==========================================================

    def clear(self):

        self.results.clear()

    # ==========================================================
    # ADD RESULT
    # ==========================================================

    def add(

        self,

        result: ScanResult,

    ):

        self.results.append(

            result

        )

    # ==========================================================
    # ALL RESULTS
    # ==========================================================

    def all(

        self,

    ) -> List[ScanResult]:

        return list(

            self.results

        )

    # ==========================================================
    # SORT RESULTS
    # ==========================================================

    def ranked(

        self,

    ) -> List[ScanResult]:

        return sorted(

            self.results,

            key=lambda x: x.score,

            reverse=True,

        )

    # ==========================================================
    # MARKET FILTER
    # ==========================================================

    def market_filter(

        self,

        stock: MarketData,

    ) -> bool:

        if stock.last_price < self.minimum_price:

            return False

        if stock.volume < self.minimum_volume:

            return False

        if abs(

            stock.gap_percent

        ) > self.maximum_gap:

            return False

        if stock.relative_volume < self.minimum_rvol:

            return False

        if stock.adx < self.minimum_adx:

            return False

        return True

    # ==========================================================
    # AI FILTER
    # ==========================================================

    def ai_filter(

        self,

        symbol: str,

    ) -> bool:

        result = self.ai.get(

            symbol

        )

        if result is None:

            return False

        return (

            result.score >=

            self.minimum_ai

        )

    # ==========================================================
    # SECTOR FILTER
    # ==========================================================

    def sector_filter(

        self,

        symbol: str,

    ) -> bool:

        sector = self.sectors.best_sector_for_stock(

            symbol

        )

        if sector is None:

            return False

        return (

            sector.total_score >= 70

        )

    # ==========================================================
    # BASE FILTER
    # ==========================================================

    def base_filter(

        self,

        stock: MarketData,

    ) -> bool:

        return (

            self.market_filter(

                stock

            )

            and

            self.ai_filter(

                stock.symbol

            )

            and

            self.sector_filter(

                stock.symbol

            )

        )
        # ==========================================================
    # EMA ALIGNMENT
    # ==========================================================

    def ema_alignment(

        self,

        stock: MarketData,

    ) -> bool:

        return (

            stock.ema20 >

            stock.ema50 >

            stock.ema200

            and

            stock.last_price >

            stock.ema20

        )

    # ==========================================================
    # VWAP CONFIRMATION
    # ==========================================================

    def vwap_confirmation(

        self,

        stock: MarketData,

    ) -> bool:

        return (

            stock.last_price >

            stock.vwap

        )

    # ==========================================================
    # MACD CONFIRMATION
    # ==========================================================

    def macd_confirmation(

        self,

        stock: MarketData,

    ) -> bool:

        return (

            stock.macd >

            stock.macd_signal

            and

            stock.macd_histogram > 0

        )

    # ==========================================================
    # OPENING RANGE BREAKOUT (ORB)
    # ==========================================================

    def orb_pattern(

        self,

        stock: MarketData,

    ) -> bool:

        candles = self.market.get_candles(

            stock.symbol,

            "5m",

        )

        if candles is None:

            return False

        if len(candles) < 10:

            return False

        opening_range = candles.iloc[:3]

        orb_high = opening_range["High"].max()

        return (

            stock.last_price >

            orb_high

            and

            stock.relative_volume >= 2

        )

    # ==========================================================
    # BULL FLAG
    # ==========================================================

    def bull_flag(

        self,

        stock: MarketData,

    ) -> bool:

        candles = self.market.get_candles(

            stock.symbol,

            "15m",

        )

        if candles is None:

            return False

        if len(candles) < 30:

            return False

        recent = candles.tail(12)

        return (

            recent["Close"].iloc[-1]

            >

            recent["Close"].mean()

            and

            stock.relative_volume >= 2

            and

            stock.last_price >

            stock.ema20

        )

    # ==========================================================
    # FALLING WEDGE
    # ==========================================================

    def falling_wedge(

        self,

        stock: MarketData,

    ) -> bool:

        candles = self.market.get_candles(

            stock.symbol,

            "1D",

        )

        if candles is None:

            return False

        if len(candles) < 40:

            return False

        highs = candles["High"].tail(20)

        lows = candles["Low"].tail(20)

        return (

            highs.iloc[-1] < highs.iloc[0]

            and

            lows.iloc[-1] < lows.iloc[0]

            and

            stock.last_price >

            stock.ema20

        )

    # ==========================================================
    # VOLATILITY CONTRACTION PATTERN
    # ==========================================================

    def vcp_pattern(

        self,

        stock: MarketData,

    ) -> bool:

        candles = self.market.get_candles(

            stock.symbol,

            "1D",

        )

        if candles is None:

            return False

        if len(candles) < 30:

            return False

        ranges = (

            candles["High"]

            -

            candles["Low"]

        ).tail(10)

        contraction = (

            ranges.iloc[-1]

            <

            ranges.mean()

        )

        return (

            contraction

            and

            stock.relative_volume >= 2

        )

    # ==========================================================
    # CUP & HANDLE
    # ==========================================================

    def cup_handle(

        self,

        stock: MarketData,

    ) -> bool:

        candles = self.market.get_candles(

            stock.symbol,

            "1D",

        )

        if candles is None:

            return False

        if len(candles) < 80:

            return False

        closes = candles["Close"]

        return (

            closes.iloc[-1]

            >

            closes.tail(40).mean()

            and

            stock.last_price >

            stock.ema50

        )

    # ==========================================================
    # DARVAS BOX
    # ==========================================================

    def darvas_box(

        self,

        stock: MarketData,

    ) -> bool:

        candles = self.market.get_candles(

            stock.symbol,

            "1D",

        )

        if candles is None:

            return False

        if len(candles) < 25:

            return False

        recent = candles.tail(20)

        resistance = recent["High"].max()

        return (

            stock.last_price >

            resistance

        )
        # ==========================================================
    # PATTERN SCORE
    # ==========================================================

    def pattern_score(

        self,

        stock: MarketData,

    ) -> tuple[float, str]:

        score = 0

        strategy = ""

        if self.orb_pattern(stock):

            score += 95

            strategy = "ORB"

        if self.vcp_pattern(stock):

            score += 90

            strategy = "VCP"

        if self.bull_flag(stock):

            score += 88

            strategy = "Bull Flag"

        if self.falling_wedge(stock):

            score += 86

            strategy = "Falling Wedge"

        if self.cup_handle(stock):

            score += 92

            strategy = "Cup & Handle"

        if self.darvas_box(stock):

            score += 89

            strategy = "Darvas Box"

        return min(score, 100), strategy

    # ==========================================================
    # MOMENTUM SCORE
    # ==========================================================

    def momentum_score(

        self,

        stock: MarketData,

    ) -> float:

        score = 0

        if stock.rsi >= 60:

            score += 25

        if stock.adx >= 25:

            score += 25

        if stock.relative_volume >= 2:

            score += 25

        if stock.change_percent > 2:

            score += 25

        return min(score, 100)

    # ==========================================================
    # TREND SCORE
    # ==========================================================

    def trend_score(

        self,

        stock: MarketData,

    ) -> float:

        score = 0

        if self.ema_alignment(stock):

            score += 40

        if self.vwap_confirmation(stock):

            score += 30

        if self.macd_confirmation(stock):

            score += 30

        return min(score, 100)

    # ==========================================================
    # BUILD REASONS
    # ==========================================================

    def build_reasons(

        self,

        stock: MarketData,

        strategy: str,

    ) -> List[str]:

        reasons = []

        reasons.append(

            f"Strategy : {strategy}"

        )

        if self.ema_alignment(stock):

            reasons.append(

                "EMA alignment confirmed"

            )

        if self.vwap_confirmation(stock):

            reasons.append(

                "Trading above VWAP"

            )

        if self.macd_confirmation(stock):

            reasons.append(

                "MACD bullish"

            )

        if stock.relative_volume >= 2:

            reasons.append(

                "High Relative Volume"

            )

        if stock.adx >= 25:

            reasons.append(

                "Strong Trend"

            )

        if stock.day_high_breakout:

            reasons.append(

                "Day Breakout"

            )

        if stock.week_high_breakout:

            reasons.append(

                "Weekly Breakout"

            )

        return reasons

    # ==========================================================
    # CALCULATE TRADE LEVELS
    # ==========================================================

    def trade_levels(

        self,

        stock: MarketData,

    ):

        entry = stock.last_price

        risk = max(

            stock.atr,

            stock.last_price * 0.01,

        )

        stop = round(

            entry - risk,

            2,

        )

        target = round(

            entry + (risk * 2),

            2,

        )

        rr = round(

            (

                target - entry

            )

            /

            max(

                entry - stop,

                0.01,

            ),

            2,

        )

        return (

            entry,

            stop,

            target,

            rr,

        )

    # ==========================================================
    # CONFIDENCE
    # ==========================================================

    def confidence(

        self,

        ai_score: float,

        pattern: float,

        trend: float,

    ) -> float:

        confidence = (

            ai_score * 0.50 +

            pattern * 0.30 +

            trend * 0.20

        )

        return round(

            min(

                confidence,

                100,

            ),

            2,

        )

    # ==========================================================
    # CREATE RESULT
    # ==========================================================

    def create_result(

        self,

        stock: MarketData,

    ) -> Optional[ScanResult]:

        if not self.base_filter(stock):

            return None

        pattern,

        strategy = self.pattern_score(

            stock

        )

        if pattern == 0:

            return None

        ai = self.ai.get(

            stock.symbol

        )

        if ai is None:

            return None

        trend = self.trend_score(

            stock

        )

        momentum = self.momentum_score(

            stock

        )

        (

            entry,

            stop,

            target,

            rr,

        ) = self.trade_levels(

            stock

        )

        score = round(

            (

                ai.score * 0.40 +

                pattern * 0.25 +

                trend * 0.20 +

                momentum * 0.15

            ),

            2,

        )

        return ScanResult(

            symbol=stock.symbol,

            timeframe=stock.timeframe,

            strategy=strategy,

            signal="BUY",

            score=score,

            confidence=self.confidence(

                ai.score,

                pattern,

                trend,

            ),

            entry=entry,

            stop_loss=stop,

            target=target,

            risk_reward=rr,

            sector=ai.sector,

            ai_score=ai.score,

            volume_score=stock.relative_volume,

            momentum_score=momentum,

            trend_score=trend,

            pattern_score=pattern,

            reasons=self.build_reasons(

                stock,

                strategy,

            ),

        )
        # ==========================================================
    # SCAN SINGLE STOCK
    # ==========================================================

    def scan_stock(

        self,

        symbol: str,

    ) -> Optional[ScanResult]:

        stock = self.market.get(

            symbol

        )

        if stock is None:

            return None

        result = self.create_result(

            stock

        )

        if result:

            self.add(

                result

            )

        return result

    # ==========================================================
    # SCAN ALL STOCKS
    # ==========================================================

    def scan_all(

        self,

    ) -> List[ScanResult]:

        self.clear()

        for stock in self.market.all_symbols():

            self.scan_stock(

                stock.symbol

            )

        self.results = sorted(

            self.results,

            key=lambda x: (

                x.score,

                x.confidence,

            ),

            reverse=True,

        )

        return self.results

    # ==========================================================
    # SCAN BY TIMEFRAME
    # ==========================================================

    def scan_timeframe(

        self,

        timeframe: str,

    ) -> List[ScanResult]:

        self.clear()

        for stock in self.market.all_symbols():

            if stock.timeframe != timeframe:

                continue

            self.scan_stock(

                stock.symbol

            )

        return self.ranked()

    # ==========================================================
    # INTRADAY SCANNER
    # ==========================================================

    def intraday_scan(

        self,

    ) -> List[ScanResult]:

        self.clear()

        allowed = {

            "1m",

            "5m",

            "15m",

        }

        for stock in self.market.all_symbols():

            if stock.timeframe not in allowed:

                continue

            self.scan_stock(

                stock.symbol

            )

        return self.ranked()

    # ==========================================================
    # SWING SCANNER
    # ==========================================================

    def swing_scan(

        self,

    ) -> List[ScanResult]:

        self.clear()

        allowed = {

            "1h",

            "4h",

            "1D",

        }

        for stock in self.market.all_symbols():

            if stock.timeframe not in allowed:

                continue

            self.scan_stock(

                stock.symbol

            )

        return self.ranked()

    # ==========================================================
    # POSITIONAL SCANNER
    # ==========================================================

    def positional_scan(

        self,

    ) -> List[ScanResult]:

        self.clear()

        allowed = {

            "1D",

            "1W",

        }

        for stock in self.market.all_symbols():

            if stock.timeframe not in allowed:

                continue

            self.scan_stock(

                stock.symbol

            )

        return self.ranked()

    # ==========================================================
    # ORB SCANNER
    # ==========================================================

    def orb_scan(

        self,

    ) -> List[ScanResult]:

        self.clear()

        for stock in self.market.all_symbols():

            if not self.orb_pattern(

                stock

            ):

                continue

            self.scan_stock(

                stock.symbol

            )

        return self.ranked()

    # ==========================================================
    # VCP SCANNER
    # ==========================================================

    def vcp_scan(

        self,

    ) -> List[ScanResult]:

        self.clear()

        for stock in self.market.all_symbols():

            if not self.vcp_pattern(

                stock

            ):

                continue

            self.scan_stock(

                stock.symbol

            )

        return self.ranked()

    # ==========================================================
    # FALLING WEDGE SCANNER
    # ==========================================================

    def falling_wedge_scan(

        self,

    ) -> List[ScanResult]:

        self.clear()

        for stock in self.market.all_symbols():

            if not self.falling_wedge(

                stock

            ):

                continue

            self.scan_stock(

                stock.symbol

            )

        return self.ranked()

    # ==========================================================
    # BULL FLAG SCANNER
    # ==========================================================

    def bull_flag_scan(

        self,

    ) -> List[ScanResult]:

        self.clear()

        for stock in self.market.all_symbols():

            if not self.bull_flag(

                stock

            ):

                continue

            self.scan_stock(

                stock.symbol

            )

        return self.ranked()

    # ==========================================================
    # CUP & HANDLE SCANNER
    # ==========================================================

    def cup_handle_scan(

        self,

    ) -> List[ScanResult]:

        self.clear()

        for stock in self.market.all_symbols():

            if not self.cup_handle(

                stock

            ):

                continue

            self.scan_stock(

                stock.symbol

            )

        return self.ranked()

    # ==========================================================
    # DARVAS BOX SCANNER
    # ==========================================================

    def darvas_scan(

        self,

    ) -> List[ScanResult]:

        self.clear()

        for stock in self.market.all_symbols():

            if not self.darvas_box(

                stock

            ):

                continue

            self.scan_stock(

                stock.symbol

            )

        return self.ranked()

    # ==========================================================
    # TOP OPPORTUNITIES
    # ==========================================================

    def top_opportunities(

        self,

        limit: int = 10,

    ) -> List[ScanResult]:

        return self.ranked()[:limit]
        # ==========================================================
    # NIFTY TREND FILTER
    # ==========================================================

    def nifty_trend_filter(

        self,

    ) -> bool:

        nifty = self.market.get(

            "NIFTY"

        )

        if nifty is None:

            return True

        return (

            nifty.last_price >

            nifty.ema20

            and

            nifty.ema20 >

            nifty.ema50

        )

    # ==========================================================
    # SECTOR ROTATION FILTER
    # ==========================================================

    def sector_rotation_filter(

        self,

        stock: MarketData,

    ) -> bool:

        sector = self.sectors.best_sector_for_stock(

            stock.symbol

        )

        if sector is None:

            return False

        return (

            sector.relative_strength >= 70

            and

            sector.total_score >= 70

        )

    # ==========================================================
    # LIQUIDITY FILTER
    # ==========================================================

    def liquidity_filter(

        self,

        stock: MarketData,

    ) -> bool:

        return (

            stock.volume >= 1_000_000

            and

            stock.value >= 10_00_00_000

        )

    # ==========================================================
    # VOLATILITY FILTER
    # ==========================================================

    def volatility_filter(

        self,

        stock: MarketData,

    ) -> bool:

        return (

            stock.atr >

            0

        )

    # ==========================================================
    # INSTITUTIONAL FILTER
    # ==========================================================

    def institutional_filter(

        self,

        stock: MarketData,

    ) -> bool:

        return (

            self.base_filter(

                stock

            )

            and

            self.nifty_trend_filter()

            and

            self.sector_rotation_filter(

                stock

            )

            and

            self.liquidity_filter(

                stock

            )

            and

            self.volatility_filter(

                stock

            )

        )

    # ==========================================================
    # INSTITUTIONAL SCORE
    # ==========================================================

    def institutional_score(

        self,

        stock: MarketData,

    ) -> float:

        ai = self.ai.get(

            stock.symbol

        )

        if ai is None:

            return 0

        sector = self.sectors.best_sector_for_stock(

            stock.symbol

        )

        sector_score = (

            sector.total_score

            if sector

            else 0

        )

        score = (

            ai.score * 0.40 +

            sector_score * 0.20 +

            self.trend_score(stock) * 0.15 +

            self.momentum_score(stock) * 0.15 +

            self.pattern_score(stock)[0] * 0.10

        )

        return round(

            score,

            2,

        )

    # ==========================================================
    # PROFESSIONAL SCAN
    # ==========================================================

    def professional_scan(

        self,

    ) -> List[ScanResult]:

        self.clear()

        for stock in self.market.all_symbols():

            if not self.institutional_filter(

                stock

            ):

                continue

            result = self.create_result(

                stock

            )

            if result is None:

                continue

            result.score = self.institutional_score(

                stock

            )

            self.add(

                result

            )

        self.results.sort(

            key=lambda x: (

                x.score,

                x.confidence,

            ),

            reverse=True,

        )

        return self.results

    # ==========================================================
    # TOP 5 INTRADAY
    # ==========================================================

    def top_intraday(

        self,

    ) -> List[ScanResult]:

        return self.professional_scan()[:5]

    # ==========================================================
    # TOP 5 SWING
    # ==========================================================

    def top_swing(

        self,

    ) -> List[ScanResult]:

        return [

            r

            for r in

            self.professional_scan()

            if r.timeframe in (

                "1h",

                "4h",

                "1D",

            )

        ][:5]

    # ==========================================================
    # TOP 5 POSITIONAL
    # ==========================================================

    def top_positional(

        self,

    ) -> List[ScanResult]:

        return [

            r

            for r in

            self.professional_scan()

            if r.timeframe in (

                "1D",

                "1W",

            )

        ][:5]

    # ==========================================================
    # DASHBOARD DATA
    # ==========================================================

    def dashboard_data(

        self,

    ):

        return {

            "intraday": self.top_intraday(),

            "swing": self.top_swing(),

            "positional": self.top_positional(),

            "total": len(

                self.results

            ),

        }
        # ==========================================================
    # EXPORT RESULTS
    # ==========================================================

    def export_results(

        self,

    ) -> List[Dict]:

        export = []

        for result in self.ranked():

            export.append(

                {

                    "symbol": result.symbol,

                    "strategy": result.strategy,

                    "signal": result.signal,

                    "timeframe": result.timeframe,

                    "score": result.score,

                    "confidence": result.confidence,

                    "entry": result.entry,

                    "stop_loss": result.stop_loss,

                    "target": result.target,

                    "risk_reward": result.risk_reward,

                    "sector": result.sector,

                    "ai_score": result.ai_score,

                    "trend_score": result.trend_score,

                    "momentum_score": result.momentum_score,

                    "pattern_score": result.pattern_score,

                    "volume_score": result.volume_score,

                    "reasons": list(result.reasons),

                    "created_at": result.created_at,

                }

            )

        return export

    # ==========================================================
    # STATISTICS
    # ==========================================================

    def statistics(

        self,

    ) -> Dict:

        total = len(

            self.results

        )

        average = (

            sum(

                r.score

                for r in self.results

            )

            /

            total

            if total

            else 0

        )

        return {

            "results": total,

            "average_score": round(

                average,

                2,

            ),

            "highest_score": max(

                (

                    r.score

                    for r in self.results

                ),

                default=0,

            ),

            "lowest_score": min(

                (

                    r.score

                    for r in self.results

                ),

                default=0,

            ),

        }

    # ==========================================================
    # HEALTH
    # ==========================================================

    def health(

        self,

    ) -> Dict:

        return {

            "status": "healthy",

            "scanner": "Professional Scanner",

            "statistics": self.statistics(),

        }

    # ==========================================================
    # RESET
    # ==========================================================

    def reset(

        self,

    ):

        self.clear()

    # ==========================================================
    # RELOAD
    # ==========================================================

    def reload(

        self,

    ):

        self.reset()

    # ==========================================================
    # STARTUP
    # ==========================================================

    def startup(

        self,

    ):

        self.clear()

        return self.health()

    # ==========================================================
    # SHUTDOWN
    # ==========================================================

    def shutdown(

        self,

    ):

        self.clear()

        return {

            "status": "stopped",

        }

    # ==========================================================
    # VERSION
    # ==========================================================

    @property

    def version(

        self,

    ):

        return "4.0"

    # ==========================================================
    # NAME
    # ==========================================================

    @property

    def name(

        self,

    ):

        return "Professional Scanner Engine"

    # ==========================================================
    # REPR
    # ==========================================================

    def __repr__(

        self,

    ):

        return (

            "ProfessionalScannerEngine("

            f"results={len(self.results)}"

            ")"

        )

    # ==========================================================
    # STR
    # ==========================================================

    def __str__(

        self,

    ):

        stats = self.statistics()

        return (

            "Professional Scanner Engine\n"

            f"Version        : {self.version}\n"

            f"Results        : {stats['results']}\n"

            f"Average Score  : {stats['average_score']}\n"

            f"Highest Score  : {stats['highest_score']}\n"

            f"Lowest Score   : {stats['lowest_score']}"

        )


# ==========================================================
# GLOBAL SINGLETON
# ==========================================================

professional_scanner = ProfessionalScannerEngine()


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [

    "ScanResult",

    "ProfessionalScannerEngine",

    "professional_scanner",

]