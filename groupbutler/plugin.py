"""
contains implementation of the plugin system
"""

import abc

class StopProcessing(Exception):
    """exception raised to stop processing of the message immediately"""

def register_command(command_name):
    """register a command to be called when a message with the given command
    arrives"""
    def decorator(method):
        # store the method in the list of commands availble in the plugin
        method.__gb_command__ = (command_name, method)

        return method

    return decorator

def register_message_handler(command):
    """register a function to be called when *any* message arrives

    NOTE: this can only be called once per plugin"""
    def decorator(method):
        # store the method in the list of commands availble in the plugin
        method.__gb_message_handler__ = True
        print(dir(method))

    return decorator

class _PluginMetaclass(abc.ABCMeta):
    """Metaclass to customize the creation of plugin classes"""
    def __new__(mcs, name, bases, namespace, **kwargs):
        # The abstract "Plugin" class has no base classes. This means if
        # the bases variable is not empty, this is not the "Plugin" class,
        # since it has a base class. This feels hacky, is there any better
        # way?
        if bases:
            namespace["name"] = name.lower().replace("plugin", "")
            namespace["__gb_commands__"] = {}

            for value in namespace.values():
                # try to get the marker attribute (with default value None)
                command = getattr(value, "__gb_command__", None)
                if command:
                    namespace["__gb_commands__"][command[0]] = command[1]

        return super().__new__(mcs, name, bases, namespace)

class Plugin(metaclass=_PluginMetaclass):
    """Abstract Base Class of plugins"""
    name = None
    __gb_commands__ = {}
    __gb_message_handlers__ = []

    def __init__(self, tgapi: "TelegramAPI", storage: "Storage"):
        self.tgapi = tgapi
        self.storage = storage

class PluginRegistry:
    """the plugin registry registers the commands and callback handlers of
    plugins"""

    def __init__(self):
        self.plugins = {}
        self._command_handlers_cache = {}
        self._message_handlers_cache = []

    def register(self, plugin):
        """decorator used to register a plugin"""
        self.plugins[plugin.name] = plugin

    def _update_caches(self):
        print(self.plugins)
        commands = {}
        message_handlers = []
        for plugin in self.plugins.values():
            # merge all of the plugin command dicts
            commands.update(plugin.__gb_commands__)
            # merge all of the plugin message handler lists
            message_handlers.extend(plugin.__gb_message_handlers__)

        print(commands)
        self._command_handlers_cache = commands

    def get_command_handler(self, command):
        self._update_caches()
        return self._command_handlers_cache.get(command)

    def get_message_handlers(self):
        self._update_caches()
        return self._message_handlers_cache

# The global PluginRegisty
registry = PluginRegistry()  # pylint: disable=invalid-name
