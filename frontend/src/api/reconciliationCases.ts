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

export type ReconciliationStatus = (typeof RECONCILIATION_STATUSES)[number]

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

export async function listReconciliationCases(): Promise<ReconciliationCaseListResponseV1> {
  const response = await fetch(buildApiUrl(RECONCILIATION_CASES_PATH), {
    headers: { Accept: 'application/json' },
  })

  if (!response.ok) {
    throw new Error(await readErrorMessage(response))
  }

  const body = await readJson(response)

  return parseListResponse(body)
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

async function readErrorMessage(response: Response): Promise<string> {
  const fallback = `Request failed with status ${response.status}.`

  try {
    const body: unknown = await response.json()

    if (!isRecord(body) || !isRecord(body.error)) {
      return fallback
    }

    const message = body.error.message

    return typeof message === 'string' && message.trim() ? message : fallback
  } catch {
    return fallback
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

function readOptionalNumber(value: unknown, fieldName: string): number | null {
  if (value === undefined || value === null) {
    return null
  }
  if (typeof value !== 'number' || !Number.isFinite(value)) {
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
