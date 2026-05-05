"""AI Customer Insight Dashboard - 后端入口（生产级增强版）"""
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from database import engine, Base, check_db_connection
from config import get_settings
from routers import auth, feedback, analytics, data_sources, orders, metrics, decisions
from health import router as health_router
from middleware import RequestLoggingMiddleware, RateLimitMiddleware
from exceptions import register_exception_handlers
from logging_config import setup_logging, RequestIDMiddleware

# 初始化日志（必须在 app 创建前）
setup_logging()
settings = get_settings()
logger = logging.getLogger(__name__)

# 环境判断
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全响应头"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时自动迁移 + 数据库连接检查"""
    # 数据库健康检查
    if not check_db_connection():
        logger.error("数据库连接失败，应用可能无法正常工作")

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
        Base.metadata.create_all(bind=engine)
    yield


# 生产环境禁用 docs
app = FastAPI(
    title="AI Customer Insight API",
    description="AI 驱动的客户反馈洞察平台",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None if IS_PRODUCTION else "/docs",
    redoc_url=None if IS_PRODUCTION else "/redoc",
    openapi_url=None if IS_PRODUCTION else "/openapi.json",
)

# 注册全局异常处理器（统一 JSON 错误格式）
register_exception_handlers(app)

# 中间件（顺序重要：先安全头，再限流，再日志，再请求ID，最后 CORS）
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestIDMiddleware)

# CORS：从环境变量读取允许的源，默认仅 localhost
cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
cors_origins = [o.strip() for o in cors_origins_str.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)

# 路由
app.include_router(health_router)
app.include_router(auth.router)
app.include_router(feedback.router)
app.include_router(analytics.router)
app.include_router(data_sources.router)
app.include_router(orders.router)
app.include_router(metrics.router)
app.include_router(decisions.router)


@app.get("/")
def root():
    return {"name": "AI Customer Insight API", "version": "1.0.0"}
