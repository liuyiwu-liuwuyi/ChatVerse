"""聊天机器人Agent模块，使用纯LCEL架构。"""
from typing import List, Dict, Any
import logging

from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate
from langchain.tools import BaseTool
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import ToolMessage, AIMessage

from app.utils.llm import create_llm

class ChatAgent:
    """聊天机器人Agent实现，使用纯LCEL架构。"""
    
    def __init__(self, tools: List[BaseTool] = None):
        """初始化聊天Agent。
        
        Args:
            tools: Agent可用的工具列表
        """
        self.llm = create_llm(temperature=0.7)
        self.tools = tools or []
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.chain = self._create_pure_lcel_chain()
    
    def _create_pure_lcel_chain(self):
        """使用纯LCEL架构创建Agent链。
        
        Returns:
            LCEL格式的Agent链
        """
        # 创建提示模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个友好的AI助手，可以与用户进行对话并解答问题。
            
你可以使用提供的工具来帮助用户解决问题。请尽可能详细地回答用户的问题。

如果不需要使用工具，请直接回答用户的问题。"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ])
        
        # 使用RunnableLambda获取聊天历史
        def get_chat_history(inputs):
            return self.memory.load_memory_variables({}).get("chat_history", [])
        
        # 创建LCEL链（使用管道操作符）
        chain = (
            RunnablePassthrough.assign(
                chat_history=RunnableLambda(get_chat_history)
            )
            | prompt 
            | self.llm.bind_tools(self.tools)
        )
        
        # 创建递归处理函数来支持多轮工具调用
        def process_response(inputs):
            # 直接调用链处理用户消息
            response = chain.invoke({
                "input": inputs["input"],
            })
            
            return {
                "output": response.content if hasattr(response, "content") else str(response),
                "intermediate_steps": []
            }
            
        # 返回完整的LCEL链
        return RunnableLambda(process_response)
    
    def _update_memory(self, input_message: str, output_message: str) -> None:
        """更新对话记忆。
        
        Args:
            input_message: 用户输入的消息
            output_message: 系统回复的消息
        """
        self.memory.chat_memory.add_user_message(input_message)
        self.memory.chat_memory.add_ai_message(output_message)
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        """处理用户消息。
        
        Args:
            message: 用户输入的消息
            
        Returns:
            处理结果
        """
        try:
            # 使用纯LCEL链处理消息
            result = await self.chain.ainvoke({"input": message})
            
            # 获取响应和中间步骤
            response = result.get("output", "")
            intermediate_steps = result.get("intermediate_steps", [])
            
            # 更新对话记忆
            self._update_memory(message, response)
            
            return {
                "response": response,
                "thoughts": intermediate_steps
            }
        except Exception as e:
            # 如果处理失败，返回简单响应
            logging.error(f"Agent处理消息失败: {str(e)}")
            return {
                "response": "我理解您的问题，但目前处理过程中遇到了一些技术问题。请稍后再试或换一种方式提问。",
                "thoughts": []
            }
