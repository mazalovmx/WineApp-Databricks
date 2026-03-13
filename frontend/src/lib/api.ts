const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

export async function login(userId: string, password: string) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, password }),
  });
  if (!res.ok) throw new Error("Login failed");
  const data = await res.json();
  if (data.access_token) localStorage.setItem("token", data.access_token);
  return data;
}

export async function api<T>(
  path: string,
  opts: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(opts.headers || {}),
  };
  if (token) (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...opts, headers });
  if (res.status === 401) {
    localStorage.removeItem("token");
    throw new Error("Unauthorized");
  }
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export const health = () => api<{ status: string; last_successful_run: string | null }>("/health");
export const me = () => api<{ user_id: string; locale: string }>("/users/me");

export type Recommendation = {
  kind: string;
  rank: number;
  wine_id: number;
  offer_id: number | null;
  score: number | null;
  explanation: string;
  wine_name: string;
  price_mxn: number | null;
  product_url: string | null;
  store_name: string | null;
};

export const getRecommendations = (kind?: string) =>
  api<Recommendation[]>(kind ? `/recommendations?kind=${kind}` : "/recommendations");

export const getTriedWines = (query?: string, wineType?: string) => {
  const p = new URLSearchParams();
  if (query) p.set("query", query);
  if (wineType) p.set("wine_type", wineType);
  return api<Array<{
    wine_id: number;
    wine_name: string;
    type: string | null;
    grapes: string[] | null;
    rating: number;
    comment: string | null;
    tried_at: string | null;
    rated_at: string | null;
  }>>(`/wines/tried?${p}`);
};

export const submitRating = (wineId: number, rating: number, comment?: string, triedAt?: string) =>
  api<{ ok: boolean; wine_id: number }>("/ratings", {
    method: "POST",
    body: JSON.stringify({
      wine_id: wineId,
      rating_1_5: rating,
      comment: comment || null,
      tried_at: triedAt || new Date().toISOString(),
    }),
  });

export const triggerRun = () => api<{ ok: boolean }>("/runs/trigger", { method: "POST" });
