import type { ReconciliationStatus } from '../../../api/reconciliation-cases'

type StatusTone = 'success' | 'warning' | 'danger' | 'default'

const STATUS_LABELS: Record<ReconciliationStatus, string> = {
  RECONCILED: 'Reconciled',
  UNDERPAID: 'Underpaid',
  OVERPAID: 'Overpaid',
  PARTIAL_PAYMENT: 'Partial payment',
  PAYMENT_NOT_FOUND: 'Payment not found',
  MULTIPLE_MATCHES_FOUND: 'Multiple matches found',
  NEEDS_REVIEW: 'Needs review',
  FAILED: 'Failed',
}

export function formatReference(value: string | null | undefined): string {
  return value?.trim() ? value : 'Not provided'
}

export function formatMoney(amountMinor: number | null, currency: string | null): string {
  if (amountMinor === null) {
    return 'Not provided'
  }

  const amountMajor = amountMinor / 100
  const formattedAmount = new Intl.NumberFormat(undefined, {
    maximumFractionDigits: 2,
    minimumFractionDigits: 2,
  }).format(amountMajor)

  return currency ? `${currency} ${formattedAmount}` : `${formattedAmount} currency missing`
}

export function formatDateTime(value: string): string {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}

export function formatStatusLabel(status: ReconciliationStatus): string {
  return STATUS_LABELS[status]
}

export function getStatusTone(status: ReconciliationStatus): StatusTone {
  if (status === 'RECONCILED') {
    return 'success'
  }

  if (status === 'FAILED') {
    return 'danger'
  }

  return 'warning'
}
