"""Handles loading of plugins."""

import inspect
import os
import sys
from pathlib import Path
from typing import List
from zipimport import zipimporter

from auto_gpt_plugin_template import AutoGPTPluginTemplate

from autogpt.config.config import Config
from autogpt.logs import logger
from autogpt.models.base_open_ai_plugin import BaseOpenAIPlugin
from autogpt.plugins import (
    inspect_zip_for_modules,
    fetch_openai_plugins_manifest_and_spec,
    initialize_openai_plugins,
)


def scan_plugins(cfg: Config, debug: bool = False) -> List[AutoGPTPluginTemplate]:
    """Scan the plugins directory for plugins and loads them.

    Args:
        cfg (Config): Config instance including plugins config
        debug (bool, optional): Enable debug logging. Defaults to False.

    Returns:
        List[Tuple[str, Path]]: List of plugins.
    """
    loaded_plugins = []
    # Generic plugins
    plugins_path_path = Path(cfg.plugins_dir)
    plugins_config = cfg.plugins_config

    # Directory-based plugins
    for plugin_path in [f.path for f in os.scandir(cfg.plugins_dir) if f.is_dir()]:
        # Avoid going into __pycache__ or other hidden directories
        if plugin_path.startswith("__"):
            continue

        plugin_module_path = plugin_path.split(os.path.sep)
        plugin_module_name = plugin_module_path[-1]
        qualified_module_name = ".".join(plugin_module_path)

        __import__(qualified_module_name)
        plugin = sys.modules[qualified_module_name]

        if not plugins_config.is_enabled(plugin_module_name):
            logger.warn(f"Plugin {plugin_module_name} found but not configured")
            continue

        for _, class_obj in inspect.getmembers(plugin):
            if hasattr(class_obj, "_abc_impl") and AutoGPTPluginTemplate in class_obj.__bases__:
                loaded_plugins.append(class_obj())

    # Zip-based plugins
    for plugin in plugins_path_path.glob("*.zip"):
        if moduleList := inspect_zip_for_modules(str(plugin), debug):
            for module in moduleList:
                plugin = Path(plugin)
                module = Path(module)
                logger.debug(f"Plugin: {plugin} Module: {module}")
                zipped_package = zipimporter(str(plugin))
                zipped_module = zipped_package.load_module(str(module.parent))

                for key in dir(zipped_module):
                    if key.startswith("__"):
                        continue
                    a_module = getattr(zipped_module, key)
                    a_keys = dir(a_module)
                    if "_abc_impl" in a_keys and a_module.__name__ != "AutoGPTPluginTemplate":
                        plugin_name = a_module.__name__
                        plugin_configured = plugins_config.get(plugin_name) is not None
                        plugin_enabled = plugins_config.is_enabled(plugin_name)

                        if plugin_configured and plugin_enabled:
                            logger.debug(f"Loading plugin {plugin_name} as it was enabled in config.")
                            loaded_plugins.append(a_module())
                        elif plugin_configured and not plugin_enabled:
                            logger.debug(f"Not loading plugin {plugin_name} as it was disabled in config.")
                        # elif not plugin_configured:
                        #     logger.warn(
                        #         f"Not loading plugin {plugin_name} as it was not found in config. "
                        #         f"Please check your config. Starting with 0.4.1, plugins will not be loaded unless "
                        #         f"they are enabled in plugins_config.yaml. Zipped plugins should use the class "
                        #         f"name ({plugin_name}) as the key."
                        #     )

    # OpenAI plugins
    if cfg.plugins_openai:
        manifests_specs = fetch_openai_plugins_manifest_and_spec(cfg)
        if manifests_specs.keys():
            manifests_specs_clients = initialize_openai_plugins(manifests_specs, cfg, debug)
            for url, openai_plugin_meta in manifests_specs_clients.items():
                if not plugins_config.is_enabled(url):
                    logger.warn(f"Plugin {plugin_module_name} found but not configured")
                    continue

                plugin = BaseOpenAIPlugin(openai_plugin_meta)
                loaded_plugins.append(plugin)

    # if loaded_plugins:
    #     logger.info(f"\nPlugins found: {len(loaded_plugins)}\n" "--------------------")
    # for plugin in loaded_plugins:
    #     logger.info(f"{plugin._name}: {plugin._version} - {plugin._description}")
    return loaded_plugins
