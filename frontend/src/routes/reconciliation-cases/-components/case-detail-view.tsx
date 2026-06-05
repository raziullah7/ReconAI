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
      <div className="flex flex-wrap gap-4">
        <Link to="/reconciliation-cases" className="recon-link w-fit">
          Back to list
        </Link>
        <Link to="/reconciliation-cases/new" className="recon-link w-fit">
          Create case
        </Link>
      </div>
      <Card className="recon-surface overflow-hidden">
        <CaseDetailCardHeader />
        <Card.Content className="recon-surface__content grid gap-8">
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
          <p className="recon-eyebrow">
            Case
          </p>
          <h2 id="case-identity-title" className="recon-section-title">
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
        <div className="recon-fact-card" key={item.label}>
          <dt className="recon-label">
            {item.label}
          </dt>
          <dd className="recon-copy break-words">
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
    <div className="recon-text-block">
      {hideLabel ? null : (
        <p className="recon-label">
          {label}
        </p>
      )}
      <p className="recon-copy whitespace-pre-wrap break-words">
        {formatReference(value)}
      </p>
    </div>
  )
}

function SectionTitle({ id, children }: { id: string; children: ReactNode }) {
  return (
    <h3 id={id} className="recon-section-title">
      {children}
    </h3>
  )
}
