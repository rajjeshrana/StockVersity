"""
=========================================================
StockVersity Scanner Pro
Market Analyzer

Institutional Market Analysis Engine

Author : StockVersity
=========================================================
"""

from __future__ import annotations

import logging
import threading

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import numpy as np
import pandas as pd

from core.data_manager import DataManager
from core.indicator_engine import IndicatorEngine
from core.upstox_client import UpstoxClient


# =========================================================
# MARKET REGIME
# =========================================================

class MarketRegime:

    STRONG_BULL = "Strong Bull"

    BULL = "Bull"

    SIDEWAYS = "Sideways"

    BEAR = "Bear"

    STRONG_BEAR = "Strong Bear"


# =========================================================
# MARKET SENTIMENT
# =========================================================

class MarketSentiment:

    VERY_BULLISH = "Very Bullish"

    BULLISH = "Bullish"

    NEUTRAL = "Neutral"

    BEARISH = "Bearish"

    VERY_BEARISH = "Very Bearish"


# =========================================================
# MARKET SCORE
# =========================================================

@dataclass
class MarketScore:

    overall: float = 0

    trend: float = 0

    momentum: float = 0

    breadth: float = 0

    volatility: float = 0

    volume: float = 0

    sector_strength: float = 0

    sentiment: str = MarketSentiment.NEUTRAL

    regime: str = MarketRegime.SIDEWAYS

    recommendation: str = "Neutral"

    timestamp: datetime = datetime.now()


# =========================================================
# MARKET ANALYZER
# =========================================================

