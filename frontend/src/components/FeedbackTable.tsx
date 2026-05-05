"use client"
import { useState, useEffect } from "react"
import api from "@/lib/api"

interface Feedback {
  id: number; source: string; content: string; date: string
  analytics?: { sentiment: string; topics: string[] } | null
}

export default function FeedbackTable() {
  const [items, setItems] = useState<Feedback[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [sentiment, setSentiment] = useState("")
  const [loading, setLoading] = useState(true)

  const fetchData = async () => {
    setLoading(true)
    try {
      const params: any = { page, page_size: 10 }
      if (sentiment) params.sentiment = sentiment
      const { data } = await api.get("/api/feedbacks", { params })
      setItems(data.items)
      setTotal(data.total)
    } catch { }
    finally { setLoading(false) }
  }

  useEffect(() => { fetchData() }, [page, sentiment])

  const sentimentColor = (s: string) => ({
    positive: "bg-green-500/20 text-green-400",
    neutral: "bg-yellow-500/20 text-yellow-400",
    negative: "bg-red-500/20 text-red-400",
  }[s] || "bg-gray-500/20 text-gray-400")

  const totalPages = Math.ceil(total / 10)

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">💬 反馈列表</h3>
        <select className="input !w-auto !py-2 text-sm" value={sentiment} onChange={e => { setSentiment(e.target.value); setPage(1) }}>
          <option value="">全部情感</option>
          <option value="positive">积极</option>
          <option value="neutral">中立</option>
          <option value="negative">消极</option>
        </select>
      </div>

      {loading ? (
        <div className="text-center py-10 text-gray-600">加载中...</div>
      ) : items.length === 0 ? (
        <div className="text-center py-10 text-gray-600">暂无反馈数据，请先上传 CSV</div>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#1e1e2e]">
                  <th className="text-left py-3 px-2 text-gray-500 font-medium">内容</th>
                  <th className="text-left py-3 px-2 text-gray-500 font-medium w-24">来源</th>
                  <th className="text-left py-3 px-2 text-gray-500 font-medium w-28">日期</th>
                  <th className="text-left py-3 px-2 text-gray-500 font-medium w-20">情感</th>
                </tr>
              </thead>
              <tbody>
                {items.map((fb) => (
                  <tr key={fb.id} className="border-b border-[#1e1e2e]/50 hover:bg-white/[0.02]">
                    <td className="py-3 px-2 text-gray-300 max-w-xs truncate">{fb.content}</td>
                    <td className="py-3 px-2 text-gray-500">{fb.source}</td>
                    <td className="py-3 px-2 text-gray-500">{new Date(fb.date).toLocaleDateString("zh-CN")}</td>
                    <td className="py-3 px-2">
                      {fb.analytics ? (
                        <span className={`text-xs px-2 py-1 rounded-full ${sentimentColor(fb.analytics.sentiment)}`}>
                          {{ positive: "积极", neutral: "中立", negative: "消极" }[fb.analytics.sentiment as string] || fb.analytics.sentiment}
                        </span>
                      ) : <span className="text-xs text-gray-600">未分析</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="flex justify-between items-center mt-4 pt-4 border-t border-[#1e1e2e]">
            <span className="text-sm text-gray-500">共 {total} 条</span>
            <div className="flex gap-2">
              <button className="btn-ghost text-sm" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>上一页</button>
              <span className="text-sm text-gray-500 py-2 px-3">{page} / {totalPages || 1}</span>
              <button className="btn-ghost text-sm" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>下一页</button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
