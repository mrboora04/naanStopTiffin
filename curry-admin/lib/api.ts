/**
 * lib/api.ts
 * Central fetch client. All data access in the frontend goes through these
 * functions. Swap the base URL or add auth headers here in one place when
 * connecting a real backend.
 */

import type {
  Member,
  Delivery,
  Dish,
  ScheduleDay,
  PricingPlan,
  TrialRequest,
  Feedback,
  PilotProgram,
  Payment,
} from "@/types";

const BASE = "";          // same-origin Next.js API routes
const JSON_HEADERS = { "Content-Type": "application/json" };

async function request<T>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${BASE}${url}`, options);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

// ─── Members ────────────────────────────────────────────────────────────────
export const getMembers      = ()                        => request<Member[]>("/api/members");
export const getMember       = (id: string)              => request<Member>(`/api/members/${id}`);
export const createMember    = (data: Omit<Member, "id">) =>
  request<Member>("/api/members", { method: "POST", headers: JSON_HEADERS, body: JSON.stringify(data) });
export const updateMember    = (id: string, data: Partial<Member>) =>
  request<Member>(`/api/members/${id}`, { method: "PATCH", headers: JSON_HEADERS, body: JSON.stringify(data) });
export const deleteMember    = (id: string) =>
  request<void>(`/api/members/${id}`, { method: "DELETE" });

// ─── Deliveries ──────────────────────────────────────────────────────────────
export const getDeliveries   = ()                           => request<Delivery[]>("/api/deliveries");
export const getDelivery     = (id: string)                 => request<Delivery>(`/api/deliveries/${id}`);
export const createDelivery  = (data: Omit<Delivery, "id">) =>
  request<Delivery>("/api/deliveries", { method: "POST", headers: JSON_HEADERS, body: JSON.stringify(data) });
export const updateDelivery  = (id: string, data: Partial<Delivery>) =>
  request<Delivery>(`/api/deliveries/${id}`, { method: "PATCH", headers: JSON_HEADERS, body: JSON.stringify(data) });
export const deleteDelivery  = (id: string) =>
  request<void>(`/api/deliveries/${id}`, { method: "DELETE" });

// ─── Schedule ────────────────────────────────────────────────────────────────
export const getSchedule     = ()                              => request<ScheduleDay[]>("/api/schedule");
export const getScheduleDay  = (id: string)                   => request<ScheduleDay>(`/api/schedule/${id}`);
export const updateScheduleDay = (id: string, data: Partial<ScheduleDay>) =>
  request<ScheduleDay>(`/api/schedule/${id}`, { method: "PATCH", headers: JSON_HEADERS, body: JSON.stringify(data) });

// ─── Pricing ─────────────────────────────────────────────────────────────────
export const getPricingPlans  = ()                                => request<PricingPlan[]>("/api/pricing");
export const getPricingPlan   = (id: string)                     => request<PricingPlan>(`/api/pricing/${id}`);
export const createPricingPlan = (data: Omit<PricingPlan, "id">) =>
  request<PricingPlan>("/api/pricing", { method: "POST", headers: JSON_HEADERS, body: JSON.stringify(data) });
export const updatePricingPlan = (id: string, data: Partial<PricingPlan>) =>
  request<PricingPlan>(`/api/pricing/${id}`, { method: "PATCH", headers: JSON_HEADERS, body: JSON.stringify(data) });
export const deletePricingPlan = (id: string) =>
  request<void>(`/api/pricing/${id}`, { method: "DELETE" });

// ─── Trial Requests ──────────────────────────────────────────────────────────
export const getTrialRequests  = ()                                  => request<TrialRequest[]>("/api/requests");
export const getTrialRequest   = (id: string)                       => request<TrialRequest>(`/api/requests/${id}`);
export const createTrialRequest = (data: Omit<TrialRequest, "id">) =>
  request<TrialRequest>("/api/requests", { method: "POST", headers: JSON_HEADERS, body: JSON.stringify(data) });
export const updateTrialRequest = (id: string, data: Partial<TrialRequest>) =>
  request<TrialRequest>(`/api/requests/${id}`, { method: "PATCH", headers: JSON_HEADERS, body: JSON.stringify(data) });
export const deleteTrialRequest = (id: string) =>
  request<void>(`/api/requests/${id}`, { method: "DELETE" });

// ─── Comments / Feedback ─────────────────────────────────────────────────────
export const getFeedback      = ()                            => request<Feedback[]>("/api/comments");
export const getFeedbackItem  = (id: string)                 => request<Feedback>(`/api/comments/${id}`);
export const createFeedback   = (data: Omit<Feedback, "id">) =>
  request<Feedback>("/api/comments", { method: "POST", headers: JSON_HEADERS, body: JSON.stringify(data) });
export const updateFeedback   = (id: string, data: Partial<Feedback>) =>
  request<Feedback>(`/api/comments/${id}`, { method: "PATCH", headers: JSON_HEADERS, body: JSON.stringify(data) });
export const deleteFeedback   = (id: string) =>
  request<void>(`/api/comments/${id}`, { method: "DELETE" });

// ─── Pilot Programs ──────────────────────────────────────────────────────────
export const getPilotPrograms  = ()                                   => request<PilotProgram[]>("/api/pilot");
export const getPilotProgram   = (id: string)                        => request<PilotProgram>(`/api/pilot/${id}`);
export const createPilotProgram = (data: Omit<PilotProgram, "id">) =>
  request<PilotProgram>("/api/pilot", { method: "POST", headers: JSON_HEADERS, body: JSON.stringify(data) });
export const updatePilotProgram = (id: string, data: Partial<PilotProgram>) =>
  request<PilotProgram>(`/api/pilot/${id}`, { method: "PATCH", headers: JSON_HEADERS, body: JSON.stringify(data) });
export const deletePilotProgram = (id: string) =>
  request<void>(`/api/pilot/${id}`, { method: "DELETE" });

// ─── Payments ────────────────────────────────────────────────────────────────
export const getPayments  = ()                             => request<Payment[]>("/api/payments");
export const getPayment   = (id: string)                  => request<Payment>(`/api/payments/${id}`);
export const createPayment = (data: Omit<Payment, "id">) =>
  request<Payment>("/api/payments", { method: "POST", headers: JSON_HEADERS, body: JSON.stringify(data) });
export const updatePayment = (id: string, data: Partial<Payment>) =>
  request<Payment>(`/api/payments/${id}`, { method: "PATCH", headers: JSON_HEADERS, body: JSON.stringify(data) });

// ─── Dishes ──────────────────────────────────────────────────────────────────
export const getDishes  = ()                           => request<Dish[]>("/api/dishes");
export const getDish    = (id: string)                => request<Dish>(`/api/dishes/${id}`);
export const createDish = (data: Omit<Dish, "id">)   =>
  request<Dish>("/api/dishes", { method: "POST", headers: JSON_HEADERS, body: JSON.stringify(data) });
export const updateDish = (id: string, data: Partial<Dish>) =>
  request<Dish>(`/api/dishes/${id}`, { method: "PATCH", headers: JSON_HEADERS, body: JSON.stringify(data) });
export const deleteDish = (id: string) =>
  request<void>(`/api/dishes/${id}`, { method: "DELETE" });
