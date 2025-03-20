"""聊天API路由。"""
import json
import logging
import os
import uuid
from typing import Dict, Union

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect

from app.agents.chat_agent import ChatAgent
from app.agents.simple_chat import SimpleChat
from app.agents.tools import create_agent_tools
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


# 缓存聊天模型实例
_chat_cache: Dict[str, Union[ChatAgent, SimpleChat]] = {}

# 检查是否使用简单聊天模式
USE_SIMPLE_CHAT = os.getenv('USE_SIMPLE_CHAT', 'false').lower() == 'true'


def get_chat_service():
    """获取聊天服务依赖。"""
    return ChatService()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket聊天端点。"""
    await websocket.accept()
    
    # 默认创建新的会话ID
    conversation_id = str(uuid.uuid4())
    chat_service = ChatService()
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            try:
                # 解析消息
                message_data = json.loads(data)
                user_message = message_data.get("message", "")
                # 如果客户端提供了会话ID，则使用它
                if message_data.get("conversation_id"):
                    conversation_id = message_data.get("conversation_id")
            except json.JSONDecodeError:
                # 如果不是JSON，直接使用文本作为消息
                user_message = data
            
            # 发送正在处理的消息
            await websocket.send_json({
                "type": "thinking",
                "content": "正在思考...",
                "conversation_id": conversation_id
            })
            
            try:
                # 获取或创建聊天模型
                if conversation_id not in _chat_cache:
                    if USE_SIMPLE_CHAT:
                        # 使用简单聊天模型
                        logging.info("使用简单聊天模型")
                        _chat_cache[conversation_id] = SimpleChat()
                    else:
                        # 使用Agent
                        logging.info("使用Agent聊天模型")
                        tools = create_agent_tools()
                        _chat_cache[conversation_id] = ChatAgent(tools=tools)
                
                chat_model = _chat_cache[conversation_id]
                
                # 保存用户消息
                chat_service.save_message(
                    conversation_id=conversation_id,
                    role="user",
                    content=user_message
                )
                
                # 处理消息
                result = await chat_model.process_message(user_message)
                
                # 保存助手回复
                chat_service.save_message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=result["response"]
                )
                
                # 发送响应
                await websocket.send_json({
                    "type": "response",
                    "content": result["response"],
                    "conversation_id": conversation_id
                })
                
            except Exception as e:
                # 记录错误
                logging.error(f"WebSocket处理消息时发生错误: {str(e)}")
                
                # 尝试简单回退方案
                try:
                    # 如果常规方法失败，尝试直接使用简单聊天
                    if not isinstance(_chat_cache.get(conversation_id), SimpleChat):
                        _chat_cache[conversation_id] = SimpleChat()
                        logging.info("切换到简单聊天模式")
                        
                    chat_model = _chat_cache[conversation_id]
                    result = await chat_model.process_message(user_message)
                    
                    # 保存对话记录
                    chat_service.save_message(
                        conversation_id=conversation_id,
                        role="user",
                        content=user_message
                    )
                    chat_service.save_message(
                        conversation_id=conversation_id,
                        role="assistant",
                        content=result["response"]
                    )
                    
                    # 发送响应
                    await websocket.send_json({
                        "type": "response",
                        "content": result["response"],
                        "conversation_id": conversation_id
                    })
                    
                except Exception as inner_e:
                    logging.error(f"WebSocket备选方案也失败了: {str(inner_e)}")
                    
                    # 发送错误响应
                    fallback_response = "抱歉，我现在无法处理您的请求。可能是网络问题或API限制。请稍后再试。"
                    
                    try:
                        chat_service.save_message(
                            conversation_id=conversation_id,
                            role="assistant",
                            content=fallback_response
                        )
                    except:
                        pass
                    
                    await websocket.send_json({
                        "type": "error",
                        "content": fallback_response,
                        "conversation_id": conversation_id
                    })
    
    except WebSocketDisconnect:
        logging.info(f"WebSocket客户端断开连接")
    except Exception as e:
        logging.error(f"WebSocket连接错误: {str(e)}")


@router.post("/message", response_model=ChatResponse)
async def chat_message(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """处理聊天消息。
    
    Args:
        request: 聊天请求
        chat_service: 聊天服务实例
        
    Returns:
        聊天响应
    """
    try:
        # 生成或使用现有的会话ID
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # 获取或创建聊天模型
        if conversation_id not in _chat_cache:
            if USE_SIMPLE_CHAT:
                # 使用简单聊天模型
                logging.info("使用简单聊天模型")
                _chat_cache[conversation_id] = SimpleChat()
            else:
                # 使用Agent
                logging.info("使用Agent聊天模型")
                tools = create_agent_tools()
                _chat_cache[conversation_id] = ChatAgent(tools=tools)
        
        chat_model = _chat_cache[conversation_id]
        
        # 处理消息
        result = await chat_model.process_message(request.message)
        
        # 保存对话记录
        chat_service.save_message(
            conversation_id=conversation_id,
            role="user",
            content=request.message
        )
        chat_service.save_message(
            conversation_id=conversation_id,
            role="assistant",
            content=result["response"]
        )
        
        return ChatResponse(
            response=result["response"],
            conversation_id=conversation_id,
            thoughts=result.get("thoughts")
        )
    except Exception as e:
        # 记录错误
        logging.error(f"处理消息时发生错误: {str(e)}")
        
        # 尝试简单回退方案
        try:
            # 如果常规方法失败，尝试直接使用简单聊天
            if 'conversation_id' in locals() and conversation_id in _chat_cache:
                if not isinstance(_chat_cache[conversation_id], SimpleChat):
                    _chat_cache[conversation_id] = SimpleChat()
                    logging.info("切换到简单聊天模式")
                    
                chat_model = _chat_cache[conversation_id]
                result = await chat_model.process_message(request.message)
                
                # 保存对话记录
                chat_service.save_message(
                    conversation_id=conversation_id,
                    role="user",
                    content=request.message
                )
                chat_service.save_message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=result["response"]
                )
                
                return ChatResponse(
                    response=result["response"],
                    conversation_id=conversation_id,
                    thoughts=[]
                )
        except Exception as inner_e:
            logging.error(f"备选方案也失败了: {str(inner_e)}")
        
        # 生成备选响应
        fallback_response = "抱歉，我现在无法处理您的请求。可能是网络问题或API限制。请稍后再试。"
        
        # 如果已有会话ID，尝试保存错误记录
        if 'conversation_id' in locals():
            try:
                chat_service.save_message(
                    conversation_id=conversation_id,
                    role="user",
                    content=request.message
                )
                chat_service.save_message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=fallback_response
                )
            except:
                # 如果保存失败也忽略
                pass
                
            # 返回备选响应
            return ChatResponse(
                response=fallback_response,
                conversation_id=conversation_id,
                thoughts=[]
            )
        
        # 如果没有会话ID，创建新的
        new_conversation_id = str(uuid.uuid4())
        return ChatResponse(
            response=fallback_response,
            conversation_id=new_conversation_id,
            thoughts=[]
        )


@router.get("/history/{conversation_id}")
async def chat_history(
    conversation_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """获取聊天历史。
    
    Args:
        conversation_id: 对话ID
        chat_service: 聊天服务实例
        
    Returns:
        聊天历史记录
    """
    history = chat_service.get_conversation_history(conversation_id)
    if not history:
        raise HTTPException(status_code=404, detail="对话记录不存在")
    return history 