from __future__ import annotations

import json
import threading
import uuid

from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# =====================================================
# USER PREFERENCES
# =====================================================

@dataclass(slots=True)
class UserPreferences:
    """Application user preferences."""

    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    # ---------------- Theme ----------------

    theme: str = "Dark"

    accent_color: str = "#2E86DE"

    font_family: str = "Segoe UI"

    font_size: int = 10

    # ---------------- Window ----------------

    window_width: int = 1600

    window_height: int = 900

    maximized: bool = False

    # ---------------- Scanner ----------------

    scanner_interval: int = 60

    auto_refresh: bool = True

    # ---------------- Dashboard ----------------

    dashboard_layout: str = "default"

    # ---------------- Notification ----------------

    notifications: bool = True

    sound_alerts: bool = False

    # ---------------- Language ----------------

    language: str = "English"

    # ---------------- User Data ----------------

    favorites: List[str] = field(
        default_factory=list
    )

    recent_projects: List[str] = field(
        default_factory=list
    )

    custom: Dict[str, Any] = field(
        default_factory=dict
    )


# =====================================================
# PREFERENCES MANAGER
# =====================================================

class PreferencesManager:

    _instance = None

    _lock = threading.Lock()

    # -------------------------------------------------

    def __new__(cls):

        with cls._lock:

            if cls._instance is None:

                cls._instance = super().__new__(cls)

        return cls._instance

    # -------------------------------------------------

    def __init__(self):

        if getattr(
            self,
            "_initialized",
            False,
        ):
            return

        self._initialized = True

        self.manager_lock = threading.RLock()

        self.config_directory = (
            Path.home()
            / ".stockversity"
        )

        self.config_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.config_file = (
            self.config_directory
            / "preferences.json"
        )

        self.preferences = UserPreferences()

        self.load()

    # =====================================================
    # LOAD
    # =====================================================

    def load(self) -> bool:

        if not self.config_file.exists():
            return False

        try:

            data = json.loads(
                self.config_file.read_text(
                    encoding="utf-8"
                )
            )

            if "created_at" in data:

                data["created_at"] = (
                    datetime.fromisoformat(
                        data["created_at"]
                    )
                )

            self.preferences = UserPreferences(
                **data
            )

            return True

        except Exception:

            return False

    # =====================================================
    # SAVE
    # =====================================================

    def save(self) -> bool:

        try:

            data = asdict(
                self.preferences
            )

            data["created_at"] = (
                self.preferences.created_at.isoformat()
            )

            self.config_file.write_text(
                json.dumps(
                    data,
                    indent=4,
                ),
                encoding="utf-8",
            )

            return True

        except Exception:

            return False

    # =====================================================
    # GET
    # =====================================================

    def get(

        self,

        key: str,

        default=None,

    ):

        if hasattr(
            self.preferences,
            key,
        ):
            return getattr(
                self.preferences,
                key,
            )

        return self.preferences.custom.get(
            key,
            default,
        )

    # =====================================================
    # SET
    # =====================================================

    def set(

        self,

        key: str,

        value,

    ):

        if hasattr(
            self.preferences,
            key,
        ):

            setattr(
                self.preferences,
                key,
                value,
            )

        else:

            self.preferences.custom[
                key
            ] = value

        return self.save()

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        self.preferences = UserPreferences()

        self.save()

    # =====================================================
    # TO DICTIONARY
    # =====================================================

    def to_dict(self) -> Dict[str, Any]:

        data = asdict(
            self.preferences
        )

        data["created_at"] = (
            self.preferences.created_at.isoformat()
        )

        return data
        # =====================================================
    # THEME
    # =====================================================

    def theme(self) -> str:

        return self.preferences.theme

    def set_theme(

        self,

        theme: str,

    ) -> bool:

        self.preferences.theme = theme

        return self.save()

    # =====================================================
    # ACCENT COLOR
    # =====================================================

    def accent_color(self) -> str:

        return self.preferences.accent_color

    def set_accent_color(

        self,

        color: str,

    ) -> bool:

        self.preferences.accent_color = color

        return self.save()

    # =====================================================
    # FONT SETTINGS
    # =====================================================

    def font(self) -> Dict[str, Any]:

        return {

            "family": self.preferences.font_family,

            "size": self.preferences.font_size,

        }

    def set_font(

        self,

        family: str,

        size: int,

    ) -> bool:

        self.preferences.font_family = family

        self.preferences.font_size = max(

            6,

            size,

        )

        return self.save()

    # =====================================================
    # WINDOW STATE
    # =====================================================

    def window_state(self) -> Dict[str, Any]:

        return {

            "width": self.preferences.window_width,

            "height": self.preferences.window_height,

            "maximized": self.preferences.maximized,

        }

    def save_window_state(

        self,

        width: int,

        height: int,

        maximized: bool,

    ) -> bool:

        self.preferences.window_width = width

        self.preferences.window_height = height

        self.preferences.maximized = maximized

        return self.save()

    # =====================================================
    # SCANNER SETTINGS
    # =====================================================

    def scanner_settings(self) -> Dict[str, Any]:

        return {

            "interval": self.preferences.scanner_interval,

            "auto_refresh": self.preferences.auto_refresh,

        }

    def set_scanner_interval(

        self,

        interval: int,

    ) -> bool:

        self.preferences.scanner_interval = max(

            5,

            interval,

        )

        return self.save()

    def set_auto_refresh(

        self,

        enabled: bool,

    ) -> bool:

        self.preferences.auto_refresh = enabled

        return self.save()

    # =====================================================
    # DASHBOARD
    # =====================================================

    def dashboard_layout(self) -> str:

        return self.preferences.dashboard_layout

    def set_dashboard_layout(

        self,

        layout: str,

    ) -> bool:

        self.preferences.dashboard_layout = layout

        return self.save()

    # =====================================================
    # NOTIFICATIONS
    # =====================================================

    def notifications(self) -> Dict[str, bool]:

        return {

            "enabled": self.preferences.notifications,

            "sound": self.preferences.sound_alerts,

        }

    def enable_notifications(

        self,

        enabled: bool,

    ) -> bool:

        self.preferences.notifications = enabled

        return self.save()

    def enable_sound_alerts(

        self,

        enabled: bool,

    ) -> bool:

        self.preferences.sound_alerts = enabled

        return self.save()

    # =====================================================
    # FAVORITES
    # =====================================================

    def add_favorite(

        self,

        symbol: str,

    ) -> bool:

        symbol = symbol.upper()

        if symbol not in self.preferences.favorites:

            self.preferences.favorites.append(

                symbol

            )

            return self.save()

        return False

    def remove_favorite(

        self,

        symbol: str,

    ) -> bool:

        symbol = symbol.upper()

        if symbol in self.preferences.favorites:

            self.preferences.favorites.remove(

                symbol

            )

            return self.save()

        return False

    def favorites(self) -> List[str]:

        return list(

            self.preferences.favorites

        )
        # =====================================================
    # RECENT PROJECTS
    # =====================================================

    def add_recent_project(

        self,

        project: str,

    ) -> bool:

        if project in self.preferences.recent_projects:

            self.preferences.recent_projects.remove(

                project

            )

        self.preferences.recent_projects.insert(

            0,

            project,

        )

        self.preferences.recent_projects = (

            self.preferences.recent_projects[:10]

        )

        return self.save()

    def remove_recent_project(

        self,

        project: str,

    ) -> bool:

        if project in self.preferences.recent_projects:

            self.preferences.recent_projects.remove(

                project

            )

            return self.save()

        return False

    def clear_recent_projects(

        self,

    ) -> bool:

        self.preferences.recent_projects.clear()

        return self.save()

    def recent_projects(self) -> List[str]:

        return list(

            self.preferences.recent_projects

        )

    # =====================================================
    # LANGUAGE
    # =====================================================

    def language(self) -> str:

        return self.preferences.language

    def set_language(

        self,

        language: str,

    ) -> bool:

        self.preferences.language = language

        return self.save()

    # =====================================================
    # IMPORT SETTINGS
    # =====================================================

    def import_settings(

        self,

        file_path: str,

    ) -> bool:

        path = Path(

            file_path

        )

        if not path.exists():

            return False

        try:

            data = json.loads(

                path.read_text(

                    encoding="utf-8"

                )

            )

            for key, value in data.items():

                if hasattr(

                    self.preferences,

                    key,

                ):

                    setattr(

                        self.preferences,

                        key,

                        value,

                    )

                else:

                    self.preferences.custom[

                        key

                    ] = value

            return self.save()

        except Exception:

            return False

    # =====================================================
    # EXPORT SETTINGS
    # =====================================================

    def export_settings(

        self,

        file_path: str,

    ) -> bool:

        try:

            path = Path(

                file_path

            )

            path.write_text(

                json.dumps(

                    self.to_dict(),

                    indent=4,

                ),

                encoding="utf-8",

            )

            return True

        except Exception:

            return False

    # =====================================================
    # CUSTOM SETTINGS
    # =====================================================

    def set_custom(

        self,

        key: str,

        value: Any,

    ) -> bool:

        self.preferences.custom[

            key

        ] = value

        return self.save()

    def get_custom(

        self,

        key: str,

        default: Any = None,

    ) -> Any:

        return self.preferences.custom.get(

            key,

            default,

        )

    def remove_custom(

        self,

        key: str,

    ) -> bool:

        if key in self.preferences.custom:

            del self.preferences.custom[

                key

            ]

            return self.save()

        return False

    def clear_custom(

        self,

    ) -> bool:

        self.preferences.custom.clear()

        return self.save()

    # =====================================================
    # UPDATE MULTIPLE SETTINGS
    # =====================================================

    def update(

        self,

        values: Dict[str, Any],

    ) -> bool:

        for key, value in values.items():

            if hasattr(

                self.preferences,

                key,

            ):

                setattr(

                    self.preferences,

                    key,

                    value,

                )

            else:

                self.preferences.custom[

                    key

                ] = value

        return self.save()

    # =====================================================
    # HEALTH
    # =====================================================

    def health(self) -> Dict[str, Any]:

        return {

            "config_file": str(

                self.config_file

            ),

            "exists": self.config_file.exists(),

            "favorites": len(

                self.preferences.favorites

            ),

            "recent_projects": len(

                self.preferences.recent_projects

            ),

            "custom_settings": len(

                self.preferences.custom

            ),

        }

    # =====================================================
    # STATISTICS
    # =====================================================

    def statistics(self) -> Dict[str, Any]:

        return {

            "theme": self.preferences.theme,

            "language": self.preferences.language,

            "favorites": len(

                self.preferences.favorites

            ),

            "recent_projects": len(

                self.preferences.recent_projects

            ),

            "custom_settings": len(

                self.preferences.custom

            ),

            "notifications": self.preferences.notifications,

            "auto_refresh": self.preferences.auto_refresh,

        }
        # =====================================================
    # STARTUP
    # =====================================================

    def startup(self) -> Dict[str, Any]:
        """
        Startup hook.

        Loads preferences from disk and returns
        current statistics.
        """

        self.load()

        return self.statistics()

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(self) -> Dict[str, Any]:
        """
        Shutdown hook.

        Saves preferences before application exit.
        """

        self.save()

        return self.statistics()

    # =====================================================
    # RELOAD
    # =====================================================

    def reload(self) -> bool:

        return self.load()

    # =====================================================
    # EXISTS
    # =====================================================

    def exists(

        self,

        key: str,

    ) -> bool:

        return (

            hasattr(

                self.preferences,

                key,

            )

            or key in self.preferences.custom

        )

    # =====================================================
    # KEYS
    # =====================================================

    def keys(self) -> List[str]:

        return (

            list(

                self.preferences.__dataclass_fields__.keys()

            )

            + list(

                self.preferences.custom.keys()

            )

        )

    # =====================================================
    # CLEAR FAVORITES
    # =====================================================

    def clear_favorites(self) -> bool:

        self.preferences.favorites.clear()

        return self.save()

    # =====================================================
    # RESET TO DEFAULTS
    # =====================================================

    def reset_defaults(self) -> bool:

        self.preferences = UserPreferences()

        return self.save()

    # =====================================================
    # REPR
    # =====================================================

    def __repr__(self) -> str:

        stats = self.statistics()

        return (

            "PreferencesManager("

            f"theme='{stats['theme']}', "

            f"favorites={stats['favorites']}, "

            f"projects={stats['recent_projects']}"

            ")"

        )

    # =====================================================
    # STR
    # =====================================================

    def __str__(self) -> str:

        stats = self.statistics()

        return (

            "Preferences Manager\n"

            f"Theme            : {stats['theme']}\n"

            f"Language         : {stats['language']}\n"

            f"Favorites        : {stats['favorites']}\n"

            f"Recent Projects  : {stats['recent_projects']}\n"

            f"Custom Settings  : {stats['custom_settings']}\n"

            f"Notifications    : {stats['notifications']}\n"

            f"Auto Refresh     : {stats['auto_refresh']}"
        )


# =====================================================
# GLOBAL SINGLETON
# =====================================================

preferences_manager = PreferencesManager()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "UserPreferences",

    "PreferencesManager",

    "preferences_manager",

]