from __future__ import annotations

"""
==========================================================
StockVersity Scanner Pro
Settings Service

Author  : StockVersity
Version : 1.0.0

Responsibilities
----------------
• Application settings
• User preferences
• Theme management
• Scanner configuration
• Dashboard settings
• Alert settings
• Watchlist settings
• Risk management
• Window state
• Auto-save
• Import / Export
• Validation
• Backup / Restore
• Diagnostics
==========================================================
"""

import json
import logging
import threading

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional


# ==========================================================
# SETTINGS FILES
# ==========================================================

SETTINGS_DIRECTORY = Path("config")

SETTINGS_FILE = SETTINGS_DIRECTORY / "settings.json"

BACKUP_DIRECTORY = SETTINGS_DIRECTORY / "backup"


# ==========================================================
# THEME
# ==========================================================

class Theme(Enum):
    """
    Application theme.
    """

    LIGHT = "light"

    DARK = "dark"

    SYSTEM = "system"


# ==========================================================
# LOG LEVEL
# ==========================================================

class LogLevel(Enum):
    """
    Logging level.
    """

    DEBUG = "DEBUG"

    INFO = "INFO"

    WARNING = "WARNING"

    ERROR = "ERROR"

    CRITICAL = "CRITICAL"


# ==========================================================
# SETTINGS MODEL
# ==========================================================

@dataclass(slots=True)
class ApplicationSettings:
    """
    Global application settings.
    """

    version: str = "1.0.0"

    theme: Theme = Theme.DARK

    language: str = "en"

    auto_save: bool = True

    auto_backup: bool = True

    backup_count: int = 10

    log_level: LogLevel = LogLevel.INFO


# ==========================================================
# DASHBOARD SETTINGS
# ==========================================================

@dataclass(slots=True)
class DashboardSettings:
    """
    Dashboard preferences.
    """

    show_market_status: bool = True

    show_watchlist: bool = True

    show_alerts: bool = True

    show_scanner: bool = True

    refresh_interval: int = 5

    remember_layout: bool = True


# ==========================================================
# SCANNER SETTINGS
# ==========================================================

@dataclass(slots=True)
class ScannerSettings:
    """
    Scanner defaults.
    """

    auto_scan: bool = False

    scan_interval: int = 60

    max_results: int = 100

    enable_cache: bool = True

    cache_duration: int = 30


# ==========================================================
# ALERT SETTINGS
# ==========================================================

@dataclass(slots=True)
class AlertSettings:
    """
    Alert preferences.
    """

    desktop_notifications: bool = True

    sound_notifications: bool = True

    email_notifications: bool = False

    telegram_notifications: bool = False

    minimum_priority: str = "NORMAL"


# ==========================================================
# WATCHLIST SETTINGS
# ==========================================================

@dataclass(slots=True)
class WatchlistSettings:
    """
    Watchlist preferences.
    """

    auto_refresh: bool = True

    refresh_interval: int = 10

    default_watchlist: str = "My Watchlist"

    max_watchlists: int = 20


# ==========================================================
# RISK SETTINGS
# ==========================================================

@dataclass(slots=True)
class RiskSettings:
    """
    Trading preferences.
    """

    capital: float = 100000.0

    risk_per_trade: float = 1000.0

    default_rr: float = 2.0

    max_open_positions: int = 5


# ==========================================================
# SETTINGS STATISTICS
# ==========================================================

@dataclass(slots=True)
class SettingsStatistics:

    loads: int = 0

    saves: int = 0

    backups: int = 0

    restores: int = 0

    validation_errors: int = 0


# ==========================================================
# SETTINGS SERVICE
# ==========================================================

