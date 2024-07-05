import tkinter as tk
import queue


class TextOverlay:
    def __init__(self, root, geometry_x, geometry_y, text1="", text2=""):
        self.root = root
        self.root.overrideredirect(True)  # 去掉窗口的边框
        self.root.geometry(f"+{geometry_x}+{geometry_y}")  # 窗口位置在左上角

        # 设置窗口透明度（Windows）
        self.root.attributes("-alpha", 0.8)

        # 创建标签并显示文字
        self.label1 = tk.Label(self.root, text=text1, font=("Helvetica", 12), bg="yellow", fg="black")
        self.label1.pack()

        self.label2 = tk.Label(self.root, text=text2, font=("Helvetica", 12), bg="yellow", fg="black")
        self.label2.pack()

        # 窗口置顶
        self.root.attributes("-topmost", True)

        # 绑定按键事件，按下左Ctrl键关闭窗口
        self.root.bind("<Control_L>", self.close_window)

        # 创建队列用于线程间通信
        self.queue1 = queue.Queue()
        self.queue2 = queue.Queue()

        # 启动消息处理线程
        self.root.after(100, self.process_queue)

    def close_window(self, event):
        self.root.destroy()

    def update_text1(self, new_text):
        # 将更新请求放入队列
        self.queue1.put(new_text)

    def update_text2(self, new_text):
        # 将更新请求放入队列
        self.queue2.put(new_text)

    def process_queue(self):
        try:
            while True:
                # 尝试从队列中获取消息
                new_text1 = self.queue1.get_nowait()
                self.label1.config(text=new_text1)
        except queue.Empty:
            pass
        try:
            while True:
                # 尝试从队列中获取消息
                new_text2 = self.queue2.get_nowait()
                self.label2.config(text=new_text2)
        except queue.Empty:
            pass
        # 再次调用自身
        self.root.after(100, self.process_queue)
