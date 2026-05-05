"""增强健康检查端点"""
import os
import time
import shutil
import logging
from fastapi import APIRouter
from sqlalchemy import text
from database import SessionLocal

router = APIRouter(tags=["运维"])
logger = logging.getLogger(__name__)


def _check_database() -> tuple[str, str | None]:
    """数据库连通性检查，不暴露内部错误"""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return "ok", None
    except Exception:
        logger.exception("健康检查: 数据库连接失败")
        return "error", "连接失败"


def _check_disk() -> tuple[str, dict]:
    """磁盘空间检查"""
    try:
        usage = shutil.disk_usage("/")
        free_gb = round(usage.free / (1024 ** 3), 1)
        status = "ok" if free_gb >= 1 else "warning"
        return status, {"free_gb": free_gb}
    except Exception:
        return "unknown", {}


def _check_ai_api() -> tuple[str, float | None]:
    """AI API 延迟检查（可选，仅当配置了 API KEY 时）"""
    api_key = os.getenv("AI_API_KEY", "")
    if not api_key:
        return "skipped", None
    try:
        import httpx
        api_base = os.getenv("AI_API_BASE_URL", "https://api.openai.com/v1")
        start = time.time()
        with httpx.Client(timeout=5) as client:
            resp = client.get(
                f"{api_base}/models",
                headers={"Authorization": f"Bearer {api_key}"},
            )
        latency_ms = round((time.time() - start) * 1000)
        if resp.status_code < 500:
            return "ok", latency_ms
        return "error", latency_ms
    except Exception:
        return "error", None


@router.get("/health")
def health_check():
    """系统健康检查: 数据库 + 磁盘 + AI API（可选）

    返回 degraded 时不代表完全不可用，仅表示部分功能受限。
    不暴露内部错误细节。
    """
    overall = "healthy"
    checks = {}

    # 数据库
    db_status, db_err = _check_database()
    checks["database"] = db_status
    if db_err:
        overall = "degraded"

    # 磁盘
    disk_status, disk_info = _check_disk()
    checks["disk"] = disk_status
    checks.update(disk_info)
    if disk_status in ("warning", "error"):
        overall = "degraded"

    # AI API（可选）
    ai_status, ai_latency = _check_ai_api()
    if ai_status != "skipped":
        checks["ai_api"] = ai_status
        if ai_latency is not None:
            checks["ai_api_latency_ms"] = ai_latency
        if ai_status == "error":
            overall = "degraded"

    return {"status": overall, "checks": checks}
