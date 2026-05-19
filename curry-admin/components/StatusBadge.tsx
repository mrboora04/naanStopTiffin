"use client";

import { Badge } from "@/components/ui/badge";

type Variant = "success" | "error" | "warning" | "info" | "default";

const styles: Record<Variant, string> = {
  success: "bg-green-100 text-green-700 border-green-200",
  error: "bg-red-100 text-red-700 border-red-200",
  warning: "bg-amber-100 text-amber-700 border-amber-200",
  info: "bg-blue-100 text-blue-700 border-blue-200",
  default: "bg-gray-100 text-gray-700 border-gray-200",
};

export default function StatusBadge({
  label,
  variant = "default",
}: {
  label: string;
  variant?: Variant;
}) {
  return (
    <Badge
      variant="outline"
      className={`text-base px-3 py-1 ${styles[variant]}`}
    >
      {label}
    </Badge>
  );
}
