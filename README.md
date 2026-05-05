# AI Customer Insight Dashboard

> AI 驱动的客户反馈洞察平台 — 全栈开发 + AI 接口整合

## 功能

- 🔐 JWT 用户认证（注册/登录）
- 📊 多数据源接入（CSV / 外部 API / Webhook）
- 🤖 AI 智能分析（情感分析 + 关键词提取 + 自动分类）
- 📈 可视化仪表盘（趋势图 + 主题图表 + 数据卡片）
- 🐳 完整容器化（前后端 Docker + docker-compose 一键启动）
- 🧪 自动化测试（pytest + Jest + Playwright E2E）
- 🔄 数据库迁移（Alembic）

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Next.js 14 + Tailwind CSS + Recharts |
| 后端 | FastAPI + SQLAlchemy + Alembic |
| 数据库 | PostgreSQL（开发可用 SQLite） |
| AI | OpenAI 兼容 API / Ollama 本地模型 |
| 测试 | pytest + Jest + Playwright |
| 部署 | Docker + GitHub Actions CI/CD |

## 快速开始

### 方式一：Docker Compose（推荐）

```bash
docker-compose up -d
```

访问 http://localhost:3000

### 方式二：本地开发

**后端：**
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # 编辑配置
alembic upgrade head   # 初始化数据库
uvicorn main:app --reload --port 8000
```

**前端：**
```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

### 方式三：本地模型（离线环境）

```bash
# 1. 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. 拉取模型
ollama pull qwen2.5:7b

# 3. 在 .env 中启用本地模型
USE_LOCAL_MODEL=true
LOCAL_MODEL_BACKEND=ollama

# 4. 启动后端
uvicorn main:app --reload
```

## 数据库迁移

```bash
# 生成迁移脚本
alembic revision --autogenerate -m "描述变更"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

## 测试

```bash
# 后端测试
cd backend && python -m pytest tests/ -v

# 前端单元测试
cd frontend && npm test

# E2E 测试
cd frontend && npx playwright install && npm run test:e2e
```

## 多数据源接入

| 数据源 | 配置 | 说明 |
|--------|------|------|
| CSV 上传 | 页面拖拽上传 | 最基础的数据导入方式 |
| 外部 API | POST /api/sources/api/sync | 对接 Zendesk、微信等 |
| Webhook | POST /api/sources/webhook/{platform} | 实时接收推送 |
| 本地模型 | .env 配置 USE_LOCAL_MODEL=true | 离线环境 AI 分析 |

## 项目结构

```
ai-customer-insight/
├── .github/workflows/ci.yml    # CI/CD
├── docker-compose.yml          # 一键部署
├── backend/
│   ├── Dockerfile
│   ├── alembic/                # 数据库迁移
│   ├── models.py               # ORM 模型
│   ├── routers/                # API 路由
│   │   ├── auth.py             # 认证
│   │   ├── feedback.py         # 反馈 CRUD
│   │   ├── analytics.py        # AI 分析 + 仪表盘
│   │   └── data_sources.py     # 多数据源管理
│   ├── services/
│   │   ├── ai_analyzer.py      # AI 分析（云端+本地）
│   │   ├── csv_parser.py       # CSV 解析
│   │   ├── local_model.py      # 本地模型推理
│   │   └── data_sources/       # 数据源抽象层
│   └── tests/                  # pytest 测试
├── frontend/
│   ├── Dockerfile
│   ├── .env.example
│   ├── e2e/                    # Playwright E2E 测试
│   └── src/
│       ├── app/                # Next.js 页面
│       ├── components/         # UI 组件
│       ├── lib/                # API 客户端
│       └── __tests__/          # Jest 单元测试
└── README.md
```
