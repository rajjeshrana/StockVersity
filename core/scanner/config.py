"""
=========================================================
StockVersity Scanner Pro
Scanner Configuration
Version : 2.0
=========================================================

Central configuration for the scanner system.

Responsibilities
----------------
• Global scanner thresholds
• Risk / reward settings
• Market filters
• Intraday settings
• Swing settings
• Positional settings
• Volume / liquidity filters
• Alert thresholds
• Engine configuration
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Dict
from typing import List


# =========================================================
# GLOBAL CONSTANTS
# =========================================================

DEFAULT_EXCHANGE = "NSE"

DEFAULT_MARKET = "INDIA"

DEFAULT_CURRENCY = "INR"

DEFAULT_TIMEFRAME = "5m"


# =========================================================
# MARKET FILTERS
# =========================================================

@dataclass(slots=True)
class MarketFilterConfig:
    """
    Basic stock universe filters.
    """

    minimum_price: float = 200.0

    maximum_price: float = 100000.0

    minimum_market_cap: float = 1000.0

    minimum_volume: int = 100000

    minimum_average_volume: int = 100000

    minimum_volume_ratio: float = 1.20

    maximum_gap_percent: float = 3.0

    minimum_adx: float = 20.0

    exclude_large_gap_up: bool = True

    exclude_large_gap_down: bool = True

    require_volume_confirmation: bool = True

    require_liquidity: bool = True


# =========================================================
# RISK MANAGEMENT
# =========================================================

@dataclass(slots=True)
class RiskConfig:
    """
    Scanner-level risk management defaults.
    """

    capital: float = 100000.0

    risk_percent: float = 1.0

    minimum_rr: float = 2.0

    preferred_rr: float = 3.0

    maximum_rr_for_scoring: float = 5.0

    default_atr_multiple: float = 2.0

    maximum_stop_percent: float = 3.0

    minimum_stop_percent: float = 0.20


# =========================================================
# QUALITY FILTERS
# =========================================================

@dataclass(slots=True)
class QualityConfig:
    """
    Signal quality requirements.
    """

    minimum_score: float = 60.0

    good_score: float = 70.0

    high_quality_score: float = 80.0

    premium_score: float = 90.0

    minimum_confidence: float = 60.0

    high_confidence: float = 80.0

    premium_confidence: float = 90.0

    maximum_signals_per_scanner: int = 50

    maximum_dashboard_signals: int = 20


# =========================================================
# INTRADAY CONFIGURATION
# =========================================================

@dataclass(slots=True)
class IntradayConfig:
    """
    Intraday scanner configuration.
    """

    enabled: bool = True

    timeframes: List[str] = field(
        default_factory=lambda: [
            "1m",
            "3m",
            "5m",
            "10m",
            "15m",
            "30m",
            "45m",
        ]
    )

    primary_timeframe: str = "5m"

    minimum_volume_ratio: float = 1.50

    minimum_adx: float = 20.0

    minimum_score: float = 70.0

    minimum_confidence: float = 65.0

    minimum_rr: float = 2.0

    maximum_gap_percent: float = 3.0

    maximum_orb_width_percent: float = 3.0

    require_vwap_confirmation: bool = True

    require_volume_confirmation: bool = True

    require_market_alignment: bool = True


# =========================================================
# SWING CONFIGURATION
# =========================================================

@dataclass(slots=True)
class SwingConfig:
    """
    Swing trading scanner configuration.
    """

    enabled: bool = True

    timeframes: List[str] = field(
        default_factory=lambda: [
            "1h",
            "2h",
            "4h",
            "1d",
        ]
    )

    primary_timeframe: str = "1d"

    minimum_score: float = 70.0

    minimum_confidence: float = 65.0

    minimum_rr: float = 2.0

    minimum_volume_ratio: float = 1.20

    minimum_adx: float = 18.0

    require_trend_alignment: bool = True

    require_volume_confirmation: bool = True

    use_sector_strength: bool = True

    use_relative_strength: bool = True


# =========================================================
# POSITIONAL CONFIGURATION
# =========================================================

@dataclass(slots=True)
class PositionalConfig:
    """
    Positional scanner configuration.
    """

    enabled: bool = True

    timeframes: List[str] = field(
        default_factory=lambda: [
            "1d",
            "1w",
            "1M",
            "2M",
            "3M",
        ]
    )

    primary_timeframe: str = "1w"

    minimum_score: float = 70.0

    minimum_confidence: float = 65.0

    minimum_rr: float = 2.5

    minimum_volume_ratio: float = 1.10

    minimum_adx: float = 18.0

    require_long_term_trend: bool = True

    require_sector_strength: bool = True

    require_relative_strength: bool = True


# =========================================================
# MOMENTUM CONFIGURATION
# =========================================================

@dataclass(slots=True)
class MomentumConfig:
    """
    Momentum scanner settings.
    """

    minimum_rsi: float = 55.0

    maximum_rsi: float = 80.0

    minimum_adx: float = 20.0

    minimum_volume_ratio: float = 1.50

    require_macd_confirmation: bool = True

    require_ema_alignment: bool = True

    require_volume_confirmation: bool = True


# =========================================================
# BREAKOUT CONFIGURATION
# =========================================================

@dataclass(slots=True)
class BreakoutConfig:
    """
    Breakout / breakdown scanner settings.
    """

    minimum_volume_ratio: float = 1.50

    strong_volume_ratio: float = 2.0

    minimum_adx: float = 20.0

    maximum_gap_percent: float = 3.0

    require_volume_confirmation: bool = True

    reject_first_breakout_without_volume: bool = True

    require_close_confirmation: bool = True


# =========================================================
# ORB CONFIGURATION
# =========================================================

@dataclass(slots=True)
class ORBConfig:
    """
    Opening Range Breakout settings.
    """

    enabled: bool = True

    opening_range_minutes: int = 15

    minimum_volume_ratio: float = 1.50

    minimum_adx: float = 20.0

    maximum_range_percent: float = 3.0

    preferred_range_percent: float = 2.5

    require_vwap_confirmation: bool = True

    require_volume_confirmation: bool = True

    require_market_alignment: bool = True


# =========================================================
# ALERT CONFIGURATION
# =========================================================

@dataclass(slots=True)
class AlertConfig:
    """
    Scanner alert thresholds.
    """

    enabled: bool = True

    minimum_score: float = 85.0

    minimum_confidence: float = 80.0

    minimum_rr: float = 2.0

    minimum_volume_ratio: float = 1.50

    entry_proximity_percent: float = 0.25

    breakout_volume_ratio: float = 2.0

    suppress_duplicate_alerts: bool = True


# =========================================================
# ENGINE CONFIGURATION
# =========================================================

@dataclass(slots=True)
class EngineConfig:
    """
    Scanner engine runtime configuration.
    """

    parallel: bool = True

    max_workers: int = 8

    debug: bool = False

    remove_duplicates: bool = True

    rank_results: bool = True

    maximum_results: int = 100


# =========================================================
# SCANNER CONFIGURATION
# =========================================================

@dataclass(slots=True)
class ScannerConfig:
    """
    Master StockVersity scanner configuration.
    """

    exchange: str = DEFAULT_EXCHANGE

    market: str = DEFAULT_MARKET

    currency: str = DEFAULT_CURRENCY

    market_filter: MarketFilterConfig = field(
        default_factory=MarketFilterConfig
    )

    risk: RiskConfig = field(
        default_factory=RiskConfig
    )

    quality: QualityConfig = field(
        default_factory=QualityConfig
    )

    intraday: IntradayConfig = field(
        default_factory=IntradayConfig
    )

    swing: SwingConfig = field(
        default_factory=SwingConfig
    )

    positional: PositionalConfig = field(
        default_factory=PositionalConfig
    )

    momentum: MomentumConfig = field(
        default_factory=MomentumConfig
    )

    breakout: BreakoutConfig = field(
        default_factory=BreakoutConfig
    )

    orb: ORBConfig = field(
        default_factory=ORBConfig
    )

    alerts: AlertConfig = field(
        default_factory=AlertConfig
    )

    engine: EngineConfig = field(
        default_factory=EngineConfig
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate(self) -> List[str]:
        """
        Validate important configuration values.
        """

        errors: List[str] = []

        if self.market_filter.minimum_price < 0:
            errors.append(
                "minimum_price cannot be negative."
            )

        if self.market_filter.minimum_market_cap < 0:
            errors.append(
                "minimum_market_cap cannot be negative."
            )

        if self.risk.capital <= 0:
            errors.append(
                "capital must be greater than zero."
            )

        if self.risk.risk_percent <= 0:
            errors.append(
                "risk_percent must be greater than zero."
            )

        if self.risk.minimum_rr <= 0:
            errors.append(
                "minimum_rr must be greater than zero."
            )

        if not (
            0
            <= self.quality.minimum_score
            <= 100
        ):
            errors.append(
                "minimum_score must be between 0 and 100."
            )

        if not (
            0
            <= self.quality.minimum_confidence
            <= 100
        ):
            errors.append(
                "minimum_confidence must be between 0 and 100."
            )

        if self.engine.max_workers < 1:
            errors.append(
                "max_workers must be at least 1."
            )

        return errors

    # =====================================================
    # HEALTH
    # =====================================================

    @property
    def valid(self) -> bool:
        """
        True when configuration has no validation errors.
        """

        return not self.validate()

    # =====================================================
    # COMMON FILTERS
    # =====================================================

    def common_filters(
        self,
    ) -> Dict[str, Any]:
        """
        Return commonly used universe filters.
        """

        return {

            "minimum_price":
                self.market_filter.minimum_price,

            "minimum_market_cap":
                self.market_filter.minimum_market_cap,

            "minimum_volume":
                self.market_filter.minimum_volume,

            "minimum_volume_ratio":
                self.market_filter.minimum_volume_ratio,

            "maximum_gap_percent":
                self.market_filter.maximum_gap_percent,

            "minimum_adx":
                self.market_filter.minimum_adx,
        }

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> Dict[str, Any]:
        """
        Lightweight configuration summary.
        """

        return {

            "exchange":
                self.exchange,

            "market":
                self.market,

            "minimum_price":
                self.market_filter.minimum_price,

            "minimum_market_cap":
                self.market_filter.minimum_market_cap,

            "minimum_score":
                self.quality.minimum_score,

            "minimum_rr":
                self.risk.minimum_rr,

            "risk_percent":
                self.risk.risk_percent,

            "parallel":
                self.engine.parallel,

            "max_workers":
                self.engine.max_workers,

            "valid":
                self.valid,
        }


# =========================================================
# GLOBAL DEFAULT CONFIG
# =========================================================

scanner_config = ScannerConfig()


# =========================================================
# GET CONFIG
# =========================================================

def get_scanner_config() -> ScannerConfig:
    """
    Return global scanner configuration.
    """

    return scanner_config


# =========================================================
# RESET CONFIG
# =========================================================

def reset_scanner_config() -> ScannerConfig:
    """
    Reset global configuration to defaults.
    """

    global scanner_config

    scanner_config = ScannerConfig()

    return scanner_config


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "ScannerConfig",

    "MarketFilterConfig",

    "RiskConfig",

    "QualityConfig",

    "IntradayConfig",

    "SwingConfig",

    "PositionalConfig",

    "MomentumConfig",

    "BreakoutConfig",

    "ORBConfig",

    "AlertConfig",

    "EngineConfig",

    "scanner_config",

    "get_scanner_config",

    "reset_scanner_config",

    "DEFAULT_EXCHANGE",

    "DEFAULT_MARKET",

    "DEFAULT_CURRENCY",

    "DEFAULT_TIMEFRAME",
]


# ==========================
# END OF FILE
# ==========================