import type { ScanRequest, ScanResponse } from './types'

const API_BASE = '/api'

const MSG_ANALYSIS_SOFT =
  'Estamos analisando o site; isso pode levar alguns segundos dependendo da complexidade.'

function formatDetail(detail: unknown): string {
  if (detail == null) {
    return ''
  }
  if (typeof detail === 'string') {
    return detail
  }
  if (Array.isArray(detail)) {
    return detail
      .map((item: unknown) => {
        if (item && typeof item === 'object' && 'msg' in item) {
          return String((item as { msg: string }).msg)
        }
        return JSON.stringify(item)
      })
      .join(' ')
  }
  if (typeof detail === 'object' && detail !== null && 'detail' in detail) {
    return formatDetail((detail as { detail: unknown }).detail)
  }
  return String(detail)
}

export async function runScan(req: ScanRequest): Promise<ScanResponse> {
  let res: Response
  try {
    res = await fetch(`${API_BASE}/scan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    })
  } catch {
    throw new Error(
      'Não foi possível contactar o motor de análise Lume. Confirme que o backend está em execução em http://127.0.0.1:8000 e que abriu esta página em http://127.0.0.1:5173.',
    )
  }

  if (!res.ok) {
    const raw = await res.text()
    let detail = res.statusText
    try {
      const parsed = JSON.parse(raw) as { detail?: unknown; message?: unknown }
      detail = formatDetail(parsed.detail ?? parsed.message ?? detail)
    } catch {
      // texto não JSON
    }

    if (res.status >= 500) {
      throw new Error(MSG_ANALYSIS_SOFT)
    }

    throw new Error(
      detail.trim() || 'Não foi possível iniciar a análise no momento. Verifique a URL e tente novamente.',
    )
  }

  return res.json() as Promise<ScanResponse>
}
