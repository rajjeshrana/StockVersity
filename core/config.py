from __future__ import annotations

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List

# =====================================================
# APPLICATION
# =====================================================

APP_NAME = "StockVersity Scanner Pro"

APP_VERSION = "4.0"

APP_AUTHOR = "StockVersity AI"

APP_COMPANY = "StockVersity"

APP_DESCRIPTION = (
    "AI Powered Stock Scanner for Indian Markets"
)

POWERED_BY = "AI"

# =====================================================
# PATHS
# =====================================================

BASE_DIR = Path(__file__).resolve().parents[2]

BACKEND_DIR = BASE_DIR / "backend"

UI_DIR = BASE_DIR / "ui"

DATA_DIR = BASE_DIR / "data"

CACHE_DIR = DATA_DIR / "cache"

DATABASE_DIR = DATA_DIR / "database"

EXPORT_DIR = DATA_DIR / "exports"

LOG_DIR = DATA_DIR / "logs"

MODEL_DIR = DATA_DIR / "models"

TEMP_DIR = DATA_DIR / "temp"

SETTINGS_DIR = DATA_DIR / "settings"

# -----------------------------------------------------

DIRECTORIES = [

    DATA_DIR,

    CACHE_DIR,

    DATABASE_DIR,

    EXPORT_DIR,

    LOG_DIR,

    MODEL_DIR,

    TEMP_DIR,

    SETTINGS_DIR,

]

# =====================================================
# CREATE DIRECTORIES
# =====================================================

for directory in DIRECTORIES:

    directory.mkdir(

        parents=True,

        exist_ok=True,

    )

# =====================================================
# DATABASE
# =====================================================

DATABASE_FILE = (

    DATABASE_DIR

    / "stockversity.db"

)

DATABASE_BACKUP = (

    DATABASE_DIR

    / "backup"

)

DATABASE_TIMEOUT = 30

DATABASE_POOL_SIZE = 10

# =====================================================
# CACHE
# =====================================================

CACHE_FILE = (

    CACHE_DIR

    / "cache.pkl"

)

CACHE_TIMEOUT = 300

CACHE_MAX_ITEMS = 5000

# =====================================================
# LOGGING
# =====================================================

LOG_FILE = (

    LOG_DIR

    / "stockversity.log"

)

LOG_LEVEL = "INFO"

LOG_FORMAT = (

    "%(asctime)s | "

    "%(levelname)s | "

    "%(name)s | "

    "%(message)s"

)

# =====================================================
# API
# =====================================================

YAHOO_TIMEOUT = 10

NSE_TIMEOUT = 10

MAX_RETRIES = 3

REQUEST_DELAY = 0.25

MAX_WORKERS = 10

# =====================================================
# MARKET
# =====================================================

MARKET_OPEN_HOUR = 9

MARKET_OPEN_MINUTE = 15

MARKET_CLOSE_HOUR = 15

MARKET_CLOSE_MINUTE = 30

PRE_OPEN_HOUR = 9

PRE_OPEN_MINUTE = 0

REFRESH_INTERVAL = 30

# =====================================================
# SCANNER
# =====================================================

DEFAULT_EXCHANGE = "NSE"

DEFAULT_TIMEFRAME = "DAY"

DEFAULT_SCAN_LIMIT = 100

DEFAULT_TOP_RESULTS = 25

DEFAULT_MIN_VOLUME = 100000

DEFAULT_MIN_PRICE = 20

DEFAULT_MAX_PRICE = 50000

DEFAULT_MARKET_CAP = 1000

DEFAULT_RISK_PERCENT = 1

DEFAULT_REWARD_RATIO = 2

# =====================================================
# AI
# =====================================================

AI_SCORE_THRESHOLD = 80

AI_CONFIDENCE_THRESHOLD = 75

AI_PROBABILITY_THRESHOLD = 70

AI_BUY_SCORE = 85

AI_SELL_SCORE = 30

AI_MODEL_VERSION = "4.0"

# =====================================================
# EXPORT
# =====================================================

EXPORT_FORMATS = [

    "csv",

    "xlsx",

    "json",

]

DEFAULT_EXPORT = "xlsx"

# =====================================================
# SUPPORTED TIMEFRAMES
# =====================================================

SUPPORTED_TIMEFRAMES = [

    "1m",

    "3m",

    "5m",

    "15m",

    "30m",

    "45m",

    "1h",

    "2h",

    "4h",

    "1d",

    "1w",

    "1mo",

]
# =====================================================
# UI CONFIGURATION
# =====================================================

WINDOW_TITLE = APP_NAME

WINDOW_WIDTH = 1600

WINDOW_HEIGHT = 950

WINDOW_MIN_WIDTH = 1280

WINDOW_MIN_HEIGHT = 720

SIDEBAR_WIDTH = 260

HEADER_HEIGHT = 70

STATUSBAR_HEIGHT = 28

DEFAULT_FONT = "Segoe UI"

DEFAULT_FONT_SIZE = 10

TITLE_FONT_SIZE = 18

CARD_RADIUS = 12

TABLE_ROW_HEIGHT = 32

