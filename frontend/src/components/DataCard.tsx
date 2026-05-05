interface Props {
  icon: string
  label: string
  value: string | number
  trend?: { value: number; up: boolean }
  color?: string
}

export default function DataCard({ icon, label, value, trend, color = "primary" }: Props) {
  return (
    <div className="card">
      <div className="flex items-start justify-between mb-4">
        <span className="text-2xl">{icon}</span>
        {trend && (
          <span className={`text-xs font-medium px-2 py-1 rounded-full ${trend.up ? "bg-green-500/10 text-green-400" : "bg-red-500/10 text-red-400"}`}>
            {trend.up ? "↑" : "↓"} {trend.value}%
          </span>
        )}
      </div>
      <p className="text-3xl font-bold text-white mb-1">{value}</p>
      <p className="text-sm text-gray-500">{label}</p>
    </div>
  )
}
