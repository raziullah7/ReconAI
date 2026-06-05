import { Alert, Button, Card, Spinner } from '@heroui/react'
import { Link, useRouter } from '@tanstack/react-router'
import type { ErrorComponentProps } from '@tanstack/react-router'

import { ApiError } from '../../../api/reconciliation-cases'

export function CaseDetailLoadingState() {
  return (
    <Card className="recon-surface recon-surface--stable overflow-hidden">
      <CaseDetailCardHeader />
      <div
        className="recon-state-panel recon-state-panel--compact grid place-items-center gap-3"
        role="status"
        aria-live="polite"
      >
        <Spinner aria-label="Loading case detail" />
        <p className="recon-meta">Loading case detail.</p>
      </div>
    </Card>
  )
}

export function CaseDetailErrorState({ error, reset }: ErrorComponentProps) {
  const router = useRouter()
  const details = getErrorDetails(error)

  function retryLoad(): void {
    reset()
    void router.invalidate()
  }

  return (
    <Card className="recon-surface recon-surface--stable overflow-hidden">
      <CaseDetailCardHeader />
      <Card.Content className="recon-surface__content">
        <Alert status="danger" role="alert">
          <Alert.Content>
            <Alert.Title>Unable to load case detail</Alert.Title>
            <Alert.Description>{details.message}</Alert.Description>
            {details.meta ? (
              <p className="recon-meta">
                {details.meta}
              </p>
            ) : null}
            <div className="flex flex-wrap gap-3">
              <Button className="recon-button recon-button--secondary w-fit" variant="secondary" onPress={retryLoad}>
                Retry
              </Button>
              <Link
                to="/reconciliation-cases"
                className="recon-button recon-button--secondary inline-flex min-h-10 items-center"
              >
                Back to list
              </Link>
            </div>
          </Alert.Content>
        </Alert>
      </Card.Content>
    </Card>
  )
}

export function CaseDetailCardHeader() {
  return (
    <Card.Header className="recon-surface__header">
      <p className="recon-eyebrow">
        Base API
      </p>
      <Card.Title id="workspace-title" className="recon-title">
        Case detail
      </Card.Title>
    </Card.Header>
  )
}

function getErrorDetails(error: Error): { message: string; meta: string | null } {
  if (error instanceof ApiError) {
    const meta = [error.code, error.requestId ? `request ${error.requestId}` : null]
      .filter((value) => value !== null)
      .join(' · ')

    return { message: error.message, meta: meta || null }
  }

  return { message: error.message || 'Unable to load case detail.', meta: null }
}
