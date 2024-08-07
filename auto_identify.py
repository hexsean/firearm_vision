import sys
import datetime
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
import base64
import re
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

# =========================================>> 加载动态配置 <<============================================


def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)


config = load_config()

# 获取lua脚本读取的配置文件路径
lua_config_path = config["lua_config_path"]
# 是否开启监控
is_open_overlay = config["is_open_overlay"]
# 是否开启按键截图
is_open_screenshot_of_keystrokes = config["is_open_screenshot_of_keystrokes"]
# 获取武器截图区域(left, top, width, height)
weapon_screenshot_area = config["weapon_screenshot_area"]
# 获取屏幕高度(像素)
screen_height = config["screen_resolution"][1]

# 获取1号位武器配件=> 枪口 =>截图区域(left, top, width, height)
muzzle_screenshot_area = config["muzzle_screenshot_area"]
# 获取1号位武器配件=> 握把 =>截图区域(left, top, width, height)
grip_screenshot_area = config["grip_screenshot_area"]
# 获取1号位武器配件=> 枪托 =>截图区域(left, top, width, height)
butt_screenshot_area = config["butt_screenshot_area"]
# 获取1号位武器配件=> 瞄准镜 =>截图区域(left, top, width, height)
sight_screenshot_area = config["sight_screenshot_area"]

# 获取垂直灵敏度倍率
vertical_sensitivity_magnification = config["vertical_sensitivity_magnification"]

# 枪械列表
firearm_list = list(config["firearms"].keys())

# 获取武器识别置信度阈值(按武器名小写)
weapon_recognition_confidence_threshold_list = {
    weapon_name: data["recognition_confidence_threshold"]
    for weapon_name, data in config["firearms"].items()
}

# 各枪械基础系数[基础系数, 站立系数, 蹲下系数, 趴下系数]
firearm_coefficient_list = {
    weapon_name: data["coefficient_list"]
    for weapon_name, data in config["firearms"].items()
}

# 枪口列表(无, 步枪消焰, 步枪补偿)
muzzle_list = list(config["firearms_accessories_list"]["muzzle_list"].keys())
muzzle_coefficient_list = config["firearms_accessories_list"]["muzzle_list"]

# 握把列表(无, 半截式握把, 轻型握把, 垂直握把, 拇指握把)
grip_list = list(config["firearms_accessories_list"]["grip_list"].keys())
grip_coefficient_list = config["firearms_accessories_list"]["grip_list"]

# 枪托列表(无, 战术枪托, 重型枪托)
butt_list = list(config["firearms_accessories_list"]["butt_list"].keys())
butt_coefficient_list = config["firearms_accessories_list"]["butt_list"]

# 瞄准镜列表(无, 红点, 全息, 二倍, 三倍, 四倍)
sight_list = list(config["firearms_accessories_list"]["sight_list"].keys())
sight_coefficient_list = config["firearms_accessories_list"]["sight_list"]

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

# =========================================>> tool函数初始化 <<============================================


# 计算后坐力系数(分辨率系数 * 垂直灵敏度系数 * 配件系数 * 姿势系数)
def calculate_recoil_coefficient():
    # 分辨率系数(与fov相关, 暂不参与计算)
    screen_coefficient = 1
    # 垂直灵敏度系数
    vertical_coefficient = 1 / vertical_sensitivity_magnification
    # 默认为裸配, 默认弹道为补偿三角(战术枪托)
    muzzle_coefficient = muzzle_coefficient_list.get(last_muzzle_name, 1.265)
    grip_coefficient = grip_coefficient_list.get(last_grip_name, 1)
    butt_coefficient = butt_coefficient_list.get(last_butt_name, 1)
    sight_coefficient = sight_coefficient_list.get(last_sight_name, 1)

    # 基础枪械系数 * 姿势系数
    if last_weapon_name in firearm_coefficient_list:
        weapon_coefficients = firearm_coefficient_list[last_weapon_name]
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
    # y = 1341
    y = 1336

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


