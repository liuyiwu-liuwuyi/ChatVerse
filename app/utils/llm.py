"""Utility functions for LLM operations."""
from typing import Optional, Union
import logging

from langchain.base_language import BaseLanguageModel
from langchain_deepseek import ChatDeepSeek
from pydantic import SecretStr
import httpx

from config.deepseek_config import config

def check_api_key(api_key: Union[str, SecretStr], base_url: str = "https://api.deepseek.com/v1") -> bool:
    """检查API密钥是否有效。
    
    Args:
        api_key: DeepSeek API密钥
        base_url: API基础URL
        
    Returns:
        API密钥是否有效
    """
    try:
        # 将SecretStr转换为字符串
        key = api_key.get_secret_value() if isinstance(api_key, SecretStr) else api_key
        
        # 发送简单请求检查API密钥
        with httpx.Client(timeout=10.0) as client:
            response = client.get(
                f"{base_url}/models",
                headers={"Authorization": f"Bearer {key}"}
            )
        
        # 检查响应状态
        return response.status_code == 200
    except Exception as e:
        logging.warning(f"API密钥检查失败: {str(e)}")
        return False

def create_llm(model_name: str = "deepseek-chat",
              temperature: float = 0.7,
              api_key: Optional[Union[str, SecretStr]] = None) -> BaseLanguageModel:
    """创建语言模型实例。

    Args:
        model_name: 使用的模型名称。
        temperature: 生成响应时的温度参数。
        api_key: DeepSeek API密钥。

    Returns:
        语言模型实例。
    """
    model_config = get_model_config(model_name)
    
    # 确定API密钥
    final_api_key = (SecretStr(api_key) if isinstance(api_key, str) else api_key) or config.api_key
    
    # 检查API密钥是否有效
    if not check_api_key(final_api_key, config.base_url):
        logging.warning("DeepSeek API密钥无效或API服务不可用，请检查配置")
    
    return ChatDeepSeek(
        model=model_name,
        temperature=temperature,
        max_tokens=model_config.get("max_tokens", 1000),
        api_key=final_api_key,
        base_url=config.base_url
    )

def get_model_config(model_name: str) -> dict:
    """获取特定模型的配置。

    Args:
        model_name: 模型名称。

    Returns:
        包含模型配置的字典。
    """
    configs = {
        "deepseek-chat": {
            "max_tokens": 4096,
            "default_temperature": 0.7,
            "supports_functions": True
        }
    }
    return configs.get(model_name, {}) 