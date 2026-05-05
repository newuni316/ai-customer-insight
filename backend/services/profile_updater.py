"""用户画像更新服务"""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import User, Order, UserProfile
from services.rfm import calculate_rfm_score, classify_user_level, classify_churn_risk


def update_user_profile(user_id: int, db: Session) -> UserProfile:
    """重新计算并更新单个用户的画像数据"""
    rfm = calculate_rfm_score(user_id, db)
    user_level = classify_user_level(rfm["rfm_score"])
    churn_risk = classify_churn_risk(rfm["recency_days"], rfm["frequency"])

    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)

    profile.total_spent = rfm["monetary"]
    profile.avg_order_value = (
        rfm["monetary"] / max(db.query(Order).filter(
            Order.user_id == user_id, Order.status == "completed"
        ).count(), 1)
    )
    profile.purchase_frequency = rfm["frequency"]
    profile.last_active_days = rfm["recency_days"]
    profile.rfm_score = rfm["rfm_score"]
    profile.user_level = user_level
    profile.churn_risk = churn_risk
    profile.updated_at = datetime.utcnow()

    db.flush()
    return profile


def update_all_profiles(db: Session) -> int:
    """批量更新所有用户的画像，返回更新数量"""
    users = db.query(User).all()
    count = 0
    for user in users:
        update_user_profile(user.id, db)
        count += 1
    db.commit()
    return count
