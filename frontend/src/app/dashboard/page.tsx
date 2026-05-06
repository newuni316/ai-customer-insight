"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import DataCard from "@/components/DataCard";
import RevenueChart from "@/components/RevenueChart";
import UserSegmentationChart from "@/components/UserSegmentationChart";
import ChurnChart from "@/components/ChurnChart";
import RetentionChart from "@/components/RetentionChart";
import AIInsightPanel from "@/components/AIInsightPanel";
import FilterBar, { type FilterState } from "@/components/FilterBar";
import OrdersTable from "@/components/OrdersTable";
import DashboardSkeleton from "@/components/DashboardSkeleton";

interface Overview {
  total_users: number;
  total_orders: number;
  total_revenue: number;
  avg_order_value: number;
  active_users_30d: number;
}

interface User {
  email: string;
  username?: string;
}

// Mock trend data — replace with real API when historical metrics are available
const MOCK_TRENDS = {
  total_users: { value: 12.5, up: true },
  total_orders: { value: 8.3, up: true },
  total_revenue: { value: 3.2, up: false },
  avg_order_value: { value: 5.7, up: true },
  active_users_30d: { value: 15.1, up: true },
};

const DEFAULT_FILTERS: FilterState = {
  startDate: "",
  endDate: "",
  userLevel: "",
  minSpending: 0,
  maxSpending: 10000,
};

export default function DashboardPage() {
  const router = useRouter();
  const [overview, setOverview] = useState<Overview | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS);

  const fetchOverview = useCallback(async () => {
    try {
      setError(null);
      const { data } = await api.get("/api/metrics/overview");
      setOverview(data);
    } catch (err: any) {
      if (err.response?.status === 401) {
        router.push("/login");
        return;
      }
      setError(err.message || "加载失败");
    } finally {
      setLoading(false);
    }
  }, [router]);

  const fetchUser = useCallback(async () => {
    try {
      const { data } = await api.get("/api/auth/me");
      setUser(data);
    } catch {
      // Non-critical — silently ignore
    }
  }, []);

  useEffect(() => {
    fetchOverview();
    fetchUser();
  }, [fetchOverview, fetchUser]);

  if (loading) return <DashboardSkeleton />;

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="card text-center max-w-md">
          <p className="text-red-400 mb-4">{error}</p>
          <button className="btn-primary" onClick={fetchOverview}>
            重试
          </button>
        </div>
      </div>
    );
  }

  const formatCurrency = (v: number) =>
    `¥${v.toLocaleString("zh-CN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  return (
    <div className="max-w-7xl mx-auto px-6 pt-24 pb-12">
      {/* Welcome Banner */}
      <div className="card bg-gradient-to-r from-indigo-600/20 to-purple-600/20 border-indigo-500/30 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white mb-1">
              欢迎回来{user?.email ? `，${user.email}` : ""}
            </h1>
            <p className="text-gray-400 text-sm">
              这是您的客户洞察仪表盘，以下是最新数据概览。
            </p>
          </div>
          <button
            className="btn-ghost text-sm border border-[#1e1e2e]"
            onClick={fetchOverview}
          >
            刷新数据
          </button>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="flex flex-wrap gap-3 mb-6">
        {[
          { label: "上传 CSV", icon: "📄", href: "#" },
          { label: "查看分析", icon: "📊", href: "#" },
          { label: "导出报告", icon: "📥", href: "#" },
        ].map((action) => (
          <a
            key={action.label}
            href={action.href}
            className="btn-ghost text-sm border border-[#1e1e2e] flex items-center gap-2 hover:border-indigo-500/50 hover:bg-indigo-500/5 transition-colors"
          >
            <span>{action.icon}</span>
            {action.label}
          </a>
        ))}
      </div>

      {/* Stat Cards with Trends */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        <DataCard
          icon="👥"
          label="总用户数"
          value={overview?.total_users?.toLocaleString() ?? "0"}
          trend={MOCK_TRENDS.total_users}
        />
        <DataCard
          icon="📦"
          label="总订单数"
          value={overview?.total_orders?.toLocaleString() ?? "0"}
          trend={MOCK_TRENDS.total_orders}
        />
        <DataCard
          icon="💰"
          label="总收入"
          value={formatCurrency(overview?.total_revenue ?? 0)}
          trend={MOCK_TRENDS.total_revenue}
        />
        <DataCard
          icon="📊"
          label="平均客单价"
          value={formatCurrency(overview?.avg_order_value ?? 0)}
          trend={MOCK_TRENDS.avg_order_value}
        />
        <DataCard
          icon="🔥"
          label="活跃用户(30天)"
          value={overview?.active_users_30d?.toLocaleString() ?? "0"}
          trend={MOCK_TRENDS.active_users_30d}
        />
      </div>

      {/* Filter Bar */}
      <div className="mb-6">
        <FilterBar filters={filters} onChange={setFilters} />
      </div>

      {/* Charts Row 1: Revenue + User Segmentation */}
      <div className="grid md:grid-cols-2 gap-6 mb-6">
        <div>
          <h2 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
            <span className="text-indigo-400">📈</span> 收入趋势
          </h2>
          <RevenueChart />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
            <span className="text-purple-400">🎯</span> 用户分层
          </h2>
          <UserSegmentationChart />
        </div>
      </div>

      {/* Charts Row 2: Retention + Churn */}
      <div className="grid md:grid-cols-2 gap-6 mb-6">
        <div>
          <h2 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
            <span className="text-green-400">🔄</span> 留存分析
          </h2>
          <RetentionChart />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
            <span className="text-red-400">⚠️</span> 流失风险
          </h2>
          <ChurnChart />
        </div>
      </div>

      {/* AI Insights */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
          <span className="text-yellow-400">🤖</span> AI 洞察
        </h2>
        <AIInsightPanel />
      </div>

      {/* Orders Table */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
          <span className="text-cyan-400">📋</span> 最近订单
        </h2>
        <OrdersTable />
      </div>
    </div>
  );
}
