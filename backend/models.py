"""SQLAlchemy ORM 模型"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    feedbacks = relationship("Feedback", back_populates="user")
    orders = relationship("Order", back_populates="user")
    profile = relationship("UserProfile", back_populates="user", uselist=False)


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    source = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="feedbacks")
    analytics = relationship("Analytics", back_populates="feedback", uselist=False)


class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    feedback_id = Column(Integer, ForeignKey("feedbacks.id"), unique=True, nullable=False)
    sentiment = Column(String(20), nullable=False)  # positive / neutral / negative
    topics = Column(JSON, default=list)  # ["物流", "质量", ...]
    confidence = Column(Float, default=0.0)
    analyzed_at = Column(DateTime, default=datetime.utcnow)

    feedback = relationship("Feedback", back_populates="analytics")


class Order(Base):
    """订单模型"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    product = Column(String(255))
    status = Column(String(50), default="completed")  # completed/refunded/cancelled
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="orders")


class UserProfile(Base):
    """用户画像模型 - RFM 分析结果"""
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    total_spent = Column(Float, default=0.0)
    avg_order_value = Column(Float, default=0.0)
    purchase_frequency = Column(Float, default=0.0)  # 每月订单数
    last_active_days = Column(Integer, default=0)
    rfm_score = Column(String(3), default="111")  # 如 "555"
    user_level = Column(String(20), default="Low Value")  # High/Medium/Low Value
    churn_risk = Column(String(10), default="low")  # low/medium/high
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="profile")


class Decision(Base):
    """AI 决策结果模型"""
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_type = Column(String(50))  # champion/loyal/potential/at_risk/lost
    churn_risk = Column(String(10))  # low/medium/high
    recommended_action = Column(Text)
    reasoning = Column(Text)
    rule_based = Column(Integer, default=0)  # 1 if AI failed and used rule fallback
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="decisions")
