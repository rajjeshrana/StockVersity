from __future__ import annotations

import json
import threading
import uuid

from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# =====================================================
# SIGNAL
# =====================================================

@dataclass(slots=True)
class TradingSignal:

    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    symbol: str = ""

    exchange: str = "NSE"

    signal_type: str = "BUY"      # BUY/SELL/SHORT/COVER

    timeframe: str = "15m"

    strategy: str = ""

    score: float = 0.0

    confidence: float = 0.0

    entry: float = 0.0

    stop_loss: float = 0.0

    target1: float = 0.0

    target2: float = 0.0

    target3: float = 0.0

    quantity: int = 0

    risk_reward: float = 0.0

    status: str = "PENDING"

    expires_at: Optional[datetime] = None

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
# SIGNAL MANAGER
# =====================================================

class SignalManager:

    _instance = None

    _lock = threading.Lock()

    def __new__(cls):

        with cls._lock:

            if cls._instance is None:

                cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):

        if getattr(self, "_initialized", False):

            return

        self._initialized = True

        self.manager_lock = threading.RLock()

        self.storage_directory = (
            Path.home() /
            ".stockversity"
        )

        self.storage_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.storage_file = (
            self.storage_directory /
            "signals.json"
        )

        self.signals: Dict[
            str,
            TradingSignal,
        ] = {}

        self.load()

    # =====================================================
    # CREATE SIGNAL
    # =====================================================

    def create_signal(

        self,

        symbol: str,

        signal_type: str,

        strategy: str,

        timeframe: str,

    ) -> TradingSignal:

        signal = TradingSignal(

            symbol=symbol,

            signal_type=signal_type,

            strategy=strategy,

            timeframe=timeframe,

        )

        self.signals[
            signal.id
        ] = signal

        self.save()

        return signal

    # =====================================================
    # GET SIGNAL
    # =====================================================

    def get(

        self,

        signal_id: str,

    ) -> Optional[TradingSignal]:

        return self.signals.get(

            signal_id

        )

    # =====================================================
    # ALL SIGNALS
    # =====================================================

    def all_signals(

        self,

    ) -> List[TradingSignal]:

        return list(

            self.signals.values()

        )
        # =====================================================
    # UPDATE SIGNAL
    # =====================================================

    def update_signal(

        self,

        signal_id: str,

        **kwargs,

    ) -> bool:

        signal = self.signals.get(

            signal_id

        )

        if signal is None:

            return False

        for key, value in kwargs.items():

            if hasattr(signal, key):

                setattr(

                    signal,

                    key,

                    value,

                )

        signal.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # ACTIVATE SIGNAL
    # =====================================================

    def activate_signal(

        self,

        signal_id: str,

    ) -> bool:

        signal = self.signals.get(

            signal_id

        )

        if signal is None:

            return False

        signal.status = "ACTIVE"

        signal.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # TRIGGER SIGNAL
    # =====================================================

    def trigger_signal(

        self,

        signal_id: str,

    ) -> bool:

        signal = self.signals.get(

            signal_id

        )

        if signal is None:

            return False

        signal.status = "TRIGGERED"

        signal.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # CLOSE SIGNAL
    # =====================================================

    def close_signal(

        self,

        signal_id: str,

    ) -> bool:

        signal = self.signals.get(

            signal_id

        )

        if signal is None:

            return False

        signal.status = "CLOSED"

        signal.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # CANCEL SIGNAL
    # =====================================================

    def cancel_signal(

        self,

        signal_id: str,

    ) -> bool:

        signal = self.signals.get(

            signal_id

        )

        if signal is None:

            return False

        signal.status = "CANCELLED"

        signal.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # EXPIRE SIGNAL
    # =====================================================

    def expire_signal(

        self,

        signal_id: str,

    ) -> bool:

        signal = self.signals.get(

            signal_id

        )

        if signal is None:

            return False

        signal.status = "EXPIRED"

        signal.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # SET ENTRY
    # =====================================================

    def set_entry(

        self,

        signal_id: str,

        entry: float,

    ) -> bool:

        signal = self.get(

            signal_id

        )

        if signal is None:

            return False

        signal.entry = float(entry)

        signal.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # SET STOP LOSS
    # =====================================================

    def set_stop_loss(

        self,

        signal_id: str,

        stop_loss: float,

    ) -> bool:

        signal = self.get(

            signal_id

        )

        if signal is None:

            return False

        signal.stop_loss = float(stop_loss)

        signal.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # SET TARGETS
    # =====================================================

    def set_targets(

        self,

        signal_id: str,

        target1: float,

        target2: float = 0.0,

        target3: float = 0.0,

    ) -> bool:

        signal = self.get(

            signal_id

        )

        if signal is None:

            return False

        signal.target1 = float(target1)

        signal.target2 = float(target2)

        signal.target3 = float(target3)

        signal.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # SET CONFIDENCE
    # =====================================================

    def set_confidence(

        self,

        signal_id: str,

        confidence: float,

    ) -> bool:

        signal = self.get(

            signal_id

        )

        if signal is None:

            return False

        signal.confidence = max(

            0.0,

            min(

                100.0,

                float(confidence),

            ),

        )

        signal.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # SET SCORE
    # =====================================================

    def set_score(

        self,

        signal_id: str,

        score: float,

    ) -> bool:

        signal = self.get(

            signal_id

        )

        if signal is None:

            return False

        signal.score = max(

            0.0,

            min(

                100.0,

                float(score),

            ),

        )

        signal.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # CALCULATE RISK / REWARD
    # =====================================================

    def calculate_risk_reward(

        self,

        signal_id: str,

    ) -> float:

        signal = self.get(

            signal_id

        )

        if signal is None:

            return 0.0

        risk = abs(

            signal.entry

            - signal.stop_loss

        )

        reward = abs(

            signal.target1

            - signal.entry

        )

        if risk <= 0:

            signal.risk_reward = 0.0

        else:

            signal.risk_reward = round(

                reward / risk,

                2,

            )

        signal.updated_at = datetime.utcnow()

        self.save()

        return signal.risk_reward

    # =====================================================
    # DUPLICATE SIGNAL CHECK
    # =====================================================

    def is_duplicate(

        self,

        symbol: str,

        signal_type: str,

        timeframe: str,

    ) -> bool:

        for signal in self.signals.values():

            if (

                signal.symbol == symbol

                and signal.signal_type == signal_type

                and signal.timeframe == timeframe

                and signal.status in (

                    "PENDING",

                    "ACTIVE",

                    "TRIGGERED",

                )

            ):

                return True

        return False
        # =====================================================
    # SAVE
    # =====================================================

    def save(self) -> bool:

        try:

            data = []

            for signal in self.signals.values():

                item = asdict(signal)

                item["created_at"] = (
                    signal.created_at.isoformat()
                )

                item["updated_at"] = (
                    signal.updated_at.isoformat()
                )

                item["expires_at"] = (
                    signal.expires_at.isoformat()
                    if signal.expires_at
                    else None
                )

                data.append(item)

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

            self.signals.clear()

            data = json.loads(

                self.storage_file.read_text(

                    encoding="utf-8"

                )

            )

            for item in data:

                signal = TradingSignal(

                    id=item["id"],

                    symbol=item["symbol"],

                    exchange=item.get(
                        "exchange",
                        "NSE",
                    ),

                    signal_type=item.get(
                        "signal_type",
                        "BUY",
                    ),

                    timeframe=item.get(
                        "timeframe",
                        "15m",
                    ),

                    strategy=item.get(
                        "strategy",
                        "",
                    ),

                    score=item.get(
                        "score",
                        0.0,
                    ),

                    confidence=item.get(
                        "confidence",
                        0.0,
                    ),

                    entry=item.get(
                        "entry",
                        0.0,
                    ),

                    stop_loss=item.get(
                        "stop_loss",
                        0.0,
                    ),

                    target1=item.get(
                        "target1",
                        0.0,
                    ),

                    target2=item.get(
                        "target2",
                        0.0,
                    ),

                    target3=item.get(
                        "target3",
                        0.0,
                    ),

                    quantity=item.get(
                        "quantity",
                        0,
                    ),

                    risk_reward=item.get(
                        "risk_reward",
                        0.0,
                    ),

                    status=item.get(
                        "status",
                        "PENDING",
                    ),

                    expires_at=(
                        datetime.fromisoformat(
                            item["expires_at"]
                        )
                        if item.get("expires_at")
                        else None
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

                self.signals[
                    signal.id
                ] = signal

            return True

        except Exception:

            return False

    # =====================================================
    # EXPORT SIGNALS
    # =====================================================

    def export_signals(

        self,

        file_path: str,

    ) -> bool:

        try:

            Path(file_path).write_text(

                self.storage_file.read_text(

                    encoding="utf-8"

                ),

                encoding="utf-8",

            )

            return True

        except Exception:

            return False

    # =====================================================
    # IMPORT SIGNALS
    # =====================================================

    def import_signals(

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
    # SEARCH
    # =====================================================

    def search(

        self,

        keyword: str,

    ) -> List[TradingSignal]:

        keyword = keyword.lower()

        return [

            signal

            for signal in self.signals.values()

            if (

                keyword in signal.symbol.lower()

                or keyword in signal.strategy.lower()

            )

        ]

    # =====================================================
    # BY SYMBOL
    # =====================================================

    def by_symbol(

        self,

        symbol: str,

    ) -> List[TradingSignal]:

        return [

            signal

            for signal in self.signals.values()

            if signal.symbol.upper() == symbol.upper()

        ]

    # =====================================================
    # BY STRATEGY
    # =====================================================

    def by_strategy(

        self,

        strategy: str,

    ) -> List[TradingSignal]:

        return [

            signal

            for signal in self.signals.values()

            if signal.strategy.lower() == strategy.lower()

        ]

    # =====================================================
    # BY STATUS
    # =====================================================

    def by_status(

        self,

        status: str,

    ) -> List[TradingSignal]:

        return [

            signal

            for signal in self.signals.values()

            if signal.status.upper() == status.upper()

        ]

    # =====================================================
    # BY TIMEFRAME
    # =====================================================

    def by_timeframe(

        self,

        timeframe: str,

    ) -> List[TradingSignal]:

        return [

            signal

            for signal in self.signals.values()

            if signal.timeframe == timeframe

        ]

    # =====================================================
    # ACTIVE SIGNALS
    # =====================================================

    def active_signals(

        self,

    ) -> List[TradingSignal]:

        return self.by_status(

            "ACTIVE"

        )

    # =====================================================
    # PENDING SIGNALS
    # =====================================================

    def pending_signals(

        self,

    ) -> List[TradingSignal]:

        return self.by_status(

            "PENDING"

        )

    # =====================================================
    # TRIGGERED SIGNALS
    # =====================================================

    def triggered_signals(

        self,

    ) -> List[TradingSignal]:

        return self.by_status(

            "TRIGGERED"

        )

    # =====================================================
    # STATISTICS
    # =====================================================

    def statistics(self) -> Dict[str, Any]:

        return {

            "total_signals": len(

                self.signals

            ),

            "pending": len(

                self.pending_signals()

            ),

            "active": len(

                self.active_signals()

            ),

            "triggered": len(

                self.triggered_signals()

            ),

            "closed": len(

                self.by_status(

                    "CLOSED"

                )

            ),

            "cancelled": len(

                self.by_status(

                    "CANCELLED"

                )

            ),

            "expired": len(

                self.by_status(

                    "EXPIRED"

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

            "total_signals": len(

                self.signals

            ),

            "active_signals": len(

                self.active_signals()

            ),

            "pending_signals": len(

                self.pending_signals()

            ),

            "triggered_signals": len(

                self.triggered_signals()

            ),

        }

    # =====================================================
    # STARTUP
    # =====================================================

    def startup(self) -> Dict[str, Any]:
        """
        Startup hook.
        """

        self.load()

        return self.statistics()

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(self) -> Dict[str, Any]:
        """
        Shutdown hook.
        """

        self.save()

        return self.statistics()

    # =====================================================
    # RELOAD
    # =====================================================

    def reload(self) -> bool:

        return self.load()

    # =====================================================
    # SIGNAL EXISTS
    # =====================================================

    def exists(

        self,

        signal_id: str,

    ) -> bool:

        return signal_id in self.signals

    # =====================================================
    # GET LATEST SIGNAL
    # =====================================================

    def get_latest_signal(

        self,

        symbol: Optional[str] = None,

    ) -> Optional[TradingSignal]:

        signals = list(

            self.signals.values()

        )

        if symbol:

            signals = [

                signal

                for signal in signals

                if signal.symbol.upper() == symbol.upper()

            ]

        if not signals:

            return None

        return max(

            signals,

            key=lambda signal: signal.created_at,

        )

    # =====================================================
    # REMOVE SIGNAL
    # =====================================================

    def remove_signal(

        self,

        signal_id: str,

    ) -> bool:

        if signal_id not in self.signals:

            return False

        del self.signals[

            signal_id

        ]

        return self.save()

    # =====================================================
    # CLEAR EXPIRED SIGNALS
    # =====================================================

    def clear_expired(self) -> int:

        expired_ids = [

            signal_id

            for signal_id, signal in self.signals.items()

            if signal.status == "EXPIRED"

        ]

        for signal_id in expired_ids:

            del self.signals[

                signal_id

            ]

        if expired_ids:

            self.save()

        return len(

            expired_ids

        )

    # =====================================================
    # REPR
    # =====================================================

    def __repr__(self) -> str:

        stats = self.statistics()

        return (

            "SignalManager("

            f"signals={stats['total_signals']}, "

            f"active={stats['active']}, "

            f"pending={stats['pending']}"

            ")"

        )

    # =====================================================
    # STR
    # =====================================================

    def __str__(self) -> str:

        stats = self.statistics()

        return (

            "Signal Manager\n"

            f"Total Signals : {stats['total_signals']}\n"

            f"Pending       : {stats['pending']}\n"

            f"Active        : {stats['active']}\n"

            f"Triggered     : {stats['triggered']}\n"

            f"Closed        : {stats['closed']}"

        )


# =====================================================
# GLOBAL SINGLETON
# =====================================================

signal_manager = SignalManager()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "TradingSignal",

    "SignalManager",

    "signal_manager",

]