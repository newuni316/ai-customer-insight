"use client"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts"

interface TopicData { topic: string; count: number }
interface Props { data: TopicData[] }

const COLORS = ["#8b5cf6","#06b6d4","#22c55e","#eab308","#ef4444","#f472b6","#a78bfa","#34d399","#fbbf24","#fb923c"]

export default function TopicChart({ data }: Props) {
  if (!data.length) {
    return <div className="card flex items-center justify-center h-64 text-gray-600">暂无数据</div>
  }
  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-white mb-4">🏷️ 热门主题</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} layout="vertical" margin={{ left: 60 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
          <XAxis type="number" stroke="#666" fontSize={12} />
          <YAxis type="category" dataKey="topic" stroke="#666" fontSize={12} />
          <Tooltip contentStyle={{ background: "#13131a", border: "1px solid #2a2a3a", borderRadius: 8 }} />
          <Bar dataKey="count" name="提及次数" radius={[0, 6, 6, 0]}>
            {data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
