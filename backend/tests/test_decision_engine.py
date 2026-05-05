"""AI 决策引擎测试"""
import json
import pytest
from unittest.mock import patch, MagicMock
from services.decision_engine import (
    rule_based_classify,
    _parse_decision_response,
    _validate_decision,
    generate_decision,
)


# --- rule_based_classify ---

def test_rule_inactive_90d():
    """超过90天未活跃 → lost + high churn"""
    profile = {"last_active_days": 100, "total_spent": 100.0, "purchase_frequency": 0.5, "rfm_score": "111"}
    result = rule_based_classify(profile)
    assert result["user_type"] == "lost"
    assert result["churn_risk"] == "high"
    assert "inactive_90d" in result["rules_fired"]


def test_rule_inactive_30d():
    """30-60天未活跃 → at_risk + medium churn"""
    profile = {"last_active_days": 45, "total_spent": 100.0, "purchase_frequency": 0.5, "rfm_score": "222"}
    result = rule_based_classify(profile)
    assert result["user_type"] == "at_risk"
    assert result["churn_risk"] == "medium"
    assert "inactive_30d" in result["rules_fired"]


def test_rule_inactive_60d_high_churn():
    """60-90天未活跃 → at_risk + high churn"""
    profile = {"last_active_days": 75, "total_spent": 100.0, "purchase_frequency": 0.5, "rfm_score": "222"}
    result = rule_based_classify(profile)
    assert result["user_type"] == "at_risk"
    assert result["churn_risk"] == "high"


def test_rule_high_value():
    """高消费 + 高频 → champion"""
    profile = {"last_active_days": 5, "total_spent": 2000.0, "purchase_frequency": 8.0, "rfm_score": "444"}
    result = rule_based_classify(profile)
    assert result["user_type"] == "champion"
    assert "high_value" in result["rules_fired"]


def test_rule_rfm_vip():
    """RFM 以5开头 → champion"""
    profile = {"last_active_days": 5, "total_spent": 500.0, "purchase_frequency": 1.0, "rfm_score": "522"}
    result = rule_based_classify(profile)
    assert result["user_type"] == "champion"
    assert "rfm_vip" in result["rules_fired"]


def test_rule_rfm_above_avg():
    """RFM 均分 >= 3.5 且默认 potential → loyal"""
    profile = {"last_active_days": 5, "total_spent": 500.0, "purchase_frequency": 1.0, "rfm_score": "433"}
    result = rule_based_classify(profile)
    assert result["user_type"] == "loyal"
    assert "rfm_above_avg" in result["rules_fired"]


def test_rule_default_potential():
    """无特殊规则命中 → potential + low churn"""
    profile = {"last_active_days": 5, "total_spent": 200.0, "purchase_frequency": 0.3, "rfm_score": "321"}
    result = rule_based_classify(profile)
    assert result["user_type"] == "potential"
    assert result["churn_risk"] == "low"


def test_rule_with_orm_object():
    """兼容 ORM 对象（使用 getattr）"""
    class FakeProfile:
        last_active_days = 100
        total_spent = 50.0
        purchase_frequency = 0.1
        rfm_score = "111"
    result = rule_based_classify(FakeProfile())
    assert result["user_type"] == "lost"
    assert result["churn_risk"] == "high"


# --- _parse_decision_response ---

def test_parse_valid_json():
    """直接 JSON 解析"""
    text = '{"user_type":"champion","churn_risk":"low","recommended_action":"VIP服务","reasoning":"高价值"}'
    result = _parse_decision_response(text)
    assert result["user_type"] == "champion"


def test_parse_json_in_codeblock():
    """从代码块提取 JSON"""
    text = '```json\n{"user_type":"loyal","churn_risk":"medium","recommended_action":"推荐","reasoning":"稳定"}\n```'
    result = _parse_decision_response(text)
    assert result["user_type"] == "loyal"


def test_parse_regex_fallback():
    """正则兜底提取"""
    text = '分析结果: user_type: at_risk, churn_risk: high, recommended_action: "发送优惠券", reasoning: "活跃度下降"'
    result = _parse_decision_response(text)
    assert result["user_type"] == "at_risk"
    assert result["churn_risk"] == "high"


def test_parse_unparseable_raises():
    """无法解析时抛出 ValueError"""
    with pytest.raises(ValueError, match="无法解析决策响应"):
        _parse_decision_response("这完全不是JSON也没有任何有用信息")


# --- _validate_decision ---

