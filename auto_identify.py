import signal
import sys
import datetime
from typing import List

import dxcam
import mss
import numpy as np
import cv2
import time
import threading
import os
import json

from pynput import keyboard
import tkinter as tk

from user_configuration import UserConfiguration
from text_overlay import TextOverlay
import base64
import re
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

# =========================================>> 加载动态配置 <<============================================


def load_configuration():
    with open('config.json', 'r') as f:
        c = json.load(f)
    return UserConfiguration(c)


config = load_configuration()

# =========================================>> 初始化静态配置 <<============================================
update_last_weapon_name = None
update_coefficient = 1
# 当前佩戴的武器名称
last_weapon_name = 'None'
last_weapon_no = 1

# 1号位
# 当前枪口配件名称
last_muzzle_name = 'None'
# 当前握把配件名称
last_grip_name = 'None'
# 当前枪托配件名称
last_butt_name = 'None'
# 当前瞄准镜配件名称
last_sight_name = 'None'

# 2号位
# 当前枪口配件名称
last_muzzle_name2 = 'None'
# 当前握把配件名称
last_grip_name2 = 'None'
# 当前枪托配件名称
last_butt_name2 = 'None'
# 当前瞄准镜配件名称
last_sight_name2 = 'None'

# 姿势状态: 1-站立, 2-蹲下, 3-趴下
posture_state = 1

last_frame = None
# =========================================>> tool函数初始化 <<============================================


# 计算后坐力系数(分辨率系数 * 垂直灵敏度系数 * 配件系数 * 姿势系数)
def calculate_recoil_coefficient():
    # 分辨率系数(与fov相关, 暂不参与计算)
    screen_coefficient = 1
    # 垂直灵敏度系数
    vertical_coefficient = 1 / config.vertical_sensitivity_magnification
    # 默认为裸配, 默认弹道为补偿三角(战术枪托)
    if last_weapon_no == 1:
        muzzle_coefficient = config.muzzle_coefficient_list.get(last_muzzle_name, config.def_muzzle)
        grip_coefficient = config.grip_coefficient_list.get(last_grip_name, 1)
        butt_coefficient = config.butt_coefficient_list.get(last_butt_name, 1)
        sight_coefficient = config.sight_coefficient_list.get(last_sight_name, 1)
    else:
        muzzle_coefficient = config.muzzle_coefficient_list.get(last_muzzle_name2, config.def_muzzle)
        grip_coefficient = config.grip_coefficient_list.get(last_grip_name2, 1)
        butt_coefficient = config.butt_coefficient_list.get(last_butt_name2, 1)
        sight_coefficient = config.sight_coefficient_list.get(last_sight_name2, 1)

    # 基础枪械系数 * 姿势系数
    if last_weapon_name in config.firearm_coefficient_list:
        weapon_coefficients = config.firearm_coefficient_list[last_weapon_name]
        firearm_coefficient = weapon_coefficients[0] * weapon_coefficients[posture_state]
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


# 使用mss截取指定区域的屏幕bgr
def take_screenshot_mss(region):
    with mss.mss() as sct:
        return sct.grab(region)


# 使用dxgi截取指定区域的屏幕bgr
def take_screenshot_dxgi(region):
    global last_frame
    try:
        # start_time = time.perf_counter()  # 开始计时
        result = last_frame[region['top']:region['top']+region['height'], region['left']:region['left']+region['width']]
        # end_time = time.perf_counter()  # 结束计时
        # elapsed_time = (end_time - start_time) * 1000  # 计算耗时（毫秒）
        # print(f"切片耗时: {elapsed_time:.2f} ms")
        return result
    except Exception as e:
        print(f"获取范围截图出现异常: {e}")
        return image2bgr(take_screenshot_mss(region))


def image2gray(screenshot):
    # 先转NumPy数组再转灰度
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2GRAY)


def image2bgr(screenshot):
    # 先转NumPy数组再转BGR
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2BGR)


# 图像二值化处理
def adaptive_threshold(image, block_size=7, c=-10):
    return cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, block_size, c)


# 计算截图与模板各个位置的相似度,返回最大相似度
def match_image(screenshot, template):
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    return max_val, max_loc


