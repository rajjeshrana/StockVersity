"""
=========================================================
StockVersity Scanner Pro
Theme Engine
Version : 4.0
Powered by AI
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


# =========================================================
# THEME ENUM
# =========================================================

class ThemeMode(str, Enum):

    DARK = "dark"
    LIGHT = "light"


# =========================================================
# COLOR PALETTE
# =========================================================

@dataclass(frozen=True)
class ThemeColors:

    # -----------------------------------------------------
    # Background
    # -----------------------------------------------------

    WINDOW: str

    SURFACE: str

    CARD: str

    SIDEBAR: str

    HEADER: str

    STATUSBAR: str

    BORDER: str

    DIVIDER: str

    # -----------------------------------------------------
    # Text
    # -----------------------------------------------------

    TEXT: str

    TEXT_SECONDARY: str

    TEXT_MUTED: str

    TEXT_DISABLED: str

    # -----------------------------------------------------
    # Primary
    # -----------------------------------------------------

    PRIMARY: str

    PRIMARY_HOVER: str

    PRIMARY_PRESSED: str

    PRIMARY_LIGHT: str

    # -----------------------------------------------------
    # Accent
    # -----------------------------------------------------

    ACCENT: str

    ACCENT_HOVER: str

    ACCENT_LIGHT: str

    # -----------------------------------------------------
    # Trading Colors
    # -----------------------------------------------------

    BUY: str

    SELL: str

    HOLD: str

    NEUTRAL: str

    # -----------------------------------------------------
    # Heatmap
    # -----------------------------------------------------

    SCORE_HIGH: str

    SCORE_MEDIUM: str

    SCORE_LOW: str

    CONFIDENCE_HIGH: str

    CONFIDENCE_MEDIUM: str

    CONFIDENCE_LOW: str

    # -----------------------------------------------------
    # Status
    # -----------------------------------------------------

    SUCCESS: str

    WARNING: str

    ERROR: str

    INFO: str

    # -----------------------------------------------------
    # Table
    # -----------------------------------------------------

    TABLE_HEADER: str

    TABLE_ROW: str

    TABLE_ALT_ROW: str

    TABLE_SELECTION: str

    TABLE_GRID: str

    # -----------------------------------------------------
    # Inputs
    # -----------------------------------------------------

    INPUT_BG: str

    INPUT_BORDER: str

    INPUT_FOCUS: str

    # -----------------------------------------------------
    # Charts
    # -----------------------------------------------------

    CHART_GRID: str

    CHART_AXIS: str

    CHART_BACKGROUND: str


# =========================================================
# DARK TERMINAL THEME
# =========================================================

DARK = ThemeColors(

    WINDOW="#111827",
    SURFACE="#1A2233",
    CARD="#202A3C",
    SIDEBAR="#0F172A",
    HEADER="#182132",
    STATUSBAR="#121A27",
    BORDER="#2D3A4F",
    DIVIDER="#334155",

    TEXT="#FFFFFF",
    TEXT_SECONDARY="#CBD5E1",
    TEXT_MUTED="#94A3B8",
    TEXT_DISABLED="#64748B",

    PRIMARY="#2563EB",
    PRIMARY_HOVER="#3B82F6",
    PRIMARY_PRESSED="#1D4ED8",
    PRIMARY_LIGHT="#DBEAFE",

    ACCENT="#14B8A6",
    ACCENT_HOVER="#2DD4BF",
    ACCENT_LIGHT="#CCFBF1",

    BUY="#22C55E",
    SELL="#EF4444",
    HOLD="#F59E0B",
    NEUTRAL="#64748B",

    SCORE_HIGH="#15803D",
    SCORE_MEDIUM="#FACC15",
    SCORE_LOW="#DC2626",

    CONFIDENCE_HIGH="#16A34A",
    CONFIDENCE_MEDIUM="#EAB308",
    CONFIDENCE_LOW="#DC2626",

    SUCCESS="#16A34A",
    WARNING="#F59E0B",
    ERROR="#DC2626",
    INFO="#3B82F6",

    TABLE_HEADER="#1E293B",
    TABLE_ROW="#1B2434",
    TABLE_ALT_ROW="#202C40",
    TABLE_SELECTION="#2563EB",
    TABLE_GRID="#334155",

    INPUT_BG="#1E293B",
    INPUT_BORDER="#334155",
    INPUT_FOCUS="#2563EB",

    CHART_GRID="#374151",
    CHART_AXIS="#CBD5E1",
    CHART_BACKGROUND="#111827",

)


# =========================================================
# LIGHT TERMINAL THEME
# =========================================================

LIGHT = ThemeColors(

    WINDOW="#F4F7FB",
    SURFACE="#FFFFFF",
    CARD="#FFFFFF",
    SIDEBAR="#EEF2F7",
    HEADER="#FFFFFF",
    STATUSBAR="#FFFFFF",
    BORDER="#D1D5DB",
    DIVIDER="#E5E7EB",

    TEXT="#111827",
    TEXT_SECONDARY="#374151",
    TEXT_MUTED="#6B7280",
    TEXT_DISABLED="#9CA3AF",

    PRIMARY="#2563EB",
    PRIMARY_HOVER="#3B82F6",
    PRIMARY_PRESSED="#1D4ED8",
    PRIMARY_LIGHT="#DBEAFE",

    ACCENT="#14B8A6",
    ACCENT_HOVER="#2DD4BF",
    ACCENT_LIGHT="#CCFBF1",

    BUY="#16A34A",
    SELL="#DC2626",
    HOLD="#CA8A04",
    NEUTRAL="#6B7280",

    SCORE_HIGH="#16A34A",
    SCORE_MEDIUM="#FACC15",
    SCORE_LOW="#DC2626",

    CONFIDENCE_HIGH="#16A34A",
    CONFIDENCE_MEDIUM="#EAB308",
    CONFIDENCE_LOW="#DC2626",

    SUCCESS="#16A34A",
    WARNING="#CA8A04",
    ERROR="#DC2626",
    INFO="#2563EB",

    TABLE_HEADER="#F3F4F6",
    TABLE_ROW="#FFFFFF",
    TABLE_ALT_ROW="#F9FAFB",
    TABLE_SELECTION="#BFDBFE",
    TABLE_GRID="#E5E7EB",

    INPUT_BG="#FFFFFF",
    INPUT_BORDER="#D1D5DB",
    INPUT_FOCUS="#2563EB",

    CHART_GRID="#E5E7EB",
    CHART_AXIS="#374151",
    CHART_BACKGROUND="#FFFFFF",

)


# =========================================================
# TYPOGRAPHY
# =========================================================

FONT_FAMILY = "Segoe UI"

FONT_MONO = "Consolas"

FONT_SIZE_XS = 10

FONT_SIZE_SM = 11

FONT_SIZE_MD = 12

FONT_SIZE_LG = 14

FONT_SIZE_XL = 16

FONT_SIZE_XXL = 18


# =========================================================
# RADIUS
# =========================================================

RADIUS_SMALL = 6

RADIUS_MEDIUM = 10

RADIUS_LARGE = 14

RADIUS_XL = 18


# =========================================================
# SPACING
# =========================================================

SPACE_4 = 4

SPACE_8 = 8

SPACE_12 = 12

SPACE_16 = 16

SPACE_20 = 20

SPACE_24 = 24

SPACE_32 = 32


# =========================================================
# SHADOWS
# =========================================================

CARD_SHADOW = 16

POPUP_SHADOW = 24


# =========================================================
# DEFAULT THEME
# =========================================================

CURRENT_THEME = DARK
# =========================================================
# GLOBAL QSS GENERATOR
# =========================================================

def build_stylesheet(colors: ThemeColors) -> str:

    return f"""

