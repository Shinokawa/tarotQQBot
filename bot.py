import asyncio
import websockets
import json
import random
from datetime import datetime
import os
import logging
from tarot import load_tarot_data, draw_random_tarot, format_tarot_message

# 设置日志记录器
logging.basicConfig(
    filename="qq_message_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# 读取塔罗牌数据
tarot_file = "TarotData.yml"
image_base_path = "TarotImages"  # 这里是存放塔罗牌图片的文件夹
tarot_data = load_tarot_data(tarot_file)

# 运势列表
fortunes = ["大吉", "吉", "中吉", "小吉", "末吉", "凶", "大凶"]

# 存储用户当天的运势的文件路径
fortune_file = "user_fortunes.json"

# 从文件加载用户运势数据
def load_fortunes():
    if os.path.exists(fortune_file):
        with open(fortune_file, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

# 将用户运势数据保存到文件
def save_fortunes():
    with open(fortune_file, 'w', encoding='utf-8') as file:
        json.dump(user_fortunes, file, ensure_ascii=False, indent=4)

# 初始化：从文件中加载用户运势
user_fortunes = load_fortunes()

# 随机生成运势
def get_fortune():
    return random.choice(fortunes)

# 获取图片路径并转换为符合 CQ 码的格式
def get_image_cq_code(image_path):
    # 将路径中的反斜杠转换为正斜杠，并确保前缀 file:// 正确拼接
    normalized_path = image_path.replace("\\", "/")
    return f"[CQ:image,file=file:///{normalized_path}]"


# 获取当前日期
def get_today():
    return datetime.now().strftime("%Y-%m-%d")

# 记录每条接收到的 QQ 消息
def log_message(message):
    if 'sender' in message and 'message' in message:
        user_id = message['sender']['user_id']
        group_id = message.get('group_id', '未知群号')
        msg_content = message['message']
        logging.info(f"QQ号: {user_id} 群号: {group_id} 消息: {msg_content}")

# 处理接收到的消息
async def handle_message(websocket, message):
    # 记录消息日志
    log_message(message)

    # 判断消息是否以 "/运势" 开头
    if 'message' in message and message['message'].startswith("/运势"):
        sender = message['sender']
        user_id = str(sender['user_id'])
        sender_name = sender.get('nickname', f"用户{user_id}")

        today = get_today()

        if user_id in user_fortunes:
            user_fortune, date = user_fortunes[user_id]
            if date == today:
                response_message = f"{sender_name} 今日的运势是: {user_fortune}"
            else:
                new_fortune = get_fortune()
                user_fortunes[user_id] = (new_fortune, today)
                response_message = f"{sender_name} 今日的运势是: {new_fortune}"
                save_fortunes()
        else:
            new_fortune = get_fortune()
            user_fortunes[user_id] = (new_fortune, today)
            response_message = f"{sender_name} 今日的运势是: {new_fortune}"
            save_fortunes()

        response = {
            "action": "send_group_msg",
            "params": {
                "group_id": message['group_id'],
                "message": response_message
            }
        }

        await websocket.send(json.dumps(response))
        print(f"已发送运势给: {sender_name}, 运势为: {user_fortunes[user_id][0]}")

    # 判断消息是否以 "/tarot" 开头
    elif 'message' in message and message['message'].startswith("/tarot"):
        sender = message['sender']
        group_id = message['group_id']
        sender_name = sender.get('nickname', '未知用户')

        # 抽取塔罗牌
        tarot_card = draw_random_tarot(tarot_data)
        response_message, image_path = format_tarot_message(tarot_card, image_base_path)
        print(image_path)
        absolute_image_path = os.path.abspath(image_path).replace("\\", "/")
        print(f"绝对图片路径: {absolute_image_path}")
        print(f"图片是否存在: {os.path.exists(image_path)}")

        if image_path and os.path.exists(image_path):
            # 准备包含图片和文字的消息
            response_message_with_image = f"{response_message}[CQ:image,file=file:///{absolute_image_path}]"
        else:
            response_message_with_image = response_message

        # 调试打印：输出要发送的消息
        print(f"发送消息内容: {response_message_with_image}")

        # 准备并发送回复
        response = {
            "action": "send_group_msg",
            "params": {
                "group_id": group_id,
                "message": response_message_with_image
            }
        }
        print(f"发送的 response 对象: {json.dumps(response, ensure_ascii=False, indent=4)}")

        try:
            await websocket.send(json.dumps(response))
            print(f"已发送塔罗牌和图片给: {sender_name}")
        except Exception as e:
            print(f"发送消息时出错: {e}")

# WebSocket 服务器，等待反向连接
async def websocket_server(websocket, path):
    print("WebSocket 连接已建立")
    try:
        async for message in websocket:
            data = json.loads(message)

            # 处理 OneBot 的消息事件
            if 'post_type' in data and data['post_type'] == 'message':
                await handle_message(websocket, data)
    except websockets.ConnectionClosed:
        print("连接关闭")

# 启动 WebSocket 服务器
async def main():
    # 启动 WebSocket 服务器并监听 8081 端口
    async with websockets.serve(websocket_server, "127.0.0.1", 8081):
        print("等待反向 WebSocket 连接...")
        await asyncio.Future()

# 启动 WebSocket 服务器
asyncio.run(main())