update_last_weapon_name = None
update_coefficient = 1


# 更新武器和后坐力系数
def update_weapon_and_coefficient():
    global update_last_weapon_name
    global update_coefficient
    coefficient = calculate_recoil_coefficient()
    if update_last_weapon_name != last_weapon_name or update_coefficient != coefficient:
        update_last_weapon_name = last_weapon_name
        update_coefficient = coefficient
        with open(lua_config_path, 'w', encoding='utf-8') as file:
            file.write(f"GunName = '{update_last_weapon_name}'\n")
            file.write(f"RecoilCoefficient = {update_coefficient}\n")


# =========================================>> 核心识别逻辑 <<============================================


# 监控当前武器
def firearm_monitor_screen(templates, interval, overlay_model):
    global last_weapon_name

    while True:
        start_time = time.time()
        screenshot = adaptive_threshold(convert_to_gray(take_screenshot_mss(weapon_screenshot_area)))
        match_found = False

        max_val_list = {}
        text_list = []

        if is_wear_fully_automatic_rifle():
            for name, template in templates.items():
                max_val = match_image(screenshot, template)

                # 常用队列统计相似度
                if overlay_model is not None:
                    text_list.append(f"{name}相似度: {max_val}\n")

                if max_val >= weapon_recognition_confidence_threshold_list.get(name):
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
            muzzle_img = adaptive_threshold(convert_to_gray(take_screenshot_mss(muzzle_screenshot_area)))
            for name, template in muzzles_template_list.items():
                max_val = match_image(muzzle_img, template)
                if max_val >= 0.65:
                    muzzles_max_val_list[name] = max_val

            # 循环握把
            grip_img = adaptive_threshold(convert_to_gray(take_screenshot_mss(grip_screenshot_area)))
            for name, template in grips_template_list.items():
                max_val = match_image(grip_img, template)
                if max_val >= 0.65:
                    grip_max_val_list[name] = max_val

            # 循环枪托
            butt_img = adaptive_threshold(convert_to_gray(take_screenshot_mss(butt_screenshot_area)))
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
            if overlay_model is not None:
                overlay_model.update_text3(f"未打开背包 当前枪口{last_muzzle_name}, 握把{last_grip_name}, 枪托{last_butt_name}, 瞄具{last_sight_name}, 耗时: {(time.time() - start_time) * 1000:.2f} ms")
                overlay_model.update_text4("")

        # 等待间隔时间
        time.sleep(interval)


def monitor_firearms(interval, overlay_model):
    global posture_state
    while True:
        posture = None
        color1 = get_pixel_color(1415, 1333)
        r, g, b = color1
        # 加速图标亮起, 认为此时打了能量, 上移能量条的高度
        if r > 200 and g > 200 and b > 200:
            posture = 2
        else:
            color2 = get_pixel_color(1420, 1351)
            r2, g2, b2 = color2
            if r2 > 200 and g2 > 200 and b2 > 200:
                posture = 3
            else:
                posture = 1
        if posture_state != posture:
            posture_state = posture
            update_weapon_and_coefficient()
        time.sleep(interval)


def monitor_coefficient(interval, overlay_model):
    while True:
        try:
            with open(lua_config_path, 'r', encoding='utf-8') as file:
                lua_config = file.read()
            if lua_config:
                overlay_model.update_text8(lua_config)
        except Exception as e:
            print(e)
        time.sleep(interval)


# 监控姿势主入口
def monitor_posture_main(overlay_model):
    print("姿势监控中...\n")
    # 启动监控线程
    monitor_thread = threading.Thread(target=monitor_firearms, args=(0.05, overlay_model))
    monitor_thread.start()


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
                                      args=(grips_templates, muzzles_templates, butt_templates, 0.1, overlay_model))
    monitor_thread.start()