/* =======================================================
   GLOBAL
======================================================= */

* {{
    font-family: "{FONT_FAMILY}";
    font-size: {FONT_SIZE_MD}px;
    color: {colors.TEXT};
}}

QWidget {{
    background: {colors.WINDOW};
    color: {colors.TEXT};
}}

QMainWindow {{
    background: {colors.WINDOW};
}}

QFrame {{
    background: {colors.CARD};
    border: 1px solid {colors.BORDER};
    border-radius: {RADIUS_MEDIUM}px;
}}

QGroupBox {{
    background: {colors.CARD};
    border: 1px solid {colors.BORDER};
    border-radius: {RADIUS_MEDIUM}px;
    margin-top: 10px;
    padding: 12px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0px 6px;
    color: {colors.TEXT};
    font-weight: 600;
}}

/* =======================================================
   LABELS
======================================================= */

QLabel {{
    background: transparent;
    color: {colors.TEXT};
}}

QLabel#title {{
    font-size: {FONT_SIZE_XXL}px;
    font-weight: 700;
}}

QLabel#subtitle {{
    font-size: {FONT_SIZE_LG}px;
    color: {colors.TEXT_SECONDARY};
}}

QLabel#muted {{
    color: {colors.TEXT_MUTED};
}}

QLabel#success {{
    color: {colors.SUCCESS};
    font-weight: 600;
}}

