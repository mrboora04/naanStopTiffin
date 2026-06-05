"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  Bike,
  CalendarDays,
  ClipboardList,
} from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";

/**
 * BottomNav — mobile-first thumb-friendly navigation bar.
 *
 * Design decisions:
 * - Only 5 primary items (cognitive load limit for mobile)
 * - Large tap targets (min 48px height per WCAG)
 * - Active state uses brand orange with filled icon background
 * - Visible on mobile/tablet (< lg), hidden on desktop
 * - Fixed to bottom so it sits near the user's thumb naturally
 */
const bottomNavItems = [
  { href: "/dashboard",  icon: LayoutDashboard, label: "Home" },
  { href: "/members",    icon: Users,           label: "Members" },
  { href: "/deliveries", icon: Bike,            label: "Deliver" },
  { href: "/schedule",   icon: CalendarDays,    label: "Schedule" },
  { href: "/requests",   icon: ClipboardList,   label: "Requests" },
];

export default function BottomNav() {
  const pathname = usePathname();

  return (
    <nav
      className="lg:hidden fixed bottom-0 inset-x-0 z-50 bg-white border-t border-gray-200 safe-area-pb"
      aria-label="Mobile navigation"
    >
      <div className="flex items-stretch h-16">
        {bottomNavItems.map((item) => {
          const isActive =
            pathname === item.href || pathname.startsWith(item.href + "/");
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              aria-label={item.label}
              aria-current={isActive ? "page" : undefined}
              className="flex-1 flex flex-col items-center justify-center gap-1 transition-colors"
            >
              <span
                className={`p-1.5 rounded-xl transition-all duration-200 ${
                  isActive
                    ? "bg-orange-50 text-orange-700"
                    : "text-gray-600 hover:text-gray-800"
                }`}
              >
                <Icon
                  className={`w-5 h-5 ${isActive ? "stroke-[2.5]" : "stroke-[1.75]"}`}
                />
              </span>
              <span
                className={`text-[10px] font-semibold tracking-wide ${
                  isActive ? "text-orange-700" : "text-gray-600"
                }`}
              >
                {item.label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
