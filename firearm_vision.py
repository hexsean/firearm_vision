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
    return config["is_open_screenshot_of_keystrokes"]


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
    return config["vertical_sensitivity_magnification"]


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
                'ump',
                'mp5k',
                'vkt',
                'p90',
                'm249',
                'dp28',
                'mg3',
                'famae']

# 各枪械基础系数[基础系数, 站立系数, 蹲下系数, 趴下系数]
firearm_coefficient_list = {
    'akm': [1, 1, 1, 1],
    'qbz': [1, 1, 1, 1],
    'm762': [1, 1, 0.83, 0.55],
    'groza': [1, 1, 1, 1],
    'scarl': [1, 1, 1, 1],
    'm16a4': [1, 1, 1, 1],
    'aug': [1, 1, 1, 1],
    'm416': [1, 1, 1, 1],
    'k2': [1, 1, 1, 1],
    'g36c': [1, 1, 1, 1],
    'mk47': [1, 1, 1, 1],
    'ace32': [1, 1, 1, 1],
    'ump': [1, 1, 1, 1],
    'mp5k': [1, 1, 1, 1],
    'vkt': [1, 1, 1, 1],
    'p90': [1, 1, 1, 1],
    'm249': [1, 1, 1, 1],
    'dp28': [1, 1, 1, 1],
    'mg3': [1, 1, 1, 1],
    'famae': [1, 1, 1, 1],
}


# 枪口列表(无, 步枪消焰, 步枪补偿)
muzzle_list = ['xiaoyan', 'buchang']
muzzle_coefficient_list = {
    'xiaoyan': 1.162,
    'buchang': 1,
}

# 握把列表(无, 半截式握把, 轻型握把, 垂直握把, 拇指握把)
grip_list = ['banjie', 'qingxing', 'chuizhi', 'muzhi']
grip_coefficient_list = {
    'banjie': 0.818,
    'qingxing': 0.86,
    'chuizhi': 0.79,
    'muzhi': 0.888,
}

