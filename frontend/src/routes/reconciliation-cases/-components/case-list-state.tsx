import type { ReactNode } from 'react'
import { Alert, Button, Card, Spinner } from '@heroui/react'
import { useRouter } from '@tanstack/react-router'
import type { ErrorComponentProps } from '@tanstack/react-router'

export function CaseListLoadingState() {
  return (
    <CaseListFrame sidebar={<CaseListFacts facts={loadingFacts} />}>
      <Card className="recon-surface recon-surface--stable overflow-hidden">
        <CaseListCardHeader />
        <div
          className="recon-state-panel grid place-items-center gap-3"
          role="status"
          aria-live="polite"
        >
          <Spinner aria-label="Loading stored cases" />
          <p className="recon-meta">Loading stored cases.</p>
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
      <Card className="recon-surface recon-surface--stable overflow-hidden">
        <CaseListCardHeader />
        <Card.Content className="recon-surface__content">
          <Alert status="danger" role="alert">
            <Alert.Content>
              <Alert.Title>Unable to load cases</Alert.Title>
              <Alert.Description>{message}</Alert.Description>
              <Button className="recon-button recon-button--secondary w-fit" variant="secondary" onPress={retryLoad}>
                Retry
              </Button>
            </Alert.Content>
          </Alert>
        </Card.Content>
      </Card>
    </CaseListFrame>
  )
}

export function CaseListCardHeader({ action }: { action?: ReactNode }) {
  return (
    <Card.Header className="recon-surface__header">
      <div className="flex w-full flex-wrap items-start justify-between gap-3">
        <div>
          <p className="recon-eyebrow">
            Base API
          </p>
          <Card.Title id="workspace-title" className="recon-title">
            Reconciliation cases
          </Card.Title>
        </div>
        {action}
      </div>
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
    <div className="recon-case-layout">
      {children}
      {sidebar}
    </div>
  )
}

export function CaseListFacts({ facts }: { facts: readonly ShellFact[] }) {
  return (
    <dl className="recon-facts overflow-hidden" aria-label="Case list status">
      {facts.map((fact) => (
        <div
          className="recon-fact flex flex-col gap-1"
          key={fact.label}
        >
          <dt>{fact.label}</dt>
          <dd>{fact.value}</dd>
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
