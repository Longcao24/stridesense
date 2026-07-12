export async function uploadMotion(endpoint: string, payload: unknown): Promise<string> {
  const trimmed = endpoint.trim();
  if (!trimmed) throw new Error("Set the Cloudflare upload URL first");

  const response = await fetch(trimmed, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const text = await response.text();
  if (!response.ok) {
    throw new Error(text || `Upload failed with HTTP ${response.status}`);
  }
  return text;
}
