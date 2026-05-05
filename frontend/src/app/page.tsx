import Link from 'next/link'

const features = [
  { icon: '📊', title: 'CSV 数据导入', desc: '一键上传客户反馈数据，自动解析并存储' },
  { icon: '🤖', title: 'AI 智能分析', desc: '情感分析、关键词提取、自动分类' },
  { icon: '📈', title: '可视化大屏', desc: '情感趋势图、主题词云、数据卡片' },
]

export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="pt-32 pb-20 px-6 text-center">
        <h1 className="text-5xl md:text-6xl font-bold mb-6">
          <span className="bg-gradient-to-r from-primary-400 to-accent-400 bg-clip-text text-transparent">
            AI Customer Insight
          </span>
        </h1>
        <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10">
          利用大语言模型对客户反馈进行情感分析、关键词提取和自动分类，<br />
          通过可视化数据大屏呈现分析结果
        </p>
        <div className="flex gap-4 justify-center">
          <Link href="/login" className="btn-primary text-lg">开始使用</Link>
          <Link href="/register" className="btn-ghost text-lg border border-[#1e1e2e]">注册账号</Link>
        </div>
      </section>

      {/* Features */}
      <section className="pb-20 px-6">
        <div className="max-w-4xl mx-auto grid md:grid-cols-3 gap-6">
          {features.map((f) => (
            <div key={f.title} className="card text-center">
              <div className="text-4xl mb-4">{f.icon}</div>
              <h3 className="text-lg font-semibold mb-2 text-white">{f.title}</h3>
              <p className="text-gray-400 text-sm">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
