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

interface RetentionData {
  month: string;
  rate: number;
}

export default function RetentionChart() {
  const [data, setData] = useState<RetentionData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchData = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await api.get("/api/metrics/retention");
      const raw = res.data;
      if (Array.isArray(raw)) {
        setData(
          raw.map((item: Record<string, unknown>) => ({
            month: String(item.month ?? item.date ?? item.period ?? ""),
            rate: Number(item.rate ?? item.retention_rate ?? item.retention ?? 0),
          }))
        );
      }
    } catch {
      setError("加载失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-white mb-4">留存率趋势</h3>

      {loading ? (
        <div className="h-64 flex items-center justify-center text-gray-500">
          加载中...
        </div>
      ) : error ? (
        <div className="h-64 flex flex-col items-center justify-center gap-2 text-gray-500">
          <span>{error}</span>
          <button onClick={fetchData} className="btn-ghost text-sm">
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
            <XAxis dataKey="month" stroke="#666" tick={{ fontSize: 12 }} />
            <YAxis
              stroke="#666"
              tick={{ fontSize: 12 }}
              domain={[0, 100]}
              tickFormatter={(v) => `${v}%`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#13131a",
                border: "1px solid #1e1e2e",
                borderRadius: "8px",
                color: "#e0e0e0",
              }}
              formatter={(value: number) => [`${value.toFixed(1)}%`, "留存率"]}
            />
            <Line
              type="monotone"
              dataKey="rate"
              stroke="#06b6d4"
              strokeWidth={2}
              dot={{ r: 3, fill: "#06b6d4" }}
              activeDot={{ r: 5 }}
              name="留存率"
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
