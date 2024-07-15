import threading
from pynput import keyboard

posture_lock = threading.Lock()

def write_posture_state(state):
    with open('file_paths', 'w', encoding='utf-8') as file:
        file.write(f"zishi = {state}\n")


def on_press(key):
    global posture_state
    try:
        char = key.char.lower()  # 将字符转为小写
        if char == 'c' or char == '\x03':
            with posture_lock:  # 加锁
                posture_state = 1 if posture_state != 1 else 0
                write_posture_state(posture_state)
        elif char == 'z' or char == '\x1a':
            with posture_lock:  # 加锁
                posture_state = 2 if posture_state != 2 else 0
                write_posture_state(posture_state)
        elif key == keyboard.Key.space:
            with posture_lock:  # 加锁
                posture_state = 0
                write_posture_state(posture_state)
    except AttributeError:
        if key == keyboard.Key.space:
            with posture_lock:  # 加锁
                posture_state = 0
                write_posture_state(posture_state)
