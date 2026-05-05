"use client"
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"

interface DataPoint { date: string; positive: number; neutral: number; negative: number }
interface Props { data: DataPoint[] }

export default function SentimentChart({ data }: Props) {
  if (!data.length) {
    return <div className="card flex items-center justify-center h-64 text-gray-600">暂无数据</div>
  }
  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-white mb-4">📈 情感趋势</h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="gPos" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#22c55e" stopOpacity={0.3}/><stop offset="95%" stopColor="#22c55e" stopOpacity={0}/></linearGradient>
            <linearGradient id="gNeu" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#eab308" stopOpacity={0.3}/><stop offset="95%" stopColor="#eab308" stopOpacity={0}/></linearGradient>
            <linearGradient id="gNeg" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/><stop offset="95%" stopColor="#ef4444" stopOpacity={0}/></linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
          <XAxis dataKey="date" stroke="#666" fontSize={12} />
          <YAxis stroke="#666" fontSize={12} />
          <Tooltip contentStyle={{ background: "#13131a", border: "1px solid #2a2a3a", borderRadius: 8 }} />
          <Legend />
          <Area type="monotone" dataKey="positive" name="积极" stroke="#22c55e" fill="url(#gPos)" />
          <Area type="monotone" dataKey="neutral" name="中立" stroke="#eab308" fill="url(#gNeu)" />
          <Area type="monotone" dataKey="negative" name="消极" stroke="#ef4444" fill="url(#gNeg)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
