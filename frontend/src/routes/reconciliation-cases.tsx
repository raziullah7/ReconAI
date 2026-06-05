import { Outlet, createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/reconciliation-cases')({
  component: () => (
    <section
      className="recon-shell recon-workspace"
      aria-labelledby="workspace-title"
    >
      <Outlet />
    </section>
  ),
})
