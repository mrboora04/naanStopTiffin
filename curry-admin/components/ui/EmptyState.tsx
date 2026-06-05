import { PackageOpen, SearchX, WifiOff, ShieldAlert, Truck } from "lucide-react";
import { ReactNode } from "react";

type EmptyStateType = "no-data" | "no-results" | "error" | "no-deliveries" | "no-members";

interface EmptyStateProps {
  type?: EmptyStateType;
  title?: string;
  description?: string;
  action?: ReactNode;
}

const presets: Record<EmptyStateType, { icon: ReactNode; title: string; description: string }> = {
  "no-data": {
    icon: <PackageOpen className="w-12 h-12 text-gray-300" />,
    title: "Nothing here yet",
    description: "Add your first record to get started.",
  },
  "no-results": {
    icon: <SearchX className="w-12 h-12 text-gray-300" />,
    title: "No results found",
    description: "Try adjusting your search or clearing your filters.",
  },
  "error": {
    icon: <WifiOff className="w-12 h-12 text-orange-300" />,
    title: "Couldn't load data",
    description: "Check that the backend server is running and try again.",
  },
  "no-deliveries": {
    icon: <Truck className="w-12 h-12 text-gray-300" />,
    title: "All clear — no deliveries today",
    description: "No deliveries are scheduled. Add one to get the route rolling.",
  },
  "no-members": {
    icon: <ShieldAlert className="w-12 h-12 text-gray-300" />,
    title: "No subscribers yet",
    description: "Add your first subscriber to start managing meals.",
  },
};

/**
 * Smart empty state with contextual icons and messaging.
 * Replaces plain-text fallbacks across the app.
 */
export function EmptyState({ type = "no-data", title, description, action }: EmptyStateProps) {
  const preset = presets[type];
  return (
    <div className="flex flex-col items-center justify-center py-16 px-6 text-center gap-4">
      <div className="p-4 rounded-2xl bg-gray-50 mb-2">{preset.icon}</div>
      <h3 className="text-lg font-semibold text-gray-800">{title ?? preset.title}</h3>
      <p className="text-sm text-gray-500 max-w-xs">{description ?? preset.description}</p>
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}
