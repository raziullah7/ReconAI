const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000'

export function getApiBaseUrl(): string {
  const configuredUrl = import.meta.env.VITE_RECONAI_API_BASE_URL?.trim()
  const baseUrl = configuredUrl || DEFAULT_API_BASE_URL

  return baseUrl.replace(/\/+$/, '')
}
