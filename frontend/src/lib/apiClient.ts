// Centralised fetch for the Architecture Archaeologist backend.
// Backend defaults to http://localhost:8007; override with PUBLIC_API_BASE.

export const BASE: string =
  (import.meta.env.PUBLIC_API_BASE as string | undefined) ??
  'http://localhost:8007';

async function request(path: string, init: RequestInit = {}): Promise<Response> {
  try {
    return await fetch(`${BASE}${path}`, init);
  } catch {
    throw new Error(
      `Backend not reachable at ${BASE}. Start the local backend (see the repo README) or set PUBLIC_API_BASE.`,
    );
  }
}

async function handle(res: Response): Promise<any> {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const data = await res.json();
      detail = (data as { detail?: string }).detail ?? JSON.stringify(data);
    } catch {
      // keep statusText
    }
    throw new Error(`API ${res.status}: ${detail}`);
  }
  return res.json();
}

export async function apiGet(path: string): Promise<any> {
  const res = await request(`${BASE}${path}`);
  return handle(res);
}

export async function apiPost(path: string, body: unknown): Promise<any> {
  const res = await request(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return handle(res);
}

export async function apiPostFile(path: string, file: File): Promise<any> {
  const form = new FormData();
  form.append('file', file);
  const res = await request(`${BASE}${path}`, {
    method: 'POST',
    body: form,
  });
  return handle(res);
}

export async function apiDelete(path: string): Promise<any> {
  const res = await request(`${BASE}${path}`, {
    method: 'DELETE',
  });
  return handle(res);
}
