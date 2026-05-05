"""订单 API 测试"""
from datetime import datetime, timedelta
from models import User, Order, UserProfile


def test_create_order(client, auth_headers, db):
    """POST /api/orders 创建订单并自动更新用户画像"""
    resp = client.post("/api/orders", headers=auth_headers, json={
        "amount": 299.99,
        "product": "测试商品",
        "status": "completed",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["amount"] == 299.99
    assert data["product"] == "测试商品"
    assert data["status"] == "completed"
    assert "id" in data

    # 验证用户画像被自动更新
    profile = db.query(UserProfile).filter(UserProfile.user_id == data["user_id"]).first()
    assert profile is not None
    assert profile.total_spent == 299.99


def test_create_order_updates_profile(client, auth_headers, db):
    """多笔订单累积更新画像"""
    client.post("/api/orders", headers=auth_headers, json={"amount": 100.0, "product": "A"})
    client.post("/api/orders", headers=auth_headers, json={"amount": 200.0, "product": "B"})

    # 查询画像
    user = db.query(User).filter(User.email == "test@example.com").first()
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    assert profile.total_spent == 300.0


def test_list_orders(client, auth_headers, db):
    """GET /api/orders 返回当前用户的订单列表"""
    # 创建订单
    client.post("/api/orders", headers=auth_headers, json={"amount": 100.0, "product": "A"})
    client.post("/api/orders", headers=auth_headers, json={"amount": 200.0, "product": "B"})

    resp = client.get("/api/orders", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


def test_list_orders_filter_by_status(client, auth_headers, db):
    """按状态过滤订单"""
    client.post("/api/orders", headers=auth_headers, json={"amount": 100.0, "status": "completed"})
    client.post("/api/orders", headers=auth_headers, json={"amount": 200.0, "status": "refunded"})

    resp = client.get("/api/orders?status=completed", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["status"] == "completed"


def test_list_orders_pagination(client, auth_headers, db):
    """分页查询"""
    for i in range(5):
        client.post("/api/orders", headers=auth_headers, json={"amount": float(i * 10), "product": f"P{i}"})

    resp = client.get("/api/orders?page=1&page_size=2", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2

    resp2 = client.get("/api/orders?page=2&page_size=2", headers=auth_headers)
    data2 = resp2.json()
    assert len(data2) == 2


def test_get_order_detail(client, auth_headers, db):
    """GET /api/orders/{id} 查询单个订单"""
    create_resp = client.post("/api/orders", headers=auth_headers, json={
        "amount": 99.99, "product": "详情测试",
    })
    order_id = create_resp.json()["id"]

    resp = client.get(f"/api/orders/{order_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["amount"] == 99.99
    assert resp.json()["product"] == "详情测试"


def test_get_order_not_found(client, auth_headers):
    """查询不存在的订单返回 404"""
    resp = client.get("/api/orders/99999", headers=auth_headers)
    assert resp.status_code == 404


def test_orders_unauthorized(client):
    """未认证访问订单 API 返回 403"""
    resp = client.get("/api/orders")
    assert resp.status_code == 403

    resp = client.post("/api/orders", json={"amount": 100.0})
    assert resp.status_code == 403
