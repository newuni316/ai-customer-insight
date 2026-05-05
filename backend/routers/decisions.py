"""AI 决策路由 - 用户分层与运营建议（使用统一任务队列）"""
import logging
from collections import Counter
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db, engine
from models import User, UserProfile, Decision
from schemas import (
    DecisionResponse, DecisionInsight, GenerateDecisionRequest, PaginatedResponse,
)
from auth import get_current_user
from services.ai_analyzer import analyze_user_decisions
from services.task_queue import task_queue

router = APIRouter(prefix="/api/decisions", tags=["AI 决策"])
logger = logging.getLogger(__name__)


def _run_decision_task(task_id: str, user_id: int | None):
    """后台决策生成任务（在线程池中执行）"""
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        if user_id:
            users = db.query(User).filter(User.id == user_id).all()
        else:
            users = db.query(User).all()

        task_queue.update_task(task_id, total=len(users))
        success = fail = 0

        for user in users:
            try:
                result = analyze_user_decisions(user.id, db)
                if result.get("error"):
                    fail += 1
                else:
                    success += 1
            except Exception as e:
                logger.error(f"决策生成失败 user_id={user.id}: {e}")
                fail += 1

            task_queue.update_task(task_id, processed=success + fail, success=success, fail=fail)

        task_queue.update_task(task_id, status="done")
    except Exception as e:
        logger.exception(f"决策任务失败 task_id={task_id}")
        task_queue.update_task(task_id, status="error", error="决策任务执行失败")
        db.rollback()
    finally:
        db.close()


@router.post("/generate")
def generate_decisions(
    request: GenerateDecisionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """同步生成决策 - 指定用户或全部用户"""
    if request.user_id:
        result = analyze_user_decisions(request.user_id, db)
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"])
        return result

    # 全部用户
    users = db.query(User).all()
    results = []
    for user in users:
        try:
            result = analyze_user_decisions(user.id, db)
            results.append(result)
        except Exception as e:
            logger.error(f"决策生成失败 user_id={user.id}: {e}")
            results.append({"user_id": user.id, "error": str(e)})

    return {
        "message": f"决策生成完成",
        "total": len(users),
        "results": results,
    }


@router.post("/generate/async")
def generate_decisions_async(
    request: GenerateDecisionRequest,
    current_user: User = Depends(get_current_user),
):
    """异步生成决策 - 立即返回 task_id"""
    task_id = task_queue.submit_task("decision", _run_decision_task, request.user_id)
    return {"task_id": task_id, "status": "running"}


@router.get("/generate/status/{task_id}")
def get_decision_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
):
    """查询异步决策任务进度（需要认证）"""
    task = task_queue.get_task_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    safe_task = {k: v for k, v in task.items() if k != "error"}
    if task.get("error"):
        safe_task["error"] = "任务执行失败"
    return safe_task


@router.get("/insights", response_model=DecisionInsight)
def get_decision_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """聚合洞察 - 用户分层统计和运营建议汇总"""
    # 获取每个用户最新的决策（去重）
    latest_subq = (
        db.query(
            Decision.user_id,
            func.max(Decision.id).label("max_id"),
        )
        .group_by(Decision.user_id)
        .subquery()
    )
    latest_decisions = (
        db.query(Decision)
        .join(latest_subq, Decision.id == latest_subq.c.max_id)
        .all()
    )

    total = len(latest_decisions)
    if total == 0:
        return DecisionInsight(
            total_users=0,
            user_type_distribution={},
            churn_risk_distribution={},
            high_churn_count=0,
            high_churn_pct=0.0,
            top_recommendations=[],
            ai_decisions_count=0,
            rule_fallback_count=0,
        )

    # 统计分布
    type_counter = Counter(d.user_type for d in latest_decisions)
    churn_counter = Counter(d.churn_risk for d in latest_decisions)
    action_counter = Counter(d.recommended_action for d in latest_decisions if d.recommended_action)

    high_churn = churn_counter.get("high", 0)
    ai_count = sum(1 for d in latest_decisions if not d.rule_based)
    rule_count = sum(1 for d in latest_decisions if d.rule_based)

    top_actions = [
        {"action": action, "count": count}
        for action, count in action_counter.most_common(5)
    ]

    return DecisionInsight(
        total_users=total,
        user_type_distribution=dict(type_counter),
        churn_risk_distribution=dict(churn_counter),
        high_churn_count=high_churn,
        high_churn_pct=round(high_churn / total * 100, 1) if total else 0.0,
        top_recommendations=top_actions,
        ai_decisions_count=ai_count,
        rule_fallback_count=rule_count,
    )


@router.get("/{user_id}", response_model=DecisionResponse)
def get_user_decision(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取指定用户的最新决策"""
    decision = (
        db.query(Decision)
        .filter(Decision.user_id == user_id)
        .order_by(Decision.created_at.desc())
        .first()
    )
    if not decision:
        raise HTTPException(status_code=404, detail="该用户暂无决策记录")
    return decision


@router.get("/", response_model=PaginatedResponse)
def list_decisions(
    user_type: str | None = Query(None, description="按用户类型过滤"),
    churn_risk: str | None = Query(None, description="按流失风险过滤"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """列出决策记录，支持过滤和分页"""
    query = db.query(Decision)

    if user_type:
        query = query.filter(Decision.user_type == user_type)
    if churn_risk:
        query = query.filter(Decision.churn_risk == churn_risk)

    total = query.count()
    items = (
        query.order_by(Decision.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # 转换 rule_based 字段为 bool
    response_items = []
    for item in items:
        d = DecisionResponse(
            id=item.id,
            user_id=item.user_id,
            user_type=item.user_type or "unknown",
            churn_risk=item.churn_risk or "unknown",
            recommended_action=item.recommended_action or "",
            reasoning=item.reasoning,
            rule_based=bool(item.rule_based),
            created_at=item.created_at,
        )
        response_items.append(d)

    return PaginatedResponse(items=response_items, total=total, page=page, page_size=page_size)
