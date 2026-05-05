"""数据源基类"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import AsyncIterator


@dataclass
class RawFeedback:
    """原始反馈数据"""
    source: str
    content: str
    date: datetime
    external_id: str | None = None
    metadata: dict | None = None


class DataSource(ABC):
    """数据源抽象基类 - 所有数据源实现此接口"""

    name: str = "base"

    @abstractmethod
    async def fetch(self, since: datetime | None = None) -> AsyncIterator[RawFeedback]:
        """拉取反馈数据，支持增量同步（since 参数）"""
        ...

    @abstractmethod
    async def test_connection(self) -> bool:
        """测试数据源连接是否正常"""
        ...
