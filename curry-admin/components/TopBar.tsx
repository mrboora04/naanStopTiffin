"use client";

import { Menu } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";
import { Button } from "@/components/ui/button";

export default function TopBar({ onMenuClick }: { onMenuClick: () => void }) {
  const { language, setLanguage } = useLanguage();

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between h-20 px-4 lg:px-6 bg-white border-b border-gray-200">
      {/* Mobile hamburger — larger tap target with text label */}
      <button
        onClick={onMenuClick}
        aria-label="Open menu"
        className="lg:hidden flex items-center gap-2 px-3 h-14 rounded-xl hover:bg-gray-100 text-gray-700"
      >
        <Menu className="w-7 h-7" />
        <span className="text-lg font-medium">Menu</span>
      </button>

      <div className="hidden lg:block" />

      {/* Language toggle — enlarged for elderly users */}
      <div className="flex items-center gap-1">
        <span className="text-base text-gray-400 mr-2 hidden sm:block">Language:</span>
        <Button
          variant={language === "en" ? "default" : "outline"}
          onClick={() => setLanguage("en")}
          className={`h-14 text-lg font-semibold min-w-[64px] rounded-xl ${
            language === "en"
              ? "bg-orange-500 hover:bg-orange-600 text-white"
              : "border-2 border-gray-300 text-gray-600 hover:bg-gray-50"
          }`}
        >
          EN
        </Button>
        <Button
          variant={language === "hi" ? "default" : "outline"}
          onClick={() => setLanguage("hi")}
          className={`h-14 text-lg font-semibold min-w-[64px] rounded-xl ${
            language === "hi"
              ? "bg-orange-500 hover:bg-orange-600 text-white"
              : "border-2 border-gray-300 text-gray-600 hover:bg-gray-50"
          }`}
        >
          हिं
        </Button>
      </div>
    </header>
  );
}
