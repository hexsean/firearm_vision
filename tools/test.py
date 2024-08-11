import os
import cv2
import pandas as pd

def adaptive_threshold(image, block_size, C):
    """对图像进行自适应阈值处理"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, C)

def match_image(screenshot, template):
    """使用模板匹配计算最大相似度"""
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    return max_val

def analyze_results(results):
    """分析结果，打印所有参数组合的平均差异得分、yes平均相似度和no的"""
    df = pd.DataFrame(results)

    # 按 block_size 和 C 分组，计算 yes 和 no 图片的平均相似度
    grouped_df = df.groupby(['block_size', 'C']).agg(
        yes_mean=('max_similarity', lambda x: x[df['filename'].str.startswith('yes')].mean()),
        no_mean=('max_similarity', lambda x: x[df['filename'].str.startswith('no')].mean())
    ).reset_index()

    # 计算差异得分
    grouped_df['diff_score'] = grouped_df['yes_mean'] - grouped_df['no_mean']

    # 按差异得分降序排序
    grouped_df = grouped_df.sort_values('diff_score', ascending=False)

    # 打印结果
    print("Analysis Results:")
    print(grouped_df[['block_size', 'C', 'diff_score', 'yes_mean', 'no_mean']])

def process_images(image_dir, output_dir_base, block_sizes, C_values, template_path):
    """处理图像、保存结果并进行模板匹配"""
    results = []  # 存储匹配结果

    # 读取模板图像
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

    for filename in os.listdir(image_dir):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            img_path = os.path.join(image_dir, filename)
            img = cv2.imread(img_path)

            for block_size in block_sizes:
                for C in C_values:
                    output_dir = os.path.join(output_dir_base, f"blockSize_{block_size}_C_{C}")
                    os.makedirs(output_dir, exist_ok=True)

                    binary_img = adaptive_threshold(img, block_size, C)
                    output_path = os.path.join(output_dir, filename)
                    cv2.imwrite(output_path, binary_img)

                    # 模板匹配
                    max_val = match_image(binary_img, template)
                    results.append({
                        'filename': filename,
                        'block_size': block_size,
                        'C': C,
                        'max_similarity': max_val
                    })

    # 打印结果，方便阅读
    for result in results:
        print(f"File: {result['filename']}, Block Size: {result['block_size']}, C: {result['C']}, Max Similarity: {result['max_similarity']:.4f}")
    return results

if __name__ == "__main__":
    image_dir = r"E:\IDEA-wordspace\firearm_vision\image\ads"
    output_dir_base = r"E:\IDEA-wordspace\firearm_vision\image\ads\output"
    block_sizes = [3, 5, 7, 11, 15]  # 邻域大小列表
    C_values = range(-10, 11)  # 常数范围
    template_path = r"E:\IDEA-wordspace\firearm_vision\image\firearms\m762.png"  # 模板图片路径

    results = process_images(image_dir, output_dir_base, block_sizes, C_values, template_path)
    analyze_results(results)
