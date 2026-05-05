"""AI 分析模块测试"""
from unittest.mock import patch, MagicMock


def test_dashboard_empty(client, auth_headers):
    """测试空数据仪表盘"""
    resp = client.get("/api/dashboard", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_feedbacks"] == 0
    assert data["analyzed_count"] == 0


@patch("routers.analytics.analyze_feedback")
def test_run_analysis(mock_analyze, client, auth_headers):
    """测试 AI 分析流程"""
    mock_analyze.return_value = {
        "sentiment": "positive",
        "topics": ["物流", "服务"],
        "confidence": 0.95,
    }

    # 先上传数据
    import io
    import pandas as pd
    csv_data = pd.DataFrame([
        {"date": "2024-01-15", "source": "淘宝", "content": "物流很快！"},
    ]).to_csv(index=False).encode()
    client.post("/api/feedback/upload-csv", headers=auth_headers,
                files={"file": ("test.csv", csv_data, "text/csv")})

    # 运行分析
    resp = client.post("/api/analyze", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["analyzed"] == 1

    # 验证仪表盘数据更新
    dash = client.get("/api/dashboard", headers=auth_headers).json()
    assert dash["analyzed_count"] == 1
    assert dash["sentiment_distribution"]["positive"] == 1
    assert len(dash["top_topics"]) > 0


def test_analyze_no_feedbacks(client, auth_headers):
    """测试无反馈时运行分析"""
    resp = client.post("/api/analyze", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["analyzed"] == 0
