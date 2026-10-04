import { Outlet, createRootRoute } from '@tanstack/react-router'

export const Route = createRootRoute({
  component: () => (
    <main className="min-h-svh bg-slate-50 text-slate-900 dark:bg-zinc-950 dark:text-zinc-100">
      <header className="border-b border-slate-200 bg-white dark:border-zinc-800 dark:bg-zinc-950">
        <div className="mx-auto flex min-h-20 w-full max-w-[1180px] items-center gap-4 px-5">
          <span
            className="grid size-11 place-items-center rounded-lg border border-blue-200 bg-blue-50 text-base font-bold text-blue-700 dark:border-blue-800 dark:bg-blue-950 dark:text-blue-200"
            aria-hidden="true"
          >
            R
          </span>
          <div>
            <p className="m-0 text-xs font-bold uppercase text-slate-500 dark:text-zinc-400">
              ReconAI
            </p>
            <h1 className="m-0 text-xl font-semibold leading-tight text-slate-950 dark:text-zinc-50">
              Payment reconciliation
            </h1>
          </div>
        </div>
      </header>
      <Outlet />
    </main>
  ),
})
