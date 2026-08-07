from __future__ import annotations

import importlib
import inspect
import pkgutil
import threading

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from backend.core.event_bus import event_bus

# =====================================================
# PLUGIN
# =====================================================

@dataclass(slots=True)
class Plugin:

    name: str
    version: str = "1.0.0"
    author: str = ""
    description: str = ""
    enabled: bool = True
    loaded: bool = False
    module: Any = None
    instance: Any = None
    dependencies: List[str] = field(default_factory=list)

    def on_load(self):
        pass

    def on_enable(self):
        pass

    def on_disable(self):
        pass

    def on_unload(self):
        pass


# =====================================================
# PLUGIN MANAGER
# =====================================================

class PluginManager:

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, plugin_directory: Optional[Path] = None):

        if getattr(self, "_initialized", False):
            return

        self._initialized = True

        self.plugin_directory = (
            plugin_directory
            or Path(__file__).resolve().parents[1] / "plugins"
        )

        self.plugin_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.plugins: Dict[str, Plugin] = {}

        self.manager_lock = threading.RLock()
            # =====================================================
    # DISCOVER PLUGINS
    # =====================================================

    def discover(self):

        """
        Discover all plugins inside the
        backend/plugins directory.
        """

        discovered = []

        with self.manager_lock:

            for module_info in pkgutil.iter_modules(

                [str(self.plugin_directory)]

            ):

                discovered.append(

                    module_info.name

                )

        return discovered

    # =====================================================
    # REGISTER
    # =====================================================

    def register(

        self,

        plugin: Plugin,

    ):

        with self.manager_lock:

            self.plugins[

                plugin.name

            ] = plugin

        event_bus.emit(

            "plugin_registered",

            plugin=plugin.name,

        )

        return plugin

    # =====================================================
    # UNREGISTER
    # =====================================================

    def unregister(

        self,

        plugin_name: str,

    ):

        with self.manager_lock:

            plugin = self.plugins.pop(

                plugin_name,

                None,

            )

        if plugin:

            event_bus.emit(

                "plugin_unregistered",

                plugin=plugin_name,

            )

            return True

        return False

    # =====================================================
    # LOAD MODULE
    # =====================================================

    def load(

        self,

        module_name: str,

    ):

        with self.manager_lock:

            if module_name in self.plugins:

                return self.plugins[module_name]

            module = importlib.import_module(

                f"backend.plugins.{module_name}"

            )

            plugin_class = None

            for _, obj in inspect.getmembers(

                module,

                inspect.isclass,

            ):

                if (

                    issubclass(

                        obj,

                        Plugin,

                    )

                    and obj is not Plugin

                ):

                    plugin_class = obj

                    break

            if plugin_class is None:

                raise RuntimeError(

                    f"No Plugin subclass found in {module_name}"

                )

            plugin = plugin_class()

            plugin.module = module

            plugin.loaded = True

            plugin.on_load()

            self.register(

                plugin

            )

            event_bus.emit(

                "plugin_loaded",

                plugin=plugin.name,

            )

            return plugin

    # =====================================================
    # LOAD ALL
    # =====================================================

    def load_all(self):

        loaded = []

        for module in self.discover():

            try:

                loaded.append(

                    self.load(

                        module

                    )

                )

            except Exception:

                pass

        return loaded

    # =====================================================
    # GET
    # =====================================================

    def get(

        self,

        name: str,

    ) -> Optional[Plugin]:

        return self.plugins.get(

            name

        )

    # =====================================================
    # EXISTS
    # =====================================================

    def exists(

        self,

        name: str,

    ):

        return name in self.plugins

    # =====================================================
    # LIST
    # =====================================================

    def all_plugins(

        self,

    ):

        return list(

            self.plugins.values()

        )

    # -------------------------------------------------

    def enabled_plugins(

        self,

    ):

        return [

            plugin

            for plugin in self.plugins.values()

            if plugin.enabled

        ]

    # -------------------------------------------------

    def disabled_plugins(

        self,

    ):

        return [

            plugin

            for plugin in self.plugins.values()

            if not plugin.enabled

        ]
        # =====================================================
    # ENABLE
    # =====================================================

    def enable(

        self,

        plugin_name: str,

    ):

        plugin = self.get(

            plugin_name

        )

        if plugin is None:

            return False

        if plugin.enabled:

            return True

        self._check_dependencies(

            plugin

        )

        plugin.enabled = True

        plugin.on_enable()

        event_bus.emit(

            "plugin_enabled",

            plugin=plugin.name,

        )

        return True

    # =====================================================
    # DISABLE
    # =====================================================

    def disable(

        self,

        plugin_name: str,

    ):

        plugin = self.get(

            plugin_name

        )

        if plugin is None:

            return False

        if not plugin.enabled:

            return True

        plugin.on_disable()

        plugin.enabled = False

        event_bus.emit(

            "plugin_disabled",

            plugin=plugin.name,

        )

        return True

    # =====================================================
    # UNLOAD
    # =====================================================

    def unload(

        self,

        plugin_name: str,

    ):

        plugin = self.get(

            plugin_name

        )

        if plugin is None:

            return False

        try:

            if plugin.enabled:

                plugin.on_disable()

                plugin.enabled = False

        except Exception:

            pass

        try:

            plugin.on_unload()

        except Exception:

            pass

        plugin.loaded = False

        self.unregister(

            plugin_name

        )

        event_bus.emit(

            "plugin_unloaded",

            plugin=plugin_name,

        )

        return True

    # =====================================================
    # RELOAD
    # =====================================================

    def reload(

        self,

        plugin_name: str,

    ):

        plugin = self.get(

            plugin_name

        )

        if plugin is None:

            return None

        module = plugin.module

        self.unload(

            plugin_name

        )

        importlib.reload(

            module

        )

        return self.load(

            module.__name__.split(

                "."

            )[-1]

        )

    # =====================================================
    # DEPENDENCIES
    # =====================================================

    def _check_dependencies(

        self,

        plugin: Plugin,

    ):

        missing = []

        for dependency in plugin.dependencies:

            dependency_plugin = self.get(

                dependency

            )

            if (

                dependency_plugin is None

                or not dependency_plugin.enabled

            ):

                missing.append(

                    dependency

                )

        if missing:

            raise RuntimeError(

                "Missing plugin dependencies: "

                + ", ".join(

                    missing

                )

            )

        return True

    # =====================================================
    # HOOKS
    # =====================================================

    def call_hook(

        self,

        hook_name: str,

        *args,

        **kwargs,

    ):

        results = []

        for plugin in self.enabled_plugins():

            method = getattr(

                plugin,

                hook_name,

                None,

            )

            if callable(

                method

            ):

                try:

                    results.append(

                        method(

                            *args,

                            **kwargs,

                        )

                    )

                except Exception:

                    event_bus.emit(

                        "plugin_error",

                        plugin=plugin.name,

                        hook=hook_name,

                    )

        return results

    # =====================================================
    # STATISTICS
    # =====================================================

    def statistics(

        self,

    ):

        return {

            "plugins": len(

                self.plugins

            ),

            "enabled": len(

                self.enabled_plugins()

            ),

            "disabled": len(

                self.disabled_plugins()

            ),

            "loaded": sum(

                plugin.loaded

                for plugin in self.plugins.values()

            ),

        }
        # =====================================================
    # SEARCH
    # =====================================================

    def find(

        self,

        keyword: str,

    ):

        keyword = keyword.lower()

        return [

            plugin

            for plugin in self.plugins.values()

            if (
                keyword in plugin.name.lower()
                or keyword in plugin.description.lower()
                or keyword in plugin.author.lower()
            )
        ]

    # =====================================================
    # BULK OPERATIONS
    # =====================================================

    def enable_all(

        self,

    ):

        enabled = 0

        for plugin in self.plugins.values():

            try:

                if self.enable(

                    plugin.name,

                ):

                    enabled += 1

            except Exception:

                pass

        return enabled

    # -------------------------------------------------

    def disable_all(

        self,

    ):

        disabled = 0

        for plugin in self.plugins.values():

            try:

                if self.disable(

                    plugin.name,

                ):

                    disabled += 1

            except Exception:

                pass

        return disabled

    # =====================================================
    # STARTUP
    # =====================================================

    def startup(

        self,

    ):

        plugins = self.load_all()

        self.enable_all()

        event_bus.emit(

            "plugins_started",

            count=len(

                plugins

            ),

        )

        return plugins

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(

        self,

    ):

        for plugin in list(

            self.plugins.values()

        ):

            try:

                self.unload(

                    plugin.name

                )

            except Exception:

                pass

        event_bus.emit(

            "plugins_shutdown"

        )

    # =====================================================
    # RELOAD ALL
    # =====================================================

    def reload_all(

        self,

    ):

        reloaded = []

        for plugin in list(

            self.plugins.values()

        ):

            try:

                reloaded.append(

                    self.reload(

                        plugin.name

                    )

                )

            except Exception:

                pass

        return reloaded

    # =====================================================
    # REMOVE ALL
    # =====================================================

    def clear(

        self,

    ):

        self.shutdown()

        self.plugins.clear()

    # =====================================================
    # SERIALIZATION
    # =====================================================

    def to_dict(

        self,

    ):

        return {

            plugin.name: {

                "version": plugin.version,

                "author": plugin.author,

                "description": plugin.description,

                "enabled": plugin.enabled,

                "loaded": plugin.loaded,

                "dependencies": plugin.dependencies,

            }

            for plugin in self.plugins.values()

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ):

        stats = self.statistics()

        return (

            "PluginManager("

            f"plugins={stats['plugins']}, "

            f"enabled={stats['enabled']}, "

            f"loaded={stats['loaded']})"

        )

    # -------------------------------------------------

    def __str__(

        self,

    ):

        stats = self.statistics()

        return (

            "Plugin Manager\n"

            f"Plugins  : {stats['plugins']}\n"

            f"Enabled  : {stats['enabled']}\n"

            f"Disabled : {stats['disabled']}\n"

            f"Loaded   : {stats['loaded']}"

        )


# =====================================================
# GLOBAL SINGLETON
# =====================================================

plugin_manager = PluginManager()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "Plugin",

    "PluginManager",

    "plugin_manager",

]