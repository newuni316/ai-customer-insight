"""边界情况测试"""
import io
import pandas as pd


def _make_csv(rows: list[dict]) -> bytes:
    return pd.DataFrame(rows).to_csv(index=False).encode()


def test_empty_csv(client, auth_headers):
    """空 CSV 上传"""
    csv_data = b"date,source,content"
    resp = client.post("/api/feedback/upload-csv", headers=auth_headers,
                       files={"file": ("empty.csv", csv_data, "text/csv")})
    assert resp.status_code == 400


def test_thousand_row_csv(client, auth_headers):
    """1000+ 行 CSV"""
    rows = [{"date": f"2024-01-{i % 28 + 1:02d}", "source": "test", "content": f"反馈{i}"}
            for i in range(1000)]
    csv_data = _make_csv(rows)
    resp = client.post("/api/feedback/upload-csv", headers=auth_headers,
                       files={"file": ("big.csv", csv_data, "text/csv")})
    assert resp.status_code == 200
    assert resp.json()["count"] == 1000


def test_very_long_content(client, auth_headers):
    """超长内容反馈"""
    long_content = "这是一条很长的反馈。" * 1000  # ~10000 字符
    csv_data = _make_csv([{"date": "2024-01-15", "source": "test", "content": long_content}])
    resp = client.post("/api/feedback/upload-csv", headers=auth_headers,
                       files={"file": ("long.csv", csv_data, "text/csv")})
    assert resp.status_code == 200


def test_dashboard_empty(client, auth_headers):
    """空数据仪表盘"""
    resp = client.get("/api/dashboard", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_feedbacks"] == 0
    assert data["analyzed_count"] == 0


def test_analyze_with_api_failure(client, auth_headers, monkeypatch):
    """AI API 故障时的分析行为"""
    from unittest.mock import patch
    # 上传数据
    csv_data = _make_csv([{"date": "2024-01-15", "source": "test", "content": "测试"}])
    client.post("/api/feedback/upload-csv", headers=auth_headers,
                files={"file": ("test.csv", csv_data, "text/csv")})

    # Mock AI 分析失败
    with patch("routers.analytics.analyze_feedback", side_effect=Exception("API 超时")):
        resp = client.post("/api/analyze", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["analyzed"] == 0
        assert data["failed"] >= 1
