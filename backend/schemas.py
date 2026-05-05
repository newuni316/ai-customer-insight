"""Pydantic 数据模型"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


# === 用户 ===
class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# === 反馈 ===
class FeedbackCreate(BaseModel):
    source: str
    content: str
    date: datetime

class AnalyticsResponse(BaseModel):
    id: int
    sentiment: str
    topics: list[str]
    confidence: float
    analyzed_at: datetime
    class Config:
        from_attributes = True

class FeedbackResponse(BaseModel):
    id: int
    source: str
    content: str
    date: datetime
    created_at: datetime
    analytics: Optional[AnalyticsResponse] = None
    class Config:
        from_attributes = True


# === 仪表盘 ===
class SentimentDist(BaseModel):
    positive: int = 0
    neutral: int = 0
    negative: int = 0

class TopTopic(BaseModel):
    topic: str
    count: int

class DailyTrend(BaseModel):
    date: str
    positive: int = 0
    neutral: int = 0
    negative: int = 0

class DashboardStats(BaseModel):
    total_feedbacks: int
    analyzed_count: int
    sentiment_distribution: SentimentDist
    top_topics: list[TopTopic]
    daily_trends: list[DailyTrend]

class PaginatedResponse(BaseModel):
    items: list[FeedbackResponse]
    total: int
    page: int
    page_size: int
