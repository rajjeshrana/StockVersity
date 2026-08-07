from __future__ import annotations

import threading
import weakref
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Optional

# =====================================================
# RESOURCE
# =====================================================

@dataclass(slots=True)
class Resource:

    name: str

    path: Optional[Path] = None

    loader: Optional[Callable] = None

    data: Any = None

    loaded: bool = False

    cache: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    # -------------------------------------------------

    def load(self):

        if self.loaded:
            return self.data

        if self.loader is not None:

            self.data = self.loader()

        elif self.path is not None:

            self.data = self.path.read_bytes()

        self.loaded = True

        return self.data

    # -------------------------------------------------

    def unload(self):

        self.data = None

        self.loaded = False


# =====================================================
# RESOURCE MANAGER
# =====================================================

class ResourceManager:

    _instance = None

    _lock = threading.Lock()

    # -------------------------------------------------

    def __new__(cls):

        with cls._lock:

            if cls._instance is None:

                cls._instance = super().__new__(cls)

        return cls._instance

    # -------------------------------------------------

    def __init__(self):

        if getattr(self, "_initialized", False):
            return

        self._initialized = True

        self.resources: Dict[str, Resource] = {}

        self.cache = weakref.WeakValueDictionary()

        self.manager_lock = threading.RLock()

        self.statistics = {

            "registered": 0,

            "loaded": 0,

            "cache_hits": 0,

            "cache_misses": 0,

        }

    # =====================================================
    # REGISTER
    # =====================================================

    def register(

        self,

        name: str,

        path: Optional[Path] = None,

        loader: Optional[Callable] = None,

        cache: bool = True,

        **metadata,

    ):

        resource = Resource(

            name=name,

            path=path,

            loader=loader,

            cache=cache,

            metadata=metadata,

        )

        with self.manager_lock:

            self.resources[name] = resource

            self.statistics["registered"] += 1

        return resource

    # =====================================================
    # UNREGISTER
    # =====================================================

    def unregister(

        self,

        name: str,

    ):

        with self.manager_lock:

            resource = self.resources.pop(

                name,

                None,

            )

        if resource:

            resource.unload()

            return True

        return False

    # =====================================================
    # EXISTS
    # =====================================================

    def exists(

        self,

        name: str,

    ):

        return name in self.resources

    # =====================================================
    # GET RESOURCE
    # =====================================================

    def get(

        self,

        name: str,

    ):

        resource = self.resources.get(name)

        if resource is None:
            return None

        if resource.loaded:

            self.statistics["cache_hits"] += 1

            return resource.data

        self.statistics["cache_misses"] += 1

        data = resource.load()

        if resource.cache and data is not None:

            try:

                self.cache[name] = data

            except TypeError:
                # Object doesn't support weak references
                pass

        self.statistics["loaded"] += 1

        return data
        # =====================================================
    # RELOAD RESOURCE
    # =====================================================

    def reload(

        self,

        name: str,

    ):

        resource = self.resources.get(

            name

        )

        if resource is None:

            return None

        resource.unload()

        if name in self.cache:

            del self.cache[name]

        return self.get(

            name

        )

    # =====================================================
    # REGISTER MULTIPLE
    # =====================================================

    def register_many(

        self,

        resources: Dict[str, Path],

    ):

        for name, path in resources.items():

            self.register(

                name=name,

                path=path,

            )

        return len(

            resources

        )

    # =====================================================
    # ICONS
    # =====================================================

    def register_icon(

        self,

        name: str,

        path: Path,

    ):

        return self.register(

            name=f"icon:{name}",

            path=path,

            category="icon",

        )

    # -------------------------------------------------

    def icon(

        self,

        name: str,

    ):

        return self.get(

            f"icon:{name}"

        )

    # =====================================================
    # IMAGES
    # =====================================================

    def register_image(

        self,

        name: str,

        path: Path,

    ):

        return self.register(

            name=f"image:{name}",

            path=path,

            category="image",

        )

    # -------------------------------------------------

    def image(

        self,

        name: str,

    ):

        return self.get(

            f"image:{name}"

        )

    # =====================================================
    # FONTS
    # =====================================================

    def register_font(

        self,

        name: str,

        path: Path,

    ):

        return self.register(

            name=f"font:{name}",

            path=path,

            category="font",

        )

    # -------------------------------------------------

    def font(

        self,

        name: str,

    ):

        return self.get(

            f"font:{name}"

        )

    # =====================================================
    # STYLESHEETS
    # =====================================================

    def register_stylesheet(

        self,

        name: str,

        path: Path,

    ):

        return self.register(

            name=f"style:{name}",

            path=path,

            category="stylesheet",

        )

    # -------------------------------------------------

    def stylesheet(

        self,

        name: str,

    ):

        data = self.get(

            f"style:{name}"

        )

        if data is None:

            return None

        if isinstance(

            data,

            bytes,

        ):

            return data.decode(

                "utf-8"

            )

        return data

    # =====================================================
    # CACHE
    # =====================================================

    def clear_cache(

        self,

    ):

        self.cache.clear()

        for resource in self.resources.values():

            resource.unload()

        self.statistics["loaded"] = 0

    # -------------------------------------------------

    def cache_size(

        self,

    ):

        return len(

            self.cache

        )

    # =====================================================
    # LISTING
    # =====================================================

    def all_resources(

        self,

    ):

        return list(

            self.resources.values()

        )

    # -------------------------------------------------

    def names(

        self,

    ):

        return sorted(

            self.resources.keys()

        )

    # -------------------------------------------------

    def loaded_resources(

        self,

    ):

        return [

            resource

            for resource in self.resources.values()

            if resource.loaded

        ]
        # =====================================================
    # REMOVE BY CATEGORY
    # =====================================================

    def remove_category(

        self,

        category: str,

    ):

        removed = 0

        keys = [

            name

            for name, resource in self.resources.items()

            if resource.metadata.get(

                "category"

            ) == category

        ]

        for name in keys:

            if self.unregister(

                name

            ):

                removed += 1

        return removed

    # =====================================================
    # SEARCH
    # =====================================================

    def search(

        self,

        keyword: str,

    ):

        keyword = keyword.lower()

        return [

            resource

            for resource in self.resources.values()

            if (
                keyword in resource.name.lower()
                or keyword
                in str(resource.metadata).lower()
            )
        ]

    # =====================================================
    # FILTER
    # =====================================================

    def filter(

        self,

        **criteria,

    ):

        results = []

        for resource in self.resources.values():

            matched = True

            for key, value in criteria.items():

                if resource.metadata.get(

                    key

                ) != value:

                    matched = False

                    break

            if matched:

                results.append(

                    resource

                )

        return results

    # =====================================================
    # VALIDATE
    # =====================================================

    def validate(

        self,

    ):

        report = {

            "valid": [],

            "missing": [],

        }

        for resource in self.resources.values():

            if resource.path is None:

                report["valid"].append(

                    resource.name

                )

                continue

            if resource.path.exists():

                report["valid"].append(

                    resource.name

                )

            else:

                report["missing"].append(

                    resource.name

                )

        return report

    # =====================================================
    # MEMORY USAGE
    # =====================================================

    def memory_usage(

        self,

    ):

        total = 0

        for resource in self.resources.values():

            data = resource.data

            if data is None:

                continue

            try:

                total += len(

                    data

                )

            except Exception:

                pass

        return total

    # =====================================================
    # CLEANUP
    # =====================================================

    def cleanup(

        self,

    ):

        released = 0

        for resource in self.resources.values():

            if resource.loaded:

                resource.unload()

                released += 1

        self.cache.clear()

        self.statistics["loaded"] = 0

        return released

    # =====================================================
    # STATISTICS
    # =====================================================

    def stats(

        self,

    ):

        return {

            "registered": len(

                self.resources

            ),

            "loaded": len(

                self.loaded_resources()

            ),

            "cache_entries": self.cache_size(),

            "cache_hits": self.statistics["cache_hits"],

            "cache_misses": self.statistics["cache_misses"],

            "memory_usage": self.memory_usage(),

        }

    # =====================================================
    # SERIALIZATION
    # =====================================================

    def to_dict(

        self,

    ):

        return {

            resource.name: {

                "loaded": resource.loaded,

                "cache": resource.cache,

                "path": (
                    str(resource.path)
                    if resource.path
                    else None
                ),

                "metadata": resource.metadata,

            }

            for resource in self.resources.values()

        }

    # =====================================================
    # RESET
    # =====================================================

    def reset(

        self,

    ):

        self.cleanup()

        self.resources.clear()

        self.statistics = {

            "registered": 0,

            "loaded": 0,

            "cache_hits": 0,

            "cache_misses": 0,

        }
            # =====================================================
    # PRELOAD
    # =====================================================

    def preload(

        self,

    ):

        loaded = 0

        for name in self.names():

            try:

                self.get(name)
                loaded += 1
            except Exception:
                pass

        return loaded

    # =====================================================
    # LOAD SELECTED
    # =====================================================

    def load_many(

        self,

        names,

    ):

        loaded = []

        for name in names:

            try:

                loaded.append(

                    self.get(name)

                )

            except Exception:

                pass

        return loaded

    # =====================================================
    # UNLOAD SELECTED
    # =====================================================

    def unload_many(

        self,

        names,

    ):

        count = 0

        for name in names:

            resource = self.resources.get(

                name

            )

            if resource is None:

                continue

            resource.unload()

            self.cache.pop(

                name,

                None,

            )

            count += 1

        return count

    # =====================================================
    # STARTUP
    # =====================================================

    def startup(

        self,

        preload: bool = False,

    ):

        if preload:

            self.preload()

        return self.stats()

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(

        self,

    ):

        released = self.cleanup()

        return {

            "released": released,

            "remaining": len(

                self.resources

            ),

        }

    # =====================================================
    # EXPORT
    # =====================================================

    def export(

        self,

    ):

        return self.to_dict()

    # =====================================================
    # IMPORT
    # =====================================================

    def import_resources(

        self,

        resources: Dict[str, Dict[str, Any]],

    ):

        imported = 0

        for name, info in resources.items():

            path = info.get("path")

            metadata = info.get(

                "metadata",

                {},

            )

            self.register(

                name=name,

                path=Path(path)

                if path

                else None,

                cache=info.get(

                    "cache",

                    True,

                ),

                **metadata,

            )

            imported += 1

        return imported

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ):

        stats = self.stats()

        return (

            "ResourceManager("

            f"registered={stats['registered']}, "

            f"loaded={stats['loaded']}, "

            f"cache={stats['cache_entries']})"

        )

    # -------------------------------------------------

    def __str__(

        self,

    ):

        stats = self.stats()

        return (

            "Resource Manager\n"

            f"Registered : {stats['registered']}\n"

            f"Loaded     : {stats['loaded']}\n"

            f"Cache      : {stats['cache_entries']}\n"

            f"Hits       : {stats['cache_hits']}\n"

            f"Misses     : {stats['cache_misses']}\n"

            f"Memory     : {stats['memory_usage']} bytes"

        )


# =====================================================
# GLOBAL SINGLETON
# =====================================================

resource_manager = ResourceManager()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "Resource",

    "ResourceManager",

    "resource_manager",

]