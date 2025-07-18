# gui_server.py

import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import QThread, pyqtSignal, QObject, Qt

# CommandListener 保持不变 (代码与上一版相同)
class CommandListener(QObject):
    command_received = pyqtSignal(dict)
    def __init__(self, queue):
        super().__init__()
        self.queue = queue
    def run(self):
        while True:
            command = self.queue.get()
            self.command_received.emit(command)
            if command.get('action') == 'exit':
                break

# 升级后的仪表盘窗口
class DashboardWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 使用垂直布局来管理所有信息标签
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0) # 布局无边距
        self.layout.setSpacing(5) # 标签之间的间距

        # 使用字典来存储每个信息源对应的QLabel
        # 格式: { 'source_id': QLabel_widget }
        self.source_labels = {}

        self.show() # 初始时就显示，即使是空的

    def process_command(self, command: dict):
        action = command.get('action')
        source_id = command.get('source_id')

        if action == 'update':
            if not source_id: return
            content = command.get('content', '')

            # 如果是新的信息源，则创建一个新的QLabel
            if source_id not in self.source_labels:
                new_label = QLabel(content, self)
                new_label.setStyleSheet("""
                    background-color: rgba(0, 0, 0, 160); 
                    color: #00FF7F; /* 春绿色 */
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 16px; 
                    font-weight: bold;
                    padding: 5px 10px; 
                    border-radius: 4px;
                """)
                self.layout.addWidget(new_label)
                self.source_labels[source_id] = new_label
            # 如果是已有的信息源，则只更新文本
            else:
                self.source_labels[source_id].setText(content)

            self.adjustSize() # 每次更新后都调整窗口大小以适应内容

        elif action == 'remove':
            if source_id and source_id in self.source_labels:
                label_to_remove = self.source_labels.pop(source_id)
                self.layout.removeWidget(label_to_remove)
                label_to_remove.deleteLater() # 安全地删除控件
                self.adjustSize()

        elif action == 'clear_all':
            for label in self.source_labels.values():
                self.layout.removeWidget(label)
                label.deleteLater()
            self.source_labels.clear()
            self.adjustSize()

        elif action == 'move':
            if 'pos' in command:
                self.move(command['pos'][0], command['pos'][1])

        elif action == 'hide':
            self.hide()

        elif action == 'show_window': # 和之前的show区分开
            self.show()

        elif action == 'exit':
            QApplication.instance().quit()

# 启动服务的函数 start_gui_server 已更新以使用新窗口名
def start_gui_server(queue):
    app = QApplication(sys.argv)
    window = DashboardWindow() # 使用新的窗口类
    # ... 后续的线程和信号连接逻辑保持不变
    listener_thread = QThread()
    command_listener = CommandListener(queue)
    command_listener.moveToThread(listener_thread)
    listener_thread.started.connect(command_listener.run)
    command_listener.command_received.connect(window.process_command)
    command_listener.command_received.connect(lambda cmd: listener_thread.quit() if cmd.get('action') == 'exit' else None)
    listener_thread.finished.connect(app.quit)
    listener_thread.start()
    print("> GUI Server Process Started...")
    sys.exit(app.exec())