class SettingsService:
    """
    Central configuration service.
    """

    VERSION = "1.0.0"

    def __init__(self) -> None:

        self.logger = logging.getLogger(
            self.__class__.__name__
        )

        self.application = (
            ApplicationSettings()
        )

        self.dashboard = (
            DashboardSettings()
        )

        self.scanner = (
            ScannerSettings()
        )

        self.alerts = (
            AlertSettings()
        )

        self.watchlist = (
            WatchlistSettings()
        )

        self.risk = (
            RiskSettings()
        )

        self._statistics = (
            SettingsStatistics()
        )

        self._callbacks: Dict[
            str,
            List[Callable[..., None]]
        ] = {}

        self._lock = threading.RLock()

        self._started = datetime.now()

        SETTINGS_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        BACKUP_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.logger.info(
            "SettingsService initialized."
        )
            # ==========================================================
    # PROPERTIES
    # ==========================================================

    @property
    def statistics(self) -> SettingsStatistics:
        """
        Return runtime statistics.
        """

        return self._statistics

    @property
    def uptime(self):
        """
        Return service uptime.
        """

        return datetime.now() - self._started

    @property
    def started(self) -> datetime:
        """
        Return service start time.
        """

        return self._started

    # ==========================================================
    # EVENTS
    # ==========================================================

    def register_event(
        self,
        event: str,
        callback: Callable[..., None],
    ) -> None:
        """
        Register an event callback.
        """

        self._callbacks.setdefault(
            event,
            [],
        ).append(callback)

    def unregister_event(
        self,
        event: str,
        callback: Callable[..., None],
    ) -> None:
        """
        Remove an event callback.
        """

        callbacks = self._callbacks.get(event)

        if callbacks is None:

            return

        try:

            callbacks.remove(callback)

        except ValueError:

            pass

    def clear_events(self) -> None:
        """
        Remove all registered callbacks.
        """

        self._callbacks.clear()

    def _emit(
        self,
        event: str,
        **kwargs: Any,
    ) -> None:
        """
        Notify subscribers.
        """

        callbacks = self._callbacks.get(
            event,
            [],
        )

        for callback in callbacks:

            try:

                callback(**kwargs)

            except Exception:

                self.logger.exception(
                    "Settings callback failed."
                )

    # ==========================================================
    # SERIALIZATION
    # ==========================================================

    def _serialize(self) -> Dict[str, Any]:
        """
        Convert settings to JSON-safe dictionary.
        """

        def convert(value: Any) -> Any:

            if isinstance(
                value,
                Enum,
            ):

                return value.value

            if isinstance(
                value,
                dict,
            ):

                return {

                    k: convert(v)

                    for k, v

                    in value.items()

                }

            if isinstance(
                value,
                list,
            ):

                return [

                    convert(v)

                    for v

                    in value

                ]

            return value

        return {

            "application":

                convert(
                    asdict(
                        self.application
                    )
                ),

            "dashboard":

                convert(
                    asdict(
                        self.dashboard
                    )
                ),

            "scanner":

                convert(
                    asdict(
                        self.scanner
                    )
                ),

            "alerts":

                convert(
                    asdict(
                        self.alerts
                    )
                ),

            "watchlist":

                convert(
                    asdict(
                        self.watchlist
                    )
                ),

            "risk":

                convert(
                    asdict(
                        self.risk
                    )
                ),

        }

    # ==========================================================
    # SAVE
    # ==========================================================

    def save(self) -> bool:
        """
        Save settings to disk.
        """

        with self._lock:

            try:

                SETTINGS_FILE.write_text(

                    json.dumps(

                        self._serialize(),

                        indent=4,

                    ),

                    encoding="utf-8",

                )

                self._statistics.saves += 1

                self._emit(
                    "settings_saved",
                )

                return True

            except Exception:

                self.logger.exception(
                    "Unable to save settings."
                )

                return False

    # ==========================================================
    # LOAD
    # ==========================================================

    def load(self) -> bool:
        """
        Load settings from disk.
        """

        if not SETTINGS_FILE.exists():

            return False

        with self._lock:

            try:

                data = json.loads(

                    SETTINGS_FILE.read_text(

                        encoding="utf-8",

                    )

                )

                if "application" in data:

                    section = data["application"]

                    self.application.version = section.get(
                        "version",
                        self.application.version,
                    )

                    self.application.theme = Theme(

                        section.get(
                            "theme",
                            self.application.theme.value,
                        )
                    )

                    self.application.language = section.get(
                        "language",
                        self.application.language,
                    )

                    self.application.auto_save = section.get(
                        "auto_save",
                        self.application.auto_save,
                    )

                    self.application.auto_backup = section.get(
                        "auto_backup",
                        self.application.auto_backup,
                    )

                    self.application.backup_count = section.get(
                        "backup_count",
                        self.application.backup_count,
                    )

                    self.application.log_level = LogLevel(

                        section.get(
                            "log_level",
                            self.application.log_level.value,
                        )
                    )

                if "dashboard" in data:

                    for key, value in data["dashboard"].items():

                        if hasattr(
                            self.dashboard,
                            key,
                        ):

                            setattr(
                                self.dashboard,
                                key,
                                value,
                            )

                if "scanner" in data:

                    for key, value in data["scanner"].items():

                        if hasattr(
                            self.scanner,
                            key,
                        ):

                            setattr(
                                self.scanner,
                                key,
                                value,
                            )

                if "alerts" in data:

                    for key, value in data["alerts"].items():

                        if hasattr(
                            self.alerts,
                            key,
                        ):

                            setattr(
                                self.alerts,
                                key,
                                value,
                            )

                if "watchlist" in data:

                    for key, value in data["watchlist"].items():

                        if hasattr(
                            self.watchlist,
                            key,
                        ):

                            setattr(
                                self.watchlist,
                                key,
                                value,
                            )

                if "risk" in data:

                    for key, value in data["risk"].items():

                        if hasattr(
                            self.risk,
                            key,
                        ):

                            setattr(
                                self.risk,
                                key,
                                value,
                            )

                self._statistics.loads += 1

                self._emit(
                    "settings_loaded",
                )

                return True

            except Exception:

                self.logger.exception(
                    "Unable to load settings."
                )

                return False
                # ==========================================================
    # THEME MANAGEMENT
    # ==========================================================

    def theme(self) -> Theme:
        """
        Return current application theme.
        """

        return self.application.theme

    def set_theme(
        self,
        theme: Theme,
    ) -> None:
        """
        Update application theme.
        """

        if not isinstance(
            theme,
            Theme,
        ):

            raise TypeError(
                "Invalid theme."
            )

        self.application.theme = theme

        self._emit(

            "theme_changed",

            theme=theme,

        )

        if self.application.auto_save:

            self.save()

    # ==========================================================
    # GENERIC SETTINGS
    # ==========================================================

    def get(
        self,
        section: str,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Return a setting value.
        """

        obj = getattr(
            self,
            section,
            None,
        )

        if obj is None:

            return default

        return getattr(
            obj,
            key,
            default,
        )

    def set(
        self,
        section: str,
        key: str,
        value: Any,
    ) -> bool:
        """
        Update a setting.
        """

        obj = getattr(
            self,
            section,
            None,
        )

        if obj is None:

            return False

        if not hasattr(
            obj,
            key,
        ):

            return False

        setattr(
            obj,
            key,
            value,
        )

        self._emit(

            "setting_changed",

            section=section,

            key=key,

            value=value,

        )

        if self.application.auto_save:

            self.save()

        return True

    # ==========================================================
    # RESET
    # ==========================================================

    def reset_defaults(
        self,
    ) -> None:
        """
        Restore default configuration.
        """

        self.application = (
            ApplicationSettings()
        )

        self.dashboard = (
            DashboardSettings()
        )

        self.scanner = (
            ScannerSettings()
        )

        self.alerts = (
            AlertSettings()
        )

        self.watchlist = (
            WatchlistSettings()
        )

        self.risk = (
            RiskSettings()
        )

        self._emit(
            "defaults_restored",
        )

    # ==========================================================
    # VALIDATION
    # ==========================================================

    def validate(
        self,
    ) -> bool:
        """
        Validate settings.
        """

        valid = True

        if self.dashboard.refresh_interval < 1:

            valid = False

        if self.watchlist.refresh_interval < 1:

            valid = False

        if self.scanner.scan_interval < 1:

            valid = False

        if self.scanner.max_results < 1:

            valid = False

        if self.risk.capital <= 0:

            valid = False

        if self.risk.risk_per_trade <= 0:

            valid = False

        if not valid:

            self._statistics.validation_errors += 1

        return valid

    # ==========================================================
    # BACKUP
    # ==========================================================

    def backup(
        self,
    ) -> Path:
        """
        Create a backup of the settings.
        """

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        backup_file = (

            BACKUP_DIRECTORY

            / f"settings_{timestamp}.json"

        )

        backup_file.write_text(

            json.dumps(

                self._serialize(),

                indent=4,

            ),

            encoding="utf-8",

        )

        self._statistics.backups += 1

        self._emit(

            "backup_created",

            file=str(backup_file),

        )

        return backup_file

    # ==========================================================
    # RESTORE
    # ==========================================================

    def restore(
        self,
        backup_file: Path,
    ) -> bool:
        """
        Restore settings from backup.
        """

        if not backup_file.exists():

            return False

        try:

            SETTINGS_FILE.write_text(

                backup_file.read_text(
                    encoding="utf-8",
                ),

                encoding="utf-8",

            )

            self.load()

            self._statistics.restores += 1

            self._emit(

                "settings_restored",

                file=str(backup_file),

            )

            return True

        except Exception:

            self.logger.exception(
                "Failed to restore backup."
            )

            return False

    # ==========================================================
    # AUTO SAVE
    # ==========================================================

    def enable_auto_save(
        self,
        enabled: bool = True,
    ) -> None:
        """
        Enable or disable automatic saving.
        """

        self.application.auto_save = enabled

        self._emit(

            "auto_save_changed",

            enabled=enabled,

        )
            # ==========================================================
    # IMPORT / EXPORT
    # ==========================================================

    def export_settings(
        self,
        file_path: str,
    ) -> bool:
        """
        Export settings to a JSON file.
        """

        try:

            Path(file_path).write_text(

                json.dumps(

                    self._serialize(),

                    indent=4,

                ),

                encoding="utf-8",

            )

            self._emit(

                "settings_exported",

                file=file_path,

            )

            return True

        except Exception:

            self.logger.exception(
                "Failed to export settings."
            )

            return False

    def import_settings(
        self,
        file_path: str,
    ) -> bool:
        """
        Import settings from a JSON file.
        """

        path = Path(file_path)

        if not path.exists():

            return False

        try:

            SETTINGS_FILE.write_text(

                path.read_text(
                    encoding="utf-8",
                ),

                encoding="utf-8",

            )

            result = self.load()

            if result:

                self._emit(

                    "settings_imported",

                    file=file_path,

                )

            return result

        except Exception:

            self.logger.exception(
                "Failed to import settings."
            )

            return False

    # ==========================================================
    # WINDOW SETTINGS
    # ==========================================================

    def save_window_state(
        self,
        *,
        width: int,
        height: int,
        x: int,
        y: int,
        maximized: bool,
    ) -> None:
        """
        Save main window geometry.
        """

        self.set(
            "dashboard",
            "window_width",
            width,
        )

        self.set(
            "dashboard",
            "window_height",
            height,
        )

        self.set(
            "dashboard",
            "window_x",
            x,
        )

        self.set(
            "dashboard",
            "window_y",
            y,
        )

        self.set(
            "dashboard",
            "maximized",
            maximized,
        )

    def window_state(
        self,
    ) -> Dict[str, Any]:
        """
        Return stored window geometry.
        """

        return {

            "width":
                self.get(
                    "dashboard",
                    "window_width",
                    1600,
                ),

            "height":
                self.get(
                    "dashboard",
                    "window_height",
                    900,
                ),

            "x":
                self.get(
                    "dashboard",
                    "window_x",
                    100,
                ),

            "y":
                self.get(
                    "dashboard",
                    "window_y",
                    100,
                ),

            "maximized":
                self.get(
                    "dashboard",
                    "maximized",
                    False,
                ),

        }

    # ==========================================================
    # API SETTINGS
    # ==========================================================

    def set_api_credentials(
        self,
        *,
        api_key: str,
        api_secret: str,
        redirect_uri: str,
    ) -> None:
        """
        Store API credentials.
        """

        self.set(
            "application",
            "api_key",
            api_key,
        )

        self.set(
            "application",
            "api_secret",
            api_secret,
        )

        self.set(
            "application",
            "redirect_uri",
            redirect_uri,
        )

    def api_credentials(
        self,
    ) -> Dict[str, str]:
        """
        Return API credentials.
        """

        return {

            "api_key":
                self.get(
                    "application",
                    "api_key",
                    "",
                ),

            "api_secret":
                self.get(
                    "application",
                    "api_secret",
                    "",
                ),

            "redirect_uri":
                self.get(
                    "application",
                    "redirect_uri",
                    "",
                ),

        }

    # ==========================================================
    # SCANNER PROFILE
    # ==========================================================

    def scanner_profile(
        self,
    ) -> Dict[str, Any]:
        """
        Return scanner configuration.
        """

        return asdict(
            self.scanner,
        )

    # ==========================================================
    # ALERT PROFILE
    # ==========================================================

    def alert_profile(
        self,
    ) -> Dict[str, Any]:
        """
        Return alert configuration.
        """

        return asdict(
            self.alerts,
        )

    # ==========================================================
    # DASHBOARD PROFILE
    # ==========================================================

    def dashboard_profile(
        self,
    ) -> Dict[str, Any]:
        """
        Return dashboard configuration.
        """

        return asdict(
            self.dashboard,
        )

    # ==========================================================
    # RISK PROFILE
    # ==========================================================

    def risk_profile(
        self,
    ) -> Dict[str, Any]:
        """
        Return risk configuration.
        """

        return asdict(
            self.risk,
        )

    # ==========================================================
    # MIGRATION
    # ==========================================================

    def migrate(
        self,
        from_version: str,
        to_version: str,
    ) -> bool:
        """
        Placeholder for configuration migration.
        """

        self.logger.info(

            "Migrating settings %s -> %s",

            from_version,

            to_version,

        )

        self.application.version = to_version

        self._emit(

            "settings_migrated",

            from_version=from_version,

            to_version=to_version,

        )

        return True
        # ==========================================================
    # STATISTICS
    # ==========================================================

    def reset_statistics(self) -> None:
        """
        Reset runtime statistics.
        """

        self._statistics = SettingsStatistics()

        self.logger.info(
            "Settings statistics reset."
        )

    def statistics_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Return runtime statistics.
        """

        stats = self._statistics

        return {

            "loads":
                stats.loads,

            "saves":
                stats.saves,

            "backups":
                stats.backups,

            "restores":
                stats.restores,

            "validation_errors":
                stats.validation_errors,

            "uptime_seconds":
                int(
                    self.uptime.total_seconds()
                ),

        }

    # ==========================================================
    # HEALTH
    # ==========================================================

    def health(
        self,
    ) -> Dict[str, Any]:
        """
        Return service health.
        """

        return {

            "healthy":
                self.validate(),

            "settings_file":
                str(
                    SETTINGS_FILE
                ),

            "settings_exists":
                SETTINGS_FILE.exists(),

            "auto_save":
                self.application.auto_save,

            "auto_backup":
                self.application.auto_backup,

            "theme":
                self.application.theme.value,

            "uptime":
                str(
                    self.uptime
                ),

        }

    # ==========================================================
    # PERFORMANCE
    # ==========================================================

    def performance_report(
        self,
    ) -> Dict[str, Any]:
        """
        Return performance information.
        """

        stats = self.statistics_dict()

        operations = (

            stats["loads"]

            + stats["saves"]

            + stats["backups"]

            + stats["restores"]

        )

        return {

            "version":
                self.VERSION,

            "operations":
                operations,

            "loads":
                stats["loads"],

            "saves":
                stats["saves"],

            "backups":
                stats["backups"],

            "restores":
                stats["restores"],

            "validation_errors":
                stats["validation_errors"],

        }

    # ==========================================================
    # DIAGNOSTICS
    # ==========================================================

    def diagnostics(
        self,
    ) -> Dict[str, Any]:
        """
        Return diagnostic information.
        """

        return {

            "service":
                self.__class__.__name__,

            "version":
                self.VERSION,

            "health":
                self.health(),

            "statistics":
                self.statistics_dict(),

            "performance":
                self.performance_report(),

            "registered_events":
                {

                    event: len(callbacks)

                    for event, callbacks

                    in self._callbacks.items()

                },

        }

    # ==========================================================
    # SUMMARY
    # ==========================================================

    def summary(
        self,
    ) -> Dict[str, Any]:
        """
        Return concise service summary.
        """

        return {

            "service":
                self.__class__.__name__,

            "version":
                self.VERSION,

            "theme":
                self.application.theme.value,

            "language":
                self.application.language,

            "auto_save":
                self.application.auto_save,

            "uptime":
                str(
                    self.uptime
                ),

        }

    # ==========================================================
    # SNAPSHOT
    # ==========================================================

    def snapshot(
        self,
    ) -> Dict[str, Any]:
        """
        Return runtime snapshot.
        """

        return {

            "summary":
                self.summary(),

            "health":
                self.health(),

            "statistics":
                self.statistics_dict(),

            "performance":
                self.performance_report(),

            "configuration":
                self._serialize(),

        }

    # ==========================================================
    # INFORMATION
    # ==========================================================

    def info(
        self,
    ) -> Dict[str, Any]:
        """
        Return service information.
        """

        return {

            "service":
                self.__class__.__name__,

            "version":
                self.VERSION,

            "started":
                self.started,

            "uptime":
                str(
                    self.uptime
                ),

            "settings_file":
                str(
                    SETTINGS_FILE
                ),

        }
        # ==========================================================
    # LIFECYCLE
    # ==========================================================

    def start(self) -> None:
        """
        Start the SettingsService.
        """

        self.logger.info(
            "Starting SettingsService..."
        )

        self._started = datetime.now()

        self._emit(
            "service_started",
        )

    def stop(self) -> None:
        """
        Stop the SettingsService.
        """

        self.logger.info(
            "Stopping SettingsService..."
        )

        self._emit(
            "service_stopped",
        )

    def restart(self) -> None:
        """
        Restart the service.
        """

        self.stop()

        self.start()

    # ==========================================================
    # RESET
    # ==========================================================

    def reset(self) -> None:
        """
        Reset the service to defaults.
        """

        self.reset_defaults()

        self.reset_statistics()

        self._emit(
            "service_reset",
        )

    # ==========================================================
    # CLONE
    # ==========================================================

    def clone(self) -> "SettingsService":
        """
        Create a clone of the current service.
        """

        cloned = SettingsService()

        cloned.application = ApplicationSettings(
            **asdict(self.application)
        )

        cloned.dashboard = DashboardSettings(
            **asdict(self.dashboard)
        )

        cloned.scanner = ScannerSettings(
            **asdict(self.scanner)
        )

        cloned.alerts = AlertSettings(
            **asdict(self.alerts)
        )

        cloned.watchlist = WatchlistSettings(
            **asdict(self.watchlist)
        )

        cloned.risk = RiskSettings(
            **asdict(self.risk)
        )

        return cloned

    # ==========================================================
    # SERIALIZATION
    # ==========================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Return the complete configuration.
        """

        return self._serialize()

    def dump(self) -> Dict[str, Any]:
        """
        Dump runtime state.
        """

        return {

            "summary":
                self.summary(),

            "snapshot":
                self.snapshot(),

            "configuration":
                self.to_dict(),

            "statistics":
                self.statistics_dict(),

        }

    # ==========================================================
    # CLEANUP
    # ==========================================================

    def dispose(self) -> None:
        """
        Release resources.
        """

        self.clear_events()

        self.logger.info(
            "SettingsService disposed."
        )

    # ==========================================================
    # CONTEXT MANAGER
    # ==========================================================

    def __enter__(
        self,
    ) -> "SettingsService":

        self.start()

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:

        self.stop()

    # ==========================================================
    # REPRESENTATION
    # ==========================================================

    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"theme={self.application.theme.value}, "

            f"language={self.application.language})"

        )

    def __str__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}"

            f"[v{self.VERSION}]"

        )
        # ==========================================================
    # EVENT UTILITIES
    # ==========================================================

    def event_count(self) -> int:
        """
        Return total registered callbacks.
        """

        return sum(

            len(callbacks)

            for callbacks

            in self._callbacks.values()

        )

    def events(self) -> Dict[str, int]:
        """
        Return registered event summary.
        """

        return {

            event: len(callbacks)

            for event, callbacks

            in self._callbacks.items()

        }

    def has_event(
        self,
        event: str,
    ) -> bool:
        """
        Return True if an event has subscribers.
        """

        return (

            event in self._callbacks

            and

            len(self._callbacks[event]) > 0

        )

    # ==========================================================
    # SETTINGS UTILITIES
    # ==========================================================

    def exists(
        self,
        section: str,
        key: str,
    ) -> bool:
        """
        Check whether a setting exists.
        """

        obj = getattr(
            self,
            section,
            None,
        )

        if obj is None:

            return False

        return hasattr(
            obj,
            key,
        )

    def sections(
        self,
    ) -> List[str]:
        """
        Return available configuration sections.
        """

        return sorted(

            [

                "alerts",

                "application",

                "dashboard",

                "risk",

                "scanner",

                "watchlist",

            ]

        )

    def keys(
        self,
        section: str,
    ) -> List[str]:
        """
        Return keys within a section.
        """

        obj = getattr(
            self,
            section,
            None,
        )

        if obj is None:

            return []

        return sorted(

            vars(obj).keys()

        )

    # ==========================================================
    # CONFIGURATION
    # ==========================================================

    def configuration(
        self,
    ) -> Dict[str, Any]:
        """
        Return the complete configuration.
        """

        return self.to_dict()

    def configuration_size(
        self,
    ) -> int:
        """
        Return approximate configuration size in bytes.
        """

        return len(

            json.dumps(

                self._serialize(),

            ).encode(

                "utf-8",

            )

        )

    # ==========================================================
    # VALIDATION HELPERS
    # ==========================================================

    def assert_valid(
        self,
    ) -> None:
        """
        Raise if configuration is invalid.
        """

        if not self.validate():

            raise RuntimeError(
                "Settings validation failed."
            )

    # ==========================================================
    # FACTORY
    # ==========================================================

    @classmethod
    def create(
        cls,
    ) -> "SettingsService":
        """
        Factory constructor.
        """

        service = cls()

        service.load()

        return service


# ==========================================================
# MODULE HELPERS
# ==========================================================

def create_settings_service(
) -> SettingsService:
    """
    Convenience factory.
    """

    return SettingsService.create()


def build_settings_service(
) -> SettingsService:
    """
    Alternate factory helper.
    """

    return SettingsService()
# ==========================================================
# MODULE EXPORTS
# ==========================================================

__all__ = [

    # Constants
    "SETTINGS_DIRECTORY",
    "SETTINGS_FILE",
    "BACKUP_DIRECTORY",

    # Enums
    "Theme",
    "LogLevel",

    # Models
    "ApplicationSettings",
    "DashboardSettings",
    "ScannerSettings",
    "AlertSettings",
    "WatchlistSettings",
    "RiskSettings",
    "SettingsStatistics",

    # Service
    "SettingsService",

    # Factory Helpers
    "create_settings_service",
    "build_settings_service",

]

# ==========================================================
# END OF FILE
# ==========================================================