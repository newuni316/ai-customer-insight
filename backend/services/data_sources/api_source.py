"""外部 API 数据源 - 对接第三方平台"""
import httpx
from datetime import datetime, timedelta
from typing import AsyncIterator
from .base import DataSource, RawFeedback


class APISource(DataSource):
    """
    通用 API 数据源，支持对接：
    - Zendesk: base_url="https://xxx.zendesk.com/api/v2", auth="Bearer xxx"
    - 微信公众号: base_url="https://api.weixin.qq.com/cgi-bin", auth="Bearer xxx"
    - 自定义 Webhook: base_url="https://your-api.com/feedbacks", auth="xxx"
    
    API 需返回如下 JSON 格式:
    {
      "data": [
        {"source": "xxx", "content": "xxx", "date": "2024-01-01", "id": "xxx"}
      ],
      "has_more": false,
      "next_cursor": "xxx"
    }
    """

    name = "api"

    def __init__(self, base_url: str, auth_token: str, headers: dict | None = None):
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token
        self.headers = headers or {}

    async def fetch(self, since: datetime | None = None) -> AsyncIterator[RawFeedback]:
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            **self.headers,
        }
        params = {}
        if since:
            params["since"] = since.isoformat()

        async with httpx.AsyncClient(timeout=30) as client:
            cursor = None
            while True:
                if cursor:
                    params["cursor"] = cursor

                resp = await client.get(
                    f"{self.base_url}/feedbacks",
                    headers=headers,
                    params=params,
                )
                resp.raise_for_status()
                data = resp.json()

                for item in data.get("data", []):
                    yield RawFeedback(
                        source=item.get("source", self.name),
                        content=item["content"],
                        date=datetime.fromisoformat(item["date"]),
                        external_id=item.get("id"),
                        metadata=item.get("metadata"),
                    )

                if not data.get("has_more"):
                    break
                cursor = data.get("next_cursor")
                if not cursor:
                    break

    async def test_connection(self) -> bool:
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}", **self.headers}
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self.base_url}/health", headers=headers)
                return resp.status_code < 500
        except Exception:
            return False
