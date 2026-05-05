"""CSV 文件数据源"""
from datetime import datetime
from typing import AsyncIterator
import io
import pandas as pd
from .base import DataSource, RawFeedback


class CSVSource(DataSource):
    """从 CSV 文件导入反馈数据"""

    name = "csv"

    def __init__(self, file_content: bytes):
        self._content = file_content

    async def fetch(self, since: datetime | None = None) -> AsyncIterator[RawFeedback]:
        df = pd.read_csv(io.BytesIO(self._content))

        required = {"date", "source", "content"}
        if not required.issubset(set(df.columns)):
            raise ValueError(f"CSV 缺少必需列: {required - set(df.columns)}")

        for _, row in df.iterrows():
            date = pd.to_datetime(row["date"]).to_pydatetime()
            if since and date < since:
                continue
            yield RawFeedback(
                source=str(row["source"]),
                content=str(row["content"]),
                date=date,
            )

    async def test_connection(self) -> bool:
        try:
            pd.read_csv(io.BytesIO(self._content))
            return True
        except Exception:
            return False
