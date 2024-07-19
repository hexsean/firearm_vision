from datetime import datetime
from typing import List

import mss
import numpy as np
import cv2
import time
import threading
import os
import json
from pynput import keyboard
import tkinter as tk
from text_overlay import TextOverlay


# =========================================>> 加载动态配置 <<============================================
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)


config = load_config()


# 获取lua脚本读取的配置文件路径
def get_lua_config_path():
    return config["lua_config_path"]


# 获取屏幕高度(像素)
def get_screen_height():
    return config["screen_resolution"][1]


# 是否开启监控
def is_open_overlay():
    return config["is_open_overlay"]


# 是否开启按键截图
def is_open_screenshot_of_keystrokes():
    return config["is_open_screenshot_of_keystrokes"][1]


# 获取武器截图区域(left, top, width, height)
def get_weapon_screenshot_area():
    return config["weapon_screenshot_area"]


# 获取1号位武器配件=> 枪口 =>截图区域(left, top, width, height)
def get_muzzle_screenshot_area():
    return config["muzzle_screenshot_area"]


# 获取1号位武器配件=> 握把 =>截图区域(left, top, width, height)
def get_grip_screenshot_area():
    return config["grip_screenshot_area"]


# 获取1号位武器配件=> 枪托 =>截图区域(left, top, width, height)
def get_butt_screenshot_area():
    return config["butt_screenshot_area"]


# 获取1号位武器配件=> 瞄准镜 =>截图区域(left, top, width, height)
def get_sight_screenshot_area():
    return config["sight_screenshot_area"]


# 获取武器识别置信度阈值(按武器名小写)
def get_weapon_recognition_confidence_threshold():
    return config["weapon_recognition_confidence_threshold"]


# 获取垂直灵敏度倍率
def get_vertical_sensitivity_magnification():
    return config["weapon_recognition_confidence_threshold"]


# =========================================>> 初始化静态配置 <<============================================


# 当前佩戴的武器名称
last_weapon_name = 'None'

# 当前枪口配件名称
last_muzzle_name = 'None'

# 当前握把配件名称
last_grip_name = 'None'

# 当前枪托配件名称
last_butt_name = 'None'

# 当前瞄准镜配件名称
last_sight_name = 'None'

# 姿势状态: 1-站立, 2-蹲下, 3-趴下
posture_state = 1

# 状态词典
state_dict = {}

# 枪械列表
firearm_list = ['akm',
                'qbz',
                'm762',
                'groza',
                'scarl',
                'm16a4',
                'aug',
                'm416',
                'k2',
                'g36c',
                'mk47',
                'ace32',
                'uzi',
                'ump45',
                'mp5k',
                'pp19',
                'vkt',
                'tmx',
                'p90',
                'mp9',
                'm249',
                'dp28',
                'mg3',
                'famae']

# 各枪械基础系数[基础系数, 站立系数, 蹲下系数, 趴下系数]
firearm_coefficient_list = {
    'akm': [1, 1, 1, 1],
    'qbz': [1, 1, 1, 1],
    'm762': [1, 1, 1, 1],
    'groza': [1, 1, 1, 1],
    'scarl': [1, 1, 1, 1],
    'm16a4': [1, 1, 1, 1],
    'aug': [1, 1, 1, 1],
    'm416': [1, 1, 1, 1],
    'k2': [1, 1, 1, 1],
    'g36c': [1, 1, 1, 1],
    'mk47': [1, 1, 1, 1],
    'ace32': [1, 1, 1, 1],
    'uzi': [1, 1, 1, 1],
    'ump45': [1, 1, 1, 1],
    'mp5k': [1, 1, 1, 1],
    'pp19': [1, 1, 1, 1],
    'vkt': [1, 1, 1, 1],
    'tmx': [1, 1, 1, 1],
    'p90': [1, 1, 1, 1],
    'mp9': [1, 1, 1, 1],
    'm249': [1, 1, 1, 1],
    'dp28': [1, 1, 1, 1],
    'mg3': [1, 1, 1, 1],
    'famae': [1, 1, 1, 1],
}


# 枪口列表(无, 步枪消焰, 步枪补偿, 步枪消音)
muzzle_list = ['xiaoyan', 'buchang', 'xiaoyin']
muzzle_coefficient_list = {
    'xiaoyan': 0.9,
    'buchang': 0.85,
    'xiaoyin': 1,
}

