"""
=========================================================
StockVersity Scanner Pro
Risk Manager
Version : 2.0
=========================================================

Central risk-management engine.

Responsibilities
----------------
• Calculate risk per trade
• Calculate risk per share
• Calculate position size
• Calculate capital required
• Calculate stop-loss percentage
• Calculate risk/reward
• Generate targets
• Validate trade risk
• Apply capital exposure limits
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from math import floor
from math import isfinite

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from core.scanner.config import RiskConfig
from core.scanner.config import scanner_config

from core.scanner.signal import SignalType


# =========================================================
# RISK RESULT
# =========================================================

@dataclass(slots=True)
class RiskResult:
    """
    Result of a complete risk calculation.
    """

    valid: bool = False

    entry: float = 0.0

    stop_loss: float = 0.0

    risk_per_share: float = 0.0

    stop_percent: float = 0.0

    account_risk: float = 0.0

    quantity: int = 0

    capital_required: float = 0.0

    actual_risk: float = 0.0

    target1: float = 0.0

    target2: float = 0.0

    target3: float = 0.0

    risk_reward: float = 0.0

    reason: str = ""

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "valid":
                self.valid,

            "entry":
                self.entry,

            "stop_loss":
                self.stop_loss,

            "risk_per_share":
                self.risk_per_share,

            "stop_percent":
                self.stop_percent,

            "account_risk":
                self.account_risk,

            "quantity":
                self.quantity,

            "capital_required":
                self.capital_required,

            "actual_risk":
                self.actual_risk,

            "target1":
                self.target1,

            "target2":
                self.target2,

            "target3":
                self.target3,

            "risk_reward":
                self.risk_reward,

            "reason":
                self.reason,
        }


# =========================================================
# RISK MANAGER
# =========================================================

class RiskManager:
    """
    Central StockVersity risk-management engine.
    """

    def __init__(
        self,
        config: Optional[RiskConfig] = None,
    ) -> None:

        self.config = (
            config
            if config is not None
            else scanner_config.risk
        )

    # =====================================================
    # SAFE NUMBER
    # =====================================================

    @staticmethod
    def _number(
        value: Any,
    ) -> bool:

        try:

            return isfinite(
                float(value)
            )

        except (
            TypeError,
            ValueError,
        ):

            return False

    # =====================================================
    # ACCOUNT RISK
    # =====================================================

    def account_risk(
        self,
        capital: Optional[float] = None,
        risk_percent: Optional[float] = None,
    ) -> float:
        """
        Maximum rupee risk permitted for one trade.
        """

        capital_value = (
            self.config.capital
            if capital is None
            else float(capital)
        )

        percent = (
            self.config.risk_percent
            if risk_percent is None
            else float(risk_percent)
        )

        if (
            capital_value <= 0
            or percent <= 0
        ):
            return 0.0

        return round(
            capital_value
            * percent
            / 100.0,
            2,
        )

    # =====================================================
    # RISK PER SHARE
    # =====================================================

    @staticmethod
    def risk_per_share(
        entry: float,
        stop_loss: float,
    ) -> float:

        if (
            entry <= 0
            or stop_loss <= 0
        ):
            return 0.0

        return round(
            abs(
                entry
                - stop_loss
            ),
            4,
        )

    # =====================================================
    # STOP PERCENT
    # =====================================================

    @classmethod
    def stop_percent(
        cls,
        entry: float,
        stop_loss: float,
    ) -> float:

        if entry <= 0:
            return 0.0

        risk = cls.risk_per_share(
            entry,
            stop_loss,
        )

        return round(
            risk
            / entry
            * 100.0,
            4,
        )

    # =====================================================
    # POSITION SIZE
    # =====================================================

    def position_size(
        self,
        entry: float,
        stop_loss: float,
        *,
        capital: Optional[float] = None,
        risk_percent: Optional[float] = None,
        maximum_capital: Optional[float] = None,
    ) -> int:
        """
        Calculate quantity using account risk and
        available capital.
        """

        if (
            not self._number(entry)
            or not self._number(stop_loss)
        ):
            return 0

        entry = float(entry)

        stop_loss = float(
            stop_loss
        )

        if (
            entry <= 0
            or stop_loss <= 0
        ):
            return 0

        risk_share = (
            self.risk_per_share(
                entry,
                stop_loss,
            )
        )

        if risk_share <= 0:
            return 0

        allowed_risk = (
            self.account_risk(
                capital,
                risk_percent,
            )
        )

        if allowed_risk <= 0:
            return 0

        risk_quantity = floor(
            allowed_risk
            / risk_share
        )

        capital_value = (
            self.config.capital
            if capital is None
            else float(capital)
        )

        if maximum_capital is not None:

            capital_value = min(
                capital_value,
                float(maximum_capital),
            )

        if capital_value <= 0:
            return 0

        capital_quantity = floor(
            capital_value
            / entry
        )

        quantity = min(
            risk_quantity,
            capital_quantity,
        )

        return max(
            0,
            quantity,
        )

    # =====================================================
    # CAPITAL REQUIRED
    # =====================================================

    @staticmethod
    def capital_required(
        entry: float,
        quantity: int,
    ) -> float:

        if (
            entry <= 0
            or quantity <= 0
        ):
            return 0.0

        return round(
            entry
            * quantity,
            2,
        )

    # =====================================================
    # ACTUAL RISK
    # =====================================================

    @classmethod
    def actual_risk(
        cls,
        entry: float,
        stop_loss: float,
        quantity: int,
    ) -> float:

        if quantity <= 0:
            return 0.0

        return round(
            cls.risk_per_share(
                entry,
                stop_loss,
            )
            * quantity,
            2,
        )

    # =====================================================
    # RISK REWARD
    # =====================================================

    @classmethod
    def risk_reward(
        cls,
        entry: float,
        stop_loss: float,
        target: float,
    ) -> float:

        risk = cls.risk_per_share(
            entry,
            stop_loss,
        )

        if (
            risk <= 0
            or target <= 0
        ):
            return 0.0

        reward = abs(
            target
            - entry
        )

        return round(
            reward / risk,
            2,
        )

    # =====================================================
    # TARGET
    # =====================================================

    @classmethod
    def target_for_rr(
        cls,
        signal_type: SignalType,
        entry: float,
        stop_loss: float,
        rr: float,
    ) -> float:
        """
        Calculate target price for required R:R.
        """

        if (
            entry <= 0
            or stop_loss <= 0
            or rr <= 0
        ):
            return 0.0

        risk = cls.risk_per_share(
            entry,
            stop_loss,
        )

        if risk <= 0:
            return 0.0

        if signal_type == SignalType.BUY:

            return round(
                entry
                + risk * rr,
                2,
            )

        if signal_type == SignalType.SELL:

            return round(
                entry
                - risk * rr,
                2,
            )

        return 0.0

    # =====================================================
    # TARGETS
    # =====================================================

    def targets(
        self,
        signal_type: SignalType,
        entry: float,
        stop_loss: float,
        *,
        ratios: Optional[List[float]] = None,
    ) -> List[float]:
        """
        Generate multiple R:R targets.
        """

        if ratios is None:

            ratios = [
                self.config.minimum_rr,
                self.config.preferred_rr,
                4.0,
            ]

        targets: List[float] = []

        for rr in ratios:

            target = (
                self.target_for_rr(
                    signal_type,
                    entry,
                    stop_loss,
                    rr,
                )
            )

            if target > 0:

                targets.append(
                    target
                )

        return targets

    # =====================================================
    # PRICE STRUCTURE
    # =====================================================

    @staticmethod
    def valid_price_structure(
        signal_type: SignalType,
        entry: float,
        stop_loss: float,
    ) -> bool:

        if (
            entry <= 0
            or stop_loss <= 0
        ):
            return False

        if signal_type == SignalType.BUY:

            return (
                stop_loss
                < entry
            )

        if signal_type == SignalType.SELL:

            return (
                stop_loss
                > entry
            )

        return False

    # =====================================================
    # STOP VALIDATION
    # =====================================================

    def valid_stop(
        self,
        entry: float,
        stop_loss: float,
    ) -> bool:

        percent = (
            self.stop_percent(
                entry,
                stop_loss,
            )
        )

        return (
            self.config.minimum_stop_percent
            <= percent
            <= self.config.maximum_stop_percent
        )

    # =====================================================
    # COMPLETE CALCULATION
    # =====================================================

    def calculate(
        self,
        signal_type: SignalType,
        entry: float,
        stop_loss: float,
        *,
        capital: Optional[float] = None,
        risk_percent: Optional[float] = None,
        target_rr: Optional[float] = None,
    ) -> RiskResult:
        """
        Perform complete trade risk calculation.
        """

        result = RiskResult(

            entry=float(entry),

            stop_loss=float(
                stop_loss
            ),
        )

        # ---------------------------------------------
        # PRICE STRUCTURE
        # ---------------------------------------------

        if not self.valid_price_structure(
            signal_type,
            entry,
            stop_loss,
        ):

            result.reason = (
                "Invalid entry / stop-loss structure."
            )

            return result

        # ---------------------------------------------
        # STOP DISTANCE
        # ---------------------------------------------

        risk_share = (
            self.risk_per_share(
                entry,
                stop_loss,
            )
        )

        stop_percent = (
            self.stop_percent(
                entry,
                stop_loss,
            )
        )

        result.risk_per_share = (
            risk_share
        )

        result.stop_percent = (
            stop_percent
        )

        if not self.valid_stop(
            entry,
            stop_loss,
        ):

            result.reason = (

                f"Stop distance "
                f"{stop_percent:.2f}% outside "
                f"allowed range "
                f"{self.config.minimum_stop_percent:.2f}%"
                f" - "
                f"{self.config.maximum_stop_percent:.2f}%."
            )

            return result

        # ---------------------------------------------
        # ACCOUNT RISK
        # ---------------------------------------------

        allowed_risk = (
            self.account_risk(
                capital,
                risk_percent,
            )
        )

        result.account_risk = (
            allowed_risk
        )

        # ---------------------------------------------
        # QUANTITY
        # ---------------------------------------------

        quantity = (
            self.position_size(
                entry,
                stop_loss,
                capital=capital,
                risk_percent=risk_percent,
            )
        )

        result.quantity = quantity

        if quantity <= 0:

            result.reason = (
                "Position size is zero."
            )

            return result

        # ---------------------------------------------
        # CAPITAL
        # ---------------------------------------------

        result.capital_required = (
            self.capital_required(
                entry,
                quantity,
            )
        )

        result.actual_risk = (
            self.actual_risk(
                entry,
                stop_loss,
                quantity,
            )
        )

        # ---------------------------------------------
        # TARGETS
        # ---------------------------------------------

        rr = (
            self.config.minimum_rr
            if target_rr is None
            else float(target_rr)
        )

        result.target1 = (
            self.target_for_rr(
                signal_type,
                entry,
                stop_loss,
                rr,
            )
        )

        result.target2 = (
            self.target_for_rr(
                signal_type,
                entry,
                stop_loss,
                max(
                    rr + 1.0,
                    self.config.preferred_rr,
                ),
            )
        )

        result.target3 = (
            self.target_for_rr(
                signal_type,
                entry,
                stop_loss,
                max(
                    rr + 2.0,
                    4.0,
                ),
            )
        )

        result.risk_reward = (
            self.risk_reward(
                entry,
                stop_loss,
                result.target1,
            )
        )

        if (
            result.risk_reward
            < self.config.minimum_rr
        ):

            result.reason = (
                "Risk/reward below minimum."
            )

            return result

        # ---------------------------------------------
        # SUCCESS
        # ---------------------------------------------

        result.valid = True

        result.reason = "VALID"

        return result

    # =====================================================
    # TRADE ACCEPTANCE
    # =====================================================

    def accept_trade(
        self,
        signal_type: SignalType,
        entry: float,
        stop_loss: float,
        target: float,
    ) -> bool:
        """
        Quick risk validation for scanner candidates.
        """

        if not self.valid_price_structure(
            signal_type,
            entry,
            stop_loss,
        ):
            return False

        if not self.valid_stop(
            entry,
            stop_loss,
        ):
            return False

        rr = self.risk_reward(
            entry,
            stop_loss,
            target,
        )

        return (
            rr
            >= self.config.minimum_rr
        )


# =========================================================
# GLOBAL RISK MANAGER
# =========================================================

risk_manager = RiskManager()


# =========================================================
# CONVENIENCE FUNCTIONS
# =========================================================

def calculate_position_size(
    entry: float,
    stop_loss: float,
    *,
    capital: Optional[float] = None,
    risk_percent: Optional[float] = None,
) -> int:
    """
    Calculate trade quantity.
    """

    return risk_manager.position_size(

        entry,

        stop_loss,

        capital=capital,

        risk_percent=risk_percent,
    )


def calculate_risk_reward(
    entry: float,
    stop_loss: float,
    target: float,
) -> float:
    """
    Calculate R:R ratio.
    """

    return risk_manager.risk_reward(
        entry,
        stop_loss,
        target,
    )


def calculate_target(
    signal_type: SignalType,
    entry: float,
    stop_loss: float,
    rr: float = 2.0,
) -> float:
    """
    Calculate target from required R:R.
    """

    return risk_manager.target_for_rr(
        signal_type,
        entry,
        stop_loss,
        rr,
    )


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "RiskResult",

    "RiskManager",

    "risk_manager",

    "calculate_position_size",

    "calculate_risk_reward",

    "calculate_target",
]


# ==========================
# END OF FILE
# ==========================