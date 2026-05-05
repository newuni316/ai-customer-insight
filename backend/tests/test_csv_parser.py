"""CSV 解析测试"""
import pytest
import io
import pandas as pd
from services.csv_parser import parse_csv


class MockUploadFile:
    """模拟 FastAPI UploadFile"""
    def __init__(self, content: bytes, filename: str = "test.csv"):
        self.filename = filename
        self._content = content

    async def read(self):
        return self._content


@pytest.mark.asyncio
async def test_parse_valid_csv():
    """测试解析合法 CSV"""
    df = pd.DataFrame([
        {"date": "2024-01-15", "source": "淘宝", "content": "好评"},
        {"date": "2024-01-16", "source": "京东", "content": "差评"},
    ])
    csv_bytes = df.to_csv(index=False).encode()
    result = await parse_csv(MockUploadFile(csv_bytes))
    assert len(result) == 2
    assert result[0]["source"] == "淘宝"


@pytest.mark.asyncio
async def test_parse_invalid_extension():
    """测试非 CSV 文件"""
    with pytest.raises(Exception):
        await parse_csv(MockUploadFile(b"data", filename="test.txt"))
