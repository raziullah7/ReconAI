import { createFileRoute } from '@tanstack/react-router'

import { CaseSubmitRoute } from './-components/case-submit-route'

export const Route = createFileRoute('/reconciliation-cases/new')({
  component: CaseSubmitRoute,
})
