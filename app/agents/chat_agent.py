"""聊天机器人Agent模块。"""
from typing import List, Dict, Any

from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool

from app.utils.llm import create_llm

class ChatAgent:
    """聊天机器人Agent实现。"""
    
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
        self.agent = self._create_agent()
    
    def _create_agent(self) -> AgentExecutor:
        """创建Agent执行器。
        
        Returns:
            Agent执行器实例
        """
        # 定义Agent提示模板，更明确地引导模型使用ReAct格式
        prompt = PromptTemplate.from_template(
            """你是一个友好的AI助手，可以与用户进行对话并解答问题。

你有权限使用以下工具:
{tools}

可用工具名称: {tool_names}

使用工具时，必须使用以下格式：
思考: 你应该在这里思考如何解决问题的过程
行动: 工具名称
行动输入: {{
    "参数": "值"
}}
观察: 工具返回的结果
... (可以有多轮思考/行动/观察)
最终回答: 向用户提供最终答案

如果不需要使用工具，请直接使用以下格式：
思考: 你的思考过程
最终回答: 向用户提供的最终答案

聊天历史:
{chat_history}

用户问题: {input}

{agent_scratchpad}
"""
        )
        
        # 创建反应型Agent，添加错误处理
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # 创建Agent执行器，添加错误处理
        return AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,  # 添加解析错误处理
            max_iterations=3  # 限制最大迭代次数
        )
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        """处理用户消息。
        
        Args:
            message: 用户输入的消息
            
        Returns:
            处理结果
        """
        try:
            result = await self.agent.ainvoke({"input": message})
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