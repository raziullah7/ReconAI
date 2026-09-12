import { Outlet, createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/reconciliation-cases')({
  component: () => (
    <section
      className="mx-auto w-full max-w-[1180px] px-5 py-7"
      aria-labelledby="workspace-title"
    >
      <Outlet />
    </section>
  ),
})
