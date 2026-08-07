from __future__ import annotations

import json
import threading
import uuid

from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# =====================================================
# STRATEGY
# =====================================================

@dataclass(slots=True)
class Strategy:

    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    name: str = ""

    description: str = ""

    enabled: bool = True

    timeframe: str = "15m"

    risk_percent: float = 1.0

    reward_ratio: float = 2.0

    entry_rules: List[str] = field(
        default_factory=list
    )

    exit_rules: List[str] = field(
        default_factory=list
    )

    stoploss_rules: List[str] = field(
        default_factory=list
    )

    target_rules: List[str] = field(
        default_factory=list
    )

    scanner: str = ""

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
# STRATEGY MANAGER
# =====================================================

class StrategyManager:

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
            / "strategies.json"
        )

        self.strategies: Dict[
            str,
            Strategy,
        ] = {}

        self.load()

    # =====================================================
    # CREATE STRATEGY
    # =====================================================

    def create_strategy(

        self,

        name: str,

        timeframe: str = "15m",

    ) -> Strategy:

        strategy = Strategy(

            name=name,

            timeframe=timeframe,

        )

        self.strategies[
            strategy.id
        ] = strategy

        self.save()

        return strategy

    # =====================================================
    # GET STRATEGY
    # =====================================================

    def get(

        self,

        strategy_id: str,

    ) -> Optional[Strategy]:

        return self.strategies.get(
            strategy_id
        )

    # =====================================================
    # ALL STRATEGIES
    # =====================================================

    def all_strategies(self) -> List[Strategy]:

        return list(
            self.strategies.values()
        )
        # =====================================================
    # ENABLE STRATEGY
    # =====================================================

    def enable_strategy(

        self,

        strategy_id: str,

    ) -> bool:

        strategy = self.strategies.get(

            strategy_id

        )

        if strategy is None:

            return False

        strategy.enabled = True

        strategy.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # DISABLE STRATEGY
    # =====================================================

    def disable_strategy(

        self,

        strategy_id: str,

    ) -> bool:

        strategy = self.strategies.get(

            strategy_id

        )

        if strategy is None:

            return False

        strategy.enabled = False

        strategy.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # RENAME STRATEGY
    # =====================================================

    def rename_strategy(

        self,

        strategy_id: str,

        name: str,

    ) -> bool:

        strategy = self.strategies.get(

            strategy_id

        )

        if strategy is None:

            return False

        strategy.name = name

        strategy.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # DELETE STRATEGY
    # =====================================================

    def delete_strategy(

        self,

        strategy_id: str,

    ) -> bool:

        if strategy_id not in self.strategies:

            return False

        del self.strategies[

            strategy_id

        ]

        return self.save()

    # =====================================================
    # SET TIMEFRAME
    # =====================================================

    def set_timeframe(

        self,

        strategy_id: str,

        timeframe: str,

    ) -> bool:

        strategy = self.strategies.get(

            strategy_id

        )

        if strategy is None:

            return False

        strategy.timeframe = timeframe

        strategy.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # SET RISK
    # =====================================================

    def set_risk(

        self,

        strategy_id: str,

        risk_percent: float,

    ) -> bool:

        strategy = self.strategies.get(

            strategy_id

        )

        if strategy is None:

            return False

        strategy.risk_percent = max(

            0.10,

            float(risk_percent),

        )

        strategy.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # SET REWARD RATIO
    # =====================================================

    def set_reward_ratio(

        self,

        strategy_id: str,

        reward_ratio: float,

    ) -> bool:

        strategy = self.strategies.get(

            strategy_id

        )

        if strategy is None:

            return False

        strategy.reward_ratio = max(

            1.0,

            float(reward_ratio),

        )

        strategy.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # ENTRY RULES
    # =====================================================

    def set_entry_rules(

        self,

        strategy_id: str,

        rules: List[str],

    ) -> bool:

        strategy = self.strategies.get(

            strategy_id

        )

        if strategy is None:

            return False

        strategy.entry_rules = list(

            rules

        )

        strategy.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # EXIT RULES
    # =====================================================

    def set_exit_rules(

        self,

        strategy_id: str,

        rules: List[str],

    ) -> bool:

        strategy = self.strategies.get(

            strategy_id

        )

        if strategy is None:

            return False

        strategy.exit_rules = list(

            rules

        )

        strategy.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # STOP LOSS RULES
    # =====================================================

    def set_stoploss_rules(

        self,

        strategy_id: str,

        rules: List[str],

    ) -> bool:

        strategy = self.strategies.get(

            strategy_id

        )

        if strategy is None:

            return False

        strategy.stoploss_rules = list(

            rules

        )

        strategy.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # TARGET RULES
    # =====================================================

    def set_target_rules(

        self,

        strategy_id: str,

        rules: List[str],

    ) -> bool:

        strategy = self.strategies.get(

            strategy_id

        )

        if strategy is None:

            return False

        strategy.target_rules = list(

            rules

        )

        strategy.updated_at = datetime.utcnow()

        return self.save()
        # =====================================================
    # SAVE
    # =====================================================

    def save(self) -> bool:

        try:

            data = []

            for strategy in self.strategies.values():

                item = asdict(

                    strategy

                )

                item["created_at"] = (

                    strategy.created_at.isoformat()

                )

                item["updated_at"] = (

                    strategy.updated_at.isoformat()

                )

                data.append(

                    item

                )

            self.storage_file.write_text(

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
    # LOAD
    # =====================================================

    def load(self) -> bool:

        if not self.storage_file.exists():

            return False

        try:

            self.strategies.clear()

            data = json.loads(

                self.storage_file.read_text(

                    encoding="utf-8"

                )

            )

            for item in data:

                strategy = Strategy(

                    id=item["id"],

                    name=item["name"],

                    description=item.get(

                        "description",

                        "",

                    ),

                    enabled=item.get(

                        "enabled",

                        True,

                    ),

                    timeframe=item.get(

                        "timeframe",

                        "15m",

                    ),

                    risk_percent=item.get(

                        "risk_percent",

                        1.0,

                    ),

                    reward_ratio=item.get(

                        "reward_ratio",

                        2.0,

                    ),

                    entry_rules=item.get(

                        "entry_rules",

                        [],

                    ),

                    exit_rules=item.get(

                        "exit_rules",

                        [],

                    ),

                    stoploss_rules=item.get(

                        "stoploss_rules",

                        [],

                    ),

                    target_rules=item.get(

                        "target_rules",

                        [],

                    ),

                    scanner=item.get(

                        "scanner",

                        "",

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

                self.strategies[

                    strategy.id

                ] = strategy

            return True

        except Exception:

            return False

    # =====================================================
    # EXPORT STRATEGIES
    # =====================================================

    def export_strategies(

        self,

        file_path: str,

    ) -> bool:

        try:

            path = Path(

                file_path

            )

            data = []

            for strategy in self.strategies.values():

                item = asdict(

                    strategy

                )

                item["created_at"] = (

                    strategy.created_at.isoformat()

                )

                item["updated_at"] = (

                    strategy.updated_at.isoformat()

                )

                data.append(

                    item

                )

            path.write_text(

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
    # IMPORT STRATEGIES
    # =====================================================

    def import_strategies(

        self,

        file_path: str,

    ) -> bool:

        try:

            path = Path(

                file_path

            )

            if not path.exists():

                return False

            data = json.loads(

                path.read_text(

                    encoding="utf-8"

                )

            )

            self.strategies.clear()

            for item in data:

                strategy = Strategy(

                    id=item.get(

                        "id",

                        str(uuid.uuid4()),

                    ),

                    name=item["name"],

                    description=item.get(

                        "description",

                        "",

                    ),

                    enabled=item.get(

                        "enabled",

                        True,

                    ),

                    timeframe=item.get(

                        "timeframe",

                        "15m",

                    ),

                    risk_percent=item.get(

                        "risk_percent",

                        1.0,

                    ),

                    reward_ratio=item.get(

                        "reward_ratio",

                        2.0,

                    ),

                    entry_rules=item.get(

                        "entry_rules",

                        [],

                    ),

                    exit_rules=item.get(

                        "exit_rules",

                        [],

                    ),

                    stoploss_rules=item.get(

                        "stoploss_rules",

                        [],

                    ),

                    target_rules=item.get(

                        "target_rules",

                        [],

                    ),

                    scanner=item.get(

                        "scanner",

                        "",

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

                self.strategies[

                    strategy.id

                ] = strategy

            return self.save()

        except Exception:

            return False

    # =====================================================
    # SEARCH STRATEGIES
    # =====================================================

    def search(

        self,

        keyword: str,

    ) -> List[Strategy]:

        keyword = keyword.lower()

        return [

            strategy

            for strategy in self.strategies.values()

            if (

                keyword in strategy.name.lower()

                or keyword in strategy.description.lower()

            )

        ]

    # =====================================================
    # ENABLED STRATEGIES
    # =====================================================

    def enabled_strategies(

        self,

    ) -> List[Strategy]:

        return [

            strategy

            for strategy in self.strategies.values()

            if strategy.enabled

        ]

    # =====================================================
    # DISABLED STRATEGIES
    # =====================================================

    def disabled_strategies(

        self,

    ) -> List[Strategy]:

        return [

            strategy

            for strategy in self.strategies.values()

            if not strategy.enabled

        ]

    # =====================================================
    # STATISTICS
    # =====================================================

    def statistics(self) -> Dict[str, Any]:

        return {

            "total_strategies": len(

                self.strategies

            ),

            "enabled": len(

                self.enabled_strategies()

            ),

            "disabled": len(

                self.disabled_strategies()

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

            "total_strategies": len(

                self.strategies

            ),

            "enabled_strategies": len(

                self.enabled_strategies()

            ),

            "disabled_strategies": len(

                self.disabled_strategies()

            ),

        }

    # =====================================================
    # STARTUP
    # =====================================================

    def startup(self) -> Dict[str, Any]:
        """
        Startup hook.

        Loads all saved strategies.
        """

        self.load()

        return self.statistics()

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(self) -> Dict[str, Any]:
        """
        Shutdown hook.

        Saves all strategies before exit.
        """

        self.save()

        return self.statistics()

    # =====================================================
    # RELOAD
    # =====================================================

    def reload(self) -> bool:

        return self.load()

    # =====================================================
    # STRATEGY EXISTS
    # =====================================================

    def exists(

        self,

        strategy_id: str,

    ) -> bool:

        return strategy_id in self.strategies

    # =====================================================
    # GET STRATEGY BY NAME
    # =====================================================

    def get_by_name(

        self,

        name: str,

    ) -> Optional[Strategy]:

        name = name.lower()

        for strategy in self.strategies.values():

            if strategy.name.lower() == name:

                return strategy

        return None

    # =====================================================
    # UPDATE DESCRIPTION
    # =====================================================

    def set_description(

        self,

        strategy_id: str,

        description: str,

    ) -> bool:

        strategy = self.strategies.get(

            strategy_id

        )

        if strategy is None:

            return False

        strategy.description = description

        strategy.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # UPDATE SCANNER
    # =====================================================

    def set_scanner(

        self,

        strategy_id: str,

        scanner: str,

    ) -> bool:

        strategy = self.strategies.get(

            strategy_id

        )

        if strategy is None:

            return False

        strategy.scanner = scanner

        strategy.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # UPDATE METADATA
    # =====================================================

    def set_metadata(

        self,

        strategy_id: str,

        metadata: Dict[str, Any],

    ) -> bool:

        strategy = self.strategies.get(

            strategy_id

        )

        if strategy is None:

            return False

        strategy.metadata = dict(

            metadata

        )

        strategy.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # REPR
    # =====================================================

    def __repr__(self) -> str:

        stats = self.statistics()

        return (

            "StrategyManager("

            f"strategies={stats['total_strategies']}, "

            f"enabled={stats['enabled']}, "

            f"disabled={stats['disabled']}"

            ")"

        )

    # =====================================================
    # STR
    # =====================================================

    def __str__(self) -> str:

        stats = self.statistics()

        return (

            "Strategy Manager\n"

            f"Total Strategies : {stats['total_strategies']}\n"

            f"Enabled          : {stats['enabled']}\n"

            f"Disabled         : {stats['disabled']}"

        )


# =====================================================
# GLOBAL SINGLETON
# =====================================================

strategy_manager = StrategyManager()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "Strategy",

    "StrategyManager",

    "strategy_manager",

]
