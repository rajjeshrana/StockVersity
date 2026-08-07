"""
=========================================================
StockVersity Scanner Pro
Theme Manager
Version : 4.0
Powered by AI
=========================================================
"""

from __future__ import annotations

from typing import Optional, List

from PySide6.QtCore import QObject
from PySide6.QtCore import Signal
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QWidget

from ui.theme import (
    ThemeMode,
    theme_manager,
    initialize_theme,
    reload_theme,
)


# =========================================================
# SETTINGS
# =========================================================

ORGANIZATION_NAME = "StockVersity"

APPLICATION_NAME = "StockVersity Scanner Pro"

SETTINGS_GROUP = "Appearance"

THEME_KEY = "Theme"


# =========================================================
# THEME CONTROLLER
# =========================================================

class ThemeController(QObject):

    # -----------------------------------------------------
    # Signals
    # -----------------------------------------------------

    themeChanged = Signal(str)

    beforeThemeChanged = Signal(str)

    afterThemeChanged = Signal(str)

    # -----------------------------------------------------

    def __init__(

        self,

        app: QApplication,

        parent=None

    ):

        super().__init__(parent)

        self.app = app

        self.settings = QSettings(

            ORGANIZATION_NAME,

            APPLICATION_NAME

        )

        self._windows: List[QWidget] = []

        self._initialized = False

        self._current_mode = ThemeMode.DARK

    # =====================================================
    # INITIALIZE
    # =====================================================

    def initialize(self):

        mode = self.load_theme()

        initialize_theme(

            self.app,

            mode

        )

        self._current_mode = mode

        self._initialized = True

    # =====================================================
    # REGISTER WINDOW
    # =====================================================

    def register_window(

        self,

        window: QWidget

    ):

        if window not in self._windows:

            self._windows.append(window)

    # =====================================================
    # UNREGISTER
    # =====================================================

    def unregister_window(

        self,

        window: QWidget

    ):

        if window in self._windows:

            self._windows.remove(window)

    # =====================================================
    # REGISTER MANY
    # =====================================================

    def register_windows(

        self,

        windows: List[QWidget]

    ):

        for window in windows:

            self.register_window(window)

    # =====================================================
    # CLEAR WINDOWS
    # =====================================================

    def clear_windows(self):

        self._windows.clear()

    # =====================================================
    # WINDOWS
    # =====================================================

    @property

    def windows(self):

        return list(self._windows)

    # =====================================================
    # CURRENT MODE
    # =====================================================

    @property

    def current_mode(self):

        return self._current_mode

    # =====================================================
    # IS DARK
    # =====================================================

    def is_dark(self):

        return self._current_mode == ThemeMode.DARK

    # =====================================================
    # IS LIGHT
    # =====================================================

    def is_light(self):

        return self._current_mode == ThemeMode.LIGHT
        # =====================================================
    # LOAD THEME
    # =====================================================

    def load_theme(self) -> ThemeMode:

        value = self.settings.value(

            f"{SETTINGS_GROUP}/{THEME_KEY}",
            ThemeMode.DARK.value,
            type=str

        )

        try:

            return ThemeMode(value)

        except Exception:

            return ThemeMode.DARK

    # =====================================================
    # SAVE THEME
    # =====================================================

    def save_theme(

        self,

        mode: ThemeMode

    ):

        self.settings.setValue(

            f"{SETTINGS_GROUP}/{THEME_KEY}",

            mode.value

        )

        self.settings.sync()

    # =====================================================
    # SET THEME
    # =====================================================

    def set_theme(

        self,

        mode: ThemeMode,

        save: bool = True

    ):

        if mode == self._current_mode:

            return

        self.beforeThemeChanged.emit(

            mode.value

        )

        theme_manager.set_theme(mode)

        self._current_mode = mode

        if save:

            self.save_theme(mode)

        self.apply_theme()

        self.themeChanged.emit(

            mode.value

        )

        self.afterThemeChanged.emit(

            mode.value

        )

    # =====================================================
    # TOGGLE THEME
    # =====================================================

    def toggle_theme(self):

        if self._current_mode == ThemeMode.DARK:

            self.set_theme(

                ThemeMode.LIGHT

            )

        else:

            self.set_theme(

                ThemeMode.DARK

            )

    # =====================================================
    # APPLY APPLICATION THEME
    # =====================================================

    def apply_theme(self):

        reload_theme(self.app)

        self.refresh_registered_windows()

    # =====================================================
    # APPLY TO SINGLE WINDOW
    # =====================================================

    def apply_to_window(

        self,

        window: QWidget

    ):

        if window is None:

            return

        try:

            window.setStyleSheet(

                theme_manager.stylesheet()

            )

            window.style().unpolish(window)

            window.style().polish(window)

            window.update()

        except Exception:

            pass

    # =====================================================
    # REFRESH REGISTERED WINDOWS
    # =====================================================

    def refresh_registered_windows(self):

        dead_windows = []

        for window in self._windows:

            try:

                if window is None:

                    dead_windows.append(window)

                    continue

                self.apply_to_window(window)

                self.refresh_children(window)

            except RuntimeError:

                dead_windows.append(window)

        for window in dead_windows:

            if window in self._windows:

                self._windows.remove(window)

    # =====================================================
    # REFRESH CHILD WIDGETS
    # =====================================================

    def refresh_children(

        self,

        parent: QWidget

    ):

        for child in parent.findChildren(QWidget):

            try:

                child.style().unpolish(child)

                child.style().polish(child)

                child.update()

            except Exception:

                pass

    # =====================================================
    # APPLY TO ALL TOP LEVEL WINDOWS
    # =====================================================

    def apply_to_all_windows(self):

        for widget in QApplication.topLevelWidgets():

            if isinstance(widget, QWidget):

                self.apply_to_window(widget)

    # =====================================================
    # FORCE COMPLETE REFRESH
    # =====================================================

    def refresh_everything(self):

        self.apply_to_all_windows()

        self.refresh_registered_windows()
            # =====================================================
    # ADD OBSERVER
    # =====================================================

    def add_observer(
        self,
        callback
    ):

        if not hasattr(self, "_observers"):

            self._observers = []

        if callback not in self._observers:

            self._observers.append(callback)

    # =====================================================
    # REMOVE OBSERVER
    # =====================================================

    def remove_observer(
        self,
        callback
    ):

        if not hasattr(self, "_observers"):

            return

        if callback in self._observers:

            self._observers.remove(callback)

    # =====================================================
    # NOTIFY OBSERVERS
    # =====================================================

    def notify_observers(self):

        if not hasattr(self, "_observers"):

            return

        for callback in list(self._observers):

            try:

                callback(self._current_mode)

            except Exception:

                pass

    # =====================================================
    # REGISTER DIALOG
    # =====================================================

    def register_dialog(
        self,
        dialog: QWidget
    ):

        self.register_window(dialog)

        self.apply_to_window(dialog)

    # =====================================================
    # REGISTER TOP LEVEL WINDOWS
    # =====================================================

    def register_existing_windows(self):

        for widget in QApplication.topLevelWidgets():

            if isinstance(widget, QWidget):

                self.register_window(widget)

    # =====================================================
    # APPLY THEME TO NEW WINDOWS
    # =====================================================

    def synchronize_windows(self):

        current = QApplication.topLevelWidgets()

        for widget in current:

            if widget not in self._windows:

                self.register_window(widget)

                self.apply_to_window(widget)

    # =====================================================
    # EVENT FILTER
    # =====================================================

    def eventFilter(
        self,
        watched,
        event
    ):

        try:

            event_name = event.type().name

        except Exception:

            return super().eventFilter(

                watched,

                event

            )

        # Window created

        if event_name in (

            "Show",

            "ShowToParent"

        ):

            if isinstance(

                watched,

                QWidget

            ):

                self.register_window(

                    watched

                )

                self.apply_to_window(

                    watched

                )

        return super().eventFilter(

            watched,

            event

        )

    # =====================================================
    # INSTALL EVENT FILTER
    # =====================================================

    def install(self):

        self.app.installEventFilter(self)

        self.register_existing_windows()

    # =====================================================
    # REMOVE EVENT FILTER
    # =====================================================

    def uninstall(self):

        self.app.removeEventFilter(self)

    # =====================================================
    # APPLY AND NOTIFY
    # =====================================================

    def refresh_theme(self):

        self.apply_theme()

        self.notify_observers()

    # =====================================================
    # FORCE SYNCHRONIZATION
    # =====================================================

    def synchronize(self):

        self.synchronize_windows()

        self.refresh_registered_windows()

        self.notify_observers()

    # =====================================================
    # DIAGNOSTICS
    # =====================================================

    def diagnostics(self):

        return {

            "initialized": self._initialized,

            "current_theme": self._current_mode.value,

            "registered_windows": len(

                self._windows

            ),

            "registered_observers": len(

                getattr(

                    self,

                    "_observers",

                    []

                )

            ),

            "settings_file": self.settings.fileName(),

        }

    # =====================================================
    # STATUS
    # =====================================================

    def status(self):

        return {

            "theme":

                self._current_mode.value,

            "dark":

                self.is_dark(),

            "light":

                self.is_light(),

            "windows":

                len(self._windows),

            "initialized":

                self._initialized,

        }

    # =====================================================
    # EXPORT STATE
    # =====================================================

    def export_state(self):

        return {

            "theme":

                self._current_mode.value,

            "diagnostics":

                self.diagnostics(),

            "status":

                self.status(),

        }
        # =====================================================
    # IMPORT STATE
    # =====================================================

    def import_state(
        self,
        state: dict
    ):

        if not state:
            return

        theme = state.get(
            "theme",
            ThemeMode.DARK.value
        )

        try:

            self.set_theme(
                ThemeMode(theme),
                save=False
            )

        except Exception:

            self.set_theme(
                ThemeMode.DARK,
                save=False
            )

    # =====================================================
    # RESET TO DEFAULT
    # =====================================================

    def reset(self):

        self.set_theme(
            ThemeMode.DARK
        )

    # =====================================================
    # RESET SETTINGS
    # =====================================================

    def reset_settings(self):

        self.settings.remove(

            f"{SETTINGS_GROUP}/{THEME_KEY}"

        )

        self.settings.sync()

        self.reset()

    # =====================================================
    # BACKUP SETTINGS
    # =====================================================

    def backup_settings(self):

        return {

            "theme": self._current_mode.value,

            "settings_file": self.settings.fileName()

        }

    # =====================================================
    # RESTORE SETTINGS
    # =====================================================

    def restore_settings(
        self,
        backup: dict
    ):

        if not backup:
            return

        theme = backup.get(
            "theme",
            ThemeMode.DARK.value
        )

        try:

            self.set_theme(

                ThemeMode(theme)

            )

        except Exception:

            self.reset()

    # =====================================================
    # MIGRATE SETTINGS
    # =====================================================

    def migrate_settings(self):

        value = self.settings.value(

            f"{SETTINGS_GROUP}/{THEME_KEY}"

        )

        if value is None:

            self.save_theme(

                ThemeMode.DARK

            )

    # =====================================================
    # STARTUP
    # =====================================================

    def startup(self):

        self.migrate_settings()

        self.initialize()

        self.install()

        self.refresh_everything()

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(self):

        self.save_theme(

            self._current_mode

        )

        self.uninstall()

    # =====================================================
    # OPTIMIZED REFRESH
    # =====================================================

    def refresh_visible_windows(self):

        for window in list(self._windows):

            try:

                if not window.isVisible():

                    continue

                self.apply_to_window(window)

            except Exception:

                pass

    # =====================================================
    # FORCE REPAINT
    # =====================================================

    def repaint_all(self):

        for window in QApplication.topLevelWidgets():

            try:

                window.repaint()

                window.update()

            except Exception:

                pass

    # =====================================================
    # APPLY WITHOUT SAVE
    # =====================================================

    def preview_theme(
        self,
        mode: ThemeMode
    ):

        old_mode = self._current_mode

        self.set_theme(
            mode,
            save=False
        )

        return old_mode

    # =====================================================
    # RESTORE PREVIEW
    # =====================================================

    def restore_preview(
        self,
        previous_mode: ThemeMode
    ):

        self.set_theme(
            previous_mode,
            save=False
        )

    # =====================================================
    # AVAILABLE THEMES
    # =====================================================

    def available_themes(self):

        return [

            {

                "id": ThemeMode.DARK,

                "name": "Dark",

                "description":
                    "Professional trading terminal"

            },

            {

                "id": ThemeMode.LIGHT,

                "name": "Light",

                "description":
                    "Professional office workspace"

            }

        ]

    # =====================================================
    # THEME NAME
    # =====================================================

    def theme_name(self):

        return self._current_mode.value.title()

    # =====================================================
    # IS INITIALIZED
    # =====================================================

    @property
    def initialized(self):

        return self._initialized
    # =========================================================
