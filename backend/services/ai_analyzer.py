"""AI 分析服务 - 支持云端 API 和本地模型"""
import json
import os
from config import get_settings

settings = get_settings()

SYSTEM_PROMPT = """你是一个客户反馈分析专家。请分析以下客户反馈，返回 JSON 格式：
{
  "sentiment": "positive" 或 "neutral" 或 "negative",
  "topics": ["主题1", "主题2"],
  "confidence": 0.0到1.0的置信度
}
主题示例：物流、质量、服务态度、价格、包装、售后、功能、体验
只返回 JSON，不要其他文字。"""


def analyze_feedback(content: str) -> dict:
    """分析单条反馈 - 自动选择云端或本地模型"""
    use_local = os.getenv("USE_LOCAL_MODEL", "false").lower() == "true"

    if use_local:
        from services.local_model import get_local_analyzer
        return get_local_analyzer().analyze(content)
    else:
        return _analyze_cloud(content)


def _analyze_cloud(content: str) -> dict:
    """云端 API 分析"""
    from openai import OpenAI
    client = OpenAI(api_key=settings.AI_API_KEY, base_url=settings.AI_API_BASE_URL)

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
    if "```" in result_text:
        result_text = result_text.split("```")[1]
        if result_text.startswith("json"):
            result_text = result_text[4:]

    result = json.loads(result_text)
    return {
        "sentiment": result.get("sentiment", "neutral"),
        "topics": result.get("topics", []),
        "confidence": float(result.get("confidence", 0.5)),
    }


def batch_analyze(feedbacks: list[str]) -> list[dict]:
    """批量分析"""
    results = []
    for content in feedbacks:
        try:
            results.append(analyze_feedback(content))
        except Exception:
            results.append({"sentiment": "neutral", "topics": [], "confidence": 0.0})
    return results
