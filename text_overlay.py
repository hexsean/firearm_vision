import tkinter as tk
import queue


class TextOverlay:
    def __init__(self, root, geometry_x, geometry_y, text1="", text2="", text3="", text4="", text5="", text6="", text7="", text8=""):
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

        self.label3 = tk.Label(self.root, text=text3, font=("Helvetica", 12), bg="yellow", fg="black")
        if text3:
            self.label3.pack()

        self.label4 = tk.Label(self.root, text=text4, font=("Helvetica", 12), bg="yellow", fg="black")
        if text4:
            self.label4.pack()

        self.label5 = tk.Label(self.root, text=text5, font=("Helvetica", 12), bg="yellow", fg="black")
        if text5:
            self.label5.pack()

        self.label6 = tk.Label(self.root, text=text6, font=("Helvetica", 12), bg="yellow", fg="black")
        if text6:
            self.label6.pack()

        self.label7 = tk.Label(self.root, text=text7, font=("Helvetica", 12), bg="yellow", fg="black")
        if text7:
            self.label7.pack()

        self.label8 = tk.Label(self.root, text=text8, font=("Helvetica", 12), bg="yellow", fg="black")
        if text8:
            self.label8.pack()

        self.root.bind("<Control_L>", self.close_window)
        self.queue1 = queue.Queue()
        self.queue2 = queue.Queue()
        self.queue3 = queue.Queue()
        self.queue4 = queue.Queue()
        self.queue5 = queue.Queue()
        self.queue6 = queue.Queue()
        self.queue7 = queue.Queue()
        self.queue8 = queue.Queue()
        self.root.after(100, self.process_queue)

    def close_window(self, event):
        self.root.destroy()

    def update_text1(self, new_text):
        self.queue1.put(new_text)

    def update_text2(self, new_text):
        self.queue2.put(new_text)

    def update_text3(self, new_text):
        self.queue3.put(new_text)

    def update_text4(self, new_text):
        self.queue4.put(new_text)

    def update_text5(self, new_text):
        self.queue5.put(new_text)

    def update_text6(self, new_text):
        self.queue6.put(new_text)

    def update_text7(self, new_text):
        self.queue7.put(new_text)

    def update_text8(self, new_text):
        self.queue8.put(new_text)

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

        try:
            new_text3 = self.queue3.get_nowait()
            self._update_label(self.label3, new_text3)
        except queue.Empty:
            pass

        try:
            new_text4 = self.queue4.get_nowait()
            self._update_label(self.label4, new_text4)
        except queue.Empty:
            pass

        try:
            new_text5 = self.queue5.get_nowait()
            self._update_label(self.label5, new_text5)
        except queue.Empty:
            pass

        try:
            new_text6 = self.queue6.get_nowait()
            self._update_label(self.label6, new_text6)
        except queue.Empty:
            pass

        try:
            new_text7 = self.queue7.get_nowait()
            self._update_label(self.label7, new_text7)
        except queue.Empty:
            pass

        try:
            new_text8 = self.queue8.get_nowait()
            self._update_label(self.label8, new_text8)
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
