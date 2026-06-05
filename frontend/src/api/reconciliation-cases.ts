import { getApiBaseUrl } from '../config/api'

const RECONCILIATION_CASES_PATH = '/v1/reconciliation-cases'

const RECONCILIATION_STATUSES = [
  'RECONCILED',
  'UNDERPAID',
  'OVERPAID',
  'PARTIAL_PAYMENT',
  'PAYMENT_NOT_FOUND',
  'MULTIPLE_MATCHES_FOUND',
  'NEEDS_REVIEW',
  'FAILED',
] as const

export const PAYMENT_TYPES = [
  'FULL_PAYMENT',
  'ADVANCE',
  'PARTIAL_PAYMENT',
  'INSTALLMENT',
  'BALANCE_PAYMENT',
  'DISCOUNTED_AMOUNT',
  'UNKNOWN',
] as const

export type ReconciliationStatus = (typeof RECONCILIATION_STATUSES)[number]
export type PaymentType = (typeof PAYMENT_TYPES)[number]

export interface AgreementExtractionInputV1 {
  schema_version: 'agreement_extraction.v1'
  agreed_amount_minor: number | null
  currency: string | null
  payment_type: PaymentType
  due_date: string | null
  is_final_amount: boolean | null
  evidence_text: string | null
  confidence: number
  needs_human_review: boolean
  model_name?: string | null
  raw_llm_output?: unknown
}

export interface ActualPaymentInputV1 {
  paid_amount_minor: number | null
  currency: string | null
  payment_date?: string | null
  reference?: string | null
  payment_method?: string | null
}

export interface ReconciliationDecisionV1 {
  status: ReconciliationStatus
  agreed_amount_minor: number | null
  paid_amount_minor: number | null
  difference_minor: number | null
  currency: string | null
  reason: string
  needs_human_review: boolean
  confidence: number
}

export interface ReconciliationCaseResponseV1 {
  id: string
  external_reference?: string | null
  customer_reference?: string | null
  source_text?: string | null
  extraction: AgreementExtractionInputV1
  actual_payment?: ActualPaymentInputV1 | null
  decision: ReconciliationDecisionV1
  created_at: string
  updated_at: string
}

export interface ReconciliationCaseCreateRequestV1 {
  external_reference?: string | null
  customer_reference?: string | null
  source_text?: string | null
  extraction: AgreementExtractionInputV1
  actual_payment?: ActualPaymentInputV1 | null
}


export interface ReconciliationCaseListItemV1 {
  id: string
  external_reference?: string | null
  customer_reference?: string | null
  status: ReconciliationStatus
  agreed_amount_minor: number | null
  paid_amount_minor: number | null
  difference_minor: number | null
  currency: string | null
  needs_human_review: boolean
  created_at: string
  updated_at: string
}

export interface ReconciliationCaseListResponseV1 {
  items: ReconciliationCaseListItemV1[]
}

export class ApiError extends Error {
  readonly code: string | null
  readonly requestId: string | null
  readonly status: number

  constructor(message: string, status: number, code: string | null, requestId: string | null) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.requestId = requestId
  }
}

export async function listReconciliationCases(): Promise<ReconciliationCaseListResponseV1> {
  const response = await fetch(buildApiUrl(RECONCILIATION_CASES_PATH), {
    headers: { Accept: 'application/json' },
  })

  if (!response.ok) {
    throw await readApiError(response)
  }

  return parseListResponse(await readJson(response))
}

export async function getReconciliationCase(
  caseId: string,
): Promise<ReconciliationCaseResponseV1> {
  const response = await fetch(
    buildApiUrl(`${RECONCILIATION_CASES_PATH}/${encodeURIComponent(caseId)}`),
    { headers: { Accept: 'application/json' } },
  )

  if (!response.ok) {
    throw await readApiError(response)
  }

  return parseCaseResponse(await readJson(response))
}

