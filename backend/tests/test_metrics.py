"""指标 API 测试"""
from datetime import datetime, timedelta
from models import User, Order, UserProfile


def _setup_data(db):
    """创建测试数据：用户 + 订单 + 画像"""
    user = User(email="metrics@test.com", password_hash="hashed")
    db.add(user)
    db.flush()

    # 创建订单
    now = datetime.utcnow()
    orders = [
        Order(user_id=user.id, amount=100.0, product="A", status="completed",
              created_at=now - timedelta(days=1)),
        Order(user_id=user.id, amount=200.0, product="B", status="completed",
              created_at=now - timedelta(days=5)),
        Order(user_id=user.id, amount=50.0, product="C", status="refunded",
              created_at=now - timedelta(days=3)),
    ]
    db.add_all(orders)

    # 创建画像
    profile = UserProfile(
        user_id=user.id, total_spent=300.0, avg_order_value=150.0,
        purchase_frequency=2.0, last_active_days=1, rfm_score="533",
        user_level="High Value", churn_risk="low",
    )
    db.add(profile)
    db.commit()
    return user


def test_overview_with_data(client, auth_headers, db):
    """GET /api/metrics/overview 有数据时返回正确统计"""
    _setup_data(db)
    resp = client.get("/api/metrics/overview", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_users"] >= 1
    assert data["total_orders"] == 2  # 只算 completed
    assert data["total_revenue"] == 300.0
    assert data["avg_order_value"] == 150.0
    assert data["active_users_30d"] >= 1


def test_overview_empty_db(client, auth_headers):
    """空数据库时 overview 返回零值"""
    resp = client.get("/api/metrics/overview", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_users"] == 1  # auth_headers 创建了一个用户
    assert data["total_orders"] == 0
    assert data["total_revenue"] == 0.0


def test_retention_with_data(client, auth_headers, db):
    """GET /api/metrics/retention 返回月度留存数据"""
    _setup_data(db)
    resp = client.get("/api/metrics/retention", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # 每条记录包含必要字段
    for item in data:
        assert "month" in item
        assert "retention_rate" in item
        assert "active_users" in item
        assert "total_users" in item


def test_revenue_daily(client, auth_headers, db):
    """GET /api/metrics/revenue?period=daily 返回日营收"""
    _setup_data(db)
    resp = client.get("/api/metrics/revenue?period=daily", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    # 有数据的天应有记录
    for item in data:
        assert "period" in item
        assert "revenue" in item
        assert "order_count" in item


def test_revenue_monthly(client, auth_headers, db):
    """GET /api/metrics/revenue?period=monthly 返回月营收"""
    _setup_data(db)
    resp = client.get("/api/metrics/revenue?period=monthly", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


def test_revenue_weekly(client, auth_headers, db):
    """GET /api/metrics/revenue?period=weekly 返回周营收"""
    _setup_data(db)
    resp = client.get("/api/metrics/revenue?period=weekly", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


def test_conversion_by_user_level(client, auth_headers, db):
    """GET /api/metrics/conversion 按用户等级分组"""
    _setup_data(db)
    resp = client.get("/api/metrics/conversion", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3  # High/Medium/Low Value
    levels = {item["user_level"] for item in data}
    assert levels == {"High Value", "Medium Value", "Low Value"}
    # High Value 有数据
    high = next(item for item in data if item["user_level"] == "High Value")
    assert high["order_count"] == 2
    assert high["user_count"] == 1


def test_metrics_unauthorized(client):
    """未认证访问指标 API 返回 403"""
    for endpoint in ["/api/metrics/overview", "/api/metrics/retention",
                     "/api/metrics/revenue", "/api/metrics/conversion"]:
        resp = client.get(endpoint)
        assert resp.status_code == 403
