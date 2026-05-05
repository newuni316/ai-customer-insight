"""CSV 文件解析服务"""
import io
from datetime import datetime
from typing import Any
import pandas as pd
from fastapi import UploadFile, HTTPException


async def parse_csv(file: UploadFile) -> list[dict[str, Any]]:
    """解析上传的 CSV 文件，返回反馈数据列表"""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="请上传 CSV 文件")

    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CSV 解析失败: {str(e)}")

    # 验证必需列
    required_cols = {"date", "source", "content"}
    if not required_cols.issubset(set(df.columns)):
        missing = required_cols - set(df.columns)
        raise HTTPException(status_code=400, detail=f"缺少必需列: {missing}")

    results = []
    for _, row in df.iterrows():
        try:
            date_val = pd.to_datetime(row["date"])
            results.append({
                "source": str(row["source"]),
                "content": str(row["content"]),
                "date": date_val.to_pydatetime(),
            })
        except Exception:
            continue  # 跳过无效行

    if not results:
        raise HTTPException(status_code=400, detail="CSV 中没有有效数据行")

    return results
