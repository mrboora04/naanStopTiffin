"use client";

import React, { useEffect, useState } from "react";
import { Users, Truck, DollarSign, ClipboardList, RefreshCw } from "lucide-react";
import { getMembers, getDeliveries, getPayments, getTrialRequests } from "@/lib/api";
import type { Member, Delivery, Payment, TrialRequest } from "@/types";

export default function Dashboard() {
  const [members, setMembers] = useState<Member[]>([]);
  const [deliveries, setDeliveries] = useState<Delivery[]>([]);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [trialRequests, setTrialRequests] = useState<TrialRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAll = async () => {
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
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  const activeMembers = members.filter((m) => m.memberStatus === "active").length;
  const todayDeliveries = deliveries.filter((d) => d.status === "scheduled" || d.status === "out-for-delivery").length;
  const totalRevenue = payments.filter((p) => p.status === "success").reduce((acc, p) => acc + p.amount, 0);
  const pendingRequests = trialRequests.filter((r) => r.status === "pending").length;

  const stats = [
    { label: "Active Members", value: activeMembers, icon: Users, bg: "bg-blue-50", color: "text-blue-600" },
    { label: "Deliveries Today", value: todayDeliveries, icon: Truck, bg: "bg-orange-50", color: "text-orange-600" },
    { label: "Revenue Collected", value: `$${totalRevenue.toLocaleString()}`, icon: DollarSign, bg: "bg-green-50", color: "text-green-600" },
    { label: "Pending Requests", value: pendingRequests, icon: ClipboardList, bg: "bg-purple-50", color: "text-purple-600" },
  ];

  if (loading) {
    return (
      <div className="p-8 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-white rounded-2xl p-6 border border-gray-100 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-4" />
              <div className="h-10 bg-gray-200 rounded w-1/3" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto animate-in fade-in zoom-in duration-500">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">Overview</h1>
        <button
          onClick={fetchAll}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-600 font-medium transition-colors"
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl font-medium">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div
              key={stat.label}
              className="bg-white rounded-2xl p-6 shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-gray-100 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-gray-500 font-medium">{stat.label}</h3>
                <div className={`p-3 ${stat.bg} ${stat.color} rounded-xl`}>
                  <Icon size={24} />
                </div>
              </div>
              <p className="text-4xl font-black text-gray-900">{stat.value}</p>
            </div>
          );
        })}
      </div>

      {/* Recent Deliveries */}
      <div className="bg-white rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-gray-100 overflow-hidden">
        <div className="p-6 border-b border-gray-100">
          <h2 className="text-xl font-bold text-gray-900">Today's Deliveries</h2>
        </div>
        {deliveries.length === 0 ? (
          <div className="p-12 text-center text-gray-400 font-medium">No deliveries today.</div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50/50 text-left text-sm font-semibold text-gray-500 uppercase tracking-wider">
                <th className="px-6 py-4">Route #</th>
                <th className="px-6 py-4">Member</th>
                <th className="px-6 py-4">Meal</th>
                <th className="px-6 py-4">Time</th>
                <th className="px-6 py-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {deliveries.map((d) => {
                const member = members.find((m) => m.id === d.memberId);
                return (
                  <tr key={d.id} className="hover:bg-gray-50/50 transition-colors">
                    <td className="px-6 py-4 font-bold text-gray-900">#{d.routeOrder}</td>
                    <td className="px-6 py-4 font-semibold text-gray-900">{member?.name ?? d.memberId}</td>
                    <td className="px-6 py-4 capitalize text-gray-600">{d.mealType}</td>
                    <td className="px-6 py-4 text-gray-600">{d.deliveryTime}</td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${
                        d.status === "delivered" ? "bg-green-100 text-green-700" :
                        d.status === "out-for-delivery" ? "bg-orange-100 text-orange-700" :
                        d.status === "failed" ? "bg-red-100 text-red-700" :
                        "bg-blue-100 text-blue-700"
                      }`}>
                        {d.status.replace("-", " ")}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}