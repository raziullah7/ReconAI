import { createFileRoute } from '@tanstack/react-router'

import { listReconciliationCases } from '../../api/reconciliation-cases'
import { CaseListErrorState, CaseListLoadingState } from './-components/case-list-state'
import { CaseListRoute } from './-components/case-list-route'

export const Route = createFileRoute('/reconciliation-cases/')({
  loader: listReconciliationCases,
  pendingComponent: CaseListLoadingState,
  errorComponent: CaseListErrorState,
  component: CaseListRoute,
})
