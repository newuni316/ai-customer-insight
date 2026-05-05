"use client";

import { useState, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import api from "@/lib/api";

interface RevenueData {
  date: string;
  revenue: number;
}

const PERIODS = [
  { key: "daily", label: "日" },
  { key: "weekly", label: "周" },
  { key: "monthly", label: "月" },
] as const;

export default function RevenueChart() {
  const [data, setData] = useState<RevenueData[]>([]);
  const [period, setPeriod] = useState<"daily" | "weekly" | "monthly">("daily");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchData = async (p: string) => {
    setLoading(true);
    setError("");
    try {
      const res = await api.get(`/api/metrics/revenue?period=${p}`);
      setData(res.data);
    } catch {
      setError("加载失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData(period);
  }, [period]);

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">收入趋势</h3>
        <div className="flex gap-1">
          {PERIODS.map((p) => (
            <button
              key={p.key}
              onClick={() => setPeriod(p.key)}
              className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                period === p.key
                  ? "bg-primary-600 text-white"
                  : "text-gray-400 hover:text-white hover:bg-white/5"
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="h-64 flex items-center justify-center text-gray-500">
          加载中...
        </div>
      ) : error ? (
        <div className="h-64 flex flex-col items-center justify-center gap-2 text-gray-500">
          <span>{error}</span>
          <button onClick={() => fetchData(period)} className="btn-ghost text-sm">
            重试
          </button>
        </div>
      ) : data.length === 0 ? (
        <div className="h-64 flex items-center justify-center text-gray-500">
          暂无数据
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
            <XAxis dataKey="date" stroke="#666" tick={{ fontSize: 12 }} />
            <YAxis stroke="#666" tick={{ fontSize: 12 }} />
            <Tooltip
              contentStyle={{
                backgroundColor: "#13131a",
                border: "1px solid #1e1e2e",
                borderRadius: "8px",
                color: "#e0e0e0",
              }}
            />
            <Line
              type="monotone"
              dataKey="revenue"
              stroke="#8b5cf6"
              strokeWidth={2}
              dot={{ r: 3, fill: "#8b5cf6" }}
              activeDot={{ r: 5 }}
              name="收入"
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
