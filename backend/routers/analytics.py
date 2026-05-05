"""AI 分析和仪表盘路由 - 增强版"""
import uuid
import logging
from collections import Counter, defaultdict
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import User, Feedback, Analytics
from schemas import DashboardStats, SentimentDist, TopTopic, DailyTrend, AnalyticsResponse
from auth import get_current_user
from services.ai_analyzer import analyze_feedback

router = APIRouter(prefix="/api", tags=["AI 分析"])
logger = logging.getLogger(__name__)

# 异步任务状态存储
_tasks: dict[str, dict] = {}


def _run_analysis_task(task_id: str, user_id: int, db_url: str):
    """后台分析任务"""
    from database import engine
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        analyzed_ids = db.query(Analytics.feedback_id).scalar_subquery()
        unanalyzed = db.query(Feedback).filter(
            Feedback.user_id == user_id, ~Feedback.id.in_(analyzed_ids)
        ).all()

        _tasks[task_id]["total"] = len(unanalyzed)
        success = fail = 0
        failures = []

        for fb in unanalyzed:
            try:
                result = analyze_feedback(fb.content)
                if result.get("error"):
                    fail += 1
                    failures.append({"id": fb.id, "error": result["error"]})
                else:
                    analytics = Analytics(
                        feedback_id=fb.id,
                        sentiment=result["sentiment"],
                        topics=result["topics"],
                        confidence=result["confidence"],
                    )
                    db.add(analytics)
                    success += 1
            except Exception as e:
                fail += 1
                failures.append({"id": fb.id, "error": str(e)})

            _tasks[task_id]["processed"] = success + fail
            _tasks[task_id]["success"] = success
            _tasks[task_id]["fail"] = fail

        db.commit()
        _tasks[task_id]["status"] = "done"
        _tasks[task_id]["failures"] = failures
    except Exception as e:
        _tasks[task_id]["status"] = "error"
        _tasks[task_id]["error"] = str(e)
        db.rollback()
    finally:
        db.close()


@router.post("/analyze")
def run_analysis(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """同步分析（保留向后兼容，但移除 50 条限制）"""
    analyzed_ids = db.query(Analytics.feedback_id).scalar_subquery()
    unanalyzed = db.query(Feedback).filter(
        Feedback.user_id == current_user.id, ~Feedback.id.in_(analyzed_ids)
    ).all()

    if not unanalyzed:
        return {"message": "没有待分析的反馈", "analyzed": 0, "failures": []}

    success = fail = 0
    failures = []
    for fb in unanalyzed:
        result = analyze_feedback(fb.content)
        if result.get("error"):
            fail += 1
            failures.append({"id": fb.id, "error": result["error"]})
        else:
            analytics = Analytics(
                feedback_id=fb.id,
                sentiment=result["sentiment"],
                topics=result["topics"],
                confidence=result["confidence"],
            )
            db.add(analytics)
            success += 1

    db.commit()
    return {"message": f"分析完成", "analyzed": success, "failed": fail, "failures": failures}


@router.post("/analyze/async")
def run_analysis_async(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """异步分析 - 立即返回 task_id"""
    from config import get_settings
    task_id = str(uuid.uuid4())[:8]
    _tasks[task_id] = {"status": "running", "total": 0, "processed": 0, "success": 0, "fail": 0}

    from fastapi.concurrency import run_in_threadpool
    import threading
    thread = threading.Thread(
        target=_run_analysis_task,
        args=(task_id, current_user.id, get_settings().DATABASE_URL),
        daemon=True,
    )
    thread.start()
    return {"task_id": task_id, "status": "running"}


@router.get("/analyze/status/{task_id}")
def get_analysis_status(task_id: str):
    """查询异步分析进度"""
    if task_id not in _tasks:
        return {"error": "任务不存在"}, 404
    return _tasks[task_id]


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """仪表盘统计"""
    total = db.query(Feedback).filter(Feedback.user_id == current_user.id).count()

    sentiment_counts = (
        db.query(Analytics.sentiment, func.count(Analytics.id))
        .join(Feedback).filter(Feedback.user_id == current_user.id)
        .group_by(Analytics.sentiment).all()
    )
    dist = {s: c for s, c in sentiment_counts}
    analyzed_total = sum(dist.values())

    all_analytics = (
        db.query(Analytics).join(Feedback)
        .filter(Feedback.user_id == current_user.id).all()
    )
    topic_counter: Counter = Counter()
    for a in all_analytics:
        if a.topics:
            topic_counter.update(a.topics)
    top_topics = [TopTopic(topic=t, count=c) for t, c in topic_counter.most_common(10)]

    trend_map: dict[str, dict] = defaultdict(lambda: {"positive": 0, "neutral": 0, "negative": 0})
    for a in all_analytics:
        day = a.analyzed_at.strftime("%Y-%m-%d") if a.analyzed_at else "unknown"
        if a.sentiment in trend_map[day]:
            trend_map[day][a.sentiment] += 1
    daily_trends = [DailyTrend(date=d, **v) for d, v in sorted(trend_map.items())]

    return DashboardStats(
        total_feedbacks=total,
        analyzed_count=analyzed_total,
        sentiment_distribution=SentimentDist(**dist),
        top_topics=top_topics,
        daily_trends=daily_trends[-30:],
    )


@router.get("/feedbacks/{feedback_id}/analytics", response_model=AnalyticsResponse)
def get_feedback_analytics(
    feedback_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    fb = db.query(Feedback).filter(Feedback.id == feedback_id, Feedback.user_id == current_user.id).first()
    if not fb:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="反馈不存在")
    if not fb.analytics:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="该反馈尚未分析")
    return fb.analytics
