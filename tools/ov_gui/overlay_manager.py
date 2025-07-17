# overlay_manager.py

import multiprocessing
from tools.ov_gui.gui_server import start_gui_server

class GuiClient:
    """升级后的客户端，支持多源操作"""
    def __init__(self, queue):
        self.queue = queue

    def update(self, source_id: str, content: str):
        """添加或更新一个信息源的内容"""
        self.queue.put({'action': 'update', 'source_id': source_id, 'content': content})

    def remove(self, source_id: str):
        """移除一个信息源"""
        self.queue.put({'action': 'remove', 'source_id': source_id})

    def clear_all(self):
        """清空所有信息"""
        self.queue.put({'action': 'clear_all'})

    def move(self, pos: tuple):
        """移动整个窗口的位置"""
        self.queue.put({'action': 'move', 'pos': pos})

    def hide(self):
        """隐藏整个窗口"""
        self.queue.put({'action': 'hide'})

    def show(self):
        """显示整个窗口"""
        self.queue.put({'action': 'show_window'})

    def shutdown(self):
        """关闭GUI服务"""
        self.queue.put({'action': 'exit'})

# OverlayManager 类保持不变 (代码与上一版相同)
class OverlayManager:
    def __init__(self):
        self._queue = multiprocessing.Queue()
        self._process = None
        self.client = GuiClient(self._queue)
    def start(self):
        if self.is_running(): return
        self._process = multiprocessing.Process(target=start_gui_server, args=(self._queue,), daemon=True)
        self._process.start()
    def stop(self):
        if not self.is_running(): return
        self.client.shutdown()
        self._process.join(timeout=3)
        if self._process.is_alive(): self._process.terminate()
        self._process = None
    def is_running(self) -> bool:
        return self._process is not None and self._process.is_alive()