# 获取指定坐标的颜色信息
def get_pixel_color(x, y):
    global last_frame
    try:
        b, g, r = last_frame[y, x, :]
        return int(r), int(g), int(b)
    except Exception as e:
        print(f"获取坐标颜色出现异常, 坐标地址x:{x}, y:{y}, e: {e}")
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
    # y = 1341
    y = config.bullet_index[1]

    # 判断是否打能量饮料
    color1 = get_pixel_color(config.energy_drink_index[0], config.energy_drink_index[1])
    r, g, b = color1
    # 加速图标亮起, 认为此时打了能量, 上移能量条的高度
    if r > 200 and g > 200 and b > 200:
        y = y - config.energy_drink_index[2]

    # 判断是否防毒背包
    color1 = get_pixel_color(config.antivirus_backpack_index[0], config.antivirus_backpack_index[1])
    r, g, b = color1
    # 有防毒条认为佩戴防毒背包, 上移防毒条的高度
    if 5 <= r <= 9 and 158 <= g <= 162 and 245 <= b <= 249:
        y = y - config.antivirus_backpack_index[2]

    # 根据第2颗子弹是否亮起判断是否佩戴全自动或半自动武器
    color = get_pixel_color(config.bullet_index[0], y)
    r, g, b = color
    return r > 200 and g > 200 and b > 200


# 判断是否打开背包
def is_open_backpack():
    color = get_pixel_color(config.backpack_index[0], config.backpack_index[1])
    r, g, b = color
    return r > 250 and g > 250 and b > 250


# 更新武器和后坐力系数
def update_weapon_and_coefficient():
    global update_last_weapon_name
    global update_coefficient
    coefficient = calculate_recoil_coefficient()
    if update_last_weapon_name != last_weapon_name or update_coefficient != coefficient:
        update_last_weapon_name = last_weapon_name
        update_coefficient = coefficient
        with open(config.lua_config_path, 'w', encoding='utf-8') as file:
            file.write(f"GunName = '{update_last_weapon_name}'\n")
            file.write(f"RecoilCoefficient = {update_coefficient}\n")


# =========================================>> 核心识别逻辑 <<============================================


# 监控当前武器
def firearm_monitor(templates, overlay_model):
    global last_weapon_name, last_weapon_no

    while True:
        start_time = time.time()
        screenshot = adaptive_threshold(cv2.cvtColor(take_screenshot_dxgi(config.weapon_screenshot_area), cv2.COLOR_BGR2GRAY))
        match_found = False

        max_val_list = {}
        text_list = []

        if is_wear_fully_automatic_rifle():
            for name, template in templates.items():
                max_val, max_loc = match_image(screenshot, template)

                # 常用队列统计相似度
                if overlay_model is not None:
                    text_list.append(f"{name}相似度: {max_val}\n")

                if max_val >= config.weapon_recognition_confidence_threshold_list.get(name):
                    max_val_list[name] = max_val, max_loc

            if len(max_val_list) > 0:
                name = max(max_val_list, key=lambda x: max_val_list[x][0])

                # 判断图片位置
                if max_val_list[name][1][1] > 75:
                    no = 1
                else:
                    no = 2

                # 识别结果不同时更新
                if last_weapon_name != name or last_weapon_no != no:
                    last_weapon_name = name
                    last_weapon_no = no
                    update_weapon_and_coefficient()
                    str_msg = f"耗时: {(time.time() - start_time) * 1000:.2f} ms, 更新时相似度: {max_val_list.get(name)} 当前{no}号位使用武器: {name}"
                    print(str_msg)

                    if overlay_model is not None:
                        overlay_model.update_text2(str_msg)

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
        time.sleep(config.firearm_monitor_interval)


def firearms_fittings_match(screenshot, template_list):
    max_val_list = {}
    img = adaptive_threshold(screenshot)
    for name, template in template_list.items():
        max_val, max_loc = match_image(img, template)
        if max_val >= 0.65:
            max_val_list[name] = max_val
    return max_val_list


def calculate_final_fittings(max_val_list):
    if len(max_val_list) > 0:
        last_name = max(max_val_list, key=max_val_list.get)
        similarity = max_val_list.get(last_name)
    else:
        last_name = "None"
        similarity = 0
    return last_name, similarity


