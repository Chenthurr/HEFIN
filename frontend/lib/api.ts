const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiFetch<T>(path: string, options: RequestInit & { token?: string } = {}): Promise<T> {
  const { token, ...rest } = options;
  const headers = new Headers(rest.headers);
  if (!headers.has("Content-Type") && !(rest.body instanceof FormData)) headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const res = await fetch(`${API_BASE_URL}${path}`, { ...rest, headers });
  if (!res.ok) { const body = await res.text(); throw new Error(`API error ${res.status}: ${body}`); }
  return res.json() as Promise<T>;
}
