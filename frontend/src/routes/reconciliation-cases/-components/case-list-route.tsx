import { useLoaderData } from '@tanstack/react-router'

import { CaseListTable } from './case-list-table'

export function CaseListRoute() {
  const response = useLoaderData({ from: '/reconciliation-cases/' })

  return <CaseListTable items={response.items} />
}