QLabel#error {{
    color: {colors.ERROR};
    font-weight: 600;
}}

QLabel#warning {{
    color: {colors.WARNING};
    font-weight: 600;
}}

QLabel#info {{
    color: {colors.INFO};
    font-weight: 600;
}}

/* =======================================================
   PUSH BUTTON
======================================================= */

QPushButton {{

    background: {colors.PRIMARY};

    color: white;

    border: none;

    border-radius: {RADIUS_SMALL}px;

    padding: 8px 18px;

    font-weight: 600;

}}

QPushButton:hover {{

    background: {colors.PRIMARY_HOVER};

}}

QPushButton:pressed {{

    background: {colors.PRIMARY_PRESSED};

}}

QPushButton:disabled {{

    background: {colors.TEXT_DISABLED};

    color: white;

}}

/* =======================================================
   SECONDARY BUTTON
======================================================= */

QPushButton#secondary {{

    background: {colors.CARD};

    border: 1px solid {colors.BORDER};

    color: {colors.TEXT};

}}

QPushButton#secondary:hover {{

    background: {colors.SURFACE};

}}

/* =======================================================
   SUCCESS BUTTON
======================================================= */

QPushButton#buy {{

    background: {colors.BUY};

    color: white;

}}

QPushButton#buy:hover {{

    background: #16a34a;

}}

/* =======================================================
   SELL BUTTON
======================================================= */

QPushButton#sell {{

    background: {colors.SELL};

    color: white;

}}

QPushButton#sell:hover {{

    background: #dc2626;

}}

/* =======================================================
   HOLD BUTTON
======================================================= */

QPushButton#hold {{

    background: {colors.HOLD};

    color: white;

}}

/* =======================================================
   TOOL BUTTON
======================================================= */

QToolButton {{

    background: transparent;

    border: none;

    padding: 6px;

    border-radius: {RADIUS_SMALL}px;

}}

QToolButton:hover {{

    background: {colors.SURFACE};

}}

/* =======================================================
   LINE EDIT
======================================================= */

QLineEdit {{

    background: {colors.INPUT_BG};

    border: 1px solid {colors.INPUT_BORDER};

    border-radius: {RADIUS_SMALL}px;

    padding: 8px;

    selection-background-color: {colors.PRIMARY};

}}

QLineEdit:focus {{

    border: 2px solid {colors.INPUT_FOCUS};

}}

QTextEdit {{

    background: {colors.INPUT_BG};

    border: 1px solid {colors.INPUT_BORDER};

    border-radius: {RADIUS_SMALL}px;

    padding: 8px;

}}

QPlainTextEdit {{

    background: {colors.INPUT_BG};

    border: 1px solid {colors.INPUT_BORDER};

    border-radius: {RADIUS_SMALL}px;

    padding: 8px;

}}

/* =======================================================
   COMBO BOX
======================================================= */

QComboBox {{

    background: {colors.INPUT_BG};

    border: 1px solid {colors.INPUT_BORDER};

    border-radius: {RADIUS_SMALL}px;

    padding: 6px 10px;

    min-height: 28px;

}}

QComboBox:hover {{

    border: 1px solid {colors.PRIMARY};

}}

QComboBox:focus {{

    border: 2px solid {colors.INPUT_FOCUS};

}}

QComboBox::drop-down {{

    border: none;

    width: 28px;

    background: transparent;

}}

QComboBox::down-arrow {{

    width: 12px;

    height: 12px;

}}

QComboBox QAbstractItemView {{

    background: {colors.CARD};

    border: 1px solid {colors.BORDER};

    selection-background-color: {colors.PRIMARY};

    selection-color: white;

    outline: none;

}}

/* =======================================================
   SPIN BOX
======================================================= */

