export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

/**
 * Fetch backend health metadata.
 *
 * What: Calls the Phase 1 backend health endpoint and parses the JSON
 * response.
 * Why: The frontend shell needs a small integration check before
 * authenticated tenant workflows exist.
 *
 * @param baseUrl - Backend origin without a trailing slash.
 * @param signal - Optional abort signal. Defaults to undefined.
 * @returns Parsed backend health metadata.
 * @throws {Error} When the backend returns a non-OK response.
 */
export async function fetchHealth(
  baseUrl: string,
  signal?: AbortSignal,
): Promise<HealthResponse> {
  const normalizedBaseUrl = baseUrl.endsWith("/") ? baseUrl.slice(0, -1) : baseUrl;
  const response = await fetch(`${normalizedBaseUrl}/health`, {
    headers: {},
    signal,
  });

  if (!response.ok) {
    throw new Error(`Backend health check failed with status ${response.status}`);
  }

  const body = (await response.json()) as HealthResponse;
  return {
    status: body.status,
    service: body.service,
    version: body.version,
  };
}
