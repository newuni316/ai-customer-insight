"""AI 分析和仪表盘路由"""
from collections import Counter, defaultdict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import User, Feedback, Analytics
from schemas import DashboardStats, SentimentDist, TopTopic, DailyTrend, AnalyticsResponse
from auth import get_current_user
from services.ai_analyzer import analyze_feedback

router = APIRouter(prefix="/api", tags=["AI 分析"])


@router.post("/analyze")
def run_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """对未分析的反馈执行 AI 分析"""
    # 找出未分析的反馈
    analyzed_ids = db.query(Analytics.feedback_id).scalar_subquery()
    unanalyzed = (
        db.query(Feedback)
        .filter(Feedback.user_id == current_user.id, ~Feedback.id.in_(analyzed_ids))
        .limit(50)
        .all()
    )

    if not unanalyzed:
        return {"message": "没有待分析的反馈", "analyzed": 0}

    success_count = 0
    for fb in unanalyzed:
        try:
            result = analyze_feedback(fb.content)
            analytics = Analytics(
                feedback_id=fb.id,
                sentiment=result["sentiment"],
                topics=result["topics"],
                confidence=result["confidence"],
            )
            db.add(analytics)
            success_count += 1
        except Exception:
            continue

    db.commit()
    return {"message": f"分析完成，成功处理 {success_count} 条", "analyzed": success_count}


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取仪表盘统计数据"""
    user_feedbacks = db.query(Feedback).filter(Feedback.user_id == current_user.id)
    total = user_feedbacks.count()

    # 情感分布
    sentiment_counts = (
        db.query(Analytics.sentiment, func.count(Analytics.id))
        .join(Feedback)
        .filter(Feedback.user_id == current_user.id)
        .group_by(Analytics.sentiment)
        .all()
    )
    dist = {s: c for s, c in sentiment_counts}
    analyzed_total = sum(dist.values())

    # Top 主题
    all_analytics = (
        db.query(Analytics)
        .join(Feedback)
        .filter(Feedback.user_id == current_user.id)
        .all()
    )
    topic_counter: Counter = Counter()
    for a in all_analytics:
        if a.topics:
            topic_counter.update(a.topics)
    top_topics = [TopTopic(topic=t, count=c) for t, c in topic_counter.most_common(10)]

    # 每日趋势（最近30天）
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
    """获取单条反馈的分析结果"""
    fb = db.query(Feedback).filter(Feedback.id == feedback_id, Feedback.user_id == current_user.id).first()
    if not fb:
        raise HTTPException(status_code=404, detail="反馈不存在")
    if not fb.analytics:
        raise HTTPException(status_code=404, detail="该反馈尚未分析")
    return fb.analytics
