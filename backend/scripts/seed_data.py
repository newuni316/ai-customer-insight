"""种子数据生成脚本 - 生成模拟用户、订单、反馈、画像和决策数据"""
import sys
import os
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import User, Feedback, Analytics, Order, UserProfile, Decision

# ── 常量 ──────────────────────────────────────────────
NUM_USERS = 50
NUM_ORDERS = 520
NUM_FEEDBACKS = 210
NUM_DECISIONS = 35
MONTHS_SPAN = 6

CHINESE_SURNAMES = [
    "张", "王", "李", "赵", "刘", "陈", "杨", "黄", "周", "吴",
    "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗",
    "梁", "宋", "郑", "谢", "韩", "唐", "冯", "于", "董", "萧",
    "程", "曹", "袁", "邓", "许", "傅", "沈", "曾", "彭", "吕",
    "苏", "卢", "蒋", "蔡", "贾", "丁", "魏", "薛", "叶", "阎",
]
CHINESE_GIVEN_NAMES = [
    "伟", "芳", "娜", "秀英", "敏", "静", "丽", "强", "磊", "洋",
    "勇", "艳", "杰", "娟", "涛", "明", "超", "秀兰", "霞", "平",
    "刚", "桂英", "文", "华", "慧", "建华", "玲", "建国", "建军", "英",
    "志强", "秀珍", "浩", "凯", "鑫", "嘉", "欣", "怡", "博", "宇",
    "泽", "思", "晨", "梓", "子涵", "雨桐", "一诺", "奕辰", "宇轩", "浩然",
]

PRODUCTS = [
    "无线蓝牙耳机", "智能手表", "机械键盘", "便携充电宝", "运动水壶",
    "护眼台灯", "电动牙刷", "保温杯", "手机支架", "数据线套装",
    "笔记本支架", "鼠标垫", "USB集线器", "降噪耳塞", "迷你风扇",
    "桌面收纳盒", "颈椎按摩仪", "电子阅读器保护套", "无线充电器", "运动手环",
]

SOURCES = ["app_review", "customer_service", "social_media", "survey", "email"]

POSITIVE_FEEDBACKS = [
    "产品质量很好，非常满意！",
    "物流速度很快，包装也很仔细。",
    "客服态度非常好，耐心解答了我的问题。",
    "性价比很高，会推荐给朋友。",
    "使用体验非常棒，超出预期。",
    "第二次购买了，一如既往的好。",
    "做工精细，手感很好。",
    "功能齐全，操作简单方便。",
    "颜色很漂亮，和图片一致。",
    "续航能力强，充一次用很久。",
    "声音清晰，佩戴舒适。",
    "设计简洁大方，很喜欢。",
    "发货及时，第二天就到了。",
    "产品质感很好，物超所值。",
    "用了半个月了，没有任何问题。",
]

NEUTRAL_FEEDBACKS = [
    "产品一般，中规中矩吧。",
    "还行，基本符合预期。",
    "包装可以再好一点。",
    "功能够用，但没什么亮点。",
    "和描述差不多，没有惊喜。",
    "等了三天才发货，有点慢。",
    "价格偏高，但质量还可以。",
    "外观一般，不过功能还行。",
    "刚开始用，后续再评价。",
    "有些小瑕疵，但不影响使用。",
    "说明书不够详细，摸索了一会儿。",
    "总体还行，不好不坏。",
]

NEGATIVE_FEEDBACKS = [
    "质量太差了，用了一天就坏了。",
    "物流太慢了，等了快两周。",
    "客服态度很差，问题也没解决。",
    "和描述严重不符，要求退货。",
    "做工粗糙，有明显划痕。",
    "充电有问题，充不满电。",
    "噪音太大了，影响使用。",
    "按键不灵敏，反应很慢。",
    "屏幕有亮点，疑似质量问题。",
    "包装破损，产品也有磕碰。",
    "退货流程太复杂了。",
    "虚假宣传，实际功能缺失。",
    "连接不稳定，经常断开。",
    "异味严重，材质堪忧。",
    "用了一周就出现故障。",
]

TOPICS_POOL = ["产品质量", "物流", "客服", "价格", "包装", "功能", "外观", "售后", "使用体验", "性价比"]

