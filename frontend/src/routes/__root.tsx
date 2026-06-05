import { Outlet, createRootRoute } from '@tanstack/react-router'

export const Route = createRootRoute({
  component: () => (
    <main className="recon-app min-h-svh">
      <header className="recon-header">
        <div className="recon-shell recon-header__inner flex items-center gap-4">
          <span
            className="recon-brand-mark grid size-11 place-items-center"
            aria-hidden="true"
          >
            R
          </span>
          <div>
            <p className="recon-brand-label">
              ReconAI
            </p>
            <h1 className="recon-brand-title">
              Payment reconciliation
            </h1>
          </div>
        </div>
      </header>
      <Outlet />
    </main>
  ),
})