# 握把列表(无, 半截式握把, 轻型握把, 垂直握把, 拇指握把, 三角握把)
grip_list = ['banjie', 'qingxing', 'chuizhi', 'muzhi', 'sanjiao']
grip_coefficient_list = {
    'banjie': 0.92,
    'qingxing': 1,
    'chuizhi': 0.85,
    'muzhi': 0.92,
    'sanjiao': 1,
}

# 枪托列表(无, 战术枪托, 重型枪托)
butt_list = ['zhongxing', 'zhanshu']
butt_coefficient_list = {
    'zhongxing': 1,
    'zhanshu': 1,
}

# 瞄准镜列表(无, 红点, 全息, 二倍, 三倍, 四倍)
sight_list = ['hongdian', 'quanxi', 'two', 'three', 'four']
sight_coefficient_list = {
    'hongdian': 1,
    'quanxi': 1,
    'two': 1,
    'three': 1,
    'four': 1,
}

posture_lock = threading.Lock()

# =========================================>> tool函数初始化 <<============================================


# 计算后坐力系数(分辨率系数 * 垂直灵敏度系数 * 配件系数 * 姿势系数)
def calculate_recoil_coefficient():
    # 分辨率系数
    screen_coefficient = 1080 / get_screen_height()
    # 垂直灵敏度系数
    vertical_coefficient = 1 / get_vertical_sensitivity_magnification()
    # 配件系数
    muzzle_coefficient = muzzle_coefficient_list.get(last_muzzle_name)
    # 配件系数
    grip_coefficient = grip_coefficient_list.get(last_grip_name)
    # 配件系数
    butt_coefficient = butt_coefficient_list.get(last_butt_name)
    # 配件系数
    sight_coefficient = sight_coefficient_list.get(last_sight_name)
    # 基础枪械系数 * 姿势系数
    firearm_coefficient = firearm_coefficient_list.get(last_weapon_name)[0] * firearm_coefficient_list.get(last_weapon_name)[posture_state]
    # 计算总系数
    return screen_coefficient * vertical_coefficient * muzzle_coefficient * grip_coefficient * butt_coefficient * sight_coefficient * firearm_coefficient


# 加载模板(从image目录下加载枪械模板)
def load_templates(path: str, name_list: List[str]):
    templates = {}
    for filename in name_list:
        template_path = os.path.join('image', os.path.join(path, filename + ".png"))
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        templates[filename] = adaptive_threshold(template)
    return templates


# 截图(mss)
def take_screenshot_mss(region):
    with mss.mss() as sct:
        # 使用mss截取指定区域的屏幕
        screenshot = sct.grab(region)
        # 将图像转换为numpy数组，并转换为OpenCV的BGR格式
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)  # mss截取的图像带有Alpha通道，所以需要使用COLOR_BGRA2BGR
        return img


# 图像灰度处理
def convert_to_gray(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# 图像二值化处理
def adaptive_threshold(image):
    return cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 11, 2)


# 计算截图与模板各个位置的相似度,返回最大相似度
def match_image(screenshot, template):
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    return max_val


# 获取指定坐标的颜色信息
def get_pixel_color(x, y):
    with mss.mss() as sct:
        # 定义截取区域为一个1x1的区域
        monitor = {"top": y, "left": x, "width": 1, "height": 1}
        # 截取屏幕
        img = sct.grab(monitor)
        # 获取RGB颜色值
        color = img.pixel(0, 0)
        return color


# 判断是否佩戴全自动武器
def is_wear_fully_automatic_rifle():
    y = 1346
    # 判断是否打能量
    color1 = get_pixel_color(1916, 1330)
    r, g, b = color1
    # 加速图标亮起, 认为此时打了能量, 子弹图标上移17个像素点
    if r > 200 and g > 200 and b > 200:
        y = y - 17

    # 根据第三颗子弹是否亮起判断是否佩戴全自动步枪
    color = get_pixel_color(1670, y)
    r, g, b = color
    return r > 200 and g > 200 and b > 200


# 判断是否打开背包
def is_open_backpack():
    color = get_pixel_color(2232, 144)
    r, g, b = color
    return r > 250 and g > 250 and b > 250


# 更新各属性状态
def update_state(key, value):
    state_dict[key] = value


def write_all_states():
    with open(get_lua_config_path(), 'w', encoding='utf-8') as file:
        for key, value in state_dict.items():
            if isinstance(value, str):
                file.write(f"{key} = '{value}'\n")
            else:
                file.write(f"{key} = {value}\n")


