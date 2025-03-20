"""聊天相关的数据模型。"""
from typing import List, Optional, Any

from pydantic import BaseModel, Field


class Message(BaseModel):
    """聊天消息模型。"""
    
    role: str = Field(..., description="消息发送者角色，如'user'或'assistant'")
    content: str = Field(..., description="消息内容")
    

class ChatRequest(BaseModel):
    """聊天请求模型。"""
    
    message: str = Field(..., description="用户消息内容")
    conversation_id: Optional[str] = Field(None, description="对话ID，用于继续现有对话")
    

class ChatResponse(BaseModel):
    """聊天响应模型。"""
    
    response: str = Field(..., description="助手的回复内容")
    conversation_id: str = Field(..., description="对话ID")
    thoughts: Optional[List[Any]] = Field(None, description="思考过程（可选，用于调试）")


class ConversationHistory(BaseModel):
    """对话历史模型。"""
    
    conversation_id: str = Field(..., description="对话ID")
    messages: List[Message] = Field(default_factory=list, description="消息历史记录") 