DECISION_USER_TYPES = ["champion", "loyal", "potential", "at_risk", "lost"]
DECISION_ACTIONS = {
    "champion": [
        "升级为VIP会员，提供专属折扣",
        "邀请参与新品内测计划",
        "发放高额优惠券，鼓励持续购买",
    ],
    "loyal": [
        "推送个性化推荐，提升客单价",
        "发放满减优惠券，刺激复购",
        "邀请参与会员积分活动",
    ],
    "potential": [
        "发送新人专享优惠券",
        "推送热销商品，引导首次复购",
        "提供限时折扣，培养购买习惯",
    ],
    "at_risk": [
        "发送挽回优惠券，提供额外折扣",
        "客服主动联系了解需求",
        "推送用户感兴趣的商品信息",
    ],
    "lost": [
        "发送大额回归优惠券",
        "问卷调查流失原因",
        "暂停营销投入，标记为低优先级",
    ],
}
DECISION_REASONINGS = {
    "champion": "该用户消费金额高、购买频次稳定、近期活跃，是高价值核心用户。",
    "loyal": "用户购买频次较高，消费金额中等偏上，具有较高的忠诚度。",
    "potential": "新用户或购买频次较低，但近期有活跃行为，具有成长潜力。",
    "at_risk": "用户最近活跃度下降，购买间隔增大，存在流失风险。",
    "lost": "用户长时间未活跃，最近无购买记录，已基本流失。",
}


# ── 辅助函数 ──────────────────────────────────────────
def random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)


def random_chinese_name() -> str:
    return random.choice(CHINESE_SURNAMES) + random.choice(CHINESE_GIVEN_NAMES)


