"use client";

import React, { useEffect, useState } from "react";
import { CheckCircle, XCircle, RefreshCw, Trash2, Plus } from "lucide-react";
import { getTrialRequests, updateTrialRequest, deleteTrialRequest, createTrialRequest } from "@/lib/api";
import type { TrialRequest, TrialStatus } from "@/types";

const STATUS_COLORS: Record<TrialStatus, string> = {
  pending: "bg-yellow-100 text-yellow-800",
  scheduled: "bg-blue-100 text-blue-800",
  completed: "bg-green-100 text-green-800",
  declined: "bg-red-100 text-red-800",
  "no-show": "bg-gray-100 text-gray-600",
};

const EMPTY_REQUEST: Omit<TrialRequest, "id"> = {
  name: "", phone: "", address: "", status: "pending", requestedDate: "",
};

export default function Requests() {
  const [requests, setRequests] = useState<TrialRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAdd, setShowAdd] = useState(false);
  const [newRequest, setNewRequest] = useState(EMPTY_REQUEST);
  const [saving, setSaving] = useState(false);

  const load = async () => {
    setLoading(true);
    setError(null);
    try { setRequests(await getTrialRequests()); }
    catch (e) { setError(e instanceof Error ? e.message : "Failed to load requests"); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleStatusUpdate = async (req: TrialRequest, status: TrialStatus) => {
    try {
      const updated = await updateTrialRequest(req.id, { status });
      setRequests((p) => p.map((r) => (r.id === req.id ? updated : r)));
    } catch (e) { alert(e instanceof Error ? e.message : "Update failed"); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this trial request?")) return;
    try {
      await deleteTrialRequest(id);
      setRequests((p) => p.filter((r) => r.id !== id));
    } catch (e) { alert(e instanceof Error ? e.message : "Delete failed"); }
  };

  const handleAdd = async () => {
    setSaving(true);
    try {
      const created = await createTrialRequest(newRequest);
      setRequests((p) => [...p, created]);
      setShowAdd(false);
      setNewRequest(EMPTY_REQUEST);
    } catch (e) { alert(e instanceof Error ? e.message : "Create failed"); }
    finally { setSaving(false); }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">Trial Requests</h1>
        <div className="flex gap-3">
          <button onClick={load} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-600 font-medium transition-colors">
            <RefreshCw size={16} /> Refresh
          </button>
          <button onClick={() => setShowAdd(true)} className="bg-black text-white px-6 py-3 rounded-full font-medium hover:bg-gray-800 transition-colors shadow-lg flex items-center gap-2">
            <Plus size={20} /> Add Request
          </button>
        </div>
      </div>

      {error && <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl">{error}</div>}

      {/* Add Form */}
      {showAdd && (
        <div className="mb-6 bg-white rounded-2xl p-6 border border-gray-200 shadow-lg">
          <h2 className="font-bold text-lg mb-4">New Trial Request</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {(["name", "phone", "address"] as const).map((field) => (
              <div key={field}>
                <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">{field}</label>
                <input className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:ring-2 focus:ring-black outline-none" value={newRequest[field]} onChange={(e) => setNewRequest((p) => ({ ...p, [field]: e.target.value }))} />
              </div>
            ))}
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Requested Date</label>
              <input type="date" className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:ring-2 focus:ring-black outline-none" value={newRequest.requestedDate} onChange={(e) => setNewRequest((p) => ({ ...p, requestedDate: e.target.value }))} />
            </div>
          </div>
          <div className="flex gap-3 mt-4">
            <button disabled={saving} onClick={handleAdd} className="px-6 py-2 bg-black text-white rounded-lg font-semibold hover:bg-gray-800 disabled:opacity-50">
              {saving ? "Saving…" : "Create"}
            </button>
            <button onClick={() => setShowAdd(false)} className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg font-semibold">Cancel</button>
          </div>
        </div>
      )}

      <div className="bg-white rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-gray-100 overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-gray-400">Loading…</div>
        ) : requests.length === 0 ? (
          <div className="p-12 text-center text-gray-400 font-medium">No trial requests.</div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50/50 text-left text-sm font-semibold text-gray-500 uppercase tracking-wider">
                <th className="px-6 py-4">Prospect</th>
                <th className="px-6 py-4">Date</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {requests.map((req) => (
                <tr key={req.id} className="hover:bg-gray-50/50 transition-colors group">
                  <td className="px-6 py-4">
                    <div className="font-semibold text-gray-900">{req.name}</div>
                    <div className="text-sm text-gray-500">{req.phone} &bull; {req.address}</div>
                  </td>
                  <td className="px-6 py-4 text-gray-600 font-medium">{req.requestedDate}</td>
                  <td className="px-6 py-4">
                    <select
                      className={`px-3 py-1 rounded-full text-xs font-bold uppercase border-none outline-none cursor-pointer ${STATUS_COLORS[req.status]}`}
                      value={req.status}
                      onChange={(e) => handleStatusUpdate(req, e.target.value as TrialStatus)}
                    >
                      {(["pending", "scheduled", "completed", "declined", "no-show"] as TrialStatus[]).map((s) => (
                        <option key={s} value={s}>{s}</option>
                      ))}
                    </select>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      {req.status === "pending" && (
                        <>
                          <button onClick={() => handleStatusUpdate(req, "scheduled")} className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors" title="Accept">
                            <CheckCircle size={20} />
                          </button>
                          <button onClick={() => handleStatusUpdate(req, "declined")} className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors" title="Decline">
                            <XCircle size={20} />
                          </button>
                        </>
                      )}
                      <button onClick={() => handleDelete(req.id)} className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors opacity-0 group-hover:opacity-100">
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}