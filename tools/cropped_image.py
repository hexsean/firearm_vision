from PIL import Image
import os

# 用于裁剪配件, 只取中间部分匹配
if __name__ == '__main__':
    # 指定原始图片的目录
    src_directory = r"E:\idea_workspace\vision\image\copy\muzzles"
    # 创建一个新目录来保存裁剪后的图片
    dst_directory = os.path.join(src_directory, "cropped")

    # 如果目标目录不存在，则创建它
    if not os.path.exists(dst_directory):
        os.makedirs(dst_directory)

    # 遍历源目录中的所有png图片
    for filename in os.listdir(src_directory):
        if filename.endswith(".png"):
            # 拼接完整的文件路径
            file_path = os.path.join(src_directory, filename)
            # 打开图片
            image = Image.open(file_path)
            # 计算裁剪区域
            left = (66 - 22) // 2
            top = left
            right = left + 22
            bottom = top + 22
            # 裁剪图片
            cropped_image = image.crop((left, top, right, bottom))
            # 保存裁剪后的图片到目标目录
            cropped_image.save(os.path.join(dst_directory, filename))

    print("图片裁剪完成，保存在:", dst_directory)
