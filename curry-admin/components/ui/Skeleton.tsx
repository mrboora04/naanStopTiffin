import { cn } from "@/lib/utils";

interface SkeletonProps {
  className?: string;
}

/**
 * Shape-accurate skeleton loader — use className to control dimensions.
 * Animates a shimmer rather than a flat pulse for a more premium feel.
 */
export function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={cn(
        "rounded-lg bg-gradient-to-r from-gray-100 via-gray-200 to-gray-100 bg-[length:200%_100%] animate-[shimmer_1.5s_ease-in-out_infinite]",
        className
      )}
      style={{
        animation: "shimmer 1.5s ease-in-out infinite",
      }}
    />
  );
}

/**
 * Pre-built table skeleton that exactly mimics the delivery/member table shape.
 */
export function TableSkeleton({ rows = 5, cols = 5 }: { rows?: number; cols?: number }) {
  return (
    <div className="divide-y divide-gray-100" role="status" aria-label="Loading table data">
      {Array.from({ length: rows }).map((_, r) => (
        <div key={r} className="flex items-center gap-4 px-6 py-4">
          {Array.from({ length: cols }).map((_, c) => (
            <Skeleton
              key={c}
              className={`h-4 ${c === 0 ? "w-36" : c === cols - 1 ? "w-16 ml-auto" : "w-24"}`}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

/**
 * Pre-built stat card skeleton grid for the dashboard.
 */
export function StatCardSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6" role="status" aria-label="Loading dashboard stats">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="bg-white rounded-2xl p-6 border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <Skeleton className="h-4 w-28" />
            <Skeleton className="h-10 w-10 rounded-xl" />
          </div>
          <Skeleton className="h-10 w-20 mt-2" />
          <Skeleton className="h-3 w-24 mt-3" />
        </div>
      ))}
    </div>
  );
}
