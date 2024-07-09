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


# 加载配置
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)


# 加载外部配置
config = load_config()
file_path = config["file_path"]
resolution = config["resolution"]
weapon_region = config["weapon_region"]
grip_region = config["grip_region"]
muzzle_region = config["muzzle_region"]
stocks_region = config["stocks_region"]
whether_overlay = config["whether_overlay"]
whether_screenshot = config["whether_screenshot"]
weapon_threshold = config["weapon_threshold"]
index_weapon_mapping = config["index_weapon_mapping"]

# 初始化参数
firearm_list = ['m762', 'aug', 'm4', 'ace32', 'akm', 'groza', 'k2', 'm249', 'p90', 'scar', 'g36c', 'qbz', 'tmx', 'ump', 'uzi', 'vkt', 'famae']
grip_list = ['banjie', 'qingxing', 'chuizhi', 'muzhi']
muzzle_list = ['xiaoyan', 'buchang']
stocks_list = ['zhongxing', 'zhanshu']

posture_lock = threading.Lock()
last_weapon_name = 'N'
posture_state = 'stand'
state_dict = {}


# 加载图片模板
def load_templates(path: str, name_list: List[str]):
    templates = {}
    for filename in name_list:
        template_path = os.path.join('image', os.path.join(path, filename + ".png"))
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        templates[filename] = adaptive_threshold(template)
    return templates


# 截图(mss)
def take_screenshot(region):
    with mss.mss() as sct:
        # 使用mss截取指定区域的屏幕
        screenshot = sct.grab(region)
        # 将图像转换为numpy数组，并转换为OpenCV的BGR格式
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)  # mss截取的图像带有Alpha通道，所以需要使用COLOR_BGRA2BGR
        return img


# 灰度处理
def convert_to_gray(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# 自适应二值化处理
def adaptive_threshold(image):
    return cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 11, 2)


# 匹配图像
def match_image(screenshot, template):
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    return max_val