# GLOBAL CONTROLLER
# =========================================================

_theme_controller: Optional[ThemeController] = None


# =========================================================
# CREATE CONTROLLER
# =========================================================

def create_theme_controller(
    app: QApplication
) -> ThemeController:
    """
    Create the global ThemeController instance.
    """

    global _theme_controller

    if _theme_controller is None:

        _theme_controller = ThemeController(app)

    return _theme_controller


# =========================================================
# GET CONTROLLER
# =========================================================

def theme_controller() -> ThemeController:
    """
    Return the global ThemeController instance.

    Raises:
        RuntimeError: If the controller has not been created.
    """

    if _theme_controller is None:

        raise RuntimeError(
            "ThemeController has not been initialized."
        )

    return _theme_controller


# =========================================================
# INITIALIZE
# =========================================================

def initialize(
    app: QApplication
) -> ThemeController:
    """
    Initialize the global theme system.
    """

    controller = create_theme_controller(app)

    controller.startup()

    return controller


# =========================================================
# SHUTDOWN
# =========================================================

def shutdown():

    global _theme_controller

    if _theme_controller is not None:

        _theme_controller.shutdown()


# =========================================================
# DARK MODE
# =========================================================

def dark():

    theme_controller().set_theme(

        ThemeMode.DARK

    )