def test_validate_normalizes_invalid_user_type():
    """无效 user_type 归一化为 potential"""
    result = _validate_decision({"user_type": "invalid_type", "churn_risk": "low"})
    assert result["user_type"] == "potential"


def test_validate_normalizes_invalid_churn_risk():
    """无效 churn_risk 归一化为 medium"""
    result = _validate_decision({"user_type": "champion", "churn_risk": "extreme"})
    assert result["churn_risk"] == "medium"


def test_validate_keeps_valid_values():
    """有效值不变"""
    result = _validate_decision({"user_type": "champion", "churn_risk": "high", "recommended_action": "VIP", "reasoning": "test"})
    assert result["user_type"] == "champion"
    assert result["churn_risk"] == "high"


def test_validate_case_insensitive():
    """大小写不敏感"""
    result = _validate_decision({"user_type": "CHAMPION", "churn_risk": "HIGH"})
    assert result["user_type"] == "champion"
    assert result["churn_risk"] == "high"


# --- generate_decision (mocked LLM) ---

@patch.dict("os.environ", {"USE_LOCAL_MODEL": "false"})
@patch("services.decision_engine.OpenAI")
def test_generate_decision_ai_success(mock_openai_cls):
    """AI 调用成功时返回 AI 决策"""
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "user_type": "champion",
        "churn_risk": "low",
        "recommended_action": "VIP专属服务",
        "reasoning": "高频高消费用户",
    })
    mock_client.chat.completions.create.return_value = mock_response

    profile = {"last_active_days": 5, "total_spent": 2000.0, "purchase_frequency": 8.0, "rfm_score": "555"}
    result = generate_decision(profile, [], "测试反馈")
    assert result["user_type"] == "champion"
    assert result["rule_based"] is False


@patch.dict("os.environ", {"USE_LOCAL_MODEL": "false"})
@patch("services.decision_engine.OpenAI")
def test_generate_decision_ai_fails_fallback(mock_openai_cls):
    """AI 调用失败时回退到规则结果"""
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.side_effect = Exception("API Error")

    profile = {"last_active_days": 100, "total_spent": 50.0, "purchase_frequency": 0.1, "rfm_score": "111"}
    result = generate_decision(profile, [], "", max_retries=1)
    assert result["rule_based"] is True
    assert result["user_type"] == "lost"  # 规则引擎的结果
    assert "ai_error" in result


@patch.dict("os.environ", {"USE_LOCAL_MODEL": "true"})
def test_generate_decision_local_model_uses_rules():
    """本地模型模式直接使用规则结果"""
    profile = {"last_active_days": 5, "total_spent": 2000.0, "purchase_frequency": 8.0, "rfm_score": "555"}
    result = generate_decision(profile, [], "")
    assert result["rule_based"] is True
    assert result["user_type"] == "champion"


@patch.dict("os.environ", {"USE_LOCAL_MODEL": "false"})
@patch("services.decision_engine.OpenAI")
def test_generate_decision_retry_mechanism(mock_openai_cls):
    """重试机制：2次失败后第3次成功"""
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client

    success_response = MagicMock()
    success_response.choices = [MagicMock()]
    success_response.choices[0].message.content = json.dumps({
        "user_type": "loyal",
        "churn_risk": "low",
        "recommended_action": "推荐关联商品",
        "reasoning": "稳定用户",
    })

    mock_client.chat.completions.create.side_effect = [
        Exception("Timeout"),
        Exception("Rate Limit"),
        success_response,
    ]

    profile = {"last_active_days": 5, "total_spent": 1000.0, "purchase_frequency": 3.0, "rfm_score": "433"}
    with patch("services.decision_engine.time.sleep"):
        result = generate_decision(profile, [], "", max_retries=3)
    assert result["user_type"] == "loyal"
    assert result["rule_based"] is False


@patch.dict("os.environ", {"USE_LOCAL_MODEL": "false"})
@patch("services.decision_engine.OpenAI")
def test_generate_decision_invalid_ai_output_validated(mock_openai_cls):
    """AI 返回无效字段时被归一化"""
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "user_type": "super_vip",  # 无效值
        "churn_risk": "extreme",   # 无效值
        "recommended_action": "测试",
        "reasoning": "测试",
    })
    mock_client.chat.completions.create.return_value = mock_response

    profile = {"last_active_days": 5, "total_spent": 500.0, "purchase_frequency": 1.0, "rfm_score": "333"}
    result = generate_decision(profile, [], "")
    assert result["user_type"] == "potential"  # 归一化
    assert result["churn_risk"] == "medium"    # 归一化
