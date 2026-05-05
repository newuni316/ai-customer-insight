"use client";

import { useState, useEffect } from "react";
import api from "@/lib/api";

interface Order {
  id: number | string;
  user_id?: number | string;
  user_email?: string;
  amount: number;
  product?: string;
  status: string;
  created_at?: string;
  date?: string;
}

const STATUS_LABELS: Record<string, { text: string; color: string }> = {
  completed: { text: "已完成", color: "bg-green-500/20 text-green-400" },
  refunded: { text: "已退款", color: "bg-yellow-500/20 text-yellow-400" },
  cancelled: { text: "已取消", color: "bg-red-500/20 text-red-400" },
  pending: { text: "待处理", color: "bg-gray-500/20 text-gray-400" },
};

const STATUS_FILTERS = [
  { value: "", label: "全部" },
  { value: "completed", label: "已完成" },
  { value: "refunded", label: "已退款" },
  { value: "cancelled", label: "已取消" },
];

export default function OrdersTable() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [statusFilter, setStatusFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const pageSize = 10;

  const fetchData = async (p: number, status: string) => {
    setLoading(true);
    setError("");
    try {
      const params: Record<string, string | number> = {
        page: p,
        page_size: pageSize,
      };
      if (status) params.status = status;
      const res = await api.get("/api/orders", { params });
      const data = res.data;
      if (Array.isArray(data)) {
        setOrders(data);
        setTotal(data.length >= pageSize ? p * pageSize + 1 : p * pageSize);
      } else {
        setOrders(data.items ?? data.orders ?? []);
        setTotal(data.total ?? 0);
      }
    } catch {
      setError("加载失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData(page, statusFilter);
  }, [page, statusFilter]);

  const handleStatusChange = (status: string) => {
    setStatusFilter(status);
    setPage(1);
  };

  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const formatDate = (order: Order) => {
    const d = order.created_at ?? order.date ?? "";
    if (!d) return "-";
    return new Date(d).toLocaleDateString("zh-CN");
  };

  const formatAmount = (amount: number) =>
    `¥${amount.toLocaleString("zh-CN", { minimumFractionDigits: 2 })}`;

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">订单列表</h3>
        <div className="flex gap-1">
          {STATUS_FILTERS.map((s) => (
            <button
              key={s.value}
              onClick={() => handleStatusChange(s.value)}
              className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                statusFilter === s.value
                  ? "bg-primary-600 text-white"
                  : "text-gray-400 hover:text-white hover:bg-white/5"
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-10 rounded bg-white/5 animate-pulse" />
          ))}
        </div>
      ) : error ? (
        <div className="flex flex-col items-center gap-2 text-gray-500 py-8">
          <span>{error}</span>
          <button
            onClick={() => fetchData(page, statusFilter)}
            className="btn-ghost text-sm"
          >
            重试
          </button>
        </div>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#1e1e2e]">
                  <th className="text-left py-3 px-2 text-gray-400 font-medium">
                    订单号
                  </th>
                  <th className="text-left py-3 px-2 text-gray-400 font-medium">
                    用户
                  </th>
                  <th className="text-right py-3 px-2 text-gray-400 font-medium">
                    金额
                  </th>
                  <th className="text-left py-3 px-2 text-gray-400 font-medium">
                    产品
                  </th>
                  <th className="text-left py-3 px-2 text-gray-400 font-medium">
                    状态
                  </th>
                  <th className="text-right py-3 px-2 text-gray-400 font-medium">
                    日期
                  </th>
                </tr>
              </thead>
              <tbody>
                {orders.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-gray-500">
                      暂无订单
                    </td>
                  </tr>
                ) : (
                  orders.map((order) => {
                    const statusInfo = STATUS_LABELS[order.status] ?? {
                      text: order.status,
                      color: "bg-gray-500/20 text-gray-400",
                    };
                    return (
                      <tr
                        key={order.id}
                        className="border-b border-[#1e1e2e]/50 hover:bg-white/[0.02]"
                      >
                        <td className="py-3 px-2 text-gray-300">#{order.id}</td>
                        <td className="py-3 px-2 text-gray-300">
                          {order.user_email ?? order.user_id ?? "-"}
                        </td>
                        <td className="py-3 px-2 text-right text-white font-medium">
                          {formatAmount(order.amount)}
                        </td>
                        <td className="py-3 px-2 text-gray-300">
                          {order.product ?? "-"}
                        </td>
                        <td className="py-3 px-2">
                          <span
                            className={`px-2 py-0.5 rounded-full text-xs ${statusInfo.color}`}
                          >
                            {statusInfo.text}
                          </span>
                        </td>
                        <td className="py-3 px-2 text-right text-gray-400">
                          {formatDate(order)}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          <div className="flex items-center justify-between mt-4">
            <span className="text-sm text-gray-500">共 {total} 条</span>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="btn-ghost px-3 py-1 text-sm disabled:opacity-30"
              >
                上一页
              </button>
              <span className="text-sm text-gray-400 py-1">
                {page} / {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="btn-ghost px-3 py-1 text-sm disabled:opacity-30"
              >
                下一页
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
