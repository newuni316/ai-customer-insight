"""安全测试"""
import io
import pandas as pd
from concurrent.futures import ThreadPoolExecutor


def test_all_endpoints_require_auth(client):
    """所有受保护端点必须返回 401/403"""
    protected = [
        ("GET", "/api/dashboard"),
        ("GET", "/api/feedbacks"),
        ("POST", "/api/analyze"),
        ("GET", "/api/auth/me"),
    ]
    for method, path in protected:
        resp = getattr(client, method.lower())(path)
        assert resp.status_code in (401, 403), f"{method} {path} 应返回 401/403，实际: {resp.status_code}"


def test_sql_injection_resistance(client, auth_headers):
    """SQL 注入测试"""
    malicious_content = "'; DROP TABLE users; --"
    csv_data = pd.DataFrame([
        {"date": "2024-01-15", "source": "test", "content": malicious_content},
    ]).to_csv(index=False).encode()

    resp = client.post("/api/feedback/upload-csv", headers=auth_headers,
                       files={"file": ("test.csv", csv_data, "text/csv")})
    assert resp.status_code == 200

    # 验证数据存在且表未被破坏
    resp = client.get("/api/feedbacks", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


def test_large_csv_upload(client, auth_headers):
    """大文件上传测试（5MB CSV）"""
    rows = [{"date": f"2024-01-{i % 28 + 1:02d}", "source": "test", "content": f"反馈内容{i} " * 50}
            for i in range(5000)]
    csv_data = pd.DataFrame(rows).to_csv(index=False).encode()
    assert len(csv_data) > 1_000_000  # > 1MB

    resp = client.post("/api/feedback/upload-csv", headers=auth_headers,
                       files={"file": ("large.csv", csv_data, "text/csv")})
    assert resp.status_code == 200
    assert resp.json()["count"] == 5000


def test_concurrent_requests(client, auth_headers):
    """并发请求测试（串行模拟，SQLite 不支持真正并发）"""
    results = []
    for _ in range(20):
        results.append(client.get("/api/dashboard", headers=auth_headers))

    success = sum(1 for r in results if r.status_code == 200)
    assert success >= 15, f"并发成功率过低: {success}/20"
