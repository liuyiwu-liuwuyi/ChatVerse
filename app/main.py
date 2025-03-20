"""应用入口模块。"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from app.api import chat

# 创建FastAPI应用
app = FastAPI(
    title="ChatVerse",
    description="AI聊天机器人平台API",
    version="0.1.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
async def root():
    """API根路径，重定向到聊天界面。"""
    return RedirectResponse(url="/static/index.html")


@app.get("/api")
async def api_info():
    """API信息页面。"""
    return {
        "message": "欢迎使用ChatVerse API",
        "docs_url": "/docs",
        "version": app.version
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 