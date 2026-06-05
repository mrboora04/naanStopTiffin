import { buildMetadata } from "@/lib/metadata";

export const metadata = buildMetadata(
  "Dashboard",
  "Live overview of active members, deliveries, revenue, and pending requests"
);

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
