"""核心指标 API"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from database import get_db
from models import User, Order, UserProfile
from schemas import MetricOverview, RetentionData, RevenueTrend, ConversionData
from auth import get_current_user

router = APIRouter(prefix="/api/metrics", tags=["指标分析"])


@router.get("/overview", response_model=MetricOverview)
def get_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """总览指标"""
    total_users = db.query(User).count()
    total_orders = db.query(Order).filter(Order.status == "completed").count()
    total_revenue = db.query(func.coalesce(func.sum(Order.amount), 0.0)).filter(
        Order.status == "completed"
    ).scalar()
    avg_order_value = total_revenue / max(total_orders, 1)

    # 30 天内活跃用户（有订单的）
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    active_users_30d = (
        db.query(func.count(func.distinct(Order.user_id)))
        .filter(Order.created_at >= thirty_days_ago)
        .scalar()
    )

    return MetricOverview(
        total_users=total_users,
        total_orders=total_orders,
        total_revenue=round(float(total_revenue), 2),
        avg_order_value=round(float(avg_order_value), 2),
        active_users_30d=active_users_30d,
    )


@router.get("/retention", response_model=list[RetentionData])
def get_retention(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """月度留存率：连续月份都有下单的用户比例"""
    # 获取最近 12 个月，每个月有订单的用户集合
    now = datetime.utcnow()
    monthly_users: dict[str, set] = {}

    for i in range(12):
        month_start = (now.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1)

        key = month_start.strftime("%Y-%m")
        user_ids = (
            db.query(func.distinct(Order.user_id))
            .filter(Order.created_at >= month_start, Order.created_at < month_end)
            .all()
        )
        monthly_users[key] = {uid for (uid,) in user_ids}

    total_users = db.query(User).count()
    results = []
    sorted_months = sorted(monthly_users.keys())

    for i, month in enumerate(sorted_months):
        current = monthly_users[month]
        # 留存率 = 本月活跃 & 上月也活跃 的用户 / 上月活跃用户
        if i > 0:
            prev_month = sorted_months[i - 1]
            prev = monthly_users[prev_month]
            if prev:
                retained = len(current & prev)
                rate = retained / len(prev)
            else:
                retained = 0
                rate = 0.0
        else:
            # 最早的月份，用占总用户比例
            rate = len(current) / max(total_users, 1)
            retained = len(current)

        results.append(RetentionData(
            month=month,
            retention_rate=round(rate, 4),
            active_users=len(current),
            total_users=total_users,
        ))

    return list(reversed(results))


@router.get("/revenue", response_model=list[RevenueTrend])
def get_revenue(
    period: str = Query("daily", regex="^(daily|weekly|monthly)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """营收趋势（按日/周/月）"""
    now = datetime.utcnow()

    if period == "daily":
        # 最近 30 天
        start = now - timedelta(days=30)
        rows = (
            db.query(
                func.date(Order.created_at).label("period"),
                func.sum(Order.amount).label("revenue"),
                func.count(Order.id).label("order_count"),
            )
            .filter(Order.status == "completed", Order.created_at >= start)
            .group_by(func.date(Order.created_at))
            .order_by(func.date(Order.created_at))
            .all()
        )
    elif period == "weekly":
        # 最近 12 周
        start = now - timedelta(weeks=12)
        rows = (
            db.query(
                func.strftime("%Y-W%W", Order.created_at).label("period"),
                func.sum(Order.amount).label("revenue"),
                func.count(Order.id).label("order_count"),
            )
            .filter(Order.status == "completed", Order.created_at >= start)
            .group_by(func.strftime("%Y-W%W", Order.created_at))
            .order_by(func.strftime("%Y-W%W", Order.created_at))
            .all()
        )
    else:  # monthly
        # 最近 12 个月
        rows = (
            db.query(
                func.strftime("%Y-%m", Order.created_at).label("period"),
                func.sum(Order.amount).label("revenue"),
                func.count(Order.id).label("order_count"),
            )
            .filter(Order.status == "completed")
            .group_by(func.strftime("%Y-%m", Order.created_at))
            .order_by(func.strftime("%Y-%m", Order.created_at))
            .all()
        )

    return [
        RevenueTrend(period=str(r.period), revenue=round(float(r.revenue), 2), order_count=r.order_count)
        for r in rows
    ]


@router.get("/conversion", response_model=list[ConversionData])
def get_conversion(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """转化分析：按用户等级统计订单数"""
    results = (
        db.query(
            UserProfile.user_level,
            func.count(Order.id).label("order_count"),
            func.count(func.distinct(UserProfile.user_id)).label("user_count"),
        )
        .join(Order, Order.user_id == UserProfile.user_id)
        .filter(Order.status == "completed")
        .group_by(UserProfile.user_level)
        .all()
    )

    # 确保三个等级都有数据
    level_map = {r.user_level: r for r in results}
    data = []
    for level in ["High Value", "Medium Value", "Low Value"]:
        if level in level_map:
            r = level_map[level]
            data.append(ConversionData(user_level=level, order_count=r.order_count, user_count=r.user_count))
        else:
            data.append(ConversionData(user_level=level, order_count=0, user_count=0))

    return data
