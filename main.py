import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.api import user_api, admin_api, agent_api
from app.core.logger import logger

# 自动创建全部数据表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="基于AI智能体的智慧文旅系统", version="1.0")

# 跨域，允许Vue前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(user_api.router, prefix="/api/user", tags=["用户端接口"])
app.include_router(admin_api.router, prefix="/api/admin", tags=["管理后台接口"])
app.include_router(agent_api.router, prefix="/api/agent", tags=["AI智能体接口"])

# 托管前端页面（访问 http://127.0.0.1:8000/ 打开智慧文旅前端）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

logger.info("智慧文旅后端服务启动成功！访问文档地址： http://127.0.0.1:8000/docs")
logger.info("智慧文旅前端页面： http://127.0.0.1:8000/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
