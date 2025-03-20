"""Agent工具模块。"""
import datetime
import json
from typing import List

from langchain.tools import BaseTool, StructuredTool


def get_current_time() -> str:
    """获取当前时间。
    
    Returns:
        当前时间的字符串表示
    """
    now = datetime.datetime.now()
    return f"当前时间是: {now.strftime('%Y-%m-%d %H:%M:%S')}"


def search_knowledge_base(query: str) -> str:
    """搜索知识库（示例方法）。
    
    Args:
        query: 搜索查询关键词
        
    Returns:
        搜索结果
    """
    # 这里只是一个简单的示例，实际应用中可以连接到向量数据库
    knowledge_base = {
        "chatverse": "ChatVerse是一个基于Langchain、FastAPI和DeepSeek构建的智能聊天机器人平台。",
        "langchain": "LangChain是一个用于构建LLM应用的框架，提供了丰富的组件和工具。",
        "fastapi": "FastAPI是一个现代、快速、高性能的Web框架，用于构建API。",
        "deepseek": "DeepSeek是一个强大的语言模型，提供自然语言处理能力。"
    }
    
    # 简单的关键词匹配搜索
    results = []
    for key, value in knowledge_base.items():
        if query.lower() in key.lower():
            results.append(f"{key}: {value}")
    
    if results:
        return "\n".join(results)
    else:
        return f"未找到与'{query}'相关的信息。"


def create_agent_tools() -> List[BaseTool]:
    """创建Agent可用的工具列表。
    
    Returns:
        工具列表
    """
    tools = [
        StructuredTool.from_function(
            func=get_current_time,
            name="get_current_time",
            description="获取当前时间",
        ),
        StructuredTool.from_function(
            func=search_knowledge_base,
            name="search_knowledge_base",
            description="搜索知识库获取信息",
        ),
    ]
    
    return tools 