# 监控当前武器配件
def accessories_monitor(grips_template_list, muzzles_template_list, butt_template_list, sight_template_list,
                        grips_template_list2, muzzles_template_list2, butt_template_list2, sight_template_list2,
                        overlay_model):

    global last_muzzle_name, last_grip_name, last_butt_name, last_sight_name
    global last_muzzle_name2, last_grip_name2, last_butt_name2, last_sight_name2

    while True:
        start_time = time.time()
        if is_open_backpack():

            screenshot_muzzles = cv2.cvtColor(take_screenshot_dxgi(config.muzzle_screenshot_area), cv2.COLOR_BGR2GRAY)
            screenshot_grips = cv2.cvtColor(take_screenshot_dxgi(config.grip_screenshot_area), cv2.COLOR_BGR2GRAY)
            screenshot_butt = cv2.cvtColor(take_screenshot_dxgi(config.butt_screenshot_area), cv2.COLOR_BGR2GRAY)
            screenshot_sight = cv2.cvtColor(take_screenshot_dxgi(config.sight_screenshot_area), cv2.COLOR_BGR2GRAY)

            screenshot_muzzles2 = cv2.cvtColor(take_screenshot_dxgi(config.muzzle_screenshot_area2), cv2.COLOR_BGR2GRAY)
            screenshot_grips2 = cv2.cvtColor(take_screenshot_dxgi(config.grip_screenshot_area2), cv2.COLOR_BGR2GRAY)
            screenshot_butt2 = cv2.cvtColor(take_screenshot_dxgi(config.butt_screenshot_area2), cv2.COLOR_BGR2GRAY)
            screenshot_sight2 = cv2.cvtColor(take_screenshot_dxgi(config.sight_screenshot_area2), cv2.COLOR_BGR2GRAY)

            # 1号位
            # 循环枪口
            muzzles_max_val_list = firearms_fittings_match(screenshot_muzzles, muzzles_template_list)
            # 循环握把
            grip_max_val_list = firearms_fittings_match(screenshot_grips, grips_template_list)
            # 循环枪托
            butt_max_val_list = firearms_fittings_match(screenshot_butt, butt_template_list)
            # 循环瞄准镜
            sight_max_val_list = firearms_fittings_match(screenshot_sight, sight_template_list)

            last_muzzle_name, muzzle_similarity = calculate_final_fittings(muzzles_max_val_list)
            last_grip_name, grip_similarity = calculate_final_fittings(grip_max_val_list)
            last_butt_name, butt_similarity = calculate_final_fittings(butt_max_val_list)
            last_sight_name, sight_similarity = calculate_final_fittings(sight_max_val_list)

            # 2号位
            # 循环枪口
            muzzles_max_val_list2 = firearms_fittings_match(screenshot_muzzles2, muzzles_template_list2)
            # 循环握把
            grip_max_val_list2 = firearms_fittings_match(screenshot_grips2, grips_template_list2)
            # 循环枪托
            butt_max_val_list2 = firearms_fittings_match(screenshot_butt2, butt_template_list2)
            # 循环瞄准镜
            sight_max_val_list2 = firearms_fittings_match(screenshot_sight2, sight_template_list2)

            last_muzzle_name2, muzzle_similarity2 = calculate_final_fittings(muzzles_max_val_list2)
            last_grip_name2, grip_similarity2 = calculate_final_fittings(grip_max_val_list2)
            last_butt_name2, butt_similarity2 = calculate_final_fittings(butt_max_val_list2)
            last_sight_name2, sight_similarity2 = calculate_final_fittings(sight_max_val_list2)

            # 更新系数
            update_weapon_and_coefficient()

            if overlay_model is not None:
                overlay_model.update_text3(f"检测背包完毕 ===> 耗时: {(time.time() - start_time) * 1000:.2f} ms")
                text_list = [f"1号位当前使用枪口: {last_muzzle_name} 相似度: {muzzle_similarity:.2f}\n",
                             f"1当前使用握把: {last_grip_name} 相似度: {grip_similarity:.2f}\n",
                             f"1当前使用枪托: {last_butt_name} 相似度: {butt_similarity:.2f}\n",
                             f"1当前使用瞄具: {last_sight_name} 相似度: {sight_similarity:.2f}\n",
                             f"2号位当前使用枪口: {last_muzzle_name2} 相似度: {muzzle_similarity2:.2f}\n",
                             f"2当前使用握把: {last_grip_name2} 相似度: {grip_similarity2:.2f}\n",
                             f"2当前使用枪托: {last_butt_name2} 相似度: {butt_similarity2:.2f}\n",
                             f"2当前使用瞄具: {last_sight_name2} 相似度: {sight_similarity2:.2f}\n"]
                overlay_model.update_text4(" ".join(text_list))
            print(f"检测背包完毕 ===> 耗时: {(time.time() - start_time) * 1000:.2f} ms")
        else:
            if overlay_model is not None:
                overlay_model.update_text3(f"未打开背包 ===> 耗时: {(time.time() - start_time) * 1000:.2f} ms")
                text_list = [f"1号位当前使用枪口: {last_muzzle_name} \n",
                             f"1号位当前使用握把: {last_grip_name} \n",
                             f"1号位当前使用枪托: {last_butt_name} \n",
                             f"1号位当前使用瞄具: {last_sight_name} \n",
                             f"2号位当前使用枪口: {last_muzzle_name2} \n",
                             f"2号位当前使用握把: {last_grip_name2} \n",
                             f"2号位当前使用枪托: {last_butt_name2} \n",
                             f"2号位当前使用瞄具: {last_sight_name2} \n"]
                overlay_model.update_text4(" ".join(text_list))

        # 等待间隔时间
        time.sleep(config.accessories_monitor_interval)


