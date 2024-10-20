import yaml
import random
import os


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


# 格式化塔罗牌信息并返回消息和图片路径（随机选择正位或逆位）
def format_tarot_message(tarot_card, image_base_path):
    if tarot_card:
        name = tarot_card.get('name', '未知')
        positive = tarot_card.get('positive', '无')
        negative = tarot_card.get('negative', '无')
        image_name = tarot_card.get('imageName', '')

        # 随机选择正位或逆位
        is_upright = random.choice([True, False])

        if is_upright:
            position = "正位"
            interpretation = positive
        else:
            position = "逆位"
            interpretation = negative

        # 准备返回的消息和图片路径
        message = (
            f"你抽到的塔罗牌是: {name} ({position})\n"
            f"解读: {interpretation}\n"
        )

        image_path = os.path.join(image_base_path, image_name).replace("\\", "/")
        return message, image_path

    return "未能抽取到塔罗牌。", None
