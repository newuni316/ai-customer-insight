"""Webhook 实时数据源 - 接收第三方推送"""
from datetime import datetime
from .base import RawFeedback


def parse_webhook_payload(platform: str, payload: dict) -> RawFeedback | None:
    """
    解析不同平台的 Webhook 推送数据
    
    支持平台: zendesk, feishu, wecom, custom
    """
    if platform == "zendesk":
        ticket = payload.get("ticket", {})
        return RawFeedback(
            source="zendesk",
            content=ticket.get("description", ""),
            date=datetime.fromisoformat(ticket["created_at"].replace("Z", "+00:00")),
            external_id=str(ticket.get("id", "")),
            metadata={"status": ticket.get("status"), "priority": ticket.get("priority")},
        )

    elif platform == "feishu":
        event = payload.get("event", {})
        msg = event.get("message", {})
        return RawFeedback(
            source="feishu",
            content=msg.get("content", ""),
            date=datetime.fromtimestamp(int(msg.get("create_time", "0")) / 1000),
            external_id=msg.get("message_id"),
        )

    elif platform == "custom":
        return RawFeedback(
            source=payload.get("source", "webhook"),
            content=payload.get("content", ""),
            date=datetime.fromisoformat(payload.get("date", datetime.utcnow().isoformat())),
            external_id=payload.get("id"),
            metadata=payload.get("metadata"),
        )

    return None
