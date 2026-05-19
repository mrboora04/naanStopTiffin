"use client";

import React, { useEffect, useState } from "react";
import { Rocket, Plus, Trash2, Pencil, X, Check, RefreshCw, Users } from "lucide-react";
import { getPilotPrograms, createPilotProgram, updatePilotProgram, deletePilotProgram } from "@/lib/api";
import type { PilotProgram, PilotStatus } from "@/types";

const STATUS_COLORS: Record<PilotStatus, string> = {
  planning: "bg-yellow-100 text-yellow-700",
  active: "bg-purple-100 text-purple-700",
  completed: "bg-green-100 text-green-700",
  cancelled: "bg-red-100 text-red-700",
};

const EMPTY_PROGRAM: Omit<PilotProgram, "id"> = {
  name: "", status: "planning", participants: [], timeline: "", feedbackSummary: "",
};

export default function Pilot() {
  const [programs, setPrograms] = useState<PilotProgram[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAdd, setShowAdd] = useState(false);
  const [newProgram, setNewProgram] = useState(EMPTY_PROGRAM);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editDraft, setEditDraft] = useState<Partial<PilotProgram>>({});
  const [saving, setSaving] = useState(false);

  const load = async () => {
    setLoading(true);
    setError(null);
    try { setPrograms(await getPilotPrograms()); }
    catch (e) { setError(e instanceof Error ? e.message : "Failed to load pilot programs"); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleAdd = async () => {
    setSaving(true);
    try {
      const created = await createPilotProgram(newProgram);
      setPrograms((p) => [...p, created]);
      setShowAdd(false);
      setNewProgram(EMPTY_PROGRAM);
    } catch (e) { alert(e instanceof Error ? e.message : "Create failed"); }
    finally { setSaving(false); }
  };

  const handleSaveEdit = async () => {
    if (!editingId) return;
    setSaving(true);
    try {
      const updated = await updatePilotProgram(editingId, editDraft);
      setPrograms((p) => p.map((pr) => (pr.id === editingId ? updated : pr)));
      setEditingId(null);
    } catch (e) { alert(e instanceof Error ? e.message : "Save failed"); }
    finally { setSaving(false); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this pilot program?")) return;
    try {
      await deletePilotProgram(id);
      setPrograms((p) => p.filter((pr) => pr.id !== id));
    } catch (e) { alert(e instanceof Error ? e.message : "Delete failed"); }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">Pilot Programs</h1>
        <div className="flex gap-3">
          <button onClick={load} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-600 font-medium transition-colors">
            <RefreshCw size={16} /> Refresh
          </button>
          <button onClick={() => setShowAdd(true)} className="bg-purple-600 text-white px-6 py-3 rounded-full font-medium hover:bg-purple-700 transition-colors shadow-lg flex items-center gap-2">
            <Plus size={20} /> New Pilot
          </button>
        </div>
      </div>

      {error && <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl">{error}</div>}

      {/* Add Form */}
      {showAdd && (
        <div className="mb-6 bg-white rounded-2xl p-6 border border-gray-200 shadow-lg">
          <h2 className="font-bold text-lg mb-4">New Pilot Program</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Name</label>
              <input className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:ring-2 focus:ring-purple-500 outline-none" value={newProgram.name} onChange={(e) => setNewProgram((p) => ({ ...p, name: e.target.value }))} />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Timeline</label>
              <input className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:ring-2 focus:ring-purple-500 outline-none" placeholder="e.g. June 2026 – July 2026" value={newProgram.timeline} onChange={(e) => setNewProgram((p) => ({ ...p, timeline: e.target.value }))} />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Status</label>
              <select className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm" value={newProgram.status} onChange={(e) => setNewProgram((p) => ({ ...p, status: e.target.value as PilotStatus }))}>
                {(["planning", "active", "completed", "cancelled"] as PilotStatus[]).map((s) => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div className="md:col-span-2">
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Feedback Summary</label>
              <textarea className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:ring-2 focus:ring-purple-500 outline-none" rows={2} value={newProgram.feedbackSummary} onChange={(e) => setNewProgram((p) => ({ ...p, feedbackSummary: e.target.value }))} />
            </div>
          </div>
          <div className="flex gap-3 mt-4">
            <button disabled={saving} onClick={handleAdd} className="px-6 py-2 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 disabled:opacity-50">
              {saving ? "Saving…" : "Create Program"}
            </button>
            <button onClick={() => setShowAdd(false)} className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg font-semibold">Cancel</button>
          </div>
        </div>
      )}

      {loading ? (
        <div className="grid gap-6">
          {Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="bg-white rounded-2xl p-6 border border-gray-100 animate-pulse h-40" />
          ))}
        </div>
      ) : programs.length === 0 ? (
        <div className="text-center p-12 text-gray-400 font-medium bg-white rounded-2xl border border-gray-100">
          No pilot programs yet.
        </div>
      ) : (
        <div className="grid gap-6">
          {programs.map((pilot) => {
            const isEditing = editingId === pilot.id;
            return (
              <div key={pilot.id} className="bg-white rounded-2xl p-6 shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-gray-100 flex flex-col md:flex-row justify-between items-start md:items-center gap-6 group">
                <div className="flex-1">
                  {isEditing ? (
                    <div className="space-y-3">
                      <input className="border rounded px-3 py-1.5 text-xl font-bold w-full" value={editDraft.name ?? pilot.name} onChange={(e) => setEditDraft((p) => ({ ...p, name: e.target.value }))} />
                      <input className="border rounded px-3 py-1.5 text-sm w-full" placeholder="Timeline" value={editDraft.timeline ?? pilot.timeline} onChange={(e) => setEditDraft((p) => ({ ...p, timeline: e.target.value }))} />
                      <select className="border rounded px-3 py-1.5 text-sm" value={editDraft.status ?? pilot.status} onChange={(e) => setEditDraft((p) => ({ ...p, status: e.target.value as PilotStatus }))}>
                        {(["planning", "active", "completed", "cancelled"] as PilotStatus[]).map((s) => <option key={s}>{s}</option>)}
                      </select>
                      <textarea className="border rounded px-3 py-1.5 text-sm w-full" rows={2} value={editDraft.feedbackSummary ?? pilot.feedbackSummary} onChange={(e) => setEditDraft((p) => ({ ...p, feedbackSummary: e.target.value }))} />
                      <div className="flex gap-2">
                        <button disabled={saving} onClick={handleSaveEdit} className="flex items-center gap-1 px-4 py-2 bg-purple-600 text-white rounded-lg text-sm font-semibold disabled:opacity-50">
                          <Check size={14} /> {saving ? "Saving…" : "Save"}
                        </button>
                        <button onClick={() => setEditingId(null)} className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm">
                          <X size={14} />
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-2xl font-bold text-gray-900">{pilot.name}</h3>
                        <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${STATUS_COLORS[pilot.status]}`}>{pilot.status}</span>
                      </div>
                      <p className="text-gray-500 font-medium">{pilot.timeline}</p>
                      {pilot.feedbackSummary && (
                        <p className="text-gray-600 mt-4 bg-gray-50 p-4 rounded-xl border border-gray-100">
                          <span className="font-semibold block mb-1">Feedback Summary:</span>
                          {pilot.feedbackSummary}
                        </p>
                      )}
                    </>
                  )}
                </div>

                {!isEditing && (
                  <div className="flex items-center gap-4">
                    <div className="text-center bg-gray-50 p-6 rounded-2xl min-w-[120px]">
                      <div className="flex items-center justify-center gap-1 mb-1">
                        <Users size={20} className="text-purple-500" />
                      </div>
                      <div className="text-4xl font-black text-purple-600 mb-1">{pilot.participants.length}</div>
                      <div className="text-xs font-bold text-gray-500 uppercase tracking-wider">Participants</div>
                    </div>
                    <div className="flex flex-col gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button onClick={() => { setEditingId(pilot.id); setEditDraft({}); }} className="p-2 text-blue-500 hover:bg-blue-50 rounded-lg transition-colors">
                        <Pencil size={18} />
                      </button>
                      <button onClick={() => handleDelete(pilot.id)} className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors">
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}