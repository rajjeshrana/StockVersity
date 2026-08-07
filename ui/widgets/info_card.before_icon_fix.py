"""
=========================================================
StockVersity Scanner Pro
Professional Info Card Widget
Version : 4.0
Powered By : AI
=========================================================
"""

from __future__ import annotations

from PySide6.QtCore import (
    Qt,
    Signal,
    QPropertyAnimation,
    QEasingCurve,
)

from PySide6.QtGui import (
    QColor,
    QFont,
)

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QSizePolicy,
    QGraphicsDropShadowEffect,
)


class InfoCard(QFrame):
    """
    Professional Dashboard Information Card
    """

    clicked = Signal()

    # =====================================================
    # INIT
    # =====================================================

    def __init__(
        self,
        title: str,
        value="--",
        parent=None
    ):

        super().__init__(parent)

        self.title_text = title
        self.current_value = value
        self.previous_value = value

        self.trend = "neutral"

        self.build_ui()

        self.apply_shadow()

        self.update_value(value)

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(self):

        self.setObjectName("InfoCard")

        self.setMinimumHeight(120)

        self.setSizePolicy(

            QSizePolicy.Expanding,

            QSizePolicy.Fixed

        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(

            15,

            12,

            15,

            12

        )

        layout.setSpacing(8)

        # ----------------------------------------
        # Header
        # ----------------------------------------

        header = QHBoxLayout()

        self.title = QLabel(

            self.title_text

        )

        title_font = QFont()

        title_font.setPointSize(10)

        self.title.setFont(title_font)

        self.status_icon = QLabel("●")

        header.addWidget(

            self.title

        )

        header.addStretch()

        header.addWidget(

            self.status_icon

        )

        layout.addLayout(header)

        # ----------------------------------------
        # Value
        # ----------------------------------------

        self.value = QLabel(

            str(self.current_value)

        )

        value_font = QFont()

        value_font.setPointSize(20)

        value_font.setBold(True)

        self.value.setFont(value_font)

        self.value.setAlignment(

            Qt.AlignCenter

        )

        layout.addWidget(

            self.value

        )

        # ----------------------------------------
        # Footer
        # ----------------------------------------

        footer = QHBoxLayout()

        self.trend_icon = QLabel("➜")

        self.change = QLabel("--")

        self.subtitle = QLabel("")

        footer.addWidget(

            self.trend_icon

        )

        footer.addWidget(

            self.change

        )

        footer.addStretch()

        footer.addWidget(

            self.subtitle

        )

        layout.addLayout(footer)

    # =====================================================
    # SHADOW
    # =====================================================

    def apply_shadow(self):

        shadow = QGraphicsDropShadowEffect()

        shadow.setBlurRadius(18)

        shadow.setOffset(0, 3)

        shadow.setColor(

            QColor(

                0,

                0,

                0,

                80

            )

        )

        self.setGraphicsEffect(

            shadow

        )

    # =====================================================
    # VALUE
    # =====================================================

    def set_value(

        self,

        value

    ):

        self.update_value(value)

    # =====================================================
    # UPDATE VALUE
    # =====================================================

    def update_value(

        self,

        value

    ):

        self.previous_value = self.current_value

        self.current_value = value

        self.value.setText(

            str(value)

        )
            # =====================================================
    # TREND
    # =====================================================

    def set_trend(
        self,
        trend: str
    ):

        trend = trend.lower()

        self.trend = trend

        if trend == "bullish":

            self.trend_icon.setText("▲")

            self.status_icon.setText("🟢")

            self.change.setStyleSheet(
                "color:#00C853;font-weight:bold;"
            )

        elif trend == "bearish":

            self.trend_icon.setText("▼")

            self.status_icon.setText("🔴")

            self.change.setStyleSheet(
                "color:#FF5252;font-weight:bold;"
            )

        else:

            self.trend_icon.setText("➜")

            self.status_icon.setText("🟡")

            self.change.setStyleSheet(
                "color:#FFA000;font-weight:bold;"
            )

    # =====================================================
    # CHANGE %
    # =====================================================

    def set_change(
        self,
        value: float
    ):

        if value > 0:

            self.set_trend("bullish")

            self.change.setText(
                f"+{value:.2f}%"
            )

        elif value < 0:

            self.set_trend("bearish")

            self.change.setText(
                f"{value:.2f}%"
            )

        else:

            self.set_trend("neutral")

            self.change.setText("0.00%")

    # =====================================================
    # SUBTITLE
    # =====================================================

    def set_subtitle(
        self,
        text: str
    ):

        self.subtitle.setText(text)

    # =====================================================
    # STATUS
    # =====================================================

    def set_status(
        self,
        status: str
    ):

        status = status.lower()

        if status == "online":

            self.status_icon.setText("🟢")

        elif status == "offline":

            self.status_icon.setText("🔴")

        elif status == "warning":

            self.status_icon.setText("🟠")

        else:

            self.status_icon.setText("⚪")

    # =====================================================
    # LOADING
    # =====================================================

    def set_loading(
        self,
        loading: bool
    ):

        if loading:

            self.value.setText("Loading...")

            self.setEnabled(False)

        else:

            self.value.setText(
                str(self.current_value)
            )

            self.setEnabled(True)

    # =====================================================
    # VALUE ANIMATION
    # =====================================================

    def animate_value(self):

        animation = QPropertyAnimation(

            self,

            b"windowOpacity"

        )

        animation.setDuration(250)

        animation.setStartValue(0.65)

        animation.setEndValue(1.0)

        animation.setEasingCurve(

            QEasingCurve.OutCubic

        )

        animation.start()

        self._animation = animation

    # =====================================================
    # FLASH
    # =====================================================

    def flash(self):

        self.animate_value()

    # =====================================================
    # UPDATE VALUE
    # =====================================================

    def update_value(
        self,
        value
    ):

        self.previous_value = self.current_value

        self.current_value = value

        self.value.setText(
            str(value)
        )

        self.animate_value()

    # =====================================================
    # MOUSE EVENTS
    # =====================================================

    def mousePressEvent(
        self,
        event
    ):

        self.clicked.emit()

        super().mousePressEvent(event)

    # =====================================================
    # HOVER ENTER
    # =====================================================

    def enterEvent(
        self,
        event
    ):

        self.setCursor(
            Qt.PointingHandCursor
        )

        self.setProperty(
            "hover",
            True
        )

        self.style().unpolish(self)

        self.style().polish(self)

        super().enterEvent(event)

    # =====================================================
    # HOVER LEAVE
    # =====================================================

    def leaveEvent(
        self,
        event
    ):

        self.setProperty(
            "hover",
            False
        )

        self.style().unpolish(self)

        self.style().polish(self)

        super().leaveEvent(event)
            # =====================================================
    # COMPACT MODE
    # =====================================================

    def set_compact_mode(
        self,
        enabled: bool
    ):

        if enabled:

            self.setMinimumHeight(85)

            value_font = self.value.font()
            value_font.setPointSize(14)
            self.value.setFont(value_font)

            self.subtitle.hide()

        else:

            self.setMinimumHeight(120)

            value_font = self.value.font()
            value_font.setPointSize(20)
            value_font.setBold(True)

            self.value.setFont(value_font)

            self.subtitle.show()

    # =====================================================
    # EXPANDED MODE
    # =====================================================

    def set_expanded_mode(self):

        self.set_compact_mode(False)

    # =====================================================
    # AUTO TREND DETECTION
    # =====================================================

    def detect_trend(self):

        try:

            current = float(str(self.current_value).replace(",", ""))

            previous = float(str(self.previous_value).replace(",", ""))

        except Exception:

            return

        if current > previous:

            self.set_trend("bullish")

        elif current < previous:

            self.set_trend("bearish")

        else:

            self.set_trend("neutral")

    # =====================================================
    # FORMAT NUMBER
    # =====================================================

    def set_numeric_value(
        self,
        value: float,
        decimals: int = 2
    ):

        self.update_value(

            f"{value:,.{decimals}f}"

        )

        self.detect_trend()

    # =====================================================
    # FORMAT CURRENCY
    # =====================================================

    def set_currency(
        self,
        value: float
    ):

        self.update_value(

            f"₹{value:,.2f}"

        )

        self.detect_trend()

    # =====================================================
    # FORMAT PERCENTAGE
    # =====================================================

    def set_percentage(
        self,
        value: float
    ):

        self.update_value(

            f"{value:.2f}%"

        )

        self.set_change(value)

    # =====================================================
    # COLOR THEMES
    # =====================================================

    def set_color_theme(
        self,
        color: str
    ):

        self.value.setStyleSheet(

            f"color:{color};"

        )

    # =====================================================
    # DEFAULT COLORS
    # =====================================================

    def reset_colors(self):

        self.value.setStyleSheet("")

        self.change.setStyleSheet("")

        self.title.setStyleSheet("")

    # =====================================================
    # SPARKLINE PLACEHOLDER
    # =====================================================

    def set_sparkline_data(
        self,
        values: list
    ):

        self.sparkline_data = values

    # =====================================================
    # LAST UPDATE
    # =====================================================

    def set_last_updated(
        self,
        text: str
    ):

        self.subtitle.setText(

            f"Updated: {text}"

        )

    # =====================================================
    # TOOLTIP
    # =====================================================

    def set_description(
        self,
        text: str
    ):

        self.setToolTip(text)

    # =====================================================
    # ENABLE
    # =====================================================

    def enable(self):

        self.setEnabled(True)

    # =====================================================
    # DISABLE
    # =====================================================

    def disable(self):

        self.setEnabled(False)

    # =====================================================
    # DIAGNOSTICS
    # =====================================================

    def diagnostics(self):

        return {

            "title": self.title_text,

            "value": self.current_value,

            "previous": self.previous_value,

            "trend": self.trend,

            "enabled": self.isEnabled(),

            "visible": self.isVisible()

        }

    # =====================================================
    # EXPORT
    # =====================================================

    def export_state(self):

        return {

            "title": self.title_text,

            "value": self.current_value,

            "previous": self.previous_value,

            "trend": self.trend,

            "subtitle": self.subtitle.text()

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

        self.title_text = state.get(
            "title",
            self.title_text
        )

        self.title.setText(
            self.title_text
        )

        self.previous_value = state.get(
            "previous",
            self.previous_value
        )

        self.update_value(
            state.get(
                "value",
                self.current_value
            )
        )

        self.set_trend(
            state.get(
                "trend",
                "neutral"
            )
        )

        self.subtitle.setText(
            state.get(
                "subtitle",
                ""
            )
        )

    # =====================================================
    # THEME
    # =====================================================

    def apply_theme(
        self,
        theme: str
    ):

        self.setProperty(
            "theme",
            theme
        )

        self.style().unpolish(self)

        self.style().polish(self)

        self.update()

    # =====================================================
    # STATUS PRESETS
    # =====================================================

    def set_bullish(self):

        self.set_trend("bullish")

    def set_bearish(self):

        self.set_trend("bearish")

    def set_neutral(self):

        self.set_trend("neutral")

    # =====================================================
    # ALERT MODE
    # =====================================================

    def set_alert(
        self,
        enabled: bool
    ):

        if enabled:

            self.setStyleSheet(
                """
                QFrame#InfoCard{
                    border:2px solid #ff9800;
                }
                """
            )

        else:

            self.setStyleSheet("")

    # =====================================================
    # HIGHLIGHT
    # =====================================================

    def highlight(
        self,
        color: str = "#00C853"
    ):

        self.setStyleSheet(
            f"""
            QFrame#InfoCard{{
                border:2px solid {color};
            }}
            """
        )

    # =====================================================
    # CLEAR HIGHLIGHT
    # =====================================================

    def clear_highlight(self):

        self.setStyleSheet("")

    # =====================================================
    # BLINK
    # =====================================================

    def blink(self):

        animation = QPropertyAnimation(
            self,
            b"windowOpacity"
        )

        animation.setDuration(700)

        animation.setStartValue(0.35)

        animation.setEndValue(1.0)

        animation.setLoopCount(3)

        animation.start()

        self._blink_animation = animation

    # =====================================================
    # HEALTH
    # =====================================================

    def health_status(self):

        return {

            "component":
                "InfoCard",

            "healthy":
                True,

            "title":
                self.title_text,

            "enabled":
                self.isEnabled(),

            "visible":
                self.isVisible(),

            "trend":
                self.trend

        }

    # =====================================================
    # BUILD INFO
    # =====================================================

    def build_information(self):

        return {

            "application":
                "StockVersity Scanner Pro",

            "component":
                "InfoCard",

            "version":
                "4.0",

            "powered_by":
                "AI"

        }

    # =====================================================
    # ACCESSIBILITY
    # =====================================================

    def focusInEvent(
        self,
        event
    ):

        self.highlight("#2196F3")

        super().focusInEvent(event)

    def focusOutEvent(
        self,
        event
    ):

        self.clear_highlight()

        super().focusOutEvent(event)

    # =====================================================
    # KEYBOARD
    # =====================================================

    def keyPressEvent(
        self,
        event
    ):

        if event.key() in (
            Qt.Key_Return,
            Qt.Key_Enter,
            Qt.Key_Space
        ):

            self.clicked.emit()

            return

        super().keyPressEvent(event)

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh(self):

        self.detect_trend()

        self.update()

        self.repaint()
            # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        self.previous_value = "--"

        self.current_value = "--"

        self.value.setText("--")

        self.change.setText("--")

        self.subtitle.clear()

        self.set_neutral()

        self.reset_colors()

        self.clear_highlight()

        self.setEnabled(True)

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(self):

        self.reset()

    # =====================================================
    # TITLE
    # =====================================================

    def set_title(
        self,
        title: str
    ):

        self.title_text = title

        self.title.setText(title)

    # =====================================================
    # GETTERS
    # =====================================================

    def get_title(self):

        return self.title_text

    def get_value(self):

        return self.current_value

    def get_previous_value(self):

        return self.previous_value

    # =====================================================
    # COMPONENT INFO
    # =====================================================

    @property
    def component_name(self):

        return "InfoCard"

    @property
    def application_name(self):

        return "StockVersity Scanner Pro"

    @property
    def version(self):

        return "4.0"

    # =====================================================
    # IS POSITIVE
    # =====================================================

    def is_positive(self):

        return self.trend == "bullish"

    # =====================================================
    # IS NEGATIVE
    # =====================================================

    def is_negative(self):

        return self.trend == "bearish"

    # =====================================================
    # IS NEUTRAL
    # =====================================================

    def is_neutral(self):

        return self.trend == "neutral"

    # =====================================================
    # COMPLETE STATE
    # =====================================================

    def state(self):

        return {

            "title": self.title_text,

            "value": self.current_value,

            "previous": self.previous_value,

            "trend": self.trend,

            "subtitle": self.subtitle.text(),

            "enabled": self.isEnabled(),

            "visible": self.isVisible()

        }

    # =====================================================
    # REFRESH DISPLAY
    # =====================================================

    def refresh_display(self):

        self.value.setText(

            str(self.current_value)

        )

        self.detect_trend()

        self.update()

        self.repaint()

    # =====================================================
    # DESTROY
    # =====================================================

    def shutdown(self):

        self.reset()

    # =====================================================
    # CLOSE
    # =====================================================

    def closeEvent(
        self,
        event
    ):

        self.shutdown()

        super().closeEvent(event)

    # =====================================================
    # STRING
    # =====================================================

    def __repr__(self):

        return (

            f"<InfoCard "

            f"title='{self.title_text}' "

            f"value='{self.current_value}' "

            f"trend='{self.trend}'>"

        )


# =====================================================
# FACTORY
# =====================================================

def create_info_card(
    title: str,
    value="--"
):

    return InfoCard(
        title,
        value
    )


# =====================================================
# END OF FILE
# =====================================================