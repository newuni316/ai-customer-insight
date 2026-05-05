"""AI 分析服务 - 鲁棒性增强版"""
import json
import re
import logging
import os
from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """分析客户反馈，返回JSON:
{"sentiment":"positive/neutral/negative","topics":["主题"],"confidence":0.0-1.0}
主题示例：物流、质量、服务态度、价格、包装、售后、功能、体验
只返回JSON。"""


def _parse_ai_response(text: str) -> dict:
    """鲁棒的 JSON 解析 - 三级回退"""
    text = text.strip()

    # 1. 直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. 从代码块提取
    patterns = [
        r"```json\s*(.*?)\s*```",
        r"```\s*(.*?)\s*```",
        r'\{[^{}]*"sentiment"[^{}]*\}',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1) if match.lastindex else match.group())
            except (json.JSONDecodeError, IndexError):
                continue

    # 3. 正则兜底提取关键字段
    sentiment_match = re.search(r'"?sentiment"?\s*:\s*"?(\w+)"?', text)
    topics_match = re.search(r'"?topics"?\s*:\s*\[(.*?)\]', text)
    if sentiment_match:
        topics = []
        if topics_match:
            topics = [t.strip().strip('"').strip("'") for t in topics_match.group(1).split(",") if t.strip()]
        return {"sentiment": sentiment_match.group(1), "topics": topics, "confidence": 0.3}

    raise ValueError(f"无法解析 AI 响应: {text[:200]}")


def analyze_feedback(content: str, max_retries: int = 2) -> dict:
    """分析单条反馈 - 自动选择云端/本地，含重试"""
    use_local = os.getenv("USE_LOCAL_MODEL", "false").lower() == "true"
    if use_local:
        from services.local_model import get_local_analyzer
        return get_local_analyzer().analyze(content)

    from openai import OpenAI
    client = OpenAI(api_key=settings.AI_API_KEY, base_url=settings.AI_API_BASE_URL)

    last_error = None
    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": content},
                ],
                temperature=0.1,
                max_tokens=200,
            )
            result_text = response.choices[0].message.content.strip()
            result = _parse_ai_response(result_text)
            return {
                "sentiment": result.get("sentiment", "neutral"),
                "topics": result.get("topics", []),
                "confidence": float(result.get("confidence", 0.5)),
                "error": None,
            }
        except Exception as e:
            last_error = str(e)
            logger.warning(f"AI 分析失败 (尝试 {attempt + 1}/{max_retries + 1}): {last_error}")

    logger.error(f"AI 分析最终失败: {last_error}")
    return {"sentiment": "neutral", "topics": [], "confidence": 0.0, "error": last_error}


def batch_analyze(feedbacks: list[str]) -> list[dict]:
    """批量分析"""
    return [analyze_feedback(c) for c in feedbacks]


def analyze_user_decisions(user_id: int, db) -> dict:
    """为单个用户生成 AI 决策并保存到数据库

    Args:
        user_id: 用户 ID
        db: SQLAlchemy Session

    Returns:
        决策结果字典
    """
    from models import User, UserProfile, Order, Feedback, Analytics, Decision
    from services.decision_engine import generate_decision
    from sqlalchemy import func

    # 获取用户画像
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        return {"error": "用户画像不存在，请先运行 RFM 分析"}

    # 获取近期订单（最近 20 条）
    recent_orders = (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .limit(20)
        .all()
    )

    # 构建反馈摘要
    feedbacks = (
        db.query(Feedback, Analytics)
        .outerjoin(Analytics, Analytics.feedback_id == Feedback.id)
        .filter(Feedback.user_id == user_id)
        .order_by(Feedback.created_at.desc())
        .limit(50)
        .all()
    )

    # 统计情感分布和主题
    sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
    top_topics = []
    for fb, analytics in feedbacks:
        if analytics:
            sentiment_counts[analytics.sentiment] = sentiment_counts.get(analytics.sentiment, 0) + 1
            if analytics.topics:
                top_topics.extend(analytics.topics)

    from collections import Counter
    topic_counter = Counter(top_topics)
    common_topics = [t for t, _ in topic_counter.most_common(5)]

    feedback_summary = (
        f"共 {len(feedbacks)} 条反馈，"
        f"情感分布: 正面{sentiment_counts['positive']}中性{sentiment_counts['neutral']}负面{sentiment_counts['negative']}，"
        f"主要话题: {', '.join(common_topics) if common_topics else '无'}"
    )

    # 调用决策引擎
    decision = generate_decision(profile, recent_orders, feedback_summary)

    # 保存到数据库
    db_decision = Decision(
        user_id=user_id,
        user_type=decision.get("user_type", "potential"),
        churn_risk=decision.get("churn_risk", "medium"),
        recommended_action=decision.get("recommended_action", ""),
        reasoning=decision.get("reasoning", ""),
        rule_based=1 if decision.get("rule_based") else 0,
    )
    db.add(db_decision)
    db.commit()
    db.refresh(db_decision)

    return {
        "decision_id": db_decision.id,
        "user_id": user_id,
        **decision,
    }
