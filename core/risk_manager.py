from __future__ import annotations

import json
import threading
import uuid

from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# =====================================================
# RISK PROFILE
# =====================================================

@dataclass(slots=True)
class RiskProfile:

    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    name: str = "Default"

    capital: float = 100000.0

    risk_per_trade: float = 1.0

    max_open_positions: int = 5

    max_daily_loss: float = 3.0

    max_position_size: float = 20.0

    reward_ratio: float = 2.0

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# =====================================================
# RISK MANAGER
# =====================================================

class RiskManager:

    _instance = None

    _lock = threading.Lock()

    def __new__(cls):

        with cls._lock:

            if cls._instance is None:

                cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):

        if getattr(
            self,
            "_initialized",
            False,
        ):
            return

        self._initialized = True

        self.manager_lock = threading.RLock()

        self.storage_directory = (
            Path.home()
            / ".stockversity"
        )

        self.storage_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.storage_file = (
            self.storage_directory
            / "risk_profiles.json"
        )

        self.profiles: Dict[
            str,
            RiskProfile,
        ] = {}

        self.default_profile: Optional[
            RiskProfile
        ] = None

        self.load()

        if self.default_profile is None:

            self.default_profile = self.create_profile(
                "Default"
            )

    # =====================================================
    # CREATE PROFILE
    # =====================================================

    def create_profile(

        self,

        name: str,

    ) -> RiskProfile:

        profile = RiskProfile(

            name=name,

        )

        self.profiles[
            profile.id
        ] = profile

        if self.default_profile is None:

            self.default_profile = profile

        self.save()

        return profile

    # =====================================================
    # GET PROFILE
    # =====================================================

    def get(

        self,

        profile_id: str,

    ) -> Optional[RiskProfile]:

        return self.profiles.get(
            profile_id
        )

    # =====================================================
    # DEFAULT PROFILE
    # =====================================================

    def default(self) -> Optional[RiskProfile]:

        return self.default_profile

    # =====================================================
    # ALL PROFILES
    # =====================================================

    def all_profiles(self) -> List[RiskProfile]:

        return list(
            self.profiles.values()
        )
        # =====================================================
    # SET CAPITAL
    # =====================================================

    def set_capital(

        self,

        profile_id: str,

        capital: float,

    ) -> bool:

        profile = self.profiles.get(

            profile_id

        )

        if profile is None:

            return False

        profile.capital = max(

            1000.0,

            float(capital),

        )

        profile.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # SET RISK PER TRADE
    # =====================================================

    def set_risk_per_trade(

        self,

        profile_id: str,

        risk_percent: float,

    ) -> bool:

        profile = self.profiles.get(

            profile_id

        )

        if profile is None:

            return False

        profile.risk_per_trade = max(

            0.10,

            float(risk_percent),

        )

        profile.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # SET MAX DAILY LOSS
    # =====================================================

    def set_max_daily_loss(

        self,

        profile_id: str,

        loss_percent: float,

    ) -> bool:

        profile = self.profiles.get(

            profile_id

        )

        if profile is None:

            return False

        profile.max_daily_loss = max(

            0.50,

            float(loss_percent),

        )

        profile.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # SET MAX OPEN POSITIONS
    # =====================================================

    def set_max_open_positions(

        self,

        profile_id: str,

        positions: int,

    ) -> bool:

        profile = self.profiles.get(

            profile_id

        )

        if profile is None:

            return False

        profile.max_open_positions = max(

            1,

            int(positions),

        )

        profile.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # SET MAX POSITION SIZE
    # =====================================================

    def set_max_position_size(

        self,

        profile_id: str,

        percent: float,

    ) -> bool:

        profile = self.profiles.get(

            profile_id

        )

        if profile is None:

            return False

        profile.max_position_size = max(

            1.0,

            float(percent),

        )

        profile.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # SET REWARD RATIO
    # =====================================================

    def set_reward_ratio(

        self,

        profile_id: str,

        ratio: float,

    ) -> bool:

        profile = self.profiles.get(

            profile_id

        )

        if profile is None:

            return False

        profile.reward_ratio = max(

            1.0,

            float(ratio),

        )

        profile.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # CALCULATE RISK AMOUNT
    # =====================================================

    def risk_amount(

        self,

        profile_id: str,

    ) -> float:

        profile = self.profiles.get(

            profile_id

        )

        if profile is None:

            return 0.0

        return (

            profile.capital

            * profile.risk_per_trade

            / 100.0

        )

    # =====================================================
    # CALCULATE POSITION SIZE
    # =====================================================

    def position_size(

        self,

        profile_id: str,

    ) -> float:

        profile = self.profiles.get(

            profile_id

        )

        if profile is None:

            return 0.0

        return (

            profile.capital

            * profile.max_position_size

            / 100.0

        )

    # =====================================================
    # CALCULATE QUANTITY
    # =====================================================

    def quantity(

        self,

        profile_id: str,

        entry_price: float,

        stop_loss: float,

    ) -> int:

        profile = self.profiles.get(

            profile_id

        )

        if (

            profile is None

            or entry_price <= 0

            or stop_loss <= 0

        ):

            return 0

        risk = abs(

            entry_price

            - stop_loss

        )

        if risk == 0:

            return 0

        qty = int(

            self.risk_amount(

                profile_id

            )

            / risk

        )

        max_qty = int(

            self.position_size(

                profile_id

            )

            / entry_price

        )

        return max(

            0,

            min(

                qty,

                max_qty,

            ),

        )

    # =====================================================
    # VALIDATE TRADE
    # =====================================================

    def validate_trade(

        self,

        profile_id: str,

        entry_price: float,

        stop_loss: float,

        current_positions: int,

    ) -> bool:

        profile = self.profiles.get(

            profile_id

        )

        if profile is None:

            return False

        if current_positions >= profile.max_open_positions:

            return False

        if stop_loss >= entry_price:

            return False

        if self.quantity(

            profile_id,

            entry_price,

            stop_loss,

        ) <= 0:

            return False

        return True
        # =====================================================
    # SAVE
    # =====================================================

    def save(self) -> bool:

        try:

            data = []

            default_profile_id = (
                self.default_profile.id
                if self.default_profile
                else None
            )

            for profile in self.profiles.values():

                item = asdict(profile)

                item["created_at"] = (
                    profile.created_at.isoformat()
                )

                item["updated_at"] = (
                    profile.updated_at.isoformat()
                )

                data.append(item)

            payload = {
                "default_profile": default_profile_id,
                "profiles": data,
            }

            self.storage_file.write_text(
                json.dumps(
                    payload,
                    indent=4,
                ),
                encoding="utf-8",
            )

            return True

        except Exception:

            return False

    # =====================================================
    # LOAD
    # =====================================================

    def load(self) -> bool:

        if not self.storage_file.exists():

            return False

        try:

            self.profiles.clear()

            payload = json.loads(
                self.storage_file.read_text(
                    encoding="utf-8"
                )
            )

            profiles = payload.get(
                "profiles",
                [],
            )

            default_profile_id = payload.get(
                "default_profile"
            )

            for item in profiles:

                profile = RiskProfile(

                    id=item["id"],

                    name=item["name"],

                    capital=item.get(
                        "capital",
                        100000.0,
                    ),

                    risk_per_trade=item.get(
                        "risk_per_trade",
                        1.0,
                    ),

                    max_open_positions=item.get(
                        "max_open_positions",
                        5,
                    ),

                    max_daily_loss=item.get(
                        "max_daily_loss",
                        3.0,
                    ),

                    max_position_size=item.get(
                        "max_position_size",
                        20.0,
                    ),

                    reward_ratio=item.get(
                        "reward_ratio",
                        2.0,
                    ),

                    created_at=datetime.fromisoformat(
                        item["created_at"]
                    ),

                    updated_at=datetime.fromisoformat(
                        item["updated_at"]
                    ),

                    metadata=item.get(
                        "metadata",
                        {},
                    ),

                )

                self.profiles[
                    profile.id
                ] = profile

            self.default_profile = self.profiles.get(
                default_profile_id
            )

            return True

        except Exception:

            return False

    # =====================================================
    # SET DEFAULT PROFILE
    # =====================================================

    def set_default_profile(

        self,

        profile_id: str,

    ) -> bool:

        profile = self.profiles.get(
            profile_id
        )

        if profile is None:

            return False

        self.default_profile = profile

        return self.save()

    # =====================================================
    # DELETE PROFILE
    # =====================================================

    def delete_profile(

        self,

        profile_id: str,

    ) -> bool:

        if profile_id not in self.profiles:

            return False

        if (
            self.default_profile
            and self.default_profile.id == profile_id
        ):
            return False

        del self.profiles[
            profile_id
        ]

        return self.save()

    # =====================================================
    # RENAME PROFILE
    # =====================================================

    def rename_profile(

        self,

        profile_id: str,

        name: str,

    ) -> bool:

        profile = self.profiles.get(
            profile_id
        )

        if profile is None:

            return False

        profile.name = name

        profile.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # SEARCH PROFILES
    # =====================================================

    def search(

        self,

        keyword: str,

    ) -> List[RiskProfile]:

        keyword = keyword.lower()

        return [

            profile

            for profile in self.profiles.values()

            if keyword in profile.name.lower()

        ]

    # =====================================================
    # EXPORT PROFILES
    # =====================================================

    def export_profiles(

        self,

        file_path: str,

    ) -> bool:

        try:

            path = Path(file_path)

            path.write_text(

                self.storage_file.read_text(
                    encoding="utf-8"
                ),

                encoding="utf-8",

            )

            return True

        except Exception:

            return False

    # =====================================================
    # IMPORT PROFILES
    # =====================================================

    def import_profiles(

        self,

        file_path: str,

    ) -> bool:

        try:

            path = Path(file_path)

            if not path.exists():

                return False

            self.storage_file.write_text(

                path.read_text(
                    encoding="utf-8"
                ),

                encoding="utf-8",

            )

            return self.load()

        except Exception:

            return False

    # =====================================================
    # STATISTICS
    # =====================================================

    def statistics(self) -> Dict[str, Any]:

        return {

            "total_profiles": len(
                self.profiles
            ),

            "default_profile": (
                self.default_profile.name
                if self.default_profile
                else None
            ),

            "total_capital": sum(
                profile.capital
                for profile in self.profiles.values()
            ),

            "average_risk": (
                sum(
                    profile.risk_per_trade
                    for profile in self.profiles.values()
                )
                / max(
                    len(self.profiles),
                    1,
                )
            ),

        }
        # =====================================================
    # HEALTH
    # =====================================================

    def health(self) -> Dict[str, Any]:

        return {

            "storage_file": str(

                self.storage_file

            ),

            "exists": self.storage_file.exists(),

            "total_profiles": len(

                self.profiles

            ),

            "default_profile": (

                self.default_profile.name

                if self.default_profile

                else None

            ),

        }

    # =====================================================
    # STARTUP
    # =====================================================

    def startup(self) -> Dict[str, Any]:
        """
        Startup hook.

        Loads all saved risk profiles.
        """

        self.load()

        return self.statistics()

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(self) -> Dict[str, Any]:
        """
        Shutdown hook.

        Saves all risk profiles before exit.
        """

        self.save()

        return self.statistics()

    # =====================================================
    # RELOAD
    # =====================================================

    def reload(self) -> bool:

        return self.load()

    # =====================================================
    # PROFILE EXISTS
    # =====================================================

    def exists(

        self,

        profile_id: str,

    ) -> bool:

        return profile_id in self.profiles

    # =====================================================
    # GET PROFILE BY NAME
    # =====================================================

    def get_by_name(

        self,

        name: str,

    ) -> Optional[RiskProfile]:

        name = name.lower()

        for profile in self.profiles.values():

            if profile.name.lower() == name:

                return profile

        return None

    # =====================================================
    # UPDATE METADATA
    # =====================================================

    def set_metadata(

        self,

        profile_id: str,

        metadata: Dict[str, Any],

    ) -> bool:

        profile = self.profiles.get(

            profile_id

        )

        if profile is None:

            return False

        profile.metadata = dict(

            metadata

        )

        profile.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # REPR
    # =====================================================

    def __repr__(self) -> str:

        stats = self.statistics()

        return (

            "RiskManager("

            f"profiles={stats['total_profiles']}, "

            f"default='{stats['default_profile']}'"

            ")"

        )

    # =====================================================
    # STR
    # =====================================================

    def __str__(self) -> str:

        stats = self.statistics()

        return (

            "Risk Manager\n"

            f"Profiles        : {stats['total_profiles']}\n"

            f"Default Profile : {stats['default_profile']}\n"

            f"Total Capital   : {stats['total_capital']:.2f}\n"

            f"Average Risk %  : {stats['average_risk']:.2f}"

        )


# =====================================================
# GLOBAL SINGLETON
# =====================================================

risk_manager = RiskManager()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "RiskProfile",

    "RiskManager",

    "risk_manager",

]