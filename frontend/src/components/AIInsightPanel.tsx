"use client";

import { useState, useEffect } from "react";
import api from "@/lib/api";

interface Insight {
  icon: string;
  text: string;
  severity: "info" | "warning" | "critical";
}

const SEVERITY_STYLES: Record<string, string> = {
  info: "border-accent-500/30 bg-accent-500/5",
  warning: "border-yellow-500/30 bg-yellow-500/5",
  critical: "border-red-500/30 bg-red-500/5",
};

function buildInsights(data: Record<string, unknown>): Insight[] {
  const insights: Insight[] = [];
  const churn = data?.churn_stats ?? data?.churn_distribution;
  const userDist = data?.user_type_distribution ?? data?.user_distribution;
  const recommendations = data?.recommendations;

  // Churn insights
  if (churn && typeof churn === "object") {
    const churnObj = churn as Record<string, number>;
    const high = churnObj.high ?? churnObj["高风险"] ?? 0;
    const total = Object.values(churnObj).reduce((s, v) => s + (Number(v) || 0), 0);
    if (total > 0 && high > 0) {
      const pct = ((high / total) * 100).toFixed(0);
      insights.push({
        icon: "\u{1F534}",
        text: `${pct}% 的用户存在高流失风险`,
        severity: "critical",
      });
    }
  }

  // User distribution insights
  if (userDist && typeof userDist === "object") {
    const dist = userDist as Record<string, number>;
    const highVal = dist.high ?? dist["高价值用户"] ?? 0;
    const total = Object.values(dist).reduce((s, v) => s + (Number(v) || 0), 0);
    if (total > 0 && highVal > 0) {
      const pct = ((highVal / total) * 100).toFixed(0);
      insights.push({
        icon: "\u{1F7E2}",
        text: `高价值用户占比 ${pct}%`,
        severity: "info",
      });
    }
  }

  // Recommendations
  if (Array.isArray(recommendations)) {
    for (const rec of recommendations.slice(0, 3)) {
      insights.push({
        icon: "\u{1F4A1}",
        text: String(rec),
        severity: "warning",
      });
    }
  } else if (typeof recommendations === "string" && recommendations) {
    insights.push({
      icon: "\u{1F4A1}",
      text: recommendations,
      severity: "warning",
    });
  }

  // Fallback if no insights built
  if (insights.length === 0) {
    insights.push({
      icon: "\u{1F4CA}",
      text: "数据加载中，请稍后查看洞察",
      severity: "info",
    });
  }

  return insights.slice(0, 5);
}

export default function AIInsightPanel() {
  const [insights, setInsights] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchData = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await api.get("/api/decisions/insights");
      setInsights(buildInsights(res.data));
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
      <h3 className="text-lg font-semibold text-white mb-4">AI 洞察</h3>

      {loading ? (
        <div className="flex gap-3 overflow-x-auto pb-2">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="min-w-[220px] h-20 rounded-lg bg-white/5 animate-pulse"
            />
          ))}
        </div>
      ) : error ? (
        <div className="flex flex-col items-center gap-2 text-gray-500 py-4">
          <span>{error}</span>
          <button onClick={fetchData} className="btn-ghost text-sm">
            重试
          </button>
        </div>
      ) : (
        <div className="flex gap-3 overflow-x-auto pb-2">
          {insights.map((insight, i) => (
            <div
              key={i}
              className={`min-w-[220px] flex-shrink-0 rounded-lg border p-4 ${SEVERITY_STYLES[insight.severity]}`}
            >
              <span className="text-xl mr-2">{insight.icon}</span>
              <span className="text-sm text-gray-200">{insight.text}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
