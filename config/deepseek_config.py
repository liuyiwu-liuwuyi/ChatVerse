import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# 自动查找项目根目录的.env文件
BASE_DIR = Path(__file__).parent.parent
_env_path = BASE_DIR / '.env'

if _env_path.exists():
    load_dotenv(_env_path)
else:
    import warnings
    warnings.warn(f"未找到环境变量文件: {_env_path}")

class Config:
    def __init__(self):
        # 确定是否使用本地模式（不依赖外部API）
        self._local_mode = os.getenv('USE_LOCAL_MODE', 'false').lower() == 'true'
        if self._local_mode:
            logging.info("使用本地模式，不会调用DeepSeek API")
    
    @property
    def is_local_mode(self) -> bool:
        """是否使用本地模式。"""
        return self._local_mode
    
    @property
    def api_key(self):
        """获取API密钥。"""
        key = os.getenv('deepseek_api_key')
        if not key and not self._local_mode:
            logging.warning("未设置DeepSeek API密钥，API调用可能会失败")
        return key
    
    @property
    def base_url(self):
        """获取API基础URL。"""
        return os.getenv('deepseek_base_url', "https://api.deepseek.com/v1")
    
    @property
    def chat_model(self):
        """获取聊天模型名称。"""
        return os.getenv('deepseek_model', "deepseek-chat")

config = Config() 