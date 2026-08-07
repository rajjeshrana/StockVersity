"""
=========================================================
StockVersity Scanner Pro
Reusable Card Component
Version : 4.0
Powered by AI
=========================================================
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import (
    QEasingCurve,
    Property,
    QPropertyAnimation,
    QRect,
    Qt,
    Signal,
)

from PySide6.QtGui import (
    QColor,
    QFont,
)

from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from ui.theme import (
    current_theme,
    FONT_SIZE_LG,
    FONT_SIZE_MD,
    FONT_SIZE_SM,
)


# =========================================================
# BASE CARD
# =========================================================

class Card(QFrame):

    # -----------------------------------------------------
    # Signals
    # -----------------------------------------------------

    clicked = Signal()

    doubleClicked = Signal()

    expanded = Signal()

    collapsed = Signal()

    # -----------------------------------------------------

    def __init__(

        self,

        title: str = "",

        parent=None

    ):

        super().__init__(parent)

        self.title = title

        self._expanded = True

        self._hover = False

        self._status_color = current_theme().PRIMARY

        self._shadow_enabled = True

        self._animation = None

        self._build_ui()

        self._build_shadow()

        self._connect_signals()

    # =====================================================
    # BUILD UI
    # =====================================================

    def _build_ui(self):

        self.setObjectName("Card")

        self.setSizePolicy(

            QSizePolicy.Expanding,

            QSizePolicy.Preferred

        )

        self.main_layout = QVBoxLayout(self)

        self.main_layout.setContentsMargins(

            16,

            16,

            16,

            16

        )

        self.main_layout.setSpacing(12)

        # ------------------------------------------
        # Header
        # ------------------------------------------

        self.header = QWidget()

        self.header_layout = QHBoxLayout(self.header)

        self.header_layout.setContentsMargins(

            0,

            0,

            0,

            0

        )

        self.header_layout.setSpacing(10)

        # ------------------------------------------
        # Status Indicator
        # ------------------------------------------

        self.status_indicator = QLabel()

        self.status_indicator.setFixedSize(10, 10)

        self.status_indicator.setObjectName(

            "cardStatus"

        )

        # ------------------------------------------
        # Title
        # ------------------------------------------

        self.title_label = QLabel(self.title)

        font = QFont()

        font.setPointSize(FONT_SIZE_LG)

        font.setBold(True)

        self.title_label.setFont(font)

        # ------------------------------------------
        # Spacer
        # ------------------------------------------

        self.header_layout.addWidget(

            self.status_indicator

        )

        self.header_layout.addWidget(

            self.title_label

        )

        self.header_layout.addItem(

            QSpacerItem(

                20,

                20,

                QSizePolicy.Expanding,

                QSizePolicy.Minimum

            )

        )

        # ------------------------------------------
        # Action Button
        # ------------------------------------------

        self.action_button = QPushButton("⋯")

        self.action_button.setFixedSize(28, 28)

        self.action_button.setObjectName(

            "secondary"

        )

        self.header_layout.addWidget(

            self.action_button

        )

        # ------------------------------------------
        # Body
        # ------------------------------------------

        self.body = QWidget()

        self.body_layout = QVBoxLayout(self.body)

        self.body_layout.setContentsMargins(

            0,

            0,

            0,

            0

        )

        self.body_layout.setSpacing(12)

        # ------------------------------------------
        # Footer
        # ------------------------------------------

        self.footer = QWidget()

        self.footer_layout = QHBoxLayout(self.footer)

        self.footer_layout.setContentsMargins(

            0,

            8,

            0,

            0

        )

        self.footer_layout.setSpacing(8)

        self.footer.hide()

        # ------------------------------------------
        # Add Widgets
        # ------------------------------------------

        self.main_layout.addWidget(

            self.header

        )

        self.main_layout.addWidget(

            self.body

        )

        self.main_layout.addWidget(

            self.footer
        )

    # =====================================================
    # SHADOW
    # =====================================================

    def _build_shadow(self):

        if not self._shadow_enabled:

            return

        shadow = QGraphicsDropShadowEffect(self)

        shadow.setBlurRadius(24)

        shadow.setOffset(0, 6)

        shadow.setColor(

            QColor(

                0,

                0,

                0,

                70

            )

        )

        self.setGraphicsEffect(

            shadow

        )

    # =====================================================
    # CONNECTIONS
    # =====================================================

    def _connect_signals(self):

        self.action_button.clicked.connect(

            self.toggle

        )

    # =====================================================
    # PUBLIC API
    # =====================================================

    def add_widget(

        self,

        widget: QWidget

    ):

        self.body_layout.addWidget(widget)

    def add_footer_widget(

        self,

        widget: QWidget

    ):

        self.footer.show()

        self.footer_layout.addWidget(widget)

    def set_title(

        self,

        title: str

    ):

        self.title = title

        self.title_label.setText(title)

    def set_status_color(

        self,

        color: str

    ):

        self._status_color = color

        self.status_indicator.setStyleSheet(

            f"""

            border-radius:5px;

            background:{color};

            """

        )
            # =====================================================
    # EXPAND / COLLAPSE
    # =====================================================

    def expand(self):

        if self._expanded:

            return

        self._expanded = True

        self.body.show()

        self.footer.setVisible(

            self.footer_layout.count() > 0

        )

        self._animate_content(True)

        self.expanded.emit()

    def collapse(self):

        if not self._expanded:

            return

        self._expanded = False

        self._animate_content(False)

        self.collapsed.emit()

    def toggle(self):

        if self._expanded:

            self.collapse()

        else:

            self.expand()

    # =====================================================
    # CONTENT ANIMATION
    # =====================================================

    def _animate_content(
        self,
        expanding: bool
    ):

        self._animation = QPropertyAnimation(

            self.body,

            b"maximumHeight",

            self

        )

        self._animation.setDuration(220)

        self._animation.setEasingCurve(

            QEasingCurve.OutCubic

        )

        if expanding:

            self.body.show()

            target = max(

                self.body.sizeHint().height(),

                1

            )

            self._animation.setStartValue(0)

            self._animation.setEndValue(target)

        else:

            current = max(

                self.body.height(),

                self.body.sizeHint().height()

            )

            self._animation.setStartValue(current)

            self._animation.setEndValue(0)

            self._animation.finished.connect(

                self.body.hide

            )

            self._animation.finished.connect(

                self.footer.hide

            )

        self._animation.start()

    # =====================================================
    # HOVER PROPERTY
    # =====================================================

    def get_hover_progress(self):

        return getattr(

            self,

            "_hover_progress",

            0.0

        )

    def set_hover_progress(

        self,

        value

    ):

        self._hover_progress = value

        self.update()

    hoverProgress = Property(

        float,

        get_hover_progress,

        set_hover_progress

    )

    # =====================================================
    # HOVER ANIMATION
    # =====================================================

    def animate_hover(

        self,

        entering: bool

    ):

        animation = QPropertyAnimation(

            self,

            b"hoverProgress",

            self

        )

        animation.setDuration(180)

        animation.setEasingCurve(

            QEasingCurve.OutQuad

        )

        animation.setStartValue(

            self.get_hover_progress()

        )

        animation.setEndValue(

            1.0 if entering else 0.0

        )

        animation.start()

        self._hover_animation = animation

    # =====================================================
    # SHADOW CONTROL
    # =====================================================

    def enable_shadow(

        self,

        enabled: bool = True

    ):

        self._shadow_enabled = enabled

        if enabled:

            self._build_shadow()

        else:

            self.setGraphicsEffect(None)

    # =====================================================
    # RAISE EFFECT
    # =====================================================

    def raise_card(self):

        effect = self.graphicsEffect()

        if isinstance(

            effect,

            QGraphicsDropShadowEffect

        ):

            effect.setBlurRadius(36)

            effect.setOffset(0, 10)

    def lower_card(self):

        effect = self.graphicsEffect()

        if isinstance(

            effect,

            QGraphicsDropShadowEffect

        ):

            effect.setBlurRadius(24)

            effect.setOffset(0, 6)

    # =====================================================
    # ENTER EVENT
    # =====================================================

    def enterEvent(

        self,

        event

    ):

        self._hover = True

        self.animate_hover(True)

        self.raise_card()

        super().enterEvent(event)

    # =====================================================
    # LEAVE EVENT
    # =====================================================

    def leaveEvent(

        self,

        event

    ):

        self._hover = False

        self.animate_hover(False)

        self.lower_card()

        super().leaveEvent(event)

    # =====================================================
    # MOUSE EVENTS
    # =====================================================

    def mousePressEvent(

        self,

        event

    ):

        if event.button() == Qt.LeftButton:

            self.clicked.emit()

        super().mousePressEvent(event)

    def mouseDoubleClickEvent(

        self,

        event

    ):

        if event.button() == Qt.LeftButton:

            self.doubleClicked.emit()

        super().mouseDoubleClickEvent(event)

    # =====================================================
    # GLASS STYLE
    # =====================================================

    def apply_glass_style(self):

        colors = current_theme()

        self.setStyleSheet(

            f"""
            QFrame#Card {{

                background-color: {colors.CARD};

                border: 1px solid {colors.BORDER};

                border-radius: 14px;

            }}

            QLabel {{

                background: transparent;

            }}

            """
        )

    # =====================================================
    # THEME REFRESH
    # =====================================================

    def refresh_theme(self):

        self.apply_glass_style()

        self.set_status_color(

            self._status_color

        )

        self.update()
            # =====================================================
    # HEADER ACTIONS
    # =====================================================

    def set_action_text(
        self,
        text: str
    ):

        self.action_button.setText(text)

    def set_action_icon(
        self,
        icon
    ):

        self.action_button.setIcon(icon)

    def hide_action_button(self):

        self.action_button.hide()

    def show_action_button(self):

        self.action_button.show()

    def set_action_tooltip(
        self,
        text: str
    ):

        self.action_button.setToolTip(text)

    # =====================================================
    # HEADER WIDGETS
    # =====================================================

    def add_header_widget(
        self,
        widget: QWidget
    ):

        self.header_layout.insertWidget(

            self.header_layout.count() - 2,

            widget

        )

    # =====================================================
    # TOOLBAR
    # =====================================================

    def create_toolbar(self):

        self.toolbar = QWidget()

        self.toolbar_layout = QHBoxLayout(

            self.toolbar

        )

        self.toolbar_layout.setContentsMargins(

            0,

            0,

            0,

            0

        )

        self.toolbar_layout.setSpacing(6)

        self.body_layout.insertWidget(

            0,

            self.toolbar

        )

        return self.toolbar

    def add_toolbar_widget(

        self,

        widget: QWidget

    ):

        if not hasattr(

            self,

            "toolbar"

        ):

            self.create_toolbar()

        self.toolbar_layout.addWidget(widget)

    # =====================================================
    # LOADING STATE
    # =====================================================

    def set_loading(

        self,

        loading: bool,

        message: str = "Loading..."

    ):

        if loading:

            if not hasattr(

                self,

                "loading_label"

            ):

                self.loading_label = QLabel()

                self.loading_label.setAlignment(

                    Qt.AlignCenter

                )

                self.body_layout.addWidget(

                    self.loading_label

                )

            self.loading_label.setText(message)

            self.loading_label.show()

        else:

            if hasattr(

                self,

                "loading_label"

            ):

                self.loading_label.hide()

    # =====================================================
    # SUCCESS MESSAGE
    # =====================================================

    def show_success(

        self,

        message: str

    ):

        self._show_banner(

            message,

            current_theme().SUCCESS

        )

    # =====================================================
    # ERROR MESSAGE
    # =====================================================

    def show_error(

        self,

        message: str

    ):

        self._show_banner(

            message,

            current_theme().ERROR

        )

    # =====================================================
    # WARNING MESSAGE
    # =====================================================

    def show_warning(

        self,

        message: str

    ):

        self._show_banner(

            message,

            current_theme().WARNING

        )

    # =====================================================
    # INFO MESSAGE
    # =====================================================

    def show_info(

        self,

        message: str

    ):

        self._show_banner(

            message,

            current_theme().INFO

        )

    # =====================================================
    # BANNER
    # =====================================================

    def _show_banner(

        self,

        message: str,

        color: str

    ):

        if not hasattr(

            self,

            "_banner"

        ):

            self._banner = QLabel()

            self._banner.setWordWrap(True)

            self.body_layout.insertWidget(

                0,

                self._banner

            )

        self._banner.setText(message)

        self._banner.setStyleSheet(

            f"""

            background:{color};

            color:white;

            padding:8px;

            border-radius:8px;

            font-weight:600;

            """

        )

        self._banner.show()

    def hide_banner(self):

        if hasattr(

            self,

            "_banner"

        ):

            self._banner.hide()

    # =====================================================
    # DRAG SUPPORT
    # =====================================================

    def enable_drag(

        self,

        enabled: bool = True

    ):

        self._drag_enabled = enabled

        self._drag_origin = None

    # =====================================================
    # START DRAG
    # =====================================================

    def mouseMoveEvent(

        self,

        event

    ):

        if not getattr(

            self,

            "_drag_enabled",

            False

        ):

            return super().mouseMoveEvent(event)

        if event.buttons() & Qt.LeftButton:

            if self._drag_origin is None:

                self._drag_origin = event.globalPosition()

                return

            delta = (

                event.globalPosition()

                - self._drag_origin

            )

            self.move(

                self.x() + int(delta.x()),

                self.y() + int(delta.y())

            )

            self._drag_origin = event.globalPosition()

        super().mouseMoveEvent(event)

    # =====================================================
    # RESET DRAG
    # =====================================================

    def mouseReleaseEvent(

        self,

        event

    ):

        self._drag_origin = None

        super().mouseReleaseEvent(event)

    # =====================================================
    # RESIZE SUPPORT
    # =====================================================

    def set_card_size(

        self,

        width: int,

        height: int

    ):

        self.resize(

            width,

            height

        )

    def set_minimum_card_size(

        self,

        width: int,

        height: int

    ):

        self.setMinimumSize(

            width,

            height

        )

    def set_maximum_card_size(

        self,

        width: int,

        height: int

    ):

        self.setMaximumSize(

            width,

            height

        )
            # =====================================================
    # MINIMIZE
    # =====================================================

    def minimize(self):

        if not self._expanded:

            return

        self.collapse()

    # =====================================================
    # MAXIMIZE
    # =====================================================

    def maximize(self):

        if self._expanded:

            return

        self.expand()

    # =====================================================
    # PIN CARD
    # =====================================================

    def pin(self):

        self._pinned = True

    # =====================================================
    # UNPIN CARD
    # =====================================================

    def unpin(self):

        self._pinned = False

    # =====================================================
    # TOGGLE PIN
    # =====================================================

    def toggle_pin(self):

        self._pinned = not getattr(

            self,

            "_pinned",

            False

        )

    # =====================================================
    # IS PINNED
    # =====================================================

    @property
    def pinned(self):

        return getattr(

            self,

            "_pinned",

            False

        )

    # =====================================================
    # FULL SCREEN
    # =====================================================

    def enter_fullscreen(self):

        if getattr(

            self,

            "_fullscreen",

            False

        ):

            return

        self._fullscreen = True

        self._normal_geometry = self.geometry()

        self.setParent(None)

        self.showFullScreen()

    # =====================================================
    # EXIT FULL SCREEN
    # =====================================================

    def exit_fullscreen(self):

        if not getattr(

            self,

            "_fullscreen",

            False

        ):

            return

        self._fullscreen = False

        self.showNormal()

        if hasattr(

            self,

            "_normal_geometry"

        ):

            self.setGeometry(

                self._normal_geometry

            )

    # =====================================================
    # TOGGLE FULL SCREEN
    # =====================================================

    def toggle_fullscreen(self):

        if getattr(

            self,

            "_fullscreen",

            False

        ):

            self.exit_fullscreen()

        else:

            self.enter_fullscreen()

    # =====================================================
    # SAVE STATE
    # =====================================================

    def save_state(self):

        return {

            "title":

                self.title,

            "expanded":

                self._expanded,

            "pinned":

                getattr(

                    self,

                    "_pinned",

                    False

                ),

            "fullscreen":

                getattr(

                    self,

                    "_fullscreen",

                    False

                ),

            "status_color":

                self._status_color,

            "visible":

                self.isVisible(),

            "geometry":

                [

                    self.x(),

                    self.y(),

                    self.width(),

                    self.height()

                ]

        }

    # =====================================================
    # RESTORE STATE
    # =====================================================

    def restore_state(

        self,

        state: dict

    ):

        if not state:

            return

        self.set_title(

            state.get(

                "title",

                self.title

            )

        )

        self.set_status_color(

            state.get(

                "status_color",

                self._status_color

            )

        )

        if state.get(

            "expanded",

            True

        ):

            self.expand()

        else:

            self.collapse()

        if state.get(

            "pinned",

            False

        ):

            self.pin()

        else:

            self.unpin()

        geometry = state.get("geometry")

        if geometry and len(geometry) == 4:

            self.setGeometry(

                QRect(

                    geometry[0],

                    geometry[1],

                    geometry[2],

                    geometry[3]

                )

            )

    # =====================================================
    # KEYBOARD SHORTCUTS
    # =====================================================

    def keyPressEvent(

        self,

        event

    ):

        key = event.key()

        modifiers = event.modifiers()

        if key == Qt.Key_Space:

            self.toggle()

            event.accept()

            return

        if key == Qt.Key_F11:

            self.toggle_fullscreen()

            event.accept()

            return

        if (

            modifiers & Qt.ControlModifier

            and key == Qt.Key_P

        ):

            self.toggle_pin()

            event.accept()

            return

        super().keyPressEvent(event)

    # =====================================================
    # ACCESSIBILITY
    # =====================================================

    def configure_accessibility(self):

        self.setAccessibleName(

            self.title

        )

        self.setAccessibleDescription(

            f"{self.title} dashboard card"

        )

        self.action_button.setAccessibleName(

            "Card Actions"

        )

    # =====================================================
    # DIAGNOSTICS
    # =====================================================

    def diagnostics(self):

        return {

            "title":

                self.title,

            "expanded":

                self._expanded,

            "pinned":

                self.pinned,

            "fullscreen":

                getattr(

                    self,

                    "_fullscreen",

                    False

                ),

            "visible":

                self.isVisible(),

            "widgets":

                self.body_layout.count(),

            "footer":

                self.footer_layout.count(),

            "hover":

                self._hover,

            "shadow":

                self._shadow_enabled

        }

    # =====================================================
    # PERFORMANCE
    # =====================================================

    def begin_bulk_update(self):

        self.setUpdatesEnabled(False)

    def end_bulk_update(self):

        self.setUpdatesEnabled(True)

        self.update()

    # =====================================================
    # CLEAR BODY
    # =====================================================

    def clear_body(self):

        while self.body_layout.count():

            item = self.body_layout.takeAt(0)

            widget = item.widget()

            if widget:

                widget.deleteLater()

    # =====================================================
    # CLEAR FOOTER
    # =====================================================

    def clear_footer(self):

        while self.footer_layout.count():

            item = self.footer_layout.takeAt(0)

            widget = item.widget()

            if widget:

                widget.deleteLater()

        self.footer.hide()
            # =====================================================
    # CLONE
    # =====================================================

    def clone(self):

        cloned = self.__class__(

            title=self.title

        )

        cloned.restore_state(

            self.save_state()

        )

        return cloned

    # =====================================================
    # EXPORT
    # =====================================================

    def export(self):

        return {

            "metadata": self.metadata(),

            "state": self.save_state(),

            "diagnostics": self.diagnostics(),

        }

    # =====================================================
    # IMPORT
    # =====================================================

    def import_data(

        self,

        data: dict

    ):

        if not data:

            return

        state = data.get(

            "state",

            {}

        )

        self.restore_state(state)

    # =====================================================
    # THEME SYNCHRONIZATION
    # =====================================================

    def synchronize_theme(self):

        self.refresh_theme()

        for child in self.findChildren(QWidget):

            try:

                child.style().unpolish(child)

                child.style().polish(child)

                child.update()

            except Exception:

                pass

        self.update()

    # =====================================================
    # LIFECYCLE
    # =====================================================

    def initialize(self):

        self.configure_accessibility()

        self.apply_glass_style()

        self.refresh_theme()

    # =====================================================
    # STARTUP
    # =====================================================

    def startup(self):

        self.initialize()

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(self):

        self.begin_bulk_update()

        self.clear_body()

        self.clear_footer()

        self.hide_banner()

        self.end_bulk_update()

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        self.set_title("")

        self.set_status_color(

            current_theme().PRIMARY

        )

        self.unpin()

        self.expand()

        self.hide_banner()

    # =====================================================
    # COMPONENT METADATA
    # =====================================================

    @staticmethod
    def metadata():

        return {

            "component": "Card",

            "application": "StockVersity Scanner Pro",

            "version": "4.0",

            "powered_by": "AI",

            "type": "Reusable Dashboard Card"

        }

    # =====================================================
    # STRING REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (

            f"<Card "

            f"title='{self.title}' "

            f"expanded={self._expanded} "

            f"widgets={self.body_layout.count()}>"

        )


# =========================================================
# FACTORY
# =========================================================

def create_card(

    title: str = ""

) -> Card:

    card = Card(title)

    card.initialize()

    return card


# =========================================================
# SPECIALIZED CARDS
# =========================================================

class AnalyticsCard(Card):

    def __init__(

        self,

        title="Analytics",

        parent=None

    ):

        super().__init__(title, parent)


class ScannerCard(Card):

    def __init__(

        self,

        title="Scanner",

        parent=None

    ):

        super().__init__(title, parent)


class DashboardCard(Card):

    def __init__(

        self,

        title="Dashboard",

        parent=None

    ):

        super().__init__(title, parent)


class StatusCard(Card):

    def __init__(

        self,

        title="Status",

        parent=None

    ):

        super().__init__(title, parent)


# =========================================================
# PUBLIC EXPORTS
# =========================================================

__all__ = [

    "Card",

    "AnalyticsCard",

    "ScannerCard",

    "DashboardCard",

    "StatusCard",

    "create_card",

]


# =========================================================
# END OF FILE
# =========================================================