"use client"
import { useEffect, useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import api from "@/lib/api"
import DataCard from "@/components/DataCard"
import SentimentChart from "@/components/SentimentChart"
import TopicChart from "@/components/TopicChart"
import FileUpload from "@/components/FileUpload"
import FeedbackTable from "@/components/FeedbackTable"

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
  const [analyzing, setAnalyzing] = useState(false)

  const fetchStats = useCallback(async () => {
    try {
      const { data } = await api.get("/api/dashboard")
      setStats(data)
    } catch (err: any) {
      if (err.response?.status === 401) router.push("/login")
    } finally {
      setLoading(false)
    }
  }, [router])

  useEffect(() => {
    if (!localStorage.getItem("token")) { router.push("/login"); return }
    fetchStats()
  }, [fetchStats, router])

  const runAnalysis = async () => {
    setAnalyzing(true)
    try {
      await api.post("/api/analyze")
      await fetchStats()
    } catch { }
    finally { setAnalyzing(false) }
  }

  if (loading) return <div className="min-h-screen flex items-center justify-center text-gray-600">加载中...</div>

  const dist = stats?.sentiment_distribution
  const positiveRate = stats?.analyzed_count ? Math.round(((dist?.positive || 0) / stats.analyzed_count) * 100) : 0
  const negativeRate = stats?.analyzed_count ? Math.round(((dist?.negative || 0) / stats.analyzed_count) * 100) : 0

  return (
    <div className="max-w-7xl mx-auto px-6 pt-24 pb-12">
      {/* 数据卡片 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <DataCard icon="📊" label="反馈总数" value={stats?.total_feedbacks || 0} />
        <DataCard icon="✅" label="已分析" value={stats?.analyzed_count || 0} />
        <DataCard icon="😊" label="积极占比" value={`${positiveRate}%`} color="green" />
        <DataCard icon="😟" label="消极占比" value={`${negativeRate}%`} color="red" />
      </div>

      {/* 操作栏 */}
      <div className="flex gap-4 mb-6">
        <FileUpload onSuccess={fetchStats} />
      </div>
      <div className="mb-6">
        <button className="btn-primary" onClick={runAnalysis} disabled={analyzing}>
          {analyzing ? "🤖 分析中..." : "🤖 运行 AI 分析"}
        </button>
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
