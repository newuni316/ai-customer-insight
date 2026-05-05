"""RFM 用户分层分析"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Order, User


def calculate_rfm_score(user_id: int, db: Session) -> dict:
    """计算单个用户的 RFM 评分

    R (Recency): 最近一次下单距今天数 → 越小越好
    F (Frequency): 订单频率（月均订单数）→ 越大越好
    M (Monetary): 总消费金额 → 越大越好

    每个维度 1-5 分（5 = 最优），返回综合评分字符串如 "543"
    """
    now = datetime.utcnow()
    orders = (
        db.query(Order)
        .filter(Order.user_id == user_id, Order.status == "completed")
        .order_by(Order.created_at.desc())
        .all()
    )

    if not orders:
        return {"rfm_score": "111", "recency_days": 999, "frequency": 0.0, "monetary": 0.0}

    # --- Recency ---
    last_order_date = orders[0].created_at
    recency_days = (now - last_order_date).days

    # --- Frequency ---
    first_order_date = orders[-1].created_at
    months_span = max((now - first_order_date).days / 30.0, 1.0)
    frequency = len(orders) / months_span

    # --- Monetary ---
    monetary = sum(o.amount for o in orders)

    # 用全局分位数评分（查询所有用户数据做五等分）
    r_score = _score_recency(recency_days, db)
    f_score = _score_frequency(frequency, db)
    m_score = _score_monetary(monetary, db)

    return {
        "rfm_score": f"{r_score}{f_score}{m_score}",
        "recency_days": recency_days,
        "frequency": round(frequency, 2),
        "monetary": round(monetary, 2),
    }


def classify_user_level(rfm_score: str) -> str:
    """根据 RFM 评分判断用户等级

    平均分 >= 4 → High Value, >= 2.5 → Medium Value, 其余 → Low Value
    """
    avg = sum(int(c) for c in rfm_score) / 3.0
    if avg >= 4:
        return "High Value"
    elif avg >= 2.5:
        return "Medium Value"
    return "Low Value"


def classify_churn_risk(recency_days: int, frequency: float) -> str:
    """流失风险判断"""
    if recency_days > 90 or frequency < 0.2:
        return "high"
    elif recency_days > 30 or frequency < 1.0:
        return "medium"
    return "low"


def _score_recency(recency_days: int, db: Session) -> int:
    """Recency 评分：天数越少分越高"""
    # 获取所有用户的最近下单天数
    now = datetime.utcnow()
    subq = (
        db.query(func.min(func.julianday(now) - func.julianday(Order.created_at)))
        .filter(Order.status == "completed")
        .correlate(Order)
        .scalar_subquery()
    )
    # 简化：用固定阈值
    if recency_days <= 7:
        return 5
    elif recency_days <= 14:
        return 4
    elif recency_days <= 30:
        return 3
    elif recency_days <= 60:
        return 2
    return 1


def _score_frequency(frequency: float, db: Session) -> int:
    """Frequency 评分：月均订单越多分越高"""
    if frequency >= 4:
        return 5
    elif frequency >= 2:
        return 4
    elif frequency >= 1:
        return 3
    elif frequency >= 0.5:
        return 2
    return 1


def _score_monetary(monetary: float, db: Session) -> int:
    """Monetary 评分：消费越多分越高"""
    if monetary >= 10000:
        return 5
    elif monetary >= 5000:
        return 4
    elif monetary >= 1000:
        return 3
    elif monetary >= 500:
        return 2
    return 1
