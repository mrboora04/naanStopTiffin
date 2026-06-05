"use client";

import React, { useEffect, useState } from "react";
import { Search, Plus, Pencil, Trash2, X, Check, ChevronLeft, ChevronRight } from "lucide-react";
import { toast } from "sonner";
import { getMembers, createMember, updateMember, deleteMember } from "@/lib/api";
import type { Member, MemberStatus, DietaryPreference } from "@/types";
import { TableSkeleton, EmptyState } from "@/components/ui";
import { Spinner } from "@/components/ui/Spinner";
import ConfirmDialog from "@/components/ConfirmDialog";
import { formatDate } from "@/lib/formatters";

const EMPTY_MEMBER: Omit<Member, "id"> = {
  name: "", phone: "", email: "", address: "",
  memberStatus: "active", dietaryPreference: "veg",
  planId: "", renewalDate: "", joinDate: "",
  allergies: "", deliveryNotes: "", emergencyContact: "",
};

const PAGE_SIZE = 10;

function StatusBadge({ status }: { status: string }) {
  const cls =
    status === "active"     ? "badge-active" :
    status === "trial"      ? "badge-info"   :
    status === "paused"     ? "badge-warning" : "badge-error";
  return (
    <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${cls}`}>
      {status}
    </span>
  );
}

export default function Members() {
  const [members,    setMembers]    = useState<Member[]>([]);
  const [loading,    setLoading]    = useState(true);
  const [search,     setSearch]     = useState("");
  const [editingId,  setEditingId]  = useState<string | null>(null);
  const [editDraft,  setEditDraft]  = useState<Partial<Member>>({});
  const [showAdd,    setShowAdd]    = useState(false);
  const [newMember,  setNewMember]  = useState(EMPTY_MEMBER);
  const [saving,     setSaving]     = useState(false);
  const [deleteId,   setDeleteId]   = useState<string | null>(null);
  const [page,       setPage]       = useState(1);

  const load = async () => {
    setLoading(true);
    try {
      setMembers(await getMembers());
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to load members");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const filtered = members.filter((m) =>
    `${m.name} ${m.phone} ${m.email}`.toLowerCase().includes(search.toLowerCase())
  );

  // Pagination
  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const paginated  = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  // Reset to page 1 when search changes
  useEffect(() => { setPage(1); }, [search]);

  const handleEdit = (m: Member) => { setEditingId(m.id); setEditDraft({ ...m }); };

  const handleSaveEdit = async () => {
    if (!editingId) return;
    setSaving(true);
    try {
      const updated = await updateMember(editingId, editDraft);
      setMembers((prev) => prev.map((m) => (m.id === editingId ? updated : m)));
      setEditingId(null);
      toast.success(`${editDraft.name ?? "Member"} updated successfully`);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Save failed");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    const member = members.find((m) => m.id === deleteId);
    try {
      await deleteMember(deleteId);
      setMembers((prev) => prev.filter((m) => m.id !== deleteId));
      toast.success(`${member?.name ?? "Member"} removed`);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Delete failed");
    } finally {
      setDeleteId(null);
    }
  };

  const handleAdd = async () => {
    if (!newMember.name.trim()) {
      toast.warning("Please enter a name before saving");
      return;
    }
    setSaving(true);
    try {
      const created = await createMember(newMember);
      setMembers((prev) => [...prev, created]);
      setShowAdd(false);
      setNewMember(EMPTY_MEMBER);
      toast.success(`${created.name} added as a new member`);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Create failed");
    } finally {
      setSaving(false);
    }
  };

  const deleteMemberName = members.find((m) => m.id === deleteId)?.name ?? "this member";

  return (
    <div className="p-4 lg:p-8 max-w-7xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-300">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl lg:text-4xl font-extrabold text-gray-900 tracking-tight">Subscribers</h1>
          <p className="text-sm text-gray-400 mt-1">{members.length} total members</p>
        </div>
        <button
          onClick={() => setShowAdd(true)}
          className="bg-orange-500 hover:bg-orange-600 text-white px-5 py-2.5 rounded-xl font-semibold shadow-sm flex items-center gap-2 transition-colors"
        >
          <Plus size={18} /> <span className="hidden sm:inline">Add Member</span>
        </button>
      </div>

      {/* Add Member Panel */}
      {showAdd && (
        <div className="mb-6 bg-white rounded-2xl p-6 border border-gray-200 shadow-lg animate-in slide-in-from-top-2 duration-200">
          <h2 className="font-bold text-lg text-gray-900 mb-4">New Member</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {(["name", "phone", "email", "address", "planId", "allergies", "deliveryNotes", "emergencyContact"] as const).map((field) => (
              <div key={field}>
                <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
                  {field === "planId" ? "Plan ID" : field.replace(/([A-Z])/g, " $1")}
                  {field === "name" && <span className="text-red-500 ml-1">*</span>}
                </label>
                <input
                  className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:ring-2 focus:ring-orange-400 outline-none transition-shadow"
                  value={newMember[field]}
                  placeholder={field === "name" ? "Full name (required)" : ""}
                  onChange={(e) => setNewMember((p) => ({ ...p, [field]: e.target.value }))}
                />
              </div>
            ))}
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Status</label>
              <select
                className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:ring-2 focus:ring-orange-400 outline-none"
                value={newMember.memberStatus}
                onChange={(e) => setNewMember((p) => ({ ...p, memberStatus: e.target.value as MemberStatus }))}
              >
                {["active", "paused", "cancelled", "trial"].map((s) => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Dietary</label>
              <select
                className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:ring-2 focus:ring-orange-400 outline-none"
                value={newMember.dietaryPreference}
                onChange={(e) => setNewMember((p) => ({ ...p, dietaryPreference: e.target.value as DietaryPreference }))}
              >
                {["veg", "non-veg", "vegan"].map((s) => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Join Date</label>
              <input type="date" className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:ring-2 focus:ring-orange-400 outline-none" value={newMember.joinDate} onChange={(e) => setNewMember((p) => ({ ...p, joinDate: e.target.value }))} />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Renewal Date</label>
              <input type="date" className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:ring-2 focus:ring-orange-400 outline-none" value={newMember.renewalDate} onChange={(e) => setNewMember((p) => ({ ...p, renewalDate: e.target.value }))} />
            </div>
          </div>
          <div className="flex gap-3 mt-5">
            <button
              disabled={saving}
              onClick={handleAdd}
              className="flex items-center gap-2 px-6 py-2.5 bg-orange-500 hover:bg-orange-600 text-white rounded-xl font-semibold disabled:opacity-50 transition-colors"
            >
              {saving ? <Spinner size="sm" /> : null}
              {saving ? "Saving…" : "Create Member"}
            </button>
            <button onClick={() => setShowAdd(false)} className="px-6 py-2.5 bg-gray-100 text-gray-700 rounded-xl font-semibold hover:bg-gray-200 transition-colors">
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Table card */}
      <div className="bg-white rounded-2xl shadow-[0_4px_24px_rgb(0,0,0,0.05)] border border-gray-100 overflow-hidden">
        {/* Search bar */}
        <div className="p-4 border-b border-gray-100">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              placeholder="Search by name, phone, or email…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-11 pr-10 py-2.5 rounded-xl bg-gray-50 border border-gray-100 focus:ring-2 focus:ring-orange-400 focus:bg-white outline-none transition-all text-sm"
            />
            {search && (
              <button onClick={() => setSearch("")} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-700">
                <X size={16} />
              </button>
            )}
          </div>
        </div>

        {loading ? (
          <TableSkeleton rows={6} cols={5} />
        ) : filtered.length === 0 ? (
          <EmptyState type={search ? "no-results" : "no-members"} />
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-gray-50/70 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    <th className="px-4 lg:px-6 py-3">Member</th>
                    <th className="px-4 lg:px-6 py-3">Status</th>
                    <th className="px-4 lg:px-6 py-3">Dietary</th>
                    <th className="px-4 lg:px-6 py-3">Renewal</th>
                    <th className="px-4 lg:px-6 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {paginated.map((member) => {
                    const isEditing = editingId === member.id;
                    return (
                      <tr key={member.id} className="hover:bg-gray-50/60 transition-colors group">
                        <td className="px-4 lg:px-6 py-4">
                          {isEditing ? (
                            <div className="flex flex-col gap-1.5">
                              <input className="border border-gray-200 rounded-lg px-2 py-1 text-sm focus:ring-2 focus:ring-orange-400 outline-none" value={editDraft.name ?? ""} onChange={(e) => setEditDraft((p) => ({ ...p, name: e.target.value }))} />
                              <input className="border border-gray-200 rounded-lg px-2 py-1 text-sm focus:ring-2 focus:ring-orange-400 outline-none" value={editDraft.email ?? ""} onChange={(e) => setEditDraft((p) => ({ ...p, email: e.target.value }))} />
                            </div>
                          ) : (
                            <>
                              <div className="font-semibold text-gray-900">{member.name}</div>
                              <div className="text-sm text-gray-400">{member.email}</div>
                            </>
                          )}
                        </td>
                        <td className="px-4 lg:px-6 py-4">
                          {isEditing ? (
                            <select className="border border-gray-200 rounded-lg px-2 py-1 text-sm" value={editDraft.memberStatus} onChange={(e) => setEditDraft((p) => ({ ...p, memberStatus: e.target.value as MemberStatus }))}>
                              {["active", "paused", "cancelled", "trial"].map((s) => <option key={s}>{s}</option>)}
                            </select>
                          ) : (
                            <StatusBadge status={member.memberStatus} />
                          )}
                        </td>
                        <td className="px-4 lg:px-6 py-4 capitalize font-medium text-gray-700">
                          {isEditing ? (
                            <select className="border border-gray-200 rounded-lg px-2 py-1 text-sm" value={editDraft.dietaryPreference} onChange={(e) => setEditDraft((p) => ({ ...p, dietaryPreference: e.target.value as DietaryPreference }))}>
                              {["veg", "non-veg", "vegan"].map((s) => <option key={s}>{s}</option>)}
                            </select>
                          ) : member.dietaryPreference}
                        </td>
                        <td className="px-4 lg:px-6 py-4 text-gray-500 text-sm">
                          {isEditing ? (
                            <input type="date" className="border border-gray-200 rounded-lg px-2 py-1 text-sm" value={editDraft.renewalDate ?? ""} onChange={(e) => setEditDraft((p) => ({ ...p, renewalDate: e.target.value }))} />
                          ) : formatDate(member.renewalDate)}
                        </td>
                        <td className="px-4 lg:px-6 py-4 text-right">
                          {isEditing ? (
                            <div className="flex items-center justify-end gap-2">
                              <button
                                disabled={saving}
                                onClick={handleSaveEdit}
                                className="flex items-center gap-1 px-3 py-1.5 bg-green-50 text-green-700 hover:bg-green-100 rounded-lg text-sm font-semibold transition-colors disabled:opacity-50"
                              >
                                {saving ? <Spinner size="sm" /> : <Check size={15} />}
                                Save
                              </button>
                              <button onClick={() => setEditingId(null)} className="p-1.5 text-gray-400 hover:bg-gray-100 rounded-lg transition-colors">
                                <X size={15} />
                              </button>
                            </div>
                          ) : (
                            <div className="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                              <button onClick={() => handleEdit(member)} className="p-2 text-blue-500 hover:bg-blue-50 rounded-lg transition-colors" title="Edit member">
                                <Pencil size={16} />
                              </button>
                              <button onClick={() => setDeleteId(member.id)} className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors" title="Remove member">
                                <Trash2 size={16} />
                              </button>
                            </div>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between px-4 lg:px-6 py-4 border-t border-gray-100">
                <p className="text-sm text-gray-400">
                  Showing {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, filtered.length)} of {filtered.length}
                </p>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="p-2 rounded-lg hover:bg-gray-100 text-gray-500 disabled:opacity-30 transition-colors"
                    aria-label="Previous page"
                  >
                    <ChevronLeft size={18} />
                  </button>
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map((n) => (
                    <button
                      key={n}
                      onClick={() => setPage(n)}
                      className={`w-8 h-8 rounded-lg text-sm font-semibold transition-colors ${
                        n === page
                          ? "bg-orange-500 text-white"
                          : "hover:bg-gray-100 text-gray-500"
                      }`}
                    >
                      {n}
                    </button>
                  ))}
                  <button
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="p-2 rounded-lg hover:bg-gray-100 text-gray-500 disabled:opacity-30 transition-colors"
                    aria-label="Next page"
                  >
                    <ChevronRight size={18} />
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Delete confirmation — uses ConfirmDialog, not native confirm() */}
      <ConfirmDialog
        open={!!deleteId}
        title="Remove this member?"
        message={`Remove "${deleteMemberName}" from the subscriber list? This action cannot be undone.`}
        confirmLabel="Yes, Remove"
        confirmVariant="danger"
        onConfirm={handleDelete}
        onCancel={() => setDeleteId(null)}
      />
    </div>
  );
}