"""
=========================================================
StockVersity Scanner Pro
Scanner Exceptions
Version : 2.0
=========================================================

Central exception hierarchy for StockVersity Scanner Pro.

Responsibilities
----------------
• Scanner runtime errors
• Configuration errors
• Market data errors
• Indicator errors
• Signal validation errors
• Scoring / ranking errors
• Registry / loader errors
• Engine errors
=========================================================
"""

from __future__ import annotations

from typing import Any
from typing import Dict
from typing import Optional


# =========================================================
# BASE EXCEPTION
# =========================================================

class StockVersityError(Exception):
    """
    Base exception for StockVersity Scanner Pro.

    All custom scanner exceptions should inherit
    from this class.
    """

    def __init__(
        self,
        message: str,
        *,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:

        self.message = str(message)

        self.code = code

        self.details = (
            dict(details)
            if details
            else {}
        )

        super().__init__(
            self.message
        )

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Return JSON-friendly exception information.
        """

        return {

            "type":
                self.__class__.__name__,

            "message":
                self.message,

            "code":
                self.code,

            "details":
                dict(self.details),
        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __str__(
        self,
    ) -> str:

        if self.code:

            return (
                f"[{self.code}] "
                f"{self.message}"
            )

        return self.message


# =========================================================
# SCANNER ERROR
# =========================================================

class ScannerError(StockVersityError):
    """
    General scanner execution error.
    """

    pass


# =========================================================
# CONFIGURATION ERROR
# =========================================================

class ConfigurationError(StockVersityError):
    """
    Invalid or missing scanner configuration.
    """

    pass


# =========================================================
# VALIDATION ERROR
# =========================================================

class ValidationError(StockVersityError):
    """
    Signal or input validation failure.
    """

    pass


# =========================================================
# MARKET DATA ERROR
# =========================================================

class MarketDataError(StockVersityError):
    """
    Invalid, missing, stale, or malformed market data.
    """

    pass


# =========================================================
# DATA NOT AVAILABLE ERROR
# =========================================================

class DataNotAvailableError(MarketDataError):
    """
    Required market data is unavailable.
    """

    pass


# =========================================================
# STALE DATA ERROR
# =========================================================

class StaleDataError(MarketDataError):
    """
    Market data is older than the permitted age.
    """

    pass


# =========================================================
# INDICATOR ERROR
# =========================================================

class IndicatorError(StockVersityError):
    """
    Indicator calculation failure.
    """

    pass


# =========================================================
# SCORING ERROR
# =========================================================

class ScoringError(StockVersityError):
    """
    Signal scoring failure.
    """

    pass


# =========================================================
# RANKING ERROR
# =========================================================

class RankingError(StockVersityError):
    """
    Signal ranking failure.
    """

    pass


# =========================================================
# FILTER ERROR
# =========================================================

class FilterError(StockVersityError):
    """
    Scanner filtering failure.
    """

    pass


# =========================================================
# SIGNAL ERROR
# =========================================================

class SignalError(StockVersityError):
    """
    Signal creation or processing failure.
    """

    pass


# =========================================================
# SIGNAL NOT FOUND
# =========================================================

class SignalNotFoundError(SignalError):
    """
    Requested signal could not be found.
    """

    pass


# =========================================================
# INVALID SIGNAL
# =========================================================

class InvalidSignalError(
    ValidationError,
    SignalError,
):
    """
    Signal failed structural or quality validation.
    """

    pass


# =========================================================
# REGISTRY ERROR
# =========================================================

class RegistryError(StockVersityError):
    """
    Scanner registry failure.
    """

    pass


# =========================================================
# SCANNER NOT REGISTERED
# =========================================================

class ScannerNotRegisteredError(RegistryError):
    """
    Requested scanner is not registered.
    """

    pass


# =========================================================
# SCANNER DISABLED
# =========================================================

class ScannerDisabledError(RegistryError):
    """
    Requested scanner is currently disabled.
    """

    pass


# =========================================================
# LOADER ERROR
# =========================================================

class ScannerLoaderError(StockVersityError):
    """
    Scanner discovery or loading failure.
    """

    pass


# =========================================================
# BOOTSTRAP ERROR
# =========================================================

class ScannerBootstrapError(StockVersityError):
    """
    Scanner bootstrap / initialization failure.
    """

    pass


# =========================================================
# ENGINE ERROR
# =========================================================

class ScannerEngineError(StockVersityError):
    """
    Scanner engine execution failure.
    """

    pass


# =========================================================
# TIMEFRAME ERROR
# =========================================================

class TimeframeError(StockVersityError):
    """
    Invalid or unsupported timeframe.
    """

    pass


# =========================================================
# SYMBOL ERROR
# =========================================================

class SymbolError(StockVersityError):
    """
    Invalid symbol or instrument information.
    """

    pass


# =========================================================
# INSTRUMENT ERROR
# =========================================================

class InstrumentError(StockVersityError):
    """
    Instrument lookup or mapping failure.
    """

    pass


# =========================================================
# RISK ERROR
# =========================================================

class RiskManagementError(StockVersityError):
    """
    Risk management calculation failure.
    """

    pass


# =========================================================
# POSITION SIZE ERROR
# =========================================================

class PositionSizeError(RiskManagementError):
    """
    Position sizing failure.
    """

    pass


# =========================================================
# ALERT ERROR
# =========================================================

class AlertError(StockVersityError):
    """
    Signal alert generation or dispatch failure.
    """

    pass


# =========================================================
# CACHE ERROR
# =========================================================

class CacheError(StockVersityError):
    """
    Scanner cache failure.
    """

    pass


# =========================================================
# SERIALIZATION ERROR
# =========================================================

class SerializationError(StockVersityError):
    """
    Serialization or deserialization failure.
    """

    pass


# =========================================================
# DEPENDENCY ERROR
# =========================================================

class DependencyError(StockVersityError):
    """
    Required scanner dependency is missing or unavailable.
    """

    pass


# =========================================================
# HELPER
# =========================================================

def exception_details(
    exc: BaseException,
) -> Dict[str, Any]:
    """
    Convert any exception into a standard diagnostic
    dictionary.

    Useful for:
    • logs
    • UI diagnostics
    • scanner health reports
    """

    if isinstance(
        exc,
        StockVersityError,
    ):

        return exc.to_dict()

    return {

        "type":
            type(exc).__name__,

        "message":
            str(exc),

        "code":
            None,

        "details":
            {},
    }


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "StockVersityError",

    "ScannerError",

    "ConfigurationError",

    "ValidationError",

    "MarketDataError",

    "DataNotAvailableError",

    "StaleDataError",

    "IndicatorError",

    "ScoringError",

    "RankingError",

    "FilterError",

    "SignalError",

    "SignalNotFoundError",

    "InvalidSignalError",

    "RegistryError",

    "ScannerNotRegisteredError",

    "ScannerDisabledError",

    "ScannerLoaderError",

    "ScannerBootstrapError",

    "ScannerEngineError",

    "TimeframeError",

    "SymbolError",

    "InstrumentError",

    "RiskManagementError",

    "PositionSizeError",

    "AlertError",

    "CacheError",

    "SerializationError",

    "DependencyError",

    "exception_details",
]


# ==========================
# END OF FILE
# ==========================