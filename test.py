import time

file_paths = ["C:/Users/Public/Downloads/pubg.lua", "C:/Users/Public/Downloads/pubgd.lua"]

# 初始化一个字典来存储文件的上一次内容
file_contents = {file_path: None for file_path in file_paths}


def read_file_content(file_path):
    """读取文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except Exception as e:
        print(f"An error occurred while reading {file_path}: {e}")
    return None


if __name__ == "__main__":
    while True:
        for file_path in file_paths:
            new_content = read_file_content(file_path)
            if new_content is not None and new_content != file_contents[file_path]:
                file_contents[file_path] = new_content
                print(new_content)
        time.sleep(0.1)
