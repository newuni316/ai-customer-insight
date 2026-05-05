"""AI 决策引擎 - 规则 + LLM 混合决策"""
import json
import re
import time
import logging
import os
from typing import Optional
from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# 决策所需的 JSON schema 定义
DECISION_SCHEMA = {
    "user_type": {"champion", "loyal", "potential", "at_risk", "lost"},
    "churn_risk": {"low", "medium", "high"},
    "recommended_action": str,
    "reasoning": str,
}

VALID_USER_TYPES = {"champion", "loyal", "potential", "at_risk", "lost"}
VALID_CHURN_RISKS = {"low", "medium", "high"}

DECISION_SYSTEM_PROMPT = """你是一位资深电商增长分析师。
根据用户画像、近期订单和反馈摘要，对该用户进行分类并给出可执行的运营建议。

必须返回严格 JSON 格式：
{"user_type":"champion|loyal|potential|at_risk|lost","churn_risk":"low|medium|high","recommended_action":"具体可执行的建议","reasoning":"简要分析理由"}

只返回JSON，不要添加任何其他文字。"""


def rule_based_classify(profile) -> dict:
    """规则预分类 - 在调用 LLM 之前应用业务规则

    Args:
        profile: UserProfile 对象或字典

    Returns:
        部分分类结果，AI 将进一步细化
    """
    # 兼容 ORM 对象和字典
    get = lambda attr, default=None: getattr(profile, attr, None) or (profile.get(attr, default) if isinstance(profile, dict) else default)

    last_active = get("last_active_days", 0) or 0
    total_spent = get("total_spent", 0.0) or 0.0
    frequency = get("purchase_frequency", 0.0) or 0.0
    rfm_score = get("rfm_score", "111") or "111"

    rules_fired = []
    user_type = "potential"  # 默认
    churn_risk = "low"
    recommendation = ""

    # 规则 1: 超过 30 天未活跃 → 流失风险高
    if last_active > 90:
        churn_risk = "high"
        user_type = "lost"
        rules_fired.append("inactive_90d")
        recommendation = "发送召回优惠券，设置 7 天后二次触达"
    elif last_active > 30:
        churn_risk = "high" if last_active > 60 else "medium"
        user_type = "at_risk"
        rules_fired.append("inactive_30d")
        recommendation = "推送个性化推荐 + 限时折扣"

    # 规则 2: 高消费 + 高频 → 高价值用户
    if total_spent > 1000 and frequency > 5:
        user_type = "champion"
        rules_fired.append("high_value")
        if not recommendation:
            recommendation = "提供 VIP 专属服务和提前购特权"

    # 规则 3: RFM 评分以 "5" 开头 → VIP
    if rfm_score.startswith("5"):
        if user_type not in ("champion",):
            user_type = "champion"
        rules_fired.append("rfm_vip")
        if not recommendation:
            recommendation = "升级为 VIP 会员，提供专属客服通道"

    # 规则 4: RFM 均分较高 → loyal
    if len(rfm_score) == 3 and rfm_score.isdigit():
        avg_score = sum(int(c) for c in rfm_score) / 3.0
        if avg_score >= 3.5 and user_type == "potential":
            user_type = "loyal"
            rules_fired.append("rfm_above_avg")
            recommendation = "推荐关联商品，提升客单价"

    return {
        "user_type": user_type,
        "churn_risk": churn_risk,
        "recommended_action": recommendation or "持续观察用户行为",
        "reasoning": f"规则引擎命中: {', '.join(rules_fired) if rules_fired else '无特定规则'}",
        "rules_fired": rules_fired,
    }


def _parse_decision_response(text: str) -> dict:
    """解析 LLM 返回的决策 JSON - 三级回退"""
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
        r'\{[^{}]*"user_type"[^{}]*\}',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1) if match.lastindex else match.group())
            except (json.JSONDecodeError, IndexError):
                continue

    # 3. 正则兜底
    user_type_match = re.search(r'"?user_type"?\s*:\s*"?(\w+)"?', text)
    churn_match = re.search(r'"?churn_risk"?\s*:\s*"?(\w+)"?', text)
    action_match = re.search(r'"?recommended_action"?\s*:\s*"([^"]+)"', text)
    reasoning_match = re.search(r'"?reasoning"?\s*:\s*"([^"]+)"', text)

    if user_type_match:
        return {
            "user_type": user_type_match.group(1),
            "churn_risk": churn_match.group(1) if churn_match else "medium",
            "recommended_action": action_match.group(1) if action_match else "待定",
            "reasoning": reasoning_match.group(1) if reasoning_match else "正则提取",
        }

    raise ValueError(f"无法解析决策响应: {text[:200]}")


