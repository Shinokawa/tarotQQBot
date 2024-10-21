import yaml
from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
import random


# 读取塔罗牌数据
def load_tarot_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    else:
        print(f"{file_path} 文件未找到。")
        return None


# 从塔罗牌列表中随机抽取一张塔罗牌
def draw_random_tarot(tarot_data):
    if tarot_data and 'tarot' in tarot_data:
        return random.choice(tarot_data['tarot'])
    return None


# 旋转逆位塔罗牌图片（根据 is_reversed 参数决定是否旋转）
def rotate_image_if_reversed(image, is_reversed):
    if is_reversed:
        print(is_reversed)
        return image.rotate(180)
    return image


# 创建包含塔罗牌图片和解读的大图片 (上下结构)
def create_combined_image(tarot_card, interpretation, image_path, output_path, is_reversed):
    try:
        # 加载塔罗牌图片
        with Image.open(image_path) as card_img:
            # 打印调试信息：检查牌位
            print(f"选择的牌位: {'逆位' if is_reversed else '正位'}")

            # 如果是逆位，旋转图片180度
            card_img = rotate_image_if_reversed(card_img, is_reversed)

            card_width, card_height = card_img.size

            # 设置字体和大小 (需要路径到合适的字体文件，可以选择系统字体路径)
            font_path = "C:/Windows/Fonts/simhei.ttf"  # Windows 系统中的黑体字体
            font = ImageFont.truetype(font_path, 24)

            # 自动换行处理
            wrapped_text = textwrap.fill(interpretation, width=30)

            # 创建文本绘制工具
            draw = ImageDraw.Draw(card_img)

            # 计算文本的边界框尺寸
            text_bbox = draw.textbbox((0, 0), wrapped_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            # 创建新的图片，高度为塔罗牌高度 + 文本高度，宽度取最大值
            new_width = max(card_width, text_width + 40)  # 40 是文字区域左右留白
            new_height = card_height + text_height + 60  # 60 是上下留白

            # 创建空白画布（白色背景）
            new_img = Image.new("RGB", (new_width, new_height), (255, 255, 255))

            # 在上部绘制塔罗牌图片
            card_position = ((new_width - card_width) // 2, 0)  # 上部居中绘制图片
            new_img.paste(card_img, card_position)

            # 在下部绘制文本
            draw = ImageDraw.Draw(new_img)
            text_position = ((new_width - text_width) // 2, card_height + 30)  # 居中绘制文本
            draw.text(text_position, wrapped_text, font=font, fill=(0, 0, 0))

            # 保存合成后的图片
            new_img.save(output_path)

            return output_path
    except Exception as e:
        print(f"生成合成图片时出错: {e}")
        return None


# 格式化塔罗牌信息并生成合成图片
def format_tarot_message_with_image(tarot_card, image_base_path, output_base_path):
    if tarot_card:
        name = tarot_card.get('name', '未知')
        positive = tarot_card.get('positive', '无')
        negative = tarot_card.get('negative', '无')
        image_name = tarot_card.get('imageName', '')

        # 随机选择正位或逆位
        is_upright = random.choice([True, False])

        # 打印调试信息：输出是否正位
        print(f"塔罗牌 '{name}' 被抽取为 {'正位' if is_upright else '逆位'}")

        if is_upright:
            position = "正位"
            interpretation = positive
            image_path = os.path.join(image_base_path, image_name).replace("\\", "/")  # 正位不旋转
        else:
            position = "逆位"
            interpretation = negative
            image_path = os.path.join(image_base_path, image_name).replace("\\", "/")

        # 准备解读消息
        interpretation_message = f"         {name} ({position})\n\n解读:\n{interpretation}"

        # 生成合成图片
        output_image_path = os.path.join(output_base_path, f"{name}_combined.jpg").replace("\\", "/")
        combined_image_path = create_combined_image(tarot_card, interpretation_message, image_path, output_image_path, is_reversed=not is_upright)

        # 转换为绝对路径（适用于 Windows 环境）
        absolute_combined_image_path = os.path.abspath(combined_image_path)

        return absolute_combined_image_path

    return None
