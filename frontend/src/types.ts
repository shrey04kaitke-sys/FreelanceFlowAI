export type Workflow = "analysis" | "proposal" | "scope" | "milestones" | "invoice";

export interface BriefRequest {
  text: string;
  client_name?: string;
  currency: string;
}

export interface GenerationResponse {
  workflow: Workflow;
  model: string;
  output: Record<string, unknown>;
}

export interface HistoryRecord {
  id: number;
  client: string;
  workflow: string;
  created_at: string;
  output: Record<string, unknown>;
}

export interface HealthResponse {
  status: "ok";
  ollama_reachable: boolean;
  model: string;
  configured_model?: string;
  fallback_model?: string;
  history_enabled: boolean;
}

export interface PricingResult {
  items: Array<Record<string, string | number>>;
  subtotal: number;
  contingency: number;
  total: number;
}
