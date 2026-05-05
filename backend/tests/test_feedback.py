"""反馈数据模块测试"""
import io
import pandas as pd


def _make_csv(rows: list[dict]) -> bytes:
    """生成 CSV 文件内容"""
    df = pd.DataFrame(rows)
    return df.to_csv(index=False).encode()


def test_upload_csv(client, auth_headers):
    """测试 CSV 上传"""
    csv_data = _make_csv([
        {"date": "2024-01-15", "source": "淘宝", "content": "物流很快，满意"},
        {"date": "2024-01-16", "source": "京东", "content": "质量太差了"},
    ])
    resp = client.post(
        "/api/feedback/upload-csv",
        headers=auth_headers,
        files={"file": ("test.csv", csv_data, "text/csv")},
    )
    assert resp.status_code == 200
    assert resp.json()["count"] == 2


def test_upload_invalid_file(client, auth_headers):
    """测试上传非 CSV 文件"""
    resp = client.post(
        "/api/feedback/upload-csv",
        headers=auth_headers,
        files={"file": ("test.txt", b"not a csv", "text/plain")},
    )
    assert resp.status_code == 400


def test_upload_missing_columns(client, auth_headers):
    """测试 CSV 缺少必需列"""
    csv_data = b"name,value\nfoo,bar"
    resp = client.post(
        "/api/feedback/upload-csv",
        headers=auth_headers,
        files={"file": ("test.csv", csv_data, "text/csv")},
    )
    assert resp.status_code == 400


def test_list_feedbacks(client, auth_headers):
    """测试获取反馈列表"""
    # 先上传数据
    csv_data = _make_csv([
        {"date": "2024-01-15", "source": "淘宝", "content": "好评"},
        {"date": "2024-01-16", "source": "京东", "content": "差评"},
    ])
    client.post("/api/feedback/upload-csv", headers=auth_headers,
                files={"file": ("test.csv", csv_data, "text/csv")})

    # 查询
    resp = client.get("/api/feedbacks", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_list_feedbacks_pagination(client, auth_headers):
    """测试分页"""
    csv_data = _make_csv([
        {"date": f"2024-01-{i:02d}", "source": "test", "content": f"反馈{i}"}
        for i in range(1, 11)
    ])
    client.post("/api/feedback/upload-csv", headers=auth_headers,
                files={"file": ("test.csv", csv_data, "text/csv")})

    resp = client.get("/api/feedbacks?page=1&page_size=3", headers=auth_headers)
    data = resp.json()
    assert data["total"] == 10
    assert len(data["items"]) == 3
    assert data["page"] == 1
