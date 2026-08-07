"""
==============================================================
StockVersity Scanner Pro
AI Trading Decision Engine
Version : 4.0
Powered by AI
==============================================================
"""

from __future__ import annotations

import math
import time
import json
import logging

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from backend.ai.market_regime_detector import (
    MarketRegimeDetector,
    MarketRegime,
)

from backend.ai.strategy_optimizer import (
    StrategyOptimizer,
)

# ==========================================================
# DECISION
# ==========================================================


class TradingDecision(Enum):

    STRONG_BUY = "STRONG_BUY"

    BUY = "BUY"

    WATCH = "WATCH"

    HOLD = "HOLD"

    SELL = "SELL"

    STRONG_SELL = "STRONG_SELL"


# ==========================================================
# ENTRY TYPE
# ==========================================================


class EntryType(Enum):

    BREAKOUT = "BREAKOUT"

    PULLBACK = "PULLBACK"

    REVERSAL = "REVERSAL"

    RANGE = "RANGE"

    NONE = "NONE"


# ==========================================================
# RISK LEVEL
# ==========================================================


class RiskLevel(Enum):

    VERY_LOW = "VERY_LOW"

    LOW = "LOW"

    MEDIUM = "MEDIUM"

    HIGH = "HIGH"

    VERY_HIGH = "VERY_HIGH"


# ==========================================================
# DECISION CONFIG
# ==========================================================


@dataclass
class DecisionConfig:

    minimum_confidence: float = 65.0

    strong_buy_score: float = 90.0

    buy_score: float = 75.0

    sell_score: float = 35.0

    strong_sell_score: float = 20.0

    minimum_rr: float = 2.0

    max_position_percent: float = 5.0

    atr_multiplier_sl: float = 1.5

    atr_multiplier_target: float = 3.0


# ==========================================================
# DECISION RESULT
# ==========================================================


@dataclass
class DecisionResult:

    symbol: str

    decision: TradingDecision

    entry_type: EntryType

    confidence: float

    score: float

    risk: RiskLevel

    entry_price: float

    stop_loss: float

    target: float

    risk_reward: float

    reasons: List[str] = field(default_factory=list)

    warnings: List[str] = field(default_factory=list)

    metadata: Dict = field(default_factory=dict)


# ==========================================================
# TRADING DECISION ENGINE
# ==========================================================


