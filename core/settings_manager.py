from __future__ import annotations

import json
import threading

from copy import deepcopy
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional

from backend.core.config import (
    SETTINGS_DIR,
    DEFAULT_THEME,
    DEFAULT_EXCHANGE,
    DEFAULT_TIMEFRAME,
    REFRESH_INTERVAL,
    DEFAULT_SCAN_LIMIT,
    DEFAULT_TOP_RESULTS,
    DEFAULT_CAPITAL,
    DEFAULT_POSITION_RISK,
    DEFAULT_RR,
    ENABLE_AI,
    ENABLE_CACHE,
)

# =====================================================
# SETTINGS FILE
# =====================================================

SETTINGS_FILE = (

    SETTINGS_DIR

    / "settings.json"

)

# =====================================================
# DEFAULT SETTINGS
# =====================================================

DEFAULT_SETTINGS = {

    "application": {

        "theme": DEFAULT_THEME,

        "language": "en",

        "auto_refresh": True,

        "refresh_interval": REFRESH_INTERVAL,

        "remember_window": True,

        "check_updates": True,

    },

    "scanner": {

        "exchange": DEFAULT_EXCHANGE,

        "timeframe": DEFAULT_TIMEFRAME,

        "scan_limit": DEFAULT_SCAN_LIMIT,

        "top_results": DEFAULT_TOP_RESULTS,

        "auto_scan": False,

        "sound_alert": True,

    },

    "ai": {

        "enabled": ENABLE_AI,

        "confidence_threshold": 75,

        "minimum_score": 80,

    },

    "risk": {

        "capital": DEFAULT_CAPITAL,

        "risk_percent": DEFAULT_POSITION_RISK,

        "reward_ratio": DEFAULT_RR,

    },

    "cache": {

        "enabled": ENABLE_CACHE,

        "clear_on_exit": False,

    },

    "market": {

        "watch_nifty": True,

        "watch_banknifty": True,

        "watch_finnifty": True,

        "market_alerts": True,

    },

    "window": {

        "width": 1600,

        "height": 900,

        "maximized": False,

        "x": 100,

        "y": 100,

    },

    "layout": {

        "sidebar_expanded": True,

        "selected_page": "Dashboard",

    },

}


# =====================================================
# SETTINGS MANAGER
# =====================================================

