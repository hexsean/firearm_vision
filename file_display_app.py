import tkinter as tk
import threading
import time
import json
from text_overlay import TextOverlay


# 加载配置
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)


config = load_config()
file_paths = config["lua_config_path"]


def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return str(e)


def update_content(interval, overlay):
    while True:
        overlay.update_text1(read_file(file_paths))
        time.sleep(interval)


def main():
    overlay = TextOverlay(tk.Tk(), '0', '0')
    monitor_thread = threading.Thread(target=update_content, args=(0.2, overlay))
    monitor_thread.start()
    overlay.root.mainloop()


if __name__ == "__main__":
    main()
