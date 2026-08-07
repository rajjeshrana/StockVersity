"""
==========================================================
StockVersity Scanner Pro
AI Risk Management Engine
Version : 4.0
Powered by AI
==========================================================
"""

from __future__ import annotations

import math
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np
import pandas as pd


# ==========================================================
# RISK RESULT
# ==========================================================

@dataclass
class RiskResult:

    symbol: str = ""

    capital: float = 0.0

    entry_price: float = 0.0

    stop_loss: float = 0.0

    target_price: float = 0.0

    risk_per_share: float = 0.0

    reward_per_share: float = 0.0

    risk_reward: float = 0.0

    position_size: int = 0

    capital_required: float = 0.0

    risk_amount: float = 0.0

    portfolio_risk: float = 0.0

    exposure: float = 0.0

    confidence_score: float = 0.0

    risk_grade: str = ""

    recommendation: str = ""

    warnings: List[str] = field(default_factory=list)

    metrics: Dict = field(default_factory=dict)


# ==========================================================
# AI RISK MANAGEMENT ENGINE
# ==========================================================

class RiskManagementEngine:

    def __init__(

        self,

        capital: float = 100000.0,

        risk_percent: float = 1.0,

        max_portfolio_risk: float = 5.0,

    ):

        self.capital = float(capital)

        self.risk_percent = float(risk_percent)

        self.max_portfolio_risk = float(max_portfolio_risk)

        self.trade = {}

        self.result = None

    # ======================================================
    # LOAD TRADE
    # ======================================================

    def load_trade(

        self,

        symbol: str,

        entry: float,

        stop: float,

        target: float,

    ):

        self.trade = {

            "symbol": symbol,

            "entry": float(entry),

            "stop": float(stop),

            "target": float(target),

        }

        return self

    # ======================================================
    # VALIDATION
    # ======================================================

    def validate(

        self,

    ) -> bool:

        if not self.trade:

            return False

        if self.trade["entry"] <= 0:

            return False

        if self.trade["stop"] <= 0:

            return False

        if self.trade["target"] <= 0:

            return False

        return True

    # ======================================================
    # RESET
    # ======================================================

    def reset(

        self,

    ):

        self.trade = {}

        self.result = None

    # ======================================================
    # RISK AMOUNT
    # ======================================================

    def risk_amount(

        self,

    ) -> float:

        return round(

            self.capital *

            self.risk_percent /

            100,

            2,

        )

    # ======================================================
    # MAX PORTFOLIO RISK
    # ======================================================

    def maximum_portfolio_risk(

        self,

    ) -> float:

        return round(

            self.capital *

            self.max_portfolio_risk /

            100,

            2,

        )

    # ======================================================
    # ENTRY PRICE
    # ======================================================

    @property
    def entry(

        self,

    ) -> float:

        return self.trade.get(

            "entry",

            0,

        )

    # ======================================================
    # STOP LOSS
    # ======================================================

    @property
    def stop(

        self,

    ) -> float:

        return self.trade.get(

            "stop",

            0,

        )

    # ======================================================
    # TARGET
    # ======================================================

    @property
    def target(

        self,

    ) -> float:

        return self.trade.get(

            "target",

            0,

        )

    # ======================================================
    # SYMBOL
    # ======================================================

    @property
    def symbol(

        self,

    ) -> str:

        return self.trade.get(

            "symbol",

            "",

        )
        # ======================================================
    # RISK PER SHARE
    # ======================================================

    def risk_per_share(

        self,

    ) -> float:

        if not self.validate():

            return 0.0

        return round(

            abs(

                self.entry -

                self.stop

            ),

            2,

        )

    # ======================================================
    # REWARD PER SHARE
    # ======================================================

    def reward_per_share(

        self,

    ) -> float:

        if not self.validate():

            return 0.0

        return round(

            abs(

                self.target -

                self.entry

            ),

            2,

        )

    # ======================================================
    # RISK REWARD RATIO
    # ======================================================

    def risk_reward_ratio(

        self,

    ) -> float:

        risk = self.risk_per_share()

        reward = self.reward_per_share()

        if risk == 0:

            return 0.0

        return round(

            reward /

            risk,

            2,

        )

    # ======================================================
    # POSITION SIZE
    # ======================================================

    def position_size(

        self,

    ) -> int:

        risk = self.risk_per_share()

        if risk <= 0:

            return 0

        quantity = math.floor(

            self.risk_amount() /

            risk

        )

        return max(

            quantity,

            0,

        )

    # ======================================================
    # CAPITAL REQUIRED
    # ======================================================

    def capital_required(

        self,

    ) -> float:

        qty = self.position_size()

        capital = qty * self.entry

        return round(

            capital,

            2,

        )

    # ======================================================
    # EXPOSURE PERCENTAGE
    # ======================================================

    def exposure_percentage(

        self,

    ) -> float:

        if self.capital <= 0:

            return 0.0

        exposure = (

            self.capital_required()

            /

            self.capital

        ) * 100

        return round(

            exposure,

            2,

        )

    # ======================================================
    # PORTFOLIO RISK
    # ======================================================

    def portfolio_risk(

        self,

    ) -> float:

        capital = self.capital_required()

        if self.capital <= 0:

            return 0.0

        risk = (

            capital

            /

            self.capital

        ) * 100

        return round(

            risk,

            2,

        )

    # ======================================================
    # RISK GRADE
    # ======================================================

    def risk_grade(

        self,

    ) -> str:

        rr = self.risk_reward_ratio()

        exposure = self.exposure_percentage()

        if rr >= 3.0 and exposure <= 30:

            return "A+"

        elif rr >= 2.5 and exposure <= 40:

            return "A"

        elif rr >= 2.0 and exposure <= 50:

            return "B"

        elif rr >= 1.5 and exposure <= 70:

            return "C"

        return "D"

    # ======================================================
    # RISK STATUS
    # ======================================================

    def risk_status(

        self,

    ) -> Dict:

        return {

            "risk_amount":

                self.risk_amount(),

            "risk_per_share":

                self.risk_per_share(),

            "reward_per_share":

                self.reward_per_share(),

            "risk_reward":

                self.risk_reward_ratio(),

            "position_size":

                self.position_size(),

            "capital_required":

                self.capital_required(),

            "portfolio_risk":

                self.portfolio_risk(),

            "exposure":

                self.exposure_percentage(),

            "grade":

                self.risk_grade(),

        }    # ======================================================
    # FIXED RISK POSITION SIZING
    # ======================================================

    def fixed_risk_position_size(

        self,

    ) -> Dict:

        quantity = self.position_size()

        return {

            "method": "Fixed Risk",

            "quantity": quantity,

            "risk_amount": self.risk_amount(),

            "capital_required": self.capital_required(),

        }

    # ======================================================
    # PERCENTAGE CAPITAL POSITION SIZING
    # ======================================================

    def percentage_capital_position(

        self,

        capital_percent: float = 20.0,

    ) -> Dict:

        allocation = (

            self.capital *

            capital_percent /

            100

        )

        quantity = math.floor(

            allocation /

            self.entry

        )

        invested = quantity * self.entry

        return {

            "method": "Capital Allocation",

            "capital_percent": capital_percent,

            "allocated_capital": round(

                allocation,

                2,

            ),

            "quantity": quantity,

            "investment": round(

                invested,

                2,

            ),

        }

    # ======================================================
    # ATR POSITION SIZING
    # ======================================================

    def atr_position_size(

        self,

        atr: float,

        atr_multiple: float = 2.0,

    ) -> Dict:

        if atr <= 0:

            return {}

        stop_distance = atr * atr_multiple

        quantity = math.floor(

            self.risk_amount()

            /

            stop_distance

        )

        investment = quantity * self.entry

        return {

            "method": "ATR",

            "atr": round(

                atr,

                2,

            ),

            "multiple": atr_multiple,

            "stop_distance": round(

                stop_distance,

                2,

            ),

            "quantity": quantity,

            "investment": round(

                investment,

                2,

            ),

        }

    # ======================================================
    # VOLATILITY POSITION SIZING
    # ======================================================

    def volatility_position_size(

        self,

        volatility_percent: float,

    ) -> Dict:

        if volatility_percent <= 0:

            return {}

        adjustment = max(

            0.25,

            1 -

            volatility_percent /

            100,

        )

        quantity = math.floor(

            self.position_size()

            *

            adjustment

        )

        return {

            "method": "Volatility",

            "volatility_percent": round(

                volatility_percent,

                2,

            ),

            "adjustment_factor": round(

                adjustment,

                2,

            ),

            "quantity": quantity,

        }

    # ======================================================
    # MAXIMUM SHARES
    # ======================================================

    def maximum_shares(

        self,

    ) -> int:

        if self.entry <= 0:

            return 0

        return math.floor(

            self.capital /

            self.entry

        )

    # ======================================================
    # LOT SIZE ADJUSTMENT
    # ======================================================

    def adjust_lot_size(

        self,

        lot_size: int,

    ) -> Dict:

        if lot_size <= 0:

            return {}

        quantity = self.position_size()

        adjusted = (

            quantity //

            lot_size

        ) * lot_size

        return {

            "lot_size": lot_size,

            "recommended_quantity": quantity,

            "adjusted_quantity": adjusted,

        }

    # ======================================================
    # MARGIN REQUIREMENT
    # ======================================================

    def margin_requirement(

        self,

        leverage: float = 1.0,

    ) -> Dict:

        if leverage <= 0:

            leverage = 1

        required = (

            self.capital_required()

            /

            leverage

        )

        return {

            "leverage": leverage,

            "margin_required": round(

                required,

                2,

            ),

        }

    # ======================================================
    # LIQUIDITY POSITION LIMIT
    # ======================================================

    def liquidity_limit(

        self,

        average_volume: int,

        participation_rate: float = 0.02,

    ) -> Dict:

        if average_volume <= 0:

            return {}

        limit = math.floor(

            average_volume *

            participation_rate

        )

        recommended = min(

            limit,

            self.position_size(),

        )

        return {

            "average_volume": average_volume,

            "participation_rate": participation_rate,

            "maximum_quantity": limit,

            "recommended_quantity": recommended,

        }

    # ======================================================
    # POSITION SIZING SUMMARY
    # ======================================================

    def position_sizing_summary(

        self,

        atr: Optional[float] = None,

        volatility_percent: Optional[float] = None,

    ) -> Dict:

        summary = {

            "fixed_risk":

                self.fixed_risk_position_size(),

            "capital_allocation":

                self.percentage_capital_position(),

            "maximum_shares":

                self.maximum_shares(),

        }

        if atr is not None:

            summary["atr"] = self.atr_position_size(

                atr,

            )

        if volatility_percent is not None:

            summary["volatility"] = self.volatility_position_size(

                volatility_percent,

            )

        return summary
        # ======================================================
    # KELLY CRITERION POSITION SIZING
    # ======================================================

    def kelly_criterion(

        self,

        win_rate: float,

        risk_reward: Optional[float] = None,

    ) -> Dict:

        rr = risk_reward or self.risk_reward_ratio()

        if rr <= 0:

            return {}

        win_probability = win_rate / 100

        loss_probability = 1 - win_probability

        kelly = (

            (rr * win_probability)

            -

            loss_probability

        ) / rr

        kelly = max(

            0,

            min(

                kelly,

                1,

            ),

        )

        allocation = self.capital * kelly

        quantity = math.floor(

            allocation /

            self.entry

        )

        return {

            "method": "Kelly Criterion",

            "win_rate": round(

                win_rate,

                2,

            ),

            "risk_reward": rr,

            "kelly_fraction": round(

                kelly,

                4,

            ),

            "capital_allocation": round(

                allocation,

                2,

            ),

            "quantity": quantity,

        }

    # ======================================================
    # OPTIMAL F
    # ======================================================

    def optimal_f(

        self,

        max_loss_percent: float,

    ) -> Dict:

        if max_loss_percent <= 0:

            return {}

        optimal = min(

            self.risk_percent /

            max_loss_percent,

            1,

        )

        allocation = self.capital * optimal

        quantity = math.floor(

            allocation /

            self.entry

        )

        return {

            "method": "Optimal F",

            "optimal_fraction": round(

                optimal,

                4,

            ),

            "capital_allocation": round(

                allocation,

                2,

            ),

            "quantity": quantity,

        }

    # ======================================================
    # VALUE AT RISK (VaR)
    # ======================================================

    def value_at_risk(

        self,

        confidence: float = 95,

        volatility: float = 2.0,

        holding_days: int = 1,

    ) -> Dict:

        z_scores = {

            90: 1.28,

            95: 1.65,

            99: 2.33,

        }

        z = z_scores.get(

            int(confidence),

            1.65,

        )

        exposure = self.capital_required()

        var = (

            exposure *

            (volatility / 100)

            *

            z

            *

            math.sqrt(

                holding_days

            )

        )

        return {

            "confidence": confidence,

            "holding_days": holding_days,

            "volatility": volatility,

            "var": round(

                var,

                2,

            ),

        }

    # ======================================================
    # EXPECTED DRAWDOWN
    # ======================================================

    def expected_drawdown(

        self,

        losing_streak: int = 5,

    ) -> Dict:

        drawdown = (

            self.risk_amount()

            *

            losing_streak

        )

        percentage = (

            drawdown /

            self.capital

        ) * 100

        return {

            "losing_streak": losing_streak,

            "drawdown_amount": round(

                drawdown,

                2,

            ),

            "drawdown_percent": round(

                percentage,

                2,

            ),

        }

    # ======================================================
    # MAXIMUM DRAWDOWN
    # ======================================================

    def maximum_drawdown(

        self,

        trade_history: Optional[List[float]] = None,

    ) -> Dict:

        if not trade_history:

            return {

                "max_drawdown": 0,

                "drawdown_percent": 0,

            }

        equity = np.cumsum(

            trade_history

        )

        peak = np.maximum.accumulate(

            equity

        )

        drawdown = peak - equity

        max_dd = float(

            np.max(drawdown)

        )

        peak_value = max(

            peak.max(),

            1,

        )

        percent = (

            max_dd /

            peak_value

        ) * 100

        return {

            "max_drawdown": round(

                max_dd,

                2,

            ),

            "drawdown_percent": round(

                percent,

                2,

            ),

        }

    # ======================================================
    # MONTE CARLO RISK PROJECTION
    # ======================================================

    def monte_carlo_projection(

        self,

        win_rate: float,

        simulations: int = 1000,

    ) -> Dict:

        rr = max(

            self.risk_reward_ratio(),

            1,

        )

        profits = []

        for _ in range(simulations):

            if np.random.random() <= win_rate / 100:

                profits.append(

                    self.reward_per_share()

                )

            else:

                profits.append(

                    -self.risk_per_share()

                )

        expectancy = np.mean(

            profits

        )

        probability = (

            np.sum(

                np.array(profits) > 0

            )

            /

            simulations

        ) * 100

        return {

            "expectancy": round(

                expectancy,

                2,

            ),

            "positive_probability": round(

                probability,

                2,

            ),

            "risk_reward": rr,

        }

    # ======================================================
    # PROBABILITY OF RUIN
    # ======================================================

    def probability_of_ruin(

        self,

        win_rate: float,

    ) -> Dict:

        edge = (

            win_rate - 50

        ) / 50

        edge = max(

            edge,

            -0.99,

        )

        ruin = (

            (1 - edge)

            **

            (

                self.capital /

                max(

                    self.risk_amount(),

                    1,

                )

            )

        )

        ruin = min(

            ruin,

            1,

        )

        return {

            "probability": round(

                ruin * 100,

                4,

            ),

            "safe": ruin < 0.05,

        }

    # ======================================================
    # CAPITAL PRESERVATION ENGINE
    # ======================================================

    def capital_preservation(

        self,

    ) -> Dict:

        exposure = self.exposure_percentage()

        grade = self.risk_grade()

        recommendation = "Maintain"

        if exposure > 75:

            recommendation = "Reduce Position"

        elif exposure < 30:

            recommendation = "Can Increase"

        return {

            "capital": self.capital,

            "risk_amount": self.risk_amount(),

            "exposure": exposure,

            "risk_grade": grade,

            "recommendation": recommendation,

        }
        # ======================================================
    # ATR STOP LOSS
    # ======================================================

    def atr_stop_loss(

        self,

        atr: float,

        multiplier: float = 2.0,

        direction: str = "LONG",

    ) -> Dict:

        if atr <= 0:

            return {}

        direction = direction.upper()

        distance = atr * multiplier

        if direction == "LONG":

            stop = self.entry - distance

        else:

            stop = self.entry + distance

        return {

            "method": "ATR",

            "direction": direction,

            "atr": round(atr, 2),

            "multiplier": multiplier,

            "stop_loss": round(stop, 2),

            "distance": round(distance, 2),

        }

    # ======================================================
    # SWING STOP LOSS
    # ======================================================

    def swing_stop_loss(

        self,

        swing_price: float,

        buffer_percent: float = 0.25,

        direction: str = "LONG",

    ) -> Dict:

        direction = direction.upper()

        buffer = swing_price * buffer_percent / 100

        if direction == "LONG":

            stop = swing_price - buffer

        else:

            stop = swing_price + buffer

        return {

            "method": "Swing",

            "direction": direction,

            "swing_price": round(swing_price, 2),

            "buffer_percent": buffer_percent,

            "stop_loss": round(stop, 2),

        }

    # ======================================================
    # MOVING AVERAGE STOP LOSS
    # ======================================================

    def moving_average_stop(

        self,

        moving_average: float,

        buffer_percent: float = 0.30,

        direction: str = "LONG",

    ) -> Dict:

        direction = direction.upper()

        buffer = moving_average * buffer_percent / 100

        if direction == "LONG":

            stop = moving_average - buffer

        else:

            stop = moving_average + buffer

        return {

            "method": "Moving Average",

            "direction": direction,

            "moving_average": round(

                moving_average,

                2,

            ),

            "stop_loss": round(stop, 2),

        }

    # ======================================================
    # CHANDELIER EXIT
    # ======================================================

    def chandelier_exit(

        self,

        highest_high: float,

        atr: float,

        multiplier: float = 3.0,

        direction: str = "LONG",

    ) -> Dict:

        direction = direction.upper()

        if direction == "LONG":

            stop = highest_high - atr * multiplier

        else:

            stop = highest_high + atr * multiplier

        return {

            "method": "Chandelier",

            "direction": direction,

            "highest_high": round(

                highest_high,

                2,

            ),

            "atr": round(

                atr,

                2,

            ),

            "multiplier": multiplier,

            "stop_loss": round(stop, 2),

        }

    # ======================================================
    # VOLATILITY STOP
    # ======================================================

    def volatility_stop(

        self,

        volatility_percent: float,

        direction: str = "LONG",

    ) -> Dict:

        direction = direction.upper()

        distance = (

            self.entry *

            volatility_percent /

            100

        )

        if direction == "LONG":

            stop = self.entry - distance

        else:

            stop = self.entry + distance

        return {

            "method": "Volatility",

            "direction": direction,

            "volatility_percent": volatility_percent,

            "stop_loss": round(stop, 2),

        }

    # ======================================================
    # TIME STOP
    # ======================================================

    def time_stop(

        self,

        maximum_bars: int,

    ) -> Dict:

        return {

            "method": "Time Stop",

            "maximum_bars": maximum_bars,

            "action":

                "Exit trade if target or stop is not hit.",

        }

    # ======================================================
    # TRAILING STOP LOSS
    # ======================================================

    def trailing_stop(

        self,

        current_price: float,

        trailing_percent: float = 2.0,

        direction: str = "LONG",

    ) -> Dict:

        direction = direction.upper()

        trail = (

            current_price *

            trailing_percent /

            100

        )

        if direction == "LONG":

            stop = current_price - trail

        else:

            stop = current_price + trail

        return {

            "method": "Trailing",

            "direction": direction,

            "current_price": round(

                current_price,

                2,

            ),

            "trailing_percent": trailing_percent,

            "stop_loss": round(stop, 2),

        }

    # ======================================================
    # AI STOP LOSS RECOMMENDATION
    # ======================================================

    def ai_stop_loss(

        self,

        atr: float,

        swing_price: float,

        moving_average: float,

        volatility_percent: float,

        direction: str = "LONG",

    ) -> Dict:

        atr_stop = self.atr_stop_loss(

            atr,

            direction=direction,

        )

        swing_stop = self.swing_stop_loss(

            swing_price,

            direction=direction,

        )

        ma_stop = self.moving_average_stop(

            moving_average,

            direction=direction,

        )

        volatility_stop = self.volatility_stop(

            volatility_percent,

            direction=direction,

        )

        candidates = [

            atr_stop["stop_loss"],

            swing_stop["stop_loss"],

            ma_stop["stop_loss"],

            volatility_stop["stop_loss"],

        ]

        if direction.upper() == "LONG":

            recommended = max(candidates)

        else:

            recommended = min(candidates)

        return {

            "recommended_stop": round(

                recommended,

                2,

            ),

            "atr": atr_stop,

            "swing": swing_stop,

            "moving_average": ma_stop,

            "volatility": volatility_stop,

        }
        # ======================================================
    # FIXED RISK : REWARD TARGETS
    # ======================================================

    def fixed_rr_targets(

        self,

        direction: str = "LONG",

    ) -> Dict:

        direction = direction.upper()

        risk = self.risk_per_share()

        if risk <= 0:

            return {}

        if direction == "LONG":

            targets = {

                "1R": self.entry + risk,

                "2R": self.entry + (risk * 2),

                "3R": self.entry + (risk * 3),

                "5R": self.entry + (risk * 5),

            }

        else:

            targets = {

                "1R": self.entry - risk,

                "2R": self.entry - (risk * 2),

                "3R": self.entry - (risk * 3),

                "5R": self.entry - (risk * 5),

            }

        return {

            "method": "Fixed Risk Reward",

            "targets": {

                key: round(value, 2)

                for key, value in targets.items()

            },

        }

    # ======================================================
    # ATR TARGET
    # ======================================================

    def atr_target(

        self,

        atr: float,

        multiplier: float = 3.0,

        direction: str = "LONG",

    ) -> Dict:

        direction = direction.upper()

        distance = atr * multiplier

        if direction == "LONG":

            target = self.entry + distance

        else:

            target = self.entry - distance

        return {

            "method": "ATR",

            "atr": round(atr, 2),

            "multiplier": multiplier,

            "target": round(target, 2),

        }

    # ==================================