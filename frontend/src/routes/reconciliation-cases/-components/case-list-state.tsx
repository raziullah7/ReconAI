import type { ReactNode } from 'react'
import { Alert, Button, Card, Spinner } from '@heroui/react'
import { useRouter } from '@tanstack/react-router'
import type { ErrorComponentProps } from '@tanstack/react-router'

export function CaseListLoadingState() {
  return (
    <CaseListFrame sidebar={<CaseListFacts facts={loadingFacts} />}>
      <Card className="min-h-[460px] overflow-hidden border border-slate-200 bg-white shadow-none dark:border-zinc-800 dark:bg-zinc-900">
        <CaseListCardHeader />
        <div
          className="grid min-h-[460px] place-items-center gap-3 p-8 text-center text-slate-500 dark:text-zinc-400"
          role="status"
          aria-live="polite"
        >
          <Spinner aria-label="Loading stored cases" />
          <p className="m-0 text-sm font-medium">Loading stored cases.</p>
        </div>
      </Card>
    </CaseListFrame>
  )
}

export function CaseListEmptyState() {
  return (
    <Alert status="default" role="status" aria-live="polite">
      <Alert.Content>
        <Alert.Title>No reconciliation cases found</Alert.Title>
        <Alert.Description>
          Stored cases from the Base API will appear here after the backend has data.
        </Alert.Description>
      </Alert.Content>
    </Alert>
  )
}

export function CaseListErrorState({ error, reset }: ErrorComponentProps) {
  const router = useRouter()
  const message = error instanceof Error ? error.message : 'Unable to load cases.'

  function retryLoad(): void {
    reset()
    void router.invalidate()
  }

  return (
    <CaseListFrame sidebar={<CaseListFacts facts={errorFacts} />}>
      <Card className="min-h-[460px] overflow-hidden border border-slate-200 bg-white shadow-none dark:border-zinc-800 dark:bg-zinc-900">
        <CaseListCardHeader />
        <Card.Content className="p-6">
          <Alert status="danger" role="alert">
            <Alert.Content>
              <Alert.Title>Unable to load cases</Alert.Title>
              <Alert.Description>{message}</Alert.Description>
              <Button className="mt-4 w-fit" variant="secondary" onPress={retryLoad}>
                Retry
              </Button>
            </Alert.Content>
          </Alert>
        </Card.Content>
      </Card>
    </CaseListFrame>
  )
}

export function CaseListCardHeader() {
  return (
    <Card.Header className="border-b border-slate-200 px-6 py-5 dark:border-zinc-800">
      <p className="m-0 text-xs font-bold uppercase text-slate-500 dark:text-zinc-400">
        Base API
      </p>
      <Card.Title id="workspace-title" className="m-0 mt-1 text-2xl leading-tight">
        Reconciliation cases
      </Card.Title>
    </Card.Header>
  )
}

export interface ShellFact {
  label: string
  value: string
}

interface CaseListFrameProps {
  children: ReactNode
  sidebar: ReactNode
}

export function CaseListFrame({ children, sidebar }: CaseListFrameProps) {
  return (
    <div className="grid w-full grid-cols-[minmax(0,1fr)_minmax(260px,340px)] items-start gap-5 max-lg:grid-cols-1">
      {children}
      {sidebar}
    </div>
  )
}

export function CaseListFacts({ facts }: { facts: readonly ShellFact[] }) {
  return (
    <dl
      className="m-0 overflow-hidden rounded-lg border border-slate-200 bg-white dark:border-zinc-800 dark:bg-zinc-900"
      aria-label="Case list status"
    >
      {facts.map((fact) => (
        <div
          className="flex min-h-20 flex-col justify-center gap-2 border-b border-slate-200 px-5 py-4 last:border-b-0 dark:border-zinc-800"
          key={fact.label}
        >
          <dt className="text-xs font-semibold text-slate-500 dark:text-zinc-400">
            {fact.label}
          </dt>
          <dd className="m-0 text-sm font-semibold text-slate-950 dark:text-zinc-50">
            {fact.value}
          </dd>
        </div>
      ))}
    </dl>
  )
}

const loadingFacts: readonly ShellFact[] = [
  { label: 'Connection', value: 'Base API' },
  { label: 'Cases', value: 'Pending' },
  { label: 'Status', value: 'Loading' },
]

const errorFacts: readonly ShellFact[] = [
  { label: 'Connection', value: 'Base API' },
  { label: 'Cases', value: 'Pending' },
  { label: 'Status', value: 'Error' },
]
