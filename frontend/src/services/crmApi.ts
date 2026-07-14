import axios from "axios";
import type { ChatRequest, ChatResponse, SessionResponse } from "../types/crm";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL as string | undefined;
const BACKEND_URL_RAW = import.meta.env.VITE_BACKEND_URL as string | undefined;

if (!API_BASE_URL) {
  throw new Error("Missing env var: VITE_API_BASE_URL must be set in .env");
}
if (!BACKEND_URL_RAW) {
  throw new Error("Missing env var: VITE_BACKEND_URL must be set in .env");
}

export const BACKEND_URL = BACKEND_URL_RAW;

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60_000,
  headers: {
    "Content-Type": "application/json",
  },
});

export async function sendChatMessage(
  request: ChatRequest,
): Promise<ChatResponse> {
  const response = await api.post<ChatResponse>("/chat", request);
  return response.data;
}

export async function getSession(
  sessionId: string,
): Promise<SessionResponse> {
  const response = await api.get<SessionResponse>(`/sessions/${sessionId}`);
  return response.data;
}

export async function deleteSession(sessionId: string): Promise<void> {
  await api.delete(`/sessions/${sessionId}`);
}

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await axios.get<{ status: string }>(
      `${BACKEND_URL}/health`,
      { timeout: 4_000 },
    );
    return response.data.status === "healthy";
  } catch {
    return false;
  }
}
