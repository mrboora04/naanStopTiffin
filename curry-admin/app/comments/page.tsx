"use client";

import React, { useEffect, useState } from "react";
import { Star, RefreshCw, Trash2, CheckCircle } from "lucide-react";
import { getFeedback, updateFeedback, deleteFeedback } from "@/lib/api";
import type { Feedback, FeedbackType } from "@/types";

const TYPE_COLORS: Record<FeedbackType, string> = {
  feedback: "bg-blue-100 text-blue-700",
  complaint: "bg-red-100 text-red-700",
  suggestion: "bg-green-100 text-green-700",
};

export default function Comments() {
  const [feedbackList, setFeedbackList] = useState<Feedback[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<"all" | "new" | "resolved">("all");

  const load = async () => {
    setLoading(true);
    setError(null);
    try { setFeedbackList(await getFeedback()); }
    catch (e) { setError(e instanceof Error ? e.message : "Failed to load feedback"); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleResolve = async (fb: Feedback) => {
    try {
      const updated = await updateFeedback(fb.id, { status: "resolved" });
      setFeedbackList((p) => p.map((f) => (f.id === fb.id ? updated : f)));
    } catch (e) { alert(e instanceof Error ? e.message : "Update failed"); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this feedback?")) return;
    try {
      await deleteFeedback(id);
      setFeedbackList((p) => p.filter((f) => f.id !== id));
    } catch (e) { alert(e instanceof Error ? e.message : "Delete failed"); }
  };

  const filtered = feedbackList.filter((fb) => filter === "all" ? true : fb.status === filter);

  return (
    <div className="p-8 max-w-7xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">Feedback & Comments</h1>
        <div className="flex items-center gap-3">
          <div className="flex rounded-xl overflow-hidden border border-gray-200 bg-white">
            {(["all", "new", "resolved"] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-4 py-2 text-sm font-semibold capitalize transition-colors ${filter === f ? "bg-black text-white" : "text-gray-500 hover:bg-gray-50"}`}
              >
                {f}
              </button>
            ))}
          </div>
          <button onClick={load} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-600 font-medium transition-colors">
            <RefreshCw size={16} /> Refresh
          </button>
        </div>
      </div>

      {error && <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl">{error}</div>}

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-white rounded-2xl p-6 border border-gray-100 animate-pulse h-40" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center p-12 text-gray-400 font-medium bg-white rounded-2xl border border-gray-100">
          No feedback found.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filtered.map((fb) => (
            <div
              key={fb.id}
              className={`bg-white rounded-2xl p-6 shadow-[0_8px_30px_rgb(0,0,0,0.04)] border relative group transition-all ${
                fb.status === "resolved" ? "opacity-60" : "border-gray-100"
              }`}
            >
              <div className="flex items-center justify-between mb-4">
                <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${TYPE_COLORS[fb.type]}`}>
                  {fb.type}
                </span>
                <div className="flex items-center gap-1 text-yellow-400">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Star key={i} size={16} fill={i < fb.rating ? "currentColor" : "none"} strokeWidth={i < fb.rating ? 0 : 2} />
                  ))}
                </div>
              </div>

              <p className="text-gray-800 text-lg font-medium">"{fb.comments}"</p>

              <div className="mt-6 pt-4 border-t border-gray-100 flex justify-between items-center">
                <span className={`text-sm font-semibold uppercase tracking-wider ${fb.status === "resolved" ? "text-green-500" : "text-gray-400"}`}>
                  {fb.status}
                </span>
                <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  {fb.status !== "resolved" && (
                    <button onClick={() => handleResolve(fb)} className="flex items-center gap-1 text-sm font-bold text-green-600 hover:bg-green-50 px-3 py-1.5 rounded-lg transition-colors">
                      <CheckCircle size={16} /> Resolve
                    </button>
                  )}
                  <button onClick={() => handleDelete(fb.id)} className="p-1.5 text-red-500 hover:bg-red-50 rounded-lg transition-colors">
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}