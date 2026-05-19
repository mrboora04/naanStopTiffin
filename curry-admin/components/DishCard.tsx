"use client";

import { useState } from "react";
import { Trash2 } from "lucide-react";
import { Dish } from "@/types";
import ConfirmDialog from "@/components/ConfirmDialog";

export default function DishCard({
  dish,
  onRemove,
  onClick,
}: {
  dish: Dish;
  onRemove?: () => void;
  onClick?: () => void;
}) {
  const [confirmOpen, setConfirmOpen] = useState(false);

  return (
    <>
      <div className="rounded-2xl overflow-hidden shadow-[0_4px_20px_rgb(0,0,0,0.03)] border border-gray-100 bg-white hover:shadow-md transition-all cursor-pointer" onClick={onClick}>
        <div className="relative p-6 pb-4">
          <div className="flex justify-between items-start mb-2">
            <h3 className="text-xl font-bold text-gray-900">{dish.name}</h3>
            {onRemove && (
              <button
                onClick={(e) => { e.stopPropagation(); setConfirmOpen(true); }}
                aria-label={`Remove ${dish.name}`}
                className="flex items-center justify-center w-8 h-8 rounded-full bg-red-50 text-red-600 hover:bg-red-100 transition-colors"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>
          <div className="flex gap-2 mt-2">
            <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs font-semibold uppercase rounded-md tracking-wider">
              {dish.category ?? ""}
            </span>
            <span className={`px-2 py-1 text-xs font-semibold uppercase rounded-md tracking-wider ${
              dish.dietaryType === 'veg' ? 'bg-green-100 text-green-700' :
              dish.dietaryType === 'vegan' ? 'bg-emerald-100 text-emerald-700' :
              'bg-red-100 text-red-700'
            }`}>
              {dish.dietaryType ?? ""}
            </span>
          </div>
        </div>
        <div className="px-6 pb-6">
          <p className="text-sm font-medium text-gray-500 mb-1">Ingredients</p>
          <p className="text-sm text-gray-700 line-clamp-2">
            {(dish.ingredients ?? []).join(", ")}

          </p>
        </div>
      </div>

      {/* Confirmation — must confirm before dish is removed */}
      {onRemove && (
        <ConfirmDialog
          open={confirmOpen}
          title="Remove this dish?"
          message={`Remove "${dish.name}" from today's menu? This cannot be undone.`}
          confirmLabel="Yes, Remove"
          confirmVariant="danger"
          onConfirm={() => { setConfirmOpen(false); onRemove(); }}
          onCancel={() => setConfirmOpen(false)}
        />
      )}
    </>
  );
}
