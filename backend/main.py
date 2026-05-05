"""AI Customer Insight Dashboard - 后端入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import auth, feedback, analytics

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Customer Insight API",
    description="AI 驱动的客户反馈洞察平台 API",
    version="1.0.0",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(feedback.router)
app.include_router(analytics.router)


@app.get("/")
def root():
    return {
        "name": "AI Customer Insight API",
        "version": "1.0.0",
        "docs": "/docs",
    }
