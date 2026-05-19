"use client";

import { useState } from "react";
import { Member } from "@/types";
import { useLanguage } from "@/contexts/LanguageContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import StatusBadge from "@/components/StatusBadge";

export default function MemberModal({
  member,
  open,
  onClose,
  onSave,
}: {
  member: Member;
  open: boolean;
  onClose: () => void;
  onSave: (updated: Member) => void;
}) {
  const { t } = useLanguage();
  const [edited, setEdited] = useState<Member>(member);

  const handleSave = () => {
    onSave(edited);
    onClose();
  };

  const todayDate = new Date();
  todayDate.setHours(0, 0, 0, 0);
  const renewalDateObj = new Date(edited.renewalDate);
  renewalDateObj.setHours(0, 0, 0, 0);
  const diffDays = Math.ceil((renewalDateObj.getTime() - todayDate.getTime()) / (1000 * 60 * 60 * 24));
  const isOverdue = diffDays <= 0;
  const renewalText = diffDays < 0 
    ? `Renewal overdue by ${Math.abs(diffDays)} days` 
    : diffDays === 0 
    ? "Renewal due today" 
    : `Renewal in ${diffDays} days (${edited.renewalDate})`;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent
        className="max-w-lg max-h-[90dvh] flex flex-col p-0 gap-0 overflow-hidden"
        showCloseButton={false}
      >
        {/* ── Header ── */}
        <DialogHeader className="px-6 pt-6 pb-4 border-b border-gray-100 shrink-0">
          <DialogTitle className="text-xl">{member.name}</DialogTitle>
          <div className="flex flex-wrap gap-2 pt-1">
            <StatusBadge
              label={(edited.dietaryPreference ?? "—").toUpperCase()}
              variant="info"
            />
            <StatusBadge
              label={edited.memberStatus.toUpperCase()}
              variant={edited.memberStatus === "active" ? "success" : "warning"}
            />
            {isOverdue && (
              <StatusBadge label="Renewal Due" variant="error" />
            )}
          </div>
        </DialogHeader>

        {/* ── Tabs body ── */}
        <div className="flex-1 overflow-y-auto px-6 py-5">
          <Tabs defaultValue="details" className="w-full">
            <TabsList className="grid w-full grid-cols-2 h-12 mb-4">
              <TabsTrigger value="details" className="text-lg h-full">Details</TabsTrigger>
              <TabsTrigger value="subscription" className="text-lg h-full">Subscription</TabsTrigger>
            </TabsList>

            <TabsContent value="details" className="space-y-5 animate-in fade-in-50">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-lg text-gray-500">Phone</Label>
                  <p className="text-xl font-medium mt-0.5">{member.phone}</p>
                </div>
                <div>
                  <Label className="text-lg text-gray-500">Email</Label>
                  <p className="text-xl font-medium mt-0.5">{member.email}</p>
                </div>
                <div className="col-span-2">
                  <Label className="text-lg">Delivery Address</Label>
                  <Input
                    className="text-lg h-12 mt-1"
                    value={edited.address}
                    onChange={(e) =>
                      setEdited({ ...edited, address: e.target.value })
                    }
                  />
                </div>
              </div>

              <div className="space-y-4 rounded-xl bg-gray-50 p-4">
                <p className="text-lg font-semibold">Preferences & Notes</p>
                <div>
                  <Label className="text-lg">Allergies</Label>
                  <Input
                    className="text-lg h-12 mt-1 bg-white"
                    value={edited.allergies ?? ""}
                    onChange={(e) =>
                      setEdited({ ...edited, allergies: e.target.value })
                    }
                  />
                </div>
                <div>
                  <Label className="text-lg">Delivery Notes</Label>
                  <Textarea
                    className="text-lg mt-1 bg-white"
                    placeholder="e.g. Leave at front door"
                    value={edited.deliveryNotes ?? ""}
                    onChange={(e) =>
                      setEdited({ ...edited, deliveryNotes: e.target.value })
                    }
                  />
                </div>
                <div>
                  <Label className="text-lg">Emergency Contact</Label>
                  <Input
                    className="text-lg h-12 mt-1 bg-white"
                    value={edited.emergencyContact ?? ""}
                    onChange={(e) =>
                      setEdited({ ...edited, emergencyContact: e.target.value })
                    }
                  />
                </div>
              </div>
            </TabsContent>

            <TabsContent value="subscription" className="space-y-5 animate-in fade-in-50">
              <div>
                <Label className="text-lg mb-2 block">Member Status</Label>
                <div className="flex gap-2 flex-wrap">
                  {(["active", "paused", "cancelled", "trial"] as const).map((s) => (
                    <button
                      key={s}
                      type="button"
                      onClick={() => setEdited({ ...edited, memberStatus: s })}
                      className={`h-12 px-4 rounded-xl border-2 text-lg font-medium transition-all capitalize ${
                        edited.memberStatus === s
                          ? "border-orange-500 bg-orange-50 text-orange-700"
                          : "border-gray-200 bg-white text-gray-600 hover:border-gray-300"
                      }`}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <Label className="text-lg mb-2 block">Dietary Preference</Label>
                <div className="flex gap-2">
                  {(["veg", "non-veg", "vegan"] as const).map((s) => (
                    <button
                      key={s}
                      type="button"
                      onClick={() => setEdited({ ...edited, dietaryPreference: s })}
                      className={`h-12 flex-1 rounded-xl border-2 text-lg font-medium transition-all capitalize ${
                        edited.dietaryPreference === s
                          ? "border-orange-500 bg-orange-50 text-orange-700"
                          : "border-gray-200 bg-white text-gray-600 hover:border-gray-300"
                      }`}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-4 rounded-xl bg-gray-50 p-4">
                <p className="text-lg font-semibold">Plan Details</p>
                <div>
                  <Label className="text-lg text-gray-500">Plan ID</Label>
                  <Input
                    className="text-lg h-12 mt-1 bg-white"
                    value={edited.planId ?? ""}
                    onChange={(e) =>
                      setEdited({ ...edited, planId: e.target.value })
                    }
                  />
                </div>
                <div>
                  <Label className="text-lg text-gray-500">Join Date</Label>
                  <p className="text-xl font-medium mt-0.5">{edited.joinDate ?? edited.joinedDate ?? "—"}</p>
                </div>
                <div>
                  <Label className="text-lg mb-2 block">Renewal Info</Label>
                  <p className={`text-base font-medium mt-1 ${isOverdue ? "text-red-600" : "text-amber-600"}`}>
                    {renewalText}
                  </p>
                </div>
              </div>

              <Button
                className="w-full h-14 text-lg font-bold bg-amber-500 hover:bg-amber-600 mt-4"
                onClick={() =>
                  setEdited({
                    ...edited,
                    memberStatus: "active",
                    renewalDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
                      .toISOString()
                      .split("T")[0],
                  })
                }
              >
                Confirm Renewal
              </Button>
            </TabsContent>
          </Tabs>
        </div>

        {/* ── Sticky footer ── */}
        <div className="shrink-0 border-t border-gray-100 bg-white px-6 py-4 flex gap-3">
          <Button
            className="flex-1 h-14 text-lg font-semibold bg-orange-500 hover:bg-orange-600 text-white"
            onClick={handleSave}
          >
            Save
          </Button>
          <Button
            variant="outline"
            className="flex-1 h-14 text-lg font-semibold border-2"
            onClick={onClose}
          >
            Cancel
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
