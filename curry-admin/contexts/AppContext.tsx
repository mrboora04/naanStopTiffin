"use client";

/**
 * AppContext — Central data layer for the NaanStop admin frontend.
 *
 * All data fetching goes through this context via the `api` helper,
 * which talks to the Python FastAPI backend at NEXT_PUBLIC_API_URL.
 *
 * Usage in any page/component:
 *   const { members, deliveries, refetch } = useAppContext();
 */

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from "react";
import type {
  Member,
  Delivery,
  ScheduleDay,
  PricingPlan,
  TrialRequest,
  Feedback,
  PilotProgram,
  Payment,
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ── Generic fetch helper ────────────────────────────────────────────────────

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    // Parse RFC 7807 Problem Details if available
    let detail = `API error ${res.status}: ${path}`;
    try {
      const body = await res.json();
      if (body.detail) detail = body.detail;
      else if (body.title) detail = `${body.title}: ${body.detail ?? ""}`;
    } catch {}
    throw new Error(detail);
  }
  // 204 No Content — return empty
  if (res.status === 204) return undefined as unknown as T;
  return res.json() as Promise<T>;
}

/**
 * List fetch: extracts `.items` from paginated responses.
 * All /api/v1/* list endpoints return { items, count, next_cursor, has_more }.
 */
async function apiList<T>(path: string): Promise<T[]> {
  const data = await apiFetch<{ items: T[] } | T[]>(path);
  if (Array.isArray(data)) return data;
  return (data as { items: T[] }).items ?? [];
}

/** Typed API client — import and use anywhere you need direct calls */
export const api = {
  // Members
  getMembers:      ()              => apiList<Member>("/api/v1/members"),
  createMember:    (d: Omit<Member, "id">) => apiFetch<Member>("/api/v1/members", { method: "POST", body: JSON.stringify(d) }),
  updateMember:    (id: string, d: Partial<Member>) => apiFetch<Member>(`/api/v1/members/${id}`, { method: "PUT", body: JSON.stringify(d) }),
  deleteMember:    (id: string)    => apiFetch<void>(`/api/v1/members/${id}`, { method: "DELETE" }),

  // Deliveries
  getDeliveries:   ()              => apiList<Delivery>("/api/v1/deliveries"),
  createDelivery:  (d: Omit<Delivery, "id">) => apiFetch<Delivery>("/api/v1/deliveries", { method: "POST", body: JSON.stringify(d) }),
  updateDelivery:  (id: string, d: Partial<Delivery>) => apiFetch<Delivery>(`/api/v1/deliveries/${id}`, { method: "PUT", body: JSON.stringify(d) }),

  // Schedule
  getSchedule:     ()              => apiList<ScheduleDay>("/api/v1/schedule"),
  updateScheduleDay: (id: string, d: Partial<ScheduleDay>) => apiFetch<ScheduleDay>(`/api/v1/schedule/${id}`, { method: "PUT", body: JSON.stringify(d) }),

  // Pricing
  getPricingPlans: ()              => apiList<PricingPlan>("/api/v1/pricing"),
  updatePlan:      (id: string, d: Partial<PricingPlan>) => apiFetch<PricingPlan>(`/api/v1/pricing/${id}`, { method: "PUT", body: JSON.stringify(d) }),

  // Trial Requests
  getRequests:     ()              => apiList<TrialRequest>("/api/v1/requests"),
  updateRequest:   (id: string, d: Partial<TrialRequest>) => apiFetch<TrialRequest>(`/api/v1/requests/${id}`, { method: "PUT", body: JSON.stringify(d) }),

  // Feedback
  getFeedback:     ()              => apiList<Feedback>("/api/v1/comments"),
  updateFeedback:  (id: string, d: Partial<Feedback>) => apiFetch<Feedback>(`/api/v1/comments/${id}`, { method: "PUT", body: JSON.stringify(d) }),

  // Pilot
  getPilots:       ()              => apiList<PilotProgram>("/api/v1/pilot"),

  // Payments
  getPayments:     ()              => apiList<Payment>("/api/v1/payments"),

  // Dashboard
  getDashboard:    ()              => apiFetch<{ activeMembers: number; totalMembers: number; totalDeliveries: number }>("/api/v1/dashboard"),

  // AI endpoints
  menuSearch:      (q: string, k?: number) => apiFetch<unknown>(`/api/v1/ai/menu-search?q=${encodeURIComponent(q)}${k ? `&k=${k}` : ""}`),
  deliveryPredict: (routeOrder: number)    => apiFetch<unknown>(`/api/v1/ai/delivery-predict?route_order=${routeOrder}`),
  aiStatus:        ()                      => apiFetch<unknown>("/api/v1/ai/status"),
  reindex:         ()                      => apiFetch<unknown>("/api/v1/ai/reindex", { method: "POST" }),
};