class SettingsManager:

    _instance = None

    _lock = threading.Lock()

    # -------------------------------------------------

    def __new__(

        cls,

    ):

        with cls._lock:

            if cls._instance is None:

                cls._instance = super().__new__(

                    cls

                )

        return cls._instance

    # -------------------------------------------------

    def __init__(

        self,

    ):

        if getattr(

            self,

            "_initialized",

            False,

        ):

            return

        self._initialized = True

        self.file = SETTINGS_FILE

        self.data = deepcopy(

            DEFAULT_SETTINGS

        )

        self.file_lock = threading.RLock()

        self.last_saved: Optional[datetime] = None

        self.load()

    # =====================================================
    # LOAD
    # =====================================================

    def load(

        self,

    ):

        if not self.file.exists():

            self.save()

            return

        try:

            with self.file.open(

                "r",

                encoding="utf-8",

            ) as fp:

                loaded = json.load(

                    fp

                )

            self._merge(

                self.data,

                loaded,

            )

        except Exception:

            self.data = deepcopy(

                DEFAULT_SETTINGS

            )

            self.save()
                # =====================================================
    # SAVE
    # =====================================================

    def save(

        self,

    ):

        with self.file_lock:

            self.file.parent.mkdir(

                parents=True,

                exist_ok=True,

            )

            with self.file.open(

                "w",

                encoding="utf-8",

            ) as fp:

                json.dump(

                    self.data,

                    fp,

                    indent=4,

                    ensure_ascii=False,

                    sort_keys=True,

                )

            self.last_saved = datetime.now()

    # =====================================================
    # MERGE
    # =====================================================

    def _merge(

        self,

        destination: Dict[str, Any],

        source: Dict[str, Any],

    ):

        for key, value in source.items():

            if (

                isinstance(value, dict)

                and isinstance(

                    destination.get(key),

                    dict,

                )

            ):

                self._merge(

                    destination[key],

                    value,

                )

            else:

                destination[key] = value

    # =====================================================
    # GET
    # =====================================================

    def get(

        self,

        key: str,

        default: Any = None,

    ):

        current = self.data

        for part in key.split("."):

            if not isinstance(

                current,

                dict,

            ):

                return default

            if part not in current:

                return default

            current = current[part]

        return current

    # =====================================================
    # SET
    # =====================================================

    def set(

        self,

        key: str,

        value: Any,

        autosave: bool = True,

    ):

        parts = key.split(".")

        current = self.data

        for part in parts[:-1]:

            current = current.setdefault(

                part,

                {},

            )

        current[parts[-1]] = value

        if autosave:

            self.save()

        return value

    # =====================================================
    # EXISTS
    # =====================================================

    def exists(

        self,

        key: str,

    ):

        return self.get(

            key,

            None,

        ) is not None

    # =====================================================
    # DELETE
    # =====================================================

    def delete(

        self,

        key: str,

        autosave: bool = True,

    ):

        parts = key.split(".")

        current = self.data

        for part in parts[:-1]:

            if part not in current:

                return False

            current = current[part]

        removed = current.pop(

            parts[-1],

            None,

        )

        if removed is not None and autosave:

            self.save()

        return removed is not None

    # =====================================================
    # RESET
    # =====================================================

    def reset(

        self,

        autosave: bool = True,

    ):

        self.data = deepcopy(

            DEFAULT_SETTINGS

        )

        if autosave:

            self.save()

        return self.data

    # =====================================================
    # RESET SECTION
    # =====================================================

    def reset_section(

        self,

        section: str,

        autosave: bool = True,

    ):

        if section not in DEFAULT_SETTINGS:

            return False

        self.data[section] = deepcopy(

            DEFAULT_SETTINGS[section]

        )

        if autosave:

            self.save()

        return True

    # =====================================================
    # UPDATE
    # =====================================================

    def update(

        self,

        values: Dict[str, Any],

        autosave: bool = True,

    ):

        self._merge(

            self.data,

            values,

        )

        if autosave:

            self.save()

        return self.data

    # =====================================================
    # RELOAD
    # =====================================================

    def reload(

        self,

    ):

        self.data = deepcopy(

            DEFAULT_SETTINGS

        )

        self.load()

        return self.data
        # =====================================================
    # APPLICATION
    # =====================================================

    @property
    def theme(self):

        return self.get(

            "application.theme",

            DEFAULT_THEME,

        )

    @theme.setter
    def theme(

        self,

        value: str,

    ):

        self.set(

            "application.theme",

            value,

        )

    # -------------------------------------------------

    @property
    def refresh_interval(self):

        return self.get(

            "application.refresh_interval",

            REFRESH_INTERVAL,

        )

    @refresh_interval.setter
    def refresh_interval(

        self,

        value: int,

    ):

        self.set(

            "application.refresh_interval",

            int(value),

        )

    # =====================================================
    # SCANNER
    # =====================================================

    @property
    def exchange(self):

        return self.get(

            "scanner.exchange",

            DEFAULT_EXCHANGE,

        )

    @exchange.setter
    def exchange(

        self,

        value: str,

    ):

        self.set(

            "scanner.exchange",

            value,

        )

    # -------------------------------------------------

    @property
    def timeframe(self):

        return self.get(

            "scanner.timeframe",

            DEFAULT_TIMEFRAME,

        )

    @timeframe.setter
    def timeframe(

        self,

        value: str,

    ):

        self.set(

            "scanner.timeframe",

            value,

        )

    # -------------------------------------------------

    @property
    def scan_limit(self):

        return self.get(

            "scanner.scan_limit",

            DEFAULT_SCAN_LIMIT,

        )

    @scan_limit.setter
    def scan_limit(

        self,

        value: int,

    ):

        self.set(

            "scanner.scan_limit",

            int(value),

        )

    # =====================================================
    # AI
    # =====================================================

    @property
    def ai_enabled(self):

        return self.get(

            "ai.enabled",

            True,

        )

    @ai_enabled.setter
    def ai_enabled(

        self,

        value: bool,

    ):

        self.set(

            "ai.enabled",

            bool(value),

        )

    # -------------------------------------------------

    @property
    def ai_score(self):

        return self.get(

            "ai.minimum_score",

            80,

        )

    @ai_score.setter
    def ai_score(

        self,

        value: int,

    ):

        self.set(

            "ai.minimum_score",

            int(value),

        )

    # =====================================================
    # RISK
    # =====================================================

    @property
    def capital(self):

        return self.get(

            "risk.capital",

            DEFAULT_CAPITAL,

        )

    @capital.setter
    def capital(

        self,

        value: float,

    ):

        self.set(

            "risk.capital",

            float(value),

        )

    # -------------------------------------------------

    @property
    def risk_percent(self):

        return self.get(

            "risk.risk_percent",

            DEFAULT_POSITION_RISK,

        )

    @risk_percent.setter
    def risk_percent(

        self,

        value: float,

    ):

        self.set(

            "risk.risk_percent",

            float(value),

        )

    # -------------------------------------------------

    @property
    def reward_ratio(self):

        return self.get(

            "risk.reward_ratio",

            DEFAULT_RR,

        )

    @reward_ratio.setter
    def reward_ratio(

        self,

        value: float,

    ):

        self.set(

            "risk.reward_ratio",

            float(value),

        )

    # =====================================================
    # WINDOW
    # =====================================================

    def save_window_state(

        self,

        width: int,

        height: int,

        x: int,

        y: int,

        maximized: bool,

    ):

        self.update(

            {

                "window": {

                    "width": width,

                    "height": height,

                    "x": x,

                    "y": y,

                    "maximized": maximized,

                }

            }

        )

    # -------------------------------------------------

    def window_state(

        self,

    ):

        return self.get(

            "window",

            {},

        )

    # =====================================================
    # LAYOUT
    # =====================================================

    def save_layout(

        self,

        selected_page: str,

        sidebar_expanded: bool,

    ):

        self.update(

            {

                "layout": {

                    "selected_page": selected_page,

                    "sidebar_expanded": sidebar_expanded,

                }

            }

        )

    # -------------------------------------------------

    def layout(

        self,

    ):

        return self.get(

            "layout",

            {},

        )

    # =====================================================
    # IMPORT / EXPORT
    # =====================================================

    def export_settings(

        self,

        filename: Path,

    ):

        with filename.open(

            "w",

            encoding="utf-8",

        ) as fp:

            json.dump(

                self.data,

                fp,

                indent=4,

                ensure_ascii=False,

            )

        return filename

    # -------------------------------------------------

    def import_settings(

        self,

        filename: Path,

    ):

        with filename.open(

            "r",

            encoding="utf-8",

        ) as fp:

            imported = json.load(

                fp

            )

        self.update(

            imported,

            autosave=True,

        )

        return True
        # =====================================================
    # VALIDATION
    # =====================================================

    def validate(self):

        """
        Validate important settings and
        restore defaults where necessary.
        """

        if self.theme not in ("dark", "light"):

            self.theme = DEFAULT_THEME

        if self.refresh_interval <= 0:

            self.refresh_interval = REFRESH_INTERVAL

        if self.scan_limit <= 0:

            self.scan_limit = DEFAULT_SCAN_LIMIT

        if self.capital <= 0:

            self.capital = DEFAULT_CAPITAL

        if self.risk_percent <= 0:

            self.risk_percent = DEFAULT_POSITION_RISK

        if self.reward_ratio <= 0:

            self.reward_ratio = DEFAULT_RR

        return True

    # =====================================================
    # BACKUP
    # =====================================================

    def backup(

        self,

        filename: Optional[Path] = None,

    ):

        if filename is None:

            filename = (

                SETTINGS_DIR

                / f"settings_backup_{datetime.now():%Y%m%d_%H%M%S}.json"

            )

        self.export_settings(

            filename

        )

        return filename

    # =====================================================
    # RESTORE
    # =====================================================

    def restore(

        self,

        filename: Path,

    ):

        self.import_settings(

            filename

        )

        self.validate()

        self.save()

        return True

    # =====================================================
    # FILE INFORMATION
    # =====================================================

    def file_exists(

        self,

    ):

        return self.file.exists()

    # -------------------------------------------------

    def file_size(

        self,

    ):

        if not self.file.exists():

            return 0

        return self.file.stat().st_size

    # -------------------------------------------------

    def modified_time(

        self,

    ):

        if not self.file.exists():

            return None

        return datetime.fromtimestamp(

            self.file.stat().st_mtime

        )

    # =====================================================
    # SERIALIZATION
    # =====================================================

    def to_dict(

        self,

    ):

        return deepcopy(

            self.data

        )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ):

        return (

            "SettingsManager("

            f"theme='{self.theme}', "

            f"exchange='{self.exchange}', "

            f"timeframe='{self.timeframe}')"

        )

    # -------------------------------------------------

    def __str__(

        self,

    ):

        return (

            "Settings Manager\n"

            f"Theme        : {self.theme}\n"

            f"Exchange     : {self.exchange}\n"

            f"Timeframe    : {self.timeframe}\n"

            f"Capital      : {self.capital}\n"

            f"Risk %       : {self.risk_percent}\n"

            f"Reward Ratio : {self.reward_ratio}"

        )


# =====================================================
# GLOBAL SINGLETON
# =====================================================

settings = SettingsManager()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "DEFAULT_SETTINGS",

    "SETTINGS_FILE",

    "SettingsManager",

    "settings",

]