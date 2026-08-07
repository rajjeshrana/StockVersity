from __future__ import annotations

"""
==========================================================
StockVersity Scanner Pro
Theme Service

Author  : StockVersity
Version : 1.0.0

Responsibilities
----------------
• Theme management
• Dark / Light mode
• Accent colors
• Font management
• Stylesheet loading
• Dynamic theme switching
• Icon themes
• High DPI support
• User themes
• Theme persistence
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

from PySide6.QtCore import QObject
from PySide6.QtGui import QColor
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from services.settings_service import (
    SettingsService,
)

# ==========================================================
# DIRECTORIES
# ==========================================================

THEME_DIRECTORY = Path("resources/themes")

STYLE_DIRECTORY = THEME_DIRECTORY / "styles"

ICON_DIRECTORY = THEME_DIRECTORY / "icons"

FONT_DIRECTORY = THEME_DIRECTORY / "fonts"

# ==========================================================
# THEME MODE
# ==========================================================

class ThemeMode(Enum):
    """
    Application theme mode.
    """

    LIGHT = "light"

    DARK = "dark"

    SYSTEM = "system"

# ==========================================================
# ACCENT COLOR
# ==========================================================

class AccentColor(Enum):
    """
    Primary application accent colors.
    """

    BLUE = "#3B82F6"

    GREEN = "#10B981"

    RED = "#EF4444"

    ORANGE = "#F97316"

    PURPLE = "#8B5CF6"

    CYAN = "#06B6D4"

    YELLOW = "#FACC15"

# ==========================================================
# FONT CONFIGURATION
# ==========================================================

@dataclass(slots=True)
class FontConfiguration:

    family: str = "Segoe UI"

    size: int = 10

    bold: bool = False

    italic: bool = False

# ==========================================================
# THEME PALETTE
# ==========================================================

@dataclass(slots=True)
class ThemePalette:

    background: str

    surface: str

    primary: str

    secondary: str

    accent: str

    success: str

    warning: str

    danger: str

    text: str

    text_secondary: str

    border: str

# ==========================================================
# THEME CONFIGURATION
# ==========================================================

@dataclass(slots=True)
class ThemeConfiguration:

    mode: ThemeMode = ThemeMode.DARK

    accent: AccentColor = AccentColor.BLUE

    font: FontConfiguration = field(

        default_factory=FontConfiguration

    )

# ==========================================================
# STATISTICS
# ==========================================================

@dataclass(slots=True)
class ThemeStatistics:

    theme_changes: int = 0

    stylesheet_loads: int = 0

    palette_changes: int = 0

    font_changes: int = 0

    icon_updates: int = 0

# ==========================================================
# THEME SERVICE
# ==========================================================

class ThemeService(QObject):
    """
    Central theme manager.
    """

    VERSION = "1.0.0"

    def __init__(
        self,
        settings_service: SettingsService,
    ) -> None:

        super().__init__()

        self.logger = logging.getLogger(

            self.__class__.__name__

        )

        self._settings = settings_service

        self._configuration = (

            ThemeConfiguration()

        )

        self._statistics = (

            ThemeStatistics()

        )

        self._callbacks: Dict[
            str,
            List[Callable[..., None]]
        ] = {}

        self._stylesheets: Dict[
            ThemeMode,
            str,
        ] = {}

        self._palettes: Dict[
            ThemeMode,
            ThemePalette,
        ] = {}

        self._lock = threading.RLock()

        self._started = datetime.now()

        THEME_DIRECTORY.mkdir(

            parents=True,

            exist_ok=True,

        )

        STYLE_DIRECTORY.mkdir(

            parents=True,

            exist_ok=True,

        )

        ICON_DIRECTORY.mkdir(

            parents=True,

            exist_ok=True,

        )

        FONT_DIRECTORY.mkdir(

            parents=True,

            exist_ok=True,

        )

        self.logger.info(

            "ThemeService initialized."

        )
            # ==========================================================
    # PROPERTIES
    # ==========================================================

    @property
    def settings(self) -> SettingsService:
        """
        Return the SettingsService instance.
        """

        return self._settings

    @property
    def configuration(self) -> ThemeConfiguration:
        """
        Return current theme configuration.
        """

        return self._configuration

    @property
    def statistics(self) -> ThemeStatistics:
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

        callbacks = self._callbacks.get(
            event,
        )

        if callbacks is None:

            return

        try:

            callbacks.remove(callback)

        except ValueError:

            pass

    def clear_events(self) -> None:
        """
        Remove every callback.
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

                    "Theme callback failed."

                )

    # ==========================================================
    # PALETTES
    # ==========================================================

    def load_default_palettes(self) -> None:
        """
        Load built-in light and dark palettes.
        """

        self._palettes[ThemeMode.DARK] = ThemePalette(

            background="#121212",

            surface="#1E1E1E",

            primary="#242424",

            secondary="#2F2F2F",

            accent=self._configuration.accent.value,

            success="#16A34A",

            warning="#EAB308",

            danger="#DC2626",

            text="#FFFFFF",

            text_secondary="#B5B5B5",

            border="#3A3A3A",

        )

        self._palettes[ThemeMode.LIGHT] = ThemePalette(

            background="#F5F5F5",

            surface="#FFFFFF",

            primary="#F8F8F8",

            secondary="#E8E8E8",

            accent=self._configuration.accent.value,

            success="#16A34A",

            warning="#CA8A04",

            danger="#DC2626",

            text="#1A1A1A",

            text_secondary="#555555",

            border="#D0D0D0",

        )

        self._statistics.palette_changes += 1

    # ==========================================================
    # CURRENT PALETTE
    # ==========================================================

    def palette(
        self,
    ) -> ThemePalette:
        """
        Return active palette.
        """

        mode = self.current_mode()

        if mode not in self._palettes:

            self.load_default_palettes()

        return self._palettes[mode]

    # ==========================================================
    # MODE
    # ==========================================================

    def current_mode(
        self,
    ) -> ThemeMode:
        """
        Return active theme mode.
        """

        return self._configuration.mode

    def set_mode(
        self,
        mode: ThemeMode,
    ) -> None:
        """
        Change application theme mode.
        """

        if not isinstance(
            mode,
            ThemeMode,
        ):

            raise TypeError(
                "Invalid theme mode."
            )

        self._configuration.mode = mode

        self._statistics.theme_changes += 1

        self._emit(

            "theme_changed",

            mode=mode,

        )

    # ==========================================================
    # STYLESHEETS
    # ==========================================================

    def load_stylesheet(
        self,
        mode: ThemeMode,
    ) -> str:
        """
        Load stylesheet from disk.
        """

        filename = f"{mode.value}.qss"

        path = STYLE_DIRECTORY / filename

        if not path.exists():

            self.logger.warning(

                "Stylesheet not found: %s",

                path,

            )

            return ""

        stylesheet = path.read_text(

            encoding="utf-8",

        )

        self._stylesheets[mode] = stylesheet

        self._statistics.stylesheet_loads += 1

        return stylesheet

    def stylesheet(
        self,
    ) -> str:
        """
        Return current stylesheet.
        """

        mode = self.current_mode()

        if mode not in self._stylesheets:

            self.load_stylesheet(
                mode,
            )

        return self._stylesheets.get(

            mode,

            "",

        )

    # ==========================================================
    # VALIDATION
    # ==========================================================

    def validate(self) -> bool:
        """
        Validate theme configuration.
        """

        return (

            isinstance(

                self._configuration.mode,

                ThemeMode,

            )

            and

            isinstance(

                self._configuration.accent,

                AccentColor,

            )

        )
        # ==========================================================
    # ACCENT COLOR
    # ==========================================================

    def accent_color(
        self,
    ) -> AccentColor:
        """
        Return current accent color.
        """

        return self._configuration.accent

    def set_accent_color(
        self,
        accent: AccentColor,
    ) -> None:
        """
        Update accent color.
        """

        if not isinstance(
            accent,
            AccentColor,
        ):

            raise TypeError(
                "Invalid accent color."
            )

        self._configuration.accent = accent

        self.load_default_palettes()

        self._statistics.palette_changes += 1

        self._emit(

            "accent_changed",

            accent=accent,

        )

    # ==========================================================
    # FONT
    # ==========================================================

    def font(
        self,
    ) -> QFont:
        """
        Return application font.
        """

        config = self._configuration.font

        font = QFont(

            config.family,

            config.size,

        )

        font.setBold(
            config.bold,
        )

        font.setItalic(
            config.italic,
        )

        return font

    def set_font(
        self,
        *,
        family: Optional[str] = None,
        size: Optional[int] = None,
        bold: Optional[bool] = None,
        italic: Optional[bool] = None,
    ) -> None:
        """
        Update application font.
        """

        config = self._configuration.font

        if family is not None:

            config.family = family

        if size is not None:

            config.size = size

        if bold is not None:

            config.bold = bold

        if italic is not None:

            config.italic = italic

        self._statistics.font_changes += 1

        self._emit(

            "font_changed",

            font=self.font(),

        )

    # ==========================================================
    # APPLY
    # ==========================================================

    def apply(
        self,
        application: Optional[QApplication] = None,
    ) -> None:
        """
        Apply the current theme.
        """

        app = application or QApplication.instance()

        if app is None:

            return

        app.setStyleSheet(

            self.stylesheet(),

        )

        app.setFont(

            self.font(),

        )

        self.refresh()

    # ==========================================================
    # REFRESH
    # ==========================================================

    def refresh(
        self,
    ) -> None:
        """
        Refresh all application windows.
        """

        app = QApplication.instance()

        if app is None:

            return

        for widget in app.topLevelWidgets():

            widget.update()

            widget.repaint()

        self._emit(

            "theme_refreshed",

        )

    # ==========================================================
    # ICONS
    # ==========================================================

    def icon_directory(
        self,
    ) -> Path:
        """
        Return active icon directory.
        """

        return ICON_DIRECTORY / self.current_mode().value

    # ==========================================================
    # HIGH DPI
    # ==========================================================

    def enable_high_dpi(
        self,
    ) -> None:
        """
        Enable High-DPI rendering.

        Reserved for future Qt configuration.
        """

        self.logger.info(
            "High-DPI support enabled."
        )

    # ==========================================================
    # PERSISTENCE
    # ==========================================================

    def save_configuration(
        self,
    ) -> None:
        """
        Save theme settings through SettingsService.
        """

        self._settings.set(

            "application",

            "theme",

            self.current_mode(),

        )

        self._settings.set(

            "application",

            "accent",

            self.accent_color().value,

        )

    def load_configuration(
        self,
    ) -> None:
        """
        Restore theme configuration from SettingsService.
        """

        theme = self._settings.get(

            "application",

            "theme",

            ThemeMode.DARK,

        )

        if isinstance(
            theme,
            str,
        ):

            try:

                theme = ThemeMode(
                    theme,
                )

            except ValueError:

                theme = ThemeMode.DARK

        self.set_mode(
            theme,
        )

        accent = self._settings.get(

            "application",

            "accent",

            AccentColor.BLUE.value,

        )

        if isinstance(
            accent,
            str,
        ):

            try:

                self.set_accent_color(

                    AccentColor(
                        accent,
                    )

                )

            except ValueError:

                self.set_accent_color(

                    AccentColor.BLUE,

                )
                    # ==========================================================
    # CUSTOM THEMES
    # ==========================================================

    def register_palette(
        self,
        mode: ThemeMode,
        palette: ThemePalette,
    ) -> None:
        """
        Register a custom theme palette.
        """

        self._palettes[mode] = palette

        self._statistics.palette_changes += 1

        self._emit(

            "palette_registered",

            mode=mode,

        )

    def remove_palette(
        self,
        mode: ThemeMode,
    ) -> bool:
        """
        Remove a custom palette.
        """

        if mode not in self._palettes:

            return False

        del self._palettes[mode]

        self._emit(

            "palette_removed",

            mode=mode,

        )

        return True

    # ==========================================================
    # IMPORT / EXPORT
    # ==========================================================

    def export_theme(
        self,
        file_path: str,
    ) -> bool:
        """
        Export current theme configuration.
        """

        try:

            data = {

                "configuration": {

                    "mode":
                        self.current_mode().value,

                    "accent":
                        self.accent_color().value,

                    "font":
                        asdict(
                            self._configuration.font,
                        ),

                },

                "palette":
                    asdict(
                        self.palette(),
                    ),

            }

            Path(file_path).write_text(

                json.dumps(

                    data,

                    indent=4,

                ),

                encoding="utf-8",

            )

            self._emit(

                "theme_exported",

                file=file_path,

            )

            return True

        except Exception:

            self.logger.exception(
                "Failed to export theme."
            )

            return False

    def import_theme(
        self,
        file_path: str,
    ) -> bool:
        """
        Import a theme configuration.
        """

        path = Path(file_path)

        if not path.exists():

            return False

        try:

            data = json.loads(

                path.read_text(

                    encoding="utf-8",

                )

            )

            config = data.get(
                "configuration",
                {},
            )

            self.set_mode(

                ThemeMode(

                    config.get(

                        "mode",

                        ThemeMode.DARK.value,

                    )

                )

            )

            self.set_accent_color(

                AccentColor(

                    config.get(

                        "accent",

                        AccentColor.BLUE.value,

                    )

                )

            )

            font = config.get(
                "font",
                {},
            )

            self.set_font(

                family=font.get("family"),

                size=font.get("size"),

                bold=font.get("bold"),

                italic=font.get("italic"),

            )

            self._emit(

                "theme_imported",

                file=file_path,

            )

            return True

        except Exception:

            self.logger.exception(
                "Failed to import theme."
            )

            return False

    # ==========================================================
    # COLOR UTILITIES
    # ==========================================================

    def color(
        self,
        name: str,
    ) -> str:
        """
        Return a palette color.
        """

        palette = self.palette()

        if hasattr(
            palette,
            name,
        ):

            return getattr(
                palette,
                name,
            )

        raise AttributeError(

            f"Unknown palette color: {name}"

        )

    def qcolor(
        self,
        name: str,
    ) -> QColor:
        """
        Return QColor from palette.
        """

        return QColor(

            self.color(
                name,
            )

        )

    # ==========================================================
    # STYLESHEET VARIABLES
    # ==========================================================

    def resolved_stylesheet(
        self,
    ) -> str:
        """
        Return stylesheet with palette variables
        replaced.
        """

        stylesheet = self.stylesheet()

        palette = self.palette()

        replacements = {

            "{{BACKGROUND}}":
                palette.background,

            "{{SURFACE}}":
                palette.surface,

            "{{PRIMARY}}":
                palette.primary,

            "{{SECONDARY}}":
                palette.secondary,

            "{{ACCENT}}":
                palette.accent,

            "{{SUCCESS}}":
                palette.success,

            "{{WARNING}}":
                palette.warning,

            "{{DANGER}}":
                palette.danger,

            "{{TEXT}}":
                palette.text,

            "{{TEXT_SECONDARY}}":
                palette.text_secondary,

            "{{BORDER}}":
                palette.border,

        }

        for key, value in replacements.items():

            stylesheet = stylesheet.replace(

                key,

                value,

            )

        return stylesheet

    # ==========================================================
    # RESET
    # ==========================================================

    def reset_defaults(
        self,
    ) -> None:
        """
        Restore default theme configuration.
        """

        self._configuration = ThemeConfiguration()

        self.load_default_palettes()

        self._stylesheets.clear()

        self._emit(

            "theme_reset",

        )
            # ==========================================================
    # STATISTICS
    # ==========================================================

    def reset_statistics(self) -> None:
        """
        Reset runtime statistics.
        """

        self._statistics = ThemeStatistics()

        self.logger.info(
            "Theme statistics reset."
        )

    def statistics_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Return runtime statistics.
        """

        stats = self._statistics

        return {

            "theme_changes":
                stats.theme_changes,

            "stylesheet_loads":
                stats.stylesheet_loads,

            "palette_changes":
                stats.palette_changes,

            "font_changes":
                stats.font_changes,

            "icon_updates":
                stats.icon_updates,

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

            "theme_mode":
                self.current_mode().value,

            "accent":
                self.accent_color().value,

            "palette_loaded":
                self.current_mode()
                in self._palettes,

            "stylesheet_loaded":
                self.current_mode()
                in self._stylesheets,

            "uptime":
                str(self.uptime),

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

            stats["theme_changes"]

            + stats["stylesheet_loads"]

            + stats["palette_changes"]

            + stats["font_changes"]

            + stats["icon_updates"]

        )

        return {

            "version":
                self.VERSION,

            "operations":
                operations,

            "theme_changes":
                stats["theme_changes"],

            "stylesheet_loads":
                stats["stylesheet_loads"],

            "palette_changes":
                stats["palette_changes"],

            "font_changes":
                stats["font_changes"],

            "icon_updates":
                stats["icon_updates"],

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
        Return service summary.
        """

        return {

            "service":
                self.__class__.__name__,

            "version":
                self.VERSION,

            "mode":
                self.current_mode().value,

            "accent":
                self.accent_color().value,

            "font":
                asdict(
                    self._configuration.font,
                ),

            "uptime":
                str(self.uptime),

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

            "configuration": {

                "mode":
                    self.current_mode().value,

                "accent":
                    self.accent_color().value,

                "font":
                    asdict(
                        self._configuration.font,
                    ),

            },

        }

    # ==========================================================
    # INFORMATION
    # ==========================================================

    def info(
        self,
    ) -> Dict[str, Any]:
        """
        Return general service information.
        """

        return {

            "service":
                self.__class__.__name__,

            "version":
                self.VERSION,

            "theme_directory":
                str(THEME_DIRECTORY),

            "style_directory":
                str(STYLE_DIRECTORY),

            "icon_directory":
                str(self.icon_directory()),

            "font_directory":
                str(FONT_DIRECTORY),

            "uptime":
                str(self.uptime),

        }
        # ==========================================================
    # LIFECYCLE
    # ==========================================================

    def start(self) -> None:
        """
        Start the ThemeService.
        """

        self.logger.info(
            "Starting ThemeService..."
        )

        self._started = datetime.now()

        self._emit(
            "service_started",
        )

    def stop(self) -> None:
        """
        Stop the ThemeService.
        """

        self.logger.info(
            "Stopping ThemeService..."
        )

        self._emit(
            "service_stopped",
        )

    def restart(self) -> None:
        """
        Restart the ThemeService.
        """

        self.stop()

        self.start()

    # ==========================================================
    # RESET
    # ==========================================================

    def reset(self) -> None:
        """
        Restore default theme configuration.
        """

        self.reset_defaults()

        self.reset_statistics()

        self._emit(
            "service_reset",
        )

    # ==========================================================
    # CLONE
    # ==========================================================

    def clone(self) -> "ThemeService":
        """
        Create a copy of the current ThemeService.
        """

        cloned = ThemeService(
            self._settings,
        )

        cloned._configuration = ThemeConfiguration(
            mode=self._configuration.mode,
            accent=self._configuration.accent,
            font=FontConfiguration(
                **asdict(
                    self._configuration.font,
                )
            ),
        )

        cloned._palettes = dict(
            self._palettes,
        )

        cloned._stylesheets = dict(
            self._stylesheets,
        )

        return cloned

    # ==========================================================
    # SERIALIZATION
    # ==========================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Serialize current theme configuration.
        """

        return {

            "mode":
                self.current_mode().value,

            "accent":
                self.accent_color().value,

            "font":
                asdict(
                    self._configuration.font,
                ),

            "statistics":
                self.statistics_dict(),

        }

    def dump(
        self,
    ) -> Dict[str, Any]:
        """
        Dump complete runtime state.
        """

        return {

            "summary":
                self.summary(),

            "snapshot":
                self.snapshot(),

            "configuration":
                self.to_dict(),

            "diagnostics":
                self.diagnostics(),

        }

    # ==========================================================
    # CLEANUP
    # ==========================================================

    def dispose(self) -> None:
        """
        Release runtime resources.
        """

        self.clear_events()

        self._stylesheets.clear()

        self._palettes.clear()

        self.logger.info(
            "ThemeService disposed."
        )

    # ==========================================================
    # CONTEXT MANAGER
    # ==========================================================

    def __enter__(
        self,
    ) -> "ThemeService":

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

            f"mode={self.current_mode().value}, "

            f"accent={self.accent_color().value})"

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
    # THEME UTILITIES
    # ==========================================================

    def available_modes(
        self,
    ) -> List[ThemeMode]:
        """
        Return supported theme modes.
        """

        return list(
            ThemeMode,
        )

    def available_accents(
        self,
    ) -> List[AccentColor]:
        """
        Return supported accent colors.
        """

        return list(
            AccentColor,
        )

    def palette_names(
        self,
    ) -> List[str]:
        """
        Return palette color names.
        """

        return sorted(

            asdict(
                self.palette(),
            ).keys()

        )

    # ==========================================================
    # STYLESHEET UTILITIES
    # ==========================================================

    def stylesheet_loaded(
        self,
        mode: ThemeMode,
    ) -> bool:
        """
        Return True if stylesheet is loaded.
        """

        return mode in self._stylesheets

    def clear_stylesheets(
        self,
    ) -> None:
        """
        Remove cached stylesheets.
        """

        self._stylesheets.clear()

        self._emit(
            "stylesheets_cleared",
        )

    # ==========================================================
    # VALIDATION HELPERS
    # ==========================================================

    def assert_valid(
        self,
    ) -> None:
        """
        Raise an exception if the configuration
        is invalid.
        """

        if not self.validate():

            raise RuntimeError(
                "Theme configuration is invalid."
            )

    # ==========================================================
    # FACTORY
    # ==========================================================

    @classmethod
    def create(
        cls,
        settings_service: SettingsService,
    ) -> "ThemeService":
        """
        Factory constructor.
        """

        service = cls(
            settings_service,
        )

        service.load_default_palettes()

        service.load_configuration()

        return service


# ==========================================================
# MODULE HELPERS
# ==========================================================

def create_theme_service(
    settings_service: SettingsService,
) -> ThemeService:
    """
    Convenience factory.
    """

    return ThemeService.create(
        settings_service,
    )


def build_theme_service(
    settings_service: SettingsService,
) -> ThemeService:
    """
    Alternate factory helper.
    """

    return ThemeService(
        settings_service,
    )
# ==========================================================
# MODULE EXPORTS
# ==========================================================

__all__ = [

    # Directories
    "THEME_DIRECTORY",
    "STYLE_DIRECTORY",
    "ICON_DIRECTORY",
    "FONT_DIRECTORY",

    # Enums
    "ThemeMode",
    "AccentColor",

    # Models
    "FontConfiguration",
    "ThemePalette",
    "ThemeConfiguration",
    "ThemeStatistics",

    # Service
    "ThemeService",

    # Factory Helpers
    "create_theme_service",
    "build_theme_service",

]

# ==========================================================
# END OF FILE
# ==========================================================