# =========================================>> 核心识别逻辑 <<============================================


# 监控当前武器
def firearm_monitor_screen(templates, interval, overlay_model):
    global last_weapon_name

    while True:
        start_time = time.time()
        screenshot = adaptive_threshold(convert_to_gray(take_screenshot_mss(get_weapon_screenshot_area())))
        match_found = False

        max_val_list = {}
        text_list = []

        if is_wear_fully_automatic_rifle():
            for name, template in templates.items():
                max_val = match_image(screenshot, template)

                # 常用队列统计相似度
                if overlay_model is not None:
                    text_list.append(f"{name}相似度: {max_val}\n")

                if max_val >= get_weapon_recognition_confidence_threshold().get(name):
                    max_val_list[name] = max_val

            if len(max_val_list) > 0:
                name = max(max_val_list, key=max_val_list.get)
                # 识别结果不同时更新
                if last_weapon_name != name:
                    last_weapon_name = name
                    update_state("GunName", name)
                    write_all_states()
                    print(
                        f"耗时: {(time.time() - start_time) * 1000:.2f} ms, 更新时相似度: {max_val_list.get(name)} 当前使用武器: {name}")

                    if overlay_model is not None:
                        overlay_model.update_text2(
                            f"耗时: {(time.time() - start_time) * 1000:.2f} ms, 相似度: {max_val_list.get(name):.2f}, 当前使用武器: {name}")

                match_found = True

            if overlay_model is not None and len(text_list) > 0:
                overlay_model.update_text1(" ".join(text_list))

        # 未匹配到图片且当前状态不为N
        if not match_found and last_weapon_name != 'None':
            last_weapon_name = 'None'
            update_state("GunName", "None")
            write_all_states()
            print(f"耗时: {(time.time() - start_time) * 1000:.2f} ms, 未佩枪")

            if overlay_model is not None:
                overlay_model.update_text2(f"耗时: {(time.time() - start_time) * 1000:.2f} ms, 未佩枪")

        # 等待间隔时间
        time.sleep(interval)


# 监控当前武器配件
def accessories_monitor_screen(grips_template_list, muzzles_template_list, butt_template_list, interval, overlay_model):
    while True:
        start_time = time.time()
        if is_open_backpack():
            grip_max_val_list = {}
            muzzles_max_val_list = {}
            butt_max_val_list = {}
            text_list = []

            # 循环握把
            grip_img = adaptive_threshold(convert_to_gray(take_screenshot_mss(get_grip_screenshot_area())))
            for name, template in grips_template_list.items():
                max_val = match_image(grip_img, template)
                if max_val >= 0.3:
                    grip_max_val_list[name] = max_val

            # 循环枪口
            muzzle_img = adaptive_threshold(convert_to_gray(take_screenshot_mss(get_muzzle_screenshot_area())))
            for name, template in muzzles_template_list.items():
                max_val = match_image(muzzle_img, template)
                if max_val >= 0.3:
                    muzzles_max_val_list[name] = max_val

            # 循环枪托
            butt_img = adaptive_threshold(convert_to_gray(take_screenshot_mss(get_butt_screenshot_area())))
            for name, template in butt_template_list.items():
                max_val = match_image(butt_img, template)
                if max_val >= 0.3:
                    butt_max_val_list[name] = max_val

            grips_rifle_name = None
            muzzles_rifle_name = None
            butt_rifle_name = None
            scopes_rifle_name = None

            if len(grip_max_val_list) > 0:
                grips_rifle_name = max(grip_max_val_list, key=grip_max_val_list.get)
                if overlay_model is not None:
                    text_list.append(f"相似度: {grip_max_val_list.get(grips_rifle_name):.2f}, 当前使用握把: {grips_rifle_name}\n")

            if len(muzzles_max_val_list) > 0:
                muzzles_rifle_name = max(muzzles_max_val_list, key=muzzles_max_val_list.get)
                if overlay_model is not None:
                    text_list.append(f"相似度: {muzzles_max_val_list.get(muzzles_rifle_name):.2f}, 当前使用枪口: {muzzles_rifle_name}\n")

            if len(butt_max_val_list) > 0:
                butt_rifle_name = max(butt_max_val_list, key=butt_max_val_list.get)
                if overlay_model is not None:
                    text_list.append(f"相似度: {butt_max_val_list.get(butt_rifle_name):.2f}, 当前使用枪托: {butt_rifle_name}\n")

            update_state("RecoilCoefficient", 1)
            write_all_states()

            if overlay_model is not None and len(text_list) > 0:
                overlay_model.update_text4(" ".join(text_list))

            print(f"检测背包完毕 ===> 耗时: {(time.time() - start_time) * 1000:.2f} ms")
            overlay_model.update_text3(f"检测背包完毕 ===> 耗时: {(time.time() - start_time) * 1000:.2f} ms")
        else:
            print(f"未打开背包 耗时: {(time.time() - start_time) * 1000:.2f} ms")
            overlay_model.update_text3(f"未打开背包 耗时: {(time.time() - start_time) * 1000:.2f} ms")
            overlay_model.update_text4("")

        # 等待间隔时间
        time.sleep(interval)


