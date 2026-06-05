import type { Metadata } from "next";

const SITE_NAME = "Curry Admin";

/**
 * Helper to create consistent Next.js page metadata.
 * Always appends "| Curry Admin" so the browser tab is always clear.
 *
 * Usage in a page or layout:
 *   export const metadata = buildMetadata("Members");
 *   // → { title: "Members | Curry Admin", description: "..." }
 */
export function buildMetadata(
  pageName: string,
  description?: string
): Metadata {
  return {
    title: `${pageName} | ${SITE_NAME}`,
    description:
      description ??
      `${pageName} — Curry in Barrie tiffin service admin panel`,
  };
}
