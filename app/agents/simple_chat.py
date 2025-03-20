"""简单聊天模型模块，不使用Agent框架。"""
from typing import Dict, Any, List

from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

from app.utils.llm import create_llm

class SimpleChat:
    """简单聊天实现，不使用Agent框架，直接调用LLM。"""
    
    def __init__(self):
        """初始化简单聊天模型。"""
        self.llm = create_llm(temperature=0.7)
        
        # 创建记忆
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # 创建提示模板
        template = """你是一个友好、有用的AI助手，可以与用户进行对话并解答问题。

聊天历史:
{chat_history}

人类: {input}
AI: """
        
        prompt = PromptTemplate.from_template(template)
        
        # 创建对话链
        self.chain = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=prompt,
            verbose=True
        )
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        """处理用户消息。
        
        Args:
            message: 用户输入的消息
            
        Returns:
            处理结果
        """
        try:
            result = await self.chain.ainvoke({"input": message})
            return {
                "response": result.get("response", ""),
                "thoughts": []  # 简单模型没有思考过程
            }
        except Exception as e:
            # 错误处理
            import logging
            logging.error(f"聊天处理失败: {str(e)}")
            return {
                "response": "抱歉，我现在无法正确处理您的请求。请稍后再试。",
                "thoughts": []
            } 