# 监控枪械主入口
def monitor_firearms_main(overlay_model):
    print("枪械监控中...\n")
    # 加载模板
    firearms_templates = load_templates("firearms", firearm_list)

    # 启动监控线程
    monitor_thread = threading.Thread(target=firearm_monitor_screen, args=(firearms_templates, 0.2, overlay_model))
    monitor_thread.start()


# 监控配件主入口
def monitor_accessories_main(overlay_model):
    print("配件监控中...\n")
    # 加载模板
    grips_templates = load_templates("grips", grip_list)
    muzzles_templates = load_templates("muzzles", muzzle_list)
    butt_templates = load_templates("butt", butt_list)

    # 启动监控线程
    monitor_thread = threading.Thread(target=accessories_monitor_screen,
                                      args=(grips_templates, muzzles_templates, butt_templates, 0.2, overlay_model))
    monitor_thread.start()


def on_press(key):
    global posture_state
    try:
        char = key.char.lower()  # 将字符转为小写
        if char == 'c' or char == '\x03':
            with posture_lock:  # 加锁
                posture_state = 2 if posture_state != 2 else 1
                update_state("Posture", posture_state)
                write_all_states()
        elif char == 'z' or char == '\x1a':
            with posture_lock:  # 加锁
                posture_state = 3 if posture_state != 3 else 1
                update_state("Posture", posture_state)
                write_all_states()
        elif is_open_screenshot_of_keystrokes() and key.char == 'k':
            print("正在截取屏幕...")
            dir_name = "screenshots"
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            # 保存截图用于调试
            weapon_filename = os.path.join(dir_name, f"weapon_ad_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}.png")
            grip_filename = os.path.join(dir_name, f"grip_ad_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}.png")
            muzzle_filename = os.path.join(dir_name, f"muzzle_ad_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}.png")
            butt_filename = os.path.join(dir_name, f"butt_ad_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}.png")

            cv2.imwrite(weapon_filename,
                        adaptive_threshold(convert_to_gray(take_screenshot_mss(get_weapon_screenshot_area()))))
            cv2.imwrite(grip_filename,
                        adaptive_threshold(convert_to_gray(take_screenshot_mss(get_grip_screenshot_area()))))
            cv2.imwrite(muzzle_filename,
                        adaptive_threshold(convert_to_gray(take_screenshot_mss(get_muzzle_screenshot_area()))))
            cv2.imwrite(butt_filename,
                        adaptive_threshold(convert_to_gray(take_screenshot_mss(get_butt_screenshot_area()))))

        elif key == keyboard.Key.space:
            with posture_lock:  # 加锁
                update_state("Posture", 1)
                write_all_states()

    except AttributeError:
        if key == keyboard.Key.space:
            with posture_lock:  # 加锁
                update_state("Posture", 1)
                write_all_states()


# =========================================>> 线程初始化 <<============================================


if __name__ == "__main__":
    print("Starting the application...")
    # 设置按键监听器
    keyboard.Listener(on_press=on_press).start()
    print("请保持窗口开启 ==> \n")
    overlay = None
    if is_open_overlay():
        # 创建监控窗口
        overlay = TextOverlay(tk.Tk(), '300', '300', "", "持续监控中...")

    # 重置枪械, 姿势, 和配件
    update_state("GunName", "None")
    update_state("RecoilCoefficient", 1)
    write_all_states()

    # 启动枪械监控线程
    monitor_firearms_main(overlay)
    # 启动配件监控线程
    monitor_accessories_main(overlay)
    if is_open_overlay():
        overlay.root.mainloop()