ENABLE_ANIMATIONS = True

AUTO_REFRESH_UI = True

UI_REFRESH_INTERVAL = 1000  # milliseconds

# =====================================================
# DASHBOARD
# =====================================================

DASHBOARD_CARD_COUNT = 8

DASHBOARD_TOP_GAINERS = 10

DASHBOARD_TOP_LOSERS = 10

DASHBOARD_TOP_VOLUME = 10

DASHBOARD_TOP_AI = 20

SHOW_MARKET_STATUS = True

SHOW_AI_SCORE = True

SHOW_MARKET_BREADTH = True

SHOW_SECTOR_ROTATION = True

# =====================================================
# THEME
# =====================================================

DEFAULT_THEME = "dark"

AVAILABLE_THEMES = [

    "dark",

    "light",

]

# =====================================================
# COLORS
# =====================================================

COLORS = {

    "primary": "#2962FF",

    "secondary": "#455A64",

    "success": "#00C853",

    "danger": "#D50000",

    "warning": "#FFAB00",

    "info": "#00B8D4",

    "background_dark": "#121212",

    "background_light": "#F5F5F5",

    "surface_dark": "#1E1E1E",

    "surface_light": "#FFFFFF",

    "text_dark": "#FFFFFF",

    "text_light": "#202124",

    "border": "#2C2C2C",

}

# =====================================================
# TABLE CONFIGURATION
# =====================================================

TABLE_COLUMNS = [

    "Rank",

    "Symbol",

    "Company",

    "Sector",

    "Price",

    "Change %",

    "Volume",

    "RVOL",

    "Pattern",

    "Signal",

    "AI Score",

    "Confidence",

    "Probability",

]

# =====================================================
# CHART SETTINGS
# =====================================================

CHART_CANDLE_LIMIT = 300

CHART_DEFAULT_INTERVAL = "1d"

CHART_ENABLE_VOLUME = True

CHART_ENABLE_VWAP = True

CHART_ENABLE_EMA = True

DEFAULT_EMAS = [

    9,

    20,

    50,

    200,

]

# =====================================================
# SCANNER PRESETS
# =====================================================

SCANNER_PRESETS = {

    "Intraday": {

        "timeframe": "5m",

        "min_volume": 500000,

        "min_ai_score": 80,

    },

    "Swing": {

        "timeframe": "1d",

        "min_volume": 200000,

        "min_ai_score": 75,

    },

    "Positional": {

        "timeframe": "1w",

        "min_volume": 100000,

        "min_ai_score": 70,

    },

}

# =====================================================
# RISK MANAGEMENT
# =====================================================

MAX_OPEN_TRADES = 5

DEFAULT_CAPITAL = 100000

DEFAULT_POSITION_RISK = 1.0

MAX_POSITION_RISK = 2.0

DEFAULT_RR = 2.0

TRAILING_STOP_ENABLED = True

MOVE_SL_TO_COST = True

# =====================================================
# ENVIRONMENT
# =====================================================

ENVIRONMENT = os.getenv(

    "STOCKVERSITY_ENV",

    "production",

)

DEBUG = os.getenv(

    "STOCKVERSITY_DEBUG",

    "false",

).lower() == "true"

ENABLE_CACHE = os.getenv(

    "STOCKVERSITY_CACHE",

    "true",

).lower() == "true"

ENABLE_DATABASE = os.getenv(

    "STOCKVERSITY_DATABASE",

    "true",

).lower() == "true"

ENABLE_AI = os.getenv(

    "STOCKVERSITY_AI",

    "true",

).lower() == "true"

ENABLE_LOGGING = os.getenv(

    "STOCKVERSITY_LOGGING",

    "true",

).lower() == "true"

API_KEY = os.getenv(

    "STOCKVERSITY_API_KEY",

    "",

)

# =====================================================
# UPSTOX CONFIGURATION
# =====================================================

UPSTOX_API_KEY = os.getenv(
    "UPSTOX_API_KEY",
    "",
)

UPSTOX_API_SECRET = os.getenv(
    "UPSTOX_API_SECRET",
    "",
)

UPSTOX_REDIRECT_URI = os.getenv(
    "UPSTOX_REDIRECT_URI",
    "",
)

# =====================================================
# CONFIGURATION MODEL
# =====================================================