// ── Context shape ────────────────────────────────────────────────────────────

type AppContextType = {
  // Cached data
  members:      Member[];
  deliveries:   Delivery[];
  schedule:     ScheduleDay[];
  pricingPlans: PricingPlan[];
  requests:     TrialRequest[];
  feedback:     Feedback[];
  pilots:       PilotProgram[];
  payments:     Payment[];
  dashboard:    { activeMembers: number; totalMembers: number; totalDeliveries: number } | null;

  // State
  loading:      boolean;
  error:        string | null;

  /** Call refetch() after any mutation to refresh all cached data */
  refetch:      () => Promise<void>;

  /** API token — persisted in localStorage */
  token:        string;
  setToken:     (t: string) => void;
};

const AppContext = createContext<AppContextType>({
  members: [], deliveries: [], schedule: [], pricingPlans: [],
  requests: [], feedback: [], pilots: [], payments: [], dashboard: null,
  loading: false, error: null, refetch: async () => {},
  token: "", setToken: () => {},
});

// ── Provider ─────────────────────────────────────────────────────────────────

export function AppProvider({ children }: { children: ReactNode }) {
  const [members,      setMembers]      = useState<Member[]>([]);
  const [deliveries,   setDeliveries]   = useState<Delivery[]>([]);
  const [schedule,     setSchedule]     = useState<ScheduleDay[]>([]);
  const [pricingPlans, setPricingPlans] = useState<PricingPlan[]>([]);
  const [requests,     setRequests]     = useState<TrialRequest[]>([]);
  const [feedback,     setFeedback]     = useState<Feedback[]>([]);
  const [pilots,       setPilots]       = useState<PilotProgram[]>([]);
  const [payments,     setPayments]     = useState<Payment[]>([]);
  const [dashboard,    setDashboard]    = useState<AppContextType["dashboard"]>(null);
  const [loading,      setLoading]      = useState(false);
  const [error,        setError]        = useState<string | null>(null);
  const [token,        setTokenState]   = useState<string>("");

  // Persist token
  useEffect(() => {
    const saved = localStorage.getItem("app_token");
    if (saved) setTokenState(saved);
  }, []);

  const setToken = (t: string) => {
    setTokenState(t);
    if (t) localStorage.setItem("app_token", t);
    else localStorage.removeItem("app_token");
  };

  const refetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [m, d, s, p, r, f, pi, pay] = await Promise.all([
        api.getMembers(),
        api.getDeliveries(),
        api.getSchedule(),
        api.getPricingPlans(),
        api.getRequests(),
        api.getFeedback(),
        api.getPilots(),
        api.getPayments(),
      ]);
      setMembers(m);
      setDeliveries(d);
      setSchedule(s);
      setPricingPlans(p);
      setRequests(r);
      setFeedback(f);
      setPilots(pi);
      setPayments(pay);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Unknown error";
      setError(`Backend unavailable: ${msg}. Make sure the Python server is running.`);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return (
    <AppContext.Provider value={{
      members, deliveries, schedule, pricingPlans,
      requests, feedback, pilots, payments, dashboard,
      loading, error, refetch,
      token, setToken,
    }}>
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext() {
  return useContext(AppContext);
}
