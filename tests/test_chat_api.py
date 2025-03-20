"""聊天API测试。"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_redirect():
    """测试根路径重定向。"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_api_info():
    """测试API信息端点。"""
    response = client.get("/api")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "version" in response.json()


def test_chat_message():
    """测试聊天消息API。"""
    # 注意：这需要一个可用的LLM API密钥和网络连接
    # 在测试环境中可能需要模拟这个调用
    response = client.post(
        "/chat/message",
        json={"message": "你好"}
    )
    assert response.status_code == 200
    assert "response" in response.json()
    assert "conversation_id" in response.json()
    
    # 保存会话ID用于历史测试
    conversation_id = response.json()["conversation_id"]
    return conversation_id


def test_chat_history():
    """测试聊天历史API。"""
    # 需要先发送一条消息获取conversation_id
    conversation_id = test_chat_message()
    
    response = client.get(f"/chat/history/{conversation_id}")
    assert response.status_code == 200
    assert "messages" in response.json()
    assert len(response.json()["messages"]) >= 2  # 至少有一对用户-助手消息
