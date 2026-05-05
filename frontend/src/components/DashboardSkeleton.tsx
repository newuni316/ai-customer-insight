export function CardSkeleton() {
  return (
    <div className="card animate-pulse">
      <div className="flex items-start justify-between mb-4">
        <div className="w-8 h-8 bg-gray-700 rounded" />
        <div className="w-12 h-5 bg-gray-700 rounded-full" />
      </div>
      <div className="w-20 h-8 bg-gray-700 rounded mb-2" />
      <div className="w-16 h-4 bg-gray-700 rounded" />
    </div>
  )
}

export function ChartSkeleton() {
  return (
    <div className="card animate-pulse">
      <div className="w-32 h-5 bg-gray-700 rounded mb-6" />
      <div className="h-64 bg-gray-800/50 rounded flex items-end gap-2 px-4 pb-4">
        {[40, 65, 50, 80, 35, 60, 45].map((h, i) => (
          <div key={i} className="flex-1 bg-gray-700 rounded-t" style={{ height: `${h}%` }} />
        ))}
      </div>
    </div>
  )
}

export function TableSkeleton() {
  return (
    <div className="card animate-pulse">
      <div className="w-24 h-5 bg-gray-700 rounded mb-4" />
      {[1, 2, 3, 4, 5].map((i) => (
        <div key={i} className="flex gap-4 py-3 border-b border-gray-800">
          <div className="flex-1 h-4 bg-gray-700 rounded" />
          <div className="w-16 h-4 bg-gray-700 rounded" />
          <div className="w-20 h-4 bg-gray-700 rounded" />
        </div>
      ))}
    </div>
  )
}

export default function DashboardSkeleton() {
  return (
    <div className="max-w-7xl mx-auto px-6 pt-24 pb-12">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {[1, 2, 3, 4].map((i) => <CardSkeleton key={i} />)}
      </div>
      <div className="grid md:grid-cols-2 gap-6 mb-6">
        <ChartSkeleton />
        <ChartSkeleton />
      </div>
      <TableSkeleton />
    </div>
  )
}
