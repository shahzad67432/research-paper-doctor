const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  return res.json();
}

export interface JobStatus {
  id: string;
  mode: "analyze" | "qa" | "discover";
  status: "pending" | "running" | "done" | "error";
  created_at: number;
  completed_at: number | null;
  result: Record<string, unknown> | null;
  error: string | null;
  steps: Array<{ label: string; ok: boolean }>;
}

export interface CacheStats {
  papers_cached: number;
}

export async function uploadPaper(file: File): Promise<{ job_id: string }> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/api/analyze`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
  return res.json();
}

export async function sendQuery(query: string): Promise<{ job_id: string }> {
  return request("/api/qa", {
    method: "POST",
    body: JSON.stringify({ query }),
  });
}

export async function sendInterest(interest: string): Promise<{ job_id: string }> {
  return request("/api/discover", {
    method: "POST",
    body: JSON.stringify({ interest }),
  });
}

export async function getJobStatus(jobId: string): Promise<JobStatus> {
  return request(`/api/jobs/${jobId}`);
}

export async function getCacheStats(): Promise<CacheStats> {
  return request("/api/cache/stats");
}