# 枪托列表(无, 战术枪托, 重型枪托)
butt_list = ['zhongxing', 'zhanshu']
butt_coefficient_list = {
    'zhongxing': 0.895,
    'zhanshu': 0.965,
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
    # 分辨率系数(与fov相关, 暂不参与计算)
    screen_coefficient = 1
    # 垂直灵敏度系数
    vertical_coefficient = 1 / get_vertical_sensitivity_magnification()

    muzzle_coefficient = muzzle_coefficient_list.get(last_muzzle_name, 1.265)
    grip_coefficient = grip_coefficient_list.get(last_grip_name, 1)
    butt_coefficient = butt_coefficient_list.get(last_butt_name, 1)
    sight_coefficient = sight_coefficient_list.get(last_sight_name, 1)

    # 基础枪械系数 * 姿势系数
    if last_weapon_name in firearm_coefficient_list:
        weapon_coefficients = firearm_coefficient_list[last_weapon_name]  # 直接访问确保键存在
        firearm_coefficient = weapon_coefficients[0] * weapon_coefficients[posture_state]  # 访问具体姿势系数
    else:
        firearm_coefficient = 1  # 如果键不存在，则使用默认值1

    # 计算总系数
    return round(screen_coefficient * vertical_coefficient * muzzle_coefficient * grip_coefficient * butt_coefficient * sight_coefficient * firearm_coefficient, 4)


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


# 判断是否佩戴全自动或半自动武器
def is_wear_fully_automatic_rifle():
    y = 1341

    # 判断是否打能量
    color1 = get_pixel_color(1916, 1330)
    r, g, b = color1
    # 加速图标亮起, 认为此时打了能量, 上移能量条的高度
    if r > 200 and g > 200 and b > 200:
        y = y - 6

    # 判断是否防毒背包
    color1 = get_pixel_color(1445, 1397)
    r, g, b = color1
    # 有防毒条认为佩戴防毒背包, 上移防毒条的高度
    if 5 <= r <= 9 and 158 <= g <= 162 and 245 <= b <= 249:
        y = y - 4

    # 根据第2颗子弹是否亮起判断是否佩戴全自动或半自动武器
    color = get_pixel_color(1670, y)
    r, g, b = color
    return r > 200 and g > 200 and b > 200


# 判断是否打开背包
def is_open_backpack():
    color = get_pixel_color(2238, 144)
    r, g, b = color
    return r > 250 and g > 250 and b > 250


# 更新武器和后坐力系数
def update_weapon_and_coefficient():
    with open(get_lua_config_path(), 'w', encoding='utf-8') as file:
        file.write(f"GunName = '{last_weapon_name}'\n")
        file.write(f"RecoilCoefficient = {calculate_recoil_coefficient()}\n")


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
                    update_weapon_and_coefficient()
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
            update_weapon_and_coefficient()
            print(f"耗时: {(time.time() - start_time) * 1000:.2f} ms, 未佩枪")

            if overlay_model is not None:
                overlay_model.update_text2(f"耗时: {(time.time() - start_time) * 1000:.2f} ms, 未佩枪")

        # 等待间隔时间
        time.sleep(interval)


# 监控当前武器配件
def accessories_monitor_screen(grips_template_list, muzzles_template_list, butt_template_list, interval, overlay_model):
    global last_muzzle_name
    global last_grip_name
    global last_butt_name
    global last_sight_name

    while True:
        start_time = time.time()
        if is_open_backpack():
            grip_max_val_list = {}
            muzzles_max_val_list = {}
            butt_max_val_list = {}
            text_list = []

            # 循环枪口
            muzzle_img = adaptive_threshold(convert_to_gray(take_screenshot_mss(get_muzzle_screenshot_area())))
            for name, template in muzzles_template_list.items():
                max_val = match_image(muzzle_img, template)
                if max_val >= 0.65:
                    muzzles_max_val_list[name] = max_val

            # 循环握把
            grip_img = adaptive_threshold(convert_to_gray(take_screenshot_mss(get_grip_screenshot_area())))
            for name, template in grips_template_list.items():
                max_val = match_image(grip_img, template)
                if max_val >= 0.65:
                    grip_max_val_list[name] = max_val

            # 循环枪托
            butt_img = adaptive_threshold(convert_to_gray(take_screenshot_mss(get_butt_screenshot_area())))
            for name, template in butt_template_list.items():
                max_val = match_image(butt_img, template)
                if max_val >= 0.65:
                    butt_max_val_list[name] = max_val

            if len(muzzles_max_val_list) > 0:
                last_muzzle_name = max(muzzles_max_val_list, key=muzzles_max_val_list.get)
                if overlay_model is not None:
                    text_list.append(f"相似度: {muzzles_max_val_list.get(last_muzzle_name):.2f}, 当前使用枪口: {last_muzzle_name}\n")
            else:
                last_muzzle_name = "None"
                if overlay_model is not None:
                    text_list.append(f"当前使用枪口None")

            if len(grip_max_val_list) > 0:
                last_grip_name = max(grip_max_val_list, key=grip_max_val_list.get)
                if overlay_model is not None:
                    text_list.append(f"相似度: {grip_max_val_list.get(last_grip_name):.2f}, 当前使用握把: {last_grip_name}\n")
            else:
                last_grip_name = "None"
                if overlay_model is not None:
                    text_list.append(f"当前使用握把None")

            if len(butt_max_val_list) > 0:
                last_butt_name = max(butt_max_val_list, key=butt_max_val_list.get)
                if overlay_model is not None:
                    text_list.append(f"相似度: {butt_max_val_list.get(last_butt_name):.2f}, 当前使用枪托: {last_butt_name}\n")
            else:
                last_butt_name = "None"
                if overlay_model is not None:
                    text_list.append(f"当前使用枪托None")

            last_sight_name = "None"

            update_weapon_and_coefficient()

            if overlay_model is not None and len(text_list) > 0:
                overlay_model.update_text4(" ".join(text_list))

            print(f"检测背包完毕 ===> 耗时: {(time.time() - start_time) * 1000:.2f} ms")
            overlay_model.update_text3(f"检测背包完毕 ===> 耗时: {(time.time() - start_time) * 1000:.2f} ms")
        else:
            print(f"未打开背包 耗时: {(time.time() - start_time) * 1000:.2f} ms")
            if overlay_model is not None:
                overlay_model.update_text3(f"未打开背包 当前枪口{last_muzzle_name}, 握把{last_grip_name}, 枪托{last_butt_name}, 瞄具{last_sight_name}, 耗时: {(time.time() - start_time) * 1000:.2f} ms")
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
                update_weapon_and_coefficient()
        elif char == 'z' or char == '\x1a':
            with posture_lock:  # 加锁
                posture_state = 3 if posture_state != 3 else 1
                update_weapon_and_coefficient()
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
                posture_state = 1
                update_weapon_and_coefficient()
    except AttributeError:
        if key == keyboard.Key.space:
            with posture_lock:  # 加锁
                posture_state = 1
                update_weapon_and_coefficient()

# =========================================>> 线程初始化 <<============================================


if __name__ == "__main__":
    print("Starting the application...")
    # 设置按键监听器
    keyboard.Listener(on_press=on_press).start()
    print("请保持窗口开启 ==> \n")
    overlay = None
    if is_open_overlay():
        # 创建监控窗口
        overlay = TextOverlay(tk.Tk(), '50', '300', "", "持续监控中...")

    # 重置枪械, 姿势, 和配件
    last_weapon_name = "None"
    last_muzzle_name = 'None'
    last_grip_name = 'None'
    last_butt_name = 'None'
    last_sight_name = 'None'
    posture_state = 1

    update_weapon_and_coefficient()

    # 启动枪械监控线程
    monitor_firearms_main(overlay)
    # 启动配件监控线程
    monitor_accessories_main(overlay)
    if is_open_overlay():
        overlay.root.mainloop()
