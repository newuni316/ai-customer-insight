"""通用 FastAPI 依赖项"""
from fastapi import Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
from models import User


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃用户（可扩展禁用用户检查）"""
    return current_user


class PaginationParams:
    """分页参数依赖"""
    def __init__(
        self,
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size
