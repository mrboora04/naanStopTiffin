"use client";

import { Component, ReactNode } from "react";
import { WifiOff, RefreshCw } from "lucide-react";

interface Props {
  children: ReactNode;
  /** Optional custom fallback — defaults to a card with icon + retry */
  fallback?: ReactNode;
  /** Section name shown in the error message */
  section?: string;
}

interface State {
  hasError: boolean;
  error?: Error;
}

/**
 * Granular Error Boundary.
 *
 * Wraps individual sections of the UI so one broken component
 * doesn't take down the whole page. Shows a friendly retry card
 * with the section name so admins know exactly what failed.
 *
 * Usage:
 *   <ErrorBoundary section="Deliveries Table">
 *     <DeliveriesTable />
 *   </ErrorBoundary>
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: { componentStack: string }) {
    // In production you'd send this to a logging service
    console.error(`[ErrorBoundary:${this.props.section ?? "unknown"}]`, error, info);
  }

  reset = () => this.setState({ hasError: false, error: undefined });

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;

      return (
        <div className="flex flex-col items-center justify-center gap-4 py-12 px-6 text-center rounded-2xl border border-dashed border-orange-200 bg-orange-50/40">
          <div className="p-3 rounded-2xl bg-white shadow-sm">
            <WifiOff className="w-8 h-8 text-orange-400" />
          </div>
          <div>
            <p className="font-semibold text-gray-900">
              {this.props.section ? `"${this.props.section}" could not load` : "Something went wrong"}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              {this.state.error?.message ?? "An unexpected error occurred in this section."}
            </p>
          </div>
          <button
            onClick={this.reset}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white border border-gray-200 text-sm font-semibold text-gray-700 hover:bg-gray-50 shadow-sm transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
