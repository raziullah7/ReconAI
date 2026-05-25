import { describe, expect, it, vi } from "vitest";

import { fetchHealth } from "./health";

describe("fetchHealth", () => {
  it("test_frontend_health_client_handles_ok_response", async () => {
    /**
     * Verifies that the health client parses a successful backend response.
     *
     * Mocks:
     * fetch: Returns a synthetic 200 response from `/health` so the client
     *   contract is tested without network access.
     *
     * Assertions:
     * - The client calls the configured backend base URL.
     * - The returned health object includes `status`, `service`, and
     *   `version`.
     * - The client does not attach auth or tenant headers in Phase 1.
     */
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          status: "ok",
          service: "reconai-backend",
          version: "0.1.0",
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    const health = await fetchHealth("http://localhost:8000");

    expect(fetchMock).toHaveBeenCalledWith("http://localhost:8000/health", {
      headers: {},
      signal: undefined,
    });
    expect(health).toEqual({
      status: "ok",
      service: "reconai-backend",
      version: "0.1.0",
    });
  });
});