QSpinBox,
QDoubleSpinBox {{

    background: {colors.INPUT_BG};

    border: 1px solid {colors.INPUT_BORDER};

    border-radius: {RADIUS_SMALL}px;

    padding: 6px;

}}

QSpinBox:focus,
QDoubleSpinBox:focus {{

    border: 2px solid {colors.INPUT_FOCUS};

}}

QSpinBox::up-button,
QDoubleSpinBox::up-button {{

    width: 18px;

    border: none;

}}

QSpinBox::down-button,
QDoubleSpinBox::down-button {{

    width: 18px;

    border: none;

}}

/* =======================================================
   DATE / TIME EDIT
======================================================= */

QDateEdit,
QTimeEdit,
QDateTimeEdit {{

    background: {colors.INPUT_BG};

    border: 1px solid {colors.INPUT_BORDER};

    border-radius: {RADIUS_SMALL}px;

    padding: 6px;

}}

QDateEdit:focus,
QTimeEdit:focus,
QDateTimeEdit:focus {{

    border: 2px solid {colors.INPUT_FOCUS};

}}

/* =======================================================
   TABLE
======================================================= */

QTableWidget {{

    background: {colors.TABLE_ROW};

    alternate-background-color: {colors.TABLE_ALT_ROW};

    gridline-color: {colors.TABLE_GRID};

    border: 1px solid {colors.BORDER};

    border-radius: {RADIUS_MEDIUM}px;

    selection-background-color: {colors.TABLE_SELECTION};

    selection-color: white;

    outline: none;

    font-size: {FONT_SIZE_SM}px;

}}

QTableWidget::item {{

    padding: 6px;

    border-bottom: 1px solid {colors.TABLE_GRID};

}}

QTableWidget::item:selected {{

    background: {colors.TABLE_SELECTION};

    color: white;

}}

QTableWidget::item:hover {{

    background: {colors.SURFACE};

}}

/* =======================================================
   HEADER VIEW
======================================================= */

QHeaderView::section {{

    background: {colors.TABLE_HEADER};

    color: {colors.TEXT};

    border: none;

    border-right: 1px solid {colors.TABLE_GRID};

    border-bottom: 1px solid {colors.TABLE_GRID};

    padding: 8px;

    font-weight: 700;

}}

QHeaderView::section:hover {{

    background: {colors.PRIMARY};

    color: white;

}}

/* =======================================================
   TREE WIDGET
======================================================= */

QTreeWidget {{

    background: {colors.TABLE_ROW};

    alternate-background-color: {colors.TABLE_ALT_ROW};

    border: 1px solid {colors.BORDER};

    border-radius: {RADIUS_MEDIUM}px;

    outline: none;

}}

QTreeWidget::item {{

    padding: 6px;

}}

QTreeWidget::item:selected {{

    background: {colors.TABLE_SELECTION};

    color: white;

}}

/* =======================================================
   LIST WIDGET
======================================================= */

QListWidget {{

    background: {colors.TABLE_ROW};

    border: 1px solid {colors.BORDER};

    border-radius: {RADIUS_MEDIUM}px;

    outline: none;

}}

QListWidget::item {{

    padding: 8px;

}}

QListWidget::item:selected {{

    background: {colors.TABLE_SELECTION};

    color: white;

}}

QListWidget::item:hover {{

    background: {colors.SURFACE};

}}

/* =======================================================
   SCROLL BAR
======================================================= */

QScrollBar:vertical {{

    background: {colors.SURFACE};

    width: 12px;

    margin: 0px;

    border-radius: 6px;

}}

QScrollBar::handle:vertical {{

    background: {colors.BORDER};

    min-height: 30px;

    border-radius: 6px;

}}

QScrollBar::handle:vertical:hover {{

    background: {colors.PRIMARY};

}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{

    height: 0px;

}}

QScrollBar:horizontal {{

    background: {colors.SURFACE};

    height: 12px;

    border-radius: 6px;

}}

QScrollBar::handle:horizontal {{

    background: {colors.BORDER};

    min-width: 30px;

    border-radius: 6px;

}}

QScrollBar::handle:horizontal:hover {{

    background: {colors.PRIMARY};

}}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{

    width: 0px;

}}

/* =======================================================
   TAB WIDGET
======================================================= */

QTabWidget::pane {{

    border: 1px solid {colors.BORDER};

    background: {colors.CARD};

    border-radius: {RADIUS_MEDIUM}px;

    top: -1px;

}}

