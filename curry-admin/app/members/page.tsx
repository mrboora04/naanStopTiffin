"use client";

import React, { useEffect, useState } from "react";
import { Search, Plus, MoreVertical, Pencil, Trash2, X, Check } from "lucide-react";
import { getMembers, createMember, updateMember, deleteMember } from "@/lib/api";
import type { Member, MemberStatus, DietaryPreference } from "@/types";

const EMPTY_MEMBER: Omit<Member, "id"> = {
  name: "", phone: "", email: "", address: "",
  memberStatus: "active", dietaryPreference: "veg",
  planId: "", renewalDate: "", joinDate: "",
  allergies: "", deliveryNotes: "", emergencyContact: "",
};

export default function Members() {
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editDraft, setEditDraft] = useState<Partial<Member>>({});
  const [showAdd, setShowAdd] = useState(false);
  const [newMember, setNewMember] = useState(EMPTY_MEMBER);
  const [saving, setSaving] = useState(false);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      setMembers(await getMembers());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load members");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const filtered = members.filter((m) =>
    `${m.name} ${m.phone} ${m.email}`.toLowerCase().includes(search.toLowerCase())
  );

  const handleEdit = (m: Member) => { setEditingId(m.id); setEditDraft({ ...m }); };

  const handleSaveEdit = async () => {
    if (!editingId) return;
    setSaving(true);
    try {
      const updated = await updateMember(editingId, editDraft);
      setMembers((prev) => prev.map((m) => (m.id === editingId ? updated : m)));
      setEditingId(null);
    } catch (e) {
      alert(e instanceof Error ? e.message : "Save failed");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this member? This cannot be undone.")) return;
    try {
      await deleteMember(id);
      setMembers((prev) => prev.filter((m) => m.id !== id));
    } catch (e) {
      alert(e instanceof Error ? e.message : "Delete failed");
    }
  };

  const handleAdd = async () => {
    setSaving(true);
    try {
      const created = await createMember(newMember);
      setMembers((prev) => [...prev, created]);
      setShowAdd(false);
      setNewMember(EMPTY_MEMBER);
    } catch (e) {
      alert(e instanceof Error ? e.message : "Create failed");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">Subscribers</h1>
        <button
          onClick={() => setShowAdd(true)}
          className="bg-black text-white px-6 py-3 rounded-full font-medium hover:bg-gray-800 transition-colors shadow-lg flex items-center gap-2"
        >
          <Plus size={20} /> Add Member
        </button>
      </div>

      {error && <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl">{error}</div>}

      {/* Add Member Form */}
      {showAdd && (
        <div className="mb-6 bg-white rounded-2xl p-6 border border-gray-200 shadow-lg">
          <h2 className="font-bold text-lg text-gray-900 mb-4">New Member</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {(["name", "phone", "email", "address", "planId", "allergies", "deliveryNotes", "emergencyContact"] as const).map((field) => (
              <div key={field}>
                <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">{field}</label>
                <input
                  className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:ring-2 focus:ring-black outline-none"
                  value={newMember[field]}
                  onChange={(e) => setNewMember((p) => ({ ...p, [field]: e.target.value }))}
                />
              </div>
            ))}
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Status</label>
              <select
                className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:ring-2 focus:ring-black outline-none"
                value={newMember.memberStatus}
                onChange={(e) => setNewMember((p) => ({ ...p, memberStatus: e.target.value as MemberStatus }))}
              >
                {["active", "paused", "cancelled", "trial"].map((s) => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Dietary</label>
              <select
                className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:ring-2 focus:ring-black outline-none"
                value={newMember.dietaryPreference}
                onChange={(e) => setNewMember((p) => ({ ...p, dietaryPreference: e.target.value as DietaryPreference }))}
              >
                {["veg", "non-veg", "vegan"].map((s) => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Join Date</label>
              <input
                type="date"
                className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:ring-2 focus:ring-black outline-none"
                value={newMember.joinDate}
                onChange={(e) => setNewMember((p) => ({ ...p, joinDate: e.target.value }))}
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Renewal Date</label>
              <input
                type="date"
                className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:ring-2 focus:ring-black outline-none"
                value={newMember.renewalDate}
                onChange={(e) => setNewMember((p) => ({ ...p, renewalDate: e.target.value }))}
              />
            </div>
          </div>
          <div className="flex gap-3 mt-4">
            <button
              disabled={saving}
              onClick={handleAdd}
              className="px-6 py-2 bg-black text-white rounded-lg font-semibold hover:bg-gray-800 disabled:opacity-50 transition-colors"
            >
              {saving ? "Saving…" : "Create Member"}
            </button>
            <button onClick={() => setShowAdd(false)} className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 transition-colors">
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="bg-white rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-gray-100 overflow-hidden">
        <div className="p-4 border-b border-gray-100 flex gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search by name, phone, or email…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-12 pr-4 py-3 rounded-xl bg-gray-50 border-none focus:ring-2 focus:ring-black outline-none transition-all"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-12 text-center text-gray-400 font-medium">Loading…</div>
          ) : filtered.length === 0 ? (
            <div className="p-12 text-center text-gray-400 font-medium">No members found.</div>
          ) : (
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50/50 text-left text-sm font-semibold text-gray-500 uppercase tracking-wider">
                  <th className="px-6 py-4">Member</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Dietary</th>
                  <th className="px-6 py-4">Renewal</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filtered.map((member) => {
                  const isEditing = editingId === member.id;
                  return (
                    <tr key={member.id} className="hover:bg-gray-50/50 transition-colors">
                      <td className="px-6 py-4">
                        {isEditing ? (
                          <div className="flex flex-col gap-1">
                            <input className="border rounded px-2 py-1 text-sm" value={editDraft.name ?? ""} onChange={(e) => setEditDraft((p) => ({ ...p, name: e.target.value }))} />
                            <input className="border rounded px-2 py-1 text-sm" value={editDraft.email ?? ""} onChange={(e) => setEditDraft((p) => ({ ...p, email: e.target.value }))} />
                          </div>
                        ) : (
                          <>
                            <div className="font-semibold text-gray-900">{member.name}</div>
                            <div className="text-sm text-gray-500">{member.email}</div>
                          </>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        {isEditing ? (
                          <select className="border rounded px-2 py-1 text-sm" value={editDraft.memberStatus} onChange={(e) => setEditDraft((p) => ({ ...p, memberStatus: e.target.value as MemberStatus }))}>
                            {["active", "paused", "cancelled", "trial"].map((s) => <option key={s}>{s}</option>)}
                          </select>
                        ) : (
                          <span className={`px-3 py-1 rounded-full text-xs font-bold ${member.memberStatus === "active" ? "bg-green-100 text-green-700" : member.memberStatus === "trial" ? "bg-blue-100 text-blue-700" : "bg-red-100 text-red-700"}`}>
                            {member.memberStatus.toUpperCase()}
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 capitalize font-medium">
                        {isEditing ? (
                          <select className="border rounded px-2 py-1 text-sm" value={editDraft.dietaryPreference} onChange={(e) => setEditDraft((p) => ({ ...p, dietaryPreference: e.target.value as DietaryPreference }))}>
                            {["veg", "non-veg", "vegan"].map((s) => <option key={s}>{s}</option>)}
                          </select>
                        ) : member.dietaryPreference}
                      </td>
                      <td className="px-6 py-4 text-gray-600">
                        {isEditing ? (
                          <input type="date" className="border rounded px-2 py-1 text-sm" value={editDraft.renewalDate ?? ""} onChange={(e) => setEditDraft((p) => ({ ...p, renewalDate: e.target.value }))} />
                        ) : member.renewalDate}
                      </td>
                      <td className="px-6 py-4 text-right">
                        {isEditing ? (
                          <div className="flex items-center justify-end gap-2">
                            <button disabled={saving} onClick={handleSaveEdit} className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors">
                              <Check size={18} />
                            </button>
                            <button onClick={() => setEditingId(null)} className="p-2 text-gray-400 hover:bg-gray-100 rounded-lg transition-colors">
                              <X size={18} />
                            </button>
                          </div>
                        ) : (
                          <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button onClick={() => handleEdit(member)} className="p-2 text-blue-500 hover:bg-blue-50 rounded-lg transition-colors">
                              <Pencil size={18} />
                            </button>
                            <button onClick={() => handleDelete(member.id)} className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors">
                              <Trash2 size={18} />
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}