"""
配置文件格式化器
保持JSON文件的字段顺序和格式
"""

import json
import os
from collections import OrderedDict
from typing import Dict, Any


class ConfigFormatter:
    """配置文件格式化器，保持字段顺序和良好的格式"""

    def __init__(self):
        # 定义配置字段的层次结构和顺序
        self.field_order = {
            # 顶级字段顺序
            'root': [
                'lua_config_path',
                'screen_resolution',
                'is_debug',
                'overlay_position',
                'vertical_sensitivity_magnification',
                'target_fps',
                'weapon_altitude',
                'weapon_screenshot_area',
                'muzzle_screenshot_area',
                'grip_screenshot_area',
                'butt_screenshot_area',
                'sight_screenshot_area',
                'muzzle_screenshot_area2',
                'grip_screenshot_area2',
                'butt_screenshot_area2',
                'sight_screenshot_area2',
                'index',
                'firearms',
                'firearms_accessories_list'
            ],
            # 截图区域字段顺序
            'screenshot_area': ['left', 'top', 'width', 'height'],
            # 武器配置字段顺序
            'firearm': ['recognition_confidence_threshold', 'coefficient_list'],
            # 配件列表字段顺序
            'accessories': ['def_muzzle', 'muzzle_list', 'grip_list', 'butt_list', 'sight_list']
        }

    def preserve_structure(self, data: Dict[str, Any], original_data: Dict[str, Any] = None) -> OrderedDict:
        """保持原始结构顺序，只对顶级字段进行基本排序"""
        if not isinstance(data, dict):
            return data

        ordered = OrderedDict()

        # 如果有原始数据，尽量保持原始顺序
        if original_data and isinstance(original_data, dict):
            # 按原始顺序添加字段
            for field in original_data.keys():
                if field in data:
                    value = data[field]
                    if isinstance(value, dict) and field in original_data and isinstance(original_data[field], dict):
                        # 递归保持嵌套结构的原始顺序
                        ordered[field] = self.preserve_structure(value, original_data[field])
                    else:
                        ordered[field] = value

            # 添加新增的字段
            for field, value in data.items():
                if field not in ordered:
                    if isinstance(value, dict):
                        ordered[field] = self.preserve_structure(value)
                    else:
                        ordered[field] = value
        else:
            # 没有原始数据时，使用预定义顺序作为参考
            field_order = self.field_order.get('root', [])

            # 按预定义顺序添加顶级字段
            for field in field_order:
                if field in data:
                    value = data[field]
                    if isinstance(value, dict):
                        if field.endswith('_screenshot_area'):
                            ordered[field] = self.preserve_screenshot_area_order(value)
                        else:
                            ordered[field] = self.preserve_structure(value)
                    else:
                        ordered[field] = value

            # 添加不在预定义顺序中的字段
            for field, value in data.items():
                if field not in ordered:
                    if isinstance(value, dict):
                        ordered[field] = self.preserve_structure(value)
                    else:
                        ordered[field] = value

        return ordered

    def preserve_screenshot_area_order(self, area_data: Dict[str, Any]) -> OrderedDict:
        """保持截图区域的标准顺序：left, top, width, height"""
        ordered = OrderedDict()
        standard_order = ['left', 'top', 'width', 'height']

        # 按标准顺序添加
        for field in standard_order:
            if field in area_data:
                ordered[field] = area_data[field]

        # 添加其他字段
        for field, value in area_data.items():
            if field not in ordered:
                ordered[field] = value

        return ordered

    def format_config(self, config: Dict[str, Any], original_config: Dict[str, Any] = None) -> OrderedDict:
        """格式化整个配置，保持原始结构顺序"""
        return self.preserve_structure(config, original_config)

    def save_config(self, config: Dict[str, Any], file_path: str, indent: int = 4):
        """保存配置到文件，保持格式和顺序"""
        # 尝试读取原始文件以保持结构
        original_config = None
        try:
            if os.path.exists(file_path):
                original_config = self.load_config(file_path)
        except:
            pass

        formatted_config = self.format_config(config, original_config)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(formatted_config, f, indent=indent, ensure_ascii=False, separators=(',', ': '))

    def load_config(self, file_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def validate_and_format(self, config: Dict[str, Any], original_config: Dict[str, Any] = None) -> tuple[
        bool, str, OrderedDict]:
        """验证并格式化配置"""
        try:
            # 基本验证
            if not isinstance(config, dict):
                return False, "配置必须是字典格式", OrderedDict()

            # 检查必需字段
            required_fields = ['lua_config_path', 'screen_resolution', 'is_debug']
            missing_fields = [field for field in required_fields if field not in config]

            if missing_fields:
                return False, f"缺少必需字段: {', '.join(missing_fields)}", OrderedDict()

            # 格式化配置，保持原始结构
            formatted_config = self.format_config(config, original_config)

            return True, "配置验证成功", formatted_config

        except Exception as e:
            return False, f"配置验证失败: {str(e)}", OrderedDict()


# 全局实例
config_formatter = ConfigFormatter()


def save_formatted_config(config: Dict[str, Any], file_path: str):
    """保存格式化的配置文件"""
    config_formatter.save_config(config, file_path)


def load_formatted_config(file_path: str) -> Dict[str, Any]:
    """加载配置文件"""
    return config_formatter.load_config(file_path)
