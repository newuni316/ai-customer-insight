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
