import { Alert, Button, Card, Spinner } from '@heroui/react'
import { Link, useRouter } from '@tanstack/react-router'
import type { ErrorComponentProps } from '@tanstack/react-router'

import { ApiError } from '../../../api/reconciliation-cases'

export function CaseDetailLoadingState() {
  return (
    <Card className="min-h-[460px] overflow-hidden border border-slate-200 bg-white shadow-none dark:border-zinc-800 dark:bg-zinc-900">
      <CaseDetailCardHeader />
      <div
        className="grid min-h-[360px] place-items-center gap-3 p-8 text-center text-slate-500 dark:text-zinc-400"
        role="status"
        aria-live="polite"
      >
        <Spinner aria-label="Loading case detail" />
        <p className="m-0 text-sm font-medium">Loading case detail.</p>
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
    <Card className="min-h-[460px] overflow-hidden border border-slate-200 bg-white shadow-none dark:border-zinc-800 dark:bg-zinc-900">
      <CaseDetailCardHeader />
      <Card.Content className="p-6">
        <Alert status="danger" role="alert">
          <Alert.Content>
            <Alert.Title>Unable to load case detail</Alert.Title>
            <Alert.Description>{details.message}</Alert.Description>
            {details.meta ? (
              <p className="m-0 mt-3 text-xs text-slate-500 dark:text-zinc-400">
                {details.meta}
              </p>
            ) : null}
            <div className="mt-4 flex flex-wrap gap-3">
              <Button className="w-fit" variant="secondary" onPress={retryLoad}>
                Retry
              </Button>
              <Link
                to="/reconciliation-cases"
                className="inline-flex min-h-10 items-center rounded-md border border-slate-300 px-4 text-sm font-semibold text-slate-700 dark:border-zinc-700 dark:text-zinc-200"
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
    <Card.Header className="border-b border-slate-200 px-6 py-5 dark:border-zinc-800">
      <p className="m-0 text-xs font-bold uppercase text-slate-500 dark:text-zinc-400">
        Base API
      </p>
      <Card.Title id="workspace-title" className="m-0 mt-1 text-2xl leading-tight">
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
