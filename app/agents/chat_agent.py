"""聊天机器人Agent模块，使用LCEL架构。"""
from typing import List, Dict, Any

from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.tools import BaseTool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain_core.messages.utils import convert_to_openai_messages
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.agents import AgentExecutor, create_tool_calling_agent

from app.utils.llm import create_llm

class ChatAgent:
    """聊天机器人Agent实现，使用LCEL架构。"""
    
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
        self.agent_chain = self._create_agent_chain()
    
    def _create_agent_chain(self):
        """创建Agent链，使用LCEL架构。
        
        Returns:
            LCEL格式的Agent链
        """
        # 定义Agent提示模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个友好的AI助手，可以与用户进行对话并解答问题。
            
你可以使用提供的工具来帮助用户解决问题。请尽可能详细地回答用户的问题。

如果不需要使用工具，请直接回答用户的问题。"""),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        # 使用create_tool_calling_agent创建agent
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        
        # 创建Agent执行器
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        """处理用户消息。
        
        Args:
            message: 用户输入的消息
            
        Returns:
            处理结果
        """
        try:
            result = await self.agent_chain.ainvoke({"input": message})
            return {
                "response": result.get("output", ""),
                "thoughts": result.get("intermediate_steps", [])
            }
        except Exception as e:
            # 如果Agent处理失败，返回简单响应
            import logging
            logging.error(f"Agent处理消息失败: {str(e)}")
            return {
                "response": "我理解您的问题，但目前处理过程中遇到了一些技术问题。请稍后再试或换一种方式提问。",
                "thoughts": []
            } 