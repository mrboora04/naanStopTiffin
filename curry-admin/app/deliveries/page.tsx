"use client";

import React, { useEffect, useState } from "react";
import { Map, CheckCircle2, Clock, RefreshCw, Pencil, X, Check } from "lucide-react";
import { getDeliveries, getMembers, updateDelivery } from "@/lib/api";
import type { Delivery, DeliveryStatus, Member } from "@/types";

const STATUS_OPTIONS: DeliveryStatus[] = ["scheduled", "out-for-delivery", "delivered", "failed", "skipped"];

export default function Deliveries() {
  const [deliveries, setDeliveries] = useState<Delivery[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editDraft, setEditDraft] = useState<Partial<Delivery>>({});
  const [saving, setSaving] = useState(false);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [d, m] = await Promise.all([getDeliveries(), getMembers()]);
      setDeliveries(d);
      setMembers(m);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load deliveries");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const memberName = (id: string) => members.find((m) => m.id === id)?.name ?? id;

  const handleStatusChange = async (delivery: Delivery, status: DeliveryStatus) => {
    try {
      const updated = await updateDelivery(delivery.id, { status });
      setDeliveries((prev) => prev.map((d) => (d.id === delivery.id ? updated : d)));
    } catch (e) {
      alert(e instanceof Error ? e.message : "Update failed");
    }
  };

  const handleSaveEdit = async () => {
    if (!editingId) return;
    setSaving(true);
    try {
      const updated = await updateDelivery(editingId, editDraft);
      setDeliveries((prev) => prev.map((d) => (d.id === editingId ? updated : d)));
      setEditingId(null);
    } catch (e) {
      alert(e instanceof Error ? e.message : "Save failed");
    } finally {
      setSaving(false);
    }
  };

  const statusStyle = (status: DeliveryStatus) => {
    const map: Record<DeliveryStatus, string> = {
      scheduled: "bg-blue-50 text-blue-700",
      "out-for-delivery": "bg-orange-50 text-orange-700",
      delivered: "bg-green-50 text-green-700",
      failed: "bg-red-50 text-red-700",
      skipped: "bg-gray-100 text-gray-500",
      pending: "bg-yellow-50 text-yellow-700",

    };
    return map[status] ?? "bg-gray-100 text-gray-600";
  };

  return (
    <div className="p-8 max-w-7xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">Daily Deliveries</h1>
        <div className="flex gap-3">
          <button
            onClick={load}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-600 font-medium transition-colors"
          >
            <RefreshCw size={16} /> Refresh
          </button>
          <button className="bg-orange-500 text-white px-6 py-3 rounded-full font-medium hover:bg-orange-600 transition-colors shadow-lg flex items-center gap-2">
            <Map size={20} /> Optimize Route
          </button>
        </div>
      </div>

      {error && <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl">{error}</div>}

      {loading ? (
        <div className="grid gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="bg-white p-6 rounded-2xl border border-gray-100 animate-pulse h-20" />
          ))}
        </div>
      ) : deliveries.length === 0 ? (
        <div className="text-center p-12 text-gray-400 font-medium bg-white rounded-2xl border border-gray-100">
          No deliveries found.
        </div>
      ) : (
        <div className="grid gap-4">
          {deliveries.map((delivery) => {
            const isEditing = editingId === delivery.id;
            return (
              <div
                key={delivery.id}
                className="bg-white p-6 rounded-2xl shadow-[0_4px_20px_rgb(0,0,0,0.03)] border border-gray-100 flex items-center justify-between group hover:shadow-md transition-all"
              >
                <div className="flex items-center gap-6">
                  <div className="w-12 h-12 rounded-full bg-orange-50 text-orange-600 flex items-center justify-center font-bold text-xl shrink-0">
                    {delivery.routeOrder}
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-900 text-lg">{memberName(delivery.memberId)}</h3>
                    {isEditing ? (
                      <div className="flex gap-2 mt-1">
                        <input
                          className="border rounded px-2 py-1 text-sm"
                          placeholder="Delivery time"
                          value={editDraft.deliveryTime ?? delivery.deliveryTime}
                          onChange={(e) => setEditDraft((p) => ({ ...p, deliveryTime: e.target.value }))}
                        />
                        <input
                          className="border rounded px-2 py-1 text-sm"
                          placeholder="Notes"
                          value={editDraft.notes ?? delivery.notes}
                          onChange={(e) => setEditDraft((p) => ({ ...p, notes: e.target.value }))}
                        />
                      </div>
                    ) : (
                      <p className="text-gray-500 flex items-center gap-1 text-sm mt-1">
                        <Clock size={14} /> {delivery.deliveryTime} &bull; {delivery.notes}
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  {isEditing ? (
                    <>
                      <select
                        className="border rounded px-2 py-1 text-sm"
                        value={editDraft.status ?? delivery.status}
                        onChange={(e) => setEditDraft((p) => ({ ...p, status: e.target.value as DeliveryStatus }))}
                      >
                        {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{s}</option>)}
                      </select>
                      <button disabled={saving} onClick={handleSaveEdit} className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors">
                        <Check size={18} />
                      </button>
                      <button onClick={() => setEditingId(null)} className="p-2 text-gray-400 hover:bg-gray-100 rounded-lg transition-colors">
                        <X size={18} />
                      </button>
                    </>
                  ) : (
                    <>
                      {/* Quick status toggle */}
                      {delivery.status !== "delivered" && delivery.status !== "failed" && (
                        <button
                          onClick={() => handleStatusChange(delivery, delivery.status === "scheduled" ? "out-for-delivery" : "delivered")}
                          className="p-2 text-green-500 hover:bg-green-50 rounded-lg transition-colors"
                          title="Advance status"
                        >
                          <CheckCircle2 size={20} />
                        </button>
                      )}
                      <span className={`px-4 py-2 rounded-xl text-sm font-bold flex items-center gap-2 ${statusStyle(delivery.status)}`}>
                        {delivery.status.replace("-", " ").toUpperCase()}
                      </span>
                      <button
                        onClick={() => { setEditingId(delivery.id); setEditDraft({}); }}
                        className="opacity-0 group-hover:opacity-100 p-2 text-blue-500 hover:bg-blue-50 rounded-lg transition-all"
                      >
                        <Pencil size={18} />
                      </button>
                    </>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}