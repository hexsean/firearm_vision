import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import json

class ConfigGUI:
    def __init__(self, master):
        self.master = master
        master.title("程序配置")

        # 创建 Notebook
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 配置文件路径
        self.config_file_path = tk.StringVar()

        # 初始化 config
        self.config = {}

        # 基本配置
        self.create_basic_config_tab()

        # 屏幕截图区域
        self.create_screenshot_area_tab()

        # 武器配置
        self.create_firearms_config_tab()

        # 其他配置
        self.create_other_config_tab()

        # 初始化 config
        self.config = {}

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

        # 加载和保存按钮
        load_button = tk.Button(basic_config_tab, text="加载配置", command=self.load_config)
        load_button.grid(row=1, column=0)
        save_button = tk.Button(basic_config_tab, text="保存配置", command=self.save_config)
        save_button.grid(row=1, column=1)

        # 实时配置开关
        self.enable_realtime_config_var = tk.BooleanVar()
        enable_realtime_config_checkbutton = tk.Checkbutton(
            basic_config_tab, text="启用实时配置", variable=self.enable_realtime_config_var
        )
        enable_realtime_config_checkbutton.grid(row=2, column=0, columnspan=2)

        # 屏幕分辨率
        screen_resolution_frame = tk.LabelFrame(basic_config_tab, text="屏幕分辨率")
        screen_resolution_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10)
        self.screen_width_var = tk.StringVar()
        self.screen_height_var = tk.StringVar()
        screen_width_label = tk.Label(screen_resolution_frame, text="宽度:")
        screen_width_label.grid(row=0, column=0)
        screen_width_entry = tk.Entry(screen_resolution_frame, textvariable=self.screen_width_var)
        screen_width_entry.grid(row=0, column=1)
        screen_height_label = tk.Label(screen_resolution_frame, text="高度:")
        screen_height_label.grid(row=1, column=0)
        screen_height_entry = tk.Entry(screen_resolution_frame, textvariable=self.screen_height_var)
        screen_height_entry.grid(row=1, column=1)

    def create_screenshot_area_tab(self):
        screenshot_area_tab = ttk.Frame(self.notebook)
        self.notebook.add(screenshot_area_tab, text="屏幕截图区域")

        screenshot_areas = [
            ("weapon_screenshot_area", "武器截图区域"),
            ("sight_screenshot_area", "瞄准镜截图区域"),
            ("muzzle_screenshot_area", "枪口截图区域"),
            ("grip_screenshot_area", "握把截图区域"),
            ("butt_screenshot_area", "枪托截图区域"),
            ("muzzle_screenshot_area2", "枪口截图区域2"),
            ("grip_screenshot_area2", "握把截图区域2"),
            ("butt_screenshot_area2", "枪托截图区域2"),
            ("sight_screenshot_area2", "瞄准镜截图区域2")
        ]

        row_num = 0
        col_num = 0
        for config_key, frame_text in screenshot_areas:
            frame = tk.LabelFrame(screenshot_area_tab, text=frame_text)
            frame.grid(row=row_num, column=col_num, padx=10, pady=10)
            self.create_screenshot_area_entries(frame, config_key)

            row_num += 1
            if row_num > 4:  # 每列最多5个
                row_num = 0
                col_num += 1

    def create_firearms_config_tab(self):
        firearms_config_tab = ttk.Frame(self.notebook)
        self.notebook.add(firearms_config_tab, text="武器配置")

        canvas = tk.Canvas(firearms_config_tab)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(firearms_config_tab, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        firearms_inner_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=firearms_inner_frame, anchor='nw')

        # 遍历 firearms 配置项
        row_num = 0
        for firearm_name, firearm_data in self.config.get("firearms", {}).items():
            firearm_subframe = tk.LabelFrame(firearms_inner_frame, text=firearm_name)
            firearm_subframe.grid(row=row_num, column=0, padx=10, pady=5)

            # 识别阈值
            recognition_threshold_label = tk.Label(firearm_subframe, text="识别阈值:")
            recognition_threshold_label.grid(row=0, column=0)
            recognition_threshold_var = tk.StringVar(value=firearm_data["recognition_confidence_threshold"])
            firearm_data["recognition_threshold_var"] = recognition_threshold_var
            recognition_threshold_entry = tk.Entry(firearm_subframe, textvariable=recognition_threshold_var)
            recognition_threshold_entry.grid(row=0, column=1)

            # 系数列表
            coefficient_list_frame = tk.Frame(firearm_subframe)
            coefficient_list_frame.grid(row=1, column=0, columnspan=2)
            coefficient_list_vars = []
            for i in range(4):
                coef_label = tk.Label(coefficient_list_frame, text=f"系数{i+1}:")
                coef_label.pack(side=tk.LEFT)
                coef_var = tk.StringVar(value=firearm_data["coefficient_list"][i])
                coefficient_list_vars.append(coef_var)
                coef_entry = tk.Entry(coefficient_list_frame, textvariable=coef_var, width=5)
                coef_entry.pack(side=tk.LEFT)
            firearm_data["coefficient_list_vars"] = coefficient_list_vars

            row_num += 1

    def create_other_config_tab(self):
        other_config_tab = ttk.Frame(self.notebook)
        self.notebook.add(other_config_tab, text="其他配置")

        # 遍历其他配置项,
        row_num = 0
        for config_key, config_value in list(self.config.items()): # 复制 keys
            if config_key not in ["lua_config_path", "firearms", "screen_resolution", "overlay_position",
                                  "weapon_screenshot_area", "muzzle_screenshot_area", "grip_screenshot_area",
                                  "butt_screenshot_area", "sight_screenshot_area", "muzzle_screenshot_area2",
                                  "grip_screenshot_area2", "butt_screenshot_area2", "sight_screenshot_area2",
                                  "enable_realtime_configuration", "is_open_overlay", "is_open_screenshot_of_keystrokes",
                                  "vertical_sensitivity_magnification"]:

                config_label = tk.Label(other_config_tab, text=config_key + ":")
                config_label.grid(row=row_num, column=0)

                if isinstance(config_value, bool):
                    config_var = tk.BooleanVar(value=config_value)
                    config_entry = tk.Checkbutton(other_config_tab, variable=config_var)
                elif isinstance(config_value, (int, float)):
                    config_var = tk.StringVar(value=config_value)
                    config_entry = tk.Entry(other_config_tab, textvariable=config_var)
                elif isinstance(config_value, list):
                    config_var = tk.StringVar(value=", ".join(map(str, config_value)))
                    config_entry = tk.Entry(other_config_tab, textvariable=config_var)
                elif isinstance(config_value, dict):
                    config_var = tk.StringVar(value=json.dumps(config_value, indent=2))  # 格式化字典输出
                    config_entry = tk.Text(other_config_tab, height=5, width=50)
                    config_entry.insert(tk.END, config_var.get())
                else:
                    config_var = tk.StringVar(value=str(config_value))
                    config_entry = tk.Entry(other_config_tab, textvariable=config_var, state="readonly")

                config_entry.grid(row=row_num, column=1)
                self.config[config_key + "_var"] = config_var  # 保存变量引用
                row_num += 1


    def create_screenshot_area_entries(self, parent_frame, config_key):
        area_data = self.config.get(config_key, {})
        for key in ["left", "top", "width", "height"]:
            label = tk.Label(parent_frame, text=key + ":")
            label.grid(row=0, column=0)
            var = tk.StringVar(value=area_data.get(key, 0))
            entry = tk.Entry(parent_frame, textvariable=var)
            entry.grid(row=0, column=1)
            self.config[config_key + "_" + key + "_var"] = var

    def browse_config_file(self):
        filepath = filedialog.askopenfilename(
            initialdir = "/",
            title = "Select a File",
            filetypes = (("Json files", "*.json"), ("all files", "*.*"))
        )
        if filepath:
            self.config_file_path.set(filepath)
            self.load_config()

    def load_config(self):
        try:
            with open(self.config_file_path.get(), 'r') as f:
                self.config = json.load(f)
            self.update_ui_from_config()
        except FileNotFoundError:
            messagebox.showerror("Error", "配置文件未找到")
        except json.JSONDecodeError:
            messagebox.showerror("Error", "配置文件格式错误")

    def save_config(self):
        if not self.validate_config():
            messagebox.showerror("Error", "配置数据有误，请检查")
            return

        self.update_config_from_ui()
        try:
            with open(self.config_file_path.get(), 'w') as f:
                json.dump(self.config, f, indent=4)
            messagebox.showinfo("Success", "配置保存成功")
        except Exception as e:
            messagebox.showerror("Error", f"保存配置文件出错: {e}")

    def validate_config(self):
        # 验证配置数据的逻辑
        # ... (根据你的需求添加验证逻辑)
        return True  # 这里暂时返回 True，表示验证通过

    def update_config_from_ui(self):
        # 基本配置
        self.config["enable_realtime_configuration"] = self.enable_realtime_config_var.get()
        try:
            self.config["screen_resolution"] = [int(self.screen_width_var.get()), int(self.screen_height_var.get())]
        except ValueError:
            print("Error: Invalid screen resolution")

        # 屏幕截图区域
        for config_key in ["weapon_screenshot_area", "sight_screenshot_area",
                           "muzzle_screenshot_area", "grip_screenshot_area",
                           "butt_screenshot_area", "muzzle_screenshot_area2",
                           "grip_screenshot_area2", "butt_screenshot_area2",
                           "sight_screenshot_area2"]:
            for key in ["left", "top", "width", "height"]:
                var_name = config_key + "_" + key + "_var"
                try:
                    self.config[config_key][key] = int(self.config[var_name].get())
                except ValueError:
                    print(f"Error: Invalid value for {config_key}.{key}")

        # 武器配置
        for firearm_name, firearm_data in self.config["firearms"].items():
            recognition_threshold_var = firearm_data.get("recognition_threshold_var")
            if recognition_threshold_var:
                try:
                    firearm_data["recognition_confidence_threshold"] = float(recognition_threshold_var.get())
                except ValueError:
                    print(f"Error: Invalid recognition threshold for {firearm_name}")

            coefficient_list_vars = firearm_data.get("coefficient_list_vars")
            if coefficient_list_vars:
                try:
                    firearm_data["coefficient_list"] = [float(var.get()) for var in coefficient_list_vars]
                except ValueError:
                    print(f"Error: Invalid coefficient list for {firearm_name}")

        # 其他配置项
        for config_key, config_value in self.config.items():
            if config_key.endswith("_var"):
                original_key = config_key[:-4]
                if isinstance(self.config[original_key], bool):
                    self.config[original_key] = self.config[config_key].get()
                elif isinstance(self.config[original_key], (int, float)):
                    try:
                        self.config[original_key] = float(self.config[config_key].get())
                    except ValueError:
                        print(f"Error: Invalid value for {original_key}")
                elif isinstance(self.config[original_key], list):
                    try:
                        self.config[original_key] = [int(x) for x in self.config[config_key].get().split(",")]
                    except ValueError:
                        print(f"Error: Invalid value for {original_key}")
                elif isinstance(self.config[original_key], dict):
                    try:
                        self.config[original_key] = json.loads(self.config[config_key].get())
                    except json.JSONDecodeError:
                        print(f"Error: Invalid JSON format for {original_key}")

    def update_ui_from_config(self):
        # 基本配置
        if "enable_realtime_configuration" in self.config:
            self.enable_realtime_config_var.set(self.config["enable_realtime_configuration"])
        if "screen_resolution" in self.config:
            self.screen_width_var.set(self.config["screen_resolution"][0])
            self.screen_height_var.set(self.config["screen_resolution"][1])

        # 屏幕截图区域
        for config_key in ["weapon_screenshot_area", "sight_screenshot_area",
                           "muzzle_screenshot_area", "grip_screenshot_area",
                           "butt_screenshot_area", "muzzle_screenshot_area2",
                           "grip_screenshot_area2", "butt_screenshot_area2",
                           "sight_screenshot_area2"]:
            for key in ["left", "top", "width", "height"]:
                var_name = config_key + "_" + key + "_var"
                if var_name in self.config:
                    self.config[var_name].set(self.config[config_key][key])

        # 武器配置
        for firearm_name, firearm_data in self.config.get("firearms", {}).items():
            recognition_threshold_var = firearm_data.get("recognition_threshold_var")
            if recognition_threshold_var:
                recognition_threshold_var.set(firearm_data["recognition_confidence_threshold"])

            coefficient_list_vars = firearm_data.get("coefficient_list_vars")
            if coefficient_list_vars:
                for i, coef_var in enumerate(coefficient_list_vars):
                    coef_var.set(firearm_data["coefficient_list"][i])

        # 其他配置项
        for config_key, config_value in self.config.items():
            if config_key.endswith("_var"):
                original_key = config_key[:-4]
                if isinstance(self.config[original_key], dict):
                    self.config[config_key].set(json.dumps(self.config[original_key], indent=2))
                else:
                    self.config[config_key].set(self.config[original_key])


if __name__ == '__main__':
    root = tk.Tk()
    app = ConfigGUI(root)
    root.mainloop()

