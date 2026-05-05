"""数据源管理路由"""
import ipaddress
from urllib.parse import urlparse
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import User
from auth import get_current_user
from services.data_sources.api_source import APISource
from services.data_sources.webhook_source import parse_webhook_payload

router = APIRouter(prefix="/api/sources", tags=["数据源"])

# 内网 IP 前缀，防止 SSRF 攻击
_PRIVATE_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
]


def _is_internal_url(url: str) -> bool:
    """检查 URL 是否指向内网地址（防 SSRF）"""
    try:
        hostname = urlparse(url).hostname
        if not hostname:
            return True
        ip = ipaddress.ip_address(hostname)
        return any(ip in net for net in _PRIVATE_NETWORKS)
    except ValueError:
        # hostname 不是 IP，可能是域名 — 允许通过
        return False


class APISourceConfig(BaseModel):
    name: str
    base_url: str
    auth_token: str


class WebhookPayload(BaseModel):
    platform: str = "custom"
    data: dict


@router.post("/api/test")
async def test_api_source(
    config: APISourceConfig,
    current_user: User = Depends(get_current_user),
):
    """测试外部 API 数据源连接（需要认证，防 SSRF）"""
    if _is_internal_url(config.base_url):
        raise HTTPException(status_code=400, detail="不允许访问内网地址")
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
