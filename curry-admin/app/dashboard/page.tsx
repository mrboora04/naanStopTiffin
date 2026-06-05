"use client";

import React, { useEffect, useState, useCallback } from "react";
import { Users, Truck, DollarSign, ClipboardList, RefreshCw, ChevronUp, ChevronDown, ChevronsUpDown } from "lucide-react";
import { toast } from "sonner";
import { getMembers, getDeliveries, getPayments, getTrialRequests } from "@/lib/api";
import type { Member, Delivery, Payment, TrialRequest } from "@/types";
import StatCard from "@/components/StatCard";
import { StatCardSkeleton, TableSkeleton, EmptyState } from "@/components/ui";
import { formatStatus, formatDate } from "@/lib/formatters";

type SortKey = "routeOrder" | "deliveryTime" | "status";
type SortDir = "asc" | "desc";
type StatusFilter = "all" | "scheduled" | "out-for-delivery" | "delivered" | "failed";

function StatusBadge({ status }: { status: string }) {
  const cls =
    status === "delivered"        ? "badge-active" :
    status === "out-for-delivery" ? "badge-warning" :
    status === "failed"           ? "badge-error"   : "badge-info";
  return (
    <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${cls}`}>
      {formatStatus(status)}
    </span>
  );
}

type SortIconProps = { col: SortKey; active: SortKey; dir: SortDir };
function SortIcon({ col, active, dir }: SortIconProps) {
  if (active !== col) return <ChevronsUpDown className="w-3.5 h-3.5 text-gray-500 inline ml-1" />;
  return dir === "asc"
    ? <ChevronUp className="w-3.5 h-3.5 text-orange-700 inline ml-1" />
    : <ChevronDown className="w-3.5 h-3.5 text-orange-700 inline ml-1" />;
}

export default function Dashboard() {
  const [members,        setMembers]        = useState<Member[]>([]);
  const [deliveries,     setDeliveries]     = useState<Delivery[]>([]);
  const [payments,       setPayments]       = useState<Payment[]>([]);
  const [trialRequests,  setTrialRequests]  = useState<TrialRequest[]>([]);
  const [loading,        setLoading]        = useState(true);
  const [error,          setError]          = useState<string | null>(null);

  // Table controls
  const [sortKey,        setSortKey]        = useState<SortKey>("routeOrder");
  const [sortDir,        setSortDir]        = useState<SortDir>("asc");
  const [statusFilter,   setStatusFilter]   = useState<StatusFilter>("all");

  const fetchAll = useCallback(async (showToast = false) => {
    setLoading(true);
    setError(null);
    try {
      const [m, d, p, tr] = await Promise.all([
        getMembers(),
        getDeliveries(),
        getPayments(),
        getTrialRequests(),
      ]);
      setMembers(m);
      setDeliveries(d);
      setPayments(p);
      setTrialRequests(tr);
      if (showToast) toast.success("Dashboard refreshed");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to load dashboard data";
      setError(msg);
      if (showToast) toast.error(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  // KPI values
  const activeMembers    = members.filter((m) => m.memberStatus === "active").length;
  const todayDeliveries  = deliveries.filter((d) => d.status === "scheduled" || d.status === "out-for-delivery").length;
  const totalRevenue     = payments.filter((p) => p.status === "success").reduce((acc, p) => acc + p.amount, 0);
  const pendingRequests  = trialRequests.filter((r) => r.status === "pending").length;

  // Sorting helper
  function toggleSort(key: SortKey) {
    if (sortKey === key) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else { setSortKey(key); setSortDir("asc"); }
  }

  // Filtered + sorted deliveries
  const visibleDeliveries = [...deliveries]
    .filter((d) => statusFilter === "all" || d.status === statusFilter)
    .sort((a, b) => {
      let av: string | number = 0, bv: string | number = 0;
      if (sortKey === "routeOrder")   { av = a.routeOrder ?? 0; bv = b.routeOrder ?? 0; }
      if (sortKey === "deliveryTime") { av = a.deliveryTime ?? ""; bv = b.deliveryTime ?? ""; }
      if (sortKey === "status")       { av = a.status ?? ""; bv = b.status ?? ""; }
      if (av < bv) return sortDir === "asc" ? -1 : 1;
      if (av > bv) return sortDir === "asc" ? 1 : -1;
      return 0;
    });

  const statusFilters: StatusFilter[] = ["all", "scheduled", "out-for-delivery", "delivered", "failed"];

  return (
    <div className="p-4 lg:p-8 max-w-7xl mx-auto animate-in fade-in zoom-in duration-300">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl lg:text-4xl font-extrabold text-gray-900 tracking-tight">Overview</h1>
          <p className="text-sm text-gray-500 mt-1">Live snapshot of your tiffin service</p>
        </div>
        <button
          onClick={() => fetchAll(true)}
          disabled={loading}
          aria-label="Refresh data"
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium transition-colors disabled:opacity-50"
        >
          <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
          <span className="hidden sm:inline">Refresh</span>
        </button>
      </div>

      {/* Error banner */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl font-medium text-sm" role="alert">
          {error}
        </div>
      )}

      {/* KPI Cards */}
      {loading ? (
        <div className="mb-10">
          <StatCardSkeleton />
        </div>
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6 mb-10">
          <StatCard
            label="Active Members"
            value={activeMembers}
            icon={<Users size={22} />}
            trend={{ value: 0, direction: "flat", label: "vs last week" }}
          />
          <StatCard
            label="Deliveries Today"
            value={todayDeliveries}
            icon={<Truck size={22} />}
            highlight={todayDeliveries > 0}
          />
          <StatCard
            label="Revenue Collected"
            value={`$${totalRevenue.toLocaleString("en-CA")}`}
            icon={<DollarSign size={22} />}
          />
          <StatCard
            label="Pending Requests"
            value={pendingRequests}
            icon={<ClipboardList size={22} />}
            highlight={pendingRequests > 0}
          />
        </div>
      )}

      {/* Deliveries Table */}
      <div className="bg-white rounded-2xl shadow-[0_4px_24px_rgb(0,0,0,0.05)] border border-gray-100 overflow-hidden">
        {/* Table header */}
        <div className="p-4 lg:p-6 border-b border-gray-100 flex flex-col sm:flex-row sm:items-center gap-3">
          <h2 className="text-lg font-bold text-gray-900 mr-auto">Today's Deliveries</h2>

          {/* Status filter chips */}
          <div className="flex items-center gap-1.5 flex-wrap">
            {statusFilters.map((f) => (
              <button
                key={f}
                onClick={() => setStatusFilter(f)}
                className={`px-3 py-1 rounded-full text-xs font-semibold capitalize transition-colors ${
                  statusFilter === f
                    ? "bg-orange-500 text-white"
                    : "bg-gray-100 text-gray-500 hover:bg-gray-200"
                }`}
              >
                {f === "all" ? "All" : formatStatus(f)}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <TableSkeleton rows={5} cols={5} />
        ) : visibleDeliveries.length === 0 ? (
          <EmptyState type={statusFilter !== "all" ? "no-results" : "no-deliveries"} />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50/70 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  <th
                    className="px-4 lg:px-6 py-3 cursor-pointer select-none hover:text-gray-800 transition-colors"
                    onClick={() => toggleSort("routeOrder")}
                  >
                    Route # <SortIcon col="routeOrder" active={sortKey} dir={sortDir} />
                  </th>
                  <th className="px-4 lg:px-6 py-3">Member</th>
                  <th className="px-4 lg:px-6 py-3">Meal</th>
                  <th
                    className="px-4 lg:px-6 py-3 cursor-pointer select-none hover:text-gray-800 transition-colors"
                    onClick={() => toggleSort("deliveryTime")}
                  >
                    Time <SortIcon col="deliveryTime" active={sortKey} dir={sortDir} />
                  </th>
                  <th
                    className="px-4 lg:px-6 py-3 cursor-pointer select-none hover:text-gray-800 transition-colors"
                    onClick={() => toggleSort("status")}
                  >
                    Status <SortIcon col="status" active={sortKey} dir={sortDir} />
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {visibleDeliveries.map((d) => {
                  const member = members.find((m) => m.id === d.memberId);
                  return (
                    <tr key={d.id} className="hover:bg-gray-50/60 transition-colors group">
                      <td className="px-4 lg:px-6 py-4 font-bold text-gray-900">#{d.routeOrder}</td>
                      <td className="px-4 lg:px-6 py-4 font-semibold text-gray-900">{member?.name ?? d.memberId}</td>
                      <td className="px-4 lg:px-6 py-4 capitalize text-gray-600">{d.mealType}</td>
                      <td className="px-4 lg:px-6 py-4 text-gray-600">{d.deliveryTime}</td>
                      <td className="px-4 lg:px-6 py-4">
                        <StatusBadge status={d.status} />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}