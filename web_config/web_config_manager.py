import json
import threading
import webbrowser
from collections import OrderedDict
from flask import Flask, render_template, request, jsonify
from .config_formatter import save_formatted_config


class WebConfigManager:
    def __init__(self, config_path='config.json', port=5000, reload_callback=None):
        self.config_path = config_path
        self.port = port
        self.reload_callback = reload_callback
        self.app = Flask(__name__)
        self.setup_routes()
        self.server_thread = None
        # 定义字段顺序
        self.field_order = [
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
        ]

    def setup_routes(self):
        """设置Flask路由"""

        @self.app.route('/')
        def index():
            """主页面"""
            return render_template('config_editor.html')

        @self.app.route('/api/config', methods=['GET'])
        def get_config():
            """获取当前配置"""
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return jsonify({'success': True, 'config': config})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})

        @self.app.route('/api/config', methods=['POST'])
        def save_config():
            """保存配置"""
            try:
                config_data = request.json

                # 验证配置数据
                validation_result = self.validate_config(config_data)
                if not validation_result['valid']:
                    return jsonify({
                        'success': False,
                        'error': f"配置验证失败: {validation_result['error']}"
                    })

                # 使用格式化器保存配置，保持字段顺序和格式
                save_formatted_config(config_data, self.config_path)

                # 触发配置重载
                if self.reload_callback:
                    self.reload_callback()

                return jsonify({'success': True, 'message': '配置已保存并重载'})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})

        @self.app.route('/api/config/validate', methods=['POST'])
        def validate_config_endpoint():
            """验证配置"""
            try:
                config_data = request.json
                result = self.validate_config(config_data)
                return jsonify(result)
            except Exception as e:
                return jsonify({'valid': False, 'error': str(e)})

    def reorder_config(self, config):
        """按预定义顺序重新排列配置字段"""
        ordered_config = OrderedDict()

        # 按预定义顺序添加字段
        for field in self.field_order:
            if field in config:
                ordered_config[field] = config[field]

        # 添加任何不在预定义顺序中的字段
        for field, value in config.items():
            if field not in ordered_config:
                ordered_config[field] = value

        return ordered_config

    def validate_config(self, config):
        """验证配置数据"""
        try:
            # 检查必需的字段
            required_fields = [
                'lua_config_path', 'screen_resolution', 'is_debug',
                'overlay_position', 'vertical_sensitivity_magnification',
                'target_fps', 'weapon_altitude'
            ]

            for field in required_fields:
                if field not in config:
                    return {'valid': False, 'error': f'缺少必需字段: {field}'}

            # 检查数据类型
            if not isinstance(config['screen_resolution'], list) or len(config['screen_resolution']) != 2:
                return {'valid': False, 'error': '屏幕分辨率必须是包含两个数字的数组'}

            if not isinstance(config['overlay_position'], list) or len(config['overlay_position']) != 2:
                return {'valid': False, 'error': '覆盖层位置必须是包含两个数字的数组'}

            if not isinstance(config['is_debug'], bool):
                return {'valid': False, 'error': 'is_debug必须是布尔值'}

            if not isinstance(config['target_fps'], (int, float)) or config['target_fps'] <= 0:
                return {'valid': False, 'error': '目标FPS必须是正数'}

            # 检查截图区域
            screenshot_areas = [
                'weapon_screenshot_area', 'muzzle_screenshot_area',
                'grip_screenshot_area', 'butt_screenshot_area', 'sight_screenshot_area'
            ]

            for area in screenshot_areas:
                if area in config:
                    area_data = config[area]
                    if not isinstance(area_data, dict):
                        return {'valid': False, 'error': f'{area}必须是对象'}

                    required_area_fields = ['left', 'top', 'width', 'height']
                    for field in required_area_fields:
                        if field not in area_data:
                            return {'valid': False, 'error': f'{area}缺少字段: {field}'}
                        if not isinstance(area_data[field], (int, float)):
                            return {'valid': False, 'error': f'{area}.{field}必须是数字'}

            return {'valid': True}

        except Exception as e:
            return {'valid': False, 'error': str(e)}

    def start_server(self):
        """启动Web服务器"""
        if self.server_thread and self.server_thread.is_alive():
            return

        def run_server():
            self.app.run(host='127.0.0.1', port=self.port, debug=False, use_reloader=False)

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()

        # 等待服务器启动
        threading.Timer(1.0, self.open_browser).start()

        print(f"> 配置管理Web界面已启动: http://127.0.0.1:{self.port}")

    def open_browser(self):
        """打开浏览器"""
        try:
            webbrowser.open(f'http://127.0.0.1:{self.port}')
        except Exception as e:
            print(f"> 无法自动打开浏览器: {e}")
            print(f"> 请手动访问: http://127.0.0.1:{self.port}")

    def stop_server(self):
        """停止Web服务器"""
        # Flask开发服务器没有优雅的停止方法，这里只是标记线程为daemon
        # 当主程序退出时会自动结束
        pass


# 全局实例
web_config_manager = None


def start_web_config_manager(config_path='config.json', port=5000, reload_callback=None):
    """启动Web配置管理器"""
    global web_config_manager
    if web_config_manager is None:
        web_config_manager = WebConfigManager(config_path, port, reload_callback)
        web_config_manager.start_server()
    return web_config_manager


def stop_web_config_manager():
    """停止Web配置管理器"""
    global web_config_manager
    if web_config_manager:
        web_config_manager.stop_server()
        web_config_manager = None
