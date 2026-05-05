"use client";

import { useState, useEffect } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import api from "@/lib/api";

interface ChurnData {
  level: string;
  count: number;
}

const LEVEL_COLORS: Record<string, string> = {
  low: "#22c55e",
  medium: "#eab308",
  high: "#ef4444",
  低风险: "#22c55e",
  中风险: "#eab308",
  高风险: "#ef4444",
};

export default function ChurnChart() {
  const [data, setData] = useState<ChurnData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchData = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await api.get("/api/decisions/insights");
      const raw = res.data;
      // Expect churn_stats with distribution
      const churn = raw?.churn_stats ?? raw?.churn_distribution ?? raw;
      if (Array.isArray(churn)) {
        setData(
          churn.map((item: Record<string, unknown>) => ({
            level: String(item.level ?? item.risk ?? item.name ?? "未知"),
            count: Number(item.count ?? item.total ?? item.value ?? 0),
          }))
        );
      } else if (churn && typeof churn === "object") {
        const labelMap: Record<string, string> = {
          low: "低风险",
          medium: "中风险",
          high: "高风险",
        };
        setData(
          Object.entries(churn)
            .filter(([, v]) => typeof v === "number")
            .map(([k, v]) => ({
              level: labelMap[k] ?? k,
              count: Number(v),
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
      <h3 className="text-lg font-semibold text-white mb-4">流失风险分布</h3>

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
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
            <XAxis dataKey="level" stroke="#666" tick={{ fontSize: 12 }} />
            <YAxis stroke="#666" tick={{ fontSize: 12 }} />
            <Tooltip
              contentStyle={{
                backgroundColor: "#13131a",
                border: "1px solid #1e1e2e",
                borderRadius: "8px",
                color: "#e0e0e0",
              }}
            />
            <Bar dataKey="count" name="用户数" radius={[4, 4, 0, 0]}>
              {data.map((entry, index) => (
                <Cell
                  key={index}
                  fill={LEVEL_COLORS[entry.level] ?? "#8b5cf6"}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
