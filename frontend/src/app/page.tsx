import Link from 'next/link'

const features = [
  { icon: '📁', title: 'CSV 导入', desc: '一键上传客户反馈数据，自动解析列映射，支持批量导入与增量更新' },
  { icon: '🤖', title: 'AI 分析', desc: '基于大语言模型的情感分析、关键词提取与自动分类，精准洞察客户心声' },
  { icon: '📊', title: '可视化', desc: '情感趋势图、主题词云、数据卡片一目了然，支持多维度交叉分析' },
  { icon: '🎯', title: 'RFM 分层', desc: '基于最近消费、消费频率、消费金额三维度自动客户分层与价值评估' },
  { icon: '⚡', title: '决策引擎', desc: '智能推荐营销策略与运营动作，从数据洞察到业务决策一键直达' },
  { icon: '🔗', title: '多数据源', desc: '支持 CSV、API、数据库等多种数据接入方式，统一数据湖管理' },
]

const steps = [
  { num: '01', title: '数据导入', desc: '上传 CSV 或连接数据源' },
  { num: '02', title: 'RFM 评分', desc: '自动计算客户价值分层' },
  { num: '03', title: 'AI 分析', desc: '情感分析与智能分类' },
  { num: '04', title: '决策输出', desc: '生成可执行营销策略' },
]

const techStack = [
  'FastAPI', 'Next.js', 'PostgreSQL', 'Tailwind CSS', 'Recharts', 'Docker',
]

const stats = [
  { value: '50+', label: 'API Endpoints' },
  { value: '13', label: 'Test Files' },
  { value: '6', label: 'Data Sources' },
  { value: '100%', label: 'Docker Ready' },
]

export default function Home() {
  return (
    <div className="min-h-screen overflow-hidden">
      {/* ── Animated Gradient Hero ── */}
      <section className="relative pt-32 pb-24 px-6 text-center">
        {/* Animated gradient backdrop */}
        <div className="absolute inset-0 -z-20 hero-gradient" />
        {/* Particle / dot grid */}
        <div className="absolute inset-0 -z-10 hero-dots" />

        <h1 className="text-5xl md:text-7xl font-extrabold mb-6 tracking-tight">
          <span className="bg-gradient-to-r from-primary-400 via-accent-300 to-primary-400 bg-[length:200%_auto] bg-clip-text text-transparent animate-gradient-x">
            AI Customer Insight
          </span>
        </h1>
        <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mb-4 leading-relaxed">
          利用大语言模型对客户反馈进行情感分析、关键词提取和自动分类
        </p>
        <p className="text-base text-gray-500 max-w-xl mx-auto mb-10">
          从数据导入到决策输出，一站式客户洞察平台
        </p>
        <div className="flex gap-4 justify-center flex-wrap">
          <Link href="/login" className="btn-primary text-lg shadow-lg shadow-primary-600/20 hover:shadow-primary-600/40 transition-shadow">
            开始使用
          </Link>
          <Link href="/register" className="btn-ghost text-lg border border-[#1e1e2e]">
            注册账号
          </Link>
        </div>
      </section>

      {/* ── Stats ── */}
      <section className="py-16 px-6 border-y border-[#1e1e2e] bg-[#0d0d14]">
        <div className="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {stats.map((s) => (
            <div key={s.label}>
              <div className="text-3xl md:text-4xl font-extrabold bg-gradient-to-r from-primary-400 to-accent-400 bg-clip-text text-transparent">
                {s.value}
              </div>
              <div className="text-sm text-gray-500 mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Features ── */}
      <section className="py-24 px-6">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-4 text-white">核心功能</h2>
        <p className="text-gray-500 text-center mb-12 max-w-lg mx-auto">
          覆盖从数据采集到智能决策的完整链路
        </p>
        <div className="max-w-5xl mx-auto grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f) => (
            <div key={f.title} className="card group text-center">
              <div className="text-4xl mb-4 transition-transform group-hover:scale-110">{f.icon}</div>
              <h3 className="text-lg font-semibold mb-2 text-white">{f.title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── How It Works ── */}
      <section className="py-24 px-6 bg-[#0d0d14]">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-4 text-white">工作流程</h2>
        <p className="text-gray-500 text-center mb-16 max-w-lg mx-auto">
          四步完成从原始数据到商业洞察的转化
        </p>
        <div className="max-w-4xl mx-auto grid sm:grid-cols-2 lg:grid-cols-4 gap-8 relative">
          {/* Connecting arrows (desktop) */}
          <div className="hidden lg:block absolute top-12 left-[calc(12.5%+2rem)] right-[calc(12.5%+2rem)] h-px">
            <div className="w-full h-full bg-gradient-to-r from-primary-600 via-accent-500 to-primary-600 opacity-40" />
          </div>
          {steps.map((s, i) => (
            <div key={s.num} className="relative flex flex-col items-center text-center">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary-600/20 to-accent-600/20 border border-primary-500/20 flex items-center justify-center mb-4 relative z-10">
                <span className="text-2xl font-extrabold bg-gradient-to-r from-primary-400 to-accent-400 bg-clip-text text-transparent">
                  {s.num}
                </span>
              </div>
              {/* Arrow between cards (desktop) */}
              {i < steps.length - 1 && (
                <div className="hidden lg:block absolute top-10 -right-4 text-primary-500/40 text-xl z-20">
                  →
                </div>
              )}
              <h3 className="text-lg font-semibold text-white mb-1">{s.title}</h3>
              <p className="text-gray-500 text-sm">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Tech Stack ── */}
      <section className="py-24 px-6">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-4 text-white">技术栈</h2>
        <p className="text-gray-500 text-center mb-12 max-w-lg mx-auto">
          现代化全栈架构，生产就绪
        </p>
        <div className="max-w-3xl mx-auto flex flex-wrap justify-center gap-3">
          {techStack.map((t) => (
            <span
              key={t}
              className="px-5 py-2.5 rounded-full text-sm font-medium bg-[#13131a] border border-[#1e1e2e] text-gray-300 hover:border-primary-500/40 hover:text-primary-300 transition-colors cursor-default"
            >
              {t}
            </span>
          ))}
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="py-12 px-6 border-t border-[#1e1e2e] bg-[#0d0d14]">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-gray-500">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-gray-300">AI Customer Insight</span>
            <span>·</span>
            <span>一站式客户洞察平台</span>
          </div>
          <div className="flex items-center gap-6">
            <a
              href="https://github.com/your-org/ai-customer-insight"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-white transition-colors"
            >
              GitHub
            </a>
            <span>© {new Date().getFullYear()} AI Customer Insight</span>
          </div>
        </div>
      </footer>
    </div>
  )
}