class MarketAnalyzer:

    VERSION = "1.0.0"

    def __init__(

        self,

        client: UpstoxClient,

        data_manager: DataManager,

        indicators: Optional[IndicatorEngine] = None,

    ):

        self.client = client

        self.data = data_manager

        self.indicators = (

            indicators

            if indicators

            else data_manager.indicators

        )

        self.logger = logging.getLogger(

            self.__class__.__name__

        )

        self.lock = threading.RLock()

        # -----------------------------
        # Cached market information
        # -----------------------------

        self.market_score = MarketScore()

        self.index_data: Dict[
            str,
            pd.DataFrame,
        ] = {}

        self.sector_data: Dict[
            str,
            pd.DataFrame,
        ] = {}

        self.market_breadth: Dict[
            str,
            Any,
        ] = {}

        self.market_context: Dict[
            str,
            Any,
        ] = {}

        self.last_update: Optional[
            datetime
        ] = None

        # -----------------------------
        # Statistics
        # -----------------------------

        self.requests = 0

        self.cache_hits = 0

        self.cache_misses = 0

        self.started = datetime.now()

        self.logger.info(

            "MarketAnalyzer initialized."

        )

    # =====================================================
    # REGISTER INDEX DATA
    # =====================================================

    def register_index(

        self,

        name: str,

        dataframe: pd.DataFrame,

    ) -> None:
        """
        Register an index dataframe.
        """

        with self.lock:

            self.index_data[name] = dataframe.copy()

    # =====================================================
    # REGISTER SECTOR DATA
    # =====================================================

    def register_sector(

        self,

        sector: str,

        dataframe: pd.DataFrame,

    ) -> None:
        """
        Register sector dataframe.
        """

        with self.lock:

            self.sector_data[

                sector

            ] = dataframe.copy()

    # =====================================================
    # GET INDEX
    # =====================================================

    def index(

        self,

        name: str,

    ) -> Optional[pd.DataFrame]:

        return self.index_data.get(

            name

        )

    # =====================================================
    # GET SECTOR
    # =====================================================

    def sector(

        self,

        name: str,

    ) -> Optional[pd.DataFrame]:

        return self.sector_data.get(

            name

        )
        # =====================================================
    # EMA TREND
    # =====================================================

    def ema_trend(
        self,
        dataframe: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        Evaluate EMA alignment and trend.
        """

        ema21 = self.indicators.ema_dataframe(
            dataframe,
            21,
        )

        ema50 = self.indicators.ema_dataframe(
            dataframe,
            50,
        )

        ema200 = self.indicators.ema_dataframe(
            dataframe,
            200,
        )

        close = float(
            dataframe["close"].iloc[-1]
        )

        alignment = (

            close > ema21 > ema50 > ema200

        )

        bearish_alignment = (

            close < ema21 < ema50 < ema200

        )

        score = 50.0

        if alignment:

            score = 100.0

        elif bearish_alignment:

            score = 0.0

        elif close > ema50:

            score = 75.0

        elif close < ema50:

            score = 25.0

        return {

            "close": close,

            "ema21": ema21,

            "ema50": ema50,

            "ema200": ema200,

            "bullish_alignment": alignment,

            "bearish_alignment": bearish_alignment,

            "score": score,

        }

    # =====================================================
    # RSI MOMENTUM
    # =====================================================

    def rsi_strength(
        self,
        dataframe: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        RSI momentum analysis.
        """

        rsi = self.indicators.rsi_dataframe(
            dataframe
        )

        if rsi >= 70:

            strength = "Strong Bullish"

            score = 100

        elif rsi >= 60:

            strength = "Bullish"

            score = 80

        elif rsi >= 45:

            strength = "Neutral"

            score = 55

        elif rsi >= 30:

            strength = "Bearish"

            score = 25

        else:

            strength = "Strong Bearish"

            score = 0

        return {

            "rsi": rsi,

            "strength": strength,

            "score": score,

        }

    # =====================================================
    # MACD ANALYSIS
    # =====================================================

    def macd_strength(
        self,
        dataframe: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        MACD trend confirmation.
        """

        macd = self.indicators.macd_dataframe(
            dataframe
        )

        histogram = macd["histogram"]

        bullish = histogram > 0

        score = 80 if bullish else 20

        return {

            "macd": macd,

            "bullish": bullish,

            "score": score,

        }

    # =====================================================
    # ADX ANALYSIS
    # =====================================================

    def adx_strength(
        self,
        dataframe: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        Trend quality.
        """

        adx = self.indicators.adx_dataframe(
            dataframe
        )

        if adx >= 40:

            quality = "Excellent"

            score = 100

        elif adx >= 30:

            quality = "Strong"

            score = 80

        elif adx >= 20:

            quality = "Average"

            score = 60

        else:

            quality = "Weak"

            score = 20

        return {

            "adx": adx,

            "quality": quality,

            "score": score,

        }

    # =====================================================
    # ATR VOLATILITY
    # =====================================================

    def volatility(
        self,
        dataframe: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        ATR based volatility.
        """

        atr = self.indicators.atr_dataframe(
            dataframe
        )

        close = float(
            dataframe.close.iloc[-1]
        )

        percentage = (

            atr / close

        ) * 100

        return {

            "atr": atr,

            "atr_percent": round(

                percentage,

                2,

            ),

            "score": min(

                100,

                percentage * 20,

            ),

        }

    # =====================================================
    # PRICE STRUCTURE
    # =====================================================

    def price_structure(
        self,
        dataframe: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        Analyze recent swing structure.
        """

        highs = dataframe["high"].tail(10)

        lows = dataframe["low"].tail(10)

        higher_high = (

            highs.iloc[-1]

            > highs.max()

            - 1e-8

        )

        higher_low = (

            lows.iloc[-1]

            > lows.min()

        )

        bullish = (

            higher_high

            and higher_low

        )

        return {

            "higher_high": higher_high,

            "higher_low": higher_low,

            "bullish_structure": bullish,

            "score": 100 if bullish else 40,

        }

    # =====================================================
    # TREND SCORE
    # =====================================================

    def trend_score(
        self,
        dataframe: pd.DataFrame,
    ) -> float:
        """
        Overall market trend score.
        """

        ema = self.ema_trend(
            dataframe
        )["score"]

        rsi = self.rsi_strength(
            dataframe
        )["score"]

        macd = self.macd_strength(
            dataframe
        )["score"]

        adx = self.adx_strength(
            dataframe
        )["score"]

        structure = self.price_structure(
            dataframe
        )["score"]

        score = np.mean(

            [

                ema,

                rsi,

                macd,

                adx,

                structure,

            ]

        )

        return round(

            float(score),

            2,

        )
        # =====================================================
    # MARKET REGIME
    # =====================================================

    def detect_regime(
        self,
        dataframe: pd.DataFrame,
    ) -> str:
        """
        Detect the current market regime.
        """

        score = self.trend_score(
            dataframe
        )

        if score >= 85:

            return MarketRegime.STRONG_BULL

        if score >= 65:

            return MarketRegime.BULL

        if score >= 40:

            return MarketRegime.SIDEWAYS

        if score >= 20:

            return MarketRegime.BEAR

        return MarketRegime.STRONG_BEAR

    # =====================================================
    # MARKET SENTIMENT
    # =====================================================

    def sentiment(
        self,
        dataframe: pd.DataFrame,
    ) -> str:
        """
        Determine market sentiment.
        """

        score = self.trend_score(
            dataframe
        )

        if score >= 85:

            return MarketSentiment.VERY_BULLISH

        if score >= 65:

            return MarketSentiment.BULLISH

        if score >= 40:

            return MarketSentiment.NEUTRAL

        if score >= 20:

            return MarketSentiment.BEARISH

        return MarketSentiment.VERY_BEARISH

    # =====================================================
    # TRADING RECOMMENDATION
    # =====================================================

    def recommendation(
        self,
        dataframe: pd.DataFrame,
    ) -> str:
        """
        Generate a market recommendation.
        """

        regime = self.detect_regime(
            dataframe
        )

        if regime == MarketRegime.STRONG_BULL:

            return "Aggressive Long"

        if regime == MarketRegime.BULL:

            return "Long"

        if regime == MarketRegime.SIDEWAYS:

            return "Wait"

        if regime == MarketRegime.BEAR:

            return "Short"

        return "Aggressive Short"

    # =====================================================
    # BUILD MARKET SCORE
    # =====================================================

    def build_score(
        self,
        dataframe: pd.DataFrame,
    ) -> MarketScore:
        """
        Build a complete MarketScore object.
        """

        trend = self.trend_score(
            dataframe
        )

        momentum = self.rsi_strength(
            dataframe
        )["score"]

        volatility = self.volatility(
            dataframe
        )["score"]

        volume = 50.0

        breadth = 50.0

        sector = 50.0

        overall = round(

            float(

                np.mean(

                    [

                        trend,

                        momentum,

                        volatility,

                        volume,

                        breadth,

                        sector,

                    ]

                )

            ),

            2,

        )

        score = MarketScore(

            overall=overall,

            trend=trend,

            momentum=momentum,

            breadth=breadth,

            volatility=volatility,

            volume=volume,

            sector_strength=sector,

            sentiment=self.sentiment(

                dataframe

            ),

            regime=self.detect_regime(

                dataframe

            ),

            recommendation=self.recommendation(

                dataframe

            ),

            timestamp=datetime.now(),

        )

        self.market_score = score

        return score

    # =====================================================
    # ANALYZE INDEX
    # =====================================================

    def analyze_index(
        self,
        index_name: str,
    ) -> Optional[MarketScore]:
        """
        Analyze a registered index.
        """

        dataframe = self.index(
            index_name
        )

        if dataframe is None:

            return None

        return self.build_score(
            dataframe
        )

    # =====================================================
    # ANALYZE ALL INDICES
    # =====================================================

    def analyze_all_indices(
        self,
    ) -> Dict[str, MarketScore]:
        """
        Analyze all registered indices.
        """

        output: Dict[
            str,
            MarketScore,
        ] = {}

        for name in self.index_data:

            result = self.analyze_index(
                name
            )

            if result:

                output[name] = result

        self.last_update = datetime.now()

        return output

    # =====================================================
    # MARKET CONTEXT
    # =====================================================

    def context(
        self,
        index_name: str,
    ) -> Dict[str, Any]:
        """
        Scanner-ready market context.
        """

        score = self.analyze_index(
            index_name
        )

        if score is None:

            return {}

        return {

            "index": index_name,

            "overall_score": score.overall,

            "trend": score.trend,

            "momentum": score.momentum,

            "volatility": score.volatility,

            "breadth": score.breadth,

            "volume": score.volume,

            "sector_strength": score.sector_strength,

            "regime": score.regime,

            "sentiment": score.sentiment,

            "recommendation": score.recommendation,

            "timestamp": score.timestamp,

        }

    # =====================================================
    # MARKET FILTER
    # =====================================================

    def trade_allowed(
        self,
        index_name: str,
        minimum_score: float = 60.0,
    ) -> bool:
        """
        Determine whether scanners are allowed to trade.
        """

        score = self.analyze_index(
            index_name
        )

        if score is None:

            return False

        return score.overall >= minimum_score
        # =====================================================
    # ADVANCE / DECLINE
    # =====================================================

    def advance_decline(
        self,
        market_data: Dict[str, pd.DataFrame],
    ) -> Dict[str, Any]:
        """
        Calculate Advance / Decline statistics.
        """

        advances = 0

        declines = 0

        unchanged = 0

        for dataframe in market_data.values():

            if dataframe.empty:

                continue

            close = float(

                dataframe["close"].iloc[-1]

            )

            previous = float(

                dataframe["close"].iloc[-2]

            )

            if close > previous:

                advances += 1

            elif close < previous:

                declines += 1

            else:

                unchanged += 1

        ratio = (

            advances / declines

            if declines > 0

            else float("inf")

        )

        return {

            "advances": advances,

            "declines": declines,

            "unchanged": unchanged,

            "ratio": round(

                ratio,

                2,

            ),

        }

    # =====================================================
    # NEW HIGH / NEW LOW
    # =====================================================

    def new_high_low(
        self,
        market_data: Dict[str, pd.DataFrame],
        period: int = 52,
    ) -> Dict[str, int]:
        """
        Count fresh highs and lows.
        """

        new_high = 0

        new_low = 0

        for dataframe in market_data.values():

            if len(dataframe) < period:

                continue

            latest = dataframe.iloc[-1]

            highest = dataframe["high"].tail(

                period

            ).max()

            lowest = dataframe["low"].tail(

                period

            ).min()

            if latest["high"] >= highest:

                new_high += 1

            if latest["low"] <= lowest:

                new_low += 1

        return {

            "new_high": new_high,

            "new_low": new_low,

        }

    # =====================================================
    # BREADTH SCORE
    # =====================================================

    def breadth_score(
        self,
        market_data: Dict[str, pd.DataFrame],
    ) -> float:
        """
        Calculate market breadth score.
        """

        stats = self.advance_decline(

            market_data

        )

        total = (

            stats["advances"]

            + stats["declines"]

            + stats["unchanged"]

        )

        if total == 0:

            return 50.0

        score = (

            stats["advances"]

            / total

        ) * 100

        return round(

            score,

            2,

        )

    # =====================================================
    # BREADTH MOMENTUM
    # =====================================================

    def breadth_momentum(
        self,
        market_data: Dict[str, pd.DataFrame],
    ) -> str:
        """
        Classify market breadth.
        """

        score = self.breadth_score(

            market_data

        )

        if score >= 80:

            return "Extremely Strong"

        if score >= 65:

            return "Strong"

        if score >= 45:

            return "Neutral"

        if score >= 30:

            return "Weak"

        return "Extremely Weak"

    # =====================================================
    # MARKET PARTICIPATION
    # =====================================================

    def participation(
        self,
        market_data: Dict[str, pd.DataFrame],
    ) -> Dict[str, Any]:
        """
        Measure participation across all stocks.
        """

        total = len(

            market_data

        )

        active = 0

        bullish = 0

        bearish = 0

        for dataframe in market_data.values():

            if dataframe.empty:

                continue

            active += 1

            close = dataframe["close"].iloc[-1]

            ema21 = self.indicators.ema_dataframe(

                dataframe,

                21,

            )

            if close > ema21:

                bullish += 1

            else:

                bearish += 1

        participation = (

            (active / total) * 100

            if total

            else 0

        )

        return {

            "tracked": total,

            "active": active,

            "participation": round(

                participation,

                2,

            ),

            "bullish": bullish,

            "bearish": bearish,

        }

    # =====================================================
    # UPDATE BREADTH CACHE
    # =====================================================

    def update_breadth(
        self,
        market_data: Dict[str, pd.DataFrame],
    ) -> Dict[str, Any]:
        """
        Refresh cached breadth statistics.
        """

        self.market_breadth = {

            "advance_decline": self.advance_decline(

                market_data

            ),

            "new_high_low": self.new_high_low(

                market_data

            ),

            "breadth_score": self.breadth_score(

                market_data

            ),

            "breadth_momentum": self.breadth_momentum(

                market_data

            ),

            "participation": self.participation(

                market_data

            ),

            "updated": datetime.now(),

        }

        return self.market_breadth

    # =====================================================
    # BREADTH SUMMARY
    # =====================================================

    def breadth_summary(
        self,
    ) -> Dict[str, Any]:
        """
        Return cached market breadth.
        """

        return self.market_breadth.copy()
        # =====================================================
    # SECTOR PERFORMANCE
    # =====================================================

    def sector_performance(
        self,
        sector: str,
    ) -> Dict[str, Any]:
        """
        Calculate sector performance statistics.
        """

        dataframe = self.sector(
            sector
        )

        if dataframe is None or dataframe.empty:

            return {}

        latest = dataframe.iloc[-1]

        previous = dataframe.iloc[-2]

        change = (

            (

                latest["close"]

                - previous["close"]

            )

            / previous["close"]

        ) * 100

        trend = self.trend_score(
            dataframe
        )

        return {

            "sector": sector,

            "price": float(

                latest["close"]

            ),

            "change_percent": round(

                float(change),

                2,

            ),

            "trend_score": trend,

            "volume": int(

                latest["volume"]

            ),

        }

    # =====================================================
    # RELATIVE STRENGTH
    # =====================================================

    def relative_strength(
        self,
        sector: str,
        benchmark: str = "NIFTY",
    ) -> float:
        """
        Relative strength against benchmark.
        """

        sector_df = self.sector(
            sector
        )

        benchmark_df = self.index(
            benchmark
        )

        if (

            sector_df is None

            or benchmark_df is None

            or sector_df.empty

            or benchmark_df.empty

        ):

            return 0.0

        sector_return = (

            (

                sector_df["close"].iloc[-1]

                - sector_df["close"].iloc[-20]

            )

            / sector_df["close"].iloc[-20]

        ) * 100

        benchmark_return = (

            (

                benchmark_df["close"].iloc[-1]

                - benchmark_df["close"].iloc[-20]

            )

            / benchmark_df["close"].iloc[-20]

        ) * 100

        return round(

            float(

                sector_return

                - benchmark_return

            ),

            2,

        )

    # =====================================================
    # SECTOR RANKING
    # =====================================================

    def sector_ranking(
        self,
        benchmark: str = "NIFTY",
    ) -> List[Dict[str, Any]]:
        """
        Rank sectors by relative strength.
        """

        rankings = []

        for sector in self.sector_data:

            performance = self.sector_performance(

                sector

            )

            if not performance:

                continue

            performance["relative_strength"] = (

                self.relative_strength(

                    sector,

                    benchmark,

                )

            )

            rankings.append(

                performance

            )

        rankings.sort(

            key=lambda x: (

                x["relative_strength"],

                x["trend_score"],

            ),

            reverse=True,

        )

        return rankings

    # =====================================================
    # LEADING SECTORS
    # =====================================================

    def leading_sectors(
        self,
        top: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Top-performing sectors.
        """

        return self.sector_ranking()[:top]

    # =====================================================
    # LAGGING SECTORS
    # =====================================================

    def lagging_sectors(
        self,
        bottom: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Worst-performing sectors.
        """

        ranking = self.sector_ranking()

        return ranking[-bottom:]

    # =====================================================
    # SECTOR MOMENTUM
    # =====================================================

    def sector_momentum(
        self,
        sector: str,
    ) -> Dict[str, Any]:
        """
        Sector momentum using RSI and MACD.
        """

        dataframe = self.sector(
            sector
        )

        if dataframe is None:

            return {}

        rsi = self.rsi_strength(
            dataframe
        )

        macd = self.macd_strength(
            dataframe
        )

        momentum = round(

            (

                rsi["score"]

                + macd["score"]

            ) / 2,

            2,

        )

        return {

            "sector": sector,

            "rsi": rsi,

            "macd": macd,

            "momentum": momentum,

        }

    # =====================================================
    # HEATMAP DATA
    # =====================================================

    def sector_heatmap(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Dashboard-ready heatmap data.
        """

        heatmap = []

        for sector in self.sector_ranking():

            heatmap.append(

                {

                    "sector": sector["sector"],

                    "strength": sector[
                        "trend_score"
                    ],

                    "change": sector[
                        "change_percent"
                    ],

                    "relative_strength": sector[
                        "relative_strength"
                    ],

                }

            )

        return heatmap

    # =====================================================
    # SECTOR SUMMARY
    # =====================================================

    def sector_summary(
        self,
    ) -> Dict[str, Any]:
        """
        Scanner and dashboard sector summary.
        """

        ranking = self.sector_ranking()

        return {

            "leaders": ranking[:3],

            "laggards": ranking[-3:],

            "heatmap": self.sector_heatmap(),

            "total_sectors": len(

                ranking

            ),

            "updated": datetime.now(),

        }
        # =====================================================
    # REGISTER INDIA VIX
    # =====================================================

    def register_vix(
        self,
        dataframe: pd.DataFrame,
    ) -> None:
        """
        Register India VIX data.
        """

        self.register_index(

            "INDIA_VIX",

            dataframe,

        )

    # =====================================================
    # INDIA VIX ANALYSIS
    # =====================================================

    def vix_analysis(
        self,
    ) -> Dict[str, Any]:
        """
        Analyze India VIX.
        """

        dataframe = self.index(

            "INDIA_VIX"

        )

        if dataframe is None or dataframe.empty:

            return {}

        latest = float(

            dataframe["close"].iloc[-1]

        )

        previous = float(

            dataframe["close"].iloc[-2]

        )

        change = latest - previous

        if latest < 13:

            regime = "Very Low"

            score = 100

        elif latest < 16:

            regime = "Low"

            score = 80

        elif latest < 20:

            regime = "Normal"

            score = 60

        elif latest < 25:

            regime = "High"

            score = 35

        else:

            regime = "Extreme"

            score = 10

        return {

            "vix": latest,

            "change": round(

                change,

                2,

            ),

            "regime": regime,

            "score": score,

        }

    # =====================================================
    # GAP ANALYSIS
    # =====================================================

    def gap_analysis(
        self,
        dataframe: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        Analyze today's opening gap.
        """

        latest = dataframe.iloc[-1]

        previous = dataframe.iloc[-2]

        gap = (

            (

                latest["open"]

                - previous["close"]

            )

            / previous["close"]

        ) * 100

        if gap >= 3:

            gap_type = "Gap Up"

        elif gap <= -3:

            gap_type = "Gap Down"

        else:

            gap_type = "Normal"

        return {

            "gap_percent": round(

                float(gap),

                2,

            ),

            "gap_type": gap_type,

            "valid_for_orb": abs(gap) < 3,

        }

    # =====================================================
    # OPENING RANGE
    # =====================================================

    def opening_range(
        self,
        dataframe: pd.DataFrame,
        candles: int = 3,
    ) -> Dict[str, Any]:
        """
        Calculate Opening Range.
        """

        orb = dataframe.head(

            candles

        )

        high = float(

            orb["high"].max()

        )

        low = float(

            orb["low"].min()

        )

        width = high - low

        close = float(

            dataframe.iloc[-1]["close"]

        )

        percent = (

            width / close

        ) * 100

        return {

            "high": high,

            "low": low,

            "width": round(

                width,

                2,

            ),

            "width_percent": round(

                percent,

                2,

            ),

            "acceptable": percent <= 3,

        }

    # =====================================================
    # INTRADAY VOLATILITY
    # =====================================================

    def intraday_volatility(
        self,
        dataframe: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        Measure current intraday volatility.
        """

        returns = dataframe[

            "close"

        ].pct_change()

        volatility = (

            returns.std()

            * np.sqrt(

                len(returns)

            )

            * 100

        )

        return {

            "volatility": round(

                float(volatility),

                2,

            ),

            "score": min(

                100,

                float(volatility) * 12,

            ),

        }

    # =====================================================
    # VOLATILITY REGIME
    # =====================================================

    def volatility_regime(
        self,
        dataframe: pd.DataFrame,
    ) -> str:
        """
        Classify volatility.
        """

        value = self.intraday_volatility(

            dataframe

        )["volatility"]

        if value < 1:

            return "Very Low"

        if value < 2:

            return "Low"

        if value < 3:

            return "Normal"

        if value < 5:

            return "High"

        return "Extreme"

    # =====================================================
    # VOLATILITY FILTER
    # =====================================================

    def volatility_filter(
        self,
        dataframe: pd.DataFrame,
        minimum: float = 1.0,
        maximum: float = 5.0,
    ) -> bool:
        """
        Filter unsuitable volatility.
        """

        value = self.intraday_volatility(

            dataframe

        )["volatility"]

        return minimum <= value <= maximum

    # =====================================================
    # MARKET OPEN ANALYSIS
    # =====================================================

    def market_open_analysis(
        self,
        dataframe: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        Combined market-open analysis.
        """

        return {

            "gap": self.gap_analysis(

                dataframe

            ),

            "opening_range": self.opening_range(

                dataframe

            ),

            "volatility": self.intraday_volatility(

                dataframe

            ),

            "volatility_regime": self.volatility_regime(

                dataframe

            ),

        }
        # =====================================================
    # FII / DII DATA
    # =====================================================

    def update_institutional_flow(
        self,
        fii_buy: float,
        fii_sell: float,
        dii_buy: float,
        dii_sell: float,
    ) -> None:
        """
        Update daily institutional activity.
        """

        self.market_context["institutional"] = {

            "fii_buy": fii_buy,

            "fii_sell": fii_sell,

            "dii_buy": dii_buy,

            "dii_sell": dii_sell,

            "updated": datetime.now(),

        }

    # =====================================================
    # NET FLOWS
    # =====================================================

    def institutional_flow(
        self,
    ) -> Dict[str, Any]:
        """
        Calculate FII/DII net flows.
        """

        flow = self.market_context.get(

            "institutional",

            {},

        )

        if not flow:

            return {}

        fii_net = (

            flow["fii_buy"]

            - flow["fii_sell"]

        )

        dii_net = (

            flow["dii_buy"]

            - flow["dii_sell"]

        )

        total = fii_net + dii_net

        return {

            "fii_net": round(

                fii_net,

                2,

            ),

            "dii_net": round(

                dii_net,

                2,

            ),

            "combined": round(

                total,

                2,

            ),

        }

    # =====================================================
    # SMART MONEY SCORE
    # =====================================================

    def smart_money_score(
        self,
    ) -> float:
        """
        Institutional sentiment score.
        """

        flow = self.institutional_flow()

        if not flow:

            return 50.0

        combined = flow["combined"]

        if combined >= 5000:

            return 100.0

        if combined >= 2000:

            return 85.0

        if combined >= 500:

            return 70.0

        if combined >= -500:

            return 50.0

        if combined >= -2000:

            return 30.0

        return 10.0

    # =====================================================
    # DELIVERY PERCENTAGE
    # =====================================================

    def delivery_analysis(
        self,
        dataframe: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        Estimate delivery participation.

        Expects optional 'delivery_volume' column.
        """

        if (

            "delivery_volume"

            not in dataframe.columns

        ):

            return {

                "available": False,

            }

        latest = dataframe.iloc[-1]

        delivery = float(

            latest["delivery_volume"]

        )

        volume = float(

            latest["volume"]

        )

        percentage = (

            (delivery / volume) * 100

            if volume > 0

            else 0

        )

        return {

            "available": True,

            "delivery_volume": delivery,

            "delivery_percent": round(

                percentage,

                2,

            ),

            "institutional": percentage >= 45,

        }

    # =====================================================
    # VOLUME PROFILE SUMMARY
    # =====================================================

    def volume_profile(
        self,
        dataframe: pd.DataFrame,
        lookback: int = 20,
    ) -> Dict[str, Any]:
        """
        Simple rolling volume analysis.
        """

        latest = float(

            dataframe["volume"].iloc[-1]

        )

        average = float(

            dataframe["volume"]

            .tail(

                lookback

            )

            .mean()

        )

        ratio = (

            latest / average

            if average > 0

            else 0

        )

        return {

            "latest": latest,

            "average": round(

                average,

                2,

            ),

            "ratio": round(

                ratio,

                2,

            ),

            "high_volume": ratio >= 1.5,

        }

    # =====================================================
    # INSTITUTIONAL PARTICIPATION
    # =====================================================

    def institutional_participation(
        self,
        dataframe: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        Combined institutional participation.
        """

        volume = self.volume_profile(

            dataframe

        )

        delivery = self.delivery_analysis(

            dataframe

        )

        score = 50.0

        if volume["high_volume"]:

            score += 20

        if delivery.get(

            "institutional",

            False,

        ):

            score += 30

        return {

            "volume": volume,

            "delivery": delivery,

            "score": min(

                score,

                100.0,

            ),

        }

    # =====================================================
    # INSTITUTIONAL FILTER
    # =====================================================

    def institutional_filter(
        self,
        dataframe: pd.DataFrame,
        minimum_score: float = 70.0,
    ) -> bool:
        """
        Scanner filter for institutional activity.
        """

        participation = (

            self.institutional_participation(

                dataframe

            )

        )

        smart_money = (

            self.smart_money_score()

        )

        score = (

            participation["score"]

            + smart_money

        ) / 2

        return score >= minimum_score

    # =====================================================
    # INSTITUTIONAL DASHBOARD
    # =====================================================

    def institutional_dashboard(
        self,
    ) -> Dict[str, Any]:
        """
        Dashboard-ready institutional summary.
        """

        return {

            "flow": self.institutional_flow(),

            "smart_money_score": self.smart_money_score(),

            "updated": datetime.now(),

        }
        # =====================================================
    # MARKET HEALTH SCORE
    # =====================================================

    def market_health_score(
        self,
        index_name: str = "NIFTY",
    ) -> float:
        """
        Calculate the overall market health score.
        """

        dataframe = self.index(
            index_name
        )

        if dataframe is None:

            return 50.0

        trend = self.trend_score(
            dataframe
        )

        volatility = 100 - self.vix_analysis().get(
            "score",
            50,
        )

        breadth = self.market_breadth.get(
            "breadth_score",
            50,
        )

        smart_money = self.smart_money_score()

        health = np.mean(

            [

                trend,

                breadth,

                smart_money,

                volatility,

            ]

        )

        return round(

            float(health),

            2,

        )

    # =====================================================
    # BULL / BEAR PROBABILITY
    # =====================================================

    def bull_bear_probability(
        self,
        index_name: str = "NIFTY",
    ) -> Dict[str, float]:
        """
        Estimate bull/bear probability.
        """

        health = self.market_health_score(
            index_name
        )

        bull = min(

            100.0,

            health,

        )

        bear = max(

            0.0,

            100 - bull,

        )

        return {

            "bull": round(

                bull,

                2,

            ),

            "bear": round(

                bear,

                2,

            ),

        }

    # =====================================================
    # RISK MODE
    # =====================================================

    def risk_mode(
        self,
        index_name: str = "NIFTY",
    ) -> str:
        """
        Detect market risk regime.
        """

        probability = self.bull_bear_probability(
            index_name
        )

        bull = probability["bull"]

        if bull >= 75:

            return "Risk-On"

        if bull >= 55:

            return "Moderately Risk-On"

        if bull >= 40:

            return "Neutral"

        if bull >= 25:

            return "Moderately Risk-Off"

        return "Risk-Off"

    # =====================================================
    # SESSION QUALITY
    # =====================================================

    def session_quality(
        self,
        index_name: str = "NIFTY",
    ) -> str:
        """
        Evaluate trading session quality.
        """

        score = self.market_health_score(
            index_name
        )

        if score >= 85:

            return "Excellent"

        if score >= 70:

            return "Good"

        if score >= 55:

            return "Average"

        if score >= 40:

            return "Weak"

        return "Poor"

    # =====================================================
    # MARKET QUALITY INDEX
    # =====================================================

    def market_quality_index(
        self,
        index_name: str = "NIFTY",
    ) -> Dict[str, Any]:
        """
        Combined market quality metrics.
        """

        return {

            "health": self.market_health_score(
                index_name
            ),

            "risk_mode": self.risk_mode(
                index_name
            ),

            "session_quality": self.session_quality(
                index_name
            ),

            "probability": self.bull_bear_probability(
                index_name
            ),

        }

    # =====================================================
    # MASTER SCANNER FILTER
    # =====================================================

    def scanner_filter(
        self,
        index_name: str = "NIFTY",
        minimum_health: float = 60.0,
    ) -> bool:
        """
        Master filter used before executing scanners.
        """

        quality = self.market_quality_index(
            index_name
        )

        return (

            quality["health"]

            >= minimum_health

        )

    # =====================================================
    # DECISION ENGINE
    # =====================================================

    def trading_decision(
        self,
        index_name: str = "NIFTY",
    ) -> Dict[str, Any]:
        """
        Professional market decision engine.
        """

        quality = self.market_quality_index(
            index_name
        )

        health = quality["health"]

        if health >= 80:

            decision = "Aggressive Buy"

        elif health >= 65:

            decision = "Buy"

        elif health >= 50:

            decision = "Wait"

        elif health >= 35:

            decision = "Sell"

        else:

            decision = "Aggressive Sell"

        return {

            "decision": decision,

            "quality": quality,

        }

    # =====================================================
    # MARKET DASHBOARD
    # =====================================================

    def dashboard(
        self,
        index_name: str = "NIFTY",
    ) -> Dict[str, Any]:
        """
        Dashboard-ready market summary.
        """

        return {

            "score": self.market_health_score(
                index_name
            ),

            "quality": self.market_quality_index(
                index_name
            ),

            "institutional": self.institutional_dashboard(),

            "breadth": self.breadth_summary(),

            "sectors": self.sector_summary(),

            "decision": self.trading_decision(
                index_name
            ),

            "updated": datetime.now(),

        }
        # =====================================================
    # TREND CHANGE ALERT
    # =====================================================

    def trend_change_alert(
        self,
        index_name: str = "NIFTY",
    ) -> Optional[Dict[str, Any]]:
        """
        Detect market trend changes.
        """

        dataframe = self.index(
            index_name
        )

        if dataframe is None or dataframe.empty:

            return None

        trend = self.ema_trend(
            dataframe
        )

        if trend["bullish_alignment"]:

            return {

                "type": "Trend",

                "severity": "High",

                "message": (
                    f"{index_name} entered a "
                    "strong bullish alignment."
                ),

                "timestamp": datetime.now(),

            }

        if trend["bearish_alignment"]:

            return {

                "type": "Trend",

                "severity": "High",

                "message": (
                    f"{index_name} entered a "
                    "strong bearish alignment."
                ),

                "timestamp": datetime.now(),

            }

        return None

    # =====================================================
    # VOLATILITY ALERT
    # =====================================================

    def volatility_alert(
        self,
    ) -> Optional[Dict[str, Any]]:
        """
        Alert based on India VIX.
        """

        vix = self.vix_analysis()

        if not vix:

            return None

        if vix["regime"] in (

            "High",

            "Extreme",

        ):

            return {

                "type": "Volatility",

                "severity": "Medium",

                "message": (

                    f"India VIX is "

                    f"{vix['regime']} "

                    f"({vix['vix']:.2f})"

                ),

                "timestamp": datetime.now(),

            }

        return None

    # =====================================================
    # BREADTH ALERT
    # =====================================================

    def breadth_alert(
        self,
    ) -> Optional[Dict[str, Any]]:
        """
        Alert when market breadth becomes extreme.
        """

        score = self.market_breadth.get(

            "breadth_score",

            50,

        )

        if score >= 80:

            return {

                "type": "Breadth",

                "severity": "Medium",

                "message": (

                    "Strong market breadth "

                    "detected."

                ),

                "timestamp": datetime.now(),

            }

        if score <= 20:

            return {

                "type": "Breadth",

                "severity": "Medium",

                "message": (

                    "Weak market breadth "

                    "detected."

                ),

                "timestamp": datetime.now(),

            }

        return None

    # =====================================================
    # SECTOR ROTATION ALERT
    # =====================================================

    def sector_rotation_alert(
        self,
    ) -> Optional[Dict[str, Any]]:
        """
        Notify when sector leadership is strong.
        """

        leaders = self.leading_sectors(

            top=1,

        )

        if not leaders:

            return None

        leader = leaders[0]

        if leader["relative_strength"] < 2:

            return None

        return {

            "type": "Sector",

            "severity": "Low",

            "message": (

                f"Sector leader: "

                f"{leader['sector']} "

                f"({leader['relative_strength']}%)"

            ),

            "timestamp": datetime.now(),

        }

    # =====================================================
    # INSTITUTIONAL FLOW ALERT
    # =====================================================

    def institutional_alert(
        self,
    ) -> Optional[Dict[str, Any]]:
        """
        Alert based on smart money.
        """

        score = self.smart_money_score()

        if score >= 85:

            return {

                "type": "Institutional",

                "severity": "High",

                "message": (

                    "Strong institutional "

                    "buying detected."

                ),

                "timestamp": datetime.now(),

            }

        if score <= 20:

            return {

                "type": "Institutional",

                "severity": "High",

                "message": (

                    "Heavy institutional "

                    "selling detected."

                ),

                "timestamp": datetime.now(),

            }

        return None

    # =====================================================
    # MARKET EVENTS
    # =====================================================

    def market_events(
        self,
        index_name: str = "NIFTY",
    ) -> List[Dict[str, Any]]:
        """
        Collect active market events.
        """

        events: List[

            Dict[str, Any]

        ] = []

        for alert in (

            self.trend_change_alert(

                index_name,

            ),

            self.volatility_alert(),

            self.breadth_alert(),

            self.sector_rotation_alert(),

            self.institutional_alert(),

        ):

            if alert:

                events.append(

                    alert

                )

        return events

    # =====================================================
    # SCANNER NOTIFICATIONS
    # =====================================================

    def scanner_notifications(
        self,
        index_name: str = "NIFTY",
    ) -> Dict[str, Any]:
        """
        Notification package for scanners.
        """

        return {

            "market_health": (

                self.market_health_score(

                    index_name,

                )

            ),

            "decision": (

                self.trading_decision(

                    index_name,

                )["decision"]

            ),

            "alerts": self.market_events(

                index_name,

            ),

            "generated": datetime.now(),

        }

    # =====================================================
    # HAS CRITICAL ALERTS
    # =====================================================

    def has_critical_alerts(
        self,
        index_name: str = "NIFTY",
    ) -> bool:
        """
        Check for High severity alerts.
        """

        for event in self.market_events(

            index_name,

        ):

            if event["severity"] == "High":

                return True

        return False
        # =====================================================
    # CACHE
    # =====================================================

    def clear_cache(
        self,
    ) -> None:
        """
        Clear runtime caches.
        """

        with self.lock:

            self.market_context.clear()

            self.market_breadth.clear()

            self.market_score = MarketScore()

            self.cache_hits = 0

            self.cache_misses = 0

    # =====================================================
    # RESET
    # =====================================================

    def reset_statistics(
        self,
    ) -> None:
        """
        Reset runtime statistics.
        """

        self.requests = 0

        self.cache_hits = 0

        self.cache_misses = 0

        self.started = datetime.now()

    # =====================================================
    # PERFORMANCE
    # =====================================================

    def performance(
        self,
    ) -> Dict[str, Any]:
        """
        Runtime performance metrics.
        """

        uptime = (

            datetime.now()

            - self.started

        ).total_seconds()

        total = (

            self.cache_hits

            + self.cache_misses

        )

        hit_rate = 0.0

        if total > 0:

            hit_rate = (

                self.cache_hits

                / total

            ) * 100

        return {

            "uptime_seconds": round(

                uptime,

                2,

            ),

            "requests": self.requests,

            "cache_hits": self.cache_hits,

            "cache_misses": self.cache_misses,

            "cache_hit_rate": round(

                hit_rate,

                2,

            ),

        }

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(
        self,
    ) -> Dict[str, Any]:
        """
        Verify MarketAnalyzer health.
        """

        return {

            "healthy": True,

            "registered_indices": len(

                self.index_data

            ),

            "registered_sectors": len(

                self.sector_data

            ),

            "breadth_available": bool(

                self.market_breadth

            ),

            "last_update": self.last_update,

        }

    # =====================================================
    # METADATA
    # =====================================================

    def metadata(
        self,
    ) -> Dict[str, Any]:
        """
        Component metadata.
        """

        return {

            "component": self.__class__.__name__,

            "version": self.VERSION,

            "started": self.started.isoformat(),

            "indices": len(

                self.index_data

            ),

            "sectors": len(

                self.sector_data

            ),

        }

    # =====================================================
    # DIAGNOSTICS
    # =====================================================

    def diagnostics(
        self,
    ) -> Dict[str, Any]:
        """
        Complete diagnostic report.
        """

        return {

            "metadata": self.metadata(),

            "health": self.health_check(),

            "performance": self.performance(),

            "market_health": self.market_health_score(),

            "smart_money": self.smart_money_score(),

        }

    # =====================================================
    # RUNTIME REPORT
    # =====================================================

    def runtime_report(
        self,
    ) -> Dict[str, Any]:
        """
        Comprehensive runtime report.
        """

        return {

            "metadata": self.metadata(),

            "diagnostics": self.diagnostics(),

            "dashboard": self.dashboard(),

            "institutional": (

                self.institutional_dashboard()

            ),

            "alerts": self.market_events(),

        }

    # =====================================================
    # UPDATE CACHE
    # =====================================================

    def update_cache(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store runtime information.
        """

        with self.lock:

            self.market_context[

                key

            ] = value

    # =====================================================
    # GET CACHE
    # =====================================================

    def cache(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve cached value.
        """

        if key in self.market_context:

            self.cache_hits += 1

            return self.market_context[

                key

            ]

        self.cache_misses += 1

        return default

    # =====================================================
    # REMOVE CACHE
    # =====================================================

    def remove_cache(
        self,
        key: str,
    ) -> None:
        """
        Remove cached item.
        """

        self.market_context.pop(

            key,

            None,

        )

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh(
        self,
    ) -> None:
        """
        Refresh analyzer state.
        """

        self.last_update = datetime.now()

        self.market_context[

            "dashboard"

        ] = self.dashboard()
            # =====================================================
    # SYMBOL COUNTS
    # =====================================================

    @property
    def index_count(
        self,
    ) -> int:
        """
        Number of registered indices.
        """

        return len(

            self.index_data

        )

    @property
    def sector_count(
        self,
    ) -> int:
        """
        Number of registered sectors.
        """

        return len(

            self.sector_data

        )

    # =====================================================
    # LIST HELPERS
    # =====================================================

    def indices(
        self,
    ) -> List[str]:
        """
        Return registered indices.
        """

        return sorted(

            self.index_data.keys()

        )

    def sectors(
        self,
    ) -> List[str]:
        """
        Return registered sectors.
        """

        return sorted(

            self.sector_data.keys()

        )

    # =====================================================
    # FACTORY
    # =====================================================

    @classmethod
    def create(
        cls,
        client: UpstoxClient,
        data_manager: DataManager,
        indicators: Optional[
            IndicatorEngine
        ] = None,
    ) -> "MarketAnalyzer":
        """
        Factory constructor.
        """

        return cls(

            client=client,

            data_manager=data_manager,

            indicators=indicators,

        )

    # =====================================================
    # CONTEXT MANAGER
    # =====================================================

    def __enter__(
        self,
    ) -> "MarketAnalyzer":
        """
        Context manager entry.
        """

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> bool:
        """
        Context manager exit.
        """

        self.shutdown()

        return False

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(
        self,
    ) -> None:
        """
        Gracefully shut down analyzer.
        """

        self.logger.info(

            "Shutting down MarketAnalyzer."

        )

        self.clear_cache()

    # =====================================================
    # MAGIC METHODS
    # =====================================================

    def __len__(
        self,
    ) -> int:
        """
        Total registered datasets.
        """

        return (

            self.index_count

            + self.sector_count

        )

    def __contains__(
        self,
        name: str,
    ) -> bool:
        """
        Check whether an index or sector exists.
        """

        return (

            name in self.index_data

            or name in self.sector_data

        )

    def __getitem__(
        self,
        name: str,
    ) -> Optional[pd.DataFrame]:
        """
        Dictionary-style access.
        """

        if name in self.index_data:

            return self.index_data[

                name

            ]

        return self.sector_data.get(

            name

        )

    def __iter__(
        self,
    ):
        """
        Iterate over all registered indices.
        """

        return iter(

            self.index_data.items()

        )

    # =====================================================
    # STRING REPRESENTATIONS
    # =====================================================

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (

            f"{self.__class__.__name__}("

            f"indices={self.index_count}, "

            f"sectors={self.sector_count}, "

            f"requests={self.requests})"

        )

    def __str__(
        self,
    ) -> str:
        """
        User-friendly representation.
        """

        return (

            f"{self.__class__.__name__}"

            f" | Indices: {self.index_count}"

            f" | Sectors: {self.sector_count}"

            f" | Version: {self.VERSION}"

        )

    # =====================================================
    # DEBUG SUMMARY
    # =====================================================

    def print_summary(
        self,
    ) -> None:
        """
        Print runtime summary.
        """

        self.logger.info(

            "========== MarketAnalyzer =========="

        )

        self.logger.info(

            "Indices        : %s",

            self.index_count,

        )

        self.logger.info(

            "Sectors        : %s",

            self.sector_count,

        )

        self.logger.info(

            "Health Score   : %.2f",

            self.market_health_score(),

        )

        self.logger.info(

            "Smart Money    : %.2f",

            self.smart_money_score(),

        )

        self.logger.info(

            "Cache Hits     : %s",

            self.cache_hits,

        )

        self.logger.info(

            "Cache Misses   : %s",

            self.cache_misses,

        )

        self.logger.info(

            "===================================="

        )

    # =====================================================
    # DUMP STATE
    # =====================================================

    def dump_state(
        self,
    ) -> Dict[str, Any]:
        """
        Lightweight state dump for debugging.
        """

        return {

            "indices": self.indices(),

            "sectors": self.sectors(),

            "market_health": self.market_health_score(),

            "smart_money": self.smart_money_score(),

            "performance": self.performance(),

            "last_update": self.last_update,

        }
        # =====================================================
    # READY
    # =====================================================

    @property
    def ready(
        self,
    ) -> bool:
        """
        Analyzer readiness.
        """

        return (

            self.index_count > 0

            and self.sector_count > 0

        )

    # =====================================================
    # STATUS
    # =====================================================

    @property
    def status(
        self,
    ) -> Dict[str, Any]:
        """
        Current analyzer status.
        """

        return {

            "ready": self.ready,

            "indices": self.index_count,

            "sectors": self.sector_count,

            "market_health": self.market_health_score(),

            "smart_money_score": self.smart_money_score(),

            "requests": self.requests,

            "cache_hits": self.cache_hits,

            "cache_misses": self.cache_misses,

            "last_update": self.last_update,

        }

    # =====================================================
    # VERSION
    # =====================================================

    @classmethod
    def version(
        cls,
    ) -> str:
        """
        Return component version.
        """

        return cls.VERSION

    # =====================================================
    # BUILD REPORT
    # =====================================================

    @classmethod
    def build_report(
        cls,
    ) -> Dict[str, str]:
        """
        Static component information.
        """

        return {

            "component": cls.__name__,

            "version": cls.VERSION,

            "status": "Production",

            "thread_safe": "Yes",

            "market_analysis": "Enabled",

            "sector_rotation": "Enabled",

            "breadth_analysis": "Enabled",

            "institutional_analysis": "Enabled",

            "alert_engine": "Enabled",

            "dashboard": "Supported",

            "scanner_ready": "Yes",

        }

    # =====================================================
    # EXPORT STATE
    # =====================================================

    def export_state(
        self,
    ) -> Dict[str, Any]:
        """
        Export runtime state.
        """

        return {

            "metadata": self.metadata(),

            "status": self.status,

            "market_score": vars(

                self.market_score

            ),

            "breadth": self.market_breadth,

            "context": self.market_context,

            "performance": self.performance(),

        }

    # =====================================================
    # CLOSE
    # =====================================================

    def close(
        self,
    ) -> None:
        """
        Compatibility wrapper.
        """

        self.shutdown()

    # =====================================================
    # DESTROY
    # =====================================================

    def destroy(
        self,
    ) -> None:
        """
        Release analyzer resources.
        """

        self.logger.info(

            "Destroying MarketAnalyzer."

        )

        self.clear_cache()

        self.index_data.clear()

        self.sector_data.clear()

    # =====================================================
    # FINALIZE
    # =====================================================

    def finalize(
        self,
    ) -> None:
        """
        Final cleanup before application exit.
        """

        self.logger.info(

            "Finalizing MarketAnalyzer."

        )

        self.destroy()

    # =====================================================
    # COPY
    # =====================================================

    def copy(
        self,
    ) -> "MarketAnalyzer":
        """
        Create a fresh analyzer using the same
        dependencies.
        """

        analyzer = self.__class__(

            client=self.client,

            data_manager=self.data,

            indicators=self.indicators,

        )

        analyzer.index_data = {

            k: v.copy()

            for k, v in self.index_data.items()

        }

        analyzer.sector_data = {

            k: v.copy()

            for k, v in self.sector_data.items()

        }

        analyzer.market_context = dict(

            self.market_context

        )

        analyzer.market_breadth = dict(

            self.market_breadth

        )

        analyzer.market_score = MarketScore(

            **vars(self.market_score)

        )

        analyzer.last_update = self.last_update

        return analyzer


# ==========================
# END OF FILE
# ==========================