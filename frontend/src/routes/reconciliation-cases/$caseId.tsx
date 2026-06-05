import { createFileRoute } from '@tanstack/react-router'

import { getReconciliationCase } from '../../api/reconciliation-cases'
import { CaseDetailRoute } from './-components/case-detail-route'
import { CaseDetailErrorState, CaseDetailLoadingState } from './-components/case-detail-state'

export const Route = createFileRoute('/reconciliation-cases/$caseId')({
  loader: ({ params }) => getReconciliationCase(params.caseId),
  pendingComponent: CaseDetailLoadingState,
  errorComponent: CaseDetailErrorState,
  component: CaseDetailRoute,
})
