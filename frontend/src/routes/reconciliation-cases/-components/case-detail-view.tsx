import { Card, Chip } from '@heroui/react'
import { Link } from '@tanstack/react-router'
import type { ReactNode } from 'react'

import type {
  ActualPaymentInputV1,
  AgreementExtractionInputV1,
  ReconciliationCaseResponseV1,
  ReconciliationDecisionV1,
} from '../../../api/reconciliation-cases'
import { CaseDetailCardHeader } from './case-detail-state'
import {
  formatBoolean,
  formatDate,
  formatDateTime,
  formatEnumLabel,
  formatMoney,
  formatPercent,
  formatReference,
  formatStatusLabel,
  getStatusTone,
} from '../-utils/formatters'

interface CaseDetailViewProps {
  caseDetail: ReconciliationCaseResponseV1
}

export function CaseDetailView({ caseDetail }: CaseDetailViewProps) {
  return (
    <div className="grid gap-5">
      <Link
        to="/reconciliation-cases"
        className="w-fit text-sm font-semibold text-blue-700 hover:text-blue-800 dark:text-blue-300 dark:hover:text-blue-200"
      >
        Back to list
      </Link>
      <Card className="overflow-hidden border border-slate-200 bg-white shadow-none dark:border-zinc-800 dark:bg-zinc-900">
        <CaseDetailCardHeader />
        <Card.Content className="grid gap-8 p-6">
          <CaseIdentity caseDetail={caseDetail} />
          <DecisionSection decision={caseDetail.decision} />
          <ExtractionSection extraction={caseDetail.extraction} />
          <ActualPaymentSection actualPayment={caseDetail.actual_payment ?? null} />
          <TextSection title="Source text" value={caseDetail.source_text} />
          <DetailGrid
            items={[
              { label: 'Created', value: formatDateTime(caseDetail.created_at) },
              { label: 'Updated', value: formatDateTime(caseDetail.updated_at) },
            ]}
          />
        </Card.Content>
      </Card>
    </div>
  )
}

function CaseIdentity({ caseDetail }: CaseDetailViewProps) {
  return (
    <section className="grid gap-4" aria-labelledby="case-identity-title">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="m-0 text-xs font-bold uppercase text-slate-500 dark:text-zinc-400">
            Case
          </p>
          <h2 id="case-identity-title" className="m-0 mt-1 text-xl font-semibold">
            {formatReference(caseDetail.external_reference)}
          </h2>
        </div>
        <Chip color={getStatusTone(caseDetail.decision.status)} size="sm" variant="soft">
          <Chip.Label>{formatStatusLabel(caseDetail.decision.status)}</Chip.Label>
        </Chip>
      </div>
      <DetailGrid
        items={[
          { label: 'Customer', value: formatReference(caseDetail.customer_reference) },
          { label: 'Case ID', value: caseDetail.id },
        ]}
      />
    </section>
  )
}

function DecisionSection({ decision }: { decision: ReconciliationDecisionV1 }) {
  return (
    <section className="grid gap-4" aria-labelledby="decision-title">
      <SectionTitle id="decision-title">Decision</SectionTitle>
      <DetailGrid
        items={[
          { label: 'Status', value: formatStatusLabel(decision.status) },
          { label: 'Agreed', value: formatMoney(decision.agreed_amount_minor, decision.currency) },
          { label: 'Paid', value: formatMoney(decision.paid_amount_minor, decision.currency) },
          { label: 'Difference', value: formatMoney(decision.difference_minor, decision.currency) },
          { label: 'Human review', value: decision.needs_human_review ? 'Required' : 'Not required' },
          { label: 'Confidence', value: formatPercent(decision.confidence) },
        ]}
      />
      <TextBlock label="Reason" value={decision.reason} />
    </section>
  )
}

function ExtractionSection({ extraction }: { extraction: AgreementExtractionInputV1 }) {
  return (
    <section className="grid gap-4" aria-labelledby="extraction-title">
      <SectionTitle id="extraction-title">Extraction</SectionTitle>
      <DetailGrid
        items={[
          { label: 'Agreed amount', value: formatMoney(extraction.agreed_amount_minor, extraction.currency) },
          { label: 'Currency', value: formatReference(extraction.currency) },
          { label: 'Payment type', value: formatEnumLabel(extraction.payment_type) },
          { label: 'Due date', value: formatDate(extraction.due_date) },
          { label: 'Final amount', value: formatBoolean(extraction.is_final_amount) },
          { label: 'Human review', value: extraction.needs_human_review ? 'Required' : 'Not required' },
          { label: 'Confidence', value: formatPercent(extraction.confidence) },
          { label: 'Model', value: formatReference(extraction.model_name) },
        ]}
      />
      <TextBlock label="Evidence" value={extraction.evidence_text} />
    </section>
  )
}

function ActualPaymentSection({ actualPayment }: { actualPayment: ActualPaymentInputV1 | null }) {
  if (actualPayment === null) {
    return <TextSection title="Actual payment" value="No payment evidence supplied" />
  }

  return (
    <section className="grid gap-4" aria-labelledby="payment-title">
      <SectionTitle id="payment-title">Actual payment</SectionTitle>
      <DetailGrid
        items={[
          { label: 'Paid amount', value: formatMoney(actualPayment.paid_amount_minor, actualPayment.currency) },
          { label: 'Currency', value: formatReference(actualPayment.currency) },
          { label: 'Payment date', value: formatDate(actualPayment.payment_date) },
          { label: 'Reference', value: formatReference(actualPayment.reference) },
          { label: 'Method', value: formatReference(actualPayment.payment_method) },
        ]}
      />
    </section>
  )
}

function TextSection({ title, value }: { title: string; value: string | null | undefined }) {
  return (
    <section className="grid gap-4" aria-labelledby={`${title.toLowerCase().replaceAll(' ', '-')}-title`}>
      <SectionTitle id={`${title.toLowerCase().replaceAll(' ', '-')}-title`}>
        {title}
      </SectionTitle>
      <TextBlock label={title} value={value} hideLabel />
    </section>
  )
}

function DetailGrid({ items }: { items: readonly { label: string; value: ReactNode }[] }) {
  return (
    <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {items.map((item) => (
        <div className="rounded-md border border-slate-200 p-4 dark:border-zinc-800" key={item.label}>
          <dt className="text-xs font-semibold text-slate-500 dark:text-zinc-400">
            {item.label}
          </dt>
          <dd className="m-0 mt-1 break-words text-sm font-semibold text-slate-950 dark:text-zinc-50">
            {item.value}
          </dd>
        </div>
      ))}
    </dl>
  )
}

function TextBlock({ label, value, hideLabel = false }: {
  label: string
  value: string | null | undefined
  hideLabel?: boolean
}) {
  return (
    <div className="rounded-md border border-slate-200 p-4 dark:border-zinc-800">
      {hideLabel ? null : (
        <p className="m-0 text-xs font-semibold text-slate-500 dark:text-zinc-400">
          {label}
        </p>
      )}
      <p className="m-0 mt-1 whitespace-pre-wrap break-words text-sm text-slate-800 dark:text-zinc-200">
        {formatReference(value)}
      </p>
    </div>
  )
}

function SectionTitle({ id, children }: { id: string; children: ReactNode }) {
  return (
    <h3 id={id} className="m-0 text-base font-semibold text-slate-950 dark:text-zinc-50">
      {children}
    </h3>
  )
}
