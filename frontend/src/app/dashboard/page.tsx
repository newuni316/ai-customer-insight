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

  useEffect(() => {
    fetchOverview();
  }, [fetchOverview]);

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
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-white">数据仪表盘</h1>
        <button
          className="btn-ghost text-sm border border-[#1e1e2e]"
          onClick={fetchOverview}
        >
          刷新数据
        </button>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        <DataCard
          icon="👥"
          label="总用户数"
          value={overview?.total_users?.toLocaleString() ?? "0"}
        />
        <DataCard
          icon="📦"
          label="总订单数"
          value={overview?.total_orders?.toLocaleString() ?? "0"}
        />
        <DataCard
          icon="💰"
          label="总收入"
          value={formatCurrency(overview?.total_revenue ?? 0)}
        />
        <DataCard
          icon="📊"
          label="平均客单价"
          value={formatCurrency(overview?.avg_order_value ?? 0)}
        />
        <DataCard
          icon="🔥"
          label="活跃用户(30天)"
          value={overview?.active_users_30d?.toLocaleString() ?? "0"}
        />
      </div>

      {/* Filter Bar */}
      <div className="mb-6">
        <FilterBar filters={filters} onChange={setFilters} />
      </div>

      {/* Charts Row 1: Revenue + User Segmentation */}
      <div className="grid md:grid-cols-2 gap-6 mb-6">
        <RevenueChart />
        <UserSegmentationChart />
      </div>

      {/* Charts Row 2: Retention + Churn */}
      <div className="grid md:grid-cols-2 gap-6 mb-6">
        <RetentionChart />
        <ChurnChart />
      </div>

      {/* AI Insights */}
      <div className="mb-6">
        <AIInsightPanel />
      </div>

      {/* Orders Table */}
      <OrdersTable />
    </div>
  );
}
