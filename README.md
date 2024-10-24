# QQ 塔罗运势机器人

## 项目简介
这是一个基于 WebSocket 的 QQ 机器人，提供每日运势和塔罗牌占卜功能。主要功能：
- **每日运势**：根据用户 ID 生成当天的随机运势。
- **塔罗牌占卜**：随机抽取塔罗牌并生成包含解释和图片的合成图。

## 文件结构
- `bot.py`：处理 WebSocket 连接、消息接收、运势生成、塔罗牌抽取及图片发送。
- `tarot.py`：加载塔罗牌数据，生成合成图片。
- `TarotData.yml`：塔罗牌数据文件。
- `TarotImages/`：塔罗牌图片存放目录。
- `output/`：合成图片保存目录。

## 使用步骤
1. 安装依赖：
   ```bash
   pip install websockets pillow pyyaml
   ```
2. 准备塔罗牌数据和图片（TarotData.yml 与 TarotImages/）。
   运行机器人：
   ```bash
   python bot.py
   ```

## 主要命令
- /运势：生成或获取当天运势。
- /tarot 或 塔罗牌：抽取一张塔罗牌并发送解读和图片。

## 日志记录
所有消息会记录在 qq_message_log.txt 文件中。

## 依赖项与许可证

本项目源码遵循 MIT 协议，允许自由使用、修改和分发。