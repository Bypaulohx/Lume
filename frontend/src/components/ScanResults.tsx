import type { ScanResponse, ScanResult } from '../types'

interface Props {
  data: ScanResponse
}

export function ScanResults({ data }: Props) {
  return (
    <section className="results">
      <h2 className="results-title">Resultados — {data.target}</h2>

      {data.results.map((r) => (
        <ResultBlock key={r.type} result={r} />
      ))}
    </section>
  )
}

function ResultBlock({ result }: { result: ScanResult }) {
  if (result.type === 'headers') {
    return (
      <div className="result-card">
        <div className="result-header">
          <h3>Headers de Segurança</h3>
          <StatusBadge ok={result.ok} />
        </div>
        {result.missing.length > 0 ? (
          <table className="result-table">
            <thead>
              <tr>
                <th>Header ausente</th>
                <th>Recomendação</th>
              </tr>
            </thead>
            <tbody>
              {result.missing.map((m) => (
                <tr key={m.header}>
                  <td><code>{m.header}</code></td>
                  <td>{m.hint}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="result-ok">✓ Todos os headers recomendados estão presentes.</p>
        )}
        {result.notes.length > 0 && (
          <ul className="result-notes">
            {result.notes.map((n, i) => (
              <li key={i}>{n}</li>
            ))}
          </ul>
        )}
      </div>
    )
  }

  if (result.type === 'xss') {
    return (
      <div className="result-card">
        <div className="result-header">
          <h3>XSS Refletido</h3>
          <StatusBadge ok={!result.vulnerable} />
        </div>
        <p className="result-meta">Parâmetros testados: {result.tested}</p>
        {result.vulnerable && result.findings.length > 0 ? (
          <table className="result-table">
            <thead>
              <tr>
                <th>Parâmetro</th>
                <th>Payload</th>
                <th>URL</th>
                <th>Evidência</th>
              </tr>
            </thead>
            <tbody>
              {result.findings.map((f, i) => (
                <tr key={i}>
                  <td><code>{f.param}</code></td>
                  <td><code className="payload">{f.payload}</code></td>
                  <td><a href={f.url} target="_blank" rel="noopener noreferrer">{f.url}</a></td>
                  <td>{f.evidence}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="result-ok">Nenhuma vulnerabilidade XSS refletida encontrada.</p>
        )}
      </div>
    )
  }

  if (result.type === 'sqli') {
    return (
      <div className="result-card">
        <div className="result-header">
          <h3>SQL Injection</h3>
          <StatusBadge ok={!result.vulnerable} />
        </div>
        <p className="result-meta">Payloads testados: {result.tested}</p>
        {result.vulnerable && result.findings.length > 0 ? (
          <table className="result-table">
            <thead>
              <tr>
                <th>Parâmetro</th>
                <th>Payload</th>
                <th>URL</th>
                <th>Evidência</th>
              </tr>
            </thead>
            <tbody>
              {result.findings.map((f, i) => (
                <tr key={i}>
                  <td><code>{f.param}</code></td>
                  <td><code className="payload">{f.payload}</code></td>
                  <td><a href={f.url} target="_blank" rel="noopener noreferrer">{f.url}</a></td>
                  <td>{f.evidence}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="result-ok">Nenhuma vulnerabilidade SQLi (erro-based) encontrada.</p>
        )}
      </div>
    )
  }

  if (result.type === 'dynamic') {
    return (
      <div className="result-card">
        <div className="result-header">
          <h3>Simulação de Navegador</h3>
          <StatusBadge ok={true} />
        </div>
        <p className="result-meta">Páginas analisadas: {result.crawled_pages}</p>
        <ul className="result-list">
          <li>Formulários encontrados: {result.forms_found}</li>
          <li>Links internos descobertos: {result.links_found}</li>
        </ul>
        {result.notes && result.notes.length > 0 && (
          <ul className="result-notes">
            {result.notes.map((n, i) => (
              <li key={i}>{n}</li>
            ))}
          </ul>
        )}
      </div>
    )
  }

  if (result.type === 'ports') {
    const ports = result.open_ports ?? []
    const subs = result.subdomains ?? []
    return (
      <div className="result-card">
        <div className="result-header">
          <h3>Scan de portas e infraestrutura</h3>
          <StatusBadge ok={ports.length === 0} />
        </div>
        <p className="result-meta">Portas abertas detectadas: {ports.length}</p>
        {ports.length > 0 ? (
          <table className="result-table">
            <thead>
              <tr>
                <th>Porta</th>
                <th>Protocolo</th>
                <th>Estado</th>
                <th>Serviço</th>
                <th>Versão</th>
              </tr>
            </thead>
            <tbody>
              {ports.map((port, index) => (
                <tr key={index}>
                  <td>{port.port}</td>
                  <td>{port.protocol}</td>
                  <td>{port.state}</td>
                  <td>{port.service}</td>
                  <td>{port.version || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="result-ok">Nenhuma porta aberta detectada nesta varredura.</p>
        )}
        {subs.length > 0 && (
          <div className="result-notes">
            <strong>Subdomínios descobertos:</strong>
            <ul>
              {subs.map((sub, idx) => (
                <li key={idx}>{sub}</li>
              ))}
            </ul>
          </div>
        )}
        {result.notes && result.notes.length > 0 && (
          <ul className="result-notes">
            {result.notes.map((n, i) => (
              <li key={i}>{n}</li>
            ))}
          </ul>
        )}
      </div>
    )
  }

  if (result.type === 'ssl') {
    const tls = result.tls_versions ?? []
    const vulns = result.vulnerabilities ?? []
    return (
      <div className="result-card">
        <div className="result-header">
          <h3>Análise de certificado SSL/TLS</h3>
          <StatusBadge ok={!result.is_vulnerable} />
        </div>
        <p className="result-meta">Força do cipher: {result.cipher_strength}</p>
        {result.certificate ? (
          <div className="result-details">
            <p><strong>Certificado:</strong> {result.certificate.subject}</p>
            <p><strong>Emitido por:</strong> {result.certificate.issuer}</p>
            <p><strong>Validade:</strong> {result.certificate.valid_from} — {result.certificate.valid_until}</p>
            <p><strong>Status:</strong> {result.certificate.is_valid ? 'Válido' : 'Inválido/expirado'}</p>
          </div>
        ) : (
          <p className="result-ok">Não foi possível obter detalhes do certificado nesta tentativa.</p>
        )}
        <div className="result-notes">
          <strong>Versões TLS testadas:</strong>
          <ul>
            {tls.length > 0 ? (
              tls.map((version, index) => (
                <li key={index}>{version.protocol}: {version.is_supported ? 'Suportado' : 'Não suportado'}</li>
              ))
            ) : (
              <li>Nenhum dado de protocolo disponível.</li>
            )}
          </ul>
        </div>
        {vulns.length > 0 ? (
          <div className="result-notes">
            <strong>Vulnerabilidades:</strong>
            <ul>
              {vulns.map((vuln, index) => (
                <li key={index}>{vuln.severity} — {vuln.description}</li>
              ))}
            </ul>
          </div>
        ) : (
          <p className="result-ok">Nenhuma vulnerabilidade SSL/TLS adicional detectada nesta verificação.</p>
        )}
        {result.notes && result.notes.length > 0 && (
          <ul className="result-notes">
            {result.notes.map((n, i) => (
              <li key={i}>{n}</li>
            ))}
          </ul>
        )}
      </div>
    )
  }

  const fallbackType = (result as any).type || 'desconhecido'

  return (
    <div className="result-card">
      <div className="result-header">
        <h3>{fallbackType}</h3>
        <StatusBadge ok={true} />
      </div>
      <pre>{JSON.stringify(result, null, 2)}</pre>
    </div>
  )
}

function StatusBadge({ ok }: { ok: boolean }) {
  return (
    <span className={`badge ${ok ? 'badge-ok' : 'badge-warn'}`}>
      {ok ? 'OK' : 'Atenção'}
    </span>
  )
}
