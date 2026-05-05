"""测试配置 - 共享 fixtures"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

# 测试数据库（SQLite 内存）
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    """每个测试前重建数据库"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    """测试客户端，注入测试数据库"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    """注册用户并返回认证 headers"""
    client.post("/api/auth/register", json={"email": "test@example.com", "password": "test123"})
    resp = client.post("/api/auth/login", json={"email": "test@example.com", "password": "test123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
