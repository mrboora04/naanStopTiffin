"use client";

import { usePathname } from "next/navigation";
import { Menu, ChevronRight, User, LogOut, Settings } from "lucide-react";
import { useState } from "react";
import { useLanguage } from "@/contexts/LanguageContext";
import { Button } from "@/components/ui/button";

/** Maps route segments to human-readable labels */
const routeLabels: Record<string, string> = {
  dashboard:  "Dashboard",
  members:    "Members",
  deliveries: "Deliveries",
  schedule:   "Schedule",
  requests:   "Requests",
  pricing:    "Pricing",
  comments:   "Comments",
  pilot:      "Pilot Lab",
  settings:   "Settings",
};

function Breadcrumbs() {
  const pathname = usePathname();
  const segments = pathname.split("/").filter(Boolean);

  if (segments.length === 0) return null;

  return (
    <nav aria-label="Breadcrumb" className="hidden sm:flex items-center gap-1 text-sm">
      <span className="text-gray-400 font-medium">Curry Admin</span>
      {segments.map((seg, i) => {
        const label = routeLabels[seg] ?? seg.charAt(0).toUpperCase() + seg.slice(1);
        const isLast = i === segments.length - 1;
        return (
          <span key={seg} className="flex items-center gap-1">
            <ChevronRight className="w-3.5 h-3.5 text-gray-300 shrink-0" />
            <span
              className={
                isLast
                  ? "font-semibold text-gray-900"
                  : "text-gray-400 hover:text-gray-700 cursor-pointer"
              }
            >
              {label}
            </span>
          </span>
        );
      })}
    </nav>
  );
}

function ProfileMenu() {
  const [open, setOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        aria-label="Open profile menu"
        aria-expanded={open}
        className="flex items-center gap-2 h-11 px-3 rounded-xl hover:bg-gray-100 transition-colors text-gray-700"
      >
        <div className="w-8 h-8 rounded-full bg-orange-100 flex items-center justify-center">
          <User className="w-4 h-4 text-orange-600" />
        </div>
        <span className="hidden md:block text-sm font-medium">Admin</span>
      </button>

      {open && (
        <>
          {/* Click-away overlay */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setOpen(false)}
          />
          <div className="absolute right-0 top-full mt-2 z-50 w-52 bg-white rounded-2xl shadow-xl border border-gray-100 py-2 overflow-hidden">
            <div className="px-4 py-3 border-b border-gray-100">
              <p className="text-sm font-semibold text-gray-900">Curry Admin</p>
              <p className="text-xs text-gray-400">admin@curryinbarrie.ca</p>
            </div>
            <button
              onClick={() => setOpen(false)}
              className="w-full flex items-center gap-3 px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
            >
              <Settings className="w-4 h-4 text-gray-400" />
              Account Settings
            </button>
            <button
              onClick={() => setOpen(false)}
              className="w-full flex items-center gap-3 px-4 py-3 text-sm text-red-600 hover:bg-red-50 transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Sign Out
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default function TopBar({ onMenuClick }: { onMenuClick: () => void }) {
  const { language, setLanguage } = useLanguage();

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between h-16 px-4 lg:px-6 bg-white/95 backdrop-blur-sm border-b border-gray-200 gap-4">
      {/* Mobile hamburger (lg: hidden — sidebar slides in; mobile only) */}
      <button
        onClick={onMenuClick}
        aria-label="Open menu"
        className="lg:hidden flex items-center gap-2 px-3 h-12 rounded-xl hover:bg-gray-100 text-gray-700 shrink-0"
      >
        <Menu className="w-6 h-6" />
        <span className="text-base font-medium">Menu</span>
      </button>

      {/* Breadcrumbs — shows on desktop */}
      <div className="flex-1 min-w-0">
        <Breadcrumbs />
      </div>

      {/* Right controls: language toggle + profile */}
      <div className="flex items-center gap-2 shrink-0">
        {/* Language toggle */}
        <div className="flex items-center gap-1">
          <Button
            variant={language === "en" ? "default" : "outline"}
            onClick={() => setLanguage("en")}
            className={`h-10 text-sm font-semibold min-w-[48px] rounded-xl ${
              language === "en"
                ? "bg-orange-500 hover:bg-orange-600 text-white border-transparent"
                : "border-2 border-gray-200 text-gray-600 hover:bg-gray-50"
            }`}
          >
            EN
          </Button>
          <Button
            variant={language === "hi" ? "default" : "outline"}
            onClick={() => setLanguage("hi")}
            className={`h-10 text-sm font-semibold min-w-[48px] rounded-xl ${
              language === "hi"
                ? "bg-orange-500 hover:bg-orange-600 text-white border-transparent"
                : "border-2 border-gray-200 text-gray-600 hover:bg-gray-50"
            }`}
          >
            हिं
          </Button>
        </div>

        <ProfileMenu />
      </div>
    </header>
  );
}
