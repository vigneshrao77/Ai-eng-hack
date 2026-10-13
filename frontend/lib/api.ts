import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

export interface ProjectSummary {
  id: string;
  name: string;
  repo_url?: string;
  target_cloud: string;
  status: string;
  created_at: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  environment: string;
  standalone_mode: boolean;
  offline_demo_mode: boolean;
  database: string;
}

export async function fetchHealth(): Promise<HealthResponse> {
  const { data } = await api.get("/health");
  return data;
}

export async function fetchProjects(): Promise<ProjectSummary[]> {
  const { data } = await api.get("/projects");
  return data;
}

export async function fetchProject(id: string): Promise<ProjectSummary> {
  const { data } = await api.get(`/projects/${id}`);
  return data;
}

export async function createProject(payload: {
  name: string;
  repo_url?: string;
  target_cloud: string;
}): Promise<ProjectSummary> {
  const { data } = await api.post("/projects", payload);
  return data;
}

export async function uploadProjectZip(id: string, file: File): Promise<any> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post(`/projects/${id}/upload`, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return data;
}

export async function analyzeProject(
  id: string,
  options: { runtime_traces?: boolean } = {}
): Promise<{ job_id: string }> {
  const { data } = await api.post(`/projects/${id}/analyze`, options);
  return data;
}

export async function fetchJob(jobId: string) {
  const { data } = await api.get(`/jobs/${jobId}`);
  return data;
}

export async function fetchTwinGraph(projectId: string) {
  const { data } = await api.get(`/projects/${projectId}/twin/graph`);
  return data;
}

export async function askTwin(projectId: string, question: string) {
  const { data } = await api.post(`/projects/${projectId}/twin/ask`, { question });
  return data;
}

export async function fetchGxp(projectId: string) {
  const { data } = await api.get(`/projects/${projectId}/gxp`);
  return data;
}

export async function overrideGxp(
  projectId: string,
  nodeId: string,
  newTier: string,
  reason: string
) {
  const { data } = await api.patch(`/projects/${projectId}/gxp/${nodeId}`, {
    new_tier: newTier,
    reason,
  });
  return data;
}

export async function fetchReadiness(projectId: string) {
  const { data } = await api.get(`/projects/${projectId}/readiness`);
  return data;
}

export async function runDecomposition(
  projectId: string,
  weights?: number[],
  gamma?: number
) {
  const { data } = await api.post(`/projects/${projectId}/decompose`, { weights, gamma });
  return data;
}

export async function fetchDecomposition(projectId: string) {
  const { data } = await api.get(`/projects/${projectId}/decomposition`);
  return data;
}

export async function runCouncil(projectId: string, clusterIds?: string[]) {
  const { data } = await api.post(`/projects/${projectId}/council/run`, {
    cluster_ids: clusterIds,
  });
  return data;
}

export async function fetchCouncilDecisions(projectId: string) {
  const { data } = await api.get(`/projects/${projectId}/council/decisions`);
  return data;
}

export async function approveDecision(decisionId: string, comment: string = "") {
  const { data } = await api.post(`/decisions/${decisionId}/approve`, { comment });
  return data;
}

export async function rejectDecision(decisionId: string, comment: string = "") {
  const { data } = await api.post(`/decisions/${decisionId}/reject`, { comment });
  return data;
}

export async function fetchRoadmap(projectId: string) {
  const { data } = await api.get(`/projects/${projectId}/roadmap`);
  return data;
}

export async function recalculateRoadmapWhatIf(
  projectId: string,
  changes: Record<string, any>
) {
  const { data } = await api.post(`/projects/${projectId}/roadmap/whatif`, changes);
  return data;
}

export async function fetchAuditLogs() {
  const { data } = await api.get("/audit");
  return data;
}

export async function verifyAuditChain() {
  const { data } = await api.get("/audit/verify");
  return data;
}

export async function generateEvidencePack(projectId: string, wave: string | number) {
  const { data } = await api.post(`/projects/${projectId}/evidence/${wave}`);
  return data;
}

export async function fetchEvidencePacks(projectId: string) {
  const { data } = await api.get(`/projects/${projectId}/evidence`);
  return data;
}

export function getEvidenceDownloadUrl(projectId: string, wave: string | number) {
  return `${API_BASE_URL}/projects/${projectId}/evidence/${wave}/download`;
}
