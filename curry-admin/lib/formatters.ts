/**
 * Data formatting utilities for the curry-admin frontend.
 *
 * Centralises all display-layer transforms so components never
 * do raw string manipulation inline.
 */

/** Format a number as Canadian currency */
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-CA", {
    style: "currency",
    currency: "CAD",
    maximumFractionDigits: 0,
  }).format(amount);
}

/** Format a phone number: "6471234567" → "(647) 123-4567" */
export function formatPhone(raw: string): string {
  const digits = raw.replace(/\D/g, "");
  if (digits.length === 10) {
    return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`;
  }
  return raw;
}

/** Format a date string as "Jun 3, 2026" */
export function formatDate(dateStr: string | undefined | null): string {
  if (!dateStr) return "—";
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return dateStr;
  return d.toLocaleDateString("en-CA", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

/** Return relative time: "2 hours ago", "just now", "in 3 days" */
export function formatRelativeTime(dateStr: string | undefined | null): string {
  if (!dateStr) return "—";
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return dateStr;
  const seconds = Math.floor((d.getTime() - Date.now()) / 1000);
  const abs = Math.abs(seconds);

  if (abs < 60)    return "just now";
  if (abs < 3600)  return `${Math.floor(abs / 60)} min${abs < 120 ? "" : "s"} ${seconds < 0 ? "ago" : "from now"}`;
  if (abs < 86400) return `${Math.floor(abs / 3600)} hr${abs < 7200 ? "" : "s"} ${seconds < 0 ? "ago" : "from now"}`;
  return `${Math.floor(abs / 86400)} day${abs < 172800 ? "" : "s"} ${seconds < 0 ? "ago" : "from now"}`;
}

/** Capitalise and replace hyphens for status display: "out-for-delivery" → "Out For Delivery" */
export function formatStatus(status: string): string {
  return status
    .replace(/-/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}
