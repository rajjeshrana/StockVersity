"""
=========================================================
StockVersity Scanner Pro
Scanner Cache
Version : 2.0
=========================================================

Lightweight in-memory cache for scanner operations.

Responsibilities
----------------
• Cache scanner results
• Cache indicator calculations
• Cache market-data transformations
• TTL expiration
• Symbol/timeframe cache keys
• Cache invalidation
• Cache statistics
• Thread-safe access
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime
from datetime import timedelta

from threading import RLock

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple


# =========================================================
# CACHE ENTRY
# =========================================================

@dataclass(slots=True)
class CacheEntry:
    """
    One cached value.
    """

    value: Any

    created_at: datetime = field(
        default_factory=datetime.now
    )

    expires_at: Optional[datetime] = None

    hits: int = 0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    # =====================================================
    # EXPIRED
    # =====================================================

    @property
    def expired(
        self,
    ) -> bool:

        if self.expires_at is None:

            return False

        return (
            datetime.now()
            >= self.expires_at
        )

    # =====================================================
    # AGE
    # =====================================================

    @property
    def age_seconds(
        self,
    ) -> float:

        return max(
            0.0,
            (
                datetime.now()
                - self.created_at
            ).total_seconds(),
        )


# =========================================================
# CACHE STATISTICS
# =========================================================

@dataclass(slots=True)
class CacheStats:

    hits: int = 0

    misses: int = 0

    writes: int = 0

    deletions: int = 0

    expirations: int = 0

    clears: int = 0

    # =====================================================
    # HIT RATE
    # =====================================================

    @property
    def hit_rate(
        self,
    ) -> float:

        total = (
            self.hits
            + self.misses
        )

        if total <= 0:

            return 0.0

        return round(
            self.hits
            / total
            * 100.0,
            2,
        )

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "hits":
                self.hits,

            "misses":
                self.misses,

            "writes":
                self.writes,

            "deletions":
                self.deletions,

            "expirations":
                self.expirations,

            "clears":
                self.clears,

            "hit_rate":
                self.hit_rate,
        }


# =========================================================
# SCANNER CACHE
# =========================================================

class ScannerCache:
    """
    Thread-safe in-memory scanner cache.
    """

    def __init__(
        self,
        *,
        default_ttl: int = 60,
        max_entries: int = 5000,
    ) -> None:

        self.default_ttl = max(
            0,
            int(default_ttl),
        )

        self.max_entries = max(
            1,
            int(max_entries),
        )

        self._cache: Dict[
            str,
            CacheEntry
        ] = {}

        self._lock = RLock()

        self._stats = CacheStats()

    # =====================================================
    # NORMALIZE
    # =====================================================

    @staticmethod
    def _normalize(
        value: Any,
    ) -> str:

        return (
            str(value)
            .strip()
            .upper()
        )

    # =====================================================
    # BUILD KEY
    # =====================================================

    @classmethod
    def build_key(
        cls,
        namespace: str,
        *parts: Any,
    ) -> str:
        """
        Create consistent cache key.

        Example
        -------
        build_key(
            "INDICATOR",
            "RELIANCE",
            "5m",
            "RSI",
            14
        )
        """

        values = [

            cls._normalize(
                namespace
            )
        ]

        for part in parts:

            if part is None:

                continue

            values.append(
                cls._normalize(
                    part
                )
            )

        return "::".join(
            values
        )

    # =====================================================
    # SYMBOL KEY
    # =====================================================

    @classmethod
    def symbol_key(
        cls,
        namespace: str,
        symbol: str,
        timeframe: Optional[str] = None,
        *parts: Any,
    ) -> str:

        values: List[Any] = [
            symbol
        ]

        if timeframe:

            values.append(
                timeframe
            )

        values.extend(
            parts
        )

        return cls.build_key(
            namespace,
            *values,
        )

    # =====================================================
    # SET
    # =====================================================

    def set(
        self,
        key: str,
        value: Any,
        *,
        ttl: Optional[int] = None,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:
        """
        Store value in cache.
        """

        key = str(
            key
        ).strip()

        if not key:

            raise ValueError(
                "Cache key cannot be empty."
            )

        ttl_value = (
            self.default_ttl
            if ttl is None
            else max(
                0,
                int(ttl),
            )
        )

        now = datetime.now()

        expires_at = None

        if ttl_value > 0:

            expires_at = (
                now
                + timedelta(
                    seconds=ttl_value
                )
            )

        entry = CacheEntry(

            value=value,

            created_at=now,

            expires_at=expires_at,

            metadata=(
                dict(metadata)
                if metadata
                else {}
            ),
        )

        with self._lock:

            # Keep cache bounded.

            if (
                key not in self._cache
                and len(self._cache)
                >= self.max_entries
            ):

                self._evict_one()

            self._cache[
                key
            ] = entry

            self._stats.writes += 1

    # =====================================================
    # GET
    # =====================================================

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve cached value.
        """

        key = str(
            key
        ).strip()

        with self._lock:

            entry = self._cache.get(
                key
            )

            if entry is None:

                self._stats.misses += 1

                return default

            if entry.expired:

                del self._cache[
                    key
                ]

                self._stats.expirations += 1

                self._stats.misses += 1

                return default

            entry.hits += 1

            self._stats.hits += 1

            return entry.value

    # =====================================================
    # GET ENTRY
    # =====================================================

    def get_entry(
        self,
        key: str,
    ) -> Optional[CacheEntry]:

        key = str(
            key
        ).strip()

        with self._lock:

            entry = self._cache.get(
                key
            )

            if entry is None:

                return None

            if entry.expired:

                del self._cache[
                    key
                ]

                self._stats.expirations += 1

                return None

            return entry

    # =====================================================
    # HAS
    # =====================================================

    def has(
        self,
        key: str,
    ) -> bool:

        key = str(
            key
        ).strip()

        with self._lock:

            entry = self._cache.get(
                key
            )

            if entry is None:

                return False

            if entry.expired:

                del self._cache[
                    key
                ]

                self._stats.expirations += 1

                return False

            return True

    # =====================================================
    # DELETE
    # =====================================================

    def delete(
        self,
        key: str,
    ) -> bool:

        key = str(
            key
        ).strip()

        with self._lock:

            if key not in self._cache:

                return False

            del self._cache[
                key
            ]

            self._stats.deletions += 1

            return True

    # =====================================================
    # DELETE PREFIX
    # =====================================================

    def delete_prefix(
        self,
        prefix: str,
    ) -> int:
        """
        Delete all keys beginning with prefix.
        """

        prefix = str(
            prefix
        ).strip().upper()

        removed = 0

        with self._lock:

            keys = [

                key

                for key in self._cache

                if key.upper().startswith(
                    prefix
                )
            ]

            for key in keys:

                del self._cache[
                    key
                ]

                removed += 1

            self._stats.deletions += (
                removed
            )

        return removed

    # =====================================================
    # INVALIDATE SYMBOL
    # =====================================================

    def invalidate_symbol(
        self,
        symbol: str,
    ) -> int:
        """
        Remove all cached entries containing symbol.
        """

        token = (
            f"::{self._normalize(symbol)}"
        )

        removed = 0

        with self._lock:

            keys = [

                key

                for key in self._cache

                if token in key.upper()
            ]

            for key in keys:

                del self._cache[
                    key
                ]

                removed += 1

            self._stats.deletions += (
                removed
            )

        return removed

    # =====================================================
    # INVALIDATE TIMEFRAME
    # =====================================================

    def invalidate_timeframe(
        self,
        timeframe: str,
    ) -> int:

        token = (
            f"::{self._normalize(timeframe)}"
        )

        removed = 0

        with self._lock:

            keys = [

                key

                for key in self._cache

                if token in key.upper()
            ]

            for key in keys:

                del self._cache[
                    key
                ]

                removed += 1

            self._stats.deletions += (
                removed
            )

        return removed

    # =====================================================
    # CLEAN EXPIRED
    # =====================================================

    def cleanup(
        self,
    ) -> int:
        """
        Remove expired entries.
        """

        removed = 0

        with self._lock:

            keys = [

                key

                for key, entry
                in self._cache.items()

                if entry.expired
            ]

            for key in keys:

                del self._cache[
                    key
                ]

                removed += 1

            self._stats.expirations += (
                removed
            )

        return removed

    # =====================================================
    # EVICT ONE
    # =====================================================

    def _evict_one(
        self,
    ) -> None:
        """
        Remove one entry when cache reaches max size.

        Preference:
        1. expired entry
        2. least recently useful entry based on hits/age
        """

        if not self._cache:

            return

        expired_keys = [

            key

            for key, entry
            in self._cache.items()

            if entry.expired
        ]

        if expired_keys:

            key = expired_keys[
                0
            ]

            del self._cache[
                key
            ]

            self._stats.expirations += 1

            return

        key = min(

            self._cache,

            key=lambda item: (

                self._cache[
                    item
                ].hits,

                self._cache[
                    item
                ].created_at,
            ),
        )

        del self._cache[
            key
        ]

        self._stats.deletions += 1

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(
        self,
    ) -> None:

        with self._lock:

            self._cache.clear()

            self._stats.clears += 1

    # =====================================================
    # RESET STATISTICS
    # =====================================================

    def reset_stats(
        self,
    ) -> None:

        with self._lock:

            self._stats = (
                CacheStats()
            )

    # =====================================================
    # KEYS
    # =====================================================

    def keys(
        self,
    ) -> List[str]:

        self.cleanup()

        with self._lock:

            return list(
                self._cache.keys()
            )

    # =====================================================
    # SIZE
    # =====================================================

    @property
    def size(
        self,
    ) -> int:

        self.cleanup()

        with self._lock:

            return len(
                self._cache
            )

    # =====================================================
    # STATS
    # =====================================================

    @property
    def stats(
        self,
    ) -> Dict[str, Any]:

        with self._lock:

            data = (
                self._stats.to_dict()
            )

            data[
                "entries"
            ] = len(
                self._cache
            )

            data[
                "max_entries"
            ] = self.max_entries

            data[
                "default_ttl"
            ] = self.default_ttl

            return data

    # =====================================================
    # INFO
    # =====================================================

    def info(
        self,
    ) -> Dict[str, Any]:

        self.cleanup()

        with self._lock:

            return {

                "size":
                    len(
                        self._cache
                    ),

                "max_entries":
                    self.max_entries,

                "default_ttl":
                    self.default_ttl,

                "keys":
                    list(
                        self._cache.keys()
                    ),

                "stats":
                    self._stats.to_dict(),
            }

    # =====================================================
    # LENGTH
    # =====================================================

    def __len__(
        self,
    ) -> int:

        return self.size

    # =====================================================
    # CONTAINS
    # =====================================================

    def __contains__(
        self,
        key: object,
    ) -> bool:

        if not isinstance(
            key,
            str,
        ):

            return False

        return self.has(
            key
        )


