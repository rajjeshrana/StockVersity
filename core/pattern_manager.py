from __future__ import annotations

import json
import threading
import uuid

from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# =====================================================
# PATTERN
# =====================================================

@dataclass(slots=True)
class ChartPattern:

    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    symbol: str = ""

    exchange: str = "NSE"

    name: str = ""

    timeframe: str = "15m"

    direction: str = "BULLISH"

    confidence: float = 0.0

    score: float = 0.0

    breakout_price: float = 0.0

    stop_loss: float = 0.0

    target: float = 0.0

    volume_confirmation: bool = False

    ai_verified: bool = False

    detected_by: str = "Scanner"

    status: str = "NEW"

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
# PATTERN MANAGER
# =====================================================

class PatternManager:

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

            / "patterns.json"

        )

        self.patterns: Dict[

            str,

            ChartPattern,

        ] = {}

        self.load()

    # =====================================================
    # CREATE PATTERN
    # =====================================================

    def create_pattern(

        self,

        symbol: str,

        pattern_name: str,

        timeframe: str,

    ) -> ChartPattern:

        pattern = ChartPattern(

            symbol=symbol,

            name=pattern_name,

            timeframe=timeframe,

        )

        self.patterns[

            pattern.id

        ] = pattern

        self.save()

        return pattern

    # =====================================================
    # GET PATTERN
    # =====================================================

    def get(

        self,

        pattern_id: str,

    ) -> Optional[ChartPattern]:

        return self.patterns.get(

            pattern_id

        )

    # =====================================================
    # ALL PATTERNS
    # =====================================================

    def all_patterns(

        self,

    ) -> List[ChartPattern]:

        return list(

            self.patterns.values()

        )
        # =====================================================
    # UPDATE PATTERN
    # =====================================================

    def update_pattern(

        self,

        pattern_id: str,

        **kwargs,

    ) -> bool:

        pattern = self.patterns.get(

            pattern_id

        )

        if pattern is None:

            return False

        for key, value in kwargs.items():

            if hasattr(pattern, key):

                setattr(

                    pattern,

                    key,

                    value,

                )

        pattern.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # DELETE PATTERN
    # =====================================================

    def delete_pattern(

        self,

        pattern_id: str,

    ) -> bool:

        if pattern_id not in self.patterns:

            return False

        del self.patterns[

            pattern_id

        ]

        return self.save()

    # =====================================================
    # CONFIRM PATTERN
    # =====================================================

    def confirm_pattern(

        self,

        pattern_id: str,

    ) -> bool:

        pattern = self.get(

            pattern_id

        )

        if pattern is None:

            return False

        pattern.status = "CONFIRMED"

        pattern.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # REJECT PATTERN
    # =====================================================

    def reject_pattern(

        self,

        pattern_id: str,

    ) -> bool:

        pattern = self.get(

            pattern_id

        )

        if pattern is None:

            return False

        pattern.status = "REJECTED"

        pattern.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # SET CONFIDENCE
    # =====================================================

    def set_confidence(

        self,

        pattern_id: str,

        confidence: float,

    ) -> bool:

        pattern = self.get(

            pattern_id

        )

        if pattern is None:

            return False

        pattern.confidence = max(

            0.0,

            min(

                100.0,

                float(confidence),

            ),

        )

        pattern.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # SET SCORE
    # =====================================================

    def set_score(

        self,

        pattern_id: str,

        score: float,

    ) -> bool:

        pattern = self.get(

            pattern_id

        )

        if pattern is None:

            return False

        pattern.score = max(

            0.0,

            min(

                100.0,

                float(score),

            ),

        )

        pattern.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # AI VERIFIED
    # =====================================================

    def set_ai_verified(

        self,

        pattern_id: str,

        verified: bool = True,

    ) -> bool:

        pattern = self.get(

            pattern_id

        )

        if pattern is None:

            return False

        pattern.ai_verified = verified

        pattern.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # SET BREAKOUT PRICE
    # =====================================================

    def set_breakout_price(

        self,

        pattern_id: str,

        price: float,

    ) -> bool:

        pattern = self.get(

            pattern_id

        )

        if pattern is None:

            return False

        pattern.breakout_price = float(

            price

        )

        pattern.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # SET STOP LOSS
    # =====================================================

    def set_stop_loss(

        self,

        pattern_id: str,

        stop_loss: float,

    ) -> bool:

        pattern = self.get(

            pattern_id

        )

        if pattern is None:

            return False

        pattern.stop_loss = float(

            stop_loss

        )

        pattern.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # SET TARGET
    # =====================================================

    def set_target(

        self,

        pattern_id: str,

        target: float,

    ) -> bool:

        pattern = self.get(

            pattern_id

        )

        if pattern is None:

            return False

        pattern.target = float(

            target

        )

        pattern.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # VOLUME CONFIRMATION
    # =====================================================

    def set_volume_confirmation(

        self,

        pattern_id: str,

        confirmed: bool,

    ) -> bool:

        pattern = self.get(

            pattern_id

        )

        if pattern is None:

            return False

        pattern.volume_confirmation = confirmed

        pattern.updated_at = datetime.utcnow()

        return self.save()

    # =====================================================
    # DUPLICATE PATTERN CHECK
    # =====================================================

    def is_duplicate(

        self,

        symbol: str,

        pattern_name: str,

        timeframe: str,

    ) -> bool:

        for pattern in self.patterns.values():

            if (

                pattern.symbol.upper() == symbol.upper()

                and pattern.name.lower() == pattern_name.lower()

                and pattern.timeframe == timeframe

                and pattern.status in (

                    "NEW",

                    "CONFIRMED",

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

            for pattern in self.patterns.values():

                item = asdict(pattern)

                item["created_at"] = (
                    pattern.created_at.isoformat()
                )

                item["updated_at"] = (
                    pattern.updated_at.isoformat()
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

            self.patterns.clear()

            data = json.loads(

                self.storage_file.read_text(

                    encoding="utf-8"

                )

            )

            for item in data:

                pattern = ChartPattern(

                    id=item["id"],

                    symbol=item["symbol"],

                    exchange=item.get(

                        "exchange",

                        "NSE",

                    ),

                    name=item.get(

                        "name",

                        "",

                    ),

                    timeframe=item.get(

                        "timeframe",

                        "15m",

                    ),

                    direction=item.get(

                        "direction",

                        "BULLISH",

                    ),

                    confidence=item.get(

                        "confidence",

                        0.0,

                    ),

                    score=item.get(

                        "score",

                        0.0,

                    ),

                    breakout_price=item.get(

                        "breakout_price",

                        0.0,

                    ),

                    stop_loss=item.get(

                        "stop_loss",

                        0.0,

                    ),

                    target=item.get(

                        "target",

                        0.0,

                    ),

                    volume_confirmation=item.get(

                        "volume_confirmation",

                        False,

                    ),

                    ai_verified=item.get(

                        "ai_verified",

                        False,

                    ),

                    detected_by=item.get(

                        "detected_by",

                        "Scanner",

                    ),

                    status=item.get(

                        "status",

                        "NEW",

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

                self.patterns[

                    pattern.id

                ] = pattern

            return True

        except Exception:

            return False

    # =====================================================
    # EXPORT PATTERNS
    # =====================================================

    def export_patterns(

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
    # IMPORT PATTERNS
    # =====================================================

    def import_patterns(

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

    ) -> List[ChartPattern]:

        keyword = keyword.lower()

        return [

            pattern

            for pattern in self.patterns.values()

            if (

                keyword in pattern.symbol.lower()

                or keyword in pattern.name.lower()

            )

        ]

    # =====================================================
    # BY SYMBOL
    # =====================================================

    def by_symbol(

        self,

        symbol: str,

    ) -> List[ChartPattern]:

        return [

            pattern

            for pattern in self.patterns.values()

            if pattern.symbol.upper() == symbol.upper()

        ]

    # =====================================================
    # BY PATTERN
    # =====================================================

    def by_pattern(

        self,

        pattern_name: str,

    ) -> List[ChartPattern]:

        return [

            pattern

            for pattern in self.patterns.values()

            if pattern.name.lower() == pattern_name.lower()

        ]

    # =====================================================
    # BY TIMEFRAME
    # =====================================================

    def by_timeframe(

        self,

        timeframe: str,

    ) -> List[ChartPattern]:

        return [

            pattern

            for pattern in self.patterns.values()

            if pattern.timeframe == timeframe

        ]

    # =====================================================
    # BY STATUS
    # =====================================================

    def by_status(

        self,

        status: str,

    ) -> List[ChartPattern]:

        return [

            pattern

            for pattern in self.patterns.values()

            if pattern.status.upper() == status.upper()

        ]

    # =====================================================
    # AI VERIFIED
    # =====================================================

    def ai_verified_patterns(

        self,

    ) -> List[ChartPattern]:

        return [

            pattern

            for pattern in self.patterns.values()

            if pattern.ai_verified

        ]

    # =====================================================
    # STATISTICS
    # =====================================================

    def statistics(self) -> Dict[str, Any]:

        return {

            "total_patterns": len(

                self.patterns

            ),

            "new": len(

                self.by_status(

                    "NEW"

                )

            ),

            "confirmed": len(

                self.by_status(

                    "CONFIRMED"

                )

            ),

            "rejected": len(

                self.by_status(

                    "REJECTED"

                )

            ),

            "ai_verified": len(

                self.ai_verified_patterns()

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

            "total_patterns": len(

                self.patterns

            ),

            "confirmed_patterns": len(

                self.by_status(

                    "CONFIRMED"

                )

            ),

            "ai_verified_patterns": len(

                self.ai_verified_patterns()

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
    # PATTERN EXISTS
    # =====================================================

    def exists(

        self,

        pattern_id: str,

    ) -> bool:

        return pattern_id in self.patterns

    # =====================================================
    # GET LATEST PATTERN
    # =====================================================

    def get_latest_pattern(

        self,

        symbol: Optional[str] = None,

    ) -> Optional[ChartPattern]:

        patterns = list(

            self.patterns.values()

        )

        if symbol:

            patterns = [

                pattern

                for pattern in patterns

                if pattern.symbol.upper() == symbol.upper()

            ]

        if not patterns:

            return None

        return max(

            patterns,

            key=lambda pattern: pattern.created_at,

        )

    # =====================================================
    # REMOVE PATTERN
    # =====================================================

    def remove_pattern(

        self,

        pattern_id: str,

    ) -> bool:

        if pattern_id not in self.patterns:

            return False

        del self.patterns[

            pattern_id

        ]

        return self.save()

    # =====================================================
    # CLEAR REJECTED PATTERNS
    # =====================================================

    def clear_rejected(self) -> int:

        rejected_ids = [

            pattern_id

            for pattern_id, pattern in self.patterns.items()

            if pattern.status == "REJECTED"

        ]

        for pattern_id in rejected_ids:

            del self.patterns[

                pattern_id

            ]

        if rejected_ids:

            self.save()

        return len(

            rejected_ids

        )

    # =====================================================
    # REPR
    # =====================================================

    def __repr__(self) -> str:

        stats = self.statistics()

        return (

            "PatternManager("

            f"patterns={stats['total_patterns']}, "

            f"confirmed={stats['confirmed']}, "

            f"verified={stats['ai_verified']}"

            ")"

        )

    # =====================================================
    # STR
    # =====================================================

    def __str__(self) -> str:

        stats = self.statistics()

        return (

            "Pattern Manager\n"

            f"Total Patterns : {stats['total_patterns']}\n"

            f"New            : {stats['new']}\n"

            f"Confirmed      : {stats['confirmed']}\n"

            f"Rejected       : {stats['rejected']}\n"

            f"AI Verified    : {stats['ai_verified']}"

        )


# =====================================================
# GLOBAL SINGLETON
# =====================================================

pattern_manager = PatternManager()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "ChartPattern",

    "PatternManager",

    "pattern_manager",

]