def monitor_coefficient_main(overlay_model):
    print("最终系数监控中...\n")
    # 启动监控线程
    monitor_thread = threading.Thread(target=monitor_coefficient, args=(0.1, overlay_model))
    monitor_thread.start()


# 按键监控截图
def on_press(key):
    try:
        char = key.char.lower()
        if is_open_screenshot_of_keystrokes and char == 'k':
            print("正在截取屏幕...")
            dir_name = "screenshots"
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            # 保存截图用于调试
            # weapon_filename = os.path.join(dir_name, f"weapon_ad_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}.png")
            # grip_filename = os.path.join(dir_name, f"grip_ad_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}.png")
            muzzle_filename = os.path.join(dir_name, f"muzzle_ad_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S%f')}.png")
            # butt_filename = os.path.join(dir_name, f"butt_ad_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}.png")

            # cv2.imwrite(weapon_filename,
            #             adaptive_threshold(convert_to_gray(take_screenshot_mss(weapon_screenshot_area))))
            # cv2.imwrite(grip_filename,
            #             adaptive_threshold(convert_to_gray(take_screenshot_mss(grip_screenshot_area))))
            cv2.imwrite(muzzle_filename, take_screenshot_mss(muzzle_screenshot_area))
            # cv2.imwrite(butt_filename,
            #             adaptive_threshold(convert_to_gray(take_screenshot_mss(butt_screenshot_area))))
    except AttributeError as e:
        print(e)

# =========================================>> 线程初始化 <<============================================


def reset_all():
    global last_weapon_name
    global last_muzzle_name
    global last_grip_name
    global last_butt_name
    global last_sight_name
    global posture_state
    last_weapon_name = "None"
    last_muzzle_name = 'None'
    last_grip_name = 'None'
    last_butt_name = 'None'
    last_sight_name = 'None'
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


privateKey = """
-----BEGIN PRIVATE KEY-----
MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDVLOXv9jUG35lf
x7C0hI2CwcJvZQUbwowPdKHpyoOceCP23fZrntCJV2aNXnuDtmfCmirgLI3N814L
3m/IN3pbCOY8SVbKXWpeWTUHKQgluQqQREkDU6InflKkiMF2/rJWDY2m5tkhgYM4
0dzk25U43xEABZy1KnWCfQQQypAtpCQOD4Mb96UueY5idhlwLfkoDq0IIIRlKSD+
Gzs9iY0HXMV+V86hqz/cRgy6gdx2hyMyHjcWg5O/9n+iITSo138UxCHDUvrxR8Q0
fJ1vJwDEj1DdqIHx7CMa0PRexa6AvEr/LTlcGOKBnPijw5Gbgw88wAgurGC0I6XS
AHl+MJZDAgMBAAECggEAB/duE7omlX5XW9TOyJLoO5nkcMechG2QULw3QtFD0DNN
229vF+rZozr7b6QMx0l9S4X5vTfyXV8kxW/Hdfrbco8najBZcyWWOza9PGpu+K3s
yaMWUW6s3Cn536vmraeWCuY7GXYoviT6E5kFgXNSpSCc9jG/f1EPZCl/ieXFXpc2
xOaQeLx+v3M+vY8YgCpdJuO6vK/V3efVUhWUncz41ObunvUhGXx9tZQv4Qzfalz1
lHQpd6iRM7PIn/grT369nRnsYvKlEx/hIiqlyLpu3HxrB80ebVevM0aOoxz93+9M
JaTs8v7unPGQ/s5vqe9jCNZaXiE/ZUHAIa24okZjrQKBgQD2T8P38HnhwLL2yyZl
JkgAzfqKzmP/+ocmvQkyHuLspWxiP/vzq+Zgmk2jBOCCXJosM5mtROsfqVjZeToG
2XYnTzvbck67HEn4fjGlBGWCBTXPcc77Yp6pnkAZ+AWBfTqUdHxCjbvmcxc6rVAT
g5op6RcNWEPEFnvyy9snvgr71QKBgQDdj3e8gl9q+KNvLXqobr2AyIExUh45tT4v
OOkO4YvsgfLOiHDtukjd/v90kp9wce6A+gzUicznqktRjg2HJQiN/AnVyn08LigD
srEzigDuwTyaQgqYBQECgY5e/cs0WwdXFNTS7WKDV8sZ2pFEmbmVdqK0TVivueEL
CrDLDXnNtwKBgQDUAGPUDA9b19gxwzkQ5poi1ydGQc6gjKm3Fg3MLflzZg6boibh
3Js1mpooLhJvIfUxBljHYgJeBgyLYmQncRTZUMFcaE6LjhW85CEmv1n/RyzBmFtm
08NsiuDxeSCEC51YGcq6HfQUrgrYXkQGB8exOwa0Xbw2EoQsvnmrA0/A4QKBgQDE
sEyXqRWUHU7ZsAIn7MeGwHkQk9oJWQDvYxJjB4/0Uhh/iVjXcnylt26IynGInVwi
W9lwBTVGpENhDz6rLxE9GvaQOMac2kzjm4r8OhNB4YIvX1mQQ0D2PJVrdtsii30k
rXWSGvNNrm67cPFteRrruPoQHmoQ9m72InN4j2oGWQKBgQDRgrT4zH2WzOeP4Gcg
7IlO4QmXLP2GQ4082YsiHw6jQV9xV8Ae6miJbKbLpWpNy6/pbS+/7kAv3cP8vjX3
SGcY6bTvTalstJfiGi2j5arCFKnt1KEyHH98UCu6reR96WSZe+z1+fksqEg/fGC5
anPr6Cll/DsAcaY61iX+B1Rxsg==
-----END PRIVATE KEY-----
"""


