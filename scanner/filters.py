"""
=========================================================
StockVersity Scanner Pro
Scanner Filters
Version : 2.0
=========================================================

Centralized scanner filtering system.

Features
--------
• Minimum price filter
• Maximum price filter
• Market-cap filter
• Gap filter
• ADX filter
• Relative-volume filter
• Absolute-volume filter
• Liquidity filter
• Risk/reward filter
• Score filter
• Confidence filter
• Beta filter
• F&O filter
• VWAP filter
• EMA200 trend filter
• RSI filter
• Sector filter
• Spread filter
• ORB-width filter
• ATR filter
• Signal-direction filter
• Custom filters
• Filter result diagnostics

Designed for:
    Intraday
    Swing
    Positional
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Set
from typing import Tuple

from core.scanner.signal import Signal
from core.scanner.signal import SignalType


# =========================================================
# TYPE ALIASES
# =========================================================

FilterCallback = Callable[[Signal], bool]


# =========================================================
# FILTER RESULT
# =========================================================

@dataclass(slots=True)
class FilterResult:
    """
    Result returned after evaluating one signal.
    """

    passed: bool = True

    reasons: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    checks: Dict[str, bool] = field(
        default_factory=dict
    )

    def fail(
        self,
        name: str,
        reason: str,
    ) -> None:

        self.passed = False

        self.checks[name] = False

        self.reasons.append(reason)

    def pass_check(
        self,
        name: str,
    ) -> None:

        self.checks[name] = True

    def warn(
        self,
        message: str,
    ) -> None:

        self.warnings.append(message)

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {
            "passed": self.passed,
            "reasons": list(self.reasons),
            "warnings": list(self.warnings),
            "checks": dict(self.checks),
        }


# =========================================================
# FILTER CONFIGURATION
# =========================================================

@dataclass(slots=True)
class ScannerFilterConfig:
    """
    Global scanner filter configuration.
    """

    # -----------------------------------------------------
    # PRICE
    # -----------------------------------------------------

    minimum_price: float = 200.0

    maximum_price: Optional[float] = None

    # -----------------------------------------------------
    # MARKET CAP
    # -----------------------------------------------------

    minimum_market_cap: float = 1000.0

    maximum_market_cap: Optional[float] = None

    # -----------------------------------------------------
    # GAP
    # -----------------------------------------------------

    maximum_gap_percent: float = 3.0

    # -----------------------------------------------------
    # TREND STRENGTH
    # -----------------------------------------------------

    minimum_adx: float = 20.0

    # -----------------------------------------------------
    # VOLUME
    # -----------------------------------------------------

    minimum_volume: int = 0

    minimum_average_volume: int = 0

    minimum_volume_ratio: float = 1.20

    # -----------------------------------------------------
    # LIQUIDITY
    # -----------------------------------------------------

    minimum_turnover: float = 0.0

    maximum_spread_percent: Optional[float] = None

    # -----------------------------------------------------
    # RISK
    # -----------------------------------------------------

    minimum_risk_reward: float = 2.0

    maximum_risk_percent_of_price: Optional[float] = None

    # -----------------------------------------------------
    # QUALITY
    # -----------------------------------------------------

    minimum_score: float = 60.0

    minimum_confidence: float = 60.0

    # -----------------------------------------------------
    # BETA
    # -----------------------------------------------------

    minimum_beta: Optional[float] = None

    maximum_beta: Optional[float] = None

    # -----------------------------------------------------
    # RSI
    # -----------------------------------------------------

    minimum_rsi: Optional[float] = None

    maximum_rsi: Optional[float] = None

    # -----------------------------------------------------
    # ORB
    # -----------------------------------------------------

    maximum_orb_width_percent: float = 3.0

    # -----------------------------------------------------
    # ATR
    # -----------------------------------------------------

    minimum_atr_percent: Optional[float] = None

    maximum_atr_percent: Optional[float] = None

    # -----------------------------------------------------
    # TREND FILTERS
    # -----------------------------------------------------

    require_vwap_confirmation: bool = False

    require_ema200_confirmation: bool = False

    # -----------------------------------------------------
    # F&O
    # -----------------------------------------------------

    require_fno: bool = False

    # -----------------------------------------------------
    # SECTOR
    # -----------------------------------------------------

    allowed_sectors: Set[str] = field(
        default_factory=set
    )

    blocked_sectors: Set[str] = field(
        default_factory=set
    )

    # -----------------------------------------------------
    # SIGNAL TYPE
    # -----------------------------------------------------

    allowed_signal_types: Set[SignalType] = field(
        default_factory=set
    )

    # -----------------------------------------------------
    # CONTROL
    # -----------------------------------------------------

    enabled: bool = True


# =========================================================
# SCANNER FILTER ENGINE
# =========================================================

class ScannerFilters:
    """
    Central filter engine for StockVersity scanners.

    Example
    -------

    filters = ScannerFilters()

    result = filters.evaluate(signal)

    if result.passed:
        ...
    """

    def __init__(
        self,
        config: Optional[
            ScannerFilterConfig
        ] = None,
    ) -> None:

        self.config = (
            config
            if config is not None
            else ScannerFilterConfig()
        )

        self.custom_filters: Dict[
            str,
            FilterCallback
        ] = {}

        self.total_checked = 0

        self.total_passed = 0

        self.total_rejected = 0

        self.rejection_counts: Dict[
            str,
            int
        ] = {}

    # =====================================================
    # RESET STATISTICS
    # =====================================================

    def reset_statistics(
        self,
    ) -> None:

        self.total_checked = 0

        self.total_passed = 0

        self.total_rejected = 0

        self.rejection_counts.clear()

    # =====================================================
    # EVALUATE
    # =====================================================

    def evaluate(
        self,
        signal: Signal,
    ) -> FilterResult:
        """
        Run every enabled filter against one signal.
        """

        result = FilterResult()

        if not self.config.enabled:

            return result

        self.total_checked += 1

        self._check_price(
            signal,
            result,
        )

        self._check_market_cap(
            signal,
            result,
        )

        self._check_gap(
            signal,
            result,
        )

        self._check_adx(
            signal,
            result,
        )

        self._check_volume(
            signal,
            result,
        )

        self._check_liquidity(
            signal,
            result,
        )

        self._check_risk_reward(
            signal,
            result,
        )

        self._check_score(
            signal,
            result,
        )

        self._check_confidence(
            signal,
            result,
        )

        self._check_beta(
            signal,
            result,
        )

        self._check_rsi(
            signal,
            result,
        )

        self._check_atr(
            signal,
            result,
        )

        self._check_orb_width(
            signal,
            result,
        )

        self._check_vwap(
            signal,
            result,
        )

        self._check_ema200(
            signal,
            result,
        )

        self._check_fno(
            signal,
            result,
        )

        self._check_sector(
            signal,
            result,
        )

        self._check_signal_type(
            signal,
            result,
        )

        self._check_spread(
            signal,
            result,
        )

        self._run_custom_filters(
            signal,
            result,
        )

        if result.passed:

            self.total_passed += 1

        else:

            self.total_rejected += 1

            for reason in result.reasons:

                self.rejection_counts[
                    reason
                ] = (
                    self.rejection_counts.get(
                        reason,
                        0,
                    )
                    + 1
                )

        return result

    # =====================================================
    # APPLY
    # =====================================================

    def apply(
        self,
        signals: Sequence[Signal],
    ) -> List[Signal]:
        """
        Filter a collection of signals.
        """

        accepted: List[Signal] = []

        for signal in signals:

            result = self.evaluate(
                signal
            )

            signal.metadata[
                "filter_result"
            ] = result.to_dict()

            if result.passed:

                accepted.append(
                    signal
                )

        return accepted

    # =====================================================
    # APPLY WITH REJECTIONS
    # =====================================================

    def apply_with_rejections(
        self,
        signals: Sequence[Signal],
    ) -> Tuple[
        List[Signal],
        List[Signal],
    ]:

        accepted: List[Signal] = []

        rejected: List[Signal] = []

        for signal in signals:

            result = self.evaluate(
                signal
            )

            signal.metadata[
                "filter_result"
            ] = result.to_dict()

            if result.passed:

                accepted.append(
                    signal
                )

            else:

                rejected.append(
                    signal
                )

        return (
            accepted,
            rejected,
        )

    # =====================================================
    # PRICE
    # =====================================================

    def _check_price(
        self,
        signal: Signal,
        result: FilterResult,
    ) -> None:

        price = (
            signal.last_price
            or signal.close_price
            or signal.entry
        )

        if (
            price
            < self.config.minimum_price
        ):

            result.fail(
                "price",
                "PRICE_BELOW_MINIMUM",
            )

            return

        maximum = (
            self.config.maximum_price
        )

        if (
            maximum is not None
            and price > maximum
        ):

            result.fail(
                "price",
                "PRICE_ABOVE_MAXIMUM",
            )

            return

        result.pass_check(
            "price"
        )

    # =====================================================
    # MARKET CAP
    # =====================================================

    def _check_market_cap(
        self,
        signal: Signal,
        result: FilterResult,
    ) -> None:

        market_cap = self._number(

            signal.metadata.get(
                "market_cap",
                0.0,
            )

        )

        if (
            market_cap
            < self.config.minimum_market_cap
        ):

            result.fail(
                "market_cap",
                "MARKET_CAP_BELOW_MINIMUM",
            )

            return

        maximum = (
            self.config.maximum_market_cap
        )

        if (
            maximum is not None
            and market_cap > maximum
        ):

            result.fail(
                "market_cap",
                "MARKET_CAP_ABOVE_MAXIMUM",
            )

            return

        result.pass_check(
            "market_cap"
        )

    # =====================================================
    # GAP
    # =====================================================

    def _check_gap(
        self,
        signal: Signal,
        result: FilterResult,
    ) -> None:

        if (
            abs(signal.gap_percent)
            > self.config.maximum_gap_percent
        ):

            result.fail(
                "gap",
                "GAP_ABOVE_LIMIT",
            )

            return

        result.pass_check(
            "gap"
        )

    # =====================================================
    # ADX
    # =====================================================

    def _check_adx(
        self,
        signal: Signal,
        result: FilterResult,
    ) -> None:

        if (
            signal.adx
            < self.config.minimum_adx
        ):

            result.fail(
                "adx",
                "ADX_BELOW_MINIMUM",
            )

            return

        result.pass_check(
            "adx"
        )

    # =====================================================
    # VOLUME
    # =====================================================

    def _check_volume(
        self,
        signal: Signal,
        result: FilterResult,
    ) -> None:

        if (
            signal.volume
            < self.config.minimum_volume
        ):

            result.fail(
                "volume",
                "VOLUME_BELOW_MINIMUM",
            )

            return

        if (
            signal.average_volume
            < self.config.minimum_average_volume
        ):

            result.fail(
                "volume",
                "AVERAGE_VOLUME_BELOW_MINIMUM",
            )

            return

        if (
            signal.volume_ratio
            < self.config.minimum_volume_ratio
        ):

            result.fail(
                "volume",
                "RVOL_BELOW_MINIMUM",
            )

            return

        result.pass_check(
            "volume"
        )

    # =====================================================
    # LIQUIDITY
    # =====================================================

    def _check_liquidity(
        self,
        signal: Signal,
        result: FilterResult,
    ) -> None:

        turnover = self._number(

            signal.metadata.get(
                "turnover",
                0.0,
            )

        )

        if (
            turnover
            < self.config.minimum_turnover
        ):

            result.fail(
                "liquidity",
                "TURNOVER_BELOW_MINIMUM",
            )

            return

        result.pass_check(
            "liquidity"
        )

    # =====================================================
    # RISK / REWARD
    # =====================================================

    def _check_risk_reward(
        self,
        signal: Signal,
        result: FilterResult,
    ) -> None:

        if (
            signal.risk_reward
            < self.config.minimum_risk_reward
        ):

            result.fail(
                "risk_reward",
                "RISK_REWARD_BELOW_MINIMUM",
            )

            return

        maximum_risk = (
            self.config
            .maximum_risk_percent_of_price
        )

        if maximum_risk is not None:

            price = (
                signal.entry
                or signal.last_price
            )

            if price > 0:

                risk_percent = (

                    signal.risk
                    / price

                ) * 100.0

                if (
                    risk_percent
                    > maximum_risk
                ):

                    result.fail(
                        "risk_reward",
                        "STOP_DISTANCE_TOO_WIDE",
                    )

                    return

        result.pass_check(
            "risk_reward"
        )

    # =====================================================
    # SCORE
    # =====================================================

    def _check_score(
        self,
        signal: Signal,
        result: FilterResult,
    ) -> None:

        if (
            signal.score
            < self.config.minimum_score
        ):

            result.fail(
                "score",
                "SCORE_BELOW_MINIMUM",
            )

            return

        result.pass_check(
            "score"
        )

    # =====================================================
    # CONFIDENCE
    # =====================================================

    def _check_confidence(
        self,
        signal: Signal,
        result: FilterResult,
    ) -> None:

        if (
            signal.confidence
            < self.config.minimum_confidence
        ):

            result.fail(
                "confidence",
                "CONFIDENCE_BELOW_MINIMUM",
            )

            return

        result.pass_check(
            "confidence"
        )

    # =====================================================
    # BETA
    # =====================================================

    def _check_beta(
        self,
        signal: Signal,
        result: FilterResult,
    ) -> None:

        minimum = (
            self.config.minimum_beta
        )

        maximum = (
            self.config.maximum_beta
        )

        if (
            minimum is None
            and maximum is None
        ):

            result.pass_check(
                "beta"
            )

            return

        beta = signal.beta

        if (
            minimum is not None
            and beta < minimum
        ):

            result.fail(
                "beta",
                "BETA_BELOW_MINIMUM",
            )

            return

        if (
            maximum is not None
            and beta > maximum
        ):

            result.fail(
                "beta",
                "BETA_ABOVE_MAXIMUM",
            )

            return

        result.pass_check(
            "beta"
        )

    # =====================================================
    # RSI
    # =====================================================

    def _check_rsi(
        self,
        signal: Signal,
        result: FilterResult,
    ) -> None:

        minimum = (
            self.config.minimum_rsi
        )

        maximum = (
            self.config.maximum_rsi
        )

        if (
            minimum is None
            and maximum is None
        ):

            result.pass_check(
                "rsi"
            )

            return

        if (
            minimum is not None
            and signal.rsi < minimum
        ):

            result.fail(
                "rsi",
                "RSI_BELOW_MINIMUM",
            )

            return

        if (
            maximum is not None
            and signal.rsi > maximum
        ):

            result.fail(
                "rsi",
                "RSI_ABOVE_MAXIMUM",
            )

            return

        result.pass_check(
            "rsi"
        )

    # =====================================================
    # ATR
    # =====================================================

    def _check_atr(
        self,
        signal: Signal,
        result: FilterResult,
    ) -> None:

        minimum = (
            self.config.minimum_atr_percent
        )

        maximum = (
            self.config.maximum_atr_percent
        )

        if (
            minimum is None
            and maximum is None
        ):

            result.pass_check(
                "atr"
            )

            return

        price = (
            signal.last_price
            or signal.entry
        )

        if (
            price <= 0
            or signal.atr <= 0
        ):

            result.fail(
                "atr",
                "ATR_DATA_MISSING",
            )

            return

        atr_percent = (

            signal.atr
            / price

        ) * 100.0

        if (
            minimum is not None
            and atr_percent < minimum
        ):

            result.fail(
                "atr",
                "ATR_BELOW_MINIMUM",
            )

            return

        if (
            maximum is not None
            and atr_percent > maximum
        ):

            result.fail(
                "atr",
                "ATR_ABOVE_MAXIMUM",
            )

            return

        result.pass_check(
            "atr"
        )

    # =====================================================
    # ORB WIDTH
    # =====================================================

    def _check_orb_width(
        self,
        signal: Signal,
        result: FilterResult,
    ) -> None:

        if (
            "orb_width_percent"
            not in signal.metadata
        ):

            result.pass_check(
                "orb_width"
            )

            return

        width = self._number(

            signal.metadata.get(
                "orb_width_percent",
                0.0,
            )

        )

        if (
            width
            > self.config.maximum_orb_width_percent
        ):

            result.fail(
                "orb_width",
                "ORB_WIDTH_ABOVE_LIMIT",
            )

            return

        result.pass_check(
            "orb_width"
        )

    # =====================================================
    # VWAP
    # =====================================================

    def _check_vwap(
        self,
        signal: Signal,
        result: FilterResult,
    ) -> None:

        if (
            not self.config
            .require_vwap_confirmation
        ):

            result.pass_check(
                "vwap"
            )

            return

        if signal.vwap <= 0:

            result.fail(
                "vwap",
                "VWAP_DATA_MISSING",
            )

            return

        price = (
            signal.last_price
            or signal.entry
        )

        if (
            signal.is_buy
            and price <= signal.vwap
        ):

            result.fail(
                "vwap",
                "BUY_BELOW_VWAP",
            )

            return

        if (
            signal.is_sell
            and price >= signal.vwap
        ):

            result.fail(
                "vwap",
                "SELL_ABOVE_VWAP",
            )

            return

        result.pass_check(
            "vwap"
        )

    # =====================================================
    # EMA200
    # =====================================================

    def _check_ema200(
        self,
        signal: Signal,
        result: FilterResult,
    ) -> None:

        if (
            not self.config
            .require_ema200_confirmation
        ):

            result.pass_check(
                "ema200"
            )

            return

        if signal.ema200 <= 0:

            result.fail(
                "ema200",
                "EMA200_DATA_MISSING",
            )

            return

        price = (
            signal.last_price
            or signal.entry
        )

        if (
            signal.is_buy
            and price <= signal.ema200
        ):

            result.fail(
                "ema200",
                "BUY_BELOW_EMA200",
            )

            return

        if (
            signal.is_sell
            and price >= signal.ema200
        ):

            result.fail(
                "ema200",
                "SELL_ABOVE_EMA200",
            )

            return

        result.pass_check(
            "ema200"
        )

    # =====================================================
    # F&O
    # =====================================================

    def _check_fno(
        self,
        signal: Signal,
        result: FilterResult,
    ) -> None:

        if not self.config.require_fno:

            result.pass_check(
                "fno"
            )

            return

        is_fno = bool(

            signal.metadata.get(
                "is_fno",
                False,
            )

        )

        if not is_fno:

            result.fail(
                "fno",
                "NOT_FNO_STOCK",
            )

            return

        result.pass_check(
            "fno"
        )

    # =====================================================
    # SECTOR
    # =====================================================

    def _check_sector(
        self,
        signal: Signal,
        result: FilterResult,
    ) -> None:

        sector = (
            signal.sector
            .upper()
            .strip()
        )

        allowed = {

            item.upper().strip()

            for item in (
                self.config.allowed_sectors
            )

        }

        blocked = {

            item.upper().strip()

            for item in (
                self.config.blocked_sectors
            )

        }

        if (
            allowed
            and sector not in allowed
        ):

            result.fail(
                "sector",
                "SECTOR_NOT_ALLOWED",
            )

            return

        if (
            sector
            and sector in blocked
        ):

            result.fail(
                "sector",
                "SECTOR_BLOCKED",
            )

            return

        result.pass_check(
            "sector"
        )

    # =====================================================
    # SIGNAL TYPE
    # =====================================================

    def _check_signal_type(
        self,
        signal: Signal,
        result: FilterResult,
    ) -> None:

        allowed = (
            self.config
            .allowed_signal_types
        )

        if (
            allowed
            and signal.signal_type
            not in allowed
        ):

            result.fail(
                "signal_type",
                "SIGNAL_TYPE_NOT_ALLOWED",
            )

            return

        result.pass_check(
            "signal_type"
        )

    # =====================================================
    # SPREAD
    # =====================================================

    def _check_spread(
        self,
        signal: Signal,
        result: FilterResult,
    ) -> None:

        maximum = (
            self.config
            .maximum_spread_percent
        )

        if maximum is None:

            result.pass_check(
                "spread"
            )

            return

        spread = self._number(

            signal.metadata.get(
                "spread_percent",
                0.0,
            )

        )

        if spread > maximum:

            result.fail(
                "spread",
                "SPREAD_ABOVE_LIMIT",
            )

            return

        result.pass_check(
            "spread"
        )

    # =====================================================
    # CUSTOM FILTERS
    # =====================================================

    def register_filter(
        self,
        name: str,
        callback: FilterCallback,
    ) -> None:
        """
        Add custom filtering logic.

        Example
        -------
        filters.register_filter(
            "RSI_LONG",
            lambda signal: signal.rsi > 55
        )
        """

        name = (
            name
            .upper()
            .strip()
        )

        if not name:

            raise ValueError(
                "Filter name cannot be empty."
            )

        if not callable(callback):

            raise TypeError(
                "Filter callback must be callable."
            )

        self.custom_filters[
            name
        ] = callback

    # =====================================================
    # REMOVE CUSTOM FILTER
    # =====================================================

    def unregister_filter(
        self,
        name: str,
    ) -> None:

        self.custom_filters.pop(
            name.upper().strip(),
            None,
        )

    # =====================================================
    # RUN CUSTOM FILTERS
    # =====================================================

    def _run_custom_filters(
        self,
        signal: Signal,
        result: FilterResult,
    ) -> None:

        for (
            name,
            callback,
        ) in self.custom_filters.items():

            try:

                passed = bool(
                    callback(signal)
                )

            except Exception:

                result.fail(
                    name,
                    f"CUSTOM_FILTER_ERROR:{name}",
                )

                continue

            if passed:

                result.pass_check(
                    name
                )

            else:

                result.fail(
                    name,
                    f"CUSTOM_FILTER_FAILED:{name}",
                )

    # =====================================================
    # CONFIGURE
    # =====================================================

    def configure(
        self,
        **kwargs: Any,
    ) -> "ScannerFilters":
        """
        Dynamically modify filter configuration.
        """

        for key, value in kwargs.items():

            if hasattr(
                self.config,
                key,
            ):

                setattr(
                    self.config,
                    key,
                    value,
                )

        return self

    # =====================================================
    # ENABLE
    # =====================================================

    def enable(
        self,
    ) -> None:

        self.config.enabled = True

    # =====================================================
    # DISABLE
    # =====================================================

    def disable(
        self,
    ) -> None:

        self.config.enabled = False

    # =====================================================
    # PRESET : INTRADAY
    # =====================================================

    def intraday(
        self,
    ) -> "ScannerFilters":
        """
        Recommended intraday configuration.
        """

        self.config.minimum_price = 200.0

        self.config.minimum_market_cap = 1000.0

        self.config.maximum_gap_percent = 3.0

        self.config.minimum_adx = 20.0

        self.config.minimum_volume_ratio = 1.5

        self.config.minimum_risk_reward = 2.0

        self.config.minimum_score = 60.0

        self.config.minimum_confidence = 60.0

        self.config.maximum_orb_width_percent = 3.0

        self.config.require_vwap_confirmation = True

        self.config.require_ema200_confirmation = True

        return self

    # =====================================================
    # PRESET : SWING
    # =====================================================

    def swing(
        self,
    ) -> "ScannerFilters":
        """
        Recommended swing configuration.
        """

        self.config.minimum_price = 200.0

        self.config.minimum_market_cap = 1000.0

        self.config.maximum_gap_percent = 5.0

        self.config.minimum_adx = 18.0

        self.config.minimum_volume_ratio = 1.20

        self.config.minimum_risk_reward = 2.0

        self.config.minimum_score = 65.0

        self.config.minimum_confidence = 60.0

        self.config.require_vwap_confirmation = False

        self.config.require_ema200_confirmation = False

        return self

    # =====================================================
    # PRESET : POSITIONAL
    # =====================================================

    def positional(
        self,
    ) -> "ScannerFilters":
        """
        Recommended positional configuration.
        """

        self.config.minimum_price = 200.0

        self.config.minimum_market_cap = 1000.0

        self.config.maximum_gap_percent = 7.0

        self.config.minimum_adx = 18.0

        self.config.minimum_volume_ratio = 1.0

        self.config.minimum_risk_reward = 2.5

        self.config.minimum_score = 70.0

        self.config.minimum_confidence = 65.0

        self.config.require_vwap_confirmation = False

        self.config.require_ema200_confirmation = False

        return self

    # =====================================================
    # PRESET : F&O INTRADAY
    # =====================================================

    def fno_intraday(
        self,
    ) -> "ScannerFilters":

        self.intraday()

        self.config.require_fno = True

        self.config.minimum_beta = 0.8

        return self

    # =====================================================
    # STATISTICS
    # =====================================================

    def statistics(
        self,
    ) -> Dict[str, Any]:

        pass_rate = 0.0

        if self.total_checked > 0:

            pass_rate = (

                self.total_passed
                / self.total_checked

            ) * 100.0

        return {

            "checked": self.total_checked,

            "passed": self.total_passed,

            "rejected": self.total_rejected,

            "pass_rate": round(
                pass_rate,
                2,
            ),

            "rejection_counts": dict(
                self.rejection_counts
            ),

        }

    # =====================================================
    # CONFIG SNAPSHOT
    # =====================================================

    def config_snapshot(
        self,
    ) -> Dict[str, Any]:

        config = self.config

        return {

            "enabled": config.enabled,

            "minimum_price": (
                config.minimum_price
            ),

            "maximum_price": (
                config.maximum_price
            ),

            "minimum_market_cap": (
                config.minimum_market_cap
            ),

            "maximum_market_cap": (
                config.maximum_market_cap
            ),

            "maximum_gap_percent": (
                config.maximum_gap_percent
            ),

            "minimum_adx": (
                config.minimum_adx
            ),

            "minimum_volume": (
                config.minimum_volume
            ),

            "minimum_average_volume": (
                config.minimum_average_volume
            ),

            "minimum_volume_ratio": (
                config.minimum_volume_ratio
            ),

            "minimum_turnover": (
                config.minimum_turnover
            ),

            "minimum_risk_reward": (
                config.minimum_risk_reward
            ),

            "minimum_score": (
                config.minimum_score
            ),

            "minimum_confidence": (
                config.minimum_confidence
            ),

            "minimum_beta": (
                config.minimum_beta
            ),

            "maximum_beta": (
                config.maximum_beta
            ),

            "require_fno": (
                config.require_fno
            ),

            "require_vwap_confirmation": (
                config
                .require_vwap_confirmation
            ),

            "require_ema200_confirmation": (
                config
                .require_ema200_confirmation
            ),

            "maximum_orb_width_percent": (
                config
                .maximum_orb_width_percent
            ),

        }

    # =====================================================
    # SAFE NUMBER
    # =====================================================

    @staticmethod
    def _number(
        value: Any,
        default: float = 0.0,
    ) -> float:

        try:

            if value is None:

                return default

            return float(value)

        except (
            TypeError,
            ValueError,
        ):

            return default


# =========================================================
# FACTORY
# =========================================================

def create_scanner_filters(
    mode: str = "intraday",
) -> ScannerFilters:
    """
    Create configured filter engine.

    Supported modes
    ---------------
    intraday
    swing
    positional
    fno_intraday
    """

    filters = ScannerFilters()

    mode = (
        mode
        .lower()
        .strip()
    )

    if mode == "swing":

        filters.swing()

    elif mode == "positional":

        filters.positional()

    elif mode == "fno_intraday":

        filters.fno_intraday()

    else:

        filters.intraday()

    return filters


# =========================================================
# CONVENIENCE FUNCTIONS
# =========================================================

def filter_intraday(
    signals: Sequence[Signal],
) -> List[Signal]:

    return (
        create_scanner_filters(
            "intraday"
        )
        .apply(signals)
    )


def filter_swing(
    signals: Sequence[Signal],
) -> List[Signal]:

    return (
        create_scanner_filters(
            "swing"
        )
        .apply(signals)
    )


def filter_positional(
    signals: Sequence[Signal],
) -> List[Signal]:

    return (
        create_scanner_filters(
            "positional"
        )
        .apply(signals)
    )


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "FilterResult",

    "ScannerFilterConfig",

    "ScannerFilters",

    "FilterCallback",

    "create_scanner_filters",

    "filter_intraday",

    "filter_swing",

    "filter_positional",

]


# ==========================
# END OF FILE
# ==========================