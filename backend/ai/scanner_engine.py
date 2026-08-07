"""
==========================================================
StockVersity Scanner Pro v4.0
Master AI Scanner Engine
Powered by AI
==========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd


# ==========================================================
# IMPORT AI ENGINES
# ==========================================================

from backend.ai.market_regime_engine import MarketRegimeEngine
from backend.ai.market_sentiment_engine import MarketSentimentEngine
from backend.ai.market_prediction_engine import MarketPredictionEngine
from backend.ai.market_structure_engine import MarketStructureEngine
from backend.ai.volume_analysis_engine import VolumeAnalysisEngine
from backend.ai.liquidity_engine import LiquidityEngine
from backend.ai.risk_management_engine import RiskManagementEngine
from backend.ai.sector_rotation_engine import SectorRotationEngine
from backend.ai.pattern_recognition_engine import PatternRecognitionEngine
from backend.ai.opportunity_ranker import OpportunityRanker
from backend.ai.trading_decision_engine import TradingDecisionEngine


# ==========================================================
# RESULT OBJECT
# ==========================================================

@dataclass
class ScannerResult:

    symbol: str

    score: float

    signal: str

    confidence: float

    category: str

    timeframe: str

    recommendation: str

    risk_reward: float

    sector: str

    priority: int

    engines: Dict = field(default_factory=dict)

    metrics: Dict = field(default_factory=dict)

    timestamp: datetime = field(
        default_factory=datetime.now
    )


# ==========================================================
# MASTER AI SCANNER
# ==========================================================

class ScannerEngine:

    VERSION = "4.0"

    def __init__(

        self,

        symbol: str,

        dataframe: pd.DataFrame,

        sector: str = "Unknown",

    ):

        self.symbol = symbol

        self.data = dataframe.copy()

        self.sector = sector

        self.result: Optional[ScannerResult] = None

        self.engines = {}

        self.initialize_engines()


# ==========================================================
# INITIALIZE AI ENGINES
# ==========================================================

    def initialize_engines(

        self,

    ) -> None:

        self.engines = {

            "market_regime":

                MarketRegimeEngine(

                    self.symbol,

                    self.data,

                ),

            "market_sentiment":

                MarketSentimentEngine(

                    self.symbol,

                    self.data,

                ),

            "prediction":

                MarketPredictionEngine(

                    self.symbol,

                    self.data,

                ),

            "market_structure":

                MarketStructureEngine(

                    self.symbol,

                    self.data,

                ),

            "volume":

                VolumeAnalysisEngine(

                    self.symbol,

                    self.data,

                ),

            "liquidity":

                LiquidityEngine(

                    self.symbol,

                    self.data,

                ),

            "risk":

                RiskManagementEngine(

                    self.symbol,

                    self.data,

                ),

            "sector":

                SectorRotationEngine(

                    self.symbol,

                    self.data,

                ),

            "patterns":

                PatternRecognitionEngine(

                    self.symbol,

                    self.data,

                ),

        }


# ==========================================================
# VALIDATION
# ==========================================================

    def validate(

        self,

    ) -> bool:

        required = [

            "Open",

            "High",

            "Low",

            "Close",

            "Volume",

        ]

        return (

            self.data is not None

            and

            not self.data.empty

            and

            all(

                column in self.data.columns

                for column in required

            )

        )


# ==========================================================
# RESET
# ==========================================================

    def reset(

        self,

    ) -> None:

        self.result = None


# ==========================================================
# LAST PRICE
# ==========================================================

    def last_price(

        self,

    ) -> float:

        return float(

            self.data["Close"].iloc[-1]

        )


# ==========================================================
# LAST VOLUME
# ==========================================================

    def last_volume(

        self,

    ) -> float:

        return float(

            self.data["Volume"].iloc[-1]

        )


# ==========================================================
# AVERAGE VOLUME
# ==========================================================

    def average_volume(

        self,

        period: int = 20,

    ) -> float:

        return float(

            self.data["Volume"]

            .tail(period)

            .mean()

        )


# ==========================================================
# RELATIVE VOLUME
# ==========================================================

    def relative_volume(

        self,

    ) -> float:

        average = self.average_volume()

        if average == 0:

            return 0.0

        return round(

            self.last_volume()

            /

            average,

            2,

        )
    # ==========================================================
# MARKET REGIME SCORE
# ==========================================================

    def market_regime_score(

        self,

    ) -> float:

        engine = self.engines["market_regime"]

        result = engine.run()

        return float(

            result["dashboard"]["Score"]

        )


# ==========================================================
# MARKET SENTIMENT SCORE
# ==========================================================

    def market_sentiment_score(

        self,

    ) -> float:

        engine = self.engines["market_sentiment"]

        result = engine.run()

        return float(

            result["dashboard"]["Sentiment Score"]

        )


# ==========================================================
# MARKET STRUCTURE SCORE
# ==========================================================

    def market_structure_score(

        self,

    ) -> float:

        engine = self.engines["market_structure"]

        result = engine.run()

        return float(

            result["dashboard"]["Priority Score"]

        )


# ==========================================================
# LIQUIDITY SCORE
# ==========================================================

    def liquidity_score(

        self,

    ) -> float:

        engine = self.engines["liquidity"]

        result = engine.run()

        return float(

            result["dashboard"]["Priority Score"]

        )


# ==========================================================
# VOLUME SCORE
# ==========================================================

    def volume_score(

        self,

    ) -> float:

        engine = self.engines["volume"]

        result = engine.run()

        return float(

            result["dashboard"]["Priority Score"]

        )


# ==========================================================
# PATTERN SCORE
# ==========================================================

    def pattern_score(

        self,

    ) -> float:

        engine = self.engines["patterns"]

        result = engine.run()

        return float(

            result["dashboard"]["Priority Score"]

        )


# ==========================================================
# RISK SCORE
# ==========================================================

    def risk_score(

        self,

    ) -> float:

        engine = self.engines["risk"]

        result = engine.run()

        return float(

            result["dashboard"]["Priority Score"]

        )


# ==========================================================
# SECTOR SCORE
# ==========================================================

    def sector_score(

        self,

    ) -> float:

        engine = self.engines["sector"]

        result = engine.run()

        return float(

            result["dashboard"]["Priority Score"]

        )


# ==========================================================
# PREDICTION SCORE
# ==========================================================

    def prediction_score(

        self,

    ) -> float:

        engine = self.engines["prediction"]

        result = engine.run()

        return float(

            result["dashboard"]["Prediction Score"]

        )


# ==========================================================
# COMBINED AI SCORE
# ==========================================================

    def combined_ai_score(

        self,

    ) -> float:

        weights = {

            "market_regime": 0.12,

            "market_sentiment": 0.10,

            "market_structure": 0.14,

            "liquidity": 0.12,

            "volume": 0.10,

            "patterns": 0.14,

            "risk": 0.08,

            "sector": 0.08,

            "prediction": 0.12,

        }

        score = (

            self.market_regime_score()

            * weights["market_regime"]

            +

            self.market_sentiment_score()

            * weights["market_sentiment"]

            +

            self.market_structure_score()

            * weights["market_structure"]

            +

            self.liquidity_score()

            * weights["liquidity"]

            +

            self.volume_score()

            * weights["volume"]

            +

            self.pattern_score()

            * weights["patterns"]

            +

            self.risk_score()

            * weights["risk"]

            +

            self.sector_score()

            * weights["sector"]

            +

            self.prediction_score()

            * weights["prediction"]

        )

        return round(

            min(score, 100),

            2,

        )
    # ==========================================================
# BUY SCORE
# ==========================================================

    def buy_score(

        self,

    ) -> float:

        score = self.combined_ai_score()

        if self.trade_direction() == "BUY":

            score += 5

        return round(

            min(score, 100),

            2,

        )


# ==========================================================
# SELL SCORE
# ==========================================================

    def sell_score(

        self,

    ) -> float:

        score = 100 - self.combined_ai_score()

        if self.trade_direction() == "SELL":

            score += 5

        return round(

            min(score, 100),

            2,

        )


# ==========================================================
# HOLD SCORE
# ==========================================================

    def hold_score(

        self,

    ) -> float:

        buy = self.buy_score()

        sell = self.sell_score()

        hold = 100 - abs(

            buy - sell

        )

        return round(

            max(

                min(hold, 100),

                0,

            ),

            2,

        )


# ==========================================================
# TRADE DIRECTION
# ==========================================================

    def trade_direction(

        self,

    ) -> str:

        prediction = self.prediction_score()

        structure = self.market_structure_score()

        regime = self.market_regime_score()

        bullish = sum(

            [

                prediction >= 60,

                structure >= 60,

                regime >= 60,

            ]

        )

        bearish = sum(

            [

                prediction <= 40,

                structure <= 40,

                regime <= 40,

            ]

        )

        if bullish >= 2:

            return "BUY"

        elif bearish >= 2:

            return "SELL"

        else:

            return "HOLD"


# ==========================================================
# CONFIDENCE SCORE
# ==========================================================

    def confidence_score(

        self,

    ) -> float:

        scores = [

            self.market_regime_score(),

            self.market_sentiment_score(),

            self.market_structure_score(),

            self.liquidity_score(),

            self.volume_score(),

            self.pattern_score(),

            self.prediction_score(),

        ]

        confidence = (

            sum(scores)

            /

            len(scores)

        )

        return round(

            confidence,

            2,

        )


# ==========================================================
# RISK / REWARD
# ==========================================================

    def risk_reward_ratio(

        self,

    ) -> float:

        risk = max(

            self.risk_score(),

            1,

        )

        reward = self.prediction_score()

        rr = reward / risk

        return round(

            rr,

            2,

        )


# ==========================================================
# PRIORITY SCORE
# ==========================================================

    def priority_score(

        self,

    ) -> float:

        score = (

            self.combined_ai_score()

            * 0.70

            +

            self.confidence_score()

            * 0.30

        )

        return round(

            min(score, 100),

            2,

        )


# ==========================================================
# MASTER RECOMMENDATION
# ==========================================================

    def recommendation(

        self,

    ) -> str:

        score = self.priority_score()

        direction = self.trade_direction()

        if score >= 90:

            return f"Strong {direction}"

        elif score >= 80:

            return direction

        elif score >= 65:

            return "Watch"

        else:

            return "Avoid"


# ==========================================================
# AI SIGNAL CLASSIFICATION
# ==========================================================

    def signal(

        self,

    ) -> str:

        direction = self.trade_direction()

        confidence = self.confidence_score()

        if direction == "BUY":

            if confidence >= 85:

                return "A+"

            elif confidence >= 75:

                return "A"

            elif confidence >= 65:

                return "B"

            else:

                return "C"

        elif direction == "SELL":

            if confidence >= 85:

                return "Strong Sell"

            elif confidence >= 70:

                return "Sell"

            else:

                return "Weak Sell"

        return "Neutral"


# ==========================================================
# INSTITUTIONAL CONFIRMATION
# ==========================================================

    def institutional_confirmation(

        self,

    ) -> Dict:

        liquidity = self.liquidity_score()

        volume = self.volume_score()

        structure = self.market_structure_score()

        confirmed = (

            liquidity >= 70

            and

            volume >= 70

            and

            structure >= 70

        )

        return {

            "confirmed":

                confirmed,

            "liquidity":

                liquidity,

            "volume":

                volume,

            "structure":

                structure,

        }
    # ==========================================================
# INTRADAY CLASSIFICATION
# ==========================================================

    def intraday_score(

        self,

    ) -> float:

        score = (

            self.volume_score() * 0.30 +

            self.liquidity_score() * 0.25 +

            self.market_structure_score() * 0.20 +

            self.pattern_score() * 0.15 +

            self.market_sentiment_score() * 0.10

        )

        return round(

            min(score, 100),

            2,

        )


# ==========================================================
# SWING CLASSIFICATION
# ==========================================================

    def swing_score(

        self,

    ) -> float:

        score = (

            self.market_regime_score() * 0.25 +

            self.pattern_score() * 0.25 +

            self.prediction_score() * 0.20 +

            self.liquidity_score() * 0.15 +

            self.sector_score() * 0.15

        )

        return round(

            min(score, 100),

            2,

        )


# ==========================================================
# POSITIONAL CLASSIFICATION
# ==========================================================

    def positional_score(

        self,

    ) -> float:

        score = (

            self.market_regime_score() * 0.30 +

            self.prediction_score() * 0.25 +

            self.sector_score() * 0.20 +

            self.market_structure_score() * 0.15 +

            self.risk_score() * 0.10

        )

        return round(

            min(score, 100),

            2,

        )


# ==========================================================
# ENTRY QUALITY
# ==========================================================

    def entry_quality(

        self,

    ) -> float:

        score = (

            self.pattern_score() * 0.40 +

            self.volume_score() * 0.30 +

            self.liquidity_score() * 0.30

        )

        return round(

            min(score, 100),

            2,

        )


# ==========================================================
# EXIT QUALITY
# ==========================================================

    def exit_quality(

        self,

    ) -> float:

        score = (

            self.prediction_score() * 0.50 +

            self.market_structure_score() * 0.30 +

            self.risk_score() * 0.20

        )

        return round(

            min(score, 100),

            2,

        )


# ==========================================================
# TRADE TIMING SCORE
# ==========================================================

    def trade_timing_score(

        self,

    ) -> float:

        score = (

            self.entry_quality() * 0.60 +

            self.market_sentiment_score() * 0.20 +

            self.market_regime_score() * 0.20

        )

        return round(

            min(score, 100),

            2,

        )


# ==========================================================
# TREND STRENGTH
# ==========================================================

    def trend_strength(

        self,

    ) -> Dict:

        score = (

            self.market_regime_score() * 0.40 +

            self.market_structure_score() * 0.30 +

            self.prediction_score() * 0.30

        )

        if score >= 85:

            trend = "Very Strong"

        elif score >= 70:

            trend = "Strong"

        elif score >= 55:

            trend = "Moderate"

        elif score >= 40:

            trend = "Weak"

        else:

            trend = "Very Weak"

        return {

            "score": round(score, 2),

            "trend": trend,

        }


# ==========================================================
# AI OPPORTUNITY SCORE
# ==========================================================

    def opportunity_score(

        self,

    ) -> float:

        score = (

            self.priority_score() * 0.50 +

            self.entry_quality() * 0.20 +

            self.trade_timing_score() * 0.20 +

            self.confidence_score() * 0.10

        )

        return round(

            min(score, 100),

            2,

        )


# ==========================================================
# SMART RANK
# ==========================================================

    def smart_rank(

        self,

    ) -> str:

        score = self.opportunity_score()

        if score >= 95:

            return "Elite"

        elif score >= 90:

            return "Diamond"

        elif score >= 80:

            return "Platinum"

        elif score >= 70:

            return "Gold"

        elif score >= 60:

            return "Silver"

        elif score >= 50:

            return "Bronze"

        return "Watchlist"


# ==========================================================
# FINAL TRADE CATEGORY
# ==========================================================

    def trade_category(

        self,

    ) -> Dict:

        intraday = self.intraday_score()

        swing = self.swing_score()

        positional = self.positional_score()

        scores = {

            "Intraday": intraday,

            "Swing": swing,

            "Positional": positional,

        }

        category = max(

            scores,

            key=scores.get,

        )

        return {

            "category": category,

            "score": round(

                scores[category],

                2,

            ),

            "all_scores": scores,

            "smart_rank": self.smart_rank(),

            "opportunity_score": self.opportunity_score(),

        }
    # ==========================================================
# AI SCANNER SUMMARY
# ==========================================================

    def scanner_summary(

        self,

    ) -> Dict:

        category = self.trade_category()

        trend = self.trend_strength()

        return {

            "Symbol":

                self.symbol,

            "Price":

                round(

                    self.last_price(),

                    2,

                ),

            "Priority Score":

                self.priority_score(),

            "Opportunity Score":

                self.opportunity_score(),

            "Signal":

                self.signal(),

            "Direction":

                self.trade_direction(),

            "Category":

                category["category"],

            "Trend":

                trend["trend"],

            "Confidence":

                self.confidence_score(),

        }


# ==========================================================
# DASHBOARD
# ==========================================================

    def dashboard(

        self,

    ) -> Dict:

        return {

            "summary":

                self.scanner_summary(),

            "market_regime":

                self.market_regime_score(),

            "market_sentiment":

                self.market_sentiment_score(),

            "market_structure":

                self.market_structure_score(),

            "volume":

                self.volume_score(),

            "liquidity":

                self.liquidity_score(),

            "pattern":

                self.pattern_score(),

            "prediction":

                self.prediction_score(),

            "risk":

                self.risk_score(),

            "sector":

                self.sector_score(),

        }


# ==========================================================
# WATCHLIST ENTRY
# ==========================================================

    def watchlist_entry(

        self,

    ) -> Dict:

        category = self.trade_category()

        return {

            "Symbol":

                self.symbol,

            "Price":

                self.last_price(),

            "Score":

                self.priority_score(),

            "Rank":

                category["smart_rank"],

            "Category":

                category["category"],

            "Signal":

                self.signal(),

            "Recommendation":

                self.recommendation(),

        }


# ==========================================================
# BUILD SCANNER RESULT
# ==========================================================

    def build_result(

        self,

    ) -> ScannerResult:

        category = self.trade_category()

        self.result = ScannerResult(

            symbol=self.symbol,

            score=self.priority_score(),

            signal=self.signal(),

            confidence=self.confidence_score(),

            category=category["category"],

            timeframe=category["category"],

            recommendation=self.recommendation(),

            risk_reward=self.risk_reward_ratio(),

            sector=self.sector,

            priority=int(

                round(

                    self.priority_score()

                )

            ),

            engines={

                "Market Regime":

                    self.market_regime_score(),

                "Market Sentiment":

                    self.market_sentiment_score(),

                "Market Structure":

                    self.market_structure_score(),

                "Volume":

                    self.volume_score(),

                "Liquidity":

                    self.liquidity_score(),

                "Pattern":

                    self.pattern_score(),

                "Prediction":

                    self.prediction_score(),

                "Risk":

                    self.risk_score(),

                "Sector":

                    self.sector_score(),

            },

            metrics={

                "Opportunity":

                    self.opportunity_score(),

                "Entry":

                    self.entry_quality(),

                "Exit":

                    self.exit_quality(),

                "Timing":

                    self.trade_timing_score(),

                "Trend":

                    self.trend_strength()["score"],

            },

        )

        return self.result


# ==========================================================
# OPPORTUNITY RANK
# ==========================================================

    def opportunity_rank(

        self,

    ) -> Dict:

        category = self.trade_category()

        return {

            "Symbol":

                self.symbol,

            "Priority":

                self.priority_score(),

            "Opportunity":

                self.opportunity_score(),

            "Rank":

                category["smart_rank"],

            "Signal":

                self.signal(),

        }


# ==========================================================
# TRADING DECISION
# ==========================================================

    def trading_decision(

        self,

    ) -> Dict:

        decision_engine = TradingDecisionEngine(

            self.symbol,

            self.data,

        )

        return decision_engine.run()


# ==========================================================
# TOP PICK SCORE
# ==========================================================

    def top_pick_score(

        self,

    ) -> float:

        score = (

            self.priority_score() * 0.50 +

            self.opportunity_score() * 0.30 +

            self.confidence_score() * 0.20

        )

        return round(

            min(score, 100),

            2,

        )


# ==========================================================
# PROFESSIONAL RECOMMENDATION
# ==========================================================

    def professional_recommendation(

        self,

    ) -> Dict:

        category = self.trade_category()

        confirmation = (

            self.institutional_confirmation()

        )

        return {

            "recommendation":

                self.recommendation(),

            "signal":

                self.signal(),

            "direction":

                self.trade_direction(),

            "category":

                category["category"],

            "confidence":

                self.confidence_score(),

            "top_pick_score":

                self.top_pick_score(),

            "institutional_confirmation":

                confirmation["confirmed"],

        }


# ==========================================================
# SCANNER OUTPUT
# ==========================================================

    def scanner_output(

        self,

    ) -> Dict:

        if self.result is None:

            self.build_result()

        return {

            "result":

                self.result,

            "summary":

                self.scanner_summary(),

            "dashboard":

                self.dashboard(),

            "watchlist":

                self.watchlist_entry(),

            "recommendation":

                self.professional_recommendation(),

            "decision":

                self.trading_decision(),

        }
    # ==========================================================
# BATCH SCANNER
# ==========================================================

    @staticmethod
    def batch_scan(

        scanners: List["ScannerEngine"],

    ) -> pd.DataFrame:

        rows = []

        for scanner in scanners:

            try:

                rows.append(

                    scanner.watchlist_entry()

                )

            except Exception:

                continue

        dataframe = pd.DataFrame(

            rows

        )

        if dataframe.empty:

            return dataframe

        dataframe = dataframe.sort_values(

            by="Score",

            ascending=False,

        ).reset_index(

            drop=True,

        )

        dataframe["Rank"] = (

            dataframe.index + 1

        )

        return dataframe


# ==========================================================
# NSE UNIVERSE SCANNER
# ==========================================================

    @staticmethod
    def scan_universe(

        scanners: List["ScannerEngine"],

    ) -> List[Dict]:

        output = []

        for scanner in scanners:

            try:

                output.append(

                    scanner.scanner_summary()

                )

            except Exception:

                continue

        return sorted(

            output,

            key=lambda x:

            x["Priority Score"],

            reverse=True,

        )


# ==========================================================
# TOP INTRADAY PICKS
# ==========================================================

    @staticmethod
    def top_intraday(

        scanners: List["ScannerEngine"],

        limit: int = 5,

    ) -> List[Dict]:

        candidates = []

        for scanner in scanners:

            category = scanner.trade_category()

            if category["category"] == "Intraday":

                candidates.append(

                    {

                        "Symbol":

                            scanner.symbol,

                        "Score":

                            scanner.intraday_score(),

                        "Signal":

                            scanner.signal(),

                        "Recommendation":

                            scanner.recommendation(),

                    }

                )

        candidates.sort(

            key=lambda x:

            x["Score"],

            reverse=True,

        )

        return candidates[:limit]


# ==========================================================
# TOP SWING PICKS
# ==========================================================

    @staticmethod
    def top_swing(

        scanners: List["ScannerEngine"],

        limit: int = 5,

    ) -> List[Dict]:

        candidates = []

        for scanner in scanners:

            category = scanner.trade_category()

            if category["category"] == "Swing":

                candidates.append(

                    {

                        "Symbol":

                            scanner.symbol,

                        "Score":

                            scanner.swing_score(),

                        "Signal":

                            scanner.signal(),

                        "Recommendation":

                            scanner.recommendation(),

                    }

                )

        candidates.sort(

            key=lambda x:

            x["Score"],

            reverse=True,

        )

        return candidates[:limit]


# ==========================================================
# TOP POSITIONAL PICKS
# ==========================================================

    @staticmethod
    def top_positional(

        scanners: List["ScannerEngine"],

        limit: int = 5,

    ) -> List[Dict]:

        candidates = []

        for scanner in scanners:

            category = scanner.trade_category()

            if category["category"] == "Positional":

                candidates.append(

                    {

                        "Symbol":

                            scanner.symbol,

                        "Score":

                            scanner.positional_score(),

                        "Signal":

                            scanner.signal(),

                        "Recommendation":

                            scanner.recommendation(),

                    }

                )

        candidates.sort(

            key=lambda x:

            x["Score"],

            reverse=True,

        )

        return candidates[:limit]


# ==========================================================
# SECTOR RANKING
# ==========================================================

    @staticmethod
    def sector_ranking(

        scanners: List["ScannerEngine"],

    ) -> pd.DataFrame:

        sector_scores = {}

        for scanner in scanners:

            score = scanner.priority_score()

            sector_scores.setdefault(

                scanner.sector,

                [],

            ).append(

                score

            )

        rows = []

        for sector, scores in sector_scores.items():

            rows.append(

                {

                    "Sector":

                        sector,

                    "Average Score":

                        round(

                            sum(scores)

                            /

                            len(scores),

                            2,

                        ),

                    "Stocks":

                        len(scores),

                }

            )

        dataframe = pd.DataFrame(

            rows

        )

        if not dataframe.empty:

            dataframe = dataframe.sort_values(

                by="Average Score",

                ascending=False,

            ).reset_index(

                drop=True,

            )

        return dataframe


# ==========================================================
# AI SORTING ENGINE
# ==========================================================

    @staticmethod
    def ai_sort(

        dataframe: pd.DataFrame,

    ) -> pd.DataFrame:

        if dataframe.empty:

            return dataframe

        return dataframe.sort_values(

            by=[

                "Score",

                "Signal",

            ],

            ascending=[

                False,

                False,

            ],

        ).reset_index(

            drop=True,

        )


# ==========================================================
# BEST 5 STOCKS
# ==========================================================

    @staticmethod
    def best_five(

        scanners: List["ScannerEngine"],

    ) -> pd.DataFrame:

        dataframe = ScannerEngine.batch_scan(

            scanners

        )

        if dataframe.empty:

            return dataframe

        return dataframe.head(

            5

        )


# ==========================================================
# SCORE NORMALIZATION
# ==========================================================

    @staticmethod
    def normalize_scores(

        dataframe: pd.DataFrame,

    ) -> pd.DataFrame:

        if dataframe.empty:

            return dataframe

        maximum = dataframe["Score"].max()

        minimum = dataframe["Score"].min()

        if maximum == minimum:

            dataframe["Normalized Score"] = 100

            return dataframe

        dataframe["Normalized Score"] = (

            (

                dataframe["Score"]

                -

                minimum

            )

            /

            (

                maximum

                -

                minimum

            )

            * 100

        ).round(

            2

        )

        return dataframe


# ==========================================================
# PORTFOLIO WATCHLIST
# ==========================================================

    @staticmethod
    def portfolio_watchlist(

        scanners: List["ScannerEngine"],

        minimum_score: float = 75,

    ) -> pd.DataFrame:

        dataframe = ScannerEngine.batch_scan(

            scanners

        )

        if dataframe.empty:

            return dataframe

        dataframe = dataframe[

            dataframe["Score"]

            >=

            minimum_score

        ]

        return dataframe.reset_index(

            drop=True,

        )
    # ==========================================================
# LIVE SCANNER DASHBOARD
# ==========================================================

    def live_dashboard(

        self,

    ) -> Dict:

        category = self.trade_category()

        trend = self.trend_strength()

        recommendation = self.professional_recommendation()

        return {

            "Symbol":

                self.symbol,

            "Last Price":

                round(

                    self.last_price(),

                    2,

                ),

            "Priority Score":

                self.priority_score(),

            "Opportunity Score":

                self.opportunity_score(),

            "Signal":

                self.signal(),

            "Direction":

                self.trade_direction(),

            "Category":

                category["category"],

            "Trend":

                trend["trend"],

            "Smart Rank":

                category["smart_rank"],

            "Recommendation":

                recommendation["recommendation"],

        }


# ==========================================================
# MARKET SUMMARY
# ==========================================================

    @staticmethod

    def market_summary(

        scanners: List["ScannerEngine"],

    ) -> Dict:

        if not scanners:

            return {}

        scores = [

            scanner.priority_score()

            for scanner in scanners

        ]

        average = sum(

            scores

        ) / len(

            scores

        )

        bullish = len(

            [

                s

                for s in scanners

                if s.trade_direction() == "BUY"

            ]

        )

        bearish = len(

            [

                s

                for s in scanners

                if s.trade_direction() == "SELL"

            ]

        )

        neutral = len(scanners) - bullish - bearish

        return {

            "Stocks":

                len(scanners),

            "Average Score":

                round(

                    average,

                    2,

                ),

            "Bullish":

                bullish,

            "Bearish":

                bearish,

            "Neutral":

                neutral,

        }


# ==========================================================
# SECTOR HEATMAP
# ==========================================================

    @staticmethod

    def sector_heatmap(

        scanners: List["ScannerEngine"],

    ) -> pd.DataFrame:

        dataframe = ScannerEngine.sector_ranking(

            scanners

        )

        if dataframe.empty:

            return dataframe

        dataframe["Heat"] = dataframe[

            "Average Score"

        ].apply(

            lambda x:

            "🟢"

            if x >= 80 else

            "🟡"

            if x >= 65 else

            "🟠"

            if x >= 50 else

            "🔴"

        )

        return dataframe


# ==========================================================
# TOP GAINERS
# ==========================================================

    @staticmethod

    def top_gainers(

        scanners: List["ScannerEngine"],

        limit: int = 10,

    ) -> pd.DataFrame:

        dataframe = ScannerEngine.batch_scan(

            scanners

        )

        if dataframe.empty:

            return dataframe

        return dataframe.sort_values(

            by="Score",

            ascending=False,

        ).head(

            limit

        )


# ==========================================================
# TOP WEAK STOCKS
# ==========================================================

    @staticmethod

    def weakest_stocks(

        scanners: List["ScannerEngine"],

        limit: int = 10,

    ) -> pd.DataFrame:

        dataframe = ScannerEngine.batch_scan(

            scanners

        )

        if dataframe.empty:

            return dataframe

        return dataframe.sort_values(

            by="Score",

            ascending=True,

        ).head(

            limit

        )


# ==========================================================
# AI WATCHLIST DASHBOARD
# ==========================================================

    @staticmethod

    def watchlist_dashboard(

        scanners: List["ScannerEngine"],

    ) -> pd.DataFrame:

        rows = []

        for scanner in scanners:

            rows.append(

                scanner.watchlist_entry()

            )

        dataframe = pd.DataFrame(

            rows

        )

        if dataframe.empty:

            return dataframe

        dataframe = dataframe.sort_values(

            by="Score",

            ascending=False,

        )

        return dataframe.reset_index(

            drop=True,

        )


# ==========================================================
# SCANNER STATISTICS
# ==========================================================

    @staticmethod

    def statistics(

        scanners: List["ScannerEngine"],

    ) -> Dict:

        dataframe = ScannerEngine.batch_scan(

            scanners

        )

        if dataframe.empty:

            return {}

        return {

            "Total":

                len(dataframe),

            "Average":

                round(

                    dataframe["Score"].mean(),

                    2,

                ),

            "Highest":

                round(

                    dataframe["Score"].max(),

                    2,

                ),

            "Lowest":

                round(

                    dataframe["Score"].min(),

                    2,

                ),

            "Median":

                round(

                    dataframe["Score"].median(),

                    2,

                ),

        }


# ==========================================================
# SCANNER HEALTH
# ==========================================================

    @staticmethod

    def health_check(

        scanners: List["ScannerEngine"],

    ) -> Dict:

        healthy = 0

        failed = 0

        for scanner in scanners:

            if scanner.validate():

                healthy += 1

            else:

                failed += 1

        return {

            "Healthy":

                healthy,

            "Failed":

                failed,

            "Total":

                healthy + failed,

        }


# ==========================================================
# EXPORT DASHBOARD
# ==========================================================

    @staticmethod

    def export_dashboard(

        scanners: List["ScannerEngine"],

    ) -> Dict:

        return {

            "Market":

                ScannerEngine.market_summary(

                    scanners

                ),

            "Statistics":

                ScannerEngine.statistics(

                    scanners

                ),

            "Health":

                ScannerEngine.health_check(

                    scanners

                ),

        }


# ==========================================================
# EXPORT DATAFRAME
# ==========================================================

    @staticmethod

    def export_dataframe(

        scanners: List["ScannerEngine"],

    ) -> pd.DataFrame:

        return ScannerEngine.batch_scan(

            scanners

        )


# ==========================================================
# EXPORT JSON
# ==========================================================

    @staticmethod

    def export_json(

        scanners: List["ScannerEngine"],

    ) -> str:

        dataframe = ScannerEngine.batch_scan(

            scanners

        )

        return dataframe.to_json(

            orient="records",

            indent=4,

        )
    # ==========================================================
# AI RANKING ENGINE
# ==========================================================

    @staticmethod
    def ai_ranking(

        scanners: List["ScannerEngine"],

    ) -> pd.DataFrame:

        dataframe = ScannerEngine.batch_scan(

            scanners

        )

        if dataframe.empty:

            return dataframe

        dataframe["AI Rank"] = (

            dataframe["Score"]

            .rank(

                ascending=False,

                method="dense",

            )

            .astype(int)

        )

        dataframe = dataframe.sort_values(

            by=[

                "AI Rank",

                "Score",

            ]

        )

        return dataframe.reset_index(

            drop=True,

        )


# ==========================================================
# OPPORTUNITY FILTER
# ==========================================================

    @staticmethod
    def opportunity_filter(

        scanners: List["ScannerEngine"],

        minimum_score: float = 80,

    ) -> List[Dict]:

        opportunities = []

        for scanner in scanners:

            if (

                scanner.priority_score()

                >=

                minimum_score

            ):

                opportunities.append(

                    scanner.scanner_summary()

                )

        return sorted(

            opportunities,

            key=lambda x:

            x["Priority Score"],

            reverse=True,

        )


# ==========================================================
# MULTI-TIMEFRAME SCANNER
# ==========================================================

    @staticmethod
    def multi_timeframe_scan(

        scanners: List["ScannerEngine"],

    ) -> pd.DataFrame:

        rows = []

        for scanner in scanners:

            category = scanner.trade_category()

            rows.append(

                {

                    "Symbol":

                        scanner.symbol,

                    "Intraday":

                        scanner.intraday_score(),

                    "Swing":

                        scanner.swing_score(),

                    "Positional":

                        scanner.positional_score(),

                    "Best":

                        category["category"],

                    "Priority":

                        scanner.priority_score(),

                }

            )

        dataframe = pd.DataFrame(

            rows

        )

        return dataframe.sort_values(

            by="Priority",

            ascending=False,

        ).reset_index(

            drop=True,

        )


# ==========================================================
# HIGH CONVICTION PICKS
# ==========================================================

    @staticmethod
    def high_conviction_picks(

        scanners: List["ScannerEngine"],

        limit: int = 10,

    ) -> List[Dict]:

        picks = []

        for scanner in scanners:

            if (

                scanner.confidence_score()

                >= 85

                and

                scanner.priority_score()

                >= 85

            ):

                picks.append(

                    scanner.watchlist_entry()

                )

        picks.sort(

            key=lambda x:

            x["Score"],

            reverse=True,

        )

        return picks[:limit]


# ==========================================================
# INSTITUTIONAL PICKS
# ==========================================================

    @staticmethod
    def institutional_picks(

        scanners: List["ScannerEngine"],

    ) -> List[Dict]:

        output = []

        for scanner in scanners:

            confirmation = (

                scanner.institutional_confirmation()

            )

            if confirmation["confirmed"]:

                output.append(

                    scanner.watchlist_entry()

                )

        output.sort(

            key=lambda x:

            x["Score"],

            reverse=True,

        )

        return output


# ==========================================================
# BREAKOUT CANDIDATES
# ==========================================================

    @staticmethod
    def breakout_candidates(

        scanners: List["ScannerEngine"],

    ) -> List[Dict]:

        results = []

        for scanner in scanners:

            if (

                scanner.pattern_score()

                >= 80

                and

                scanner.trade_direction()

                == "BUY"

            ):

                results.append(

                    scanner.scanner_summary()

                )

        return sorted(

            results,

            key=lambda x:

            x["Priority Score"],

            reverse=True,

        )


# ==========================================================
# TREND CONTINUATION
# ==========================================================

    @staticmethod
    def trend_continuation_candidates(

        scanners: List["ScannerEngine"],

    ) -> List[Dict]:

        output = []

        for scanner in scanners:

            trend = scanner.trend_strength()

            if (

                trend["score"]

                >= 75

            ):

                output.append(

                    scanner.scanner_summary()

                )

        return sorted(

            output,

            key=lambda x:

            x["Priority Score"],

            reverse=True,

        )


# ==========================================================
# REVERSAL CANDIDATES
# ==========================================================

    @staticmethod
    def reversal_candidates(

        scanners: List["ScannerEngine"],

    ) -> List[Dict]:

        output = []

        for scanner in scanners:

            if (

                scanner.trade_direction()

                == "HOLD"

                and

                scanner.pattern_score()

                >= 70

            ):

                output.append(

                    scanner.scanner_summary()

                )

        return sorted(

            output,

            key=lambda x:

            x["Pattern Score"]

            if "Pattern Score" in x

            else x["Priority Score"],

            reverse=True,

        )


# ==========================================================
# MASTER AI REPORT
# ==========================================================

    @staticmethod
    def master_report(

        scanners: List["ScannerEngine"],

    ) -> Dict:

        return {

            "market_summary":

                ScannerEngine.market_summary(

                    scanners

                ),

            "statistics":

                ScannerEngine.statistics(

                    scanners

                ),

            "top_intraday":

                ScannerEngine.top_intraday(

                    scanners

                ),

            "top_swing":

                ScannerEngine.top_swing(

                    scanners

                ),

            "top_positional":

                ScannerEngine.top_positional(

                    scanners

                ),

            "high_conviction":

                ScannerEngine.high_conviction_picks(

                    scanners

                ),

            "institutional":

                ScannerEngine.institutional_picks(

                    scanners

                ),

        }


# ==========================================================
# ENTERPRISE OUTPUT
# ==========================================================

    @staticmethod
    def enterprise_output(

        scanners: List["ScannerEngine"],

    ) -> Dict:

        return {

            "ranking":

                ScannerEngine.ai_ranking(

                    scanners

                ),

            "watchlist":

                ScannerEngine.watchlist_dashboard(

                    scanners

                ),

            "heatmap":

                ScannerEngine.sector_heatmap(

                    scanners

                ),

            "report":

                ScannerEngine.master_report(

                    scanners

                ),

            "health":

                ScannerEngine.health_check(

                    scanners

                ),

        }
    # ==========================================================
# SCAN HISTORY MANAGER
# ==========================================================

    @staticmethod
    def scan_history(

        scanners: List["ScannerEngine"],

    ) -> pd.DataFrame:

        rows = []

        timestamp = datetime.now()

        for scanner in scanners:

            rows.append(

                {

                    "Timestamp":

                        timestamp,

                    "Symbol":

                        scanner.symbol,

                    "Price":

                        scanner.last_price(),

                    "Priority":

                        scanner.priority_score(),

                    "Opportunity":

                        scanner.opportunity_score(),

                    "Signal":

                        scanner.signal(),

                    "Recommendation":

                        scanner.recommendation(),

                }

            )

        return pd.DataFrame(rows)


# ==========================================================
# ALERT QUEUE
# ==========================================================

    @staticmethod
    def alert_queue(

        scanners: List["ScannerEngine"],

        minimum_score: float = 85,

    ) -> List[Dict]:

        alerts = []

        for scanner in scanners:

            if (

                scanner.priority_score()

                >= minimum_score

            ):

                alerts.append(

                    {

                        "Symbol":

                            scanner.symbol,

                        "Signal":

                            scanner.signal(),

                        "Priority":

                            scanner.priority_score(),

                        "Recommendation":

                            scanner.recommendation(),

                        "Time":

                            datetime.now(),

                    }

                )

        alerts.sort(

            key=lambda x:

            x["Priority"],

            reverse=True,

        )

        return alerts


# ==========================================================
# DAILY TOP 5
# ==========================================================

    @staticmethod
    def daily_top_five(

        scanners: List["ScannerEngine"],

    ) -> pd.DataFrame:

        dataframe = ScannerEngine.batch_scan(

            scanners

        )

        if dataframe.empty:

            return dataframe

        dataframe = dataframe.sort_values(

            by="Score",

            ascending=False,

        )

        return dataframe.head(5)


# ==========================================================
# EXPORT CSV
# ==========================================================

    @staticmethod
    def export_csv(

        scanners: List["ScannerEngine"],

        filename: str,

    ) -> bool:

        try:

            dataframe = ScannerEngine.batch_scan(

                scanners

            )

            dataframe.to_csv(

                filename,

                index=False,

            )

            return True

        except Exception:

            return False


# ==========================================================
# EXPORT EXCEL
# ==========================================================

    @staticmethod
    def export_excel(

        scanners: List["ScannerEngine"],

        filename: str,

    ) -> bool:

        try:

            dataframe = ScannerEngine.batch_scan(

                scanners

            )

            dataframe.to_excel(

                filename,

                index=False,

            )

            return True

        except Exception:

            return False


# ==========================================================
# PERFORMANCE METRICS
# ==========================================================

    @staticmethod
    def performance_metrics(

        scanners: List["ScannerEngine"],

    ) -> Dict:

        dataframe = ScannerEngine.batch_scan(

            scanners

        )

        if dataframe.empty:

            return {}

        return {

            "Total Stocks":

                len(dataframe),

            "Average Score":

                round(

                    dataframe["Score"].mean(),

                    2,

                ),

            "Highest Score":

                round(

                    dataframe["Score"].max(),

                    2,

                ),

            "Lowest Score":

                round(

                    dataframe["Score"].min(),

                    2,

                ),

            "Above 80":

                len(

                    dataframe[

                        dataframe["Score"] >= 80

                    ]

                ),

            "Above 90":

                len(

                    dataframe[

                        dataframe["Score"] >= 90

                    ]

                ),

        }


# ==========================================================
# CACHE REFRESH
# ==========================================================

    def refresh(

        self,

    ) -> None:

        self.reset()

        self.initialize_engines()


# ==========================================================
# ENTERPRISE VALIDATION
# ==========================================================

    @staticmethod
    def validate_scanners(

        scanners: List["ScannerEngine"],

    ) -> bool:

        return all(

            scanner.validate()

            for scanner in scanners

        )


# ==========================================================
# DEPLOYMENT INFORMATION
# ==========================================================

    @staticmethod
    def deployment_info(

    ) -> Dict:

        return {

            "Application":

                "StockVersity Scanner Pro",

            "Module":

                "Scanner Engine",

            "Version":

                "4.0",

            "Environment":

                "Production",

            "Powered By":

                "AI",

        }


# ==========================================================
# PRODUCTION SUMMARY
# ==========================================================

    @staticmethod
    def production_summary(

        scanners: List["ScannerEngine"],

    ) -> Dict:

        return {

            "Deployment":

                ScannerEngine.deployment_info(),

            "Health":

                ScannerEngine.health_check(

                    scanners

                ),

            "Performance":

                ScannerEngine.performance_metrics(

                    scanners

                ),

            "Market":

                ScannerEngine.market_summary(

                    scanners

                ),

        }
    # ==========================================================
# MASTER EXECUTION PIPELINE
# ==========================================================

    def run(

        self,

    ) -> Dict:

        if not self.validate():

            raise ValueError(

                "Invalid scanner data."

            )

        self.build_result()

        return {

            "result":

                self.result,

            "summary":

                self.scanner_summary(),

            "dashboard":

                self.dashboard(),

            "watchlist":

                self.watchlist_entry(),

            "recommendation":

                self.professional_recommendation(),

            "decision":

                self.trading_decision(),

            "category":

                self.trade_category(),

            "trend":

                self.trend_strength(),

            "institutional":

                self.institutional_confirmation(),

        }


# ==========================================================
# COMPLETE RESULT
# ==========================================================

    def result_object(

        self,

    ) -> ScannerResult:

        if self.result is None:

            self.build_result()

        return self.result


# ==========================================================
# HEALTH CHECK
# ==========================================================

    def health_check(

        self,

    ) -> Dict:

        checks = {

            "Data Valid":

                self.validate(),

            "Market Regime":

                "market_regime" in self.engines,

            "Market Sentiment":

                "market_sentiment" in self.engines,

            "Prediction":

                "prediction" in self.engines,

            "Market Structure":

                "market_structure" in self.engines,

            "Volume":

                "volume" in self.engines,

            "Liquidity":

                "liquidity" in self.engines,

            "Risk":

                "risk" in self.engines,

            "Sector":

                "sector" in self.engines,

            "Patterns":

                "patterns" in self.engines,

        }

        return {

            "healthy":

                all(checks.values()),

            "checks":

                checks,

        }


# ==========================================================
# SELF TEST
# ==========================================================

    def self_test(

        self,

    ) -> Dict:

        tests = {

            "Combined Score":

                isinstance(

                    self.combined_ai_score(),

                    float,

                ),

            "Priority Score":

                isinstance(

                    self.priority_score(),

                    float,

                ),

            "Signal":

                isinstance(

                    self.signal(),

                    str,

                ),

            "Recommendation":

                isinstance(

                    self.recommendation(),

                    str,

                ),

            "Result":

                isinstance(

                    self.build_result(),

                    ScannerResult,

                ),

        }

        return {

            "passed":

                all(

                    tests.values()

                ),

            "tests":

                tests,

        }


# ==========================================================
# VERSION
# ==========================================================

    @staticmethod
    def version(

    ) -> Dict:

        return {

            "Application":

                "StockVersity Scanner Pro",

            "Module":

                "Scanner Engine",

            "Version":

                "4.0",

            "Powered By":

                "AI",

            "Status":

                "Production Ready",

        }


# ==========================================================
# ENGINE SUMMARY
# ==========================================================

    def engine_summary(

        self,

    ) -> Dict:

        return {

            "Version":

                self.version(),

            "Health":

                self.health_check(),

            "Self Test":

                self.self_test(),

            "Summary":

                self.scanner_summary(),

            "Dashboard":

                self.dashboard(),

        }


# ==========================================================
# STRING REPRESENTATION
# ==========================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"ScannerEngine("

            f"symbol='{self.symbol}', "

            f"score={self.priority_score():.2f}, "

            f"signal='{self.signal()}')"

        )


# ==========================================================
# HUMAN READABLE OUTPUT
# ==========================================================

    def __str__(

        self,

    ) -> str:

        return (

            "\n"

            "==============================================\n"

            "     STOCKVERSITY SCANNER PRO v4.0\n"

            "==============================================\n"

            f"Symbol          : {self.symbol}\n"

            f"Price           : {self.last_price():.2f}\n"

            f"Priority Score  : {self.priority_score():.2f}\n"

            f"Signal          : {self.signal()}\n"

            f"Direction       : {self.trade_direction()}\n"

            f"Recommendation  : {self.recommendation()}\n"

            "=============================================="

        )


# ==========================================================
# END OF FILE
# ==========================================================