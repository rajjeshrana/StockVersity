"""
=========================================================
StockVersity Scanner Pro v4.0
Backend Models Package
=========================================================

This package contains all business models used throughout
the application.

Models
------
MarketData
Opportunity
ScanResult

Author:
StockVersity AI

Version:
4.0
"""

from .market_data import MarketData
from .opportunity import Opportunity
from .scan_result import ScanResult

__all__ = [
    "MarketData",
    "Opportunity",
    "ScanResult",
]

__version__ = "4.0"