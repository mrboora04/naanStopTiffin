"use client";

import { useState, ReactNode } from "react";
import { Toaster } from "sonner";
import { LanguageProvider } from "@/contexts/LanguageContext";
import { AppProvider } from "@/contexts/AppContext";
import Sidebar from "@/components/Sidebar";
import TopBar from "@/components/TopBar";
import BottomNav from "@/components/BottomNav";

/**
 * AppShell — root layout shell.
 *
 * Architecture:
 *  - LanguageProvider & AppProvider wrap everything (single provider tree)
 *  - Sidebar: desktop left rail (lg+)
 *  - BottomNav: mobile thumb-friendly bottom navigation (< lg)
 *  - TopBar: sticky header with breadcrumbs + language toggle
 *  - Toaster: global toast notifications (Sonner)
 */
export default function AppShell({ children }: { children: ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <LanguageProvider>
      <AppProvider>
        <div className="min-h-screen bg-gray-50">
          {/* Desktop sidebar */}
          <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

          {/* Main content area — offset by sidebar width on desktop */}
          <div className="lg:ml-[260px] flex flex-col min-h-screen pb-16 lg:pb-0">
            <TopBar onMenuClick={() => setSidebarOpen(true)} />
            <main className="flex-1 p-4 lg:p-6">{children}</main>
          </div>

          {/* Mobile bottom navigation bar */}
          <BottomNav />

          {/* Global toast notifications */}
          <Toaster
            position="bottom-right"
            richColors
            expand={false}
            duration={4000}
            toastOptions={{
              style: { fontFamily: "inherit" },
            }}
          />
        </div>
      </AppProvider>
    </LanguageProvider>
  );
}