# 匹配图像按平方差， 此方式对亮度敏感
def match_image_sqd(screenshot, template):
    result = cv2.matchTemplate(screenshot, template, cv2.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    return 1 - min_val


# 获取子弹坐标的颜色信息
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
def whether_wear_fully_automatic_rifle():
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


def whether_open_backpack():
    # 判断是否打开背包
    color = get_pixel_color(2232, 144)
    r, g, b = color
    return r > 250 and g > 250 and b > 250


# 监控当前武器
def firearm_monitor_screen(templates, interval, overlay_model):
    global last_weapon_name

    while True:
        start_time = time.time()
        screenshot = adaptive_threshold(convert_to_gray(take_screenshot(weapon_region)))
        match_found = False

        max_val_list = {}
        text_list = []

        if whether_wear_fully_automatic_rifle():
            for name, template in templates.items():
                max_val = match_image(screenshot, template)

                # 常用队列统计相似度
                if overlay_model is not None:
                    text_list.append(f"{name}相似度: {max_val}\n")

                if max_val >= weapon_threshold.get(name):
                    max_val_list[name] = max_val

            if len(max_val_list) > 0:
                name = max(max_val_list, key=max_val_list.get)
                # 识别结果不同时更新
                if last_weapon_name != name:
                    last_weapon_name = name
                    update_state("weapon_name", name)
                    write_all_states(file_path)
                    print(f"耗时: {(time.time() - start_time) * 1000:.2f} ms, 更新时相似度: {max_val_list.get(name)} 当前使用武器: {name}")

                    if overlay_model is not None:
                        overlay_model.update_text2(f"耗时: {(time.time() - start_time) * 1000:.2f} ms, 相似度: {max_val_list.get(name):.2f}, 当前使用武器: {name}")

                match_found = True

            if overlay_model is not None and len(text_list) > 0:
                overlay_model.update_text1(" ".join(text_list))

        # 未匹配到图片且当前状态不为N
        if not match_found and last_weapon_name != 'N':
            last_weapon_name = 'N'
            update_state("weapon_name", "None")
            write_all_states(file_path)
            print(f"耗时: {(time.time() - start_time) * 1000:.2f} ms, 未佩枪")

            if overlay_model is not None:
                overlay_model.update_text2(f"耗时: {(time.time() - start_time) * 1000:.2f} ms, 未佩枪")

        # 等待间隔时间
        time.sleep(interval)


# 监控当前武器配件
def accessories_monitor_screen(grips_template_list, muzzles_template_list, stocks_template_list, interval, overlay_model):
    while True:
        start_time = time.time()
        if whether_open_backpack():
            grip_max_val_list = {}
            muzzles_max_val_list = {}
            stocks_max_val_list = {}
            text_list = []

            # 循环握把
            grip_img = adaptive_threshold(convert_to_gray(take_screenshot(grip_region)))
            for name, template in grips_template_list.items():
                max_val = match_image(grip_img, template)
                if max_val >= 0.3:
                    grip_max_val_list[name] = max_val

            # 循环枪口
            muzzle_img = adaptive_threshold(convert_to_gray(take_screenshot(muzzle_region)))
            for name, template in muzzles_template_list.items():
                max_val = match_image(muzzle_img, template)
                if max_val >= 0.3:
                    muzzles_max_val_list[name] = max_val

            # 循环枪托
            stocks_img = adaptive_threshold(convert_to_gray(take_screenshot(stocks_region)))
            for name, template in stocks_template_list.items():
                max_val = match_image(stocks_img, template)
                if max_val >= 0.3:
                    stocks_max_val_list[name] = max_val

            if len(grip_max_val_list) > 0:
                name = max(grip_max_val_list, key=grip_max_val_list.get)
                update_state("grips_rifle", name)
                if overlay_model is not None:
                    text_list.append(f"相似度: {grip_max_val_list.get(name):.2f}, 当前使用握把: {name}\n")
            else:
                update_state("grips_rifle", "None")

            if len(muzzles_max_val_list) > 0:
                name = max(muzzles_max_val_list, key=muzzles_max_val_list.get)
                update_state("muzzles_rifle", name)
                if overlay_model is not None:
                    text_list.append(f"相似度: {muzzles_max_val_list.get(name):.2f}, 当前使用枪口: {name}\n")
            else:
                update_state("muzzles_rifle", "None")

            if len(stocks_max_val_list) > 0:
                name = max(stocks_max_val_list, key=stocks_max_val_list.get)
                update_state("stocks_rifle", name)
                if overlay_model is not None:
                    text_list.append(f"相似度: {stocks_max_val_list.get(name):.2f}, 当前使用枪托: {name}\n")
            else:
                update_state("stocks_rifle", "None")

            # 瞄准镜默认
            update_state("scopes_rifle", "None")
            write_all_states(file_path)

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
    stocks_templates = load_templates("stocks", stocks_list)

    # 启动监控线程
    monitor_thread = threading.Thread(target=accessories_monitor_screen, args=(grips_templates, muzzles_templates, stocks_templates, 0.2, overlay_model))
    monitor_thread.start()


def update_state(key, value):
    state_dict[key] = value


def write_all_states(file_path_name):
    with open(file_path_name, 'w', encoding='utf-8') as file:
        for key, value in state_dict.items():
            file.write(f"{key} = {value}\n")


def on_press(key):
    global posture_state
    try:
        char = key.char.lower()  # 将字符转为小写
        if char == 'c' or char == '\x03':
            with posture_lock:  # 加锁
                posture_state = 'down' if posture_state != 'down' else 'stand'
                update_state("posture_state", posture_state)

        elif char == 'z' or char == '\x1a':
            with posture_lock:  # 加锁
                posture_state = 'lie' if posture_state != 'lie' else 'stand'
                update_state("posture_state", posture_state)
        elif whether_screenshot and key.char == 'k':
            print("正在截取屏幕...")
            dir_name = "screenshots"
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            # 保存截图用于调试
            weapon_filename = os.path.join(dir_name, f"weapon_ad_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}.png")
            grip_filename = os.path.join(dir_name, f"grip_ad_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}.png")
            muzzle_filename = os.path.join(dir_name, f"muzzle_ad_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}.png")
            stocks_filename = os.path.join(dir_name, f"stocks_ad_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}.png")

            cv2.imwrite(weapon_filename, adaptive_threshold(convert_to_gray(take_screenshot(weapon_region))))
            cv2.imwrite(grip_filename, adaptive_threshold(convert_to_gray(take_screenshot(grip_region))))
            cv2.imwrite(muzzle_filename, adaptive_threshold(convert_to_gray(take_screenshot(muzzle_region))))
            cv2.imwrite(stocks_filename, adaptive_threshold(convert_to_gray(take_screenshot(stocks_region))))

        elif key == keyboard.Key.space:
            with posture_lock:  # 加锁
                update_state("posture_state", "stand")

        write_all_states(file_path)
    except AttributeError:
        if key == keyboard.Key.space:
            with posture_lock:  # 加锁
                update_state("posture_state", "stand")
                write_all_states(file_path)


if __name__ == "__main__":
    print("Starting the application...")
    # 设置按键监听器
    keyboard.Listener(on_press=on_press).start()
    print("请保持窗口开启 ==> \n")
    overlay = None
    if whether_overlay:
        # 创建监控窗口
        overlay = TextOverlay(tk.Tk(), '1540', '1288', "", "持续监控中...")

    # 重置枪械, 姿势, 和配件
    update_state("weapon_name", "None")
    update_state("posture_state", "stand")
    update_state("grips_rifle", "None")
    update_state("muzzles_rifle", "None")
    update_state("stocks_rifle", "None")
    update_state("scopes_rifle", "None")
    write_all_states(file_path)

    # 启动枪械监控线程
    monitor_firearms_main(overlay)
    # 启动配件监控线程
    monitor_accessories_main(overlay)
    if whether_overlay:
        overlay.root.mainloop()
