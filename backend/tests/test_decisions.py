"""决策 API 测试"""
from datetime import datetime
from unittest.mock import patch
from models import User, Order, UserProfile, Decision


def _setup_user_with_profile(db, email="decision@test.com"):
    """创建用户 + 画像 + 订单"""
    user = User(email=email, password_hash="hashed")
    db.add(user)
    db.flush()

    profile = UserProfile(
        user_id=user.id, total_spent=2000.0, avg_order_value=200.0,
        purchase_frequency=5.0, last_active_days=3, rfm_score="544",
        user_level="High Value", churn_risk="low",
    )
    db.add(profile)

    order = Order(user_id=user.id, amount=200.0, product="测试", status="completed")
    db.add(order)
    db.commit()
    return user


def _create_decision(db, user_id, user_type="champion", churn_risk="low", rule_based=0):
    """创建决策记录"""
    decision = Decision(
        user_id=user_id, user_type=user_type, churn_risk=churn_risk,
        recommended_action="VIP服务", reasoning="测试", rule_based=rule_based,
    )
    db.add(decision)
    db.flush()
    return decision


@patch.dict("os.environ", {"USE_LOCAL_MODEL": "true"})
def test_generate_decision_single_user(client, auth_headers, db):
    """POST /api/decisions/generate 指定用户"""
    user = _setup_user_with_profile(db)
    resp = client.post("/api/decisions/generate", headers=auth_headers, json={
        "user_id": user.id,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == user.id
    assert "user_type" in data
    assert "churn_risk" in data


@patch.dict("os.environ", {"USE_LOCAL_MODEL": "true"})
def test_generate_decision_all_users(client, auth_headers, db):
    """POST /api/decisions/generate 全部用户"""
    _setup_user_with_profile(db, "u1@test.com")
    _setup_user_with_profile(db, "u2@test.com")
    resp = client.post("/api/decisions/generate", headers=auth_headers, json={})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 2


def test_generate_decision_user_not_found(client, auth_headers, db):
    """用户画像不存在时返回错误"""
    user = User(email="noprofile@test.com", password_hash="hashed")
    db.add(user)
    db.commit()

    with patch.dict("os.environ", {"USE_LOCAL_MODEL": "true"}):
        resp = client.post("/api/decisions/generate", headers=auth_headers, json={
            "user_id": user.id,
        })
    assert resp.status_code == 400


def test_get_decision_insights_empty(client, auth_headers):
    """GET /api/decisions/insights 无决策时返回空"""
    resp = client.get("/api/decisions/insights", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_users"] == 0
    assert data["user_type_distribution"] == {}


def test_get_decision_insights_with_data(client, auth_headers, db):
    """GET /api/decisions/insights 有数据时返回聚合统计"""
    user = _setup_user_with_profile(db)
    _create_decision(db, user.id, user_type="champion", churn_risk="low", rule_based=0)

    resp = client.get("/api/decisions/insights", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_users"] == 1
    assert data["user_type_distribution"]["champion"] == 1
    assert data["churn_risk_distribution"]["low"] == 1
    assert data["ai_decisions_count"] == 1
    assert data["rule_fallback_count"] == 0


def test_get_decision_insights_high_churn(client, auth_headers, db):
    """高流失用户统计"""
    user = _setup_user_with_profile(db)
    _create_decision(db, user.id, user_type="at_risk", churn_risk="high")

    resp = client.get("/api/decisions/insights", headers=auth_headers)
    data = resp.json()
    assert data["high_churn_count"] == 1
    assert data["high_churn_pct"] == 100.0


def test_get_user_decision(client, auth_headers, db):
    """GET /api/decisions/{user_id} 获取用户最新决策"""
    user = _setup_user_with_profile(db)
    _create_decision(db, user.id, user_type="loyal")

    resp = client.get(f"/api/decisions/{user.id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == user.id
    assert data["user_type"] == "loyal"


def test_get_user_decision_not_found(client, auth_headers):
    """用户无决策时返回 404"""
    resp = client.get("/api/decisions/99999", headers=auth_headers)
    assert resp.status_code == 404


def test_decisions_unauthorized(client):
    """未认证访问决策 API 返回 403"""
    resp = client.get("/api/decisions/insights")
    assert resp.status_code == 403
