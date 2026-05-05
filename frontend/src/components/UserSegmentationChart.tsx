"use client";

import { useState, useEffect } from "react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import api from "@/lib/api";

interface SegmentData {
  name: string;
  value: number;
}

const COLORS: Record<string, string> = {
  高价值用户: "#22c55e",
  "High Value": "#22c55e",
  中价值用户: "#eab308",
  "Medium Value": "#eab308",
  低价值用户: "#ef4444",
  "Low Value": "#ef4444",
};

const FALLBACK_COLORS = ["#22c55e", "#eab308", "#ef4444"];

export default function UserSegmentationChart() {
  const [data, setData] = useState<SegmentData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchData = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await api.get("/api/metrics/conversion");
      const raw = res.data;
      // Normalize: expect array of {name, value} or {level, count}
      if (Array.isArray(raw)) {
        setData(
          raw.map((item: Record<string, unknown>) => ({
            name: String(item.name ?? item.level ?? item.user_level ?? "未知"),
            value: Number(item.value ?? item.count ?? item.total ?? 0),
          }))
        );
      } else if (raw && typeof raw === "object") {
        // Object form: {high: N, medium: N, low: N}
        const labelMap: Record<string, string> = {
          high: "高价值用户",
          medium: "中价值用户",
          low: "低价值用户",
        };
        setData(
          Object.entries(raw).map(([k, v]) => ({
            name: labelMap[k] ?? k,
            value: Number(v),
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

  const getColor = (name: string, index: number) =>
    COLORS[name] ?? FALLBACK_COLORS[index % FALLBACK_COLORS.length];

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-white mb-4">用户分层</h3>

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
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={100}
              paddingAngle={3}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={index} fill={getColor(entry.name, index)} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: "#13131a",
                border: "1px solid #1e1e2e",
                borderRadius: "8px",
                color: "#e0e0e0",
              }}
              formatter={(value: number, name: string) => {
                const total = data.reduce((s, d) => s + d.value, 0);
                const pct = total > 0 ? ((value / total) * 100).toFixed(1) : "0";
                return [`${value} (${pct}%)`, name];
              }}
            />
            <Legend
              wrapperStyle={{ color: "#999", fontSize: "12px" }}
            />
          </PieChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