def compute_rfm_score(recency: int, frequency: float, monetary: float) -> str:
    """简单 RFM 评分 (1-5)"""
    r = min(5, max(1, 6 - recency // 30))
    f = min(5, max(1, int(frequency * 2)))
    m = min(5, max(1, int(monetary / 1000)))
    return f"{r}{f}{m}"


def classify_user_level(rfm_score: str) -> str:
    total = sum(int(c) for c in rfm_score)
    if total >= 12:
        return "High Value"
    elif total >= 7:
        return "Medium Value"
    return "Low Value"


def classify_churn_risk(rfm_score: str) -> str:
    recency = int(rfm_score[0])
    if recency >= 4:
        return "low"
    elif recency >= 2:
        return "medium"
    return "high"


def classify_user_type(rfm_score: str, level: str) -> str:
    if level == "High Value":
        return "champion" if int(rfm_score[0]) >= 4 else "loyal"
    elif level == "Medium Value":
        return "potential" if int(rfm_score[0]) >= 3 else "at_risk"
    return "lost" if int(rfm_score[0]) <= 2 else "potential"


# ── 主逻辑 ────────────────────────────────────────────
def seed():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    now = datetime.utcnow()
    start_date = now - timedelta(days=MONTHS_SPAN * 30)

    try:
        # 1) Users
        print(f"[1/6] 创建 {NUM_USERS} 个用户...")
        users = []
        for i in range(NUM_USERS):
            name = random_chinese_name()
            user = User(
                email=f"user{i+1:03d}@example.com",
                password_hash=f"hashed_seed_{i+1}",
                created_at=random_date(start_date, start_date + timedelta(days=30)),
            )
            users.append(user)
        db.add_all(users)
        db.commit()
        user_ids = [u.id for u in users]
        print(f"  ✓ 用户创建完成 (IDs: {user_ids[0]}~{user_ids[-1]})")

        # 2) Orders
        print(f"[2/6] 创建 {NUM_ORDERS} 笔订单...")
        orders = []
        statuses = ["completed"] * 85 + ["refunded"] * 10 + ["cancelled"] * 5
        for _ in range(NUM_ORDERS):
            order = Order(
                user_id=random.choice(user_ids),
                amount=round(random.uniform(50, 2000), 2),
                product=random.choice(PRODUCTS),
                status=random.choice(statuses),
                created_at=random_date(start_date, now),
            )
            orders.append(order)
        db.add_all(orders)
        db.commit()
        print(f"  ✓ 订单创建完成")

        # 3) Feedbacks + Analytics
        print(f"[3/6] 创建 {NUM_FEEDBACKS} 条反馈及情感分析...")
        sentiment_dist = (
            ["positive"] * 105
            + ["neutral"] * 53
            + ["negative"] * 52
        )
        feedbacks = []
        analytics_list = []
        for _ in range(NUM_FEEDBACKS):
            sentiment = random.choice(sentiment_dist)
            if sentiment == "positive":
                content = random.choice(POSITIVE_FEEDBACKS)
            elif sentiment == "neutral":
                content = random.choice(NEUTRAL_FEEDBACKS)
            else:
                content = random.choice(NEGATIVE_FEEDBACKS)

            fb_date = random_date(start_date, now)
            fb = Feedback(
                user_id=random.choice(user_ids),
                source=random.choice(SOURCES),
                content=content,
                date=fb_date,
                created_at=fb_date,
            )
            feedbacks.append(fb)
        db.add_all(feedbacks)
        db.flush()

        for fb in feedbacks:
            sentiment = random.choice(sentiment_dist)
            if "好" in fb.content or "满意" in fb.content or "棒" in fb.content or "推荐" in fb.content:
                sentiment = "positive"
            elif "差" in fb.content or "坏" in fb.content or "慢" in fb.content or "退货" in fb.content:
                sentiment = "negative"
            else:
                sentiment = "neutral"

            ana = Analytics(
                feedback_id=fb.id,
                sentiment=sentiment,
                topics=random.sample(TOPICS_POOL, k=random.randint(1, 3)),
                confidence=round(random.uniform(0.6, 0.99), 2),
                analyzed_at=fb_date,
            )
            analytics_list.append(ana)
        db.add_all(analytics_list)
        db.commit()
        print(f"  ✓ 反馈及情感分析创建完成")

        # 4) UserProfiles (RFM)
        print(f"[4/6] 创建 {NUM_USERS} 个 RFM 用户画像...")
        profiles = []
        for uid in user_ids:
            user_orders = [o for o in orders if o.user_id == uid]
            total_spent = sum(o.amount for o in user_orders)
            order_count = len(user_orders)
            avg_order = total_spent / order_count if order_count else 0
            frequency = order_count / MONTHS_SPAN

            if user_orders:
                last_order_date = max(o.created_at for o in user_orders)
                last_active = (now - last_order_date).days
            else:
                last_active = random.randint(60, 180)

            rfm = compute_rfm_score(last_active, frequency, total_spent)
            level = classify_user_level(rfm)
            churn = classify_churn_risk(rfm)

            profile = UserProfile(
                user_id=uid,
                total_spent=round(total_spent, 2),
                avg_order_value=round(avg_order, 2),
                purchase_frequency=round(frequency, 2),
                last_active_days=last_active,
                rfm_score=rfm,
                user_level=level,
                churn_risk=churn,
                updated_at=now,
            )
            profiles.append(profile)
        db.add_all(profiles)
        db.commit()
        print(f"  ✓ 用户画像创建完成")

        # 5) Decisions
        print(f"[5/6] 创建 {NUM_DECISIONS} 条 AI 决策...")
        decisions = []
        selected_users = random.sample(user_ids, k=min(NUM_DECISIONS, len(user_ids)))
        for uid in selected_users:
            profile = next(p for p in profiles if p.user_id == uid)
            user_type = classify_user_type(profile.rfm_score, profile.user_level)
            action = random.choice(DECISION_ACTIONS[user_type])
            reasoning = DECISION_REASONINGS[user_type]

            dec = Decision(
                user_id=uid,
                user_type=user_type,
                churn_risk=profile.churn_risk,
                recommended_action=action,
                reasoning=reasoning,
                rule_based=random.choice([0, 0, 0, 1]),
                created_at=random_date(now - timedelta(days=7), now),
            )
            decisions.append(dec)
        db.add_all(decisions)
        db.commit()
        print(f"  ✓ AI 决策创建完成")

        # 6) Summary
        print(f"\n{'='*50}")
        print(f"种子数据生成完成！")
        print(f"{'='*50}")
        print(f"  用户:     {NUM_USERS}")
        print(f"  订单:     {NUM_ORDERS}")
        print(f"  反馈:     {NUM_FEEDBACKS}")
        print(f"  情感分析: {NUM_FEEDBACKS}")
        print(f"  用户画像: {NUM_USERS}")
        print(f"  AI 决策:  {NUM_DECISIONS}")
        print(f"{'='*50}")

    except Exception as e:
        db.rollback()
        print(f"✗ 错误: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
