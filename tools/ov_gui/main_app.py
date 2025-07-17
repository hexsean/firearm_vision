# main.py

import time
import threading
import random
from overlay_manager import OverlayManager, GuiClient


# 工作线程函数
def data_producer(client: GuiClient, source_id: str, interval: float):
    """
    一个模拟数据生产者的线程函数。
    它会周期性地更新它在仪表盘上对应的区域。
    """
    print(f"Thread '{source_id}' started.")
    for i in range(20):
        # 模拟计算或获取数据
        value = random.randint(0, 100)
        status = "OK" if value > 20 else "CRITICAL"
        content = f"{source_id}: {value:3d} | Status: {status}"

        # 发送更新命令
        client.update(source_id, content)

        time.sleep(interval)

    # 任务完成后，可以选择移除自己的显示
    print(f"Thread '{source_id}' finished. Removing from dashboard.")
    client.remove(source_id)


if __name__ == '__main__':
    manager = OverlayManager()
    try:
        # 启动服务
        manager.start()
        time.sleep(1) # 等待服务进程初始化

        # 将仪表盘移动到屏幕右侧中间
        manager.client.move(pos=(1920 - 450, 400))

        # 创建并启动两个工作线程
        # 它们会并发地向仪表盘发送数据
        thread1 = threading.Thread(
            target=data_producer,
            args=(manager.client, "CPU Usage ", 0.1)
        )
        thread2 = threading.Thread(
            target=data_producer,
            args=(manager.client, "GPU Temp  ", 0.2)
        )
        thread3 = threading.Thread(
            target=data_producer,
            args=(manager.client, "AAAA\nBBBB", 0.2)
        )

        thread1.start()
        thread2.start()
        thread3.start()

        # 主线程可以做其他事情，或者等待子线程结束
        thread1.join()
        thread2.join()
        thread3.join()

        print("All data producers have finished.")
        time.sleep(2)

    finally:
        # 确保在程序退出时关闭服务
        if manager.is_running():
            print("Shutting down overlay service.")
            manager.stop()
        print("Program finished.")
