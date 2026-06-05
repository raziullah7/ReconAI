import type {
  PaymentType,
  ReconciliationCaseCreateRequestV1,
} from '../../../api/reconciliation-cases'

export type FinalAmountChoice = 'unknown' | 'yes' | 'no'

export interface ReconciliationCaseCreateFormState {
  externalReference: string
  customerReference: string
  sourceText: string
  agreedAmount: string
  currency: string
  paymentType: PaymentType
  dueDate: string
  isFinalAmount: FinalAmountChoice
  evidenceText: string
  confidence: string
  needsHumanReview: boolean
  actualPaidAmount: string
  actualPaymentCurrency: string
  actualPaymentDate: string
  actualPaymentReference: string
  actualPaymentMethod: string
}

type FieldErrorMap = Partial<Record<keyof ReconciliationCaseCreateFormState, string>>

export const INITIAL_RECONCILIATION_CASE_CREATE_FORM_STATE: ReconciliationCaseCreateFormState = {
  externalReference: '',
  customerReference: '',
  sourceText: '',
  agreedAmount: '',
  currency: 'PKR',
  paymentType: 'FULL_PAYMENT',
  dueDate: '',
  isFinalAmount: 'unknown',
  evidenceText: '',
  confidence: '0.90',
  needsHumanReview: false,
  actualPaidAmount: '',
  actualPaymentCurrency: '',
  actualPaymentDate: '',
  actualPaymentReference: '',
  actualPaymentMethod: '',
}

export class CreateRequestValidationError extends Error {
  readonly fieldErrors: FieldErrorMap

  constructor(fieldErrors: FieldErrorMap) {
    super('Please fix the highlighted fields before submitting.')
    this.name = 'CreateRequestValidationError'
    this.fieldErrors = fieldErrors
  }
}

export function buildReconciliationCaseCreateRequest(
  form: ReconciliationCaseCreateFormState,
): ReconciliationCaseCreateRequestV1 {
  const fieldErrors: FieldErrorMap = {}
  const agreedAmountMinor = parseOptionalAmount(form.agreedAmount, 'agreedAmount', fieldErrors)
  const paidAmountMinor = parseOptionalAmount(
    form.actualPaidAmount,
    'actualPaidAmount',
    fieldErrors,
  )
  const confidence = parseRequiredConfidence(form.confidence, fieldErrors)
  const currency = normalizeOptionalCurrency(form.currency, 'currency', fieldErrors)
  const paymentCurrency = normalizeOptionalCurrency(
    form.actualPaymentCurrency,
    'actualPaymentCurrency',
    fieldErrors,
  )

  if (Object.keys(fieldErrors).length > 0) {
    throw new CreateRequestValidationError(fieldErrors)
  }

  const actualPaymentFields = {
    paid_amount_minor: paidAmountMinor,
    currency: paymentCurrency,
    payment_date: normalizeOptionalString(form.actualPaymentDate),
    reference: normalizeOptionalString(form.actualPaymentReference),
    payment_method: normalizeOptionalString(form.actualPaymentMethod),
  }
  const hasActualPayment = Object.values(actualPaymentFields).some((value) => value !== null)

  return {
    external_reference: normalizeOptionalString(form.externalReference),
    customer_reference: normalizeOptionalString(form.customerReference),
    source_text: normalizeOptionalString(form.sourceText),
    extraction: {
      schema_version: 'agreement_extraction.v1',
      agreed_amount_minor: agreedAmountMinor,
      currency,
      payment_type: form.paymentType,
      due_date: normalizeOptionalString(form.dueDate),
      is_final_amount: parseFinalAmountChoice(form.isFinalAmount),
      evidence_text: normalizeOptionalString(form.evidenceText),
      confidence,
      needs_human_review: form.needsHumanReview,
    },
    actual_payment: hasActualPayment ? actualPaymentFields : null,
  }
}

function parseOptionalAmount(
  value: string,
  field: 'agreedAmount' | 'actualPaidAmount',
  fieldErrors: FieldErrorMap,
): number | null {
  const trimmed = value.trim()

  if (!trimmed) {
    return null
  }

  if (!/^\d+(?:\.\d{1,2})?$/.test(trimmed)) {
    fieldErrors[field] = 'Use a positive amount with up to two decimal places.'
    return null
  }

  const [wholePart, decimalPart = ''] = trimmed.split('.')
  return Number(wholePart) * 100 + Number(decimalPart.padEnd(2, '0'))
}

function parseRequiredConfidence(
  value: string,
  fieldErrors: FieldErrorMap,
): number {
  const trimmed = value.trim()
  const confidence = Number(trimmed)

  if (!trimmed || !Number.isFinite(confidence) || confidence < 0 || confidence > 1) {
    fieldErrors.confidence = 'Enter a confidence value from 0 to 1.'
    return 0
  }

  return confidence
}

function normalizeOptionalCurrency(
  value: string,
  field: 'currency' | 'actualPaymentCurrency',
  fieldErrors: FieldErrorMap,
): string | null {
  const trimmed = value.trim()

  if (!trimmed) {
    return null
  }

  if (!/^[A-Z]{3}$/.test(trimmed)) {
    fieldErrors[field] = 'Use a three-letter uppercase currency code.'
    return null
  }

  return trimmed
}

function normalizeOptionalString(value: string): string | null {
  const trimmed = value.trim()
  return trimmed ? trimmed : null
}

function parseFinalAmountChoice(value: FinalAmountChoice): boolean | null {
  if (value === 'yes') {
    return true
  }

  if (value === 'no') {
    return false
  }

  return null
}
