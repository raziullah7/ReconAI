import "@testing-library/jest-dom/vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { App } from "./App";
import { fetchHealth } from "./api/health";

vi.mock("./api/health", () => ({
  fetchHealth: vi.fn(),
}));

const mockedFetchHealth = vi.mocked(fetchHealth);

describe("App", () => {
  beforeEach(() => {
    mockedFetchHealth.mockReset();
  });

  it("test_frontend_app_renders_shell", async () => {
    /**
     * Verifies that the Vite app renders the initial operator shell.
     *
     * Mocks:
     * fetchHealth: Replaces the backend health client so the component test
     *   does not depend on a running backend.
     *
     * Assertions:
     * - The shell exposes Login and Dashboard skeleton regions.
     * - The health status surface is present.
     * - No customer, payment, call, or reconciliation workflows render in
     *   Phase 1.
     */
    mockedFetchHealth.mockResolvedValue({
      status: "ok",
      service: "reconai-backend",
      version: "0.1.0",
    });

    render(<App />);

    expect(screen.getByRole("region", { name: "Login" })).toBeInTheDocument();
    expect(screen.getByRole("region", { name: "Dashboard" })).toBeInTheDocument();
    expect(screen.getByRole("status")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("Backend ok")).toBeInTheDocument();
    });
    expect(screen.queryByText(/customer/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/payment/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/call/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/reconciliation/i)).not.toBeInTheDocument();
  });
});
