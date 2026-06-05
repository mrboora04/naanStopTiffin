import { cn } from "@/lib/utils";

interface SpinnerProps {
  size?: "sm" | "md" | "lg";
  className?: string;
  label?: string;
}

const sizeMap = {
  sm: "w-4 h-4 border-2",
  md: "w-6 h-6 border-2",
  lg: "w-10 h-10 border-[3px]",
};

/**
 * Accessible loading spinner.
 * Uses CSS border trick — no SVG, no JS animation overhead.
 */
export function Spinner({ size = "md", className, label = "Loading…" }: SpinnerProps) {
  return (
    <span
      role="status"
      aria-label={label}
      className={cn(
        "inline-block rounded-full border-gray-200 border-t-orange-500 animate-spin",
        sizeMap[size],
        className
      )}
    />
  );
}