def posture_monitor():
    global posture_state
    while True:
        color1 = get_pixel_color(config.posture_2_index[0], config.posture_2_index[1])
        r, g, b = color1
        if r > 200 and g > 200 and b > 200:
            posture = 2
        else:
            color2 = get_pixel_color(config.posture_3_index[0], config.posture_3_index[1])
            r2, g2, b2 = color2
            if r2 > 200 and g2 > 200 and b2 > 200:
                posture = 3
            else:
                posture = 1
        if posture_state != posture:
            posture_state = posture
            update_weapon_and_coefficient()
        time.sleep(config.posture_monitor_interval)


def coefficient_monitor(overlay_model, interval):
    while True:
        try:
            with open(config.lua_config_path, 'r', encoding='utf-8') as file:
                lua_config = file.read()
            if lua_config:
                overlay_model.update_text5(lua_config)
        except Exception as e:
            print(e)
        time.sleep(interval)


# 按键监控截图
def on_press(key):
    try:
        char = key.char.lower()
        if config.is_open_screenshot_of_keystrokes and char == 'k':
            print("> 正在截取屏幕...")
            dir_name = "screenshots"
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)

            datestr = datetime.datetime.now().strftime('%Y%m%d_%H%M%S%f')
            weapon_filename = os.path.join(dir_name, f"weapon_ad_{datestr}.png")
            muzzle_filename = os.path.join(dir_name, f"muzzle_ad_{datestr}.png")
            grip_filename = os.path.join(dir_name, f"grip_ad_{datestr}.png")
            butt_filename = os.path.join(dir_name, f"butt_ad_{datestr}.png")
            sight_filename = os.path.join(dir_name, f"sight_ad_{datestr}.png")
            muzzle_filename2 = os.path.join(dir_name, f"muzzle2_ad_{datestr}.png")
            grip_filename2 = os.path.join(dir_name, f"grip2_ad_{datestr}.png")
            butt_filename2 = os.path.join(dir_name, f"butt2_ad_{datestr}.png")
            sight_filename2 = os.path.join(dir_name, f"sight2_ad_{datestr}.png")

            cv2.imwrite(weapon_filename, image2bgr(take_screenshot_mss(config.weapon_screenshot_area)))
            cv2.imwrite(muzzle_filename, image2bgr(take_screenshot_mss(config.muzzle_screenshot_area)))
            cv2.imwrite(grip_filename, image2bgr(take_screenshot_mss(config.grip_screenshot_area)))
            cv2.imwrite(butt_filename, image2bgr(take_screenshot_mss(config.butt_screenshot_area)))
            cv2.imwrite(sight_filename, image2bgr(take_screenshot_mss(config.sight_screenshot_area)))
            cv2.imwrite(muzzle_filename2, image2bgr(take_screenshot_mss(config.muzzle_screenshot_area2)))
            cv2.imwrite(grip_filename2, image2bgr(take_screenshot_mss(config.grip_screenshot_area2)))
            cv2.imwrite(butt_filename2, image2bgr(take_screenshot_mss(config.butt_screenshot_area2)))
            cv2.imwrite(sight_filename2, image2bgr(take_screenshot_mss(config.sight_screenshot_area2)))

            # name1 = os.path.join(dir_name, f"mss_{datestr}.png")
            # name2 = os.path.join(dir_name, f"dxgi_{datestr}.png")
            # name3 = os.path.join(dir_name, f"dxgi_re_{datestr}.png")
            #
            # cv2.imwrite(name1, image2bgr(take_screenshot_mss(config.muzzle_screenshot_area)))
            #
            # cv2.imwrite(name2, take_screenshot_dxgi(config.muzzle_screenshot_area))

            # camera = dxcam.create(output_color="BGR")
            # left = config.muzzle_screenshot_area['left']
            # top = config.muzzle_screenshot_area['top']
            # right = left + config.muzzle_screenshot_area['width']
            # bottom = top + config.muzzle_screenshot_area['height']
            # img = camera.grab((left, top, right, bottom))
            # cv2.imwrite(name3, img)

            print("> 截图已保存:")
            print(f"> 右下角武器区域截图,请确保截图范围包括两把武器: {weapon_filename}")
            print(f"> 打开背包的枪口截图: {muzzle_filename}")
            print(f"> 打开背包的握把截图: {grip_filename}")
            print(f"> 打开背包的枪托截图: {butt_filename}")
            print(f"> 打开背包的瞄具截图: {sight_filename}")
    except AttributeError as e:
        print(e)

