"""反馈数据路由"""
from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.orm import Session
from database import get_db
from models import User, Feedback
from schemas import FeedbackResponse, PaginatedResponse
from auth import get_current_user
from services.csv_parser import parse_csv

router = APIRouter(prefix="/api", tags=["反馈数据"])


@router.post("/feedback/upload-csv")
async def upload_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """上传 CSV 文件导入反馈数据"""
    rows = await parse_csv(file)

    feedbacks = []
    for row in rows:
        fb = Feedback(
            user_id=current_user.id,
            source=row["source"],
            content=row["content"],
            date=row["date"],
        )
        db.add(fb)
        feedbacks.append(fb)

    db.commit()
    return {"message": f"成功导入 {len(feedbacks)} 条反馈", "count": len(feedbacks)}


@router.get("/feedbacks", response_model=PaginatedResponse)
def list_feedbacks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sentiment: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取反馈列表（分页 + 情感筛选）"""
    query = db.query(Feedback).filter(Feedback.user_id == current_user.id)

    if sentiment:
        from models import Analytics
        query = query.join(Analytics).filter(Analytics.sentiment == sentiment)

    total = query.count()
    items = query.order_by(Feedback.date.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)
