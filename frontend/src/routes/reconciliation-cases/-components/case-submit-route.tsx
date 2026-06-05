import { Alert, Button, Card, Chip } from '@heroui/react'
import { Link, useRouter } from '@tanstack/react-router'
import type { FormEvent, ReactNode } from 'react'
import { useState } from 'react'

import {
  ApiError,
  PAYMENT_TYPES,
  createReconciliationCase,
} from '../../../api/reconciliation-cases'
import type {
  PaymentType,
  ReconciliationCaseResponseV1,
} from '../../../api/reconciliation-cases'
import {
  CreateRequestValidationError,
  INITIAL_RECONCILIATION_CASE_CREATE_FORM_STATE,
  buildReconciliationCaseCreateRequest,
} from '../-utils/create-request'
import type {
  FinalAmountChoice,
  ReconciliationCaseCreateFormState,
} from '../-utils/create-request'
import {
  formatMoney,
  formatPercent,
  formatStatusLabel,
  getStatusTone,
} from '../-utils/formatters'

type FieldName = keyof ReconciliationCaseCreateFormState
type FieldErrors = Partial<Record<FieldName, string>>

interface SubmitError {
  message: string
  meta: string | null
}

export function CaseSubmitRoute() {
  const router = useRouter()
  const [form, setForm] = useState<ReconciliationCaseCreateFormState>(
    INITIAL_RECONCILIATION_CASE_CREATE_FORM_STATE,
  )
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({})
  const [submitError, setSubmitError] = useState<SubmitError | null>(null)
  const [result, setResult] = useState<ReconciliationCaseResponseV1 | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  function updateField<Field extends FieldName>(
    field: Field,
    value: ReconciliationCaseCreateFormState[Field],
  ): void {
    setForm((current) => ({ ...current, [field]: value }))
    setFieldErrors((current) => ({ ...current, [field]: undefined }))
    setSubmitError(null)
    setResult(null)
  }

  function resetForm(): void {
    setForm(INITIAL_RECONCILIATION_CASE_CREATE_FORM_STATE)
    setFieldErrors({})
    setSubmitError(null)
    setResult(null)
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault()

    if (isSubmitting) {
      return
    }

    setSubmitError(null)
    setResult(null)

    let request
    try {
      request = buildReconciliationCaseCreateRequest(form)
      setFieldErrors({})
    } catch (error) {
      if (error instanceof CreateRequestValidationError) {
        setFieldErrors(error.fieldErrors)
        setSubmitError({ message: error.message, meta: null })
        return
      }

      throw error
    }

    setIsSubmitting(true)
    try {
      const response = await createReconciliationCase(request)
      setResult(response)
      void router.invalidate()
    } catch (error) {
      setSubmitError(getSubmitError(error))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="grid gap-5">
      <Link to="/reconciliation-cases" className="recon-link w-fit">
        Back to list
      </Link>
      <Card className="recon-surface overflow-hidden">
        <Card.Header className="recon-surface__header">
          <p className="recon-eyebrow">
            Base API
          </p>
          <Card.Title id="workspace-title" className="recon-title">
            Create reconciliation case
          </Card.Title>
        </Card.Header>
        <Card.Content className="recon-surface__content grid gap-6">
          {submitError ? <SubmitErrorAlert error={submitError} /> : null}
          <form className="grid gap-7" onSubmit={handleSubmit} noValidate>
            <FormSection title="Case input">
              <TextField
                label="External reference"
                name="externalReference"
                value={form.externalReference}
                error={fieldErrors.externalReference}
                onChange={updateField}
              />
              <TextField
                label="Customer reference"
                name="customerReference"
                value={form.customerReference}
                error={fieldErrors.customerReference}
                onChange={updateField}
              />
              <TextAreaField
                label="Source text"
                name="sourceText"
                value={form.sourceText}
                error={fieldErrors.sourceText}
                onChange={updateField}
              />
            </FormSection>

            <FormSection title="Agreement extraction">
              <TextField
                label="Agreed amount"
                name="agreedAmount"
                value={form.agreedAmount}
                error={fieldErrors.agreedAmount}
                inputMode="decimal"
                onChange={updateField}
              />
              <TextField
                label="Currency"
                name="currency"
                value={form.currency}
                error={fieldErrors.currency}
                maxLength={3}
                onChange={updateField}
              />
              <PaymentTypeField value={form.paymentType} onChange={updateField} />
              <TextField
                label="Due date"
                name="dueDate"
                value={form.dueDate}
                error={fieldErrors.dueDate}
                type="date"
                onChange={updateField}
              />
              <FinalAmountField value={form.isFinalAmount} onChange={updateField} />
              <TextField
                label="Confidence"
                name="confidence"
                value={form.confidence}
                error={fieldErrors.confidence}
                inputMode="decimal"
                onChange={updateField}
              />
              <CheckboxField
                label="Needs human review"
                checked={form.needsHumanReview}
                onChange={(checked) => updateField('needsHumanReview', checked)}
              />
              <TextAreaField
                label="Evidence text"
                name="evidenceText"
                value={form.evidenceText}
                error={fieldErrors.evidenceText}
                onChange={updateField}
              />
            </FormSection>

            <FormSection title="Actual payment">
              <TextField
                label="Paid amount"
                name="actualPaidAmount"
                value={form.actualPaidAmount}
                error={fieldErrors.actualPaidAmount}
                inputMode="decimal"
                onChange={updateField}
              />
              <TextField
                label="Payment currency"
                name="actualPaymentCurrency"
                value={form.actualPaymentCurrency}
                error={fieldErrors.actualPaymentCurrency}
                maxLength={3}
                onChange={updateField}
              />
              <TextField
                label="Payment date"
                name="actualPaymentDate"
                value={form.actualPaymentDate}
                error={fieldErrors.actualPaymentDate}
                type="date"
                onChange={updateField}
              />
              <TextField
                label="Payment reference"
                name="actualPaymentReference"
                value={form.actualPaymentReference}
                error={fieldErrors.actualPaymentReference}
                onChange={updateField}
              />
              <TextField
                label="Payment method"
                name="actualPaymentMethod"
                value={form.actualPaymentMethod}
                error={fieldErrors.actualPaymentMethod}
                onChange={updateField}
              />
            </FormSection>

            <div className="flex flex-wrap gap-3">
              <Button className="recon-button recon-button--primary" type="submit" isDisabled={isSubmitting}>
                {isSubmitting ? 'Submitting' : 'Submit case'}
              </Button>
              <Button className="recon-button recon-button--secondary" type="button" variant="secondary" onPress={resetForm}>
                Reset
              </Button>
            </div>
          </form>
        </Card.Content>
      </Card>
      {result ? <SubmitResult caseDetail={result} /> : null}
    </div>
  )
}

function FormSection({ children, title }: { children: ReactNode; title: string }) {
  return (
    <section
      className="recon-section grid gap-4"
      aria-labelledby={`${title.toLowerCase().replaceAll(' ', '-')}-title`}
    >
      <h2
        id={`${title.toLowerCase().replaceAll(' ', '-')}-title`}
        className="recon-section-title"
      >
        {title}
      </h2>
      <div className="grid gap-4 md:grid-cols-2">{children}</div>
    </section>
  )
}

function TextField({
  error,
  inputMode,
  label,
  maxLength,
  name,
  onChange,
  type = 'text',
  value,
}: {
  error?: string
  inputMode?: 'decimal'
  label: string
  maxLength?: number
  name: FieldName
  onChange: <Field extends FieldName>(
    field: Field,
    value: ReconciliationCaseCreateFormState[Field],
  ) => void
  type?: 'date' | 'text'
  value: string
}) {
  return (
    <label className="recon-field grid gap-2">
      {label}
      <input
        aria-invalid={error ? true : undefined}
        inputMode={inputMode}
        maxLength={maxLength}
        type={type}
        value={value}
        onChange={(event) => onChange(name, event.target.value)}
      />
      {error ? <FieldError>{error}</FieldError> : null}
    </label>
  )
}

function TextAreaField({
  error,
  label,
  name,
  onChange,
  value,
}: {
  error?: string
  label: string
  name: FieldName
  onChange: <Field extends FieldName>(
    field: Field,
    value: ReconciliationCaseCreateFormState[Field],
  ) => void
  value: string
}) {
  return (
    <label className="recon-field grid gap-2 md:col-span-2">
      {label}
      <textarea
        aria-invalid={error ? true : undefined}
        className="min-h-28 resize-y"
        value={value}
        onChange={(event) => onChange(name, event.target.value)}
      />
      {error ? <FieldError>{error}</FieldError> : null}
    </label>
  )
}

function PaymentTypeField({
  onChange,
  value,
}: {
  onChange: <Field extends FieldName>(
    field: Field,
    value: ReconciliationCaseCreateFormState[Field],
  ) => void
  value: PaymentType
}) {
  return (
    <label className="recon-field grid gap-2">
      Payment type
      <select
        value={value}
        onChange={(event) => onChange('paymentType', event.target.value as PaymentType)}
      >
        {PAYMENT_TYPES.map((paymentType) => (
          <option key={paymentType} value={paymentType}>
            {paymentType}
          </option>
        ))}
      </select>
    </label>
  )
}

function FinalAmountField({
  onChange,
  value,
}: {
  onChange: <Field extends FieldName>(
    field: Field,
    value: ReconciliationCaseCreateFormState[Field],
  ) => void
  value: FinalAmountChoice
}) {
  return (
    <label className="recon-field grid gap-2">
      Final amount
      <select
        value={value}
        onChange={(event) => onChange('isFinalAmount', event.target.value as FinalAmountChoice)}
      >
        <option value="unknown">Unknown</option>
        <option value="yes">Yes</option>
        <option value="no">No</option>
      </select>
    </label>
  )
}

function CheckboxField({
  checked,
  label,
  onChange,
}: {
  checked: boolean
  label: string
  onChange: (checked: boolean) => void
}) {
  return (
    <label className="recon-field flex min-h-12 items-center gap-3">
      <input
        checked={checked}
        type="checkbox"
        onChange={(event) => onChange(event.target.checked)}
      />
      {label}
    </label>
  )
}

function FieldError({ children }: { children: string }) {
  return <span className="recon-error">{children}</span>
}

function SubmitErrorAlert({ error }: { error: SubmitError }) {
  return (
    <Alert status="danger" role="alert">
      <Alert.Content>
        <Alert.Title>Unable to create case</Alert.Title>
        <Alert.Description>{error.message}</Alert.Description>
        {error.meta ? (
          <p className="recon-meta">
            {error.meta}
          </p>
        ) : null}
      </Alert.Content>
    </Alert>
  )
}

function SubmitResult({ caseDetail }: { caseDetail: ReconciliationCaseResponseV1 }) {
  const decision = caseDetail.decision

  return (
    <Card className="recon-surface overflow-hidden">
      <Card.Header className="recon-surface__header">
        <div className="flex w-full flex-wrap items-start justify-between gap-3">
          <div>
            <p className="recon-eyebrow">
              Created case
            </p>
            <Card.Title className="recon-title">
              Backend decision
            </Card.Title>
          </div>
          <Chip color={getStatusTone(decision.status)} size="sm" variant="soft">
            <Chip.Label>{formatStatusLabel(decision.status)}</Chip.Label>
          </Chip>
        </div>
      </Card.Header>
      <Card.Content className="recon-surface__content grid gap-5">
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <DecisionFact label="Agreed" value={formatMoney(decision.agreed_amount_minor, decision.currency)} />
          <DecisionFact label="Paid" value={formatMoney(decision.paid_amount_minor, decision.currency)} />
          <DecisionFact label="Difference" value={formatMoney(decision.difference_minor, decision.currency)} />
          <DecisionFact label="Confidence" value={formatPercent(decision.confidence)} />
          <DecisionFact label="Review" value={decision.needs_human_review ? 'Required' : 'Not required'} />
          <DecisionFact label="Case ID" value={caseDetail.id} />
        </div>
        <div className="recon-text-block">
          <p className="recon-label">
            Reason
          </p>
          <p className="recon-copy">
            {decision.reason}
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <Link
            to="/reconciliation-cases/$caseId"
            params={{ caseId: caseDetail.id }}
            className="recon-button recon-button--primary inline-flex min-h-10 items-center"
          >
            View created case
          </Link>
          <Link
            to="/reconciliation-cases"
            className="recon-button recon-button--secondary inline-flex min-h-10 items-center"
          >
            Back to list
          </Link>
        </div>
      </Card.Content>
    </Card>
  )
}

function DecisionFact({ label, value }: { label: string; value: string }) {
  return (
    <div className="recon-fact-card">
      <p className="recon-label">
        {label}
      </p>
      <p className="recon-copy break-words">
        {value}
      </p>
    </div>
  )
}

function getSubmitError(error: unknown): SubmitError {
  if (error instanceof ApiError) {
    const meta = [error.code, error.requestId ? `request ${error.requestId}` : null]
      .filter((value) => value !== null)
      .join(' | ')

    return { message: error.message, meta: meta || null }
  }

  if (error instanceof Error) {
    return { message: error.message, meta: null }
  }

  return { message: 'Unable to create case.', meta: null }
}