export async function createReconciliationCase(
  input: ReconciliationCaseCreateRequestV1,
): Promise<ReconciliationCaseResponseV1> {
  const response = await fetch(buildApiUrl(RECONCILIATION_CASES_PATH), {
    body: JSON.stringify(input),
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    method: 'POST',
  })

  if (!response.ok) {
    throw await readApiError(response)
  }

  return parseCaseResponse(await readJson(response))
}


function buildApiUrl(path: string): string {
  return new URL(path, getApiBaseUrl()).toString()
}

async function readJson(response: Response): Promise<unknown> {
  try {
    return await response.json()
  } catch {
    throw new Error('The backend returned an invalid JSON response.')
  }
}

async function readApiError(response: Response): Promise<ApiError> {
  const fallback = `Request failed with status ${response.status}.`

  try {
    const body: unknown = await response.json()

    if (!isRecord(body) || !isRecord(body.error)) {
      return new ApiError(fallback, response.status, null, null)
    }

    const message = body.error.message
    const code = body.error.code
    const requestId = body.error.request_id

    return new ApiError(
      typeof message === 'string' && message.trim() ? message : fallback,
      response.status,
      typeof code === 'string' && code.trim() ? code : null,
      typeof requestId === 'string' && requestId.trim() ? requestId : null,
    )
  } catch {
    return new ApiError(fallback, response.status, null, null)
  }
}

function parseListResponse(value: unknown): ReconciliationCaseListResponseV1 {
  if (!isRecord(value) || !Array.isArray(value.items)) {
    throw new Error('The backend returned an unexpected case list response.')
  }

  return { items: value.items.map(parseListItem) }
}

function parseListItem(value: unknown): ReconciliationCaseListItemV1 {
  if (!isRecord(value)) {
    throw new Error('The backend returned an invalid case summary.')
  }

  return {
    id: readRequiredString(value.id, 'id'),
    external_reference: readOptionalString(value.external_reference, 'external_reference'),
    customer_reference: readOptionalString(value.customer_reference, 'customer_reference'),
    status: readStatus(value.status),
    agreed_amount_minor: readOptionalNumber(value.agreed_amount_minor, 'agreed_amount_minor'),
    paid_amount_minor: readOptionalNumber(value.paid_amount_minor, 'paid_amount_minor'),
    difference_minor: readOptionalNumber(value.difference_minor, 'difference_minor'),
    currency: readOptionalString(value.currency, 'currency'),
    needs_human_review: readRequiredBoolean(value.needs_human_review, 'needs_human_review'),
    created_at: readRequiredString(value.created_at, 'created_at'),
    updated_at: readRequiredString(value.updated_at, 'updated_at'),
  }
}

function parseCaseResponse(value: unknown): ReconciliationCaseResponseV1 {
  if (!isRecord(value)) {
    throw new Error('The backend returned an invalid case detail.')
  }

  return {
    id: readRequiredString(value.id, 'id'),
    external_reference: readOptionalString(value.external_reference, 'external_reference'),
    customer_reference: readOptionalString(value.customer_reference, 'customer_reference'),
    source_text: readOptionalString(value.source_text, 'source_text'),
    extraction: parseAgreementExtraction(value.extraction),
    actual_payment: parseActualPayment(value.actual_payment),
    decision: parseDecision(value.decision),
    created_at: readRequiredString(value.created_at, 'created_at'),
    updated_at: readRequiredString(value.updated_at, 'updated_at'),
  }
}

function parseAgreementExtraction(value: unknown): AgreementExtractionInputV1 {
  if (!isRecord(value)) {
    throw new Error('The backend returned an invalid extraction.')
  }

  return {
    schema_version: readSchemaVersion(value.schema_version),
    agreed_amount_minor: readOptionalNumber(value.agreed_amount_minor, 'agreed_amount_minor'),
    currency: readOptionalString(value.currency, 'currency'),
    payment_type: readPaymentType(value.payment_type),
    due_date: readOptionalString(value.due_date, 'due_date'),
    is_final_amount: readOptionalBoolean(value.is_final_amount, 'is_final_amount'),
    evidence_text: readOptionalString(value.evidence_text, 'evidence_text'),
    confidence: readRequiredNumber(value.confidence, 'confidence'),
    needs_human_review: readRequiredBoolean(value.needs_human_review, 'needs_human_review'),
    model_name: readOptionalString(value.model_name, 'model_name'),
    raw_llm_output: value.raw_llm_output,
  }
}

