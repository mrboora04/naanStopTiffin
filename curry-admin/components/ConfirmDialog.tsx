"use client";

import { useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { AlertTriangle } from "lucide-react";

/**
 * Granny-friendly confirmation dialog.
 * Large buttons, clear language, no tiny X to hunt for.
 * Cancel is always left/top so accidental taps default to safety.
 */
export default function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel,
  confirmVariant = "danger",
  onConfirm,
  onCancel,
}: {
  open: boolean;
  title: string;
  message: string;
  confirmLabel: string;
  confirmVariant?: "danger" | "warning";
  onConfirm: () => void;
  onCancel: () => void;
}) {
  // Keyboard accessibility: Escape to cancel, Enter to confirm
  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") { e.preventDefault(); onCancel(); }
      if (e.key === "Enter")  { e.preventDefault(); onConfirm(); onCancel(); }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [open, onConfirm, onCancel]);

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onCancel()}>
      <DialogContent
        className="max-w-sm flex flex-col p-0 gap-0 overflow-hidden"
        showCloseButton={false}
      >
        {/* Header */}
        <DialogHeader className="px-6 pt-6 pb-4 shrink-0">
          <div className="flex items-center gap-3">
            <AlertTriangle
              className={`w-7 h-7 shrink-0 ${
                confirmVariant === "danger" ? "text-red-500" : "text-amber-500"
              }`}
            />
            <DialogTitle className="text-xl leading-tight">{title}</DialogTitle>
          </div>
        </DialogHeader>

        {/* Message */}
        <p className="px-6 pb-6 text-lg text-gray-600 leading-relaxed">
          {message}
        </p>

        {/* Sticky footer — Cancel first (safer default for accidental taps) */}
        <div className="shrink-0 border-t border-gray-100 bg-white px-6 py-4 flex gap-3">
          <Button
            variant="outline"
            className="flex-1 h-14 text-lg font-semibold border-2"
            onClick={onCancel}
          >
            Cancel
          </Button>
          <Button
            className={`flex-1 h-14 text-lg font-semibold ${
              confirmVariant === "danger"
                ? "bg-red-600 hover:bg-red-700"
                : "bg-amber-500 hover:bg-amber-600"
            }`}
            onClick={() => {
              onConfirm();
              onCancel();
            }}
          >
            {confirmLabel}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
