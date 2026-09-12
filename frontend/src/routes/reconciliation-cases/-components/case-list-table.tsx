import { Card, Chip, Table } from '@heroui/react'
import { Link } from '@tanstack/react-router'

import type { ReconciliationCaseListItemV1 } from '../../../api/reconciliation-cases'
import {
  CaseListCardHeader,
  CaseListEmptyState,
  CaseListFacts,
  CaseListFrame,
} from './case-list-state'
import type { ShellFact } from './case-list-state'
import {
  formatDateTime,
  formatMoney,
  formatReference,
  formatStatusLabel,
  getStatusTone,
} from '../-utils/formatters'

interface CaseListTableProps {
  items: ReconciliationCaseListItemV1[]
}

export function CaseListTable({ items }: CaseListTableProps) {
  return (
    <CaseListFrame sidebar={<CaseListFacts facts={buildCaseListFacts(items)} />}>
      <Card className="min-h-[460px] overflow-hidden border border-slate-200 bg-white shadow-none dark:border-zinc-800 dark:bg-zinc-900">
        <CaseListCardHeader />
        <Card.Content className="p-0">
          {items.length === 0 ? <EmptyContent /> : <SuccessContent items={items} />}
        </Card.Content>
      </Card>
    </CaseListFrame>
  )
}

function EmptyContent() {
  return (
    <div className="p-6">
      <CaseListEmptyState />
    </div>
  )
}

function SuccessContent({ items }: { items: ReconciliationCaseListItemV1[] }) {
  return (
    <Table className="rounded-none border-0 shadow-none" variant="secondary">
      <Table.ScrollContainer>
        <Table.Content aria-label="Stored reconciliation cases">
          <Table.Header>
            <Table.Column isRowHeader>Case</Table.Column>
            <Table.Column>Status</Table.Column>
            <Table.Column>Agreed</Table.Column>
            <Table.Column>Paid</Table.Column>
            <Table.Column>Difference</Table.Column>
            <Table.Column>Review</Table.Column>
            <Table.Column>Updated</Table.Column>
          </Table.Header>
          <Table.Body items={items}>
            {(caseItem) => (
              <Table.Row id={caseItem.id}>
                <Table.Cell>
                  <div className="min-w-48">
                    <Link
                      to="/reconciliation-cases/$caseId"
                      params={{ caseId: caseItem.id }}
                      className="font-semibold text-blue-700 hover:text-blue-800 hover:underline dark:text-blue-300 dark:hover:text-blue-200"
                    >
                      {formatReference(caseItem.external_reference)}
                    </Link>
                    <p className="m-0 text-sm text-slate-500 dark:text-zinc-400">
                      Customer {formatReference(caseItem.customer_reference)}
                    </p>
                  </div>
                </Table.Cell>
                <Table.Cell>
                  <Chip color={getStatusTone(caseItem.status)} size="sm" variant="soft">
                    <Chip.Label>{formatStatusLabel(caseItem.status)}</Chip.Label>
                  </Chip>
                </Table.Cell>
                <Table.Cell>
                  {formatMoney(caseItem.agreed_amount_minor, caseItem.currency)}
                </Table.Cell>
                <Table.Cell>
                  {formatMoney(caseItem.paid_amount_minor, caseItem.currency)}
                </Table.Cell>
                <Table.Cell>
                  {formatMoney(caseItem.difference_minor, caseItem.currency)}
                </Table.Cell>
                <Table.Cell>
                  {caseItem.needs_human_review ? 'Required' : 'Not required'}
                </Table.Cell>
                <Table.Cell>{formatDateTime(caseItem.updated_at)}</Table.Cell>
              </Table.Row>
            )}
          </Table.Body>
        </Table.Content>
      </Table.ScrollContainer>
      <Table.Footer className="justify-between text-xs text-slate-500 dark:text-zinc-400">
        <span>{items.length} stored cases</span>
        <span>Newest first from Base API</span>
      </Table.Footer>
    </Table>
  )
}

function buildCaseListFacts(items: readonly ReconciliationCaseListItemV1[]): readonly ShellFact[] {
  if (items.length === 0) {
    return [
      { label: 'Connection', value: 'Base API' },
      { label: 'Cases', value: '0' },
      { label: 'Status', value: 'Empty' },
    ]
  }

  return [
    { label: 'Connection', value: 'Base API' },
    { label: 'Cases', value: String(items.length) },
    { label: 'Status', value: 'Loaded' },
  ]
}
