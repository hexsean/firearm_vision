import time

import cv2
import dxcam
import mss
import numpy as np

# 截图次数
num_screenshots = 100
camera = dxcam.create(output_color="GRAY")

# DXGI 截图函数
def dxcam_screenshot():
    global camera
    return camera.grab(region=(0, 0, 2000, 1000))  # 获取截图
    # camera.stop()  # 停止 DXCam

# MSS 截图函数
def mss_screenshot():
    with mss.mss() as sct:
        img = sct.grab({'top': 0, 'left': 0, 'width': 2000, 'height': 1000})
        return cv2.cvtColor(np.array(img), cv2.COLOR_BGRA2GRAY)

# DXCam 性能测试 & 保存图片
start_time = time.perf_counter_ns()
for i in range(num_screenshots):
    frame = dxcam_screenshot()
dxcam_time = (time.perf_counter_ns() - start_time) / 1e6
print(f"DXCam: {num_screenshots} screenshots in {dxcam_time:.2f} ms")
    # cv2.imwrite(f"dxcam_screenshot_{i}.png", frame)  # 保存 DXCam 截图


# MSS 性能测试 & 保存图片
start_time = time.perf_counter_ns()
for i in range(num_screenshots):
    gray_img = mss_screenshot()
mss_time = (time.perf_counter_ns() - start_time) / 1e6
print(f"MSS: {num_screenshots} screenshots in {mss_time:.2f} ms")
    # cv2.imwrite(f"mss_screenshot_{i}.png", gray_img)  # 保存 MSS 截图 (灰度图)


# 停止 DXCam (在所有截图完成后)
camera.stop()