QTabWidget::tab-bar {{

    alignment: left;

}}

/* =======================================================
   TAB BAR
======================================================= */

QTabBar::tab {{

    background: {colors.SURFACE};

    color: {colors.TEXT_SECONDARY};

    border: 1px solid {colors.BORDER};

    border-bottom: none;

    border-top-left-radius: {RADIUS_SMALL}px;

    border-top-right-radius: {RADIUS_SMALL}px;

    padding: 8px 18px;

    margin-right: 2px;

    min-width: 100px;

    font-weight: 600;

}}

QTabBar::tab:selected {{

    background: {colors.PRIMARY};

    color: white;

}}

QTabBar::tab:hover {{

    background: {colors.PRIMARY_HOVER};

    color: white;

}}

QTabBar::tab:!selected {{

    margin-top: 3px;

}}

/* =======================================================
   MENU BAR
======================================================= */

QMenuBar {{

    background: {colors.HEADER};

    color: {colors.TEXT};

    border-bottom: 1px solid {colors.BORDER};

}}

QMenuBar::item {{

    background: transparent;

    padding: 8px 12px;

}}

QMenuBar::item:selected {{

    background: {colors.PRIMARY};

    color: white;

}}

QMenuBar::item:pressed {{

    background: {colors.PRIMARY_PRESSED};

}}

/* =======================================================
   MENU
======================================================= */

QMenu {{

    background: {colors.CARD};

    border: 1px solid {colors.BORDER};

    border-radius: {RADIUS_SMALL}px;

    padding: 6px;

}}

QMenu::item {{

    padding: 8px 28px 8px 12px;

    border-radius: {RADIUS_SMALL}px;

}}

QMenu::item:selected {{

    background: {colors.PRIMARY};

    color: white;

}}

QMenu::separator {{

    height: 1px;

    background: {colors.DIVIDER};

    margin: 6px 0px;

}}

/* =======================================================
   TOOL BAR
======================================================= */

QToolBar {{

    background: {colors.HEADER};

    border-bottom: 1px solid {colors.BORDER};

    spacing: 6px;

    padding: 4px;

}}

QToolBar::separator {{

    width: 1px;

    background: {colors.DIVIDER};

}}

/* =======================================================
   DOCK WIDGET
======================================================= */

QDockWidget {{

    background: {colors.SURFACE};

    border: 1px solid {colors.BORDER};

}}

QDockWidget::title {{

    background: {colors.HEADER};

    color: {colors.TEXT};

    padding: 8px;

    text-align: left;

    font-weight: 700;

}}

/* =======================================================
   PROGRESS BAR
======================================================= */

QProgressBar {{

    background: {colors.SURFACE};

    border: 1px solid {colors.BORDER};

    border-radius: {RADIUS_SMALL}px;

    text-align: center;

    min-height: 20px;

}}

QProgressBar::chunk {{

    background: {colors.PRIMARY};

    border-radius: {RADIUS_SMALL}px;

}}

/* =======================================================
   CHECK BOX
======================================================= */

QCheckBox {{

    spacing: 8px;

    color: {colors.TEXT};

}}

QCheckBox::indicator {{

    width: 18px;

    height: 18px;

    border: 1px solid {colors.INPUT_BORDER};

    border-radius: 4px;

    background: {colors.INPUT_BG};

}}

QCheckBox::indicator:checked {{

    background: {colors.PRIMARY};

    border: 1px solid {colors.PRIMARY};

}}

/* =======================================================
   RADIO BUTTON
======================================================= */

QRadioButton {{

    spacing: 8px;

    color: {colors.TEXT};

}}

QRadioButton::indicator {{

    width: 18px;

    height: 18px;

    border-radius: 9px;

    border: 1px solid {colors.INPUT_BORDER};

    background: {colors.INPUT_BG};

}}

QRadioButton::indicator:checked {{

    background: {colors.PRIMARY};

    border: 1px solid {colors.PRIMARY};

}}

/* =======================================================
   SLIDER
======================================================= */

QSlider::groove:horizontal {{

    border: none;

    background: {colors.DIVIDER};

    height: 6px;

    border-radius: 3px;

}}

QSlider::handle:horizontal {{

    background: {colors.PRIMARY};

    width: 18px;

    margin: -6px 0;

    border-radius: 9px;

}}

