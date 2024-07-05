from datetime import datetime

import pyautogui
import numpy as np
import cv2
import time
import threading
import os
from pynput import keyboard
import tkinter as tk
from text_overlay import TextOverlay

screen_resolution = [2560, 1440]
screenshot_region = (screen_resolution[0] - 800, screen_resolution[1] - 260, 800, 260)  # (left, top, width, height)

commonly_used_firearm_list = ['m762', 'aug', 'm4', 'ace32', 'akm', 'groza', 'k2', 'm249', 'p90', 'scar']
low_frequency_used_firearms_list = ['g36c', 'qbz', 'tmx', 'ump', 'uzi', 'vkt', 'famae']

whether_overlay = True

weapon_threshold = {
    'm762': 0.76,
    'aug': 0.81,
    'm4': 0.81,
    'ace32': 0.81,
    'akm': 0.81,
    'groza': 0.81,
    'k2': 0.81,
    'm249': 0.81,
    'p90': 0.81,
    'scar': 0.81,
    'g36c': 0.81,
    'qbz': 0.81,
    'tmx': 0.81,
    'ump': 0.81,
    'uzi': 0.81,
    'vkt': 0.81,
    'famae': 0.81
}
index_weapon_mapping = {
    'm762': 2,
    'aug': 11,
    'm4': 3,
    'ace32': 4,
    'akm': 1,
    'groza': 10,
    'k2': 12,
    'm249': 13,
    'p90': 16,
    'scar': 5,
    'g36c': 6,
    'qbz': 7,
    'tmx': 14,
    'ump': 8,
    'uzi': 9,
    'vkt': 15,
    'famae': 17
}
last_indexWeapon = 'N'
posture_state = 0
file_paths = ["C:/Users/Public/Downloads/pubg.lua", "C:/Users/Public/Downloads/pubgd.lua"]


# 截图
def take_screenshot(region):
    screenshot = pyautogui.screenshot(region=region)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return screenshot


# 灰度处理
def convert_to_gray(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# 匹配图像
def match_image(screenshot, template):
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    return max_val


# 加载图片模板
def load_templates(firearm_list):
    templates = {}
    for filename in firearm_list:
        template_path = os.path.join('firearms', filename + ".png")
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        # template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        templates[filename] = template
    return templates


# 监控屏幕是否出现指定模板
def monitor_screen(templates, interval, overlay):
    w_file_path = file_paths[0]
    global last_indexWeapon

    while True:
        start_time = time.time()
        screenshot = take_screenshot(screenshot_region)
        match_found = False

        text_list = []

        for name, template in templates.items():
            max_val = match_image(convert_to_gray(screenshot), template)

            # 常用队列统计相似度
            if overlay is not None and name in commonly_used_firearm_list:
                text_list.append(f"{name}相似度: {max_val}\n")

            if max_val >= weapon_threshold.get(name):

                if overlay is not None:
                    overlay.update_text1(f"当前匹配相似度: {max_val}")

                # 识别结果不同时更新
                if last_indexWeapon != name:
                    last_indexWeapon = name
                    with open(w_file_path, 'w', encoding='utf-8') as file:
                        file.write(f"indexWeapon = {index_weapon_mapping.get(name)}\n")

                    print(f"耗时: {(time.time() - start_time) * 1000:.2f} ms, 更新时相似度: {max_val} 当前使用武器: {name}")
                    if overlay is not None:
                        overlay.update_text2(f"耗时: {(time.time() - start_time) * 1000:.2f} ms, 相似度: {max_val}, 当前使用武器: {name}")

                # # 保存截图用于调试
                # screenshot_filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}.png"
                # cv2.imwrite(screenshot_filename, screenshot)

                match_found = True
                break

        if len(text_list) > 0:
            overlay.update_text1(" ".join(text_list))

        # 未匹配到图片且当前状态不为N
        if not match_found and last_indexWeapon != 'N':
            if last_indexWeapon in templates:
                last_indexWeapon = 'N'
                with open(w_file_path, 'w', encoding='utf-8') as file:
                    file.write(f"indexWeapon = 0\n")
                print(f"耗时: {(time.time() - start_time) * 1000:.2f} ms, 未佩枪")

                if overlay is not None:
                    overlay.update_text2(f"耗时: {(time.time() - start_time) * 1000:.2f} ms, 未佩枪")

        # 等待间隔时间
        time.sleep(interval)


# 监控屏幕主入口
def image_identification_main():
    commonly_used_firearm_templates = load_templates(commonly_used_firearm_list)
    low_frequency_used_firearms_templates = load_templates(low_frequency_used_firearms_list)

    if whether_overlay:
        root = tk.Tk()
        # 创建监控窗口
        overlay = TextOverlay(root, '1000', '0', "当前匹配相似度: xxx", "持续监控中...")

        # 启动监控线程
        monitor_thread1 = threading.Thread(target=monitor_screen, args=(commonly_used_firearm_templates, 0.1, overlay))
        monitor_thread2 = threading.Thread(target=monitor_screen, args=(low_frequency_used_firearms_templates, 0.5, overlay))
        monitor_thread1.start()
        monitor_thread2.start()

        root.mainloop()
    else:
        monitor_thread1 = threading.Thread(target=monitor_screen, args=(commonly_used_firearm_templates, 0.1, None))
        monitor_thread2 = threading.Thread(target=monitor_screen, args=(low_frequency_used_firearms_templates, 0.5, None))
        monitor_thread1.start()
        monitor_thread2.start()


def write_posture_state(state):
    with open(file_paths[1], 'w', encoding='utf-8') as file:
        file.write(f"zishi = {state}\n")


def on_posture_main(key):
    global posture_state
    try:
        if key.char == 'c':
            if posture_state == 1:
                posture_state = 0
            else:
                posture_state = 1
            write_posture_state(posture_state)
        elif key.char == 'k':
            print("正在截取屏幕...")
            dir_name = "screenshots"
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            # 保存截图用于调试
            screenshot_filename = os.path.join(dir_name, f"screenshot_def_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}.png")
            cv2.imwrite(screenshot_filename, take_screenshot(screenshot_region))

            screenshot_filename = os.path.join(dir_name, f"screenshot_gray_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}.png")
            cv2.imwrite(screenshot_filename, convert_to_gray(take_screenshot(screenshot_region)))

        elif key.char == 'z':
            if posture_state == 2:
                posture_state = 0
            else:
                posture_state = 2
            write_posture_state(posture_state)
    except AttributeError:
        if key == keyboard.Key.space:
            posture_state = 0
            write_posture_state(posture_state)


if __name__ == "__main__":
    print("Starting the application...")
    # 设置按键监听器
    keyboard.Listener(on_press=on_posture_main).start()
    print("请保持窗口开启 ==> 截图监控中...\n")
    image_identification_main()