@dataclass(slots=True)
class AppConfig:

    app_name: str = APP_NAME

    version: str = APP_VERSION

    author: str = APP_AUTHOR

    company: str = APP_COMPANY

    environment: str = ENVIRONMENT

    debug: bool = DEBUG

    refresh_interval: int = REFRESH_INTERVAL

    cache_timeout: int = CACHE_TIMEOUT

    cache_max_items: int = CACHE_MAX_ITEMS

    database_file: Path = DATABASE_FILE

    log_file: Path = LOG_FILE

    theme: str = DEFAULT_THEME

    exchange: str = DEFAULT_EXCHANGE

    timeframe: str = DEFAULT_TIMEFRAME

    capital: float = DEFAULT_CAPITAL

    risk_percent: float = DEFAULT_POSITION_RISK

    reward_ratio: float = DEFAULT_RR

    api_key: str = API_KEY

    upstox_api_key: str = UPSTOX_API_KEY
    upstox_api_secret: str = UPSTOX_API_SECRET
    upstox_redirect_uri: str = UPSTOX_REDIRECT_URI

    metadata: Dict[str, str] = field(
        default_factory=dict
    )

    # -------------------------------------------------

    def to_dict(self):

        return {

            "app_name": self.app_name,

            "version": self.version,

            "author": self.author,

            "company": self.company,

            "environment": self.environment,

            "debug": self.debug,

            "refresh_interval": self.refresh_interval,

            "cache_timeout": self.cache_timeout,

            "cache_max_items": self.cache_max_items,

            "database_file": str(self.database_file),

            "log_file": str(self.log_file),

            "theme": self.theme,

            "exchange": self.exchange,

            "timeframe": self.timeframe,

            "capital": self.capital,

            "risk_percent": self.risk_percent,

            "reward_ratio": self.reward_ratio,

            "api_key": self.api_key,

            "upstox_api_key": self.upstox_api_key,
            "upstox_api_secret": self.upstox_api_secret,
            "upstox_redirect_uri": self.upstox_redirect_uri,

            "metadata": self.metadata,

        }

    # -------------------------------------------------

    @classmethod
    def from_environment(cls):

        return cls(

            environment=ENVIRONMENT,

            debug=DEBUG,

            refresh_interval=REFRESH_INTERVAL,

            cache_timeout=CACHE_TIMEOUT,

            cache_max_items=CACHE_MAX_ITEMS,

            api_key=API_KEY,

            upstox_api_key=UPSTOX_API_KEY,
            upstox_api_secret=UPSTOX_API_SECRET,
            upstox_redirect_uri=UPSTOX_REDIRECT_URI,

        )


# =====================================================
# CONFIGURATION MANAGER
# =====================================================

class ConfigManager:

    def __init__(self):

        self.config = AppConfig()

    # -------------------------------------------------

    def load_from_environment(self):

        self.config = AppConfig.from_environment()

        return self.config

    # -------------------------------------------------

    def validate(self):

        if self.config.refresh_interval <= 0:

            raise ValueError(
                "Refresh interval must be greater than zero."
            )

        if self.config.cache_timeout <= 0:

            raise ValueError(
                "Cache timeout must be greater than zero."
            )

        if self.config.cache_max_items <= 0:

            raise ValueError(
                "Cache size must be greater than zero."
            )

        if self.config.risk_percent <= 0:

            raise ValueError(
                "Risk percent must be greater than zero."
            )

        if self.config.reward_ratio <= 0:

            raise ValueError(
                "Reward ratio must be greater than zero."
            )

        return True

    # -------------------------------------------------

    def ensure_directories(self):

        for directory in DIRECTORIES:

            directory.mkdir(

                parents=True,

                exist_ok=True,

            )

    # -------------------------------------------------

    def database_path(self):

        return self.config.database_file

    # -------------------------------------------------

    def cache_path(self):

        return CACHE_FILE

    # -------------------------------------------------

    def log_path(self):

        return self.config.log_file

    # -------------------------------------------------

    def export_path(self):

        return EXPORT_DIR

    # -------------------------------------------------

    def temp_path(self):

        return TEMP_DIR

    # -------------------------------------------------

    def settings_path(self):

        return SETTINGS_DIR

    # -------------------------------------------------

    def model_path(self):

        return MODEL_DIR

    # -------------------------------------------------

    def to_dict(self):

        return self.config.to_dict()

    # -------------------------------------------------

    def __repr__(self):

        return (

            "ConfigManager("

            f"environment='{self.config.environment}', "

            f"theme='{self.config.theme}', "

            f"version='{self.config.version}')"

        )

    # -------------------------------------------------

    def __str__(self):

        return (

            f"{self.config.app_name} "

            f"v{self.config.version}\n"

            f"Environment : {self.config.environment}\n"

            f"Theme       : {self.config.theme}\n"

            f"Exchange    : {self.config.exchange}\n"

            f"Timeframe   : {self.config.timeframe}"

        )


# =====================================================
# GLOBAL CONFIGURATION
# =====================================================

config = AppConfig()

config_manager = ConfigManager()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "APP_NAME",
    "APP_VERSION",
    "APP_AUTHOR",
    "APP_COMPANY",

    "BASE_DIR",
    "BACKEND_DIR",
    "UI_DIR",
    "DATA_DIR",
    "CACHE_DIR",
    "DATABASE_DIR",
    "EXPORT_DIR",
    "LOG_DIR",
    "MODEL_DIR",
    "TEMP_DIR",
    "SETTINGS_DIR",

    "DATABASE_FILE",
    "CACHE_FILE",
    "LOG_FILE",

    "UPSTOX_API_KEY",
    "UPSTOX_API_SECRET",
    "UPSTOX_REDIRECT_URI",

    "COLORS",
    "TABLE_COLUMNS",
    "SUPPORTED_TIMEFRAMES",
    "SCANNER_PRESETS",

    "AppConfig",
    "ConfigManager",

    "config",
    "config_manager",

]