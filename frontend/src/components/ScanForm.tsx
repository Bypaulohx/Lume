import { useState, FormEvent } from 'react'
import { runScan } from '../api'
import type { ScanRequest } from '../types'

interface Props {
  onResult: (data: Awaited<ReturnType<typeof runScan>>) => void
  onError: (msg: string) => void
  onLoading: (loading: boolean) => void
  disabled?: boolean
}

function normalizeUrl(rawUrl: string) {
  const trimmed = rawUrl.trim()
  if (!trimmed) {
    return ''
  }
  if (/^https?:\/\//i.test(trimmed)) {
    return trimmed
  }
  return `https://${trimmed}`
}

export function ScanForm({ onResult, onError, onLoading, disabled }: Props) {
  const [url, setUrl] = useState('')
  const [xss, setXss] = useState(true)
  const [sqli, setSqli] = useState(true)
  const [headers, setHeaders] = useState(true)
  const [infra, setInfra] = useState(true)
  const [sslTls, setSslTls] = useState(true)
  const [dynamic, setDynamic] = useState(true)
  const [insecure, setInsecure] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()

    if (!url.trim()) {
      onError('Informe a URL alvo.')
      return
    }

    const targetUrl = normalizeUrl(url)
    try {
      new URL(targetUrl)
    } catch {
      onError('Formato de URL inválido. Use algo como exemplo.com ou https://exemplo.com')
      return
    }

    onLoading(true)
    try {
      const req: ScanRequest = {
        url: targetUrl,
        xss,
        sqli,
        headers,
        infra,
        ssl_tls: sslTls,
        dynamic,
        timeout: 10,
        insecure,
      }
      const data = await runScan(req)
      onResult(data)
    } catch (err) {
      if (err instanceof Error) {
        onError(err.message)
      } else {
        onError(
          'Estamos analisando o site; isso pode levar alguns segundos dependendo da complexidade. Tente novamente daqui a pouco.',
        )
      }
    } finally {
      onLoading(false)
    }
  }

  return (
    <form className="scan-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="url">URL alvo</label>
        <input
          id="url"
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Digite a URL alvo, por exemplo exemplo.com"
          disabled={disabled}
        />
        {url.trim() && (
          <p className="url-preview">
            Será usado: <strong>{normalizeUrl(url)}</strong>
          </p>
        )}
      </div>

      <div className="form-group form-checks">
        <span className="checks-label">Testes a executar:</span>
        <label className="checkbox">
          <input
            type="checkbox"
            checked={headers}
            onChange={(e) => setHeaders(e.target.checked)}
            disabled={disabled}
          />
          Headers de segurança
        </label>
        <label className="checkbox">
          <input
            type="checkbox"
            checked={xss}
            onChange={(e) => setXss(e.target.checked)}
            disabled={disabled}
          />
          XSS refletido
        </label>
        <label className="checkbox">
          <input
            type="checkbox"
            checked={sqli}
            onChange={(e) => setSqli(e.target.checked)}
            disabled={disabled}
          />
          SQL Injection
        </label>
        <label className="checkbox">
          <input
            type="checkbox"
            checked={infra}
            onChange={(e) => setInfra(e.target.checked)}
            disabled={disabled}
          />
          Scan de portas e rede (DNS / subdomínios)
        </label>
        <label className="checkbox">
          <input
            type="checkbox"
            checked={sslTls}
            onChange={(e) => setSslTls(e.target.checked)}
            disabled={disabled}
          />
          Análise de certificado SSL/TLS
        </label>
        <label className="checkbox">
          <input
            type="checkbox"
            checked={dynamic}
            onChange={(e) => setDynamic(e.target.checked)}
            disabled={disabled}
          />
          Simulação de Navegador (Dinâmico)
        </label>
        <label className="checkbox">
          <input
            type="checkbox"
            checked={insecure}
            onChange={(e) => setInsecure(e.target.checked)}
            disabled={disabled}
          />
          Ignorar erros TLS (--insecure)
        </label>
      </div>

      <button type="submit" className="btn-primary" disabled={disabled}>
        Iniciar varredura
      </button>
    </form>
  )
}
