"""认证模块测试"""


def test_register(client):
    """测试用户注册"""
    resp = client.post("/api/auth/register", json={
        "email": "new@example.com",
        "password": "pass1234",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate(client):
    """测试重复注册"""
    client.post("/api/auth/register", json={"email": "dup@example.com", "password": "pass1234"})
    resp = client.post("/api/auth/register", json={"email": "dup@example.com", "password": "pass1234"})
    assert resp.status_code == 400


def test_login_success(client):
    """测试登录成功"""
    client.post("/api/auth/register", json={"email": "login@example.com", "password": "pass1234"})
    resp = client.post("/api/auth/login", json={"email": "login@example.com", "password": "pass1234"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    """测试密码错误"""
    client.post("/api/auth/register", json={"email": "wrong@example.com", "password": "pass1234"})
    resp = client.post("/api/auth/login", json={"email": "wrong@example.com", "password": "wrong"})
    assert resp.status_code == 401


def test_login_nonexistent_user(client):
    """测试不存在的用户"""
    resp = client.post("/api/auth/login", json={"email": "none@example.com", "password": "pass1234"})
    assert resp.status_code == 401


def test_get_me(client, auth_headers):
    """测试获取当前用户信息"""
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"


def test_unauthorized(client):
    """测试未认证访问"""
    resp = client.get("/api/auth/me")
    assert resp.status_code == 403
