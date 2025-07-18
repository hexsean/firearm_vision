"""
Web配置管理器包
提供基于Web界面的配置文件管理功能
"""

from .web_config_manager import WebConfigManager, start_web_config_manager, stop_web_config_manager
from .config_formatter import ConfigFormatter, save_formatted_config, load_formatted_config

__version__ = "1.0.0"
__author__ = "Firearm Vision Team"

__all__ = [
    'WebConfigManager',
    'start_web_config_manager', 
    'stop_web_config_manager',
    'ConfigFormatter',
    'save_formatted_config',
    'load_formatted_config'
]
