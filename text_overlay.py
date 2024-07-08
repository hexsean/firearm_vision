import tkinter as tk
import queue


class TextOverlay:
    def __init__(self, root, geometry_x, geometry_y, text1="", text2=""):
        self.root = root
        self.root.overrideredirect(True)
        self.root.geometry(f"+{geometry_x}+{geometry_y}")
        self.root.attributes("-alpha", 0.6)
        self.root.config(bg="blue")
        self.root.attributes("-transparentcolor", "blue")
        self.root.attributes("-topmost", True)

        self.label1 = tk.Label(self.root, text=text1, font=("Helvetica", 12), bg="yellow", fg="black")
        if text1:
            self.label1.pack()
        self.label2 = tk.Label(self.root, text=text2, font=("Helvetica", 12), bg="yellow", fg="black")
        if text2:
            self.label2.pack()

        self.root.bind("<Control_L>", self.close_window)
        self.queue1 = queue.Queue()
        self.queue2 = queue.Queue()
        self.root.after(100, self.process_queue)

    def close_window(self, event):
        self.root.destroy()

    def update_text1(self, new_text):
        self.queue1.put(new_text)

    def update_text2(self, new_text):
        self.queue2.put(new_text)

    def process_queue(self):
        try:
            new_text1 = self.queue1.get_nowait()
            self._update_label(self.label1, new_text1)
        except queue.Empty:
            pass

        try:
            new_text2 = self.queue2.get_nowait()
            self._update_label(self.label2, new_text2)
        except queue.Empty:
            pass

        self.root.after(100, self.process_queue)

    def _update_label(self, label, new_text):
        if new_text:  # 检查是否有内容
            label.config(text=new_text)
            if not label.winfo_ismapped():
                label.pack()
        else:  # 如果没有内容或内容为空，则隐藏标签
            if label.winfo_ismapped():
                label.pack_forget()
