"""
=========================================================
StockVersity Scanner Pro
Signal Validator
Version : 2.0
=========================================================

Central validation layer for scanner-generated signals.

Responsibilities
----------------
• Validate required signal fields
• Validate BUY / SELL price structure
• Validate risk/reward
• Validate score and confidence
• Validate liquidity and volume
• Validate gap percentage
• Validate ADX
• Validate market cap
• Validate indicator values
• Validate expiry
• Produce detailed validation reports
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from math import isfinite

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from core.scanner.signal import Signal
from core.scanner.signal import SignalType

from core.scanner.config import ScannerConfig
from core.scanner.config import scanner_config


# =========================================================
# VALIDATION RESULT
# =========================================================

@dataclass(slots=True)
class ValidationResult:
    """
    Result returned by SignalValidator.
    """

    valid: bool = True

    errors: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    checks: Dict[str, bool] = field(
        default_factory=dict
    )

    # =====================================================
    # ADD ERROR
    # =====================================================

    def add_error(
        self,
        message: str,
        *,
        check: Optional[str] = None,
    ) -> None:

        self.valid = False

        self.errors.append(
            str(message)
        )

        if check:
            self.checks[check] = False

    # =====================================================
    # ADD WARNING
    # =====================================================

    def add_warning(
        self,
        message: str,
    ) -> None:

        self.warnings.append(
            str(message)
        )

    # =====================================================
    # PASS CHECK
    # =====================================================

    def pass_check(
        self,
        name: str,
    ) -> None:

        self.checks[name] = True

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "valid":
                self.valid,

            "errors":
                list(self.errors),

            "warnings":
                list(self.warnings),

            "checks":
                dict(self.checks),
        }

    # =====================================================
    # BOOL
    # =====================================================

    def __bool__(
        self,
    ) -> bool:

        return self.valid


# =========================================================
# SIGNAL VALIDATOR
# =========================================================

class SignalValidator:
    """
    Validate signals before they enter the ranking,
    alerting, or execution pipeline.
    """

    def __init__(
        self,
        config: Optional[ScannerConfig] = None,
    ) -> None:

        self.config = (
            config
            if config is not None
            else scanner_config
        )

    # =====================================================
    # NUMBER HELPER
    # =====================================================

    @staticmethod
    def _valid_number(
        value: Any,
    ) -> bool:
        """
        True when value can safely be treated as a
        finite numeric value.
        """

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
    # REQUIRED FIELDS
    # =====================================================

    def validate_identity(
        self,
        signal: Signal,
        result: ValidationResult,
    ) -> None:

        if not signal.instrument_key:

            result.add_error(
                "instrument_key is missing.",
                check="identity",
            )

            return

        if not signal.symbol:

            result.add_error(
                "symbol is missing.",
                check="identity",
            )

            return

        result.pass_check(
            "identity"
        )

    # =====================================================
    # PRICE VALIDATION
    # =====================================================

    def validate_prices(
        self,
        signal: Signal,
        result: ValidationResult,
    ) -> None:

        values = {

            "entry":
                signal.entry,

            "stop_loss":
                signal.stop_loss,

            "target1":
                signal.target1,
        }

        for name, value in values.items():

            if not self._valid_number(
                value
            ):

                result.add_error(
                    f"{name} is not a valid number.",
                    check="prices",
                )

                return

            if float(value) <= 0:

                result.add_error(
                    f"{name} must be greater than zero.",
                    check="prices",
                )

                return

        # ---------------------------------------------
        # BUY STRUCTURE
        # ---------------------------------------------

        if signal.signal_type == SignalType.BUY:

            if signal.stop_loss >= signal.entry:

                result.add_error(
                    "BUY stop loss must be below entry.",
                    check="prices",
                )

                return

            if signal.target1 <= signal.entry:

                result.add_error(
                    "BUY target must be above entry.",
                    check="prices",
                )

                return

        # ---------------------------------------------
        # SELL STRUCTURE
        # ---------------------------------------------

        elif signal.signal_type == SignalType.SELL:

            if signal.stop_loss <= signal.entry:

                result.add_error(
                    "SELL stop loss must be above entry.",
                    check="prices",
                )

                return

            if signal.target1 >= signal.entry:

                result.add_error(
                    "SELL target must be below entry.",
                    check="prices",
                )

                return

        result.pass_check(
            "prices"
        )

    # =====================================================
    # MINIMUM STOCK PRICE
    # =====================================================

    def validate_stock_price(
        self,
        signal: Signal,
        result: ValidationResult,
    ) -> None:

        price = (
            signal.last_price
            or signal.close_price
            or signal.entry
        )

        minimum = (
            self.config
            .market_filter
            .minimum_price
        )

        maximum = (
            self.config
            .market_filter
            .maximum_price
        )

        if price < minimum:

            result.add_error(
                (
                    f"Stock price {price:.2f} is below "
                    f"minimum {minimum:.2f}."
                ),
                check="stock_price",
            )

            return

        if price > maximum:

            result.add_error(
                (
                    f"Stock price {price:.2f} exceeds "
                    f"maximum {maximum:.2f}."
                ),
                check="stock_price",
            )

            return

        result.pass_check(
            "stock_price"
        )

    # =====================================================
    # RISK REWARD
    # =====================================================

    def validate_risk_reward(
        self,
        signal: Signal,
        result: ValidationResult,
    ) -> None:

        minimum_rr = (
            self.config
            .risk
            .minimum_rr
        )

        if not self._valid_number(
            signal.risk_reward
        ):

            result.add_error(
                "Risk/reward is invalid.",
                check="risk_reward",
            )

            return

        if signal.risk_reward < minimum_rr:

            result.add_error(
                (
                    f"Risk/reward {signal.risk_reward:.2f} "
                    f"is below minimum {minimum_rr:.2f}."
                ),
                check="risk_reward",
            )

            return

        result.pass_check(
            "risk_reward"
        )

    # =====================================================
    # SCORE
    # =====================================================

    def validate_score(
        self,
        signal: Signal,
        result: ValidationResult,
    ) -> None:

        score = signal.score

        if not self._valid_number(
            score
        ):

            result.add_error(
                "Signal score is invalid.",
                check="score",
            )

            return

        if not 0 <= score <= 100:

            result.add_error(
                "Signal score must be between 0 and 100.",
                check="score",
            )

            return

        minimum = (
            self.config
            .quality
            .minimum_score
        )

        if score < minimum:

            result.add_error(
                (
                    f"Signal score {score:.2f} is below "
                    f"minimum {minimum:.2f}."
                ),
                check="score",
            )

            return

        result.pass_check(
            "score"
        )

    # =====================================================
    # CONFIDENCE
    # =====================================================

    def validate_confidence(
        self,
        signal: Signal,
        result: ValidationResult,
    ) -> None:

        confidence = (
            signal.confidence
        )

        if not self._valid_number(
            confidence
        ):

            result.add_error(
                "Signal confidence is invalid.",
                check="confidence",
            )

            return

        if not 0 <= confidence <= 100:

            result.add_error(
                (
                    "Signal confidence must be "
                    "between 0 and 100."
                ),
                check="confidence",
            )

            return

        minimum = (
            self.config
            .quality
            .minimum_confidence
        )

        if confidence < minimum:

            result.add_error(
                (
                    f"Confidence {confidence:.2f} is below "
                    f"minimum {minimum:.2f}."
                ),
                check="confidence",
            )

            return

        result.pass_check(
            "confidence"
        )

    # =====================================================
    # MARKET CAP
    # =====================================================

    def validate_market_cap(
        self,
        signal: Signal,
        result: ValidationResult,
    ) -> None:

        minimum = (
            self.config
            .market_filter
            .minimum_market_cap
        )

        raw_market_cap = (
            signal.metadata.get(
                "market_cap"
            )
        )

        # Market cap may not yet be available from every
        # market-data source. Missing data is a warning.

        if raw_market_cap is None:

            result.add_warning(
                "Market cap data unavailable."
            )

            result.pass_check(
                "market_cap"
            )

            return

        if not self._valid_number(
            raw_market_cap
        ):

            result.add_error(
                "Market cap is invalid.",
                check="market_cap",
            )

            return

        market_cap = float(
            raw_market_cap
        )

        if market_cap < minimum:

            result.add_error(
                (
                    f"Market cap {market_cap:.2f} Cr is "
                    f"below minimum {minimum:.2f} Cr."
                ),
                check="market_cap",
            )

            return

        result.pass_check(
            "market_cap"
        )

    # =====================================================
    # VOLUME
    # =====================================================

    def validate_volume(
        self,
        signal: Signal,
        result: ValidationResult,
    ) -> None:

        config = (
            self.config
            .market_filter
        )

        if not config.require_liquidity:

            result.pass_check(
                "volume"
            )

            return

        if signal.volume < 0:

            result.add_error(
                "Volume cannot be negative.",
                check="volume",
            )

            return

        if (
            config.minimum_volume > 0
            and signal.volume
            < config.minimum_volume
        ):

            result.add_error(
                (
                    f"Volume {signal.volume} is below "
                    f"minimum {config.minimum_volume}."
                ),
                check="volume",
            )

            return

        result.pass_check(
            "volume"
        )

    # =====================================================
    # RELATIVE VOLUME
    # =====================================================

    def validate_volume_ratio(
        self,
        signal: Signal,
        result: ValidationResult,
    ) -> None:

        config = (
            self.config
            .market_filter
        )

        if not config.require_volume_confirmation:

            result.pass_check(
                "volume_ratio"
            )

            return

        ratio = signal.volume_ratio

        if ratio <= 0:

            if (
                signal.volume > 0
                and signal.average_volume > 0
            ):

                ratio = (
                    signal.volume
                    / signal.average_volume
                )

        if ratio <= 0:

            result.add_warning(
                "Relative volume data unavailable."
            )

            result.pass_check(
                "volume_ratio"
            )

            return

        if (
            ratio
            < config.minimum_volume_ratio
        ):

            result.add_error(
                (
                    f"RVOL {ratio:.2f} is below minimum "
                    f"{config.minimum_volume_ratio:.2f}."
                ),
                check="volume_ratio",
            )

            return

        result.pass_check(
            "volume_ratio"
        )

    # =====================================================
    # GAP FILTER
    # =====================================================

    def validate_gap(
        self,
        signal: Signal,
        result: ValidationResult,
    ) -> None:

        config = (
            self.config
            .market_filter
        )

        gap = signal.gap_percent

        if not self._valid_number(
            gap
        ):

            result.add_error(
                "Gap percentage is invalid.",
                check="gap",
            )

            return

        maximum = abs(
            config.maximum_gap_percent
        )

        if (
            config.exclude_large_gap_up
            and gap > maximum
        ):

            result.add_error(
                (
                    f"Gap-up {gap:.2f}% exceeds "
                    f"{maximum:.2f}%."
                ),
                check="gap",
            )

            return

        if (
            config.exclude_large_gap_down
            and gap < -maximum
        ):

            result.add_error(
                (
                    f"Gap-down {gap:.2f}% exceeds "
                    f"-{maximum:.2f}%."
                ),
                check="gap",
            )

            return

        result.pass_check(
            "gap"
        )

    # =====================================================
    # ADX
    # =====================================================

    def validate_adx(
        self,
        signal: Signal,
        result: ValidationResult,
    ) -> None:

        minimum = (
            self.config
            .market_filter
            .minimum_adx
        )

        adx = signal.adx

        # Zero means indicator snapshot may not yet have
        # been populated.

        if adx <= 0:

            result.add_warning(
                "ADX data unavailable."
            )

            result.pass_check(
                "adx"
            )

            return

        if adx < minimum:

            result.add_error(
                (
                    f"ADX {adx:.2f} is below "
                    f"minimum {minimum:.2f}."
                ),
                check="adx",
            )

            return

        result.pass_check(
            "adx"
        )

    # =====================================================
    # STOP DISTANCE
    # =====================================================

    def validate_stop_distance(
        self,
        signal: Signal,
        result: ValidationResult,
    ) -> None:

        if signal.entry <= 0:
            return

        distance = abs(
            signal.entry
            - signal.stop_loss
        )

        percent = (
            distance
            / signal.entry
            * 100.0
        )

        minimum = (
            self.config
            .risk
            .minimum_stop_percent
        )

        maximum = (
            self.config
            .risk
            .maximum_stop_percent
        )

        if percent < minimum:

            result.add_error(
                (
                    f"Stop distance {percent:.2f}% is below "
                    f"minimum {minimum:.2f}%."
                ),
                check="stop_distance",
            )

            return

        if percent > maximum:

            result.add_error(
                (
                    f"Stop distance {percent:.2f}% exceeds "
                    f"maximum {maximum:.2f}%."
                ),
                check="stop_distance",
            )

            return

        result.pass_check(
            "stop_distance"
        )

    # =====================================================
    # TARGET ORDER
    # =====================================================

    def validate_targets(
        self,
        signal: Signal,
        result: ValidationResult,
    ) -> None:

        targets = signal.targets

        if not targets:

            result.add_error(
                "Signal has no valid targets.",
                check="targets",
            )

            return

        if signal.is_buy:

            previous = signal.entry

            for target in targets:

                if target <= previous:

                    result.add_error(
                        (
                            "BUY targets must increase "
                            "sequentially."
                        ),
                        check="targets",
                    )

                    return

                previous = target

        elif signal.is_sell:

            previous = signal.entry

            for target in targets:

                if target >= previous:

                    result.add_error(
                        (
                            "SELL targets must decrease "
                            "sequentially."
                        ),
                        check="targets",
                    )

                    return

                previous = target

        result.pass_check(
            "targets"
        )

    # =====================================================
    # EXPIRY
    # =====================================================

    def validate_expiry(
        self,
        signal: Signal,
        result: ValidationResult,
    ) -> None:

        if signal.is_expired:

            result.add_error(
                "Signal has expired.",
                check="expiry",
            )

            return

        result.pass_check(
            "expiry"
        )

    # =====================================================
    # POSITION SIZE
    # =====================================================

    def validate_quantity(
        self,
        signal: Signal,
        result: ValidationResult,
    ) -> None:

        if signal.risk <= 0:

            result.add_error(
                "Signal risk must be greater than zero.",
                check="quantity",
            )

            return

        if signal.quantity <= 0:

            result.add_error(
                (
                    "Calculated quantity is zero. "
                    "Risk per share may exceed account risk."
                ),
                check="quantity",
            )

            return

        result.pass_check(
            "quantity"
        )

    # =====================================================
    # INDICATOR SANITY
    # =====================================================

    def validate_indicators(
        self,
        signal: Signal,
        result: ValidationResult,
    ) -> None:

        if signal.rsi != 0:

            if not 0 <= signal.rsi <= 100:

                result.add_error(
                    "RSI must be between 0 and 100.",
                    check="indicators",
                )

                return

        if signal.adx < 0:

            result.add_error(
                "ADX cannot be negative.",
                check="indicators",
            )

            return

        if signal.volume_ratio < 0:

            result.add_error(
                "Volume ratio cannot be negative.",
                check="indicators",
            )

            return

        if signal.atr < 0:

            result.add_error(
                "ATR cannot be negative.",
                check="indicators",
            )

            return

        result.pass_check(
            "indicators"
        )

    # =====================================================
    # COMPLETE VALIDATION
    # =====================================================

    def validate(
        self,
        signal: Signal,
    ) -> ValidationResult:
        """
        Run complete signal validation.
        """

        if not isinstance(
            signal,
            Signal,
        ):

            result = ValidationResult(
                valid=False
            )

            result.add_error(
                "Object must be a Signal instance."
            )

            return result

        result = ValidationResult()

        self.validate_identity(
            signal,
            result,
        )

        self.validate_prices(
            signal,
            result,
        )

        self.validate_stock_price(
            signal,
            result,
        )

        self.validate_risk_reward(
            signal,
            result,
        )

        self.validate_score(
            signal,
            result,
        )

        self.validate_confidence(
            signal,
            result,
        )

        self.validate_market_cap(
            signal,
            result,
        )

        self.validate_volume(
            signal,
            result,
        )

        self.validate_volume_ratio(
            signal,
            result,
        )

        self.validate_gap(
            signal,
            result,
        )

        self.validate_adx(
            signal,
            result,
        )

        self.validate_stop_distance(
            signal,
            result,
        )

        self.validate_targets(
            signal,
            result,
        )

        self.validate_expiry(
            signal,
            result,
        )

        self.validate_quantity(
            signal,
            result,
        )

        self.validate_indicators(
            signal,
            result,
        )

        result.valid = (
            len(result.errors) == 0
        )

        return result

    # =====================================================
    # SIMPLE BOOL VALIDATION
    # =====================================================

    def is_valid(
        self,
        signal: Signal,
    ) -> bool:
        """
        Return True when signal passes validation.
        """

        return self.validate(
            signal
        ).valid

    # =====================================================
    # VALIDATE MANY
    # =====================================================

    def validate_many(
        self,
        signals: List[Signal],
    ) -> Dict[
        str,
        ValidationResult
    ]:
        """
        Validate multiple signals.
        """

        results: Dict[
            str,
            ValidationResult
        ] = {}

        for signal in signals:

            key = (
                signal.signal_id
                or signal.symbol
            )

            results[key] = (
                self.validate(
                    signal
                )
            )

        return results

    # =====================================================
    # FILTER VALID
    # =====================================================

    def filter_valid(
        self,
        signals: List[Signal],
    ) -> List[Signal]:
        """
        Return only signals passing validation.
        """

        return [

            signal

            for signal in signals

            if self.is_valid(
                signal
            )

        ]

    # =====================================================
    # REPORT
    # =====================================================

    def report(
        self,
        signal: Signal,
    ) -> Dict[str, Any]:
        """
        UI / diagnostics friendly validation report.
        """

        result = self.validate(
            signal
        )

        return {

            "signal_id":
                signal.signal_id,

            "symbol":
                signal.symbol,

            "valid":
                result.valid,

            "errors":
                result.errors,

            "warnings":
                result.warnings,

            "checks":
                result.checks,

            "error_count":
                len(result.errors),

            "warning_count":
                len(result.warnings),
        }


# =========================================================
# DEFAULT VALIDATOR
# =========================================================

signal_validator = SignalValidator()


# =========================================================
# CONVENIENCE FUNCTIONS
# =========================================================

def validate_signal(
    signal: Signal,
) -> ValidationResult:
    """
    Validate one signal using global validator.
    """

    return signal_validator.validate(
        signal
    )


def is_valid_signal(
    signal: Signal,
) -> bool:
    """
    True when signal passes validation.
    """

    return signal_validator.is_valid(
        signal
    )


def filter_valid_signals(
    signals: List[Signal],
) -> List[Signal]:
    """
    Return valid signals only.
    """

    return signal_validator.filter_valid(
        signals
    )


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "ValidationResult",

    "SignalValidator",

    "signal_validator",

    "validate_signal",

    "is_valid_signal",

    "filter_valid_signals",
]


# ==========================
# END OF FILE
# ==========================