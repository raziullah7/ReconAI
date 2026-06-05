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
      <div className="grid gap-4">
        <Card className="recon-surface recon-surface--stable overflow-hidden">
          <CaseListCardHeader action={<CreateCaseAction />} />
          <Card.Content className="recon-surface__content">
            {items.length === 0 ? <EmptyContent /> : <SuccessContent items={items} />}
          </Card.Content>
        </Card>
      </div>
    </CaseListFrame>
  )
}

function EmptyContent() {
  return (
    <div>
      <CaseListEmptyState />
    </div>
  )
}

function CreateCaseAction() {
  return (
    <Link
      to="/reconciliation-cases/new"
      className="recon-button recon-button--primary inline-flex min-h-10 items-center gap-2"
    >
      <span className="recon-button__icon" aria-hidden="true">
        +
      </span>
      <span>Create case</span>
    </Link>
  )
}

function SuccessContent({ items }: { items: ReconciliationCaseListItemV1[] }) {
  return (
    <Table className="recon-table" variant="secondary">
      <Table.ScrollContainer className="recon-table__scroll">
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
                  <div className="recon-case-cell grid min-w-0 gap-1">
                    <Link
                      to="/reconciliation-cases/$caseId"
                      params={{ caseId: caseItem.id }}
                      className="recon-link"
                    >
                      {formatReference(caseItem.external_reference)}
                    </Link>
                    <p className="recon-meta">
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
                <Table.Cell>
                  <UpdatedAt value={caseItem.updated_at} />
                </Table.Cell>
              </Table.Row>
            )}
          </Table.Body>
        </Table.Content>
      </Table.ScrollContainer>
      <Table.Footer className="recon-meta justify-between">
        <span>{items.length} stored cases</span>
        <span>Newest first from Base API</span>
      </Table.Footer>
    </Table>
  )
}

function UpdatedAt({ value }: { value: string }) {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return <span>{value}</span>
  }

  return (
    <time className="recon-updated-at" dateTime={value}>
      <span>
        {new Intl.DateTimeFormat(undefined, {
          day: 'numeric',
          month: 'short',
          year: 'numeric',
        }).format(date)}
      </span>
      <span>
        {new Intl.DateTimeFormat(undefined, {
          hour: 'numeric',
          minute: '2-digit',
        }).format(date)}
      </span>
    </time>
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