# =========================================>> 线程初始化 <<============================================


def reset_all():
    global last_weapon_name
    global last_weapon_no
    global last_muzzle_name
    global last_grip_name
    global last_butt_name
    global last_sight_name
    global last_muzzle_name2
    global last_grip_name2
    global last_butt_name2
    global last_sight_name2
    global posture_state
    last_weapon_name = "None"
    last_weapon_no = 1
    last_muzzle_name = 'None'
    last_grip_name = 'None'
    last_butt_name = 'None'
    last_sight_name = 'None'
    last_muzzle_name2 = 'None'
    last_grip_name2 = 'None'
    last_butt_name2 = 'None'
    last_sight_name2 = 'None'
    posture_state = 1
    update_weapon_and_coefficient()


def decrypt_message(ciphertext_str, private_pem_str):
    private_key = serialization.load_pem_private_key(
        private_pem_str.encode("utf-8"),
        password=None,
    )
    ciphertext = base64.b64decode(ciphertext_str.encode("utf-8"))
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    plaintext_str = plaintext.decode("utf-8")
    return plaintext_str


def verify_activation_code():
    try:
        with open('激活码.txt', 'r', encoding='utf-8') as file:
            activation_code = file.read()
        if activation_code:
            plaintext_str = decrypt_message(activation_code, config.private_key)
            is_succeed = False
            if plaintext_str.startswith("expiration_"):
                match = re.search(r"expiration_(\d+)", plaintext_str)
                if match:
                    timestamp_str = match.group(1)
                    timestamp = int(timestamp_str)
                    date = datetime.datetime.fromtimestamp(timestamp)
                    if date:
                        if datetime.datetime.now() > date:
                            print("> 激活码已过期,请联系客服获取最新激活码")
                            exit_application()
                        else:
                            # 格式化输出日期和时间
                            is_succeed = True
                            formatted_date = date.strftime("%Y-%m-%d %H:%M:%S")
                            print("> 激活成功! 有效期至:" + formatted_date)

            if not is_succeed:
                print("> 请输入有效的激活码")
                exit_application()
        else:
            print("> 请输入激活码")
            exit_application()

    except Exception as e:
        print("> 激活码无效")
        exit_application()


