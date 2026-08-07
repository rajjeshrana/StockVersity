"""
==========================================================
StockVersity Scanner Pro
Configuration Manager
Version : 4.0
Powered By : AI
==========================================================
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict


class ConfigurationManager:
    """
    Central configuration manager for the application.

    Responsible for:
        • Application settings
        • Scanner configuration
        • Risk configuration
        • Dashboard preferences
        • Theme settings
        • User preferences
    """

    DEFAULT_FILE = "config/settings.json"

    def __init__(self):

        self.logger = logging.getLogger(
            "ConfigurationManager"
        )

        self.config_path = Path(
            self.DEFAULT_FILE
        )

        self.config: Dict[str, Any] = {}

        self.load()

    # ==================================================
    # DEFAULT CONFIGURATION
    # ==================================================

    def default_configuration(self):

        return {

            "application": {

                "name":
                    "StockVersity Scanner Pro",

                "version":
                    "4.0",

                "powered_by":
                    "AI",

                "theme":
                    "Dark",

                "auto_save":
                    True,

                "language":
                    "English",

                "refresh_interval":
                    60
            },

            "scanner": {

                "market":
                    "NSE",

                "scan_interval":
                    60,

                "max_results":
                    5,

                "minimum_price":
                    200,

                "minimum_market_cap":
                    1000,

                "volume_multiplier":
                    2.0,

                "minimum_rvol":
                    1.5,

                "enable_intraday":
                    True,

                "enable_swing":
                    True,

                "enable_positional":
                    True
            },

            "risk": {

                "capital":
                    100000,

                "risk_per_trade":
                    1000,

                "max_open_positions":
                    5,

                "reward_ratio":
                    2,

                "daily_loss_limit":
                    3000,

                "trailing_stop":
                    True
            },

            "dashboard": {

                "show_heatmap":
                    True,

                "show_sector_rotation":
                    True,

                "show_market_breadth":
                    True,

                "show_news":
                    False,

                "show_watchlist":
                    True
            },

            "watchlist": [],

            "recent_scans": []
        }

    # ==================================================
    # LOAD
    # ==================================================

    def load(self):

        try:

            if not self.config_path.exists():

                self.logger.info(
                    "Creating Default Configuration"
                )

                self.config = self.default_configuration()

                self.save()

                return

            with open(

                self.config_path,

                "r",

                encoding="utf-8"

            ) as file:

                self.config = json.load(file)

        except Exception as e:

            self.logger.exception(e)

            self.config = self.default_configuration()

    # ==================================================
    # SAVE
    # ==================================================

    def save(self):

        self.config_path.parent.mkdir(

            parents=True,

            exist_ok=True

        )

        with open(

            self.config_path,

            "w",

            encoding="utf-8"

        ) as file:

            json.dump(

                self.config,

                file,

                indent=4

            )

    # ==================================================
    # GET
    # ==================================================

    def get(

        self,

        key,

        default=None

    ):

        return self.config.get(

            key,

            default

        )

    # ==================================================
    # SET
    # ==================================================

    def set(

        self,

        key,

        value

    ):

        self.config[key] = value

    # ==================================================
    # RESET
    # ==================================================

    def reset(self):

        self.config = self.default_configuration()

        self.save()
            # ==================================================
    # APPLICATION SETTINGS
    # ==================================================

    @property
    def application(self):

        return self.config.setdefault(
            "application",
            {}
        )

    @property
    def scanner(self):

        return self.config.setdefault(
            "scanner",
            {}
        )

    @property
    def risk(self):

        return self.config.setdefault(
            "risk",
            {}
        )

    @property
    def dashboard(self):

        return self.config.setdefault(
            "dashboard",
            {}
        )

    # ==================================================
    # THEME
    # ==================================================

    def theme(self):

        return self.application.get(
            "theme",
            "Dark"
        )

    def set_theme(

        self,

        theme: str

    ):

        self.application["theme"] = theme

        self.save()

    # ==================================================
    # REFRESH INTERVAL
    # ==================================================

    def refresh_interval(self):

        return self.application.get(
            "refresh_interval",
            60
        )

    def set_refresh_interval(

        self,

        seconds: int

    ):

        self.application[
            "refresh_interval"
        ] = max(5, int(seconds))

        self.save()

    # ==================================================
    # SCANNER SETTINGS
    # ==================================================

    def scanner_setting(

        self,

        key,

        default=None

    ):

        return self.scanner.get(
            key,
            default
        )

    def set_scanner_setting(

        self,

        key,

        value

    ):

        self.scanner[key] = value

        self.save()

    # ==================================================
    # RISK SETTINGS
    # ==================================================

    def risk_setting(

        self,

        key,

        default=None

    ):

        return self.risk.get(
            key,
            default
        )

    def set_risk_setting(

        self,

        key,

        value

    ):

        self.risk[key] = value

        self.save()

    # ==================================================
    # DASHBOARD SETTINGS
    # ==================================================

    def dashboard_setting(

        self,

        key,

        default=None

    ):

        return self.dashboard.get(
            key,
            default
        )

    def set_dashboard_setting(

        self,

        key,

        value

    ):

        self.dashboard[key] = value

        self.save()

    # ==================================================
    # WATCHLIST
    # ==================================================

    def watchlist(self):

        return self.config.setdefault(
            "watchlist",
            []
        )

    def add_watchlist(

        self,

        symbol: str

    ):

        symbol = symbol.upper()

        watchlist = self.watchlist()

        if symbol not in watchlist:

            watchlist.append(symbol)

            self.save()

    def remove_watchlist(

        self,

        symbol: str

    ):

        symbol = symbol.upper()

        watchlist = self.watchlist()

        if symbol in watchlist:

            watchlist.remove(symbol)

            self.save()

    def clear_watchlist(self):

        self.config["watchlist"] = []

        self.save()

    # ==================================================
    # RECENT SCANS
    # ==================================================

    def recent_scans(self):

        return self.config.setdefault(
            "recent_scans",
            []
        )

    def add_recent_scan(

        self,

        scan_data: dict

    ):

        scans = self.recent_scans()

        scans.insert(0, scan_data)

        self.config["recent_scans"] = scans[:100]

        self.save()

    def clear_recent_scans(self):

        self.config["recent_scans"] = []

        self.save()

    # ==================================================
    # EXPORT
    # ==================================================

    def export(self):

        return self.config.copy()

    # ==================================================
    # IMPORT
    # ==================================================

    def import_configuration(

        self,

        configuration: dict

    ):

        self.config = configuration

        self.save()

    # ==================================================
    # VALIDATION
    # ==================================================

    def validate(self):

        required = [

            "application",

            "scanner",

            "risk",

            "dashboard"

        ]

        for section in required:

            if section not in self.config:

                return False

        return True
        # ==================================================
    # BACKUP CONFIGURATION
    # ==================================================

    def backup(

        self,

        file_path: str

    ):

        path = Path(file_path)

        path.parent.mkdir(

            parents=True,

            exist_ok=True

        )

        with open(

            path,

            "w",

            encoding="utf-8"

        ) as file:

            json.dump(

                self.config,

                file,

                indent=4

            )

        self.logger.info(

            f"Configuration backed up to {path}"

        )

        return True

    # ==================================================
    # RESTORE CONFIGURATION
    # ==================================================

    def restore(

        self,

        file_path: str

    ):

        path = Path(file_path)

        if not path.exists():

            raise FileNotFoundError(path)

        with open(

            path,

            "r",

            encoding="utf-8"

        ) as file:

            self.config = json.load(file)

        self.save()

        self.logger.info(

            "Configuration restored."

        )

    # ==================================================
    # JSON
    # ==================================================

    def to_json(self):

        return json.dumps(

            self.config,

            indent=4

        )

    # ==================================================
    # LOAD JSON STRING
    # ==================================================

    def from_json(

        self,

        json_string: str

    ):

        self.config = json.loads(

            json_string

        )

        self.save()

    # ==================================================
    # BUILD INFORMATION
    # ==================================================

    def build_information(self):

        return {

            "application":
                "StockVersity Scanner Pro",

            "version":
                "4.0",

            "powered_by":
                "AI",

            "python":
                "3.14",

            "framework":
                "PySide6"
        }

    # ==================================================
    # RUNTIME INFORMATION
    # ==================================================

    def runtime_information(self):

        return {

            "configuration_file":

                str(self.config_path),

            "configuration_loaded":

                bool(self.config),

            "sections":

                list(self.config.keys()),

            "total_sections":

                len(self.config)

        }

    # ==================================================
    # SYSTEM INFORMATION
    # ==================================================

    def system_information(self):

        return {

            "build":

                self.build_information(),

            "runtime":

                self.runtime_information()

        }

    # ==================================================
    # LOG SYSTEM INFORMATION
    # ==================================================

    def log_system_information(self):

        report = self.system_information()

        self.logger.info(report)

        return report

    # ==================================================
    # RELOAD
    # ==================================================

    def reload(self):

        self.load()

    # ==================================================
    # SHUTDOWN
    # ==================================================

    def shutdown(self):

        try:

            self.save()

        except Exception as e:

            self.logger.exception(e)

    # ==================================================
    # CONTEXT MANAGER
    # ==================================================

    def __enter__(self):

        return self

    def __exit__(

        self,

        exc_type,

        exc_value,

        traceback

    ):

        self.shutdown()

    # ==================================================
    # STRING REPRESENTATION
    # ==================================================

    def __repr__(self):

        return (

            f"<ConfigurationManager "

            f"sections={len(self.config)} "

            f"path='{self.config_path}'>"

        )


# ======================================================
# GLOBAL INSTANCE
# ======================================================

_configuration = None


def get_configuration() -> ConfigurationManager:

    global _configuration

    if _configuration is None:

        _configuration = ConfigurationManager()

    return _configuration


def reset_configuration():

    global _configuration

    if _configuration is not None:

        try:

            _configuration.shutdown()

        except Exception:

            pass

    _configuration = None


# ======================================================
# END OF FILE
# ======================================================