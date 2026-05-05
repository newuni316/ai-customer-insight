"use client";

export interface FilterState {
  startDate: string;
  endDate: string;
  userLevel: string;
  minSpending: number;
  maxSpending: number;
}

interface FilterBarProps {
  filters: FilterState;
  onChange: (filters: FilterState) => void;
}

const USER_LEVELS = [
  { value: "", label: "全部等级" },
  { value: "high", label: "高价值" },
  { value: "medium", label: "中价值" },
  { value: "low", label: "低价值" },
];

export default function FilterBar({ filters, onChange }: FilterBarProps) {
  const update = (partial: Partial<FilterState>) =>
    onChange({ ...filters, ...partial });

  const reset = () =>
    onChange({
      startDate: "",
      endDate: "",
      userLevel: "",
      minSpending: 0,
      maxSpending: 10000,
    });

  return (
    <div className="card">
      <div className="flex flex-wrap items-end gap-4">
        <div className="flex flex-col gap-1">
          <label className="text-xs text-gray-400">开始日期</label>
          <input
            type="date"
            value={filters.startDate}
            onChange={(e) => update({ startDate: e.target.value })}
            className="input py-1.5 text-sm"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs text-gray-400">结束日期</label>
          <input
            type="date"
            value={filters.endDate}
            onChange={(e) => update({ endDate: e.target.value })}
            className="input py-1.5 text-sm"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs text-gray-400">用户等级</label>
          <select
            value={filters.userLevel}
            onChange={(e) => update({ userLevel: e.target.value })}
            className="input py-1.5 text-sm"
          >
            {USER_LEVELS.map((l) => (
              <option key={l.value} value={l.value}>
                {l.label}
              </option>
            ))}
          </select>
        </div>
        <div className="flex flex-col gap-1 min-w-[160px]">
          <label className="text-xs text-gray-400">
            消费范围: {filters.minSpending} - {filters.maxSpending}
          </label>
          <div className="flex gap-2 items-center">
            <input
              type="range"
              min={0}
              max={50000}
              step={100}
              value={filters.minSpending}
              onChange={(e) => update({ minSpending: Number(e.target.value) })}
              className="w-full accent-primary-500"
            />
            <input
              type="range"
              min={0}
              max={50000}
              step={100}
              value={filters.maxSpending}
              onChange={(e) => update({ maxSpending: Number(e.target.value) })}
              className="w-full accent-primary-500"
            />
          </div>
        </div>
        <div className="flex gap-2 ml-auto">
          <button onClick={reset} className="btn-ghost px-4 py-1.5 text-sm">
            重置
          </button>
        </div>
      </div>
    </div>
  );
}