# =========================================================
# LIGHT MODE
# =========================================================

def light():

    theme_controller().set_theme(

        ThemeMode.LIGHT

    )


# =========================================================
# TOGGLE
# =========================================================

def toggle():

    theme_controller().toggle_theme()


# =========================================================
# CURRENT MODE
# =========================================================

def current_mode():

    return theme_controller().current_mode


# =========================================================
# IS DARK
# =========================================================

def is_dark():

    return theme_controller().is_dark()


# =========================================================
# IS LIGHT
# =========================================================

def is_light():

    return theme_controller().is_light()


# =========================================================
# REGISTER WINDOW
# =========================================================

def register(
    window: QWidget
):

    theme_controller().register_window(window)


# =========================================================
# UNREGISTER WINDOW
# =========================================================

def unregister(
    window: QWidget
):

    theme_controller().unregister_window(window)


# =========================================================
# REFRESH
# =========================================================

def refresh():

    theme_controller().refresh_everything()


# =========================================================
# RESET
# =========================================================

def reset():

    theme_controller().reset()


# =========================================================
# EXPORT
# =========================================================

def export_theme():

    return theme_controller().export_state()


# =========================================================
# IMPORT
# =========================================================

def import_theme(
    state: dict
):

    theme_controller().import_state(state)


# =========================================================
# APPLICATION METADATA
# =========================================================

MODULE_NAME = "Theme Manager"

MODULE_VERSION = "4.0"

MODULE_AUTHOR = "StockVersity"

MODULE_DESCRIPTION = (
    "Application-wide theme controller for "
    "StockVersity Scanner Pro."
)


def metadata():

    return {

        "module": MODULE_NAME,

        "version": MODULE_VERSION,

        "author": MODULE_AUTHOR,

        "description": MODULE_DESCRIPTION,

    }


# =========================================================
# PUBLIC EXPORTS
# =========================================================

__all__ = [

    "ThemeController",

    "create_theme_controller",

    "theme_controller",

    "initialize",

    "shutdown",

    "dark",

    "light",

    "toggle",

    "current_mode",

    "is_dark",

    "is_light",

    "register",

    "unregister",

    "refresh",

    "reset",

    "export_theme",

    "import_theme",

    "metadata",

]


# =========================================================
# END OF FILE
# =========================================================