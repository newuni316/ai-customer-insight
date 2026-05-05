# AI Customer Insight Dashboard

> AI 驱动的客户反馈洞察平台 — 展示全栈开发 + AI 接口整合能力

## 功能

- 🔐 JWT 用户认证（注册/登录）
- 📊 CSV 数据导入（客户反馈）
- 🤖 AI 智能分析（情感分析 + 关键词提取 + 自动分类）
- 📈 可视化仪表盘（趋势图 + 主题图表 + 数据卡片）

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Next.js 14 + Tailwind CSS + Recharts |
| 后端 | FastAPI + SQLAlchemy |
| 数据库 | PostgreSQL (开发环境可用 SQLite) |
| AI | OpenAI 兼容 API |

## 快速开始

### 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # 编辑 .env 填入 API Key
uvicorn main:app --reload --port 8000
```

API 文档: http://localhost:8000/docs

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问: http://localhost:3000

### 使用流程

1. 注册账号并登录
2. 上传 CSV 文件（列名: `date`, `source`, `content`）
3. 点击 "运行 AI 分析" 按钮
4. 查看仪表盘可视化结果

## CSV 格式示例

```csv
date,source,content
2024-01-15,淘宝,物流速度很快，包装也很好，非常满意！
2024-01-16,京东,产品质量太差了，用了两天就坏了
2024-01-17,客服,服务态度一般，问题没有完全解决
```

## 项目结构

```
ai-customer-insight/
├── backend/           # FastAPI 后端
│   ├── main.py        # 入口
│   ├── models.py      # 数据库模型
│   ├── routers/       # API 路由
│   └── services/      # 业务逻辑
├── frontend/          # Next.js 前端
│   └── src/
│       ├── app/       # 页面
│       ├── components/# 组件
│       └── lib/       # 工具
└── README.md
```
