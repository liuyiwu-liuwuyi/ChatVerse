"""聊天服务模块。"""
from typing import Dict, List, Optional

from app.schemas.chat import ConversationHistory, Message


class ChatService:
    """聊天服务实现。"""
    
    def __init__(self):
        """初始化聊天服务。"""
        # 简单的内存存储，生产环境应使用数据库
        self._conversations: Dict[str, ConversationHistory] = {}
        
    def save_message(self, conversation_id: str, role: str, content: str) -> None:
        """保存聊天消息。
        
        Args:
            conversation_id: 对话ID
            role: 消息发送者角色
            content: 消息内容
        """
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = ConversationHistory(
                conversation_id=conversation_id,
                messages=[]
            )
            
        self._conversations[conversation_id].messages.append(
            Message(role=role, content=content)
        )
        
    def get_conversation_history(self, conversation_id: str) -> Optional[ConversationHistory]:
        """获取对话历史。
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            对话历史记录，如果不存在则返回None
        """
        return self._conversations.get(conversation_id)
        
    def get_messages(self, conversation_id: str) -> List[Message]:
        """获取对话中的所有消息。
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            消息列表
        """
        if conversation_id not in self._conversations:
            return []
            
        return self._conversations[conversation_id].messages
