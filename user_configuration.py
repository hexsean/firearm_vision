class UserConfiguration:
    def __init__(self, config):
        # 获取lua脚本读取的配置文件路径
        self.lua_config_path = config["lua_config_path"]
        # 启用实时配置
        self.enable_realtime_configuration = config["enable_realtime_configuration"]
        # 是否开启监控
        self.is_open_overlay = config["is_open_overlay"]
        # 是否开启按键截图
        self.is_open_screenshot_of_keystrokes = config["is_open_screenshot_of_keystrokes"]
        # 获取武器区分12高度
        self.weapon_altitude = config["weapon_altitude"]
        # 获取武器截图区域(left, top, width, height)
        self.weapon_screenshot_area = config["weapon_screenshot_area"]
        # 获取屏幕高度(像素)
        self.screen_height = config["screen_resolution"][1]
        # 获取1号位武器配件=> 枪口 =>截图区域(left, top, width, height)
        self.muzzle_screenshot_area = config["muzzle_screenshot_area"]
        # 获取1号位武器配件=> 握把 =>截图区域(left, top, width, height)
        self.grip_screenshot_area = config["grip_screenshot_area"]
        # 获取1号位武器配件=> 枪托 =>截图区域(left, top, width, height)
        self.butt_screenshot_area = config["butt_screenshot_area"]
        # 获取1号位武器配件=> 瞄准镜 =>截图区域(left, top, width, height)
        self.sight_screenshot_area = config["sight_screenshot_area"]

        # 获取2号位武器配件=> 枪口 =>截图区域(left, top, width, height)
        self.muzzle_screenshot_area2 = config["muzzle_screenshot_area2"]
        # 获取2号位武器配件=> 握把 =>截图区域(left, top, width, height)
        self.grip_screenshot_area2 = config["grip_screenshot_area2"]
        # 获取2号位武器配件=> 枪托 =>截图区域(left, top, width, height)
        self.butt_screenshot_area2 = config["butt_screenshot_area2"]
        # 获取2号位武器配件=> 瞄准镜 =>截图区域(left, top, width, height)
        self.sight_screenshot_area2 = config["sight_screenshot_area2"]

        # 获取垂直灵敏度倍率
        self.vertical_sensitivity_magnification = config["vertical_sensitivity_magnification"]
        # 枪械列表
        self.firearm_list = list(config["firearms"].keys())
        # 获取武器识别置信度阈值(按武器名小写)
        self.weapon_recognition_confidence_threshold_list = {
            weapon_name: data["recognition_confidence_threshold"]
            for weapon_name, data in config["firearms"].items()
        }
        # 各枪械基础系数[基础系数, 站立系数, 蹲下系数, 趴下系数]
        self.firearm_coefficient_list = {
            weapon_name: data["coefficient_list"]
            for weapon_name, data in config["firearms"].items()
        }
        # 枪口列表(无, 步枪消焰, 步枪补偿)
        self.def_muzzle = config["firearms_accessories_list"]["def_muzzle"]
        self.muzzle_list = list(config["firearms_accessories_list"]["muzzle_list"].keys())
        self.muzzle_coefficient_list = config["firearms_accessories_list"]["muzzle_list"]
        # 握把列表(无, 半截式握把, 轻型握把, 垂直握把, 拇指握把)
        self.grip_list = list(config["firearms_accessories_list"]["grip_list"].keys())
        self.grip_coefficient_list = config["firearms_accessories_list"]["grip_list"]
        # 枪托列表(无, 战术枪托, 重型枪托)
        self.butt_list = list(config["firearms_accessories_list"]["butt_list"].keys())
        self.butt_coefficient_list = config["firearms_accessories_list"]["butt_list"]
        # 瞄准镜列表(无, 红点, 全息, 二倍, 三倍, 四倍)
        self.sight_list = list(config["firearms_accessories_list"]["sight_list"].keys())
        # 瞄具系数
        self.sight_coefficient_list = config["firearms_accessories_list"]["sight_list"]
        # 监控位置
        self.overlay_position = config["overlay_position"]
        # 背包开启坐标
        self.backpack_index = config["index"]["backpack"]
        # 饮料坐标
        self.energy_drink_index = config["index"]["energy_drink"]
        # 子弹坐标
        self.bullet_index = config["index"]["bullet"]
        # 毒包坐标
        self.antivirus_backpack_index = config["index"]["antivirus_backpack"]
        # 蹲姿坐标
        self.posture_2_index = config["index"]["posture_2"]
        # 趴姿坐标
        self.posture_3_index = config["index"]["posture_3"]
        # 枪械监控间隔
        self.firearm_monitor_interval = config["interval"]["firearm_monitor_interval"]
        # 配件监控间隔
        self.accessories_monitor_interval = config["interval"]["accessories_monitor_interval"]
        # 姿势监控间隔
        self.posture_monitor_interval = config["interval"]["posture_monitor_interval"]
        # 系数监控间隔
        self.coefficient_monitor_interval = config["interval"]["coefficient_monitor_interval"]
        # 配置监控间隔
        self.config_monitor_interval = config["interval"]["config_monitor_interval"]
        # 解密私钥
        self.private_key = """
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
