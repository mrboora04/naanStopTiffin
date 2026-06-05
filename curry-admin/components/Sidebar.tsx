"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
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
  ChevronDown,
} from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";

/** Navigation groups — primary ones always show, secondary are collapsible */
const primaryNavItems = [
  { href: "/dashboard",  icon: LayoutDashboard, labelKey: "dashboard"  as const },
  { href: "/members",    icon: Users,           labelKey: "members"    as const },
  { href: "/deliveries", icon: Bike,            labelKey: "deliveries" as const },
  { href: "/schedule",   icon: CalendarDays,    labelKey: "schedule"   as const },
  { href: "/requests",   icon: ClipboardList,   labelKey: "requests"   as const },
];

const secondaryNavItems = [
  { href: "/pricing",   icon: DollarSign,    labelKey: "pricing"   as const },
  { href: "/comments",  icon: MessageCircle, labelKey: "comments"  as const },
  { href: "/pilot",     icon: FlaskConical,  labelKey: "pilotLab"  as const },
  { href: "/settings",  icon: SettingsIcon,  labelKey: "settings"  as const },
];

function NavItem({ href, icon: Icon, label, onClick }: {
  href: string;
  icon: React.ElementType;
  label: string;
  onClick?: () => void;
}) {
  const pathname = usePathname();
  const isActive = pathname === href || pathname.startsWith(href + "/");

  return (
    <Link
      href={href}
      onClick={onClick}
      aria-current={isActive ? "page" : undefined}
      className={`flex items-center gap-3 px-4 py-3 rounded-xl text-base font-medium transition-all duration-150 ${
        isActive
          ? "font-bold text-orange-600 bg-orange-50 border-l-4 border-orange-500 pl-3"
          : "text-gray-600 hover:bg-gray-50 hover:text-gray-900 border-l-4 border-transparent"
      }`}
    >
      <Icon
        className={`w-5 h-5 shrink-0 ${isActive ? "stroke-[2.5]" : "stroke-[1.75]"}`}
        aria-hidden="true"
      />
      {label}
    </Link>
  );
}

export default function Sidebar({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const { t } = useLanguage();
  const [moreOpen, setMoreOpen] = useState(false);

  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/30 lg:hidden backdrop-blur-[2px]"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed top-0 left-0 z-50 h-full w-[260px] bg-white border-r border-gray-200 flex flex-col transition-transform duration-200 ease-out lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
        aria-label="Primary navigation"
      >
        {/* Brand header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-gray-100 shrink-0">
          <div className="flex items-center gap-2">
            <span className="text-2xl" aria-hidden="true">🍱</span>
            <span className="text-lg font-bold text-orange-500 leading-tight">
              Curry in Barrie
            </span>
          </div>
          <button
            onClick={onClose}
            aria-label="Close menu"
            className="lg:hidden p-2 rounded-xl hover:bg-gray-100 text-gray-500 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Primary nav */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto" aria-label="Main navigation">
          {primaryNavItems.map((item) => (
            <NavItem
              key={item.href}
              href={item.href}
              icon={item.icon}
              label={t[item.labelKey]}
              onClick={onClose}
            />
          ))}

          {/* Collapsible "More" section */}
          <div className="pt-2">
            <button
              onClick={() => setMoreOpen((o) => !o)}
              aria-expanded={moreOpen}
              className="w-full flex items-center justify-between px-4 py-2 text-xs font-bold text-gray-400 uppercase tracking-widest hover:text-gray-600 transition-colors rounded-lg hover:bg-gray-50"
            >
              <span>More</span>
              <ChevronDown
                className={`w-4 h-4 transition-transform duration-200 ${moreOpen ? "rotate-180" : ""}`}
              />
            </button>
            {moreOpen && (
              <div className="mt-1 space-y-1 animate-in slide-in-from-top-2 duration-150">
                {secondaryNavItems.map((item) => (
                  <NavItem
                    key={item.href}
                    href={item.href}
                    icon={item.icon}
                    label={t[item.labelKey]}
                    onClick={onClose}
                  />
                ))}
              </div>
            )}
          </div>
        </nav>

        {/* Footer */}
        <div className="shrink-0 px-4 py-4 border-t border-gray-100">
          <p className="text-xs text-gray-300 text-center">Curry Admin v0.1</p>
        </div>
      </aside>
    </>
  );
}
