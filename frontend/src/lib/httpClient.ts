export type JSONValue = any;

const API_BASE =
  (import.meta as any)?.env?.VITE_API_BASE_URL ??
  (window as any)?.__API_BASE__ ??
  '';

function joinURL(base: string, path: string) {
  if (!base) return path;
  return [base.replace(/\/+$/, ''), path.replace(/^\/+/, '')].join('/');
}

function fetchWithTimeout(url: string, options: RequestInit = {}, ms = 15000) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), ms);
  const merged: RequestInit = { ...options, signal: controller.signal };
  return fetch(url, merged).finally(() => clearTimeout(id));
}

async function parseJSONSafe(res: Response) {
  const text = await res.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export async function request(
  path: string,
  options: RequestInit & { timeoutMs?: number } = {}
): Promise<{ ok: boolean; status?: number; data?: JSONValue; networkError?: boolean; error?: string }> {
  const { timeoutMs, ...rest } = options;
  const url = API_BASE ? joinURL(API_BASE, path) : path;

  try {
    const res = await fetchWithTimeout(url, rest, timeoutMs ?? 15000);
    const data = await parseJSONSafe(res);
    return { ok: res.ok, status: res.status, data };
  } catch (err: any) {
    return { ok: false, networkError: true, error: err?.message || String(err) };
  }
}