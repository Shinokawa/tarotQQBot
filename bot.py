import asyncio
import websockets
import json
import random

# 运势列表
fortunes = ["大吉", "吉", "中吉", "小吉", "末吉", "凶", "大凶"]

# 随机生成运势
def get_fortune():
    return random.choice(fortunes)

# 处理接收到的消息
async def handle_message(websocket, message):
    # 判断消息是否以 "/运势" 开头
    if 'message' in message and message['message'].startswith("/运势"):
        # 随机生成运势
        fortune = get_fortune()

        # 获取发送消息的人的昵称或ID
        sender = message['sender']
        sender_name = sender.get('nickname', f"用户{sender['user_id']}")

        # 准备回复内容
        response = {
            "action": "send_group_msg",  # 发送群消息
            "params": {
                "group_id": message['group_id'],  # 群号
                "message": f"{sender_name} 今日的运势是: {fortune}"
            }
        }

        # 发送回复
        await websocket.send(json.dumps(response))
        print(f"已发送运势给: {sender_name}, 运势为: {fortune}")

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
