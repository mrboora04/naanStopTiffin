"use client";

import { ReactNode } from "react";

export default function StatCard({
  label,
  value,
  icon,
  highlight,
}: {
  label: string;
  value: string | number;
  icon: ReactNode;
  highlight?: boolean;
}) {
  return (
    <div
      className={`rounded-2xl p-6 shadow-sm border ${
        highlight
          ? "bg-orange-50 border-orange-200"
          : "bg-white border-gray-100"
      }`}
    >
      <div className="flex items-center gap-3 mb-2">
        <div className="text-orange-500">{icon}</div>
        <p className="text-lg text-gray-500">{label}</p>
      </div>
      <p className="text-3xl font-bold text-gray-900">{value}</p>
    </div>
  );
}