class TradingDecisionEngine:

    """
    Converts scanner output into
    institutional-quality trading decisions.
    """

    def __init__(

        self,

        config: Optional[DecisionConfig] = None,

    ) -> None:

        self.config = config or DecisionConfig()

        self.market_detector = MarketRegimeDetector()

        self.strategy_optimizer = StrategyOptimizer()

        self.symbol: str = ""

        self.data: Optional[pd.DataFrame] = None

        self.result: Optional[DecisionResult] = None

        self.history: List[DecisionResult] = []

        self.logger = logging.getLogger(__name__)

        self.running = False

        self.last_runtime = 0.0

    # ==========================================================
    # CONFIGURATION
    # ==========================================================

    def configure(

        self,

        config: DecisionConfig,

    ) -> None:

        self.config = config

    # ==========================================================
    # LOAD DATA
    # ==========================================================

    def load_data(

        self,

        symbol: str,

        dataframe: pd.DataFrame,

    ) -> None:

        self.symbol = symbol

        self.data = dataframe.copy()

    # ==========================================================
    # VALIDATE
    # ==========================================================

    def validate(

        self,

    ) -> None:

        if self.data is None or self.data.empty:

            raise ValueError("Market data not loaded.")

        required = [

            "Open",

            "High",

            "Low",

            "Close",

            "Volume",

        ]

        for column in required:

            if column not in self.data.columns:

                raise ValueError(
                    f"Missing column: {column}"
                )

    # ==========================================================
    # RESET
    # ==========================================================

    def clear(

        self,

    ) -> None:

        self.result = None

        self.running = False
    # ==========================================================
    # ATR
    # ==========================================================

    def atr(

        self,

        period: int = 14,

    ) -> float:

        high = self.data["High"]

        low = self.data["Low"]

        close = self.data["Close"]

        tr = pd.concat(

            [

                high - low,

                (high - close.shift()).abs(),

                (low - close.shift()).abs(),

            ],

            axis=1,

        ).max(

            axis=1

        )

        atr = tr.rolling(

            period

        ).mean()

        return float(

            atr.iloc[-1]

        )

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
    # ENTRY PRICE
    # ==========================================================

    def entry_price(

        self,

        decision: TradingDecision,

    ) -> float:

        price = self.last_price()

        atr = self.atr()

        if decision in (

            TradingDecision.BUY,

            TradingDecision.STRONG_BUY,

        ):

            return round(

                price + atr * 0.10,

                2,

            )

        if decision in (

            TradingDecision.SELL,

            TradingDecision.STRONG_SELL,

        ):

            return round(

                price - atr * 0.10,

                2,

            )

        return round(

            price,

            2,

        )

    # ==========================================================
    # STOP LOSS
    # ==========================================================

    def stop_loss(

        self,

        decision: TradingDecision,

        entry: float,

    ) -> float:

        atr = self.atr()

        distance = (

            atr

            *

            self.config.atr_multiplier_sl

        )

        if decision in (

            TradingDecision.BUY,

            TradingDecision.STRONG_BUY,

        ):

            return round(

                entry - distance,

                2,

            )

        if decision in (

            TradingDecision.SELL,

            TradingDecision.STRONG_SELL,

        ):

            return round(

                entry + distance,

                2,

            )

        return round(

            entry,

            2,

        )

    # ==========================================================
    # TARGET
    # ==========================================================

    def target(

        self,

        decision: TradingDecision,

        entry: float,

    ) -> float:

        atr = self.atr()

        distance = (

            atr

            *

            self.config.atr_multiplier_target

        )

        if decision in (

            TradingDecision.BUY,

            TradingDecision.STRONG_BUY,

        ):

            return round(

                entry + distance,

                2,

            )

        if decision in (

            TradingDecision.SELL,

            TradingDecision.STRONG_SELL,

        ):

            return round(

                entry - distance,

                2,

            )

        return round(

            entry,

            2,

        )

    # ==========================================================
    # RISK REWARD
    # ==========================================================

    def risk_reward(

        self,

        entry: float,

        stop: float,

        target: float,

    ) -> float:

        risk = abs(

            entry - stop

        )

        reward = abs(

            target - entry

        )

        if risk == 0:

            return 0.0

        return round(

            reward / risk,

            2,

        )

    # ==========================================================
    # POSITION SIZE
    # ==========================================================

    def position_size(

        self,

        capital: float,

        risk_percent: float,

        entry: float,

        stop: float,

    ) -> Dict:

        risk_amount = (

            capital

            *

            risk_percent

            / 100

        )

        risk_per_share = abs(

            entry - stop

        )

        if risk_per_share <= 0:

            quantity = 0

        else:

            quantity = math.floor(

                risk_amount

                /

                risk_per_share

            )

        investment = quantity * entry

        return {

            "capital":

                capital,

            "risk_amount":

                round(

                    risk_amount,

                    2,

                ),

            "quantity":

                int(

                    quantity

                ),

            "investment":

                round(

                    investment,

                    2,

                ),

        }

    # ==========================================================
    # VOLATILITY ADJUSTED POSITION SIZE
    # ==========================================================

    def volatility_position_size(

        self,

        capital: float,

        risk_percent: float,

    ) -> Dict:

        atr = self.atr()

        price = self.last_price()

        volatility = atr / price

        adjustment = 1.0

        if volatility > 0.05:

            adjustment = 0.50

        elif volatility > 0.03:

            adjustment = 0.70

        elif volatility > 0.02:

            adjustment = 0.85

        adjusted_risk = (

            risk_percent

            *

            adjustment

        )

        entry = self.last_price()

        stop = entry - atr

        data = self.position_size(

            capital,

            adjusted_risk,

            entry,

            stop,

        )

        data["adjustment_factor"] = round(

            adjustment,

            2,

        )

        data["volatility"] = round(

            volatility * 100,

            2,

        )

        return data

    # ==========================================================
    # INITIAL TRADE SCORE
    # ==========================================================

    def trade_score(

        self,

        confidence: float,

        regime_score: float,

        risk_reward: float,

    ) -> float:

        score = (

            confidence * 0.45

            +

            regime_score * 0.35

            +

            min(

                risk_reward,

                5,

            ) * 20 * 0.20

        )

        return round(

            min(

                score,

                100,

            ),

            2,

        )
        # ==========================================================
    # DECISION SCORE
    # ==========================================================

    def decision_score(

        self,

        confidence: float,

        regime_score: float,

        rr: float,

        volume_score: float = 50.0,

    ) -> float:

        score = (

            confidence * 0.35

            +

            regime_score * 0.30

            +

            min(rr, 5.0) / 5.0 * 20

            +

            volume_score * 0.15

        )

        return round(

            min(

                score,

                100.0,

            ),

            2,

        )

    # ==========================================================
    # DECISION
    # ==========================================================

    def classify_decision(

        self,

        score: float,

        confidence: float,

    ) -> TradingDecision:

        if confidence < self.config.minimum_confidence:

            return TradingDecision.WATCH

        if score >= self.config.strong_buy_score:

            return TradingDecision.STRONG_BUY

        if score >= self.config.buy_score:

            return TradingDecision.BUY

        if score <= self.config.strong_sell_score:

            return TradingDecision.STRONG_SELL

        if score <= self.config.sell_score:

            return TradingDecision.SELL

        return TradingDecision.HOLD

    # ==========================================================
    # ENTRY TYPE
    # ==========================================================

    def determine_entry_type(

        self,

        regime: MarketRegime,

    ) -> EntryType:

        if regime == MarketRegime.STRONG_BULL:

            return EntryType.BREAKOUT

        if regime == MarketRegime.BULL:

            return EntryType.PULLBACK

        if regime == MarketRegime.STRONG_BEAR:

            return EntryType.BREAKOUT

        if regime == MarketRegime.BEAR:

            return EntryType.REVERSAL

        if regime == MarketRegime.SIDEWAYS:

            return EntryType.RANGE

        return EntryType.NONE

    # ==========================================================
    # RISK LEVEL
    # ==========================================================

    def determine_risk(

        self,

        confidence: float,

        volatility: str,

    ) -> RiskLevel:

        if volatility == "EXTREME":

            return RiskLevel.VERY_HIGH

        if confidence >= 90:

            return RiskLevel.LOW

        if confidence >= 80:

            return RiskLevel.MEDIUM

        if confidence >= 65:

            return RiskLevel.HIGH

        return RiskLevel.VERY_HIGH

    # ==========================================================
    # TRADE QUALITY
    # ==========================================================

    def trade_quality(

        self,

        score: float,

    ) -> str:

        if score >= 90:

            return "A+"

        if score >= 80:

            return "A"

        if score >= 70:

            return "B"

        if score >= 60:

            return "C"

        return "D"

    # ==========================================================
    # REASONS
    # ==========================================================

    def generate_reasons(

        self,

        regime_result,

    ) -> List[str]:

        reasons = []

        if regime_result.regime in (

            MarketRegime.BULL,

            MarketRegime.STRONG_BULL,

        ):

            reasons.append(

                "Market trend is bullish."

            )

        if regime_result.regime in (

            MarketRegime.BEAR,

            MarketRegime.STRONG_BEAR,

        ):

            reasons.append(

                "Market trend is bearish."

            )

        if regime_result.confidence >= 80:

            reasons.append(

                "High confidence setup."

            )

        if regime_result.score >= 80:

            reasons.append(

                "Strong regime score."

            )

        if regime_result.details.get(

            "behavior"

        ) == "BREAKOUT":

            reasons.append(

                "Breakout market structure."

            )

        if regime_result.details.get(

            "volatility_shock"

        ):

            reasons.append(

                "Momentum expansion detected."

            )

        return reasons

    # ==========================================================
    # WARNINGS
    # ==========================================================

    def generate_warnings(

        self,

        regime_result,

        rr: float,

    ) -> List[str]:

        warnings = []

        if rr < self.config.minimum_rr:

            warnings.append(

                "Risk/Reward below preferred threshold."

            )

        if regime_result.confidence < self.config.minimum_confidence:

            warnings.append(

                "Low confidence trade."

            )

        if regime_result.details.get(

            "volatility"

        ) == "EXTREME":

            warnings.append(

                "Extreme volatility."

            )

        if regime_result.details.get(

            "behavior"

        ) == "MEAN_REVERSION":

            warnings.append(

                "Trend not confirmed."

            )

        return warnings

    # ==========================================================
    # INSTITUTIONAL FILTER
    # ==========================================================

    def institutional_filter(

        self,

        regime_result,

    ) -> bool:

        confidence = regime_result.confidence

        score = regime_result.score

        behavior = regime_result.details.get(

            "behavior"

        )

        return (

            confidence >= 75

            and

            score >= 70

            and

            behavior == "BREAKOUT"

        )

    # ==========================================================
    # FINAL QUALITY SCORE
    # ==========================================================

    def quality_score(

        self,

        score: float,

        rr: float,

        institutional: bool,

    ) -> float:

        final = score

        if institutional:

            final += 5

        if rr >= 3:

            final += 5

        return round(

            min(

                final,

                100,

            ),

            2,

        )
        # ==========================================================
    # LONG TRADE BUILDER
    # ==========================================================

    def build_long_trade(

        self,

        confidence: float,

        regime_score: float,

    ) -> Dict:

        entry = self.entry_price(

            TradingDecision.BUY

        )

        stop = self.stop_loss(

            TradingDecision.BUY,

            entry,

        )

        target = self.target(

            TradingDecision.BUY,

            entry,

        )

        rr = self.risk_reward(

            entry,

            stop,

            target,

        )

        score = self.trade_score(

            confidence,

            regime_score,

            rr,

        )

        return {

            "direction": "LONG",

            "entry": entry,

            "stop_loss": stop,

            "target": target,

            "risk_reward": rr,

            "score": score,

        }

    # ==========================================================
    # SHORT TRADE BUILDER
    # ==========================================================

    def build_short_trade(

        self,

        confidence: float,

        regime_score: float,

    ) -> Dict:

        entry = self.entry_price(

            TradingDecision.SELL

        )

        stop = self.stop_loss(

            TradingDecision.SELL,

            entry,

        )

        target = self.target(

            TradingDecision.SELL,

            entry,

        )

        rr = self.risk_reward(

            entry,

            stop,

            target,

        )

        score = self.trade_score(

            confidence,

            regime_score,

            rr,

        )

        return {

            "direction": "SHORT",

            "entry": entry,

            "stop_loss": stop,

            "target": target,

            "risk_reward": rr,

            "score": score,

        }

    # ==========================================================
    # DYNAMIC STOP LOSS
    # ==========================================================

    def optimize_stop_loss(

        self,

        direction: str,

        entry: float,

    ) -> float:

        atr = self.atr()

        recent_high = float(

            self.data["High"].tail(10).max()

        )

        recent_low = float(

            self.data["Low"].tail(10).min()

        )

        if direction == "LONG":

            sl = max(

                recent_low,

                entry - atr * self.config.atr_multiplier_sl,

            )

        else:

            sl = min(

                recent_high,

                entry + atr * self.config.atr_multiplier_sl,

            )

        return round(

            sl,

            2,

        )

    # ==========================================================
    # MULTI TARGETS
    # ==========================================================

    def profit_targets(

        self,

        direction: str,

        entry: float,

        stop: float,

    ) -> Dict:

        risk = abs(

            entry - stop

        )

        if direction == "LONG":

            t1 = entry + risk

            t2 = entry + risk * 2

            t3 = entry + risk * 3

        else:

            t1 = entry - risk

            t2 = entry - risk * 2

            t3 = entry - risk * 3

        return {

            "T1": round(t1, 2),

            "T2": round(t2, 2),

            "T3": round(t3, 2),

        }

    # ==========================================================
    # TRAILING STOP
    # ==========================================================

    def trailing_stop(

        self,

        direction: str,

        current_price: float,

        current_stop: float,

    ) -> float:

        atr = self.atr()

        if direction == "LONG":

            new_stop = max(

                current_stop,

                current_price - atr,

            )

        else:

            new_stop = min(

                current_stop,

                current_price + atr,

            )

        return round(

            new_stop,

            2,

        )

    # ==========================================================
    # BREAK EVEN
    # ==========================================================

    def break_even_price(

        self,

        entry: float,

        stop: float,

        current_price: float,

        direction: str,

    ) -> bool:

        risk = abs(

            entry - stop

        )

        if direction == "LONG":

            return current_price >= entry + risk

        return current_price <= entry - risk

    # ==========================================================
    # PARTIAL PROFIT BOOKING
    # ==========================================================

    def partial_exit_plan(

        self,

        quantity: int,

    ) -> Dict:

        first = int(

            quantity * 0.30

        )

        second = int(

            quantity * 0.30

        )

        final = quantity - first - second

        return {

            "T1_QTY": first,

            "T2_QTY": second,

            "T3_QTY": final,

        }

    # ==========================================================
    # COMPLETE TRADE SETUP
    # ==========================================================

    def trade_setup(

        self,

        direction: str,

        confidence: float,

        regime_score: float,

    ) -> Dict:

        if direction == "LONG":

            trade = self.build_long_trade(

                confidence,

                regime_score,

            )

        else:

            trade = self.build_short_trade(

                confidence,

                regime_score,

            )

        trade["optimized_stop"] = self.optimize_stop_loss(

            direction,

            trade["entry"],

        )

        trade["targets"] = self.profit_targets(

            direction,

            trade["entry"],

            trade["optimized_stop"],

        )

        trade["trail_after"] = "Target 1"

        trade["move_to_break_even"] = "After 1R"

        trade["partial_booking"] = {

            "T1": "30%",

            "T2": "30%",

            "T3": "40%",

        }

        return trade
        # ==========================================================
    # MARKET REGIME VALIDATION
    # ==========================================================

    def validate_market_regime(

        self,

        regime_result,

    ) -> bool:

        if regime_result is None:

            return False

        if regime_result.confidence < self.config.minimum_confidence:

            return False

        if regime_result.score < 60:

            return False

        return True

    # ==========================================================
    # MULTI TIMEFRAME CONFIRMATION
    # ==========================================================

    def multi_timeframe_confirmation(

        self,

        timeframe_results: Dict[str, str],

    ) -> Dict:

        bullish = 0

        bearish = 0

        neutral = 0

        for value in timeframe_results.values():

            value = value.upper()

            if "BULL" in value:

                bullish += 1

            elif "BEAR" in value:

                bearish += 1

            else:

                neutral += 1

        total = max(

            len(timeframe_results),

            1,

        )

        confidence = round(

            max(

                bullish,

                bearish,

                neutral,

            ) / total * 100,

            2,

        )

        if bullish > bearish:

            trend = "BULLISH"

        elif bearish > bullish:

            trend = "BEARISH"

        else:

            trend = "NEUTRAL"

        return {

            "trend": trend,

            "bullish": bullish,

            "bearish": bearish,

            "neutral": neutral,

            "confidence": confidence,

        }

    # ==========================================================
    # VOLUME CONFIRMATION
    # ==========================================================

    def volume_confirmation(

        self,

        period: int = 20,

    ) -> Dict:

        volume = self.data["Volume"]

        average = volume.rolling(

            period

        ).mean()

        latest = float(

            volume.iloc[-1]

        )

        avg = float(

            average.iloc[-1]

        )

        ratio = 1.0

        if avg > 0:

            ratio = latest / avg

        confirmed = ratio >= 1.50

        return {

            "confirmed": confirmed,

            "ratio": round(

                ratio,

                2,

            ),

        }

    # ==========================================================
    # RELATIVE STRENGTH CONFIRMATION
    # ==========================================================

    def relative_strength_confirmation(

        self,

        benchmark_close: pd.Series,

    ) -> Dict:

        asset_return = (

            self.data["Close"].iloc[-1]

            /

            self.data["Close"].iloc[-20]

            - 1

        )

        benchmark_return = (

            benchmark_close.iloc[-1]

            /

            benchmark_close.iloc[-20]

            - 1

        )

        rs = (

            asset_return

            -

            benchmark_return

        ) * 100

        return {

            "relative_strength": round(

                rs,

                2,

            ),

            "confirmed": rs > 0,

        }

    # ==========================================================
    # SECTOR CONFIRMATION
    # ==========================================================

    def sector_confirmation(

        self,

        sector_score: float,

    ) -> Dict:

        return {

            "score": round(

                sector_score,

                2,

            ),

            "confirmed": sector_score >= 70,

        }

    # ==========================================================
    # AI CONFIDENCE ADJUSTMENT
    # ==========================================================

    def adjusted_confidence(

        self,

        base_confidence: float,

        mtf: Dict,

        volume: Dict,

        sector: Dict,

    ) -> float:

        confidence = base_confidence

        if mtf["confirmed"] if "confirmed" in mtf else mtf["confidence"] >= 75:

            confidence += 5

        if volume["confirmed"]:

            confidence += 5

        if sector["confirmed"]:

            confidence += 5

        return round(

            min(

                confidence,

                100,

            ),

            2,

        )

    # ==========================================================
    # TRADE REJECTION FILTER
    # ==========================================================

    def reject_trade(

        self,

        regime_result,

        rr: float,

        volume_confirmed: bool,

    ) -> Tuple[bool, List[str]]:

        reasons = []

        if regime_result.confidence < self.config.minimum_confidence:

            reasons.append(

                "Low confidence"

            )

        if rr < self.config.minimum_rr:

            reasons.append(

                "Poor Risk Reward"

            )

        if not volume_confirmed:

            reasons.append(

                "Low volume confirmation"

            )

        if regime_result.details.get(

            "volatility"

        ) == "EXTREME":

            reasons.append(

                "Extreme volatility"

            )

        return (

            len(reasons) > 0,

            reasons,

        )

    # ==========================================================
    # EXECUTION SCORE
    # ==========================================================

    def execution_score(

        self,

        confidence: float,

        rr: float,

        volume_ratio: float,

        mtf_confidence: float,

    ) -> float:

        score = (

            confidence * 0.40

            +

            min(

                rr,

                5,

            ) * 20 * 0.20

            +

            min(

                volume_ratio,

                3,

            ) / 3 * 20

            +

            mtf_confidence * 0.20

        )

        return round(

            min(

                score,

                100,

            ),

            2,

        )

    # ==========================================================
    # COMPLETE VALIDATION
    # ==========================================================

    def validate_trade(

        self,

        regime_result,

        timeframe_results: Dict[str, str],

        sector_score: float,

        benchmark_close: Optional[pd.Series] = None,

    ) -> Dict:

        mtf = self.multi_timeframe_confirmation(

            timeframe_results

        )

        volume = self.volume_confirmation()

        sector = self.sector_confirmation(

            sector_score

        )

        relative = None

        if benchmark_close is not None:

            relative = self.relative_strength_confirmation(

                benchmark_close

            )

        confidence = self.adjusted_confidence(

            regime_result.confidence,

            mtf,

            volume,

            sector,

        )

        return {

            "market_valid":

                self.validate_market_regime(

                    regime_result

                ),

            "multi_timeframe":

                mtf,

            "volume":

                volume,

            "sector":

                sector,

            "relative_strength":

                relative,

            "adjusted_confidence":

                confidence,

        }
        # ==========================================================
    # AI DECISION SYNTHESIS
    # ==========================================================

    def synthesize_decision(

        self,

        regime_result,

        validation: Dict,

        rr: float,

        volume_ratio: float,

    ) -> Dict:

        confidence = validation[

            "adjusted_confidence"

        ]

        execution = self.execution_score(

            confidence,

            rr,

            volume_ratio,

            validation["multi_timeframe"]["confidence"],

        )

        decision = self.classify_decision(

            execution,

            confidence,

        )

        return {

            "decision": decision,

            "confidence": confidence,

            "execution_score": execution,

        }

    # ==========================================================
    # FINAL RECOMMENDATION
    # ==========================================================

    def recommendation(

        self,

        decision: TradingDecision,

    ) -> str:

        mapping = {

            TradingDecision.STRONG_BUY:

                "Aggressive Long Entry",

            TradingDecision.BUY:

                "Buy on Confirmation",

            TradingDecision.WATCH:

                "Watchlist Candidate",

            TradingDecision.HOLD:

                "No Fresh Position",

            TradingDecision.SELL:

                "Sell / Short on Weakness",

            TradingDecision.STRONG_SELL:

                "Aggressive Short",

        }

        return mapping.get(

            decision,

            "No Recommendation",

        )

    # ==========================================================
    # CAPITAL ALLOCATION
    # ==========================================================

    def capital_allocation(

        self,

        capital: float,

        confidence: float,

    ) -> Dict:

        max_capital = (

            capital

            *

            self.config.max_position_percent

            / 100

        )

        allocation = (

            max_capital

            *

            confidence

            / 100

        )

        return {

            "capital":

                capital,

            "recommended":

                round(

                    allocation,

                    2,

                ),

            "maximum":

                round(

                    max_capital,

                    2,

                ),

        }

    # ==========================================================
    # PORTFOLIO EXPOSURE
    # ==========================================================

    def portfolio_exposure(

        self,

        open_positions: int,

        max_positions: int,

    ) -> Dict:

        exposure = (

            open_positions

            /

            max(

                max_positions,

                1,

            )

        ) * 100

        return {

            "open_positions":

                open_positions,

            "max_positions":

                max_positions,

            "exposure":

                round(

                    exposure,

                    2,

                ),

            "can_add":

                open_positions < max_positions,

        }

    # ==========================================================
    # CORRELATION FILTER
    # ==========================================================

    def correlation_filter(

        self,

        correlations: Dict[str, float],

        threshold: float = 0.80,

    ) -> Dict:

        blocked = []

        for symbol, value in correlations.items():

            if abs(value) >= threshold:

                blocked.append(

                    symbol

                )

        return {

            "approved":

                len(blocked) == 0,

            "blocked_symbols":

                blocked,

        }

    # ==========================================================
    # DAILY RISK LIMIT
    # ==========================================================

    def daily_risk_check(

        self,

        today_loss_percent: float,

        limit: float = 3.0,

    ) -> Dict:

        return {

            "allowed":

                today_loss_percent < limit,

            "loss_percent":

                today_loss_percent,

            "daily_limit":

                limit,

        }

    # ==========================================================
    # POSITION RANKING
    # ==========================================================

    def rank_positions(

        self,

        opportunities: List[Dict],

    ) -> List[Dict]:

        ranked = sorted(

            opportunities,

            key=lambda x: (

                x.get(

                    "execution_score",

                    0,

                ),

                x.get(

                    "confidence",

                    0,

                ),

            ),

            reverse=True,

        )

        for index, item in enumerate(

            ranked,

            start=1,

        ):

            item["rank"] = index

        return ranked

    # ==========================================================
    # INSTITUTIONAL EXECUTION MODEL
    # ==========================================================

    def institutional_execution(

        self,

        confidence: float,

        execution_score: float,

        volume_ratio: float,

    ) -> Dict:

        algo = "TWAP"

        if volume_ratio >= 2:

            algo = "VWAP"

        if confidence >= 90:

            algo = "Iceberg"

        urgency = "NORMAL"

        if execution_score >= 90:

            urgency = "HIGH"

        elif execution_score <= 60:

            urgency = "LOW"

        return {

            "algorithm":

                algo,

            "urgency":

                urgency,

            "slice_orders":

                confidence >= 85,

        }

    # ==========================================================
    # COMPLETE AI EXECUTION PLAN
    # ==========================================================

    def execution_plan(

        self,

        capital: float,

        confidence: float,

        execution_score: float,

        volume_ratio: float,

        open_positions: int,

        max_positions: int,

    ) -> Dict:

        allocation = self.capital_allocation(

            capital,

            confidence,

        )

        exposure = self.portfolio_exposure(

            open_positions,

            max_positions,

        )

        institutional = self.institutional_execution(

            confidence,

            execution_score,

            volume_ratio,

        )

        return {

            "allocation":

                allocation,

            "portfolio":

                exposure,

            "institutional":

                institutional,

        }
        # ==========================================================
    # ANALYZE TRADE
    # ==========================================================

    def analyze_trade(

        self,

        regime_result,

        capital: float,

        timeframe_results: Dict[str, str],

        sector_score: float,

        benchmark_close: Optional[pd.Series] = None,

    ) -> DecisionResult:

        self.validate()

        validation = self.validate_trade(

            regime_result,

            timeframe_results,

            sector_score,

            benchmark_close,

        )

        direction = "LONG"

        if regime_result.regime in (

            MarketRegime.BEAR,

            MarketRegime.STRONG_BEAR,

        ):

            direction = "SHORT"

        trade = self.trade_setup(

            direction,

            validation["adjusted_confidence"],

            regime_result.score,

        )

        volume_ratio = validation["volume"]["ratio"]

        synthesis = self.synthesize_decision(

            regime_result,

            validation,

            trade["risk_reward"],

            volume_ratio,

        )

        rejected, reject_reasons = self.reject_trade(

            regime_result,

            trade["risk_reward"],

            validation["volume"]["confirmed"],

        )

        decision = synthesis["decision"]

        if rejected:

            decision = TradingDecision.WATCH

        risk = self.determine_risk(

            synthesis["confidence"],

            regime_result.volatility.value,

        )

        entry_type = self.determine_entry_type(

            regime_result.regime,

        )

        reasons = self.generate_reasons(

            regime_result,

        )

        warnings = self.generate_warnings(

            regime_result,

            trade["risk_reward"],

        )

        warnings.extend(

            reject_reasons,

        )

        result = DecisionResult(

            symbol=self.symbol,

            decision=decision,

            entry_type=entry_type,

            confidence=synthesis["confidence"],

            score=synthesis["execution_score"],

            risk=risk,

            entry_price=trade["entry"],

            stop_loss=trade["optimized_stop"],

            target=trade["targets"]["T3"],

            risk_reward=trade["risk_reward"],

            reasons=reasons,

            warnings=warnings,

            metadata={

                "trade_setup": trade,

                "validation": validation,

                "recommendation": self.recommendation(

                    decision,

                ),

            },

        )

        self.result = result

        self.history.append(

            result,

        )

        return result

    # ==========================================================
    # EXPLAINABLE AI
    # ==========================================================

    def explain_decision(

        self,

        result: Optional[DecisionResult] = None,

    ) -> Dict:

        if result is None:

            result = self.result

        if result is None:

            return {}

        explanation = {

            "decision":

                result.decision.value,

            "confidence":

                result.confidence,

            "entry":

                result.entry_price,

            "stop":

                result.stop_loss,

            "target":

                result.target,

            "risk_reward":

                result.risk_reward,

            "why":

                list(result.reasons),

            "warnings":

                list(result.warnings),

        }

        return explanation

    # ==========================================================
    # AUDIT TRAIL
    # ==========================================================

    def audit_trail(

        self,

        result: Optional[DecisionResult] = None,

    ) -> Dict:

        if result is None:

            result = self.result

        if result is None:

            return {}

        return {

            "symbol":

                result.symbol,

            "timestamp":

                datetime.now().isoformat(),

            "decision":

                result.decision.value,

            "entry_type":

                result.entry_type.value,

            "confidence":

                result.confidence,

            "score":

                result.score,

            "risk":

                result.risk.value,

        }

    # ==========================================================
    # STRATEGY COMPATIBILITY
    # ==========================================================

    def strategy_compatibility(

        self,

        strategy_name: str,

        regime: MarketRegime,

    ) -> float:

        strategy = strategy_name.lower()

        if "trend" in strategy:

            if regime in (

                MarketRegime.BULL,

                MarketRegime.STRONG_BULL,

                MarketRegime.BEAR,

                MarketRegime.STRONG_BEAR,

            ):

                return 95.0

            return 45.0

        if "mean" in strategy:

            if regime == MarketRegime.SIDEWAYS:

                return 90.0

            return 40.0

        if "breakout" in strategy:

            if regime in (

                MarketRegime.STRONG_BULL,

                MarketRegime.STRONG_BEAR,

            ):

                return 95.0

            return 60.0

        return 70.0

    # ==========================================================
    # SIGNAL CONFLICT
    # ==========================================================

    def signal_conflict(

        self,

        decision: TradingDecision,

        regime: MarketRegime,

    ) -> bool:

        if decision in (

            TradingDecision.BUY,

            TradingDecision.STRONG_BUY,

        ):

            return regime in (

                MarketRegime.BEAR,

                MarketRegime.STRONG_BEAR,

            )

        if decision in (

            TradingDecision.SELL,

            TradingDecision.STRONG_SELL,

        ):

            return regime in (

                MarketRegime.BULL,

                MarketRegime.STRONG_BULL,

            )

        return False

    # ==========================================================
    # DECISION HISTORY
    # ==========================================================

    def decision_history(

        self,

    ) -> List[DecisionResult]:

        return list(

            self.history,

        )

    # ==========================================================
    # CLEAR HISTORY
    # ==========================================================

    def clear_history(

        self,

    ) -> None:

        self.history.clear()

    # ==========================================================
    # PERFORMANCE SUMMARY
    # ==========================================================

    def performance_summary(

        self,

    ) -> Dict:

        total = len(

            self.history,

        )

        buys = sum(

            1

            for x in self.history

            if x.decision in (

                TradingDecision.BUY,

                TradingDecision.STRONG_BUY,

            )

        )

        sells = sum(

            1

            for x in self.history

            if x.decision in (

                TradingDecision.SELL,

                TradingDecision.STRONG_SELL,

            )

        )

        watches = sum(

            1

            for x in self.history

            if x.decision == TradingDecision.WATCH

        )

        return {

            "total":

                total,

            "buy_signals":

                buys,

            "sell_signals":

                sells,

            "watch_signals":

                watches,

        }
        # ==========================================================
    # OPPORTUNITY SCORE
    # ==========================================================

    def opportunity_score(

        self,

        decision: DecisionResult,

    ) -> float:

        score = (

            decision.confidence * 0.40

            +

            decision.score * 0.35

            +

            min(

                decision.risk_reward,

                5.0,

            ) / 5.0 * 25

        )

        return round(

            min(

                score,

                100.0,

            ),

            2,

        )

    # ==========================================================
    # RANK OPPORTUNITIES
    # ==========================================================

    def rank_opportunities(

        self,

        decisions: List[DecisionResult],

    ) -> List[DecisionResult]:

        return sorted(

            decisions,

            key=lambda x: (

                self.opportunity_score(x),

                x.confidence,

                x.score,

            ),

            reverse=True,

        )

    # ==========================================================
    # CAPITAL DISTRIBUTION
    # ==========================================================

    def capital_distribution(

        self,

        capital: float,

        decisions: List[DecisionResult],

    ) -> List[Dict]:

        ranked = self.rank_opportunities(

            decisions,

        )

        total_score = sum(

            self.opportunity_score(

                d

            )

            for d in ranked

        )

        allocation = []

        if total_score <= 0:

            return allocation

        for item in ranked:

            weight = (

                self.opportunity_score(item)

                /

                total_score

            )

            allocation.append({

                "symbol":

                    item.symbol,

                "weight":

                    round(

                        weight * 100,

                        2,

                    ),

                "capital":

                    round(

                        capital * weight,

                        2,

                    ),

            })

        return allocation

    # ==========================================================
    # RISK BALANCER
    # ==========================================================

    def balance_risk(

        self,

        decisions: List[DecisionResult],

    ) -> Dict:

        risk_map = {

            RiskLevel.VERY_LOW: 1,

            RiskLevel.LOW: 2,

            RiskLevel.MEDIUM: 3,

            RiskLevel.HIGH: 4,

            RiskLevel.VERY_HIGH: 5,

        }

        values = [

            risk_map[d.risk]

            for d in decisions

        ]

        if not values:

            return {

                "average_risk": 0,

                "balanced": True,

            }

        average = np.mean(

            values,

        )

        return {

            "average_risk":

                round(

                    average,

                    2,

                ),

            "balanced":

                average <= 3,

        }

    # ==========================================================
    # SECTOR DIVERSIFICATION
    # ==========================================================

    def sector_diversification(

        self,

        positions: List[Dict],

    ) -> Dict:

        sectors = {}

        for position in positions:

            sector = position.get(

                "sector",

                "UNKNOWN",

            )

            sectors.setdefault(

                sector,

                0,

            )

            sectors[sector] += 1

        maximum = max(

            sectors.values(),

            default=0,

        )

        diversified = maximum <= 3

        return {

            "sector_distribution":

                sectors,

            "diversified":

                diversified,

        }

    # ==========================================================
    # CORRELATION MATRIX
    # ==========================================================

    def correlation_matrix(

        self,

        returns: pd.DataFrame,

    ) -> pd.DataFrame:

        return returns.corr()

    # ==========================================================
    # CORRELATION CHECK
    # ==========================================================

    def correlation_check(

        self,

        matrix: pd.DataFrame,

        threshold: float = 0.80,

    ) -> List[Tuple[str, str]]:

        conflicts = []

        columns = list(

            matrix.columns,

        )

        for i in range(

            len(columns),

        ):

            for j in range(

                i + 1,

                len(columns),

            ):

                value = matrix.iloc[

                    i,

                    j,

                ]

                if abs(

                    value,

                ) >= threshold:

                    conflicts.append(

                        (

                            columns[i],

                            columns[j],

                        )

                    )

        return conflicts

    # ==========================================================
    # PORTFOLIO SCORE
    # ==========================================================

    def portfolio_score(

        self,

        decisions: List[DecisionResult],

    ) -> float:

        if not decisions:

            return 0.0

        scores = [

            self.opportunity_score(

                d,

            )

            for d in decisions

        ]

        return round(

            float(

                np.mean(

                    scores,

                )

            ),

            2,

        )

    # ==========================================================
    # BUILD PORTFOLIO
    # ==========================================================

    def build_portfolio(

        self,

        capital: float,

        decisions: List[DecisionResult],

    ) -> Dict:

        ranked = self.rank_opportunities(

            decisions,

        )

        allocations = self.capital_distribution(

            capital,

            ranked,

        )

        risk = self.balance_risk(

            ranked,

        )

        return {

            "portfolio_score":

                self.portfolio_score(

                    ranked,

                ),

            "allocations":

                allocations,

            "risk":

                risk,

            "positions":

                len(

                    ranked,

                ),

        }
        # ==========================================================
    # OPPORTUNITY SCORE
    # ==========================================================

    def opportunity_score(

        self,

        decision: DecisionResult,

    ) -> float:

        score = (

            decision.confidence * 0.40

            +

            decision.score * 0.35

            +

            min(

                decision.risk_reward,

                5.0,

            ) / 5.0 * 25

        )

        return round(

            min(

                score,

                100.0,

            ),

            2,

        )

    # ==========================================================
    # RANK OPPORTUNITIES
    # ==========================================================

    def rank_opportunities(

        self,

        decisions: List[DecisionResult],

    ) -> List[DecisionResult]:

        return sorted(

            decisions,

            key=lambda x: (

                self.opportunity_score(x),

                x.confidence,

                x.score,

            ),

            reverse=True,

        )

    # ==========================================================
    # CAPITAL DISTRIBUTION
    # ==========================================================

    def capital_distribution(

        self,

        capital: float,

        decisions: List[DecisionResult],

    ) -> List[Dict]:

        ranked = self.rank_opportunities(

            decisions,

        )

        total_score = sum(

            self.opportunity_score(

                d

            )

            for d in ranked

        )

        allocation = []

        if total_score <= 0:

            return allocation

        for item in ranked:

            weight = (

                self.opportunity_score(item)

                /

                total_score

            )

            allocation.append({

                "symbol":

                    item.symbol,

                "weight":

                    round(

                        weight * 100,

                        2,

                    ),

                "capital":

                    round(

                        capital * weight,

                        2,

                    ),

            })

        return allocation

    # ==========================================================
    # RISK BALANCER
    # ==========================================================

    def balance_risk(

        self,

        decisions: List[DecisionResult],

    ) -> Dict:

        risk_map = {

            RiskLevel.VERY_LOW: 1,

            RiskLevel.LOW: 2,

            RiskLevel.MEDIUM: 3,

            RiskLevel.HIGH: 4,

            RiskLevel.VERY_HIGH: 5,

        }

        values = [

            risk_map[d.risk]

            for d in decisions

        ]

        if not values:

            return {

                "average_risk": 0,

                "balanced": True,

            }

        average = np.mean(

            values,

        )

        return {

            "average_risk":

                round(

                    average,

                    2,

                ),

            "balanced":

                average <= 3,

        }

    # ==========================================================
    # SECTOR DIVERSIFICATION
    # ==========================================================

    def sector_diversification(

        self,

        positions: List[Dict],

    ) -> Dict:

        sectors = {}

        for position in positions:

            sector = position.get(

                "sector",

                "UNKNOWN",

            )

            sectors.setdefault(

                sector,

                0,

            )

            sectors[sector] += 1

        maximum = max(

            sectors.values(),

            default=0,

        )

        diversified = maximum <= 3

        return {

            "sector_distribution":

                sectors,

            "diversified":

                diversified,

        }

    # ==========================================================
    # CORRELATION MATRIX
    # ==========================================================

    def correlation_matrix(

        self,

        returns: pd.DataFrame,

    ) -> pd.DataFrame:

        return returns.corr()

    # ==========================================================
    # CORRELATION CHECK
    # ==========================================================

    def correlation_check(

        self,

        matrix: pd.DataFrame,

        threshold: float = 0.80,

    ) -> List[Tuple[str, str]]:

        conflicts = []

        columns = list(

            matrix.columns,

        )

        for i in range(

            len(columns),

        ):

            for j in range(

                i + 1,

                len(columns),

            ):

                value = matrix.iloc[

                    i,

                    j,

                ]

                if abs(

                    value,

                ) >= threshold:

                    conflicts.append(

                        (

                            columns[i],

                            columns[j],

                        )

                    )

        return conflicts

    # ==========================================================
    # PORTFOLIO SCORE
    # ==========================================================

    def portfolio_score(

        self,

        decisions: List[DecisionResult],

    ) -> float:

        if not decisions:

            return 0.0

        scores = [

            self.opportunity_score(

                d,

            )

            for d in decisions

        ]

        return round(

            float(

                np.mean(

                    scores,

                )

            ),

            2,

        )

    # ==========================================================
    # BUILD PORTFOLIO
    # ==========================================================

    def build_portfolio(

        self,

        capital: float,

        decisions: List[DecisionResult],

    ) -> Dict:

        ranked = self.rank_opportunities(

            decisions,

        )

        allocations = self.capital_distribution(

            capital,

            ranked,

        )

        risk = self.balance_risk(

            ranked,

        )

        return {

            "portfolio_score":

                self.portfolio_score(

                    ranked,

                ),

            "allocations":

                allocations,

            "risk":

                risk,

            "positions":

                len(

                    ranked,

                ),

        }
        # ==========================================================
    # EXECUTE COMPLETE AI PIPELINE
    # ==========================================================

    def execute(
        self,
        regime_result,
        capital: float,
        timeframe_results: Dict[str, str],
        sector_score: float,
        benchmark_close: Optional[pd.Series] = None,
    ) -> DecisionResult:

        start_time = datetime.now()

        result = self.analyze_trade(
            regime_result=regime_result,
            capital=capital,
            timeframe_results=timeframe_results,
            sector_score=sector_score,
            benchmark_close=benchmark_close,
        )

        self.runtime_metrics = {
            "execution_time_ms": (
                datetime.now() - start_time
            ).total_seconds()
            * 1000,
            "generated_at": datetime.now().isoformat(),
        }

        return result

    # ==========================================================
    # SERIALIZE RESULT
    # ==========================================================

    def to_dict(
        self,
        result: Optional[DecisionResult] = None,
    ) -> Dict:

        if result is None:
            result = self.result

        if result is None:
            return {}

        return {

            "symbol": result.symbol,

            "decision": result.decision.value,

            "entry_type": result.entry_type.value,

            "confidence": result.confidence,

            "score": result.score,

            "risk": result.risk.value,

            "entry_price": result.entry_price,

            "stop_loss": result.stop_loss,

            "target": result.target,

            "risk_reward": result.risk_reward,

            "reasons": result.reasons,

            "warnings": result.warnings,

            "metadata": result.metadata,

        }

    # ==========================================================
    # DATAFRAME EXPORT
    # ==========================================================

    def to_dataframe(
        self,
        decisions: Optional[List[DecisionResult]] = None,
    ) -> pd.DataFrame:

        if decisions is None:
            decisions = self.history

        rows = []

        for item in decisions:

            rows.append({

                "Symbol": item.symbol,

                "Decision": item.decision.value,

                "Confidence": item.confidence,

                "Score": item.score,

                "Risk": item.risk.value,

                "Entry": item.entry_price,

                "SL": item.stop_loss,

                "Target": item.target,

                "RR": item.risk_reward,

            })

        return pd.DataFrame(rows)

    # ==========================================================
    # JSON EXPORT
    # ==========================================================

    def export_json(
        self,
        path: str,
    ) -> None:

        data = [

            self.to_dict(item)

            for item in self.history

        ]

        with open(

            path,

            "w",

            encoding="utf-8",

        ) as f:

            json.dump(

                data,

                f,

                indent=4,

            )

    # ==========================================================
    # CSV EXPORT
    # ==========================================================

    def export_csv(
        self,
        path: str,
    ) -> None:

        self.to_dataframe().to_csv(

            path,

            index=False,

        )

    # ==========================================================
    # SAVE HISTORY
    # ==========================================================

    def save_history(
        self,
        path: str,
    ) -> None:

        self.export_json(path)

    # ==========================================================
    # LOAD HISTORY
    # ==========================================================

    def load_history(
        self,
        path: str,
    ) -> List[Dict]:

        with open(

            path,

            "r",

            encoding="utf-8",

        ) as f:

            return json.load(f)

    # ==========================================================
    # SIMPLE LOGGER
    # ==========================================================

    def log(
        self,
        message: str,
    ) -> None:

        timestamp = datetime.now().strftime(

            "%H:%M:%S",

        )

        print(

            f"[{timestamp}] {message}"

        )

    # ==========================================================
    # ENGINE STATUS
    # ==========================================================

    def status(self) -> Dict:

        return {

            "symbol": self.symbol,

            "loaded": self.data is not None,

            "history": len(

                self.history,

            ),

            "runtime": getattr(

                self,

                "runtime_metrics",

                {},

            ),

        }

    # ==========================================================
    # RESET ENGINE
    # ==========================================================

    def reset(self) -> None:

        self.clear()

        self.clear_history()

        self.runtime_metrics = {}

    # ==========================================================
    # VERSION
    # ==========================================================

    @staticmethod
    def version() -> str:

        return "StockVersity AI Decision Engine v4.0"

    # ==========================================================
    # END OF FILE
    # ==========================================================