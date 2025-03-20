"""项目运行脚本。"""
import argparse
import logging
import os
import sys

import uvicorn
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# 加载环境变量
load_dotenv()

def main():
    """主函数，解析命令行参数并启动服务。"""
    parser = argparse.ArgumentParser(description="ChatVerse AI聊天机器人服务")
    parser.add_argument('--host', default='0.0.0.0', help='服务监听主机地址')
    parser.add_argument('--port', type=int, default=8000, help='服务监听端口')
    parser.add_argument('--reload', action='store_true', help='是否启用热重载')
    parser.add_argument('--local-mode', action='store_true', help='是否使用本地模式（不调用外部API）')
    parser.add_argument('--simple-chat', action='store_true', help='使用简单聊天模式（不使用Agent框架）')
    args = parser.parse_args()
    
    # 设置本地模式环境变量
    if args.local_mode:
        os.environ['USE_LOCAL_MODE'] = 'true'
        logging.info("已启用本地模式，将不会调用DeepSeek API")
    
    # 设置简单聊天模式
    if args.simple_chat:
        os.environ['USE_SIMPLE_CHAT'] = 'true'
        logging.info("已启用简单聊天模式，不使用Agent框架")

    logging.info("启动 ChatVerse 服务...")
    logging.info(f"服务URL: http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{args.port}")
    
    # 检查API密钥
    api_key = os.getenv('deepseek_api_key')
    if not api_key and not args.local_mode:
        logging.warning("未设置DeepSeek API密钥 (deepseek_api_key)，API调用可能会失败")
    
    # 启动服务
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )

if __name__ == "__main__":
    main() 