import { useCallback, useEffect, useState } from 'react'

import './App.css'
import { listReconciliationCases } from './api/reconciliationCases'
import type { ReconciliationCaseListItemV1 } from './api/reconciliationCases'

type CaseListState =
  | { status: 'loading' }
  | { status: 'empty' }
  | { status: 'success'; items: ReconciliationCaseListItemV1[] }
  | { status: 'error'; message: string }

function App() {
  const [caseListState, setCaseListState] = useState<CaseListState>({
    status: 'loading',
  })

  const loadCases = useCallback(async () => {
    setCaseListState({ status: 'loading' })
    setCaseListState(await getNextCaseListState())
  }, [])

  useEffect(() => {
    let isCurrent = true

    async function loadInitialCases() {
      const nextState = await getNextCaseListState()

      if (isCurrent) {
        setCaseListState(nextState)
      }
    }

    void loadInitialCases()

    return () => {
      isCurrent = false
    }
  }, [])

  const shellFacts = buildShellFacts(caseListState)

  return (
    <main className="app-shell">
      <header className="app-header" aria-label="ReconAI workspace">
        <div className="brand-lockup">
          <span className="brand-mark" aria-hidden="true">
            R
          </span>
          <div>
            <p className="brand-name">ReconAI</p>
            <h1>Payment reconciliation</h1>
          </div>
        </div>
      </header>

      <section className="workspace-panel" aria-labelledby="workspace-title">
        <div className="workspace-main">
          <div className="workspace-heading">
            <p className="section-label">Base API</p>
            <h2 id="workspace-title">Reconciliation cases</h2>
          </div>
          <CaseList state={caseListState} onRetry={loadCases} />
        </div>

        <dl className="shell-facts" aria-label="Case list status">
          {shellFacts.map((fact) => (
            <div className="fact-item" key={fact.label}>
              <dt>{fact.label}</dt>
              <dd>{fact.value}</dd>
            </div>
          ))}
        </dl>
      </section>
    </main>
  )
}

async function getNextCaseListState(): Promise<CaseListState> {
  try {
    const response = await listReconciliationCases()

    return response.items.length === 0
      ? { status: 'empty' }
      : { status: 'success', items: response.items }
  } catch (error) {
    return {
      status: 'error',
      message: error instanceof Error ? error.message : 'Unable to load cases.',
    }
  }
}

function CaseList({
  state,
  onRetry,
}: {
  state: CaseListState
  onRetry: () => Promise<void>
}) {
  if (state.status === 'loading') {
    return (
      <div className="state-panel" role="status" aria-live="polite">
        <p>Loading stored cases.</p>
      </div>
    )
  }

  if (state.status === 'empty') {
    return (
      <div className="state-panel" role="status" aria-live="polite">
        <p>No reconciliation cases found.</p>
      </div>
    )
  }

  if (state.status === 'error') {
    return (
      <div className="state-panel state-panel-error" role="alert">
        <p>{state.message}</p>
        <button type="button" onClick={() => void onRetry()}>
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="case-list" aria-label="Stored reconciliation cases">
      {state.items.map((caseItem) => (
        <article className="case-row" key={caseItem.id}>
          <div className="case-row-header">
            <div>
              <p className="case-reference">
                {formatReference(caseItem.external_reference)}
              </p>
              <p className="case-customer">
                Customer {formatReference(caseItem.customer_reference)}
              </p>
            </div>
            <span className={`status-chip ${getStatusClassName(caseItem.status)}`}>
              {caseItem.status}
            </span>
          </div>

          <dl className="case-metrics">
            <Metric
              label="Agreed"
              value={formatMoney(caseItem.agreed_amount_minor, caseItem.currency)}
            />
            <Metric
              label="Paid"
              value={formatMoney(caseItem.paid_amount_minor, caseItem.currency)}
            />
            <Metric
              label="Difference"
              value={formatMoney(caseItem.difference_minor, caseItem.currency)}
            />
            <Metric
              label="Review"
              value={caseItem.needs_human_review ? 'Required' : 'Not required'}
            />
          </dl>

          <dl className="case-timestamps">
            <Metric label="Created" value={formatDateTime(caseItem.created_at)} />
            <Metric label="Updated" value={formatDateTime(caseItem.updated_at)} />
          </dl>
        </article>
      ))}
    </div>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt>{label}</dt>
      <dd>{value}</dd>
    </div>
  )
}

function buildShellFacts(state: CaseListState): ReadonlyArray<{ label: string; value: string }> {
  if (state.status === 'success') {
    return [
      { label: 'Connection', value: 'Base API' },
      { label: 'Cases', value: String(state.items.length) },
      { label: 'Status', value: 'Loaded' },
    ]
  }

  return [
    { label: 'Connection', value: 'Base API' },
    { label: 'Cases', value: state.status === 'empty' ? '0' : 'Pending' },
    { label: 'Status', value: state.status === 'error' ? 'Error' : 'Loading' },
  ]
}

function formatReference(value: string | null | undefined): string {
  return value?.trim() ? value : 'Not provided'
}

function formatMoney(amountMinor: number | null, currency: string | null): string {
  if (amountMinor === null) {
    return 'Not provided'
  }

  const amountMajor = amountMinor / 100
  const formattedAmount = new Intl.NumberFormat(undefined, {
    maximumFractionDigits: 2,
    minimumFractionDigits: 2,
  }).format(amountMajor)

  return currency ? `${currency} ${formattedAmount}` : `${formattedAmount} currency missing`
}

function formatDateTime(value: string): string {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}

function getStatusClassName(status: string): string {
  return `status-${status.toLowerCase().replaceAll('_', '-')}`
}

export default App
