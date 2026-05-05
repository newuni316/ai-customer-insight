"""健康检查端点"""
import shutil
from fastapi import APIRouter
from sqlalchemy import text
from database import SessionLocal

router = APIRouter(tags=["运维"])


@router.get("/health")
def health_check():
    """系统健康检查: 数据库 + 磁盘空间"""
    status = {"status": "healthy", "checks": {}}

    # 数据库连接
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        status["checks"]["database"] = "ok"
    except Exception as e:
        status["checks"]["database"] = f"error: {str(e)}"
        status["status"] = "degraded"

    # 磁盘空间
    try:
        usage = shutil.disk_usage("/")
        free_gb = round(usage.free / (1024 ** 3), 1)
        status["checks"]["disk_free_gb"] = free_gb
        if free_gb < 1:
            status["status"] = "degraded"
    except Exception:
        status["checks"]["disk"] = "unknown"

    return status
