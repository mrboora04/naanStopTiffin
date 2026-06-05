import { buildMetadata } from "@/lib/metadata";

export const metadata = buildMetadata(
  "Members",
  "Manage subscriber profiles, dietary preferences, and renewal dates"
);

export default function MembersLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
