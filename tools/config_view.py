import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import json
import os

import cv2
import dxcam


class ConfigGUI:
    def __init__(self, master):
        self.master = master
        master.title("自动识别程序配置")
        master.geometry('600x700')

        # 创建 Notebook选项卡
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.isLoadConfig = False
        # 原始配置数据
        self.config_data = {}

        # UI 变量
        self.ui_vars = {}

        # 配置文件路径
        self.config_file_path = tk.StringVar(value=os.path.join(os.path.dirname(__file__), "config.json"))

        self.camera = dxcam.create(output_color="BGR")

        # 加载和保存按钮 - 放在主窗口底部
        button_frame = tk.Frame(master)
        button_frame.pack(side=tk.BOTTOM, pady=10)  # 放在底部，设置垂直间距

        load_button = tk.Button(button_frame, text="加载配置", command=self.load_config)
        load_button.pack(side=tk.LEFT, padx=5)  # 放在左边，设置水平间距

        save_button = tk.Button(button_frame, text="保存配置", command=self.save_config)
        save_button.pack(side=tk.LEFT, padx=5)  # 放在左边，设置水平间距

        # 基本配置
        self.create_basic_config_tab()

        # 获取截图
        self.create_screenshot_tab()

        # 截图区域设置
        self.create_screenshot_area_tab()

        # 武器配置
        self.create_firearms_config_tab()

        # 其他配置
        self.create_other_config_tab()

    def create_basic_config_tab(self):
        basic_config_tab = ttk.Frame(self.notebook)
        self.notebook.add(basic_config_tab, text="基本配置")

        # 配置文件路径
        config_file_label = tk.Label(basic_config_tab, text="配置文件路径:")
        config_file_label.grid(row=0, column=0)

        config_file_entry = tk.Entry(basic_config_tab, textvariable=self.config_file_path, width=50)
        config_file_entry.grid(row=0, column=1)

        browse_button = tk.Button(basic_config_tab, text="浏览", command=self.browse_config_file)
        browse_button.grid(row=0, column=2)

        # 实时配置开关
        self.ui_vars["enable_realtime_configuration"] = tk.BooleanVar()
        enable_realtime_config_checkbutton = tk.Checkbutton(
            basic_config_tab, text="启用实时配置", variable=self.ui_vars["enable_realtime_configuration"]
        )

        # 启用实时监控
        self.ui_vars["is_open_overlay"] = tk.BooleanVar()
        is_open_overlay_checkbutton = tk.Checkbutton(
            basic_config_tab, text="启用实时监控", variable=self.ui_vars["is_open_overlay"]
        )

        self.ui_vars["is_open_screenshot_of_keystrokes"] = tk.BooleanVar()
        is_open_screenshot_of_keystrokes_checkbutton = tk.Checkbutton(
            basic_config_tab, text="启用按键截图", variable=self.ui_vars["is_open_screenshot_of_keystrokes"]
        )

        enable_realtime_config_checkbutton.grid(row=2, column=1, columnspan=1)
        is_open_overlay_checkbutton.grid(row=3, column=1, columnspan=1)
        is_open_screenshot_of_keystrokes_checkbutton.grid(row=4, column=1, columnspan=1)

        # 垂直灵敏度放大倍数
        vertical_sensitivity_label = tk.Label(basic_config_tab, text="垂直灵敏度放大倍数:")
        vertical_sensitivity_label.grid(row=6, column=0)  # 调整行号

        vertical_sensitivity_var = tk.StringVar()
        vertical_sensitivity_entry = tk.Entry(basic_config_tab, textvariable=vertical_sensitivity_var)
        vertical_sensitivity_entry.grid(row=6, column=1)  # 调整行号
        self.ui_vars["vertical_sensitivity_magnification"] = vertical_sensitivity_var

        # 武器高度
        weapon_altitude_label = tk.Label(basic_config_tab, text="武器高度:")
        weapon_altitude_label.grid(row=7, column=0)  # 调整行号

        weapon_altitude_var = tk.StringVar()
        weapon_altitude_entry = tk.Entry(basic_config_tab, textvariable=weapon_altitude_var)
        weapon_altitude_entry.grid(row=7, column=1)  # 调整行号
        self.ui_vars["weapon_altitude"] = weapon_altitude_var

        # 屏幕分辨率控件
        screen_resolution_frame = tk.LabelFrame(basic_config_tab, text="屏幕分辨率")
        screen_resolution_frame.grid(row=8, column=1, columnspan=3, padx=10, pady=10)

        if "screen_resolution" not in self.ui_vars:
            self.ui_vars["screen_resolution"] = [tk.StringVar(), tk.StringVar()]

        screen_width_label = tk.Label(screen_resolution_frame, text="宽度:")
        screen_width_label.grid(row=0, column=0)
        screen_width_entry = tk.Entry(screen_resolution_frame, textvariable=self.ui_vars["screen_resolution"][0])
        screen_width_entry.grid(row=0, column=1)

        screen_height_label = tk.Label(screen_resolution_frame, text="高度:")
        screen_height_label.grid(row=1, column=0)
        screen_height_entry = tk.Entry(screen_resolution_frame, textvariable=self.ui_vars["screen_resolution"][1])
        screen_height_entry.grid(row=1, column=1)

    def browse_lua_config_file(self):
        filepath = filedialog.askopenfilename(
            initialdir="/",
            title="Select a File",
            filetypes=(("Lua files", "*.lua"), ("all files", "*.*"))
        )
        if filepath:
            self.config_file_path.set(filepath)

    def create_screenshot_area_tab(self):
        screenshot_area_tab = ttk.Frame(self.notebook)
        self.notebook.add(screenshot_area_tab, text="截图区域设置")

        # 创建 Canvas
        canvas = tk.Canvas(screenshot_area_tab)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)  # 填充并扩展

        # 创建 Scrollbar
        scrollbar = tk.Scrollbar(screenshot_area_tab, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 将 Canvas 与 Scrollbar 关联
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)

        # 在 Canvas 中创建 Frame
        inner_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor='nw')

        screenshot_areas = [
            ("weapon_screenshot_area", "武器截图区域"),
            ("sight_screenshot_area", "1号位瞄准镜截图区域"),
            ("muzzle_screenshot_area", "1号位枪口截图区域"),
            ("grip_screenshot_area", "1号位握把截图区域"),
            ("butt_screenshot_area", "1号位枪托截图区域"),
            ("muzzle_screenshot_area2", "2号位枪口截图区域"),
            ("grip_screenshot_area2", "2号位握把截图区域"),
            ("butt_screenshot_area2", "2号位枪托截图区域"),
            ("sight_screenshot_area2", "2号位瞄准镜截图区域")
        ]

        row_num = 0
        col_num = 0
        for config_key, frame_text in screenshot_areas:
            frame = tk.LabelFrame(inner_frame, text=frame_text)  # 将 frame 放置在 inner_frame 中
            frame.grid(row=row_num, column=col_num, padx=10, pady=10)
            self.create_screenshot_area_entries(frame, config_key)

            row_num += 1
            if row_num > 4:  # 每列最多5个
                row_num = 0
                col_num += 1

    def create_screenshot_area_entries(self, parent_frame, config_key):
        # 如果 self.config_data 中不存在该配置项，则设置默认值
        if config_key not in self.config_data:
            self.config_data[config_key] = {'left': 0, 'top': 0, 'width': 0, 'height': 0}

        # 在 ui_vars 中创建对应的字典
        self.ui_vars[config_key] = {}

        area_data = self.config_data[config_key]
        for i, key in enumerate(["left", "top", "width", "height"]):
            label = tk.Label(parent_frame, text=key + ":")
            label.grid(row=i, column=0, padx=5, pady=5)

            var = tk.StringVar(value=str(area_data[key]))  # 直接使用 config_data 中的值
            entry = tk.Entry(parent_frame, textvariable=var)
            entry.grid(row=i, column=1, padx=5, pady=5)

            self.ui_vars[config_key][key] = var

    def create_firearms_config_tab(self):
        firearms_config_tab = ttk.Frame(self.notebook)
        self.notebook.add(firearms_config_tab, text="武器配置")

        canvas = tk.Canvas(firearms_config_tab)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(firearms_config_tab, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)

        firearms_inner_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=firearms_inner_frame, anchor='nw')

        # 固定枪械列表
        firearm_names = ["akm", "qbz", "m762", "groza", "scarl", "m16a4", "aug", "m416", "k2", "g36c",
                         "mk47", "ace32", "ump", "mp5k", "vkt", "p90", "m249", "dp28", "mg3", "famae"]

        # 遍历 firearms 配置项
        for firearm_name in firearm_names:
            self.create_firearm_config_entries(firearms_inner_frame, firearm_name)

    def create_firearm_config_entries(self, parent_frame, firearm_name):
        # 如果 self.config_data["firearms"] 不存在或为空，则创建一个空字典
        if "firearms" not in self.config_data or self.config_data.get("firearms", {}) == {}:
            self.config_data["firearms"] = {}

        # 如果 self.config_data["firearms"] 中不存在该配置项，则设置默认值
        if firearm_name not in self.config_data["firearms"]:
            self.config_data["firearms"][firearm_name] = {
                'recognition_confidence_threshold': 0,
                'coefficient_list': [0, 0, 0, 0]
            }

        # 在 ui_vars 中创建对应的字典
        if "firearms" not in self.ui_vars or self.ui_vars.get("firearms", {}) == {}:
            self.ui_vars["firearms"] = {}
        self.ui_vars["firearms"][firearm_name] = {}

        firearm_data = self.config_data["firearms"][firearm_name]
        firearm_subframe = tk.LabelFrame(parent_frame, text=firearm_name)
        firearm_subframe.pack(padx=10, pady=10, fill=tk.X)

        # 识别阈值
        recognition_threshold_label = tk.Label(firearm_subframe, text="识别阈值:")
        recognition_threshold_label.grid(row=0, column=0, padx=5, pady=5)
        recognition_threshold_var = tk.StringVar(value=str(firearm_data["recognition_confidence_threshold"]))
        self.ui_vars["firearms"][firearm_name]["recognition_confidence_threshold"] = recognition_threshold_var
        recognition_threshold_entry = tk.Entry(firearm_subframe, textvariable=recognition_threshold_var)
        recognition_threshold_entry.grid(row=0, column=1, padx=5, pady=5)

        # 系数列表
        coefficient_list_frame = tk.Frame(firearm_subframe)
        coefficient_list_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        for i in range(4):
            coef_label = tk.Label(coefficient_list_frame, text=f"系数{i + 1}:")
            coef_label.grid(row=0, column=i * 2, padx=5, pady=5)
            coef_var = tk.StringVar(value=str(firearm_data["coefficient_list"][i]))
            self.ui_vars["firearms"][firearm_name][f"coefficient_list_{i}"] = coef_var
            coef_entry = tk.Entry(coefficient_list_frame, textvariable=coef_var, width=5)
            coef_entry.grid(row=0, column=i * 2 + 1, padx=5, pady=5)

    def browse_config_file(self):
        filepath = filedialog.askopenfilename(
            initialdir="/",
            title="Select a File",
            filetypes=(("Json files", "*.json"), ("all files", "*.*"))
        )
        if filepath:
            self.config_file_path.set(filepath)

    def load_config(self):
        try:
            with open(self.config_file_path.get(), 'r') as f:
                self.config_data = json.load(f)
            self.update_ui_from_config()
            self.isLoadConfig = True
        except FileNotFoundError:
            messagebox.showerror("Error", "配置文件未找到")
        except json.JSONDecodeError:
            messagebox.showerror("Error", "配置文件格式错误")
        except Exception as e:
            messagebox.showerror("Error", f"加载配置文件出错: {e}")

    def save_config(self):
        if not self.validate_config():
            messagebox.showerror("Error", "配置数据有误，请检查")
            return

        self.update_config_from_ui()

        try:
            if self.isLoadConfig:
                with open(self.config_file_path.get(), 'w') as f:
                    json.dump(self.config_data, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"保存配置文件出错: {e}")

    def validate_config(self):
        # ... 其他验证逻辑
        return True

    def update_config_from_ui(self):
        if self.isLoadConfig:
            # 基本配置
            self.config_data["enable_realtime_configuration"] = self.ui_vars["enable_realtime_configuration"].get()  # 获取 StringVar 的值
            self.config_data["is_open_overlay"] = self.ui_vars["is_open_overlay"].get()  # 获取 StringVar 的值
            self.config_data["is_open_screenshot_of_keystrokes"] = self.ui_vars["is_open_screenshot_of_keystrokes"].get()  # 获取 StringVar 的值

            try:
                self.config_data["screen_resolution"] = [
                    int(self.ui_vars["screen_resolution"][0].get()),
                    int(self.ui_vars["screen_resolution"][1].get())
                ]
            except ValueError:
                print("Error: Invalid screen resolution")

            # 屏幕截图区域
            for config_key in ["weapon_screenshot_area", "sight_screenshot_area",
                               "muzzle_screenshot_area", "grip_screenshot_area",
                               "butt_screenshot_area", "muzzle_screenshot_area2",
                               "grip_screenshot_area2", "butt_screenshot_area2",
                               "sight_screenshot_area2"]:
                for key in ["left", "top", "width", "height"]:
                    try:
                        self.config_data[config_key][key] = int(self.ui_vars[config_key][key].get())
                    except ValueError:
                        print(f"Error: Invalid value for {config_key}.{key}")
            # 垂直灵敏度放大倍数
            try:
                self.config_data["vertical_sensitivity_magnification"] = \
                    float(self.ui_vars["vertical_sensitivity_magnification"].get())
            except ValueError:
                print("Error: Invalid vertical sensitivity magnification")

            # 武器高度
            try:
                self.config_data["weapon_altitude"] = int(self.ui_vars["weapon_altitude"].get())
            except ValueError:
                print("Error: Invalid weapon altitude")

            # 武器配置
            for firearm_name, firearm_ui_vars in self.ui_vars["firearms"].items():
                try:
                    self.config_data["firearms"][firearm_name]["recognition_confidence_threshold"] = \
                        float(firearm_ui_vars["recognition_confidence_threshold"].get())
                except ValueError:
                    print(f"Error: Invalid recognition threshold for {firearm_name}")

                try:
                    self.config_data["firearms"][firearm_name]["coefficient_list"] = [
                        float(firearm_ui_vars[f"coefficient_list_{i}"].get()) for i in range(4)
                    ]
                except ValueError:
                    print(f"Error: Invalid coefficient list for {firearm_name}")

            # 其他配置项
            for config_key in ["index", "interval"]:
                for key, var in self.ui_vars[config_key].items():
                    try:
                        # 根据原始配置类型进行转换
                        if isinstance(self.config_data[config_key][key], list):
                            self.config_data[config_key][key] = [int(x) for x in var.get().split(",")]
                        elif isinstance(self.config_data[config_key][key], (int, float)):
                            self.config_data[config_key][key] = float(var.get())
                        else:
                            self.config_data[config_key][key] = var.get()
                    except ValueError:
                        print(f"Error: Invalid value for {config_key}.{key}")

            messagebox.showinfo("Success", "配置保存成功")
        else:
            messagebox.showerror("Error", "请先加载配置文件")

    def update_ui_from_config(self):
        # 基本配置
        if "enable_realtime_configuration" in self.config_data:
            self.ui_vars["enable_realtime_configuration"].set(self.config_data["enable_realtime_configuration"])
        if "is_open_overlay" in self.config_data:
            self.ui_vars["is_open_overlay"].set(self.config_data["is_open_overlay"])
        if "is_open_screenshot_of_keystrokes" in self.config_data:
            self.ui_vars["is_open_screenshot_of_keystrokes"].set(self.config_data["is_open_screenshot_of_keystrokes"])
        if "screen_resolution" in self.config_data:
            self.ui_vars["screen_resolution"][0].set(self.config_data["screen_resolution"][0])
            self.ui_vars["screen_resolution"][1].set(self.config_data["screen_resolution"][1])
        # 垂直灵敏度放大倍数
        if "vertical_sensitivity_magnification" in self.config_data:
            self.ui_vars["vertical_sensitivity_magnification"].set(
                str(self.config_data["vertical_sensitivity_magnification"])
            )

        # 武器高度
        if "weapon_altitude" in self.config_data:
            self.ui_vars["weapon_altitude"].set(str(self.config_data["weapon_altitude"]))

        # 屏幕截图区域
        for config_key in ["weapon_screenshot_area", "sight_screenshot_area",
                           "muzzle_screenshot_area", "grip_screenshot_area",
                           "butt_screenshot_area", "muzzle_screenshot_area2",
                           "grip_screenshot_area2", "butt_screenshot_area2",
                           "sight_screenshot_area2"]:
            for key in ["left", "top", "width", "height"]:
                self.ui_vars[config_key][key].set(str(self.config_data[config_key][key]))

        # 武器配置
        for firearm_name, firearm_data in self.config_data["firearms"].items():
            # 更新识别阈值
            self.ui_vars["firearms"][firearm_name]["recognition_confidence_threshold"].set(
                str(firearm_data["recognition_confidence_threshold"])
            )

            # 更新系数列表
            for i in range(4):
                self.ui_vars["firearms"][firearm_name][f"coefficient_list_{i}"].set(
                    str(firearm_data["coefficient_list"][i])
                )
        # 其他配置项
        for config_key in ["index", "interval"]:
            if config_key in self.config_data:
                for key, value in self.config_data[config_key].items():
                    self.ui_vars[config_key][key].set(str(value))  # 更新 StringVar 的值

    def create_screenshot_tab(self):
        screenshot_tab = ttk.Frame(self.notebook)
        self.notebook.add(screenshot_tab, text="截图配置")

        # 说明部分
        instructions_frame = ttk.LabelFrame(screenshot_tab, text="使用说明")
        instructions_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        instructions_text = """
        本功能用于更新配件截图。
    
        1. 程序加载配置后，进入游戏，打开背包。
        2. 确保本程序不遮挡背包右侧枪械放置区域。
        3. 一、二号位携带四配件武器，如M4或ACE32。
        4. 务必严格按照说明配置枪械，点击截图。
        """
        instructions_label = tk.Label(instructions_frame, text=instructions_text, justify=tk.LEFT, wraplength=500, anchor='w')  # 靠左对齐
        instructions_label.pack(padx=10, pady=10)

        # 按钮部分 - 使用 Canvas 和 Scrollbar 实现滚动
        canvas = tk.Canvas(screenshot_tab)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)  # 填充并扩展

        scrollbar = tk.Scrollbar(screenshot_tab, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)

        buttons_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=buttons_frame, anchor='nw')

        def take_screenshot_dxgi(frame, region):
            try:
                result = frame[region['top']:region['top']+region['height'], region['left']:region['left']+region['width']]
                return result
            except Exception as e:
                print(f"获取范围截图出现异常: {e}")

        # 截图函数入口
        def take_screenshot(button, button_text):
            if self.isLoadConfig:
                frame = self.camera.grab()
                while frame is None:
                    frame = self.camera.grab()
                muzzle_screenshot = take_screenshot_dxgi(frame, self.ui_vars["muzzle_screenshot_area"])
                grip_screenshot = take_screenshot_dxgi(frame, self.ui_vars["grip_screenshot_area"])
                butt_screenshot = take_screenshot_dxgi(frame, self.ui_vars["butt_screenshot_area"])
                sight_screenshot = take_screenshot_dxgi(frame, self.ui_vars["sight_screenshot_area"])
                muzzle_screenshot_2 = take_screenshot_dxgi(frame, self.ui_vars["muzzle_screenshot_area2"])
                grip_screenshot_2 = take_screenshot_dxgi(frame, self.ui_vars["grip_screenshot_area2"])
                butt_screenshot_2 = take_screenshot_dxgi(frame, self.ui_vars["butt_screenshot_area2"])
                sight_screenshot_2 = take_screenshot_dxgi(frame, self.ui_vars["sight_screenshot_area2"])

                image_dir = os.path.join(os.path.dirname(__file__), "image")
                # 创建目录（如果不存在）
                os.makedirs(os.path.join(image_dir, "muzzles"), exist_ok=True)
                os.makedirs(os.path.join(image_dir, "grips"), exist_ok=True)
                os.makedirs(os.path.join(image_dir, "butt"), exist_ok=True)
                os.makedirs(os.path.join(image_dir, "sight"), exist_ok=True)
                os.makedirs(os.path.join(image_dir, "muzzles2"), exist_ok=True)
                os.makedirs(os.path.join(image_dir, "grips2"), exist_ok=True)
                os.makedirs(os.path.join(image_dir, "butt2"), exist_ok=True)
                os.makedirs(os.path.join(image_dir, "sight2"), exist_ok=True)

                if button_text == "点击保存截图1":
                    cv2.imwrite(os.path.join(image_dir, "muzzles", "buchang.png"), muzzle_screenshot)
                    cv2.imwrite(os.path.join(image_dir, "grips", "chuizhi.png"), grip_screenshot)
                    cv2.imwrite(os.path.join(image_dir, "butt", "zhanshu.png"), butt_screenshot)
                    cv2.imwrite(os.path.join(image_dir, "sight", "hongdian.png"), sight_screenshot)

                    cv2.imwrite(os.path.join(image_dir, "muzzles2", "buchang.png"), muzzle_screenshot_2)
                    cv2.imwrite(os.path.join(image_dir, "grips2", "chuizhi.png"), grip_screenshot_2)
                    cv2.imwrite(os.path.join(image_dir, "butt2", "zhanshu.png"), butt_screenshot_2)
                    cv2.imwrite(os.path.join(image_dir, "sight2", "hongdian.png"), sight_screenshot_2)
                elif button_text == "点击保存截图2":
                    cv2.imwrite(os.path.join(image_dir, "muzzles", "xiaoyan.png"), muzzle_screenshot)
                    cv2.imwrite(os.path.join(image_dir, "grips", "banjie.png"), grip_screenshot)
                    cv2.imwrite(os.path.join(image_dir, "butt", "zhongxing.png"), butt_screenshot)
                    cv2.imwrite(os.path.join(image_dir, "sight", "quanxi.png"), sight_screenshot)

                    cv2.imwrite(os.path.join(image_dir, "muzzles2", "xiaoyan.png"), muzzle_screenshot_2)
                    cv2.imwrite(os.path.join(image_dir, "grips2", "banjie.png"), grip_screenshot_2)
                    cv2.imwrite(os.path.join(image_dir, "butt2", "zhongxing.png"), butt_screenshot_2)
                    cv2.imwrite(os.path.join(image_dir, "sight2", "quanxi.png"), sight_screenshot_2)
                elif button_text == "点击保存截图3":
                    cv2.imwrite(os.path.join(image_dir, "muzzles", "zhitui.png"), muzzle_screenshot)
                    cv2.imwrite(os.path.join(image_dir, "grips", "muzhi.png"), grip_screenshot)
                    # 无枪托，不保存
                    cv2.imwrite(os.path.join(image_dir, "sight", "two.png"), sight_screenshot)

                    cv2.imwrite(os.path.join(image_dir, "muzzles2", "zhitui.png"), muzzle_screenshot_2)
                    cv2.imwrite(os.path.join(image_dir, "grips2", "muzhi.png"), grip_screenshot_2)
                    # 无枪托，不保存
                    cv2.imwrite(os.path.join(image_dir, "sight2", "two.png"), sight_screenshot_2)
                elif button_text == "点击保存截图4":
                    # 无枪口，不保存
                    cv2.imwrite(os.path.join(image_dir, "grips", "qingxing.png"), grip_screenshot)
                    # 无枪托，不保存
                    cv2.imwrite(os.path.join(image_dir, "sight", "three.png"), sight_screenshot)
                    # 无枪口，不保存
                    cv2.imwrite(os.path.join(image_dir, "grips2", "qingxing.png"), grip_screenshot_2)
                    # 无枪托，不保存
                    cv2.imwrite(os.path.join(image_dir, "sight2", "three.png"), sight_screenshot_2)
                elif button_text == "点击保存截图5":
                    # 无枪口，不保存
                    # 无握把，不保存
                    # 无枪托，不保存
                    cv2.imwrite(os.path.join(image_dir, "sight", "four.png"), sight_screenshot)
                    # 无枪口，不保存
                    # 无握把，不保存
                    # 无枪托，不保存
                    cv2.imwrite(os.path.join(image_dir, "sight2", "four.png"), sight_screenshot_2)
                button.config(bg="green")
                messagebox.showinfo("成功",  "保存成功")
            else:
                messagebox.showerror("Error",  "请先加载配置")

        def create_screenshot_row_template(parent_frame, instruction_text, button_text):
            row_frame = tk.Frame(parent_frame)  # 为每一行创建一个框架
            row_frame.pack(fill=tk.X, padx=5, pady=5)  # 水平填充，设置间距

            instruction_label = tk.Label(row_frame, text=instruction_text, wraplength=500, justify=tk.LEFT)
            instruction_label.pack(side=tk.LEFT, padx=5)

            screenshot_button = tk.Button(row_frame, text=button_text, bg="white",
                                          command=lambda: take_screenshot(screenshot_button, button_text))
            screenshot_button.pack(side=tk.LEFT, padx=5)

        # 示例：使用模板创建截图行
        create_screenshot_row_template(buttons_frame, "一号武器：步枪补偿器 + 垂直握把 + 红点瞄准镜 + 战术枪托\n"
                                                      "二号武器：步枪补偿器 + 垂直握把 + 红点瞄准镜 + 战术枪托", "点击保存截图1")

        create_screenshot_row_template(buttons_frame, "一号武器：步枪消焰器 + 半截式握把 + 全息瞄准镜 + 重型枪托\n"
                                                      "二号武器：步枪消焰器 + 半截式握把 + 全息瞄准镜 + 重型枪托", "点击保存截图2")

        create_screenshot_row_template(buttons_frame, "一号武器：枪口制退器 + 拇指握把 + 二倍瞄准镜 + 无枪托\n"
                                                      "二号武器：枪口制退器 + 拇指握把 + 二倍瞄准镜 + 无枪托", "点击保存截图3")

        create_screenshot_row_template(buttons_frame, "一号武器：无枪口 + 轻型握把 + 三倍瞄准镜 + 无枪托\n"
                                                      "二号武器：无枪口 + 轻型握把 + 三倍瞄准镜 + 无枪托", "点击保存截图4")

        create_screenshot_row_template(buttons_frame, "一号武器：无枪口 + 无握把 + 四倍瞄准镜 + 无枪托\n"
                                                      "二号武器：无枪口 + 无握把 + 四倍瞄准镜 + 无枪托", "点击保存截图5")

    def create_other_config_tab(self):
        other_config_tab = ttk.Frame(self.notebook)
        self.notebook.add(other_config_tab, text="其他配置")

        # 创建 Canvas
        canvas = tk.Canvas(other_config_tab)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建 Scrollbar
        scrollbar = tk.Scrollbar(other_config_tab, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 将 Canvas 与 Scrollbar 关联
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)

        # 在 Canvas 中创建 Frame
        inner_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor='nw')

        # index 配置项
        index_frame = tk.LabelFrame(inner_frame, text="坐标")
        index_frame.pack(padx=10, pady=10, fill=tk.X)
        self.create_index_entries(index_frame)  # 直接创建，不判断 isLoadConfig

        # interval 配置项
        interval_frame = tk.LabelFrame(inner_frame, text="休眠")
        interval_frame.pack(padx=10, pady=10, fill=tk.X)
        self.create_interval_entries(interval_frame)  # 直接创建，不判断 isLoadConfig

        # # firearms_accessories_list 配置项
        # firearms_accessories_list_frame = tk.LabelFrame(inner_frame, text="配件区域")
        # firearms_accessories_list_frame.pack(padx=10, pady=10, fill=tk.X)
        # self.create_firearms_accessories_list_entries(firearms_accessories_list_frame)  # 直接创建，不判断 isLoadConfig

    def create_index_entries(self, parent_frame):
        # 固定参数名
        index_keys = ["bullet", "backpack", "energy_drink", "antivirus_backpack", "posture_2", "posture_3"]

        # 在 ui_vars 中创建对应的字典
        self.ui_vars["index"] = {}

        for i, key in enumerate(index_keys):
            label = tk.Label(parent_frame, text=key + ":")
            label.grid(row=i, column=0, padx=5, pady=5)

            # 如果 self.config_data["index"] 中不存在该键，则设置默认值 []
            value = self.config_data.get("index", {}).get(key, [])

            if isinstance(value, list):
                var = tk.StringVar(value=", ".join(map(str, value)))
                entry = tk.Entry(parent_frame, textvariable=var)
                entry.grid(row=i, column=1, padx=5, pady=5)
            else:
                var = tk.StringVar(value="0")  # 默认值为 0
                entry = tk.Entry(parent_frame, textvariable=var, state="readonly")
                entry.grid(row=i, column=1, padx=5, pady=5)

            self.ui_vars["index"][key] = var

    def create_interval_entries(self, parent_frame):
        # 固定参数名
        interval_keys = ["firearm_monitor_interval", "accessories_monitor_interval", "posture_monitor_interval",
                         "coefficient_monitor_interval", "config_monitor_interval"]

        # 在 ui_vars 中创建对应的字典
        self.ui_vars["interval"] = {}

        for i, key in enumerate(interval_keys):
            label = tk.Label(parent_frame, text=key + ":")
            label.grid(row=i, column=0, padx=5, pady=5)

            # 如果 self.config_data["interval"] 中不存在该键，则设置默认值 0
            value = self.config_data.get("interval", {}).get(key, 0)

            var = tk.StringVar(value=str(value))
            entry = tk.Entry(parent_frame, textvariable=var)
            entry.grid(row=i, column=1, padx=5, pady=5)

            self.ui_vars["interval"][key] = var

    def create_firearms_accessories_list_entries(self, parent_frame):
        # 在 ui_vars 中创建对应的字典
        self.ui_vars["firearms_accessories_list"] = {}

        # 这里为了简化，直接将整个字典内容显示在一个 Text 控件中，你可以根据需要设计更复杂的 UI
        label = tk.Label(parent_frame, text="firearms_accessories_list:")
        label.grid(row=0, column=0, padx=5, pady=5)

        var = tk.StringVar(value=json.dumps(self.config_data["firearms_accessories_list"], indent=2))
        text_widget = tk.Text(parent_frame, height=10, width=50)
        text_widget.insert(tk.END, var.get())
        text_widget.grid(row=0, column=1, padx=5, pady=5)

        self.ui_vars["firearms_accessories_list"]["text"] = var

if __name__ == '__main__':
    root = tk.Tk()
    app = ConfigGUI(root)
    root.mainloop()
