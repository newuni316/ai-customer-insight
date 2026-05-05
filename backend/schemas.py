"""Pydantic 数据模型"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# === 用户 ===
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="密码至少 8 位")

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


# === 订单 ===
class OrderCreate(BaseModel):
    amount: float
    product: str = ""
    status: str = "completed"

class OrderResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    product: str
    status: str
    created_at: datetime
    class Config:
        from_attributes = True


# === 用户画像 ===
class UserProfileResponse(BaseModel):
    id: int
    user_id: int
    total_spent: float
    avg_order_value: float
    purchase_frequency: float
    last_active_days: int
    rfm_score: str
    user_level: str
    churn_risk: str
    updated_at: datetime
    class Config:
        from_attributes = True


# === 指标 ===
class MetricOverview(BaseModel):
    total_users: int
    total_orders: int
    total_revenue: float
    avg_order_value: float
    active_users_30d: int

class RetentionData(BaseModel):
    month: str
    retention_rate: float
    active_users: int
    total_users: int

class RevenueTrend(BaseModel):
    period: str
    revenue: float
    order_count: int

class ConversionData(BaseModel):
    user_level: str
    order_count: int
    user_count: int


# === 决策 ===
class DecisionResponse(BaseModel):
    id: int
    user_id: int
    user_type: str
    churn_risk: str
    recommended_action: str
    reasoning: Optional[str] = None
    rule_based: bool = False
    created_at: datetime
    class Config:
        from_attributes = True


class DecisionInsight(BaseModel):
    total_users: int
    user_type_distribution: dict[str, int]  # {"champion": 10, "loyal": 20, ...}
    churn_risk_distribution: dict[str, int]  # {"low": 30, "medium": 15, "high": 5}
    high_churn_count: int
    high_churn_pct: float
    top_recommendations: list[dict]  # [{"action": "...", "count": 5}, ...]
    ai_decisions_count: int
    rule_fallback_count: int


class GenerateDecisionRequest(BaseModel):
    user_id: Optional[int] = None  # None = all users
