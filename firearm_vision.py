import pyautogui
import numpy as np
import cv2
import time
import threading
import os
from pynput import keyboard

screen_resolution = [2560, 1440]
screenshot_region = (screen_resolution[0] - 800, screen_resolution[1] - 260, 800, 260)  # (left, top, width, height)

commonly_used_firearm_list = ['m762', 'aug', 'm4', 'ace32', 'akm', 'groza', 'k2', 'm249', 'p90', 'scar']
low_frequency_used_firearms_list = ['g36c', 'qbz', 'tmx', 'ump', 'uzi', 'vkt', 'famae']

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


# 匹配图像
def match_image(screenshot, template, threshold=0.8):
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= threshold)
    return len(loc[0]) > 0


# 加载图片模板
def load_templates(firearm_list):
    templates = {}
    for filename in firearm_list:
        template_path = os.path.join('firearms', filename + ".png")
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        templates[filename] = template
    return templates


# 监控屏幕是否出现指定模板
def monitor_screen(templates, interval):
    w_file_path = file_paths[0]
    global last_indexWeapon

    while True:
        start_time = time.time()
        screenshot = take_screenshot(screenshot_region)
        match_found = False

        for name, template in templates.items():

            if match_image(screenshot, template):
                # 识别结果不同时更新
                if last_indexWeapon != name:
                    last_indexWeapon = name
                    with open(w_file_path, 'w', encoding='utf-8') as file:
                        file.write(f"indexWeapon = {index_weapon_mapping.get(name)}\n")
                    print(f"耗时: {(time.time() - start_time) * 1000:.2f} ms, 当前使用武器: {name}")

                # # 保存截图用于调试
                # screenshot_filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}.png"
                # cv2.imwrite(screenshot_filename, screenshot)

                match_found = True
                break

        # 未匹配到图片且当前状态不为N
        if not match_found and last_indexWeapon != 'N':
            if last_indexWeapon in templates:
                last_indexWeapon = 'N'
                with open(w_file_path, 'w', encoding='utf-8') as file:
                    file.write(f"indexWeapon = 0\n")
                print(f"耗时: {(time.time() - start_time) * 1000:.2f} ms, 未佩枪")

        # 等待间隔时间
        time.sleep(interval)


# 监控屏幕主入口
def image_identification_main():
    print("Starting the application...")

    commonly_used_firearm_templates = load_templates(commonly_used_firearm_list)
    low_frequency_used_firearms_templates = load_templates(low_frequency_used_firearms_list)

    # 启动监控线程
    monitor_thread1 = threading.Thread(target=monitor_screen, args=(commonly_used_firearm_templates, 0.1))
    monitor_thread2 = threading.Thread(target=monitor_screen, args=(low_frequency_used_firearms_templates, 0.5))
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
    image_identification_main()
    # 设置按键监听器
    listener = keyboard.Listener(on_press=on_posture_main)
    listener.start()
    input("请保持窗口开启 ==> 持续监控中...\n")
