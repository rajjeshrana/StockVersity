from __future__ import annotations

import threading
import time
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from collections import OrderedDict
from functools import wraps
from typing import Any, Callable


class CacheItem:

    def __init__(
        self,
        value: Any,
        expires_at: datetime,
    ):

        self.value = value

        self.expires_at = expires_at

        self.created_at = datetime.now()

        self.last_access = datetime.now()

        self.hits = 0

    # -------------------------------------------------

    @property
    def expired(self):

        return datetime.now() >= self.expires_at

    # -------------------------------------------------

    def touch(self):

        self.last_access = datetime.now()

        self.hits += 1


# =====================================================
# CACHE SERVICE
# =====================================================

class CacheService:

    """
    Thread-safe in-memory cache with:

    • TTL
    • LRU eviction
    • Persistence
    • Statistics
    """

    DEFAULT_TTL = 300

    DEFAULT_MAX_ITEMS = 5000

    # -------------------------------------------------

    def __init__(

        self,

        ttl=DEFAULT_TTL,

        max_items=DEFAULT_MAX_ITEMS,

    ):

        self.ttl = ttl

        self.max_items = max_items

        self.lock = threading.RLock()

        self.cache = OrderedDict()

        self.stats = {

            "hits": 0,

            "miss": 0,

            "evictions": 0,

            "expired": 0,

            "sets": 0,

            "deletes": 0,

        }

    # =====================================================
    # BASIC
    # =====================================================

    def __len__(self):

        return len(self.cache)

    # -------------------------------------------------

    def __contains__(

        self,

        key,

    ):

        return key in self.cache

    # -------------------------------------------------

    def keys(self):

        return list(

            self.cache.keys()

        )

    # -------------------------------------------------

    def values(self):

        return [

            item.value

            for item in self.cache.values()

        ]

    # -------------------------------------------------

    def items(self):

        return [

            (

                key,

                item.value,

            )

            for key, item

            in self.cache.items()

        ]

    # =====================================================
    # SET
    # =====================================================

    def set(

        self,

        key,

        value,

        ttl=None,

    ):

        ttl = ttl or self.ttl

        with self.lock:

            if key in self.cache:

                del self.cache[key]

            self.cache[key] = CacheItem(

                value=value,

                expires_at=datetime.now()

                + timedelta(

                    seconds=ttl

                ),

            )

            self.cache.move_to_end(key)

            self.stats["sets"] += 1

            self._evict()

    # =====================================================
    # GET
    # =====================================================

    def get(

        self,

        key,

        default=None,

    ):

        with self.lock:

            item = self.cache.get(

                key

            )

            if item is None:

                self.stats["miss"] += 1

                return default

            if item.expired:

                del self.cache[key]

                self.stats["expired"] += 1

                self.stats["miss"] += 1

                return default

            item.touch()

            self.cache.move_to_end(key)

            self.stats["hits"] += 1

            return item.value

    # =====================================================
    # DELETE
    # =====================================================

    def delete(

        self,

        key,

    ):

        with self.lock:

            if key in self.cache:

                del self.cache[key]

                self.stats["deletes"] += 1

    # -------------------------------------------------

    def clear(self):

        with self.lock:

            self.cache.clear()

    # =====================================================
    # EXISTS
    # =====================================================

    def exists(

        self,

        key,

    ):

        return self.get(

            key

        ) is not None

    # =====================================================
    # EVICTION
    # =====================================================

    def _evict(self):

        while len(

            self.cache

        ) > self.max_items:

            self.cache.popitem(

                last=False

            )

            self.stats["evictions"] += 1

    # =====================================================
    # CLEANUP
    # =====================================================

    def cleanup(self):

        expired = []

        with self.lock:

            for key, item in list(

                self.cache.items()

            ):

                if item.expired:

                    expired.append(key)

            for key in expired:

                del self.cache[key]

                self.stats["expired"] += 1

        return len(expired)
        # =====================================================
    # PERSISTENCE
    # =====================================================

    def save(
        self,
        filename,
    ):

        with self.lock:

            data = {

                key: item

                for key, item in self.cache.items()

                if not item.expired

            }

            with open(
                Path(filename),
                "wb",
            ) as file:

                pickle.dump(
                    data,
                    file,
                )

    # -------------------------------------------------

    def load(
        self,
        filename,
    ):

        path = Path(filename)

        if not path.exists():

            return 0

        with open(
            path,
            "rb",
        ) as file:

            data = pickle.load(file)

        with self.lock:

            self.cache = OrderedDict(data)

        self.cleanup()

        return len(self.cache)

    # =====================================================
    # BULK OPERATIONS
    # =====================================================

    def set_many(
        self,
        mapping,
        ttl=None,
    ):

        for key, value in mapping.items():

            self.set(
                key,
                value,
                ttl,
            )

    # -------------------------------------------------

    def get_many(
        self,
        keys,
    ):

        return {

            key: self.get(key)

            for key in keys

        }

    # -------------------------------------------------

    def delete_many(
        self,
        keys,
    ):

        for key in keys:

            self.delete(key)

    # =====================================================
    # TTL
    # =====================================================

    def extend(
        self,
        key,
        seconds,
    ):

        with self.lock:

            item = self.cache.get(key)

            if item is None:

                return False

            item.expires_at += timedelta(
                seconds=seconds
            )

            return True

    # -------------------------------------------------

    def ttl(
        self,
        key,
    ):

        item = self.cache.get(key)

        if item is None:

            return None

        remaining = (

            item.expires_at

            - datetime.now()

        ).total_seconds()

        return max(
            0,
            int(remaining),
        )

    # =====================================================
    # MEMORY
    # =====================================================

    def approximate_size(self):

        size = 0

        for key, item in self.cache.items():

            try:

                size += len(

                    pickle.dumps(

                        (

                            key,

                            item.value,

                        )

                    )

                )

            except Exception:

                pass

        return size

    # =====================================================
    # STATISTICS
    # =====================================================

    def statistics(self):

        return {

            **self.stats,

            "items": len(self.cache),

            "max_items": self.max_items,

            "ttl": self.ttl,

            "memory_bytes": self.approximate_size(),

        }

    # -------------------------------------------------

    def hit_ratio(self):

        total = (

            self.stats["hits"]

            + self.stats["miss"]

        )

        if total == 0:

            return 0.0

        return round(

            self.stats["hits"]

            / total

            * 100,

            2,

        )

    # =====================================================
    # AUTO CLEANUP
    # =====================================================

    def start_cleanup_thread(

        self,

        interval=60,

    ):

        thread = threading.Thread(

            target=self._cleanup_loop,

            args=(interval,),

            daemon=True,

        )

        thread.start()

        return thread

    # -------------------------------------------------

    def _cleanup_loop(

        self,

        interval,

    ):

        while True:

            try:

                self.cleanup()

            except Exception:

                pass

            time.sleep(interval)

    # =====================================================
    # CACHE DECORATOR
    # =====================================================

    def cached(

        self,

        ttl=None,

    ):

        def decorator(func):

            @wraps(func)

            def wrapper(

                *args,

                **kwargs,

            ):

                key = (

                    func.__name__,

                    args,

                    tuple(

                        sorted(

                            kwargs.items()

                        )

                    ),

                )

                cached = self.get(key)

                if cached is not None:

                    return cached

                result = func(

                    *args,

                    **kwargs,

                )

                self.set(

                    key,

                    result,

                    ttl,

                )

                return result

            return wrapper

        return decorator
        # =====================================================
    # PRUNING
    # =====================================================

    def prune(
        self,
        keep=1000,
    ):

        """
        Keep only the newest 'keep' cache items.
        """

        with self.lock:

            while len(self.cache) > keep:

                self.cache.popitem(last=False)

                self.stats["evictions"] += 1

        return len(self.cache)

    # -------------------------------------------------

    def expired_keys(self):

        now = datetime.now()

        return [

            key

            for key, item in self.cache.items()

            if item.expires_at <= now

        ]

    # -------------------------------------------------

    def active_keys(self):

        now = datetime.now()

        return [

            key

            for key, item in self.cache.items()

            if item.expires_at > now

        ]

    # =====================================================
    # IMPORT / EXPORT
    # =====================================================

    def export_dict(self):

        result = {}

        now = datetime.now()

        for key, item in self.cache.items():

            if item.expires_at <= now:

                continue

            result[key] = {

                "value": item.value,

                "created_at": item.created_at.isoformat(),

                "last_access": item.last_access.isoformat(),

                "expires_at": item.expires_at.isoformat(),

                "hits": item.hits,

            }

        return result

    # -------------------------------------------------

    def import_dict(
        self,
        data,
    ):

        self.clear()

        now = datetime.now()

        with self.lock:

            for key, value in data.items():

                expires = datetime.fromisoformat(
                    value["expires_at"]
                )

                if expires <= now:

                    continue

                item = CacheItem(

                    value=value["value"],

                    expires_at=expires,

                )

                item.created_at = datetime.fromisoformat(
                    value["created_at"]
                )

                item.last_access = datetime.fromisoformat(
                    value["last_access"]
                )

                item.hits = value["hits"]

                self.cache[key] = item

    # =====================================================
    # RESET
    # =====================================================

    def reset_statistics(self):

        self.stats = {

            "hits": 0,

            "miss": 0,

            "evictions": 0,

            "expired": 0,

            "sets": 0,

            "deletes": 0,

        }

    # -------------------------------------------------

    def reset(self):

        with self.lock:

            self.clear()

            self.reset_statistics()

    # =====================================================
    # CONTEXT MANAGER
    # =====================================================

    def __enter__(self):

        return self

    # -------------------------------------------------

    def __exit__(

        self,

        exc_type,

        exc,

        traceback,

    ):

        self.cleanup()

        return False

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (

            "CacheService("

            f"items={len(self.cache)}, "

            f"hits={self.stats['hits']}, "

            f"miss={self.stats['miss']}, "

            f"hit_ratio={self.hit_ratio()}%)"

        )

    # -------------------------------------------------

    def __str__(self):

        stats = self.statistics()

        return (

            f"Cache Items : {stats['items']}\n"

            f"Hits        : {stats['hits']}\n"

            f"Misses      : {stats['miss']}\n"

            f"Hit Ratio   : {self.hit_ratio()}%\n"

            f"Memory      : {stats['memory_bytes']} bytes"

        )


# =====================================================
# GLOBAL CACHE INSTANCE
# =====================================================

default_cache = CacheService()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "CacheItem",

    "CacheService",

    "default_cache",

]