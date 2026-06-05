"use client";

import { ReactNode } from "react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatCardProps {
  label: string;
  value: string | number;
  icon: ReactNode;
  highlight?: boolean;
  /** Optional trend vs. yesterday/last period */
  trend?: {
    value: number;      // percentage e.g. 12.5
    direction: "up" | "down" | "flat";
    label?: string;     // e.g. "vs yesterday"
  };
  className?: string;
}

/**
 * KPI stat card with optional trend indicator arrow.
 * Uses .card-hover CSS utility for micro-interaction lift on hover.
 */
export default function StatCard({
  label,
  value,
  icon,
  highlight,
  trend,
  className,
}: StatCardProps) {
  const TrendIcon =
    trend?.direction === "up" ? TrendingUp :
    trend?.direction === "down" ? TrendingDown : Minus;

  const trendColor =
    trend?.direction === "up" ? "text-green-700" :
    trend?.direction === "down" ? "text-red-600" : "text-gray-500";

  return (
    <div
      className={cn(
        "rounded-2xl p-6 shadow-sm border card-hover",
        highlight
          ? "bg-orange-50 border-orange-200"
          : "bg-white border-gray-100",
        className
      )}
    >
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider">{label}</p>
        <div className="text-orange-500">{icon}</div>
      </div>
      <p className="text-4xl font-black text-gray-900 leading-none">{value}</p>
      {trend && (
        <div className={cn("flex items-center gap-1 mt-3 text-xs font-semibold", trendColor)}>
          <TrendIcon className="w-3.5 h-3.5" />
          <span>
            {trend.direction !== "flat" && `${trend.value > 0 ? "+" : ""}${trend.value}%`}
            {trend.direction === "flat" && "No change"}
            {trend.label && ` ${trend.label}`}
          </span>
        </div>
      )}
    </div>
  );
}
