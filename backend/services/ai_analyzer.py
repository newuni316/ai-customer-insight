"""AI 分析服务 - 调用 LLM 进行情感分析和主题提取"""
import json
from openai import OpenAI
from config import get_settings

settings = get_settings()

SYSTEM_PROMPT = """你是一个客户反馈分析专家。请分析以下客户反馈，返回 JSON 格式结果：
{
  "sentiment": "positive" 或 "neutral" 或 "negative",
  "topics": ["主题1", "主题2"],
  "confidence": 0.0到1.0的置信度
}
主题示例：物流、质量、服务态度、价格、包装、售后、功能、体验
只返回 JSON，不要其他文字。"""


def analyze_feedback(content: str) -> dict:
    """调用 AI API 分析单条反馈"""
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
    # 提取 JSON
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
    """批量分析反馈"""
    results = []
    for content in feedbacks:
        try:
            result = analyze_feedback(content)
            results.append(result)
        except Exception:
            results.append({"sentiment": "neutral", "topics": [], "confidence": 0.0})
    return results
