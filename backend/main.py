"""AI Customer Insight Dashboard - 后端入口（生产级）"""
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from config import get_settings
from routers import auth, feedback, analytics, data_sources
from health import router as health_router
from middleware import RequestLoggingMiddleware, RateLimitMiddleware

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时自动迁移（可选），不再直接 create_all"""
    if settings.AUTO_MIGRATE:
        logger.info("AUTO_MIGRATE=true, 执行数据库迁移...")
        try:
            from alembic.config import Config as AlembicConfig
            from alembic import command as alembic_command
            alembic_cfg = AlembicConfig("alembic.ini")
            alembic_command.upgrade(alembic_cfg, "head")
            logger.info("数据库迁移完成")
        except Exception as e:
            logger.warning(f"自动迁移失败，回退到 create_all: {e}")
            Base.metadata.create_all(bind=engine)
    else:
        # 开发环境直接 create_all
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="AI Customer Insight API",
    description="AI 驱动的客户反馈洞察平台",
    version="1.0.0",
    lifespan=lifespan,
)

# 中间件（顺序重要：先限流，再日志，最后 CORS）
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由
app.include_router(health_router)
app.include_router(auth.router)
app.include_router(feedback.router)
app.include_router(analytics.router)
app.include_router(data_sources.router)


@app.get("/")
def root():
    return {"name": "AI Customer Insight API", "version": "1.0.0", "docs": "/docs"}