def _validate_decision(data: dict) -> dict:
    """验证并规范化决策结果"""
    user_type = data.get("user_type", "potential").lower()
    churn_risk = data.get("churn_risk", "medium").lower()

    if user_type not in VALID_USER_TYPES:
        user_type = "potential"
    if churn_risk not in VALID_CHURN_RISKS:
        churn_risk = "medium"

    return {
        "user_type": user_type,
        "churn_risk": churn_risk,
        "recommended_action": str(data.get("recommended_action", "持续观察")),
        "reasoning": str(data.get("reasoning", "")),
    }


def _build_decision_prompt(profile, recent_orders: list, feedback_summary: str, rule_result: dict) -> str:
    """构建 LLM 决策提示词"""
    # 兼容 ORM 对象和字典
    get = lambda attr, default="N/A": getattr(profile, attr, None) or (profile.get(attr, default) if isinstance(profile, dict) else default)

    orders_text = "无近期订单"
    if recent_orders:
        orders_lines = []
        for o in recent_orders[:10]:
            oid = getattr(o, "id", None) or o.get("id", "?")
            amount = getattr(o, "amount", None) or o.get("amount", 0)
            product = getattr(o, "product", None) or o.get("product", "")
            status = getattr(o, "status", None) or o.get("status", "")
            orders_lines.append(f"  - 订单#{oid}: ¥{amount} {product} ({status})")
        orders_text = "\n".join(orders_lines)

    return f"""用户画像:
- RFM 评分: {get('rfm_score', '111')}
- 总消费: ¥{get('total_spent', 0)}
- 购买频率: {get('purchase_frequency', 0)}次/月
- 最近活跃: {get('last_active_days', 0)}天前
- 用户等级: {get('user_level', 'N/A')}

规则预分类结果:
- 用户类型: {rule_result['user_type']}
- 流失风险: {rule_result['churn_risk']}
- 命中规则: {rule_result.get('rules_fired', [])}

近期订单:
{orders_text}

反馈摘要:
{feedback_summary or '暂无反馈数据'}

请基于以上信息进行综合判断，返回 JSON 决策结果。"""


def generate_decision(profile, recent_orders: list, feedback_summary: str, max_retries: int = 3) -> dict:
    """生成用户决策 - 规则 + AI 混合方案

    Args:
        profile: UserProfile 对象或字典
        recent_orders: 近期订单列表
        feedback_summary: 反馈摘要文本
        max_retries: LLM 调用最大重试次数

    Returns:
        决策结果字典
    """
    # Step 1: 规则预分类
    rule_result = rule_based_classify(profile)

    # Step 2: 尝试调用 LLM
    use_local = os.getenv("USE_LOCAL_MODEL", "false").lower() == "true"
    if use_local:
        # 本地模型不支持决策复杂任务，直接使用规则结果
        logger.info("使用本地模型，回退到规则决策")
        return {**rule_result, "rule_based": True}

    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.AI_API_KEY, base_url=settings.AI_API_BASE_URL)
    except Exception as e:
        logger.warning(f"无法初始化 AI 客户端: {e}")
        return {**rule_result, "rule_based": True}

    prompt = _build_decision_prompt(profile, recent_orders, feedback_summary, rule_result)

    # Step 3: 带重试的 LLM 调用
    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "system", "content": DECISION_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=500,
            )
            result_text = response.choices[0].message.content.strip()
            result = _parse_decision_response(result_text)
            validated = _validate_decision(result)
            logger.info(f"AI 决策成功: user_type={validated['user_type']}, churn_risk={validated['churn_risk']}")
            return {**validated, "rule_based": False}

        except Exception as e:
            last_error = str(e)
            logger.warning(f"AI 决策失败 (尝试 {attempt + 1}/{max_retries}): {last_error}")
            if attempt < max_retries - 1:
                # 指数退避
                time.sleep(2 ** attempt)

    # Step 4: 所有重试失败，回退到规则结果
    logger.error(f"AI 决策最终失败，使用规则回退: {last_error}")
    return {
        **rule_result,
        "rule_based": True,
        "ai_error": last_error,
    }
