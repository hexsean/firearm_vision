import tkinter as tk
import threading
import time

file_paths = ["C:/Users/Public/Downloads/pubg.lua", "C:/Users/Public/Downloads/pubgd.lua"]


class FileDisplayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("实时文件显示")
        self.root.geometry("+0+0")  # 窗口位置在左上角

        # 设置窗口透明度和置顶
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-alpha", 0.8)
        self.root.attributes("-topmost", True)

        self.label1 = tk.Label(root, text="", font=("Helvetica", 12), bg="yellow", fg="black", anchor="w", justify="left")
        self.label1.pack(fill=tk.BOTH, expand=True)

        self.label2 = tk.Label(root, text="", font=("Helvetica", 12), bg="yellow", fg="black", anchor="w", justify="left")
        self.label2.pack(fill=tk.BOTH, expand=True)

        self.update_interval = 50  # 更新间隔，毫秒
        self.update_content()  # 初次调用更新内容

    def read_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            return str(e)

    def update_content(self):
        content1 = self.read_file(file_paths[0])
        content2 = self.read_file(file_paths[1])

        self.label1.config(text=content1)
        self.label2.config(text=content2)

        # 安排下次更新
        self.root.after(self.update_interval, self.update_content)

def main():
    root = tk.Tk()
    app = FileDisplayApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
