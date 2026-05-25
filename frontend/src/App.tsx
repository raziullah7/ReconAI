import { useEffect, useState } from "react";
import type { JSX } from "react";

import { fetchHealth, type HealthResponse } from "./api/health";

type HealthState =
  | { status: "loading" }
  | { status: "ready"; health: HealthResponse }
  | { status: "error"; message: string };

/**
 * Render the Phase 1 operator shell.
 *
 * What: Shows Login and Dashboard skeleton regions plus backend health
 * status.
 * Why: Later UI phases need a stable app root while domain surfaces remain
 * out of scope.
 *
 * @returns The React app shell for Phase 1.
 */
export function App(): JSX.Element {
  const [healthState, setHealthState] = useState<HealthState>({
    status: "loading",
  });

  useEffect(() => {
    const controller = new AbortController();

    fetchHealth("", controller.signal)
      .then((health) => {
        setHealthState({ status: "ready", health });
      })
      .catch((error: Error) => {
        if (!controller.signal.aborted) {
          setHealthState({ status: "error", message: error.message });
        }
      });

    return () => {
      controller.abort();
    };
  }, []);

  const statusText =
    healthState.status === "ready"
      ? `Backend ${healthState.health.status}`
      : healthState.status === "error"
        ? "Backend unavailable"
        : "Backend checking";

  return (
    <main aria-label="ReconAI">
      <h1>ReconAI</h1>
      <section aria-label="Login">
        <h2>Login</h2>
      </section>
      <section aria-label="Dashboard">
        <h2>Dashboard</h2>
      </section>
      <p role="status">{statusText}</p>
    </main>
  );
}
