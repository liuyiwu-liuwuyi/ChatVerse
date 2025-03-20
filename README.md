# ChatVerse - AI聊天机器人平台

基于Langchain、FastAPI和DeepSeek构建的智能聊天机器人平台。

## 功能特点

- 基于DeepSeek大模型的智能对话能力
- 可扩展的Agent框架
- RESTful API接口
- 简单易用的聊天界面

## 技术栈

- **后端框架**：FastAPI
- **LLM框架**：Langchain
- **大语言模型**：DeepSeek
- **部署**：Docker (可选)

## 安装与运行

### 环境要求

- Python 3.9+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

创建`.env`文件，设置必要的API密钥：

```
deepseek_api_key="your_api_key_here"
```

### 启动服务

```bash
uvicorn app.main:app --reload
```

## 项目结构

```
chatverse/
├── app/                    # 应用主目录
│   ├── api/                # API路由和端点
│   ├── agents/             # Agent组件
│   ├── core/               # 核心功能
│   ├── schemas/            # 数据模型
│   ├── services/           # 业务逻辑
│   ├── utils/              # 工具函数
│   └── main.py             # 应用入口
├── config/                 # 配置文件
├── tests/                  # 测试目录
├── .env                    # 环境变量
├── .gitignore              # Git忽略文件
├── requirements.txt        # 项目依赖
└── README.md               # 项目说明
``` 