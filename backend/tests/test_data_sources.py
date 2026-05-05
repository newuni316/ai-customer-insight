"""数据源测试"""
import pytest
from datetime import datetime
from services.data_sources.csv_source import CSVSource
from services.data_sources.webhook_source import parse_webhook_payload


@pytest.mark.asyncio
async def test_csv_source_valid():
    """合法 CSV 数据源"""
    import pandas as pd
    df = pd.DataFrame([
        {"date": "2024-01-15", "source": "淘宝", "content": "好评"},
        {"date": "2024-01-16", "source": "京东", "content": "差评"},
    ])
    csv_bytes = df.to_csv(index=False).encode()
    source = CSVSource(csv_bytes)

    results = []
    async for item in source.fetch():
        results.append(item)
    assert len(results) == 2
    assert results[0].source == "淘宝"


@pytest.mark.asyncio
async def test_csv_source_missing_columns():
    """缺少必需列"""
    csv_bytes = b"name,value\nfoo,bar"
    source = CSVSource(csv_bytes)
    with pytest.raises(ValueError, match="缺少必需列"):
        async for _ in source.fetch():
            pass


def test_webhook_zendesk():
    """Zendesk Webhook 解析"""
    payload = {
        "ticket": {
            "id": 12345,
            "description": "产品质量有问题",
            "status": "open",
            "priority": "high",
            "created_at": "2024-01-15T10:30:00Z",
        }
    }
    result = parse_webhook_payload("zendesk", payload)
    assert result is not None
    assert result.source == "zendesk"
    assert "产品质量" in result.content


def test_webhook_custom():
    """自定义 Webhook"""
    payload = {
        "data": {
            "source": "自定义系统",
            "content": "客户反馈内容",
            "date": "2024-01-15T10:30:00",
        }
    }
    result = parse_webhook_payload("custom", payload["data"])
    assert result is not None


def test_webhook_unsupported():
    """不支持的平台"""
    result = parse_webhook_payload("unknown_platform", {})
    assert result is None
