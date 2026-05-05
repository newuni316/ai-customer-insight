"use client"
import { useEffect, useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import api from "@/lib/api"
import DataCard from "@/components/DataCard"
import SentimentChart from "@/components/SentimentChart"
import TopicChart from "@/components/TopicChart"
import FileUpload from "@/components/FileUpload"
import FeedbackTable from "@/components/FeedbackTable"
import DashboardSkeleton from "@/components/DashboardSkeleton"

interface Stats {
  total_feedbacks: number
  analyzed_count: number
  sentiment_distribution: { positive: number; neutral: number; negative: number }
  top_topics: { topic: string; count: number }[]
  daily_trends: { date: string; positive: number; neutral: number; negative: number }[]
}

export default function DashboardPage() {
  const router = useRouter()
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [analyzing, setAnalyzing] = useState(false)

  const fetchStats = useCallback(async () => {
    try {
      setError(null)
      const { data } = await api.get("/api/dashboard")
      setStats(data)
    } catch (err: any) {
      if (err.response?.status === 401) { router.push("/login"); return }
      setError(err.message || "加载失败")
    } finally {
      setLoading(false)
    }
  }, [router])

  useEffect(() => {
    fetchStats()
  }, [fetchStats])

  const runAnalysis = async () => {
    setAnalyzing(true)
    try {
      const { data } = await api.post("/api/analyze")
      alert(`分析完成: 成功 ${data.analyzed} 条, 失败 ${data.failed} 条`)
      await fetchStats()
    } catch (err: any) {
      alert("分析失败: " + (err.response?.data?.detail || err.message))
    } finally {
      setAnalyzing(false)
    }
  }

  if (loading) return <DashboardSkeleton />

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="card text-center max-w-md">
          <p className="text-red-400 mb-4">❌ {error}</p>
          <button className="btn-primary" onClick={fetchStats}>重试</button>
        </div>
      </div>
    )
  }

  const dist = stats?.sentiment_distribution
  const positiveRate = stats?.analyzed_count ? Math.round(((dist?.positive || 0) / stats.analyzed_count) * 100) : 0
  const negativeRate = stats?.analyzed_count ? Math.round(((dist?.negative || 0) / stats.analyzed_count) * 100) : 0

  return (
    <div className="max-w-7xl mx-auto px-6 pt-24 pb-12">
      {/* 操作栏 */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-white">📊 数据仪表盘</h1>
        <button className="btn-ghost text-sm border border-[#1e1e2e]" onClick={fetchStats}>
          🔄 刷新数据
        </button>
      </div>

      {/* 数据卡片 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <DataCard icon="📊" label="反馈总数" value={stats?.total_feedbacks || 0} />
        <DataCard icon="✅" label="已分析" value={stats?.analyzed_count || 0} />
        <DataCard icon="😊" label="积极占比" value={`${positiveRate}%`} />
        <DataCard icon="😟" label="消极占比" value={`${negativeRate}%`} />
      </div>

      {/* 上传 + 分析 */}
      <div className="grid md:grid-cols-2 gap-4 mb-6">
        <FileUpload onSuccess={() => { fetchStats() }} />
        <div className="card flex items-center justify-center">
          <button className="btn-primary text-lg" onClick={runAnalysis} disabled={analyzing}>
            {analyzing ? "🤖 分析中..." : "🤖 运行 AI 分析"}
          </button>
        </div>
      </div>

      {/* 图表 */}
      <div className="grid md:grid-cols-2 gap-6 mb-6">
        <SentimentChart data={stats?.daily_trends || []} />
        <TopicChart data={stats?.top_topics || []} />
      </div>

      {/* 反馈列表 */}
      <FeedbackTable />
    </div>
  )
}
