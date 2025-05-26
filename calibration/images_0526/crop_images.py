import os
from PIL import Image


def process_images(input_dir, output_dir):
    """处理输入目录中的所有图片，保留左半部分并保存到输出目录"""
    os.makedirs(output_dir, exist_ok=True)

    valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(valid_extensions):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)

            try:
                with Image.open(input_path) as img:
                    width, height = img.size

                    # 计算左半部分坐标 (left, upper, right, lower)
                    left_area = (0, 0, width//2, height)
                    left_half = img.crop(left_area)

                    if img.mode in ('RGBA', 'LA'):
                        left_half.save(output_path, format=img.format)
                    else:
                        left_half.convert('RGB').save(output_path)

                    print(f"成功处理: {filename}")

            except Exception as e:
                print(f"处理失败 {filename}: {str(e)}")


process_images("./original_images", "./processed_images")
