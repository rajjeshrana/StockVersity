"""
=========================================================
StockVersity Scanner Pro

Settings Page
=========================================================
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QFormLayout,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QColorDialog,
    QMessageBox,
    QLineEdit,
)

from core.app_controller import AppController
from core.configuration_manager import get_configuration


class SettingsPage(QWidget):

    def __init__(self, controller: AppController):

        super().__init__()

        self.controller = controller
        self.config = get_configuration()

        self.build_ui()

        self.load_settings()

    # ==================================================
    # UI
    # ==================================================

    def build_ui(self):

        self.main_layout = QVBoxLayout(self)

        self.main_layout.setContentsMargins(
            20,
            20,
            20,
            20,
        )

        self.main_layout.setSpacing(20)

        title = QLabel("Application Settings")

        title.setObjectName("pageTitle")

        self.main_layout.addWidget(title)

        self.create_general_group()

        self.create_scanner_group()

        self.create_risk_group()

        self.create_buttons()

        self.main_layout.addStretch()

    # ==================================================
    # GENERAL
    # ==================================================

    def create_general_group(self):

        group = QGroupBox("General")

        layout = QFormLayout(group)

        self.theme_combo = QComboBox()

        self.theme_combo.addItems(

            [

                "Dark",

                "Light",

            ]

        )

        self.accent_edit = QLineEdit()

        self.accent_button = QPushButton(

            "Choose"

        )

        accent_layout = QHBoxLayout()

        accent_layout.addWidget(

            self.accent_edit

        )

        accent_layout.addWidget(

            self.accent_button

        )

        accent_widget = QWidget()

        accent_widget.setLayout(

            accent_layout

        )

        self.auto_refresh = QSpinBox()

        self.auto_refresh.setRange(

            5,

            3600,

        )

        self.auto_refresh.setSuffix(

            " sec"

        )

        layout.addRow(

            "Theme",

            self.theme_combo,

        )

        layout.addRow(

            "Accent",

            accent_widget,

        )

        layout.addRow(

            "Auto Refresh",

            self.auto_refresh,

        )

        self.main_layout.addWidget(group)

        self.accent_button.clicked.connect(

            self.choose_color

        )

    # ==================================================
    # SCANNER
    # ==================================================

    def create_scanner_group(self):

        group = QGroupBox(

            "Scanner"

        )

        layout = QFormLayout(group)

        self.strategy_combo = QComboBox()

        self.strategy_combo.addItems(

            [

                "Intraday",

                "Swing",

                "Positional",

            ]

        )

        self.ai_score = QSpinBox()

        self.ai_score.setRange(

            0,

            100,

        )

        self.worker_spin = QSpinBox()

        self.worker_spin.setRange(

            1,

            32,

        )

        layout.addRow(

            "Default Strategy",

            self.strategy_combo,

        )

        layout.addRow(

            "Minimum AI Score",

            self.ai_score,

        )

        layout.addRow(

            "Threads",

            self.worker_spin,

        )

        self.main_layout.addWidget(group)

    # ==================================================
    # RISK
    # ==================================================

    def create_risk_group(self):

        group = QGroupBox(

            "Risk Management"

        )

        layout = QFormLayout(group)

        self.capital = QDoubleSpinBox()

        self.capital.setMaximum(

            100000000

        )

        self.capital.setDecimals(

            2

        )

        self.capital.setSingleStep(

            10000

        )

        self.risk = QDoubleSpinBox()

        self.risk.setRange(

            0.25,

            10,

        )

        self.risk.setDecimals(

            2

        )

        self.risk.setSuffix("%")

        self.notifications = QCheckBox(

            "Enable Notifications"

        )

        layout.addRow(

            "Capital",

            self.capital,

        )

        layout.addRow(

            "Risk / Trade",

            self.risk,

        )

        layout.addRow(

            "",

            self.notifications,

        )

        self.main_layout.addWidget(group)

    # ==================================================
    # BUTTONS
    # ==================================================

    def create_buttons(self):

        layout = QHBoxLayout()

        self.save_button = QPushButton(

            "Save"

        )

        self.reset_button = QPushButton(

            "Reset"

        )

        self.reload_button = QPushButton(

            "Reload"

        )

        layout.addStretch()

        layout.addWidget(

            self.reload_button

        )

        layout.addWidget(

            self.reset_button

        )

        layout.addWidget(

            self.save_button

        )

        self.main_layout.addLayout(layout)

        self.save_button.clicked.connect(

            self.save_settings

        )

        self.reset_button.clicked.connect(

            self.reset_settings

        )

        self.reload_button.clicked.connect(

            self.load_settings

        )
            # ==================================================
    # LOAD SETTINGS
    # ==================================================

    def load_settings(self):

        try:

            settings = {
                "theme": self.config.get("theme", "dark"),
                "accent": self.config.get("accent", "#3daee9"),
                "auto_refresh": self.config.get("auto_refresh", 60),
                "scanner_strategy": self.config.get("scanner_strategy", "Swing"),
                "minimum_ai_score": self.config.get("minimum_ai_score", 70),
                "max_workers": self.config.get("max_workers", 4),
                "capital": self.config.get("capital", 100000),
                "risk_percent": self.config.get("risk_percent", 1.0),
                "notifications": self.config.get("notifications", True),
            }

            theme = settings.get(

                "theme",

                "dark",

            ).lower()

            index = self.theme_combo.findText(

                theme.capitalize(),

                Qt.MatchFixedString,

            )

            if index >= 0:

                self.theme_combo.setCurrentIndex(

                    index

                )

            self.accent_edit.setText(

                settings.get(

                    "accent",

                    "#3daee9",

                )

            )

            self.auto_refresh.setValue(

                int(

                    settings.get(

                        "auto_refresh",

                        60,

                    )

                )

            )

            strategy = settings.get(

                "scanner_strategy",

                "Swing",

            )

            index = self.strategy_combo.findText(

                strategy,

                Qt.MatchFixedString,

            )

            if index >= 0:

                self.strategy_combo.setCurrentIndex(

                    index

                )

            self.ai_score.setValue(

                int(

                    settings.get(

                        "minimum_ai_score",

                        70,

                    )

                )

            )

            self.worker_spin.setValue(

                int(

                    settings.get(

                        "max_workers",

                        4,

                    )

                )

            )

            self.capital.setValue(

                float(

                    settings.get(

                        "capital",

                        100000,

                    )

                )

            )

            self.risk.setValue(

                float(

                    settings.get(

                        "risk_percent",

                        1.0,

                    )

                )

            )

            self.notifications.setChecked(

                bool(

                    settings.get(

                        "notifications",

                        True,

                    )

                )

            )

        except Exception as e:

            QMessageBox.critical(

                self,

                "Error",

                str(e),

            )

    # ==================================================
    # SAVE SETTINGS
    # ==================================================

    def save_settings(self):

        settings = {

            "theme":

                self.theme_combo.currentText().lower(),

            "accent":

                self.accent_edit.text().strip(),

            "auto_refresh":

                self.auto_refresh.value(),

            "scanner_strategy":

                self.strategy_combo.currentText(),

            "minimum_ai_score":

                self.ai_score.value(),

            "max_workers":

                self.worker_spin.value(),

            "capital":

                self.capital.value(),

            "risk_percent":

                self.risk.value(),

            "notifications":

                self.notifications.isChecked(),

        }

        if not self.validate_settings(settings):

            return

        try:

            for key, value in settings.items():

                self.config.set(key, value)

            self.config.save()

            QMessageBox.information(

                self,

                "Success",

                "Settings saved successfully.",

            )

        except Exception as e:

            QMessageBox.critical(

                self,

                "Error",

                str(e),

            )

    # ==================================================
    # VALIDATION
    # ==================================================

    def validate_settings(

        self,

        settings,

    ):

        if not settings["accent"].startswith("#"):

            QMessageBox.warning(

                self,

                "Validation",

                "Accent color must start with #",

            )

            return False

        if settings["capital"] <= 0:

            QMessageBox.warning(

                self,

                "Validation",

                "Capital must be greater than zero.",

            )

            return False

        if settings["risk_percent"] <= 0:

            QMessageBox.warning(

                self,

                "Validation",

                "Risk must be greater than zero.",

            )

            return False

        return True

    # ==================================================
    # RESET SETTINGS
    # ==================================================

    def reset_settings(self):

        reply = QMessageBox.question(

            self,

            "Reset Settings",

            "Reset all settings to default?",

            QMessageBox.Yes

            | QMessageBox.No,

        )

        if reply != QMessageBox.Yes:

            return

        self.controller.reset_settings()

        self.load_settings()

        QMessageBox.information(

            self,

            "Settings",

            "Default settings restored.",

        )

    # ==================================================
    # COLOR PICKER
    # ==================================================

    def choose_color(self):

        color = QColorDialog.getColor(

            parent=self

        )

        if color.isValid():

            self.accent_edit.setText(

                color.name()

            )

    # ==================================================
    # LIVE THEME CHANGE
    # ==================================================

    def theme_changed(self):

        self.controller.set_theme(

            self.theme_combo.currentText().lower()

        )

    # ==================================================
    # LIVE ACCENT CHANGE
    # ==================================================

    def accent_changed(self):

        self.controller.set_accent(

            self.accent_edit.text()

        )
            # ==================================================
    # SCANNER SETTINGS
    # ==================================================

    def scanner_settings(self):

        return {

            "strategy": self.strategy_combo.currentText(),

            "minimum_ai_score": self.ai_score.value(),

            "max_workers": self.worker_spin.value(),

            "auto_refresh": self.auto_refresh.value(),

        }

    # ==================================================
    # RISK SETTINGS
    # ==================================================

    def risk_settings(self):

        return {

            "capital": self.capital.value(),

            "risk_percent": self.risk.value(),

        }

    # ==================================================
    # GENERAL SETTINGS
    # ==================================================

    def general_settings(self):

        return {

            "theme": self.theme_combo.currentText().lower(),

            "accent": self.accent_edit.text().strip(),

            "notifications": self.notifications.isChecked(),

        }

    # ==================================================
    # COMPLETE SETTINGS
    # ==================================================

    def current_settings(self):

        settings = {}

        settings.update(

            self.general_settings()

        )

        settings.update(

            self.scanner_settings()

        )

        settings.update(

            self.risk_settings()

        )

        return settings

    # ==================================================
    # APPLY SETTINGS LIVE
    # ==================================================

    def apply_live_settings(self):

        settings = self.current_settings()

        try:

            self.controller.apply_settings(

                settings

            )

        except AttributeError:

            # Older controller versions may not
            # expose apply_settings().
            pass

    # ==================================================
    # UPDATE CONTROLLER
    # ==================================================

    def update_controller(self):

        try:

            self.controller.update_runtime_settings(

                self.current_settings()

            )

        except AttributeError:

            pass

    # ==================================================
    # AI SCORE CHANGED
    # ==================================================

    def ai_score_changed(self, value):

        try:

            self.controller.set_minimum_ai_score(

                value

            )

        except AttributeError:

            pass

    # ==================================================
    # THREAD COUNT CHANGED
    # ==================================================

    def workers_changed(self, value):

        try:

            self.controller.set_max_workers(

                value

            )

        except AttributeError:

            pass

    # ==================================================
    # AUTO REFRESH CHANGED
    # ==================================================

    def refresh_interval_changed(

        self,

        value,

    ):

        try:

            self.controller.set_refresh_interval(

                value

            )

        except AttributeError:

            pass

    # ==================================================
    # STRATEGY CHANGED
    # ==================================================

    def strategy_changed(self):

        try:

            self.controller.set_default_strategy(

                self.strategy_combo.currentText()

            )

        except AttributeError:

            pass

    # ==================================================
    # CAPITAL CHANGED
    # ==================================================

    def capital_changed(self, value):

        try:

            self.controller.set_capital(

                value

            )

        except AttributeError:

            pass

    # ==================================================
    # RISK CHANGED
    # ==================================================

    def risk_changed(self, value):

        try:

            self.controller.set_risk_percent(

                value

            )

        except AttributeError:

            pass

    # ==================================================
    # NOTIFICATION CHANGED
    # ==================================================

    def notifications_changed(self):

        try:

            self.controller.set_notifications(

                self.notifications.isChecked()

            )

        except AttributeError:

            pass

    # ==================================================
    # CONNECT SIGNALS
    # ==================================================

    def connect_signals(self):

        self.theme_combo.currentIndexChanged.connect(

            self.theme_changed

        )

        self.accent_edit.editingFinished.connect(

            self.accent_changed

        )

        self.strategy_combo.currentIndexChanged.connect(

            self.strategy_changed

        )

        self.ai_score.valueChanged.connect(

            self.ai_score_changed

        )

        self.worker_spin.valueChanged.connect(

            self.workers_changed

        )

        self.auto_refresh.valueChanged.connect(

            self.refresh_interval_changed

        )

        self.capital.valueChanged.connect(

            self.capital_changed

        )

        self.risk.valueChanged.connect(

            self.risk_changed

        )

        self.notifications.stateChanged.connect(

            self.notifications_changed

        )

    # ==================================================
    # INITIALIZE SIGNALS
    # ==================================================

    def initialize(self):

        self.connect_signals()

        self.apply_live_settings()
            # ==================================================
    # APPEARANCE GROUP
    # ==================================================

    def create_appearance_group(self):

        group = QGroupBox("Appearance")

        layout = QFormLayout(group)

        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)

        self.row_height = QSpinBox()
        self.row_height.setRange(18, 60)

        self.table_density = QComboBox()
        self.table_density.addItems(
            [
                "Compact",
                "Normal",
                "Comfortable",
            ]
        )

        layout.addRow(
            "Font Size",
            self.font_size,
        )

        layout.addRow(
            "Row Height",
            self.row_height,
        )

        layout.addRow(
            "Table Density",
            self.table_density,
        )

        self.main_layout.addWidget(group)

    # ==================================================
    # MARKET GROUP
    # ==================================================

    def create_market_group(self):

        group = QGroupBox("Market Preferences")

        layout = QFormLayout(group)

        self.exchange = QComboBox()

        self.exchange.addItems(
            [
                "NSE",
                "BSE",
            ]
        )

        self.market_timezone = QComboBox()

        self.market_timezone.addItems(
            [
                "Asia/Kolkata",
            ]
        )

        self.market_open = QLineEdit("09:15")

        self.market_close = QLineEdit("15:30")

        layout.addRow(
            "Exchange",
            self.exchange,
        )

        layout.addRow(
            "Timezone",
            self.market_timezone,
        )

        layout.addRow(
            "Market Open",
            self.market_open,
        )

        layout.addRow(
            "Market Close",
            self.market_close,
        )

        self.main_layout.addWidget(group)

    # ==================================================
    # STARTUP GROUP
    # ==================================================

    def create_startup_group(self):

        group = QGroupBox("Startup")

        layout = QFormLayout(group)

        self.auto_scan = QCheckBox(
            "Run Scanner on Startup"
        )

        self.restore_session = QCheckBox(
            "Restore Previous Session"
        )

        self.load_watchlist = QCheckBox(
            "Load Watchlist Automatically"
        )

        self.default_watchlist = QLineEdit()

        layout.addRow(
            "",
            self.auto_scan,
        )

        layout.addRow(
            "",
            self.restore_session,
        )

        layout.addRow(
            "",
            self.load_watchlist,
        )

        layout.addRow(
            "Default Watchlist",
            self.default_watchlist,
        )

        self.main_layout.addWidget(group)

    # ==================================================
    # LOAD APPEARANCE
    # ==================================================

    def load_appearance_settings(
        self,
        settings,
    ):

        self.font_size.setValue(
            int(
                settings.get(
                    "font_size",
                    11,
                )
            )
        )

        self.row_height.setValue(
            int(
                settings.get(
                    "row_height",
                    28,
                )
            )
        )

        density = settings.get(
            "table_density",
            "Normal",
        )

        index = self.table_density.findText(
            density,
            Qt.MatchFixedString,
        )

        if index >= 0:

            self.table_density.setCurrentIndex(
                index
            )

    # ==================================================
    # LOAD MARKET SETTINGS
    # ==================================================

    def load_market_settings(
        self,
        settings,
    ):

        exchange = settings.get(
            "exchange",
            "NSE",
        )

        index = self.exchange.findText(
            exchange,
            Qt.MatchFixedString,
        )

        if index >= 0:

            self.exchange.setCurrentIndex(
                index
            )

        self.market_open.setText(
            settings.get(
                "market_open",
                "09:15",
            )
        )

        self.market_close.setText(
            settings.get(
                "market_close",
                "15:30",
            )
        )

    # ==================================================
    # LOAD STARTUP SETTINGS
    # ==================================================

    def load_startup_settings(
        self,
        settings,
    ):

        self.auto_scan.setChecked(
            settings.get(
                "auto_scan",
                False,
            )
        )

        self.restore_session.setChecked(
            settings.get(
                "restore_session",
                True,
            )
        )

        self.load_watchlist.setChecked(
            settings.get(
                "load_watchlist",
                True,
            )
        )

        self.default_watchlist.setText(
            settings.get(
                "default_watchlist",
                "",
            )
        )

    # ==================================================
    # APPEARANCE SETTINGS
    # ==================================================

    def appearance_settings(self):

        return {

            "font_size":
                self.font_size.value(),

            "row_height":
                self.row_height.value(),

            "table_density":
                self.table_density.currentText(),

        }

    # ==================================================
    # MARKET SETTINGS
    # ==================================================

    def market_settings(self):

        return {

            "exchange":
                self.exchange.currentText(),

            "timezone":
                self.market_timezone.currentText(),

            "market_open":
                self.market_open.text(),

            "market_close":
                self.market_close.text(),

        }

    # ==================================================
    # STARTUP SETTINGS
    # ==================================================

    def startup_settings(self):

        return {

            "auto_scan":
                self.auto_scan.isChecked(),

            "restore_session":
                self.restore_session.isChecked(),

            "load_watchlist":
                self.load_watchlist.isChecked(),

            "default_watchlist":
                self.default_watchlist.text().strip(),

        }
        # ==================================================
    # ALERT SETTINGS GROUP
    # ==================================================

    def create_alert_group(self):

        group = QGroupBox("Alerts & Notifications")

        layout = QFormLayout(group)

        self.enable_alerts = QCheckBox(
            "Enable Price Alerts"
        )

        self.enable_sound = QCheckBox(
            "Play Alert Sound"
        )

        self.enable_popup = QCheckBox(
            "Desktop Popup Notification"
        )

        self.enable_email = QCheckBox(
            "Email Notifications"
        )

        self.enable_telegram = QCheckBox(
            "Telegram Notifications"
        )

        self.email_address = QLineEdit()

        self.telegram_token = QLineEdit()

        self.telegram_chat = QLineEdit()

        self.webhook_url = QLineEdit()

        layout.addRow("", self.enable_alerts)
        layout.addRow("", self.enable_sound)
        layout.addRow("", self.enable_popup)
        layout.addRow("", self.enable_email)
        layout.addRow("", self.enable_telegram)

        layout.addRow(
            "Email",
            self.email_address,
        )

        layout.addRow(
            "Telegram Bot Token",
            self.telegram_token,
        )

        layout.addRow(
            "Telegram Chat ID",
            self.telegram_chat,
        )

        layout.addRow(
            "Webhook URL",
            self.webhook_url,
        )

        self.main_layout.addWidget(group)

    # ==================================================
    # LOGGING GROUP
    # ==================================================

    def create_logging_group(self):

        group = QGroupBox("Logging")

        layout = QFormLayout(group)

        self.log_level = QComboBox()

        self.log_level.addItems(

            [

                "DEBUG",

                "INFO",

                "WARNING",

                "ERROR",

                "CRITICAL",

            ]

        )

        self.save_logs = QCheckBox(
            "Save Log File"
        )

        self.max_log_days = QSpinBox()

        self.max_log_days.setRange(

            1,

            365,

        )

        layout.addRow(

            "Log Level",

            self.log_level,

        )

        layout.addRow(

            "",

            self.save_logs,

        )

        layout.addRow(

            "Keep Logs",

            self.max_log_days,

        )

        self.main_layout.addWidget(group)

    # ==================================================
    # BACKUP GROUP
    # ==================================================

    def create_backup_group(self):

        group = QGroupBox("Backup")

        layout = QFormLayout(group)

        self.auto_backup = QCheckBox(
            "Enable Automatic Backup"
        )

        self.backup_interval = QComboBox()

        self.backup_interval.addItems(

            [

                "Daily",

                "Weekly",

                "Monthly",

            ]

        )

        self.backup_path = QLineEdit()

        layout.addRow(

            "",

            self.auto_backup,

        )

        layout.addRow(

            "Backup Frequency",

            self.backup_interval,

        )

        layout.addRow(

            "Backup Folder",

            self.backup_path,

        )

        self.main_layout.addWidget(group)

    # ==================================================
    # ALERT SETTINGS
    # ==================================================

    def alert_settings(self):

        return {

            "enable_alerts":
                self.enable_alerts.isChecked(),

            "enable_sound":
                self.enable_sound.isChecked(),

            "enable_popup":
                self.enable_popup.isChecked(),

            "enable_email":
                self.enable_email.isChecked(),

            "enable_telegram":
                self.enable_telegram.isChecked(),

            "email":
                self.email_address.text().strip(),

            "telegram_token":
                self.telegram_token.text().strip(),

            "telegram_chat":
                self.telegram_chat.text().strip(),

            "webhook":
                self.webhook_url.text().strip(),

        }

    # ==================================================
    # LOG SETTINGS
    # ==================================================

    def logging_settings(self):

        return {

            "log_level":
                self.log_level.currentText(),

            "save_logs":
                self.save_logs.isChecked(),

            "log_retention_days":
                self.max_log_days.value(),

        }

    # ==================================================
    # BACKUP SETTINGS
    # ==================================================

    def backup_settings(self):

        return {

            "auto_backup":
                self.auto_backup.isChecked(),

            "backup_frequency":
                self.backup_interval.currentText(),

            "backup_path":
                self.backup_path.text().strip(),

        }

    # ==================================================
    # LOAD ALERT SETTINGS
    # ==================================================

    def load_alert_settings(self, settings):

        self.enable_alerts.setChecked(
            settings.get("enable_alerts", True)
        )

        self.enable_sound.setChecked(
            settings.get("enable_sound", True)
        )

        self.enable_popup.setChecked(
            settings.get("enable_popup", True)
        )

        self.enable_email.setChecked(
            settings.get("enable_email", False)
        )

        self.enable_telegram.setChecked(
            settings.get("enable_telegram", False)
        )

        self.email_address.setText(
            settings.get("email", "")
        )

        self.telegram_token.setText(
            settings.get("telegram_token", "")
        )

        self.telegram_chat.setText(
            settings.get("telegram_chat", "")
        )

        self.webhook_url.setText(
            settings.get("webhook", "")
        )

    # ==================================================
    # LOAD LOGGING SETTINGS
    # ==================================================

    def load_logging_settings(self, settings):

        level = settings.get(
            "log_level",
            "INFO",
        )

        index = self.log_level.findText(level)

        if index >= 0:

            self.log_level.setCurrentIndex(index)

        self.save_logs.setChecked(
            settings.get(
                "save_logs",
                True,
            )
        )

        self.max_log_days.setValue(
            settings.get(
                "log_retention_days",
                30,
            )
        )

    # ==================================================
    # LOAD BACKUP SETTINGS
    # ==================================================

    def load_backup_settings(self, settings):

        self.auto_backup.setChecked(
            settings.get(
                "auto_backup",
                False,
            )
        )

        freq = settings.get(
            "backup_frequency",
            "Weekly",
        )

        index = self.backup_interval.findText(freq)

        if index >= 0:

            self.backup_interval.setCurrentIndex(index)

        self.backup_path.setText(
            settings.get(
                "backup_path",
                "",
            )
        )
    # ==================================================
    # MARK DIRTY
    # ==================================================

    def mark_dirty(self):

        self._settings_changed = True

        try:

            self.save_button.setEnabled(True)

        except Exception:

            pass

    # ==================================================
    # CLEAR DIRTY
    # ==================================================

    def clear_dirty(self):

        self._settings_changed = False

    # ==================================================
    # HAS UNSAVED CHANGES
    # ==================================================

    def has_unsaved_changes(self):

        return getattr(

            self,

            "_settings_changed",

            False,

        )

    # ==================================================
    # APPLY
    # ==================================================

    def apply_changes(self):

        if not self.validate_settings(

            self.current_settings()

        ):

            return

        try:

            self.controller.save_settings(

                self.current_settings()

            )

        except Exception:

            pass

        self.apply_live_settings()

        self.update_controller()

        self.clear_dirty()

        QMessageBox.information(

            self,

            "Settings",

            "Changes applied successfully.",

        )

    # ==================================================
    # CANCEL
    # ==================================================

    def cancel_changes(self):

        if self.has_unsaved_changes():

            reply = QMessageBox.question(

                self,

                "Discard Changes",

                "Discard unsaved changes?",

                QMessageBox.Yes

                | QMessageBox.No,

            )

            if reply != QMessageBox.Yes:

                return

        self.load_settings()

        self.clear_dirty()

    # ==================================================
    # REFRESH UI
    # ==================================================

    def refresh_ui(self):

        try:

            self.load_settings()

        except Exception:

            pass

    # ==================================================
    # RELOAD
    # ==================================================

    def reload(self):

        self.refresh_ui()

    # ==================================================
    # ENABLE EDITING
    # ==================================================

    def enable_editing(

        self,

        enabled=True,

    ):

        widgets = [

            self.theme_combo,

            self.accent_edit,

            self.auto_refresh,

            self.strategy_combo,

            self.ai_score,

            self.worker_spin,

            self.capital,

            self.risk,

            self.notifications,

        ]

        for widget in widgets:

            try:

                widget.setEnabled(

                    enabled

                )

            except Exception:

                pass

    # ==================================================
    # CONNECT DIRTY SIGNALS
    # ==================================================

    def connect_dirty_signals(self):

        self.theme_combo.currentIndexChanged.connect(

            self.mark_dirty

        )

        self.strategy_combo.currentIndexChanged.connect(

            self.mark_dirty

        )

        self.auto_refresh.valueChanged.connect(

            self.mark_dirty

        )

        self.ai_score.valueChanged.connect(

            self.mark_dirty

        )

        self.worker_spin.valueChanged.connect(

            self.mark_dirty

        )

        self.capital.valueChanged.connect(

            self.mark_dirty

        )

        self.risk.valueChanged.connect(

            self.mark_dirty

        )

        self.notifications.stateChanged.connect(

            self.mark_dirty

        )

        self.accent_edit.textChanged.connect(

            self.mark_dirty

        )

    # ==================================================
    # SHORTCUTS
    # ==================================================

    def setup_shortcuts(self):

        from PySide6.QtGui import QShortcut

        from PySide6.QtGui import QKeySequence

        QShortcut(

            QKeySequence("Ctrl+S"),

            self,

            activated=self.apply_changes,

        )

        QShortcut(

            QKeySequence("Ctrl+R"),

            self,

            activated=self.reload,

        )

        QShortcut(

            QKeySequence("Esc"),

            self,

            activated=self.cancel_changes,

        )

    # ==================================================
    # CLOSE EVENT
    # ==================================================

    def closeEvent(

        self,

        event,

    ):

        if not self.has_unsaved_changes():

            event.accept()

            return

        reply = QMessageBox.question(

            self,

            "Unsaved Changes",

            "Save changes before closing?",

            QMessageBox.Yes

            | QMessageBox.No

            | QMessageBox.Cancel,

        )

        if reply == QMessageBox.Yes:

            self.apply_changes()

            event.accept()

            return

        if reply == QMessageBox.No:

            event.accept()

            return

        event.ignore()

    # ==================================================
    # INITIALIZE PAGE
    # ==================================================

    def initialize_page(self):

        self.connect_signals()

        self.connect_dirty_signals()

        self.setup_shortcuts()

        self.clear_dirty()

    # ==================================================
    # PAGE ACTIVATED
    # ==================================================

    def on_page_activated(self):

        self.refresh_ui()

    # ==================================================
    # PAGE DEACTIVATED
    # ==================================================

    def on_page_deactivated(self):

        pass
    # ==================================================
    # SETTINGS SUMMARY
    # ==================================================

    def settings_summary(self):

        return {

            "general": self.general_settings(),

            "scanner": self.scanner_settings(),

            "risk": self.risk_settings(),

            "appearance": self.appearance_settings(),

            "market": self.market_settings(),

            "startup": self.startup_settings(),

            "alerts": self.alert_settings(),

            "logging": self.logging_settings(),

            "backup": self.backup_settings(),

        }

    # ==================================================
    # SYNCHRONIZE RUNTIME
    # ==================================================

    def synchronize_runtime(self):

        settings = self.settings_summary()

        try:

            self.controller.apply_settings(

                settings

            )

        except AttributeError:

            pass

        try:

            self.controller.refresh_runtime()

        except AttributeError:

            pass

    # ==================================================
    # RESET UI STATE
    # ==================================================

    def reset_ui_state(self):

        self.clear_dirty()

        self.enable_editing(True)

    # ==================================================
    # RELOAD EVERYTHING
    # ==================================================

    def reload_all(self):

        self.load_settings()

        self.reset_ui_state()

        self.synchronize_runtime()

    # ==================================================
    # SAVE & APPLY
    # ==================================================

    def save_and_apply(self):

        if not self.validate_settings(

            self.current_settings()

        ):

            return False

        try:

            self.controller.save_settings(

                self.current_settings()

            )

            self.synchronize_runtime()

            self.clear_dirty()

            return True

        except Exception as e:

            QMessageBox.critical(

                self,

                "Save Failed",

                str(e),

            )

            return False

    # ==================================================
    # EXPORT SUMMARY
    # ==================================================

    def export_summary(self):

        import json

        return json.dumps(

            self.settings_summary(),

            indent=4,

        )

    # ==================================================
    # IMPORT SUMMARY
    # ==================================================

    def import_summary(

        self,

        summary,

    ):

        try:

            import json

            settings = json.loads(

                summary

            )

            for key, value in settings.items():

                self.config.set(key, value)

            self.config.save()

            self.load_settings()

            return True

        except Exception:

            return False

    # ==================================================
    # CONTROLLER AVAILABLE
    # ==================================================

    def controller_available(self):

        return self.controller is not None

    # ==================================================
    # PAGE READY
    # ==================================================

    def is_ready(self):

        return (

            self.controller_available()

            and

            self.isVisible()

        )

    # ==================================================
    # INITIALIZATION COMPLETE
    # ==================================================

    def finalize(self):

        self.initialize_page()

        self.load_settings()

        self.reset_ui_state()

    # ==================================================
    # STRING REPRESENTATION
    # ==================================================

    def __repr__(self):

        return (

            "<SettingsPage "

            f"theme={self.theme_combo.currentText()} "

            f"strategy={self.strategy_combo.currentText()} "

            f"capital={self.capital.value():,.2f}>"

        )


# ==================================================
# END OF FILE
# ==================================================



