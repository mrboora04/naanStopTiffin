"use client";

import React, { useEffect, useState } from "react";
import { Calendar as CalendarIcon, Edit3, X, Check, RefreshCw } from "lucide-react";
import { getSchedule, updateScheduleDay } from "@/lib/api";
import type { ScheduleDay, Dish } from "@/types";

export default function Schedule() {
  const [schedule, setSchedule] = useState<ScheduleDay[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editDraft, setEditDraft] = useState<Partial<ScheduleDay>>({});
  const [saving, setSaving] = useState(false);

  const load = async () => {
    setLoading(true);
    setError(null);
    try { setSchedule(await getSchedule()); }
    catch (e) { setError(e instanceof Error ? e.message : "Failed to load schedule"); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const dishNames = (dishes: Dish[]) => dishes.map((d) => d.name).join(", ") || "—";

  const handleSave = async () => {
    if (!editingId) return;
    setSaving(true);
    try {
      const updated = await updateScheduleDay(editingId, editDraft);
      setSchedule((p) => p.map((d) => (d.id === editingId ? updated : d)));
      setEditingId(null);
    } catch (e) { alert(e instanceof Error ? e.message : "Save failed"); }
    finally { setSaving(false); }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">Weekly Menu</h1>
        <div className="flex gap-3">
          <button onClick={load} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-600 font-medium transition-colors">
            <RefreshCw size={16} /> Refresh
          </button>
          <button className="bg-black text-white px-6 py-3 rounded-full font-medium hover:bg-gray-800 transition-colors shadow-lg flex items-center gap-2">
            <CalendarIcon size={20} /> View Full Calendar
          </button>
        </div>
      </div>

      {error && <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl">{error}</div>}

      {loading ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-white rounded-3xl p-8 border border-gray-100 animate-pulse h-64" />
          ))}
        </div>
      ) : schedule.length === 0 ? (
        <div className="text-center p-12 text-gray-400 font-medium bg-white rounded-2xl border border-gray-100">
          No schedule days found.
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {schedule.map((day) => {
            const isEditing = editingId === day.id;
            return (
              <div key={day.id} className="bg-white rounded-3xl p-8 shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-gray-100">
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h2 className="text-2xl font-black text-gray-900">{day.dayOfWeek}</h2>
                    <p className="text-gray-500 font-medium">{day.date}</p>
                    {day.isHoliday && (
                      <span className="inline-block mt-1 px-2 py-0.5 bg-red-100 text-red-600 text-xs font-bold rounded-full">HOLIDAY</span>
                    )}
                  </div>
                  {isEditing ? (
                    <div className="flex gap-2">
                      <button disabled={saving} onClick={handleSave} className="p-2 text-green-600 hover:bg-green-50 rounded-full transition-colors">
                        <Check size={18} />
                      </button>
                      <button onClick={() => setEditingId(null)} className="p-2 text-gray-400 hover:bg-gray-100 rounded-full transition-colors">
                        <X size={18} />
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => { setEditingId(day.id); setEditDraft({}); }}
                      className="p-3 bg-gray-50 text-gray-600 rounded-full hover:bg-black hover:text-white transition-all"
                    >
                      <Edit3 size={18} />
                    </button>
                  )}
                </div>

                <div className="space-y-6">
                  <div className="bg-orange-50/50 p-5 rounded-2xl">
                    <h3 className="font-bold text-orange-800 mb-3 text-lg">Lunch Menu</h3>
                    {isEditing ? (
                      <div className="space-y-2">
                        <div>
                          <label className="text-xs font-semibold text-green-700 uppercase">Veg dishes (comma-separated names)</label>
                          <input
                            className="w-full mt-1 px-3 py-2 rounded-lg border border-gray-200 text-sm"
                            defaultValue={dishNames(day.lunchVegDishes ?? [])}

                            onChange={(e) => {
                              const names = e.target.value.split(",").map((n) => n.trim()).filter(Boolean);
                              const dishes = names.map((name, idx) => ({ id: `tmp-lv-${idx}`, name, category: "Main", dietaryType: "veg" as const, ingredients: [] }));
                              setEditDraft((p) => ({ ...p, lunchVegDishes: dishes }));
                            }}
                          />
                        </div>
                        <div>
                          <label className="text-xs font-semibold text-red-600 uppercase">Non-veg dishes (comma-separated names)</label>
                          <input
                            className="w-full mt-1 px-3 py-2 rounded-lg border border-gray-200 text-sm"
                            defaultValue={dishNames(day.lunchNonVegDishes ?? [])}

                            onChange={(e) => {
                              const names = e.target.value.split(",").map((n) => n.trim()).filter(Boolean);
                              const dishes = names.map((name, idx) => ({ id: `tmp-lnv-${idx}`, name, category: "Main", dietaryType: "non-veg" as const, ingredients: [] }));
                              setEditDraft((p) => ({ ...p, lunchNonVegDishes: dishes }));
                            }}
                          />
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        <p className="text-sm font-semibold text-gray-700"><span className="text-green-600 mr-2">V:</span>{dishNames(day.lunchVegDishes ?? [])}</p>
                        <p className="text-sm font-semibold text-gray-700"><span className="text-red-500 mr-2">NV:</span>{dishNames(day.lunchNonVegDishes ?? [])}</p>
                      </div>
                    )}
                  </div>

                  <div className="bg-blue-50/50 p-5 rounded-2xl">
                    <h3 className="font-bold text-blue-800 mb-3 text-lg">Dinner Menu</h3>
                    {isEditing ? (
                      <div className="space-y-2">
                        <div>
                          <label className="text-xs font-semibold text-green-700 uppercase">Veg dishes (comma-separated names)</label>
                          <input
                            className="w-full mt-1 px-3 py-2 rounded-lg border border-gray-200 text-sm"
                            defaultValue={dishNames(day.dinnerVegDishes ?? [])}

                            onChange={(e) => {
                              const names = e.target.value.split(",").map((n) => n.trim()).filter(Boolean);
                              const dishes = names.map((name, idx) => ({ id: `tmp-dv-${idx}`, name, category: "Main", dietaryType: "veg" as const, ingredients: [] }));
                              setEditDraft((p) => ({ ...p, dinnerVegDishes: dishes }));
                            }}
                          />
                        </div>
                        <div>
                          <label className="text-xs font-semibold text-red-600 uppercase">Non-veg dishes (comma-separated names)</label>
                          <input
                            className="w-full mt-1 px-3 py-2 rounded-lg border border-gray-200 text-sm"
                            defaultValue={dishNames(day.dinnerNonVegDishes ?? [])}

                            onChange={(e) => {
                              const names = e.target.value.split(",").map((n) => n.trim()).filter(Boolean);
                              const dishes = names.map((name, idx) => ({ id: `tmp-dnv-${idx}`, name, category: "Main", dietaryType: "non-veg" as const, ingredients: [] }));
                              setEditDraft((p) => ({ ...p, dinnerNonVegDishes: dishes }));
                            }}
                          />
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        <p className="text-sm font-semibold text-gray-700"><span className="text-green-600 mr-2">V:</span>{dishNames(day.dinnerVegDishes ?? [])}</p>
                        <p className="text-sm font-semibold text-gray-700"><span className="text-red-500 mr-2">NV:</span>{dishNames(day.dinnerNonVegDishes ?? [])}</p>
                      </div>
                    )}
                  </div>

                  {isEditing && (
                    <div>
                      <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Special Notes</label>
                      <input
                        className="w-full mt-1 px-3 py-2 rounded-lg border border-gray-200 text-sm"
                        defaultValue={day.specialNotes}
                        onChange={(e) => setEditDraft((p) => ({ ...p, specialNotes: e.target.value }))}
                      />
                      <label className="flex items-center gap-2 mt-2 text-sm">
                        <input
                          type="checkbox"
                          defaultChecked={day.isHoliday}
                          onChange={(e) => setEditDraft((p) => ({ ...p, isHoliday: e.target.checked }))}
                        />
                        Mark as Holiday
                      </label>
                    </div>
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