const SESSION_STORAGE_KEY = "hcp-crm-session-id";

export function createSessionId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }

  return `hcp-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function getOrCreateSessionId(): string {
  const existing = localStorage.getItem(SESSION_STORAGE_KEY);
  if (existing) {
    return existing;
  }

  const created = createSessionId();
  localStorage.setItem(SESSION_STORAGE_KEY, created);
  return created;
}

export function saveSessionId(sessionId: string): void {
  localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
}
