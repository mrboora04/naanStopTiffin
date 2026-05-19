"use client";

import React, { useEffect, useState } from "react";
import { Plus, Check, X, Trash2, Pencil, RefreshCw } from "lucide-react";
import { getPricingPlans, createPricingPlan, updatePricingPlan, deletePricingPlan } from "@/lib/api";
import type { PricingPlan } from "@/types";

const EMPTY_PLAN: Omit<PricingPlan, "id"> = {
  name: "", type: "monthly", dietaryType: "veg", price: 0, features: [], isActive: true,
};

export default function Pricing() {
  const [plans, setPlans] = useState<PricingPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAdd, setShowAdd] = useState(false);
  const [newPlan, setNewPlan] = useState(EMPTY_PLAN);
  const [newFeature, setNewFeature] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editDraft, setEditDraft] = useState<Partial<PricingPlan>>({});
  const [saving, setSaving] = useState(false);

  const load = async () => {
    setLoading(true);
    setError(null);
    try { setPlans(await getPricingPlans()); }
    catch (e) { setError(e instanceof Error ? e.message : "Failed to load plans"); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleAdd = async () => {
    setSaving(true);
    try {
      const created = await createPricingPlan(newPlan);
      setPlans((p) => [...p, created]);
      setShowAdd(false);
      setNewPlan(EMPTY_PLAN);
      setNewFeature("");
    } catch (e) { alert(e instanceof Error ? e.message : "Create failed"); }
    finally { setSaving(false); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this pricing plan?")) return;
    try {
      await deletePricingPlan(id);
      setPlans((p) => p.filter((pl) => pl.id !== id));
    } catch (e) { alert(e instanceof Error ? e.message : "Delete failed"); }
  };

  const handleSaveEdit = async () => {
    if (!editingId) return;
    setSaving(true);
    try {
      const updated = await updatePricingPlan(editingId, editDraft);
      setPlans((p) => p.map((pl) => (pl.id === editingId ? updated : pl)));
      setEditingId(null);
    } catch (e) { alert(e instanceof Error ? e.message : "Save failed"); }
    finally { setSaving(false); }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex justify-between items-center mb-8 mt-4">
        <div>
          <h1 className="text-4xl font-black text-gray-900 tracking-tight">Pricing Plans</h1>
          <p className="text-gray-500 mt-2">Manage subscription tiers available to your customers.</p>
        </div>
        <div className="flex gap-3">
          <button onClick={load} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-600 font-medium transition-colors">
            <RefreshCw size={16} /> Refresh
          </button>
          <button
            onClick={() => setShowAdd(true)}
            className="bg-black text-white px-6 py-3 rounded-full font-medium hover:bg-gray-800 transition-colors shadow-lg flex items-center gap-2"
          >
            <Plus size={20} /> New Plan
          </button>
        </div>
      </div>

      {error && <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl">{error}</div>}

      {/* Add Plan Form */}
      {showAdd && (
        <div className="mb-8 bg-white rounded-2xl p-6 border border-gray-200 shadow-lg">
          <h2 className="font-bold text-lg mb-4">New Pricing Plan</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Name</label>
              <input className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:ring-2 focus:ring-black outline-none" value={newPlan.name} onChange={(e) => setNewPlan((p) => ({ ...p, name: e.target.value }))} />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Price ($)</label>
              <input type="number" className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:ring-2 focus:ring-black outline-none" value={newPlan.price} onChange={(e) => setNewPlan((p) => ({ ...p, price: Number(e.target.value) }))} />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Type</label>
              <select className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm" value={newPlan.type} onChange={(e) => setNewPlan((p) => ({ ...p, type: e.target.value as PricingPlan["type"] }))}>
                {["daily", "weekly", "monthly"].map((t) => <option key={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Dietary</label>
              <select className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm" value={newPlan.dietaryType} onChange={(e) => setNewPlan((p) => ({ ...p, dietaryType: e.target.value as PricingPlan["dietaryType"] }))}>
                {["veg", "non-veg", "both"].map((t) => <option key={t}>{t}</option>)}
              </select>
            </div>
            <div className="md:col-span-2">
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Features</label>
              <div className="flex gap-2 mb-2">
                <input
                  className="flex-1 px-3 py-2 rounded-lg border border-gray-200 text-sm focus:ring-2 focus:ring-black outline-none"
                  placeholder="Add a feature and press Enter"
                  value={newFeature}
                  onChange={(e) => setNewFeature(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && newFeature.trim()) {
                      setNewPlan((p) => ({ ...p, features: [...p.features, newFeature.trim()] }));
                      setNewFeature("");
                    }
                  }}
                />
              </div>
              <div className="flex flex-wrap gap-2">
                {newPlan.features.map((f, i) => (
                  <span key={i} className="flex items-center gap-1 bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm">
                    {f}
                    <button onClick={() => setNewPlan((p) => ({ ...p, features: p.features.filter((_, fi) => fi !== i) }))} className="ml-1 text-gray-400 hover:text-red-500">×</button>
                  </span>
                ))}
              </div>
            </div>
          </div>
          <div className="flex gap-3 mt-4">
            <button disabled={saving} onClick={handleAdd} className="px-6 py-2 bg-black text-white rounded-lg font-semibold hover:bg-gray-800 disabled:opacity-50">
              {saving ? "Saving…" : "Create Plan"}
            </button>
            <button onClick={() => setShowAdd(false)} className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200">Cancel</button>
          </div>
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="bg-white rounded-3xl p-8 border border-gray-100 animate-pulse h-64" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {plans.map((plan) => {
            const isEditing = editingId === plan.id;
            return (
              <div key={plan.id} className="bg-white rounded-3xl p-8 shadow-[0_8px_30px_rgb(0,0,0,0.06)] border border-gray-100 relative overflow-hidden flex flex-col group">
                {!plan.isActive && (
                  <div className="absolute top-0 right-0 bg-gray-400 text-white text-xs font-bold px-4 py-1 rounded-bl-xl">INACTIVE</div>
                )}
                {isEditing ? (
                  <>
                    <input className="text-xl font-bold border rounded px-2 py-1 mb-2" value={editDraft.name ?? plan.name} onChange={(e) => setEditDraft((p) => ({ ...p, name: e.target.value }))} />
                    <div className="flex gap-2 mb-4">
                      <input type="number" className="border rounded px-2 py-1 w-28" value={editDraft.price ?? plan.price} onChange={(e) => setEditDraft((p) => ({ ...p, price: Number(e.target.value) }))} />
                      <select className="border rounded px-2 py-1" value={editDraft.type ?? plan.type} onChange={(e) => setEditDraft((p) => ({ ...p, type: e.target.value as PricingPlan["type"] }))}>
                        {["daily", "weekly", "monthly"].map((t) => <option key={t}>{t}</option>)}
                      </select>
                    </div>
                    <label className="flex items-center gap-2 text-sm mb-4">
                      <input type="checkbox" checked={editDraft.isActive ?? plan.isActive} onChange={(e) => setEditDraft((p) => ({ ...p, isActive: e.target.checked }))} />
                      Active
                    </label>
                    <div className="flex gap-2 mt-auto">
                      <button disabled={saving} onClick={handleSaveEdit} className="flex items-center gap-1 px-4 py-2 bg-black text-white rounded-lg text-sm font-semibold disabled:opacity-50">
                        <Check size={14} /> {saving ? "Saving…" : "Save"}
                      </button>
                      <button onClick={() => setEditingId(null)} className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-semibold">
                        <X size={14} />
                      </button>
                    </div>
                  </>
                ) : (
                  <>
                    <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                    <div className="flex items-baseline gap-2 mb-6">
                      <span className="text-5xl font-black text-gray-900">${plan.price}</span>
                      <span className="text-gray-500 font-medium">/{plan.type}</span>
                    </div>
                    <ul className="space-y-4 mb-8 flex-1">
                      {plan.features.map((feature, idx) => (
                        <li key={idx} className="flex items-center gap-3 text-gray-700 font-medium">
                          <div className="p-1 bg-green-100 text-green-700 rounded-full"><Check size={14} strokeWidth={3} /></div>
                          {feature}
                        </li>
                      ))}
                    </ul>
                    <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button onClick={() => { setEditingId(plan.id); setEditDraft({}); }} className="flex-1 py-3 rounded-xl font-bold bg-gray-50 text-gray-900 hover:bg-gray-100 flex items-center justify-center gap-2">
                        <Pencil size={16} /> Edit
                      </button>
                      <button onClick={() => handleDelete(plan.id)} className="p-3 rounded-xl bg-red-50 text-red-600 hover:bg-red-100">
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}