# =========================================================
# GLOBAL CACHE
# =========================================================

scanner_cache = ScannerCache(
    default_ttl=60,
    max_entries=5000,
)


# =========================================================
# CACHE NAMESPACES
# =========================================================

CACHE_MARKET_DATA = "MARKET_DATA"

CACHE_INDICATOR = "INDICATOR"

CACHE_SCANNER = "SCANNER"

CACHE_CONTEXT = "CONTEXT"

CACHE_SECTOR = "SECTOR"

CACHE_RANKING = "RANKING"


# =========================================================
# CONVENIENCE FUNCTIONS
# =========================================================

def cache_get(
    key: str,
    default: Any = None,
) -> Any:

    return scanner_cache.get(
        key,
        default,
    )


def cache_set(
    key: str,
    value: Any,
    *,
    ttl: Optional[int] = None,
) -> None:

    scanner_cache.set(
        key,
        value,
        ttl=ttl,
    )


def cache_delete(
    key: str,
) -> bool:

    return scanner_cache.delete(
        key
    )


def clear_scanner_cache(
) -> None:

    scanner_cache.clear()


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "CacheEntry",

    "CacheStats",

    "ScannerCache",

    "scanner_cache",

    "CACHE_MARKET_DATA",

    "CACHE_INDICATOR",

    "CACHE_SCANNER",

    "CACHE_CONTEXT",

    "CACHE_SECTOR",

    "CACHE_RANKING",

    "cache_get",

    "cache_set",

    "cache_delete",

    "clear_scanner_cache",
]


# ==========================
# END OF FILE
# ==========================