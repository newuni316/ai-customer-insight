"""数据源管理路由"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import User
from auth import get_current_user
from services.data_sources.api_source import APISource
from services.data_sources.webhook_source import parse_webhook_payload

router = APIRouter(prefix="/api/sources", tags=["数据源"])


class APISourceConfig(BaseModel):
    name: str
    base_url: str
    auth_token: str


class WebhookPayload(BaseModel):
    platform: str = "custom"
    data: dict


@router.post("/api/test")
async def test_api_source(config: APISourceConfig):
    """测试外部 API 数据源连接"""
    source = APISource(config.base_url, config.auth_token)
    ok = await source.test_connection()
    if not ok:
        raise HTTPException(status_code=402, detail="连接测试失败")
    return {"status": "ok", "message": f"成功连接到 {config.name}"}


@router.post("/api/sync")
async def sync_from_api(
    config: APISourceConfig,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """从外部 API 同步反馈数据"""
    from models import Feedback
    source = APISource(config.base_url, config.auth_token)
    count = 0
    async for raw in source.fetch():
        fb = Feedback(
            user_id=current_user.id,
            source=raw.source,
            content=raw.content,
            date=raw.date,
        )
        db.add(fb)
        count += 1
    db.commit()
    return {"message": f"从 {config.name} 同步了 {count} 条反馈", "count": count}


@router.post("/webhook/{platform}")
async def receive_webhook(
    platform: str,
    payload: WebhookPayload,
    db: Session = Depends(get_db),
):
    """接收第三方平台 Webhook 推送（无需认证）"""
    from models import Feedback
    raw = parse_webhook_payload(platform, payload.data)
    if not raw:
        raise HTTPException(status_code=400, detail=f"不支持的平台: {platform}")

    fb = Feedback(
        user_id=1,  # 默认用户，生产环境应根据 webhook header 识别
        source=raw.source,
        content=raw.content,
        date=raw.date,
    )
    db.add(fb)
    db.commit()
    return {"status": "received", "id": fb.id}
