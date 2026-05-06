"""RFM 用户分层逻辑测试"""
from datetime import datetime, timedelta
from services.rfm import calculate_rfm_score, classify_user_level, classify_churn_risk
from models import User, Order


def _create_user(db, email="rfm@test.com"):
    user = User(email=email, password_hash="hashed")
    db.add(user)
    db.flush()
    return user


def _create_order(db, user_id, amount=100.0, days_ago=0, status="completed"):
    order = Order(
        user_id=user_id,
        amount=amount,
        product="测试商品",
        status=status,
        created_at=datetime.utcnow() - timedelta(days=days_ago),
    )
    db.add(order)
    db.flush()
    return order


# --- calculate_rfm_score ---

def test_rfm_no_orders(db):
    """无订单用户返回最低分 111"""
    user = _create_user(db)
    result = calculate_rfm_score(user.id, db)
    assert result["rfm_score"] == "111"
    assert result["recency_days"] == 999
    assert result["frequency"] == 0.0
    assert result["monetary"] == 0.0


def test_rfm_single_order(db):
    """单笔订单的 RFM 计算"""
    user = _create_user(db)
    _create_order(db, user.id, amount=500.0, days_ago=5)
    result = calculate_rfm_score(user.id, db)
    # Recency 5天 → 5分, Frequency 1单/月 → 3分, Monetary 500 → 2分
    assert result["rfm_score"] == "532"
    assert result["recency_days"] == 5
    assert result["monetary"] == 500.0


def test_rfm_many_orders(db):
    """多笔高频高消费订单"""
    user = _create_user(db)
    # 最近7天内多笔订单，总消费15000+
    for i in range(20):
        _create_order(db, user.id, amount=1000.0, days_ago=i)
    result = calculate_rfm_score(user.id, db)
    assert result["rfm_score"][0] == "5"  # Recency 最近有订单
    assert result["monetary"] == 20000.0
    # Frequency: 20 orders / ~1 month = high
    assert result["frequency"] > 4


def test_rfm_score_range_111_to_555(db):
    """验证评分范围在 111-555 之间"""
    user = _create_user(db)
    _create_order(db, user.id, amount=1.0, days_ago=365)
    result = calculate_rfm_score(user.id, db)
    score = result["rfm_score"]
    assert len(score) == 3
    assert all(c in "12345" for c in score)


def test_rfm_recent_high_value(db):
    """最近活跃 + 高消费 → 高分"""
    user = _create_user(db)
    for i in range(10):
        _create_order(db, user.id, amount=2000.0, days_ago=i)
    result = calculate_rfm_score(user.id, db)
    # R=5 (最近), F>=4 (高频), M=5 (>=10000)
    assert result["rfm_score"] == "555"


def test_rfm_old_low_value(db):
    """很久前的少量低消费订单 → 低分"""
    user = _create_user(db)
    _create_order(db, user.id, amount=50.0, days_ago=200)
    result = calculate_rfm_score(user.id, db)
    # R=1 (>60天), F=1 (频率低), M=1 (<500)
    assert result["rfm_score"] == "111"


def test_rfm_only_completed_orders_counted(db):
    """只计算 completed 状态的订单"""
    user = _create_user(db)
    _create_order(db, user.id, amount=5000.0, days_ago=1, status="completed")
    _create_order(db, user.id, amount=5000.0, days_ago=2, status="refunded")
    result = calculate_rfm_score(user.id, db)
    assert result["monetary"] == 5000.0  # 只算 completed


def test_rfm_multiple_users_independent(db):
    """不同用户的 RFM 独立计算"""
    user1 = _create_user(db, "u1@test.com")
    user2 = _create_user(db, "u2@test.com")
    _create_order(db, user1.id, amount=10000.0, days_ago=1)
    _create_order(db, user2.id, amount=100.0, days_ago=90)

    rfm1 = calculate_rfm_score(user1.id, db)
    rfm2 = calculate_rfm_score(user2.id, db)
    assert rfm1["rfm_score"] > rfm2["rfm_score"]


# --- classify_user_level ---

def test_classify_high_value():
    assert classify_user_level("555") == "High Value"
    assert classify_user_level("544") == "High Value"
    assert classify_user_level("444") == "High Value"


def test_classify_medium_value():
    assert classify_user_level("333") == "Medium Value"
    assert classify_user_level("332") == "Medium Value"
    assert classify_user_level("253") == "Medium Value"


def test_classify_low_value():
    assert classify_user_level("111") == "Low Value"
    assert classify_user_level("222") == "Low Value"
    assert classify_user_level("123") == "Low Value"


# --- classify_churn_risk ---

def test_churn_risk_high():
    assert classify_churn_risk(recency_days=100, frequency=0.1) == "high"
    assert classify_churn_risk(recency_days=91, frequency=5.0) == "high"
    assert classify_churn_risk(recency_days=10, frequency=0.1) == "high"


def test_churn_risk_medium():
    assert classify_churn_risk(recency_days=45, frequency=5.0) == "medium"
    assert classify_churn_risk(recency_days=10, frequency=0.5) == "medium"


def test_churn_risk_low():
    assert classify_churn_risk(recency_days=5, frequency=3.0) == "low"
    assert classify_churn_risk(recency_days=1, frequency=10.0) == "low"