QSlider::sub-page:horizontal {{

    background: {colors.PRIMARY};

    border-radius: 3px;

}}

QSlider::add-page:horizontal {{

    background: {colors.DIVIDER};

    border-radius: 3px;

}}

/* =======================================================
   SPLITTER
======================================================= */

QSplitter::handle {{

    background: {colors.BORDER};

}}

QSplitter::handle:hover {{

    background: {colors.PRIMARY};

}}

/* =======================================================
   TOOLTIP
======================================================= */

QToolTip {{

    background: {colors.CARD};

    color: {colors.TEXT};

    border: 1px solid {colors.BORDER};

    padding: 6px;

    border-radius: {RADIUS_SMALL}px;

}}
"""


# =========================================================
# THEME MANAGER
# =========================================================

class ThemeManager:
    """
    Centralized theme manager for StockVersity Scanner Pro.
    Responsible for:
        • Theme switching
        • Runtime stylesheet generation
        • Widget refresh
        • Theme persistence
    """

    def __init__(self):

        self._themes = {
            ThemeMode.DARK: DARK,
            ThemeMode.LIGHT: LIGHT,
        }

        self._current_mode = ThemeMode.DARK

        self._current_theme = DARK

    # -----------------------------------------------------
    # Register Theme
    # -----------------------------------------------------

    def register_theme(
        self,
        name: ThemeMode,
        theme: ThemeColors
    ):

        self._themes[name] = theme

    # -----------------------------------------------------
    # Current Theme
    # -----------------------------------------------------

    @property
    def current_theme(self) -> ThemeColors:

        return self._current_theme

    @property
    def current_mode(self) -> ThemeMode:

        return self._current_mode

    # -----------------------------------------------------
    # Set Theme
    # -----------------------------------------------------

    def set_theme(
        self,
        mode: ThemeMode
    ):

        if mode not in self._themes:

            return

        self._current_mode = mode

        self._current_theme = self._themes[mode]

    # -----------------------------------------------------
    # Toggle Theme
    # -----------------------------------------------------

    def toggle_theme(self):

        if self._current_mode == ThemeMode.DARK:

            self.set_theme(
                ThemeMode.LIGHT
            )

        else:

            self.set_theme(
                ThemeMode.DARK
            )

    # -----------------------------------------------------
    # Get Stylesheet
    # -----------------------------------------------------

    def stylesheet(self) -> str:

        return build_stylesheet(
            self._current_theme
        )

    # -----------------------------------------------------
    # Apply Theme
    # -----------------------------------------------------

    def apply_to_application(
        self,
        app
    ):

        app.setStyleSheet(

            self.stylesheet()

        )

    # -----------------------------------------------------
    # Apply Theme
    # -----------------------------------------------------

    def apply_to_widget(
        self,
        widget
    ):

        widget.setStyleSheet(

            self.stylesheet()

        )

    # -----------------------------------------------------
    # Refresh Widget Tree
    # -----------------------------------------------------

    def refresh_widget_tree(
        self,
        widget
    ):

        widget.setStyleSheet(

            self.stylesheet()

        )

        widget.style().unpolish(widget)

        widget.style().polish(widget)

        widget.update()

        for child in widget.findChildren(object):

            try:

                child.style().unpolish(child)

                child.style().polish(child)

                child.update()

            except Exception:

                pass

    # -----------------------------------------------------
    # Theme Dictionary
    # -----------------------------------------------------

    def available_themes(self):

        return list(

            self._themes.keys()

        )

    # -----------------------------------------------------
    # Theme Exists
    # -----------------------------------------------------

    def has_theme(
        self,
        mode: ThemeMode
    ):

        return mode in self._themes

    # -----------------------------------------------------
    # Serialize
    # -----------------------------------------------------

    def serialize(self):

        return {

            "theme": self._current_mode.value

        }

    # -----------------------------------------------------
    # Restore
    # -----------------------------------------------------

    def restore(
        self,
        state: dict
    ):

        if not state:

            return

        value = state.get(

            "theme",

            ThemeMode.DARK.value

        )

        try:

            self.set_theme(

                ThemeMode(value)

            )

        except Exception:

            self.set_theme(

                ThemeMode.DARK

            )


# =========================================================
# GLOBAL INSTANCE
# =========================================================

theme_manager = ThemeManager()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def current_theme() -> ThemeColors:

    return theme_manager.current_theme


def current_mode() -> ThemeMode:

    return theme_manager.current_mode


def set_theme(
    mode: ThemeMode
):

    theme_manager.set_theme(mode)


def toggle_theme():

    theme_manager.toggle_theme()


def stylesheet() -> str:

    return theme_manager.stylesheet()


def apply_theme(app):

    theme_manager.apply_to_application(app)


def apply_widget_theme(widget):

    theme_manager.apply_to_widget(widget)


def refresh_widget_theme(widget):

    theme_manager.refresh_widget_tree(widget)


# =========================================================
# PERSISTENCE HELPERS
# =========================================================

def export_theme_state():

    return theme_manager.serialize()


def import_theme_state(state):

    theme_manager.restore(state)


# =========================================================
# APPLICATION STARTUP
# =========================================================

def initialize_theme(
    app,
    mode: ThemeMode = ThemeMode.DARK
):

    theme_manager.set_theme(mode)

    theme_manager.apply_to_application(app)


# =========================================================
# RELOAD ALL
# =========================================================

def reload_theme(
    app
):

    theme_manager.apply_to_application(app)


# =========================================================
# COLOR UTILITIES
# =========================================================

def color(name: str) -> str:
    """
    Return a color from the active theme by attribute name.
    """

    return getattr(
        theme_manager.current_theme,
        name.upper(),
        "#000000"
    )


def buy_color() -> str:

    return theme_manager.current_theme.BUY


def sell_color() -> str:

    return theme_manager.current_theme.SELL


def hold_color() -> str:

    return theme_manager.current_theme.HOLD


def primary_color() -> str:

    return theme_manager.current_theme.PRIMARY


def accent_color() -> str:

    return theme_manager.current_theme.ACCENT


# =========================================================
# SIGNAL COLORS
# =========================================================

def signal_color(signal: str) -> str:

    signal = str(signal).upper()

    mapping = {

        "BUY": buy_color(),

        "STRONG BUY": buy_color(),

        "LONG": buy_color(),

        "SELL": sell_color(),

        "STRONG SELL": sell_color(),

        "SHORT": sell_color(),

        "HOLD": hold_color(),

        "WAIT": hold_color(),

        "NEUTRAL": theme_manager.current_theme.NEUTRAL,

    }

    return mapping.get(

        signal,

        theme_manager.current_theme.TEXT

    )


# =========================================================
# AI SCORE COLORS
# =========================================================

def score_color(score: float) -> str:

    score = float(score)

    if score >= 90:

        return theme_manager.current_theme.SCORE_HIGH

    if score >= 75:

        return "#65A30D"

    if score >= 60:

        return theme_manager.current_theme.SCORE_MEDIUM

    return theme_manager.current_theme.SCORE_LOW


# =========================================================
# CONFIDENCE COLORS
# =========================================================

def confidence_color(confidence: float) -> str:

    confidence = float(confidence)

    if confidence >= 90:

        return theme_manager.current_theme.CONFIDENCE_HIGH

    if confidence >= 75:

        return "#65A30D"

    if confidence >= 60:

        return theme_manager.current_theme.CONFIDENCE_MEDIUM

    return theme_manager.current_theme.CONFIDENCE_LOW


# =========================================================
# RISK / REWARD COLOR
# =========================================================

def rr_color(rr: float) -> str:

    rr = float(rr)

    if rr >= 4:

        return "#15803D"

    if rr >= 3:

        return "#22C55E"

    if rr >= 2:

        return "#EAB308"

    return "#DC2626"


# =========================================================
# RELATIVE VOLUME COLOR
# =========================================================

def volume_color(rvol: float) -> str:

    rvol = float(rvol)

    if rvol >= 5:

        return "#7C3AED"

    if rvol >= 3:

        return "#2563EB"

    if rvol >= 2:

        return "#14B8A6"

    return theme_manager.current_theme.TEXT_SECONDARY


# =========================================================
# MARKET STATUS COLORS
# =========================================================

def market_status_color(status: str) -> str:

    value = status.strip().lower()

    if value == "open":

        return theme_manager.current_theme.SUCCESS

    if value == "closed":

        return theme_manager.current_theme.ERROR

    if value == "pre-open":

        return theme_manager.current_theme.WARNING

    return theme_manager.current_theme.INFO