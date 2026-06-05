import { useLoaderData } from '@tanstack/react-router'

import { CaseDetailView } from './case-detail-view'

export function CaseDetailRoute() {
  const caseDetail = useLoaderData({ from: '/reconciliation-cases/$caseId' })

  return <CaseDetailView caseDetail={caseDetail} />
}
