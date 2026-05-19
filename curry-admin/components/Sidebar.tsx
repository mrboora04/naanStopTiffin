"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  Bike,
  CalendarDays,
  ClipboardList,
  DollarSign,
  MessageCircle,
  FlaskConical,
  Settings as SettingsIcon,
  X,
} from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";

const navItems = [
  { href: "/dashboard", icon: LayoutDashboard, labelKey: "dashboard" as const },
  { href: "/members", icon: Users, labelKey: "members" as const },
  { href: "/deliveries", icon: Bike, labelKey: "deliveries" as const },
  { href: "/schedule", icon: CalendarDays, labelKey: "schedule" as const },
  { href: "/requests", icon: ClipboardList, labelKey: "requests" as const },
  { href: "/pricing", icon: DollarSign, labelKey: "pricing" as const },
  { href: "/comments", icon: MessageCircle, labelKey: "comments" as const },
  { href: "/pilot", icon: FlaskConical, labelKey: "pilotLab" as const },
  { href: "/settings", icon: SettingsIcon, labelKey: "settings" as const },
];

export default function Sidebar({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const pathname = usePathname();
  const { t } = useLanguage();

  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/30 lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed top-0 left-0 z-50 h-full w-[260px] bg-white border-r border-gray-200 flex flex-col transition-transform duration-200 lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-gray-100">
          <h1 className="text-xl font-bold text-orange-500">
            🍱 Curry in Barrie
          </h1>
          <button
            onClick={onClose}
            aria-label="Close menu"
            className="lg:hidden flex items-center gap-1.5 h-12 px-3 rounded-xl hover:bg-gray-100 text-gray-600 text-lg font-medium"
          >
            <X className="w-5 h-5" />
            Close
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onClose}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-lg transition-colors ${
                  isActive
                    ? "font-bold text-orange-600 bg-orange-50 border-l-4 border-orange-500"
                    : "text-gray-600 hover:bg-gray-50 hover:text-gray-900 border-l-4 border-transparent"
                }`}
              >
                <Icon className="w-5 h-5 shrink-0" />
                {t[item.labelKey]}
              </Link>
            );
          })}
        </nav>
      </aside>
    </>
  );
}
