import type { BriefRequest, GenerationResponse, HealthResponse, HistoryRecord, PricingResult, Workflow } from "./types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  try {
    const response = await fetch(`${API_URL}${path}`, {
      headers: { "Content-Type": "application/json", ...(options?.headers ?? {}) },
      ...options,
    });
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(body.detail ?? `Request failed (${response.status})`);
    }
    return (response.status === 204 ? undefined : await response.json()) as T;
  } catch (error) {
    if (error instanceof TypeError) throw new Error("Backend is unavailable. Start the FastAPI server and try again.");
    throw error;
  }
}

export const api = {
  health: () => request<HealthResponse>("/api/health"),
  demoBrief: () => request<{ brief: string }>("/api/demo-brief"),
  generate: (workflow: Workflow, brief: BriefRequest) =>
    request<GenerationResponse>(`/api/${workflow === "analysis" ? "analyze" : workflow}`, { method: "POST", body: JSON.stringify(brief) }),
  pricing: (payload: { items: Array<{ description: string; hours: number; cost: number }>; hourly_rate: number; contingency_percent: number }) =>
    request<PricingResult>("/api/pricing", { method: "POST", body: JSON.stringify(payload) }),
  history: () => request<HistoryRecord[]>("/api/history"),
  saveHistory: (payload: { client: string; brief: string; workflow: string; output: Record<string, unknown> }) =>
    request<{ status: string }>("/api/history", { method: "POST", body: JSON.stringify(payload) }),
  deleteHistory: (id: number) => request<void>(`/api/history/${id}`, { method: "DELETE" }),
};