def verify_activation_code():
    try:
        with open('激活码.txt', 'r', encoding='utf-8') as file:
            activation_code = file.read()
        if activation_code:
            plaintext_str = decrypt_message(activation_code, privateKey)
            is_succeed = False
            if plaintext_str.startswith("expiration_"):
                match = re.search(r"expiration_(\d+)", plaintext_str)
                if match:
                    timestamp_str = match.group(1)
                    timestamp = int(timestamp_str)
                    date = datetime.datetime.fromtimestamp(timestamp)
                    if date:
                        if datetime.datetime.now() > date:
                            print("===>  激活码已过期,请联系客服获取最新激活码")
                            exit_application()
                        else:
                            # 格式化输出日期和时间
                            is_succeed = True
                            formatted_date = date.strftime("%Y-%m-%d %H:%M:%S")
                            print("===>  激活成功! 有效期至:" + formatted_date)

            if not is_succeed:
                print("===>  请输入有效的激活码")
                exit_application()
        else:
            print("===>  请输入激活码")
            exit_application()

    except Exception as e:
        print("===>  激活码无效")
        exit_application()


def exit_application():
    for i in range(3, 0, -1):  # 倒计时 3 秒
        print(f"程序将在 {i} 秒后退出...")
        time.sleep(1)  # 暂停 1 秒
    sys.exit()


if __name__ == "__main__":
    print("Starting the application...")
    # 验证激活码
    verify_activation_code()
    # 设置按键监听器
    if is_open_screenshot_of_keystrokes:
        keyboard.Listener(on_press=on_press).start()
    print("程序运行中,请保持窗口开启 =====> \n")
    overlay = None
    if is_open_overlay:
        # 创建监控窗口
        overlay = TextOverlay(tk.Tk(), config["overlay_position"][0], config["overlay_position"][1])
        monitor_coefficient_main(overlay)

    # 重置枪械, 姿势, 和配件
    reset_all()

    # 启动监控姿势
    monitor_posture_main(overlay)
    # 启动枪械监控线程
    monitor_firearms_main(overlay)
    # 启动配件监控线程
    monitor_accessories_main(overlay)
    if is_open_overlay:
        overlay.root.mainloop()