def exit_application():
    for i in range(3, 0, -1):  # 倒计时 3 秒
        print(f"> 程序将在 {i} 秒后退出...")
        time.sleep(1)  # 暂停 1 秒
    sys.exit()


def realtime_config_monitor():
    global config
    while True:
        config = load_configuration()
        time.sleep(config.config_monitor_interval)


def signal_handler(sig, frame):
    print("正在关闭程序...")


# dxgi截图线程
def dxgi_screenshot():
    global last_frame
    camera = dxcam.create(output_color="BGR")
    target_sleep_ms = 20  # 目标休眠时间，单位为毫秒

    while True:
        start_time = time.perf_counter()  # 记录开始时间

        try:
            frame = camera.grab()
            if frame is not None:
                last_frame = frame
        except Exception as e:
            print(f"截图出现异常: {e}")

        elapsed_ms = (time.perf_counter() - start_time) * 1000  # 计算运行时间，单位为毫秒
        actual_sleep_ms = max(0, int(target_sleep_ms - elapsed_ms))  # 计算实际休眠时间

        time.sleep(actual_sleep_ms / 1000)  # 执行休眠


if __name__ == "__main__":
    print("Starting the application...")
    print("> 验证程序中... ")
    print("> ")
    verify_activation_code()
    print("> ")
    # 验证激活码
    print("> 当前程序运行中,请保持窗口开启 ")
    print("> ")

    # 设置按键监听器
    if config.is_open_screenshot_of_keystrokes:
        keyboard.Listener(on_press=on_press).start()

    overlay = None

    if config.is_open_overlay:
        # 创建监控窗口
        overlay = TextOverlay(tk.Tk(), config.overlay_position[0], config.overlay_position[1])
        # 启动监控线程
        coefficient_thread = threading.Thread(target=coefficient_monitor, daemon=True, args=(overlay, config.coefficient_monitor_interval))
        coefficient_thread.start()
        print("> 计算系数监控中...")

    if config.enable_realtime_configuration:
        # 动态更新配置文件
        config_thread = threading.Thread(target=realtime_config_monitor, daemon=True)
        config_thread.start()
        print("> 已启用动态配置")

    # 重置枪械, 姿势, 和配件
    reset_all()

    # 启动截图线程
    screenshot_thread = threading.Thread(target=dxgi_screenshot, daemon=True)
    screenshot_thread.start()

    # 启动监控姿势
    posture_thread = threading.Thread(target=posture_monitor, daemon=True)
    posture_thread.start()
    print("> 姿势监控中...")

    # 加载灰度模板
    firearms_templates = load_templates("firearms", config.firearm_list)

    grips_templates = load_templates("grips", config.grip_list)
    muzzles_templates = load_templates("muzzles", config.muzzle_list)
    butt_templates = load_templates("butt", config.butt_list)
    sight_templates = load_templates("sight", config.sight_list)

    grips_templates2 = load_templates("grips2", config.grip_list)
    muzzles_templates2 = load_templates("muzzles2", config.muzzle_list)
    butt_templates2 = load_templates("butt2", config.butt_list)
    sight_templates2 = load_templates("sight2", config.sight_list)

    # # 启动枪械监控线程
    firearm_thread = threading.Thread(target=firearm_monitor, daemon=True, args=(firearms_templates, overlay))
    firearm_thread.start()
    print("> 枪械监控中...")

    # 启动配件监控线程
    accessories_thread = threading.Thread(target=accessories_monitor, daemon=True,
                                          args=(grips_templates,
                                                muzzles_templates,
                                                butt_templates,
                                                sight_templates,
                                                grips_templates2,
                                                muzzles_templates2,
                                                butt_templates2,
                                                sight_templates2,
                                                overlay))
    accessories_thread.start()
    print("> 配件监控中...")

    # 处理退出程序
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    stop_event = threading.Event()

    if config.is_open_overlay:
        try:
            overlay.root.mainloop()
        except KeyboardInterrupt:
            overlay.root.destroy()
    else:
        while not stop_event.is_set():
            try:
                signal.pause()
            except KeyboardInterrupt:
                stop_event.set()
