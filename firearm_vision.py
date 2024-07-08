from datetime import datetime

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
file_paths = config["file_paths"]
resolution = config["resolution"]
screenshot_region = config["screenshot_region"]
whether_overlay = config["whether_overlay"]
whether_screenshot = config["whether_screenshot"]
weapon_threshold = config["weapon_threshold"]
index_weapon_mapping = config["index_weapon_mapping"]

# 初始化参数
firearm_list = ['m762', 'aug', 'm4', 'ace32', 'akm', 'groza', 'k2', 'm249', 'p90', 'scar', 'g36c', 'qbz', 'tmx', 'ump', 'uzi', 'vkt', 'famae']
posture_lock = threading.Lock()
last_indexWeapon = 'N'
posture_state = 0


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


# 加载图片模板
def load_templates(firearm_list):
    templates = {}
    for filename in firearm_list:
        template_path = os.path.join('firearms', filename + ".png")
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        templates[filename] = adaptive_threshold(template)
    return templates


# 监控屏幕是否出现指定模板
def monitor_screen(templates, interval, overlay):
    global last_indexWeapon

    while True:
        start_time = time.time()
        screenshot = adaptive_threshold(convert_to_gray(take_screenshot(screenshot_region)))
        match_found = False

        max_val_list = {}
        text_list = []

        y = 1346
        # 判断是否打能量
        color1 = get_pixel_color(1916, 1330)
        r, g, b = color1
        if r > 200 and g > 200 and b > 200:
            y = y - 17
        # 判断是否佩戴全自动步枪
        color = get_pixel_color(1670, y)
        r, g, b = color
        if r > 200 and g > 200 and b > 200:
            for name, template in templates.items():
                max_val = match_image(screenshot, template)

                # 常用队列统计相似度
                # if overlay is not None:
                #     text_list.append(f"{name}相似度: {max_val}\n")

                if max_val >= weapon_threshold.get(name):
                    max_val_list[name] = max_val

            if len(max_val_list) > 0:
                name = max(max_val_list, key=max_val_list.get)
                # 识别结果不同时更新
                if last_indexWeapon != name:
                    last_indexWeapon = name
                    write_weapon_state(index_weapon_mapping.get(name))

                    print(f"耗时: {(time.time() - start_time) * 1000:.2f} ms, 更新时相似度: {max_val_list.get(name)} 当前使用武器: {name}")

                    if overlay is not None:
                        overlay.update_text2(f"耗时: {(time.time() - start_time) * 1000:.2f} ms, 相似度: {max_val_list.get(name):.2f}, 当前使用武器: {name}")

                match_found = True

            if overlay is not None and len(text_list) > 0:
                overlay.update_text1(" ".join(text_list))

        # 未匹配到图片且当前状态不为N
        if not match_found and last_indexWeapon != 'N':
            last_indexWeapon = 'N'
            write_weapon_state(0)
            print(f"耗时: {(time.time() - start_time) * 1000:.2f} ms, 未佩枪")

            if overlay is not None:
                overlay.update_text2(f"耗时: {(time.time() - start_time) * 1000:.2f} ms, 未佩枪")

        # 等待间隔时间
        time.sleep(interval)


# 监控屏幕主入口
def image_identification_main():
    # 重置枪械和姿势
    write_weapon_state(0)
    write_posture_state(0)
    commonly_used_firearm_templates = load_templates(firearm_list)
    overlay = None

    if whether_overlay:
        # 创建监控窗口
        overlay = TextOverlay(tk.Tk(), '1540', '1288', "", "持续监控中...")

    # 启动监控线程
    monitor_thread = threading.Thread(target=monitor_screen, args=(commonly_used_firearm_templates, 0.2, overlay))
    monitor_thread.start()

    if whether_overlay:
        overlay.root.mainloop()


# 更新枪械状态
def write_weapon_state(state):
    with open(file_paths[0], 'w', encoding='utf-8') as file:
        file.write(f"indexWeapon = {state}\n")


# 更新姿势状态
def write_posture_state(state):
    with open(file_paths[1], 'w', encoding='utf-8') as file:
        file.write(f"zishi = {state}\n")


def on_press(key):
    global posture_state
    try:
        char = key.char.lower()  # 将字符转为小写
        if char == 'c' or char == '\x03':
            with posture_lock:  # 加锁
                posture_state = 1 if posture_state != 1 else 0
                write_posture_state(posture_state)
        elif char == 'z' or char == '\x1a':
            with posture_lock:  # 加锁
                posture_state = 2 if posture_state != 2 else 0
                write_posture_state(posture_state)
        elif whether_screenshot and key.char == 'k':
            print("正在截取屏幕...")
            dir_name = "screenshots"
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            # 保存截图用于调试
            screenshot_filename = os.path.join(dir_name, f"screenshot_def_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}.png")
            cv2.imwrite(screenshot_filename, take_screenshot(screenshot_region))

            screenshot_filename = os.path.join(dir_name, f"screenshot_gray_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}.png")
            cv2.imwrite(screenshot_filename, convert_to_gray(take_screenshot(screenshot_region)))

            screenshot_filename = os.path.join(dir_name, f"screenshot_ad_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}.png")
            cv2.imwrite(screenshot_filename, adaptive_threshold(convert_to_gray(take_screenshot(screenshot_region))))
        elif key == keyboard.Key.space:
            with posture_lock:  # 加锁
                posture_state = 0
                write_posture_state(posture_state)
    except AttributeError:
        if key == keyboard.Key.space:
            with posture_lock:  # 加锁
                posture_state = 0
                write_posture_state(posture_state)


if __name__ == "__main__":
    print("Starting the application...")
    # 设置按键监听器
    keyboard.Listener(on_press=on_press).start()
    print("请保持窗口开启 ==> 截图监控中...\n")
    image_identification_main()
