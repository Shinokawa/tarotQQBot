import asyncio
import websockets
import json
import random
from datetime import datetime
import os
import logging

# 设置日志记录器
logging.basicConfig(
    filename="qq_message_log.txt",  # 日志文件名
    level=logging.INFO,  # 日志等级
    format="%(asctime)s - %(message)s",  # 日志格式
    datefmt="%Y-%m-%d %H:%M:%S"  # 时间格式
)

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
        # 获取发送消息的人的信息
        sender = message['sender']
        user_id = str(sender['user_id'])  # 将 user_id 转为字符串以便作为字典的键
        sender_name = sender.get('nickname', f"用户{user_id}")

        # 获取今天的日期
        today = get_today()

        # 检查该用户是否已经生成过运势
        if user_id in user_fortunes:
            user_fortune, date = user_fortunes[user_id]
            # 如果是今天的运势，直接返回之前的结果
            if date == today:
                response_message = f"{sender_name} 今日的运势是: {user_fortune}"
            else:
                # 如果是旧日期，重新生成运势并更新
                new_fortune = get_fortune()
                user_fortunes[user_id] = (new_fortune, today)
                response_message = f"{sender_name} 今日的运势是: {new_fortune}"
                save_fortunes()  # 保存更新后的运势
        else:
            # 如果没有生成过运势，生成新的并存储
            new_fortune = get_fortune()
            user_fortunes[user_id] = (new_fortune, today)
            response_message = f"{sender_name} 今日的运势是: {new_fortune}"
            save_fortunes()  # 保存新生成的运势

        # 准备回复内容
        response = {
            "action": "send_group_msg",  # 发送群消息
            "params": {
                "group_id": message['group_id'],  # 群号
                "message": response_message
            }
        }

        # 发送回复
        await websocket.send(json.dumps(response))
        print(f"已发送运势给: {sender_name}, 运势为: {user_fortunes[user_id][0]}")

# WebSocket 服务器，等待反向连接
async def websocket_server(websocket, path):
    print("WebSocket 连接已建立")
    try:
        async for message in websocket:
            data = json.loads(message)

            # 处理 OneBot 的消息事件
            if 'post_type' in data and data['post_type'] == 'message':  # 处理消息事件
                await handle_message(websocket, data)
    except websockets.ConnectionClosed:
        print("连接关闭")

# 启动 WebSocket 服务器
async def main():
    # 启动 WebSocket 服务器并监听 8081 端口
    async with websockets.serve(websocket_server, "127.0.0.1", 8081):
        print("等待反向 WebSocket 连接...")
        await asyncio.Future()  # 保持服务器运行

# 启动 WebSocket 服务器
asyncio.run(main())