function parseActualPayment(value: unknown): ActualPaymentInputV1 | null {
  if (value === undefined || value === null) {
    return null
  }

  if (!isRecord(value)) {
    throw new Error('The backend returned an invalid actual payment.')
  }

  return {
    paid_amount_minor: readOptionalNumber(value.paid_amount_minor, 'paid_amount_minor'),
    currency: readOptionalString(value.currency, 'currency'),
    payment_date: readOptionalString(value.payment_date, 'payment_date'),
    reference: readOptionalString(value.reference, 'reference'),
    payment_method: readOptionalString(value.payment_method, 'payment_method'),
  }
}

function parseDecision(value: unknown): ReconciliationDecisionV1 {
  if (!isRecord(value)) {
    throw new Error('The backend returned an invalid decision.')
  }

  return {
    status: readStatus(value.status),
    agreed_amount_minor: readOptionalNumber(value.agreed_amount_minor, 'agreed_amount_minor'),
    paid_amount_minor: readOptionalNumber(value.paid_amount_minor, 'paid_amount_minor'),
    difference_minor: readOptionalNumber(value.difference_minor, 'difference_minor'),
    currency: readOptionalString(value.currency, 'currency'),
    reason: readRequiredString(value.reason, 'reason'),
    needs_human_review: readRequiredBoolean(value.needs_human_review, 'needs_human_review'),
    confidence: readRequiredNumber(value.confidence, 'confidence'),
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}

function readStatus(value: unknown): ReconciliationStatus {
  if (typeof value !== 'string') {
    throw new Error('The backend returned a case summary without a valid status.')
  }

  const status = RECONCILIATION_STATUSES.find((candidate) => candidate === value)

  if (status === undefined) {
    throw new Error('The backend returned an unknown reconciliation status.')
  }

  return status
}

function readPaymentType(value: unknown): PaymentType {
  if (typeof value !== 'string') {
    throw new Error('The backend returned an extraction without a valid payment_type.')
  }

  const paymentType = PAYMENT_TYPES.find((candidate) => candidate === value)

  if (paymentType === undefined) {
    throw new Error('The backend returned an unknown payment type.')
  }

  return paymentType
}

function readSchemaVersion(value: unknown): 'agreement_extraction.v1' {
  if (value !== 'agreement_extraction.v1') {
    throw new Error('The backend returned an unsupported extraction schema version.')
  }

  return value
}

function readRequiredString(value: unknown, fieldName: string): string {
  if (typeof value !== 'string' || value.length === 0) {
    throw new Error(`The backend returned a case summary without ${fieldName}.`)
  }

  return value
}

function readOptionalString(value: unknown, fieldName: string): string | null {
  if (value === undefined || value === null) {
    return null
  }

  if (typeof value !== 'string') {
    throw new Error(`The backend returned an invalid ${fieldName}.`)
  }

  return value
}

function readRequiredNumber(value: unknown, fieldName: string): number {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new Error(`The backend returned an invalid ${fieldName}.`)
  }

  return value
}

function readOptionalNumber(value: unknown, fieldName: string): number | null {
  if (value === undefined || value === null) {
    return null
  }
  return readRequiredNumber(value, fieldName)
}

function readOptionalBoolean(value: unknown, fieldName: string): boolean | null {
  if (value === undefined || value === null) {
    return null
  }

  if (typeof value !== 'boolean') {
    throw new Error(`The backend returned an invalid ${fieldName}.`)
  }

  return value
}

function readRequiredBoolean(value: unknown, fieldName: string): boolean {
  if (typeof value !== 'boolean') {
    throw new Error(`The backend returned an invalid ${fieldName}.`)
  }

  return value
}
